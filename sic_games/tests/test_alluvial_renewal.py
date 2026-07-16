"""Terrain-dependent soil renewal: a FLOODPLAIN farm (high wateracc) is re-fertilised in place by the annual flood
silt (Nile — cropped for millennia without fallow) while RAIN-FED dryland exhausts (swidden). Default-OFF ⇒ every farm
depletes (bit-exact)."""
import pytest

from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField


def _world(**kw):
    # flat-tropical: rain-fed (aquatic 0.6%) + broadly cultivable ⇒ plenty of FARM sites at both wateracc extremes
    k = world_lottery_climate(0, terrain="flat", climate="tropical")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    d = DemographyConfig(**kw)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=d)


def _farm_site(w, high_water: bool):
    """The FARM cell (cultivability > aquatic, genuinely arable) with the highest / lowest wateracc."""
    cult = w._fields.cultivability; aq = w._fields.aquatic_food
    wacc = w._fields.wateracc; wet = w._fields.isWater
    best, bestv = None, None
    for y in range(100):
        for x in range(100):
            if wet[y, x] or cult[y, x] <= aq[y, x] or cult[y, x] < 0.2:
                continue
            v = float(wacc[y, x])
            if best is None or (v > bestv if high_water else v < bestv):
                best, bestv = (x, y), v
    return best, bestv


def _farm_for(w, site, steps):
    """Settle `carry` people on the site (farming pressure ≈ 1) and run the soil update for `steps` months."""
    carry = int(w._demog.soil_carry_per_cell * (2 * w._demog.settle_catchment_radius + 1) ** 2)
    for _ in range(carry):
        a = w._make_agent(sex="male", lh_cfg=None); a.pos = site
        w.agent_list.append(a)
    w._settlement_sites[site] = w._demog.settle_release_steps
    for _ in range(steps):
        w._update_settlement_soil()
    return w._settlement_soil.get(site, 1.0)


def test_alluvial_renewal_defaults_off():
    c = DemographyConfig()
    assert c.enable_alluvial_renewal is False
    assert c.alluvial_renew_per_yr == 3.0


def test_alluvial_farm_is_renewed_by_the_flood():
    w = _world(enable_soil_depletion=True, enable_alluvial_renewal=True)
    site, wv = _farm_site(w, high_water=True)
    assert site is not None
    soil = _farm_for(w, site, 240)                       # 20 years of continuous cropping
    assert soil > 0.5, f"alluvial farm (wateracc={wv:.2f}) should stay fertile via flood silt; got soil={soil:.3f}"


def test_rainfed_farm_exhausts():
    w = _world(enable_soil_depletion=True, enable_alluvial_renewal=True)
    site, wv = _farm_site(w, high_water=False)
    assert site is not None
    soil = _farm_for(w, site, 240)
    assert soil < 0.2, f"rain-fed farm (wateracc={wv:.2f}) should exhaust (swidden); got soil={soil:.3f}"


def test_renewal_off_alluvial_also_exhausts():
    """Default-OFF ⇒ terrain is ignored and even floodplain farmland exhausts (the old uniform behaviour)."""
    w = _world(enable_soil_depletion=True, enable_alluvial_renewal=False)
    site, _ = _farm_site(w, high_water=True)
    soil = _farm_for(w, site, 240)
    assert soil < 0.2, f"renewal OFF → alluvial farmland exhausts like dryland; got soil={soil:.3f}"
