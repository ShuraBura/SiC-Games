"""CTB (Constructed-Truth Benchmark) for the climate health diagnostic.

THE PROCEDURE, which this file is the reference implementation of:
    1. build a world whose answer you already know — here, a climate field with a hand-set amplitude, period
       and mask, so the correct reading is arithmetic rather than opinion
    2. measure it with the REAL diagnostic, not a reimplementation of it
    3. verify the measurement returns what was built

It exists because the diagnostic is the thing being tested, not the model. Every climate reading this project
has made was believed on the strength of a config dump saying "on", and three separate channels turned out to
be inert while reading as live — an empty llanos mask, a caribou channel in a world with no steppe, and a
regime telegraph whose recurrence exceeded the run length. A health verdict that cannot tell those apart is
worse than none, because it launders them into confidence.

The four verdicts the instrument must distinguish, each constructed below:
    OFF          amplitude zero — the channel was not asked to do anything
    UNREACHABLE  amplitude live, mask empty — it can never touch a cell
    NEVER-FIRED  amplitude live, mask populated, clock never came round in this run
    LIVE         it actually moved the field
"""
import math

import numpy as np
import pytest

from sic_games.climate import INTERCEPT_BOOST, INTERCEPT_DRY_THRESHOLD, ClimateField


class _FlatBase:
    """A carrying-capacity field of exactly 1.0 everywhere, so any deviation `level()` reports IS the climate
    multiplier and nothing else."""
    width = height = 10

    def level(self, x, y):
        return 1.0


def _mask(**cells):
    """A 10x10 boolean mask, True at the given (x, y) keys like x3y4=True."""
    m = np.zeros((10, 10), dtype=bool)
    for k, v in cells.items():
        x, y = int(k.split("y")[0][1:]), int(k.split("y")[1])
        m[y, x] = v
    return m


def _run(field, steps):
    for t in range(steps):
        field.set_step(t)
    return field.health()


# ── the four verdicts, constructed ────────────────────────────────────────────────────────────────────────

def test_a_zero_amplitude_channel_reports_OFF():
    """THE CONTROL. Nothing configured ⇒ nothing measured. If this ever reads LIVE the instrument is inventing
    signal, and every other assertion in this file is worthless."""
    h = _run(ClimateField(_FlatBase(), a_seas=0.0), 24)
    assert h["interannual"]["verdict"] == "OFF"
    assert h["regime"]["verdict"] == "OFF"
    assert h["season"]["verdict"] == "OFF"
    assert h["interannual"]["mean"] == 1.0


def test_a_live_amplitude_with_an_EMPTY_mask_reports_UNREACHABLE():
    """The llanos bug, reconstructed. The flood amplitude is a real 0.45 and the clock is running; the mask
    selects zero cells, so the channel cannot touch anything. This must NOT read LIVE, and it must not read
    OFF either — the two call for completely different fixes."""
    f = ClimateField(_FlatBase(), a_seas=0.4, interannual_amp=0.3, interannual_period=48,
                     llanos_flood_amp=0.45, llanos_mask=np.zeros((10, 10), dtype=bool))
    h = _run(f, 96)
    assert h["llanos"]["reach"] == 0
    assert h["llanos"]["verdict"] == "UNREACHABLE"


def test_a_live_channel_whose_CLOCK_never_comes_round_reports_NEVER_FIRED():
    """The regime-telegraph case, and the one nothing in this project could previously see. Amplitude 0.15,
    reachable everywhere, but a recurrence of 10^9 steps means the excursion never starts inside the run. The
    config dump says 'on'; the world never felt it."""
    import random
    f = ClimateField(_FlatBase(), a_seas=0.0, regime_amp=0.15, regime_duration=1200,
                     regime_recurrence=10 ** 9, rng=random.Random(0))
    h = _run(f, 500)
    assert h["regime"]["verdict"] == "NEVER-FIRED"
    assert h["regime"]["active_frac"] == 0.0
    assert h["regime"]["min"] == 1.0, "it never depressed the field, so the extreme must still be neutral"


