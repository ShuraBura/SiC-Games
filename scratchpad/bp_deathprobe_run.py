"""Launch bp_deathprobe.py on the three canonical worlds in parallel (canon config, planet = canonical seed 0).
stdin=DEVNULL on every child: without it Windows raises WinError 6 in this shell. Progress -> deathprobe_progress.txt.
"""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
PROBE = os.path.join(ROOT, "scratchpad", "bp_deathprobe.py")
PROG = os.path.join(ROOT, "scratchpad", "deathprobe_progress.txt")
STEPS = os.environ.get("DPR_STEPS", "6000")
FROM = os.environ.get("DPR_FROM", "3000")
WORLDS = [("temperate", "coastal", "temperate"), ("montane", "mountainous", "savanna"),
          ("savanna", "coastal", "savanna")]


def note(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


open(PROG, "w", encoding="utf-8").close()
procs = []
for w, terr, clim in WORLDS:
    env = dict(os.environ, C_ALLON="1", C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_SEED="0",
               C_WORLD_SEED="0", C_CLIM_SEED="0", C_AGENT_SEED="0", C_TAG=f"_dp_{w}",
               C_GENEA="0", C_GENOME="1", C_LOGEVERY="100",
               DP_FROM=FROM, DP_OUT=os.path.join(ROOT, "scratchpad", f"deathprobe_{w}.json"))
    log = open(os.path.join(ROOT, "scratchpad", f"deathprobe_{w}.log"), "w", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-u", PROBE], cwd=ROOT, env=env,
                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
    procs.append((w, p, log, time.time()))
    note(f"launch {w}  ({STEPS} steps, recording from {FROM})")
while procs:
    time.sleep(20)
    for item in list(procs):
        w, p, log, t0 = item
        if p.poll() is not None:
            log.close()
            note(f"{'DONE  ' if p.returncode == 0 else 'FAILED'} {w}  rc={p.returncode}  {(time.time()-t0)/60:.0f} min")
            procs.remove(item)
note("ALL FINISHED")
