# SiC Games — Stage 4.1c Patch: Missing Metrics + Report Standards

**Version:** 1.0
**Date:** 2026-05-18
**Scope:** Two tasks. No mechanism changes, no new runs.

---

## Why this patch exists

Stage 4.1c passed its primary gate criteria but left four gaps that must be
closed before the stage can be marked complete:

1. **Criterion 4 unverified** — blueprint §5 requires deaths/step (established)
   ≤ 30% above Stage 4.1b baseline (C: 0.60/step, Si: 0.90/step). The report
   shows elder starvation % but never reports this specific number.

2. **n_mvp_threshold not reported** — required metric (blueprint §1.4, §2).
   Relevant to Stage 4.2 Allee bistability design.

3. **Parental transfer and Cred pool contribution reported as "(tracked)"**
   with no actual numbers in the primary comparison table.

4. **ROADMAP.md not updated** — blueprint directive §7.8 requires marking
   Stage 4.1c complete with juvenile starvation % achieved and P_max adjustments
   noted.

Additionally, this patch introduces updated standing rules for report plots
and gate criterion interpretation (see Task 2).

---

## Task 1 — Fill missing metrics from parquets

**Source:** `outputs/stage41c_{config}_seed42/metrics.parquet` for all four
configs. Do not re-run any simulation. Read from cache only.

### 1.1 Criterion 4 — established starvation

From each null-control parquet (c_static, si_static), compute for t≥500:

```
deaths_per_step_established_C  = mean(established_deaths_per_step, t≥500)
deaths_per_step_established_Si = mean(established_deaths_per_step, t≥500)
```

Compare against Stage 4.1b baseline values: C = 0.60/step, Si = 0.90/step.

Threshold: must not exceed 30% above baseline.
- C threshold: 0.60 × 1.30 = 0.78 deaths/step
- Si threshold: 0.90 × 1.30 = 1.17 deaths/step

Report as PASS or FAIL with the observed value.

**If FAIL:** this is a real finding — the pool is impoverishing active adults.
Do not silently adjust parameters. Flag for supervisor with the observed value
and a note that τ_pool may need reduction in Stage 4.2.

### 1.2 n_mvp_threshold

From each run parquet, compute:

```
n_mvp_threshold = min N(t) observed before N first recovers above 200
                  within any 100-step window
```

Per blueprint §1.4: "minimum N observed before population recovers to above
200 in any 100-step window. This is the operational measure of the Allee
threshold."

For C seasonal (collapsed): n_mvp_threshold = min N(t) over full run
(population never recovers — record as "collapse: min N = X at t = Y").

Report one value per config in the primary comparison table.

### 1.3 Parental transfer and Cred pool contribution

From null-control parquets, compute for t≥500:

```
mean_parental_transfer_C  = mean(mean_parental_transfer, t≥500)  [C static]
mean_parental_transfer_Si = mean(mean_parental_transfer, t≥500)  [Si static]
cred_pool_contribution_C  = mean(cred_pool_contribution, t≥500)  [C static]
```

Replace the "(tracked)" placeholders in the primary comparison table with
these numbers.

### 1.4 Updated report

Append a **§ Patch notes** section to
`outputs/stage41c_seed42/report.md` containing:

- Updated primary comparison table with all "(tracked)" cells filled in
- Updated §7 success criteria table with Criterion 4 result (PASS/FAIL +
  observed deaths/step values for C and Si)
- n_mvp_threshold row added to primary comparison table
- Pool gate interpretation note (see §Pool gate clarification below)

Do not rewrite the existing report — append the patch section at the end
with a clear heading: `## Patch 2026-05-18 — Missing metrics`.

---

## Pool gate clarification (add to patch notes)

The blueprint §5 criterion 2 says "pool_draw_unmet_frac < 20% at steady
state." This patch locks the interpretation:

**Gate is evaluated as time-mean over t≥500, not as instantaneous maximum.**

Rationale: pool exhaustion is bursty (correlated with birth events and
seasonal troughs). Instantaneous peaks above 20% during otherwise healthy
runs do not indicate a structurally depleted pool. The mean captures the
baseline resource balance.

**However:** instantaneous peaks must be reported and are informative.
Add the following to the pool diagnostics table:

