"""Economy-from-Climate C1 — the real temperature field (mode="climate").

Pins: legacy mode is bit-exact (temperature = latitudinal placeholder, temp_seas_amp = 0); climate mode applies
elevation lapse (montane cools) + a latitude-rising, maritime-damped seasonal half-amplitude. Blueprint
`…_ClimateEconomy_Scoping.md` C1; RT: the temperature field is otherwise demographically inert.
"""
import numpy as np

from sic_games.terrain import (generate_world, world_lottery, LAPSE_C_PER_KM, N, miami_npp, NPP_GM2_SCALE,
                               whittaker_biome, BIOME_FOREST, BIOME_SAVANNA, BIOME_GRASS, BIOME_DESERT)


def _k(arch="montane", seed=0):
    return world_lottery(seed, archetype=arch)


def test_legacy_default_bit_exact():
    """Default mode == explicit legacy; temperature identical to the historical latitudinal field; amp = 0."""
    k = _k()
    a = generate_world(k)
    b = generate_world(k, mode="legacy")
    assert np.array_equal(a.temperature, b.temperature)
    assert np.array_equal(a.temp_seas_amp, b.temp_seas_amp)
    assert np.all(a.temp_seas_amp == 0.0)
    # legacy temperature is uniform across each row (pure latitudinal)
    assert np.allclose(a.temperature, a.temperature[:, :1])


def test_legacy_temperature_unchanged_by_new_code():
    """The legacy latitudinal field must be untouched by the C1 addition (row-only gradient, warm→cold)."""
    a = generate_world(_k())
    col = a.temperature[:, 0]
    assert col[0] > col[-1]                       # equator (row 0) warmer than pole edge
    assert np.all(np.diff(col) <= 1e-9)           # monotone non-increasing with latitude


def test_climate_mode_elevation_lapse_dominates_variability():
    """Regional model: within a climate world, high-elevation cells are markedly colder than low-elevation cells
    (elevation, not latitude, is the big spatial driver). The lapse enters as −6.5·elev_m/1000."""
    k = _k("montane")
    C = generate_world(k, mode="climate")
    land = (C.isWater == 0)
    hi = land & (C.elev > 0.6)
    lo = land & (C.elev < 0.2)
    if hi.any() and lo.any():
        assert C.temperature[hi].mean() < C.temperature[lo].mean() - 5.0    # ≥5 °C colder at elevation
    # spot-check the lapse relative to a flat (elev≈0) reference in the same column band
    ys, xs = np.where(hi)
    y, x = ys[0], xs[0]
    base_at_zero = C.temperature[y, x] + LAPSE_C_PER_KM * (C.elev[y, x] * C.reliefAmpM) / 1000.0
    assert 0.0 <= base_at_zero <= 30.0        # the de-lapsed base temperature is a sane regional value


def test_climate_seasonal_amplitude_rises_with_latitude_and_damps_near_water():
    """temp_seas_amp: ~0 at the equator, large at high latitude; reduced where wateracc is high (maritime)."""
    C = generate_world(_k("montane"), mode="climate")
    land = (C.isWater == 0)
    rows = np.arange(C.temperature.shape[0])[:, None]
    lowlat = land & (rows < 20)
    highlat = land & (rows > 80)
    assert C.temp_seas_amp[lowlat].mean() < C.temp_seas_amp[highlat].mean()
    assert C.temp_seas_amp[land].min() >= 0.0
    # maritime damping: among same-latitude-band cells, higher wateracc → lower amplitude
    band = land & (rows > 60) & (rows < 80)
    wa = C.wateracc[band]; amp = C.temp_seas_amp[band]
    if wa.std() > 0.05:
        wet = amp[wa > np.median(wa)].mean()
        dry = amp[wa <= np.median(wa)].mean()
        assert wet <= dry + 1e-9


# --------------------------------------------------------------------------- C2 precipitation

def _band(land, lo, hi):
    rows = np.arange(N)[:, None]
    return land & (rows >= lo) & (rows < hi)


