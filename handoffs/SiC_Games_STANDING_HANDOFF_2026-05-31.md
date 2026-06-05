# SiC Games — Standing Handoff (2026-05-31)

**Session focus:** OWE-1 absolute-scale calibration (completed), OWE-1.1 follow-up
(completed), and the opening of a resource-ecology redesign (design doc owed — see
companion file `SiC_Games_ResourceEcology_DesignDoc_Task.md`).

**Read this first, then the design-doc task file. The design doc is the first deliverable
of the next chat.**

---

## 1. CRITICAL CORRECTION — H1(ii) direction

A stale summary earlier in this session described the live result as "Si-dominant." **That
is wrong and must not propagate.** Per the live ROADMAP (Stage 5, 2026-05-27):

> **H1(ii) is C-DOMINANT and ROBUST: C 5/5 vs Si 0/5 at A=0.75.**

This is exactly what the founding hypothesis predicted (C survives higher-volatility shocks
better than Si). The Si-dominant reading was an artifact of the **Stage 4.4 era**, when C
could not survive null controls (structural viability failure, Allee/age-out bistability at
k=4). The **Stage 4.5 carrying-cost redesign fixed C's viability**, and the result then
flipped to the hypothesised C-dominance and has held robustly since.

**Mechanism of the inversion:** Si collapses at deep troughs via a **structural dormancy
cliff** (A=0.75, T=200). This is confirmed structural, not an artifact of missing Si Cred
(Stage 5.1 re-confirmed it after Si Cred was activated). **Governing implication for all
future work: the inversion depends on troughs being deep enough to trigger Si's dormancy
cliff. Any change that makes the world more forgiving risks masking the inversion.**

---

## 2. Current model state

- **Committed version:** Stage 5.2 complete (2026-05-29). 233 tests pass. No git repo —
  version-by-directory-backup; current backup `v5.1.2_pre_cultural` (note: backup name lags
  the actual Stage 5.2 state — confirm with CC before relying on it).
- **Stage ladder:** 1–5.2 complete. Stage 5.3 (terrain topography) pending. Stage 5.x (LHS
  scan, c1/c2 hooks, inter-pool connectivity), Stage 6 (statistical framework), Stage 7+
  (HiveMind, Si-biparental if designed, full 100-world run) all pending.
- **What C is:** biparental, Cred economy (status/dominance from joint tasks), status-coupled
  decision noise σ, proximity support pool + status-mediated L3, wealth inheritance λ=0.1,
  age-efficiency ramp η(a), Cred-modulated birth (γ=0.2, Turchin elite-overproduction hook),
  carrying-cost birth suppression, starvation death.
- **What Si is:** single-parent fission, fixed σ_Si=1.238, near-dormancy Cred (counter-
  cyclical, Stage 5.1), proximity pool L1+L2 only (no status), differential metabolism β=5,
  **dormancy instead of starvation death** (this is the dormancy cliff that drives H1(ii)),
  no η ramp, λ=0. Cultural dynamics (Stage 5.2): c2 defection active, Deffuant trait updating.

---

## 3. What this session locked / changed

### OWE-1 — Absolute-scale calibration (CLOSED)
- **Geometry:** 100×100 cells, ~10 km/cell (~1000×1000 km ≈ 10⁶ km² world).
- **Temporal resolution:** 1 step = 1 month, via **Route A** (declare the existing locked
  step to BE one month; preserve all Stage 4.x science; rescale nothing). **STANDING
  CONSTRAINT:** changing resolution requires full recalibration (rescale every per-step rate
  + re-confirm key findings). Recorded MODEL_SPEC §9.3.
- **Runtime:** measured **36.4 ms/step** at target geometry (100×100, N=2000) — the earlier
  ~130 ms interpolation was a 3.5× overestimate. N-exponent ≈ −0.018 (flat); grid-exponent
  ≈ 1.33 (steep). "N is a cheap lever, grid is expensive" CONFIRMED.
- **Full matrix budget:** ⟨ρ⟩×A×T×seeds×{C,Si} = 360 runs @ 12k steps ≈ **~11 h at 4
  workers.** Compute is no longer a binding constraint at these scales.

