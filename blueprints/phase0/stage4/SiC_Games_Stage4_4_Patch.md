# SiC Games — Stage 4.4 Patch: Age Initialisation Fix + p_max Re-calibration

**Version:** 1.0
**Scope:** Two targeted fixes only. No new mechanics. No seasonal runs.
**Prerequisite:** Stage 4.4 Diagnostic complete. Diagnosis: H_B_partial (age-out).
  pct_isolated_C = 4.9% (H_A ruled out). p_max=0.07 Run A anomalous (explosion).
**ROADMAP:** `G:\My Drive\docs\SiC Games\ROADMAP.md`
**Output dir:** `outputs/stage44_patch_seed42/`

---

## 0. Problem statement and patch scope

The Stage 4.4 diagnostic concluded that C null control failure is driven
by **age-out**: the realistic age initialisation (Stage 4.1b, upper bound
τ_max/2) seeds too many near-senescent agents at t=0. These age out in a
large first-generation death wave around t≈50–80, faster than p_max=0.03–0.05
can generate replacements. The population then undershoots and cannot recover.

Two anomalies must be resolved before the seasonal sweep can proceed:

1. **Age initialisation upper bound.** `Uniform[0, τ_max/2]` places the mean
   starting age at τ_max/4 ≈ 20 steps. The oldest initial cohort (starting
   near age τ_max/2 ≈ 40) reaches senescence at t≈40–60, creating a
   concentrated death wave. A lower upper bound spreads the senescence load
   across more time and reduces the peak demand on birth rate.

2. **p_max=0.07 explosion.** Run A at p_max=0.07 produced N=[1437, 1633]
   — roughly 4–5× the upper gate — with est_starv=0.75/step. Runs at
   p_max=0.10 and 0.15 collapsed back to N=[0,0]. This non-monotonic
   response (collapse → explosion → collapse) is not explained by the
   diagnostic and must be resolved before locking any p_max value.
   Probable cause: at p_max=0.07 the birth rate exceeds the carrying
   capacity of the k=4 grid, the population overshoots, then a resource
   crash generates a juvenile starvation cascade (est_starv counts only
   established agents, so juveniles dying in bulk shows as 0). Confirming
   this matters because the patch target p_max must sit *below* the
   overshoot threshold, not above it.

**What this patch is not.** No new mechanics. No seasonal runs. No ψ
redesign. No λ changes. No Stage 4.5 carrying-cost work. Two parameter
adjustments + re-calibration only.

---

## 1. Task 0 — Diagnose the p_max=0.07 explosion (no new runs)

Before any new runs, read the Stage 4.4 diagnostic parquets for
Run A p_max=0.07 and extract:

```
# From stage44_diag_seed42 parquet, Run A p_max=0.07:
n_timeseries          # N(t) at every step, t=0..1000
deaths_starvation_juvenile   # starvation deaths, agents age < a_forage_min
deaths_starvation_established
births_per_step
mean_age              # mean age of living agents per step
```

Report in §0 of the patch report:

| Metric | p_max=0.07 |
|---|---|
| N at t=100 | ? |
| N at t=500 | ? |
| N at t=1000 (= N_late min–max) | 1437–1633 |
| Mean births/step (t≥500) | ? |
| est_starv/step (t≥500) | 0.750 |
| Juv starvation deaths/step (t≥500) | ? |
| Mean agent age (t=500) | ? |
| Pool draw unmet % (t≥500) | ? |

**If juv starvation deaths at p_max=0.07 are >> est_starv:** confirms the
overshoot interpretation — births flood the grid with juveniles, resource
depletion drives juvenile starvation, but the adult "established" stratum
survives. The N gate [150,400] is not met because N is too high, not because
C is dying. This is **not extinction** — it is over-calibration.

**If juv starvation deaths are near zero at p_max=0.07:** the explosion is
structural (no density-dependence in the birth rule at k=4 grid scale). Flag
and note: the DTM birth formula may need a population-density ceiling hook
at Stage 4.5, but for now this just means p_max=0.07 is above the upper
viable band.