def test_legacy_precip_zero_climate_nonzero():
    k = _k("mixed")
    assert np.all(generate_world(k).precip_mm == 0.0)                 # legacy: unused
    assert generate_world(k, mode="climate").precip_mm.max() > 0.0    # climate: real field


def _region_precip_cells(archetype, climate_latitude):
    k = dict(_k(archetype)); k["climate_latitude"] = climate_latitude
    C = generate_world(k, mode="climate")
    return C.precip_mm[C.isWater == 0]


def test_precip_hadley_itcz_across_regions():
    """The Hadley/ITCZ regime is set by the REGIONAL latitude: equatorial (~0.05) wet, subtropical (~0.30) DRY,
    mid-latitude (~0.70) wet again — in MEAN wetness (orography adds within-region variance on top)."""
    eq = _region_precip_cells("mixed", 0.05).mean()
    subtrop = _region_precip_cells("mixed", 0.30).mean()
    midlat = _region_precip_cells("mixed", 0.70).mean()
    assert eq > subtrop            # equatorial ITCZ region wetter than the subtropical desert belt
    assert midlat > subtrop        # mid-latitude storm track wetter than the subtropical trough


def test_precip_range_earthlike_across_regions():
    """Across regional latitudes + orography the ensemble spans desert → rainforest: the equatorial region has
    rainforest-wet cells, the subtropical region has desert-dry cells (lee/lowland), and it's drier overall."""
    trop = _region_precip_cells("mixed", 0.05)
    subtrop = _region_precip_cells("mixed", 0.30)
    assert trop.max() > 2000                      # equatorial region reaches rainforest-wet somewhere
    assert np.percentile(subtrop, 10) < 500       # subtropical region has desert-dry cells (rain-shadow/lowland)
    assert trop.mean() > subtrop.mean()           # equatorial wetter overall


def test_precip_orographic_windward_wetter():
    """Rain-shadow sign: precipitation correlates positively with the up-wind (eastward) elevation gradient."""
    C = generate_world(_k("montane"), mode="climate")
    land = (C.isWater == 0)
    band = _band(land, 40, 70)
    grad = (C.elev - np.roll(C.elev, 1, axis=1))[band]
    p = C.precip_mm[band]
    if grad.std() > 1e-3:
        assert np.corrcoef(grad, p)[0, 1] > 0.0      # windward (rising eastward) wetter than lee


# --------------------------------------------------------------------------- C3 Miami NPP

def test_legacy_npp_bit_exact():
    """The C3 reorder must leave legacy NPP/npp_gm2 byte-identical."""
    k = _k("mixed")
    a = generate_world(k)
    b = generate_world(k, mode="legacy")
    assert np.array_equal(a.npp, b.npp)
    assert np.array_equal(a.npp_gm2, b.npp_gm2)


def test_miami_helper_cold_or_dry_limits():
    """Miami = min(temp-limb, precip-limb): cold OR dry both cap NPP; warm+wet is high; monotone in each."""
    assert miami_npp(-5, 2000) < 500          # cold-limited (tundra) despite ample rain
    assert miami_npp(28, 150) < 500           # precip-limited (desert) despite heat
    assert miami_npp(28, 2500) > 2000         # warm + wet → rainforest
    assert miami_npp(15, 1200) > 1000         # temperate forest
    assert miami_npp(20, 800) > miami_npp(20, 300)     # monotone up in precip
    assert miami_npp(20, 1500) > miami_npp(2, 1500)    # monotone up in temperature (in the growth range)


def test_climate_npp_is_miami_of_TP():
    """Under climate mode npp_gm2 == Miami(temperature, precip) on land (0 on water)."""
    C = generate_world(_k("montane"), mode="climate")
    land = (C.isWater == 0)
    expect = miami_npp(C.temperature, C.precip_mm)
    assert np.allclose(C.npp_gm2[land], expect[land], rtol=1e-9, atol=1e-6)
    assert np.all(C.npp_gm2[C.isWater == 1] == 0.0)
    # npp (normalised) = npp_gm2 / NPP_GM2_SCALE and stays ≤ ~0.88 (Miami ≤ 3000 < 3400)
    assert np.allclose(C.npp[land], C.npp_gm2[land] / NPP_GM2_SCALE)
    assert C.npp[land].max() <= 3000.0 / NPP_GM2_SCALE + 1e-9


