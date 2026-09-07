import sys, os, statistics
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def run(cap, lev, seed, steps=600, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_capture_frac=cap,
        material_decay=0.002, aggrandizer_frac=0.15,
        enable_leveling=lev, leveling_strength=(0.79 if lev else 0.0), leveling_share=(0.8 if lev else 0.0)))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    al=[a for a in w.agent_list if a.age>=15*12]
    ag=[a.material for a in al if getattr(a,'aggrandizer',0)>0]
    no=[a.material for a in al if getattr(a,'aggrandizer',0)==0]
    if not ag or not no: return None
    m=w.demography()
    return statistics.mean(ag)/max(1e-9,statistics.mean(no)), m["material_gini"], len(w.agent_list)

print("Does the AGGRANDIZER still out-accumulate? mean(material|aggr) / mean(material|non-aggr). 2 seeds x 600.")
print(f"{'capture_frac':>13} {'leveling':>9} {'aggr/non ratio':>15} {'mat_GINI':>9} {'pop':>6}")
print('-'*58)
for cap in (0.0, 0.5, 0.8):
    for lev in (False, True):
        rs=[run(cap,lev,s) for s in range(2)]; rs=[r for r in rs if r]
        if not rs: print(f"{cap:13.2f} {str(lev):>9}   extinct"); continue
        print(f"{cap:13.2f} {str(lev):>9} {statistics.mean([r[0] for r in rs]):15.2f}x {statistics.mean([r[1] for r in rs]):9.3f} {statistics.mean([r[2] for r in rs]):6.0f}")
