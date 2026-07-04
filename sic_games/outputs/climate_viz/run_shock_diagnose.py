"""Layer 2b diagnostic: is a fishery settlement STABLE under shock regimes (NW-Coast-correct), or churning
(collapse+reform masked by 'settled_frac')? Track settlement TURNOVER (formations/dissolutions), mean settlement
LIFESPAN, and total SETTLED POPULATION — no-shock vs a harsh AR(1) regime (cv0.6, rho0.85).

Run:  py -3 -u outputs/climate_viz/run_shock_diagnose.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

FOUNDERS, STEPS = 400, 1800
_k = world_lottery_climate(0, terrain="mountainous", climate="tropical")
_f = generate_world(_k, mode="climate")


def run(update, tag):
    cap = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    aq = _f.aquatic_food
    reach = [(x, y) for y in range(100) for x in range(100)
             if cap.level(x, y) > 0 and _f.isWater[y, x] == 0 and aq[y, x] >= 0.5]
    zone = set()
    for (x, y) in reach:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cx, cy = (x + dx) % 100, (y + dy) % 100
                if cap.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0:
                    zone.add((cx, cy))
    zone = sorted(zone)
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True, **update))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    rad = w._demog.settle_radius
    prev = set(); age = {}; lifespans = []; forms = 0; dissolves = 0
    print(f"  [{tag}]", flush=True)
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print(f"  [{tag}] EXTINCT {i+1}", flush=True); return
        now = set(w._settlement_sites)
        for s in now - prev:
            forms += 1; age[s] = i
        for s in prev - now:
            dissolves += 1; lifespans.append(i - age.pop(s, i))
        prev = now
        if i % 300 == 299 or i == STEPS - 1:
            spop = sum(1 for a in al if any(w._torus_cheby(a.pos[0], a.pos[1], s[0], s[1]) <= rad for s in now))
            print(f"    step {i+1:4d}: pop={len(al):4d}  n_settle={len(now):2d}  settled_pop={spop:4d}  "
                  f"shock={w._tier2_shock:.2f}  forms={forms:3d} dissolves={dissolves:3d}", flush=True)
    ml = sum(lifespans) / len(lifespans) if lifespans else float('nan')
    print(f"  [{tag}] mean settlement lifespan={ml:.0f} steps ({ml/12:.1f} yr); {forms} forms / {dissolves} dissolves", flush=True)


def main():
    print("LAYER 2b DIAGNOSE — settlement turnover / lifespan / settled-pop: stable village vs churn?\n")
    run(dict(enable_tier2_shock=False), "no-shock       ")
    print()
    run(dict(enable_tier2_shock=True, shock_cv=0.6, shock_rho=0.85), "cv0.6 rho0.85  ")


if __name__ == "__main__":
    main()
