"""Storability-gated society morph (§4.5.10, blueprint …_StorabilityGatedMorph): gate storage on biome seasonal
amplitude (Testart/Binford) so the morph fits the biome — aseasonal forest → egalitarian, seasonal → complex."""
import numpy as np

from sic_games.climate import seasonal_amplitude_field, BIOME_SEASONAL_AMP_BY_CODE


def test_amp_field_maps_biome_codes():
    biome = np.array([[2, 3], [4, 0]], dtype=np.uint8)   # forest, savanna / grass, water
    amp = seasonal_amplitude_field(biome)
    assert amp[0, 0] == BIOME_SEASONAL_AMP_BY_CODE[2] == 0.05   # forest aseasonal
    assert amp[0, 1] == BIOME_SEASONAL_AMP_BY_CODE[3] == 0.40   # savanna
    assert amp[1, 0] == BIOME_SEASONAL_AMP_BY_CODE[4] == 0.60   # grass/llanos
    assert amp[1, 1] == 0.0                                     # water


def test_forest_below_threshold_savanna_above():
    """The default threshold 0.25 splits aseasonal forest (no storage) from seasonal biomes (storage)."""
    thr = 0.25
    assert BIOME_SEASONAL_AMP_BY_CODE[2] < thr                 # forest → no storage → egalitarian
    for code in (3, 4, 5, 6):                                  # savanna/grass/desert/mountain → storage-capable
        assert BIOME_SEASONAL_AMP_BY_CODE[code] >= thr


def test_all_biome_codes_present():
    for code in range(7):
        assert code in BIOME_SEASONAL_AMP_BY_CODE


def test_gate_default_off_bit_exact():
    """storage_seasonality_gated default OFF ⇒ the temperature gate path (bit-exact) — a short seeded run matches."""
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "outputs", "biome_society_20260702"))
    from run_biome_society import realistic_forager_demog, capacity_aware_seed, BURN, X0, Y0, PATCH, FOUNDERS, GRP
    from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
    from sic_games.phase1_model import TerrainWorld
    from sic_games.terrain import generate_world, world_lottery
    from sic_games.capacity import NPPCapacityField
    from collections import Counter

    def world(update, steps=40):
        knobs = world_lottery(0, archetype="savanna")
        fields = generate_world(knobs)
        cap = NPPCapacityField(fields, BURN, patch=(X0, Y0, PATCH), mode="tallavaara")
        pos = capacity_aware_seed(cap, BURN, FOUNDERS)
        demog = realistic_forager_demog().model_copy(update=update)
        w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs, game_stream=False,
            seed=0, carbon_cfg=CarbonConfig(kappa=1.5),
            substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                          contest_exponent=1.5, move_cost_flat=0.0, **GRP),
            harvest_field=cap, placement_positions=pos, demography_cfg=demog)
        for _ in range(steps):
            w.step()
        return w

    w0 = world({})
    w1 = world(dict(storage_seasonality_gated=False))
    assert Counter(a.pos for a in w0.agent_list) == Counter(a.pos for a in w1.agent_list)


def test_morph_aquatic_gate_default_off_bit_exact():
    """morph_aquatic_gated default OFF ⇒ identical trajectory (the aquatic morph gate is the corrected fix:
    storage stays a broad buffer, only the surplus→complex morph is gated on water access)."""
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "outputs", "biome_society_20260702"))
    from run_biome_society import realistic_forager_demog, capacity_aware_seed, BURN, X0, Y0, PATCH, FOUNDERS, GRP
    from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
    from sic_games.phase1_model import TerrainWorld
    from sic_games.terrain import generate_world, world_lottery
    from sic_games.capacity import NPPCapacityField
    from collections import Counter

    def world(update, steps=40):
        knobs = world_lottery(0, archetype="savanna")
        fields = generate_world(knobs)
        cap = NPPCapacityField(fields, BURN, patch=(X0, Y0, PATCH), mode="tallavaara")
        pos = capacity_aware_seed(cap, BURN, FOUNDERS)
        demog = realistic_forager_demog().model_copy(update=update)
        w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs, game_stream=False,
            seed=0, carbon_cfg=CarbonConfig(kappa=1.5),
            substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                          contest_exponent=1.5, move_cost_flat=0.0, **GRP),
            harvest_field=cap, placement_positions=pos, demography_cfg=demog)
        for _ in range(steps):
            w.step()
        return w

    w0 = world({})
    w1 = world(dict(morph_aquatic_gated=False))
    assert Counter(a.pos for a in w0.agent_list) == Counter(a.pos for a in w1.agent_list)
