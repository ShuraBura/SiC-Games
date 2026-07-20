# SiC Games — Pre-Registered Hypotheses

**The ONE question:** "What did we predict *before looking*, and how did it resolve?" (charter §2, home 7).

**Purpose:** The authoritative record of what the project *predicted before looking at the data*, and how each prediction resolved. This document exists to prevent HARKing (Hypothesising After Results are Known). A hypothesis written here *before* the run that tests it is a genuine prediction; a "hypothesis" written after seeing results is a description, and the project does not count it as confirmation.

**Discipline (charter §1.4, §5):**
- **Append-only.** Never edit a hypothesis after its test has run. Add a dated **Resolution** block beneath it instead.
- Every entry has: an ID, the date registered, a falsifiable claim, the test specification (what run, what statistic, what threshold), the pre-committed interpretation of each outcome, and the stage/artifact that will test it.
- Nothing enters here without a test spec + pre-committed interpretation. Aspirations live in **TARGETS.md** and *graduate* here only when they acquire a falsification spec (charter §5).

**Status key:** `OPEN` (registered, not yet tested) · `RESOLVED-SUPPORTED` · `RESOLVED-REFUTED` · `RESOLVED-AMBIGUOUS` · `SUPERSEDED`.

> **Triage note (2026-06-05 reorg):** this file was consolidated from two divergent copies.
> Resolved/relocated entries were routed to their charter homes: **H1(ii) → RESULTS.md**
> (resolved finding); **H-ORTHOGONALITY → TARGETS.md T-2** + a DEAD_ENDS note;
> **H-instinct-debt → TARGETS.md T-3**. The three live, falsifiable, run-pending entries
> below stay here. See `archive/superseded/` for the two source files + routing notes.

---

## H-EMERGE-1 — Emergent group structure from topographic heterogeneity

**Registered:** 2026-05-29.
**Status:** OPEN.
**Centrality:** HIGH. This is a load-bearing pre-registration: the group-level dynamics the project intends to study later (differential cohesion, asabiyyah, between-group effects) are only legitimate to pursue if group structure *emerges* from existing mechanisms rather than being imposed. This hypothesis tests that precondition. It is registered now, before the terrain-topography stage exists, precisely because it would be tempting to assert after the fact ("groups emerged, as expected") — writing the prediction first is the honest order.

**Claim (falsifiable):**
On a single world with sufficiently large spatial extent and heterogeneous topography (distinct resource regimes — e.g. a highland regime and a valley regime), and at a population large enough to sustain a viable sub-population in each region, the existing mechanisms (local-neighbour Deffuant cultural transmission + spatial sorting + biparental/fission reproduction) will produce **spatially-partitioned cultural differentiation** — regions will develop measurably different distributions of the cohesion-relevant traits (c1, c2, and ψ) — **without any group-level mechanism being added.** Group structure is predicted to be an *emergent partition*, not a coded construct.

**Mechanistic grounding (see LITERATURE.md):**
- Epstein & Axtell (1996), Sugarscape "tribes": spatial structure + local interaction produces persistent cultural groups with no group-level rule. `[INLINE]`
- Turchin (2003) asabiyyah-on-frontiers: cohesion differentiates most sharply at high-contrast regime boundaries — i.e. exactly where topography creates them. `[INLINE]`
- Metapopulation / habitat-heterogeneity (population ecology): regions of differing carrying capacity structure local interaction and persistence. `[UNVERIFIED — general]`

**Test specification:**
- **Run:** the terrain-topography stage (roadmap: terrain → LHS → Stage 6), single world, heterogeneous topography with ≥2 distinct resource regimes, C strategy (and separately Si), Deffuant ON, existing mechanics only — **no group-membership code, no group-level cohesion variable, no between-group mechanism.**
- **Scale (from the 2026-05-28 perf audit; superseded by the 2026-06-05 substrate perf recon — see ARTIFACTS.md):** the substrate perf recon (6.0a-perf) found occupancy is the cost wall and grid-cells are sub-dominant at low occupancy; re-derive the affordable grid/N before this run.
- **Primary statistic:** Moran's I for c1, c2, ψ at steady state (diagnostic exists since Stage 3.3). High Moran's I = spatial autocorrelation = regional clustering of traits.
- **Secondary statistic:** regional trait distributions — partition agents by topographic region and compare per-region trait means and dispersions (SD, not Gini). Bimodality *across* the world resolving into *unimodal-but-different* distributions *within* regions is the signature of emergent groups.
- **Seeds:** ≥8 (a 2-seed result cannot distinguish genuine structure from a single lucky partition).

