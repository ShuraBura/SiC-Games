"""Tests for GreedyMaximizer (movement rule M)."""
import random

import pytest

from sic_games.agents.perception import CellView, Perception
from sic_games.agents.strategies.greedy import GreedyMaximizer


class _FakeModel:
    class _SF:
        width = 50
        height = 50

    sugar_field = _SF()


class _FakeAgent:
    model = _FakeModel()
    pos = (5, 5)

    def __init__(self, x=5, y=5):
        self.pos = (x, y)
        self.model = _FakeModel()


def _perception(cells: list[tuple[int, int, float]], cx=5, cy=5) -> Perception:
    return Perception(
        visible_cells=tuple(CellView(x, y, s) for x, y, s in cells),
        current_x=cx,
        current_y=cy,
    )


def test_picks_max_sugar_cell():
    agent = _FakeAgent(5, 5)
    perc = _perception([(5, 5, 0.0), (5, 6, 3.0), (5, 4, 1.0), (6, 5, 1.0)])
    rng = random.Random(0)
    target = GreedyMaximizer().select_target(agent, perc, rng)
    assert target == (5, 6)


def test_tie_break_by_distance_prefers_nearer():
    # Two cells with equal sugar: one at distance 1, one at distance 2
    agent = _FakeAgent(5, 5)
    perc = _perception([(5, 6, 4.0), (5, 7, 4.0)], cx=5, cy=5)
    rng = random.Random(0)
    target = GreedyMaximizer().select_target(agent, perc, rng)
    assert target == (5, 6)


def test_stay_in_place_when_current_cell_is_best():
    agent = _FakeAgent(5, 5)
    perc = _perception([(5, 5, 4.0), (5, 6, 1.0), (6, 5, 2.0)])
    rng = random.Random(0)
    target = GreedyMaximizer().select_target(agent, perc, rng)
    assert target == (5, 5)


def test_random_tiebreak_among_equidistant():
    # Three cells at same sugar and same distance — result should be one of them
    agent = _FakeAgent(5, 5)
    perc = _perception([(5, 6, 4.0), (6, 5, 4.0), (4, 5, 4.0)], cx=5, cy=5)
    rng = random.Random(42)
    results = set()
    for _ in range(50):
        t = GreedyMaximizer().select_target(agent, perc, random.Random())
        results.add(t)
    # Should see more than one result over many tries
    assert len(results) > 1


def test_single_cell_returned_immediately():
    agent = _FakeAgent(5, 5)
    perc = _perception([(5, 5, 0.0)])
    rng = random.Random(0)
    target = GreedyMaximizer().select_target(agent, perc, rng)
    assert target == (5, 5)


def test_toroidal_distance_tiebreak_across_boundary():
    # Cell at (0, 5) is 1 step from (49, 5) via wrap-around
    agent = _FakeAgent(49, 5)
    perc = _perception([(0, 5, 4.0), (20, 5, 4.0)], cx=49, cy=5)
    rng = random.Random(0)
    target = GreedyMaximizer().select_target(agent, perc, rng)
    # (0, 5) is distance 1 via wrap; (20, 5) is 29 away — should pick (0,5)
    assert target == (0, 5)
