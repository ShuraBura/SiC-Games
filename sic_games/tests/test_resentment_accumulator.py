"""R-95 — resentment ACCUMULATES, and the VILLAGE holds it.

TWO FIXES, DELIBERATELY PAIRED. Neither works alone; `test_accumulator_on_bands_alone_is_not_enough` asserts
that rather than leaving it as a claim in a comment.

(a) THE MECHANISM NEVER ACCUMULATED. `_do_delegitimation`'s docstring says in capitals that resentment
    ACCUMULATES, after Leach - *"prestige-seeking only increased their followers' resentment and hastened their
    overthrow"*. The code was an EMA, which does not accumulate: it TRACKS, converging to whatever it is fed.
    A threshold at or above the typical privilege therefore can NEVER be crossed, at any horizon - not slowly,
    never. Measured (R-94, campaign scale): the grudge rose to 0.796 against a threshold of 0.800 and stopped
    there; 1 revolt in 3000 years. The irony worth recording: that 0.8 was ANCHORED (Cohen's "large"), and the
    real effect sizes genuinely are ~0.8 - a correct anchor pointed at the wrong quantity, because a running
    average cannot exceed its own input mean.

(b) THE MEMORY OUTLIVED ITS CONTAINER BY ~40-100x. R-88 measured band lifetime at 10.2 yr median / 17.5 mean;
    the grudge needed 700-1600 yr of sustained privilege to mature, and band fission resets it to zero. Leach's
    gumlao premises describe VILLAGES - "villages autonomous", headmen, councils of elders - not 25-person
    residential bands. Keying by settlement site follows R-71's precedent: the place remembers, members churn.

WHAT IS NOW ANCHORED, AND WHAT IS NO LONGER FREE. `resent_years_to_revolt` is the time to revolt under UNIT
privilege (an effect size of 1.0), set to 80 yr from Flannery ch.10's *"lasted for a few generations, and then
collapsed"* (~60-100 yr). The crossing threshold is FIXED AT 1.0 by construction - it stopped being a knob,
which is the point, since three consecutive results were caused by invented constants drifting out of range.
"""
import pytest

from sic_games.demography import DemographyConfig


def _accumulate(priv, years_to_revolt, steps):
    """The new rule, in isolation: r += priv/ytr each step, fires at 1.0."""
    r = 0.0
    for t in range(1, steps + 1):
        r += priv / years_to_revolt
        if r >= 1.0:
            return t
    return None


def _ema(priv, alpha, thr, steps):
    """The old rule, for contrast: r <- (1-a)r + a*priv, fires at thr."""
    r = 0.0
    for t in range(1, steps + 1):
        r = (1.0 - alpha) * r + alpha * priv
        if r >= thr:
            return t
    return None


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_resentment_accumulator is False
    assert c.enable_village_resentment is False
    assert c.resent_years_to_revolt == 80.0


def test_the_ema_can_never_cross_a_threshold_at_its_own_input_level():
    """THE R-94 BUG, demonstrated rather than asserted. This is not slowness - it is impossibility."""
    assert _ema(priv=0.8, alpha=0.001, thr=0.8, steps=1_000_000) is None
    assert _ema(priv=0.79, alpha=0.001, thr=0.8, steps=1_000_000) is None


def test_the_accumulator_always_crosses_given_sustained_privilege():
    """THE FIX. Any positive sustained privilege reaches the threshold eventually - the question becomes WHEN,
    which is the quantity Leach actually constrains."""
    for priv in (0.1, 0.5, 0.8, 2.0):
        assert _accumulate(priv, 80.0, 100_000) is not None


def test_unit_privilege_revolts_on_the_anchored_timescale():
    """`resent_years_to_revolt` means what it says: at an effect size of 1.0 the revolt lands at 80 yr, inside
    Flannery's "a few generations" (~60-100 yr).

    The +/-1 tolerance is FLOAT ACCUMULATION, not a modelling choice: 80 additions of 1/80 sum to
    0.9999999999999999, so it fires on step 81. One year in eighty is not a question about the ethnography."""
    assert _accumulate(priv=1.0, years_to_revolt=80.0, steps=1000) == pytest.approx(80, abs=1)


def test_time_to_revolt_scales_inversely_with_privilege():
    """Twice the gap, half the wait - the ethnographic claim that prestige-seeking HASTENED the overthrow."""
    assert _accumulate(2.0, 80.0, 1000) == pytest.approx(40, abs=1)
    assert _accumulate(0.5, 80.0, 1000) == pytest.approx(160, abs=1)


def test_threshold_is_no_longer_a_free_parameter():
    """It is fixed at 1.0 by construction; the timescale carries the calibration. Three consecutive results
    were caused by invented constants drifting out of range, so removing one is the point."""
    c = DemographyConfig()
    assert not hasattr(c, "resent_accumulator_threshold")


def test_accumulator_on_bands_alone_is_not_enough():
    """THE ENTANGLEMENT, asserted rather than claimed. A band lives 10.2 yr (median, R-88) and its grudge resets
    on fission. Even accumulating, a typical privilege cannot reach the threshold within one band's life - which
    is why the village unit is not an optional extra."""
    band_life_median, band_life_mean = 10.2, 17.5
    for life in (band_life_median, band_life_mean):
        for priv in (0.5, 0.8, 1.0):
            reached = priv / 80.0 * life
            assert reached < 1.0, (
                f"a grudge of {reached:.2f} would fire within a {life} yr band life at privilege {priv} — "
                "the entanglement argument would not hold")


def test_a_village_lived_long_enough_does_fire():
    """And the same privilege DOES boil over once the container survives long enough to hold the memory."""
    assert _accumulate(priv=0.8, years_to_revolt=80.0, steps=200) == pytest.approx(100, abs=1)
