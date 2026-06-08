"""Stage 7.5 GATE B1 -- Occupancy benchmark (E2 redesign, 2026-06-08).

Measures SoAWorld + VecJointTaskManager step-time vs realised mean occupancy
(agents-per-cell) across a climbing n_carry sweep on a fixed 40x40 grid.

E2 fix (supervisor decision, Finding B1-4):
  The original config (OCC_3200_g40 with N_init=3200 on 40x40=1600 cells)
  always hung at init: run.py _random_unoccupied() is an infinite while-True
  loop once all cells are occupied (N_init > grid_cells).  Stage 6.0a's
  "hard-infeasible" record was a subprocess timeout at init placement, NOT a
  step-time ceiling hit.  No performance cliff was ever measured at OCC_3200.

  Fix: all configs use N_init=1600 (= 40x40 cells, no init hang).  n_carry
  drives the sustained population — and therefore mean agents-per-cell — during
  the measurement window.  Gate thresholds are reinterpreted from N-based to
  occupancy-based:
    Gate 1 (was OCC_3200 < 300 ms): step time < 300 ms at mean_occ >= 2
    Gate 2 (was OCC_6400 <= 500 ms): step time <= 500 ms at mean_occ >= 3
    Gate 3 (unchanged): occupancy exponent <= 1.5

Protocol (unchanged from Stage 6.0a):
  - WARMUP = 10 steps (excluded from timing)
  - WINDOW  = 80 steps (measured)
  - STEP_CEILING = 600 ms/step; 3 consecutive steps above -> hard-infeasible

Recon baseline (oracle JTM, stage6_0a perf_results.json):
  - OCC_1600_g40: 170.6 ms/step, mean_occ=2.354  (ONLY valid recon point)
  - OCC_3200_g40: "hard-infeasible" = init-placement timeout, not step-time cliff
  - OCC_6400_g40, OCC_12800_g40: skipped (downstream of init-infeasible)

Usage:
    py outputs/stage7_5/benchmark_b1_occupancy.py
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sic_games.config import SubstrateConfig
from sic_games.owe1_calibration import _bench_config
from sic_games.soa_jt import VecJointTaskManager
from sic_games.soa_step import SoAWorld

_WARMUP = 10
_WINDOW = 80
_SEED = 42
_STEP_CEILING_MS = 600.0   # ms/step; 3 consecutive above this = hard-infeasible
_CONSEC_LIMIT = 3
_OUT_DIR = Path(__file__).parent

# Recon baseline from perf_results.json (oracle JTM, stage6_0a).
# OCC_1600_g40 is the ONLY valid recon data point.  OCC_3200+ were init-infeasible
# (Finding B1-4): N_init > grid_cells caused _random_unoccupied() to loop forever;
# their "hard-infeasible" labels reflect subprocess timeouts at init, not step-time
# ceilings.  No oracle step-time data exists for those configs.
_RECON = {
    "OCC_1600_g40": dict(
        ms_mean=170.593, ms_sd=57.54, mean_occ=2.354, status="window-completed",
        note="valid — N_init=1600 = 40x40 cells",
    ),
    # OCC_3200_g40 and higher: init-infeasible in oracle (Finding B1-4, 2026-06-08).
    # _random_unoccupied() hangs when N_init > grid_cells. No valid step-time data.
}

# Gate thresholds — reinterpreted from N-based to occupancy-based (E2, 2026-06-08).
# See ARCHITECTURE ss12.1-H ss H.3 (updated) for rationale.
_GATE_OCC2_MS    = 300.0   # step time < 300 ms at mean_occ >= 2  (was: OCC_3200 < 300)
_GATE_OCC3_MS    = 500.0   # step time <= 500 ms at mean_occ >= 3  (was: OCC_6400 <= 500)
_GATE_OCC_MIN2   = 2.0     # mean_occ threshold for Gate 1
_GATE_OCC_MIN3   = 3.0     # mean_occ threshold for Gate 2
_GATE_EXP_LIMIT  = 1.5     # occupancy exponent (log-log slope) <= 1.5


def _run_config(label: str, grid: int, init_n: int, n_carry: int,
                kappa: float) -> dict:
    """Run one config with VecJTM + SoAWorld; return timing + occupancy stats.

    n_carry is explicit — the caller controls the target population ceiling.
    init_n must satisfy init_n <= grid*grid to avoid the _random_unoccupied()
    infinite loop in the frozen oracle (Finding B1-4 / BUG-003).
    """
    import numpy as np

    assert init_n <= grid * grid, (
        f"init_n={init_n} > grid^2={grid*grid}: would hang at init (BUG-003)"
    )

    cfg = _bench_config(grid, grid, init_n, _WARMUP + _WINDOW + 5, seed=_SEED,
                        n_carry_override=n_carry)
    cfg = cfg.model_copy(update={"substrate": SubstrateConfig(
        enabled=True, k_cell=0, movement_mode="diffusion",
        contest_exponent=kappa, move_cost_flat=0.0,
    )})
    cfg = cfg.model_copy(update={"run": cfg.run.model_copy(update={
        "metrics_every": 9999, "k_moran": 9999, "k_density": 9999,
    })})

    # C-wire: SoAWorld caches mean_cred() once per step (pre-batch semantic),
    # eliminating the O(N^2) mean_cred-per-birth bottleneck (run.py line 784).
    m = SoAWorld(cfg)
    jt = m._jt_manager
    m._jt_manager = VecJointTaskManager(
        distance_d=jt.distance_d,
        capacity_threshold=jt.capacity_threshold,
        matthew_alpha=jt.matthew_alpha,
        epsilon=jt.epsilon,
        cred_bonus_per_participant=jt.cred_bonus_per_participant,
        seed=_SEED,
        c2_defection_enabled=jt.c2_defection_enabled,
    )

    step_times: list[float] = []
    consec_over = 0
    status = "window-completed"

    for step in range(_WARMUP + _WINDOW):
        t0 = time.perf_counter()
        m.step()
        dt_ms = (time.perf_counter() - t0) * 1000.0

        if step >= _WARMUP:
            step_times.append(dt_ms)
            if dt_ms > _STEP_CEILING_MS:
                consec_over += 1
                if consec_over >= _CONSEC_LIMIT:
                    status = "hard-infeasible"
                    break
            else:
                consec_over = 0

        if step % 10 == 0 or step == _WARMUP + _WINDOW - 1:
            n_now = len(list(m.agents))
            counts: dict = {}
            for a in m.agents:
                counts[a.pos] = counts.get(a.pos, 0) + 1
            pk = max(counts.values()) if counts else 0
            ts = time.time()
            print(f"  {ts:.1f}  step={step}  N={n_now}  ms={dt_ms:.1f}  peak_occ={pk}",
                  flush=True)

    # Final occupancy stats
    counts = {}
    for a in m.agents:
        counts[a.pos] = counts.get(a.pos, 0) + 1
    final_n = len(list(m.agents))
    occs = list(counts.values()) if counts else [0]
    mean_occ = float(sum(occs) / len(occs)) if occs else 0.0
    peak_occ = int(max(occs)) if occs else 0
    occ_all = final_n / (grid * grid)

    if step_times:
        ms_mean = float(sum(step_times) / len(step_times))
        ms_sd   = float((sum((x - ms_mean)**2 for x in step_times) / len(step_times))**0.5)
    else:
        ms_mean = float("nan")
        ms_sd   = float("nan")

    return dict(
        label=label, grid=grid, init_n=init_n, n_carry=n_carry, kappa=kappa,
        final_n=final_n,
        ms_mean=ms_mean, ms_sd=ms_sd,
        mean_occ=mean_occ, peak_occ=peak_occ, occ_per_cell_all=occ_all,
        status=status,
    )


def _log_log_exp(x_vals: list[float], y_vals: list[float]) -> float:
    """Least-squares log-log slope (exponent) from paired (x, y) lists."""
    if len(x_vals) < 2:
        return float("nan")
    import numpy as np
    lx = np.log(x_vals)
    ly = np.log(y_vals)
    n = len(lx)
    slope = (n * np.dot(lx, ly) - lx.sum() * ly.sum()) / (
        n * np.dot(lx, lx) - lx.sum() ** 2
    )
    return float(slope)


def main() -> None:
    # E2 configs: N_init=1600 (= 40x40 cells) for all — no init hang.
    # n_carry climbs to drive sustained occupancy through 2 → 3 → 4+ agents/cell.
    # Labels encode the n_carry in thousands (nc20k, nc40k, nc80k).
    configs = [
        # label,                grid, init_n, n_carry,  kappa
        ("OCC_1600_g40",          40,  1600,  20000,    1.0),  # reference: matches recon
        ("OCC_1600_nc40k_g40",    40,  1600,  40000,    1.0),  # target mean_occ ~ 3
        ("OCC_1600_nc80k_g40",    40,  1600,  80000,    1.0),  # target mean_occ ~ 4+
    ]

    results = []
    for label, grid, init_n, n_carry, kappa in configs:
        print(f"\n=== {label} (grid={grid}, N_init={init_n}, n_carry={n_carry}) ===",
              flush=True)
        res = _run_config(label, grid, init_n, n_carry, kappa)
        results.append(res)
        ms_str  = f"{res['ms_mean']:.1f}" if not math.isnan(res['ms_mean']) else "N/A"
        occ_str = f"{res['mean_occ']:.2f}" if res['mean_occ'] > 0 else "N/A"
        print(f"  -> {res['status']}: ms_mean={ms_str}, mean_occ={occ_str}, "
              f"final_N={res['final_n']}", flush=True)

        if res["status"] == "hard-infeasible":
            print(f"  [stopped: 3+ consecutive steps > {_STEP_CEILING_MS:.0f} ms]",
                  flush=True)
            for future_label, *_ in configs[len(results):]:
                results.append(dict(
                    label=future_label, status="skipped",
                    ms_mean=float("nan"), ms_sd=float("nan"),
                    mean_occ=float("nan"), peak_occ=0, occ_per_cell_all=float("nan"),
                    final_n=0,
                ))
            break

    # ── Gate evaluation ─────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("GATE B1 OCCUPANCY PERFORMANCE EVALUATION (E2 redesign)")
    print("="*60)

    # Direct comparison vs. recon (single valid recon point: OCC_1600_g40)
    print("\n--- Comparison vs. recon baseline ---")
    recon_ref = _RECON.get("OCC_1600_g40", {})
    header = f"{'Label':<24} {'Recon ms':>9} {'Vec ms':>9} {'Recon occ':>10} {'Vec occ':>9} {'N_carry':>8} {'Status'}"
    print(header)
    print("-" * len(header))
    for res in results:
        label = res["label"]
        if label == "OCC_1600_g40":
            recon_ms  = f"{recon_ref.get('ms_mean', 0.0):.1f}"
            recon_occ = f"{recon_ref.get('mean_occ', 0.0):.2f}"
        else:
            recon_ms  = "N/A"
            recon_occ = "N/A"
        vec_ms  = f"{res['ms_mean']:.1f}" if not math.isnan(res['ms_mean']) else "N/A"
        vec_occ = f"{res['mean_occ']:.2f}" if not math.isnan(res.get('mean_occ', float('nan'))) else "N/A"
        nc_str  = str(res.get("n_carry", ""))
        print(f"  {label:<22} {recon_ms:>9} {vec_ms:>9} {recon_occ:>10} {vec_occ:>9} "
              f"{nc_str:>8} {res['status']}")

    print(f"\n  Note: OCC_3200_g40 / OCC_6400_g40 / OCC_12800_g40 from Stage 6.0a recon")
    print(f"  were init-infeasible (Finding B1-4): init-placement timeout, NOT a")
    print(f"  step-time cliff. No valid oracle step-time data exists for those configs.")

    gate_pass = True
    gate_lines: list[str] = []

    # Gate 1: step time < 300 ms at mean_occ >= 2 (restatement of OCC_3200 < 300 ms)
    occ2_results = [r for r in results
                    if r["status"] == "window-completed"
                    and not math.isnan(r.get("mean_occ", float("nan")))
                    and r["mean_occ"] >= _GATE_OCC_MIN2]
    if occ2_results:
        r2 = min(occ2_results, key=lambda r: abs(r["mean_occ"] - 2.0))  # closest to occ=2
        ok = r2["ms_mean"] < _GATE_OCC2_MS
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(
            f"  Gate 1 occ>={_GATE_OCC_MIN2:.0f} < {_GATE_OCC2_MS:.0f} ms/step: "
            f"{r2['ms_mean']:.1f} ms @ mean_occ={r2['mean_occ']:.2f}  [{mark}]"
        )
        if not ok:
            gate_pass = False
    else:
        gate_lines.append(
            f"  Gate 1 occ>={_GATE_OCC_MIN2:.0f} < {_GATE_OCC2_MS:.0f} ms/step: "
            f"no config achieved mean_occ>={_GATE_OCC_MIN2:.0f}  [INCONCLUSIVE]"
        )
        gate_pass = False

    # Gate 2: step time <= 500 ms at mean_occ >= 3 (restatement of OCC_6400 <= 500 ms)
    occ3_results = [r for r in results
                    if r["status"] == "window-completed"
                    and not math.isnan(r.get("mean_occ", float("nan")))
                    and r["mean_occ"] >= _GATE_OCC_MIN3]
    if occ3_results:
        r3 = max(occ3_results, key=lambda r: r["mean_occ"])  # highest occ achieved
        ok = r3["ms_mean"] <= _GATE_OCC3_MS
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(
            f"  Gate 2 occ>={_GATE_OCC_MIN3:.0f} <= {_GATE_OCC3_MS:.0f} ms/step: "
            f"{r3['ms_mean']:.1f} ms @ mean_occ={r3['mean_occ']:.2f}  [{mark}]"
        )
        if not ok:
            gate_pass = False
    else:
        gate_lines.append(
            f"  Gate 2 occ>={_GATE_OCC_MIN3:.0f} <= {_GATE_OCC3_MS:.0f} ms/step: "
            f"no feasible config reached mean_occ>={_GATE_OCC_MIN3:.0f}  [FAIL - occupancy target not reached]"
        )
        gate_pass = False

    # Gate 3: occupancy exponent
    feasible = [(r["mean_occ"], r["ms_mean"]) for r in results
                if r["status"] == "window-completed"
                and not math.isnan(r.get("ms_mean", float("nan")))
                and not math.isnan(r.get("mean_occ", float("nan")))
                and r["mean_occ"] > 0]
    if len(feasible) >= 2:
        x_vals = [p[0] for p in feasible]
        y_vals = [p[1] for p in feasible]
        exp_val = _log_log_exp(x_vals, y_vals)
        ok = exp_val <= _GATE_EXP_LIMIT
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(
            f"  Gate 3 occ exponent <= {_GATE_EXP_LIMIT:.1f}: "
            f"{exp_val:.3f}  [{mark}]"
        )
        if not ok:
            gate_pass = False
    else:
        n_feas = len(feasible)
        gate_lines.append(
            f"  Gate 3 occ exponent: only {n_feas} feasible point(s)  [INCONCLUSIVE]"
        )

    print("\n--- Gate evaluation (E2 restatement; ARCHITECTURE ss12.1-H ss H.3) ---")
    for line in gate_lines:
        print(line)

    print(f"\n{'='*60}")
    verdict = "PASS" if gate_pass else "FAIL"
    print(f"GATE B1 OCCUPANCY: {verdict}")
    print(f"{'='*60}")

    # Save results
    out_path = _OUT_DIR / "benchmark_b1_occupancy_results.json"
    payload = {
        "vec_results": results,
        "recon_baseline": _RECON,
        "gate_thresholds": {
            "occ_ge2_ms": _GATE_OCC2_MS,
            "occ_ge3_ms": _GATE_OCC3_MS,
            "exp_limit":  _GATE_EXP_LIMIT,
        },
        "gate_verdict": verdict,
        "gate_lines": gate_lines,
        "finding_b1_4": (
            "OCC_3200/6400/12800 were init-infeasible in the oracle: "
            "_random_unoccupied() hangs when N_init > grid_cells. "
            "Stage 6.0a hard-infeasible labels were subprocess init timeouts, "
            "not step-time ceiling hits. E2: N_init fixed at grid_cells=1600; "
            "n_carry varied to drive occupancy."
        ),
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nResults saved to: {out_path.name}")


if __name__ == "__main__":
    main()
