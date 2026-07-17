import sys
from collections import Counter
sys.path.insert(0,"sic_games/outputs/phase1_social_evolution"); sys.path.insert(0,"sic_games/outputs/biome_society_20260702")
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate, RETURN_CV
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
import numpy as np
names={0:'water',1:'wetland',2:'forest',3:'savanna',4:'grass',5:'desert',6:'mountain'}

def run(terr,clim,on,steps=200):
    k=world_lottery_climate(0,terrain=terr,climate=clim); f=generate_world(k,mode="climate")
    hf=ClimateField(NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True),a_seas=0.5)
    hf0=NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    if not land: return None
    pos=[land[i%len(land)] for i in range(800)]
    d=emergent_village_demog().model_copy(update=dict(enable_emergent_band_size=on))
    w=TerrainWorld(n_agents=800,kcal_cfg=KcalEconomyConfig(),terrain_knobs=k,game_stream=False,seed=0,
       carbon_cfg=CarbonConfig(kappa=1.5),substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0,**GRP),
       harvest_field=hf,placement_positions=pos,demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    s=list(Counter(a._group.band_id for a in w.agent_list).values())
    cvf=w._return_cv_field()
    mcv=float(np.median([cvf[a.pos[1],a.pos[0]] for a in w.agent_list])) if cvf is not None else float('nan')
    bio=Counter(names[int(f.biome[a.pos[1],a.pos[0]])] for a in w.agent_list).most_common(1)[0][0]
    return bio,mcv,len(w.agent_list),float(np.median(s))

print(f"{'world':24} {'dom biome':9} {'med CV':>7} {'g*':>6} {'pop':>5} {'band ON':>8} {'band OFF':>9}")
print('-'*76)
rows=[]
for terr in ("flat","hilly","mountainous","coastal","alpine"):
    for clim in ("temperate","tropical","boreal","savanna"):
        a=run(terr,clim,True); b=run(terr,clim,False)
        if a is None or b is None: continue
        bio,mcv,pop,med=a
        g=mcv/0.037
        print(f"{terr+'/'+clim:24} {bio:9} {mcv:>7.2f} {g:>6.1f} {pop:>5} {med:>8.0f} {b[3]:>9.0f}")
        rows.append((bio,mcv,med,b[3]))
cv=np.array([r[1] for r in rows]); on=np.array([r[2] for r in rows]); off=np.array([r[3] for r in rows])
print()
print(f"{len(rows)} worlds | ACROSS-WORLD corr(biome CV, med band):  ON {np.corrcoef(cv,on)[0,1]:+.3f}   OFF {np.corrcoef(cv,off)[0,1]:+.3f}")
print(f"  med band ON : range {on.min():.0f}-{on.max():.0f}  (spread {on.max()/on.min():.2f}x)")
print(f"  med band OFF: range {off.min():.0f}-{off.max():.0f}  (spread {off.max()/off.min():.2f}x)")
