# SiC Games — Stage R0 Blueprint: Seasonal-at-Scale Confound Check + Marginal-Distance Diagnostic

**Version:** 1.0
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** R0 only. A pre-design diagnostic run. **No new mechanics, no design latitude** —
this is instrumentation + execution on the existing calibrated world.
**Prerequisite:** Stage 5.2 complete (233 tests pass). Calibrated geometry locked:
100×100, N_carry=4100, run-length 12k/500-transient, seed set as below.
**ROADMAP:** `G:\My Drive\docs\SiC Games\ROADMAP.md`
**Reconcile against:** LIVE drive docs, not the `/mnt/project/` snapshot.

---

## 0. North Star (read first)

The OWE-1.1 calibration surfaced **est_starv = 0.000** and **rel std = 0.014** at settled N
on the 100×100 / N_carry=4100 world. The supervisor flagged both as wrong for a forager
world (a population that never starves and barely fluctuates is failing to produce the
boom-crash character secular cycles require). Before any resource-ecology redesign is
scoped, **one fact must be measured, not assumed:**

> **Was the calibration world static (`perturbation: null`) or seasonal? And does turning
> seasonal oscillation ON at the calibrated scale restore finite starvation?**

This is an unverified confound, not a known result. Every prior seasonal run executed on the
**50×50 grid** with old constants (max_sugar=16 at k=4, N_carry=400). `SeasonalOscillation`
has **never touched the 100×100 / N_carry=4100 geometry.** The mechanic is known-good as code
(exercised through every Stage 4.2–5 seasonal sweep), but its interaction with (a) the new
capacity field and (b) the carrying-cost birth-suppression mechanic at N_carry=4100 is
**completely uncharacterised.**

**Why R0 reorders a load-bearing document.** R0's result decides the spine of the
Resource-Ecology Design Doc:

- If seasons restore finite starvation at scale → zero-starvation problem is milder →
  **R1 (terrain) leads.**
- If still zero starvation under the seasonal trough → the single-resource renewal regime
  is itself the problem → **R2 (resource-lifetime classes) leads.**

A false negative here — seasonal forcing silently failing to engage and masquerading as
"seasons don't restore starvation" — would mis-order the entire design doc. **That is the
specific failure this blueprint's gate exists to prevent.**

**What R0 is not.** Not a calibration. Not a parameter search. Not an H1(ii) test (that is
OWE-14, sequenced after R0). No tuning is authorised — if a gate fails, **STOP and report**,
do not adjust parameters to make it pass.

---

## 1. Task 0 — Smoke-test gate: confirm seasonal oscillation fires at 100×100

**This gate runs first and blocks everything else.** Its job is to catch silent
non-firing before a full run is interpreted.

### 1.1 The check

Instantiate the calibrated world (100×100, N_carry=4100) with `perturbation: seasonal`,
A=0.75, T=200. Run a short trace (≥ 2·T = 400 steps is sufficient; 500 to be safe) and
assert that the seasonal forcing is actually modulating the resource field.

**Assertion (the exact Stage 4 check, re-applied at the new geometry):**

- Record `effective_capacity` (the seasonally-modulated capacity field) at each step over
  one full cycle.
- Compute the per-step **global sum** (or mean) of `effective_capacity` across all cells.
- **Assert this quantity oscillates** — i.e. its coefficient of variation over the cycle is
  non-trivial (CV > 0.01 as a floor; for A=0.75 the swing should be large, so this is a
  weak floor deliberately set to catch *constant*, not to police amplitude).
- **Assert the trough is where expected:** the minimum of the global capacity sum should
  occur at the trough phase of the oscillation, and the peak at the peak phase. A flat or
  phase-misaligned trace is a wiring failure.

The Stage 4 blueprint specified: *"if sugar capacity is constant, the WorldPerturbation hook
is not connected."* That failure mode is real in this codebase. This gate re-runs that check
at the untested scale.

### 1.2 Gate logic

- **PASS:** `effective_capacity` oscillates, trough/peak phase-aligned. → Proceed to Task 1.
- **FAIL (constant capacity):** the perturbation hook is not connected at 100×100. **STOP.
  Report immediately.** Do not run the full matrix — a static result would be
  indistinguishable from a true seasonal null and would corrupt R0's headline answer. Report
  the capacity trace and the hook-connection point in code.

### 1.3 Report

In §1 of the R0 report: the capacity-sum trace over one cycle (figure), the computed CV, and
the phase-alignment confirmation. One sentence: gate PASS or FAIL.

---

## 2. Task 1 — Equivalence check: seasons-OFF reproduces the static baseline

