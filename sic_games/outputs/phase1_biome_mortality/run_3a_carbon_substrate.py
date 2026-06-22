"""Carbon-on-substrate Tier-1 — the Cred-survival gradient under ordinary meat variance (G.3).

Scoping: `blueprints/phase1/SiC_Games_P1_CarbonSubstrate_Scoping.md`. The Carbon advantage is COMPOSITIONAL —
κ-weighted meat sharing concentrates bad-streak (G.3) starvation on the low-Cred periphery while the high-Cred
core persists. Aggregate e₀ is fertility-pinned (R-16) and ~κ-invariant; the signal is WHO survives.

Measure (drift-controlled — κ=0 vs κ>0 share identical seeding/inheritance, so any difference IS selection):
  - mean(cred | alive) at the tail — does κ>0 lift it above κ=0 (high-Cred selected)?
  - Gini(cred | alive) — the hierarchy's inequality.
  - eq_pop — substrate intact / aggregate ~invariant.
Forest-Aché substrate (de-warfared Siler, meat_frac 0.55, meat CV 0.73), density-disease ON (δ=3, the
provisional regulator) so the population sits near K where bad streaks bite. carbon_cfg.kappa=0 holds the
movement temperature at σ_base (isolate meat from the cred→movement channel).
Run:  py -3 -u outputs/phase1_biome_mortality/run_3a_carbon_substrate.py
"""
from __future__ import annotations
import math, os, time, statistics
import numpy as np

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEEDS = 400, 700, [11, 23, 42]
KAPPAS = [0.0, 1.0, 2.0]
MEAT_CV, MEAT_FRAC, SEED_SIGMA, INHERIT_SIGMA, DELTA = 0.73, 0.55, 0.5, 0.1, 3.0


def gini(xs):
    xs = sorted(xs); n = len(xs); s = sum(xs)
    if s <= 0 or n == 0:
        return 0.0
    return (2.0 * sum((i + 1) * x for i, x in enumerate(xs))) / (n * s) - (n + 1) / n


def run_one(kappa, seed):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=kappa, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(
                         siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=DELTA, dens_rho_half=0.2,
                         enable_game=True, game_meat_frac=MEAT_FRAC, game_meat_cv=MEAT_CV,
                         enable_cred_status=True, cred_seed_sigma=SEED_SIGMA, cred_inherit_sigma=INHERIT_SIGMA))
    c0 = statistics.mean([a.cred for a in w.agent_list])
    tail_pop, tail_mc, tail_g = [], [], []
    t0 = int(0.6 * STEPS)
    for step in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            break
        if step >= t0:
            creds = [a.cred for a in al]
            tail_pop.append(len(al)); tail_mc.append(statistics.mean(creds)); tail_g.append(gini(creds))
    alive = len(w.agent_list) > 0
    return dict(kappa=kappa, seed=seed, alive=alive, c0=c0,
                eq_pop=float(np.mean(tail_pop)) if tail_pop else 0.0,
                mean_cred=float(np.mean(tail_mc)) if tail_mc else 0.0,
                gini_cred=float(np.mean(tail_g)) if tail_g else 0.0)


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_3a.txt")
    agg = {}
    for k in KAPPAS:
        rows = [run_one(k, s) for s in SEEDS]
        agg[k] = dict(eq_pop=np.mean([r["eq_pop"] for r in rows]),
                      mean_cred=np.mean([r["mean_cred"] for r in rows]),
                      gini=np.mean([r["gini_cred"] for r in rows]),
                      c0=np.mean([r["c0"] for r in rows]))
        msg = (f"kappa={k:.0f}: eq_pop {agg[k]['eq_pop']:6.0f} | mean_cred(alive) {agg[k]['mean_cred']:.3f} "
               f"(founder {agg[k]['c0']:.3f}) | Gini(cred) {agg[k]['gini']:.3f}")
        print(f"[3a] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w", encoding="utf-8") as f:
            f.write(f"3a {msg} | elapsed {time.time()-t0:.0f}s\n")
    base = agg[0.0]["mean_cred"]
    print("\n[3a] COMPOSITIONAL SELECTION (drift-controlled: κ>0 mean_cred vs κ=0):", flush=True)
    for k in KAPPAS:
        lift = agg[k]["mean_cred"] - base
        print(f"   κ={k:.0f}: Δmean_cred {lift:+.3f}  ({'selection for high-Cred' if lift>0.02 else 'no selection'})",
              flush=True)
    verdict = ("κ>0 lifts mean(cred|alive) above κ=0 → Cred-weighted meat concentrates bad-streak survival on "
               "the high-Cred core (the COMPOSITIONAL anti-fragility, R-1) while eq_pop stays ~κ-invariant "
               "(fertility-pinned, R-16)." if agg[max(KAPPAS)]["mean_cred"] - base > 0.02 else
               "No κ-selection at this CV/band-size — the forest gradient (CV 0.73) may be too weak; "
               "test savanna (CV 2.24) or smaller bands. A null WITH G.3 on is the real finding.")
    print(f"\n[3a] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
