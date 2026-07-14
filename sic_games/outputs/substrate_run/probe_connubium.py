"""Calibrate the Cut-2 adaptive connubium: sweep m* (mate_search_min_eligible) and measure the EMERGENT mating-network
reach against Wobst's ~475-person connubium. Full R-64 settlement stack + adaptive connubium + patriclan exogamy
(lineage), so the reach self-organizes under realistic density + kin-saturation. Reports median/p90 reach over the
measurement window + mate success (unpaired-female frac) + pop + settlement count (also confirms the Cut-2 founding
wiring fires in a live run).

Run:  py -3 -u sic_games/outputs/substrate_run/probe_connubium.py     (from repo root)
Env:  Q_MSTARS "3,8,20,40" | Q_FOUNDERS 2500 | Q_STEPS 700 | Q_WINDOW 150 | Q_SEED 0
"""
import sys, os, time, json, statistics
from collections import Counter

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(HERE, "..", "biome_society_20260702"))
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from run_se0_controlled_climate import emergent_village_demog
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

M_STARS  = [int(v) for v in os.environ.get("Q_MSTARS", "3,8,20,40").split(",")]
FOUNDERS = int(os.environ.get("Q_FOUNDERS", "2500"))
STEPS    = int(os.environ.get("Q_STEPS", "700"))
WINDOW   = int(os.environ.get("Q_WINDOW", "150"))       # measure reach over the last WINDOW steps (near-capacity)
SEED     = int(os.environ.get("Q_SEED", "0"))
WOBST    = 475

PROG = os.path.join(HERE, "connubium_progress.txt")
OUT  = os.path.join(HERE, "connubium_results.json")


def log(m):
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(m + "\n"); fh.flush()
    print(m, flush=True)


def run_arm(m_star):
    k = world_lottery_climate(SEED, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base.level(x, y) > 0]
    cap = ClimateField(base, a_seas=0.4, regime_driver=None)
    pos = [land[i % len(land)] for i in range(FOUNDERS)]
    demog = emergent_village_demog().model_copy(update=dict(
        enable_landscape_packing=True, enable_sedentism_fertility=True,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
        enable_catchment_ceiling=True, enable_settlement_scalar_stress=True, settle_catchment_radius=1,
        enable_adaptive_connubium=True, mate_search_min_eligible=m_star,
        enable_exogamy=True, exogamy_degree="lineage",
        enable_genome=True, genome_loci=48))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=SEED,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    men = demog.menarche_months
    reaches = []
    t0 = time.time()
    for step in range(1, STEPS + 1):
        w.step()
        if not w.agent_list:
            return dict(m_star=m_star, extinct_at=step)
        if step > STEPS - WINDOW and w._connubium_sizes:
            reaches.extend(w._connubium_sizes)              # this gathering's realized reaches
    al = w.agent_list
    fem = [a for a in al if a.sex == "female" and a.age >= men]
    unpaired = sum(1 for a in fem if a._partner is None) / len(fem) if fem else 0.0
    sizes = Counter(a._group.band_id for a in al)
    r = dict(m_star=m_star, pop=len(al), n_settle=len(w._settlement_sites),
             band_med=statistics.median(sizes.values()) if sizes else 0,
             unpaired_frac=round(unpaired, 3), n_reach=len(reaches),
             reach_med=round(statistics.median(reaches), 0) if reaches else 0,
             reach_p90=round(statistics.quantiles(reaches, n=10)[-1], 0) if len(reaches) >= 10 else 0,
             reach_mean=round(statistics.mean(reaches), 0) if reaches else 0,
             minutes=round((time.time() - t0) / 60, 1))
    return r


def main():
    open(PROG, "w").close()
    log(f"connubium calibration: m* sweep {M_STARS}, coastal-temperate, {FOUNDERS} founders x {STEPS} steps, "
        f"reach over last {WINDOW}. Target = Wobst {WOBST}.")
    results = []
    for m_star in M_STARS:
        r = run_arm(m_star)
        results.append(r)
        json.dump(results, open(OUT, "w"))
        if r.get("extinct_at"):
            log(f"  m*={m_star:3d}: EXTINCT@{r['extinct_at']}")
        else:
            log(f"  m*={m_star:3d}: reach med={r['reach_med']:.0f} p90={r['reach_p90']:.0f} mean={r['reach_mean']:.0f} "
                f"(n={r['n_reach']}) | pop={r['pop']} settle={r['n_settle']} band_med={r['band_med']} "
                f"unpaired={r['unpaired_frac']} | {r['minutes']}m  [Wobst {WOBST}]")
    log(f"DONE -> {OUT}")


if __name__ == "__main__":
    main()
