"""R-106 Add.105 part 10 — ARE VILLAGES BEING FOUNDED AND THEN DYING? (settlement churn)

Every other explanation for the ~28-village saturation is now dead:
  - patch area        REFUTED: 1549 food cells at patch 40, room for ~62 villages, only 28 exist
  - founding gate     REFUTED: 564 founding-eligible FOOD-BEARING cells at patch 40 vs 28 sites
  - site threshold    REFUTED: `settle_persist_threshold` clears 2306 cells
  - bud spacing       not binding: `_bud_sep` clamps at 3 cells, which would allow ~169 sites at patch 40

What remains is SURVIVAL. Canon fires ~122 bud events per 400 steps while site count stays flat, so villages
must be forming and dissolving continuously. A bud sheds a bloc of about `settle_min_pool` (40), and
`_maintain_settlements` dissolves any site holding fewer than 40 within `settle_radius` — so a daughter is born
EXACTLY at its own survival threshold and any attrition kills it. That would be churn, not colonization, and it
would explain why a bigger world does not help: the constraint is per-village survival, not space.

MEASURED: formation and dissolution rates from the model's own counters (`settle_formed_this_step`,
`settle_released_this_step`), plus the LIFETIME of each site (how long a newly founded site persists).

  formed ~= released, short lifetimes   => CHURN. The colonization machinery works and the daughters die. The
                                           fix is daughter VIABILITY, not founding.
  formed ~= released ~= 0               => the machinery is idle; founding is what is blocked.
  formed > released                     => sites are still accumulating and 2000 steps was simply too short.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "1500"))
FROM = int(os.environ.get("C_FROM", "700"))          # measure at equilibrium, not in the founding transient
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1").split(",")]
PATCH = int(os.environ.get("C_PATCH", "40"))
N = 100


def run_one(ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, patch=PATCH, clim="temperate", terr="coastal")
    formed = released = 0
    born: dict = {}          # site -> step it appeared
    lifetimes: list = []
    prev = set()
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        cur = set(w._settlement_sites)
        if t >= FROM:
            formed += w.settle_formed_this_step
            released += w.settle_released_this_step
        for s in cur - prev:
            born[s] = t
        for s in prev - cur:
            if s in born:
                if t >= FROM:
                    lifetimes.append(t - born[s])
                del born[s]
        prev = cur
    span = STEPS - FROM
    pop = w.agent_list
    grp: dict = {}
    for a in pop:
        s = w._nearest_settlement(a.pos)
        if s is not None:
            grp[s] = grp.get(s, 0) + 1
    sizes = sorted(grp.values())
    minp = w._demog.settle_min_pool
    return dict(
        pop=len(pop), sites=len(w._settlement_sites),
        formed_per100=100.0 * formed / span, released_per100=100.0 * released / span,
        life_med=st.median(lifetimes) if lifetimes else float("nan"),
        life_n=len(lifetimes),
        frac_short=(sum(1 for L in lifetimes if L < 100) / len(lifetimes)) if lifetimes else float("nan"),
        vill_med=st.median(sizes) if sizes else float("nan"),
        # how close is a typical village to the dissolution threshold it must clear every step?
        frac_near_min=(sum(1 for s in sizes if s < 1.5 * minp) / len(sizes)) if sizes else float("nan"),
        min_pool=minp)


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    ARMS = {"canon": {}, "radius 1": {"settle_radius": 1}}
    print(f"SETTLEMENT CHURN | temperate patch {PATCH} | steps {FROM}-{STEPS} | seeds {SEEDS}")
    print("are villages founded and then dying?\n")
    res = {a: [r for r in (run_one(s, ov) for s in SEEDS) if r] for a, ov in ARMS.items()}
    keys = [("pop", "pop", "{:.0f}"), ("sites", "settlement sites (net)", "{:.1f}"),
            ("formed_per100", "sites FORMED per 100 steps", "{:.1f}"),
            ("released_per100", "sites DISSOLVED per 100 steps", "{:.1f}"),
            ("life_n", "site deaths observed", "{:.0f}"),
            ("life_med", "median site LIFETIME (steps)", "{:.0f}"),
            ("frac_short", "frac of sites dead inside 100 steps", "{:.2f}"),
            ("vill_med", "village size, median", "{:.0f}"),
            ("min_pool", "settle_min_pool (dissolve below this)", "{:.0f}"),
            ("frac_near_min", "frac of villages under 1.5x the threshold", "{:.2f}")]
    print(f"{'metric':44s}" + "".join(f"{a:>20s}" for a in ARMS))
    print("-" * 84)
    for k, label, fmt in keys:
        line = ""
        for a in ARMS:
            m, e = ms([r[k] for r in res[a]])
            line += f"{fmt.format(m) + ' +/- ' + fmt.format(e):>20s}"
        print(f"{label:44s}{line}")


if __name__ == "__main__":
    main()
