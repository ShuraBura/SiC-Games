"""CTB — THE STANDING DEMOGRAPHY PANEL (R-106, 2026-08-13, supervisor request).

WHY A PANEL. Social dynamics are built on the age-sex structure, so a skewed demography invalidates every
marker above it — and today gave a clean example. `band_med` read 23 against Birdsell's ~25 and looked like a
pass, on a population that was 54% children. That band held about 11 ADULTS, and Hill et al. 2011's anchor is
28.2 ADULTS. The marker that read as passing was failing by a factor of two and a half, because nothing
scored the age structure beside it.

THE THREE GROUPS BUILT HERE, and what each answers:

  A. LIFE-TABLE EXTENSIONS.  e0 is the WRONG headline: it is dominated by infant mortality, which is why the
     cross-forager e0 range is 21-37 while e15 sits near 38 everywhere. Gurven & Kaplan 2007's Aché-forest
     row gives five more quantities that were on file, VERIFIED, and unused while this arc reported e0 alone.
     `test_the_estimator_returns_the_five_published_ache_values` feeds the estimator the published Siler
     coefficients and demands the published life table back. That is the strongest CTB available: the input
     and the expected output are both printed in the source.

  B. VITAL RATES.  A population count says WHERE the model is; the flows say WHY. CBR and CDR computed from
     the run's OWN exposure cannot drift from the life table beside them, which a hand-differenced growth
     rate can and did.

  C. FAMILY STRUCTURE.  `frac_motherless` and `frac_fatherless` were reported separately, so a child that
     lost BOTH was counted once in each and never as itself — and that is the highest-hazard group in the
     R-74 orphan work (child mortality is orphan-CONDITIONED, x5.09 for a lost mother). `frac_unpaired_adult`
     pooled the widowed with the never-married, which are different phenomena: near-universal marriage means
     never-partnered-by-30 should be near zero in foragers, while widowhood is common. Pooling them makes a
     broken pairing mechanism indistinguishable from ordinary mortality.

A DENOMINATOR CAUGHT BY BUILDING THIS. LITERATURE.md records "survival-to-15 = 0.66, survival 15→45 = 0.43".
Fed the published coefficients, this estimator returns l(15) = 0.66 exactly and a CONDITIONAL 15→45 of 0.65 —
and 0.66 x 0.65 = 0.43. So the published 0.43 is survival to 45 FROM BIRTH. Scoring the conditional against
it would have marked a correct schedule wrong by ~50%: the fifth "right number, wrong denominator" in this
project. Both are now returned under separate names and
`test_the_two_survivorships_are_not_interchangeable` pins the distinction.
"""
import math

import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import ACHE_FOREST, DemographyConfig, MONTHS_PER_YEAR
from sic_games.phase1_model import IBI_HIST_MAX, LT_MAX_AGE_YR, TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

# Gurven & Kaplan 2007 Table 2, Aché forest period [VERIFIED, docs/LITERATURE.md]
PUB = dict(e0=37.0, e15=38.5, e45=21.1, surv_to_15=0.66, surv_to_45=0.43, modal_adult_death=71.0)


class _Counters:
    """Only the counters the accessors read. The methods under test are the REAL unbound ones."""

    def __init__(self):
        self.step_count = 0
        for k in ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc",
                  "fert_exposure", "fert_births"):
            setattr(self, k, [0] * LT_MAX_AGE_YR)
        self.ibi_hist = [0] * (IBI_HIST_MAX + 1)
        self.fert_factor_sum = 0.0
        self.fert_factor_n = 0
        self.fert_factor_sat = 0
        self.births_male = 0
        self.births_female = 0
        self.first_birth_age_sum = 0.0
        self.first_birth_n = 0

    lt = TerrainWorld.life_table
    vr = TerrainWorld.vital_rates


def _feed(c, hazard, py_per_age=200000.0):
    for i in range(LT_MAX_AGE_YR):
        c.lt_exposure[i] = int(round(py_per_age * MONTHS_PER_YEAR))
        c.lt_deaths[i] = int(round(py_per_age * hazard(i + 0.5)))
        c.lt_deaths_senesc[i] = c.lt_deaths[i]


# ── A. the life table, against five published numbers ─────────────────────────────────────────────────────

def test_the_estimator_returns_the_five_published_ache_values():
    """THE CENTRAL CTB. Input: the exact Siler coefficients Gurven & Kaplan published. Expected output: the
    life table they published from them. Both are in the paper, so there is nothing to calibrate."""
    c = _Counters()
    _feed(c, ACHE_FOREST.hazard)
    r = c.lt()
    for k, want in PUB.items():
        got = r[k]
        tol = 0.6 if k in ("e0", "e15", "e45") else (0.02 if k.startswith("surv") else 1.5)
        assert abs(got - want) <= tol, f"{k}: estimator {got:.3f} vs published {want} (tol {tol})"


