"""S.4 society morph (per-cell). Locks the scenario behaviours the build is meant to produce: (1) a cold,
seasonal, storable region with tethering MORPHS egalitarian→complex; (2) a warm world (storage ET-gated off)
NEVER morphs (immediate-return — the Testart/Woodburn geography); (3) a sustained famine COLLAPSES the morphed
cells back to egalitarian; (4) flag off ⇒ no morph state (back-compat)."""
from __future__ import annotations

from collections import Counter

from sic_games.climate import ClimateField
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


class _Famine:                       # a sustained downturn: scale the whole field down
    def __init__(self, base, f): self._base = base; self._f = f
    def level(self, x, y): return self._base.level(x, y) * self._f
    def __getattr__(self, n): return getattr(self._base, n)


def _world(temp_threshold, tether, morph=True, seed=7, n=200):
    demog = DemographyConfig(enable_storage=True, storable_fraction=0.5, store_capacity_reserves=3.0,
                             storage_temp_threshold_c=temp_threshold, enable_cred_status=True, cred_seed_sigma=0.6,
                             cred_inherit_sigma=0.3, enable_morph=morph, morph_settle_steps=80,
                             storage_tether_reserves=tether)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     carbon_cfg=CarbonConfig(kappa=1.5), demography_cfg=demog)
    w._harvest_field = ClimateField(w.terrain_field, a_seas=0.6)
    return w


def test_morph_fires_in_cold_storable_region_with_tethering():
    w = _world(temp_threshold=100.0, tether=0.5)              # overwintering everywhere + tethering
    for _ in range(500):
        w.step()
    assert any(s == "complex_forager" for s in w._cell_society.values())   # egalitarian → complex morph fired


def test_morph_needs_tethering_to_concentrate():
    # without tethering agents diffuse (max occupancy ~2) → never reach the settlement preconditions → no morph
    w = _world(temp_threshold=100.0, tether=0.0)
    for _ in range(500):
        w.step()
    assert len(w._cell_society) == 0                          # no concentration ⇒ no morph


def test_morph_geography_warm_world_stays_egalitarian():
    # warm everywhere (storage ET-gated OFF) ⇒ no storage ⇒ no surplus ⇒ never morphs (immediate-return)
    w = _world(temp_threshold=-100.0, tether=0.5)
    for _ in range(500):
        w.step()
    assert len(w._cell_store) == 0 and len(w._cell_society) == 0


def test_morph_collapses_under_sustained_famine():
    w = _world(temp_threshold=100.0, tether=0.5)
    for _ in range(500):
        w.step()
    assert len(w._cell_society) > 0                           # morphed up first
    w._harvest_field = _Famine(w._harvest_field, 0.12)        # sustained downturn
    for _ in range(400):
        w.step()
    assert len(w._cell_society) == 0                          # … then collapses back to egalitarian


def test_morph_off_no_society_state():
    w = _world(temp_threshold=100.0, tether=0.5, morph=False)
    for _ in range(200):
        w.step()
    assert len(w._cell_society) == 0                          # flag off ⇒ no morph state (back-compat)
