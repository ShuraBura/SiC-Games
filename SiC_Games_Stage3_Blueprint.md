# SiC Games — Stage 3 Blueprint

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 3 only. Stages 1 and 2 are complete and locked — do not refactor them.
**Prerequisite:** Stage 2.2 κ sweep complete. Confirmed parameters: κ=2.0, σ_Si=1.051.

---

## 0. North Star (read first, every session)

**Stage 3 goal:** the honest comparison. Replace the greedy-Si baseline with a
*bounded-rational Si* whose decision temperature is variance-matched to C's mean
decision entropy at quasi-steady-state. This is the comparison the project is built
around: status-coupled noise (C) vs equivalent-total-variance uniform noise (Si),
on identical worlds, with identical substrates.

**What Stage 3 is not.** It is not a new mechanism stage. No new world mechanics,
no new Cred dynamics, no perturbations. The only addition is the BoundedRationalSi
decision strategy and the newborn Cred endowment for C agents. Everything else is
locked from Stage 2.

**The comparison that matters.** Stage 2 compared C against greedy-Si — a strawman
(zero noise vs status-coupled noise). Stage 3 compares C against variance-matched Si.
If C still outperforms Si on niche occupancy and between-run diversity after
variance-matching, the mechanism claim is supported. If the difference disappears,
the null result is confirmed. Both outcomes are valid.

**Scope discipline.** If the coding agent finds itself touching joint_task.py,
world.py, the replacement rule, or the growback logic, **stop and consult the
supervisor.** The only files that change in Stage 3 are: agents/base.py (newborn
Cred), agents/strategies/si_bounded.py (new), config.py (new fields), metrics.py
(new agent-age split), and report.py (updated comparison table).

**Failure modes to watch for:**
- Bounded-Si absorption: σ_Si=1.051 is high. If Si population collapses below 200
  sustained for >100 steps, σ_Si needs recalibration. Halt and report.
- Newborn Cred runaway: if mean_cred drifts upward without bound due to the
  proportional endowment feedback loop, f_C is too high. Diagnostic: mean_cred
  growing >5% per 100 steps at t>500. Halt and report.
- C/Si behavioral collapse: if the two populations produce identical metrics,
  the variance-matching may have over-corrected. Report; do not retune silently.

---

## 1. What changes in Stage 3 (delta from Stage 2)

Stage 2 (patched, κ=2.0) is fully preserved. Stage 3 adds the following:

### 1.1 New decision strategy: BoundedRationalSi

`src/sic_games/agents/strategies/si_bounded.py`

Softmax decision with fixed temperature σ_Si=1.051, no Cred state, no Cred utility
term. Egalitarian joint-task reward partition (already implemented in joint_task.py —
no changes needed there).

The utility function for Si agents:
$$U_{ij}^{(Si)} = \hat{\Delta\mathcal{R}}_{ij}$$

Same normalization and softmax as CarbonDecision, same candidate cell enumeration
(Von Neumann neighborhood within vision). The only difference: fixed temperature,
no Cred term.

$$P(\text{choose cell } j) = \frac{\exp(U_{ij} / \sigma_{\text{Si}})}{\sum_{k \in J_i} \exp(U_{ik} / \sigma_{\text{Si}})}$$

where $\sigma_{\text{Si}} = 1.051$ (constant, from Stage 2.2 κ=2.0 calibration).

### 1.2 Newborn Cred endowment (C agents only)

**Motivation:** Stage 2.2 revealed that Q1 starvation (lowest Cred) dominates the
starvation excess, driven by replacement agents entering at Cred=0 into a competitive
environment. The endowment gives newborns baseline social capital — "basic dignity,"
the goodwill a community extends to any new member before they've earned status.

**Mechanism:** at birth, C agents receive:
$$\mathcal{C}_i(0) = f_C \cdot \overline{\mathcal{C}}(t)$$

where $\overline{\mathcal{C}}(t)$ is the current population mean Cred at the step of
birth, and $f_C \in [0, 1]$ is the endowment fraction. Default $f_C = 0.1$.

