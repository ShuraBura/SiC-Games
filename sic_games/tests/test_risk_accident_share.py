"""Terrain risk as an ACCIDENT SHARE of a2 (R-106 Addendum 113, `enable_risk_accident_share`).

MODEL_SPEC §4.3.3: terrain accidents are ≈10% of baseline a2 in average-risk terrain, scaling with risk (Hill,
Hurtado & Walker 2007). `risk_mult` multiplies the WHOLE a2 by risk_cell / mean land risk; settled people live on
safer-than-mean land, so the realised factor is 0.44–0.62 (Add.112) and it removes ~half of all age-independent
mortality. With the flag on, the factor is (1 − s) + s·risk_mult, s = 0.10.

These tests pin: default OFF and s = 0.10; the flag is LIVE; and the arithmetic invariant — with it on, the mean risk
factor of every step lies in [1 − s, 1 − s + s·risk_cap] = [0.9, 1.2] (a necessary bound on each agent's factor);
with it off, the realised mean sits below 0.9 in this world
(the defect, measured, so this test fails if the whole-a2 form ever stops removing mortality).
"""
import os
import sys

import pytest

from sic_games.demography import DemographyConfig

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

WORLD = dict(n=900, patch=18, terr="coastal", clim="temperate")


def test_default_off_and_share_is_the_anchor():
    c = DemographyConfig()
    assert c.enable_risk_accident_share is False
    assert c.risk_accident_share == 0.10


def _risk_factors(update, steps=120):
    import battery1_liveness as B1
    w = B1._build(update, **WORLD)
    if not w._demog.enable_terrain_risk:
        pytest.skip("terrain risk is off in this world — nothing to scale")
    lo = hi = None                  # the min / max of the PER-STEP mean factor (a necessary bound on each factor)
    for _ in range(steps):
        n0, s0 = w.a2_n, w.a2_risk_sum
        w.step()
        if w.a2_n > n0:
            m = (w.a2_risk_sum - s0) / (w.a2_n - n0)
            lo = m if lo is None else min(lo, m)
            hi = m if hi is None else max(hi, m)
    return w, w.a2_risk_sum / max(w.a2_n, 1), lo, hi


@pytest.mark.slow
def test_share_form_bounds_every_risk_factor():
    w, mean, lo, hi = _risk_factors(dict(enable_risk_accident_share=True))
    s, cap = w._demog.risk_accident_share, w._demog.risk_cap
    assert (1.0 - s) - 1e-9 <= lo and hi <= (1.0 - s + s * cap) + 1e-9, (lo, hi)
    assert 0.9 <= mean <= 1.2


@pytest.mark.slow
def test_whole_a2_form_removes_mortality_in_this_world():
    """The defect, pinned: the default (whole-a2) factor averages below the share form's floor of 0.9."""
    _, mean, _, _ = _risk_factors({})
    assert mean < 0.9, f"whole-a2 risk factor now averages {mean:.3f} — re-measure Addendum 112"


@pytest.mark.slow
def test_the_flag_changes_the_world():
    import battery1_liveness as B1
    off, _, _ = B1.signature({}, steps=200, **WORLD)
    on, _, _ = B1.signature(dict(enable_risk_accident_share=True), steps=200, **WORLD)
    assert on != off
