"""Climate stage (§4.1.6 star-mechanics seam) — C.1: obliquity → seasonal-amplitude lottery + the time-varying
`ClimateField` wrapper. Blueprint: blueprints/phase1/SiC_Games_P1_Climate_OrbitalLottery_Scoping.md.

Discipline (§4.1.6): the stellar mechanics BOUND the parameter draws; they do NOT run tick-by-tick. The
ClimateField multiplies the carrying-capacity field by a peak-normalized seasonal multiplier (the validated R-6
`run_2d` form), so the demographic substrate is UNCHANGED code — it just reads a time-varying field (§4.1.7
isolation). Later steps (C.2–C.4) fold interannual / regime-shift / catastrophe layers into `mult()`.
"""
from __future__ import annotations
import math

OBLIQUITY_EARTH_DEG = 23.4            # Earth axial tilt
OBLIQUITY_HABITABLE_MAX_DEG = 60.0    # conservative habitable envelope (Spiegel 2009: broad band, no clean
                                      # monotone obliquity→snowball threshold; the equator-freeze intuition is
                                      # Williams & Kasting 1997). Uniform draws within (Q3).
SEASON_PERIOD_DEFAULT = 12            # steps per year (1 step = 1 month)

# §4.1.4 Earth-anchored seasonal amplitude (A_seas = 1 − s_min) per biome, AT EARTH obliquity (23.4°).
A_SEAS_EARTH = {
    "forest":  0.05,   # Aché — calories ~aseasonal (Hill 1984)
    "savanna": 0.40,   # Hadza — moderate, dry-season aggregation (Hawkes 1991)
    "llanos":  0.60,   # Hiwi — wet-season flood access loss, Liebig (Hurtado & Hill 1987)
}


def obliquity_to_amplitude(epsilon_deg: float, a_earth: float) -> float:
    """Q1-(B): map obliquity to seasonal amplitude by SCALING the empirical Earth amplitude `a_earth` (§4.1.4)
    by sin ε / sin 23.4° — a PROVISIONAL bounding heuristic onto the Earth band, NOT a sunlight→food transfer
    function (forage amplitude is rain/phenology-driven). Earth ε=23.4° → a_earth; clamped to [0,1]; rises
    monotone with ε (insolation contrast crosses pole>equator at ε≈54°)."""
    a = a_earth * math.sin(math.radians(epsilon_deg)) / math.sin(math.radians(OBLIQUITY_EARTH_DEG))
    return max(0.0, min(1.0, a))


def draw_obliquity(rng) -> float:
    """Per-world UNIFORM draw over the habitable-relevant obliquity envelope [0°, 60°] (Q3 uniform)."""
    return rng.uniform(0.0, OBLIQUITY_HABITABLE_MAX_DEG)


# ── C.2: eccentricity, stellar flux, interannual (ENSO) ────────────────────────
ECCENTRICITY_MAX = 0.6               # Spiegel 2010 (upper third marginal — snowball cut 0.4<e<0.6)
STELLAR_FLUX_MIN = 0.34              # Kopparapu 2013 max-greenhouse outer edge (S⊕)
STELLAR_FLUX_MAX = 1.05             # moist/runaway inner edge
T_EFF_EARTH_K = 255.0               # Earth effective (blackbody) temperature
T_SURFACE_EARTH_C = 14.0            # §4.3.2 anchor: S=1 → 14°C surface (a fixed effective-greenhouse offset)
ENSO_PERIOD_MIN_YR, ENSO_PERIOD_MAX_YR = 2.0, 7.0   # Timmermann 2018
ENSO_AMP_MIN, ENSO_AMP_MAX = 0.20, 0.40             # Timmermann 2018 (±20–40% CC, marginal biomes)

# ── C.3: regime-shift (Layer 3) — a two-state Markov / telegraph excursion ──────
# v2 red-team: this is a REGIME-SWITCHING / step process (a sustained multi-generational PLATEAU), NOT a
# mean-reverting OU wiggle, and excursion DURATION (~100–500 yr) ≠ RECURRENCE (~1000–2000 yr).
REGIME_AMP_MIN, REGIME_AMP_MAX = 0.10, 0.15         # Wanner 2008: LIA global-mean ~0.5°C → central ±10–15% CC
REGIME_AMP_TAIL = 0.30                              # reserve ±30% / ~1°C for explicitly-flagged 8.2-kyr/YD tails
REGIME_DURATION_MIN_YR, REGIME_DURATION_MAX_YR = 100.0, 500.0   # excursion length (LIA ≈ 500 yr; Wanner/Mayewski)
REGIME_RECURRENCE_MIN_YR, REGIME_RECURRENCE_MAX_YR = 1000.0, 2000.0   # onset spacing (Bond ~1500; Mayewski RCC)

