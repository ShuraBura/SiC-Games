"""R-102 — BIOME x RESIDENCE sweep of the full elite stack.

WHY. Everything from R-86 to R-101 was validated in ONE world (coastal-temperate) under ONE residence rule
(virilocal). Charter D16: a mechanism validated in one world is a claim about that world. And R-70/R-71 already
established that terrain alone yields two regimes (rain-fed swidden -> egalitarian; alluvial floodplain ->
stratified), so terrain-dependence is a KNOWN property of the substrate that the elite layer has never been
tested against.

TWO QUESTIONS, both with predictions:
  1. Does the terrain->hierarchy signal survive the elite layer, or does R-99's rank->hierarchy route WEAKEN it
     by giving poor worlds a second road up? Either answer is informative.
  2. Does ANY world cycle? R-97's negative covers coastal-temperate and tropical only. A world with stronger
     seasonal or resource swings is the most likely place for a positive, and one would substantially change
     R-97's "not at this scale, anywhere".
  3. (bonus) RESIDENCE: Ember & Ember 1971 is filed as REFERENCE with "comparisons deferred". virilocal vs
     uxorilocal has never been run. This closes that.

Runs SEQUENTIALLY on purpose: these are single-threaded and CPU-bound, so running them concurrently only makes
each slower without finishing sooner (measured earlier today: three concurrent arms roughly halved per-arm
throughput). Genealogy is ON throughout — measured at zero runtime cost and ~37 MB/run, and leaving it off is
what made the previous pair unable to answer post-hoc questions at all.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# Spanning set over the axis the project already knows matters: aquatic availability x productivity.
#
# ORDERED CHEAPEST-FIRST, and that ordering is load-bearing. Runtime scales with POPULATION, not steps: the
# measured flat-tropical arms carried pop 21k-39k and cost 59-173 min for THREE THOUSAND steps, against 16 min
# for coastal-temperate at pop 6.4k. Running the rich worlds first would mean a whole night spent inside one
# arm with nothing else finished; running them last means the marginal worlds are done and comparable by
# morning whatever the tropics do.
WORLDS = [
    ("mountainous", "boreal"),    # marginal, little aquatic         -> predict LEAST stratified. cheapest.
    ("hilly", "temperate"),       # intermediate control
    ("flat", "tropical"),         # rich but rain-fed, the agrarian route
    ("coastal", "tropical"),      # max aquatic + max productivity   -> predict MOST. dearest.
]
RESIDENCE = ["virilocal", "uxorilocal"]   # adjacent per world, so each world's PAIR completes together

STEPS = os.environ.get("SWEEP_STEPS", "15000")
FOUNDERS = os.environ.get("SWEEP_FOUNDERS", "3000")
# Per-run wall-clock budget. Bounds the sweep at 8 x 2.5h worst case while letting cheap arms finish early.
# CONSEQUENCE FOR ANALYSIS, stated up front: arms that hit the budget stop SHORT of 15000, so the cross-world
# comparison must be read at the deepest COMMON step, not at each arm's own end. meta["steps_completed"] and
# meta["truncated"] record which is which -- comparing an arm's endpoint against another's would be exactly the
# hidden-denominator error the charter's D15 names.
MAXMIN = os.environ.get("SWEEP_MAXMIN", "150")

STACK = dict(
    C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
    C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
    C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1",
    C_GENEA="1",                      # ON: free, and the post-hoc substrate
)

PROG = os.path.join(HERE, "sweep_progress.txt")


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


if __name__ == "__main__":
    open(PROG, "w").close()
    jobs = [(t, c, r) for (t, c) in WORLDS for r in RESIDENCE]
    log(f"BIOME x RESIDENCE sweep: {len(jobs)} runs x {STEPS} steps, sequential")
    log(f"worlds: {WORLDS}")
    log(f"residence: {RESIDENCE}\n")
    t0 = time.time()
    done = []
    for i, (terr, clim, res) in enumerate(jobs, 1):
        tag = f"_sw_{terr}_{clim}_{res[:4]}"
        env = dict(os.environ, C_TAG=tag, C_TERR=terr, C_CLIM=clim, C_MAXMIN=MAXMIN,
                   C_STEPS=STEPS, C_FOUNDERS=FOUNDERS, C_RESIDENCE=res, **STACK)
        log(f"[{i}/{len(jobs)}] {terr}-{clim} {res}  -> {tag}   (elapsed {(time.time()-t0)/60:.0f}m)")
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "run_campaign.py")],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:] or ["(no output)"]
        log(f"      rc={r.returncode}  {tail[0][:110]}")
        if r.returncode != 0:
            log(f"      STDERR: {r.stderr.strip()[-400:]}")
            continue
        # Report the achieved horizon per arm, so the common-step question is answerable from the log alone
        # rather than by opening eight trajectories.
        try:
            import json
            with open(os.path.join(HERE, f"campaign_trajectory{tag}.json"), encoding="utf-8") as fh:
                m = json.load(fh)["meta"]
            done.append((tag, m.get("steps_completed"), m.get("truncated")))
            log(f"      steps_completed={m.get('steps_completed')}  truncated={m.get('truncated')}"
                f"  wall={m.get('wall_minutes')}m")
        except Exception as e:
            log(f"      (could not read back meta: {e})")
    log(f"\nSWEEP DONE in {(time.time()-t0)/60:.0f} min")
    if done:
        common = min(s for _, s, _ in done if s)
        log(f"DEEPEST COMMON STEP = {common}   <- compare arms HERE, not at their own endpoints")
        for tag, s, tr in done:
            log(f"   {tag:38s} {s:>6} {'(truncated)' if tr else ''}")
