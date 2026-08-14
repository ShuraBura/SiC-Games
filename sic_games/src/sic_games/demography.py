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
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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

    def monthly_death_prob(self, age_months: float, a2_mult: float = 1.0,
                           hazard_mult: float = 1.0) -> float:
        """P(die during this month) at `age_months`. Annual hazard → monthly-interval prob.

        `hazard_mult` scales the WHOLE age-specific hazard (unlike `a2_mult`, which scales only the
        Makeham term). Used by the kin/orphan channel: Hill & Hurtado's Table 13.1 controls for age and
        age², so its parameters are proportional effects on the total age-specific rate, not on a1.
        Threaded through `hazard()` ONLY — `cumulative_hazard()`/`survivorship()` stay unmodulated, as
        founder sampling, the ×12 guard and the life-table test depend on the unmodulated forms.
        """
        h = self.hazard(age_months / MONTHS_PER_YEAR, a2_mult) * hazard_mult
        return 1.0 - math.exp(-h / MONTHS_PER_YEAR)


# Aché forest-period (Gurven & Kaplan 2007, Table 2; both sexes; the M-1 anchor).
# VALIDATED: reproduces e₀=36.5, e₁₅=38.3, e₄₅=21.3, l(15)=0.66, l(45)=0.43, modal adult death=71.
ACHE_FOREST = SilerParams(a1=0.157, b1=0.721, a2=0.013, a3=4.80e-5, b3=0.103)

# ── THE DEMOGRAPHY MONITOR'S ANCHOR REGISTRY (R-106, 2026-08-14, supervisor request) ──────────────────────
# "We cannot expect social dynamics to work when the demography is skewed."
#
# THE CASE THAT PROVES IT. `band_med` read 23 against Birdsell's ~25 and looked like a PASS, on a population
# that was 54% children — about 11 ADULTS against Hill et al. 2011's 28.2 ADULTS. A marker read as passing
# while failing 2.5-fold, because nothing scored the age structure beside it. `docs/MARKER_MATRIX.md` #1
# already recorded this ("the 23/25 all-ages pass is carried by excess children") and it was still missed.
#
# EVERY BAND HERE IS COPIED FROM A FILED SOURCE. Nothing is invented. Two kinds of entry:
#   ("band", lo, hi, src)   a RANGE that exists in the literature. A hard PASS / OUT-OF-BAND verdict.
#   ("point", v, tol, src)  a single published value. `tol` is a REPORTING tolerance for flagging a
#                           DEVIATION — it is a display choice, NOT a calibration target, and no parameter
#                           is ever fitted to it. The reported quantity is the ratio to the anchor.
#
# DENOMINATOR TRAPS ARE ENCODED IN THE KEY NAMES. `surv_to_45` is l(45) FROM BIRTH, which is what Gurven &
# Kaplan's "survival 15→45 = 0.43" actually means; `surv_15_to_45_cond` is the conditional (0.65) and is
# deliberately NOT scored against it. `band_med_adults`, not `band_med`, carries Hill's 28.2. Five of this
# project's retractions were a real number read against the wrong denominator, so the names carry the unit.
_GK07 = "Gurven & Kaplan 2007 PDR 33(2) Table 2, Aché forest [VERIFIED]"
_HH44 = "Hill & Hurtado 1996 Table 4.4 p.141, 3 forager populations [VERIFIED VERBATIM]"
_HH8 = "Hill & Hurtado 1996 Tables 8.1/8.2, forest/contact/reservation [VERIFIED]"
DEMOG_ANCHORS: dict[str, tuple] = {
    # ---- age structure: the GATE. If these are out of band, everything above them is provisional. ----
    "frac_child": ("band", 0.287, 0.454, _HH44 + " — %<15 = 28.7 !Kung / 45.4 Yanomamö / 41.9 Aché"),
    "dependency_ratio": ("band", 0.598, 0.899, _HH44 + " — 0.598 !Kung / 0.866 Yanomamö / 0.899 Aché"),
    "sex_ratio_m_f": ("band", 0.896, 1.368, _HH44 + " — 0.896 / 1.202 / 1.368"),
    # ---- mortality. e15 is the HEADLINE, not e0: e0 is dominated by infant mortality, which is why the
    #      cross-forager e0 range is 21-37 while e15 sits near 38 everywhere. ----
    "realised_e0": ("band", 21.0, 37.0, _GK07 + " — cross-HG e0 range 21-37"),
    "e15": ("point", 38.5, 0.20, _GK07 + " — e15 = 38.5 REMAINING years at exact age 15"),
    "e45": ("point", 21.1, 0.25, _GK07 + " — e45 = 21.1 remaining years"),
    "surv_to_15": ("point", 0.66, 0.20, _GK07 + " — l(15) from birth"),
    "surv_to_45": ("point", 0.43, 0.25, _GK07 + " — l(45) FROM BIRTH, not conditional on reaching 15"),
    "modal_adult_death": ("band", 68.0, 78.0, _GK07 + " — adaptive lifespan 68-78; cross-HG modal avg 72"),
    # ---- fertility ----
    "realised_tfr": ("band", 4.69, 8.03, _HH8 + " — TFR 8.03 forest / 4.69 contact / 6.86 reservation"),
    "realised_ibi_med": ("band", 34.4, 49.4, _HH8 + " — IBI 37.6 / 49.4 / 34.4 months"),
    # ---- family ----
    "frac_motherless": ("point", 0.02, 0.50, "Hill & Hurtado Table 13.1 covariate — mother alive 0.98"),
    "frac_fatherless": ("point", 0.05, 0.50, "Hill & Hurtado Table 13.1 covariate — father alive 0.95"),
    # ---- group size: the marker the whole exercise is guarding ----
    "band_med_adults": ("point", 28.2, 0.25,
                        "Hill et al. 2011, 32 societies [VERIFIED, PDF read] — 28.2 ADULTS, NOT all-ages"),
    # ---- added from the 2026-08-14 literature survey ----
    # AGE AT FIRST BIRTH. Walker et al. 2006 Table 2 gives 15 forager societies between 16.2 (Wichi) and
    # 20.5 (Hiwi), median ~18.6. Gainj 25.7 and Turkana 22.2 are EXCLUDED — New Guinea highland
    # horticulturalists and pastoralists respectively, not foragers. A second, independent tie exists:
    # AFR = menarche + 4.5 yr (SD 1.6, n=14), so with menarche_months = 180 the model's own configuration
    # implies ~19.5. CAUTION from the survey: W06's figure is a mean over ALL adult women and is biased
    # UPWARD by age-estimation error — for the Hiwi it is 20.5 over all women but 17.9 over mothers under
    # 35, where ages are reliable. Prefer the LOW end. Measured here: 22.4-24.9, above every forager in
    # the sample.
    "age_first_birth_yr": ("band", 16.2, 20.5,
                           "Walker et al. 2006 AJHB 18(3) Table 2, 15 forager societies [VERIFIED]"),
    # MID-CHILDHOOD HAZARD. GK07 p.330 verbatim: "The mortality hazard has slowed to 0.01 by age 10,
    # doubled to about 0.02 by age 40". Ages 5-15 is the LOWEST-mortality band in a human life table and
    # the trough is broad. The tolerance is wide because the source states one significant figure.
    "m_5_15": ("point", 0.010, 0.50,
               "Gurven & Kaplan 2007 p.330 [VERIFIED VERBATIM] — hazard ~0.01/yr at age 10, cross-HG"),
}
# Markers deliberately NOT scored, because no anchor is filed. Reported as NO-ANCHOR rather than silently
# omitted, so the gap stays visible: a marker nobody scores is a marker nobody fixes.
DEMOG_UNANCHORED = ("srb_male_frac", "frac_double_orphan",
                    "frac_never_partnered_30", "frac_widowed_adult", "completed_parity_mean",
                    "cbr", "cdr", "e0_gap_f_minus_m")
# The age-structure markers that GATE everything above them in the benchmark ladder.
DEMOG_GATE = ("frac_child", "dependency_ratio")


def isogrowth_check(tfr: float, l15: float, r_measured_pct: float,
                    srb_male: float = 0.512, gen_length: float = 28.0) -> dict:
    """The GURVEN & KAPLAN ISO-GROWTH IDENTITY — a HARD consistency constraint, not another anchor.

    GK07 endnote 5 [VERIFIED via literature survey 2026-08-14]:

        R0  = (TFR / 2.06) · l25
        l25 = 0.9973·l15 − 0.0422        (their regression, R² = 0.98, p < 0.0001)
        R0  = exp(r · T),  T = 28 yr

    GIVEN ANY TWO OF {TFR, l15, r} THE THIRD IS FIXED. There is no freedom. That makes this the check the
    project has lacked: a run can be scored against its own internal consistency rather than only against
    point values. The identity reproduces GK07's own published claims — at l15 = 0.55 it returns TFR = 4.069
    for r = 0, which is the number they state.

    THE 2.06 IS A SEX-RATIO ASSUMPTION, NOT A CONSTANT. It converts TFR to daughters and embeds 1.06 males
    per female. This model configures `srb_male` (0.512 ⇒ 2.049), so the divisor is derived from the model's
    own value rather than hard-coded — importing 2.06 blind would be exactly the kind of borrowed constant
    that has cost this project five retractions.

    WHY THE IMPLIED GENERATION LENGTH IS RETURNED. T = 28 yr is GK07's forager value. A model whose age at
    first birth is late carries a LONGER generation, which lowers r for the same R0 — so a mismatch here can
    mean an inconsistent run OR simply a different T. Reporting `implied_gen_length` separates the two: if it
    comes back near 28 the discrepancy is real, and if it comes back at 35 the run's fertility SCHEDULE is
    displaced rather than its arithmetic being wrong. Measured 2026-08-14: this model's age at first birth is
    22-25 yr against a forager bracket of 16.2-20.5 (Walker 2006), so a long implied T is expected and is the
    same defect seen from another side.
    """
    nan = float("nan")
    if not (tfr and tfr > 0.0) or l15 is None or l15 != l15:
        return {"r_predicted_pct": nan, "R0": nan, "implied_gen_length": nan,
                "r_measured_pct": r_measured_pct, "consistent": None}
    l25 = 0.9973 * l15 - 0.0422
    if l25 <= 0.0:                      # l25 hits zero at l15 ≈ 0.0423; the regression is invalid below it
        return {"r_predicted_pct": nan, "R0": nan, "implied_gen_length": nan,
                "r_measured_pct": r_measured_pct, "consistent": None}
    R0 = tfr * (1.0 - srb_male) * l25
    if R0 <= 0.0:
        return {"r_predicted_pct": nan, "R0": R0, "implied_gen_length": nan,
                "r_measured_pct": r_measured_pct, "consistent": None}
    r_pred = math.log(R0) / gen_length
    implied_T = nan
    if r_measured_pct is not None and r_measured_pct == r_measured_pct and abs(r_measured_pct) > 1e-9:
        implied_T = math.log(R0) / (r_measured_pct / 100.0)
    ok = None
    if r_measured_pct is not None and r_measured_pct == r_measured_pct:
        ok = abs(r_pred * 100.0 - r_measured_pct) <= 0.5      # within half a percent per year
    return {"r_predicted_pct": r_pred * 100.0, "R0": R0, "l25": l25,
            "implied_gen_length": implied_T, "r_measured_pct": r_measured_pct, "consistent": ok}


