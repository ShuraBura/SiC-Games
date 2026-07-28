"""BATTERY 5 — THE ENGINEERED WORLD SET: does the whole setup behave, and does it hit its benchmarks?

Batteries 1-4 test mechanisms. This tests the SYSTEM: a world set chosen so that the model's documented targets
are actually exercised, and so that the headline result is an ORDERING rather than a single number — because an
ordering cannot be hit by tuning one knob.

THE SPINE IS T-7 (docs/TARGETS.md, Smith & Codding 2021, n=89 Pacific-coast HG societies, [VERIFIED]):

    predictor of hierarchy      effect
    Resource Index (STRUCTURE)   0.37     <- should move stratification a LOT
    NPP PRODUCTIVITY             0.04     <- should move it hardly at all

TARGETS.md states the requirement explicitly: "The model must reproduce the ORDERING, not just the existence of
stratification". So the world set is built as two crossed axes, each varying ONE thing:

  AXIS P — PRODUCTIVITY, structure held constant.  flat-boreal -> flat-temperate -> flat-tropical.
           Same diffuse terrain, NPP climbs. T-7 predicts hierarchy barely moves.
  AXIS S — STRUCTURE, productivity held roughly constant.  flat-temperate (diffuse) -> hilly-temperate
           (patchy) -> coastal-temperate (aquatic, patchy AND storable/defensible), plus a defensibility
           ablation on the coastal arm. T-7 predicts hierarchy moves a lot.

HEALTH VERDICT = range(stratification | AXIS S) must exceed range(stratification | AXIS P), by the ordering
T-7 gives. If productivity moves hierarchy more than structure does, the setup contradicts its own anchor.

Read off the SAME runs, against their documented targets:
  band size ~25                    (Johnson scalar stress / R-72)
  settlement median 50-150         (Bar-Yosef; R-63/R-64)
  connubium ~475-500               (Wobst)
  lineage_size_gini 0.51-0.68      (BHM 2009 stratified range; R-103g)
  lineage top_share ~0.16          (T-9, Karmin et al. 2015)
  ascribed_frac vs EA true elite   (3.6-7.8% — the model has run far above this)

NOT scored: %stratified as an absolute level. R-105 retired R-64's "9-16%" after measuring 2.7-12.5% across
seeds with a within-run range of 1.2-25.7. It is used here only as a RELATIVE quantity between arms, which is
what T-7 actually asks for and what survives that seed variance.

RESUMABLE: each arm writes its own trajectory; a completed arm is skipped on re-run. Safe across a restart.

Run:  py -3 -u sic_games/outputs/mechanism_battery/battery5_worldset.py
Env:  B5_STEPS (3000) · B5_SEEDS (0,1) · B5_MAXMIN (75) · B5_PAR (4 concurrent arms)
"""
import json
import os
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAMP = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")

STEPS = os.environ.get("B5_STEPS", "3000")
SEEDS = [s for s in os.environ.get("B5_SEEDS", "0,1").split(",") if s]
MAXMIN = os.environ.get("B5_MAXMIN", "75")
PAR = int(os.environ.get("B5_PAR", "4"))
PROG = os.path.join(HERE, "battery5_progress.txt")
OUT = os.path.join(HERE, "battery5_results.json")

# The live campaign stack + every fix Battery 3 established, so the system under test is the RESUSCITATED one.
STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal",
             C_MATINHERIT="1", C_MATRULE="primogeniture", C_HEIRSTAT="1",
             C_LINTRIBUTE="1", C_TRIBFRAC="0.15", C_NOBLEXEMPT="1")

# (arm, axis, terrain, climate, extra env)
ARMS = [
    ("P_flat_boreal",    "P", "flat",    "boreal",    dict(C_DEFEND="1")),
    ("P_flat_temperate", "P", "flat",    "temperate", dict(C_DEFEND="1")),
    ("P_flat_tropical",  "P", "flat",    "tropical",  dict(C_DEFEND="1")),
    ("S_flat_temperate", "S", "flat",    "temperate", dict(C_DEFEND="1")),   # diffuse  (== P_flat_temperate)
    ("S_hilly_temperate","S", "hilly",   "temperate", dict(C_DEFEND="1")),   # patchy
    ("S_coastal_temp",   "S", "coastal", "temperate", dict(C_DEFEND="1")),   # patchy + storable/defensible
    ("S_coastal_nodefend", "S", "coastal", "temperate", dict(C_DEFEND="0")), # ablate ownership (T-7's 0.13 term)
]

KEYS = ("pop", "pct_stratified", "gini_cred", "band_med", "settle_med", "settle_max", "n_settle",
        "connubium_med", "lineage_size_gini", "lin_top_share", "ascribed_frac",
        "noble_lineage_size_lift", "noble_material_lift", "surplus_med")

# target, low, high, source
TARGETS = {
    "band_med": (25.0, 18.0, 35.0, "Johnson scalar stress / R-72"),
    "settle_med": (100.0, 50.0, 150.0, "Bar-Yosef 50-150; R-63/R-64"),
    "connubium_med": (475.0, 300.0, 700.0, "Wobst ~475"),
    "lineage_size_gini": (0.60, 0.51, 0.68, "BHM 2009 stratified range; R-103g"),
    "lin_top_share": (0.16, 0.08, 0.30, "T-9 Karmin et al. 2015"),
    "ascribed_frac": (0.057, 0.036, 0.078, "EA true-elite 3.6-7.8%"),
}


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


def tag_of(arm, seed):
    return f"_b5_{arm}_s{seed}"


