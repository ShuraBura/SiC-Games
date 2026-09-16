"""R-106 Addendum 87: re-calibrate the two tolerance bands around a GROUNDED capture fraction.

Add.86 landed at material_capture_frac=0.5, an unanchored [DESIGN] value. That is aggrandizer CONFISCATION of half
the group's durable output, not Big-Man skimming. The one documented tribal surplus-extraction rate the project
uses is the gumsa "a thigh from every animal" ~0.10-0.15 (= lineage_tribute_frac 0.15). So this re-calibrates the
bands around material_capture_frac = C_CAPFRAC (default 0.15). Weaker capture => wider bands may be needed to reach
BHM 0.36. Grid over (leveling_tolerance, feast_tolerance), both biomes, low-noise 3-world panel, feast ON (0.25).
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
CAPFRAC = float(os.environ.get("C_CAPFRAC", "0.15"))
LTS = [float(x) for x in os.environ.get("C_LTS", "1.0,1.5,2.0").split(",")]
FTS = [float(x) for x in os.environ.get("C_FTS", "1.5,2.0,3.0").split(",")]


def _arm(lt, ft):
    return {"material_capture_frac": CAPFRAC, "material_heir_by_status": True,
            "leveling_strength": 0.79, "leveling_tolerance": lt, "feast_tolerance": ft}


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
    cc = float(np.corrcoef(cred, mat)[0, 1]) if len(pop) > 2 and np.std(mat) > 0 else float("nan")
    return dict(mat_gini=gini(mat), e0=lt["e0"], frac_child=dm["frac_child"], cred_gini=gini(cred),
                corr_cm=cc, pct_strat=n_strat / max(len(band_ids), 1), pop=len(pop))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    biomes = os.environ.get("C_BIOMES", "temperate,savanna").split(",")
    for clim in biomes:
        print(f"== {clim.upper()} | GROUNDED capfrac {CAPFRAC} + heir, feast ON 0.25 | {STEPS} steps | "
              f"worlds {worlds} | TARGET 0.36 ==", flush=True)
        for lt in LTS:
            for ft in FTS:
                rows = [run_one(clim, ws, _arm(lt, ft)) for ws in worlds]
                mg, mge = ms([r["mat_gini"] for r in rows])
                e0, _ = ms([r["e0"] for r in rows])
                fc, _ = ms([r["frac_child"] for r in rows])
                cg, _ = ms([r["cred_gini"] for r in rows])
                co, _ = ms([r["corr_cm"] for r in rows])
                ps, _ = ms([r["pct_strat"] for r in rows])
                pp, _ = ms([r["pop"] for r in rows])
                hit = "  <== ~0.36" if abs(mg - 0.36) <= 0.03 else ""
                print(f"  lt{lt:.1f}/ft{ft:.1f}  mat_gini {mg:.3f}+/-{mge:.3f}{hit}  | e0 {e0:.1f}  "
                      f"frac_child {fc:.2f}  cred_gini {cg:.2f}  corr(cred,mat) {co:+.2f}  pct_strat {ps:.0%}  "
                      f"pop {pp:.0f}", flush=True)


if __name__ == "__main__":
    main()
