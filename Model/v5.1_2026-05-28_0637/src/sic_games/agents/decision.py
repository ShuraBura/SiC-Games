from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.agents.perception import Perception


class DecisionLogic(Protocol):
    """How an agent picks its next cell, given what it perceives.

    Stage 1: GreedyMaximizer (simple Si baseline).
    Stage 2: CarbonDecision (status-coupled softmax).
    Stage 3: BoundedRationalSi.
    """

    def select_target(
        self,
        agent: "BaseAgent",
        perception: "Perception",
        rng: object,
    ) -> tuple[int, int]:
        """Return (x, y) of the cell the agent will move to this step."""
        ...
