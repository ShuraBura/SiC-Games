"""CTB for the SCALED FAMILY FOOTPRINT (R-106, 2026-08-22).

THE DEFECT. `comove_footprint = 0` is documented as "exact snap": every co-moving family collapses onto ONE
cell. At the annual pairing gate (`aggregation_period = 12`) a cohort of new couples therefore stacks, and the
occupied-cell count halves in a single step. Measured on the arid world, step 12 -> 13:

    comove_footprint = 0        110 -> 75 cells,  occ 1.07 -> 1.56    collapse
    comove_footprint = 2        110 -> 114 cells, occ 1.07 -> 1.06    no collapse

In a world with ~0.07 people/cell of headroom that doubling is fatal. Two earlier hypotheses for the same
event were FALSIFIED first -- ablating the annual drought shock (`enable_tier2_shock`) and ablating
`band_cohesion` each left the collapse untouched -- so this is the surviving explanation, not the first guess.

THE FIX WAS ALREADY BUILT AND DARK. `comove_footprint_scaled` computes k proportional to 1/NPP, reusing the
Kelly/Binford shape that `mobility_radius` already uses, capped at `comove_footprint_max = 3`:

    world                  median NPP   k   family extent
    arid  flat-subtropical        293   2   25 cells = 2,500 km2
    mountain alpine-boreal        214   3   49 cells = 4,900 km2
    savanna coastal-savanna      1070   0    1 cell  =   100 km2
    BASE  coastal-temperate      1054   0    1 cell  =   100 km2
    forest coastal-tropical      2296   0    1 cell  =   100 km2

Rich worlds get k = 0, which IS the current exact snap -- so enabling this is bit-exact everywhere the land is
productive and only disperses families where it is not.

WHAT THIS DOES NOT DO. It does NOT rescue the arid world, which still goes extinct at step 54 from the
seasonal trough (median intake halves in one step while occupancy stays flat at 1.03) with no storage buffer,
because storage is gated to the overwintering zone by Binford ET and a hot desert never qualifies. That is a
separate open defect and is not claimed here.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "sic_games" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "sic_games" / "src"))

from sic_games.demography import DemographyConfig, footprint_radius  # noqa: E402

# Median NPP measured per canonical world at seed 0.
NPP = {"arid": 293.0, "mountain": 214.0, "savanna": 1070.0, "temperate": 1054.0, "forest": 2296.0}
RICH = ("savanna", "temperate", "forest")
POOR = ("arid", "mountain")


def _cfg(**over):
    return DemographyConfig(**over)


# ─────────────────────────── the mechanism is currently DARK ──────────────────────────────────────────

def test_the_scaled_footprint_is_off_by_default_so_this_is_a_dark_mechanism():
    """It is built, anchored and reachable, and nothing turns it on -- the pattern this project's flag audit
    exists to catch (27 of 79 flags were dark and nobody knew)."""
    c = DemographyConfig()
    assert c.comove_footprint_scaled is False
    assert c.comove_footprint == 0, "the fixed footprint is ALSO 0, so families snap exactly"


def test_the_unscaled_default_snaps_every_family_onto_one_cell():
    """The defect itself: with the flag off, footprint is 0 at EVERY productivity."""
    c = _cfg()
    for npp in NPP.values():
        assert footprint_radius(npp, c) == 0


# ─────────────────────────── bit-exactness where the land is rich ─────────────────────────────────────

@pytest.mark.parametrize("world", RICH)
def test_rich_worlds_get_k_zero_so_enabling_the_flag_changes_nothing(world):
    """THE NEGATIVE CONTROL that makes adoption safe. k = 0 is the exact-snap path, so every temperate,
    forest and savanna run is unchanged. If a rich world moved, adopting this would silently re-open every
    prior result."""
    on = footprint_radius(NPP[world], _cfg(comove_footprint_scaled=True))
    off = footprint_radius(NPP[world], _cfg())
    assert on == 0, f"{world} (NPP {NPP[world]}) got footprint {on}, expected 0"
    assert on == off, f"{world} changed when the flag was enabled"


@pytest.mark.parametrize("world", POOR)
def test_poor_worlds_disperse_the_family_over_its_range(world):
    """THE MECHANISM. A desert family cannot camp 5 people on 100 km2 -- the filed density is one person per
    170-200 km2 (Long 1971, Cane 1990). The footprint spreads them over the family's RANGE rather than its
    camp, which is what the coarse 100 km2 cell cannot otherwise represent."""
    k = footprint_radius(NPP[world], _cfg(comove_footprint_scaled=True))
    assert k >= 2, f"{world} (NPP {NPP[world]}) got footprint {k}, expected >= 2"


def test_the_footprint_is_monotone_in_productivity():
    """k ∝ 1/NPP: poorer land must never give a SMALLER family range than richer land."""
    c = _cfg(comove_footprint_scaled=True)
    ordered = sorted(NPP.items(), key=lambda kv: kv[1])          # poorest first
    ks = [footprint_radius(v, c) for _, v in ordered]
    assert ks == sorted(ks, reverse=True), f"footprint not monotone in 1/NPP: {list(zip(ordered, ks))}"


def test_the_footprint_is_capped_and_never_negative():
    """An unbounded footprint would scatter a family across the map on barren ground."""
    c = _cfg(comove_footprint_scaled=True)
    assert footprint_radius(1e-9, c) == c.comove_footprint_max, "must saturate at the cap on barren land"
    assert footprint_radius(1e9, c) == 0, "must not go negative on hyper-productive land"
    for npp in (0.0, 1.0, 50.0, 500.0, 5000.0, 1e6):
        k = footprint_radius(npp, c)
        assert 0 <= k <= c.comove_footprint_max


# ─────────────────────────── the quantity the fix is aimed at ─────────────────────────────────────────

def test_the_arid_family_extent_lands_near_the_filed_desert_density():
    """The whole point, in the units the anchor is stated in. At k=2 a family spreads over a 5x5 window; the
    algorithm places each follower on the lowest-occupancy cell, so a family of ~5 occupies ~5 cells of
    100 km2 = ~100 km2 per person = 0.01 /km2. The filed anchor is 0.005 /km2, one person per 170-200 km2
    (Long 1971, Cane 1990). Same order, and DERIVED from the NPP scaling rather than fitted to the anchor."""
    k = footprint_radius(NPP["arid"], _cfg(comove_footprint_scaled=True))
    window_cells = (2 * k + 1) ** 2
    assert window_cells >= 25, f"a 5x5 window is the minimum that can hold a family apart; got {window_cells}"
    per_person_km2 = 100.0                      # one follower per cell, cell = 100 km2
    assert 0.5 <= (1.0 / per_person_km2) / 0.005 <= 5.0, \
        "the implied density is more than 5x from the filed 0.005/km2 anchor"


def test_a_fixed_footprint_still_works_when_the_scaled_flag_is_off():
    """`comove_footprint` remains usable on its own, so an arm can set a flat radius without the NPP scaling.
    Guards against the scaled path silently swallowing the fixed one."""
    assert footprint_radius(NPP["forest"], _cfg(comove_footprint=2)) == 2
    assert footprint_radius(NPP["arid"], _cfg(comove_footprint=2)) == 2


def test_the_scaled_flag_overrides_the_fixed_value_as_documented():
    """The field comment says scaled 'overrides the fixed comove_footprint when True'. On rich land that means
    the fixed 2 must give way to 0 -- otherwise enabling scaling would NOT be bit-exact on rich worlds."""
    c = _cfg(comove_footprint=2, comove_footprint_scaled=True)
    assert footprint_radius(NPP["forest"], c) == 0
    assert footprint_radius(NPP["arid"], c) >= 2
