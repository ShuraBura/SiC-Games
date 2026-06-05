"""Tests for metrics.py — Gini, spatial dispersion, and C spatial density."""
import math

import pytest

from sic_games.metrics import c_spatial_density, gini, spatial_dispersion


def _reference_gini(values: list[float]) -> float:
    """Reference implementation: mean absolute difference formula."""
    n = len(values)
    if n < 2:
        return 0.0
    total = sum(values)
    if total == 0:
        return 0.0
    mad = sum(abs(a - b) for a in values for b in values) / (n * n)
    return mad / (2 * total / n)


def test_gini_equal_distribution():
    assert gini([1.0, 1.0, 1.0, 1.0]) == pytest.approx(0.0, abs=1e-9)


def test_gini_maximum_inequality():
    # One agent has all the wealth
    vals = [0.0, 0.0, 0.0, 4.0]
    # Gini = 1 - 1/n for this distribution (all wealth to one agent)
    # With n=4: (4-1)/4 = 0.75
    assert gini(vals) == pytest.approx(0.75, abs=1e-6)


def test_gini_matches_reference():
    """Compare against the mean-absolute-difference reference formula."""
    test_cases = [
        [1.0, 2.0, 3.0, 4.0, 5.0],
        [10.0, 10.0, 10.0, 100.0],
        [0.5, 1.0, 2.0, 5.0, 10.0, 20.0],
    ]
    for vals in test_cases:
        ours = gini(vals)
        ref = _reference_gini(vals)
        assert ours == pytest.approx(ref, abs=1e-4), f"Mismatch for {vals}: {ours} vs {ref}"


def test_gini_single_agent():
    assert gini([5.0]) == 0.0


def test_gini_all_zero():
    assert gini([0.0, 0.0, 0.0]) == 0.0


def test_spatial_dispersion_uniform_grid():
    # Agents uniformly spread across a 10x10 grid — high dispersion
    positions = [(x, y) for x in range(10) for y in range(10)]
    disp = spatial_dispersion(positions, width=50, height=50)
    assert disp > 0.0


def test_spatial_dispersion_clustered():
    # All agents at same point — dispersion 0
    positions = [(5, 5)] * 50
    disp = spatial_dispersion(positions, width=50, height=50)
    assert disp == pytest.approx(0.0, abs=1e-6)


def test_spatial_dispersion_empty():
    assert spatial_dispersion([], 50, 50) == 0.0


# ---------------------------------------------------------------------------
# Tests for c_spatial_density (Stage 4.4 Diagnostic)
# ---------------------------------------------------------------------------

def test_c_spatial_density_empty():
    """Empty population → both metrics 0."""
    dist, pct = c_spatial_density([], 50, 50)
    assert dist == 0.0
    assert pct == 0.0


def test_c_spatial_density_single():
    """Single agent is trivially isolated (100%) and has no nearest neighbour."""
    dist, pct = c_spatial_density([(5, 5)], 50, 50)
    assert dist == 0.0
    assert pct == 100.0


def test_c_spatial_density_two_adjacent():
    """Two agents at Chebyshev distance 1 — not isolated (r=3), mean_nearest=1."""
    dist, pct = c_spatial_density([(5, 5), (6, 5)], 50, 50, isolation_radius=3)
    assert dist == pytest.approx(1.0, abs=1e-9)
    assert pct == pytest.approx(0.0, abs=1e-9)


def test_c_spatial_density_two_far_apart():
    """Two agents at Chebyshev distance 10 — both isolated for r=3."""
    dist, pct = c_spatial_density([(5, 5), (15, 15)], 50, 50, isolation_radius=3)
    assert dist == pytest.approx(10.0, abs=1e-9)
    assert pct == pytest.approx(100.0, abs=1e-9)


def test_c_spatial_density_toroidal_wrap():
    """Agents on opposite corners of a 10×10 toroidal grid: Chebyshev distance = 1."""
    # (0,0) and (9,9) on a 10×10 grid: toroidal dx=min(9,1)=1, dy=min(9,1)=1 → cheb=1
    dist, pct = c_spatial_density([(0, 0), (9, 9)], 10, 10, isolation_radius=3)
    assert dist == pytest.approx(1.0, abs=1e-9)
    assert pct == pytest.approx(0.0, abs=1e-9)


def test_c_spatial_density_mixed_isolation():
    """Three agents: two close together, one far — 1/3 isolated."""
    # (5,5) and (5,6) are distance 1 apart (not isolated).
    # (25,25) is far from both — distance ~20, isolated.
    positions = [(5, 5), (5, 6), (25, 25)]
    dist, pct = c_spatial_density(positions, 50, 50, isolation_radius=3)
    # mean nearest: (1 + 1 + 20) / 3 = 7.333...
    assert dist == pytest.approx((1.0 + 1.0 + 20.0) / 3.0, abs=1e-6)
    assert pct == pytest.approx(100.0 / 3.0, abs=1e-6)
