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

## v2 DONE (2026-07-08) — social floor + CV-gap fix → band emerges near ~25
Added: (1) **social floor** `band_size_min = 15` (Hill 2011 min observed co-residential group — the non-foraging drivers: mating/kin/demographic buffering); band size = **max(risk-pooling optimum, floor)**. (2) **CV floor** `cv_min = 0.4` (data-gap fix — grass/mountain 10%-default SD is unrealistically low; foraging returns are never CV≈0.1, Kaplan/Hill).

**Result (800 agents, 3 climates):** median band **19–22** (was v1's 8–26 bimodal; the low-variance under-prediction 8→19 is fixed), within the empirical 15–50 range, near the ~25 mean, and EMERGENT (floor + variance) not pinned. Structure: the **median tracks the lit-anchored floor** (~15, most cells modest-variance), while size **rises with local return variance in the tail** (big bands 45–82 in high-variance patches) — `cv_safe` moves the tail, `band_size_min` the floor. Deliberately NOT cranking the floor to 20 to force exactly 25 (that re-hardcodes). Median sits slightly below 25 because the flat test worlds are low-variance; richer/more-variable environments push it up. Default OFF, bit-exact. **Verdict: band size is now emergent (grounded floor + variance-driven variation), a real replacement for the hardcoded 25.**

## v3 DONE (2026-07-16, branch `band-size-cv`; RESULTS **R-72**) — v2's verdict RETRACTED

**v2's "band size is now emergent" verdict was WRONG.** Auditing before enabling the flag showed the mechanism
could not work. v1's own result section had already named two of the three causes ("the quadratic is over-steep
(bimodal 5/45)"; "grass/mountain variances are 10%-DEFAULT placeholders") and listed the fixes as v2 to-dos —
**v2 did neither**, adding the `band_size_min` floor and the `cv_min` band-aid, which patch the *symptom*. v3 is
that deferred work, plus a third cause nobody had spotted:

1. **Category error in the REUSE.** `FORAGE/GAME_KCAL_STD` are **SPATIAL** cross-cell spreads (they feed the
   lognormal cell-value draw, Resource table §1.5); the risk-pooling law needs **TEMPORAL** day-to-day variance.
   Sharing cannot smooth a spread across habitat patches. The §2/§3 extraction is fine — the reuse was not.
   Which side of the clamp a biome hit was set by which *kind* of statistic its source happened to report.
2. **The blueprint's own instruction was never carried out.** This document says remove `band_base_tolerable`
   **and `repulsion_midpoint`** (the two hardcoded 25s). v1/v2 removed neither. `repulsion_midpoint=25` is the
   term that ACTUALLY sets band size — so **R-64's "band ≈ 24" came out at 24 because it was put in at 25.**
3. **g\* was a ceiling, not a force** — measured corr(g\*, band size) = **−0.22**. A permission to be big cannot
   pull a band together, so fixing the data alone would have changed nothing.

**v3:** new temporal CV layer (`terrain.HUNT_CV=2.11` / `GATHER_CV=0.70` / `RETURN_CV`, all measured — see
Resource table §4); **linear** `g*=CV/cv_safe`, no clamps (the square is a stopping rule with no cost side, hence
unbounded, hence the clamps, hence saturation; linear falls out of benefit-vs-cost ⇒ n\* ∝ CV); and
**`repulsion_midpoint` per-band = g\*(CV)** so the CV drives the cost side. Deletes `band_size_min`, `cv_min`,
both 25s. **Falsified en route:** hunting CV is biome-INVARIANT (10 societies, forest alone spans 1.53–4.64), so
the entire gradient must come from the diet mix (Cordain MEAT_FRAC) — a per-biome hunting CV is not supportable.

**Result — HONEST.** Saturation gone (100% interior, was 0–59%); **causal** (same world+seed, sweeping cv_safe:
med band 33→22 as g\* 43→17 — v1/v2 could not do this); mean lands on Hill 2011's 25–30 (med 29) with the 2.0×
CV spread a *free* prediction against Marlowe's 2×. **BUT the environmental gradient is weak**: paired biome
battery (20 worlds, productivity controlled) gives corr(g\*, ON−OFF delta) = **+0.335, n=18, n.s.**, with grass
and forest inverted. Cause: `repulsion_gain=0.3` (UNANCHORED) is too small for the CV's effect on the cost term
to survive against assabiyah (~0.83).

## v3 FINAL VERDICT (2026-07-16) — the environment-dependence FAILS; the blueprint's premise does not survive

`repulsion_gain` was anchored as this document's last instruction demanded. **Alberti 2014** fits
`logit P(critical scalar stress | n) = −18.636 + 0.147·n` ⇒ **gain = 1.0** (his logistic IS a probability; the
0.3 in use is an arbitrary attenuation) and **width = 1/b1 = 6.80**. *Caveat:* his midpoint −b0/b1 = **126.9** is
a **community** — the VILLAGE rung — not the ~25 band, so the band-scale slope extrapolates below his data.

**It did not help, and three explanations died in a row (RESULTS R-72):**

| test | paired corr(g\*, ON−OFF delta) |
|---|---|
| 1 seed/world, n=18 | +0.335 (n.s.) |
| **anchored gain=1.0** | +0.374 (n.s.) — *"cost too weak" refuted* |
| **4 seeds/world, n=20** | **+0.165 (n.s.) — the gradient VANISHES** |

Seeding also collapses the OFF confound reference (+0.382 → **−0.001**), so the 1-seed signal was noise on both
arms. "The fission threshold never binds" was refuted too (9/27 bands sit at/above their g\* base).

**The premise fails for a structural reason.** This document assumed return-CV varies enough across environments
to set band size. It does not: hunting CV is **biome-INVARIANT** (measured — 10 societies; forest alone spans
1.53–4.64), so the whole gradient must ride on Cordain's meat fraction, which spans only 0.34–0.66 ⇒ CV 0.85–1.41
⇒ **a 1.66× g\* range**. Band size is also driven by productivity, assabiyah, terrain and mating, which swamp a
1.6× signal. **Risk-pooling predicts a 2× gradient; inside the full model it is undetectable.**

**Kept as default-OFF and NOT recommended for adoption:** it replaces a hardcoded 25 with a *measured* mean
(genuine progress: R-72's temporal CV, linear law, and the un-pinning of both 25s all stand) but buys no
environment-dependence to pay for its complexity. **The one live route:** our six biomes have no high-meat
environment. An arctic/tundra diet (Cordain m≈0.9) gives CV 1.80 ⇒ g\*≈49 — the top of Marlowe's range. Widening
the biome set is the only way the predicted 2× has room to appear; without it, this blueprint's goal is
unreachable by construction.

*Blueprint 2026-07-08. Implementation tracked in RESULTS as it lands.*
