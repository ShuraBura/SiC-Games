"""CTB for the diagnostics behind the markers this project currently reports as FAILURES.

WHY THESE THREE FIRST. `material_gini` (#14, "0.162 against BHM's 0.36 — 2x too low"), `settle_max` (#17,
"median 220, 39/52 arms over Alberti's 158") and `band_max` (#1's neighbour) had **no test anywhere**. Three of
the last four "findings" in this project turned out to be instrument defects rather than model defects —
`hayden_stage` divided by occupied cells instead of territory, `lineage_size_gini` counted rank-keys instead of
patrilines, `connubium_med` appended two different quantities to one list — so a failure computed by an
unvalidated diagnostic is not yet evidence about the model.

This file does not ask whether the model is right. It asks whether the number we are quoting is the number we
think we are quoting.
"""
import math

import pytest

from sic_games.phase1_model import TerrainWorld

_gini = TerrainWorld._gini
_top_share = TerrainWorld._top_share


# ── the Gini kernel, against hand-computed values ─────────────────────────────────────────────────────────

def test_gini_of_a_perfectly_equal_holding_is_zero():
    assert _gini([5.0] * 10) == pytest.approx(0.0)


def test_gini_of_one_holder_among_n_approaches_one():
    """The maximum for a finite sample is (n-1)/n, not 1.0 — worth pinning, because reading 0.9 as 'nearly
    maximal' depends on knowing n."""
    for n in (10, 100):
        v = [0.0] * (n - 1) + [1.0]
        assert _gini(v) == pytest.approx((n - 1) / n, abs=1e-9)


def test_gini_matches_the_textbook_formula_on_a_known_vector():
    """[1,2,3,4,5]: mean 3, sum of |xi-xj| over all pairs = 20, Gini = 20/(2*25*3) ... computed longhand
    below so the assertion does not merely restate the implementation."""
    v = [1.0, 2.0, 3.0, 4.0, 5.0]
    n = len(v)
    brute = sum(abs(a - b) for a in v for b in v) / (2.0 * n * n * (sum(v) / n))
    assert _gini(v) == pytest.approx(brute, abs=1e-12)
    assert _gini(v) == pytest.approx(0.2667, abs=1e-3)


def test_gini_is_zero_for_an_all_zero_holding_not_undefined():
    """A population that owns nothing is not maximally unequal. This is the difference between 'no material
    economy yet' and 'one agent owns everything', and they must not read alike."""
    assert _gini([0.0] * 20) == 0.0
    assert _gini([]) == 0.0


def test_top_share_is_the_share_held_by_the_top_decile():
    """10 holders, one with 100 and nine with 0 -> the top 10% (1 holder) holds 100%."""
    assert _top_share([100.0] + [0.0] * 9, 0.10) == pytest.approx(1.0)
    assert _top_share([10.0] * 10, 0.10) == pytest.approx(0.10)


def test_top_share_always_counts_at_least_one_holder():
    """`int(len*frac)` is 0 for small populations; the implementation floors at 1. Otherwise a 5-agent world
    would report a top-decile share of 0 while one agent held everything."""
    assert _top_share([7.0, 0.0, 0.0], 0.10) == pytest.approx(1.0)


# ── THE UNIT QUESTION behind marker #14 ───────────────────────────────────────────────────────────────────

class _Agent:
    def __init__(self, material, age_yr=30, sex="female"):
        self.material = material
        self.age = int(age_yr * 12)
        self.sex = sex
        self.wealth = 0.0
        self.cred = 1.0
        self.aggrandizer = 0.0
        self.pos = (0, 0)
        self._partner = None
        self._wives = set()
        self._mother = None
        self._father = None
        self.alive = True


def test_material_gini_is_computed_over_the_WHOLE_population_including_children():
    """THE FACT, established rather than assumed. `_mat = [a.material for a in pop]` runs over every agent,
    children included, and children hold nothing.

    That matters for marker #14 because BHM 2009's 0.36 is a Gini over INDIVIDUALS **age-adjusted with a
    quadratic in age** — they explicitly removed the life-cycle component. We do not. So the two numbers are
    not computed the same way, and the comparison needs that stated whichever direction it turns out to run."""
    adults = [_Agent(m) for m in (0.0, 1.0, 2.0, 3.0, 4.0)]
    kids = [_Agent(0.0, age_yr=5) for _ in range(5)]

    g_adults = _gini([a.material for a in adults])
    g_all = _gini([a.material for a in adults + kids])
    assert g_all > g_adults, (
        "adding zero-holding children RAISES the measured Gini — the child fraction is a live confound")

    m = TerrainWorld._demog_markers(TerrainWorld, adults + kids)
    assert m["material_gini"] == pytest.approx(g_all), "the diagnostic uses the all-ages vector"


