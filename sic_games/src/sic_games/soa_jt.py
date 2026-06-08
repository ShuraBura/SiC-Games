"""Stage 7.5 Workstream B — vectorised Joint Task manager (GATE B1).

VecJointTaskManager is a drop-in replacement for JointTaskManager.
Same interface: process_step(sugar_field, agents, rng) -> list[JointTaskEvent].

**Why this kills the occupancy cliff:**
The oracle's JointTaskManager scans all W×H candidate cells in a Python loop, then
for each qualifying cell builds the cluster by dictionary lookups over the d-neighbourhood
offsets, then calls matthew_shares() as a Python list comprehension. At high per-cell
occupancy the cluster lists are large, so the total cost per step is
O(W×H × mean_occ × |offsets|) in Python — the cliff.

This implementation replaces:
  - The O(W×H) Python candidate scan  → numpy bincount + roll qualifying mask (O(N) + O(W×H))
  - The per-cell dict cluster build    → pre-built pos_to_slots dict (O(1) per lookup)
  - matthew_shares() list comprehension → numpy array ops on cluster slot vectors

The Python loop now iterates over n_jt_events (qualifying cells that actually fire), not
W×H. The inner arithmetic is vectorised numpy — no Python loops over agent objects.

**Scheme declaration (Tier-3, ARCHITECTURE ss12.1-H, pre-registered 2026-06-06):**
  - Cluster: agents within toroidal Euclidean distance d of qualifying cell (same as oracle)
  - Processing order: qualifying cells in x-major ascending order (same as oracle scan)
  - Agent exclusivity: oracle semantics — `processed_cells` prevents a CELL from firing
    twice; the same AGENT can appear in multiple events if it is within distance d of two
    adjacent qualifying cells. VecJTM matches this: no consumed-agent mask (A-fix 2026-06-08).
  - Defection RNG: keyed_uniform(seed, step, unique_ids, "jt_c2_defect") — D2 counter-based;
    replaces per-agent Python RNG (deliberate Tier-3 change; see ARCHITECTURE ss12.1-H)
  - Matthew arithmetic: identical to oracle (same formula, same epsilon, same alpha)

Nothing here modifies run.py. The oracle stays frozen (D4).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from sic_games.joint_task import JointTaskEvent
from sic_games.soa import keyed_uniform

if TYPE_CHECKING:
    from sic_games.world import SugarField


class VecJointTaskManager:
    """Vectorised JT manager — drop-in for JointTaskManager.

    Complexity: O(N) + O(W×H) + O(n_jt_events × |cluster|_numpy_ops)
    vs oracle:  O(N) + O(W×H × mean_occ × |offsets|) Python-object loops.
    """

    def __init__(
        self,
        distance_d: int,
        capacity_threshold: int,
        matthew_alpha: float,
        epsilon: float,
        cred_bonus_per_participant: float,
        seed: int = 0,
        c2_defection_enabled: bool = False,
    ) -> None:
        self.distance_d = distance_d
        self.capacity_threshold = capacity_threshold
        self.matthew_alpha = matthew_alpha
        self.epsilon = epsilon
        self.cred_bonus_per_participant = cred_bonus_per_participant
        self.c2_defection_enabled = c2_defection_enabled
        self._seed = seed
        self._step: int = 0

        # Pre-compute neighbourhood offsets (constant for fixed d; done once)
        d_sq = distance_d * distance_d
        self._offsets: list[tuple[int, int]] = [
            (dx, dy)
            for dx in range(-distance_d, distance_d + 1)
            for dy in range(-distance_d, distance_d + 1)
            if dx * dx + dy * dy <= d_sq
        ]

    # ── Public interface ──────────────────────────────────────────────────────

    def process_step(
        self,
        sugar_field: "SugarField",
        agents: list,
        rng,
    ) -> list[JointTaskEvent]:
        """Identify joint-task cells, distribute Matthew payoffs, return event list.

        Matches the oracle's JointTaskManager.process_step signature exactly.
        `rng` is accepted but not used (matches oracle's parameter list; the oracle
        also doesn't use it — JT defection draws come from per-agent agent._rng, here
        replaced by keyed_uniform per D2).
        """
        self._step += 1
        w, h = sugar_field.width, sugar_field.height
        n = len(agents)
        if n == 0:
            return []

        # ── 1. Build agent arrays from objects (O(N), one pass) ──────────────
        pos_x = np.empty(n, dtype=np.int64)
        pos_y = np.empty(n, dtype=np.int64)
        cred_arr = np.empty(n, dtype=np.float64)
        c2_arr = np.empty(n, dtype=np.float64)
        is_carbon = np.zeros(n, dtype=bool)
        uid_arr = np.empty(n, dtype=np.int64)

        for i, a in enumerate(agents):
            pos_x[i] = a.pos[0]
            pos_y[i] = a.pos[1]
            cred_arr[i] = a.cred
            c2_arr[i] = a.c2
            is_carbon[i] = (a.strategy == "carbon")
            uid_arr[i] = a.unique_id

        # ── 2. Occupancy grid: occ_grid[y, x] = agent count at cell (x, y) ──
        lin_pos = pos_y * w + pos_x          # y-major linear index
        occ_flat = np.bincount(lin_pos.astype(np.intp), minlength=w * h)
        occ_grid = occ_flat.reshape(h, w)    # shape (H, W)

        # ── 3. Neighbourhood count (vectorised, toroidal) ────────────────────
        neigh_grid = _neighbourhood_sum(occ_grid, self.distance_d, self._offsets)

        # ── 4. Qualifying-cell mask (vectorised) ─────────────────────────────
        # sugar_field arrays are indexed [x, y]; transpose to (H, W) for operations
        cap_grid = sugar_field.capacity.T.astype(np.int64)        # (H, W)
        sug_local = sugar_field.sugar.T.astype(np.float64).copy() # (H, W) local copy

        qual_mask = (
            (cap_grid >= self.capacity_threshold)
            & (sug_local > 0.0)
            & (neigh_grid >= 2)
        )

        ys_q, xs_q = np.where(qual_mask)
        if ys_q.size == 0:
            return []

        # Sort qualifying cells in x-major order (matches oracle's
        # `for x in range(w) for y in range(h)` scan — tie-breaking parity)
        xmaj_keys = xs_q * h + ys_q
        order = np.argsort(xmaj_keys, kind="stable")
        ys_q = ys_q[order]
        xs_q = xs_q[order]

        # ── 5. pos → slot list (O(N), built once; O(1) per lookup) ───────────
        pos_to_slots: dict[tuple[int, int], list[int]] = {}
        for i in range(n):
            key = (int(pos_x[i]), int(pos_y[i]))
            if key not in pos_to_slots:
                pos_to_slots[key] = []
            pos_to_slots[key].append(i)

        # ── 6. Process qualifying cells ───────────────────────────────────────
        # Oracle semantics: processed_cells prevents a CELL from firing twice
        # but does NOT prevent an agent from appearing in multiple adjacent events.
        # No consumed-agent mask here — matches oracle behavior.
        wealth_delta = np.zeros(n, dtype=np.float64)
        cred_delta = np.zeros(n, dtype=np.float64)
        events: list[JointTaskEvent] = []

        for cx, cy in zip(xs_q.tolist(), ys_q.tolist()):
            # Collect ALL agents from neighbourhood (including those in prior events)
            cluster_list: list[int] = []
            for dx, dy in self._offsets:
                nx = (cx + dx) % w
                ny = (cy + dy) % h
                for slot in pos_to_slots.get((nx, ny), []):
                    cluster_list.append(slot)

            if len(cluster_list) < 2:
                continue

            cluster_arr = np.array(cluster_list, dtype=np.int64)
            total_sugar = float(sug_local[cy, cx])
            total_cred_bonus = self.cred_bonus_per_participant * len(cluster_arr)

            defector_slots: list[int] = []
            cooperator_arr = cluster_arr

            if self.c2_defection_enabled:
                # Step 1: tentative Matthew shares for the full cluster
                w_raw = (cred_arr[cluster_arr] + self.epsilon) ** self.matthew_alpha
                w_sum = float(w_raw.sum())
                if w_sum > 0.0:
                    tentative = total_sugar * w_raw / w_sum
                else:
                    tentative = np.full(len(cluster_arr),
                                        total_sugar / len(cluster_arr), dtype=np.float64)

                # Step 2: solo harvest for each agent in cluster
                solo = sug_local[pos_y[cluster_arr], pos_x[cluster_arr]]

                # Step 3: defection check — C agents only; keyed RNG (D2)
                can_def = is_carbon[cluster_arr] & (solo > tentative)
                draws = keyed_uniform(
                    self._seed, self._step,
                    uid_arr[cluster_arr].astype(np.uint64),
                    "jt_c2_defect",
                )
                defects = can_def & (draws < c2_arr[cluster_arr])

                defector_slots = cluster_arr[defects].tolist()
                cooperator_arr = cluster_arr[~defects]

                if len(cooperator_arr) < 2:
                    continue  # no JT event — all fell through to solo

                total_cred_bonus = self.cred_bonus_per_participant * len(cooperator_arr)

            # Matthew shares for cooperators
            w_raw = (cred_arr[cooperator_arr] + self.epsilon) ** self.matthew_alpha
            w_sum = float(w_raw.sum())
            if w_sum > 0.0:
                sugar_shares = total_sugar * w_raw / w_sum
                cred_shares_arr = total_cred_bonus * w_raw / w_sum
            else:
                nc = len(cooperator_arr)
                sugar_shares = np.full(nc, total_sugar / nc, dtype=np.float64)
                cred_shares_arr = np.full(nc, total_cred_bonus / nc, dtype=np.float64)

            # Accumulate deltas (vectorised)
            np.add.at(wealth_delta, cooperator_arr, sugar_shares)
            np.add.at(cred_delta, cooperator_arr, cred_shares_arr)

            # Zero the cell in local copy + field (prevents double-counting the same CELL)
            sugar_field.sugar[cx, cy] = 0.0
            sug_local[cy, cx] = 0.0   # keep local copy in sync for subsequent events

            # Emit event (agent objects for metrics compatibility)
            coop_agents = [agents[s] for s in cooperator_arr.tolist()]
            defect_agents = [agents[s] for s in defector_slots]
            events.append(JointTaskEvent(
                cell=(cx, cy),
                cluster=coop_agents,
                total_sugar=total_sugar,
                total_cred_bonus=total_cred_bonus,
                sugar_shares=sugar_shares.tolist(),
                cred_shares=cred_shares_arr.tolist(),
                n_defectors=len(defector_slots),
                defectors=defect_agents,
            ))

        # ── 7. Apply accumulated deltas to agent objects (O(N)) ───────────────
        nonzero_w = np.flatnonzero(wealth_delta)
        for slot in nonzero_w.tolist():
            agents[slot].wealth += float(wealth_delta[slot])
        nonzero_c = np.flatnonzero(cred_delta)
        for slot in nonzero_c.tolist():
            agents[slot]._pending_cred_delta += float(cred_delta[slot])

        return events


# ── Neighbourhood helpers ─────────────────────────────────────────────────────

def _neighbourhood_sum(
    occ_grid: np.ndarray,
    distance_d: int,
    offsets: list[tuple[int, int]],
) -> np.ndarray:
    """Toroidal neighbourhood sum of occ_grid for each cell.

    Returns array of same shape; entry [y, x] = sum of occ_grid over all cells
    within Euclidean distance d of (x, y), including (x, y) itself.
    d=1 (the default) uses 5 np.roll calls — O(W×H) vectorised.
    """
    if distance_d == 0:
        return occ_grid.copy()
    if distance_d == 1:
        # Fast path: 5-cell cross kernel (center + 4 cardinals)
        return (occ_grid
                + np.roll(occ_grid, 1, axis=0)
                + np.roll(occ_grid, -1, axis=0)
                + np.roll(occ_grid, 1, axis=1)
                + np.roll(occ_grid, -1, axis=1))
    # General d: accumulate each offset via np.roll (O(|offsets|×W×H) vectorised)
    result = np.zeros_like(occ_grid, dtype=np.int64)
    for dx, dy in offsets:
        result = result + np.roll(np.roll(occ_grid, dy, axis=0), dx, axis=1)
    return result
