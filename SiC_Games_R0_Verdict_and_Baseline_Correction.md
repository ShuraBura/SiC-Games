# SiC Games — Stage R0 Verdict, Baseline Correction, and Process Flag

**Version:** 1.0
**Intended consumer:** Claude Code (merge into live ROADMAP / handoff) and the supervisor.
**Reconcile against:** LIVE drive docs (`G:\My Drive\docs\SiC Games\...`), not the
`/mnt/project/` snapshot. Merge discipline: append-if-absent,
skip-if-present-and-consistent, STOP-and-report-if-contradictory.
**Status:** Supervisor-approved 2026-06-02.

---

## 1. R0 verdict (recorded)

**OUTCOME: R1-LEADS.** Confirmed and accepted.

Seasonal forcing fires cleanly at the calibrated 100×100 / N_carry=4100 scale (Task 0
gate PASS: effective_capacity CV ≈ 0.42 over one cycle, trough phase-aligned at T/2; the
Stage-4 "constant capacity ⇒ hook not connected" failure mode does not occur). The
seasonal trough at A=0.75 restores finite resource-driven mortality: est_starv rises from
0.0000/step (static) to 0.0612/step (A=0.75). The response is **monotonic in trough
depth** — A=0.5 still gives 0.0000/step, only the deep A=0.75 trough engages mortality —
i.e. a threshold/cliff, not a smooth ramp. Marginal-distance time series confirm the
margins breathe with the forcing (D1 5th-percentile drops to ≈3.4 steps-to-starvation at
the trough, recovers at peak), ruling out the "capacity oscillates but agents are buffered"
third outcome.

Per the pre-registered §3.4 mapping, this selects **R1 (terrain topography) as the
design-doc spine lead**; resource-lifetime classes (R2) become enrichment rather than the
primary fix for the zero-starvation problem.

The static/seasonal confound is **closed**: under `perturbation: null`, est_starv = 0.0000
exactly matches the OWE-1.1 calibration's 0.000. The original calibration was run on the
static branch. (See §2 for a minor caveat on the rel_std component of the equivalence
check.)

---

## 2. Baseline correction — static rel_std

**Old recorded value:** static rel_std ≈ 0.014 (from a SINGLE OWE-1.1 calibration run).
**Corrected value:** static rel_std ≈ **0.019** (mean of 3 R0 seeds: 0.0181, 0.0196,
0.0206 for seeds 42/43/44).

The R0 static equivalence check returned rel_std = 0.0194, which exceeded the blueprint's
registered tolerance of 0.014 ± 0.005 (ceiling 0.019) by ≈0.0004 (~2%). On review:

- The 0.014 figure was a single-run value with no distribution behind it; the ±0.005
  tolerance was an estimate of seed scatter, not a measured band.
- The three R0 seeds cluster tightly around 0.0194 with low spread, and **all three sit
  above** the old 0.014 baseline (none below). This is more consistent with the static
  world genuinely running at rel_std ≈ 0.019 than with symmetric noise around 0.014.
- Settled N (2399, within tolerance) and est_starv (0.0000, exact) — the two quantities
  that carry R0's R1-vs-R2 logic — passed cleanly. The rel_std component is a regression
  sanity-check, not load-bearing for the verdict.

**Decision:** accept the result. Replace the recorded static rel_std baseline with the
3-seed value (≈0.019, strictly better data than the prior single run). Widen the registered
equivalence tolerance to **±0.007** to reflect actual measured seed scatter, so this
component does not falsely trip on future re-runs.

**Caveat to record (do not overstate the confound closure):** because rel_std did not match
the old baseline, the static-provenance confirmation is "confirmed static, with a minor
rel_std discrepancy attributable to single-run baseline noise," NOT a clean three-for-three
match. The load-bearing fact (est_starv = 0.0000 under `perturbation: null`) held exactly;
the confound is closed on that basis.

---

## 3. Mechanism note for the design doc (D3 finding)

The static marginal diagnostics indicated §4 sub-reading **(b) near-margin-but-birth-clamped**,
and the D3 parameter-level annotation sharpened it: the carrying-cost birth suppression is
**density-based** (`carry_discount = max(0, 1 − N_C/N_carry)`), operating entirely off the
wealth axis. The wealth-axis birth floor (θ_sub) sits only ≈5 steps-of-metabolism above the
death threshold, but the density clamp bites first. So reproduction is throttled by crowding
long before any agent approaches starvation (D1 5th-pctile = 18.8 steps; D2 5th-pctile =
−3.08).

**Implication carried into the design doc:** the zero-starvation-under-static result is a
*regulation-architecture* feature (density-decoupled-from-mortality), not a resource-
abundance accident. This is an independent argument that R2 (resource-lifetime classes) will
matter eventually even though R1 leads — the resource regime is not the proximate cause of
zero static starvation, the regulation mechanism is.

---

## 4. Process flag (for the next coding-agent directive)

CC proceeded past a **FAILED equivalence gate** (rel_std out of tolerance) and ran the full
seasonal matrix, rather than stopping and reporting as the R0 blueprint's stopping rule #2
required ("any quantity outside tolerance → STOP and report, do not proceed to the seasonal
run"). The breach was benign and the supervisor has accepted the result, but the override
itself was a scope decision the blueprint explicitly reserved for the supervisor.

**Directive for future blueprints/runs:** when a gate fails — even by a small margin — STOP
and surface it for the supervisor's call. Do not absorb a gate breach and proceed. A small
breach may be acceptable, but that judgment is the supervisor's to make, not the coding
agent's to make silently.

---

## 5. What is NOT changed

- No locked parameter altered (p_max_C, p_fission_Si, k_grid, β_Si, τ_pool, ρ, λ, γ,
  N_carry, run-length all unchanged).
- H1(ii) verdict untouched (remains C-DOMINANT and ROBUST per the live ROADMAP; R0 did not
  test it — that is OWE-14, sequenced after R0).
- Only the recorded static rel_std baseline (0.014 → ≈0.019) and its equivalence tolerance
  (±0.005 → ±0.007) are updated, plus the process flag in §4.

---

*End of R0 Verdict and Baseline Correction — 2026-06-02.*