**Pre-committed interpretation (state before the run):**
- **Supported:** Moran's I for c1/c2 high and stable, regional trait distributions differ significantly and consistently across seeds, no group-level code present. → Emergent group structure is real on existing mechanisms; the asabiyyah / differential-cohesion programme is empirically grounded and may proceed to *measurement* (still not to imposed-group mechanisms).
- **Refuted:** Moran's I stays low / traits stay well-mixed despite topography. → Interaction/movement ranges too long relative to world extent. The correct response is **geometric** (larger world or shorter interaction radius), **not** a new mechanism.
- **Ambiguous:** structure in some seeds/regions but not others, or grid-size-sensitive. → Marginal-separation regime; characterise the dependence on grid/radius before any group-level work.

**Explicitly NOT licensed (TMTS guard):** a *supported* result licenses **measuring** emergent group properties. It does **not** license adding hierarchical lumping / family-cell base units, group-membership tracking, group-level cohesion variables, or between-group competition. Those remain deferred and would each need their own registration.

**Resolution:** *(none yet — OPEN)*

---

## H-SUBSTRATE-6.0a — Multi-occupancy substrate viability

**Registered:** 2026-06-03.
**Status:** RESOLVED-SUPPORTED (density-calibration flag raised) — 2026-06-08.

**Statement:** This is a substrate pre-registration, not a theory-bearing hypothesis. It records the sanity readings committed before the Stage 6.0a §7.2–7.4 behavioural numbers are seen, so a sane/insane substrate cannot be reinterpreted after the fact. The generalised multi-occupancy substrate (resource-split harvest, Cred-weighted contest for C, diffusion movement) is predicted to be a viable, physically-plausible generalisation of the one-agent-per-cell model.

**Pre-committed readings (stated before the run):**
1. **C viability (κ=0 and κ=1).** N(t) settles to a stable band — neither extinction nor unbounded growth — within the ≥2000-step run. Settles both κ → substrate viable; crashes/pins/explodes → broken or per-capita-need vs regrowth miscalibrated (blocking, investigate before 6.0b).
2. **Self-limiting density.** Per-cell occupancy stabilises (per-capita intake → metabolic break-even), not unbounded crowding or overcrowding-collapse to zero.
3. **Density vs ethnography (flat terrain).** Steady-state persons/km² (agents/cell ÷ 100) lands order ~0.1, within ~0.01–1. Inside → scale calibration sane for 6.0b; outside → per-capita-need vs sugar-regrowth miscalibrated for the declared 100 km²/cell (calibration flag, investigate before 6.0b).
4. **Cred–wealth concentration (κ=1 only) — OBSERVE AND DEFER.** Cov(φ,wealth) and the Cred distribution logged. Rising covariance + collapsing Cred toward a single dominant high-φ lineage = a **Matthew-runaway flag**. 6.0a does NOT mitigate and this pre-registration does NOT pre-commit an interpretation: observed, magnitude reported, design response deferred.
5. **N_carry / N ratio.** Settled N and whether it sits in a viable band reported as evidence toward the deferred N_carry reconciliation. No threshold pre-committed; descriptive only.

**Test reference:** Stage 6.0a §7.2 (C-behavioural, κ=0 vs κ=1, ≥2000 steps), §7.3 (density validation), §7.4 (N_carry flag). Recovery gate §7.1 PASSED bit-identically.

**Resolution (2026-06-08):** RESOLVED-SUPPORTED — density-calibration flag raised.

Full §8 report: `outputs/stage6_0a_substrate/gate_6_0a_report.md`.

