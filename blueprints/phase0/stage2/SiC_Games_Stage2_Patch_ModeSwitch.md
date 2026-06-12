# SiC Games — Stage 2 Patch: Behavioral Statistics Mode Switch

**Version:** 2.1
**Applies to:** Stage 2 codebase, after confirmed baseline run (seed=42, Gini=0.47).
**Scope:** Single mechanism addition. No other changes.

---

## 0. Motivation

Stage 2 baseline showed C agents starving 63% more than Si (2.9 vs 1.8 deaths/step).
Diagnosis: high-Cred agents are locked into high-σ behavior with no adaptive recourse.
φ_i is a fixed born-trait — it sets a permanent Cred-seeking weight regardless of whether
the agent can afford status-seeking. This conflates *inclination toward Cred* with
*ability to afford Cred-seeking*, producing mechanically enforced starvation.

Fix: φ_i becomes the ceiling on Cred-seeking. Actual Cred-seeking weight is modulated
down when the agent's recent wealth trend is negative. σ-Cred coupling is untouched —
this patch changes *what agents seek*, not *how noisily they decide*.

---

## 1. New agent state

One new scalar per agent, initialized to 0 at birth:

| Field | Type | Init | Description |
|---|---|---|---|
| `wealth_velocity` | float | 0.0 | EMA of recent Δwealth |

Update rule — applied each step, after metabolism and harvest:

$$v_i(t) = \left(1 - \frac{1}{\tau}\right) v_i(t-1) + \frac{1}{\tau} \,\Delta w_i(t)$$

where $\Delta w_i(t) = w_i(t) - w_i(t-1)$ is the net wealth change this step
(harvest minus metabolism), and $\tau$ is the EMA window in steps.

Default $\tau = 10$.

---

## 2. Modified utility weight

The effective Cred-seeking weight replaces the fixed φ_i in the utility function:

$$w_C^{(i)}(t) = \phi_i \cdot \text{sigmoid}\!\left(\frac{v_i(t)}{v_0}\right)$$

where $\text{sigmoid}(x) = 1/(1 + e^{-x})$ and $v_0$ is a velocity scale parameter.

Default $v_0 = 1.0$ (in sugar units per step, i.e., roughly one unit of metabolism).

**Behaviour at limits:**

| Condition | $v_i$ | sigmoid | $w_C^{(i)}$ |
|---|---|---|---|
| Thriving (steady surplus) | $v_i \gg 0$ | → 1 | → $\phi_i$ (full born inclination) |
| Neutral (breaking even) | $v_i = 0$ | = 0.5 | = $\phi_i / 2$ |
| Struggling (net loss) | $v_i \ll 0$ | → 0 | → 0 (pure resource-seeking) |

The full utility function becomes:

$$U_{ij}(t) = \left(1 - w_C^{(i)}(t)\right)\hat{\Delta\mathcal{R}}_{ij} + w_C^{(i)}(t)\,\hat{\Delta\mathcal{C}}_{ij}$$

This replaces the Stage 2 baseline's fixed-weight utility. Everything else in
CarbonDecision (softmax, normalization, σ computation) is unchanged.

---

## 3. What does NOT change

- $\sigma_i^{(C)} = \sigma_{\text{base}} + \kappa \cdot \tanh(\mathcal{C}_i / \mathcal{C}^*)$ — untouched.
  A struggling high-Cred agent still explores noisily; they just redirect that
  exploration toward resources rather than joint tasks.
- Cred accumulation and decay — untouched.
- Joint-task detection and Matthew partition — untouched.
- GreedyMaximizer (Si baseline) — untouched.
- All Stage 1 files — untouched.

---

## 4. New config parameters

Added to the `carbon:` block:

```yaml
carbon:
  # ... existing parameters unchanged ...
  velocity_tau: 10       # τ — EMA window in steps
  velocity_scale: 1.0    # v0 — normalization scale (sugar units/step)
```

---

## 5. New tests

`tests/test_mode_switch.py`:

1. **Velocity EMA:** initialize agent with v=0, apply sequence of Δw values,
   verify v_i(t) matches closed-form EMA to 6 decimal places.

2. **Weight at limits:** verify w_C → φ_i as v → +∞ and w_C → 0 as v → −∞,
   and w_C = φ_i / 2 exactly at v = 0.

3. **Struggling agent becomes resource-seeker:** construct agent with φ=0.8,
   apply 20 steps of negative Δw, verify w_C < 0.1·φ_i (strongly suppressed).

4. **Thriving agent maintains Cred-seeking:** construct agent with φ=0.8,
   apply 20 steps of positive Δw, verify w_C > 0.9·φ_i (near ceiling).

5. **No effect on GreedyMaximizer:** run greedy-Si agent through same
   wealth sequence, verify utility function is unchanged (φ ignored by Si).

---

## 6. Updated report requirements

The Stage 2 patched report (run name: `stage2_carbon_patched_seed42`) must include:

### New diagnostic metric (final 100 steps)
| Metric | Definition |
|---|---|
| `mean_w_C` | mean effective $w_C^{(i)}$ over living agents |
| `mean_velocity` | mean $v_i$ over living agents |
| `frac_suppressed` | fraction of agents with $w_C^{(i)} < 0.1 \cdot \phi_i$ |

### Updated comparison table
| Metric | Stage 1 (Si) | Stage 2 baseline | Stage 2 patched | Δ (patch vs baseline) |
|---|---|---|---|---|
| Mean wealth | 52.3 | 42.0 | ? | ? |
| Deaths/step (starvation) | 1.8 | 2.9 | ? | ? |
| Gini wealth | 0.47 | 0.47 | ? | ? |
| Spatial dispersion | 15.5 | 18.1 | ? | ? |
| Mean sigma | — | 0.936 | ? | ? |
| Gini Cred | — | 0.871 | ? | ? |
| Joint tasks/step | — | 30.41 | ? | ? |
| mean_w_C | — | — | ? | — |
| frac_suppressed | — | — | ? | — |

**The starvation delta is the primary diagnostic.** The target window is:

$$1.8 < \text{deaths/step (starvation)} < 2.9$$

Lower bound (1.8) is the Si rate — reaching it would mean the mode switch is
suppressing Cred-seeking so aggressively that C is behaviourally indistinguishable
from Si. That is a failure mode, not a success. Upper bound (2.9) is the unpatched
C baseline — no improvement at all. Any result inside the window confirms the
release mechanism is functioning while preserving the genuine exploration cost.

If the result stays at 2.9: velocity_tau is too long (agents adapt too slowly) or
velocity_scale v0 is too large (sigmoid stays near 0.5, insufficient suppression).
If the result hits 1.8 or below: v0 is too small or tau too short — the switch is
over-reactive, collapsing C to Si behaviour.

---

## 7. Implementation order

1. Add `wealth_velocity` field to `BaseAgent` with default 0.0.
2. Add velocity update to the agent step (after metabolism, before death check).
3. Add `velocity_tau` and `velocity_scale` to config schema.
4. Modify `CarbonDecision.select_target` to compute `w_C` from velocity before
   building the utility vector.
5. Add `mean_w_C`, `mean_velocity`, `frac_suppressed` to `metrics.py`.
6. Write `test_mode_switch.py`.
7. Run patched config, produce updated report with three-way comparison table.

---

## 8. Deferred

- Evolution / heuristic drift of φ_i across generations. → Stage 7+.
- Cred transfer / gifting between agents. → Stage 7+.
- σ modulation by velocity (currently σ is Cred-only). → Evaluate after Stage 3
  results; only add if Stage 3 comparison is still confounded by starvation excess.
