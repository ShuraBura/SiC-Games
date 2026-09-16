"""R-106 tier-5 band-size lever test: does widening the provisioning radius (central-place foraging) raise
band_med_adults toward Hill 28.2 WITHOUT inflating pop/e0 or breaking the biome control?

Mechanism: _settlement_carrying_capacity caps a residence's food at ceiling_mult * sum(cell yield over a
(2*rad+1)^2 catchment). Canon rad=1 (9 cells) feeds ~10 adults. Sweep settle_catchment_radius and watch
band_med_adults, e0, pop, n_bands on BOTH biomes (savanna is the natural control — the fix must lift it too).
Low-noise 3-world panel, life table 400-800.
"""
import os
import sys
import statistics as st
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
DFROM = int(os.environ.get("C_DFROM", "400"))
RADS = [int(x) for x in os.environ.get("C_RADS", "1,2,3").split(",")]
ADULT_MO = 15.0 * 12.0


def band_med_adults(w):
    groups = {}
    for a in w.agent_list:
        groups.setdefault(a._group.band_id, []).append(a)
    adults = [sum(1 for a in g if a.age >= ADULT_MO) for g in groups.values()]
    sizes = [len(g) for g in groups.values()]
    return (st.median(adults) if adults else 0.0, st.median(sizes) if sizes else 0.0, len(groups))


def run_one(clim, ws, rad):
    canon = dict(runconfig.load()["DemographyConfig"])
    canon["settle_catchment_radius"] = rad
    w = build(canon, ws, 0, clim=clim)
    snap = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == DFROM:
            snap = w.raw_demographic_counters()
    lt = w.life_table(since=snap) if snap else w.life_table()
    bma, bm, nb = band_med_adults(w)
    return dict(band_med_adults=bma, band_med=bm, n_bands=nb, e0=lt["e0"], pop=len(w.agent_list))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    biomes = os.environ.get("C_BIOMES", "temperate,savanna").split(",")
    print(f"CATCHMENT-RADIUS SWEEP | {STEPS} steps | worlds {worlds} | Hill band_med_adults=28.2 | "
          f"guardrail e0 [21-37]", flush=True)
    for clim in biomes:
        print(f"== {clim.upper()} ==", flush=True)
        for rad in RADS:
            rows = [run_one(clim, ws, rad) for ws in worlds]
            bma, bmae = ms([r["band_med_adults"] for r in rows])
            bm, _ = ms([r["band_med"] for r in rows])
            nb, _ = ms([r["n_bands"] for r in rows])
            e0, _ = ms([r["e0"] for r in rows])
            pp, _ = ms([r["pop"] for r in rows])
            hit = "  <== ~28.2" if abs(bma - 28.2) <= 4 else ""
            print(f"  rad{rad} (cells {(2*rad+1)**2:2d})  band_med_adults {bma:.1f}+/-{bmae:.1f}{hit}  "
                  f"band_med {bm:.1f}  n_bands {nb:.0f}  e0 {e0:.1f}  pop {pp:.0f}", flush=True)


if __name__ == "__main__":
    main()
