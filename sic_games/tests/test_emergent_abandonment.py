"""Emergent abandonment: a settlement's HOLD erodes with the village's REMEMBERED fortunes (a slow per-SITE hardship
EMA — the elders' memory). No "if soil < X dissolve" rule and no global knowledge; releasing the pin just lets the
agents' existing IFD drive decide. Default-OFF ⇒ the pin never releases (bit-exact)."""
import pytest

from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField


def _world(**kw):
    k = world_lottery_climate(0, terrain="flat", climate="tropical")   # rain-fed: farm sites at both wateracc extremes
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=DemographyConfig(**kw))


def _farm_site(w, high_water: bool):
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
    return best


def _farm_for(w, site, steps, pressure=1.0):
    carry = int(w._demog.soil_carry_per_cell * (2 * w._demog.settle_catchment_radius + 1) ** 2 * pressure)
    for _ in range(carry):
        a = w._make_agent(sex="male", lh_cfg=None); a.pos = site
        w.agent_list.append(a)
    w._settlement_sites[site] = w._demog.settle_release_steps
    for _ in range(steps):
        w._update_settlement_soil()
    return w._settlement_hardship.get(site, 0.0)


def test_emergent_abandonment_defaults_off():
    c = DemographyConfig()
    assert c.enable_emergent_abandonment is False
    assert c.settlement_memory_yr == 12.0
    assert c.abandon_hardship_gain == 1.0


def test_chronic_decline_builds_the_villages_memory():
    """A rain-fed village farmed into exhaustion accumulates remembered hardship → its hold erodes."""
    w = _world(enable_soil_depletion=True, enable_emergent_abandonment=True)
    site = _farm_site(w, high_water=False)
    h = _farm_for(w, site, 240)                       # 20 yr of cropping an exhausting site
    assert h > 0.5, f"chronic decline should build remembered hardship; got {h:.3f}"


def test_renewed_village_never_builds_hardship():
    """A flood-renewed (alluvial) village keeps its soil ⇒ no remembered hardship ⇒ it never abandons (hydraulic)."""
    w = _world(enable_soil_depletion=True, enable_alluvial_renewal=True, enable_emergent_abandonment=True)
    site = _farm_site(w, high_water=True)
    h = _farm_for(w, site, 240)
    assert h < 0.3, f"a renewed village should not accumulate hardship; got {h:.3f}"


def test_memory_is_slow_one_bad_year_does_not_move_it():
    """Hysteresis is intrinsic: the memory is generational, so a transient bad spell barely registers."""
    w = _world(enable_soil_depletion=True, enable_emergent_abandonment=True)
    site = _farm_site(w, high_water=False)
    h = _farm_for(w, site, 1)
    assert h < 0.02, f"a single bad step should barely move a generational memory; got {h:.4f}"


def test_hardship_is_proportional_to_real_over_exploitation():
    """REASSURANCE: the trigger is not arbitrary/elapsed-time — hardship tracks ACTUAL over-working of the land. A
    lightly-worked village keeps its soil (and its hold on its people) far longer than a heavily-worked one."""
    heavy = _world(enable_soil_depletion=True, enable_emergent_abandonment=True)
    h_heavy = _farm_for(heavy, _farm_site(heavy, high_water=False), 144, pressure=1.0)   # 12 yr, full pressure
    light = _world(enable_soil_depletion=True, enable_emergent_abandonment=True)
    h_light = _farm_for(light, _farm_site(light, high_water=False), 144, pressure=0.1)   # 12 yr, a tenth the pressure
    assert h_light < 0.5 * h_heavy, f"hardship must scale with real over-exploitation: light={h_light:.3f} heavy={h_heavy:.3f}"
    assert h_heavy > 0.3, f"a fully-worked village SHOULD accumulate hardship; got {h_heavy:.3f}"


def test_memory_off_stays_empty():
    w = _world(enable_soil_depletion=True, enable_emergent_abandonment=False)
    site = _farm_site(w, high_water=False)
    _farm_for(w, site, 120)
    assert not w._settlement_hardship, "memory should not accumulate when the mechanism is off"
