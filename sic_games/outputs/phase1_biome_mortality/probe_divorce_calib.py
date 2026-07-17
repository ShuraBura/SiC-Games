"""R-78: refine divorce_rate to Ache 0.14, on BOTH pairing paths (per-step base vs seasonal village),
to quantify the re-pairing-latency effect on divorced PREVALENCE."""
import sys, os, statistics
_H="sic_games/outputs/phase1_biome_mortality"; sys.path.insert(0, os.path.normpath(os.path.join(_H,"..","phase1_social_evolution")))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

def run(rate, seed, village, steps=500, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,75000.0,patch=(20,20,60),mode="tallavaara",aquatic=True,enable_depletion=True)
    land=[(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    pos=[land[i%len(land)] for i in range(n)]
    upd=dict(divorce_rate=rate)
    if village:
        upd.update(enable_marriage_aggregation=True, enable_aggregation_sedentism=True, enable_catchment_ceiling=True,
                   enable_settlement_scalar_stress=True, enable_landscape_packing=True, enable_sedentism_fertility=True)
    d = realistic_forager_demog().model_copy(update=upd)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list: return None
    m = w.demography()
    return m["frac_parents_divorced"], m["frac_paired_adult_f"], m["n"]

for village in (False, True):
    label = "VILLAGE stack (_do_gathering, seasonal re-pair)" if village else "BASE preset (_do_pairing, per-step re-pair)"
    print(f"\n=== {label} ===   anchor: Ache divorced exposure 0.14")
    print(f"{'div_rate':>9} {'divorced':>9} {'pairedF':>8} {'eq_pop':>7}")
    for rate in (0.004, 0.005, 0.006, 0.008):
        rs=[run(rate,s,village) for s in range(4)]; rs=[r for r in rs if r]
        if not rs: print(f"{rate:9.4f}  extinct"); continue
        dv=statistics.mean([r[0] for r in rs if r[0]==r[0]]); pf=statistics.mean([r[1] for r in rs if r[1]==r[1]]); ep=statistics.mean([r[2] for r in rs])
        tag = "  <-- ~0.14" if abs(dv-0.14)<0.02 else ""
        print(f"{rate:9.4f} {dv:9.3f} {pf:8.3f} {ep:7.0f}{tag}")
