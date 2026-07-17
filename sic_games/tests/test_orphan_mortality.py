"""Kin/orphan child mortality (R-74) — Hill & Hurtado 1996, Aché life history, Table 13.1.

"Parents, but not other kin, have a strong and unique influence on the mortality of Aché children living
in the forest period." Losing a parent — NOT birth-spacing infanticide — is the dominant killing channel:
Table 5.1 puts homicide/neglect at 39.7% of Aché 0–3 deaths, of which parental infanticide is only 5.3%;
the bulk is child homicide, grave accompaniment and neglect of orphans. And it is a HAZARD MULTIPLIER
(Table 13.1 controls age/age²/sex), not a separate killing event.

The load-bearing test here is `test_e0_invariant_at_ache_orphan_rates`: a1 already CONTAINS these deaths
("infanticide KEPT"), so the mechanism must REDISTRIBUTE mortality, not add a second helping of it.
"""
import math

import pytest

from sic_games.demography import ACHE_FOREST_NATURAL, DemographyConfig, SilerParams, life_expectancy


def test_defaults_off_and_anchored():
    c = DemographyConfig()
    assert c.enable_orphan_mortality is False          # opt-in ⇒ bit-exact
    # Table 13.1 log-parameters, exponentiated
    assert c.orphan_mult_mother_dead == pytest.approx(math.exp(1.6277), abs=0.01)   # 5.09 "about fivefold"
    assert c.orphan_mult_father_dead == pytest.approx(math.exp(1.1146), abs=0.01)   # 3.05 "about threefold"
    assert c.orphan_mult_divorced == pytest.approx(math.exp(1.0892), abs=0.01)      # 2.97 "threefold"
    assert c.orphan_max_age_years == 9.0                                            # Table 13.1 window: ages 0–9


def test_mother_matters_more_than_father():
    """The book's headline ordering: mother ~5×, father ~3×. Losing the mother is worse."""
    c = DemographyConfig()
    assert c.orphan_mult_mother_dead > c.orphan_mult_father_dead > 1.0


def test_e_mult_matches_table_131_mean_values():
    """The double-count divisor is DERIVED from Table 13.1's own means (mother alive 0.98, father alive
    0.95, divorced 0.14 | both alive), not fitted."""
    c = DemographyConfig()
    p_m_alive, p_f_alive, p_div = 0.98, 0.95, 0.14
    both = p_m_alive * p_f_alive
    e = ((p_m_alive + (1 - p_m_alive) * c.orphan_mult_mother_dead)
         * (p_f_alive + (1 - p_f_alive) * c.orphan_mult_father_dead)
         * ((1 - both) + both * ((1 - p_div) + p_div * c.orphan_mult_divorced)))
    assert c.orphan_e_mult == pytest.approx(e, abs=0.01)


def test_hazard_mult_scales_the_whole_hazard_not_just_a2():
    """Table 13.1 controls for age, so its effect is proportional on the TOTAL age-specific rate —
    unlike a2_mult, which scales only the Makeham term."""
    p = ACHE_FOREST_NATURAL
    h1 = p.hazard(2.0)
    d_plain = p.monthly_death_prob(24.0)
    d_x2 = p.monthly_death_prob(24.0, 1.0, 2.0)
    # doubling the hazard ⇒ the monthly survival prob is squared
    assert (1.0 - d_x2) == pytest.approx((1.0 - d_plain) ** 2, rel=1e-9)
    assert h1 > 0


def test_hazard_mult_defaults_to_bit_exact():
    p = ACHE_FOREST_NATURAL
    assert p.monthly_death_prob(24.0, 1.0, 1.0) == p.monthly_death_prob(24.0)


def test_survivorship_is_not_modulated():
    """Blueprint hazard I-2: a new multiplier must thread through hazard() ONLY — founder sampling, the
    ×12 guard and the life-table test all depend on the unmodulated cumulative forms."""
    p = ACHE_FOREST_NATURAL
    import inspect
    for fn in (p.cumulative_hazard, p.survivorship):
        assert "mult" not in inspect.signature(fn).parameters


