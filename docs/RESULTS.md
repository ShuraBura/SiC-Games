# SiC Games — Results

**The ONE question:** "What do we actually *know* now?" — established findings, in prose (charter §2, home 8).

**Discipline:** append-only ledger. A finding is recorded here when it is established (a hypothesis resolves, or a measurement settles a question). Supersede with a dated note, never silently rewrite. Values live in PARAMETERS.md; runs/reports are indexed in ARTIFACTS.md — this home states *what we know*, with pointers.

---

## R-1 — H1(ii): strategy resilience inverts the naive prior (Sugarscape-era result — NOT a standing confirmed finding on Phase 1 substrate)

**Origin:** originally registered as the project's central hypothesis **H1(ii)**; routed here on resolution (2026-06-05 reorg). The re-test on Phase 1 terrain + resource infrastructure is **pre-registered in `HYPOTHESES.md §H1ii-RETEST`**.

**⚠ SUPERSEDED PENDING RE-TEST (2026-06-13):** The Phase 0 Sugarscape-era confirmation below is a historical record, not a standing live finding. Phase 1 rebuilds the resource ecology on a continental terrain generator; the prior result does not carry forward to the new substrate. The inversion may hold, reverse, or become conditional — the re-test in §STAGE-RECAL (ROADMAP) will adjudicate. Do NOT cite this as a current confirmed result.

**Phase 0 finding (Sugarscape substrate, flat homogeneous world):** Of the two civilisational strategies, one is more resilient to periodic resource shocks than the other. **Result: Si goes extinct at A=0.75 / T=200 (both seeds, by t≈1500), while C persists** — the resilience comparison *inverts* the naive "individualist self-reliance is robust" prior; the inversion was robust to a more capable Si (Stage 5.1 Si Cred, 5/5 seeds).

**Mechanism (Phase 0):** the inversion is structural on the Sugarscape substrate — Si's dormancy mechanic creates a synchronised mass-death cliff when trough duration exceeds T_dormant_max (Si T* ∈ (68,87) at A=0.75; C T* > 500). This mechanism is substrate-dependent: terrain heterogeneity is expected to alter the resource-access dynamics that produce the cliff.

**Evidence:** Stage 5 multi-seed ensemble — see ARTIFACTS.md (`outputs/stage5/report_stage5.html`). Si Cred redesign (Stage 5.1) did not rescue Si on the Sugarscape substrate.

**Re-test registration:** `HYPOTHESES.md §H1ii-RETEST` (2026-06-13). OWE-14 (≥3 seeds, calibrated N_carry) is the minimum re-confirmation before the 100×100 scale can be trusted.

---

## R-2 — A-3 First-Light: a placement-independent food-capacity ceiling, but a FROZEN demographic equilibrium

**Origin:** A-3 First-Light Shakedown (exploratory, not a gate), 2026-06-18. C agents on Phase-1 terrain, rivalrous Stage-6.0a multi-occupancy substrate, CC-1 cell-capacity field, opt-in reproduction. Narrative: `handoffs/SiC_Games_Progress_Report_2026-06-18.md`; data + index in ARTIFACTS.md.

**What we know:**
1. The terrain economy has a **clean, placement-independent food-capacity ceiling.** Two different founder placements both equilibrated to **~133,400** agents on 100×100 (spread ~0.06%; ≈97% of the 138,021 per-cell-K terrain ceiling; settling onset ~step 173). Rails clean, determinism PASS. A **terrain-driven attractor**, not a placement artifact.
2. **The equilibrium is demographically FROZEN — births and deaths both → 0 at carrying capacity.** The model's only death causes are density-dependent starvation (transient — stops once agents spread to intake≈burn) and a hard senescence age-cap (never fires / fires as a synchronized wave). **The model lacks density-independent baseline mortality.**

**⚠ PROVISIONAL:** the ~133.4k figure is the *food-capacity ceiling*, not the demographic carrying capacity. Under real demographics (birth–death balance) it will be **superseded, likely lower**. CC-1 capacity (Tallavaara NPP density) is itself provisional. Not comparable to the Sugarscape/OWE-1 `N_carry` scale-setting choices — different substrate.

**Consequence:** motivates the demographic-mechanics stage (`blueprints/phase1/SiC_Games_P1_Demography_Siler_Blueprint.md` — Siler mortality + IBI reproduction, Aché-gated).

---

## R-3 — Step-1 demography: the frozen equilibrium is fixed; Aché vital rates reproduced

**Origin:** Demographic stage Step-1 (non-spatial Aché calibration), 2026-06-18. Fixed Aché Siler mortality (Gurven & Kaplan 2007; M-1) + IBI female reproduction, well-mixed, terrain-free, all modulators off. Artifact: `outputs/phase1_demography_calib/report.html` (+ `results.json`).

