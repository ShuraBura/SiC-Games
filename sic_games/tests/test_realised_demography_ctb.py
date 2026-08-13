"""CTB — THE REALISED LIFE TABLE AND FERTILITY SCHEDULE (R-106, 2026-08-12).

THE MEASURED DEFECT THIS ANSWERS. The model is CONFIGURED with a Siler schedule (ACHE_FOREST, e0 = 36.6 yr)
and a fertility schedule (expected IBI 30 + 1/0.12 = 38.3 months against Hill & Hurtado's verified 37.6;
ceiling TFR 9 against their 8.031). Both sit on their anchors. Yet the campaign realises `frac_child` 0.60
against a verified [0.287, 0.454] and `dependency_ratio` 1.81 against [0.598, 0.899], and the deficit is
MONOTONE IN AGE: the 0-5 band runs 1.17x its predicted share and the 60+ band 0.59x.

That cannot be a fertility effect. Reproducing the observed age structure from the model's own Siler
schedule would need TFR ~14.3, and the model's arithmetic CEILING is 9 — the reproductive span divided by
the minimum inter-birth interval. Running the calibrated schedule at stationarity instead gives frac_child
0.307, dead centre of the anchor. So the configured schedules are right and the REALISED ones are not, and
nothing in the model ever measured a realised one. Derived from the age structure, the run's realised e0 is
about 19 yr: roughly half the calibration, i.e. the world holds its Malthusian equilibrium by killing people
at nearly twice the anchored rate.

WHAT THESE TESTS GUARD. Two separable failures, tested separately, because conflating them is how the
food-consistency diagnostic shipped with ten green tests that all checked the formula and none the meaning:

  (1) THE ESTIMATOR. Feed `life_table` counters whose answer is known analytically and demand that answer.
      The load-bearing one is `test_the_estimator_recovers_the_ache_forest_schedule`: fed the very schedule
      the model is configured with, it must return 36.6 yr. An instrument that cannot recover a known
      schedule cannot be trusted to report an unknown one — and this whole finding is a claim about a
      number this instrument produces.
  (2) THE WIRING. Run the REAL model and demand conservation: every death counted by the pre-existing
      per-step counters must appear in the life table, and total exposure must equal the population summed
      over steps. An estimator can be perfect while the counters behind it are fed from the wrong place.

`test_the_observers_never_feed_back` is the guard that keeps these PURE. The moment a dynamic reads
`fert_factor_mean` or `lt_deaths`, every prior run stops being bit-exact and the diagnostic becomes part of
the model it is supposed to measure.
"""
import math
import re
from pathlib import Path

import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import ACHE_FOREST, DemographyConfig, MONTHS_PER_YEAR
from sic_games.phase1_model import IBI_HIST_MAX, LT_MAX_AGE_YR, TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


# ── a bare carrier for the estimator, so the arithmetic is tested without a world ─────────────────────────

class _Counters:
    """Just the counters `life_table`/`fertility_schedule` read. The methods under test are the REAL ones,
    borrowed unbound from TerrainWorld — a reimplementation here would test this file, not the model."""

    def __init__(self):
        self.step_count = 0
        self.lt_exposure = [0] * LT_MAX_AGE_YR
        self.lt_deaths = [0] * LT_MAX_AGE_YR
        self.lt_deaths_starv = [0] * LT_MAX_AGE_YR
        self.lt_deaths_senesc = [0] * LT_MAX_AGE_YR
        self.fert_exposure = [0] * LT_MAX_AGE_YR
        self.fert_births = [0] * LT_MAX_AGE_YR
        self.ibi_hist = [0] * (IBI_HIST_MAX + 1)
        self.fert_factor_sum = 0.0
        self.fert_factor_n = 0
        self.fert_factor_sat = 0

    lt = TerrainWorld.life_table
    fs = TerrainWorld.fertility_schedule
    raw = TerrainWorld.raw_demographic_counters


