# SiC Games · Phase 1 · **Carbon-on-Substrate (Cred coupling)** — Scoping draft

**Status:** SCOPING — red-teamed 2026-06-21 (NEEDS-REVISION), **then supervisor-corrected** (the red-team
*and* the first revision over-corrected into a "shock/catastrophe" frame — wrong; see the central finding).
Goal: a **working Carbon (hierarchical) simulation** — bring the Cred/status dynamics onto the validated
demographic substrate so κ-weighted meat sharing produces a real status hierarchy with anti-fragile
demographics. **Silicon deferred.** Builds on the game economy G.1+G.2 (commit c8d3f31, §4.5.5).

> **CENTRAL FINDING (supervisor-corrected 2026-06-21; governs everything below).** The Carbon advantage is
> **compositional, not aggregate, and lives in ORDINARY foraging variance — no catastrophe needed.** Two
> steps:
> 1. **The red-team's wash-out is real only for a DETERMINISTIC meat economy.** Cap-pinning (R-8,
>    `min(total,cap)` `phase1_model.py:335`) discards a high-Cred agent's larger share **only when everyone is
>    fed to cap.** That is the current build (G.3 not yet built). **With stochastic returns (the real HG case —
>    forest meat CV 0.73, savanna 2.24), a bad streak routinely thins the band pool below cap-for-all, and
>    THEN the share rule decides who crosses the starvation floor.** Bad streaks / lean weeks / "no game" are
>    *ordinary variability*, not rare shocks — so the variance itself, at its anchored magnitude (attenuated by
>    band-pooling ~CV/√n), manufactures the sub-cap moments. **⇒ G.3 stochastic meat is the CORE mechanism, not
>    a deferred increment.**
> 2. **Fertility-pinning (R-16) fixes the aggregate death RATE, NOT who dies.** density-disease is a function
>    of local density ρ, not Cred, so it **cannot preferentially spare the high-Cred core.** With status-weighted
>    meat, starvation deaths **concentrate on the low-Cred periphery** while δ holds the aggregate at r=0. So a
>    **Cred→survival gradient lives at ordinary stochastic equilibrium** — it is *compositional* (who dies),
>    which R-16 does not touch, NOT *aggregate* (e₀, which R-16 pins). The red-team conflated the two.
>
> **⇒ A catastrophe/shock is NOT required** (the prior framing was wrong). The primary test is the **Cred–survival
> correlation under ordinary variance**; a big shock is only an *amplified* version, optional/secondary. Whether
> the gradient is large enough to matter (band size, CV, floor-proximity) is **empirical — the model measures
> it**, not asserted. **No RESULT recorded** until the model shows it with stats (this is a design hypothesis).

---

## 1. The integration reality — two model lineages must meet

The Cred dynamics and the demographic substrate were built as **separate models**:

| | **`oracle.py`** (Sugarscape-era Carbon/Si) | **`phase1_model.py` TerrainWorld** (demographic substrate) |
|---|---|---|
| Resource | SugarField | terrain NPP capacity + forage/meat split |
| Cred source | **joint-task co-working** clusters | none |
| Cred update | `cred=(1−decay)·cred+pending_delta`, decay 0.01 | none |
| Inheritance | `offspring.cred=f_C·mean_cred` (f_C=0.25) | none (φ trait fixed 0.5) |
| Status→advantage | softmax temperature, w_C, β-amplification | none yet (κ on meat exists but reads φ) |
| Demography | none (Sugarscape births) | Siler + IBI + biome (R-3…R-17, validated) |

This stage **ports the Cred mechanics onto TerrainWorld's rivalrous path** — it is an integration, not a new
mechanic. The thesis to reproduce: **R-1 anti-fragility** — under shock, a Carbon hierarchy protects its
high-Cred core (fast recovery); Silicon's equal sharing crashes together (dormancy cliff). On the substrate
the advantage channel is **Cred-weighted meat sharing**.

## 2. D1 (load-bearing) — meat must be weighted by `cred`, not `φ`