def test_e15_is_the_stable_indicator_and_e0_is_not():
    """The reason e15 was added. Halving the INFANT term moves e0 a long way and e15 barely at all — which
    is why the cross-forager e0 range is 21-37 while e15 sits near 38. Scoring a mortality schedule on e0
    alone confounds child survival with adult survival."""
    lo = ACHE_FOREST.__class__(a1=ACHE_FOREST.a1 * 0.5, b1=ACHE_FOREST.b1, a2=ACHE_FOREST.a2,
                               a3=ACHE_FOREST.a3, b3=ACHE_FOREST.b3)
    base, child = _Counters(), _Counters()
    _feed(base, ACHE_FOREST.hazard)
    _feed(child, lo.hazard)
    b, ch = base.lt(), child.lt()
    assert ch["e0"] - b["e0"] > 1.5, "halving infant mortality must move e0 materially"
    assert abs(ch["e15"] - b["e15"]) < 0.2, "and must barely move e15"


def test_the_two_survivorships_are_not_interchangeable():
    """THE DENOMINATOR GUARD. 0.43 is l(45) FROM BIRTH; the conditional 15->45 is 0.65. If a later edit
    collapses them, a correct schedule scores ~50% wrong against the filed anchor."""
    c = _Counters()
    _feed(c, ACHE_FOREST.hazard)
    r = c.lt()
    assert r["surv_to_45"] == pytest.approx(0.43, abs=0.02)
    assert r["surv_15_to_45_cond"] == pytest.approx(0.65, abs=0.02)
    assert r["surv_to_15"] * r["surv_15_to_45_cond"] == pytest.approx(r["surv_to_45"], rel=1e-6)


def test_modal_adult_death_ignores_the_infant_peak():
    """Taken over ALL ages the mode is age 0 in any forager schedule, and the anchor (71) would look absurd.
    It must be the mode of the ADULT death distribution."""
    c = _Counters()
    _feed(c, ACHE_FOREST.hazard)
    assert c.lt()["modal_adult_death"] == pytest.approx(71.0, abs=1.5)
    dx = [c.lt()["l"][i] - (c.lt()["l"] + [0.0])[i + 1] for i in range(LT_MAX_AGE_YR - 1)]
    assert dx.index(max(dx)) < 5, "the all-ages mode really is in infancy — which is why it is excluded"


def test_survivorship_can_never_go_negative():
    """THE DEFECT THIS BATTERY MISSED FOR A DAY. `q = m/(1 + m/2)` exceeds 1.0 whenever m > 2 deaths per
    person-year, and a probability above 1 drives l(x) NEGATIVE. Found 2026-08-14 on the short test runs,
    which carry almost no exposure: l(15) came back -0.091 and l(25) -0.500, and every quantity built on
    them — e0, e15, surv_to_15 — inherits the sign.

    A real 15,000-step arm never approaches m = 2, so no scored result was affected. But a survivorship that
    can go negative is not a survivorship. Every constructed case in this file fed a plausible hazard, which
    is exactly why the battery passed while the estimator could produce nonsense.
    """
    for hazard in (2.5, 10.0, 100.0):
        c = _Counters()
        for i in range(LT_MAX_AGE_YR):
            c.lt_exposure[i] = 12 * 100                   # 100 person-years
            c.lt_deaths[i] = int(100 * hazard)            # m = hazard, far above 2
            c.lt_deaths_senesc[i] = c.lt_deaths[i]
        r = c.lt()
        assert all(0.0 <= x <= 1.0 for x in r["l"]), f"l(x) left [0,1] at m={hazard}: min {min(r['l'])}"
        assert all(0.0 <= x <= 1.0 for x in r["q"]), f"q left [0,1] at m={hazard}"
        assert r["e0"] >= 0.0 and r["surv_to_15"] >= 0.0
        assert r["e0"] < 2.0, "at 2.5+ deaths per person-year nobody should live long"


def test_the_sex_split_table_also_clamps():
    """Same guard on the other life table. A fix applied to one copy and not the other is how this project
    got two survivorship conventions in the first place."""
    w = _world(n=40)
    w.step()
    for i in range(LT_MAX_AGE_YR):
        w.lt_exposure[i] = 12 * 50
        w.lt_exposure_f[i] = 12 * 25
        w.lt_deaths[i] = 500                              # m = 10/yr
        w.lt_deaths_f[i] = 250
    s = w.life_table_by_sex()
    for k in ("e0_female", "e0_male", "e15_female", "e15_male"):
        v = s[k]
        assert v != v or v >= 0.0, f"{k} went negative: {v}"