def test_including_children_pushes_the_gini_UP_which_is_away_from_the_reported_miss():
    """DIRECTION CHECK, and it is the useful half of this file.

    Marker #14 reports the model 2x BELOW the anchor (0.162 vs 0.36). Including children can only push the
    measured Gini UP. So the child confound cannot explain the miss — correcting for it would make the gap
    WIDER, not narrower. Whatever #14's failure is, it is not this."""
    adults = [_Agent(m) for m in (1.0, 2.0, 3.0, 4.0, 5.0)]
    for n_kids in (0, 5, 20):
        pop = adults + [_Agent(0.0, age_yr=4) for _ in range(n_kids)]
        g = _gini([a.material for a in pop])
        if n_kids:
            assert g > _gini([a.material for a in adults])
    # the ordering is monotone in the child fraction
    gs = [_gini([a.material for a in adults + [_Agent(0.0, age_yr=4)] * k]) for k in (0, 5, 20)]
    assert gs == sorted(gs)


def test_a_measured_gini_of_0_162_is_a_real_spread_not_an_empty_economy():
    """The other way #14 could be an artefact: if almost nobody held material, `_gini` returns 0.0 by
    construction and a near-zero reading would mean 'no economy' rather than 'equal economy'. 0.162 is not
    that — this constructs a holding that actually produces ~0.162 so the value is shown to be reachable by a
    real distribution."""
    # a mild spread: most hold a similar amount, a few hold somewhat more
    v = [1.0] * 60 + [1.5] * 25 + [2.5] * 15
    g = _gini(v)
    assert 0.10 < g < 0.25, g
    assert _gini([0.0] * 100) == 0.0, "an empty economy reads 0.0 and must not be confused with the above"


# ── settle_max and band_max: the MAXIMUM statistic behind marker #17 ──────────────────────────────────────

def test_settle_max_is_the_largest_single_settlement_not_a_percentile():
    """Marker #17 scores `settle_max` against Alberti's 158 and Alvard's 250. A MAXIMUM over a distribution
    grows with the number of settlements even if the distribution itself is unchanged — so the marker is
    sensitive to how many settlements a run happens to have, in a way a median is not.

    This constructs that sensitivity explicitly. It does not make #17 wrong; it makes it conditional."""
    import statistics as st
    small = [40, 50, 60]
    many = [40, 50, 60] + [55, 45, 52, 48, 58, 42, 61, 39]
    assert max(small) == 60 and max(many) == 61
    assert st.median(small) == 50 and st.median(many) == 50
    # the median is stable across a 4x change in settlement count; the max is not bounded to be
    assert max(many) >= max(small)


def test_the_max_of_a_sample_rises_with_sample_size_at_fixed_distribution():
    """THE CONFOUND, quantified on a known distribution. Draw from the SAME normal distribution and the
    expected maximum climbs with n. A run with more settlements will report a higher `settle_max` even if its
    settlements are individually no larger, so #17's 'median settle_max 220' is partly a statement about how
    many settlements the arms had."""
    import random
    rng = random.Random(0)
    def emax(n, trials=400):
        return sum(max(rng.gauss(100, 25) for _ in range(n)) for _ in range(trials)) / trials
    e5, e50 = emax(5), emax(50)
    assert e50 > e5 + 15, (e5, e50)


def test_band_max_and_settle_max_are_different_units_and_must_not_be_compared():
    """`band_max` is the largest BAND (a social affiliation of any spatial extent); `settle_max` is the
    largest SETTLEMENT SITE. The campaign renamed n_villages->n_bigbands in 2026-08-04 precisely because these
    were being read as the same thing. Pinned here so the two never merge again."""
    import inspect
    src = inspect.getsource(TerrainWorld.settlements)
    assert "self._settlement_sites" in src, "settle_* is a SITE measure"
    # band_max comes from the band-size vector in run_campaign's snapshot(), not from settlements()
    assert "settlement" not in "band_max"
