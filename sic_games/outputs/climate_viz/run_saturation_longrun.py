"""Saturation long-run (R-51 payoff experiment): let a demographically-robust population GROW toward carrying
capacity on a normal bounded area, and watch whether — AS the land saturates — bands concentrate on the fast-
replenishing aquatic cells → cross Binford packing → the density-morph fires complexity/stratification.

This is the natural dynamic (a colonizing population filling the land until density-dependence + circumscription
bite), the thing the whole EFC + GD-1 arc was building toward. Bootstrapped with a healthy founder count so it is
demographically robust (unlike the failed 12×12 circumscription) and reaches saturation in fewer generations.

Run:  py -3 -u outputs/climate_viz/run_saturation_longrun.py
"""
import sys, os
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
from run_biome_society import realistic_forager_demog, BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, world_lottery_climate

FOUNDERS = 1000
STEPS = 3500


def run(terr, clim, seed=0):
    k = world_lottery_climate(seed, terrain=terr, climate=clim)
    f = generate_world(k, mode="climate")
    cap = NPP = __import__("sic_games.capacity", fromlist=["NPPCapacityField"]).NPPCapacityField(
        f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    cells = [(x, y) for y in range(100) for x in range(100) if cap.level(x, y) > 0]
    pos = [cells[i % len(cells)] for i in range(FOUNDERS)] if cells else []
    if not pos:
        print(f"  {terr}-{clim}: no habitable patch"); return
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=realistic_forager_demog())
    print(f"  {terr}-{clim}: patch ceiling={cap.ceiling:.0f} people, {FOUNDERS} founders", flush=True)
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print("    EXTINCT", flush=True); return
        if i % 250 == 249 or i == STEPS - 1:
            occ = Counter(a.pos for a in al)
            bm = defaultdict(int); bc = defaultdict(set)
            for a in al:
                bm[a._group.band_id] += 1; bc[a._group.band_id].add(a.pos)
            dens = [bm[b] / (len(bc[b]) * _CELL_KM2) for b in bm]
            packed = sum(1 for d in dens if d >= 0.091) / len(dens)
            soc = Counter(w._band_society.get(b) for b in bm)
            cplx = (soc.get("complex_forager", 0) + soc.get("stratified_chiefdom", 0)) / max(1, sum(soc.values()))
            print(f"    step {i+1:4d}: pop={len(al):6d} ({100*len(al)/cap.ceiling:4.0f}% of ceiling)  "
                  f"max/cell={max(occ.values()):4d}  band_dens_max={max(dens):.3f}  %packed={100*packed:3.0f}%  "
                  f"%complex={100*cplx:3.0f}%", flush=True)


def main():
    print(f"SATURATION long-run — {FOUNDERS} founders × {STEPS} steps, aquatic+depletion; watch for concentration→packing→complexity as the land fills\n")
    run("mountainous", "tropical")
    print()
    run("coastal", "temperate")


if __name__ == "__main__":
    main()
