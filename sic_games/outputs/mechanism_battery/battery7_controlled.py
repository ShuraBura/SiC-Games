"""BATTERY 7 — CONTROLLED: every comparison is same-build, same-session, paired.

WHY THIS EXISTS (R-106 Addendum 19). Battery 6 drew two conclusions from a control that was written two days
before the arms compared against it, with a demography overhaul and a wealth fix committed in between. Both
conclusions measured code drift rather than the mechanisms under test, and one had to be retracted. The root
cause was not the analysis — it was that the harness accepted any trajectory file whose NAME matched, with no
check on the BUILD that produced it. `run_matrix.py` had already solved that ("Existence is not enough");
battery 6 had not adopted it.

The rules this battery enforces, each of which failed at least once in the R-106 arc:

  R1  SAME BUILD. Every arm records `meta.sha`; an arm from a different build is not reusable and is re-run.
      A stage refuses to score if ANY of its arms disagree on the build.
  R2  SAME SESSION. The control is run HERE, alongside the ablations, never read from a previous run.
  R3  PAIRED. Every ablation is compared to the control arm of the SAME (world, seed). R-65 measured 30x seed
      variance; unpaired means are not interpretable.
  R4  MATCHED HORIZON. All arms in a stage run the same steps, and scoring truncates to the shortest actually
      reached (arms can wall-clock early), because `sustained()` medians over the last half of whatever it is
      given — a shorter arm is scored on a different window.
  R5  FAIL LOUD. Unknown flag names raise. Missing arms are reported, never silently dropped.

STAGES
  S1 CONTROL          the canonical preset, worlds x seeds, this build. Everything else is measured against it.
  S2 MECHANISM AUDIT  each mechanism ablated OUT of the full stack one at a time, paired vs S1's full-stack
                      arm. Verdict per mechanism: LIVE (removing it changes the world), INERT (it does not),
                      or UNTESTABLE (its precondition never occurred — no settlement, no claim, no death).
                      "INERT" is a real finding; "UNTESTABLE" is not a defect, and conflating them is how the
                      old flag audit reported "no defects" while being unable to find one.
  S3 MATRIX           long arms scored against MARKER_MATRIX bands as PASS FRACTIONS, control vs full stack.

Run:   py -3 -u sic_games/outputs/mechanism_battery/battery7_controlled.py
Env:   B7_STAGES (s1,s2,s3)  B7_WORLDS  B7_SEEDS  B7_STEPS  B7_LONG  B7_PAR  B7_MAXMIN
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
DOCS = os.path.join(ROOT, "docs")
PROG = os.path.join(HERE, "battery7_progress.txt")
OUT = os.path.join(HERE, "battery7_results.json")

sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))

STAGES = [s.strip() for s in os.environ.get("B7_STAGES", "s1,s2,s3").split(",") if s.strip()]
# SAVANNA joined the menu in R-106. `terrain.py` has carried a `savanna` CLIMATE_PRESET since 2026-07-08
# ("Koppen Aw ... the human-evolution biome (Hadza)"), deliberately left OUT of CLIMATE_ORDER so the
# seed->climate lottery stays bit-exact — which made it explicit-only, and nothing ever asked for it. The
# consequence was measured: every campaign world was forest, forest or desert, so savanna is 0-0.6% of the
# capacity patch and every savanna-keyed mechanism (C.5 intercept hunting, C.4c llanos flood) was
# structurally unreachable. In a savanna world it is 52-67%. It stays out of CLIMATE_ORDER — adding it there
# would renumber every existing seed->climate mapping — and goes in the harness menus instead.
WORLD_MAP = {"coastal_temperate": ("coastal", "temperate"), "flat_temperate": ("flat", "temperate"),
             "flat_boreal": ("flat", "boreal"), "flat_tropical": ("flat", "tropical"),
             "hilly_temperate": ("hilly", "temperate"),
             "flat_savanna": ("flat", "savanna"), "coastal_savanna": ("coastal", "savanna")}
WORLDS = [w for w in os.environ.get("B7_WORLDS", "coastal_temperate,flat_temperate,hilly_temperate").split(",") if w]
SEEDS = [s for s in os.environ.get("B7_SEEDS", "0,1").split(",") if s]
STEPS = os.environ.get("B7_STEPS", "1200")
LONG = os.environ.get("B7_LONG", "2500")
PAR = int(os.environ.get("B7_PAR", "4"))
MAXMIN = os.environ.get("B7_MAXMIN", "25")

# The live stack a campaign actually runs, matching battery6 so results are comparable.
STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal",
             C_MATINHERIT="1", C_MATRULE="primogeniture", C_HEIRSTAT="1",
             C_LINTRIBUTE="1", C_TRIBFRAC="0.15", C_NOBLEXEMPT="1", C_DEFEND="1",
             C_BUD="1", C_BUDHAZ="1", C_IMPROVED="0")

# MARKER_MATRIX bands, with the docs probe battery6 uses so a retired anchor is skipped, not scored.
BENCH = [("band_med", 18, 35, "Johnson scalar stress / R-72", "repulsion_midpoint"),
         ("settle_med", 50, 150, "Bar-Yosef 50-150", "Bar-Yosef"),
         ("settle_med", 50, 250, "Alvard 2009 village 50-250", "50 to ~250"),
         ("connubium_med", 79, 332, "White 2017 MVP", "minimum viable population"),
         ("lineage_size_gini", 0.51, 0.68, "BHM 2009", "BHM 2009"),
         ("lin_top_share", 0.08, 0.30, "Karmin 2015", "Karmin")]

# Mechanisms whose ablation is meaningless or already adjudicated — each with the reason, never a bare skip.
SKIP = {
    "enable_infanticide": "documented UNIMPLEMENTED STUB - no logic reads it",
    "enable_genealogy_log": "observer/logging, not a dynamic",
    "enable_bud_hazard": "mutually-exclusive alternate to the legacy budding path",
    "enable_stratification_inequality_gate": "R-103: criterion known wrong, parked for supervisor call",
}
# Preconditions: a mechanism whose UNIT never came into existence is UNTESTABLE, not dead (battery1's lesson).
PRECOND = {
    "enable_emergent_abandonment": ("settlements", "no settlement ever formed"),
    "enable_sedentism_fertility": ("settlements", "no settlement ever formed"),
    "enable_village_budding": ("settlements", "no settlement ever formed"),
    "enable_economic_defensibility": ("owned", "no cell was ever claimable/owned"),
    "enable_improved_land": ("owned", "no cell was ever claimable/owned"),
    "enable_store_anchor": ("settlements", "no settlement ever formed"),
}


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M')}] {m}\n")
    print(m, flush=True)


def head_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


HEAD = head_sha()


def load(tag):
    """R1: a trajectory is usable only if it was produced by THE CURRENT BUILD.

    `meta.tree_dirty` closes the hole under the sha gate: a run started from uncommitted edits records the
    PARENT commit, so sha alone would pair it with a run of the committed code and call them the same build.
    A dirty arm is not identified by its sha, so it is never reusable — it is re-run instead."""
    p = os.path.join(CAMP, f"campaign_trajectory{tag}.json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    if not d.get("traj"):
        return None
    meta = d.get("meta") or {}
    if meta.get("tree_dirty"):
        return None
    sha = meta.get("sha", "")
    if HEAD and sha and not sha.startswith(HEAD) and not HEAD.startswith(sha):
        return None
    return d


def sustained(t, key, horizon, frac=0.5):
    """R4: truncate to a COMMON horizon before taking the last-half median."""
    t = [r for r in t if r["step"] <= horizon]
    if not t:
        return None
    cut = t[-1]["step"] * frac
    v = [r[key] for r in t if r["step"] >= cut and r.get(key) is not None]
    return statistics.median(v) if v else None


def run_arms(arms, steps):
    """arms: list of (tag, env_overrides). Only arms missing FOR THIS BUILD are run."""
    todo = [(t, e) for (t, e) in arms if load(t) is None]
    if len(todo) < len(arms):
        log(f"    resume: {len(arms)-len(todo)} arm(s) already complete on this build")
    running = []
    while todo or running:
        while todo and len(running) < PAR:
            tag, over = todo.pop(0)
            # ~20 snapshots per arm regardless of horizon. `sustained()` medians the LAST HALF, so a coarse
            # cadence leaves 2-3 points to median and the statistic becomes a coin flip; the smoke test at
            # C_LOGEVERY=400 over 60 steps produced a single snapshot and a "common horizon" of 1 step.
            env = dict(os.environ, **STACK, C_TAG=tag, C_FOUNDERS="3000", C_STEPS=str(steps),
                       C_MAXMIN=MAXMIN, C_LOGEVERY=str(max(25, int(steps) // 20)), **over)
            out = open(os.path.join(HERE, f"b7_stdout{tag}.txt"), "w", encoding="utf-8")
            running.append((tag, subprocess.Popen(
                [sys.executable, "-u", os.path.join(CAMP, "run_campaign.py")],
                cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, text=True), out))
            log(f"    launched {tag}")
        time.sleep(15)
        for it in list(running):
            tag, p, o = it
            if p.poll() is not None:
                o.close(); running.remove(it)
                log(f"    finished {tag} rc={p.returncode}")


def gather(tags):
    """Load arms, verify they agree on the build, return (data, common_horizon)."""
    data, shas, hs = {}, set(), []
    for tag in tags:
        d = load(tag)
        if d is None:
            continue
        data[tag] = d
        shas.add((d.get("meta") or {}).get("sha", ""))
        hs.append(d["traj"][-1]["step"])
    if len(shas) > 1:
        raise SystemExit(f"BUILD MISMATCH across arms: {shas} — refusing to score (R1)")
    return data, (min(hs) if hs else 0)


def all_flags():
    from run_se0_controlled_climate import emergent_village_demog
    from sic_games.demography import DemographyConfig
    base = emergent_village_demog()
    return sorted(f for f in DemographyConfig.model_fields if f.startswith("enable_")), base


# ------------------------------------------------------------------ S1 CONTROL
def stage_s1(R):
    log(f"S1 CONTROL — canonical preset + full stack, build {HEAD}, {len(WORLDS)}x{len(SEEDS)} arms")
    arms = []
    for w in WORLDS:
        terr, clim = WORLD_MAP[w]
        for sd in SEEDS:
            arms.append((f"_b7_ctl_{w}_s{sd}", dict(C_TERR=terr, C_CLIM=clim, C_SEED=sd)))
            arms.append((f"_b7_full_{w}_s{sd}", dict(C_TERR=terr, C_CLIM=clim, C_SEED=sd, C_ALLON="1")))
    run_arms(arms, STEPS)
    tags = [t for (t, _) in arms]
    data, hz = gather(tags)
    log(f"    arms loaded {len(data)}/{len(tags)}, common horizon {hz} steps")
    rows = []
    for w in WORLDS:
        for sd in SEEDS:
            c, f = data.get(f"_b7_ctl_{w}_s{sd}"), data.get(f"_b7_full_{w}_s{sd}")
            if not c or not f:
                continue
            rows.append(dict(world=w, seed=sd,
                             ctl={k: sustained(c["traj"], k, hz) for k, *_ in BENCH},
                             full={k: sustained(f["traj"], k, hz) for k, *_ in BENCH},
                             ctl_pop=sustained(c["traj"], "pop", hz),
                             full_pop=sustained(f["traj"], "pop", hz)))
    log(f"\n    CONTROL vs FULL STACK — paired, same build, horizon {hz}")
    log(f"    {'marker':>20} {'control':>10} {'full':>10} {'delta':>8} {'up/pairs':>9}")
    for (k, lo, hi, src, _p) in BENCH:
        pairs = [(r["ctl"][k], r["full"][k]) for r in rows
                 if r["ctl"].get(k) is not None and r["full"].get(k) is not None]
        if not pairs:
            continue
        cm = statistics.median([a for a, _ in pairs]); fm = statistics.median([b for _, b in pairs])
        up = sum(1 for a, b in pairs if b > a)
        rel = f"{100.0*(fm-cm)/abs(cm):+.0f}%" if cm else "n/a"
        log(f"    {k:>20} {cm:>10.4g} {fm:>10.4g} {rel:>8} {f'{up}/{len(pairs)}':>9}")
    R["S1"] = dict(build=HEAD, horizon=hz, rows=rows)
    return hz


# ------------------------------------------------------------------ S2 MECHANISM AUDIT
def stage_s2(R):
    flags, base = all_flags()
    w0 = WORLDS[0]
    terr, clim = WORLD_MAP[w0]
    sd = SEEDS[0]
    full_tag = f"_b7_full_{w0}_s{sd}"
    if load(full_tag) is None:
        run_arms([(full_tag, dict(C_TERR=terr, C_CLIM=clim, C_SEED=sd, C_ALLON="1"))], STEPS)
    ref = load(full_tag)
    if ref is None:
        log("S2 skipped — no full-stack reference arm on this build")
        return
    # R6 (added after the first S2 run scored 7 invalid verdicts): only ablate a flag that is actually ON in
    # the reference stack. Setting an already-False flag to False is a no-op, so it reads INERT trivially —
    # "the mechanism does nothing" and "the mechanism was never running" are different claims and the first
    # one is a finding. The campaign records the resolved config in `meta.demography_config`, so read it.
    cfg = (ref.get("meta") or {}).get("demography_config") or {}
    if not isinstance(cfg, dict):
        cfg = {}
    in_stack = [f for f in flags if f not in SKIP and cfg.get(f) is True]
    not_in_stack = [f for f in flags if f not in SKIP and cfg.get(f) is not True]
    log(f"S2 MECHANISM AUDIT — ablate each of {len(in_stack)} ON flags OUT of the full stack ({w0} s{sd})")
    for f, why in SKIP.items():
        log(f"    SKIP {f}: {why}")
    if not_in_stack:
        log(f"    NOT IN STACK ({len(not_in_stack)}) — off in the reference build, so NOT TESTED (ablating an "
            f"already-off flag is a no-op and would read INERT for free):")
        for f in not_in_stack:
            log(f"      {f}")
    testable = in_stack
    arms = [(f"_b7_abl_{f.replace('enable_','')}_{w0}_s{sd}",
             dict(C_TERR=terr, C_CLIM=clim, C_SEED=sd, C_ALLON="1", C_EXTRA_OFF=f)) for f in testable]
    run_arms(arms, STEPS)
    _, hz = gather([full_tag] + [t for t, _ in arms])
    rt = ref["traj"]
    keys = ["pop", "band_med", "settle_med", "n_settle", "lineage_size_gini", "gini_cred"]
    refv = {k: sustained(rt, k, hz) for k in keys}
    live, inert, untest, missing = [], [], [], []
    for f, (tag, _) in zip(testable, arms):
        d = load(tag)
        if d is None:
            missing.append(f); continue
        v = {k: sustained(d["traj"], k, hz) for k in keys}
        moved = [k for k in keys if v[k] is not None and refv[k] is not None
                 and abs(v[k] - refv[k]) > 1e-9]
        if moved:
            live.append((f, moved))
        else:
            pre = PRECOND.get(f)
            if pre and not (refv.get("n_settle") or 0):
                untest.append((f, pre[1]))
            else:
                inert.append(f)
    log(f"\n    LIVE   {len(live)}/{len(testable)}")
    for f, mv in live:
        log(f"      {f:<42} moved: {','.join(mv)}")
    log(f"    INERT  {len(inert)}  (on, and removing it changes NOTHING — a real finding)")
    for f in inert:
        log(f"      {f}")
    if untest:
        log(f"    UNTESTABLE {len(untest)}  (precondition never occurred — NOT a defect)")
        for f, why in untest:
            log(f"      {f:<42} {why}")
    if missing:
        log(f"    MISSING {len(missing)} arm(s): {missing}")
    R["S2"] = dict(build=HEAD, live=[f for f, _ in live], inert=inert,
                   untestable=[f for f, _ in untest], missing=missing)


# ------------------------------------------------------------------ S3 MATRIX
def stage_s3(R):
    txt = ""
    for fn in ("LITERATURE.md", "TARGETS.md", "PARAMETERS.md"):
        p = os.path.join(DOCS, fn)
        if os.path.exists(p):
            txt += open(p, encoding="utf-8", errors="ignore").read()
    live = [b for b in BENCH if b[4] in txt]
    for b in BENCH:
        if b not in live:
            log(f"    SKIPPED '{b[0]}' ({b[3]}): anchor quote {b[4]!r} not in docs/ — not scored")
    log(f"S3 MATRIX — long arms ({LONG} steps), control vs full stack, pass fractions")
    arms = []
    for w in WORLDS:
        terr, clim = WORLD_MAP[w]
        for sd in SEEDS:
            arms.append((f"_b7L_ctl_{w}_s{sd}", dict(C_TERR=terr, C_CLIM=clim, C_SEED=sd)))
            arms.append((f"_b7L_full_{w}_s{sd}", dict(C_TERR=terr, C_CLIM=clim, C_SEED=sd, C_ALLON="1")))
    run_arms(arms, LONG)
    data, hz = gather([t for t, _ in arms])
    log(f"    arms {len(data)}/{len(arms)}, common horizon {hz}")
    out = []
    for label, pref in (("CONTROL", "_b7L_ctl_"), ("FULL STACK", "_b7L_full_")):
        log(f"\n    {label}")
        for (k, lo, hi, src, _p) in live:
            vals = []
            for w in WORLDS:
                for sd in SEEDS:
                    d = data.get(f"{pref}{w}_s{sd}")
                    if d:
                        v = sustained(d["traj"], k, hz)
                        if v is not None:
                            vals.append((w, v))
            if not vals:
                continue
            hits = [v for _, v in vals if lo <= v <= hi]
            fails = sorted({w for w, v in vals if not (lo <= v <= hi)})
            log(f"      {k:>20} {len(hits):2d}/{len(vals):2d} in [{lo}-{hi}] | "
                f"{min(v for _, v in vals):.4g}..{max(v for _, v in vals):.4g} | "
                f"misses: {', '.join(fails) if fails else 'none'}")
            out.append(dict(arm=label, key=k, band=[lo, hi], hits=len(hits), n=len(vals)))
    R["S3"] = dict(build=HEAD, horizon=hz, score=out)


if __name__ == "__main__":
    open(PROG, "a", encoding="utf-8").close()
    R = {"build": HEAD}
    t0 = time.time()
    log("=" * 78)
    log(f"BATTERY 7 CONTROLLED — build {HEAD} — stages {STAGES}")
    log(f"  worlds={WORLDS} seeds={SEEDS} steps={STEPS} long={LONG} par={PAR}")
    for name, fn in (("s1", stage_s1), ("s2", stage_s2), ("s3", stage_s3)):
        if name not in STAGES:
            continue
        try:
            fn(R)
        except SystemExit as e:
            log(f"  *** {name} REFUSED: {e}")
        except Exception as e:
            log(f"  *** {name} CRASHED: {type(e).__name__}: {e}")
            log(traceback.format_exc()[-800:])
        json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
        log(f"  elapsed {(time.time()-t0)/60:.0f} min")
    log(f"DONE in {(time.time()-t0)/60:.0f} min -> {OUT}")
