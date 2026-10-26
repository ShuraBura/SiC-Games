"""R-106 Addendum 105 — WHY does hunger dispersal crash e0? Diagnose before building.

The packing paradox is a RETENTION failure (per the enable_hunger_dispersal docstring): 98% of the hungriest decile
are pinned settlers and 99% would eat >1.3x better one cell away. Add.78 released the pin and e0 CRASHED. Before
building anything we need to know WHAT breaks, because the obvious fix was already tried and failed.

Candidate crash mechanisms:
  (a) VILLAGE DISSOLUTION — released agents abandon sites, so the settlement pooling / agglomeration bonus is lost
      and everyone eats worse despite each individual step being locally better.
  (b) CHURN — agents oscillate, never re-settle, and pay the movement/instability cost forever.
  (c) BUFFER LOSS — dispersal breaks food sharing among co-residents, raising variance even if the mean is fine.

These predict different signatures, so measure them: settlement count and residency, occupancy spread, reserve mean
AND spread, and the starvation profile. COMPARATIVE test (both arms share the harness) => probe harness is
legitimate per Add.101. 5 seeds per arm, as the supervisor asked: nothing believed from one run.
"""
import os
import sys
import statistics as st
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
DFROM = int(os.environ.get("C_DFROM", "400"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1,2,3,4").split(",")]

ARMS = {
    "canon (pinned)":          {},
    "hunger_dispersal ON":     {"enable_hunger_dispersal": True},
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
    if not pop:
        return None
    lt = w.life_table(since=snap) if snap else w.life_table()
    cells = {}
    for a in pop:
        cells[a.pos] = cells.get(a.pos, 0) + 1
    sites = set(getattr(w, "_settlement_sites", ()))
    on_site = sum(1 for a in pop if a.pos in sites)

    def fill(a):
        return getattr(a, "wealth", 0.0) / max(w._reserve_full, 1e-9)
    kids = [a for a in pop if a.is_juvenile()]
    adults = [a for a in pop if not a.is_juvenile()]
    res = [fill(a) for a in pop]
    # PERSON-WEIGHTED co-resident count: the size of the sharing pool AS EXPERIENCED. The mean over cells
    # would be dominated by the many near-empty cells dispersal creates, which is the quantity we are
    # testing, so it must be weighted by person (the hidden-denominator rule).
    pool = st.mean([cells[a.pos] for a in pop])
    # THE LOAD-BEARING MEASUREMENT. Band provisioning groups by `_nearest_settlement(pos) or pos`. An agent
    # inside settle_radius keeps the whole village as its food-sharing group. An agent OUTSIDE falls back to
    # its own cell, so its juveniles lose every alloparental donor. Measure the share that falls out, and the
    # size of the sharing group each person actually experiences.
    bk = [(w._nearest_settlement(a.pos) or a.pos) for a in pop]
    gsz = {}
    for k in bk:
        gsz[k] = gsz.get(k, 0) + 1
    orphaned = sum(1 for a, k in zip(pop, bk) if w._nearest_settlement(a.pos) is None)
    kid_orph = (sum(1 for a in kids if w._nearest_settlement(a.pos) is None) / len(kids)) if kids else float("nan")
    mb = lt["m_by_band"]
    return dict(
        e0=lt["e0"], e15=lt["e15"], surv15=lt["surv_to_15"], pop=len(pop),
        occupied=len(cells), max_cell=max(cells.values()), mean_occ=len(pop) / len(cells),
        n_sites=len(sites), frac_on_site=on_site / len(pop), pool=pool,
        frac_out=orphaned / len(pop), kid_out=kid_orph,
        share_grp=st.mean([gsz[k] for k in bk]),
        reserve_mean=st.mean(res), reserve_p10=float(np.percentile(res, 10)),
        kid_fill=st.mean([fill(a) for a in kids]) if kids else float("nan"),
        adult_fill=st.mean([fill(a) for a in adults]) if adults else float("nan"),
        m_0_1=mb.get("0_1", float("nan")), m_1_5=mb.get("1_5", float("nan")),
        m_5_15=mb.get("5_15", float("nan")), m_15_30=mb.get("15_30", float("nan")),
        m_30_45=mb.get("30_45", float("nan")),
        starv_share=lt["starv_share"])


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    print(f"MALTHUS DIAGNOSIS | {clim} | {STEPS} steps | seeds {SEEDS} (n={len(SEEDS)} per arm)")
    print("what breaks when the residence pin is released?\n")
    keys = [("e0", "e0 (yr)", "{:.1f}"), ("e15", "e15 (yr remaining)", "{:.1f}"),
            ("surv15", "survival to 15", "{:.2f}"),
            ("pop", "pop", "{:.0f}"),
            ("__", "-- DOES IT UNPACK? --", ""),
            ("occupied", "occupied cells", "{:.0f}"),
            ("mean_occ", "people per occupied cell", "{:.1f}"),
            ("max_cell", "largest cell", "{:.0f}"),
            ("n_sites", "settlement sites", "{:.1f}"),
            ("frac_on_site", "frac of pop ON a site cell", "{:.2f}"),
            ("pool", "co-residents, person-weighted", "{:.1f}"),
            ("__1b", "-- IS THE SHARING GROUP LOST? --", ""),
            ("share_grp", "food-sharing group, experienced", "{:.1f}"),
            ("frac_out", "frac OUTSIDE any catchment", "{:.2f}"),
            ("kid_out", "frac of JUVENILES outside", "{:.2f}"),
            ("__2", "-- IS THERE MORE FOOD? --", ""),
            ("reserve_mean", "reserve fill, mean", "{:.2f}"),
            ("reserve_p10", "reserve fill, p10", "{:.2f}"),
            ("adult_fill", "reserve fill, ADULTS", "{:.2f}"),
            ("kid_fill", "reserve fill, CHILDREN <15", "{:.2f}"),
            ("__3", "-- WHO DIES? (hazard /py) --", ""),
            ("m_0_1", "m 0-1", "{:.3f}"), ("m_1_5", "m 1-5", "{:.3f}"),
            ("m_5_15", "m 5-15", "{:.3f}"), ("m_15_30", "m 15-30", "{:.3f}"),
            ("m_30_45", "m 30-45", "{:.3f}"),
            ("starv_share", "starvation share of deaths", "{:.2f}")]
    res = {}
    for arm, ov in ARMS.items():
        rows = [r for r in (run_one(clim, s, ov) for s in SEEDS) if r]
        res[arm] = rows
    print(f"{'metric':34s}" + "".join(f"{a:>26s}" for a in ARMS))
    print("-" * 90)
    for k, label, fmt in keys:
        if not fmt:
            print(f"\n{label}")
            continue
        cells = ""
        for arm in ARMS:
            m, e = ms([r[k] for r in res[arm]])
            cells += f"{fmt.format(m) + ' +/- ' + fmt.format(e):>26s}"
        print(f"{label:34s}{cells}")


if __name__ == "__main__":
    main()
