"""CTB — the diagnostics added 2026-08-11 to investigate the bistable-regime split (task #61: one world, one
climate, four agent paths, and the population separates into two DIFFERENT SOCIETIES — 0-2% stratified on two
paths, 62-82% on the other two). None of these fields are new MECHANISMS; every one summarizes state or a
counter the model already maintained and threw away each step.

THREE GROUPS, THREE DIFFERENT FAILURE MODES TO GUARD AGAINST:
  A. 12 elite/instability/lineage counters were computed every step() and never logged. Failure mode: a flag
     that gates the MECHANISM (e.g. enable_rank_hierarchy) also silently gates the COUNTER, so a run with the
     mechanism off would read a stale None instead of a true 0.
  B. settle_formed_this_step / settle_released_this_step are NEW counters. The one bug that would matter here is
     invisible from a single site's final state: `_settlement_sites[site] = release_steps` is a "found OR
     refresh" write at three call sites, so miscounting a REFRESH as a FORMATION would inflate settle_formed on
     every long run with any settlement at all (i.e. every run this diagnostic is meant to explain).
  C. `frac_resident` and `settlement_health()` summarize dicts (`_settlement_soil`, `_settlement_hardship`) that
     are entirely absent when their flags are off. Failure mode: reading `{}.get(...)` without a default returns
     None, and None serialises to JSON `null`, which breaks every downstream `np.mean()` on the trajectory.
"""
from types import SimpleNamespace

import numpy as np
import pytest

from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


# ── group B: settle_formed / settle_released ────────────────────────────────────────────────────────────────

def _occ_world(agent_positions, spot=None, min_pool=10, sep=10.0, thr=0.3, release=5):
    """A fake sized for `_found_settlements_by_occupancy`: needs `_s_pot_field()`, `_harvest_field` (for
    width/height), and the settlement dicts/counters `_maintain_settlements` and the founder both touch."""
    cfg = DemographyConfig(enable_aggregation_sedentism=True, settle_min_pool=min_pool,
                           settle_radius=2, settle_release_steps=release,
                           settle_persist_threshold=thr, aggregation_site_sep=sep)
    aq = np.zeros((100, 100)) if spot is None else spot
    f = SimpleNamespace(
        _fields=SimpleNamespace(aquatic_food=aq, cultivability=None), _demog=cfg, _spot_cache=None,
        _harvest_field=SimpleNamespace(width=100, height=100),
        _settlement_sites={}, settle_formed_this_step=0, settle_released_this_step=0,
        agent_list=[SimpleNamespace(pos=p) for p in agent_positions],
    )
    f._s_pot_field = lambda: TerrainWorld._s_pot_field(f)
    return f


def test_a_new_site_forming_is_counted_exactly_once():
    spot = np.zeros((100, 100)); spot[50, 50] = 0.9
    f = _occ_world([(50, 50)] * 15, spot=spot)
    assert not f._settlement_sites
    TerrainWorld._found_settlements_by_occupancy(f)
    assert (50, 50) in f._settlement_sites
    assert f.settle_formed_this_step == 1, "a genuinely new site must increment the FORMED counter"


def test_a_refresh_of_an_EXISTING_site_is_NOT_counted_as_a_formation():
    """THE BUG THIS TEST EXISTS FOR. `_settlement_sites[site] = release_steps` is identical code for founding
    and refreshing; without the `if site not in self._settlement_sites` guard, every long run's settle_formed
    would count every refresh of every long-lived site, which is most of the signal on a 15,000-step run."""
    spot = np.zeros((100, 100)); spot[50, 50] = 0.9
    f = _occ_world([(50, 50)] * 15, spot=spot)
    TerrainWorld._found_settlements_by_occupancy(f)          # founds it, counter -> 1
    assert f.settle_formed_this_step == 1
    f.settle_formed_this_step = 0                             # reset, as step() would between steps
    TerrainWorld._found_settlements_by_occupancy(f)           # same site, still above threshold: a REFRESH
    assert f.settle_formed_this_step == 0, "a refresh of an already-active site must not be counted as new"


