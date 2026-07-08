# SiC Games — Emergent Band Size Blueprint (v1.0, 2026-07-08)

**Goal.** Make the ~25 co-residential band size **emerge** from grounded forces instead of being hardcoded
(`band_base_tolerable=25`, `repulsion_midpoint=25`, tuned GRP scales). Success = band size is a *prediction* (~25 mean,
Birdsell/Wobst/Hill 2011) that also **varies with environment** (25–50, Marlowe/Kelly), not an input.

## The physics: band size = the risk-pooling optimum
The ~25 band is overdetermined; the *dominant, quantifiable* driver is **risk-pooling of foraging-return variance**
(Winterhalder 1986; Kaplan & Hill). If returns were deterministic (σ=0) there is NO benefit to grouping — only
competition — so band size → 1. The entire grouping incentive is **variance reduction via sharing.**

- Individual period-return: mean μ, std σ (per biome — already in `FORAGE_KCAL_STD` / `GAME_KCAL_STD`; CV 0.23 forest …
  2.35 wetland). CV = σ/μ.
- A sharing group of `g` pools returns → per-capita ~ (μ_g, σ/√g), where **μ_g falls with g** (per-capita resource
  competition, the existing `S/n` + finite-stock) and **σ/√g falls with g** (pooling).
- Starvation risk `p_starve(g) = P(per-capita pooled < BURN) ≈ Φ((BURN − μ_g)/(σ/√g))`.
- **Optimal g minimises p_starve**: pooling (↓variance) vs competition (↓mean). The balance is the band size, and it
  is a PREDICTION set by the return CV, the subsistence threshold, and the local resource — not a parameter.
  High-CV biomes (wetland, hunting-heavy) → bigger optimal bands (more to pool); low-CV (forest gathering) → smaller.

## What replaces what
- **`group_safety`** (currently `ypc *= 1 + s_max·(1−e^{−g/g_s})`, s_max=8/g_s=15 — an ad-hoc yield multiplier) →
  a **risk-reduction term derived from σ (the biome return std) and BURN**: the marginal survival value of lowering
  `p_starve` by adding a co-forager. No free `s_max`/`g_s`; the scale comes from σ/μ.
- **`band_base_tolerable` / `repulsion_midpoint` (the hardcoded 25)** → removed; band size is the emergent argmax of
  {risk-pooling − competition − scalar stress}.
- **`size_repulsion` (scalar stress)** stays as the upper-bound coordination cost but should be grounded in Johnson's
  n² pairwise cost (magnitude bracketed) rather than a pinned midpoint — the fission ceiling then also emerges.
- **`group_mate` (mate-access)** is a SEPARATE grouping benefit (min viable mating access) → belongs to the connubium
  scale (~500, Wobst), not the ~25 band; keep distinct.

## Inputs (all already lit-anchored)
- Per-biome return (μ, σ): `SiC_Games_Resource_Return_Rate_Table.md` / `Game_Return_Rate_Table.md` (FORAGE/GAME_KCAL
  TARGETS+STD) — the CV that drives the pooling incentive.
- Subsistence BURN (2500 kcal/day). Resource μ_g from the finite-stock field (Tallavaara K, R-58).
- Scalar-stress shape: Johnson 1982 / Alberti 2014 (already `size_repulsion`).

## Validation
- **Mean band size ≈ 25** emerges across biomes (Birdsell/Wobst/Hill), single most important check.
- **Environment-dependence:** band size rises with return CV / resource richness (Marlowe/Kelly 25–50) — a testable
  PREDICTION the fixed-25 model cannot make. Sweep biomes; correlate emergent band size with CV.
- Downstream: status→RS, eq-pop, packing still sane (this changes a validated mechanism → full re-validation).

## Effort / risk
Medium. It's a targeted rewrite of the `group_safety` term (variance-based) + un-pinning the two hardcoded 25s, then
re-validation. Risk: touches the validated band/status machinery → do on a branch, expect the headline numbers to move,
re-validate there. Note: on this world the mean NPP is arid-low (Tallavaara ~5/cell) — band size may emerge *below* 25
in poor biomes and above in rich, which is the *correct* environment-dependence, not a failure.

## Relation to the rest
Sits ALONGSIDE the perf re-architecture (SiC_Games_ReArchitecture_Blueprint.md) as the two real next efforts:
emergent-sizes = the *science* correctness; SoA/numba = the *scale* to run the Turchin campaign. Independent; can proceed
in parallel (emergent-sizes validated at a few thousand agents).

## v1 IMPLEMENTED + VALIDATED (2026-07-08, branch `emergent-band-size`)
`enable_emergent_band_size` (default OFF, bit-exact): the fission-threshold floor per band = `clamp((mean-cell-CV/cv_safe)², band_size_min, band_split_size)`, CV from `_return_cv_field()` (per-biome forage+game σ/μ). cv_safe=0.14, band_size_min=5.

**Result — PARTIAL SUCCESS (environment-dependence YES; absolute ~25 NO).** In-sim (800 agents, 200 steps): emergent band size **tracks the biome return variance** — median **8** on low-variance flat/temperate (grass, CV~0.08) vs **26** on higher-variance flat/tropical. That environmental *variation* is the goal and a testable prediction the fixed-25 cannot make. BUT it **under-predicts the ~25 floor in low-variance environments** (grass→~8): pure risk-pooling says "low foraging variance → little to pool → small band," missing the OTHER overdetermining drivers of ~25 (mating/connubium minimum, kin, information). Also: the quadratic `(CV/cv_safe)²` is over-steep (bimodal 5/45 across biomes), and grass/mountain variances are 10%-DEFAULT placeholders (no lit spread) → artificially deflated CV.

**Refinements needed for absolute ~25 (v2):** (1) add a GROUNDED social/mating floor (min viable exogamy/info unit) so low-variance environments still hold ~25 — band = max(risk-pooling optimum, social floor); (2) fill the per-biome return-variance data gaps (grass/mountain lack lit SD); (3) consider a gentler functional form + variance-tempering (storage buffers temporal variance, diet diversity lowers effective CV). The number is genuinely overdetermined (blueprint premise) — risk-pooling is ONE term, correctly delivering the environmental gradient; the floor is a second term. **v1 kept opt-in as the validated variation-driver.**

*Blueprint 2026-07-08. Implementation tracked in RESULTS as it lands.*
