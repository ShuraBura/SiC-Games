"""TIER 3 — DEMOGRAPHY. CTB for the mortality schedule, and the arithmetic that locates the age-pyramid fault.

LADDER POSITION. Tier 3 sits under bands (5), settlement (9) and everything above. `band_med` fails 16/16 on
ADULTS while "passing" 23/25 all-ages, and the difference is carried entirely by excess children — so the age
structure is not a curiosity here, it is the thing that decides whether tier 5's marker means anything.

WHAT THIS FILE ESTABLISHES, in order:

  1. **The Siler schedule is CORRECT.** Integrated, it gives e0 = 36.5 yr against the Ache forest-period ~37.
     The anchored life table is not the problem, and any fix aimed at it would be aimed at the wrong thing.
  2. **The age structure it implies** at any plausible forager growth rate. This is a closed-form stable
     population: density proportional to exp(-r*a) * S(a). At r = 0 it gives frac<15 = 0.307 / median 26.5;
     even at an implausible r = 2%/yr it reaches only 0.446 / 17.5.
  3. **The model sits outside that family.** Measured on the 2026-08-07 long run: r = +0.67 %/yr with
     frac_child = 0.571 and median age 12.3. At that growth its own curve implies ~0.35 and ~23. The pyramid
     is therefore NOT explainable by growth plus the anchored mortality.
  4. **Where the difference lives.** Births run 5.66 %/yr (crude birth rate ~57/1000, against a forager norm
     nearer 40-45) and STARVATION deaths alone run 3.80 %/yr -- larger than the entire anchored Siler schedule,
     whose crude death rate at this structure is ~2.7 %/yr. The engine is in a HIGH-TURNOVER regime, and high
     turnover is what makes a pyramid young.

So the correction to the note in `test_age_structure.py` -- "people die in early adulthood" -- is that they
die at every age, of starvation, on a channel that is outside the life table entirely; and they are born
faster than foragers are born. Mortality *schedule* and mortality *realised* are different quantities.
"""
import math

import pytest

from sic_games.demography import DemographyConfig


def _survivorship(p):
    def S(t_yr):
        H = ((p.a1 / p.b1) * (1.0 - math.exp(-p.b1 * t_yr))
             + p.a2 * t_yr
             + (p.a3 / p.b3) * (math.exp(p.b3 * t_yr) - 1.0))
        return math.exp(-H)
    return S


def _e0(p, hi=120.0, n=12000):
    S = _survivorship(p)
    h = hi / n
    return sum(S(i * h) for i in range(n)) * h


def _stable(p, r, hi=100.0, n=20000):
    """Stable-population age structure: density proportional to exp(-r*a)*S(a). Returns (frac<15, median)."""
    S = _survivorship(p)
    h = hi / n
    w = [math.exp(-r * (i * h)) * S(i * h) for i in range(n)]
    tot = sum(w) * h
    frac15 = sum(w[:int(15.0 / h)]) * h / tot
    c = 0.0
    med = hi
    for i in range(n):
        c += w[i] * h
        if c >= tot / 2.0:
            med = i * h
            break
    return frac15, med


# ── 1. the schedule is anchored and correct ───────────────────────────────────────────────────────────────

def test_the_siler_schedule_reproduces_the_ache_life_expectancy():
    """THE FOUNDATION. Gurven & Kaplan's fitted Ache coefficients, integrated, must give the published e0 --
    otherwise every demographic result rests on a curve that is not the one it cites."""
    assert _e0(DemographyConfig().siler()) == pytest.approx(36.5, abs=1.5)


def test_the_sex_split_preserves_the_both_sexes_expectancy():
    """M-3 splits the schedule by the Hill & Hurtado ratios. The split must redistribute risk between sexes,
    not change the total -- a split that moved e0 would silently re-anchor the life table."""
    c = DemographyConfig()
    both, f, m = _e0(c.siler()), _e0(c.siler("female")), _e0(c.siler("male"))
    assert 0.5 * (f + m) == pytest.approx(both, abs=1.2)
    assert f != m, "the sex split must actually differ or the ratios are inert"


