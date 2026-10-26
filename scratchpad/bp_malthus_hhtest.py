"""R-106 Add.105 part 13 — DOES THE FAMILY-CLOSED BLOC FIX THE CHURN?

The diagnosis (part 12, confirmed per-agent): budding cleaves the emigrant bloc by INDIVIDUAL kin affinity, so
the bloc is not closed under `_family_head`; the F.3b co-movement block then teleports every follower to its
head's cell at ANY distance, and 97% of the founders that leave a new site land EXACTLY on their head's cell.
The daughter loses ~90% of its founders in one step and dies inside the 12-step hysteresis.

`enable_bud_household_closure` assembles the bloc from whole households instead. This tests it.

PRIMARY (the mechanism itself — if this does not move, the fix does not work and nothing else matters):
    frac of founders still ON the site one step after founding      canon ~0.13
    median site LIFETIME                                            canon ~20 steps
    frac of sites dead inside 100 steps                             canon ~0.90

SECONDARY (does fixing it produce Malthusian behaviour?):
    settlement count, population, % of measured carrying capacity, land use

GUARDRAIL (a fix that breaks an anchored marker is not a fix):
    village size median + frac inside Bar-Yosef 40-150; e0 vs Ache 36.6; starvation share
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "1500"))
FROM = int(os.environ.get("C_FROM", "700"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1,2").split(",")]
PATCH = int(os.environ.get("C_PATCH", "40"))
N = 100
BURN = 75000.0

ARMS = {"canon": {}, "household closure": {"enable_bud_household_closure": True}}


def run_one(ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, patch=PATCH, clim="temperate", terr="coastal")
    tf = w._harvest_field
    land = [(x, y) for y in range(N) for x in range(N) if w._fields.isWater[y, x] == 0]
    food = [c for c in land if tf.level(c[0], c[1]) > 0]
    cap = sum(tf.level(c[0], c[1]) for c in food) / BURN
    rad = w._demog.settle_radius

    formed = released = 0
    born: dict = {}
    lifetimes: list = []
    retain: list = []          # frac of founders still ON the site one step later
    pending: list = []         # [(site, founders, t0)]
    prev = set()
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        cur = set(w._settlement_sites)
        live = {id(a) for a in w.agent_list}
        for (site, f, t0) in list(pending):
            if t - t0 >= 1:
                alive = [a for a in f if id(a) in live]
                retain.append(sum(1 for a in alive if a.pos == site) / len(f))
                pending.remove((site, f, t0))
        if t >= FROM:
            formed += w.settle_formed_this_step
            released += w.settle_released_this_step
        for s in cur - prev:
            born[s] = t
            if t >= FROM:
                f = [a for a in w.agent_list if a.pos == s]
                if len(f) >= 10:
                    pending.append((s, f, t))
        for s in prev - cur:
            if s in born:
                if t >= FROM:
                    lifetimes.append(t - born[s])
                del born[s]
        prev = cur

    span = STEPS - FROM
    pop = w.agent_list
    cells = {a.pos for a in pop}
    grp: dict = {}
    for a in pop:
        s = w._nearest_settlement(a.pos)
        if s is not None:
            grp[s] = grp.get(s, 0) + 1
    sizes = sorted(grp.values())
    lt = w.life_table()
    return dict(
        retain=st.mean(retain) if retain else float("nan"), retain_n=len(retain),
        life_med=st.median(lifetimes) if lifetimes else float("nan"),
        frac_short=(sum(1 for L in lifetimes if L < 100) / len(lifetimes)) if lifetimes else float("nan"),
        formed=100.0 * formed / span, released=100.0 * released / span,
        sites=len(w._settlement_sites), pop=len(pop), pct=len(pop) / cap,
        land_use=len(cells) / max(1, len(food)),
        vill_med=st.median(sizes) if sizes else float("nan"),
        in_band=(sum(1 for s in sizes if 40 <= s <= 150) / len(sizes)) if sizes else float("nan"),
        e0=lt["e0"], starv=lt["starv_share"])


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    print(f"FAMILY-CLOSED BLOC | temperate patch {PATCH} | {STEPS} steps | seeds {SEEDS}\n")
    res = {a: [r for r in (run_one(s, ov) for s in SEEDS) if r] for a, ov in ARMS.items()}
    keys = [("__1", "-- PRIMARY: the mechanism --", ""),
            ("retain", "founders still ON site after 1 step", "{:.2f}"),
            ("life_med", "median site lifetime (steps)", "{:.0f}"),
            ("frac_short", "frac of sites dead inside 100 steps", "{:.2f}"),
            ("formed", "sites formed per 100 steps", "{:.1f}"),
            ("released", "sites dissolved per 100 steps", "{:.1f}"),
            ("__2", "-- SECONDARY: Malthusian expansion --", ""),
            ("sites", "settlement sites", "{:.1f}"),
            ("pop", "population", "{:.0f}"),
            ("pct", "frac of carrying capacity", "{:.3f}"),
            ("land_use", "frac of food cells used", "{:.3f}"),
            ("__3", "-- GUARDRAILS (anchors) --", ""),
            ("vill_med", "village size median (Bar-Yosef 40-150)", "{:.0f}"),
            ("in_band", "frac of villages inside 40-150", "{:.2f}"),
            ("e0", "e0 (Ache 36.6)", "{:.1f}"),
            ("starv", "starvation share of deaths", "{:.2f}")]
    print(f"{'metric':44s}" + "".join(f"{a:>22s}" for a in ARMS))
    print("-" * 88)
    for k, label, fmt in keys:
        if not fmt:
            print(f"\n{label}")
            continue
        line = ""
        for a in ARMS:
            m, e = ms([r[k] for r in res[a]])
            line += f"{fmt.format(m) + ' +/- ' + fmt.format(e):>22s}"
        print(f"{label:44s}{line}")


if __name__ == "__main__":
    main()
