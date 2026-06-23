# SiC Games · Phase 1 · **Cred-vector + B+ paternity** — Scoping draft

**Status:** SCOPING for red-team (2026-06-21). Generalizes Carbon-on-substrate (R-18) from a **scalar** Cred to
a **multifaceted status vector**, adds **earned prowess** (growth + decay), and introduces **paternity** so the
male achieved facet can be inherited and reproductively rewarded. Target = **B+** (minimal paternity +
prowess-weighted mate-choice + *partial* paternal provisioning), **all knob-tunable** so it collapses cleanly
**B+ → B → matrilineal → R-18-scalar**, and **C** (full pair-bonding) can bolt on later. Builds on R-18.

---

## 0. Why these pieces come together
Lineage = inherited *parental* standing, and real forager status is **bilateral + multidimensional**. To model
"father's hunter record + mother's forager record" the design pulls in a chain: **multifaceted Cred** (so
hunting-prowess is a distinct facet) → **sex-divided production** (so men earn hunting-prowess, women foraging-
competence) → **paternity** (so the father's facet can propagate) → **mate-choice** (so prowess has a
reproductive consequence — the von Rueden status→fitness loop). Each link is independently tunable.

## 1. Literature anchors (pulled 2026-06-21; ★ = need full PDF, see §8)

- **von Rueden & Jaeggi 2016, PNAS 113:10739** (meta-analysis, 33 nonindustrial societies, 288 associations;
  **open access PMC5047206**). Male status → reproductive success **r ≈ 0.19** (95% CI 0.09–0.31) — *real but
  MODEST in humans* (cf. r≈0.80 in nonhuman primates: human egalitarian leveling). **Four status dimensions —
  physical formidability, hunting ability, material wealth, political influence — carry ~EQUAL weight** (each
  r≈0.30): status is genuinely multidimensional. Effect is **strongest via mating success + fertility (r≈0.50)**,
  weaker via offspring survival (r≈0.39) → the *mating* channel dominates, provisioning is secondary.
  **Polygyny amplifies** the surviving-offspring effect ~⅓ vs monogamy. → *Calibration: tune mate-choice skew
  LOW (~r 0.19); facet weights comparable; mating is the primary channel.*
- **Smith 2004, "Why do good hunters have higher reproductive success?", Hum. Nat. 15:343** (★; open preprint
  faculty.washington.edu/easmith/HunterRS.pdf). Hunting→RS runs mainly through **social status / mating**, not
  direct provisioning. **Reputation > instantaneous return**: Aché hunting *reputation* predicted RS (forest
  period), observed *return rate* did not (reservation). → *prowess = an ACCUMULATED reputation (EMA + decay),
  not raw per-step yield.*
- **Marlowe 2003, "A critical period for provisioning by Hadza men", Evol. Hum. Behav. 24:217** (in
  `literature/`, EXTRACTED). Baseline adult **male provisioning ≈ 43%** of camp Kcal (female 57%); it **rises
  to 58% when a man has a child <3 yr, and 69% when <1 yr** (the lactation critical period). Conditional on
  **biological paternity** — men provision more "so long as the children were their own offspring and not
  stepchildren." Polygyny ≈ 4% of Hadza men. → *`paternal_provision_frac` calibration target: emergent male
  share of <3-yr-old provisioning ≈ 58% (vs ~43% baseline); the RT-2 residual-need routing lands it on exactly
  this constrained-mother/young-child cohort.*
- **Descent/residence (web, 2026-06-21):** foragers are predominantly **bilateral descent + flexible/bilocal
  residence** (~40% bilocal, 23% matrilocal, 25% patrilocal; gathering-heavy → matrilocal lean; early human
  kinship tended matrilineal). → ***Q3 RESOLVED: `patriline_weight = 0.5` (symmetric bilateral) is the
  lit-justified default***, with a defensible slight matrilineal tilt option.
- **Polygyny rates** (PLoS ONE 2011 marriage-practices; Traditions-of-Conflict review). Foragers **mostly
  monogamous** (~11% of men ever polygynous; best hunters up to 2 wives). Skew is driven by **serial monogamy**,
  not simultaneous harems. **Aché: partible paternity — 2.1 possible fathers/child.** → *B+'s per-conception
  mate-choice lottery captures the serial-monogamy skew WITHOUT pair-bonds; simultaneous polygyny (the ~10%
  tail) is a C-feature; single-father is a simplification of Aché partible paternity (flag).*
