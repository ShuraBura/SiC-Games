"""Does the mechanism ITSELF work when it can bootstrap? Seed the population DENSELY onto the aquatic-rich reaches
(supplying the density foothold that IFD/unsaturated-land denies) and lower claim_min to a pioneer level, then
compare OFF vs ON. If ON HOLDS the bands concentrated on the owned reaches (density crosses packing 0.091, owned
cells stay filled) while OFF lets IFD disperse them off → the ownership+tether mechanism works; the remaining gap
is purely getting the population TO the reaches (a saturation/seeding lever), not the mechanism.

Run:  py -3 -u outputs/climate_viz/run_defensibility_demo.py
"""
import sys, os
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

FOUNDERS, STEPS, PACK = 300, 800, 0.091


def run(defend):
    k = world_lottery_climate(0, terrain="mountainous", climate="tropical")
    f = generate_world(k, mode="climate")
    cap = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    aq = f.aquatic_food
    # seed onto the reach ZONE (rich cells + a 2-ring of habitable land) at a VIABLE density — supplies the
    # foothold IFD never provides WITHOUT the over-subscription crash (fix #3).
    reach = [(x, y) for y in range(100) for x in range(100)
             if cap.level(x, y) > 0 and f.isWater[y, x] == 0 and aq[y, x] >= 0.5]
    zone = set()
    for (x, y) in reach:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cx, cy = (x + dx) % 100, (y + dy) % 100
                if cap.level(cx, cy) > 0 and f.isWater[cy, cx] == 0:
                    zone.add((cx, cy))
    zone = sorted(zone)
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_economic_defensibility=defend, defensibility_claim_min=1, defensibility_claim_dwell=6))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    tag = "DEFEND" if defend else "  OFF "
    print(f"  [{tag}] {len(reach)} reach cells (aq>=0.5), {FOUNDERS} founders seeded on them", flush=True)
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print(f"  [{tag}] EXTINCT at {i+1}", flush=True); return
        if i % 200 == 199 or i == STEPS - 1:
            occ = Counter(a.pos for a in al)
            bm = defaultdict(int); bc = defaultdict(set)
            for a in al:
                bm[a._group.band_id] += 1; bc[a._group.band_id].add(a.pos)
            dens = [bm[b] / (len(bc[b]) * _CELL_KM2) for b in bm]
            packed = sum(1 for d in dens if d >= PACK) / len(dens)
            on_reach = sum(1 for a in al if aq[a.pos[1], a.pos[0]] >= 0.5)
            owner = w._cell_owner
            oocc = [occ.get(c, 0) for c in owner]
            print(f"  [{tag}] step {i+1:4d}: pop={len(al):4d}  on_reach={100*on_reach/len(al):3.0f}%  "
                  f"band_dens_max={max(dens):.3f}  %packed={100*packed:3.0f}%  "
                  f"owned={len(owner):3d}  owned_occ_max={max(oocc) if oocc else 0:3d}", flush=True)


def main():
    print(f"ECON-DEFENSIBILITY DEMO — dense seed on reaches, claim_min=1; does ON hold concentration vs OFF?\n")
    run(False)
    print()
    run(True)


if __name__ == "__main__":
    main()
