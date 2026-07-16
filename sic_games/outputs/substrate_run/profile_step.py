"""Profile the CURRENT full emergent-village step (post-hierarchy machinery + budding) to find the real hotspots
at scale — grounds the perf-architecture decision. Runs the campaign config under cProfile.

Run:  py -3 sic_games/outputs/substrate_run/profile_step.py    (from repo root)
Env:  P_FOUNDERS 4000 | P_STEPS 150
"""
import sys, os, cProfile, pstats, io
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(HERE, "..", "biome_society_20260702"))
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from run_se0_controlled_climate import emergent_village_demog
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

FOUNDERS = int(os.environ.get("P_FOUNDERS", "4000"))
STEPS = int(os.environ.get("P_STEPS", "150"))

k = world_lottery_climate(0, terrain="coastal", climate="temperate")
f = generate_world(k, mode="climate")
base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base.level(x, y) > 0]
cap = ClimateField(base, a_seas=0.4, regime_driver=None)
demog = emergent_village_demog().model_copy(update=dict(
    enable_landscape_packing=True, enable_sedentism_fertility=True,
    enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
    enable_catchment_ceiling=True, enable_settlement_scalar_stress=True, settle_catchment_radius=1,
    enable_village_budding=True, village_fission_threshold=150,
    enable_genome=False, enable_genealogy_log=False))
w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                 carbon_cfg=CarbonConfig(kappa=1.5),
                 substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                               contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                 harvest_field=cap, placement_positions=[land[i % len(land)] for i in range(FOUNDERS)], demography_cfg=demog)
for _ in range(20):        # warm up to a realistic packed/villaged state before profiling
    w.step()
print(f"warmup done; pop={len(w.agent_list)}. profiling {STEPS} steps...", flush=True)
pr = cProfile.Profile()
pr.enable()
for _ in range(STEPS):
    w.step()
pr.disable()
print(f"final pop={len(w.agent_list)}", flush=True)
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
ps.print_stats(22)
print("\n".join(l for l in s.getvalue().splitlines() if l.strip())[:4000])
