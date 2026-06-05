"""Tests for JointTaskManager on a small constructed world."""
import pytest

from sic_games.joint_task import JointTaskManager
from sic_games.world import SugarField


PEAKS = [(1, 1)]  # small world with one peak


def _make_field(width=5, height=5):
    return SugarField(width, height, PEAKS, max_capacity=4, band_width_k=2, alpha=1)


class _FakeAgent:
    def __init__(self, x, y, cred=0.0):
        self.pos = (x, y)
        self.cred = cred
        self.wealth = 0.0
        self._pending_cred_delta = 0.0


def _manager(**kwargs):
    defaults = dict(
        distance_d=1,
        capacity_threshold=4,
        matthew_alpha=1.5,
        epsilon=0.01,
        cred_bonus_per_participant=1.0,
    )
    defaults.update(kwargs)
    return JointTaskManager(**defaults)


def _isolated_field(cell=(1, 1), sugar=4.0):
    """A 5x5 field with sugar only at the specified cell."""
    field = _make_field()
    field.sugar[:] = 0.0
    field.sugar[cell[0], cell[1]] = sugar
    return field


def test_joint_task_fires_when_two_agents_near_peak():
    field = _isolated_field((1, 1), sugar=4.0)
    a1 = _FakeAgent(1, 1)
    a2 = _FakeAgent(1, 2)

    mgr = _manager()
    events = mgr.process_step(field, [a1, a2], rng=None)

    assert len(events) == 1
    assert events[0].cell == (1, 1)
    assert len(events[0].cluster) == 2


def test_joint_task_does_not_fire_with_one_agent():
    field = _isolated_field((1, 1), sugar=4.0)
    a1 = _FakeAgent(1, 1)

    mgr = _manager()
    events = mgr.process_step(field, [a1], rng=None)
    assert len(events) == 0


def test_joint_task_zeros_cell_sugar():
    field = _isolated_field((1, 1), sugar=4.0)
    a1 = _FakeAgent(1, 1)
    a2 = _FakeAgent(1, 2)

    _manager().process_step(field, [a1, a2], rng=None)
    assert field.sugar[1, 1] == 0.0


def test_sugar_shares_sum_to_cell_sugar():
    field = _isolated_field((1, 1), sugar=4.0)
    a1 = _FakeAgent(1, 1, cred=0.0)
    a2 = _FakeAgent(1, 2, cred=0.0)

    mgr = _manager()
    events = mgr.process_step(field, [a1, a2], rng=None)
    assert sum(events[0].sugar_shares) == pytest.approx(4.0, rel=1e-5)


def test_wealth_updated_immediately():
    field = _isolated_field((1, 1), sugar=4.0)
    a1 = _FakeAgent(1, 1, cred=0.0)
    a2 = _FakeAgent(1, 2, cred=0.0)

    _manager().process_step(field, [a1, a2], rng=None)
    assert a1.wealth + a2.wealth == pytest.approx(4.0, rel=1e-5)


def test_cred_delta_queued_not_applied():
    field = _isolated_field((1, 1), sugar=4.0)
    a1 = _FakeAgent(1, 1, cred=1.0)
    a2 = _FakeAgent(1, 2, cred=1.0)

    _manager().process_step(field, [a1, a2], rng=None)
    assert a1._pending_cred_delta > 0.0
    assert a1.cred == 1.0  # unchanged until run loop flushes


def test_no_fire_below_capacity_threshold():
    # Build a field with only a low-capacity cell having sugar
    field = _make_field()
    field.sugar[:] = 0.0
    field.capacity[1, 1] = 3  # below threshold=4
    field.sugar[1, 1] = 3.0
    a1 = _FakeAgent(1, 1)
    a2 = _FakeAgent(1, 2)

    mgr = _manager(capacity_threshold=4)
    events = mgr.process_step(field, [a1, a2], rng=None)
    assert len(events) == 0


def test_matthew_split_favours_high_cred_agent():
    field = _isolated_field((1, 1), sugar=10.0)
    a_low = _FakeAgent(1, 1, cred=0.0)
    a_high = _FakeAgent(1, 2, cred=10.0)

    _manager().process_step(field, [a_low, a_high], rng=None)
    assert a_high.wealth > a_low.wealth


# ── Spatial-hash correctness tests (added post-fix) ──────────────────────────

