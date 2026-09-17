"""R-106 Add.92 — fine-tune the band landing for adults-0.36 in BOTH biomes, and VALIDATE tier-11 together.

Grounded concentrators (cap 0.15 / ag 0.15 / heir). Sweep the band widths in the landing zone and report, per arm:
  - material_gini_adults (target 0.36 both biomes)  + all-ages (deprecated, for reference)
  - TIER-11: pct_strat (fraction of non-egalitarian bands), cred_gini (status inequality anchor 0.36)
  - corr(cred, material) (the Add.82 status->material coupling)
  - guardrails: e0, frac_child, pop
Low-noise 3-world panel, both biomes.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from bp_gini import gini

STEPS = 800
DFROM = 400
ADULT_MO = 15.0 * 12.0
BANDS = [(2.5, 3.5), (3.0, 3.5), (3.0, 4.0), (2.5, 4.0)]


def run_one(clim, ws, lt, ft):
    canon = dict(runconfig.load()["DemographyConfig"])
    canon.update({"leveling_tolerance": lt, "feast_tolerance": ft})
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
    lt_ = w.life_table(since=snap) if snap else w.life_table()
    mat = [getattr(a, "material", 0.0) for a in pop]
    cred = [getattr(a, "cred", 1.0) for a in pop]
    cc = float(np.corrcoef(cred, mat)[0, 1]) if len(pop) > 2 and np.std(mat) > 0 else float("nan")
    bs = getattr(w, "_band_society", {}) or {}
    bids = {a._group.band_id for a in pop}
    ps = sum(1 for b in bids if bs.get(b, "egalitarian_forager") != "egalitarian_forager") / max(len(bids), 1)
    return dict(gad=dg.get("material_gini_adults", float("nan")), gall=dg.get("material_gini", float("nan")),
                cg=gini(cred), cc=cc, ps=ps, e0=lt_["e0"], fc=dg.get("frac_child", float("nan")), pop=len(pop))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1)/np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


for clim in ("temperate", "savanna"):
    print(f"== {clim.upper()} | grounded cap0.15/ag0.15/heir; fine-tune bands | TARGET adults 0.36 + tier-11 intact ==",
          flush=True)
    for lt, ft in BANDS:
        rows = [run_one(clim, ws, lt, ft) for ws in (0, 1, 2)]
        gad, gade = ms([r["gad"] for r in rows]); gall, _ = ms([r["gall"] for r in rows])
        cg, _ = ms([r["cg"] for r in rows]); cc, _ = ms([r["cc"] for r in rows])
        ps, _ = ms([r["ps"] for r in rows]); e0, _ = ms([r["e0"] for r in rows])
        fc, _ = ms([r["fc"] for r in rows]); pp, _ = ms([r["pop"] for r in rows])
        hit = "  <==0.36" if abs(gad - 0.36) <= 0.03 else ""
        print(f"  lt{lt}/ft{ft}  adults {gad:.3f}+/-{gade:.3f}{hit} (all {gall:.2f}) | cred_gini {cg:.2f} "
              f"corr(cr,mat) {cc:+.2f} pct_strat {ps:.0%} | e0 {e0:.1f} fc {fc:.2f} pop {pp:.0f}", flush=True)
