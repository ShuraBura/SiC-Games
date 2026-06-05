from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.world import SugarField


def matthew_shares(
    cluster: list["BaseAgent"],
    total: float,
    alpha: float,
    epsilon: float,
) -> list[float]:
    """Compute Matthew-weighted shares of `total` for each agent in `cluster`.

    share_i = total * (C_i + eps)^alpha / sum_j (C_j + eps)^alpha
    """
    weights = [(a.cred + epsilon) ** alpha for a in cluster]
    w_sum = sum(weights)
    return [total * w / w_sum for w in weights]


@dataclass
class JointTaskEvent:
    cell: tuple[int, int]
    cluster: list["BaseAgent"]
    total_sugar: float
    total_cred_bonus: float
    sugar_shares: list[float] = field(default_factory=list)
    cred_shares: list[float] = field(default_factory=list)


class JointTaskManager:
    """Detects joint-task cells and distributes Matthew payoffs.

    Called once per step *before* agent movement.

    Detection: a cell (x,y) with capacity >= capacity_threshold becomes a
    joint-task cell if >= 2 agents are within toroidal distance d of it.

    Payoff:
      - Sugar is distributed immediately to agent wealth (Matthew shares).
      - Cell sugar is zeroed (pre-harvested).
      - Cred delta is stored in agent._pending_cred_delta for the run loop
        to flush after all agents have moved.
    """

    def __init__(
        self,
        distance_d: int,
        capacity_threshold: int,
        matthew_alpha: float,
        epsilon: float,
        cred_bonus_per_participant: float,
    ) -> None:
        self.distance_d = distance_d
        self.capacity_threshold = capacity_threshold
        self.matthew_alpha = matthew_alpha
        self.epsilon = epsilon
        self.cred_bonus_per_participant = cred_bonus_per_participant

    @staticmethod
    def _tor_dist(ax: int, ay: int, bx: int, by: int, w: int, h: int) -> float:
        dx = min(abs(ax - bx), w - abs(ax - bx))
        dy = min(abs(ay - by), h - abs(ay - by))
        return (dx * dx + dy * dy) ** 0.5

    def process_step(
        self,
        sugar_field: "SugarField",
        agents: list["BaseAgent"],
        rng,
    ) -> list[JointTaskEvent]:
        """Identify joint-task cells, distribute payoffs, return event list.

        Complexity: O(N + W×H×k²) where k = 2×distance_d+1 (constant for
        fixed d). Previously O(W×H×N) — spatial hash eliminates the per-cell
        full agent scan.

        Algorithm:
          1. Build pos→agent dict from the agent list — O(N).
          2. For each candidate cell look up only the (2d+1)² neighbouring
             positions (Euclidean distance ≤ distance_d) — O(1) per cell.
        """
        w, h = sugar_field.width, sugar_field.height
        events: list[JointTaskEvent] = []
        processed_cells: set[tuple[int, int]] = set()

        # Step 1: spatial hash — O(N)
        # At most one agent per cell (enforced by SugarWorld.occupied set).
        pos_to_agent: dict[tuple[int, int], "BaseAgent"] = {
            a.pos: a for a in agents
        }

        # Pre-compute integer offsets within Euclidean distance ≤ distance_d.
        # Evaluated once per process_step call; tiny list (5 entries at d=1).
        d = self.distance_d
        d_sq = d * d
        _offsets = [
            (dx, dy)
            for dx in range(-d, d + 1)
            for dy in range(-d, d + 1)
            if dx * dx + dy * dy <= d_sq
        ]

        # Step 2: scan candidate cells — O(W×H × |offsets|)
        candidate_cells = [
            (x, y)
            for x in range(w)
            for y in range(h)
            if (sugar_field.capacity[x, y] >= self.capacity_threshold
                and sugar_field.sugar[x, y] > 0)
        ]

        for cx, cy in candidate_cells:
            if (cx, cy) in processed_cells:
                continue

            # Spatial-hash lookup: only positions within distance d — O(|offsets|)
            cluster = []
            for dx, dy in _offsets:
                a = pos_to_agent.get(((cx + dx) % w, (cy + dy) % h))
                if a is not None:
                    cluster.append(a)

            if len(cluster) < 2:
                continue

            # Joint task fires — identical payoff logic, unchanged.
            processed_cells.add((cx, cy))
            total_sugar = float(sugar_field.sugar[cx, cy])
            total_cred_bonus = self.cred_bonus_per_participant * len(cluster)

            sugar_shares = matthew_shares(
                cluster, total_sugar, self.matthew_alpha, self.epsilon
            )
            cred_shares = matthew_shares(
                cluster, total_cred_bonus, self.matthew_alpha, self.epsilon
            )

            # Distribute sugar wealth immediately
            for agent, share in zip(cluster, sugar_shares):
                agent.wealth += share

            # Queue Cred deltas (flushed by run loop after movement)
            for agent, delta in zip(cluster, cred_shares):
                agent._pending_cred_delta += delta

            # Zero the cell (pre-harvest)
            sugar_field.sugar[cx, cy] = 0.0

            events.append(JointTaskEvent(
                cell=(cx, cy),
                cluster=list(cluster),
                total_sugar=total_sugar,
                total_cred_bonus=total_cred_bonus,
                sugar_shares=sugar_shares,
                cred_shares=cred_shares,
            ))

        return events
