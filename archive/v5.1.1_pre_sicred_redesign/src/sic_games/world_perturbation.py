"""WorldPerturbation protocol — Stage 4.

Called once per step, after growback scheduling slot 1:
  apply(world, t, rng) -> None

Two implementations:
  NullPerturbation    — no-op; recovers Stage 3 behavior exactly.
  SeasonalOscillation — sinusoidal effective_capacity modulation.

Duck-typing is sufficient; no shared base class required.
The run loop calls .apply(world, t, rng) and that is the full interface.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sic_games.world import SugarField


class NullPerturbation:
    """No-op perturbation. effective_capacity stays equal to max_capacity."""

    def apply(self, sugar_field: "SugarField", t: int, rng) -> None:
        pass


class SeasonalOscillation:
    """Sinusoidal oscillation of sugar capacity.

    Symmetric (trough_fraction=0.5, default):
        c_eff(i,j,t) = c_max(i,j) * (1 - A * sin²(π * t / T))
        At t=0:   factor=1.0 (peak)
        At t=T/2: factor=1-A (minimum)
        At t=T:   factor=1.0 (peak again)

    Asymmetric (trough_fraction=tf, Stage 4.5 Task 4 Q17):
        Piecewise: descent phase over tf*T steps, recovery phase over (1-tf)*T steps.
        Minimum still 1-A; recovery is faster (shorter) when tf>0.5.
        factor(phase) = 1 - A * sin²(phase/2), where phase ∈ [0, 2π] mapped from t.
        Phase increases at rate π/(tf*T) for t < tf*T, then π/((1-tf)*T) for t ≥ tf*T.

    Modifies sugar_field.effective_capacity in-place.
    Never modifies sugar_field.capacity (the static ceiling).
    """

    def __init__(self, amplitude: float, period: int,
                 trough_fraction: float = 0.5) -> None:
        self.A = amplitude
        self.T = period
        self.tf = float(trough_fraction)

    def apply(self, sugar_field: "SugarField", t: int, rng) -> None:
        import numpy as np
        tf = self.tf
        t_in = t % self.T
        if tf == 0.5:
            # Symmetric fast path (original formula)
            factor = 1.0 - self.A * math.sin(math.pi * t_in / self.T) ** 2
        else:
            # Asymmetric: piecewise phase mapping
            trough_end = tf * self.T
            if t_in < trough_end:
                phase = math.pi * t_in / trough_end          # [0, π]
            else:
                phase = math.pi + math.pi * (t_in - trough_end) / (self.T - trough_end)  # [π, 2π]
            factor = 1.0 - self.A * math.sin(phase / 2.0) ** 2
        np.multiply(sugar_field.capacity, factor, out=sugar_field.effective_capacity)