`compute_harvest_shares` weights by `(a.phi+ε)^κ`. But **`φ` is a fixed trait (0.5 for all)** and the evolving
status is **`a.cred`**. So today κ-on-meat is uniform — no hierarchy. **Fix:** the meat-share weight (and the
movement-contest `occ_wsum`, `phase1_model.py:283/304`) must read **`cred`** (accumulated status), not `φ`.
Options: (a) change `compute_harvest_shares` to read a `status` accessor that returns `cred`; (b) keep φ but
drive it from cred. **Recommend (a)** — a `status_of(agent)` hook so the contest weight is `(status+ε)^κ`.
**Red-team fixes (RT verified φ is uniform 0.5, `_make_agent:224`, and is read only by the contest weight on
the demographic path):** (i) the hook **defaults to `φ`** (preserves `test_substrate.py:59` /
`test_game_economy.py` which assert φ-weighting) and returns **`cred` only under the carbon flag**; (ii)
**cred-seeding is MANDATORY** when the hook reads cred — `cred` defaults to 0.0 (`base.py:74`), so an unseeded
carbon run collapses every weight to `(0+ε)^κ` (uniform). This makes the hierarchy *bite* on meat — but the
gradient only **materializes when meat is stochastic** (G.3): a uniform-share cap-pinned band shows nothing
(central finding).

## 3. D2 (the crux) — what is the Cred SOURCE on a forager substrate?

The Oracle earns Cred via joint tasks. Foragers don't co-work on sugar cells. Three options:

*(NB: the Cred SOURCE [A/B/C] is independent of the meat VARIANCE [G.3] — G.3 is in the first build either way;
A vs C is only about whether status is earned or seeded.)*
- **A — Earned from hunting/provisioning (lit-faithful; costly signaling, Hawkes 1991).** A successful hunter
  who contributes meat to the band beyond his own need gains prestige. G.3's per-hunter variance is what makes
  one hunter "stand out." Most realistic, most work, and carries the **runaway risk** (Cred→more meat→more
  Cred) the Oracle already had to guard (fc_sweep `_cred_runaway`, >5%/100 steps).
- **B — Port joint tasks** (cooperative hunts as the "task"). Reuses machinery but is awkward on the forager
  substrate and re-imports the Sugarscape framing we're trying to leave.
- **C — Heritable status, seeded (minimal; isolates the consequence).** Don't *earn* Cred; **seed** a Cred
  distribution and **inherit** it at IBI birth (mother's cred ×noise, or `f_C·mean_cred`). Cred-weighted meat,
  **under G.3 variance**, gives high-Cred lineages a survival edge in bad streaks; the hierarchy persists by
  **differential survival**, not earning. Tests directly: *does a heritable status hierarchy concentrate
  bad-streak mortality on the periphery and protect the core?*

**Recommendation: C-first, then A.** C isolates the project's actual question (does a Cred hierarchy →
anti-fragility on real demography?) with minimal new mechanism and **no Cred→Cred runaway** (the only dynamics
are inheritance + selection; G.3 supplies the *external* variance, not a feedback). Once C shows the
compositional gradient, **A** makes the hierarchy *endogenous* (earned from hunting + the runaway guard) as
increment 2. **B** rejected (Sugarscape re-import).

**C-first decay decision:** with no earning, per-step `cred_decay` would erode all Cred → flat. So **C-first
runs decay OFF (cred is a persistent heritable trait)**; decay returns with the earning source (A) that
balances it. Document this explicitly.

## 4. D3–D5 — inheritance, the shock, amplification

- **D3 Inheritance (port):** at `_do_births_ibi`, set `child.cred = inherit(mother.cred)`. Two sub-options:
  **(i)** noisy copy `mother.cred·(1±σ)` (vertical transmission — status runs in lineages, the heritable-status
  model); **(ii)** the Oracle's `f_C·mean_cred` (regression to the mean — weaker heritability). **Recommend (i)**
  for C-first (heritability is the point); make σ a config knob. Seed founders from a lognormal (or from a
  spread of φ→cred).
- **D4 The shock (the anti-fragility test):** reuse the **seasonal/catastrophe seam** (§4.1.7) or a one-off
  resource crash. Measure whether the high-Cred core survives + keeps reproducing (Carbon) vs collective
  collapse (Si, κ=0 comparison run). This is the R-1 reproduction on demography.
