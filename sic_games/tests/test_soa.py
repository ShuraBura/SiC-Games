"""Stage 7.5 Workstream A — SoA container + keyed-RNG tests.

Infrastructure only (blueprint §4.1): proves the Structure-of-Arrays container,
the counter-based keyed RNG (decision D2), the cell-bucket primitive (§2), and the
capacity/alive-mask birth-death machinery (decision D3) before any mechanic
migrates off the object oracle.
"""
from __future__ import annotations

import numpy as np

from sic_games.config import Config
from sic_games.run import SugarWorld
from sic_games.soa import (
    ALL_COLUMNS,
    STRATEGY_GREEDY,
    AgentArray,
    keyed_uniform,
)


def _small_model(n=30, steps=0):
    cfg = Config(
        agents={"initial_population": n},
        world={"grid_size": (12, 12), "sugar_peaks": [(2, 2), (9, 9)]},
        run={"n_steps": max(steps, 1)},
    )
    m = SugarWorld(cfg)
    for _ in range(steps):
        m.step()
    return m


# ── keyed RNG (D2) ────────────────────────────────────────────────────────────

def test_keyed_uniform_deterministic():
    ids = np.array([0, 1, 2, 7, 99], dtype=np.int64)
    a = keyed_uniform(42, 3, ids, "move")
    b = keyed_uniform(42, 3, ids, "move")
    assert np.array_equal(a, b)


def test_keyed_uniform_order_independent():
    ids = np.array([5, 1, 9, 3, 0], dtype=np.int64)
    perm = np.array([3, 0, 4, 2, 1])
    base = keyed_uniform(7, 11, ids, "defect")
    permd = keyed_uniform(7, 11, ids[perm], "defect")
    # the draw for a given agent id is identical regardless of array position
    assert np.allclose(base[perm], permd)


def test_keyed_uniform_in_unit_interval():
    ids = np.arange(10_000, dtype=np.int64)
    u = keyed_uniform(123, 0, ids, "x")
    assert u.min() >= 0.0 and u.max() < 1.0
    # crude uniformity sanity: mean near 0.5
    assert abs(u.mean() - 0.5) < 0.02


def test_keyed_uniform_streams_differ():
    ids = np.arange(1000, dtype=np.int64)
    a = keyed_uniform(1, 1, ids, "stream_a")
    b = keyed_uniform(1, 1, ids, "stream_b")
    assert not np.allclose(a, b)


def test_keyed_uniform_steps_differ():
    ids = np.arange(1000, dtype=np.int64)
    assert not np.allclose(keyed_uniform(1, 1, ids, "s"), keyed_uniform(1, 2, ids, "s"))


# ── container schema + snapshot ───────────────────────────────────────────────

def test_empty_schema():
    arr = AgentArray.empty(16, 12, 12)
    assert arr.capacity == 16 and arr.n_slots == 0
    for name in ALL_COLUMNS:
        assert name in arr.columns
        assert arr.columns[name].shape == (16,)


def test_from_oracle_matches_agents():
    m = _small_model(n=25)
    arr = AgentArray.from_oracle(m)
    agents = list(m.agents)
    assert arr.n_slots == len(agents)
    assert arr.n_live == len(agents)
    # spot-check a few columns against the object agents (aligned by unique_id)
    by_id = {a.unique_id: a for a in agents}
    for i in range(arr.n_slots):
        a = by_id[int(arr.columns["unique_id"][i])]
        assert arr.columns["wealth"][i] == float(a.wealth)
        assert arr.columns["metabolism"][i] == int(a.metabolism)
        assert arr.columns["pos_x"][i] == a.pos[0]
        assert arr.columns["pos_y"][i] == a.pos[1]
        assert arr.columns["strategy"][i] == STRATEGY_GREEDY  # default config


def test_from_oracle_capacity_headroom():
    m = _small_model(n=20)
    arr = AgentArray.from_oracle(m)
    assert arr.capacity >= arr.n_slots + 64  # births have room (D3)


# ── cell-bucket primitive (§2) ────────────────────────────────────────────────

def test_bucket_by_cell_segments():
    arr = AgentArray.empty(8, 5, 5)
    arr.n_slots = 6
    # place agents: 3 in cell (1,1), 2 in (4,0), 1 in (0,3)
    xs = [1, 1, 1, 4, 4, 0]
    ys = [1, 1, 1, 0, 0, 3]
    arr.columns["pos_x"][:6] = xs
    arr.columns["pos_y"][:6] = ys
    arr.columns["alive"][:6] = True
    b = arr.bucket_by_cell()
    # 3 unique cells with occupancies summing to 6
    assert b.unique_cells.size == 3
    assert int(b.occupancy().sum()) == 6
    assert sorted(b.occupancy().tolist()) == [1, 2, 3]
    # every segment's slots actually share the segment's cell
    for k in range(b.unique_cells.size):
        s, c = int(b.seg_starts[k]), int(b.seg_counts[k])
        slots = b.sorted_idx[s:s + c]
        cells = arr.pos_linear()[slots]
        assert np.all(cells == b.unique_cells[k])


def test_bucket_excludes_dead():
    arr = AgentArray.empty(8, 5, 5)
    arr.n_slots = 4
    arr.columns["pos_x"][:4] = [1, 1, 2, 2]
    arr.columns["pos_y"][:4] = [1, 1, 2, 2]
    arr.columns["alive"][:4] = [True, False, True, True]
    b = arr.bucket_by_cell(live_only=True)
    assert int(b.occupancy().sum()) == 3  # the dead one is excluded


# ── births / deaths (D3) ──────────────────────────────────────────────────────

def test_alloc_and_kill():
    arr = AgentArray.empty(4, 5, 5)
    s0 = arr.alloc(3)
    assert list(s0) == [0, 1, 2] and arr.n_slots == 3
    arr.columns["alive"][s0] = True
    arr.kill(np.array([1]))
    assert arr.n_live == 2
    # alloc beyond capacity grows the backing arrays
    s1 = arr.alloc(5)
    assert arr.capacity >= 8 and arr.n_slots == 8
    assert list(s1) == [3, 4, 5, 6, 7]


def test_compact_packs_living():
    arr = AgentArray.empty(8, 5, 5)
    s = arr.alloc(5)
    arr.columns["alive"][s] = True
    arr.columns["unique_id"][s] = [10, 11, 12, 13, 14]
    arr.kill(np.array([1, 3]))  # remove ids 11, 13
    arr.compact()
    assert arr.n_slots == 3 and arr.n_live == 3
    assert sorted(arr.columns["unique_id"][:3].tolist()) == [10, 12, 14]
    assert np.all(arr.columns["alive"][:3])
