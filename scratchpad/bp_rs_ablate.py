"""R-106 Addendum 102 — ABLATION: which knob carries the #11 status->RS skew?

Correlation failed to find the driver (nothing tracks within-world; the cross-world connubium ranking was an n=3
coincidence). So ablate. Female pairing is PROWESS-WEIGHTED by `mate_choice_strength` (canon 5.0) at EVERY pairing,
including re-pairing after widowhood, and the same weighting decides which already-married male wins a polygynous
bond (`polygyny_rate` 0.005, `max_wives` 3). Either could carry the skew.

This is a COMPARATIVE test, so per Addendum 101's rule it runs safely in the fast probe harness: both arms share the
harness, so the harness cancels. Absolute values here are the PROBE regime, not canon; the ARM ORDERING is what
transfers.

Arms sweep mate_choice_strength and pin monogamy, and report the age-partialled corr(prowess, n_fathered) exactly
as run_campaign computes it.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from bp_gini import gini

STEPS = int(os.environ.get("C_STEPS", "800"))
MEN_MO = 180.0

ARMS = {
    "canon (m=5.0)":        {},
    "m=0 (no status wt)":   {"mate_choice_strength": 0.0},
    "m=1":                  {"mate_choice_strength": 1.0},
    "m=2":                  {"mate_choice_strength": 2.0},
    "m=5, max_wives=1":     {"max_wives": 1},
    "m=5, polygyny_rate=0": {"polygyny_rate": 0.0},
}


def pcorr(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def partial(x, y, z):
    rxy, rxz, ryz = pcorr(x, y), pcorr(x, z), pcorr(y, z)
    d = ((1 - rxz ** 2) * (1 - ryz ** 2)) ** 0.5
    return (rxy - rxz * ryz) / d if d > 0 else float("nan")


def run_one(clim, ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    males = [a for a in w.agent_list if a.sex == "male" and a.age >= MEN_MO]
    if len(males) < 9:
        return (float("nan"),) * 4
    pr = [getattr(a, "prowess", 1.0) for a in males]
    off = [float(getattr(a, "_n_fathered", 0)) for a in males]
    age = [float(a.age) for a in males]
    wives = [len(getattr(a, "_wives", ())) for a in males]
    poly = sum(1 for v in wives if v > 1) / len(wives)
    return partial(pr, off, age), gini(off), poly, len(w.agent_list)


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    print(f"#11 ABLATION | {clim} | {STEPS} steps | worlds {worlds} | anchor: von Rueden monogamous ~0.15")
    print("(probe harness => ABSOLUTE values are the probe regime; the ARM ORDERING is the result)\n")
    for arm, ov in ARMS.items():
        rows = [run_one(clim, ws, ov) for ws in worlds]
        r, re_ = ms([x[0] for x in rows])
        g, _ = ms([x[1] for x in rows])
        p, _ = ms([x[2] for x in rows])
        n, _ = ms([x[3] for x in rows])
        print(f"  {arm:22s} status->RS {r:+.3f}+/-{re_:.3f}   male_RS_gini {g:.3f}   polygyny {p:.3f}   pop {n:.0f}")


if __name__ == "__main__":
    main()