**Proportional, not fixed.** The endowment scales with the world's current status
distribution — in a high-Cred world, newborns enter with more; in a depleted world,
less. This prevents the endowment from becoming negligible or outsized over long runs.

**Si newborns:** Si agents carry the `cred` field (BaseAgent symmetry) but their
newborn Cred endowment is deferred to Stage 5+ when mixed populations are introduced.
Si newborns continue to spawn at cred=0.0. The distinction encodes that Si agents
are not participants in the C status economy, and the community sponsorship C newborns
receive does not extend to Si agents.

**Config parameter:** `f_C` is added to the `carbon:` block. Setting f_C=0.0
recovers Stage 2 behavior exactly, allowing clean before/after comparison.

### 1.3 New metrics: agent-age split on starvation

Stage 2.2 revealed that Q1 starvation is dominated by newly spawned agents. To
verify this and track the newborn Cred endowment's effect, add a starvation split
by agent age:

| Metric | Definition |
|---|---|
| `deaths_starvation_newborn` | starvation deaths among agents with age < 20 |
| `deaths_starvation_established` | starvation deaths among agents with age ≥ 20 |

Age 20 is an arbitrary but reasonable cutoff — roughly 20-33% of minimum lifespan
(τ_min=60). Adjust if the data shows the newborn window is longer or shorter.

---

## 2. Math specification (Stage 3 additions)

### 2.1 BoundedRationalSi decision

Identical to CarbonDecision except:

1. Temperature is fixed: σ = σ_Si = 1.051 (from config, not computed from Cred).
2. Utility has no Cred term: $U_{ij} = \hat{\Delta\mathcal{R}}_{ij}$ only.
3. w_C = 0 always (velocity modulation does not apply — Si has no Cred utility).
4. wealth_velocity is still tracked (BaseAgent field) but unused in decision.

The softmax, normalization, and candidate enumeration are identical to CarbonDecision.
This is deliberate — the only difference between C and Si is the temperature source
and the utility function. Code reuse is appropriate here; consider a shared softmax
utility base class.

### 2.2 Newborn Cred endowment

Applied in the replacement rule R, at agent spawn:

```python
if strategy == "carbon":
    mean_cred = world.mean_cred()   # population mean at this step
    agent.cred = config.carbon.f_C * mean_cred
else:
    agent.cred = 0.0
```

`world.mean_cred()` is a cheap O(N) call over living agents. If mean_cred=0 (early
in the run before any Cred has accumulated), newborns still start at 0 — correct
behavior.

### 2.3 Scheduling (unchanged from Stage 2)

No changes to step order. The newborn Cred is applied at spawn time within step R.

---

## 3. Configuration

### 3.1 New config file: `configs/stage3_si_bounded_seed42.yaml`

```yaml
seed: 42
world:
  grid_size: [50, 50]
  toroidal: true
  sugar_peaks: [[10, 40], [40, 10]]
  max_sugar_capacity: 4
  band_width_k: 6
  growth_rate_alpha: 1
agents:
  initial_population: 250
  vision_dist: [1, 6]
  metabolic_rate_dist: [1, 4]
  max_age_dist: [60, 100]
  initial_wealth_dist: [5, 25]
  phi_mean: 0.5
  phi_std: 0.2
decision:
  strategy: "si_bounded"
si_bounded:
  sigma_si: 1.051          # fixed temperature — calibrated from Stage 2.2 κ=2.0
joint_task:
  distance_d: 1
  capacity_threshold: 4
run:
  n_steps: 1000
  metrics_every: 1
  output_dir: "outputs/stage3_si_bounded_seed42"
  si_reference_dir: "outputs/stage1_baseline_seed42"
visualization:
  animate: true
  frames_per_save: 5
  save_static_plots: true
  agent_color: "blue"
```

### 3.2 Updated C config: `configs/stage3_carbon_seed42.yaml`

Identical to `stage2_carbon_patched_seed42.yaml` with κ=2.0, plus:

