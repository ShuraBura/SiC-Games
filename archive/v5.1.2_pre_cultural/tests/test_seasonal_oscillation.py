"""Tests for Stage 4 seasonal oscillation mechanic.

5 tests per blueprint §6:
  1. Capacity formula: c_eff matches analytic at t=0, T/4, T/2, 3T/4, T
  2. Sugar shedding: sugar > effective_capacity is clipped down
  3. Growback respects c_eff, not c_max
  4. NullPerturbation: effective_capacity always equals max_capacity
  5. Protocol duck-typing: both implementations have apply()
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from sic_games.config import Config
from sic_games.run import SugarWorld
from sic_games.world import SugarField
from sic_games.world_perturbation import NullPerturbation, SeasonalOscillation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_field(max_capacity: int = 4) -> SugarField:
    return SugarField(
        width=10, height=10,
        peaks=[(5, 5)],
        max_capacity=max_capacity,
        band_width_k=6,
        alpha=1,
    )


# ---------------------------------------------------------------------------
# Test 1: Capacity formula matches analytic at t = 0, T/4, T/2, 3T/4, T
# ---------------------------------------------------------------------------

def test_seasonal_capacity_formula():
    A = 0.5
    T = 200
    field = _make_field(max_capacity=4)
    osc = SeasonalOscillation(amplitude=A, period=T)

    # Pick the peak cell — it has c_max = 4
    peak_x, peak_y = 5, 5
    c_max_peak = int(field.capacity[peak_x, peak_y])

    for t in [0, T // 4, T // 2, (3 * T) // 4, T]:
        osc.apply(field, t, rng=None)
        expected = c_max_peak * (1.0 - A * math.sin(math.pi * t / T) ** 2)
        got = float(field.effective_capacity[peak_x, peak_y])
        assert abs(got - expected) < 1e-5, (
            f"t={t}: expected c_eff={expected:.6f}, got {got:.6f}"
        )


# ---------------------------------------------------------------------------
# Test 2: Sugar shedding clips sugar to effective_capacity
# ---------------------------------------------------------------------------

def test_sugar_shedding():
    field = _make_field(max_capacity=4)
    # Force sugar above effective_capacity
    field.sugar[:] = 4.0
    field.effective_capacity[:] = 2.0
    field.shed_excess_sugar()
    assert float(field.sugar.max()) <= 2.0 + 1e-9
    assert float(field.sugar.min()) <= 2.0 + 1e-9


def test_sugar_shedding_does_not_reduce_below_effective_capacity():
    field = _make_field(max_capacity=4)
    field.sugar[:] = 1.5
    field.effective_capacity[:] = 2.0
    field.shed_excess_sugar()
    # Sugar below c_eff must be untouched
    assert abs(float(field.sugar[0, 0]) - 1.5) < 1e-9


# ---------------------------------------------------------------------------
# Test 3: Growback respects c_eff (not c_max) during trough
# ---------------------------------------------------------------------------

def test_growback_respects_effective_capacity():
    field = _make_field(max_capacity=4)
    # Set c_eff to 2 (trough) for all cells, sugar to 0
    field.effective_capacity[:] = 2.0
    field.sugar[:] = 0.0
    # After one growback (alpha=1), sugar should reach min(1, 2) = 1
    field.growback()
    assert float(field.sugar.max()) <= 2.0 + 1e-9
    assert float(field.sugar.max()) == pytest.approx(1.0)

    # Run many growbacks: sugar caps at 2.0, not 4.0
    for _ in range(10):
        field.growback()
    assert float(field.sugar.max()) == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# Test 4: NullPerturbation leaves effective_capacity equal to max_capacity
# ---------------------------------------------------------------------------

def test_null_perturbation_leaves_effective_capacity_unchanged():
    field = _make_field(max_capacity=4)
    null = NullPerturbation()
    cap_before = field.capacity.copy()

    for t in range(500):
        null.apply(field, t, rng=None)

    # effective_capacity was initialized as a copy of capacity; null must not change it
    np.testing.assert_array_equal(field.effective_capacity, cap_before)


# ---------------------------------------------------------------------------
# Test 5: Protocol duck-typing — both implementations have apply()
# ---------------------------------------------------------------------------

def test_protocol_duck_typing():
    null = NullPerturbation()
    osc  = SeasonalOscillation(amplitude=0.5, period=200)
    field = _make_field()

    # Both must be callable with (field, t, rng) without raising
    null.apply(field, 0, rng=None)
    osc.apply(field, 0, rng=None)
    assert hasattr(null, "apply")
    assert hasattr(osc, "apply")


# ---------------------------------------------------------------------------
# Integration: oscillation visible in a short run via effective_capacity
# ---------------------------------------------------------------------------

def test_oscillation_fires_in_run():
    """Verify that mean_effective_capacity oscillates over 400 steps."""
    raw = {
        "seed": 42,
        "agents": {"initial_population": 50},
        "decision": {"strategy": "greedy"},
        "perturbation": {"type": "seasonal", "amplitude": 0.5, "period": 200},
        "run": {"n_steps": 400, "output_dir": "outputs/_test_oscillation"},
    }
    cfg = Config.model_validate(raw)
    world = SugarWorld(cfg)
    df = world.run()

    # At t=100 (T/2): c_eff should be near c_max*(1-0.5) = half capacity
    # At t=200 (T):   c_eff should be back near c_max
    t100 = float(df[df["step"] == 100]["mean_effective_capacity"].iloc[0])
    t200 = float(df[df["step"] == 200]["mean_effective_capacity"].iloc[0])
    t400 = float(df[df["step"] == 400]["mean_effective_capacity"].iloc[0])

    # t=100 is trough (half capacity), t=200 is peak (full capacity)
    assert t100 < t200, f"Trough at t=100 ({t100:.3f}) should be below peak at t=200 ({t200:.3f})"
    # t=400 is also a peak (400 = 2*T): should match t=200 closely
    assert abs(t400 - t200) < 0.1, f"t=400 and t=200 both peaks; got {t400:.3f} vs {t200:.3f}"


# ---------------------------------------------------------------------------
# Test 7: Asymmetric seasonal — trough at t=tf*T, analytic match at key steps
# ---------------------------------------------------------------------------

def test_asymmetric_trough_at_correct_step():
    """With trough_fraction=0.6, minimum capacity is reached at t=tf*T=120, not T/2=100."""
    A = 0.5
    T = 200
    tf = 0.6
    field = _make_field(max_capacity=4)
    osc = SeasonalOscillation(amplitude=A, period=T, trough_fraction=tf)

    peak_x, peak_y = 5, 5
    c_max = int(field.capacity[peak_x, peak_y])

    # Key analytic checkpoints
    checkpoints = [
        # (t,  expected_factor)
        (0,   1.0),            # peak: phase=0, sin(0)²=0
        (120, 1.0 - A),        # trough: t_in=120==trough_end → recovery branch at phase=π, sin(π/2)²=1
        (200, 1.0),            # peak again: t_in=200, phase=2π, sin(π)²=0
    ]
    for t_check, expected_factor in checkpoints:
        osc.apply(field, t_check, rng=None)
        got = float(field.effective_capacity[peak_x, peak_y])
        expected = c_max * expected_factor
        assert abs(got - expected) < 1e-5, (
            f"t={t_check}: expected factor={expected_factor} → c_eff={expected:.6f}, got {got:.6f}"
        )

    # At t=100 (symmetric trough location) factor must NOT be (1-A) when tf≠0.5.
    # phase at t=100: π*100/(0.6*200) = 5π/6; factor = 1 - 0.5*sin(5π/12)² ≈ 0.647
    osc.apply(field, 100, rng=None)
    c_eff_100 = float(field.effective_capacity[peak_x, peak_y])
    # It should be higher than the true trough (i.e. not yet at minimum)
    true_trough = c_max * (1.0 - A)
    assert c_eff_100 > true_trough + 0.05, (
        f"At t=100, c_eff={c_eff_100:.4f} should be above trough={true_trough:.4f} "
        f"when tf=0.6 (trough is at t=120)"
    )


# ---------------------------------------------------------------------------
# Test 8: Asymmetric trough_fraction=0.5 recovers symmetric formula exactly
# ---------------------------------------------------------------------------

def test_asymmetric_tf05_matches_symmetric():
    """trough_fraction=0.5 (asymmetric code path) matches original symmetric formula."""
    A = 0.5
    T = 200
    field_sym = _make_field(max_capacity=4)
    field_asym = _make_field(max_capacity=4)
    osc_sym  = SeasonalOscillation(amplitude=A, period=T)             # tf=0.5 (default → fast path)
    osc_asym = SeasonalOscillation(amplitude=A, period=T, trough_fraction=0.5)  # explicit 0.5

    peak_x, peak_y = 5, 5
    for t in [0, 25, 50, 75, 100, 125, 150, 175, 200]:
        osc_sym.apply(field_sym, t, rng=None)
        osc_asym.apply(field_asym, t, rng=None)
        sym_val  = float(field_sym.effective_capacity[peak_x, peak_y])
        asym_val = float(field_asym.effective_capacity[peak_x, peak_y])
        assert abs(sym_val - asym_val) < 1e-9, (
            f"t={t}: symmetric={sym_val:.8f} vs asymmetric-tf0.5={asym_val:.8f}"
        )
