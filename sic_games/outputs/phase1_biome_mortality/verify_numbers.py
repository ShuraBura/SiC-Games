"""SELF-CHECK — recompute every headline number by an INDEPENDENT route and flag disagreement.

Written 2026-07-18 after five instrument artifacts in one day. The point is not to re-run the same code and
get the same answer; it is to compute each claim a DIFFERENT way and see whether the two agree. Where a number
was an estimate rather than a measurement, that is stated.

Run: py -3 sic_games/outputs/phase1_biome_mortality/verify_numbers.py
"""
import glob
import os

import numpy as np

HERE = os.path.dirname(__file__)
OK, BAD = "  ok ", " ***"


def chk(name, a, b, tol=0.02, note=""):
    agree = abs(a - b) <= tol * max(1.0, abs(b))
    print(f"{OK if agree else BAD} {name:44s} {a:9.4f} vs {b:9.4f}   {note}")
    return agree


print("=" * 100)
print("1. PURE ARITHMETIC — the anchored constants (check these by hand)")
print("=" * 100)
chk("Boehm deposition share  9/(9+17)", 9 / 26, 0.3462, note="9 deposition, 17 desertion")
chk("Boehm overreach weight  (14+5)/29", 19 / 29, 0.6552, note="14 dominating + 5 monopolizing / 29")
chk("Boehm leveling strength 38/48", 38 / 48, 0.7917, note="38 of 48 societies sanction decisively")
comp = 0.46 * 0.257 + 0.39 * 0.267 + 0.15 * 0.237
chk("BHM forager composite (a.G products)", comp, 0.258,
    note="0.46*0.257 + 0.39*0.267 + 0.15*0.237")
chk("BHM alpha row sums to 1 (forager)", 0.46 + 0.39 + 0.15, 1.0, tol=1e-9)
chk("BHM alpha row sums to 1 (agricultural)", 0.27 + 0.14 + 0.59, 1.0, tol=1e-9)

print()
print("=" * 100)
print("2. CORRELATION TIME — 1/e crossing vs an INDEPENDENT exponential fit to the ACF")
print("=" * 100)
for fn in sorted(glob.glob(os.path.join(HERE, "hcycles_series_*.npy"))):
    a = os.path.basename(fn).split("_a")[1][:-4]
    y = np.load(fn)
    x = y - y.mean()
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]
    ac /= ac[0]
    tau_cross = int(np.argmax(ac < 1 / np.e)) * 4 / 12.0          # method A: first 1/e crossing
    m = ac[:200] > 0.02                                            # method B: log-linear fit on the positive head
    k = np.arange(200)[m]
    tau_fit = (-1.0 / np.polyfit(k, np.log(ac[:200][m]), 1)[0]) * 4 / 12.0 if len(k) > 5 else float("nan")
    chk(f"alpha={a}: corr time (yr)", tau_cross, tau_fit, tol=0.5,
        note=f"1/e crossing vs exp-fit slope")

print()
print("=" * 100)
print("3. NULL FLOORS — re-derived with DIFFERENT seeds; a stable floor should barely move")
print("=" * 100)
import sys
sys.path.insert(0, HERE)
from cycle_fit import null_amplitude
for seed in (0, 12345):
    n = null_amplitude(900, 0.35, trials=120, seed=seed)
    print(f"       fit-null p95 (n=900, sd=0.35, seed={seed:5d}) = {n['amp_p95']:.4f}")

print()
print("=" * 100)
print("4. DWELL TIME — DIRECT measurement from the series, replacing the earlier ESTIMATE")
print("=" * 100)
print("   Earlier figures (3.9 / 10.2 / 4.8 yr) were INFERRED from aggregate reversion counts assuming")
print("   ~25 agents/band. Here the aggregate series is thresholded and run-lengths measured directly.")
for fn in sorted(glob.glob(os.path.join(HERE, "hcycles_series_*.npy"))):
    a = os.path.basename(fn).split("_a")[1][:-4]
    y = np.load(fn)
    hi = y > 0.5
    runs, cur = [], 0
    for v in hi:
        if v:
            cur += 1
        elif cur:
            runs.append(cur); cur = 0
    if cur:
        runs.append(cur)
    lo_runs, cur = [], 0
    for v in ~hi:
        if v:
            cur += 1
        elif cur:
            lo_runs.append(cur); cur = 0
    if cur:
        lo_runs.append(cur)
    f = lambda r: (np.mean(r) * 4 / 12.0 if r else 0.0)
    print(f"       alpha={a:7s} frac time ranked {hi.mean():.3f} | ranked spells n={len(runs):3d} "
          f"mean {f(runs):6.1f} yr max {(max(runs)*4/12 if runs else 0):6.1f} yr | "
          f"egalitarian spells mean {f(lo_runs):6.1f} yr")

print()
print("=" * 100)
print("5. THE CLAIM THAT DIED — is correlation time monotone in the lag?")
print("=" * 100)
lags = {"0.0005": 166.7, "0.001": 83.3, "0.02": 4.2}
rows = []
for fn in sorted(glob.glob(os.path.join(HERE, "hcycles_series_*.npy"))):
    a = os.path.basename(fn).split("_a")[1][:-4]
    y = np.load(fn); x = y - y.mean()
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]; ac /= ac[0]
    rows.append((lags.get(a, float("nan")), int(np.argmax(ac < 1 / np.e)) * 4 / 12.0, a))
rows.sort()
print(f"       {'lag memory (yr)':>16} {'corr time (yr)':>16}")
for lag, tau, a in rows:
    print(f"       {lag:16.1f} {tau:16.1f}")
taus = [r[1] for r in rows]
mono = all(taus[i] <= taus[i + 1] for i in range(len(taus) - 1)) or \
       all(taus[i] >= taus[i + 1] for i in range(len(taus) - 1))
print(f"       monotone in lag? {mono}  -> {'claim would hold' if mono else 'CLAIM REFUTED (as recorded in R-87d)'}")
