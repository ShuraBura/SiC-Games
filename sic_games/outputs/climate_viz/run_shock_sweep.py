"""Layer 2b calibration sweep: settlement PERSISTENCE vs shock_cv × shock_rho (IID years vs AR(1) regimes).
Fixed aquatic world (lottery seed 0); the model RNG seed varies. Hypothesis: at ρ=0 storage trivially buffers
isolated bad years (persistence high, ~flat in cv); at ρ=0.85 multi-year BAD REGIMES drain the granary → higher
cv sharply lowers persistence — the meaningful stable-village-vs-earned-bust regime.

Metric: settled_frac = fraction of post-burn-in steps with ≥1 active settlement (1.0 = always settled = stable).

Run:  py -3 -u outputs/climate_viz/run_shock_sweep.py
"""
import sys, os, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

FOUNDERS, STEPS, BURN_IN, SEEDS = 400, 1200, 200, [0, 1, 2]

_k = world_lottery_climate(0, terrain="mountainous", climate="tropical")
_f = generate_world(_k, mode="climate")


def _zone(cap):
    aq = _f.aquatic_food
    reach = [(x, y) for y in range(100) for x in range(100)
             if cap.level(x, y) > 0 and _f.isWater[y, x] == 0 and aq[y, x] >= 0.5]
    z = set()
    for (x, y) in reach:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cx, cy = (x + dx) % 100, (y + dy) % 100
                if cap.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0:
                    z.add((cx, cy))
    return sorted(z)


def run(update, seed):
    cap = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    zone = _zone(cap)
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True, **update))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    settled = 0
    for i in range(STEPS):
        w.step()
        if not w.agent_list:
            return dict(settled_frac=0.0, final_pop=0, extinct=True)
        if i >= BURN_IN and w._settlement_sites:
            settled += 1
    return dict(settled_frac=settled / (STEPS - BURN_IN), final_pop=len(w.agent_list), extinct=False)


CONFIGS = [
    ("no-shock          ", dict(enable_tier2_shock=False)),
    ("cv0.3 rho0.0 (IID)", dict(enable_tier2_shock=True, shock_cv=0.3, shock_rho=0.0)),
    ("cv0.6 rho0.0 (IID)", dict(enable_tier2_shock=True, shock_cv=0.6, shock_rho=0.0)),
    ("cv0.3 rho0.85 (reg)", dict(enable_tier2_shock=True, shock_cv=0.3, shock_rho=0.85)),
    ("cv0.6 rho0.85 (reg)", dict(enable_tier2_shock=True, shock_cv=0.6, shock_rho=0.85)),
]


def main():
    print(f"SHOCK SWEEP — settled_frac (fraction of steps settled) over {len(SEEDS)} seeds × {STEPS} steps\n")
    print(f"  {'config':22s} {'settled_frac (mean)':20s} {'final_pop':10s} extinct")
    for name, upd in CONFIGS:
        rs = [run(upd, s) for s in SEEDS]
        sf = statistics.mean(r["settled_frac"] for r in rs)
        fp = statistics.mean(r["final_pop"] for r in rs)
        ne = sum(r["extinct"] for r in rs)
        bar = "#" * round(sf * 20)
        print(f"  {name:22s} {sf:4.2f} |{bar:20s}| {fp:7.0f}    {ne}/{len(SEEDS)}", flush=True)


if __name__ == "__main__":
    main()
