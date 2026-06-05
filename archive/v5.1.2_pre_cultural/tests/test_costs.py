"""Tests for CostModel implementations."""
from sic_games.agents.costs import MetabolicOnly, ScaledMetabolicCost


class _FakeAgent:
    def __init__(self, metabolism: int, wealth: float = 0.0):
        self.metabolism = metabolism
        self.wealth = wealth


def test_metabolic_only_returns_metabolism():
    agent = _FakeAgent(metabolism=3)
    cost = MetabolicOnly().step_cost(agent, {})
    assert cost == 3.0


def test_metabolic_only_ignores_actions():
    agent = _FakeAgent(metabolism=2)
    cost = MetabolicOnly().step_cost(agent, {"moved": True, "messages_sent": 99})
    assert cost == 2.0


def test_metabolic_only_is_float():
    agent = _FakeAgent(metabolism=4)
    cost = MetabolicOnly().step_cost(agent, {})
    assert isinstance(cost, float)


# ── Stage 4.5 Task 3: ScaledMetabolicCost k_carry tests ──────────────────────

def test_k_carry_disabled_no_penalty():
    """k_carry=None (default) does not touch agent.wealth."""
    agent = _FakeAgent(metabolism=2, wealth=1000.0)
    cost_model = ScaledMetabolicCost(beta=5.0, k_carry=None)
    cost = cost_model.step_cost(agent, {})
    assert cost == 10.0          # 2 * 5.0
    assert agent.wealth == 1000.0  # untouched


def test_k_carry_below_ceiling_no_penalty():
    """No penalty when wealth ≤ k_carry * metabolism."""
    # k_carry=10, metabolism=2 → ceiling=20; wealth=15 < 20
    agent = _FakeAgent(metabolism=2, wealth=15.0)
    ScaledMetabolicCost(beta=5.0, k_carry=10.0, phi_carry=0.02).step_cost(agent, {})
    assert agent.wealth == 15.0


def test_k_carry_above_ceiling_applies_penalty():
    """Penalty = phi_carry * (wealth - k_carry * metabolism)."""
    # k_carry=10, metabolism=2 → ceiling=20; wealth=50 → excess=30 → penalty=0.02*30=0.6
    agent = _FakeAgent(metabolism=2, wealth=50.0)
    ScaledMetabolicCost(beta=5.0, k_carry=10.0, phi_carry=0.02).step_cost(agent, {})
    assert abs(agent.wealth - (50.0 - 0.6)) < 1e-9


def test_k_carry_cost_return_unaffected():
    """The returned cost (beta * metabolism) is not changed by k_carry penalty."""
    agent = _FakeAgent(metabolism=3, wealth=200.0)
    cost = ScaledMetabolicCost(beta=5.0, k_carry=10.0, phi_carry=0.02).step_cost(agent, {})
    assert cost == 15.0  # 3 * 5.0
