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

**Why — the operative heterogeneity is SPATIAL competition near carrying capacity, not temporal "bad streaks."** Near K (δ=3) cells are crowded/poor, so per-capita shares are **sub-cap deterministically** — the cap-pinning argument (everyone fed to cap → surplus wasted) is false near K. Two Cred channels are active at CV=0: (a) the **meat harvest split** (high-Cred get more of a contested cell's meat), and (b) the **cell-occupancy movement contest** (`occ_wsum`/`w_self` are also `(cred+ε)^κ`-weighted → high-Cred secure better cells). Both are variance-independent. **G.3 only MODULATES**: the effect **peaks at moderate CV** (forest 0.73: Δmean_cred +0.093, deficit +0.118) and is **lower at the extremes** — CV=0 (spatial only) *and* CV=2.24 (savanna: meat is mostly near-zero with rare over-cap jackpots → the band lives on egalitarian forage, so Cred-weight has little meat to bite on). Forest-like variance is the sweet spot.

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

*End of RESULTS — seeded 2026-06-05 (R-1 routed from former hypothesis H1(ii)). Append-only.*
