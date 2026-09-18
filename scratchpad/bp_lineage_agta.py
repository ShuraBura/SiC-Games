"""R-106 anchor development:
 (A) #5 re-anchor — lineage DYNAMICS vs Guyon et al. 2024 (Nat Comms) EMPIRICAL per-generation rates: descent-group
     extinction [0.16, 30]%/gen, successful-group growth [0.12, 2.5]/gen. Snapshot lineage sizes at t=500 and t=800
     (300 steps = 25 yr ~ 1 generation); extinction = fraction of t500 lineages gone by t800; growth = mean size
     ratio of survivors. NOTE the Guyon range is broad + skews dynastic (China imperial, Ui Neill), so this is a
     CONSISTENCY SCREEN, not a tight target.
 (B) #14 cross-check — WITHIN-CELL material Gini vs Agta (Page et al.) within-camp Gini mean 0.23 (range 0-0.44,
     age-corrected household goods). Median over cells (>=2 adults) of the adult material Gini at t=800.
Current canon, both biomes, 3-world panel.
"""
import os
import sys
import statistics as st
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from bp_gini import gini

STEPS = 800
GEN = 300          # ~25 yr = 1 generation
ADULT_MO = 180.0


def lineage_sizes(w):
    c = {}
    for a in w.agent_list:
        lid = getattr(a, "_lineage", None)
        if lid is not None:
            c[lid] = c.get(lid, 0) + 1
    return c


def run_one(clim, ws):
    w = build(dict(runconfig.load()["DemographyConfig"]), ws, 0, clim=clim)
    snap0 = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == STEPS - GEN:
            snap0 = lineage_sizes(w)
    snap1 = lineage_sizes(w)
    # (A) lineage extinction + growth over the last generation
    ext = grow = float("nan")
    if snap0:
        alive0 = set(snap0)
        extinct = sum(1 for l in alive0 if snap1.get(l, 0) == 0)
        ext = extinct / len(alive0)
        survivors = [snap1[l] / snap0[l] for l in alive0 if snap1.get(l, 0) > 0]
        grow = float(np.mean(survivors)) if survivors else float("nan")
    # (B) within-cell adult material Gini (Agta within-camp analog)
    by_cell = {}
    for a in w.agent_list:
        if a.age >= ADULT_MO:
            by_cell.setdefault(a.pos, []).append(getattr(a, "material", 0.0))
    cell_ginis = [gini(v) for v in by_cell.values() if len(v) >= 2]
    within_cell_gini = st.median(cell_ginis) if cell_ginis else float("nan")
    return ext, grow, within_cell_gini, len(snap0) if snap0 else 0, len(snap1)


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return v.mean() if len(v) else float("nan")


for clim in ("temperate", "savanna"):
    rows = [run_one(clim, ws) for ws in (0, 1, 2)]
    print(f"== {clim.upper()} ==", flush=True)
    print(f"  (A) lineage extinction/gen {ms([r[0] for r in rows]):.1%}  (Guyon [0.16-30]%)   "
          f"survivor growth/gen {ms([r[1] for r in rows]):.2f}x  (Guyon [0.12-2.5])   "
          f"n_lineages {ms([r[3] for r in rows]):.0f}->{ms([r[4] for r in rows]):.0f}", flush=True)
    print(f"  (B) within-CELL adult material Gini (median) {ms([r[2] for r in rows]):.3f}  (Agta within-camp 0.23 [0-0.44])",
          flush=True)
