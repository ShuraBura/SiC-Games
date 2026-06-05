"""Stage 6.0a-perf — Substrate Performance Reconnaissance (robust driver).

Maps the cost surface of the CURRENT multi-occupancy substrate (diffusion movement,
resource-split harvest, Cred/phi contest) across three axes: grid, total N, per-cell
occupancy. Two-tier ms/step cutoff. Flushed incremental logging. Plausibility rails.

DOCUMENTED CHOICES (blueprint §8 legibility):
- Window: 10 warm-up steps + 80 measured steps (90 total). ms/step = mean over the 80
  measured steps, with SD. Warm-up excludes first-touch / occupancy transient.
- n_carry = init_N: self-stabilising population at the ceiling (carry_discount=0 at N≈init,
  births resume as deaths lower N) → population sits NEAR the configured N with stable
  occupancy, so the cost point is measured at a controlled (N, occupancy) rather than
  letting births explode (which earlier hung a dense-grid config for hours).
- Substrate isolation: k_moran=k_density=metrics_every=9999 so the O(N^2) diagnostic
  metrics (Moran's I, c_spatial_density) fire at most once and do NOT mask substrate cost.
  A separate profiling pass measures the full step (diagnostics on) to show their dominance.
- kappa=1 (contest) default sweep path (the more expensive harvest path). One kappa=0 point.
- ROBUSTNESS: each config runs in its OWN subprocess with a wall-clock timeout. A runaway
  config (single mega-step) is killed by the parent and recorded HARD-INFEASIBLE, so the
  sweep never hangs. The flushed per-config log survives the kill (§6).
- Rate-ceiling cut: 300 ms/step. Per-config wall-clock budget: 180 s -> hard-infeasible.

Usage:
    py -m sic_games.stage6_0a_perf            # driver (spawns worker subprocesses)
    py -m sic_games.stage6_0a_perf worker <label> <grid> <init_n> <kappa>   # one config
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from pathlib import Path

_OUT = Path(__file__).parent.parent.parent / "outputs" / "stage6_0a_perf"
_WARMUP = 10
_WINDOW = 80
_RATE_CEILING_MS = 300.0
_PER_CONFIG_TIMEOUT_S = 90   # config that can't finish the 90-step window in 90s = hard-infeasible
_SEED = 42


# ─── WORKER: run one config, write result json + flushed log ──────────────────

def _worker(label: str, grid: int, init_n: int, kappa: float) -> None:
    import numpy as np
    from sic_games.config import SubstrateConfig
    from sic_games.owe1_calibration import _bench_config
    from sic_games.run import SugarWorld

    _OUT.mkdir(parents=True, exist_ok=True)
    logdir = _OUT / "logs"; logdir.mkdir(exist_ok=True)
    # n_carry high (10x init): births not artificially suppressed, population finds a
    # sensible equilibrium (~init to ~2x init) giving a clean N spread. The per-config
    # subprocess timeout (not n_carry) guards against the dense-grid birth/occupancy blowup.
    n_carry = max(20000, 10 * init_n)

    logf = open(logdir / f"log_{label}.txt", "w")
    def L(s):
        logf.write(s + "\n"); logf.flush()
    L(f"# {label} grid={grid} init_n={init_n} kappa={kappa} n_carry={n_carry}")
    L("# ts\tstep\tN\tms_step\tpeak_occ")

    cfg = _bench_config(grid, grid, init_n, _WARMUP + _WINDOW + 5, seed=_SEED, n_carry_override=n_carry)
    cfg = cfg.model_copy(update={"substrate": SubstrateConfig(
        enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=kappa, move_cost_flat=0.0,
    )})
    cfg = cfg.model_copy(update={"run": cfg.run.model_copy(update={
        "metrics_every": 9999, "k_moran": 9999, "k_density": 9999,
    })})

    m = SugarWorld(cfg)
    step_times, pop_trail = [], []
    for step in range(_WARMUP + _WINDOW):
        t0 = time.perf_counter()
        m.step()
        dt = time.perf_counter() - t0
        if step >= _WARMUP:
            step_times.append(dt * 1000.0)
        n_now = len(list(m.agents))
        pop_trail.append(n_now)
        if step % 10 == 0 or step == _WARMUP + _WINDOW - 1:
            counts = {}
            for a in m.agents:
                counts[a.pos] = counts.get(a.pos, 0) + 1
            pk = max(counts.values()) if counts else 0
            L(f"{time.time():.1f}\t{step}\t{n_now}\t{dt*1000:.1f}\t{pk}")

    # occupancy + rails on final state
    counts = {}
    for a in m.agents:
        counts[a.pos] = counts.get(a.pos, 0) + 1
    occ = np.array(list(counts.values())) if counts else np.array([0])
    n = len(list(m.agents))
    # rails (§3)
    rail = "PASS"
    if n == 0:
        rail = "FAIL:extinct"
    elif n > n_carry * 3:
        rail = "FAIL:explode"
    elif counts and max(counts.values()) > 0.5 * n and n > 20:
        rail = "FAIL:single_cell_pileup"
    else:
        for a in list(m.agents)[:5000]:
            if not (math.isfinite(a.wealth) and math.isfinite(a.cred)):
                rail = "FAIL:nan"; break

    arr = np.array(step_times)
    ms_mean = float(arr.mean()); ms_sd = float(arr.std())
    cut = "ceiling-cut" if ms_mean > _RATE_CEILING_MS else "window-completed"
    res = {
        "label": label, "grid": grid, "init_n": init_n, "kappa": kappa, "n_carry": n_carry,
        "ms_mean": ms_mean, "ms_sd": ms_sd,
        "mean_occ": float(occ.mean()), "peak_occ": int(occ.max()),
        "n_occupied": len(counts), "final_n": n,
        "cut_status": cut, "rail_status": rail,
        "occ_per_cell_all": n / (grid * grid),
    }
    L(f"# RESULT {json.dumps(res)}")
    json.dump(res, open(_OUT / f"res_{label}.json", "w"))
    logf.close()


# ─── DRIVER: spawn worker subprocesses with timeout; two-tier cut + axis-stop ──

def _sweep_configs():
    pts = []
    # N-axis: grid 100, climb init N (n_carry=init pins population near N).
    # Low occupancy (~N/10000); isolates the N exponent.
    for n in (2000, 5000, 10000, 20000, 40000):
        pts.append((f"N_{n}_g100", 100, n, 1.0))
    # Grid-axis: init N=2000 fixed, vary grid cells -> grid exponent at low occupancy.
    # DESCENDING grid order (sparsest first) so the axis-stop on the dense small grid
    # does not pre-empt the feasible larger grids. (g=100 covered by N_2000_g100.)
    for g in (70, 50, 30):
        pts.append((f"G_{g}_n2000", g, 2000, 1.0))
    # Occupancy-axis: grid 40 (1600 cells) fixed, climb N -> rising agents/cell.
    # Fine low rungs to fit the occupancy exponent before infeasibility; high rungs
    # expected hard-infeasible (the JT-cohort occupancy blowup is the finding).
    for n in (1600, 3200, 6400, 12800):
        pts.append((f"OCC_{n}_g40", 40, n, 1.0))
    # kappa comparison (even split vs contest) at a feasible mid point
    pts.append(("K0_5000_g100", 100, 5000, 0.0))
    return pts


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    configs = _sweep_configs()
    axis_ceiling = {"N": False, "G": False, "OCC": False}
    results = []
    for label, grid, init_n, kappa in configs:
        axis = label.split("_")[0]
        if axis in axis_ceiling and axis_ceiling[axis]:
            print(f"  SKIP {label} (axis {axis} past ceiling)", flush=True)
            results.append({"label": label, "grid": grid, "init_n": init_n, "kappa": kappa,
                            "cut_status": "skipped-past-ceiling", "rail_status": "",
                            "ms_mean": float("nan")})
            continue
        resfile = _OUT / f"res_{label}.json"
        if resfile.exists():
            resfile.unlink()
        print(f"  RUN  {label} ...", flush=True)
        t0 = time.perf_counter()
        try:
            subprocess.run(
                [sys.executable, "-m", "sic_games.stage6_0a_perf", "worker",
                 label, str(grid), str(init_n), str(kappa)],
                timeout=_PER_CONFIG_TIMEOUT_S, cwd=str(Path(__file__).parent.parent.parent),
                check=False,
            )
        except subprocess.TimeoutExpired:
            print(f"    HARD-INFEASIBLE (timeout {_PER_CONFIG_TIMEOUT_S}s) — killed", flush=True)
            results.append({"label": label, "grid": grid, "init_n": init_n, "kappa": kappa,
                            "cut_status": "hard-infeasible", "rail_status": "timeout",
                            "ms_mean": float("nan")})
            if axis in axis_ceiling:
                axis_ceiling[axis] = True
            json.dump(results, open(_OUT / "perf_results.json", "w"))
            continue
        if resfile.exists():
            res = json.load(open(resfile))
            results.append(res)
            print(f"    ms/step={res['ms_mean']:.1f}+-{res['ms_sd']:.1f} "
                  f"occ(mean/peak)={res['mean_occ']:.2f}/{res['peak_occ']} N={res['final_n']} "
                  f"cut={res['cut_status']} rail={res['rail_status']} [{time.perf_counter()-t0:.0f}s]", flush=True)
            if axis in axis_ceiling and res["cut_status"] in ("ceiling-cut",):
                axis_ceiling[axis] = True
        else:
            print(f"    worker produced no result (crash?) [{time.perf_counter()-t0:.0f}s]", flush=True)
            results.append({"label": label, "grid": grid, "init_n": init_n, "kappa": kappa,
                            "cut_status": "worker-crash", "rail_status": "", "ms_mean": float("nan")})
        json.dump(results, open(_OUT / "perf_results.json", "w"))

    print("\n=== sweep done; results in perf_results.json ===", flush=True)


if __name__ == "__main__":
    if len(sys.argv) >= 6 and sys.argv[1] == "worker":
        _worker(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
    else:
        main()