| Pre-registration | Outcome |
|-----------------|---------|
| C viability (κ=0 and κ=1) | **SUPPORTED.** Settles ~1080/1150 both κ. Self-limiting. No extinction. |
| Self-limiting density | **SUPPORTED.** Per-cell occupancy stabilises; no crowding-collapse. |
| Density vs ethnography (0.01–1 p/km²) | **CALIBRATION FLAG.** 0.00108–0.00115 p/km² (pkl, κ=0/1, 100×100 grid, final-step snapshot); ≈9× below band lower bound, ≈90× below expected ~0.1 → hands to calibration pass. |
| Cov(φ,wealth) — observe and defer | **OPEN-PENDING-CALIBRATION.** Cov≈−0.11; negative (not Matthew-runaway). Re-measure at production density. |
| N_carry / N ratio — descriptive | Settled/N_carry≈2.7–2.9 (multi-occ decouples from N_carry; descriptive only). |

Occupancy-cliff finding (6.0a-perf): recorded as **superseded-premise correction** — Stage 7.5
array restructure (VecJTM + C1 diagnostic vectorisation, GATE FINAL PASS 2026-06-08) cleared
the Python-path infeasibility. Proto-ag density is no longer blocked by the legacy O(N²) paths.

Parameter references: all values in `docs/PARAMETERS.md` (authoritative, extracted 2026-06-08).

---

## H_cc — C carry-discount counter-cyclical recovery

**Registered:** Stage 4.5 patch (2026-05-28).
**Status:** OPEN (partially supported, single-seed) — KEPT live: the multi-seed A=0.9 run is still planned.

**Claim (falsifiable):** The carry_discount birth ceiling (`max(0, 1 − N_C/N_carry)`) produces a counter-cyclical birth boost during troughs: as N_C falls during a trough, the discount decreases, P_birth rises, accelerating recovery. C trough-recovery speed is therefore faster than a DTM-formula-alone prediction.

**Test specification:** regress C trough-recovery time on N_min/N_carry across seeds; predict a negative slope. Multi-seed at A=0.9 (≥5 seeds).

**Status detail:** Regression-supported at Stage 5 (single-seed). Pending multi-seed at A=0.9.

**Resolution:** *(none yet — single-seed supportive; multi-seed pending)*

---

## H-TERRAIN-ASYMMETRY — Generator reachable world-space is biome-asymmetric

**Registered:** 2026-06-13.
**Status:** RESOLVED-CONFIRMED (structural; not an empirical claim requiring a run).
**Category:** Generator design note — pre-registered as a finding to prevent future "mountain-dominant worlds" from being interpreted as achievable calibration targets.

**Claim:** The terrain generator's reachable world-space is *asymmetrically bounded* in biome dominance. Specifically:
- `desert_fraction` can reach ≥ 0.76 (aridK near max saturates the NPP floor).
- `mountain_fraction` is structurally capped at ≈ **0.317** and cannot exceed this ceiling regardless of knob values.

**Structural cause (verified 2026-06-13, coarse ceiling search):**
Mountain classification requires the *joint* condition `elev > 0.72 AND slope > 0.18` (at relief=1.0). Under spatially autocorrelated FBM elevation:
- High plateaus satisfy `elev > 0.72` but are flat → fail `slope > 0.18`.
- Steep valley flanks satisfy `slope > 0.18` but are low → fail `elev > 0.72`.
- Only the narrow set of high-and-steep cells satisfies both; spatial autocorrelation makes that set self-limiting.
- High waterK raises mountain_fraction by flooding low/mid-elevation land (reducing the land-cell denominator), but cannot push the joint-condition fraction past ≈ 0.317.

**Ceiling search (Step 1 of CC_A8_Mountain_Ceiling_Directions.md, 2026-06-13):**
Grid: relief=1.0 (pinned) × rough=[0,0.33,0.67,1] × waterK=[0.1,0.4,0.7,0.99] × aridK=[0,0.33,0.67,1] × 7 seeds = 448 worlds.
Result: mtn_ceiling = 0.317. Best knobs: rough=1.0, waterK=0.99, forestK=0.5, aridK=0.0 (aridK irrelevant). Ceiling held across 7 seeds (mean≈0.225; max=0.317 is genuinely the ceiling, not one lucky draw).

**Consequence:** mountain-dominant worlds (mountain_fraction >> 0.3) are **not producible** by this generator. Any hypothesis or analysis that requires a mountain-dominant world is blocked until either (a) the generator is redesigned (out of scope for Phase 1) or (b) the question is reframed around the achievable range [0, 0.317].