- **D5 Status amplification (β, defer):** `CarbonDecision.amplification = 1+β·tanh(cred/scale)` — the
  positive-feedback knob. **Keep β=0 for C-first** (it's a runaway accelerant; belongs with A + the guard).

## 5. Minimal first build (in / out) — REVISED

**IN:**
- **D1** — `status_of` hook (φ-default; `cred` only under the carbon flag; **seeding mandatory**) in
  `compute_harvest_shares` + `occ_wsum` so the meat/contest weight is `(status+ε)^κ`.
- **G.3 stochastic meat (NOW CORE, was deferred)** — per-hunter lognormal meat draw with the **per-biome CV**
  (`terrain.GAME_KCAL_STD`; forest 0.73), as a **band-level correlated draw** (a shared per-cell encounter
  shock, not N independent draws that wash to ~CV/√n), from `agent.random`. This is the variance that creates
  the sub-cap moments where the share rule decides survival. *Without it the first build is null (red-team).*
- **D3(i)** — heritable cred: founder seeding (lognormal, model RNG) + `child.cred = mother.cred·(1±σ)` at
  `_do_births_ibi`. Decay OFF, β=0.
- **carbon path** — `carbon_cfg` already wires `strategy="carbon"` (`_make_agent:196`). **Isolate the
  movement confound (RT-6):** seeding cred silently activates the temperature coupling
  (`diffusion_select_target` → `agent._decision.temperature` → `tanh(cred/scale)`); **hold σ_base** for the
  meat-isolation run (or measure dispersion separately).
- **Diagnostics + harness** — the Cred–survival correlation + Gini(cred) over a forest-Aché run, **κ>0 vs κ=0**.

**OUT (later increments):** earned/endogenous Cred (prestige-from-provisioning) + decay + the re-statisticked
runaway guard; an *optional amplified* catastrophe shock (time-varying `harvest_field` wrapper, R-6 `run_2d`
pattern — confirmed absent in the rivalrous path; **not needed for the first test**); D5 β; Silicon comparison;
multi-biome. *(Note: G.3 moved from OUT→IN per the central finding — it is the mechanism, not a refinement.)*

## 6. First forest-Aché Carbon run — what it measures (regime-aware)
The **aggregate** e₀ is fertility-pinned (R-16) and will be ~unchanged by κ — that is *correct*, not the test.
The signal is **compositional** and lives in the **ordinary stochastic variance** (G.3), no catastrophe needed:
1. **PRIMARY — the Cred–survival gradient under ordinary variance:** with G.3 on, does κ>0 (Carbon)
   **concentrate starvation deaths on the low-Cred periphery** while the high-Cred core persists (cred–survival
   correlation **> 0**), vs κ=0 (egalitarian) spreading deaths evenly (correlation ~0)? This is anti-fragility
   (R-1) in its native form — *who* the bad streaks kill. Measured at stochastic equilibrium; **no shock**.
2. **Magnitude is empirical:** report the gradient as a function of **band size** (pooling shrinks band CV
   ~CV/√n) and **floor-proximity** — it may be modest in the forest (CV 0.73) and large in the savanna (2.24).
   A null *here* (with G.3 on) would be the real "Carbon inert on this substrate" finding; a null *without* G.3
   is just the deterministic wash-out and tells us nothing.
3. **Hierarchy stable, not drifting/runaway:** gate on **Gini(cred) drift + the cred–survival correlation**,
   NOT `mean_cred` slope (a multiplicative noisy-copy inflates Gini/variance while leaving mean flat → the
   fc_sweep mean-slope guard misses it).
4. **Substrate intact:** with κ=0 (or game off) the run reproduces the validated baseline (e₀, density); 452
   green throughout (opt-in).
5. **OPTIONAL later — amplified shock:** a catastrophe (field crash) is just a *bigger* down-fluctuation; it
   sharpens the same compositional gradient. Build it only if the ordinary-variance signal needs amplifying.

## 6b. TIER-2 — active individualism / leadership (the Couzin–Henrich loop) [scoped 2026-06-21]

Tier 1 (above) is the **passive** advantage: Cred-weighted meat shares concentrate bad-streak mortality on the
periphery, on a *static* spatial economy. But the defining Carbon individualism is **active**: high-Cred agents
**lead** — they actively seek high-reward / high-variance cells (game), **peel off** viable cells to chase
bigger rewards elsewhere, and **pull companions with them** (they lead the band; the band follows in *most*
cases, not all). This is **not yet in the code**: the rivalrous movement (`diffusion_select_target`,
`substrate.py:66`) is a **purely local** (von-Neumann r=1) per-capita-yield softmax with **trait hooks held
neutral** (`affinity=1, crowd=1`, line 89) — no goal-seeking, no leadership, no prestige-cohesion.

**Models to build it from (validated literature):**
- **Couzin et al. 2005 (Nature 433:513)** — informed-minority leadership in collective motion: each agent
  balances a **private goal direction** vs **group cohesion**; a few informed individuals (leaders) steer the
  group *without signaling identity*. The mechanics of "leaders pull, band follows."
- **Couzin et al. 2011 (Science 334:1578)** — when leaders pull different ways, the band's **consensus vs
  split** depends on numbers + conviction → "**most cases, not all**" + band fission, for free.
- **Henrich & Gil-White 2001 (Evol. Hum. Behav. 22:165)** — **prestige-biased** deference/copying: low-status
  follow high-status. Grounds *why* low-Cred follow high-Cred (Cred = prestige) → cohesion biased toward
  **high-Cred neighbors**, not the band centroid.
- **Hawkes show-off / costly signaling** (our meat anchor) — the high-status hunter *leads* risky high-reward
  hunts; leadership and prestige are one loop.

**How it implements (activates the existing neutral hooks):** movement utility per agent becomes a tug-of-war
`U(cell) = w_goal·goal_pull + w_cohesion·prestige_cohesion − move_cost`, with `w_goal/w_cohesion` from the
existing `CarbonDecision.w_C_eff(cred)`. **Leader (high Cred):** large `w_goal`, **risk-seeking** goal_pull
(values the high-variance *game* cell's upside, not just the mean), small cohesion → peels off. **Follower (low
Cred):** small `w_goal`, large cohesion **toward high-Cred neighbors** → follows. Softmax temperature → "mostly,
not always" + splits. Two real pieces: (a) a **non-local goal** (leaders perceive/aim at the best cell in a
radius — extend perception beyond r=1); (b) the **prestige-cohesion** term.

