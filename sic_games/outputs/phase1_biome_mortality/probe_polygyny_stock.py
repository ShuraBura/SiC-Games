"""Does status->RS survive at a forager-realistic polygyny rate?
Marlowe (Hadza monograph): "there are usually only about 4% of MEN with 2 wives" -- of MEN, not of
married men. R-19/R-20 adopted polygyny_rate=0.3/max_wives=3 because it recovered von Rueden's
status->RS ~0.13-0.15. If that number is bought with 7x too much polygyny, it is an artifact.
"""
import sys, os, math, statistics
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

def run(rate, cap, seed, steps=900, n=400):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(polygyny_rate=rate, max_wives=cap))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    adult_m=[a for a in w.agent_list if a.sex=="male" and a.age>=15*12]
    if len(adult_m)<20: return None
    poly_of_all = sum(1 for a in adult_m if len(a._wives)>1)/len(adult_m)          # Marlowe's denominator
    married=[a for a in adult_m if len(a._wives)>0]
    poly_of_married = (sum(1 for a in married if len(a._wives)>1)/len(married)) if married else float('nan')
    # status->RS: corr(combined status, children fathered) among adult males
    st=[a.cred*getattr(a,"prowess",1.0) for a in adult_m]
    rs=[getattr(a,"_n_fathered",0) for a in adult_m]
    return poly_of_all, poly_of_married, corr(st,rs), len(w.agent_list)

print("Marlowe (Hadza): ~4% of MEN have 2 wives.  von Rueden status->RS r~0.15 (monogamous societies)")
print(f"{'rate':>6} {'cap':>4} {'poly%|all men':>14} {'poly%|married':>14} {'status→RS':>10} {'eq_pop':>7}")
print('-'*62)
for rate, cap in ((0.0,1), (0.002,2), (0.005,2), (0.01,2), (0.02,2)):
    rs_=[run(rate,cap,s) for s in range(3)]
    rs_=[r for r in rs_ if r]
    if not rs_: print(f"{rate:6.2f} {cap:4d}  extinct"); continue
    pa=statistics.mean([r[0] for r in rs_]); pm=statistics.mean([r[1] for r in rs_ if r[1]==r[1]])
    sr=statistics.mean([r[2] for r in rs_ if r[2]==r[2]]); ep=statistics.mean([r[3] for r in rs_])
    star = "  <-- CANONICAL" if rate==0.3 else ("  <-- ~Marlowe 4%" if abs(pa-0.04)<0.03 else "")
    print(f"{rate:6.2f} {cap:4d} {pa*100:13.1f}% {pm*100:13.1f}% {sr:+10.3f} {ep:7.0f}{star}")
