"""R-82b: material now from GAME (hides), leveling anchored to Boehm 38/48 = 0.79.
Runs on a NON-storage world too, since hides come from hunting not the granary."""
import sys, os, statistics
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def run(lev, seed, steps=600, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_capture_frac=0.5,
        material_decay=0.002, aggrandizer_frac=0.15, material_invulnerability_min=0.0,
        enable_leveling=lev, leveling_strength=(0.79 if lev else 0.0), leveling_share=(0.8 if lev else 0.0)))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    ev=0
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
        ev += w.leveling_events_this_step
    m = w.demography()
    # does material couple to PROWESS (hunting) now that hides come from game?
    ad=[a for a in w.agent_list if a.age>=15*12]
    pr = TerrainWorld._corr([getattr(a,'prowess',1.0) for a in ad],[a.material for a in ad]) if len(ad)>2 else float('nan')
    return m["material_gini"], m["corr_aggr_material"], pr, m["material_top10_share"], ev, m["n"]

print("R-82b: MATERIAL FROM GAME (hides, 7% of meat). leveling_strength=0.79 [Boehm 38/48]. 3 seeds x 600.")
print(f"{'leveling':>9} {'mat_GINI':>9} {'corr(aggr,mat)':>15} {'corr(prowess,mat)':>18} {'top10%':>8} {'sanctions':>10} {'pop':>6}")
print('-'*82)
for lev in (False, True):
    rs=[run(lev,s) for s in range(3)]; rs=[r for r in rs if r]
    if not rs: print(f"{str(lev):>9}  extinct"); continue
    def f_(i):
        v=[r[i] for r in rs if isinstance(r[i],float) and r[i]==r[i]]
        return statistics.mean(v) if v else float('nan')
    print(f"{str(lev):>9} {f_(0):9.3f} {f_(1):+15.3f} {f_(2):+18.3f} {f_(3)*100:7.1f}% {statistics.mean([r[4] for r in rs]):10.0f} {f_(5):6.0f}")
