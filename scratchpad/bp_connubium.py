"""R-106 #4 connubium re-score. Anchor: White 2017 MVP 150 [79-332] (mating-network reach). The pooled '15/25' was
an artefact of including near-dead sparse worlds (corr(density, connubium)=+0.55; note #4). Score on the appropriately
-dense canonical world, not pooled. Under canon (adaptive_connubium on) the diagnostic records reach_pop (network pop
within realized reach), the right unit. Current canon, both biomes, 3-world panel; report connubium_med + density."""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = 800


def run_one(clim, ws):
    w = build(dict(runconfig.load()["DemographyConfig"]), ws, 0, clim=clim)
    meds, means, npools = [], [], []
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t >= STEPS - 60:                 # sample the last ~5 yr to catch pairing phases (reset each phase)
            c = w.connubium() or {}
            if c.get("n_pools", 0) > 0:
                meds.append(c["median"]); means.append(c["mean"]); npools.append(c["n_pools"])
    pop = len(w.agent_list)
    # density over OCCUPIED area (the probe world lacks _habitable_cells)
    ncells = len({a.pos for a in w.agent_list})
    dens = pop / (ncells * 100.0) if ncells else float("nan")
    if not meds:
        return float("nan"), float("nan"), 0, pop, dens
    return float(np.mean(meds)), float(np.mean(means)), float(np.mean(npools)), pop, dens


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return v.mean() if len(v) else float("nan")


for clim in ("temperate", "savanna"):
    rows = [run_one(clim, ws) for ws in (0, 1, 2)]
    inrange = "  <== IN [79-332]" if 79 <= ms([r[0] for r in rows]) <= 332 else ""
    print(f"== {clim.upper()} | White MVP 150 [79-332] ==", flush=True)
    print(f"  connubium_med {ms([r[0] for r in rows]):.0f}{inrange}  mean {ms([r[1] for r in rows]):.0f}  "
          f"n_pools {ms([r[2] for r in rows]):.0f}  | pop {ms([r[3] for r in rows]):.0f}  "
          f"regional_density {ms([r[4] for r in rows]):.4f}/km2", flush=True)