def test_climate_npp_cold_highlands_low():
    """Cold high-elevation cells (low NPP_T) are low-NPP even if wet — the elevation effect enters via temperature."""
    C = generate_world(_k("montane"), mode="climate")
    land = (C.isWater == 0)
    cold = land & (C.temperature < 5.0)
    warm = land & (C.temperature > 15.0)
    if cold.any() and warm.any():
        assert C.npp_gm2[cold].mean() < C.npp_gm2[warm].mean()


# --------------------------------------------------------------------------- C4 Whittaker biome

def test_whittaker_helper_climate_biomes():
    """Whittaker(T,P): warm+wet→forest, warm+seasonal→savanna, warm+arid→desert, cool+moderate→grass; cold+wet→
    forest (taiga), cold+arid→desert."""
    assert whittaker_biome(26, 2500) == BIOME_FOREST
    assert whittaker_biome(24, 800) == BIOME_SAVANNA
    assert whittaker_biome(20, 250) == BIOME_DESERT
    assert whittaker_biome(8, 700) == BIOME_GRASS
    assert whittaker_biome(3, 1200) == BIOME_FOREST      # taiga
    assert whittaker_biome(0, 150) == BIOME_DESERT       # cold desert


def test_whittaker_desert_forest_thresholds_rise_with_temperature():
    """Warmer needs more rain for the same class (evapotranspiration): the desert→grass and grass→forest edges
    shift to higher P as T rises."""
    # a P that is 'forest' when cool becomes 'grass/savanna' when hot (higher forest threshold)
    assert whittaker_biome(5, 700) == BIOME_FOREST
    assert whittaker_biome(28, 700) != BIOME_FOREST
    # a P that is 'grass' when cool becomes 'desert' when hot (higher desert threshold)
    assert whittaker_biome(2, 300) != BIOME_DESERT
    assert whittaker_biome(28, 300) == BIOME_DESERT


def test_climate_biome_emerges_from_regional_climate():
    """On FLAT terrain the biome follows the regional climate: tropical→forest-dominant, subtropical→dry
    (desert/savanna/grass, little forest), temperate→forest+grass mosaic."""
    from collections import Counter
    base = dict(world_lottery(0, archetype="forest")); base["relief"] = 0.08
    def frac(cl, code):
        k = dict(base); k["climate_latitude"] = cl
        b = generate_world(k, mode="climate").biome
        land = b[generate_world(k, mode="climate").isWater == 0]
        return np.mean(land == code)
    assert frac(0.08, BIOME_FOREST) > 0.7                       # tropical → rainforest-dominant
    subtrop_dry = frac(0.30, BIOME_DESERT) + frac(0.30, BIOME_SAVANNA) + frac(0.30, BIOME_GRASS)
    assert subtrop_dry > 0.6                                    # subtropical → dry (open) biomes dominate
    assert frac(0.30, BIOME_FOREST) < 0.3                       # subtropical → little forest


def test_world_lottery_climate_terrain_x_climate():
    """Independent terrain × climate draws → emergent biomes: flat-tropical = forest, flat-subtropical = desert."""
    from collections import Counter
    from sic_games.terrain import world_lottery_climate

    def dominant(terr, clim):
        k = world_lottery_climate(0, terrain=terr, climate=clim)
        assert k["mode"] == "climate"
        f = generate_world(k, mode="climate")
        land = f.biome[f.isWater == 0]
        return Counter(int(x) for x in land).most_common(1)[0][0]

    assert dominant("flat", "tropical") == BIOME_FOREST        # rainforest world
    assert dominant("flat", "subtropical") == BIOME_DESERT     # desert world (aridity + Hadley descent)


