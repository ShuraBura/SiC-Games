# SiC Games — Stage 2.2 Directive: Baseline Fix + κ Sweep

**Version:** 1.0
**Applies to:** Stage 2 patched codebase (post patch 2.1).
**Scope:** Two tasks only. No mechanism changes.

---

## Task 1 — Fix the baseline discrepancy

### Problem
The three-way comparison table in the Stage 2.1 patched report shows C baseline
numbers that differ from the confirmed Stage 2 baseline report:

| Metric | Confirmed Stage 2 baseline | Three-way table "C baseline" |
|---|---|---|
| Mean wealth | 42.0 | 45.8 |
| Mean Cred | 6.923 | 7.141 |
| Joint tasks/step | 30.41 | 31.06 |

These should be identical (same seed, same mechanism). They are not.

### Required actions

1. **Diagnose the cause.** Identify exactly what changed in the noswitch reference
   run that produced different numbers. The most likely cause: adding `wealth_velocity`
   to `BaseAgent` altered the RNG call sequence at agent initialization, shifting the
   trajectory even with seed=42. Confirm or refute this with a code audit.

2. **Fix the reference strategy.** Do not re-run the Stage 2 baseline to generate
   comparison numbers. Instead, load the confirmed baseline directly from its saved
   parquet:
   ```
   outputs/stage2_carbon_seed42/metrics.parquet
   ```
   The comparison columns in all future reports must be read from this file, not
   from a live re-run. This freezes the confirmed baseline as ground truth.

3. **Verify the fix.** After the code change, confirm that the three-way comparison
   table in a fresh patched run (seed=42) shows the confirmed numbers (42.0, 6.923,
   30.41) in the C baseline column, not the drifted values.

4. **Document the root cause in LITERATURE.md** (or a new `BUGS.md` if preferred)
   with: what changed, why it shifted the trajectory, and the fix applied.

### Deliverable
A short written explanation (in the Notes section of the Stage 2.2 report) of what
caused the discrepancy and how it was resolved. No plots needed for this task alone.

---

## Task 2 — κ sweep

### Purpose
Determine how sensitive mean_sigma and starvation rate are to κ, the maximum
additional noise Cred can add. This resolves two open questions:
- Q4 (variance-matching): provides the σ_Si calibration target for Stage 3.
- Design: gives a defensible κ choice before the definitive C vs Si comparison.

### Runs

Three configs, identical to `stage2_carbon_patched_seed42.yaml` except κ:

| Run name | κ |
|---|---|
| `stage2_kappa10_seed42` | 1.0 |
| `stage2_kappa20_seed42` | 2.0 (patched baseline — already have it) |
| `stage2_kappa30_seed42` | 3.0 |

Seed=42 for all. 1000 steps. All other parameters unchanged.

### Report format

A single report `stage2_kappa_sweep_seed42/report.md` containing one comparison
table across all three runs (do not produce three separate reports):

| Metric (final 100 steps) | κ=1.0 | κ=2.0 | κ=3.0 |
|---|---|---|---|
| Mean wealth | | 45.1 | |
| Gini wealth | | 0.46 | |
| Spatial dispersion | | 17.8 | |
| Deaths/step (starvation) | | 2.9 | |
| Deaths/step (senescence) | | 2.4 | |
| Mean Cred | | 9.477 | |
| Gini Cred | | 0.834 | |
| Max Cred fraction | | 0.069 | |
| Mean sigma | | 1.051 | |
| Joint tasks/step | | 39.46 | |
| mean_w_C | | ? | |
| frac_suppressed | | ? | |

### Additional diagnostic (new — not in prior reports)

**Starvation by Cred quartile.** For each run, divide the agent population into
four quartiles by Cred level (Q1=lowest, Q4=highest) and report mean
deaths/step (starvation) within each quartile. This directly answers whether
starvation is concentrated in high-Cred agents (mechanism working as designed)
or distributed uniformly (mechanical artifact).

Format:

| Cred quartile | κ=1.0 | κ=2.0 | κ=3.0 |
|---|---|---|---|
| Q1 (lowest Cred) | | | |
| Q2 | | | |
| Q3 | | | |
| Q4 (highest Cred) | | | |

### Overlay plots

For the sweep report, produce overlay plots (all three κ values on the same axes,
distinct colors) for:
- Mean sigma over time
- Deaths/step (starvation) over time
- Mean Cred over time
- Gini Cred over time

### What to look for (for the supervisor — not a pass/fail criterion)

- **If starvation concentrates in Q4 across all κ values:** the σ-Cred mechanism
  is the genuine driver. Starvation excess is the real exploration cost, not an
  artifact.
- **If starvation is uniform across quartiles:** investigate crowding near peaks
  as the cause.
- **σ_Si calibration target:** the mean_sigma value from whichever κ is selected
  becomes the fixed temperature for Stage 3's bounded-rational Si.
- **κ selection guidance:** prefer the κ where mean_sigma is meaningfully above
  σ_base (exploration is real) but starvation excess over Si is not catastrophic
  (< 2× the Si rate of 1.8, i.e., < 3.6 deaths/step).

---

## Deliverables

1. Written diagnosis of the baseline discrepancy (Task 1).
2. `outputs/stage2_kappa_sweep_seed42/report.md` with the two tables and four
   overlay plots above (Task 2).
3. All new pytest tests pass (no new mechanism code, so this should be trivial).
4. Reproducibility confirmed for all three κ runs.

## Out of scope

- Any mechanism changes.
- Any changes to Stage 1 files.
- Stage 3 spec (follows after supervisor reviews sweep results).
- Parameter sweeps over anything other than κ.
