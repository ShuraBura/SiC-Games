"""R-77: at Marlowe-calibrated polygyny (~4% of men), does the WIFE-QUALITY channel recover von Rueden's
status->RS r ~ 0.15? Validation: wife-quality r ~ 0.15 in MONOGAMOUS societies (von Rueden 33-societies).
Also reports corr(status, wife youth) -- their 'wife quality' measure = wife's age."""
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

def run(wq, seed, rate=0.005, attr=0.02, cap=3, steps=900, n=400):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(
        polygyny_rate=rate, max_wives=cap, polygyny_attrition=attr, wife_quality_strength=wq))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    am=[a for a in w.agent_list if a.sex=="male" and a.age>=15*12]
    if len(am)<20: return None
    poly=sum(1 for a in am if len(a._wives)>1)/len(am)
    st=[a.cred*getattr(a,"prowess",1.0) for a in am]; rs=[getattr(a,"_n_fathered",0) for a in am]
    # wife quality: corr(status, wife YOUTH) among married men -- von Rueden's measure is wife's age
    mm=[a for a in am if a._wives]
    wq_r=float('nan')
    if len(mm)>=3:
        s2=[a.cred*getattr(a,"prowess",1.0) for a in mm]
        youth=[-statistics.mean([x.age for x in a._wives]) for a in mm]   # negate: higher = younger
        wq_r=corr(s2,youth)
    return poly, corr(st,rs), wq_r, len(w.agent_list)

print("R-77 wife-quality sweep @ Marlowe-calibrated polygyny (rate=0.005, attrition=0.02)")
print("von Rueden 33-societies: overall status->RS r=0.19; wife quality r=0.15 in MONOGAMOUS societies")
print(f"{'wq':>5} {'poly pct men':>13} {'status2RS':>10} {'corr(status,wife youth)':>24} {'eq_pop':>7}")
print('-'*64)
for wq in (0.0, 1.0, 2.0, 4.0, 8.0):
    rs_=[run(wq,s) for s in range(4)]
    rs_=[r for r in rs_ if r]
    if not rs_: print(f"{wq:5.1f}   extinct"); continue
    pa=statistics.mean([r[0] for r in rs_])
    a=[r[1] for r in rs_ if r[1]==r[1]]; b=[r[2] for r in rs_ if r[2]==r[2]]
    sr=statistics.mean(a) if a else float('nan'); wr=statistics.mean(b) if b else float('nan')
    ep=statistics.mean([r[3] for r in rs_])
    print(f"{wq:5.1f} {pa*100:12.1f}% {sr:+10.3f} {wr:+24.3f} {ep:7.0f}")
