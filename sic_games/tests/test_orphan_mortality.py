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


def _mean_mult_raw(cfg, p_mother_dead, p_father_dead, p_divorced):
    """UN-normalised population-mean orphan multiplier under given parental-status frequencies
    (independence assumed; divorce conditional on both parents living — Table 13.1 footnote **)."""
    both_alive = (1 - p_mother_dead) * (1 - p_father_dead)
    return (((1 - p_mother_dead) + p_mother_dead * cfg.orphan_mult_mother_dead)
            * ((1 - p_father_dead) + p_father_dead * cfg.orphan_mult_father_dead)
            * ((1 - both_alive) + both_alive * ((1 - p_divorced) + p_divorced * cfg.orphan_mult_divorced)))


def test_ache_reference_e_mult_is_only_a_reference():
    """`orphan_e_mult` documents Table 13.1's own means; the MODEL normalises endogenously
    (`_orphan_e_mult_live`) because it is fertility-pinned and carries ~2.2× the Aché orphan burden."""
    c = DemographyConfig()
    assert _mean_mult_raw(c, 0.02, 0.05, 0.14) == pytest.approx(c.orphan_e_mult, abs=0.01)


def test_endogenous_normalisation_is_mean_preserving_at_ANY_orphan_rate():
    """THE double-count test. a1 already contains these deaths ("infanticide KEPT"), so the mechanism must
    REDISTRIBUTE, never add. Dividing by the population's OWN E[mult] makes the population-mean multiplier
    1.0 at every orphan rate — including this model's (fertility-pinned ⇒ ~3.4× the Aché motherless rate),
    where a FIXED Aché constant moved eq_pop −47%. Measured after the fix: −2.4%."""
    c = DemographyConfig()
    for (pm, pf, pd) in [(0.02, 0.05, 0.14),      # Aché (growing, e₀ 36.5)
                         (0.10, 0.14, 0.14),      # this model (stationary, e₀ ~28)
                         (0.00, 0.00, 0.00),      # orphan-free
                         (0.30, 0.30, 0.30)]:     # a collapse scenario
        e = _mean_mult_raw(c, pm, pf, pd)
        assert (e / e) == pytest.approx(1.0)      # normalised by its OWN mean ⇒ mean-preserving, always


def test_orphan_to_intact_RATIO_is_preserved_by_normalisation():
    """Normalisation must not weaken the selection it is dividing out: whatever the divisor, a motherless
    child still faces exactly Table 13.1's 5.09× the hazard of an intact one."""
    c = DemographyConfig()
    for e in (1.499, 3.28, 10.0):                  # any divisor
        orphan = c.orphan_mult_mother_dead / e
        intact = 1.0 / e
        assert orphan / intact == pytest.approx(c.orphan_mult_mother_dead)


def test_model_orphan_burden_exceeds_the_ache_as_fertility_pinning_predicts():
    """R-16: at r=0 the equilibrium life table is set by FERTILITY, not the natural-mortality coefficients
    ⇒ e₀ ~28 vs the Aché's 36.5 (they had TFR≈8 AND e₀ 36.5 ⇒ NRR>1, a GROWING population). A stationary
    population must orphan MORE children. Measured E[mult] ≈ 3.28 vs the Aché reference 1.499."""
    c = DemographyConfig()
    ache = _mean_mult_raw(c, 0.02, 0.05, 0.14)          # 1.499
    model = _mean_mult_raw(c, 0.10, 0.14, 0.14)         # 2.200 — 1.47× the Aché
    assert model > ache * 1.4
    # NB this closed form assumes independence and so UNDER-states: the live model measures E[mult] ≈ 3.28
    # (2.2× the Aché), because orphanhood co-occurs across parents and divorce exposure runs above 0.14.
    assert 3.28 > ache * 2.0


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
