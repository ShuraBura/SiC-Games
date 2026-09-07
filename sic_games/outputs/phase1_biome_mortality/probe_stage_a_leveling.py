"""R-82 Stage A complete: aggrandizers vs Boehm leveling, with ABUNDANCE as the arbiter.
Hayden's falsifiable claim: hold the trait AND the leveling constant; vary abundance ->
inequality should appear only where resources are abundant/invulnerable."""
import sys, os, statistics
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def run(lev, seed, steps=700, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="boreal")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.6)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    if not land: return None
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_storage=True, enable_resource_storability=True,
        enable_material_capture=True, material_capture_frac=0.5, material_decay=0.002,
        aggrandizer_frac=0.15, material_invulnerability_min=0.0,
        enable_leveling=lev, leveling_strength=(0.5 if lev else 0.0), leveling_share=(0.8 if lev else 0.0)))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    lev_ev = 0
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
        lev_ev += w.leveling_events_this_step
    m = w.demography()
    return m["material_gini"], m["corr_aggr_material"], m["material_top10_share"], lev_ev, m["density_occupied_per_km2"], m["hayden_stage_occupied"], m["n"]

print("R-82 STAGE A COMPLETE: aggrandizer capture vs Boehm leveling (boreal, 3 seeds x 700)")
print(f"{'leveling':>10} {'mat_GINI':>9} {'corr(aggr,mat)':>15} {'top10%':>8} {'sanctions':>10} {'dens/km2':>9} {'stage':>13}")
print('-'*80)
for lev in (False, True):
    rs=[run(lev,s) for s in range(3)]; rs=[r for r in rs if r]
    if not rs: print(f"{str(lev):>10}  extinct"); continue
    def f_(i):
        v=[r[i] for r in rs if isinstance(r[i],float) and r[i]==r[i]]
        return statistics.mean(v) if v else float('nan')
    stage=statistics.mode([r[5] for r in rs])
    print(f"{str(lev):>10} {f_(0):9.3f} {f_(1):+15.3f} {f_(2)*100:7.1f}% {statistics.mean([r[3] for r in rs]):10.0f} {f_(4):9.3f} {stage:>13}")
