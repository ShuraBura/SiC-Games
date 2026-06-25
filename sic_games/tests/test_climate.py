"""Climate C.1 — obliquity→seasonal-amplitude lottery + the ClimateField wrapper.

Locks: (1) the obliquity→amplitude map (Earth ε→Earth amplitude, monotone, clamped); (2) the seasonal multiplier
is the EXACT validated R-6 form (range [s_min,1], peak-normalized); (3) A_seas=0 ⇒ aseasonal baseline bit-exact;
(4) the model advances the climate clock (set_step) each step; (5) field delegation.
"""
from __future__ import annotations
import math
import random

from sic_games.climate import (
    ClimateField, obliquity_to_amplitude, draw_obliquity, A_SEAS_EARTH, OBLIQUITY_EARTH_DEG,
    eccentricity_mean_factor, draw_eccentricity, draw_stellar_flux, flux_to_temperature, draw_world_climate,
    ECCENTRICITY_MAX, STELLAR_FLUX_MIN, STELLAR_FLUX_MAX,
)
from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


class _MockField:
    width = 40
    height = 40
    def level(self, x, y):
        return 100.0
    def consume(self, occ):
        self._consumed = True


# ── obliquity → amplitude (Q1-B mapping) ──────────────────────────────────────
def test_earth_obliquity_gives_earth_amplitude():
    for biome, a in A_SEAS_EARTH.items():
        assert abs(obliquity_to_amplitude(OBLIQUITY_EARTH_DEG, a) - a) < 1e-9


def test_amplitude_monotone_and_clamped():
    a_e = 0.4
    assert obliquity_to_amplitude(0.0, a_e) == 0.0                      # no tilt → no seasons
    assert obliquity_to_amplitude(10.0, a_e) < obliquity_to_amplitude(40.0, a_e)   # monotone in ε
    assert 0.0 <= obliquity_to_amplitude(60.0, 0.9) <= 1.0             # clamped to [0,1]


def test_draw_obliquity_in_envelope():
    rng = random.Random(0)
    vals = [draw_obliquity(rng) for _ in range(200)]
    assert all(0.0 <= v <= 60.0 for v in vals) and max(vals) > 40.0


# ── ClimateField seasonal multiplier = the R-6 form ───────────────────────────
def test_aseasonal_baseline_is_exact():
    f = ClimateField(_MockField(), a_seas=0.0)
    for t in range(24):
        f.set_step(t)
        assert f.season() == 1.0 and f.level(3, 3) == 100.0            # A_seas=0 ⇒ M≡1, level == base


def test_seasonal_matches_R6_form():
    # A_seas=0.6 ⇔ s_min=0.4 — the validated R-6 multiplier: s(t)=s_min+(1-s_min)·½(1+cos(2πt/12))
    f = ClimateField(_MockField(), a_seas=0.6)
    s_min = 0.4
    for t in range(13):
        f.set_step(t)
        expect = s_min + (1.0 - s_min) * 0.5 * (1.0 + math.cos(2.0 * math.pi * t / 12.0))
        assert abs(f.season() - expect) < 1e-12
    f.set_step(0);  assert abs(f.season() - 1.0) < 1e-12               # peak
    f.set_step(6);  assert abs(f.season() - 0.4) < 1e-12               # trough = s_min


def test_field_delegates_and_scales():
    f = ClimateField(_MockField(), a_seas=0.6)
    assert f.width == 40 and f.height == 40                            # delegated
    f.set_step(6)
    assert abs(f.level(1, 1) - 40.0) < 1e-9                            # 100 × trough(0.4)
    f.consume({})                                                      # delegated method works


# ── C.2: eccentricity, flux, interannual ──────────────────────────────────────
def test_eccentricity_mean_factor():
    assert eccentricity_mean_factor(0.0) == 1.0                        # circular → no brightening
    assert abs(eccentricity_mean_factor(0.017) - 1.0) < 1e-3          # Earth ~negligible
    assert abs(eccentricity_mean_factor(0.6) - 1.25) < 0.01          # (1-0.36)^-0.5 = 1.25
    assert eccentricity_mean_factor(0.3) > eccentricity_mean_factor(0.1)   # monotone


def test_flux_to_temperature():
    assert abs(flux_to_temperature(1.0) - 14.0) < 1e-9               # S=1 anchored to 14°C
    assert flux_to_temperature(1.05) > 14.0 and flux_to_temperature(0.5) < 14.0   # warmer / colder, monotone


def test_draws_in_range():
    rng = random.Random(1)
    es = [draw_eccentricity(rng) for _ in range(100)]
    Ss = [draw_stellar_flux(rng) for _ in range(100)]
    assert all(0.0 <= e <= ECCENTRICITY_MAX for e in es)
    assert all(STELLAR_FLUX_MIN <= s <= STELLAR_FLUX_MAX for s in Ss)


def test_interannual_depresses_bounded():
    f = ClimateField(_MockField(), a_seas=0.0, interannual_amp=0.3, interannual_period=48)  # 4-yr ENSO
    vals = [f.interannual() for f.t in range(48)]
    assert min(vals) >= 1.0 - 0.3 - 1e-9 and max(vals) <= 1.0 + 1e-9   # ∈ [1-amp, 1] (depression only)
    assert min(vals) < 0.99                                            # it does depress some years


def test_c2_defaults_nest_to_c1():
    # mean_factor=1, interannual_amp=0 (C.2 defaults) ⇒ identical to C.1 (level == base·season)
    c1 = ClimateField(_MockField(), a_seas=0.6)
    c2 = ClimateField(_MockField(), a_seas=0.6, mean_factor=1.0, interannual_amp=0.0)
    for t in range(24):
        c1.set_step(t); c2.set_step(t)
        assert abs(c1.level(2, 2) - c2.level(2, 2)) < 1e-12


def test_mean_factor_scales_baseline():
    f = ClimateField(_MockField(), a_seas=0.0, mean_factor=1.25)       # high-e brightening
    f.set_step(0)
    assert abs(f.level(1, 1) - 125.0) < 1e-9                           # 100 × 1.25 (aseasonal, brightened)


def test_draw_world_climate_keys_and_ranges():
    rng = random.Random(7)
    d = draw_world_climate(rng, a_earth=A_SEAS_EARTH["llanos"])
    for k in ("a_seas", "mean_factor", "interannual_amp", "interannual_period", "mean_temperature",
              "obliquity", "eccentricity", "flux"):
        assert k in d
    assert 0.0 <= d["a_seas"] <= 1.0 and d["mean_factor"] >= 1.0
    assert 0.20 <= d["interannual_amp"] <= 0.40 and 24 <= d["interannual_period"] <= 84   # 2–7 yr × 12
    f = ClimateField(_MockField(), a_seas=d["a_seas"], mean_factor=d["mean_factor"],
                     interannual_amp=d["interannual_amp"], interannual_period=d["interannual_period"],
                     interannual_phase=d["interannual_phase"])
    f.set_step(3); assert f.level(1, 1) > 0.0                          # constructs + runs from the lottery


# ── model wiring: the climate clock advances each step ────────────────────────
def test_model_advances_climate_clock():
    w = TerrainWorld(n_agents=60, kcal_cfg=KcalEconomyConfig(), seed=3, game_stream=False,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     demography_cfg=DemographyConfig())
    w._harvest_field = ClimateField(w.terrain_field, a_seas=0.6)       # wrap after construction
    for _ in range(5):
        w.step()
    assert w._harvest_field.t == w.step_count == 5                     # model drove set_step
