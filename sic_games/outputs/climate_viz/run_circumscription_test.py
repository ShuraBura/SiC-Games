"""Circumscription verification (R-51 follow-up): does SATURATING a bounded rich habitable area make bands
concentrate on the fast-replenishing aquatic cells → cross Binford packing → the density-morph fire complexity?

R-51 found sedentism is blocked because on the normal 40×40 patch the population fills only ~0.4% of capacity
(slow-growth transient) → no circumscription → IFD always disperses. Here we CIRCUMSCRIBE: a small patch placed on
the aquatic-richest region, so a modest population saturates it in a normal-length run (Carneiro's literal
circumscription). If saturation → concentration → packing → stratification, the whole aquatic complexity chain is
confirmed (EFC + GD-1 + circumscription → complexity).

Run:  py -3 -u outputs/climate_viz/run_circumscription_test.py
"""
import sys, os, statistics
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
from run_biome_society import realistic_forager_demog, BURN, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
import numpy as np

PATCH = 12          # small circumscribed window (12×12 = 144 cells)
STEPS = 2000
FOUNDERS = 200


def best_aquatic_patch(f, cap_ppl):
    """Find the PATCH×PATCH window with the most aquatic-food + capacity (a rich circumscribed area)."""
    best, bxy = -1.0, (44, 44)
    aq = f.aquatic_food
    for y0 in range(0, 100 - PATCH, 4):
        for x0 in range(0, 100 - PATCH, 4):
            w = aq[y0:y0 + PATCH, x0:x0 + PATCH]
            land = (f.isWater[y0:y0 + PATCH, x0:x0 + PATCH] == 0)
            score = w.sum() + 0.001 * cap_ppl[y0:y0 + PATCH, x0:x0 + PATCH].sum() + land.sum() * 0.01
            if score > best:
                best, bxy = score, (x0, y0)
    return bxy


def run(terr, clim, seed=0):
    k = world_lottery_climate(seed, terrain=terr, climate=clim)
    f = generate_world(k, mode="climate")
    cap_ppl = np.where(f.isWater == 0, __import__("sic_games.capacity", fromlist=["density_tallavaara"]).density_tallavaara(f.npp_gm2), 0.0)
    x0, y0 = best_aquatic_patch(f, cap_ppl)
    cap = NPPCapacityField(f, BURN, patch=(x0, y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    cells = [(x, y) for y in range(100) for x in range(100) if cap.level(x, y) > 0]
    pos = [cells[i % len(cells)] for i in range(FOUNDERS)] if cells else []
    if not pos:
        return None
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=realistic_forager_demog())
    print(f"  {terr}-{clim}: patch at ({x0},{y0}) ceiling={cap.ceiling:.0f} people; trajectory:")
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print("    EXTINCT"); return None
        if i % 400 == 399 or i == STEPS - 1:
            occ = Counter(a.pos for a in al)
            bm = defaultdict(int); bc = defaultdict(set)
            for a in al:
                bm[a._group.band_id] += 1; bc[a._group.band_id].add(a.pos)
            dens = [bm[b] / (len(bc[b]) * _CELL_KM2) for b in bm]
            packed = sum(1 for d in dens if d >= 0.091) / len(dens)
            soc = Counter(w._band_society.get(b) for b in bm)
            cplx = (soc.get("complex_forager", 0) + soc.get("stratified_chiefdom", 0)) / max(1, sum(soc.values()))
            print(f"    step {i+1:4d}: pop={len(al):5d} ({100*len(al)/cap.ceiling:3.0f}% of ceiling)  max/cell={max(occ.values()):3d}"
                  f"  band_dens_max={max(dens):.3f}  %packed={100*packed:3.0f}%  %complex={100*cplx:3.0f}%")
    return True


def main():
    print(f"CIRCUMSCRIPTION test — bounded {PATCH}×{PATCH} rich patch, saturate it, watch for concentration→packing→complexity\n")
    for terr, clim in [("coastal", "temperate"), ("mountainous", "tropical")]:
        run(terr, clim)
        print()


if __name__ == "__main__":
    main()
