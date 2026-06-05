from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

import numpy as np

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.world import SugarField


@dataclass(frozen=True)
class CellView:
    x: int
    y: int
    sugar: float
    neighbor_count: int = 0  # occupied neighbours within Chebyshev d=1 (Stage 3.3)
    c_proximity: int = 0     # Stage 4.4: C agents within r_pool Chebyshev radius


@dataclass(frozen=True)
class Perception:
    """What an agent knows at a given step."""
    visible_cells: tuple[CellView, ...]
    current_x: int
    current_y: int


class PerceptionBuilder(Protocol):
    def build(self, agent: "BaseAgent", sugar_field: "SugarField", occupied: set[tuple[int, int]]) -> Perception:
        ...


class LocalVisionPerception:
    """Stage 1: agent sees unoccupied cells along cardinal arms up to vision v,
    plus its own current cell. Stage 3.3: also counts occupied neighbours per cell.
    Stage 4.4: also reports c_proximity (C agents within r_pool radius) per cell.
    """

    def __init__(self) -> None:
        # Stage 4.4: precomputed C-proximity grid (W×H int array), set each step by run.py.
        # None → c_proximity=0 for all cells (backward-compatible default).
        self.c_prox_grid: "np.ndarray | None" = None

    def build(
        self,
        agent: "BaseAgent",
        sugar_field: "SugarField",
        occupied: set[tuple[int, int]],
    ) -> Perception:
        x, y = agent.pos
        v = agent.vision
        w, h = sugar_field.width, sugar_field.height
        cells: list[CellView] = []

        cpg = self.c_prox_grid  # local alias for speed

        def _c_prox(nx: int, ny: int) -> int:
            return int(cpg[nx, ny]) if cpg is not None else 0

        # Skip _neighbor_count when c_prox_grid is set: CarbonDecision uses
        # c_proximity (box-filter grid) not neighbor_count, so _neighbor_count
        # is unused for C runs and computing it is pure overhead. [perf-fix]
        _skip_nc = cpg is not None

        cells.append(CellView(x, y, sugar_field.level(x, y),
                               0 if _skip_nc else self._neighbor_count(x, y, occupied, w, h),
                               _c_prox(x, y)))

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for step in range(1, v + 1):
                nx = (x + dx * step) % w
                ny = (y + dy * step) % h
                if (nx, ny) not in occupied or (nx, ny) == (x, y):
                    cells.append(CellView(nx, ny, sugar_field.level(nx, ny),
                                          0 if _skip_nc else self._neighbor_count(nx, ny, occupied, w, h),
                                          _c_prox(nx, ny)))

        return Perception(
            visible_cells=tuple(cells),
            current_x=x,
            current_y=y,
        )

    @staticmethod
    def _neighbor_count(
        nx: int, ny: int,
        occupied: set[tuple[int, int]],
        w: int, h: int,
    ) -> int:
        """Number of occupied cells within Chebyshev distance 1 of (nx, ny)."""
        count = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if ((nx + ddx) % w, (ny + ddy) % h) in occupied:
                    count += 1
        return count