def _mean_mult(cfg, p_mother_dead, p_father_dead, p_divorced):
    """Population-mean orphan multiplier under given parental-status frequencies (independence assumed,
    divorce conditional on both parents living — Table 13.1 footnote **)."""
    both_alive = (1 - p_mother_dead) * (1 - p_father_dead)
    e = (((1 - p_mother_dead) + p_mother_dead * cfg.orphan_mult_mother_dead)
         * ((1 - p_father_dead) + p_father_dead * cfg.orphan_mult_father_dead)
         * ((1 - both_alive) + both_alive * ((1 - p_divorced) + p_divorced * cfg.orphan_mult_divorced)))
    return e / cfg.orphan_e_mult if cfg.orphan_normalize else e


def test_mean_hazard_preserved_at_ache_parental_rates():
    """THE double-count test. a1 was fit to OBSERVED Aché mortality, which already contains these deaths
    ("infanticide KEPT"), so at Aché parental-status frequencies the population-MEAN multiplier must be
    1.0 — the mechanism redistributes mortality onto orphans without adding a second helping of it.
    (Computed from the frequencies, NOT from orphan_e_mult/orphan_e_mult — that would be circular.)"""
    c = DemographyConfig()
    assert _mean_mult(c, 0.02, 0.05, 0.14) == pytest.approx(1.0, abs=0.01)
    # ... and e₀ is therefore untouched at those rates
    p = ACHE_FOREST_NATURAL
    e0 = life_expectancy(p)
    scaled = SilerParams(p.a1 * _mean_mult(c, 0.02, 0.05, 0.14), p.b1, p.a2, p.a3, p.b3)
    assert life_expectancy(scaled) == pytest.approx(e0, abs=0.3)
    assert 40.0 < e0 < 46.0                # de-warfared baseline e₀=42.7 (R-15)


def test_mechanism_is_NOT_mean_preserving_off_ache_rates():
    """The normaliser is a FIXED Aché constant, so it only preserves the mean at Aché orphan rates. A
    population with more orphans than the Aché takes a net mortality INCREASE — that is the mechanism
    working (parental death really does kill children), but it means the flag cannot be switched on
    without re-checking eq_pop. R-74 measured the model at ~3.4× the Aché motherless rate ⇒ eq_pop −47%."""
    c = DemographyConfig()
    assert _mean_mult(c, 0.067, 0.113, 0.14) > 1.2      # the model's measured rates ⇒ net hazard rise
    assert _mean_mult(c, 0.00, 0.00, 0.0) < 0.7         # an orphan-free population ⇒ net hazard fall


def test_normalisation_lowers_the_baseline_for_an_intact_family():
    """A child with both parents alive and married must face LESS than the raw observed a1 — that is the
    counterfactual the observed schedule was averaging over."""
    c = DemographyConfig()
    intact = 1.0 / c.orphan_e_mult
    assert intact < 1.0
    assert intact == pytest.approx(0.667, abs=0.02)      # 1/1.499


def test_orphan_penalty_survives_normalisation():
    """Normalisation must not neuter the effect: an orphan still faces a materially raised hazard."""
    c = DemographyConfig()
    assert c.orphan_mult_mother_dead / c.orphan_e_mult > 3.0      # ~3.4×
    assert c.orphan_mult_father_dead / c.orphan_e_mult > 2.0      # ~2.0×


def test_infanticide_flag_is_superseded_and_still_inert():
    """`enable_infanticide` was scoped as birth-spacing/sex-biased infanticide. Table 5.1 shows parental
    infanticide is 5.3% of infant deaths and infancy is near sex-SYMMETRIC (38% M / 41% F) — the sex bias
    is at 4–14 and comes from grave accompaniment. Superseded; still read by no logic."""
    assert DemographyConfig().enable_infanticide is False
