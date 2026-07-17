"""Divorce semantics (R-78) — `divorce_rate` now means per-step on ALL pairing paths.

THE BUG (found by the R-75 dashboard: frac_parents_divorced 0.014 vs the Aché 0.14). `divorce_rate` is
documented "per-step bond dissolution prob". It WAS per-step in `_do_pairing` (runs every step) but sat AFTER
the seasonal gate in `_do_gathering`/`_do_connubium` (`step % aggregation_period != 0: return`), so under
`enable_marriage_aggregation` — the canonical village stack — it fired only on gathering steps: ~12× rarer.
Fix: the draw moved to `_do_divorce`, called once per step in the main loop, independent of pairing path.

Anchor: Hill & Hurtado Tab. 13.1, ~0.14 of child (0-9) risk-intervals are parents-divorced (both living) —
a prevalence, so `divorce_rate` (a flow) is calibrated to 0.005 (reproduces ≈0.14 on both paths). Feeds the
R-74 orphan channel's ×2.97 divorced-child multiplier.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

YR = 12


def _world(**kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=DemographyConfig(**kw))


class _P:
    def __init__(self, sex="female", age_yr=25.0):
        self.sex = sex
        self.age = age_yr * YR
        self._partner = None
        self._wives = set()
        self.alive = True


def _pair(h, w):
    w._partner = h
    h._wives.add(w)


def test_divorce_rate_defaults_off():
    assert DemographyConfig().divorce_rate == 0.0            # 0 ⇒ lifelong unless widowed ⇒ bit-exact


def test_divorce_off_is_a_noop():
    w = _world(divorce_rate=0.0)
    h = _P("male", 35); wife = _P()
    _pair(h, wife)
    w.agent_list = [h, wife]
    w._do_divorce()
    assert wife._partner is h and wife in h._wives


def test_divorce_dissolves_a_bond_and_returns_the_wife_to_the_pool():
    w = _world(divorce_rate=1.0)                             # certainty → deterministic
    h = _P("male", 35); wife = _P()
    _pair(h, wife)
    w.agent_list = [h, wife]
    w._do_divorce()
    assert wife._partner is None and wife not in h._wives    # serial monogamy: she re-enters pairing


def test_divorce_is_symmetric_across_paths_because_it_left_the_pairing_methods():
    """THE fix. The draw is no longer inside `_do_pairing`/`_do_gathering`/`_do_connubium` — those methods
    must contain no `divorce_rate` logic, so the seasonal gate on the gathering paths can no longer make it
    fire ~12× rarer. `_do_divorce` is the single home."""
    import inspect
    from sic_games.phase1_model import TerrainWorld as TW
    for name in ("_do_pairing", "_do_gathering", "_do_connubium"):
        src = inspect.getsource(getattr(TW, name))
        assert "divorce_rate" not in src, f"{name} still references divorce_rate — semantics split remains"
    assert "divorce_rate" in inspect.getsource(TW._do_divorce)


def test_divorce_fires_every_step_not_per_gathering():
    """Over N steps with a small rate, the expected number of dissolutions scales with N (every-step), not
    with N/aggregation_period (per-gathering). Checked as a rate, not an exact count."""
    w = _world(divorce_rate=0.05)
    husbands = [_P("male", 35) for _ in range(200)]
    wives = [_P("female", 25) for _ in range(200)]
    for h, wf in zip(husbands, wives):
        _pair(h, wf)
    w.agent_list = husbands + wives
    intact0 = sum(1 for wf in wives if wf._partner is not None)
    for _ in range(10):
        w._do_divorce()
    intact = sum(1 for wf in wives if wf._partner is not None)
    # per-step: ~1-(0.95)^10 ≈ 40% dissolved over 10 steps. Per-gathering (annual) would be ~0 over 10 steps.
    dissolved = intact0 - intact
    assert dissolved > 0.25 * intact0, f"expected every-step attrition; only {dissolved}/{intact0} dissolved"


def test_calibrated_rate_is_the_canonical_value():
    """The canonical preset sets divorce_rate=0.005 (calibrated to the Aché 0.14 divorced exposure). Guards
    against a silent drift of that number away from its anchor."""
    import os
    import sys
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.normpath(os.path.join(_here, "..", "outputs", "phase1_social_evolution")))
    from run_se0_controlled_climate import realistic_forager_demog
    assert realistic_forager_demog().divorce_rate == pytest.approx(0.005)
