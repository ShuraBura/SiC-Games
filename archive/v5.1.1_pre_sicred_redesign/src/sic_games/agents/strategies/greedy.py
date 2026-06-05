from __future__ import annotations

import math
from random import Random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.agents.perception import Perception


class GreedyMaximizer:
    """Vanilla Sugarscape movement rule M.

    1. Find visible unoccupied cells with maximum sugar.
    2. Among ties, pick the cell nearest (toroidal) to the agent.
    3. Among ties on both sugar and distance, pick uniformly at random.
    """

    def select_target(
        self,
        agent: "BaseAgent",
        perception: "Perception",
        rng: Random,
    ) -> tuple[int, int]:
        cells = perception.visible_cells
        if not cells:
            return agent.pos

        max_sugar = max(c.sugar for c in cells)
        candidates = [c for c in cells if c.sugar == max_sugar]

        if len(candidates) == 1:
            return (candidates[0].x, candidates[0].y)

        # Tie-break by toroidal distance to current position
        w = agent.model.sugar_field.width
        h = agent.model.sugar_field.height
        cx, cy = perception.current_x, perception.current_y

        def toroidal_dist(c) -> float:
            dx = min(abs(c.x - cx), w - abs(c.x - cx))
            dy = min(abs(c.y - cy), h - abs(c.y - cy))
            return math.sqrt(dx * dx + dy * dy)

        min_dist = min(toroidal_dist(c) for c in candidates)
        nearest = [c for c in candidates if abs(toroidal_dist(c) - min_dist) < 1e-9]

        chosen = rng.choice(nearest)
        return (chosen.x, chosen.y)
