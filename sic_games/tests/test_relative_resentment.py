"""R-94 — SCALE-FREE resentment: privilege as an EFFECT SIZE, not a ratio against a fixed reference.

THE BUG IT FIXES — the third instance of charter D15 in three consecutive results. Privilege was

    (mean_cred_ascribed − mean_cred_other) / mean_cred_other  ÷  resent_privilege_ref      [ref = 10.0]

and that reference was chosen while ascription was UNIVERSAL and cred saturated toward
1 + legit_cred_gain = 11. When R-93 turned nobility into a real 6% minority the gap shrank, privilege peaked at
0.166 against a 0.5 threshold, and the gumsa→gumlao reversion NEVER FIRED — 0 events in 3000 steps, against
5,741 under the previous regime. **The reverse mechanism had been calibrated against the BROKEN forward
mechanism**, so repairing the forward one moved the regime out from under it.

THE FIX is scale-free rather than a re-tuned constant (D15): the gap is measured in units of the band's OWN
pooled spread — an effect size. It does not care whether cred sits near 1 or near 11, and the threshold can be
anchored on Cohen's conventions (0.2 small / 0.5 medium / 0.8 large) instead of invented.

These are arithmetic tests over the formula itself rather than world runs, because the property under test —
invariance to the cred SCALE — is a property of the formula, and a world fixes the scale to whatever it happens
to produce.
"""
import pytest

from sic_games.demography import DemographyConfig
from sic_games.phase1_model import RESENT_EFFECT_CAP


def _priv_ratio(asc, oth, ref=10.0):
    """The OLD form: relative excess over the commoner mean, divided by a fixed reference."""
    m_a, m_o = sum(asc) / len(asc), sum(oth) / len(oth)
    return 0.0 if m_o <= 0.0 else max(0.0, (m_a - m_o) / m_o) / ref


def _priv_effect(asc, oth):
    """The NEW form: the gap in units of the band's own pooled spread."""
    m_a, m_o = sum(asc) / len(asc), sum(oth) / len(oth)
    vals = list(asc) + list(oth)
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / len(vals)) ** 0.5
    return 0.0 if sd <= 1e-9 else min(max(0.0, (m_a - m_o) / sd), RESENT_EFFECT_CAP)


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_relative_resentment is False and c.resent_effect_threshold == 0.8


def test_effect_size_is_invariant_to_the_cred_SCALE():
    """THE PROPERTY. The same social structure, expressed at a different cred scale, must give the same
    privilege — this is precisely what the ratio form lacks and what broke it."""
    asc, oth = [3.0, 3.2, 2.8], [1.0, 1.1, 0.9]
    base = _priv_effect(asc, oth)
    for k in (0.1, 10.0, 100.0):
        scaled = _priv_effect([v * k for v in asc], [v * k for v in oth])
        assert scaled == pytest.approx(base), f"effect size moved under scaling by {k}"


def test_the_ratio_form_is_NOT_scale_invariant_across_regimes():
    """THE BUG, shown rather than asserted. The ratio form depends on the ABSOLUTE cred level: the same rank
    separation reads very differently depending on where cred happens to sit, which is how a threshold tuned in
    the saturated regime became unreachable in the minority regime."""
    saturated = _priv_ratio([11.0, 11.0, 11.0], [1.0, 1.0, 1.0])     # universal-ascription era
    minority = _priv_ratio([2.6, 2.6, 2.6], [1.0, 1.0, 1.0])         # measured post-R-93 ratio ~1.6
    assert saturated > 0.5 > minority, (saturated, minority)
    # the effect-size form separates them far less dramatically, because both are complete rank separations
    assert _priv_effect([11.0, 11.0, 11.0], [1.0, 1.0, 1.0]) == pytest.approx(
        _priv_effect([2.6, 2.6, 2.6], [1.0, 1.0, 1.0]))


def test_no_gap_gives_no_privilege():
    """Nobles indistinguishable from commoners ⇒ nothing to resent. The mechanism must be able to return zero."""
    assert _priv_effect([1.0, 1.2, 0.8], [1.0, 1.2, 0.8]) == pytest.approx(0.0, abs=1e-9)


def test_nobles_worse_off_gives_no_privilege():
    """Privilege floors at zero — a disadvantaged elite is not resented for its advantages."""
    assert _priv_effect([1.0, 1.0], [5.0, 5.0]) == 0.0


def test_uniform_band_cannot_generate_privilege():
    """sd == 0 means there is no DISCERNIBLE spread, whatever the means say. Guards the divide-by-zero and the
    degenerate case where an infinitesimal gap would otherwise read as infinite separation."""
    assert _priv_effect([1.0, 1.0], [1.0, 1.0]) == 0.0


def test_effect_size_is_capped():
    """A nearly-uniform band can produce an enormous effect size off a tiny absolute gap; the cap stops one
    degenerate band from dominating the resentment EMA."""
    assert _priv_effect([1.0001, 1.0001], [1.0, 1.0]) <= RESENT_EFFECT_CAP


def test_a_large_separation_clears_the_cohen_threshold():
    """The threshold is anchored, not invented: 0.8 is Cohen's 'large'. A clean rank separation must clear it,
    or the default is useless."""
    assert _priv_effect([3.0, 3.2, 2.8], [1.0, 1.1, 0.9]) > 0.8


def test_a_small_separation_does_not_clear_it():
    """And a marginal difference must NOT — otherwise the mechanism fires on noise."""
    assert _priv_effect([1.05, 1.10, 0.95], [1.00, 1.06, 0.92]) < 0.8
