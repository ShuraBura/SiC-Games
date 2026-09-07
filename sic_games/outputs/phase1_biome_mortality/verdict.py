"""THE WRAPPER — makes MECHANISM_CHARTER §10 (the diagnostic discipline) structural instead of remembered.

Built 2026-07-20 after a single day produced six instrument artifacts (R-82's unit error, R-85's phantom dead
knobs, R-87's uncalibrated threshold, the sinusoid fit's grid-ceiling trend, the correlation-time estimator
disagreement, R-86's age-biased lift) — every one caught by the supervisor asking to see something, none by the
rules being followed voluntarily. Rules that live in a docstring get skipped under time pressure. This does not
let you skip them: `Verdict.render()` raises unless a null floor and a positive control are attached, and it
downgrades a clean-looking effect size if the goodness-of-fit is poor.

Usage:
    v = Verdict("H-CYCLES: 167yr-lag arm")
    v.positive_control(recovered=75.3, expected=75.0, tol=5.0)   # D1 — required
    v.null(samples=null_ac_peaks)                                 # D2 — required
    v.measure(value=0.19, fit_r2=0.14)                            # the actual finding
    print(v.render())                                             # raises if either required call is missing

`v.render()` cannot be called (raises RuntimeError) until both `positive_control()` and `null()` have been
supplied. If the positive control FAILED, `render()` refuses outright — a detector that cannot find a known
effect cannot be trusted to rule one out.
"""
from __future__ import annotations

import numpy as np


class DetectorNotValidated(RuntimeError):
    """Raised by Verdict.render() when D1 (positive control) or D2 (null floor) is missing."""


class PositiveControlFailed(RuntimeError):
    """Raised when the positive control itself did not recover the known effect — the instrument is broken."""


class Verdict:
    """One measured claim, forced through D1 (positive control) + D2 (null floor) + D12 (goodness-of-fit)
    before it can be printed. Charter D14 (two estimators) is supported via `second_estimate()`."""

    def __init__(self, name: str, r2_floor: float = 0.30):
        self.name = name
        self.r2_floor = r2_floor
        self._pc: dict | None = None
        self._null: np.ndarray | None = None
        self._measured: float | None = None
        self._fit_r2: float | None = None
        self._second: tuple[str, float, float] | None = None       # (label, value, tol) — D14
        self._note: str = ""

    def positive_control(self, recovered: float, expected: float, tol: float, label: str = "") -> "Verdict":
        """D1. Record that a KNOWN effect of size `expected` was injected and the detector recovered
        `recovered`. Must be within `tol` or every subsequent verdict from this detector is untrustworthy —
        `render()` will refuse to run at all."""
        ok = abs(recovered - expected) <= tol
        self._pc = {"recovered": recovered, "expected": expected, "tol": tol, "ok": ok, "label": label}
        return self

    def null(self, samples) -> "Verdict":
        """D2. The distribution of the SAME statistic computed on data known to contain no effect (shuffled,
        synthetic noise, or a permutation null). Never an invented threshold."""
        arr = np.asarray(samples, dtype=float)
        if len(arr) < 20:
            raise ValueError(f"null() needs >=20 samples for a usable p95/max; got {len(arr)}")
        self._null = arr
        return self

    def measure(self, value: float, fit_r2: float | None = None) -> "Verdict":
        """The actual measurement. `fit_r2` is required whenever the claim rests on a fitted MODEL (a period, a
        trend, a slope) rather than a raw statistic — D12: effect size alone is not sufficient, because a fitter
        free to choose its own frequency/shape will always report SOME amplitude, even from pure noise."""
        self._measured = value
        self._fit_r2 = fit_r2
        return self

    def second_estimate(self, label: str, value: float, tol: float) -> "Verdict":
        """D14. An INDEPENDENT estimator of the same headline quantity (different method, not a re-run of the
        same code). render() will flag disagreement rather than silently averaging or picking one."""
        self._second = (label, value, tol)
        return self

    def note(self, text: str) -> "Verdict":
        self._note = text
        return self

    # ------------------------------------------------------------------

    def render(self) -> str:
        if self._pc is None:
            raise DetectorNotValidated(
                f"[{self.name}] D1 VIOLATION: no positive_control() attached. "
                f"Cannot report a negative (or a positive) without first showing this detector finds a KNOWN "
                f"effect. Call .positive_control(recovered=..., expected=..., tol=...) before render()."
            )
        if not self._pc["ok"]:
            raise PositiveControlFailed(
                f"[{self.name}] positive control FAILED: recovered {self._pc['recovered']:.4g} vs expected "
                f"{self._pc['expected']:.4g} (tol {self._pc['tol']:.4g}). The detector cannot find a KNOWN "
                f"effect, so it cannot be trusted to rule one out here. Fix the detector before trusting any "
                f"verdict from it."
            )
        if self._null is None:
            raise DetectorNotValidated(
                f"[{self.name}] D2 VIOLATION: no null() attached. Cannot judge whether {self._measured!r} is "
                f"a real effect without knowing what this statistic reads on data with NO effect. Call "
                f".null(samples=...) before render()."
            )
        if self._measured is None:
            raise DetectorNotValidated(f"[{self.name}] no measure() attached — nothing to render.")

        p95 = float(np.quantile(self._null, 0.95))
        nmax = float(self._null.max())
        z = (self._measured - self._null.mean()) / self._null.std() if self._null.std() > 0 else float("nan")
        clears_p95 = self._measured > p95
        clears_max = self._measured > nmax

        fit_ok = True
        fit_note = ""
        if self._fit_r2 is not None:
            fit_ok = self._fit_r2 >= self.r2_floor
            fit_note = f"  fit_r2={self._fit_r2:.3f} ({'>=':s}{self.r2_floor:.2f} required)"
            if not fit_ok:
                fit_note += "  *** GOODNESS-OF-FIT TOO LOW — effect size alone is not sufficient (D12) ***"

        verdict = "SIGNAL" if (clears_p95 and fit_ok) else ("ABOVE NOISE MAX, weak fit" if clears_max and not fit_ok
                                                              else "WITHIN NOISE" if not clears_p95 else "SIGNAL")
        if clears_p95 and not fit_ok:
            verdict = "REJECTED — clears null but fails goodness-of-fit (D12)"

        lines = [
            f"=== {self.name} ===",
            f"  positive control : recovered {self._pc['recovered']:.4g} vs expected {self._pc['expected']:.4g} "
            f"(tol {self._pc['tol']:.4g})  [{self._pc['label'] or 'ok'}]",
            f"  null (n={len(self._null)}): mean {self._null.mean():.4g}  p95 {p95:.4g}  max {nmax:.4g}",
            f"  measured         : {self._measured:.4g}   z={z:.2f}   "
            f"{'clears p95' if clears_p95 else 'within null'}{fit_note}",
            f"  VERDICT: {verdict}",
        ]
        if self._second is not None:
            label, val, tol = self._second
            agree = abs(val - self._measured) <= tol
            lines.append(f"  D14 second estimate ({label}): {val:.4g} vs {self._measured:.4g}  "
                        f"{'AGREE' if agree else '*** DISAGREE — do not trust either without reconciling ***'}")
        if self._note:
            lines.append(f"  note: {self._note}")
        return "\n".join(lines)

    def __repr__(self):
        try:
            return self.render()
        except (DetectorNotValidated, PositiveControlFailed) as e:
            return f"<Verdict {self.name!r}: NOT YET RENDERABLE — {e}>"


