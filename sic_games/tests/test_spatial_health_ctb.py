"""CTB for the SPATIAL SANITY CHECK (R-106, 2026-08-16).

WHY THIS EXISTS. For a week the R-106 arc chased mortality, then fertility, on a population using 14% of its
land at 4.8x BELOW Binford packing regionally while sitting 1.4x ABOVE it locally, median intake 2.7x
requirement. Every input was already logged. Nobody multiplied `pop` by anything and compared it to the map.

THE LOAD-BEARING CASE is `test_the_real_run_that_motivated_this_is_caught`: the actual measured numbers from
`fert_sedoff_s0` must trip the paradox. A checker that does not fire on the run that prompted it is decoration.
Its companion `test_a_healthy_forager_landscape_is_not_flagged` is the NEGATIVE CONTROL — a sane landscape must
pass, or the checker is just a tripwire that always fires.
"""
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if os.path.join(ROOT, "sic_games", "src") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))

from sic_games.demography import SPATIAL_ANCHORS, expected_population, spatial_health  # noqa: E402

PACK = 0.091      # Binford 2001, persons/km²
CATCH = 314.0     # Vita-Finzi & Higgs 1970, km²


def test_the_anchors_are_the_filed_ones():
    """If either number drifts, every verdict below silently re-scales."""
    assert SPATIAL_ANCHORS["binford_packing_per_km2"][0] == pytest.approx(0.091)
    assert SPATIAL_ANCHORS["catchment_km2"][0] == pytest.approx(314.0)
    for _, note in SPATIAL_ANCHORS.values():
        assert "FILED" in note, "an anchor without a filed source must not be scored against"


# ─────────────────────────── the case that motivated the checker ──────────────────────────────────────

def test_the_real_run_that_motivated_this_is_caught():
    """MEASURED, fert_sedoff_s0, coastal-temperate seed 0, mean of the last 120 steps:
    pop 3010, habitable 1584 cells, occupied 229 cells, 107 bands.
    regional 0.0190/km² (4.8x BELOW packing) while local 0.1320/km² (1.4x ABOVE it)."""
    h = spatial_health(pop=3010, habitable_cells=1584, cells_occupied=229, n_bands=107)
    assert h["regional_per_km2"] == pytest.approx(0.0190, abs=0.0005)
    assert h["local_per_km2"] == pytest.approx(0.1315, abs=0.001)
    assert h["land_use_frac"] == pytest.approx(0.1446, abs=0.002)
    assert h["km2_per_band"] == pytest.approx(214.0, abs=1.0)
    assert h["packed_locally"] is True
    assert h["sparse_regionally"] is True
    assert h["paradox"] is True, "THE run this checker exists for must trip it"
    assert h["band_below_catchment"] is True, "214 km² per band is inside one 10 km catchment (314 km²)"


def test_the_control_arm_is_caught_too():
    """claim_both: pop 2782, occupied 195, 102 bands. The paradox predates the fertility work."""
    h = spatial_health(pop=2782, habitable_cells=1584, cells_occupied=195, n_bands=102)
    assert h["paradox"] is True
    assert h["band_below_catchment"] is True


def test_savanna_the_extreme_case_is_caught():
    """fert_ctl_savanna: 240 agents on 12 occupied cells of 1544. Land use 0.8%."""
    h = spatial_health(pop=240, habitable_cells=1544, cells_occupied=12, n_bands=12)
    assert h["land_use_frac"] < 0.01
    assert h["paradox"] is True


# ─────────────────────────── the negative control ─────────────────────────────────────────────────────

def test_a_healthy_forager_landscape_is_not_flagged():
    """NEGATIVE CONTROL. A population spread over its range at a plausible forager density must PASS, or the
    checker is a tripwire that fires on everything and carries no information.

    7920 people at 0.05/km² over 158,400 km², in 317 bands of 25, using 90% of the land.
    """
    h = spatial_health(pop=7920, habitable_cells=1584, cells_occupied=1426, n_bands=317)
    assert h["regional_per_km2"] == pytest.approx(0.05, abs=0.002)
    assert h["local_per_km2"] < PACK, "spread out, so local density sits below the packing ceiling"
    assert h["paradox"] is False
    assert h["band_below_catchment"] is False
    assert h["km2_per_band"] > CATCH


def test_a_genuinely_full_world_is_not_flagged_as_a_paradox():
    """A population AT packing everywhere is dense but NOT paradoxical — it is simply full. The checker must
    distinguish 'full' from 'clumped', which is the whole point."""
    h = spatial_health(pop=14414, habitable_cells=1584, cells_occupied=1584, n_bands=577)
    assert h["regional_per_km2"] == pytest.approx(PACK, abs=0.002)
    assert h["sparse_regionally"] is False
    assert h["paradox"] is False, "at packing everywhere the population is FULL, not clumped"


def test_a_genuinely_empty_world_is_not_flagged_as_a_paradox():
    """A sparse population spread thinly is sparse but NOT paradoxical."""
    h = spatial_health(pop=1584, habitable_cells=1584, cells_occupied=1000, n_bands=63)
    assert h["sparse_regionally"] is True
    assert h["packed_locally"] is False
    assert h["paradox"] is False


# ─────────────────────────── the checker is load-bearing on each condition ────────────────────────────

def test_paradox_needs_BOTH_conditions():
    """Either alone must not trip it. This is what separates a distribution failure from ordinary density."""
    packed_only = spatial_health(pop=20000, habitable_cells=1584, cells_occupied=800, n_bands=800)
    assert packed_only["packed_locally"] is True and packed_only["sparse_regionally"] is False
    assert packed_only["paradox"] is False
    sparse_only = spatial_health(pop=800, habitable_cells=1584, cells_occupied=1500, n_bands=32)
    assert sparse_only["sparse_regionally"] is True and sparse_only["packed_locally"] is False
    assert sparse_only["paradox"] is False


def test_degenerate_inputs_do_not_raise():
    """A collapsed or pre-init run must not crash the panel that reports it."""
    for kw in ({"pop": 0, "habitable_cells": 1584, "cells_occupied": 0, "n_bands": 0},
               {"pop": 100, "habitable_cells": 0, "cells_occupied": 0, "n_bands": 0}):
        h = spatial_health(**kw)
        assert isinstance(h["paradox"], bool)


# ─────────────────────────── the expectation table ────────────────────────────────────────────────────

def test_expected_population_table_matches_the_filed_arithmetic():
    """158,400 km² at Binford packing carries 14,414 people in 577 bands of 25."""
    rows = expected_population(1584)
    at_pack = [r for r in rows if r[0] == pytest.approx(0.091)][0]
    assert at_pack[2] == pytest.approx(14414, abs=5)
    assert at_pack[3] == pytest.approx(577, abs=1)
    assert "FILED ANCHOR" in at_pack[1]


def test_the_illustrative_rows_are_labelled_so_nobody_cites_them_as_anchors():
    """Rule 2 of MARKER_MATRIX: a marker with no documented band is not scored. These rows are a reference
    bracket, and must say so in their own label."""
    for dens, lab, _, _ in expected_population(1584):
        if dens != pytest.approx(0.091):
            assert "illustrative" in lab and "ROUND" in lab, f"{dens} must not read as a filed band"
