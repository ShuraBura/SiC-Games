"""R-106 packing-paradox mechanism: reach vs perception vs pull.

The food-chain diagnosis showed the population clusters onto ~14% of the land and starves there while 86% of
food-bearing land sits empty. Movement (substrate.diffusion_select_target) is LOCAL: an agent evaluates only the
current cell + 4 cardinal cells at stride `move_radius`. So the question is why the empty rich cells are not used:

  REACH       the nearest empty FEEDING cell is farther than an agent moves in a step (movement too local to
              relocate — no residential move).
  PERCEPTION  an empty feeding cell IS within a step's reach but the local gradient / candidate set does not
              send the agent there.
  PULL        the agent has a within-reach feeding cell but stays (agglomeration/cohesion outweighs the escape).

Instrument, at equilibrium (canon, bp OFF), for FOOD-SHORT agents (realized intake < maintenance):
  - per-step displacement actually achieved (how far agents move);
  - Chebyshev distance to the nearest EMPTY feeding cell (a cell that could feed a lone forager: min(S,cv) >=
    burn, occupancy 0);
  - whether such a cell lies within the agent's realized reach (=> perception/pull) or beyond it (=> reach).
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("R_STEPS", "800"))
SAMPLE_FROM = int(os.environ.get("R_SAMPLE_FROM", "760"))   # a few equilibrium steps
SAMPLE_EVERY = int(os.environ.get("R_SAMPLE_EVERY", "8"))


def cheb_nearest_empty_feeding(px, py, feed_empty_cells):
    """min Chebyshev distance from (px,py) to any cell in feed_empty_cells (list of (x,y)). inf if none."""
    best = 1e9
    for (cx, cy) in feed_empty_cells:
        dxy = max(abs(cx - px), abs(cy - py))
        if dxy < best:
            best = dxy
            if best <= 1:
                break
    return best


def run_one(clim, world_seed, agent_seed):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, world_seed, agent_seed, clim=clim)
    burn = w._burn
    cap_on = getattr(w._demog, "enable_forage_cap", False)
    fcap = w._forage_cap_field() if cap_on else None

    disp = []            # per-step displacement of all agents (Chebyshev)
    short_dist = []      # for ADULT food-short agents: distance to nearest empty feeding cell
    short_reachable = [] # 1 if that cell is within this agent's realized step reach, else 0
    short_eta = []       # eta of the adult-short agents (rule out the low-eta explanation)
    short_frac = []
    prev_pos = {}
    for t in range(STEPS):
        if t >= SAMPLE_FROM and (t % SAMPLE_EVERY == 0):
            prev_pos = {id(a): a.pos for a in w.agent_list}
        w.step()
        if not w.agent_list:
            break
        if t >= SAMPLE_FROM and (t % SAMPLE_EVERY == 0):
            hf = w._harvest_field
            # occupancy now
            occ = {}
            for a in w.agent_list:
                occ[a.pos] = occ.get(a.pos, 0) + 1
            # displacement this step (agents present before and after)
            step_disp = {}
            for a in w.agent_list:
                p0 = prev_pos.get(id(a))
                if p0 is not None:
                    dd = max(abs(a.pos[0] - p0[0]), abs(a.pos[1] - p0[1]))
                    step_disp[id(a)] = dd
                    disp.append(dd)
            reach = int(np.percentile(list(step_disp.values()), 90)) if step_disp else 1
            reach = max(reach, 1)
            # empty feeding cells: could feed a lone forager (min(S,cv) >= burn) and currently unoccupied
            feed_empty = []
            H, W = hf.height, hf.width
            for y in range(H):
                for x in range(W):
                    S = hf.level(x, y)
                    if S <= 0.0:
                        continue
                    cv = float(fcap[y, x]) if fcap is not None else 1e18
                    if min(S, cv) >= burn and occ.get((x, y), 0) == 0:
                        feed_empty.append((x, y))
            # food-short agents this step. Split ADULT (moving could help) from JUVENILE (low-eta tail: short
            # everywhere, a provisioning problem, not a spatial one). Only the ADULT-short population tests the
            # reach/perception/pull question.
            shorts = [a for a in w.agent_list
                      if getattr(a, "_last_intake", 0.0) < burn * a.consumption_factor()]
            short_frac.append(len(shorts) / len(w.agent_list))
            for a in shorts:
                if a.is_juvenile():
                    continue
                # would MOVING help this adult? only if a reachable empty feeding cell gives it >= its own req
                # (eta-limited adults cannot be fed by moving; exclude the eta explanation).
                dnear = cheb_nearest_empty_feeding(a.pos[0], a.pos[1], feed_empty)
                short_dist.append(dnear)
                short_reachable.append(1 if dnear <= reach else 0)
                short_eta.append(a.eta())
    return dict(
        disp=np.array(disp), short_dist=np.array(short_dist),
        short_reachable=np.array(short_reachable), short_eta=np.array(short_eta),
        short_frac=float(np.mean(short_frac)) if short_frac else float("nan"),
        pop=len(w.agent_list))


def main():
    biomes = os.environ.get("R_BIOMES", "temperate,savanna").split(",")
    worlds = [int(x) for x in os.environ.get("R_WORLDS", "0,1,2").split(",")]
    agents = [int(x) for x in os.environ.get("R_AGENTS", "0").split(",")]
    print(f"REACH/PERCEPTION/PULL PROBE | canon (bp OFF) | {STEPS} steps | sample>={SAMPLE_FROM} every "
          f"{SAMPLE_EVERY} | worlds {worlds} x agents {agents}", flush=True)
    for clim in biomes:
        D, SD, SR, SE, SF = [], [], [], [], []
        for ws in worlds:
            for as_ in agents:
                r = run_one(clim, ws, as_)
                D.append(r["disp"]); SD.append(r["short_dist"]); SR.append(r["short_reachable"])
                SE.append(r["short_eta"]); SF.append(r["short_frac"])
                print(f"  {clim} w{ws}a{as_}: pop {r['pop']} short {r['short_frac']:.2f} | "
                      f"disp med {np.median(r['disp']):.1f} p90 {np.percentile(r['disp'],90):.1f} | "
                      f"dist-to-empty-feed med {np.median(r['short_dist']):.1f} "
                      f"reachable {r['short_reachable'].mean():.2%}", flush=True)
        disp = np.concatenate(D); sd = np.concatenate(SD); sr = np.concatenate(SR)
        print(f"  === {clim} POOLED ===")
        print(f"    food-short fraction of pop         {np.mean(SF):.2f}")
        print(f"    per-step displacement  median {np.median(disp):.1f}  p90 {np.percentile(disp,90):.1f}  "
              f"max {disp.max():.0f}  (fraction that stay put: {(disp==0).mean():.2%})")
        print(f"    short agents' distance to nearest EMPTY feeding cell: "
              f"median {np.median(sd):.1f}  p25 {np.percentile(sd,25):.1f}  p90 {np.percentile(sd,90):.1f}")
        se = np.concatenate(SE)
        print(f"    ADULT-short agents (n={len(sd)}): median eta {np.median(se):.2f}  "
              f"(adult fed eta ~0.95; low eta => cannot be fed by moving)")
        print(f"    ADULT-short distance to nearest EMPTY feeding cell: "
              f"median {np.median(sd):.1f}  p25 {np.percentile(sd,25):.1f}  p90 {np.percentile(sd,90):.1f}")
        print(f"    ADULT-short with a feeding cell WITHIN reach: {sr.mean():.2%}  "
              f"-> {'PERCEPTION/PULL' if sr.mean()>0.5 else 'REACH'} dominates")
        if os.environ.get("R_DUMP"):
            np.savez(f"{os.environ['R_DUMP']}_{clim}.npz", disp=disp, short_dist=sd, short_reachable=sr,
                     short_eta=se, short_frac=np.array([np.mean(SF)]))
            print(f"    [dumped {os.environ['R_DUMP']}_{clim}.npz]")


if __name__ == "__main__":
    main()