def demography_health(row: dict) -> dict:
    """Score a trajectory row against DEMOG_ANCHORS and return verdicts. Pure function of the row.

    MODELLED ON `ClimateField.health()`, which returns UNREACHABLE / NEVER-FIRED verdicts and found three
    dark climate channels on its first real run. Every demographic failure of 2026-08-13/14 was visible in
    numbers already being printed; what was missing was something that said OUT-OF-BAND without a human
    going to look for it.

    THE GATE. `structure_ok` is False when frac_child or dependency_ratio is out of band. When it is False
    every marker ABOVE demography in the benchmark ladder — band size, connubium, marriage, settlement — is
    provisional, because it is being read on a population with the wrong age composition. That is not a
    stylistic warning: `band_med` 23 against Birdsell's ~25 read as a PASS on a population that was 54%
    children, i.e. ~11 adults against Hill's 28.2 ADULTS.

    Returns verdicts as a list of dicts and a one-line `banner` for the run log.
    """
    verdicts = []
    for key, spec in DEMOG_ANCHORS.items():
        v = row.get(key)
        if v is None or (isinstance(v, float) and v != v):        # missing or NaN
            verdicts.append({"marker": key, "value": v, "verdict": "NO-DATA", "src": spec[-1]})
            continue
        if spec[0] == "band":
            _, lo, hi, src = spec
            ok = lo <= v <= hi
            verdicts.append({"marker": key, "value": v, "lo": lo, "hi": hi, "src": src,
                             "verdict": "PASS" if ok else "OUT-OF-BAND",
                             "ratio": (v / lo if v < lo else (v / hi if v > hi else 1.0))})
        else:
            _, anchor, tol, src = spec
            ratio = (v / anchor) if anchor else float("nan")
            # DEVIATION, not FAIL: `tol` is a reporting threshold for display, never a calibration target.
            ok = abs(ratio - 1.0) <= tol
            verdicts.append({"marker": key, "value": v, "anchor": anchor, "tol": tol, "src": src,
                             "verdict": "PASS" if ok else "DEVIATION", "ratio": ratio})
    for key in DEMOG_UNANCHORED:
        if key in row:
            verdicts.append({"marker": key, "value": row.get(key), "verdict": "NO-ANCHOR",
                             "src": "no filed anchor — reported so the gap stays visible"})
    bad = [x for x in verdicts if x["verdict"] in ("OUT-OF-BAND", "DEVIATION")]
    gate = [x for x in verdicts if x["marker"] in DEMOG_GATE]
    structure_ok = all(x["verdict"] == "PASS" for x in gate) and bool(gate)
    n_scored = sum(1 for x in verdicts if x["verdict"] in ("PASS", "OUT-OF-BAND", "DEVIATION"))
    worst = sorted(bad, key=lambda x: -abs(x.get("ratio", 1.0) - 1.0))[:4]
    parts = ", ".join(f"{x['marker']}={x['value']:.3g}({x.get('ratio', float('nan')):.2f}x)" for x in worst)
    banner = (f"demography: {n_scored - len(bad)}/{n_scored} in band"
              + ("" if structure_ok else "  !! AGE STRUCTURE OUT OF BAND -> every marker above"
                                         " demography in the ladder is PROVISIONAL")
              + (f"  worst: {parts}" if parts else ""))
    return {"verdicts": verdicts, "n_scored": n_scored, "n_out": len(bad),
            "structure_ok": structure_ok, "banner": banner}

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

    `extra="forbid"` (added 2026-08-06). Pydantic's default is to SILENTLY IGNORE an unknown keyword, which
    means a harness can pass `band_risk_penalty=0.05` to a config that no longer has the field and run happily
    with a setting that does nothing — the run reports success, the manifest looks right, and the mechanism is
    absent. That is the precise failure this whole audit arc has been chasing, sitting one line from being
    impossible. It was found while deleting two dead knobs: the deletion itself would have been the trap,
    turning every stale call site into a silent no-op instead of an error.
    """

    model_config = ConfigDict(extra="forbid")

    # --- mortality: Siler, FIXED from Gurven & Kaplan 2007 (both-sexes; M-1) ---
    siler_a1: float = 0.157
    siler_b1: float = Field(0.721, gt=0.0)   # DIVISOR in the Siler cumulative hazard, (a1/b1)(1-exp(-b1*t)):
    #   zero is not a slow decay, it is a crash. Found by the stress battery (S2), which ran every parameter
    #   at its declared bounds and discovered this one had NO declared bounds at all.
    siler_a2: float = 0.013
    siler_a3: float = 4.80e-5
    siler_b3: float = Field(0.103, gt=0.0)   # DIVISOR in (a3/b3)(exp(b3*t)-1); same finding as siler_b1
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
    # ── KIN/ORPHAN CHILD MORTALITY (Hill & Hurtado 1996 Table 13.1; MODEL_SPEC §4.6.4; R-74) ──────────
    # SUPERSEDES `enable_infanticide` (below). Losing a parent — not birth-spacing — is the dominant
    # killing channel among the forest Aché, and it is a HAZARD MULTIPLIER, not a separate event.
    #
    # Table 13.1 ("Kin Effects on Child Mortality Rates during the Forest Period: Age 0–9"), a hazard model
    # controlling age, age², sex, mother's age, mother's age². Log-parameters → rate ratios:
    #   mother alive  −1.6277 (p<.001) ⇒ mother DEAD  ×exp(1.6277) = 5.09   ["about fivefold"]
    #   father alive  −1.1146 (p<.001) ⇒ father DEAD  ×exp(1.1146) = 3.05   ["about threefold"]
    #   parents divorced +1.0892 (p<.001) ⇒           ×exp(1.0892) = 2.97   ["threefold increase"]
    # Every OTHER kin category is null: adult brothers/sisters, grandmothers, grandfathers, aunts, uncles,
    # total kin helpers (p .156–.990) — "parents, but NOT other kin, have a strong and unique influence."
    # Mechanism: "A good deal of this effect is due to child homicide" + orphans "treated worse" — Table 5.1's
    # homicide/neglect is 39.7% of 0–3 deaths (child homicide 24, sacrificed-with-adult 11, left-behind 5,
    # parental infanticide only 7 of 131 = 5.3%). Effects are age-PROPORTIONAL (no significant age interaction).
    enable_orphan_mortality: bool = False
    orphan_mult_mother_dead: float = Field(5.09, ge=1.0)   # exp(1.6277) [LIT — Hill & Hurtado Tab. 13.1]
    orphan_mult_father_dead: float = Field(3.05, ge=1.0)   # exp(1.1146) [LIT]
    orphan_mult_divorced: float = Field(2.97, ge=1.0)      # exp(1.0892) [LIT]; both parents alive but unbonded
    orphan_max_age_years: float = Field(9.0, gt=0.0)       # Table 13.1's window is ages 0–9
    # DOUBLE-COUNT GUARD — normalise by E[mult] over the population's OWN children (`_orphan_e_mult_live`).
    # The Siler a1 was fit to OBSERVED Aché mortality, which already contains these deaths ("infanticide
    # KEPT"), so applying the multipliers raw would kill the same children twice.
    #
    # Why ENDOGENOUS and not the Aché constant? This model is **fertility-pinned** (R-16): held at r=0 its
    # equilibrium e₀ is ~28, whereas the Aché had TFR≈8 AND e₀≈36.5 — NRR>1, a GROWING population. A
    # stationary population must therefore orphan MORE children, and it does: measured E[mult] ≈ 3.28 vs the
    # Aché's 1.499, motherless ~10% vs their ~2% exposure (the analytic agrees: a2_mult≈3 ⇒ 10.7%). Dividing
    # by a constant fitted to a growing population moved eq_pop **−47%**; normalising by the population's own
    # mean gives **−2.4%** — i.e. exactly compositional: WHO dies is orphan-graded, HOW MANY stays
    # fertility-pinned. Same split R-16/R-18 established for the Cred hierarchy.
    orphan_normalize: bool = True
    # The Aché reference value, kept for documentation + the Table 13.1 arithmetic check. NOT used by the
    # model (which normalises endogenously). E[mult] at Tab. 13.1's own means (mother alive 0.98, father
    # alive 0.95, divorced 0.14 | both living):
    #   (0.98 + 0.02·5.09) · (0.95 + 0.05·3.05) · [P(¬both) + P(both)·(0.86 + 0.14·2.97)]
    #   = 1.0818 · 1.1025 · (0.069 + 0.931·1.2758) = 1.499
    orphan_e_mult: float = Field(1.499, gt=0.0)            # Aché REFERENCE ONLY — see `_orphan_e_mult_live`
    # "Mother's death in the first year of a child's life leads to mortality in 100% of the cases in our
    # sample" — an unweaned infant cannot survive its mother's loss. Small n; kept flaggable.
    orphan_infant_mother_lethal: bool = True
    # `enable_infanticide` WAS HERE AND IS DELETED (2026-08-06). It was a declared flag that no line of code
    # ever read — three separate audits had to re-discover that and write "UNIMPLEMENTED STUB" next to it, and
    # `C_ALLON` had to carry a special case to skip it. A switch that does nothing is not documentation, it is a
    # standing invitation to believe the mechanism exists.
    # THE SCIENCE IT ENCODED, KEPT: baseline infanticide is ALREADY inside the Siler infant curve, which was fit
    # to observed Aché deaths with "infanticide KEPT". An explicit mechanism would only add CONDITIONAL
    # infanticide, and Table 5.1 says parental infanticide is 5.3% of Aché infant deaths while infancy is nearly
    # sex-SYMMETRIC (38% of male vs 41% of female infant deaths are homicide/neglect). The sex bias is at ages
    # 4-14 (28% F vs 6% M) and comes from grave accompaniment, not infanticide. R-74's `enable_orphan_mortality`
    # is the mechanism that actually carries this channel, and it is built, anchored and ON.
    # economy-fix (Tier-0): births scale with maternal reserve, capping the population BEFORE reserves
    # drain to the starvation floor → realistic equilibrium reserve (red-team 2b prerequisite)
    enable_energetic_fertility: bool = False
    # INTAKE-based energetic fertility (supersedes the reserve-based branch above when ON). Measured
    # 2026-07-30: the reserve-based version is INERT by construction. Burn is ~68% of the floor-to-full span
    # per step, so an agent either re-saturates at the cap or dies within a step; there is no persistent
    # intermediate state. Post-harvest reserve reads 0.996 of full and the post-burn trough 0.318, each with
    # spread ~0.002 and ZERO response across a 5x density range, so the factor returns ~0.995 always and
    # fertility cannot respond to scarcity. Regulation therefore falls entirely on mortality (CDR +59% while
    # CBR moves 3%), which forces e0 = 1/CDR ~ 20.7 yr, median age 13 and 8-11% motherless.
    # INTAKE is the live signal the reserve level cannot be: p10 0.93 to p90 4.26 of requirement. Ellison's
    # energetics is the mechanism — fecundity tracks energy FLUX, not stored reserve.
    enable_intake_fertility: bool = False
    intake_ema_alpha: float = Field(0.04, gt=0.0, le=1.0)  # half-life = ln2/-ln(1-a) ~ 17 steps ~ 1.4 yr:
    #   slow enough that one bad month does not stop births, fast enough to track a multi-year squeeze
    # DEPENDENT LOAD (requires enable_intake_fertility). A mother's energy budget is not her own maintenance —
    # she must also cover what her juveniles cannot produce. Counting only her own needs understates the cost of
    # a further birth for a woman who already has dependents, which is the anchored driver of forager birth
    # spacing (Blurton Jones, Hadza; Kaplan's provisioning model). Denominator becomes own requirement + the sum
    # of her living juveniles' UNMET need (their requirement minus what they gathered themselves), so a child who
    # increasingly feeds itself costs her less — the load falls as they age, without any explicit schedule.
    # BUILT BUT CURRENTLY INERT — and the reason is a finding, not a wiring bug (2026-07-30, R-106).
    # Life-history IS on in the village/elite presets (eta_min 0.2, cons_min 0.3, mother-links 91%), yet only
    # 1.0% of juveniles run any deficit: measured juvenile eta med 0.529 against consumption_factor med 0.588,
    # and with adults harvesting ~1.7x their own burn a juvenile still gathers ~1.5x its requirement. So
    # CHILDREN IN THIS MODEL ARE NET FOOD PRODUCERS, which contradicts the Kaplan 2000 net-deficit anchor that
    # `consumption_factor` itself cites — the anchor human life-history theory rests on (long juvenile period,
    # provisioning, grandmothering). There are no dependents to load. Same root cause as the fertility brake:
    # at ~1.7x surplus intake everyone over-produces, including seven-year-olds.
    # UNBLOCK BY: recalibrating the juvenile eta ramp against Kaplan's production/consumption curves (foragers
    # do not break even until ~18-20 yr), NOT by tuning this mechanism. Kept default-OFF and bit-exact.
    enable_dependent_load: bool = False
    # PASSTHROUGH to the auto-built LifeHistoryConfig (the value's HOME is `LifeHistoryConfig
    # .eta_juvenile_exponent` — see config.py; do not document the anchor twice). 1.0 = the original linear
    # juvenile production ramp, bit-exact. >1 bends it toward Kaplan 2000's convex curve.
    lh_eta_juvenile_exponent: float = Field(1.0, gt=0.0)
    intake_fert_lo: float = Field(1.00, ge=0.0)   # intake = maintenance ⇒ no surplus for gestation/lactation
    intake_fert_hi: float = Field(1.20, gt=0.0)   # + the lactation increment (~+500 kcal/d on ~2500, FAO/IOM;
    #   pregnancy is ~+285 ⇒ +11%, lactation ~+20%, so full reproductive capacity needs ~1.2x maintenance)
    # SEDENTISM fertility (Neolithic Demographic Transition): birth-spacing SHORTENS with sedentism/complexity —
    # mobile foragers space births ~44 mo (carrying cost + prolonged lactational amenorrhea on a low-fat mobile diet;
    # !Kung, Howell), sedentary/complex/farming ~24-30 mo (no carrying cost + storable weaning foods → earlier weaning
    # → shorter amenorrhea; Sellen & Mace 2007), ~doubling the birth rate (Bocquet-Appel 2011). The mother's `ibi_
    # refractory_months` becomes society-dependent (SEDENTISM_IBI_MONTHS). Multiplies with `enable_energetic_fertility`
    # (nutritional-stress suppression stays on top). Default OFF ⇒ uniform IBI (bit-exact).
    enable_sedentism_fertility: bool = False
    # ── SOCIAL CAPITAL / STANDING — the village anchor with a REAL payoff (P6). Wiessner 1977 (!Kung *hxaro*): exchange
    # partnerships need **≥1 yr of reciprocal gifting** before the bond is "firm", each person sits in a network of
    # paths, and THAT NETWORK is what covers you in bad years. Status is also within-community (von Rueden) — a migrant
    # arrives a low-status outsider. So standing is a RELATIONAL third status facet: it accrues with TENURE among your
    # co-resident band and is largely LOST on leaving. Because `base_status` weights the harvest contest, the granary
    # draw AND mate choice, leaving is a real FITNESS cost — this is the anchor that holds a village together, and it
    # makes dispersal SELECTIVE (low-standing juniors leave; established/elite stay). Default OFF ⇒ facet absent, bit-exact.
    enable_standing: bool = False
    standing_tenure_rate: float = Field(0.083, gt=0.0, le=1.0)   # saturating accrual/step; 1/12 ⇒ ~63% after 1 yr (Wiessner "≥1 yr to firm")
    standing_leave_penalty: float = Field(0.4, ge=0.0, le=1.0)   # fraction of standing RETAINED on leaving your community
    standing_floor: float = Field(0.15, ge=0.0, le=1.0)          # newcomer baseline (never 0 — kin/lineage reputation travels)
    # ── STORE ANCHOR (P1). The cell granary is a REAL payoff (allocate_store_draw already prevents starvation) and is
    # CELL-BOUND — leaving abandons it — but the mover never sees it (`diffusion_select_target` weighs only forage S).
    # Testart 1982: delayed-return STORAGE is what makes foragers sedentary; you don't walk away from a full granary
    # for a 5% better patch. Unlike `standing` (a RELATIVE contest weight, which cancels on an empty cell), the store is
    # an ABSOLUTE place-bound value ⇒ it is what actually anchors. Perceived as the per-capita stored buffer amortised
    # over `store_anchor_horizon` steps. Default OFF (gain 0) ⇒ bit-exact.
    enable_store_anchor: bool = False
    store_anchor_gain: float = Field(1.0, ge=0.0)                # weight on the perceived per-capita granary buffer
    store_anchor_horizon: float = Field(24.0, gt=0.0)            # steps over which the stock is amortised into a per-step value (~2 yr)
    # Resource-Ecology Phase C.2b: mother-linked provisioning. A mother's harvest that overflows her
    # reserve cap (otherwise wasted) is redirected to her dependent children (age < forage_age_min).
    # Flow-based (adults at the cap have no reserve headroom to give); the variance lands on the
    # mother's cell quality. Forage-only = the gathered-plant kin-sharing tier (Gurven 2004).
    enable_provisioning: bool = False
    # Newborn→adult LIFE-HISTORY transition (Kaplan 2000 cooperative breeding): when ON, the model auto-uses a
    # MONTH-scaled LifeHistoryConfig (forage_age_min=180=15yr, forage_age_max_offset=120=10yr) so a child's
    # production (η ramp 0.2→1), maintenance (0.3→1) and reserve (0.3→1) all ramp over childhood — the graded
    # juvenile deficit that provisioning covers. Fixes the gap where lh_config was never passed → newborns foraged
    # at full adult rate. Pair with enable_provisioning (feed the deficit). Default OFF ⇒ no juvenile penalty.
    enable_life_history: bool = False
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
    # ── DENSITY-DISEASE REFERENCE NORMALISATION (R-106, 2026-08-13) ────────────────────────────────────────
    # THE DEFECT. `a2_mult` multiplies three modulators into Siler's Makeham term. TWO of them are
    # reference-normalised so that the ANCHOR CONDITION returns exactly 1.0 — `risk_mult` divides by
    # `risk_ref` ("≈1 in average-risk terrain") and `pathogen_mult` is "mean-normalised so
    # pathogen_mult(npp_ref) = 1 (the Aché-forest reference biome is neutral)". `density_mult` is NOT. It
    # returns 1.0 only at ρ = 0, an EMPTY WORLD.
    #
    # WHY THAT IS A DOUBLE-COUNT. Gurven & Kaplan 2007 fitted a2 = 0.0130 on Aché foragers who were LIVING AT
    # A REAL DENSITY, so that coefficient already contains whatever density-dependent disease those people
    # experienced. Multiplying it again at the same density charges for it twice.
    #
    # MEASURED SIZE. `dens_rho_half` = 0.2/km² sits ABOVE the whole ethnographic range (Binford packing
    # 0.091/km²; Tallavaara observed HG median 0.119/km²; this model's own Tallavaara capacity at its terrain
    # median NPP ≈ 0.053/km²), so every real forager density lies on the steep rising limb. At Binford's own
    # anchor the unnormalised term already returns 1.94x. The measured non-starvation hazard runs 1.56x the
    # configured Siler, and realised e0 is 17.7 yr against a configured 36.6.
    #
    # AND THE DYNAMICS AMPLIFY IT. `aggl_beta` = 1.15 gives increasing returns to crowding, so agents pack
    # into cells of ~71 (0.714/km², EIGHT times the Binford anchor and 3.6x past half-saturation), which drives
    # the term to 3.34x against its 4.0 ceiling. The error is in the maths; the agglomeration makes it large.
    #
    # THE FIX INTRODUCES NO NEW NUMBER. `dens_rho_ref` defaults to Binford 2001's packing threshold, which is
    # already filed (LITERATURE.md: "forager packing threshold 9.098 persons/100 km² = 0.091/km²"). Default
    # OFF ⇒ every prior run stays bit-exact.
    enable_density_reference: bool = False
    dens_rho_ref: float = Field(0.091, gt=0.0)  # agents/km² at which density_mult == 1 [ANCHORED, Binford 2001]
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
    # all occupants share it). 0 = deterministic (back-compat). The ordinary bad-streak variance, NOT a shock.
    #
    # ANCHOR = `terrain.MEAT_CV` — measured DAY-TO-DAY meat CV (forest/Aché 1.97, desert/Martu 2.92, savanna/
    # Hadza-big-game 5.29), or `terrain.HUNT_CV` = 2.11 for a generic forager. **NOT `GAME_KCAL_STD/mean`**
    # (forest 0.73, savanna 2.24, desert 0.29), which is what this said until R-72: those are SPATIAL cross-cell
    # spreads (a spread across 7 species' *means* for forest, 3 hunt types for desert) and this draw is TEMPORAL
    # — fresh every step, per cell. The old anchor understated forest 2.7× and desert 10×. Runs predating R-72
    # (R-18/19/20, society benchmark, paternal calib) hardcode 0.73 = the mis-anchored forest value.
    game_meat_cv: float = Field(0.0, ge=0.0)
    # ── PER-BIOME two-stream economy (wired 2026-08-08; RESULTS Addendum 37) ────────────────────────────────
    # Until this date both quantities above were SCALARS, so a campaign gave every biome the same diet split and
    # the same meat variance. MODEL_SPEC §4.5.5 said so ("`mf` is a scalar config ... the per-biome
    # `terrain.MEAT_FRAC` dict is the home for a future per-cell wiring"), and Addendum 36 measured the
    # consequence: no biome signal reached the harvest at all, because `game_kcal` is not read either.
    #
    # Each flag reads the cell's biome from an ALREADY ANCHORED dict. Neither introduces a new number.
    #   enable_biome_meat_frac → `terrain.MEAT_FRAC`  (Cordain 2000 Table 2, terrestrial-renormalized)
    #   enable_biome_meat_cv   → `terrain.MEAT_CV`    (cchunts day-to-day CV; Hawkes 1991 for the Hadza)
    #
    # ABSENT BIOMES FALL BACK, AND THE FALLBACK DIFFERS BY DICT — because the two dicts document different
    # reasons for absence. `MEAT_FRAC` omits WETLAND deliberately ("a gap, not a measured zero" — a 0.0 there
    # would assert that wetland foragers eat no meat), so an absent biome takes the SCALAR `game_meat_frac`.
    # `MEAT_CV` omits GRASS/MOUNTAIN/WETLAND for want of a calibration people, and terrain.py's own rule for
    # that case is `HUNT_CV` = 2.11, the biome-INVARIANT measured hunting CV — so an absent biome takes it.
    # Do not "fix" either fallback to 0.0; both zeros would be claims that no source supports.
    #
    # Both default False ⇒ every prior run stays bit-exact. `enable_game` and `game_meat_frac > 0` still gate
    # the whole two-stream path, so the scalar remains the master switch as well as the fallback value.
    enable_biome_meat_frac: bool = False
    enable_biome_meat_cv: bool = False
    # ── VILLAGE IDENTITY: co-residence dissolves band identity (2026-08-12) ────────────────────────────────
    # THE GAP THIS FILLS. Birdsell's nesting is already filed in LITERATURE.md — band ~25 → horde/local group
    # ~40 → dialectal tribe ~500 — and the model implements ONLY the band level. Nothing above it exists, so
    # co-residence has no effect on identity anywhere in the code. MEASURED consequence: a 204-person
    # settlement contains **45 distinct bands** of ~4-5 co-resident members each. A "village" is a spatial
    # coincidence of strangers, not a community, which is why every fission-cleavage rule tested returns a
    # 1-4 person splinter (see the budding investigation, 2026-08-12).
    #
    # `_maintain_bands` cannot do this: its FUSION branch fires only below `band_merge_size` (10), a rescue
    # rule for dying remnants. Bands sit at equilibrium between merge 10 and split 45 and never combine.
    #
    # THE RULE. An agent accrues co-residence at whichever settlement it is within `settle_radius` of (the
    # model's own `_nearest_settlement`). Past `village_identity_months` it adopts that village's identity.
    # Leaving resets the clock — so this is per-agent tenure, not a global timer, and it degrades gracefully
    # when a settlement dissolves.
    #
    # THE TIMESCALE IS THE MODEL'S OWN COMING-OF-AGE CONSTANT, not a new number: 180 months = 15 yr =
    # `menarche_months`. Mechanism — identity is inherited at birth, so a merged identity consolidates when
    # the first cohort born after aggregation reaches adulthood. Half a generation (the model's mean age at
    # reproduction is ~28 yr from the Table 8.2 schedule). Supervisor decision 2026-08-12, after the
    # alternatives (~1 yr Wiessner hxaro = a DYADIC partnership, wrong quantity; ~28 yr full generation =
    # slower than the 42-yr window in which the settlement bifurcation is decided) were costed.
    enable_village_identity: bool = False
    village_identity_months: int = Field(180, ge=1)   # = menarche_months; NOT an independent number
    # ── BUD SITE SEPARATION: a daughter village's catchment must not overlap its parent's (2026-08-12) ─────
    # THE ASYMMETRY. `_maintain_settlements` holds a site while >= `settle_min_pool` (40) people are inside its
    # (2·settle_radius+1) = 5-cell block, but budding only required a daughter 3 cells away. Two sites 3 apart
    # share 10 of their 25 catchment cells, so each counts the OTHER's residents toward its own survival test.
    # MEASURED: ~110 settlements at mean spacing 3.79 cells, mean on-site occupancy 15.8 against a 40-person
    # requirement — individually unviable sites propping each other up. Combined with a fission cleavage that
    # sheds a median of TWO people (the kinship comparison excludes the 97% who are equidistant), every
    # micro-splinter founded a settlement that survived on its neighbours. That is the budding runaway.
    # ON ⇒ minimum separation 2·settle_radius+1, so catchments are DISJOINT and a daughter must hold its own
    # pool. Default OFF ⇒ bit-exact.
    enable_bud_site_separation: bool = False
    # ── EXCLUSIVE VILLAGE MEMBERSHIP: settlement spacing becomes EMERGENT (2026-08-12) ─────────────────────
    # THE SAME DEFECT, TREATED AT ITS CAUSE INSTEAD OF ITS GEOMETRY. `_maintain_settlements` counts every
    # person inside a site's (2*settle_radius+1) window, and those windows overlap whenever sites are closer
    # than that, so neighbouring villages each count the SAME people toward their own survival threshold.
    # ON => each agent is counted for exactly ONE village, the nearest. Villages COMPETE for members rather
    # than sharing them, so a village sited too close to another cannot assemble its own pool and dissolves.
    # SPACING IS THEN AN OUTCOME, NOT A CONSTANT -- supervisor directive 2026-08-12, "we need that distance
    # emergent", after the geometric rule above was found to hard-code 5 cells = 50 km against a filed anchor
    # of ~20 km for disjoint forager catchments (Vita-Finzi & Higgs 1970: ~10 km site exploitation radius, the
    # two-hour walk; Lee's !Kung agree). `enable_bud_site_separation` is retained default-OFF purely as the
    # ablation control for "geometry alone" vs "competition". Default OFF => bit-exact.
    enable_exclusive_village_membership: bool = False
    # ── EMERGENT VILLAGE FOUNDING: one rule for every village (supervisor spec 2026-08-12) ─────────────────
    # "They travel until they find a suitable place for a village that is more attractive than being a roving
    #  band -- just like any village forms. So a fitting cell with proto-ag or fishing potential, out of
    #  catchment range of other villages."
    # Replaces the ranked-candidate scan, which was measured to be a MAP-COVERAGE parameter wearing a spacing
    # parameter's name: it sorts storable cells by S_pot descending and stops at 40, so `aggregation_site_sep`
    # governed how much of the map was eligible. At sep=2 (20 km, the ethnographic value) all 40 candidates sat
    # in a 9x79 sliver of the single best ridge and ZERO villages formed. Founding is now evaluated where
    # people ACTUALLY ARE: fitting cell + settle_min_pool within settle_radius + outside every existing
    # village's catchment (anchored to settle_catchment_radius = Vita-Finzi & Higgs 1970's ~10 km forager site
    # exploitation territory, [VERIFIED]). No candidate list, no site cap, no separation constant.
    enable_emergent_village_founding: bool = False
    # ── BUD-FOUNDING BYPASS REMOVED: settlement founding is occupancy-gated for EVERY path (2026-08-12) ────
    # `_found_settlements_by_occupancy` already requires settle_min_pool (40) people within settle_radius
    # before a settlement exists -- an emergent, occupancy-gated rule. Budding SKIPPED it and created a site
    # outright, so a faction of TWO (the measured median: the kinship cleavage excludes the 97% of villagers
    # equidistant from both leaders) founded a full settlement. ~1,700 settlements manufactured out of pairs
    # of people in 400 steps. That asymmetry is the generator of the runaway, and no downstream rule could
    # absorb it -- five were built and measured, all five failed (min-faction share silenced budding entirely;
    # village identity was inert against the churn; parent-only separation changed nothing; global separation
    # worked but imposed 50 km against a ~20 km filed anchor, Vita-Finzi & Higgs 1970; exclusive membership
    # raised churn rather than spacing).
    # ON => a bud RELOCATES its faction and splits the band, but founds NO site. The daughter becomes a
    # settlement only where people actually gather, via the rule every other path already obeys. Settlement
    # SPACING IS THEN EMERGENT and no distance constant exists anywhere in the model -- supervisor directive
    # 2026-08-12, "we need that distance emergent". This REMOVES a rule rather than adding one.
    # Default OFF => bit-exact.
    enable_bud_requires_occupancy: bool = False
    # ── Storage (delayed-return economy; the sedentism/inequality precursor — Testart 1982, Woodburn 1982,
    # Binford 2001). FLAGGABLE. In the OVERWINTERING zone (cell mean temp ≤ storage_temp_threshold_c ≈ Binford's
    # Effective-Temperature 15.25 °C storage threshold) an agent banks a `storable_fraction` of its harvest
    # OVERFLOW (intake above the reserve cap — otherwise wasted/given away) into a per-agent store (cap =
    # store_capacity_reserves × the reserve cap), then DRAWS it down in the lean season to stay one step above
    # the starvation floor. Warm/aseasonal cells never accumulate (immediate-return → egalitarian, by
    # construction — Aché/Hadza/Hiwi/!Kung). Default OFF = exact back-compat. (Per-agent store is v1; the
    # collective-vs-individual grain + the storage→inequality morph is the next step.)
    enable_storage: bool = False
    storable_fraction: float = Field(0.7, ge=0.0, le=1.0)        # fraction of overflow that is storable — lit ~0.5–0.8 (strongly-seasonal storers live mostly off stores; grain 50–70% stored) [LIT-CALIBRATED, storage survey]
    # RESOURCE-DEPENDENT STORABILITY (Testart 1982: it's the STORABLE seasonal resources — grain, nuts, dried fish —
    # that enable sedentism, NOT perishable fresh forage/meat). When enabled, storable_fraction becomes a per-cell
    # weighted average of the resource mix's storabilities: Σ(resource·s_r)/Σ(resource), s_grain 0.85 / s_fish 0.80 /
    # s_forage 0.15 / s_game 0.35 (STORABILITY_BY_RESOURCE). So grain/fishing cells accumulate granaries → sedentism/
    # complexity, while fresh-forage cells can't store → stay mobile (the Testart distinction). Default OFF ⇒ scalar, bit-exact.
    enable_resource_storability: bool = False
    store_capacity_reserves: float = Field(12.0, ge=0.0)        # store cap = this × reserve cap. reserve_full≈1.33 mo BURN ⇒ 12≈16 mo ≈ Halstead 1–2 yr granary (annual cycle + bad-year buffer). Old 3 (=4 mo) was far too low. [LIT-CALIBRATED, storage survey]
    storage_temp_threshold_c: float = Field(15.25)             # Binford ET 15.25 °C → model mean-temp proxy [CALIBRATION]
    storage_decay: float = Field(0.0, ge=0.0, le=1.0)          # S.3 per-step spoilage/maintenance loss (0 = off). Realistic traditional ≈ 0.02/mo (~22%/yr; lit 10–30%/yr) [LIT-CALIBRATED when on]
    # STORABILITY-GATED MORPH (blueprint …_StorabilityGatedMorph; R-45): gate the overwintering STORE on the cell's
    # biome SEASONAL AMPLITUDE (Testart/Binford storability) instead of the constant-placeholder temperature — an
    # aseasonal biome (forest, amp 0.05) can't store → egalitarian; a seasonal biome (savanna 0.40, grass 0.60)
    # stores → surplus → complex. Makes the society MORPH fit the biome. Default OFF ⇒ the temperature gate (bit-exact).
    storage_seasonality_gated: bool = False
    storage_seasonality_threshold: float = Field(0.25, ge=0.0, le=1.0)  # storage viable where biome amp ≥ this (above forest 0.05, below savanna 0.40) [PROVISIONAL]
    # SEASONAL-AQUATIC-GLUT MORPH (blueprint …_StorabilityGatedMorph v3; R-46/R-47): the ANTHROPOLOGICALLY CORRECT
    # driver of forager complexity is a dense STORABLE resource = a SEASONAL AQUATIC GLUT — the anadromous run /
    # seasonal fishery that must be stored through the lean season (NW-Coast salmon; Testart/Kelly/Ames). Storage
    # stays a broad survival BUFFER (marginal biomes cache → survive); COMPLEXITY requires the band's
    # mean(wateracc) × mean(seasonal_amplitude) ≥ threshold. So an ASEASONAL watery forest (Mbuti) stays EGALITARIAN
    # despite rivers, a DRY seasonal desert (Ju) stays egalitarian for lack of water; only SEASONAL-WATERY bands
    # (montane salmon rivers) morph COMPLEX. SEPARATES survival-storage from complexity. Default OFF ⇒ bit-exact.
    morph_aquatic_gated: bool = False
    morph_aquatic_threshold: float = Field(0.15, ge=0.0, le=1.0)  # complex needs seasonal aquatic glut mean(wateracc×seas_amp) ≥ this [PROVISIONAL]
    # R-103 STRATIFICATION-INEQUALITY GATE. The morph classifier calls a band "stratified" on high MEAN surplus
    # (surplus_frac ≥ 0.7), but stratification is UNEQUAL control of surplus, not affluence — Testart's own chain
    # is storage → wealth DIFFERENTIALS → heritable rank, and the level-only test skipped the differentials step.
    # Diagnosed 2026-07-22: a uniformly-affluent packed world (flat-tropical) read 45% stratified while having the
    # LOWEST cred-Gini of any arm (0.29) — the label ran OPPOSITE to inequality. When ON, a would-be stratified
    # band must also show within-band cred concentration ≥ `stratification_gini_min`. Default OFF ⇒ bit-exact.
    # R-105 BUGFIX TOGGLE — the AGGLOMERATION CEILING GAP. Point-mode agglomeration adds a SUPERLINEAR
    # occupancy bonus (n**aggl_a - n) to ANY occupied cell, but the R-63 carrying-capacity ceiling was gated on
    # `(cx,cy) in _settlement_sites`. So a NON-settlement cell got unbounded increasing returns: more crowding →
    # superlinearly more food → more people. Diagnosed R-104: a run sat at pop ~3000 for 1750 steps, then
    # surplus_med saturated at 1.0 and pop went 3259→97551 with ZERO starvation at 61 agents/cell. ON ⇒ the
    # ceiling also applies wherever the agglomeration bonus is applied. Default OFF ⇒ bit-exact with every
    # pre-R-105 result (which were all run with the gap open).
    enable_aggl_ceiling: bool = False
    enable_stratification_inequality_gate: bool = False
    stratification_gini_min: float = Field(0.40, ge=0.0, le=1.0)  # BHM 2009 Table 2 α-weighted Gini: forager 0.25,
    #   horticultural 0.27, agricultural/pastoral ~0.45–0.57 → the egalitarian↔stratified boundary sits ~0.35–0.40.
    #   PROVISIONAL: within-band Gini runs below whole-population Gini, so calibrate on the validated baseline.
    # PACKING MEASURE (R-61 fix): the morph "packed" test vs Binford 0.091/km². Default = a band's members / its
    # footprint area (a band's density over its own range ~0.017 = a NORMAL forager → never packs). Binford's 0.091 is
    # a LANDSCAPE population density, so `enable_landscape_packing` uses (all agents on the band's cells / area) — is the
    # LAND crowded, not is my band spread thin — so a genuinely dense village (rich/circumscribed terrain) can cross
    # packing and stratify. Default OFF ⇒ old measure (bit-exact).
    enable_landscape_packing: bool = False
    morph_npp_floor: float = Field(500.0, ge=0.0)  # AND a PRODUCTIVE setting: mean(npp_gm2) ≥ this — the true-desert(≈400) vs river-desert/Nile(≳550) distinguisher [PROVISIONAL, from R-47 occupied-cell data]
    # ── S.4 society morph (PER-CELL): a cell that stays packed (≥ Binford packing) with a defendable storable
    # surplus for ~1 generation morphs egalitarian_forager → complex_forager → stratified_chiefdom (the cell's κ
    # rises → unequal store/meat sharing); it DE-morphs back when the surplus/density collapse (hysteresis via the
    # settle timer). Drives `society_from_character` (which was never called). Needs enable_storage (the surplus
    # signal). Default OFF = bit-exact back-compat. (v1 morphs the κ/inequality lever per cell; the family-knob
    # localization — per-cell mate-choice etc. — is a follow-on, reproduction still reads the global config.)
    enable_morph: bool = False
    morph_settle_steps: int = Field(300, ge=1)                  # T: sustained-settlement steps to morph (~1 generation; Bocquet-Appel)
    # ── ECONOMIC DEFENSIBILITY / OWNED-PATCH (blueprint …_EconomicDefensibility; Dyson-Hudson & Smith 1978): the
    # BETWEEN-band driver of concentration. Movement is Ideal FREE Distribution → no band can monopolise a dense
    # storable resource → it dilutes to the landscape average → no private surplus → no tether (diagnosed GATE-3 /
    # R-51). A band that LEAD-occupies a DEFENSIBLE cell (dense × predictable resource: aquatic_food/S_pot ≥
    # defensibility_min) for defensibility_claim_dwell steps CLAIMS it; then OUTSIDERS perceive a reduced per-capita
    # there (× defensibility_exclusion — the shadow of defence, so IFD routes them away) while OWNER members get a
    # tether bonus (× defensibility_tether) pulling them onto their reach → per-capita stays high → concentration →
    # packing → the density morph fires. Soft / no-violence v1 (a perception change only). Resource-agnostic (a
    # proto-agriculture `cultivability` source drops into S_pot later). Needs distinct band_ids
    # (enable_band_affiliation) to be meaningful. Default OFF ⇒ owner map is None ⇒ movement/split bit-exact.
    enable_economic_defensibility: bool = False
    defensibility_min: float = Field(0.15, ge=0.0)              # D_min: min aquatic_food/S_pot for a cell to be CLAIMABLE (dense+predictable) [PROVISIONAL]
    defensibility_claim_dwell: int = Field(6, ge=1)             # steps a band must lead-occupy a claimable cell before it OWNS it (bootstrapping toehold)
    defensibility_claim_min: int = Field(3, ge=1)              # min owner members present to build/hold a claim (a family; below → the claim decays)
    defensibility_exclusion: float = Field(0.2, ge=0.0, le=1.0)  # OUTSIDER's perceived per-capita on an OWNED cell × this (shadow of defence → routed away) [PROVISIONAL]
    defensibility_tether: float = Field(6.0, ge=1.0)           # OWNER member's perceived per-capita on ITS band's owned cell × this (delayed-return tether → concentrate) [PROVISIONAL]
    # IMPROVED-LAND (agriculture): cultivable land becomes DEFENSIBLE/claimable where it is actively WORKED — inside an
    # active settlement's catchment — NOT merely fertile. "You own what you've cleared and planted" (Testart delayed-
    # return; Bandy landscape capital). Opens the AGRARIAN territoriality → stratification path (Fertile Crescent/Nile)
    # alongside the aquatic (NW-Coast) one, without letting the ~62% cultivable wilderness all be claimable at once.
    # Requires enable_economic_defensibility. Default OFF ⇒ aquatic-only claimable (bit-exact).
    enable_improved_land: bool = False
    # ── AGGREGATION-SEDENTISM (blueprint …_AggregationSedentism; Mauss/Binford/Johnson): settlements as MULTI-BAND
    # coalescence — "the gathering that stops dispersing". Q1 lit: villages form by COALESCENCE of several bands at a
    # rich node (not one band packing); Q2: the landscape is ~6× below Binford packing, so the density must come from
    # AGGREGATING bands. At a persistent-abundant site a seasonal pool (≥ settle_min_pool people) PERSISTS: members
    # within settle_radius are held (cohesion → site, at the POOL scale where it is stable) so the aggregation packs →
    # the density morph fires; scalar stress → hierarchy. Dissolves (hysteresis) when the pool can't be sustained.
    # LAYER 1 (this): lifecycle + hold, reside-on-cluster harvest. LAYER 2 (later): logistical CATCHMENT foraging
    # (residence ≠ foraging; Binford collectors) + catchment-grain defensibility. Needs enable_marriage_aggregation
    # (the gathering) + enable_band_affiliation. Default OFF ⇒ no settlements ⇒ bit-exact.
    enable_aggregation_sedentism: bool = False
    settle_min_pool: int = Field(40, ge=2)                     # min people to found/hold a settlement — minimum-viable-hamlet threshold (Bar-Yosef 1998: Natufian settlements range small ~dozens → medium 100–150; 40 = the small-settlement lower bound) [ANCHORED-lower-bound]
    settle_persist_threshold: float = Field(0.3, ge=0.0)      # site aquatic_food/S_pot ≥ this = a persistent-abundant (storable) settlement site [PROVISIONAL]
    settle_radius: int = Field(2, ge=1)                       # Chebyshev radius of the settlement cluster (membership + hold) — a day's logistical range (~1–2 cells)
    settlement_cohesion: float = Field(1.5, ge=0.0)          # (Layer 1 soft hold — SUPERSEDED by the Layer 2 residence pin below; kept for ablation)
    settle_release_steps: int = Field(12, ge=1)              # hysteresis: steps a settlement survives below settle_min_pool before it dissolves
    # LAYER 2 — residence ≠ foraging (Binford collectors). A settlement of ~dozens is « one 100 km² cell, so settled
    # members RESIDE on the single site cell (→ residential density ≫ Binford packing → the morph fires) and FORAGE a
    # CATCHMENT. The catchment yields an intensive TIER-2 resource UNLOCKED only by settlement (gated: a mobile band
    # gets only the small tier-1 return; the intensive fishery/proto-ag needs the settled labour + storage — Testart
    # delayed-return / Boserup intensification). RESOURCE-AGNOSTIC: reads S_pot (= aquatic_food now; a cultivability
    # source drops in later — one field, many sources). This sustains the packed pool that reside-on-cluster starved.
    settle_catchment_radius: int = Field(2, ge=0)            # cells the settlement forages tier-2 from (a day's logistical range) [PROVISIONAL]
    settle_tier2_yield: float = Field(40.0, ge=0.0)          # intensive tier-2 yield per unit S_pot per catchment cell, unlocked by settlement (gated) [PROVISIONAL — sweep]
    # CATCHMENT CARRYING-CAPACITY CEILING (R-63): a settled village's TOTAL food (base forage + resource tier-2 +
    # agglomeration social-returns) is capped at what its catchment land can sustainably yield — a village cannot
    # out-produce its territory, whether by intensifying OR by specializing. This is the resource ceiling R-54 recorded
    # (Bettencourt: "a subsistence village has a resource ceiling a modern city does not") but never applied — the fix
    # for the UNBOUNDED point-superlinear premium (R-63). Increasing returns then RISE → SATURATE at the ceiling →
    # scalar stress caps size; rich (aquatic/arable) catchments carry more → surplus → stratify. Default OFF ⇒ bit-exact.
    enable_catchment_ceiling: bool = False
    catchment_ceiling_mult: float = Field(1.0, gt=0.0)       # ceiling = this × Σ(sustainable cell yield over the catchment); 1.0 = the land's own capacity
    # SETTLEMENT SCALAR STRESS (Johnson 1982, dissipated by hierarchy) — the missing cost that caps VILLAGE size. The
    # residence pin otherwise pulls every nearby agent into a settlement unconditionally ⇒ villages grow to the food
    # ceiling with no cap (R-63). Here an over-crowded settlement REPELS agents (prob = size_repulsion(village_pop))
    # — but the repulsion is scaled by the settlement's SOCIETY factor (egalitarian 1.0 → complex 0.5 → stratified
    # 0.25): hierarchy absorbs scalar stress (Johnson's thesis), so an EGALITARIAN village fissions at ~midpoint while
    # a STRATIFIED one grows past it. Combined with the catchment ceiling this closes the loop: cap at ~150 → surplus
    # (ceiling > pop) → morph to stratified → scalar stress weakens → village grows toward the ceiling. Default OFF.
    enable_settlement_scalar_stress: bool = False
    settlement_ss_gain: float = Field(1.0, ge=0.0, le=1.0)   # max repel probability for an egalitarian over-crowded village
    settlement_ss_midpoint: float = Field(150.0, gt=0.0)     # village pop at half-max repulsion (Bar-Yosef egalitarian upper bound)
    settlement_ss_width: float = Field(50.0, gt=0.0)         # logistic width (Alberti 2014 shape)
    # LAYER 2b core — SHOCK (a bad-run / drought year). Fisheries don't deplete-collapse (salmon self-renews — NW
    # Coast stable millennia); the real dispersal driver is a correlated bad YEAR that STORAGE must buffer. Once per
    # aggregation_period a mean-preserving REGIONAL lognormal `s ~ LN(CV=shock_cv)` scales that year's tier-2 yield
    # (shared across settlements — a climate bad year can't be insured away). Full granaries ride it out; thin ones →
    # deficit → the existing starvation + settlement-dissolve → dispersal EMERGES. Anchor: salmon run inter-annual
    # CV ~0.5–1 (ENSO/ocean regimes). Soil-depletion + learning (landesque capital) deferred to the cultivability
    # tier. Default OFF ⇒ shock=1.0 ⇒ bit-exact.
    enable_tier2_shock: bool = False
    shock_cv: float = Field(0.6, ge=0.0)                     # inter-annual tier-2 yield CV (salmon-run anchored) [PROVISIONAL — sweep]
    shock_rho: float = Field(0.0, ge=0.0, lt=1.0)           # AR(1) persistence: 0 = IID single bad years; →1 = multi-year good/bad REGIMES (ENSO/PDO/drought). Storage matters most at high ρ (must carry a multi-year bad regime). [PROVISIONAL — sweep]
    # AGRICULTURE TIER Layer A (blueprint …_AgricultureTier): add `cultivability` (EFC-derived, resource-agnostic) as
    # a SECOND S_pot source → S_pot = max(aquatic_food, cultivability), so settlements form on FERTILE LAND and behave
    # like fishery villages (the generality payoff — farming villages via one field). Layer B (soil-depletion +
    # landesque + relocation → the dynastic bust) follows. Default OFF ⇒ S_pot = aquatic_food only ⇒ bit-exact.
    enable_agriculture: bool = False
    # AGRICULTURE TIER Layer B1 — SOIL DEPLETION (the bust driver fisheries lack). A FARM settlement (cultivability >
    # aquatic at its site) degrades a per-site SOIL stock ∈[SOIL_FLOOR,1] under farming pressure; tier-2 farm yield ×
    # soil. Regrowth is SLOW (swidden fallow ~10–20 yr) — depleted land only recovers on a long fallow (after the
    # village leaves). FISHERIES are exempt (aquatic-dominant sites never deplete → R-53 stable villages preserved).
    # This gives boom → soil-degrade → yield-fall → bust (relocation = Layer B3). Default OFF ⇒ soil≡1 ⇒ bit-exact.
    enable_soil_depletion: bool = False
    soil_regrow_per_yr: float = Field(0.045, ge=0.0)        # slow fallow soil recovery (~1/0.045 ≈ 22 yr) — Boserup FOREST-FALLOW: a parcel is cropped 1–2 yr then fallowed 20–25 yr (Conklin) [ANCHORED, forest-fallow band]
    soil_deplete_frac: float = Field(0.6, ge=0.0)           # per-YEAR soil exhaustion at pressure=1 (PROGRESSIVE while farmed — no equilibrium; swidden) [PROVISIONAL]
    soil_carry_per_cell: float = Field(8.0, ge=0.1)         # persons/catchment-cell that = pressure 1.0 (farming carrying density) [PROVISIONAL]
    # ALLUVIAL RENEWAL — soil renewal is TERRAIN-dependent, not uniform. The annual FLOOD re-deposits nutrient silt, so
    # FLOODPLAIN farmland is renewed WHILE FARMED (the Nile floodplain was cropped ~5,000 yr essentially without fallow —
    # the flood WAS the fertilizer), whereas RAIN-FED dryland exhausts → the swidden deplete→fallow→re-settle cycle.
    # Keyed on `wateracc`, the SAME alluvial signal cultivability_field already uses (CULT_WATER_BASE far-from-water =
    # rain-fed/no alluvium … CULT_WATER_GAIN at the water = alluvial floodplain/irrigable = prime; Nile/Mesopotamia/Indus).
    # ⇒ TWO agrarian regimes emerge: rain-fed SWIDDEN (deplete→abandon→re-settle = cycles) vs HYDRAULIC floodplain
    # (renewed → stable, dense, stratifying without cycling). Requires enable_soil_depletion. Default OFF ⇒ every farm
    # depletes (bit-exact).
    enable_alluvial_renewal: bool = False
    alluvial_renew_per_yr: float = Field(3.0, ge=0.0)       # flood soil-restoration rate at wateracc=1 — restores ~97% of the deficit within a year ⇒ equilibrium soil ≈ 1 − deplete/renew ≈ 0.8 at full farming pressure = sustainable WITHOUT fallow (the Nile) [PROVISIONAL]
    # EMERGENT ABANDONMENT — a settlement's HOLD on its people is not permanent; it erodes when the village's REMEMBERED
    # FORTUNES have been bad for a long time. There is NO "if soil < X then dissolve" rule and NO global knowledge: the
    # agents' ordinary IFD drive already wants to move somewhere better — it is merely OVERRIDDEN by the residence pin.
    # So we make the PIN condition-dependent on the site's own history (which is the only information the elders
    # actually have) and let the existing drive decide: released ⇒ the agent stays anyway if nowhere nearby is better,
    # or drifts out if it is → the pool falls below settle_min_pool → the settlement dissolves by the EXISTING rule →
    # the field fallows → budding re-settles fresh land. Abandonment thus EMERGES.
    #   memory: per-SITE EMA of hardship (1 − realized field productivity) — attached to the PLACE (members churn, the
    #   place persists). A slow EMA ⇒ one bad year does not move it (natural hysteresis); only CHRONIC decline does.
    #   Fisheries/alluvial sites keep soil ≈1 ⇒ hardship ≈0 ⇒ they never abandon (the permanent hydraulic village).
    # ANCHOR: swidden villages relocate every ~5–30 yr (Conklin's "integral pioneers… move on to new village sites
    # often"; Yanomamö ~5–10 yr) = WITHIN one generation, not several. Requires enable_soil_depletion.
    # Default OFF ⇒ the pin never releases (bit-exact).
    enable_emergent_abandonment: bool = False
    settlement_memory_yr: float = Field(12.0, gt=0.0)       # the village's memory window for its remembered fortunes — sets the relocation interval into the ethnographic ~5–30 yr band [ANCHORED-range]
    abandon_hardship_gain: float = Field(1.0, ge=0.0)       # how strongly chronic remembered hardship erodes the residence pin (1 ⇒ attachment = 1 − hardship_ema)
    # ── AGGLOMERATION ECONOMICS (the "grand unification" rework; blueprint …_AgglomerationEconomics). ONE idea:
    # INCREASING RETURNS TO CO-LOCATION. Each cell's intensive catchment resource R(c) = aggl_tier2·Σ_catchment(S_pot·
    # soil); a co-located group of n gets total output R·L(n) with L(n)=n^α/(n^α+half^α) (convex→saturating), so
    # per-capita R·L(n)/n is SINGLE-PEAKED in n. Under IFD, agents then aggregate to the peak → villages/packing/optimal-
    # size/relocation/bust all EMERGE, replacing the discrete settlement lifecycle. Applied CONSISTENTLY to movement
    # (perceived) AND harvest (realized) so no over-subscription death. α anchored to Bettencourt ~1.15 (MODEL_SPEC
    # §4.8.21) — SWEPT (band-scale at 1.15, village-scale needs sharper). Default OFF ⇒ legacy S/(n+1) ⇒ bit-exact.
    # aggl_mode selects the returns-to-co-location FORM:
    #  "point"     — Bettencourt-CORRECT (Branch A): the cell's OWN intensive output scales super-linearly with its
    #                occupancy, O(n) = A_cell·n^β, so PER-CAPITA = A_cell·n^(β-1) RISES with n (β>1) → co-location is
    #                genuinely more productive per head → packing NUCLEATES and reinforces GRP. A_cell = tier2·S_pot·cv_ref
    #                (single cell — a POINT return, not an areal sum). This is the intended agglomeration economy.
    #  "catchment" — FALSIFIED (kept for comparison): shared catchment pot R·L(n)/n with L saturating → per-capita PEAKS
    #                then CONGESTS (∝1/n at scale) → areal-dispersive, monotonically REDUCES packing as tier2 rises. The
    #                exponent there (aggl_alpha) is a logistic saturation-sharpness, NOT Bettencourt's scaling β. See
    #                DEAD_ENDS + MODEL_SPEC §4.8.21.
    enable_agglomeration: bool = False
    aggl_mode: str = "point"                                 # "point" (Bettencourt-correct) | "catchment" (falsified)
    aggl_beta: float = Field(1.15, ge=1.0)                   # POINT super-linear exponent: per-capita ∝ n^(β-1) (Bettencourt β≈1.15) [VERIFIED-anchored]
    aggl_alpha: float = Field(1.15, ge=1.0)                  # CATCHMENT logistic sharpness L(n)~n^α (falsified mode only) [PROVISIONAL]
    aggl_half: float = Field(100.0, gt=0.0)                  # CATCHMENT half-saturation n of L(n) (falsified mode only) [PROVISIONAL]
    aggl_tier2: float = Field(2.0, ge=0.0)                   # intensification MULTIPLE: A_cell/R = tier2·S_pot·cv_ref — dimensionless (~1–5) [PROVISIONAL]
    aggl_catchment_radius: int = Field(1, ge=0)             # CATCHMENT pooling radius (falsified mode; Vita-Finzi 5–10 km ≈ radius 1) [VERIFIED-anchored]
    # PER-PERSON FORAGE CAP (the solitude fix): a forager can only WORK so much land — intake is capped at the biome
    # return-rate × work hours (forage_kcal[cell] · forage_cap_hours), NOT the whole cell (S/n gave a lone agent ~27×
    # subsistence → solitude over-rewarded → aggregation never paid; GATE-3). Grounds the economy in the Survey-A
    # return-rate data (MODEL_SPEC §4.1; forage_kcal already a field, biome-dependent + right-skewed distribution).
    # Flattens the forage per-capita (≈cap up to carrying) so grouping/agglomeration decide clustering. Applied in
    # movement (perceived) AND harvest (realized). Default OFF ⇒ legacy S/n ⇒ bit-exact. (v2: × age-skill curve +
    # cred-transmitted embodied capital — Walker 2002 / Gurven 2006 / Koster 2020, pending fetch.)
    enable_forage_cap: bool = False
    forage_cap_hours: float = Field(100.0, ge=0.0)          # foraging work-hours/period; cap = forage_kcal·hours (~1.6× BURN at hours=100) [PROVISIONAL — Hadza time-budget]
    # (storage_tether_reserves RETIRED 2026-06-29 — the band-aid that froze stocked bands in place to force packing;
    # superseded by the emergent-bands grouping drives + bonded mating, which reach packing and fire the morph on
    # their own. See MODEL_SPEC §4.8.5 and outputs/.../run_3h_tether_retirement.py.)
    # F.1 bonded mating (emergent bands via SELECTION): a female reproduces only if her cell has a co-resident
    # adult male who is NOT her own son (kin-avoidance) — a LONER cannot reproduce, so loner lineages die out and
    # the population concentrates in bands by selection (not navigation). Default OFF = asexual/female-only (R-18/19).
    enable_bonded_mating: bool = False
    # F.2 mate-search RADIUS (Chebyshev). The band is a spatially-EXTENDED group: on the IFD substrate agents sit
    # ~1 per 100 km² cell (Binford packing) and spread over a territory, so a mate co-resident in the BAND is
    # rarely on the mother's EXACT cell. radius=0 = the original per-cell gate (a loner with no neighbours can't
    # reproduce); radius≥1 = an unrelated adult male anywhere within the band territory (Chebyshev r) qualifies.
    bonded_mate_radius: int = Field(0, ge=0)
    # `enable_band_risk` / `band_risk_penalty` / `band_risk_size` WERE HERE AND ARE DELETED (2026-08-06).
    # F.2 band risk-dilution: a sub-band group loses the safety-in-numbers mitigation on the exogenous biome
    # hazard → elevated a2 mortality, scaled by the cell's own incident rate (Hamilton 1971 selfish-herd). With
    # density-disease rising in crowding, this was hypothesised to produce an emergent OPTIMAL band size.
    # ⚠ THE FINDING, WHICH IS THE POINT AND IS KEPT: **it does not, and it cannot.** Mortality does not cause
    # aggregation — that is the E.1 movement safety-drive's job. A loner-mortality penalty just CULLS: fewer
    # people → lower density → smaller bands → more loners → more penalty. A DEATH SPIRAL, not a stabilising
    # optimum (F.2 prototype run_3i, 2026-06-29; penalty 0→6 took pop 281→64 and mean band 56→5).
    # WHY DELETED RATHER THAN LEFT OFF: the gain defaulted to 0.0 and the code was guarded by `> 0.0`, so the
    # flag could read ON in a config dump while the mechanism was INERT — it survived a whole ablation battery
    # as a fake positive. The only two states available were "does nothing" and "kills the population", and a
    # knob with no useful setting is not a knob. Risk-dilution belongs in MOVEMENT (E.1); banding already has
    # fitness teeth via the F.1 mate-gate.
    # RECOVERY: the mechanism, and the `run_3i_band_risk_proto.py` sweep that killed it, are both at commit
    # daa7194 ("F.2: risk-dilution mortality SHELVED (negative result) + band life-cycle diagnostics"). The
    # prototype was deleted with the fields — it could not have run again, and a script that cannot run is the
    # same kind of lie as a flag that does nothing.
    # F.3a/b PERSISTENT FAMILIES (the deferred "C"; core of FD-1). `enable_pair_bonds`: a female forms a DURABLE
    # monogamous bond with a band male (prowess-weighted by mate_choice_strength), persisting across births (vs the
    # per-conception lottery); births default to the living co-resident partner; the bond dissolves on partner
    # death (→ widow re-pairs = serial monogamy) or at `divorce_rate`/step. The NUCLEAR FAMILY — mother + bonded
    # father + dependent children (age < `family_maturity_months`) — MOVES AS A UNIT (co-locates to the mother each
    # step); children DETACH at maturity → exogamous dispersal. Builds stable family-cored bands (Hill et al. 2011;
    # Marlowe monogamy). Uses bonded_mate_radius as the band extent. Default OFF = bit-exact back-compat.
    enable_pair_bonds: bool = False
    # PERF (re-arch Tier 0): pool mates by SOCIAL band_id (fission-capped ~25–45) instead of the SPATIAL bands()
    # clump. Fixes the O(clump²) mating blow-up under agglomeration (thousands co-located → one giant pool) → O(n),
    # and is more realistic (mate choice is band-local, von Rueden scale). Default OFF ⇒ spatial pool, bit-exact.
    # NB: changes the mating SKEW → re-validate status→RS (R-19/R-55). Requires enable_band_affiliation.
    mate_within_band_id: bool = False
    # PER-STEP bond dissolution probability, applied in `_do_divorce` every step on all pairing paths (R-78 —
    # it previously sat inside the seasonal gate on the gathering/connubium paths ⇒ ~12× rarer than "per-step"
    # there; R-75). 0 = lifelong unless widowed. Anchor: Hill & Hurtado Tab. 13.1 gives ~0.14 of child (0-9)
    # risk-intervals as PARENTS-DIVORCED PREVALENCE (both parents living) — a stock, so `divorce_rate` (a flow)
    # is CALIBRATED to reproduce that `frac_parents_divorced` via `report_demography.py`, not read off directly.
    # Feeds the R-74 orphan channel's ×2.97 divorced-child multiplier.
    divorce_rate: float = Field(0.0, ge=0.0, le=1.0)
    family_maturity_months: int = Field(180, ge=0)        # child detaches from the family unit at this age (~15 yr)
    # F.3a MODEST POLYGYNY (von Rueden & Jaeggi 2016: polygyny is the MAIN status→RS amplifier; ~4-11% of forager
    # marriages). polygyny_rate>0: when a female pairs she may also consider ALREADY-MARRIED males (each with prob
    # polygyny_rate), prowess-weighted (mate_choice_strength) — so high-status males accumulate up to `max_wives`
    # wives and some low-status males are bachelors → the status→RS skew (lost under strict monogamy) returns.
    # A female has ONE husband (`_partner`); a male's wives = `_wives`. Polygynous (>1 wife) husbands move as
    # roots (wives are mother-anchored cores in his band; the birth gate is band-level). 0 = strict monogamy.
    polygyny_rate: float = Field(0.0, ge=0.0, le=1.0)
    max_wives: int = Field(1, ge=1)                       # cap on wives per male (1 = monogamy even if rate>0)
    # POLYGYNY ATTRITION (R-76) — the stock's missing OUTFLOW. `polygyny_rate` gates only whether a married
    # male is CONSIDERED; once considered he wins prowess-weighted, and a polygynous bond never ends. So
    # polygyny is a stock that only fills, and the rate cannot set the level: measured, a **150× rate change
    # (0.002→0.3) moves realized polygyny just 9.2%→25.3%**, and Marlowe's ~4% is unreachable (0% at rate=0,
    # then straight to 9.2% at 0.002). With an outflow, inflow-vs-attrition reaches an equilibrium the rate
    # actually controls.
    # ANCHOR — Marlowe, *The Hadza* (monograph): "When a man does have 2 wives, the women usually live in
    # different camps, and **polygynous marriages are less enduring**." Level target from the same page:
    # "there are usually only about **4% of men with 2 wives**" (note the denominator: of MEN, not of married
    # men). Per-step dissolution probability for a wife whose husband holds >1 wife; fires EVERY step (unlike
    # `divorce_rate`, which is trapped inside the seasonal gate on the gathering path — R-75, task_9804e99a).
    # 0 = no attrition ⇒ bit-exact pre-R-76 behaviour.
    polygyny_attrition: float = Field(0.0, ge=0.0, le=1.0)
    # WIFE QUALITY (R-77) — the missing status→RS channel for a MONOGAMY-DOMINANT system.
    # von Rueden & Jaeggi, "Men's status and reproductive success in 33 nonindustrial societies" (PNAS;
    # phylogenetic multilevel meta-analysis, 288 associations / 46 studies / 33 societies): overall status→RS
    # **r = 0.19**, but decomposed by marriage system — status associates with **wife quality ONLY in
    # MONOGAMOUS societies (r = 0.15)** and with offspring mortality only in polygynous ones (r = −0.08).
    # Their operational definition: wife quality = "**wife's age or interbirth interval**, wife's productivity".
    # WHY IT MATTERS HERE (R-76): the model's ONLY status→RS channel was wives-COUNT, so it had to run 6× the
    # ethnographic polygyny rate (25% of men vs Marlowe's 4%) to reach von Rueden's r. At a Marlowe-calibrated
    # ~4% polygyny, status→RS collapsed to ≈+0.02. A monogamy-dominant forager system is supposed to route
    # status→RS through wife QUALITY, not wife count — and the model had no such route.
    # MECHANISM: females pair in order of remaining fertility^strength (weighted sampling without
    # replacement), so the most fertile pair FIRST and — choosing prowess-weighted — take the highest-status
    # men. The status↔wife-youth assortment EMERGES from mutual choice rather than being imposed as a
    # correlation. 0 = random pairing order (bit-exact).
    wife_quality_strength: float = Field(0.0, ge=0.0)
    # ⚠ UNIT WARNING on the "~25, Hill 2011" below (Addendum 28; propagated here 2026-08-06, Addendum 29).
    # Hill et al. 2011's verified number is **28.2 ADULTS** per band (32 societies). The all-ages ~25 (and the
    # [18–35] band this project scored for years) is a MIS-ATTRIBUTION of it. That matters because the model
    # carries too many children: on the adults unit `band_med` reads 11.8 against 28.2 and FAILS 16/16, while
    # the all-ages reading "passes" 23/25 on the strength of the surplus children. Birdsell's ~25 stands on its
    # own; Hill's does not support an all-ages 25. Treat the split/merge sizes below as tuned to Birdsell, not
    # to Hill, until `band_med` is re-scored on adults.
    # F.3c-1 BAND AFFILIATION (the collective-identity vector's band_id cell). A persistent band membership that
    # families AFFILIATE into → multi-family bands (~25, Hill 2011 / Birdsell), the stable handle per-band society
    # attaches to. Newborns inherit the mother's band; at marriage the incoming spouse JOINS the larger/richer band
    # (FLEXIBLE/multilocal — keeps bands non-kin). A band-cohesion movement drive pulls family-roots toward their
    # band's centroid (food stays dominant); emergent fission (> band_split_size) / fusion (< band_merge_size) with
    # hysteresis bound band size ~25. Requires enable_pair_bonds. Default OFF = bit-exact back-compat.
    enable_band_affiliation: bool = False
    band_cohesion: float = Field(0.0, ge=0.0)             # cohesion-drive strength (pull toward band centroid); 0 = off
    band_split_size: int = Field(45, ge=2)               # band fissions above this (upper "community" rung / HARD cap)
    band_merge_size: int = Field(10, ge=1)               # band fuses into the nearest band below this (hysteresis vs split)
    # EMERGENT BAND SIZE v3 (blueprint …_EmergentBandSize; R-72). Band size = the argmax of
    # {risk-pooling − competition}, per the blueprint's original spec. Two coupled changes vs v1/v2:
    #
    # (1) LINEAR law, no clamps: g* = CV/cv_safe, where CV is the local DAY-TO-DAY return CV
    #     (terrain.RETURN_CV — a temporal field, NOT the spatial FORAGE/GAME_KCAL_STD; see terrain.py).
    #     v1/v2 used g*=(CV/cv_safe)², which is a *stopping rule with no cost side* ("pool until residual
    #     CV hits a threshold") — unbounded in CV, hence the clamps, hence saturation at 15/45 with nothing
    #     in between. The linear form falls out of benefit-vs-cost: pooled variance falls as σ²/n while
    #     crowding cost rises with n, so the optimum is n* ∝ CV. It needs no clamps, and a 2× CV spread
    #     gives a 2× band spread — which is what the ethnography shows (Marlowe/Kelly 25–50).
    # (2) The CV drives the COST side. v1/v2 only lowered the fission *ceiling*, i.e. a permission to be
    #     big — measured corr(g*, band size) = −0.22, no gradient, because a ceiling cannot pull a band
    #     together. `repulsion_midpoint` (Johnson scalar stress) is the term that actually sets band size,
    #     and it was still hardcoded at 25 — which is why R-64's "band ≈ 24" came out at 24. It is now
    #     per-band = g*(CV), so a high-variance band tolerates crowding longer before scalar stress bites.
    #
    # This deletes band_size_min, cv_min, and the two hardcoded 25s from the ON path (band_base_tolerable
    # and repulsion_midpoint survive only as the default-OFF values ⇒ bit-exact back-compat).
    enable_emergent_band_size: bool = False
    # cv_safe: the ONE fitted scale. Composite of risk-aversion and per-capita crowding cost, neither
    # independently anchored, so it is calibrated — but ONLY to place the MEAN band at Hill 2011's ~25–30
    # (mean RETURN_CV 1.017 / 27.5 = 0.037), never the spread. Predicted g*: wetland 19, mountain 23,
    # savanna 25, desert 28, forest 33, grass 38 (mean 27.5, spread 2.0× = Marlowe's 25–50). [CALIBRATED]
    # ⚠ CALIBRATED TO AN ALL-AGES TARGET THAT IS A MIS-READING (Addendum 28; noted here 2026-08-06). Hill 2011
    # gives **28.2 ADULTS**, not an all-ages 25–30, so the 27.5 this was fitted to is not the paper's quantity.
    # The R-106 re-fit against the corrected target was attempted and FALSIFIED (the mechanism cannot reach it
    # from this direction), so the fit is left standing and the target is left labelled — an honest mismatch
    # beats a second fit to a number that is still the wrong unit. See the band-affiliation note above.
    cv_safe: float = Field(0.037, gt=0.0)
    # F.3c-3 DYNAMIC fission/fusion + the ASSABIYAH seam (Ibn Khaldun group solidarity). Instead of a hard split at
    # band_split_size, a band fissions only above its CONDITION-DEPENDENT `tolerable_size` = base + (hard_cap −
    # base)·assabiyah — so a rich, high-solidarity band STAYS TOGETHER larger; a poor one fissions at the base.
    # `assabiyah` (the GroupVector seam, now active) builds from the band's SURPLUS (success → solidarity, +gain·
    # surplus) and decays (−decay) — a per-band cohesion state, mirrored onto members' GroupVector. band_split_size
    # stays the absolute runaway cap; band_merge_size the viability floor. Requires enable_band_affiliation.
    enable_dynamic_bands: bool = False
    band_base_tolerable: int = Field(25, ge=2)           # tolerable size at assabiyah=0 (Birdsell/Wobst ~25 baseline)
    assabiyah_gain: float = Field(0.05, ge=0.0)          # solidarity gained per step per unit band surplus
    assabiyah_decay: float = Field(0.02, ge=0.0)         # baseline solidarity decay per step (luxury/turnover erosion)
    # ── THE COHESION BUDGET HAS NO HEADROOM (R-106 Addendum 22) — two flagged candidates ──────────────
    # MEASURED: `cohesion_frac = clamp01(assabiyah + leader − repulsion − malnutrition)` is pinned at 1.0 for
    # every band that has a leader, so `split_thr` collapses to the constant `band_split_size` and g* (hence
    # `cv_safe`) drops out. corr(g*, band size) = −0.077; a cv_safe sweep over +22/+41/+62% moved `band_med`
    # by −1.9/−3.5/−8.4%, an elasticity of −0.14 against the law's −1.0. Four mechanisms feed that one
    # saturated expression — emergent band size, dynamic bands, size repulsion, malnutrition fission — and
    # are structurally inert at ANY magnitude.
    #
    # (1) LEAKY ASSABIYAH. The update above is `a += gain·s − decay`: a pure integrator with a CONSTANT leak,
    #     so it has no interior fixed point at all. If `gain·s > decay` it climbs to the clamp and stays;
    #     otherwise it falls to 0. It is bang-bang BY CONSTRUCTION, and no choice of gain/decay makes it
    #     graded — only the share of bands at each end changes. Measured: 95.7% of bands sit above the
    #     switchover `s = decay/gain = 0.40` (band surplus runs 0.35–0.99, median 0.69), and assabiyah's
    #     median is exactly 1.000 from step 100 onward.
    #     Making the leak proportional to the level — `a += gain·s·(1−a) − decay·a` — gives the interior
    #     fixed point `a* = gain·s / (gain·s + decay)`, which TRACKS surplus: 0.47 at s=0.35, 0.63 at the
    #     median 0.69, 0.71 at s=0.99. That is what F.3c-3's premise needs ("a rich, high-solidarity band
    #     STAYS TOGETHER larger; a poor one fissions at the base") — the band has to be able to be poor.
    enable_leaky_assabiyah: bool = False
    # (2) LEADER WEIGHT. Even an ungraded assabiyah leaves the leader term (0.41–1.64, median 0.78) ADDED on
    #     top, which re-saturates the sum on its own. This scales the leader's contribution INTO the budget
    #     without touching `leader_gain`, which the diagnostics report separately. 1.0 = today, bit-exact.
    cohesion_leader_weight: float = Field(1.0, ge=0.0)
    # (RETIRED 2026-07-01, DE-7: `season_aggregation` coupled tolerable_size to seasonal abundance → lean-season
    # fission. Mis-signed (moderate lean should not fission) + inert (dormant threshold, R-31). Superseded by M2
    # malnutrition fission. Field removed; configs that set it will now error — intended, it is retired.)
    # Social-Evolution Stage 1: LEADER COHERENCE (a SECOND, distinct cohesion source added to `tolerable_size`,
    # additive alongside assabiyah, not a relabel). A band's top-status member (highest cred·prowess) lends extra
    # cohesion, scaled by a Boehm 1999 reverse-dominance GATE on the band's society type (egalitarian bands LEVEL
    # would-be leaders → weight≈0; complex/stratified bands institutionalize authority → weight rises). Read FRESH
    # every step from current membership (no accumulated state, unlike assabiyah) so the benchmark signature —
    # leader death/removal → an IMMEDIATE cohesion drop → a fission spike next check — is not smoothed by a decay
    # lag. Requires enable_dynamic_bands (the term feeds the same tolerable_size headroom). Default OFF = bit-exact
    # (leader_term≡0 regardless of gain when the flag is off).
    enable_leader_coherence: bool = False
    leader_coherence_gain: float = Field(0.0, ge=0.0)    # UNANCHORED magnitude (red-team: bracket/sweep, don't fit)
    # Social-Evolution Stage 1b: SIZE-DRIVEN REPULSION (Johnson 1982 scalar stress) — a DISPERSIVE counterweight
    # to cohesion, rising with band size N via a logistic (Alberti 2014 shape), SUBTRACTED from the cohesion_frac
    # so a large band needs MORE cohesion (assabiyah+leader) to stay whole. DISTINCT from the existing resource-
    # scarcity fission (that runs through assabiyah↓ when surplus is low; this is resource-INDEPENDENT, purely
    # coordination cost). Boehm/Johnson coupling: scalar stress is what organizational HIERARCHY exists to absorb,
    # so the repulsion is scaled by REPULSION_SOCIETY_FACTOR — FULL in egalitarian mobile bands (no hierarchy →
    # capped ~small), RELIEVED in complex/stratified (settling + institutions let a group grow toward the hard
    # cap). The midpoint is the band-scale scalar-stress onset (≈ the Wobst-minimal band); the width is Alberti's
    # logistic shape re-anchored to band scale (village-scale N≈127 → band scale — a bracket, not a fit, cf. the
    # regime °C→CC% re-anchoring). Requires enable_dynamic_bands. Default OFF ⇒ repulsion≡0, bit-exact.
    # Johnson 1982 scalar stress as a dispersive term. **The anchor is Alberti 2014** (PLoS ONE 9(3):e91510),
    # who fits P(critical scalar stress | community size n) by logistic regression on archaeological +
    # ethnographic cases: `logit = b0 + b1·n` with **b0 = −18.636** (SE 3.127) and **b1 = 0.147** (SE 0.025),
    # both p<0.001; 98% correctly classified, Somers' D 0.99. Equivalently midpoint = −b0/b1 = **126.9**
    # (95% CI 121.9–131.9) and width = 1/b1 = **6.80**. Cross-check: p=0.99 at n=158.2 ⇒ logit 4.62 ✓.
    #
    # ⇒ ANCHORED VALUES: `repulsion_gain = 1.0` (Alberti's logistic IS a probability ∈ [0,1] — any gain<1
    # arbitrarily attenuates it) and `repulsion_width = 6.80`.
    # **CAVEAT (R-72):** Alberti's 126.9 is a COMMUNITY — i.e. the VILLAGE rung (Bar-Yosef 50–150, which
    # `enable_settlement_scalar_stress` uses; R-63/R-64) — NOT the ~25 band. Applying his slope at band scale
    # extrapolates below his data.
    # **The validated village stack (`emergent_village_demog`, R-54…R-64) runs gain=0.3 + width=6.0** — i.e.
    # a 0.3 attenuation and a rounded width. Left as-is: those results are validated at those values, and
    # testing gain=1.0 did NOT rescue the band gradient (+0.335 → +0.374 paired, still n.s.), so re-running
    # the village stack would buy documentation tidiness at the cost of re-validating R-54…R-64.
    enable_size_repulsion: bool = False
    repulsion_gain: float = Field(0.0, ge=0.0)           # max repulsion (subtracted from cohesion_frac). ANCHORED value = 1.0 (Alberti P); village stack uses 0.3
    repulsion_midpoint: float = Field(25.0, gt=0.0)      # band size at half-max repulsion (≈ Wobst-minimal band). Alberti's own midpoint is 126.9 = the VILLAGE rung; under enable_emergent_band_size this is replaced per-band by g*(CV)
    repulsion_width: float = Field(6.0, gt=0.0)          # logistic steepness in band-size units. ANCHORED value = 6.80 (= 1/b1, Alberti 2014); village stack validated at 6.0
    # Resource-response redesign (blueprint …_ResourceResponse_Scoping):
    # M2 — MALNUTRITION FISSION: a band losing members to REALIZED starvation adds a DISPERSIVE term that lowers
    # tolerable_size toward band_base_tolerable → a large band breaks up (fission), the child band diffuses apart
    # → lower local density → higher per-capita yield → the subsequent starvation mortality relaxes (dispersal
    # SUBSTITUTES for further death). REACTIVE, not a forecast (supervisor: real bands disperse when starvation
    # actually bites, not on anticipation — anticipatory dispersal would be a future "wise leadership" feature).
    # Signal = an EMA of the band's per-capita starvation-death rate (`_band_starv_ema`); NOT `_condition` (which
    # samples the post-harvest FED reserve → pinned ~1.0 under scarcity, survivor-biased — see RESULTS R-32).
    # Intrinsically size-gated: tolerable floors at band_base_tolerable, so only bands LARGER than it can fission
    # (small bands just shrink/die). Default OFF.
    enable_malnutrition_fission: bool = False
    malnutrition_fission_gain: float = Field(0.0, ge=0.0)      # max dispersion (subtracted from cohesion); UNANCHORED
    malnutrition_starv_rate: float = Field(0.05, gt=0.0)       # per-capita recent-starvation rate (EMA) at which the pressure SATURATES
    malnutrition_ema_alpha: float = Field(0.3, gt=0.0, le=1.0)  # smoothing of the per-band starvation-rate signal
    # F — RESOURCE-DIRECTED FUSION: a band below band_merge_size joins the RICHEST nearby neighbour (highest
    # `_band_surplus`) instead of the NEAREST — starving remnants merge into well-provisioned bands (Wiessner hxaro).
    # Bounded to `fusion_search_radius` cells (stay local; fall back to nearest if none in range). Default OFF ⇒
    # nearest-neighbour join, bit-exact.
    enable_resource_directed_fusion: bool = False
    fusion_search_radius: float = Field(25.0, gt=0.0)          # cells; locality bound for the richest-neighbour search
    # Stage 1 (village-nucleation arc) — SUPRA-BAND SCALING: band_split_size is normally a HARD cap (cohesion_frac
    # clamped to [0,1] ⇒ tolerable ≤ band_split_size). Johnson 1982: a group exceeds scalar-stress-limited band scale
    # ONLY when payoff + HIERARCHY overcome scalar stress. When enabled, net payoff ABOVE saturation (the UNCLAMPED
    # assabiyah + leader − repulsion − malnutrition, minus 1) adds village HEADROOM beyond the hard cap:
    #   tolerable = base + (cap−base)·min(1,net) + village_gain·(cap−base)·max(0, net−1).
    # Since assabiyah alone caps at 1 (= the hard cap exactly), exceeding band scale REQUIRES the leader/hierarchy term
    # (enable_leader_coherence) — villages need leadership (Johnson/Testart). Default OFF ⇒ hard cap, bit-exact.
    enable_village_scaling: bool = False
    village_gain: float = Field(0.0, ge=0.0)                   # headroom multiplier on net-payoff-above-saturation; UNANCHORED (sweep)
    # VILLAGE BUDDING (Bandy 2004; Chagnon 1975) — the ethnographic settlement-SPREAD/recovery mode. A village (band_id)
    # grown past a scalar-stress FISSION THRESHOLD sheds its RIVAL-LEADER (2nd-largest lineage) faction, which RELOCATES
    # to a nearby available STORABLE site and founds a DAUGHTER village. So the settlement system propagates by BUDDING
    # (not by aggregating scattered individuals — the mode aggregation-only lacked, R-68) and re-spreads after a crash.
    # Fission CEASES once a village STRATIFIES (integrative institutions suppress it — Bandy → the Carneiro fork). If no
    # open site is in reach (CIRCUMSCRIPTION → high relocation cost), budding fails and the village stays large (existing
    # morph → hierarchy handles it). Requires enable_band_affiliation. Default OFF ⇒ no-op (bit-exact).
    enable_village_budding: bool = False
    village_fission_threshold: int = Field(170, ge=10)        # BASE (open-landscape) fission threshold — Bandy 2004 Early Chiripa ~170 (villages fissioned at pop-index 157–186); =Alberti N≈127–158 / Yanomamö ~200 range [ANCHORED, Bandy 2004 p.330]
    village_bud_min_faction: float = Field(0.0, ge=0.0, le=1.0)   # minimum rival-bloc share to carry a fission.
    #   WAS 0.25, which silently disabled budding: measured, a 475-person village held 126 lineages with the
    #   largest at 8.2%, so no bloc could ever reach a quarter. That 0.25 was the ONE budding parameter with no
    #   [ANCHORED] tag, and it is absent from the load-bearing source — Bandy 2004 (filed) models fission as
    #   scaling with village SIZE and relocation COST and never mentions faction size; "lineage" appears in it
    #   once, in a bibliography entry. The lineage-cleavage premise came from Chagnon, which LITERATURE.md
    #   records as NOT OBTAINED / corroborating only. Default 0 ⇒ the kinship cleavage below decides the split;
    #   raise it to re-impose a minimum-bloc rule. [DESIGN — deliberately unanchored, was blocking an anchored
    #   mechanism]
    village_bud_search_radius: int = Field(8, ge=1)           # cells searched for an open daughter site; beyond it ⇒ CIRCUMSCRIBED (no bud → the village grows + stratifies). ~a day's relocation range
    # ── EMERGENT FISSION HAZARD (2026-07-27) ────────────────────────────────────────────────────────
    # Fission is no longer a size THRESHOLD but a per-village-per-step HAZARD. Bandy 2004 is explicit that the
    # threshold is not a constant — "if the cost of fissioning is low ... fissioning may be expected to occur
    # frequently and at a VERY LOW population threshold" — and that the outcome is a RACE: Johnson's growth →
    # conflict resolves "in only one of two ways: (1) the village fissions or (2) institutions ... emerge ...
    # in such a way that fissioning is not necessary", the latter opening the way to "greater social group
    # sizes, and spiraling social inequality". A village whose economy works therefore does NOT split, and
    # large stable centres become an OUTCOME rather than something suppressed by hand.
    enable_bud_hazard: bool = False        # OFF ⇒ the old size-threshold path, bit-exact
    # SIZE TERM — Alberti 2014 (PLoS ONE 9(3):e91510) fitted logistic for P(critical scalar stress | size).
    # Read from the filed PDF: slope 0.147 (95% CI 0.098–0.196), intercept −18.636 (95% CI −24.76…−12.51),
    # which reproduce his stated inflection at size 127 (−b0/b1 = 126.8) and max stress ~158. [ANCHORED]
    bud_hazard_b0: float = Field(-18.636)
    bud_hazard_b1: float = Field(0.147, ge=0.0)
    # BASE RATE — Bandy 2004's own event counts. Three fission events, and in ALL THREE the village was the
    # largest of its phase: Chiaramaya + Cerro Choncaya (top two of Early Chiripa, a 500-yr phase) and Sonaji
    # (largest of Middle Chiripa, 200 yr) ⇒ ~2–5 × 10⁻³ per large-village-year. This is the CEILING hazard, for
    # a maximally-stressed village with every modifier at maximum and an open site next door. [ANCHORED —
    # bracket, not a point; the realised rate is an output to compare back against 2–5e-3.]
    bud_hazard_per_yr: float = Field(0.005, ge=0.0)
    bud_steps_per_year: float = Field(12.0, gt=0.0)           # model calendar (2000 steps ≈ 167 yr)
    # MODIFIER WEIGHTS — Bandy names the DIRECTIONS ("factors favouring fissioning include resource depletion
    # and a high level of internal conflict"; "factors discouraging ... high levels of investment in landscape
    # (nonportable) capital, and social circumscription") but gives no coefficients. Each weight w mixes its
    # factor in as (1−w) + w·factor, so w=0 ablates that factor and w=1 applies it fully. [DESIGN — deliberately
    # not dressed up as anchored. Their COMBINED effect has a validation target instead: Bandy's regional
    # signature of early frequent fissioning followed by cessation as integration appears.]
    bud_w_depletion: float = Field(1.0, ge=0.0, le=1.0)       # granaries empty ⇒ fission (favours)
    bud_w_capital: float = Field(1.0, ge=0.0, le=1.0)         # owned/improved land ⇒ stay (discourages)
    bud_w_integration: float = Field(1.0, ge=0.0, le=1.0)     # complex/stratified ⇒ stay (Bandy's branch 2)
    # ── POLARIZATION (2026-07-27) ───────────────────────────────────────────────────────────────
    # Bandy's factors FAVOURING fission are "resource depletion AND A HIGH LEVEL OF INTERNAL CONFLICT". Only
    # depletion was wired; conflict was left out although the model already carries the grievance state. These
    # add the conflict side, from the sources that name each driver:
    #   MATE COMPETITION  Alvard 2009 on the Yanomamö: villages "splinter for reasons often related to mate
    #                     competition", and the axe fight itself began in a dispute over a woman.
    #   LEADERSHIP RIVALRY Chagnon: a large village "develops SEVERAL competing headmen and cleaves between
    #                     them". Measured as how close the rival is to the incumbent — one dominant man is a
    #                     settled village, two near-equals is one about to split. Uses the SAME pair the
    #                     cleavage already identifies, so it costs nothing extra.
    #   GRIEVANCE         the existing per-band resentment stock (privilege measured as an effect size, so it
    #                     is a wealth/status GAP rather than a level — the supervisor's point).
    # COMBINATION RULE — these are ALTERNATIVE SUFFICIENT CAUSES in Bandy, not joint requirements: a village
    # splits because it is hungry OR riven OR led by two rivals. They therefore combine as a MAX, not a
    # product. Multiplying them (as the first version did with depletion alone) would drive the hazard toward
    # zero as factors were added, i.e. adding causes of fission would make fission rarer. The DISCOURAGING
    # factors stay multiplicative, since each genuinely damps whatever the cause. [DESIGN — Bandy names the
    # directions, not the coefficients.]
    bud_w_mate_competition: float = Field(1.0, ge=0.0, le=1.0)
    bud_w_rivalry: float = Field(1.0, ge=0.0, le=1.0)
    bud_w_grievance: float = Field(1.0, ge=0.0, le=1.0)
    # ── WEALTH → OBLIGATION → PRODUCTION (2026-07-27) ───────────────────────────────────────────
    # TYPE **C (Conversion)** · UNIT **agent pair** · INVARIANT **DEBITED** (the grant SPENDS material) ·
    # ANCHOR [Sahlins 1963, VERIFIED, already filed in LITERATURE.md].
    #
    # THE DIAGNOSIS THIS FIXES. Material never concentrated in the elite - noble_material_lift 0.87-1.04 -
    # and it survived every explanation tried: not decay (zeroing it changed nothing), not leveling (off
    # changed nothing), not elite breadth (narrowing 51% -> 16% doubled the PEOPLE lift and left material at
    # 0.99). The cause is structural: `material` is a TERMINAL STOCK. It is produced from hunting, it sits,
    # it decays, and it cannot buy anything. A stock with no investment channel cannot compound, so
    # per-capita concentration stays flat however well it is protected. That is also why the model's elite is
    # in PEOPLE - followers are the only asset that compounds, so they are the only elite we ever see.
    #
    # Sahlins on the Melanesian big-man: "Deploying his resources carefully, the emerging leader USES WEALTH
    # TO PLACE OTHERS IN HIS DEBT ... he constructs a following whose production may be harnassed to his
    # ambition." Wealth's function is conversion - into obligation, and obligation into others' production.
    #
    # MECHANISM: a creditor spends `material` to feed a band-mate in deficit (the grant is debited from the
    # creditor and arrives as kcal, which is what a hungry agent can use). In return he holds a claim on that
    # agent's future durable output until the debt is discharged. Conversion rate is NOT invented: it is the
    # inverse of the model's own production relation, material = material_hide_frac x meat kcal.
    # FEAST CADENCE (2026-07-27). Sacrifices are events at gatherings, not a per-step bleed. Applying
    # `legit_feast_frac` every step drained ~97%/yr of the durable stock and made the elite the set of agents
    # who had spent their wealth on rank (measured: 673:1 against tribute). Legitimacy is a SHARE of band
    # feasting, so scaling everyone's spend leaves the status outcome alone — the cadence was free for status
    # and decisive for wealth. 12 = annual, matching `aggregation_period`. 0 = the old per-step behaviour.
    feast_every: int = Field(12, ge=0)
    enable_wealth_obligation: bool = False        # default OFF ⇒ bit-exact
    obligation_grant_frac: float = Field(0.10, ge=0.0, le=1.0)    # share of the creditor's stock per grant
    obligation_return_frac: float = Field(0.25, ge=0.0, le=1.0)   # share of a debtor's output redirected
    obligation_premium: float = Field(1.2, ge=1.0)                # claim per unit granted (>1 = the gift binds)
    obligation_min_ratio: float = Field(2.0, ge=1.0)              # creditor needs this multiple of band-mean
    village_circumscription_gain: float = Field(0.6, ge=0.0)  # the fission threshold RISES with relocation cost: eff_thr = base·(1 + gain·d_nearest_open/R). Bandy: 170 open → ~277 when circumscribed ⇒ +60% ⇒ gain 0.6 [ANCHORED, Bandy 2004 p.330]
    # Stage 1b — TERRAIN-DEPENDENT MOVEMENT COST: relocating burns energy scaled by terrain difficulty (the terrain
    # `cost` field ∈[0.15,1], slope/elev-driven, water=1). Realized cost = move_cost_kcal·cost[dest] DRAINED at
    # metabolism (moving repeatedly depletes reserve → selection for sedentism) AND PERCEIVED in the IFD utility
    # (agents prefer to stay / take cheap-terrain steps → central-place foraging, prime real-estate valued). Locomotion
    # was previously FREE (move_cost_flat=0, fixed per-step BURN). Default OFF ⇒ no move cost, bit-exact.
    # Stage 1c — CATCHMENT SITE-APPRAISAL (Kennett-Winterhalder IFD-suitability + Vita-Finzi catchment + Orians-Pearson
    # central place): a static per-cell SITE-VALUE field = Σ_{catchment} S_pot(c')·exp(−λ·dist·(0.5+cost(c'))) — the
    # resource potential of the surrounding catchment DISCOUNTED by cost-distance (rugged/far cells contribute less).
    # Normalized [0,1], scaled by site_gain·BURN, PERCEIVED in the IFD utility (occupancy-independent). This gives a
    # GLOBAL gradient that agents climb toward prime central places → solves the ASSEMBLY problem (converge on best
    # catchment, not coordinate) + values prime real-estate + tightens communities onto catchment cores. Perceived-only
    # (anticipation) — actual food is still forage cap + point-superlinear + storage (no double-count). Default OFF ⇒ bit-exact.
    enable_site_appraisal: bool = False
    site_gain: float = Field(0.0, ge=0.0)                     # central-place bonus magnitude (× BURN × normalized suitability); UNANCHORED (sweep)
    site_radius: int = Field(2, ge=1)                         # catchment radius (Vita-Finzi 5–10 km ≈ 1–2 cells) [VERIFIED-anchored]
    site_lambda: float = Field(1.0, ge=0.0)                   # cost-distance decay of catchment contribution; UNANCHORED
    enable_terrain_move_cost: bool = False
    move_cost_kcal: float = Field(0.0, ge=0.0)                # kcal to traverse a max-cost (cost=1) cell; realized = ·cost[dest].
    # CALIBRATED ~750 (≈0.01·BURN): a ~10 km residential move costs a human ~50–75 kcal/km × 10 km ≈ 500–750 kcal
    # (locomotion energetics). This is BOTH the physical scale AND the beneficial sweet spot: at 750 packing 25.7→30.3%,
    # max/cell 25.7→32, pop healthy (430); ABOVE it over-penalizes (per-step movement IS essential foraging → starves
    # marginal agents; 0.1·BURN collapses pop). [VERIFIED-anchored to walking energetics; sweep-confirmed non-lethal window.]
    # Social-Evolution Stage 2: GENEALOGY LOGGER — opt-in append-only logging of each birth/death (uid, mother,
    # father, lineage, band_id, step, cred) to an in-memory flat buffer (O(births+deaths); dump to disk offline).
    # A PURE OBSERVER: writes AFTER the step, reads nothing back, never touches the RNG or dynamics (bit-exact).
    # The analytic substrate for Stage 3 (lineage-extinction curves, dynasty depth vs assabiyah, who-fathered-whom).
    enable_genealogy_log: bool = False
    # Ascribed-status mate-choice (blueprint …_AscribedMateChoice): let cred (ascribed lineage) earn a mating
    # advantage, SOCIETY-GATED (Boehm) — ≈0 egalitarian, rising complex→stratified. Mate weight interpolates from
    # prowess (egalitarian) to base_status=cred·prowess (stratified): w = (prowess · cred^(a·sw))^mate_choice_strength.
    # Fixes the composite status→RS ~0 (R-35: cred had no mating channel). Default OFF ⇒ prowess-only, bit-exact.
    enable_ascribed_mate_choice: bool = False
    ascribed_mate_strength: float = Field(0.0, ge=0.0)   # global scale `a` of the ascribed(cred) mating exponent; UNANCHORED
    # Seasonal MARRIAGE-AGGREGATION ("the gathering"; blueprint …_MarriageAggregation): dispersed bands converge on
    # abundant sites in the abundance window; unpaired adults pair ACROSS bands (regional connubium) → durable
    # bonds; then disperse. Fixes the low-density mate-gate collapse (R-37) — families form in every biome via a
    # regional marriage network (Wobst/Steward/Lee), not a daily within-camp mate-gate. When ON, the daily
    # `_do_pairing` is REPLACED by the periodic gathering; births still gate on the persistent pair-bond year-round.
    # Default OFF ⇒ daily within-band pairing, bit-exact.
    enable_marriage_aggregation: bool = False
    aggregation_period: int = Field(12, ge=1)             # steps between gatherings (12 = annual)
    aggregation_season_threshold: float = Field(0.8, ge=0.0, le=1.0)  # gather only when ClimateField.season() ≥ this (abundance window); ignored on static fields
    aggregation_radius: float = Field(8.0, gt=0.0)        # connubium/travel range: a band's site must be within this many cells (~80 km); isolated bands get no gathering (die — "se la vi")
    aggregation_site_sep: float = Field(10.0, gt=0.0)     # min cell separation between aggregation sites (≈ one per region)
    aggregation_residence: str = Field("virilocal")       # {virilocal (bride→groom), uxorilocal (groom→bride), flexible (smaller→larger band)}
    aggregation_rank_homogamy: float = Field(0.0, ge=0.0)  # 0 = directional only; >0 = like-cred assortment (rank homogamy) preserves the lineage gradient
    # ── Neutral-marker GENOME (population genetics: relatedness, inbreeding, effective pop size Nₑ, drift). A DIAGNOSTIC
    # substrate, NOT the marriage rule — forager exogamy is cultural (lineage/clan; see connubium). Founders seeded with
    # distinct alleles; children inherit each locus Mendelian ½/½. genome.py. Default OFF ⇒ no genome carried, bit-exact.
    enable_genome: bool = False
    genome_loci: int = Field(32, ge=1)                    # number of neutral loci (relatedness resolution ~1/L)
    genome_mutation: float = Field(0.0, ge=0.0, le=1.0)   # per-locus per-birth mutation prob (0 = pure drift / infinite-allele)
    # ⚠ THE "~7 LINEAGES/BAND, DOMINANT SHARE 0.38" TARGET CITED BELOW DOES NOT EXIST (retracted 2026-08-04,
    # RESULTS Addendum 28; propagated to the point of use 2026-08-06, Addendum 29 — Charter P3). The string
    # "lineage" occurs ZERO times in Hill et al. 2011. Its unit is co-residence of PRIMARY KIN (brothers,
    # sisters, parents, offspring); the three "0.38"s are Table 1 cells (Nunamuit, Hadza, a column average).
    # The R-90/R-92/R-93 REASONING below is untouched by this — an absorbing lineage process really does
    # fixate, and a share really does have a hidden denominator — but the NUMBER those arguments are aimed at
    # is not a literature target, so nothing here is calibrated and none of it should be scored. `legit_threshold`
    # = 0.15 and `rank_hierarchy_frac` = 0.15 were both DERIVED as ~1/7 from it and are therefore UNANCHORED
    # until a real forager lineage-concentration source is found (MARKER_MATRIX #6 — none exists in the folder).
    # Values deliberately left as they are: re-deriving them is a calibration decision, not a doc fix.
    # ── LINEAGE BRANCHING (R-90). `_lineage` (the named patriline/patriclan — the exogamy unit AND the dynasty unit)
    # was founder-seeded and only ever LOST by extinction, never created: an ABSORBING process that fixates with
    # probability 1. Measured (R-89): 3000 founding lines drifted to 5 by step 1950 and stuck there, which (a) breaks
    # the FILED Hill-2011 target of ~7 lineages/band + dominant-lineage share 0.38 that R-25 already passed, and
    # (b) freezes the elite layer, since with no non-ascribed lineage left the gumsa→gumlao reversion cannot fire.
    # Real named descent groups both die AND branch. Same INFINITE-ALLELE device genome_mutation already uses.
    # Deliberately NOT size-triggered segmentation: capping lineage size would make `top_share` an artifact of the
    # cap, destroying the very statistic T-9 measures against Zerjal/Yan. Rate 0.0 ⇒ no RNG draw ⇒ bit-exact.
    enable_lineage_branching: bool = False
    lineage_branch_rate: float = Field(0.0, ge=0.0, le=1.0)   # per-BIRTH prob the child founds a new named line
    # ── LINEAGE SEGMENTATION (R-92) — the CORRECTED SHAPE of the above. Per-birth branching mints SINGLETONS,
    # and a lineage of one usually leaves no descendants, so it adds a churning tail of ephemeral names that
    # inflates the COUNT while the dominant line keeps its mass untouched. Measured (R-90, campaign scale):
    # n_lineages 5→32 but eff_lineages (inverse-Simpson) FELL 3.4→1.8 and top_share ROSE 0.42→0.73 — diversity
    # up on paper, down in substance, and lineages_per_band barely moved (2.14→2.33 against a target of ~7).
    # Real Y-haplogroup trees do not sprout singletons at the tip; an existing line SEGMENTS into sub-clades
    # that inherit real membership. So: pick a living member as the apical ancestor and split off ALL of its
    # live patrilineal descendants as a new named line. Both halves are viable and both stay spread across
    # bands, which is what lifts per-band diversity toward the Hill 2011 target.
    # [RETRACTED 2026-08-06 — there is no Hill 2011 lineage target; the paper has no lineage data at all
    # (Addendum 28). The SEGMENTATION MECHANISM is unaffected and still correct; only the number it was
    # aimed at is void, so this is not calibrated to anything and must not be scored.]
    # NB this is NOT the size-CAPPED segmentation rejected in R-90: hazard scales with size (a Yule process,
    # which is what generates realistic skewed haplogroup distributions) but nothing bounds a lineage's size,
    # so `top_share` stays a free measurement rather than an artifact of a threshold.
    # ── RELATIVE legitimacy (R-93) — `legit_threshold` compares a lineage's SHARE of its band's feasting to a
    # CONSTANT, and a share has a hidden denominator: the mean share is 1/lineages_per_band, so the test only
    # discriminates while lineages_per_band > 1/legit_threshold. At the campaign's 0.15 that boundary is 6.67,
    # against a ~~Hill 2011 target of ~7~~ — a FIVE PERCENT margin against NOTHING: the target does not
    # exist (RETRACTED 2026-08-06, Addendum 28). The hidden-denominator ARGUMENT stands on its own; the
    # 6.67-vs-7 coincidence that made it look calibrated does not. Nobody changed the parameter; the substrate
    # drifted under it (measured lpb 2.14-3.69), at which point the AVERAGE lineage clears the bar and
    # "nobility" becomes universal by arithmetic rather than by competition. R-92 confirmed a healthier
    # substrate does NOT rescue it: the DOMAIN violation still fires at step ~650 with segmentation on.
    # Fix: normalise the share by the number of lineages actually competing in that band, so the stored stock is
    # a RELATIVE share where 1.0 means "exactly an average lineage" — scale-free, and Friedman's logic anyway
    # ("one lineage convinces all the others" is about standing out from your neighbours, not clearing a fixed bar).
    # ── SCALE-FREE resentment (R-94) — the SAME bug class as legit_threshold, one layer down. Privilege was
    # `(mean_cred_ascribed − mean_cred_other)/mean_cred_other ÷ resent_privilege_ref`, with ref=10.0 chosen while
    # ascription was UNIVERSAL and cred saturated toward 1+legit_cred_gain=11. Once R-93 made nobility a real 6%
    # minority the gap shrank, privilege peaked at 0.166 against a 0.5 threshold, and reversions NEVER fired
    # (0 vs 5,741). The reverse mechanism had been tuned against the BROKEN forward mechanism, so repairing the
    # forward one moved the regime out from under it. Per charter D15, the fix is a scale-free measure rather
    # than a re-tuned constant: privilege becomes an EFFECT SIZE — the noble/commoner cred gap divided by the
    # band's own pooled spread — which has no denominator left to drift AND lets the threshold be anchored on
    # Cohen's conventions (0.2 small / 0.5 medium / 0.8 large) instead of invented.
    # ── RESENTMENT AS A TRUE ACCUMULATOR, HELD BY THE VILLAGE (R-95). Two flags, separable but ENTANGLED —
    # neither works alone, and there is a test asserting exactly that.
    #
    # (a) ACCUMULATOR. `_do_delegitimation`'s own docstring says in capitals that resentment ACCUMULATES, after
    #     Leach — *"prestige-seeking only increased their followers' resentment and hastened their overthrow"*.
    #     The code implemented an EMA, which does not accumulate: it TRACKS, converging to whatever it is fed.
    #     So a threshold at or above the typical privilege can NEVER be crossed at any horizon. Measured (R-94):
    #     the grudge rose to 0.796 against a threshold of 0.800 and stopped — 1 revolt in 3000 years.
    #     Accumulating instead makes the TIME-TO-REVOLT the anchored quantity, which is what Leach actually
    #     claims, and removes the threshold as a free parameter (it is fixed at 1.0 by construction).
    # (b) VILLAGE UNIT. R-88 measured band lifetime at 10.2 yr median / 17.5 mean, while the grudge needed
    #     700-1600 yr to mature — the memory outlived its container by ~40-100x, and band fission resets it to
    #     zero. Leach's gumlao premises describe VILLAGES ("villages autonomous", headmen, councils of elders),
    #     not 25-person residential bands, so the settlement is both the lit-correct unit AND the one that
    #     persists. Follows R-71's per-SITE precedent exactly: the place remembers, the members churn.
    # ── LOCAL ascription (R-96). `_lineage_ascribed` was a GLOBAL set while every mechanism acting on it is
    # LOCAL, so one village's revolt de-ranked that lineage in EVERY other village at once. Measured (R-95):
    # ~7% of all lineages stripped per revolt, and nobility went from 82% of villages to 3% — annihilated
    # rather than cycled. It contradicts the anchor directly: Leach's observation is that communities sit in
    # DIFFERENT states simultaneously ("shifting back and forth"), which a single global set cannot represent.
    # With this on, rank is held per (community, lineage): a lineage is noble IN A PLACE, and a revolt touches
    # only the community that revolted. The community is the settlement when village resentment is on, else
    # the band. Rank is NOT portable — a family that moves must earn standing where it arrives, which is what
    # "villages autonomous" implies.
    # ── RANK UNLOCKS HIERARCHY (R-98). `society_from_character(density, surplus_frac)` decides a band's society
    # from CROWDING and SURPLUS only — it never asks whether anyone is actually ranked. So a village where every
    # lineage is hereditary nobility is still labelled `egalitarian_forager` if it is sparse and poor, and since
    # LEADER_SOCIETY_WEIGHT is 0.0 there, its nobility has NO structural consequence: it cannot grow past the
    # band cap, sheds no scalar stress, and the whole elite layer is decorative with respect to settlement size.
    # The model has surplus→hierarchy but not rank→hierarchy.
    # THE ANCHOR SAYS RANK CAN COME FIRST. Leach's gumsa were rain-fed SWIDDEN HILL FARMERS without a storable
    # glut — no aquatic gate, no great surplus — yet had ranked lineages, chiefs, tribute, and "all settlements
    # under one chief". Testart's preconditions are one route to hierarchy, not the only one.
    # So a band holding ranked lineages is promoted ONE rung on the ladder, and deliberately only one: this
    # opens the route, it does not hand out chiefdoms.
    enable_rank_hierarchy: bool = False
    rank_hierarchy_frac: float = Field(0.15, ge=0.0, le=1.0)   # ascribed head-count share that counts as "ranked"
    # ⚠ [UNANCHORED — the derivation below is void. Addendum 28/29.] It read: "0.15 is ~1/7: the FILED Hill 2011
    # target is ~7 lineages per band, so one ranked lineage among them is ~0.14 of heads … tied to a target the
    # model already carries rather than picked freely." **Hill et al. 2011 contains no lineage data at all** —
    # the word does not appear in it — so there is no ~7, and 0.15 was not tied to anything. It is a free
    # parameter that has been reading as a derived one. Left at 0.15 (changing it is a calibration decision, and
    # `enable_rank_hierarchy` is default-OFF), but it must not be presented or scored as anchored.
    enable_local_ascription: bool = False
    enable_resentment_accumulator: bool = False
    resent_years_to_revolt: float = Field(80.0, gt=0.0)   # yr to revolt at UNIT privilege (effect size 1.0);
    # [Leach via Flannery ch.10, VERIFIED] hereditary inequality "lasted for a few generations, and then
    # collapsed" => ~60-100 yr. Privilege scales it: twice the gap, half the time.
    enable_village_resentment: bool = False
    enable_relative_resentment: bool = False
    resent_effect_threshold: float = Field(0.8, ge=0.0)   # sustained effect size that triggers reversion (Cohen "large")
    enable_relative_legitimacy: bool = False
    legit_rel_multiplier: float = Field(2.0, ge=0.0)      # cross at this MULTIPLE of an average lineage's share
    enable_lineage_split: bool = False
    lineage_split_rate: float = Field(0.0, ge=0.0, le=1.0)    # per-MEMBER per-step hazard (lineage hazard = rate·n)
    lineage_split_min_segment: int = Field(8, ge=1)           # both halves must reach this, else the split is skipped
    # ── CONNUBIUM: real individual-level EXOGAMY so the ~500 mating network (Wobst 1974) EMERGES from the kin-taboo
    # instead of the blind spatial aggregation_radius. A ~25-band is too small to self-mate under a real prohibition →
    # marriage must reach across bands → the pool self-organizes to ~connubium scale. blueprint …_Connubium. Default OFF
    # ⇒ only the historical parent-child avoidance applies (bit-exact).
    enable_exogamy: bool = False
    exogamy_degree: str = "lineage"                       # {"nuclear" (parents/sibs), "lineage" (+patriclan), "cousin" (+genome r>r*)}
    exogamy_relatedness: float = Field(0.125, ge=0.0, le=1.0)  # r* first-cousin threshold for the "cousin" degree (needs enable_genome)
    mate_search_min_eligible: int = Field(3, ge=1)        # m*: eligible-mate famine-safety margin (the connubium's cv_safe)
    # Cut 2 — ADAPTIVE connubium: replace the fixed aggregation_radius with a per-seeker expanding-ring search that
    # grows until ≥ m* eligible non-kin mates are in reach (or the travel cap). The realized reach self-organizes to the
    # connubium scale (Wobst ~500) instead of being set by a radius. Needs enable_exogamy. Default OFF ⇒ bit-exact.
    enable_adaptive_connubium: bool = False
    mate_search_max_radius: int = Field(15, ge=1)         # travel cap on the marriage search (~150 km); isolated seekers past it stay unpaired
    # PRODUCTIVITY-SCALED MOBILITY (blueprint …_ProductivityScaledMobility): the diffusion step STRIDE scales
    # inversely with STATIC local geographic productivity (Kelly 1995 / Binford 2001: mobility ∝ 1/productivity).
    # Low-NPP (savanna/desert) → longer stride → agents spread over sparse territory instead of piling on the few
    # rich cells (the R-37/R-39 collapse root). High-NPP (forest) → stride→base=1 → dense-forest dynamics unchanged.
    # r = clamp(round(base·(npp_ref/max(local_npp, npp_floor))**exp), base, r_max). Default OFF / base=1 ⇒ bit-exact.
    # Calibration (ref/exp/max) PROVISIONAL — mechanism ships ablatable; locking the law for canonical runs needs
    # supervisor sign-off. (§4.8.19; R-39.)
    # AGGLOMERATION ATTRACTION/PRODUCTION SPLIT (R-106 Addendum 13, 2026-07-31). The point-superlinear
    # agglomeration term is applied TWICE from one parameter set: as a per-capita premium in the movement
    # scorer (`substrate.diffusion_select_target`, it ATTRACTS) and as realized output in the harvest
    # (`phase1_model`, `S += aggl_R·(n^β − n)`, it FEEDS). Addendum 10 measured the consequence: ablating
    # agglomeration drops population to x0.20–0.45 because it supplies over half the economy, while max cell
    # occupancy falls 159 → 10 — so the concentration defect could not be addressed without destroying
    # subsistence. This weight scales the PERCEIVED premium alone, leaving realized production untouched, so
    # the two functions become independently tunable. 1.0 ⇒ bit-exact (the shipped behaviour).
    aggl_attraction_weight: float = Field(1.0, ge=0.0)
    enable_productivity_mobility: bool = False
    mobility_base_radius: int = Field(1, ge=1)               # stride at/above npp_ref
    mobility_max_radius: int = Field(6, ge=1)                # cap on stride (bounds cost + jump-over risk); PROVISIONAL
    mobility_npp_ref: float = Field(900.0, gt=0.0)           # forager-median NPP g/m²/yr (Tallavaara); r=base at/above; PROVISIONAL
    mobility_npp_floor: float = Field(50.0, gt=0.0)          # denom floor so hyper-arid cells don't → ∞ range; PROVISIONAL
    mobility_exponent: float = Field(1.0, ge=0.0)            # Kelly/Binford slope; 1.0 = strict ∝1/NPP; PROVISIONAL (bracket)
    # PRESSURE-AWARE MOBILITY (R-106 Addendum 6, 2026-07-31): the NPP-driven stride above is STATIC/geographic —
    # a cell packed with 40+ occupants still reads as "rich" (raw local_npp unchanged), so `mobility_radius`
    # never expands for an agent stuck in a crowded cluster (measured 2026-07-30: r_used==1 in 100% of
    # equilibrium decisions, Addendum 4). Kelly/Binford's actual packing claim is density-dependent — mobility
    # responds to REALIZED pressure, not nominal biome fertility. `source="intake"` swaps the driving variable
    # to the agent's own `_intake_ema` (the SAME live intake/requirement EMA `enable_intake_fertility` computes,
    # R-106 — reused, not duplicated), which is occupancy-diluted by construction. Auto-enables the EMA update
    # loop even when `enable_intake_fertility` itself is off (`phase1_model.py`), so the two mechanisms stay
    # independently ablatable while sharing one signal. `source="npp"` (default) is the ORIGINAL formula,
    # bit-exact — this is a pure additive mode, not a replacement.
    mobility_pressure_source: Literal["npp", "intake"] = "npp"
    mobility_intake_ref: float = Field(1.00, gt=0.0)         # ratio at/above which stride=base; reuses the
    #   maintenance anchor `intake_fert_lo` already carries (§21.10) rather than inventing a new number
    mobility_intake_floor: float = Field(0.15, gt=0.0)       # denom floor so a near-starving ratio doesn't → ∞ range
    # CENTRAL-PLACE FORAGING fixes (blueprint …_CoMovementCentralPlace; R-41): family co-movement snaps the whole
    # family onto the mother's (root's) single cell → she extracts S/(n+family) not S/(n+1) → energetic-fertility
    # collapse in marginal biomes. Real foragers CO-RESIDE but forage DISPERSED and SHARE (Isaac 1978 central-place;
    # Hawkes/Marlowe Hadza; Kaplan children-are-provisioned). Three ablatable prototypes (all default OFF ⇒ bit-exact
    # exact-snap co-movement); at most one should be canonicalized after the comparison. Need enable_pair_bonds.
    comove_anticipate: bool = False        # (i) the root's move utility counts its followers: per-capita on S/(n+family_size), so she picks emptier/richer ground
    comove_footprint: int = Field(0, ge=0)  # (ii) followers scatter to lowest-occupancy cells within this Chebyshev radius of the head (0 = exact snap); a dispersed camp
    # (ii-scaled) the footprint = the biome-scaled MONTHLY RANGE on the uniform grid: the 10 km cell = forest
    # monthly range → forest k≈0 (tight camp), sparser biomes k grows ∝1/NPP. Honors the cell-size calibration
    # without variable cells (which would break the lattice + double-count the Tallavaara capacity). Reuses the
    # mobility_* scaling shape; overrides the fixed comove_footprint when True.
    comove_footprint_scaled: bool = False
    comove_footprint_max: int = Field(3, ge=0)   # cap on the scaled footprint radius
    comove_provision_exclude: bool = False  # (iii) JUVENILE followers (age<forage_age_min) take NO forage share (central-place: children are provisioned, not self-extracting) → don't dilute the mother's cell
    # F.3c-2b FAMILY-KNOB localization: reproduction reads the mother's BAND-society family knobs (mate-choice skew,
    # descent, heritability, paternal investment) instead of the global config. Decision (so it does NOT override
    # the E.3 m calibration): the global config is the EGALITARIAN BASELINE; a band applies the ADDITIVE DELTA from
    # the egalitarian preset — an egalitarian (un-morphed) band keeps the global value EXACTLY, only a morphed
    # complex/stratified band deviates (e.g. higher mate_choice_strength + lower lineage_reversion = more dynastic).
    # Needs enable_band_affiliation + enable_morph (society must be per-band). Default OFF = bit-exact.
    enable_band_family_knobs: bool = False
    # ABLATION (lumping experiment): each step, flatten every agent's cred to its BAND (cell) mean → the band is
    # internally homogeneous in status (no within-band heterogeneity). Tests whether the individual status
    # DISTRIBUTION is load-bearing for R-18 (mortality-on-low-cred), R-19 (compositional anti-fragility), and the
    # inequality contest — i.e., whether the model could lump to band-as-unit. Default OFF (full individualism).
    homogenize_cred: bool = False
    # Full band-as-unit lump: ALSO flatten the achieved PROWESS facet within the band (applied after the prowess
    # EMA each step). With homogenize_cred this erases ALL within-band status heterogeneity (cred AND prowess) →
    # the strict "treat each band as a single status unit" ablation. Default OFF.
    homogenize_prowess: bool = False
    # Carbon-on-substrate (Tier-1): meat/contest weight reads accumulated `cred` (status), not the `φ` trait,
    # when ON (else φ — preserves the Sugarscape contest tests). Founder cred is seeded lognormally
    # (cred_seed_sigma; median 1) and inherited at IBI birth as a noisy lineage copy `mother.cred·exp(N(0,σ))`
    # (cred_inherit_sigma). Decay/earning OFF in Tier-1 (persistent heritable status). See Carbon scoping bp.
    enable_cred_status: bool = False
    cred_seed_sigma: float = Field(0.0, ge=0.0)      # founder log-status spread; 0 = uniform (no hierarchy)
    cred_inherit_sigma: float = Field(0.0, ge=0.0)   # lineage-copy noise at birth; 0 = exact inheritance
    # CRED RENORMALISATION (R-81) — per-step rescale of cred to population-mean 1. FIXES a latent homeostat
    # defect: the inheritance reverts toward a FIXED 1.0 anchor (a contraction validated in R-18, pre-selection),
    # but R-19/R-20 added fertility-weighted mate-choice + a `cred·prowess` product base — both inject an upward
    # bias each generation that DEFEATS the fixed-1.0 contraction (measured: mean cred 1→18.6 over 2000 steps, so
    # the homeostat's `ρ·1.0` pull becomes negligible vs `(1−ρ)·base` ⇒ the homeostat progressively loses grip).
    # Renormalising to mean-1 each step restores the anchor's meaning (1.0 = the running mean again) ⇒ constant
    # homeostat grip ρ at any scale, without the "revert-to-co-moving-mean" unbounded-drift the red-team blocked
    # (RT: that had no fixed scale; this pins the scale hard). Cred enters every downstream weight RELATIVELY
    # (`(cred)^κ` / Σ, normalised mate weights), so the rescale is dynamics-neutral for those — but it re-tightens
    # the inheritance homeostat, which LOWERS the realised Gini (so it re-touches R-19's status→RS; re-verify).
    # Prerequisite for the elite/material layer (a leaking homeostat can't be made state-dependent, Stage D).
    # Default OFF ⇒ bit-exact.
    enable_cred_renorm: bool = False
    # ── ELITE LAYER, STAGE A (R-82): MATERIAL as a third capital cell ───────────────────────────────
    # The status vector is [cred (ascribed), prowess (achieved), MATERIAL (durable)]. cred/prowess couple to
    # the food contest and mating, but BOTH wash out materially — measured corr(cred, wealth) ≈ 0, because the
    # sharing economy feeds everyone to their reserve cap each step. **Durability is the stratifying property**:
    # a small per-step capture advantage integrates into a large stock gap only if the stock PERSISTS.
    #
    # ANCHORS (all [VERIFIED] in LITERATURE.md): **Sahlins 1968** — foragers deliberately "run below capacity"
    # (~20–30%), so surplus is a SOCIAL outcome, not a technical given; **Boehm 1993** — that baseline is held
    # by active leveling (38/48 societies remove an over-assertive individual; triggers include "lack of
    # generosity or MONOPOLIZING RESOURCES"); **Testart 1982** — STORABLE surplus is the escape route, because
    # a granary cannot be shared out the way a carcass can; **Hayden** (aggrandizer / control-of-redistribution,
    # TO-GRAB) — the driver: the aggrandizer claims MORE THAN HE NEEDS and converts it to durable goods.
    #
    # MECHANISM — capture the granary LEFTOVER. The S.2 draw is deficit-capped, so weight-rich but near-full
    # claimants leave surplus in the store ("any leftover … stays in the granary"). That leftover is exactly
    # what an aggrandizer takes beyond need: it is claimed status^κ-weighted into a DURABLE `material` stock
    # (not `wealth`, which is burned and capped). High cred ⇒ bigger claim ⇒ material stratification that does
    # NOT wash out. Requires enable_storage (the granary) + the overwintering/seasonal zone.
    enable_material_capture: bool = False
    # SOURCE = GAME, not the granary (supervisor correction, R-82b). Durable goods in a forager economy are the
    # BYPRODUCT OF HUNTING — hides, furs, bone, antler, sinew — produced in proportion to game taken. Stored
    # food is EATEN or rots; turning granary grain into durable wealth conflated subsistence with capital.
    # (Testart's storable-food route drives inequality by BUFFERING SUBSISTENCE, which is a different channel.)
    # Bonus: hides ∝ meat couples material to the hunting economy, hence to `prowess` — the achieved facet.
    material_hide_frac: float = Field(0.0, ge=0.0)              # durable yield per unit meat taken (sets UNITS only)
    material_capture_frac: float = Field(0.0, ge=0.0, le=1.0)   # share of the cell's hide pool claimed by aggrandizers
    material_decay: float = Field(0.0, ge=0.0, le=1.0)          # per-step depreciation of the durable stock (0 = imperishable)
    # R-103d MATERIAL INHERITANCE — bequeath durable capital at death, the missing 'bequeathing' step (Flannery
    # ch.10: big men "had no way of bequeathing renown to their offspring") that converts a lifetime OFFICE
    # advantage into a heritable LINEAGE estate. Rule is regime-dependent [Goody 1976 diverging devolution;
    # D-PLACE EA075×EA028 cross-tab, LITERATURE.md]. Default OFF ⇒ material dissolves at death (bit-exact).
    enable_material_inheritance: bool = False
    material_inheritance_rule: str = Field("primogeniture")     # none|primogeniture|partible_equal|patrilineal_sons
    #   primogeniture   → whole estate to the ELDEST surviving child (concentrates; the extensive-agri pattern)
    #   partible_equal  → split equally among ALL surviving children (dissipates; Goody's intensive-agri devolution)
    #   patrilineal_sons→ split equally among surviving SONS (the EA-modal 43-61% rule)
    # R-103e — HEIR COUPLED TO STATUS. Estate+rank should pass TOGETHER (Flannery ch.16 chiefly primogeniture),
    # not to a random child. ON ⇒ primogeniture picks the highest-CRED (status) child, so wealth follows rank.
    material_heir_by_status: bool = False
    # R-103e — LEGITIMACY EXEMPTS THE NOBLE FROM LEVELING. The load-bearing device (Flannery ch.16 "how to turn
    # rank into stratification"; Friedman: a legitimated lineage's holding is "his by right… entitled to tribute",
    # NOT overreach-grievance). Without it, the model's Boehm overreach mechanism DEPOSES any material accumulator,
    # so an elite can never lock in. ON ⇒ an ASCRIBED (noble) leader's material-overreach grievance is scaled by
    # (1 - noble_exemption_frac); his FAILURE-TO-DELIVER grievance is untouched (a noble is still deposed for
    # famine, just not for wealth). Default OFF ⇒ bit-exact.
    enable_noble_leveling_exemption: bool = False
    noble_exemption_frac: float = Field(1.0, ge=0.0, le=1.0)    # 1.0 = full waiver of the wealth-grievance for nobles
    # R-103f — PER-LINEAGE (CHIEFLY) TRIBUTE. The office levy (`leader_share`) fills a rotating OFFICE and cannot
    # make a hereditary estate (R-103e benchmark: leader_material_lift rose to 1.26 but noble_material_lift stayed
    # 1.10 — the levy concentrates in the office, not the lineage). This is the LINEAGE channel: in each band the
    # locally-dominant ASCRIBED lineage's head (the CHIEF, by legitimacy+rank, NOT by winning the office contest)
    # levies `lineage_tribute_frac` of every non-chief-lineage member's durable production. The estate therefore
    # persists across office turnover and is bequeathed WITHIN the lineage — Friedman "the legitimated lineage
    # controls resources and is entitled to tribute"; Earle wealth finance. Rate anchor: gumsa "a thigh from every
    # animal" ≈ 0.10–0.15 of a kill (DM-F6; no % levy rate exists in the lit — D'Altroy&Earle verified neg — so
    # this is calibrated to OUTCOME: noble_material_lift > 1). Default OFF ⇒ bit-exact.
    enable_lineage_tribute: bool = False
    lineage_tribute_frac: float = Field(0.15, ge=0.0, le=1.0)
    # WHO captures — the AGGRANDIZER trait, NOT inherited status. [Hayden 1995 VERIFIED] The captor is an
    # "ambitious, accumulative aggrandizer" — "the best and most highly motivated minds of an epoch" — i.e. a
    # PERSONALITY/STRATEGY TYPE held by a MINORITY, present in every society. It is NOT a rank in an inherited
    # status order. (R-82's first cut weighted capture by cred^κ and measured corr(cred, material) = −0.018:
    # a SPECIFICATION error, not a tuning one — the wrong variable.) Aggrandizers exist everywhere; what varies
    # is whether conditions let them act — which is the gate below. That separation is the testable core of
    # Hayden's thesis: hold the trait constant, vary the gate, and inequality should appear only under abundance.
    aggrandizer_frac: float = Field(0.0, ge=0.0, le=1.0)        # share of agents who are aggrandizer-type
    # WHEN capture is possible — the ABUNDANCE + INVULNERABILITY gate. [Hayden 1995 Fig. 6, p.77 VERIFIED] the
    # top trait row is "Resource Abundance and Resources Invulnerable to Overexploitation or Degradation",
    # running from MINIMUM expression among Egalitarian to MAXIMAL among Entrepreneurs/Chiefs. Extraction can
    # only persist where it does not endanger the stock — otherwise Boehm leveling crushes the aggrandizer.
    # Implemented against the GD-1 stock fraction B ∈ [0,1] (1.0 = at ceiling ⇒ invulnerable; low = overexploited).
    material_invulnerability_min: float = Field(0.0, ge=0.0, le=1.0)   # min local stock fraction B for capture to fire
    # ── LEVELING — the counter-force [Boehm 1993 VERIFIED] ──────────────────────────────────────────
    # R-82's first working cut had capture with NO opposition and ran to material Gini 0.909 while sitting in
    # Hayden's EGALITARIAN density band — chiefdom inequality at forager density, the opposite of his Fig. 6.
    # Hayden's thesis needs BOTH: aggrandizers push, the group pushes back, and ABUNDANCE decides who wins.
    # Boehm: egalitarian societies run a "reverse dominance hierarchy" — the rank and file act as a coalition to
    # suppress upstarts. Of ~47 sanctioned behaviours he tabulates, "lack of generosity or MONOPOLIZING
    # RESOURCES" is an explicit trigger (5); the majority involve dominance/self-assertion. The recurring
    # sanction against a monopolizer is DESERTION and forced disgorging — the Chaco desert a chief "who was
    # stingy", the Nambicuara leave one "too exacting", and "often it is in fact the entire group that leaves".
    # MECHANISM: a co-resident coalition sanctions whoever holds conspicuously more material than the local
    # norm, forcing him to redistribute the excess to his cell-mates (Boehm's sanction executed as Hayden's
    # competitive feast — the two authors' mechanisms are the same act seen from either side).
    # NOTE the deliberate asymmetry with capture: leveling is NOT abundance-gated. Capture is (it needs an
    # invulnerable surplus); leveling always operates. So abundance alone decides the balance — under scarcity
    # capture is gated off while leveling still bites (egalitarian); under abundance capture outruns it
    # (stratified). That emergent competition IS Hayden's thesis, and it is what makes it falsifiable here.
    # ── LEADER SHARE — "managerial rights" over CORPORATE product (R-83, elite-layer step 1) ──────────
    # THE MISSING RUNG between corporate property and personal stratification. Cell ownership in this model is
    # CORPORATE (`_cell_owner` maps a cell to a band_id), but stratification needs PERSONS to differ. The bridge
    # is not ownership — it is AUTHORITY OVER corporate property. [Hayden 1995 VERIFIED]: on the NW Coast
    # aggrandizers "control access to spatially restricted resource locations or productive facilities (fishing
    # rocks, weirs, boats, deer fences, drying sheds)"; that class "had MANAGERIAL RIGHTS over the resource
    # locations and facilities of the group". Managerial rights, not title — the Big-Man/chiefly position.
    # WHY BAND-LEVEL: R-82b's aggrandizer capture was applied per CELL, where 1–2 agents sit, so there was no
    # group to skim and the effect was 1.14×. Bands are ~25 agents and already tracked (`band_id`), so the
    # corporate unit is the band. Wrong level, not wrong mechanism.
    # NOT HEREDITARY, and that is anchored [Boehm 1993 VERIFIED]: leaders are DEPOSABLE — Iroquois sachems were,
    # and among the Yokuts even "a HEREDITARY chief ... suspected of too much self-aggrandizement was ... ignored
    # in favor of another chief". Councils of elders act as the brake (Navajo, Fox, Yokuts, Tupinamba, Cuna).
    # So the office is held on CONTINGENT merit: `band_leaders()` recomputes it each step from cred·prowess, and
    # Boehm leveling still bites the holder. Hereditary succession is a LATER rung, and Hayden says it appears
    # only where resource locations are spatially restricted (NW Coast) — not where land is ubiquitous (New Guinea).
    enable_leader_share: bool = False
    leader_share_frac: float = Field(0.0, ge=0.0, le=1.0)      # share of the BAND's per-step durable output taken as managerial right
    enable_leveling: bool = False
    # ANCHOR [Boehm 1993, VERIFIED]: "Ousting or ostracizing the individual or removing him from a leadership
    # role involved **38 of the 48 societies**" reporting deliberate control of over-assertive leaders — i.e.
    # a DECISIVE sanction is applied in 38/48 = **0.79** of societies (a further 28 instances used softer
    # social pressure; 11/48 report assassination, the top rung). So a conspicuous monopolizer should draw a
    # sanction with probability ≈0.79, not rarely: leveling is the NORM, not the exception. `leveling_strength`
    # is the per-step rate at unit relative excess (excess = local norm), so 0.79 reproduces that.
    leveling_strength: float = Field(0.0, ge=0.0)              # sanction rate per unit of relative excess [0.79 = Boehm 38/48]
    leveling_share: float = Field(0.0, ge=0.0, le=1.0)         # fraction of the excess disgorged when sanctioned [DESIGN]
    # ── R-84 CHALLENGE-SUCCESSION: leadership as a TENURED OFFICE, and the two ways it is LOST ───────────
    # DEFECT this fixes: `band_leaders()` recomputes argmax(cred·prowess) EVERY step ⇒ zero incumbency. There is
    # no office, no tenure, and a leader is never *removed* — he merely stops being the maximum. The ethnography
    # is the reverse: leadership is HELD, and lost to a SANCTION.
    # ANCHOR [Boehm 1993 Table I, VERIFIED — columns counted from the 48-society world survey]:
    #   Public opinion 10 · Criticism 6 · Ridicule 5 · Disobedience 7 · **DEPOSITION 9** · **DESERTION 17** ·
    #   Exile 2 · Execution 10.
    # DESERTION outnumbers DEPOSITION ≈2:1 — the commonest end of a bad leader is that his following WALKS AWAY,
    # not a challenge-and-defeat duel ("if a bad chief was not deposed he might be deserted gradually" — Iban,
    # Freeman 1970:114; "an entire dissatisfied lineage might simply go away" — Mandari, Buxton). And the split is
    # structural, not arbitrary: DEPOSITION societies are the centralized ones (Iroquois sachems, Yap chiefs,
    # Somali sultans, Iban, Assiniboin, Coeur d'Alene, Yokuts) while DESERTION societies are mobile/dispersed
    # (Batek, Mendrig, Apache, Kutchin, Ute, Nambicuara, Yanomamö, Patagonia) — i.e. Sahlins' Nootka-vs-Siuai and
    # Hayden's restricted-vs-ubiquitous resources, showing up as a sanction frequency.
    # TRIGGERS [Boehm 1993, the 47 coded motivations for negative sanctioning]: "dominating others as leader" (14)
    # + "lack of generosity or monopolizing resources" (5) = OVERREACH (19); "ineffectiveness, partiality, or
    # unresponsiveness in a leadership role" (10) = FAILURE TO DELIVER. Hence `office_overreach_weight` = 19/29.
    # THE LOOP THIS CLOSES: overreach is read off the leader's OWN material relative to his band — which is exactly
    # what `leader_share_frac` inflates. A greedier levy raises the sanction hazard on the man taking it. Boehm's
    # reverse dominance hierarchy as a feedback loop, not a constant.
    enable_leader_office: bool = False
    office_challenge_margin: float = Field(0.25, ge=0.0)       # challenger must exceed the incumbent's merit by this factor [DESIGN]
    office_deposition_share: float = Field(9.0 / 26.0, ge=0.0, le=1.0)   # 0.346 = Boehm deposition 9 / (9 deposition + 17 desertion)
    office_overreach_weight: float = Field(19.0 / 29.0, ge=0.0, le=1.0)  # 0.655 = Boehm (14 dominating + 5 monopolizing) / 29 leadership motivations
    office_grievance_gain: float = Field(1.0, ge=0.0)          # per-step sanction hazard at unit grievance [DESIGN — calibrated on tenure]
    # SUCCESSION ON THE HOLDER'S DEATH — two regimes [Sahlins 1972:209, VERIFIED]. The Nootka chief "is an
    # officeholder in a lineage (house group), his following is this corporate group, and his central economic
    # position is ascribed by right of chiefly due" ⇒ "centricity is built into the structure" and the office
    # OUTLIVES him. The Siuai big-man's following "is an achievement — a result of generosity bestowed — the
    # leadership an achievement, and the whole structure will as such DISSOLVE with the demise of the pivotal
    # big-man." True ⇒ big-man regime (vacancy until someone re-earns it); False ⇒ chiefly office (filled at once).
    succession_dissolve: bool = False
    # ── DM-F1 / R-86: THE LEGITIMACY CHANNEL — how ACHIEVED success becomes ASCRIBED rank ────────────────
    # WHY THIS EXISTS. Flannery & Marcus 2012 ch.10 is blunt that our elite layer's premise is insufficient:
    # "if feasting were all it took to produce hereditary inequality, there would have been no
    # achievement-based societies left for anthropologists to study" — competitive feasting "produced
    # individual Big Men who had no way of bequeathing renown to their offspring." That is EXACTLY what the
    # model measures (R-83/R-84: leaders 3.68× ahead, father-was-leader only 53–69%, no transmission), i.e. the
    # model is a correct ACHIEVEMENT-BASED society and hereditary rank needs a different mechanism.
    # THE MECHANISM [Friedman's endogenous scenario, via Flannery ch.10 VERIFIED]: rank is created by a
    # REINTERPRETATION of success, not by accumulation. Successful lineages were not credited with hard work —
    # "they believed that one only obtained good harvests through proper sacrifices to the nats. The key shift
    # in social logic was therefore from 'They must have pleased the nats' to 'They must be descended from
    # higher nats than we are.'" Once a lineage is held to descend from the ruling spirits it controls the
    # region's land and "was also entitled to receive tribute from other lineages".
    # CHARTER DECLARATION (MECHANISM_CHARTER §3.1):
    #   TYPE      C (Conversion) — material → heritable cred, gated on a legitimating belief. An OFF-DIAGONAL
    #             of the capital matrix: the achieved→ascribed cell.
    #   UNIT      LINEAGE (patriline `_lineage`), competing WITHIN a band. Friedman's unit is explicit: "one
    #             lineage convinces all the others". NOT the band, and not the agent (cf. R-82's unit error).
    #   INVARIANT DEBITED, not catalytic — sponsoring the sacrifice SPENDS material ("could sponsor the most
    #             prestigious sacrifices and feed the most visitors"); belief is bought, not merely asserted.
    #   ANCHOR    [VERIFIED Flannery & Marcus 2012 ch.10] for the mechanism; the four rates are [DESIGN],
    #             calibrated against TARGETS T-6 (Hayden's 75% father-was-leader) and T-5 (BHM composite Gini).
    # NOTE on the seam: MECHANISM_CHARTER §9.2 named `GroupVector.religion` as the carrier. On inspection that
    # cell is an int RELIGION ID, while legitimacy is a continuous per-LINEAGE stock — so it lives on the model
    # as `_lineage_legit` (mirroring `_band_surplus`), and `religion` stays reserved for actual religion ids.
    enable_legitimacy: bool = False
    legit_feast_frac: float = Field(0.0, ge=0.0, le=1.0)   # share of a lineage's material spent on sacrifices/feasts each step
    legit_decay: float = Field(0.02, ge=0.0, le=1.0)       # legitimacy fades without renewal (~1/0.02 = 50-step memory)
    legit_threshold: float = Field(0.5, ge=0.0, le=1.0)    # above this share of the band's feasting, the lineage is "descended from higher nats"
    legit_cred_gain: float = Field(0.0, ge=0.0)            # per-step heritable-cred boost to a legitimated lineage's members
    # ── DM-F1 stage 2 / R-87: DELEGITIMATION — the gumsa → gumlao collapse ───────────────────────────────
    # NOT optional polish. R-86 built the ascription RATCHET and it works (father-was-leader 76% vs Hayden's
    # 75%), but a ratchet with no reverse HAS NO EQUILIBRIUM: `ascribed_frac_pop` reaches 0.70–0.85, at which
    # point "descended from higher nats" stops being a distinction. The model derived the need for a collapse.
    # ANCHOR [Leach via Flannery ch.10, VERIFIED]: Kachin society shifts between ranked (**gumsa**) and
    # egalitarian (**gumlao**) modes — "hereditary inequality was repeatedly created, lasted for a few
    # generations, and then collapsed." The driver is accumulated RESENTMENT, not an instantaneous check:
    # ambitious leaders' prestige-seeking "only increased their followers' resentment and HASTENED THEIR
    # OVERTHROW." gumlao premise 1 is "All lineages are considered equal" — a WHOLE-COMMUNITY reversion, which
    # is why the flip is per-BAND rather than per-lineage.
    # THIS IS THE H-CYCLES TEST. MECHANISM_CHARTER §5: every feedback in the model so far is INSTANTANEOUS
    # negative feedback ⇒ a stable node ⇒ exponential return, never oscillation (three independent negatives,
    # DE-14). A DELAYED negative feedback is what admits a complex eigenvalue pair. `resent_alpha` IS that
    # delay, and it is the one parameter the hypothesis actually rides on.
    # Ethnographic period to hit: "a few generations" ≈ 60–100 yr ≈ 720–1200 steps.
    enable_delegitimation: bool = False
    resent_alpha: float = Field(0.004, gt=0.0, le=1.0)     # EMA weight on privilege; 1/240 ≈ a 20-yr generational memory
    resent_threshold: float = Field(0.5, ge=0.0)           # accumulated resentment that triggers the gumlao reversion
    resent_privilege_ref: float = Field(1.0, gt=0.0)       # cred-advantage ratio treated as unit privilege [DESIGN]
    # VALUE HOOK (the supervisor's market insight, deliberately deferred): material's worth is treated as a
    # CONSTANT per unit here. Stage E replaces this with an endogenous, exchange-set value (anchored to a real
    # exchange system — Kula/cattle/bride-price — NOT a price-setting market, which Polanyi puts far later).
    # Keeping it a separate scalar now means Stage E swaps one function, with no rearchitecting.
    material_unit_value: float = Field(1.0, ge=0.0)
    # Cred-vector (B+ stage). `cred` is the LINEAGE facet (ascribed). When `enable_prowess_facet`, the PROWESS
    # facet (achieved) joins the contest weight multiplicatively (Cobb–Douglas, equal within-domain exponents):
    # weight = ((cred+ε)·(prowess+ε))^κ. Default off → lineage-only = R-18 exact. Build step 1 ships the seam;
    # prowess GROWTH/decay (earned from provisioning) is step 2. See SiC_Games_P1_CredVector_BplusPaternity bp.
    enable_prowess_facet: bool = False
    # B+ step 2: prowess GROWTH. Prowess is a decaying EMA of the agent's RELATIVE meat intake (reputation, not
    # instantaneous return — Smith 2004): `prowess ← (1−λ)·prowess + λ·(meat_i / mean_meat)`. λ = `prowess_decay`
    # (EMA rate / fade; 0 = static facet = step-1 seam only). RELATIVE ⇒ mean-pinned ⇒ runaway-safe by
    # construction (mean prowess stays ~1); G.3 supplies the skill/luck component independent of lineage.
    prowess_decay: float = Field(0.0, ge=0.0, le=1.0)
    # B+ step 3: sex-divided PRODUCTION (men hunt → meat, women gather → forage). Tunes the prowess SIGNAL only
    # (male prowess from meat-production credit, female from forage credit), NOT the consumption economy — so
    # e₀/density are preserved (the band still shares meat+forage to everyone). `sex_division`∈[0,1]: 0 = unisex
    # (= step-2, meat-intake signal); 1 = strict. Decouples male prowess from the Cred-weighted consumption
    # share → makes prowess a genuinely independent (hunting) axis from inherited lineage.
    sex_division: float = Field(0.0, ge=0.0, le=1.0)
    # B+ step 4: PATERNITY. At each IBI conception a father is assigned by prowess-weighted mate-choice —
    # P(father=j) ∝ (prowess_j+ε)^mate_choice_strength among living adult males (m=0 = random = the drift-control)
    # — and the child's LINEAGE inherits a BILATERAL blend of the parents' TOTAL standing (cred·prowess, folding
    # the father's hunting record into the child's ascribed rank), with MEAN-REVERSION toward the population mean
    # (lineage_reversion ρ = the c_lineage homeostat; lineage has no decay otherwise — red-team RT-3). Calibrate
    # mate_choice_strength to status→RS r≈0.19 (von Rueden). enable_paternity off → matrilineal (step-1). Reopens
    # R-14 minimally: fertility stays female-IBI (this only sets WHO fathers / how lineage propagates).
    enable_paternity: bool = False
    mate_choice_strength: float = Field(0.0, ge=0.0)         # m; 0 = random paternity (the drift-control twin)
    patriline_weight: float = Field(0.5, ge=0.0, le=1.0)     # father vs mother weight in lineage inheritance
    lineage_reversion: float = Field(0.0, ge=0.0, le=1.0)    # ρ: mean-reversion of inherited lineage (homeostat)
    # B+ step 5: PATERNAL provisioning. A father gives `paternal_provision_frac` of his harvest OVERFLOW (above
    # his cap, otherwise wasted) to his OWN children, drawn against the child's RESIDUAL need AFTER the maternal
    # tiers (RT-2: conserved, no double-feed) — so it bites only on the constrained-mother / ORPHAN cohort (the
    # Marlowe critical-period target; calibrate so emergent male share of <3-yr provisioning ≈ 58%). 0 = pure B
    # (no paternal feeding). Requires enable_paternity (the father-links).
    paternal_provision_frac: float = Field(0.0, ge=0.0, le=1.0)
    # [R-80, NOT BUILT] A status→fertility provisioning channel (husband's overflow → wife's reproductive
    # reserve → shorter IBI) was prototyped and REVERTED: it is structurally inert. The transfer needs a husband
    # with harvest OVERFLOW and a wife with reserve NEED simultaneously, but those are anti-correlated —
    # overflow ⟺ well-fed (so the wife is also full, need≈0); scarcity ⟺ wife-need (but then the husband has
    # 0 overflow). Measured at a crowded equilibrium: 0% of married men had any overflow, 100% of wives had full
    # need ⇒ zero transfers. Root cause is R-16 fertility-pinning: no surplus at r=0, so von Rueden's DOMINANT
    # channel (status→fertility, "enhances fertility more than offspring well-being") cannot operate here. See RESULTS R-80.
    # B++ : ASSORTATIVE mating. The father a mother draws is weighted by his prowess^m (the B+ skew) AND his
    # status-SIMILARITY to the mother — a Gaussian-in-log-status kernel exp(−α·(ln s_j − ln s_i)²), s = cred·
    # prowess, α = assortative_strength. So high-status mothers pair with high-status fathers, CONSOLIDATING
    # dynasties (vs B+'s one-sided draw that dilutes the dynasty through random maternal lineage each
    # generation). 0 = B+ (no assortment — the paired control). Requires enable_paternity.
    assortative_strength: float = Field(0.0, ge=0.0)

    def siler(self, sex: str | None = None) -> SilerParams:
        """Both-sexes schedule (sex=None) or the M-3 sex split (sex='female' / 'male')."""
        both = SilerParams(self.siler_a1, self.siler_b1, self.siler_a2, self.siler_a3, self.siler_b3)
        if sex is None:
            return both
        female, male = _sex_split(both, self.childhood_ratio_mf, self.adult_ratio_mf)
        return female if sex == "female" else male


# ---------------------------------------------------------------------------
# Society presets — switchable, lit-anchored bundles of the family/status knobs.
# Each maps an ethnographic TYPE to (kappa = status-weighted sharing [SubstrateConfig.contest_exponent]) +
# the family knobs (mate-choice skew m, assortment α, descent patriline_weight, status-mobility ρ, paternal
# investment, sex-division). These capture each type's family-dynamics SIGNATURE (skew / descent / heritability
# / sharing) with the available knobs — NOT every institution (bridewealth, the avunculate, persistent
# households are approximated, not mechanistic). Switch seamlessly via `society_knobs(name)`.
# ---------------------------------------------------------------------------
SOCIETY_PRESETS: dict[str, dict] = {
    # Immediate-return mobile foragers (!Kung/Ju'hoansi, Hadza, Mbuti, Aché): leveled, no heritable rank,
    # bilateral/flexible descent, modest skew, band-wide sharing. [Woodburn 1982; Lee 1979; Boehm 1999 reverse
    # dominance; von Rueden 2016 r≈0.19]. ≈ the Silicon-leaning baseline.
    "egalitarian_forager": dict(kappa=0.0, mate_choice_strength=1.0, assortative_strength=0.0,
                                patriline_weight=0.5, lineage_reversion=0.30, paternal_provision_frac=0.5,
                                sex_division=1.0),
    # Delayed-return / complex foragers (NW Coast: Kwakiutl, Tlingit, Haida): heritable RANK from a stored
    # surplus, status-weighted sharing, chiefly lineages. [Ames 1994; Service 1962 chiefdom; Sahlins 1958].
    "complex_forager": dict(kappa=1.5, mate_choice_strength=3.0, assortative_strength=1.0,
                            patriline_weight=0.5, lineage_reversion=0.10, paternal_provision_frac=0.5,
                            sex_division=1.0),
    # Patrilineal pastoralists (Nuer, Maasai, Turkana, Kipsigis): cattle-wealth → bridewealth → polygyny,
    # strong patrilineal descent + patrilocality. [Evans-Pritchard 1940; Borgerhoff Mulder; Betzig 1986].
    "patrilineal_pastoralist": dict(kappa=1.0, mate_choice_strength=4.0, assortative_strength=2.0,
                                    patriline_weight=0.9, lineage_reversion=0.08, paternal_provision_frac=0.5,
                                    sex_division=1.0),
    # Matrilineal horticulturalists (Trobriand, Hopi, Iroquois, Navajo): matrilineal descent + matrilocality,
    # the avunculate (mother's brother invests, not father → low paternal provision), dampened male skew.
    # [Malinowski 1929; Schneider & Gough 1961; Holden & Mace 2003].
    "matrilineal_horticulturalist": dict(kappa=0.5, mate_choice_strength=2.0, assortative_strength=0.5,
                                         patriline_weight=0.1, lineage_reversion=0.20,
                                         paternal_provision_frac=0.2, sex_division=0.5),
    # Stratified chiefdoms (Polynesia, early states): hereditary stratification, reproductive monopoly +
    # rigid ascribed rank. [Sahlins 1958; Fried 1967 stratified; Kirch 1984; Betzig despotism].
    "stratified_chiefdom": dict(kappa=2.0, mate_choice_strength=4.0, assortative_strength=2.0,
                                patriline_weight=0.8, lineage_reversion=0.04, paternal_provision_frac=0.5,
                                sex_division=1.0),
}


# Leader-coherence Boehm gate (Social-Evolution Stage 1): how much a band's top-status member's authority
# translates into extra group cohesion, by society type. Egalitarian foragers actively LEVEL would-be leaders via
# mockery/desertion/assassination (Boehm 1999 reverse dominance) → weight 0 (the mechanism is INERT there, not
# just weak). Complex foragers show incipient institutionalized rank/leadership in collective action (Hooper,
# Kaplan & Boone 2010; Ames 1994) → a moderate weight. Stratified chiefdoms institutionalize chiefly authority
# (Sahlins 1958; Service 1962) → the full weight. UNANCHORED magnitudes (no measured "how much cohesion" number
# exists) — these are a bracketed 0 / 0.5 / 1.0 ladder for sensitivity sweeps, not a fitted scale.
# Per-resource storability (Testart 1982): grain/cereal & dried fish keep for a lean season; fresh forage & meat
# perish. Used by the resource-dependent storable_fraction (a weighted average over a cell's resource mix). Meat gets
# a partial value (jerky/pemmican preservation exists but is riskier than grain). UNANCHORED ladder — bracketed.
STORABILITY_BY_RESOURCE: dict[str, float] = {
    "grain": 0.85,      # cultivability (cereal/nut agriculture)
    "fish": 0.80,       # aquatic_food (smoked/dried fish — NW Coast salmon)
    "forage": 0.15,     # fresh wild plants (perishable)
    "game": 0.35,       # meat (partial: dried/smoked possible but riskier)
}


LEADER_SOCIETY_WEIGHT: dict[str, float] = {
    "egalitarian_forager": 0.0,
    "complex_forager": 0.5,
    "stratified_chiefdom": 1.0,
}


def leader_society_weight(society: str | None) -> float:
    """Boehm-gate lookup for leader coherence; an unclassified/None band defaults to the EGALITARIAN weight (0.0)
    — the conservative default (no leader effect until a band is positively morphed toward complexity)."""
    return LEADER_SOCIETY_WEIGHT.get(society, 0.0)


# Scalar-stress RELIEF by society type (Social-Evolution Stage 1b, Johnson 1982): the FRACTION of coordination
# cost NOT absorbed by organizational structure. Egalitarian mobile bands have no hierarchy → they retain the
# FULL scalar stress (1.0) → mobile forager bands stay small. Complex foragers' incipient rank + a settled/stored
# base absorb some (0.5); stratified chiefdoms' institutionalized authority absorbs most (0.25) → hierarchy is
# precisely what lets a group grow larger (Johnson's thesis). UNANCHORED ladder — bracketed for sensitivity.
REPULSION_SOCIETY_FACTOR: dict[str, float] = {
    "egalitarian_forager": 1.0,
    "complex_forager": 0.5,
    "stratified_chiefdom": 0.25,
}


def repulsion_society_factor(society: str | None) -> float:
    """Scalar-stress retention by society type; an unclassified/None band defaults to the EGALITARIAN factor (1.0)
    — a mobile band feels the FULL coordination cost until it positively morphs toward hierarchy."""
    return REPULSION_SOCIETY_FACTOR.get(society, 1.0)


# Ascribed-status mate-choice: the Boehm society gate on how much cred (ascribed) enters mate-choice. Egalitarian
# bands LEVEL ascribed status (0 — a lineage name buys no marriage); complex foragers' incipient rank lets it
# matter (0.5); stratified chiefdoms fully value it (1.0) — chiefly marriage / hypergamy. Parallels
# LEADER_SOCIETY_WEIGHT. UNANCHORED ladder — calibrated against the von Rueden 0.13(egalitarian)→0.19(stratified) gradient.
MATE_ASCRIBED_WEIGHT: dict[str, float] = {
    "egalitarian_forager": 0.25,   # non-zero FLOOR: family/kin standing sways marriage even among egalitarians
                                   # (bride-service, parental say, alliance — Chagnon), but SMALL (Hadza/Ju favour
                                   # the achieved/hunting channel — Marlowe). Boehm levels political authority, not
                                   # family marriage reputation. NB largely latent until a stratification RANGE exists.
    "complex_forager": 0.6,        # incipient rank lets ascribed status matter more.
    "stratified_chiefdom": 1.0,    # chiefly marriage / hypergamy — ascribed status fully valued.
}


def mate_ascribed_weight(society: str | None) -> float:
    """Society gate for ascribed(cred) mate-choice; an unclassified/None band = the EGALITARIAN default (the floor):
    a band that hasn't positively morphed is in the egalitarian state, so it gets the small egalitarian floor."""
    return MATE_ASCRIBED_WEIGHT.get(society, MATE_ASCRIBED_WEIGHT["egalitarian_forager"])


