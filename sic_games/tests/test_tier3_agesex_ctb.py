"""TIER 3 — AGE AND SEX STRUCTURE against the ethnographic record. Requested by the supervisor 2026-08-08.

THE ANCHOR, VERIFIED VERBATIM and unusually good: it states its own DEFINITION, which is what makes it
checkable rather than merely quotable.

    "The dependency ratios for the Ache (number of individuals under 15 or over 65 years divided by the number
     between 15 and 65 years) in 1970 and 1987 can be calculated ... In both cases the dependency ratios are
     high (0.79 for 1970, and 0.92 for 1987), indicating a very young population with high fertility."
                                              — Hill & Hurtado, *Ache Life History*, Ch. 4

**1970 is the precontact forager year** — the book says it was "the last year that all Northern Ache bands
lived as full-time uncontacted forest hunter-gatherers", so 0.79 is a forager number and 0.92 (1987) is not.

**AND THE ACHE ARE THE YOUNG END OF THE RANGE.** The same passage: the precontact Ache population "was
significantly younger than the !Kung", with the difference "primarily due to higher fertility among the
Ache". So 0.79 is not a middling target — it is close to the maximum a forager population reaches, and a model
above it is outside the ethnographic range rather than merely at its edge.

**MEASURED: 1.495.** Nearly twice the youngest well-documented forager population.

WHAT IS *NOT* ANCHORED, and why. Table 4.4 (Age-sex Composition of Ache, !Kung and Yanomamo) carries the sex
ratios, and the scan's numbers are OCR-garbled — the same state as Bar-Yosef's figures and Hayden's Fig. 6.
The prose gives only the direction ("the Ache sex ratio is significantly more male-biased than that of the
!Kung for both juveniles and adults"). **A human read of Table 4.4 would close the sex-ratio side of this
tier**; it is registered as NOT machine-readable rather than guessed at.
"""
import pytest

# Verified against the PDF, with the paper's own definition.
ACHE_DEPENDENCY_1970 = 0.79        # precontact forager year
ACHE_DEPENDENCY_1987 = 0.92        # post-contact, reservation — NOT a forager number

# Measured on long_climate (30,000 steps), last 40 checkpoints.
MODEL_DEPENDENCY = 1.495
MODEL_FRAC_CHILD = 0.585
MODEL_MEDIAN_AGE = 11.84
MODEL_SEX_RATIO_MF = 1.061
MODEL_ADULT_SEX_RATIO = 1.046


def test_the_model_and_the_anchor_use_DIFFERENT_elder_cutoffs():
    """THE UNIT, checked before the comparison. Hill & Hurtado cut elders at 65; `_demog_markers` cuts at 60,
    so ours counts 60-65-year-olds as dependent where theirs counts them as working. Ours is therefore biased
    UPWARD relative to the anchor — which matters, because the model is already above it."""
    from sic_games.phase1_model import TerrainWorld
    assert TerrainWorld._AGE_CHILD_YR == 15.0, "the child cutoff DOES match the anchor"
    assert TerrainWorld._AGE_ELDER_YR == 60.0
    assert TerrainWorld._AGE_ELDER_YR != 65.0, (
        "the elder cutoff does NOT match; the bias runs toward over-counting dependants")


def test_the_dependency_ratio_is_nearly_double_the_ache_forager_value():
    """THE FINDING. 1.495 against 0.79. The unit difference above makes ours slightly generous, but a
    60-vs-65 cutoff cannot account for a factor of 1.9 in a population with almost no one over 60."""
    assert MODEL_DEPENDENCY / ACHE_DEPENDENCY_1970 == pytest.approx(1.89, abs=0.05)
    assert MODEL_DEPENDENCY > ACHE_DEPENDENCY_1987, (
        "the model is above even the POST-CONTACT reservation value, which is not a forager number at all")


def test_the_ache_are_the_YOUNG_end_so_exceeding_them_is_out_of_range_not_at_its_edge():
    """The book states the precontact Ache were "significantly younger than the !Kung", driven by higher
    fertility. So 0.79 is near the top of the forager range, and 1.495 is outside it — this is not a model
    sitting at the edge of the ethnographic envelope."""
    assert ACHE_DEPENDENCY_1970 < 1.0, "even the youngest forager population has more workers than dependants"
    assert MODEL_DEPENDENCY > 1.0, "the model has MORE dependants than workers, which no forager arm reports"


def test_the_three_age_markers_tell_one_consistent_story():
    """Dependency ratio, child fraction and median age are not independent evidence — they are three views of
    the same pyramid, and MARKER_MATRIX rule 4 says they travel together. Consistency is the check that the
    diagnostics agree with each other before any of them is believed."""
    # with 58.5% children and few elders, dependants/workers should be about frac/(1-frac)
    implied = MODEL_FRAC_CHILD / (1.0 - MODEL_FRAC_CHILD)
    assert implied == pytest.approx(1.41, abs=0.05)
    assert MODEL_DEPENDENCY == pytest.approx(implied, abs=0.12), (
        "dependency ratio and child fraction must agree; a gap would mean the elder class is doing work it "
        "cannot do in a population this young")
    assert MODEL_MEDIAN_AGE < 15.0, "median age below the child cutoff is the same fact stated a third way"


def test_the_sex_ratio_is_measured_but_NOT_yet_anchored():
    """HONEST GAP. The model reports 1.061 (all ages) and 1.046 (adults) male-biased. The Ache are described
    as "significantly more male-biased than the !Kung", so the DIRECTION agrees — but a direction is not a
    target, and Table 4.4's numbers are OCR-garbled.

    This asserts only what can be asserted: the diagnostic runs, the values are plausible, and the sex ratio
    is male-biased as the source describes. Scoring it needs a human read of Table 4.4."""
    assert 0.9 < MODEL_SEX_RATIO_MF < 1.2, "a plausible sex ratio, not a broken one"
    assert MODEL_SEX_RATIO_MF > 1.0, "male-biased, the direction the source reports"
    assert MODEL_ADULT_SEX_RATIO > 1.0
    # and the two must be consistent: adults are a subset, so they cannot diverge wildly
    assert abs(MODEL_SEX_RATIO_MF - MODEL_ADULT_SEX_RATIO) < 0.10


def test_the_anchor_and_the_unreadable_table_are_both_in_the_registry():
    """One VERIFIED, one flagged NOT machine-readable. The second is the Bar-Yosef state, and recording it as
    such is what stopped that case becoming a phantom anchor."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
    from verify_anchor import REGISTRY, check
    rows = {label: check(rel, pat) for label, rel, pat in REGISTRY if "Ach" in label}
    assert any(s == "VERIFIED" for s, _ in rows.values()), rows
    assert any(s == "INTERPRETIVE" for s, _ in rows.values()), "Table 4.4 must be flagged, not guessed"