def _feed_hazard(c, hazard, py_per_age=20000.0):
    """Expose `py_per_age` person-years at every age and kill the exact expected number at each — a
    constructed cohort whose life table is known in closed form from `hazard`."""
    for i in range(LT_MAX_AGE_YR):
        c.lt_exposure[i] = int(round(py_per_age * MONTHS_PER_YEAR))
        m = hazard(i + 0.5)
        c.lt_deaths[i] = int(round(py_per_age * m))
        c.lt_deaths_senesc[i] = c.lt_deaths[i]


def _analytic_e0(hazard):
    """e0 for a continuous hazard, by the same actuarial convention the estimator uses (a(x) = 1/2)."""
    l, e0 = 1.0, 0.0
    for i in range(LT_MAX_AGE_YR):
        m = hazard(i + 0.5)
        q = m / (1.0 + 0.5 * m)
        e0 += 0.5 * (l + l * (1.0 - q))
        l *= (1.0 - q)
    return e0


# ── (1) the estimator, against answers known in advance ───────────────────────────────────────────────────

def test_no_deaths_means_everyone_reaches_the_table_edge():
    c = _Counters()
    for i in range(LT_MAX_AGE_YR):
        c.lt_exposure[i] = 12000
    lt = c.lt()
    assert lt["e0"] == pytest.approx(float(LT_MAX_AGE_YR), abs=1e-9)
    assert all(x == pytest.approx(1.0) for x in lt["l"])


def test_a_constant_hazard_gives_the_closed_form_expectancy():
    """The one case with an exact answer: constant m ⇒ e0 = Σ l, and l is geometric in q = m/(1+m/2)."""
    m = 0.05
    c = _Counters()
    _feed_hazard(c, lambda a: m)
    q = m / (1.0 + 0.5 * m)
    expect = sum(0.5 * ((1 - q) ** i + (1 - q) ** (i + 1)) for i in range(LT_MAX_AGE_YR))
    assert c.lt()["e0"] == pytest.approx(expect, rel=1e-3)


def test_the_estimator_recovers_the_ache_forest_schedule():
    """THE POSITIVE CONTROL, and the reason this file exists. Fed the schedule the model is CONFIGURED with,
    the instrument must return that schedule's life expectancy. The R-106 claim is that a run realises ~19 yr
    against this 36.6 — a claim only worth making if the instrument returns 36.6 when 36.6 is true."""
    c = _Counters()
    _feed_hazard(c, ACHE_FOREST.hazard)
    lt = c.lt()
    assert lt["e0"] == pytest.approx(_analytic_e0(ACHE_FOREST.hazard), rel=0.01)
    assert 35.0 < lt["e0"] < 38.5, f"ACHE_FOREST e0 should be ~36.6, estimator said {lt['e0']:.2f}"
    for age in (1, 5, 15, 45, 60):
        assert lt["m"][age] == pytest.approx(ACHE_FOREST.hazard(age + 0.5), rel=0.02)


def test_the_estimator_is_load_bearing_on_the_schedule_it_is_fed():
    """CTB corollary (2026-08-06): a diagnostic that returns the right answer for the right world must also
    MOVE when the world moves. Double the Gompertz term and life expectancy must fall materially — an
    estimator that returned 36.6 for every input would pass the test above and be worthless."""
    steep = ACHE_FOREST.__class__(a1=ACHE_FOREST.a1, b1=ACHE_FOREST.b1, a2=ACHE_FOREST.a2,
                                  a3=ACHE_FOREST.a3 * 8.0, b3=ACHE_FOREST.b3)
    base, pert = _Counters(), _Counters()
    _feed_hazard(base, ACHE_FOREST.hazard)
    _feed_hazard(pert, steep.hazard)
    assert pert.lt()["e0"] < base.lt()["e0"] - 3.0, "an 8x Gompertz term barely moved the estimate"


