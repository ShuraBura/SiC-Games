"""Economy-from-Climate C1 — the real temperature field (mode="climate").

Pins: legacy mode is bit-exact (temperature = latitudinal placeholder, temp_seas_amp = 0); climate mode applies
elevation lapse (montane cools) + a latitude-rising, maritime-damped seasonal half-amplitude. Blueprint
`…_ClimateEconomy_Scoping.md` C1; RT: the temperature field is otherwise demographically inert.
"""
import numpy as np

from sic_games.terrain import generate_world, world_lottery, LAPSE_C_PER_KM


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


def test_climate_mode_applies_elevation_lapse():
    """Climate mode cools cells by elevation lapse → high-elevation cells markedly colder than legacy."""
    k = _k("montane")
    L = generate_world(k)
    C = generate_world(k, mode="climate")
    land = (C.isWater == 0)
    hi = land & (C.elev > 0.5)
    assert C.temperature[hi].mean() < L.temperature[hi].mean() - 3.0     # ≥3 °C colder at elevation
    # the lapse is exactly latitudinal minus 6.5·elev_m/1000 (spot-check a land cell)
    ys, xs = np.where(land)
    y, x = ys[len(ys) // 2], xs[len(xs) // 2]
    expected = L.temperature[y, x] - LAPSE_C_PER_KM * (C.elev[y, x] * C.reliefAmpM) / 1000.0
    assert abs(C.temperature[y, x] - expected) < 1e-9


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
