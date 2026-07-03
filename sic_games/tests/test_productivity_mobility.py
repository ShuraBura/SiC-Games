"""Productivity-scaled mobility (§4.8.19, blueprint …_ProductivityScaledMobility).

The diffusion step STRIDE scales inversely with static local NPP (Kelly 1995 / Binford 2001). These tests pin:
  - `mobility_radius` monotone-decreasing in NPP, clamped [base, r_max], off ⇒ base;
  - the glide candidate set in `diffusion_select_target` (stride positions, water-stop);
  - flag-off / base=1 / water=None ⇒ BIT-EXACT with the legacy r=1 mover.
"""
import numpy as np
import pytest

from sic_games.demography import DemographyConfig, mobility_radius
from sic_games.substrate import diffusion_select_target


def _cfg(**kw):
    base = dict(enable_productivity_mobility=True, mobility_base_radius=1, mobility_max_radius=6,
                mobility_npp_ref=900.0, mobility_npp_floor=50.0, mobility_exponent=1.0)
    base.update(kw)
    return DemographyConfig(**base)


# --------------------------------------------------------------------------- mobility_radius helper

def test_off_returns_base():
    c = _cfg(enable_productivity_mobility=False, mobility_base_radius=1)
    assert mobility_radius(10.0, c) == 1
    assert mobility_radius(5000.0, c) == 1


def test_high_npp_gives_base():
    c = _cfg()
    assert mobility_radius(900.0, c) == 1      # at ref
    assert mobility_radius(5000.0, c) == 1     # above ref → clamped to base


def test_low_npp_gives_longer_stride():
    c = _cfg()
    # npp 300 → 900/300 = 3
    assert mobility_radius(300.0, c) == 3
    # very low → clamped by floor (50) then r_max (6): 900/50 = 18 → 6
    assert mobility_radius(10.0, c) == 6


def test_monotone_decreasing_in_npp():
    c = _cfg()
    xs = [50, 100, 200, 400, 900, 2000]
    rs = [mobility_radius(x, c) for x in xs]
    assert all(rs[i] >= rs[i + 1] for i in range(len(rs) - 1))
    assert min(rs) == 1 and max(rs) <= c.mobility_max_radius


def test_exponent_flattens_response():
    steep = _cfg(mobility_exponent=1.0)
    flat = _cfg(mobility_exponent=0.0)
    # exponent 0 ⇒ ratio**0 = 1 ⇒ always base, regardless of NPP
    assert mobility_radius(100.0, flat) == 1
    assert mobility_radius(100.0, steep) > 1


def test_floor_bounds_arid():
    c = _cfg(mobility_npp_floor=100.0, mobility_max_radius=50)
    # denom floored at 100 ⇒ 900/100 = 9, not larger even at npp 1
    assert mobility_radius(1.0, c) == 9
    assert mobility_radius(0.0, c) == 9


# --------------------------------------------------------------------------- glide candidate set


class _Field:
    """Minimal sugar_field: uniform level, torus w×h."""
    def __init__(self, w=20, h=20, val=100.0):
        self.width, self.height, self._v = w, h, val
    def level(self, x, y):
        return self._v


class _SC:
    contest_exponent = 0.0
    phi_epsilon = 0.0
    k_cell = 0
    move_cost_flat = 0.0
    group_safety_max = 0.0
    group_safety_scale = 8.0
    group_mate_min = 0.0
    group_mate_floor = 0.3


class _Agent:
    strategy = "greedy"
    def __init__(self, pos):
        self.pos = pos


def test_bit_exact_legacy_when_r1_no_water():
    """base=1, water=None ⇒ identical target to the legacy call (no move_radius arg)."""
    f, sc = _Field(), _SC()
    for px in range(3, 17):
        a1, a2 = _Agent((px, 8)), _Agent((px, 8))
        occ = {(px, 8): 1}
        t_legacy = diffusion_select_target(a1, f, occ, None, sc, None, None)
        t_new = diffusion_select_target(a2, f, dict(occ), None, sc, None, None, move_radius=1, water=None)
        assert t_legacy == t_new


def test_stride_reaches_distance_r():
    """With a yield gradient, a stride-3 mover can jump 3 cells toward the richer cell in one step."""
    class Grad(_Field):
        def level(self, x, y):
            return float(x)      # increasing east → argmax picks the farthest-east candidate
    f, sc = Grad(), _SC()
    a = _Agent((8, 8))
    occ = {(8, 8): 1}
    t = diffusion_select_target(a, f, occ, None, sc, None, None, move_radius=3,
                                water=np.zeros((20, 20), dtype=np.uint8))
    assert t == (11, 8)          # +3 east (the glide's farthest land cell), not +1


def test_glide_stops_at_water():
    """A water cell at distance 2 blocks the ray; the farthest LAND candidate is distance 1."""
    class Grad(_Field):
        def level(self, x, y):
            return float(x)
    f, sc = Grad(), _SC()
    water = np.zeros((20, 20), dtype=np.uint8)
    water[8, 10] = 1             # (x=10, y=8) is water → east ray blocked beyond x=9
    a = _Agent((8, 8))
    occ = {(8, 8): 1}
    t = diffusion_select_target(a, f, occ, None, sc, None, None, move_radius=5, water=water)
    assert t == (9, 8)          # farthest reachable land east is x=9 (x=10 blocked)


def test_glide_no_candidate_when_adjacent_water():
    """If the immediate east neighbour is water, the east ray contributes nothing (agent stays / picks elsewhere)."""
    f, sc = _Field(), _SC()
    water = np.zeros((20, 20), dtype=np.uint8)
    water[8, 9] = 1             # (x=9,y=8) water, immediately east of (8,8)
    a = _Agent((8, 8))
    occ = {(8, 8): 1}
    # uniform field ⇒ argmax tie-break keeps current cell; the key assertion is no crash + valid land target
    t = diffusion_select_target(a, f, occ, None, sc, None, None, move_radius=4, water=water)
    assert water[t[1], t[0]] == 0
