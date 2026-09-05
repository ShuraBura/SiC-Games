"""CTB for AGE-GRADED NUTRITION SYNERGY (R-106, 2026-09-05).

THE DEFECT. `mu_max = 2.5` is Pelletier 1994 CHILD malnutrition-mortality data, applied at full strength to
every age. Adults are far more robust (community-dwelling >50 HR ~1.14-1.29). The e0 breakdown (Addendum 64)
showed the 15-45 band at 2.6x the schedule with the synergy amplifying it ~2x — an over-amplification of adults.

THE FIX. `enable_synergy_age_grade`: an agent past menarche (15 yr) uses `synergy_mu_max_adult` (~1.3); children
keep the full `mu_max`.

LOAD-BEARING is `test_MODEL_adult_synergy_attenuated_child_full`: at the SAME (hungry) reserve, the adult's a2
disease multiplier drops to ~synergy_mu_max_adult while the child's stays at ~mu_max, with the flag on; both
equal mu_max with the flag off.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery",
          ROOT / "sic_games" / "outputs" / "phase1_social_evolution"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off():
    assert DemographyConfig().enable_synergy_age_grade is False


def _world(age_grade):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    # isolate the nutrition-synergy term (reserve path, not the condition EMA)
    cfg.update(enable_nutrition_synergy=True, enable_condition=False, enable_synergy_age_grade=age_grade,
               enable_terrain_risk=False, enable_density_disease=False, enable_terrain_pathogen=False)
    return B1._build(cfg, n=50, patch=40, terr="coastal", clim="temperate", seed=0)


def _starve(a, w):
    """Put the agent at its reserve floor so the synergy is at full strength (frac = 0)."""
    a._fed_reserve = a.reserve_floor * a.reserve_scale()


def _syn(age_grade, age_months):
    w = _world(age_grade)
    a = w.agent_list[0]
    a.age = age_months
    _starve(a, w)
    return w._a2_mult(a, {a.pos: 1})   # only the synergy term is live, so this == the synergy multiplier


def test_MODEL_adult_synergy_attenuated_child_full():
    """LOAD-BEARING. With age-grade ON: a hungry ADULT's synergy ~= synergy_mu_max_adult, a hungry CHILD's ~=
    mu_max. With age-grade OFF: both ~= mu_max."""
    cfg = DemographyConfig()
    mu, mu_ad = cfg.mu_max, cfg.synergy_mu_max_adult
    child_age = cfg.menarche_months - 12      # 14 yr (juvenile)
    adult_age = cfg.menarche_months + 240     # 35 yr (an adult in the 15-45 band)

    # ON: child full, adult attenuated
    assert _syn(True, child_age) == pytest.approx(mu, rel=0.02), "child must keep the full Pelletier synergy"
    assert _syn(True, adult_age) == pytest.approx(mu_ad, rel=0.02), "adult synergy must attenuate to the adult cap"
    assert mu_ad < mu, "the adult cap must be below the child cap for this test to mean anything"

    # OFF: both full (bit-exact with the single-mu form)
    assert _syn(False, adult_age) == pytest.approx(mu, rel=0.02), "flag off ⇒ adult uses mu_max ⇒ bit-exact"
