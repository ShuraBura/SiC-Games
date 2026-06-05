# SiC Games — Stage 4.2 Blueprint: Seasonal Sweep + Cred-Modulated Birth

**Version:** 1.0
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 4.2 only. Four sequential tasks; each gates the next.
**Prerequisite:** Stage 4.1c complete and patched. Locked values:
C static p_max=0.065, Si static p_fission_max=0.28,
C seasonal p_max=0.075 (collapsed — deferred), Si seasonal p_fission_max=0.35.

---

## 0. North Star (read first, every session)

**Stage 4.2 goal:** two things in sequence.

First, fix the two unresolved findings from Stage 4.1c before any new
scientific runs: (1) established starvation FAIL (τ_pool over-draining adults),
and (2) Cred pool contribution = 0.0 (Cred-scaling of pool contributions not
activating — possible bug or structural zero).

Second, with the fixed model, activate Cred-modulated birth (γ) and run the
seasonal amplitude × period sweep that is the main scientific output of this
stage. This sweep is the first proper test of H1(ii): do C and Si civilizations
respond differently to environmental volatility?

**What Stage 4.2 is not.** No wealth inheritance (λ > 0) — deferred to Stage
4.3. No Si Cred. No inter-pool connectivity. No new agent mechanics beyond γ.

**Carry-forward findings from 4.1c (must address before sweep):**
- Established starvation: 2.28/step C, 2.24/step Si vs threshold 0.78/0.78.
  τ_pool = 0.10 is too aggressive. Recalibration required.
- Cred pool contribution = 0.0: C agents contributed zero above-base
  pool wealth throughout 1000 steps. Root cause unknown — diagnose first.
- C seasonal Allee bistability: deferred from 4.1c. γ may help by suppressing
  birth at peaks (reducing N at trough entry). Test after γ is active.
- Si seasonal pool unmet 22.3%: flagged. Monitor after τ_pool change.

---

## 1. Task 0 — Diagnose Cred pool contribution = 0.0

**No simulation runs. Parquet read only.**

From `outputs/stage41c_c_static_seed42/metrics.parquet` and
`outputs/stage41c_c_static_seed42/final_state.parquet`, compute:

```python
# Check 1: Cred distribution at steady state
cred_mean   = mean(agent_cred, t≥500)
cred_std    = std(agent_cred, t≥500)
cred_max    = max(agent_cred, t≥500)
frac_above_cstar = mean(agent_cred > C_star, t≥500)  # C* = 10.0

# Check 2: Cred-scaled contribution formula
# contribution_i = tau_pool * surplus_i * (1 + tau_cred * tanh(C_i / C*))
# For C_i << C*, tanh(C_i/C*) ≈ 0 → no above-base contribution
# Threshold: agents with C_i > C* contribute meaningfully above base

# Check 3: Was cred_pool_contribution metric correctly implemented?
# It should = tau_cred_reward * (contribution_above_base) per step
# If formula reads C_i/C* but agents have C_i ~ 0–2, tanh ≈ 0–0.2
# → above-base contribution ≈ tau_cred * 0.2 * surplus = small but nonzero
# → metric should not be exactly 0.0 unless agents have C_i ≈ 0
```

**Expected outcomes and implications:**

| Finding | Implication |
|---|---|
| cred_mean << C* (e.g. < 2.0) | Structural zero — tanh(C/C*) ≈ 0. γ won't have much effect either. Investigate Cred accumulation. |
| cred_mean ≈ C* (e.g. 8–12) | Code bug in reward pathway. Fix before 4.2 runs. |
| cred_pool_contribution metric always 0 but Cred > 0 | Metric not wired correctly. Fix. |

Report findings in §0 of the Stage 4.2 report before proceeding to Task 1.
If the root cause is a code bug, fix it and re-run the 4.1c null control
diagnostics (C static only) to confirm the fix. Do not re-run all 4.1c runs.

**Why this matters for γ:** Cred-modulated birth
`P_birth × (1 + γ·tanh(𝒞/C***))` will be inert if agents have near-zero
Cred. Fixing or diagnosing Cred accumulation first prevents building on
a broken foundation.

---

## 2. Task 1 — τ_pool recalibration

**Goal:** find τ_pool such that established starvation deaths/step ≤ 130%
of Stage 4.1b baseline (C: ≤ 0.78/step, Si: ≤ 1.17/step) while juvenile
starvation remains < 60%.

**Runs:** C static and Si static null controls only. Seed=42, 1000 steps.

**Starting point:** τ_pool = 0.05 (half of current 0.10). Try in steps:

