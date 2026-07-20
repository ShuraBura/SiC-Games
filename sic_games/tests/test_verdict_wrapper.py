"""Tests for `outputs/phase1_biome_mortality/verdict.py` — the structural enforcement of MECHANISM_CHARTER §10.

These lock in the ENFORCEMENT, not any particular scientific claim: render() must be unusable without a
positive control and a null, must refuse outright if the positive control failed, and must downgrade a
statistically-significant-looking effect that fails goodness-of-fit (D12).
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "outputs", "phase1_biome_mortality"))
from verdict import DetectorNotValidated, PositiveControlFailed, Verdict


def test_render_refuses_without_positive_control():
    v = Verdict("t").null(np.random.default_rng(0).normal(0, 1, 50)).measure(3.0)
    with pytest.raises(DetectorNotValidated):
        v.render()


def test_render_refuses_without_null():
    v = Verdict("t").positive_control(recovered=1.0, expected=1.0, tol=0.1).measure(3.0)
    with pytest.raises(DetectorNotValidated):
        v.render()


def test_render_refuses_without_a_measurement():
    v = (Verdict("t").positive_control(recovered=1.0, expected=1.0, tol=0.1)
         .null(np.random.default_rng(0).normal(0, 1, 50)))
    with pytest.raises(DetectorNotValidated):
        v.render()


def test_failed_positive_control_blocks_everything():
    """A detector that cannot find a KNOWN effect must not be allowed to rule one out."""
    v = (Verdict("t").positive_control(recovered=0.0, expected=75.0, tol=5.0)
         .null(np.random.default_rng(0).normal(0, 1, 50)).measure(3.0))
    with pytest.raises(PositiveControlFailed):
        v.render()


def test_clean_signal_renders_as_signal():
    rng = np.random.default_rng(0)
    v = (Verdict("t").positive_control(recovered=75.3, expected=75.0, tol=5.0)
         .null(rng.normal(0.05, 0.02, 200)).measure(0.40, fit_r2=0.6))
    out = v.render()
    assert "VERDICT: SIGNAL" in out


def test_r87_case_is_rejected_on_goodness_of_fit_not_the_old_invented_cutoff():
    """Regression guard for the actual R-87/R-87d history: 0.19 clears the null p95, so an amplitude-only
    check would call it a signal (as the old invented-0.2-cutoff report effectively conceded once corrected).
    r2=0.14 is what actually sinks it (D12), and that must be the stated reason."""
    rng = np.random.default_rng(0)
    null = np.clip(rng.normal(0.05, 0.04, 200), 0, None)
    v = (Verdict("t").positive_control(recovered=75.3, expected=75.0, tol=5.0)
         .null(null).measure(0.19, fit_r2=0.14))
    out = v.render()
    assert float(np.quantile(null, 0.95)) < 0.19, "test setup: measured value should clear the null p95"
    assert "REJECTED" in out
    assert "GOODNESS-OF-FIT" in out


def test_second_estimate_disagreement_is_flagged():
    rng = np.random.default_rng(0)
    v = (Verdict("t").positive_control(recovered=1.0, expected=1.0, tol=0.1)
         .null(rng.normal(0, 1, 50)).measure(15.0, fit_r2=0.9)
         .second_estimate("alt method", 22.0, tol=2.0))
    out = v.render()
    assert "DISAGREE" in out


def test_second_estimate_agreement_is_not_flagged():
    rng = np.random.default_rng(0)
    v = (Verdict("t").positive_control(recovered=1.0, expected=1.0, tol=0.1)
         .null(rng.normal(0, 1, 50)).measure(15.0, fit_r2=0.9)
         .second_estimate("alt method", 15.4, tol=2.0))
    out = v.render()
    assert "AGREE" in out and "DISAGREE" not in out


def test_null_requires_at_least_twenty_samples():
    with pytest.raises(ValueError):
        Verdict("t").null([0.1, 0.2, 0.3])


def test_repr_does_not_raise_when_incomplete():
    """__repr__ must be safe to print mid-construction (e.g. in a debugger) — it should describe the
    missing piece, not throw during an interactive session."""
    v = Verdict("incomplete")
    assert "NOT YET RENDERABLE" in repr(v)
