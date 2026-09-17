"""R-106 Add.92 — #14 re-calibration against the CORRECTED marker (material_gini_adults, Add.90).

Adopted canon gives adults material Gini ~0.22 temp / 0.16 sav vs BHM 0.36. Question: does 0.36 have a GROUNDED
landing, or is ~0.22 the grounded ceiling (like the packing paradox capped e0)? Sweep the direct adult-concentration
levers on top of the adopted stack (heir_by_status=True, bands lt1.0/ft1.5):
  - material_capture_frac: the aggrandizer skim (GROUNDED 0.15 = gumsa 'thigh'; >0.3 drifts to confiscation)
  - aggrandizer_frac: the minority who skim (canon 0.15; fewer => more concentrated)
Watch guardrails (e0, frac_child, tier-11 pct_strat, pop) and the all-ages Gini. Low-noise 3-world panel, both biomes.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from bp_gini import gini

STEPS = int(os.environ.get("C_STEPS", "800"))
DFROM = int(os.environ.get("C_DFROM", "400"))
ADULT_MO = 15.0 * 12.0

# adopted stack is already in canon; arms only perturb the concentrators
ARMS = {
    "adopted(cap.15/ag.15)": {},
    "cap0.30":               {"material_capture_frac": 0.30},
    "cap0.50":               {"material_capture_frac": 0.50},
    "cap0.75":               {"material_capture_frac": 0.75},
    "cap.15/ag.05":          {"aggrandizer_frac": 0.05},
    "cap0.30/ag.05":         {"material_capture_frac": 0.30, "aggrandizer_frac": 0.05},
    "cap0.50/ag.05":         {"material_capture_frac": 0.50, "aggrandizer_frac": 0.05},
    "cap0.30/ag.05/lt2/ft3": {"material_capture_frac": 0.30, "aggrandizer_frac": 0.05,
                              "leveling_tolerance": 2.0, "feast_tolerance": 3.0},
}


def run_one(clim, ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, clim=clim)
    snap = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == DFROM:
            snap = w.raw_demographic_counters()
    pop = w.agent_list
    dg = w.demography()
    lt = w.life_table(since=snap) if snap else w.life_table()
    bs = getattr(w, "_band_society", {}) or {}
    bids = {a._group.band_id for a in pop}
    ps = sum(1 for b in bids if bs.get(b, "egalitarian_forager") != "egalitarian_forager") / max(len(bids), 1)
    return dict(gad=dg.get("material_gini_adults", float("nan")), gall=dg.get("material_gini", float("nan")),
                e0=lt["e0"], fc=dg.get("frac_child", float("nan")), ps=ps, pop=len(pop))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1)/np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    biomes = os.environ.get("C_BIOMES", "temperate,savanna").split(",")
    arms = os.environ.get("C_ARMS", ",".join(ARMS)).split(",")
    print(f"#14 ADULTS-GINI RE-CALIBRATION | {STEPS} steps | worlds {worlds} | TARGET material_gini_adults 0.36 | "
          f"grounded capfrac = 0.15", flush=True)
    for clim in biomes:
        print(f"== {clim.upper()} ==", flush=True)
        for arm in arms:
            rows = [run_one(clim, ws, ARMS[arm]) for ws in worlds]
            gad, gade = ms([r["gad"] for r in rows])
            gall, _ = ms([r["gall"] for r in rows])
            e0, _ = ms([r["e0"] for r in rows]); fc, _ = ms([r["fc"] for r in rows])
            ps, _ = ms([r["ps"] for r in rows]); pp, _ = ms([r["pop"] for r in rows])
            hit = "  <== ~0.36" if abs(gad - 0.36) <= 0.03 else ""
            print(f"  {arm:24s} adults_gini {gad:.3f}+/-{gade:.3f}{hit}  (all-ages {gall:.3f}) | "
                  f"e0 {e0:.1f}  frac_child {fc:.2f}  pct_strat {ps:.0%}  pop {pp:.0f}", flush=True)


if __name__ == "__main__":
    main()
