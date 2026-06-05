from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TraitVector:
    """Cultural/behavioural trait vector H_i = [φ, ψ, c1, c2].

    All dimensions live in [0, 1].

    φ  — status-seeking weight (active Stage 2+)
    ψ  — sociability / proximity preference (active Stage 3.3+)
    c1 — conformism (0) ↔ individualism (1)  [inert until Stage 4+]
    c2 — cooperation (0) ↔ competition (1)   [inert until Stage 4+]
    """

    phi: float
    psi: float
    c1: float
    c2: float
