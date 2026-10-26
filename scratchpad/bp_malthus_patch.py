"""R-106 Add.105 part 9 — IS THE SITE-COUNT INVARIANCE A HARNESS ARTIFACT?

Pass 2 found site count pinned at 21-27 across a THREEFOLD population range, and I called it the key clue. But
the probe world's food lives entirely inside the capacity patch: `NPPCapacityField(patch=(20,20,24))` = a 24x24
box, and the measurement confirms it — 543 food-bearing cells out of 9449 land cells (5.7%), against 3861 cells
that clear `settle_persist_threshold`. With `settle_radius = 2` a village window covers 25 cells, so ~23 village
windows TILE THE WHOLE PATCH. 576/25 = 23. Measured: 21-27.

So the "invariance" may be pure geometry: the patch is full of villages and there is nowhere else to put one.
The canonical campaign uses patch 40 (1600 cells, ~2.8x the area), so this would not transfer — Add.101's rule
(comparative results transfer between harnesses; spatial limits do not).

THE TEST. Vary ONLY the patch size and see whether site count scales with AREA:
  sites ~ area        => patch saturation, a harness artifact. In a larger world the population keeps founding
                         villages, and the Malthusian expansion is NOT blocked the way pass 2 suggested.
  sites ~ constant    => a real model constraint on how many villages can exist, worth chasing.

Also reported as a fraction of each world's OWN carrying capacity, so the arms are comparable despite different
absolute food.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "1200"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1").split(",")]
PATCHES = [int(x) for x in os.environ.get("C_PATCHES", "16,24,40").split(",")]
N = 100
BURN = 75000.0

ARMS = {"canon": {}, "radius 1": {"settle_radius": 1}}


def run_one(patch, ov, ws):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, patch=patch, clim="temperate", terr="coastal")
    tf = w._harvest_field
    land = [(x, y) for y in range(N) for x in range(N) if w._fields.isWater[y, x] == 0]
    food = [c for c in land if tf.level(c[0], c[1]) > 0]
    cap = sum(tf.level(c[0], c[1]) for c in food) / BURN
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    pop = w.agent_list
    cells = {a.pos for a in pop}
    grp = {}
    for a in pop:
        s = w._nearest_settlement(a.pos)
        if s is not None:
            grp[s] = grp.get(s, 0) + 1
    lt = w.life_table()
    return dict(n_food=len(food), cap=cap, pop=len(pop), pct=len(pop) / cap,
                sites=len(w._settlement_sites), land_use=len(cells) / max(1, len(food)),
                vill_med=st.median(grp.values()) if grp else float("nan"),
                e0=lt["e0"], starv=lt["starv_share"])


def main():
    print(f"PATCH-SIZE TEST | temperate | {STEPS} steps | seeds {SEEDS}")
    print("does the number of villages scale with the AREA of food-bearing land?\n")
    for arm, ov in ARMS.items():
        print(f"--- {arm}")
        print(f"{'patch':>7s}{'food cells':>12s}{'capacity':>11s}{'pop':>9s}{'% cap':>8s}"
              f"{'sites':>7s}{'cells/site':>12s}{'land use':>10s}{'vill med':>10s}{'e0':>7s}")
        for p in PATCHES:
            rows = [r for r in (run_one(p, ov, s) for s in SEEDS) if r]
            if not rows:
                print(f"{p:>7d}   (all seeds died)")
                continue
            def m(k):
                return st.mean([r[k] for r in rows if r[k] == r[k]])
            print(f"{p:>7d}{m('n_food'):>12.0f}{m('cap'):>11,.0f}{m('pop'):>9,.0f}"
                  f"{m('pct')*100:>7.1f}%{m('sites'):>7.0f}{m('n_food')/max(m('sites'),1):>12.1f}"
                  f"{m('land_use'):>10.3f}{m('vill_med'):>10.0f}{m('e0'):>7.1f}")
        print()


if __name__ == "__main__":
    main()
