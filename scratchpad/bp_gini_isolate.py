"""R-106 tier-10 isolation: which flow keeps material Gini at 0.17 vs BHM 0.36?

Addendum 82: cred (status) Gini is at the anchor (0.36) but material does not follow (corr ~0.2). Candidate flows:
  FLATTENERS  - enable_leveling (0.79, Boehm reverse-dominance takes from the wealthy); legit_feast_frac (0.25,
                feast debits proportional-to-wealth then redistributes per-capita).
  DECOUPLER   - material_heir_by_status=False: primogeniture inheritance concentrates within a lineage but is NOT
                chosen by status, so a big concentrator does not track cred.
Ablation arms (diagnostic, NOT adoption): remove each flattener / couple inheritance to status, and see which
moves material Gini toward 0.36 and corr(cred,material) up. Guardrail: pop (don't break the population).

Canon, low-noise panel, read-only ablations. `scratchpad/bp_gini_isolate.py`.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from bp_gini import gini, top_share

STEPS = int(os.environ.get("G_STEPS", "800"))
ARMS = {
    "canon":        {},
    "no_leveling":  {"enable_leveling": False},
    "no_feast":     {"legit_feast_frac": 0.0},
    "heir_status":  {"material_heir_by_status": True},
    "high_capture": {"material_hide_frac": 0.20, "aggrandizer_frac": 0.30},
    "lvl_half":     {"leveling_strength": 0.40},
    "cap_nolvl":    {"material_hide_frac": 0.20, "aggrandizer_frac": 0.30, "enable_leveling": False},
    "cap_lvlhalf":  {"material_hide_frac": 0.20, "aggrandizer_frac": 0.30, "leveling_strength": 0.40},
    # the REAL concentration knob (canon material_capture_frac = 0.0 = dead): aggrandizers' claim on the pool
    "capfrac_25":   {"material_capture_frac": 0.25},
    "capfrac_50":   {"material_capture_frac": 0.50},
    "capfrac_75":   {"material_capture_frac": 0.75},
    "cap75_nolvl":  {"material_capture_frac": 0.75, "enable_leveling": False},
    "max_stack":    {"material_capture_frac": 0.75, "enable_leveling": False,
                     "material_heir_by_status": True, "legit_feast_frac": 0.0},
}


def run_one(clim, world_seed, agent_seed, overrides):
    canon = dict(runconfig.load()["DemographyConfig"])
    canon.update(overrides)
    w = build(canon, world_seed, agent_seed, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    pop = w.agent_list
    mat = [getattr(a, "material", 0.0) for a in pop]
    cred = [getattr(a, "cred", 1.0) for a in pop]
    aggr = [getattr(a, "aggrandizer", 0.0) for a in pop]
    return dict(mat_gini=gini(mat), top10=top_share(mat),
                corr=float(np.corrcoef(cred, mat)[0, 1]) if np.std(mat) > 0 else float("nan"),
                corr_aggr=float(np.corrcoef(aggr, mat)[0, 1]) if (np.std(mat) > 0 and np.std(aggr) > 0) else float("nan"),
                cred_gini=gini(cred), pop=len(pop))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    biomes = os.environ.get("G_BIOMES", "temperate").split(",")
    worlds = [int(x) for x in os.environ.get("G_WORLDS", "0,1,2").split(",")]
    arms = os.environ.get("G_ARMS", ",".join(ARMS)).split(",")
    print(f"MATERIAL-GINI ISOLATION | canon vs ablations | {STEPS} steps | worlds {worlds} | anchor 0.36", flush=True)
    for clim in biomes:
        print(f"  --- {clim} ---")
        base = {}
        for arm in arms:
            rows = [run_one(clim, ws, 0, ARMS[arm]) for ws in worlds]
            mg, mge = ms([r["mat_gini"] for r in rows])
            cr, cre = ms([r["corr"] for r in rows])
            ca, _ = ms([r["corr_aggr"] for r in rows])
            cg, _ = ms([r["cred_gini"] for r in rows])
            pp, _ = ms([r["pop"] for r in rows])
            t10, _ = ms([r["top10"] for r in rows])
            if arm == "canon":
                base = dict(mg=mg, cr=cr)
            dmg = mg - base.get("mg", mg)
            print(f"    {arm:12s} mat_gini {mg:.3f}+/-{mge:.3f} (delta {dmg:+.3f})  corr(cred) {cr:+.2f}  "
                  f"corr(aggr) {ca:+.2f}  top10 {t10:.2f}  cred_gini {cg:.2f}  pop {pp:.0f}", flush=True)


if __name__ == "__main__":
    main()
