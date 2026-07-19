"""R-87c — POWER ANALYSIS of the cycle detector. Could R-87's negative have missed a real cycle?

R-87 reported "no cycles at any lag" from an autocorrelation test, and that verdict is only worth as much as the
detector's sensitivity — which was never measured. This runs the positive control that should have come first:
inject a cycle of KNOWN period and amplitude into noise matching the observed series, and ask what the detector
returns.

Three specific suspicions about the R-87 test:
  1. LENGTH — 3600 steps at the anchored 60-100 yr period is only 3-5 cycles. Autocorrelation is weak there.
  2. TREND — population grew 500 -> 3200 during the run. `period_of` subtracts the MEAN only, not a trend, and a
     monotone trend produces slowly-decaying positive autocorrelation that can push the first zero-crossing far
     out and mask everything before it.
  3. THRESHOLD — the `ac_peak > 0.2` cut was invented, not calibrated against anything.

Measured series for reference (R-87, 83-yr lag arm): mean 0.476, sd 0.428, bounded [0,1], 900 samples.
"""
import numpy as np

SAMPLE_EVERY = 4
N_SAMPLES = 900          # 3600 steps / 4, as in R-87
OBS_MEAN, OBS_SD = 0.476, 0.428


def period_of(series, sample_every=SAMPLE_EVERY):
    """EXACTLY the R-87 detector, reproduced so the power analysis tests the thing that was actually used."""
    x = np.asarray(series, dtype=float)
    if len(x) < 60:
        return None, 0.0
    x = x - x.mean()
    if x.std() < 1e-9:
        return None, 0.0
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]
    ac /= ac[0]
    neg = np.where(ac < 0)[0]
    if len(neg) == 0:
        return None, 0.0
    start = neg[0]
    seg = ac[start:]
    if len(seg) < 3:
        return None, 0.0
    k = int(np.argmax(seg)) + start
    return k * sample_every, float(ac[k])


def synth(period_steps, amp_frac, noise_sd, trend=0.0, rng=None, n=N_SAMPLES):
    """A bounded [0,1] series with a known cycle. `amp_frac` is the cycle's sd as a fraction of total sd."""
    rng = rng or np.random.default_rng(0)
    t = np.arange(n) * SAMPLE_EVERY
    cyc = np.sin(2 * np.pi * t / period_steps)
    y = OBS_MEAN + amp_frac * cyc + noise_sd * rng.standard_normal(n) + trend * (t / t[-1])
    return np.clip(y, 0.0, 1.0)


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    print(__doc__.strip().split("\n")[0])

    print("\n=== 1. POSITIVE CONTROL: can the detector see a KNOWN cycle at the anchored period? ===")
    print("    (period 900 steps = 75 yr, i.e. 4 cycles in the run; noise sd fixed at 0.20)")
    print(f"{'cycle amp':>10} {'total sd':>9} {'true P (yr)':>12} {'found P (yr)':>13} {'ac_peak':>8} {'verdict':>12}")
    print("-" * 74)
    for amp in (0.05, 0.10, 0.20, 0.30, 0.45):
        peaks, pers = [], []
        for s in range(8):
            y = synth(900, amp, 0.20, rng=np.random.default_rng(s))
            p, pk = period_of(y)
            peaks.append(pk); pers.append(p / 12.0 if p else np.nan)
        pk, per = float(np.mean(peaks)), float(np.nanmean(pers))
        print(f"{amp:10.2f} {np.std(synth(900, amp, 0.20, rng=rng)):9.3f} {75.0:12.1f} {per:13.1f} "
              f"{pk:8.2f} {'DETECTED' if pk > 0.2 else 'MISSED':>12}")

    print("\n=== 2. TREND CONTAMINATION: does a population-growth-like trend break the detector? ===")
    print("    (a REAL cycle of amp 0.30 is present in every row; only the trend varies)")
    print(f"{'trend':>8} {'found P (yr)':>13} {'ac_peak':>8} {'verdict':>12}")
    print("-" * 46)
    for tr in (0.0, 0.2, 0.5, 1.0):
        peaks, pers = [], []
        for s in range(8):
            y = synth(900, 0.30, 0.20, trend=tr, rng=np.random.default_rng(100 + s))
            p, pk = period_of(y)
            peaks.append(pk); pers.append(p / 12.0 if p else np.nan)
        pk, per = float(np.mean(peaks)), float(np.nanmean(pers))
        print(f"{tr:8.2f} {per:13.1f} {pk:8.2f} {'DETECTED' if pk > 0.2 else 'MISSED':>12}")

    print("\n=== 3. LENGTH: how many cycles must fit before the detector is reliable? ===")
    print("    (cycle amp 0.30, noise 0.20, period 900 steps; only the run length varies)")
    print(f"{'steps':>7} {'cycles':>7} {'found P (yr)':>13} {'ac_peak':>8} {'verdict':>12}")
    print("-" * 50)
    for steps in (1800, 3600, 7200, 14400):
        n = steps // SAMPLE_EVERY
        peaks, pers = [], []
        for s in range(8):
            y = synth(900, 0.30, 0.20, rng=np.random.default_rng(200 + s), n=n)
            p, pk = period_of(y)
            peaks.append(pk); pers.append(p / 12.0 if p else np.nan)
        pk, per = float(np.mean(peaks)), float(np.nanmean(pers))
        print(f"{steps:7d} {steps / 900:7.1f} {per:13.1f} {pk:8.2f} {'DETECTED' if pk > 0.2 else 'MISSED':>12}")

    print("\n=== 4. NULL: what does PURE NOISE score? (the false-positive floor) ===")
    peaks = []
    for s in range(40):
        y = np.clip(OBS_MEAN + OBS_SD * np.random.default_rng(300 + s).standard_normal(N_SAMPLES), 0, 1)
        peaks.append(period_of(y)[1])
    a = np.asarray(peaks)
    print(f"    white noise ac_peak: mean {a.mean():.3f}  p95 {np.quantile(a, 0.95):.3f}  max {a.max():.3f}")
    print(f"    R-87 measured: 0.03 / 0.13 / 0.19  <- compare against this floor, not against 0.2")
