"""Launch Stage A of Add.128: 3 worlds x 2 seeds x (flag off control; flag on control, x0.70 one year, x0.70 five years).
To step 3000, shock at step 2400, observers from step 2364. stdin=DEVNULL (WinError 6). Progress: scratchpad/stageA_progress.txt.
"""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
WRAP = os.path.join(ROOT, "scratchpad", "bp_stageA.py")
LOGDIR = os.path.join(ROOT, "scratchpad", "design_logs")
PROG = os.path.join(ROOT, "scratchpad", "stageA_progress.txt")
os.makedirs(LOGDIR, exist_ok=True)
CONC = int(os.environ.get("DR_CONC", "13"))
STEPS = os.environ.get("DR_STEPS", "3000")
ONSET = os.environ.get("DR_ONSET", "2400")
FROM = os.environ.get("DR_FROM", "2364")
SMOKE = os.environ.get("DR_SMOKE")
WORLDS = [("temperate", "coastal", "temperate"), ("montane", "mountainous", "savanna"), ("savanna", "coastal", "savanna")]
ARMS = [("off", "c", "1.0", "12"), ("on", "c", "1.0", "12"), ("on", "y1", "0.70", "12"), ("on", "y5", "0.70", "60")]


def note(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


if not SMOKE:
    open(PROG, "w", encoding="utf-8").close()
jobs = [(w, t, c, s, a) for (w, t, c) in WORLDS for s in (0, 1) for a in ARMS]
if SMOKE:
    jobs = [j for j in jobs if j[0] == "savanna" and j[3] == 0 and j[4][1] == "c"]
note(f"STAGE A START | {len(jobs)} runs | {STEPS} steps | onset {ONSET} | from {FROM} | concurrency {CONC}")
running, done = [], 0
while jobs or running:
    while jobs and len(running) < CONC:
        w, terr, clim, s, (fl, nm, m, ln) = jobs.pop(0)
        tag = f"_{'smoke' if SMOKE else 'vc'}_{w}_{fl}_{nm}_s{s}"
        env = dict(os.environ, C_ALLON="1", C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_SEED="0", C_WORLD_SEED="0", C_CLIM_SEED="0",
                   C_AGENT_SEED=str(s), C_TAG=tag, C_GENEA="0", C_GENOME="1", C_LT_SNAP_STEP=os.environ.get("DR_SNAP", "1200"),
                   DR_MULT=m, DR_LEN=ln, DR_ONSET=ONSET, DR_FROM=FROM)
        env.pop("C_EXTRA_ON", None)
        env.pop("C_PARAM", None)
        if fl == "on":
            env["C_EXTRA_ON"] = "enable_village_ceiling"
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
note("STAGE A FINISHED")