| Attempt | τ_pool | Est. starvation C | Est. starvation Si | Juv. starvation | Outcome |
|---|---|---|---|---|---|
| 4.1c locked | 0.10 | 2.28/step ⚠ | 2.24/step ⚠ | 0.3% / 0.0% | FAIL criterion 4 |
| Attempt 1 | 0.05 | ? | ? | ? | ? |
| … | … | … | … | … | … |

**Acceptance criteria:** both established starvation thresholds met AND
juvenile starvation still < 60% for both C and Si.

**Constraint:** do not increase τ_pool above 0.10. Do not run more than
4 attempts. If no τ_pool in [0.02, 0.10] satisfies both criteria
simultaneously, flag as a design tension and defer resolution:
accept τ_pool = 0.05 as the working value and document the trade-off.

**N stability check:** changing τ_pool alters adult wealth and may shift
equilibrium N. Check N range (t≥500) after each attempt. If N exits
[150, 400], P_max may need minor adjustment (document any such change).
Accept up to 2 P_max adjustments before flagging as a new design issue.

**Lock:** once τ_pool passes, record the locked value in ROADMAP.md.
All subsequent Stage 4.2 runs use this τ_pool value.

---

## 3. Task 2 — Activate γ (Cred-modulated birth, C only)

**Mechanism:** multiply C birth probability by a Cred-dependent factor:

$$P_{\text{birth},i}^C \leftarrow P_{\text{birth},i}^C \cdot
\left(1 + \gamma \cdot \tanh\!\left(\frac{\mathcal{C}_i}{C^{***}}\right)\right)$$

where $C^{***}$ is the Cred threshold for birth modulation (default $C^{***}=C^*=10.0$
until Q11 is resolved) and $\gamma=0.2$ (default, Q20).

**C only.** Si birth is wealth-threshold only. No γ for Si.

**Purpose:** Turchin elite overproduction. High-Cred C agents reproduce more
aggressively. This creates boom-bust cycles in C not present in Si — a
testable prediction of the C/Si hypothesis.

**Runs:** C static null control only (seed=42, 1000 steps) with γ=0.2 and
the locked τ_pool from Task 1. Verify:
1. N remains in [150, 400] at t≥500
2. Established starvation still ≤ threshold (γ boosts births → more juveniles
   → more pool draw → potential re-stress of adults)
3. Cred distribution — does γ=0.2 create Cred runaway? Check mean_cred growth
   rate after t=500. Accept < 5%/100 steps.

**If N exits [150, 400] with γ active:** reduce P_max by 0.005 and re-run.
Document. Maximum 2 adjustments before flagging.

**Lock:** γ=0.2 as the Stage 4.2 default unless stability checks fail.
If γ must be reduced to maintain stability, document and lock the adjusted value.

**λ decision (explicit hold):** λ (wealth inheritance) remains λ=0 in Stage 4.2.
Adding γ and λ simultaneously would confound the Turchin cycle signal.
λ > 0 is deferred to Stage 4.3.

---

## 4. Task 3 — Seasonal amplitude × period sweep

**This is the primary scientific output of Stage 4.2.**

Using the model locked after Tasks 0–2 (recalibrated τ_pool, γ=0.2 active),
run the seasonal sweep to test H1(ii): C civilizations survive higher-volatility
perturbations better than Si.

### 4.1 Parameter grid

Current baseline: A=0.5, T=200 (Stage 4 locked). New runs:

| Run ID | A | T | Agent type | Config |
|---|---|---|---|---|
| 4.2-C-A05-T200 | 0.5 | 200 | C | baseline (reuse 4.1c C seasonal result if compatible) |
| 4.2-Si-A05-T200 | 0.5 | 200 | Si | baseline (reuse 4.1c Si seasonal result if compatible) |
| 4.2-C-A075-T200 | **0.75** | 200 | C | new |
| 4.2-Si-A075-T200 | **0.75** | 200 | Si | new |
| 4.2-C-A05-T100 | 0.5 | **100** | C | new |
| 4.2-Si-A05-T100 | 0.5 | **100** | Si | new |
| 4.2-C-A05-T050 | 0.5 | **50** | C | new |
| 4.2-Si-A05-T050 | 0.5 | **50** | Si | new |

**Baseline reuse rule:** the 4.1c seasonal runs used different τ_pool and
no γ. They are NOT compatible baselines — re-run A=0.5, T=200 for both
C and Si with the Stage 4.2 locked parameters.

Total new simulation runs: 8.

