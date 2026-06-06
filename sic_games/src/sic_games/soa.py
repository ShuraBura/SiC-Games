"""Stage 7.5 Workstream A — Structure-of-Arrays (SoA) agent container.

The array reformulation of the agent population: every agent attribute becomes a
parallel numpy column indexed by a stable slot id, replacing per-agent Python
objects. This is the substrate that (a) removes per-agent-object Python loops,
(b) lets `mean_cred` become an O(1) cached column-mean instead of the legacy
O(N²), and (c) makes a Numba/GPU path *structurally* possible later (blueprint
§2, §5 "THE enabling path").

**This module is infrastructure only — it migrates no mechanic.** Per blueprint
§4.1 the SoA container + the parity harness (`parity.py`) stand up FIRST; no
mechanic moves off the object oracle until the harness can diff oracle-vs-array
per column. Nothing here touches the live model (`run.py`) — the object model
stays frozen as the reference oracle until the FINAL gate (decision D4).

Design decisions realised here (blueprint §10):
  * **D2 — counter-based / per-agent-keyed RNG.** `keyed_uniform` derives every
    draw from `(seed, step, agent_id, stream)` via a splitmix64 mix, so a draw's
    value depends only on those keys, never on evaluation order. This is what
    lets non-interacting stochastic mechanics stay reproducible (and Tier-1/2
    identical) under vectorisation, and makes the interacting ones reproducible
    under a *chosen* scheme.
  * **D3 — preallocate-with-capacity + alive mask + compaction.** Births fill
    free slots, deaths flip the mask; the backing arrays are resized only at
    explicit compaction, never per step.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# ── Strategy enum (int column; matches the object model's string `strategy`) ──
STRATEGY_GREEDY = 0
STRATEGY_CARBON = 1
STRATEGY_SI_BOUNDED = 2

STRATEGY_TO_INT = {
    "greedy": STRATEGY_GREEDY,
    "carbon": STRATEGY_CARBON,
    "si_bounded": STRATEGY_SI_BOUNDED,
}
INT_TO_STRATEGY = {v: k for k, v in STRATEGY_TO_INT.items()}

# Float and int column names. Kept explicit (not introspected) so the schema is
# auditable and a missing/extra column is a loud error, not silent drift.
FLOAT_COLUMNS: tuple[str, ...] = (
    "wealth",
    "phi",
    "psi",
    "c1",
    "c2",
    "cred",
    "pending_cred_delta",
    "wealth_velocity",
    "si_cred",
)
INT_COLUMNS: tuple[str, ...] = (
    "pos_x",
    "pos_y",
    "vision",
    "metabolism",
    "max_age",
    "age",
    "strategy",
    "dormant_steps",
    "unique_id",
    "parent_id",      # -1 = founder (no parent); for T-1 lineage analysis later
    "lineage_root",   # the founding ancestor's unique_id; self for founders
)
BOOL_COLUMNS: tuple[str, ...] = (
    "alive",
    "dormant",
)
ALL_COLUMNS: tuple[str, ...] = FLOAT_COLUMNS + INT_COLUMNS + BOOL_COLUMNS

# ── splitmix64 constants (counter-based keyed RNG, D2) ────────────────────────
_MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
_SM_INC = np.uint64(0x9E3779B97F4A7C15)
_SM_M1 = np.uint64(0xBF58476D1CE4E5B9)
_SM_M2 = np.uint64(0x94D049BB133111EB)
_S30 = np.uint64(30)
_S27 = np.uint64(27)
_S31 = np.uint64(31)
_S11 = np.uint64(11)
_INV53 = 1.0 / float(1 << 53)


def _splitmix64(x: np.ndarray) -> np.ndarray:
    """splitmix64 finaliser (vectorised or scalar uint64); wraps mod 2^64 by design.

    Modular wraparound is the intended arithmetic, so numpy's scalar-overflow
    warning is suppressed (array uint64 ops wrap silently; scalar ones warn).
    """
    with np.errstate(over="ignore"):
        z = (x + _SM_INC) & _MASK64
        z = ((z ^ (z >> _S30)) * _SM_M1) & _MASK64
        z = ((z ^ (z >> _S27)) * _SM_M2) & _MASK64
        return z ^ (z >> _S31)


def _stream_key(stream_label: str) -> np.uint64:
    """Stable 64-bit key for a named draw stream (order-independent of process)."""
    h = np.uint64(0xCBF29CE484222325)  # FNV-1a 64-bit offset basis
    prime = np.uint64(0x100000001B3)
    with np.errstate(over="ignore"):
        for ch in stream_label.encode("utf-8"):
            h = ((h ^ np.uint64(ch)) * prime) & _MASK64
    return h


def keyed_uniform(
    seed: int,
    step: int,
    agent_ids: np.ndarray,
    stream_label: str,
) -> np.ndarray:
    """Counter-based per-agent-keyed uniform draws in [0, 1) (decision D2).

    The value for each agent depends ONLY on (seed, step, agent_id, stream_label)
    — never on position in the array or evaluation order. Two array models that
    process the same agents in any order get identical draws; this is the
    property that keeps the non-interacting stochastic mechanics reproducible
    under vectorisation, and lets interacting mechanics commit to a *declared*
    pairing scheme rather than inheriting the loop's accidental order.

    Returns a float64 array the same shape as `agent_ids`.
    """
    ids = np.asarray(agent_ids, dtype=np.uint64)
    with np.errstate(over="ignore"):
        key = _splitmix64(np.uint64(seed) ^ ((np.uint64(step) * _SM_INC) & _MASK64))
        key = _splitmix64(key ^ _stream_key(stream_label))
        bits = _splitmix64(key ^ ids)
    # top 53 bits → double in [0, 1), the standard construction
    return (bits >> _S11).astype(np.float64) * _INV53


@dataclass
class AgentArray:
    """Structure-of-Arrays population container with capacity + alive mask (D3).

    Slots `[0, n_slots)` are in use as agent records; `capacity >= n_slots` is the
    allocated backing size. `alive` distinguishes living agents from dead-but-not-
    yet-compacted slots. `live_indices()` is the canonical way to iterate agents.

    Columns are plain numpy arrays of length `capacity`; see ALL_COLUMNS. Position
    is stored as integer (pos_x, pos_y); `pos_linear(width)` gives the `y*W+x`
    cell index the blueprint's cell-bucket primitive (§2) operates on.
    """

    capacity: int
    n_slots: int
    width: int
    height: int
    columns: dict[str, np.ndarray] = field(default_factory=dict)

    # ── construction ─────────────────────────────────────────────────────────
    @classmethod
    def empty(cls, capacity: int, width: int, height: int) -> "AgentArray":
        cols: dict[str, np.ndarray] = {}
        for name in FLOAT_COLUMNS:
            cols[name] = np.zeros(capacity, dtype=np.float64)
        for name in INT_COLUMNS:
            cols[name] = np.zeros(capacity, dtype=np.int64)
        for name in BOOL_COLUMNS:
            cols[name] = np.zeros(capacity, dtype=bool)
        return cls(capacity=capacity, n_slots=0, width=width, height=height, columns=cols)

    @classmethod
    def from_oracle(cls, model, capacity: int | None = None) -> "AgentArray":
        """Snapshot the frozen object model into a fresh SoA (the oracle bridge).

        Captures the *living* agents in the model's current AgentSet order. This is
        the harness's entry point: a snapshot taken here can be diffed column-by-
        column against the same model after a step, or used to seed a vectorised
        mechanic for a per-mechanic parity test (blueprint §3, §7).

        `capacity` defaults to a `n_carry`-style headroom (10×, min +64) so births
        have free slots without an immediate resize (D3). Pass an explicit value
        for tight tests.
        """
        agents = list(model.agents)
        n = len(agents)
        if capacity is None:
            capacity = max(n * 10, n + 64, 64)
        wc = model.cfg.world
        width, height = wc.grid_size
        arr = cls.empty(capacity, width, height)
        c = arr.columns
        for i, a in enumerate(agents):
            c["wealth"][i] = float(a.wealth)
            c["phi"][i] = float(a.phi)
            c["psi"][i] = float(a.psi)
            c["c1"][i] = float(a.c1)
            c["c2"][i] = float(a.c2)
            c["cred"][i] = float(a.cred)
            c["pending_cred_delta"][i] = float(a._pending_cred_delta)
            c["wealth_velocity"][i] = float(a.wealth_velocity)
            c["si_cred"][i] = float(a.si_cred)
            c["pos_x"][i] = int(a.pos[0])
            c["pos_y"][i] = int(a.pos[1])
            c["vision"][i] = int(a.vision)
            c["metabolism"][i] = int(a.metabolism)
            c["max_age"][i] = int(a.max_age)
            c["age"][i] = int(a.age)
            c["strategy"][i] = STRATEGY_TO_INT[a.strategy]
            c["dormant_steps"][i] = int(a.dormant_steps)
            c["unique_id"][i] = int(a.unique_id)
            c["parent_id"][i] = -1
            c["lineage_root"][i] = int(a.unique_id)
            c["alive"][i] = bool(a.alive)
            c["dormant"][i] = bool(a.dormant)
        arr.n_slots = n
        return arr

    # ── views & accessors ────────────────────────────────────────────────────
    def __getattr__(self, name: str) -> np.ndarray:
        # Convenience: arr.wealth -> the full-capacity column. (dataclass fields
        # resolve normally; this only fires for unknown attributes = column names.)
        cols = self.__dict__.get("columns")
        if cols is not None and name in cols:
            return cols[name]
        raise AttributeError(name)

    def live_indices(self) -> np.ndarray:
        """Slot indices of living agents (the canonical iteration order)."""
        return np.flatnonzero(self.columns["alive"][: self.n_slots])

    @property
    def n_live(self) -> int:
        return int(self.columns["alive"][: self.n_slots].sum())

    def pos_linear(self) -> np.ndarray:
        """Linear cell index y*W + x for every slot in [0, n_slots)."""
        c = self.columns
        return (c["pos_y"][: self.n_slots] * self.width + c["pos_x"][: self.n_slots]).astype(np.int64)

    # ── cell-bucket primitive (blueprint §2) ─────────────────────────────────
    def bucket_by_cell(self, live_only: bool = True) -> "CellBuckets":
        """Group agent slots by their cell (the single shared spatial primitive).

        Sorts the (selected) slot indices by linear cell id so that agents sharing
        a cell are contiguous. Serves harvest-split, the JT contest, local density,
        and ψ-proximity (build once, reuse everywhere — §2/§5). Returns a
        `CellBuckets` with the sorted order, the per-occupant cell ids, and the
        unique cells with their segment offsets.
        """
        if live_only:
            idx = self.live_indices()
        else:
            idx = np.arange(self.n_slots, dtype=np.int64)
        lin_all = self.pos_linear()
        lin = lin_all[idx]
        order = np.argsort(lin, kind="stable")
        sorted_idx = idx[order]
        sorted_cells = lin[order]
        unique_cells, starts, counts = _segment_offsets(sorted_cells)
        return CellBuckets(
            sorted_idx=sorted_idx,
            sorted_cells=sorted_cells,
            unique_cells=unique_cells,
            seg_starts=starts,
            seg_counts=counts,
            width=self.width,
        )

    # ── births / deaths (D3: mask + capacity + compaction) ───────────────────
    def kill(self, slots: np.ndarray) -> None:
        """Flip the alive mask off for the given slots (no array resize)."""
        self.columns["alive"][slots] = False

    def alloc(self, n: int) -> np.ndarray:
        """Reserve `n` fresh slots for births, growing capacity if needed (D3).

        Returns the new slot indices. Newly grown tail is zero-initialised; callers
        must populate the standard columns (and set alive=True) for the returned
        slots. Compaction (reclaiming dead slots) is a separate, explicit pass.
        """
        end = self.n_slots + n
        if end > self.capacity:
            new_cap = max(end, self.capacity * 2)
            for name, arr in self.columns.items():
                grown = np.zeros(new_cap, dtype=arr.dtype)
                grown[: self.capacity] = arr
                self.columns[name] = grown
            self.capacity = new_cap
        new_slots = np.arange(self.n_slots, end, dtype=np.int64)
        self.n_slots = end
        return new_slots

    def compact(self) -> None:
        """Reclaim dead slots: pack living agents to the front, shrink n_slots."""
        live = self.live_indices()
        n = live.size
        for name, arr in self.columns.items():
            arr[:n] = arr[live]
            arr[n:] = 0
        self.columns["alive"][:n] = True
        self.n_slots = n


@dataclass
class CellBuckets:
    """Output of `AgentArray.bucket_by_cell` — the shared cell-grouping primitive.

    `sorted_idx[seg_starts[k] : seg_starts[k]+seg_counts[k]]` are the agent slots
    occupying `unique_cells[k]`. Segment-sum / segment-max reductions (harvest
    split, Matthew denominator) run directly off this with np.add.at / bincount.
    """

    sorted_idx: np.ndarray
    sorted_cells: np.ndarray
    unique_cells: np.ndarray
    seg_starts: np.ndarray
    seg_counts: np.ndarray
    width: int

    def occupancy(self) -> np.ndarray:
        """Per-unique-cell occupant counts (aligned with `unique_cells`)."""
        return self.seg_counts

    def cell_xy(self) -> tuple[np.ndarray, np.ndarray]:
        """(x, y) of each unique cell from its linear id."""
        return self.unique_cells % self.width, self.unique_cells // self.width


def _segment_offsets(sorted_cells: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Given cell ids sorted ascending, return (unique_cells, starts, counts)."""
    if sorted_cells.size == 0:
        z = np.empty(0, dtype=np.int64)
        return z, z, z
    unique_cells, starts, counts = np.unique(sorted_cells, return_index=True, return_counts=True)
    return unique_cells.astype(np.int64), starts.astype(np.int64), counts.astype(np.int64)
