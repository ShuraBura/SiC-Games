"""Tests for the Step-1 demographic core (`sic_games.demography`).

Covers: the Aché Siler coefficients reproduce the published life table; the ×12 units guard
(monthly-stepped survivorship == closed-form annual l(x)); a2 modulation; fertility eligibility.
"""
import math

import pytest

from sic_games.demography import (
    ACHE_FOREST,
    ACHE_FOREST_FEMALE,
    ACHE_FOREST_MALE,
    DemographyConfig,
    SilerParams,
    density_mult,
    is_fertile,
    life_expectancy,
    modal_adult_death,
    risk_mult,
    synergy_mult,
)


# --- the published Aché anchors (Gurven & Kaplan 2007, Table 2, forest period) ---
def test_ache_coefficients_reproduce_published_life_table():
    p = ACHE_FOREST
    assert life_expectancy(p, 0.0) == pytest.approx(37.0, abs=1.0)        # e0 = 37
    assert life_expectancy(p, 15.0) == pytest.approx(38.5, abs=1.5)       # e15 = 38.5 REMAINING yr
    assert life_expectancy(p, 45.0) == pytest.approx(21.1, abs=1.5)       # e45 = 21.1
    assert p.survivorship(15.0) == pytest.approx(0.66, abs=0.02)          # l(15) = 0.66
    assert p.survivorship(45.0) == pytest.approx(0.43, abs=0.03)          # l(45) = 0.43 (from birth)
    assert modal_adult_death(p) == pytest.approx(71.0, abs=2.0)           # mode = 71


def test_e15_is_remaining_years_not_total():
    """Guard against the v1 blueprint error: e15 is REMAINING years (~38), not total age (~70)."""
    assert life_expectancy(ACHE_FOREST, 15.0) < 45.0


def test_mrdt_matches_paper():
    # MRDT = ln2 / b3 ≈ 6.7 yr (Gurven & Kaplan: Aché adult mortality doubles in ~7 yr)
    assert math.log(2) / ACHE_FOREST.b3 == pytest.approx(6.7, abs=0.5)


# --- the ×12 units guard: the classic factor-of-12 bug (blueprint M-4) ---
def test_monthly_stepped_survivorship_matches_closed_form():
    """Stepping the monthly death probability month-by-month must reproduce the closed-form
    annual l(x). If the hazard were applied per-month WITHOUT the /12 conversion, simulated
    survivorship would collapse ~12× too fast and this test would fail."""
    p = ACHE_FOREST
    surv = 1.0
    age_m = 0
    checkpoints = {y * 12: y for y in (10, 25, 45, 70)}
    seen = {}
    while age_m <= 70 * 12:
        if age_m in checkpoints:
            seen[checkpoints[age_m]] = surv
        surv *= (1.0 - p.monthly_death_prob(age_m))
        age_m += 1
    for yr, sim in seen.items():
        closed = p.survivorship(float(yr))
        assert sim == pytest.approx(closed, abs=0.01), f"age {yr}: sim {sim:.4f} vs l(x) {closed:.4f}"


def test_monthly_death_prob_is_a_probability_and_rises_with_age():
    p = ACHE_FOREST
    for age_m in (0, 240, 600, 1000):
        q = p.monthly_death_prob(age_m)
        assert 0.0 <= q < 1.0
    # senescence: a 90-yr-old faces a higher monthly hazard than a 30-yr-old
    assert p.monthly_death_prob(90 * 12) > p.monthly_death_prob(30 * 12)


# --- a2 is the modulated (environmental) term ---
def test_a2_mult_raises_baseline_hazard_only():
    p = ACHE_FOREST
    base = p.hazard(30.0, a2_mult=1.0)
    raised = p.hazard(30.0, a2_mult=2.0)
    assert raised > base
    # the increment equals exactly one extra a2 (only the baseline term scales)
    assert raised - base == pytest.approx(p.a2, abs=1e-9)
    # higher baseline → lower monthly survival
    assert p.monthly_death_prob(30 * 12, a2_mult=2.0) > p.monthly_death_prob(30 * 12, a2_mult=1.0)


