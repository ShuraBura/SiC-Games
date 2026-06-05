"""Tests for BoundedRationalSi strategy."""
from __future__ import annotations

import math
import random

import pytest

from sic_games.agents.perception import CellView, Perception
from sic_games.agents.strategies.si_bounded import BoundedRationalSi


class _FakeAgent:
    def __init__(self, cred: float = 5.0, phi: float = 0.5, wealth_velocity: float = 1.0):
        self.cred = cred
        self.phi = phi
        self.pos = (5, 5)
        self.wealth_velocity = wealth_velocity


def _perc(*cells):
    return Perception(
        visible_cells=tuple(CellView(x, y, s) for x, y, s in cells),
        current_x=5,
        current_y=5,
    )


SIGMA = 1.051


def test_temperature_constant_regardless_of_cred():
    dec = BoundedRationalSi(sigma_si=SIGMA)
    for cred in [0.0, 1.0, 10.0, 100.0]:
        agent = _FakeAgent(cred=cred)
        assert dec.temperature(agent) == pytest.approx(SIGMA)


def test_temperature_constant_regardless_of_phi():
    dec = BoundedRationalSi(sigma_si=SIGMA)
    for phi in [0.0, 0.3, 0.7, 1.0]:
        agent = _FakeAgent(phi=phi)
        assert dec.temperature(agent) == pytest.approx(SIGMA)


def test_temperature_constant_regardless_of_velocity():
    dec = BoundedRationalSi(sigma_si=SIGMA)
    for v in [-5.0, 0.0, 5.0]:
        agent = _FakeAgent(wealth_velocity=v)
        assert dec.temperature(agent) == pytest.approx(SIGMA)


def test_utilities_proportional_to_sugar():
    dec = BoundedRationalSi(sigma_si=SIGMA)
    agent = _FakeAgent()
    cells = (CellView(0, 0, 2.0), CellView(1, 0, 4.0), CellView(2, 0, 4.0))
    utils = dec.compute_utilities(agent, cells)
    # _normalize divides by max, so [0.5, 1.0, 1.0]
    assert utils == pytest.approx([0.5, 1.0, 1.0])


def test_utilities_no_cred_term():
    """Utilities must not change when only cred varies."""
    dec = BoundedRationalSi(sigma_si=SIGMA)
    cells = (CellView(0, 0, 3.0), CellView(1, 0, 6.0))
    u_low = dec.compute_utilities(_FakeAgent(cred=0.0), cells)
    u_high = dec.compute_utilities(_FakeAgent(cred=99.0), cells)
    assert u_low == pytest.approx(u_high)


def test_softmax_probabilities_analytic():
    """For a 2-cell case, probabilities should match analytic softmax."""
    dec = BoundedRationalSi(sigma_si=SIGMA)
    agent = _FakeAgent()
    # cells with sugar 0 and max => normalized utils [0.0, 1.0]
    perc = _perc((0, 0, 0.0), (1, 0, 4.0))
    rng = random.Random(0)

    # Analytic: utils=[0.0, 1.0], sigma=SIGMA
    # scaled = [0/SIGMA, 1/SIGMA]; subtract max=1/SIGMA → [-1/SIGMA, 0]
    # exp_vals = [exp(-1/SIGMA), 1]; total = exp(-1/SIGMA)+1
    e = math.exp(-1.0 / SIGMA)
    p0_expected = e / (e + 1.0)
    p1_expected = 1.0 / (e + 1.0)

    # Sample many times to verify probabilities are approximately correct
    counts = {(0, 0): 0, (1, 0): 0}
    N = 10000
    for _ in range(N):
        pos = dec.select_target(agent, perc, rng)
        counts[pos] += 1

    assert counts[(0, 0)] / N == pytest.approx(p0_expected, abs=0.02)
    assert counts[(1, 0)] / N == pytest.approx(p1_expected, abs=0.02)


def test_select_target_returns_valid_cell():
    dec = BoundedRationalSi(sigma_si=SIGMA)
    agent = _FakeAgent()
    perc = _perc((2, 3, 1.0), (4, 5, 2.0), (6, 7, 3.0))
    rng = random.Random(42)
    for _ in range(100):
        pos = dec.select_target(agent, perc, rng)
        assert pos in {(2, 3), (4, 5), (6, 7)}


def test_all_zero_sugar_still_selects():
    """All-zero sugar should not crash (normalize with max=1 fallback)."""
    dec = BoundedRationalSi(sigma_si=SIGMA)
    agent = _FakeAgent()
    perc = _perc((0, 0, 0.0), (1, 0, 0.0))
    rng = random.Random(1)
    pos = dec.select_target(agent, perc, rng)
    assert pos in {(0, 0), (1, 0)}
