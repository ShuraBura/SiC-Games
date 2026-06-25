"""Storage (delayed-return economy) — flaggable; the sedentism/inequality precursor (Testart 1982, Woodburn
1982, Binford 2001). Locks: (1) OFF ⇒ no store accrues (back-compat); (2) in the overwintering zone (cell temp
≤ threshold) a glut banks surplus into the per-agent store; (3) the ET/temperature gate — warm cells never
accumulate (immediate-return); (4) the winter-survival payoff — storage raises the harsh-winter carrying
capacity (the population is no longer capped by the lean season)."""
from __future__ import annotations

from sic_games.climate import ClimateField
from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


def _world(storage_on, temp_threshold=100.0, n=60, seed=5, a_seas=0.0):
    demog = DemographyConfig(enable_storage=storage_on, storable_fraction=0.5,
                             store_capacity_reserves=3.0, storage_temp_threshold_c=temp_threshold)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     demography_cfg=demog)
    if a_seas > 0.0:
        w._harvest_field = ClimateField(w.terrain_field, a_seas=a_seas)
    return w


def _max_store(w):
    return max((getattr(a, "_store", 0.0) for a in w.agents), default=0.0)


def test_storage_off_no_store_accrues():
    w = _world(storage_on=False)
    for _ in range(120):
        w.step()
    assert _max_store(w) == 0.0                                    # flag off ⇒ no store anywhere (back-compat)


def test_storage_accumulates_in_overwintering_zone():
    # threshold=100 °C ⇒ every cell is an overwintering zone; a productive glut banks surplus into the store
    w = _world(storage_on=True, temp_threshold=100.0)
    for _ in range(150):
        w.step()
    assert _max_store(w) > 0.0                                     # at least one agent banked a store


def test_storage_temperature_gated_off_in_warm_cells():
    # threshold = −100 °C ⇒ NO cell qualifies (all warmer) ⇒ immediate-return, no store accrues even when ON
    w = _world(storage_on=True, temp_threshold=-100.0)
    for _ in range(150):
        w.step()
    assert _max_store(w) == 0.0                                    # warm/immediate-return ⇒ no accumulation


def test_storage_raises_harsh_winter_carrying_capacity():
    # The payoff: under a harsh winter the unstored population is capped by the lean season; storage lifts it.
    def eq_pop(on):
        w = _world(storage_on=on, temp_threshold=100.0, n=120, a_seas=0.85)
        pops = [ (w.step(), len(w.agents))[1] for _ in range(500) ]
        return sum(pops[-150:]) / 150.0
    on, off = eq_pop(True), eq_pop(False)
    assert on > 1.3 * off                                          # storage materially raises harsh-winter capacity
