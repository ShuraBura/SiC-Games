# SiC Games — Targets (TARGETS.md)

**Purpose:** The home for **emergent behaviours the project is shooting for** — qualitative
phenomenology we hope the model produces — that are *not yet* formal predictions. This is the
deliberate counterpart to HYPOTHESES.md: a place for generative ideas to live honestly,
without masquerading as pre-registered predictions.
**Maintainer:** Supervisor curates; Claude Code maintains.
**Created:** 2026-06-05.
**Not here:** *quantitative* empirical benchmarks (village size, density, catchment radius, agglomeration α — the values the model is calibrated/validated against, with extraction methods) live in **`MODEL_SPEC.md` §4.8.21** (the methods home). This doc is for *qualitative emergent aspirations* only.

---

## The line between a TARGET and a HYPOTHESIS (charter §5)

- A **TARGET** is an aspiration — "we're shooting for X to emerge." Qualitative, not tied to
  a specific scheduled run, not falsifiable-as-written.
- A **HYPOTHESIS** is a pre-registration — a falsifiable claim with a test spec (which run,
  which statistic, which threshold) and a pre-committed interpretation, dated *before* the run.

**Graduation rule:** a target becomes a hypothesis the moment it acquires a falsification
spec. At that point it is **moved** (not copied) into HYPOTHESES.md with its registration
date, and its entry here is replaced by a pointer. **A target is never marked
"supported/confirmed"** — only a hypothesis can resolve. The test of whether something is
ready to graduate: *could a run plausibly come out against it and update you?* If not, it
stays a target (or it's really a finding → RESULTS, or an abandoned idea → DEAD_ENDS).

---

## T-1 — Microscale secular cycles from status-coupled decision noise

**Status:** TARGET (highest interest). **Origin:** supervisor, 2026-06-05.

**Aspiration:** the C status–σ coupling (`σ_i = σ_base + κ·tanh(𝒞_i/C*)`, MECHANISMS / Cred)
— high-Cred agents make noisier decisions — produces **boom/bust cyclic dynamics at the
microscale**: within family lineages or local clusters ("tribes"), Cred concentrates →
decision noise rises in the high-Cred set → over-exploration / mis-foraging → local collapse
→ Cred redistributes → recovery. A Turchin-style secular cycle, but emergent at the
lineage/cluster scale rather than imposed at the population scale.

**Why this is a real target and not a rationalization:** it is genuinely falsifiable in
principle — a run could show Cred and decision-noise *don't* couple to any cyclic structure,
or that local dynamics are monotonic rather than oscillatory. That asymmetry (it could embarrass
us) is exactly what makes it worth chasing.

**What it needs to graduate to a HYPOTHESIS:**
- A unit of analysis: lineage (parent-child tree) and/or local cluster (cell-neighbourhood).
- A periodicity statistic: autocorrelation / spectral peak / peak-trough counting on a
  per-unit time series of {cluster size, local mean Cred, Cred concentration (Gini or top-share)}.
- A threshold distinguishing "cyclic" from "noise" and from "monotonic," and seeds (≥5+).
- A pre-committed interpretation of cyclic / acyclic / monotonic outcomes.
- *Watch:* this is a measurement target, not a license to add a group-level cycle mechanism
  (cf. H-EMERGE-1's TMTS guard — emergence must come from existing mechanisms).

---

## T-2 — C/Si home-range orthogonality (movement decomposition)

**Status:** TARGET (deprioritized). **Origin:** routed from the former H-ORTHOGONALITY
pre-registration, 2026-06-05. See DEAD_ENDS for the deprioritization note.

**Aspiration:** C and Si movement decomposes into different mixtures of foraging-pull (sugar
gradient) vs social-pull (ψ proximity) — C weighted toward social, Si toward foraging — as a
*difference-set*, not merely a scale difference.

**Why it's a target, not a hypothesis:** it is close to **implied by construction** — the C2
classification (MECHANISMS: ψ proximity-to-agents for C vs proximity-to-foraging-spots for Si)
already builds the asymmetry in, so a "confirmation" would largely restate the design rather
than risk it. Low capacity to embarrass us. Worth *measuring* if the diagnostic gets built,
but not a live bet.

**What it needs to graduate:** the OWE-13 movement-decomposition diagnostic built and
validated; matched C/Si runs at a density where both survive ≥2000 steps post-transient; and
a pre-committed magnitude threshold for "orthogonal" vs "parallel-but-scaled." If/when OWE-13
is scheduled, this graduates with the test spec already drafted in the original pre-reg.

---

## T-3 — Instinct-debt mortality (culturally-mandated exploration cost)

**Status:** TARGET (contingent, downstream of T-2). **Origin:** routed from the former
H-instinct-debt pre-registration, 2026-06-05.

**Aspiration:** the social-pull term draws C agents away from optimal foraging under stress,
so in deep troughs C agents die at *higher* wealth than starvation would require — a bimodal
terminal-wealth-at-death distribution (one mode near zero = true starvation; one mode at
2–5× metabolism = "instinct-debt death") — absent when the ψ social term is disabled.

**Why it's a (good) target:** more specific and more falsifiable than T-2 — the bimodality
prediction could clearly fail. But it is doubly gated: it needs OWE-13, and it presupposes T-2
holds (no orthogonality ⇒ no pathway). No run is coming, so it waits.

**What it needs to graduate:** OWE-13 built; T-2 measured and holding; terminal-wealth-at-death
histogram logged per strategy per trough phase; a matched C control with the ψ social term
disabled; ≥5 seeds; pre-committed interpretation of bimodal vs unimodal.

---

## T-4 — Emergent nutritional child mortality reproduces the Aché schedule

**Status:** TARGET (downstream of the Resource-Ecology stage). **Origin:** supervisor, 2026-06-19.

**Aspiration:** instead of the all-cause Aché Siler encoding child mortality *by construction*,
**decouple the nutritional component**: keep an exogenous non-nutritional residual (accidents,
violence, non-nutritional infection — from Hill & Hurtado cause-of-death) in the schedule, and let
the **nutritional** part of child mortality EMERGE from the mechanisms — children's low per-class
reserves × scarcity (seasonality / depletion) × parental provisioning load. The emergent nutritional
child mortality + the exogenous residual should then **reproduce the empirical Aché child-mortality
schedule**.

**Why this is a real target and not a rationalization:** it is genuinely falsifiable — the emergent
child mortality could come out too high, too low, or the wrong age-shape, and that would update us on
what the nutrition/provisioning model is missing. It converts "the model reproduces Aché child
mortality" from a **tautology** (painted-in by the all-cause Siler) into a real test of the mechanisms
— the project's "emergent, not painted-in" ideal applied to mortality — and it dissolves the M-3-style
double-count (nutrition is the part *removed* from the Siler, not restated on top of it).

**What it needs to graduate to a HYPOTHESIS:**
- The Resource-Ecology stage built and trustworthy: nutritional variance (seasonality + depletion),
  per-class reserves (children's low buffer), and family provisioning (JV-1 / MR-2).
- A decomposition of Aché child mortality into nutritional vs non-nutritional from Hill & Hurtado
  cause-of-death (the non-nutritional residual stays in the Siler).
- An l(x) / q(x) comparison over child ages with a tolerance band, ≥5 seeds, and a pre-committed
  interpretation of match / too-high / too-low / wrong-shape.
- *Watch (TMTS guard):* the emergent mortality must come from the existing reserve/scarcity/provisioning
  mechanisms, not a new child-mortality knob.

**⚑ [2026-06-20 — ATTEMPTED & DEFERRED — THE MARK FOR LATER]** First attempt at the *fine* (graded
nutrition→disease) version, via **S0** (lagged body-condition EMA so synergy reads sustained nutritional
state, not the bang-bang reserve) + **S1** (child-priority shortfall-sharing). **Result: CORRECT-BUT-INERT**
(red-team `a1f44d9c`, RESULTS R-11). The code is right; it can't bite because provisioning **tops children
to their cap** → survivors sit at condition ≈1.0, and the only under-cap children hit the starvation floor
in ~1 step (R-10 bang-bang) before the EMA moves. The self-regulation attractor (R-5…R-8) defeats it: the
*surviving* mothers are by construction the ones who can cover their kids, so children rarely dwell lean.
**What the fine version needs to graduate (the deferred work):** a TWO-part fix — (a) change provisioning
*target* from cap to maintenance/burn (`phase1_model.py:338`) so a drawn-down child is NOT refilled and
dwells at partial reserve; **AND** (b) slow the child reserve dynamics (widen the cap-to-floor span beyond
~1.3 months) OR add **stochastic foraging returns** so even adequate mothers occasionally fail — i.e.
re-open the R-7 "source-of-variance" problem one level down. Red-team predicts (a) alone stays flat. This is
a dedicated research subproject, NOT a quick add. **Banked, not abandoned:** `enable_condition` /
`condition_alpha` (S0) are kept as **opt-in, off-by-default** flags for this future effort.
**The COARSE version IS in use now** (RESULTS R-11): the model's two existing cause buckets —
**starvation (floor)** vs **Siler baseline `deaths_senesc` (disease+infanticide+accident)** — give a
disease-dominated / low-nutritional child split that roughly matches the Aché coarse benchmark, with **S1
(kept ON)** driving child nutritional death toward the data's ≈0. The Biome-Mortality stage validates this
coarse split as a byproduct; the fine mechanistic synergy is what remains here as T-4.

---

*End of TARGETS — seeded 2026-06-05. Graduate a target by moving it to HYPOTHESES with a test
spec; never mark a target "confirmed."*

---

## T-5 - Wealth inequality matches BHM 2009 by SOCIETY TYPE (not just in the forager case)

**Status:** ACTIVE VALIDATION TARGET (forager arm already met). **Origin:** R-84b, 2026-07-18.
**Source:** Borgerhoff Mulder et al. 2009 (*Science* 326:682) Table 2, `[VERIFIED]`.

The alpha-weighted composite Gini, computed on the model's three status facets with BHM's own importance weights
(embodied=`prowess`, relational=`cred`, material=`material`):

| System | alpha (emb, rel, mat) | Target Gini | Model status |
|---|---|---|---|
| Hunter-gatherer | 0.46 / 0.39 / 0.15 | **0.25 +/- 0.04** | **MET** - 0.258 at `leader_share_frac`=0.20 |
| Horticultural | 0.53 / 0.26 / 0.21 | 0.27 | not yet attempted |
| Pastoral | 0.26 / 0.14 / 0.61 | 0.42 | not yet attempted |
| Agricultural | 0.27 / 0.14 / 0.59 | **0.48** | **NOT MET** - best 0.435 (leveling off, share 0.50) |

**Why it is a real target:** the forager arm is met almost trivially (the composite barely moves with the levy,
because material is only 15% of forager weight), so the *discriminating* test is the AGRICULTURAL arm - reaching
0.48 requires the model to produce material heritability, not just material accumulation. BHM's beta for material
goes 0.17 (forager) -> 0.55-0.67 (agricultural); **the model currently has no material inheritance at all**.

**REFRAMED 2026-07-18 after the Flannery digest.** Do NOT close this gap by adding material heritability on its
own. Flannery ch. 10: *"if feasting were all it took to produce hereditary inequality, there would have been no
achievement-based societies left for anthropologists to study"* - competitive feasting *"produced individual Big
Men who had no way of bequeathing renown to their offspring."* **The model is currently behaving CORRECTLY as an
achievement-based society** (leaders 3.68x ahead, father-was-leader only 53-69%, no hereditary transmission), so
the agricultural shortfall is most likely a MISSING MECHANISM rather than a calibration error. Friedman's
endogenous account puts that mechanism in LEGITIMACY - achieved success reinterpreted as descent from higher
spirits - not in accumulation. See MECHANISM_CHARTER §9 and DEFERRED_MECHANICS DM-F1. Forcing the Gini with a
material-inheritance coefficient would hit the number while getting the cause wrong.

## T-6 - Big-man status is inherited ~75% of the time WITHOUT inheriting the office

**Status:** ACTIVE VALIDATION TARGET (partially met). **Origin:** R-84, 2026-07-18.
**Source:** Hayden 1995 `[VERIFIED]`: *"About 75% of New Guinea Entrepreneur Big Men had fathers that were also
Big Men"* - transmitted via moka partners and wives, **not** the position.

**Model status: MET on Hayden's metric, VALIDATED 2026-07-20 (R-86v) - and the mechanism's role is narrower
than R-86 claimed.** Age-matched measured value 0.769 vs Hayden's 0.75, sitting far in the right tail of a
permutation null (z = 3.1-4.9). The 76% is a genuine signal, not a base-rate artifact (null base rate 0.44).

**Three caveats that must travel with this number:**
1. **The mechanism supplies CONCENTRATION, not TRANSMISSION.** Age-matched, legitimacy ON and OFF give the SAME
   lift over null (1.43 vs 1.43). Legitimacy raises the raw fraction (0.769 vs 0.627) by raising the base rate
   in step (0.536 vs 0.439) - more of a favoured lineage's members hold office. The father->son association is
   unchanged and was already supplied by `cred` inheritance.
2. **Hayden's base rate is unknown**, so his LIFT cannot be computed and the raw-fraction match cannot
   distinguish concentration from transmission. If big-man status was rare (~10% of men), his 75% implies a
   lift near 7 against our 1.43. **Finding that base rate is the highest-value open literature question here.**
3. Measured in a regime where `ascribed_frac_pop` reaches 0.70-0.85 (the ratchet saturates); re-check once
   delegitimation bounds it.
**Why the gap is informative:** Hayden's actual channel is RELATIONAL capital (exchange partnerships), which the
model does not transmit - `cred` is a scalar, not a partner network. Closing this gap most likely means making
relational capital heritable, which is also the alpha=0.39 cell BHM says matters most for foragers after embodied.
**Graduation:** becomes a HYPOTHESIS once relational capital is a transmissible object rather than a scalar.

## T-7 - Hierarchy tracks resource STRUCTURE, not productivity

**Status:** ACTIVE VALIDATION TARGET. **Origin:** 2026-07-18 (filed with Smith & Codding).
**Source:** Smith & Codding 2021 (*PNAS* 118:e2016134118) `[VERIFIED]`, n=89 Pacific-coast HG societies.

| Predictor of hierarchy | Effect size |
|---|---|
| Resource Index (structure) | **0.37** |
| Fishing-site OWNERSHIP | 0.13 (pSEM direct b_std 0.96, P=0.043) |
| **NPP productivity** | **0.04** |
| Offensive raiding | -0.01 |

with **r = 0.881 (n=89)** between the Hierarchy Index and Resource Index.

**The model must reproduce the ORDERING, not just the existence of stratification:** varying raw productivity
should move stratification hardly at all, while varying resource structure/defensibility should move it a lot.
**This independently corroborates R-65's correction** ("storability, not NPP, is the axis") and is directly
testable against the existing world survey. **Also note raiding at -0.01** - warfare does not predict hierarchy in
this sample, which is a caution against reaching for a conflict-driven stratification route.

## T-8 - Leaders are removed the way Boehm's societies remove them

**Status:** MET at the attempt level. **Origin:** R-84, 2026-07-18.
**Source:** Boehm 1993 Table I `[VERIFIED]`, columns counted over the 48-society survey.

Desertion 17 : deposition 9 (~65% desertion) among removal-type sanctions. **Model: 62-74% of sanction ATTEMPTS
are desertion.** The comparison is deliberately on attempts, not outcomes - Boehm codes which sanctions a society
PRACTISES, and in the model a challenge can fail against the margin while a desertion cannot.
**Still open:** the structural split (deposition in centralized societies, desertion in mobile/dispersed ones) is
anchored but **not yet tested** - it predicts that turning on settlement-scale institutions should shift the model
toward the deposition channel. That is a free prediction worth running.

---

## T-9 - Male-lineage effective-count collapse under stratification (Karmin et al. 2015)

**Status:** PROPOSED 2026-07-20; **NOT YET RUNNABLE as designed - see the 2026-07-21 note below.**
Replacing/supplementing T-6 as the primary quantitative check on lineage concentration. **Origin:** the search for a better-anchored alternative to Hayden's uncomputable 75% (T-6),
triggered by R-86v finding no base rate exists to compute Hayden's lift against.

**Why this is a stronger target than T-6:** Karmin et al. 2015 (Genome Research, `[VERIFIED]`, LITERATURE.md) is
a population-GENETICS statistic, not an ethnographic fraction - **female effective population size ran up to
17x male effective population size at the Y-chromosome bottleneck's peak (about 8-4 kya)**, i.e. male lineages
collapsed toward a few dominant patrilines while female-mediated diversity did not. This is a hard number with
a stated timing and geography, unlike T-6's unquantifiable raw fraction.

**The model already produces the qualitative signature, found independently before this source was located.**
R-66 (2026-07-13, deep-time Carbon-civilization campaign): *"patriline-name-fixation not equal to genetic"* -
`_lineage` (patriline) concentrates hard while autosomal genome diversity (H about 0.88-0.999) stays high. That
is the SAME shape Karmin describes: a male-lineage-specific collapse, not a general population bottleneck.

**What is needed to turn this into a real test (not yet run):**
1. Compute `dynasties()["eff_lineages"]` (the inverse-Simpson effective patriline count) for a matched pair of
   arms - EGALITARIAN (elite layer off) vs STRATIFIED (economic defensibility + material capture + legitimacy
   all on) - at a comparable population size and horizon.
2. Express the result as a RATIO: `eff_lineages(egalitarian) / eff_lineages(stratified)`, the model's own
   analogue of Karmin's female:male Ne ratio (a collapse in effective lineage count under stratification,
   against a roughly unchanged baseline).
3. Compare that ratio's ORDER OF MAGNITUDE to Karmin's about 17x - not an exact match (the model has no
   autosomal/maternal-lineage tracking to form a literal Nf, so the comparison is EGALITARIAN-eff_lineages as
   the stand-in "unstratified" baseline, not a true female-lineage count) but a real, falsifiable quantitative
   target where T-6 offered none.

**TWO SHARPER COMPANION TARGETS, added 2026-07-20 (LITERATURE.md, same entry) - more literally comparable to
`dynasties()`'s existing output than the aggregate Ne ratio, since both are direct "top lineage(s) share":**
- **Zerjal et al. 2003:** one lineage = ~8% of men (continental scale, ~1000 yr old, a named single dynasty).
  Compare directly against `dynasties()["top_share"]` (largest single lineage / population) in a stratified arm.
- **Yan et al. 2014:** three lineages = ~40% of men (national scale, ~6000 yr old, Neolithic/agricultural).
  Compare against the SUMMED share of the top 3 rows of `dynasties()`'s per-lineage table in a stratified arm.

These are arguably the more natural first test - `top_share` and a top-3 sum are already computed by
`dynasties()` with no new instrumentation needed, unlike constructing the egalitarian/stratified eff_lineages
ratio for the Karmin comparison. **PDFs for Zerjal and Yan not yet filed** (secondary-source verified only).

**Honest limits, stated up front:** (a) Karmin's ratio is female:male within ONE bottleneck period; the model
comparison is stratified:egalitarian across two CONFIGURATIONS, so the two ratios are analogous, not identical
quantities - the comparison tests order-of-magnitude concentration, not a literal replication. (b) the timing
(8-4 kya, Neolithic/Bronze Age agricultural societies) matches the model's "agricultural" society-type target
(T-5) better than the forager stage the elite layer currently operates at - this target is more naturally a
Stage-C/agricultural check than an immediate one. (c) not yet run - this is a proposal, not a result.

**UPDATE 2026-07-21 (R-89 -> R-93) - why this target could not be run as written, and what changed.**

The comparison assumed the model's lineage pool was a live population that stratification could concentrate.
It was not: `_lineage` could only be LOST, never created, so the pool was an ABSORBING process that fixates
with probability 1 regardless of the elite layer. Measured: 3000 founding patrilines -> 5 by step 1950, then
frozen. Worse, R-91's replay showed **every historical campaign run** reached that state (R-66's arms 61-62% of
the run, R-67's cycling tests 67-74%), so any egalitarian-vs-stratified contrast run before this would have
compared two frozen end-states rather than two live dynamics.

Three fixes later (R-90 branching -> R-92 segmentation -> R-93 relative legitimacy) the substrate now sustains
diversity: eff_lineages 3.4 -> **18.1**, top_share 0.422 -> **0.154**, lineages_per_band 2.14 -> **6.66**
against the FILED Hill 2011 ~7. **T-9 is now runnable in principle.**

**Two things to settle before running it:**
1. `resent_privilege_ref` must be re-anchored for the minority-elite regime, or the stratified arm has no
   working reversion mechanism at all (0 reversions vs 5,741 - RESULTS R-93).
2. **The UNIT of the comparison must be declared (D6) - and for Yan this is now RESOLVED.** The headline 40%
   is the top-THREE combined while the model's `top_share` is top-ONE; an earlier plot of ours drew 40% as a
   line against top-one before the mismatch was caught. **The filed PDF supplies the matched number**: the
   per-clade breakdown is *"16% for Oα, 11% for Oβ, and 14% for Oγ"*, so **largest single clade = 16%** is the
   like-for-like anchor for `top_share`. Measured: 0.154 (R-93/R-94), 0.192 (R-96) - same order, matched unit.
   Zerjal's ~8% remains one lineage across 16 populations and is SECONDARY-source only (PDF fetch failed; see
   LITERATURE), so it should not carry a headline comparison until filed.

**A SECOND, ALREADY-FILED TARGET was found to be live during this work** and is now the sharper near-term check:
MODEL_SPEC §4.8.8's **~7 lineages/band + dominant-lineage share 0.38 (Hill et al. 2011)**, which R-25 passed and
the lineage collapse silently broke. It had no standing test - it was validated once in a one-off probe and
never checked again, so it regressed unnoticed for months. `dynasties()` now reports `lineages_per_band` and
`dom_lineage_share` on every snapshot. **Recommend promoting it to a standing test with a declared horizon.**
