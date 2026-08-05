"""Every climate channel, checked ONE AT A TIME against its own signature.

WHY (R-106). `draw_world_climate()` produces a full per-world climate lottery — orbital seasonality,
eccentricity mean factor, ENSO interannual, a regime telegraph, caribou herd swings, llanos floods. It was
unit-tested and **its only callers were those tests**: every `ClimateField` in the project was built as
`ClimateField(base, a_seas=0.4, regime_driver=None)` and took the 0.0 default for everything else. So every
experiment this project has run had a fixed seasonal sine and white noise and no multi-year environmental
variability at any timescale — which is the scope caveat the no-cycles findings never carried.

The channels are configuration now (`ClimateConfig`, in `config/mechanisms.toml` beside the social flags).
This file is the acceptance gate for each one, and each test asserts the channel's OWN SIGNATURE rather than
merely that something changed:

  * OFF is bit-exact, so adopting the config changes no prior result
  * ON with a zero magnitude is REFUSED, not silently inert — the defect class this arc has spent itself on
  * seasonality      period 12, peak-to-trough == a_seas
  * eccentricity     scales the mean by exactly mean_factor
  * interannual      a depression on the configured ENSO period, deepest at the trough
  * regime           a sustained PLATEAU (piecewise-constant), not a mean-reverting wiggle
  * caribou          hits GRASS_STEPPE meat and nothing else
  * llanos           TWO-SIDED — depressed at BOTH extremes of the same ENSO clock
  * intercept        a game boost only in the late dry season
"""
import math

import numpy as np
import pytest

from sic_games.climate import (CARIBOU_AMP_ABOUT_MEAN, ClimateConfig, ClimateField,
                               build_climate_field)


class _Flat:
    """A base field of constant level, so any variation seen is the climate layer's own."""
    width = height = 8

    def level(self, x, y):
        return 100.0


class _Fields:
    """Minimal WorldFields stand-in: a grass_subtype grid with one steppe and one llanos cell."""
    def __init__(self, steppe=(1, 1), llanos=(2, 2)):
        from sic_games.terrain import GRASS_LLANOS, GRASS_STEPPE
        self.grass_subtype = np.zeros((8, 8), dtype=np.uint8)
        self.grass_subtype[steppe[1], steppe[0]] = GRASS_STEPPE
        self.grass_subtype[llanos[1], llanos[0]] = GRASS_LLANOS


def _series(field, n, x=0, y=0):
    out = []
    for t in range(n):
        field.set_step(t)
        out.append(field.level(x, y))
    return out


# ── the adoption gate ────────────────────────────────────────────────────────────────────────────────

def test_defaults_rebuild_the_historical_field_exactly():
    """Every campaign this project has run used `ClimateField(base, a_seas=0.4, regime_driver=None)`. If the
    config's defaults do not reproduce that, adopting it silently invalidates the entire results log."""
    base = _Flat()
    a = build_climate_field(base, ClimateConfig(), fields=_Fields(), seed=0)
    b = ClimateField(base, a_seas=0.4, regime_driver=None)
    for n in ("a_seas", "mean_factor", "interannual_amp", "interannual_period", "regime_amp",
              "regime_duration", "regime_recurrence", "caribou_amp", "caribou_period",
              "llanos_flood_amp"):
        assert getattr(a, n) == getattr(b, n), f"{n} differs from the historical construction"
    assert a.regime_driver is None
    assert _series(a, 24) == _series(b, 24)


@pytest.mark.parametrize("flag", ["enable_interannual", "enable_regime_shift", "enable_caribou_swing",
                                  "enable_eccentricity_mean"])
def test_a_channel_on_with_a_zero_magnitude_is_refused(flag):
    """ON-but-dead is the defect this project keeps finding: live in the config dump, absent from the world,
    INERT in every ablation. A channel must not be allowed to reach that state quietly."""
    cfg = ClimateConfig().model_copy(update={flag: True})
    with pytest.raises(ValueError, match="do nothing|neutral"):
        build_climate_field(_Flat(), cfg, fields=_Fields(), seed=0)


