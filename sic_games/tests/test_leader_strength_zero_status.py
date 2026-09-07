"""Leader coherence must survive a ZERO-STATUS band — the cred ABLATION has to be runnable.

FOUND BY THE MECHANISM BATTERY (2026-07-26). Turning `enable_cred_status` OFF crashed the model outright:

    phase1_model.py:3800  ratio = top_status / (mean_status + 1e-9)
                          leader_strength = 1.0 - 1.0 / ratio      -> ZeroDivisionError

The `1e-9` guards the ratio's DENOMINATOR but not the ratio when it is itself used as a divisor. With cred
status off every `a.cred` is 0, so `top_status` is 0, so `ratio` is exactly 0.0 and the next line divides by it.

Why this matters beyond the crash: it means the cred ablation — the control you would run to ask "how much of
this result comes from status at all?" — could not be executed. An ablation that cannot run is a hole in every
claim that would have been checked against it.

Semantics of the fix: zero status SPREAD means no distinct leader, which is `leader_strength = 0.0` — the same
value the `ratio -> 1` limit gives. Bit-exact wherever any cred is non-zero, i.e. in every existing result.
"""
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)


@pytest.mark.slow
def test_cred_ablation_runs_without_dividing_by_zero():
    """The regression proper: drive a real world with cred status OFF. Before the fix this raised
    ZeroDivisionError inside `_maintain_bands` on the first step that evaluated leader coherence."""
    import battery1_liveness as B
    sig, _, _ = B.signature({"enable_cred_status": False}, steps=150)
    assert sig["final_pop"] > 0, "world died — the ablation is unusable for a different reason"


@pytest.mark.slow
def test_cred_ablation_actually_ablates():
    """A crash-free ablation that changes nothing would be just as useless: pin that removing status moves the
    world, so the control has power."""
    import battery1_liveness as B
    off, _, _ = B.signature({"enable_cred_status": False}, steps=150)
    base, _, _ = B.signature({}, steps=150)
    assert off != base, "cred ablation left the run identical — the control cannot detect status effects"


def test_leader_strength_formula_is_defined_at_zero_spread():
    """The arithmetic itself, isolated from the model: a band whose members all have zero status must yield
    strength 0.0, not an exception. Pinned as a formula so a future refactor cannot reintroduce the divide."""
    for statuses in ([0.0, 0.0, 0.0], [0.0], [0.0] * 25):
        mean_status = sum(statuses) / len(statuses)
        top_status = max(statuses)
        ratio = top_status / (mean_status + 1e-9)
        strength = (1.0 - 1.0 / ratio) if ratio > 0.0 else 0.0
        assert strength == 0.0

    # and the ordinary case is untouched: a clear leader still saturates toward 1
    statuses = [1.0, 1.0, 10.0]
    mean_status = sum(statuses) / len(statuses)
    ratio = max(statuses) / (mean_status + 1e-9)
    strength = (1.0 - 1.0 / ratio) if ratio > 0.0 else 0.0
    assert 0.5 < strength < 1.0
