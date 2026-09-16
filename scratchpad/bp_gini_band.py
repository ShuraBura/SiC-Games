"""R-106 Addendum 86: does the leveling TOLERANCE BAND lift material Gini toward BHM 0.36?

Addendum 84 found the coalition + feast pin the Gini near the mean for ANY nonzero strength (a bang-bang shape).
The band (leveling_tolerance) lets a co-resident hold up to (1+tol)*mean before the sanction fires, so the
equilibrium should settle at the tolerated band, not the mean. THIS PROBE tests two things:
  (1) with the FEAST STILL ON (canon 0.25), does the band alone move the Gini, or does the feast pin it?
  (2) with the feast off, how far does the band carry it?
Concentrators ON in every non-canon arm (capture>0, heir_by_status) so the band has something to hold.

Low-noise panel: fix the world seed, vary nothing but the knobs; 3 temperate worlds, period life table 400-800.
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

_CONC = {"material_capture_frac": CAPFRAC, "material_heir_by_status": True}  # the concentrators, on in every arm


def _arm(strength, tol, feast=None):
    d = dict(_CONC)
    d["leveling_strength"] = strength
    d["leveling_tolerance"] = tol
    if feast is not None:
        d["legit_feast_frac"] = feast
    return d


ARMS = {
    "canon": {},                                   # bit-exact reference (no concentrators, tol default 0.0)
    # FEAST ON (canon 0.25), leveling_strength canon 0.79, sweep the band
    "s79_t0.0": _arm(0.79, 0.0),
    "s79_t0.5": _arm(0.79, 0.5),
    "s79_t1.0": _arm(0.79, 1.0),
    "s79_t2.0": _arm(0.79, 2.0),
    "s79_t4.0": _arm(0.79, 4.0),
    # FEAST OFF, same band sweep — isolates whether the feast is the ceiling
    "nf_t0.0": _arm(0.79, 0.0, feast=0.0),
    "nf_t1.0": _arm(0.79, 1.0, feast=0.0),
    "nf_t2.0": _arm(0.79, 2.0, feast=0.0),
    "nf_t4.0": _arm(0.79, 4.0, feast=0.0),
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
    print(f"TIER-10 BAND SWEEP | {clim} | capfrac {CAPFRAC} + heir_by_status | {STEPS} steps | worlds {worlds} | "
          f"TARGET material Gini 0.36", flush=True)
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
