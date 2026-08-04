"""Sweep ONE calibrated parameter against ONE marker, on the full stack, paired and build-gated.

Two jobs this arc needs repeatedly, and they are the same shape:

  (a) RE-FIT a fitted constant whose fit has gone stale. `cv_safe` is documented as "the ONE fitted scale ...
      calibrated — but ONLY to place the MEAN band at Hill 2011's ~25-30 (mean RETURN_CV 1.017 / 27.5 =
      0.037)". It was fitted for `enable_emergent_band_size` ALONE; `enable_resource_directed_fusion` adds a
      further ~10% (paired, 3 worlds x 2 seeds) that the fit never saw, and the full stack lands `band_med` at
      37-38 against Johnson's [18-35]. Re-fitting to the SAME anchor is maintenance of an existing
      calibration, not fitting the model to a benchmark.

  (b) BRACKET a parameter whose own provenance says to. `pathogen_gamma`: "BRACKETED strength (NPP exponent);
      0 = OFF/flat. Sweep low/mid/high" — the mechanism reads INERT because its magnitude is 0, and the doc
      asks for exactly this sweep. Likewise `shock_rho` ("[PROVISIONAL — sweep]").

The value of a swept point is only meaningful against a control produced by the SAME build in the SAME
session, so the sweep always includes the current default as one of its points and refuses to report a table
with a missing or unloadable arm (the first version of this script discarded stdout and printed four clean
empty rows while all 24 arms were dying in the constructor).

Run:  py -3 -u diag_param_sweep.py
Env:  R_FIELD  config field to sweep            (default cv_safe)
      R_VALS   csv of values, INCLUDE the current default as the control
      R_MARKER trajectory key to score          (default band_med)
      R_BAND   "lo,hi" benchmark band           (default 18,35 = Johnson)
      R_TARGET "lo,hi" the anchor being fitted  (default 25,30 = Hill 2011 mean band)
      R_WORLDS R_SEEDS R_STEPS R_PAR R_TAG
"""
import json
import os
import statistics
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
CAMP = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
LOGDIR = os.path.dirname(os.path.abspath(__file__))

FIELD = os.environ.get("R_FIELD", "cv_safe")
VALS = [v.strip() for v in os.environ.get("R_VALS", "0.037,0.045,0.052,0.060").split(",") if v.strip()]
MARKER = os.environ.get("R_MARKER", "band_med")
BAND_LO, BAND_HI = [float(x) for x in os.environ.get("R_BAND", "18,35").split(",")]
TARGET_LO, TARGET_HI = [float(x) for x in os.environ.get("R_TARGET", "25,30").split(",")]
TAG = os.environ.get("R_TAG", FIELD[:6])

WORLD_MAP = {"coastal_temperate": ("coastal", "temperate"), "flat_temperate": ("flat", "temperate"),
             "hilly_temperate": ("hilly", "temperate"), "flat_boreal": ("flat", "boreal"),
             "flat_tropical": ("flat", "tropical")}
WORLDS = [w for w in os.environ.get(
    "R_WORLDS", "coastal_temperate,flat_temperate,hilly_temperate").split(",") if w]
SEEDS = [s for s in os.environ.get("R_SEEDS", "0,1").split(",") if s]
STEPS = os.environ.get("R_STEPS", "1200")
PAR = int(os.environ.get("R_PAR", "6"))
# Wall-clock cap per arm. Battery 7's S3 lost 8 of 12 arms to a 25-minute cap, and a truncated arm is not a
# short arm — the common-horizon logic then drags every other arm down to the shortest one.
MAXMIN = os.environ.get("R_MAXMIN", "35")

# The full stack. C_ALLON now turns on every built mechanism except the five documented exclusions, and
# implies C_ELITE, so the elite magnitudes come with the elite flags. The knobs kept here are the ones whose
# VALUE (not on/off) is a choice — plus C_IMPROVED=0, which is a deliberate ablation: improved-land
# agriculture is a regime change, and every marker being scored here (Johnson band size, Bar-Yosef
# settlement, Binford mobility) is a FORAGER anchor.
STACK = dict(C_ALLON="1", C_SOIL="1", C_ABANDON="1", C_IMPROVED="0", C_GENEA="0",
             C_RESIDENCE="virilocal", C_MATRULE="primogeniture", C_HEIRSTAT="1",
             C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8", C_TRIBFRAC="0.15",
             C_RELMULT="2.0", C_RESYTR="80")


def head_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


def tree_dirty():
    try:
        return bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip())
    except Exception:
        return True


HEAD = head_sha()


def traj(tag):
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
    if meta.get("tree_dirty"):     # a dirty tree records the PARENT commit — not identified by its sha
        return None
    sha = meta.get("sha", "")
    if HEAD and sha and not sha.startswith(HEAD) and not HEAD.startswith(sha):
        return None
    return d["traj"]


def sustained(t, key, horizon):
    t = [r for r in t if r["step"] <= horizon]
    if not t:
        return None
    cut = t[-1]["step"] * 0.5
    v = [r[key] for r in t if r["step"] >= cut and r.get(key) is not None]
    return statistics.median(v) if v else None


def tag_of(val, w, sd):
    return f"_sw{TAG}{val.replace('.', 'p').replace('-', 'm')}_{w}_s{sd}"