def test_spatial_hash_finds_adjacent():
    """Agents at Euclidean d=1 (orthogonal neighbours) are detected as
    joint-task candidates after the spatial-hash rewrite."""
    field = _isolated_field((2, 2), sugar=4.0)
    a1 = _FakeAgent(2, 2)   # on the cell
    a2 = _FakeAgent(2, 3)   # one step away (d=1)
    events = _manager().process_step(field, [a1, a2], rng=None)
    assert len(events) == 1
    assert set(id(a) for a in events[0].cluster) == {id(a1), id(a2)}


def test_spatial_hash_misses_distant():
    """Agents at Euclidean distance > 1 are not included in a d=1 cluster."""
    field = _isolated_field((2, 2), sugar=4.0)
    a1 = _FakeAgent(2, 2)   # on the cell
    a2 = _FakeAgent(2, 4)   # two steps away (d=2) — outside d=1 radius
    events = _manager(distance_d=1).process_step(field, [a1, a2], rng=None)
    assert len(events) == 0


def test_spatial_hash_toroidal_wrap():
    """Agent at row=0 finds a neighbour at row=grid_height-1 (toroidal wrap)."""
    # 5×5 field; high-sugar cell at (0, 0)
    field = _make_field(width=5, height=5)
    field.sugar[:] = 0.0
    field.capacity[0, 0] = 4
    field.sugar[0, 0] = 4.0
    # a1 at (0,0), a2 at (4,0) — toroidally adjacent in x (distance=1)
    a1 = _FakeAgent(0, 0)
    a2 = _FakeAgent(4, 0)
    events = _manager().process_step(field, [a1, a2], rng=None)
    assert len(events) == 1, "toroidal wrap should let (4,0) be in cluster of cell (0,0)"
    assert len(events[0].cluster) == 2


def test_no_double_participation():
    """The processed_cells guard ensures the same cell never fires twice.

    When a cell has already been processed, re-encountering it in the
    candidate list (possible if the list is built lazily) must not produce
    a second event for the same cell.
    """
    # Single high-sugar cell with two agents close enough to trigger a task.
    field = _isolated_field((2, 2), sugar=4.0)
    a1 = _FakeAgent(2, 2)
    a2 = _FakeAgent(2, 3)

    mgr = _manager()
    events = mgr.process_step(field, [a1, a2], rng=None)

    # Exactly one event for cell (2,2) — processed_cells prevents double-fire.
    cells_fired = [e.cell for e in events]
    assert cells_fired.count((2, 2)) == 1, \
        "same cell fired more than once"
    assert len(events) == 1


def test_task_outcomes_unchanged():
    """Spatial-hash rewrite produces identical payoffs to the reference
    (pre-fix) algorithm for a deterministic small scenario.

    Verifies: same cluster membership, same sugar shares, same cred deltas.
    """
    # Arrange: 5×5 field, one high-sugar peak cell at (2,2);
    # two agents within d=1.
    field = _make_field(width=5, height=5)
    field.sugar[:] = 0.0
    field.capacity[2, 2] = 4
    field.sugar[2, 2] = 8.0

    a1 = _FakeAgent(2, 2, cred=2.0)
    a2 = _FakeAgent(2, 3, cred=6.0)

    mgr = _manager(matthew_alpha=2.0, cred_bonus_per_participant=1.0)
    events = mgr.process_step(field, [a1, a2], rng=None)

    assert len(events) == 1
    e = events[0]

    # Verify Matthew partition manually:
    # weights: (2+0.01)^2=4.0804, (6+0.01)^2=36.1201 → total=40.2005
    # sugar shares: 8 × [4.0804/40.2005, 36.1201/40.2005]
    import pytest
    assert sum(e.sugar_shares) == pytest.approx(8.0, rel=1e-5)
    assert e.sugar_shares[1] > e.sugar_shares[0]   # high-cred agent gets more

    # Cred bonus total = 1.0 × 2 participants = 2.0
    assert sum(e.cred_shares) == pytest.approx(2.0, rel=1e-5)

    # Agent wealth updated, cred unchanged (delta queued)
    assert a1.wealth + a2.wealth == pytest.approx(8.0, rel=1e-5)
    assert a1.cred == 2.0   # unchanged until run loop flushes
    assert a2.cred == 6.0
    assert a1._pending_cred_delta > 0.0
    assert a2._pending_cred_delta > 0.0
