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
    ClimateField, ClimateDriver, obliquity_to_amplitude, draw_obliquity, A_SEAS_EARTH, OBLIQUITY_EARTH_DEG,
    eccentricity_mean_factor, draw_eccentricity, draw_stellar_flux, flux_to_temperature, draw_world_climate,
    ECCENTRICITY_MAX, STELLAR_FLUX_MIN, STELLAR_FLUX_MAX,
    REGIME_AMP_MIN, REGIME_AMP_MAX, REGIME_DURATION_MIN_YR, REGIME_RECURRENCE_MAX_YR,
    CARIBOU_AMP_ABOUT_MEAN, CARIBOU_PERIOD_MIN_YR, CARIBOU_PERIOD_MAX_YR,
    LLANOS_FLOOD_AMP, LLANOS_FLOOD_AMP_MIN, LLANOS_FLOOD_AMP_MAX,
    INTERCEPT_BOOST, INTERCEPT_DRY_THRESHOLD,
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


# ── C.4c: llanos flood (two-sided interannual tail on GRASS_LLANOS forage) ────
def test_llanos_off_nests_to_generic_interannual():
    # llanos_flood_amp=0 OR no mask ⇒ level() uses the generic one-sided ENSO (== C.3, bit-exact)
    base_kw = dict(interannual_amp=0.3, interannual_period=48)
    c3 = ClimateField(_MockField(), **base_kw)
    c4 = ClimateField(_MockField(), **base_kw, llanos_flood_amp=0.0, llanos_mask=np.ones((40, 40), bool))
    for t in range(48):
        c3.set_step(t); c4.set_step(t)
        assert abs(c3.level(2, 2) - c4.level(2, 2)) < 1e-12


def test_llanos_flood_is_two_sided_only_on_llanos():
    mask = np.zeros((40, 40), dtype=bool)
    mask[5, 5] = True                                                  # one llanos cell at (x=5, y=5)
    f = ClimateField(_MockField(), interannual_amp=0.3, interannual_period=48, interannual_phase=0.0,
                     llanos_flood_amp=0.45, llanos_mask=mask)
    # llanos cell: depressed at BOTH flood extremes (sin=+1 at t=12, sin=−1 at t=36), best at sin=0 (t=0)
    f.set_step(0);  assert abs(f.level(5, 5) - 100.0) < 1e-9          # median flood → no stress
    f.set_step(12); assert abs(f.level(5, 5) - 55.0) < 1e-9          # over-flood (sin=+1) → 1−0.45
    f.set_step(36); assert abs(f.level(5, 5) - 55.0) < 1e-9          # failed-flood (sin=−1) → 1−0.45 (TWO-sided)
    # non-llanos cell: generic ONE-sided ENSO (amp 0.3) — depressed only on the sin>0 half
    f.set_step(12); assert abs(f.level(1, 1) - 70.0) < 1e-9          # 100·(1−0.3)
    f.set_step(36); assert abs(f.level(1, 1) - 100.0) < 1e-9         # sin<0 ⇒ no ENSO depression (one-sided)


def test_llanos_does_not_touch_meat_factor():
    # C.4c hits forage capacity (level); the caribou meat channel is independent and stays 1.0 here.
    mask = np.ones((40, 40), dtype=bool)
    f = ClimateField(_MockField(), interannual_amp=0.0, interannual_period=48,
                     llanos_flood_amp=0.45, llanos_mask=mask)
    f.set_step(12)
    assert f.level(3, 3) < 100.0                                      # forage depressed by the flood
    assert f.meat_factor(3, 3) == 1.0                                 # no caribou config ⇒ meat untouched


def test_draw_world_climate_llanos_key():
    # llanos flood amplitude is DRAWN per-world over the lit-bounded band [0.15, 0.45] (Castello/Welcomme/Apure)
    for s in range(50):
        d = draw_world_climate(random.Random(s), a_earth=A_SEAS_EARTH["llanos"])
        assert LLANOS_FLOOD_AMP_MIN <= d["llanos_flood_amp"] <= LLANOS_FLOOD_AMP_MAX


# ── C.5: intercept-hunting meat boost at water (late dry season, savanna+llanos) ──
def _intercept_field(a_seas=0.6, on=True, seed=0):
    N = 40
    ww = np.random.RandomState(seed).rand(N, N)               # synthetic wateracc ∈ [0,1)
    mask = np.ones((N, N), bool)
    return ClimateField(_MockField(), a_seas=a_seas, water_weight=ww, agg_mask=mask, intercept_on=on), ww, mask


