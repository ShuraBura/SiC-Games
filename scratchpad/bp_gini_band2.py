"""R-106 Addendum 86: land material Gini at BHM 0.36 with BOTH tolerance bands, the FEAST KEPT ON.

Probe 1 (bp_gini_band) showed the leveling band alone saturates ~0.24 with the feast on — the feast is the second
ceiling. This probe adds the feast band (feast_tolerance) and keeps legit_feast_frac at CANON 0.25 (the legitimacy
channel stays live) to find the joint (leveling_tolerance, feast_tolerance) that lands 0.36 with guardrails intact.

Concentrators ON in every arm (capture>0, heir_by_status). Low-noise 3-world temperate panel, life table 400-800.
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

_CONC = {"material_capture_frac": CAPFRAC, "material_heir_by_status": True}  # concentrators on, feast stays canon 0.25


def _arm(lt, ft):
    d = dict(_CONC)
    d["leveling_strength"] = 0.79           # canon Boehm
    d["leveling_tolerance"] = lt
    d["feast_tolerance"] = ft
    return d


ARMS = {
    "canon": {},
    # feast band only (leveling at canon tol 0)
    "lt0_ft0.5": _arm(0.0, 0.5),
    "lt0_ft1.0": _arm(0.0, 1.0),
    "lt0_ft2.0": _arm(0.0, 2.0),
    "lt0_ft4.0": _arm(0.0, 4.0),
    # both bands
    "lt1_ft1.0": _arm(1.0, 1.0),
    "lt1_ft2.0": _arm(1.0, 2.0),
    "lt2_ft2.0": _arm(2.0, 2.0),
    "lt1_ft3.0": _arm(1.0, 3.0),
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
    cred = [getattr(a, "cred", 1.0) for a in pop]
    # corr(cred, material) — the Addendum-82 coupling the arc is trying to restore
    cc = float(np.corrcoef(cred, mat)[0, 1]) if len(pop) > 2 and np.std(mat) > 0 else float("nan")
    return dict(mat_gini=gini(mat), e0=lt["e0"], frac_child=dm["frac_child"], cred_gini=gini(cred),
                corr_cm=cc, pct_strat=n_strat / max(len(band_ids), 1), pop=len(pop))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    arms = os.environ.get("C_ARMS", ",".join(ARMS)).split(",")
    print(f"TIER-10 JOINT BAND (feast ON 0.25) | {clim} | capfrac {CAPFRAC} + heir_by_status | {STEPS} steps | "
          f"worlds {worlds} | TARGET material Gini 0.36", flush=True)
    print(f"  guardrails: e0 [21-37], frac_child [0.287-0.454], pct_strat (tier-11), pop", flush=True)
    for arm in arms:
        rows = [run_one(clim, ws, ARMS[arm]) for ws in worlds]
        mg, mge = ms([r["mat_gini"] for r in rows])
        e0, _ = ms([r["e0"] for r in rows])
        fc, _ = ms([r["frac_child"] for r in rows])
        cg, _ = ms([r["cred_gini"] for r in rows])
        co, _ = ms([r["corr_cm"] for r in rows])
        ps, _ = ms([r["pct_strat"] for r in rows])
        pp, _ = ms([r["pop"] for r in rows])
        hit = "  <== ~0.36" if abs(mg - 0.36) <= 0.03 else ""
        print(f"  {arm:9s} mat_gini {mg:.3f}+/-{mge:.3f}{hit}  | e0 {e0:.1f}  frac_child {fc:.2f}  "
              f"cred_gini {cg:.2f}  corr(cred,mat) {co:+.2f}  pct_strat {ps:.0%}  pop {pp:.0f}", flush=True)


if __name__ == "__main__":
    main()