def done(tag):
    """Resume: an arm whose trajectory exists and reached the horizon is skipped."""
    f = os.path.join(CAMP, f"campaign_trajectory{tag}.json")
    if not os.path.exists(f):
        return None
    try:
        d = json.load(open(f, encoding="utf-8"))
        if d.get("traj"):
            return d
    except Exception:
        return None
    return None


def launch(arm, terr, clim, extra, seed):
    tag = tag_of(arm, seed)
    env = dict(os.environ, C_TAG=tag, C_TERR=terr, C_CLIM=clim, C_SEED=str(seed), C_FOUNDERS="3000",
               C_STEPS=STEPS, C_MAXMIN=MAXMIN, C_LOGEVERY="250", C_IMPROVED="0", **STACK, **extra)
    out = open(os.path.join(HERE, f"b5_stdout{tag}.txt"), "w", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-u", os.path.join(CAMP, "run_campaign.py")],
                         cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, text=True)
    return p, out


def sustained(traj, key, frac=0.5):
    """Median over the run's second half — R-65: these are FLUCTUATING quantities, a final snapshot is not
    the statistic."""
    if not traj:
        return None
    cut = traj[-1]["step"] * frac
    v = [r[key] for r in traj if r["step"] >= cut and r.get(key) is not None]
    return round(statistics.median(v), 4) if v else None


def main():
    open(PROG, "a", encoding="utf-8").close()
    log(f"\n=== BATTERY 5 @ {time.strftime('%H:%M')} | {len(ARMS)} arms x {len(SEEDS)} seeds "
        f"| {STEPS} steps | budget {MAXMIN}m | {PAR} concurrent ===")

    todo = [(a, t, c, e, s) for (a, ax, t, c, e) in ARMS for s in SEEDS if not done(tag_of(a, s))]
    skip = len(ARMS) * len(SEEDS) - len(todo)
    if skip:
        log(f"  RESUME: {skip} arm(s) already complete, skipping")

    running = []
    while todo or running:
        while todo and len(running) < PAR:
            arm, terr, clim, extra, seed = todo.pop(0)
            p, out = launch(arm, terr, clim, extra, seed)
            running.append((arm, seed, p, out))
            log(f"  launched {arm} seed {seed}")
        time.sleep(20)
        for item in list(running):
            arm, seed, p, out = item
            if p.poll() is not None:
                out.close(); running.remove(item)
                log(f"  finished {arm} seed {seed} rc={p.returncode}")

    # ── SCORE ───────────────────────────────────────────────────────────────────────────────────
    res = {}
    for arm, ax, *_ in [(a, ax) for (a, ax, t, c, e) in ARMS]:
        vals = {}
        for seed in SEEDS:
            d = done(tag_of(arm, seed))
            if not d:
                continue
            for k in KEYS:
                vals.setdefault(k, []).append(sustained(d["traj"], k))
        res[arm] = {k: (round(statistics.median([x for x in v if x is not None]), 4)
                        if [x for x in v if x is not None] else None) for k, v in vals.items()}
        res[arm]["axis"] = ax

    log("\n=== ARMS (sustained medians over the run's second half, pooled across seeds) ===")
    hdr = f"{'arm':22s} {'ax':3s} " + " ".join(f"{k[:13]:>13s}" for k in KEYS)
    log(hdr)
    for arm, r in res.items():
        log(f"{arm:22s} {r.get('axis','?'):3s} " + " ".join(f"{str(r.get(k)):>13s}" for k in KEYS))

    # T-7: the ORDERING is the headline
    def rng(axis, key):
        v = [r[key] for a, r in res.items() if r.get("axis") == axis and r.get(key) is not None]
        return (max(v) - min(v)) if len(v) > 1 else None

    log("\n=== T-7 HEALTH TEST — structure must move hierarchy more than productivity does ===")
    log("    (Smith & Codding 2021: Resource structure 0.37 vs NPP productivity 0.04)")
    verdicts = {}
    for key in ("pct_stratified", "gini_cred", "lineage_size_gini"):
        p_rng, s_rng = rng("P", key), rng("S", key)
        ok = (p_rng is not None and s_rng is not None and s_rng > p_rng)
        verdicts[key] = dict(productivity_range=p_rng, structure_range=s_rng, ordering_holds=ok)
        log(f"  {key:20s} productivity-range {p_rng}  structure-range {s_rng}  -> "
            f"{'ORDERING HOLDS' if ok else '*** ORDERING VIOLATED / inconclusive ***'}")

    log("\n=== BENCHMARK SCORECARD (per arm, vs documented targets) ===")
    score = {}
    for key, (tgt, lo, hi, src) in TARGETS.items():
        hits = []
        for arm, r in res.items():
            v = r.get(key)
            if v is None:
                continue
            hits.append((arm, v, lo <= v <= hi))
        n_hit = sum(1 for _, _, h in hits if h)
        score[key] = dict(target=tgt, lo=lo, hi=hi, source=src, hits=n_hit, n=len(hits),
                          values={a: v for a, v, _ in hits})
        log(f"  {key:20s} target {tgt} [{lo}-{hi}]  MET in {n_hit}/{len(hits)} arms   ({src})")
        for a, v, h in hits:
            log(f"        {'HIT ' if h else 'miss'} {a:22s} {v}")

    json.dump(dict(arms=res, t7=verdicts, scorecard=score,
                   config=dict(steps=STEPS, seeds=SEEDS, maxmin=MAXMIN, stack=STACK)),
              open(OUT, "w", encoding="utf-8"), indent=1)
    log(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
