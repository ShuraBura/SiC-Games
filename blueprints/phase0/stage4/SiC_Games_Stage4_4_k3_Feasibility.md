# SiC Games — Stage 4.4 Patch: k=3 Feasibility Check

**Version:** 1.0
**Parent:** Stage 4.4 Patch (all three fixes confirmed: age_init_upper_frac=0.25,
  wealth_init_scale_k, cluster_init). 166/166 tests passing.
**Scope:** Feasibility check only. Two tasks, strict order. No new mechanics.
**Question:** Can Si pass its null control gate at k=3? If yes, can C find a
  stable attractor at k=3?
**Output dir:** `outputs/stage44_k3_feasibility_seed42/`

---

## Context

The Stage 4.4 blueprint calibrated the grid starting at k=4 and going upward
(k=4, 5, 6) because the k=1 grid was known to be too sparse for Si at β=5.
k=3 was never tested. At k=3 (max_sugar=12, growback_alpha=3), Si mean
harvest is approximately 3× the k=1 baseline (~7–9/step), while Si mean
metabolism is 12.5/step. Dormancy will be required, but the question is
whether the dormancy rate stays below the 20% gate. C at k=3 benefits from
restored resource competition as a density-dependent ceiling, which should
allow a stable attractor in [150, 400] to exist.

This is a binary feasibility check: run, read results, escalate or proceed.
Max 9 new runs total (3 Si + 6 C). Do not tune beyond the attempt budgets
specified below.

---

## Grid parameters at k=3

```yaml
world:
  max_sugar:       12    # 4 × k = 4 × 3
  growback_alpha:  3     # 1 × k = 1 × 3
  # All other world params unchanged: 50×50 toroidal, same peak positions
```

---

## Task 1 — Si static null control at k=3

### Config

```yaml
# stage44_k3_si_static_seed42.yaml
seed: 42
world:
  max_sugar: 12
  growback_alpha: 3
agents:
  type: Si
  beta_metabolism: 5.0
dormancy:
  enabled: true
  k_dormant: 1.0
  tau_trickle: 0.05
  k_reactivate: 3.0
  t_dormant_max: 50
pool:
  enabled: false
initialization:
  age_distribution: realistic
  age_init_upper_frac: 0.5    # Si uses Stage 4.1b default — no cluster needed
  wealth_init_scale_k: true   # Uniform[5×3, 25×3] = [15, 75]
reproduction:
  p_fission: 0.28             # Stage 4.3 locked value — start here
run:
  n_steps: 1000
  seed: 42
```

### Gate

| Criterion | Target |
|---|---|
| N_active ∈ [150, 400] at t≥500 | Required |
| dormancy_rate < 20% at t≥500 | Required |
| permanent_dormancy_deaths ≤ 0.5/step | Required |

### Tuning protocol

Start at p_fission=0.28 (Stage 4.3 locked value). If gate fails:

| Attempt | Adjustment | Rationale |
|---|---|---|
| 1 | p_fission=0.28 | Stage 4.3 baseline |
| 2 | p_fission=0.35 | Richer grid suppresses fission; raise to compensate |
| 3 | p_fission=0.20 | If N overshoots; reduce |

Max 3 attempts. Report all. Do not adjust dormancy parameters — they are
locked from Stage 4.3 and should be tested as-is.

**If dormancy_rate > 20% at all attempts:** k=3 is insufficient for Si at
β=5. Record this, skip Task 2, and escalate. The feasibility check is
complete — its answer is "k=3 does not work for Si."

**If N_active gate passes but permanent_dormancy_deaths > 0.5/step:** note
as a flag but do not block. This is a softer criterion; if the N gate passes
and dormancy_rate < 20%, proceed to Task 2 and record the deaths value.

### Metrics to report