- **Batek (Kraft et al. 2019)** — foraging performance did NOT predict RS in an egalitarian forager group →
  the status→RS link is **real on average but context-dependent** (egalitarian leveling can suppress it).
  *Maps onto C-vs-Si: Silicon = the leveled/low-skew regime, Carbon = the high-skew regime.*
- *(In repo already, supporting:)* Boyd & Richerson 1985 prestige-bias (LITERATURE.md), von Rueden Gurven
  Kaplan 2008 multidimensional Tsimane status ★, Trivers 1972 parental investment (conceptual), Hill & Hurtado
  1996 Aché (in literature/).

## 2. Architecture

### 2.1 Cred → facet vector; κ → domain×facet matrix
`cred` (scalar) → **c = (c_lineage, c_prowess[, c_influence])**. The contest weight in **domain d** is
**Cobb–Douglas**: `w_{i,d} = Π_f (c_{i,f} + ε)^{κ_{d,f}}`. **κ is a matrix** (rows = domains, cols = facets) of
exponents. With one facet & one domain this is *exactly* R-18 (`(cred+ε)^κ`) → backward-compatible. Domains:
**sharing** (meat split), **movement** (cell contest), **mate-choice** (new). This **dissolves the R-18 caveat**:
the two channels become two κ-rows; the ablation = zero a row.

| facet | type (Linton) | source | decay |
|---|---|---|---|
| **c_lineage** | ascribed | seeded + inherited at birth (bilateral, §2.4) | **none — but mean-reverting** (RT-3): inheritance blends toward the *population mean* so it can't drift unboundedly |
| **c_prowess** | achieved | provisioning *reputation* (sex-specific, §2.3) | fast λ (fades w/o renewal) |
| *c_influence* (later) | achieved | being followed (leadership, Tier-2 §6b) | medium |

### 2.2 Prowess growth + decay (the "earned Cred" loop; Smith/von Rueden)
`c_prowess ← (1−λ)·c_prowess + gain`, **gain = Matthew-amplified provisioning reputation**:
`gain = γ · (c_prowess+ε)^α · max(0, provided − band_mean)` — you earn prowess by **provisioning above the band
average** (costly signaling, Hawkes), amplified by existing reputation (`α` = Matthew). **Reputation, not raw
yield** (Smith): `provided` is a smoothed/realized provisioning, so a lucky one-off doesn't spike status.
**Decay λ** is the homeostat **for prowess only** (lineage gets its own homeostat, §2.4 ρ). Runaway brakes:
λ + `tanh` saturation + α tuned (Gini-drift hard gate on **lineage AND prowess**). **Caveat (R-18, align §1):**
R-18 found the operative survival channel is **spatial competition near K**, not temporal meat variance — so a
prowess signal built on "meat provided − band mean" may be **weak near K** (meat is mostly cap-clipped there).
Measure the realized prowess signal; if weak, base `gain` on *realized provisioning to others* (which captures
the spatial-success channel) rather than raw meat overflow.

### 2.3 Sex-divided production (so prowess is sex-specific) — TUNABLE
Men preferentially produce the **meat** stream, women the **forage** stream (the documented division; currently
inactive in the rivalrous path). Knob **`sex_division`∈[0,1]**: 0 = unisex (current; back-compat), 1 = strict.
Male prowess accrues from **meat** provisioning (high-variance → the show-off facet); female prowess from
**forage** (steadier). *(For a first cut, prowess can be a single facet earned from each sex's own stream; a
two-prowess [hunting/gathering] split is a refinement.)*

