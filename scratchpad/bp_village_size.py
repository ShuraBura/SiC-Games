"""R-106 #3 village size re-measure. Anchor: Alvard 2009 verified 50-250 (Yanomamo). The current marker settle_med
(settlements(), exact-cell) reads ~32 (FRAGMENTS a multi-cell village); settlement_clusters() union-find reads ~500
(OVER-merges the packing blob). Neither is a village.

Clean partition: assign each agent to its NEAREST settlement site (Voronoi) within the catchment radius r; a village
= the residents of one site. No double-count, no blob-merge. Report median/max village size, n_villages, resident
fraction, vs Alvard 50-250. Current canon, both biomes, 3-world panel.
"""
import os
import sys
import statistics as st
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = 800


def run_one(clim, ws):
    w = build(dict(runconfig.load()["DemographyConfig"]), ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    sites = list(getattr(w, "_settlement_sites", ()))
    pop = w.agent_list
    r = int(getattr(w._demog, "settle_radius", 2))
    if not sites:
        return dict(vmed=0, vmax=0, nv=0, fres=0.0, pop=len(pop), scmed=0)
    # nearest-site (Voronoi) assignment within radius r -> resident villages, no double-count
    vsize = {s: 0 for s in sites}
    for a in pop:
        ax, ay = a.pos
        best = None
        for (sx, sy) in sites:
            d = max(abs(ax - sx), abs(ay - sy))
            if best is None or d < best[0]:
                best = (d, (sx, sy))
        if best is not None and best[0] <= r:
            vsize[best[1]] += 1
    sizes = sorted((n for n in vsize.values() if n > 0), reverse=True)
    resident = sum(sizes)
    # also the exact-cell settle_med for reference (the current marker)
    stt = w.settlements() or {}
    return dict(vmed=st.median(sizes) if sizes else 0, vmax=sizes[0] if sizes else 0, nv=len(sizes),
                fres=resident / len(pop) if pop else 0.0, pop=len(pop), scmed=stt.get("median", 0))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return v.mean() if len(v) else float("nan")


for clim in ("temperate", "savanna"):
    rows = [run_one(clim, ws) for ws in (0, 1, 2)]
    print(f"== {clim.upper()} | Alvard village 50-250 | nearest-site (Voronoi, within catchment r) partition ==", flush=True)
    print(f"  village_med {ms([r['vmed'] for r in rows]):.0f}  village_max {ms([r['vmax'] for r in rows]):.0f}  "
          f"n_villages {ms([r['nv'] for r in rows]):.0f}  frac_resident {ms([r['fres'] for r in rows]):.2f}", flush=True)
    print(f"  (ref) exact-cell settle_med {ms([r['scmed'] for r in rows]):.0f}  | pop {ms([r['pop'] for r in rows]):.0f}",
          flush=True)
