# SiC Games — Stage 4.5 Blueprint: C Carrying-Cost Fix + H1(ii) Sweep

**Version:** 1.0
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Five tasks in strict order. Tasks 0–1 are blockers; Tasks 2–4 follow
  sequentially. No task may begin before its predecessor passes all gate criteria.
**Prerequisites:**
  - k_grid=4 confirmed (Si minimum viable grid)
  - β_Si=5.0 confirmed viable at k=4
  - All Stage 4.4 patch fixes active: age_init_upper_frac=0.25,
    wealth_init_scale_k=True, cluster_init=True (C only, peak_index=0, radius=10)
  - Dormancy locked: k_dormant=1.0, τ_trickle=0.05, k_reactivate=3.0, T_dormant_max=50
  - Pool locked: τ_pool=0.05, ρ=0.3, γ=0.2
  - 166/166 tests passing
  - p_max_C: NOT LOCKED (blocked by Stage 4.4 patch — Task 0 of this stage)
  - λ=0.1: scoped but not verified
  - ψ redesign: deferred from Stage 4.4, now Task 2
**ROADMAP:** `G:\My Drive\docs\SiC Games\ROADMAP.md`
**Output dir:** `outputs/stage45_seed42/`

---

## 0. North Star (read first, every session)

**Stage 4.5 goal:** fix C's bistability at k=4, complete all Stage 4.4 mechanics
that were blocked by the null control failure, and run the first valid H1(ii)
seasonal sweep.

Stage 4.4 + patch established k=4 as the minimum viable grid for Si at β=5, and
confirmed all three patch fixes (age-init, wealth scaling, cluster init). However,
C's birth formula has no density-dependent ceiling at k=4, producing a bistable
system with no stable attractor in [150, 400]. Task 0 adds the carrying-cost
mechanic that gives C a natural population ceiling. Everything downstream — pool/λ
verification, ψ redesign, Si pool, and the seasonal sweep — was blocked by this
null control failure and is now addressed in strict order.

**What Stage 4.5 is not.** No β sweep. No ρ sweep. No multi-seed runs. No Si Cred.
No inter-pool connectivity. No c1/c2 behavioral hooks.

---

## 1. Task 0 — C carrying-cost birth ceiling (new mechanic)

### 1.1 Rationale

At k=4, grid resources are abundant enough that the DTM birth formula produces
births faster than senescence and starvation can remove agents, driving the
population to the upper attractor (N≈1500). Below a critical p_max, the
population collapses; above it, the population explodes. No stable equilibrium
exists in [150, 400].

The fix: add a global density-dependent discount to C's birth probability. As
N_C rises, birth probability falls, creating a stable equilibrium at the level
where births and deaths balance. This is mechanistically grounded — in biological
populations, resource competition and crowding suppress reproduction as density
rises, independent of individual wealth.

**C only.** Si reproduces via fission gated by wealth threshold; Si does not use
this mechanic.

### 1.2 Mechanic specification

Replace the bare birth probability `p_birth = p_max × DTM_factor` with:

```
p_birth_effective = p_max × DTM_factor × carry_discount(N_C)

carry_discount(N_C) = max(0.0,  1.0 - alpha_carry × (N_C / N_carry))
```

Where:
- `N_C` = total living C agents at current step
- `N_carry` = carrying capacity (config, default 400)
- `alpha_carry` = discount steepness (config, default 1.0)
- `DTM_factor` = existing wealth + Cred modulation (unchanged)

**Behaviour:**
- At N_C = 0: `carry_discount = 1.0` — no discount, full birth rate
- At N_C = N_carry: `carry_discount = 0.0` — births suppressed entirely
- At N_C = N_carry/2: `carry_discount = 0.5` — births at half rate

With alpha_carry=1.0, the function is linear. Values of alpha_carry > 1.0 produce
a steeper discount (ceiling bites harder at lower N); values < 1.0 produce a
gentler ceiling.

### 1.3 Config

```yaml
# C configs only — never Si
reproduction:
  p_max: 0.05           # starting value for Task 0 sweep
  carrying_cost:
    enabled: true
    N_carry: 400         # carrying capacity; start at upper gate
    alpha_carry: 1.0     # discount steepness; start at 1.0 (linear)
```

`enabled: false` (default) preserves all prior behaviour. All prior C configs
that omit `carrying_cost` are unaffected.

### 1.4 New tests

Add to `tests/test_birth.py`:

