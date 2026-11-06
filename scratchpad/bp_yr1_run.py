"""Launch R-106 Add.127: 3 canonical worlds x 3 paired seeds, the canon stack, 20 one-year shocks in each run.
Same environment as bp_drought_run.py, so seed k reproduces campaign_trajectory_s2_<world>_pair_s<k> until the first
shock. stdin=DEVNULL on every child (WinError 6). Progress -> scratchpad/yr1_progress.txt.
"""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
WRAP = os.path.join(ROOT, "scratchpad", "bp_yr1.py")
PROG = os.path.join(ROOT, "scratchpad", "yr1_progress.txt")
LOGDIR = os.path.join(ROOT, "scratchpad", "drought_logs")
CONC = int(os.environ.get("DR_CONC", "9"))
STEPS = os.environ.get("DR_STEPS", "13800")
SEEDS = [int(s) for s in os.environ.get("DR_SEEDS", "0,1,2").split(",")]
WORLDS = [("temperate", "coastal", "temperate"), ("montane", "mountainous", "savanna"),
          ("savanna", "coastal", "savanna")]


def note(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


open(PROG, "w", encoding="utf-8").close()
jobs = [(w, t, c, s) for (w, t, c) in WORLDS for s in SEEDS]
note(f"YR1 START | {len(jobs)} runs | {STEPS} steps | concurrency {CONC}")
running, done = [], 0
while jobs or running:
    while jobs and len(running) < CONC:
        w, terr, clim, s = jobs.pop(0)
        tag = f"_yr1_{w}_s{s}"
        env = dict(os.environ, C_ALLON="1", C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_SEED="0", C_WORLD_SEED="0",
                   C_CLIM_SEED="0", C_AGENT_SEED=str(s), C_TAG=tag, C_GENEA="0", C_GENOME="1", C_LT_SNAP_STEP="7500")
        env.pop("C_EXTRA_ON", None)
        env.pop("C_PARAM", None)
        log = open(os.path.join(LOGDIR, tag.lstrip("_") + ".log"), "w", encoding="utf-8")
        p = subprocess.Popen([sys.executable, "-u", WRAP], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log,
                             stderr=subprocess.STDOUT)
        running.append((tag, p, log, time.time()))
        note(f"  launch {tag}  ({len(running)} running, {len(jobs)} queued)")
    time.sleep(30)
    for item in list(running):
        tag, p, log, t0 = item
        if p.poll() is not None:
            log.close()
            running.remove(item)
            done += 1
            note(f"  {'DONE  ' if p.returncode == 0 else 'FAILED'} {tag}  rc={p.returncode}  {(time.time()-t0)/60:.0f} min  [{done}]")
note("YR1 FINISHED")
