"""Tests for LocalVisionPerception."""
import pytest

from sic_games.agents.perception import LocalVisionPerception
from sic_games.world import SugarField

PEAKS = [(10, 40), (40, 10)]


class _FakeAgent:
    def __init__(self, x, y, vision):
        self.pos = (x, y)
        self.vision = vision


def test_vision1_returns_cross_plus_current():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    agent = _FakeAgent(5, 5, vision=1)
    occupied = set()
    perc = LocalVisionPerception().build(agent, field, occupied)
    coords = {(c.x, c.y) for c in perc.visible_cells}
    # Current + 4 cardinal neighbors
    assert (5, 5) in coords
    assert (6, 5) in coords
    assert (4, 5) in coords
    assert (5, 6) in coords
    assert (5, 4) in coords
    assert len(coords) == 5


def test_vision2_extends_two_steps():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    agent = _FakeAgent(5, 5, vision=2)
    occupied = set()
    perc = LocalVisionPerception().build(agent, field, occupied)
    coords = {(c.x, c.y) for c in perc.visible_cells}
    assert (7, 5) in coords  # two steps right
    assert (3, 5) in coords  # two steps left
    assert (5, 7) in coords
    assert (5, 3) in coords
    assert len(coords) == 9  # 1 + 4*2


def test_wraps_toroidally():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    agent = _FakeAgent(0, 0, vision=1)
    occupied = set()
    perc = LocalVisionPerception().build(agent, field, occupied)
    coords = {(c.x, c.y) for c in perc.visible_cells}
    assert (49, 0) in coords  # wraps left
    assert (0, 49) in coords  # wraps down


def test_occupied_cells_excluded():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    agent = _FakeAgent(5, 5, vision=1)
    occupied = {(6, 5)}  # one neighbor occupied
    perc = LocalVisionPerception().build(agent, field, occupied)
    coords = {(c.x, c.y) for c in perc.visible_cells}
    assert (6, 5) not in coords
    assert len(coords) == 4  # current + 3 unoccupied neighbors


def test_sugar_values_match_field():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    field.sugar[5, 6] = 2.5
    agent = _FakeAgent(5, 5, vision=1)
    occupied = set()
    perc = LocalVisionPerception().build(agent, field, occupied)
    cell = next(c for c in perc.visible_cells if c.x == 5 and c.y == 6)
    assert cell.sugar == pytest.approx(2.5)
