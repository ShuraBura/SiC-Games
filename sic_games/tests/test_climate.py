"""Climate C.1 — obliquity→seasonal-amplitude lottery + the ClimateField wrapper.

Locks: (1) the obliquity→amplitude map (Earth ε→Earth amplitude, monotone, clamped); (2) the seasonal multiplier
is the EXACT validated R-6 form (range [s_min,1], peak-normalized); (3) A_seas=0 ⇒ aseasonal baseline bit-exact;
(4) the model advances the climate clock (set_step) each step; (5) field delegation.
"""
from __future__ import annotations
import math
import random
import numpy as np

from sic_games.climate import (
    ClimateField, obliquity_to_amplitude, draw_obliquity, A_SEAS_EARTH, OBLIQUITY_EARTH_DEG,
    eccentricity_mean_factor, draw_eccentricity, draw_stellar_flux, flux_to_temperature, draw_world_climate,
    ECCENTRICITY_MAX, STELLAR_FLUX_MIN, STELLAR_FLUX_MAX,
    REGIME_AMP_MIN, REGIME_AMP_MAX, REGIME_DURATION_MIN_YR, REGIME_RECURRENCE_MAX_YR,
    CARIBOU_AMP_ABOUT_MEAN, CARIBOU_PERIOD_MIN_YR, CARIBOU_PERIOD_MAX_YR,
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


# ── C.3: regime-shift telegraph (two-state Markov / sustained plateau) ─────────
def test_regime_off_nests_to_c2():
    # regime_amp=0 ⇒ regime()≡1 ⇒ identical to C.2 (no Layer-3 effect)
    c2 = ClimateField(_MockField(), a_seas=0.6, interannual_amp=0.3, interannual_period=48)
    c3 = ClimateField(_MockField(), a_seas=0.6, interannual_amp=0.3, interannual_period=48, regime_amp=0.0)
    for t in range(24):
        c2.set_step(t); c3.set_step(t)
        assert abs(c2.level(2, 2) - c3.level(2, 2)) < 1e-12


def test_regime_excursion_is_a_sustained_plateau():
    # Force the chain into the excursion state: the level holds a FLAT depressed plateau (NOT a mean-reverting
    # wiggle). Seasonal/interannual off to isolate Layer 3.
    f = ClimateField(_MockField(), a_seas=0.0, regime_amp=0.12, regime_duration=3600, regime_recurrence=18000,
                     rng=random.Random(0))
    f._regime_state = 1                                                  # in an excursion
    levels = []
    for t in range(1, 200):                                             # short window vs 3600-step dwell → stays on
        f.set_step(t); levels.append(f.level(1, 1))
    assert all(abs(v - 88.0) < 1e-9 for v in levels)                    # 100 × (1 − 0.12), perfectly flat plateau
    assert max(levels) - min(levels) < 1e-9                             # zero variance = a plateau, not a wiggle


def test_telegraph_occupancy_matches_duty_cycle():
    # Long run: excursion-state occupancy ≈ duration/(duration+recurrence); dwell ≫ a generation.
    dur, rec = 240, 1200                                                # 20-yr / 100-yr (scaled for a fast test)
    f = ClimateField(_MockField(), a_seas=0.0, regime_amp=0.1, regime_duration=dur, regime_recurrence=rec,
                     rng=random.Random(42))
    occ = 0; N = 400_000
    for t in range(1, N + 1):
        f.set_step(t); occ += f._regime_state
    expected = dur / (dur + rec)                                        # ≈ 0.1667
    assert abs(occ / N - expected) < 0.03
    assert dur >= 12 * 15                                                # excursion ≫ ~15-yr generation (multi-gen)


def test_draw_world_climate_regime_keys_and_ranges():
    rng = random.Random(11)
    d = draw_world_climate(rng, a_earth=A_SEAS_EARTH["savanna"])
    for k in ("regime_amp", "regime_duration", "regime_recurrence"):
        assert k in d
    assert REGIME_AMP_MIN <= d["regime_amp"] <= REGIME_AMP_MAX          # central band (tails reserved for C.4)
    assert d["regime_duration"] < d["regime_recurrence"]               # duration ≠ recurrence (v2 fix)
    assert 100 * 12 <= d["regime_duration"] <= 500 * 12
    assert 1000 * 12 <= d["regime_recurrence"] <= int(REGIME_RECURRENCE_MAX_YR * 12)
    assert d["regime_duration"] >= 12 * int(REGIME_DURATION_MIN_YR)    # ≥100 yr ≫ generation


# ── C.4b: caribou herd-swing (meat-channel quasi-cycle on GRASS_STEPPE) ───────
def test_caribou_off_meat_factor_is_one():
    # amp=0 OR no mask ⇒ meat_factor ≡ 1 (back-compat: the economy multiplies meat by 1.0)
    f0 = ClimateField(_MockField(), caribou_amp=0.0)
    assert f0.meat_factor(5, 5) == 1.0
    mask = np.ones((40, 40), dtype=bool)
    fn = ClimateField(_MockField(), caribou_amp=0.871, caribou_period=480, steppe_mask=None)
    assert fn.meat_factor(5, 5) == 1.0                                  # mask None ⇒ inert even with amp>0


def test_caribou_depresses_steppe_cells_only():
    mask = np.zeros((40, 40), dtype=bool)
    mask[7, 3] = True                                                   # one steppe cell at (x=3, y=7)
    f = ClimateField(_MockField(), caribou_amp=0.871, caribou_period=480,
                     caribou_phase=math.pi, steppe_mask=mask)           # phase=π ⇒ t=0 is the trough
    f.set_step(0)
    assert f.meat_factor(2, 2) == 1.0                                   # non-steppe cell untouched
    a = 0.871
    assert abs(f.meat_factor(3, 7) - (1.0 - a) / (1.0 + a)) < 1e-12    # steppe trough = (1-a)/(1+a) ≈ 0.069


def test_caribou_peak_pinned_and_bounded():
    mask = np.ones((40, 40), dtype=bool)
    f = ClimateField(_MockField(), caribou_amp=0.871, caribou_period=480, caribou_phase=0.0, steppe_mask=mask)
    a = 0.871; lo = (1.0 - a) / (1.0 + a)
    vals = []
    for t in range(480):
        f.set_step(t); vals.append(f.meat_factor(1, 1))
    assert abs(max(vals) - 1.0) < 1e-9                                  # peak pinned to 1.0
    assert abs(min(vals) - lo) < 1e-3                                   # trough ≈ 0.069
    assert all(lo - 1e-9 <= v <= 1.0 + 1e-9 for v in vals)             # bounded


def test_caribou_does_not_touch_forage_or_capacity():
    # meat_factor is a SEPARATE accessor; level()/mult() (forage capacity) are unaffected by the caribou layer.
    mask = np.ones((40, 40), dtype=bool)
    f = ClimateField(_MockField(), a_seas=0.0, caribou_amp=0.871, caribou_period=480,
                     caribou_phase=math.pi, steppe_mask=mask)
    f.set_step(0)
    assert f.level(1, 1) == 100.0 and f.mult() == 1.0                  # capacity/forage untouched at caribou trough


def test_draw_world_climate_caribou_keys_and_ranges():
    d = draw_world_climate(random.Random(3), a_earth=A_SEAS_EARTH["savanna"])
    assert d["caribou_amp"] == CARIBOU_AMP_ABOUT_MEAN                   # fixed empirical anchor (0.871)
    assert int(CARIBOU_PERIOD_MIN_YR * 12) <= d["caribou_period"] <= int(CARIBOU_PERIOD_MAX_YR * 12)   # 480–1080


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