def test_mortality_by_age_group_conserves_and_is_readable():
    c = _Counters()
    _feed(c, ACHE_FOREST.hazard)
    r = c.lt()
    assert sum(r["deaths_by_band"].values()) == r["deaths"]
    assert sum(r["exposure_by_band"].values()) == pytest.approx(r["exposure_py"], rel=1e-9)
    for k, m in r["m_by_band"].items():
        lo = int(k.split("_")[0])
        assert m == pytest.approx(r["deaths_by_band"][k] / r["exposure_by_band"][k], rel=1e-9), k
    assert r["m_by_band"]["0_1"] > r["m_by_band"]["5_15"] < r["m_by_band"]["60_plus"], "the J shape must show"


# ── B. vital rates ────────────────────────────────────────────────────────────────────────────────────────

def test_crude_rates_are_per_thousand_person_years():
    """The unit that makes them comparable to published crude rates. A missing 1000 or a missing /12 is the
    single most common defect in this codebase's history."""
    c = _Counters()
    for i in range(20, 40):
        c.lt_exposure[i] = 12 * 1000        # 1000 person-years per age -> 20,000 py total
    c.fert_births[25] = 800                 # 800 births
    c.lt_deaths[30] = 400                   # 400 deaths
    v = c.vr()
    assert v["person_years"] == pytest.approx(20000.0)
    assert v["cbr"] == pytest.approx(40.0)          # 800 / 20000 * 1000
    assert v["cdr"] == pytest.approx(20.0)
    assert v["r_pct_yr"] == pytest.approx(2.0)      # (40 - 20) / 10 = 2 % per year


def test_growth_is_the_difference_of_the_two_rates():
    c = _Counters()
    for i in range(20, 30):
        c.lt_exposure[i] = 12 * 500
    c.fert_births[25] = 150
    c.lt_deaths[25] = 150
    assert c.vr()["r_pct_yr"] == pytest.approx(0.0), "equal births and deaths must give zero growth"


def test_realised_srb_is_reported_as_the_male_fraction():
    c = _Counters()
    c.births_male, c.births_female = 512, 488
    assert c.vr()["srb_male_frac"] == pytest.approx(0.512)


def test_age_at_first_birth_is_in_years():
    c = _Counters()
    c.first_birth_age_sum = 19.5 * MONTHS_PER_YEAR * 40      # 40 women, each at 19.5 yr
    c.first_birth_n = 40
    assert c.vr()["age_first_birth_yr"] == pytest.approx(19.5)


def test_vital_rates_difference_into_a_period():
    c = _Counters()
    for i in range(20, 30):
        c.lt_exposure[i] = 12 * 100
    c.fert_births[25] = 100
    mark = TerrainWorld.raw_demographic_counters(c)
    mark["births_male"] = c.births_male; mark["births_female"] = c.births_female
    mark["first_birth_age_sum"] = c.first_birth_age_sum; mark["first_birth_n"] = c.first_birth_n
    for i in range(20, 30):
        c.lt_exposure[i] += 12 * 100
    c.fert_births[25] += 50
    assert c.vr(since=mark)["cbr"] == pytest.approx(50.0)     # 50 births / 1000 py * 1000
    assert c.vr()["cbr"] == pytest.approx(75.0)               # cumulative 150 / 2000 py * 1000


def test_empty_counters_report_nan_not_zero():
    c = _Counters()
    v = c.vr()
    assert math.isnan(v["cbr"]) and math.isnan(v["srb_male_frac"]) and math.isnan(v["age_first_birth_yr"])


# ── C. family structure, on constructed families ──────────────────────────────────────────────────────────

def _world(n=60, **upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, **upd)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


def test_joint_orphanhood_is_counted_as_itself():
    """CONSTRUCTED FAMILIES with a known answer: 4 children with both parents, 3 with one, 2 with neither.
    The separate motherless/fatherless fractions cannot express the last group at all."""
    w = _world()
    w.step()
    mum, dad = w.agent_list[0], w.agent_list[1]
    mum.alive = dad.alive = True
    kids = []
    for i in range(9):
        c = w.agent_list[2 + i]
        c.age = 5 * MONTHS_PER_YEAR
        c._mother, c._father = mum, dad
        kids.append(c)
    dead_m = w.agent_list[40]; dead_m.alive = False
    dead_f = w.agent_list[41]; dead_f.alive = False
    for c in kids[4:7]:
        c._father = dead_f                     # 3 with one parent alive
    for c in kids[7:9]:
        c._mother, c._father = dead_m, dead_f  # 2 with neither
    w.agent_list = [mum, dad] + kids
    for a in (mum, dad):
        a.age = 40 * MONTHS_PER_YEAR
    f = w.family_structure()
    assert f["n_children"] == 9
    assert f["frac_both_parents_alive"] == pytest.approx(4 / 9)
    assert f["frac_one_parent_alive"] == pytest.approx(3 / 9)
    assert f["frac_double_orphan"] == pytest.approx(2 / 9)


