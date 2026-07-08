"""Biome battery — band size + habitability across all terrain x climate worlds.

5 terrains x 5 climates x N seeds, boosted founders so marginal (desert/cold) worlds get a fair chance to bootstrap
before we call them uninhabitable (separates 'harsh-but-viable' from 'can't-even-start'). Emergent band size ON.
Correct biome labels (FOREST=2, SAVANNA=3, GRASS=4, DESERT=5, MOUNTAIN=6). Flushes progress per run to progress file.

Run:  py -3 -u sic_games/outputs/climate_viz/run_biome_battery.py    (from repo root)
"""
import sys, os, time, json
from collections import Counter
import numpy as np

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

NAMES = {0: "water", 1: "wetland", 2: "forest", 3: "savanna", 4: "grass", 5: "desert", 6: "mountain"}
TERRAINS = ("flat", "hilly", "mountainous", "coastal", "alpine")
CLIMATES = ("tropical", "subtropical", "temperate", "boreal", "savanna")
SEEDS = int(os.environ.get("BATTERY_SEEDS", "5"))
FOUNDERS = int(os.environ.get("BATTERY_FOUNDERS", "1500"))
STEPS = int(os.environ.get("BATTERY_STEPS", "300"))

PROG = os.path.join(HERE, "battery_progress.txt")
OUT = os.path.join(HERE, "battery_results.json")


def log(msg):
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
        fh.flush()
    print(msg, flush=True)


def run_one(terr, clim, seed):
    k = world_lottery_climate(seed, terrain=terr, climate=clim)
    f = generate_world(k, mode="climate")
    land = (f.isWater == 0)
    b = f.biome[land]
    biomes = {NAMES[v]: round(float((b == v).mean()), 3) for v in np.unique(b)}
    hf = ClimateField(NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    hab = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    if not hab:
        return dict(terr=terr, clim=clim, seed=seed, biomes=biomes, hab_cells=0, survived=False,
                    pop=0, bands=[], extinct_step=0)
    pos = [hab[i % len(hab)] for i in range(FOUNDERS)]
    d = emergent_village_demog().model_copy(update=dict(enable_emergent_band_size=True))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=hf, placement_positions=pos, demography_cfg=d)
    extinct_step = None
    for s in range(STEPS):
        w.step()
        if not w.agent_list:
            extinct_step = s
            break
    survived = bool(w.agent_list)
    bands = list(Counter(a._group.band_id for a in w.agent_list).values()) if survived else []
    return dict(terr=terr, clim=clim, seed=seed, biomes=biomes, hab_cells=len(hab), survived=survived,
                pop=len(w.agent_list) if survived else 0, bands=bands, extinct_step=extinct_step)


def main():
    open(PROG, "w").close()
    t0 = time.time()
    total = len(TERRAINS) * len(CLIMATES) * SEEDS
    log(f"battery: {len(TERRAINS)} terrains x {len(CLIMATES)} climates x {SEEDS} seeds = {total} runs; "
        f"founders={FOUNDERS} steps={STEPS}")
    results = []
    n = 0
    for terr in TERRAINS:
        for clim in CLIMATES:
            for seed in range(SEEDS):
                n += 1
                try:
                    r = run_one(terr, clim, seed)
                except Exception as e:  # keep the battery alive
                    r = dict(terr=terr, clim=clim, seed=seed, error=repr(e), survived=False, pop=0, bands=[])
                results.append(r)
                el = time.time() - t0
                eta = el / n * (total - n)
                bnd = np.median(r["bands"]) if r.get("bands") else 0
                log(f"[{n:3d}/{total}] {terr:11s} {clim:11s} s{seed}: "
                    f"{'OK ' if r['survived'] else 'EXT'} pop={r['pop']:4d} medBand={bnd:.0f} "
                    f"| el={el/60:.1f}m eta={eta/60:.1f}m")
                with open(OUT, "w", encoding="utf-8") as fh:
                    json.dump(results, fh)
    log(f"DONE in {(time.time()-t0)/60:.1f} min -> {OUT}")


if __name__ == "__main__":
    main()
