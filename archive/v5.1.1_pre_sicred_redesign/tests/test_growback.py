"""Tests for G_alpha growback rule."""
import numpy as np

from sic_games.world import SugarField


PEAKS = [(10, 40), (40, 10)]


def _empty_field(alpha: int = 1) -> SugarField:
    field = SugarField(50, 50, PEAKS, max_capacity=4, band_width_k=6, alpha=alpha)
    field.sugar[:] = 0.0
    return field


def test_growback_adds_alpha_when_empty():
    field = _empty_field(alpha=1)
    field.growback()
    # Every cell with capacity > 0 should now have sugar == min(alpha, capacity)
    expected = np.minimum(1, field.capacity).astype(np.float32)
    np.testing.assert_array_equal(field.sugar, expected)


def test_growback_caps_at_capacity():
    field = _empty_field(alpha=1)
    # Set peak cell to capacity - 1
    px, py = PEAKS[0]
    field.sugar[px, py] = float(field.capacity[px, py] - 1)
    field.growback()
    assert field.sugar[px, py] == float(field.capacity[px, py])


def test_growback_does_not_exceed_capacity():
    field = _empty_field(alpha=1)
    field.sugar[:] = field.capacity.astype(np.float32)  # already full
    field.growback()
    np.testing.assert_array_equal(field.sugar, field.capacity)


def test_growback_zero_capacity_cell_stays_zero():
    field = _empty_field(alpha=1)
    # Cell (36, 36) has capacity 0 in canonical params (verified: ~24.3 from each peak)
    assert field.capacity[36, 36] == 0
    field.growback()
    assert field.sugar[36, 36] == 0.0


def test_partial_fill_advances_by_alpha():
    field = _empty_field(alpha=1)
    px, py = PEAKS[0]
    field.sugar[px, py] = 1.0  # capacity is 4
    field.growback()
    assert field.sugar[px, py] == 2.0


def test_growback_multiple_steps_fill_correctly():
    field = _empty_field(alpha=1)
    px, py = PEAKS[0]
    cap = field.capacity[px, py]  # 4
    for step in range(1, cap + 2):
        field.growback()
        assert field.sugar[px, py] == min(step, cap)
