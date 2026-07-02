"""Deep-audit perf profile: the FULL social stack (all flags on) at scale, under cProfile."""
import sys, os, cProfile, pstats, io, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.climate import ClimateField, ClimateDriver
from sic_games.terrain import generate_world
import importlib.util as iu
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

FOUNDERS, STEPS, SEED = 300, 400, 0
demog = realistic_forager_demog().model_copy(update=dict(
    enable_leader_coherence=True, leader_coherence_gain=1.5,
    enable_size_repulsion=True, repulsion_gain=1.0,
    enable_malnutrition_fission=True, malnutrition_fission_gain=2.0,
    enable_resource_directed_fusion=True, enable_genealogy_log=True))
fields = generate_world(knobs_for(SEED)); base = SubWindowCapacity(fields)
pos = band_positions_patch(fields, base, FOUNDERS)
cap = ClimateField(base, a_seas=0.25, regime_driver=ClimateDriver.pulse(200, 100, 0.6))
w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(SEED), game_stream=False,
    seed=SEED, carbon_cfg=CarbonConfig(kappa=1.5),
    substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
    harvest_field=cap, placement_positions=pos, demography_cfg=demog)

t0 = time.time()
pr = cProfile.Profile(); pr.enable()
for _ in range(STEPS):
    w.step()
    if not w.agent_list: break
pr.disable()
wall = time.time() - t0
pop = len(w.agent_list)
print(f"FULL STACK: {STEPS} steps, endpop {pop}, wall {wall:.1f}s = {1000*wall/STEPS:.1f} ms/step "
      f"({1000*wall/STEPS/max(pop,1):.3f} ms/step/agent)")
s = io.StringIO(); ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(22)
print("\n".join(l for l in s.getvalue().splitlines() if l.strip())[-2600:])
