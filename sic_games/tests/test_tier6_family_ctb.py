"""TIER 6 — FAMILY. The polygyny marker PASSES on a denominator that is not the anchor's.

WHY THIS MATTERS MORE THAN THE USUAL CASE. Every unit mismatch this project has found so far turned a
reported FAILURE into an artefact — `hayden_stage` on occupied vs regional density, `lineage_size_gini` on
rank-keys vs patrilines, `connubium_med` on two quantities in one list, `band_med` on adults vs all ages. This
one runs the other way: **marker #10 is currently reported as a PASS ("was 15x off; now 1.0x") and the
denominator underneath it is wrong.** A wrong unit is not more forgivable because the answer came out nice.

THE ANCHOR, VERIFIED VERBATIM (Marlowe, *The Hadza*, filed in `literature/`):

    "Since I have been working with the Hadza, about 4% of men have 2 wives at any given time, but never more
     than two wives, and these polygynous marriages are not very stable."

and again, independently: *"there are usually only about 4% of men with 2 wives."*

**The denominator is ALL MEN.** `frac_polygynous_m` divides by MARRIED men:

    frac_polygynous_m = (men with >1 wife) / (men with >=1 wife)

so the two differ by the male marriage rate. Measured on `long_climate`: 84.7% of adult men are married, so

    model on OUR denominator      0.0362   -> scored as ~0.9x the anchor, reported "1.0x"
    model on MARLOWE'S denominator 0.0307  -> 0.77x the anchor

The model is ~23% BELOW the Hadza rate on the anchor's own unit, not level with it. And because the gap is
exactly the marriage rate, **the size of the error moves between runs** — in an arm where fewer men are
married the discrepancy grows, and nothing currently accounts for that.
"""
import pytest

# Measured on long_climate (2026-08-07), recorded so the arithmetic cannot drift from what was observed.
FRAC_POLYGYNOUS_MARRIED = 0.0362
MALE_MARRIAGE_RATE = 0.847
MARLOWE_ALL_MEN = 0.04


def test_the_two_denominators_are_related_by_the_male_marriage_rate():
    """The conversion, stated once: polygynous/all-men = polygynous/married-men * married-fraction. Anything
    that changes how many men marry changes the comparison, without touching polygyny at all."""
    on_all_men = FRAC_POLYGYNOUS_MARRIED * MALE_MARRIAGE_RATE
    assert on_all_men == pytest.approx(0.0307, abs=0.0005)


def test_the_marker_reads_as_a_PASS_on_our_unit_and_a_23_percent_miss_on_the_anchors():
    """THE FINDING. On the married-men denominator the model looks level with Marlowe; on Marlowe's own
    denominator it is 0.77x. The marker is not badly wrong — but "1.0x" is not what it is."""
    ours = FRAC_POLYGYNOUS_MARRIED / MARLOWE_ALL_MEN
    theirs = (FRAC_POLYGYNOUS_MARRIED * MALE_MARRIAGE_RATE) / MARLOWE_ALL_MEN
    assert ours == pytest.approx(0.905, abs=0.02), "on our unit it reads as a pass"
    assert theirs == pytest.approx(0.77, abs=0.02), "on the anchor's unit it is a 23% shortfall"


def test_the_size_of_the_error_depends_on_the_marriage_rate_so_it_MOVES_between_runs():
    """The part that makes this more than a one-off correction. The discrepancy IS the marriage rate, so an
    arm with a different pairing regime carries a different error while the marker's definition never changes.
    A marker whose bias varies with an unrelated quantity cannot be compared across arms."""
    for rate in (0.5, 0.7, 0.847, 0.95):
        on_all_men = FRAC_POLYGYNOUS_MARRIED * rate
        assert on_all_men < FRAC_POLYGYNOUS_MARRIED
    # halving the marriage rate nearly halves the anchor-unit figure, with polygyny itself unchanged
    assert (FRAC_POLYGYNOUS_MARRIED * 0.5) / (FRAC_POLYGYNOUS_MARRIED * 0.95) == pytest.approx(0.526, abs=0.01)


def test_the_marlowe_quote_carries_a_SECOND_checkable_property_never_scored():
    """"...but NEVER MORE THAN TWO WIVES". That is a hard cap in the ethnography and a free extra check on the
    mating mechanism — a model producing men with three or four wives would violate the same sentence the 4%
    comes from, and nothing currently looks.

    Measured `mean_wives_married_m` = 1.0384, consistent with a population where a few men hold two. The cap
    itself is not asserted here because the diagnostic does not report a maximum — that is the gap this test
    records."""
    MEAN_WIVES_MARRIED = 1.0384
    assert 1.0 < MEAN_WIVES_MARRIED < 1.10
    # if every polygynous man held exactly 2, the mean would be 1 + frac_polygynous
    implied = 1.0 + FRAC_POLYGYNOUS_MARRIED
    assert MEAN_WIVES_MARRIED == pytest.approx(implied, abs=0.005), (
        "consistent with a strict two-wife cap; a third wife anywhere would push the mean above this")


def test_the_anchor_names_a_sentence_which_is_what_makes_it_checkable():
    """MARKER_MATRIX cites this as 'Marlowe, The Hadza' — an author and a book, the exact citation shape that
    failed for Bar-Yosef, BHM, Hill 2011 and Timmermann. It survived only because the book is filed and the
    sentence exists. `tools/verify_anchor.py` now registers the sentence so the check is mechanical."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
    from verify_anchor import REGISTRY
    labels = " ".join(label for label, _, _ in REGISTRY)
    assert "Marlowe" in labels, "the polygyny anchor must be in the verification registry"
