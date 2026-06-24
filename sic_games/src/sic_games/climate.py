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


class ClimateField:
    """Wrap a base carrying-capacity field (any object exposing `.level(x,y)`; width/height/consume/etc. are
    delegated) with the time-varying climate multiplier M(t). **C.1 = the seasonal layer only:**

        s(t) = s_min + (1−s_min)·½(1 + cos(2πt/P − φ)),   with  A_seas ≡ 1 − s_min

    range [s_min, 1], **peak-normalized to 1.0** — the EXACT validated R-6 form. The harness/model sets the
    current step via `set_step(t)` (R-6 `run_2d` pattern). **A_seas = 0 ⇒ s(t) ≡ 1.0 (aseasonal baseline,
    bit-exact).** `mult()` is the single product the demographic field reads; C.2+ multiply more layers in."""
    _is_climate = True

    def __init__(self, base, a_seas: float = 0.0, phase: float = 0.0, period: int = SEASON_PERIOD_DEFAULT):
        self._base = base
        self.a_seas = max(0.0, min(1.0, a_seas))
        self.phase = phase
        self.period = period
        self.t = 0

    def set_step(self, t: int) -> None:
        self.t = t

    def season(self) -> float:
        if self.a_seas <= 0.0:
            return 1.0
        return (1.0 - self.a_seas) + self.a_seas * 0.5 * (
            1.0 + math.cos(2.0 * math.pi * self.t / self.period - self.phase))

    def mult(self) -> float:
        return self.season()   # C.1: seasonal only

    def level(self, x: int, y: int) -> float:
        return self._base.level(x, y) * self.mult()

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._base, name)   # delegate width / height / consume / ...
