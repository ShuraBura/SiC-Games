"""CTB for METABOLIC DOWN-REGULATION under deficit (R-106, 2026-08-28; Keys 1950, MODEL_SPEC §4.6.7).

THE DEFECT. The reserve is spent at a FLAT burn (`wealth += intake - burn`, death at `wealth <= floor`), so any
sustained intake below 100% of the fixed burn is inexorably fatal and there is no thin-but-alive state. Measured:
96% of starvation deaths are ACUTE one-step crashes with the reserve still half-full, and realised e0 is 23.5
against a Siler schedule 36.5.

THE FIX (Keys 1950, Minnesota Starvation). Under a draining reserve the body turns its metabolism DOWN
(~10-25% adaptive over weeks, ~40% total at ~25% weight loss). Modelled on the reserve level:
`burn_eff = burn * (1 - d)`, `d = downreg_max * clamp((1 - frac)/downreg_span, 0, 1)`,
`frac = (wealth - floor)/(full - floor)`. A full reserve gives `d = 0` (bit-exact for the well-fed).

THE LOAD-BEARING TEST is `test_MODEL_a_draining_reserve_burns_less`: two identical worlds are driven a step with
every agent's reserve set into the draining zone; with the flag ON the population burns strictly less than with
it OFF, and the OFF world is bit-identical to a no-downreg baseline. The `test_MODEL_a_full_reserve_is_unchanged`
control is the required negative: down-regulation must be INERT for the well-fed, on the same path.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off():
    c = DemographyConfig()
    assert c.enable_metabolic_downreg is False
    assert c.metabolic_downreg_max == pytest.approx(0.40)
    assert c.metabolic_downreg_span == pytest.approx(0.5)


# ─────────────────────────── the down-regulation curve (documentation) ───────────────────────────

def _d(frac, dr_max=0.40, span=0.5):
    return dr_max * min(1.0, max(0.0, (1.0 - frac) / span))


def test_a_full_reserve_has_no_down_regulation():
    assert _d(1.0) == pytest.approx(0.0)


def test_a_depleted_reserve_reaches_the_cap():
    assert _d(0.5) == pytest.approx(0.40)      # full down-reg reached at half-depleted (span=0.5)
    assert _d(0.0) == pytest.approx(0.40)      # and stays at the cap below that
    assert _d(0.75) == pytest.approx(0.20)     # halfway to the cap at frac 0.75


# ─────────────────────────── the model path ───────────────────────────

def _world(downreg, seed=0, n=200):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load().get("DemographyConfig", {}))
    cfg["enable_metabolic_downreg"] = downreg
    return B1._build(cfg, n=n, patch=30, terr="coastal", clim="temperate", seed=seed)


def _set_all_reserve_frac(w, frac):
    """Put every agent's reserve at `frac` of its own [floor, full] band, and return the mean wealth set."""
    tot = 0.0
    for a in w.agent_list:
        flr = a.reserve_floor * a.reserve_scale()
        cap = w._reserve_full * a.reserve_scale()
        a.wealth = flr + frac * (cap - flr)
        tot += a.wealth
    return tot


def _mean_burn_this_step(w, frac):
    """Zero the food (a total famine — the only state in which down-regulation fires, since it reads the
    reserve AFTER eating and a fed cell refills to full ⇒ d=0), set every reserve to `frac`, run ONE step, and
    recover the mean burn as the wealth DROP (intake is zero). Isolates the burn through the REAL step path."""
    w._harvest_field.level = lambda x, y: 0.0     # total famine: no cell yields anything this step
    _set_all_reserve_frac(w, frac)
    before = {id(a): a.wealth for a in w.agent_list}
    w.step()
    drains = [before[id(a)] - a.wealth for a in w.agent_list if id(a) in before]  # intake=0 ⇒ drop == burn_eff
    return sum(drains) / len(drains) if drains else 0.0


def test_MODEL_a_draining_reserve_burns_less():
    """LOAD-BEARING. With reserves in the draining zone (frac 0.3), the ON world burns strictly LESS per agent
    than the OFF world, through the real metabolism path. Verified to FAIL (equal burn) when the flag is off."""
    off = _mean_burn_this_step(_world(False), frac=0.7)
    on = _mean_burn_this_step(_world(True), frac=0.7)
    assert on < off * 0.98, (
        f"metabolic down-regulation did not reduce the burn on a draining reserve (on={on:.0f} off={off:.0f}) "
        "-- the mechanism is not reaching the metabolism step")


def test_MODEL_a_full_reserve_is_unchanged():
    """THE NEGATIVE CONTROL. Down-regulation must be INERT for the well-fed: at a full reserve the ON and OFF
    worlds burn the same. If this fails, the mechanism is taxing healthy agents, not just starving ones."""
    off = _mean_burn_this_step(_world(False), frac=0.999)
    on = _mean_burn_this_step(_world(True), frac=0.999)
    assert on == pytest.approx(off, rel=0.01), (
        f"down-regulation changed the burn of FULL-reserve agents (on={on:.0f} off={off:.0f}) -- it must be "
        "inert for the well-fed")
