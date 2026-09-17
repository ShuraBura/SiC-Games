"""R-106 #17 fission-ceiling audit: is the settle_max over-run REAL, or a unit/measurement artifact + stale data?

Anchor (Alberti 2014, verified): community-size ceiling — P(critical scalar stress)=0.99 at N~158, ethnographic max
~250 (Alvard). The MARKER_MATRIX 'MISS' (median settle_max 220) is from 52 STALE pre-R105/R106 trajectories.
`settle_max` comes from settlements() which counts agents on the EXACT site cell (fragments a multi-cell village).
This measures the largest COMMUNITY on CURRENT canon under three units and compares to 158/250:
  - settlements().max      : exact-cell occupancy (the current #17 marker)
  - settlement_clusters().cluster_max : union-find whole community (the clean measure)
  - bigband_max            : largest band_id total (the fissioning social unit)
Both biomes, low-noise 3-world panel.
"""
import os
import sys
import numpy as np
from collections import Counter

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
    st = w.settlements() or {}
    sc = w.settlement_clusters() or {}
    bcount = Counter(a._group.band_id for a in w.agent_list)
    bigband_max = max(bcount.values()) if bcount else 0
    return dict(smax=st.get("max", 0), smed=st.get("median", 0), n_settle=st.get("n", 0),
                fres=st.get("frac_resident", 0.0),
                cmax=sc.get("cluster_max", 0), cmed=sc.get("cluster_med", 0), n_clust=sc.get("n_clusters", 0),
                bbmax=bigband_max, pop=len(w.agent_list))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return v.mean() if len(v) else float("nan")


for clim in ("temperate", "savanna"):
    rows = [run_one(clim, ws) for ws in (0, 1, 2)]
    print(f"== {clim.upper()} (current canon) | anchor: community ceiling ~158, ethnographic max ~250 ==", flush=True)
    print(f"  settlements() exact-cell : max {ms([r['smax'] for r in rows]):.0f}  med {ms([r['smed'] for r in rows]):.0f}"
          f"  n {ms([r['n_settle'] for r in rows]):.0f}  frac_resident {ms([r['fres'] for r in rows]):.2f}", flush=True)
    print(f"  settlement_clusters()    : cluster_max {ms([r['cmax'] for r in rows]):.0f}  "
          f"cluster_med {ms([r['cmed'] for r in rows]):.0f}  n_clusters {ms([r['n_clust'] for r in rows]):.0f}", flush=True)
    print(f"  bigband_max (band_id)    : {ms([r['bbmax'] for r in rows]):.0f}   | pop {ms([r['pop'] for r in rows]):.0f}",
          flush=True)
