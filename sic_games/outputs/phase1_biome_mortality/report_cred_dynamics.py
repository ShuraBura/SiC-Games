"""CRED DYNAMICS diagnostic: how is cred distributed, and how does it evolve in time + space?
Canonical realistic_forager_demog on a village world. Answers: is it flat? bounded? clustered?
does cred->food->survival actually bite, or wash out?"""
import sys, math, statistics
sys.path.insert(0,"sic_games/outputs/phase1_social_evolution")
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def gini(v):
    v=sorted(v); n=len(v); s=sum(v)
    return (2*sum((i+1)*x for i,x in enumerate(v)))/(n*s) - (n+1)/n if s>0 and n else 0.0
def corr(xs,ys):
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
pos=[land[i%len(land)] for i in range(500)]
d = realistic_forager_demog().model_copy(update=dict(
    enable_marriage_aggregation=True, enable_aggregation_sedentism=True, enable_catchment_ceiling=True,
    enable_settlement_scalar_stress=True, enable_landscape_packing=True, enable_sedentism_fertility=True))
print(f"canonical: cred_seed_sigma={d.cred_seed_sigma} cred_inherit_sigma={d.cred_inherit_sigma} lineage_reversion={d.lineage_reversion} kappa=1.5")
w = TerrainWorld(n_agents=500, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
    carbon_cfg=CarbonConfig(kappa=1.5),
    substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
    harvest_field=hf, placement_positions=pos, demography_cfg=d)

print(f"\n{'step':>5} {'pop':>5} {'mean_cred':>9} {'Gini':>6} {'top10%share':>11} {'max/med':>8}")
for step in range(1,701):
    w.step()
    if not w.agent_list: print("extinct"); break
    if step % 100 == 0:
        cr=sorted((a.cred for a in w.agent_list), reverse=True)
        n=len(cr); top10=sum(cr[:max(1,n//10)])/sum(cr)
        print(f"{step:>5} {n:>5} {statistics.mean(cr):>9.3f} {gini(cr):>6.3f} {top10*100:>10.1f}% {cr[0]/statistics.median(cr):>8.2f}")

# SPATIAL: cred by village
al=w.agent_list
vil={}
for a in al:
    s=w._nearest_settlement(a.pos)
    if s is not None: vil.setdefault(s,[]).append(a.cred)
big=[(s,v) for s,v in vil.items() if len(v)>=30]
print(f"\nSPATIAL — mean cred across {len(big)} large villages:")
if big:
    mc=[statistics.mean(v) for s,v in big]
    print(f"  village mean-cred: min {min(mc):.2f}  spread {max(mc)/min(mc):.2f}x  (are villages cred-differentiated?)")

# COUPLING: does cred -> food -> survival actually bite?
adults=[a for a in al if a.age>=15*12]
print(f"\nCOUPLING (n={len(adults)} adults):")
print(f"  corr(cred, wealth/food)      = {corr([a.cred for a in adults],[a.wealth for a in adults]):+.3f}")
print(f"  corr(cred, _n_fathered | male) = {corr([a.cred for a in adults if a.sex=='male'],[getattr(a,'_n_fathered',0) for a in adults if a.sex=='male']):+.3f}")
print(f"  cred: min {min(a.cred for a in al):.2f} median {statistics.median([a.cred for a in al]):.2f} max {max(a.cred for a in al):.2f}")
