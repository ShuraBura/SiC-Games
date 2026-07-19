"""Sinusoid FIT for cycle detection — replaces the bare autocorrelation with something that reports an
AMPLITUDE and a FREQUENCY you can overlay on the data and judge by eye.

Why this exists (supervisor, 2026-07-18): the R-87 detector returned an autocorrelation peak and nothing else —
no amplitude, no fitted curve, no goodness-of-fit. That is why a value of 0.19 could be filed as "no cycle"
without anyone being able to see what was being rejected. A least-squares sinusoid over a frequency grid gives
the two numbers that actually matter and a curve that can be drawn on top of the series.

Method: for each trial frequency f, regress y on [sin(2*pi*f*t), cos(2*pi*f*t), 1] and take
amplitude = sqrt(a^2 + b^2). The best f maximises amplitude (equivalently minimises residual) — i.e. a
least-squares periodogram. Linear detrend first (charter D5).

MECHANISM_CHARTER D2 — the fit carries its own NULL: pure noise ALWAYS yields some best-fit amplitude, because
the fitter is free to pick the most flattering frequency out of the whole grid. The only meaningful question is
whether the measured amplitude exceeds what noise alone produces. `null_amplitude()` returns that distribution.
"""
import numpy as np


def fit_cycle(y, sample_every=4, pmin_steps=120, pmax_steps=3000, ngrid=400, detrend=True):
    """Best-fit sinusoid. Returns dict with amplitude, period (steps), phase, offset, r2, and the fitted curve."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    t = np.arange(n, dtype=float) * sample_every
    if detrend:                                   # charter D5
        y = y - np.polyval(np.polyfit(t, y, 1), t) + y.mean()
    # FIX 1 (2026-07-18): cap the period grid at window/3 — a fit that cannot complete three cycles is
    # describing a trend, not a periodicity. Unfixed, this returned 250 yr (the grid ceiling) from a 300 yr
    # window with r2 0.30, which was the single build-and-collapse episode, not a cycle.
    window = n * sample_every
    periods = np.linspace(pmin_steps, min(pmax_steps, window / 3.0), ngrid)
    best = None
    for P in periods:
        w = 2.0 * np.pi / P
        X = np.column_stack([np.sin(w * t), np.cos(w * t), np.ones(n)])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ coef
        ss = float(resid @ resid)
        if best is None or ss < best[0]:
            best = (ss, P, coef, X)
    ss, P, coef, X = best
    a, b, c = coef
    sstot = float(((y - y.mean()) ** 2).sum())
    return {
        "amplitude": float(np.hypot(a, b)),
        "period_steps": float(P),
        "period_years": float(P / 12.0),
        "offset": float(c),
        "r2": float(1.0 - ss / sstot) if sstot > 0 else 0.0,
        "curve": (X @ coef).tolist(),
        "detrended": y.tolist(),
    }


def null_amplitude(n, sd, trials=200, sample_every=4, seed=0, **kw):
    """The best-fit amplitude the SAME fitter recovers from pure noise. This is the floor a measured amplitude
    must clear — a free choice of frequency guarantees a non-zero fit even when nothing is there."""
    rng = np.random.default_rng(seed)
    amps, r2s = [], []
    for _ in range(trials):
        f = fit_cycle(rng.normal(0.0, sd, n), sample_every=sample_every, **kw)
        amps.append(f["amplitude"]); r2s.append(f["r2"])
    a, r = np.asarray(amps), np.asarray(r2s)
    return {"amp_mean": float(a.mean()), "amp_p95": float(np.quantile(a, 0.95)), "amp_max": float(a.max()),
            "r2_mean": float(r.mean()), "r2_p95": float(np.quantile(r, 0.95)), "r2_max": float(r.max())}


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from probe_cycle_power import synth

    print("Sinusoid fit vs its own null. True period 900 steps = 75.0 yr, noise sd 0.20.\n")
    nul = null_amplitude(225, 0.20, trials=200)
    print(f"NULL (pure noise, same fitter, 200 trials):")
    print(f"   best-fit amplitude  mean {nul['amp_mean']:.3f}   p95 {nul['amp_p95']:.3f}   max {nul['amp_max']:.3f}")
    print(f"   fit r2              mean {nul['r2_mean']:.3f}   p95 {nul['r2_p95']:.3f}   max {nul['r2_max']:.3f}")
    print(f"   => an amplitude below ~{nul['amp_p95']:.3f} is indistinguishable from noise.\n")

    print(f"{'true amp':>9} {'fit amp':>9} {'fit period':>11} {'r2':>7}  {'verdict':>22}")
    print("-" * 64)
    for amp in (0.0, 0.05, 0.10, 0.20, 0.30, 0.45):
        y = synth(900, amp, 0.20, rng=np.random.default_rng(3))
        f = fit_cycle(y)
        v = "clears null" if f["amplitude"] > nul["amp_p95"] else "WITHIN NOISE"
        print(f"{amp:9.2f} {f['amplitude']:9.3f} {f['period_years']:10.1f}y {f['r2']:7.3f}  {v:>22}")
