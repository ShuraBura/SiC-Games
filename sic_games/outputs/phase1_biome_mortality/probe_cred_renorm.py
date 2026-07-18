"""R-81 re-verify: does cred renorm (a) bound mean+Gini, (b) how much does it move status->RS (R-19)?"""
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
    return (2*sum((i+1)*x for i,x in enumerate(v)))/(n*s)-(n+1)/n if s>0 and n else 0.0
def corr(xs,ys):
    n=len(xs)
    if n<3: return float('nan')
    mx=sum(xs)/n; my=sum(ys)/n
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/(sx*sy) if sx>0 and sy>0 else float('nan')
def run(renorm, seed, steps=800, n=400):
    k=world_lottery_climate(seed,terrain="coastal",climate="temperate"); f=generate_world(k,mode="climate")
    hf=ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True),a_seas=0.5)
    hf0=NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    d=realistic_forager_demog().model_copy(update=dict(enable_cred_renorm=renorm))
    w=TerrainWorld(n_agents=n,kcal_cfg=KcalEconomyConfig(),terrain_knobs=k,game_stream=False,seed=seed,
      carbon_cfg=CarbonConfig(kappa=1.5),
      substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
      harvest_field=hf,placement_positions=pos,demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    al=w.agent_list; am=[a for a in al if a.sex=="male" and a.age>=15*12]
    if len(am)<20: return None
    cr=[a.cred for a in al]
    st=[a.cred*getattr(a,'prowess',1.0) for a in am]; rs=[getattr(a,'_n_fathered',0) for a in am]
    return statistics.mean(cr), gini(cr), max(cr), corr(st,rs), len(al)
print("R-81 cred renorm: OFF (current, leaking homeostat) vs ON (fixed). 4 seeds x 800 steps, canonical.")
print(f"{'renorm':>7} {'mean_cred':>9} {'cred_Gini':>9} {'max_cred':>9} {'status2RS':>10} {'eq_pop':>7}")
print('-'*56)
for renorm in (False, True):
    rs_=[run(renorm,s) for s in range(4)]; rs_=[r for r in rs_ if r]
    mc=statistics.mean([r[0] for r in rs_]); gi=statistics.mean([r[1] for r in rs_]); mx=statistics.mean([r[2] for r in rs_])
    a=[r[3] for r in rs_ if r[3]==r[3]]; sr=statistics.mean(a) if a else float('nan'); ep=statistics.mean([r[4] for r in rs_])
    print(f"{str(renorm):>7} {mc:>9.2f} {gi:>9.3f} {mx:>9.1f} {sr:+10.3f} {ep:7.0f}")