```python
def test_carry_discount_at_zero():
    """carry_discount = 1.0 when N_C = 0."""
    assert carry_discount(N_C=0, N_carry=400, alpha_carry=1.0) == 1.0

def test_carry_discount_at_capacity():
    """carry_discount = 0.0 when N_C = N_carry."""
    assert carry_discount(N_C=400, N_carry=400, alpha_carry=1.0) == 0.0

def test_carry_discount_midpoint():
    """carry_discount = 0.5 at N_C = N_carry / 2."""
    assert abs(carry_discount(N_C=200, N_carry=400, alpha_carry=1.0) - 0.5) < 1e-9

def test_carry_discount_no_negative():
    """carry_discount never goes below 0.0."""
    assert carry_discount(N_C=800, N_carry=400, alpha_carry=1.0) == 0.0

def test_carry_discount_disabled():
    """When enabled=False, birth probability is unchanged."""
    # Confirm that p_birth_effective == p_max * DTM_factor when disabled
    ...
```

Run full test suite. All 166 prior tests must pass; suite should reach ≥171.

### 1.5 Task 0 p_max sweep

With carrying_cost enabled (N_carry=400, alpha_carry=1.0), re-run the C bare
null control sweep. All patch fixes active (age_init_upper_frac=0.25,
wealth_init_scale_k=True, cluster_init=True). Pool OFF, λ=0.

| Run | p_max | Expected outcome |
|---|---|---|
| T0-p01 | 0.05 | Reference — collapsed in patch, may now stabilise |
| T0-p02 | 0.06 | Was slow-drift collapse in patch |
| T0-p03 | 0.07 | Was overshoot/upper attractor |
| T0-p04 | 0.08 | New territory |
| T0-p05 | 0.09 | New territory |
| T0-p06 | 0.10 | Upper bound probe |

Run in ascending order. Stop after first sustained overshoot (N > 400).

**Gate:** N ∈ [150, 400] at t≥500, est_starv ≤ 0.78/step.

**If no p_max passes with N_carry=400, alpha_carry=1.0:**
Try alpha_carry=1.5 (steeper discount) at p_max=0.07 and 0.08. Max 2
additional runs. If still no pass, try N_carry=300. Max 2 more. Document
every attempt. Do not go beyond 10 total Task 0 runs without supervisor
approval.

**If equilibrium N is consistently < 150 across all p_max values:**
N_carry is too low or alpha_carry too steep. Reduce alpha_carry to 0.7 and
re-run from p_max=0.07. Max 3 additional runs.

**Stopping condition:** record the first p_max that produces N ∈ [150, 400]
as the bare locked value `p_max_C_bare`. Also record the N_carry and
alpha_carry values that produced the pass.

**Additional metrics per run** (same as patch Task 2c, plus):

| Metric | Definition |
|---|---|
| `carry_discount_mean` | mean carry_discount(N_C) per step, t≥500 |
| `p_birth_effective_mean` | mean p_birth_effective per step, t≥500 |
| `births/step` | t≥500 |
| `senescence/step` | t≥500 |
| `births/senes ratio` | must be ≥ 1.0 for stability |

The `carry_discount_mean` at steady state should be in (0, 1) — it being 1.0
means the ceiling is not engaged (N << N_carry); it being 0.0 means births
are fully suppressed (unstable).

---

## 2. Task 1 — C pool/λ verification (Runs B/C/D)

Run immediately after Task 0 produces a locked `p_max_C_bare`.
This is the pool/λ verification that was skipped in the patch (Task 3 of the
patch blueprint). Procedure is carried over verbatim:

**Configs** (anchor at p_max_C_bare from Task 0, locked N_carry/alpha_carry):

| Run | p_max values | Pool | λ |
|---|---|---|---|
| B (pool) | {0.03 anchor, p_max_C_bare, p_max_C_bare+0.01} | On (τ_pool=0.05, ρ=0.3) | 0 |
| C (λ) | {0.03 anchor, p_max_C_bare, p_max_C_bare+0.01} | Off | 0.1 |
| D (pool+λ) | {0.03 anchor, p_max_C_bare} | On | 0.1 |

**Gate for B/C/D:** N ∈ [150, 400], est_starv ≤ 0.78/step.

**Adjustment rules** (same as patch blueprint Task 3):
- If pool shifts viable p_max downward: reduce τ_pool in steps of 0.01, max 3 attempts.
- If λ=0.1 causes overshoot at p_max_C_bare: reduce p_max by 0.005 for C/D only, max 2 reductions.

