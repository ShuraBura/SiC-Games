"""R-106 #12/#13 — rank-size slope + primacy over the CLEAN village partition (village_sizes, nearest-site) vs the
contaminated settlements() panel. Anchors: #12 zipf_slope ≈ −1 (Zipf, Johnson); #13 primate_ratio ≈ 1 (no primate
centre). Current canon, both biomes, 3-world panel."""
import os
import sys
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
    vs = w.village_sizes() or {}
    st = w.settlements() or {}
    return (vs.get("village_zipf"), vs.get("village_primate"), vs.get("n_villages", 0),
            st.get("zipf_slope"), st.get("primate_ratio"))


def ms(v):
    v = np.array([x for x in v if x is not None and x == x], float)
    return v.mean() if len(v) else float("nan")


for clim in ("temperate", "savanna"):
    rows = [run_one(clim, ws) for ws in (0, 1, 2)]
    print(f"== {clim.upper()} | #12 zipf ≈ −1 (Zipf), #13 primacy ≈ 1 (no primate centre) ==", flush=True)
    print(f"  CLEAN village partition : zipf {ms([r[0] for r in rows]):+.2f}  primacy {ms([r[1] for r in rows]):.2f}"
          f"  n_villages {ms([r[2] for r in rows]):.0f}", flush=True)
    print(f"  (ref) settlements() panel: zipf {ms([r[3] for r in rows]):+.2f}  primacy {ms([r[4] for r in rows]):.2f}",
          flush=True)
