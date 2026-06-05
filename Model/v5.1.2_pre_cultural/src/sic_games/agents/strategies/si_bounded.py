from __future__ import annotations

import math
from typing import TYPE_CHECKING

from sic_games.agents.strategies.softmax_base import SoftmaxDecision, _normalize

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.agents.perception import CellView


class BoundedRationalSi(SoftmaxDecision):
    """Fixed-temperature softmax over resource utility only.

    sigma is constant (sigma_si), calibrated from Stage 2.2 kappa=2.0 mean_sigma.
    No Cred utility term — Si agents maximise sugar only, with uniform exploration noise.
    Wealth_velocity is tracked in BaseAgent but unused here.

    Stage 5 Task 3: when kappa_si > 0 (Si Cred active), temperature becomes
    agent-specific:
        σ_Si_eff_i(t) = σ_Si + κ_Si × tanh(si_cred_i(t) / C*_Si)
    High-Cred Si agents are more explorative. kappa_si=0.0 (default) recovers
    Stage 4.5 fixed-temperature behaviour exactly.
    """

    def __init__(self, sigma_si: float,
                 kappa_si: float = 0.0,
                 c_star_si: float = 10.0) -> None:
        self.sigma_si = sigma_si
        self.kappa_si = float(kappa_si)
        self.c_star_si = float(c_star_si)

    def temperature(self, agent: "BaseAgent") -> float:
        if self.kappa_si == 0.0:
            return self.sigma_si
        return self.sigma_si + self.kappa_si * math.tanh(agent.si_cred / self.c_star_si)

    def compute_utilities(
        self,
        agent: "BaseAgent",
        cells: tuple["CellView", ...],
    ) -> list[float]:
        return _normalize([c.sugar for c in cells])
