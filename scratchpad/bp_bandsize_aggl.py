"""R-106 tier-5 band-size lever test #2: the AGGLOMERATION<->SIZE-REPULSION balance.

Sweep #1 (bp_bandsize_catchment) showed the food ceiling caps POPULATION, not band size — band size is set by the
clustering equilibrium. This sweeps that equilibrium: repulsion_gain (canon 0.3; size-repulsion pushes agents off
large clusters) down toward 0, plus a stronger-agglomeration arm (aggl_beta), to see whether band_med_adults climbs
toward Hill 28.2 — and whether it does so as BIGGER BANDS or by COLLAPSING TO VILLAGES.

Reports the band-adult distribution (median, mean, max, % of pop in village-scale bands >20 adults, % in fragments
<5), e0 and pop, on BOTH biomes. Low-noise 3-world panel, life table 400-800.
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
ADULT_MO = 15.0 * 12.0

ARMS = {
    "canon(rg0.3)":   {},
    "rg0.2":          {"repulsion_gain": 0.2},
    "rg0.1":          {"repulsion_gain": 0.1},
    "rg0.0":          {"repulsion_gain": 0.0},
    "rg0.0_beta1.5":  {"repulsion_gain": 0.0, "aggl_beta": 1.5},
}


def band_stats(w):
    groups = {}
    for a in w.agent_list:
        groups.setdefault(a._group.band_id, []).append(a)
    adults = [sum(1 for a in g if a.age >= ADULT_MO) for g in groups.values()]
    pop = len(w.agent_list)
    if not adults or pop == 0:
        return dict(bma=0.0, mean=0.0, mx=0.0, pct_village=0.0, pct_frag=0.0, nb=0)
    # % of the POPULATION living in village-scale bands (>20 adults) vs fragments (<5 adults)
    pop_in_village = sum(len(g) for g in groups.values() if sum(1 for a in g if a.age >= ADULT_MO) > 20)
    pop_in_frag = sum(len(g) for g in groups.values() if sum(1 for a in g if a.age >= ADULT_MO) < 5)
    return dict(bma=st.median(adults), mean=float(np.mean(adults)), mx=float(np.max(adults)),
                pct_village=pop_in_village / pop, pct_frag=pop_in_frag / pop, nb=len(groups))


def run_one(clim, ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"])
    canon.update(ov)
    w = build(canon, ws, 0, clim=clim)
    snap = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == DFROM:
            snap = w.raw_demographic_counters()
    lt = w.life_table(since=snap) if snap else w.life_table()
    bs = band_stats(w)
    bs["e0"] = lt["e0"]; bs["pop"] = len(w.agent_list)
    return bs


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return v.mean() if len(v) else float("nan")


def se(v):
    v = np.array([x for x in v if x == x], float)
    return v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    biomes = os.environ.get("C_BIOMES", "temperate,savanna").split(",")
    arms = os.environ.get("C_ARMS", ",".join(ARMS)).split(",")
    print(f"AGGL<->REPULSION SWEEP | {STEPS} steps | worlds {worlds} | Hill band_med_adults=28.2 | "
          f"guardrail e0 [21-37]", flush=True)
    for clim in biomes:
        print(f"== {clim.upper()} ==", flush=True)
        for arm in arms:
            rows = [run_one(clim, ws, ARMS[arm]) for ws in worlds]
            bma = ms([r["bma"] for r in rows]); bmae = se([r["bma"] for r in rows])
            mean = ms([r["mean"] for r in rows]); mx = ms([r["mx"] for r in rows])
            pv = ms([r["pct_village"] for r in rows]); pf = ms([r["pct_frag"] for r in rows])
            e0 = ms([r["e0"] for r in rows]); pp = ms([r["pop"] for r in rows]); nb = ms([r["nb"] for r in rows])
            hit = "  <== ~28" if abs(bma - 28.2) <= 4 else ""
            print(f"  {arm:15s} bma {bma:.1f}+/-{bmae:.1f}{hit}  mean {mean:.1f}  max {mx:.0f}  "
                  f"%pop>20ad {pv:.0%}  %pop<5ad {pf:.0%}  n_bands {nb:.0f}  e0 {e0:.1f}  pop {pp:.0f}", flush=True)


if __name__ == "__main__":
    main()
