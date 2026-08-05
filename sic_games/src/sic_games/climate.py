"""Climate stage (§4.1.6 star-mechanics seam) — C.1: obliquity → seasonal-amplitude lottery + the time-varying
`ClimateField` wrapper. Blueprint: blueprints/phase1/SiC_Games_P1_Climate_OrbitalLottery_Scoping.md.

Discipline (§4.1.6): the stellar mechanics BOUND the parameter draws; they do NOT run tick-by-tick. The
ClimateField multiplies the carrying-capacity field by a peak-normalized seasonal multiplier (the validated R-6
`run_2d` form), so the demographic substrate is UNCHANGED code — it just reads a time-varying field (§4.1.7
isolation). Later steps (C.2–C.4) fold interannual / regime-shift / catastrophe layers into `mult()`.
"""
from __future__ import annotations
import math
import random
from typing import Literal

from pydantic import BaseModel, Field

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

# §4.5.10 Storability-gated morph: per-cell seasonal amplitude keyed by BIOME CODE (terrain.BIOME_*). This is the
# TESTART/BINFORD storability signal — an aseasonal biome (equatorial forest) has no glut→lean cycle → no storage →
# immediate-return/egalitarian (Mbuti); a strongly-seasonal biome has a storable glut → delayed-return → complexity
# (NW-Coast-style). forest/savanna/grass(=llanos) are the lit-anchored A_SEAS_EARTH values; wetland/desert/mountain
# are PROVISIONAL (seasonal-but-not-directly-anchored — flagged, pending supervisor). water=0 (no land storage).
BIOME_SEASONAL_AMP_BY_CODE = {
    0: 0.00,   # WATER    — no land storage
    1: 0.30,   # WETLAND  — seasonal flooding [PROVISIONAL]
    2: 0.05,   # FOREST   — Aché aseasonal [LIT, A_SEAS_EARTH]
    3: 0.40,   # SAVANNA  — Hadza wet/dry [LIT, A_SEAS_EARTH]
    4: 0.60,   # GRASS    — llanos/Hiwi strongly seasonal [LIT, A_SEAS_EARTH llanos]
    5: 0.45,   # DESERT   — arid, strong seasonal rain/temperature swings [PROVISIONAL]
    6: 0.55,   # MOUNTAIN — montane strong seasonality / cold winters [PROVISIONAL]
}


def seasonal_amplitude_field(biome):
    """Per-cell seasonal amplitude [0,1] from a biome-code array (terrain.WorldFields.biome) — the storability
    signal for the storability-gated morph (§4.5.10). Vectorized lookup over BIOME_SEASONAL_AMP_BY_CODE."""
    import numpy as np
    amp = np.zeros(biome.shape, dtype=np.float64)
    for code, a in BIOME_SEASONAL_AMP_BY_CODE.items():
        amp[biome == code] = a
    return amp


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

# ── C.4c: llanos flood — a TWO-SIDED interannual-tail depression on GRASS_LLANOS *forage* ──────────
# Hamilton et al. 2004: Llanos del Orinoco inundated area 1,278–105,454 km² (median 25,374) — BOTH a failed
# flood (drought → aquatic collapse) and an over-flood (terrestrial drowning) hurt the forager, so the llanos
# interannual is two-sided `1 − amp·|sin θ|` (worst at either flood extreme), vs the generic one-sided ENSO.
# Same Layer-2 clock (period/phase) → the flood IS the llanos ENSO (El Niño suppresses Orinoco discharge), not a
# parallel Poisson (v2 anti-double-count). The amplitude is DRAWN per world over a LIT-BOUNDED band (the exact
# inundation-km²→forage-kcal mapping stays interpretive WITHIN the band, cf. the regime °C→CC% note):
#   lower 0.15 = Castello et al. 2015 (Lower Amazon flood-pulse fishery): climate explains ~18% of yield var,
#               per-extreme single-species swings ~15–20% — a MODERATE extreme year (protein channel). Their
#               "high and low waters exert EQUAL forcing" is the empirical basis for the TWO-SIDED form.
#   upper 0.45 = Sarmiento et al. 2004 (Apure llanos) MEASURED above-ground production drop in an exceptional-
#               flood year: TotalANPP 1996 (dyke-breach flood, 3 mo under water) 265–418 vs 1997 (normal)
#               601–659 g/m² (ungrazed) → −37 to −56%, central ~45%; their "both drought and water excess limit
#               production, even more in wet years" also confirms the two-sided form. Corroborated by Welcomme
#               1979 (fish yield ∝ flood extent). NOTE: a direct flood-year→production measurement (NOT the
#               earlier interpretive km²→kcal hand-wave).
LLANOS_FLOOD_AMP_MIN, LLANOS_FLOOD_AMP_MAX = 0.15, 0.45
LLANOS_FLOOD_AMP = LLANOS_FLOOD_AMP_MAX          # Sarmiento-anchored severe-end (used by unit tests / default cap)