def test_c6_river_source_temperature():
    """C6: river water temperature carries the cold of its montane HEADWATER (snowmelt), so a montane world's rivers
    read COLDER than the local air, while a flat world's rivers ≈ local air. Legacy water_temp is 0."""
    from sic_games.terrain import world_lottery_climate
    # legacy: water_temp field is zero (unused)
    assert np.all(generate_world(_k("montane")).water_temp == 0.0)
    mtn = generate_world(world_lottery_climate(0, terrain="mountainous", climate="temperate"), mode="climate")
    flat = generate_world(world_lottery_climate(0, terrain="flat", climate="temperate"), mode="climate")
    for F, cold_gap in ((mtn, 1.5), (flat, None)):
        riv = F.isRiver.astype(bool)
        if not riv.any():
            continue
        gap = F.temperature[riv].mean() - F.water_temp[riv].mean()      # air − water (positive = water colder)
        if cold_gap is not None:
            assert gap > cold_gap                                        # montane rivers markedly colder than air
        else:
            assert abs(gap) < 1.0                                        # flat rivers ≈ air temp
    # water is never warmer than air (headwater cooling only cools)
    assert np.all(mtn.water_temp <= mtn.temperature + 1e-9)


def test_c6_montane_rivers_more_salmon_capable_than_air_suggests():
    """A tropical MONTANE world has cold (salmon-capable, <16 °C) rivers via headwater sourcing, even though its air
    is warm — so water-temp gives MORE cold rivers than air-temp would."""
    from sic_games.terrain import world_lottery_climate
    F = generate_world(world_lottery_climate(0, terrain="mountainous", climate="tropical"), mode="climate")
    riv = F.isRiver.astype(bool)
    if riv.any():
        by_air = (F.temperature[riv] < 16.0).mean()
        by_water = (F.water_temp[riv] < 16.0).mean()
        assert by_water > by_air + 0.1                                   # headwater sourcing opens up cold-water rivers


def test_gd1_deplete_and_recover():
    """GD-1: a cell foraged hard hunts out (yield → floor) and recovers over a fallow; default OFF ⇒ static field."""
    from sic_games.terrain import world_lottery_climate
    from sic_games.capacity import NPPCapacityField
    k = world_lottery_climate(0, terrain="flat", climate="temperate")
    F = generate_world(k, mode="climate")
    burn = 75000.0
    ys, xs = np.where((F.isWater == 0) & (F.npp_gm2 > 800))
    x, y = int(xs[0]), int(ys[0])
    # depletion OFF ⇒ deplete_and_regrow is a no-op (static)
    off = NPPCapacityField(F, burn, mode="tallavaara", enable_depletion=False)
    y0 = off.level(x, y)
    off.deplete_and_regrow({(x, y): 500}, 1.0)
    assert off.level(x, y) == y0                              # no-op when disabled

    on = NPPCapacityField(F, burn, mode="tallavaara", enable_depletion=True)
    full = on.level(x, y)
    for _ in range(24):
        on.deplete_and_regrow({(x, y): 200}, 1.0)            # 2 yr heavy foraging
    hunted = on.level(x, y)
    for _ in range(120):
        on.deplete_and_regrow({}, 1.0)                       # fallow
    recovered = on.level(x, y)
    assert hunted < full * 0.5                                # hunted-out
    assert recovered > hunted * 1.5                           # recovers over fallow