def size_repulsion(n: int, gain: float, midpoint: float, width: float, society: str | None) -> float:
    """Johnson 1982 scalar stress as a per-band DISPERSIVE term ∈ [0, gain): a logistic in band size `n` (Alberti
    2014 shape) scaled by `gain` and the society scalar-stress-retention factor. ≈0 for small bands, saturating
    toward `gain·factor` as the band grows past the coordination-cost midpoint. Resource-INDEPENDENT (pure
    coordination cost) — the size-driven counterweight to the assabiyah/leader cohesion terms."""
    if gain <= 0.0:
        return 0.0
    logistic = 1.0 / (1.0 + math.exp(-(n - midpoint) / width))
    return gain * repulsion_society_factor(society) * logistic


def mobility_radius(value: float, cfg) -> int:
    """Productivity-scaled movement STRIDE (Kelly 1995 / Binford 2001: mobility ∝ 1/productivity).

    r = clamp(round(base · (ref / max(value, floor))**exponent), base, r_max).
    Low `value` → long stride (spread out); high `value` → r=base (=1 by default, bit-exact).
    Returns `base` unconditionally when the flag is off. `cfg` is a DemographyConfig (or any object with the
    mobility_* fields).

    `cfg.mobility_pressure_source` selects what `value` MEANS (R-106 Addendum 6):
      - "npp" (default, bit-exact): `value` = static geographic local NPP (§4.8.19 original). ref/floor =
        `mobility_npp_ref`/`mobility_npp_floor`. Calibration PROVISIONAL pending supervisor sign-off.
      - "intake": `value` = the agent's own live intake/requirement EMA (`_intake_ema`, R-106) — density-aware,
        since a crowded cell dilutes it regardless of the cell's nominal fertility. ref/floor =
        `mobility_intake_ref`/`mobility_intake_floor`. Caller is responsible for passing the right `value`."""
    base = cfg.mobility_base_radius
    if not cfg.enable_productivity_mobility:
        return base
    # UNIT GUARD (2026-08-07, tier-4 CTB). The two sources live on scales three orders of magnitude apart —
    # NPP is g/m²/yr in the hundreds, intake is a requirement RATIO around 1 — and the docstring put the
    # burden of matching them on the caller. Both mismatches were SILENT and failed in opposite directions:
    #   source="intake" fed an NPP value  -> ratio ~1/900 -> r pinned to `base`, the mechanism INERT while ON
    #   source="npp"    fed an intake one -> ratio ~900/50 -> r pinned to `max`, every agent at full stride
    #                                        regardless of productivity, i.e. Kelly/Binford exactly inverted
    # ⚠ NOT GUARDABLE FROM THE VALUE, and two attempts to do so both failed against real data:
    #     attempt 1 rejected small values under "npp"    -> broke 4 tests: an arid or near-water cell
    #               genuinely has NPP below 20 g/m²/yr, which is exactly what `mobility_npp_floor` is for
    #     attempt 2 rejected large values under "intake" -> broke 2 tests: a well-fed agent genuinely has an
    #               intake ratio of 27, early in a run when few agents sit on rich land
    # The two scales OVERLAP across their whole useful ranges, so no threshold separates them. The mismatch
    # is real and silent in both directions — `source="intake"` fed NPP pins the stride to `base` (inert while
    # reading ON); `source="npp"` fed an intake ratio pins it to `max` (Kelly/Binford inverted) — but it can
    # only be caught at the CALL SITE, by passing the value the source names. `test_pressure_mobility.py`
    # covers the call sites; `test_tier4_movement_ctb.py` documents the hazard.
    # A guard that fires on legitimate input is worse than none: it gets switched off, and nothing replaces it.
    if getattr(cfg, "mobility_pressure_source", "npp") == "intake":
        ref, floor = cfg.mobility_intake_ref, cfg.mobility_intake_floor
    else:
        ref, floor = cfg.mobility_npp_ref, cfg.mobility_npp_floor
    denom = max(value, floor)
    ratio = ref / denom
    r = base * (ratio ** cfg.mobility_exponent)
    return int(max(base, min(cfg.mobility_max_radius, round(r))))


