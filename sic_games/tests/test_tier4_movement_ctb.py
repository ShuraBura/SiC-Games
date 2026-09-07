"""TIER 4 — MOVEMENT. CTB for the productivity-scaled stride, and the unit footgun it was carrying.

LADDER POSITION. Movement sits under bands (5) and settlement (9): where agents go decides who co-resides,
which decides band size, which is MARKER_MATRIX #1. Tier 4 had zero constructed-truth coverage.

THE ANCHOR. Kelly 1995 / Binford 2001: forager mobility scales inversely with productivity. Rich land, short
stride; poor land, long stride. `mobility_radius` implements
    r = clamp(round(base * (ref / max(value, floor)) ** exponent), base, r_max)

THE FOOTGUN, found here and NOT closed — which is the honest outcome. The function accepts two PRESSURE
SOURCES, NPP in g/m²/yr and an intake requirement RATIO, and its docstring said "caller is responsible for
passing the right value". Both mismatches are silent and fail in opposite directions:

    source="intake" fed an NPP value   ->  r pinned to `base`  ->  mechanism INERT while reading ON
    source="npp"    fed an intake one  ->  r pinned to `max`   ->  every agent at full stride regardless of
                                                                   productivity: Kelly/Binford INVERTED

TWO ATTEMPTS TO GUARD IT BOTH FAILED ON REAL DATA — rejecting small NPP broke four tests (arid cells are
genuinely below 20 g/m²/yr), rejecting large intake broke two (a well-fed agent genuinely reads 27). The
scales OVERLAP across their whole useful ranges, so no threshold separates them and the mismatch is only
catchable at the call site. The hazard is therefore documented rather than papered over, because a guard that
fires on legitimate input gets switched off and takes the sound half with it.
"""
import pytest

from sic_games.demography import DemographyConfig, mobility_radius


def _cfg(**over):
    return DemographyConfig().model_copy(update={"enable_productivity_mobility": True, **over})


# ── the off switch is a bit-exactness guarantee ───────────────────────────────────────────────────────────

def test_the_flag_off_returns_base_for_every_value():
    """`base` = 1 by default, so OFF must be bit-exact with every pre-R-39 run. If any value could change the
    stride while the flag is off, every historical result would need re-checking."""
    off = DemographyConfig()
    assert off.enable_productivity_mobility is False
    for v in (0.0, 1.0, 50.0, 900.0, 5000.0):
        assert mobility_radius(v, off) == off.mobility_base_radius


# ── the Kelly/Binford relationship, on constructed values ─────────────────────────────────────────────────

def test_rich_land_gives_the_base_stride_and_poor_land_a_longer_one():
    c = _cfg()
    assert mobility_radius(c.mobility_npp_ref, c) == c.mobility_base_radius
    assert mobility_radius(c.mobility_npp_ref * 2, c) == c.mobility_base_radius, "richer than ref cannot shrink below base"
    assert mobility_radius(200.0, c) > mobility_radius(600.0, c)


def test_the_stride_is_monotone_non_increasing_in_productivity():
    """THE ANCHORED RELATIONSHIP itself. Any non-monotonicity would mean a band moved MORE in richer land."""
    c = _cfg()
    vals = [50, 100, 200, 300, 450, 600, 900, 1500]
    radii = [mobility_radius(v, c) for v in vals]
    assert radii == sorted(radii, reverse=True), radii


def test_the_stride_matches_the_closed_form_on_hand_computed_points():
    """ref/value at exponent 1: 900/200 = 4.5 -> round 4 (within r_max 6); 900/50 = 18 -> clamped to 6."""
    c = _cfg()
    assert mobility_radius(200.0, c) == 4
    assert mobility_radius(50.0, c) == 6
    assert mobility_radius(450.0, c) == 2


def test_the_floor_stops_an_empty_cell_producing_an_unbounded_stride():
    """Without the floor, value -> 0 gives ratio -> infinity. The floor and r_max are two independent guards
    and both must hold, because a zero-NPP cell is a real thing on a generated world."""
    c = _cfg()
    assert mobility_radius(0.0, c) == c.mobility_max_radius
    assert mobility_radius(c.mobility_npp_floor / 10.0, c) == c.mobility_max_radius


def test_the_radius_is_always_an_int_within_its_declared_bounds():
    c = _cfg()
    for v in (0.0, 1e-6, 37.0, 251.0, 900.0, 1e6):
        r = mobility_radius(v, c)
        assert isinstance(r, int)
        assert c.mobility_base_radius <= r <= c.mobility_max_radius


# ── THE UNIT HAZARD ───────────────────────────────────────────────────────────────────────────────────────

def test_the_unit_mismatch_is_SILENT_IN_BOTH_DIRECTIONS_and_cannot_be_guarded_from_the_value():
    """THE HAZARD, and the honest limit — recorded after TWO attempts to guard it both failed on real data.

    The two mismatches fail in opposite ways and neither raises:
        source="intake" fed an NPP value  -> stride pins to `base` -> mechanism INERT while reading ON
        source="npp"    fed an intake one -> stride pins to `max`  -> Kelly/Binford exactly INVERTED

    Attempt 1 rejected small values under "npp" and broke four tests: an arid or near-water cell genuinely has
    NPP below 20 g/m²/yr, which is precisely what `mobility_npp_floor` exists for.
    Attempt 2 rejected large values under "intake" and broke two: a well-fed agent genuinely has an intake
    ratio of 27, early in a run when few agents sit on rich land.

    **The two scales overlap across their whole useful ranges.** No threshold separates them, so the mismatch
    is only catchable at the CALL SITE, by passing the value the source names. A guard that fires on
    legitimate input is worse than none — it gets switched off, and nothing replaces it.

    This test asserts the hazard is present and documented rather than pretending it is fixed."""
    npp = _cfg()
    intake = _cfg(mobility_pressure_source="intake")

    # the inert direction: an NPP value read as an intake ratio
    assert mobility_radius(900.0, intake) == intake.mobility_base_radius

    # the inverted direction: an intake ratio read as NPP
    assert mobility_radius(1.0, npp) == npp.mobility_max_radius

    # and both legitimate readings of those same numbers are ordinary
    assert mobility_radius(900.0, npp) == npp.mobility_base_radius
    assert mobility_radius(1.0, intake) == intake.mobility_base_radius


def test_every_value_a_real_world_can_present_is_accepted():
    """The property both failed guards violated. Every value either source can legitimately produce must
    pass — the arid NPP values below 20 AND the well-fed intake ratios above 20. Their overlap is exactly
    why neither direction is guardable."""
    npp = _cfg()
    for v in (0.0, 1.0, 5.0, 25.0, 50.0, 200.0, 900.0, 3000.0):
        assert mobility_radius(v, npp) >= npp.mobility_base_radius
    intake = _cfg(mobility_pressure_source="intake")
    for v in (0.05, 0.1, 0.5, 1.0, 2.0, 3.0, 19.0):
        assert mobility_radius(v, intake) >= intake.mobility_base_radius


def test_the_intake_source_scales_on_its_own_reference():
    """The point of the intake source (R-106): it is DENSITY-AWARE. A crowded cell dilutes intake regardless
    of the cell's nominal fertility, so the stride responds to actual shortfall rather than to geography."""
    c = _cfg(mobility_pressure_source="intake")
    assert mobility_radius(c.mobility_intake_ref, c) == c.mobility_base_radius
    assert mobility_radius(0.2, c) > mobility_radius(0.8, c)
    assert mobility_radius(c.mobility_intake_floor / 10.0, c) == c.mobility_max_radius