**This is the regression guarantee** that the new-scale seasonal *config* perturbed nothing
other than the seasonality, and it doubles as the comparison baseline the seasonal run needs.

### 2.1 The run

Run the calibrated world (100×100, N_carry=4100, full 12k steps, 500-transient exclusion)
with `perturbation: null` — i.e. seasons OFF — across the locked seed set.

### 2.2 Equivalence gate

Compare against the OWE-1.1 calibration baseline:

| Quantity | Expected (OWE-1.1 baseline) | Tolerance |
|---|---|---|
| Settled N | ≈ 2357 | within ±5% (≈ 2240–2475) |
| est_starv | 0.000 | must be 0.000 (or < 0.001/step) |
| rel std (pop) | ≈ 0.014 | within ±0.005 |

- **PASS:** all three within tolerance. The seasons-OFF config is equivalent to the
  calibration baseline. → Proceed to Task 2.
- **FAIL:** any quantity outside tolerance. This means the seasonal config branch changed
  something even with the feature off. **STOP and report** — do not proceed to the seasonal
  run, because the baseline comparison would be contaminated. Report which quantity diverged
  and by how much.

**Note on provenance.** This task also *retroactively establishes* the missing fact from the
handoff: if seasons-OFF here reproduces the calibration numbers exactly, it confirms the
original calibration was static (it matches the `perturbation: null` branch). Record this
explicitly — it closes the open confound regardless of the seasonal-ON result.

### 2.3 Marginal-distance diagnostic on the static baseline (instrument here)

While the seasons-OFF trajectory runs, capture the marginal-distance diagnostics. These come
off the trajectory already being computed — **logging + post-processing only, no extra runs.**

Three diagnostics (definitions agreed with supervisor):

**D1 — Wealth-to-zero distance (per-agent, distributional).**
For each agent at each logged step: `(current accumulated resource stock) − (death threshold)`,
expressed in **steps-of-unreplenished-metabolism** until starvation
(i.e. `stock / per_step_metabolism`). Report the population distribution — emphasise the
**lower tail**: min, 5th percentile, median. This is the direct "how close to death is the
marginal agent" reading.

**D2 — Per-step energy balance (per-agent, distributional).**
For each agent at each logged step: `(intake at current location this step) − (metabolism
this step)`. Report distribution, lower tail emphasised. Distinguishes *fat-but-declining*
(positive stock, negative balance) from *lean-but-stable* (low stock, ≥0 balance). D1 and D2
together separate stock from flow.

**D3 — Birth-clamp-vs-death-margin gap (parameter-level annotation, NOT per-agent).**
Compute, from the config/threshold values, the distance on the shared resource axis between:
- the carrying-cost **birth-suppression threshold** (where `alpha_carry` clamps reproduction), and
- the **starvation-death threshold**.

This is a statement about *where the two thresholds sit relative to each other*, derived once
from parameters, not measured per agent. It is the direct test of §4 sub-reading (b): "birth-
clamped *before* death engages" is literally the claim that the birth-suppression threshold
sits above the death threshold by a wide margin, so the population is regulated on the birth
side and never reaches the death side. Report the two threshold values and the gap, with a
one-line interpretation.

### 2.4 What the static diagnostics discriminate

Pre-register the reading (no HARKing — this is stated before the numbers are seen):

- **Far-from-margin** (D1 lower tail large, D2 lower tail ≥ 0, D3 gap wide) → population is
  **over-provisioned** at calibrated N → handoff §4 sub-reading **(a)** → an R2-flavoured fix
  (lower ⟨ρ⟩ / resource-lifetime regime change) is indicated.
- **Near-margin-but-clamped** (D1 lower tail small but D2 lower tail still ≥ 0, D3 gap such
  that birth clamps well above death) → population sits near the resource margin but is
  **birth-suppressed before mortality engages** → handoff §4 sub-reading **(b)** → a
  regulation-mechanism fix (weaken `alpha_carry`) is indicated.

R0 does not *decide* the fix — it *pre-stages the discrimination* and feeds whichever spine
the seasonal result selects.

---

## 3. Task 2 — The run: seasons ON at scale

Only after Tasks 0 and 1 pass. Run the calibrated world (100×100, N_carry=4100, full 12k,
500-transient) with `perturbation: seasonal` ON, at two amplitudes.

### 3.1 Run matrix

| Run ID | Perturbation | A | T | Steps | Seeds |
|---|---|---|---|---|---|
| R0-static | null | — | — | 12k | locked set |
| R0-seasonal-A075 | seasonal | 0.75 | 200 | 12k | locked set |
| R0-seasonal-A05 | seasonal | 0.5 | 200 | 12k | locked set |

