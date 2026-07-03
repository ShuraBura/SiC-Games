"""Economy-from-Climate C1 — the real temperature field (mode="climate").

Pins: legacy mode is bit-exact (temperature = latitudinal placeholder, temp_seas_amp = 0); climate mode applies
elevation lapse (montane cools) + a latitude-rising, maritime-damped seasonal half-amplitude. Blueprint
`…_ClimateEconomy_Scoping.md` C1; RT: the temperature field is otherwise demographically inert.
"""
import numpy as np

from sic_games.terrain import generate_world, world_lottery, LAPSE_C_PER_KM, N, miami_npp, NPP_GM2_SCALE


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


def _region_precip(archetype, climate_latitude):
    k = dict(_k(archetype)); k["climate_latitude"] = climate_latitude
    C = generate_world(k, mode="climate")
    land = (C.isWater == 0)
    return C.precip_mm[land].mean()


def test_precip_hadley_itcz_across_regions():
    """The Hadley/ITCZ regime is set by the REGIONAL latitude: equatorial (~0.05) wet, subtropical (~0.30) DRY,
    mid-latitude (~0.70) wet again. (Within a 1000 km grid the profile is regional, not a full transect.)"""
    eq = _region_precip("mixed", 0.05)
    subtrop = _region_precip("mixed", 0.30)
    midlat = _region_precip("mixed", 0.70)
    assert eq > subtrop * 2            # equatorial ITCZ much wetter than the subtropical desert belt
    assert midlat > subtrop            # mid-latitude storm track wetter than the subtropical trough
    assert subtrop < 700               # subtropical region is desert-dry


def test_precip_range_earthlike_across_regions():
    """Across regional latitudes the ensemble spans desert → rainforest (a single region is narrower)."""
    wettest = _region_precip("mixed", 0.05)      # equatorial region
    driest = _region_precip("mixed", 0.30)       # subtropical region
    assert wettest > 1500                        # equatorial region reaches rainforest-wet
    assert driest < 600                          # subtropical region is desert-dry


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