def test_intercept_off_meat_factor_is_one_and_forage_is_plain_seasonal():
    # flag off ⇒ no meat boost; and intercept (meat channel) never changes forage capacity vs the plain seasonal
    f, ww, mask = _intercept_field(on=False)
    plain = ClimateField(_MockField(), a_seas=0.6)              # same season, no C.5
    for t in (0, 3, 6, 9):
        f.set_step(t); plain.set_step(t)
        assert f.meat_factor(3, 3) == 1.0                       # flag off ⇒ no boost
        assert abs(f.level(3, 3) - plain.level(3, 3)) < 1e-12  # forage capacity == plain seasonal (intercept is meat-only)
    # and ON likewise leaves forage capacity identical (boost is meat-channel, not forage):
    fon, _, _ = _intercept_field(on=True)
    for t in (0, 3, 6, 9):
        fon.set_step(t); plain.set_step(t)
        assert abs(fon.level(3, 3) - plain.level(3, 3)) < 1e-12


def test_intercept_default_on():
    f, ww, mask = _intercept_field()                            # intercept_on defaults True
    assert f.intercept_on is True


def test_intercept_boost_at_water_late_dry_only():
    N = 40
    ww = np.zeros((N, N)); ww[5, :] = 1.0; ww[20, :] = 0.0       # row5 = at water, row20 = far
    mask = np.ones((N, N), bool)
    f = ClimateField(_MockField(), a_seas=0.6, water_weight=ww, agg_mask=mask)
    f.set_step(6)                                                # dry trough: dryness=(1−s)/A_seas = 1 ≥ threshold
    assert abs(f.meat_factor(3, 5) - (1.0 + INTERCEPT_BOOST)) < 1e-9   # AT water → full +44% boost
    assert f.meat_factor(3, 20) == 1.0                          # far from water → no boost
    f.set_step(0)                                                # wet peak: dryness=0 < threshold → gate OFF
    assert f.meat_factor(3, 5) == 1.0                           # no intercept in the wet season


def test_intercept_threshold_gate_is_late_dry_only():
    # boost only once normalized dryness crosses INTERCEPT_DRY_THRESHOLD (a late-dry window, not all dry season)
    N = 40
    ww = np.full((N, N), 1.0); mask = np.ones((N, N), bool)
    f = ClimateField(_MockField(), a_seas=0.6, water_weight=ww, agg_mask=mask)
    boosted = []
    for t in range(12):
        f.set_step(t)
        dryness = (1.0 - f.season()) / 0.6
        on = f.meat_factor(0, 0) > 1.0
        assert on == (dryness >= INTERCEPT_DRY_THRESHOLD)        # exactly the threshold gate
        boosted.append(on)
    assert 0 < sum(boosted) < 12                                # a WINDOW (late dry), not always / never


def test_intercept_only_aggregation_biomes_and_aseasonal_off():
    N = 40
    ww = np.full((N, N), 1.0)
    mask = np.zeros((N, N), bool); mask[5, :] = True            # only row 5 is an aggregation biome
    f = ClimateField(_MockField(), a_seas=0.6, water_weight=ww, agg_mask=mask)
    f.set_step(6)
    assert f.meat_factor(3, 5) > 1.0                           # agg biome at water in late dry → boost
    assert f.meat_factor(3, 10) == 1.0                         # off-biome → no boost
    f2 = ClimateField(_MockField(), a_seas=0.0, water_weight=ww, agg_mask=np.ones((N, N), bool))  # no season
    f2.set_step(6)
    assert f2.meat_factor(3, 3) == 1.0                         # no seasonality ⇒ no dry season ⇒ no intercept


def test_intercept_and_caribou_compose_on_disjoint_biomes():
    # a cell is steppe XOR savanna/llanos; meat_factor = caribou × intercept, each active only on its biome
    N = 40
    ww = np.full((N, N), 1.0)
    steppe = np.zeros((N, N), bool); steppe[10, :] = True       # row 10 = steppe (caribou)
    agg = np.zeros((N, N), bool);    agg[5, :] = True           # row 5 = savanna/llanos (intercept)
    f = ClimateField(_MockField(), a_seas=0.6, caribou_amp=0.871, caribou_period=480, caribou_phase=math.pi,
                     steppe_mask=steppe, water_weight=ww, agg_mask=agg)
    f.set_step(6)
    assert f.meat_factor(3, 5) > 1.0                           # intercept boost on the agg row
    a = 0.871
    assert abs(f.meat_factor(3, 10) - (1.0 - a) / (1.0 + a)) < 1e-2   # caribou depression on the steppe row (phase π near trough)