All runs: seed=42, 1000 steps. All use locked τ_pool and γ=0.2 (C) / γ=0 (Si).

### 4.2 C seasonal Allee check

The 4.1c C seasonal run collapsed at all tested p_max values (Allee bistability).
With γ active, high-Cred agents may sustain birth rates during troughs,
potentially resolving the bistability. Test at p_max = 0.065 (current C static
locked value) first.

If C seasonal still collapses with γ=0.2: try p_max = 0.07 (one step only).
If still collapses: accept bistability as structural and document. C seasonal
runs in the sweep report as collapsed/non-viable — this is a finding, not a failure.

### 4.3 Primary comparison table (H1(ii))

| Metric (t≥500) | C A=0.5 T=200 | Si A=0.5 T=200 | C A=0.75 T=200 | Si A=0.75 T=200 | C A=0.5 T=100 | Si A=0.5 T=100 | C A=0.5 T=50 | Si A=0.5 T=50 |
|---|---|---|---|---|---|---|---|---|
| N mean | ? | ? | ? | ? | ? | ? | ? | ? |
| N range | ? | ? | ? | ? | ? | ? | ? | ? |
| Survived? | ? | ? | ? | ? | ? | ? | ? | ? |
| Juv starvation % | ? | ? | ? | ? | ? | ? | ? | ? |
| Est. starvation/step | ? | ? | ? | ? | ? | ? | ? | ? |
| Pool unmet mean | ? | ? | ? | ? | ? | ? | ? | ? |
| n_mvp_threshold | ? | ? | ? | ? | ? | ? | ? | ? |

**"Survived?"** = N(t) remains in [100, 600] at t=1000. Collapse = N < 10
for > 50 consecutive steps. Overshoot = N > 600 sustained > 100 steps.

### 4.4 H1(ii) assessment criteria

H1(ii): C survives higher-volatility perturbations than Si.

Operationalised: at the highest amplitude (A=0.75) and/or shortest period
(T=50), does C maintain quasi-stationarity while Si collapses (or vice versa)?

Report honestly regardless of direction. If Si outperforms C, that is the
result. Do not tune p_max post-hoc to rescue failing runs — document collapse
as a finding.

---

## 5. Task 4 — ψ_i starvation diagnostic

ψ_i (proximity utility term) is already implemented in C agents. This task
checks whether ψ_i correlates with starvation risk under seasonal stress.

**No new runs.** Use the Task 3 seasonal parquets.

From each seasonal run parquet, compute for t≥500:

```python
# Bin agents by ψ_i quartile at time of death
# Q1 (lowest ψ) vs Q4 (highest ψ): does high ψ protect against starvation
# during trough phases?

psi_starvation_by_quartile = {
    'Q1': starvation_rate(agents where psi < psi_25th_percentile),
    'Q2': starvation_rate(agents where psi_25 ≤ psi < psi_50),
    'Q3': starvation_rate(agents where psi_50 ≤ psi < psi_75),
    'Q4': starvation_rate(agents where psi ≥ psi_75th_percentile),
}
# Compute separately for trough phases and peak phases
```

Report as a table (C and Si seasonal, A=0.5 T=200 run). If ψ has no
discriminating power (flat across quartiles), note it and defer ψ redesign
to Stage 4.3 (Q25 resolution).

---

## 6. New metrics

| Metric | Definition |
|---|---|
| `gamma_birth_boost` | Mean (1 + γ·tanh(𝒞/C***)) across C agents at birth events each step |
| `psi_starvation_q1` to `psi_starvation_q4` | Starvation rate by ψ quartile |
| `seasonal_phase` | 1 = peak phase (sugar > 0.75 × peak), 0 = trough (sugar < 0.25 × peak) |
| `est_starvation_per_step` | deaths_starvation_established / step (from 4.1c patch) |

---

## 7. Runs summary (all Stage 4.2 runs)

| Priority | Task | Run | Notes |
|---|---|---|---|
| 1 | Task 0 | parquet read (no run) | Gate Task 1 |
| 2 | Task 1 | C static, Si static (τ_pool sweep) | Max 4 attempts |
| 3 | Task 2 | C static (γ=0.2 verification) | Gate Task 3 |
| 4 | Task 3 | 8 seasonal runs | Primary output |
| 5 | Task 4 | parquet read from Task 3 | No new runs |

---

## 8. Report format

### §0 Cred diagnosis
Findings from Task 0. Root cause of Cred = 0.0. Fix applied (if any).

### §1 τ_pool recalibration table
Full tuning history. Locked τ_pool value. N stability check result.

