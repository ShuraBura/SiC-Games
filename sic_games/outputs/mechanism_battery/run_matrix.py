"""MARKER MATRIX RUNNER — re-measure every benchmark on the polygyny-corrected stack, with a watchdog.

WHY NOW: adopting the Marlowe polygyny calibration (60.2% -> 4.2% of married men) invalidates every marker
measured on the old stack. R-77 established the old status->RS was an artefact of the excess, and the same
excess feeds male_rs_gini, lin_top_share and the lineage-size lift behind the wealth-in-people result. Those
numbers have to be re-taken before anything is built on them.

SAFEGUARDS (the previous unattended run lost 4 hours to a stalled arm):
  · WATCHDOG - each arm's progress file is polled; an arm whose STEP COUNT has not advanced in STALL_MIN
    minutes is killed and recorded as STALLED. The last run had two arms sitting at step 200 for four hours
    because the per-step budget check cannot interrupt a single slow step. External progress is the only
    reliable liveness signal.
  · HEARTBEAT - a line every HEARTBEAT_MIN minutes listing every live arm and its current step, so the log
    shows liveness rather than silence.
  · RESUMABLE - completed arms are skipped; re-running continues.
  · Per-arm crash isolation: one arm dying never stops the others.

Run:  py -3 -u sic_games/outputs/mechanism_battery/run_matrix.py
"""
import json
import os
import re
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAMP = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
PROG = os.path.join(HERE, "matrix_progress.txt")
OUT = os.path.join(HERE, "matrix_results.json")

STEPS = os.environ.get("M_STEPS", "3000")
SEEDS = [s for s in os.environ.get("M_SEEDS", "0,1,2,3,4").split(",") if s]
PAR = int(os.environ.get("M_PAR", "6"))
MAXMIN = os.environ.get("M_MAXMIN", "100")
STALL_MIN = float(os.environ.get("M_STALL", "25"))        # no step advance for this long => kill
HEARTBEAT_MIN = float(os.environ.get("M_HEARTBEAT", "10"))

STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal",
             C_MATINHERIT="1", C_MATRULE="primogeniture", C_HEIRSTAT="1",
             C_LINTRIBUTE="1", C_TRIBFRAC="0.15", C_NOBLEXEMPT="1", C_DEFEND="1",
             C_BUD="1", C_BUDHAZ="1")

# SPLIT STRATEGY (supervisor's call): depth on the markers that are FAILING, breadth on those that pass.
# Depth = coastal/flat temperate at all seeds (where the elite markers are measurable);
# breadth = the remaining biomes at 2 seeds, enough to show a passing marker still passes.
DEPTH = [("coastal_temperate", "coastal", "temperate"), ("flat_temperate", "flat", "temperate")]
BREADTH = [("flat_tropical", "flat", "tropical"), ("hilly_temperate", "hilly", "temperate"),
           ("flat_boreal", "flat", "boreal")]

STEP_RE = re.compile(r"\[\s*(\d+)/")
_HEAD = ""   # set in __main__ once git is available


def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(line + "\n"); f.flush()
    print(line, flush=True)


def arm_step(tag):
    """Current step from the arm's own progress file — the only liveness signal that cannot lie."""
    p = os.path.join(CAMP, f"campaign_progress{tag}.txt")
    if not os.path.exists(p):
        return 0
    try:
        lines = [l for l in open(p, encoding="utf-8", errors="ignore") if l.startswith("[")]
        if not lines:
            return 0
        m = STEP_RE.search(lines[-1])
        return int(m.group(1)) if m else 0
    except Exception:
        return 0


def _head_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


