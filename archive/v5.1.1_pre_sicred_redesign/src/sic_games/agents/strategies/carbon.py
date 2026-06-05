from __future__ import annotations

import math
from typing import TYPE_CHECKING

from sic_games.agents.strategies.softmax_base import SoftmaxDecision, _normalize

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.agents.perception import CellView, Perception


class CarbonDecision(SoftmaxDecision):
    """Status-coupled softmax decision logic.

    sigma_i = sigma_base + kappa * tanh(C_i / cred_scale)
    U_ij    = w_R * R_hat_ij + w_C * C_hat_ij
    P(j)    = softmax(U / sigma_i)

    joint_task_cells is injected each step by the run loop so the utility
    function can estimate Cred gain for joint-task candidates.
    """

    def __init__(
        self,
        sigma_base: float,
        kappa: float,
        cred_scale: float,
        matthew_alpha: float,
        epsilon: float,
        cred_bonus_per_participant: float,
        velocity_scale: float = 1.0,
        beta: float = 0.0,
        joint_task_cells: set[tuple[int, int]] | None = None,
    ) -> None:
        self.sigma_base = sigma_base
        self.kappa = kappa
        self.cred_scale = cred_scale
        self.matthew_alpha = matthew_alpha
        self.epsilon = epsilon
        self.cred_bonus_per_participant = cred_bonus_per_participant
        self.velocity_scale = velocity_scale
        self.beta = beta
        self.joint_task_cells: set[tuple[int, int]] = joint_task_cells or set()

    def temperature(self, agent: "BaseAgent") -> float:
        return self.sigma_base + self.kappa * math.tanh(agent.cred / self.cred_scale)

    # Public aliases used by metrics.py
    def sigma(self, agent: "BaseAgent") -> float:
        return self.temperature(agent)

    def amplification(self, agent: "BaseAgent") -> float:
        """Status amplification term: 1 + β·tanh(C_i / C**)."""
        return 1.0 + self.beta * math.tanh(agent.cred / self.cred_scale)

    def w_C_eff(self, agent: "BaseAgent") -> float:
        """Effective Cred-seeking weight: φ·amplification·sigmoid(v/v₀)."""
        amp = self.amplification(agent)
        stress = 1.0 / (1.0 + math.exp(-agent.wealth_velocity / self.velocity_scale))
        return agent.phi * amp * stress

    def compute_utilities(
        self,
        agent: "BaseAgent",
        cells: tuple["CellView", ...],
    ) -> list[float]:
        r_raw = [c.sugar for c in cells]

        c_raw = []
        for c in cells:
            if (c.x, c.y) in self.joint_task_cells:
                bonus = self.cred_bonus_per_participant * 2
                own_w = (agent.cred + self.epsilon) ** self.matthew_alpha
                other_w = (agent.cred + self.epsilon) ** self.matthew_alpha
                share = bonus * own_w / (own_w + other_w)
                c_raw.append(share)
            else:
                c_raw.append(0.0)

        r_hat = _normalize(r_raw)
        c_hat = _normalize(c_raw)

        # Proximity term ψ_i · P̂_ij (Stage 4.4: C-agent proximity at r_pool radius).
        # Uses c_proximity (C agents within r_pool, precomputed) when available;
        # falls back to neighbor_count (Chebyshev d=1, all agents) for backward compat.
        if hasattr(cells[0], "c_proximity"):
            n_raw = [float(c.c_proximity) for c in cells]
        else:
            n_raw = [float(getattr(c, "neighbor_count", 0)) for c in cells]
        n_max = max(n_raw) if any(v > 0 for v in n_raw) else 1.0
        n_hat = [v / n_max for v in n_raw]

        w_c = self.w_C_eff(agent)
        w_r = 1.0 - w_c
        psi = getattr(agent, "psi", 0.0)

        return [w_r * r + w_c * c + psi * n for r, c, n in zip(r_hat, c_hat, n_hat)]