**Output table** (must be filled, no blanks):

| Condition | p_max_C | N_carry | alpha_carry | τ_pool | λ | N_late [lo,hi] | est_starv |
|---|---|---|---|---|---|---|---|
| Bare (A) | ? | ? | ? | off | 0 | ? | ? |
| Pool (B) | ? | ? | ? | ? | 0 | ? | ? |
| λ (C) | ? | ? | ? | off | 0.1 | ? | ? |
| Pool+λ (D) | ? | ? | ? | ? | 0.1 | ? | ? |

The Stage 4.5 seasonal sweep uses the Run D locked values (pool ON, λ=0.1).
State these explicitly at the end of §1: `p_max_C_final`, `τ_pool_final`,
`λ=0.1`, `N_carry`, `alpha_carry`.

---

## 3. Task 2 — ψ redesign

Deferred from Stage 4.4 Task 2. Carry over spec verbatim.

### 3.1 Diagnosis first (no runs)

Read `agents/carbon_decision.py` and `death_events.parquet` from any prior
C seasonal run. Report in §2 of the Stage 4.5 report:

1. How ψ_i is initialised at birth (distribution, range, config key)
2. Where ψ_i enters the utility function (which term, coefficient)
3. Whether ψ_i changes during lifetime or is fixed at birth
4. Observed ψ range in parquets (min, max, mean, std)

Expected finding: ψ drawn from a narrow distribution with a small coefficient,
producing the flat quartile starvation distribution observed in Stage 4.3.

### 3.2 Redesign

Make ψ_i the multiplicative weight on the proximity utility term:

```
U_ij^C = w_R(i) × ΔR_ij_norm
        + w_C(i) × ΔC_ij_norm
        + ψ_i   × ΔP_ij_norm
```

Where `ΔP_ij_norm` = number of C agents within r_pool radius of cell j,
normalised to [0,1] across candidate cells.

**ψ_i distribution:** Beta(2, 2) at birth — range [0, 1], peaked at 0.5,
meaningful tails. Replace whatever narrow distribution is currently in use.

**C only.** ψ_i is carried in Si's trait vector but the hook remains deferred
(Stage 5+). Do not activate for Si.

### 3.3 Verification

Run C static null control with redesigned ψ. Use p_max_C_final and N_carry
from Task 1.

Verify:
- N still ∈ [150, 400] at t≥500 (ψ redesign must not destabilise population)
- ψ distribution at steady state: mean ≈ 0.5, std ≈ 0.18 (Beta(2,2) moments)
- Gini of ψ > 0.1 (confirm meaningful spread — flat Gini means redesign failed)
- ψ quartile starvation table: Q1 (low-ψ, solitary) vs Q4 (high-ψ, social)
  should show est_starv Q4 < Q1 if the pool benefit is operating correctly.

If ψ quartile distribution is still flat after redesign: note as a flag for
Stage 5 (ψ may require agent-level co-evolution). Do not block the seasonal
sweep on this — report it and proceed.

---

## 4. Task 3 — Si carrying costs + Si pool toggle

Two sub-tasks, independent of each other. Run in order.

### 4.1 Si carrying costs (k_carry)

Add a per-agent wealth penalty to Si's CostModel when individual wealth exceeds
`k_carry` × metabolism. This is distinct from C's population-level birth ceiling:
Si's k_carry operates at the individual level, discouraging hoarding and
encouraging fission/dormancy as a wealth-management strategy.

```python
# In Si CostModel.step_cost():
if agent.wealth > k_carry * agent.metabolism:
    carrying_cost = phi_carry * (agent.wealth - k_carry * agent.metabolism)
    agent.wealth -= carrying_cost
```

Config (Si only):
```yaml
cost_model:
  k_carry: 10.0       # wealth ceiling in units of metabolism; default 10
  phi_carry: 0.02     # penalty rate per unit excess wealth; default 0.02
```

`k_carry: null` (default) disables the mechanic — all prior Si configs unaffected.

**Verification:** Run Si static null control with k_carry=10, phi_carry=0.02.
Gate: N_active ∈ [150, 400], dormancy_rate < 20%, perm_deaths ≤ 0.5/step.

If Si gate fails with k_carry active: adjust phi_carry down (0.01) or raise
k_carry (15). Max 3 attempts. If still failing, disable k_carry for Si and
note it — the mechanic is not required for the seasonal sweep.

