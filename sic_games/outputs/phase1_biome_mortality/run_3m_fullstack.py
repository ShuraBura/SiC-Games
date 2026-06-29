"""FULL-STACK integration validation. Every social-architecture layer ON at once, on the corrected CC-1 substrate:
Carbon status (cred+prowess+paternity) · game/meat variance · density-disease · F.1/F.2 bonded mating · F.3a/b
persistent families + co-movement · F.3c-1 band affiliation (the collective-identity vector) · F.3c-2 per-band
society morph · F.3c-2b per-band family knobs · F.3c-3 dynamic fission/fusion + assabiyah. The gate: does the
whole thing COHERE (sustains, healthy demography) AND do the validated core results SURVIVE with everything
stacked — status→RS (von Rueden ~0.19), R-18 compositional anti-fragility (death-deficit>0), the cred homeostat,
healthy N_e, ~25 non-kin bands, per-band societies?
Run:  py -3 -u outputs/phase1_biome_mortality/run_3m_fullstack.py
"""
from __future__ import annotations
import os, time, math, statistics
from collections import Counter

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, N as GRID_N
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

SEEDS = list(range(6))
STEPS, FOUNDERS = 1500, 300
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


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


def band_positions_patch(fields, cap, n, band_size=25, sep=4):
    cells = sorted(((cap.level(x, y), x, y) for y in range(GRID_N) for x in range(GRID_N)
                    if fields.isWater[y, x] == 0 and cap.level(x, y) > 0), reverse=True)
    sites, pos = [], []
    for (_, x, y) in cells:
        if len(sites) >= max(1, n // band_size):
            break
        if all(max(abs(x - px), abs(y - py)) >= sep for (px, py) in sites):
            sites.append((x, y)); pos.extend([(x, y)] * band_size)
    i = 0
    while len(pos) < n and sites:
        pos.append(sites[i % len(sites)]); i += 1
    return pos[:n]


def run_one(seed, polygyny_rate=0.0, max_wives=1):
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, cap, FOUNDERS)
    demog = DemographyConfig(
        polygyny_rate=polygyny_rate, max_wives=max_wives,
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
        enable_game=True, game_meat_frac=0.55, game_meat_cv=0.73,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_prowess_facet=True, prowess_decay=0.1, sex_division=1.0,
        enable_paternity=True, mate_choice_strength=5.0, patriline_weight=0.5, lineage_reversion=0.1,
        enable_bonded_mating=True, bonded_mate_radius=1,
        enable_pair_bonds=True,                                   # F.3a/b
        enable_band_affiliation=True, band_cohesion=0.3, band_split_size=45, band_merge_size=10,   # F.3c-1
        enable_storage=True, storable_fraction=0.5, store_capacity_reserves=3.0,
        storage_temp_threshold_c=100.0, storage_decay=0.05, enable_morph=True, morph_settle_steps=60,   # F.3c-2
        enable_band_family_knobs=True,                           # F.3c-2b
        enable_dynamic_bands=True, band_base_tolerable=25, assabiyah_gain=0.05, assabiyah_decay=0.02)   # F.3c-3
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    t0 = int(0.6 * STEPS)
    pops, mcred, ginis, live_status, starv_status = [], [], [], [], []
    awt_band, kin_dom, assab, soc = [], [], [], []
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= t0:
            pops.append(len(al))
            mcred.append(statistics.mean([a.cred for a in al]))
            ginis.append(gini([a.cred for a in al]))
            live_status.append(statistics.mean([a.cred * getattr(a, "prowess", 1.0) for a in al]))
            starv_status.extend(w.starv_status_this_step)
            byb: dict = {}
            for a in al:
                byb.setdefault(a._group.band_id, []).append(a)
            sz = [len(m) for m in byb.values()]; tot = sum(sz)
            awt_band.append(sum(n * n for n in sz) / tot if tot else 0.0)
            kin_dom.append(statistics.mean([max(Counter(x._lineage for x in m).values()) / len(m) for m in byb.values()]))
            assab.append(statistics.mean(list(w._band_assabiyah.values())) if w._band_assabiyah else 0.0)
            soc.append(len([1 for s in w._band_society.values() if s != "egalitarian_forager"]) / max(1, len(byb)))
    al = w.agent_list
    if not al:
        return dict(extinct=True)
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        fa = getattr(a, "_father", None)
        if fa is not None and id(fa) in ids:
            fc[id(fa)] = fc.get(id(fa), 0) + 1
    males = [a for a in al if a.sex == "male"]
    rs = corr([a.prowess for a in males], [fc.get(id(a), 0) for a in males])
    ks = list(fc.values()); ne = (sum(ks) ** 2 / sum(k * k for k in ks)) if ks else 0.0
    deficit = (statistics.mean(live_status) - statistics.mean(starv_status)) if starv_status else float("nan")
    m = lambda xs: statistics.mean([x for x in xs if not (isinstance(x, float) and math.isnan(x))]) if xs else 0.0
    return dict(extinct=False, eq_pop=m(pops), mean_cred=m(mcred), gini=m(ginis), rs=rs, ne=ne, deficit=deficit,
                band=m(awt_band), kin_dom=m(kin_dom), assab=m(assab), morph_frac=m(soc))


def main():
    t0 = time.time()
    for lab, pr, mw in (("MONOGAMY", 0.0, 1), ("POLYGYNY", 0.3, 3)):
        rows = [run_one(s, polygyny_rate=pr, max_wives=mw) for s in SEEDS]
        ok = [r for r in rows if not r.get("extinct")]
        print(f"\n[{lab}] full-stack ({len(SEEDS)} seeds × {STEPS} steps; {len(ok)} non-extinct)")
        if not ok:
            print("  ALL EXTINCT — does not cohere."); continue
        agg = {k: statistics.mean([r[k] for r in ok]) for k in ("eq_pop", "mean_cred", "gini", "rs", "ne",
                                                                 "deficit", "band", "kin_dom", "assab", "morph_frac")}
        print(f"  eq_pop {agg['eq_pop']:.0f} | N_e {agg['ne']:.0f} | STATUS→RS {agg['rs']:+.3f} (von Rueden 0.19) | "
              f"death-deficit {agg['deficit']:+.3f}")
        print(f"  mean_cred {agg['mean_cred']:.2f} Gini {agg['gini']:.2f} | band {agg['band']:.1f} "
              f"dom-lineage {agg['kin_dom']:.2f} morphed {agg['morph_frac']:.2f} assabiyah {agg['assab']:.2f}  "
              f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
