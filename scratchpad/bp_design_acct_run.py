"""Launch the food-account measurement: 3 worlds x 2 seeds, control only, one year at equilibrium. stdin=DEVNULL (WinError 6)."""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
WRAP = os.path.join(ROOT, "scratchpad", "bp_design_acct.py")
LOGDIR = os.path.join(ROOT, "scratchpad", "design_logs")
PROG = os.path.join(ROOT, "scratchpad", "design_acct_progress.txt")
STEPS = os.environ.get("DR_STEPS", "1776")
WORLDS = [("temperate", "coastal", "temperate"), ("montane", "mountainous", "savanna"), ("savanna", "coastal", "savanna")]


def note(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


open(PROG, "w", encoding="utf-8").close()
jobs = [(w, t, c, s) for (w, t, c) in WORLDS for s in (0, 1)]
note(f"DACC START | {len(jobs)} runs | {STEPS} steps")
running = []
for w, terr, clim, s in jobs:
    tag = f"_dacc_{w}_s{s}"
    env = dict(os.environ, C_ALLON="1", C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_SEED="0", C_WORLD_SEED="0", C_CLIM_SEED="0",
               C_AGENT_SEED=str(s), C_TAG=tag, C_GENEA="0", C_GENOME="1", C_LT_SNAP_STEP="900")
    env.pop("C_EXTRA_ON", None)
    env.pop("C_PARAM", None)
    log = open(os.path.join(LOGDIR, tag.lstrip("_") + ".log"), "w", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-u", WRAP], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
    running.append((tag, p, log, time.time()))
    note(f"  launch {tag}")
while running:
    time.sleep(20)
    for item in list(running):
        tag, p, log, t0 = item
        if p.poll() is not None:
            log.close()
            running.remove(item)
            note(f"  {'DONE  ' if p.returncode == 0 else 'FAILED'} {tag} rc={p.returncode} {(time.time()-t0)/60:.0f} min")
note("DACC FINISHED")
