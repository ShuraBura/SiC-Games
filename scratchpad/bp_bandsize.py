"""R-106 tier-5 band-size diagnosis: reproduce the saturation, and separate a cohesion-CAP limit from a
spatial/demographic one.

Benchmark: band_med_adults = 28.2 (Hill 2011); model reads ~11.8 (fails 16/16). Prior finding (Addendum 22):
the cohesion budget cohesion_frac = clamp01(assabiyah + leader - repulsion - malnutrition) saturates at 1.0, so
split_thr collapses to band_split_size and the four band-size mechanisms are inert. This reproduces that on the
CURRENT canon and asks the decisive question:
  - if realised band size ~ split_thr  -> a COHESION-CAP limit (de-saturating / raising the cap is the lever);
  - if band size << split_thr           -> a SPATIAL/demographic limit (bands never grow to their allowed size;
                                           de-saturation cannot help — ties to the packing arc).

Canon, biome_seasonality ON, 600 agents, low-noise panel. Per-band probe hook `_band_probe` (bit-exact off).
"""
import os
import sys
import statistics as st
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("B_STEPS", "800"))
SAMPLE_FROM = int(os.environ.get("B_SAMPLE_FROM", "740"))
SAMPLE_EVERY = int(os.environ.get("B_SAMPLE_EVERY", "4"))
ADULT_MO = 15.0 * 12.0


def band_medians(w):
    """median total size and median adult count per band_id (the band_med / band_med_adults markers)."""
    groups = {}
    for a in w.agent_list:
        groups.setdefault(a._group.band_id, []).append(a)
    sizes = [len(g) for g in groups.values()]
    adults = [sum(1 for a in g if a.age >= ADULT_MO) for g in groups.values()]
    return (st.median(sizes) if sizes else 0.0, st.median(adults) if adults else 0.0, len(groups))


def run_one(clim, world_seed, agent_seed):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, world_seed, agent_seed, clim=clim)
    rows = []
    for t in range(STEPS):
        if t >= SAMPLE_FROM and (t % SAMPLE_EVERY == 0):
            w._band_probe = []
        w.step()
        if not w.agent_list:
            break
        if t >= SAMPLE_FROM and (t % SAMPLE_EVERY == 0) and w._band_probe:
            rows.extend(w._band_probe)
        w._band_probe = None
    bmed, bmed_ad, nband = band_medians(w)
    return dict(rows=rows, band_med=bmed, band_med_adults=bmed_ad, n_bands=nband, pop=len(w.agent_list))


def main():
    biomes = os.environ.get("B_BIOMES", "temperate,savanna").split(",")
    worlds = [int(x) for x in os.environ.get("B_WORLDS", "0,1,2").split(",")]
    agents = [int(x) for x in os.environ.get("B_AGENTS", "0").split(",")]
    print(f"BAND-SIZE DIAGNOSIS | canon | {STEPS} steps | sample>={SAMPLE_FROM} every {SAMPLE_EVERY} | "
          f"worlds {worlds} x agents {agents} | Hill anchor band_med_adults=28.2", flush=True)
    for clim in biomes:
        allrows, bmed, bmed_ad, nb = [], [], [], []
        for ws in worlds:
            for as_ in agents:
                r = run_one(clim, ws, as_)
                allrows.extend(r["rows"]); bmed.append(r["band_med"])
                bmed_ad.append(r["band_med_adults"]); nb.append(r["n_bands"])
                print(f"  {clim} w{ws}a{as_}: band_med_adults {r['band_med_adults']:.1f} band_med {r['band_med']:.1f} "
                      f"n_bands {r['n_bands']} pop {r['pop']} rows {len(r['rows'])}", flush=True)
        sizes = np.array([x["size"] for x in allrows], float)
        thr = np.array([x["split_thr"] for x in allrows], float)
        coh = np.array([x["cohesion_frac"] for x in allrows], float)
        asb = np.array([x["assabiyah"] for x in allrows], float)
        led = np.array([x["leader_term"] for x in allrows], float)
        rep = np.array([x["repulsion"] for x in allrows], float)
        mal = np.array([x["malnutrition"] for x in allrows], float)
        util = sizes / np.maximum(thr, 1e-9)     # how close a band is to its own fission threshold
        print(f"  === {clim} (band-records n={len(allrows)}) ===")
        print(f"    band_med_adults {np.mean(bmed_ad):.1f} +/- {np.std(bmed_ad, ddof=1)/np.sqrt(len(bmed_ad)):.1f}"
              f"  (Hill 28.2) | band_med {np.mean(bmed):.1f}")
        print(f"    cohesion_frac   mean {coh.mean():.3f}  frac at 1.0: {(coh >= 0.999).mean():.2%}  "
              f"(saturated?)")
        print(f"    budget terms    assabiyah {asb.mean():.2f}  leader {led.mean():.2f}  "
              f"repulsion {rep.mean():.2f}  malnutrition {mal.mean():.2f}")
        print(f"    split_thr       mean {thr.mean():.1f}  (band_split_size cap)")
        print(f"    band size       mean {sizes.mean():.1f}  median {np.median(sizes):.1f}")
        print(f"    size / split_thr  mean {util.mean():.2f}  median {np.median(util):.2f}  "
              f"-> {'COHESION-CAP limit' if np.median(util) > 0.8 else 'SPATIAL limit (bands never fill their cap)'}")
        if os.environ.get("B_DUMP"):
            np.savez(f"{os.environ['B_DUMP']}_{clim}.npz", sizes=sizes, thr=thr, coh=coh, util=util,
                     band_med_adults=np.array(bmed_ad))
            print(f"    [dumped {os.environ['B_DUMP']}_{clim}.npz]")


if __name__ == "__main__":
    main()
