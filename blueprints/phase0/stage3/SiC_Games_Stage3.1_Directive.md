# SiC Games — Stage 3.1 Directive: f_C Sweep

**Version:** 1.0
**Applies to:** Stage 3 codebase.
**Scope:** Parameter sweep only. No mechanism changes.

---

## Purpose

Determine the appropriate newborn Cred endowment fraction f_C before Stage 4
introduces perturbation dynamics that would confound the signal. The sweep runs
in a static environment where f_C is the only variable. The selected value becomes
locked for all subsequent stages.

---

## Runs

Four configs, identical to `stage3_carbon_seed42.yaml` except f_C:

| Run name | f_C |
|---|---|
| `stage3_fC00_seed42` | 0.0 (already exists — load from parquet, do not re-run) |
| `stage3_fC01_seed42` | 0.1 (already exists — load from parquet, do not re-run) |
| `stage3_fC025_seed42` | 0.25 |
| `stage3_fC05_seed42` | 0.5 |

Seed=42 for all. 1000 steps. All other parameters unchanged (κ=2.0, σ_base=0.5,
velocity_tau=10, velocity_scale=1.0, δ=0.01).

**Critical:** do not re-run f_C=0.0 or f_C=0.1. Load their metrics directly from:
- `outputs/stage3_carbon_no_endowment_seed42/metrics.parquet`
- `outputs/stage3_carbon_seed42/metrics.parquet`

This preserves confirmed baselines and avoids the BUG-001 class of discrepancy.

---

## Report format

A single report `outputs/stage3_fC_sweep_seed42/report.md` with:

### Primary comparison table

| Metric (final 100 steps) | f_C=0.0 | f_C=0.1 | f_C=0.25 | f_C=0.5 |
|---|---|---|---|---|
| Mean wealth | 45.1 | 44.7 | ? | ? |
| Gini wealth | 0.462 | 0.462 | ? | ? |
| Spatial dispersion | 17.8 | 17.8 | ? | ? |
| Deaths/step (starvation) | 2.86 | 2.98 | ? | ? |
| Deaths/step (newborn) | 2.07 | 2.18 | ? | ? |
| Deaths/step (established) | 0.79 | 0.80 | ? | ? |
| Mean Cred | 9.477 | 7.537 | ? | ? |
| Gini Cred | 0.834 | 0.765 | ? | ? |
| Max Cred fraction | 0.069 | 0.064 | ? | ? |
| Mean sigma | 1.051 | 1.105 | ? | ? |
| Joint tasks/step | 39.46 | 29.21 | ? | ? |
| mean_w_C | 0.290 | 0.288 | ? | ? |

### Starvation by Cred quartile

| Cred quartile | f_C=0.0 | f_C=0.1 | f_C=0.25 | f_C=0.5 |
|---|---|---|---|---|
| Q1 (lowest Cred) | 2.129 | 0.887 | ? | ? |
| Q2 | 0.005 | 0.880 | ? | ? |
| Q3 | 0.426 | 0.982 | ? | ? |
| Q4 (highest Cred) | 0.288 | 0.288 | ? | ? |

### Cred trajectory diagnostic

For f_C=0.25 and f_C=0.5 specifically: plot mean_cred over all 1000 steps.
If mean_cred is still trending upward at t=1000 (growth >5% per 100 steps after
t=500), flag as runaway — that f_C value is off the table regardless of other
metrics.

### Overlay plots (all four f_C values on same axes)

- Mean Cred over time
- Deaths/step (starvation) over time
- Deaths/step (newborn) over time
- Gini Cred over time

---

## What to look for (for the supervisor — not pass/fail criteria)

**Newborn starvation trajectory:** does deaths_starvation_newborn decrease
monotonically with f_C, or does it stabilize or reverse? If it keeps rising
(as it did from f_C=0.0 to f_C=0.1), the endowment is pushing newborns into
higher quartiles without protecting them — and higher f_C makes this worse.

**Total starvation:** does it keep rising with f_C? A monotonic increase would
suggest the endowment-driven σ elevation (higher starting Cred → higher σ at
birth) is net harmful. A stabilization would suggest a sweet spot exists.

**Cred feedback loop:** mean_cred with f_C=0.1 was 7.537 vs 9.477 at f_C=0.0.
Counterintuitively, higher f_C may suppress mean_cred (more egalitarian
distribution, lower Gini) or inflate it (positive feedback: higher endowment →
higher mean_cred → higher next endowment). The trajectory plot resolves this.

**Gini Cred:** the endowment equalizes status (0.834 → 0.765 from f_C=0 to 0.1).
How far does this go at 0.25 and 0.5? Very low Gini Cred weakens the Matthew
effect — if everyone has similar Cred, the super-proportional reward partition
degenerates toward egalitarian. This would undermine the core C mechanism.

**Joint tasks:** dropped from 39.46 to 29.21 between f_C=0.0 and f_C=0.1.
Does this trend continue? If joint tasks collapse at high f_C, the Cred economy
is being diluted past the point of function.

**f_C selection guidance:** prefer the value where:
1. No Cred runaway (mean_cred stable at t=1000)
2. Gini Cred remains meaningfully above 0.6 (Matthew effect intact)
3. Joint tasks/step remains above 25 (mechanic still firing)
4. Total starvation is not catastrophically above f_C=0.0 baseline

---

## Deliverables

1. `outputs/stage3_fC_sweep_seed42/report.md` with primary table, quartile
   table, Cred trajectory diagnostic, and four overlay plots.
2. Reproducibility confirmed for f_C=0.25 and f_C=0.5 runs.
3. No new tests required (no mechanism changes).

## Out of scope

- Any mechanism changes.
- Sweeping any parameter other than f_C.
- Stage 4 spec (follows after supervisor selects f_C).
- Si endowment parameter f_Si — deferred to Stage 5+.