**What we know:**
1. **The A-3 frozen equilibrium is fixed.** With baseline (Siler) mortality the population turns over continuously: **CBR 61 / CDR 27 per 1000/yr, births ≈ deaths > 0** (A-3 had births = deaths = 0).
2. **The FIXED Aché Siler reproduces the published life table** (a verification, not a fit): e₀=36.5, e₁₅=38.3 remaining yr, e₄₅=21.3, modal adult death=71, MRDT=6.7 — matching Gurven & Kaplan / Hill & Hurtado.
3. **Fertility calibrated to the Aché:** IBI = 37.0 mo, completed TFR = 7.9 (Aché 37 / ~8).
4. **r≈0 is a Step-2 property, not Step-1.** Aché fertility under Aché mortality necessarily yields a **growing** population (realized **r = +3.3%/yr**; the real forest-period Aché grew ~2.5%). Forcing r≈0 demands unrealistic fertility (TFR≈3, IBI≈68). The density-dependent terrain/disease modulators bring r→0 at carrying capacity in Step-2. **Refines the blueprint §8 gate.**

**M-3 sex-split LANDED (2026-06-18):** sex-specific Siler via the Hill & Hurtado 1996 (Ch. 6) forest-period mortality-risk ratios — childhood M:F = 0.71 (female-higher infant/juvenile term `a1`; Aché sex-biased infanticide/neglect), adult M:F = 1.47 (male-higher Gompertz `a3`), Makeham `a2` shared → female→male crossover in adolescence, as the monograph reports. Maternal mortality **folded into the all-cause female schedule** (approach (ii); the maternal-removed approach (a) is deferred — needs the Aché maternal rate). Vital rates **hold**: IBI 37.0, TFR 8.0, r = +3.3%/yr. 11 demography tests; full suite **442 passed**.

**Open:** approach-(a) maternal-removed female fit; realized r (+3.3%) still above the Aché ~2.5% (fertility at the high end of the band). The age-specific sex curves live in monograph figures (not machine-readable), so the ratio-split is a level approximation that preserves the sex-average = the validated both-sexes life table.

---

## R-4 — Step-2 2a-pre: food density-dependence stabilizes the growing population (B-1 resolved)

**Origin:** Demographic stage Step-2, stage 2a-pre stability test, 2026-06-18. Sex-specific Siler + IBI (modulators OFF, energetic fertility modifier OFF — strict test) on a 40×40 terrain sub-window with the CC-1 food economy; 3 seeds × 2500 steps. Artifact: `outputs/phase1_demography_step2/report.html`.

**What we know:** the Aché-calibrated **+3.3%/yr population settles smoothly** against the density-dependent food wall — all 3 seeds plateau at **~94–95% of the food ceiling**, settled-peak 1.01× / settled-trough 0.90×, no extinction, no oscillation, no collapse. **BOUNDED SETTLING.** The red-team's B-1 concern (intrinsic growth + saturating resource + mortality *lag* → overshoot/collapse) does NOT materialize because the food brake is **fast (~1 step = `reserve_full/burn`)**: excess density crashes reserves to the starvation floor within ~1 month, so the population approaches equilibrium logistically rather than overshooting. **Food density-dependence alone stabilizes the population**; the Step-2 terrain/disease modulators shift the equilibrium *down* and sort the population (2b), not stabilize it.

**Consequence:** the Step-2 blueprint's central mechanism (red-team B-1) is **validated**; the approach is sound. Step-2's only remaining lock gate is the 2b knob-anchoring (Tallavaara pathogen SEM, μ_max, risk scale).

---

## R-5 — Step-2 modulators are inert on the constant economy; the 2b/2c "pathologies" were a read-timing bug

**Origin:** Step-2 2b/2c investigation + diagnostic, 2026-06-19. Artifacts: `outputs/phase1_demography_step2/`.

**What we know:**
1. **The 2b "synergy dominates → CC 19%" and the 2c "economy pins reserves at the floor" were a single bug**, not real dynamics. The synergy modulator read the reserve **post-burn** (`a.wealth` after the monthly burn), which for *any* well-fed agent equals `reserve_full − burn = 100k − 75k = 25k` — right at the 20k floor. So synergy fired ~2.4× for the *entire* well-fed population (a flat mortality multiplier in disguise), and the post-burn snapshot made fed agents look starved. **Diagnostic:** agents are well-spread (occ/K ≈ 0.07; zero cells near capacity) and **fully fed** (post-harvest reserve = 100k). **FIXED:** synergy + energetic-fertility now read the **post-harvest** reserve → `synergy_mult = 1.0` for fed agents (verified). `reserve_full = 100k` is ~physiologically right (~1.3–1.5 mo of fat); the bug was timing, not magnitude.
2. **On the current constant / undepletable / aseasonal economy, all three `a2` modulators are inert** (agents always fully fed → synergy 1; agents spread → density ~1; risk mean-normalized small). The demographic carrying capacity is therefore ≈ the **food ceiling with continuous turnover** (the 2a-pre baseline, R-4).
3. **The modulators need nutritional VARIANCE to be meaningful** — lean seasons, depletion, local scarcity, provisioning load. `μ_max` is not calibratable until then.