### 4.2 Si pool toggle

Toggle Si pool ON for the first time (toggle-ready since Stage 4.3 §1.5).

```yaml
# Si configs for pool experiment:
support_pool:
  enabled: true
  tau_pool: 0.05
  rho_carryover: 0.3
```

Run Si static null control with pool enabled. Gate: same as §4.1.

This is a single verification run — no tuning of pool parameters (those are
locked from Stage 4.3 for C; apply the same values to Si). Report N_active,
dormancy_rate, pool diagnostics (contributions/step, draws/step, pool_balance).

If Si pool causes gate failure (N overshoot or dormancy spike): disable Si pool
for the seasonal sweep and note it. The pool toggle is informational at this
stage — it does not gate Task 4.

---

## 5. Task 4 — Seasonal sweep (H1(ii))

### 5.1 Core sweep (8 runs)

Use fully locked Stage 4.5 model: k=4, β_Si=5, p_max_C_final, N_carry,
alpha_carry, τ_pool_final, λ=0.1, ψ redesigned, cluster_init (C only).
Si: p_fission locked, k_carry and pool per Task 3 outcome.

| Run ID | A | T | Agent |
|---|---|---|---|
| 4.5-C-A05-T200 | 0.5 | 200 | C |
| 4.5-Si-A05-T200 | 0.5 | 200 | Si |
| 4.5-C-A075-T200 | 0.75 | 200 | C |
| 4.5-Si-A075-T200 | 0.75 | 200 | Si |
| 4.5-C-A05-T100 | 0.5 | 100 | C |
| 4.5-Si-A05-T100 | 0.5 | 100 | Si |
| 4.5-C-A05-T050 | 0.5 | 50 | C |
| 4.5-Si-A05-T050 | 0.5 | 50 | Si |

### 5.2 Amplitude asymmetry (Q17, +2 runs)

Q17 asked whether a longer trough than peak changes the survival ordering.
Add two asymmetric seasonal runs at the most informative condition (A=0.5,
T=200 — longest period, where trough duration matters most):

```
Asymmetric seasonal: same A=0.5, T=200, but trough occupies 60% of the period
and peak 40% (vs 50/50 for symmetric). Specifically:
  peak_fraction: 0.4    # proportion of period at or above mean
  trough_fraction: 0.6  # proportion of period below mean
```

| Run ID | A | T | Agent | Asymmetry |
|---|---|---|---|---|
| 4.5-C-A05-T200-asym | 0.5 | 200 | C | trough=60% |
| 4.5-Si-A05-T200-asym | 0.5 | 200 | Si | trough=60% |

These two runs are informational — they do not gate H1(ii) assessment. Report
results alongside the symmetric T=200 pair for direct comparison.

### 5.3 T* re-search (C only, conditional)

If C survives at any condition in the core sweep: run binary T* search
(max 3 runs, same protocol as Stage 4.3 Task 4) to bracket the critical
period. Report T* as a range ≤ ±25 steps and compare to Stage 4.3 T*.

If C collapses at all conditions: accept as structural fragility under
current parameter set. Do not re-tune p_max or N_carry to rescue C in
seasonal runs — the null control pass is the standard.

### 5.4 H1(ii) assessment (mandatory, ≥150 words)

Write substantive prose in §4 of the report covering:

- Which agent survives at each (A, T) using N_active for Si and N for C
- Whether the carrying-cost fix changed C's resilience profile relative to
  Stage 4.3 results (compare collapse conditions directly)
- Whether λ=0.1 + ψ redesign visibly affected C trough survival (ψ quartile
  difference during seasonal trough phases)
- Whether Si dormancy rate spikes during troughs — is dormancy the mechanism
  explaining Si advantage, or is Si's resilience margin already set by the
  null control equilibrium?
- Asymmetric seasonal result: does a longer trough change the C/Si ordering,
  and in which direction?
- Clear verdict: H1(ii) supported / null / mixed — with explanation.

"See table" is not acceptable per Standing Rule 10. The assessment must
contain argument, not just summary.

---

## 6. Report format

HTML, single self-contained file:
`outputs/stage45_seed42/report_45.html`

All figures base64-embedded (Standing Rule 13).

### Sections

