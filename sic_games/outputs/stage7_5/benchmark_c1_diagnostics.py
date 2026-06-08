"""Stage 7.5 GATE C1 — Diagnostic vectorisation benchmark.

Measures step time for the oracle (dense _moran_W) vs SoAWorld (sparse _moran_W_csr)
across increasing N at k_moran=10 and k_density=10 (production default cadence).

GATE C1 pass criterion (blueprint §8):
  "Full-step affordable N no longer collapses to ~3–4k."

Methodology:
  - Both oracle (SugarWorld) and array model (SoAWorld) run for WARMUP + WINDOW steps.
  - Diagnostics enabled: metrics_every=1, k_moran=10, k_density=10.
  - Timing captures TOTAL step cost including diagnostics.
  - Grid: 100×100 (production-like, sparse density), N_init varied.
  - mode="fixed" (no births/deaths): isolates the diagnostic cost from demographic noise.

Gate thresholds (pre-registered):
  - Gate 1: Oracle + SoAWorld step time < 500 ms at N=2000 with diagnostics enabled.
  - Gate 2: SoAWorld step time < 500 ms at N=4000 with diagnostics enabled
            (the ~3–4k "collapse" threshold must be exceeded without hitting the wall).
  - Gate 3: SoAWorld diagnostic overhead (ms/step at k_moran step vs off-step) < 200%
            of the non-diagnostic step cost (no longer dominates).

Usage:
    py outputs/stage7_5/benchmark_c1_diagnostics.py
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sic_games.owe1_calibration import _bench_config
from sic_games.run import SugarWorld
from sic_games.soa_step import SoAWorld

_WARMUP = 5
_WINDOW = 30
_SEED   = 42
_OUT_DIR = Path(__file__).parent

# Gate thresholds
_GATE1_MS = 500.0   # oracle + SoAWorld < 500 ms at N=2000 (diagnostics on)
_GATE2_MS = 500.0   # SoAWorld < 500 ms at N=4000 (exceeds old 3–4k "collapse")
_GATE3_OVERHEAD_PCT = 200.0  # SoAWorld diagnostic overhead < 200% of base step cost

_N_LIST = [500, 1000, 2000, 3000, 4000]  # N_init values to sweep


def _make_cfg(n_init: int, k_moran: int = 10, k_density: int = 10):
    """100×100 grid, fixed-mode (no births), diagnostics enabled at production cadence."""
    cfg = _bench_config(100, 100, n_init, _WARMUP + _WINDOW + 5, seed=_SEED,
                        n_carry_override=max(n_init * 2, 1000))
    cfg = cfg.model_copy(update={"run": cfg.run.model_copy(update={
        "metrics_every": 1,
        "k_moran":   k_moran,
        "k_density": k_density,
    })})
    # Fixed-mode: no births or deaths (isolates diagnostic cost)
    cfg = cfg.model_copy(update={"population": cfg.population.model_copy(update={
        "mode": "fixed",
    })})
    return cfg


def _run_model(ModelClass, cfg, label: str) -> dict:
    """Run ModelClass for WARMUP + WINDOW steps; return per-step timing stats."""
    m = ModelClass(cfg)

    step_times: list[float] = []
    moran_step_times: list[float] = []    # steps where k_moran fires
    non_moran_step_times: list[float] = []

    k_m = cfg.run.k_moran

    for step in range(_WARMUP + _WINDOW):
        t0 = time.perf_counter()
        m.step()
        dt_ms = (time.perf_counter() - t0) * 1000.0

        if step >= _WARMUP:
            step_times.append(dt_ms)
            if step % k_m == 0:
                moran_step_times.append(dt_ms)
            else:
                non_moran_step_times.append(dt_ms)

    n_final = len(list(m.agents))
    ms_mean = sum(step_times) / len(step_times) if step_times else float("nan")
    ms_moran = (sum(moran_step_times) / len(moran_step_times)
                if moran_step_times else float("nan"))
    ms_base  = (sum(non_moran_step_times) / len(non_moran_step_times)
                if non_moran_step_times else float("nan"))
    overhead_pct = (
        100.0 * (ms_moran - ms_base) / ms_base
        if (ms_base > 0 and not math.isnan(ms_moran)) else float("nan")
    )

    return dict(
        label=label, n_init=cfg.agents.initial_population, n_final=n_final,
        ms_mean=ms_mean, ms_moran=ms_moran, ms_base=ms_base,
        overhead_pct=overhead_pct,
        n_moran_steps=len(moran_step_times),
        n_base_steps=len(non_moran_step_times),
    )


def main() -> None:
    oracle_results = []
    soa_results    = []

    for n in _N_LIST:
        cfg = _make_cfg(n)
        n_cells = 100 * 100
        assert n <= n_cells, f"N_init={n} > {n_cells} cells — would hang at init (BUG-003)"

        print(f"\n=== N_init={n} ===", flush=True)

        label_o = f"oracle_N{n}"
        print(f"  Oracle (dense _moran_W)...", flush=True)
        res_o = _run_model(SugarWorld, cfg, label_o)
        oracle_results.append(res_o)
        print(f"    ms/step={res_o['ms_mean']:.1f}  "
              f"ms@k_moran={res_o['ms_moran']:.1f}  "
              f"ms_base={res_o['ms_base']:.1f}  "
              f"overhead={res_o['overhead_pct']:.0f}%", flush=True)

        label_s = f"soa_N{n}"
        print(f"  SoAWorld (sparse _moran_W_csr)...", flush=True)
        res_s = _run_model(SoAWorld, cfg, label_s)
        soa_results.append(res_s)
        print(f"    ms/step={res_s['ms_mean']:.1f}  "
              f"ms@k_moran={res_s['ms_moran']:.1f}  "
              f"ms_base={res_s['ms_base']:.1f}  "
              f"overhead={res_s['overhead_pct']:.0f}%", flush=True)

    # ── Gate evaluation ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("GATE C1 DIAGNOSTIC VECTORISATION EVALUATION")
    print("=" * 60)

    # Table header
    print(f"\n{'N_init':>7}  {'Oracle ms':>10}  {'SoA ms':>10}  "
          f"{'SoA@moran':>10}  {'SoA_base':>9}  {'overhead':>9}")
    print("-" * 70)
    for res_o, res_s in zip(oracle_results, soa_results):
        n = res_o["n_init"]
        print(f"{n:>7}  {res_o['ms_mean']:>10.1f}  {res_s['ms_mean']:>10.1f}  "
              f"{res_s['ms_moran']:>10.1f}  {res_s['ms_base']:>9.1f}  "
              f"{res_s['overhead_pct']:>8.0f}%")

    gate_pass = True
    gate_lines: list[str] = []

    # Gate 1: oracle + SoAWorld < 500 ms at N=2000
    res_o2000 = next((r for r in oracle_results if r["n_init"] == 2000), None)
    res_s2000 = next((r for r in soa_results    if r["n_init"] == 2000), None)
    if res_o2000 and res_s2000:
        ok = res_o2000["ms_mean"] < _GATE1_MS and res_s2000["ms_mean"] < _GATE1_MS
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(
            f"  Gate 1 (N=2000, diag on, both < {_GATE1_MS:.0f} ms): "
            f"oracle={res_o2000['ms_mean']:.1f}ms, SoA={res_s2000['ms_mean']:.1f}ms  [{mark}]"
        )
        if not ok:
            gate_pass = False
    else:
        gate_lines.append("  Gate 1: N=2000 not measured  [INCONCLUSIVE]")

    # Gate 2: SoAWorld < 500 ms at N=4000 (exceeds old 3–4k cap)
    res_s4000 = next((r for r in soa_results if r["n_init"] == 4000), None)
    if res_s4000:
        ok = res_s4000["ms_mean"] < _GATE2_MS
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(
            f"  Gate 2 (N=4000, SoA < {_GATE2_MS:.0f} ms, diag on): "
            f"{res_s4000['ms_mean']:.1f}ms  [{mark}]"
        )
        if not ok:
            gate_pass = False
    else:
        gate_lines.append("  Gate 2: N=4000 not measured  [INCONCLUSIVE]")

    # Gate 3: SoAWorld diagnostic overhead < 200% of base step
    for res_s in soa_results:
        n = res_s["n_init"]
        oh = res_s["overhead_pct"]
        if math.isnan(oh):
            continue
        ok = oh < _GATE3_OVERHEAD_PCT
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(
            f"  Gate 3 (N={n}, SoA overhead < {_GATE3_OVERHEAD_PCT:.0f}%): "
            f"{oh:.0f}%  [{mark}]"
        )
        if not ok:
            gate_pass = False

    print("\n--- Gate evaluation ---")
    for line in gate_lines:
        print(line)

    print(f"\n{'=' * 60}")
    verdict = "PASS" if gate_pass else "FAIL"
    print(f"GATE C1 DIAGNOSTICS: {verdict}")
    print(f"{'=' * 60}")

    # Save results
    out_path = _OUT_DIR / "benchmark_c1_diagnostics_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "oracle_results": oracle_results,
            "soa_results": soa_results,
            "gate_thresholds": {
                "gate1_ms": _GATE1_MS,
                "gate2_ms": _GATE2_MS,
                "gate3_overhead_pct": _GATE3_OVERHEAD_PCT,
            },
            "gate_verdict": verdict,
            "gate_lines": gate_lines,
        }, f, indent=2)
    print(f"\nResults saved to: {out_path.name}")


if __name__ == "__main__":
    main()