def done(tag):
    """An arm counts as complete only if it was produced by THE CURRENT CODE.

    Existence is not enough. A run killed mid-way was resumed against trajectories written before three
    branches landed (markers, polarization, obligation), which would have silently mixed two different
    stacks into one scorecard. The campaign already records its build in `meta.sha`, so the resume check
    compares it against HEAD and re-runs anything stale."""
    p = os.path.join(CAMP, f"campaign_trajectory{tag}.json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    if not d.get("traj"):
        return None
    sha = (d.get("meta") or {}).get("sha", "")
    if _HEAD and sha and not sha.startswith(_HEAD) and not _HEAD.startswith(sha):
        return None                      # produced by a different build ⇒ not reusable
    return d


def sustained(t, key, frac=0.5):
    if not t:
        return None
    cut = t[-1]["step"] * frac
    v = [r[key] for r in t if r["step"] >= cut and r.get(key) is not None]
    return round(statistics.median(v), 4) if v else None


def run(arms):
    todo = [a for a in arms if done(a[0]) is None]
    if len(todo) < len(arms):
        log(f"resume: {len(arms) - len(todo)} arm(s) already complete")
    live, stalled, t_beat = [], [], time.time()
    while todo or live:
        while todo and len(live) < PAR:
            tag, over = todo.pop(0)
            env = dict(os.environ, C_TAG=tag, C_FOUNDERS="3000", C_STEPS=STEPS, C_MAXMIN=MAXMIN,
                       C_LOGEVERY="250", C_IMPROVED="0", **STACK, **over)
            out = open(os.path.join(HERE, f"mx_stdout{tag}.txt"), "w", encoding="utf-8")
            p = subprocess.Popen([sys.executable, "-u", os.path.join(CAMP, "run_campaign.py")],
                                 cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, text=True)
            live.append(dict(tag=tag, p=p, out=out, step=0, t_last=time.time()))
            log(f"  launched {tag}")
        time.sleep(20)
        now = time.time()
        for it in list(live):
            if it["p"].poll() is not None:
                it["out"].close(); live.remove(it)
                log(f"  finished {it['tag']} rc={it['p'].returncode} at step {arm_step(it['tag'])}")
                continue
            s = arm_step(it["tag"])
            if s > it["step"]:
                it["step"], it["t_last"] = s, now
            elif (now - it["t_last"]) / 60.0 > STALL_MIN:
                # WATCHDOG. A single slow step cannot be interrupted from inside the run, so it is killed here.
                log(f"  *** STALLED {it['tag']} — no step advance for {STALL_MIN:.0f}m at step {s}. KILLING.")
                try:
                    it["p"].kill()
                except Exception:
                    pass
                it["out"].close(); live.remove(it); stalled.append(it["tag"])
        if (now - t_beat) / 60.0 >= HEARTBEAT_MIN:
            t_beat = now
            log("  heartbeat | " + " · ".join(f"{i['tag'][4:]}@{i['step']}" for i in live)
                + f" | queued {len(todo)}")
    return stalled


if __name__ == "__main__":
    globals()["_HEAD"] = _head_sha()
    open(PROG, "a", encoding="utf-8").close()
    t0 = time.time()
    log("=" * 70)
    log(f"MARKER MATRIX — build {_HEAD} | polygyny corrected, markers wired, polarization + obligation in")
    log(f"  depth {[d[0] for d in DEPTH]} x {len(SEEDS)} seeds | breadth {[b[0] for b in BREADTH]} x 2 seeds")
    log(f"  watchdog: kill an arm after {STALL_MIN:.0f}m without a step; heartbeat every {HEARTBEAT_MIN:.0f}m")

    arms = [(f"_mx_{nm}_s{sd}", dict(C_TERR=t, C_CLIM=c, C_SEED=sd))
            for (nm, t, c) in DEPTH for sd in SEEDS]
    arms += [(f"_mx_{nm}_s{sd}", dict(C_TERR=t, C_CLIM=c, C_SEED=sd))
             for (nm, t, c) in BREADTH for sd in SEEDS[:2]]
    stalled = run(arms)

    KEYS = ("pop", "band_med", "settle_med", "settle_max", "n_settle", "connubium_med",
            "lineage_size_gini", "lin_top_share", "ascribed_frac", "pct_stratified", "gini_cred",
            "noble_lineage_size_lift", "noble_material_lift", "male_rs_gini", "primate_ratio",
            "zipf_slope", "bud_events", "surplus_med")
    R = {"stalled": stalled, "arms": {}}
    for tag, _ in arms:
        d = done(tag)
        if d:
            R["arms"][tag] = {k: sustained(d["traj"], k) for k in KEYS}
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)

    log("\n=== MARKER MATRIX (sustained medians, second half of each run) ===")
    hdr = f"{'arm':26s} " + " ".join(f"{k[:12]:>12}" for k in KEYS)
    log(hdr)
    for tag, vals in R["arms"].items():
        log(f"{tag[4:]:26s} " + " ".join(f"{str(vals.get(k)):>12}" for k in KEYS))
    if stalled:
        log(f"\nSTALLED (killed by watchdog): {stalled}")
    log(f"\nDONE in {(time.time() - t0) / 3600:.2f} h -> {OUT}")