**When + why it pairs with earned Cred (NOT Tier 1):** "high-Cred chases higher Cred" only *closes* when chasing
high-reward game **earns** Cred (the show-off circuit: lead → big kill [G.3 upside] → share wide → gain prestige
→ lead more). In the seeded C-first build, Cred doesn't grow from chasing, so leadership has no feedback. ⇒
**Tier-2 = leadership + earned-Cred TOGETHER** (Couzin movement + risk-seeking + Henrich prestige-cohesion +
prestige-from-big-kills, runaway-guarded). This is also where anti-fragility (R-1) gets its **spatial** form:
Carbon leaders explore high-variance opportunity (find resources after a shock) while egalitarian Si stays put
(dormancy) — exploration-vs-dormancy. Build **after** Tier 1 confirms the passive compositional gradient.

## 7. Red-team targets (for the fresh repo-grounded sub-agent)
RT-1: **D1 cred-vs-φ** — is reading `cred` in `compute_harvest_shares`/`occ_wsum` correct, or does φ have a
defined role that breaks? Does any existing test/path assume the φ-weight? Is a `status_of` hook clean?
RT-2: **D2 C-first legitimacy** — does seeded+heritable Cred (no earning) actually test the anti-fragility
thesis, or is *earned* Cred essential (i.e., is the consequence trivial/circular without an endogenous source)?
RT-3: **D3 inheritance** — noisy-copy (i) vs `f_C·mean_cred` (ii): does (i) runaway via selection (high-cred
lineages dominate → Gini→1)? Is decay-OFF coherent, or does heritable-no-decay inevitably ossify/explode?
RT-4: **the advantage channel** — does Cred-weighted meat actually produce a *survival* gradient given the
bang-bang reserve + per-capita sharing (R-8/R-14)? Or does the band-level economy wash the individual Cred
advantage the way it washed per-agent variance (R-14)? **This is the make-or-break:** if meat advantage
doesn't translate to differential survival, the whole Carbon mechanism is inert on this substrate.
RT-5: **runaway** — even in C-first (no β, no earning), can Cred-weighted meat → differential survival →
high-cred lineages dominate → effective runaway? Is the fc_sweep guard the right gate?
RT-6: **integration hazards** — porting Cred onto TerrainWorld: does `agent.cred` exist/initialize on the
demographic agents? Determinism with new draws? Does CarbonDecision's movement (temperature reads cred) already
partially couple, and does that interact with diffusion movement?
RT-7: **scope** — is D1+D3 the right minimal first build, or is the shock-test (D4) premature before
confirming the advantage channel (RT-4) in equilibrium?

## 8. Open questions for the supervisor (post supervisor-correction)
- **Q1:** Endorse **C-first** (heritable seeded Cred, no earning yet) **+ G.3 stochastic meat in the first
  build** (the variance is the mechanism), earned-Cred (A) as increment 2?
- **Q2:** Inheritance **(i) noisy lineage copy** vs **(ii) f_C·mean_cred regression**? (Recommend i.)
- **Q3 (resolved):** the test is the **Cred–survival gradient under ordinary variance** (who the bad streaks
  kill), measured at stochastic equilibrium — **no catastrophe**. A big shock is an optional later amplifier.
