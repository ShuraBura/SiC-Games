"""R-106 Add.105 part 3 — HOW BIG is the food cliff at the village boundary?

CLAIM UNDER TEST. `_do_harvest` deposits the ENTIRE tier-2 catchment yield of a 9-cell catchment onto the ONE
site cell (phase1_model.py ~1992). A member standing on the site shares (tier-1 of that cell + tier-2 of nine
cells + agglomeration). A member one step away gets tier-1 of its own cell ONLY.

If the cliff is large, the packing is not a behavioural failure — it is the correct response to an economy whose
entire surplus sits at a point, and no movement rule can fix it. If the cliff is small, this reframe is wrong
and the constraint is elsewhere.

Measured per ACTIVE SITE, at the run's own equilibrium:
  tier1_site      tf.level(site)                      what the site cell itself grows
  tier2_site      _settlement_catchment_yield(site)   what the 9-cell catchment adds, deposited at the point
  ring_tier1      mean tf.level over the 24 membership cells that are NOT the site
  cliff           (tier1+tier2) / tier1_of_a_ring_cell  = the per-cell food ratio a leaver gives up
  per_capita_on   (tier1+tier2) / people standing on the site
  per_capita_off  tier1 of the best empty ring cell    = what a leaver would actually eat

The honest comparison is PER CAPITA, not per cell: the site pool is split among many. A leaver trades a small
share of a huge pool for the whole of a small one, so the cliff only bites while the village is small enough
that its per-capita share still beats an empty cell.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1,2").split(",")]
N = 100


def run_one(clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    tf = w._harvest_field
    pop = w.agent_list
    cells = {}
    for a in pop:
        cells[a.pos] = cells.get(a.pos, 0) + 1
    rad = w._demog.settle_radius
    rows = []
    for site in w._settlement_sites:
        sx, sy = site
        t1 = tf.level(sx, sy)
        t2 = w._settlement_catchment_yield(site)
        ring = []
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if dx == 0 and dy == 0:
                    continue
                c = ((sx + dx) % N, (sy + dy) % N)
                if w._fields.isWater[c[1], c[0]] == 0:
                    ring.append((tf.level(c[0], c[1]), c))
        if not ring:
            continue
        n_on = cells.get(site, 0)
        best_off = max(r[0] for r in ring)
        rows.append(dict(
            t1=t1, t2=t2, ring=st.mean(r[0] for r in ring), best_off=best_off,
            cliff=((t1 + t2) / best_off) if best_off > 0 else float("nan"),
            pc_on=((t1 + t2) / n_on) if n_on else float("nan"),
            pc_off=best_off,
            ratio=(((t1 + t2) / n_on) / best_off) if n_on and best_off > 0 else float("nan"),
            n_on=n_on))
    if not rows:
        return None
    def m(k):
        v = [r[k] for r in rows if r[k] == r[k]]
        return st.mean(v) if v else float("nan")
    return {k: m(k) for k in rows[0]} | {"n_sites": len(rows)}


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    print(f"FOOD CLIFF AT THE VILLAGE BOUNDARY | {clim} | {STEPS} steps | seeds {SEEDS}\n")
    rows = [r for r in (run_one(clim, s) for s in SEEDS) if r]
    keys = [("n_sites", "active sites"), ("n_on", "people standing ON the site"),
            ("t1", "tier-1 of the site cell"), ("t2", "tier-2 deposited at the site"),
            ("ring", "tier-1, mean ring cell"), ("best_off", "tier-1, BEST ring cell"),
            ("cliff", "PER-CELL cliff (site pool / best ring)"),
            ("pc_on", "PER-CAPITA on the site"),
            ("pc_off", "PER-CAPITA if you step off (best ring)"),
            ("ratio", "stay/leave per-capita RATIO  (<1 => leaving pays)")]
    for k, label in keys:
        v = [r[k] for r in rows if r[k] == r[k]]
        if not v:
            continue
        mm = st.mean(v)
        se = st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
        print(f"{label:44s}{mm:12.3f} +/- {se:.3f}")


if __name__ == "__main__":
    main()
