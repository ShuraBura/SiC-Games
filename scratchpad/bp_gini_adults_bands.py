"""R-106 Add.92 — isolate the lever: widen the tolerance BANDS at the GROUNDED concentrators (cap 0.15, ag 0.15,
heir on) and measure adults material Gini + e0, both biomes. The concentrator sweep showed capture plateaus ~0.24;
the bands are the lever. This asks: do wider bands ALONE (grounded concentrators) reach adults-0.36, at what e0 cost,
and does savanna follow temperate? Low-noise 3-world panel."""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = 800
DFROM = 400
BANDS = [(1.0, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 4.0)]   # (leveling_tolerance, feast_tolerance); (1.0,1.5)=adopted


def run_one(clim, ws, lt, ft):
    canon = dict(runconfig.load()["DemographyConfig"])
    canon.update({"leveling_tolerance": lt, "feast_tolerance": ft})   # grounded concentrators kept at canon
    w = build(canon, ws, 0, clim=clim)
    snap = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == DFROM:
            snap = w.raw_demographic_counters()
    dg = w.demography()
    lt_ = w.life_table(since=snap) if snap else w.life_table()
    bs = getattr(w, "_band_society", {}) or {}
    bids = {a._group.band_id for a in w.agent_list}
    ps = sum(1 for b in bids if bs.get(b, "egalitarian_forager") != "egalitarian_forager") / max(len(bids), 1)
    return dg.get("material_gini_adults", float("nan")), dg.get("material_gini", float("nan")), lt_["e0"], \
        dg.get("frac_child", float("nan")), ps, len(w.agent_list)


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1)/np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


for clim in ("temperate", "savanna"):
    print(f"== {clim.upper()} | grounded cap 0.15 / ag 0.15 + heir; widen bands | TARGET adults 0.36 | guardrail e0<=37 ==",
          flush=True)
    for lt, ft in BANDS:
        rows = [run_one(clim, ws, lt, ft) for ws in (0, 1, 2)]
        gad, gade = ms([r[0] for r in rows]); gall, _ = ms([r[1] for r in rows])
        e0, e0e = ms([r[2] for r in rows]); fc, _ = ms([r[3] for r in rows])
        ps, _ = ms([r[4] for r in rows]); pp, _ = ms([r[5] for r in rows])
        hit = "  <== ~0.36" if abs(gad - 0.36) <= 0.03 else ""
        note = "  !!e0>37" if e0 > 37.0 else ""
        print(f"  lt{lt}/ft{ft:<4} adults {gad:.3f}+/-{gade:.3f}{hit}  (all-ages {gall:.3f}) | e0 {e0:.1f}{note}  "
              f"frac_child {fc:.2f}  pct_strat {ps:.0%}  pop {pp:.0f}", flush=True)
