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

---

*End of RESULTS — seeded 2026-06-05 (R-1 routed from former hypothesis H1(ii)). Append-only.*