# --- fertility eligibility (window + IBI refractory) ---
def test_is_fertile_window_and_refractory():
    cfg = DemographyConfig()  # menarche 180, menopause 504, refractory 30
    assert not is_fertile(150, 99, cfg)            # pre-menarche
    assert not is_fertile(520, 99, cfg)            # post-menopause
    assert not is_fertile(300, 10, cfg)            # in window but still in lactational refractory
    assert is_fertile(300, 30, cfg)                # eligible: in window, past refractory
    assert is_fertile(cfg.menarche_months, cfg.ibi_refractory_months, cfg)  # boundaries inclusive


def test_config_siler_roundtrip_and_flags_default_off():
    cfg = DemographyConfig()
    p = cfg.siler()
    assert (p.a1, p.b1, p.a2, p.a3, p.b3) == (0.157, 0.721, 0.013, 4.80e-5, 0.103)
    assert not any([cfg.enable_terrain_risk, cfg.enable_density_disease,
                    cfg.enable_terrain_pathogen, cfg.enable_nutrition_synergy,
                    cfg.enable_infanticide])


# --- M-3 sex split (Hill & Hurtado 1996 forest-period ratios) ---
def test_sex_split_ratios_preserve_average():
    f, m, both = ACHE_FOREST_FEMALE, ACHE_FOREST_MALE, ACHE_FOREST
    # childhood (a1): male = 0.71 × female ; adult (a2, a3): male = 1.47 × female
    assert m.a1 == pytest.approx(0.71 * f.a1, rel=1e-9)          # childhood: a1 scaled (female higher)
    assert m.a3 == pytest.approx(1.47 * f.a3, rel=1e-9)          # adulthood: a3 (Gompertz) scaled (male higher)
    assert f.a2 == m.a2 == both.a2                                # Makeham baseline SHARED
    # the sex-average reproduces the validated both-sexes anchor
    assert 0.5 * (f.a1 + m.a1) == pytest.approx(both.a1, rel=1e-9)
    assert 0.5 * (f.a3 + m.a3) == pytest.approx(both.a3, rel=1e-9)
    assert (f.b1, f.b3) == (m.b1, m.b3) == (both.b1, both.b3)   # shape params common


def test_sex_split_ordering_matches_monograph():
    # forest Aché (Hill & Hurtado): HIGHER female child mortality, HIGHER male adult mortality
    assert ACHE_FOREST_FEMALE.hazard(5.0) > ACHE_FOREST_MALE.hazard(5.0)     # childhood
    assert ACHE_FOREST_MALE.hazard(50.0) > ACHE_FOREST_FEMALE.hazard(50.0)   # adulthood


def test_config_returns_sex_specific_siler():
    cfg = DemographyConfig()
    assert cfg.siler() == ACHE_FOREST                 # default = both-sexes
    assert cfg.siler("female") == ACHE_FOREST_FEMALE
    assert cfg.siler("male") == ACHE_FOREST_MALE


# --- Step-2 a2 modulators ---
def test_a2_modulators():
    # terrain risk: 1 at mean, capped, rises on high-risk cells
    assert risk_mult(0.2, 0.2, 3.0) == pytest.approx(1.0)
    assert risk_mult(1.0, 0.2, 3.0) == 3.0                    # capped
    assert risk_mult(0.4, 0.2, 3.0) == pytest.approx(2.0)
    # density-disease: 1 at ρ=0, +δ/2 at ρ=ρ_half, saturating below 1+δ
    assert density_mult(0.0, 1.0, 0.2) == pytest.approx(1.0)
    assert density_mult(0.2, 1.0, 0.2) == pytest.approx(1.5)
    assert 1.0 < density_mult(0.1, 1.0, 0.2) < density_mult(0.5, 1.0, 0.2) < 2.0
    # nutrition synergy: 1 at full reserve, μ_max at floor, monotone in between
    assert synergy_mult(100_000, 20_000, 100_000, 2.5) == pytest.approx(1.0)
    assert synergy_mult(20_000, 20_000, 100_000, 2.5) == pytest.approx(2.5)
    assert synergy_mult(60_000, 20_000, 100_000, 2.5) == pytest.approx(1.75)