# ── C.5: water→aggregation = the dry-season INTERCEPT-HUNTING game boost at water (§4.1.5) ──────────────
# Reframed after supervisor red-team: the ALWAYS-ON "good hunting near water" is ALREADY in the terrain
# (wateracc is 55% of the moisture term → NPP → forage+game, terrain.py:529), so it needs no climate layer.
# What C.5 adds is the genuinely-SEASONAL piece the ethnography flags as a distinct dry-season event: as
# ephemeral water dries, game FUNNELS to the few permanent waterholes and INTERCEPT hunting (night water-blinds)
# becomes viable — a high-return mode that switches on only in the late dry season (§4.1.5; NOT continuous).
# It is a meat-channel BOOST (not a cost / not a redistribution), on the savanna+llanos aggregation biomes,
# scaled by water proximity. Anchor (Hawkes 1991, §4.1.5 / game return-rate table):
INTERCEPT_RETURN_RATIO = 745.0 / 518.0           # Hadza intercept (water blinds, ~745 kcal/hr, late dry) vs encounter (~518) hunting
INTERCEPT_BOOST = INTERCEPT_RETURN_RATIO - 1.0   # ≈ +0.439 (+44%) game premium AT the waterhole in the late dry season
INTERCEPT_DRY_THRESHOLD = 0.75                   # threshold-like (§4.1.5): switches on only when normalized dryness
                                                 # (1−season)/A_seas ≥ this → ~late-dry quarter (≈ Hadza Aug–Oct)
# (Hiwi caiman 44→489 kg/km² ~11×, Hurtado & Hill 1987, corroborates that game concentrates at dry-season water.)


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
        # Layer 4c llanos flood (GRASS_LLANOS forage) — rides the same interannual ENSO clock, two-sided.
        llanos_flood_amp=rng.uniform(LLANOS_FLOOD_AMP_MIN, LLANOS_FLOOD_AMP_MAX),
        mean_temperature=flux_to_temperature(S),
        obliquity=eps, eccentricity=e, flux=S,
    )