def footprint_radius(local_npp: float, cfg) -> int:
    """Central-place family FOOTPRINT radius (cells) = the biome-scaled monthly range on the uniform grid.
    Fixed `comove_footprint` unless `comove_footprint_scaled`, in which case k ∝ 1/NPP (reusing the mobility
    scaling shape): k = clamp(round((npp_ref/max(npp,floor))**exp) − 1, 0, footprint_max). At NPP≥ref (forest)
    → 0 (tight camp = 1 cell = the calibrated forest monthly range); sparser biomes → larger camp."""
    if not getattr(cfg, "comove_footprint_scaled", False):
        return cfg.comove_footprint
    denom = max(local_npp, cfg.mobility_npp_floor)
    ratio = cfg.mobility_npp_ref / denom
    k = round(ratio ** cfg.mobility_exponent) - 1
    return int(max(0, min(cfg.comove_footprint_max, k)))


def society_knobs(name: str) -> tuple[float, dict]:
    """Return (kappa → SubstrateConfig.contest_exponent, family-knob dict → DemographyConfig(**base, **knobs))
    for a society preset. Seamless switching: pick a name, splice the knobs into the configs."""
    p = dict(SOCIETY_PRESETS[name])
    return p.pop("kappa"), p


# Lit-anchored MILESTONES for society morphing (the egalitarian→complex→stratified ladder is driven by resource
# STRUCTURE, not biome label): Binford 2001 PACKING threshold ≈ 9.1 persons/100 km² (0.091/km²) — above it
# foragers can't freely move → intensification/territoriality/complexity; Testart 1982 STORAGE/surplus → a
# defendable delayed-return surplus → wealth differentials → heritable inequality; Carneiro 1970 circumscription.
BINFORD_PACKING_PER_KM2 = 0.091


