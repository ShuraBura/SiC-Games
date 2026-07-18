"""R-82 Stage A (fixed): Hayden's thesis, made falsifiable.
Hold the AGGRANDIZER trait constant; vary the ABUNDANCE/INVULNERABILITY gate.
Predicted: material inequality appears only where the gate permits (invulnerable stock)."""
import sys, os, statistics
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def run(mat, inv_min, seed, steps=700, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="boreal")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.6)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    if not land: return None
    pos=[land[i%len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_storage=True, enable_resource_storability=True,
        enable_material_capture=mat, material_capture_frac=(0.5 if mat else 0.0),
        material_decay=0.002, aggrandizer_frac=0.15, material_invulnerability_min=inv_min))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    m = w.demography()
    return (m["material_gini"], m["corr_aggr_material"], m["corr_cred_material"],
            m["wealth_gini"], m["frac_aggrandizer"], m["density_per_km2"], m["hayden_stage"], m["n"])

print("R-82 STAGE A (fixed): aggrandizer trait held at 0.15; vary the invulnerability GATE. boreal, 3 seeds x 700.")
print(f"{'arm':>26} {'mat_GINI':>9} {'corr(aggr,mat)':>15} {'corr(cred,mat)':>15} {'wealth_g':>9} {'dens/km2':>9} {'stage':>14}")
print('-'*104)
arms=[("capture OFF", False, 0.0), ("ON, gate off (B>=0)", True, 0.0),
      ("ON, gate B>=0.6", True, 0.6), ("ON, strict B>=0.9", True, 0.9)]
for label, mat, inv in arms:
    rs=[run(mat,inv,s) for s in range(3)]; rs=[r for r in rs if r]
    if not rs: print(f"{label:>26}  extinct"); continue
    def f_(i):
        v=[r[i] for r in rs if isinstance(r[i],float) and r[i]==r[i]]
        return statistics.mean(v) if v else float('nan')
    stage = statistics.mode([r[6] for r in rs])
    print(f"{label:>26} {f_(0):9.3f} {f_(1):+15.3f} {f_(2):+15.3f} {f_(3):9.3f} {f_(5):9.3f} {stage:>14}")