**Consequence:** the demographic *mechanisms* (Siler + IBI + wired-but-dormant modulators) are validated; the demographic CC on this economy is the food-ceiling baseline. The rich regulation, `μ_max` calibration, and the emergent-child-mortality validation (TARGETS) await the **Resource-Ecology stage** (seasonality + depletion + per-class reserves + family/provisioning).

---

## R-6 — Seasonality regulates the carrying capacity to the lean-season bottleneck, but does NOT create equilibrium nutritional stress (depletion needed)

**Origin:** Resource-Ecology Phase A.1, 2026-06-19. Artifact: `outputs/phase1_resource_ecology/report_2d.html`.

**What we know:** a uniform seasonal harvest multiplier (s_min=0.4) **regulates the demographic carrying capacity down to the lean-season bottleneck** — equilibrium population drops from **95%** of the peak food ceiling (constant control) to **37%** (≈ the lean-season capacity; Liebig's law of the minimum). This is a *desired* result: seasonality pulls the demographic CC well below the peak food ceiling. **But it does NOT create equilibrium nutritional stress** — at the lean-season-limited density, agents are fed year-round (mean reserve stays ~full 99–100k; synergy stays ~1.0, inert; no seasonal synergy/mortality pulse). The population self-adjusts to the lean-season capacity — the fast ~1-step food brake + perfect diffusion spreading cull any overshoot *within* the lean season — so at equilibrium no one is under-fed.

**Consequence:** confirms the red-team — **seasonality alone is insufficient to make the demographic modulators bite.** Persistent, *inescapable*, heterogeneous scarcity requires **depletion** (Phase A.2): a depleted cell that regrows slowly cannot be instantly fled, so some agents stay under-fed. Seasonality gives a lower, realistic CC; depletion gives the stress.

## R-7 — Mean-lowering mechanisms (seasonality, depletion) lower the carrying capacity but CANNOT make the graded modulators bite; per-agent nutritional variance needs dependency/provisioning or constrained movement

**Origin:** Resource-Ecology Phase A.2, 2026-06-19. Artifact: `outputs/phase1_resource_ecology/report_2e.html`.

**What we know:** adding **depletion** (per-cell freshness `f`; harvest draws it down ∝ occ/K, slow logistic regrow) — on top of (optionally) seasonality — lowers the demographic CC *further*: depletion-only to **26%** of the peak ceiling (cells settle at freshness **0.32** — visibly depleted), seasonal×depletion to **17%** (freshness 0.56). **But synergy stays ~1.0 and ZERO agents are under-fed** (fraction with `synergy>1.2` = **0%** in both). The cells are heavily depleted, yet every *survivor* is fed.

**Diagnosis (structural):** the agents' per-capita-yield-maximizing movement (an **ideal free distribution**) + the fast ~1-step food brake means the population **thins until per-capita intake ≈ maintenance everywhere**; survivors sit at full reserve and the margin is culled by starvation (a sharp threshold). **No agent dwells in the "chronically lean but alive" band where the graded synergy/disease modulators act.** A mechanism that only lowers the *mean* food (seasonality R-6, depletion R-7) therefore only lowers the CC — it cannot generate the per-agent *variance* the modulators grade. (Compounded by a near-bang-bang reserve: intake≥burn refills to full, intake<burn drains to the floor in ~1 step, so the intermediate-reserve zone is transient.)

**Consequence:** the per-agent nutritional variance the modulators — and the T-4 emergent-child-mortality test — require must come from **structure the ideal-free-distribution cannot wash out**, not from more resource-field tuning: **(A) dependency / provisioning** — children, elderly, pregnant/lactating have requirement > own foraging return, so scarcity concentrates on *dependents first* (the real locus of hunter-gatherer seasonal child mortality; the T-4 prerequisite); **(B) constrained movement** (territoriality / kin / imperfect info) trapping some agents on poor cells; **(C) stochastic foraging returns** (feast/famine). Seasonality + depletion remain the **CC-setting backdrop**. The stage's unblock is the *source-of-variance* choice.

## R-8 — Constrained movement is a clean mobility knob but does NOT create per-agent variance; the variance is STRUCTURAL (dependency), not spatial — and the limiter is the bang-bang reserve

**Origin:** Resource-Ecology Phase B, 2026-06-19. Artifact: `outputs/phase1_resource_ecology/report_2f.html`.

**What we know:**
1. A **move cost** (`move_cost_flat`, a decision friction on cell utility — *not* a wealth debit) is a clean, monotone **mobility control**: residential moves/yr 0.93 → 0.48 → 0.27 → 0.15 and range 2.4 → 1.3 cells as move_cost rises 0 → 0.35×burn. The substrate has a working mobility knob.
2. **But it creates NO per-agent nutritional variance:** the under-fed fraction (synergy>1.2) stays **0.0% at every level**, and occupancy heterogeneity is **invariant** (occ_CV ≈ 0.50 throughout). Stickiness cuts churn but leaves the equilibrium spatial occupancy — and everyone's fed status — unchanged. **Spatial trapping is ruled out as the variance source.**
3. **Diagnosis (deeper than R-7): the limiter is the near-BANG-BANG reserve, not the IFD per se.** Under the food economy an adult is either fed (intake ≥ burn → reserve pinned at the 100k cap → synergy 1) or culled (intake < burn → drains to the floor in ~1 step). There is **no stable "chronically lean but alive" band** for the graded modulators to act on, and movement constraints don't manufacture one — a stuck, under-fed adult dies fast rather than dwelling lean. Only **dependents** — who cannot forage to maintenance, are partially provisioned, and drain slowly — can be sustained in the lean band. The variance the modulators (and T-4) need is **structural (who can/can't self-feed), not spatial.**
4. **Incidental realism finding:** the model is **under-mobile** at equilibrium — baseline 0.93 residential moves/yr vs the Binford 2001 / Kelly 2013 forager envelope (~10–40/yr); move_cost only lowers it. Real HG mobility is resource-**tracking** (seasonal/depletion-driven relocation), damped here because the equilibrium food field is near-stationary. The lit-realistic move_cost is ≈0 (baseline); restoring HG mobility is a resource-driver realism issue, **separate** from the variance question.

