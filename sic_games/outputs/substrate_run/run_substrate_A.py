"""Substrate scale run "A" — grow one diverse temperate world toward capacity and log the time series that answers:
  (1) does the population OVERSHOOT-and-BUST (Malthusian) or glide?
  (2) does STRATIFICATION emerge at capacity (morph → complex/stratified)?
  (3) does structure DISCRETIZE (sparse bands/villages) as density rises?

Config: coastal temperate (diverse + water/rivers), emergent_village_demog, genome ON (diagnostic), exogamy OFF,
climate = seasonal but NO regime forcing (isolate ENDOGENOUS social dynamics; Turchin cycles are endogenous).
Diagnostics per the pre-run audit (SiC_Games_PreRun_Audit.md Gate 1): total deaths, Gini, %stratified, village count.
village_gain checked against the Bar-Yosef 50-150 band in-run.

Run:  py -3 -u sic_games/outputs/substrate_run/run_substrate_A.py    (from repo root)
Env:  A_FOUNDERS (default 3000), A_STEPS (6000), A_SEED (0), A_LOGEVERY (20), A_GENEVERY (200)
"""
import sys, os, time, json, statistics, subprocess
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
from sic_games.demography import SOCIETY_PRESETS

FOUNDERS = int(os.environ.get("A_FOUNDERS", "3000"))
STEPS    = int(os.environ.get("A_STEPS", "6000"))
SEED     = int(os.environ.get("A_SEED", "0"))
LOGEVERY = int(os.environ.get("A_LOGEVERY", "20"))
GENEVERY = int(os.environ.get("A_GENEVERY", "200"))   # genome diagnostics are O(N·L) → sample less often
BAND_SPLIT = 45                                        # village = a band grown past the fission cap (R-55)

PROG = os.path.join(HERE, "A_progress.txt")
OUT  = os.path.join(HERE, "A_trajectory.json")


def gini(xs):
    xs = sorted(v for v in xs if v is not None)
    n = len(xs)
    if n < 2:
        return 0.0
    s = sum(xs)
    if s <= 0:
        return 0.0
    cum = 0.0
    for i, v in enumerate(xs):
        cum += (i + 1) * v
    return (2.0 * cum) / (n * s) - (n + 1.0) / n


def society_of(a, w):
    """The society type an agent lives under (per-band morph if present, else per-cell, else egalitarian)."""
    s = w._band_society.get(a._group.band_id)
    if s is None:
        s = w._cell_society.get(a.pos)
    return s or "egalitarian_forager"


def log(msg):
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n"); fh.flush()
    print(msg, flush=True)


def snapshot(w, step):
    al = w.agent_list
    pop = len(al)
    sizes = Counter(a._group.band_id for a in al)
    szv = list(sizes.values())
    villages = [n for n in szv if n > BAND_SPLIT]
    socs = Counter(society_of(a, w) for a in al)
    cred = [getattr(a, "cred", 1.0) for a in al]
    wealth = [a.wealth for a in al]
    occ = Counter(a.pos for a in al)
    row = dict(
        step=step, pop=pop, births=w.births_this_step, deaths_starv=w.deaths_starv_this_step,
        n_bands=len(sizes), band_med=statistics.median(szv) if szv else 0,
        band_mean=round(statistics.mean(szv), 1) if szv else 0, band_max=max(szv) if szv else 0,
        n_villages=len(villages), village_med=round(statistics.median(villages), 1) if villages else 0,
        village_max=max(villages) if villages else 0,
        pct_complex=round(100 * socs.get("complex_forager", 0) / pop, 1) if pop else 0,
        pct_stratified=round(100 * socs.get("stratified_chiefdom", 0) / pop, 1) if pop else 0,
        gini_cred=round(gini(cred), 3), gini_wealth=round(gini(wealth), 3),
        mean_reserve=round(statistics.mean(wealth) / w._reserve_full, 3) if pop else 0,
        occ_cells=len(occ), occ_max=max(occ.values()) if occ else 0,
    )
    if step % GENEVERY == 0:
        g = w.genetics(sample_pairs=1500)
        row["heterozygosity"] = round(g.get("heterozygosity", 0.0), 4)
        row["mean_relatedness"] = round(g.get("mean_relatedness", 0.0), 4)
    return row


def main():
    open(PROG, "w").close()
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=os.path.join(HERE, "..", "..", "..")).decode().strip()
    except Exception:
        sha = "?"
    k = world_lottery_climate(SEED, terrain="coastal", climate="temperate")   # diverse + water/rivers
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    base0 = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base0.level(x, y) > 0]
    cap_total = sum(base0.level(x, y) for (x, y) in land)
    cap = ClimateField(base, a_seas=0.4, regime_driver=None)   # seasonal, NO regime forcing (endogenous only)
    pos = [land[i % len(land)] for i in range(FOUNDERS)]
    demog = emergent_village_demog().model_copy(update=dict(enable_genome=True, genome_loci=48, enable_exogamy=False))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=SEED,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    meta = dict(sha=sha, seed=SEED, founders=FOUNDERS, steps=STEPS, world="coastal-temperate",
                habitable_cells=len(land), reserve_full=w._reserve_full, band_split=BAND_SPLIT)
    log(f"substrate run A: sha={sha} world=coastal-temperate founders={FOUNDERS} steps={STEPS} "
        f"habitable_cells={len(land)} reserve_full={w._reserve_full:.0f}")
    traj = []
    t0 = time.time()
    for step in range(1, STEPS + 1):
        w.step()
        if not w.agent_list:
            log(f"[{step}] EXTINCT"); break
        if step % LOGEVERY == 0 or step == 1:
            row = snapshot(w, step)
            traj.append(row)
            with open(OUT, "w", encoding="utf-8") as fh:
                json.dump(dict(meta=meta, traj=traj), fh)          # frequent trajectory checkpoint (crash-safe data)
            el = time.time() - t0
            eta = el / step * (STEPS - step)
            log(f"[{step:5d}/{STEPS}] pop={row['pop']:6d} bands={row['n_bands']:4d} "
                f"band(med/max)={row['band_med']}/{row['band_max']} vill={row['n_villages']}(med {row['village_med']},max {row['village_max']}) "
                f"cplx={row['pct_complex']}% strat={row['pct_stratified']}% giniC={row['gini_cred']} "
                f"res={row['mean_reserve']} starvD={row['deaths_starv']} occ={row['occ_cells']}c/max{row['occ_max']} "
                f"| el={el/60:.1f}m eta={eta/60:.1f}m")
    log(f"DONE step={step} in {(time.time()-t0)/60:.1f} min -> {OUT}")


if __name__ == "__main__":
    main()
