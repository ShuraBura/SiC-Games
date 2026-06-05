from __future__ import annotations

import numpy as np
from numpy.random import Generator


def _toroidal_dist(ax: int, ay: int, bx: int, by: int, width: int, height: int) -> float:
    """Euclidean toroidal distance between two grid cells."""
    dx = min(abs(ax - bx), width - abs(ax - bx))
    dy = min(abs(ay - by), height - abs(ay - by))
    return (dx * dx + dy * dy) ** 0.5


def build_capacity_field(
    width: int,
    height: int,
    peaks: list[tuple[int, int]],
    max_capacity: int,
    band_width_k: int,
) -> np.ndarray:
    """Compute the sugar capacity field.

    c(i,j) = max(0, max_capacity - floor(min_dist_to_nearest_peak / band_width_k))
    where min_dist is Euclidean toroidal distance.
    """
    capacity = np.zeros((width, height), dtype=np.int32)
    for i in range(width):
        for j in range(height):
            min_dist = min(
                _toroidal_dist(i, j, px, py, width, height) for px, py in peaks
            )
            capacity[i, j] = max(0, max_capacity - int(min_dist // band_width_k))
    return capacity


class SugarField:
    """Manages the sugar environment: capacity field, current levels, and growback."""

    def __init__(
        self,
        width: int,
        height: int,
        peaks: list[tuple[int, int]],
        max_capacity: int,
        band_width_k: int,
        alpha: int,
    ) -> None:
        self.width = width
        self.height = height
        self.alpha = alpha
        self.capacity = build_capacity_field(width, height, peaks, max_capacity, band_width_k)
        # Stage 4: effective_capacity is the seasonal ceiling, modified each step by
        # WorldPerturbation.apply(). max_capacity (self.capacity) is never modified.
        self.effective_capacity: np.ndarray = self.capacity.astype(np.float32)
        self.sugar = self.capacity.copy().astype(np.float32)

    def growback(self) -> None:
        """Apply G_alpha: every cell gains alpha sugar, capped at effective_capacity."""
        np.minimum(self.sugar + self.alpha, self.effective_capacity, out=self.sugar)

    def shed_excess_sugar(self) -> None:
        """Clip current sugar to effective_capacity (called after perturbation update)."""
        np.minimum(self.sugar, self.effective_capacity, out=self.sugar)

    def harvest(self, x: int, y: int) -> float:
        """Remove and return all sugar at cell (x, y)."""
        amount = float(self.sugar[x, y])
        self.sugar[x, y] = 0.0
        return amount

    def level(self, x: int, y: int) -> float:
        return float(self.sugar[x, y])

    def total_sugar(self) -> float:
        return float(self.sugar.sum())
