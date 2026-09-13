"""R-106 tier-10 joint calibration: land material Gini at BHM 0.36 with the grounded knobs, keeping leveling ON.

Fix the two dead/mis-set concentrators (material_capture_frac>0, material_heir_by_status=True) and dial
leveling_strength down from 0.79 to find where material Gini crosses 0.36 - while watching the downstream tiers
(e0, frac_child - lower tiers; pct non-egalitarian bands - tier 11) and the population, so the fix does not break
what is below it. Grounded: capture (Hayden), status inheritance (BHM/Shennan), leveling (Boehm) all stay ON,
only re-calibrated.

Canon, low-noise panel (3 worlds temperate), period life table 400-800.
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
CAPFRAC = float(os.environ.get("C_CAPFRAC", "0.50"))

ARMS = {  # material_heir_by_status=True + material_capture_frac=CAPFRAC in all; dial leveling
    "canon":     {},
    "lvl_0.79":  {"material_capture_frac": CAPFRAC, "material_heir_by_status": True, "leveling_strength": 0.79},
    "lvl_0.40":  {"material_capture_frac": CAPFRAC, "material_heir_by_status": True, "leveling_strength": 0.40},
    "lvl_0.20":  {"material_capture_frac": CAPFRAC, "material_heir_by_status": True, "leveling_strength": 0.20},
    "lvl_0.00":  {"material_capture_frac": CAPFRAC, "material_heir_by_status": True, "leveling_strength": 0.00},
    "lvl_off":   {"material_capture_frac": CAPFRAC, "material_heir_by_status": True, "enable_leveling": False},
    "lvl_off_nofeast": {"material_capture_frac": CAPFRAC, "material_heir_by_status": True,
                        "enable_leveling": False, "legit_feast_frac": 0.0},
    # FEAST DIAL (the binding leveler) at a reduced-but-nonzero grounded leveling — find the 0.36 landing
    "feast_0.15": {"material_capture_frac": CAPFRAC, "material_heir_by_status": True,
                   "leveling_strength": 0.20, "legit_feast_frac": 0.15},
    "feast_0.10": {"material_capture_frac": CAPFRAC, "material_heir_by_status": True,
                   "leveling_strength": 0.20, "legit_feast_frac": 0.10},
    "feast_0.05": {"material_capture_frac": CAPFRAC, "material_heir_by_status": True,
                   "leveling_strength": 0.20, "legit_feast_frac": 0.05},
}


def run_one(clim, ws, overrides):
    canon = dict(runconfig.load()["DemographyConfig"])
    canon.update(overrides)
    w = build(canon, ws, 0, clim=clim)
    snap = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == DFROM:
            snap = w.raw_demographic_counters()
    pop = w.agent_list
    mat = [getattr(a, "material", 0.0) for a in pop]
    lt = w.life_table(since=snap) if snap else w.life_table()
    dm = w.demography()
    bs = getattr(w, "_band_society", {}) or {}
    band_ids = {a._group.band_id for a in pop}
    n_strat = sum(1 for b in band_ids if bs.get(b, "egalitarian_forager") != "egalitarian_forager")
    return dict(mat_gini=gini(mat), e0=lt["e0"], frac_child=dm["frac_child"],
                cred_gini=gini([getattr(a, "cred", 1.0) for a in pop]),
                pct_strat=n_strat / max(len(band_ids), 1), pop=len(pop))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    arms = os.environ.get("C_ARMS", ",".join(ARMS)).split(",")
    print(f"TIER-10 JOINT CALIBRATION | {clim} | capfrac {CAPFRAC} + heir_by_status, dial leveling | "
          f"{STEPS} steps | worlds {worlds} | TARGET material Gini 0.36", flush=True)
    print(f"  guardrails: e0 [21-37], frac_child [0.287-0.454], pct_strat (tier-11), pop", flush=True)
    for arm in arms:
        rows = [run_one(clim, ws, ARMS[arm]) for ws in worlds]
        mg, mge = ms([r["mat_gini"] for r in rows])
        e0, _ = ms([r["e0"] for r in rows])
        fc, _ = ms([r["frac_child"] for r in rows])
        cg, _ = ms([r["cred_gini"] for r in rows])
        ps, _ = ms([r["pct_strat"] for r in rows])
        pp, _ = ms([r["pop"] for r in rows])
        hit = "  <== ~0.36" if abs(mg - 0.36) <= 0.03 else ""
        print(f"  {arm:9s} mat_gini {mg:.3f}+/-{mge:.3f}{hit}  | e0 {e0:.1f}  frac_child {fc:.2f}  "
              f"cred_gini {cg:.2f}  pct_strat {ps:.0%}  pop {pp:.0f}", flush=True)


if __name__ == "__main__":
    main()
