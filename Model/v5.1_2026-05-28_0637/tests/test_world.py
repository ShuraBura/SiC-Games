"""Tests for world.py: capacity field and toroidal distance."""
import numpy as np
import pytest

from sic_games.world import SugarField, _toroidal_dist, build_capacity_field


PEAKS = [(10, 40), (40, 10)]


def test_toroidal_dist_no_wrap():
    assert _toroidal_dist(0, 0, 3, 4, 50, 50) == pytest.approx(5.0)


def test_toroidal_dist_wraps_x():
    # dist from x=0 to x=48 on width=50 should be 2, not 48
    assert _toroidal_dist(0, 0, 48, 0, 50, 50) == pytest.approx(2.0)


def test_toroidal_dist_wraps_y():
    assert _toroidal_dist(0, 0, 0, 49, 50, 50) == pytest.approx(1.0)


def test_peak_cell_has_max_capacity():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    for px, py in PEAKS:
        assert field.capacity[px, py] == 4, f"Peak ({px},{py}) should have capacity 4"


def test_desert_cell_has_zero_capacity():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    # Cell (36, 36) is ~24.3 units from each peak (floor(24.3/6)=4 → capacity=max(0,4-4)=0)
    assert field.capacity[36, 36] == 0


def test_capacity_non_negative_everywhere():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    assert (field.capacity >= 0).all()


def test_initial_sugar_equals_capacity():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    np.testing.assert_array_equal(field.sugar, field.capacity)


def test_harvest_removes_sugar():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    amount = field.harvest(10, 40)
    assert amount == 4.0
    assert field.sugar[10, 40] == 0.0


def test_total_sugar():
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=1)
    expected = float(field.capacity.sum())
    assert field.total_sugar() == pytest.approx(expected)