| Config | Mean unmet (t≥500) | Peak unmet (t≥500) | Gate (mean<20%) |
|---|---|---|---|
| C static | 8.6% | ? | PASS |
| Si static | 0.1% | ? | PASS |
| C seasonal | (collapsed) | — | — |
| Si seasonal | 22.3% | ? | FLAGGED |

Fill in peak unmet values from parquets:
```
peak_unmet_C_static  = max(pool_draw_unmet_frac, t≥500)  [c_static parquet]
peak_unmet_Si_static = max(pool_draw_unmet_frac, t≥500)  [si_static parquet]
peak_unmet_Si_seas   = max(pool_draw_unmet_frac, t≥500)  [si_seasonal parquet]
```

---

## Task 2 — Update ROADMAP.md standing rules

### 2.1 Mark Stage 4.1c complete

Update the current status table in ROADMAP.md:

```
| Stage 4.1c | ✓ Complete | Proximity support pool. Juv starvation: 0.3% C / 0.0% Si.
               P_max retuned: C static 0.065, Si static 0.28.
               C seasonal: Allee bistability — deferred to Stage 4.2+.
               Si seasonal: pool unmet 22.3% at troughs — flagged. |
```

Also update Stage 4.1a and 4.1b if they show as pending/in-progress — they
should be marked complete per earlier patches.

### 2.2 Add standing rule 11 — Plot embedding

Add the following as standing rule 11 in the ROADMAP.md standing rules
section:

---

**11. Plot embedding (mandatory from Stage 4.1c onwards).** Every report.md
must embed its diagnostic plots inline using relative paths. Plots are NOT
uploaded separately alongside the report — they must resolve when the
report.md is rendered.

**Required structure:**

```
outputs/<run_name>/
├── report.md
└── figures/
    ├── population_trajectory.png
    ├── pool_diagnostics_<config>.png
    └── <any additional diagnostic plots>
```

**In report.md:**

```markdown
## Plots

### Population trajectory
![N(t) — null controls](figures/population_trajectory.png)

### Pool diagnostics — C static
![Pool diagnostics C static](figures/pool_diagnostics_c_static.png)

### Pool diagnostics — Si static
![Pool diagnostics Si static](figures/pool_diagnostics_si_static.png)

### Pool diagnostics — C seasonal
![Pool diagnostics C seasonal](figures/pool_diagnostics_c_seasonal.png)

### Pool diagnostics — Si seasonal
![Pool diagnostics Si seasonal](figures/pool_diagnostics_si_seasonal.png)
```

**Figure generation:** add a `generate_figures.py` (or equivalent) script
that reads from parquets and writes all figures to `outputs/<run>/figures/`.
This script must be callable independently of the simulation run so figures
can be regenerated without re-simulation.

**Minimum required plots per stage** (add stage-specific plots in the
blueprint §4 Report format section):
- N(t) time series for all configs in one overlay
- Pool diagnostics (N, contributed/drawn, unmet fraction) for each config
  that has a pool active
- Any plot referenced in the blueprint report format section

A report without embedded plots is incomplete per rule 10.

---

### 2.3 Add standing rule 12 — Pool gate interpretation

Add the following as standing rule 12:

---

**12. Pool gate criterion is mean-based.** `pool_draw_unmet_frac < 20%` is
evaluated as the time-mean over t≥500 (or the quasi-stationary window for
that stage). Instantaneous peaks above 20% do not constitute a gate failure
but must be reported alongside the mean (see pool diagnostics table format
established in Stage 4.1c patch).

---

## Deliverable checklist

- [ ] `outputs/stage41c_seed42/report.md` appended with `## Patch 2026-05-18`
      section containing: filled comparison table, Criterion 4 PASS/FAIL,
      n_mvp_threshold values, peak unmet fractions
- [ ] `ROADMAP.md` updated: Stage 4.1c marked complete, standing rules 11+12 added
- [ ] No simulation re-runs
- [ ] No mechanism code changes
- [ ] Tests unchanged (142/142 still passing — verify with `py -m pytest tests/ -q`)

---

## Out of scope

- Any parameter changes
- Stage 4.2 design
- New simulation runs
- Changes to any mechanism code
