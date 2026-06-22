# SiC Games · Phase 1 · **Carbon-on-Substrate (Cred coupling)** — Scoping draft

**Status:** SCOPING — **red-teamed 2026-06-21, verdict NEEDS-REVISION; revised below** (red-team record §9).
Goal: a **working Carbon (hierarchical) simulation** — bring the Cred/status dynamics onto the validated
demographic substrate so κ-weighted meat sharing produces a real status hierarchy with anti-fragile
demographics. **Silicon deferred.** Builds on the game economy G.1+G.2 (commit c8d3f31, §4.5.5).

> **THE RED-TEAM'S CENTRAL FINDING (governs everything below).** On this substrate the Cred advantage is
> **inert at equilibrium by construction** — *two stacked wash-outs*: (1) the **bang-bang cap** (R-8) clips a
> high-Cred agent's larger meat share to the same `reserve_full` cap (`min(total,cap)`, `phase1_model.py:335`)
> → the surplus is discarded/overflowed, not a survival buffer; (2) **fertility-pinning at r=0** (R-16/R-17) —
> density-disease supplies *whatever* excess mortality holds deaths=births, so any cred-driven survival edge
> for the core is **compensated away** elsewhere (the same lever that ate the +6.2 yr de-warfaring to 0.0).
> **⇒ The Carbon advantage is an inherently NON-EQUILIBRIUM phenomenon** — it appears only **below K**
> (growth/colonization, where agents aren't cap-pinned and density-disease is slack — R-17's regime) and
> **during/after a shock** (food, not density-disease, binds). This is not a defect: **anti-fragility (R-1)
> was always a shock/transient property.** The revision below makes the shock/transient regime THE test and
> explicitly predicts (and accepts) a NULL equilibrium gradient — *not* a sign of inertness.

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
carbon run collapses every weight to `(0+ε)^κ` (uniform). This single change makes the hierarchy *bite* on
meat — but only in the non-equilibrium regime (see the central finding).

## 3. D2 (the crux) — what is the Cred SOURCE on a forager substrate?

The Oracle earns Cred via joint tasks. Foragers don't co-work on sugar cells. Three options:

- **A — Earned from hunting/provisioning (lit-faithful; costly signaling, Hawkes 1991).** A successful hunter
  who contributes meat to the band beyond his own need gains prestige. **Needs per-hunter variance (G.3,
  deferred)** so there *is* a "successful hunter"; without it every occupant gets an equal deterministic meat
  share and no one stands out. Most realistic, most work, and carries the **runaway risk** (Cred→more meat→
  more Cred) the Oracle already had to guard (fc_sweep `_cred_runaway`, >5%/100 steps).
- **B — Port joint tasks** (cooperative hunts as the "task"). Reuses machinery but is awkward on the forager
  substrate and re-imports the Sugarscape framing we're trying to leave.
- **C — Heritable status, seeded (minimal; isolates the consequence).** Don't *earn* Cred; **seed** a Cred
  distribution and **inherit** it at IBI birth (mother's cred ×noise, or `f_C·mean_cred`). Cred-weighted meat
  gives high-Cred lineages a survival/fertility edge; the hierarchy persists by **differential survival**, not
  earning. Tests directly: *does a heritable status hierarchy produce anti-fragile demographics under shock?*

**Recommendation: C-first, then A.** C isolates the project's actual question (does a Cred hierarchy →
anti-fragility on real demography?) with minimal new mechanism and **no runaway risk** (no Cred→Cred feedback;
the only dynamics are inheritance + selection). Once C shows the anti-fragility signature, **A** makes the
hierarchy *endogenous* (earned from hunting, needs G.3 + the runaway guard) as increment 2. **B** rejected
(Sugarscape re-import).

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