### OWE-1.1 — Follow-up (CLOSED)
- **Home-range "56× overshoot" was an estimator artifact.** Original estimator was
  lifetime-accumulated distinct-cell count; recomputed on contemporaneous rolling windows the
  discrepancy shrinks monotonically (lifetime 7.5× → annual 3.2× → seasonal 1.7×).
  **Recommended record: use the ANNUAL window (residual ~3×), not seasonal (1.7×)** — the
  ~100 km² !Kung benchmark is an annual-territory quantity; picking the seasonal window
  because it minimises the residual would be fitting the benchmark to the number. The residual
  ~3× is attributable to !Kung being unusually sedentary among foragers. OWE-1's lifetime-based
  56× is SUPERSEDED. (CC recorded seasonal as "consistent" — supervisor should overrule to
  annual when reviewing.)
- **N_carry calibrated to target population.** N_carry was confirmed ARBITRARY (a numerical-
  stability scale parameter from Stage 4.5, top of the hand-set viability band — NOT an
  ecological estimate). Measured map on 100×100: settled ≈ 0.754·N_carry − 566. **Locked
  N_carry = 4100 → settled N ≈ 2357** (target band 2000–3000, → ~24–47 ethnographic bands).
  Production 50×50 value remains 400. N_carry is a declared **calibration choice (scale-
  setting), not an emergent prediction** — set once, shared across both arms, locked before
  looking at H1(ii). Recorded MODEL_SPEC §9.3.
- **Run-length locked:** 12,000 steps (1000 yr, ~4 secular cycles), ~500-step transient
  exclusion. 24k in reserve.

### Locked-parameter additions (live ROADMAP)
- N_carry(100×100) = 4100; run-length 12k/500-transient; ⟨ρ⟩ sweep axis registered.

---

## 4. OPEN PROBLEM driving the next chat — zero starvation / over-stability

The calibration surfaced **est_starv = 0.000** and **rel std = 0.014** at settled N. Supervisor
flagged both as wrong for a forager world. Diagnosis developed this session:

- **Ecological reading (Chupeau–Bénichou–Redner, "foraging with resource renewal"):** fast
  resource renewal puts foragers in the "immortal" regime — never starve. The current world
  has ONE resource type with fast growback (α), so it sits in that regime. This is *mechanism*,
  not a tuning error.