# ── C.4b: caribou herd-swing — a quasi-periodic depression on GRASS_STEPPE *meat* only ──────────
# St. John 2022 (43-herd database): migratory-tundra cycles, amplitude 0.871 standardized about the mean
# (⇒ peak 1.871× / trough 0.129× mean → ~93% peak-to-trough drawdown), median period 40.5 yr (range 40–90 yr).
# Vors & Boyce 2009 corroborate ~57% (modern, confounded). Hits the meat channel on the steppe sub-biome only.
CARIBOU_AMP_ABOUT_MEAN = 0.871                  # St. John 2022 cyclic amplitude (fraction of the mean)
CARIBOU_PERIOD_MIN_YR, CARIBOU_PERIOD_MAX_YR = 40.0, 90.0


def draw_eccentricity(rng) -> float:
    """Per-world UNIFORM draw over [0, 0.6] (Q3; Spiegel 2010)."""
    return rng.uniform(0.0, ECCENTRICITY_MAX)


def eccentricity_mean_factor(e: float) -> float:
    """Annual-mean flux BRIGHTENING `(1−e²)^(−½)` (Spiegel 2010): e=0.017→1.0001, e=0.6→1.25. A per-world
    baseline scalar on the carrying capacity (NOT part of the [0,1] temporal multiplier)."""
    return (1.0 - e * e) ** -0.5


def draw_stellar_flux(rng) -> float:
    """Per-world UNIFORM draw over the HZ flux range [0.34, 1.05] S⊕ (Q3; Kopparapu 2013)."""
    return rng.uniform(STELLAR_FLUX_MIN, STELLAR_FLUX_MAX)


def flux_to_temperature(S: float) -> float:
    """Mean SURFACE temperature (°C) from stellar flux: `T_eff ∝ S^¼` (Stefan-Boltzmann), anchored S=1→14°C via
    a fixed effective-greenhouse offset (the bare effective temp is ~33 K too cold for a surface T). RT-3 fix.
    `T(S) = 14 + T_eff_earth·(S^¼ − 1)`. NOTE: a world property / dormant seam — the pathogen channel (§4.6.3)
    currently reads NPP, not this T field, so it does NOT yet drive pathogen seasonality (a future wiring)."""
    return T_SURFACE_EARTH_C + T_EFF_EARTH_K * (S ** 0.25 - 1.0)


def draw_world_climate(rng, a_earth: float) -> dict:
    """Per-world orbital lottery (the full (ε, e, S) trio + an ENSO draw) → a dict of climate params: the
    `ClimateField` kwargs (a_seas, mean_factor, interannual_*) plus the world properties (mean_temperature,
    and the raw orbital draws for the record). Q3 uniform draws."""
    eps = draw_obliquity(rng); e = draw_eccentricity(rng); S = draw_stellar_flux(rng)
    return dict(
        a_seas=obliquity_to_amplitude(eps, a_earth),
        mean_factor=eccentricity_mean_factor(e),
        interannual_amp=rng.uniform(ENSO_AMP_MIN, ENSO_AMP_MAX),
        interannual_period=int(rng.uniform(ENSO_PERIOD_MIN_YR, ENSO_PERIOD_MAX_YR) * SEASON_PERIOD_DEFAULT),
        interannual_phase=rng.uniform(0.0, 2.0 * math.pi),
        # Layer 3 regime-shift (telegraph) params — the central band; tails (REGIME_AMP_TAIL) are reserved for
        # explicitly-flagged catastrophe events (C.4), not the routine lottery (v2 red-team).
        regime_amp=rng.uniform(REGIME_AMP_MIN, REGIME_AMP_MAX),
        regime_duration=int(rng.uniform(REGIME_DURATION_MIN_YR, REGIME_DURATION_MAX_YR) * SEASON_PERIOD_DEFAULT),
        regime_recurrence=int(rng.uniform(REGIME_RECURRENCE_MIN_YR, REGIME_RECURRENCE_MAX_YR) * SEASON_PERIOD_DEFAULT),
        # Layer 4a caribou herd-swing (GRASS_STEPPE meat) — amplitude is the empirical anchor, period drawn.
        caribou_amp=CARIBOU_AMP_ABOUT_MEAN,
        caribou_period=int(rng.uniform(CARIBOU_PERIOD_MIN_YR, CARIBOU_PERIOD_MAX_YR) * SEASON_PERIOD_DEFAULT),
        caribou_phase=rng.uniform(0.0, 2.0 * math.pi),
        mean_temperature=flux_to_temperature(S),
        obliquity=eps, eccentricity=e, flux=S,
    )