def run_val(val):
    todo = [(w, sd) for w in WORLDS for sd in SEEDS if traj(tag_of(val, w, sd)) is None]
    running, failed = [], []
    while todo or running:
        while todo and len(running) < PAR:
            w, sd = todo.pop(0)
            terr, clim = WORLD_MAP[w]
            tag = tag_of(val, w, sd)
            env = dict(os.environ, **STACK, C_TAG=tag, C_TERR=terr, C_CLIM=clim, C_SEED=sd,
                       C_FOUNDERS="3000", C_STEPS=STEPS, C_MAXMIN=MAXMIN,
                       C_LOGEVERY=str(max(25, int(STEPS) // 20)), C_PARAM=f"{FIELD}={val}")
            out = open(os.path.join(LOGDIR, f"sweep{tag}.log"), "w")
            running.append((tag, subprocess.Popen(
                [sys.executable, "-u", os.path.join(CAMP, "run_campaign.py")],
                cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT), out))
        time.sleep(12)
        for it in list(running):
            tag, p, o = it
            if p.poll() is not None:
                o.close(); running.remove(it)
                if p.returncode != 0:
                    failed.append((tag, p.returncode))
    if failed:
        for tag, rc in failed:
            tail = open(os.path.join(LOGDIR, f"sweep{tag}.log"),
                        encoding="utf-8", errors="replace").read()[-1500:]
            print(f"\n!! ARM FAILED rc={rc} {tag}\n{tail}", flush=True)
        raise SystemExit(f"{FIELD}={val}: {len(failed)} arm(s) failed — refusing to report a sweep with "
                         f"missing arms as a result")
    # Every arm exited 0, so every arm must LOAD. If not, the build gate rejected it and the sweep has no
    # data even though nothing "failed" — which is how the first version printed four clean empty rows.
    missing = [tag_of(val, w, sd) for w in WORLDS for sd in SEEDS if traj(tag_of(val, w, sd)) is None]
    if missing:
        raise SystemExit(f"{FIELD}={val}: {len(missing)} arm(s) ran but are not loadable — the build gate "
                         f"rejected them (stale sha, or dirty tree). First: {missing[0]}")
    per = {}
    for w in WORLDS:
        for sd in SEEDS:
            per[(w, sd)] = traj(tag_of(val, w, sd))
    H = min(t[-1]["step"] for t in per.values())
    return {k: sustained(t, MARKER, H) for k, t in per.items()}, H


def main():
    if tree_dirty():
        raise SystemExit("working tree is DIRTY — commit first. Arms from a dirty tree record the PARENT "
                         "commit, so they are not identified by their sha and the gate will reject them.")
    print(f"[sweep] {FIELD} over {VALS} | marker {MARKER} | build {HEAD}")
    print(f"[sweep] {len(WORLDS)} world(s) x {len(SEEDS)} seed(s), {STEPS} steps, full stack (C_ALLON=1)")
    print(f"[sweep] benchmark band [{BAND_LO:g}, {BAND_HI:g}] | anchor being fitted "
          f"[{TARGET_LO:g}, {TARGET_HI:g}]\n", flush=True)
    rows, base = [], None
    for val in VALS:
        got, H = run_val(val)
        vals = [v for v in got.values() if v is not None]
        if not vals:
            raise SystemExit(f"{FIELD}={val}: no arm produced {MARKER!r}")
        med = statistics.median(vals)
        inband = sum(1 for v in vals if BAND_LO <= v <= BAND_HI)
        if base is None:
            base = got                                   # the first value listed is the control
            delta = "  (control)"
        else:
            # PAIRED by (world, seed): the seed variance is 30x the effect size (R-65), so only the
            # within-pair direction is readable at this sample size.
            pairs = [(base[k], got[k]) for k in got if base.get(k) is not None and got[k] is not None]
            up = sum(1 for a, b in pairs if b > a)
            mean_d = statistics.mean((b - a) / a for a, b in pairs) if pairs else 0.0
            delta = f"  {mean_d:+6.1%} paired, {len(pairs) - up}/{len(pairs)} down"
        rows.append((val, med, inband, len(vals), TARGET_LO <= med <= TARGET_HI))
        print(f"  {FIELD}={val:>8}  {MARKER} median={med:>7.2f}  "
              f"range {min(vals):.1f}..{max(vals):.1f}  in-band {inband}/{len(vals)}"
              f"{delta}  (horizon {H}){'   <= ON ANCHOR' if TARGET_LO <= med <= TARGET_HI else ''}",
              flush=True)
    print("\n=== SUMMARY ===")
    print(f"{FIELD:>10} {MARKER:>12} {'in-band':>9} {'on anchor':>10}")
    for val, med, inband, n, ok in rows:
        print(f"{val:>10} {med:>12.2f} {f'{inband}/{n}':>9} {'YES' if ok else 'no':>10}")
    good = [r for r in rows if r[4] and r[2] == r[3]]
    if good:
        mid = (TARGET_LO + TARGET_HI) / 2.0
        best = min(good, key=lambda r: abs(r[1] - mid))
        print(f"\nCANDIDATE: {FIELD}={best[0]} -> {MARKER} {best[1]:.2f}, {best[2]}/{best[3]} in band.")
        print("NOT adopted here — needs the full worlds x seeds envelope and a green suite first.")
    else:
        print(f"\nNo swept value both lands {MARKER} on the anchor and keeps every arm in band. Reported "
              f"as-is; widening the target to make one fit would be fitting the anchor to the model.")


if __name__ == "__main__":
    main()
