"""Newborn→adult life-history wiring + the two bugs it exposed. Locks: (1) enable_life_history auto-builds the
MONTH-scaled lh (forage_age_min=180, not the legacy 15); (2) an agent forced past max_age DIES (the hard cap was
dead code under demog); (3) η is clamped ≥ eta_old past max_age (never negative → no complex crash); (4) with
life-history on, juveniles forage at a graded η<1 and the run doesn't crash."""
from __future__ import annotations
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig, LifeHistoryConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


def _world(**demog_kw):
    d = DemographyConfig(siler_a1=0.157, siler_b1=0.721, siler_a2=0.013, siler_a3=4.8e-5, siler_b3=0.103, **demog_kw)
    return TerrainWorld(n_agents=40, kcal_cfg=KcalEconomyConfig(), seed=2, game_stream=False,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        carbon_cfg=CarbonConfig(kappa=1.5), demography_cfg=d)


def test_enable_life_history_auto_builds_month_scaled_lh():
    off = _world(enable_life_history=False)
    assert off._lh_cfg is None
    on = _world(enable_life_history=True)
    assert on._lh_cfg is not None and on._lh_cfg.forage_age_min == 180 and on._lh_cfg.forage_age_max_offset == 120


def test_agent_past_max_age_dies_under_demog():
    # the hard lifespan cap was an elif on `demog is None` (dead code under demog) → Siler-tail agents reached 1111.
    w = _world(enable_life_history=True)
    a = w.agent_list[0]
    a.age = a.max_age + 50          # force it past the cap
    w.step()
    assert a not in w.agent_list and not a.alive         # backstop now fires


def test_eta_clamped_non_negative_past_max_age():
    a = _world(enable_life_history=True).agent_list[0]
    a.age = a.max_age + 500          # far past max_age (the old formula went negative here)
    assert a.eta() >= a._eta_old - 1e-9 and a.eta() >= 0.0


def test_life_history_run_has_graded_juveniles_no_crash():
    w = _world(enable_life_history=True, enable_provisioning=True, enable_paternity=True,
               enable_cred_status=True, enable_prowess_facet=True)
    for _ in range(120):
        w.step()
        if not w.agent_list:
            break
    juv = [a for a in w.agent_list if a.age < 180]
    if juv:                                              # some juveniles present → they forage at graded η<1
        assert all(0.0 <= a.eta() < 1.0 for a in juv)
    assert all(a.age < a.max_age for a in w.agent_list)  # cap holds through the run
