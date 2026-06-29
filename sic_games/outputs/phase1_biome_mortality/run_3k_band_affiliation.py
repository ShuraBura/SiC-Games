"""F.3c-1 VALIDATION — the band as a first-class persistent multi-family entity (the collective-identity vector's
band_id). Targets: (1) emergent affiliation-band size ~25 (Birdsell/Wobst); (2) bands are NON-KIN / multi-lineage
(Hill 2011) — NOT single-lineage clans; (3) eq_pop preserved (cohesion didn't over-constrain movement / starve);
(4) stable band counts (no fission/fusion thrash).
Run:  py -3 -u outputs/phase1_biome_mortality/run_3k_band_affiliation.py
"""
from __future__ import annotations
import os, time, statistics
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

SEEDS = list(range(5))
STEPS, FOUNDERS, MATE_R = 1000, 300, 1
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


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


def run_one(seed, cohesion=0.3):
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, cap, FOUNDERS)
    demog = DemographyConfig(
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_prowess_facet=True, prowess_decay=0.1, sex_division=1.0, enable_paternity=True,
        mate_choice_strength=5.0, enable_bonded_mating=True, bonded_mate_radius=MATE_R,
        enable_pair_bonds=True, enable_band_affiliation=True, band_cohesion=cohesion,
        band_split_size=45, band_merge_size=10)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.0, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    t0 = int(0.6 * STEPS)
    awt, med, nb, dom, nlin, adkin = [], [], [], [], [], []
    for step in range(STEPS):
        w.step()
        if step < t0 or not w.agent_list:
            continue
        al = w.agent_list
        byb: dict = {}
        for a in al:
            byb.setdefault(a._group.band_id, []).append(a)
        sizes = [len(m) for m in byb.values()]
        tot = sum(sizes)
        awt.append(sum(n * n for n in sizes) / tot)
        med.append(statistics.median(sizes))
        nb.append(len(byb))
        # Hill-2011 non-kin test: per band, the DOMINANT-lineage share (1.0 = single-lineage clan) + # lineages
        ds, nl = [], []
        for m in byb.values():
            lc = Counter(a._lineage for a in m)
            ds.append(max(lc.values()) / len(m)); nl.append(len(lc))
        dom.append(statistics.mean(ds)); nlin.append(statistics.mean(nl))
        # adult-only kin co-residence (adults are mostly non-kin in real bands)
        adults = [a for a in al if a.age >= 180]
        if adults:
            k = sum(1 for a in adults if (a._mother is not None and a._mother.alive and a._mother._group.band_id == a._group.band_id)
                    or (a._father is not None and a._father.alive and a._father._group.band_id == a._group.band_id))
            adkin.append(k / len(adults))
    m = lambda xs: statistics.mean(xs) if xs else 0.0
    return dict(pop=len(w.agent_list), awt=m(awt), med=m(med), nbands=m(nb),
                dom_lineage=m(dom), n_lineages=m(nlin), adult_kin=m(adkin))


def main():
    t0 = time.time()
    rows = [run_one(s) for s in SEEDS]
    agg = {k: statistics.mean([r[k] for r in rows]) for k in rows[0]}
    print(f"F.3c-1 band affiliation (CC-1 patch, {len(SEEDS)} seeds × {STEPS} steps, tail 40%)")
    print(f"  affiliation-band size:  agent-weighted {agg['awt']:.1f} | median {agg['med']:.1f} | "
          f"n_bands {agg['nbands']:.1f}   (target ~25, Birdsell/Wobst)")
    print(f"  composition (Hill 2011): dominant-lineage share {agg['dom_lineage']:.2f} (1.0=clan) | "
          f"distinct lineages/band {agg['n_lineages']:.1f} | adult-with-parent-in-band {agg['adult_kin']:.2f}")
    print(f"  eq_pop {agg['pop']:.0f}  [{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