def test_c8_aquatic_capacity_subsidy():
    """C8: aquatic=True adds capacity on aquatic cells (super-terrestrial) but leaves interior (aquatic_food=0)
    byte-identical; aquatic=False ⇒ base field unchanged."""
    from sic_games.terrain import world_lottery_climate
    from sic_games.capacity import NPPCapacityField, AQUATIC_DENSITY_MAX
    F = generate_world(world_lottery_climate(0, terrain="mountainous", climate="tropical"), mode="climate")
    burn = 75000.0
    off = NPPCapacityField(F, burn, mode="tallavaara", aquatic=False)
    on = NPPCapacityField(F, burn, mode="tallavaara", aquatic=True)
    interior = (F.isWater == 0) & (F.aquatic_food == 0)
    aquatic = (F.isWater == 0) & (F.aquatic_food > 0.3)
    assert np.array_equal(off._E[interior], on._E[interior])                 # interior bit-exact
    if aquatic.any():
        assert (on._E[aquatic] > off._E[aquatic]).all()                      # aquatic cells subsidised
        # a full aquatic cell (aq=1) gets ~+AQUATIC_DENSITY_MAX persons/cell
        full = (F.aquatic_food > 0.95) & (F.isWater == 0)
        if full.any():
            gained = (on._E[full] - off._E[full]) / burn
            assert abs(gained.mean() - AQUATIC_DENSITY_MAX) < 1.0


def test_c7_aquatic_food_helper():
    """aquatic_food_field: cold sea-connected river → anadromous; warm river → less; shore → shellfish; dry interior → 0."""
    from sic_games.terrain import aquatic_food_field
    z = np.zeros((5, 5)); water_cold = np.full((5, 5), 8.0); water_warm = np.full((5, 5), 25.0)
    river = np.zeros((5, 5), np.uint8); river[2, 2] = 1
    shore = np.zeros((5, 5), np.uint8); shore[0, 0] = 1
    sea = np.ones((5, 5), bool); npp01 = np.full((5, 5), 0.5)
    cold = aquatic_food_field(water_cold, river, np.zeros((5, 5), np.uint8), sea, npp01)
    warm = aquatic_food_field(water_warm, river, np.zeros((5, 5), np.uint8), sea, npp01)
    assert cold[2, 2] > 0.8                         # cold river cell = strong anadromous
    assert warm[2, 2] < cold[2, 2]                  # warm river = weaker (salmon lethal)
    sh = aquatic_food_field(water_warm, np.zeros((5, 5), np.uint8), shore, sea, npp01)
    assert sh[0, 0] > 0.3                            # coastal shore = shellfish (warm-tolerant)
    interior = aquatic_food_field(water_warm, np.zeros((5, 5), np.uint8), np.zeros((5, 5), np.uint8), sea, npp01)
    assert np.all(interior == 0.0)                   # no river, no shore → no aquatic food


def test_c7_aquatic_food_rare_and_water_linked():
    """The aquatic-food field is 0 in legacy, rare in climate, and concentrated on cold rivers + shores."""
    from sic_games.terrain import world_lottery_climate
    assert np.all(generate_world(_k("montane")).aquatic_food == 0.0)               # legacy: unused
    F = generate_world(world_lottery_climate(0, terrain="mountainous", climate="tropical"), mode="climate")
    land = (F.isWater == 0)
    assert F.aquatic_food[land].max() > 0.5                                          # some genuinely rich fishery cells
    assert (F.aquatic_food[land] > 0.3).mean() < 0.25                               # but RARE (water-linked, not everywhere)
    riv = F.isRiver.astype(bool) & land
    if riv.any():                                                                   # cold rivers richer than warm rivers
        cold = riv & (F.water_temp < 16); warm = riv & (F.water_temp >= 16)
        if cold.any() and warm.any():
            assert F.aquatic_food[cold].mean() > F.aquatic_food[warm].mean()


def test_world_lottery_climate_aridity_dries_precip():
    """The climate_aridity axis scales precip down independent of latitude (continental/leeward dryness)."""
    from sic_games.terrain import world_lottery_climate
    humid = dict(world_lottery_climate(0, terrain="flat", climate="temperate")); humid["climate_aridity"] = 0.0
    arid = dict(humid); arid["climate_aridity"] = 0.9
    ph = generate_world(humid, mode="climate").precip_mm
    pa = generate_world(arid, mode="climate").precip_mm
    assert pa[pa > 0].mean() < ph[ph > 0].mean() * 0.7         # aridity markedly reduces precip
