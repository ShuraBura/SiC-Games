"""Aggregation-sedentism LAYER 1 validation. The gathering (marriage-aggregation) is ON in BOTH arms; only
enable_aggregation_sedentism is toggled. Question: does letting the seasonal gathering PERSIST at persistent-
abundant reaches produce SETTLEMENTS that hold a multi-band pool and cross Binford packing (0.091) → morph,
where single-band tethering could not? Reside-on-cluster harvest (Layer 1); catchment foraging is Layer 2.

Run:  py -3 -u outputs/climate_viz/run_aggregation_layer1.py
"""
import sys, os
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

FOUNDERS, STEPS, PACK = 400, 1200, 0.091


def run(settle):
    k = world_lottery_climate(0, terrain="mountainous", climate="tropical")
    f = generate_world(k, mode="climate")
    cap = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    aq = f.aquatic_food
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
        enable_marriage_aggregation=True, enable_aggregation_sedentism=settle))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    tag = "SETTLE" if settle else "  OFF "
    print(f"  [{tag}] {len(reach)} reach cells, {FOUNDERS} founders on the reach zone", flush=True)
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print(f"  [{tag}] EXTINCT at {i+1}", flush=True); return
        if i % 200 == 199 or i == STEPS - 1:
            bm = defaultdict(int); bc = defaultdict(set)
            for a in al:
                bm[a._group.band_id] += 1; bc[a._group.band_id].add(a.pos)
            dens = [bm[b] / (len(bc[b]) * _CELL_KM2) for b in bm]
            packed = sum(1 for d in dens if d >= PACK) / len(dens)
            soc = Counter(w._band_society.get(b) for b in bm)
            cplx = (soc.get("complex_forager", 0) + soc.get("stratified_chiefdom", 0)) / max(1, sum(soc.values()))
            sites = w._settlement_sites
            rad = w._demog.settle_radius
            spop = []
            for s in sites:
                n = sum(1 for a in al if w._torus_cheby(a.pos[0], a.pos[1], s[0], s[1]) <= rad)
                spop.append(n)
            print(f"  [{tag}] step {i+1:4d}: pop={len(al):4d}  settlements={len(sites):2d}  "
                  f"max_settle_pop={max(spop) if spop else 0:4d}  band_dens_max={max(dens):.3f}  "
                  f"%packed={100*packed:3.0f}%  %cplx={100*cplx:3.0f}%", flush=True)


def main():
    print(f"AGGREGATION-SEDENTISM LAYER 1 — gathering ON both arms; does persistence make settlements pack?\n")
    run(False)
    print()
    run(True)


if __name__ == "__main__":
    main()
