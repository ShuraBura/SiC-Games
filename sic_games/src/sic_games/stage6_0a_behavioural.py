"""Stage 6.0a S7.2 — C-behavioural runs under true multi-occupancy + diffusion movement.

kappa=0 (scramble reference, even split) and kappa=1 (Cred/phi-weighted contest), C static,
100×100, N_carry=4100, init N=2250, seed=42, 2000 steps, production substrate
(enabled, k_cell=0 unlimited, movement_mode="diffusion").

Logs: N(t) both runs; steady-state per-cell density distribution (+persons/km2);
Cov(phi,wealth) and Cred distribution for kappa=1 (Matthew-runaway flag — observe only).

Pre-registered readings (H-SUBSTRATE-6.0a): settles to stable band both kappa = viable;
crash/pin/explode = blocking. Density ~0.1 persons/km2 (0.01–1) = sane. Matthew-runaway:
report magnitude only, no mitigation, interpretation deferred.

Usage: py -m sic_games.stage6_0a_behavioural
"""
from __future__ import annotations

import pickle
import time
from pathlib import Path

import numpy as np

from sic_games.config import SubstrateConfig
from sic_games.metrics import gini
from sic_games.owe1_calibration import _bench_config
from sic_games.run import SugarWorld

_OUT = Path(__file__).parent.parent.parent / "outputs" / "stage6_0a_substrate"
_GRID, _N, _NCARRY, _STEPS, _SEED = 100, 2250, 4100, 2000, 42
_CELL_AREA_KM2 = 100.0
_SETTLE_FROM = 1500


def _run(kappa: float) -> dict:
    cfg = _bench_config(_GRID, _GRID, _N, _STEPS, seed=_SEED, n_carry_override=_NCARRY)
    cfg = cfg.model_copy(update={"substrate": SubstrateConfig(
        enabled=True, k_cell=0, movement_mode="diffusion",
        contest_exponent=kappa, move_cost_flat=0.0, cell_area_km2=_CELL_AREA_KM2,
    )})
    m = SugarWorld(cfg)
    pop = np.zeros(_STEPS, dtype=np.int64)
    t0 = time.perf_counter()
    for step in range(_STEPS):
        m.step()
        pop[step] = len(list(m.agents))
    elapsed = time.perf_counter() - t0

    agents = list(m.agents)
    # per-cell density (agents/cell) at final state
    counts: dict = {}
    for a in agents:
        counts[a.pos] = counts.get(a.pos, 0) + 1
    occ_vals = np.array(list(counts.values()))
    n_occupied = len(counts)
    n_cells = _GRID * _GRID
    mean_occ_per_occupied = float(occ_vals.mean()) if len(occ_vals) else 0.0
    # population-weighted mean occupancy (mean band size an agent lives in)
    pop_wt_occ = float((occ_vals ** 2).sum() / occ_vals.sum()) if occ_vals.sum() else 0.0
    # density persons/km2: mean agents per cell over ALL cells ÷ cell_area
    agents_per_cell_all = len(agents) / n_cells
    persons_per_km2 = agents_per_cell_all / _CELL_AREA_KM2

    settled = float(pop[_SETTLE_FROM:].mean())
    settled_std = float(pop[_SETTLE_FROM:].std())
    rel_std = settled_std / settled if settled > 0 else float("inf")

    # Matthew-runaway diagnostics (kappa=1): Cov(phi,wealth), Cred distribution
    phis = np.array([a.phi for a in agents])
    wealths = np.array([a.wealth for a in agents])
    creds = np.array([a.cred for a in agents])
    cov_phi_wealth = float(np.cov(phis, wealths)[0, 1]) if len(agents) > 1 else float("nan")
    corr_phi_wealth = float(np.corrcoef(phis, wealths)[0, 1]) if len(agents) > 1 else float("nan")
    cred_gini = gini(list(creds))
    cred_max_frac = float(creds.max() / creds.sum()) if creds.sum() > 0 else 0.0

    return {
        "kappa": kappa, "elapsed_s": elapsed,
        "pop": pop, "settled": settled, "settled_std": settled_std, "rel_std": rel_std,
        "final_n": int(pop[-1]),
        "n_occupied_cells": n_occupied, "n_cells": n_cells,
        "occ_hist": np.bincount(occ_vals) if len(occ_vals) else np.array([]),
        "max_occ": int(occ_vals.max()) if len(occ_vals) else 0,
        "mean_occ_per_occupied": mean_occ_per_occupied,
        "pop_wt_occ": pop_wt_occ,
        "agents_per_cell_all": agents_per_cell_all,
        "persons_per_km2": persons_per_km2,
        "cov_phi_wealth": cov_phi_wealth, "corr_phi_wealth": corr_phi_wealth,
        "cred_mean": float(creds.mean()), "cred_std": float(creds.std()),
        "cred_gini": cred_gini, "cred_max_frac": cred_max_frac,
        "phi_mean": float(phis.mean()), "wealth_mean": float(wealths.mean()),
    }


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    for kappa in (0.0, 1.0):
        print(f"\n=== S7.2 run: kappa={kappa} (diffusion, multi-occupancy, {_STEPS} steps) ===")
        r = _run(kappa)
        results[kappa] = r
        pickle.dump(results, open(_OUT / "behavioural_partial.pkl", "wb"))
        print(f"  pop {r['pop'][0]} -> {r['final_n']}  settled(t>={_SETTLE_FROM})={r['settled']:.0f} "
              f"rel_std={r['rel_std']:.4f}  ({r['elapsed_s']:.0f}s)")
        print(f"  occupied cells={r['n_occupied_cells']}/{r['n_cells']}  max_occ={r['max_occ']} "
              f"mean_occ(occupied)={r['mean_occ_per_occupied']:.2f}  pop-wt band={r['pop_wt_occ']:.2f}")
        print(f"  density: {r['agents_per_cell_all']:.4f} agents/cell  -> {r['persons_per_km2']:.4f} persons/km2")
        if kappa == 1.0:
            print(f"  Matthew: Cov(phi,wealth)={r['cov_phi_wealth']:.4f}  corr={r['corr_phi_wealth']:.4f}")
            print(f"  Cred: mean={r['cred_mean']:.3f} std={r['cred_std']:.3f} gini={r['cred_gini']:.4f} "
                  f"max_frac={r['cred_max_frac']:.4f}")

    print("\n=== SUMMARY (pre-registered readings) ===")
    for kappa in (0.0, 1.0):
        r = results[kappa]
        # viability: settled in a stable band, not extinct, not exploding/pinning
        viable = (r['final_n'] > 50 and r['rel_std'] < 0.30
                  and r['settled'] < _NCARRY * 1.5)
        print(f"  kappa={kappa}: settled={r['settled']:.0f} final={r['final_n']} rel_std={r['rel_std']:.4f} "
              f"density={r['persons_per_km2']:.4f} p/km2  viable={'YES' if viable else 'CHECK'}")


if __name__ == "__main__":
    main()
