from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent


class CostModel(Protocol):
    def step_cost(self, agent: "BaseAgent", actions_taken: dict) -> float:
        ...


class MetabolicOnly:
    """Stage 1: cost = agent.metabolism, regardless of actions."""

    def step_cost(self, agent: "BaseAgent", actions_taken: dict) -> float:
        return float(agent.metabolism)


class ScaledMetabolicCost:
    """Stage 4.3: Si differential metabolism — cost = metabolism × beta.

    β=5.0 default (conservative silicon; 5× biological brain energy budget).
    C agents always use MetabolicOnly (β=1). Si agents use this class.
    β is supplied from SiBoundedConfig.beta_metabolism and must NOT be
    hardcoded in BaseAgent.

    Stage 4.5 Task 3: optional per-agent wealth carrying cost.
    When k_carry is not None and agent.wealth > k_carry * metabolism,
    a penalty of phi_carry * excess wealth is deducted from agent.wealth
    as a side effect, discouraging hoarding and encouraging fission/dormancy.
    k_carry=None (default) preserves all prior behaviour.
    """

    def __init__(
        self,
        beta: float = 1.0,
        k_carry: float | None = None,
        phi_carry: float = 0.02,
    ) -> None:
        self.beta = float(beta)
        self.k_carry = float(k_carry) if k_carry is not None else None
        self.phi_carry = float(phi_carry)

    def step_cost(self, agent: "BaseAgent", actions_taken: dict) -> float:
        # Stage 4.5: apply wealth carrying-cost penalty as side effect (Si only).
        if self.k_carry is not None:
            ceiling = self.k_carry * float(agent.metabolism)
            if agent.wealth > ceiling:
                penalty = self.phi_carry * (agent.wealth - ceiling)
                agent.wealth -= penalty
        return float(agent.metabolism) * self.beta