```yaml
carbon:
  # ... all Stage 2 parameters unchanged ...
  kappa: 2.0
  f_C: 0.1                 # newborn Cred endowment fraction
run:
  output_dir: "outputs/stage3_carbon_seed42"
  si_reference_dir: "outputs/stage3_si_bounded_seed42"
visualization:
  agent_color: "orange"
```

### 3.3 Parameter locked from Stage 2 (do not change)

| Parameter | Value | Source |
|---|---|---|
| κ | 2.0 | Stage 2.2 κ sweep |
| σ_Si | 1.051 | Stage 2.2 κ=2.0 mean_sigma |
| σ_base | 0.5 | Stage 2 default |
| C* | 10.0 | Stage 2 default |
| δ | 0.01 | Stage 2 default |
| α | 1.5 | Stage 2 default |
| velocity_tau | 10 | Stage 2.1 patch |
| velocity_scale | 1.0 | Stage 2.1 patch |

---

## 4. Module structure (additions only)

```
src/sic_games/
└── agents/
    └── strategies/
        └── si_bounded.py     # NEW: BoundedRationalSi
tests/
└── test_si_bounded.py        # NEW
configs/
├── stage3_si_bounded_seed42.yaml  # NEW
└── stage3_carbon_seed42.yaml      # NEW
```

Everything else unchanged from Stage 2.

---

## 5. Runs to execute

Three runs, in this order:

| Run | Config | Purpose |
|---|---|---|
| 1 | `stage3_si_bounded_seed42.yaml` | Bounded-rational Si baseline |
| 2 | `stage3_carbon_seed42.yaml` (f_C=0.0) | C without newborn endowment — isolates endowment effect |
| 3 | `stage3_carbon_seed42.yaml` (f_C=0.1) | C with newborn endowment — canonical Stage 3 C |

Run 2 exists to isolate the endowment effect: comparing Run 2 vs Run 3 shows exactly
what f_C=0.1 does to starvation and Cred dynamics, independently of the Si comparison.

**Output directories:**
- `outputs/stage3_si_bounded_seed42/`
- `outputs/stage3_carbon_no_endowment_seed42/`
- `outputs/stage3_carbon_seed42/`

**Critical:** do not overwrite any Stage 2 output directories. All Stage 3 runs write
to new directories. Confirmed baselines are read-only. (See BUGS.md BUG-001.)

---

## 6. Metrics and report

### 6.1 Primary comparison table (Stage 3 report)

The report must include a four-way comparison table:

| Metric (final 100 steps) | Stage 1 Si (greedy) | Stage 2 C (κ=2.0) | Stage 3 Si (bounded) | Stage 3 C (f_C=0.1) |
|---|---|---|---|---|
| Mean wealth | 52.3 | 42.0† | ? | ? |
| Gini wealth | 0.47 | 0.47† | ? | ? |
| Spatial dispersion | 15.5 | 18.1† | ? | ? |
| Deaths/step (starvation) | 1.8 | 2.9† | ? | ? |
| Deaths/step (newborn) | — | — | ? | ? |
| Deaths/step (established) | — | — | ? | ? |
| Mean sigma | — | 0.936† | 1.051 (fixed) | ? |
| Mean Cred | — | 6.923† | — | ? |
| Gini Cred | — | 0.871† | — | ? |
| Joint tasks/step | — | 30.41† | ? | ? |

† hardcoded from confirmed Stage 2 pre-patch baseline (see BUGS.md BUG-001).

### 6.2 Starvation quartile table

Repeat the Cred quartile starvation table from Stage 2.2 for both Stage 3 runs.
The key question: does the newborn endowment (f_C=0.1) reduce Q1 starvation
specifically, while leaving Q3/Q4 starvation unchanged?

| Cred quartile | Stage 2 C (ref) | Stage 3 C (f_C=0.0) | Stage 3 C (f_C=0.1) | Stage 3 Si |
|---|---|---|---|---|
| Q1 (lowest Cred) | 2.129 | ? | ? | ? |
| Q2 | 0.005 | ? | ? | ? |
| Q3 | 0.426 | ? | ? | ? |
| Q4 (highest Cred) | 0.288 | ? | ? | ? |

