"""Is `w.agents` (the metric the bands test uses) counting DEAD agents?
If phase1_model never calls agent.remove(), corpses stay in the Mesa AgentSet at their
death cell -> the 25-stacked seed corpses look like 'persistent dense bands'."""
from __future__ import annotations
from collections import Counter
from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld, seed_band_positions, _DEFAULT_KNOBS
from sic_games.terrain import generate_world

fields = generate_world({**_DEFAULT_KNOBS, "seedStr": "world7"})
pos = seed_band_positions(fields, 250, band_size=25, territory_radius=3)
sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                     move_cost_flat=0.0, group_safety_max=8.0, group_safety_scale=15.0,
                     group_mate_min=15.0, group_mate_floor=0.2)
w = TerrainWorld(n_agents=250, kcal_cfg=KcalEconomyConfig(), seed=7, game_stream=False, substrate_cfg=sc,
                 demography_cfg=DemographyConfig(enable_bonded_mating=True), placement_positions=pos)
for _ in range(400):
    w.step()

mesa_agents = list(w.agents)
alive_in_mesa = [a for a in mesa_agents if getattr(a, "alive", True)]
print(f"len(w.agents)          = {len(mesa_agents)}   <- what the test measures")
print(f"  of which alive==True = {len(alive_in_mesa)}")
print(f"len(w.agent_list)      = {len(w.agent_list)}   <- the true LIVE population")

def frac_in_bands(occ, k=10):
    pop = sum(occ.values());
    return sum(s for s in occ.values() if s >= k) / pop if pop else 0.0

occ_mesa = Counter(a.pos for a in mesa_agents)
occ_live = Counter(a.pos for a in w.agent_list)
print(f"\nframe_in_bands(w.agents, k=10)     = {frac_in_bands(occ_mesa):.2f}  (test asserts >0.7)")
print(f"frac_in_bands(agent_list, k=10)    = {frac_in_bands(occ_live):.2f}  (the truth)")
print(f"\ntop occupied cells in w.agents (corpses?): {occ_mesa.most_common(5)}")
print(f"top occupied cells, live:                  {occ_live.most_common(5)}")
