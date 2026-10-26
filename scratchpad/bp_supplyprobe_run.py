"""Launch bp_supplyprobe.py on the three canonical worlds in parallel (NEW canon: viable sites + fathers 0.5; seed 0).
Savanna is the target; temperate and montane are the controls. stdin=DEVNULL on every child (WinError 6 otherwise).
Progress -> supplyprobe_progress.txt.
"""
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
PROBE = os.path.join(ROOT, "scratchpad", "bp_supplyprobe.py")
PROG = os.path.join(ROOT, "scratchpad", "supplyprobe_progress.txt")
STEPS = os.environ.get("SPR_STEPS", "6000")
FROM = os.environ.get("SPR_FROM", "3000")
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
               C_WORLD_SEED="0", C_CLIM_SEED="0", C_AGENT_SEED="0", C_TAG=f"_sp_{w}",
               C_GENEA="0", C_GENOME="1", C_LOGEVERY="100",
               SP_FROM=FROM, SP_OUT=os.path.join(ROOT, "scratchpad", f"supplyprobe_{w}.json"))
    log = open(os.path.join(ROOT, "scratchpad", f"supplyprobe_{w}.log"), "w", encoding="utf-8")
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