**A8 acceptance criterion:** `mountain_fraction ≥ 0.9 × mtn_ceiling = 0.285`. Desert stays absolute ≥ 0.5.

**Out of scope (do NOT):** lower `mtn_elev_thresh` / `mtn_slope_thresh` to hit a coverage number — that redefines "mountain" and corrupts a terrain primitive.

**Resolution:** RESOLVED-CONFIRMED (structural finding, coarse grid search 2026-06-13).

**Update 2026-07-08 — SUPERSEDED for mountain-dominant worlds by orogeny (RESULTS §R-59; ARCHITECTURE §9.5.1a).** The ceiling is confirmed *more* structural than stated — high∧steep is geometrically self-limiting (steepness = elevation gradient, so a uniformly high massif is flat; ridge-boost + uplift prototypes top out ≈ 0.34). And the gate was never anchored: `slope` is the per-world max-normalized gradient (not a grade), `0.72/0.18` are unanchored Stage-7 constants, and physical slope on a real 4 km range is ~1° at 10 km/cell (sub-grid). The gate was therefore NOT lowered. Instead the alpine biome is redefined by the **Köppen 10 °C warmest-month air tree-line** (consistent with Körner & Paulsen 2004's 6.7 °C growing-season soil mean — cold-because-high, elevation/lapse-driven), riding on an opt-in **orogenic uplift massif** (`orogenK`) that builds a genuine ~4 km range (~2 km prominence) out of lowland. Alpine is climate-graded ≈ 0.36/0.77/0.93 (tropical/temperate/boreal) on real mountains with vegetated valleys; the same range is less alpine in warm climates (higher tree-line). This is the "redesigned generator" clause (a) anticipated in the Consequence above. Default (`orogenK=0`) is bit-exact ⇒ the 0.317 ceiling remains exactly true for every default world; only the explicit `alpine` preset exceeds it.

---

---

## §H1ii-RETEST — H1(ii) re-test on rebuilt terrain + resource substrate (pre-registered)

**Registered:** 2026-06-13 (Consolidated Reconciliation directive).
**Status:** OPEN — pre-registered for re-test. NOT a standing confirmed result.

**Background:** H1(ii) (Si is more resilient than C under periodic resource shocks) was confirmed INVERTED in Phase 0 Sugarscape-era runs (Stage 4.2–Stage 5.1): C persisted at A=0.75/T=200; Si collapsed (dormancy cliff). The Stage 5 ensemble confirmed the inversion 5/5 seeds. The Sugarscape-era finding is recorded in `RESULTS.md R-1`.

**Why the prior confirmation does NOT carry forward:** The Phase 0 confirmation was on the homogeneous flat Sugarscape substrate with no terrain. Phase 1 rebuilds the resource ecology on a continental terrain generator (heterogeneous biomes, realistic foraging returns, spatial structure). The terrain substrate is expected to qualitatively alter the resource-access dynamics that drove the dormancy cliff. A finding on the old substrate does not pre-commit the result on the new substrate — it is a prior, not a standing fact. The inversion may hold, deepen, reverse, or become parameter-dependent under terrain. Pre-registering the re-test here (before running) is the anti-HARKing discipline.

**What is pre-committed:**
- **Claim:** The strategy resilience inversion (C > Si at A=0.75/T=T*) either holds, reverses, or becomes conditional on terrain type under Phase 1 terrain + resource ecology.
- **Test specification:** Multi-seed (≥5 seeds, CRN), C vs Si matched worlds, Phase 1 terrain substrate active, at least two amplitude/period combinations bracketing the Phase 0 T* = (68,87) window. Statistic: proportion of seeds where C survives to t=1500 vs Si extinct.
- **Calibration prerequisite:** OWE-14 (re-confirm at calibrated N_carry=4100, ≥3 seeds) must complete before this re-test is authoritative at the 100×100 scale.
- **Pre-committed outcomes:**
  - **Holds:** C survives, Si collapses, same mechanism (dormancy cliff) → terrain does not rescue Si; original finding extends to new substrate.
  - **Reverses:** Si survives, C collapses → terrain creates a resource regime where C's JT-based clustering becomes a liability; requires mechanism explanation.
  - **Conditional:** outcome depends on terrain type (biome mix, water coverage) → terrain is a moderator; report the conditioning variable.
  - **Indeterminate:** neither pure collapse/survival → parameter-dependent; report the T*/A* shift and mechanism.

**Adjudication stage:** §STAGE-RECAL (ROADMAP, DEFERRED). This re-test is one of the targets for that stage.

**Resolution:** *(none yet — OPEN, pre-registered 2026-06-13)*

---

*End of HYPOTHESES — consolidated 2026-06-05; §H1ii-RETEST appended 2026-06-13. Append-only; graduate targets in by moving them from TARGETS.md with a test spec.*

---

## H-CYCLES — Secular cycles require a DELAYED negative feedback, not a stronger one

**Status:** OPEN — pre-registered 2026-07-18. **Origin:** supervisor (architecture discussion, the field/operator
framing). **Home of the criterion:** `MECHANISM_CHARTER.md` §5.

**Claim.** The model has failed three times to produce secular cycles — connubium (R-67), substrate attractor
(R-68), soil/swidden (R-71) — and these are not three facts but **one**: every feedback in the model is
INSTANTANEOUS negative feedback, whose linearization has a real negative eigenvalue and therefore a stable node.
A stable node returns to equilibrium exponentially; it cannot oscillate. Boehm leveling is the clearest case — it
corrects excess *within the same step*, which is exactly why it CAPS inequality (3.68x -> 2.21x, R-83) rather
than overshooting it.

**Prediction (falsifiable).** Introducing a **lag** between a quantity and the correction that removes it, of
order the measured relaxation time (~250 steps, from R-68's kill-half recovery), will produce sustained
oscillation where no amount of strengthening an instantaneous feedback does. Specifically: elite NUMBERS
responding to elite WEALTH with a generational (~20 yr = 240 step) delay.

**How it could fail (and what each failure teaches):**
- Oscillation appears but is damped -> the delay is too short relative to relaxation, or the loop gain too low.
- Oscillation appears at the wrong period -> the delay is the wrong length; period should scale with it.
- No oscillation at any delay -> the loop gain is below the Hopf threshold; the elite feedback is too weak to
  matter regardless of timing, which would be a genuine and interesting negative.
- Runaway instead -> the feedback is net positive, not delayed-negative (an R-66-class failure).

**Test protocol.** Cheap first: linearize a mean-field reduction around the measured equilibrium and locate the
Hopf boundary in (delay, gain) analytically. Only then build. **The mean-field reduction is an ANALYSIS TOOL for
this hypothesis only** — explicitly NOT a replacement for the ABM (charter §5), which must keep the
individual-level outputs (RS skew, dynasties, kinship).

**ETHNOGRAPHIC ANCHOR ADDED 2026-07-18 (Flannery & Marcus ch. 10, [VERIFIED]).** The hypothesis was
pre-registered on a purely dynamical argument. It now has a documented case: **Kachin gumsa/gumlao cycling**,
where societies shift back and forth between ranked and egalitarian modes and *"hereditary inequality was
repeatedly created, lasted for a few generations, and then collapsed."*
- **The period is given: "a few generations" (~60–100 yr).** That is the target for any oscillation the model
  produces, and it is ~3–5× the ~250-step relaxation time measured in R-68 — a plausible Hopf regime.
- **The mechanism is explicitly a LAG:** leaders' prestige-seeking *"only increased their followers' resentment
  and hastened their overthrow"* — resentment ACCUMULATES over generations, where our Boehm leveling corrects
  within the step. This is direct field support for the delay, not just the dynamical argument.
- **REFINEMENT to the prediction:** the lagged variable should be a **legitimacy/resentment stock**, not only
  elite material wealth. Friedman's endogenous account makes rank a *legitimacy reinterpretation* ("they pleased
  the nats" → "they descend from higher nats"), so both the rise AND the collapse run through legitimacy. The
  model's `GroupVector.religion` cell — currently a **stub** — is the natural carrier.
- **A second, DISTINCT cycling mode is named and should not be conflated:** Polynesian *status rivalry* among
  near-equal heirs (assassination/overthrow/usurpation), which cycles *incumbents* without cycling the
  ranked/unranked *regime*. Our R-84 challenge-succession already models something close to this — so the model
  may already contain the Polynesian mode while lacking the Kachin one.

**Resolution (2026-07-18, R-87): PREDICTION NOT MET — but partially supported, and the hypothesis is REFINED
rather than refuted.**

A delayed negative feedback was built explicitly to supply the missing complex eigenvalue pair (the gumsa→gumlao
resentment/reversion mechanism, R-87). Swept across lag memories of 4, 83 and 167 years, it produced **no
periodic behaviour at any lag** — a fourth independent negative for secular cycles.

Two results keep the hypothesis alive in refined form:
- **The lag acts in the predicted direction.** Autocorrelation peak rises monotonically with lag length
  (0.03 → 0.13 → 0.19). The mechanism behaves as the theory says; it does not reach cycle amplitude.
- **Large-amplitude system-wide regime switching now exists**, where the three prior negatives had none:
  sd(frac_gumsa) = 0.428 vs an independent-bands null of 0.056–0.112, i.e. **3.8–7.7× the null**, so bands
  switch together. The model alternates between ranked and egalitarian across nearly the full range.

**Refined statement:** a delayed negative feedback is apparently sufficient for **recurrent regime alternation**
but not for **periodicity**.

**AND THE PREDICTION WAS MIS-SPECIFIED — by me, not by the source.** The literature check was run the same day:
Flannery's Kachin are "created, overthrown, and **periodically reinstated**", "this **repetitive cycle**",
"**oscillated between**", with the duration claim "lasted for **a few generations**". **A fixed period is
nowhere asserted; recurrence plus a characteristic SPELL DURATION is.** The autocorrelation test therefore
measured a property the ethnography does not claim, and H-CYCLES' "period ~60–100 yr" should be restated as
**"mean dwell time in the ranked regime ~60–100 yr"**.

**On the corrected metric the model still misses, but differently and by a diagnosable amount:** estimated mean
gumsa dwell is **3.9 / 10.2 / 4.8 yr** at the three lags, i.e. **one to two orders short** of the anchor. The
model alternates far too fast. The likely cause is no longer "missing lag" (the lag is built and acts in the
right direction) but that the reversion trigger — a hard threshold on a noisy quantity — is crossed
stochastically rather than by clean build-up.

**RESOLVED NEGATIVE 2026-07-18 (R-87d), on fixed and control-validated instruments.** Both detectors were
re-specified (reject periods beyond window/3; require a genuine local maximum) and re-validated against a
positive control — a real 75 yr cycle is still recovered at 75.3 yr. On the real series the autocorrelation
peaks are NEGATIVE (−0.021, −0.028) and the sinusoid explains 5–14% of variance. The raw trace, plotted and
inspected, is one build-and-collapse episode followed by ~150 yr pinned at zero: not oscillatory in any form.
**A delayed negative feedback is NOT sufficient for secular cycles.** Fourth independent negative, and the first
on validated instruments. Reported quantity is now CORRELATION TIME (15–33 yr), which does rise with the lag,
and DWELL TIME — both 2–6× short of the 60–100 yr ethnographic anchor.

**RESOLVED FURTHER (R-88, 2026-07-20): the non-monotonicity is explained, and the governor is identified.**
Band lifetime (median 10.2 yr, mean 17.5 yr) is IDENTICAL across the 83-yr and 4-yr-control arms - band churn
is exogenous, driven by `band_split_size`/`band_merge_size`, not by resentment. Mean band lifetime (17.5 yr)
sits almost exactly on the measured correlation time (~20-22 yr) uniform across ALL THREE tested memories
(4/83/167 yr): `_maintain_bands()` FISSION mints a fresh `band_id` whose `_band_resentment` entry defaults to
0.0 (a silent reset never counted in `reversions_this_step`), and FUSION abandons the absorbed band's entry
entirely. **A delayed social feedback cannot express a memory longer than the unit carrying it survives** - the
band does not live long enough for `resent_alpha` to matter at 83 or 167 yr, and even the 4-yr control's own
short memory is itself governed by band turnover rather than by its own alpha.

**Next step:** either move the slow social state to a longer-lived unit (LINEAGE or SETTLEMENT instead of BAND)
before re-testing periodicity, or treat this as the standing explanation and move on - re-running H-CYCLES on
the band unit without addressing this would re-measure the same ceiling.
