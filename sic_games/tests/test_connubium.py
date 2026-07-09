"""Connubium exogamy rule (Cut 1): individual-level kin/clan prohibition in _pair_from_pool. Default OFF ⇒ bit-exact."""
import pytest

from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField


def _world(degree):
    k = world_lottery_climate(0, terrain="flat", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    d = DemographyConfig(enable_exogamy=True, exogamy_degree=degree, enable_pair_bonds=True)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=d)


def test_exogamy_defaults_off():
    cfg = DemographyConfig()
    assert cfg.enable_exogamy is False
    assert cfg.exogamy_degree == "lineage"


def test_lineage_exogamy_rejects_sibling_and_clan_pairs_outsider():
    w = _world("lineage")
    mom = w._make_agent(sex="female", lh_cfg=None)
    f0 = w._make_agent(sex="female", lh_cfg=None); f0._mother = mom; f0._lineage = 1; f0.age = 300
    bro = w._make_agent(sex="male", lh_cfg=None); bro._mother = mom; bro._lineage = 1; bro.age = 300   # sibling
    clan = w._make_agent(sex="male", lh_cfg=None); clan._lineage = 1; clan.age = 300                   # same clan, unrelated
    out = w._make_agent(sex="male", lh_cfg=None); out._lineage = 2; out.age = 300                      # exogamous
    w._pair_from_pool([f0], [bro, clan, out], "flexible", 0.0, None)
    assert f0._partner is out                                     # not the brother, not the clansman


def test_nuclear_degree_allows_unrelated_same_lineage():
    w = _world("nuclear")
    f1 = w._make_agent(sex="female", lh_cfg=None); f1._lineage = 1; f1.age = 300
    clan = w._make_agent(sex="male", lh_cfg=None); clan._lineage = 1; clan.age = 300   # same lineage but NOT a relative
    w._pair_from_pool([f1], [clan], "flexible", 0.0, None)
    assert f1._partner is clan                                    # nuclear degree ignores clan membership


def test_sibling_via_shared_father_rejected():
    w = _world("nuclear")
    dad = w._make_agent(sex="male", lh_cfg=None)
    f0 = w._make_agent(sex="female", lh_cfg=None); f0._father = dad; f0.age = 300
    halfbro = w._make_agent(sex="male", lh_cfg=None); halfbro._father = dad; halfbro.age = 300   # shared father
    w._pair_from_pool([f0], [halfbro], "flexible", 0.0, None)
    assert f0._partner is None                                    # no eligible non-kin → unpaired
