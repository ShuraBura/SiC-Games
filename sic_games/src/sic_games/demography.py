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
    enable_infanticide: bool = False    # [UNIMPLEMENTED STUB — no logic reads this.] Baseline infanticide is ALREADY
    # folded into the Siler infant-mortality curve (fit to observed HG infant deaths — "infanticide KEPT"). An explicit
    # mechanism would only add CONDITIONAL infanticide (birth-spacing enforcement / sex-selective); the resource-stress
    # channel overlaps enable_energetic_fertility, sex-selection is a separate future scoping. Documented stub, not built.
    # economy-fix (Tier-0): births scale with maternal reserve, capping the population BEFORE reserves
    # drain to the starvation floor → realistic equilibrium reserve (red-team 2b prerequisite)
    enable_energetic_fertility: bool = False
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
    soil_regrow_per_yr: float = Field(0.06, ge=0.0)         # slow fallow soil recovery (~1/0.06 ≈ 17 yr; Conklin/Boserup swidden) [PROVISIONAL]
    soil_deplete_frac: float = Field(0.6, ge=0.0)           # per-YEAR soil exhaustion at pressure=1 (PROGRESSIVE while farmed — no equilibrium; swidden) [PROVISIONAL]
    soil_carry_per_cell: float = Field(8.0, ge=0.1)         # persons/catchment-cell that = pressure 1.0 (farming carrying density) [PROVISIONAL]
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
    # F.2 band risk-dilution (safety-in-numbers on the EXOGENOUS biome hazard). The lit biome accident/incident
    # rate (the terrain-risk channel, anchored on people LIVING IN BANDS — Hill/Hurtado/Walker 2007) is the
    # band-level baseline; a SUB-band group loses that mitigation → elevated a2 mortality, SCALED by the biome's
    # own incident rate (being alone is dangerous in a risky biome, ~harmless in a safe one — Hamilton 1971
    # selfish-herd / domain-of-danger). A full band (size ≥ band_risk_size, summed over bonded_mate_radius)
    # faces the anchored baseline (factor → 1, so the validated biome-mortality calibration is unchanged). With
    # density-disease (which RISES with crowding) this was hypothesized to give an emergent OPTIMAL band size.
    # ⚠ CAVEAT (F.2 prototype, run_3i, 2026-06-29 — KEEP OFF): it does NOT. Mortality doesn't cause aggregation
    # (that is the E.1 movement safety-drive's job); a loner-mortality penalty just CULLS the population, which
    # lowers density → smaller bands → more loners → more penalty = a DEATH SPIRAL, not a stabilizing optimum
    # (penalty 0→6: pop 281→64, mean band 56→5). Risk-dilution is properly expressed in MOVEMENT (E.1), and
    # banding already has fitness teeth via the F.1 mate-gate. Left in (default OFF) for future experiments only.
    enable_band_risk: bool = False
    band_risk_penalty: float = Field(0.0, ge=0.0)   # max extra a2 multiplier for a LONER in a mean-risk biome
    band_risk_size: int = Field(25, ge=1)           # band size at which the biome risk is fully mitigated (Wobst ~25)
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
    divorce_rate: float = Field(0.0, ge=0.0, le=1.0)      # per-step bond dissolution prob (0 = lifelong unless widowed)
    family_maturity_months: int = Field(180, ge=0)        # child detaches from the family unit at this age (~15 yr)
    # F.3a MODEST POLYGYNY (von Rueden & Jaeggi 2016: polygyny is the MAIN status→RS amplifier; ~4-11% of forager
    # marriages). polygyny_rate>0: when a female pairs she may also consider ALREADY-MARRIED males (each with prob
    # polygyny_rate), prowess-weighted (mate_choice_strength) — so high-status males accumulate up to `max_wives`
    # wives and some low-status males are bachelors → the status→RS skew (lost under strict monogamy) returns.
    # A female has ONE husband (`_partner`); a male's wives = `_wives`. Polygynous (>1 wife) husbands move as
    # roots (wives are mother-anchored cores in his band; the birth gate is band-level). 0 = strict monogamy.
    polygyny_rate: float = Field(0.0, ge=0.0, le=1.0)
    max_wives: int = Field(1, ge=1)                       # cap on wives per male (1 = monogamy even if rate>0)
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
    # EMERGENT BAND SIZE (blueprint …_EmergentBandSize): the fission-threshold FLOOR is not the hardcoded
    # band_base_tolerable=25 but the RISK-POOLING optimum g* = (CV/cv_safe)² — the group needed to pool the local
    # foraging-return variance (per-biome CV from the Return-Rate Tables) down to a safe residual cv_safe. Higher-CV
    # biomes (hunting/wetland) → bigger emergent bands; low-CV (forest gathering) → smaller. Predicts mean ~25 AND
    # environment-dependence (Marlowe 25–50). Clamped [band_size_min, band_split_size]. Default OFF ⇒ hardcoded 25.
    enable_emergent_band_size: bool = False
    cv_safe: float = Field(0.14, gt=0.0)                 # residual per-capita CV the band pools variance down to (sets the scale; ~25 at CV≈0.7) [UNANCHORED — bracket]
    # v2 SOCIAL FLOOR: band size = max(risk-pooling optimum, band_size_min). The ~25 is OVERDETERMINED — risk-pooling
    # gives the environmental gradient (variance→size), but the FLOOR comes from the non-foraging drivers (min viable
    # co-residential + mating + demographic-buffering unit). band_size_min anchored to Hill 2011 observed minimum
    # co-residential group (~15; groups range ~15–50, mean ~25–30). cv_min corrects data-gap biomes (grass/mountain
    # use 10%-default SD → unrealistically low CV; real foraging returns have CV ≳0.4, Kaplan/Hill).
    band_size_min: int = Field(15, ge=1)                 # min viable co-residential/mating/demographic unit [LIT-anchored, Hill 2011]
    cv_min: float = Field(0.4, ge=0.0)                   # floor on the per-biome return CV (corrects 10%-default data gaps; foraging is never CV≈0.1)
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
    enable_size_repulsion: bool = False
    repulsion_gain: float = Field(0.0, ge=0.0)           # max repulsion (subtracted from cohesion_frac); UNANCHORED
    repulsion_midpoint: float = Field(25.0, gt=0.0)      # band size at half-max repulsion (≈ Wobst-minimal band)
    repulsion_width: float = Field(6.0, gt=0.0)          # logistic steepness in band-size units (Alberti shape ~6.7)
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
    village_fission_threshold: int = Field(150, ge=10)        # village size that triggers fission — Bandy open-landscape ~150 → ~277 circumscribed; Alberti N≈127–158; Yanomamö ~200 [PROVISIONAL, from Bandy 2004]
    village_bud_min_faction: float = Field(0.25, ge=0.0, le=1.0)  # the rival (2nd) lineage bloc must be ≥ this fraction of the village to carry a fission (else too leader-dominated to split)
    village_bud_search_radius: int = Field(8, ge=1)           # cells searched for an available daughter site; beyond it ⇒ circumscribed (no bud → hierarchy). ~a day's relocation range
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
    enable_productivity_mobility: bool = False
    mobility_base_radius: int = Field(1, ge=1)               # stride at/above npp_ref
    mobility_max_radius: int = Field(6, ge=1)                # cap on stride (bounds cost + jump-over risk); PROVISIONAL
    mobility_npp_ref: float = Field(900.0, gt=0.0)           # forager-median NPP g/m²/yr (Tallavaara); r=base at/above; PROVISIONAL
    mobility_npp_floor: float = Field(50.0, gt=0.0)          # denom floor so hyper-arid cells don't → ∞ range; PROVISIONAL
    mobility_exponent: float = Field(1.0, ge=0.0)            # Kelly/Binford slope; 1.0 = strict ∝1/NPP; PROVISIONAL (bracket)
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


