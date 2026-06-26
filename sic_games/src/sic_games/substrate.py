"""Stage 6.0a: multi-occupancy substrate helpers.

The harvest split (§3): a cell's available sugar S is divided among its occupants.
- Even split (κ=0 or single occupant): scramble competition, share = S/|O|.
- Cred-weighted contest (κ>0, C only): share_i = S · (φ_i+ε)^κ / Σ_j (φ_j+ε)^κ.
  κ=0 recovers the even split exactly. Si/other occupants get uniform weight
  (Si has no Cred/φ-contest — it never enters the κ>0 branch in practice).

Shares are pre-efficiency (Σ share_i == S exactly); the caller applies η when
banking to wealth, mirroring the legacy `harvested = raw * eta` convention.
The split is order-independent within a cell (a determinism property, §3.4).
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent


def status_of(agent: "BaseAgent") -> float:
    """Contest/share weight basis (LINEAGE facet). Carbon-on-substrate: accumulated `cred` (status) when the
    agent opts in (`use_cred_status`), else the `φ` trait. Defaulting to φ preserves the Sugarscape contest
    tests and any non-demographic carbon path; only the seeded/heritable Carbon-substrate run reads cred."""
    if getattr(agent, "use_cred_status", False):
        return agent.cred
    return agent.phi


def base_status(agent: "BaseAgent", eps: float) -> float:
    """Multiplicative contest-weight base over ACTIVE status facets (Cobb–Douglas, equal within-domain
    exponents → the caller applies the exponent κ). Lineage (`status_of`) is always present; the achieved
    PROWESS facet joins when `_use_prowess` (B+). Collapses to the scalar `(cred+ε)` / `(φ+ε)` (R-18) when
    prowess is off — exact back-compat."""
    b = status_of(agent) + eps
    if getattr(agent, "_use_prowess", False):
        b *= (getattr(agent, "prowess", 0.0) + eps)
    return b


def compute_harvest_shares(
    occupants: list["BaseAgent"],
    S: float,
    kappa: float,
    phi_epsilon: float,
) -> list[float]:
    """Return per-occupant shares of S (Σ shares == S). See module docstring."""
    n = len(occupants)
    if n == 0:
        return []
    if kappa == 0.0 or n == 1:
        base = S / n
        return [base] * n
    weights = [
        base_status(a, phi_epsilon) ** kappa if a.strategy == "carbon" else 1.0
        for a in occupants
    ]
    wsum = sum(weights)
    return [S * w / wsum for w in weights]


def diffusion_select_target(
    agent: "BaseAgent",
    sugar_field,
    occ_count: dict,
    occ_wsum: dict | None,
    sc,
    rng,
    temperature: float | None,
) -> tuple[int, int]:
    """Stage 6.0a §4.1/4.2 diffusion movement: local-gradient step over the von-Neumann
    r=1 neighbourhood (4 cardinal + current), NO unoccupied filter.

    Full-form utility with trait hooks at neutral values (6.0a):
        U = expected_per_capita_yield × affinity(=1) × crowd_response(=1) − move_cost
    expected_per_capita_yield is the agent's ANTICIPATED share if it occupied the cell:
      - even (κ=0):  S/(n+1) for a neighbour (one more occupant), S/n for the current cell;
      - contest (κ>0): S·w_self/(Wsum+w_self) neighbour, S·w_self/Wsum current,
        where Wsum is the per-cell sum of occupant weights (φ+ε)^κ (O(1) via occ_wsum).
    Self-limiting: a mobbed rich cell offers a small per-capita share, so it stops attracting.
    Selection: softmax with the agent's decision temperature (one rng draw), else argmax.
    K_cell ceiling: a full neighbour (count ≥ k_cell, k_cell>0) is not a candidate.
    """
    x, y = agent.pos
    w, h = sugar_field.width, sugar_field.height
    kappa = sc.contest_exponent
    eps = sc.phi_epsilon
    kc = sc.k_cell
    s_max = getattr(sc, "group_safety_max", 0.0)        # E.1 emergent-bands safety drive (0 = off → bit-exact IFD)
    g_s = getattr(sc, "group_safety_scale", 8.0)
    g_mate = getattr(sc, "group_mate_min", 0.0)         # E.2 mating-access drive (0 = off)
    m_floor = getattr(sc, "group_mate_floor", 0.3)
    cands = [(x, y), ((x + 1) % w, y), ((x - 1) % w, y), (x, (y + 1) % h), (x, (y - 1) % h)]
    w_self = base_status(agent, eps) ** kappa if (kappa > 0.0 and agent.strategy == "carbon") else 1.0

    cells: list[tuple[int, int]] = []
    utils: list[float] = []
    for (cx, cy) in cands:
        is_cur = (cx == x and cy == y)
        if not is_cur and kc > 0 and occ_count.get((cx, cy), 0) >= kc:
            continue  # full cell, blocked by K_cell ceiling
        S = sugar_field.level(cx, cy)
        n_cell = occ_count.get((cx, cy), 0)
        if kappa == 0.0:
            n_after = n_cell if is_cur else n_cell + 1
            ypc = S / n_after if n_after > 0 else S
        else:
            Wsum = occ_wsum.get((cx, cy), 0.0) if occ_wsum is not None else 0.0
            denom = Wsum if is_cur else Wsum + w_self
            ypc = (S * w_self / denom) if denom > 0 else S
        move_cost = 0.0 if is_cur else sc.move_cost_flat
        # Emergent-bands grouping multipliers on the cell value (the crowd_response hook), traded against the
        # falling per-capita yield ⇒ an optimal band size emerges. E.1 safety (risk dilution, saturating) +
        # E.2 mating access (a penalty below the minimum viable band ⇒ being alone is actively bad).
        if s_max > 0.0 or g_mate > 0.0:
            g = n_cell if is_cur else n_cell + 1                 # post-move group size
            if s_max > 0.0:
                ypc *= 1.0 + s_max * (1.0 - math.exp(-g / g_s))
            if g_mate > 0.0:
                ypc *= m_floor + (1.0 - m_floor) * min(1.0, g / g_mate)
        cells.append((cx, cy))
        utils.append(ypc - move_cost)

    if not cells:
        return (x, y)

    if temperature is None or temperature <= 0.0:
        # argmax (greedy); deterministic tie-break by first occurrence
        best = max(range(len(cells)), key=lambda i: utils[i])
        return cells[best]

    # softmax (normalise to [0,1] like softmax_base), one rng draw — preserves draw order
    vmax = max(utils) if any(u > 0 for u in utils) else 1.0
    scaled = [(u / vmax) / temperature for u in utils]
    m = max(scaled)
    ex = [math.exp(s - m) for s in scaled]
    tot = sum(ex)
    probs = [e / tot for e in ex]
    roll = rng.random()
    cum = 0.0
    for c, p in zip(cells, probs):
        cum += p
        if roll <= cum:
            return c
    return cells[-1]
