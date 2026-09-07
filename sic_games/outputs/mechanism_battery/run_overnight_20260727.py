"""UNATTENDED RUN — 2026-07-27. Four stages, ~10.5 h minimum. Plan + PRE-REGISTERED predictions in
`PLAN_overnight_2026-07-27.md`; read that first, it was written before any of this executed.

Robustness rules, because nobody is watching:
  · every stage is wrapped — a stage that crashes is logged and the next one starts. No stage blocks another.
  · every arm checkpoints; completed arms are SKIPPED on re-run, so a machine restart resumes rather than
    restarting. Re-running this file is always safe.
  · progress is flushed to `overnight_progress.txt` after every event, so the state is readable at any moment.
  · no population cap anywhere (standing instruction: a cap would hide the phenomenon).
"""
import json
import os
import statistics
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAMP = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
PROG = os.path.join(HERE, "overnight_progress.txt")
RESULTS = os.path.join(HERE, "overnight_results.json")

STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal",
             C_MATINHERIT="1", C_MATRULE="primogeniture", C_HEIRSTAT="1",
             C_LINTRIBUTE="1", C_TRIBFRAC="0.15", C_NOBLEXEMPT="1", C_DEFEND="1")

R: dict = {}


def log(m):
    line = f"[{time.strftime('%H:%M')}] {m}"
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(line + "\n"); f.flush()
    print(line, flush=True)
    with open(RESULTS, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def traj(tag):
    p = os.path.join(CAMP, f"campaign_trajectory{tag}.json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
        return d if d.get("traj") else None
    except Exception:
        return None


def sustained(t, key, frac=0.5):
    if not t:
        return None
    cut = t[-1]["step"] * frac
    v = [r[key] for r in t if r["step"] >= cut and r.get(key) is not None]
    return round(statistics.median(v), 4) if v else None


def run_arms(arms, par, steps, maxmin, logevery="250"):
    """arms = list of (tag, env_overrides). Skips completed, runs `par` at a time."""
    todo = [(t, e) for (t, e) in arms if traj(t) is None]
    if len(todo) < len(arms):
        log(f"    resume: {len(arms) - len(todo)} arm(s) already complete")
    running = []
    while todo or running:
        while todo and len(running) < par:
            tag, over = todo.pop(0)
            env = dict(os.environ, C_TAG=tag, C_FOUNDERS="3000", C_STEPS=str(steps),
                       C_MAXMIN=str(maxmin), C_LOGEVERY=logevery, C_IMPROVED="0", **STACK, **over)
            out = open(os.path.join(HERE, f"ov_stdout{tag}.txt"), "w", encoding="utf-8")
            running.append((tag, subprocess.Popen(
                [sys.executable, "-u", os.path.join(CAMP, "run_campaign.py")],
                cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, text=True), out))
            log(f"    launched {tag}")
        time.sleep(20)
        for item in list(running):
            tag, p, out = item
            if p.poll() is not None:
                out.close(); running.remove(item)
                log(f"    finished {tag} rc={p.returncode}")


# ── STAGE A1 — interference null ────────────────────────────────────────────────────────────────
def stage_a1():
    log("STAGE A1 — interference null distribution (5 seeds)")
    seeds, per_seed = [0, 1, 2, 3, 4], {}
    for sd in seeds:
        env = dict(os.environ, B4_WORKERS="4", B4_STEPS="400", PYTHONIOENCODING="utf-8", B_SEED=str(sd))
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "battery4_interference.py")],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        src = os.path.join(HERE, "battery4_results.json")
        if r.returncode != 0 or not os.path.exists(src):
            log(f"    seed {sd} FAILED rc={r.returncode}"); continue
        d = json.load(open(src, encoding="utf-8"))
        dst = os.path.join(HERE, f"battery4_results_s{sd}.json")
        json.dump(d, open(dst, "w", encoding="utf-8"), indent=1)
        per_seed[sd] = {tuple(row["off"]): row.get("dist") for row in d["rows"] if "dist" in row}
        log(f"    seed {sd} done ({len(per_seed[sd])} combinations)")

    # A candidate SURVIVES only if its sub-additivity exceeds the between-seed spread of the same quantity.
    survivors = []
    if len(per_seed) >= 3:
        keys = set.intersection(*(set(v) for v in per_seed.values()))
        singles = {k[0]: [per_seed[s][k] for s in per_seed] for k in keys if len(k) == 1}
        for k in sorted(kk for kk in keys if len(kk) == 2):
            a, b = k
            if a not in singles or b not in singles:
                continue
            dab = [per_seed[s][k] for s in per_seed]
            deficit = [max(singles[a][i], singles[b][i]) - dab[i] for i in range(len(dab))]
            m = statistics.mean(deficit)
            sd_ = statistics.pstdev(deficit)
            if m > 0 and m > 2 * sd_:                     # deficit exceeds its own between-seed spread
                survivors.append((a, b, round(m, 3), round(sd_, 3)))
    R["A1_survivors"] = [dict(a=a, b=b, mean_deficit=m, sd=s) for a, b, m, s in survivors]
    R["A1_n_seeds"] = len(per_seed)
    log(f"  A1 RESULT: {len(survivors)} of 18 candidate pairs survive the null "
        f"(PREDICTED: fewer than 5)")
    for a, b, m, s in survivors[:10]:
        log(f"      {a[7:]} + {b[7:]}  deficit {m} +/- {s}")