| § | Content |
|---|---|
| §0 | Stage context: what was blocked, what this stage fixes. One paragraph. |
| §1 | Task 0: carrying-cost mechanic. Sweep table, carry_discount_mean column, N(t) overlay, locked params. |
| §2 | Task 1: pool/λ table (all four conditions, all columns filled). Locked final params stated explicitly. |
| §3 | Task 2: ψ diagnosis (implementation table). ψ redesign test results. Quartile starvation table. |
| §4 | Task 3: Si k_carry and pool. Attempt history. N_active + dormancy diagnostics per condition. |
| §5 | Task 4: full sweep table (10 runs). N(t) overlay. H1(ii) assessment ≥150 words. T* result if found. |
| §6 | Recommended next action: locked parameters for Stage 5, or escalation with specific blocker. |

---

## 7. Coding-agent directives

1. **Implement and test Task 0 mechanic before any runs.** `carry_discount`
   function must have ≥5 unit tests passing before the sweep begins.

2. **Task ordering is strict.** Task 0 gates Task 1. Task 1 gates Tasks 2–4.
   Task 2 and Task 3 may run in parallel (they are independent). Task 4 requires
   Tasks 0–3 complete.

3. **Carry_discount must appear in every C run's parquet.** Add `carry_discount_mean`
   and `p_birth_effective_mean` as logged metrics from Task 0 onward. A run
   without these columns in its parquet is incomplete.

4. **ψ diagnosis is a code read, not a run.** Do not run anything for Task 2
   until the diagnosis is written and confirmed. The code read comes first.

5. **Si pool toggle is config only — no code changes.** If any code change is
   needed to enable the Si pool toggle, that is a bug from Stage 4.3 §1.5.
   Fix the config plumbing before running Si pool experiments.

6. **H1(ii) assessment must be written before the report is closed.** Not a
   placeholder. Not "see table." At least 150 words of substantive argument.

7. **Full test suite after every code change.** Confirm count: should be
   ≥171 after Task 0, ≥173 after Task 2 ψ redesign.

8. **Update ROADMAP.md** at completion. Mark Stage 4.4 and Stage 4.5 complete.
   Add to locked parameters table:
   ```
   N_carry       | Task 0 locked value  | Stage 4.5 | C birth ceiling
   alpha_carry   | Task 0 locked value  | Stage 4.5 | C birth ceiling steepness
   p_max_C       | Task 1 locked value  | Stage 4.5 | Pool+λ condition
   λ             | 0.1                  | Stage 4.5 | C wealth inheritance
   k_carry_Si    | Task 3 locked value  | Stage 4.5 | Si wealth penalty (or disabled)
   ```
   Update Stage 5 entry: multi-seed runs, nD LHS parameter scan, Si Cred activation.

---

## 8. Success criteria

| Criterion | Target |
|---|---|
| `carry_discount` implemented + ≥5 tests pass | Confirmed |
| Full test suite passes after Task 0 | ≥171 green |
| Task 0 sweep complete | All attempts documented with numbers |
| C null control passes (bare) | N ∈ [150, 400], est_starv ≤ 0.78/step |
| `carry_discount_mean` in parquet | (0, 1) at steady state |
| Pool/λ verification complete | All 4 conditions, table fully filled |
| Final locked params stated | p_max_C_final, τ_pool_final, N_carry, alpha_carry |
| ψ diagnosis reported | Implementation table in §3 |
| ψ quartile starvation table | Q1 vs Q4 comparison present |
| Si k_carry verification | Pass or documented failure |
| Si pool toggle | Pass or documented failure |
| Seasonal sweep complete | All 10 runs |
| H1(ii) assessment | ≥150 words, substantive, clear verdict |
| T* reported | Range ≤ ±25 steps, or "C collapsed at all conditions" |
| ROADMAP updated | All locked params added, stages marked complete |
| Reproducibility | seed=42 throughout |

---

## 9. Out of scope

- β sweep {2, 5, 10} → Stage 5.x
- ρ sweep → Stage 5.x
- τ_pool sweep → Stage 5.x
- N_carry or alpha_carry as sweep parameters → Stage 5.x
- Multi-seed ensemble → Stage 5+
- Si Cred economy → Stage 5+
- Inter-pool connectivity → Stage 5+
- c1/c2 behavioral hooks → Stage 4+
- HiveMind → Stage 7+
- Any change to κ, σ_Si, σ_base, δ, α, ε, velocity_tau, f_C, β_status,
  σ_inherit, or parent_radius

---

*End of Stage 4.5 Blueprint*
