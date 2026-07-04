"""Agriculture Layer B1 — SOIL DEPLETION. (1) On a FARM world, does soil-depletion ON degrade a village's soil →
yield fall → bust, vs a stable soil-OFF baseline? (2) On a FISHERY world, is soil-depletion a no-op (aquatic-
dominant sites exempt → R-53 stability preserved)? Tracks mean farm-site soil + settlement fate.

Run:  py -3 -u outputs/climate_viz/run_agriculture_layerB1.py
"""
import sys, os
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

FOUNDERS = 400


def run(terr, clim, soil, steps, tag, cult_gate=0.5):
    k = world_lottery_climate(0, terrain=terr, climate=clim)
    f = generate_world(k, mode="climate")
    cult, aq = f.cultivability, f.aquatic_food
    cap = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    key = cult if terr == "flat" else aq
    rich = [(x, y) for y in range(100) for x in range(100)
            if cap.level(x, y) > 0 and f.isWater[y, x] == 0 and key[y, x] >= cult_gate]
    zone = set()
    for (x, y) in rich:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cx, cy = (x + dx) % 100, (y + dy) % 100
                if cap.level(cx, cy) > 0 and f.isWater[cy, cx] == 0:
                    zone.add((cx, cy))
    zone = sorted(zone)
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
        enable_agriculture=True, enable_soil_depletion=soil))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    print(f"  [{tag}]", flush=True)
    for i in range(steps):
        w.step()
        al = w.agent_list
        if not al:
            print(f"  [{tag}] EXTINCT {i+1}", flush=True); return
        if i % 300 == 299 or i == steps - 1:
            soils = list(w._settlement_soil.values())
            msoil = sum(soils) / len(soils) if soils else 1.0
            rad = w._demog.settle_radius
            spop = sum(1 for a in al if any(w._torus_cheby(a.pos[0], a.pos[1], s[0], s[1]) <= rad
                                            for s in w._settlement_sites))
            print(f"  [{tag}] step {i+1:4d}: pop={len(al):4d}  settlements={len(w._settlement_sites):2d}  "
                  f"settled_pop={spop:4d}  mean_soil={msoil:.2f}  min_soil={min(soils) if soils else 1.0:.2f}", flush=True)


def main():
    print("\nAGRICULTURE LAYER B1 — soil depletion: farm bust vs fishery-exempt\n")
    print(" FARM world (flat-temperate):")
    run("flat", "temperate", False, 2000, "farm soil-OFF")
    print()
    run("flat", "temperate", True, 2000, "farm soil-ON ")
    print()
    print(" FISHERY world (mountainous-tropical) — soil-ON must be a no-op (R-53 preserved):")
    run("mountainous", "tropical", True, 1500, "fish soil-ON ")


if __name__ == "__main__":
    main()
