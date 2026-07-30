"""Fertility must respond to sustained energy BALANCE, because the stored reserve carries no signal.

THE DEFECT (measured 2026-07-30). `enable_energetic_fertility` scales births by the maternal RESERVE level,
which is inert by construction. Burn is ~68% of the floor-to-full span per step, so an agent either
re-saturates at the cap or dies within a step — there is no persistent intermediate state. Measured across a
5x density range: post-harvest reserve 0.996 of full, post-burn trough 0.318, each with spread ~0.002 and
ZERO density response, so the factor returns ~0.995 always. Consequences, all measured:

  * births barely move with crowding (CBR 53.8 -> 52.0 across 5x density) while deaths do all the work
    (CDR 48.5 -> 77.0, starvation 46% -> 61% of deaths);
  * a stationary population then has e0 = 1/CDR ~ 20.7 yr, median age 13, motherless 8-11%;
  * no Malthusian feedback: a positive control at three resource gradients (per-capita elasticity -0.195 /
    -0.387 / -1.062) produced NO oscillation at any of them, and deaths out-swung births in all three.

THE FIX: read a slow EMA of intake over requirement. Intake is the live signal the reserve level cannot be
(p10 0.93 to p90 4.26 of requirement), and it is the biologically right one — Ellison's energetics has
fecundity tracking energy FLUX, not stored reserve. Thresholds are anchored, not tuned: 0 at maintenance
(no surplus to gestate or lactate), full at maintenance + the lactation increment (~+500 kcal/d on ~2500,
FAO/IOM ⇒ ~1.2x).

DEFAULT OFF and bit-exact when off, per the mechanism charter.
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


def test_defaults_off_and_thresholds_anchored():
    c = DemographyConfig()
    assert c.enable_intake_fertility is False, "must be opt-in"
    assert c.intake_fert_lo == 1.00, "the floor is MAINTENANCE — intake=burn leaves no reproductive surplus"
    assert c.intake_fert_hi == 1.20, "the ceiling is maintenance + the lactation increment (FAO/IOM)"
    assert 0.0 < c.intake_ema_alpha <= 1.0


def test_ema_half_life_is_about_fourteen_months():
    """Slow enough that one bad month cannot stop births, fast enough to track a multi-year squeeze."""
    import math
    a = DemographyConfig().intake_ema_alpha
    hl = math.log(2) / -math.log(1 - a)
    assert 10.0 <= hl <= 24.0, f"half-life {hl:.1f} steps is outside the intended ~1-2 yr band"


@pytest.mark.slow
def test_off_is_bit_exact():
    """The charter's adoption gate: with the flag off the world must be unchanged."""
    import battery1_liveness as B1
    base, _, _ = B1.signature({}, steps=120, **WORLD)
    off, _, _ = B1.signature(dict(enable_intake_fertility=False), steps=120, **WORLD)
    assert base == off, "explicitly disabling the flag changed the world — the branch is not inert when off"


@pytest.mark.slow
def test_on_changes_the_world():
    """Liveness: if switching it on is bit-identical, the mechanism is on and doing nothing."""
    import battery1_liveness as B1
    off, _, _ = B1.signature({}, steps=120, **WORLD)
    on, _, _ = B1.signature(dict(enable_intake_fertility=True), steps=120, **WORLD)
    assert on != off, "enabling intake-fertility is bit-identical — the new branch is dead"


@pytest.mark.slow
def test_the_ema_actually_varies_unlike_the_reserve():
    """The whole point. The reserve-based inputs sit at spread ~0.002; this one must genuinely discriminate,
    otherwise we have swapped one dead input for another."""
    import statistics

    import battery1_liveness as B1
    w = B1._build(dict(enable_intake_fertility=True), **WORLD)
    for _ in range(300):
        w.step()
        if not w.agent_list:
            break
    cfg = w._demog
    ema = [a._intake_ema for a in w.agent_list if a.age >= cfg.menarche_months]
    assert len(ema) > 20, "too few adults to judge"
    assert statistics.pstdev(ema) > 0.05, (
        f"intake EMA spread {statistics.pstdev(ema):.4f} — as flat as the reserve it replaced, so fertility "
        f"still cannot discriminate hungry from well-fed agents")


@pytest.mark.slow
def test_juveniles_do_not_accumulate_a_penalty():
    """A child's GATHERED intake understates what it EATS, because juveniles are provisioned. The EMA must
    therefore stay at its neutral start until menarche, or girls would reach fertility pre-penalised."""
    import battery1_liveness as B1
    w = B1._build(dict(enable_intake_fertility=True), **WORLD)
    for _ in range(60):
        w.step()
        if not w.agent_list:
            break
    cfg = w._demog
    kids = [a._intake_ema for a in w.agent_list if a.age < cfg.menarche_months]
    assert kids, "no juveniles"
    assert all(abs(v - cfg.intake_fert_hi) < 1e-12 for v in kids), (
        "a juvenile's intake EMA drifted from neutral — it must only accumulate from menarche")