**IN:** D1 (`status_of` hook, φ-default / cred-under-carbon-flag, mandatory seeding) · D3(i) (heritable cred at
birth + founder seeding from the model RNG) · a `carbon` TerrainWorld path (`carbon_cfg` already wires
`strategy="carbon"`, `_make_agent:196`) · **a shock hook in the rivalrous path** — confirmed NOT to exist
(`PerturbationConfig` is Oracle-only; `phase1_model.py` has no perturbation/season multiplier), so **build it
as a time-varying `harvest_field` wrapper** (the R-6 `run_2d` seasonal harness already modulated the field
externally — reuse that pattern; no deep model change) · the **post-shock-recovery harness**, κ>0 vs κ=0, on
**forest-Aché** (meat_frac 0.55). Decay OFF, β=0.
**Isolate the confound (RT-6):** seeding cred **silently activates the movement-temperature coupling**
(`diffusion_select_target` reads `agent._decision.temperature` → `tanh(cred/scale)`, `carbon.py:47`; neutral
only at cred=0). For the meat-isolation run, **hold temperature at σ_base** (or measure movement dispersion as
a separate channel) so the meat-share effect isn't confounded by cred-driven exploration.
**OUT (increments):** A earned-Cred + G.3 hunting variance + the (re-statisticked) runaway guard; B joint
tasks; D5 β; the Silicon comparison; multi-biome.

## 6. First forest-Aché Carbon run — what it measures (REVISED: regime-aware)
**Equilibrium gradient is NULL by construction (predicted, not a failure)** — do not lead with it; cap-pinning
+ fertility-pinning erase it (central finding). The signal is in the **non-equilibrium** regimes:
1. **PRIMARY — post-shock recovery (the R-1 anti-fragility test):** apply a resource crash (a time-varying
   `harvest_field` wrapper — §5) to a settled population; measure whether κ>0 (Carbon) **retains a reproducing
   high-cred core and recovers faster**, vs κ=0 (egalitarian) dipping collectively. The cred–survival
   correlation should go **positive during the shock** (when food binds) and ~0 at equilibrium.
2. **SECONDARY — below-K transient (R-17 regime):** in the growth phase (agents below cap, density-disease
   slack), is there a cred→reserve→survival/parity gradient? This is the *other* place the advantage can live.
3. **Hierarchy is stable, not drifting/runaway:** gate on **Gini(cred) drift + the cred–survival
   correlation**, NOT `mean_cred` slope (RT-5: a multiplicative noisy-copy inflates Gini/variance while leaving
   mean flat, so the fc_sweep mean-slope guard would miss it).
4. **Substrate intact:** with κ=0 (or game off) the run reproduces the validated baseline (e₀, density); 452
   green throughout (opt-in).

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

## 8. Open questions for the supervisor (REVISED post-red-team)
- **Q1:** Endorse **C-first** (heritable seeded Cred, no earning yet) as the minimal first Carbon sim, with
  earned-Cred (A, needs G.3) as increment 2? *(Red-team caveat: C-first is legitimate ONLY in the
  shock/transient regime — at equilibrium it tests nothing, by construction.)*
- **Q2:** Inheritance **(i) noisy lineage copy** vs **(ii) f_C·mean_cred regression**? (Recommend i.)
- **Q3 (resolved by the central finding):** ~~equilibrium advantage first vs shock first~~ → **shock/transient
  is the test; equilibrium gradient is a predicted null.** Confirm you accept leading with the **post-shock
  recovery** comparison (and the below-K transient) rather than an equilibrium gradient.
- **Q4:** Decay **OFF** for C-first (persistent heritable status) — agreed?
- **Q5 (new):** The Carbon advantage being a **non-equilibrium phenomenon** is a genuine *scientific result*
  about this substrate, not just a build choice. Accept that framing — anti-fragility lives off-equilibrium —
  as the stage's thesis, and record it as a RESULT?

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

---

**Code anchors:** `oracle.py:740` (cred update), `:795/825` (f_C inheritance), `config.py:43` CarbonConfig
(cred_decay 0.01, matthew_alpha 2.0, f_C 0.25, β), `agents/strategies/carbon.py` (CarbonDecision: temperature,
amplification, w_C_eff), `substrate.py:22` compute_harvest_shares (the φ→cred fix), `phase1_model.py:283/304`
(occ_wsum φ-weight), `:_do_births_ibi` (inheritance hook), `fc_sweep.py:85` `_cred_runaway` (the guard).
RESULTS R-1 (anti-fragility thesis), R-14 (per-agent variance washed at band scale — RT-4's warning).
