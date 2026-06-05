# SiC Games — ROADMAP Update Directive

**Version:** 1.0
**Date:** 2026-05-18
**Scope:** ROADMAP.md edits only. No simulation runs. No code changes.
**Estimated time:** < 5 minutes.

---

## Why this exists

The Stage 4.1c patch (SiC_Games_Stage4_1c_Patch.md) required ROADMAP.md to
be updated but the update was not applied. This directive lists every
outstanding ROADMAP change. Apply all of them in one commit.

---

## File location

```
G:\My Drive\docs\SiC Games\ROADMAP.md
```

Edit this file directly. Do not create a copy elsewhere.

---

## Required changes (apply exactly as specified)

### 1. Current status table — update stage statuses

Replace the current status rows for Stage 4.1a through 4.1c with:

```
| Stage 4.1a | ✓ Complete | Variable population. Birth/death decoupled. p_max exploratory. |
| Stage 4.1b | ✓ Complete (patched) | Age-efficiency ramp η(a). η_min=0.3 confirmed. P_max locked: C 0.12, Si 0.14, C seas 0.14, Si seas 0.17. |
| Stage 4.1c | ✓ Complete (patched) | Proximity support pool. Juv starvation: 0.3% C / 0.0% Si. P_max retuned: C static 0.065, Si static 0.28, Si seasonal 0.35. C seasonal: Allee bistability — deferred. Established starvation FAIL flagged (τ_pool=0.10 too aggressive). Cred pool contribution = 0.0 flagged. Both carry to Stage 4.2. |
```

### 2. Locked parameters table — add τ_pool entry

Add the following row to the locked parameters table:

```
| τ_pool | 0.10 (to be recalibrated in Stage 4.2 Task 1) | Stage 4.1c | Pool contribution rate. Criterion 4 FAIL at 0.10 — recalibration pending. |
```

### 3. Open design questions — update Q22

Replace the current Q22 row:
```
| Q22 | τ_C (pool contribution rate) | Default TBD in Stage 4.1c |
```
With:
```
| Q22 | τ_pool recalibration | Set to 0.10 in Stage 4.1c. Established starvation FAIL — reduce in Stage 4.2 Task 1. Target: est. starvation ≤ 130% of 4.1b baseline. |
```

### 4. Standing rules — add Rules 11 and 12

Append the following two rules to the standing rules section (after rule 10):

---

**11. Plot embedding (mandatory from Stage 4.2 onwards).** Every report.md
must embed its diagnostic plots inline using relative paths. Plots must
resolve when report.md is rendered — do not upload plots separately.

Required output structure:
```
outputs/<run_name>/
├── report.md
└── figures/
    ├── <plot_name>.png
    └── ...
```

In report.md, reference plots as:
```markdown
![Caption](figures/plot_name.png)
```

A `generate_figures.py` script (or equivalent) must exist that reads from
parquets and writes all figures to `outputs/<run>/figures/`. This script
must be runnable independently of the simulation (figures regenerable from
cache without re-simulation).

A report without embedded, resolving plot references is incomplete per Rule 10.

---

**12. Pool gate criterion is mean-based.** `pool_draw_unmet_frac < 20%` is
evaluated as the time-mean over t≥500 (or the quasi-stationary window for
that stage). Instantaneous peaks above 20% do not constitute a gate failure
but must be reported alongside the mean in the pool diagnostics table.

Pool diagnostics table format (mandatory when pool is active):

| Config | Mean contributed/step | Mean drawn/step | Mean unmet (t≥500) | Peak unmet (t≥500) | Gate (mean<20%) |
|---|---|---|---|---|---|

---

### 5. Population mechanics tracker — update pending items

In the "Pending — C (Stage 4.1x)" section, mark the support pool as complete
and add γ as pending:

Replace:
```
- [ ] Proximity support pool (τ_parent, τ_pool, k_reserve, k_draw). → Stage 4.1c.
```
With:
```
- [x] Proximity support pool (τ_parent=0.10, τ_pool=0.10→recalibrating, k_reserve=5, k_draw=3). Stage 4.1c. Criterion 4 FAIL — τ_pool recalibration in Stage 4.2.
- [ ] Cred-modulated birth: P_birth × (1 + γ·tanh(𝒞/C***)). γ=0.2 default. → Stage 4.2 Task 2.
```

---

## Deliverable

Single commit to ROADMAP.md with all five changes above.
No other files touched.
Confirm with: `git diff ROADMAP.md` shows only the expected changes.
