"""BATTERY 6, LONG STAGES — S4 benchmark envelope + S6 long-horizon drift. Design in DESIGN_stress_battery.md.

S4  BENCHMARK ENVELOPE. Batteries scored targets pass/fail at ONE configuration. R-65 documented 30x seed
    variance in %stratified, so a single point cannot distinguish "the model misses this target" from "this
    seed missed it". Here every benchmark gets a PASS FRACTION across worlds x seeds and the conditions under
    which it fails.

    THE ANCHOR GUARD. Every band is re-verified against the docs AT RUN TIME, and a benchmark whose anchor has
    been retired or struck is SKIPPED WITH A NOTE rather than scored. This exists because Battery 5 scored
    connubium 0/7 against "Wobst ~475" — a target LITERATURE.md had retired two weeks earlier as an
    extrapolation. Scoring a stale number is worse than not scoring it: it manufactures a defect.

S6  LONG-HORIZON DRIFT. 30,000 steps. R-105's runaway sat quiet for 1750 steps before tipping, so any battery
    that stops at 400 is structurally blind to late-onset instability. Flags any tracked quantity that grows
    without bound or goes flat-then-explodes.

Resumable: completed arms are skipped, so a restart continues. Crash-wrapped per stage.

Run:  py -3 -u sic_games/outputs/mechanism_battery/battery6_long.py
"""
import json
import os
import re
import statistics
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAMP = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
DOCS = os.path.join(ROOT, "docs")
PROG = os.path.join(HERE, "battery6_long_progress.txt")
OUT = os.path.join(HERE, "battery6_long_results.json")

STEPS_S4 = os.environ.get("L_STEPS", "3000")
SEEDS = [s for s in os.environ.get("L_SEEDS", "0,1,2,3,4").split(",") if s]
PAR = int(os.environ.get("L_PAR", "6"))
MAXMIN = os.environ.get("L_MAXMIN", "90")

STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal",
             C_MATINHERIT="1", C_MATRULE="primogeniture", C_HEIRSTAT="1",
             C_LINTRIBUTE="1", C_TRIBFRAC="0.15", C_NOBLEXEMPT="1", C_DEFEND="1",
             C_BUD="1", C_BUDHAZ="1")

WORLDS = [("flat_boreal", "flat", "boreal"), ("flat_temperate", "flat", "temperate"),
          ("flat_tropical", "flat", "tropical"), ("hilly_temperate", "hilly", "temperate"),
          ("coastal_temperate", "coastal", "temperate")]

# key, target, lo, hi, source, ANCHOR PROBE (substring that must still be live in docs/)
BENCH = [
    ("band_med", 25, 18, 35, "Johnson scalar stress / R-72", "repulsion_midpoint"),
    ("settle_med", 100, 50, 150, "Bar-Yosef 50-150; R-63/R-64", "Bar-Yosef"),
    ("settle_med", 150, 50, 250, "Alvard 2009 village 50-250", "50 to ~250"),
    ("connubium_med", 150, 79, 332, "White 2017 MVP ~150; Wobst simulated MES 79-332",
     "minimum viable population"),
    ("lineage_size_gini", 0.60, 0.51, 0.68, "BHM 2009 stratified range", "BHM 2009"),
    ("lin_top_share", 0.16, 0.08, 0.30, "T-9 Karmin et al. 2015", "Karmin"),
    # DELIBERATELY LEFT UNVERIFIABLE. docs/ record only "EA true-elite few %" - the precise 3.6-7.8% band
    # this project has been scoring against is NOT documented anywhere in docs/. The guard therefore skips
    # it, which is the correct outcome: an undocumented band cannot be checked by anyone, and scoring
    # against it would manufacture a defect exactly as the retired Wobst 475 did. File the EA source with
    # its numbers and this benchmark starts scoring on its own.
    ("ascribed_frac", 0.057, 0.036, 0.078, "EA true-elite 3.6-7.8%", "3.6-7.8"),
]


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M')}] {m}\n"); f.flush()
    print(m, flush=True)


def _docs_text():
    t = ""
    for fn in ("LITERATURE.md", "TARGETS.md", "PARAMETERS.md"):
        p = os.path.join(DOCS, fn)
        if os.path.exists(p):
            t += open(p, encoding="utf-8", errors="ignore").read()
    return t