def test_no_qualifying_site_forms_nothing():
    f = _occ_world([(50, 50)] * 2, min_pool=40)                # far below min_pool
    TerrainWorld._found_settlements_by_occupancy(f)
    assert not f._settlement_sites
    assert f.settle_formed_this_step == 0


def test_release_is_counted_exactly_once_per_dissolution():
    cfg = DemographyConfig(enable_aggregation_sedentism=True, settle_min_pool=40, settle_radius=2,
                           settle_release_steps=2)
    site = (50, 50)
    f = SimpleNamespace(_settlement_sites={site: 2}, _demog=cfg, _nearest_map=None,
                        settle_released_this_step=0,
                        agent_list=[SimpleNamespace(pos=(0, 0))] * 45)   # nobody near the site
    f._torus_cheby = lambda ax, ay, bx, by: TerrainWorld._torus_cheby(f, ax, ay, bx, by)
    f._build_nearest_map = lambda: TerrainWorld._build_nearest_map(f)
    TerrainWorld._maintain_settlements(f)                      # timer 2 -> 1, still alive
    assert site in f._settlement_sites and f.settle_released_this_step == 0
    TerrainWorld._maintain_settlements(f)                      # timer 1 -> 0 -> popped
    assert site not in f._settlement_sites
    assert f.settle_released_this_step == 1, "exactly one dissolution must be counted, not zero and not two"


def test_refreshing_does_not_touch_the_released_counter():
    cfg = DemographyConfig(enable_aggregation_sedentism=True, settle_min_pool=10, settle_radius=2,
                           settle_release_steps=5)
    site = (50, 50)
    f = SimpleNamespace(_settlement_sites={site: 1}, _demog=cfg, _nearest_map=None,
                        settle_released_this_step=0,
                        agent_list=[SimpleNamespace(pos=site)] * 20)     # pool present -> refresh, not release
    f._torus_cheby = lambda ax, ay, bx, by: TerrainWorld._torus_cheby(f, ax, ay, bx, by)
    f._build_nearest_map = lambda: TerrainWorld._build_nearest_map(f)
    TerrainWorld._maintain_settlements(f)
    assert f._settlement_sites[site] == 5
    assert f.settle_released_this_step == 0


# ── group C: settlements()'s frac_resident, and settlement_health() ────────────────────────────────────────

def _settle_world(sites, agent_positions):
    f = SimpleNamespace(_settlement_sites=dict(sites), agent_list=[SimpleNamespace(
        pos=p, _group=SimpleNamespace(band_id=0), _lineage=None, cred=1.0) for p in agent_positions])
    f._band_society = {}
    f._settlement_catchment_yield = lambda s: 0.0
    return f


def test_frac_resident_is_the_settled_share_of_the_WHOLE_population():
    site = (50, 50)
    f = _settle_world({site: 5}, [site] * 30 + [(0, 0)] * 70)   # 30 on-site, 70 elsewhere; pop=100
    out = TerrainWorld.settlements(f)
    assert out["frac_resident"] == pytest.approx(0.30)


def test_frac_resident_is_ZERO_not_missing_with_no_settlements():
    """The failure mode this guards: `{}.get("frac_resident", 0.0)` in run_campaign.py needs the caller-side
    default, because `settlements()` returns `{}` outright when there are no active sites. Confirms the EMPTY
    dict is what is actually returned (so the caller's default is exercised, not bypassed)."""
    f = _settle_world({}, [(0, 0)] * 50)
    assert TerrainWorld.settlements(f) == {}