class ClimateDriver:
    """A DETERMINISTIC, scriptable climate driver for CONTROLLED experiments (the dynamic-social benchmark
    harness; blueprint Stage 0 verdict / R-27 red-team #3). It REPLACES the stochastic regime telegraph with a
    known waveform on the regime channel: a callable `t → regime multiplier ∈ [0,1]` (1.0 = good times / no
    stress; <1 = a depressed multi-generation period). Wire it via `ClimateField(regime_driver=…)`.

    WHY (R-27): a single stochastic telegraph buried in a long mixed run gives a noisy, lag-confounded "response"
    — you cannot tell a social outcome (band fission, leader turnover, assabiyah swing) from a *random* climate
    crash. With a scripted "good-vs-bad periods at known times" driver, any change in a social metric is
    attributable to the SOCIAL response, so the leader-coherence / dynastic-cycle stages can be benchmarked
    cleanly. The stochastic `ClimateField` telegraph remains the *production* substrate once a mechanism is
    validated against this controlled driver.

    The named factories are EXPERIMENTAL-DESIGN constructs (NOT lit-anchored climate). For a realism-bounded
    stress set the depressed multiplier within the C.3 regime band (1−[0.10,0.15] = ±10–15% CC, REGIME_AMP_*);
    use 1−REGIME_AMP_TAIL = 0.70 (±30%) for an explicitly-flagged catastrophe. The driver is a pure function of
    `t` ⇒ fully reproducible (red-team #4)."""

    def __init__(self, fn, label: str = ""):
        self._fn = fn
        self.label = label

    def __call__(self, t: int) -> float:
        return max(0.0, min(1.0, self._fn(int(t))))

    @classmethod
    def flat(cls, mult: float = 1.0) -> "ClimateDriver":
        """Constant level (the CONTROL arm). `mult=1.0` ⇒ no regime stress at all — the clean baseline a stage's
        social metric is measured against."""
        return cls(lambda t: mult, f"flat({mult:g})")

    @classmethod
    def step(cls, t_onset: int, mult: float) -> "ClimateDriver":
        """A sustained downshift: 1.0 before `t_onset`, then `mult` for ever after — a permanent regime plateau
        (the Ibn-Khaldun "hard times set in" press)."""
        return cls(lambda t: 1.0 if t < t_onset else mult, f"step(t={t_onset},m={mult:g})")

    @classmethod
    def pulse(cls, t_onset: int, duration: int, mult: float) -> "ClimateDriver":
        """A single bad period of KNOWN onset + length: `mult` on [t_onset, t_onset+duration), 1.0 otherwise —
        the catastrophe-and-recovery waveform (measure fission DURING, re-aggregation AFTER)."""
        return cls(lambda t: mult if t_onset <= t < t_onset + duration else 1.0,
                   f"pulse(t={t_onset},d={duration},m={mult:g})")

    @classmethod
    def square(cls, period: int, mult: float, duty: float = 0.5, phase: int = 0) -> "ClimateDriver":
        """A periodic good/bad alternation (a DETERMINISTIC replacement for the telegraph): `mult` for the first
        `duty` fraction of each `period`, 1.0 otherwise. For dose-response across repeated, identical cycles."""
        bad = max(1, int(round(duty * period)))
        return cls(lambda t: mult if ((t - phase) % period) < bad else 1.0,
                   f"square(P={period},duty={duty:g},m={mult:g})")

    @classmethod
    def ramp(cls, t_start: int, t_end: int, mult: float) -> "ClimateDriver":
        """A gradual linear decline: 1.0 at `t_start` → `mult` at `t_end`, held at `mult` after. A slow squeeze
        (vs the `step` shock) — to separate press- from shock-driven social responses."""
        span = max(1, t_end - t_start)

        def f(t):
            if t <= t_start:
                return 1.0
            if t >= t_end:
                return mult
            return 1.0 + (mult - 1.0) * (t - t_start) / span
        return cls(f, f"ramp(t={t_start}->{t_end},m={mult:g})")

    @classmethod
    def piecewise(cls, breakpoints) -> "ClimateDriver":
        """The most general "known times" driver: `breakpoints = [(t0,m0),(t1,m1),…]`, step-held — the multiplier
        is `m_i` for t ∈ [t_i, t_{i+1}); 1.0 before the first breakpoint. step/flat are special cases."""
        bps = sorted(breakpoints)

        def f(t):
            m = 1.0
            for (ti, mi) in bps:
                if t >= ti:
                    m = mi
                else:
                    break
            return m
        return cls(f, f"piecewise({len(bps)}bp)")