def biome_default_society(biome_code: int | None = None, aquatic_rich: bool = False) -> str:
    """Initial society by a biome's RESOURCE STRUCTURE (NOT a clean biome→type mapping — see §4.5.10). The
    model's terrestrial forager biomes (forest/desert/savanna/grass = dispersed, low-storability resources)
    all default **egalitarian_forager** (Testart/Binford); the ONE clean enabler of forager complexity is a
    dense **storable/aquatic** resource base (NW Coast salmon) → **complex_forager**. Everything richer is
    reached by morphing on CONDITIONS (`society_from_character`), not assigned by biome."""
    return "complex_forager" if aquatic_rich else "egalitarian_forager"


def society_from_character(density_per_km2: float, surplus_frac: float,
                           wealth_gini: float | None = None, gini_min: float | None = None) -> str:
    """Morph hook — map a band's measured CHARACTER (density vs Binford packing; surplus = Testart storage
    enabler) onto the complexity ladder. surplus_frac = mean reserve fraction above subsistence (0..1).
      below packing & no defendable surplus → egalitarian (mobile, leveled);
      packed (≥ Binford) AND large sustained surplus → stratified (hereditary);
      else (packed OR storable surplus) → complex (intensification/ranking).
    Note: this ladder is the storage/packing (complexity) axis only — the patrilineal/matrilineal DESCENT types
    are set by history/biome, not reached by density. And in the current forage-only model the equilibrium
    density (~0.065–0.1/km²) sits AT/below packing, so a band stays egalitarian until a carrying-capacity boost
    (storage/aquatic/agriculture — the deferred surplus mechanic) lifts it past the threshold.

    R-103 INEQUALITY GATE (`gini_min` not None ⇒ ON; None ⇒ bit-exact with the level-only classifier). When on,
    the stratified verdict additionally requires `wealth_gini ≥ gini_min` — a packed, affluent, but EQUAL band is
    complex (affluent-egalitarian), not stratified. Closes the diagnosed decoupling where the stratified LABEL
    ran opposite to measured inequality (a uniformly-rich world read 45% stratified at cred-Gini 0.29)."""
    packed = density_per_km2 >= BINFORD_PACKING_PER_KM2
    if not packed and surplus_frac < 0.5:
        return "egalitarian_forager"
    if packed and surplus_frac >= 0.7:
        if gini_min is not None and (wealth_gini is None or wealth_gini < gini_min):
            return "complex_forager"          # packed + affluent but EQUAL ⇒ not stratified (Testart's missing step)
        return "stratified_chiefdom"
    return "complex_forager"