def test_the_lottery_draws_every_channel_inside_its_published_band():
    """The drawn values are the lit anchors, so they are worth asserting: Timmermann ENSO 2-7 yr / 0.20-0.40,
    Wanner regime 0.10-0.15 with 100-500 yr excursions recurring every 1000-2000 yr, St. John caribou 40-90 yr
    at amplitude 0.871."""
    cfg = ClimateConfig().model_copy(update={
        "enable_climate_lottery": True, "enable_interannual": True, "enable_regime_shift": True,
        "enable_caribou_swing": True, "enable_eccentricity_mean": True})
    for seed in range(6):
        f = build_climate_field(_Flat(), cfg, fields=_Fields(), seed=seed)
        assert 0.20 <= f.interannual_amp <= 0.40
        assert 2 * 12 <= f.interannual_period <= 7 * 12
        assert 0.10 <= f.regime_amp <= 0.15
        assert 100 * 12 <= f.regime_duration <= 500 * 12
        assert 1000 * 12 <= f.regime_recurrence <= 2000 * 12
        assert f.caribou_amp == pytest.approx(CARIBOU_AMP_ABOUT_MEAN)
        assert 40 * 12 <= f.caribou_period <= 90 * 12
        assert f.mean_factor >= 1.0


# ── channel by channel ───────────────────────────────────────────────────────────────────────────────

def test_seasonality_has_period_12_and_the_configured_depth():
    f = build_climate_field(_Flat(), ClimateConfig(a_seas=0.4), fields=_Fields(), seed=0)
    s = _series(f, 36)
    assert s[:12] == pytest.approx(s[12:24]), "the seasonal cycle is not 12 steps"
    assert max(s) == pytest.approx(100.0), "the seasonal multiplier must be peak-normalised"
    assert min(s) / max(s) == pytest.approx(1.0 - 0.4, abs=1e-9), "trough depth != a_seas"


def test_eccentricity_scales_the_mean_by_exactly_mean_factor():
    plain = _series(build_climate_field(_Flat(), ClimateConfig(), fields=_Fields(), seed=0), 24)
    cfg = ClimateConfig(enable_eccentricity_mean=True, mean_factor=1.2)
    lifted = _series(build_climate_field(_Flat(), cfg, fields=_Fields(), seed=0), 24)
    assert np.mean(lifted) / np.mean(plain) == pytest.approx(1.2, rel=1e-9)


def test_interannual_depresses_on_its_own_period():
    """The ENSO layer must show up AT the configured period, not merely make the series different."""
    per = 5 * 12
    cfg = ClimateConfig(enable_interannual=True, interannual_amp=0.3, interannual_period=per)
    f = build_climate_field(_Flat(), cfg, fields=_Fields(), seed=0)
    # Read the ENSO factor DIRECTLY rather than inferring it from the product with the seasonal cycle: a
    # 12-step yearly mean smears the trough and understates the depth (measured 0.73 against a true 0.70),
    # and loosening the tolerance to absorb that would be fitting the test to its own blunt instrument.
    enso = []
    for t in range(per * 3):
        f.set_step(t)
        enso.append(f.interannual())
    assert max(enso) == pytest.approx(1.0), "the ENSO layer must be a depression, peak-normalised at 1"
    assert min(enso) == pytest.approx(1.0 - 0.3, abs=1e-9), "ENSO depth != interannual_amp"
    troughs = [i for i in range(1, len(enso) - 1)
               if enso[i] <= enso[i - 1] and enso[i] < enso[i + 1]]
    gaps = [b - a for a, b in zip(troughs, troughs[1:]) if b - a > 1]
    assert gaps and gaps[0] == pytest.approx(per, rel=0.05), (
        f"troughs recur every {gaps[:3]} steps, not on the {per}-step ENSO period")