Either way: the target p_max for the patch sits in the narrow stable band
between the age-out floor (where births can't replace senescence losses)
and the overshoot ceiling (where births exceed carrying capacity). The
age-init fix raises the floor; the sweep in Task 2 finds the ceiling.

---

## 2. Task 1 — Age initialisation fix

### 2.1 The change

Replace the Stage 4.1b initialisation upper bound with a configurable
fraction:

```yaml
# All Stage 4.4 patch configs:
initialization:
  age_distribution: "realistic"
  age_init_upper_frac: 0.25     # NEW — was implicitly 0.5 in Stage 4.1b
```

This changes the draw from:

```
a_i(0) ~ Uniform[0, floor(τ_max,i × 0.5)]    # Stage 4.1b default
```

to:

```
a_i(0) ~ Uniform[0, floor(τ_max,i × 0.25)]   # Stage 4.4 patch
```

With τ_max ∈ [60, 100], this gives starting ages in [0, 15–25]. Mean
starting age ≈ τ_max/8 ≈ 10 steps — just below the foraging_min=15
threshold. Initial agents are mostly juveniles or very young adults; no
agent starts already past their prime foraging window. The first-generation
senescence wave is pushed to t≈45–75 (rather than t≈20–50) and is lower in
amplitude (fewer agents near the upper bound).

The existing `age_distribution: "zero"` config flag continues to work for
regression tests. Stage 4.1b outputs are not re-run.

### 2.2 Implementation requirement

`age_init_upper_frac` must be read from config in the initialisation
routine. The default in code remains 0.5 (preserving Stage 4.1b behaviour
when the key is absent from config). Stage 4.4 patch configs explicitly
set 0.25.

### 2.3 New test

Add to `tests/test_life_history.py`:

```python
def test_age_init_upper_frac():
    """age_init_upper_frac=0.25 produces no agent older than tau_max*0.25."""
    agents = initialise(N=500, age_distribution="realistic",
                        age_init_upper_frac=0.25, seed=42)
    for a in agents:
        assert a.age <= floor(a.tau_max * 0.25), (
            f"Agent age {a.age} exceeds floor(tau_max={a.tau_max} × 0.25)"
        )

def test_age_init_upper_frac_default():
    """age_init_upper_frac=0.5 (default) still produces no agent older than tau_max*0.5."""
    agents = initialise(N=500, age_distribution="realistic", seed=42)
    for a in agents:
        assert a.age <= floor(a.tau_max * 0.5)
```

Run full test suite after the code change. All prior tests must still pass.

---

## 3. Task 2 — p_max re-calibration sweep (Run A bare only)

### 3.1 Sweep design

With the age-init fix applied, re-run C bare null control (pool off, λ=0)
across a wider p_max sweep centred below the explosion threshold:

| Run | p_max | Purpose |
|---|---|---|
| A-p01 | 0.03 | Anchor (Stage 4.4 baseline) |
| A-p02 | 0.04 | Below old range |
| A-p03 | 0.05 | Below old range |
| A-p04 | 0.06 | Approaching old explosion |
| A-p05 | 0.065 | Narrow-band probe |
| A-p06 | 0.07 | Old explosion value (verify resolved or unchanged) |

All runs: seed=42, 1000 steps, k_grid=4, β_Si=5, pool off, λ=0.
age_init_upper_frac=0.25.

**Gate:** N ∈ [150, 400] at t≥500, est_starv ≤ 0.78/step.

**Stopping rule:** run in ascending p_max order. Stop after the first
p_max that produces N > 400 sustained (overshoot confirmed). Record the
minimum viable p_max (first to pass gate) and the overshoot threshold
(first to exceed gate ceiling). The viable band is between them.

**If no p_max passes the gate** (all collapse or all explode): the age-init
fix was insufficient alone. Do NOT try further p_max values beyond 0.07 —
escalate to supervisor. Note the remaining diagnosis: if collapse still
occurs at 0.05 with fixed init, there may be a secondary mechanism (e.g.
the Cred economy or pool draw is interfering even in "bare" runs — check
whether Cred or pool is truly disabled in the bare config).

**Max attempts:** 6 (the sweep above). Do not add more without supervisor
approval.

### 3.2 Additional diagnostics to record per run

Beyond the standard run matrix from the diagnostic (N_late, est_starv,
pct_isolated_C, collapse_step), also record per run:

| Metric | Definition |
|---|---|
| `deaths_senescence/step` | mean senescence deaths per step, t≥500 |
| `deaths_starvation_juv/step` | mean juvenile starvation deaths per step, t≥500 |
| `mean_age` (t=100, 300, 500) | tracks whether age-init fix is working |
| `births/step` (t≥500) | must exceed senescence deaths for stability |

These are the mechanistic check: a stable run requires births/step >
senescence/step + est_starv/step. If the ratio is < 1.0 for all tested
p_max, the birth formula itself is insufficient at k=4 scale and the
problem is not the initialisation.

---

## 4. Task 3 — Pool and λ verification (Runs B/C/D)

Run only after Task 2 produces a locked p_max_C with N ∈ [150, 400].

Use the same 3-value logic as the diagnostic, anchored to the locked value:

| Run | p_max values | Pool | λ |
|---|---|---|---|
| B (pool) | {0.03 anchor, locked, locked+0.01} | On (τ_pool=0.05) | 0 |
| C (λ) | {0.03 anchor, locked, locked+0.01} | Off | 0.1 |
| D (pool+λ) | {0.03 anchor, locked} | On | 0.1 |

**Gate for B/C/D:** same N ∈ [150, 400] and est_starv ≤ 0.78/step.

**If pool shifts viable p_max downward:** reduce τ_pool in steps of 0.01.
Max 3 attempts. Document each attempt.

**If λ=0.1 causes overshoot at locked p_max:** reduce p_max by 0.005 for
Run C/D only. This is expected — inheritance boosts juvenile wealth survival
and may raise equilibrium N. Max 2 p_max reductions for λ runs.

Record the final locked p_max for each condition:

| Condition | Locked p_max | τ_pool | λ | N range (t≥500) |
|---|---|---|---|---|
| Bare (Run A) | ? | off | 0 | ? |
| Pool (Run B) | ? | ? | 0 | ? |
| λ (Run C) | ? | off | 0.1 | ? |
| Pool+λ (Run D) | ? | ? | 0.1 | ? |

The Stage 4.4 seasonal sweep will use the Run D locked values (full
mechanics).

---

## 5. Report format

HTML, single self-contained file:
`outputs/stage44_patch_seed42/report_patch.html`

All figures embedded as base64. No external dependencies.

### §0 Explosion diagnosis
Parquet read from Stage 4.4 diagnostic. Filled table from Task 0.
Plain-language statement of mechanism (overshoot vs structural).

### §1 Age initialisation fix
Code change summary. Test results (pass/fail with counts).
Mean starting age at t=0 for one sample run: confirm ≈ τ_max/8 ≈ 10 steps.

### §2 p_max sweep (Run A)
Full sweep table. Indicate gate pass/fail for each row.
State locked p_max and viable band (min pass → first overshoot).
N(t) overlay plot for all 6 p_max values.
Senescence/births/step ratio table.

### §3 Pool and λ verification (Runs B/C/D)
Full table per condition (Task 3 table above, filled).
Any τ_pool or p_max adjustments documented with attempt history.
Locked values for Stage 4.4 seasonal sweep stated explicitly.

### §4 Recommended next action
One of:
- **Proceed to Stage 4.4 seasonal sweep.** All null controls pass.
  Locked parameters: k_grid=4, p_max_C=X, τ_pool=Y, λ=Z.
- **Escalate.** State specific blocking condition and what supervisor
  decision is needed before proceeding.

---

## 6. Success criteria

| Criterion | Target |
|---|---|
| `age_init_upper_frac` config parameter implemented | Confirmed in code + test |
| New age-init test passes | PASS |
| Full test suite still passes | All prior tests green |
| Task 0 explosion mechanism stated | Plain text, no "see plot" |
| p_max sweep complete | All 6 runs (or stopped at first overshoot, documented) |
| Viable p_max band identified | min-pass to first-overshoot stated numerically |
| Locked p_max for bare C | N ∈ [150, 400], est_starv ≤ 0.78/step |
| Runs B/C/D complete at locked p_max | Gate pass for each condition |
| Stage 4.4 seasonal locked params stated | p_max_C, τ_pool, λ all explicit |
| ROADMAP.md updated | Stage 4.4 Patch row added, locked params recorded |
| Reproducibility | seed=42 throughout |

---

## 7. Coding-agent directives

1. **Task 0 first, before any new runs.** Read the existing diagnostic
   parquet. The explosion mechanism must be stated before the sweep is
   designed. If the parquet for p_max=0.07 Run A does not contain
   `deaths_starvation_juvenile`, compute it from available age and death
   fields (age < a_forage_min = 15 at death step).

2. **Implement and test before running.** Add `age_init_upper_frac` to
   config and code, add tests, confirm suite passes — then run Task 2.
   Do not run simulations against unverified code.

3. **Run A sweep in strict ascending order.** Stop at the first overshoot.
   Do not run all 6 simultaneously if early results show the overshoot
   threshold is at p_max=0.04 — that would waste compute and obscure the
   phase structure.

4. **Do not attempt to rescue C by other means.** If the age-init fix +
   p_max sweep does not produce a passing run within the Task 2 budget,
   report that and stop. Do not start adjusting η_min, τ_pool, parent_radius,
   or any other parameter.

5. **Verify "bare" configs are truly bare.** Check that pool is disabled and
   λ=0 in Task 2 configs. A partial re-activation of pool or λ in a config
   that is supposed to be bare would contaminate the isolation.

6. **Report every tuning attempt.** Table entries must be filled with numbers,
   not PASS/FAIL only. Every run that executes must appear in the report.

7. **Update ROADMAP.md** at completion. Add a new row:
   ```
   | Stage 4.4 Patch | ✓ Complete | age_init_upper_frac=0.25.
                       Locked: p_max_C=X, τ_pool=Y, λ=0.1.
                       N=[min,max]. Explosion at p_max=0.07 confirmed as [mechanism]. |
   ```
   Update the locked parameters table with p_max_C (Stage 4.4), τ_pool
   (Stage 4.4 confirmed or adjusted), and age_init_upper_frac.

8. **Standing rules 11 and 12 apply.** Report is HTML with base64 figures.
   Pool gate is evaluated as time-mean over t≥500, not instantaneous peak.

---

## 8. Out of scope

- Stage 4.4 seasonal sweep → follows after this patch passes.
- ψ redesign → Stage 4.4 Task 2 (unchanged).
- λ sweep → Stage 4.4 Task 1 handles λ=0.1 verification only.
- Carrying-cost redesign → Stage 4.5 (flagged, deferred).
- Any change to parent_radius, η_min, growback_alpha, or grid structure.
- Multi-seed ensemble runs.

---

*End of Stage 4.4 Patch Blueprint*
