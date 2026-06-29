"""F.3c-3 VALIDATION — dynamic, condition-dependent fission/fusion + the assabiyah seam. Under a REALISTIC storage
threshold (only cold/overwintering bands accumulate surplus), bands should DIFFERENTIATE: rich/high-solidarity
(high-assabiyah) bands stay together LARGER; poor (low-surplus) bands fission at the base ~25. Validate the
positive band-size ↔ assabiyah/surplus correlation (condition-dependent band size) + eq_pop preserved + stability.
Run:  py -3 -u outputs/phase1_biome_mortality/run_3l_dynamic_bands.py
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

SEEDS = list(range(5))
STEPS, FOUNDERS = 1000, 300
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx > 0 and sy > 0 else 0.0


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


def run_one(seed, dynamic=True, temp_thr=15.25):
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, cap, FOUNDERS)
    d = dict(siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
             enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
             enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
             enable_prowess_facet=True, prowess_decay=0.1, sex_division=1.0, enable_paternity=True,
             mate_choice_strength=5.0, enable_bonded_mating=True, bonded_mate_radius=1, enable_pair_bonds=True,
             enable_band_affiliation=True, band_cohesion=0.3, band_split_size=45, band_merge_size=10,
             enable_storage=True, storable_fraction=0.5, store_capacity_reserves=3.0, storage_temp_threshold_c=temp_thr,
             storage_decay=0.05, enable_morph=True, morph_settle_steps=60)
    if dynamic:
        d.update(enable_dynamic_bands=True, band_base_tolerable=25, assabiyah_gain=0.05, assabiyah_decay=0.02)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed), game_stream=False,
                     seed=seed, carbon_cfg=CarbonConfig(kappa=1.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.0, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=DemographyConfig(**d))
    t0 = int(0.6 * STEPS)
    rho_assab, medsz, maxsz, popz, assz = [], [], [], [], []
    for step in range(STEPS):
        w.step()
        if step < t0 or not w.agent_list:
            continue
        sizes = Counter(a._group.band_id for a in w.agent_list)
        bids = [b for b in sizes if sizes[b] >= 2]
        if len(bids) >= 3:
            sz = [sizes[b] for b in bids]
            ab = [w._band_assabiyah.get(b, 0.0) for b in bids]
            rho_assab.append(corr(ab, sz))                      # per-band assabiyah ↔ size
            assz.append(statistics.mean(ab))
            medsz.append(statistics.median(sz)); maxsz.append(max(sz))
        popz.append(len(w.agent_list))
    m = lambda xs: statistics.mean(xs) if xs else 0.0
    return dict(pop=m(popz), med=m(medsz), mx=m(maxsz), assab=m(assz), rho_assab_size=m(rho_assab))


def main():
    t0 = time.time()
    print(f"F.3c-3 dynamic bands + assabiyah (CC-1 patch, realistic temp_thr=15.25, {len(SEEDS)} seeds × {STEPS} steps)")
    for dyn in (False, True):
        rows = [run_one(s, dynamic=dyn) for s in SEEDS]
        agg = {k: statistics.mean([r[k] for r in rows]) for k in rows[0]}
        lab = "DYNAMIC " if dyn else "HARD-thr"
        print(f"  [{lab}] pop {agg['pop']:.0f} | median band {agg['med']:.1f} | max {agg['mx']:.1f} | "
              f"mean assabiyah {agg['assab']:.2f} | corr(assabiyah,size) {agg['rho_assab_size']:+.2f}  "
              f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
