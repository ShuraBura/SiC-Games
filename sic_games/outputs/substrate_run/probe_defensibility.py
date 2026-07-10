"""Probe: does the economic-defensibility TETHER sustain concentration (and hence stratification)?

A3 showed stratification collapses because IFD dispersal spreads the population (occ_cells up, occ_max down).
`enable_economic_defensibility` (Dyson-Hudson & Smith) tethers owner-band members to claimed cells (×tether) and
routes outsiders away (×exclusion) — its docstring's stated purpose is "concentration → packing → the morph fires".
It was OFF in every run so far. This A/B tests it. Flushes progress every LOGEVERY steps (standing rule: long runs
must be watchable).

Run:  DEFENS=0|1 py -3 -u sic_games/outputs/substrate_run/probe_defensibility.py
Env:  DEFENS (0/1), P_STEPS (1500), P_FOUNDERS (3000), P_LOGEVERY (250)
"""
import sys, os, time
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

DEFENS = os.environ.get("DEFENS", "0") == "1"
STEPS = int(os.environ.get("P_STEPS", "1500"))
FOUNDERS = int(os.environ.get("P_FOUNDERS", "3000"))
LOGEVERY = int(os.environ.get("P_LOGEVERY", "250"))
TAG = "ON" if DEFENS else "OFF"


def main():
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base.level(x, y) > 0]
    cap = ClimateField(base, a_seas=0.4)
    d = emergent_village_demog().model_copy(update=dict(
        enable_landscape_packing=True, enable_sedentism_fertility=True, enable_economic_defensibility=DEFENS))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=[land[i % len(land)] for i in range(FOUNDERS)],
                     demography_cfg=d)
    print(f"[defens={TAG}] start founders={FOUNDERS} steps={STEPS}", flush=True)
    t0 = time.time()
    for step in range(1, STEPS + 1):
        w.step()
        if not w.agent_list:
            print(f"[defens={TAG}] EXTINCT at {step}", flush=True); return
        if step % LOGEVERY == 0:
            socs = Counter(w._band_society.get(a._group.band_id, "egalitarian_forager") for a in w.agent_list)
            occ = Counter(a.pos for a in w.agent_list)
            pop = len(w.agent_list)
            ns = socs.get("stratified_chiefdom", 0)
            el = time.time() - t0
            print(f"[defens={TAG}] s{step:5d} pop={pop:5d} occ_cells={len(occ):4d} occ_max={max(occ.values()):3d} "
                  f"N_strat={ns:4d} ({100*ns/pop:4.1f}%) owned={len(w._cell_owner):4d} "
                  f"| el={el/60:.1f}m eta={el/step*(STEPS-step)/60:.1f}m", flush=True)
    print(f"[defens={TAG}] DONE in {(time.time()-t0)/60:.1f}m", flush=True)


if __name__ == "__main__":
    main()
