"""Does the wife-fertility transfer ever fire, and is a husband's overflow status-graded?
Instrument the provision_pool directly on a crowded run."""
import sys, math, statistics
sys.path.insert(0,"sic_games/outputs/phase1_social_evolution")
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def corr(xs, ys):
    n=len(xs)
    if n<3: return float('nan')
    mx=sum(xs)/n; my=sum(ys)/n
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/(sx*sy) if sx>0 and sy>0 else float('nan')

k = world_lottery_climate(0, terrain="coastal", climate="temperate")
f = generate_world(k, mode="climate")
hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
pos=[land[i%len(land)] for i in range(900)]
d = realistic_forager_demog().model_copy(update=dict(polygyny_rate=0.005, max_wives=3, polygyny_attrition=0.02,
    wife_quality_strength=2.0, wife_fertility_provision_frac=0.9))
w = TerrainWorld(n_agents=900, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
    carbon_cfg=CarbonConfig(kappa=1.5),
    substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
    harvest_field=hf, placement_positions=pos, demography_cfg=d)
for _ in range(600): w.step()

# snapshot: how many married men have overflow? is overflow status-graded? do wives have need?
am=[a for a in w.agent_list if a.sex=="male" and a.age>=15*12 and a._wives]
rf=w._reserve_full
n_over=sum(1 for h in am if h.wealth > rf*h.reserve_scale())
print(f"married men: {len(am)} | with overflow (wealth>cap): {n_over} ({100*n_over/max(1,len(am)):.0f}%)")
if len(am)>=5:
    st=[h.cred*getattr(h,'prowess',1.0) for h in am]
    over=[max(0.0, h.wealth - rf*h.reserve_scale()) for h in am]
    print(f"  mean husband overflow: {statistics.mean(over):.1f}  (median {statistics.median(over):.1f})")
    print(f"  corr(husband status, his overflow) = {corr(st,over):+.3f}   <-- the status-grading the channel relies on")
# do wives have reserve NEED (the precondition for the transfer to fire)?
wv=[a for a in w.agent_list if a.sex=="female" and a._partner is not None and a.age>=15*12]
need=[rf*a.reserve_scale() - a.wealth for a in wv]
n_need=sum(1 for x in need if x>0)
print(f"married women: {len(wv)} | with reserve NEED (wealth<full): {n_need} ({100*n_need/max(1,len(wv)):.0f}%)")
print(f"  mean wife need: {statistics.mean(need):.1f}" if wv else "")
