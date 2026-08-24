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

## R-10 — The A→B→C arc resolves: provisioning + seasonality produce emergent SEASONAL CHILD MORTALITY — but via the hard floor, not the graded synergy modulator

**Origin:** Resource-Ecology Phase C.2b (+ A.1), 2026-06-20. Artifacts: `outputs/phase1_resource_ecology/report_2i.html` (provisioning rescue), `report_2j.html` (seasonal pulse).

**What we know:**
1. **Mother-linked provisioning rescues the dependent class.** Each mother's harvest overflow (above her age-scaled cap, otherwise wasted) is redirected to her dependent children. On the depletion economy this takes the population from C.2a **extinction (0)** to a **stable ~5000 with a normal 34%-juvenile age structure** (`enable_provisioning`, opt-in, 444 green). Fix en route: `reserve_min` must equal `cons_min` (a neonate's cap must cover ≥1 step's burn, else the monthly timestep makes a dependent unsustainable even when fully provisioned).
2. **On a self-adjusting economy provisioning over-smooths** — mothers sit at the cap with overflow ≫ child need, so children are always fully provisioned (juvenile under-fed ≈ 0%). The dependent class exists but nothing squeezes it (the A/B over-smoothing, now for children).
3. **Seasonality + provisioning BITES — emergent seasonal child mortality.** Adding a lean season (s_min=0.4) drives a clean annual child STARVATION pulse: **lean-trough 34 starvation deaths/step vs good-season 0.3 (≈68× pulse)**, falling on *children* (n_juv drops in each trough) while *adults stay fed* (they self-adjust to the lean-season bottleneck, A.1). Children are the buffer that absorbs the seasonal squeeze — exactly the real hunter-gatherer seasonal child-mortality pattern. **This is the per-agent/per-class variance the entire A→B→C arc was chasing** (A.1/A.2/B/C.2b-constant all over-smoothed; only dependent-class + squeeze together work).
4. **It runs through the hard floor, NOT the graded synergy modulator.** A squeezed child plummets from full to the starvation floor in ~1 step (the bang-bang reserve, R-8, applies to children too — `reserve_full·scale ≈ 1.3 months' burn`), too fast to *dwell* in the synergy zone, so graded synergy>1.2 stays ~0% among survivors and the deaths register as "starvation."

**Consequence:** the mechanism (seasonal provisioning failure → child mortality) is real and matches the HG *rate/seasonality*. But the Aché child-mortality *cause profile* (Hill & Hurtado) is **disease-dominated, malnutrition synergistic — not literal starvation**. So for T-4 fidelity the mortality should route through the **graded synergy/disease channel**, which requires synergy to read a **smoothed/lagged body-condition signal** (immune competence degrading over weeks–months) rather than the instantaneous bang-bang reserve. That is the next modeling decision before the T-4 emergent-q(x)-vs-Aché validation.

## R-11 — S0+S1 (graded nutrition→disease) is correct-but-inert; the fine cause-channel is over-engineering for total mortality — coarse split kept, fine deferred to T-4

**Origin:** Biome-Mortality S0 (body-condition) + S1 (child-priority shortfall-sharing), built + red-teamed (sub-agent `a1f44d9c`), 2026-06-20. Artifacts: `outputs/phase1_resource_ecology/report_2k.html`, `report_2l.html`.

**What we know:**
1. **S0 (lagged body-condition EMA, synergy reads it) + S1 (mother shares her reserve down to `provision_self_keep`·cap) are correctly implemented (444 green) but INERT** for the graded-disease purpose. **Reason (code-grounded, red-team):** provisioning **tops children to their cap** (`need = full·scale − wealth`), so any provisioned child sits at full reserve → condition pinned ≈1.0; the only under-cap children hit the starvation floor in ~1 step (the R-8/R-10 bang-bang reserve) before the α=0.25 EMA can walk down → surviving juveniles always read ≈1.0, synergy(condition)=1, no graded disease. It is **R-10 #4 restated.** The self-regulation attractor (R-5…R-8) compounds it: surviving mothers are by construction the ones who can cover their children, so children rarely dwell lean.
2. **S1 still earns its place:** child-priority shortfall-sharing cut lean-trough child starvation **33.7→18.2/step** (mothers absorb more of the squeeze); the residual ~18 is orphans / failed-support mothers (= the data's *infanticide* cohort, not starvation). So S1 drives child *nutritional* death toward the Aché ≈0.
3. **For the supervisor's deliverable (TOTAL mortality by biome, not cause channels), the fine graded-nutrition→disease channel is OVER-ENGINEERING a cause label.** The model already produces (R-10) emergent seasonal child mortality at the right rate / seasonality / cohort (weaning-age) / trigger (provisioning shortfall); routing it from the "starvation" bucket to a "disease" bucket the total sums over anyway changes no q(x) or biome total.

**Decision (supervisor-confirmed 2026-06-20):** **keep S1 ON** (protects children → low nutritional death), **bank S0 OFF** (opt-in `enable_condition` for a future T-4 effort), take the **coarse** disease-vs-starvation split (Siler-baseline bucket vs floor) as a near-free byproduct validated in the Biome-Mortality stage, and **proceed to the pathogen biome channel** (the gradient comes from an *exogenous* per-biome `a2` multiplier — no dwell problem). The **fine** mechanistic synergy is deferred to **T-4** (the mark is left there with the two-part fix it needs). The biome gradient never depended on this.

## R-12 — Multi-biome: the pathogen channel works, but biome mortality is dominated by food-starvation (over-strong vs data) — the pipeline + the honest divergence

**Origin:** Biome-Mortality S2/S3.5/S4, `outputs/phase1_biome_mortality/run_2m_multibiome.py`, 2026-06-20. 3 isolated populations (arid/temperate/lush; NPP 0.077/0.185/0.293), each biome's NPP driving food (CC-1) + pathogen (S2), bracketed `pathogen_gamma` {0, 0.5, 1.0}, **period life tables** (age-specific death rates → e₀, decoupled from growth).

**What we know:**
1. **The pipeline works** (multi-biome, isolated, per-biome life tables) and **the S2 pathogen channel works**: lush (high-NPP→high-pathogen) e₀ falls **43.8→32.1 yr** and its population collapses **11,936→1,955** as γ 0→1; arid (pathogen_mult<1) is spared → an emergent **food-disease trade-off** (productive biome = most food but most disease).
2. **But the DOMINANT biome-mortality driver is FOOD-starvation, not pathogen.** At **γ=0** (no pathogen, identical Siler) e₀ already swings **arid 23.8 / temperate 35.8 / lush 43.8** (CDR 48/33/26) — heavy density-dependent **starvation** in the food-poor biome; temperate ≈ recovers the validated Siler e₀ (36.5).
3. **This food-driven gradient is UNREALISTICALLY STRONG vs the data.** Real foragers have *broadly similar* e₀ across biomes (!Kung ~36, Aché ~37, Hadza ~32–43; weakly biome-graded, disease/violence-dominated). The model's ~20-yr arid–lush e₀ span — via *starvation*, which the data says is ≈0 — is the recurring **R-5…R-11 acute-food-margin over-mortality** surfacing as an over-strong biome gradient.
4. **Measurement caveats:** realized mean age (living OR at-death) is growth-confounded; the period life table removes most of it but retains some upward bias in fast-growing populations (lush γ=0 e₀ 43.8 > Siler 36.5); the pathogen e₀ signal is entangled with the food/starvation/density dynamics.

**Consequence:** total q(x) by biome IS produced (the deliverable), but **food-starvation-dominated and over-strong**, with the (data-anchored) pathogen channel a real but *secondary* gradient — all **bracketed + exploratory** (NPP-proxy, no CL-1 climate, no validated fit). To make biome mortality realistic (broadly similar across biomes, disease-dominated), the **food-starvation over-mortality must be tamed** (the R-10/R-11 self-regulation/acute-margin + child-priority work) so the disease channels become the driver. This is the deep recurring issue, now quantified at the biome scale.

## R-13 — Density-disease DOES regulate (the make-or-break passes): graded disease holds r→0 below the food ceiling, starvation→0 — the Step-2 design finally works

**Origin:** Biome-Mortality density-disease regulation test, `outputs/phase1_biome_mortality/run_2n_density_regulation.py`, 2026-06-20. Temperate biome, δ-sweep of the density-disease free lever.

**What we know:** turning ON `enable_density_disease` and sweeping δ — at δ=0 the population sits at the food ceiling (18,535) with **49% starvation** (the R-12 starvation-regulated baseline); at **δ=4 it settles at 10,463 (well below the ceiling) with starvation → 0%**; δ=8 → 5,979, δ=16 → 2,871, all 0% starvation. So **graded disease regulates the population below the food ceiling, drives r→0, and collapses the starvation fraction 49% → 0%** — mortality becomes **disease-regulated, not starvation-regulated** (the realistic regime; the data's regime).

**Why it bites when depletion / seasonality / synergy all washed out (R-5…R-12):** agents are **confined to the finite food patch** (food exists only there), so they cannot spread away from each other indefinitely — local cell density rises *with* the total population, and `density_mult` engages. The self-regulation attractor has **no escape hatch** here. This is the structural difference, and it realizes the original Step-2 design (R-3: density-dependent disease brings r→0 at the carrying capacity).

**Consequence — the path to realistic biome mortality is open.** δ is the calibration knob (≥4 for starvation→0; the equilibrium density ~0.04–0.13/km² spans the Tallavaara forager band). **Next:** calibrate δ to the forager e₀ + density, then re-run the multi-biome sweep WITH density-disease ON → expect **broadly-similar e₀ across biomes** (disease-regulated, no starvation) with the **pathogen productivity gradient on top** — matching the data (vs the R-12 starvation-dominated over-gradient). The supervisor's "turn on density-disease" was correct.

## R-14 — Scale resolution: per-agent variance is non-physical here (intra-band), the modulators were measuring the wrong level; the operative variance is inter-band/biome, and individuality lives in the Cred/sharing rule

**Origin:** supervisor design closure, 2026-06-20. Resolves the recurring "modulators inert" frustration (R-5…R-13) and the agent-vs-density architecture question. Full architecture record: MODEL_SPEC §4.7.

**What we know (the reframing):**
1. **Per-agent (intra-band) nutritional variance is NON-PHYSICAL in this model, and that's correct.** Within a cell the harvest is split **per-capita** (`compute_harvest_shares`, kappa=0), and over a 1-month step a band is fed or not *as a unit* — individuals do not starve individually. So the nine "modulators inert / under-fed ≈0%" results (R-5…R-13) were **measuring a quantity that should be ≈0**, not failing to find a real one. The cell **IS** the band (the sharing unit).
2. **The operative variance is INTER-BAND / INTER-BIOME** — between bands in different biomes, scaled by band size / population density — which is exactly what **R-12/R-13 produced** (the arid↔lush mortality gradient; density-disease regulating per biome).
3. **Band-level starvation is a RARE / EXTREME-EVENT mode, not the equilibrium regulator.** R-13's density-disease holds the band below the food ceiling (r→0, starvation→0). Mass starvation belongs to the catastrophe seam (§4.1.7), not the steady state.
4. **Per-agent variance is STRATEGY-SPECIFIC — and that is where individuality is preserved.** The within-band sharing rule is the dial: **Si / egalitarian (kappa=0) → equal split → no per-agent variance** (the baseline we built, R-1…R-13); **Carbon / hierarchical (kappa>0) → `(phi+ε)^kappa`, Cred-weighted shares → per-agent variance BY STATUS** (high-Cred eat more, low-Cred squeezed). So R-5…R-13 is the **Si baseline**; the C case has real per-agent (status) variance. Individuality is NOT erased by band-level ecology — it lives in the Cred/contest sharing.
5. **The C-vs-Si anti-fragility (R-1) IS the individualism**: under shock, C's hierarchy channels scarce food to the high-Cred core → the core persists; Si's equal sharing → everyone crashes together (the dormancy cliff). So "averaging out" is the *Si failure mode*, not a modeling choice — lumping the *ecology* to band-level does not touch the C-vs-Si difference, which is the *sharing rule on top of* it.
6. **S0/S1 (the banked per-agent condition/provisioning machinery, "over-engineering" per R-11) is actually the Carbon mechanism** — inert under equal sharing, **live under Cred-weighted sharing** (low-status → chronically under-fed → synergy/disease bites differentially). Banked for the right reason, not wasted.

**Scale decision (the architecture):** keep **individual agents** (the Cred/strategy/resilience core is path-dependent — Matthew effect — + discrete — small-band stochasticity — + emergent — the R-1 cliff — exactly what mean-field DENSITY smooths away; and agents are affordable at HG scale) with the **ecology running on band/biome-level rates**. Fallbacks (band-as-super-agent for continental/deep-time scale; mean-field as a fast *surrogate* only) are **deferred to concrete triggers**; we keep the **ecology-rates ↔ individual-strategy boundary clean** (cheap discipline, not premature architecture) so a future coarsening is a swap-the-consumer job. Details + triggers: MODEL_SPEC §4.7.

**Consequence:** the demographic substrate (R-1…R-13) is the **validated Si/egalitarian ecological baseline**; the **C/Cred individuality is the next real layer** (kappa>0 + the demographic core) — the C-vs-Si demographic resilience test, the project's central question, now on a real ecology instead of Sugarscape. The per-agent-variance chase is closed (it was the wrong level for Si; it's the *point* for C).

## R-15 — δ calibration lands the model at a Hiwi-like e₀ (~28), ~8 yr below the Aché (37) it's parameterized to — the double-count; de-warfaring is the prerequisite for a clean calibration

**Origin:** Biome-Mortality density-disease δ calibration, `outputs/phase1_biome_mortality/run_2o_delta_calibration.py`, 2026-06-20. Temperate biome, period life tables + density.

**What we know:** sweeping δ — as it rises, starvation falls (49%→0% at δ=4) and **e₀ rises to a peak of 28.5 yr at δ=4, then falls** (δ=8 → 25.1); density falls monotonically (0.116→0.037/km²). **No δ satisfies all three forager constraints at once** (e₀ 27–43, density 0.1–0.5, starvation≈0): low δ → realistic density but heavy starvation (24–49%) + low e₀; **δ≈3–4 → forager-range e₀ (27–28.5) + borderline density (0.065–0.083) + starvation 0–9%**; high δ → no starvation but density too low + e₀ falls. The recommended **δ≈3–4 is a HIWI-like regulated state** (e₀~28, disease-regulated) — realistic for a *low-end* forager but **~8 years below the Aché (37)** the Siler is parameterized to.

**The gap is the DOUBLE-COUNT:** density-disease is added **on top of the Aché-TOTAL Siler**, which already encodes the Aché's own mortality regime — so the regulation costs ~8 yr of e₀ (at δ=4, e₀ drops from the Siler's 36.5 to 28.5). The fix is the **mean-preservation / DE-WARFARING** (deferred, §4.6.1): strip the ~50% frontier violence from the baseline (e₀≈42–44) so density-disease brings it down to ~34–36, matching the Aché *and* supporting a higher (Tallavaara-range) density.

**Consequence:** **de-warfaring is the PREREQUISITE for a clean δ calibration** — the order is **baseline-first** (de-warfare → re-fit Siler → re-calibrate δ → multi-biome). δ is PROVISIONALLY ~3–4 (the forage-only Hiwi-like regulated state). The δ↔(starvation, density, e₀) trade-off curve is itself a finding: the forage-only economy is *mortal* — regulating the +3.3% growth costs ~8 yr of e₀ whichever way (starvation or disease).

---

## R-16 — De-warfaring DOESN'T change the regulated e₀ — R-15's double-count diagnosis was wrong: at r=0 equilibrium e₀ is pinned by FERTILITY, not by the natural-mortality Siler. The Aché's e₀=37 is a growth-phase snapshot, not a stationary value.

**Origin:** Biome-Mortality δ re-calibration on the **de-warfared** baseline (ACHE_FOREST_NATURAL, natural e₀=42.7), `outputs/phase1_biome_mortality/run_2o_delta_calibration.py`, 2026-06-20. Same temperate biome / period life table / δ-sweep as R-15, only the Siler coefficients changed (Aché-total e₀=36.5 → de-warfared e₀=42.7, +6.2 yr).

**The result FALSIFIES R-15's prediction.** R-15 predicted de-warfaring would lift the regulated e₀ into the Aché range (~34–36). It did not. Side-by-side at the regulating δ=4:

| baseline | natural e₀ | regulated e₀ (δ=4) | density | starv |
|---|---|---|---|---|
| Aché-total (R-15) | 36.5 | 28.5 | 0.065 | 0% |
| de-warfared (R-16) | **42.7** | **28.5** | 0.065 | 0.1% |

A **+6.2 yr** change in the *natural* baseline moved the *regulated* e₀ by **0.0 yr**. The whole de-warfared sweep tracks R-15 within noise (peak e₀ 28.5 @ δ=4, falling either side; no δ hits all three targets).

**Why — the regulated e₀ is fertility-pinned, not mortality-pinned.** At a carrying-capacity equilibrium the population is held at **r=0**: deaths must exactly balance births. Density-disease is the free lever that supplies *whatever excess mortality* is needed to reach r=0. Lowering the natural-mortality floor (de-warfaring) just means density-disease must work *harder* — and it eats back exactly the e₀ that de-warfaring added. The two cancel. **At r=0 the equilibrium life table is determined by the FERTILITY schedule (IBI/TFR), not by the natural-mortality coefficients.** This is the classic stationary-population identity: NRR=1 ties e₀ to TFR. A forager schedule with the Aché's high fertility, held stationary, *must* have a low e₀ (~25–28) regardless of the natural Siler.

**The reframe — Aché e₀=37 @ TFR≈8 is a GROWTH-phase snapshot, not an equilibrium.** Those two numbers coexist in the ethnographic record only because the observed Aché were **growing** (r>0, below K), not sitting at carrying capacity. Our model regulates *to* K (r=0), so it correctly lands at the *stationary* e₀ for the Aché fertility schedule (~28), which is genuinely Hiwi-like. **The model is behaving correctly; the target was mis-specified.** To make the model sit at e₀≈37 at equilibrium you must **lower fertility (lengthen IBI)** — not lower mortality. De-warfaring (kept, OPT-IN, §4.6.1) is still a *cleaner* natural baseline, but it is NOT the lever for equilibrium e₀.

**Consequence / fork (SUPERVISOR DECISION):** the "calibrate δ to hit Aché e₀=37" goal is demographically incoherent at r=0 with Aché fertility. Options: **(A)** accept the stationary e₀~28 as correct and re-target validation to a *stationary* forager (Hiwi-like e₀ 27 is already in-range — the model may simply be *done* and correct); **(B)** calibrate to e₀≈37 by **lowering fertility** (longer IBI) and document that as the equilibrium-consistent schedule; **(C)** validate against the *growth-phase* by running the model below K (r>0, transient) and comparing the transient e₀. Re-running the multi-biome sweep on the current substrate would only re-confirm e₀~28 everywhere — **deferred pending this fork.** δ remains PROVISIONALLY ~3–4. → **Resolved by R-17: (B) rejected (launders an artifact into fertility), (C) done & confirms, (A) adopted as the equilibrium framing.**

---

## R-17 — Growth-phase validation CONFIRMS R-16: below K the model reproduces the Aché e₀ (38≈37) in the regime they were measured in; the equilibrium ~28 is a regime effect, not a coefficient failure. The model is correct in BOTH regimes.

**Origin:** Growth-phase validation, `outputs/phase1_biome_mortality/run_2p_growth_validation.py`, 2026-06-20. Density-disease **OFF**; period life table accumulated only over a **below-K window** (density ∈ [0.005, 0.040]/km², ≪ the δ=0 equilibrium ≈0.116); two baselines (Aché-total, de-warfared); 3 seeds pooled (~450k person-years each). Option C of the R-16 fork.

**What we know:** in the growth window (r ≈ +3.4–3.7 %/yr, starvation **0%**, density ≪ K) the period e₀ **recovers the input Siler**:

| baseline | input Siler e₀ | growth-phase e₀ | stationary e₀ (R-16) |
|---|---|---|---|
| **Aché-total** | 36.5 (ethnographic Aché 37) | **38.2** | ~28 |
| de-warfared | 42.7 | **45.1** | ~28 |

(Fine age bands required: the first pass with a wide 50–120 band read e₀ ~8 yr high — a known wide-band period-table bias in a young/growing age structure; refining to `[0,1,5,10,15,20,30,40,50,60,70,80,120]` brought 44.1→38.2 and 51.5→45.1, i.e. onto the input within ~2 yr. The residual ~+2 yr is the still-open 80–120 band + finite old-age sample.)

**Interpretation — the model is correct in BOTH regimes, and the e₀ gap is a *regime* difference it explains:**
- **Growth (below K):** mortality = the natural Siler; e₀ = 38.2 ≈ **the ethnographic Aché 37**, validating the substrate *in the regime the Aché were measured in* (growing, food-ample, starvation-free). De-warfaring is now *visible* and correct (45.1 ≈ 42.7) — confirming it sets the natural-mortality **ceiling**, which only the growth regime exposes (R-16: invisible at r=0).
- **Stationary (at K):** e₀ ~28, fertility-pinned (R-16). Genuinely Hiwi-like and in-range.
- The **~10 yr swing (38 growth → 28 stationary)** is the stationary-population identity in action, not a calibration miss.

**Resolution of the R-16 fork:** **(B) rejected** — forcing equilibrium e₀=37 by lowering fertility would launder a growth-phase artifact into a corrupted core input matching no real forager. **(A) adopted** — stationary e₀~28 is the *correct* value for a high-TFR forager at K. **(C) done** — growth-phase e₀≈37 validates the substrate. The two regimes together are a *stronger* result than hitting either number alone: the model spans the Aché (growth) and a Hiwi-like stationary state with one consistent parameter set.

**Standing caveat (orthogonal to e₀, the real next constraint):** at the starvation-free δ the *density* sits at 0.065/km², **below the Tallavaara forager floor (0.1)** (R-15/R-16). No e₀ choice fixes this — it is the **forage-only carrying-capacity ceiling**. The fix is the **game/meat stream** raising per-cell K (the "add game before calibrating" call). Game economy stays on the critical path for density, independent of the now-settled e₀ question.

---

## R-18 — Carbon validated on the demographic substrate: a Cred hierarchy concentrates mortality on the low-Cred periphery (aggregate κ-invariant) — but the channel is SPATIAL competition near K, NOT temporal meat variance (the CV=0 control did not vanish)

**Origin:** Carbon-on-substrate Tier-1 statistical validation, `outputs/phase1_biome_mortality/run_3b_carbon_statval.py`, 2026-06-21. Forest-Aché substrate (de-warfared Siler, meat_frac 0.55, δ=3), seeded heritable Cred (lognormal median 1, inherit σ=0.1), movement temperature held at σ_base (`carbon_cfg.kappa=0`). **N=20 seeds**, paired drift-control (κ>0 vs κ=0 share seeding/inheritance), sweep **κ∈{0,1,2} × meat-CV∈{0.0, 0.73, 2.24}** (control / forest / savanna). Direct measure: cred of starvation-deaths vs the living (`model.starv_cred_this_step`).

**The thesis HOLDS, strongly — the Carbon advantage is compositional.** At every κ>0 and every CV, κ-weighting **concentrates starvation on the low-Cred periphery**: cred-death-deficit **+0.07…+0.12, t=6.5–7.5**, monotone in κ; mean(cred|alive) lifts **+0.04…+0.09, t=2.4–4.2**; and **eq_pop stays κ-invariant** (~550–580 across all κ). So *who* dies is Cred-graded while *how many* is fertility-pinned (R-16) — the compositional anti-fragility (R-1) reproduced on real demography, for the first time off the Sugarscape toy. The κ=0 rows are a clean null (deficit t≈0).

**But a prediction was FALSIFIED — meat variance (G.3) is NOT the switch.** The pre-registered control was: at **CV=0** (deterministic meat) the gradient must vanish (the red-team's cap-pinning wash-out). **It did not** — CV=0, κ=2: Δmean_cred t=3.5***, death-deficit t=7.2. The advantage is **fully present without any temporal meat variance.**

**Why — the operative heterogeneity is SPATIAL competition near carrying capacity, not temporal "bad streaks."** Near K (δ=3) cells are crowded/poor, so per-capita shares are **sub-cap deterministically** — the cap-pinning argument (everyone fed to cap → surplus wasted) is false near K. Two Cred channels are active at CV=0: (a) the **meat harvest split** (high-Cred get more of a contested cell's meat), and (b) the **cell-occupancy movement contest** (`occ_wsum`/`w_self` are also `(cred+ε)^κ`-weighted → high-Cred secure better cells). Both are variance-independent. **G.3 only MODULATES**: ~~the effect **peaks at moderate CV** (forest 0.73: Δmean_cred +0.093, deficit +0.118) and is **lower at the extremes** — CV=0 (spatial only) *and* CV=2.24 (savanna: meat is mostly near-zero with rare over-cap jackpots → the band lives on egalitarian forage, so Cred-weight has little meat to bite on). Forest-like variance is the sweet spot.~~ **[SUPERSEDED by R-73, 2026-07-16 — no sweet spot; and "forest = 0.73" was mis-anchored.]** The re-anchored sweep (CV∈{0, 0.73, 1.97, 2.24, 2.92, 5.29}, N=20) finds the effect **FLAT** from 0.73 to 5.29 (κ=2 death-deficit +0.111…+0.132, all overlapping) — there is no peak, and 2.24 is not "lower". *That G.3 only modulates stands; that it has an optimum does not.* Separately, 0.73 was never forest's temporal CV (it is a spread across 7 species' means); forest's measured day-to-day CV is **1.97** (Aché, n=14,071) — which yields a statistically indistinguishable result, so this mis-anchoring did not affect R-18's conclusions.

**Consequence / caveats:** (1) This **revises** the "ordinary temporal meat variance / bad streaks" framing (scoping bp central finding, §4.5.5): the channel is spatial competition near K; G.3 is a modulator, not a prerequisite. (2) **κ Cred-weights two things at once** — the meat harvest split AND the movement contest. The validated result is the *combined* Cred-competition advantage; a clean **harvest-only vs movement-only ablation** is the next step to apportion them. (3) Decay/β OFF, Gini(cred) stable (~0.23–0.27, no runaway in 700 steps). δ=3 provisional. **This is the first recorded Carbon result on the substrate; Tier-2 (earned Cred + leadership) is the next stage.**

---

## R-19 — The full Carbon "lineage of chiefs" validated: a multifaceted heritable status hierarchy with prowess-weighted mate-choice reproduces the von Rueden status→RS r≈0.19, stays runaway-bounded, and keeps the R-18 compositional anti-fragility

**Origin:** Cred-vector + B+ paternity stage statistical validation, `outputs/phase1_biome_mortality/run_3c_bplus_statval.py`, 2026-06-21. Forest-Aché substrate (de-warfared Siler, δ=3, meat_frac 0.55, meat CV 0.73), **full B+** (lineage `cred` + earned sex-specific `prowess` + prowess-weighted mate-choice + bilateral lineage with the mean-reversion homeostat, ρ=0.1), **N=8 seeds × 1500 steps (~4 generations)**, sweep `mate_choice_strength` m∈{0,2,4}.

**What we know (per-m, mean across seeds):**

| m | status→RS `corr(prowess,offspring\|♂)` | mean(cred) | Gini(cred) | male N_e | combined-status death-deficit |
|---|---|---|---|---|---|
| 0 (random-paternity control) | −0.00 ± 0.02 | 1.21 | 0.21 | 170 | +0.04 |
| 2 | +0.089 ± 0.013 | 1.90 | 0.22 | 134 | +0.10 |
| **4** | **+0.190 ± 0.015** | 3.08 | 0.23 | 111 | +0.11 |

**Four results:**
1. **Status→RS calibrates to the literature.** `mate_choice_strength` **m≈4 gives status→reproductive-success r = +0.190**, matching **von Rueden & Jaeggi 2016 (r≈0.19)** — the "lineage of chiefs" emerges at the *realistic* magnitude (modest human skew), monotone from the m=0 random-paternity control (~0). **This is the calibrated operating value.**
2. **The lineage homeostat holds LIVE (the R-18-era BLOCKER fix validated in practice).** mean(cred) is **bounded/finite (1.2–3.1)** across ~4 generations — NOT the ~10⁴ runaway of the pre-fix code (mean-1 noise + fixed-anchor reversion works). Gini(cred) **bounded 0.18–0.23**.
3. **The compositional anti-fragility (R-1/R-18) SURVIVES the multifaceted hierarchy.** Mortality concentrates on the low-**combined-status** (cred·prowess) periphery — death-deficit **+0.04 → +0.11**, rising with m. (Measured on the *combined* status, not cred alone: with prowess sharing the survival advantage, the cred-only gradient washes out — itself confirming prowess is a real second axis, R-17-style.)
4. **No small-N drift collapse.** Male **N_e stays 111–170** (declining with m as fathering concentrates, but healthy) — the hierarchy is *selection*, not drift (RT-4 clear).

**Caveat (operating envelope, honest):** the cred *equilibrium* RISES with m (1.2→3.1) because prowess-weighted fathering folds achieved status into the inherited lineage (`base = cred·prowess`). It is finite/bounded at the tested settings, and since contest shares are **ratio/scale-invariant**, the *absolute* mean is largely cosmetic — **Gini is the meaningful inequality and it is bounded**. But the runaway margin (`(1−ρ)·mean-father-prowess < 1`) narrows at high m; the safe envelope is **m≲4, ρ≥0.1**. Paternal-provisioning (`paternal_provision_frac`) calibration to Marlowe 58% still pending (needs a life-history-enabled run; the channel is built + conserved).

**Status:** the **complete Carbon civilization** — multifaceted heritable status, achieved prowess, status→fitness mating, runaway-safe lineage — is now built (476 tests), deep-red-teamed (1 BLOCKER found + fixed), and statistically validated on the demographic substrate. The deferred **C (pair-bonding)** and the **Silicon comparison** (the original C-vs-Si question) are the open frontiers.

---

## R-20 — Assortative mating (B++) SPREADS reproduction, it does NOT consolidate dynasties — a counterintuitive control-revealed result: homogamy ≠ reproductive skew

**Origin:** B++ assortative-mating build + paired control comparison, `outputs/phase1_biome_mortality/run_3e_bpp_assortment.py`, 2026-06-21. Full B+ (m=4), forest-Aché δ=3, lineage-tracking (patriline IDs), N=6 seeds × 1200 steps, sweep `assortative_strength` α∈{0 (=B+ control), 2, 4}. Mate-choice father weight = prowess^m × **status-similarity kernel** `exp(−α·(ln s_j−ln s_i)²)`, s=cred·prowess.

**Hypothesis (mine, going in): assortment amplifies dynasties** — high-status ♂ pairing with high-status ♀ should make status compound on both lineages and consolidate the elite. **The control comparison FALSIFIED it.**

| α | mate-status corr | largest patriline | #lineages | lineage-Gini | status→RS | mean(cred) |
|---|---|---|---|---|---|---|
| **0 (B+ control)** | +0.04 | 10% | 54 | 0.53 | **+0.19** | 2.9 |
| 2 | +0.66 | 11% | 55 | 0.50 | +0.10 | 1.7 |
| 4 | +0.80 | 9% | 56 | 0.53 | **+0.10** | 1.4 |

**What we know:** the assortment **mechanism works strongly** (mate-status correlation +0.04→**+0.80**), but its consequences are the *opposite* of the hypothesis: **no dynastic consolidation** (largest patriline 10%→9%, #lineages flat ~55, lineage-Gini flat 0.53), and it **REDUCES the status→reproductive-success skew** (+0.19→+0.10) and lowers mean(cred). Robust across 6 seeds.

**Why — homogamy ≠ reproductive skew (orthogonal mating-system axes).** The "lineage of chiefs" consolidation comes from **reproductive MONOPOLY** — a few high-prowess males fathering many children across *all* mothers (dominance; B+'s one-sided prowess draw at m=4). **Assortment COUNTERS that monopoly**: it constrains a top male to the *limited pool of top-status mothers*, so he fathers *fewer* total children → the prowess→fertility skew drops (0.19→0.10) and no single patriline runs away. Assortment sorts *who pairs with whom* (homogamy); it does not concentrate *how unequal* reproduction is — if anything it democratizes it.

**Consequence:** **B++ is built + validated but is NOT a dynastic amplifier** (my §pair-bonding recommendation was wrong). It is a *realistic homogamy* feature that **spreads** reproduction. If the goal is maximal dynastic skew, the lever is *higher* `mate_choice_strength` (more monopoly), not assortment. The two are tunable independently (m = skew/monopoly; α = homogamy). The homeostat held throughout (mean cred bounded); R-19's status→RS calibration (r≈0.19) is a B+ (α=0) property — with assortment on, realized skew is lower. Lineage-tracking diagnostics (patriline IDs, largest-fraction, #lineages, Gini) now exist for all future dynasty questions.

---

## R-21 — E.3-proper: status→RS r≈0.19 at m=5 on the BANDED substrate; the lumping ablation REVISED (2026-06-29)

**Origin:** `outputs/phase1_biome_mortality/run_3g_e3_proper.py`, 6 seeds × 1200 steps, CC-1 SubWindowCapacity patch + `bonded_mate_radius=1` + banded seeding. Supersedes the contaminated E.3 (0f39c2d — bare-forage + per-cell gate + `w.agents` corpse-counting). MODEL_SPEC §4.8.5.

**What we know:** **`mate_choice_strength` m=5 → status→RS = +0.190 = von Rueden 0.19 exactly** (m=4→0.162, m=6→0.216). The banded substrate needs m=5 vs R-19's IFD m≈4 because the band-territory mate-gate dilutes the skew. Homeostat holds, N_e 37–58, eq_pop fertility-pinned. **The old lumping claim ("homogenizing collapses status→RS 0.48→0.13") does NOT replicate** — it was a corpse/bare-forage artifact. Corrected, nuanced finding: the status→RS *correlation* is **prowess-driven** (robust to flattening cred), but **lumping a band to a single unit destroys R-18 compositional anti-fragility** (death-deficit +0.127 → −0.087). ⇒ "don't lump to band-as-unit" stands, but for the **mortality-selection** mechanism, NOT the RS skew.

## R-22 — The "frozen band" was a corpse-counting MEASUREMENT bug + a substrate/mate-gate error (2026-06-26)

**Origin:** turnover-fix diagnosis, commit a6a4ccf. MODEL_SPEC §4.8.4.

**What we know:** the seeded-bands "96% in bands / pop stable 254" claim was an **artifact of counting CORPSES** — `phase1_model` pruned `agent_list` on death but never called `agent.remove()`, so dead agents lingered in Mesa's `self.agents`, stacked 25-deep at their death cells. Fixed (`agent.remove()`; band metrics read live `agent_list`). Two further errors: bands were run on the **bare forage field** (~1–8/cell, starves a 25-band instantly) instead of the **CC-1 capacity field** (~30–50/cell, where R-18/19 are valid); and the per-CELL bonded mate-gate fails at the substrate's ~1/cell density. Fix: run bands on CC-1 + **`bonded_mate_radius=1`** (band-territory mate-gate) → population sustains and turns over (CC-1: r=0 extinct, r=1 250→1624). **Audit:** R-18/19 used `agent_list` + CC-1 and STAND; morph/storage claims survive on live counts.

## R-23 — Storage-tethering RETIRED: the morph fires from emergent bands alone (2026-06-29)

**Origin:** `run_3h_tether_retirement.py`, 5 seeds × 800 steps. MODEL_SPEC §4.5.11/§4.8.5.

**What we know:** the `storage_tether_reserves` band-aid (froze stocked bands to force packing) is unnecessary — on the corrected substrate emergent bands reach Binford packing on their own and the egal→complex morph fires from emergent density+storage (220 cells → complex_forager, no tether). The tether's only distinct effects were over-concentration artifacts (≈4× pop, spurious `stratified_chiefdom`). Config field + movement guard deleted; CC-1 capacity promoted to `sic_games/capacity.py: NPPCapacityField`.

## R-24 — F.2: risk-dilution-as-MORTALITY is a death spiral (SHELVED); the band life-cycle is a balanced fluid equilibrium (2026-06-29)

**Origin:** `run_3i` (risk), `run_3j` (life-cycle). MODEL_SPEC §4.8.6.

**What we know:** wiring safety-in-numbers into the *mortality* schedule (a loner penalty) FAILS — higher penalty → fewer people in smaller bands (penalty 0→6: pop 281→64), a **death spiral, not an optimum**, because mortality culls but does not *aggregate* (aggregation is the E.1 movement drive's job). **Risk-dilution belongs in movement (E.1); banding's fitness teeth are the F.1 mate-gate.** `enable_band_risk` kept default-OFF with a caveat. Band life-cycle (`TerrainWorld.bands()`): a **balanced dynamic equilibrium** — merge ≈ split (~21/100 steps), collapse ≈ form (~6/100); a time-together persistence filter shows ~30% of agents in *durable* bands (the rest fluid), motivating F.3 (no persistent bond yet).

## R-25 — The complete dynamic band: persistent families → a first-class non-kin ~25 band entity → per-band society → assabiyah-driven size (2026-06-29)

**Origin:** F.3a/b (d457794), F.3c-1 (c870165), F.3c-2/2b/3 (175e15f, 29b9922, 61042e8). `run_3k`/`run_3l`. MODEL_SPEC §4.8.7–11.

**What we know:** (a) **persistent monogamous pair-bonds + nuclear-family co-movement** raise the durable-band fraction 0.30→0.41 and resolve the connectivity macroband artifact (bands become discrete family cores). (b) The band becomes a **first-class multi-family entity via the collective-identity VECTOR** (`GroupVector`: band_id active; assabiyah/religion reserved seams — the Carbon "hive-mind"): emergent affiliation + exogamy (spouse→larger band) + cohesion + hysteretic fission/fusion → **agent-weighted band size 28.7, median 25.3 ≈ Wobst/Birdsell 25**, and **NON-kin** (dominant-lineage 0.38, ~7 lineages/band, only 30% of adults co-reside with a parent — Hill 2011 ✓). (c) **Society relocates from the cell to the band**; (d) **assabiyah** (Ibn Khaldun solidarity) builds from band surplus and makes `tolerable_size` condition-dependent — **corr(assabiyah, band size) = +0.27** (rich/high-solidarity bands stay together larger). All flags independent + default-OFF.

## R-26 — Full-stack: the architecture coheres; status→RS settles at ≈0.13, the marriage-system-appropriate value (2026-06-29)

**Origin:** `run_3m_fullstack.py`, 6 seeds × 1500 steps, the entire social stack on CC-1. MODEL_SPEC §4.8.12.

**What we know:** with everything on, the model **coheres** (eq_pop ~360–540, N_e ~65, bands ~26 non-kin, per-band societies, assabiyah, **R-18 survival anti-fragility intact** death-deficit >0). The von Rueden status→RS, validated at 0.19 in the simpler lottery model, **becomes ≈0.13** under the family stack — and **0.13 is CORRECT**: von Rueden & Jaeggi 2016's own marriage-system breakdown puts MONOGAMOUS societies at r≈0.15 (the 0.19 is the polygyny-inflated cross-system average), and the family model is monogamy-dominant. Getting there required fixing two bugs: the **prowess prod-credit was corrupted** (diluted by a father's co-resident dependent sons → reproduction *depressed* prowess; fixed by crediting adult producers only), and prowess was **too volatile** (`prowess_decay` 0.10→0.05 = a persistent reputation, Smith 2004). The skew is **polygyny-carried** (strict monogamy ≈+0.03 — the model lacks a status→partner-fertility "wife-quality" channel, a noted future enrichment). E.3's lottery m=5→0.19 stands as the superseded simpler-mechanism calibration.

## R-27 — Climate integration (Stage 0): coheres but the population is TROUGH-LIMITED; the social response needs a controlled driver (2026-06-29)

**Origin:** `run_3o_climate_social.py`. Blueprint `…_SocialEvolution_Dynamic_Scoping.md` Stage 0.

**What we know:** running the social stack on a `ClimateField`-modulated capacity (so conditions vary) is mechanically sound (coheres, bands preserved), but **climate variability lowers carrying capacity** (Liebig lean-season binding): eq_pop −27% gentle, −44% moderate, **4× crash under a harsh compressed regime** — the population is **trough-limited and the current storage does NOT buffer multi-generation downturns** (→ a future storage/mobility enhancement). The social metrics are **config-sensitively perturbed** (status→RS 0.06–0.19 across climate configs); a single stochastic-telegraph run gives a noisy "regime response" ⇒ **the dynamic-social stages need a CONTROLLED/deterministic climate driver** for clean benchmarking, with the stochastic ClimateField as the production substrate once validated.

---

## R-28 — Controlled-climate harness (Social-Evolution Stage 0): a deterministic driver resolves the climate-attributable social response that R-27 smeared out (2026-06-30)

**Origin:** `outputs/phase1_social_evolution/run_se0_controlled_climate.py` + 5 `ClimateDriver` unit tests. Answers R-27's "needs a controlled driver." Methods: MODEL_SPEC §4.1.9; mechanism: MECHANISMS §16.

**What we know:** the new `ClimateDriver` (a deterministic, pure `t→[0,1]` regime waveform that overrides the stochastic telegraph; `regime_driver=None` ⇒ bit-exact telegraph — locked by `test_driver_none_is_bit_exact_telegraph`) gives the dynamic-social stages a **clean benchmark**. Demonstration (full social stack, 3 seeds × 1500 steps, a_seas=0.25; FLAT control vs a scripted −30% PULSE on [600,900)): because the arms are **bit-identical until the scripted onset**, the climate-attributable response = the **between-arm gap at matched times** (difference-in-differences). Result — the **placebo check passes exactly (ΔPRE = −0.00** on pop/band/surplus/assabiyah), then a **−70 pop catastrophe footprint DURING** and a **−135 lagged demographic scar POST** (the population resumes growth after the pulse lifts but does not catch the counterfactual within the window). Band size and surplus track down cleanly; **assabiyah is near-invariant to a single pulse (ΔPOST ≈ −0.01)** — an informative null the future dynastic-cycle stage (Ibn Khaldun) must reckon with (solidarity does not erode from one shock). **Why it matters:** ΔPRE≈0 proves the harness isolates the social response free of the population-growth trend that confounds the within-arm PRE→POST read; the stochastic R-27 run could not. 562 passed/1 xfailed.

---

## R-29 — Size-driven repulsion (Johnson scalar stress) binds at the full-stack level AND resolves assabiyah saturation (2026-07-01)

**Origin:** `outputs/phase1_social_evolution/run_se1_leader_coherence.py` + 7 `size_repulsion` unit tests. Social-Evolution Stage 1b. Methods MODEL_SPEC §4.8.13; mechanism MECHANISMS §16; lit Johnson 1982 / Alberti 2014 / Layton 2012 (LITERATURE).

**What we know:** `tolerable_size` is now an explicit **cohesion − dispersion** balance; the new dispersive term is Johnson 1982 scalar stress as a logistic in band size (Alberti 2014 shape, re-anchored from village scale N≈127 to band scale — a bracket, not a fit), **subtracted** from cohesion, and **relieved by hierarchy** (Johnson's thesis: `REPULSION_SOCIETY_FACTOR` egalitarian 1.0 → complex 0.5 → stratified 0.25 — so settling/institutions unlock larger groups). It is **resource-INDEPENDENT** (distinct from the existing surplus↓→assabiyah↓→fission path). **Two results:** (1) repulsion **binds** — with it ON, max band size dropped **44 → 31** in the realistic full-stack run; (2) it **fixes the R-30/earlier saturation problem** — assabiyah alone drifts to its 1.0 ceiling in steady state and silently absorbs any second cohesion source via the `min(1,·)` clamp; repulsion pulls `cohesion_frac` back down (0.86 assab + 0.23 leader − 0.19 repulsion ≈ 0.89), restoring the headroom for leader coherence (or any future cohesion term) to move `tolerable_size` again. Unit tests lock the logistic shape, the Boehm/Johnson society relief (egalitarian fissions a large mobile band; stratified stays whole), the hard-cap guard, and the headroom restoration. Default OFF = bit-exact. **This is the validated Stage-1 deliverable.** 579 passed/1 xfailed.

## R-30 — Leader coherence: built + unit-valid, but the leader-death→fission signature is a PRINCIPLED NULL in the complex-forager regime → benchmark deferred to the dynastic stage (2026-07-01)

**Origin:** `run_se1_leader_coherence.py` cohort event study (6 seeds × 900-step burn) + 10 leader-coherence unit tests. Social-Evolution Stage 1a. Methods MODEL_SPEC §4.8.13.

**What we know:** leader coherence — a second, additive cohesion source from a band's top-status member (`leader_strength = 1 − mean/top status`), **Boehm-gated** (egalitarian weight 0 → inert; complex 0.5; stratified 1.0) — is BUILT and unit-validated (raises tolerable size, scales with the society weight, additive-not-a-relabel, hard-cap preserved; a hand-built stark-leader band stays intact where it would otherwise fission). **But its behavioural signature is absent:** a cohort-specific event study (kill each complex/stratified band's leader vs. a matched random adult; measure how the bereaved band's original member cohort fragments) found **Δ(leader−placebo) ≈ −0.02 … −0.25** distinct-bands (slightly *negative*, robust over 6 seeds and 4 checkpoints) — killing the leader does **not** fission the band more than killing a random adult. **Two structural reasons, both correct-by-design:** (i) **fission is not the equilibrium-binding size constraint** — bands settle ~20 (mortality + mate-gate + movement) below tolerable_size, so a small leader-loss threshold drop rarely tips a split; (ii) **leadership is a *distributional* property** (top/mean ratio), so killing the top instantly promotes a near-identical runner-up — no keystone, no succession gap, no collapse. This is anthropologically right: Boehm's foragers have no fixed keystone chiefs; leader-death-collapse is the signature of **hereditary chiefs + succession crises**, i.e., the **stratified Ibn Khaldun dynastic-cycle stage (Stage 3)**. **Verdict:** leader coherence retained as a correct, ablatable mechanism; its benchmark is **deferred to the dynastic stage** (not claimed validated here). Measurement note: the null held under BOTH a population-aggregate and a cohort-specific estimator — it is not a measurement artifact.

---

## R-31 — The fission threshold is DORMANT at equilibrium; band size is movement-set, not fission-set (+ R-29 correction) (2026-07-01)

**Origin:** controlled probe (realistic full-stack config, repulsion off-vs-on) during the fission-driver design review. Supersedes part of R-29's headline. Feeds the movement-channel blueprint (`…_MovementChannel_ResourceResponse_Scoping.md`).

**What we know:** at equilibrium **0/26 bands sit near their `tolerable_size`** — bands settle at N≈20 while tolerable≈42. So the entire cohesion−dispersion balance (assabiyah + leader − repulsion − season) is **inert for setting *central* band size**; size is set upstream by the **movement (diffusion) + mortality + mate-gate** complex. The fission threshold is a **tail safety-valve** (runaway prevention + the future settled/dynastic regime), NOT the primary band-size regulator. **R-29 CORRECTION:** repulsion's *clean* controlled effect (off-vs-on, all else equal) is **max band 37→36, mean 20.7→20.0** + a modest pop drop (539→441 via tail-fission) — NOT the "max 44→31 cap" R-29 first reported (that 44 baseline was an unclean cross-config comparison). Repulsion *does* pull `cohesion_frac` off the 1.0 ceiling (0.975→0.875 — that part of R-29 holds), but it is **moot** while tolerable (42) ≫ N (20). Repulsion trims the tail; it does not cap the typical band. **Driver taxonomy + the three-channel architecture** (movement sets central size / threshold = tail valve / mortality = failure mode) and the non-monotonic resource response (moderate lean → aggregate, severe scarcity → disperse, catastrophe → die) are recorded in the blueprint; `season_aggregation`'s lean→fission sign is mis-signed AND inert → to be retired (DE-7). **No mechanism claim is overturned** — leader coherence (R-30) and repulsion (R-29) remain correct, ablatable mechanisms doing their (tail) job; the review re-scopes what job that is.

---

## R-32 — `_condition` is a survivor-biased FED-moment signal; it cannot drive malnutrition responses (2026-07-01)

**Origin:** M2 integration probe (severe scarcity pulse on the realistic full-stack). A red-team catch mid-build.

**What we know:** `agent._condition` (the EMA of nutritional status, §4.2) is **pinned at ~1.0 even under a population-crashing scarcity pulse** — probe: pop 383→133, hundreds of starvation deaths, reserves at the 0.25 floor, yet mean `_condition` = 1.000 throughout. Two causes: (1) it is captured from `_fed_reserve = wealth` at the **post-harvest / pre-burn** moment (phase1_model.py:814), i.e. the FED peak, so it never sees the post-burn hunger trough; (2) **survivor bias** — agents who aren't refilled die and are pruned, so the living always look fed. Consequence: **scarcity in this model manifests as death, not as a lingering low-condition state**, so any mechanism that reads mean band `_condition` as a malnutrition signal is silent exactly when it should fire. Practical impact: M2 was first built on `_condition` and would never have triggered. **Fix:** M2 now reads a per-band **realized starvation-rate EMA** (`_band_starv_ema`) instead. (Wider implication: `_condition`-gated mechanisms measure the fed survivors, not scarcity — noted for the density-disease synergy which also reads it.)

## R-33 — M2 malnutrition fission VALIDATED (dispersal substitutes for starvation death); resource-directed fusion built (2026-07-01)

**Origin:** `outputs/phase1_social_evolution/run_se2_malnutrition_fission.py` (substitution test) + 9 M2/F unit tests. Blueprint `…_ResourceResponse_Scoping.md`; methods MODEL_SPEC §4.8.13; supervisor-chosen realized-starvation anchor.

**What we know:** **M2** — a band losing members to realized starvation (`_band_starv_ema`) gets a dispersive term that lowers `tolerable_size` toward `band_base_tolerable` → a LARGE band fissions (intrinsically size-gated: tolerable floors at base, so bands <25 can't be fissioned — "large bands, not small," for free), the child band diffuses apart. **Substitution test (the decisive validation)**, severe −50% pulse, M2 off vs on, 3 seeds: **starvation deaths DROP with M2 on in all 3** (−120, −31, −24), M2 fires (max pressure 0.6–1.2), and 2/3 seeds end with *higher* surviving population — dispersal reroutes the scarcity cost from death (spreads out → higher per-capita yield → fewer subsequent deaths), not merely more fission. Net demographic effect modest/mixed (dispersing to avoid starving can cost the best patches — honest). REACTIVE to realized starvation, not a forecast (supervisor: anticipatory dispersal would need "wise leadership" — a future feature). **F** — resource-directed fusion: a band below `band_merge_size` joins the RICHEST neighbour within `fusion_search_radius` (highest `_band_surplus`) instead of the nearest (starving remnants merge into well-provisioned bands; Wiessner hxaro), falling back to nearest if none in range; unit-tested (nearest when off = bit-exact, richest-nearby when on, radius bound). Both flags default OFF, bit-exact. `season_aggregation`'s severe-scarcity role is now superseded by M2 (DE-7; field retained inert pending a cleanup removal). 588 passed/1 xfailed.

---

## R-34 — Deep audit (pre-big-run): no regressions; stack healthy + cheap; one perf win (2026-07-01)

**Origin:** `outputs/audit_20260701/` (profile_fullstack, coherence_fullstack, statusRS_6seed_flagson) + full suite. Four passes after the Social-Evolution arc.

**What we know:** (1) **Tests** 592 passed/1 xfailed. (2) **Perf** full stack 13.5 ms/step (0.057 ms/step/agent); the recent social machinery is CHEAP — `_maintain_bands` (leader+repulsion+M2+F) is 2.4% of runtime, genealogy negligible. The cost is the core loop (`diffusion_select_target` + `climate.level`); the **climate temporal multiplier (season·regime·interannual) is recomputed per-cell-eval (~28% of runtime) though it's cell-independent** → OPT-1: cache per `set_step` (~25% saving, bit-exact). (3) **Coherence** full stack (all flags on, 6 seeds) coheres: eq_pop 339, bands 22.3, Gini 0.17, no extinctions; eq_pop below static-R-26 is the expected seasonal trough-limiting (R-27), not a regression. (4) **status→RS is NOT regressed:** ≈+0.014 (flags on) vs +0.029 (flags off) — both near-zero on the CLIMATE substrate, within seed noise; the documented **0.13 is the STATIC + new-flags-OFF value (R-26)**, guaranteed by bit-exactness, and climate depresses it to ~0.01–0.03 (R-27, reconfirmed). **status→RS needs the full 6-seed×1500-step protocol — unreliable (±0.1) at small samples.** (5) **Flag interactions clean:** one dependency to note — leader/repulsion/M2 are no-ops unless `enable_dynamic_bands=True` (they live in that block); F + genealogy are independent. No degenerate combinations. **No blocker for CC-1 or the big run.** Findings + actions: `outputs/audit_20260701/AUDIT_FINDINGS.md`.

## R-35 — Ascribed-status mate-choice recovers the composite status→RS (2026-07-02)

**Origin:** 16-seed re-estimation + partial-correlation diagnostic + ascribed-mate-choice recalibration (`outputs/statusRS_reestimate_20260702/`). Methods MODEL_SPEC §4.8.16; blueprint `…_AscribedMateChoice_Scoping.md`.

**What we know:** the documented "status→RS = 0.13" (composite cred·prowess) is **NOT robust** — at 16 seeds it is **+0.001 [95% CI −0.035, +0.037]** (≈0, 0.13 outside the CI; R-26's was a 6-seed estimate at the optimistic tail). It **decomposes**: **prowess (achieved) → RS = +0.101 [+0.062, +0.140]** — the genuine von-Rueden signal, working — and **cred (ascribed) → RS = −0.066**, which cancels it. Root cause: **mate-choice was prowess-weighted only** (`_do_pairing`); cred had no mating channel. The cred-negative is a **weak, diffuse, seed-noisy confound**, not causal (partial-corr diagnostic: survives age/prowess control only at −0.02…−0.04, seed range −0.18…+0.11). **FIX (built + CANONICAL):** society-gated ascribed(cred) mate-choice — `enable_ascribed_mate_choice`, `MATE_ASCRIBED_WEIGHT` (egalitarian 0.25 floor / complex 0.6 / stratified 1.0), weight interpolates `prowess → cred·prowess`. Pinned **`ascribed_mate_strength=2.5` → composite +0.128 ≈ von-Rueden 0.13**, Gini stable (no dynastic runaway). Egalitarian floor 0.25 (family sways marriage even among egalitarians; Ember & Ember). **The full reframe of the R-19/R-21/R-26 headline (0.13/0.19) is HELD** pending settlement-arc validation of the stratified ~0.19 endpoint.

## R-36 — CC-1: the full Tallavaara capacity fitted + implemented (~57% of provisional); diverse-world lottery (2026-07-02)

**Origin:** Tallavaara 2018 data-analyses SI (extracted + validated vs Dataset_4); `capacity.py::density_tallavaara`; `terrain.py::world_lottery`. Methods MODEL_SPEC §4.3.1; LITERATURE Tallavaara.

**What we know:** the provisional linear-clamp `min(0.5, 0.3·npp/1360)` is replaced by Tallavaara's **actual segmented regression** `ln(density) = −0.1353 + 0.0028623·NPP − 0.0030745·(NPP−1372)₊` (hump-shaped; density in #/100km² = persons/cell). `NPPCapacityField(mode='tallavaara')`, provisional kept selectable (default). **Impact: ~57% of the provisional patch capacity** (provisional over-generous at low NPP where 97% of our cells sit) → eq_pop ~40% lower — a **correctness** improvement (Tallavaara ~0.05/km² at NPP 633 matches the ethnographic record). Also built the **world-lottery**: per-world knob draws cycling forest/savanna/desert/montane/mixed archetypes (NPP 175→856) so CC-1 is characterized across a productivity range. NB our worlds are arid-biased (median NPP ~500 vs forager-median ~900).

## R-37 — Biome → society: the bonded-family structure is productivity-gated (a model gap) (2026-07-02)

**Origin:** `outputs/biome_society_20260702/run_biome_society.py` (Tallavaara CC-1, world-lottery, canonical config).

**What we know:** biome DOES shape society — **FOREST** (NPP 850) thrives into a complex-forager society (band ~22, 98% complex, status→RS positive); **savanna/desert/montane/mixed** (low NPP) **collapse**. But the collapse is a **model gap, not a real pattern** — marginal foragers (Hadza/Ju) DO have families and bands. Diagnostic: with **simple reproduction** the same worlds sustain **355–896** → capacity is fine; the **bonded-family/co-residence structure** can't sustain at low density. Anthropologically the immediate-/delayed-return divide (Woodburn) + Binford/Kelly productivity gradient — but the model should grow a *mobile-egalitarian* society at marginality, not collapse. → the marriage-aggregation + mobility work (R-39).

## R-38 — Newborn→adult life-history wired canonical; 3 latent bugs fixed (2026-07-02)

**Origin:** life-history wiring + `test_life_history_wiring.py`. Methods MODEL_SPEC §4.2/§4.3.

**What we know:** the Kaplan-2000 childhood-dependency machinery (graded η production 0.2→1, maintenance 0.3→1, reserve 0.3→1 over 15 yr + provisioning) was **fully built but OFF** — no `LifeHistoryConfig` was ever passed, so **newborns foraged at full adult rate**. Canonicalized: `enable_life_history` (auto-builds a MONTH-scaled config — the class defaults are legacy YEARS) + `enable_provisioning`. **Three latent bugs exposed + fixed:** (1) the hard `max_age` cap was **dead code under demog** (an `elif` on `demog is None`) → Siler-tail agents reached age **1111** → enforced (maxage 899); (2) the elder η ramp went **negative past max_age** → `base_status<0` → `base_status**1.5` **complex** → movement crash → clamped at eta_old; (3) founders got lh from the constructor param, not the auto-built `self._lh_cfg` → fixed. Forest childhood-ON eq_pop 322 (≈320 off — children cost ≈ their lower consumption), 41% children foraging at η 0.57.

## R-39 — The gathering fixes mate-finding; the savanna collapse is FIXED-RANGE MOBILITY (2026-07-02)

**Origin:** marriage-aggregation build + co-movement/mobility diagnostics. Blueprint `…_MarriageAggregation_Scoping.md`; methods MODEL_SPEC §4.8.18.

**What we know:** the **gathering** (seasonal cross-band exogamous pairing at abundant sites — `enable_marriage_aggregation`) **fixes mate-finding** (savanna: 50 pairs at the first gathering; forest: 93% of adult females paired, eq_pop 433). But savanna still bleeds to ~5. Root-cause chain (all ruled out): NOT mate-finding (fixed), NOT capacity (ceiling 6771 vs pop 5), NOT connubium radius (r8=r15=r25=r40 → 5), NOT eligibility (94–100% have living **same-band** partners). **DECISIVE:** family **co-movement** piles the family onto the mother's single cell → at 3.7 persons/cell it **overcrowds → starves**; disabling co-movement → savanna **eq_pop 279**. **DEEPER root (supervisor):** the diffusion movement is **hard-coded r=1** (no biome-aware mobility) — real foragers spread over sparse territory by **ranging farther** (Kelly/Binford: mobility ∝ 1/productivity). Our savanna agents *can't* spread → pile up → starve. **FIX (next):** productivity-scaled movement range (larger foraging/move radius in low-NPP cells) — supersedes the family-spread band-aid.

## R-40 — Mobility ablation FALSIFIES the pile-up diagnosis; the savanna collapse is FAMILY CO-MOVEMENT (2026-07-03)

**Origin:** productivity-scaled-mobility build (§4.8.19) + ablation on biome→society (`outputs/biome_society_20260702/run_mobility_ablation.py`) + early-transient and co-movement probes. Supersedes R-39's root diagnosis.

**What we know:** productivity-scaled mobility (`enable_productivity_mobility`, stride ∝ 1/static-NPP; Kelly/Binford) was built (default-OFF, bit-exact, 10 unit tests) — but the ablation is **NEGATIVE**: ON does NOT rescue the low-NPP biomes and is **consistently mildly harmful** (savanna survival 2/3→**0/3**; every archetype's eq_pop ON ≤ OFF; forest 229→189). **Two probes falsify R-39's "fixed-r=1 pile-up → overcrowd → starve":** (1) the founder seed-stack (occ/cell 5.15, max 30) **decompresses to occ/cell ~1.7 within 25 steps in BOTH arms** — there is NO persistent pile-up; the collapse is a slow chronic bleed (220→82 over 220 steps, →~3 by step 900), not an acute crowding event; and mobility ON bleeds *faster* (step-219 pop 56 vs 82). (2) **The real lever is FAMILY CO-MOVEMENT:** savanna @ 900 steps — canonical (co-move ON) → **pop 3**; `enable_pair_bonds=False` (no co-move) → **pop 327**; mobility ON → **pop 3** (no effect). **Mechanism (re-diagnosis):** co-movement snaps dependent followers to the family head's cell each step, coupling the whole family's subsistence to ONE marginal cell's yield and preventing followers from independently foraging better cells → chronic per-capita deficit in low-NPP biomes → the bleed. NOT a spatial pile-up; a **foraging-efficiency loss from forced co-location**. **Consequence:** productivity-scaled mobility is retained as a valid, ablatable, default-OFF mechanism but is **NOT the biome→society fix** (DEAD_ENDS DE-9); the R-37 collapse is a property of the co-movement mechanic at low density. **NEXT lever (open):** make co-movement viable in marginal biomes — e.g. let the family occupy a small *footprint* (not one cell), route follower subsistence through provisioning off the head's actual yield, or relax co-movement below a productivity threshold — rather than range. **[MECHANISM REFINED by R-41 — the harm is primarily FERTILITY suppression, not a starvation deficit.]**

## R-41 — Co-movement decomposition: the harm is FERTILITY suppression via over-subscribing the MOTHER's cell (2026-07-03)

**Origin:** "diagnose deeper first" (supervisor) — per-cause death/birth counters + a clean 3-arm decomposition isolating co-movement from pair-bond fertility (patch `_family_head→None` keeps the bonds, kills only co-movement). Savanna, 900 steps. Refines R-40's mechanism.

**What we know:** `enable_pair_bonds` bundles TWO effects; decomposed:
| arm | pop@900 | births | starv | senesc |
|---|---|---|---|---|
| **A** full canonical (bonds + co-move) | **3** | 163 | 273 | 107 |
| **C** bonds ON, **co-move OFF** (patch) | **249** | 672 | 283 | 360 |
| **B** `enable_pair_bonds=False` (daily mate-gate, no bond, no co-move) | 327 | 936 | 420 | 409 |
Disabling **only** co-movement (C, bonds retained for fertility) recovers **3→249** (~76% of the full 327) — so **co-movement is the dominant killer**, confirming R-40. **But the CHANNEL is FERTILITY, not starvation:** A→C births **163→672 (4.1×)** while starvation is ~flat (273 vs 283). **Refined mechanism:** the **mother is the movement ROOT** (her bonded male + dependent children follow HER). She selects her cell to maximise her *own* per-capita share `S/(n+1)` as if moving alone — then the family snaps onto that exact cell, spiking its occupancy (measured **occ/head-cell 3.73 vs population-mean 1.71**, a 2.2× over-subscription) → her realised share drops to `S/(n+family)` → her **energetic-fertility factor** falls → births collapse; seasonal troughs add the secondary starvation. Note food is NOT globally scarce (per-capita yield 4–8× burn at equilibrium) — the deficit is LOCAL to the over-subscribed root cell and expresses through fertility first. **Fix must target the occupancy spike on the ROOT's cell** (not mobility range): (i) family **footprint** — followers occupy adjacent cells, not the exact cell; (ii) **move-anticipation** — the mother chooses her cell against `S/(n + family_size)`, so she picks emptier/richer ground; (iii) **provisioning-exclusion** — followers on the cell don't take a forage share (they eat from the mother's provision), so they don't inflate `n`. All three prevent the root-cell over-subscription; (ii) is the most physically-grounded (a mother knows she's feeding a family). B's higher births (936) reflect the daily mate-gate out-reproducing persistent monogamy — a separate, expected finding (strict monogamy ≈ lower fertility; MODEL_SPEC §4.8.12), NOT the biome fix.

## R-42 — Central-place fix: FOOTPRINT (dispersed camp) resolves the savanna collapse; anticipation doesn't (2026-07-03)

**Origin:** the conceptual re-frame (supervisor: "real savanna tribes proliferated — what are we missing?") + the three-prototype comparison (`outputs/biome_society_20260702/run_comove_fixes.py`), savanna (collapse) + forest (control), 3 seeds × 900 steps. Blueprint `…_CoMovementCentralPlace_Scoping.md`.

**The missing physics:** the model **conflated co-RESIDENCE with co-FORAGING**. Real foragers are CENTRAL-PLACE (Isaac 1978; Hadza/Ju — Hawkes/Marlowe/Lee): they co-reside + share, but forage DISPERSED by day; dependents eat the pooled return, not the patch they stand on. Our exact-snap co-movement forced the whole family to *extract* `S/n` from ONE 100 km² cell → self-competition → the R-41 fertility collapse. (The model *without* co-movement already forages dispersed — hence it thrives.)

**Three ablatable prototypes built** (`comove_anticipate` / `comove_footprint=k` / `comove_provision_exclude`; all default OFF ⇒ bit-exact; 5 unit tests; full suite 628 passed). Comparison (savanna pop → OFF-ref 461; forest pop → OFF-ref 808):
| arm | savanna pop | savanna births | forest pop |
|---|---|---|---|
| A canon (exact snap) | 8 | 176 | 145 |
| (i) anticipate | 4 | 192 | 133 |
| **(ii) footprint=1** | **243** | 669 | 426 |
| **(ii) footprint=2** | **378** | 882 | 451 |
| (iii) provision-exclude | 22 | 276 | 221 |
| (i)+(ii) anticipate+fp1 | **393** | 907 | 408 |
| OFF (no pair_bonds) | 461 | 1065 | 808 |

**Verdict:** **FOOTPRINT (dispersed camp) is the load-bearing fix** — footprint=2 → savanna 8→**378** (82% of the OFF reference) while the forest control stays healthy (145→451). It works because it physically spreads the family over adjacent cells (the "camp"), killing the one-cell over-subscription — exactly the central-place mechanism. **(i) anticipation alone barely helps** (8→4): the mother picks emptier ground but the family still lands on her single cell, so the spike persists. **(iii) provision-exclusion helps only partially** (8→22): only juveniles are excluded; the co-locating husband still over-subscribes. **(i)+(ii) combined** ≈ footprint=2 (savanna 393). The residual gap to OFF is the pair-bond-vs-daily-mate-gate fertility difference (R-41), NOT the co-location bug. Note footprint also lifts the FOREST (co-movement over-subscription was suppressing it too, 145 vs OFF 808 — not fatally). **Mechanism is ablatable/default-OFF; canonicalizing footprint (+ its radius) is a science/calibration change pending supervisor sign-off.** MODEL_SPEC §4.8.20.

## R-43 — Full biome table: UNIFORM footprint=1 wins everywhere; the NPP-scaled footprint is falsified (2026-07-03)

**Origin:** the cell-size design question (supervisor: "10 km cell = forest monthly range; sparser biomes need a larger range — coarser cells per biome, or footprint?") + the full biome→society validation across ALL archetypes (`outputs/biome_society_20260702/run_comove_biome_table.py`). Blueprint `…_CoMovementCentralPlace_Scoping.md` §3.

**Design answer (cell size):** keep the **uniform** lattice + behavioural footprint, NOT coarser per-biome cells: variable cell sizes break the uniform grid (movement/neighbourhood/diffusion assume it) and can't handle gradient/mixed worlds; and the Tallavaara CC-1 **already** biome-scales carrying capacity per unit area, so bigger poor-biome cells would double-count it. The footprint IS the biome-scaled monthly range expressed on a uniform grid.

**But the "principled" NPP-scaled footprint (k∝1/NPP: forest≈0 tight, savanna≈2–3) is FALSIFIED empirically.** Full table (eq_pop, 3 seeds × 900 steps; OFF = no-co-movement ceiling):
| archetype | exact-snap | **footprint=1** | footprint-scaled | OFF |
|---|---|---|---|---|
| forest | 145 | 426 | 192 | 808 |
| savanna | 8 | **243** | 29 | 461 |
| desert | 0 (0/3) | **64** (1/3) | 2 | 16 |
| montane | 14 | **276** | 43 | 360 |
| mixed | 18 | **519** | 105 | 697 |
**Uniform footprint=1 recovers the collapse in EVERY biome; the scaled form barely helps.** Root cause (verified): agents **self-select onto local NPP maxima** — in a savanna world (mean NPP 474) occupied cells have **median NPP 912** (near the forest ref 900), so the scaled rule reads "rich" and returns **k=0 for 75% of families** → tight camp → collapse. The scaled footprint keys on the agent's *chosen rich spot*, not the biome's sparseness, so it can't detect marginality. Uniform footprint works because it's unconditional. (A world-mean-NPP-keyed scaling could in principle fix this but adds a world statistic + fails on mixed worlds; not pursued — uniform footprint=1 already works robustly and does well in the forest, 426, not pathological.) **RECOMMEND canonical `comove_footprint=1`** (a 3×3 = ~900 km² monthly camp on the uniform grid). **Pending before the flip (supervisor gate):** confirm forest E.3 status→RS + the full-stack results survive footprint=1, then set it in `realistic_forager_demog`. **[GATE PASSED — R-44.]**

## R-44 — Safety gate: footprint=1 PRESERVES status→RS (0.13) but ~doubles eq_pop (2026-07-03)

**Origin:** pre-canonicalization safety check (`outputs/statusRS_reestimate_20260702/footprint_safety.py`), 6 seeds × 1500 steps, STATIC substrate + realistic config, `comove_footprint` 0 vs 1.
| arm | status→RS | eq_pop |
|---|---|---|
| footprint=0 (baseline) | **+0.129** [95% CI +0.085, +0.173] | 543 |
| footprint=1 | **+0.127** [95% CI +0.098, +0.155] | 1073 |

**What we know:** the **von-Rueden status→RS calibration is PRESERVED** under footprint=1 (+0.129→+0.127, ~identical, CIs heavily overlap) — the E.3/R-26 result survives, so ascribed mate-choice + the family stack are undisturbed by the camp-spread. **But eq_pop ~DOUBLES (543→1073):** exact-snap co-movement was silently *halving* population everywhere (the same over-subscription that fatally collapsed the savanna only suppressed the resource-rich static/forest substrate) — footprint=1 relieves it → the equilibrium roughly doubles. **Consequence:** footprint=1 is SAFE for the shape results (status→RS/Gini/band structure) but is a substrate change that RAISES the population level ~2× — prior eq_pop numbers (R-26 ~530, etc.) were suppressed by the co-movement artifact and would re-baseline upward. Recommend canonicalizing `comove_footprint=1`; the eq_pop re-baseline is a correctness gain (removes an artificial population brake), not a regression, but any absolute-population claim must be re-read on the footprint=1 substrate.

## R-45 — Biome → society SUCCEEDS on the canonical (footprint=1) config: productivity shapes the society (2026-07-03)

**Origin:** the biome→society experiment (`outputs/biome_society_20260702/run_biome_society.py`) re-run on the CANONICAL config after canonicalizing `comove_footprint=1` (R-44). 5 seeds/archetype × 1300 steps, Tallavaara CC-1. Closes the R-37 collapse.

**What we know:** with the central-place footprint fix canonical, **ALL biomes now sustain a society** (R-37 had only forest surviving; savanna/desert/montane/mixed collapsed):
| archetype | survive | eq_pop | density (p/cell) | band_awt | %complex | status→RS | Gini | starv% |
|---|---|---|---|---|---|---|---|---|
| forest | 5/5 | 527 | 0.329 | 26.1 | 87% | **+0.190** | 0.23 | 23% |
| mixed | 5/5 | 510 | 0.319 | 26.2 | 83% | +0.147 | 0.25 | 35% |
| montane | 5/5 | 328 | 0.205 | 26.4 | 80% | +0.139 | 0.27 | 41% |
| savanna | 5/5 | 311 | 0.194 | 26.0 | 88% | +0.134 | 0.26 | 43% |
| desert | 2/5 | 75 | 0.047 | 24.9 | 100% | +0.139 | 0.13 | 66% |

**BIOME → SOCIETY is now a real, gradient signal** (the hypothesis, finally testable because societies persist): productivity (NPP) drives **density** (forest 0.329 → desert 0.047, the emergent Tallavaara/Binford gradient), **eq_pop** (527→75), **starvation pressure** (forest 23% → desert 66% — the marginal-biome signature), and the **status→RS gradient** (rich forest sustains the full von-Rueden **+0.190** = the cross-cultural 0.19; marginal biomes ~+0.13–0.14 — richer environments allow more reproductive skew, matching the ethnographic pattern). **band_awt ~26 (Wobst) is biome-INVARIANT** (set by the mate-gate/affiliation, not productivity — plausible). **Desert stays marginal** (2/5 survive, 66% starvation) — genuinely near the habitability edge, not a bug. **OPEN (next refinement):** society MORPH (%complex) is NOT strongly biome-graded (80–100% complex everywhere; desert even 100%) — we'd expect marginal biomes to stay MORE egalitarian (immediate-return, Woodburn) and rich/storage biomes to stratify. The morph→stratification ladder needs a biome/productivity coupling to complete the biome→society picture. But the core R-37 goal — *societies persist in every biome and their demography/inequality/reproductive-skew track productivity* — is ACHIEVED. **[MORPH gradient built — R-46.]**

## R-46 — Storability-gated morph: the society MORPH now fits the biome (aseasonal forest → egalitarian) (2026-07-03)

**Origin:** the R-45 open item (morph "complex everywhere"). Diagnosis + storability-gated-morph build (`storage_seasonality_gated`); blueprint `…_StorabilityGatedMorph_Scoping.md`. Supervisor chose the **storability/seasonality** driver over productivity/threshold-recalibration.

**Diagnosis:** the morph was "complex everywhere" for two reasons — (1) **no band is ever "packed"** (band density ~0.011 ≪ Binford 0.091 → the `stratified` endpoint is UNREACHABLE without settlement density; separate, roadmap), and (2) **`surplus_frac ≥ 0.5` in every biome** (even the leanest, montane 0.94) → all → `complex_forager`. Root: storage (the Testart surplus enabler) was **not biome-gated** — the canonical `storage_temp_threshold_c=100°C` + a constant-14°C placeholder temperature meant storage fired everywhere.

**Fix (built, ablatable):** `storage_seasonality_gated` gates the overwintering store on the cell's **biome SEASONAL AMPLITUDE** (Testart/Binford storability — an aseasonal biome has no glut→lean cycle → no storage → immediate-return egalitarian; a seasonal biome stores → surplus → complex) instead of the placeholder temperature. Per-cell amplitude from `climate.py::BIOME_SEASONAL_AMP_BY_CODE` (forest 0.05 / savanna 0.40 / grass 0.60 LIT-anchored; desert 0.45 / mountain 0.55 / wetland 0.30 PROVISIONAL); threshold 0.25 splits aseasonal forest from seasonal biomes. Off ⇒ the temperature gate (bit-exact). **Result (3 seeds × 1300, gated OFF→ON):**
| biome | %complex OFF | %egalitarian ON | pop ON |
|---|---|---|---|
| **forest** (amp 0.05) | 88% | **99% egalitarian** | 588 (survives) |
| savanna (0.40) | 88% complex | 15% egal (85% complex) | 344 |
| desert (0.45) | 100% complex | 100% complex | 57 |
| montane | 73% complex | 76% complex | 418 |
| mixed (81% savanna) | 84% complex | 76% complex | 622 |
**The aseasonal FOREST flips 88% complex → 99% EGALITARIAN while the seasonal biomes stay complex** — the Testart/Binford storability signal (rich-but-aseasonal forest foragers are egalitarian, like the Mbuti; seasonal-storage biomes develop complexity). Forest SURVIVES (588, healthy — the storage buffer was not load-bearing there). **NB the ordering is SEASONALITY-driven, not productivity** (savanna, seasonal-but-marginal, can be complex; forest, rich-but-aseasonal, is egalitarian — the OPPOSITE of a productivity ordering, and the intended/correct Testart pattern). **OPEN:** `stratified` still needs packing/settlement density (roadmap); the Hadza-savanna-egalitarian nuance (seasonal but glut too small to store) is finer than the current gate (RT-4); desert/mountain/wetland amplitudes are PROVISIONAL. **Canonicalization pending supervisor sign-off.** **[SUPERSEDED by R-47 — the seasonality gate mis-orders desert (complex); the correct driver is AQUATIC.]**

## R-47 — The morph driver is AQUATIC, not seasonal: gate COMPLEXITY (not storage) on water access (2026-07-03)

**Origin:** supervisor pushback on R-46 ("forest and desert misbehave — what can we do?"). The seasonality gate (R-46) made **desert 100% complex** (WRONG — desert foragers Ju/'hoansi, Aboriginal Australians are the paradigm EGALITARIANS) and only got forest right by accident. Blueprint `…_StorabilityGatedMorph_Scoping.md` v2.

**The correct anthropology:** MOST foragers in MOST biomes are egalitarian (Mbuti forest, Hadza savanna, Ju desert). Complex foragers are the RARE exception and are overwhelmingly tied to a dense STORABLE AQUATIC resource — NW Coast salmon, Calusa estuaries, Jomon, Chumash (Testart 1982; Kelly; Ames). The driver is not terrestrial seasonality; it is a **storable aquatic glut**. The model has the signals (`wateracc`, `is_shore`, `isRiver`, Bird-1997 shore bonus).

**Two-role bug found + fixed:** storage plays TWO roles — a survival BUFFER (ride out the lean season) AND the complexity trigger. Gating STORAGE on water (first attempt, `storage_aquatic_gated`) removed the buffer from dry biomes → **desert went EXTINCT**. Fix = **separate them**: keep storage a broad buffer (every forager caches → marginal biomes survive), gate only the **MORPH** (`morph_aquatic_gated`) — a band morphs complex only where its mean `wateracc ≥ threshold`; otherwise egalitarian however much buffer it holds. **Result (thr=0.6, 3 seeds × 1300):**
| biome | baseline %complex | morph-aquatic %complex | pop |
|---|---|---|---|
| forest | 88% | 8% | 697 |
| savanna | 88% | 1% | 396 |
| **desert** | 100% | **0% (egalitarian)** | **28 (SURVIVES)** |
| montane | 73% | 22% | 484 |
| mixed | 84% | 1% | 762 |
**The correct pattern: mostly egalitarian; complexity RARE and water-linked** (montane river valleys 22% — cf. Plateau/Columbia salmon cultures; forest 8% — riverine). **Desert FIXED — egalitarian AND surviving** (buffer keeps it alive, no aquatic resource → no complexity — the Ju/'hoansi pattern). Off ⇒ ungated morph (bit-exact). **[REFINED by R-48 — the pure-wateracc gate over-flags marginal biomes whose only habitable cells are watered; the corrected form is a SEASONAL AQUATIC GLUT in a PRODUCTIVE setting.]**

## R-48 — The morph driver, finalized: seasonal aquatic glut × productivity floor (true-desert vs river-desert) (2026-07-03)

**Origin:** two supervisor refinements — "aquatic richness is wired to seasonality, should be" (→ multiply by seasonality) and "distinguish true-desert from river-desert" (Nile vs Kalahari). Occupied-cell component diagnosis + threshold/floor sweeps.

**Diagnosis (occupied-cell components, per biome):** `shore%`/`river%` are 0 everywhere (agents sit on LAND near water, not on water cells) → those signals are useless. **wateracc and seasonality do NOT separate desert** — desert survivors have the HIGHEST wateracc (0.55) and seasonal amplitude (0.54), because in a marginal biome the only habitable cells are the watered ones. **The one signal that separates true-desert is ABSOLUTE PRODUCTIVITY** `npp_gm2`: desert 401 vs montane 552 vs savanna 667 vs forest 1172. A desert oasis is a poor setting (a waterhole, not a fishery); a Nile floodplain / salmon river is productive.

**Final mechanism (`morph_aquatic_gated`):** storage stays a broad survival BUFFER; a band morphs complex only if BOTH (a) **seasonal aquatic glut** `mean(wateracc × seasonal_amplitude) ≥ morph_aquatic_threshold` (0.15) — so aseasonal watery forest (Mbuti, amp 0.05) stays egalitarian despite rivers — AND (b) **productive setting** `mean(npp_gm2) ≥ morph_npp_floor` (500) — the true-desert (401, below floor → egalitarian) vs river-desert/Nile (≳550 → can be complex) distinguisher. **Result (floor 500, glut 0.12–0.18):**
| biome | %complex | reads as |
|---|---|---|
| **forest** | **0%** | Mbuti — aseasonal → egalitarian |
| **desert** | **0%** | Kalahari/Ju — poor setting → egalitarian (FIXED) |
| montane | 24–51% | Plateau/Columbia — seasonal productive rivers → complex |
| savanna | 18–76% | seasonal floodplain (tunable) |
| mixed | 2–54% | intermediate |
**All three anchor cases now correct: aseasonal-rich forest EGALITARIAN, poor desert EGALITARIAN, seasonal-productive-riverine COMPLEX** — complexity is rare, water+season+productivity-linked (the real forager-complexity signature; Testart/Ames/Kelly). Off ⇒ ungated morph (bit-exact). **Recommend canonical `morph_aquatic_gated=True, morph_aquatic_threshold=0.15, morph_npp_floor=500`** (all PROVISIONAL, sweep-chosen from the occupied-cell data). `stratified` still awaits settlement density. Canonicalization pending sign-off.

## R-49 — Economy-from-Climate (EFC) C1–C3 built; GATE 1 (Miami-NPP viability) PASSES (2026-07-03)

**Origin:** the deep first-principles substrate decision (supervisor: "B is too tempting") — make the food economy EMERGE from climate. Blueprint `…_ClimateEconomy_Scoping.md`; built as an opt-in world-generation MODE (`generate_world(…, mode="climate")`; legacy default, bit-exact — the migration scaffold that keeps R-2…R-48 valid until EFC is validated + cut over).

**What we know:** the pre-EFC substrate was semi-lumped — NPP = a fractal-NOISE moisture field × terrain penalties (NO temperature, no real rainfall); temperature latitude-only + static; humidity constant; biome a moisture label; food-rates biome-keyed. EFC C1–C3 replace the front of the causal chain: **C1** temperature = latitude − elevation lapse (6.5 °C/km; montane 14→3.9 °C, fixing the savanna-cold/montane-warm inversion) + a latitude-rising, maritime-damped seasonal amplitude; **C2** precipitation = Hadley/ITCZ latitude bands (equator 2865 mm rainforest → subtropics ~30° 340 mm desert → mid-lat 1489 mm → subpolar 501 mm) × orographic rain-shadow × maritime × noise; **C3** `NPP = Miami(T,P) = min(3000/(1+e^{1.315−0.119T}), 3000(1−e^{−0.000664P}))` g/m²/yr (Lieth 1972/1975, VERIFIED vs primary eqs 12-1/12-2) — so NPP is now temperature-limited (cold→low, tundra) AND precip-limited (dry→low, desert), feeding `npp_gm2`→Tallavaara capacity (a coherent real-NPP pairing; Miami sanity: −5 °C/2000 mm→387, 28 °C/150 mm→284, 28 °C/2500 mm→2430, 15 °C/1200 mm→1648). **GATE 1 (the stop-and-decide — does climate-NPP sustain populations like legacy?): PASS** — climate worlds sustain comparably or better (forest 482→442, savanna 267→417, **desert 57 [1/3] → 430 [3/3]**, montane 307→491, mixed 577→434; 3 seeds × 1000 steps). So the economy rebuild is VIABLE. **OPEN (next):** archetypes still read similar NPP because the world-lottery knobs are moisture-based not climate-based — a "desert world" isn't dry yet (RT-5; C4 rework). Legacy bit-exact throughout (full suite 645+12 climate tests). NEXT: C4 Whittaker biome (+ climate-parameterized archetypes) → GATE 2, then C6–C9 aquatic.

## R-50 — EFC C4: biome EMERGES from climate (Whittaker) + terrain×climate lottery; GATE 2 PASS (2026-07-03)

**Origin:** the first-principles reframe (supervisor: "lottery terrain and climate, biomes fall out of it"). `terrain.py::whittaker_biome`, `world_lottery_climate`; visualizer `outputs/climate_viz/render_climate_maps.py`.

**Design correction first (the 1000 km biome-count question):** a 1000×1000 km grid (~9° latitude) legitimately holds 4–6 biomes (Montana/Oregon/AZ→LA) — driven by ELEVATION + rain-shadow + coast, NOT latitude. So C1/C2 were REGIONALIZED: the grid is a ~9° swath centred on a lottery `climate_latitude`; the within-grid latitudinal gradient is now MODEST (26 °C→3.6 °C) and the big variability is elevation lapse + orographic. Also fixed orographic precipitation (was corr(precip,elev)=−0.04 — mountains invisible): added elevation UPLIFT + a multi-cell RAIN SHADOW → corr +0.51, high-ground 1284 mm vs lee 316 mm (Cascades pattern).

**C4:** biome is now an OUTCOME of climate, not a label. `whittaker_biome(T,P)` maps annual T×P onto the coarse codes (temperature-scaled thresholds: warmer needs more rain) — DESERT/SAVANNA/GRASS/FOREST, cold+wet→taiga(FOREST), cold+dry→DESERT; MOUNTAIN/WETLAND/WATER are terrain overrides. **`world_lottery_climate(seed, terrain, climate)`** draws INDEPENDENT terrain (flat/hilly/mountainous/coastal — relief+water) × climate (tropical/subtropical/temperate/boreal — `climate_latitude` + a new `climate_aridity` axis for continental/leeward dryness), and the biome falls out. **Emergent worlds (validated + visualized):** flat-tropical→forest 95% (Amazon), **flat-subtropical→desert 100% (Sahara — a genuine desert world, via aridity+Hadley descent)**, flat-temperate→forest/grass mosaic, flat-boreal→taiga, mountainous-temperate→forest+mountain+grass (Rockies), coastal-tropical→wet forest. **GATE 2 (biome sanity + demographic viability): PASS** — all 12 terrain×climate worlds sustain populations (2/2 survival, eq_pop 222–592; even subtropical deserts hold). Climate mode only; legacy bit-exact (full suite 654). **OPEN (PROVISIONAL tuning):** boreal reads all-taiga (a drier polar precip band would open tundra/steppe); dry-region orographic uplift may be too strong (moisture-limited uplift is the refinement). **Visualizer** (`render_climate_maps.py`) renders the real Python fields as a contact sheet + interactive HTML (toggle world × layer). NEXT: C6–C9 (river-source temperature → aquatic-food field → wire into capacity → morph from density → stratification).

## R-51 — GD-1 finite resources built + viable; emergent sedentism BLOCKED by lack of circumscription (2026-07-03)

**Origin:** EFC C8 GATE-3 failure (aquatic capacity subsidy didn't concentrate bands — IFD disperses) → build GD-1 finite resources (depletable stock) to test whether depletion makes concentration emerge. `capacity.py::NPPCapacityField(enable_depletion=True)`, `deplete_and_regrow`; blueprint `…_GD1_FiniteResources_Scoping.md`, LITERATURE (Coe 1976 / Cortés 2016 / central-place depletion halos).

**GD-1 built + viable:** a cell is now a depletable STOCK `B∈[0,1]` of its ceiling, logistic regrowth at a biome-specific rate (grassland ~0.6–0.7/yr, forest ~0.15, aquatic ~0.8 — Cortés r_max, Coe) minus foraging pressure (occupancy/capacity); `season` hook (aseasonal for now). Deplete/recover validated (a cell hunted-out over 2 yr → floor, recovers over a fallow). Default OFF ⇒ non-depleting standing flow (bit-exact; full suite 660). eq_pop stays viable with depletion ON (mtn-tropical 329→319, coastal 328→339).

**But emergent sedentism did NOT fire — and the reason is fundamental (Carneiro).** Bands still spread (band density ~0.012/km², 0% packed, aquatic cells barely occupied) even with depletion + the C8 aquatic subsidy. **Root cause:** the population equilibrates at ~320 against a patch carrying-capacity CEILING of **71,246** — the land is filled to **0.4%**. The population is **DEMOGRAPHICALLY limited** (Siler mortality + density-disease + IBI fertility balance), NOT resource/space limited. So the landscape NEVER saturates → IFD always has empty high-per-capita cells to disperse into → no circumscription → no forced concentration → sedentism/complexity cannot emerge from resource richness alone. **This is Carneiro 1970 circumscription as a hard prerequisite:** complexity needs the population to FILL the habitable land (so concentrating on the best cells is forced), which requires either (a) population that grows to resource-saturation (higher net growth / weaker demographic ceiling), (b) a circumscribed/bounded habitable area, or (c) the rich resource to dominate so strongly that concentrating beats dispersing even when empty land exists. GD-1 + aquatic + depletion are necessary substrate but not sufficient — **circumscription/saturation is the missing keystone.** NEXT: decide the circumscription lever before (or alongside) the camp/sedentism build.

## R-52 — Aggregation-sedentism: settlements as MULTI-BAND coalescence close the packing→morph chain (2026-07-04)

**Origin:** the R-51 keystone (no concentration without saturation) + two supervisor questions that reframed the whole approach — (Q1) *do settlements form from one band or from bands banding together?* and (Q2) *was regional density high enough — are we just too empty?* Blueprint `…_AggregationSedentism_Scoping.md`; built on the existing `_do_gathering` (marriage-aggregation) + fission–fusion machinery. Anchors: Mauss & Beuchat 1904/1979 (seasonal aggregation↔dispersal), Binford 2001 (forager↔collector logistical mobility; the 0.091/km² packing threshold is a *regional* density), Vita-Finzi & Higgs 1970 (site-catchment), Johnson 1982 (scalar stress), Testart 1982 (delayed-return storage), Ames 1994 / Bar-Yosef & Belfer-Cohen (NW-Coast / Natufian villages are multi-household).

**The lit answers, and what they told us to fix:** (Q1) villages form by **coalescence of several bands/households** at a rich node — the founding unit is ~100–300 people, not one ~25 band; so the between-band *cell* exclusion of the defensibility experiments (DE-10) was fighting the very coalescence that makes settlements. (Q2) sedentism onset clusters at/above ~0.091/km² and complex foragers ran ~0.5–5/km², while our equilibrium sits at ~0.015/km² — ~6× **below** packing → genuinely under-populated → the density must come from *aggregating* bands, not from forcing one band to pack.

**The mechanism — "the gathering that stops dispersing":** at a persistent-abundant site a seasonal pool (≥ `settle_min_pool` people within `settle_radius`) PERSISTS instead of dispersing → a settlement (form/hold/dissolve by proximity membership, hysteretic; robust to band churn). Two coupled pieces make it pack AND survive (both supervisor-identified): **(1) single-cell residence** — a village of dozens is « one 100 km² cell, so settled members pin onto the SINGLE site cell and settled families STACK there (overriding the footprint scatter) → residential density ≫ packing *automatically*; **(2) settlement-unlocked TIER-2 resource** — the site's yield gains an intensive catchment resource `= settle_tier2_yield × Σ_catchment S_pot`, GATED on settlement (a mobile band gets only the tier-1 cell return — which *also* explains GATE-3: reaches don't attract mobile bands because the payoff requires committing to settle). Residence≠foraging (Binford collectors) is what makes single-cell packing both correct AND safe — every prior single-band *tether* died because it coupled residence to foraging (pile up → starve on your own cell). RESOURCE-AGNOSTIC: `S_pot = aquatic_food` now, a `cultivability` source (proto-agriculture) drops in later — one field, many sources.

**Validation (aquatic mountainous-tropical world, A/B, 1 seed × 1200 steps, gathering ON both arms, only `enable_aggregation_sedentism` toggled):** OFF stays mobile (band_dens ~0.012, **0% packed**, no settlements, pop→444). SETTLE holds **2–3 persistent settlements (~110 people)**, **band_dens 0.19–0.34/km² (2–4× Binford packing)**, **%packed 38–75%**, morph fires (%complex 62–100%), and the **population survives and grows (100→248)** — no death-spiral, no starvation collapse. *For the first time the packing→morph chain closes:* climate→biome→economy → reach tier-2 → gathering → settlement persists → residents pack → morph → complex. Full suite 679 pass (12 aggregation-sedentism tests), default-OFF bit-exact through the harvest-core change.

**Caveats / OPEN:** single seed/world; provisional knobs (`settle_tier2_yield=40`, `catchment_radius=2`, `settle_min_pool=40`); %packed churns (38–75%) and settled pop (248) < free-foraging OFF (444) — settlements concentrate a subset and pay a density-disease cost (realistic — sedentism→disease — but uncalibrated). It is "complex," **not yet stratified** (hereditary rank needs scalar-stress→hierarchy + the deferred heritable-ownership→`cred` bridge). Tier-2 is currently **static → settlements never exhaust their catchment**, so there is no collapse/dynastic cycle yet. NEXT: **Layer 2b** — tier-2 depletion → central-place halo → collapse (the boom→bust) — then multi-seed calibration, then complex→stratified.

## R-53 — Layer 2b shock: fishery settlements are STABLE (storage buffers even multi-year regimes); the dynastic bust belongs to agriculture (2026-07-04)

**Origin:** Layer 2a settlements never exhaust their static tier-2, so they can only die demographically. Straightening the resource ecology (supervisor) corrected the "tier-2 depletes → bust" model: **fisheries ≈ sustainable** (salmon self-renews; NW-Coast villages stable for *millennia* — Ames), so their dispersal driver is a bad *year* that storage must buffer, not slow exhaustion; **soil-depletion + landesque-capital learning** are an *agriculture* phenomenon (deferred). Built the tractable core: a regional tier-2 **SHOCK** + the existing storage buffer → dispersal emerges on deficit. Blueprint §10b; `enable_tier2_shock` / `shock_cv` / `shock_rho`.

**SHOCK mechanism:** once per year a mean-preserving **regional lognormal** scales that year's tier-2 catchment yield (reuses the `game_meat_cv` draw; shared = a correlated climate bad year). Made **AR(1)** (`shock_rho`): ρ=0 = IID single bad years (bit-identical to the first draw), ρ→1 = multi-year good/bad **regimes** (ENSO/PDO/drought). This mattered: IID single bad years are trivially buffered (a bad year is followed by a good one — storage never tested); only *regimes* (runs of bad years) actually test the granary. Storage (`_cell_store`, already built — bank in good years, draw down in lean) is finally load-bearing.

**Finding (4 seeds × 1800 steps, harsh regime cv=0.6 ρ=0.85):** settlements are **STABLE / effectively permanent** — **0 dissolutions across all shock seeds** (IID and regime); settlements form early and never die (right-censored ages ~100–124 yr = run length). A settlement **rode out a severe multi-year bad regime** (shock 0.21–0.31) on storage. So storage fully buffers even ENSO-scale regimes → **the NW-Coast stable-village benchmark, reproduced.** (A lone dissolution in one earlier single-seed run did NOT reproduce — noise.) The shock is *not* inert, though: it **halves total population** (166 vs 544 no-shock) while the settled village rides through untouched — i.e. the shock hits the **mobile hinterland** and the **storing village is insulated** (villages hoard; the periphery bears bad years — a sensible dynamic).

**Interpretation + decision:** rich salmon reaches give *stable multi-generational villages*, not boom-bust — forcing fisheries to collapse from bad years would be wrong. The bulletproofness is partly `settle_tier2_yield=40` over-provisioning (~7× a village's need — never food-stressed), but the *qualitative* answer is anthropologically correct. **The acute dynastic bust (boom→intensify→degrade→relocate) is genuinely an AGRICULTURE / soil-depletion phenomenon** (Boserup 1965; Blaikie & Brookfield 1987 landesque capital), NOT a fishery one. Layer 2b (fishery) is **done**; the dynastic cycle moves to the **agriculture tier** (`cultivability` S_pot source + generational soil-depletion + learning). Default OFF ⇒ bit-exact; full suite 681. NEXT: scope + build the agriculture tier.

## R-54 — Agglomeration rework: catchment-economics FALSIFIED, point-superlinear is correct, the forage cap is the nucleation lever (2026-07-06)

**Origin:** the "grand-unification" rework (branch `gu-point-superlinear`) tried to replace the discrete settlement machinery (R-52) with ONE emergent mechanism — increasing returns to co-location under IFD. A fundamentals decomposition (per-cell force ladder) settled which form is right.

**Catchment form FALSIFIED (see DE-11).** The intended mechanism, R·L(n)/n with L(n)=n^α/(n^α+half^α), is a **saturating shared pot** → per-capita **peaks then congests** (∝1/n at scale) — the mathematical *opposite* of Bettencourt super-linearity (total ∝ N^β, per-capita ∝ N^(β−1) *rising*). The `α` in L is a saturation *sharpness*, NOT the scaling exponent β; we conflated them. In-sim, cranking `tier2` **monotonically reduces** packing (26→15%) — it's areal-dispersive (rewards fertile *catchment* not fertile *point*, diluting GRP's steep multiplicative gradient). A bug hid this at first: R was mis-scaled ~10⁴ too big (`level` kcal-capacity mistaken for a 0–1 fraction → R≈54M ≈18×S, defeating the forage cap). Fixed R = tier2·Σ(S_pot·cv_ref).

**The forage cap is the real nucleation lever.** `enable_forage_cap` (per-person intake ≤ forage_kcal·hours) is the solitude fix: clean multi-seed 2×2 → cap OFF **5.8%** packed, cap ON **31.7%**. It works by removing the lone-agent whole-cell over-reward so GRP's grouping drives concentrate agents. Non-monotone in cap (optimum ~cv≈5×BURN).

**Point-superlinear economics: SOUND but ASSEMBLY binds.** `aggl_mode="point"`: per-capita PREMIUM = A_cell·(n^(β−1)−1), 0 for a lone agent, *rising* with co-location (A_cell=tier2·S_pot·cv_ref, β≈1.15). Single-cell math predicts a band→village transition, but the SIM doesn't realize it from a spread seed (fragments) — because local greedy IFD (radius-1) has no gradient to *assemble* a village (a cell isn't lucrative until the crowd is there → first-mover/coordination failure). A **seeded** proto-village disambiguates: point-economics *holds* a pre-formed village (46.5% packed vs 37.3% baseline) → **economics sustains, assembly is the binding constraint.** Commits `dd54747`, `a7cf076`, `752b420`; 687 pass, default-OFF bit-exact.

## R-55 — Emergent village stack: hierarchy-gated fission ceiling + catchment site-appraisal → villages + emergent Carneiro circumscription (2026-07-06)

**Stage 1 — fission ceiling (`5ff44c0`).** The band machinery already encodes the Testart→Johnson chain (surplus→complexity morph→hierarchy unlock→scale) but caps it: `tolerable = base + (cap−base)·clamp[0,1](assabiyah+leader−repulsion)` makes `band_split_size=45` a HARD cap. `enable_village_scaling` lets net payoff *above* saturation add headroom past 45. Since assabiyah alone caps at 1 (= the hard cap), exceeding band scale **requires the leader term** → villages need HIERARCHY (Johnson 1982). Multi-seed: village-OFF pins MAXBAND ~42–43; village-ON scales bands to **55–77**, tunable, with %complex 82–94% confirming the morph→hierarchy chain does the work (not a free param); `repulsion` 0.3→0.5 shrinks villages 77→62 (scalar-stress balance live); reaches 77 from the *spread* seed (also eases assembly).

**Stage 1b — terrain movement metabolism (`8045d57`).** Relocating burns move_cost_kcal·cost[dest] (perceived in IFD + drained at metabolism). Physical scale = beneficial value: ~750 kcal (0.01·BURN) = a ~10 km move (50–75 kcal/km); at 750, packing 25.7→30.3%, pop healthy. Above it over-penalizes (per-step movement IS essential foraging). Prior baseline metabolism was terrain-flat and locomotion free; kept baseline ~fixed (Pontzer constrained-TEE) — terrain belongs on the *return* side (forage_kcal), climate on baseline metabolism.

**Stage 1c — catchment site-appraisal → emergent Carneiro (`c2deaad`).** A static central-place suitability field (Σ_catchment S_pot·exp(−λ·dist·(0.5+cost)), perceived) gives the global gradient local IFD lacked (Kennett-Winterhalder IFD-suitability). It steers agents to prime real-estate on every world (occ_suit up), but **concentration is scarcity-dependent (emergent Carneiro, not hardcoded):** flat (2028 cultivable, abundant) → occ_suit up but NO packing (spread among ~518 prime sites); mountainous (33, scarce) → FUNNELS (occ 97→76, %packed 19.8→26.5%, occ_suit +32%). Villages nucleate from the suitability gradient × resource **scarcity**. All default-OFF, 687 pass throughout.

## R-56 — The "land of plenty": pressure-driven mechanisms (Carneiro, Testart, storage) stay dormant on the abundant flat world (2026-07-07)

**Finding:** THREE scarcity-response mechanisms are correctly wired but **inert** on the flat-temperate test world for the SAME reason. (1) Circumscription packing (R-55) activates only where land is scarce. (2) Resource-dependent storability (`504df6d`; storable_fraction a per-cell grain/fish/forage/game blend — Testart) never separates: storable_fraction sets only the granary FILL RATE, but the CAP (3×reserve×n) binds and *both* storable and forage cells reach it from abundant overflow. (3) Even a deep lean (`ClimateField` a_seas=0.85, pop halved) leaves granaries FULL — the pop decline is fertility-driven, not starvation (storage buffers adults → granaries stay full → no survival differential). A key sub-finding: the village harnesses ran **seasonality OFF the whole time** (bare NPPCapacityField has no `.season()`); and even seasonal, the generous forage cap MASKS the lean (intake pinned at cv≈5×BURN through winter).

**Root cause = the world, not the mechanisms.** The flat-rich world + generous forage cap + modest granary cap = a **land of plenty** where the population never experiences real scarcity, so Carneiro/Testart/storage-selection have no trigger. Resource audit confirms over-provisioning: **14–20% of land cultivable** (vs a few % real) in **big blobs** (mean 1,200 km², largest 9,300 km²) rather than thin river-linked ribbons.

**Decision:** stop the parameter chase — the mechanisms are armed. The unlock is a **scarcity calibration** (scoped follow-on): a resource-realistic world (scarce river-ribbon prime land ~few %, deeper seasonality, higher granary cap so *filling* it is an achievement only storable sites manage, sharper storability floor). That single change should wake circumscription + storage + Testart *together*, to be re-validated then.

## R-57 — Scarcity calibration resolves R-56: emergent riverine villages; storability confirmed second-order (2026-07-07)

**Resolves R-56** (the "land of plenty" dormancy). Two stages.

**Stage 1 (`6bbd3eb`) — seasonality + hard-won storage.** The village harnesses ran **seasonless the whole arc** (bare `NPPCapacityField` has no `.season()`); wrapping the harvest in `ClimateField(a_seas)` activated it → store drawdown **20–26%** (was ~0% / saturated) — the lean season now genuinely draws granaries. Raising the granary cap (`store_capacity_reserves` 3→12; storage becomes hard-won) lifts packing 19→27%.

**Stage 2 (`…`) — resource-structured (river-ribbon) world.** Sharpened `cultivability` into thin ribbons along river channels (`cult·exp(−d2river/λ)`, injected into the mutable `WorldFields`) → prime arable **20%→6%** (scarce + linear, Nile-valley structure), making storable (river-grain) vs perishable (hinterland-forage) sites spatially distinct.

**WIN — emergent riverine villages.** On the scarce-ribbon world, **~50% of the population lives on the river ribbons** (only 23% of land) = **2× enrichment**, with 20–26% packing. Villages nucleate *on the rivers* via the circumscription + site-appraisal machinery (R-55) — the empirical cradle-of-civilization pattern, emergent, not hardcoded. This resolves the *circumscription* half of R-56.

**Storability CONFIRMED SECOND-ORDER (thread closed).** Even with seasonality (drawdown 20–26%) + hard-won storage (cap 12) + scarce spatially-distinct sites + an **18× storable/perishable contrast** (forage 0.05 vs grain 0.90), villages do NOT concentrate on storable sites (near-river flat 49→51%). Robust reason: `storable_fraction` is a fill-*rate* modifier, but granaries fill from abundant overflow regardless, and a 25% winter drawdown doesn't empty them → no survival/relocation differential; the site-appraisal (S_pot-driven) already sets settlement location. Storability gates complexity only in a **marginal** economy (scarce surplus), which the point-superlinear + forage-cap economy is not. Kept wired (default-OFF) as a correct-but-minor refinement. **Open:** promote the river-ribbon resharpening from harness to a flaggable `terrain.py` scarce-arable mode; a marginal-economy regime if storability is ever wanted load-bearing; Stage 2-military (assabiyah/warfare) for supra-village scale.

## R-58 — The finite resource (GD-1) is FULLY lit-anchored and working; "decorative depletion" was an over-diagnosis (2026-07-08)

**Context.** Investigating why the model shows a panmictic mating pool + one mega-cluster + no boom-bust (toward the Turchin campaign + emergent band/village sizes), I initially concluded the finite-resource depletion was "decorative / ~4–10× too weak" and proposed cranking `DEPLETE_FRAC`. Checking the literature anchoring (per supervisor) **reversed that conclusion.**

**The GD-1 resource model is anchored per-biome, end-to-end** (LITERATURE.md §GD-1; MODEL_SPEC §4.3.11; PARAMETERS §19.7):
- **Capacity** `K_persons` = **Tallavaara et al. 2018** NPP→density segmented regression (extracted from their SI, validated vs Dataset_4): 2–44 persons/cell, median ~21, on our world.
- **Recovery** `R_BIOME_PER_YR` = **Cortés 2016** (r_max ≈ 0.3–0.4/yr medium ungulate; megafauna slower) + **Coe et al. 1976** (game stock/production ∝ NPP); aquatic fast-restock 0.80.
- **Deplete→disperse mechanism** = the **central-place depletion-halo** papers (biorxiv 2024; PMC5645145/5373393) — Charnov marginal-value residential mobility.
- The one provisional constant, **`DEPLETE_FRAC=0.5`**, even has a rationale: it puts the stock at **B=0.5 (logistic MSY) when occupancy = the observed Tallavaara density** — i.e. the ethnographic equilibrium sits at half-stock. Principled, not arbitrary.

**Why it looked "decorative" (correct behaviour, not a bug).** Agents pack to ~37/cell — right at the rich-cell capacity (~44). At only 3–4K agents = **6–8% of the 52K world carrying capacity**, they cherry-pick the richest cells (IFD on a depleting resource) and, when forced over-capacity (stress test), **deplete a little then disperse to fresh land** (B settled ~0.79 because they *left* before hunting it out) — exactly the anchored marginal-value mobility. With abundant fresh land to escape to, no cell is fully hunted out and the population doesn't collapse.

**Implication (corrects the roadmap).** The emergent size-limiting and the Malthusian boom-bust are **latent in the anchored model** and **activate near regional carrying capacity** (the full-scale ~52K regime, no escape from depletion). So: **do NOT recalibrate `deplete_frac`** (it would override Coe/Cortés/Tallavaara/MSY). The genuine gate to observing emergent sizes + the secular cycle is **reaching scale** — i.e. the SoA/numba performance re-architecture (SiC_Games_ReArchitecture_Blueprint.md), not a resource change. `deplete_frac`/`recovery_scale` were made tunable (34ccbf8) but kept at their anchored defaults (bit-exact); they remain an experimental knob only.

---

## R-59 — Mountain-dominant worlds ARE producible via orogeny; the 0.317 ceiling was real but the fix is geometry+tree-line, not lowering the gate (2026-07-08)

**Context.** The pre-registered H-TERRAIN-ASYMMETRY finding (2026-06-13) held that mountain-dominant worlds are "not producible" (mtn_ceiling ≈ 0.317) and pre-registered "do NOT lower `mtn_elev_thresh`/`mtn_slope_thresh`." Revisiting it to give the model real mountain worlds.

**Two findings on re-examination:**
1. **The ceiling is *geometric*, deeper than a knob range.** "Mountain = high AND steep" is self-limiting because steepness IS elevation gradient — a large uniformly-high area (plateau/massif) is flat. Prototypes with boosted ridge weight and added uplift top out ≈ 0.34; real ranges are high-and-steep only on flanks/ridges. The pre-registration was *right*.
2. **The gate was never anchored.** The classifier's `slope` is the **per-world max-normalized** gradient (dimensionless, relative to that world's single steepest cell), not a grade; `0.72/0.18` are unanchored Stage-7 design constants (contrast the Tallavaara/Siler trails). And at 10 km/cell, physical slope on a real 4 km range is only ~1° (sub-grid) — a slope criterion can't represent mountain steepness at this resolution at all.

**Resolution (opt-in `orogenK`, the "redesigned generator" the finding deferred; default OFF ⇒ bit-exact).** Alpine is redefined as **above the tree-line** — barren because *cold-and-high*, an elevation/temperature property, the **Köppen 10 °C warmest-month air isotherm** (forest/alpine-tundra boundary, consistent with Körner & Paulsen 2004's 6.7 °C growing-season soil mean — a real lit anchor replacing the unanchored gate). The knob (a) adds an additive low-frequency **uplift massif** pre-normalization so a genuine range rises out of lowland, and (b) raises reliefAmpM ~+2 km so lapse-cooling drives the high core below the tree-line. On the `alpine` terrain preset: **maxElev ≈ 4074 m, prominence ≈ 2000 m** (real mountains, not a relabelled plateau). Alpine fraction is climate-graded (colder base → more of the *same* range clears the tree-line): **tropical ≈ 0.36, temperate ≈ 0.77, boreal ≈ 0.93–0.99** (4-seed medians) — a physical behavior the old gate could not produce. Habitable (1500 founders): tropical 3/3 seeds survive (pop ~1100–1300), temperate 3/3 (sparse, one near-death), boreal 2/3 (marginal — a cold ~all-alpine massif); **band size ≈ 26–33** in mountain worlds (bigger than lowland ~23 — risk-pooling in the harsher, higher-variance environment).

**Tree-line anchor correction (2026-07-08, same day).** The first draft used **6.4 °C**, which was Körner's *growing-season soil* value mis-slotted into the model's *warmest-month air* field. Web-verified and corrected to the **Köppen 10 °C warmest-month air** isotherm; this lowered the tree-line on the massif, raising temperate alpine 0.59→0.77 (the numbers above are post-correction).

**Bookkeeping.** `mtnK` (an earlier crude threshold-drop attempt) was replaced by `orogenK`. Default (`orogenK=0`, absent from every existing preset) leaves elevation, relief, and the high∧steep classifier byte-identical ⇒ the 0.317 ceiling remains exactly true for all default worlds; only the explicit `alpine` preset exceeds it. Full suite 687 pass / 1 xfail. Docs synced: PARAMETERS §12.1/§12.2, ARCHITECTURE §9.5.1a, HYPOTHESES §H-TERRAIN-ASYMMETRY, LITERATURE (Köppen; Körner & Paulsen 2004).

---

## R-60 — Substrate scale run A: soft overshoot (not boom-bust), villages emerge at ~56 (validated), and the morph's SURPLUS GATE is inert (mis-scaled) → stratification is packing-blocked, not surplus-blocked (2026-07-09)

**Setup.** First scaled substrate run (`outputs/substrate_run/run_substrate_A.py`) after the pre-run audit + Cahill
reserve anchoring. One **coastal-temperate** diverse world (forest 34/grass 55/desert 6/water 6, 722 river cells,
relief 0.33 — deliberately NOT flat), `emergent_village_demog` + genome-on/exogamy-off, seasonal-but-no-regime climate
(endogenous only). 4000 founders → 6000 steps (~500 yr). Logged the audit Gate-1 derived metrics every 25 steps.

**Q1 — overshoot vs glide → SOFT OVERSHOOT then gentle secular decline (NOT boom-bust).** Pop 3914 → peak **~6970**
(+78%, ~step 1500-2000) → slow relaxation to ~4850; mean reserve held **~0.36 throughout** (no mass starvation).
This is the **energetic-fertility self-limiting** working as designed: at reserve 0.36 the fertility factor =
(0.36·130k−20k)/(130k−20k) ≈ **0.24**, so births run at ~¼ max fecundability — the population caps softly before
reserves reach the starvation floor. No Turchin cycles (that layer isn't built); the soft-landing design also
suppresses Malthusian boom-bust. A slow decline over steps 2000-6000 (likely depletion of packed village cells).

**Q2 — stratification → COMPLEXITY saturates ~90%, STRATIFICATION 0% — but the reason is NOT "no surplus".**
Initial reading ("surplus never reaches 0.7") was WRONG. Diagnostic (400-step run-A config): `_band_surplus` median
**6.3**, max 14.3 — **127/127 bands ≥ 0.7**. Surplus is abundant, not scarce. **The `surplus_frac` metric is
mis-scaled** (`phase1_model.py:1220,1285`): per-cell granary cap ∝ TOTAL cell occupancy, but `surplus_frac =
Σ(whole-cell granaries over the band's footprint) / (band members n)` — so a band sharing/spanning cells with other
agents scores `Σ cell-occupancy / n` ≈ 6-14 instead of the intended 0-1. Consequence: **the morph's surplus gate is
INERT (always true)** → the "surplus≥0.5 → complex" test fires for everyone (∴ the ~90% complex is trivial, not a
finding), and "packed AND surplus≥0.7 → stratified" reduces to **packed alone**. Stratification is 0% because bands'
per-band footprint density (members / occupied-footprint) stays **below Binford 0.091/km²** — they spread over too
many cells to read as packed — NOT because surplus is lacking. **So the real stratification blocker is the PACKING
gate + a broken surplus normalization, not a missing surplus engine.**

**Emergent village size → VALIDATED.** ~34-44 villages sustained; **median 56, max 94-108 — squarely in the Bar-Yosef
50-150 range.** `village_gain=5.0` produces ethnographically-correct village sizes, emergent (R-55 mechanism), not a
tuned artifact. The `village_gain` check passes.

**Structure / genetics.** Semi-discrete (villages = dense packed nodes 37-75/cell; landscape ~60% occupied — denser
than the old continuous smear but not yet sparse-bands-in-empty-land, which needs true-capacity circumscription).
Genome N_e healthy: H 0.999→0.985 over 500 yr (slow drift), mean relatedness →0.016 (large outbred network).

**Actions (opened by this run):** (1) FIX the `surplus_frac` mis-scaling (branch; make it a real 0-1 band-share
fraction) so the morph's surplus gate discriminates again — until then %complex/%stratified are not interpretable.
(2) Relax the fertility self-limiting toward a lit-anchored sedentism/society-dependent model (Neolithic Demographic
Transition — Bocquet-Appel 2011; Sellen & Mace 2007) so sedentary/complex groups grow faster (the real demographic
engine) and can overshoot → bust / accumulate. (3) Re-examine whether per-band packing is the right stratification
driver. THE RUN WAS VALUABLE precisely because it surfaced the inert surplus gate — a bug the small validation runs
never exposed.

---

## R-61 — A2 (surplus-gate fix + NDT sedentism fertility): overshoot-and-bust with a COMPLEXITY CYCLE emerges; stratification is density-blocked (carrying-capacity < packing), not a bug (2026-07-09)

**Setup.** Re-run of R-60's substrate run with two fixes (branch `dynamics-fix`): (1) the `surplus_frac` mis-scaling
fixed → real 0-1, gate discriminates (30% bands ≥0.7); (2) **NDT sedentism fertility** ON (society-dependent
lactational refractory: egalitarian 30 → complex 22 → stratified 14 mo; Howell/Sellen&Mace/Bocquet-Appel). Same
coastal-temperate world, 4000 founders, 6000 steps. Full suite 698 pass (both fixes bit-exact on the tested paths).

**Both fixes work.** (a) `%complex` is no longer a trivial ~100% artifact — it's a dynamic 40-94% tracking real
packing+surplus. (b) Sedentism fertility turned R-60's soft glide into a genuine **overshoot-and-bust**: pop 3914 →
**peak 9468** (@step 1600; vs R-60's 6970) → starvation bit (**62 deaths/step peak**) → correction to ~5400 (CV 0.16
→ **0.23**).

**NEW — a COMPLEXITY CYCLE.** Villages/complexity rose during the boom (85% complex, 53 villages) then **collapsed
during the bust** (10%, 5 villages) as villages dissolved (morph de-morph tracking the demographic collapse). A
proto-secular-cycle in **social complexity**, emergent from demography + the morph **with no elite/instability layer**
— the first Turchin-flavored rise-and-fall the model has produced. Gini cred rose 0.278→0.317 during the boom.

**Villages VALIDATED again:** median 53-61, max ~100 — Bar-Yosef 50-150 (`village_gain` holds across the re-run).

**Stratification still 0% — CONFIRMED density-blocked, not surplus/fertility-blocked, and NOT a bug.** Diagnostic
(6000 agents, 600 steps): **0/219 bands packed** — per-band density max **0.037**, median **0.017**, vs Binford
0.091/km². 75/219 bands have surplus ≥0.7 (surplus fine); **0/219 satisfy BOTH.** Two layers: (i) the "packed" MEASURE
is mis-specified — `band members / footprint` = a band's density over its ~14-cell range (~0.017 = a *normal forager*
density), but Binford's threshold is a LANDSCAPE population density; (ii) even the REGIONAL density at the 9468 peak =
**0.060/km², still < 0.091**. **Interpretation (Carneiro/Binford): this is CORRECT — a normal-richness forager world
sits below packing → egalitarian, as most ethnographic foragers were.** Stratification needs carrying-capacity >
packing, i.e. exceptionally rich land (dense storable aquatic / agriculture), ideally naturally circumscribed (Nile
floodplain) so population concentrates. **Circumscription should EMERGE from realistic terrain, not be imposed** (per
supervisor).

**Actions (next, branch):** (1) fix the packing measure → LANDSCAPE population density (`total agents on the band's
cells / area`), the correct Binford quantity — lets a genuinely dense village cross packing. (2) Run on `scarce_arable`
river-ribbon worlds (emergent Nile circumscription) to test whether stratification fires where rich land is naturally
bounded. NO imposed circumscription knob.

**RESULT (`enable_landscape_packing`, opt-in default-OFF):** the measure fix ALONE fires stratification on the plain
realistic coastal world — **STRAT 0.0% → 15.4%** (same pop ~8180), and it DISCRIMINATES (egalitarian ~9% / complex 76%
/ **stratified 15%** = a real emergent complexity gradient, not everyone flipping). Circumscription is NOT needed:
imposing `scarce_arable` (river-ribbon) actually LOWERED stratification to 3.1% (it cut total pop/villages 8180→4779).
Confirms the Carneiro reading operationally — stratification emerges from realistic dense terrain once "packed" is the
correct LANDSCAPE density; the old band-members/footprint measure was the sole blocker. The 0.091 Binford threshold is
untouched (verified correct, R-59).

**A3 full run (6000 steps, sedentism + landscape-packing ON) — stratification EMERGES but is TRANSIENT; inequality
couples to pressure (proto-Turchin), sustained stratification is the open problem.** Pop 3914 → peak 9673 (@s1525) →
6061 end. **Stratification: peak 18.2%, mean 3.7%, end 1.2%** — it ROSE during the early boom (11% @s1000 when cells
packed hardest, occ 99/cell) then COLLAPSED as the population relaxed and cells DE-PACKED (occ 99→32). A single
rise-and-fall, not sustained. **Coupling: corr(pop, Gini)=+0.45, corr(stratified, Gini)=+0.31** (inequality rises with
population pressure AND stratification — the immiseration signal Turchin needs); corr(pop, stratified)=+0.02 (near
zero — OUT OF PHASE: stratification leads on the rising density, pop peaks later; stratification tracks PACKING not the
pop level). **Why it doesn't sustain — VERIFIED (2026-07-09): IFD DISPERSAL, not soil.** The proto-ag/soil hypothesis (both
supervisor's and Claude's) was FALSIFIED — `_settlement_sites`=0 the whole run (the swidden soil machinery is inactive
under `emergent_village_demog`; villages come from agglomeration+band-morph). Real driver: the population SPREADS to
fill the landscape (occ_cells 641→1067 as pop grows), so local density → the sub-packing regional average (~0.06/km²)
and the stratified cores de-concentrate → de-morph (absolute N_stratified 1219→51, not just the fraction). GD-1
depletion ACCELERATES but is not the cause (depletion-OFF A/B still collapses, peak 28%→4.9%). The early stratification
is a TRANSIENT of the concentrated founder placement. **Same root as R-54 "assembly binds" and the original
"continuous spread."** To SUSTAIN: hold local concentration AGAINST IFD dispersal — emergent circumscription
(terrain-bounded rich land) or stronger agglomeration/defensibility — NOT soil-renewal. (Agent EXPERTISE / heritable
skill is orthogonal: it makes re-adaptation cheaper ⇒ if anything eases dispersal, not concentration.)

---

## R-62 — Villages dissolve because RESIDENCE≠FORAGING is switched off, not for want of payoffs: the utility optimum is a BAND (n=15) by construction; restoring the catchment inverts the dynamics (concentration + 50% stratification) — and revises R-54's "assembly binds" (2026-07-09)

**Question (supervisor).** Sustained concentration needs *mechanisms with a real payoff* — villages should buy personal
security, a share in stored food, stable dwellings, societal life — not perception hacks. Which of these exist?

**Measured payoff ledger (movement decision, `diffusion_select_target`).** COSTS are real and uncapped
(`density_disease` ON, `dens_delta=3.0` ⇒ up to ×4 mortality; `size_repulsion` ON; depletion halo). PAYOFFS are capped,
gated or invisible: `group_safety` saturates at `g_s=15`; mating caps at `g_mate=15`; the **granary is absent from the
decision**; **security never affects mortality** (group size only multiplies yield); **dwellings/built capital don't
exist**; the agglomeration premium `Rv·(n^{β−1}−1)` is the ONLY village-scale term and is gated to `S_pot` (rich cells).
The `enable_economic_defensibility` tether is, by its own docstring, **"a perception change only"** — and inert anyway
(A/B: only 3–14 cells ever claimed; occ_cells 889 vs 899 — no effect).

**THE DECISIVE MEASUREMENT — utility vs group size on a real packed cell** (S=1.70 M, forage_cap=144.5 k, g_s=15):
n=10 → 575 k; **n=15 → 743 k (PEAK)**; n=25 → 566 k; **n=58 (the actual village) → 316 k**; n=120 → 185 k.
**The utility-maximising group is 15 — a BAND.** A villager at n=58 *doubles* their payoff by leaving for a 15-cell.
Safety saturates (×9 by n≈60) while per-capita forage falls as `S/n`; the granary term is a per-capita constant (57 k).
**Villages are strictly dominated.** Every anchor tried (tether ×6, standing, granary) was attempting to bridge a
**427 k kcal** gap with **57 k** terms — hopeless by construction.

**ROOT CAUSE (physics, not payoffs): `ypc = S/n` makes 58 people eat ONE 100 km² cell.** Real villages RESIDE at a
point and FORAGE A CATCHMENT (Binford logistical collectors; Orians & Pearson central-place foraging). The model knows
this — `"Layer 2 RESIDENCE PIN: … residence ≠ foraging; its food comes from the catchment tier-2, not the cell it
stands on"`, `"a village « one 100 km² cell"` — but the machinery (`enable_aggregation_sedentism`, catchment radius 2 =
25 cells, `settle_tier2_yield`) is **OFF** in `emergent_village_demog`, and additionally requires
`enable_marriage_aggregation` (settlements are founded inside `_do_gathering`). Hence `_settlement_sites=0` in every
run of this session (also explains R-61's falsified soil hypothesis).

**REVISES R-54.** The agglomeration rework replaced the settlement machinery (which HAD the catchment) with a
point-superlinear premium `A·n^{0.15}` on a single cell. That premium rises **×1.2** from n=15→58 while per-capita
forage falls **×3.9**. R-54's "*economics sustains, assembly binds*" is better read as: **assembly binds because a
village standing on one cell is a starvation trap.** The economics only ever held a PRE-SEEDED village that had not yet
felt the dilution.

**RESTORING THE CATCHMENT INVERTS EVERYTHING** (600 steps, coastal-temperate, landscape-packing + sedentism):
| arm | pop | occ_cells | occ_max | sites | %stratified |
|---|---|---|---|---|---|
| baseline (one-cell forage) | 4077 | 538 | 72 | 0 | 19.4 |
| gathering only | 8010 | 853 | 125 | 0 | 15.3 |
| **+ catchment (residence≠forage)** | **12715** | **209** | 1930 | **21** | **50.5** |
| + catchment + store + standing | 12224 | **165** | 2034 | 19 | **58.8** |
Occupied cells COLLAPSE 853→209 (population concentrates into 21 settlements), capacity triples, **stratification
50.5%**. Dispersal stops. **The payoff anchors then WORK on top** (occ_cells 209→165, strat 50.5→58.8%) — they were
never wrong, merely swamped by the 1/n collapse.

**NEW PROBLEM = THE ORIGINAL ONE.** `occ_max = 2034` — villages average ~600, up to ~2000, vs Bar-Yosef's ethnographic
**50–150**. This is precisely the supervisor's very first observation ("*why do we have a few thousands piling up on
adjacent cells?*"). Two failure modes: catchment OFF ⇒ one-cell starvation trap ⇒ continuous spread; catchment ON with
`settle_tier2_yield=40.0` [PROVISIONAL — sweep] ⇒ mega-villages. The truth is between.

**Built this session (branch `payoff-anchors`, both default-OFF, bit-exact):** **P6 STANDING** — relational social
capital as a 3rd `base_status` facet, tenure-built (Wiessner 1977 hxaro: ≥1 yr of reciprocal exchange to become
"firm"), forfeited on leaving; it gates harvest share, granary draw AND mate choice. It cannot anchor alone (a relative
weight CANCELS on an empty cell: `ypc = S·w/(Wsum+w)` → `S` when `Wsum=0`) but it does produce the correct **SELECTIVE
dispersal** (low-standing squeezed out; established stay). **P1 STORE ANCHOR** — the band's COLLECTIVE granary valued
only on the community's own cells (a stranger has no claim); an absolute place-bound value that does not cancel
(Testart delayed-return). First cut was buggy (ungated + per-capita ⇒ rewarded moving to a *less crowded* cell) — fixed.

**NEXT:** calibrate the catchment economy (`settle_tier2_yield`, catchment radius) + costs (scalar stress,
density-disease, depletion halo) so **village size EMERGES at 50–150** — payoff-vs-cost, exactly as band size emerged
from risk-pooling-vs-competition. Then P2 (security-as-mortality, repairing the density_disease asymmetry) and P5
(built capital / dwellings).

---

## R-63 — Emergent village size = Bar-Yosef 50–150 ACHIEVED (median 88, 100% in band) with catchment ON + the UNBOUNDED point-superlinear agglomeration OFF; `n^1.15` is the mega-village bug (2026-07-09)

**Context.** Following R-62 (restoring residence≠foraging inverts dispersal → concentration + stratification but
`occ_max=2034` mega-villages). Question: calibrate village size to 50–150. First plan was to sweep `settle_tier2_yield`
(catchment food, PROVISIONAL=40).

**FALSIFIED that plan (measurement).** `settle_tier2_yield ∈ {1,2,5}` at catchment radius 1 gave **byte-identical**
runs (pop 22406, villages med 3832) — the catchment FOOD term is negligible (`S_pot=max(aquatic,cultivability)≈0` on
the forest cells where villages form; it only pays near water/arable). The mega-villages are fed by the **AGGLOMERATION
premium** `S += aggl_R·(n^β − n)` (phase1_model.py:1191–1196; β=1.15, point mode) — **point-superlinear and UNBOUNDED**:
per-capita output RISES with n forever (n^1.15 at n=3800 ≈ 15,700). The residence pin removed the `S/n` forage-dilution
brake that previously balanced it ⇒ runaway.

**A/B (catchment ON, agglomeration ON vs OFF, 800 steps, coastal-temperate):**
| | villages med/p90/max | in 50–150 | strat | pop |
|---|---|---|---|---|
| aggl ON (n^1.15) | 3832 / 5607 / 5608 | 0% | 34% | 22406 (exploding) |
| **aggl OFF** | **88 / 101 / 102** | **100%** | 4% | 881 (stable) |
**Emergent village size lands EXACTLY at Bar-Yosef 50–150 (median 88, 100% in band) with no fitting** — it falls out of
catchment carrying capacity minus scalar-stress cost, as band size fell out of risk-pooling minus competition. The
unbounded `n^1.15` was the sole thing breaking it.

**But neither endpoint is right — the tension is now clean.** aggl OFF → correct size but strat only 4% and population
DECLINES (3000→881: the increasing-returns economy that made villages worthwhile + generated surplus is gone). aggl ON
→ runaway. **The middle = increasing returns that SATURATE at the catchment's carrying capacity** — Bettencourt's own
caveat that R-54 recorded but never applied (*"a subsistence village has a resource ceiling a modern city does not"*).
The point-superlinear premium is missing that ceiling.

**REVISES R-54 further:** the point-superlinear premium isn't merely "assembly-binds" — it is **UNBOUNDED**, so once
assembly is solved (residence pin) it runs away. It needs a resource-ceiling saturation.

**NEXT (proposed, awaiting sign-off):** cap `A·(n^β − n)` at the catchment carrying capacity (≈ catchment_cells ×
Tallavaara/cell) so returns rise → saturate → scalar stress caps size. Predict: village size stays 50–150, but rich
(aquatic/arable) catchments accumulate surplus → stratify, poor (forest) stay small egalitarian — the NW-Coast-vs-
interior pattern — with population sustained.

**CATCHMENT CEILING BUILT + TESTED (`enable_catchment_ceiling`, default-OFF, bit-exact).** Total settled-cell food
capped at `catchment_ceiling_mult · Σ(sustainable cell yield over catchment)` — a village can't out-produce its land
(the resource ceiling R-54 flagged). **Result: STOPS the runaway** (pop 22406→3391 stable; villages med 3832→~450;
occ_max 3514→~390). ✓ **But two things remain, and they REFRAME the problem:**
1. **Villages sit AT the ceiling (~450, 3× Bar-Yosef), and stratification COLLAPSED to ~2%** — because a village at its
   food ceiling has per-capita = subsistence, i.e. NO surplus (surplus needs population BELOW the food max; Testart/
   Hayden). The ceiling that stops runaway also removes the surplus that drives stratification.
2. **Scalar stress does NOT cap settlement size** — `repulsion_gain` 0.3→1.0→2.0 left villages ~417–511 (the movement
   pins agents onto the settlement SITE via the residence pin; `size_repulsion` acts on BAND fission, a different
   quantity). So the assumed "cost that bites at 50–150" isn't wired to settlement occupancy.

**HONEST STATE (5 relocations of the lever this thread — consolidating):** the CLEANEST emergent village size (median
88, 100% in 50–150) is the **agglomeration-OFF** result (R-63 table) — the catchment alone sizes villages correctly;
the point-superlinear premium is the inflator, and even bounded by the ceiling it pulls villages up to the catchment
capacity (~450). So the real fork is: **(A)** drop the agglomeration social-returns for villages (option 2) — villages
= ~88, and surplus/stratification comes from the resource **tier-2** on rich (aquatic/arable) catchments only (forest
villages small egalitarian — the realistic NW-Coast-vs-interior split); **(B)** keep agglomeration but the ceiling must
be sized to the ETHNOGRAPHIC foraging radius (~5 km ≈ radius 0–1, Vita-Finzi & Higgs), not a 900 km² radius-1
catchment, so the ceiling itself is ~50–150; **AND** wire a real cost (or the tier-2 surplus gap) so villages sit
BELOW the ceiling → surplus → stratification. This is a genuine open design choice, not a knob-tune.

---

## R-64 — Option B: settlement scalar stress (Johnson, hierarchy-dissipated) completes the emergent settlement hierarchy — village size ≈ Bar-Yosef 50–150 + a bounded stratified-center tail, STABLE over 2000 steps, and it also fixes A3's transient stratification (2026-07-09)

**The fix (R-63 fork B).** The residence pin pulled every nearby agent into a settlement unconditionally → no size
cap → villages grew to the food ceiling (~450) without stratifying. `enable_settlement_scalar_stress` (default OFF,
698 pass bit-exact): an over-crowded settlement REPELS agents from the residence pin with probability
`size_repulsion(village_pop, midpoint=150, society)` — Johnson 1982 scalar stress, scaled by the EXISTING
`REPULSION_SOCIETY_FACTOR` (egalitarian 1.0 / complex 0.5 / stratified 0.25). Wired to the **residence pin** (where
settlement growth actually happens), NOT the band-fission `size_repulsion` (which does nothing to settlements — the
lever mislocated for 5 iterations; utility-decompose before building, VERIFICATION_LOG).

**The loop closes** (each rung already lit-anchored): scalar stress caps an EGALITARIAN village ~150 (Johnson) → the
catchment ceiling (R-63, Tallavaara) leaves a food surplus (ceiling > capped pop) → surplus morphs the village to
hierarchy (Testart) → hierarchy dissipates scalar stress (society factor 0.25) → it grows into a larger stratified
center (Carneiro).

**RESULT — STABLE over 2000 steps (~167 yr), coastal-temperate, catchment radius 1** (village = site-cell occupancy):
| step | pop | village med/p90/max | in 50–150 | strat |
|---|---|---|---|---|
| 400 | 4885 | 64/133/233 | 63% | 29% |
| 800 | 7151 | 101/134/282 | 77% | 7% |
| 1200 | 7733 | 97/151/255 | 77% | 13% |
| 2000 | 7210 | 102/154/241 | 77% | 9% |
Population PLATEAUS (~7200, no runaway); **village size median ~100, p90 ~154, 77% in Bar-Yosef 50–150**, with a
**bounded** stratified-center tail (~240); **stratification SUSTAINED 9–16%**. The distribution is the predicted
bimodal Johnson pattern (a mass of egalitarian villages capped ~150 + larger stratified centers).

**ALSO FIXES A3's TRANSIENT STRATIFICATION (R-61):** A3's stratification collapsed to ~1% because the "villages" were
transient packing that de-concentrated via IFD dispersal. Here stratification PERSISTS (9–16% at step 2000) because
villages are stable CATCHMENT-ANCHORED settlements (residence pin + scalar-stress equilibrium), not transient packing
— the concentration is held by a real mechanism, so the stratification it drives is durable.

**THE EMERGENT SETTLEMENT HIERARCHY IS COMPLETE** on realistic worlds, each rung emergent-from-mechanism (not
hardcoded) and lit-anchored:
- **band ≈ 24** ← ~~risk-pooling vs competition (Winterhalder/Wobst; emergent-band-size v3)~~
  **[CORRECTED 2026-07-16, R-72 — this attribution was FALSE.]** The config for this run (listed below) does
  **not** include `enable_emergent_band_size`; the flag was default-OFF and contributed nothing. The ~24 came
  from `repulsion_midpoint = 25` — the hardcoded midpoint of the Johnson scalar-stress logistic, which is the
  term that actually sets band size. **The number came out at 24 because it was put in at 25.** So the band was
  the ONE rung in this list that was hardcoded, under a banner claiming none were. The other three rungs are
  unaffected. R-72 rebuilds the mechanism and un-pins the midpoint; band size is emergent-from-mechanism only
  from R-72 onward, and even there the environmental gradient is weak (see R-72's limitations).
- **connubium ≈ 500** ← mate-availability under kin exogamy (Wobst; Cut 1/2, opt-in)
- **village ≈ 50–150** ← catchment carrying capacity vs Johnson scalar stress (Bar-Yosef; R-63/R-64)
- **stratified centers (to ~240) + ~10–16% stratified** ← surplus (ceiling − pop) → hierarchy (Testart/Carneiro/Johnson)

**Branch `payoff-anchors` (off dynamics-fix), local-only, all opt-in/default-OFF, 698 pass.** The realistic
"everything-on" village config = `emergent_village_demog` + `enable_marriage_aggregation` + `enable_aggregation_
sedentism` + `enable_catchment_ceiling` + `enable_settlement_scalar_stress` + `enable_landscape_packing` +
`enable_sedentism_fertility` (+ optional genome/exogamy). **NEXT (calibration, not structural):** the population
plateau (~7200) and strat level (~10–16%) vs world richness; catchment radius vs Vita-Finzi & Higgs; then the Turchin
elite/instability layer now has a stable stratified substrate to act on.

---

## R-65 — Validating the emergent-stratification prediction: village size ROBUST across worlds + within-world "stratified-on-richer-catchments" CONFIRMED; the cross-world %strat correlation is UNDERPOWERED (my claim over-reached) (2026-07-09)

**Test (supervisor chose validate-before-campaign).** Full R-64 settlement config across a richness-ordered set (7
worlds × 2 seeds × 800 steps): coastal/flat/hilly × tropical/temperate/boreal. `validate_stratification.py`.

**Result — 2 of 3 predictions hold; the cross-world one does NOT (a useful catch):**
1. **Village size 50–150 is EMERGENT + ROBUST across worlds** — median 61–106 in *every* non-extinct world. R-64 was
   not a coastal-temperate fluke. ✓
2. **WITHIN-WORLD: stratified settlements sit on RICHER catchments than egalitarian** — S_pot 0.892 vs 0.791, **6/7
   worlds** strat>egal. The causal mechanism (surplus from rich land → hierarchy) is confirmed cleanly (isolates the
   mechanism without the cross-world population confound). ✓
3. **CROSS-WORLD: %stratified vs richness — NOT confirmed.** corr(mean_npp,%strat)=−0.28, corr(aquatic_frac,%strat)=
   −0.15 (I predicted POSITIVE). CAUSE = the aggregate `%stratified` is swamped by (a) huge SEED VARIANCE (same world:
   coastal-temp 7.4% vs 23.8%; hilly-temp 0.8% vs 23.1% — 30×) and (b) SMALL-POPULATION artifacts (the largest value,
   hilly-boreal 73.8%, is a pop of 1019 — 1–2 settlements dominating; it drags the corr negative), plus (c) an 800-step
   snapshot of a time-FLUCTUATING quantity (R-64: strat wobbles 7–29% on one world). Strip the small-pop outlier and a
   coarse signal exists (poor BOREAL worlds mostly 0% — flat-boreal 0/0, hilly-boreal s1 0 — vs richer 7–24%), but with
   2 seeds it is UNDERPOWERED, not clean. **Not falsified; my confident cross-world claim over-reached — the test
   caught it. Proper test: more seeds + longer runs + population-controlled/absolute-count metric.**

**Refinement (better than the original prediction):** stratification tracks STORABLE/aquatic resources, NOT raw NPP —
**flat-tropical has the HIGHEST NPP (2397) but ~0.8–2% stratification** (rich forest isn't storable). That is Testart's
delayed-return thesis produced emergently, and it is the correct anthropology (rich-forest foragers stayed egalitarian;
NW-Coast aquatic stratified). So the cross-world axis should be STORABILITY, not productivity — and even that needs the
better-powered test to show cleanly.

**Verdict:** the settlement-size emergence and the surplus→stratification CAUSAL mechanism are VALIDATED; the
cross-world aggregate %stratified is an inherently noisy quantity that this 2-seed/800-step battery cannot resolve.
Value of validate-first: a confident prediction was corrected BEFORE spending a long campaign on it.

---

## R-66 — The deep-time CAMPAIGN (15,000 steps ≈ 1,250 yr, fully instrumented): the substrate CONSOLIDATES, it does not cycle; economic defensibility is the pivot between single-dynasty fixation and multi-dynasty pluralism (2026-07-13)

**Setup.** Two parallel arms on coastal-temperate, 3,000 founders × 15,000 steps, endogenous (seasonal climate, NO
regime forcing), full R-64 settlement stack + genome + genealogy. **OFF** = the validated substrate; **ON** = OFF +
economic-defensibility (Dyson-Hudson & Smith; the instability channel). `run_campaign.py`; ~114 min/arm; genealogy
1.05M / 1.11M birth-death rows streamed (bounded memory). Analysis `analyze_campaign.py`.

**Headline: neither arm produces secular cycles.** Both overshoot mildly then relax to equilibrium — 0 stratification
swings (>10%) in the capacity phase. The validated substrate does **not** self-organize into Turchin secular cycles; it
CONSOLIDATES. Genuine aggregate cycling would need an explicit elite/instability coupling (option 3). *But* the ON arm
shows dynasty-level TURNOVER (below) — elite competition without a single winner — the seed a cycling layer would build on.

**The pivotal finding — economic defensibility flips the dynastic outcome:**

| | OFF (validated) | ON (+defensibility) |
|---|---|---|
| Population endpoint | overshoot 7,914→6,008, settle ~6,400 (mild bust) | glide 7,847→6,589→7,206 (**no bust**) |
| Sustained stratification (cap-phase) | **7.0 %** | **14.4 % (≈2×)** |
| Dynastic outcome | **1 patriline @ 88.6 %** (winner-take-all) | **~3 dynasties, top 45 %** (pluralistic) |
| eff_lineages (patriline) 2913 → | **1.3** | **3.3** |
| top_share trajectory | monotone 0→0.89 (fixation) | oscillates 0.61→0.42→0.42→0.50 (**turnover**) |
| Instability (contest events/step) | 0 | **42** |
| gini_cred (final) | 0.265 | 0.309 |
| Individual reproductive skew | 37 % childless, RS-gini 0.66, max 81 | 37 % childless, RS-gini 0.66, max 68 |
| Neutral genome H 0.999 → | 0.884 | 0.868 |

**Reading.** (1) **Defensibility sustains pluralism + hierarchy.** Without a conflict channel, drift under strict
patriliny drives WINNER-TAKE-ALL: one "house" fixes to 88.6 % and stratification decays to ~7 %. Defended resource
patches PARTITION the landscape → ~3 competing dynasties coexist (top 45 %), stratification holds ~2× higher, inequality
and population are both higher and more stable. Defensibility is the difference between "one house rules" and "competing
houses." (2) **Stratification is a founder TRANSIENT in both** — peaks ~50 % at step ~300 (concentrated placement),
then decays to the capacity equilibrium (7 % / 14 %); confirms the A3 transient over deep time. (3) **Individual
reproductive skew is universal and severe** (37 % childless, RS-gini 0.66, one man 68–81 children) and INDEPENDENT of
defensibility — elite overproduction is individual (mate-choice/polygyny); its DYNASTIC consequence is what the regime
sets. (4) **Patrilineal-name fixation ≠ genetic fixation** — the `_lineage` patriline fixes to 1 (OFF) while the neutral
autosomal genome stays diverse (H 0.88): non-patrilineal maternal alleles keep flowing even as one surname dominates. A
correct, subtle pop-gen result, visible only because the genome layer was on.

**Method note.** Every dynasty-level quantity here (fixation curves, RS distribution, name-vs-gene divergence,
pluralism-vs-fixation) was INVISIBLE before the campaign diagnostics + genealogy layer (this session). Validate-then-
instrument-then-run paid off: the smoke's "2× stratification" was real (it is the capacity-phase equilibrium, 14.4 vs
7.0), not an artifact — it was masked at step 250 because both arms were still in the founder transient.

**Open forks.** (a) Elite/instability layer (option 3) to test whether the ON arm's dynasty turnover can be amplified
into true secular cycles. (b) Defensibility params are PROVISIONAL (`D_min` 0.15, dwell 6, min 3) — the 2× effect
motivates anchoring them. (c) connubium reach plateaus ~146–181, below Wobst ~475 — the adaptive-connubium (Cut 2)
search may be needed to reach the ethnographic mating-network scale.

---

## R-67 — The connubium is load-bearing for BOTH dynasty and demography: Cut-2 (adaptive exogamous mating) robustly BREAKS the winner-take-all fixation but flattens reproductive skew → Malthusian boom-bust at every reach; the lit anchor was wrong (475 → MVP ~150) but that is a correctness fix, NOT the bust fix (2026-07-13)

**Why.** R-66's OFF arm fixated to a single patriline (top-share 0.89) under the fixed-radius Cut-1 gathering. Hypothesis:
that fixation is a small-connubium DRIFT artifact; a Wobst-scale mating network should break it. Built + calibrated the
adaptive connubium (Cut-2: each unpaired seeker expands a ring search to `m*` eligible non-kin males, patriclan exogamy),
gave it its own settlement founding (`_found_settlements_by_occupancy`; the gathering path is bypassed), and ran the
2×2 (Cut-1/Cut-2 × OFF/ON) plus an m* sweep. `run_campaign.py C_CONNUBIUM=cut2 C_MSTAR`.

**Lit re-check (supervisor: "is 475 relevant, or band-of-25 specific?") — the anchor was WRONG.** Wobst 1974's Minimum
Equilibrium Size = "persons in the intervening distance between two marriage partners" = a spatial mate-search REACH; his
runs gave **MES 79–332** (the cited **175–475 is an EXTRAPOLATION** to 1–2 hex tiers), and it DEPENDS on density/
arrangement (shrinks as residential units aggregate). The spatial-independent demographic floor is White 2017's **MVP
~150** (40–150 by marriage rule; our monogamy+exogamy config → ~140–150). The 500 is Birdsell's separate, contested
"dialectal tribe." So the connubium target is the **~150 floor with reach EMERGENT**, not a fixed 475. Our probe
calibration (m*=50 → reach ~475) had anchored to the contested max-dispersal number. LITERATURE.md corrected.

**The 2×2 + m* sweep (coastal-temperate, 15k steps, seed 0):**

| arm | peak pop | end pop | top-share | eff-dyn | childless | RS-gini | stratification |
|---|---|---|---|---|---|---|---|
| Cut-1 OFF (R-66) | 7,914 | **6,403 glide** | **0.89** | 1.3 | 37% | 0.66 | 7% |
| Cut-1 ON (R-66) | — | 7,206 glide | 0.45 | 3.3 | 37% | — | 14% |
| Cut-2 OFF m*=50 (reach ~475) | 10,379 | 1,812 BUST | 0.31 | 5.0 | 28% | 0.61 | →0 |
| Cut-2 ON m*=50 | 10,869 | 1,661 BUST | 0.25 | 5.6 | 28% | 0.61 | →0 |
| Cut-2 OFF m*=25 (reach ~285) | 11,210 | 2,565 ↑recovering | 0.21 | 5.4 | 26% | 0.59 | →0 (10 vil back) |
| Cut-2 OFF m*=15 (reach ~167) | **13,932** | 1,840 BUST | 0.215 | **8.7** | **23%** | **0.575** | →0 |

**Finding 1 — Cut-2 robustly BREAKS the drift-fixation (the hypothesis holds).** Every Cut-2 arm collapses the
winner-take-all: top-share 0.89 → 0.21–0.31, eff-lineages 1.3 → 5–9, and the birth-lineage drift is far slower
(eff 239→79→30→8 vs Cut-1's 78→10→3.6→1.7). The exogamous outward search mixes patrilines regardless of reach. **R-66's
single-dynasty outcome WAS a mating-structure artifact** — confirmed.

**Finding 2 — but Cut-2 boom-busts at EVERY reach; the driver is reproductive-skew flattening, NOT reach width (my "wide
net → scatter" hypothesis is REFUTED).** All three m* overshoot to 10–14k then crash to ~1,800; a reach of 167 (≈ Cut-1's
own 146–181, which glided) busts as hard as 475. Mechanism: Cut-2 cuts childlessness 37% → 23–28% (fraction reproducing
63% → ~75%), removing the reproductive-skew BRAKE that gave Cut-1 its smooth glide → Malthusian overshoot → starvation
bust → de-sedentization (villages → 0) → low mobile-forager attractor. COUNTERINTUITIVELY, NARROWER search flattens skew
MORE (m*=15: childless 23%, RS-gini 0.575, peak 13,932) — a wide prowess-weighted search is more mate-SELECTIVE (top
males chosen across more rings) than a narrow grab, and Cut-1's site-POOLING concentrates most of all (all a site's
females choose from one pool → one male monopolizes). So re-anchoring to MVP (m*=15) made the overshoot WORSE. **The lit
correction is real but is a correctness fix, not the bust fix.**

**Finding 3 — defensibility washes out under Cut-2** (OFF ≈ ON: both ~1,700, eff ~5, strat ~0): the R-66 defensibility
pivot needs aggregation to bite, and the bust destroyed aggregation.

**Finding 4 — a cycling hint:** m*=25 is RECOVERING at the end (pop 1,676 → 2,565, villages 0 → 10) — the skew-flatten →
overshoot-bust is the demographic instability the Cut-1 substrate refused to show; it may be the seed of Turchin cycles.

**Verdict + fork.** The connubium is load-bearing for BOTH the dynastic outcome (fixation) AND population stability (via
skew). Cut-2's two effects must be DECOUPLED: keep the fixation-break, restore the brake — i.e. **preserve status-based
reproductive skew WITHIN the exogamous network** (stronger polygyny / global-status mate weighting; von Rueden "polygyny
is the main amplifier"). OPEN FORK (supervisor to steer): (a) build the skew-preservation fix and damp the bust, vs
(b) treat the overshoot-bust as a FEATURE — the Turchin-cycle seed — and chase it. Cut-2 remains default-OFF, NOT yet the
substrate. Branch `connubium-cut2`. `m*` anchor retired from 50→(pending); mechanism refinement required before adoption.

**[CYCLING TEST RESOLVED — Finding 4 is NEGATIVE, 2026-07-14]:** extended m*=25 to 45,000 steps (≈3,750 yr) × 2 seeds
(genealogy off; `C_GENEA=0`). Both seeds are CONCORDANT and show a SINGLE founder-overshoot transient (peak 9.8k–11.8k
@ ~year 170), then a flat noisy low plateau (~1,900–2,170, well below Cut-1's ~6,400 capacity) for the remaining ~43k
steps — **no repeating boom-busts, NOT secular cycling.** The 15k-step "recovery" tail was just the plateau settling.
Dynasties slowly RE-CONCENTRATE on the plateau (top-share drifts 0.02→0.3–0.4) but never fixate (eff ~3–5) and never
cycle. **Conclusion: the Cut-2 overshoot-bust is a one-time transient, not the Turchin engine — the substrate (Cut-1 OR
Cut-2) does NOT self-cycle. Secular cycles require the explicit elite/instability layer; no connubium tuning produces
them.** The connubium arc is CLOSED: its scientific yield = (i) R-66's winner-take-all fixation was a mating-structure
artifact; (ii) a realistic wide/exogamous connubium breaks it but flattens skew → destabilizes; (iii) the lit anchor was
475→corrected to MVP ~150; (iv) no self-cycling. Next levers are ELSEWHERE: the explicit Turchin elite layer (for
cycles) and the agriculture/claimable-cells expansion (for the agrarian stratification path).

---

## R-68 — The founder boom-bust is a STARTUP ARTIFACT specific to Cut-2; the validated Cut-1 substrate is a GENUINE attractor (recovers from a 50% kill); agents are never immobile (2026-07-14)

**Why.** Supervisor: "founder dynamics differing from post-crash is a problem — are they still mobile? do bands move?"
Reboot test (`probe_reboot.py`): grow to the plateau, measure per-step MOBILITY, then kill 50% of the population and
watch whether the sedentary regime re-forms (re-boom) or the flat plateau is the true attractor.

**Mobility — agents are NOT frozen.** Fraction of agents changing cell per step: **0.73 (founder growth), 0.60 (Cut-2
plateau), 0.29–0.31 (Cut-1, lower only because they are settled in villages).** Movement is never energy-gated
([phase1_model.py:1093/1051](sic_games/src/sic_games/phase1_model.py:1093)); it is *self-limiting* (a cell attracts only
if it beats your per-capita), so at low density there is no aggregation gradient — bands drift locally but don't
converge. The flat plateau is NOT immobility.

**Cut-2 (m*=25) — founder boom is a startup artifact.** Kill 1,641 → 820 ⇒ NO re-boom; pop re-glides to the same flat
~1,700, villages stay 0. The one-time boom to 11k required the PRISTINE landscape (untouched stock briefly supporting a
villaged overshoot past the sedentism tipping density); once worked, the sustainable *mobile* K is ~1,700 and the
population sits there regardless of headroom. → Cut-2's boom-bust is substantially an INITIALIZATION artifact; its true
attractor is the mobile low-K. Explains R-67's single boom.

**Cut-1 (VALIDATED substrate) CONTROL — genuine robust attractor.** Kill 7,124 → 3,562 ⇒ RAPID full recovery to ~7,250
within ~250 steps, **villages persist 42–62 throughout**. The sedentary high-K returns to equilibrium after a 50%
perturbation — the signature of a genuine attractor, not a privileged start. → **R-58…R-66 are NOT founder-artifacts;
the validated substrate is sound.**

**Root of the Cut-1/Cut-2 divergence = VILLAGE PERSISTENCE (refines R-67).** Cut-1's seasonal gathering actively
RE-CONVERGES bands onto sites each year → villages persist → high sedentary fertility → robust attractor + fast
recovery. Cut-2's per-seeker ring-search SCATTERS (virilocal brides travel to distant grooms) → villages can't hold →
collapse to the mobile floor after the founder transient. So Cut-2's destabilization is fundamentally the
**virilocal-scatter breaking village persistence**, NOT the connubium reach (reach 167 busts like 475; R-67). Any Cut-3
must keep marriage relocation LOCAL so villages persist.

**BUG exposed (latent, validated path):** the long Cut-1 run crashed at ~step 16,500 —
`_pair_from_pool` ([phase1_model.py:2108](sic_games/src/sic_games/phase1_model.py:2108)) weight overflow ("Total of
weights must be finite"): `(prowess+1e-6)**mate_choice_strength` → inf when prowess drifts large over a long run. The 15k
campaigns just missed it. Needs a fix that preserves bit-exactness for normal (non-overflowing) cases. Did NOT affect the
reboot conclusion (obtained by step 16,000).

**Hard-kill addendum (2026-07-14):** Cut-1 at 75% kill (6,834 → 1,703) recovers to ~8,000 within ~1,000 steps, villages
40→24 (robust). BUT the *random* kill only THINS villages below the size threshold momentarily — survivors stay
concentrated in the old village cells and regrow bands back over threshold, so villages "re-thicken from thinned," they do
NOT nucleate from a DISPERSED village-less state. Aggregation-only village formation is weak precisely at
dispersed-nucleation (the Cut-2 crash state). Ethnography consult (Bandy 2004; Chagnon 1975; Yanomamö fission ~200;
Alberti N≈127–158) → the correct recovery/settlement-spread mechanism is village FISSION/BUDDING driven by leadership
competition (a village past a scalar-stress threshold sheds a rival-led segment onto a nearby storable site), NOT
individual scalar-stress repulsion. That is the recovery fix to build (independent of agriculture), and it doubles as the
"re-settle" step the agro depletion oscillator needs.

---

## R-69 — Village BUDDING (Bandy 2004): leadership-cleavage fission → daughter village is the settlement-SPREAD/recovery mechanism; revealed the baseline capacity was a spread-BOTTLENECK artifact; circumscription self-limits it + forks to hierarchy; +3.2× perf fix (2026-07-15)

**Why.** R-68: aggregation-only village formation can't NUCLEATE villages from a dispersed state — the recovery weak
spot. Ethnography consult (Bandy 2004 filed; Chagnon 1975; Yanomamö fission ~200; Alberti N≈127–158) → the correct
settlement-spread/recovery mechanism is village FISSION/BUDDING driven by internal leadership competition, NOT
aggregation. Built `_maintain_village_budding` (default-OFF, `enable_village_budding`): a VILLAGE (multi-band cluster
within settle_radius of a settlement) past a scalar-stress threshold sheds its RIVAL faction (2nd-largest lineage bloc,
Chagnon cleavage), which RELOCATES to a nearby open storable site and founds a DAUGHTER village. Operates on the
settlement so the band~25 scale is untouched. 6 tests; default-off bit-exact.

**Finding 1 — budding works + revealed a BASELINE ARTIFACT.** Paired run (Cut-1 + budding vs the R-66 Cut-1 baseline,
bit-identical until the first bud): budding **propagates settlements 49 → 532** and caps village size (~150–256), while
the baseline was STUCK at ~49 settlements forever (the aggregation-only spread bottleneck). So **the baseline's ~6,400
"carrying capacity" was an ARTIFACT** — remove the spread bottleneck and pop climbs to ~29,000 (0.18 people/km², a
realistic mid-forager/proto-ag density; the baseline's 0.04/km² was too LOW). Budding CORRECTED an under-population
artifact. But with ~62% of land buddable (cultivability), it spread unchecked → 29k / 530 settlements → impractically
slow.

**Finding 2 — (b) CIRCUMSCRIPTION self-limits it + forks to hierarchy (Bandy p.330, anchored).** "As the landscape fills
in, the costs of fissioning and relocation rise… an initially high rate of fissioning followed by a cessation of
fissioning and the appearance of higher-level integrative practices." Threshold: **~170 (Early Chiripa, open) → ~277
(Middle, circumscribed) = +60%.** Wired: `eff_thr = base·(1 + circ_gain·d_nearest_open/R)`, `base`=170,
`circ_gain`=0.6 (170→272 ≈ 277); budding targets the NEAREST open site (relocation cost); where none is in reach the
village grows + STRATIFIES (Carneiro fork, via the existing morph). **Result:** pop SELF-LIMITS to ~6,800 (was 29k),
~53 settlements (was 530), stratification 7–17% — budding while land is open, stratification once circumscribed. The
ethnographically-complete Bandy mechanism.

**Finding 3 — PERF (the "run 20–30K" ask).** Profiling the full step (4k agents) showed **56% of runtime in `_torus_cheby`
(63.5M calls)** — two O(agents·n_settlements) loops (`_nearest_settlement` scans every settlement per agent;
`_maintain_settlements` same) that exploded with hundreds of settlements. Fixed bit-exact with cell-neighbourhood
lookups (a per-step cell→nearest-settlement map, O(n_sites·rad²); occupancy-sum counting): **106.5s → 33.4s at 4k
(3.2×)**, scaling with settlement COUNT correctly (so the budding regime benefits most). Suite bit-exact.

**Status.** Branch `village-budding` (off connubium-cut2). Village budding + circumscription + perf all committed,
default-OFF. Anchored to Bandy 2004 (filed). NEXT: validate the (b) equilibrium at scale (is ~53 settlements / stratified
fraction stable + realistic?); tie budding's daughter-founding into the agro depletion oscillator's re-settle step;
consider SoA/numba for 50–100K if ever needed (the remaining time is now honest per-agent movement/status work).

---

## R-70 — Improved-land defensibility opens the AGRARIAN stratification path (Fertile-Crescent/Nile), distinct from the aquatic NW-Coast one, in rain-fed worlds (2026-07-15)

**Why.** Defensibility was aquatic/fisherman-only (claimable ⟺ aquatic_food ≥ D_min); farmland could never be defended.
Built `enable_improved_land` (default-OFF): cultivable land is ALSO claimable where WORKED (inside a settlement's
catchment) — "you own what you've cleared" (Testart delayed-return; Bandy landscape capital). 4 tests, 714 pass,
bit-exact. In riverine worlds (coastal/flat-temperate) the effect is MODEST (cells_owned 41→46) — settlements already
sit on aquatic-defensible cells, so aquatic SUBSUMES it (realistic: the river valley is the defended resource). The
DISTINCT agrarian path needs a rain-fed world.

**Rain-fed test (supervisor: run it on the right world).** World survey → flat-tropical is rain-fed: **aquatic 0.6%,
cultivable 38%** (highest-NPP world in the model; R-65 found it stays EGALITARIAN — rich forest isn't
storable/defensible). Ran improved OFF vs ON (Cut-1 + defensibility + budding, 1200 steps):

| flat-tropical | cells_owned | instability | stratification |
|---|---|---|---|
| improved OFF (aquatic-only) | **0** | 0 | 3.1–4.6% (egalitarian — = R-65) |
| improved ON (farmland defensible) | **5–10** | active (1–10) | **16.2% → 11.5%** (stratified) |

**Result.** Without improved-land the richest world stays egalitarian (nothing defensible → no territoriality → no
hierarchy). WITH it, **worked farmland becomes the defended resource → agrarian territoriality → stratification jumps to
11–16%**. So improved-land is exactly the mechanism that lets rich CULTIVABLE land drive complexity — the
Fertile-Crescent/Nile agrarian route — and it is DISTINCT from the aquatic (NW-Coast) route only where no river subsumes
it (rain-fed). **Both resource routes to Testart delayed-return complexity (dense-predictable AQUATIC + WORKED AGRARIAN
land) are now emergent + lit-anchored.** Improved-land also lifted the flat-tropical population (10k→16k) — defended
farmland tethers/concentrates, raising the realized capacity. Branch `agriculture`.

**NEXT (the payoff):** village-coupled SOIL DEPLETION — farm → deplete → abandon → **budding re-settles** on fresh land
→ fallow recovers — now has every piece (defensible farmland R-70 + a working re-settle mechanism R-69). This is the
candidate for the depletion-driven secular cycles the connubium (R-67) could not produce.

---

## R-71 — Emergent abandonment closes the swidden loop: collapse → SUSTAINABLE rotation (1.71×), but still NO cycles; and swidden churn is ANTI-hierarchical → completes the two-regime picture (2026-07-15)

**Setup.** Rain-fed flat-tropical (aquatic 0.6%), full agrarian stack (Cut-1 + defensibility + budding + improved-land +
soil depletion + alluvial renewal), 6000 steps, seed 0. Paired arms differing ONLY in `enable_emergent_abandonment` ⇒
bit-identical until the pin first releases. `run_campaign C_SOIL=1 C_ABANDON=0|1`.

**The ratchet (abandonment OFF) — the loop does not close.** pop 2,428 → peak **20,244 @1,600** → **monotonic slide to
8,563**, zero swings; villages 154→27; stratification 16%→0.7%. Diagnostic: `n_settle` sat **frozen at 12–16 while the
population halved** — settlements NEVER abandon. Depletion crashes the yield but nothing converts that into leaving, so
people farm floor-soil forever, the land never fallows, and the landscape ratchets down. **Real forest-fallow swidden
survives its 1:10 crop:fallow ratio ONLY because people move on** — the same (correct, lit-anchored) parameters produce
a death spiral without that step.

**Emergent abandonment (ON) — collapse becomes a sustainable rotation.**

| | abandonment ON | ratchet (OFF) |
|---|---|---|
| peak | 19,896 @2,500 | 20,244 @1,600 |
| endpoint | **equilibrium ≈14,421** (13,838–15,132, ±4.5%) | **8,563** (monotone, no recovery) |
| settlements | **25–26, churning** | 12–16, frozen |
| largest village | ~50 | large |

**⇒ 1.71× the ratchet endpoint.** The mechanism reads exactly as designed: many small villages, constantly abandoning
exhausted ground and re-founding on healed land, at a density the landscape can rotate (Boserup forest-fallow carrying
capacity). **The collapse is cured.**

**But NO CYCLES (±4.5% = noise).** Rotating swidden is *stable* — the ethnographically correct answer (it persisted for
millennia). **Third independent negative for secular cycles**: the connubium (R-67), the bare substrate (R-68), and now
soil depletion all find EQUILIBRIA. **Secular cycles are NOT in the subsistence base** — they need exogenous shocks
(`enable_tier2_shock`, deliberately OFF to isolate endogeneity; its own docstring notes shock deficit → dissolve →
dispersal) or the explicit Turchin elite layer.

**Unexpected second finding — swidden churn is ANTI-HIERARCHICAL, completing R-70's two regimes.** Stratification
collapsed to **0.4%** here, versus **11–16%** in the SAME world with improved-land but WITHOUT soil depletion (R-70):
constant relocation prevents surplus accumulation, so no hierarchy forms. With alluvial renewal keeping floodplain soil
≈1 (no hardship ⇒ never abandons), the model now yields BOTH regimes from terrain alone:
- **rain-fed swidden** → mobile, rotating, sustainable, **EGALITARIAN**
- **alluvial floodplain** → renewed, sedentary, **STRATIFIED** (the hydraulic state)
Which is the ethnography: shifting cultivators ARE egalitarian; Fertile-Crescent/Nile hierarchy required SEDENTARY
(flood-renewed/irrigated) agriculture.

**Design note (supervisor's framing, and the shortcut in it).** Abandonment did NOT need a new "leave" drive — the IFD
drive already wants better per-capita; it was merely OVERRIDDEN by the residence pin. So the pin was made
condition-dependent on the site's own remembered fortunes (a per-SITE generational hardship EMA, 12 yr — the place
persists while members churn; slow ⇒ intrinsic hysteresis, only CHRONIC decline registers = "the elders notice"), and
the existing drive decides. **This dissolves the information problem: agents never need to know whether elsewhere is
better** — release the pin and the local comparison settles it. Anchor: swidden villages relocate every ~5–30 yr
(Conklin; Yanomamö ~5–10) = WITHIN one generation. Lit re-check also CONFIRMED the existing params (Boserup
forest-fallow: crop 1–2 yr / fallow 20–25 yr ⇒ `soil_deplete_frac` 0.6/yr ≈1.6 crop-yr is RIGHT; the 10:1 ratio IS the
system); `soil_regrow_per_yr` 0.06→0.045 (~22 yr) to sit in the band. Branch `agriculture`; all default-OFF; 723 pass.

---

## R-72 — Emergent band size never worked: a SPATIAL variance fed to a TEMPORAL law, and both hardcoded 25s still alive. Rebuilt on measured cross-cultural data — mechanism now causal, but the environmental gradient stays weak (2026-07-16)

**Origin:** branch `band-size-cv`. MODEL_SPEC §4.8; Resource_Return_Rate_Table §4; PARAMETERS §21.1.

**Context.** `enable_emergent_band_size` was never validated — PARAMETERS §21.1 headed the section with a literal
`R-…` placeholder and no test referenced the flag. Auditing it before enabling it (the biome-comparison work needs
Marlowe's 25–50 environment-dependence) showed it could not work, for three stacked reasons.

**1. A category error in the REUSE (not the extraction).** `FORAGE_KCAL_STD`/`GAME_KCAL_STD` are **spatial**
cross-cell spreads feeding the lognormal cell-value draw (Resource table §1.5); §1.6's sourcing rule is correct
*for that*. `_return_cv_field()` fed them to a risk-pooling law that needs **temporal** day-to-day variance.
Sharing cannot smooth a spread across habitat patches. Which side of the `[15,45]` clamp a biome landed on was
decided purely by which *kind* of statistic its source reported — forest 0.73 = spread across 7 species' means;
desert 0.29 = across 3 hunt types; wetland 2.35 = a skew across ~286 habitat samples; savanna 2.24 = the lone
genuine temporal one (§3.2 already flagged it "for supervisor review"); grass/mountain = 10%-DEFAULT, no data.
**A measurement artifact wearing an environmental signal's clothes** — and backwards: it made forest, the
meat-heaviest biome, the lowest-variance/smallest-band one.

**2. Both hardcoded 25s were alive.** The blueprint said remove `band_base_tolerable` AND `repulsion_midpoint`;
v1/v2 removed neither. `repulsion_midpoint=25` is ON in `emergent_village_demog()` (`repulsion_gain=0.3`) and is
the term that actually sets band size. **R-64's "band ≈ 24" came out at 24 because it was put in at 25** —
RESULTS:922's "band ≈ 24 ← risk-pooling … (not hardcoded)" was FALSE and is corrected there.

**3. g\* was a permission ceiling, not a force.** Measured: hilly/temperate → g\* constant 15 across all 32 bands
(provably inert); coastal/tropical → 59% interior via biome-mixing but **corr(g\*, band size) = −0.22**. A ceiling
cannot pull a band together, so better CV data alone would have changed nothing.

**THE REBUILD.** (a) A **new temporal CV layer** (`terrain.HUNT_CV`/`GATHER_CV`/`RETURN_CV`), separate from the
spatial stds, which stay untouched. (b) **Linear** `g*=CV/cv_safe`, no clamps — the square is a stopping rule with
no cost side (unbounded ⇒ clamps ⇒ saturation); linear falls out of benefit-vs-cost (pooled variance σ²/n vs
crowding ∝ n ⇒ n\* ∝ CV). (c) **`repulsion_midpoint` per-band = g\*(CV)** — the CV finally reaches the cost term
that sets size. Deletes `band_size_min`, `cv_min`, and both 25s from the ON path.

**THE ANCHORS — measured, not assumed** (Resource table §4; data archived at `literature/cchunts/`):
- **`HUNT_CV = 2.11`** — median of 10 societies / ~15,600 trips from `cchunts` (McElreath/Koster; Koster et al.
  2020 Sci. Adv.), directly-observed single-day individually-attributed adult-male trips. Aché n=14,071 → **1.97**
  (51.6% of hunting days return nothing); Martu n=612 → 2.92.
- **`GATHER_CV = 0.70`** — Berbesque & Marlowe 2009 Tab. 4, Hadza tuber 257.7±182.1 over N=56 bouts. Bird 2009
  Tab. 1: every Martu plant food has **success rate 1.00**. *All gathering variance is HOW MUCH; all hunting
  variance is WHETHER AT ALL.*
- **NEGATIVE — hunting CV is BIOME-INVARIANT.** Forest alone spans 1.53–4.64; Martu desert (2.92) sits inside it;
  two Baka samples (same people, same biome) give 1.91 vs 3.94. It tracks prey choice/technology, not environment.
  **This falsifies deriving prey size per biome** and forces the gradient onto the diet mix (Cordain MEAT_FRAC) —
  which is the only reason the design works at all.

**RESULT — what IS demonstrated:**
- **Saturation gone.** g\* 100% interior on both probe worlds (was 0% and 59%).
- **CAUSAL** (the clean test — same world, same seed, sweep `cv_safe`): med band **33→29→24→22** as g\* falls
  **43→33→24→17**. The CV now moves realized band size; v1/v2 could not.
- **Mean lands on the ethnography.** At calibrated `cv_safe=0.037`: med band 29 / mean 29.4 = Hill 2011's 25–30.
  `cv_safe` is fitted ONLY to the mean; the **CV spread 0.70→1.41 = 2.0× is a free prediction vs Marlowe's 2×**.

**RESULT — what is NOT: the environment-dependence FAILS. A clean, well-powered negative.**
The blueprint's actual success criterion ("band size varies with environment, Marlowe 25–50") is **NOT met**, and
three successive explanations for the weakness were each falsified by measurement:

| test | paired corr(g\*, ON−OFF delta) | verdict |
|---|---|---|
| Biome battery, **1 seed**/world, n=18 | +0.335 (t=1.42) | n.s. |
| Same at **anchored `repulsion_gain=1.0`** | +0.374 (t=1.61) | n.s. — *"cost side too weak" REFUTED* |
| Biome battery, **4 seeds**/world, n=20 | **+0.165 (t=0.71)** | **n.s. — "underpowered" REFUTED; the gradient VANISHES** |

- *"The cost term is swamped by assabiyah."* **Refuted:** anchoring `repulsion_gain` 0.3→1.0 (Alberti's logistic
  IS a probability; see PARAMETERS §21.1) moved it +0.335→+0.374. Still n.s.
- *"The fission threshold never binds."* **Refuted:** 9/27 bands sit at or above their g\* base, 6/27 at the hard
  cap, 1/27 at the merge floor. It binds.
- *"The battery is underpowered."* **Refuted, decisively:** seeding 4×/world *lowers* the paired r to **+0.165**.
  The 1-seed +0.374 was noise — and so was the "productivity confound": the OFF reference falls from +0.382 to
  **−0.001** once seeds are averaged. Low-g\* worlds gained MORE than high (+2.42 vs +1.79); ON spread 1.66× vs
  OFF 1.60×.

**Why it fails — structural, not a bug.** The per-biome CV range is only **1.66×** (0.85→1.41), because Cordain's
meat fraction spans just 0.34–0.66 ⇒ g\* 23→38. Band size is *also* set by productivity, assabiyah, terrain and
mating, which swamp a 1.6× signal. **Risk-pooling predicts a 2× gradient; inside a full model with competing
drivers it is undetectable.** (Marlowe's real 25–50 likely spans a wider meat range than our six biomes: an
arctic/tundra diet at m≈0.9 would give CV 1.80 ⇒ g\*≈49 — the top of his range. Our worlds have no such biome.)

**Verdict — what R-72 DID buy.** (1) The category error is fixed and the CV is now a measured temporal statistic.
(2) The law is unclamped and the saturation is gone (g\* 100% interior, was 0–59%). (3) The mechanism is **causal**
(cv_safe sweep: med band 33→22 as g\* 43→17). (4) The mean is emergent-from-measured-data and lands on Hill 2011's
25–30, with ON consistently ~+2 above OFF. **What it did NOT buy: the environmental gradient.** Keep default-OFF —
it replaces a hardcoded 25 with a measured mean but adds no environment-dependence to justify the complexity.
**NEXT (if resumed): widen the biome CV range — a tundra/arctic biome (m≈0.9) is the missing high end and the only
way the predicted 2× has room to show.** `band-size-cv`; 736 pass.

---

## R-73 — `game_meat_cv` was anchored to a SPATIAL spread (forest 2.7× low, desert 10× low) since the Carbon build — but re-anchoring changes nothing, because the Cred effect is CV-INSENSITIVE. R-18's "sweet spot" falsified; its primary finding strengthened (2026-07-16)

**Origin:** `run_3b_carbon_statval.py` re-anchor sweep, branch `band-size-cv`. MODEL_SPEC §4.5.6; Resource table §4.

**The defect (found by the supervisor asking "didn't we already do this? did you check the model spec?").** G.3's
stochastic meat draw (`phase1_model.py:1340`) is **temporal** — a fresh mean-preserving lognormal per cell, per
step. Its documented anchor was `terrain.GAME_KCAL_STD/mean`: **spatial** cross-cell spreads (forest 0.73 = the
spread across 7 species' *means*; desert 0.29 = across 3 hunt types). Against the measured day-to-day CVs
(cchunts, R-72): **forest 0.73 vs 1.97 → 2.7× low; desert 0.29 vs 2.92 → 10× low.** Savanna's 2.24 was the lone
temporal number but describes *small* game (≈1% of Hadza animal tissue by mass; big game is 5.29). So one
number was doing double duty as spatial AND temporal variance — and `game_meat_cv=0.73` is hardcoded into
R-18/19/20, the society benchmark and the paternal calibration.

**RESULT — the blast radius is ZERO.** Re-anchored sweep, κ∈{0,1,2} × CV∈{0, 0.73, 1.97, 2.24, 2.92, 5.29},
N=20 seeds, paired drift-control. At κ=2:

| meat CV | Δmean_cred | cred-death-deficit | eq_pop |
|---|---|---|---|
| 0.00 (control) | +0.035 (t=1.8) | +0.099 (t=8.9) | 553 |
| 0.73 (old "forest") | +0.082 (t=6.2) | +0.132 (t=9.7) | 556 |
| **1.97 (TRUE forest, Aché)** | **+0.077 (t=5.7)** | **+0.120 (t=9.6)** | 567 |
| 2.24 (old "savanna") | +0.093 (t=6.2) | +0.125 (t=8.8) | 576 |
| 2.92 (TRUE desert, Martu) | +0.073 (t=4.4) | +0.111 (t=9.0) | 575 |
| 5.29 (Hadza big game) | +0.062 (t=3.3) | +0.118 (t=9.9) | 566 |

1. **The Cred effect is CV-INSENSITIVE.** From 0.73 to 5.29 it is flat (deficit +0.111…+0.132; Δmean_cred
   +0.062…+0.093, all within ~1.5 SE), and significant throughout. **At forest's true 1.97 the result is
   statistically indistinguishable from the 0.73 it was actually run at ⇒ R-19, R-20, the society benchmark and
   the paternal calibration need NO re-run.** The mis-anchoring was real but consequence-free.
2. **R-18's PRIMARY finding is reproduced and strengthened.** The CV=0 control still does not vanish (κ=2:
   deficit +0.099, t=8.9). The operative channel is **spatial competition near K**, not temporal meat variance —
   and no re-anchoring can touch a CV=0 control. *This is also WHY (1) holds: an effect that survives at CV=0 was
   never going to care what CV is.*
3. **R-18's SECONDARY claim is FALSIFIED** (corrected in place at R-18): "the effect **peaks at moderate
   forest-CV (0.73)** and is lower at CV=2.24 (savanna meat too bursty to leverage) — forest-like variance is the
   sweet spot." **There is no sweet spot.** 2.24 (+0.125) is not below 0.73 (+0.132); the effect persists at 5.29.
   *That G.3 only modulates stands; that it has an optimum does not.*

**CAVEAT — this is NOT a reproduction of R-18.** The model has changed materially since 2026-06-21 (prowess-credit
fix, `prowess_decay=0.05`, et al.), so the 0.73 arm here (+0.082/+0.132) differs modestly from R-18's reported
(+0.093/+0.118). **The across-CV comparison within this run is clean** (one model, one seed set, paired); the
comparison to R-18's absolute numbers is not.

**Fix shipped:** `terrain.MEAT_CV` (forest 1.97 / desert 2.92 / savanna-big-game 5.29, measured) is now the single
home and the documented anchor for `game_meat_cv`; `GAME_KCAL_STD` is explicitly marked spatial-only in
demography.py + MODEL_SPEC §4.5.6. Harness CVs left at 0.73 with the mis-anchoring documented, since (1) shows
re-running them would be compute spent to reproduce the same numbers.

---

## R-74 — Infanticide is the WRONG mechanism: Aché child killing is orphan-conditioned, and it's a hazard multiplier. Built + anchored — and it exposes a demographic validation FAILURE: the model makes 3.4× too many orphans (2026-07-17)

**Origin:** Hill & Hurtado 1996 (*Aché Life History*) Tables 5.1 + 13.1, extracted by image render (the tables have
no usable text layer). MODEL_SPEC §4.6.4; PARAMETERS. Branch `orphan-mortality`.

**The scoping was wrong, and the data says so.** `enable_infanticide` was scoped (Siler blueprint §4.1) as
birth-spacing/sex-biased infanticide, never built. Table 5.1 ("Causes of Death during the Forest Period", ages
0–3, n=131) says otherwise:

| category | n | % |
|---|---|---|
| all illness | 36 | 27.5 |
| congenital/degenerative | 19 | 14.5 |
| accident | 3 | 2.3 |
| **homicide/neglect** | **52** | **39.7** |
| warfare | 21 | 16.0 |

- **Parental infanticide is only 7/131 = 5.3%** (father 3 + mother 4). The 39.7% is dominated by **child
  homicide (24)**, **sacrificed-with-adult (11)** and **left-behind (5)** — killing orphans and burying children
  with dead adults, NOT birth spacing. (Arithmetic reproduces the book's prose exactly: homicide/neglect is
  26/63 female = 41.3% and 26/68 male = 38.2% ↔ its "41% / 38%".)
- **The blueprint's "optional sex-biased variant" is misplaced for infancy** — infancy is near-symmetric
  (38% M / 41% F). The bias is at 4–14 (28% F vs 6% M) and comes from grave accompaniment (80% of children
  buried with a deceased adult are female).
- **39.7% is a FLOOR:** Hill & Hurtado warn "some of the children reported to have died of defects at birth were
  actually killed and are coded incorrectly."

**The mechanism is a hazard MULTIPLIER, fully anchored** (Table 13.1, "Kin Effects on Child Mortality Rates
during the Forest Period: Age 0–9"; controls age, age², sex, mother's age, mother's age²):

| variable | parameter | rate ratio | prose |
|---|---|---|---|
| mother alive | −1.6277 (p<.001) | mother dead **×5.09** | "about fivefold" |
| father alive | −1.1146 (p<.001) | father dead **×3.05** | "about threefold" |
| parents divorced | +1.0892 (p<.001) | **×2.97** | "threefold increase" |
| *all other kin* | ~0 | — | brothers/sisters/grandparents/aunts/uncles ALL n.s. (p .156–.990) |

"Parents, but **not** other kin, have a strong and unique influence." Effects are age-proportional (no
significant age interaction). Plus: mother's death in year 1 ⇒ **100% mortality**.

**Built:** `enable_orphan_mortality` (default-OFF, bit-exact) + a `hazard_mult` on `monthly_death_prob` that
scales the TOTAL age-specific hazard (Table 13.1 controls age, so its effect is not a1-specific), threaded
through `hazard()` only — `cumulative_hazard`/`survivorship` stay unmodulated per blueprint hazard I-2. Reads
the existing `_mother`/`_father`/`_partner` links. 11 tests.

**THE FINDING — Table 13.1's mean values are an independent confirmation of R-16's fertility-pinning.**
Its *mean values* are a demographic target this project never had: **mother alive 0.98, father alive 0.95** (2% of
Aché child-EXPOSURE is motherless, 5% fatherless). The model measures **~10%** motherless. That is **not a bug**:

- **The chain, each step measured.** dens_delta ∈ {0,1,3} makes **no difference** (motherless 10.0/10.1/9.8%) —
  density-disease REFUTED as the cause. At dens_delta=0 (pure de-warfared Siler) the schedule's own analytic
  prediction is **4.01%**, but the model gives **10.0%** — the model kills mothers 2.5× faster than its own
  configured schedule. Cause: **49.2% of all deaths are STARVATION**, a channel outside the Siler, which roughly
  doubles total mortality.
- **And that is R-16, already documented:** "the regulated e₀ is **fertility-pinned, not mortality-pinned** …
  at r=0 the equilibrium life table is determined by the FERTILITY schedule (IBI/TFR), not by the
  natural-mortality coefficients … **Stationary (at K): e₀ ~28**." The analytic closes it: at a2_mult≈3 (≈e₀ 28)
  the schedule predicts **10.73%** motherless — the model measures **10.0%**. ✓
- **So the Aché/model gap is forced, not broken.** The Aché had TFR≈8 **and** e₀≈36.5 ⇒ NRR>1 — a **GROWING**
  population. A model pinned at r=0 must run e₀≈28 and therefore must orphan more children. *(An earlier draft
  of this entry called it a validation failure. Retracted: it is R-16's known consequence, now independently
  confirmed from a completely different measurement — child orphanhood rather than a life table.)*
- The Aché 2% is also **exposure**, depleted by the very mortality it measures (motherless infants die ⇒ leave
  the risk set). Their own schedule predicts 6.2% pre-selection ⇒ selection depletes ~3.1×. Self-consistent.

**⇒ THE DESIGN CONSEQUENCE: normalise ENDOGENOUSLY, not by the Aché constant.** A fixed divisor fitted to a
*growing* population cannot work in a *fertility-pinned* one. Measured:

| normaliser | eq_pop ON vs OFF | motherless (OFF→ON) |
|---|---|---|
| fixed Aché (1.499) | **−47%** | 9.8% → 8.2% |
| **endogenous (`_orphan_e_mult_live`, measured E[mult] ≈ 3.28)** | **−2.4%** | 9.8% → **7.4%** |

Dividing by the population's own E[mult] makes the channel **exactly compositional: WHO dies is orphan-graded,
HOW MANY stays fertility-pinned** — the same split R-16/R-18 established for the Cred hierarchy. The live
E[mult]≈3.28 vs the Aché 1.499 also *quantifies* the pinning: this population carries **2.2× the Aché orphan
burden**, as e₀ 28 vs 36.5 predicts.

**Also found — a trap:** `_father` is assigned inside the `use_cred_status` gate (`phase1_model.py:1938`), so
the paternity link — and any father-conditioned mechanism — **silently no-ops unless `enable_cred_status` is on**.
The first probe (paternity off) showed fatherless = 0.0% and eq_pop *rising* 25%.

**Verdict.** Built, anchored, default-OFF, compositional (eq_pop −2.4%). 13 tests; 749 pass. Ready to enable
where the orphan channel is wanted; it redistributes mortality onto orphans without touching eq_pop.
**NEXT (unused, anchored, free):** Table 13.1's companion result — 63% of forest children had ≥1 secondary
father, survivorship PEAKS at one primary + one secondary father, and 3+ fathers fare WORSE (paternity
confidence diluted ⇒ investment withdrawn). That plugs straight into the existing paternity stack.

---

## R-75 — A standing demographic dashboard, per village. Found three calibration flags on its first run — including a `divorce_rate` that means two different things (2026-07-17)

**Origin:** `TerrainWorld.demography(by=None|'band'|'village')` + `tests/test_demography_diagnostics.py` +
`outputs/phase1_biome_mortality/report_demography.py`. Branch `orphan-mortality`.

**Why.** R-74 burned a session chasing a "3.4× orphan excess" that turned out to be R-16's fertility-pinning
working correctly — **four hypotheses died** before the answer arrived (cost side too weak; threshold never binds;
study underpowered; density-disease). All of it would have been visible at a glance with the orphan-exposure
markers sitting next to e₀ on a per-village read-out. The model had exactly ONE diagnostic method (`bands()`).
So: measure every marker continuously, per settlement, and let drift announce itself.

**Built.** `demography()` returns population/sex/age-class/dependency/pairing/polygyny/orphan-exposure markers;
`by='band'` or `by='village'` partitions the live population (verified exactly — no agent lost or double-counted),
with the mobile hinterland kept visible under key `None` (R-69: the shock hits the hinterland while the storing
village rides through, so a village-only view hides half the story). `nan` where a denominator is empty — never a
fake 0. Agents of unknown parentage (founders) are excluded from the 0–9 orphan risk set, or the marker would
dilute toward 0 early in a run and hide exactly the drift it exists to catch. 9 tests (7 unit on synthetic
populations + 2 integration driving a real village world, ~8 s).

**RESULT — three flags on the first run** (400 steps, coastal-temperate, full village stack, n=1014, 11
settlements / 6 large, hinterland 264):

| marker | model | anchor | |
|---|---|---|---|
| sex ratio M:F | 1.18 | ~1.05 (SRB 0.512) | ok |
| **frac polygynous ♂** | **0.564** | Hadza ~4% (Marlowe); Aché monogamy-dominant | **14× high** |
| **dependency ratio** | **1.65** | forager ~0.8 | **2× high** — but this population is GROWING (500→1014 in 33 yr); a growing population *is* young (median age 11.6, frac<15 0.58). Re-check at K before calling it a defect. |
| **frac parents divorced** | **0.014** | Aché 0.14 (Tab. 13.1) | **10× LOW → a real bug (below)** |
| frac motherless | 0.045 | Aché 0.02; model must EXCEED (R-74/R-16) | ok |

**THE BUG — `divorce_rate` means two different things.** Documented as "per-step bond dissolution prob", it is
per-step in `_do_pairing` (called every step) but sits INSIDE the seasonal gate in `_do_gathering`/`_do_connubium`
(`if step_count % aggregation_period != 0: return`), so under `enable_marriage_aggregation` — i.e. the canonical
village stack (R-64) — it fires only on gathering steps: **~12× rarer than configured**. A per-step 0.004 should
dissolve ~35% of bonds over a 9-yr child window; measured exposure is 1.4%. This is not cosmetic: Table 13.1 gives
divorce a **×2.97** child-mortality multiplier — the same order as losing a father (×3.05) — and R-74's orphan
channel reads this state, so an under-firing divorce knob silently mutes a third of that mechanism. Flagged, not
fixed (it would move validated results): `task_9804e99a`.

**Verdict.** Pure measurement, mutates nothing, one pass. The dashboard paid for itself on run one. **Use
`report_demography.py` before believing any demographic claim, and after any change that could move the
substrate.** 758 pass.

---

## R-76/R-77 — R-19/R-20's status→RS was an ARTIFACT of 6× too much polygyny. Polygyny had no outflow, so its knob never worked; the missing wife-quality channel closes only a third of the gap (2026-07-17)

**Origin:** the R-75 dashboard flagged polygyny at 56% of married men against a forager anchor. Branch
`polygyny-stock`. Marlowe, *The Hadza*; von Rueden & Jaeggi, "Men's status and reproductive success in 33
nonindustrial societies" (PNAS).

**R-76 — the knob never worked, because polygyny had no exit.** `polygyny_rate` gates only whether a married
male is CONSIDERED; he then wins prowess-weighted, and a polygynous bond never ends. Polygyny was a **stock
that only fills**:

| `polygyny_rate` | realized polygyny (% of MEN) |
|---|---|
| 0.002 | 9.2% |
| 0.30 (canonical) | 25.3% |
| **Marlowe (Hadza)** | **~4%** |

**A 150× rate change moved the level 2.8×**, and Marlowe's 4% was unreachable (0% at rate=0, then straight to
9.2% at 0.002). **ANCHOR — Marlowe:** *"there are usually only about **4% of men with 2 wives**"* (denominator:
of MEN) and the missing outflow, from the same page: *"When a man does have 2 wives, the women usually live in
different camps, and **polygynous marriages are less enduring**."* Adding `polygyny_attrition` (per-step, fires
EVERY step — it must not inherit `divorce_rate`'s seasonal-gate bug, R-75) gives an inflow/attrition
equilibrium the rate controls: **0.0005→0.02 now spans 0.9%→11.5%**, and Marlowe's ~4–5% lands at
`rate≈0.005, attrition=0.02`. Attrition's floor is monogamy — it erodes the polygyny, never the marriage.

**R-77 — and that exposes the artifact.** With polygyny calibrated to Marlowe:

| configuration | polygyny (% men) | status→RS |
|---|---|---|
| old canonical | **25.3%** (6× Marlowe) | **+0.170** |
| Marlowe-calibrated, no wife quality | 5.3% | **+0.019** |
| **Marlowe-calibrated + wife quality** | 4–5% | **+0.070** |
| von Rueden target | — | **0.19** |

**R-19/R-20's status→RS ≈0.13–0.17 was bought with 6× the ethnographic polygyny rate.** The model reaches von
Rueden's r only above ~10% polygyny. Cause is structural: **polygyny was the model's ONLY status→RS channel**,
so it had to be cranked past the ethnography to hit the target — the same shape as R-64's "band ≈ 24" (came out
at 24 because 25 went in) and R-18's "sweet spot" (which vanished on re-measurement).

**The missing channel, named by the anchor.** von Rueden & Jaeggi (288 associations, 46 studies, 33 societies):
overall status→RS **r=0.19**; status associates with **wife quality ONLY in MONOGAMOUS societies (r=0.15)** and
with offspring mortality only in polygynous ones (r=−0.08); *"reproductive strategies that enhance fertility
more than offspring well-being"*; and **no significant difference by subsistence type** (foraging included — the
egalitarianism hypothesis is rejected). Their definition: wife quality = *"wife's age or interbirth interval,
wife's productivity"*. The model had **no** such route — females chose prowess-weighted, but a high-prowess man
was as likely to pair with a 40-year-old as a 16-year-old. `wife_quality_strength` supplies it: females pair in
order of remaining fertility^strength (Efraimidis–Spirakis weighted sampling — Plackett–Luce, not a
deterministic youth sort), so the most fertile pair FIRST and, choosing prowess-weighted, take the
highest-status men. The assortment **emerges from mutual choice** rather than being imposed as a correlation.

**RESULT — it works, and it is NOT enough.** Wife-youth assortment rises ~0 → **+0.06–0.08** (vs von Rueden's
**0.15**) and status→RS **+0.02 → +0.07** (vs **0.19**) — **about a third of the gap**. It **saturates
immediately** (strength 1→8 changes nothing): the ordering only decides who pairs *first*, and the band-limited
male pool caps how much better than average the first chooser can do. **Do not over-claim it.**

**Verdict.** Both mechanisms default-OFF/bit-exact; 767 pass. The honest position: **at a forager-realistic
polygyny rate the model does NOT reproduce von Rueden's r — it reaches ~0.07, not 0.19.** **NEXT:** von Rueden's
remaining channels — **mating success** ("age at marriage or probability of marriage") and **fertility**
(status→shorter IBI) — hold the other half of the gap. Until they exist, R-19/R-20's status→RS should be read
as *polygyny-inflated and not validated at a realistic marriage system*.

---

## R-78 — `divorce_rate` meant two things; fixed to per-step everywhere, calibrated to the Aché 0.14, and turned on — which completes R-74's dead divorce arm (2026-07-17)

**Origin:** the R-75 dashboard (`frac_parents_divorced` 0.014 vs the Aché 0.14). Branch `divorce-semantics`.
MODEL_SPEC; PARAMETERS.

**The bug.** `divorce_rate` is documented "per-step bond dissolution prob". It WAS per-step in `_do_pairing`
(runs every step) but sat AFTER the seasonal gate in `_do_gathering`/`_do_connubium`
(`step % aggregation_period != 0: return`, period=12), so under `enable_marriage_aggregation` — the canonical
village stack — it fired only on gathering steps: **~12× rarer than documented**, and rarer still on seasonal
worlds where the `season ≥ 0.8` window trims it further. The same knob meant two different things.

**Fix.** The draw moved to a single `_do_divorce`, called once per step in the main loop, independent of
pairing path. The three in-pairing copies were removed. Bit-exact for every current config (default and
canonical were both 0.0; no test set it >0). Verified on the gathering path: `divorce_rate=0.004` now gives
0.111 exposure, up from 0.014 — the ~8× the seasonal gate had been eating.

**Calibration.** Hill & Hurtado Table 13.1 gives ~0.14 of child (0–9) risk-intervals as parents-divorced
PREVALENCE (both parents living) — a stock, so the flow `divorce_rate` is calibrated, not read off. Swept
against `report_demography.py`: **`divorce_rate=0.005` reproduces `frac_parents_divorced` ≈ 0.14 on BOTH pairing
paths** (base/per-step 0.140, village/seasonal 0.149 — re-pairing latency barely shifts the stock). Adopted
CANONICAL.

**It completes R-74.** The orphan channel (canonical) carries a **×2.97 divorced-child multiplier** — the same
order as losing a father (×3.05) — but at `divorce_rate=0` it never fired. Turning divorce on (paired, village
stack, 4 seeds): divorced exposure 0.000→0.149, **orphan-flagged deaths 80→126**, motherless 0.045→0.058, eq_pop
848→924 (fertility-pinned, holds). A third of R-74's mechanism was dead until now.

**Verdict.** Semantics fixed, Aché-anchored, canonical-on; completes R-74; 6 new tests; 767 pass. It is the
prerequisite the von-Rueden-`r` work needed: status→RS will now be measured on a marriage system where divorce
sits at its real level, not 12× too low. *(Side note: the R-75 dashboard paid off a second time — it found this
bug, and now the same dashboard confirms the fix.)*

---

## R-79 — Desert game return was an extraction error: the doc swapped hill kangaroo in for bustard, dropping the Martu's 2nd-most-frequent hunt. Corrected 730 → 995 (+36%) (2026-07-17)

**Origin:** verifying the flagged Bird 2009 sample-size swap (task_52ad3af5) by re-reading Table 1 from the page
image. Resource_Return_Rate_Table §3.2; PARAMETERS §game.

**The error.** `GAME_KCAL_TARGETS[DESERT] = 730` (supervisor-approved 2026-06-15) was derived from Bird 2009
(Martu) Table 1's Return-Rate/Bout column as "sand monitor 641 (n=612), perentie 765 (n=78), bustard ~1,300
(n=91)". Against the actual table: **perentie is 697 (not 765)**, and the third species — labelled "bustard
~1,300 (n=91)" — is in fact **hill kangaroo** (1,203, n=91); the real **bustard is 1,761, n=289**, and it was
"excluded" under the mislabel "kangaroo (n=289)". So the derivation silently **dropped the Martu's 2nd-most-
frequent hunt (bustard, n=289)** and computed 570,262/781 = 730 from {sand monitor, perentie, kangaroo}. It was
right for a species set nobody intended.

**The fix (supervisor-chosen basis B — all four main hunts).** Bout-weighted mean of {sand monitor 641 (612),
perentie 697 (78), bustard 1,761 (289), hill kangaroo 1,203 (91)} = 1,065,060/1,070 = **995** (std 490, CV 0.49);
feral cat (n=25) excluded as opportunistic. **730 → 995, +36%.**

**Blast radius — contained by the R-72/R-73 separation.** `GAME_KCAL_STD` is the SPATIAL cell-value spread
(§1.5); it does NOT feed the temporal band-size CV (`RETURN_CV`, from Cordain meat_frac — R-72) or the G.3 meat
draw (`terrain.MEAT_CV`, from cchunts — R-73). So the correction moves only the desert **game cell-value
distribution**, not any status/band/meat mechanism. `RETURN_CV[DESERT]` = 1.025, unchanged. No test asserted the
old value; desert-world runs shift (richer desert game), the coastal-temperate validation substrate does not. 773
pass.

**Method note.** This is the 4th value this session that was wrong because it was hard-read off a table image
(after the Hawkes/Berbesque/cchunts CV extractions): the Bird 2009 table has no text layer, and the original
lift transposed two rows. Re-rendering the page and re-reading it caught it — the same tool (`pymupdf` render)
that the R-72 CV work leaned on.

---

## R-80 — von Rueden's DOMINANT channel (status→fertility) is structurally unavailable to a fertility-pinned model. status→RS caps at ~0.07 at realistic polygyny; 0.19 is polygyny-inflated (2026-07-17)

**Origin:** building von Rueden's remaining status→RS channels after R-77 showed the 0.19 was 6× polygyny.
Branch `vonrueden-fertility`. von Rueden & Jaeggi, "Men's status and RS in 33 nonindustrial societies" (PNAS).

**The goal.** R-77 built wife quality (r=0.15 in monogamous societies) and it closed only ~⅓ of the gap
(status→RS +0.02→+0.07). von Rueden's other decomposed channels: **fertility** (total offspring born — the
DOMINANT one; "status enhances fertility MORE than offspring well-being") and **mating success** (age at
marriage). Built the fertility channel: a husband directs his harvest OVERFLOW to his wife's reproductive
reserve → higher `energetic_fertility_factor` → shorter IBI → more births; status-graded emergently
(high-prowess ⇒ bigger meat share ⇒ bigger overflow).

**RESULT — it is STRUCTURALLY INERT. Built, measured, REVERTED.** The transfer fired ZERO times. Direct
instrumentation at a crowded equilibrium:

| | value |
|---|---|
| married men with any overflow (wealth > cap) | **0%** |
| married women with reserve need (wealth < full) | **100%** (mean need = a full reserve) |

**The two preconditions are anti-correlated by construction.** A husband has overflow only when food is
plentiful — but then his co-resident wife is *also* full (need ≈ 0); under scarcity the wife has need but the
husband has 0 overflow. Overflow and need never co-occur ⇒ no transfer ⇒ `corr(husband status, wife fertility)`
≈ 0 across all fracs, and a frac=0.9 run is bit-identical to off. Sweeps (+0.03→+0.08) were noise; the higher
values at n=900 (+0.10–0.14) were the **polygyny artifact** (crowding pushed polygyny to 12–16%, R-77), not the
fertility channel.

**Root cause — R-16 fertility-pinning.** At r=0 there is no surplus above subsistence, so a status→fertility
channel (which needs surplus to convert into *more births*) cannot operate. **The model can only access
fixed-pie channels** — mating monopoly (polygyny) and who-pairs-with-whom (wife quality) — **not pie-growing
ones** (status→fertility). von Rueden's *dominant* real-world pathway is therefore foreclosed in this model.

**SYNTHESIS — the von-Rueden-r arc, closed honestly.**
- At forager-realistic polygyny (~4%, Marlowe), the model's status→RS is **~0.07** (wife quality ~⅓; fertility
  channel dead; mating-success/age-at-marriage unbuilt but a fixed-pie channel unlikely to close a 0.12 gap).
- The model reaches von Rueden's 0.19 only above ~10% polygyny (R-77) — **~3× the ethnographic rate**.
- **CONCLUSION: von Rueden's 0.19 is a cross-cultural average, inflated by the polygynous societies in his
  33-society sample. A monogamy-dominant forager system has LOWER status→RS (~0.07–0.10 here), because its two
  strongest real-world channels are unavailable to the model — polygyny (calibrated down to the ethnographic 4%)
  and fertility (foreclosed by fertility-pinning).** R-19/R-21's 0.19 was the polygyny lottery; it is not
  reproducible through legitimate monogamous-society channels, and should be read as polygyny-inflated.

**Code:** the fertility mechanism is REVERTED (provably inert — dead weight); a `[NOT BUILT]` note in
`demography.py` records why, so it isn't re-attempted without first solving the overflow/need anti-correlation
(would require intra-household inequality — husband eats first — which the model's co-resident sharing precludes).
770 pass.

---

## R-81 — The cred homeostat was silently leaking: a contraction validated pre-selection, defeated by R-19's mate-choice. Fixed by renormalising to mean-1 (2026-07-17)

**Origin:** the cred-dynamics diagnostic (built while designing the elite layer). Branch `cred-renorm`.

**The defect.** cred inheritance reverts toward a FIXED 1.0 anchor: `child.cred = (1−ρ)·base·noise + ρ·1.0`.
The code comment calls it "a TRUE contraction that bounds the no-decay lineage facet (red-team BLOCKER fix)" —
and it was, **in R-18, before mate-choice existed**. R-19/R-20 then added (a) fertility-weighted paternity
(high-cred father more ⇒ the next generation over-samples high status) and (b) a `base = cred·prowess` product
(mean > 1 when the facets correlate). **Both inject an upward bias each generation that defeats the fixed-1.0
contraction.** Measured on the canonical village stack: mean cred **1 → 18.6 over 2000 steps** (max 242), so the
`ρ·1.0` pull becomes negligible next to `(1−ρ)·base` and **the homeostat progressively loses grip** — nobody
re-checked it after adding selection.

**Why it matters (and why it didn't visibly break anything yet).** Cred enters every downstream weight
RELATIVELY — `(cred)^κ / Σ(cred)^κ` for the food contest, normalised `(cred·prowess)^m` mate weights — so the
absolute drift is cosmetic for the dynamics (the Gini still plateaued ~0.5). But a homeostat that leaks at scale
**cannot be made state-dependent** — which is exactly what the elite layer's Stage D (a conditional homeostat
for secular cycles) requires. A leaking homeostat is not a floor you can build two capitals on.

**The fix — `enable_cred_renorm` (R-81).** Renormalise cred to population-mean 1 each step. This restores the
anchor's meaning (1.0 = the running mean again ⇒ constant homeostat grip ρ at any scale), and it sidesteps the
"revert-to-co-moving-mean" unbounded-drift the red-team originally blocked (that had no fixed scale; a hard
per-step rescale pins the scale). **Re-verified SAFE** (4 seeds × 800 steps, canonical): mean **1.75 → 1.00**
(pinned), **Gini 0.332 → 0.326**, **status→RS +0.248 → +0.261**, eq_pop 728 → 702 — all within noise, **R-19
preserved**. Adopted CANONICAL. 777 pass.

**Note.** This reinforces R-77/R-80: part of the model's late-run status skew was the *inflating* cred mean
(the homeostat losing grip), not a real hierarchy — with the grip restored, the Gini is the same but honest.
The elite layer now builds on a homeostat that actually holds.

---

### R-82 - Material wealth stratifies where food cannot; the captor is a TYPE, not a rank (2026-07-17)
**Question.** Cred already skews the food draw, yet equilibrium inequality stays flat. Can a DURABLE stock do what
a burned one cannot? **Build.** `material` as a stock (hides from game; `material_hide_frac`), `material_decay`,
aggrandizer capture, Boehm leveling. **Result.** Durability alone stratifies - food is consumed, `material`
persists, so small per-step differences integrate. **Two corrections, both mine:** (i) keying capture on `cred^k`
gave corr -0.018 - Hayden's captor is an ambition TYPE (`aggrandizer_frac`), and re-keying gave +0.780;
(ii) [SUPERVISOR-CAUGHT] material was drawn from the GRANARY, i.e. from food. Reworked to come from GAME as hides.
Boehm leveling cuts the top decile 90% -> 28%. **Aggrandizer capture stayed inert at forager dispersal (1.14x even
at 80% capture) - it needs co-residence.** That negative is what R-83 explains.

### R-83 - Elite step 1: leader "managerial rights" over BAND corporate output -> 3.68x (2026-07-17)
**The missing rung** [SUPERVISOR]: `_cell_owner` is CORPORATE (band_id), but stratification needs PERSONS to
differ. The bridge is not ownership, it is AUTHORITY OVER corporate property - controlling the product of property
one does not own. **Anchor** [Hayden 1995 VERIFIED]: NW-Coast aggrandizers "control access to spatially restricted
resource locations or productive facilities" and that class "had MANAGERIAL RIGHTS over the resource locations and
facilities of the group"; contrast New Guinea, where "more ubiquitous access to productive land probably limited
the development of social stratification". **Result** (2 seeds x 600):

| share | leveling | material Gini | leader/other | top-10% |
|---|---|---|---|---|
| 0.00 | OFF | 0.416 | 1.18x | 25.3% |
| 0.20 | OFF | 0.487 | 2.11x | 34.1% |
| 0.50 | OFF | 0.636 | **3.68x** | 53.6% |
| 0.50 | ON | 0.281 | 2.21x | 24.2% |

**The R-82 negative was the WRONG UNIT, not the wrong mechanism** - a cell holds 1-2 agents, a band ~25, and you
cannot skim a group of one. Leveling does not abolish the leader's advantage, it CAPS it (3.68x -> 2.21x): the Big
Man as the ethnography has him - ahead, but held there.

### R-84 - Challenge-succession: DESERTION, not the duel, is how a leader goes (2026-07-18)
**Origin** [SUPERVISOR]: "I am not sure that chief is hereditary yet ... in tribes chief holds office until he dies
or challenged and defeated (vikings) ... perhaps council of elders (north american) ... need lit." **The lit
confirms the correction and then corrects the mechanism.**

**(a) NOT hereditary** [Boehm 1993 VERIFIED]: leaders are deposable (Iroquois sachems; Coeur d'Alene and Assiniboin
for "remarkable meanness, parsimony"); even a *hereditary* Yokuts chief "suspected of too much self-aggrandizement
was ... ignored in favor of another chief"; councils of ELDERS are the documented brake and are specifically North
American (Navajo, Fox, Yokuts) plus Tupinamba, Cuna, Mandari; Boehm even has "incipient chiefdoms ... egalitarian
despite hereditary leadership". **Every part of the supervisor's correction holds.**

**(b) But the challenge-and-defeat duel is the MINORITY channel.** Boehm Table I columns, counted over the
48-society survey: Public opinion 10 - Criticism 6 - Ridicule 5 - Disobedience 7 - **DEPOSITION 9** -
**DESERTION 17** - Exile 2 - Execution 10. Followers walking away outnumbers deposition ~2:1 ("if a bad chief was
not deposed he might be deserted gradually" - Iban; "an entire dissatisfied lineage might simply go away" -
Mandari). And the split is STRUCTURAL: deposition societies are the centralized ones (Iroquois, Yap, Somali, Iban,
Assiniboin, Coeur d'Alene, Yokuts), desertion societies the mobile/dispersed ones (Batek, Mendrig, Apache, Kutchin,
Ute, Nambicuara, Yanomamo, Patagonia) - i.e. Sahlins' Nootka-vs-Siuai and Hayden's restricted-vs-ubiquitous
resources, surfacing as a sanction frequency. The supervisor's biome hunch is right, with resource structure as the
real axis.

**(c) Two triggers** [Boehm's 47 coded motivations]: OVERREACH = "dominating others as leader" (14) + "lack of
generosity or monopolizing resources" (5) = 19; FAILURE TO DELIVER = "ineffectiveness, partiality, or
unresponsiveness in a leadership role" (10). **This closes a loop:** overreach is read off the leader's own
material relative to his band - which `leader_share_frac` is what inflates - so a greedier levy raises the sanction
hazard on the man taking it. Measured: 24 -> 82 -> 103 sanction attempts as the levy goes 0 -> 0.2 -> 0.5.

**(d) Succession on death, two regimes** [Sahlins 1972:209]: Nootka office "ascribed by right of chiefly due" =>
"centricity is built into the structure" and outlives him; the Siuai big-man's following "will as such dissolve
with the demise of the pivotal big-man". Coded as `succession_dissolve` - ON leaves 2/18 bands leaderless (and
levying nothing); OFF fills every office.

**THREE DEFECTS THE BUILD EXPOSED, each found by measurement not inspection:**
1. **Tenure was capped ~4 yr with sanctions OFF** - so it was not politics ending careers. The office was keyed to
   `band_id`, and band_ids churn on every fusion/fission. Re-keyed the tenure clock to the MAN.
2. **Collisions ended 106 of 135 tenures** (death only 29): when two bands fused, the surviving office-holder was
   picked by dict order. Now resolved by MERIT.
3. **Mean leader age 23.5 yr against an adult mean of 34.1 - leaders were YOUNGER than average**, inverting every
   source. Cause: `max(ms, ...)` ranged over ALL band members, so a high-cred CHILD (inherited cred, default
   prowess 1.0) could hold office. Gated on `menarche_months`. Leader age -> 34.0.

**Validated after the fixes** (2 seeds x 600): desertion 62-74% of attempts vs the 65% that went in [OK]; leader
age 34.0 vs adult 34.1 [OK]; father-was-a-leader 53-69% (centred ~60%) against **Hayden's 75% of New Guinea
Entrepreneur Big Men** - same order, somewhat low, and EMERGENT (the office is never inherited here; any continuity
comes from heritable cred, which is Hayden's own mechanism - he transmits moka partners and wives, not the
position).

**HONEST LIMIT:** band-level tenure settles at **4-6 yr**, bounded by band fusion rather than by the leader's life.
A 20-year chief is a CHIEFDOM phenomenon and would need the office attached to the SETTLEMENT, not the band -
which is exactly Hayden's precondition (spatially restricted resources) and the next rung.

### R-84b - `leader_share_frac` anchored on BHM 2009, and the levy turns out to be nearly powerless (2026-07-18)
**Verified negative first:** no chiefly-due PERCENTAGE exists in Sahlins 1972 or Ames 1994 - both read directly for
one. So the levy is anchored on its OUTCOME, as `leveling_strength` was on Boehm 38/48. **Anchor** [Borgerhoff
Mulder et al. 2009 Table 2]: their three wealth classes ARE the model's three facets (embodied=prowess,
relational=cred, material=material - confirmed by what their Table 1 measures), with forager alpha = (0.46, 0.39,
**0.15**) and an alpha-weighted Gini target of **0.25 +/- 0.04**; agricultural alpha = (0.27, 0.14, **0.59**),
Gini **0.48**.

| share | leveling | G_prowess | G_cred | G_material | **HG composite** | agri-weighted |
|---|---|---|---|---|---|---|
| 0.00 | ON | 0.241 | 0.281 | 0.181 | **0.248** | 0.211 |
| 0.20 | ON | 0.257 | 0.267 | 0.237 | **0.258** | 0.247 |
| 0.50 | ON | 0.243 | 0.275 | 0.281 | 0.261 | 0.270 |
| 0.50 | OFF | 0.250 | 0.251 | 0.563 | 0.298 | **0.435** |
| | | | | **BHM target** | **0.25** | **0.48** |

**`leader_share_frac = 0.20` -> composite 0.258 vs 0.25 +/- 0.04 = the anchored forager value.**

**THE REAL RESULT IS THE FLATNESS.** Across the whole levy range 0 -> 0.5 the forager composite moves only
0.248 -> 0.261, because material carries just **15%** of the forager weight. **A levy cannot by itself make a
forager society unequal** - the agricultural 0.48 is approached (0.435) only by removing leveling AND shifting the
weight to material. That is BHM's own thesis (inequality tracks WHICH wealth class matters and how heritable it
is, not how much any one man takes) and it is Testart's chain. **Standing caution for the elite layer: stratifying
on material alone over-weights the one class the ethnography says matters least at the forager stage.**

---

### R-85 - Charter retrofit: the flag audit finds a crash in its own author's code, refutes a charter claim, and exposes five dead knobs (2026-07-18)

**What was run.** The MECHANISM_CHARTER (adopted the same day) types every mechanism and gives each type an
invariant. `audit_flag_invariants.py` implements the black-box half: for each of the 60 `enable_*` flags, run an
ENRICHED baseline (prerequisite chains satisfied) and the same config with that one flag flipped, same seed, and
diff a signature (population trajectory, totals, band structure, bonds, positions, births/deaths). Every
no-change flag is then re-tested at a second seed and a longer horizon before being called a defect.

**Why the baseline had to be enriched:** the realistic preset has the entire elite layer OFF, so flipping
`enable_leveling` alone would do nothing for want of MATERIAL and read as vacuous. That is exactly the
prerequisite false-negative that made R-82's capture look inert. The audit encodes the prerequisite chains
explicitly and reports "prereq unmet" separately from "vacuous".

**FINDING 1 - a live crash in code committed hours earlier.** `enable_leader_office` with
`enable_band_affiliation=False` raised `AttributeError: 'TerrainWorld' object has no attribute '_next_band_id'`.
R-84 deliberately placed `_maintain_leader_office` OUTSIDE the affiliation guard so the office could stand alone,
but its desertion branch allocates a new band id from a counter initialised only INSIDE that guard. **All ten
R-84 tests set `enable_band_affiliation=True`, so none could see it.** Fixed by initialising `_next_band_id`
unconditionally (the affiliation seeding block re-zeroes it => bit-exact); regression test added.

**FINDING 2 - `enable_cred_renorm` is NOT gauge fixing; the charter's own worked example was wrong.** The
charter argued (same day) that renorm changes no observable because every downstream use of cred is relative.
Measured: it moves population, deaths, wealth, material and band structure. **Root cause:** the cred inheritance
homeostat reverts toward a **fixed 1.0 anchor**, so rescaling cred changes each agent's distance to that anchor
and hence its children's cred - not scale-invariant. Not a bug (restoring the anchor was R-81's whole purpose),
but not a gauge. Re-typed as a new category **R - Regulator**. The surviving rule is sharper: *a regulator is a
gauge only if nothing downstream reads an absolute scale, and that is an empirical question* - measure it, do
not assert it from the code.

**FINDING 3 - a new defect class: FLAG ON, MAGNITUDE ZERO.** Of 11 flags inert at both seeds with prerequisites
satisfied and a live reader present, **five are gated by a companion gain of exactly 0**:

| Flag | Dead knob |
|---|---|
| `enable_leader_coherence` | `leader_coherence_gain = 0.0` |
| `enable_malnutrition_fission` | `malnutrition_fission_gain = 0.0` |
| `enable_size_repulsion` | `repulsion_gain = 0.0` |
| `enable_terrain_pathogen` | `pathogen_gamma = 0.0` |
| `enable_village_scaling` | `village_gain = 0.0` |

They read as ON in any flag-level audit while contributing nothing. **This invalidates the 2026-07-15 config
audit's conclusion that "all built mechanisms + prerequisites are correctly ON"** - five of those were dead.
**New standing check: `flag is True` is not evidence a mechanism is live; inspect the magnitude too.**

**CONFIRMED INDEPENDENTLY:** `enable_infanticide` has no reader outside the config (the known stub, now
detected mechanically rather than by memory); `enable_genealogy_log` [O] mutates nothing - **the observer
invariant HOLDS**, which is the first positive confirmation that a charter type is real rather than imposed.

**METHODOLOGICAL LIMIT (recorded so it is not re-attempted).** A black-box differential audit **cannot** test
conservation invariants. Over a long coupled run, changing the band graph changes who forages together and hence
wealth - so an A-typed flag legitimately moves conserved quantities *in the trajectory* while its operator still
conserves them *within its own step*. Conservation needs instrumentation **around the call**. The black-box
audit soundly decides only vacuity, observer violations, crashes, and magnitude-zero gating.

**RESIDUAL - 6 flags inert at both seeds, live reader, non-zero magnitude, no explanation yet:**
`enable_bonded_mating`, `enable_condition`, `enable_energetic_fertility`, `enable_landscape_packing`,
`enable_site_appraisal`, `enable_terrain_move_cost`. These are the remaining charter §6 candidates and need
individual inspection - NOT yet claimed as defects.

**Regime-gated and correctly inert (not defects), each already documented:** settlement machinery inactive in
this world config (`enable_aggregation_sedentism`, `..._scalar_stress`, `enable_village_budding`,
`enable_catchment_ceiling`); `enable_economic_defensibility` + `enable_improved_land` (DE-10: the claim gate
never fires on unsaturated land); `enable_agriculture`/`enable_soil_depletion`/`enable_alluvial_renewal` (wrong
world, R-70/R-71); `enable_band_risk` (shelved, DE-4).

---

### R-85b - The six residual flags: the dead-knob class is bigger than it looked, and it hides one level deeper (2026-07-18)

**Closing R-85's residual.** Six flags were inert at both seeds despite a live reader and a non-zero magnitude at
the reader site. Each had a specific hypothesis tested empirically rather than by reading. **All six are now
explained, and none is a spec bug - but the dead-knob count rises from 5 to 7 (+1 chained).**

| Flag | Diagnosis | Class |
|---|---|---|
| `enable_terrain_move_cost` | `move_cost_kcal = 0.0` | **DEAD KNOB** (hidden inside the field builder) |
| `enable_site_appraisal` | `site_gain = 0.0` | **DEAD KNOB** (hidden inside the field builder) |
| `enable_condition` | its EMA's only live consumer is the pathogen term, and `pathogen_gamma = 0.0` | **DEAD DOWNSTREAM** (chained) |
| `enable_bonded_mating` | gated `if bonded and not pair_bonds`; the preset sets pair-bonds ON | **SUPERSEDED BY DESIGN** (F.3a replaced F.1) |
| `enable_energetic_fertility` | factor = 1.0 for **99.75%** of birth-eligible draws; the rest span 0.9954-1.0 | **REGIME-GATED** (no food stress at this density) |
| `enable_landscape_packing` | both density definitions give the SAME society target in **8 of 8** bands | **REGIME-GATED** (below threshold resolution) |

**METHODOLOGICAL FINDING - the magnitude can be one level deeper than the flag.** R-85's gate scan looked for a
companion parameter NEAR THE READER LINE and found five zeros. It MISSED `move_cost_kcal` and `site_gain`
because those live inside the *field builders* (`_move_cost_field`, `_site_suitability_field`), not at the call
site. The give-away was measurable and general: **the terrain `cost` layer has real spread (std 0.188) while the
fields built from it have std EXACTLY 0.0** - a builder that multiplies a varying input by zero. **New check:
scan for zero magnitudes along the whole dependency chain, and flag any derived field whose std is 0 while its
input's is not.**

**A SUBSTANTIVE consequence, not just bookkeeping.** `enable_energetic_fertility` is ON in the preset and reads
as a live nutrition->fertility coupling, but on the population that actually uses it the factor is 1.0 in 99.75%
of draws and never falls below 0.9954. **So the model's fertility is effectively NOT nutrition-modulated at
current densities.** Any result that assumes energetic fertility is doing work needs re-reading in that light -
it will only bite under real food stress, which this regime does not produce.

**Two are correctly inert and should NOT be "fixed":** `enable_bonded_mating` is superseded by the pair-bond path
(F.3a) and is dead whenever `enable_pair_bonds` is on - that is the intended supersession, not a defect;
`enable_landscape_packing` is wired correctly and simply does not change the society target at ~0.011 agents/km2
(both definitions read `complex_forager`). It would separate at higher density, which is what R-61 built it for.

**The dead-knob list for decision (7 + 1 chained):**
`leader_coherence_gain`, `malnutrition_fission_gain`, `repulsion_gain`, `pathogen_gamma`, `village_gain`,
`move_cost_kcal`, `site_gain` - plus `enable_condition`, alive but feeding only the zero-gain pathogen term.
Each needs a per-knob judgement: is the zero DELIBERATE (mechanism built and parked) or an OVERSIGHT?

---

### R-85c - RETRACTION: the "dead knobs" were an artifact of my own audit harness (2026-07-18)

**Origin:** the supervisor asked whether a zeroed knob's job might already be done by ANOTHER mechanism. Checking
that meant looking outside the single preset the audit had been using - and the answer overturned R-85's and
R-85b's headline finding.

**WHAT WAS WRONG.** R-85 reported "five flags enabled in the preset but multiplied by a gain of exactly 0", and
R-85b added two more. **None of those seven flags is enabled in `realistic_forager_demog()`.** That preset
enables 17 flags and none of the seven is among them. The audit harness flipped each flag `False -> True` while
its companion gain stayed at the **zero DEFAULT**, so the mechanism stayed inert - and I read that inertness as a
property of the configuration rather than of my own test.

**They are also not dead anywhere.** All seven run at live values in `emergent_village_demog()` and the stage
harnesses: `leader_coherence_gain=2.0`, `repulsion_gain=0.3`, `village_gain=5.0`, `site_gain=0.3`,
`move_cost_kcal=750.0` (0.01·BURN, in the SAME FILE at line 113), `malnutrition_fission_gain=2.0`,
`pathogen_gamma` swept in `run_2m_multibiome.py`. They are **preset-scoped village/scarcity-arc mechanisms,
correctly absent from a forager preset** - not defects.

**PROOF.** Re-running the audit with a MAGNITUDE map (each flag turned on at the value the project actually uses)
makes **five of the seven active immediately**: `malnutrition_fission`, `size_repulsion`, `site_appraisal`,
`terrain_move_cost`, `terrain_pathogen`. The other two (`leader_coherence`, `village_scaling`) remain inert for
regime reasons - `village_scaling` needs villages, and the discrete settlement machinery is inactive in this
world config.

**RETRACTED:**
- "Five dead knobs" (R-85) and "seven dead knobs, magnitude hides one level deeper" (R-85b). **Withdrawn.**
- "This invalidates the 2026-07-15 config audit's claim that all built mechanisms are correctly ON."
  **That retraction was itself wrong and is withdrawn.** The 2026-07-15 audit was not shown to be in error.
- The per-knob supervisor decision this generated is **moot**; there is nothing to decide.

**WHAT SURVIVES, and why each is unaffected:**
| Finding | Status | Why it holds |
|---|---|---|
| `_next_band_id` crash under `enable_leader_office` + no band affiliation | **HOLDS** | a real AttributeError, reproduced and fixed, regression-tested |
| `enable_cred_renorm` is NOT gauge fixing | **HOLDS** | it IS enabled in the forager preset, so this was a genuine ON->OFF test |
| `enable_infanticide` is an unimplemented stub | **HOLDS** | established by reader search, independent of magnitudes |
| `enable_genealogy_log` [O] mutates nothing | **HOLDS** | observer invariance; a magnitude would not change it |
| `enable_bonded_mating` superseded by pair-bonds | **HOLDS** | enabled in the preset; a genuine ON->OFF test |
| Black-box audits cannot test conservation | **HOLDS** | methodological, independent of this error |
| `enable_energetic_fertility` factor ~1.0 in 99.75% of eligible draws | **HOLDS** | measured directly on the eligible population, not inferred from a flip |
| `enable_landscape_packing` gives the same society target in 8/8 bands | **HOLDS** | measured directly |

**THE REAL FINDING, correctly stated.** *A boolean flip is not enabling a mechanism.* Most flags are paired with
a gain that **defaults to zero**, so `enable_X=True` alone leaves X inert. That is a genuine trap - it caught me,
running a harness built specifically to catch this class of thing - but it is a trap for **whoever enables a
flag**, not evidence that any preset is misconfigured. The harness now carries a MAGNITUDE map and sets a live
gain whenever it turns a flag on, and its output records `baseline_on` so that only `True` rows are read as
genuine tests of a running mechanism.

**METHOD LESSON (the one that generalises).** The audit conflated "this flag does nothing when I turn it on" with
"this flag does nothing". The distinguishing question is **what was the baseline state**, and I did not record it
prominently enough to notice. A differential audit must report the baseline value beside every verdict.
Second-order: I grepped `enable_*=True` across a FILE that contains two presets and attributed the union to one
of them. **Scope a config audit to the function, not the file.**

---

### R-86 - The LEGITIMACY channel: the RATCHET is the mechanism, and it hits Hayden's 75% (2026-07-18)

**Origin:** DM-F1, the first item from the Flannery digest. Flannery ch.10 says our elite layer's premise cannot
produce hereditary rank - *"if feasting were all it took to produce hereditary inequality, there would have been
no achievement-based societies left for anthropologists to study"*; feasting *"produced individual Big Men who
had no way of bequeathing renown to their offspring."* R-83/R-84 measured exactly that. Friedman's endogenous
scenario supplies the missing mechanism as a **reinterpretation**, not an accumulation.

**BUILD** (charter-declared: **type C** Conversion, **unit LINEAGE**, **invariant DEBITED**, anchor Flannery
ch.10 `[VERIFIED]`): lineages spend material on sacrifices; legitimacy is an EMA of a lineage's SHARE of its
band's ritual expenditure (bounded [0,1] by construction, so the threshold is interpretable); crossing the
threshold converts into heritable `cred`.

**THREE CUTS, and the first two were wrong in instructive ways.**

**Cut 1 - the feast destroyed material.** Material Gini jumped 0.237 -> 0.416 from the debit alone, a pure drain
with nothing to do with legitimacy. Flannery is explicit that the sponsor *"could sponsor the most prestigious
sacrifices AND FEED THE MOST VISITORS"* - a feast is an EXCHANGE. Fixed: the spend is redistributed to the
band's guests, conserving material (now asserted as the X invariant in tests). **With the feast conserved,
material Gini goes DOWN, 0.237 -> ~0.10** - competitive feasting is a material LEVELLER, which is Boehm and
Sahlins and precisely why it yields Big Men rather than dynasties.

**Cut 2 - an unbounded multiplicative cred boost.** Measured cred Gini **0.968-0.988**: one lineage holding
essentially everything, the R-66 winner-take-all failure mode. A sustained multiplicative push beats the
homeostat's contraction - **the same lesson as R-81**. Fixed by relaxing toward a legitimacy-set target
(`LEGIT_RELAX`), which is bounded by construction.

**Cut 3 - THE RATCHET, which is the actual mechanism.** With a DECAYING legitimacy stock the result was a flat
negative: father-was-leader stayed at baseline (59-67% vs 65%) at every gain up to 20, and the agricultural
composite got WORSE. The diagnosis is conceptual and it was a misreading of the source. Friedman's key shift is
*"from 'They must have **PLEASED** the nats' to 'They must be **DESCENDED FROM** higher nats than we are.'"* A
stock that decays and must be re-earned by feasting **is still "pleased the nats"** - i.e. I had built the
achievement-based mechanism Flannery says does not produce heredity. Crossing the threshold must **ASCRIBE the
lineage permanently**: descent, once believed, is not contingent on this year's harvest.

**RESULT with the ratchet** (2 seeds x 600, `feast=0.25`, `legit_cred_gain=20`, `threshold=0.15`):

| | father-was-leader | agricultural composite |
|---|---|---|
| baseline (no legitimacy) | 65% | 0.247 |
| decaying stock (cut 2) | 59-67% | 0.147-0.200 |
| **RATCHET (cut 3)** | **76%** | 0.189 |
| **TARGET** | **75% (Hayden)** | **0.48 (BHM)** |

**T-6 IS MET: 76% vs Hayden's "about 75% of New Guinea Entrepreneur Big Men had fathers that were also Big
Men"** - and it is EMERGENT, since the office is never inherited in the model and the target was never fitted.

**T-5 IS NOT MET, and the reason is structural rather than a calibration shortfall.** The agricultural composite
is 59% MATERIAL-weighted, and this mechanism *equalises* material (the feast redistributes) while concentrating
CRED. It therefore moves the forager composite up and the agricultural composite down. **Legitimacy is not the
route to material stratification** - it is the route to heritable RANK. Those are different things, and BHM's
alpha weights make the difference measurable.

**THE OPEN PROBLEM, and it is not optional polish: SATURATION.** `ascribed_frac_pop` reaches **0.70-0.85** - over
600 steps most lineages eventually cross, so "descended from higher nats" stops being a distinction. A pure
ratchet with no reverse has no equilibrium. **This is exactly why the Kachin cycle requires the gumsa -> gumlao
COLLAPSE**: Flannery's *"hereditary inequality was repeatedly created, lasted for a few generations, and then
collapsed."* The two halves are structurally coupled - **delegitimation is not Stage 2 polish, it is required
for Stage 1 to remain meaningful**, and it is the same lagged resentment stock H-CYCLES predicts. Building it is
the next step.

**Also fixed in passing:** the ratchet was first recorded BELOW the `legit_cred_gain <= 0` guard, so the
`n_ascribed` diagnostic read 0 whenever the conversion gain was 0 - whether a lineage is believed to descend
from the nats is a fact about the society, not about how strongly we convert that belief. Regression-tested.

**Status:** default-OFF, bit-exact. 7 new tests including the X-conservation assertion on the feast and the
ratchet-does-not-leak assertion. The four rates remain `[DESIGN]`, calibrated against T-6.

---

### R-87 - Delegitimation (gumsa -> gumlao): regime SWITCHING appears, periodicity does not. H-CYCLES partly supported, prediction NOT met (2026-07-18)

**Origin:** R-86 derived the need for this. The ascription ratchet works (father-was-leader 76% vs Hayden's 75%)
but has no equilibrium - `ascribed_frac_pop` runs to 0.70-0.85 and nobility becomes universal. Leach's Kachin
cycle supplies the reverse, and it is a LAG: prestige-seeking *"only increased their followers' resentment and
hastened their overthrow"*, so hereditary inequality *"lasted for a few generations, and then collapsed."*

**BUILD** (charter-declared: type **C reverse**, unit **BAND** - Leach's gumlao premise 1 is "All lineages are
considered equal", a whole-community reversion - invariant: changes ascription and cred only). Resentment is a
slow EMA of the ascribed lineages' cred advantage over commoners; crossing the threshold de-ascribes every
lineage in the band and resets. Hysteresis comes from having to rebuild legitimacy from zero.

**THE EXPERIMENT WAS BROKEN ON THE FIRST PASS, and the failure is worth recording.** `resent_privilege_ref` was
left at 1.0 while ascription confers a cred advantage of ~`legit_cred_gain` = 10 - so privilege ran at **20x the
threshold** and even a nominal "40-year" EMA crossed in ~12 steps. All three arms of the lag sweep were
therefore effectively INSTANTANEOUS, and the sweep tested nothing. Symptom: `mean_gumsa` 0.03-0.11 with ~1500
reversions - hierarchy squashed the moment it formed, in every arm. **Third time this session that a sweep
varied a parameter that was not the operative one** (cf. R-85c). Fixed by normalising privilege so the EMA time
constant governs.

**CORRECTED RESULT** (1 seed x 3600 steps = 300 yr, privilege normalised, crossing times ~115 / ~58 / ~3 yr):

| lag memory | reversions | mean gumsa | sd gumsa | autocorr peak | verdict |
|---|---|---|---|---|---|
| 167 yr | 2576 | 0.258 | 0.353 | **0.19** | weak/none |
| 83 yr | 1609 | 0.476 | 0.428 | 0.13 | weak/none |
| 4 yr (control) | 2047 | 0.269 | 0.389 | **0.03** | weak/none |

**H-CYCLES: PREDICTION NOT MET. This is a FOURTH independent negative for secular cycles** (after connubium
R-67, substrate R-68, soil R-71). A delayed negative feedback, built explicitly to supply the missing complex
eigenvalue pair, does **not** produce periodic behaviour at any lag from 4 to 167 years.

**But it is NOT a null result, and two things distinguish it from the three prior negatives.**

1. **The lag pushes in the PREDICTED DIRECTION.** Autocorrelation peak rises monotonically with lag length:
   0.03 (4 yr control) -> 0.13 (83 yr) -> 0.19 (167 yr). The mechanism does what the theory says; it simply
   never reaches an amplitude that constitutes a cycle.
2. **Large-amplitude SYSTEM-WIDE regime switching now exists where nothing switched before.** `sd_gumsa` = 0.428
   against a mean of 0.476 - the society swings across nearly the full range from mostly-ranked to
   mostly-egalitarian. **Tested against the independent-bands null**: if ~N bands flipped independently,
   sd(frac_gumsa) = sqrt(p(1-p)/N) = 0.112 / 0.079 / 0.056 for N = 20 / 40 / 80. Measured 0.428 is **3.8-7.7x
   that null**, so bands are switching TOGETHER, not averaging out. The prior negatives had no switching at all.

**So the honest summary: the model now produces APERIODIC BISTABLE SWITCHING between ranked and egalitarian
regimes, not a limit cycle.** Leach's Kachin are described as cycling; this reproduces the *alternation* and the
*amplitude* but not the *regularity*. Whether real gumsa/gumlao alternation is genuinely periodic or merely
recurrent is itself worth checking before treating the missing periodicity as a model defect - "repeatedly
created, lasted for a few generations, then collapsed" describes recurrence, and does not by itself assert a
fixed period.

**THE SOURCE WAS RE-READ, AND I HAD MEASURED THE WRONG QUANTITY (R-87b, same day).** Flannery's Kachin are
*"created, overthrown, and **periodically reinstated**"*, *"this **repetitive cycle**"*, *"**oscillated
between**"* - and the duration claim is *"lasted for **a few generations**"*. **Periodicity in the strict
(fixed-interval) sense is nowhere asserted; RECURRENCE plus a characteristic SPELL DURATION is.** The
autocorrelation test above therefore measures a property the ethnography never claims. **The right metric is
DWELL TIME in gumsa**, and my H-CYCLES prediction over-specified the source.

**Dwell time, estimated from the aggregate counts** (dwell = band-steps in gumsa / exits; band count assumed
~25 agents/band, so this is an estimate, not a measurement):

| lag memory | ~bands | mean gumsa dwell |
|---|---|---|
| 167 yr | 128 | **3.9 yr** |
| 83 yr | 115 | **10.2 yr** |
| 4 yr | 121 | **4.8 yr** |

**Against the anchor of ~60-100 yr, dwell is one to two orders SHORT.** So there IS still a real gap - the model
alternates far too fast - but it is a different gap from the one the autocorrelation test reported, and it has a
different likely cause: the reversion trigger fires too easily, not that the feedback lacks a lag.

**Open leads, re-ordered after that correction:**
- **Measure dwell time directly** (per-band spell lengths, not inferred from aggregate counts) and calibrate
  `resent_threshold` against the ~60-100 yr anchor. This is now the primary metric for H-CYCLES, replacing the
  autocorrelation period.
- **The reversion trigger is a hard threshold on a noisy quantity**, so bands cross it stochastically rather
  than by clean build-up - the likely reason spells are short and irregular. A smooth hazard, or hysteresis on
  the reversion itself (a band that just reverted resisting immediate re-ranking), is the natural next cut.
- Coupling between bands is NOT the missing piece - the null test above shows they are already correlated.
- Note the non-monotonicity: the 83-yr lag gives the LONGEST dwell (10.2 yr), longer than the 167-yr lag
  (3.9 yr). That is not what a simple lag story predicts and should be explained before more tuning.

**Status:** default-OFF, bit-exact. 13 tests on the legitimacy/delegitimation pair, including that
delegitimation BOUNDS the ascribed fraction (R-86's open problem, closed), that resentment resets on reversion,
and that the ratchet stays monotone when the reverse is disabled. `resent_*` remain `[DESIGN]`.

---

### R-87d - H-CYCLES resolved NEGATIVE, on instruments that were fixed twice and validated against controls (2026-07-18)

**This supersedes the verdicts in R-87 and R-87c, both of which were instrument artifacts.** The supervisor
asked two questions that broke the analysis open: *"how good is the SNR of cycle diagnostics?"* and *"plot the
solution over the data and I will judge."* Neither verdict survived being looked at.

**THE THREE INSTRUMENT FAILURES, in order.**
1. **R-87 (autocorrelation, uncalibrated).** Reported "no cycles" against an INVENTED threshold of 0.2, with no
   positive control, no null floor, and no detrending on a series whose population grew 500 -> 3200.
2. **R-87c (autocorrelation, calibrated).** Measured the null (white-noise peak mean 0.088 / max 0.138) and
   found the 0.19 measurement ABOVE it - so the negative was withdrawn as underpowered. **Also wrong**: that
   null was computed at a different series length than some comparisons used, and length changes the floor
   substantially (n=900 -> 0.138 max; n=225 -> 0.197 p95).
3. **Sinusoid fit (new instrument, still mis-specified).** Built to report an amplitude and a curve that could
   be drawn on the data. It returned amplitude 0.260, "period" 250 yr, r2 0.301, clearing its null - **and it
   was fitting the grid ceiling.** A 250 yr period in a 300 yr window is 1.2 cycles: a trend wearing a
   sinusoid's clothes.

**WHAT THE RAW DATA ACTUALLY SHOWS (plotted for the supervisor, and decisive).** `frac_gumsa(t)` is not
oscillatory in any form. It is: a build-up to ~90% ranked over ~25 yr; a sustained ranked phase; a violent spiky
collapse around yr 75-125; then **~150 yr pinned at zero** (28% of samples exactly 0); then a terminal jump to
1.0. **One episode, then the mechanism dies.** No fit of any periodic model is appropriate, which is why two
different periodic instruments both produced confident wrong answers.

**TWO DETECTOR FIXES (supervisor-approved), then re-validated per charter D1:**
- **Reject any period beyond window/3.** A fit that cannot complete three cycles is describing a trend. Both
  instruments had happily returned ~250-270 yr from a 300 yr window.
- **Require a genuine LOCAL MAXIMUM in the autocorrelation**, not merely the largest value in a wandering tail.
  The unfixed code took `argmax` unconditionally, so pure drift always produced a "peak".

**POSITIVE CONTROL AFTER THE FIXES (D1) - the fixes tighten without blinding:** a real 75 yr cycle injected into
a 300 yr window is still recovered at 75.3 yr (autocorrelation) and 74.5 yr (fit) at every amplitude >= 0.10;
pure noise returns fit amplitude 0.029 against a null p95 of 0.034.

**FINAL RESULT on the real series, both instruments fixed and validated:**

| lag memory | n | AC period | AC peak | fit amp (null p95) | r2 | correlation time | verdict |
|---|---|---|---|---|---|---|---|
| 167 yr | 900 | 69.0 yr | **-0.021** | 0.174 (0.061) | 0.140 | 22.2 yr | NO CYCLE |
| 83 yr | 900 | 59.0 yr | **-0.028** | 0.130 (0.074) | 0.051 | 22.6 yr | NO CYCLE |
| 4 yr (control) | 900 | 59.3 yr | **-0.122** | 0.135 (0.067) | 0.079 | 20.7 yr | NO CYCLE |

(correlation time from a log-linear fit to the ACF decay, not the 1/e crossing — see the correction below)

The autocorrelation "peaks" are **NEGATIVE** - a turning point inside a negative region, which is definitively
not recurrence. The sinusoid explains 5-14% of variance.

**A DIAGNOSTIC RULE THIS PRODUCED:** `fit_amp` clears its null in BOTH arms (0.174 vs 0.061; 0.130 vs 0.074)
while explaining 14% and 5% of variance. **An amplitude-versus-null test alone would have declared a cycle in
both.** Goodness-of-fit is the discriminator, and a verdict rule must require BOTH: amplitude above the null AND
r2 above a floor. Added to the charter.

**H-CYCLES: RESOLVED NEGATIVE.** A delayed negative feedback, built explicitly to supply the missing complex
eigenvalue pair, does not produce cycles. This is the fourth independent negative (R-67, R-68, R-71, R-87d) and
the first one measured on validated instruments.

**AND THE THIRD ARM KILLS THE ONE POSITIVE I HAD CLAIMED.** An earlier draft claimed "correlation time rises
with the lag" from the first two arms; the control arm refutes it. Fifth time in one day a pattern read off a
partial sweep dissolved when the full sweep landed - **do not draw a trend from two points when a third is
still running.**

**CORRECTION (self-check, `verify_numbers.py`): the correlation-time FIGURES were estimator noise.** Reported as
15 / 33 / 32 yr from the ACF's **1/e crossing** - a SINGLE POINT on a noisy curve. An independent
**log-linear fit to the whole ACF decay** gives **22.2 / 22.6 / 20.7 yr**, i.e. essentially IDENTICAL across
lags of 167 / 83 / 4 yr. The two estimators disagree by 30-50%, so the crossing figures should not be quoted.
**Use ~22 yr, uniform.** This strengthens rather than weakens the conclusion: on the robust estimator every arm
has the same memory regardless of the lag, which refutes lag-governance more cleanly than the
non-monotonicity did.

**DWELL TIME, measured directly instead of estimated.** The earlier 3.9 / 10.2 / 4.8 yr were INFERRED from
aggregate reversion counts assuming ~25 agents/band. Measured as run-lengths of the thresholded series:
mean ranked spell **2.7 / 3.6 / 4.6 yr** over 32 / 41 / 14 spells. **But the distribution is heavily skewed -
maximum spells reach 17.7 / 81.0 / 58.7 yr.** Occasional spells DO land in the ethnographic 60-100 yr range;
they are rare among many short ones, and reporting only the mean hid that. Any future calibration against the
"few generations" anchor must use the spell-length DISTRIBUTION, not its mean.

**So the lag parameter is not governing the dynamics.** Combined with the dwell-time inversion (10.2 yr at the
83 yr lag vs 3.9 yr at 167 yr), two independent metrics agree the mechanism's timescale is set by something
OTHER than `resent_alpha` - most likely the band fission/fusion churn that R-84 already showed dominates
leader tenure (106 of 135 tenures ended by band collision, not politics). **That is the thing to identify
before any further cycle work**: a delayed feedback cannot govern a system whose own substrate turns over
faster than the delay.

**What does survive:** large-amplitude regime switching exists where the three prior negatives had none. The
mechanism does something real - it is neither periodic nor lag-governed.

**Reported quantity going forward is CORRELATION TIME (15-33 yr) and DWELL TIME, not period** - the ethnography
claims spell duration ("lasted for a few generations"), never a fixed period, and the model is 2-6x short of
that 60-100 yr anchor.

---

### R-86v - The 76% SURVIVES validation, but it measures CONCENTRATION, not TRANSMISSION (2026-07-20)

**Why this was run.** R-86's father-was-leader = 76% was the elite arc's one positive result, was written into
TARGETS T-6 as MET, and had never been held to the standard R-87d established. It is a **single summary
statistic over a possibly-skewed population** - exactly the shape that failed in R-87d, where a mean dwell of
2.7 yr described almost none of the actual spells.

**D1 POSITIVE CONTROL passes.** A synthetic population with known father-son transmission returns the lift it
was built with: 1.0 -> 1.02, 1.5 -> 1.52, 2.0 -> 2.01, 2.5 -> 2.51. The statistic can measure heredity.

**D2 NULL: the feared artifact is NOT present.** `father_was_leader` = P(father ever led | self ever led). If a
large share of the population ever led, leaders having leader fathers would be arithmetic. The measured base
rate P(father ever led) is **0.44**, not ~0.70, and the measured value sits far in the right tail of a 2000-shuffle
permutation null (**z = 3.1 to 4.9** at every age gate). **The 76% is a genuine signal.**

**BUT THE UNGATED LIFT WAS AGE-INFLATED.** The comparison pool averages **17.7 yr** while leaders average
**36.0 yr** - the pool is full of agents who have not yet had their chance to lead, which deflates the base rate
and inflates the ratio. Age-matching fixes it:

| arm | age gate | n | measured | base rate | **lift** | z |
|---|---|---|---|---|---|---|
| legitimacy ON | none | 52 | 0.757 | 0.439 | **1.72** | 4.87 |
| legitimacy ON | >= 25 yr | 43 | 0.769 | 0.536 | **1.43** | 3.36 |
| legitimacy ON | >= 35 yr | 30 | 0.767 | 0.537 | **1.43** | 3.06 |
| baseline OFF | none | 50 | 0.655 | 0.427 | 1.54 | 3.34 |
| baseline OFF | >= 25 yr | 38 | 0.627 | 0.439 | **1.43** | 2.63 |
| baseline OFF | >= 35 yr | 22 | 0.614 | 0.393 | 1.58 | 2.50 |

**THE FINDING THAT CHANGES THE INTERPRETATION: age-matched, the two arms have the SAME LIFT (1.43 vs 1.43).**
The legitimacy channel raises the raw fraction (0.769 vs 0.627) **by raising the base rate in step**
(0.536 vs 0.439). It concentrates leadership into fewer lineages, so fathers AND sons within those lineages both
lead more often - **but the father->son ASSOCIATION is not strengthened at all.**

**So the ratchet produces CONCENTRATION, not TRANSMISSION.** R-86 framed it as "achieved success becomes ascribed
rank"; the transmission ratio was already present in the baseline, supplied by `cred` inheritance. What
legitimacy adds is that more of a favoured lineage's members hold office. That is a real effect and it is what
moves the raw fraction toward Hayden's number, but it is not a new heredity channel.

**T-6 STATUS: MET on Hayden's own metric, with a caveat that cannot currently be removed.** Hayden reports
"about 75% of New Guinea Entrepreneur Big Men had fathers that were also Big Men" - a RAW FRACTION whose base
rate he does not give. Without it we cannot compute HIS lift, so the raw-fraction comparison (0.769 vs 0.75) is
the only like-for-like available, and **it cannot distinguish concentration from transmission**. If big-man
status in New Guinea was rare (say 10% of men), Hayden's 75% implies a lift near 7 and our 1.43 is nowhere near
it. **Finding Hayden's base rate is now the single highest-value literature question for this target.**

**Method notes for reuse:** the age gate matters and should be standard for any statistic conditioned on a
life-course event - an ungated pool mixes agents who have had their chance with those who have not. And report
the LIFT beside the raw fraction always; the fraction alone moved 0.655 -> 0.757 (looks like a large mechanism
effect) while the lift did not move at all.

---

### R-88 - BAND CHURN, not resent_alpha, sets the delegitimation timescale (2026-07-20)

**Origin.** R-87d found the delegitimation mechanism's correlation time (~20-22 yr) was IDENTICAL across three
resentment-memory settings spanning 4 to 167 years - the lag parameter measurably did not govern the dynamics.
R-84 had already found something structurally similar: 106 of 135 leader tenures ended by band COLLISION, not
by politics. This tests whether the same substrate churn is the common cause.

**MECHANISM, confirmed by reading the code (not inferred).** `_maintain_bands()` FISSION mints a fresh
`band_id` (`new_id = self._next_band_id; self._next_band_id += 1`) for roughly half a splitting band's members;
`self._band_resentment.get(new_id, 0.0)` then returns 0.0 - a SILENT reset, independent of `resent_alpha`,
regardless of what had accumulated. FUSION moves every agent onto the surviving `band_id` and simply abandons
the smaller band's resentment entry. Neither event passes through `_do_delegitimation()`, so neither is counted
in `reversions_this_step` - these are resets nobody was tracking.

**MEASURED** (`probe_band_churn.py`, 2 arms x 3600 steps, band lifetime = first-seen to last-seen span for
every band_id that ever existed):

| | 83 yr lag | 4 yr control |
|---|---|---|
| band lifetime, median | 10.2 yr | 10.2 yr |
| band lifetime, mean | 17.5 yr | 17.5 yr |
| bands created | 2,277 | 2,407 |

**Band lifetime is IDENTICAL across both arms** (median AND mean, to one decimal place) - confirming band churn
is exogenous to delegitimation, driven purely by `band_split_size`/`band_merge_size` and population dynamics,
not coupled to resentment at all.

**THE MATCH: mean band lifetime (17.5 yr) sits almost exactly on R-87d's measured correlation time (~20-22 yr),
uniform across resentment memories of 4, 83 AND 167 years.** For the long memories (83, 167 yr) band churn caps
the observed timescale far below the nominal setting; for the short control (4 yr, nominal memory ~4.2 yr),
band identity itself OUTLASTS the resentment memory, so the band substrate sets the pace either way. **Band
churn, not `resent_alpha`, is the governor** - a delayed social feedback cannot express a memory longer than the
unit carrying it survives.

**A SAMPLING-BIAS FINDING IN THE PROBE ITSELF, recorded so it is not mistaken for a second effect.** The same
probe's "age" statistic (age of a currently-live band, sampled at random timepoints) reported median 54 yr /
mean ~78 yr - roughly 5x the lifetime figures. This is NOT a second timescale; it is the inspection paradox
(the bus-waiting-time problem): sampling at random timepoints oversamples long-lived bands, the same way asking
riders at a stop "how long is your commute" oversamples people on the longest routes. **Lifetime (unbiased,
computed over the full population of band_ids that ever existed) is the correct statistic; age (sampled at
timepoints) is confounded and should not be quoted as a timescale.**

**PERFORMANCE, checked in passing (the supervisor asked).** Today's additions (R-86 legitimacy + R-87
delegitimation) cost ~9% extra per step at matched population (11.7 -> 12.7 ms/step, N~500, both pure Python
per-agent loops, unvectorized - consistent with the model's existing style, charter types A/N/C are the loop-
legitimate categories). The perceived slowness of the H-CYCLES/band-churn runs is population size, not these
mechanisms: those runs grew to 6,800-7,500 agents (15-20x the N=500 these were tuned at), and per-step cost
scales with population throughout the model, not specifically here. The band-churn probe's own instrumentation
(a full-population band_id scan every step) added further overhead on top, separate from the model's own cost.

**CONSEQUENCE for the elite/legitimacy arc.** A delayed social feedback (resentment, or any future slow social
mechanism) cannot express a memory longer than ~15-20 yr while attached to the BAND as its unit, because the
band itself does not survive longer than that on average. Two paths forward, not mutually exclusive:
(a) attach slow social state to something with a longer natural lifetime - the LINEAGE (already used for
ascription) or the SETTLEMENT rather than the band; (b) reduce band churn itself, e.g. widen
`band_split_size`/`band_merge_size` so bands persist longer - but this changes the substrate's calibrated
demography (R-58...R-64) and should not be done casually to chase a cycle result.

---

### R-89 - The delegitimation trap: full ascription is an ABSORBING state, not an equilibrium (2026-07-20)

**Origin.** T-9 pilot (2 arms, 4000 steps / 3000 founders, stratified arm = full R-82...R-87 elite stack) run
to check whether dynastic concentration (`eff_lineages`/`lin_top_share`) diverges from baseline before
committing to the full 15,000-step campaign. The stratified arm's tail showed `ascribed_frac`/`frac_gumsa`
pinned at exactly 1.0 and `leader_tenure` frozen at 9.2-9.3yr across 39+ consecutive checkpoints (950 steps) -
too clean to be a converged steady state.

**BUG 1, confirmed by reading the code.** `_do_legitimacy()`'s cred-conversion step relaxes EVERY ascribed
agent's cred toward one fixed target:
```
a.cred += LEGIT_RELAX * ((1.0 + cg) - a.cred)   # cg = legit_cred_gain, the SAME constant for every lineage
```
Once ascription reaches 100% of the population, everyone relaxes toward the same number, so cred stops
differentiating between lineages. Measured: `gini_cred` collapses from a peak of 0.67 (step 150) to a
permanent 0.006-0.010 from step 2625 on.

**BUG 2, confirmed by reading the code - the one that matters.** `_do_delegitimation()`'s resentment update
requires a live non-ascribed "oth" group WITHIN THE SAME BAND to compute privilege:
```
if not asc or not oth:
    self._band_resentment[bid] = self._band_resentment.get(bid, 0.0) * (1.0 - alpha)   # decay only, never rebuild
    continue
```
Once every lineage present in a band is ascribed, `oth` is empty, resentment can only decay, and reversion
(`r >= thr`) can never fire again for that band. **This is a one-way door**: nothing in the mechanism can push
a fully-saturated band back out. Ascription is a per-lineage ratchet that only grows (R-86), so any band will
eventually random-walk into full saturation given enough time - and once there, it is stuck permanently.

**MEASURED, directly from the pilot's logged trajectory** (`campaign_trajectory_t9_stratified.json`, plotted
in `plots/r89_ascription_trap.png` / `_zoom.png`):
- Steps 1-2600: genuine oscillation. `ascribed_frac` ranges from 0.0 up to 0.68 and back down to 0.03-0.13
  repeatedly; `frac_gumsa` swings 0.3-1.0. This is the intended Leach gumsa<->gumlao dynamic, and it is real for
  the first 65% of the pilot.
- Step 2600 -> 2625 (one 25-step window): `ascribed_frac` jumps 0.651 -> 1.0 population-wide; `frac_gumsa`
  hits 1.0 simultaneously.
- Steps 2625-4000 (remaining 1375 steps, 34% of the pilot): `ascribed_frac`/`frac_gumsa` pinned at exactly
  1.0, zero deviation across 39 checkpoints. `leader_tenure` frozen 9.2-9.3yr. No reversions.

**T-9's actual metrics are computed from lineage counts, not cred - confirmed by reading `dynasties()`.**
`eff_lineages`/`lin_top_share`/`size_gini` are computed purely from `sizes = [len(v) for v in groups.values()]`
(population count per patriline); no `cred` term appears anywhere in that calculation, so BUG 1 cannot
contaminate them directly.

**BUG 2's effect on T-9's metrics, in THIS pilot, is small and continuous with the pre-trap trend, not a
discontinuity.** Directly measured (excluding the initial 1200-step founder shakeout, which is ordinary
finite-population lineage extinction, same process R-66/connubium-cut2 already characterized):

| | pre-trap (step 1200-2625) | post-trap (step 2625-4000) |
|---|---|---|
| eff_lineages, mean | 3.39 (range 2.9-4.4) | 3.00 (range 2.9-3.1) |
| lin_top_share, mean | 0.430 (range 0.406-0.450) | 0.444 (range 0.407-0.472) |

Both continue the same slow-consolidation direction they were already on (n_lineages itself falls 8 -> 5 across
steps 2400-2800, smoothly through the trap boundary) - a modest further tightening, not a jump timed to the
trap.

**BUT this pilot cannot clear the full campaign.** The trap had only 1375 of 4000 steps (34%) to act here. A
15,000-step campaign (3.75x longer, same population-scale dynamics) would be expected to hit the same trap at a
similarly early step and then spend roughly 12,000+ steps - 80%+ of the run - frozen in a state the mechanism
was never designed to reach. Whether the modest post-trap drift seen above stays modest over 10,000+ additional
trapped steps, rather than compounding, is not established by a 1375-step window. Running the full campaign on
the mechanism as-is means the "stratified" arm's headline numbers would mostly describe a broken-oscillator
end-state, not the Leach cycle R-87/88 were built to produce.

**RECOMMENDATION, ACTIONED.** Fixed BUG 2: `_do_delegitimation()` now falls back to the population-wide
commoner mean when a band has ascribed members but none of its own commoners left (`sic_games/phase1_model.py`,
`_do_delegitimation`), so a fully-ascribed band remains capable of reverting. Bands that still have live
commoners of their own are untouched — confirmed byte-for-byte, see validation below. Two new regression tests
(`test_saturation_trap_is_fixed_by_the_population_fallback`, `test_fully_ascribed_band_can_still_revert`) force
the exact broken state directly and check resentment builds/fires. Full suite: 812 passed, 1 xfailed (was 810
before the two new tests). BUG 1 (fixed cred-relaxation target) left as-is per plan — see validation below for
whether it still matters.

**VALIDATION, part 1: the fix is inert on unaffected bands.** Re-ran the stratified arm at the pilot's own
scale (`campaign_progress_t9_stratified_fix.txt`, 6000 steps, 50% longer than the original pilot). Steps 1-200
are reproduced BIT-FOR-BIT against the original pre-fix pilot (every logged field, to the printed decimal) -
exactly as expected, since the fix only changes behaviour in the specific edge case (`not oth` while `asc` is
non-empty) that does not arise that early.

**VALIDATION, part 2: at full campaign scale, still no recovery within 6000 steps - the fix looked dead on
arrival.** `ascribed_frac` saturated even earlier this time (step 1950 vs. 2625) and then stayed pinned at
exactly 1.0 for the remaining 4050 steps (67.5% of the run), same as the unfixed pilot. Zero reversions logged.
This is NOT a sign the fix doesn't work (see part 3) - `run_campaign.py` was never logging
`mean_resentment`/`max_resentment`, so there was no way to see whether resentment was climbing toward threshold
and simply hadn't arrived yet, or was genuinely inert.

**VALIDATION, part 3: a small, per-step-instrumented probe (`probe_r89_fix.py`, N=500, the campaign's actual
ELITE_KW values - `resent_alpha=0.001`, `resent_threshold=0.5`, `resent_privilege_ref=10.0`, nothing
hair-triggered) settles it directly: the fix works, and the pre-fix code could not possibly have produced
this under any parameter setting.** Plotted in `plots/r89_fix_validation.png`:

- Steps ~400-2650: `max_resent` (the most-resentful band) sits flat at 0.225 for ~2250 steps - unremarkable;
  R-88 already established band churn resets most bands' resentment long before a slow (alpha=0.001, ~1000-step
  time-constant) EMA matures, so individual bands plateau at whatever their local privilege gap supports.
- Step ~2650 on (population-wide `ascribed_frac` locks near 1.0): `max_resent` and `mean_resent` both start
  climbing in a sustained way for the first time - the population-wide fallback engaging exactly where it
  should.
- **Step 3102: `max_resent` reaches 0.5 and a reversion FIRES.** `ascribed_frac` drops 1.000 -> 0.611 in a
  single step - "every lineage present loses ascription", exactly the reversion code's documented behaviour.
  Under the pre-fix code this was mathematically impossible: `oth` was empty, so resentment could only decay,
  never reach the threshold, ever, regardless of `resent_alpha`/`resent_threshold`/any other parameter. This is
  a structural difference, not a tuning one.
- After the reversion: `max_resent` snaps to 0.489 (a DIFFERENT band, one that did not revert) and sits there
  for the remaining 2400 steps without crossing again, while `ascribed_frac` climbs back to ~0.97-0.98 and
  `mean_resent` decays 0.20 -> 0.02. Plausible mechanism, not yet directly confirmed: the reverted band's
  ex-nobles carry residual high cred (cred is not reset on reversion, only status is), so they raise the
  population-wide commoner baseline everyone else's fallback compares against, damping the remaining stuck
  band's privilege signal just below threshold.

**READING THE TIMESCALE.** One full cycle (climb, cross, partial recovery) took ~3100 of 5500 probed steps at
N=500; the real campaign-scale run got 4050 post-saturation steps without completing one. Slow and irregular is
consistent with what R-87/88 set out to model in the first place - Leach's own claim is that hereditary
inequality "lasted for A FEW GENERATIONS, and then collapsed" (generational, not a fast flicker), and R-88
already established that no band-attached social memory can express a timescale the band substrate itself
outlives. **What changed is not the speed of the cycle - it is that a cycle can now complete AT ALL.** The
open question this does not resolve: whether the full 15,000-step campaign (roughly 3x this probe's horizon,
and with ~13,000 steps of runway past a saturation onset around step 2000) sees multiple reversions, one, or
lands in another multi-thousand-step plateau like the 2400-step one observed here. Not settled by current
evidence either way.

### R-90 - Lineage BRANCHING: the mechanism was necessary, the SHAPE was wrong (2026-07-20)

*(Documented retroactively 2026-07-21 - the mechanism was built and committed at the time, the RESULTS entry
was missed. Superseded in shape by R-92; recorded because the FAILURE is the instructive part.)*

**Origin.** R-89 established `_lineage` was founder-seeded and only ever LOST by extinction, never created - an
absorbing Markov chain, so fixation has probability 1. Measured: 3000 founding patrilines -> 5 by step 1950,
then frozen at exactly 5 for the next 5,650 steps. That breaks the FILED Hill 2011 target R-25 already passed
(~7 lineages/band is impossible with 5 worldwide) and freezes the elite layer.

**Built:** the standard infinite-allele device already used by `genome_mutation` - with probability
`lineage_branch_rate` a newborn founds a new named line. Default OFF, no RNG draw when off, bit-exact.

**MEASURED, and it FAILED on the statistic that matters.** Campaign scale, 3000 founders x 3000 steps:
n_lineages rose 5 -> 32, but `eff_lineages` (inverse-Simpson) FELL 3.4 -> 1.8 and `top_share` ROSE 0.42 -> 0.73.
`lineages_per_band` barely moved (2.14 -> 2.33 against a target of ~7). **Diversity up on paper, down in
substance.** Cause: a per-birth branch mints a SINGLETON, and a lineage of one usually leaves no descendants, so
the mechanism adds a churning tail of ephemeral names while the dominant lineage keeps its mass untouched.

**It DID fix the R-89 trap** (1,089 reversions in the final third vs 0 for the control), which is why the
diagnosis needed BOTH statistics - judged on `n_lineages` alone it looked like a success.

**THREE METHOD ERRORS, all caught before they shipped a number, all recorded because they recur:**
- the presence test was UNDERPOWERED: at rate 0.05 the world gives ~51 births in 60 steps => ~2.6 expected
  events => P(zero) ~ 7%, and seed 0 drew zero, failing a test whose mechanism was working.
- the first calibration sweep had NO POSITIVE CONTROL (D1/D4): on the plain substrate the Hill target was
  already met AT RATE 0.0 (7.34 lin/band), so the swept parameter was not rate-limiting and the sweep could
  only ever have said "change nothing". The collapse requires the ELITE STACK, where male_rs_gini ~0.70.
- a monotone population drop across that sweep (3490 -> 635) was checked and is NOT real: 3 seeds x 2 rates x
  elite on/off gives 631 vs 634 and 329 vs 328. Single-seed RNG-stream divergence; within-condition spread
  (802/647/444) exceeds any between-condition difference.

**Interpretation that survives.** Male-lineage collapse under an inequality layer is what Karmin 2015 REPORTS
(female Ne up to 17x male Ne, 8-4 kya). The model reproducing a Y-bottleneck is CORRECT; what is wrong is that
it cannot RECOVER from one, because named lines could only die. See R-92 for the corrected shape.

---

### R-91 - CONSISTENCY INVARIANTS: complaining when two numbers cannot both be true (2026-07-20)

*(Documented retroactively 2026-07-21; tool committed at the time.)*

**Why it exists, and why it is not more D-series.** D1-D14 ask *"is this measurement trustworthy?"* and they
work - in one session they caught an underpowered test, a sweep with no positive control, and a fake population
crash. They do NOT catch the failure behind R-89/R-90's worst errors, where every number was INDIVIDUALLY
CORRECT and the RELATIONSHIP between them was impossible. `ascribed_frac=1.0` sat beside `pct_stratified=11.5`
in the SAME log line for hours, unnoticed. **More FIELDS do not help - that line already carried ~20. Passive
reporting is exactly what failed.** `sic_games/invariants.py` is ACTIVE: it returns violations and the harness
prints them, so a 90-minute run says something is incoherent at minute 3.

**Four rule classes**, each generalised from a real failure rather than invented: CONTRADICTION (two fields
mutually impossible) - DOMAIN (a threshold on a share whose hidden denominator drifted) - FROZEN (a cumulative
counter that stopped while its driver is live) - STUCK (a field that should fluctuate, pinned).

**Validated as an INSTRUMENT (D1 applied reflexively).** Every rule is exercised first on a reconstruction of
the actual observed failure, then on a healthy trajectory that must stay silent - the null is asserted before
any positive is trusted. It also must NOT fire when high ascription is accompanied by genuinely ranked
societies, i.e. it keys on the contradiction, not on one field being large.

**EARLINESS, the whole point.** Replayed on the R-90 control arm it names the ROOT CAUSE (share threshold
degenerate) at **step 475**, against step 1950 where the collapse first became visible by eye - about 2.5
minutes into a 16-minute run.

**IT SURFACED A FINDING NOBODY HAD LOOKED FOR.** Replayed over all 15 archived campaign trajectories, **every
historical run reached the absorbing lineage state**: the R-66 deep-time arms froze at step ~5,700-5,800 of
15,000 (61-62% of the run); the R-67 45,000-step cycling tests at 11,525 and 14,850 (74% and 67%). Those runs'
DYNASTY numbers were therefore measured in a pool that could no longer change. It discriminates rather than
firing everywhere: `t9_baseline` (no elite stack) and both swidden runs come back clean.

**R-66 RE-CHECK, done from the archived trajectories (no re-runs needed).** Dynasty metrics AT the freeze point
vs at end-of-run: `off` top_share 0.317 -> 0.886 (eff_lineages 6.6 -> 1.3); `on` 0.630 -> 0.453 (eff 2.4 -> 3.3).
**R-66's DIRECTION survives and is real** - with defensibility off one patriline runs away, with it on the
system resists, and eff_lineages RISING under `on` is not something drift alone produces. **What does not
survive is the headline NUMBER:** 88.6% is the endpoint of a closed pool, where fixation is near-guaranteed
given enough time, not a measured property of defensibility. R-67's claims (no cycling; connubium breaking
fixation) hold at BOTH the freeze point and the end, and stand unchanged.

**Two defects in the checker itself, found later by running it on R-93's fix** - see R-93.

---

### R-92 - Lineage SEGMENTATION works; the per-band target is blocked by a CEILING, not by the mechanism (2026-07-21)

**Origin.** R-90's per-birth branching had the wrong shape: it minted SINGLETON lineages, which mostly die, so
it inflated the lineage COUNT while concentration got worse (n_lineages 5->32 but eff_lineages 3.4->1.8,
top_share 0.42->0.73). Replaced by a PAIR - branching now seeds a heritable `_subclan` tag (singletons harmless
there), and `_do_lineage_split` promotes a sub-branch to a full lineage only once it has grown.

**A DESIGN CONSTRAINT DISCOVERED BY MEASUREMENT, not assumed.** The first cut split off "the live patrilineal
descendants of an apical ancestor" - the textbook sub-clade. It is not computable here: live `_father` chains
reach a MAXIMUM DEPTH OF 2 (median 1) even after 400 steps, because a chain terminates at the first ancestor
born without an assigned father and early births largely lack one (father-link rate 19% at step 80 -> 74% by
step 400). Deep ancestry exists only in the offline genealogy CSV, never in memory. Hence the inherited tag,
which is in any case what a Y-haplogroup label actually is.

**MEASURED at campaign scale** (3000 founders x 3000 steps, elite stack ON, all arms identical otherwise):

| arm | n_lineages | eff_lineages | top_share | lineages/band |
|---|---|---|---|---|
| control (no mechanism) | 5 | 3.4 | 0.422 | 2.14 |
| R-90 singleton branching | 32 | 1.8 | 0.733 | 2.33 |
| **R-92 segmentation, rate 3e-5** | 28 | **5.9** | **0.235** | **3.69** |
| R-92 segmentation, rate 1.5e-4 | 82 | 4.1 | 0.347 | 3.51 |

**RATE IS NOT THE LEVER, and pushing it reproduces the pathology it was built to fix.** 5x the rate gives 3x
the lineages but LOWER effective diversity and HIGHER concentration - splitting faster shatters lineages into
fragments quicker than they can grow. The LOW rate is adopted as the better setting.

**INDEPENDENT CONFIRMATION from R-91.** The consistency checker - written before these runs existed and not
touched for them - drops from SIX violations on the control (frozen lineage pool, dead reversion mechanism,
ascription pinned at 1.0, frac_gumsa pinned, rank-vs-society contradiction, absorbing state) to exactly ONE on
both segmentation arms. The R-89 trap and the absorbing state are gone.

**THE HILL TARGET IS STILL MISSED (3.69 vs ~7), and the reason is a CEILING the mechanism cannot lift.**
Computed null, two independent routes agreeing to 2dp: for a band of size b drawn at random from a distribution
with inverse-Simpson E, expected distinct lineages = E*(1-(1-1/E)^b) ~ E, because b (~29) >> E. **So
`lineages_per_band` is bounded above by `eff_lineages`** - 7 per band is arithmetically impossible while the
effective count worldwide is 5.9, at any rate. Two separate deficits therefore remain, NEITHER of them the
segmentation rate:
  (a) eff_lineages must exceed ~7 - needs a more EVEN lineage-size distribution, and raising the split rate
      moves it the wrong way (5.9 -> 4.1);
  (b) observed lpb is only 63% of even that ceiling (3.69 vs 5.87) - bands over-represent locally-resident
      lineages. This is SPATIAL, i.e. the marriage-relocation/connubium machinery (cf. R-67/R-68 on Cut-2's
      spatial effects), not the descent mechanism.

**CAVEAT ON THAT NULL, recorded so the 63% is not over-read.** It assumes equal-sized lineages, so it
UNDER-estimates expected distinct for a skewed distribution - which is why the R-90 arm reads a nonsensical
129%. For the segmentation arms the true shortfall is therefore WORSE than 63%; the clustering conclusion is
conservative.

**Single seed per arm.** The large contrasts (eff 5.9 vs 1.8) are far beyond noise; the smaller ones are not
defended without replication.

### R-93 - Relative legitimacy: fixing one hidden denominator immediately exposes the next (2026-07-21)

**The fix.** `legit_threshold` compared a lineage's SHARE of its band's feasting to a CONSTANT. Mean share is
1/lineages_per_band, so the test discriminated only above 1/0.15 = 6.67 lineages/band, against a FILED Hill 2011
target of ~7 - a FIVE PERCENT margin. Measured lpb was 2.14-3.69, so the AVERAGE lineage cleared the bar and
nobility was universal by arithmetic. Now normalised by the competing-lineage count: 1.0 means "exactly an
average lineage". Scale-free, and Friedman's own logic.

**MEASURED at campaign scale** (3000 founders x 3000 steps, elite stack ON, segmentation ON in both R-92/R-93):

| arm | n_lineages | eff_lineages | top_share | lineages/band | ascribed | strat% |
|---|---|---|---|---|---|---|
| control | 5 | 3.4 | 0.422 | 2.14 | 1.000 | 11.5 |
| R-92 segmentation | 28 | 5.9 | 0.235 | 3.69 | 0.581 | 7.8 |
| **R-93 + relative** | **96** | **18.1** | **0.154** | **6.66** | **0.063** | **23.3** |

**lineages_per_band 6.66 against the Hill target of ~7 - essentially met**, from 2.14 at the start of this arc.
R-92 alone could not get there because lpb is bounded above by eff_lineages; relative legitimacy lifted
eff_lineages to 18.1, which raised the ceiling. Nobility is now a real 6% minority rather than everyone.

**BUT: the reversion mechanism now NEVER FIRES.** cum_reversions = 0 across all 3000 steps, against 5,741 in the
R-92 arm. Diagnosed: resentment peaks at 0.166 against `resent_threshold` 0.5, where R-92 peaked at 0.499.
Privilege is `(mean_cred_ascribed - mean_cred_other)/mean_cred_other / resent_privilege_ref`, and
`resent_privilege_ref=10.0` was implicitly calibrated in the regime where ascription was UNIVERSAL and cred
saturated toward 1+legit_cred_gain=11. With nobility a genuine minority the privilege signal is much smaller and
the threshold sits out of range.

**THE SAME BUG CLASS, ONE LAYER DOWN.** `resent_privilege_ref` is a normaliser and `resent_threshold` a
threshold on the normalised quantity - the identical structure to the bug just fixed, calibrated against the
BROKEN version of the mechanism upstream. Fixing the forward mechanism moved the regime out from under the
reverse one. Any threshold on a normalised quantity has a validity domain; this is the third instance in three
results (legit_threshold, resent_privilege_ref, and R-92's rate/eff interaction).

**TWO DEFECTS IN THE R-91 CHECKER ITSELF, found by running it on the fix:**
- it reported the quiet reversion counter as *"the reversion mechanism is dead"* at step 475, when at that point
  a resent_alpha=0.001 EMA (~1000-step constant) had simply not matured. The outcome was right, the stated cause
  wrong - and a checker that misattributes a cause sends the reader hunting in the wrong place. Now separates
  STOPPED (was firing, died) from NEVER-FIRED (longer window, and points at the threshold's range).
- the OFFLINE CLI re-check produced a false DOMAIN positive on an already-fixed run, because trajectory `meta`
  did not record the mode while the live harness passed it correctly. `meta` now carries it.

**Not yet done:** re-anchor `resent_privilege_ref`/`resent_threshold` for the minority-elite regime, then re-test
whether the gumsa<->gumlao cycle returns. Single seed.

### R-94 - Scale-free resentment: privilege as an EFFECT SIZE (2026-07-21)

*(Documented retroactively 2026-07-21 with R-95/R-96/R-98; all four were committed at the time.)*

**Third instance of charter D15 in three consecutive results.** Privilege was
`(m_asc - m_oth)/m_oth / resent_privilege_ref`, and ref=10.0 had been chosen while ascription was UNIVERSAL and
cred saturated toward `1+legit_cred_gain`=11. When R-93 made nobility a real 6% minority the gap shrank,
resentment peaked at 0.166 against a 0.5 threshold, and reversions NEVER fired - 0 in 3000 steps against 5,741
before. **The reverse mechanism had been calibrated against the BROKEN forward mechanism**, so repairing the
forward one moved the regime out from under it.

**Fix, per D15: scale-free rather than re-tuned.** Privilege is now the gap in units of the band's OWN pooled
spread - an effect size, with no denominator left to drift - and the threshold is ANCHORED on Cohen's
conventions (0.8 = "large") instead of invented. Guards: sd≈0 yields zero privilege rather than dividing by
zero, and the value is capped so one near-uniform band cannot dominate the accumulator off a tiny absolute gap.

**A PERFORMANCE BUG introduced and fixed here, recorded because the symptom was misleading:** the first cut
rebuilt `asc + pop_oth_cred` per band whenever a band had no commoners of its own - O(pop) per band per step,
~1.4M operations/step at campaign scale. The run went 3-4x slower at a LOWER population, which is what exposed
it. Replaced with running sums hoisted once per step.

---

### R-95 - Resentment ACCUMULATES, and the VILLAGE holds it (2026-07-21)

**Two paired fixes; neither works alone, and a test asserts that rather than leaving it as a claim.**

**(a) The mechanism never accumulated.** `_do_delegitimation`'s own docstring says in capitals that resentment
ACCUMULATES, after Leach. The code was an EMA, which does not accumulate - it TRACKS, converging to whatever it
is fed. **A threshold at or above the typical privilege can therefore NEVER be crossed, at any horizon.**
Measured: the grudge rose to **0.796 against a threshold of 0.800** and stopped there; 1 revolt in 3000 years.
The irony worth recording is that 0.8 was correctly ANCHORED (Cohen "large") and the real effect sizes genuinely
are ~0.8 - a good anchor pointed at the wrong quantity, because a running average cannot exceed its own mean.

**(b) The memory outlived its container by ~40-100x.** R-88 measured band lifetime at 10.2 yr median / 17.5
mean; the grudge needed 700-1600 yr to mature, and band fission resets it to zero. Leach's gumlao premises
describe VILLAGES ("villages autonomous", headmen, councils of elders), not 25-person residential bands. Now
held by the SETTLEMENT, following R-71's per-site precedent exactly: the place remembers, the members churn.

**What is now anchored, and what stopped being free:** the crossing threshold is FIXED AT 1.0 by construction -
it is no longer a knob. What is calibrated instead is a TIME, `resent_years_to_revolt`=80, from Flannery ch.10's
*"lasted for a few generations, and then collapsed"*. Privilege scales it: twice the gap, half the wait.

**RESULT: revolts fire (323 vs 0 and 1) but nobility is EXTERMINATED rather than cycled** - villages holding
nobility fell 82% -> 3%, and the revolt curve flattened for want of anything left to overthrow. That exposed
R-96.

---

### R-96 - Rank is LOCAL: a lineage is noble in a place, not in the world (2026-07-21)

**A SCOPE MISMATCH present since R-86.** `_lineage_ascribed` was a single GLOBAL set while every mechanism
acting on it is local, so `discard(lineage)` at a revolt de-ranked that lineage in EVERY other village at the
same instant. Measured: ~7% of all lineages stripped per revolt, which is why R-95 annihilated nobility instead
of cycling it. **It contradicts the anchor head-on** - Leach's observation is that communities sit in DIFFERENT
states simultaneously; a single global set cannot represent that at any parameter setting.

**Invisible until now for the recurring reason:** before R-93 the ascription threshold was degenerate, so status
was re-earned within a few years and the global strip was undone before anyone could notice the scope was wrong.
Fixing the threshold made status genuinely hard to earn, at which point the same strip became permanent.

**Rank is now keyed per (community, lineage).** The key is polymorphic - a bare lineage id when off, a pair when
on - so ONE code path serves both and OFF stays bit-exact (the 15 existing legitimacy tests pass unchanged).

**RESULT - the first arm where nobility and revolts COEXIST:**

| arm | ascribed | revolts | frac_gumsa |
|---|---|---|---|
| R-93 | 0.063 | 0 | decaying (nobility permanent, never overthrown) |
| R-95 global rank | 0.006 | 323 | 0.03 (nobility annihilated) |
| **R-96 local rank** | **0.365** | **678** | **0.58-0.99 (a patchwork)** |

Also eff_lineages 10.0, lineages_per_band 6.12, gini_cred 0.508, strat 19.9%.

**A TEST FAILED USEFULLY and became a finding:** with rank keyed to BANDS nobody is ever ennobled at all,
because the legitimacy stock resets on band fission (~10 yr) while needing ~50 to mature - R-95's container
churn reappearing one level up, in the FORWARD mechanism. Local rank therefore REQUIRES a persistent community;
that dependency is now a standing test.

---

### R-98 - RANK unlocks HIERARCHY (2026-07-21)

**The gap.** `society_from_character(density, surplus_frac)` reads CROWDING and SURPLUS only and never asks
whether anyone is ranked. So a village where every lineage is hereditary nobility stayed labelled
`egalitarian_forager` if sparse and poor - and since `LEADER_SOCIETY_WEIGHT` is **0.0** there, that nobility had
NO structural consequence: no growth past the band cap, no scalar-stress relief (Johnson 1982), the entire elite
layer decorative with respect to settlement size. **The model had surplus->hierarchy but not rank->hierarchy.**
This is what the R-91 checker flags as the rank-vs-society CONTRADICTION.

**The anchor says rank can come first.** Leach's gumsa were rain-fed SWIDDEN HILL FARMERS - no storable glut, no
great surplus - yet had ranked lineages, chiefs, tribute and "all settlements under one chief". Testart's
storable-surplus route is ONE road to hierarchy, not the only one. The promotion is therefore applied AFTER the
aquatic gate, deliberately overriding it.

**A band holding ranked lineages climbs ONE rung** (egalitarian -> complex -> stratified, stratified a fixed
point), converting leader weight 0.0 -> 0.5. Rank opens the route; it does not hand out chiefdoms.

**Threshold DERIVED, not picked:** 0.15 ~ 1/7, because the FILED Hill 2011 target is ~7 lineages/band, so one
ranked lineage among them is ~0.14 of heads. It means "at least one lineage here is ranked".

**INHERITANCE LIT AUDIT (asked 2026-07-21), recorded here since it scopes the next mechanism:**
- **by SOCIETY - QUANTIFIED.** BHM 2009 Table 2 `beta material`: hunter-gatherer 0.17, horticultural 0.09,
  pastoral 0.67, agricultural 0.55. Filed + verified, and the same table the alpha weights already come from.
- **by RANK - ATTESTED, NOT QUANTIFIED.** gumsa "elite bride-price higher" vs gumlao "equal bride-price";
  "splits produce senior/junior" vs "no senior/junior". Direction anchored, magnitude would be [DESIGN].
- **by GEOGRAPHY - NOTHING NEW NEEDED.** BHM's categories are economic systems, and terrain acts THROUGH
  subsistence; biome->society already exists, so plains vs mountain differ by supporting different economies.

---

### R-97 - The elite layer WORKS and still does not cycle. Turchin's cycles are not at this SCALE (2026-07-21)

**The question this arc existed to answer.** R-67/R-68/R-71 gave three independent negatives for secular cycles
from the subsistence base, and the standing conclusion (DE-14) was that cycles REQUIRE the explicit Turchin
elite/instability layer. That layer now works: R-96 sustains a real noble minority AND ongoing revolts, in a
patchwork of ranked and egalitarian villages (ascribed 0.365, 678 revolts, frac_gumsa ranging 0.58-0.99). So:
does it cycle?

**INSTRUMENT REUSED, NOT REBUILT.** `probe_hcycles.period_of` — the detector fixed twice and supervisor-approved
in R-87c/d (linear detrend; period capped at window/3; a genuine local maximum required). Null floor from R-87's
own white-noise calibration: ac_peak mean 0.03, **p95 0.13**, max 0.19. Compared against 0.13, not an invented
cut-off (using an invented 0.2 was R-87c's original error).

**D1 FIRST — the detector was re-validated at THIS resolution before any negative was read.** Campaign snapshots
are 121 points at 25-step spacing, far coarser than the series R-87 validated on, so an underpowered detector
would have produced a worthless negative. Injecting known cycles into noise matched to the observed magnitude
(sd 0.143): **9/9 DETECTED**, down to amplitude 0.08 — i.e. smaller than the variation actually present in the
arms. The instrument is adequate; a negative is interpretable.

**RESULT — all four arms below the noise floor** (`probe_r97_cycles.py`, series `frac_gumsa`):

| arm | sd | period reported | ac_peak | vs null 0.13 |
|---|---|---|---|---|
| coastal (R-96) | 0.172 | 375 yr | 0.068 | BELOW |
| tropical, no soil | 0.131 | 500 yr | 0.083 | BELOW |
| tropical, rotation OFF | 0.131 | 500 yr | 0.078 | BELOW |
| TRUE swidden (rotation ON) | 0.137 | 825 yr | **-0.008** | BELOW |

**NO CYCLES. A FOURTH independent negative, and the first from the elite side.**

**WHY, and it is visible in the mechanism rather than inferred.** Villages DO flip — thousands of revolts in
every arm. But each village keeps its own grudge against its own nobles and revolts when its own threshold is
crossed. **Nothing couples one village's timing to its neighbours'.** Independent oscillators with no coupling
sum to a flat aggregate, which is exactly what the series show.

**THE REFRAME, which is the actual finding.** The missing ingredient is not a better elite mechanism — it is a
LEVEL OF POLITICAL ORGANISATION this model does not have. Turchin's secular cycles are a property of STATES:
taxation, standing armies, elite overproduction competing for a finite number of OFFICES, fiscal crisis. What
synchronises local rise-and-fall into an aggregate cycle is a superordinate polity that all the villages belong
to. **We built the Kachin; Turchin was writing about kingdoms.** Autonomous villages with big men and hereditary
rank produce exactly what Leach describes — local, unsynchronised rise and fall — and that is what the model now
reproduces. The negative is therefore evidence about SCALE, not a failure of the elite layer.

**This was already flagged twice and proceeded past.** ROADMAP's Dynamic Social Evolution stage says the Ibn
Khaldun dynastic cycle *"needs a large settled/stratified polity (a keystone chief + succession crisis); the
current model tops out at mobile-forager bands ~25, so the settlement/high-tier-resource substrate is a
PREREQUISITE."* The prerequisite was recorded and the elite layer was built at village scale anyway.

**Where the next rung is already visible in filed sources:** the gumsa premises describe *"all settlements under
one chief"* with tribute flowing upward; Flannery ch.16 (Tonga) gives sacred/secular chief splits, assassination
constrained by mana, and resource allocation as the balancing knob — filed, extracted, and unbuilt. R-64 already
produces stratified CENTRES above ordinary villages, so the substrate has the beginnings of a hierarchy that the
political layer was never attached to.

**CONSEQUENCE for DE-14:** its conclusion ("cycles require the explicit Turchin elite layer") is now SUPERSEDED —
the elite layer is necessary-but-not-sufficient. See the dated revision there.

---

### R-106 - The demography and the missing Malthus are ONE defect: nothing in this model can be HUNGRY (2026-07-30)

**The question.** Two standing complaints: the population is far too young (median age 13 vs ~20) with too many
motherless children (8-11% vs Ache ~2%), and no Malthusian/secular cycles ever emerge. Asked to fix the
demography as an EMERGENT property, not by forcing a rate.

**FOUR OF MY OWN HYPOTHESES WERE FALSIFIED BEFORE THE REAL ONE SURVIVED.** Recorded because each was plausible
and each cost a measurement:
1. *"It is a GROWTH artefact - the population is still climbing."* NO. Starts of 3k/12k/20k all converge on the
   same ~4.8k with the same age structure; the dense starts CRASH. This is the equilibrium demography.
2. *"Everyone is pinned at the reserve cap."* NO. Only 0.6-0.8% are at the cap. (My `wealth/floor` metric had
   divided by `reserve_scale()`, which scales with wealth - the normalisation manufactured the flatness.)
3. *"Mortality MULTIPLIERS are stacking."* NO. Ablating density-disease, terrain-risk or orphan-mortality each
   moves e0 by <0.5 yr, and `a2_cap` never binds (0 hits).
4. *"Agglomeration gives INCREASING returns, so density-dependence has the wrong SIGN."* NO. Fitting S ~ n^gamma
   gives gamma 0.805 - decreasing returns. Crowding does not pay.

**THE CHAIN, every link measured (coastal/temperate, 900-1200 steps, 5x density range):**
1. Burn is ~68% of the floor-to-full reserve span per step, so an agent either re-saturates at the cap or dies
   within a step. Margin at the trough: **0.46 burn-steps** - nobody survives one missed harvest.
2. Both fertility-brake candidates are therefore CONSTANTS: post-harvest reserve 0.996 of full, post-burn trough
   (`_condition`) 0.318, each with spread ~0.002 and ZERO density response.
3. So `energetic_fertility_factor` returns ~0.995 always. The brake is inert BY CONSTRUCTION.
4. Births cannot respond: CBR 53.8 -> 52.0 across 5x density (-3%).
5. Regulation falls entirely on mortality: CDR 48.5 -> 77.0 (+59%), starvation 46% -> 61% of deaths.
6. A stationary population has e0 = 1/CDR, hence **e0 20.7**, median age 13, motherless 8-11%.
7. The young population and the orphan rate are ONE symptom with ONE cause, seven links upstream.

Deaths before age 1 are 11.5% of deaths (~= q(0) in a stationary population), MATCHING the Ache ~12%. The excess
is in ages 1-5 (29.7% vs ~20%) and it is not in the multipliers - it is the mortality-only regulation.

**This partially re-derives R-12/R-13 ("starvation-dominated, unrealistically strong") from the fertility side,
and it is consistent with R-16/R-17:** at r=0 e0 is FERTILITY-pinned, with a documented stationary e0 ~28. Our
20.7 sits ~7 yr below even that, and the fact that mortality does 100% of the regulating is the defect.

**WHY NO MALTHUS - two independent obstacles.**
- **The world is 99% EMPTY.** 4.8k agents occupy **88-100 of 10,000 cells** while **94.1% of cells could feed at
  least one forager** (median cell cv = 1.62x burn). The population never approaches the resource base, so
  aggregate scarcity is impossible. This clumping PERSISTS with agglomeration AND sedentism both off (109
  cells), so band co-residence drives it independently. **OPEN.**
- **The gradient is flattened ~5x.** Per-capita elasticity: full stack **-0.195**, aggl off -0.387, aggl+sedentism
  off **-1.062** (textbook sharing). Doubling a cell's population costs each occupant only 13%. The third arm
  doubles as a SELECTION CONTROL - with no mechanism adding S, gamma ~ 0 shows richer cells are not drawing
  proportionally larger crowds, so the cross-sectional fit is not badly confounded.

Regulation is **distributional, not Malthusian**: in crowded cells the MEAN occupant gets 2.10x subsistence
while 11-15% fall below it. The average agent never experiences scarcity.

**POSITIVE CONTROL (gradient is NOT the lever).** Ran 500 model-yr at all three elasticities. No oscillation at
any of them; population CV non-monotonic (10.9 / 4.5 / 16.1%); deaths out-swung births in ALL arms (CV ratio
0.56 / 0.46 / 0.45). Steepening scarcity does not move regulation to the birth side - it just kills more people
(equilibrium 5258 -> 763 -> 261).
> **INSTRUMENT CAVEAT - this result is PROVISIONAL.** I wrote an ad-hoc periodogram instead of reusing
> `probe_hcycles.period_of`, the detector fixed and approved in R-87c/d, and hit the failure it was fixed for:
> mean-only detrending, so drift loaded onto the lowest scanned frequency and two arms reported a "period" of
> exactly window/2. Re-running with linear detrend still pegged all three arms at the scan floor (=> red noise,
> no characteristic timescale; 36-49 turning points = ~8-10 yr noise; residual CV 3.7-8.3% vs the 30-50% swings
> of real secular cycles). **Must be re-run against `period_of` and its calibrated null floor (ac_peak p95
> 0.13) before the negative is filed as firm.**

**THE FIX - `enable_intake_fertility` (MECHANISMS; PARAMETERS §21.10).** Fertility reads a slow EMA of
intake/requirement instead of a reserve level that cannot vary. Intake IS the live signal (p10 0.93 to p90 4.26
of requirement) and is the biologically correct one - Ellison: fecundity tracks energy FLUX, not stored reserve.
Thresholds ANCHORED, not tuned: 0 at maintenance, full at maintenance + the lactation increment (~+500 kcal/d on
~2500, FAO/IOM => 1.2x). Accumulates only from menarche, because a juvenile's GATHERED intake understates what
it EATS (juveniles are provisioned).

**WHAT IT BOUGHT** (off -> on):

| | n=3000 | n=15000 |
|---|---|---|
| e0 | 18.5 -> 20.5 | 19.1 -> **21.4** |
| median age | 13.6 -> 15.2 | 13.4 -> **15.2** |
| child frac | 53.6 -> 49.5% | 54.5 -> **49.6%** |
| motherless | 6.1 -> 7.2% | 11.8 -> **7.9%** |
| CBR | 54.3 -> 48.9 | 52.3 -> 47.1 |
| CDR | 50.0 -> 44.5 | 73.6 -> 68.7 |

**26-40% of the gap to the anchors closed**, and regulation MOVED from deaths to births: population CV over
400 yr **7.9% -> 1.9%**. Births fall, deaths fall to match - the stationary identity working as predicted.

**WHAT IT DID NOT BUY, and why.** No cycles. A working negative feedback with a **1.4-yr half-life is
effectively instantaneous** on demographic timescales, so it DAMPS deviations (hence the CV collapse) rather
than overshooting them. Standard population dynamics: instantaneous density-dependence => stable equilibrium;
**DELAYED** density-dependence => oscillation. **Every feedback in this model is fast.** That is a sharper
statement of R-97's negative: cycles need a SLOW variable, not merely an elite layer.

**A DENSITY TEST THAT COULD NOT WORK, recorded so it is not repeated.** Comparing n=3000 vs n=15000 for a
density response is void: both converge to the SAME equilibrium (~4.7-4.9k), so starting density washes out and
there is no contrast to measure. Population must be the VARYING quantity (within-run), not a starting condition.

**NEXT (agreed order):** (1) count DEPENDENTS in the requirement - a mother provisioning 3 children needs 2-3x
her own maintenance, which is the anchored driver of forager birth spacing (Blurton Jones, Hadza) and should
close more of the gap without tuning; (2) find a SLOW variable for lagged feedback (soil degradation under
settlement; accumulated structural load) - the cycles question, now well-posed; (3) the clumping.

**ADDENDUM (same day) — step (1) is BLOCKED, and the blocker is a bigger finding than the feature.**
`enable_dependent_load` was built as planned: a mother's requirement widens by her juveniles' UNMET need, so a
child who increasingly feeds itself costs her less with no explicit weaning schedule. It is **wired correctly
and finds nothing**, because there are no dependents to find:

| measured (village/elite preset, 300 steps) | value |
|---|---|
| life-history active | **yes** (`eta_min` 0.2, `cons_min` 0.3, auto-built) |
| juveniles with a living mother-link | 91% |
| juvenile `eta` (production) | median **0.529** |
| juvenile `consumption_factor` (need) | median **0.588** |
| juvenile deficit | median **−1.24 burn units** |
| juveniles running ANY deficit | **1.0%** |

**Children in this model are net food PRODUCERS**, clearing roughly 1.5× their own requirement. This
contradicts **Kaplan 2000** — the net child deficit cited in `consumption_factor()`'s own docstring, and the
anchor beneath human life-history theory (the long juvenile period, provisioning, grandmothering all exist
*because* children run a deficit until ~18–20 yr). It is the same root cause as the fertility brake: at ~1.7×
surplus intake **everyone** over-produces, including seven-year-olds.

**Consequence:** the mechanism stays default-OFF and bit-exact, with the materiality test marked `xfail(strict)`
so it TRIPS the moment children become dependent. **Unblock by recalibrating the juvenile `eta` ramp against
Kaplan's production/consumption curves — not by tuning the load.** The current ramp is linear from `eta_min`
over 0→180 months, giving a 7.5-yr-old eta ≈ 0.5, where Kaplan's foragers produce a small fraction of what
they eat at that age. This also plausibly bears on the age structure directly: children who feed themselves
neither die as dependents nor constrain their mothers.

**ADDENDUM 2 — the Kaplan recalibration: mechanism FIXED, demography barely moves (2026-07-30).**
The blocker above was diagnosed as the juvenile production ramp. It is LINEAR (η 0.2→1.0 over 0→180 months)
against a linear consumption ramp (0.3→1.0), so η/c runs **0.67→1.0** — a *relative* deficit at every juvenile
age, exactly as `consumption_factor()`'s docstring claims. But an ABSOLUTE deficit needs η/c < **0.588** at
~1.7× cell shares, so the ratio never gets there. Kaplan's curves are **convex** (production near zero to ~10 yr,
then steep); the model's are straight lines. Added `LifeHistoryConfig.eta_juvenile_exponent` (1.0 = the original
linear ramp, **bit-exact default**), mirrored in the vectorised `soa_tier1.eta`.

| arm (coastal/temperate, 1200 steps, brake ON) | pop | e₀ | deaths <5yr | med age | child | mless |
|---|---|---|---|---|---|---|
| linear (baseline) | 4688 | 20.5 | 27.8% | 15.2 | 49.5% | 7.2% |
| convex exp=2 | 4779 | 19.3 | — | 14.6 | 51.0% | 6.1% |
| convex exp=3 | 4326 | 19.0 | — | 14.6 | 50.9% | 7.0% |
| convex exp=3 + dependent load | 4375 | 19.6 | 30.6% | **15.7** | **48.1%** | 7.0% |
| + `provision_self_keep` 0.7 | 4038 | 20.3 | 28.7% | **15.7** | 48.6% | 8.0% |
| + `provision_self_keep` 0.5 | 4804 | **21.0** | **27.6%** | 15.3 | 49.1% | **6.0%** |

1. **Convexity DOES create dependency** — juveniles running a deficit rise **10% → 35%** as η@7.5yr falls
   0.60 → 0.30. The Kaplan net-consumer anchor is met, and `enable_dependent_load` UNBLOCKS and works.
2. **But it first made things worse** (e₀ 20.5 → 19.0): children who cannot feed themselves simply died. The
   cause is that `enable_provisioning` was already ON with its load-bearing half OFF — `provision_self_keep`
   defaults to **1.0**, so a mother gives only overflow she would have wasted and never draws on her own
   reserve. **Provisioning was "on but dead" for the SAME root reason as everything else in R-106: no child
   ever ran a deficit to provision.** Restoring tier 2 recovers e₀ 19.6 → 21.0 and under-5 deaths 30.6 → 27.6%.
3. **Net against the linear baseline: e₀ +0.5 yr, motherless −1.2 pts, median age +0.1.** Mechanically the
   model is now correct — real dependants, live provisioning, working dependent load — but **the remaining gap
   to the anchors is NOT explained by juvenile production.** It is still the abundance/regulation problem.

**NOT ADOPTED AS DEFAULTS.** `eta_juvenile_exponent` stays 1.0 and `provision_self_keep` stays 1.0. The
exponent has a SHAPE anchor (Kaplan convexity) but no published value, and 0.5 for self-keep is a swept
number with no anchor at all — adopting either on the strength of a sweep would be fitting to our own artefact,
particularly since the deficit threshold (0.588) is itself set by the ~1.7× surplus that is the defect.
**Revisit once the abundance is fixed**, when the required curvature can be derived rather than swept.

**ADDENDUM 3 — METHODOLOGY CORRECTION: the "world is 99% empty" figure compared occupancy against an
UNREACHABLE denominator (2026-07-30, caught by supervisor question).** Every diagnostic in this entry that
measured world-scale land use (`diag_field.py`, the S~n^γ fit, the Malthusian positive control) built its
world through `battery1_liveness._build()` — a helper designed for FAST, BOUNDED liveness/ablation tests, not
world-scale questions. It passes `patch=24` into `NPPCapacityField`, which **zeroes harvest capacity outside a
576-cell (24×24) window** (`capacity.py`: `E[~mask] = 0.0`). But `_forage_cap_field()`, used to compute "94.1%
of cells habitable," reads `self._fields.forage_kcal` — the **raw, unpatched** terrain field for the full
10,000-cell grid, a **different object** than `self._harvest_field`. So "88 occupied cells" was divided by a
10,000-cell count that included ~9,000 cells the harness had already made unreachable. **Corrected: within the
576 cells actually reachable, occupancy was 88/576 = 15.3%,** not 88/10,000 = 0.9%.

**Re-run on the TRUE unconfined grid (`patch=None`, all ~9,600 habitable cells genuinely reachable), testing
the supervisor's proposed fix directly — seed agents spread across the whole map instead of clustered:**

| seeding | pop | occupied cells | % of 9604 habitable | mean occ/cell |
|---|---|---|---|---|
| clustered (old patch window) | 3189 | 335 | 3.5% | 9.5 |
| **spread across the full grid** | **6299** | **230** | **2.4%** | **27.4** |

**Spreading the seed made concentration WORSE, not better** — fewer cells used, ~3× the density per cell, and
a larger total population. This DISPROVES "just seed them further apart" as a fix and rules out plain seed-
position artefact as the driver. Wherever agents start, the dynamics pull them back into a small number of
dense cells — which points at the mechanism ITSELF (the crowding/agglomeration bonus, or band cohesion
resisting split) outweighing whatever pull the empty richer-per-capita land should exert, rather than at
movement range or initial placement.

**What this does and does not overturn.** The core R-106 chain is unaffected — intake/burn ratios, the S~n^γ
elasticity fit, and the cycle positive control all compare cells or years AGAINST EACH OTHER within the same
world, so they do not depend on the 10,000-cell denominator. What changes is the FRAMING of "obstacle 2": the
unused-land fraction is a real and now CONFIRMED-NOT-A-SEED-ARTEFACT phenomenon, but its magnitude was
overstated (≥85% of reachable land unused, not ~99% of the world), and the mechanism is now narrowed to
agglomeration/cohesion rather than left as an open field-vs-terrain question.

**STANDING WARNING for future diagnostics:** `battery1_liveness._build()` defaults to a small `patch` window
built for cheap ablation checks. **Do not reuse it for any question about world-scale land use, dispersal, or
carrying capacity without passing `patch=None`** and checking what `NPPCapacityField.patch` actually masks.

**NEXT to finish diagnosing this:** compare, per agent, food where they stand against the best EMPTY reachable
cell, and measure actual movement distances — to isolate whether the pull is the agglomeration bonus
specifically or band-cohesion resistance to fissioning, before proposing a fix.

**ADDENDUM 4 — the crowding pull IS the agglomeration bonus, not band cohesion; and it is compounded by a
second, independent search-horizon defect (2026-07-30).** Ran the comparison Addendum 3 called for, on the
TRUE unconfined world (`patch=None`, per the STANDING WARNING above): monkeypatched the live
`diffusion_select_target` with a read-only replica that logs its full per-candidate breakdown (no RNG draws,
so the model's dynamics and determinism are untouched), plus a whole-world scan for the best EMPTY habitable
cell, at two regimes — early growth (step ~50-60, mean **5** occupants/cell) and true equilibrium (step
700-900, mean **32-47** occupants/cell, population 5,030 → 6,511).

1. **SEARCH HORIZON (structural, independent of any bonus).** `mobility_radius()` scales the movement stride
   with the standing cell's RAW local NPP, not the agent's REALIZED per-capita share — so a cell packed with
   40+ people still reads as "rich" and the radius never expands past the `enable_productivity_mobility`
   floor. Measured: **`r_used == 1` in 143/143 (100%) of equilibrium decisions.** The world's actual best
   empty cell sits a mean **33.6 cells away** and was inside an agent's evaluated candidate set **0/143 times
   (0%)**. No mechanism downstream of perception can fix this — the opportunity is invisible, full stop.
2. **LOCAL RETENTION (the agglomeration bonus, not cohesion).** Even when a genuinely empty cell sits directly
   adjacent — true in 75.5% of equilibrium decisions — it still loses to staying crowded in 67.6% of those.
   Decomposed by term (mean advantage of the crowded HERE cell over the losing empty candidate):

   | term | early growth (n≈5) | equilibrium (n≈32) |
   |---|---|---|
   | raw per-capita split (pre-bonus) | +5,818 | **−35,810** |
   | **agglomeration bonus** (`aggl_beta`, point mode) | **+103,375** | **+387,290** |
   | band cohesion | +3,977 | +383 |
   | site appraisal | +723 | +779 |

   At equilibrium the raw food math already FAVORS the empty cell (crowding dilutes the split more than the
   empty cell's lower absolute yield costs) — the agglomeration term alone overturns that by >10x and is
   effectively the entire reason agents stay. **Band cohesion is not a meaningful lever here**: at equilibrium
   its contribution is ~0.1% the size of the agglomeration term, well within noise of the other minor terms.

**What this resolves.** Addendum 3 narrowed the mechanism to "agglomeration/cohesion or band-cohesion
resistance to fissioning" and left it open. This closes it: **the fix, if pursued, targets the agglomeration
bonus's functional form** (currently point-mode `S ~ n^β`, β=1.15, unbounded in local occupancy n) — band
cohesion and fission thresholds were not implicated and are not where the leverage is. The search-horizon
defect is separate and additive: a corrected agglomeration term alone cannot make agents discover land 30+
cells away; `mobility_radius` reading raw NPP instead of realized crowding needs its own fix.

**NOT YET ACTED ON.** This is measurement only — no code changed, no default flipped. Two candidate next
moves identified, neither started: (a) bound/reshape the point-mode agglomeration bonus so it saturates
instead of rewarding co-location indefinitely; (b) make `mobility_radius` respond to local occupancy pressure
(e.g. per-capita share vs. requirement) rather than raw cell NPP. Which to do first, and how, is undecided.

**Origin:** diagnostic-only, `diag_crowding.py` (scratchpad; monkeypatches
`sic_games.phase1_model.diffusion_select_target` with a read-only instrumented replica of
`substrate.diffusion_select_target`, built on the corrected `patch=None` world construction from Addendum 3).
No source files changed, no tests added. Raw per-decision log: `diag_crowding_log.json` (scratchpad).

**Origin (R-106 core):** `sic_games/src/sic_games/{demography,phase1_model,config,soa_tier1}.py`,
`agents/base.py`, `tests/test_intake_fertility.py` (11 tests);
diagnostics in scratchpad (`diag_mortality/brake/condition/surplus/malthus/returns/cycles`, `eval_brake`,
`eval_feedback`). Branches `diag/intake-instrumentation` (305b2ba, 8c921c9 - diagnostic-only) and
`demog/intake-fertility-brake` (f2e839e…b15017e). Suite 1,024 passed / 2 xfailed (one strict, intentional).
Default OFF, bit-exact when off.

**ADDENDUM 5 — village budding (Bandy 2004) exists, was off in every measurement to date, and measurably
changes the picture; `bud_events` was silently blind to it; and dispersed pre-settlement newborns range much
closer to the ethnographic envelope than settled agents do (2026-07-30).**

**1. A directed relocation mechanism already exists and was never engaged.** `_maintain_village_budding`
(`phase1_model.py:4103`), grounded in Bandy 2004/Chagnon 1975: a village past `village_fission_threshold`
(170) sheds its rival kinship faction, searches up to `village_bud_search_radius` (8 cells, "~a day's
relocation range") for the nearest open storable site, and **teleports** the faction there (`a.pos = best`) —
a real "go find a new place" behaviour, categorically different from the ordinary band split
(`_maintain_bands`, size 45), which is a pure in-place relabel that moves nobody. `enable_village_budding`
defaults **OFF** and was OFF in the entire R-106 chain and in Addendum 4's crowding diagnostic — every
measurement of "the world is mostly empty" to date was made with this mechanism dormant.

**2. Ablation (same seed/preset/world otherwise, N=3000, 900 steps, `patch=None`):**

| | budding OFF (R-106 preset) | budding ON |
|---|---|---|
| population (step 900) | 6,511 | **7,836** (+20%) |
| occupied cells | 277 / 9,449 (2.93%) | 382 / 9,449 (4.04%) |
| settlements (villages) | 81 | **319** (+294%) |
| mean village size | 607.8 | 291.8 |
| `bud_events` (relocations) | 0 | **733** |

Budding quadruples the number of villages and lifts population ~20% (plausibly less local-crowding mortality
when spread across more, smaller settlements — not independently isolated here), but only modestly expands the
footprint (2.9% → 4.0%). **Why it can't do more:** its own search radius (8 cells) is itself far short of the
~34-cell average distance to the world's best truly unclaimed land (Addendum 4). It relieves local crowding by
founding nearby daughter villages, not by reaching the rich, empty far side of the map.

**3. `bud_events` was silently blind to the path actually used.** The counter only incremented inside the
`enable_bud_hazard` branch (unused here); the legacy threshold path — the one `enable_village_budding=True`
alone exercises — relocated factions without ever counting them, so the counter read 0 in the table above
before the fix even though 733 relocations demonstrably occurred (inferred from the settlement-count/population
divergence, since the mechanism is deterministic and RNG-neutral when truly inert — confirmed directly once
fixed). **FIXED:** moved the increment to the shared relocation code so both paths count
(`phase1_model.py`, `_maintain_village_budding`). Full suite re-run clean: 1,024 passed / 2 xfailed, no
regressions.

**4. An instrument flaw in the diagnostics themselves, caught and fixed before trusting the numbers.** The
travel-distance tracking scripts (this addendum and Addendum 4's would-be follow-up) originally keyed tracked
agents by Python `id()`. CPython recycles a garbage-collected object's `id()`, so a tracked agent's death
followed by an unrelated birth landing at the same address would silently splice two different agents'
histories together — exactly the kind of instrument bug [[feedback_validate_the_instrument]] warns about.
Switched to the model's own stable `unique_id`. Re-running the travel-distance measurement below with the
fix produced **identical numbers to the unfixed version** — the flaw didn't happen to bite this particular
run — but it was a real risk, not a hypothetical one, and the fix is now in place for future use.

**5. Post-settlement residual travel** (300 agents sampled live at step 700, tracked to step 900 = 200
steps/16.7 yr; `unique_id`-based): baseline mean cumulative path 34.1 cells (~341 km, ~20 km/yr) but mean *net*
displacement only 3.2 cells — once settled, agents shuffle locally and go nowhere. Budding ON: even less
churn (mean 8.4 cells / ~84 km, ~5 km/yr) — smaller villages apparently have less internal crowding pressure
to escape. Both are far below the Binford/Kelly ethnographic ~150-175 km/yr total annual travel (external
literature search, not yet filed in LITERATURE.md) — consistent with the project's own R-8 finding
(0.93 moves/yr vs Binford's ~10-40/yr envelope) that the model is under-mobile independent of anything else
in this investigation.

**6. Pre-settlement travel — the real answer to "how far do dispersed bands travel before settling."**
Tracked newborns from birth (steps 100-700 warmup+run), but only those born OUTSIDE any settlement's
`settle_radius` (i.e. genuinely dispersed at birth — most are not: 77-80% of all newborns are already born to
an already-settled mother and never face this question):

| (of 300 dispersed-at-birth newborns tracked) | budding OFF | budding ON |
|---|---|---|
| eventually settled | 144 (48.0%) | 161 (53.7%) |
| died before ever settling | 123 (41.0%) | 116 (38.7%) |
| still unsettled at run end | 33 (11.0%) | 23 (7.7%) |
| *of those that settled:* time from birth to settling | mean 159 mo (~13.3 yr) | mean 180.5 mo (~15 yr) |
| *of those that settled:* cumulative path traveled | mean 130.2 cells (~1,302 km) | mean 147.9 cells (~1,479 km) |
| *of those that settled:* net displacement, birth→settling | mean 10.0 cells (~100 km) | mean 8.6 cells (~86 km) |

**This is the real mobility signal, and it's much closer to the ethnographic envelope than #5 above:** ~1,300
km over ~13 years ≈ **~98 km/yr** while dispersed — not the ~20 km/yr of post-settlement churn. The model
isn't uniformly under-mobile; it's specifically *settled* agents who go nearly stationary (matching real
ethnography reasonably well — people who've found their village mostly stop wandering), while *dispersed*
agents genuinely range, just via an undirected, backtracking radius-1 random walk (net displacement is only
~8% of cumulative path) rather than anything resembling directed exploration.

**A new, unflagged connection to the R-106 demography gap:** 39-41% of dispersed newborns **die before ever
settling** — a large, previously unmeasured mortality channel tied specifically to dispersal status, not
age/orphaning/starvation-multiplier as measured so far. Whether this is a meaningful piece of the e0 gap
(~21 vs anchor ~28) is untested — flagged, not chased, this session.

**NOT YET ACTED ON.** No default changed. `enable_village_budding` remains OFF; whether to adopt it, and
whether to also address the search-horizon/agglomeration findings from Addendum 4, is undecided.

**Origin:** diagnostic-only additions this session — `diag_bands_travel.py`, `diag_birth_cohort.py`
(scratchpad, both reused the Addendum 3/4 `patch=None` world construction). One source fix:
`phase1_model.py::_maintain_village_budding` (`bud_events` counter, ~2 lines). No new tests added; existing
suite re-verified green (1,024 passed / 2 xfailed) from the repo root after the fix.

**ADDENDUM 6 — pressure-aware mobility BUILT and tested; calibration MISSES the Binford/Kelly moves/yr target
honestly; combined with budding it breaks the historical population ceiling (unvalidated); the cycle test is
INCONCLUSIVE, not negative, because the world never reached stationarity (2026-07-31, overnight session).**

**1. The mechanism, as scoped in conversation.** `mobility_radius()`'s NPP-driven stride (§4.8.19) is
static/geographic — a cell packed with 40+ occupants still reads as "rich," so it never expands (Addendum 4:
`r_used==1` in 100% of equilibrium decisions). New `mobility_pressure_source: Literal["npp","intake"]="npp"`
(pure additive mode, `"npp"` is bit-exact with the original). `source="intake"` drives the SAME formula off the
agent's own `_intake_ema` (R-106's live intake/requirement EMA) instead of raw NPP — density-aware by
construction, and reusing an existing signal rather than adding a new one. `_intake_ema`'s update loop is now
gated by `intake_fert_on OR mobility_wants_intake` (`phase1_model.py`) so the two mechanisms share the
computation while staying independently ablatable (flip either flag alone; verified by test). New fields
`mobility_intake_ref` (default 1.00, reuses the already-anchored `intake_fert_lo` maintenance threshold — not
a new number) and `mobility_intake_floor` (0.15, a pure numerical clamp, same role as `mobility_npp_floor`).
14 new tests (`tests/test_pressure_mobility.py`): shape parity with the NPP-mode tests, bit-exactness when off
or at the default source, and the EMA-liveness/independent-ablatability guarantees. Full suite: 1,038 passed
(1,024 + 14) / 2 xfailed, no regressions.

**2. Calibration sweep 1 (exponent, ref fixed at 1.0) — a mathematically GUARANTEED null, confirmed
empirically.** N=3000, 900 steps, `patch=None`, budding ON, exponent ∈ {0.5,1.0,1.5,2.0,3.0}: moves/yr never
exceeds 1.62, km/yr never exceeds 20 — no trend. This is not noise: when `intake_ema >= ref`, `ratio<=1` for
any exponent ≥0, and `max(base,...)` floors the radius back to `base` regardless of the exponent's value. Since
R-106/Addendum 4 already established crowded occupants average 2.1x subsistence, most of the tracked population
sits above `ref=1.0` most of the time, so the exponent literally cannot matter there. **The real lever is the
threshold, not the response steepness** — diagnosed from the formula's structure before spending the full sweep
budget confirming it.

**3. Calibration sweep 2 (ref, exponent fixed at 1.5) — an honest MISS against the target.** ref ∈
{1.0,1.2,1.5,1.7,2.0,2.5}: best result **ref=1.7 → moves/yr=1.45, km/yr=18.5** — roughly **7-27x short** of the
Binford/Kelly band (10-40 moves/yr, 150-175 km/yr), and the sweep is noisy/non-monotonic across both dimensions
(0.79-1.62 moves/yr, no clean curve), not a smooth calibration surface with an obvious better setting further
out.

| ref | pop | moves/yr | km/yr | occ% | settlements | bud_events |
|---|---|---|---|---|---|---|
| 1.00 | 7051 | 1.10 | 12.5 | 3.80% | 269 | 480 |
| 1.20 | 7385 | 1.06 | 13.0 | 3.45% | 292 | 527 |
| 1.50 | 7519 | 0.79 | 11.0 | 4.13% | 386 | 1043 |
| **1.70** | 7273 | **1.45** | **18.5** | 3.73% | 247 | 312 |
| 2.00 | 6951 | 1.19 | 14.7 | 4.18% | 213 | 315 |
| 2.50 | 7482 | 0.81 | 12.4 | 3.06% | 170 | 123 |

**Why, diagnosed rather than shrugged off:** the mechanism correctly targets the food-STRESSED minority (real
forager logic — you don't relocate camp because you're comfortable), but Binford/Kelly's ~10-40 moves/yr is a
POPULATION-WIDE ethnographic average that includes plenty of well-fed foragers moving for reasons this
mechanism was never built to capture (seasonal rounds, social visiting, camp rotation independent of current
hunger). Addendum 4's own finding applies again here: "the average agent never experiences scarcity" — so an
average taken across the whole tracked population is diluted by the majority who are fine. **Not pursued
further tonight:** pushing `ref` past 2.5 to force more of the population below threshold would fit the
benchmark by construction, exactly the kind of ad hoc tuning the project rejects (cf. Addendum 2's refusal to
adopt an unanchored `provision_self_keep`=0.5). Closing this gap for real needs either a second, non-hunger
mobility driver, or accepting the ethnographic moves/yr figure doesn't transfer cleanly onto this specific
mechanism's scope. **`ref=1.7` carried forward as the best-available setting, not a validated calibration.**

**4. The unplanned, MUCH bigger result: combined with budding, the historical population ceiling breaks —
unvalidated.** Full run: N=3000, ref=1.7, exponent=1.5, budding ON, 1500 steps (125 yr):

| | Addendum 5 baseline (900 steps) | this run (1500 steps) |
|---|---|---|
| population | 6,511 (budding off) / 7,836 (budding only) | **15,947** |
| occupied cells | 277/9449 (2.93%) / 382/9449 (4.04%) | **848/9449 (8.97%)** |
| settlements | 81 / 319 | **809** |
| moves/yr | — | 0.47 (LOWER, see below) |

Every prior R-106 measurement found population converging to the SAME ~4.7-4.9k equilibrium regardless of
starting size (Addendum to R-106 core: "starting density washes out"). Here, at step 1500, population is
**3x that historical ceiling and still accelerating** — growth increments per 200 steps (467→977→1750→2396→
2711→3111) are still rising, though their SECOND difference is shrinking (+510,+773,+646,+315,+400,+107),
consistent with early-stage logistic growth approaching, not yet at, an inflection — not confirmed. Occupied
land nearly TRIPLED and settlement count went **10x**. **This is flagged as a major but UNVALIDATED finding**:
it could be a genuine unlock of previously-inaccessible carrying capacity (more land finally reachable via
budding's 8-cell site search + the intake-driven radius bump), or it could indicate `enable_village_budding`'s
relocation is now firing too permissively once combined with a second mobility mechanism — no time tonight to
check this population against an independent density/carrying-capacity anchor. **Do not adopt either mechanism
as a default on the strength of this run alone.**

**Moves/yr going DOWN (1.45→0.47) despite MORE spreading is not a contradiction**, it's the mechanism working
as intended interacting with the averaging methodology: budding minted 809 settlements by step 1500 (vs 247 at
900 steps in the sweep), so a much larger share of the tracked population is freshly settled at any snapshot —
and post-settlement agents barely move (Addendum 5). Success at settling more people mechanically lowers the
population-wide average mobility, the same dilution effect noted in §3.

**5. The Malthusian-cycle stretch goal: INCONCLUSIVE, not negative — the world never reached stationarity.**
Ran `probe_hcycles.period_of` (the canonical, validated instrument — R-97's own detector, not an ad-hoc
periodogram) on population, occupied-cell-count, and mean-per-capita-wealth series (sampled every 4 steps,
matching R-87/R-97 convention) over the full 1500-step run. **All three: `ac_peak=0.000`, no period found** —
the autocorrelation never even crosses negative, which `period_of` reports specifically when a series is
monotonically drifting rather than oscillating. **This is not a valid cycle test.** With population still
accelerating at step 1500 (see §4), the world hasn't reached anything resembling stationarity — R-87/R-97's own
cycle tests were run on populations that had already stabilized or were fluctuating around a mean, not ones in
unresolved exponential-ish growth. Testing for oscillation before there's an equilibrium to oscillate around is
a category error, not a finding. **Consistent with, and does not update, R-97's standing diagnosis** that a
delayed feedback needs to out-govern the substrate's own churn timescale — and today's budding-driven explosion
in settlement count (81→809) plausibly SHORTENS that churn timescale further, working against rather than
toward the cycle goal, if anything.

**NOT YET ACTED ON.** `enable_village_budding` and `mobility_pressure_source="intake"` both remain OFF as
defaults. Nothing here should be adopted without: (a) validating the step-1500 population against an
independent carrying-capacity anchor, (b) a much longer run (several thousand steps) to see whether growth
ever plateaus, and (c) a decision on the calibration miss in §3 (accept it, find a second mobility driver, or
re-scope the target).

**Origin:** `sic_games/src/sic_games/demography.py` (`mobility_pressure_source`, `mobility_intake_ref`,
`mobility_intake_floor` fields; `mobility_radius()` signature `local_npp`→`value`, source-dispatch),  
`sic_games/src/sic_games/phase1_model.py` (`mobility_source` at the movement call site; `intake_signal_on`
gating). New: `sic_games/tests/test_pressure_mobility.py` (14 tests). Diagnostics in scratchpad:
`diag_calibrate_mobility.py` (exponent + ref sweeps), `diag_final_combined.py` (long-run validation + cycle
test, reuses `probe_hcycles.period_of`). Suite 1,038 passed / 2 xfailed. Both new knobs default OFF/`"npp"`,
bit-exact when off.

**ADDENDUM 7 — CORRECTION to Addendum 6 §3: the mobility "7-27x miss" was mostly a HIDDEN-DENOMINATOR error.
The model's MOBILE foragers move at 8.4 moves/yr against a hard structural ceiling of 12. The real defects are
a stride collapse, a residence pin that bypasses the mover entirely, and a saturated-but-BLOCKED push
(2026-07-31).**

**What prompted it.** Two of this session's own measurements contradicted each other and I had not reconciled
them: `diag_crowding.py` found **75% of agents MOVED per decision** at equilibrium (~9/yr if that were
population-wide), while `diag_calibrate_mobility.py` reported **0.47-1.45 moves/yr**. Both were correct
measurements *of different populations*.

**The mechanism.** `phase1_model.py:1435` pins any agent within `settle_radius` of an active settlement:
`_toward(pos, site)` returns `pos` unchanged once the agent stands ON the site (line 754), and the movement
loop `continue`s **before `diffusion_select_target` is ever called**. A settled agent on its site is therefore
structurally FROZEN — zero moves, permanently, independent of hunger, depletion, or any mobility knob. The
crowding wrapper only ever observed the *unsettled remainder*; the calibration averaged that remainder together
with a pinned majority.

**Measured (N=2000, 700 steps, 120-step window, `patch=None`, budding ON, mobility-intake ON, ref=1.7;
per-agent per-step state attribution so each transition is credited to the state it began in):**

| | moves/yr | km/yr |
|---|---|---|
| POPULATION-WIDE (what Addendum 6 §3 reported) | 1.76 | 19.6 |
| **MOBILE steps — Binford's own denominator** | **8.39** | **86.3** |
| settled steps | 0.74 | — |
| of which fully pinned ON-SITE | 0.47 | — |

agent-steps: 245,378 total; **212,782 settled (86.7%)**, of which **207,511 (84.6%) fully on-site**; 32,596
mobile (13.3%). Per-agent settled fraction: mean 0.867, **median 1.000**; 1,714/2,062 agents *always* settled,
240/2,062 *never*.

**1. The denominator was wrong, and the benchmark's own scope says so.** Binford's mobility dataset covers
"all groups that move at least once per year" (n=314) — MOBILE foragers by construction; sedentary groups are
excluded from his denominator. Averaging our ~87% pinned villagers into that comparison is the
**HIDDEN-DENOMINATOR bug class already on this project's record** (R-97 et al.: any ratio compared against a
benchmark has a validity domain and fails silently when the denominator drifts). Corrected, the model's mobile
foragers sit at **8.39 moves/yr vs a reachable band of 10-12** — near-validation, not a 7-27x failure.

**2. A STRUCTURAL CEILING nobody had stated: 12 moves/yr, by construction.** Diffusion movement resolves once
per model step and 1 step = 1 month, so no configuration can exceed 12 residential moves/yr. (Village budding
can add rare extra relocations, so 12 is an approximate rather than strict bound.) **Binford's upper range —
40/yr, i.e. relocating every ~9 days — is unreachable without a sub-monthly timestep.** Every prior framing of
this benchmark, including R-8's original "0.93 vs ~10-40/yr" and Addendum 5's, compared against a band whose
top ~70% the architecture cannot reach. The honest target is **10-12**.

**3. The real remaining gap is DISTANCE, and it appears only as the world fills.** Mobile agents average
86.3 km/yr = **10.3 km per move ≈ 1.03 cells** — the `r>1` glide is not firing, exactly matching Addendum 4's
`r_used==1` in 100% of equilibrium decisions. But in an early, uncrowded world (N=400, 80 steps, zero
settlements formed) the same configuration gives **9.16 moves/yr and 179.8 km/yr — at the Kelly anchor**, with
~2 cells per move. **Stride collapses as the world fills.** That is the tractable mechanism defect, and the
intake-pressure mode of Addendum 6 does not fix it because the agents who would need a long stride are not
hungry enough to trigger one.

**4. The PUSH driver is NOT missing — it saturates where it matters and is BLOCKED from acting.** Depletion has
a deterministic equilibrium `B* = 1 − 0.5·(occ/K)` (`capacity.py`, `DEPLETE_FRAC=0.5`), so measured B pins
occupancy exactly. Occupied cells (n=218): mean B 0.905, **median 0.974**, p10 0.723, **min 0.05 (the
`B_FLOOR`)**; unoccupied 0.999; 8/218 below B=0.5.
- median B 0.974 ⇒ pressure ≈ 0.052 ⇒ **~1.3 agents on a cell of K≈25** — most "occupied" cells hold a single
  forager on pristine land;
- B at the 0.05 floor ⇒ pressure ≥ 1.9 ⇒ those cells are **hunted out at ≥1.9x carrying capacity**.

So the landscape is bimodal, precisely as Addendum 4's concentration finding predicts. **Patch depletion — the
ethnographic prime mover of forager residential mobility (MVT) — is present and firing hard in exactly the
cells that are overcrowded.** Its output simply cannot reach the movement decision: those agents are either
settlement-pinned (never call the scorer) or held by the agglomeration bonus (Addendum 4: +387,290 vs a
−35,810 raw-food disadvantage). **The failure is a disconnected response, not an absent stimulus.**

**5. Carrying capacity is NOT inflated** (checked because a mis-scaled K would have made depletion dormant by
construction): land-cell `K_persons` median **24.7/cell = 0.247 persons/km²**, p10 7.1, p90 51.5, max 116.9 —
inside the Tallavaara ethnographic band (0.1-0.5/km²), with 80.1% of land above Binford packing (0.091/km²) as
the aquatic-subsidy design intends. My first estimate of "K≈236/cell" was inferred from B and was wrong;
measured directly, K is sound.

**WHAT IS GENUINELY MISSING (drivers, as opposed to the blockers above) — all already documented as deferred
seams in this project's own spec, none of them the binding constraint:**
- **Seasonal transhumance.** §4.8.19 (MODEL_SPEC line 1706) states the stride reads STATIC `npp_gm2` by design
  "so the *range* doesn't oscillate with the season; transhumance is a deferred extension."
- **Game/herd-following.** §4.1.8 wires `game_mobility` as a parameter with the **MECHANIC DEFERRED**
  (`GRASS/steppe 1.0` = Nunamiut caribou / plains bison logistical herd-following).
- **Logistical (collector) mobility.** The model has residential moves only; Binford's forager↔collector
  continuum has collectors *reducing* residential moves while running long logistical forays.
- **Social/scheduling relocation** (death in camp, disputes, vermin/sanitation) — routine relocation triggers
  in the ethnography (e.g. Amazonian villages relocating every few years), with no analogue in the model.

**Adding any of these on top of a blocked response would produce motion without meaning.** Order of work
implied: (a) report mobility conditioned on mobile state — free, and turns a reported failure into a
near-validation; (b) test whether the **86.7% sedentary fraction** is itself the defect — plausible for
coastal/temperate (NW-Coast storage foragers really were largely sedentary) but this is exactly the
[[feedback_check_biome_dependence]] case: if flat_boreal / savanna / desert also come out ~87% sedentary, then
sedentism is biome-independent and THAT is the bug; (c) fix the equilibrium stride collapse; (d) only then
consider new drivers.

**INSTRUMENT NOTE.** The diagnostic's own per-agent settled-fraction line initially read
`sum(1 for (_, s, _) in h)` (missing the `if s`), reporting "always-settled 329/329" while the agent-step
counter directly beneath it read 0% settled. Caught because the two disagreed, fixed before any number here was
used — the same class of self-check that [[feedback_validate_the_instrument]] exists for.

**Origin:** diagnostic-only; `diag_mobility_denominator.py` (scratchpad) + a direct `K_persons` percentile
check. No source files changed by this addendum. Numbers above supersede Addendum 6 §3's population-wide
framing; Addendum 6's mechanism, tests and §4 population-ceiling finding are unaffected.

**ADDENDUM 8 — BIOME BATTERY: sedentism IS biome-dependent (the bug tested for is NOT present), but mobile
mobility is biome-INVARIANT — the model reproduces the ethnographic MAGNITUDE while failing to produce the
ethnographic LAW, and the monthly timestep makes that law unrepresentable through move frequency at all
(2026-07-31).**

**The test.** Addendum 7's 86.7%-sedentary baseline was measured on ONE world (coastal/temperate). Per
[[feedback_check_biome_dependence]] — a mechanism validated in one world is a claim about that world — six
biomes were run identically (N=1500, 600 steps, 120-step window, `patch=None`, plain village/elite preset:
budding OFF, mobility-intake OFF, so this is the CANONICAL stack, not Addendum 6's experimental one).
Prediction if sedentism were correctly biome-gated: coastal/temperate high (NW-Coast storage foragers),
flat/boreal low (Nunamiut caribou-followers), tropical/interior low-moderate.

| biome | pop | settled % | moves/yr (pop) | moves/yr (MOBILE) | km/yr (MOBILE) | settlements | mean NPP | med K/cell |
|---|---|---|---|---|---|---|---|---|
| mountainous/boreal | 223 | **66.3%** | 4.23 | 9.31 | 115.3 | 2 | **458** | **3.2** |
| coastal/temperate | 1584 | 64.1% | 3.31 | 8.63 | 92.2 | 30 | 1004 | 24.7 |
| flat/temperate | 695 | 48.5% | 5.15 | 9.41 | 101.1 | 8 | 1083 | 28.6 |
| hilly/temperate | 832 | 24.9% | 7.17 | 9.35 | 99.3 | 9 | 1002 | 21.4 |
| flat/tropical | 1472 | 0.9% | 9.16 | 9.22 | 110.2 | 1 | **2291** | 35.5 |
| flat/boreal | 3693 | **0.0%** | 9.74 | 9.74 | 106.7 | 0 | 795 | 11.4 |

**1. VERDICT ON THE TESTED HYPOTHESIS: NEGATIVE — sedentism is NOT biome-independent.** Spread **0.0% → 66.3%
(sd 27.4 pts)**, correlation with mean aquatic food **+0.616** (`AQUATIC_R_PER_YR=0.80` is `capacity.py`'s
documented "sedentism enabler"). So **Addendum 7's coastal baseline stands as a legitimately coastal-specific
result**, and its central claim survives: the mobility "miss" is a COMPOSITION artifact, not a broken mobility
mechanism. (The exact figure differs — 64.1% here vs 86.7% in Addendum 7 — because that run used
budding+mobility-intake at N=2000/700 steps; within-battery comparisons are apples-to-apples.)

**2. BUT THE GRADIENT'S ORDER IS PARTLY BACKWARDS.** `mountainous/boreal` — the POOREST world on every measure
(mean NPP 458, median K 3.2/cell, total K 74,697, all lowest by a wide margin) — is the **MOST sedentary
(66.3%)**. Kelly/Binford have mobility ∝ 1/productivity, so the most marginal environment should be the most
MOBILE. **Circumscription is ruled out as the explanation**: all six worlds have 9,449–9,994 habitable cells,
i.e. land is not scarce anywhere. The apparent mechanism is that poverty makes the few viable cells the ONLY
viable cells, population concentrates onto them, the settlement threshold is met, and the residence pin
(Addendum 7) then freezes everyone — **poverty producing nucleation instead of dispersal.** With pop 223 this
is also the noisiest cell in the battery; worth re-running at larger N before treating the inversion as firm.

**3. THE SHARPER FINDING — MOBILE MOBILITY IS BIOME-INVARIANT.** Across a **5x productivity range** (NPP
458→2291, median K 3.2→35.5), mobile-agent mobility is **flat: 8.63–9.74 moves/yr (12% spread) and 92–115
km/yr**. `enable_productivity_mobility` is ON in this preset and exists precisely to implement Kelly 1995 /
Binford 2001's ∝1/productivity law (§4.8.19) — **it produces no realized gradient whatsoever.** This is the
same defect Addendum 4 found from the other side (`r_used==1` in 100% of equilibrium decisions): the stride
never expands, so the biome gradient encoded in the stride formula never reaches behaviour. R-40 already
recorded this mechanism as "NOT the biome→society fix" and retained it for "its own uses (mobility
gradients)" — this measures that those uses are also not being served.

**So the model reproduces the ethnographic MAGNITUDE and fails to reproduce the ethnographic LAW.** ~9.3
moves/yr and ~100 km/yr sit close to the anchors (Binford 158 / Kelly 174 km/yr; reachable move band 10-12,
per Addendum 7's ceiling) — but the anchor is not only a number, it is a SLOPE, and we produce a flat line.

**4. THE CEILING MAKES THE LAW UNREPRESENTABLE THROUGH MOVE FREQUENCY.** Addendum 7 established a hard 12
moves/yr ceiling (one movement resolution per monthly step). Tropical foragers already sit at **9.22/yr = 77%
of that ceiling**. Kelly's law anchored there would put mountainous/boreal at ~46 moves/yr — nearly 4x above
what the architecture can express. **Even a perfectly working productivity-mobility mechanism could not fit the
ethnographic gradient into move COUNT.** The only channel with headroom is **distance per move (stride)**,
which is currently also flat (~10 km/move ≈ 1 cell everywhere, Addendum 7 §3). **Conclusion: the
productivity-mobility law must be delivered through stride, and stride is exactly the thing that is broken.**
That converges with Addendum 4's search-horizon finding and Addendum 7 §3's stride-collapse finding from a
third independent direction.

**5. AN INCIDENTAL, CONFOUNDED OBSERVATION (flagged, not established).** Population as a fraction of nominal
total K is 0.24–0.6% in every biome EXCEPT `flat/boreal` — the one world where **zero settlements formed** —
which reaches 2.6%, ~5x the others, and the largest absolute population (3,693) despite only the 4th-highest
total K. Consistent with R-106's chain (settlement/agglomeration concentrate people, and concentration kills),
but **confounded**: these are 600-step runs and not all arms are at equilibrium (some grew, some shrank), so
this is a hypothesis for a controlled test, not a result. Separately, every biome running at **<3% of nominal
carrying capacity** re-confirms R-106's "nobody can be hungry" root cause as biome-general rather than
coastal-specific.

**Origin:** diagnostic-only; `diag_biome_sedentism.py` + a direct per-biome land/NPP/K check (scratchpad). No
source files changed. Supersedes nothing; extends Addendum 7 §3's stride diagnosis with the biome-gradient
evidence and adds the dynamic-range argument.

**ADDENDUM 9 — TWO SUPERVISOR CHALLENGES ANSWERED: the biome stride is INERT BY CALIBRATION (not broken);
depletion is CORRECT TO SPEC and too gentle to evict anyone; and a genuine dimensional bug — the settlement
tier-2 food layer contributes 0.005% of cell food (2026-07-31).**

**Challenge (A): "the biome-adapted stride was lit-sourced and built — did it not happen? did it break?"**
It happened, it is ON, and it is not broken. `enable_productivity_mobility=True` in the canonical preset;
`mobility_radius` computes correctly. It is **inert by CALIBRATION**:
`r = clamp(round(base·(npp_ref/max(npp,floor))^exp), base, r_max)` with `npp_ref=900, exp=1.0, base=1` requires
`900/npp ≥ 1.5`, i.e. **npp ≤ 600 g/m²/yr, before r even reaches 2**. Measured on coastal/temperate:

| | value |
|---|---|
| land-cell NPP | mean 1004, median 1054 |
| NPP where agents actually are | mean **769** |
| fraction of LAND below the r≥2 threshold (600) | **3.2%** |
| fraction of AGENTS below it | **0.9%** |
| stride actually computed for agents | **r=1: 1570, r=2: 14 (99.1% at r=1)** |

`npp_ref=900` is documented as the Tallavaara forager-median NPP, but this project's canonical worlds average
**1004–2291** (only mountainous/boreal 458 and flat/boreal 795 sit below it), so the reference lands beneath
the landscape and the mechanism returns base almost everywhere. **The source itself flags
`ref/exp/max` as "PROVISIONAL — locking the scaling law for canonical runs needs supervisor sign-off"
(§4.8.19). That sign-off never happened, yet `emergent_village_demog()` turns the flag ON** — so it ships as
if adopted while being calibrated into inertness. This is the direct mechanical cause of Addendum 4's
`r_used==1` and Addendum 8's flat biome gradient.

**MY OWN HYPOTHESIS FALSIFIED (recorded per the R-106 house rule).** I proposed that agents *self-select into
high-NPP cells*, so a cell-keyed law would cancel itself. **Measured: agents sit at NPP 769 vs a landscape mean
of 1004 — 0.77x, i.e. POORER than average, the opposite of my prediction.** The self-selection story is dead;
the parameter-range story is the whole explanation. (The separate *scope* critique — that Kelly/Binford's law
is regional while the model applies it per-cell — remains untested and is now unsupported by any measurement.)

**Challenge (B): "populations survive and grow sourcing the same cell for a long time — the cell resource is
not depleting correctly."** The intuition is right about the OUTCOME and wrong about the CAUSE, and **my own
proposed cause was also wrong.**

**FALSIFIED (mine, from the same session):** I claimed the residence pin puts *every* villager on the single
site cell, so pressure lands on 1 cell while food is drawn from 9 — "a village hunts out its plaza while its
fields stay pristine." **Measured: catchment-ring occupancy is 148.8 vs 35.3 on the site cell.** Villagers are
spread across the catchment; foraging pressure does reach the ring. The story is dead.

**What is actually happening (30 settlements, coastal/temperate, 600 steps):**

| | site cell | catchment ring |
|---|---|---|
| stock fraction B | mean 0.805, median 0.789, **min 0.535** | mean 0.895, min 0.813 |
| occupancy | mean 35.3, max 85 | mean 148.8 total |
| K at the cell | **87.5 persons** | — |
| sites hunted below B=0.2 | **0/30** | — |

**Depletion is working exactly as specified.** The spec is `B* = 1 − DEPLETE_FRAC·(occ/K)` with
`DEPLETE_FRAC=0.5`; measured pressure is 35.3/87.5 = **0.403**, predicting B* = **0.799** against a **measured
0.805**. The model is not failing to run its own equation. Two structural facts explain why the resource never
runs out:
1. **The law caps drawdown at 50% by construction.** Even at FULL carrying capacity (occ = K) the stock only
   falls to B=0.5 — half the pristine yield. **A patch can never be hunted out at any realistic occupancy.**
   Real forager mobility is driven by returns falling far enough to beat the cost of moving (MVT); this law
   cannot produce that.
2. **Villages sit on the richest cells, whose assumed capacity is ~10x Binford packing.** Settlement sites have
   **K = 87.5 persons/cell = 0.875 persons/km²** (vs landscape median 0.247, Tallavaara band 0.1–0.5, Binford
   packing 0.091). That is the aquatic subsidy working as designed (`AQUATIC_DENSITY_MAX=80`, MODEL_SPEC:
   the super-density "that lets a concentrated band cross Binford packing") plus site-appraisal selecting the
   best cells. **So 35 people on a cell rated for 87 is a 40% load, and a 20% yield haircut is the *correct*
   answer to that load.** The village persists indefinitely because the model believes that cell can feed
   87 people.

**A GENUINE BUG FOUND — the settlement tier-2 food layer is dimensionally inert.**
`_settlement_catchment_yield = settle_tier2_yield · Σ_catchment S_pot`, where `S_pot = max(aquatic_food,
cultivability)` is a **normalized 0–1 static field** and `settle_tier2_yield = 40.0`. Measured at settlement
cells: **tier-2 = 2.68e2 kcal against tier-1 = 5.28e6 kcal — 0.0051%.** The entire Layer-2 "settlement unlocks
intensive food" mechanism — the thing that is supposed to make being a village pay — contributes five
thousandths of one percent of the cell's food. Villages in this configuration are fed **essentially entirely by
ordinary depletable tier-1 forage**. Whether `settle_tier2_yield=40` was calibrated against a differently
scaled tier-1 (the `burn=75000` normalisation sets tier-1's magnitude) is not established here; what is
measured is that in the CURRENT canonical configuration the layer does nothing. **This needs a unit audit
before any settlement/agriculture conclusion that assumed tier-2 was load-bearing is trusted.**

The R-63 ceiling (`_settlement_carrying_capacity`, the one path that *does* read the depletable field) **binds
in 8/28 = 28.6% of settlement cells** (S/cap mean 0.621, max 1.002), so depletion does throttle villages some
of the time — via the cap, not via the tier-2 term.

**NOTE ON A CONFIG DIFFERENCE.** Addendum 7 reported min occupied-cell B = 0.05 (the hunted-out floor); here no
settlement site falls below 0.535. Different configurations (Addendum 7: budding + mobility-intake ON,
N=2000/700 steps; here: plain canonical preset, N=1500/600) — the floor-hitting cells in Addendum 7 were not
necessarily settlement sites. Not reconciled; flagged.

**IMPLICATION FOR THE MOBILITY WORK.** Addendum 8 concluded the productivity gradient must be carried by
stride. Addendum 9 says the stride mechanism *already exists and is simply calibrated below its own operating
range* — so the first move is a **calibration decision on `npp_ref`/`exponent`/`r_max` against the Kelly/Binford
range data (the sign-off §4.8.19 has been waiting for), not new mechanism.** Separately, `DEPLETE_FRAC=0.5`
capping drawdown at 50% is the reason no amount of mobility tuning will produce eviction-driven movement.

**Origin:** diagnostic-only; `diag_depletion_catchment.py` (scratchpad), reading `_diag_pool`, `capacity._B`,
`_K_persons`, and the model's own `_settlement_catchment_yield`/`_settlement_carrying_capacity`. No source
files changed. Two of my own hypotheses falsified by this run and recorded above.

**ADDENDUM 10 — THE DENSITY MISS AND THE SPATIAL CONCENTRATION ARE ONE DEFECT; FOUR CANDIDATE CAUSES
FALSIFIED BY MEASUREMENT (three of them mine, two INVERTED); and the agglomeration term is structurally
entangled — it is the concentrator AND the food supply at once (2026-07-31).**

**How the question changed.** Under the supervisor directive *"generally the anchor wins, but practically it
means something else is missing or not working, so it would have to be found — everything is on but the pop
is not moving,"* the investigation moved off mobility and onto the DENSITY anchor, which is the larger miss:

| | measured (ALL-ON preset) | anchor |
|---|---|---|
| population density | **0.0018 persons/km²** | Tallavaara **0.1–0.5**; Binford packing 0.091 |
| population vs the landscape's own K | **0.65%** of 253,887 | — |

**THE ARITHMETIC THAT REFRAMES IT.** density = (crowding-limited population per OCCUPIED cell) × (fraction of
land occupied). Measured: 1657 agents on 254 of 9449 habitable cells = **6.5/cell over 2.69% of the land**.
Spread that SAME per-cell density over all habitable land: 6.5 × 9449 / 944,900 km² = **0.065 persons/km²** —
essentially the Binford packing anchor. **So the density shortfall is not a separate problem from the
concentration; it is the arithmetic consequence of it.** Population sits at its crowding-limited equilibrium
*for the tiny area it actually uses*.

**FOUR CANDIDATES FALSIFIED (all measured on the ALL-ON preset, coastal/temperate, N=1500, 600 steps):**

1. **Dark mechanisms — NO.** A full audit found 27 of 79 `enable_*` flags off in the canonical preset; 23 were
   turned on (4 excluded with stated reasons: an unimplemented stub, an observer, a mutually-exclusive
   alternate path, and R-103's known-wrong criterion). Per-flag liveness ablating FROM all-on: **20/23 LIVE**,
   3 inert (`band_risk`, `malnutrition_fission`, `terrain_pathogen`). The mechanisms work — and all-on moved
   land use only **2.62% → 2.69%**.
2. **The contest split — NO, and INVERTED.** Removing status-weighted sharing makes it *worse*:
   κ=1.5→0 gives pop ×0.81 (1657→1341) and agents below maintenance **7.0% → 15.3%**. Inequality is
   PROTECTIVE at the population level here — an even split spreads the shortage across everybody instead of
   keeping some agents robustly above the floor. My hypothesis (a permanently-starved underclass sets the
   death rate) is not merely falsified, its sign is backwards.
3. **Food limitation — NO.** Median realized intake is **2.47–4.41× requirement**; only 3–15% of agents fall
   below maintenance in any arm. The population is not subsistence-limited. This re-confirms R-106's core
   finding from a new direction.
4. **The forage cap — REAL BUT MINOR.** Clean ablation: pop ×1.23, land 2.69% → **4.09%** (+52% more cells,
   the single largest land-use effect measured). It is the main *dispersal* blocker — a lone agent on a rich
   empty cell perceives only `cv`, exactly what a crowded cell still delivers, so there is no gradient to
   disperse along — but it is nowhere near sufficient.
   **CONFOUND RECORDED:** the `forage_cap_hours ×5/×20` arms must NOT be cited as cap tests. `cv_ref =
   forage_kcal · forage_cap_hours` (`phase1_model` 1078/1098) ALSO sets the agglomeration base scale, so those
   arms were 5×/20× agglomeration subsidies. That is why "cap OFF" (2046) came out BELOW "hours ×20" (3674).

**THE AGGLOMERATION ABLATION — INVERTED TOO, AND IT EXPOSES A DESIGN ENTANGLEMENT.**

| arm | pop | cells | %land | mean occ | max occ | dens/km² |
|---|---|---|---|---|---|---|
| aggl ON, cap ON (shipped) | 1657 | 254 | 2.69 | 6.5 | **159** | 0.0018 |
| **aggl OFF**, cap ON | **331 (×0.20)** | 141 | 1.49 | 2.3 | 21 | 0.0004 |
| aggl ON, cap OFF | 2046 (×1.23) | **386** | **4.09** | 5.3 | 158 | 0.0022 |
| aggl OFF, cap OFF | 742 (×0.45) | 285 | 3.02 | 2.6 | **10** | 0.0008 |
| aggl β=1.0, cap OFF | 742 | 285 | 3.02 | 2.6 | 10 | 0.0008 |

Agglomeration IS the concentrator — max cell occupancy **10 → 159** — exactly as Addendum 4's decomposition
predicted (+387,290 premium against a −35,810 raw-food disadvantage). **But turning it off COLLAPSES the
population (×0.20 to ×0.45)**, because the premium is not merely perceptual: it is realized in the harvest as
`S += aggl_R·(n^β − n)` (`phase1_model` 1633-1641), i.e. it is a genuine production subsidy supplying over
half the economy's output. **The same term does two jobs — spatial attraction and food creation — so it cannot
be tuned for one without wrecking the other.** Any future attempt to fix concentration by weakening
agglomeration will crash the population; the two functions must be separated first.
(*Instrument check passed:* the β=1.0 arm reproduced the OFF arm bit-identically, as the algebra requires
since `n^(β−1) − 1 → 0`.)

**WHERE THIS LEAVES THE DENSITY GAP — no single cause, and still short.** Best measured arm (aggl ON, cap OFF)
reaches 0.0022/km², **46× below the low anchor**. Its projected density at FULL land occupancy is **0.053/km²**
— within ~2× of Binford packing but still under the Tallavaara band. So even perfect spreading does not close
the gap alone: it needs BOTH ~full land occupancy AND ~10 agents/cell (against a median cell K of 24.7, i.e.
40% load — comfortably feasible). The system is in a **low-level trap**: agents harvest only the cells they
stand on, so realized food ≈ (occupied cells) × (per-cell yield); few agents ⇒ few cells harvested ⇒ little
food ⇒ few agents. The capacity field's 253,887-person K is unreachable because 97% of it is never touched.

**MARKER-MATRIX GAP (flagged).** `docs/MARKER_MATRIX.md` scores 16 markers and **has no population-density
marker**, despite density having a documented band (Tallavaara 0.1–0.5/km², MODEL_SPEC §4.3.1) and being the
single largest quantitative miss in the model. Nothing has ever been looking at it — the same failure mode
that let polygyny sit 15× off Marlowe unnoticed (MARKER_MATRIX's own note). **Proposed as marker #17.**

**Origin:** diagnostic-only; `diag_forage_cap.py`, `diag_pop_suppressor.py`, `diag_agglomeration_ablation.py`,
`diag_liveness_allon.py`, `diag_all_on.py` (scratchpad). No source files changed by this addendum. Three of my
own hypotheses falsified here (contest split, agglomeration-as-suppressor, and earlier the self-selection
story), two of them with the sign inverted — recorded per the R-106 house rule.

**ADDENDUM 11 — `settle_tier2_yield` IS dimensionally inert, but the settlement economy is CEILING-GOVERNED,
so correcting it changes almost nothing — and R-63's Bar-Yosef village benchmark SURVIVES the correction
(2026-07-31).**

**The bug, confirmed.** At settlement cells (coastal/temperate, ALL-ON preset):
`tier-2 = settle_tier2_yield · Σ_catchment S_pot = 40 × ~6.7 ≈ 2.7e2 kcal` against
`tier-1 = tf.level(site) ≈ 5.3e6 kcal` — **0.012% of the cell's food.** To supply ~1× a village's own need
(100 people × 75,000 kcal) against Σ S_pot ≈ 6.7 needs `settle_tier2_yield ≈ 1.1e6`; the "~7×" claimed in
PARAMETERS.md needs ≈ 7.8e6. The shipped value is **40** — four to six orders of magnitude short.

**PROVENANCE CONFLICT RESOLVED.** PARAMETERS.md §517 claimed 40 = "~7× a village's need ⇒ fisheries never
food-stressed (R-53)". R-63 §836 separately measured `settle_tier2_yield ∈ {1,2,5}` as **byte-identical** and
attributed that to `S_pot = max(aquatic, cultivability) ≈ 0` on the forest cells where villages formed. Both
cannot hold here: on coastal/temperate settlement cells S_pot ≈ 0.75/cell, so the term is **not** gated to
zero — on this biome the cause is purely SCALE. R-63's explanation was correct for its own (forest) regime;
the PARAMETERS.md claim is false at this value and has been corrected in place.

**THE PREDICTION I MADE WAS WRONG.** I expected a dimensionally-correct tier-2 to blow village size through
the Bar-Yosef band, which would have meant R-63's headline ("village size lands EXACTLY at Bar-Yosef 50–150,
median 88, 100% in band, with no fitting") passed only because the mechanism was dead. Swept instead:

| `settle_tier2_yield` | tier2/tier1 | pop | %land | sites | village med | in 50–150 | in 50–250 |
|---|---|---|---|---|---|---|---|
| **40** (shipped) | 0.012% | 1657 | 2.69 | 17 | 63 | 52.9% | 64.7% |
| 4e3 | 1.30% | 1659 | 2.68 | 28 | 104 | 75.0% | 96.4% |
| 4e4 | 33.5% | 1498 | 2.68 | 8 | 94 | 62.5% | 87.5% |
| 4e5 | 224% | 1608 | 2.78 | 6 | 108 | 50.0% | 66.7% |
| 1.1e6 (~1× need) | 819% | 1557 | 2.55 | 15 | 75 | **80.0%** | 86.7% |
| 7.8e6 (claimed 7×) | **4673%** | 1407 | 1.96 | 14 | 118 | 78.6% | **100%** |

**Across a 200,000× change in the parameter, village median moves only 63 → 118 and population 1657 → 1407.**
The in-band score *improves* (52.9% → ~78-80%). **R-63's benchmark is not an artefact of the dead mechanism —
it survives the correction.**

**WHY — the settlement economy is CEILING-GOVERNED, not tier-2-governed.** `phase1_model` line 1648 applies
`S = min(S, self._settlement_carrying_capacity((cx, cy)))` — the R-63 catchment ceiling, which reads the
DEPLETABLE harvest field over the catchment. However large the (static, un-depletable) tier-2 term becomes, the
realized cell pool is clamped to what the catchment can actually yield. That is why `tier2/tier1` can reach
4673% with almost no behavioural consequence, and why `settle_tier2_yield` reads as a **dead parameter over
five-plus orders of magnitude**. It also means the ceiling — not the tier-2 term — is the load-bearing piece of
the settlement economy, and the one that carries depletion into village food (Addendum 9 measured it binding in
28.6% of settlement cells).

**NOT ADOPTED.** Raising the value mildly improves the Bar-Yosef in-band score, but that is a single seed with
only 14–17 villages, and MARKER_MATRIX binding rule 3 ("seeds must beat the variance") forbids adopting on it.
Queued for the multi-seed battery. The DOCUMENTATION error is corrected regardless, since it was asserting a
food supply that does not exist.

**Origin:** diagnostic-only; `diag_tier2_scale.py` (scratchpad). `docs/PARAMETERS.md` §517 corrected in place
(a false claim, not a calibration change). No source files changed. Fourth of my own hypotheses falsified by
measurement today.

**ADDENDUM 12 — "ALL MECHANISMS ON" SCORES MATERIALLY WORSE AGAINST THE MARKER MATRIX than the curated
preset (run-length-matched, 5 worlds × 5 seeds); plus a direct confirmation of Addendum 10's density
arithmetic, and no long-horizon runaway (2026-07-31).**

**Why this run.** The supervisor rule is that every BUILT mechanism runs unless deliberately off for an
ablation. An audit found **27 of 79 `enable_*` flags dark** in the canonical preset (`emergent_village_demog`
+ VILLAGE + ELITE), and `run_campaign.py` exposed a `C_*` knob for only ~10 of them, so a campaign could not
exercise the rest at all. Added `C_ALLON` (enables every remaining built mechanism except four, each with a
stated reason) and `L_TAGSUF` (a tag namespace, see the instrument note below), then ran the canonical
`battery6_long` S4 envelope — the project's own harness, with its runtime anchor guard — at 5 worlds × 5 seeds
× 2000 steps. `ascribed_frac` was correctly SKIPPED by the anchor guard as undocumented.

**TWO INSTRUMENT FAULTS CAUGHT, ONE OF THEM MINE.**
1. **My own tag bug.** `L_TAGSUF` was applied to arm CONSTRUCTION but not to the four places that
   re-derive tags during SCORING (`battery6_long` lines 169/198/199/218). The battery therefore *ran* 25 new
   all-on arms (5.3 h of compute, files written correctly) and then **scored the 25 pre-existing baseline
   trajectories** — reporting numbers identical to those already in MARKER_MATRIX.md. Caught only because six
   markers matching the recorded values to four decimal places (0.2515, 0.296) is not plausible. Fixed; the
   all-on arms were rescored from disk at zero compute cost. **This is the same silent-no-op class as the
   `bud_events` counter and the `battery1_liveness` patch window — the third such fault this arc.**
2. **A run-length confound.** The historical baseline arms on disk ran **3000** steps; the all-on arms ran
   **2000**. `sustained()` medians over the LAST 50%, so baseline covered steps 1500-3000 and all-on
   1000-2000. `connubium_med`, `lineage_size_gini` and `lin_top_share` are structure-ACCUMULATION markers that
   grow with time, so the shorter run scores lower for free. Corrected by TRUNCATING every baseline trajectory
   to step ≤ 2000 and rescoring with identical `sustained()` semantics — no re-simulation. The uncorrected
   comparison would have overstated the degradation (baseline connubium reads 15/25 at 3000 steps, 13/25 at
   2000; lineage Gini 17/25 → 12/25).

**PAIRED RESULT (both arms at an identical 2000-step horizon, 25 arms each):**

| marker | band | baseline | ALL-ON | delta |
|---|---|---|---|---|
| `band_med` | [18–35] | 23/25 | **20/25** | −12% |
| `settle_med` | [50–150] Bar-Yosef | 21/25 | 21/25 | 0 |
| `settle_med` | [50–250] Alvard | 21/25 | 21/25 | 0 |
| `connubium_med` | [79–332] | 13/25 | **3/25** | **−40%** |
| `lineage_size_gini` | [0.51–0.68] | 12/25 | **3/25** | **−36%** |
| `lin_top_share` | [0.08–0.30] | 1/25 | 2/25 | +4% |
| T-7 hierarchy ordering | 3 proxies | 2 of 3 hold | **0 of 3** | — |

**Turning on all built mechanisms makes the model fit the ethnographic record substantially WORSE on three of
six markers, with two unchanged and one (the weakest, already 1/25) marginally better.** `band_med`'s observed
range widens 15.5–32 → 8–37, i.e. band sizes become more variable in both directions, which points at the
band-size/fission group (`enable_emergent_band_size`, `enable_malnutrition_fission`,
`enable_resource_directed_fusion`) as candidate culprits — **not yet bisected; 23 flags cannot be attributed
from one contrast.**

**INTERPRETATION, stated carefully.** This does NOT show the dark mechanisms are wrong, and it does not settle
whether they should be on. It shows that the canonical preset's curation is load-bearing for the current
marker scores, and that "everything on" is a materially different model that has never been calibrated. The
honest options are (a) keep the curated preset as canonical and treat all-on as a research configuration,
(b) bisect the degradation, fix or re-calibrate the offending mechanisms, and then adopt all-on, or (c) accept
worse marker fit in exchange for mechanistic completeness. **(b) is the only one that does not discard
information; it is the recommended next step and is not yet done.**

**DENSITY — ADDENDUM 10'S ARITHMETIC CONFIRMED.** The campaign harness runs a capacity sub-window, so these
worlds have **1584 habitable cells** (not 9449). Final coastal/temperate population **7909 on 1584 cells =
4.99 agents/cell ⇒ 0.0499 persons/km²**. Addendum 10 projected **0.053/km²** for full land occupancy from the
per-cell equilibrium — measured 0.0499. **The density decomposition holds**: when agents occupy essentially
all of the available land, density lands where the arithmetic said it would. It remains **~2× below Binford
packing (0.091)** and 2–10× below the Tallavaara band, so a residual per-cell deficit survives the spatial
one — the two deficits are separable and both real.

**S6 LONG-HORIZON DRIFT — NO RUNAWAY.** Two 30k-step-budget arms reached 15,402 and 11,708 steps: population
×1.73/×1.76 with **late-acceleration 0.833/0.745 (decelerating)**, settlements ×2.26/×2.20 (late-accel
0.745/0.719), `mean_material` flat (×0.913/×0.992), `gini_cred` stable. R-105's late-onset runaway does not
recur under all-on. **Fission rate 5.0e-4/settlement-yr against Bandy's 2–5e-3 — out of band (≈10× low)**,
where MARKER_MATRIX previously recorded 5.6e-3 ✓; whether that is the all-on config or the shorter horizon is
not established.

**Origin:** `sic_games/outputs/mechanism_battery/battery6_long.py` (`L_TAGSUF` + the four scoring-tag fixes),
`sic_games/outputs/substrate_run/run_campaign.py` (`C_ALLON`), both default-off/no-op; paired rescoring via
`score_paired.py` (scratchpad). Results: `battery6_long_results.json` (all-on), baseline arms rescored from
their existing trajectories.

**ADDENDUM 13 — THE ATTRACTION/PRODUCTION SPLIT IS BUILT AND THE HYPOTHESIS BEHIND IT IS FALSIFIED: the
concentration comes from REAL superlinear production, not from perception. Agents are behaving correctly; the
economics they read are what concentrate them (2026-07-31).**

**What was built.** `aggl_attraction_weight` (default 1.0, bit-exact) scales the PERCEIVED co-location premium
in `substrate.diffusion_select_target` alone, leaving realized harvest production untouched. Motivated by
Addendum 10's entanglement finding: one term, `aggl_R·(n^β − n)`, both ATTRACTS movers and FEEDS them, so
ablating it broke the concentration (max cell occupancy 159 → 10) while cutting population to ×0.20–0.45.
The weight was supposed to let those be tuned separately. 7 unit tests, including a quantitative one that
reads the premium back out of the scorer by bisecting the balancing move cost and confirms it equals
`wt·R·(n^(β−1) − 1)` to 2%.

**THE PREDICTION: a lowered weight should give aggl-OFF's DISPERSAL while keeping aggl-ON's POPULATION.
FALSIFIED.** (ALL-ON preset, coastal/temperate, N=1500, 600 steps, `patch=None`.)

| arm | pop | cells | %land | mean occ | max occ | dens/km² | intake<1× |
|---|---|---|---|---|---|---|---|
| attract 1.0 (shipped) | 1657 | 254 | 2.69 | 6.5 | 159 | 0.0018 | 7.0% |
| attract 0.5 | 1463 | 223 | 2.36 | 6.6 | 205 | 0.0015 | 13.1% |
| attract 0.25 | 1508 | 223 | 2.36 | 6.8 | 191 | 0.0016 | 9.5% |
| attract 0.1 | 1413 | 227 | 2.40 | 6.2 | 86 | 0.0015 | 7.4% |
| **attract 0.0** | 1379 | **199** | **2.11** | **6.9** | 128 | 0.0015 | 7.5% |
| **agglomeration fully OFF** | **331** | 141 | 1.49 | **2.3** | **21** | 0.0004 | 7.9% |

**Zeroing the perceived premium does essentially nothing to the concentration.** Mean occupancy is flat at
**6.2–6.9 across every weight** — and 2.3 only when agglomeration is fully off. Occupied cells go DOWN
(254 → 199), not up. `max_occ` is non-monotone (159/205/191/86/128), i.e. noise. Population falls modestly
(×0.83), so the knob is not perfectly inert, but it is nowhere near the lever.

**WHAT THIS MEANS — Addendum 4's decomposition was right and my reading of it was wrong.** Addendum 4 measured
the perceived agglomeration premium at **+387,290** against a **−35,810** raw-food disadvantage, and I treated
that as agents being *lured* into crowding against their interest. They are not. That premium is a FAITHFUL
signal of a genuine production advantage: `S += aggl_R·(n^β − n)` puts real food on crowded cells, so
per-capita yield really does rise with n. **The ideal-free distribution is working correctly — it sends agents
where the returns actually are.** The perception was never the driver; the economics are. My fix targeted the
messenger.

**SO THE LEVER IS THE PRODUCTION FUNCTION, AND THE ANCHOR BEHIND IT IS ALREADY FLAGGED AS BORROWED.** With
`aggl_beta = 1.15` (point mode) per-capita output rises with n **without bound**, which makes unlimited
crowding economically optimal; concentration is then the correct answer to the economics, not a defect in the
movement rule. MODEL_SPEC §4.8.21 already records the provenance caveat verbatim: β≈1.15 is **Bettencourt
2013, measured on MODERN CITIES (socioeconomic output)** — "an explicit cross-domain borrowing... subsistence
returns-to-co-location (weirs/terraces/defense/storage) may be sharper — **a *testable prediction*, not a
fit**." This is that test, and it reads against the borrowing: unbounded urban superlinearity applied to
forager subsistence produces a landscape 97% empty with everyone stacked on 2.7% of it.

**Consistent with R-63**, which found villages land exactly at Bar-Yosef 50–150 with agglomeration OFF and
become mega-villages with it ON. Same cause, seen from the settlement side.

**THE REMAINING TENSION, stated honestly.** Agglomeration OFF gives good village size and correct dispersal
(mean occupancy 2.3) but a population of 331 — far too small. Agglomeration ON gives a viable population and
untenable concentration. Neither is right, and no setting of the new weight bridges them, because the weight
does not touch the term that matters. **The next test is the SHAPE of the production function**: an unbounded
`n^β` versus a SATURATING one (returns to co-location that rise then level off, which is what a real catchment
does — you cannot keep gaining from crowding forever). The `catchment` mode (`L(n) = n^α/(n^α + half^α)`)
already implements a saturating form and is retired as DEAD_ENDS DE-11, but it was retired for a different
question and is worth re-testing against this one.

**KEPT ANYWAY, at default 1.0.** The split is retained because it is correct, tested and bit-exact, and it
now carries a measured answer — "perception is not the concentrator" — that the codebase previously only
assumed. It is not adopted as a non-default value.

**Origin:** `sic_games/src/sic_games/{demography,substrate,phase1_model}.py`,
`sic_games/tests/test_aggl_attraction_split.py` (7 tests), commit 7506828; sweep
`diag_aggl_split.py` (scratchpad). Seventh of my own hypotheses falsified in this arc.

**ADDENDUM 14 — A POSITIVE RESULT: a CONGESTIBLE production form breaks the population/concentration
tradeoff (pop ×0.95, land use +57%, mean occupancy −40%). It does NOT fix the density gap, and the mechanism
that does it is one this project already retired — for exactly the property we now want (2026-07-31).**

**Setup.** Addendum 13 established the concentration is produced by REAL superlinear output
(`S += aggl_R·(n^β − n)`, β=1.15, per-capita rising without bound), not by perception. This sweeps the
production SHAPE at the bit-exact default attraction weight: point mode β ∈ {1.15, 1.10, 1.05, 1.00} and the
`catchment` form `L(n) = n^α/(n^α + half^α)` over `aggl_half` ∈ {25, 50, 100, 200}, plus an agglomeration-OFF
reference. Coastal/temperate, ALL-ON, N=1500, 600 steps, `patch=None`.

**INSTRUMENT CHECK PASSED:** `point β=1.00` reproduced the agglomeration-OFF arm **exactly** (331 / 141 cells /
occ 2.3 / max 21 / 0.0004), as the algebra requires since both `n^(β−1) − 1` and `n^β − n` vanish at β=1.

| arm | pop | cells | %land | mean occ | max occ | dens/km² | village med |
|---|---|---|---|---|---|---|---|
| point β=1.15 (shipped) | 1657 | 254 | 2.69 | 6.5 | 159 | 0.0018 | 63 |
| point β=1.10 | 1044 | 167 | 1.77 | 6.3 | 179 | 0.0011 | 110 |
| point β=1.05 | 795 | 226 | 2.39 | 3.5 | 167 | 0.0008 | 134 |
| point β=1.00 | 331 | 141 | 1.49 | 2.3 | 21 | 0.0004 | — |
| **catchment half=25** | **1569** | **398** | **4.21** | **3.9** | **89** | 0.0017 | **49** |
| catchment half=50 | 938 | 298 | 3.15 | 3.1 | 49 | 0.0010 | 50 |
| catchment half=100 | 626 | 200 | 2.12 | 3.1 | 51 | 0.0007 | 51 |
| catchment half=200 | 540 | 200 | 2.12 | 2.7 | 44 | 0.0006 | 51 |
| agglomeration OFF | 331 | 141 | 1.49 | 2.3 | 21 | 0.0004 | — |

**THE POSITIVE.** `catchment half=25` keeps **95% of the shipped population** (1569 vs 1657) while cutting
mean cell occupancy **6.5 → 3.9 (−40%)**, max occupancy **159 → 89 (−44%)**, and expanding land use
**2.69% → 4.21% (+57%)**. Lowering β in point mode cannot do this — β=1.10/1.05 shed 37%/52% of the population
for little dispersal, and β=1.00 is just agglomeration off. **This is the first arm in the arc that improves
the spatial pathology without paying for it in population.**

**WHAT IT DOES NOT DO — stated plainly. It does not fix the density gap.** Realized density is
**0.0017 vs the shipped 0.0018** — unchanged, still ~55× below the Tallavaara low anchor. Density is
population ÷ total land, and population is essentially the same; dispersal redistributes the same people over
more cells. Worse for the projection: since `proj = mean_occ/100`, the full-occupancy projection FALLS
(0.0652 → 0.0394), because dispersal trades per-cell density for coverage. **The population ceiling and the
concentration are separable problems, and this addresses only the second.** Village median 49 also sits just
under Bar-Yosef's 50 floor (from 63), and under-maintenance intake rises 7.0% → 10.8%.

**THE MECHANISM IS RETIRED, AND DE-11 CALLED THIS EXACTLY RIGHT.** `aggl_mode="catchment"` is DEAD_ENDS
**DE-11** (2026-07-06). Its stated reason is not that the mechanism misbehaves — it is that `L(n)` saturates
so per-capita `R·L(n)/n` **peaks then falls ∝1/n**, making the term "**areal-dispersive**", with the measured
signature that cranking it "**monotonically reduces packing (26→21→15%)**". **This sweep reproduces that
direction precisely** (mean occupancy 3.9 → 3.1 → 3.1 → 2.7 as `half` rises 25 → 200). DE-11 retired it for
failing to produce nucleation, because nucleation was the goal in July. **We now measure over-nucleation as
the defect. The mechanism has not changed; the objective inverted.**

**BUT DO NOT CALL IT "SATURATING AGGLOMERATION" — DE-11 is right that it is a different economic object.**
Bettencourt's form has per-capita rising without bound (an agglomeration economy); the catchment form has
per-capita peaking then declining (a **congestible common-pool**). So the real modelling question this
exposes is: *which is correct for FORAGER subsistence?* MODEL_SPEC §4.8.21 already flags β≈1.15 as measured on
**modern cities** and labels the transfer "a *testable prediction*, not a fit". A weir, a drive hunt, a shellfish
bed or a catchment is congestible — past some crew size more bodies add nothing and then subtract. Unbounded
increasing returns may well be right for later urbanism and wrong here. **That is a substantive claim about
the model's economics, and it is now supported by a measurement rather than asserted.**

**NOT ADOPTED.** One seed, one world. MARKER_MATRIX binding rule 3 ("seeds must beat the variance", with R-65's
30× seed variance on record) forbids adopting on this. Required before any adoption: the full 5×5 envelope on
`battery6_long`, a check that village size stays inside Bar-Yosef, and an explicit decision on whether to
revive a DEAD_ENDS entry — which needs the supervisor, since it reverses a documented retirement.

**Origin:** diagnostic-only; `diag_aggl_shape.py` (scratchpad). No source changed (the catchment path already
exists and is kept "for comparison only" per DE-11). Reads against DEAD_ENDS DE-11's retirement and against
MODEL_SPEC §4.8.21's own flagged caveat.

**ADDENDUM 15 — THE MOBILITY THREAD CLOSES: nothing is miscalibrated. The world set matches the forager
anchor (+18%), and the missing gradient is a DISCRETIZATION limit — the model cannot represent a move shorter
than 10 km or more often than monthly. Plus: the group bisection was UNDERPOWERED and its null is not
evidence (2026-07-31).**

**PART 1 — the mobility question, answered under the anchor-wins directive.** The supervisor rule is that when
a lit anchor blocks a benchmark the anchor stands and something else must be broken. Addendum 9 found
`mobility_npp_ref = 900` sits BELOW the landscape mean (1004), so 99.1% of agents get `r=1` and the
Kelly/Binford productivity gradient never reaches behaviour. Two candidate culprits: the anchor, or the worlds.
**Measured: it is neither.**

| world | mean NPP | median NPP | p10 | p90 | r at median |
|---|---|---|---|---|---|
| coastal/temperate | 1004 | 1054 | 694 | 1280 | 1 |
| flat/boreal | 795 | 859 | 497 | 987 | 1 |
| flat/tropical | 2291 | 2410 | 1806 | 2508 | 1 |
| flat/temperate | 1083 | 1109 | 720 | 1406 | 1 |
| hilly/temperate | 1002 | 1067 | 688 | 1232 | 1 |
| mountainous/boreal | 458 | 440 | 316 | 624 | **2** |

Median NPP across the six worlds is **1061 against the 900 anchor — +18%**. That is not a systematic bias;
foragers occupy habitats spanning roughly 150–2500 g/m²/yr and this world set sits comfortably inside it.
**World generation is not the defect, and `npp_ref=900` (the Tallavaara forager median) does not need moving.**

**THE ACTUAL CONSTRAINT IS THE GRID.** `mobility_radius` returns an INTEGER stride with a floor of 1, and one
cell is **10 km**. So the shortest move the model can represent is 10 km — while Binford/Kelly's *mean*
residential move is **~4–16 km** (158 km/yr spread over 10–40 moves). In rich habitat Kelly's ∝1/productivity
law calls for moves SHORTER than one cell, which is unrepresentable; the stride can only floor at 1. The
gradient therefore survives only at the poor end (mountainous/boreal, r=2) and is mathematically erased
everywhere above ~600 g/m²/yr. **`r=1` in a rich biome is not a calibration failure — it is the model
correctly saturating at its own spatial resolution, at a value (10 km) that is already a realistic
residential move.**

**COMBINED WITH THE TEMPORAL LIMIT (Addendum 7), THE ENVELOPE IS BOUNDED.** Movement resolves once per monthly
step ⇒ ≤12 moves/yr; each move is ≥10 km ⇒ the representable maximum is **12 × 10 = 120 km/yr**, against
Binford **158** and Kelly **174**. **The discretization caps achievable annual travel just BELOW the
ethnographic anchor, and only if every agent moves every step.** Measured mobile-agent travel is 86–115 km/yr
(Addenda 7/8), i.e. **72–96% of the model's own representable ceiling.** The model is close to the most it can
express. Closing the remaining gap is an architectural question (sub-cell movement, a finer grid, or a
sub-monthly step), not a parameter one. This retires the "calibrate `mobility_npp_ref`" task: there is nothing
to calibrate.

**PART 2 — THE GROUP BISECTION IS INCONCLUSIVE, AND ITS NULL MUST NOT BE READ AS A RESULT.** Addendum 12's
degradation (connubium 13/25→3/25, lineage Gini 12/25→3/25) was bisected by adding flag groups one at a time
on top of the canonical baseline (3 worlds × 2 seeds × 1200 steps):

| arm | band_med | connubium_med | lineage_size_gini | settle_med |
|---|---|---|---|---|
| baseline | 6/6 | **1/6** | **0/6** | 6/6 |
| G1 band/fission | 6/6 | 0/6 | 0/6 | 6/6 |
| G2 social/residence | 6/6 | 2/6 | 0/6 | 6/6 |
| G3 demography | 6/6 | 0/6 | 0/6 | 6/6 |
| G4 environment | 6/6 | 1/6 | 0/6 | 6/6 |

No group reproduces the degradation — **but the test had no power to detect one.** The two markers that
degraded are ALREADY FLOORED AT BASELINE at this horizon (connubium 1/6, lineage Gini 0/6), because both are
structure-ACCUMULATION markers and 1200 steps is too short for them to reach their bands at all; at 2000 steps
the same baseline reaches 13/25 and 12/25, which is where the headroom to detect a drop exists. `band_med` is
6/6 in every arm, so it carries no signal either. **I chose 1200 steps for speed and destroyed the very
contrast the test was built to measure.** Reporting "no group is responsible" would be a false negative
manufactured by the instrument — the same class of error as the un-suffixed scoring tags and the missing
`C_EXTRA_ON` knob. **The bisection must be re-run at ≥2000 steps; until then the attribution is OPEN.**

**Origin:** diagnostic-only; a direct world-NPP/stride computation and `diag_bisect_allon.py` (scratchpad).
No source changed. Retires the mobility-calibration task; leaves the Addendum 12 attribution open.

**ADDENDUM 16 — ADDENDUM 14'S POSITIVE DOES NOT SURVIVE THE FULL ENVELOPE. The congestible form buys
dispersal by destroying villages: `settle_med` 21/25 → 12/25. The tradeoff was not broken, it was RELOCATED —
and that identifies superlinear co-location as what MAKES villages (2026-07-31).**

**The confirmation required by binding rule 3.** Addendum 14 reported a single-seed positive: the congestible
`catchment` production form kept 95% of the population while cutting mean cell occupancy 40% and expanding
land use 57%. It flagged the risk that village median had fallen 63 → 49, just under the Bar-Yosef floor.
The full 5 worlds × 5 seeds × 2000 steps envelope was run to settle it (`C_AGGLMODE=catchment`,
`C_AGGLHALF=25`, tags `_b6_catch_*`). **The flagged risk is what happened.** All three columns at a matched
2000-step horizon:

| marker | band | baseline | ALL-ON (point β=1.15) | ALL-ON (catchment half=25) |
|---|---|---|---|---|
| `band_med` | [18–35] | 23/25 | 20/25 | **22/25** |
| `settle_med` | [50–150] Bar-Yosef | 21/25 | 21/25 | **12/25** |
| `settle_med` | [50–250] Alvard | 21/25 | 21/25 | **12/25** |
| `connubium_med` | [79–332] | 13/25 | 3/25 | **1/25** |
| `lineage_size_gini` | [0.51–0.68] | 12/25 | 3/25 | 3/25 |
| `lin_top_share` | [0.08–0.30] | 1/25 | 2/25 | 2/25 |
| T-7 ordering | 3 proxies | 2 of 3 | 0 of 3 | 1 of 3 |

**Village formation collapses.** `settle_med` falls **21/25 → 12/25** on both the Bar-Yosef and Alvard bands,
with observed values **0..83** — villages never exceed 83 anywhere, and in several arms fail to form at all
(the 0s). Band size improves marginally (20→22/25) but its observed range widens to 3..38. Connubium degrades
further (3/25 → 1/25). Only T-7 recovers slightly (0 → 1 of 3 proxies).

**SO THE TRADEOFF WAS NOT BROKEN — IT MOVED.** Addendum 14 measured the congestible form paying no price in
POPULATION and concluded the population/concentration tension was resolved. It was not: the price is paid in
VILLAGE SIZE instead. Dispersal works so well that nucleation stops happening. **Addendum 14's headline is
hereby superseded: it was a real effect measured on too narrow a slice, and the marker it broke was not among
the four that sweep scored.** The single-seed sweep tracked village median but not the pass fraction across
worlds, which is precisely what binding rule 3 exists to catch.

**WHAT THIS BUYS US ANYWAY — a mechanistic identification.** Point-mode superlinearity (per-capita output
rising without bound with n) is what MAKES villages in this model. Replace it with a congestible common-pool
(per-capita peaking then falling ∝1/n) and villages stop reaching Bar-Yosef size. So the same term is doing a
THIRD job on top of the two Addendum 10 identified: it attracts movers, it feeds the economy, **and it is the
engine of village nucleation.** That is why every attempt to soften it costs something elsewhere — population
(Addendum 13), or villages (here). **The concentration is not a bug bolted onto village formation; it is the
same mechanism seen from the other side.**

**IMPLICATION FOR THE DENSITY PROGRAMME.** There is now no known setting of the agglomeration production
function that gives dispersed settlement AND viable population AND Bar-Yosef villages simultaneously. Either
the three are genuinely in tension under any single co-location term — in which case villages and dispersal
need SEPARATE mechanisms (nucleation from something other than unbounded returns, e.g. defensibility, storage
tethering or site appraisal, with co-location returns left congestible) — or the resolution lies outside this
term entirely. Addendum 10's arithmetic still stands and is untouched by this: density = per-cell occupancy ×
fraction of land occupied, and the shortfall is dominated by the 2.7% land-use term.

**NOTHING ADOPTED. `aggl_mode` stays `"point"`**, and DEAD_ENDS **DE-11** stands — its retirement of the
catchment form is now supported by a second, independent line of evidence (village collapse), on top of the
"areal-dispersive" reason it originally gave. The revival question raised in Addendum 14 is **answered
negatively and does not need supervisor time.**

**Origin:** `battery6_long` 5×5 envelope, tags `_b6_catch_*`, via the `C_AGGLMODE`/`C_AGGLHALF` knobs
(d359054). Compared at a matched 2000-step horizon against the ALL-ON point-mode arms (Addendum 12) and the
run-length-truncated canonical baseline. Supersedes Addendum 14's adoption case; Addendum 14's measurements
themselves stand.

**ADDENDUM 17 — BISECTION, PROPERLY POWERED: `band_med`'s degradation IS attributable (band/fission group,
+14% band size in 6/6 pairs). The connubium and lineage-Gini degradations are NOT — their per-pair variance
dwarfs any group effect. Plus a fifth instance of the silent-resume bug, this one mine (2026-07-31).**

**INSTRUMENT FAULT FIRST (the fifth in this arc, third of them mine).** The first re-run of the bisection at
2000 steps produced output **byte-identical** to the 1200-step pass. It had not run: `diag_bisect_allon.py`
tagged arms `_bx_{group}_{world}_s{seed}` with **no horizon in the tag**, so its resume check
(`traj(tag) is None`) matched the existing 1200-step trajectories and skipped all 30 arms, re-scoring stale
files. Identical to `battery6_long`'s un-suffixed scoring tags (Addendum 12) and the missing `C_EXTRA_ON`
knob. Fixed by putting the step count in the tag. **Every one of these five faults produced a clean,
plausible, wrong answer; the only reason any was caught is that the results were suspiciously consistent.**
(Arms then wall-clocked at **1800** steps against the 2000 requested — the analysis below is at 1800.)

**SECOND METHOD FIX — pass fractions were the wrong statistic.** Scoring 6 arms as a pass fraction discards
nearly all the information: baseline sits at 1/6 on both degraded markers, so a real drop has nowhere to
appear (floor effect), and 6 Bernoulli trials cannot resolve a 40-point change. Re-analysed the SAME
trajectories as **paired continuous deltas** — each group arm against the baseline arm of the same world and
seed, so world/seed variation (R-65: up to 30×) cancels exactly. Sign test over the 6 pairs.

| group | marker | median Δ | pairs down | rel. | reading |
|---|---|---|---|---|---|
| **G1 band/fission** | `band_med` | **+3.75** | **0/6** | **+14%** | **consistent, all pairs up** |
| G1 band/fission | `pop` | +425 | 0/6 | +6% | consistent |
| G1 band/fission | `lineage_size_gini` | −0.023 | 5/6 | −5% | small, consistent |
| G2 social/resid | `pop` | +1008 | 1/6 | +14% | consistent |
| G3 demography | `pop` | −1200 | 4/6 | −16% | real, some spread |
| G3 demography | `lineage_size_gini` | −0.013 | 5/6 | −3% | small, consistent |
| G4 environment | `settle_med` | −4.25 | 5/6 | −4% | small, consistent |
| G4 environment | `band_med` | +1.50 | 0/6 | +6% | consistent |
| *all four groups* | `connubium_med` | −15 … +10.5 | 1–3/6 | — | **NOISE** (per-pair −49 … +62) |

**ATTRIBUTED: the `band_med` degradation.** `G1_band_fission` (`emergent_band_size`,
`malnutrition_fission`, `resource_directed_fusion`, `band_risk`) raises band size **+14% in 6 of 6 pairs** —
the most consistent effect in the whole table. Baseline bands run 23.5–31.5 against a [18–35] band, so a
uniform +14% pushes the upper arms out the top. That is precisely Addendum 12's `band_med` 23/25 → 20/25, and
it matches the observed range widening to 8..37 there. **`G4_environment` adds a smaller +6% in the same
direction.** Which of G1's four flags carries it is not resolved (the group was not split further).

**NOT ATTRIBUTED — and the reason is measurement, not absence.** `connubium_med` per-pair deltas swing from
**−49 to +62** with no group showing a consistent direction; at that variance a 6-pair design cannot resolve
anything, and no group comes close to explaining Addendum 12's 13/25 → 3/25. `lineage_size_gini` shows small
consistent negatives for G1 (−5%) and G3 (−3%) which together are nowhere near its 12/25 → 3/25 collapse.
**So the two large degradations are either INTERACTIVE across groups, or driven by the knob-controlled flags
`C_ALLON` deliberately does not touch** (`enable_exogamy`, `enable_adaptive_connubium`,
`enable_economic_defensibility`, `enable_village_budding`, `enable_soil_depletion`, `enable_genome`, the
lineage branch/split rates — several of which bear directly on connubium reach and lineage structure).
Resolving it needs either a full 5×5 envelope per group (5 × 25 = 125 arms) or a design that varies the
knob-controlled set, and **is left OPEN rather than forced.**

**INCIDENTAL, worth recording:** the population effects are the clearest signals here — G2 social/residence
**+14%**, G1 band/fission **+6%**, G3 demography **−16%**. The demography group (which includes
`enable_intake_fertility`, this arc's own addition) costs population, consistent with R-106's finding that the
intake brake moves regulation from deaths to births and lowers the equilibrium.

**Origin:** diagnostic-only; `diag_bisect_allon.py` (horizon-tagged) + `score_bisect_paired.py` (scratchpad,
re-analysis of the same trajectories, no new simulation). 3 worlds × 2 seeds, 1800 steps. No source changed.

**ADDENDUM 18 — MALTHUS RETEST ON A TRACTABLE WORLD: NO CYCLES. Population does not oscillate, it DECLINES
in every completed seed — the slow variable (soil) DRAGS carrying capacity down rather than driving
oscillation. And the equilibrium-seeding trick failed for an instructive reason (2026-07-31).**

**Design, and why it is the first tractable attempt.** Every prior cycle test in this arc was uninterpretable
because the population never reached stationarity (Addendum 6). Two changes fixed the tractability: a SMALL
world (`patch=32` ⇒ 708–1008 habitable cells, so equilibrium is reached in hundreds of steps rather than
thousands) and **seeding AT the measured equilibrium** rather than growing into it (R-106: starts of 3k/12k/20k
converge on the same attractor). ALL-ON, 6000 steps, sampled every 4 (1500 samples ⇒ `period_of` accepts
periods to window/3 = 2000 steps = 167 yr, covering the 60–100 yr anchor), 3 seeds. Founders tuned to
6200/6000/4400 after a first attempt at 10,000 proved ~60% too high and cost 2.2 s/step.

| series | seed 1 | seed 2 | verdict |
|---|---|---|---|
| population | trend **−11.4%**/1000 steps, ratio 0.805 → **DRIFTING** | **−13.0%**/1000, ratio 0.690 → **DRIFTING** | **uninterpretable** |
| occupied cells | stationary; period 1368, ac_peak **−0.003** | stationary; period 784 (65 yr), ac_peak **+0.042** | **NO CYCLE** (both ≤ null p95 0.13) |
| mean wealth | stationary; period **144 (12.0 yr)**, ac_peak **+0.312**, CV 0.101 | stationary; period **240 (20.0 yr)**, ac_peak **+0.176**, CV 0.134 | see below |

(Seed 0 incomplete at 3000/6000 steps; its trajectory 6200 → 10522 → **12054** → 11926 → 9982 → 8301 → 8001
shows clear OVERSHOOT then decline.)

**1. NO MALTHUSIAN CYCLES — and this time the negative is INTERPRETABLE.** `occupied_cells` is stationary in
both completed seeds and its autocorrelation peak is **−0.003 and +0.042**, at or below R-87d's calibrated
null floor (p95 = 0.13). That is a genuine negative on a stationary series — **the first one this arc has been
entitled to state**, since every previous attempt failed the stationarity gate.

**2. THE ONE REPRODUCIBLE POSITIVE IS NOT A SECULAR CYCLE.** `mean_wealth` clears the null floor in BOTH seeds
(+0.312, +0.176). But it fails on three counts: the **periods disagree by 1.7×** (12.0 vs 20.0 yr — two seeds
agreeing that *a* peak exists while disagreeing on *where* is not a period); both are far below the **60–100 yr**
ethnographic anchor; and the detrended CV is **10–13%** against the **30–50%** swings real secular cycles show.
It is also a per-capita STOCK, not the Malthusian population variable. **Plausible mechanical origin, offered
as a hypothesis and not a finding:** `soil_regrow_per_yr ≈ 0.06` gives a ~17 yr time constant, squarely in the
12–20 yr band — i.e. this may simply be the soil depletion/regrowth relaxation showing up in wealth, not a
population dynamic at all.

**3. THE REAL FINDING — THE SLOW VARIABLE DRAGS, IT DOES NOT CYCLE.** R-106 and R-97 concluded that cycles
need a SLOW variable and that the model had none. `enable_soil_depletion` supplies one (~17 yr). With it live,
population does not oscillate around a level — **it falls monotonically in both completed seeds** (−11.4%,
−13.0% per 1000 steps) and, in seed 0, overshoots to 12,054 and then falls a third to 8,001. Progressive
capacity degradation moves the attractor DOWNWARD instead of creating a delayed restoring force. **A slow
variable is necessary for cycles but is evidently not sufficient; a degrading one produces decline, not
oscillation.**

**4. THE EQUILIBRIUM-SEEDING TRICK FAILED, INSTRUCTIVELY.** It was meant to deliver stationarity by starting
at the attractor. It could not, because **under soil depletion there is no stationary state to start at** —
carrying capacity itself is falling, so any seeded level is transient by construction. Future cycle tests face
a fork: ablate soil depletion (removing the only slow variable, and with it any hope of a delayed feedback), or
accept a declining baseline and detrend hard enough to test for oscillation *about the trend* — which
`period_of` already does via its linear detrend, and which is what makes the `occupied_cells` negative usable.

**5. A CAUTION ON SINGLE-SEED DENSITY CLAIMS.** The three seeds settle at very different densities — seed 0
~0.120/km² (after overshoot), seed 1 ~0.062, seed 2 ~0.035 and falling — a **3× spread** on worlds differing
only in the terrain lottery. Any density statement from one seed, including several made earlier today, carries
that uncertainty.

**Origin:** diagnostic-only; `diag_malthus_stationarity.py` (scratchpad), `patch=(30,30,32)`, ALL-ON,
`probe_hcycles.period_of` (the R-87c/d validated detector: linear detrend, reject periods beyond window/3,
require a genuine local ACF maximum). Seed 0 incomplete. No source changed.

**ADDENDUM 19 — RETRACTION AND QUALIFICATION: the baseline trajectories used as a control were TWO DAYS
OLDER than the arms compared against them, so Addendum 12's headline and today's MARKER_MATRIX #14 claim both
measured CODE DRIFT, not the flags. Sixth instrument fault of the arc, fourth of them mine (2026-08-03).**

**How it was caught.** A solo ablation of `enable_wealth_obligation` was run to attribute the apparent
MARKER_MATRIX #14 movement. It came back NEGATIVE (`noble_material_lift` 1.248 → 1.183, −5%, 2/6 pairs up;
`leader_material_lift` 0/6 pairs up). But its BASELINE read **1.248**, where the battery6 baseline used an hour
earlier read **1.059** for the nominally identical configuration. That discrepancy — not the ablation result —
is the finding.

**PROVENANCE (checked by file mtime):**

| trajectory set | written |
|---|---|
| battery6 BASELINE `_b6_*` (used as the control all day) | **2026-07-29 00:21** |
| battery6 ALL-ON `_b6_allon_*` | 2026-07-31 10:30 |
| bisect baseline `_bx2000_base_*` (same-session control) | 2026-08-03 13:55 |

**Commits that landed between the control and the arms compared to it** include, verbatim from the log:
`4980344` **"THE WEALTH FIX: a feast is an EVENT, not a per-step bleed — and the elite now accrues wealth"**;
`4c1c90a` "Marker matrix: wire 14 markers that were computed every step and never recorded";
`ed8cb11` "Adopt the Marlowe polygyny calibration"; the entire 2026-07-30 R-106 demography arc
(`f2e839e` intake fertility, `3db3532` dependent load, `13bcb5b` Kaplan convex ramp, `676f37d`, `b15017e`);
and this session's own `a3e0b64`…`5204d75`.

**1. RETRACTED — the MARKER_MATRIX #14 claim.** Earlier today I reported `noble_material_lift` 1.059 → 1.228
(+16%, 24/25 pairs up) and called the project's "live open question" moved for the first time. **It is not.**
The same-code control run in this session gives baseline **1.248** against all-on **1.228** — no material
difference. The +16% is almost certainly commit `4980344`, whose own message states the elite now accrues
wealth. The marker moved because of a fix made on 2026-07-29, not because of the dark flags.

**2. QUALIFIED — Addendum 12's headline is NOT established.** "ALL-ON scores materially worse on 3 of 6
markers (connubium 13→3/25, lineage Gini 12→3/25, band 23→20/25)" compared the 07-29 baseline against the
07-31 all-on arms. Two days of substantive model change sit between them, including a demography overhaul that
directly touches fertility, mortality and lineage formation — precisely the quantities those markers measure.
**The comparison cannot separate flags from code drift, so the conclusion "the preset's curation is
load-bearing" is unsupported as stated.** Addendum 12's *method* corrections (the run-length truncation, the
tag fix) stand; its headline does not. Note the same-session bisect baseline (`band_med` 6/6, `connubium_med`
1/6, `lineage_size_gini` 1/6, `settle_med` 6/6) with groups added on top showed NO large degradation, which is
consistent with the flags being far less harmful than Addendum 12 claimed.

**3. CONFIRMED, and it agrees with the project's own prior finding.** The solo `enable_wealth_obligation`
ablation shows it does not concentrate durable wealth (−4 to −5% across three markers, 0–2 of 6 pairs up).
Commit `605000b` (2026-07-29) already recorded exactly this: *"Wealth → obligation → production (Sahlins), and
the finding that it is NOT sufficient."* An independent reproduction of a known negative — which is the one
clean thing to come out of this.

**THE LESSON, and it is the general one.** **Pre-existing trajectory files are not a control.** They carry no
record of the code that produced them, so any A/B that reuses them silently compares two different models. This
is the same failure as Addendum 12's un-suffixed scoring tags (which also silently read old files) and as the
bisect tags without a horizon — three variants of one mistake: *trusting a file's name instead of its
provenance*. **Any future A/B must run BOTH arms with the same commit, in the same session**, or verify the
commit that produced each trajectory. The campaign banner already prints `sha=` — that should be read back and
compared before any cross-run claim.

**Origin:** solo ablation via `B_SOLO` (`diag_bisect_allon.py`), material scoring via `score_material.py`
(scratchpad), provenance by file mtime and `git log --since`. No source changed. Retracts one claim made
earlier this session and qualifies Addendum 12.

**ADDENDUM 20 — BATTERY 7 (controlled): the full stack's ONLY large effect is band size +22%, and at long
horizon that pushes `band_med` OUT of its ethnographic band. connubium, lineage-Gini and top-share fail in
the CONTROL TOO, so they were never flag-caused. 7 mechanisms are genuinely inert (2026-08-04).**

**The instrument.** `battery7_controlled.py`, built after Addendum 19's retraction, enforces: same build (arms
carry `meta.sha`, a stage refuses to score if they disagree), same session (the control is produced here, never
read from a previous run), paired by (world, seed), matched horizon, and fail-loud on unknown flags. Run with
`C_SOIL=1 C_ABANDON=1` so the soil stack — the only slow variable, and absent from every previous battery
because `C_SOIL` defaults to 0 — is exercised for the first time.

**S1 — CONTROL vs FULL STACK (3 worlds × 2 seeds, 1200 steps, paired):**

| marker | control | full stack | delta | pairs up |
|---|---|---|---|---|
| **`band_med`** | 31.5 | **38.5** | **+22%** | **6/6** |
| `settle_med` | 58.5 | 53 | −9% | 3/6 |
| `connubium_med` | 66.25 | 52.75 | **−20%** | 1/6 (i.e. 5/6 DOWN) |
| `lineage_size_gini` | 0.4165 | 0.4035 | −3% | 3/6 |
| `lin_top_share` | 0.0105 | 0.010 | −5% | 1/6 |

**S3 — LONG (2500 steps requested; arms wall-clocked, common horizon 1625):**

| marker | band | CONTROL | FULL STACK |
|---|---|---|---|
| `band_med` | [18–35] | **2/2** (31..33) | **0/2 (37..38)** |
| `settle_med` | [50–150] | 2/2 (64..86) | 2/2 (80..95) |
| `connubium_med` | [79–332] | **0/2** (43..68) | 0/2 (70..77) |
| `lineage_size_gini` | [0.51–0.68] | **0/2** (0.385..0.42) | 0/2 (0.384..0.407) |
| `lin_top_share` | [0.08–0.30] | **0/2** (0.013..0.018) | 0/2 (0.011..0.016) |

**1. THE FLAGS BREAK EXACTLY ONE MARKER, AND IT IS `band_med`.** +22% in every pair at 1200 steps, and at the
long horizon that carries band size to **37–38 against Johnson's [18–35]** — inside the band under the control,
outside it under the full stack. This is the third independent measurement of the same effect (Addendum 17's
band/fission group at +14%, 6/6 pairs; battery7's first S1 at +23%, 6/6), now with a clean control and a
consequence: it is not a curiosity, it is a benchmark failure the mechanisms cause.

**2. connubium, lineage-Gini and top-share FAIL IN THE CONTROL.** All three score 0/2 with the canonical preset
alone. **They are baseline failures of the model, not costs of enabling mechanisms.** This finally closes the
question Addendum 12 opened and Addendum 19 qualified: Addendum 12 attributed a collapse in those markers to
the dark flags; the flags are not responsible, and never were. (The full stack even *improves* connubium's
range at long horizon, 43–68 → 70–77, moving toward the 79 floor without reaching it.)

**3. SEVEN MECHANISMS ARE GENUINELY INERT** — on, in the stack, and removing them changes nothing:
`enable_band_risk`, `enable_bonded_mating`, `enable_energetic_fertility`, `enable_malnutrition_fission`,
`enable_relative_resentment`, `enable_resentment_accumulator`, `enable_terrain_pathogen`. `energetic_fertility`
is expected and confirmatory — R-106 established it is inert by construction, superseded by
`enable_intake_fertility`. The other six are open defects. Four more (`adaptive_connubium`,
`ascribed_mate_choice`, `exogamy`, `improved_land`) were correctly reported NOT IN STACK rather than inert,
after the first S2 run scored 7 such verdicts invalid by ablating already-off flags.

**4. THE SOIL STACK IS LIVE.** With `C_SOIL=1`, both `enable_soil_depletion` and `enable_alluvial_renewal` read
LIVE. Previous batteries never tested them: `C_SOIL` defaults to 0, so the model's only slow variable had never
been in a battery stack at all. Addendum 18's Malthus runs did enable it (via a different harness), so its
measurements stand, but no benchmark result before this one exercised soil.

**INCOMPLETE:** S3 finished only 4 of 12 arms within the 25-minute-per-arm budget, so the long-horizon scores
above are coastal/temperate × 2 seeds only, at horizon 1625 rather than the requested 2500. The
control-vs-full contrast on `band_med` is consistent with S1's six pairs, but the pass fractions are
under-powered and the other two worlds are unmeasured. **Needs a re-run with a larger wall-clock budget before
the S3 numbers are quoted as an envelope.**

**Origin:** `sic_games/outputs/mechanism_battery/battery7_controlled.py` (commits e83c0c7, fde3e52),
`C_EXTRA_OFF` in `run_campaign.py`, build fde3e52. Supersedes Addendum 12's attribution entirely.

**ADDENDUM 21 — SEVEN CONFIGURATION DEFECTS, found by pointing the knobs at themselves. One killed a 24-arm
sweep silently; one means `C_ALLON=1` alone was never "all on"; one is a hole underneath the sha gate
Addendum 19 built; and one shows two liveness verdicts were coin flips (2026-08-04).**

None of these is an analysis error. Every one is a *"what was actually on?"* error — the class this arc keeps
paying for, and the reason `config/*.toml` exists. They are grouped here because they were all found the same
way: by asserting, in a test, what a knob claims to do.

**1. `C_PARAM` SHADOWED THE TERRAIN KNOBS.** The knob added yesterday parsed its arguments with

```python
for item in _pv:
    k, v = item.split("=", 1)
```

inside `main()`, where `k` had been bound 90 lines earlier to the terrain-knob dict. Every `C_PARAM` run
therefore died in the `TerrainWorld` constructor with a bare `'str' object has no attribute 'get'`. It was
found 24 arms into a `cv_safe` sweep whose every arm was dead — and the harness, which discarded stdout to
`/dev/null` and treated a missing trajectory as "no arms", **printed a tidy empty table instead of an error**.
Two fixes: the loop variables are renamed and commented, and the harness now raises with the failing arm's log
tail rather than reporting a sweep with missing arms as a result. `tests/test_campaign_knobs.py` (9 tests) now
drives the actual script as a subprocess and asserts the process EXITS 0 as well as that the value lands — the
original smoke test checked only that the value parsed, which is exactly what a run that dies 90 lines later
still does.

**2. `C_ALLON=1` ALONE WAS NEVER "ALL ON": ten mechanisms stayed dark behind their knobs' OFF defaults.**
`C_ALLON` skipped every flag that has a `C_*` knob, unconditionally, so a knob's *default* silently overrode
the supervisor rule. A bare `C_ALLON=1` left `adaptive_connubium`, `exogamy`, `ascribed_mate_choice`,
`material_inheritance`, `noble_leveling_exemption`, `lineage_tribute`, `lineage_branching`, `lineage_split`,
`improved_land` and `emergent_abandonment` off. The rule is now the intended one: **an explicitly set knob
wins (an ablation is respected), an unset knob does not (a default is not an ablation)**. A bare `C_ALLON=1`
goes from 28 to 38 enabled mechanisms and leaves exactly five off, and the campaign now ECHOES both lists at
launch. Flags whose magnitude knob defaults to zero (`lineage_branch_rate`, `lineage_split_rate`,
`ascribed_mate_strength`, `mate_search_min_eligible`) carry their validated value with them, so `C_ALLON`
cannot enable a mechanism into a no-op.

**3. `C_ALLON` ALSO SWITCHED THE ELITE LAYER ON AT ZERO STRENGTH.** The elite *flags* are not the elite layer:
its magnitudes live in `ELITE_KW`, which is empty unless `C_ELITE=1`. A bare `C_ALLON=1` therefore switched on
all twelve elite flags while a config dump from the same environment reads `leveling_strength=0.0`,
`leveling_share=0.0`, `material_hide_frac=0.0`, `material_decay=0.0`, `aggrandizer_frac=0.0`,
`leader_share_frac=0.0`, `legit_cred_gain=0.0`, `legit_feast_frac=0.0` — material capture, leader share,
leveling and legitimacy were on and completely dead. `C_ALLON` now implies `C_ELITE` unless `C_ELITE` is set,
and the elite block is governed as a unit so that `C_ELITE=0` is a REAL ablation (flags off) rather than a half
one (flags on, magnitudes 0) — the worst of both states, since the dump says the mechanism ran and the world
says it did nothing.

**Battery 7 was NOT affected by (2) or (3), and this was checked rather than assumed.** Its `STACK` sets
`C_ELITE=1` and fourteen other knobs explicitly. Read back from
`campaign_trajectory_b7_full_coastal_temperate_s0.json` (`meta.sha` `fde3e52`): **72 flags ON, 7 OFF**, with
`leveling_strength=0.79`, `material_hide_frac=0.07`, `legit_cred_gain=10.0`. Addendum 20's stack is what it
said it was. **What does change for it:** `C_ALLON` now enables `adaptive_connubium`, `exogamy` and
`ascribed_mate_choice`, three of the four mechanisms Addendum 20 correctly reported as NOT IN STACK — and
`connubium_med` failed there 3/25 **with the adaptive connubium switched off**. That marker must be
re-measured on the fixed stack before Addendum 20's connubium reading stands.

**4. `enable_band_risk` IS A MEASURED DEAD END AND WAS BEING SWITCHED ON AT GAIN ZERO.** `demography.py`'s own
comment records the F.2 prototype result — loner-mortality does not produce an optimal band size, it culls:
*"pop 281→64, mean band 56→5 ... a DEATH SPIRAL, not a stabilizing optimum ... KEEP OFF"*. Its only magnitude
`band_risk_penalty` is 0.0 and the code is guarded on `> 0.0`, so `C_ALLON` was enabling a no-op: "on" in the
dump, INERT in every ablation, and a death spiral at any value that would make it live. It is now excluded by
name, with the reason. **One of Addendum 20's seven "genuinely inert" verdicts is resolved as
correctly-excluded rather than defective.**

**5. THE SHA GATE HAD A HOLE UNDERNEATH IT: a DIRTY tree records the PARENT commit.** Addendum 19's fix was to
record `meta.sha` and refuse to score arms whose builds disagree. But `git rev-parse HEAD` does not identify a
build when the working tree has uncommitted edits — a run started from a dirty tree records the parent commit,
so the gate happily pairs it with a run of the committed code and calls them the same build. That is the same
failure, one level down. The campaign now records `meta.tree_dirty`, prints a loud banner when it is set, and
`battery6_long`, `battery7_controlled` and the sweep harness all treat a dirty arm as ABSENT, forcing a re-run.

**6. `divorce_rate` WAS UN-CALIBRATED IN THE BATTERY OVERLAY.** R-78 (`b8501ea`, 2026-07-17) calibrated it to
**0.005** against Hill & Hurtado Tab. 13.1, explicitly on both pairing paths (*"base 0.140 / village 0.149"*).
The `VILLAGE` overlay written ten days later (`46eb0c9`) listed `divorce_rate=0.004` with no rationale,
silently overriding the calibration for `battery1_liveness` and `battery6_stress` — and, because
`config/parameters.toml` is generated from that overlay, putting the wrong number in the authoritative file
while every campaign ran 0.005. Removed; the calibrated value stands and the files are regenerated.

**7. AND THE `divorce_rate` FIX EXPOSED A SEVENTH: two liveness tests were coin flips.** Changing
`divorce_rate` by 0.001, in an unrelated overlay, flipped
`test_intake_fertility.py::test_on_changes_the_world` from pass to fail — the intake-fertility branch became
*bit-identical*, i.e. it never fired at all. The mechanism is fine; the test's horizon was not. The brake only
bites below `intake_fert_hi = 1.20`, and the share of fertile women under that gate in the liveness world
measures **0.0% at step 60, 2.2% (three women) at 120, 7.3% at 180, 13.1% at 300** — so at the 120-step
horizon the verdict turned on whether one of three women happened to be drawn for a birth. The population
GROWS through that window (757 → 867), which is the root of it: a fertility brake needs scarcity, and the
small liveness world is rich. Both tests now run at 300 steps, the horizon at which the gate demonstrably
binds and the one the sibling EMA-spread test already used. **A liveness test whose verdict a 0.001 change
elsewhere can reverse is not evidence that a mechanism is live** — and this arc has been reading exactly such
verdicts.

**A ZERO-PARAMETER AUDIT, since (2)–(4) are all the same shape.** Under a bare `C_ALLON=1`, fifteen numeric
parameters are exactly 0. Six are INTENTIONAL and documented as such in their own provenance comments —
`maternal_mortality_per_birth` (folded into the all-cause female Siler by construction), `assortative_strength`
(R-80, prototyped and REVERTED as structurally inert), `pathogen_npp_ref` (0 ⇒ use the terrain mean),
`genome_mutation` (0 ⇒ pure drift / infinite-allele), `comove_footprint` (0 ⇒ exact snap),
`aggregation_rank_homogamy` (0 ⇒ directional only). The rest are open, and three of them are why a mechanism
reads INERT:

| parameter | flag it silences | status in its own provenance |
|---|---|---|
| `malnutrition_fission_gain` | `enable_malnutrition_fission` | "UNANCHORED" |
| `pathogen_gamma` | `enable_terrain_pathogen` | "0 = OFF/flat. **Sweep low/mid/high**" |
| `material_capture_frac` | the aggrandizer-capture half of `enable_material_capture` | no note — see below |
| `shock_rho` | the REGIME half of `enable_tier2_shock` | "[PROVISIONAL — sweep]" |
| `paternal_provision_frac` | the paternal channel of `enable_paternity` | "0 = pure B (no paternal feeding)" |
| `wife_quality_strength` | R-77's status→RS channel | built, never switched on |

`material_capture_frac` is the sharpest of these. Material production from hides is live
(`material_hide_frac=0.07`), but the branch that lets aggrandizers claim a share of the GROUP's durable output
— Hayden's actual move — is gated on `mat_frac > 0.0` and never fires, while `aggrandizer_frac=0.15` IS set.
So the elite runs have an aggrandizer population that captures nothing, and every noble/commoner material
gap in this arc was produced by inheritance, tribute and the leveling exemption alone. **This bears directly on
MARKER_MATRIX #14 (`noble_material_lift`)** and is recorded here as an open question, not fixed: no value for
it is anchored, and inventing one is not a calibration.

**Origin:** `run_campaign.py` (C_PARAM shadowing, C_ALLON knob table, C_ELITE implication, `band_risk`
exclusion, `meta.tree_dirty`), `battery1_liveness.py` (`divorce_rate`), `battery6_long.py` and
`battery7_controlled.py` (dirty gate), `test_intake_fertility.py` and `test_pressure_mobility.py` (horizon),
`config/parameters.toml` regenerated, and `sic_games/tests/test_campaign_knobs.py` — 9 new subprocess-level
tests that pin every claim above. Suite 1065 pass / 2 xfail. Qualifies Addendum 20 on `connubium_med` and on
one of its seven inert verdicts; supersedes nothing.

**ADDENDUM 22 — THE COHESION BUDGET HAS NO HEADROOM. `cohesion_frac` clamps at 1.0 for every band that has a
leader, so the band-fission threshold is EXACTLY `band_split_size`, and four mechanisms that feed it —
emergent band size, dynamic bands/assabiyah, size repulsion, malnutrition fission — cannot act on band size at
all. R-72's emergent band size is structurally inert, not mis-calibrated (2026-08-04).**

**WHAT WAS BEING FIXED.** Addendum 20 measured the full stack pushing `band_med` to 37–38 against Johnson's
[18–35], attributed additively to `enable_emergent_band_size` (+11.9%) and `enable_resource_directed_fusion`
(+9.7%). `cv_safe` is documented as *"the ONE fitted scale ... calibrated — but ONLY to place the MEAN band at
Hill 2011's ~25–30 (mean RETURN_CV 1.017 / 27.5 = 0.037)"*, and it was fitted for emergent band size ALONE.
Re-fitting it to its own anchor with the current stack looked like ordinary calibration maintenance.

**IT IS NOT, AND THE SWEEP SAID SO.** Four values, full stack, 3 worlds × 2 seeds, 1200 steps (common horizon
1020), paired by (world, seed), same build `77151e4`, same session:

| `cv_safe` | vs default | `band_med` median | range | paired Δ | in Johnson [18–35] |
|---|---|---|---|---|---|
| 0.037 (default) | — | 35.00 | 34.0–38.0 | control | 4/6 |
| 0.045 | +22% | 33.50 | 31.0–43.0 | −1.9%, 4/6 down | 4/6 |
| 0.052 | +41% | 34.50 | 32.0–36.5 | −3.5%, **6/6 down** | 5/6 |
| 0.060 | +62% | 33.00 | 31.0–34.0 | −8.4%, **6/6 down** | 6/6 |

The mechanism's own law is `g* = CV/cv_safe`, so band size should scale as `1/cv_safe`: **elasticity −1.0**.
Measured elasticity is **−0.14** — a seventh of the law, consistently signed but nearly inert. Reaching Hill's
27.5 at that elasticity would need `cv_safe ≈ 0.22`, a SIX-FOLD move in a constant the model calls calibrated.
That is not maintaining a calibration; that is fitting the model to the benchmark. **The re-fit is dropped.**

**WHY — measured, not inferred.** Instrumenting the model's own stored per-band state (`_band_assabiyah`,
`_band_leader_term`, `_band_repulsion`, `_band_malnutrition`) over 94 bands after 400 steps on the village +
elite stack:

```
  band size        min 10.0  p25 27.0  med 34.0  p75 47.0  max 98.0
  g* = CV/cv_safe  min 29.2  p25 37.5  med 38.2  p75 38.2  max 38.2
  split_thr        min 45.0  p25 45.0  med 45.0  p75 45.0  max 45.0     <- sd 0.00
  cohesion_frac    min 1.000 p25 1.000 med 1.000 p75 1.000 max 1.000    <- 94/94 pinned
    assabiyah      min 0.955 p25 1.000 med 1.000 p75 1.000 max 1.000
    leader term    min 0.409 p25 0.670 med 0.783 p75 1.255 max 1.641
    repulsion      min 0.001 p25 0.017 med 0.044 p75 0.075 max 0.150
    malnutrition   min 0.000 p25 0.000 med 0.000 p75 0.000 max 0.000
  raw (unclamped)  min 1.329 p25 1.576 med 1.718 p75 2.214 max 2.621
```

The threshold is `split_thr = g* + max(0, cap − g*) · cohesion_frac`, `cohesion_frac = clamp01(assabiyah +
leader − repulsion − malnutrition)`, `cap = band_split_size = 45`. Two independent causes each suffice to pin
it:

**(a) Assabiyah saturates BY CONSTRUCTION.** Its update is `a += gain·surplus − decay`, clamped to [0,1], so
its fixed point is `surplus_frac = decay/gain = 0.02/0.05 = 0.40`. Measured band `surplus_frac` runs
0.35–0.99, **median 0.69**, and **90 of 94 bands (95.7%) sit above the fixed point** — so assabiyah is not a
state variable at all, it is the constant 1.0. F.3c-3's premise (*"a rich, high-solidarity band STAYS TOGETHER
larger; a poor one fissions at the base"*) requires the band to be able to be poor; in this economy it cannot.

**(b) The leader term alone would do it.** It runs 0.409–1.641 with median 0.783, and it is ADDED on top of a
saturated assabiyah. The unclamped sum is 1.33–2.62 for every band — **33% to 162% above the clamp**.

**THE RULE, checked across horizons and two world scales.** The share of bands pinned tracks the share that
has acquired a leader, and at every checkpoint the unpinned bands are EXACTLY the leaderless ones: 0% pinned
at step 50 (no leaders yet), 68%/86% at 100, 88%/99% at 200, 96%/100% at 400 (n=1200 patch=30 / n=2500
patch=40). Assabiyah's median reaches exactly 1.000 by step 100 in both and never comes down. So the general
statement is *a leader term on top of a saturated assabiyah always exceeds the clamp* — the 100% figure above
is that rule evaluated in a mature world where every band has a leader, not a coincidence of one run.

**THE CONSEQUENCE.** With `cohesion_frac ≡ 1`, the threshold reduces to `max(g*, band_split_size)`. Measured
`g*` spans 29.2–38.2 and **0 of 94 bands have g* > 45**, so `split_thr` is exactly 45 for every band, sd 0.00.
`corr(g*, realized band size) = −0.077`. R-72 built v3 specifically because v1/v2 measured −0.22 and *"a
ceiling cannot pull a band together"*; v3 replaced the ceiling with a per-band centre and the correlation is
still −0.08. **Realized `band_med` ≈ 34 ≈ 0.75 × cap** — the sawtooth of grow-then-halve against a threshold
that is the same constant everywhere. That, and not the CV, is what sets band size.

**FOUR MECHANISMS FEED ONE SATURATED EXPRESSION.** `_band_repulsion` and `_band_leader_term` are stored but
read nowhere else (both are commented "diagnostic"), and `_band_assabiyah` is read only to update itself. So
`cohesion_frac` is the ONLY consumer of the repulsion, leader, malnutrition and assabiyah terms — and it is
clamped for every band. `enable_size_repulsion` (Johnson scalar stress), `enable_dynamic_bands`,
`enable_malnutrition_fission` and the Stage-1 leader-coherence term are therefore all structurally inert with
respect to band size, whatever their magnitudes.

This gives a QUANTITATIVE floor for the ones still awaiting anchors: **a malnutrition term must exceed 0.718 —
the median headroom — before it changes a single median band's threshold**, and 1.62 before it reaches the
largest. `malnutrition_fission_gain` is documented as a "max dispersion" scale and is currently 0.0; any
plausible small value calibrated in isolation would still read INERT here, and Addendum 20's inert verdict for
it would be reproduced by a correctly-calibrated mechanism. The same arithmetic applies to `band_risk_penalty`
(already excluded as a dead end, Addendum 21) and to `repulsion_gain`.

**WHAT THIS DOES NOT SAY.** It does not say `band_split_size = 45` is wrong — that constant is the Johnson
"upper community rung" and lowering it to land `band_med` on an anchor would be exactly the benchmark-fitting
refused above. It says the model currently has ONE lever where it was designed to have five, and that the
four dead ones are dead for a stated, measurable reason. The design question — whether assabiyah's clamp, its
`decay/gain` fixed point, or the leader term's scale is the thing to change so the budget regains headroom —
is a supervisor call, not a calibration.

**Incidentally, `band_med` improved on its own.** On the fixed stack of Addendum 21 the control reads 35.0
(4/6 arms in Johnson's band), against 38.5 on Addendum 20's stack. Turning the previously-dark mechanisms on
moved it about a third of the way back inside the band without touching a calibrated constant.

**Origin:** `sic_games/outputs/mechanism_battery/diag_param_sweep.py` and `diag_band_size_terms.py`, build
`77151e4`, 24 campaign arms plus in-process instrumented worlds (n=1200 patch=30 and n=2500 patch=40,
village+elite stack). Pinned as `sic_games/tests/test_cohesion_headroom.py` (5 blocker tests that FAIL when
the headroom is restored). No model source changed — this is a diagnosis, and the fix it implies is a design
decision. Supersedes the `cv_safe` re-fit proposed after Addendum 20; explains, mechanically, several of
Addendum 20's inert verdicts.

**ADDENDUM 23 — CORRECTION to Addendum 22, and the fix measured. The clamp does NOT make four mechanisms
inert; it kills the CONDITION-DEPENDENCE for the 91–100% of bands that have a leader, while the mechanisms
stay live on the unled remainder. An ablation therefore reads LIVE while the mechanism is swallowed for the
bands that matter — which is why the ablation audit could never have found this (2026-08-04).**

**THE CORRECTION.** Addendum 22 ended: *"`enable_size_repulsion`, `enable_dynamic_bands`,
`enable_malnutrition_fission` and the Stage-1 leader term are therefore all structurally inert with respect to
band size, whatever their magnitudes."* **That is wrong, and it is wrong in the direction of overstatement.**
Ablated one at a time out of the live stack, 2 seeds, 300 steps, 1500 agents:

| ablated | under the baseline | under the candidate fix |
|---|---|---|
| `size_repulsion` | **LIVE 2/2** | LIVE 2/2 |
| `dynamic_bands` | **LIVE 2/2** | LIVE 2/2 |
| `emergent_band_size` | **LIVE 2/2** | LIVE 2/2 |
| `malnutrition_fission` | inert 0/2 | inert 0/2 |

`malnutrition_fission` is the negative control — its gain is 0.0, so it must read inert under both, and it
does. The instrument is sound; the earlier claim was not.

**WHY THEY ARE STILL LIVE, AND WHAT IS ACTUALLY DEAD.** The clamp binds only where the leader term is
present. Measured share of multi-member bands that have a leader: **91.4% at step 150, 100% at step 300,
93.3% at step 500**. For those, `cohesion_frac ≡ 1`, `split_thr ≡ band_split_size` (sd 0.00), and the
repulsion, malnutrition and leader terms cannot move the threshold at all. On the unled 0–9% remainder,
cohesion is genuinely below 1 and every term acts — and `dynamic_bands` additionally gates the whole block
while `emergent_band_size` sets the threshold's base, so ablating either changes the world through those
paths regardless.

So Addendum 22's measurements all stand — the pinning, the sd 0.00, the assabiyah saturation, `corr(g*, band
size) = −0.077`, the `cv_safe` elasticity of −0.14. What was wrong was the inference from them.

**AND THE CORRECTED VERSION IS THE SHARPER METHODOLOGICAL POINT.** A mechanism can be LIVE by ablation and
still be swallowed where it was supposed to act. "Turn it off and see if the world changes" cannot
distinguish *"acts on 9% of bands"* from *"acts on all of them"*, so it certifies a mechanism that has lost
the population it was written for. This is the same shape as C.5 intercept hunting, which computes a correct
+28% boost on cells no agent stands on.

**A STRUCTURAL FINDING ABOUT ASSABIYAH, which Addendum 22 missed.** Its update is

    a += gain·surplus − decay          (clamped to [0,1])

— a pure integrator with a CONSTANT leak. That has **no interior fixed point at all**: if `gain·s > decay` it
climbs to the clamp and stays; otherwise it falls to 0. It is bang-bang *by construction*, and no choice of
gain or decay makes it graded — only the share of bands at each end changes. F.3c-3's premise ("a rich,
high-solidarity band STAYS TOGETHER larger; a poor one fissions at the base") needs a band to be able to be
poor, and this form cannot deliver that at any calibration.

Making the leak proportional to the level, `a += gain·s·(1−a) − decay·a`, gives the interior fixed point
`a* = gain·s/(gain·s + decay)`, which tracks surplus: 0.47 at s=0.35, 0.63 at the measured median 0.69, 0.71
at s=0.99.

**THE CANDIDATES, MEASURED.** Two flags, both default-off and bit-exact: `enable_leaky_assabiyah` and
`cohesion_leader_weight` (scales the leader's share of the budget; 1.0 = today). Coastal-temperate, 1500
agents, 300 steps, 2 seeds:

| candidate | headroom | median assabiyah | thr spread | corr(g*, n) | `band_med` |
|---|---|---|---|---|---|
| baseline | 0.0% | 1.000 | 1.0% | −0.073 | 30.2 |
| leaky | 3.4% | 0.607 | 3.4% | +0.124 | 25.8 ✓Hill |
| leader weight 0.5 | 0.0% | 1.000 | 1.0% | −0.073 | 30.2 |
| leader weight 0.25 | 0.9% | 1.000 | 1.0% | −0.073 | 30.2 |
| leaky + weight 0.5 | 64.8% | 0.603 | 1.8% | −0.058 | 29.0 ✓Hill |
| leaky + weight 0.25 | **100.0%** | 0.602 | 2.5% | −0.089 | 28.2 ✓Hill |
| leaky + weight 0.1 | 100.0% | 0.604 | 1.8% | −0.070 | 26.8 ✓Hill |

*headroom* = share of LED bands with `cohesion_frac` below the clamp. Three readings:

**1. The leader weight alone does nothing** (0.0% / 0.9%). Assabiyah is already at the clamp on its own, so
scaling the leader changes nothing until assabiyah is graded. Saturation is assabiyah's, not the leader's.

**2. Leaky alone is not enough either** (3.4%) — it makes assabiyah a state variable again (median 1.000 →
0.607) but the leader term then saturates the sum by itself. **Both are needed**, and that is a fact about
the expression rather than a tuning preference.

**3. It does NOT restore R-72's gradient.** `corr(g*, band size)` stays at −0.089 with the headroom fully
restored, against −0.22 for v1/v2 and −0.077 for v3. The clamp was not the only thing decoupling the CV from
realized band size: with cohesion at ~0.6, `split_thr = g* + (cap − g*)·0.6` gives g* only 40% weight, and the
grow-then-halve sawtooth around the threshold swamps what is left. **Restoring the headroom is not the same
as making band size emergent from the CV**, and the second still has no mechanism.

`band_med` incidentally improves — 30.2 → 26.8–29.0, i.e. from "inside Johnson" to "inside Hill 25–30" — but
that is a by-product, and adopting a fix *because* a marker moved is the benchmark-fitting refused throughout
this arc.

**NOTHING IS ADOPTED.** Both flags stay default-off and bit-exact. `enable_leaky_assabiyah` is a structural
correction with a stated rationale and is defensible on its own terms; `cohesion_leader_weight` is an
UNANCHORED fitted constant, and inventing one is what this arc has spent itself refusing to do. There is an
in-code precedent for the principled alternative — `rank_w` is already normalised to [0,1] by
`resent_effect_threshold` before it is combined — so normalising the leader term to its own reference, rather
than scaling it by a free parameter, is the obvious candidate to try next. That is a supervisor call.

**Origin:** `diag_cohesion_candidates.py` and `diag_cohesion_unlocks.py`
(`sic_games/outputs/mechanism_battery/`), build 5b91d2b, in-process instrumented worlds. Two new flags in
`DemographyConfig`, both default-off. Corrects Addendum 22's closing inference; every measurement in
Addendum 22 stands.

**ADDENDUM 24 — THE LONG-HORIZON ENVELOPE, complete for the first time: 16/16 arms at 2500 steps on the fixed
build. The full stack is NOT uniformly worse than the control — it FIXES two markers and BREAKS two — and the
connubium is now BRACKETED between the two arms, which makes it a calibration with an anchor on both sides
rather than an open failure (2026-08-04).**

**THE INSTRUMENT.** Battery 7 stages S1 and S3 on build `f77be6a` — the build carrying Addendum 21's
configuration fixes (`C_ALLON` reaching 38 mechanisms rather than 28, `C_ELITE` implied, the `tree_dirty`
gate), Addendum 23's corrections, the wired climate layer, and the savanna world. Four worlds
(coastal/flat/hilly temperate + **flat savanna**) × 2 seeds, paired, same build, same session. **All 16 arms
reached the full 2500 steps** — Addendum 20's attempt lost 8 of 12 to the wall-clock cap and its S3 numbers
were withdrawn as under-powered, so this is the first time the envelope has actually been measured.

| marker | band | CONTROL | FULL STACK |
|---|---|---|---|
| `band_med` | Johnson 18–35 | **7/8** (17.5–33) | 5/8 (19–39) |
| `settle_med` | Bar-Yosef 50–150 | 6/8 (21–122) | 6/8 (52–154) |
| `settle_med` | Alvard 50–250 | 6/8 | **8/8** |
| `connubium_med` | White MVP 79–332 | 1/8 (**8–89**) | 0/8 (**440–2387**) |
| `lineage_size_gini` | BHM 0.51–0.68 | 1/8 (0.411–0.532) | **8/8** (0.522–0.600) |
| `lin_top_share` | Karmin 0.08–0.30 | 1/8 (0.024–0.085) | 1/8 (0.011–0.124) |

**1. THE FULL STACK IS NOT A NET LOSS, which is a change from Addendum 20's reading.** It takes
`lineage_size_gini` from 1/8 to **8/8** — every arm inside BHM 2009's band, range 0.522–0.600 against a band
of 0.51–0.68 — and `settle_med` from 6/8 to 8/8 on Alvard's wider village band. Those are the two markers the
lineage and settlement layers exist to produce, and with the previously-dark mechanisms switched on they land.

**2. THE CONNUBIUM IS NOW BRACKETED, and that is the most useful single number here.** With the adaptive
connubium OFF (the control, `m* = 3`) the reach is **8–89**, below White's MVP band. With it ON at `m* = 50`
the reach is **440–2387**, overshooting by up to 7×. The band [79, 332] lies strictly between the two arms, so
`mate_search_min_eligible` has an anchor on BOTH sides — a genuine interpolation rather than an open failure.
This also surfaces an anchor conflict worth settling: `m* = 50` was calibrated to **Wobst's ~475 reach**,
which is a different quantity from White's minimum viable population, and both cannot be met at once.

**3. `lin_top_share` FAILS IN BOTH ARMS** — 1/8 either way, 0.011–0.124 against Karmin's 0.08–0.30, i.e. short
by roughly an order of magnitude at the low end. It is a BASELINE failure and was never flag-caused. Whatever
concentrates Y-lineages in Karmin 2015 is not in this model, and no configuration change in this arc has
touched it. That is the one marker with no route currently visible.

**4. `band_med` gets worse, and it is the cohesion clamp.** 7/8 → 5/8, the full stack reaching 39 against
Johnson's ceiling of 35, with the misses in coastal- and flat-temperate. This is the same +40% Addendum 22
attributed and Addendum 23 diagnosed: with `cohesion_frac` pinned, `split_thr` is the constant
`band_split_size = 45` and the realised median sits at ~0.75 of it. The measured candidate fix
(`enable_leaky_assabiyah` + a leader weight) puts `band_med` back to 26.8–29.0 in-process but is NOT adopted,
because the leader weight is an unanchored constant (Addendum 23).

**5. THE SAVANNA WORLD BEHAVES DIFFERENTLY, and it is the control's only `settle_med` miss** (21, far below
Bar-Yosef's floor of 50) and its only `band_med` miss. This is the first time the Hadza-anchored biome has
been in a battery at all — it was an explicit-only preset no harness had ever requested — so a divergence
there is expected and unexamined rather than a defect. It deserves its own look: most of the ethnographic
anchors in this project (Hadza band size, Hadza intercept hunting, the savanna return rates) come from
exactly this biome, so a world that fails `settle_med` there is worth understanding before the temperate
worlds are trusted as representative.

**Origin:** `battery7_controlled.py` stages S1+S3, build `f77be6a`, `B7_WORLDS` including `flat_savanna`,
133 min wall clock, 16/16 arms at horizon 2500. Supersedes Addendum 20's withdrawn S3 numbers. Confirms
Addendum 21's qualification that `connubium_med` had to be re-measured with the adaptive connubium switched
on — it was, and it overshoots.

**ADDENDUM 25 — CORRECTION to Addendum 24, twice over. There is no anchor conflict in the connubium (R-67
retracted the 475 three weeks ago and the CODE NEVER FOLLOWED), and `connubium_med` is TWO DIFFERENT
STATISTICS reported under one name — so Addendum 24's control-vs-full comparison put a pool-of-adults count
beside a population-within-reach count (2026-08-04).**

**PART 1 — THE PROPAGATION FAILURE.** Addendum 24 read the connubium overshoot as a conflict between two
anchors: *"m* = 50 was calibrated to Wobst's ~475 reach … and both cannot be met at once."* **Wrong on both
halves.** `LITERATURE.md` (2026-07-13) and RESULTS **R-67** had already settled it:

> Wobst's **Minimum Equilibrium Size** … his 40 simulation runs returned **MES = 79–332** — the commonly cited
> **175–475 is an *extrapolation*** … The earlier `mate_search_min_eligible` calibration to reach ~475
> (m* = 50) anchored to the contested max-dispersal extrapolation … **re-anchored to MVP (m* ≈ 15)**.

Wobst's real MES **is** the MARKER_MATRIX band, and White's MVP ~150 sits inside it. The anchors agree.

The defect is that the re-anchoring never reached the code. `run_campaign.py` kept
`MSTAR = int(os.environ.get("C_MSTAR", "50"))  # probe: m*=50 → median reach 496 ≈ Wobst` — the retired value,
with the RETRACTED anchor quoted in its own comment as justification, for three weeks. Fixed: default → 15,
with the retraction recorded at the point of use. Fourth instance of one shape; now **MECHANISM_CHARTER §11,
the propagation discipline**.

**PART 2 — AND THE MARKER IS TWO STATISTICS.** Prompted by the supervisor's question — *is the lit anchor
biome-specific, so could the model legitimately differ?* Wobst's MES is indeed density-dependent, but the
dominant effect is that `self._connubium_sizes` is appended from two places with two different quantities:

    phase1_model:3642   (Cut-1, gathering)   append(pool_n)      # distinct adults in the mating pool
    phase1_model:3719   (Cut-2, adaptive)    append(reach_pop)   # TOTAL POPULATION within the realized reach

`reach_pop` increments once for **every agent** in every cell of the expanding search ring — all ages, both
sexes. That is exactly Wobst's quantity, *"persons living in the intervening distance between two marriage
partners"*. `pool_n` is not. The class attribute declares only the first meaning
(*"distinct-adult size of each mating pool"*), so the name and the comment describe the Cut-1 statistic while
Cut-2 silently reports another.

**Consequences for Addendum 24, precisely:**
- the FULL-stack numbers (440–2387) ARE in the anchor's units and DO overshoot [79, 332] by 1.3–7×. **That
  finding stands.**
- the CONTROL numbers (8–89) are a pool-of-adults count and are **not comparable to the band at all**. Scoring
  them "1/8 in [79–332]" was a category error, and so was the conclusion that the band *"lies strictly between
  the two arms"* — the two arms are not measuring the same thing, so nothing was bracketed.

**WHY THE POOL REACHES 75% OF THE WORLD.** The ring expands until `len(eligible) >= m_star`, where eligible
means adult male, non-kin, exogamy-passing and not already at `max_wives`. Those are a small minority, so
finding 50 of them requires sweeping a large area, and `reach_pop` counts everyone swept. In `flat_savanna_s0`
(pop 1563, dispersed) that is 1168 people — 75% of everyone alive. Full-stack `connubium_med / pop` across the
eight long arms: 0.75, 0.73, 0.33, 0.17, 0.17, 0.13, 0.11, 0.11. **A mate-search catchment holding 11–75% of a
population is not a catchment**, and at m* = 50 it was guaranteed by arithmetic rather than by any biology.
With the default now 15 the reach should fall by roughly the same factor; that is measured, not assumed, and
is not yet done.

**AN OPEN TENSION, stated rather than resolved.** Wobst is explicit that the MES **SHRINKS as residential
units aggregate** — "a large village already contains the pool". Measured on the full-stack arms, where
`connubium_med` genuinely is the MES: `corr(connubium_med, density_per_km2) = +0.544`,
`corr(…, n_villages) = +0.572`. The model's reach RISES with aggregation. This is confounded — `n_villages`
also tracks total population, and `reach_pop` scales with the area that had to be swept — so it is not yet a
finding. Disentangling it needs a same-population, different-aggregation pair.

**WHAT IS NOW OPEN.** (a) Split the two statistics — a Cut-1 pool size and a Cut-2 reach are both worth having,
under different names, and only the second is scoreable against Wobst. (b) `MARKER_MATRIX` row 4 must say
which quantity it scores, since White's demographic pool and Wobst's spatial reach are different numbers with
different dependencies. (c) Re-measure the reach at m* = 15 before treating the re-anchor as verified.

**A PLANNED SWEEP WAS STOPPED BECAUSE OF THIS.** m* over 50/25/15/8 was running when the two-statistics
problem was found. It was killed rather than completed: half its arms would have reported `pool_n` and half
`reach_pop`, scored against one band. Reporting that would have been a D3/D4 failure dressed as a calibration.

**Origin:** `LITERATURE.md` 2026-07-13, RESULTS R-67, `MARKER_MATRIX.md` row 4,
`phase1_model.connubium()` and lines 3642/3719, and Addendum 24's 16 long arms re-read for composition and
density. Corrects Addendum 24's anchor-conflict reading AND its control-vs-full bracketing. `C_MSTAR` default
50 → 15 committed as the documented re-anchor; whether 15 is right is now OPEN, not closed.

**ADDENDUM 26 — MARKER #5's ANCHOR IS WITHDRAWN. The paper was read: BHM 2009 contains no lineage-size Gini.
[0.51–0.68] is its MATERIAL-WEALTH band, applied to a lineage-size distribution — the wrong QUANTITY, not
merely the wrong unit. And the quantity it does belong to, #14, reads about half the anchor (2026-08-04).**

**THE CHECK.** On the supervisor's instruction — *check the actual paper in the lit folder* —
`literature/borgerhoff-mulder.som.pdf` was read. It is the Supporting Online Material for Borgerhoff Mulder
et al., *Intergenerational Wealth Transmission and the Dynamics of Inequality in Small-Scale Societies*,
Science 326:682 (2009). Every Gini in it is a **wealth** Gini:

> Population- and wealth-type-specific Gini coefficients were calculated using the maximal sample of
> individuals … for whom **wealth** and age data were available … The Ginis were age-adjusted by regressing
> the raw data against a quadratic in age.

Forty-three **wealth types** across four economic systems. **Table S5**, the α-weighted averages:

| economic system | embodied | relational | **material** | α-weighted |
|---|---|---|---|---|
| hunter-gatherer | 0.21 | 0.24 | **0.36** | 0.25 |
| horticultural | 0.20 | 0.23 | **0.52** | 0.27 |
| pastoral | 0.20 | na | **0.51** | 0.42 |
| agricultural | 0.28 | 0.46 | **0.57** | 0.48 |

**There is no lineage-size Gini anywhere in the paper.** The band [0.51–0.68] is the MATERIAL column for the
stratified systems — 0.51 pastoral, 0.52 horticultural, 0.57 agricultural. It was borrowed onto a
lineage-size distribution, which is a different quantity, not a different unit of the same one.
`ELITE_STRATIFICATION_ROADMAP` also quotes two incompatible BHM ranges for this same marker — "0.51–0.68
(BHM stratified range)" at line 173 and "0.4–0.6" at line 190 — which is the tell that neither was traced to
the table.

**WHERE THE BAND ACTUALLY BELONGS — and it was already there.** MARKER_MATRIX **#14** reads *"wealth
concentration | `material_gini`, `material_top10_share` | BHM by society type | BHM 2009 (T-5)"*. So BHM was
cited for two markers and only #14 is the right one. Scored properly, against the **hunter-gatherer** row a
forager model has to answer to (material Gini **0.36**), the model reads:

    material_gini   median 0.162   range 0.131-0.185   (16 long arms, control and full)

**About half the anchor.** #14 was already flagged as "the live open question" — this puts a number on it and
identifies the correct band, which is 0.36 and not the stratified 0.51–0.68 that a mis-assigned row had been
suggesting. Note the model's `wealth_gini` (0.17 control → 0.30–0.46 full) is a *different* stock and is not
BHM's material class.

**AND #5 HAS A SEPARATE UNIT PROBLEM.** `lineage_size_gini` is a Gini over `_rank_keys()`, which under
`enable_local_ascription` — ON in the canonical stack — returns **(community, lineage) pairs**, so one
patriline fragments into one unit per community. `lin_size_gini`, in the same trajectory row, is the Gini over
`_lineage` itself. They differ in **16/16** long arms and the sign of the difference flips between arms:

| unit | control in the old band | full in the old band |
|---|---|---|
| rank-key (what was scored) | 1/8 | 8/8 |
| patriline | 6/8 | 4/8 |

So Addendum 24's "the full stack takes `lineage_size_gini` from 1/8 to 8/8" held only on the fragmented unit
and against a band that does not belong to the marker. **Both halves of that headline are withdrawn.**

**WHAT #5 NEEDS BEFORE IT IS SCORED AGAIN:** a decision on the quantity (is a lineage-size Gini a marker this
project wants at all, and against what source), and on the unit (patriline, or lineage-within-community).
Neither is inferable from the code, and neither should be settled by whichever choice scores better.

**THE GENERAL LESSON, which is charter §11 P5 with teeth.** The band survived because it was written as a
number with a citation and never as a traceable claim — no table, no column, no quantity. Reading the paper
took ten minutes and settled a marker that had been scored 17/25 for months. **A doc claim about a measurable
quantity names its measurement**, and "BHM 2009" is not a measurement.

**Origin:** `literature/borgerhoff-mulder.som.pdf` Table S5 and the Gini methods section, against
`MARKER_MATRIX.md` rows 5 and 14, `ELITE_STRATIFICATION_ROADMAP.md` lines 173/190, and the 16 long arms of
Addendum 24 re-read for `material_gini`, `wealth_gini`, `lineage_size_gini` and `lin_size_gini`.
MARKER_MATRIX row 5 marked NOT SCOREABLE; row 14 given its real band and the measured value.

**ADDENDUM 27 — THE ANCHOR-PROVENANCE SWEEP. Every marker's cited source checked against the actual paper in
`literature/`. Two sources are NOT IN THE FOLDER AT ALL (one of them scores 21/25), two bands are traceable
to a DIFFERENT paper than the one cited, one was withdrawn yesterday, and two verify verbatim (2026-08-04).**

**WHY.** Addendum 26 withdrew marker #5 after ten minutes with the actual PDF: BHM 2009's Ginis are wealth
Ginis and the band had been borrowed from its material-wealth column. The obvious question was how many of
the other fifteen rows cite a source without naming a table, a column or a quantity. This is that sweep — the
source PDF located in `literature/`, opened, and searched for the number.

| # | marker | band | cited source | verdict |
|---|---|---|---|---|
| 1 | `band_med` | 25 [18–35] | Johnson scalar stress | **MIS-ATTRIBUTED** |
| 2 | `settle_med` | 100 [50–150] | Bar-Yosef | **SOURCE NOT IN `literature/`** |
| 3 | `settle_med` | [50–250] | Alvard 2009 | **VERIFIED VERBATIM** |
| 4 | `connubium_med` | 150 [79–332] | White 2017 / Wobst MES | verified (R-67 already corrected it from the paper) |
| 5 | `lineage_size_gini` | [0.51–0.68] | BHM 2009 | **WITHDRAWN** (Addendum 26) |
| 6 | `lin_top_share` | 0.16 [0.08–0.30] | Karmin 2015 | **MIS-CITED — numbers are from two OTHER papers** |
| 8 | `bud_events` | 2–5×10⁻³ | Bandy 2004 | citation NAMES its derivation — the best-documented row |
| 9 | T-7 ordering | structure > productivity | Smith & Codding 2021 | **SOURCE NOT IN `literature/`** |
| 14 | `material_gini` | HG 0.36 … | BHM 2009 Table S5 | **VERIFIED** (Addendum 26) |

**#3 IS EXACTLY RIGHT, and shows what a good citation looks like.** `AlvardPaper2.pdf`: *"Yanomamö villages are
small compared to Lamalera, ranging from **50** or so up to **250** individuals."* The band is the sentence.

**#6 — THE NUMBERS ARE REAL AND THE CITATION IS WRONG.** Karmin 2015 is *"A recent bottleneck of Y chromosome
diversity coincides with a global change in culture"*; its quantities are Y-chromosome **effective population
sizes** and **coalescence dates** — "0.16", "0.08" and "0.30" appear nowhere in it. The band's numbers are in
the folder, in two other papers:

- **Yan 2014** (`yan2014_three_neolithic_super_grandfathers_PLoSONE.pdf`): the three star-like Neolithic
  clades *"encompass more than 40% of the present Han Chinese in total (estimated **16%** for Oα, 11% for Oβ,
  and 14% for Oγ)"*. **0.16 is Oα, exactly the marker's point value.**
- **Zerjal 2003** (`Zerjal et al. - 2003 - The Genetic Legacy of the Mongols.pdf`): the star cluster *"was
  present at high frequency: ∼**8%** of the men in this region carry it"*. **That is the 0.08 floor.**

So the band was assembled from Yan and Zerjal and filed under Karmin. **And it matters beyond the citation:**
both sources are POST-NEOLITHIC EXPANSIONS — an agricultural expansion in Neolithic China and the Mongol
empire. R-97 already concluded that Turchin's cycles are a state-scale phenomenon and *"we built the Kachin"*.
Marker #6 has been asking a forager/Kachin-scale model to reproduce the Y-lineage concentration of an empire,
and its 7/25 — the matrix's own "weakest" — is what that should look like. The 0.30 ceiling is traceable to
neither paper and remains unaccounted for.

**#1 — THE BEST-SCORING MARKER IS MIS-ATTRIBUTED.** `SiC_Games_D2_Johnson1982_OrgStructureScalarStress.pdf`
reports *"average camp size was 30.9 people, the range over the 28 days was **22-40** (SD = 5.4)"* for the
!Kung, and an organisational threshold *"in groups of approximately six individuals"*. It does not contain
[18–35] or a band-size band of any kind — Johnson's contribution is the scalar-stress curve, which is what
`repulsion_width` and the logistic FORM were taken from. `LITERATURE.md` says so itself: the ~25 *"rest[s] on
Wobst/Kelly/Hill"*, and the famous band ≈ 25 is Birdsell's 1968 *Man the Hunter* chapter. So #1's band comes
from real sources — just not the one on the row. Johnson's own **22–40** would be a defensible and better-
traced alternative, and the model scores differently against it (2500-step arms: control 17.5–33, full 19–39).

**#2 AND #9 CANNOT BE CHECKED AT ALL.** Neither Bar-Yosef nor Smith & Codding 2021 is in `literature/`. #2 is
not a minor row: `settle_med` against [50–150] scores **21/25** and is one of the two markers Addendum 24
reported the full stack fixing. Its band is currently unverifiable from anything in this repository.

**WHAT THE SWEEP SAYS ABOUT THE MATRIX AS A WHOLE.** Of nine rows with a numeric band and a named paper:
2 verify, 2 are mis-attributed with the real numbers elsewhere in the folder, 1 is withdrawn, 2 have no source
present, and 2 (#8 Bandy, #15 Hill & Hurtado) name their derivation well enough to be trusted without
re-reading. **The rows that survived are the ones whose citation named a table, a page or a sentence.** Every
row that failed cited only an author and a year.

That is charter §11 P5 turned into an acceptance criterion: **an anchor names its table, or it is not an
anchor.** A number with an author-year beside it has, on this evidence, about a one-in-three chance of coming
from that author.

**NOT RE-CHECKED HERE:** #10 (Marlowe polygyny — the PDF's page extracts as a garbled table; the marker was
already corrected once, 15× → 1.0×), #11 (von Rueden, verified during R-77/R-80), #15 (Hill & Hurtado, cites
Table 13.1 explicitly), #7 (`ascribed_frac`, band never documented, not scored), #12/#13 (Johnson rank-size —
conceptual, ≈−1.0 and ≈1 are definitions rather than measurements).

**Origin:** `literature/` read directly — AlvardPaper2, Genome Res.-2015-Karmin, yan2014_three_neolithic_
super_grandfathers, Zerjal et al. 2003, SiC_Games_D2_Johnson1982, borgerhoff-mulder.som — against
`MARKER_MATRIX.md`. No model code touched.

**ADDENDUM 28 — THE THREE FETCHED PAPERS, READ. Smith & Codding verifies verbatim. Hill 2011 contains NO
LINEAGE DATA, which retracts the replacement anchor proposed for #6 one turn earlier. And Hill's real number
— band size in ADULTS — shows the model's bands hold 11.8 adults against 28.2, failing 16/16, while
`band_med` "passes" 23/25 because it counts children the model has too many of (2026-08-04).**

**#9 SMITH & CODDING 2021 — VERIFIED VERBATIM.** *"among the 17 CAL groups with maximum fish harvest scores …
the correlation between HI and RI was nearly as high (**r = 0.766, n = 17**) as for the full sample
(**r = 0.881, n = 89**)"*. Exactly as `LITERATURE.md` recorded it. The `[VERIFIED]` tag was honest; only the
PDF was missing. #9's source is now filed and confirmed.

**#6's PROPOSED REPLACEMENT ANCHOR IS RETRACTED — Hill 2011 has no lineages in it.** One turn ago this log
recommended retargeting #6 from whole-population `lin_top_share` to band-level `dom_lineage_share`, anchored
to *"Hill 2011: dominant-lineage share 0.38, ~7 lineages/band"* as carried by `MODEL_SPEC` §4.8.8, `TARGETS`
and `PARAMETERS` (where `rank_hierarchy_frac = 0.15` is DERIVED as ~1/7 from it). The paper is now in the
folder and **the string "lineage" occurs ZERO times in it**. Its unit is the co-residence of *primary kin* —
brothers, sisters, parents, offspring — not descent groups. The three occurrences of "0.38" are cells in
Table 1: the Nunamuit and Hadza co-residence values, and a column average. **There is no dominant-lineage
share and no ~7-lineages-per-band in Hill et al. 2011.**

That is the fourth mis-attribution this sweep has found, it was recommended in this log as the *fix* for the
third, and it propagates further than the others — `rank_hierarchy_frac = 0.15` rests on the 1/7.

**WHAT HILL 2011 ACTUALLY GIVES, verified:** 32 societies, and

> mean experienced band size = **28.2 adults** … the mean total number of co-resident adult primary kin per
> band is only **1.8** … most individuals in residential groups are **genetically unrelated**

**AND THAT NUMBER BREAKS MARKER #1, in the units it is stated in.** Hill's 28.2 is **ADULTS**. The model's
`band_med` counts everyone. Converting across the 16 long arms of Addendum 24 with each arm's own
`frac_child`:

| | model band_med (all ages) | frac_child | **adults per band** | vs Hill 28.2 |
|---|---|---|---|---|
| control, median | 26.0 | 0.60 | **10.7** | 0.38× |
| full stack, median | 32.5 | 0.59 | **13.3** | 0.47× |
| **all 16 arms, median** | | | **11.8** | **0.42×** |

Range across arms 0.29×–0.58×. **Not one arm reaches even 60% of Hill's figure.** Meanwhile `band_med` scores
**23/25** against [18–35] — the matrix's best row — because it is an all-ages count measured against a band
whose provenance Addendum 27 already showed is not Johnson's.

**The two findings are one finding.** MARKER #4/#5 records the demographic engine as running far too young:
`frac_child` **0.59** against the ~0.40 anchor, median age 12.8 against ~20, e₀ 21.4 against ~28. A band of 27
people that is 60% children holds 11 adults. **The band-size pass is being carried by the excess children.**
Fix the demography and `band_med` falls out of [18–35] from below unless adult band size roughly doubles.

So #1 should be scored on **adults**, against Hill 2011's 28.2 — a traceable, in-folder, 32-society figure —
and on that basis the model fails it 16/16 rather than passing it 23/25.

**#2 BAR-YOSEF 1998 — STILL NOT VERIFIED, now for a better reason.** The PDF is filed and read. Its treatment
of size is archaeological and comparative: sections titled *"Site Size and Settlement Pattern"* and *"Site
Size, Intrasite Variability, and Settlement Pattern"*, and the one quantitative statement in the extracted
text is relative — *"The largest Neolithic sites … are at least **three to eight times larger** than the
largest Natufian sites."* **No population figure appears anywhere in the extracted text**: no "100–150", no
"dozens", and a regex for "N to M people/persons/inhabitants" matches nothing. `LITERATURE.md` had already
conceded the position — *"Status: SEARCH-VERIFIED (PDF not filed)"* — and its own note derives the band's
floor from the project rather than the paper: *"should let villages LAND in ~50–150 — checked in run A, not
pre-tuned"*.

**CAVEAT, stated because it is the honest limit of this check:** PDF text extraction does not recover figures
or embedded tables, and this is a 19-page review article. A site-size figure may exist that this method cannot
see. #2's band should be treated as UNVERIFIED — not disproven — until someone reads the figures.

**THE SWEEP'S TALLY, after three fetches.** Of the markers with a numeric band and a named paper: **3 verify**
(#3 Alvard, #9 Smith & Codding, #14 BHM), **4 are mis-attributed** (#1, #5, #6, and #6's proposed replacement),
**1 remains unverified with the PDF in hand** (#2). Every verified one cites a sentence or a table. Every
failed one cites an author and a year.

**Origin:** `literature/hill2011.pdf`, `literature/baryosef.pdf`,
`literature/smith-codding-2021-....pdf` (all added by the supervisor 2026-08-06), read directly; the 16 long
arms of Addendum 24 re-read for `band_med` × `frac_child`. Retracts this log's own prior recommendation for
#6. No model code touched.

---

**ADDENDUM 29 — THE ANCHOR SWEEP EXTENDED TO THE CLIMATE LAYER AND TO THE CONFIG ITSELF. Four climate anchors
opened for the first time: three verify, one does not exist in the paper it is credited to. Village sizes turn
out to be well anchored after all — the row that looked unanchored was the redundant one — and the LARGEST
village is the marker that actually misses. And the parameter-provenance gap reported one turn ago was mostly
an artefact of the generator that reports it (2026-08-06).**

Prompted by the supervisor's read of Bar-Yosef ("mostly maps and burial sites") and the two questions it
raised: is there a village anchor at all, and what else has never been checked. Worked in three tiers.

---

### TIER 1a — the climate anchors, checked against the PDFs for the first time

The C.2–C.5 channels were wired on 2026-08-04 and every number in them was transcribed from a code comment or
a web survey. `tools/verify_anchor.py` now extracts each source PDF and searches it for the number the code
claims. Four sources were in the folder; a fifth is not.

| anchor | verdict |
|---|---|
| **Sarmiento 2004** — llanos flood-year ANPP | **VERIFIED VERBATIM.** The table reads `Total ANPP (*) 236±36 265±38 428±71 601±58` / `(**) 352±45 418±43 601±82 659±68` for grazed/ungrazed 1996 vs 1997. The ungrazed ratios 265/601 and 418/659 give **−56%** and **−37%** — exactly the range the code quotes. Arithmetic reproduced, not just the digits |
| **Wanner 2008** — regime amplitude | **VERIFIED VERBATIM:** EMICs *"simulate relatively modest changes during the period AD 1000-1850, with peak to peak variations in the order of 0.5 C"*. Note that is **peak-to-peak over the millennium**, not an LIA-vs-baseline anomaly. The °C→CC% step was already tagged interpretive in `LITERATURE.md` and now is in the code too |
| **Hawkes 1991** — intercept hunting | **VERIFIED VIA A DOCUMENTED CONVERSION.** 745 and 518 are *not in the paper* — it reports **mass**. Table 2's kg/hr column gives encounter/scavenge all-seasons **0.71** and night intercept **1.02**, with footnote a fixing the denominator: *"mean number of hours spent by adult men in day-time foraging was about 4.5 hours … We use this number to calculate an hourly rate."* The return-rate table's LOCKED constants (0.50 × 1460 = 730) convert them to **518.3** and **744.6**. Exact to the unit |
| **Timmermann 2018** — ENSO **period** | **VERIFIED, as a SYNTHESIS of two printed bands.** EOF1 is *"quasi-quadrennial timescales (3-7 years)"*; EOF2 is quasi-biennial, and the eigenmode section pins the pair at *"timescales of approximately four and two years, respectively"*. So our [2, 7] is the union of the two observed modes — defensible, but a union and not a quotation, and now labelled one |
| **Timmermann 2018** — ENSO **amplitude** | **RETRACTED. THE NUMBER IS NOT IN THE PAPER** |
| **St. John 2022** — caribou swing | **UNSOURCED. NO PDF EXISTS IN `literature/`** |

**THE ENSO AMPLITUDE WAS NEVER TIMMERMANN'S.** `LITERATURE.md` recorded *"±20–40% CC swing in marginal biomes
→ `interannual_amp`"* and `climate.py` carried `ENSO_AMP_MIN, ENSO_AMP_MAX = 0.20, 0.40  # Timmermann 2018`.
Timmermann 2018 is an **SST-dynamics review**. It discusses ENSO amplitude only qualitatively — skewness,
*"a wide range of amplitudes"* in palaeo-reconstructions — and states **no production or carrying-capacity
amplitude anywhere in the text**. This is the Bar-Yosef pattern reproduced exactly, in code two days old,
written after the sweep that found Bar-Yosef.

The value is retained and **retagged `[INTERPRETIVE]`**, which is the treatment its sibling `REGIME_AMP`
(Wanner's ±10–15%) has carried since it was written. It is **bounded, not anchored**: Sarmiento measures
−37…−56% in an *exceptional* flood year, and an ordinary interannual excursion must be milder than an
exceptional one, so [0.20, 0.40] sitting below [0.37, 0.56] is coherent. That is an argument for the bracket,
not a source for the number, and the code now says so.

**ST. JOHN 2022 IS THE BAR-YOSEF CASE AGAIN, WITHOUT THE PAPER.** The caribou amplitude 0.871 and the 40–90 yr
period rest on an M.Sc. thesis that is **not in the folder**. The only caribou paper we hold is Usher 2022,
which `LITERATURE.md`'s own entry explicitly *rejects* for this purpose as a category error. The channel is
default-OFF in both `ClimateConfig` and `mechanisms.toml`, so nothing in the canonical stack rides on it, and
`test_anchor_provenance.py` now **fails if it is ever defaulted ON while the row reports UNSOURCED**.

**Also corrected, a P5 drift in my own week-old work:** `LITERATURE.md`'s St. John entry said *"C.4b, NOT yet
wired"*. C.4b was wired on 2026-08-04, by me, and tested live. The doc had not moved with the code.

---

### TIER 1b — village sizes ARE anchored. The unanchored-looking row was the redundant one

The supervisor's finding on Bar-Yosef closes marker **#2**, and closing it costs nothing:

- **#2 RETIRED.** 100 [50–150] on `settle_med`, sourced to a paper with no village-population figure in it.
  It was a **second band on the same field as #3**, whose band is verified. Retiring it removes an
  unverifiable number and loses no measurement.
- **#3 STANDS and re-scores well.** Alvard 2009 [50–250], verified verbatim. Re-scored over every trajectory
  on disk (52 arms): **46/52 pass**, median of arm medians **97.5**.

Two further sources were verified verbatim and both land on the same scale:

- **Alberti 2014:** *"a critical scalar stress threshold at community size 127 (95% CI: 122–132), while the
  maximum probability of critical scale stress is predicted at size 158 (95% CI: 147–170)"*
- **Hamilton 2007:** aggregated group **53.66 [49.86–58.29]** (n=297), periodic aggregation
  **165.32 [152.25–181.00]** (n=213)

**AND SCORING ALBERTI AS A BAND WOULD HAVE BEEN THE FOURTH INSTANCE OF THIS PROJECT'S UNIT-MISMATCH BUG.**
The tempting move — add `settle_med ∈ [122, 132]`, the CI is beautifully tight — is wrong, and would have
scored **0/52**. **127 is the size at which a community starts to come apart.** A population whose *median*
village sat there would be permanently mid-fission. What Alberti bounds is the **ceiling**, so the field is
`settle_max` and the test is one-sided. Same family as `hayden_stage` on occupied-vs-regional density,
`lineage_size_gini` on rank-keys-vs-patrilines, and `connubium_med` on `pool_n`-vs-`reach_pop`. **All four
were real numbers read against the wrong denominator, unit or statistic — never wrong numbers.**

**NEW MARKER #17 — THE FISSION CEILING, AND IT MISSES.** Scored correctly against `settle_max` over the same
52 trajectories:

| | median `settle_max` | arms over Alberti's 158 | arms over Alvard's 250 |
|---|---|---|---|
| 52 trajectories | **220** | **39/52** | **18/52** |

**The typical village is right and the largest one is not.** `settle_med` ≈ 98 sits comfortably inside the
ethnographic band while `settle_max` ≈ 220 routinely exceeds the size at which both Alberti (scalar stress)
and Alvard (ethnographic maximum) say communities break up. That is not a contradiction between #3 and #17 —
it is the diagnosis: **fission fires, but not hard enough at the top of the distribution.** A single "village
size" verdict would have averaged the two into a meaningless pass.

**#17 is a SCREEN, not a score.** The 52 arms were run for other purposes, across different worlds, lengths
and flag stacks, several predating the R-105 and R-106 fixes. They establish direction and that the marker is
worth wiring; they do not size the miss. That needs a proper campaign.

**#6 remains unanchored.** Smith & Codding was fetched and verifies, but for #9's ordering claim, not for a
lineage share. No forager-scale lineage-concentration source exists in the folder. Retire or leave visibly
broken — the supervisor's call.

---

### TIER 2 — the provenance gap was mostly the generator, not the parameters

One turn ago this log reported *"245 parameters, 26 PROVISIONAL, 18 ANCHORED, ~200 with no provenance tag at
all"*. **That number was wrong, and wrong in the direction that flatters nobody: it overstated the gap.** Two
measurement defects, both in the instrument rather than the model:

**(1) `gen_runconfig.py` harvested only the comment TOUCHING each field.** The config classes are written in
channel blocks — one comment carrying the anchor, then the flag and the two or three parameters it governs:

```
# [Wanner 2008] LIA global mean ~0.5 C => central +-10-15% CC; duration 100-500 yr ...
enable_regime_shift: bool = False
regime_amp: float = Field(0.0, ...)          <- documented to a human, "UNDOCUMENTED" to the generator
regime_duration: int = Field(0, ...)         <- same
```

Only the flag sat directly under the comment, so only the flag inherited it. **18 of the 25 "undocumented"
parameters were documented in the line above their own.** The generator now inherits the channel note
(tagged, so a field-specific note is still distinguishable) and falls back to the class docstring **only when
the docstring names the field** — a blanket fallback would dress an undocumented field in its neighbours'
prose and hide a real gap.

**(2) The audit's own classifier tested `ANCHORED` before `UNANCHORED`.** One string contains the other, so
16 parameters that **honestly declare they have no literature source** were counted as anchored. The first
corrected run read 31 ANCHORED; the true figure is 15. A clean sweep produced by a substring.

Both bugs are now constructed-truth tests in `test_provenance_coverage.py`. CLAUDE.md's first rule applies to
an audit exactly as it applies to a diagnostic.

**The corrected picture, 244 parameters:**

| class | n | % |
|---|---|---|
| ANCHORED | 15 | 6% |
| PROVISIONAL | 25 | 10% |
| UNANCHORED (explicitly declared) | 16 | 7% |
| CITES-A-YEAR, untagged | 88 | 36% |
| COMMENTED, no source | 100 | 41% |
| **UNDOCUMENTED** | **0** | **0%** |

**59% now declare a source or declare that they have none**, and nothing is silent. The actionable backlog is
the **88 that name a paper-and-year but carry no tag** — they are the cheap expansion of the
`verify_anchor.py` registry, because the citation is already there and only the tag is missing.

**The one real gap was `CarbonConfig` — and reachability answered it better than provenance would have.**
9 of its 10 fields had no comment anywhere, and none of the names appear in `PARAMETERS.md` either. Before
writing provenance, the reachability was checked: **`phase1_model.py` imports neither `oracle.py` nor
`joint_task.py`**, so **five of the nine cannot be reached from any campaign run** — `cred_decay` and
`velocity_tau` (Oracle only), `matthew_alpha`, `epsilon` and `cred_bonus_per_participant` (joint-task only).
Chasing literature anchors for those would have been effort spent on the wrong five. Each field is now
labelled LIVE or DEAD at its point of use, and the generated config carries the label.

---

### TIER 3 — all six named open parameters are INERT, and that is the finding

`pathogen_gamma`, `shock_rho`, `material_capture_frac`, `paternal_provision_frac`, `wife_quality_strength`
and `cohesion_leader_weight` were checked against their neutral values:

```
pathogen_gamma           0.0   neutral 0.0    INERT
shock_rho                0.0   neutral 0.0    INERT
material_capture_frac    0.0   neutral 0.0    INERT
paternal_provision_frac  0.0   neutral 0.0    INERT
wife_quality_strength    0.0   neutral 0.0    INERT
cohesion_leader_weight   1.0   neutral 1.0    INERT   (bit-exact today)
```

**Every one sits at its no-op value, so none has ever affected a campaign.** That reframes the backlog: it is
not a correctness risk to the current stack, it is a set of unexercised mechanisms. It also separates two
things that had been filed together — `wife_quality_strength` **already has a lit anchor** (von Rueden &
Jaeggi, r = 0.19, cited in full at its point of use). Its gap is **adoption**, not anchoring. Only
`pathogen_gamma` (Cashdan 2014, comment reads "Sweep low/mid/high") and `shock_rho` ([PROVISIONAL — sweep])
are genuinely waiting on a run.

---

### WHAT IS NOW CODE RATHER THAN PROSE

- **`tools/verify_anchor.py`** — extracts each source PDF and searches it for the number the code claims.
  Three honest states: VERIFIED, INTERPRETIVE (our judgement, informed by the paper but not printed in it),
  UNSOURCED (no PDF). 12 rows registered, 0 unaccounted for.
- **`tools/audit_provenance.py`** — provenance coverage over the generated config, with the class order that
  the substring bug made load-bearing.
- **`sic_games/tests/test_anchor_provenance.py`** (17 tests) — fails the suite if any wired number stops being
  findable in its own source; pins the ENSO retraction; reproduces the Hawkes conversion from the paper's own
  kg/hr; constructs the per-session-vs-per-hour unit error the Hawkes table invites; and keeps the caribou
  channel OFF while its source is unfilebound.
- **`sic_games/tests/test_provenance_coverage.py`** — a ratchet. Coverage may rise and may not fall, and both
  audit bugs are constructed cases.

**The rule this arc keeps re-learning, now in three places:** a citation that names an author and a year is a
promise, not a provenance. Every row that survived a check named a table, a page or a sentence. Every row that
failed named only an author and a year — Bar-Yosef, BHM, Hill 2011, Timmermann's amplitude, St. John.

---

**ADDENDUM 30 — ADDENDUM 28's RETRACTION NEVER REACHED THE CODE. Three live parameters were still citing Hill
2011's nonexistent lineage target two days after it was retracted, and one of them derives its value from it.
Found by the provenance audit of Addendum 29, which was not looking for it (2026-08-06).**

Charter **P3** — *a retracted anchor is edited at its point of use* — was written on 2026-08-04 in response to
the Addendum-28 retractions. It was being violated by those same retractions at the moment it was written.

**HOW IT SURFACED.** The Tier-2 audit grouped the 88 untagged-but-citing parameters by cited source, purely to
size the registry backlog. **`Hill 2011` came back with five hits.** Addendum 28 had established two days
earlier that the word *"lineage"* occurs **zero times** in Hill et al. 2011. Opening the five showed the
retraction had been written into `RESULTS.md` and `MARKER_MATRIX.md` and nowhere else.

**WHAT WAS STILL STANDING IN `demography.py`:**

| parameter | what the comment still said |
|---|---|
| `lineage_branch_rate` | *"breaks the FILED Hill-2011 target of ~7 lineages/band + dominant-lineage share 0.38 that R-25 already passed"* |
| `rank_hierarchy_frac` = **0.15** | *"0.15 is ~1/7: the FILED Hill 2011 target is ~7 lineages per band … tied to a target the model already carries rather than picked freely"* |
| `legit_threshold` = 0.15 (R-93 note) | *"that boundary is 6.67, against a Hill 2011 target of ~7 — a FIVE PERCENT margin"* |

**`rank_hierarchy_frac` is the one that bites.** Its comment presents 0.15 as **derived** — the reader is told
it was *"tied to a target the model already carries rather than picked freely."* There is no ~7. It is a free
parameter that has been reading as a derived one for as long as the comment has existed, and R-93's "five
percent margin" argument is a margin against nothing.

**A SECOND, DIFFERENT FAMILY in the same five.** `band_cohesion` / `band_split_size` / `band_merge_size` and
`cv_safe` cite Hill 2011 for band size **~25 all-ages**. That number *does* have a paper behind it, but the
paper's quantity is **28.2 ADULTS** — the all-ages reading is the mis-attribution Addendum 28 identified.
`cv_safe` is explicitly *"calibrated … ONLY to place the MEAN band at Hill 2011's ~25–30"*, i.e. **fitted to a
quantity in the wrong unit.** The R-106 re-fit against the corrected adults target was attempted earlier in
this arc and **falsified** — the mechanism cannot reach 28.2 adults from this direction — so the fit is left
standing and the target is now labelled. An honest, documented mismatch beats a second fit to a wrong unit.

**NOTHING WAS RE-VALUED.** Every one of these is left at its current number and labelled `[UNANCHORED]` with
the reason. Re-deriving `rank_hierarchy_frac` or `legit_threshold` is a calibration decision requiring runs and
a supervisor call, not a documentation fix, and `enable_rank_hierarchy` is default-OFF in any case. The
R-90/R-92/R-93 *reasoning* is untouched by the retraction and stays: an absorbing lineage process really does
fixate at probability 1, and a threshold on a share really does have a hidden denominator. Only the **number
those arguments were aimed at** turns out not to be a literature target.

**NOW ENFORCED — `sic_games/tests/test_retraction_propagation.py`.** For each retracted claim, any source file
still mentioning it must also carry the retraction marker. The claim may stay (the surrounding reasoning is
usually sound and deleting it would lose the history); it may not stand unqualified. Registered: Hill 2011 as
a lineage source, Timmermann 2018 as the ENSO amplitude source, St. John 2022 as a filed source. The guard
includes a constructed violation, because a check that can only pass is not a check — and on its first run it
caught a defect in **itself**, splitting on the bare parameter name and landing in the new warning block
instead of the field declaration.

**THE PATTERN, STATED PLAINLY.** Every retraction this arc has produced was recorded in the log that produced
it and left live at the point of use. Bar-Yosef, BHM, Hill 2011, Timmermann's amplitude. **A retraction that
lives only in RESULTS.md is a note, not a correction** — the next person to read the parameter reads the
comment, not the log. The docs are downstream of the code, and the code is what runs.

---

**ADDENDUM 31 — TWO DEAD KNOBS DELETED, THE CLIMATE LAYER SWITCHED ON BY DEFAULT, AND A PER-CHANNEL HEALTH
DIAGNOSTIC THAT FOUND THREE DARK CHANNELS ON ITS FIRST REAL RUN. Also: the regime telegraph is correctly
anchored and STRUCTURALLY UNABLE TO ACT at our run lengths — it fires in ~13% of a standard campaign
(2026-08-06).**

Supervisor directive: *"kill all dead knobs, turn on the climate channels — wire them with diagnostics of
healthy functioning and benchmark on a well characterized case."* The procedure now has a name — **CTB
(Constructed-Truth Benchmark)** — defined at the end of this entry.

---

### 1. THE DEAD KNOBS ARE DELETED, AND THE DELETION EXPOSED A WORSE BUG

**`enable_infanticide`** — a declared flag that **no line of code ever read**. Three separate audits had to
re-discover that and write "UNIMPLEMENTED STUB" beside it; `C_ALLON` carried a special case to skip it; two
mechanism batteries carried an entry explaining it. A switch that does nothing is not documentation, it is a
standing invitation to believe the mechanism exists. The science it encoded is unchanged and lives in R-74's
`enable_orphan_mortality`, which is built, anchored and ON.

**`enable_band_risk` + `band_risk_penalty` + `band_risk_size`** — not a stub; a **measured dead end** with real
implemented code. Loner-mortality does not produce an optimal band size, it culls: fewer people → lower density
→ smaller bands → more loners → more penalty (run_3i: penalty 0→6 took pop 281→64 and mean band 56→5). Its gain
defaulted to 0.0 behind a `> 0.0` guard, so **the flag could read ON in a config dump while the mechanism was
inert — it passed a whole ablation battery as a fake positive.** Its only two reachable states were "does
nothing" and "kills the population". Recoverable at commit `daa7194`; the `run_3i` prototype went with it,
because a script that can no longer run is the same kind of lie as a flag that does nothing.

**THE BUG THE DELETION FOUND, WHICH IS BIGGER THAN EITHER KNOB.** `DemographyConfig` **silently ignored unknown
keyword arguments** — pydantic's default. So deleting `band_risk_penalty` would have made every harness that
still passed it run happily *without* it: the run succeeds, the manifest looks right, the setting is absent.
That is precisely the failure this entire audit arc has been chasing, sitting one line away from being
impossible, and **the cleanup itself would have been the trap.**

`model_config = ConfigDict(extra="forbid")` on `DemographyConfig` and `ClimateConfig`. A stale or mistyped field
now raises. Three harnesses were passing the deleted fields and were repaired rather than left to no-op.

---

### 2. CLIMATE IS ON BY DEFAULT. THE CONTROL IS NOW A CHOICE, NOT AN INHERITANCE

`C_CLIMATE` flipped from opt-in to opt-out. Five channels run by default — seasonality, eccentricity mean,
ENSO interannual, the regime telegraph, the llanos flood — plus the lottery that draws their per-world values.
`C_CLIMATE=0` still reproduces the pre-2026-08-06 flat world exactly, and that arm is now what a climate
ablation compares against. **A control has to be chosen, not inherited by default**, and the old default meant
the entire variability layer sat out every experiment this project ran while reading as built.

**One channel stays off, by name and with a reason: `enable_caribou_swing`.** Its amplitude (0.871) and period
(40–90 yr) are credited to an M.Sc. thesis that is not in `literature/` (Addendum 29). Not a control and not
"not needed" — **unverifiable**. Turning it on would put an unsourced number into every result. File the thesis
and delete one line.

---

### 3. THE HEALTH DIAGNOSTIC, AND WHAT IT FOUND IMMEDIATELY

A climate channel fails in three ways that are **indistinguishable in a config dump**:

| | what it looks like | what it is |
|---|---|---|
| `OFF` | flag false | not asked to act |
| `UNREACHABLE` | flag true, **mask empty** | cannot touch a cell at any amplitude |
| `NEVER-FIRED` | flag true, mask populated, **run shorter than the channel's clock** | asked to act, never got the chance |

The third is the one nothing in this project could previously see. `ClimateField.health()` now reports, per
channel, its reach in cells, how often it actually moved the field, and its measured extremes — **seven scalar
evaluations per STEP, not per cell**, carried in every checkpoint and printed to the run log only when the set
of complaints changes.

**First real run (coastal-temperate, the campaign default), step 25:**

```
~~ climate: intercept=UNREACHABLE, llanos=UNREACHABLE, regime=NEVER-FIRED
```

**Three of six channels dark on the default world.** llanos and intercept are UNREACHABLE because a temperate
coastal world contains neither llanos nor savanna — biome-dependence, exactly as the standing rule says: *a
mechanism validated in one world is a claim about that world.* On a **savanna** world both come alive
(llanos reach 200 cells, intercept 4499), which is the correct behaviour and confirms the masks are wired.

**THE MEASURED EXTREMES EQUAL THE CONFIGURED AMPLITUDES — the diagnostic and the seeding align:**

| channel | verdict | reach | measured extreme | expected from the config |
|---|---|---|---|---|
| season | LIVE | global | min **0.221** | 1 − a_seas(0.779) = 0.221 ✓ |
| eccentricity | LIVE | global | **1.1228** flat | the drawn mean_factor ✓ |
| interannual | LIVE | global | min **0.7484** | 1 − ENSO amp(0.25) = 0.75 ✓ |
| llanos | LIVE | 200 cells | min **0.6989**, active **100%** | 1 − 0.30 = 0.70, two-sided ✓ |
| intercept | LIVE | 4499 cells | max **1.4382**, active **33.5%** | **745/518 = 1.4382** exactly, late-dry only ✓ |
| caribou | OFF | 0 | — | excluded, unsourced ✓ |
| regime | **NEVER-FIRED** | global | — | see below |

The intercept row is worth pausing on: **the Hawkes anchor verified from the PDF this morning is now measured
coming out of a live run, to four decimal places.**

---

### 4. THE REGIME TELEGRAPH IS ANCHORED CORRECTLY AND CANNOT ACT AT OUR RUN LENGTHS

Not a bug — a **structural mismatch between the literature's timescale and ours**. The recurrence is anchored to
Bond ~1500 yr (Mayewski RCC), drawn over 1000–2000 yr. A standard campaign is 2500 steps = **208 years**.

| run | years | P(≥1 regime onset) at 1000 / 1500 / 2000 yr recurrence |
|---|---|---|
| 400 | 33 | 3.3% / 2.2% / 1.7% |
| **2500** | **208** | **18.8% / 13.0% / 9.9%** |
| 5000 | 417 | 34.1% / 24.3% / 18.8% |
| 12000 | 1000 | 63.2% / 48.7% / 39.3% |
| 30000 | 2500 | 91.8% / 81.1% / 71.3% |

**A standard campaign sees the slow driver about one run in eight.** Reaching a coin-flip needs ~12,500 steps
(1,040 yr); reaching 90% needs ~41,000 (3,450 yr).

This matters directly for the cycles question. Turning the regime channel on does **not** by itself put a slow
environmental variable into a secular-cycle test — at 2500 steps it mostly puts a *flag* into one. The three
honest options are (a) run 5–16× longer, (b) drive it deterministically with the `regime_driver` /
`ClimateDriver` hook that §4.1.9 already built for exactly this, or (c) accept it as a rare-event driver and
say so. **(b) is the right instrument for a controlled test** and costs nothing to adopt.

Shortening the recurrence to make it fire is the one thing that must not happen: it is the anchored number.

---

### 5. **CTB — CONSTRUCTED-TRUTH BENCHMARK.** The procedure, now named

> **Build a world whose answer you already know. Measure it with the real diagnostic. Verify the measurement
> returns what you built.**

Named at supervisor request. It is CLAUDE.md's first rule with a handle, and it applies to a mechanism, a
diagnostic, a map, a population, or an audit — anything where a measurement could be believed without being
checked. `sic_games/tests/test_climate_health_ctb.py` is the reference implementation: each of the four
verdicts is constructed explicitly, so the instrument is shown to distinguish them rather than assumed to.

**THE CTB EARNED ITSELF THREE TIMES IN ONE SITTING, ALL THREE DEFECTS IN THE INSTRUMENT:**

1. **`OFF` was decided from the observation, not the config** — so "you never switched it on" and "you switched
   it on and it never fired" collapsed into one verdict, the exact distinction the diagnostic exists to draw.
   Caught within a minute of the instrument being written.
2. **A brightening channel reported a value it never took.** min/max were seeded at the neutral 1.0, so
   `eccentricity` — always ~1.12 — reported `min 1.0`. Depressions hid the bug because for them 1.0 genuinely
   is the ceiling. Found by *reading a real run's output*, then constructed as a test.
3. **An unreachable channel reported a fictional magnitude.** On the temperate world the block read
   `llanos: verdict UNREACHABLE, reach 0, active_frac 1.0, min 0.699` — the verdict right, and the numbers
   underneath describing a depression applied to **zero cells**. Detail that looks like corroboration is worse
   than a bare wrong answer, because it invites someone to quote the 0.699.

**Every one was a defect in the measuring instrument, not the model** — which is the entire argument for the
procedure. A diagnostic is not a neutral window onto a run; it is code, and it is wrong until it is checked
against something whose answer is already known.

---

**ADDENDUM 32 — THE CARIBOU THESIS ARRIVED AND FALSIFIED HALF OF WHAT WE HAD CREDITED TO IT. Plus: the
ON-but-dead gate, which caught two more flags advertising mechanisms that could not act; and the config files
can now SET a run instead of only describing one (2026-08-06).**

---

### 1. THE CARIBOU ANCHOR — one confirmation, three corrections

`[UNSOURCED]` for one morning (Addendum 29); the supervisor filed it the same afternoon. **Reading it was not
a formality.**

**St. John, Jack R. (2022), "Understanding Caribou Population Cycles", University of Montana ScholarWorks.**

| | what we carried | what the thesis says |
|---|---|---|
| **amplitude** | 0.871 about the mean | ✅ **CONFIRMED** verbatim — *"the amplitude, standardized about the mean population size, was .871"* |
| **period band** | **40–90 yr**, credited to Bergerud | ❌ **FALSIFIED.** Figure 9: `Min=23, Q1=33, Median=40.5, Q3=50, Max=67`. **Bergerud is not cited in the thesis at all** (zero occurrences) |
| **sample** | "43-herd database" of cycles | ❌ **OVERSTATED.** *"of the 43 herds, I only 19 were deemed cyclic via periodogram analysis"* — **56% of the database is not cyclic** |
| **status** | M.Sc. thesis | ❌ **UNDERGRADUATE thesis** (ScholarWorks: *Undergraduate Theses, Professional Papers, and Capstone Artifacts*). Not peer-reviewed |

**The period band was wrong on BOTH ends.** It excluded everything below the median (Min 23, Q1 33) and ran 23
years past the longest cycle ever measured, so nearly every drawn world got a period longer than the median
herd. **Corrected to the observed 23–67**, and the correction is pinned by a test so a future edit back toward
40–90 fails.

**Both figures are MEDIANS of wide distributions**, not constants:
```
period     Min=23   Q1=33    Median=40.5  Q3=50     Max=67      (years)
amplitude  Min=.406 Q1=.700  Median=.871  Q3=1.126  Max=1.570
```

**⚠ A HAZARD THE DISTRIBUTION EXPOSES, found before anyone could hit it.** `_caribou_factor` is peak-pinned
`(1 + a·cos)/(1 + a)`, whose trough is `(1−a)/(1+a)` — **negative for a > 1**. The thesis's Q3 (1.126) and Max
(1.570) are both above 1, so **half the observed herds sit above the value at which our form breaks**. Pinning
the median is safe; a per-world draw from this distribution would silently produce negative meat. Constructed
as a CTB case so the clamp is a known requirement rather than a future bug report.

**Channel switched ON** (boreal world: reach 4794 steppe cells, drawn period 584 steps = 48.7 yr, inside the
corrected band). The campaign's `_CLIMATE_UNSOURCED` exclusion set is now **empty**, which was the point of
naming it.

**The general lesson, third instance today: fetching the paper is not a rubber stamp.** Bar-Yosef had nothing.
Timmermann had the period and not the amplitude. St. John had the amplitude and not the period band. **In every
case the number that survived was the one someone had actually read, and the number that failed was the one
that came with an author-and-year and no page.**

---

### 2. THE ON-BUT-DEAD GATE — two more flags advertising mechanisms that cannot act

**Closing R-85's residual (task #23).** R-85b explained all six inert flags on 2026-07-18 and left a decision
list of seven zero-magnitude knobs. **Five have since been given values** (`leader_coherence_gain` 2.0,
`repulsion_gain` 0.3, `village_gain` 5.0, `move_cost_kcal` 750, `site_gain` 0.3). Two had not:

| flag | magnitude | status |
|---|---|---|
| `enable_terrain_pathogen` | `pathogen_gamma = 0.0` | **ON-but-dead in the canonical config** |
| `enable_malnutrition_fission` | `malnutrition_fission_gain = 0.0` | **ON-but-dead in the canonical config** |

Both read as live mechanisms in every config dump throughout this entire audit arc.

**`enable_condition` is NO LONGER dead-downstream** — R-85b found its only consumer was the zeroed pathogen
term, but `enable_nutrition_synergy` is now ON and reads `a._condition` directly. That chained finding is
resolved.

**Neither got an invented value.** `pathogen_gamma` has a real anchor (Cashdan 2014) and its own comment says
*"sweep low/mid/high"* — the sweep has never been run, and picking a number without it is the exact sin this
arc documents. `malnutrition_fission_gain` was **deliberately** zeroed as the R-106 negative control and
behaved correctly as one; the mistake was leaving the FLAG on rather than the gain at zero. Both are now
excluded by name in `C_ALLON` under §12 **UNDER EVALUATION**.

**Now structural, not an audit finding.** `runconfig.dead_flags()` generalises `climate.py`'s `need()` refusal
to demography, and `run_campaign.py` checks the FINAL config before a single step runs:

```
campaign: ON-but-dead mechanism(s) in the final config:
  enable_terrain_pathogen is ON but pathogen_gamma=0.0 — the mechanism cannot act
  Turn the flag off to ablate, or give the magnitude a value.
```

**You ablate by turning the FLAG off, never by zeroing the magnitude** — zeroing leaves the flag advertising a
mechanism that is not running. This bug class produced 3 of battery 7's 6 "inert" verdicts, cost R-85 an entire
follow-up study, and let `enable_band_risk` pass a whole ablation battery as a fake positive before it was
deleted this morning. It is now a run-halting error.

---

### 3. THE CONFIG FILES CAN NOW SET A RUN (task #24, step B)

**The asymmetry that existed until today.** `tools/gen_runconfig.py` produces `config/*.toml` by *executing*
`run_campaign.py` with `C_ALLON=1` and recording the resolved config. So the files were a faithful **record**
of a run with no power to **cause** one — "edit the file and you get that run" was not true, and nothing told
a reader otherwise.

`C_CFGSRC=files` makes the file the base configuration, with `C_PARAM` / `C_EXTRA_ON` / `C_EXTRA_OFF` still
applying on top so ablations stay expressible.

**MEASURED EQUIVALENCE, which is what makes it safe: the file and a `C_ALLON=1` run agree on all 279 fields,
zero differences.** Loading the file reproduces the canonical arm exactly rather than approximately, and a
test pins it.

**WHAT WAS DELIBERATELY NOT DONE, and why it is the supervisor's call.** `preset` remains the default. A
**plain** run and the file differ in **52 fields** — the entire elite layer (leveling, legitimacy, leader
share, material capture, rank hierarchy, resentment), village budding, soil depletion, improved land, intake
fertility, adaptive connubium, lineage branching and split, and ~30 others are OFF in a plain run and ON in the
file. Flipping the default would silently convert every ad-hoc run, probe and quick check into the full
canonical stack.

That is arguably what "nothing stays off" implies, and it may well be right — but it changes what every
existing invocation of the script does, which is a scientific decision rather than a refactor. The gap is
pinned as a measurement (`test_the_default_is_still_the_preset_path_and_differs_from_the_file`) so it cannot
drift unnoticed, and that test is the one to invert when the call is made.

---

**ADDENDUM 33 — THE BENCHMARK LADDER, AND FOUR TIERS CLIMBED IN ONE NIGHT. The mortality curve is right and the
turnover is not; marker #1 is two faults on two tiers; the canonical world contains no savanna, so the best-
verified anchor in the project never enters a run. Three instrument defects found, two of them mine, one of
them in the ladder itself (2026-08-07).**

Supervisor principle: **benchmark behavioural groups in the order they appear in evolution**, not by size or
novelty. Adopted as `docs/BENCHMARK_LADDER.md`. It changed a decision immediately — the `noble_*_lift` block
had been proposed as the next CTB target because it was the largest uncovered one, and it is **tier 12, the
top of the ladder**, while both known failures sit at tiers 3 and 5.

---

### TIER 2 — ENERGETICS. The anchors are right; the world does not contain one of them

**What verifies.** Game return rates hit their anchored means exactly across seeds — forest 5,541 (Hill 1987),
grass 3,001 (Hurtado & Hill 1987), desert 995. Forage needed a qualifier: it **overshoots** on any coastal
world (desert reads 1332 against 1200) because the Bird 1997 shore bonus (1491.5, **additive**) is applied
*after* the per-biome rescale. Measured off-shore the targets hold exactly.

**THE FINDING: `coastal-temperate`, the campaign's default world, contains ZERO savanna cells.** So

- **Hawkes 1991's savanna game rate, 518 kcal/hr** — verified against the PDF to the unit on 2026-08-06, one
  of the best-provenanced numbers in the project — **never enters the canonical run**;
- nor does the intercept-hunting boost (745/518), which is savanna+llanos gated.

That is exactly why `ClimateField.health()` has been reporting `intercept=UNREACHABLE` and `llanos=UNREACHABLE`
on every temperate run since it was built. **The channels are not broken. The world has no savanna in it.** On
a savanna world the same anchor lands at 518 within 2%.

**VERIFIED, IMPLEMENTED and REACHABLE are three separate claims**, and this is the first time the third has
been measured. Which worlds can exercise the savanna layer is now pinned: savanna and tropical yes, temperate
and boreal no.

---

### TIER 3 — DEMOGRAPHY. The standing diagnosis was wrong

`test_age_structure.py` has said for weeks that the pyramid is young because *"people die in early
adulthood"*, which implicates the Siler schedule. **It does not.** Integrated, that schedule gives
**e₀ = 36.5 yr** against the Aché forest-period ~37, and its survivorship shows no early-adult collapse at all
(S(30) = 0.54, S(45) = 0.43). The anchored life table is fine, and a fix aimed at it would have been aimed at
the wrong thing.

The stable age structure the model's **own** curve implies is a one-parameter family in the growth rate:

| r (%/yr) | frac < 15 | median age |
|---|---|---|
| 0.0 | 0.307 | 26.5 |
| 1.0 | 0.377 | 21.5 |
| 2.0 | 0.446 | 17.5 |

The Aché anchor (0.40 / ~20) sits at r ≈ 1.3 %/yr — so the target is internally consistent with the life
table, which makes it a fair one.

**Measured: r = +0.67 %/yr with frac_child = 0.571 and median age 12.3.** At that growth the curve implies
~0.35 and ~23. **The model is outside the family its own mortality can produce**, and no forager growth rate
closes it.

**Where the difference lives.** Births run **5.66 %/yr** (crude birth rate ~57/1000 against a forager norm of
40–45) and **starvation deaths alone run 3.80 %/yr — larger than the entire anchored life table**, whose crude
death rate at this structure is ~2.7 %/yr. Starvation is outside the life table, so the realised mortality
regime is the anchored one *plus a bigger unanchored one*. High births and high deaths together are a
**high-turnover regime**, and turnover is what makes a pyramid young.

This is the ladder's *"an anchor verified is not a mechanism validated"* corollary arriving as an empirical
result.

---

### TIER 4 — MOVEMENT. A real hazard, and two failed attempts to guard it

`mobility_radius` implements Kelly/Binford correctly: monotone in productivity, base stride at the reference,
the closed form matching hand-computed points, the floor bounding an empty cell, and OFF returning base for
every value (the bit-exactness guarantee every pre-R-39 result rests on).

**The hazard.** It takes two pressure sources — NPP in g/m²/yr and an intake requirement RATIO — and its
docstring put the burden of matching them on the caller. Both mismatches are silent and fail in **opposite**
directions:

- `source="intake"` fed an NPP value → stride pins to `base` → **inert while reading ON**
- `source="npp"` fed an intake ratio → stride pins to `max` → **Kelly/Binford exactly inverted**

**I tried to guard it twice and both guards were wrong.** Rejecting small values under `"npp"` broke four
existing tests within a minute — an arid or near-water cell genuinely has NPP below 20 g/m²/yr, which is what
`mobility_npp_floor` exists for. Rejecting large values under `"intake"` broke two more — a well-fed agent
genuinely reads an intake ratio of 27. **The scales overlap across their whole useful ranges.** No threshold
separates them.

So the hazard is **documented, not fixed**. A guard that fires on legitimate input gets switched off and takes
the sound half with it. The existing tests catching both bad guards is the CTB discipline working on my own
change.

---

### TIER 5 — BANDS. Marker #1 is two faults on two tiers

Applying the ladder's rule — *a failure at tier N is diagnosed at tier N or below* — to #1 (`band_med` fails
16/16 on adults, 11.8 against Hill's 28.2):

| | adults/band |
|---|---|
| measured (band 23.0 all-ages, frac_child 0.589) | **9.4** |
| same band, Aché child fraction 0.40 → **tier 3 fixed** | **13.8** |
| Hill 2011 anchor | **28.2** |

**Fixing tier 3 closes about a quarter of the gap and no more.** The residual — 13.8 against 28.2 — is a
genuine **tier 5** fault: the bands are too small. To hold 28.2 adults at the measured child fraction a band
would need **69 people** against the 23 produced; even with a perfect Aché pyramid it would need **47**. Both
tiers have to move, and neither is diagnosable at tier 9 or above, which is where most recent attention went.

It also explains why #1 "passed" 23/25 on the all-ages unit for so long: **23 people sits inside Birdsell's
~25 and Marlowe's 25–50**, so the body count looks right. It *is* right, as a count of bodies. Hill counts
ADULTS, and the model reaches that total only by including children it should not have.

---

### THE THIRD INSTRUMENT DEFECT WAS IN THE LADDER

Its **CTB column undercounts**. It is a filename heuristic (`*_ctb.py`, `*_ground_truth.py`), and genuine
constructed-truth tests live in ordinarily-named files —
`test_bands.py::test_bands_method_connected_components` hand-places five agents and asserts `bands()` returns
the partition `[1, 2, 2]`, which is textbook CTB in a file the heuristic scores as zero.

The error can only undercount and is roughly uniform across tiers, so the prescribed **ordering stands**. But
no tier should be called "uncovered" on that column alone. It now reads *"has no dedicated CTB file"*.

The ladder's tier membership had also drifted **before it was committed** — the first draft invented five
flags that do not exist and missed eight that do, including `game` and `forage_cap`, which are tier 2, the
very next thing to benchmark. A hand-maintained list of 86 names is a second copy, so Charter P4 applies and
`test_benchmark_ladder.py` now checks it against the config classes.

---

### THE NIGHT'S SCORE ON INSTRUMENTS VS MODEL

Three defects found in **instruments** (two unsound mobility guards, one ladder heuristic) and two genuine
**model** faults located and decomposed (the turnover regime, the band-size shortfall). Both surviving marker
failures from 2026-08-06 (#14 wealth, #17 fission ceiling) had already been CTB'd and held.

Configuration is now a file per run (`--config`), so every arm above was launched from a named, fully-resolved
config with a stated reason for differing.

---

**ADDENDUM 34 — THE REGIME TELEGRAPH FIRED. The overnight long-climate arm passed 844 model years and the slow
environmental driver acted for the first time in this project's history; the health diagnostic tracked it
through all three of its states, and both live channels reproduce their configured amplitudes to the fourth
decimal (2026-08-07, overnight).**

The arm: `config/runs/long_climate.toml`, 30,000 steps capped at 7 h, launched from a clean tree at `04d0724`
under the new `--config` path — the first campaign in this project configured by a named file rather than by
environment variables.

### The telegraph fired, and the instrument caught the transition

`ClimateField.health()` reported the regime channel in three successive states as the run advanced:

| model years | verdict | what it means |
|---|---|---|
| ~30 | `NEVER-FIRED` | configured, reachable, clock never came round |
| ~500 | `RARE` | fired, active on <1% of steps |
| **844** | **`LIVE`** | active 2.0% of steps, trough **0.8608** |

That is the diagnostic doing exactly what it was built for on 2026-08-06 — distinguishing "not switched on"
from "switched on and never got a chance to act" — and it is the first time the distinction has been observed
resolving in a live run rather than constructed in a test.

**The prediction held.** Addendum 31 computed that at ~1500 yr recurrence the telegraph fires in ~13% of a
standard 2500-step campaign and needs ~12,500 steps for a coin flip. It fired between step 2,500 and 10,000,
which is the middle of that range.

### Both live channels reproduce their configured amplitudes exactly

| channel | configured | measured trough |
|---|---|---|
| regime | amp 0.14 → 0.860 | **0.8608** |
| caribou | a = 0.871 → (1−a)/(1+a) = 0.0689 | **0.069** |

The caribou figure is the anchor corrected yesterday when the supervisor filed the thesis — its peak-pinned
form, reproduced in a live 844-year run on 5,474 steppe cells.

### And the tier-2 finding is visible in the same block

`intercept` and `llanos` remain **UNREACHABLE** at 844 years, on every checkpoint, for the reason tier 2
established: `coastal-temperate` contains **no savanna**, so the sub-biome those channels need does not exist
in this world. Not a defect, not a clock problem — an absent biome. A run of any length will report the same.

### Status

The arm is still running at ~10,200 of 30,000 steps and will stop at its 7 h cap. Full suite green at
**1300 passed, 2 xfailed** across the whole night's work.

---

**ADDENDUM 35 — THE CARIBOU HERD CYCLE PACES FORAGER POPULATION AT ITS OWN PERIOD. Attributed by ablation, not
inferred from a coincidence: the oscillation signature vanishes when the channel is switched off, and the
channel depresses mean population by 32%. The first environmental driver this project has attributed to a
population response (2026-08-08).**

### The observation

`long_climate` (30,000 steps = 2,500 model years, completed in 86 min) showed population autocorrelation that
**does not decay monotonically**. It dips to a trough and rises again to a local peak at **lag 23 = 47.9 yr**.
The caribou period drawn for that world was **584 steps = 48.7 yr** — a 1.6% match.

**That is a coincidence until tested.** A driver's period matching a response's periodicity is not evidence it
caused it, and this project's recent history is mostly of such inferences failing.

### The ablation

`long_climate_no_caribou.toml` — identical in all 315 settings except `enable_caribou_swing = false`,
authored by `tools/make_runconfig.py` with the reason recorded in its `[meta]`. This is the first experiment
in the project where "identical except one thing" is a checkable property of two files rather than a claim.

| lag (yr) | caribou **ON** | caribou **OFF** |
|---|---|---|
| 8.3 | +0.658 | +0.826 |
| 20.8 | +0.344 | +0.739 |
| **25.0** | **+0.314** ← trough | +0.721 |
| 37.5 | +0.486 | +0.672 |
| **47.9** | **+0.560** ← peak | +0.632 |
| 62.5 | +0.383 | +0.585 |
| 83.3 | +0.344 | +0.516 |

**ON: a trough at 25 yr and a peak at 48 yr.** A trough at half the period and a peak at the period is the
textbook autocorrelation signature of an oscillation, and 25.0 is half of 48.7 to within the checkpoint
spacing.

**OFF: smooth monotonic decay** from +0.83 to +0.52 across the same range. No trough, no local peak — ordinary
persistence in a slowly drifting population.

**The oscillation is the caribou channel.** Switch it off and the periodic structure disappears entirely.

### THE LEVEL COMPARISON IS A TRAP, and it caught me first

The autocorrelation at 48 yr is **higher in the no-caribou arm** (+0.632 vs +0.560), and read on its own that
says the opposite — that removing caribou strengthened the 48-year signal. It does not. The whole
autocorrelation function sits higher in the OFF arm because that population is more persistent; what matters
is the **shape**, and only the ON arm has a local maximum. Comparing the level at one lag, rather than the
curvature across lags, would have inverted the conclusion.

### Magnitude

Mean population **2,470 with caribou / 3,642 without — a 32% depression**, from a channel that applies a 93%
peak-to-trough meat drawdown on 5,474 steppe cells. The herd swing is not a decoration; it is one of the
largest single effects measured in this model.

### Why one seed is defensible here and was NOT for the regime telegraph

The caribou channel is **deterministic** — a cosine with a drawn period and phase — so its period is fixed
once drawn and the response is reproducible. The regime telegraph is a **stochastic two-state chain**, and
60-seed replication (same drawn parameters) gives an active fraction ranging **0.000 to 0.494 with 18% of
seeds never firing at all in 2,500 years**. A single regime arm carries no information; a single caribou arm
carries its period.

**That distinction should govern how the climate layer is benchmarked**: deterministic channels can be read
from one long arm, stochastic ones need seed replication. MARKER_MATRIX binding rule 3 ("seeds must beat the
variance") applies to the climate layer, and nothing had said so.

### Caveats, stated

- One seed per arm. Defensible for the deterministic channel as above; the 32% level effect would still
  benefit from replication.
- `coastal-temperate` has no savanna, so `intercept` and `llanos` were UNREACHABLE in both arms (tier-2
  finding). This is a claim about a steppe-bearing temperate world.
- The caribou amplitude 0.871 is from an UNDERGRADUATE thesis (Addendum 32) — the weakest anchor in the
  climate layer, and this result rests on it.


---

**ADDENDUM 36 — A DIAGNOSTIC I BUILT, COMMITTED AND WIRED INTO EVERY CAMPAIGN COMPARED INCOMPATIBLE UNITS.
Retracted in full. Measuring the question properly instead produced a real finding: the per-biome GAME
return-rate table has never affected a single run, and `forage_kcal` is load-bearing through exactly three
surfaces, none of them "food supply" (2026-08-08).**

### The retraction

`food_consistency.py` (commit `4f02e1d`, reverted `25df603`) divided a **cell capacity** (persons/cell, from the
NPP-derived Tallavaara field) by a **per-person harvest multiple** (`forage_kcal × hours / burn`). Those are not
the same kind of quantity. Everything downstream was void: the "savanna 16.9×, wetland 14.0×, cluster 2.2–2.7"
result, the reading that savanna's rates were mis-scoped, and the wetland `game_kcal` 0 → 3,001 change made to
fix it. None of it reached this file before the retraction; it was reported in chat and is recorded here so the
reasoning is on the record rather than only the reversal.

`capacity.py`'s own header states the design outright — *"a cell's extractable kcal/step is set by its
NPP-derived forager density, NOT the bare `forage_kcal` rate ... the bare forage field (~1–8 persons/cell) is too
poor to hold a band, while this field gives ~30–50 persons/cell."* The ~1–8 vs ~30–50 gap I reported as a defect
**is the documented rationale for the capacity field existing**. There are not two competing food models; there
is one supply and a return-rate table doing other jobs.

The suite caught the second half unaided: `test_phase1_kcal.py::test_game_kcal_zeroed_at_wetland` asserts
*"game_kcal must be 0 at wetland (UNANCHORED)"* — a deliberate provenance guard (Return-Rate Table §1.4) that an
unanchored biome reads zero rather than carrying an invented number. I overrode a tested design rule on the
strength of a diagnostic that was wrong.

**The specific failure of discipline, since CTB is supposed to prevent exactly this.** I wrote ten CTB tests for
that diagnostic and every one of them verified that the ratio was *computed as specified*. Not one asked whether
the ratio *meant* anything. **A constructed truth for the arithmetic is not a constructed truth for the
quantity** — the CTB has to be built on a world whose ANSWER is known, not on a formula whose STEPS are known.
Sixth instrument defect of this arc, and the first that was committed and wired into every campaign before being
caught.

### The question that was actually open

If the capacity field is the supply, what are `forage_kcal` and `game_kcal` doing? Answered by **perturbation,
not inspection**: scale a field ×1000 or ×0, re-run, compare the trajectory. Reading call sites tells you where
a name *appears*; only perturbation tells you whether the value *matters*. Config: `full_campaign.toml`
(the config campaigns actually run), coastal-temperate, 200 founders, 10 steps.

**The instrument's own first version was wrong, and the positive control is what caught it.**
`TerrainWorld.__init__` line 267 does `self._fields = generate_world(knobs)` — the model **regenerates its own
world** from the knobs and never reads the `WorldFields` the caller built for the capacity field. Perturbing the
caller's copy changed nothing; every arm read "not load-bearing"; the answer was clean, plausible and
meaningless. The tell was that `enable_forage_cap=True` with `forage_kcal ×0.001` should starve everyone and did
not. The published version perturbs `w._fields` and **requires** a known-live field (`npp_gm2 ×0.5`) to change
the run before any negative result is reported. Two instrument failures in one day on the same question, the
first shipped and the second caught in ten minutes — by a control that costs one test.

### The findings

| Perturbation | Result |
|---|---|
| `npp_gm2 × 0.5` — POSITIVE CONTROL | pool_sum ×0.66, pop 106 → 104 (**changes, as required**) |
| `game_kcal × 0` | **bit-identical** |
| `game_kcal × 1000` | **bit-identical** |
| `forage_kcal × 1000`, in-model | pool_sum ×3.24, pop 106 → 110 |
| `forage_kcal × 0.001` at seeding | placement 67 → **175** distinct cells |
| `forage_kcal × 1000` at seeding | placement 67 → **8** distinct cells |
| `forage_kcal × 1000`, agglomeration + forage cap both OFF | **bit-identical** |

**`game_kcal` is dead, and always has been.** It is read only by `TerrainField.game_level`, called from exactly
one site (`_step_agent`), which executes only when the multi-occupancy substrate is **disabled** *and*
`game_stream=True`. Every campaign is rivalrous and passes `game_stream=False`, and **no harness anywhere in the
repository sets it True** — only `tests/test_phase1_kcal.py`. An anchored, curated, twice-corrected per-biome
table (R-79 corrected desert game 730 → 995 as recently as 2026-07-17) has never entered a result.

**Campaign meat is `game_meat_frac × S`** — and `game_meat_frac` is a **scalar** (0.55, the forest value), so the
same fraction of the capacity pool in **every biome**. Whatever biome-to-biome variation in hunting the table
encodes, the model does not have it. Two live things must not be swept in with this: the climate `meat_factor`
(caribou swing, Addendum 35) modulates meat in *time* on GRASS_STEPPE, so **Addendum 35's finding is
unaffected** — it runs through `meat_factor`, not `game_kcal`; and Cordain 2000's per-biome `terrain.MEAT_FRAC`
does reach the model, by a different route (`terrain.RETURN_CV` → `enable_emergent_band_size`, on in
`full_campaign.toml`). What is missing is a biome-varying **harvest split**, not every biome-varying diet term.

**`forage_kcal` is live on three surfaces and no others:** founder **band placement** (outside the model, the
largest effect), the per-person **forage cap**, and the **agglomeration base**
`A_cell = aggl_tier2 · S_pot · (forage_kcal · forage_cap_hours)`. The exhaustiveness is itself a test: with
`enable_agglomeration` and `enable_forage_cap` both off, `×1000` is bit-identical in-model, so those two flags
carry **all** of its in-model influence and a third consumer added later will fail loudly.

### What this dissolves, and what it does not

The wetland/mountain `game_kcal` zeros — which I spent the preceding stretch trying to justify filling — **cost
nothing at present**. They are honest gaps under the §1.4 UNANCHORED policy, and no run outcome depends on them.
Anchoring them is a prerequisite for a two-stream economy, not a fix for a live defect. Rademaker 2014
(Cuncaicha foragers at 4,480 m taking vicuña, guanaco and taruka) still shows the mountain zero is
*ecologically* false; that stays a real gap in the table and a false one in the model's biology.

**Still unexplained, and back to unknown:** `world_savanna` settles at **9%** of trough-limited capacity against
51% and 69% for the other two canonical worlds. That measurement stands — it came from run trajectories, not
from the retracted diagnostic — but the explanation offered for it was the retracted one. No replacement is
offered here rather than a third guess.

Pinned by `sic_games/tests/test_field_load_bearing_ctb.py` (12 tests, positive control first). Documented in
Return-Rate Table §0. **The modelling decision — wire the two-stream economy so §3 becomes load-bearing, or
retire §3 to a reference table and say so — is the supervisor's and is not taken here.**

---

**ADDENDUM 37 — THE TWO-STREAM ECONOMY BECOMES PER-BIOME. Both new flags read dicts that were already anchored,
so no new number enters the model. The CTB caught a bug in my own wiring on its first run (2026-08-08).**

### What was already live, and what was not

The supervisor's reaction to Addendum 36 was surprise that the two-stream economy was not live. The record needs
a correction here, because **the split itself has run in every campaign since the Carbon build**: the cell pool
`S` divides into a forage stream at a literal κ=0 and a meat stream at the substrate κ, band-pooled and
Cred-weighted, with the G.3 stochastic meat draw on top. That mechanism was never dead.

What was **scalar** is the split. One `game_meat_frac` = 0.55 — the FOREST value — for every biome on the map,
and one `game_meat_cv` for every biome. Combined with Addendum 36 (`game_kcal` reaches nothing), a campaign
carried **no biome signal in its diet at all**. MODEL_SPEC §4.5.5 had said so in one line since 2026-06-21:
*"`mf` is a scalar config ... the per-biome `terrain.MEAT_FRAC` dict is the home for a future per-cell wiring."*

### The wiring

Two flags, each reading a dict that already exists and is already anchored. **Neither introduces a new number.**

| Flag | Source | Values |
|---|---|---|
| `enable_biome_meat_frac` | `terrain.MEAT_FRAC` — Cordain 2000 Table 2, terrestrial-renormalized | forest 0.55, desert 0.45, savanna 0.38, grass 0.66, mountain 0.34 |
| `enable_biome_meat_cv` | `terrain.MEAT_CV` — cchunts day-to-day CV; Hawkes 1991 for the Hadza | forest/Aché 1.97, desert/Martu 2.92, savanna/Hadza 5.29 |

**The two fallbacks differ, and that is deliberate.** The dicts record different reasons for an absent biome.
`MEAT_FRAC` omits WETLAND on purpose — terrain.py calls it *"a gap, not a measured zero"*, because 0.0 would
assert that wetland foragers eat no meat — so an absent biome takes the configured **scalar**. `MEAT_CV` omits
grass, mountain and wetland for want of a calibration people, and terrain.py's own rule for that case is
**`HUNT_CV` = 2.11**, a measured biome-invariant value across ~15,600 trips. Both fallbacks are pinned by tests,
so a later tidy-up to 0.0 fails loudly rather than quietly asserting two things no source supports.

Class defaults are False (Charter §12, bit-exact). The **campaign** default is `true` in
`config/mechanisms.toml`, per the supervisor's standing rule that nothing stays off without being a control.

### What the wiring puts on each canonical world — FIELDS, not yet run results

Measured on the three tier-2 worlds at their configured terrain × climate. This says what CHANGED, not what it
DOES; the run comparison is a separate step and is not reported here.

| world | land cells | biomes | mean `mf` (was 0.55 everywhere) | mean meat CV (was 0.73 everywhere) |
|---|---|---|---|---|
| `world_temperate` | 9,449 | forest 3399, grass 5474, desert 576 | **0.608** | **2.11** |
| `world_savanna` | 9,453 | savanna 4499, desert 2896, forest 1717, grass 237, wetland 104 | **0.441** | **3.85** |
| `world_montane` | 9,822 | grass 4325, forest 2285, desert 2113, savanna 654, mountain 367, wetland 78 | **0.558** | **2.46** |

Two things stand out and neither is a claim yet:

- **The change is not a uniform shift.** Temperate goes UP (grass-dominated, `mf` 0.66) and savanna goes DOWN
  (`mf` 0.38). A flat 0.55 was not a neutral average of the three — it sat above savanna and below temperate.
- **`world_savanna` moves most, on both axes at once**: the meat fraction falls 0.55 → 0.44 while the meat CV
  rises 0.73 → 3.85, a **5.3×** more variable meat stream, because Hadza big-game hunting is the documented
  extreme (Hawkes 1991, CV 5.29). Savanna is also the world with the unexplained 9%-of-capacity settling
  (Addendum 36). **That is a coincidence of location, not evidence**, and it must be tested as a hypothesis with
  the flags as the ablation — not adopted as the explanation this arc has already had two of.

### A side effect worth naming: the retired 0.73 leaves live runs

`game_meat_cv = 0.73` is still the scalar in `full_campaign.toml`. R-72/R-73 established that 0.73 is
`GAME_KCAL_STD/mean` for forest — a **SPATIAL** cross-cell spread used as a **TEMPORAL** per-step draw, 2.7×
low. R-73 then measured that error's blast radius as **zero** (the Cred effect is CV-insensitive), so the value
was left in place and quietly outlived its own retraction by three weeks. The per-biome path does not reproduce
it anywhere, and a test asserts that. **This is a provenance correction, not a results correction** — R-73 says
not to expect a marker to move.

That a retired anchor sat in the live config for three weeks is the same class as Addendum 30 ("Addendum 28's
retraction never reached the code"). A sweep of every config value against the addenda that touched its anchor
is now an open task.

### The CTB caught a bug in my own wiring, first run

`test_each_flag_is_live_on_its_own[enable_biome_meat_cv]` failed: the flag was on and the trajectory did not
move. Cause — I replaced the guard `if meat_cv > 0.0` with `if cv_c > 0.0`, and left the line below it computing
`sig = sqrt(log(1 + meat_cv²))` from the **scalar**. The per-cell CV gated the draw and then took no part in it.

Worth recording plainly, because it is the *cheap* version of the failure that has cost this arc six
instruments: the per-flag liveness test is three lines, and it is the only reason a half-wired mechanism did not
ship reading "on". A flag that is on and changes nothing is exactly what the ON-but-dead gate exists for
(Charter §12) — that gate checks the CONFIG, and this one needed a check on the RUN.

### Not done, and why

**The meat pool still does not come from `game_kcal`.** `game_kcal` is a RATE (kcal per forager-hour); `S` is a
cell POOL (kcal per step). Feeding one into the other is the unit error of commit `4f02e1d`, one addendum ago.
Total food already comes from the Tallavaara NPP capacity field, which integrates the whole subsistence base,
and diet composition now comes from Cordain. **In the current architecture the game return-rate table has no
remaining job.** The recommendation is to retire Return-Rate Table §3 to a reference table unless the separate
depletable game stock (the GD-1/CC-1 seam) is built. That decision is the supervisor's; nothing is deleted.

Pinned by `sic_games/tests/test_biome_meat_ctb.py` (12 tests, including per-cell energy conservation).

---

**ADDENDUM 38 — CORRECTION TO ADDENDUM 37. I described a documented, reasoned decision as a lapse. R-73 did not
forget to remove `game_meat_cv = 0.73`; it decided to leave it and wrote down why. Third time in two days that
I have read a deliberate design decision as a defect (2026-08-08).**

### What Addendum 37 got wrong

Addendum 37 says the value *"outlived its own retraction by three weeks"*, that *"nobody removed it"*, and that
it is *"the same class as Addendum 30"*. **All three are wrong.** R-73's closing paragraph states the decision
in plain words:

> *"Harness CVs left at 0.73 with the mis-anchoring documented, since (1) shows re-running them would be compute
> spent to reproduce the same numbers."*

That is a decision with a reason and a measurement behind it — R-73's own sweep showed the Cred effect is flat
from CV 0.73 to 5.29, so at forest's true 1.97 the result is statistically indistinguishable from the arm that
was actually run. Leaving the value was the *cheap* correct call. **It is the opposite of Addendum 30's case**,
where a retraction reached RESULTS.md and never reached the code at all.

What survives from Addendum 37 on this point: nothing, except the plain fact that the scalar is 0.73 and that
`enable_biome_meat_cv` now bypasses it for every biome with a calibration people. That is a genuine improvement.
It is not a rescue.

### The instrument I built on the misreading, and did not ship

I wrote `tools/retired_values.py` — a registry of values that a RESULTS addendum has withdrawn, plus a sweep of
every config for one still live. It ran, and reported **24 live retired values across 8 config files**.

**Every one was a false positive.** The two registry rows were `game_meat_cv = 0.73` (above) and
`rank_hierarchy_frac = 0.15`, and Addendum 30 states the second in capitals: **"NOTHING WAS RE-VALUED."** Both
values are deliberately kept and labelled `[UNANCHORED]` at their point of use. The tool's whole premise — that
a retired value in a live config is an oversight — is false for exactly the cases that motivated it.

**The tool is deleted, not fixed.** Two reasons. First, the check that actually matters is Charter P3 (*a
retracted anchor is edited at its point of use*), and `tests/test_retraction_propagation.py` already enforces
it — a second instrument over the same rule is a second copy, which Charter P4 forbids. Second, a diagnostic
whose first run produces 24 confident false findings has not earned a place in the suite; the arc has shipped
enough of those.

### The pattern, since this is now the third instance

| what I called it | what it was | where it was written down |
|---|---|---|
| two food models disagree (Addendum 36) | the capacity field's design rationale | `capacity.py` header, first paragraph |
| wetland game 0 is a defect (Addendum 36) | a provenance guard, deliberately zero | `test_phase1_kcal.py`, the assertion message |
| 0.73 outlived its retraction (Addendum 37) | a measured decision to leave it | R-73, closing paragraph |

The common shape: **I found a value or a structure that looked wrong, and reported it before reading the place
where the project had already reasoned about it.** In all three the explanation was one grep away, in the file
or the log I was already working in. The CTB rules cover instruments. This is a reading failure upstream of any
instrument — the fix is to search the record for the thing before calling it a defect, not to build a diagnostic
that finds it again.

Addendum 37's substance is otherwise unaffected: the per-biome wiring, the anchored dicts, the two fallbacks,
the CTB that caught the σ bug, and the field measurements on the three canonical worlds all stand.

---

**ADDENDUM 39 — THE CANONICAL WORLDS, AND THE SEED. The savanna capacity anomaly carried through three addenda
is a SEED, not a world. Replicating it closed it; every world in this project is far more seed-dispersed than
any single-run result has admitted; the montane world cannot be partitioned and no world can be; and the
capacity denominator has a floor nobody had noticed (2026-08-08 / 08-11).**

### Why this entry is late, and what that cost

The three worlds were built and run on 2026-08-08 and reported in chat only. `world_montane.toml` carried a
`why` citing *"the partition measurement in Addendum 36"* — an addendum that did not exist, and whose number was
then taken by the retraction entry. The false forward reference is removed. Every figure below was re-measured
from the current code and the committed run outputs, not transcribed from the earlier report.

### The world set

| world | terrain × climate | land cells | biomes present (land cells) |
|---|---|---|---|
| `world_temperate` | coastal × temperate | 9,449 | forest 3,399 · grass 5,474 · desert 576 |
| `world_savanna` | coastal × savanna | 9,453 | savanna 4,499 · desert 2,896 · forest 1,717 · grass 237 · wetland 104 |
| `world_montane` | mountainous × savanna | 9,822 | grass 4,325 · forest 2,285 · desert 2,113 · savanna 654 · mountain 367 · wetland 78 |

Between them the set covers all six land biomes. **No single world does**, which closed the supervisor's option
(a) — one canonical world containing everything — and forced the three-world set.

### THE DENOMINATOR, because this measure has two

`settled_fraction` = settled population ÷ supportable population, and "supportable" has two defensible readings
that differ by 3.9×. Both are recorded so no later reader has to guess which one a number meant.

| world | MEAN capacity | TROUGH capacity | trough ÷ mean |
|---|---|---|---|
| `world_temperate` | 27,614 | 7,161 | **0.259** |
| `world_savanna` | 26,549 | 6,907 | **0.260** |
| `world_montane` | 31,023 | 8,052 | **0.260** |

Measured over 2,500 steps of the live climate field, all channels on, sampled every 5 steps. **The trough/mean
ratio is 0.26 in all three worlds to three decimals** — the climate layer compresses capacity by the same factor
everywhere, so a cross-world comparison is insensitive to the choice. That is what makes the next section safe,
and it was not obvious in advance.

### THE FINDING: the savanna anomaly is a seed

`world_savanna`, flat-meat control, settled population by seed:

| seed | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| settled | 594 | 3,034 | 2,518 | **8,677** | 634 | 3,572 | **186** | 3,961 |

**Range 186 → 8,677: a 46.7× spread, CV 0.949.** Seed 3 settles at 126% of its own trough capacity; seed 0 — the
seed every earlier savanna number came from — is near the floor.

So *"world_savanna settles at 9% of trough capacity while the others reach 51% and 69%"* is a statement about
**seed 0**. It was carried as an open anomaly through Addenda 36, 37 and 38, survived two retracted explanations
and one reverted diagnostic, and **every one of those rounds was spent interpreting a single run.** One extra
seed would have closed it at the start, for twenty minutes of compute. MARKER_MATRIX binding rule 3 — *a seeded
effect must beat 30× seed variance* — exists for exactly this and was applied to markers but not to this.

### AND THE DISPERSION IS NOT SAVANNA'S ALONE

| world | flat-control range | spread | CV | n seeds |
|---|---|---|---|---|
| `world_savanna` | 186 → 8,677 | **46.7×** | 0.949 | 8 |
| `world_temperate` | 2,445 → 13,467 | 5.5× | 0.666 | 5 |
| `world_montane` | 3,729 → 9,975 | **2.7×** | 0.392 | 5 |

Savanna is genuinely the outlier — the ordering is clean and monotone. **But even montane, the tightest world,
spans 2.7× on identical configuration.** No single-seed settled population in this project's history means what
it appears to mean, and that includes results this log has recorded as findings.

### The flag effects, replicated

Each arm against the SAME seed's own flat control (the per-biome meat wiring of Addendum 37):

| world | fraction only | CV only | both |
|---|---|---|---|
| `world_savanna` | −30.3% (n=8, all neg) | **−65.3%** (n=8, all neg) | **−67.5%** (n=8, all neg) |
| `world_temperate` | −11.6% (n=5, all neg) | −8.0% (n=5, **not** all neg) | −19.4% (n=5, all neg) |
| `world_montane` | −10.7% (n=5, **not** all neg) | −17.1% (n=5, all neg) | −28.7% (n=5, **not** all neg) |

Standard deviations run 7–28 points, comparable to the effects themselves. **The sign replicates; the magnitude
is not estimable from five seeds.** Savanna is the only world where every arm in every seed is negative — in the
other two the flags sometimes *help* (temperate CV-only +11% at seed 0, montane both +5% at seed 3). So *"the
per-biome wiring reduces population"* is a savanna statement, not a model statement.

**One clean structural signal, and it is the first thing in this arc that behaved as predicted without needing a
retraction first: effect size tracks the size of the CV change.** Savanna's mean meat CV moves 0.73 → 3.85,
montane's → 2.46, temperate's → 2.11, and the CV-only effects order the same way (−65%, −17%, −8%).

### A SELECTION BIAS IN THE ANALYSIS, caught before publication

The first version of this analysis filtered on `steps_completed == 2500` and silently dropped two savanna arms
— seed 6, CV-only and both — which had **gone EXTINCT** (population 1 at steps 1411 and 1503;
`run_campaign.py:915` is `log("EXTINCT"); break`, and with `max_minutes = 0` the budget branch cannot fire).

**Those are the strongest possible instances of the effect being measured, and the filter threw them away**,
biasing every arm mean toward the survivors. Correcting it — an extinction is settled = 0, not a missing datum —
moved savanna CV-only from −60.4% to **−65.3%** and both from −62.8% to **−67.5%**, and made seed 6 read −100%
on both arms. The filter now distinguishes extinction from budget truncation and asserts which it is seeing.

### The montane world is NOT partitioned, and no world can be

Measured on the traversal-cost field the model actually uses, not on elevation:

- land traversal cost **0.151 → 1.000**, mean 0.420 · cells at maximum cost: **3** · **impassable cells: 0**
- mountain biome: 367 cells, **3.7% of land**

**The model has no impassable terrain.** Relief raises the *cost* of movement and cannot isolate a population.
The supervisor's original design — *"all biomes seeded with people and preferably separated by hard-to-pass
mountains that would keep the pops separated and evolving differently"* — is **not buildable on this terrain
generator as it stands**. That is a statement about the generator, not about these worlds. A partitioned world
needs water or a gap of uninhabitable cells.

### The capacity diagnostic has a floor, and the CTB negative found it

CTB before use: a flat 800 g/m²/yr NPP world over the 40×40 patch. Expected 8.62 persons/cell × 1,600 cells =
13,799; the diagnostic returned **13,799**.

**Then the negative, which is the half that earned its keep.** A zero-NPP world — bare rock, all water — should
support nobody. It reads **1,398 persons**, ~0.87 per 100 km². `density_tallavaara` is `exp(INT + B1·npp + …)`
and `exp(−0.1353) = 0.873` at npp = 0. An exponential never reaches zero, and Tallavaara 2018's data do not
extend to a barren world, so this is extrapolation outside the fitted range.

Size: ~1,398 in a denominator of 26,000–31,000, so **~5% of every capacity figure in this entry is floor rather
than ecology.** It changes no conclusion here, but it is a real property of the measure and has presumably been
present in every capacity number this project has produced.

### What tier 2 covers, and what it does not

**Covered:** all six land biomes across the set; the Hawkes 1991 savanna game rate and the llanos flood are
reachable for the first time (they read `UNREACHABLE` on `world_temperate` and looked broken for that reason);
the capacity diagnostic is CTB'd positive and negative.

**Not covered:** a partitioned world. Independent evolution of separated populations is not testable at tier 2
as built.

**CLOSED:** the savanna capacity gap. There is nothing left to explain at world level.

**NEWLY OPEN, and larger than what it replaced:** every world is seed-dispersed by 2.7–47×, and this project has
been reading single runs as results throughout. The question is no longer "why is savanna low" but **"which
existing findings survive replication?"** That is a re-audit, not a study.

---

**ADDENDUM 40 — THE VARIANCE IS THE WORLD LOTTERY, NOT THE DYNAMICS. Splitting the seed into its three roles
attributes 73% of the population variance to the PLANET DRAW and under 1% each to the climate realisation and
the stochastic path. But the marker that this project scores stratification on is the exception, and the rule
that follows differs by marker (2026-08-11).**

### The design

Commit `fe00524` split `seed` into `world_seed` / `climate_seed` / `agent_seed`. Fifteen arms on
coastal-savanna, 2,500 steps, current config; each arm varies ONE role over 0–4 and pins the other two at 0.

**CONSISTENCY CHECK FIRST, and it is not decoration.** `var_P_a0`, `var_W_w0` and `var_C_c0` are the same run
(0,0,0) authored three ways. All three settle at **105.2**, identically. If they had differed, the pinning would
not work and every number below would be void. It cost nothing and it ran first.

### The answer

| source varied | n | CV | share of variance | share of CV |
|---|---|---|---|---|
| **all three** (an ordinary `seed` sweep) | 8 | **1.735** | 100% | 100% |
| **world** — the planet draw | 5 | **1.487** | **73.5%** | 85.7% |
| climate — the realisation on one planet | 5 | 0.200 | **1.3%** | 11.5% |
| path — repeated trials of one planet | 5 | 0.149 | **0.7%** | 8.6% |

Settled populations: path **105 · 96 · 99 · 72 · 108**; climate **105 · 148 · 99 · 92 · 125**; world
**105 · 1,403 · 695 · 5,562 · EXTINCT**.

**One planet in five goes extinct; no path and no climate realisation ever does.** The three named sources
account for 76% of the variance; the remainder is interaction plus the different n.

### Two expectations of mine were wrong

**I predicted climate would be the smallest source.** It is not — it is larger than path, on every marker except
`band_med` and `deaths_starv`. **And the 400-step probe put path CV at 0.27, but by step 2,500 it is 0.149**:
early divergence partly re-converges rather than compounding. A short probe over-states path sensitivity, which
is worth knowing before anyone uses one as a shortcut.

### THE EXCEPTION, and it is the marker that matters most

| marker | path | climate | **world** |
|---|---|---|---|
| `pop` | 0.151 | 0.199 | **1.487** |
| `band_med` | 0.193 | 0.162 | **0.565** |
| `gini_cred` | 0.188 | 0.145 | **0.529** |
| **`pct_stratified`** | **0.404** | **0.546** | **0.947** |
| **`deaths_starv`** | **1.465** | 0.573 | 1.245 |

**`pct_stratified` carries a 3–5× spread on ONE IDENTICAL PLANET.** And `deaths_starv` is the one marker where
PATH variance EXCEEDS world variance — which makes sense, since a starvation count is an event tally driven by
bad draws, not by how much land there is.

So "fix the world and one run is enough" is true for population and false for the two markers this project most
often argues from.

### The rule this produces, and it is per-marker

- **A population or capacity claim** — pin the world. Path noise is ~15% CV, so one run per world is adequate
  and the comparison should be ACROSS worlds, replicated.
- **A stratification, inequality or mortality claim** — replicate the PATH on a fixed world. Multiple worlds do
  not substitute: `pct_stratified` moves 3× and `deaths_starv` moves more from the path alone than from the
  planet.
- **MARKER_MATRIX binding rule 3** says *"seeds must beat the variance"* and cites R-65's 30× seed variance in
  `%stratified`. That rule is right and its stated basis was imprecise: until `fe00524`, "seed variance" could
  only mean WORLD variance, because one integer drew the planet. It should now distinguish the two, because the
  answer differs by marker and for `%stratified` BOTH bars are large.

### What this settles about Addendum 39

The 46.7× savanna spread is **the planet lottery**, not model chaos. `world_lottery_climate(seed)` draws relief,
roughness, water fraction, latitude and aridity from the preset ranges, and one draw in five gives a world that
cannot hold a population at all. The model is not unstable; the world set is wide. That is a defensible design —
but it means a "seed sweep" has always been a sweep over planets, and a result quoted from one is a result about
one planet.

### One more hidden denominator, in my own reporting

The first version of the decomposition table printed a spread of **6×10⁸** for `deaths_starv`, because one arm
reached ~0 and the ratio divided by it. Fixed: the ratio is suppressed when the floor is near zero and CV carries
the comparison. Same bug class as the settled-fraction denominator in Addendum 39, two entries apart, in code I
wrote to investigate the first one.

---

**ADDENDUM 41 — THE TIER-3 AGE-STRUCTURE FAULT IS REAL: two alternative explanations tested and both
FALSIFIED. But the mechanism is NOT yet attributable, because the vital-rate comparators I reached for are not
in the filed source and I withdraw them (2026-08-11).**

### The fault, on verified ground

Model under-15 fraction at stationarity, measured across nine arms (Addendum 40's decomposition set):

| | value |
|---|---|
| model, 9 arms | **0.478 – 0.569**, mean **0.518** |
| !Kung 1968 | 0.287 |
| Aché 1970 | 0.419 |
| Yanomamö 1960s | 0.454 |

Table 4.4 is VERIFIED verbatim and uses the model's own age classes, so no conversion is involved. **Every arm
sits above the highest of three real forager populations.** Model mean age is 19.0 years.

### Alternative 1: "the population is still growing" — FALSIFIED

A growing population is legitimately young, and MARKER_MATRIX rule 4 exists to catch exactly this. Measured the
tail growth rate (log-linear, last 20%) on all fifteen arms: **most are stationary**, |growth| < 0.5%/yr, and
they carry juvenile fractions of 0.478–0.569 regardless. Two arms that ARE growing (0.93 and 1.20 %/yr) sit at
0.546 and 0.514 — inside the same range. The fault is not a transient.

### Alternative 2: "the definition differs from the anchor's" — FALSIFIED

`juv_frac` could have been the `is_juvenile()` productivity gate rather than the under-15 count, which would
make the whole comparison a category error — the `connubium_med` failure again. Checked at the point of
computation: `sum(1 for x in ages if x < 180) / pop`, and 180 months is 15 years. **It is the under-15
fraction.** The comparison is valid.

### AND HERE I HAVE TO STOP, because the next step needs an anchor I do not have

The obvious mechanism question is whether this is too much fertility or too little adult survival. Model crude
birth rate across the same arms is **3.99 – 7.75 %/yr, mean 5.26**. I compared that to "Aché ~4.6 %/yr" and
"!Kung ~3.5 %/yr" — **and those two numbers are not verified.** Searching the filed Hill & Hurtado PDF for
*crude birth rate*, *births per 1000* and *birth rate of* returns **nothing**. I quoted them from memory, which
is the precise failure this project has recorded four times in six days.

**Both comparators are withdrawn.** With them goes the interpretation they supported — that the model is a
high-turnover population with excess fertility. It may be; the evidence for it is not on file.

What that leaves, which is still worth having: **several arms produce a juvenile fraction of 0.478–0.514 at a
crude birth rate of 3.99–4.37 %/yr.** Whatever the ethnographic rate turns out to be, a *within-model* fact
holds — the youngest age structures do not sit on the highest birth rates, so fertility alone does not order
this. That points at adult survivorship, and it is a hypothesis, not a finding.

### Next, and it is a literature task before it is a modelling one

1. Find a VERIFIED forager crude birth rate, or a life table. The Aché book has one (it is a demography
   monograph) but not under the phrases searched; it will need the tables read, not grepped.
2. Then compare the model's survivorship curve, not its aggregate rates. The age-band diagnostic already exists
   (`demography()` returns `frac_child` / `frac_adult` / `frac_elder` / `dependency_ratio`) but is NOT in the
   trajectory rows, so it cannot be read off any completed run — that wiring is the cheap enabling step.

---

**ADDENDUM 42 — THE FERTILITY ANCHOR EXISTS AND IS NOW FILED, BUT IT IS NOT A CRUDE BIRTH RATE. My attempt to
derive one was dominated by an assumption I invented, and I abandoned it rather than ship it. The comparison
tier 3 needs is TFR, and the model does not measure TFR (2026-08-11).**

### Found, by listing the book's tables instead of guessing phrases

Addendum 41 searched the Hill & Hurtado PDF for *"crude birth rate"*, *"births per 1000"* and *"birth rate of"*
and got nothing, so two comparators were withdrawn. The failure was the **search method**: guessing what a
sentence might say. Extracting all **73 table captions** and reading them found the data immediately.

Three anchors now registered and VERIFIED (registry 22/22):

| anchor | content |
|---|---|
| **Table 8.1** | Aché forest ASFR by SINGLE year of age, 10–49, with women-years at risk. **3,309 women-years, TFR 8.031** |
| **Table 8.2** | Comparative TFR — **Aché 8.03 · !Kung 4.69 · Yanomamö 6.86** |
| **Table 8.2** | Interbirth interval (months) — **Aché 37.6 · !Kung 49.4 · Yanomamö 34.4** |

Table 8.2 covers **the same three societies as Table 4.4**, so fertility and age structure can be read off one
consistent set. `!Kung` from Howell 1979 Table 6.1; Yanomamö from Melancon 1982 Table 4.2.

### The derivation I abandoned, and why that is the result

The monograph states **no crude birth rate anywhere.** I tried to derive one by combining Table 4.4's age
structure with Table 8.2's age-specific rates. Table 4.4 gives 15–60 as ONE band, so the within-band female age
split has to be assumed. Sensitivity to that assumption:

| assumed attrition per decade | Aché | !Kung | model ÷ Aché |
|---|---|---|---|
| 1.00 (flat) | 4.13 | 3.24 | **1.27×** |
| 0.95 | 5.07 | 4.61 | 1.04× |
| 0.90 | 5.27 | 5.41 | **1.00×** |
| 0.80 | 5.00 | 5.90 | 1.05× |

**The conclusion flips on the assumption.** At flat weighting the model has 27% excess fertility and that alone
explains the excess child fraction; at 0.90 the model's fertility matches the Aché exactly and the excess needs
a different cause. My invented parameter was doing all the work, so the derivation says nothing — and my
memory-quoted 4.6%/yr happens to sit inside the range, which is luck, not corroboration.

**Abandoned rather than published.** Six days ago this project shipped a diagnostic that divided incompatible
units; the lesson was to name the quantity before computing it. Here the quantity was fine and the *input* was
invented. Same discipline, different point in the chain.

### What the comparison should be, and what it needs

**TFR, not CBR.** TFR needs no total-population denominator, it is stated verbatim for all three societies, and
it is the quantity a fertility model should be judged on. Interbirth interval is a second direct comparator and
the model already has an IBI mechanism (`_do_births_ibi`).

**But the model measures neither.** The trajectory logs `births` (a count per step) and `juv_frac`. It does not
log TFR, age-specific fertility, or realised IBI. So the tier-3 fertility question — the one Addendum 41 stopped
on — **cannot be answered from any run on disk**, and no amount of re-analysis will change that.

### Status of Addendum 41's hypothesis

Addendum 41 closed with *"that points at adult survivorship"*, reasoning that the lowest-CBR arms still carried
high juvenile fractions. **That reasoning used the withdrawn comparators and is now unsupported in either
direction.** It is neither confirmed nor refuted; it is untested, and it stays that way until the model reports
TFR.

### The enabling work, in order

1. **Log TFR, ASFR and realised IBI** per run. Pairs with the age-band diagnostic (`frac_child` / `frac_adult` /
   `frac_elder` / `dependency_ratio`) which `demography()` already computes and nothing writes down.
2. Then compare against Table 8.1/8.2 directly, with no derivation and no assumed splits.

**A note on method, because it generalises.** Grepping a PDF for a phrase you expect tests your guess about the
wording, not the document. Listing its TABLE CAPTIONS tests the document. That is how Table 4.4 was recovered
after being wrongly called OCR-garbled, and it is how these three were found in one pass.

---

## Addendum 42 — The fertility brake multiplies the wrong term (2026-08-13, R-106)

**THE FAULT.** The demography markers fail together. `frac_child` reads 0.481 to 0.633 against a VERIFIED
[0.287, 0.454]. `dependency_ratio` reads 1.18 to 1.81 against a VERIFIED [0.598, 0.899]. The realised life
expectancy is 15 to 19 years against a CONFIGURED 36.6 (Siler ACHE_FOREST, Gurven & Kaplan 2007 Table 2).

**NEW INSTRUMENTS.** Nothing measured a REALISED schedule before this date. `phase1_model.py` now counts
person-months and deaths per year of age per cause, woman-months and births per mother age, the realised
IBI, and the fertility multiplier that is actually applied. `life_table()`, `fertility_schedule()` and
`raw_demographic_counters()` read them. All are pure observers, consume no RNG and carry no flag, so every
earlier run stays bit-exact. 22 CTB tests, including a positive control that feeds ACHE_FOREST to the
estimator and demands 36.6 back, and a purity guard that fails on an injected read.

**THE IDENTITY THAT EXPLAINS EVERY ARM.** `TFR = span / (refractory + 1/(fecundability x brake factor))`.
With span 324 months and fecundability 0.12 this reproduces both measured arms to within 1%:

| arm | refractory | brake factor | predicted TFR | MEASURED TFR |
|---|---|---|---|---|
| canonical (`enable_sedentism_fertility` ON) | 22 | 0.950 | 10.53 | 10.46 |
| `hg_villages_off` (that flag OFF) | 30 | 0.9998 | 8.45 | 8.41 |

**REPAIR 1 FAILS, AND THE IDENTITY SAYS WHY.** The brake multiplies `1/(fecundability x factor)`, which is
only 22% of the birth interval. A bracket over the EMA half-life (1, 3, 6, 12 months against the shipped
~17) moved the applied factor from 0.967 to 0.861 — the brake DID bite harder — and moved nothing else:

| half-life (mo) | 1 | 3 | 6 | 12 | ~17 |
|---|---|---|---|---|---|
| mean factor | 0.861 | 0.927 | 0.925 | 0.935 | 0.967 |
| realised TFR | 10.33 | 10.57 | 10.27 | 10.43 | 10.46 |
| `frac_child` | 0.592 | 0.593 | 0.573 | 0.604 | 0.572 |
| realised e0 | 15.2 | 15.0 | 15.2 | 15.1 | 15.0 |

Even at the ABSOLUTE ceiling — zero memory, measured factor 0.767 over 240 steps and 331 women — the brake
reaches TFR 7.93. The age structure needs about 4.5. **The brake cannot regulate this model's fertility.**

**THE VARIANCE HYPOTHESIS IS FALSIFIED, WITH A PASSING POSITIVE CONTROL.** A bracket over `game_meat_cv`
(0.0 deterministic / 2.11 = terrain.HUNT_CV / 4.0) left the starvation share flat at 0.493, 0.499, 0.518.
The positive control confirms the knob is live and strong: the same sweep moves the intake coefficient of
variation from 0.604 to 1.933 and p90/p10 from 4.3 to 9.8. Note the FLAG ALONE would have given a vacuous
test — `enable_biome_meat_cv=false` falls back to the scalar `game_meat_cv`, which the canonical stack sets
to 0.73, so the parameter had to go to 0.0.

**THE VILLAGES ARE NOT THE CAUSE.** `hg_villages_off` removes only the settlement lifecycle and keeps every
production mechanism. It gives the best world this project has produced — regional density 0.061/km2 =
0.67x the Binford 0.091 anchor, `band_med` 23 against Birdsell ~25, realised IBI 35 months against Hill
& Hurtado's 37.6, the lowest starvation share at 0.352, and `frac_resident` 0.0. The population is 9661,
FOUR TIMES the sedentary arms, so the villages SUPPRESS population rather than support it. `frac_child`
0.543 and `dependency_ratio` 1.292 still fail.

**A CORRECTION.** An earlier note this arc said fertility was exonerated because the observed age structure
needed TFR 14.3 against "a ceiling of 9". That ceiling assumed `ibi_refractory_months = 30`, but
`enable_sedentism_fertility` replaces it with a society-dependent value as low as 22. Measured TFR is 8.4
to 10.5. Fertility is NOT exonerated; it is the dominant term.

**A SECOND CORRECTION.** An earlier note said starvation was a minor death channel, from one final step of
each of 12 arms. The cumulative counters give 0.35 to 0.58 depending on the arm.

**A DISCARDED PROBE.** A seasonality test returned `season()` = 1.000 for all 12 months and a starvation
share of 0.026 against the campaign's 0.35. It built a `TerrainWorld` without the campaign's
`NPPCapacityField` and `ClimateField`, so that world had no climate. Seasonality REMAINS UNTESTED.

**WHAT THE IDENTITY PROPOSES.** Lactational amenorrhea physically IS the refractory period, and energy
availability modulates its LENGTH — so the energetic condition belongs on the refractory, not on
fecundability. Inside the FILED ethnographic range the refractory alone spans the needed TFR:

| refractory | 34.4 | 37.6 | 44 | 49.4 |
|---|---|---|---|---|
| source | Hill 8.2 reservation | Hill 8.2 forest | Howell !Kung | Hill 8.2 contact |
| TFR | 7.58 | 7.05 | 6.19 | 5.61 |

The decomposition puts BOTH anchors in band at TFR 5 to 8 on this arm's own mortality. **NOT ADOPTED** —
this is a proposal awaiting the supervisor.

**AN ANCHOR GAP FOUND.** `demography.py` names Ellison's energetics as the mechanism behind the intake
brake, but no Ellison source appears in `docs/LITERATURE.md` or in `literature/`, and the specs carry only
the LENGTH of lactational amenorrhea, not its RESPONSE TIME. `intake_ema_alpha` therefore has no anchor and
no value was adopted from the bracket.

---

## Addendum 43 — The demography monitor, and two corrections to Addendum 42's follow-ups (2026-08-14, R-106)

**THE STANDING PANEL.** Supervisor directive: *"We cannot expect social dynamics to work when the demography
is skewed."* The case that proves it: `band_med` read 23 against Birdsell's ~25 and looked like a PASS on a
population that was 54% children — about 11 ADULTS against Hill et al. 2011's **28.2 ADULTS**. A marker read
as passing while failing 2.5-fold. `MARKER_MATRIX.md` #1 had already recorded this and it was still missed.

Every run now logs, and SCORES against filed bands: `e15` / `e45` / `surv_to_15` / `surv_to_45` /
`modal_adult_death`; mortality in seven age bands; `cbr` / `cdr` / `r_pct_yr` / `srb_male_frac` /
`age_first_birth_yr`; completed parity of post-menopausal women; joint orphanhood, never-partnered-by-30,
widowhood; sex-specific `e0`/`e15`; child and old-age dependency separately; and **`band_med_adults`**, the
quantity Hill's anchor names and which the model had never logged. `demography_health()` prints one verdict
line and GATES the ladder: age structure out of band ⇒ every marker above demography is provisional.

**THE CEILING FIX WORKED.** `ceiling_on` required `settle_on`, so switching villages off switched the R-63
carrying capacity off with them — including R-105's branch for capping agglomeration at non-settlement
cells, unreachable in exactly the configuration it exists for. Before: population 2,916 → 24,727 by step
3,000 and climbing, per-capita intake RISING with density. After: both arms **stable at 15,000 steps**,
0.27x and 0.35x Binford, r ≈ 0. R-105's tripwire test fired with its own message, *"scope note is stale"*,
exactly as it was written to.

**CORRECTION 1 — the density-reference fix does NOT buy 3 years of life expectancy.** Addendum 42's
follow-up reported e0 17.7 → 20.9. That was measured on the RUNAWAY world, where density had exploded and
`density_mult` was saturated near its 4.0 ceiling, so re-referencing it mattered. With the ceiling working,
density stays low, the term sits near its reference, and the fix is **near-neutral: e0 17.87 → 17.96, +0.09
yr**. The normalisation remains correct on its own terms — `risk_mult` and `pathogen_mult` hold that
invariant and `density_mult` did not — but it is NOT load-bearing at forager densities. It stays default-OFF
and out of `C_ALLON`.

**CORRECTION 2 — "age at first birth 22-25, above every forager" was a short-run transient.** Measured on
400-step smoke runs. Over 15,000 steps AFB declines monotonically 18.95 → **16.25**, which is INSIDE Walker
et al. 2006's forager bracket [16.2, 20.5] — at its extreme low edge. The defect I reported does not exist
at equilibrium; if anything the equilibrium value is now too early.

**THE ISO-GROWTH CONSTRAINT IS VIOLATED, IDENTICALLY IN BOTH ARMS.** Gurven & Kaplan 2007 endnote 5 gives
`R0 = (TFR/2.06)·l25`, `l25 = 0.9973·l15 − 0.0422`, `R0 = exp(r·28)`. The implementation reproduces their
own published claims (R0 = 1.0001 at their stated TFR 4.069, l15 0.55). Applied to the pair:

| arm | TFR | l(15) | r measured | r REQUIRED | gap |
|---|---|---|---|---|---|
| hg_villages_off | 8.37 | 0.424 | +0.02 %/yr | **+1.58 %/yr** | +1.56 |
| hg_densref | 8.40 | 0.427 | +0.03 %/yr | **+1.62 %/yr** | +1.59 |

**WHERE THE VIOLATION LIVES.** GK07's regression (R² = 0.98) says adult survival is tightly predicted by
child survival in a real forager. Measured against it: predicted l(25) 0.390, **ACTUAL 0.268 — a ratio of
0.69**, consistent at 0.67–0.71 across every arm. The model's adults die ~30% faster than the forager
relationship allows, on top of already-poor child survival.

**THE REMAINING DEFECT, DECOMPOSED.** `m_5_15` = **0.0506 against GK07's 0.010** — five times over, in the
band that is the LOWEST-mortality band of a human life table. Split by cause (control arm):

| band | m total | m starvation | m other |
|---|---|---|---|
| 1–5 | 0.0574 | 0.0143 | 0.0430 |
| **5–15** | **0.0506** | **0.0208** | **0.0298** |
| 15–30 | 0.0474 | 0.0225 | 0.0249 |
| 30–45 | 0.0474 | 0.0211 | 0.0263 |
| 45–60 | 0.0528 | 0.0206 | 0.0321 |

Two roughly equal contributors, both already named. (i) `m_other` in the 5–15 band is 0.0298 against a
configured Siler ~0.0137 = **2.2x**, which is the `a2_mult` inflation — and since the density term is now
shown to be near-neutral at these densities, the remaining inflation must be `risk_mult` and/or
`synergy_mult`, NOT density. (ii) `m_starv` is **flat at ~0.021 from age 1 to 60**, confirming Addendum 42's
"second Makeham term" at scale and now per age band.

**THREE DEFECTS IN MY OWN INSTRUMENTS, all caught before they reached a conclusion.**
- `family_structure()` counted a missing `_father` link as a DEAD father, inflating double-orphanhood
  **8.8x** (0.086 → 0.0098). `_orphan_status` had always been right. The CTB missed it because every
  constructed family had explicit links.
- `q = m/(1+m/2)` exceeds 1.0 at m > 2 deaths/person-year, driving survivorship NEGATIVE: short test runs
  returned l(15) = −0.091, l(25) = −0.500. No scored result was affected (a real arm never approaches m=2),
  but a survivorship that can go negative is not a survivorship. Clamped, negative control confirms
  l(x) = −0.111 without it.
- A duplicate keyword argument from a rename broke the campaign entrypoint and cost a 27-failure suite run,
  because I launched the suite without an import check.

**A PROCESS NOTE.** Editing source while the suite runs produces spurious failures: several tests read
`phase1_model.py` FROM DISK for token scans, so a half-written file fails them. Three such failures were
recorded and discarded on 2026-08-14.

**LITERATURE SURVEY (2026-08-14).** Registered `age_first_birth_yr` [16.2, 20.5] (Walker et al. 2006 Table
2, 15 forager societies; Gainj and Turkana excluded as horticulturalist/pastoralist) and `m_5_15` = 0.010
(GK07 p.330 verbatim). The survey also established that **e0 is NOT diagnostic**: Sweden 1751–59 had e0 = 34,
inside the forager range of 21–37. Neither is e45 (20.7 vs 19.8 across HG and forager-horticulturalist) nor
MRDT (6–10 yr, a human constant). **Score on l(15), r and the juvenility index.** And GK07 Fig. 9: *"forager
mortality is narrowly confined, fertility ranges widely from below 4 to as high as 8"* — regulation runs
through fertility. **NO forager anchor exists** for joint orphanhood, never-married-by-30, widowhood, sex-
specific life tables, or CBR/CDR; those report NO-ANCHOR rather than being dropped. **Ellison remains
unobtained** and is the single gap blocking a fertility-response timescale.

---

## Addendum 44 — The model is Malthusian, so no hazard fix can raise e0 (2026-08-14, R-106)

**THE a2 MODULATOR, DECOMPOSED.** `_a2_mult` multiplies three live factors into Siler's Makeham term and only
the PRODUCT was ever visible. Per-factor observers, measured on a 600-step campaign:

| factor | measured | what it was meant to be |
|---|---|---|
| `risk_mult` | **0.630** | ~1.1 — accidents ≈10% of HG deaths (Hill, Hurtado & Walker 2007) |
| `density_mult` | **2.435** (1.329 with `enable_density_reference`) | — |
| `synergy_mult` | **1.000**, mean body condition 1.0000 | up to 2.5 at zero condition |

**`risk_mult` RUNS BELOW 1.0 — terrain risk is a net PROTECTIVE factor.** It divides by a GLOBAL mean risk
(`risk_cell / risk_ref`) while agents self-select into low-risk cells, so the realised mean sits on the wrong
side of 1. The normalisation is not wrong in itself; the reference is a world mean and the sample is a biased
subset of it. Filed, not fixed.

**CORRECTION TO ADDENDUM 43 — the density fix is not "near-neutral", it is COMPENSATED.** Addendum 43 recorded
e0 17.87 → 17.96 and called the fix near-neutral. A controlled pair shows the fix working exactly as designed
and the system absorbing it:

| | 600 steps | 15,000 steps |
|---|---|---|
| e0 gain | **+5.8 yr** (21.6 → 27.4) | **+0.09 yr** |
| `density_mult` | 2.435 → 1.329 (−45%) | same |
| `a2` product | 1.414 → 0.719 (−49%) | same |

In the 15,000-step pair, `m_other` in the 5–15 band fell **0.0298 → 0.0165** while `m_starv` rose **0.0208 →
0.0339**, holding total mortality flat at 0.0506 → 0.0504.

**THE STRUCTURAL RESULT.** Once the carrying-capacity ceiling is repaired (Addendum 43), the model is
MALTHUSIAN: equilibrium e0 is set by the food-to-population balance, NOT by the hazard parameters. Reduce any
hazard and the population grows until starvation restores the same total mortality. **No hazard fix can raise
equilibrium e0.** The `hg_villages_off` trajectory shows it directly — e0 falls 30.15 → 18.5 → 17.87 as the
population fills the world, and thereafter is flat while intake p50 fluctuates 2.3–3.9.

The only levers on equilibrium e0 are FERTILITY (a lower equilibrium density) or PRODUCTIVITY. That is what
Gurven & Kaplan 2007 Fig. 9 says independently: *"forager mortality is narrowly confined, fertility ranges
widely from below 4 to as high as 8"*. Regulation runs through fertility, and this model now agrees.

**A CLAIM OF MINE CORRECTED BY ITS OWN TEST.** I first recorded that `enable_nutrition_synergy` is DEAD, having
measured `synergy_mult` = 1.000 and condition = 1.0000 on a campaign run. The CTB failed at once: in the
smaller, poorer test world condition is **0.49** and the synergy is live at ~1.76. **The mechanism is not
inert — it is SILENCED BY THE WORLD**, because campaign agents eat 2.6x their requirement and `_condition`
saturates. That is the same root cause as the dead energetic fertility brake, which reads an intake signal
that saturates for the same reason. TWO MECHANISMS, ONE FAILURE. "World-dependent" is a fixable finding;
"inert" would have aimed the next fix at the wrong target.

**TASK #70 IS PARTLY REHABILITATED.** Its premise — that the energy signal never enters the FAO/IOM window
[1.0, 1.2] — was falsified on the RUNAWAY world. Re-measured at equilibrium on the repaired world:

| | runaway world | repaired world |
|---|---|---|
| intake EMA median | 6.62 | **2.58** |
| EMA p10 | 1.72 | **1.41** |
| below 1.2, raw | 4.7% | **8.5%** |
| below 1.2, after the EMA | **0.0%** | **2.0%** |
| `fert_factor_sat` | 0.999 | **0.971** |

Still small, but no longer zero, and 2.5x closer to the window. The refractory route deserves a re-test rather
than the flat falsification recorded earlier.

**BASELINE PAIR, 15,000 steps, ceiling repaired, sha dff049f, both stable.** `hg_villages_off` pop 3,916
(0.27x Binford), `hg_densref` pop 5,062 (0.35x). Both `structure_ok = False`: `frac_child` 0.535/0.559 against
[0.287, 0.454] and `dependency` 1.262/1.398 against [0.598, 0.899]. `band_med_adults` **10 against Hill's
28.2**. Cohort parity 8.46 and synthetic TFR 8.37 now AGREE, confirming the arms are in steady state — the
divergence seen on the 400-step run was the diagnostic working, not an artefact.

---

## Addendum 45 — The refractory lever works, and delivers a tenth of what is needed (2026-08-15, R-106)

**THE TRIO.** Three arms at one sha (96caab9), 15,000 steps, differing by ONE setting at a time. Control =
`hg_villages_off`; `hg_refrac` adds `enable_energetic_refractory`; `hg_refrac_ema` adds the Ellison-anchored
one-month EMA half-life (`intake_ema_alpha` 0.04 → 0.5) on top.

| marker | control | +refractory | +refractory & EMA | anchor |
|---|---|---|---|---|
| realised TFR | 8.372 | 8.355 | **8.005** | [4.69, 8.03] |
| cohort parity | 8.46 | 8.57 | 8.12 | — |
| realised IBI mean | 38.0 | 38.1 | **39.5** | — |
| e0 | 17.87 | 17.90 | **18.35** | [21, 37] |
| l(15) | 0.424 | 0.426 | **0.434** | 0.66 |
| starvation share | 0.364 | 0.362 | **0.352** | — |
| markers in band | 3/16 | 3/16 | **4/16** | — |

**PREDICTION 1 CONFIRMED — the mechanism alone does nothing.** `hg_refrac` moved TFR by 0.017 and e0 by 0.03,
i.e. nothing. The shipped 17-month EMA smooths away the very signal the mechanism reads. This was stated
before the run.

**PREDICTION 2 CONFIRMED — the Ellison timescale is what makes it live.** With the one-month half-life, the
fraction of women below the FAO/IOM window rises **0.0195 → 0.0476**, realised IBI mean rises 38.0 → 39.5
months, and **`realised_tfr` crosses from OUT-OF-BAND into PASS** (8.005 against a [4.69, 8.03] band). That
is the first marker this mechanism has brought into band, and it is attributable to the TIMESCALE rather than
to the mechanism, because the two arms separate them.

**PREDICTION 3 CONFIRMED, WEAKLY — e0 rose.** 17.87 → 18.35, **+0.48 yr**, with l(15) 0.424 → 0.434 and the
starvation share falling 0.364 → 0.352. The direction is exactly what Addendum 44's Malthusian reading
requires: lower fertility → lower equilibrium density → less starvation → longer life. **Addendum 44 STANDS.**
The refrac-only arm moved e0 by 0.03, so the EMA arm's 0.48 is roughly sixteen times that noise floor — but
this is ONE SEED and the claim deserves replication before it is leaned on.

**THE MAGNITUDE IS ABOUT A TENTH OF WHAT IS NEEDED.** The iso-growth identity requires TFR ≈ 5.45 at this
l(15); the mechanism delivers 8.005. The iso-growth gap barely moves (+1.56 → +1.49 percentage points). e0
needs +19 years and gains 0.48.

**WHY, AND IT IS THE SAME REASON AS EVERY PREVIOUS FAILURE.** Even with the anchored fast EMA, only **4.8% of
women fall below the physiological window**. The other 95% get no stretch at all, because the median woman
takes in **2.85x her requirement**. The lever is correctly built, correctly anchored and correctly wired, and
it has almost nothing to act on.

**FOUR MECHANISMS ARE NOW DEAD FOR ONE REASON.** `enable_energetic_fertility` (the reserve saturates at its
cap), `enable_intake_fertility` (the intake ratio sits at 2.6-3.4x the window), `enable_nutrition_synergy`
(body condition pins at 1.0 — see Addendum 44, where this was first misreported as inertness and corrected to
world-dependence), and now `enable_energetic_refractory`. Every energetically-gated mechanism in the model is
silenced by the same fact: **the world feeds almost everyone above the level at which any energetic signal
carries information.**

**SO THE ARC RETURNS TO WHERE THE SUPERVISOR PUT IT ON DAY ONE** — *"either our bands are idiots and settle
too easy or this world is too abundant"* (2026-08-12). Task #65 measured the first half then: 40% of habitable
land passes the village-site test, because `settle_persist_threshold` sits at the MEDIAN of S_pot. This
addendum measures the second half from the demographic side: the median agent eats ~2.85x maintenance, and
that single fact has now defeated four separate mechanisms and every mortality fix attempted since Addendum
42. **The productivity question is no longer deferrable; it is the binding constraint on the whole
demographic layer.**

**WHAT IS NOT CLAIMED.** That `refractory_stretch_max = 1.436` is right — it is a bracket endpoint and was
never swept, because the mechanism turned out to be signal-limited rather than magnitude-limited. Sweeping it
before fixing the supply would be tuning a lever that is not attached to anything.

---

## Addendum 46 — The cell split was age-blind, and that is why the hazard was age-blind (2026-08-15, R-106)

**THE SUPERVISOR'S QUESTION.** *"What then will move the demography? If not food — something is broken in
demographic mechanisms."* This addendum answers it. Something was broken, it was not a demographic mechanism,
and it was not food. It was the rule that decides who eats.

**THE DEFECT.** `substrate.compute_harvest_shares` divided a cell pool FLAT per head at κ=0: `base = S / n`.
Every occupant claimed the same absolute kcal regardless of age. **59% of a canonical population is under 15**
(measured age_0_5 26.0%, age_5_15 33.2%), so a newborn claimed exactly what a 30-year-old hunter claimed.

**THE MEASUREMENT THAT NAMES IT.** The realised hazard was FLAT across the whole of life:

| age band | 1-5 | 5-15 | 15-30 | 30-45 | 45-60 |
|---|---|---|---|---|---|
| realised hazard /yr | 0.069 | 0.057 | 0.060 | 0.059 | 0.064 |

Siler ACHE_FOREST gives **0.0141/yr at age 30**. The excess is ~0.045/yr and it does not vary with age.
Starvation cannot produce that — starvation kills the small and the old first. An age-blind split can, and it
was the only term in the model that could.

**THIS RESOLVES THE PARADOX OPEN SINCE ADDENDUM 44.** The median agent eats 2.8x requirement AND
`starv_share` is 0.51-0.67. Both are true. Only ~3% sit below the floor at any instant
(`intake_ema_frac_below_hi` 0.031); the FLUX through that state carries the deaths, at every age at once.

**A HYPOTHESIS OF MINE IS FALSIFIED, and is recorded rather than dropped.** Task #71 predicted the starving
would be ISOLATED agents. They are not. `starv_occ_at_death` 44.1 against `starv_occ_of_living` 27.7 — the
dead sit in cells MORE crowded than the living. The earlier 6.5-against-71.4 reading came from a single arm
and did not replicate. The isolation-flux hypothesis is dead.

**THE FIX.** `compute_harvest_shares` gains an optional per-occupant CLAIM WEIGHT applied before the κ
contest. `claim=None` reproduces the historical split bit-exact. Two flags, because they are two separate
assertions, and neither introduces a new number — each reads a ramp that already exists:

- `enable_need_weighted_shares` — claim ∝ `consumption_factor` (cons_min 0.3→1.0). [ANCHORED — Kaplan 2000,
  already the citation on `BaseAgent.consumption_factor`.]
- `enable_eta_weighted_shares` — claim ∝ `eta` (eta_min 0.2→1.0). Recovers the ~26% of every cell pool
  claimed by someone who cannot convert it.

**THE PREDICTION WAS STATED BEFORE THE MEASUREMENT, and it held at BOTH ends.** Coastal-temperate, seed 0:

| marker | control | need | eta | both | anchor |
|---|---|---|---|---|---|
| m 0-1 | 0.1366 | 0.1666 | 0.1702 | 0.1819 | ~0.20 (Aché) |
| m 15-30 | 0.0611 | 0.0539 | 0.0538 | 0.0494 | 0.005-0.010 (G&K) |
| m 30-45 | 0.0594 | 0.0534 | 0.0522 | 0.0493 | 0.005-0.010 |
| **e15** | **15.92** | **17.60** | **17.73** | **18.85** | **~35** |
| e45 | 12.95 | 13.57 | 13.69 | 14.03 | |
| frac_double_orphan | 0.0394 | 0.0291 | 0.0263 | 0.0202 | |
| frac_both_parents_alive | 0.746 | 0.776 | 0.779 | 0.801 | |
| band_med_adults | 9.74 | 10.25 | 10.18 | 11.06 | 9-25 |

Monotone in how much claim weighting is applied. Family structure improved without being targeted.

**THE CTB IS LOAD-BEARING, CHECKED RATHER THAN ASSERTED.** 26 tests pass, and 4 FAIL under a perturbation
that disables the mechanism. The control that decides interpretability is
`test_all_adult_cell_is_untouched_by_*`: every adult has `consumption_factor` 1.0, so an all-adult cell must
not move. If it did, the effect would be a code-path artefact rather than age composition.

**A SIDE EFFECT PREDICTED BEFORE IT WAS MEASURED.** Task #77 recorded that this change would move the spatial
distribution. The savanna reachability gate that failed at 0.058 now measures 0.210, population 861→1017. The
threshold was NOT touched.

**WHAT DID NOT MOVE, AND IT MATTERS MORE THAN WHAT DID.** `starv_share` is 0.67 in EVERY arm. TFR is ~10 in
every arm. The claim weight changed WHO starves, not HOW MANY. That CONFIRMS Addendum 44 rather than
overturning it: total deaths are still set by the food-to-population balance. This fix redistributes them
across ages.

**THE SHARPER DEFECT THIS EXPOSES.** `m_0_1` now nearly reaches its anchor (0.182 vs ~0.20), but `l15` moved
the WRONG way, 0.399 → 0.357 against an anchor of 0.55-0.60. Those two are compatible only if mortality
between 1 and 15 is far lower than the model's — it is not (`m_1_5` 0.080, `m_5_15` 0.054, against `m_30_45`
0.049). **The hazard is still nearly flat from 1 to 60.** Real foragers have a deep survival trough across
ages 5-40 that this model lacks. The claim weight fixed the SIGN of the age gradient at the infant end; the
trough is a separate, still-open defect.

**HONEST SIZE OF THE GAIN.** e15 closes ~15% of its gap to 35. Prime-adult hazard falls 17% where a 5-10x
reduction is needed. This is a real, correctly-signed, mechanism-driven improvement. It is NOT a solved
demography.

**A METHOD NOTE, because it saved four CPU-hours.** Two of the four arms were cut short at ~13800 steps. I
began a re-run, then tested the assumption instead: reading the two COMPLETE arms at BOTH 13875 and 15000
changed every marker the finding rests on by **≤0.3%**, against effect sizes of 17-33%. The truncation is two
orders of magnitude below the signal, so the re-run was cancelled. The endpoint check is three minutes of
arithmetic; the re-run was four hours.

**WHAT IS NOT CLAIMED.** That the claim weight fixes the demography — it does not; it fixes the shape, and the
level remains wrong. That `both` is the right adoption — it is canonically ON via C_ALLON per the standing
rule, and every mortality-shape marker improves monotonically, but the arms are ONE world and TWO of them are
single-seed. That the residual flat hazard is understood — it is not.

---

## Addendum 47 — The population is not food-limited; it fails to disperse (2026-08-22, R-106)

**THE HEADLINE, and it retires a claim this document made three addenda ago.** Addendum 44 concluded "the
model is Malthusian, so no hazard fix can raise e0". The arithmetic there was right and the label was wrong.
A population sitting at **4.8× BELOW** Binford's packing threshold regionally, on **13% of its habitable
land**, with the median agent eating **2.7× requirement**, is not limited by carrying capacity. It is limited
by a local crowding pathology. Every carrying-capacity reading taken between Addenda 44 and 46 should be
re-read in that light.

### The packing paradox

A forager population cannot be simultaneously PACKED (locally dense enough that Binford says it would
intensify) and SPARSE (regionally nowhere near filling its range). Measured on coastal-temperate, seed 0:

| | value | anchor |
|---|---|---|
| regional density | 0.0174 /km² | **4.8× below** Binford packing 0.091 |
| local density | 0.131 /km² | **1.4× above** it |
| land used | 13.3% | — |
| km² per band | 214 | below its own 314 km² catchment (Vita-Finzi & Higgs) |
| corr(forage, people) | **+0.12** | on a landscape with a 5× productivity range |
| top-decile land occupied | 34.6% | — |

The check needs NO new number: it uses Binford's filed 0.091 twice, once per side. It is now WIRED
(`demography.spatial_health`, a `!! SPATIAL:` banner in every campaign snapshot) rather than written down,
because a table nobody reads is what allowed this. Verified firing from the first snapshot of a live run.

### SubstrateConfig was outside the config system

`run_campaign` built `SubstrateConfig` inline from `**GRP`, imported from a 2026 one-off script, while
`config/parameters.toml` — the authoritative file — stated the grouping drives were **OFF**:

| field | the file said | every campaign ran |
|---|---|---|
| `group_safety_max` | 0.0 | **8.0** |
| `group_mate_min` | 0.0 | **15.0** |

Those two multipliers make leaving a band of 30 cost **20.6×** in perceived yield, against a terrain signal
whose entire range is 4.8× — clustering outweighed the whole landscape by 4.3×. The same
`DemographyConfig + ClimateConfig` pair was hardcoded in FOUR places (`gen_runconfig.resolved_canonical`,
`runspec.load` validation, `make_runconfig --set`, and the campaign's construction), and SubstrateConfig fell
through every one. `runspec.build` was ALREADY generic over all three modules — the design was right and only
the guards were narrow. Fixed in five bit-exact steps, and the fidelity test is now parametrised over owner
classes rather than checking DemographyConfig alone.

### THE HYPOTHESIS THAT FOLLOWED WAS FALSIFIED

Having found a 20.6× clustering force, the obvious inference was that it caused the crowding. **It does not.**
Ablating both grouping drives entirely moved land use 13.3% → **14.1%**, and `corr(forage,people)` got WORSE
(+0.120 → +0.082). Five arms — mobility radius, agglomeration attraction, cohesion, E.1 safety, E.2 mate
access — every attraction term nameable, and **none disperses the population**. The constraint is not any
single attraction parameter, and that is recorded here because the 20.6× number is seductive and wrong.

Note also `disp_radius` came back BIT-IDENTICAL to control: `mobility_max_radius` only binds where NPP < 150
g/m²/yr, which never occurs on occupied land. A knob raised 6 → 20 changed nothing.

### TWO CLAIMS OF MINE, WITHDRAWN

**(1) "Villages form on non-optimal areas" — WITHDRAWN.** Every spatial claim in this arc was scored against
`forage_kcal`. Village siting reads `S_pot = max(aquatic_food, cultivability)`, and the two are
**UNCORRELATED (+0.027)**. Scored against the field that actually governs it, sites sit at S_pot **0.934**
against a habitable mean of 0.353 — 2.6× better than average and near the maximum. **Villages are well
sited.** What survives, restated properly: only 9.5% of top-decile S_pot land carries a site.

**(2) The isolation-flux hypothesis (task #71) — FALSIFIED.** The dead sit in cells MORE crowded than the
living (`occ_at_death` 44.1 vs `occ_of_living` 27.7). The earlier 6.5-against-71.4 reading came from a single
arm and did not replicate.

### Two terrain-generator defects, found by single-biome testing

The generator had never had a coherence benchmark. It is structurally SOUND — determinism, no NaN, rivers and
shore never on water, `aquatic_food` bounded and only where there is water, every biome label re-derivable
from its own climate, and **every filed per-biome forage anchor reproduced at 0.96–1.00** once shore cells are
excluded (the `SHORE_BONUS_KCAL` addition, verified by a positive control so the exclusion cannot hide a real
defect). Two real defects:

**(a) Rivers are drainage AREA with no water balance.** `flow = np.ones()` gives every cell one unit
regardless of rainfall, so across 20 worlds **deserts are 1.63× WETTER than forests** (0.075 vs 0.046). That
propagates: `aquatic_food` scores desert rivers as cold anadromous fisheries, `S_pot` ranks desert 0.413 >
grass 0.404 > forest 0.259, and villages settle the desert at 2.5× enrichment. Weighting the accumulation by
Budyko runoff (VERIFIED and filed; parameter-free) reverses the ordering to forest 0.283 > grass 0.228 >
desert 0.171 and the river ratio to 0.49.

**(b) The river threshold is RELATIVE.** `riverThresh = fmax * (0.10 − waterK*0.06)` is a fraction of the
world's own maximum flow, so "is this a river" means "is this in the top decile of this world's drainage" —
equally true in a rainforest and a desert. The 100%-desert world went 474 → **519** river cells under Budyko.
An earlier version of the test asserted that world dropped to ~0 rivers; it did under the crude
`Q = max(0, P − PET)`, but FOR THE WRONG REASON — that form returns exactly zero everywhere P < PET, so `fmax`
was 0, the guard substituted 1.0, and every cell failed the comparison. **An accident of a broken runoff model
passing a test by luck.** The fix this points to is an ABSOLUTE discharge threshold, which introduces a number
this project has not filed.

### Three scored markers are provisional

`_maintain_settlements` counts everyone inside a site's 25-cell, 2,500 km² window, and the windows OVERLAP:
**184 sites × 25 cells = 4,602 window-cells over 229 OCCUPIED cells**, so every occupied cell lies inside ~20
different sites' persistence windows. `n_settle = 184` with `settle_med = 11` is ONE clustered population
counted twenty times. `primate_ratio` and `zipf_slope` read the same list, so #12's clean-looking Zipf −0.98
is a rank-size slope over phantom settlements. Markers #3, #12, #13 are flagged PROVISIONAL; #3's prior
"46/52 arms PASS" is withdrawn.
`enable_exclusive_village_membership` is NOT the fix: re-tested against this question rather than the spacing
question it was rejected for, it failed the discriminator — population fell 9.5%/63.7% across two seeds and
founding churn rose 8×. It buys a correct-looking number by destroying the population that produced it.

### What single-biome testing found that the mixed world hid

Forest and savanna run. **Arid and mountain go extinct inside 80 steps, 95% starvation, ZERO births**, and the
mixed world never pressed on it because base_s0 has 1,229 viable anchor sites. Four predictions were made and
all four FAILED: cluster seeding, capacity-scaled grouping, both together, and seeding at the anchored
density. The measured cause is a startup transient — the bottom intake decile sits at 0.62× requirement from
step 1 with reserves under one month, 90% die in six steps, and the ~30 survivors on good land thrive
(intake 2–5×) but are below the breeding threshold. The arid world is NOT uninhabitable: 1,471 of its 3×3
neighbourhoods can feed ≥15 people, and the filed density (0.005/km², Long 1971 / Cane 1990) clears its
stability ceiling `K/(1+DEPLETE_FRAC)` = 1.33 by 2.7×.

**One real defect was found there:** `comove_footprint = 0` ("exact snap") collapses every co-moving family
onto ONE cell, so the annual pairing gate halves the occupied-cell count in a single step (110 → 75, occupancy
1.07 → 1.56). Two competing explanations were falsified first — ablating the annual drought shock and ablating
band cohesion each left it untouched. The fix was ALREADY BUILT AND DARK: `comove_footprint_scaled`, k ∝ 1/NPP
on the Kelly/Binford shape, giving **k = 0 on every rich world** (bit-exact) and k = 2–3 on poor ones.

### What is NOT claimed

That the demography is fixed — `e15` is 18.9 against ~35, TFR ~10 against 5–8. That any of tonight's
mechanisms rescues arid — none does; it still dies in the first seasonal trough, and the reason is now
anchored: the model implements only CENTRAL-PLACE overwintering storage, and the mode that applies to arid
Australia (dispersed caching, keyed to multi-year unpredictability) was never built. That `runoff_rivers`,
`enable_capacity_scaled_grouping` or `comove_footprint_scaled` should be adopted — all three remain OFF
pending a supervisor call. And that the residual flat hazard is understood — it is not.

---

## Addendum 48 — Earth climate becomes the baseline, and Addendum 47's numbers are superseded (2026-08-23, R-106)

**READ THIS BEFORE QUOTING ADDENDUM 47.** Every quantity in Addendum 47 was measured on a planet with more
than twice Earth's obliquity. The FINDINGS there stand; the NUMBERS are superseded by the ones below.

### The canonical world was an outlier, by lottery accident

`a_seas` — the seasonal amplitude of the food field — is drawn per world from an obliquity lottery,
ε ~ U[0°, 60°], as `a_seas = 0.40 · sin ε / sin 23.4°`. **Seed 0, which every canonical run in this project
uses, draws ε = 50.7° → a_seas 0.779**: the second highest of twelve seeds, against a median of 0.464 and
Earth's 0.4.

| seed | ε (deg) | a_seas | trough yield |
|---|---|---|---|
| **0 (canonical)** | **50.7** | **0.779** | **22.1% of mean** |
| median of 12 | ~27 | 0.464 | 53.6% |
| Earth | 23.4 | 0.400 | 60.0% |

**That amplitude is not anchored.** `obliquity_to_amplitude`'s own docstring calls it *"a PROVISIONAL bounding
heuristic onto the Earth band, NOT a sunlight→food transfer function (forage amplitude is rain/phenology-
driven)"*. An insolation heuristic was doing load-bearing work on food seasonality in every result.

### It is why arid could not be fixed

At a_seas 0.779 an arid cell yields **0.44 BURN** at the seasonal trough against a lone adult's requirement of
1.0. **The world cannot feed anyone for part of every year — at any density, however seeded or dispersed.**
Four mechanism-level fixes (cluster seeding, capacity-scaled grouping, both together, seeding at the
anchored density) were each predicted to work and each failed, because all four were tuned against a periodic
hard floor that none of them could lift. The floor should have been checked before the second attempt, let
alone the fourth.

### Adopted (supervisor call, 2026-08-22)

**Earth climate is now the default.** `C_CLIMATE` defaulted to `"1"` — every channel on; it now defaults to
`"0"`, so `ClimateConfig`'s class defaults apply, and those already ARE the Earth baseline (a_seas 0.4,
seasonality live, lottery / interannual / regime-shift / caribou / llanos / eccentricity off). Variability is
opted INTO with `C_CLIMATE=1`, and belongs to a later stage.

Three mechanisms adopted alongside it: `runoff_rivers` (Budyko-weighted flow; reverses deserts being 1.63×
wetter than forests), `enable_capacity_scaled_grouping` (a group larger than the land feeds earns no further
benefit), `comove_footprint_scaled` (k ∝ 1/NPP; fixes the annual pairing collapse).

### The re-measurement

| | Addendum 47 (a_seas 0.779) | Addendum 48 (Earth) | target |
|---|---|---|---|
| pop | 2,760 | **3,841** | — |
| land used | 13.3% | **14.3%** | > 50% |
| regional /km² | 0.0174 | **0.0242** | ~0.091 |
| corr(forage, people) | +0.120 | **+0.157** | > +0.50 |
| top-decile occupied | 34.6% | **38.4%** | > 80% |
| km² per site | 85 | **125** | > 314 |
| settle_med | 11.5 | **15.4** | 50–250 |
| e15 | 18.9 | **19.4** | ~35 |
| TFR | 9.96 | **9.93** | 5.0–8.0 |
| starv share | 0.666 | **0.661** | — |
| PACKING PARADOX | yes | **yes** | no |

**Everything moved the right way and nothing was fixed.** Population +39%, but the paradox holds, land use is
still 14% against a 50% target, and **TFR and starvation share are unchanged**. Arid survives 294 steps
against 29–52 originally and 150 for Earth-climate-alone — roughly 6× — and still goes extinct.

### A confound in my own test design, stated rather than buried

`earth_forest` was presented as the control for the claim that the adoptions are bit-exact where land is
productive. **It is not a control**: it changes the climate AND the three mechanisms at once, so its +31%
population against `biome_forest` is unattributable. That claim was measured only on unit arithmetic (0 of 72
rich configurations changed; footprint k = 0 at forest NPP) and **remains untested at run scale**. An arm with
the two behavioural mechanisms ablated is running to separate them.

### What is NOT claimed

That the demography is fixed — `e15` 19.4 against ~35 and TFR 9.9 against 5–8 are barely moved. That arid is
solved — it is not, and the anchored reason stands: the model implements only CENTRAL-PLACE overwintering
storage, and the mode that applies to arid Australia (dispersed caching, keyed to multi-year unpredictability)
was never built. That the adoptions are individually validated at run scale — one arm is still running to
test that. And that `runoff_rivers` is properly configurable — it is a TERRAIN knob outside the config system,
the same defect class as the `SubstrateConfig` breach and `ClimateConfig.a_seas` being overridden by the
lottery, both found this week.

---

## Addendum 49 — Fertility solved: it was two config errors, not a mechanism (2026-08-24, R-106)

**THE RESULT.** On a warm world with both fixes active, the demography reaches its forager anchors for the
first time in this project, and life expectancy rose 9 years as a free consequence:

| | earth_base (broken) | fert_warm (fixed) | anchor |
|---|---|---|---|
| %egalitarian | 8% | **100%** | >80 |
| surplus_med (false storage) | 0.76 | **0.00** | ~0 |
| IBI median | 24 | **35** | 37 (Aché) |
| TFR | 9.9 | **7.5** | 5–8 |
| CBR /1000 | 65 | **53** | 45–55 |
| **e15** | **19.4** | **28.5** | ~35 |
| starv share | 0.66 | 0.59 | — |

TFR and CBR are IN BAND for the first time. IBI is at 35 against a 37 anchor. And **e15 rose from 19.4 to 28.5
with no mortality parameter touched** — the "dying is the bill for the breeding" chain, confirmed: the
population is stationary, births fell, deaths followed.

### It was TWO config errors, both the same defect class

Neither the fertility mechanism nor the society classifier was wrong. Each was fed a corrupted input, by an
override silently defeating an anchored default — the class of defect this arc found four times (SubstrateConfig
`**GRP`, the `a_seas` lottery, and these two).

**Cause 1 — the classifier read LOCAL density (Addendum 48 groundwork; fixed `ea725c6`).** The morph
classifier asks "is this band packed past Binford's 0.091/km²?" — a REGIONAL threshold. It was fed
members/occupied-cells, a LOCAL density. Because the model crowds everyone onto ~14% of the land, every band
read as packed → chiefdom → 14-month refractory. 46–57% of a pure forager world came out stratified. Fix: feed
the classifier members/(range share), the scale Binford's number means. Stratified share → 0.

**Cause 2 — storage was ungated (fixed `f92eb83`).** `realistic_forager_demog()` overrode
`storage_temp_threshold_c = 100.0`, so every cell on every world counted as "overwintering" and stored. A warm
tropical world with no winter stored anyway (surplus 0.62), which read as `complex_forager` → 22-month
refractory. The correct value is Binford's ET 15.25 °C — the class default, named in the field's own doc, on
the scale of the model's temperature field (tropical 21, temperate 10, boreal 2 °C). The 100 was an
un-annotated test convenience that leaked into the production preset. Fix: delete the override. Warm worlds now
store nothing and stay egalitarian; only genuinely cold worlds store — Testart's distinction.

### A correction to my own reasoning, on record

After the FIRST fix alone (temperate world, storage still ungated), e15 moved only +0.8 years, and I wrote that
this WEAKENED the fertility→mortality chain. That was wrong: only half the fix was active. With BOTH causes
removed, e15 moved +9.1 years. The chain is not weak; the earlier measurement was on a half-fixed run.

### Two legitimate regimes, not one target

This is the WARM world (immediate-return, egalitarian, IBI ~35). The TEMPERATE world correctly DOES store, so
its bands read complex and space births shorter (~24), and that is the Neolithic Demographic Transition
(Bocquet-Appel 2011), not a bug. A cold storing world SHOULD out-breed a warm mobile one. Both must be reported
as the two regimes the model now distinguishes correctly, rather than forcing both to the Aché mobile anchor.

### What is NOT solved

e15 is 28.5 against ~35, and l15 is 0.38 against 0.55–0.60 — closer, not closed. The residual mortality is now
CONCENTRATED IN CHILDHOOD (m_1_5 at 3.3× Siler, m_5_15 2.7×), where before the whole curve was flat; prime-
adult hazard has fallen to ~1.8× Siler. The paradox persists in age-graded form: the bottom intake decile eats
2.7× requirement, yet 59% of deaths are "starvation", and they are children. Provisioning and both claim-
weights are ON, so it is not a missing mechanism — something is defeating the provisioning that exists. That is
the next thread (child mortality), diagnosed rather than guessed.

---

*End of RESULTS — seeded 2026-06-05 (R-1 routed from former hypothesis H1(ii)). Append-only.*