# ── STAGE A2 — ascribed_frac calibration ────────────────────────────────────────────────────────
def stage_a2():
    log("STAGE A2 — ascribed_frac sweep vs EA true-elite 3.6-7.8%")
    arms = [(f"_ov_asc_t{str(t).replace('.', '')}_s{sd}",
             dict(C_TERR="coastal", C_CLIM="temperate", C_SEED=str(sd), C_LEGITTHR=str(t), C_BUD="1"))
            for t in (0.15, 0.25, 0.40, 0.60) for sd in (0, 1)]
    run_arms(arms, par=4, steps=3000, maxmin=90)
    rows = []
    for t in (0.15, 0.25, 0.40, 0.60):
        af, lift = [], []
        for sd in (0, 1):
            d = traj(f"_ov_asc_t{str(t).replace('.', '')}_s{sd}")
            if not d:
                continue
            af.append(sustained(d["traj"], "ascribed_frac"))
            lift.append(sustained(d["traj"], "noble_lineage_size_lift"))
        af = [x for x in af if x is not None]; lift = [x for x in lift if x is not None]
        if not af:
            continue
        a_med, l_med = statistics.median(af), (statistics.median(lift) if lift else None)
        in_band = 0.036 <= a_med <= 0.078
        elite_alive = l_med is not None and l_med > 2.0
        rows.append(dict(legit_threshold=t, ascribed_frac=a_med, lineage_lift=l_med,
                         in_EA_band=in_band, elite_survives=elite_alive, PASS=bool(in_band and elite_alive)))
        log(f"    legit_threshold {t}: ascribed_frac {a_med} "
            f"({'IN BAND' if in_band else 'out'}), lineage lift {l_med} "
            f"({'elite alive' if elite_alive else 'ELITE GONE'})")
    R["A2"] = rows
    ok = [r for r in rows if r["PASS"]]
    log(f"  A2 RESULT: {len(ok)} setting(s) hit the EA band WITH the elite intact "
        f"(PREDICTED: 0 — the two targets are in tension)")


# ── STAGE B — budding A/B on the engineered world set ───────────────────────────────────────────
WORLDS = [("P_flat_boreal", "flat", "boreal"), ("P_flat_temperate", "flat", "temperate"),
          ("P_flat_tropical", "flat", "tropical"), ("S_hilly_temperate", "hilly", "temperate"),
          ("S_coastal_temp", "coastal", "temperate")]


