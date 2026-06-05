"""Tests for Stage 3.2 status amplification in CarbonDecision."""
from __future__ import annotations

import math
import random

import pytest

from sic_games.agents.perception import CellView, Perception
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.strategies.si_bounded import BoundedRationalSi


def _decision(beta: float = 1.0, **kwargs) -> CarbonDecision:
    defaults = dict(
        sigma_base=0.5,
        kappa=2.0,
        cred_scale=10.0,
        matthew_alpha=1.5,
        epsilon=0.01,
        cred_bonus_per_participant=1.0,
        velocity_scale=1.0,
        beta=beta,
    )
    defaults.update(kwargs)
    return CarbonDecision(**defaults)


class _Agent:
    def __init__(self, *, cred: float, phi: float, wealth_velocity: float):
        self.cred = cred
        self.phi = phi
        self.wealth_velocity = wealth_velocity
        self.pos = (0, 0)


# ---------------------------------------------------------------------------
# Test 1: Amplification at limits
# ---------------------------------------------------------------------------

def test_amplification_zero_cred_is_one():
    dec = _decision(beta=1.0)
    a = _Agent(cred=0.0, phi=0.5, wealth_velocity=0.0)
    assert dec.amplification(a) == pytest.approx(1.0)


def test_amplification_high_cred_approaches_one_plus_beta():
    dec = _decision(beta=1.5)
    a = _Agent(cred=1000.0, phi=0.5, wealth_velocity=0.0)
    # tanh(1000/10) ≈ 1.0
    assert dec.amplification(a) == pytest.approx(1.0 + 1.5, abs=1e-6)


def test_amplification_at_cred_scale():
    beta = 2.0
    cred_scale = 10.0
    dec = _decision(beta=beta, cred_scale=cred_scale)
    a = _Agent(cred=cred_scale, phi=0.5, wealth_velocity=0.0)
    expected = 1.0 + beta * math.tanh(1.0)
    assert dec.amplification(a) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Test 2: Stress suppression dominates even with maxed amplification
# ---------------------------------------------------------------------------

def test_stress_suppression_dominates_over_amplification():
    # phi=1.0, beta=2.0, cred=50 → amplification ≈ 3.0
    # wealth_velocity=-10 → sigmoid(-10/1.0) ≈ 0.0000454
    # w_C = 1.0 * 3.0 * 0.0000454 ≈ 0.000136 — well below 0.1
    dec = _decision(beta=2.0)
    a = _Agent(cred=50.0, phi=1.0, wealth_velocity=-10.0)
    w_c = dec.w_C_eff(a)
    assert w_c < 0.1


# ---------------------------------------------------------------------------
# Test 3: Thriving high-Cred agent reaches amplified ceiling
# ---------------------------------------------------------------------------

def test_thriving_high_cred_reaches_ceiling():
    phi = 0.8
    beta = 1.0
    dec = _decision(beta=beta)
    # cred=50 → tanh(50/10) ≈ 1.0 → amplification ≈ 1+β = 2.0
    # wealth_velocity=+10 → sigmoid(10) ≈ 1.0
    # expected w_C ≈ phi * (1+beta) * 1.0 = 0.8 * 2.0 = 1.6
    a = _Agent(cred=50.0, phi=phi, wealth_velocity=10.0)
    expected = phi * (1.0 + beta)
    assert dec.w_C_eff(a) == pytest.approx(expected, rel=1e-3)


# ---------------------------------------------------------------------------
# Test 4: β=0 recovers Stage 3 / Stage 2.1 behavior exactly
# ---------------------------------------------------------------------------

def test_beta_zero_recovers_stage3_formula():
    dec = _decision(beta=0.0)
    for cred in [0.0, 5.0, 50.0]:
        a = _Agent(cred=cred, phi=0.6, wealth_velocity=0.5)
        sigmoid = 1.0 / (1.0 + math.exp(-0.5 / 1.0))
        expected = 0.6 * sigmoid
        assert dec.w_C_eff(a) == pytest.approx(expected, rel=1e-9), (
            f"beta=0 w_C should equal phi*sigmoid(v/v0) regardless of cred, "
            f"failed at cred={cred}"
        )


def test_beta_zero_amplification_is_exactly_one():
    dec = _decision(beta=0.0)
    for cred in [0.0, 1.0, 100.0]:
        a = _Agent(cred=cred, phi=0.5, wealth_velocity=0.0)
        assert dec.amplification(a) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Test 5: BoundedRationalSi is unaffected by beta parameter
# ---------------------------------------------------------------------------

def test_si_utility_unchanged_by_beta():
    """Si strategy has no beta; its utilities must be sugar-only regardless."""
    si = BoundedRationalSi(sigma_si=1.051)

    class _SiAgent:
        cred = 99.0
        phi = 1.0
        wealth_velocity = 10.0
        pos = (0, 0)

    cells = (CellView(0, 0, 2.0), CellView(1, 0, 4.0), CellView(2, 0, 6.0))
    utils = si.compute_utilities(_SiAgent(), cells)
    # _normalize: max=6 → [2/6, 4/6, 6/6]
    assert utils == pytest.approx([2 / 6, 4 / 6, 1.0])
