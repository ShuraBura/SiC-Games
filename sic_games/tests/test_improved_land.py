"""Improved-land defensibility (agriculture): cultivable land becomes claimable where WORKED (inside an active
settlement's catchment), not merely fertile — the agrarian territoriality path. Default-OFF ⇒ aquatic-only (bit-exact)."""
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


def _cultivable_nonaquatic_cell(w):
    """A cell cultivable (≥ dmin) but NOT aquatic (< dmin) — so ONLY improved-land can make it claimable."""
    cult = w._fields.cultivability; aqf = w._fields.aquatic_food; dmin = w._demog.defensibility_min
    for y in range(100):
        for x in range(100):
            if cult[y, x] >= dmin and aqf[y, x] < dmin:
                return (x, y)
    return None


def _place_band(w, cell, n, band_id=1):
    for _ in range(n):
        a = w._make_agent(sex="male", lh_cfg=None)
        a.pos = cell; a._group.band_id = band_id
        w.agent_list.append(a)


def _claim_for_dwell(w):
    for _ in range(w._demog.defensibility_claim_dwell + 1):
        w._update_defensibility_claims()


def test_improved_land_defaults_off():
    assert DemographyConfig().enable_improved_land is False


def test_improved_land_claims_worked_cultivable_cell():
    w = _world(enable_economic_defensibility=True, enable_improved_land=True)
    cell = _cultivable_nonaquatic_cell(w)
    assert cell is not None, "coastal world should have a cultivable non-aquatic cell"
    _place_band(w, cell, w._demog.defensibility_claim_min + 2)
    w._settlement_sites[cell] = w._demog.settle_release_steps       # the cell is WORKED (a settlement catchment)
    _claim_for_dwell(w)
    assert w._cell_owner.get(cell) == 1, "a worked cultivable cell is claimed under improved-land"


def test_improved_land_ignores_unworked_cultivable_cell():
    w = _world(enable_economic_defensibility=True, enable_improved_land=True)
    cell = _cultivable_nonaquatic_cell(w)
    _place_band(w, cell, w._demog.defensibility_claim_min + 2)      # cultivable land, but NO settlement → unworked
    _claim_for_dwell(w)
    assert cell not in w._cell_owner, "cultivable but UN-worked land is not claimable"


def test_off_leaves_cultivable_unclaimable():
    """Default-OFF (aquatic-only): even a WORKED cultivable-non-aquatic cell is not claimable — bit-exact old behaviour."""
    w = _world(enable_economic_defensibility=True, enable_improved_land=False)
    cell = _cultivable_nonaquatic_cell(w)
    _place_band(w, cell, w._demog.defensibility_claim_min + 2)
    w._settlement_sites[cell] = w._demog.settle_release_steps
    _claim_for_dwell(w)
    assert cell not in w._cell_owner, "improved-land OFF → cultivable land stays unclaimable"