def test_a_channel_that_actually_moves_the_field_reports_LIVE_with_the_constructed_amplitude():
    """THE POSITIVE CONTROL, and the arithmetic is the point. A one-sided ENSO of amplitude 0.30 on a 48-step
    clock must reach exactly 1 - 0.30 = 0.70 at its trough and 1.0 at its peak, and must be active on the half
    of the cycle where sin > 0."""
    f = ClimateField(_FlatBase(), a_seas=0.0, interannual_amp=0.30, interannual_period=48)
    h = _run(f, 48 * 4)
    assert h["interannual"]["verdict"] == "LIVE"
    assert h["interannual"]["min"] == pytest.approx(0.70, abs=1e-3)
    assert h["interannual"]["max"] == pytest.approx(1.0, abs=1e-2)
    assert h["interannual"]["active_frac"] == pytest.approx(0.5, abs=0.05), (
        "a one-sided depression is active on the positive half of the sine and neutral on the other")


# ── the seasonal + spatial channels, against hand-computed values ─────────────────────────────────────────

def test_the_seasonal_trough_is_one_minus_the_amplitude():
    """A_seas = 0.6 ⇒ the peak-normalised season runs [0.4, 1.0]. This is the R-6 `run_2d` form the whole
    capacity field rests on, so its extremes are worth pinning independently of the health wrapper."""
    h = _run(ClimateField(_FlatBase(), a_seas=0.6, period=12), 120)
    assert h["season"]["min"] == pytest.approx(0.4, abs=1e-3)
    assert h["season"]["max"] == pytest.approx(1.0, abs=1e-3)
    assert h["season"]["verdict"] == "LIVE"


def test_the_llanos_flood_is_TWO_SIDED_where_the_enso_is_one_sided():
    """The forms genuinely differ and the diagnostic must show it: the llanos flood is `1 - amp*|sin|`, hurt by
    BOTH a failed flood and an over-flood, so it is active almost always. The generic ENSO is `1 - amp*max(0,
    sin)` and is neutral for half the cycle. Same clock, same world, different shape."""
    f = ClimateField(_FlatBase(), a_seas=0.0, interannual_amp=0.30, interannual_period=48,
                     llanos_flood_amp=0.40, llanos_mask=_mask(x2y2=True, x3y3=True))
    h = _run(f, 48 * 4)
    assert h["llanos"]["reach"] == 2
    assert h["llanos"]["verdict"] == "LIVE"
    assert h["llanos"]["min"] == pytest.approx(0.60, abs=1e-3)
    assert h["llanos"]["active_frac"] > 0.9, "two-sided: only the zero-crossings are neutral"
    assert h["interannual"]["active_frac"] == pytest.approx(0.5, abs=0.05)


def test_the_caribou_swing_is_peak_pinned_and_its_trough_is_the_published_ratio():
    """Peak-pinned to 1.0 with trough (1-a)/(1+a). At the cited a = 0.871 that is 0.069 — a ~93%
    peak-to-trough drawdown. The channel is default-OFF because that number has no filed source (Addendum 29),
    but the FORM is still worth pinning so the arithmetic is checked when the thesis arrives."""
    a = 0.871
    f = ClimateField(_FlatBase(), a_seas=0.0, caribou_amp=a, caribou_period=480,
                     steppe_mask=_mask(x1y1=True))
    h = _run(f, 480)
    assert h["caribou"]["reach"] == 1
    assert h["caribou"]["verdict"] == "LIVE"
    assert h["caribou"]["max"] == pytest.approx(1.0, abs=1e-3)
    assert h["caribou"]["min"] == pytest.approx((1 - a) / (1 + a), abs=1e-3)
    assert h["caribou"]["min"] == pytest.approx(0.069, abs=2e-3)


