"""Stage 7.5 GATE B1 -- Occupancy benchmark.

Re-runs the Stage 6.0a OCC_XXXX_g40 configs with VecJointTaskManager swapped in
and compares directly against the perf_results.json recon baseline.

Protocol mirrors Stage 6.0a perf (stage6_0a_perf.py):
  - WARMUP = 10 steps (excluded from timing)
  - WINDOW  = 80 steps (measured)
  - STEP_CEILING = 600 ms/step; if exceeded on 3 consecutive steps -> hard-infeasible
  - configs: OCC_1600, OCC_3200, OCC_6400, OCC_12800 (all g40, kappa=1.0)

Pre-registered performance gate (ARCHITECTURE ss12.1-H ss H.3):
  - OCC_3200_g40  < 300 ms/step
  - OCC_6400_g40  <= 500 ms/step
  - Occupancy exponent (log-log slope across feasible configs) <= 1.5

Recon baseline (oracle JTM, from perf_results.json):
  - OCC_1600_g40: 170.6 ms/step  (PASS)
  - OCC_3200_g40: hard-infeasible (cliff)
  - OCC_6400_g40: skipped (past ceiling)
  - OCC_12800_g40: skipped (past ceiling)

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
from sic_games.run import SugarWorld
from sic_games.soa_jt import VecJointTaskManager

_WARMUP = 10
_WINDOW = 80
_SEED = 42
_STEP_CEILING_MS = 600.0   # ms/step; 3 consecutive above this = hard-infeasible
_CONSEC_LIMIT = 3
_OUT_DIR = Path(__file__).parent

# Recon baseline from perf_results.json (oracle JTM, stage6_0a)
_RECON = {
    "OCC_1600_g40": dict(ms_mean=170.593, ms_sd=57.54, mean_occ=2.354, status="window-completed"),
    "OCC_3200_g40": dict(ms_mean=None,    ms_sd=None,  mean_occ=None,  status="hard-infeasible"),
    "OCC_6400_g40": dict(ms_mean=None,    ms_sd=None,  mean_occ=None,  status="skipped"),
    "OCC_12800_g40": dict(ms_mean=None,   ms_sd=None,  mean_occ=None,  status="skipped"),
}

# Gate thresholds (from ARCHITECTURE ss12.1-H ss H.3)
_GATE_OCC3200_MS   = 300.0
_GATE_OCC6400_MS   = 500.0
_GATE_EXP_LIMIT    = 1.5


def _run_config(label: str, grid: int, init_n: int, kappa: float) -> dict:
    """Run one OCC config with VecJTM; return timing + occupancy stats."""
    import numpy as np

    n_carry = max(20000, 10 * init_n)
    cfg = _bench_config(grid, grid, init_n, _WARMUP + _WINDOW + 5, seed=_SEED,
                        n_carry_override=n_carry)
    cfg = cfg.model_copy(update={"substrate": SubstrateConfig(
        enabled=True, k_cell=0, movement_mode="diffusion",
        contest_exponent=kappa, move_cost_flat=0.0,
    )})
    cfg = cfg.model_copy(update={"run": cfg.run.model_copy(update={
        "metrics_every": 9999, "k_moran": 9999, "k_density": 9999,
    })})

    m = SugarWorld(cfg)
    # Swap in VecJointTaskManager
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
    mean_occ = float(np.mean(occs)) if occs else 0.0
    peak_occ = int(max(occs)) if occs else 0
    occ_all = final_n / (grid * grid)

    if step_times:
        ms_mean = float(np.mean(step_times))
        ms_sd   = float(np.std(step_times))
    else:
        ms_mean = float("nan")
        ms_sd   = float("nan")

    return dict(
        label=label, grid=grid, init_n=init_n, kappa=kappa,
        n_carry=n_carry, final_n=final_n,
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
    configs = [
        ("OCC_1600_g40",  40, 1600,  1.0),
        ("OCC_3200_g40",  40, 3200,  1.0),
        ("OCC_6400_g40",  40, 6400,  1.0),
        ("OCC_12800_g40", 40, 12800, 1.0),
    ]

    results = []
    for label, grid, init_n, kappa in configs:
        print(f"\n=== {label} (grid={grid}, N_init={init_n}) ===", flush=True)
        res = _run_config(label, grid, init_n, kappa)
        results.append(res)
        ms_str = f"{res['ms_mean']:.1f}" if not math.isnan(res['ms_mean']) else "N/A"
        occ_str = f"{res['mean_occ']:.2f}" if res['mean_occ'] > 0 else "N/A"
        print(f"  -> {res['status']}: ms_mean={ms_str}, mean_occ={occ_str}", flush=True)

        if res["status"] == "hard-infeasible":
            print(f"  [stopped: 3+ consecutive steps > {_STEP_CEILING_MS:.0f} ms]", flush=True)
            # Mark remaining configs as skipped
            for future_label, *_ in configs[len(results):]:
                results.append(dict(
                    label=future_label, status="skipped",
                    ms_mean=float("nan"), ms_sd=float("nan"),
                    mean_occ=float("nan"), peak_occ=0, occ_per_cell_all=float("nan"),
                ))
            break

    # ── Performance gate evaluation ─────────────────────────────────────────
    print("\n" + "="*60)
    print("GATE B1 OCCUPANCY PERFORMANCE EVALUATION")
    print("="*60)

    print("\n--- Direct comparison vs. recon baseline ---")
    header = f"{'Label':<18} {'Recon ms':>10} {'Vec ms':>10} {'Recon occ':>10} {'Vec occ':>9} {'Status':<18}"
    print(header)
    print("-" * len(header))
    for res in results:
        label = res["label"]
        rec = _RECON.get(label, {})
        recon_ms = f"{rec.get('ms_mean', 'N/A'):.1f}" if isinstance(rec.get('ms_mean'), float) else "N/A"
        recon_occ = f"{rec.get('mean_occ', 'N/A'):.2f}" if isinstance(rec.get('mean_occ'), float) else "N/A"
        vec_ms = f"{res['ms_mean']:.1f}" if not math.isnan(res['ms_mean']) else "N/A"
        vec_occ = f"{res['mean_occ']:.2f}" if not math.isnan(res.get('mean_occ', float('nan'))) else "N/A"
        cliff_sym = ""
        if rec.get("status") in ("hard-infeasible", "skipped") and res["status"] == "window-completed":
            cliff_sym = " <-- CLIFF GONE"
        print(f"  {label:<16} {recon_ms:>10} {vec_ms:>10} {recon_occ:>10} {vec_occ:>9} {res['status']:<18}{cliff_sym}")

    # Gate checks
    gate_pass = True
    gate_lines = []

    # Find OCC_3200 and OCC_6400 results
    r3200 = next((r for r in results if r["label"] == "OCC_3200_g40"), None)
    r6400 = next((r for r in results if r["label"] == "OCC_6400_g40"), None)
    r1600 = next((r for r in results if r["label"] == "OCC_1600_g40"), None)

    # Gate 1: OCC_3200 < 300 ms/step
    if r3200 and r3200["status"] == "window-completed" and not math.isnan(r3200["ms_mean"]):
        ok = r3200["ms_mean"] < _GATE_OCC3200_MS
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(f"  Gate 1 OCC_3200 < {_GATE_OCC3200_MS:.0f} ms/step: "
                          f"{r3200['ms_mean']:.1f} ms  [{mark}]")
        if not ok:
            gate_pass = False
    else:
        gate_lines.append(f"  Gate 1 OCC_3200 < {_GATE_OCC3200_MS:.0f} ms/step: "
                          f"status={r3200['status'] if r3200 else 'N/A'}  [FAIL - not completed]")
        gate_pass = False

    # Gate 2: OCC_6400 <= 500 ms/step
    if r6400 and r6400["status"] == "window-completed" and not math.isnan(r6400["ms_mean"]):
        ok = r6400["ms_mean"] <= _GATE_OCC6400_MS
        mark = "PASS" if ok else "FAIL"
        gate_lines.append(f"  Gate 2 OCC_6400 <= {_GATE_OCC6400_MS:.0f} ms/step: "
                          f"{r6400['ms_mean']:.1f} ms  [{mark}]")
        if not ok:
            gate_pass = False
    else:
        gate_lines.append(f"  Gate 2 OCC_6400 <= {_GATE_OCC6400_MS:.0f} ms/step: "
                          f"status={r6400['status'] if r6400 else 'N/A'}  [FAIL - not completed]")
        gate_pass = False

    # Gate 3: occupancy exponent from feasible points
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
        gate_lines.append(f"  Gate 3 Occupancy exponent <= {_GATE_EXP_LIMIT:.1f}: "
                          f"{exp_val:.3f}  [{mark}]")
        if not ok:
            gate_pass = False
    else:
        n_feas = len(feasible)
        gate_lines.append(f"  Gate 3 Occupancy exponent: only {n_feas} feasible point(s)  [INCONCLUSIVE]")

    print("\n--- Gate evaluation (ARCHITECTURE ss12.1-H ss H.3) ---")
    for line in gate_lines:
        print(line)

    # Overall verdict
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
            "OCC_3200_ms": _GATE_OCC3200_MS,
            "OCC_6400_ms": _GATE_OCC6400_MS,
            "exp_limit": _GATE_EXP_LIMIT,
        },
        "gate_verdict": verdict,
        "gate_lines": gate_lines,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nResults saved to: {out_path.name}")


if __name__ == "__main__":
    main()
