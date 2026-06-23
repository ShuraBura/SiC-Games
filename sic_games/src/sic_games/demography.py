"""Phase 1 Demographic stage — Step-1 core: Siler mortality + IBI reproduction.

Non-spatial, terrain-free. Imported by the Step-1 calibration harness
(`outputs/phase1_demography_calib/`) and, later, by the Phase-1 model for Step 2.

Mortality: Siler (1979) 3-component competing hazard, coefficients FIXED from a published
Aché fit (Gurven & Kaplan 2007, Table 2; blueprint M-1). The baseline (Makeham) term `a2` — in
the paper's words "exogenous mortality due to environmental conditions" — is the ONLY term the
world modulates (terrain risk / disease / nutrition synergy, Step 2); exposed via `a2_mult`
(default 1.0 → pure Aché schedule).

Units: coefficients are ANNUAL with age in YEARS; 1 model step = 1 MONTH. The monthly death
probability is `1 - exp(-h_year(age) / 12)`. See `tests/test_demography.py` for the ×12 guard
(monthly-stepped survivorship must reproduce the closed-form annual l(x)).

Blueprint: `blueprints/phase1/SiC_Games_P1_Demography_Siler_Blueprint.md`
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pydantic import BaseModel, Field

MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class SilerParams:
    """Siler competing-hazard coefficients (annual; age in years).

    h(x) = a1·exp(−b1·x) + a2 + a3·exp(b3·x)
      a1 — initial infant mortality rate;  b1 — infant decline rate
      a2 — age-independent (Makeham) baseline  ← the world modulates THIS
      a3 — initial adult mortality rate;  b3 — Gompertz rate (MRDT = ln2/b3)
    """

    a1: float
    b1: float
    a2: float
    a3: float
    b3: float

    def hazard(self, age_years: float, a2_mult: float = 1.0) -> float:
        """Annual mortality hazard at `age_years`. `a2_mult` scales ONLY the baseline term."""
        return (
            self.a1 * math.exp(-self.b1 * age_years)
            + self.a2 * a2_mult
            + self.a3 * math.exp(self.b3 * age_years)
        )

    def cumulative_hazard(self, age_years: float) -> float:
        """Closed-form H(x) = ∫₀ˣ h(t)dt (a2 unmodulated) — for survivorship / life tables."""
        a1, b1, a2, a3, b3 = self.a1, self.b1, self.a2, self.a3, self.b3
        return (
            (a1 / b1) * (1.0 - math.exp(-b1 * age_years))
            + a2 * age_years
            + (a3 / b3) * (math.exp(b3 * age_years) - 1.0)
        )

    def survivorship(self, age_years: float) -> float:
        """l(x) = exp(−H(x))."""
        return math.exp(-self.cumulative_hazard(age_years))

    def monthly_death_prob(self, age_months: float, a2_mult: float = 1.0) -> float:
        """P(die during this month) at `age_months`. Annual hazard → monthly-interval prob."""
        h = self.hazard(age_months / MONTHS_PER_YEAR, a2_mult)
        return 1.0 - math.exp(-h / MONTHS_PER_YEAR)


# Aché forest-period (Gurven & Kaplan 2007, Table 2; both sexes; the M-1 anchor).
# VALIDATED: reproduces e₀=36.5, e₁₅=38.3, e₄₅=21.3, l(15)=0.66, l(45)=0.43, modal adult death=71.
ACHE_FOREST = SilerParams(a1=0.157, b1=0.721, a2=0.013, a3=4.80e-5, b3=0.103)

# M-3 sex split (Hill & Hurtado 1996, Ch. 6, forest period): documented sex mortality-risk ratios
# male:female = 0.71 in CHILDHOOD (Aché have HIGHER female child mortality — sex-biased
# infanticide/neglect) and 1.47 in ADULTHOOD (standard pattern). Applied to the validated both-sexes
# Siler: scale a1 by the childhood ratio (female higher), the Gompertz a3 by the adult ratio (male
# higher), keep the Makeham baseline a2 SHARED and b1/b3 common, and preserve the sex-average =
# ACHE_FOREST. (Scaling a3 not a2 puts the female→male crossover in adolescence ~age 15-20 as the
# monograph reports; scaling the shared a2 would cross over far too early.) Maternal mortality is
# FOLDED INTO the all-cause female schedule
# (approach (ii)): the explicit per-birth term is 0 here; a maternal-removed fit (approach (a)) would
# set it > 0. [b's common is an approximation; the full age-specific sex curves are in the monograph's
# figures, not machine-readable.]
_CHILDHOOD_MF, _ADULT_MF = 0.71, 1.47


def _sex_split(both: SilerParams, childhood_mf: float = _CHILDHOOD_MF,
               adult_mf: float = _ADULT_MF) -> tuple[SilerParams, SilerParams]:
    """Split a both-sexes Siler into (female, male) by the M:F mortality-risk ratios, preserving the
    sex-average. Childhood ratio scales the infant/juvenile term a1 (female higher); adult ratio scales
    the Gompertz senescence term a3 (male higher); the Makeham baseline a2 is SHARED; b1,b3 common —
    so the female→male crossover lands in adolescence (~age 15-20), matching the monograph."""
    f_a1 = both.a1 * 2.0 / (1.0 + childhood_mf)
    f_a3 = both.a3 * 2.0 / (1.0 + adult_mf)
    female = SilerParams(f_a1, both.b1, both.a2, f_a3, both.b3)
    male = SilerParams(childhood_mf * f_a1, both.b1, both.a2, adult_mf * f_a3, both.b3)
    return female, male


ACHE_FOREST_FEMALE, ACHE_FOREST_MALE = _sex_split(ACHE_FOREST)

# De-warfared "natural mortality" baseline (Biome-Mortality, 2026-06-20; RESULTS R-15, MODEL_SPEC §4.6.1).
# The Aché TOTAL Siler includes ~50% frontier/external warfare (a contact-era artifact, supervisor: "does not
# belong in the model"). Stripping the external-warfare hazard by age (≈0 unweaned — infanticide KEPT —;
# ~0.35 ages 4–59; ~0.25 ≥60) and re-fitting a Siler to h_total·(1−w) gives this "natural mortality"
# schedule: **e₀=42.7, e₁₅=45.0** (vs Aché-total e₀=36.4). The change is concentrated in the Makeham a2
# (0.013→0.0081) — warfare was the age-independent adult hazard; infant a1 ~unchanged (infanticide kept).
# Used as the biome-mortality baseline: density-disease then regulates it DOWN to the realistic ~34–36
# (Aché-matched) WITHOUT the R-15 double-count. OPT-IN — pass these via DemographyConfig.siler_* in biome
# runs; the default config keeps the validated Aché-total (R-3) so existing runs/tests are unchanged.
ACHE_FOREST_NATURAL = SilerParams(a1=0.1611, b1=0.6775, a2=0.00813, a3=3.781e-5, b3=0.1025)


# ---------------------------------------------------------------------------
# Life-table metrics — for validating a schedule against the Aché anchors.
# ---------------------------------------------------------------------------
def life_expectancy(p: SilerParams, at_age_years: float = 0.0, x_max: float = 120.0,
                    dx: float = 0.01) -> float:
    """e(at) = ∫_at^xmax l(x) dx / l(at)  (trapezoidal). e(0) is life expectancy at birth."""
    n = int(round((x_max - at_age_years) / dx))
    total = 0.0
    for i in range(n + 1):
        x = at_age_years + i * dx
        w = 0.5 if (i == 0 or i == n) else 1.0
        total += w * p.survivorship(x)
    return (total * dx) / p.survivorship(at_age_years)


def modal_adult_death(p: SilerParams, adult_min: float = 15.0, x_max: float = 110.0,
                      dx: float = 0.05) -> float:
    """Age (≥ adult_min) that maximizes the death density l(x)·h(x) — the modal adult death age."""
    best_x, best_d = adult_min, -1.0
    steps = int(round((x_max - adult_min) / dx))
    for i in range(steps + 1):
        x = adult_min + i * dx
        d = p.survivorship(x) * p.hazard(x)
        if d > best_d:
            best_d, best_x = d, x
    return best_x


# ---------------------------------------------------------------------------
# Configuration (co-located with the engine it parameterizes).
# ---------------------------------------------------------------------------
class DemographyConfig(BaseModel):
    """Phase-1 demographic-stage parameters (blueprint §6).

    All modulator flags OFF → pure Aché schedule + IBI fertility (the Step-1 calibration world).
    Siler coefficients are FIXED constants from the published Aché fit (M-1) — NOT free knobs.
    """

    # --- mortality: Siler, FIXED from Gurven & Kaplan 2007 (both-sexes; M-1) ---
    siler_a1: float = 0.157
    siler_b1: float = 0.721
    siler_a2: float = 0.013
    siler_a3: float = 4.80e-5
    siler_b3: float = 0.103
    # M-3 sex split (Hill & Hurtado 1996): male:female mortality-risk ratios (childhood / adulthood)
    childhood_ratio_mf: float = Field(0.71, gt=0.0)
    adult_ratio_mf: float = Field(1.47, gt=0.0)

    # --- fertility (Aché-anchored window; IBI/fecundability tuned in Step-1) ---
    menarche_months: int = Field(180, ge=0)        # 15 yr — fertility onset
    menopause_months: int = Field(504, ge=0)       # 42 yr — last-birth ceiling
    ibi_refractory_months: int = Field(30, ge=0)   # lactational refractory [FREE — calibrate to IBI~37]
    fecundability: float = Field(0.12, ge=0.0, le=1.0)  # monthly birth prob past refractory [FREE]
    srb_male: float = Field(0.512, ge=0.0, le=1.0)      # secondary sex ratio (anchored ~105:100)
    # approach (ii): maternal mortality is FOLDED INTO the all-cause female Siler → explicit term 0.
    # Set > 0 only with a maternal-removed female schedule (approach (a)).
    maternal_mortality_per_birth: float = Field(0.0, ge=0.0, le=1.0)

    # --- modulator flags (Step-2; neutral/off in Step-1 calibration) ---
    enable_terrain_risk: bool = False
    enable_density_disease: bool = False
    enable_terrain_pathogen: bool = False
    enable_nutrition_synergy: bool = False
    enable_infanticide: bool = False
    # economy-fix (Tier-0): births scale with maternal reserve, capping the population BEFORE reserves
    # drain to the starvation floor → realistic equilibrium reserve (red-team 2b prerequisite)
    enable_energetic_fertility: bool = False
    # Resource-Ecology Phase C.2b: mother-linked provisioning. A mother's harvest that overflows her
    # reserve cap (otherwise wasted) is redirected to her dependent children (age < forage_age_min).
    # Flow-based (adults at the cap have no reserve headroom to give); the variance lands on the
    # mother's cell quality. Forage-only = the gathered-plant kin-sharing tier (Gurven 2004).
    enable_provisioning: bool = False
    # Biome-Mortality S0: lagged body-condition / immune-competence signal. When ON, the nutrition×disease
    # synergy reads a slow EMA of nutritional status (`_condition`) instead of the instantaneous (bang-bang)
    # reserve — so sustained undernutrition potentiates DISEASE mortality (Pelletier), routing the seasonal
    # squeeze through graded disease rather than the hard starvation floor (R-8/R-10 critical-path fix).
    enable_condition: bool = False
    condition_alpha: float = 0.25   # EMA rate; half-life ≈ ln2/−ln(1−α) ≈ 2.4 steps (months) of immune lag
    # Biome-Mortality S1: child-priority shortfall-sharing. The mother provisions her child's deficit not
    # only from wasted overflow (C.2b) but from her own reserve DOWN TO `provision_self_keep`·(her cap) —
    # so in a lean season the shortfall is *shared* (child dwells at a mild deficit instead of starving;
    # mother absorbs the deeper end). 1.0 = C.2b overflow-only (no reserve-sharing); lower = more priority.
    # The child-priority knob, gated so child starvation→≈0 but children still dwell (→ condition degrades).
    provision_self_keep: float = 1.0

    # --- Step-2 a2-modulator parameters (values + citations: MODEL_SPEC §4.3.3) ---
    risk_cap: float = Field(3.0, ge=1.0)        # max terrain-risk multiplier (red-team M-2: pin the scale)
    dens_delta: float = Field(1.0, ge=0.0)      # density-disease max excess [FREE — calibrated]
    dens_rho_half: float = Field(0.2, gt=0.0)   # density-disease half-saturation, agents/km² [FREE]
    mu_max: float = Field(2.5, ge=1.0)          # nutrition-synergy max (Pelletier 1994) [PROVISIONAL]
    a2_cap: float = Field(5.0, ge=1.0)          # cap on the a2_eff multiplier (red-team n-1)
    # Biome-Mortality S2 pathogen channel (Cashdan 2014; §4.6.3) — biome disease-ecology on a2.
    pathogen_gamma: float = Field(0.0, ge=0.0)  # BRACKETED strength (NPP exponent); 0 = OFF/flat. Sweep low/mid/high.
    pathogen_cap: float = Field(3.0, ge=1.0)    # symmetric cap [1/cap, cap] on pathogen_mult
    pathogen_npp_ref: float = Field(0.0, ge=0.0)  # reference NPP (Aché-forest biome); 0 → model uses terrain mean
    # Game/meat economy (the Carbon substrate; MODEL_SPEC §4.5.5, blueprint v2). The cell yield is split into
    # a forage stream (household, shared at κ=0) and a meat stream (band-pooled, Cred-weighted at κ>0 — the
    # status/show-off sharing of high-variance game, Kaplan & Hill 1985 / Hawkes 1991). `game_meat_frac` = the
    # diet animal fraction by biome (Cordain 2000 Table 2, terrestrial-renormalized; terrain.MEAT_FRAC).
    # Energy-conserving: at κ=0 forage+meat == the single stream (exact back-compat; default 0 = forage-only).
    enable_game: bool = False
    game_meat_frac: float = Field(0.0, ge=0.0, le=1.0)
    # G.3 stochastic meat returns (the Carbon-stage core variance; MODEL_SPEC §4.5.5 / Carbon scoping). The
    # cell meat pool is a mean-preserving lognormal draw with this CV (band-level correlated: ONE draw per cell,
    # all occupants share it). 0 = deterministic (back-compat). Per-biome anchors (terrain.GAME_KCAL_STD/mean):
    # forest 0.73, savanna 2.24, desert 0.29. The ordinary bad-streak variance, NOT a shock.
    game_meat_cv: float = Field(0.0, ge=0.0)
    # Carbon-on-substrate (Tier-1): meat/contest weight reads accumulated `cred` (status), not the `φ` trait,
    # when ON (else φ — preserves the Sugarscape contest tests). Founder cred is seeded lognormally
    # (cred_seed_sigma; median 1) and inherited at IBI birth as a noisy lineage copy `mother.cred·exp(N(0,σ))`
    # (cred_inherit_sigma). Decay/earning OFF in Tier-1 (persistent heritable status). See Carbon scoping bp.
    enable_cred_status: bool = False
    cred_seed_sigma: float = Field(0.0, ge=0.0)      # founder log-status spread; 0 = uniform (no hierarchy)
    cred_inherit_sigma: float = Field(0.0, ge=0.0)   # lineage-copy noise at birth; 0 = exact inheritance
    # Cred-vector (B+ stage). `cred` is the LINEAGE facet (ascribed). When `enable_prowess_facet`, the PROWESS
    # facet (achieved) joins the contest weight multiplicatively (Cobb–Douglas, equal within-domain exponents):
    # weight = ((cred+ε)·(prowess+ε))^κ. Default off → lineage-only = R-18 exact. Build step 1 ships the seam;
    # prowess GROWTH/decay (earned from provisioning) is step 2. See SiC_Games_P1_CredVector_BplusPaternity bp.
    enable_prowess_facet: bool = False

    def siler(self, sex: str | None = None) -> SilerParams:
        """Both-sexes schedule (sex=None) or the M-3 sex split (sex='female' / 'male')."""
        both = SilerParams(self.siler_a1, self.siler_b1, self.siler_a2, self.siler_a3, self.siler_b3)
        if sex is None:
            return both
        female, male = _sex_split(both, self.childhood_ratio_mf, self.adult_ratio_mf)
        return female if sex == "female" else male


def is_fertile(age_months: float, months_since_birth: int, cfg: DemographyConfig) -> bool:
    """Female fertility eligibility this month: within the fertile window AND past the IBI
    lactational refractory. (Sex check and the stochastic birth/maternal/SRB draws are the
    caller's job — the harness in Step 1, the Mesa model in Step 2.)"""
    return (
        cfg.menarche_months <= age_months < cfg.menopause_months
        and months_since_birth >= cfg.ibi_refractory_months
    )


# ---------------------------------------------------------------------------
# Step-2 a2 modulators — each gated by its DemographyConfig flag; the baseline (Makeham) a2 is the
# ONLY term the world modulates. Values + citations: MODEL_SPEC §4.3.3.
# ---------------------------------------------------------------------------
def risk_mult(risk_cell: float, risk_ref: float, cap: float) -> float:
    """Terrain accident/exposure: `min(cap, risk_cell/risk_ref)`. Mean-normalized (≈1 in average-risk
    terrain), capped — pins the risk *scale*, not just the mean (red-team M-2). Anchor: accidents
    ≈10% of HG deaths (Hill, Hurtado & Walker 2007)."""
    if risk_ref <= 0.0:
        return 1.0
    return min(cap, risk_cell / risk_ref)


def density_mult(density_per_km2: float, delta: float, rho_half: float) -> float:
    """Density-dependent disease: `1 + δ·ρ/(ρ+ρ_half)`, ρ in **agents/km²** (red-team m-3). Endemic /
    zoonotic — modest (Dunn 1968 / Houldcroft & Underdown 2023), NOT crowd-epidemic. The free lever."""
    return 1.0 + delta * density_per_km2 / (density_per_km2 + rho_half)


def pathogen_mult(npp_cell: float, npp_ref: float, gamma: float, cap: float) -> float:
    """Biome disease-ecology: pathogen load → multiplies a2. Pathogen PREVALENCE rises with
    productivity/warmth/wetness (Cashdan 2014 prevalence index by temperature+precipitation; §4.6.3).
    **PROXY (Biome-Mortality S2, path A):** driven by **NPP** because real spatial temperature+humidity are
    constant CL-1 placeholders — so this is the PARTIAL, *productivity-driven* gradient (NPP conflates warmth
    and wetness), NOT the real climate decomposition (that needs CL-1). Mean-normalised so
    `pathogen_mult(npp_ref) = 1` (the Aché-forest reference biome is neutral); other biomes deviate.
    **`gamma` is the BRACKETED magnitude** (0 → flat; report the gradient as a function of it — the
    prevalence→mortality step is unvalidated, §4.6.3). Symmetrically capped to [1/cap, cap]."""
    if npp_ref <= 0.0 or gamma <= 0.0:
        return 1.0
    m = (npp_cell / npp_ref) ** gamma
    return min(cap, max(1.0 / cap, m))


def synergy_mult(reserve: float, floor: float, full: float, mu_max: float) -> float:
    """Nutrition × infection synergy: `1 + (μ_max−1)·(1 − clamp((reserve−floor)/(full−floor)))`.
    Undernutrition multiplicatively potentiates mortality (Pelletier 1994): 1 at full reserve → μ_max
    near the floor."""
    span = full - floor
    frac = 0.0 if span <= 0.0 else max(0.0, min(1.0, (reserve - floor) / span))
    return 1.0 + (mu_max - 1.0) * (1.0 - frac)


def energetic_fertility_factor(reserve: float, floor: float, full: float) -> float:
    """Energetic fertility modifier (Step-2 economy fix): birth probability scales with maternal
    reserve — 1 at full reserve → 0 at the floor. Lean conditions depress fertility WITHOUT a hard
    cliff, so the population caps before reserves drain to the starvation floor."""
    span = full - floor
    if span <= 0.0:
        return 1.0
    return max(0.0, min(1.0, (reserve - floor) / span))