- **A=0.75** is the inversion-relevant amplitude (the H1(ii) inversion's trough-depth driver
  lives here — handoff §1). It is the primary run.
- **A=0.5** is included as the shallower comparison so we can see whether starvation re-engages
  monotonically with trough depth, or only at the deep trough. Cheap (same machinery), and it
  characterises the *shape* of the starvation response rather than a single point.
- **T=200** matches the inversion runs. Do not vary T in R0 — period is not the question here.

**Seed set:** use the locked R0 seed set (≥ 3 seeds; default seed 42 + 2 others from the
project's standard set). Report per-seed and aggregate.

### 3.2 Primary outputs (per run, against the static baseline)

| Quantity | Static baseline | Seasonal A=0.5 | Seasonal A=0.75 |
|---|---|---|---|
| Settled N (mean, post-transient) | | | |
| est_starv (/step, mean) | 0.000 | | |
| rel std (pop) | 0.014 | | |
| min N over trough phases | | | |

### 3.3 Marginal-distance diagnostic under seasonal forcing — TIME SERIES, not snapshot

Capture **D1 and D2 as time series across the seasonal cycle**, not only at the trough.
(D3 is parameter-level and unchanged by forcing — report once, from Task 1.)

Rationale: the trough is just the minimum of the series. The full time series strictly
dominates a single worst-case snapshot — same logging cost — because it shows whether the
margin *breathes* with the forcing (D1/D2 lower tail dipping at trough, recovering at peak)
or sits flat (forcing not reaching the agents). A flat margin under a confirmed-oscillating
capacity field (Task 0 passed) would itself be a finding: the population is buffered against
the trough by something (stock, pool, mobility).

For each seasonal run, report:
- D1 lower tail (min, 5th pctile) as a time series over ≥ 2 full cycles, with the seasonal
  phase overlaid.
- D2 lower tail as a time series over the same window.
- The **trough-phase values** (the series minima) called out explicitly, since those are the
  worst-case the seasonal channel produces.

### 3.4 The headline answer (pre-registered interpretation)

State, before seeing the numbers, what each outcome means for the design-doc spine:

- **est_starv goes finite under seasonal A=0.75** (and ideally rises from A=0.5 → A=0.75):
  the seasonal trough restores resource-driven mortality at scale. Zero-starvation problem is
  **milder than feared** → design doc spine leads with **R1 (terrain)**; resource-lifetime
  classes (R2) become enrichment rather than a fix.
- **est_starv remains ≈ 0.000 even under seasonal A=0.75** (D1/D2 margins breathe but never
  cross zero): the trough is not enough; the single-resource fast-renewal regime keeps the
  population in the "immortal" regime regardless of seasonal forcing → the resource regime
  itself is the problem → design doc spine leads with **R2 (resource-lifetime classes)**.
- **est_starv ≈ 0.000 AND D1/D2 margins are flat** (don't breathe) despite Task 0 confirming
  capacity oscillates: the forcing reaches the field but not the agents — investigate the
  buffer (stock? pool? mobility absorbing the trough?). Report as a distinct third outcome;
  it changes the diagnosis from "resource regime" to "buffer mechanic."

---

## 4. Metrics summary

| Metric | Definition | Where |
|---|---|---|
| `eff_cap_sum_cv` | CV of global `effective_capacity` sum over one cycle | Task 0 gate |
| `eff_cap_phase_aligned` | bool: trough at trough-phase, peak at peak-phase | Task 0 gate |
| `settled_N` | mean post-transient population | all runs |
| `est_starv` | established starvation rate /step | all runs |
| `rel_std_pop` | relative std of population, post-transient | all runs |
| `min_N_trough` | min population during trough phases | seasonal runs |
| `d1_wealth_to_zero` | per-agent stock/metabolism = steps-to-starvation; report lower tail | static (snapshot) + seasonal (time series) |
| `d2_energy_balance` | per-agent intake − metabolism per step; report lower tail | static (snapshot) + seasonal (time series) |
| `d3_birth_death_gap` | parameter-level gap: birth-suppression threshold − death threshold | Task 1 (once) |

---

## 5. Stopping rules

1. **Task 0 FAIL (capacity constant):** STOP. Report the capacity trace and the unconnected
   hook. No further runs. This is the most important stop — it prevents a false negative from
   reordering the design doc.
2. **Task 1 FAIL (equivalence broken):** STOP. Report which baseline quantity diverged. No
   seasonal run, because its baseline comparison would be contaminated.
3. **No tuning under any circumstances.** R0 has no design latitude. If results are surprising,
   that is the *finding* — report it, do not adjust parameters to produce an expected number.
4. **All gates pass:** complete the run matrix, produce the report, **stop.** Do not proceed
   to OWE-14 or any design work — R0's deliverable is the report and the spine-selecting
   headline answer, which goes back to the supervisor for the design-doc decision.

---

## 6. Report format

HTML (Standing Rule 13), single self-contained file with base64-embedded figures.

Structure:
1. **§1 Gate (Task 0)** — capacity-sum trace figure, CV, phase-alignment, PASS/FAIL.
2. **§2 Equivalence (Task 1)** — baseline comparison table, PASS/FAIL, the static/seasonal
   provenance conclusion (did this confirm the original calibration was static?), and the
   static marginal-distance diagnostics D1/D2/D3 with the (a)-vs-(b) reading.
3. **§3 Seasonal run (Task 2)** — primary outputs table, D1/D2 time-series figures with phase
   overlay, trough-phase callouts.
4. **§4 Headline answer (≥ 150 words, prose)** — which of the three outcomes obtains, and
   therefore which spine (R1-leads / R2-leads / buffer-investigation) the design doc should
   commit to. State the §4 sub-reading the static diagnostics indicated (over-provisioned vs
   birth-clamped). **Do not write "see table."**

---

## 7. Coding-agent directives

1. **Gate first, run second.** Do not execute the 12k seasonal runs until Task 0 (capacity
   oscillates at 100×100) and Task 1 (seasons-OFF ≡ calibration baseline) both pass. The gate
   is cheap; the run is not; a silent wiring failure caught after the run wastes the run and
   risks a wrong design-doc spine.

2. **Re-use the exact Stage 4 capacity-oscillation check.** Do not invent a new assertion. The
   check that "constant capacity ⇒ hook not connected" already exists in the Stage 4 blueprint
   lineage — apply it at the new geometry.

3. **Marginal-distance diagnostics are logging + post-processing only.** They come off
   trajectories you are already running. Do not add runs to produce them. D1 and D2 are
   per-agent distributions (report lower tails); D3 is a parameter-level annotation computed
   once from config (NOT per-agent).

4. **D1/D2 as TIME SERIES under seasonal forcing**, snapshot under static. The seasonal
   time series with phase overlay is the deliverable, not just the trough snapshot.

5. **No tuning.** If a gate fails or a result is surprising, STOP and report. R0 has zero
   design latitude. A surprising est_starv is the finding, not a bug to tune away.

6. **Pre-registered interpretation is fixed before the numbers.** The §3.4 outcome→spine
   mapping is committed in this blueprint. Report which outcome obtains; do not re-derive a
   new interpretation from the result (no HARKing).

7. **Reconcile docs against the LIVE drive copies** (`G:\My Drive\docs\SiC Games\...`), not the
   `/mnt/project/` snapshot. Merge discipline: append-if-absent, skip-if-present-and-consistent,
   STOP-and-report-if-contradictory.

8. **Do NOT update the ROADMAP's H1(ii) verdict or any locked parameter.** R0 changes nothing
   locked. It produces a diagnostic report only. Record R0's completion and headline answer in
   the ROADMAP's run log / OWE table; touch nothing else.

---

## 8. Success criteria

| Criterion | Target |
|---|---|
| Task 0 gate executed | Capacity-oscillation check run at 100×100; PASS/FAIL reported |
| Task 1 equivalence | Seasons-OFF reproduces calibration baseline within tolerance; static/seasonal provenance of original calibration stated |
| Static marginal diagnostics | D1, D2 distributions + D3 parameter gap reported; (a)-vs-(b) reading given |
| Seasonal runs complete | A=0.5 and A=0.75 at T=200, ≥3 seeds, 12k steps each |
| Seasonal marginal diagnostics | D1/D2 time series with phase overlay; trough-phase callouts |
| Headline answer written | ≥150 words; commits to R1-leads / R2-leads / buffer-investigation |
| Report is HTML | Single self-contained report.html, figures embedded |
| Tests pass | Full suite after any instrumentation code change |
| Nothing locked changed | No parameter, no H1(ii) verdict touched |

---

## 9. Sequencing note (for the supervisor, not CC)

R0 is the standalone first deliverable. The Resource-Ecology Design Doc's R0-independent
scaffolding (framing, three-mechanic literature section, per-stage structural template,
red-team lenses, falsifiability constraints) can be drafted in parallel while this runs. The
design doc's **spine (R1-leads vs R2-leads)** is committed only once R0's §4 headline answer
returns. OWE-14 (H1(ii) re-confirmation at calibrated N_carry) is sequenced **after** R0 —
its refined spec requires knowing whether starvation re-engages under shock at the new scale,
which is exactly what R0 measures.