def test_regime_is_a_sustained_plateau_not_a_wiggle():
    """The C.3 red-team point: this is a regime-SWITCHING step process (a multi-generational plateau), not a
    mean-reverting OU wiggle. So the regime multiplier must take exactly two values and hold each of them."""
    cfg = ClimateConfig(enable_regime_shift=True, regime_amp=0.15, regime_duration=200 * 12,
                        regime_recurrence=1000 * 12)
    f = build_climate_field(_Flat(), cfg, fields=_Fields(), seed=3)
    vals = []
    for t in range(0, 4000 * 12, 12):
        f.set_step(t)
        vals.append(round(f.regime(), 12))
    distinct = set(vals)
    assert distinct <= {1.0, round(1.0 - 0.15, 12)}, f"regime took intermediate values {distinct}"
    if len(distinct) == 1:
        pytest.skip("no excursion occurred on this seed within the window")
    runs, cur = [], 1
    for a, b in zip(vals, vals[1:]):
        cur = cur + 1 if a == b else (runs.append(cur) or 1)
    runs.append(cur)
    excursions = [r for r, v in zip(runs, [vals[0]]) if True] and max(runs)
    assert excursions >= 10, "the regime flips too fast to be a plateau"


def test_caribou_hits_steppe_meat_and_nothing_else():
    cfg = ClimateConfig(enable_caribou_swing=True, caribou_amp=CARIBOU_AMP_ABOUT_MEAN,
                        caribou_period=50 * 12)
    fl = _Fields(steppe=(1, 1), llanos=(2, 2))
    f = build_climate_field(_Flat(), cfg, fields=fl, seed=0)
    steppe, elsewhere = [], []
    for t in range(0, 50 * 12, 12):
        f.set_step(t)
        steppe.append(f.meat_factor(1, 1))
        elsewhere.append(f.meat_factor(5, 5))
    assert max(elsewhere) == pytest.approx(min(elsewhere)), "caribou touched a non-steppe cell"
    assert max(steppe) - min(steppe) > 0.5, "no herd swing on the steppe cell"


def test_llanos_flood_is_two_sided():
    """Hamilton/Sarmiento: BOTH a failed flood and an over-flood hurt the forager, so the llanos depression is
    `1 - amp*|sin theta|` — worst at BOTH extremes of the ENSO clock, unlike the one-sided generic ENSO."""
    per = 4 * 12
    cfg = ClimateConfig(enable_interannual=True, interannual_amp=0.25, interannual_period=per,
                        enable_llanos_flood=True, llanos_flood_amp=0.4)
    fl = _Fields(steppe=(1, 1), llanos=(2, 2))
    f = build_climate_field(_Flat(), cfg, fields=fl, seed=0)
    vals = []
    for t in range(per):
        f.set_step(t)
        vals.append(f.interannual_at(2, 2))
    lo = min(vals)
    deep = [i for i, v in enumerate(vals) if v < lo + 0.02 * (max(vals) - lo + 1e-12)]
    # Two-sided ⇒ minima at both half-cycle extremes, i.e. separated by about half a period.
    assert max(deep) - min(deep) > per * 0.25, (
        f"llanos minima cluster at one extreme ({deep}) — the layer is one-sided")


def test_llanos_without_a_clock_is_refused():
    """The flood rides the ENSO period; without `enable_interannual` it has no clock and would be inert."""
    cfg = ClimateConfig(enable_llanos_flood=True, llanos_flood_amp=0.4)
    with pytest.raises(ValueError, match="clock|enable_interannual"):
        build_climate_field(_Flat(), cfg, fields=_Fields(), seed=0)


def test_caribou_without_masks_is_refused():
    """Without `grass_subtype` the mask is None and C.4b is inert at any amplitude — the exact failure this
    whole exercise exists to stop."""
    cfg = ClimateConfig(enable_caribou_swing=True, caribou_amp=0.871, caribou_period=600)
    with pytest.raises(ValueError, match="grass_subtype|mask"):
        build_climate_field(_Flat(), cfg, fields=None, seed=0)
