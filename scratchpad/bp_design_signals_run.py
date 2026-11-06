"""Launch the signal measurement: 3 worlds x 2 seeds x 3 arms (control, x0.85, x0.70). stdin=DEVNULL (WinError 6)."""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
WRAP = os.path.join(ROOT, "scratchpad", "bp_design_signals.py")
LOGDIR = os.path.join(ROOT, "scratchpad", "design_logs")
PROG = os.path.join(ROOT, "scratchpad", "design_progress.txt")
os.makedirs(LOGDIR, exist_ok=True)
CONC = int(os.environ.get("DR_CONC", "13"))
STEPS = os.environ.get("DR_STEPS", "1836")
WORLDS = [("temperate", "coastal", "temperate"), ("montane", "mountainous", "savanna"), ("savanna", "coastal", "savanna")]


def note(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


open(PROG, "w", encoding="utf-8").close()
jobs = [(w, t, c, s, m) for (w, t, c) in WORLDS for s in (0, 1) for m in ("1.0", "0.85", "0.70")]
note(f"DSIG START | {len(jobs)} runs | {STEPS} steps | concurrency {CONC}")
running, done = [], 0
while jobs or running:
    while jobs and len(running) < CONC:
        w, terr, clim, s, m = jobs.pop(0)
        tag = f"_dsig_{w}_m{m.replace('.', '')}_s{s}"
        env = dict(os.environ, C_ALLON="1", C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_SEED="0", C_WORLD_SEED="0", C_CLIM_SEED="0",
                   C_AGENT_SEED=str(s), C_TAG=tag, C_GENEA="0", C_GENOME="1", C_LT_SNAP_STEP="900", DR_MULT=m)
        env.pop("C_EXTRA_ON", None)
        env.pop("C_PARAM", None)
        log = open(os.path.join(LOGDIR, tag.lstrip("_") + ".log"), "w", encoding="utf-8")
        p = subprocess.Popen([sys.executable, "-u", WRAP], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        running.append((tag, p, log, time.time()))
        note(f"  launch {tag}")
    time.sleep(20)
    for item in list(running):
        tag, p, log, t0 = item
        if p.poll() is not None:
            log.close()
            running.remove(item)
            done += 1
            note(f"  {'DONE  ' if p.returncode == 0 else 'FAILED'} {tag} rc={p.returncode} {(time.time()-t0)/60:.0f} min [{done}]")
note("DSIG FINISHED")