def stage_b():
    log("STAGE B — budding A/B on the engineered world set")
    arms = [(f"_ov_b5_{nm}_bud{b}_s{sd}",
             dict(C_TERR=terr, C_CLIM=clim, C_SEED=str(sd), C_BUD=str(b)))
            for (nm, terr, clim) in WORLDS for b in (0, 1) for sd in (0, 1)]
    run_arms(arms, par=6, steps=3000, maxmin=90)
    out = {}
    for (nm, terr, clim) in WORLDS:
        for b in (0, 1):
            vals = {}
            for sd in (0, 1):
                d = traj(f"_ov_b5_{nm}_bud{b}_s{sd}")
                if not d:
                    continue
                for k in ("pop", "band_med", "settle_med", "settle_max", "n_settle", "connubium_med",
                          "lineage_size_gini", "lin_top_share", "ascribed_frac", "pct_stratified",
                          "gini_cred", "noble_lineage_size_lift"):
                    vals.setdefault(k, []).append(sustained(d["traj"], k))
            out[f"{nm}_bud{b}"] = {k: (round(statistics.median([x for x in v if x is not None]), 4)
                                       if [x for x in v if x is not None] else None)
                                   for k, v in vals.items()}
    R["B"] = out
    log("  B RESULT (sustained medians):")
    for k, v in out.items():
        log(f"      {k:28s} settle_med {v.get('settle_med')} n_settle {v.get('n_settle')} "
            f"band {v.get('band_med')} top_share {v.get('lin_top_share')} asc {v.get('ascribed_frac')}")
    # the headline: does budding move settlement size toward the ethnographic band without breaking a rung?
    for (nm, _, _) in WORLDS:
        off, on = out.get(f"{nm}_bud0", {}), out.get(f"{nm}_bud1", {})
        if off.get("settle_med") and on.get("settle_med"):
            log(f"      {nm}: settle_med {off['settle_med']} -> {on['settle_med']}, "
                f"n_settle {off.get('n_settle')} -> {on.get('n_settle')}, "
                f"band {off.get('band_med')} -> {on.get('band_med')}")


# ── STAGE C — deep time on the repaired substrate ───────────────────────────────────────────────
def stage_c(budget_min):
    log(f"STAGE C — deep time, budding ON, {budget_min}m per arm, LOGEVERY=100")
    arms = [(f"_ov_deep_s{sd}", dict(C_TERR="coastal", C_CLIM="temperate", C_SEED=str(sd), C_BUD="1"))
            for sd in (0, 1)]
    run_arms(arms, par=2, steps=30000, maxmin=budget_min, logevery="100")
    for sd in (0, 1):
        d = traj(f"_ov_deep_s{sd}")
        if not d:
            continue
        t = d["traj"]
        R[f"C_s{sd}"] = dict(steps=d["meta"].get("steps_completed"), snapshots=len(t),
                             pop=sustained(t, "pop"), lift=sustained(t, "noble_lineage_size_lift"),
                             strat=sustained(t, "pct_stratified"), settle=sustained(t, "settle_med"))
        log(f"    seed {sd}: {d['meta'].get('steps_completed')} steps, {len(t)} snapshots, "
            f"pop {sustained(t, 'pop')}, lineage lift {sustained(t, 'noble_lineage_size_lift')}, "
            f"strat {sustained(t, 'pct_stratified')}%")
    log("    NOTE: no cycle verdict is emitted here. Per R-97's D1 rule the detector must first be "
        "re-validated at 100-step spacing; that analysis is a separate, deliberate step.")


if __name__ == "__main__":
    t0 = time.time()
    log("=" * 70)
    log("UNATTENDED RUN 2026-07-27 — plan + pre-registered predictions in PLAN_overnight_2026-07-27.md")
    for name, fn in (("A1", stage_a1), ("A2", stage_a2), ("B", stage_b)):
        try:
            fn()
        except Exception as e:
            log(f"  *** STAGE {name} CRASHED: {type(e).__name__}: {e}")
            log(traceback.format_exc()[-800:])
        log(f"  elapsed {(time.time() - t0) / 3600:.1f} h")
    # Stage C takes whatever is left, so an overrun upstream shortens deep time rather than skipping it.
    left = max(60.0, 10.0 * 60 - (time.time() - t0) / 60.0)
    try:
        stage_c(int(min(left / 2, 240)))
    except Exception as e:
        log(f"  *** STAGE C CRASHED: {type(e).__name__}: {e}")
    log(f"DONE in {(time.time() - t0) / 3600:.1f} h -> {RESULTS}")
