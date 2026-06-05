"""Shared softmax decision machinery used by CarbonDecision and BoundedRationalSi."""
from __future__ import annotations

import math
from random import Random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.agents.perception import CellView, Perception


def _normalize(vals: list[float]) -> list[float]:
    """Scale a list to [0, 1] by dividing by the maximum positive value."""
    v_max = max(vals) if any(v > 0 for v in vals) else 1.0
    return [v / v_max for v in vals]


class SoftmaxDecision:
    """Abstract base for softmax-based decision strategies.

    Subclasses implement:
      compute_utilities(agent, cells) -> list[float]   (already on [0,1] scale)
      temperature(agent)             -> float
    """

    def compute_utilities(
        self,
        agent: "BaseAgent",
        cells: tuple["CellView", ...],
    ) -> list[float]:
        raise NotImplementedError

    def temperature(self, agent: "BaseAgent") -> float:
        raise NotImplementedError

    def select_target(
        self,
        agent: "BaseAgent",
        perception: "Perception",
        rng: Random,
    ) -> tuple[int, int]:
        cells = perception.visible_cells
        if not cells:
            return agent.pos

        utilities = self.compute_utilities(agent, cells)
        sig = self.temperature(agent)

        scaled = [u / sig for u in utilities]
        max_s = max(scaled)
        exp_vals = [math.exp(s - max_s) for s in scaled]
        total = sum(exp_vals)
        probs = [e / total for e in exp_vals]

        roll = rng.random()
        cumulative = 0.0
        for cell, p in zip(cells, probs):
            cumulative += p
            if roll <= cumulative:
                return (cell.x, cell.y)
        return (cells[-1].x, cells[-1].y)
