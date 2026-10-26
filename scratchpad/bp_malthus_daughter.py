"""R-106 Add.105 part 11 — WATCH A DAUGHTER VILLAGE FROM BIRTH.

Churn is established (part 10): sites form at 6.4/100 steps and dissolve at 5.3/100, median lifetime 20 steps
against a `settle_release_steps` hysteresis of 12. So a daughter falls under `settle_min_pool` within a step or
two of founding and then just runs out the timer.

THE ARITHMETIC THAT WOULD EXPLAIN IT. A bud sheds
    _bloc = min(len(village) // 2, max(settle_min_pool, len(village) - village_fission_threshold))
and budding needs len(village) > 150. For a village of 150-190, len//2 >= 75 while max(40, len-150) = 40, so
_bloc = 40 = settle_min_pool EXACTLY — the same number `_maintain_settlements` requires the daughter to keep
exceeding every step. Founded with zero margin, it fails on the first loss.

MEASURED HERE, per newly founded site: the head-count within `settle_radius` at birth and over the next steps.
  starts at ~40 and falls        => confirmed: the bloc is sized to the threshold, with no margin.
  starts well above 40           => the bloc is fine and something else drains it; look there instead.

This is a pure observer. Nothing is changed.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "1200"))
FROM = int(os.environ.get("C_FROM", "600"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1").split(",")]
PATCH = int(os.environ.get("C_PATCH", "40"))
TRACK = [0, 1, 2, 3, 5, 10, 20, 40]
N = 100


def run_one(ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, patch=PATCH, clim="temperate", terr="coastal")
    rad = w._demog.settle_radius
    minp = w._demog.settle_min_pool
    watching: dict = {}          # site -> (birth_step, {age: count})
    done: list = []
    prev = set()

    def headcount(site, occ):
        sx, sy = site
        return sum(occ.get(((sx + dx) % N, (sy + dy) % N), 0)
                   for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1))

    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        occ: dict = {}
        for a in w.agent_list:
            occ[a.pos] = occ.get(a.pos, 0) + 1
        cur = set(w._settlement_sites)
        # record the tracked daughters at their tracked ages
        for site, (t0, hist) in list(watching.items()):
            age = t - t0
            if site not in cur:                       # it died
                hist["died_at"] = age
                done.append(hist); del watching[site]
                continue
            if age in TRACK:
                hist[age] = headcount(site, occ)
            if age > max(TRACK):
                done.append(hist); del watching[site]
        if t >= FROM:
            for site in cur - prev:                   # newly founded
                watching[site] = (t, {0: headcount(site, occ)})
        prev = cur
    done.extend(watching.values())
    if not done:
        return None
    out = {"n": len(done), "min_pool": minp}
    for a in TRACK:
        v = [h[a] for h in done if a in h]
        out[f"age{a}"] = st.mean(v) if v else float("nan")
        out[f"below{a}"] = (sum(1 for x in v if x < minp) / len(v)) if v else float("nan")
    dd = [h["died_at"] for h in done if "died_at" in h]
    out["died_frac"] = len(dd) / len(done)
    out["died_med"] = st.median(dd) if dd else float("nan")
    return out


def main():
    print(f"DAUGHTER VILLAGES FROM BIRTH | temperate patch {PATCH} | seeds {SEEDS}")
    print("is a new village founded at exactly its own survival threshold?\n")
    rows = [r for r in (run_one(s) for s in SEEDS) if r]
    if not rows:
        print("no daughters observed")
        return
    def m(k):
        v = [r[k] for r in rows if k in r and r[k] == r[k]]
        return st.mean(v) if v else float("nan")
    print(f"daughters tracked: {m('n'):.0f} per seed | settle_min_pool = {m('min_pool'):.0f}\n")
    print(f"{'age (steps)':>13s}{'head-count in radius':>24s}{'frac BELOW min_pool':>23s}")
    print("-" * 60)
    for a in TRACK:
        print(f"{a:>13d}{m(f'age{a}'):>24.1f}{m(f'below{a}'):>23.2f}")
    print(f"\ndied within the tracking window: {m('died_frac'):.2f}"
          f" | median age at death {m('died_med'):.0f} steps")


if __name__ == "__main__":
    main()
