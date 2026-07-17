import sys, os, statistics
_H="sic_games/outputs/phase1_social_evolution"; sys.path.insert(0,_H)
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def run(orph, seed, steps=500, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(enable_orphan_mortality=orph))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    pops=[]
    for s in range(steps):
        w.step()
        if not w.agent_list: return None
        if s>=int(0.6*steps): pops.append(len(w.agent_list))
    m=w.demography()
    return statistics.mean(pops), m["frac_motherless"], m["frac_fatherless"], m["n_risk_0_9"], m["frac_child"]

print("CANONICAL preset realistic_forager_demog() -- paired ON vs OFF, 3 seeds x 500 steps")
print(f"{'arm':>5} {'eq_pop':>8} {'motherless':>11} {'fatherless':>11} {'n_0_9':>7} {'frac_child':>11}")
print('-'*58)
res={}
for orph in (False, True):
    rs=[run(orph,s) for s in range(3)]; rs=[r for r in rs if r]
    if not rs: print("extinct"); continue
    ep=statistics.mean([r[0] for r in rs]); ml=statistics.mean([r[1] for r in rs])
    fl=statistics.mean([r[2] for r in rs]); nr=statistics.mean([r[3] for r in rs]); fc=statistics.mean([r[4] for r in rs])
    res[orph]=ep
    print(f"{'ON' if orph else 'OFF':>5} {ep:8.0f} {ml*100:10.1f}% {fl*100:10.1f}% {nr:7.0f} {fc:11.3f}")
if len(res)==2:
    print(f"\neq_pop change ON vs OFF: {100*(res[True]-res[False])/res[False]:+.1f}%")
    print("compositional target: |change| small (how many is fertility-pinned, R-16); WHO dies shifts")
print("\nNB preset divorce_rate =", realistic_forager_demog().divorce_rate, "=> the x2.97 divorce channel never fires")
