"""`_condition` must sample the metabolic TROUGH, and the S0 branch it feeds must not be silently dead.

THE DEFECT (found by the mechanism battery, 2026-07-27). `enable_nutrition_synergy` has two branches
(phase1_model.py:4011): with `enable_condition` ON it multiplies mortality by the condition EMA, with it OFF by
the instantaneous post-harvest reserve. The EMA read `_fed_reserve` — wealth POST-harvest but PRE-burn, i.e. the
PEAK of the metabolic cycle — and `_frac` clamps at 1.0, so any agent whose harvest topped it up read
"completely fed". Measured `_condition`: mean 0.9998 in a crowded BOREAL world. The multiplier was ~1.0002 and
the whole hunger→disease channel was OFF whenever both flags were on (ablation displacement 0.3468 -> 0.0000).

THE FIX: sample after maintenance and movement costs are deducted. `_fed_reserve` is deliberately unchanged —
energetic fertility (phase1_model.py:2220) and the legacy synergy branch both want the post-harvest value.

WHAT THE FIX DOES *NOT* BUY, pinned here so nobody re-reads it as success. Post-fix, `_condition` is ~0.32 for
essentially every agent (p05 0.314, p95 0.347) and reads the SAME in a crowded boreal world as in a comfortable
temperate one. Reserves in this model are homeostatic and shortfall is lethal quickly, so every survivor sits at
the setpoint and there is no chronic-malnutrition state to detect. The branch therefore applies a near-UNIFORM
~2x mortality multiplier rather than discriminating between hungry and well-fed agents — which is not what S0
claims to model. `enable_condition` stays OFF by default; the instantaneous branch is the working one.
"""
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

STRESSED = dict(n=900, patch=18, terr="flat", clim="boreal")


def _cfg(**over):
    base = dict(enable_condition=True, enable_nutrition_synergy=True)
    base.update(over)
    return base


@pytest.mark.slow
def test_condition_registers_hardship_instead_of_saturating():
    """The regression proper. Pre-fix this sat at 0.9998 with essentially no agent below 0.999."""
    import battery1_liveness as B1
    w = B1._build(_cfg(), **STRESSED)
    for _ in range(200):
        w.step()
        if not w.agent_list:
            break
    cond = [a._condition for a in w.agent_list]
    assert cond, "world died"
    mean = sum(cond) / len(cond)
    assert mean < 0.9, (
        f"_condition mean {mean:.4f} — the EMA is saturated again, which silently disables the S0 branch. "
        f"Check that it is sampled AFTER the burn/move-cost deductions, not from `_fed_reserve`.")


@pytest.mark.slow
def test_the_s0_branch_is_not_silently_dead():
    """The consequence that actually mattered: with condition ON, ablating nutrition-synergy must still CHANGE
    the world. Pre-fix the two runs were bit-identical, i.e. the mechanism was on and doing nothing."""
    import battery1_liveness as B1
    on, _, _ = B1.signature(_cfg(), steps=200, **STRESSED)
    off, _, _ = B1.signature(_cfg(enable_nutrition_synergy=False), steps=200, **STRESSED)
    assert on != off, "nutrition-synergy ablation is bit-identical with condition ON — the S0 branch is dead"


@pytest.mark.slow
def test_condition_is_near_uniform_KNOWN_LIMITATION():
    """DOCUMENTED LIMITATION, not an endorsement. Reserves are homeostatic and shortfall is lethal fast, so
    survivors cluster at the setpoint: `_condition` barely discriminates, and the S0 branch acts as a level
    shift on mortality rather than as a hunger DISCRIMINATOR. Pinned so the limitation stays visible; if this
    test ever fails because the spread got large, S0 has become meaningful and the docstrings should say so."""
    import statistics

    import battery1_liveness as B1
    w = B1._build(_cfg(), **STRESSED)
    for _ in range(200):
        w.step()
        if not w.agent_list:
            break
    cond = [a._condition for a in w.agent_list]
    assert statistics.pstdev(cond) < 0.25, (
        "condition spread is now WIDE — the known limitation may have been fixed; if so, update this test and "
        "the S0 notes rather than widening the bound.")
