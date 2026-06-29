"""Storage-tethering RETIREMENT test (the tether was DELETED 2026-06-29 on the strength of this run).

The tether (storage_tether_reserves) was a band-aid: pre-bands diffusion left max-occupancy ~2 so no cell ever
reached Binford packing → the §4.5.11 society morph could only fire if a stocked band was nailed in place. With
emergent bands (E.1/E.2 grouping + F.1/F.2 bonded mating) the morph fires from emergent density+storage ALONE.

ORIGINAL COMPARISON (5 seeds × 800 steps, before deletion) — recorded for the record:
    arm        pop  max_occ  packed_peak  ever_morphed  complex_end  strat_end
    NO-tether  195    11.8        4.8         250.0        220.4        0.0
    tether0.5  746    38.0       35.8          56.8         21.4       27.0
⇒ the morph fires WITHOUT the tether (packing reached, 220 cells morph to complex_forager). The tether's only
distinct effects were OVER-concentration artifacts (≈4× pop, a few cells forced to surplus≥0.7 → stratified) —
stratified chiefdoms from generic foraging are themselves an artifact (they need a delayed-return surplus base).
The tether config field + movement block were removed; this script now confirms the morph fires on the corrected
substrate (single no-tether arm). Run:  py -3 -u outputs/phase1_biome_mortality/run_3h_tether_retirement.py
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
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT, BINFORD_PACKING_PER_KM2
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, N as GRID_N
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
SEEDS = list(range(5))
STEPS, FOUNDERS = 800, 300
PACK_OCC = BINFORD_PACKING_PER_KM2 * _CELL_KM2     # occupants/cell == packing density (≈9.1)
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


def band_positions_patch(fields, cap, n, band_size=25, territory_radius=4):
    cells = sorted(((cap.level(x, y), x, y) for y in range(GRID_N) for x in range(GRID_N)
                    if fields.isWater[y, x] == 0 and cap.level(x, y) > 0), reverse=True)
    sites, pos = [], []
    for (_, x, y) in cells:
        if len(sites) >= max(1, n // band_size):
            break
        if all(max(abs(x - px), abs(y - py)) >= territory_radius for (px, py) in sites):
            sites.append((x, y)); pos.extend([(x, y)] * band_size)
    i = 0
    while len(pos) < n and sites:
        pos.append(sites[i % len(sites)]); i += 1
    return pos[:n]


def run_one(seed):
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, cap, FOUNDERS)
    demog = DemographyConfig(
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
        enable_game=True, game_meat_frac=0.55, game_meat_cv=0.73,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_prowess_facet=True, prowess_decay=0.1, sex_division=1.0,
        enable_paternity=True, mate_choice_strength=5.0, patriline_weight=0.5, lineage_reversion=0.1,
        enable_bonded_mating=True, bonded_mate_radius=1,
        enable_storage=True, storable_fraction=0.5, store_capacity_reserves=3.0,
        storage_temp_threshold_c=100.0,                 # overwinter everywhere (isolate the concentration question)
        enable_morph=True, morph_settle_steps=80)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    ever_morphed = 0
    max_occ_seen = 0
    packed_cells_peak = 0
    for _ in range(STEPS):
        w.step()
        occ = Counter(a.pos for a in w.agent_list)
        if occ:
            max_occ_seen = max(max_occ_seen, max(occ.values()))
            packed_cells_peak = max(packed_cells_peak, sum(1 for v in occ.values() if v >= PACK_OCC))
        ever_morphed = max(ever_morphed, len(w._cell_society))
    morphed_now = Counter(w._cell_society.values())
    return dict(pop=len(w.agent_list), max_occ=max_occ_seen, packed_peak=packed_cells_peak,
                ever_morphed=ever_morphed, complex_now=morphed_now.get("complex_forager", 0),
                strat_now=morphed_now.get("stratified_chiefdom", 0))


def main():
    t0 = time.time()
    print(f"packing threshold = {PACK_OCC:.1f} occupants/cell (Binford 0.091/km^2 x {_CELL_KM2:.0f} km^2)")
    print(f"{'arm':>10} {'pop':>5} {'max_occ':>8} {'packed_peak':>12} {'ever_morphed':>13} {'complex_end':>12} {'strat_end':>10}")
    rows = [run_one(s) for s in SEEDS]                       # tether removed from the model → single arm
    agg = {k: statistics.mean([r[k] for r in rows]) for k in rows[0]}
    print(f"{'NO-tether':>10} {agg['pop']:>5.0f} {agg['max_occ']:>8.1f} {agg['packed_peak']:>12.1f} "
          f"{agg['ever_morphed']:>13.1f} {agg['complex_now']:>12.1f} {agg['strat_now']:>10.1f}  "
          f"[{time.time()-t0:.0f}s]", flush=True)
    verdict = ("CONFIRMED RETIRED: morph fires on the corrected substrate without any tether (packing reached + "
               "cells morphed)."
               if agg["ever_morphed"] >= 1 and agg["packed_peak"] >= 1 else
               "REGRESSION: morph no longer fires — investigate (packing or morph missing).")
    print(f"\nVERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