### 6.3 New plots

- Newborn vs established starvation over time (both C and Si)
- Newborn Cred endowment over time (mean endowment received at birth each step)
- Four-way overlay: mean_sigma for greedy-Si / bounded-Si / C (κ=2.0)

---

## 7. Success criteria

1. **Bounded-Si stability.** N(t) stays in [200, 300] for all 1000 steps. σ_Si=1.051
   is high — population collapse is a real risk. This is the first check.

2. **σ_Si is actually 1.051.** Verify in the metrics that mean_sigma for the Si run
   equals 1.051 ± 0.001 at every step (it's fixed, so this should be exact).

3. **Newborn endowment reduces Q1 starvation.** Comparing Run 2 (f_C=0.0) vs Run 3
   (f_C=0.1): deaths_starvation_newborn should decrease. If Q1 starvation is
   unchanged, the endowment is not reaching newborns — investigate the spawn logic.

4. **No newborn Cred runaway.** mean_cred in Run 3 should reach quasi-steady-state
   (std over last 100 steps < 0.1). If it's still trending upward at t=1000, f_C
   is creating a feedback loop — halt and report.

5. **Tests pass.** Minimum:
   - `test_si_bounded`: verify σ is exactly σ_Si for all agents regardless of Cred;
     verify utility has no Cred term; verify softmax probabilities match analytic
     calculation for a 3-cell constructed example.
   - `test_newborn_endowment`: verify spawned C agent receives f_C * mean_cred at
     birth; verify Si agent spawns at cred=0.0 regardless of f_C config.

6. **Reproducibility.** All three runs reproduce exactly on same seed.

---

## 8. Coding-agent directives

1. **Re-read BUGS.md BUG-001 before touching any output directory.** Confirmed
   baseline parquets are read-only. New runs write to new directories only.
2. **Implement BoundedRationalSi by extending or sharing code with CarbonDecision,**
   not by copying it. The softmax and normalization logic should not be duplicated.
   Consider a shared `SoftmaxDecision` base class with temperature and utility
   function as overridable parameters.
3. **Run the three runs in order** (Si bounded → C no endowment → C with endowment).
   Do not run them in parallel — confirm Si bounded stability before investing in
   the C runs.
4. **The f_C=0.0 run is mandatory.** Do not skip it. It's the control that isolates
   the endowment effect from everything else.
5. **Random seeds.** All stochastic calls use seeded RNG. `world.mean_cred()` is
   deterministic — no RNG involved. The endowment assignment is deterministic given
   the world state at spawn time.
6. **Log the σ_Si calibration rationale in LITERATURE.md.** Note that σ_Si=1.051
   is the population-mean decision temperature of C at quasi-steady-state with κ=2.0,
   seed=42. It is an empirical calibration, not a derived quantity.

---

## 9. Open questions (for the supervisor)

| Q | Topic | Status |
|---|---|---|
| Q7 | Variance-matching protocol | **Resolved.** σ_Si=1.051 from Stage 2.2 κ=2.0 mean_sigma. |
| Q8 | f_C value | **Exploratory default.** f_C=0.1 is the starting point. Revisit after Stage 3 if newborn starvation is still dominant. |
| Q9 | Si newborn Cred endowment | **Deferred to Stage 5+** when mixed populations are introduced. Si newborns spawn at cred=0.0 in Stage 3. |
| Q10 | Age cutoff for newborn/established split | **TBD from data.** Age=20 is the default. If the quartile table shows Q1 starvation persists beyond age 20, raise the cutoff. |

---

## 10. Deferred

- Mixed C+Si populations. → Stage 5+.
- Si newborn Cred endowment and f_Si parameter. → Stage 5+.
- Environmental perturbations. → Stage 4.
- Multi-world batch runs. → Stage 5.
- Statistical testing of H1 (effect sizes, power). → Stage 6.
- Evolution / heuristic drift of φ_i. → Stage 7+.
- Status amplification: w_C^(i)(t) = φ_i · f(𝒞_i(t)). → Stage 3+ refinement,
  evaluate after Stage 3 results.
