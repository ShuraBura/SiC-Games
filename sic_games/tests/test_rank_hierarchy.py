"""R-99 — RANK unlocks hierarchy, GRADED by measured stratification (supersedes R-98's one-rung promotion).

WHY GRADED, and why the obvious monotonic form is WRONG. R-98 promoted a whole village one rung on the society
ladder once a threshold share of heads were ranked. Measured at campaign scale that gave **70.6% stratified
against R-64's validated 9-16%** — the promotion was too cheap, because rank is common and a rung is a large
jump (leader weight 0.0 -> 0.5, unlocking growth AND halving scalar stress at once). See DEAD_ENDS DE-22.

But the naive replacement — hierarchy rising with the ranked SHARE — is wrong in a way worth stating: with
binary ascription, a village where EVERY lineage is ranked has no ranked/commoner distinction at all. It is
flat. Monotonic-in-share would hand that village MAXIMUM hierarchy, reproducing exactly the degeneracy R-89
fixed and that R-87's own note names: "nobility universal, i.e. meaningless".

So the measure must be ZERO AT BOTH ENDS and peak where a ranked few stand over a commoner many. Rather than
invent a peaked distribution and a location parameter for it, this reuses the privilege EFFECT SIZE already
computed for resentment (R-94): the noble/commoner cred gap in units of the community's own spread. It is zero
when there is no distinction in either direction, scale-free, already capped, already validated — and it means
the SAME measured quantity drives both consequences of privilege, resentment from below and organisational
capacity above, rather than two independently tuned claims.

NO NEW CONSTANT. The normaliser is `resent_effect_threshold` (Cohen's "large", 0.8), already in the config.
A community whose nobles stand a large effect above its commoners earns the full stratified weight.
"""
import pytest

from sic_games.demography import DemographyConfig, LEADER_SOCIETY_WEIGHT, society_from_character


class _A:
    """Minimal stand-in carrying only what `_privilege_effect` reads."""
    def __init__(self, cred, lineage):
        self.cred = cred
        self._lineage = lineage


class _W:
    """The helper under test, bound to a controllable ascribed set."""
    def __init__(self, ascribed):
        self._lineage_ascribed = set(ascribed)
    from sic_games.phase1_model import TerrainWorld as _T
    _privilege_effect = _T._privilege_effect


def _eff(nobles, commoners):
    """Effect size for a community with these two cred lists."""
    ms = [_A(c, "N") for c in nobles] + [_A(c, "C") for c in commoners]
    rk = {a: a._lineage for a in ms}
    return _W({"N"})._privilege_effect(ms, rk)


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_rank_hierarchy is False


def test_the_gap_it_fixes_is_real():
    """The classifier's inputs do not include rank, so a sparse poor village is 'egalitarian' however ranked it
    is — and a leader counts for nothing there."""
    assert society_from_character(density_per_km2=0.01, surplus_frac=0.0) == "egalitarian_forager"
    assert LEADER_SOCIETY_WEIGHT["egalitarian_forager"] == 0.0


def test_zero_when_nobody_is_ranked():
    assert _eff(nobles=[], commoners=[1.0, 1.2, 0.9]) == 0.0


def test_zero_when_EVERYONE_is_ranked():
    """THE KEY PROPERTY, and the reason a monotonic-in-share form was rejected. Universal rank is FLAT — no
    ranked/commoner distinction exists — so it must score zero, not maximum. This is the R-89 degeneracy, and
    scoring it zero closes the back door rather than leaving it open via a population-wide fallback."""
    assert _eff(nobles=[3.0, 3.2, 2.8], commoners=[]) == 0.0


def test_rises_with_a_real_gap():
    small = _eff([1.1, 1.15, 1.05], [1.0, 1.05, 0.95])
    large = _eff([3.0, 3.2, 2.8], [1.0, 1.1, 0.9])
    assert 0.0 < small < large


def test_scale_free():
    """Same social structure at a different cred scale must score the same — the property that makes it safe to
    threshold (charter D15)."""
    base = _eff([3.0, 3.2, 2.8], [1.0, 1.1, 0.9])
    for k in (0.1, 10.0, 100.0):
        assert _eff([v * k for v in (3.0, 3.2, 2.8)], [v * k for v in (1.0, 1.1, 0.9)]) == pytest.approx(base)


def test_nobles_worse_off_scores_zero():
    """Privilege floors at zero: a disadvantaged elite confers no organisational capacity."""
    assert _eff([1.0, 1.0], [5.0, 5.0]) == 0.0


def test_uniform_community_scores_zero():
    """sd == 0 means nothing is discernible, whatever the means say. Guards the divide-by-zero."""
    assert _eff([1.0, 1.0], [1.0, 1.0]) == 0.0


def test_a_large_gap_earns_the_full_weight_at_the_cohen_normaliser():
    """The normaliser is `resent_effect_threshold` (Cohen 'large'), already in the config — so a large gap maps
    to weight 1.0, the stratified-equivalent, and NO new constant is introduced."""
    ref = DemographyConfig().resent_effect_threshold
    assert ref == 0.8
    w = min(1.0, _eff([3.0, 3.2, 2.8], [1.0, 1.1, 0.9]) / ref)
    assert w == pytest.approx(1.0)


def test_a_marginal_gap_earns_only_a_little():
    """And a slight difference must NOT buy hierarchy, or the fix repeats R-98's too-cheap promotion.

    MARGINAL MEANS SMALL RELATIVE TO THE SPREAD, not small in absolute terms — and the first cut of this test
    got that wrong. A 4% gap inside a community whose own spread is 6% is Cohen's d ~ 0.63, i.e. medium-to-large,
    and it scored 0.79. That is the measure behaving CORRECTLY: in a very uniform community a consistently
    better-off family is conspicuous, which is Boehm's point exactly — it is the visible distinction that draws
    attention, not the absolute magnitude. A genuinely marginal case needs a small gap against a WIDE spread."""
    ref = DemographyConfig().resent_effect_threshold
    w = min(1.0, _eff([1.05, 2.0, 0.3], [1.00, 1.95, 0.25]) / ref)
    assert 0.0 < w < 0.5