def anchor_live(probe, text):
    """Is this benchmark's anchor still current?

    VERBATIM QUOTE, not proximity to a keyword. The first version of this guard searched for words like
    "RETIRED" near the anchor and FAILED ITS OWN CONTROL TEST in both directions: it skipped the live
    connubium anchor (White's MVP) and would have SCORED the retired Wobst 475, because that retirement is
    worded "[CORRECTION 2026-07-13 ...]" and contains no keyword from the list.

    So each benchmark now carries a distinctive substring of the sentence that states its CURRENT anchor. If
    the anchor is retired, whoever retires it edits that sentence and this check fires. A band whose quote
    cannot be found is SKIPPED, not scored - an unverifiable band is worse than no band, because scoring a
    stale number manufactures a defect (Battery 5 reported connubium 0/7 against exactly such a number)."""
    if probe in text:
        return True, ""
    return False, (f"anchor quote {probe!r} no longer present in docs/ — the source may have been revised or "
                   f"retired; not scored until the band is re-derived")


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
    todo = [(t, e) for (t, e) in arms if traj(t) is None]
    if len(todo) < len(arms):
        log(f"    resume: {len(arms)-len(todo)} arm(s) already complete")
    running = []
    while todo or running:
        while todo and len(running) < par:
            tag, over = todo.pop(0)
            env = dict(os.environ, C_TAG=tag, C_FOUNDERS="3000", C_STEPS=str(steps), C_MAXMIN=str(maxmin),
                       C_LOGEVERY=logevery, C_IMPROVED="0", **STACK, **over)
            out = open(os.path.join(HERE, f"b6l_stdout{tag}.txt"), "w", encoding="utf-8")
            running.append((tag, subprocess.Popen(
                [sys.executable, "-u", os.path.join(CAMP, "run_campaign.py")],
                cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, text=True), out))
            log(f"    launched {tag}")
        time.sleep(20)
        for it in list(running):
            tag, p, o = it
            if p.poll() is not None:
                o.close(); running.remove(it)
                log(f"    finished {tag} rc={p.returncode}")


def stage_s4(R):
    log("S4 — BENCHMARK ENVELOPE (%d worlds x %d seeds)" % (len(WORLDS), len(SEEDS)))
    text = _docs_text()
    live, skipped = [], []
    for b in BENCH:
        ok, why = anchor_live(b[5], text)
        (live if ok else skipped).append((b, why))
    for (b, why) in skipped:
        log(f"    SKIPPED benchmark '{b[0]}' ({b[4]}): {why}")
    R["S4_skipped"] = [dict(key=b[0], source=b[4], reason=w) for (b, w) in skipped]

    arms = [(f"_b6_{nm}_s{sd}", dict(C_TERR=terr, C_CLIM=clim, C_SEED=sd))
            for (nm, terr, clim) in WORLDS for sd in SEEDS]
    run_arms(arms, PAR, STEPS_S4, MAXMIN)

    vals = {}
    for (nm, terr, clim) in WORLDS:
        for sd in SEEDS:
            d = traj(f"_b6_{nm}_s{sd}")
            if not d:
                continue
            for (b, _) in live:
                vals.setdefault(b[0] + "|" + b[4], []).append((nm, sustained(d["traj"], b[0])))

    log("\n    BENCHMARK ENVELOPE — pass fraction across arms")
    score = []
    for (b, _) in live:
        key, tgt, lo, hi, src, _p = b
        got = [(nm, v) for nm, v in vals.get(key + "|" + src, []) if v is not None]
        if not got:
            continue
        hits = [(nm, v) for nm, v in got if lo <= v <= hi]
        by_world = {}
        for nm, v in got:
            by_world.setdefault(nm, []).append(v)
        fails = sorted({nm for nm, v in got if not (lo <= v <= hi)})
        score.append(dict(key=key, source=src, band=[lo, hi], n=len(got), hits=len(hits),
                          fraction=round(len(hits) / len(got), 3),
                          range=[round(min(v for _, v in got), 4), round(max(v for _, v in got), 4)],
                          fails_in=fails))
        log(f"      {key:20s} {len(hits):2d}/{len(got):2d} in [{lo}-{hi}] | observed "
            f"{min(v for _, v in got):.4g}..{max(v for _, v in got):.4g} | misses: "
            f"{', '.join(fails) if fails else 'none'}   ({src})")
    R["S4"] = score

    # T-7 ORDERING: structure must move hierarchy more than productivity does.
    def rng(names, key):
        v = [sustained(traj(f"_b6_{n}_s{sd}")["traj"], key)
             for n in names for sd in SEEDS if traj(f"_b6_{n}_s{sd}")]
        v = [x for x in v if x is not None]
        return (max(v) - min(v)) if len(v) > 1 else None
    prod = ["flat_boreal", "flat_temperate", "flat_tropical"]        # productivity axis, structure held
    struct = ["flat_temperate", "hilly_temperate", "coastal_temperate"]  # structure axis, productivity held
    log("\n    T-7 (Smith & Codding: structure 0.37 vs productivity 0.04)")
    t7 = {}
    for key in ("pct_stratified", "lineage_size_gini", "gini_cred"):
        p, s = rng(prod, key), rng(struct, key)
        holds = (p is not None and s is not None and s > p)
        t7[key] = dict(productivity_range=p, structure_range=s, ordering_holds=holds)
        log(f"      {key:20s} productivity {p} vs structure {s} -> "
            f"{'HOLDS' if holds else 'VIOLATED/inconclusive'}")
    R["S4_t7"] = t7

    # Bandy fission rate, now that the campaign records bud_events
    rates = []
    for (nm, _, _) in WORLDS:
        for sd in SEEDS:
            d = traj(f"_b6_{nm}_s{sd}")
            if not d:
                continue
            last = d["traj"][-1]
            ev = last.get("bud_events")
            if ev is None:
                continue
            yrs = last["step"] / 12.0
            nv = max(1, last.get("n_settle") or 1)
            rates.append(ev / (yrs * nv))
    if rates:
        med = statistics.median(rates)
        R["S4_fission_rate"] = dict(median=med, n=len(rates), band=[0.002, 0.005],
                                    in_band=0.002 <= med <= 0.005)
        log(f"\n    fission rate {med:.2e} per settlement-year (Bandy anchor 2-5e-3) "
            f"-> {'IN BAND' if 0.002 <= med <= 0.005 else 'out of band'}")