# ── Controlled-climate DRIVER (deterministic regime waveforms; blueprint Stage 0) ──────
def test_driver_waveforms_shapes_and_bounds():
    # flat = control; step = permanent downshift; pulse = single window; ramp = linear; piecewise = general.
    assert all(ClimateDriver.flat()(t) == 1.0 for t in range(50))
    assert all(ClimateDriver.flat(0.8)(t) == 0.8 for t in range(50))
    st = ClimateDriver.step(100, 0.7)
    assert st(99) == 1.0 and st(100) == 0.7 and st(500) == 0.7              # before/at/after onset
    pu = ClimateDriver.pulse(100, 50, 0.7)
    assert pu(99) == 1.0 and pu(100) == 0.7 and pu(149) == 0.7 and pu(150) == 1.0   # half-open [onset, onset+dur)
    rp = ClimateDriver.ramp(100, 200, 0.6)
    assert rp(100) == 1.0 and abs(rp(150) - 0.8) < 1e-9 and rp(200) == 0.6 and rp(300) == 0.6   # linear then held
    pw = ClimateDriver.piecewise([(0, 1.0), (100, 0.7), (200, 1.0)])
    assert pw(50) == 1.0 and pw(150) == 0.7 and pw(250) == 1.0               # step-held breakpoints
    sq = ClimateDriver.square(period=40, mult=0.7, duty=0.5)
    vals = [sq(t) for t in range(40)]
    assert vals[:20] == [0.7] * 20 and vals[20:] == [1.0] * 20              # 50% bad / 50% good per cycle
    assert all(0.0 <= ClimateDriver.step(10, 5.0)(t) <= 1.0 for t in range(20))   # clamped to [0,1]


def test_driver_is_deterministic_and_pure():
    # a pure function of t: identical across instances/calls, no hidden state, no RNG (red-team #4 reproducibility).
    d1 = ClimateDriver.pulse(300, 100, 0.65); d2 = ClimateDriver.pulse(300, 100, 0.65)
    assert [d1(t) for t in range(700)] == [d2(t) for t in range(700)]
    assert [d1(t) for t in range(700)] == [d1(t) for t in range(700)]       # re-callable, order-independent


def test_driver_overrides_telegraph_in_field():
    # With a regime_driver set, regime() follows the driver and IGNORES the stochastic telegraph / regime_amp.
    drv = ClimateDriver.pulse(10, 5, 0.7)
    f = ClimateField(_MockField(), a_seas=0.0, regime_amp=0.13, regime_duration=99, regime_recurrence=99,
                     rng=random.Random(0), regime_driver=drv)
    seq = []
    for t in range(20):
        f.set_step(t); seq.append(f.regime())
    assert seq[9] == 1.0 and seq[10] == 0.7 and seq[14] == 0.7 and seq[15] == 1.0   # exactly the pulse
    assert f._regime_state == 0                                              # telegraph never advanced (driver in control)
    f.set_step(12); assert abs(f.level(1, 1) - 70.0) < 1e-9                  # 100 × driver mult, deterministic


def test_driver_none_is_bit_exact_telegraph():
    # regime_driver=None ⇒ unchanged stochastic behaviour (bit-exact vs a field built without the param).
    kw = dict(a_seas=0.4, interannual_amp=0.2, interannual_period=48, regime_amp=0.12,
              regime_duration=240, regime_recurrence=1200)
    a = ClimateField(_MockField(), **kw, rng=random.Random(7))
    b = ClimateField(_MockField(), **kw, rng=random.Random(7), regime_driver=None)
    for t in range(1, 2000):
        a.set_step(t); b.set_step(t)
        assert a.level(2, 2) == b.level(2, 2) and a._regime_state == b._regime_state


def test_driver_flat_control_equals_no_regime():
    # the control arm (flat(1.0)) is identical to a field with no regime layer at all — a clean baseline.
    drv = ClimateField(_MockField(), a_seas=0.6, interannual_amp=0.2, interannual_period=48,
                       regime_driver=ClimateDriver.flat(1.0))
    none = ClimateField(_MockField(), a_seas=0.6, interannual_amp=0.2, interannual_period=48)
    for t in range(96):
        drv.set_step(t); none.set_step(t)
        assert abs(drv.level(3, 3) - none.level(3, 3)) < 1e-12


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