### §2 γ activation
Verification run results. Locked γ value. Cred distribution at t≥500.
gamma_birth_boost mean and std.

### §3 Seasonal sweep — primary comparison table
Full 8-run table (§4.3 above). H1(ii) assessment.

### §4 ψ_i starvation diagnostic
Quartile starvation table. Interpretation.

### §5 C seasonal Allee update
Did γ resolve the bistability? Result and implication for Stage 4.3.

### Plots (mandatory, embedded per Standing Rule 11)

```markdown
![N(t) amplitude sweep](figures/n_timeseries_amplitude_sweep.png)
![N(t) period sweep](figures/n_timeseries_period_sweep.png)
![Pool diagnostics — C A=0.5 T=200](figures/pool_diagnostics_c_a05_t200.png)
![Pool diagnostics — Si A=0.5 T=200](figures/pool_diagnostics_si_a05_t200.png)
![Pool diagnostics — C A=0.75 T=200](figures/pool_diagnostics_c_a075_t200.png)
![Pool diagnostics — Si A=0.75 T=200](figures/pool_diagnostics_si_a075_t200.png)
![ψ starvation by quartile](figures/psi_starvation_quartile.png)
![Cred distribution at steady state](figures/cred_distribution_c_static.png)
```

---

## 9. Success criteria

1. **τ_pool recalibrated.** Established starvation ≤ 130% of 4.1b baseline
   (C: ≤ 0.78/step, Si: ≤ 1.17/step) with juvenile starvation still < 60%.

2. **γ active and stable.** C static null control passes N gate [150,400]
   with γ=0.2 and recalibrated τ_pool. No Cred runaway (< 5%/100 steps).

3. **Sweep complete.** All 8 seasonal runs executed and reported. Collapsed
   runs documented as findings.

4. **H1(ii) assessment.** A clear statement on whether C outperforms, matches,
   or underperforms Si under the tested amplitude and period conditions.
   A null result is a valid result — do not suppress it.

5. **ψ_i diagnostic reported.** Quartile table present with interpretation.

6. **Tests pass.** Run full test suite after each code change (τ_pool parameter,
   γ mechanism). 

7. **Reproducibility.** seed=42 throughout.

---

## 10. Coding-agent directives

1. **Task 0 is a gate.** Do not run any simulation until the Cred = 0.0
   diagnosis is complete and reported. If it reveals a code bug, fix it first.

2. **τ_pool is now a locked parameter.** Once Task 1 is complete, add
   τ_pool to the ROADMAP locked parameters table.

3. **γ applies to C birth only.** Never apply γ to Si. Check C/Si distinction
   table before touching ReproductionCoordinator.

4. **C*** defaults to C* = 10.0.** Q11 (C** independent from C*) is still
   deferred. Use C*** = C* = 10.0 for now.

5. **Do not re-run 4.1c parquets** unless Task 0 confirms a code bug
   requiring a one-run diagnostic re-run (C static only).

6. **Baseline reuse rule.** The 4.1c seasonal parquets are not valid
   baselines for Stage 4.2 (different τ_pool, no γ). Re-run A=0.5 T=200
   for both agent types.

7. **H1(ii) is not pre-cooked.** Report whatever the sweep shows. If Si
   outperforms C, that is the result. Do not tune parameters to rescue a
   preferred outcome.

8. **Embed all plots in report.md** (Standing Rule 11). Run
   `generate_figures.py` (or equivalent) after all parquets are written.
   Save figures to `outputs/stage42_seed42/figures/`. Reference every figure
   inline in report.md using relative paths exactly as shown in §8. A report
   without embedded plots is incomplete — do not upload report.md until all
   `![...](...) ` references resolve to existing files.

9. **Update ROADMAP.md** at completion: mark Stage 4.2 complete, record
   locked τ_pool, locked γ, H1(ii) sweep result summary, and update
   Stage 4.3 description with λ as next mechanism. ROADMAP lives at:
   `G:\My Drive\docs\SiC Games\ROADMAP.md`

---

## 11. Deferred

- λ > 0 (wealth inheritance, C only). → Stage 4.3.
- Amplitude asymmetry (Q17: longer trough than peak). → Stage 4.3.
- τ_pool, τ_parent, γ as sweep parameters (nD scan). → Stage 5.x.
- Si Cred economy. → Stage 5+.
- Inter-pool connectivity. → Stage 5+.
- c1/c2 behavioral hooks. → Stage 4+.
- Mobile resources, scheduled shocks. → Stage 4.4+.