| Metric | Window |
|---|---|
| N_active mean, min, max | t≥500 |
| N_total (active + dormant) | t≥500 |
| dormancy_rate | t≥500 |
| mean_dormancy_duration | t≥500 |
| permanent_dormancy_deaths/step | t≥500 |
| mean_wealth (active agents) | t≥500 |

---

## Task 2 — C bare null control at k=3

**Run only if Task 1 passes all three gate criteria.**

### Config (base)

```yaml
# stage44_k3_c_bare_pXXX_seed42.yaml
seed: 42
world:
  max_sugar: 12
  growback_alpha: 3
agents:
  type: C
pool:
  enabled: false
reproduction:
  lambda_inheritance: 0.0
initialization:
  age_distribution: realistic
  age_init_upper_frac: 0.25
  wealth_init_scale_k: true   # Uniform[5×3, 25×3] = [15, 75]
  cluster_init: true
  cluster_peak_index: 0
  cluster_radius: 10
run:
  n_steps: 1000
  seed: 42
```

### p_max sweep

| Run | p_max |
|---|---|
| C-p01 | 0.03 |
| C-p02 | 0.04 |
| C-p03 | 0.05 |
| C-p04 | 0.06 |
| C-p05 | 0.065 |
| C-p06 | 0.07 |

Run in ascending order. Stop at first overshoot (N > 400 sustained).

**Gate:** N ∈ [150, 400] at t≥500, est_starv ≤ 0.78/step.

**If a p_max passes the gate:** record as locked p_max_C for k=3. This is
the feasibility check passing. Do not proceed to pool/λ verification here —
that follows in a separate directive if this check passes.

**If no p_max passes:** k=3 does not resolve C's bistability. Escalate.
Report which mechanism is still blocking (same diagnostic columns as prior
patch sweeps).

### Metrics to report (same columns as Task 2c in patch report)

est_starv/step, births/step, senes/step, juv_starv/step, mean_age at
t=100/300/500, pct_isolated_C at t=0/50/100/300, w_step1.

---

## Report format

HTML, single self-contained file:
`outputs/stage44_k3_feasibility_seed42/report_k3.html`

All figures base64-embedded.

### §0 — k=3 grid context
One-paragraph rationale. State max_sugar=12, growback_alpha=3, wealth
init=[15,75]. Confirm no code changes — config change only.

### §1 — Si static null control
Tuning history table (all attempts). Final gate assessment (PASS/FAIL per
criterion). Dormancy diagnostics table. N(t) plot with n_active and n_total
overlaid.

### §2 — C bare p_max sweep
Full sweep table. Gate pass/fail per row. Locked p_max if found.
N(t) overlay plot.

### §3 — Feasibility verdict
One of:
- **PROCEED.** Si passes at k=3 (p_fission=X). C passes at k=3 (p_max=Y).
  Locked values: k_grid=3, p_fission_Si=X, p_max_C=Y. Ready for pool/λ
  verification.
- **Si FAIL.** k=3 insufficient for Si at β=5 (dormancy_rate=Z%).
  k=4 minimum confirmed. Escalate to Stage 4.5 or Option A.
- **C FAIL.** Si passes at k=3 but C bistability persists. State blocking
  mechanism. Escalate.

---

## Success criteria

| Criterion | Target |
|---|---|
| No code changes | Config only — verify |
| Si attempt history reported | All attempts with numbers |
| C sweep reported | All 6 runs (or stopped at overshoot) |
| §3 verdict present | Explicit PROCEED or FAIL with locked values or reason |
| ROADMAP updated | New row for k=3 feasibility check result |
| Tests unchanged | 166/166 still passing — verify with `py -m pytest tests/ -q` |

---

## Out of scope

- Pool/λ verification → follows if §3 verdict is PROCEED.
- Dormancy parameter tuning → locked from Stage 4.3.
- Any C mechanic changes (η_min, parent_radius, γ, ψ).
- Seasonal runs.
- Multi-seed runs.

---

*End of Stage 4.4 k=3 Feasibility Directive*
