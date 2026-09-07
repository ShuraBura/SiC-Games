"""The age pyramid, the mating-suitability ratios, and the growth-regime call.

WHY (R-106, supervisor request 2026-08-04). The R-75 dashboard carried `median_age_yr`, `sex_ratio_m_f` and a
coarse child/adult/elder split — enough to notice something is wrong, not enough to say what. Three gaps, each
of which cost time in this arc:

  * **the pyramid itself.** The SHAPE distinguishes a growing population from a declining one; three classes
    cannot show it. Measured, the model's pyramid has a 3x cliff from 24.6% (15-30) to 8.5% (30-45) — people
    die in early adulthood — which is invisible in `frac_adult`.
  * **mating suitability.** `frac_unpaired_adult` is the φ that `LITERATURE.md` assumes is ≈0.1 when it
    derives `mate_search_min_eligible ≈ 15` from White's ~150-person MVP. NOTHING MEASURED IT. It is 0.012,
    eight times smaller, so the derivation had been wrong for three weeks (Addendum 25).
  * **the operational sex ratio.** Mate-seeking males per receptive female is what sets how far the connubium
    search must reach — and that reach was 11-75% of the entire population.

These are STOCK markers on the live population: pure measurement, no state mutated, one pass over agents that
the caller has already materialised.
"""
import math
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

from sic_games.phase1_model import TerrainWorld  # noqa: E402

PYRAMID_KEYS = ["age_0_5", "age_5_15", "age_15_30", "age_30_45", "age_45_60", "age_60_plus"]


@pytest.fixture(scope="module")
def markers():
    import battery1_liveness as B1

    from sic_games import runconfig
    # n=1500 / 300 steps is the configuration the pinned numbers below were MEASURED on. A shorter, smaller
    # run gives a genuinely different pyramid — at 200 steps the 15-30 : 30-45 ratio is 1.41 rather than 2.9,
    # because the cohort that will die in early adulthood has not reached it yet. Matching the fixture to the
    # measurement is the fix; loosening the assertion to cover both would pin nothing.
    w = B1._build(dict(runconfig.load().get("DemographyConfig", {})), n=1500, patch=30,
                  terr="coastal", clim="temperate", seed=0)
    for _ in range(300):
        w.step()
        if not w.agent_list:
            pytest.skip("population collapsed")
    return w.demography()


def test_the_pyramid_partitions_the_population(markers):
    """Every agent falls in exactly one class, so the shares are a distribution and not a sample of one."""
    total = sum(markers[k] for k in PYRAMID_KEYS)
    assert total == pytest.approx(1.0, abs=1e-9), f"pyramid classes sum to {total}, not 1"
    assert all(0.0 <= markers[k] <= 1.0 for k in PYRAMID_KEYS)


def test_the_pyramid_is_finer_than_the_coarse_split_it_supplements(markers):
    """The 0-5/5-15 classes must reconstruct `frac_child`, or the two views disagree about who is a child."""
    assert markers["age_0_5"] + markers["age_5_15"] == pytest.approx(markers["frac_child"], abs=1e-9)
    assert markers["age_60_plus"] == pytest.approx(markers["frac_elder"], abs=1e-9)


def test_mating_suitability_ratios_are_adult_only_and_finite(markers):
    """`sex_ratio_m_f` is over the WHOLE population including children; the mating-relevant ratios are
    adult-only, which is why they are separate keys rather than a refinement of that one."""
    assert 0.0 < markers["adult_sex_ratio"] < 10.0
    assert 0.0 <= markers["frac_unpaired_adult"] <= 1.0
    assert 0.0 <= markers["frac_unpaired_adult_m"] <= 1.0
    # An unpaired-adult share and a whole-population sex ratio are different quantities; if they ever come
    # out identical the plumbing has crossed.
    assert markers["frac_unpaired_adult"] != pytest.approx(markers["sex_ratio_m_f"])


def test_phi_is_measured_rather_than_assumed(markers):
    """THE BLOCKER. `LITERATURE.md` derives `mate_search_min_eligible ≈ 15` from White's ~150-person MVP via
    "a ~150-person breeding pool contains ~15 eligible males at φ≈0.1". Measured, φ is ~0.012 — so m*=15
    targets a pool far larger than 150 persons, and the re-anchor's arithmetic does not hold.

    WHEN THIS STARTS FAILING: φ has moved into the range the derivation assumed, so re-derive m* from
    White's MVP and re-measure `connubium_med` against Wobst's band."""
    phi = markers["frac_unpaired_adult"]
    assert phi < 0.05, (
        f"φ (unpaired-adult share) is now {phi:.3f}, no longer far below the 0.1 that LITERATURE.md's "
        f"m*≈15 derivation assumes — re-derive m* and re-measure the connubium reach")


