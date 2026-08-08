"""TIER 5 — BANDS. The decomposition of MARKER_MATRIX #1, which turns out to be two faults on two tiers.

#1 reports "band_med FAILS 16/16 on adults — model 11.8 adults/band against Hill 2011's 28.2, = 0.42x". That
is a single verdict on a single number, and the ladder's rule is that a failure at tier N is diagnosed at tier
N or BELOW. Doing that splits it in two.

MEASURED on the long_climate run (2026-08-07):

    band_med, all ages   23.0
    frac_child           0.589
    => adults per band    9.4          (consistent with the 11.8 reported on other arms)

Now hold the band size fixed and correct only the age structure, which is a TIER 3 fault (births 5.66 %/yr and
starvation deaths 3.80 %/yr — a high-turnover regime, see test_tier3_demography_ctb.py):

    at the Ache child fraction 0.40, the same 23-person band holds  13.8 adults

**So fixing tier 3 closes about a third of the gap and no more.** 13.8 against 28.2 is still a factor of two,
and that residual is a genuine TIER 5 fault: the bands themselves are too small. Put the other way, to hold
28.2 adults at the measured child fraction a band would need 69 people — three times what the model produces.

That decomposition is the point of the ladder. "band_med fails" was one number hiding two problems on two
tiers, and neither is fixable at the tier where the marker is scored.
"""
import pytest

# The measured quantities. Recorded here so the decomposition cannot drift away from what was observed.
BAND_MED_ALL_AGES = 23.0
FRAC_CHILD_MEASURED = 0.589
FRAC_CHILD_ACHE = 0.40
HILL_ADULTS_PER_BAND = 28.2


def _adults(band_all_ages, frac_child):
    return band_all_ages * (1.0 - frac_child)


def test_the_measured_adult_count_follows_from_band_size_and_the_child_fraction():
    """First that the arithmetic is the arithmetic: the adult count is not an independent measurement, it is
    the all-ages band scaled by one minus the child share. Anything that moves either moves it."""
    assert _adults(BAND_MED_ALL_AGES, FRAC_CHILD_MEASURED) == pytest.approx(9.4, abs=0.2)


def test_correcting_the_tier3_age_structure_closes_only_a_THIRD_of_the_gap():
    """THE DECOMPOSITION. If the pyramid were at the Ache anchor and nothing else changed, the band would hold
    13.8 adults — up from 9.4, and still half of Hill's 28.2.

    So the age structure is a real contributor and not the main one. A fix aimed only at fertility would move
    #1 from 'fails badly' to 'fails', and someone would reasonably conclude the fix had not worked."""
    now = _adults(BAND_MED_ALL_AGES, FRAC_CHILD_MEASURED)
    corrected = _adults(BAND_MED_ALL_AGES, FRAC_CHILD_ACHE)
    assert corrected == pytest.approx(13.8, abs=0.3)

    closed = (corrected - now) / (HILL_ADULTS_PER_BAND - now)
    assert 0.20 < closed < 0.30, f"the age fix closes {closed:.0%} of the gap"
    assert corrected < HILL_ADULTS_PER_BAND / 1.9, "a factor-of-two residual remains after the age fix"


def test_the_residual_is_a_genuine_TIER_5_band_size_fault():
    """The other half. To hold Hill's 28.2 ADULTS at the measured child fraction, a band would need 69 people
    against the 23 the model produces — a threefold shortfall in band size itself, which no age-structure
    correction can supply."""
    needed_all_ages = HILL_ADULTS_PER_BAND / (1.0 - FRAC_CHILD_MEASURED)
    assert needed_all_ages == pytest.approx(69.0, abs=2.0)
    assert needed_all_ages > 2.5 * BAND_MED_ALL_AGES


def test_even_a_perfect_age_structure_leaves_the_band_too_small():
    """The cleanest statement of the residual: with the Ache pyramid AND the model's band size, adults still
    fall short by more than a factor of two. Both tiers have to move."""
    needed_all_ages_ache = HILL_ADULTS_PER_BAND / (1.0 - FRAC_CHILD_ACHE)
    assert needed_all_ages_ache == pytest.approx(47.0, abs=1.0)
    assert needed_all_ages_ache > 2.0 * BAND_MED_ALL_AGES


def test_the_all_ages_band_is_NOT_wildly_wrong_which_is_why_the_old_reading_passed():
    """Why #1 'passed' 23/25 on the all-ages unit for so long: 23 people is inside Birdsell's ~25 and Marlowe's
    25–50, so the all-ages number looks fine. It is fine — as a count of BODIES. Hill's 28.2 counts ADULTS, and
    the model reaches that count only by including children it should not have.

    This is the unit error MARKER_MATRIX #1 already records, seen from the band side."""
    assert 18 <= BAND_MED_ALL_AGES <= 35, "the all-ages band sits in the ethnographic range"
    assert _adults(BAND_MED_ALL_AGES, FRAC_CHILD_MEASURED) < 0.5 * HILL_ADULTS_PER_BAND


def test_the_two_faults_are_on_different_tiers_and_neither_is_at_tier_5s_marker():
    """The ladder's rule applied: a failure at tier N is diagnosed at tier N or below. #1 is scored at tier 5;
    one of its causes is at tier 3 and the other is at tier 5. Nothing about it is diagnosable at tier 9 or
    above, which is where most of the project's recent attention has been."""
    contributions = {
        "tier 3 — high-turnover age structure": _adults(BAND_MED_ALL_AGES, FRAC_CHILD_ACHE)
                                                - _adults(BAND_MED_ALL_AGES, FRAC_CHILD_MEASURED),
        "tier 5 — bands too small": HILL_ADULTS_PER_BAND - _adults(BAND_MED_ALL_AGES, FRAC_CHILD_ACHE),
    }
    assert all(v > 0 for v in contributions.values()), contributions
    assert contributions["tier 5 — bands too small"] > 2.5 * contributions["tier 3 — high-turnover age structure"]