def mobility_radius(local_npp: float, cfg) -> int:
    """Productivity-scaled movement STRIDE (Kelly 1995 / Binford 2001: mobility ∝ 1/productivity).

    r = clamp(round(base · (npp_ref / max(local_npp, npp_floor))**exponent), base, r_max).
    Low local NPP → long stride (spread over sparse land); high NPP → r=base (=1 by default, bit-exact).
    Returns `base` unconditionally when the flag is off. `cfg` is a DemographyConfig (or any object with the
    mobility_* fields). Calibration (ref/exp/max) PROVISIONAL pending supervisor sign-off."""
    base = cfg.mobility_base_radius
    if not cfg.enable_productivity_mobility:
        return base
    denom = max(local_npp, cfg.mobility_npp_floor)
    ratio = cfg.mobility_npp_ref / denom
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


def society_from_character(density_per_km2: float, surplus_frac: float) -> str:
    """Morph hook — map a band's measured CHARACTER (density vs Binford packing; surplus = Testart storage
    enabler) onto the complexity ladder. surplus_frac = mean reserve fraction above subsistence (0..1).
      below packing & no defendable surplus → egalitarian (mobile, leveled);
      packed (≥ Binford) AND large sustained surplus → stratified (hereditary);
      else (packed OR storable surplus) → complex (intensification/ranking).
    Note: this ladder is the storage/packing (complexity) axis only — the patrilineal/matrilineal DESCENT types
    are set by history/biome, not reached by density. And in the current forage-only model the equilibrium
    density (~0.065–0.1/km²) sits AT/below packing, so a band stays egalitarian until a carrying-capacity boost
    (storage/aquatic/agriculture — the deferred surplus mechanic) lifts it past the threshold."""
    packed = density_per_km2 >= BINFORD_PACKING_PER_KM2
    if not packed and surplus_frac < 0.5:
        return "egalitarian_forager"
    if packed and surplus_frac >= 0.7:
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
