"""Probe: with residence≠foraging ON, does EMERGENT village size land at Bar-Yosef 50-150 when the catchment economy is
physically anchored (settle_tier2_yield ~1-2 not 40, catchment radius ~1 = Vita-Finzi & Higgs ~5 km forager reach)?
Measures the village-size distribution = population within settle_radius of each settlement site. Flushes per LOGEVERY.

Env: TIER2 (settle_tier2_yield, default 1.0), CRAD (settle_catchment_radius, 1), P_STEPS (800), P_FOUNDERS (3000)
"""
import sys, os, time, statistics
from collections import Counter

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(HERE, "..", "biome_society_20260702"))
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

TIER2 = float(os.environ.get("TIER2", "1.0"))
CRAD = int(os.environ.get("CRAD", "1"))
AGGL = os.environ.get("AGGL", "1") == "1"   # point-superlinear agglomeration premium on/off
CEIL = os.environ.get("CEIL", "0") == "1"   # R-63 catchment carrying-capacity ceiling
REP = float(os.environ.get("REP", "0.3"))   # scalar-stress repulsion_gain (Johnson/Alberti n^2 coordination cost)
SS = os.environ.get("SS", "0") == "1"        # B: settlement scalar stress (caps egalitarian villages, dissipated by hierarchy)
SSMID = float(os.environ.get("SSMID", "150"))
STEPS = int(os.environ.get("P_STEPS", "800"))
FOUNDERS = int(os.environ.get("P_FOUNDERS", "3000"))
LOGEVERY = int(os.environ.get("P_LOGEVERY", "200"))
TAG = f"ceil={int(CEIL)}/ss={int(SS)}@{SSMID:.0f}"


def village_sizes(w, rad):
    """Village = agents ON the settlement SITE cell (the residence pin converges them there). `rad` unused (kept for
    signature); the old radius-2 area metric double-counted overlapping catchments."""
    if not w._settlement_sites:
        return []
    occ = Counter(a.pos for a in w.agent_list)
    return [occ.get(s, 0) for s in w._settlement_sites]


def main():
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base.level(x, y) > 0]
    cap = ClimateField(base, a_seas=0.4)
    d = emergent_village_demog().model_copy(update=dict(
        enable_landscape_packing=True, enable_sedentism_fertility=True,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True, enable_agglomeration=AGGL,
        enable_catchment_ceiling=CEIL, repulsion_gain=REP,
        enable_settlement_scalar_stress=SS, settlement_ss_midpoint=SSMID,
        settle_tier2_yield=TIER2, settle_catchment_radius=CRAD))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=[land[i % len(land)] for i in range(FOUNDERS)],
                     demography_cfg=d)
    print(f"[{TAG}] start (Bar-Yosef target 50-150)", flush=True)
    t0 = time.time()
    for step in range(1, STEPS + 1):
        w.step()
        if not w.agent_list:
            print(f"[{TAG}] EXTINCT at {step}", flush=True); return
        if step % LOGEVERY == 0:
            vs = village_sizes(w, d.settle_radius)
            pop = len(w.agent_list)
            socs = Counter(w._band_society.get(a._group.band_id, "egalitarian_forager") for a in w.agent_list)
            vdesc = (f"n={len(vs)} med={statistics.median(vs):.0f} p90={sorted(vs)[int(0.9*len(vs))]:.0f} "
                     f"max={max(vs)}") if vs else "n=0"
            in_band = sum(1 for v in vs if 50 <= v <= 150) / len(vs) * 100 if vs else 0
            el = time.time() - t0
            print(f"[{TAG}] s{step:4d} pop={pop:5d} villages[{vdesc}] in_50_150={in_band:.0f}% "
                  f"strat={100*socs.get('stratified_chiefdom',0)/pop:.0f}% occ_max={max(Counter(a.pos for a in w.agent_list).values())} "
                  f"| el={el/60:.1f}m eta={el/step*(STEPS-step)/60:.1f}m", flush=True)
    print(f"[{TAG}] DONE {(time.time()-t0)/60:.1f}m", flush=True)


if __name__ == "__main__":
    main()
