"""R-106 Add.106 STAGE 2 — `enable_density_fill_matched_radius` on the three CANONICAL worlds, real pipeline.

WHY THE REAL PIPELINE. Stage 1 (probe harness, world 0) showed the fix is a real lever (+25% population) with a
real cost (e0 -2.0 yr, starvation +5 pts). But world 0 carries a canon e0 of 40.4, well ABOVE the Ache anchor
36.6, so it could not answer the adoption question: on a world where canon sits AT the anchor, does the -2.0 push
e0 BELOW it? That is an ABSOLUTE anchor question, and Add.101 established absolute values do not transfer from the
probe harness to `run_campaign.py`. So Stage 2 runs the canonical pipeline itself.

DESIGN (the supervisor's protocol: Stage 2 = the three canonical worlds at full 15000 steps):
  worlds   temperate (coastal/temperate), savanna (coastal/savanna), montane (mountainous/savanna)
           = test_canonical_worlds_ctb.WORLDS
  arms     canon = C_ALLON=1 ; fix = canon + C_EXTRA_ON=enable_density_fill_matched_radius
  seeds    PLANET FIXED (C_WORLD_SEED=0, C_CLIM_SEED=0), DEMOGRAPHIC PATH varied (C_AGENT_SEED 0,1,2) and PAIRED
           across arms — the low-noise instrument (the world lottery dominates population/e0 variance)
  steps    15000, with C_LT_SNAP_STEP=7500 so a PERIOD life table over the equilibrium half can be computed
           (every row's `realised_e0` is CUMULATIVE from step 0 and carries the founding transient)
  kept ON  C_GENOME=1: `_kin_affinity` uses the genome when it is live, so turning it off would change the
           budding cleavage — a silent confound. OFF: C_GENEA=0, the genealogy CSV stream (pure logging).

RESOURCES (measured): ~200 MB peak at 600 steps, ~0.22 s/step, so ~300 MB and ~55 min for a full temperate run.
6 concurrent keeps memory under ~2 GB beside the user's open apps and below the 14 cores. Longest-first order.
Every child gets stdin=DEVNULL — without it Windows raises WinError 6 in `_make_inheritable` in this shell.
"""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
CAMP = os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py")
LOGDIR = os.path.join(ROOT, "scratchpad", "stage2_logs")
PROGRESS = os.path.join(ROOT, "scratchpad", "stage2_progress.txt")
CONCURRENCY = int(os.environ.get("S2_CONC", "6"))
STEPS = os.environ.get("S2_STEPS", "15000")
SNAP = os.environ.get("S2_SNAP", "7500")
SEEDS = [int(x) for x in os.environ.get("S2_SEEDS", "0,1,2").split(",")]

# longest-first: temperate ~55 min, montane ~45 min, savanna ~12 min (measured / Add.100 scaled)
WORLDS = [("temperate", "coastal", "temperate"),
          ("montane", "mountainous", "savanna"),
          ("savanna", "coastal", "savanna")]
ARMS = {"canon": "", "fix": "enable_density_fill_matched_radius"}


def note(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(PROGRESS, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def jobs():
    # S2_ONLY_ARM=name:flag runs ONLY that arm on every world/seed (the canon arm is REUSED from an earlier
    # Stage 2 when nothing canonical has changed); S2_CONTROL=world:seed adds ONE canon re-run, tagged
    # `_s2ctl_...`, which must reproduce the stored canon trajectory exactly — the proof that reuse is valid.
    only = os.environ.get("S2_ONLY_ARM")
    # several arms: "name:flag1,flag2;name2:flag3" (C_EXTRA_ON takes a comma list)
    arms = dict(a.split(":", 1) for a in only.split(";")) if only else ARMS
    for wname, terr, clim in WORLDS:
        for s in SEEDS:
            for arm, extra in arms.items():
                yield dict(world=wname, terr=terr, clim=clim, seed=s, arm=arm, extra=extra,
                           tag=f"_s2_{wname}_{arm}_s{s}")
    ctl = os.environ.get("S2_CONTROL")
    if ctl:
        cw, cs = ctl.split(":")
        for wname, terr, clim in WORLDS:
            if wname == cw:
                yield dict(world=wname, terr=terr, clim=clim, seed=int(cs), arm="canon", extra="",
                           tag=f"_s2ctl_{wname}_canon_s{cs}")


def launch(j):
    env = dict(os.environ, C_ALLON="1", C_TERR=j["terr"], C_CLIM=j["clim"], C_STEPS=STEPS,
               C_SEED="0", C_WORLD_SEED="0", C_CLIM_SEED="0", C_AGENT_SEED=str(j["seed"]),
               C_TAG=j["tag"], C_GENEA="0", C_GENOME="1", C_LT_SNAP_STEP=SNAP)
    env.pop("C_EXTRA_ON", None)
    env.pop("C_PARAM", None)
    if j["extra"].startswith("@"):          # "@field=value[,field=value]" -> a PARAMETER change via C_PARAM
        env["C_PARAM"] = j["extra"][1:]
    elif j["extra"]:
        env["C_EXTRA_ON"] = j["extra"]
    log = open(os.path.join(LOGDIR, j["tag"].lstrip("_") + ".log"), "w", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-u", CAMP], cwd=ROOT, env=env,
                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
    return p, log


def main():
    os.makedirs(LOGDIR, exist_ok=True)
    open(PROGRESS, "w", encoding="utf-8").close()
    queue = list(jobs())
    total = len(queue)
    note(f"STAGE 2 START | {total} runs | {len(WORLDS)} worlds x {len(ARMS)} arms x {len(SEEDS)} seeds | "
         f"{STEPS} steps, period snapshot at {SNAP} | concurrency {CONCURRENCY}")
    running = []
    done = failed = 0
    t0 = time.time()
    while queue or running:
        while queue and len(running) < CONCURRENCY:
            j = queue.pop(0)
            p, log = launch(j)
            j["t_start"] = time.time()
            running.append((j, p, log))
            note(f"  launch {j['tag']}  ({len(running)} running, {len(queue)} queued)")
        time.sleep(15)
        still = []
        for j, p, log in running:
            rc = p.poll()
            if rc is None:
                still.append((j, p, log))
                continue
            log.close()
            mins = (time.time() - j["t_start"]) / 60
            if rc == 0:
                done += 1
                note(f"  DONE   {j['tag']}  rc=0  {mins:.0f} min  [{done + failed}/{total}]")
            else:
                failed += 1
                note(f"  FAILED {j['tag']}  rc={rc}  {mins:.0f} min  [{done + failed}/{total}] — see stage2_logs")
        running = still
        el = (time.time() - t0) / 60
        fin = done + failed
        if fin:
            note(f"    progress {fin}/{total}  elapsed {el:.0f} min  "
                 f"rough ETA {el / fin * (total - fin):.0f} min") if fin % 3 == 0 else None
    note(f"STAGE 2 FINISHED | {done} ok, {failed} failed | {(time.time() - t0) / 60:.0f} min")


if __name__ == "__main__":
    main()
