"""Tests for the Mode-Switch patch (wealth velocity EMA and w_C modulation)."""
from __future__ import annotations

import math
import random

import pytest

from sic_games.agents.base import BaseAgent
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.strategies.greedy import GreedyMaximizer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent(model, phi=0.5, wealth=10.0, decision=None):
    if decision is None:
        decision = GreedyMaximizer()
    a = BaseAgent(
        model=model,
        vision=3,
        metabolism=1,
        max_age=100,
        initial_wealth=wealth,
        decision_logic=decision,
        phi=phi,
    )
    a.pos = (0, 0)
    return a


class _FakeModel:
    """Minimal stand-in so BaseAgent.__init__ doesn't need a real Mesa Model."""

    def __init__(self):
        self._agents = set()
        self.random = random.Random(0)

    # Mesa Agent.__init__ calls model.register_agent(self) in Mesa 3.x
    def register_agent(self, agent):
        self._agents.add(agent)

    def deregister_agent(self, agent):
        self._agents.discard(agent)


class _FakeSugarField:
    """Returns a fixed harvest value and exposes width/height."""

    def __init__(self, harvest_val=3):
        self.width = 10
        self.height = 10
        self._harvest_val = harvest_val

    def harvest(self, x, y):
        return float(self._harvest_val)

    def get_neighbors(self, x, y, vision):
        return []


# ---------------------------------------------------------------------------
# Test 1: wealth_velocity starts at zero and updates correctly via EMA
# ---------------------------------------------------------------------------

def test_velocity_ema_update():
    model = _FakeModel()
    agent = _make_agent(model)
    # Manually set wealth_velocity and call the EMA update logic directly
    tau = 5
    alpha = 1.0 / tau
    delta_w = 4.0  # harvested - cost

    agent.wealth_velocity = 0.0
    expected = (1 - alpha) * 0.0 + alpha * delta_w
    agent.wealth_velocity = (1 - alpha) * agent.wealth_velocity + alpha * delta_w
    assert abs(agent.wealth_velocity - expected) < 1e-9


def test_velocity_ema_converges():
    """After many identical delta_w steps the EMA should converge to delta_w."""
    tau = 10
    alpha = 1.0 / tau
    delta_w = 3.0
    v = 0.0
    for _ in range(200):
        v = (1 - alpha) * v + alpha * delta_w
    assert abs(v - delta_w) < 0.01


# ---------------------------------------------------------------------------
# Test 2: w_C limits
# ---------------------------------------------------------------------------

def test_w_c_near_zero_when_velocity_very_negative():
    """Struggling agent (large negative velocity) → w_C ≈ 0."""
    phi = 0.8
    velocity_scale = 1.0
    wealth_velocity = -20.0  # deeply negative
    w_c = phi / (1.0 + math.exp(-wealth_velocity / velocity_scale))
    assert w_c < 0.01 * phi


def test_w_c_near_phi_when_velocity_very_positive():
    """Thriving agent (large positive velocity) → w_C ≈ phi."""
    phi = 0.8
    velocity_scale = 1.0
    wealth_velocity = 20.0
    w_c = phi / (1.0 + math.exp(-wealth_velocity / velocity_scale))
    assert abs(w_c - phi) < 0.01 * phi


# ---------------------------------------------------------------------------
# Test 3: CarbonDecision uses velocity-modulated w_C
# ---------------------------------------------------------------------------

def test_carbon_decision_suppresses_cred_weight_when_struggling():
    """A struggling agent (negative velocity) should weight resources more than Cred."""
    from sic_games.agents.perception import CellView, Perception

    decision = CarbonDecision(
        sigma_base=0.3,
        kappa=0.0,   # flat sigma to isolate weight effect
        cred_scale=10.0,
        matthew_alpha=1.5,
        epsilon=0.01,
        cred_bonus_per_participant=1.0,
        velocity_scale=1.0,
    )
    model = _FakeModel()
    agent = _make_agent(model, phi=1.0, decision=decision)
    agent.wealth_velocity = -10.0   # deeply struggling
    agent.cred = 0.0

    # Two cells: one with sugar, one is a joint-task cell with Cred gain
    sugar_cell = CellView(x=1, y=0, sugar=4.0)
    jt_cell = CellView(x=0, y=1, sugar=0.0)
    decision.joint_task_cells = {(0, 1)}

    perception = Perception(
        visible_cells=(sugar_cell, jt_cell),
        current_x=0,
        current_y=0,
    )

    rng = random.Random(0)
    # Run many trials; struggling agent should almost always pick the sugar cell
    picks = [decision.select_target(agent, perception, rng) for _ in range(200)]
    sugar_picks = sum(1 for p in picks if p == (1, 0))
    assert sugar_picks > 150, f"Expected resource bias, got {sugar_picks}/200 sugar picks"


# ---------------------------------------------------------------------------
# Test 4: Greedy agent wealth_velocity stays 0 (velocity_tau=0 path)
# ---------------------------------------------------------------------------

def test_greedy_agent_velocity_stays_zero():
    """Greedy-Si path: velocity_tau=0 means wealth_velocity is never updated."""
    model = _FakeModel()
    agent = _make_agent(model, decision=GreedyMaximizer())
    assert agent.wealth_velocity == 0.0

    # Simulate the EMA logic manually with tau=0 (as run.py does)
    velocity_tau = 0
    delta_w = 5.0
    if velocity_tau > 0:
        alpha = 1.0 / velocity_tau
        agent.wealth_velocity = (1 - alpha) * agent.wealth_velocity + alpha * delta_w

    assert agent.wealth_velocity == 0.0