def test_growth_regime_is_labelled_from_the_ratio_it_reports(markers):
    """The label must be reproducible from the raw number beside it, so it is never load-bearing on its own."""
    r = markers["pyramid_base_ratio"]
    assert r == r and r > 0.0
    assert markers["growth_regime"] == TerrainWorld._growth_regime(r, markers["dependency_ratio"])


@pytest.mark.parametrize("ratio,expected", [(2.0, "expansive"), (1.5, "expansive"), (1.0, "stationary"),
                                            (0.8, "stationary"), (0.5, "constrictive"),
                                            (float("nan"), "n/a")])
def test_growth_regime_boundaries(ratio, expected):
    assert TerrainWorld._growth_regime(ratio, 1.0) == expected


def test_the_pyramid_is_young_but_the_child_share_is_now_anchored(markers):
    """A FACT ABOUT THE MODEL, pinned so it cannot rot. RE-BASELINED 2026-08-28 (R-106 Addendum 54) when
    `enable_village_identity` was adopted; this test was previously
    `test_the_model_is_currently_pathologically_young` and pinned `frac_child` > 0.45.

    WHAT CHANGED. The old pathology was median age ~12.8 against the Aché ~20 and `frac_child` ~0.54 against
    a 0.287–0.454 forager range. Adopting village identity (co-resident bands merge into one community) moved
    the MARKER_MATRIX #16 family together, on this same fixture:

        frac_child        0.585 -> 0.414   INSIDE the Hill & Hurtado range, at the Aché value 0.419
        dependency_ratio  1.495 -> 0.907   was 1.66x the highest of three forager peoples; now ~= Aché 0.899
        sex_ratio_m_f     1.061 -> 0.987   still inside 0.896-1.368
        median_age_yr      12.8 -> 17.1    IMPROVED BUT STILL SHORT of the ~20 anchor
        frac_motherless    high -> 0.036   against ~0.02 Aché

    So #16's child share and sex ratio PASS, dependency misses its ceiling by 0.9 %, and median age remains
    the open gap. The turnover diagnosis in the old docstring still holds for what is LEFT: the early-adult
    cliff (15-30 : 30-45) is 2.71x and has not gone away. The Siler schedule was never the cause — integrated
    it gives e₀ = 36.5 yr against the Aché ~37 — see `test_tier3_demography_ctb.py`.

    RE-SCORED 2026-09-06 (R-106 Addendum 65) when `enable_density_fertility` was adopted (it closes the e0 gap,
    deaths→births). The median-age tripwire above fired, as designed. The #16 family moved together again, on
    this same fixture, and now sits AT the Aché anchor:

        frac_child        0.414 -> 0.371   still inside 0.287-0.454 (toward mid-range, from the Aché 0.419 top)
        dependency_ratio  0.907 -> 0.813   now BELOW the Aché 0.899
        sex_ratio_m_f     0.987 -> 1.089   still inside 0.896-1.368
        median_age_yr      17.1 -> 19.33   REACHED the ~20 anchor's neighbourhood — the open gap is closed
        frac_motherless   0.036 -> 0.006   below the Aché ~0.02
        early-adult ratio  2.71 -> 2.32    the cliff has SOFTENED but persists (> 2)

    WHAT THIS NOW PINS is the anchored regime, in BOTH directions: the child share stays inside the forager
    range, and median age stays in the anchor's neighbourhood — a regression that drops it back toward the old
    pathology (12.8) or the pre-density-fertility 17.1 fails the floor, and implausible over-aging fails the
    ceiling. If either bound starts failing, re-score the #16 family together, as MARKER_MATRIX requires, and
    update R-106."""
    assert 0.287 < markers["frac_child"] < 0.454, (
        "the child share has left the Hill & Hurtado forager range (0.287-0.454) — re-score MARKER #16")
    assert 18.0 < markers["median_age_yr"] < 21.0, (
        "median age has left the Aché anchor's neighbourhood (~20) — re-score MARKER #16 and update R-106")
    assert markers["age_15_30"] > 2.0 * markers["age_30_45"], (
        "the early-adult mortality cliff has softened — the pyramid is no longer collapsing at 30")
