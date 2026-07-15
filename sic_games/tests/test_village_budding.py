"""Village budding (Bandy 2004 / Chagnon 1975): a village past the fission threshold sheds its 2nd-largest lineage
faction, which relocates to a nearby available storable site and founds a daughter village. Default-OFF ⇒ bit-exact."""
import pytest

from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField


def _world(**kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    d = DemographyConfig(**kw)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=d)


def _place(w, cell, n, lineage, band_id):
    out = []
    for _ in range(n):
        a = w._make_agent(sex="male", lh_cfg=None)
        a.pos = cell; a._lineage = lineage; a._group.band_id = band_id
        w.agent_list.append(a); out.append(a)
    return out


def _site_with_neighbor(w):
    """A storable cell that has ANOTHER storable cell within [sep+1, R] (so a daughter site exists)."""
    aqf = w._s_pot_field(); persist = w._demog.settle_persist_threshold
    sep = w._demog.settle_radius; R = w._demog.village_bud_search_radius
    storable = [(x, y) for y in range(100) for x in range(100) if aqf[y, x] >= persist]
    S = set(storable)
    for (sx, sy) in storable:
        for (x, y) in storable:
            if sep + 1 <= max(abs(x - sx), abs(y - sy)) <= R:
                return (sx, sy)
    return None


def test_village_budding_defaults_off():
    c = DemographyConfig()
    assert c.enable_village_budding is False
    assert c.village_fission_threshold == 150
    assert c.village_bud_min_faction == 0.25


def test_budding_sheds_rival_lineage_to_new_site():
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=20)
    site = _site_with_neighbor(w)
    assert site is not None, "coastal world should have a storable site with a storable neighbor in reach"
    maj = _place(w, site, 20, 1, 0)          # majority lineage-1 (band_id 0)
    riv = _place(w, site, 10, 2, 0)          # rival lineage-2 (10/30 = 33% ≥ min_faction 0.25)
    w._settlement_sites[site] = w._demog.settle_release_steps
    w._next_band_id = 7                       # invariant: the id counter is above all live band_ids (as in a real run)
    n0 = len(w._settlement_sites)
    w._maintain_village_budding()
    riv_bids = set(a._group.band_id for a in riv)
    assert len(riv_bids) == 1 and 0 not in riv_bids, "rival faction takes ONE new band_id"
    assert all(a.pos != site for a in riv), "rival faction relocates off the parent site"
    assert all(a._group.band_id == 0 and a.pos == site for a in maj), "majority stays put"
    assert len(w._settlement_sites) > n0, "a daughter settlement is founded"


def test_single_lineage_village_does_not_bud():
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=20)
    site = _site_with_neighbor(w)
    riv = _place(w, site, 30, 1, 0)          # ONE lineage → no cleavage line
    w._settlement_sites[site] = w._demog.settle_release_steps
    n0 = len(w._settlement_sites)
    w._maintain_village_budding()
    assert len(w._settlement_sites) == n0 and all(a._group.band_id == 0 for a in riv)


def test_stratified_village_does_not_bud():
    """Bandy: integrative institutions (stratification) suppress fission."""
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=20)
    site = _site_with_neighbor(w)
    _place(w, site, 20, 1, 0); riv = _place(w, site, 10, 2, 0)
    w._band_society[0] = "stratified_chiefdom"     # the village's band is stratified
    w._settlement_sites[site] = w._demog.settle_release_steps
    n0 = len(w._settlement_sites)
    w._maintain_village_budding()
    assert len(w._settlement_sites) == n0 and all(a._group.band_id == 0 for a in riv)


def test_below_threshold_does_not_bud():
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=50)
    site = _site_with_neighbor(w)
    _place(w, site, 20, 1, 0); riv = _place(w, site, 10, 2, 0)   # 30 ≤ 50 threshold
    w._settlement_sites[site] = w._demog.settle_release_steps
    w._maintain_village_budding()
    assert all(a._group.band_id == 0 for a in riv)