def test_a_period_table_shows_the_period_not_the_run():
    """`since` must difference the counters. Without it the early transient is averaged into the steady
    state — the same mistake as reporting a cumulative TFR and calling it a period rate."""
    c = _Counters()
    _feed_hazard(c, lambda a: 0.30)                 # an early, lethal regime
    mark = c.raw()
    for i in range(LT_MAX_AGE_YR):                  # then a gentle one
        c.lt_exposure[i] += 12000
        c.lt_deaths[i] += 100                       # m = 0.10 over the period
        c.lt_deaths_senesc[i] += 100
    period = c.lt(since=mark)
    assert period["m"][10] == pytest.approx(0.10, rel=1e-6)
    assert c.lt()["m"][10] > period["m"][10], "the cumulative table must still show the blend"


def test_starvation_share_is_reported_and_sums():
    c = _Counters()
    for i in range(LT_MAX_AGE_YR):
        c.lt_exposure[i] = 12000
        c.lt_deaths[i] = 10
        c.lt_deaths_starv[i] = 3
        c.lt_deaths_senesc[i] = 7
    lt = c.lt()
    assert lt["starv_share"] == pytest.approx(0.3)
    assert lt["deaths_starv"] + lt["deaths_senesc"] == lt["deaths"]


# ── (1b) the fertility estimator ──────────────────────────────────────────────────────────────────────────

def test_tfr_is_the_sum_of_single_year_asfr():
    """TFR must be the synthetic-cohort measure, because that is what Hill & Hurtado Table 8.1 states
    (8.031). Summing a rate per woman-year over single years of age is the whole definition."""
    c = _Counters()
    for age in range(15, 42):
        c.fert_exposure[age] = 12000            # 1000 woman-years at each age
        c.fert_births[age] = 300                # ASFR = 0.30
    fs = c.fs()
    assert fs["asfr"][20] == pytest.approx(0.30, rel=1e-9)
    assert fs["tfr"] == pytest.approx(0.30 * 27, rel=1e-9)


def test_the_month_to_year_conversion_is_present():
    """The unit error this project has made before: exposure is in person-MONTHS and ASFR is per person-YEAR.
    Omitting the /12 would divide the rate by twelve and make every fertility verdict silently wrong."""
    c = _Counters()
    c.fert_exposure[20] = 12                    # exactly one woman-year
    c.fert_births[20] = 1
    assert c.fs()["asfr"][20] == pytest.approx(1.0)


def test_realised_ibi_median_and_overflow_bin():
    c = _Counters()
    for months in (30, 31, 40, 41, 200):        # 200 must fold into the 120+ overflow, not be dropped
        c.ibi_hist[months if months < IBI_HIST_MAX else IBI_HIST_MAX] += 1
    fs = c.fs()
    assert fs["ibi_n"] == 5
    assert fs["ibi_median"] == pytest.approx(40.0)


def test_the_saturation_detector_separates_a_live_brake_from_a_dead_one():
    """POSITIVE AND NEGATIVE CONTROL for the instrument that will decide whether `enable_intake_fertility`
    actually bites. `enable_energetic_fertility` was found dead because its reserve re-saturated at the cap
    for ~99% of agents; a detector that could not tell those two states apart would repeat that failure."""
    dead = _Counters()
    dead.fert_factor_sum, dead.fert_factor_n, dead.fert_factor_sat = 1000.0, 1000, 1000
    assert dead.fs()["factor_saturated"] == pytest.approx(1.0)
    assert dead.fs()["factor_mean"] == pytest.approx(1.0)

    live = _Counters()
    live.fert_factor_sum, live.fert_factor_n, live.fert_factor_sat = 400.0, 1000, 50
    assert live.fs()["factor_saturated"] == pytest.approx(0.05)
    assert live.fs()["factor_mean"] == pytest.approx(0.40)


def test_empty_counters_do_not_crash_or_invent_a_rate():
    """A diagnostic must never crash a run, and must not report 0.0 as though it were measured."""
    c = _Counters()
    assert c.lt()["e0"] == pytest.approx(float(LT_MAX_AGE_YR))
    fs = c.fs()
    assert fs["tfr"] == 0.0 and fs["ibi_n"] == 0
    assert math.isnan(fs["ibi_median"]) and math.isnan(fs["factor_mean"])


