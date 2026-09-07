"""R-83 elite step 1: leader "managerial rights" over BAND corporate output.
Does the BAND unit (~25) produce personal stratification where the CELL unit (1-2) failed?"""
import sys, os, statistics
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def run(lf, lev, seed, steps=600, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_capture_frac=0.0,
        material_decay=0.002, aggrandizer_frac=0.15,
        enable_leader_share=(lf>0), leader_share_frac=lf,
        enable_leveling=lev, leveling_strength=(0.79 if lev else 0.0), leveling_share=(0.8 if lev else 0.0)))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    levy=0.0
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
        levy += w.leader_levy_this_step
    m = w.demography()
    leaders = set(id(x) for x in w.band_leaders().values())
    al=[a for a in w.agent_list if a.age>=15*12]
    ld=[a.material for a in al if id(a) in leaders]
    ot=[a.material for a in al if id(a) not in leaders]
    ratio = (statistics.mean(ld)/max(1e-9,statistics.mean(ot))) if ld and ot else float('nan')
    return m["material_gini"], ratio, m["material_top10_share"], levy, len(w.agent_list)

print("R-83: LEADER SHARE at BAND level (cell-level capture gave only 1.14x). 2 seeds x 600.")
print(f"{'share':>6} {'leveling':>9} {'mat_GINI':>9} {'leader/other':>13} {'top10%':>8} {'pop':>6}")
print('-'*58)
for lf in (0.0, 0.2, 0.5):
    for lev in (False, True):
        rs=[run(lf,lev,s) for s in range(2)]; rs=[r for r in rs if r]
        if not rs: print(f"{lf:6.2f} {str(lev):>9}   extinct"); continue
        def f_(i):
            v=[r[i] for r in rs if isinstance(r[i],float) and r[i]==r[i]]
            return statistics.mean(v) if v else float('nan')
        print(f"{lf:6.2f} {str(lev):>9} {f_(0):9.3f} {f_(1):12.2f}x {f_(2)*100:7.1f}% {statistics.mean([r[4] for r in rs]):6.0f}")
