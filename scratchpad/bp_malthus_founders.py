"""R-106 Add.105 part 12 — FOLLOW THE ACTUAL FOUNDERS, not a spatial window.

Part 11 measured a daughter village's head-count in a 5x5 window: 82.6 at birth, 23.6 one step later. I read
that as a one-step exodus, but the window is not the village — it can count people who belong to a NEIGHBOURING
older site and simply walked home. Two candidate explanations were then checked and BOTH failed:
  - stale `_nearest_map` (founders not pinned to their own new site): REFUTED, `_step_rivalrous` clears the map
    at the start of every movement phase, so the new site is in it.
  - settlement scalar stress: at n=83 against midpoint 150 / width 50 the repulsion is ~21%/step, not 71%.

So measure the thing itself. When a new site appears, snapshot the AGENT OBJECTS standing on that exact cell —
the teleported faction (`a.pos = best`) — and follow those identities:
    alive        did they die?
    on_site      still standing on the site cell
    in_radius    still inside settle_radius of it
    dist         median Chebyshev distance from the site
    left_band    band_id changed away from the founding band

  founders stay, window falls   => part 11's "exodus" was a window artifact; the daughters are drained by
                                   something slower, and the churn cause is still open.
  founders scatter              => a real one-step exodus of the founders themselves, and the cause is in the
                                   movement step, to be found there.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "1100"))
FROM = int(os.environ.get("C_FROM", "600"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1").split(",")]
PATCH = int(os.environ.get("C_PATCH", "40"))
TRACK = [0, 1, 2, 3, 5, 10, 20]
N = 100


def cheb(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    dx = min(dx, N - dx); dy = min(dy, N - dy)
    return max(dx, dy)


def run_one(ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, patch=PATCH, clim="temperate", terr="coastal")
    rad = w._demog.settle_radius
    watch: list = []          # [{site, t0, founders:[agents], band, rec:{age:dict}}]
    done: list = []
    prev = set()
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        live = set(id(a) for a in w.agent_list)
        cur = set(w._settlement_sites)
        for e in list(watch):
            age = t - e["t0"]
            if age in TRACK and age > 0:
                f = e["founders"]
                alive = [a for a in f if id(a) in live]
                e["rec"][age] = dict(
                    alive=len(alive) / len(f),
                    on_site=sum(1 for a in alive if a.pos == e["site"]) / len(f),
                    in_rad=sum(1 for a in alive if cheb(a.pos, e["site"]) <= rad) / len(f),
                    dist=st.median([cheb(a.pos, e["site"]) for a in alive]) if alive else float("nan"),
                    left=sum(1 for a in alive if a._group.band_id != e["band"]) / max(1, len(alive)))
            if age >= max(TRACK) or e["site"] not in cur:
                e["died"] = e["site"] not in cur
                e["death_age"] = age if e["died"] else None
                done.append(e); watch.remove(e)
        if t >= FROM:
            for site in cur - prev:
                founders = [a for a in w.agent_list if a.pos == site]
                if len(founders) >= 10:
                    bands = {}
                    for a in founders:
                        bands[a._group.band_id] = bands.get(a._group.band_id, 0) + 1
                    watch.append(dict(site=site, t0=t, founders=founders,
                                      band=max(bands, key=bands.get),
                                      rec={0: dict(alive=1.0, on_site=1.0, in_rad=1.0, dist=0.0, left=0.0)},
                                      n0=len(founders)))
        prev = cur
    done.extend(watch)
    return done or None


def main():
    print(f"FOLLOW THE FOUNDERS | temperate patch {PATCH} | seeds {SEEDS}")
    print("snapshot the agents standing on a brand-new site, then follow those identities\n")
    allrec = []
    for s in SEEDS:
        r = run_one(s)
        if r:
            allrec.extend(r)
    if not allrec:
        print("no daughters observed")
        return
    n0 = st.mean([e["n0"] for e in allrec])
    print(f"daughters tracked: {len(allrec)} | founders on the site cell at birth: {n0:.1f}")
    died = [e for e in allrec if e.get("died")]
    print(f"died within the window: {len(died)}/{len(allrec)}\n")
    print(f"{'age':>5s}{'alive':>9s}{'ON the site':>13s}{'in radius':>12s}{'med dist':>10s}{'left band':>11s}")
    print("-" * 60)
    for a in TRACK:
        vals = [e["rec"][a] for e in allrec if a in e["rec"]]
        if not vals:
            continue
        def m(k):
            v = [x[k] for x in vals if x[k] == x[k]]
            return st.mean(v) if v else float("nan")
        print(f"{a:>5d}{m('alive'):>9.2f}{m('on_site'):>13.2f}{m('in_rad'):>12.2f}"
              f"{m('dist'):>10.1f}{m('left'):>11.2f}")


if __name__ == "__main__":
    main()
