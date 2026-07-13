"""Validate the R-64 emergent-stratification PREDICTION (not a calibration):
  (X) CROSS-WORLD: %stratified rises with world RICHNESS (mean NPP / storable-resource fraction).
  (Y) WITHIN-WORLD: stratified settlements sit on RICHER catchments (higher S_pot) than egalitarian ones.
Full settlement-hierarchy config (R-64) across a richness-ordered set of worlds × seeds. Writes per-run results to a
progress file (flushed) + JSON — the population-weighted %stratified is the headline.

Run:  py -3 -u sic_games/outputs/substrate_run/validate_stratification.py   (from repo root)
Env:  V_STEPS (800), V_SEEDS (2)
"""
import sys, os, time, json, statistics
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

STEPS = int(os.environ.get("V_STEPS", "800"))
SEEDS = int(os.environ.get("V_SEEDS", "2"))
# richness-ordered (rich → poor), skipping the extinct/degenerate ones from the biome battery (subtropical, alpine)
WORLDS = [("coastal", "tropical"), ("coastal", "temperate"), ("flat", "tropical"),
          ("flat", "temperate"), ("hilly", "temperate"), ("flat", "boreal"), ("hilly", "boreal")]
PROG = os.path.join(HERE, "validate_progress.txt")
OUT = os.path.join(HERE, "validate_results.json")


def log(m):
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(m + "\n"); fh.flush()
    print(m, flush=True)


def run(terr, clim, seed):
    k = world_lottery_climate(seed, terrain=terr, climate=clim)
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    base0 = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base0.level(x, y) > 0]
    if not land:
        return None
    cap = ClimateField(base, a_seas=0.4)
    # world richness proxies
    mean_npp = float(np.mean([f.npp_gm2[y, x] for (x, y) in land]))
    spot = np.maximum(getattr(f, "aquatic_food", np.zeros_like(f.npp_gm2)), getattr(f, "cultivability", np.zeros_like(f.npp_gm2)))
    aquatic_frac = float(np.mean([spot[y, x] > 0.1 for (x, y) in land]))
    d = emergent_village_demog().model_copy(update=dict(
        enable_landscape_packing=True, enable_sedentism_fertility=True,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
        enable_catchment_ceiling=True, enable_settlement_scalar_stress=True, settle_catchment_radius=1))
    w = TerrainWorld(n_agents=3000, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=[land[i % len(land)] for i in range(3000)], demography_cfg=d)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return dict(terr=terr, clim=clim, seed=seed, mean_npp=round(mean_npp, 0), aquatic_frac=round(aquatic_frac, 3), extinct=True, pct_strat=0.0)
    al = w.agent_list; pop = len(al)
    socs = Counter(w._band_society.get(a._group.band_id, "egalitarian_forager") for a in al)
    pct_strat = round(100 * socs.get("stratified_chiefdom", 0) / pop, 1)
    occ = Counter(a.pos for a in al)
    vs = sorted([occ.get(s, 0) for s in w._settlement_sites], reverse=True)
    # (Y) within-world: catchment S_pot of stratified vs egalitarian settlement sites (band society at the site's occupants)
    def site_soc(s):
        bids = Counter(a._group.band_id for a in al if a.pos == s)
        if not bids:
            return "egalitarian_forager"
        return w._band_society.get(bids.most_common(1)[0][0], "egalitarian_forager")
    strat_spot = [float(spot[s[1], s[0]]) for s in w._settlement_sites if "stratified" in str(site_soc(s))]
    egal_spot = [float(spot[s[1], s[0]]) for s in w._settlement_sites if "stratified" not in str(site_soc(s))]
    return dict(terr=terr, clim=clim, seed=seed, mean_npp=round(mean_npp, 0), aquatic_frac=round(aquatic_frac, 3),
                pop=pop, n_sites=len(vs), village_med=statistics.median(vs) if vs else 0, pct_strat=pct_strat,
                strat_site_spot=round(statistics.mean(strat_spot), 3) if strat_spot else None,
                egal_site_spot=round(statistics.mean(egal_spot), 3) if egal_spot else None, extinct=False)


def main():
    open(PROG, "w").close()
    log(f"validate stratification prediction: {len(WORLDS)} worlds × {SEEDS} seeds, {STEPS} steps. "
        f"Prediction: %strat rises with richness; stratified sites richer than egalitarian.")
    results = []
    t0 = time.time()
    for (terr, clim) in WORLDS:
        for seed in range(SEEDS):
            try:
                r = run(terr, clim, seed)
            except Exception as e:
                r = dict(terr=terr, clim=clim, seed=seed, error=repr(e))
            if r:
                results.append(r)
                json.dump(results, open(OUT, "w"))
                el = time.time() - t0
                log(f"  {terr:8s} {clim:9s} s{seed}: npp={r.get('mean_npp')} aq={r.get('aquatic_frac')} "
                    f"pop={r.get('pop','-')} strat={r.get('pct_strat')}% village_med={r.get('village_med','-')} "
                    f"strat_spot={r.get('strat_site_spot')} egal_spot={r.get('egal_site_spot')} | el={el/60:.1f}m")
    # correlation richness ↔ stratification
    ok = [r for r in results if not r.get("extinct") and not r.get("error") and r.get("pop")]
    if len(ok) >= 3:
        npp = np.array([r["mean_npp"] for r in ok]); strat = np.array([r["pct_strat"] for r in ok])
        aq = np.array([r["aquatic_frac"] for r in ok])
        log(f"CROSS-WORLD: corr(mean_npp, %strat)={np.corrcoef(npp, strat)[0,1]:+.2f}  "
            f"corr(aquatic_frac, %strat)={np.corrcoef(aq, strat)[0,1]:+.2f}  (prediction: POSITIVE)")
        sp = [(r["strat_site_spot"], r["egal_site_spot"]) for r in ok if r.get("strat_site_spot") and r.get("egal_site_spot")]
        if sp:
            log(f"WITHIN-WORLD: stratified-site S_pot vs egalitarian: "
                f"{np.mean([a for a,b in sp]):.3f} vs {np.mean([b for a,b in sp]):.3f} "
                f"({sum(1 for a,b in sp if a>b)}/{len(sp)} worlds strat>egal; prediction: strat RICHER)")
    log(f"DONE {(time.time()-t0)/60:.1f}m -> {OUT}")


if __name__ == "__main__":
    main()