- **The forager population paradox (ethnographic):** real HG populations were NOT smoothly
  regulated at carrying capacity — they boomed and crashed. A population pinned at rel-std
  0.014 with zero starvation is failing to reproduce the boom-crash character that secular
  cycles (the project's headline ambition) require. **Zero starvation and pathological
  stability are likely the same symptom: a birth-suppression-regulated equilibrium with no
  resource-driven mortality to generate cycles.**
- **Two competing sub-readings, not yet distinguished:** (a) world is over-provisioned at
  calibrated N (lower ⟨ρ⟩), vs (b) carrying-cost mechanic over-regulates on the birth side,
  decoupling mortality from resources (weaken alpha_carry). The discriminating diagnostic is
  **marginal-agent-to-starvation-threshold distance at baseline** — not yet measured.
- **CONFOUND TO CHECK FIRST (cheap):** the calibration run may have used `perturbation: null`
  (static world). Seasonal oscillation has NEVER been run at the calibrated 100×100 scale
  (Stage 4 tested it at N=250, "no pop-level stress visible"). Turning seasons ON at scale may
  already restore finite starvation via the trough. **Confirm the calibration's perturbation
  setting before designing anything.**

This open problem is what motivated the supervisor's resource-ecology vision (§5).

---

## 5. Supervisor's resource-ecology vision (→ design doc is the next deliverable)

Supervisor wants richer, more realistic resource dynamics. Three instincts, all literature-
grounded this session:

1. **Resource-lifetime distribution.** Multiple resource classes with different renewal +
   depletion rates: fast-depleting/mobile, mid-term, slow/long-lived. Anchored in
   Chupeau–Bénichou–Redner renewal-time regimes (renewal time → starvation risk).
2. **Activation / residence requirement.** Some resources yield only after the population
   stays in place long enough (accumulation-then-depletion). Creates stay-vs-move tension
   (marginal value theorem). **Coupling to social traits:** different ψ / trait profiles →
   different stay/move thresholds → near-mechanical realisation of H-ORTHOGONALITY (OWE-8/13).
3. **Two shock classes:** (a) seasonal pressure (already implemented — tests buffer adequacy /
   winter scarcity, "starvation peaks when pools depleted"); (b) **disaster shocks** —
   irregular, stochastic, heavy-tailed amplitude, spatially local (fire, flood, epidemic /
   epizootic). Tests robustness-to-surprise, a different resilience property; C and Si may
   rank differently on it.

**Supervisor decision (2026-05-31): WILLING TO REOPEN H1(ii)** to get rich dynamics, provided
compute sustains it (it does) and provided the work is staged. This is a deliberate choice: a
result that survives a richer world is stronger than one that only holds in a degenerate
single-resource world.

**Governing constraints for the design doc:**
- Each mechanic = its own stage, its own equivalence gate (reduces to current model when the
  feature is off), its own **H1(ii) inversion re-confirmation checkpoint** before proceeding.
- Every new resource parameter needs a pre-committed default + justification (falsifiability
  discipline — degrees of freedom are how ABMs become unfalsifiable).
- Must preserve / explicitly test trough-depth (the inversion's driver — see §1).
- Natural build order starts from the existing hook: **Stage 5.3 terrain topography / OWE-2
  (static spatial heterogeneity)** is the foundation that resource-lifetime, residence, and
  disasters all build on.

---

## 6. Owed items (live ROADMAP backlog — status this session)

- **OWE-1** — CLOSED (calibration done).
- **OWE-11** (larger-N feasibility) — CLOSED (measured; N is cheap lever; real lever for more
  steady-state agents is raising N_carry, not init N).
- **OWE-14** — OPEN, **HIGH PRIORITY, authorised not yet run.** Re-confirm H1(ii) inversion at
  calibrated N_carry=4100 (≥3 seeds, C vs Si). **REFINED SPEC (this session):** must also check
  whether **starvation re-engages under shock at the new scale** — not just whether the inversion
  sign holds. If the richer-scale world has zero starvation even under seasonal trough, the
  inversion test has no teeth (see §4). Sequence OWE-14 AFTER the §4 confound check (is the
  calibration world static or seasonal?).
- **OWE-2** (terrain topography) — OPEN — becomes the spine of the resource-ecology design doc.
- **OWE-8 / OWE-13** (movement decomposition: enumeration + diagnostic) — OPEN — the residence/
  activation mechanic (§5.2) is the natural place to build OWE-13, and it directly serves
  H-ORTHOGONALITY.
- **OWE-12** (min-band-size-in-trough finite-size diagnostic) — OPEN — sharper now: settled
  N≈2357 peak means troughs may push bands into the finite-size/drift regime; contaminates
  H1(ii) terminal readings. Pairs with OWE-14.
- **OWE-3, 4, 5, 6, 7, 9, 10** — OPEN/DEFERRED, unchanged this session.
- **OWE-2..10 numbering caveat:** CC reconstructed these IDs (the canonical "2026-05-30 Standing
  Handoff §5" file was not findable on the drive); CC flagged the provenance. **The live ROADMAP
  Owed table (uploaded this session) now shows the reconciled OWE-1..14 list — supervisor should
  confirm it matches intent.** As of the uploaded ROADMAP, OWE-2..10 appear correctly populated.

---

## 7. Process notes

- **Documents are markdown, handed to Claude Code; CC reconciles against the LIVE drive copies**
  (`G:\My Drive\docs\SiC Games\...`), not the stale `/mnt/project/` snapshots. Merge discipline:
  idempotent + conflict-surfacing (append if absent, skip if present-and-consistent, STOP and
  report if contradictory — never auto-resolve).
- **Blueprints/directives:** headers + numbered tasks, explicit gates + stopping rules. Analysis/
  discussion: prose.
- **Pre-register before analysing** (no HARKing). **Default to scepticism** on surprising results
  (artifact vs finding). **Red-team** with 2–3 disciplinary lenses on substantive content.
- **MODEL_SPEC is still PILOT scope**; §9 (world/resource substrate) was created this session and
  currently holds the calibration content. The resource-ecology work will populate §9 heavily.

---

## 8. Next-chat opening move

1. Deliver the **resource-ecology design doc** (companion task file). This is the first
   deliverable — a staged, gated, prioritised decomposition of §5, NOT a single mechanic
   blueprint yet.
2. In parallel or immediately after, the **§4 confound check** (is the calibration world static
   or seasonal? does turning seasons on at scale restore finite starvation?) — cheap, and it
   determines whether the zero-starvation problem even survives, which shapes the design doc's
   first stage.
3. Then **OWE-14** with the refined spec, once the world has teeth.

*End of Standing Handoff 2026-05-31.*