# ── (2) the wiring, on the REAL model ─────────────────────────────────────────────────────────────────────

def _world(n=120, **upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, **upd)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


def test_every_death_the_old_counters_saw_reaches_the_life_table():
    """CONSERVATION. The per-step counters predate this work and are trusted; the life table is new. If the
    two disagree, the new instrument is reading from the wrong place — which is exactly how a diagnostic
    ends up measuring something other than what its name says."""
    w = _world()
    seen = 0
    for _ in range(60):
        w.step()
        seen += w.deaths_starv_this_step + w.deaths_senesc_this_step
    assert seen > 0, "no deaths in 60 steps — this test would be vacuous"
    assert sum(w.lt_deaths) == seen
    assert sum(w.lt_deaths_starv) + sum(w.lt_deaths_senesc) == seen


def test_exposure_equals_the_population_summed_over_steps():
    """The ASFR/hazard denominator. An exposure that counted the wrong set would rescale every rate.

    The exact identity, and it is worth stating because getting it wrong is how a denominator drifts: the
    mortality loop is entered by everyone alive at that point in the step, so it tallies N. By the time the
    census is taken after `step()`, that step's deaths have gone and its newborns have arrived — and a
    newborn is created AFTER the loop, so it earns no exposure in the month it is born. Hence
        Σ exposure − Σ post-step census = Σ deaths − Σ births.
    """
    w = _world()
    census = births = 0
    for _ in range(40):
        w.step()
        census += len(w.agent_list)
        births += w.births_this_step
    assert births > 0 and sum(w.lt_deaths) > 0, "vacuous without both flows"
    assert sum(w.lt_exposure) - census == sum(w.lt_deaths) - births


def test_female_exposure_counts_only_women():
    w = _world()
    for _ in range(20):
        w.step()
    assert 0 < sum(w.fert_exposure) < sum(w.lt_exposure)


def test_exposure_lands_in_the_agents_own_age_bin():
    """The off-by-one that would silently shift every hazard by a year."""
    w = _world(n=40)
    for a in w.agent_list:
        a.age = 30 * MONTHS_PER_YEAR + 3        # 30 yr 3 mo; ages to 30 yr 4 mo during the step
    w.step()
    assert w.lt_exposure[30] > 0
    assert sum(w.lt_exposure[:30]) == 0 and sum(w.lt_exposure[31:]) == 0


def test_the_realised_table_is_readable_from_a_real_run():
    w = _world()
    for _ in range(60):
        w.step()
    lt, fs = w.life_table(), w.fertility_schedule()
    assert 0.0 < lt["e0"] <= float(LT_MAX_AGE_YR)
    assert lt["exposure_py"] > 0.0
    assert fs["tfr"] >= 0.0 and fs["woman_years"] > 0.0


def test_a_period_table_from_a_real_run_excludes_the_transient():
    w = _world()
    for _ in range(30):
        w.step()
    mark = w.raw_demographic_counters()
    for _ in range(30):
        w.step()
    period = w.life_table(since=mark)
    assert period["deaths"] <= sum(w.lt_deaths)
    assert period["exposure_py"] < w.life_table()["exposure_py"]


def test_the_counter_snapshot_is_a_copy_not_a_view():
    """A `since` mark holding live references would keep accumulating, and every period rate computed from
    it would silently be the cumulative one."""
    w = _world()
    w.step()
    mark = w.raw_demographic_counters()
    before = list(mark["lt_exposure"])
    for _ in range(10):
        w.step()
    assert mark["lt_exposure"] == before


def test_reading_a_diagnostic_does_not_mutate_it():
    w = _world()
    for _ in range(20):
        w.step()
    first = (w.life_table()["e0"], w.fertility_schedule()["tfr"], list(w.lt_exposure))
    second = (w.life_table()["e0"], w.fertility_schedule()["tfr"], list(w.lt_exposure))
    assert first == second


