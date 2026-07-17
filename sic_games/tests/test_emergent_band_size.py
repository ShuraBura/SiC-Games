"""Emergent band size v3 (R-72): band size = argmax{risk-pooling − competition}.

Pins the three things v1/v2 got wrong:
  1. The CV is TEMPORAL (one forager's day-to-day luck), not the SPATIAL cross-cell spread in
     FORAGE/GAME_KCAL_STD. Those stay untouched — they feed the lognormal cell-value draw.
  2. The law is LINEAR (g*=CV/cv_safe), not quadratic. The square is a stopping rule with no cost
     side ⇒ unbounded ⇒ needs clamps ⇒ saturates at floor/cap with nothing between.
  3. The CV drives the COST side (scalar-stress midpoint = g*), not merely a fission ceiling.
     A ceiling is permission to be big; it cannot pull a band together.
Default-OFF ⇒ bit-exact.
"""
import math

import numpy as np
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig, size_repulsion
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import (GATHER_CV, HUNT_CV, MEAT_FRAC, RETURN_CV, biome_return_cv,
                               generate_world, world_lottery_climate)


def _world(**kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=DemographyConfig(**kw))


def test_defaults_off_and_calibration():
    c = DemographyConfig()
    assert c.enable_emergent_band_size is False          # opt-in ⇒ bit-exact back-compat
    assert c.cv_safe == 0.037
    # the two knobs v3 deletes (v2's band_size_min=15 social floor + cv_min=0.4 data-gap band-aid)
    assert not hasattr(c, "band_size_min")
    assert not hasattr(c, "cv_min")


def test_stream_cvs_are_the_measured_anchors():
    assert HUNT_CV == 2.11        # cchunts median, 10 observed societies (~15,600 trips); Aché 1.97, Martu 2.92
    assert GATHER_CV == 0.70      # Berbesque & Marlowe 2009 Tab. 4, Hadza tuber 257.7±182.1 over N=56 bouts


def test_hunting_is_the_high_variance_stream():
    """The whole grouping incentive. Hill 1987: 'daily variance in calories acquired is much higher for
    hunting than it is for gathering'. Bird 2009: every plant food has success rate 1.00."""
    assert HUNT_CV > 2.5 * GATHER_CV


def test_biome_cv_is_derived_from_meat_fraction_not_hand_set():
    for b, m in MEAT_FRAC.items():
        assert RETURN_CV[b] == pytest.approx(biome_return_cv(m))


def test_cv_endpoints_are_the_pure_streams():
    """A pure-gathering diet carries exactly the gathering CV; a pure-hunting diet the hunting CV."""
    assert biome_return_cv(0.0) == pytest.approx(GATHER_CV)
    assert biome_return_cv(1.0) == pytest.approx(HUNT_CV)


def test_cv_rises_monotonically_with_meat_dependence():
    """The entire per-biome gradient: the stream CVs carry no biome signal (cchunts — forest alone spans
    1.53–4.64), so ALL of it comes from how much of the diet rides the high-variance stream."""
    cvs = [biome_return_cv(m) for m in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
    assert all(b > a for a, b in zip(cvs, cvs[1:]))


def test_predicted_band_sizes_match_the_ethnography():
    """THE headline result. cv_safe is fitted ONLY to place the mean (Hill 2011 ~25–30); the SPREAD is a
    free prediction and must land on Marlowe/Kelly's observed 25–50 (a 2× range)."""
    cfg = DemographyConfig()
    # the EFFECTIVE set the model uses: the anchored biomes plus the gathering floor that unanchored
    # ones (wetland) fall back to in _return_cv_field — not RETURN_CV alone.
    eff = list(RETURN_CV.values()) + [GATHER_CV]
    vals = sorted(v / cfg.cv_safe for v in eff)
    assert 25.0 <= (sum(vals) / len(vals)) <= 30.0        # mean in Hill 2011's 25–30 (calibrated)
    assert vals[-1] / vals[0] == pytest.approx(2.0, abs=0.15)   # spread ≈ Marlowe 2× (PREDICTED)
    assert 15.0 <= vals[0] and vals[-1] <= 50.0           # every biome inside Hill 2011's observed 15–50


def test_law_is_linear_not_quadratic():
    """v1/v2's (CV/cv_safe)² turned a 2× CV spread into 4× and blew through any clamp. Linear ⇒ a 2× CV
    spread is a 2× band spread, which is what the ethnography shows."""
    cfg = DemographyConfig()
    assert (2.0 * 0.7) / cfg.cv_safe == pytest.approx(2.0 * (0.7 / cfg.cv_safe))


def test_optimum_field_is_unclamped_and_linear():
    w = _world(enable_emergent_band_size=True)
    cv = w._return_cv_field()
    g = w._band_optimum_field()
    assert cv is not None and g is not None
    assert np.allclose(g, cv / w._demog.cv_safe)          # no clip anywhere
    # every biome present lands in the interior of the OLD clamps [15, 45] — the saturation is gone
    vals = np.unique(g)
    assert vals.min() > 15.0 and vals.max() < 45.0


def test_cv_field_uses_temporal_not_spatial_variance():
    """Regression on the category error: the per-cell CV must equal the diet-derived RETURN_CV, never the
    σ/μ of the spatial FORAGE/GAME_KCAL_STD (which gave wetland 2.35 from a cross-habitat skew)."""
    w = _world(enable_emergent_band_size=True)
    cv = w._return_cv_field()
    biome = w._fields.biome
    for code in np.unique(biome):
        expect = RETURN_CV.get(int(code), GATHER_CV)
        assert cv[biome == code] == pytest.approx(expect)
    assert cv.max() <= HUNT_CV + 1e-9                     # nothing above the pure-hunting ceiling (old: 2.35)


def test_unanchored_biome_falls_back_to_gathering_floor():
    """A biome with no diet anchor must not manufacture a pooling incentive out of nothing."""
    w = _world(enable_emergent_band_size=True)
    cv = w._return_cv_field()
    biome = w._fields.biome
    for code in np.unique(biome):
        if int(code) not in RETURN_CV:
            assert cv[biome == code] == pytest.approx(GATHER_CV)


def test_scalar_stress_midpoint_tracks_the_local_optimum():
    """THE causal fix. Same band size, same gain: a band on high-variance returns (grass, g*≈38) must feel
    LESS dispersive scalar stress than one on low-variance returns (wetland, g*≈19) — so the CV reaches the
    term that actually sets band size, instead of only raising a ceiling it never touches."""
    cfg = DemographyConfig()
    g_lo = GATHER_CV / cfg.cv_safe                        # the gathering floor (e.g. unanchored wetland)
    g_hi = max(RETURN_CV.values()) / cfg.cv_safe          # BIOME_GRASS — 66% meat, the highest-variance diet
    assert g_hi > g_lo
    n = 30
    rep_lo = size_repulsion(n, 0.3, g_lo, cfg.repulsion_width, None)
    rep_hi = size_repulsion(n, 0.3, g_hi, cfg.repulsion_width, None)
    assert rep_hi < rep_lo
    # and the old hardcoded 25 sits between them — i.e. it was averaging away a real gradient
    rep_25 = size_repulsion(n, 0.3, 25.0, cfg.repulsion_width, None)
    assert rep_hi < rep_25 < rep_lo
