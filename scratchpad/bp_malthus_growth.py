"""R-106 Add.105 part 8 — DOES THE POPULATION GROW, SPREAD, AND PLATEAU AT THE FOOD CEILING?

The supervisor's target, stated plainly: Malthusian dynamics = the population expands (and SPREADS while it
expands) while food remains, and contracts when food fails — the contraction normally driven by an EXTERNAL
shock (a long drought), not by an endogenous stall.

Measured so far: the population sits at ~8% of carrying capacity on all three worlds while 100% of agents hold
a better EMPTY cell one step away. The brake that stops growth is `enable_village_density_disease` — the
skip-list's own "de-facto Malthusian brake" — which is a CROWDING brake, not a food brake.

THE QUESTION THIS PROBE ANSWERS. Remove the crowding brake and watch the TRAJECTORY against the measured food
ceiling (temperate stock capacity ~13,611 people, bp_malthus_ratecap.py):
  (a) grows, SPREADS, and PLATEAUS near the food ceiling  => the substrate CAN do Malthusian dynamics; the
      crowding brake is simply the wrong brake, and a drought can then be laid on top.
  (b) grows without limit, no plateau                      => the food ceiling does not bind regionally either,
      and THAT is the defect to fix before any drought is added.
  (c) grows but does NOT spread                            => the pin, not the brake, is the binding constraint.

Reading (b) is what the skip-list reports for `enable_village_catchment_spread` ("571 -> 5,134, accelerating,
no plateau") — but that was never compared against a measured carrying capacity, and 5,134 is well UNDER the
13,611 this world can feed. So an apparent runaway may have been an approach to the ceiling. This probe records
the trajectory so the difference is visible instead of inferred.

ARMS are diagnostic ablations only. Nothing is adopted and canon is not touched.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "2000"))
EVERY = int(os.environ.get("C_EVERY", "100"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1,2").split(",")]
N = 100
BURN = 75000.0

# PASS 2 — clean attribution. Pass 1 showed `enable_village_density_disease` is INERT (1358 vs 1357 pop, land
# use 0.18 vs 0.19), so the "de-facto Malthusian brake" of the skip-list does nothing here and the gain in pass
# 1's third arm must come from the radius. These arms separate that, and test the NEXT candidate brake: site
# count sat at 23-25 in EVERY pass-1 arm regardless of population, so something pins the number of villages.
ARMS = {
    "canon":                     {},
    "radius 1 ONLY":             {"settle_radius": 1},
    "radius 1 + no dens-fert":   {"settle_radius": 1, "enable_density_fertility": False},
}


def run_one(clim, terr, ws, ov):
    canon = dict(runconfig.load()["DemographyConfig"]); canon.update(ov)
    w = build(canon, ws, 0, clim=clim, terr=terr)
    tf = w._harvest_field
    land = [(x, y) for y in range(N) for x in range(N) if w._fields.isWater[y, x] == 0]
    cap = sum(tf.level(x, y) for x, y in land) / BURN          # STOCK carrying capacity, people
    n_food = sum(1 for x, y in land if tf.level(x, y) > 0)
    traj = []
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if (t + 1) % EVERY == 0:
            pop = w.agent_list
            cells = {a.pos for a in pop}
            traj.append((t + 1, len(pop), len(cells) / max(1, n_food), len(pop) / cap))
    # END-STATE DIAGNOSTICS — why does it plateau HERE? Site count was invariant at 23-25 across every pass-1
    # arm, so record how the population is organised, and whether people still have somewhere better to go.
    pop = w.agent_list
    occ = {}
    for a in pop:
        occ[a.pos] = occ.get(a.pos, 0) + 1
    grp = {}
    unsettled = 0
    for a in pop:
        s = w._nearest_settlement(a.pos)
        if s is None:
            unsettled += 1
        else:
            grp[s] = grp.get(s, 0) + 1
    better = 0
    for a in pop:
        here = occ[a.pos]
        mine = tf.level(*a.pos) / here
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                q = ((a.pos[0] + dx) % N, (a.pos[1] + dy) % N)
                if w._fields.isWater[q[1], q[0]] != 0:
                    continue
                if tf.level(*q) / (occ.get(q, 0) + 1) > mine:
                    better += 1
                    break
            else:
                continue
            break
    lt = w.life_table()
    return dict(traj=traj, cap=cap, starv=lt["starv_share"], e0=lt["e0"],
                n_sites=len(getattr(w, "_settlement_sites", ())),
                frac_unsettled=unsettled / max(1, len(pop)),
                vill_med=(st.median(grp.values()) if grp else float("nan")),
                frac_better=better / max(1, len(pop)))


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    terr = os.environ.get("C_TERR", "coastal")
    print(f"MALTHUSIAN GROWTH TEST | {clim}/{terr} | {STEPS} steps | seeds {SEEDS}")
    print("does the population GROW, SPREAD, and PLATEAU at the food ceiling?\n")
    res = {}
    for arm, ov in ARMS.items():
        res[arm] = [run_one(clim, terr, s, ov) for s in SEEDS]
        print(f"  {arm}: done", flush=True)
    cap = st.mean([r["cap"] for r in res["canon"]])
    print(f"\nSTOCK carrying capacity of this world: {cap:,.0f} people\n")
    steps = [p[0] for p in res["canon"][0]["traj"]]
    for arm in ARMS:
        print(f"--- {arm}")
        print(f"{'step':>7s}{'pop':>12s}{'% of capacity':>16s}{'land use':>12s}")
        for i, s in enumerate(steps):
            pops, pcts, lus = [], [], []
            for r in res[arm]:
                if i < len(r["traj"]):
                    pops.append(r["traj"][i][1]); lus.append(r["traj"][i][2]); pcts.append(r["traj"][i][3])
            if not pops:
                continue
            print(f"{s:>7d}{st.mean(pops):>12,.0f}{st.mean(pcts)*100:>15.1f}%{st.mean(lus):>12.3f}")
        def _m(k):
            v = [r[k] for r in res[arm] if r[k] == r[k]]
            return st.mean(v) if v else float("nan")
        print(f"   end: e0 {_m('e0'):.1f} | starvation {_m('starv'):.2f} | sites {_m('n_sites'):.0f} "
              f"| village med {_m('vill_med'):.0f} | OUTSIDE any village {_m('frac_unsettled'):.2f} "
              f"| still have a better cell {_m('frac_better'):.2f}\n")


if __name__ == "__main__":
    main()