# ── (3) the purity guard ──────────────────────────────────────────────────────────────────────────────────

_OBSERVER_NAMES = ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc",
                   "fert_exposure", "fert_births", "ibi_hist",
                   "fert_factor_sum", "fert_factor_n", "fert_factor_sat")


def test_the_observers_never_feed_back():
    """These counters must be WRITE-ONLY outside their own accessors. If a dynamic ever reads one, the
    diagnostic becomes part of the model it measures, every earlier run stops being bit-exact, and the
    comparison against the configured schedule stops meaning anything. Comments are stripped first — an
    earlier version of this guard matched its own explanatory prose and passed for the wrong reason."""
    path = Path(__file__).resolve().parents[1] / "src" / "sic_games" / "phase1_model.py"
    assert path.exists(), f"cannot locate the model source at {path}"
    lines = [re.sub(r"#.*$", "", ln).strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    # Everything from the first accessor onward is allowed to READ them; that is what they are for.
    cut = next(i for i, ln in enumerate(lines) if ln.startswith("def life_table("))
    # The only forms that WRITE. Anything else mentioning a counter is a read, and a read is the defect.
    allowed = [re.compile(rf"^self\.{{n}}\s*(:[^=]+)?=\s"),          # declaration / plain assignment
               re.compile(rf"^self\.{{n}}\s*(\+|-)=\s"),             # scalar accumulate
               re.compile(rf"^self\.{{n}}\[[^\]]+\]\s*(\+|-)=\s")]   # indexed accumulate
    for i, ln in enumerate(lines[:cut]):
        for name in _OBSERVER_NAMES:
            if not re.search(rf"\bself\.{name}\b", ln):
                continue
            # A line may carry two increments separated by ';' — check each statement on its own.
            for stmt in (s.strip() for s in ln.split(";")):
                if not re.search(rf"\bself\.{name}\b", stmt):
                    continue
                pats = [re.compile(p.pattern.replace("{n}", name)) for p in allowed]
                assert any(p.match(stmt) for p in pats), (
                    f"line {i + 1}: `self.{name}` is READ inside the model dynamics:\n    {stmt}\n"
                    "These counters are pure observers; a read makes them load-bearing.")


def test_the_harness_contract_for_the_final_arrays_holds():
    """run_campaign writes the age-specific arrays into the trajectory meta at the end of a run, by reading
    exactly these keys off `raw_demographic_counters()`. The per-row fields carry only the SCALARS, and the
    scalars cannot say WHICH AGES carry the excess hazard — which is the question an age-structure failure
    turns on. A renamed key here would silently produce runs with no arrays, and nobody would notice until an
    attribution was attempted months later. This pins the contract without paying for a campaign subprocess."""
    w = _world(n=40)
    w.step()
    c = w.raw_demographic_counters()
    for k in ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc",
              "fert_births", "fert_exposure", "ibi_hist",
              "fert_factor_sum", "fert_factor_n", "fert_factor_sat"):
        assert k in c, f"run_campaign reads `{k}` off raw_demographic_counters(); it is missing"
    assert len(c["lt_exposure"]) == LT_MAX_AGE_YR
    assert len(c["ibi_hist"]) == IBI_HIST_MAX + 1
    assert sum(c["lt_deaths"]) == sum(c["lt_deaths_starv"]) + sum(c["lt_deaths_senesc"])


def test_no_flag_gates_the_observers():
    """Deliberate: a flag would let a run silently produce no life table, and the first thing anyone would
    do with an empty table is assume the run was fine. The counters cost two list increments per agent-step
    and consume no RNG, so there is nothing to ablate."""
    d = DemographyConfig()
    assert not any(f.startswith("enable_") and ("life_table" in f or "fert_factor" in f)
                   for f in DemographyConfig.model_fields)
    assert d is not None
