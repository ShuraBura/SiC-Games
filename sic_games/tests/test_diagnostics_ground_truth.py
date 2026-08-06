"""CONSTRUCTED-TRUTH tests: build a population whose answer is known, then check the diagnostic returns it.

CLAUDE.md's first rule, and the reason it exists. On 2026-08-04 the interpretation of a single marker
(`connubium_med`) was revised three times in one day, and every revision was caused by the INSTRUMENT rather
than by the model:

  1. read off the docstring — "distinct unpaired adults in each pool"
  2. inferred a unit mismatch against the anchor, and computed a conversion from population composition
  3. found the truth: `_connubium_sizes` is appended from TWO places with TWO different quantities, and the
     class comment describes only one of them

Careful reasoning about an unvalidated instrument produced three confident, incompatible answers. A world with
a KNOWN answer settles it in one assertion.

So: agents are placed BY HAND — known ages, known sexes, known pairings, known cells — and each diagnostic is
asserted against the construction, element by element. No simulation, no plausibility judgement. If a
diagnostic disagrees with a population that was built to a specification, the diagnostic is wrong.
"""
import pytest

from sic_games.phase1_model import MONTHS_PER_YEAR, TerrainWorld


class _Agent:
    """A hand-built agent carrying only what the demographic diagnostics read."""

    def __init__(self, age_yr, sex, pos=(0, 0), partner=None, wives=(), mother=None, father=None):
        self.age = int(age_yr * MONTHS_PER_YEAR)
        self.sex = sex
        self.pos = pos
        self._partner = partner
        self._wives = set(wives)
        self._mother = mother
        self._father = father
        self.alive = True
        self.material = 0.0
        self.aggrandizer = 0.0
        self.wealth = 0.0
        self.cred = 1.0
        self.prowess = 1.0


def _markers(pop):
    """Run the real diagnostic against a hand-built population, with no world stepping."""
    return TerrainWorld._demog_markers(TerrainWorld, pop)


# ── the age pyramid ──────────────────────────────────────────────────────────────────────────────────

def test_pyramid_returns_exactly_the_ages_that_were_placed():
    """TEN agents, one per class in a known pattern. The expected shares are arithmetic, not a judgement."""
    pop = ([_Agent(2, "female"), _Agent(4, "male")]                       # 2 in 0-5
           + [_Agent(7, "female"), _Agent(14, "male"), _Agent(5, "female")]   # 3 in 5-15
           + [_Agent(15, "male"), _Agent(29, "female")]                   # 2 in 15-30
           + [_Agent(30, "male")]                                         # 1 in 30-45
           + [_Agent(59, "female")]                                       # 1 in 45-60
           + [_Agent(60, "male")])                                        # 1 in 60+
    m = _markers(pop)
    assert m["n"] == 10
    assert m["age_0_5"] == pytest.approx(0.2)
    assert m["age_5_15"] == pytest.approx(0.3)
    assert m["age_15_30"] == pytest.approx(0.2)
    assert m["age_30_45"] == pytest.approx(0.1)
    assert m["age_45_60"] == pytest.approx(0.1)
    assert m["age_60_plus"] == pytest.approx(0.1)
    # the class boundaries are half-open [lo, hi): 15 is an adult, 14 a child, 60 an elder
    assert m["frac_child"] == pytest.approx(0.5)
    assert m["frac_elder"] == pytest.approx(0.1)


def test_pyramid_base_ratio_is_the_ratio_it_claims():
    """base = under-15, middle = 15-45. Built 6 : 3 ⇒ exactly 2.0, which must read 'expansive'."""
    pop = ([_Agent(3, "male") for _ in range(3)] + [_Agent(10, "female") for _ in range(3)]
           + [_Agent(20, "male") for _ in range(2)] + [_Agent(35, "female")])
    m = _markers(pop)
    assert m["pyramid_base_ratio"] == pytest.approx(6 / 3)
    assert m["growth_regime"] == "expansive"


def test_a_constricted_pyramid_is_labelled_constrictive():
    """The mirror: 1 child to 8 in the reproductive middle ⇒ 0.125, well below the 0.8 cut."""
    pop = [_Agent(5, "female")] + [_Agent(25, "male") for _ in range(4)] \
        + [_Agent(40, "female") for _ in range(4)]
    m = _markers(pop)
    assert m["pyramid_base_ratio"] == pytest.approx(1 / 8)
    assert m["growth_regime"] == "constrictive"