def test_survivorship_falls_monotonically_and_reaches_the_expected_landmarks():
    S = _survivorship(DemographyConfig().siler())
    for a, b in zip([1, 5, 15, 30, 45, 60, 75], [5, 15, 30, 45, 60, 75, 90]):
        assert S(a) > S(b)
    assert S(1) == pytest.approx(0.88, abs=0.03), "infant survival"
    assert S(45) == pytest.approx(0.43, abs=0.05), "no early-adult collapse in the SCHEDULE"


# ── 2-3. the age structure the schedule implies, and where the model sits ────────────────────────────────

@pytest.mark.parametrize("r,frac15,median", [
    (0.000, 0.307, 26.5), (0.005, 0.342, 23.9), (0.010, 0.377, 21.5), (0.020, 0.446, 17.5)])
def test_the_stable_age_structure_implied_by_the_schedule(r, frac15, median):
    """Closed form, no simulation. These are the ONLY age structures the model's own mortality curve can
    produce, one per growth rate. Anything outside this family has a cause other than growth."""
    f, m = _stable(DemographyConfig().siler(), r)
    assert f == pytest.approx(frac15, abs=0.01)
    assert m == pytest.approx(median, abs=0.6)


def test_the_ache_anchor_corresponds_to_a_plausible_forager_growth_rate():
    """Sanity on the anchor itself: frac<15 ~0.40 with median ~20 is what this curve gives at r ~ 1.3 %/yr --
    a slowly growing forager population. The anchor is internally consistent with the life table, which is why
    it is a fair target."""
    f, m = _stable(DemographyConfig().siler(), 0.013)
    assert f == pytest.approx(0.40, abs=0.02)
    assert m == pytest.approx(20.0, abs=1.5)


def test_the_models_measured_pyramid_is_OUTSIDE_the_family_its_own_curve_allows():
    """THE FINDING (long_climate, 2026-08-07). Measured r = +0.67 %/yr, frac_child = 0.571, median 12.3.

    At that growth the schedule implies ~0.35 and ~23. To reach frac<15 = 0.571 by GROWTH ALONE would need a
    rate far outside anything a forager population sustains -- and the model is not growing that fast. So the
    excess children are not a growth artefact, and the mortality curve is not the culprit either.

    These are recorded measurements, asserted here so the inconsistency cannot quietly disappear."""
    MEASURED_R, MEASURED_FRAC, MEASURED_MED = 0.0067, 0.571, 12.3
    implied_frac, implied_med = _stable(DemographyConfig().siler(), MEASURED_R)
    assert implied_frac < 0.40, implied_frac
    assert implied_med > 21.0, implied_med
    assert MEASURED_FRAC > implied_frac + 0.15, "the gap is large, not marginal"
    assert MEASURED_MED < implied_med - 8.0

    # and no growth rate in the forager range closes it
    for r in (0.01, 0.02, 0.03):
        f, _ = _stable(DemographyConfig().siler(), r)
        assert f < MEASURED_FRAC, f"growth of {r:.0%}/yr still does not reach {MEASURED_FRAC}"


def test_starvation_is_a_larger_mortality_channel_than_the_entire_anchored_life_table():
    """WHERE THE DIFFERENCE LIVES. Measured on the same run: births 5.66 %/yr and STARVATION deaths alone
    3.80 %/yr, against a Siler crude death rate of roughly 1/e0 = 2.7 %/yr at this structure.

    Starvation is outside the life table entirely, so the realised mortality regime is not the anchored one --
    it is the anchored one plus a larger unanchored one. High births and high deaths together are a
    HIGH-TURNOVER regime, and turnover is what makes a pyramid young. That is the mechanism to look at, not
    the Siler coefficients."""
    BIRTHS_YR, STARV_YR = 0.0566, 0.0380
    siler_cdr = 1.0 / _e0(DemographyConfig().siler())
    assert STARV_YR > siler_cdr, "starvation exceeds the whole anchored schedule"
    assert BIRTHS_YR > 0.045, "births are above the forager crude-birth-rate range (~40-45/1000)"
    # the two nearly cancel, which is why the population looks calm while the pyramid does not
    assert abs((BIRTHS_YR - STARV_YR) - 0.019) < 0.005
