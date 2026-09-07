"""R-103 — the STRATIFICATION-INEQUALITY GATE: 'stratified' must mean UNEQUAL wealth, not merely high wealth.

WHY. `society_from_character` classified a band stratified on packed + high MEAN surplus (surplus_frac >= 0.7).
But stratification is unequal CONTROL of surplus — Testart's chain is storage -> wealth DIFFERENTIALS -> heritable
rank, and the level-only test skipped the differentials step. Diagnosed 2026-07-22 in the R-102 biome sweep: the
flat-tropical arm read 45% stratified while carrying the LOWEST cred-Gini of any arm (0.29) — the label ran
OPPOSITE to inequality (a society that is 45% 'stratified' but the most equal is a contradiction). Confirmed
independent of the growth mechanism: the 45% survived ablating sedentism-fertility.

THE GATE. When `gini_min` is supplied (config `enable_stratification_inequality_gate` on), a would-be stratified
band must also show within-band cred concentration >= gini_min, else it is affluent-egalitarian -> complex_forager.
Passing `gini_min=None` (the default) is bit-exact with the level-only classifier — this is what protects every
result validated before the gate existed (verified: edited gate-off == pre-edit across all 56 campaign metrics).

THRESHOLD. BHM 2009 Table 2 alpha-weighted Gini: forager 0.25, horticultural 0.27, agricultural/pastoral
~0.45-0.57 -> the egalitarian<->stratified boundary is ~0.35-0.40 at the POPULATION scale. Within-band Gini runs
LOWER, so the operative value is calibrated on the validated baseline, not taken from BHM directly.
"""
import pytest

from sic_games.demography import DemographyConfig, society_from_character as S


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_stratification_inequality_gate is False
    assert c.stratification_gini_min == 0.40


# ── bit-exactness: gini_min None must reproduce the level-only classifier exactly ─────────────────────
def test_gini_min_none_is_bit_exact():
    """The whole safety guarantee. With no gate, every verdict is the pre-R-103 verdict."""
    cases = [(0.2, 0.8), (0.2, 0.3), (0.05, 0.9), (0.5, 0.75), (0.09, 0.7)]
    for d, s in cases:
        assert S(d, s) == S(d, s, wealth_gini=0.01, gini_min=None), (d, s)
        assert S(d, s) == S(d, s, wealth_gini=0.99, gini_min=None), (d, s)


def test_level_only_still_stratifies_the_packed_affluent():
    assert S(0.2, 0.8) == "stratified_chiefdom"           # packed (>=0.091) + surplus>=0.7


# ── the gate itself ───────────────────────────────────────────────────────────────────────────────────
def test_gate_demotes_affluent_but_EQUAL_band():
    """THE BUG IT FIXES. Packed and affluent, but members are equal (low Gini) => NOT stratified."""
    assert S(0.2, 0.8, wealth_gini=0.10, gini_min=0.30) == "complex_forager"


def test_gate_keeps_affluent_and_UNEQUAL_band():
    """The gate must not over-correct: a genuinely unequal packed-affluent band stays stratified."""
    assert S(0.2, 0.8, wealth_gini=0.50, gini_min=0.30) == "stratified_chiefdom"


def test_gate_boundary_is_inclusive():
    """gini exactly at the floor qualifies (>=), just above/below as expected."""
    assert S(0.2, 0.8, wealth_gini=0.30, gini_min=0.30) == "stratified_chiefdom"
    assert S(0.2, 0.8, wealth_gini=0.2999, gini_min=0.30) == "complex_forager"


def test_missing_gini_under_active_gate_is_conservative():
    """If the gate is on but no inequality could be measured (wealth_gini None), do NOT stratify — absence of
    evidence of inequality is not evidence of stratification."""
    assert S(0.2, 0.8, wealth_gini=None, gini_min=0.30) == "complex_forager"


# ── the gate only ever touches the STRATIFIED verdict ────────────────────────────────────────────────
def test_gate_never_blocks_egalitarian():
    """Below packing and low surplus is egalitarian regardless of inequality — the gate sits only on the
    stratified branch, so a high Gini cannot manufacture complexity from an unpacked band."""
    assert S(0.01, 0.2, wealth_gini=0.9, gini_min=0.30) == "egalitarian_forager"


def test_gate_does_not_touch_complex():
    """A packed-but-not-affluent band is complex with or without the gate (never reaches the stratified branch)."""
    assert S(0.2, 0.5) == "complex_forager"
    assert S(0.2, 0.5, wealth_gini=0.9, gini_min=0.30) == "complex_forager"


def test_high_inequality_cannot_upgrade_a_poor_band():
    """Inequality is necessary, not sufficient: a poor unequal band is not stratified — surplus is still required."""
    assert S(0.2, 0.4, wealth_gini=0.95, gini_min=0.30) == "complex_forager"
