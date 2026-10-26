"""R-106 Add.105 part 14 — POWERED replication of the family-closed bloc (supervisor's Stage 1).

WHY THIS RERUN. The first A/B (3 seeds) reported sites 29.0 -> 36.3 and population 2112 -> 2305 and I called the
population effect "no effect". That was wrong: the spread was +/-799 on 2112 (+/-38%), so the test could not
have detected anything under about +50%. The honest statement was "cannot tell".

TWO DESIGN FIXES, both from the project's own record:
  1. FIX THE WORLD, VARY THE DEMOGRAPHIC SEED. `build(update, world_seed, agent_seed)` — the earlier probes
     varied the WORLD seed, and the e0/population noise in this model is dominated by the world lottery
     ([[project_sic_games_emigration_e0]] trap note). One world, 10 demographic seeds, is the low-noise
     instrument and is also Stage 1 of the supervisor's protocol (one world first, then across worlds).
  2. PAIR THE ARMS on the same seed and test the PAIRED difference, which removes the between-seed variance
     that swamped the first test.

PRIMARY QUESTION: does the repair raise the number of villages, and does the population follow?
    N_villages is the only quantity that can let the population track the region: population ~= N_villages x
    village_size, village_size is held at the local condition margin (~55, well under its ~180 food ceiling),
    and N_villages does not grow with land (14.3% -> 9.8% -> 4.7% of capacity as the patch grows).

GUARDRAILS: a fix that buys villages by breaking an anchored marker is not a fix — Bar-Yosef 40-150 village
size, Ache e0 36.6, starvation share.
"""
import os
import statistics as st
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "2000"))
FROM = int(os.environ.get("C_FROM", "1000"))
NSEED = int(os.environ.get("C_NSEED", "10"))
WORLD = int(os.environ.get("C_WORLD", "0"))
PATCH = int(os.environ.get("C_PATCH", "40"))
PROGRESS = os.path.join(ROOT, "scratchpad", "malthus_replicate_progress.txt")
N = 100
BURN = 75000.0

ARMS = {"canon": {}, "viable site": {"enable_bud_viable_site": True}}


def note(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(PROGRESS, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def run_one(agent_seed, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, WORLD, agent_seed, patch=PATCH, clim="temperate", terr="coastal")
    tf = w._harvest_field
    land = [(x, y) for y in range(N) for x in range(N) if w._fields.isWater[y, x] == 0]
    food = [c for c in land if tf.level(c[0], c[1]) > 0]
    cap = sum(tf.level(c[0], c[1]) for c in food) / BURN
    formed = released = 0
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        if t >= FROM:
            formed += w.settle_formed_this_step
            released += w.settle_released_this_step
    pop = w.agent_list
    cells = {a.pos for a in pop}
    grp: dict = {}
    for a in pop:
        s = w._nearest_settlement(a.pos)
        if s is not None:
            grp[s] = grp.get(s, 0) + 1
    sizes = sorted(grp.values())
    lt = w.life_table()
    span = STEPS - FROM
    return dict(
        sites=len(w._settlement_sites), pop=len(pop), pct=len(pop) / cap,
        land_use=len(cells) / max(1, len(food)),
        formed=100.0 * formed / span, released=100.0 * released / span,
        vill_med=st.median(sizes) if sizes else float("nan"),
        in_band=(sum(1 for s in sizes if 40 <= s <= 150) / len(sizes)) if sizes else float("nan"),
        e0=lt["e0"], starv=lt["starv_share"])


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    open(PROGRESS, "w", encoding="utf-8").close()
    note(f"START | world {WORLD} fixed | {NSEED} demographic seeds | {STEPS} steps | patch {PATCH}")
    t0 = time.time()
    res = {a: {} for a in ARMS}
    total = NSEED * len(ARMS)
    done = 0
    for s in range(NSEED):
        for arm, ov in ARMS.items():
            r = run_one(s, ov)
            if r:
                res[arm][s] = r
            done += 1
            el = time.time() - t0
            eta = el / done * (total - done)
            note(f"  seed {s} | {arm:18s} | sites {r['sites'] if r else 'DIED':>4} "
                 f"pop {r['pop'] if r else 0:>5} | {done}/{total} done "
                 f"| elapsed {el/60:.0f}m ETA {eta/60:.0f}m")
    note("DONE — analysing")

    keys = [("__1", "-- PRIMARY: the lever --", ""),
            ("sites", "settlement sites", "{:.1f}"),
            ("pop", "population", "{:.0f}"),
            ("pct", "frac of carrying capacity", "{:.3f}"),
            ("land_use", "frac of food cells used", "{:.3f}"),
            ("formed", "sites formed / 100 steps", "{:.2f}"),
            ("released", "sites dissolved / 100 steps", "{:.2f}"),
            ("__2", "-- GUARDRAILS (anchors) --", ""),
            ("vill_med", "village size median (Bar-Yosef 40-150)", "{:.0f}"),
            ("in_band", "frac of villages inside 40-150", "{:.2f}"),
            ("e0", "e0 (Ache 36.6)", "{:.1f}"),
            ("starv", "starvation share of deaths", "{:.2f}")]
    arm_a, arm_b = list(ARMS)
    print()
    print(f"{'metric':42s}{arm_a:>20s}{arm_b:>20s}{'paired diff':>22s}")
    print("-" * 104)
    for k, label, fmt in keys:
        if not fmt:
            print(f"\n{label}")
            continue
        both = [s for s in res[arm_a] if s in res[arm_b]]
        a = [res[arm_a][s][k] for s in both]
        b = [res[arm_b][s][k] for s in both]
        ma, ea = ms(a); mb, eb = ms(b)
        dif = [y - x for x, y in zip(a, b) if x == x and y == y]
        md, ed = ms(dif)
        # paired t-like statistic: how many standard errors is the mean difference from zero?
        z = (md / ed) if ed > 0 else float("nan")
        star = "  *" if abs(z) >= 2 else ""
        print(f"{label:42s}{fmt.format(ma):>20s}{fmt.format(mb):>20s}"
              f"{fmt.format(md) + ' +/- ' + fmt.format(ed) + f' ({z:+.1f}se)' + star:>22s}")
    print("\n  * = mean paired difference is at least 2 standard errors from zero")
    print(f"  n = {len(both)} paired seeds on world {WORLD}")


if __name__ == "__main__":
    main()