class ClimateField:
    """Wrap a base carrying-capacity field (any object exposing `.level(x,y)`; width/height/consume/etc. are
    delegated) with the time-varying climate multiplier M(t). **C.1 = the seasonal layer only:**

        s(t) = s_min + (1−s_min)·½(1 + cos(2πt/P − φ)),   with  A_seas ≡ 1 − s_min

    range [s_min, 1], **peak-normalized to 1.0** — the EXACT validated R-6 form. The harness/model sets the
    current step via `set_step(t)` (R-6 `run_2d` pattern). **A_seas = 0 ⇒ s(t) ≡ 1.0 (aseasonal baseline,
    bit-exact).** `mult()` is the single product the demographic field reads; C.2+ multiply more layers in."""
    _is_climate = True

    def __init__(self, base, a_seas: float = 0.0, phase: float = 0.0, period: int = SEASON_PERIOD_DEFAULT,
                 mean_factor: float = 1.0, interannual_amp: float = 0.0,
                 interannual_period: int = 0, interannual_phase: float = 0.0,
                 regime_amp: float = 0.0, regime_duration: int = 0, regime_recurrence: int = 0, rng=None,
                 caribou_amp: float = 0.0, caribou_period: int = 0, caribou_phase: float = 0.0,
                 steppe_mask=None):
        self._base = base
        self.a_seas = max(0.0, min(1.0, a_seas))
        self.phase = phase
        self.period = period
        # C.2 layers:
        self.mean_factor = mean_factor                          # eccentricity annual-mean brightening (≥1; baseline scalar)
        self.interannual_amp = max(0.0, min(1.0, interannual_amp))   # ENSO depression amplitude
        self.interannual_period = interannual_period            # steps (yr×12); 0 = off
        self.interannual_phase = interannual_phase
        # C.3 regime-shift (telegraph): two states {0 normal, 1 excursion}; geometric dwell times.
        self.regime_amp = max(0.0, min(1.0, regime_amp))        # CC depression while in excursion
        self.regime_duration = regime_duration                  # mean excursion length (steps); P(end)=1/duration
        self.regime_recurrence = regime_recurrence              # mean onset spacing (steps); P(onset)=1/recurrence
        self._rng = rng                                         # drives the telegraph (per-world, seeded)
        self._regime_state = 0                                  # current state (0/1); a sustained PLATEAU, not a wiggle
        self._regime_last_t = 0
        # C.4b caribou herd-swing (GRASS_STEPPE meat-channel quasi-cycle):
        self.caribou_amp = caribou_amp                          # amplitude about the mean (St. John 0.871)
        self.caribou_period = caribou_period                    # steps (yr×12); 0 = off
        self.caribou_phase = caribou_phase
        self._steppe_mask = steppe_mask                         # (N,N) bool [y,x]; None ⇒ layer inert
        self.t = 0

    def set_step(self, t: int) -> None:
        # Advance the regime telegraph once per forward step (state persists → a sustained plateau).
        if (self.regime_amp > 0.0 and self._rng is not None
                and self.regime_duration > 0 and self.regime_recurrence > 0):
            for _ in range(max(0, t - self._regime_last_t)):
                if self._regime_state == 0:
                    if self._rng.random() < 1.0 / self.regime_recurrence:
                        self._regime_state = 1                  # onset of an excursion
                elif self._rng.random() < 1.0 / self.regime_duration:
                    self._regime_state = 0                      # excursion ends
        self._regime_last_t = t
        self.t = t

    def season(self) -> float:
        if self.a_seas <= 0.0:
            return 1.0
        return (1.0 - self.a_seas) + self.a_seas * 0.5 * (
            1.0 + math.cos(2.0 * math.pi * self.t / self.period - self.phase))

    def interannual(self) -> float:
        """C.2 ENSO-like layer: a quasi-periodic DEPRESSION (bad years only, ≤1), period 2–7 yr. Refinement:
        irregular/stochastic ENSO; C.2 uses a single drawn period."""
        if self.interannual_amp <= 0.0 or self.interannual_period <= 0:
            return 1.0
        return 1.0 - self.interannual_amp * max(
            0.0, math.sin(2.0 * math.pi * self.t / self.interannual_period + self.interannual_phase))

    def regime(self) -> float:
        """C.3 regime-shift: a sustained CC PLATEAU while the telegraph sits in the excursion state (state·A_reg
        depression), 1.0 in the normal state. Multi-generational because the dwell time is ~100–500 yr ≫ a
        ~25-yr generation. NOT mean-reverting — it holds the level until the chain switches back."""
        if self.regime_amp <= 0.0:
            return 1.0
        return 1.0 - self.regime_amp * self._regime_state

    def mult(self) -> float:
        # temporal [0,1] layers: seasonal × interannual × regime-shift
        return self.season() * self.interannual() * self.regime()

    def meat_factor(self, x: int, y: int) -> float:
        """C.4b caribou herd-swing: a per-cell MEAT-channel multiplier (read by the economy's meat_pool, §4.5.5).
        A 40–90 yr quasi-periodic depression on GRASS_STEPPE cells ONLY (steppe_mask); 1.0 elsewhere / when off.
        Peak-pinned to 1.0; trough (1−a)/(1+a) (a=0.871 ⇒ ~0.069 = a ~93% peak-to-trough megafauna crash). The
        forage channel ((1−meat_frac)·S) is untouched — a herd crash is not a plant crash (supervisor choice B)."""
        if self.caribou_amp <= 0.0 or self.caribou_period <= 0 or self._steppe_mask is None:
            return 1.0
        if not self._steppe_mask[y, x]:
            return 1.0
        a = self.caribou_amp
        return (1.0 + a * math.cos(2.0 * math.pi * self.t / self.caribou_period + self.caribou_phase)) / (1.0 + a)

    def level(self, x: int, y: int) -> float:
        # mean_factor (eccentricity brightening) is the per-world baseline scalar (outside the [0,1] temporal mult)
        return self._base.level(x, y) * self.mean_factor * self.mult()

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._base, name)   # delegate width / height / consume / ...
