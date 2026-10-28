"""The four mortality-structure fixes from the external audit (R-106 Addendum 118), each a held flag, default OFF.

  enable_lifespan_from_siler    the demographic death check uses siler_lifespan_cap_months (100 yr), not max_age (75 yr)
  enable_condition_full_scale   body condition scaled by the best attainable post-burn fill (a fed agent reads ~1)
  enable_density_common_window  a mobile agent's disease density over the same window as a village's
  enable_eta_once               with η-weighted claims, η is not applied a second time at the harvest
  enable_orphan_norm_by_age     the orphan multiplier is normalised per year of age, not pooled over 0–9 (Add.120)

These tests pin: all default OFF; each is LIVE; the lifespan, condition and orphan fixes do what they claim on a
constructed case.
"""
import os
import sys

import pytest

from sic_games.demography import DemographyConfig

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

WORLD = dict(n=900, patch=18, terr="coastal", clim="temperate")
FLAGS = ["enable_lifespan_from_siler", "enable_condition_full_scale", "enable_density_common_window", "enable_eta_once",
         "enable_orphan_norm_by_age"]
# The battery world builds from emergent_village_demog() and does NOT apply the run file, so the mechanisms each fix
# acts through are OFF there. Both arms get them ON (as in canon); only the fix flag differs.
PREREQ = {"enable_lifespan_from_siler": {},
          "enable_condition_full_scale": {"enable_condition": True, "enable_nutrition_synergy": True},
          "enable_density_common_window": {"enable_village_density_disease": True, "enable_density_reference": True},
          "enable_eta_once": {"enable_eta_weighted_shares": True, "enable_need_weighted_shares": True},
          "enable_orphan_norm_by_age": {"enable_orphan_mortality": True}}


def test_all_default_off():
    c = DemographyConfig()
    for f in FLAGS:
        assert getattr(c, f) is False, f
    assert c.siler_lifespan_cap_months == 1200


@pytest.mark.slow
@pytest.mark.parametrize("flag", FLAGS)
def test_each_fix_changes_the_world(flag):
    import battery1_liveness as B1
    off, _, _ = B1.signature(dict(PREREQ[flag]), steps=200, **WORLD)
    on, _, _ = B1.signature(dict(PREREQ[flag], **{flag: True}), steps=200, **WORLD)
    assert on != off, f"{flag} ON is bit-identical to OFF in this world"


def _old_agents_survival(update, k=20, steps=3):
    """Constructed case: set k adults to age 899 months with a full reserve, step, count survivors among them."""
    import battery1_liveness as B1
    w = B1._build(update, **WORLD)
    for _ in range(30):
        w.step()
    adults = [a for a in w.agent_list if a.age >= 240][:k]
    assert len(adults) == k
    for a in adults:
        a.age = 899
        a.wealth = w._reserve_full * a.reserve_scale()
    ids = {id(a) for a in adults}
    for _ in range(steps):
        w.step()
    return sum(1 for a in w.agent_list if id(a) in ids)


@pytest.mark.slow
def test_lifespan_cap_kills_at_75_off_and_not_on():
    assert _old_agents_survival({}) == 0, "the 900-month cap no longer kills — re-measure F-05"
    assert _old_agents_survival({"enable_lifespan_from_siler": True}) >= 12, \
        "with the Siler lifespan most 75-year-olds should survive three months (monthly hazard ~1%)"


@pytest.mark.slow
def test_condition_reads_high_for_the_fed_only_with_the_fix():
    import battery1_liveness as B1
    res = {}
    for on in (False, True):
        w = B1._build(dict(PREREQ["enable_condition_full_scale"], enable_condition_full_scale=on), **WORLD)
        for _ in range(60):
            w.step()
        fed = [a._condition for a in w.agent_list if getattr(a, "_fed_reserve", 0) >= 0.99 * w._reserve_full * a.reserve_scale()]
        assert fed, "no fed agents to read"
        res[on] = sum(fed) / len(fed)
    assert res[False] < 0.4, f"OFF: fed agents' condition {res[False]:.3f} — the trough ceiling (F-05 review) changed"
    assert res[True] > 0.8, f"ON: fed agents' condition {res[True]:.3f} should approach 1"


@pytest.mark.slow
def test_orphan_norm_by_age_gives_infants_the_schedule_hazard():
    """Add.120: the pooled divisor gives infants with known parents a mean multiplier below 1 (they are rarely
    orphaned, older children often are); the per-age divisor makes it exactly 1 at every year of age."""
    import battery1_liveness as B1
    res = {}
    for on in (False, True):
        w = B1._build(dict(PREREQ["enable_orphan_norm_by_age"], enable_orphan_norm_by_age=on), **WORLD)
        for _ in range(250):
            w.step()
        inf = [a for a in w.agent_list if a.age < 12
               and (getattr(a, "_mother", None) is not None or getattr(a, "_father", None) is not None)]
        assert inf, "no infants with known parents to read"
        w._orphan_e_cache = None      # the divisor is cached at its first use in a step; re-read it on THIS population
        res[on] = sum(w._orphan_mult(a) for a in inf) / len(inf)
    assert res[False] < 0.95, f"OFF: infants' mean multiplier {res[False]:.3f} — the pooled discount (Add.120) changed"
    assert abs(res[True] - 1.0) < 1e-9, f"ON: infants' mean multiplier {res[True]:.6f} should be exactly 1"
