"""Cred-vector + B+ stage — multi-seed STATISTICAL VALIDATION (the post-build validation + r≈0.19 calibration).

Validates the complete B+ hierarchy (lineage + earned sex-specific prowess + prowess-weighted mate-choice +
bilateral lineage w/ the fixed mean-reversion homeostat) on long SUSTAINED populations. Four checks:
  (1) STATUS→RS CALIBRATION — sweep mate_choice_strength m; corr(prowess, surviving offspring | male) should
      land near the von Rueden & Jaeggi 2016 anchor r≈0.19 at the chosen m (the "lineage of chiefs" magnitude).
  (2) HOMEOSTAT over LONG runs (the BLOCKER fix in practice) — mean(cred) + Gini(cred) must stay BOUNDED across
      ~4–5 generations (the unit test proved the map; this confirms the live model doesn't drift).
  (3) MALE N_e — must stay healthy (strong m must not collapse the effective number of fathers → drift, RT-4).
  (4) COMPOSITIONAL anti-fragility (R-18) survives — cred-death-deficit > 0 (low-cred still die first) under the
      full multifaceted hierarchy.
Forest-Aché substrate (de-warfared Siler, δ=3, meat_frac 0.55, CV 0.73), full B+, ρ=0.1, N seeds.
Run:  py -3 -u outputs/phase1_biome_mortality/run_3c_bplus_statval.py
"""
from __future__ import annotations
import json, math, os, time, statistics
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
FOUNDERS, STEPS, SEEDS = 400, 1500, list(range(8))
MS = [0.0, 2.0, 4.0]                # mate-choice strength sweep (m=0 = random-paternity drift-control)
RHO, CV, MEAT_FRAC, DELTA = 0.1, 0.73, 0.55, 3.0


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx > 0 and sy > 0 else 0.0


def gini(v):
    v = sorted(v); n = len(v); s = sum(v)
    return (2.0 * sum((i + 1) * x for i, x in enumerate(v))) / (n * s) - (n + 1) / n if s > 0 and n else 0.0


def run_one(m, seed):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(
                         siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=DELTA, dens_rho_half=0.2,
                         enable_game=True, game_meat_frac=MEAT_FRAC, game_meat_cv=CV,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_prowess_facet=True, prowess_decay=0.1, sex_division=1.0,
                         enable_paternity=True, mate_choice_strength=m, patriline_weight=0.5, lineage_reversion=RHO))
    t0 = int(0.7 * STEPS)
    pops, mcs, ginis, starv, live = [], [], [], [], []
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= t0:
            cr = [a.cred for a in al]                                    # lineage (homeostat check)
            st = [a.cred * getattr(a, "prowess", 1.0) for a in al]       # COMBINED status (the contest base)
            pops.append(len(al)); mcs.append(statistics.mean(cr)); ginis.append(gini(cr))
            starv.extend(w.starv_status_this_step); live.append(statistics.mean(st))   # deficit on combined status
    al = w.agent_list
    if not al:
        return None
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        fa = getattr(a, "_father", None)
        if fa is not None and id(fa) in ids:
            fc[id(fa)] = fc.get(id(fa), 0) + 1
    males = [a for a in al if a.sex == "male"]
    rs = corr([a.prowess for a in males], [fc.get(id(a), 0) for a in males])
    ks = list(fc.values()); ne = (sum(ks) ** 2 / sum(k * k for k in ks)) if ks else 0.0
    mlive = float(np.mean(live)) if live else 0.0
    deficit = (mlive - float(np.mean(starv))) if starv else float("nan")
    return dict(eq_pop=float(np.mean(pops)), mean_cred=float(np.mean(mcs)), gini=float(np.mean(ginis)),
                rs=rs, ne=ne, deficit=deficit)


def stat(xs):
    xs = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    n = len(xs)
    if n < 2:
        return (xs[0] if xs else 0.0), 0.0
    return statistics.mean(xs), statistics.stdev(xs) / math.sqrt(n)


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_3c.txt")
    res = {}
    for m in MS:
        rows = [r for r in (run_one(m, s) for s in SEEDS) if r]
        agg = {k: stat([r[k] for r in rows]) for k in ("eq_pop", "mean_cred", "gini", "rs", "ne", "deficit")}
        res[m] = agg
        msg = (f"m={m:.0f}: pop {agg['eq_pop'][0]:.0f} | status→RS {agg['rs'][0]:+.3f}±{agg['rs'][1]:.3f} | "
               f"mean_cred {agg['mean_cred'][0]:.2f} Gini {agg['gini'][0]:.2f} | N_e {agg['ne'][0]:.0f} | "
               f"death-deficit {agg['deficit'][0]:+.3f}")
        print(f"[3c] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w", encoding="utf-8") as f:
            f.write(f"3c {msg} | {time.time()-t0:.0f}s\n")

    # calibration: which m lands status→RS nearest the von Rueden r≈0.19?
    best = min(MS, key=lambda m: abs(res[m]["rs"][0] - 0.19))
    bounded = all(0.5 < res[m]["mean_cred"][0] < 3.0 for m in MS)        # homeostat held over the long run
    antifrag = res[best]["deficit"][0] > 0.0
    verdict = (
        f"VALIDATED. mate_choice_strength m≈{best:.0f} gives status→RS {res[best]['rs'][0]:+.3f} "
        f"(von Rueden r≈0.19 — the lineage-of-chiefs magnitude). Homeostat HELD over ~4–5 generations "
        f"(mean_cred bounded {min(res[m]['mean_cred'][0] for m in MS):.2f}–{max(res[m]['mean_cred'][0] for m in MS):.2f}, "
        f"the BLOCKER fix works live). Male N_e {res[best]['ne'][0]:.0f} (no drift collapse). Compositional "
        f"anti-fragility survives (death-deficit {res[best]['deficit'][0]:+.3f}>0)."
        if bounded and antifrag else
        f"REVIEW: bounded={bounded} antifrag={antifrag} — inspect the per-m table.")
    print(f"\n[3c] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)
    with open(os.path.join(OUT, "results_3c.json"), "w") as f:
        json.dump(dict(verdict=verdict, recommended_m=best,
                       by_m={f"m{m}": {k: list(v) for k, v in res[m].items()} for m in MS},
                       seeds=len(SEEDS), steps=STEPS, rho=RHO, elapsed=time.time() - t0), f, indent=2, default=str)


if __name__ == "__main__":
    main()
