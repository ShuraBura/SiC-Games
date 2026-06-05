# SiC Games — Resource-Ecology Redesign: Design-Doc Task Brief

**This is a TASK BRIEF for the next chat's first deliverable, not the design doc itself.**
The design doc should be produced *with the supervisor in the loop* — the build order and
default-parameter choices are load-bearing and should be discussed, not decided unilaterally
inside a document. Read alongside the Standing Handoff (2026-05-31).

---

## Goal

Produce a **staged, gated, prioritised decomposition** of the supervisor's resource-ecology
vision (Handoff §5) into individually buildable stages. The doc's job is to turn a big
"richer resources" ambition into an ordered build plan that **protects falsifiability and the
H1(ii) inversion at every step**, rather than reopening everything at once.

The supervisor has authorised reopening H1(ii) (Handoff §1, §5). The doc must nonetheless
sequence the work so the inversion is re-confirmed at each stage, not abandoned.

---

## The three target mechanics (from Handoff §5)

1. **Resource-lifetime classes** — multiple resource types differing in renewal rate,
   depletion response, and mobility. Fast/mobile, mid, slow/long-lived.
   *Literature anchor:* Chupeau, Bénichou & Redner, "Universality classes of foraging with
   resource renewal" (renewal time → three regimes incl. starvation-free "immortal" regime);
   optimal-foraging patch-depletion curves (diminishing returns within a patch).
2. **Activation / residence dynamics** — resources that yield only after sufficient residence
   (accumulation-then-depletion), creating stay-vs-move tension.
   *Literature anchor:* marginal value theorem (Charnov); patch-leaving under uncertainty
   (Bayesian patch-foraging). *Key coupling:* trait-dependent stay/move thresholds →
   mechanical realisation of H-ORTHOGONALITY (OWE-8/13).
3. **Disaster shock class** — irregular, stochastic, heavy-tailed, spatially-local events
   (fire/flood/epidemic) distinct from the existing periodic seasonal forcing.
   *Probes:* robustness-to-surprise vs the seasonal channel's buffer-adequacy test.

---

## Required structure of the design doc

For EACH proposed stage, the doc must specify:

1. **What it adds** — the mechanic, in prose + the minimal math (parameter vector for the
   resource descriptor / shock process).
2. **Pre-committed default parameters + justification** — every new degree of freedom needs
   a default and a reason (falsifiability discipline; Handoff §5 governing constraints). No
   free knobs without defaults.
3. **Equivalence gate** — the explicit test that the new mechanic reduces to the *current*
   model when the feature is switched off (e.g. single fast-renewal instant-access static
   resource = today's Sugarscape). This is the regression guarantee.
4. **H1(ii) inversion re-confirmation checkpoint** — the run (≥3 seeds, C vs Si) that must
   pass before proceeding to the next stage, AND an explicit statement of whether the mechanic
   is *expected* to preserve, strengthen, or perturb the inversion, with the trough-depth
   driver (Handoff §1) protected or explicitly tested.
5. **Stopping rule + what gets reported.**
6. **Dependencies** — what must be built first.

---

## Proposed spine (for discussion — the doc should argue for or revise this order)

The natural build order starts from static heterogeneity and adds dynamics on top. Candidate
sequence, to be debated in the doc:

- **Stage R0 (confound check, pre-design):** is the calibration world static or seasonal? Run
  the calibrated 100×100 / N_carry=4100 world WITH seasonal oscillation ON and report
  est_starv and population variability. This may already restore finite starvation and partly
  dissolve the zero-starvation problem (Handoff §4) — and it reshapes R1's motivation. Cheap;
  do first.
- **Stage R1 — terrain topography (= OWE-2 / Stage 5.3):** static spatial heterogeneity
  (spatially-varying sugar capacity + optional metabolism multiplier). The foundation. Already
  on the roadmap. Equivalence gate: flat terrain = current twin-peak world.
- **Stage R2 — resource-lifetime classes:** introduce renewal-rate heterogeneity (slow/mid/
  fast). Directly targets the zero-starvation/over-stability problem via the renewal-time→
  starvation mechanism. Equivalence gate: all-fast-renewal = current world.
- **Stage R3 — residence/activation + trait coupling:** accumulation-then-depletion resources;
  stay-vs-move tension; trait-dependent thresholds. Build OWE-13 movement-decomposition
  diagnostic here. Serves H-ORTHOGONALITY.
- **Stage R4 — disaster shock channel:** stochastic heavy-tailed local events, separate from
  seasonal forcing. New perturbation type alongside `SeasonalOscillation`.
- **Resource mobility** — where does patch *relocation* enter? Possibly folded into R2
  (mobile = fast-renewal-elsewhere) or its own sub-stage. The doc should decide.

The doc should challenge this ordering if a better one exists (e.g. whether R0's result makes
R2 the true first priority over R1).

---

## Red-team lenses the doc must apply

At minimum: **population ecology** (renewal-time regimes, density dependence, Allee at low
trough N), **complexity science** (do new parameters create genuine attractors or just
numerical artifacts; is bistability robust), **philosophy of science** (falsifiability under
added degrees of freedom; pre-registration of expected inversion effect per stage). Add
**cliodynamics** where boom-crash / secular-cycle emergence is the explicit target.

---

## Hard constraints (from Handoff)

- Markdown. Handed to CC for any eventual build; CC reconciles against LIVE drive docs.
- Compute is NOT the binding constraint (36.4 ms/step; ~11 h full matrix) — design for
  richness, not frugality, but keep grid-size growth in check (grid-exponent ≈ 1.33 is the
  expensive axis; adding resource *types* on a fixed grid is cheap, like adding agents).
- The inversion's trough-depth driver must be preserved or explicitly tested at each stage.
- One mechanic per stage; equivalence-gated; inversion re-confirmed before proceeding.

---

## First question to put to the supervisor at the top of the next chat

Before writing the doc: **does Stage R0 (confound check) come back showing the seasonal world
already has finite starvation at scale?** If yes, the zero-starvation problem is milder than
feared and R1 (terrain) leads. If no (still zero starvation even under seasonal trough), then
the resource regime itself is the problem and R2 (resource-lifetime classes) should lead. The
R0 result reorders the whole doc — so run/confirm it first, or at least decide whether to
block the doc on it.

*End of Resource-Ecology Design-Doc Task Brief — 2026-05-31.*
