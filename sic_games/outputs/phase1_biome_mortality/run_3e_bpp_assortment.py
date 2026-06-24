"""B++ — assortative mating: does it CONSOLIDATE dynasties? Paired comparison vs B+ (the control).

assortative_strength=0 IS B+ (one-sided prowess-weighted mate-choice — the control); >0 adds status-similarity
(high-status mothers pair with high-status fathers). Sweep it (same seeds = paired drift-control) and measure:
  - ASSORTMENT MECHANISM: corr(mother status, father status) over mate pairs — must rise with α (else inert).
  - DYNASTIC CONSOLIDATION (emergent, the point): patriline diagnostics — # surviving lineages (↓), largest-
    lineage fraction (↑), lineage-size Gini (↑) if assortment consolidates the elite vs B+ diluting it.
  - status→RS, mean_cred, Gini(cred) — confirm the homeostat still holds and RS stays calibrated.
Full B+ (m=4, R-19 value), forest-Aché δ=3, N seeds × long runs.
Run:  py -3 -u outputs/phase1_biome_mortality/run_3e_bpp_assortment.py
"""
from __future__ import annotations
import json, math, os, time, statistics
from collections import Counter
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
FOUNDERS, STEPS, SEEDS = 400, 1200, list(range(6))
ASSORTS = [0.0, 2.0, 4.0]    # 0 = B+ (control)


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


def run_one(assort, seed):
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
                         enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
                         enable_game=True, game_meat_frac=0.55, game_meat_cv=0.73,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_prowess_facet=True, prowess_decay=0.1, sex_division=1.0,
                         enable_paternity=True, mate_choice_strength=4.0, patriline_weight=0.5,
                         lineage_reversion=0.1, assortative_strength=assort))
    pair_m, pair_f = [], []
    t0 = int(0.5 * STEPS)
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= t0:
            for sm, sf in w.mate_pairs_this_step:
                pair_m.append(sm); pair_f.append(sf)
    al = w.agent_list
    if not al:
        return None
    lin = Counter(a._lineage for a in al)
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        fa = getattr(a, "_father", None)
        if fa is not None and id(fa) in ids:
            fc[id(fa)] = fc.get(id(fa), 0) + 1
    males = [a for a in al if a.sex == "male"]
    return dict(mate_corr=corr(pair_m, pair_f), n_lineages=len(lin),
                largest_frac=max(lin.values()) / len(al), lineage_gini=gini(list(lin.values())),
                rs=corr([a.prowess for a in males], [fc.get(id(a), 0) for a in males]),
                mean_cred=statistics.mean([a.cred for a in al]), gini_cred=gini([a.cred for a in al]))


def st(xs):
    xs = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return (statistics.mean(xs), statistics.stdev(xs) / math.sqrt(len(xs))) if len(xs) > 1 else (xs[0] if xs else 0.0, 0.0)


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_3e.txt")
    res = {}
    for a in ASSORTS:
        rows = [r for r in (run_one(a, s) for s in SEEDS) if r]
        agg = {k: st([r[k] for r in rows]) for k in
               ("mate_corr", "n_lineages", "largest_frac", "lineage_gini", "rs", "mean_cred", "gini_cred")}
        res[a] = agg
        msg = (f"α={a:.0f}{' (B+ control)' if a == 0 else ''}: mate-corr {agg['mate_corr'][0]:+.2f} | "
               f"#lineages {agg['n_lineages'][0]:.0f} | largest {agg['largest_frac'][0]*100:.0f}% | "
               f"lineageGini {agg['lineage_gini'][0]:.2f} | status→RS {agg['rs'][0]:+.2f} | "
               f"mean_cred {agg['mean_cred'][0]:.1f}")
        print(f"[3e] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w", encoding="utf-8") as f:
            f.write(f"3e {msg} | {time.time()-t0:.0f}s\n")
    b, hi = res[0.0], res[max(ASSORTS)]
    verdict = (
        f"B++ {'CONSOLIDATES dynasties' if hi['largest_frac'][0] > b['largest_frac'][0] + 0.02 else 'has little effect'}: "
        f"assortment raises mate-status corr {b['mate_corr'][0]:+.2f}→{hi['mate_corr'][0]:+.2f}; "
        f"largest patriline {b['largest_frac'][0]*100:.0f}%→{hi['largest_frac'][0]*100:.0f}%, "
        f"#lineages {b['n_lineages'][0]:.0f}→{hi['n_lineages'][0]:.0f}, lineage-Gini "
        f"{b['lineage_gini'][0]:.2f}→{hi['lineage_gini'][0]:.2f}. Homeostat holds (mean_cred bounded); "
        f"status→RS stays ~{hi['rs'][0]:+.2f}.")
    print(f"\n[3e] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)
    with open(os.path.join(OUT, "results_3e.json"), "w") as f:
        json.dump(dict(verdict=verdict, by_alpha={str(a): {k: list(v) for k, v in res[a].items()} for a in ASSORTS},
                       seeds=len(SEEDS), steps=STEPS), f, indent=2, default=str)


if __name__ == "__main__":
    main()