### 2.4 B paternity + prowess-weighted mate-choice (bilateral lineage)
At each **conception** (the existing IBI birth event, mother's schedule UNCHANGED — R-3/R-17 preserved):
assign a **father** from co-located/nearby males via a **prowess-weighted lottery**:
`P(father = j) ∝ (c_{j,prowess}+ε)^{m}` — **`mate_choice_strength` m** tunes the skew (m=0 → random pairing
[paternity for lineage only, no fitness skew]; m>0 → high-prowess men father more). **Calibrate m so the
emergent status→RS ≈ r 0.19** (von Rueden). Set **father-link** `child._father = j`. **Bilateral inheritance with mean-reversion (RT-3 fix — the
load-bearing homeostat):** `child.c_lineage = (1−ρ)·blend(mother_standing, father_standing) + ρ·pop_mean_lineage`,
where blend is `patriline_weight`-weighted (0.5 = symmetric) and **`ρ`>0 pulls inheritance toward the population
mean** so the *no-decay* lineage facet still has a brake — without ρ, lineage compounds unboundedly (the real
runaway channel; decay λ only touches prowess). **Paternity drift-control (RT-4 fix):** the build MUST run the
R-18 paired design — an `m>0` run against an `m=0` (random-paternity) twin sharing seeding/inheritance RNG; the
status→survival signal only counts if it **exceeds the random-paternity drift twin**. Report **male effective-N**
(`N_e`) explicitly — strong `mate_choice_strength` collapses it and can manufacture a *drift* hierarchy.
Serial-monogamy skew emerges from the per-conception lottery (no pair-bond); **Aché partible paternity** (2.1
fathers) is a flagged single-father simplification (later: a co-father set).

### 2.5 B+ paternal provisioning — TUNABLE (0 ⇒ rolls back to B exactly)
A father directs a fraction **`paternal_provision_frac`∈[0,1]** of his **meat surplus** to his **own** children
(`_father` link), **biased to biological offspring** (Marlowe). **`paternal_provision_frac = 0` ⇒ pure B**.
**No-double-count routing (RT-2 fix — build-blocking detail):** add it as a **THIRD provisioning tier AFTER the
two maternal tiers** (`phase1_model.py:361-380`), drawing `min(residual_need, father_overflow)` against the
**single running `need` accumulator** the maternal tiers already decrement — *never* a recomputed need (else the
mother fills the child to cap and the father fills it *again* → energy creation). Father overflow comes from a
`father_provision_pool` populated from his `total-cap` at line ~354, exactly mirroring the mother's tier-1.
**Consequence (and it's the right one, Marlowe):** because it targets the *post-maternal residual* deficit,
paternal provisioning is automatically **inert when the mother is solvent** and **bites only on the
constrained-mother / orphan cohort** — precisely the lactation-critical-period target. **Conservation test:**
`Σ child intake ≤ Σ child caps`; `Σ transfers ≤ Σ overflow`.

### 2.6 The tunable nesting (the "seamless roll-back")
`paternal_provision_frac=0` → **B**. `mate_choice_strength=0` → random paternity (bilateral lineage, no skew).
`father-link off` → **matrilineal-only**. `sex_division=0` → unisex production. single facet + single domain →
**R-18 scalar**. And the C-seam: `paternal_provision_frac`, a future `pair_bond_persistence`, and a
`polygyny_cap` are where **C** bolts on. Nothing built here is wasted toward C.

## 3. Build order (within this stage; each nests)
1. **Cred-vector refactor** (scalar→vector, κ→matrix, Cobb–Douglas; collapses to R-18). Foundation + tests.
2. **Prowess growth/decay** (§2.2) — earned achieved facet; the fc_sweep Gini-drift guard.
3. **Sex-divided production** (§2.3, tunable) — so prowess is sex-specific.
4. **B paternity + mate-choice + bilateral lineage** (§2.4) — father-link, calibrate m to r≈0.19.
5. **B+ paternal provisioning** (§2.5, tunable, 0=B) — the no-double-count gate.

## 4. Validation / gates
- **status→RS ≈ r 0.19** emergent (calibrates `mate_choice_strength`); **mating channel > survival channel**
  (von Rueden); facet weights comparable.
- **Reputation predicts RS, instantaneous yield does not** (Smith) — emergent check on the EMA/decay design.
- **Paternal provisioning biased to bio offspring, matters under maternal constraint** (Marlowe) — emergent.
- **Modest polygyny/serial-monogamy skew** (~10% men multi-mate) — emergent from the lottery, not imposed.
- **VITAL RATES preserved, composition deliberately reopened (RT-1 fix):** births stay female-IBI-only, so
  **eq_pop / IBI / TFR / growth-phase e₀ reproduce R-3/R-17/R-18 within seed-noise** (the numeric regression
  gate) — but the *equilibrium mortality composition* (who dies) is **intentionally** reopened: that IS the
  R-18 channel, now with an added reproductive arm. Don't claim "core untouched"; claim "rates fixed,
  composition is the experiment."
- **Nesting = statistical, not bit-for-bit (RT-7/8 fix):** the conception-time paternity lottery is a NEW
  RNG consumer, so rollback reproduces R-18/B *statistically* (N-seed), not bit-identically — UNLESS the
  lottery is gated to draw **zero** RNG when `mate_choice_strength=0` / father-link off (then bit-for-bit holds).
  461→ green throughout (opt-in defaults).

## 5. Red-team targets (for the fresh repo-grounded sub-agent)
RT-1: **Does B+ keep the validated demographic core read-only?** Fertility stays maternal-IBI; paternity +
paternal provisioning must not change *how many* are born (only who fathers / who's fed). Verify no R-3/R-17
regression path.
RT-2: **Paternal-provisioning double-count** (the load-bearing one) — father→own-child meat ON TOP of the band
meat share + the mother's forage overflow (S1/C.2b). Is there a clean conserved routing, or does it over-feed?
RT-3: **Runaway** — the loop is now prowess→mating→inherited lineage→(weighted in sharing)→survival/more
prowess: a *reproductive* arm the scalar R-18 lacked. Does it runaway (chiefly oligarchy, Gini→1, effective-N
collapse)? Is λ+tanh+α+the Gini-drift guard enough? Is the human r≈0.19 calibration a sufficient brake?
RT-4: **Small-N paternity drift** — strong mate-choice → few fathers → male effective-N collapses → lineage
facet drifts like a small-N random walk → hierarchy by *drift* not selection (R-18 RT-5, amplified by the
reproductive skew). Gate?
RT-5: **Cobb–Douglas vs additive** — is `Π(c_f+ε)^{κ_{d,f}}` right (facets complementary; a zero tanks the
weight), or should facets substitute (additive)? Identifiability of the κ-matrix (too many free exponents?).
RT-6: **Sex-division break** — does activating men-meat/women-forage break the e₀/economy validation, or
interact with the two-stream G.1/G.2 economy + provisioning?
RT-7: **Partible paternity / single-father** — is collapsing Aché 2.1-fathers to one father a problem for the
lineage signal or the validation?
RT-8: **Tunable nesting** — does `paternal_provision_frac=0` reproduce B *exactly*; each knob→0 reproduce the
parent regime bit-for-bit (the seamless-rollback claim)?
RT-9: **Scope / parameter discipline** — is the κ-matrix + (sex_division, λ, α, m, patriline_weight,
paternal_provision_frac) the minimal identifiable set, or is it sprawling? What's deferrable?

## 6. Out of scope / deferred → C
Pair-bond persistence + dissolution; simultaneous polygyny + a polygyny cap; assortative pair-formation; full
paternal care (beyond meat); widowhood/remarriage/orphan dynamics; partible-paternity co-father sets;
c_influence + the leadership movement model (Tier-2 §6b of the Carbon scoping bp). All bolt onto the B+ seams.

## 7. Open questions for the supervisor
- **Q1:** Facet set — **red-team recommends minimal: 2 facets (lineage + single prowess), defer c_influence**
  (the leadership hook) until the κ-matrix has >1 identifying constraint. OK, or include c_influence now?
- **Q2:** Prowess as **one facet earned from each sex's own stream** (red-team rec, keeps it identifiable), or a
  **two-facet hunting/gathering** split from the start?
- **Q3:** `patriline_weight` default — symmetric **0.5** bilateral, or a patrilineal/matrilineal bias?
- **Q4:** Calibrate `mate_choice_strength` to the von Rueden **r≈0.19** (modest), confirmed? (Guards runaway.)

## 8. Literature I still need from you (paywalled — flag ★)
- **Marlowe 2003** (Evol. Hum. Behav. 24:217) — paternal-provisioning fractions + the critical-period numbers.
- **von Rueden, Gurven & Kaplan 2008** (Evol. Hum. Behav. 29:402) — the multidimensional-status correlations.
- **Smith 2004** Hum. Nat. 15:343 — *likely open* (faculty.washington.edu/easmith/HunterRS.pdf); I can fetch.
- von Rueden & Jaeggi 2016 — **have the numbers** (open PMC5047206); full PDF optional.
I have enough from abstracts/PMC to scope + calibrate direction; full PDFs would sharpen the provisioning
fraction (Marlowe) and the per-dimension correlations (von Rueden 2008). Tell me which to prioritize, or drop
the ★ PDFs into `literature/`.

---

**Code anchors:** `substrate.py` `status_of`/`compute_harvest_shares` (scalar→vector), `phase1_model.py`
`_step_rivalrous` (sharing+movement domains), `_do_births_ibi` (paternity + inheritance hook), `_make_agent`
(facet init), `_select_stream` (the dormant sex-division). R-18 (scalar validated), R-14 (fecundity ensemble —
reopened minimally), R-3/R-17 (vital rates to keep fixed).

## 9. Red-team record (2026-06-21, fresh repo-grounded sub-agent) — VERDICT: APPROVE-WITH-FIXES (applied)

All code claims verified TRUE (births female-IBI-only `_do_births_ibi:499`; **zero** `father` matches in
`sic_games/src`; `status_of` scalar→vector target; Cobb–Douglas single-facet == R-18; κ weights harvest AND
movement; `_select_stream` sex-division dormant in the rivalrous path). Findings + resolutions:
- **[MAJOR→fixed] RT-2 double-count:** paternal provisioning must be a **third tier after the maternal tiers**,
  drawing `min(residual_need, father_overflow)` against the **single running `need`** (not a recomputed need) —
  else mother + father both fill the child to cap (energy creation). Lands it on the constrained-mother/orphan
  cohort = the Marlowe target. + conservation test. §2.5.
- **[MAJOR→fixed] RT-3 the runaway is `c_lineage`, not mate-choice:** decay λ only homeostats *prowess*; the
  *inherited* lineage facet had **no brake** → unbounded compounding. Fix: **mean-reversion ρ** in the
  inheritance blend (pull toward population mean) + the **Gini-drift hard gate on lineage** (abort/flag), not
  just prowess. §2.1/§2.4. (The human r≈0.19 mate-choice calibration is a *target, not a brake* — corrected.)
- **[MAJOR→fixed] RT-4 paternity drift-control:** port R-18's paired design — `m>0` vs `m=0` random-paternity
  twin sharing RNG; signal counts only if it beats the drift twin. Report **male N_e**. §2.4.
- **[MINOR→fixed] RT-1 "read-only" oversold:** true for *vital rates*, false for *equilibrium mortality
  composition* (= the R-18 channel, deliberately reopened). Reworded + numeric regression gate. §4.
- **[MINOR→fixed] RT-5/9 κ-matrix not identifiable:** a 3×3 exponent matrix can't be identified from one
  anchor (r≈0.19). **Constrain: equal facet exponents within a domain** (justified — von Rueden's 4 dims carry
  ~equal weight), **2 facets, single prowess, defer the full matrix + c_influence** (→ Q1/Q2 answered minimal).
- **[MINOR→fixed] RT-7/8 nesting statistical, not bit-for-bit:** the conception lottery is a new RNG consumer;
  rollback is N-seed statistical unless the lottery draws zero RNG at `mate_choice_strength=0`. §4.
- **[MINOR→fixed] Literature:** keep `paternal_provision_frac` **PROVISIONAL/unset** pending the Marlowe ★
  extraction (don't ship an invented default). And **realign §2.2** — R-18 found the channel is *spatial
  competition near K*, not temporal meat variance, so prowess-from-meat-overflow may be weaker than the
  costly-signaling framing implies (measure it).
- **[MINOR] RT-6 sex-division:** re-confirm growth-phase e₀ at `sex_division>0`; note **female-prowess
  degeneracy** (women earn only low-variance forage → near-constant female prowess; intended if male prowess
  is the point, but state it).
- **[noted] Refactor scope:** the scalar→vector change touches **6+ `cred`-read sites** — `compute_harvest_shares`
  (`substrate.py:45`), `diffusion_select_target` `w_self` (`:80`), `occ_wsum` ×2 (`phase1_model.py:292,313`),
  the inheritance copy (`:522`), the founder seed (`:181`), and the `starv_cred_this_step` diagnostic (`:407`);
  enumerate all in build-step 1. And **prowess `gain` needs a NEW per-male provisioning-output accumulator**
  (none exists today — `provision_pool` is mother→child only): a real new flow, not a tweak.

**Net:** 3 MAJORs resolved in design (no BLOCKER); the build order (§3) stands with these gates folded in.