# ----------------------------------------------------------------------
# SELF-TEST + RETROFIT DEMONSTRATION: today's actual mistakes, reproduced through the wrapper, to prove it
# actually blocks them rather than just describing them.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("1. The wrapper REFUSES a verdict with no positive control:")
    v = Verdict("demo A")
    v.null(np.random.default_rng(0).normal(0.09, 0.03, 100))
    v.measure(0.19)
    try:
        v.render()
        print("   *** FAILED TO RAISE — bug in the wrapper ***")
    except DetectorNotValidated as e:
        print(f"   raised correctly: {e}\n")

    print("2. The wrapper REFUSES a verdict with no null:")
    v2 = Verdict("demo B")
    v2.positive_control(recovered=75.3, expected=75.0, tol=5.0)
    v2.measure(0.19)
    try:
        v2.render()
        print("   *** FAILED TO RAISE — bug in the wrapper ***")
    except DetectorNotValidated as e:
        print(f"   raised correctly: {e}\n")

    print("3. RETROFIT of R-87's actual mistake — 0.19 against an INVENTED 0.2 cutoff vs the MEASURED null:")
    rng = np.random.default_rng(0)
    white_noise_peaks = [max(0.0, x) for x in rng.normal(0.05, 0.04, 200)]  # stand-in for the measured floor
    v3 = Verdict("R-87 autocorrelation peak, 167yr-lag arm", r2_floor=0.30)
    v3.positive_control(recovered=75.3, expected=75.0, tol=5.0, label="75yr synthetic cycle recovered")
    v3.null(white_noise_peaks)
    v3.measure(0.19, fit_r2=0.14)      # the REAL r2 from R-87d — this is what actually sinks it
    print(v3.render())
    print("\n   (0.19 clears the null p95 on its own — the OLD invented-0.2-cutoff report called this")
    print("   'weak/none' for the wrong reason. The wrapper correctly flags it as REJECTED, but on the")
    print("   right grounds: r2=0.14 fails goodness-of-fit, exactly what D12 says a verdict needs.)\n")

    print("4. RETROFIT of R-86's age-bias mistake — the wrapper does not know about age-gating, which is")
    print("   the point: it can only ever be as good as what you measure and hand it. It is a NULL/CONTROL/FIT")
    print("   enforcer, not a substitute for asking the right question. Recorded here as the limitation.")