# Neolithic Demographic Transition — society-dependent birth-spacing (lactational refractory months). Mobile foragers
# space births ~44 mo (Howell !Kung; carrying cost + on-demand nursing) → sedentary/complex/agricultural shorten toward
# ~24 mo (Sellen & Mace 2007 weaning×subsistence; Bocquet-Appel 2011 ~2× birth rate). Values are the REFRACTORY (the
# ~7 mo to conceive at fecundability 0.12 adds on top → effective IBI ≈ refractory + 7). egalitarian keeps the base 30
# (effective ~37, a forager). Only used when `enable_sedentism_fertility` (default OFF).
SEDENTISM_IBI_MONTHS = {
    "egalitarian_forager": 30,   # effective ~37 mo (mobile forager baseline; between !Kung 44 and farming 24)
    "complex_forager":     22,   # effective ~29 mo (sedentary, storage, delayed-return)
    "stratified_chiefdom": 14,   # effective ~21 mo (~1.8× the forager birth rate → the NDT signature)
}


def sedentism_ibi(society: str | None, base: int) -> int:
    """Society-dependent lactational refractory (NDT). Unknown/None → the base (config) value."""
    return SEDENTISM_IBI_MONTHS.get(society, base)


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


def density_mult(density_per_km2: float, delta: float, rho_half: float,
                 rho_ref: float = 0.0) -> float:
    """Density-dependent disease: `1 + δ·ρ/(ρ+ρ_half)`, ρ in **agents/km²** (red-team m-3). Endemic /
    zoonotic — modest (Dunn 1968 / Houldcroft & Underdown 2023), NOT crowd-epidemic. The free lever.

    `rho_ref > 0` divides through by the value at that density, so the multiplier is exactly 1.0 there and
    the term becomes a RELATIVE excess above the reference rather than above an empty world. This is the
    same invariant `risk_mult` and `pathogen_mult` already hold, and the one this function silently broke:
    Siler's a2 was fitted on a population living at a real density, so charging it again at that density
    double-counts. `rho_ref = 0` reproduces the historical unnormalised form exactly (bit-exact default).
    See `DemographyConfig.enable_density_reference` for the measurement that motivated it.
    """
    raw = 1.0 + delta * density_per_km2 / (density_per_km2 + rho_half)
    if rho_ref <= 0.0:
        return raw
    return raw / (1.0 + delta * rho_ref / (rho_ref + rho_half))


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
