"""Launch the R-106 Add.117 drought test: 3 canonical worlds × 3 paired seeds × 2 drought depths, the canon stack.

Same environment as the Stage-2 driver (`bp_stage2_driver.py`), so seed k reproduces `campaign_trajectory_s2_<world>
_riskvg_s<k>.json` until the drought onset. stdin=DEVNULL on every child (WinError 6). Progress -> drought_progress.txt.
"""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
WRAP = os.path.join(ROOT, "scratchpad", "bp_drought.py")
PROG = os.path.join(ROOT, "scratchpad", "drought_progress.txt")
LOGDIR = os.path.join(ROOT, "scratchpad", "drought_logs")
CONC = int(os.environ.get("DR_CONC", "8"))
STEPS = os.environ.get("DR_STEPS", "12000")
MULTS = [m for m in os.environ.get("DR_MULTS", "0.85,0.70").split(",")]
SEEDS = [int(s) for s in os.environ.get("DR_SEEDS", "0,1,2").split(",")]
WORLDS = [("temperate", "coastal", "temperate"), ("montane", "mountainous", "savanna"),
          ("savanna", "coastal", "savanna")]


def note(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


os.makedirs(LOGDIR, exist_ok=True)
open(PROG, "w", encoding="utf-8").close()
jobs = [(w, t, c, s, m) for (w, t, c) in WORLDS for m in MULTS for s in SEEDS]
note(f"DROUGHT START | {len(jobs)} runs | {STEPS} steps | mults {MULTS} | concurrency {CONC}")
running, done = [], 0
while jobs or running:
    while jobs and len(running) < CONC:
        w, terr, clim, s, m = jobs.pop(0)
        tag = f"_dr_{w}_m{m.replace('.', '')}_s{s}"
        env = dict(os.environ, C_ALLON="1", C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_SEED="0",
                   C_WORLD_SEED="0", C_CLIM_SEED="0", C_AGENT_SEED=str(s), C_TAG=tag, C_GENEA="0",
                   C_GENOME="1", C_LT_SNAP_STEP="7500", DR_MULT=m)
        env.pop("C_EXTRA_ON", None)
        env.pop("C_PARAM", None)
        log = open(os.path.join(LOGDIR, tag.lstrip("_") + ".log"), "w", encoding="utf-8")
        p = subprocess.Popen([sys.executable, "-u", WRAP], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                             stdout=log, stderr=subprocess.STDOUT)
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
note("DROUGHT FINISHED")
