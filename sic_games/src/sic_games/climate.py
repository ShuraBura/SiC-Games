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
                 interannual_period: int = 0, interannual_phase: float = 0.0):
        self._base = base
        self.a_seas = max(0.0, min(1.0, a_seas))
        self.phase = phase
        self.period = period
        # C.2 layers:
        self.mean_factor = mean_factor                          # eccentricity annual-mean brightening (≥1; baseline scalar)
        self.interannual_amp = max(0.0, min(1.0, interannual_amp))   # ENSO depression amplitude
        self.interannual_period = interannual_period            # steps (yr×12); 0 = off
        self.interannual_phase = interannual_phase
        self.t = 0

    def set_step(self, t: int) -> None:
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

    def mult(self) -> float:
        return self.season() * self.interannual()               # temporal [0,1] layers (seasonal × interannual)

    def level(self, x: int, y: int) -> float:
        # mean_factor (eccentricity brightening) is the per-world baseline scalar (outside the [0,1] temporal mult)
        return self._base.level(x, y) * self.mean_factor * self.mult()

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._base, name)   # delegate width / height / consume / ...
