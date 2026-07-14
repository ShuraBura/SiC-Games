"""Cut-2 adaptive connubium (`enable_adaptive_connubium`): per-seeker expanding mate search + its OWN
settlement founding (decoupled from `_do_gathering`, which the dispatch bypasses). Default-OFF ⇒ bit-exact."""
import numpy as np
import pytest

from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField


def _world(n_agents=0, positions=None, **demog_kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    d = DemographyConfig(**demog_kw)
    w = TerrainWorld(n_agents=n_agents, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                     harvest_field=hf, demography_cfg=d, placement_positions=positions)
    return w


def test_adaptive_connubium_defaults_off():
    cfg = DemographyConfig()
    assert cfg.enable_adaptive_connubium is False
    assert cfg.mate_search_min_eligible == 3
    assert cfg.mate_search_max_radius == 15


def test_cut2_founds_settlements_decoupled_from_gathering():
    """The wiring guard for `_found_settlements_by_occupancy`: a cluster of ≥ settle_min_pool agents on a storable
    (S_pot ≥ persist) cell founds a settlement — with NO `_do_gathering` call in the path."""
    w = _world(enable_adaptive_connubium=True, enable_aggregation_sedentism=True, enable_pair_bonds=True)
    aqf = w._s_pot_field()
    assert aqf is not None
    y, x = np.unravel_index(int(np.argmax(aqf)), aqf.shape)   # the single most-storable cell → candidate #1
    assert aqf[y, x] >= w._demog.settle_persist_threshold, "coastal world must have a storable site"
    site = (int(x), int(y))
    for _ in range(w._demog.settle_min_pool):                # cluster exactly the min-viable pool onto it
        a = w._make_agent(sex="male", lh_cfg=None); a.pos = site
        w.agent_list.append(a)
    assert not w._settlement_sites
    w._found_settlements_by_occupancy()
    # founded from occupancy alone (no mating pools); anchors at the best storable cell WITHIN the cluster's reach
    # (top-S_pot, min-separated candidacy) — which may be an adjacent cell, not the exact modal one.
    assert w._settlement_sites, "a cluster of settle_min_pool on a storable cell must found a settlement"
    founded = next(iter(w._settlement_sites))
    assert max(abs(founded[0] - site[0]), abs(founded[1] - site[1])) <= w._demog.settle_radius


def test_cut2_founding_respects_min_pool():
    """One agent below the threshold ⇒ no settlement (min-viable-hamlet gate holds on the Cut-2 path too)."""
    w = _world(enable_adaptive_connubium=True, enable_aggregation_sedentism=True, enable_pair_bonds=True)
    aqf = w._s_pot_field()
    y, x = np.unravel_index(int(np.argmax(aqf)), aqf.shape)
    site = (int(x), int(y))
    for _ in range(w._demog.settle_min_pool - 1):            # one short of the pool
        a = w._make_agent(sex="male", lh_cfg=None); a.pos = site
        w.agent_list.append(a)
    w._found_settlements_by_occupancy()
    assert site not in w._settlement_sites


def test_cut2_dispatch_runs_and_records_reach():
    """End-to-end: with adaptive connubium the dispatch calls `_do_connubium` (not gathering); a gathering step
    records connubium reach and the run does not crash."""
    land = None
    w = _world(n_agents=300, positions=None,
               enable_adaptive_connubium=True, enable_exogamy=True, enable_pair_bonds=True,
               enable_band_affiliation=True, enable_aggregation_sedentism=True)
    period = w._demog.aggregation_period
    for _ in range(period + 1):                               # step past one gathering
        w.step()
        if not w.agent_list:
            pytest.skip("population died before a gathering fired")
    con = w.connubium()
    assert con == {} or con.get("median", 0) >= 1            # reach recorded (or no pairing this phase) — no crash
