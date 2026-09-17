"""R-106 Add.90: did Add.87's concentrators raise the ADULTS-ONLY material Gini, or only the child-inflated all-ages
figure? Compare pre-Add.87 canon (the 4 knobs back to neutral) vs the adopted canon, on the adults-only statistic."""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from bp_gini import gini

STEPS = 800
ADULT_MO = 15.0 * 12.0
PRE = {"material_capture_frac": 0.0, "material_heir_by_status": False,
       "leveling_tolerance": 0.0, "feast_tolerance": 0.0}   # pre-Add.87 neutral


def run_one(clim, ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    pop = w.agent_list
    allm = [getattr(a, "material", 0.0) for a in pop]
    adm = [getattr(a, "material", 0.0) for a in pop if a.age >= ADULT_MO]
    return gini(allm), gini(adm)


def ms(v):
    v = np.array(v, float); return v.mean(), (v.std(ddof=1)/np.sqrt(len(v)) if len(v) > 1 else 0.0)


for clim in ("temperate", "savanna"):
    for name, ov in (("pre-Add.87", PRE), ("adopted", {})):
        rows = [run_one(clim, ws, ov) for ws in (0, 1, 2)]
        ga, _ = ms([r[0] for r in rows]); gd, gde = ms([r[1] for r in rows])
        print(f"  {clim:9s} {name:10s} | all-ages {ga:.3f} | ADULTS {gd:.3f}+/-{gde:.3f}  (BHM 0.36)", flush=True)
