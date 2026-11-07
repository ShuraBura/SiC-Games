"""Launch the Add.130 per-village log: 3 worlds x 2 seeds x flag off and on, control only, to step 3000, observer from step 1800.
stdin=DEVNULL (WinError 6). Progress: scratchpad/vlog_progress.txt. DR_SMOKE=1 runs savanna, flag on, seed 0.
"""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
WRAP = os.path.join(ROOT, "scratchpad", "bp_vlog.py")
LOGDIR = os.path.join(ROOT, "scratchpad", "design_logs")
PROG = os.path.join(ROOT, "scratchpad", "vlog_progress.txt")
os.makedirs(LOGDIR, exist_ok=True)
CONC = int(os.environ.get("DR_CONC", "12"))
STEPS = os.environ.get("DR_STEPS", "3000")
FROM = os.environ.get("DR_FROM", "1800")
SMOKE = os.environ.get("DR_SMOKE")
WORLDS = [("temperate", "coastal", "temperate"), ("montane", "mountainous", "savanna"), ("savanna", "coastal", "savanna")]


def note(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


if not SMOKE:
    open(PROG, "w", encoding="utf-8").close()
jobs = [(w, t, c, s, fl) for (w, t, c) in WORLDS for s in (0, 1) for fl in ("off", "on")]
if SMOKE:
    jobs = [j for j in jobs if j[0] == "savanna" and j[3] == 0 and j[4] == "on"]
note(f"VLOG START | {len(jobs)} runs | {STEPS} steps | from {FROM} | concurrency {CONC}")
running, done = [], 0
while jobs or running:
    while jobs and len(running) < CONC:
        w, terr, clim, s, fl = jobs.pop(0)
        tag = f"_{'vsm' if SMOKE else 'vl'}_{w}_{fl}_s{s}"
        env = dict(os.environ, C_ALLON="1", C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_SEED="0", C_WORLD_SEED="0", C_CLIM_SEED="0",
                   C_AGENT_SEED=str(s), C_TAG=tag, C_GENEA="0", C_GENOME="1", C_LT_SNAP_STEP=os.environ.get("DR_SNAP", "1200"), DR_FROM=FROM)
        env.pop("C_EXTRA_ON", None)
        env.pop("C_PARAM", None)
        if fl == "on":
            env["C_EXTRA_ON"] = "enable_village_ceiling"
        log = open(os.path.join(LOGDIR, tag.lstrip("_") + ".log"), "w", encoding="utf-8")
        p = subprocess.Popen([sys.executable, "-u", WRAP], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        running.append((tag, p, log, time.time()))
        note(f"  launch {tag}")
    time.sleep(10 if SMOKE else 20)
    for item in list(running):
        tag, p, log, t0 = item
        if p.poll() is not None:
            log.close()
            running.remove(item)
            done += 1
            note(f"  {'DONE  ' if p.returncode == 0 else 'FAILED'} {tag} rc={p.returncode} {(time.time()-t0)/60:.0f} min [{done}]")
note("VLOG FINISHED")