**Consequence:** B cleanly rules out spatial trapping and confirms the needed variance is structural → **provisioning / dependency (Phase C) is the unblock, now empirically forced.** `move_cost` is banked as a mobility knob (held at the realistic ≈0); precise Binford tuning deferred to a resource-driver realism pass. Phase C must also give dependents a **graded** nutritional state (slow drain), since the bang-bang adult reserve is itself part of why no lean band exists.

## R-9 — C.1: the childhood deficit lowers the CC but doesn't wall recruitment — because newborns inherit an ADULT-sized reserve that masks it

**Origin:** Resource-Ecology Phase C.1, 2026-06-20. Artifact: `outputs/phase1_resource_ecology/report_2g.html`.

**What we know:** turning on graded `η(age)` production + age-scaled `c(age)` consumption (provisioning OFF — the Kaplan 2000 childhood deficit) drops the demographic CC to **~26%** of the children-as-adults baseline (eq 1504 vs 5824). The deficit is real and the machinery works, and the **444-suite stays green** (opt-in via `lh_cfg`; the validated core is untouched — baseline grows with normal R-3/R-4 dynamics). **But it does NOT wall recruitment as predicted:** the population settles lower but *stable*, with a normal age structure — children self-rescue at the reduced density (uncrowded cells → large per-capita shares). **Root cause (artifact flushed out by C.1):** in the IBI birth path newborns inherit `reserve_full` = **100k kcal — a full ADULT fat reserve (~1.3 months of adult maintenance)**, physiologically absurd for a neonate, which buffers the entire early-childhood deficit. Children coast on an inherited adult reserve instead of depending on anyone.

**Consequence:** the realistic fix ties to **per-class reserves (MR-1 / Pontzer 2012)** — scale the newborn endowment to body size (small). Then the deficit bites immediately and **mother-linked provisioning (C.2) becomes load-bearing** — the dependent class can dwell lean (the variance + the T-4 prerequisite). C.1 also confirms the graded-η / age-scaled-consumption edits leave the validated demographic core intact.

**C.2a CONFIRMATION (2026-06-20, `report_2h.html`):** age-scaling the reserve (floor + cap + birth endowment) by body size (`reserve_min`=0.1 at birth → 1.0 at 15 yr; new `reserve_scale()`, opt-in, 444 green) makes the deficit bite as predicted. Three-way on the constant economy: baseline (children=adults) eq 5824 growing; C.1 (deficit, **adult**-sized reserves) eq 1504 stable (no wall, reproduces R-9); **C.2a (deficit, body-sized reserves) → EXTINCTION (pop 0 by ~yr 100)** — a body-sized neonate cannot self-buffer a month of maintenance, so without provisioning recruitment fails totally and the founders age out. The adult-sized reserve was the *only* thing masking the deficit. Provisioning (C.2b) is now strictly load-bearing.

---

*End of RESULTS — seeded 2026-06-05 (R-1 routed from former hypothesis H1(ii)). Append-only.*
