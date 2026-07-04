"""Aggregation-sedentism LAYER 2b core — the SHOCK. A regional bad-run year scales tier-2 yield; storage
(already built) must buffer it. Question: does a settlement PERSIST through ordinary shocks (stable fishery =
NW-Coast benchmark) and only disperse on a SEVERE/multi-year shock, with storage predicting survival?

Run:  py -3 -u outputs/climate_viz/run_aggregation_shock.py
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

FOUNDERS, STEPS = 400, 1500


def run(shock, cv=0.6):
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
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
        enable_tier2_shock=shock, shock_cv=cv))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    tag = f"SHOCK cv={cv}" if shock else "  NO-SHOCK "
    print(f"  [{tag}]", flush=True)
    worst_year = (1.0, 0)
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print(f"  [{tag}] EXTINCT at {i+1}", flush=True); return
        if shock and w._tier2_shock < worst_year[0]:
            worst_year = (w._tier2_shock, i + 1)
        if i % 250 == 249 or i == STEPS - 1:
            bm = defaultdict(int); bc = defaultdict(set)
            for a in al:
                bm[a._group.band_id] += 1; bc[a._group.band_id].add(a.pos)
            dens = [bm[b] / (len(bc[b]) * _CELL_KM2) for b in bm]
            packed = sum(1 for d in dens if d >= 0.091) / len(dens)
            sites = w._settlement_sites
            store = sum(w._cell_store.get(s, 0.0) for s in sites)
            print(f"  [{tag}] step {i+1:4d}: pop={len(al):4d}  settlements={len(sites):2d}  "
                  f"shock={w._tier2_shock:.2f}  band_dens_max={max(dens):.3f}  %packed={100*packed:3.0f}%  "
                  f"site_store={store:6.0f}", flush=True)
    if shock:
        print(f"  [{tag}] worst run-year: shock={worst_year[0]:.2f} at step {worst_year[1]} — settlements survived it: "
              f"{'YES' if w._settlement_sites else 'NO'}", flush=True)


def main():
    print("AGGREGATION-SEDENTISM 2b — does STORAGE buffer the SHOCK? (stable fishery vs earned bust)\n")
    run(False)
    print()
    run(True, cv=0.6)
    print()
    run(True, cv=1.2)      # severe: multi-x bad years — expect more dispersal


if __name__ == "__main__":
    main()