class ClimateConfig(BaseModel):
    """Every climate channel as a switch and a value, on the same footing as `DemographyConfig`.

    WHY THIS EXISTS (R-106, 2026-08-04). `draw_world_climate()` above produces a full per-world climate
    lottery — orbital seasonality, eccentricity mean factor, ENSO interannual, the regime telegraph, caribou
    herd swings, llanos floods, temperature from stellar flux. It is unit-tested. **Its only callers were
    those tests.** Every `ClimateField` in the project, including `run_campaign.py`, was built as
    `ClimateField(base, a_seas=0.4, regime_driver=None)` and took the constructor default — 0.0 — for every
    other channel. So every experiment this project has run had a fixed seasonal sine and white noise, and no
    multi-year environmental variability at any timescale.

    That is material for the repeated no-cycles findings: Malthusian and secular dynamics were looked for in a
    world with no slow environmental variable. Those results are not wrong, but they say "no endogenous cycles
    under a flat climate", which is narrower than how they were recorded. It probably began as a deliberate
    control (`run_se0_controlled_climate`) that became the permanent default.

    DEFAULTS REPRODUCE THE OLD BEHAVIOUR EXACTLY — `a_seas = 0.4`, every variability channel off — so adopting
    this config changes no prior result. Each channel is INDEPENDENTLY ablatable, so a channel can be turned
    on and checked on its own, which is the whole point.
    """
    # ── MASTER ───────────────────────────────────────────────────────────────────────────────────────
    # Draw the per-world parameters from `draw_world_climate()` (the orbital + ENSO + regime + herd lottery)
    # instead of using the fixed values below. A drawn value is applied ONLY if its own channel flag is also
    # on, so the lottery never silently switches a layer on.
    enable_climate_lottery: bool = False
    # Which biome's Earth reference amplitude the obliquity draw is scaled against (A_SEAS_EARTH). The world
    # is a mix of biomes and `a_seas` is a scalar, so this names the reference explicitly rather than picking
    # one implicitly. "savanna" (0.40) is the Hadza mid-range and matches the fixed default below.
    lottery_a_earth_biome: Literal["forest", "savanna", "llanos"] = "savanna"

    # ── C.1 SEASONALITY (validated: R-6 run_2d form) ─────────────────────────────────────────────────
    enable_seasonality: bool = True
    # Peak-normalised seasonal amplitude A_seas = 1 - s_min. 0.40 = Hadza savanna [LIT, A_SEAS_EARTH]; it is
    # the value every campaign has used. Under the lottery this is drawn from obliquity instead.
    a_seas: float = Field(0.40, ge=0.0, le=1.0)

    # ── C.2a ECCENTRICITY annual-mean brightening ────────────────────────────────────────────────────
    # A scalar (>= 1) on the annual mean from orbital eccentricity. 1.0 = no effect. [Spiegel 2010 envelope]
    enable_eccentricity_mean: bool = False
    mean_factor: float = Field(1.0, ge=1.0)

    # ── C.2b INTERANNUAL / ENSO — a one-sided depression on a 2-7 yr clock ───────────────────────────
    # [Timmermann 2018] amplitude 0.20-0.40 of CC in marginal biomes; period 2-7 yr. This is the FAST
    # environmental variability the model has never had.
    enable_interannual: bool = False
    interannual_amp: float = Field(0.0, ge=0.0, le=1.0)
    interannual_period: int = Field(0, ge=0)        # steps (yr x 12); 0 = off
    interannual_phase: float = 0.0

    # ── C.3 REGIME SHIFT — a two-state telegraph, a sustained PLATEAU rather than a wiggle ───────────
    # [Wanner 2008] LIA global mean ~0.5 C => central +-10-15% CC; excursion DURATION 100-500 yr (LIA ~500)
    # is distinct from RECURRENCE 1000-2000 yr (Bond ~1500; Mayewski RCC). This is the SLOW variable a
    # secular-cycle test needs, and it has been off in every run.
    enable_regime_shift: bool = False
    regime_amp: float = Field(0.0, ge=0.0, le=1.0)
    regime_duration: int = Field(0, ge=0)          # mean excursion length in steps; P(end) = 1/duration
    regime_recurrence: int = Field(0, ge=0)        # mean onset spacing in steps; P(onset) = 1/recurrence

    # ── C.4b CARIBOU HERD SWING — quasi-periodic meat depression on GRASS_STEPPE only ────────────────
    # [St. John 2022, 43-herd database] amplitude 0.871 about the mean (peak 1.871x / trough 0.129x), median
    # period 40.5 yr over 40-90. Needs `steppe_mask`; without it the layer is inert whatever the amplitude.
    enable_caribou_swing: bool = False
    caribou_amp: float = Field(0.0, ge=0.0)
    caribou_period: int = Field(0, ge=0)
    caribou_phase: float = 0.0

    # ── C.4c LLANOS FLOOD — TWO-SIDED forage depression on GRASS_LLANOS, on the ENSO clock ───────────
    # [Sarmiento 2004 / Castello 2015] 0.15-0.45; both a failed flood and an over-flood hurt the forager, so
    # the form is `1 - amp*|sin theta|`. Rides the C.2b clock (the flood IS the llanos ENSO), so it needs
    # `enable_interannual` for a period. Needs `llanos_mask`.
    enable_llanos_flood: bool = False
    llanos_flood_amp: float = Field(0.0, ge=0.0, le=1.0)

    # ── C.5 INTERCEPT HUNTING — late-dry-season game boost at water ──────────────────────────────────
    # [Hawkes 1991] Hadza water-blind intercept ~745 vs encounter ~518 kcal/hr => +44% at the waterhole,
    # switching on only when normalised dryness >= 0.75. ClimateField's own default is ON, so this default
    # keeps it on and bit-exact.
    enable_intercept_hunting: bool = True


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
                 regime_driver=None,
                 caribou_amp: float = 0.0, caribou_period: int = 0, caribou_phase: float = 0.0,
                 steppe_mask=None, llanos_flood_amp: float = 0.0, llanos_mask=None,
                 water_weight=None, agg_mask=None, intercept_on: bool = True):
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
        # CONTROLLED-experiment hook: a deterministic ClimateDriver (t→[0,1]) that OVERRIDES the stochastic
        # telegraph on the regime channel (blueprint Stage 0 / R-27). None ⇒ the production telegraph (bit-exact).
        self.regime_driver = regime_driver
        self._regime_state = 0                                  # current state (0/1); a sustained PLATEAU, not a wiggle
        self._regime_last_t = 0
        # C.4b caribou herd-swing (GRASS_STEPPE meat-channel quasi-cycle):
        self.caribou_amp = caribou_amp                          # amplitude about the mean (St. John 0.871)
        self.caribou_period = caribou_period                    # steps (yr×12); 0 = off
        self.caribou_phase = caribou_phase
        self._steppe_mask = steppe_mask                         # (N,N) bool [y,x]; None ⇒ layer inert
        # C.4c llanos flood (GRASS_LLANOS forage-channel, two-sided interannual tail):
        self.llanos_flood_amp = max(0.0, min(1.0, llanos_flood_amp))
        self._llanos_mask = llanos_mask                         # (N,N) bool [y,x]; None ⇒ layer inert
        # C.5 water→aggregation = the dry-season INTERCEPT-HUNTING meat boost at water (savanna+llanos).
        self.intercept_on = intercept_on                       # flag, ON by default
        self._agg_mask = agg_mask                              # (N,N) bool [y,x]; savanna+llanos aggregation biomes
        self._water_weight = water_weight                     # (N,N) wateracc [0,1]; spatial water-proximity scale
        self.t = 0

    def set_step(self, t: int) -> None:
        # Advance the regime telegraph once per forward step (state persists → a sustained plateau). Skipped when
        # a deterministic regime_driver is in control (it needs no RNG and ignores _regime_state).
        if (self.regime_driver is None and self.regime_amp > 0.0 and self._rng is not None
                and self.regime_duration > 0 and self.regime_recurrence > 0):
            for _ in range(max(0, t - self._regime_last_t)):
                if self._regime_state == 0:
                    if self._rng.random() < 1.0 / self.regime_recurrence:
                        self._regime_state = 1                  # onset of an excursion
                elif self._rng.random() < 1.0 / self.regime_duration:
                    self._regime_state = 0                      # excursion ends
        self._regime_last_t = t
        self.t = t
        self._season_cached = None      # PERF: invalidate the per-step GLOBAL (cell-independent) temporal caches;
        self._regime_cached = None      # level(x,y) recomputes these ~n×candidates/step otherwise (profile hot spot)

    def season(self) -> float:
        c = getattr(self, "_season_cached", None)
        if c is not None:
            return c
        c = 1.0 if self.a_seas <= 0.0 else ((1.0 - self.a_seas) + self.a_seas * 0.5 * (
            1.0 + math.cos(2.0 * math.pi * self.t / self.period - self.phase)))
        self._season_cached = c
        return c

    def interannual(self) -> float:
        """C.2 ENSO-like layer: a quasi-periodic DEPRESSION (bad years only, ≤1), period 2–7 yr. Refinement:
        irregular/stochastic ENSO; C.2 uses a single drawn period."""
        if self.interannual_amp <= 0.0 or self.interannual_period <= 0:
            return 1.0
        return 1.0 - self.interannual_amp * max(
            0.0, math.sin(2.0 * math.pi * self.t / self.interannual_period + self.interannual_phase))

    def interannual_at(self, x: int, y: int) -> float:
        """Per-cell interannual: the generic one-sided ENSO everywhere, but a TWO-SIDED flood-deviation
        depression `1 − amp·|sin θ|` on GRASS_LLANOS cells (C.4c) — same Layer-2 clock, flood-shaped, REPLACING
        (not stacked on) the ENSO form so the flood is the llanos ENSO (no double-count)."""
        if self.interannual_period <= 0:
            return 1.0
        theta = 2.0 * math.pi * self.t / self.interannual_period + self.interannual_phase
        if (self.llanos_flood_amp > 0.0 and self._llanos_mask is not None and self._llanos_mask[y, x]):
            return 1.0 - self.llanos_flood_amp * abs(math.sin(theta))      # two-sided flood tail (llanos forage)
        if self.interannual_amp <= 0.0:
            return 1.0
        return 1.0 - self.interannual_amp * max(0.0, math.sin(theta))      # one-sided ENSO (everywhere else)

    def regime(self) -> float:
        """C.3 regime-shift: a sustained CC PLATEAU while the telegraph sits in the excursion state (state·A_reg
        depression), 1.0 in the normal state. Multi-generational because the dwell time is ~100–500 yr ≫ a
        ~25-yr generation. NOT mean-reverting — it holds the level until the chain switches back. A CONTROLLED
        `regime_driver`, when set, supplies this multiplier DETERMINISTICALLY (overriding the telegraph) for the
        benchmark harness."""
        c = getattr(self, "_regime_cached", None)
        if c is not None:
            return c
        if self.regime_driver is not None:
            c = self.regime_driver(self.t)
        elif self.regime_amp <= 0.0:
            c = 1.0
        else:
            c = 1.0 - self.regime_amp * self._regime_state
        self._regime_cached = c
        return c

    def mult(self) -> float:
        # temporal [0,1] layers: seasonal × interannual × regime-shift
        return self.season() * self.interannual() * self.regime()

    def meat_factor(self, x: int, y: int) -> float:
        """The per-cell MEAT-channel multiplier read by the economy's meat_pool (§4.5.5) = the product of the two
        meat-channel climate layers, which live on DISJOINT biomes (so at most one is ≠1 per cell):
          • C.4b caribou herd-swing — a depression on GRASS_STEPPE; • C.5 intercept hunting — a boost on
        savanna+llanos near-water cells in the late dry season. Forage capacity (level) is untouched by both."""
        return self._caribou_factor(x, y) * self._intercept_factor(x, y)

    def _caribou_factor(self, x: int, y: int) -> float:
        """C.4b: 40–90 yr quasi-periodic megafauna depression on GRASS_STEPPE meat (steppe_mask). Peak-pinned to
        1.0; trough (1−a)/(1+a) (a=0.871 ⇒ ~0.069 = ~93% peak-to-trough). 1.0 off-steppe / when off."""
        if self.caribou_amp <= 0.0 or self.caribou_period <= 0 or self._steppe_mask is None:
            return 1.0
        if not self._steppe_mask[y, x]:
            return 1.0
        a = self.caribou_amp
        return (1.0 + a * math.cos(2.0 * math.pi * self.t / self.caribou_period + self.caribou_phase)) / (1.0 + a)

    def _intercept_factor(self, x: int, y: int) -> float:
        """C.5 intercept hunting: a late-dry-season meat BOOST at water on the savanna+llanos aggregation biomes.
        `1 + INTERCEPT_BOOST·wateracc(x,y)` (Hadza 745/518 ≈ +44% AT the waterhole, tapering to 0 far from water),
        gated THRESHOLD-like (§4.1.5) — on ONLY when normalized dryness (1−season)/A_seas ≥ INTERCEPT_DRY_THRESHOLD
        (the late dry season). 1.0 when the flag is off / off-biome / no seasonality / outside the dry window."""
        if not self.intercept_on or self._agg_mask is None or self._water_weight is None:
            return 1.0
        if not self._agg_mask[y, x] or self.a_seas <= 0.0:
            return 1.0
        dryness = (1.0 - self.season()) / self.a_seas          # ∈ [0,1]; 1 at the dry trough
        if dryness < INTERCEPT_DRY_THRESHOLD:
            return 1.0                                          # not yet the late dry season → no intercept
        return 1.0 + INTERCEPT_BOOST * float(self._water_weight[y, x])

    def level(self, x: int, y: int) -> float:
        # mean_factor (eccentricity brightening) is the per-world baseline scalar (outside the [0,1] temporal mult).
        # Uses interannual_at(x,y) (C.4c llanos flood; == generic off-llanos). C.5 intercept hunting is a MEAT-
        # channel boost (meat_factor), NOT a forage/capacity change — so level() (forage capacity) is unchanged.
        return (self._base.level(x, y) * self.mean_factor
                * self.season() * self.interannual_at(x, y) * self.regime())

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._base, name)   # delegate width / height / consume / ...