def test_an_unrecorded_parent_is_UNKNOWN_not_dead():
    """THE BUG THIS METHOD SHIPPED WITH FOR AN HOUR, and the case the first CTB missed.

    `_father` is None whenever paternity was never assigned. The first version counted "not alive" for a
    None link, so a child with no recorded father was scored as having a dead one — the smoke run reported
    8.6% double-orphans that were mostly children with no father link at all. `_orphan_status` has always
    done this correctly, and the constructed families in the test above all had explicit links, which is
    exactly why the battery passed while the method was wrong.

    Constructed: 3 children whose mother is alive and whose father was never recorded. None is bereaved.
    """
    w = _world()
    w.step()
    mum = w.agent_list[0]; mum.alive = True; mum.age = 40 * MONTHS_PER_YEAR
    kids = []
    for i in range(3):
        c = w.agent_list[1 + i]
        c.age = 4 * MONTHS_PER_YEAR
        c._mother, c._father = mum, None        # father UNKNOWN, not dead
        kids.append(c)
    w.agent_list = [mum] + kids
    f = w.family_structure()
    assert f["n_children"] == 3
    assert f["frac_double_orphan"] == pytest.approx(0.0), "an unrecorded father is not a dead father"
    assert f["frac_both_parents_alive"] == pytest.approx(1.0)
    assert f["frac_partial_parent_link"] == pytest.approx(1.0), "and the partial coverage must be visible"


def test_a_child_with_no_parent_links_at_all_leaves_the_risk_set():
    """Same convention as the existing frac_motherless/frac_fatherless risk set: a child with NO known
    parent carries no information about bereavement and must not dilute the denominator."""
    w = _world()
    w.step()
    lone = w.agent_list[0]
    lone.age = 4 * MONTHS_PER_YEAR
    lone._mother = lone._father = None
    w.agent_list = [lone]
    assert w.family_structure()["n_children"] == 0


def test_never_partnered_and_widowed_are_different_people():
    """THE DISTINCTION THAT WAS MISSING. `frac_unpaired_adult` pooled these. Constructed: of 4 over-30s, one
    never partnered, two are widowed, one is currently partnered."""
    w = _world()
    w.step()
    a, b, c, d, spouse = w.agent_list[:5]
    for x in (a, b, c, d, spouse):
        x.age = 35 * MONTHS_PER_YEAR
        x._partner = None
        x._wives = set()
        x._ever_partnered = False
    a._ever_partnered = False                                  # never partnered
    b._ever_partnered = True                                   # widowed
    c._ever_partnered = True                                   # widowed
    d._ever_partnered = True; d._partner = spouse              # currently partnered
    spouse._ever_partnered = True; spouse._wives = {d}
    w.agent_list = [a, b, c, d, spouse]
    f = w.family_structure()
    assert f["n_adults_30"] == 5
    assert f["frac_never_partnered_30"] == pytest.approx(1 / 5)
    assert f["frac_widowed_adult"] == pytest.approx(2 / 5)
    assert f["frac_partnered_adult"] == pytest.approx(2 / 5)


def test_never_partnered_is_read_at_thirty_not_at_menarche():
    """Reading it at 15 would score the ordinary pre-marital years as a pairing failure."""
    w = _world()
    w.step()
    young = w.agent_list[0]
    young.age = 18 * MONTHS_PER_YEAR
    young._ever_partnered = False
    young._partner = None; young._wives = set()
    w.agent_list = [young]
    assert w.family_structure()["n_adults_30"] == 0


def test_the_panel_is_readable_from_a_real_run():
    w = _world()
    for _ in range(40):
        w.step()
    lt, vr, fam = w.life_table(), w.vital_rates(), w.family_structure()
    assert lt["e0"] > 0 and not math.isnan(lt["e15"])
    assert vr["person_years"] > 0
    assert 0.0 <= fam["frac_partnered_adult"] <= 1.0 or math.isnan(fam["frac_partnered_adult"])