def stage_s6(R, budget):
    log(f"S6 — LONG-HORIZON DRIFT (30k steps, budget {budget}m/arm)")
    arms = [(f"_b6_drift_s{sd}", dict(C_TERR="coastal", C_CLIM="temperate", C_SEED=sd)) for sd in ("0", "1")]
    run_arms(arms, 2, 30000, budget, logevery="100")
    out = {}
    for sd in ("0", "1"):
        d = traj(f"_b6_drift_s{sd}")
        if not d:
            continue
        t = d["traj"]
        rep = {}
        for key in ("pop", "tot_material" if "tot_material" in t[-1] else "mean_material",
                    "n_lineages", "n_settle", "gini_cred"):
            v = [r.get(key) for r in t if r.get(key) is not None]
            if len(v) < 8:
                continue
            first, last = statistics.median(v[:len(v)//4]), statistics.median(v[-len(v)//4:])
            # FLAT-THEN-EXPLODE is R-105's exact signature and is not caught by a start/end comparison alone
            mid = statistics.median(v[len(v)//2: 3*len(v)//4]) or 1e-9
            rep[key] = dict(first_quarter=first, last_quarter=last,
                            ratio=round(last / first, 3) if first else None,
                            late_accel=round((last / mid) / max(mid / (first or 1e-9), 1e-9), 3) if mid else None)
        out[f"seed{sd}"] = dict(steps=d["meta"].get("steps_completed"), snapshots=len(t), drift=rep)
        log(f"    seed {sd}: {d['meta'].get('steps_completed')} steps, {len(t)} snapshots")
        for k, r in rep.items():
            log(f"        {k:16s} {r['first_quarter']} -> {r['last_quarter']} (x{r['ratio']}, "
                f"late-accel {r['late_accel']})")
    R["S6"] = out


if __name__ == "__main__":
    open(PROG, "a", encoding="utf-8").close()
    R = {}
    t0 = time.time()
    log("=" * 70)
    log("BATTERY 6 LONG — S4 benchmark envelope + S6 drift")
    for name, fn in (("S4", stage_s4),):
        try:
            fn(R)
        except Exception as e:
            log(f"  *** {name} CRASHED: {type(e).__name__}: {e}")
            log(traceback.format_exc()[-700:])
        json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
        log(f"  elapsed {(time.time()-t0)/3600:.1f} h")
    left = max(60.0, 9.5 * 60 - (time.time() - t0) / 60.0)
    try:
        stage_s6(R, int(min(left / 2, 240)))
    except Exception as e:
        log(f"  *** S6 CRASHED: {type(e).__name__}: {e}")
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
    log(f"DONE in {(time.time()-t0)/3600:.1f} h -> {OUT}")
