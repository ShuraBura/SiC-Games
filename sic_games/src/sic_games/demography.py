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