def test_intercept_hunting_fires_only_in_the_late_dry_season_and_by_the_hawkes_ratio():
    """C.5 is a THRESHOLD, not a continuous modifier: it switches on only when normalised dryness clears 0.75,
    which is a minority of the year (the Hadza Aug–Oct window). Its magnitude at the wettest waterhole is the
    verified Hawkes ratio, +44%."""
    water = np.full((10, 10), 0.0)
    water[1, 1] = 1.0
    f = ClimateField(_FlatBase(), a_seas=0.5, period=12, agg_mask=_mask(x1y1=True), water_weight=water)
    h = _run(f, 12 * 8)
    assert h["intercept"]["reach"] == 1
    assert h["intercept"]["verdict"] == "LIVE"
    assert h["intercept"]["max"] == pytest.approx(1.0 + INTERCEPT_BOOST, abs=1e-3)
    assert h["intercept"]["max"] == pytest.approx(745 / 518, abs=1e-3)
    assert h["intercept"]["active_frac"] < 0.5, (
        f"a threshold at dryness>={INTERCEPT_DRY_THRESHOLD} must be a minority of the year, not most of it")


def test_health_never_reports_LIVE_for_a_channel_that_did_not_move_the_field():
    """THE INSTRUMENT'S OWN NULL. Across every construction above, a channel whose measured extremes are both
    exactly neutral must never carry a LIVE verdict — that equivalence is what the whole diagnostic rests on."""
    import random
    fields = [
        ClimateField(_FlatBase(), a_seas=0.0),
        ClimateField(_FlatBase(), a_seas=0.4, interannual_amp=0.3, interannual_period=48,
                     llanos_flood_amp=0.45, llanos_mask=np.zeros((10, 10), dtype=bool)),
        ClimateField(_FlatBase(), a_seas=0.0, regime_amp=0.2, regime_duration=100,
                     regime_recurrence=10 ** 9, rng=random.Random(1)),
    ]
    for f in fields:
        for ch, r in _run(f, 200).items():
            if r.get("min") == 1.0 and r.get("max") == 1.0:
                assert r["verdict"] != "LIVE", f"{ch} reported LIVE without moving the field: {r}"


def test_the_caribou_period_band_matches_the_thesis_and_not_the_number_we_carried():
    """THE CORRECTION THE FETCHED PAPER FORCED (2026-08-06, Addendum 32).

    We carried `40-90 yr`, attributed to Bergerud. The thesis was filed, read, and says (Figure 9, over the 19
    cyclic herds of 43 collected): `Min=23, Q1=33, Median=40.5, Q3=50, Max=67`. Bergerud is not cited in it at
    all. So the old band excluded everything below the median AND ran 23 years past the longest cycle ever
    measured — nearly every drawn world got a period longer than the median herd.

    This pins the corrected band to the OBSERVED range, so a future edit back toward 40-90 fails here."""
    from sic_games.climate import (CARIBOU_AMP_ABOUT_MEAN, CARIBOU_AMP_QUARTILES,
                                   CARIBOU_PERIOD_MAX_YR, CARIBOU_PERIOD_MIN_YR,
                                   CARIBOU_PERIOD_QUARTILES_YR)
    assert (CARIBOU_PERIOD_MIN_YR, CARIBOU_PERIOD_MAX_YR) == (23.0, 67.0)
    assert CARIBOU_PERIOD_QUARTILES_YR == (23.0, 33.0, 40.5, 50.0, 67.0)
    assert CARIBOU_AMP_QUARTILES == (0.406, 0.700, 0.871, 1.126, 1.570)
    # the pinned value is the paper's MEDIAN, and it must sit inside the band it is drawn from
    assert CARIBOU_AMP_ABOUT_MEAN == CARIBOU_AMP_QUARTILES[2]
    assert CARIBOU_PERIOD_MIN_YR <= CARIBOU_PERIOD_QUARTILES_YR[2] <= CARIBOU_PERIOD_MAX_YR