def build_climate_field(base, cfg: "ClimateConfig | None" = None, fields=None, seed: int = 0):
    """Construct a `ClimateField` from a `ClimateConfig` — the ONE place a run's climate is assembled.

    Before this existed every harness hand-wrote `ClimateField(base, a_seas=0.4, regime_driver=None)` and
    silently took the 0.0 default for every other channel, so the ENSO / regime / herd / flood layers were
    built, tested, and never once in a run (R-106). Assembling it from a config means the channels appear in
    `config/mechanisms.toml` alongside the social ones and can be ablated one at a time.

    `fields` is a `WorldFields` (for the GRASS sub-biome masks C.4b/C.4c need); `seed` makes both the lottery
    draw and the regime telegraph deterministic per world.

    Defaults reproduce the historical call exactly: `a_seas=0.4`, everything else off.
    """
    # Imported here, not at module scope: terrain.py does not import climate.py today, but a module-level
    # import would create the cycle the moment it does, and the sub-biome codes are needed only on the two
    # GRASS paths.
    from sic_games.terrain import GRASS_LLANOS, GRASS_STEPPE

    cfg = cfg or ClimateConfig()
    drawn: dict = {}
    if cfg.enable_climate_lottery:
        drawn = draw_world_climate(random.Random(seed), A_SEAS_EARTH[cfg.lottery_a_earth_biome])

    def val(name):
        """The drawn value when the lottery is on, else the configured one."""
        return drawn[name] if name in drawn else getattr(cfg, name)

    # A CHANNEL ON WITH A ZERO MAGNITUDE IS THE DEFECT THIS PROJECT KEEPS FINDING — it reads as live in the
    # config dump and does nothing in the world, and every ablation of it scores INERT. Refuse it.
    # A channel's NEUTRAL value is not always 0: `mean_factor` is a multiplier whose no-op is 1.0, so a bare
    # `if not value` check would wave it through as configured while it did nothing.
    neutral = {"mean_factor": 1.0}

    def need(flag, *names):
        if not getattr(cfg, flag):
            return False
        dead = [n for n in names if val(n) == neutral.get(n, 0)]
        if dead:
            raise ValueError(
                f"ClimateConfig.{flag} is on but {', '.join(dead)} is at its neutral value — the channel "
                f"would run and do nothing. Set the value(s), or turn on enable_climate_lottery to draw "
                f"them.")
        return True

    kw: dict = dict(intercept_on=cfg.enable_intercept_hunting)
    kw["a_seas"] = val("a_seas") if need("enable_seasonality", "a_seas") else 0.0
    kw["mean_factor"] = val("mean_factor") if need("enable_eccentricity_mean", "mean_factor") else 1.0

    if need("enable_interannual", "interannual_amp", "interannual_period"):
        kw.update(interannual_amp=val("interannual_amp"),
                  interannual_period=int(val("interannual_period")),
                  interannual_phase=val("interannual_phase"))
    if need("enable_regime_shift", "regime_amp", "regime_duration", "regime_recurrence"):
        kw.update(regime_amp=val("regime_amp"), regime_duration=int(val("regime_duration")),
                  regime_recurrence=int(val("regime_recurrence")),
                  rng=random.Random(seed ^ 0x5EED))       # the telegraph needs its own stream
    if need("enable_caribou_swing", "caribou_amp", "caribou_period"):
        kw.update(caribou_amp=val("caribou_amp"), caribou_period=int(val("caribou_period")),
                  caribou_phase=val("caribou_phase"),
                  steppe_mask=_grass_mask(fields, GRASS_STEPPE, "enable_caribou_swing"))
    if need("enable_llanos_flood", "llanos_flood_amp"):
        # The llanos flood rides the C.2b clock — it IS the llanos ENSO, not a parallel process — so without
        # an interannual period it has no clock and would be inert.
        if not kw.get("interannual_period"):
            raise ValueError("ClimateConfig.enable_llanos_flood needs enable_interannual for its clock — the "
                             "flood rides the ENSO period rather than having one of its own.")
        kw.update(llanos_flood_amp=val("llanos_flood_amp"),
                  llanos_mask=_grass_mask(fields, GRASS_LLANOS, "enable_llanos_flood"))
    return ClimateField(base, **kw)


def _grass_mask(fields, subtype: int, flag: str):
    """(N,N) bool mask of a GRASS sub-biome, from `WorldFields.grass_subtype`."""
    gs = getattr(fields, "grass_subtype", None) if fields is not None else None
    if gs is None:
        raise ValueError(f"ClimateConfig.{flag} needs the world's `grass_subtype` field to build its mask; "
                         f"pass `fields=` to build_climate_field(). Without it the layer is inert.")
    return gs == subtype
