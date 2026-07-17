import sys
from collections import Counter
sys.path.insert(0,"sic_games/outputs/phase1_social_evolution"); sys.path.insert(0,"sic_games/outputs/biome_society_20260702")
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
import numpy as np

def run(cv_safe, steps=200):
    k=world_lottery_climate(0,terrain="coastal",climate="tropical"); f=generate_world(k,mode="climate")
    hf=ClimateField(NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True),a_seas=0.5)
    hf0=NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(800)]
    upd=dict(enable_emergent_band_size=True) if cv_safe else dict(enable_emergent_band_size=False)
    if cv_safe: upd["cv_safe"]=cv_safe
    d=emergent_village_demog().model_copy(update=upd)
    w=TerrainWorld(n_agents=800,kcal_cfg=KcalEconomyConfig(),terrain_knobs=k,game_stream=False,seed=0,
       carbon_cfg=CarbonConfig(kappa=1.5),substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0,**GRP),
       harvest_field=hf,placement_positions=pos,demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    s=list(Counter(a._group.band_id for a in w.agent_list).values())
    gs=None
    if cv_safe:
        cvf=w._return_cv_field()
        gs=float(np.median([cvf[a.pos[1],a.pos[0]] for a in w.agent_list]))/cv_safe
    return len(w.agent_list), float(np.median(s)), float(np.mean(s)), gs

print("CAUSAL TEST: same world+seed, sweep cv_safe -> does realized band size follow g*?")
print(f"{'cv_safe':>8} {'g* (med cell)':>13} {'pop':>6} {'med band':>9} {'mean band':>10}")
print('-'*54)
r=run(None)
print(f"{'OFF':>8} {'(25 hardcoded)':>13} {r[0]:>6} {r[1]:>9.0f} {r[2]:>10.1f}")
for cs in (0.020, 0.028, 0.037, 0.050, 0.070):
    r=run(cs)
    if r is None: print(f"{cs:>8.3f}  extinct"); continue
    print(f"{cs:>8.3f} {r[3]:>13.1f} {r[0]:>6} {r[1]:>9.0f} {r[2]:>10.1f}")