def test_settlement_health_summarizes_soil_and_hardship():
    f = SimpleNamespace(_settlement_soil={(1, 1): 0.9, (2, 2): 0.1, (3, 3): 0.05},
                        _settlement_hardship={(1, 1): 0.2, (2, 2): 0.8})
    out = TerrainWorld.settlement_health(f)
    assert out["soil_mean"] == pytest.approx((0.9 + 0.1 + 0.05) / 3, abs=1e-6)
    assert out["soil_min"] == pytest.approx(0.05)
    assert out["soil_frac_depleted"] == pytest.approx(2 / 3, abs=1e-3)   # 0.1 and 0.05 are both < 0.2; rounded to 3dp
    assert out["hardship_mean"] == pytest.approx(0.5)
    assert out["hardship_max"] == pytest.approx(0.8)


def test_settlement_health_is_EMPTY_not_a_crash_with_neither_dict_populated():
    """The negative. Both flags off (or no site has existed long enough) ⇒ both dicts empty ⇒ {} — the caller
    in run_campaign.py must default every key to 0.0, never leave a None to serialise as null."""
    f = SimpleNamespace(_settlement_soil={}, _settlement_hardship={})
    assert TerrainWorld.settlement_health(f) == {}


def test_settlement_health_handles_soil_only():
    f = SimpleNamespace(_settlement_soil={(1, 1): 0.5}, _settlement_hardship={})
    out = TerrainWorld.settlement_health(f)
    assert "soil_mean" in out and "hardship_mean" not in out


# ── group A: the per-step counters are always numeric, never None, whatever flags are set ─────────────────

@pytest.mark.parametrize("attr", [
    "deaths_senesc_this_step", "deaths_orphan_this_step", "leveling_events_this_step",
    "depositions_this_step", "desertions_this_step", "challenges_this_step", "feast_spend_this_step",
    "legitimated_this_step", "reversions_this_step", "lineage_branches_this_step",
    "lineage_splits_this_step", "lineage_tribute_this_step", "bud_events_this_step",
    "settle_formed_this_step", "settle_released_this_step",
])
def test_every_new_counter_exists_and_is_numeric_after_a_step(attr):
    """A run with every optional mechanism OFF must still carry these as 0 / 0.0 AFTER a step, never
    AttributeError and never None — the exact failure that made polygyny invisible for weeks: a value that was
    never wrong, only never READ. Built with the default (mechanism-off) DemographyConfig.

    CHECKED AFTER w.step(), NOT before construction. All twenty-odd `*_this_step` counters (mine and the
    pre-existing ones alike) are reset inside step()'s own reset block, not `__init__` — three exceptions
    (`births_this_step`, `deaths_starv_this_step`, `deaths_senesc_this_step`) are pre-seeded in `__init__` for
    reasons unrelated to this diagnostic. The harness itself (`run_campaign.py`) never calls its snapshot
    before the first `w.step()` — `for step in range(1, STEPS+1): w.step(); ... snapshot(...)` — so that is the
    guarantee that actually matters, not "exists before any step ever runs"."""
    from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
    from sic_games.terrain import generate_world, world_lottery_climate
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    w = TerrainWorld(n_agents=30, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                     demography_cfg=DemographyConfig())
    w.step()
    got = getattr(w, attr)
    assert isinstance(got, (int, float)), f"{attr} must be numeric after a step, got {got!r}"


def test_bud_events_this_step_resets_while_the_cumulative_counter_does_not():
    """Pins the ONE property that distinguishes the new per-step twin from the pre-existing cumulative counter:
    `bud_events` (cumulative) must never decrease; `bud_events_this_step` must reset to 0 every step()."""
    from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
    from sic_games.terrain import generate_world, world_lottery_climate
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    w = TerrainWorld(n_agents=30, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                     demography_cfg=DemographyConfig())
    assert w.bud_events == 0
    w.bud_events = 7                                            # simulate prior fissions
    w.step()
    assert w.bud_events >= 7, "the cumulative counter must never go backwards"
    # the per-step twin resets to 0 at the top of step() and increments in lock-step with the cumulative
    # counter thereafter, so whatever this step ADDED to bud_events must equal bud_events_this_step exactly.
    assert w.bud_events_this_step == w.bud_events - 7, (
        "the per-step and cumulative counters must record the SAME fissions this step")
