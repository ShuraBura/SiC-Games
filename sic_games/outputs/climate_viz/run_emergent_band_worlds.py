import sys, math
from collections import Counter
sys.path.insert(0,"sic_games/outputs/phase1_social_evolution"); sys.path.insert(0,"sic_games/outputs/biome_society_20260702")
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import (generate_world, world_lottery_climate, FORAGE_KCAL_TARGETS as FT, FORAGE_KCAL_STD as FS,
                               GAME_KCAL_TARGETS as GT, GAME_KCAL_STD as GS, DEFAULT_STD_FRAC as D)
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
import numpy as np
names={0:'water',1:'wetland',2:'forest',3:'savanna',4:'grass',5:'desert',6:'mountain'}
def cvof(code):
    fm=FT.get(code,0); fs=FS.get(code,D*fm); gm=GT.get(code,0); gs=GS.get(code,D*gm)
    tm=fm+gm; return max(math.sqrt(fs*fs+gs*gs)/tm,0.4) if tm>0 else 0.4
def run(terr,clim):
    k=world_lottery_climate(0,terrain=terr,climate=clim); f=generate_world(k,mode="climate")
    hf=ClimateField(NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True),a_seas=0.5)
    hf0=NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    if not land: return None
    occb=Counter(int(f.biome[y,x]) for (x,y) in land); dom=occb.most_common(1)[0][0]
    pos=[land[i%len(land)] for i in range(800)]
    d=emergent_village_demog().model_copy(update=dict(enable_emergent_band_size=True))
    w=TerrainWorld(n_agents=800,kcal_cfg=KcalEconomyConfig(),terrain_knobs=k,game_stream=False,seed=0,
       carbon_cfg=CarbonConfig(kappa=1.5),substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0,**GRP),
       harvest_field=hf,placement_positions=pos,demography_cfg=d)
    for _ in range(200):
        w.step()
        if not w.agent_list: return dict(dom=dom,ext=True)
    s=list(Counter(a._group.band_id for a in w.agent_list).values())
    return dict(dom=dom,pop=len(w.agent_list),med=np.median(s),mx=max(s),cv=cvof(dom))
print(f"  {'terrain':11s} {'climate':10s} {'dom_biome':9s} {'CV':>4} {'pop':>4} {'med_band':>8} {'max_band':>8}")
for terr in ("hilly","mountainous","coastal"):
    for clim in ("temperate","tropical"):
        r=run(terr,clim)
        if r is None: print(f"  {terr:11s} {clim:10s} no-land"); continue
        if r.get("ext"): print(f"  {terr:11s} {clim:10s} {names[r['dom']]:9s} EXTINCT"); continue
        print(f"  {terr:11s} {clim:10s} {names[r['dom']]:9s} {r['cv']:4.2f} {r['pop']:4d} {r['med']:8.0f} {r['mx']:8d}")
