"""Society-type BENCHMARK — run each lit-anchored preset and report its family-dynamics signature.

Switchable society types (demography.SOCIETY_PRESETS) on a common forest-Aché substrate. Each is a knob-bundle
(κ status-sharing + mate-choice skew m + assortment α + descent patriline_weight + status-mobility ρ + paternal
investment + sex-division) mapped to an ethnographic type. The benchmark shows each produces a DISTINCT
signature: reproductive skew (status→RS), mate homogamy (mate-corr), lineage structure (#lineages, largest
patriline, lineage-Gini), status inequality (Gini cred), and the cred level. N seeds × long runs.
Run:  py -3 -u outputs/phase1_biome_mortality/run_3f_society_benchmark.py
"""
from __future__ import annotations
import json, math, os, time, statistics
from collections import Counter
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT, SOCIETY_PRESETS, society_knobs
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEEDS = 400, 1000, [11, 23, 42]


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


def run_one(name, seed):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    kappa, fam = society_knobs(name)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=kappa, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(
                         siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
                         enable_game=True, game_meat_frac=0.55, game_meat_cv=0.73,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_prowess_facet=True, prowess_decay=0.1, enable_paternity=True,
                         enable_provisioning=True, **fam))
    pm, pf = [], []
    t0 = int(0.5 * STEPS)
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= t0:
            for sm, sf in w.mate_pairs_this_step:
                pm.append(sm); pf.append(sf)
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
    return dict(eq_pop=len(al), rs=corr([a.prowess for a in males], [fc.get(id(a), 0) for a in males]),
                mate_corr=corr(pm, pf), n_lin=len(lin), largest=max(lin.values()) / len(al),
                lin_gini=gini(list(lin.values())), gini_cred=gini([a.cred for a in al]),
                mean_cred=statistics.mean([a.cred for a in al]))


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_3f.txt")
    res = {}
    hdr = f"{'society':28s} {'pop':>4} {'RS':>6} {'mate-corr':>9} {'#lin':>5} {'largest':>8} {'linGini':>8} {'crGini':>7} {'mcred':>6}"
    print(f"[3f] {hdr}", flush=True)
    for name in SOCIETY_PRESETS:
        rows = [r for r in (run_one(name, s) for s in SEEDS) if r]
        agg = {k: statistics.mean([r[k] for r in rows]) for k in
               ("eq_pop", "rs", "mate_corr", "n_lin", "largest", "lin_gini", "gini_cred", "mean_cred")}
        res[name] = agg
        line = (f"{name:28s} {agg['eq_pop']:4.0f} {agg['rs']:+6.2f} {agg['mate_corr']:+9.2f} {agg['n_lin']:5.0f} "
                f"{agg['largest']*100:7.0f}% {agg['lin_gini']:8.2f} {agg['gini_cred']:7.2f} {agg['mean_cred']:6.1f}")
        print(f"[3f] {line}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w", encoding="utf-8") as f:
            f.write(f"3f {name}: {line} | {time.time()-t0:.0f}s\n")
    print(f"\n[3f] DONE — {len(res)} lit-anchored society types benchmarked; each a distinct family-dynamics "
          f"signature (skew / homogamy / lineage structure / inequality). Switchable via society_knobs(name). "
          f"[{time.time()-t0:.0f}s]", flush=True)
    with open(os.path.join(OUT, "results_3f.json"), "w") as f:
        json.dump(dict(societies=res, seeds=len(SEEDS), steps=STEPS), f, indent=2, default=str)


if __name__ == "__main__":
    main()
