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


def test_the_model_is_currently_pathologically_young(markers):
    """A FACT ABOUT THE MODEL, pinned so it cannot rot — this is MARKER_MATRIX #4/#5's open failure seen in
    one view. Measured median age ~12.8 against the Aché anchor ~20, `frac_child` ~0.54 against ~0.40, and a
    3x cliff between the 15-30 and 30-45 classes: people die in early adulthood.

    WHEN THIS STARTS FAILING the demographic engine has improved — re-score e₀, `median_age_yr`,
    `frac_child` and `frac_motherless` TOGETHER, as MARKER_MATRIX requires, and update R-106."""
    assert markers["median_age_yr"] < 18.0, "median age has reached the Aché anchor's neighbourhood"
    assert markers["frac_child"] > 0.45, "the child share has come down toward the ~0.40 anchor"
    assert markers["age_15_30"] > 2.0 * markers["age_30_45"], (
        "the early-adult mortality cliff has softened — the pyramid is no longer collapsing at 30")
