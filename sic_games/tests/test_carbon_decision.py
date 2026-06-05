"""Tests for CarbonDecision softmax strategy."""
import math
import random

import pytest

from sic_games.agents.perception import CellView, Perception
from sic_games.agents.strategies.carbon import CarbonDecision


def _decision(**kwargs):
    defaults = dict(
        sigma_base=1.0,
        kappa=2.0,
        cred_scale=10.0,
        matthew_alpha=1.5,
        epsilon=0.01,
        cred_bonus_per_participant=1.0,
    )
    defaults.update(kwargs)
    return CarbonDecision(**defaults)


class _FakeAgent:
    def __init__(self, cred=0.0, phi=0.5, wealth_velocity=0.0):
        self.cred = cred
        self.phi = phi
        self.pos = (5, 5)
        self.wealth_velocity = wealth_velocity


def _perc(*cells):
    return Perception(
        visible_cells=tuple(CellView(x, y, s) for x, y, s in cells),
        current_x=5,
        current_y=5,
    )


def test_sigma_at_zero_cred_equals_sigma_base():
    d = _decision(sigma_base=0.5, kappa=2.0, cred_scale=10.0)
    agent = _FakeAgent(cred=0.0)
    assert d.sigma(agent) == pytest.approx(0.5, rel=1e-6)


def test_sigma_increases_with_cred():
    d = _decision(sigma_base=0.5, kappa=2.0, cred_scale=10.0)
    s0 = d.sigma(_FakeAgent(cred=0.0))
    s1 = d.sigma(_FakeAgent(cred=5.0))
    s2 = d.sigma(_FakeAgent(cred=50.0))
    assert s0 < s1 < s2


def test_sigma_saturates_near_sigma_base_plus_kappa():
    d = _decision(sigma_base=0.5, kappa=2.0, cred_scale=10.0)
    s_high = d.sigma(_FakeAgent(cred=1000.0))
    assert s_high == pytest.approx(0.5 + 2.0, rel=1e-3)


def test_pure_resource_agent_prefers_high_sugar(monkeypatch):
    """phi=0 → resource-only utility → should strongly prefer high-sugar cell."""
    d = _decision(sigma_base=0.1, kappa=0.0)  # low temp for near-greedy
    agent = _FakeAgent(phi=0.0, cred=0.0)
    perc = _perc((5, 5, 0.0), (5, 6, 4.0), (5, 4, 1.0))

    rng = random.Random(42)
    counts = {(5, 5): 0, (5, 6): 0, (5, 4): 0}
    for _ in range(200):
        t = d.select_target(agent, perc, rng)
        counts[t] += 1
    # High-sugar cell should dominate
    assert counts[(5, 6)] > 150


def test_single_cell_always_chosen():
    d = _decision()
    agent = _FakeAgent()
    perc = _perc((5, 5, 3.0))
    rng = random.Random(0)
    assert d.select_target(agent, perc, rng) == (5, 5)


def test_softmax_probabilities_sum_to_one():
    """Verify softmax is a valid distribution for a known utility vector."""
    sigma = 1.0
    utilities = [0.0, 0.5, 1.0]
    exp_vals = [math.exp(u / sigma) for u in utilities]
    total = sum(exp_vals)
    probs = [e / total for e in exp_vals]
    assert sum(probs) == pytest.approx(1.0, abs=1e-9)
    assert probs[2] > probs[1] > probs[0]


def test_uniform_sugar_produces_near_uniform_choice():
    """With equal utilities, all cells should be chosen with equal probability."""
    d = _decision(sigma_base=1.0, kappa=0.0)
    agent = _FakeAgent(phi=0.0, cred=0.0)
    perc = _perc((5, 4, 2.0), (5, 5, 2.0), (5, 6, 2.0))
    rng = random.Random(7)
    counts = {(5, 4): 0, (5, 5): 0, (5, 6): 0}
    for _ in range(600):
        t = d.select_target(agent, perc, rng)
        counts[t] += 1
    for c in counts.values():
        assert 100 < c < 300, f"Expected ~200, got {c}"
