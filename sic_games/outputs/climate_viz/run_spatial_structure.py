"""Investigate WHY the population is a continuous BLANKET instead of discrete bands/villages with empty gaps.
Candidates: (1) abundant contiguous resources (vs patchy scarce_arable), (2) spread seed (vs clustered founding bands),
(3) missing between-band TERRITORIALITY (all village mechanisms pull TOGETHER; no spacing). Measure the emergent
spatial structure: # connected occupied components (discrete settlements?), largest component, % land occupied.

Run:  py -3 -u outputs/climate_viz/run_spatial_structure.py
"""
import sys, os
import numpy as np
from collections import Counter
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

STEPS = 150


def _seed(f, hf, n, clustered):
    prod = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    if not clustered:
        return [prod[i % len(prod)] for i in range(n)]
    # clustered: n agents in ~n/100 founding bands (100 each) on the richest cells, min-separated
    rich = sorted(prod, key=lambda c: hf.level(*c), reverse=True)
    sites, pos = [], []
    for c in rich:
        if len(sites) >= max(1, n // 100):
            break
        if all(max(abs(c[0] - s[0]), abs(c[1] - s[1])) >= 8 for s in sites):
            sites.append(c)
    for i in range(n):
        pos.append(sites[i % len(sites)])
    return pos


def _run(scarce, clustered, n=2000):
    k = world_lottery_climate(0, terrain="flat", climate="temperate", scarce_arable=scarce)
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True), a_seas=0.5)
    pos = _seed(f, hf, n, clustered)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=emergent_village_demog())
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    land = int((f.isWater == 0).sum())
    grid = np.zeros((100, 100), dtype=int)
    for (x, y), nn in occ.items():
        grid[y, x] = 1
    lbl, ncomp = ndimage.label(grid)                       # connected occupied components (settlements)
    sizes = ndimage.sum(grid, lbl, range(1, ncomp + 1)) if ncomp else np.array([0])
    return dict(pop=len(al), occ=len(occ), pct_land=100 * len(occ) / land, ncomp=ncomp,
                largest=int(sizes.max()), pop_in_largest=100 * sum(n for (x, y), n in occ.items() if lbl[y, x] == np.argmax(sizes) + 1) / len(al))


def main():
    print(f"SPATIAL STRUCTURE — discrete settlements vs continuous blanket ({STEPS} steps, 2000 agents).")
    print("  Realistic = MANY small components (discrete bands/villages) + LOW %land occupied + gaps.\n")
    print(f"  {'world':30s} {'pop':>5} {'occ_cells':>9} {'%land':>6} {'#components':>11} {'largest_cells':>13} {'%pop_largest':>12}")
    for scarce in (False, True):
        for clustered in (False, True):
            r = _run(scarce, clustered)
            tag = f"{'scarce' if scarce else 'abundant'}, {'clustered' if clustered else 'spread'} seed"
            if r is None:
                print(f"  {tag:30s} EXTINCT"); continue
            print(f"  {tag:30s} {r['pop']:5.0f} {r['occ']:9.0f} {r['pct_land']:5.0f}% {r['ncomp']:11d} {r['largest']:13d} {r['pop_in_largest']:11.0f}%")


if __name__ == "__main__":
    main()