def test_a_caribou_amplitude_above_one_would_produce_NEGATIVE_meat():
    """THE HAZARD THE PAPER'S OWN DISTRIBUTION EXPOSES, constructed before anyone writes the draw.

    `_caribou_factor` is peak-pinned: (1 + a*cos)/(1 + a), so its trough is (1-a)/(1+a) — which goes NEGATIVE
    for a > 1. The thesis's Q3 is 1.126 and its Max is 1.570, so **half the observed herds are above the value
    at which this form breaks**. Pinning the median (0.871) is safe today; drawing per-world from the observed
    distribution is not, and would silently produce negative meat rather than raising.

    Constructed here so the clamp is a known requirement rather than a later bug report."""
    from sic_games.climate import CARIBOU_AMP_QUARTILES

    def trough(a):
        return (1.0 - a) / (1.0 + a)

    assert trough(0.871) == pytest.approx(0.0689, abs=1e-3), "the pinned median is a safe ~93% drawdown"
    assert trough(1.0) == 0.0, "a = 1 is exactly the boundary"
    for a in (CARIBOU_AMP_QUARTILES[3], CARIBOU_AMP_QUARTILES[4]):   # Q3 1.126, Max 1.570
        assert a > 1.0 and trough(a) < 0.0, f"a={a} gives a negative trough and must be clamped before use"

    # and the live field, at the pinned value, never goes negative anywhere in a full cycle
    f = ClimateField(_FlatBase(), a_seas=0.0, caribou_amp=0.871, caribou_period=120,
                     steppe_mask=_mask(x1y1=True))
    h = _run(f, 240)
    assert h["caribou"]["min"] > 0.0


def test_a_brightening_channel_reports_the_value_it_actually_took():
    """FOUND BY READING A REAL RUN, then constructed here. `eccentricity` is a BRIGHTENING — every value it
    takes is above 1.0. The accumulator seeded min/max at the neutral 1.0, so it reported `min = 1.0`, a value
    the channel never held. Depressions hid the bug because for them 1.0 genuinely is the ceiling.

    A one-directional channel must report its own range, not a range padded with the neutral point."""
    f = ClimateField(_FlatBase(), a_seas=0.0, mean_factor=1.25)
    h = _run(f, 50)
    assert h["eccentricity"]["verdict"] == "LIVE"
    assert h["eccentricity"]["min"] == pytest.approx(1.25), "it was never 1.0"
    assert h["eccentricity"]["max"] == pytest.approx(1.25)
    assert h["eccentricity"]["mean"] == pytest.approx(1.25)


def test_an_unreachable_channel_reports_NO_magnitude_rather_than_a_fictional_one():
    """ALSO FOUND BY READING A REAL RUN. On a temperate world with no llanos, the health block read
    `llanos: verdict UNREACHABLE, reach 0, active_frac 1.0, min 0.699` — the verdict correct, and the numbers
    beneath it describing a depression applied to zero cells.

    Detail that looks like corroboration is worse than a bare wrong answer, because it invites someone to
    quote the 0.699. An unreachable channel must be neutral in every field, not just in its verdict."""
    f = ClimateField(_FlatBase(), a_seas=0.4, interannual_amp=0.3, interannual_period=48,
                     llanos_flood_amp=0.45, llanos_mask=np.zeros((10, 10), dtype=bool))
    h = _run(f, 96)
    assert h["llanos"]["verdict"] == "UNREACHABLE"
    assert h["llanos"]["active_frac"] == 0.0
    assert h["llanos"]["min"] == 1.0 and h["llanos"]["max"] == 1.0
    # and the sibling channel on the same clock is unaffected by the fix
    assert h["interannual"]["verdict"] == "LIVE"


def test_observing_does_not_perturb_the_simulation():
    """The diagnostic must be an OBSERVER. Two identically-seeded fields stepped the same way must produce
    identical `level()` traces — if health accounting touched the RNG or a cache, every climate result after
    2026-08-06 would differ from every result before it for a reason that is not the climate."""
    import random

    def trace(seed):
        f = ClimateField(_FlatBase(), a_seas=0.4, period=12, interannual_amp=0.25, interannual_period=48,
                         regime_amp=0.12, regime_duration=50, regime_recurrence=80, rng=random.Random(seed))
        return [(f.set_step(t), f.level(3, 4))[1] for t in range(300)]

    assert trace(7) == trace(7)
    assert trace(7) != trace(8), "different seeds must give different telegraphs, or the test proves nothing"
