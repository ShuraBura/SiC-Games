"""R-103 — validate the STRATIFICATION-INEQUALITY GATE across worlds.

The R-102 sweep exposed a decoupling: the flat-tropical arm read 45% stratified while carrying the LOWEST cred-Gini
of any arm. Diagnosis (2026-07-22): `society_from_character` classified stratified on high MEAN surplus, not on
UNEQUAL control of it — a uniformly-affluent packed world is mislabelled. The gate (default OFF, bit-exact verified)
requires within-band cred-Gini >= a floor for the stratified verdict.

THIS CAMPAIGN answers three questions, each as a matched OFF-vs-ON pair so the gate is the only difference:
  1. PRESERVE  — does the gate keep the VALIDATED baseline (coastal-temperate) near R-64's 9-16%? (must, or too harsh)
  2. FIX       — does it drop the flat-tropical 45% artifact to something sane?
  3. NOT OVER-CORRECT — does a genuinely-unequal tropical world (coastal-tropical) KEEP its stratification?

Two thresholds are swept because within-band Gini runs ~0.20 in this model (far below BHM's population-scale 0.40),
so the operative floor had to be CALIBRATED on the baseline, not taken from the literature directly. G_LO/G_HI are
set from the calibration run's `strat_band_gini_med` separation between genuine (baseline/coastal) and artifact (flat).

Sequential (single-threaded, CPU-bound). Cheap worlds first so the morning has finished arms whatever the tropics do.
Flat-tropical is compute-capped (it fills a high carrying capacity to ~40k); every arm records steps_completed.
"""
import os, subprocess, sys, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# thresholds — SET FROM CALIBRATION (placeholders; overwritten before launch)
G_LO = os.environ.get("R103_GLO", "0.15")
G_HI = os.environ.get("R103_GHI", "0.25")

STEPS = os.environ.get("R103_STEPS", "3000")
FOUNDERS = os.environ.get("R103_FOUNDERS", "3000")
MAXMIN = os.environ.get("R103_MAXMIN", "45")

WORLDS = [
    ("coastal", "temperate", "base"),    # the R-64 validated baseline — PRESERVE test
    ("hilly", "temperate", "hilly"),     # control
    ("coastal", "tropical", "coast"),    # genuinely unequal tropical — NOT-OVER-CORRECT test
    ("flat", "tropical", "flat"),        # the 45% artifact — FIX test (dearest, last)
]
CONDS = [("off", "0", "0.40"), ("glo", "1", G_LO), ("ghi", "1", G_HI)]

STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal")

PROG = os.path.join(HERE, "r103_progress.txt")


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


if __name__ == "__main__":
    open(PROG, "w").close()
    jobs = [(t, c, wn, cn, ig, gm) for (t, c, wn) in WORLDS for (cn, ig, gm) in CONDS]
    log(f"R-103 gate validation: {len(jobs)} arms x {STEPS} steps  (G_LO={G_LO} G_HI={G_HI})")
    t0 = time.time()
    done = []
    for i, (terr, clim, wn, cn, ig, gm) in enumerate(jobs, 1):
        tag = f"_r103_{wn}_{cn}"
        env = dict(os.environ, C_TAG=tag, C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_FOUNDERS=FOUNDERS,
                   C_MAXMIN=MAXMIN, C_INEQGATE=ig, C_GINIMIN=gm, **STACK)
        log(f"[{i}/{len(jobs)}] {wn:5s} {cn:3s} (gate={ig} gini_min={gm})  elapsed {(time.time()-t0)/60:.0f}m")
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "run_campaign.py")],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            log(f"      rc={r.returncode} STDERR: {r.stderr.strip()[-300:]}")
            continue
        try:
            m = json.load(open(os.path.join(HERE, f"campaign_trajectory{tag}.json"), encoding="utf-8"))
            row = m["traj"][-1]
            done.append((tag, row))
            log(f"      done: steps={m['meta'].get('steps_completed')} pop={row['pop']} "
                f"strat={row['pct_stratified']}% giniC={row['gini_cred']} "
                f"strat_band_gini={row.get('strat_band_gini_med')} nStratBands={row.get('n_strat_bands')}")
        except Exception as e:
            log(f"      (readback failed: {e})")
    log(f"\nR-103 DONE in {(time.time()-t0)/60:.0f} min")
    log("SUMMARY (pct_stratified by world x condition):")
    for tag, row in done:
        log(f"   {tag:22s} strat={row['pct_stratified']:5}%  giniC={row['gini_cred']}  pop={row['pop']}")
