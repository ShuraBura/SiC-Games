"""R-106 Add.105 part 2 — is the packing paradox a BUD-GATE deadlock?

DIAGNOSIS UNDER TEST. In canon `enable_bud_hazard` is OFF, so `_maintain_village_budding` uses the LEGACY gate:
a village buds only if `len(village) > village_fission_threshold` (150, rising to ~240 circumscribed). The whole
`drive` term — depletion, mate competition, rivalry, grievance — is computed ONLY in the hazard branch, which
canon never runs. So in canon a village splits when it is BIG, never when it is HUNGRY.

Meanwhile density-dependent fertility (exponent 6, adopted Add.65) stops village growth AS IT NEARS ITS FOOD
CEILING. Add.100 measured the canonical median village at 43-50 — under a third of the trigger.

=> The adopted food brake suppresses the growth that the adopted colonization trigger needs. Villages homeostat
locally at their own 25-cell catchment while the region stays empty. That is the packing paradox, and it is the
SAME defect as Add.104's open montane question (356 eligible sites, 23 founded).

PREDICTIONS, so the test can fail:
  P1  In canon, the share of villages above 150 is ~0, and bud_events is small.
  P2  Villages sit AT their catchment food ceiling (that is the fertility brake biting), not below it.
  P3  Turning the depletion-driven hazard path ON raises site count and land use, and cuts the starvation share.
  P4  CONTROL — just lowering the threshold should also unpack. If it does NOT, the gate is not the constraint
      and this diagnosis is wrong. If it DOES but starves them anyway, the gate is necessary but not sufficient.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
DFROM = int(os.environ.get("C_DFROM", "400"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1,2").split(",")]

ARMS = {
    "canon (size gate 150)":   {},
    "bud_hazard ON (food)":    {"enable_bud_hazard": True},
    "CONTROL thresh 150->50":  {"village_fission_threshold": 50},
}


def run_one(clim, ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, clim=clim)
    snap = None
    buds0 = 0
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        if t == DFROM:
            snap = w.raw_demographic_counters()
            buds0 = w.bud_events
    pop = w.agent_list
    lt = w.life_table(since=snap) if snap else w.life_table()
    vs = w.village_sizes()
    cells = {}
    for a in pop:
        cells[a.pos] = cells.get(a.pos, 0) + 1
    # village size distribution against the gate that decides colonization
    sizes = []
    grp = {}
    for a in pop:
        k = w._nearest_settlement(a.pos)
        if k is not None:
            grp[k] = grp.get(k, 0) + 1
    sizes = sorted(grp.values())
    thr = canon.get("village_fission_threshold", 150)
    # LAND USE MUST BE SCORED AGAINST FOOD-BEARING LAND, not the whole map. The probe map is mostly outside
    # the capacity patch, so a whole-map fraction understates by ~20x and is not the campaign's statistic.
    # Two denominators, both reported: the share of food-bearing CELLS occupied, and the share of total food
    # POTENTIAL that sits under someone. The second is the Malthusian quantity (the campaign's "forage unused").
    tf = w._harvest_field
    W = H = 100
    lev = [[tf.level(x, y) for x in range(W)] for y in range(H)]
    food_cells = [(x, y) for y in range(H) for x in range(W)
                  if w._fields.isWater[y, x] == 0 and lev[y][x] > 0.0]
    tot_food = sum(lev[y][x] for x, y in food_cells)
    used_food = sum(lev[y][x] for (x, y) in cells if (x, y) in set(food_cells))
    return dict(
        e0=lt["e0"], pop=len(pop), starv=lt["starv_share"],
        n_sites=len(getattr(w, "_settlement_sites", ())),
        buds=w.bud_events - buds0,
        occupied=len(cells),
        land_use=len(cells) / max(1, len(food_cells)),
        food_used=(used_food / tot_food) if tot_food > 0 else float("nan"),
        vill_med=(st.median(sizes) if sizes else float("nan")),
        vill_max=(max(sizes) if sizes else float("nan")),
        frac_over=(sum(1 for s in sizes if s > thr) / len(sizes)) if sizes else float("nan"),
        vmax_marker=vs.get("village_max", float("nan")),
        local_dens=len(pop) / len(cells))


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    print(f"BUD-GATE DEADLOCK TEST | {clim} | {STEPS} steps | seeds {SEEDS}")
    print("does a village bud when it is HUNGRY, or only when it is BIG?\n")
    keys = [("pop", "pop", "{:.0f}"), ("e0", "e0 (yr)", "{:.1f}"),
            ("starv", "starvation share of deaths", "{:.2f}"),
            ("__", "-- P1: CAN a village bud? --", ""),
            ("vill_med", "village size, median", "{:.0f}"),
            ("vill_max", "village size, max", "{:.0f}"),
            ("frac_over", "frac of villages OVER the gate", "{:.3f}"),
            ("buds", "bud events (2nd half)", "{:.1f}"),
            ("__2", "-- P3: does the land fill? --", ""),
            ("n_sites", "settlement sites", "{:.1f}"),
            ("occupied", "occupied cells", "{:.0f}"),
            ("land_use", "frac of FOOD-BEARING cells used", "{:.3f}"),
            ("food_used", "frac of total FOOD under someone", "{:.3f}"),
            ("local_dens", "people per occupied cell", "{:.1f}")]
    res = {a: [r for r in (run_one(clim, s, ov) for s in SEEDS) if r] for a, ov in ARMS.items()}
    print(f"{'metric':34s}" + "".join(f"{a:>26s}" for a in ARMS))
    print("-" * 112)
    for k, label, fmt in keys:
        if not fmt:
            print(f"\n{label}")
            continue
        line = ""
        for arm in ARMS:
            m, e = ms([r[k] for r in res[arm]])
            line += f"{fmt.format(m) + ' +/- ' + fmt.format(e):>26s}"
        print(f"{label:34s}{line}")


if __name__ == "__main__":
    main()