# ── mating suitability: the numbers that were wrong for three weeks ──────────────────────────────────

def test_phi_counts_exactly_the_unpaired_adults_that_were_placed():
    """φ = unpaired adults / WHOLE population. Built: 20 agents, of which 4 unpaired adults ⇒ 0.20.

    This is the quantity `LITERATURE.md` assumes is ≈0.1 when deriving `mate_search_min_eligible ≈ 15` from
    White's ~150-person MVP. Nothing had ever measured it against a known answer."""
    f1, f2 = _Agent(25, "female"), _Agent(30, "female")
    m1, m2 = _Agent(28, "male", wives=[f1]), _Agent(33, "male", wives=[f2])
    f1._partner, f2._partner = m1, m2
    pop = ([f1, f2, m1, m2]                                     # 4 PAIRED adults
           + [_Agent(22, "female"), _Agent(24, "male"),         # 4 UNPAIRED adults
              _Agent(40, "male"), _Agent(50, "female")]
           + [_Agent(5, "male") for _ in range(12)])            # 12 children — adults only, so excluded
    assert len(pop) == 20
    m = _markers(pop)
    assert m["frac_unpaired_adult"] == pytest.approx(4 / 20)
    # adult males: m1, m2 (paired) + 2 unpaired ⇒ 2/4 unpaired
    assert m["frac_unpaired_adult_m"] == pytest.approx(0.5)


def test_operational_sex_ratio_is_seeking_males_over_receptive_females():
    """Built 3 unpaired adult males to 2 unpaired adult females ⇒ exactly 1.5."""
    pop = ([_Agent(25, "male") for _ in range(3)] + [_Agent(25, "female") for _ in range(2)]
           + [_Agent(3, "male")])
    m = _markers(pop)
    assert m["operational_sex_ratio"] == pytest.approx(1.5)
    assert m["adult_sex_ratio"] == pytest.approx(3 / 2)


def test_operational_sex_ratio_is_nan_not_zero_when_no_female_is_seeking():
    """A missing denominator must be `nan`, never a fake 0 — a 0 here would read as "no male competition"
    when the truth is "the question does not apply". This is the state the live model is in: measured
    `operational_sex_ratio = nan` because every adult female is paired."""
    f = _Agent(25, "female")
    male = _Agent(26, "male", wives=[f])
    f._partner = male
    m = _markers([f, male, _Agent(30, "male")])
    assert m["operational_sex_ratio"] != m["operational_sex_ratio"], "expected nan, got a number"


def test_adult_sex_ratio_is_adult_only_unlike_the_whole_population_ratio():
    """The distinction that made `sex_ratio_m_f` unusable for mating questions: built with 2 adult males,
    2 adult females (ratio 1.0) but 6 male children, so the whole-population ratio is 8:2 = 4.0."""
    pop = ([_Agent(25, "male"), _Agent(30, "male"), _Agent(25, "female"), _Agent(30, "female")]
           + [_Agent(4, "male") for _ in range(6)])
    m = _markers(pop)
    assert m["adult_sex_ratio"] == pytest.approx(1.0)
    assert m["sex_ratio_m_f"] == pytest.approx(8 / 2)


# ── the coarse markers the pyramid supplements ───────────────────────────────────────────────────────

def test_dependency_ratio_is_dependents_over_working_age():
    """Built 3 children + 2 elders over 5 working-age ⇒ exactly 1.0."""
    pop = ([_Agent(5, "male") for _ in range(3)] + [_Agent(70, "female") for _ in range(2)]
           + [_Agent(30, "male") for _ in range(5)])
    m = _markers(pop)
    assert m["dependency_ratio"] == pytest.approx(1.0)
    assert m["median_age_yr"] == pytest.approx(30.0)


def test_polygyny_markers_count_wives_not_marriages():
    """Built one man with 3 wives and one with 1 ⇒ mean 2.0 among married men, half of them polygynous."""
    wives = [_Agent(25, "female") for _ in range(4)]
    big = _Agent(40, "male", wives=wives[:3])
    small = _Agent(40, "male", wives=wives[3:])
    for w in wives[:3]:
        w._partner = big
    wives[3]._partner = small
    m = _markers(wives + [big, small, _Agent(45, "male")])
    assert m["mean_wives_married_m"] == pytest.approx(2.0)
    assert m["frac_polygynous_m"] == pytest.approx(0.5)
    assert m["frac_paired_adult_f"] == pytest.approx(1.0)