- **Q4:** Decay **OFF** for C-first (persistent heritable status) — agreed?
- **Q5 (resolved — do NOT record):** the "non-equilibrium" framing was an over-correction (supervisor); the
  advantage lives in **ordinary stochastic variance**, not off-equilibrium. Either way it is a **design
  hypothesis, not a RESULT** — record nothing until the model demonstrates it with statistics.

## 9. Red-team record (2026-06-21, fresh repo-grounded sub-agent) — VERDICT: NEEDS-REVISION → revised

All factual/code claims verified correct (two-lineage map, `oracle.py:740` cred-update, `:795/825`
`f_C·mean_cred`, `agent.cred` exists at `base.py:74`, `carbon_cfg` wires at `_make_agent:196`, φ uniform 0.5).
The gap was conceptual — the scoping didn't follow its own R-16/R-17 to the conclusion. Findings + resolutions:
- **[BLOCKER → resolved] RT-4 double wash-out:** cap-pinning (R-8, `min(total,cap)`) discards the high-cred
  meat surplus; fertility-pinning at r=0 (R-16/R-17) compensates away any residual gradient. **⇒ equilibrium
  gradient is null by construction.** Resolution: re-scoped to the **non-equilibrium regime** (central finding
  box + §6); equilibrium null is now *predicted*, not a failure.
- **[MAJOR → resolved] RT-7/RT-2 wrong regime/order:** "confirm equilibrium advantage first" would confirm a
  null and be misread as inert (the R-5…R-13 trap). Resolution: **shock/transient-first** (§6, Q3).
- **[MAJOR → resolved] D4 shock seam unbuilt** in the rivalrous path (verified: `PerturbationConfig` Oracle-only).
  Resolution: **build a time-varying `harvest_field` wrapper** (R-6 `run_2d` pattern) — §5 IN.
- **[MINOR → resolved] RT-5 wrong guard statistic:** multiplicative noisy-copy inflates Gini/variance with flat
  `mean_cred` → fc_sweep mean-slope guard misses it. Resolution: gate on **Gini drift + cred–survival corr** (§6.3).
- **[MINOR → resolved] RT-6 movement-temperature confound:** seeding cred silently activates the
  `temperature=σ_base+κ·tanh(cred/scale)` movement channel. Resolution: **hold σ_base** for the meat-isolation
  run (§5).
- **[MINOR → resolved] D1 breaks φ tests + unseeded-cred uniformity:** `status_of` **defaults to φ**, cred only
  under the carbon flag; **seeding mandatory** (§2).

### 9b. Supervisor correction (2026-06-21) — the red-team's RT-4 was HALF right; the first revision over-corrected
The red-team proved the **aggregate** gradient is washed out (cap-pinning + fertility-pinning) and I revised
into a **"shock/catastrophe, non-equilibrium"** frame. The supervisor caught two errors in that:
1. **Cap-pinning only holds for a DETERMINISTIC meat economy.** Real HG meat is high-variance (CV 0.73–2.24);
   **ordinary bad streaks** (not catastrophes) routinely thin the band pool below cap-for-all, and there the
   share rule decides who crosses the floor. **⇒ G.3 stochastic meat is the CORE mechanism (moved OUT→IN); no
   shock needed.** "Variability, not catastrophe."
2. **Fertility-pinning (R-16) pins the aggregate death RATE, not the COMPOSITION.** density-disease is
   density- not cred-keyed → it cannot spare the core → with status-weighted meat, **bad-streak deaths
   concentrate on the low-Cred periphery at ordinary stochastic equilibrium.** The advantage is *compositional*
   (who dies), which R-16 does not touch. The red-team conflated aggregate with distributional.
**Net:** the "non-equilibrium/shock-first" framing is withdrawn (central finding + §5/§6 rewritten); the catastrophe
shock is demoted to an optional later amplifier; **no RESULT is recorded** (design hypothesis until the model
shows it with stats).

---

**Code anchors:** `oracle.py:740` (cred update), `:795/825` (f_C inheritance), `config.py:43` CarbonConfig
(cred_decay 0.01, matthew_alpha 2.0, f_C 0.25, β), `agents/strategies/carbon.py` (CarbonDecision: temperature,
amplification, w_C_eff), `substrate.py:22` compute_harvest_shares (the φ→cred fix), `phase1_model.py:283/304`
(occ_wsum φ-weight), `:_do_births_ibi` (inheritance hook), `fc_sweep.py:85` `_cred_runaway` (the guard).
RESULTS R-1 (anti-fragility thesis), R-14 (per-agent variance washed at band scale — RT-4's warning).
