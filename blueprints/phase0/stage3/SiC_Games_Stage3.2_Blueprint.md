# SiC Games — Stage 3.2 Blueprint: Status Amplification

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 3.2 only. All prior stages locked — do not refactor them.
**Prerequisite:** Stage 3.1 f_C sweep complete. Confirmed parameters: f_C=0.25, κ=2.0, σ_Si=1.051.

---

## 0. North Star (read first, every session)

**Stage 3.2 goal:** add status amplification to the Carbon utility weight. Born-egomaniacs
who accumulate Cred become progressively more status-seeking — success feeds ambition.
Sweep the amplification strength β in a static environment, lock the value, then proceed
to Stage 3.3 with a fully-amplified C agent.

**What Stage 3.2 is not.** It is not a new world mechanic. No changes to joint_task.py,
world.py, growback, or the replacement rule. The only change is to the utility weight
computation in CarbonDecision.

**Scope discipline.** One new parameter (β). One new term in the utility weight formula.
One sweep. If the coding agent finds itself touching anything outside CarbonDecision and
config.py, stop and consult the supervisor.

**Failure modes to watch for:**
- Utility saturation: if β is too high, born-egomaniacs with high Cred assign near-zero
  weight to resources and starve. Diagnostic: deaths_established rising sharply with β,
  concentrated in Q4.
- Cred runaway: amplification drives agents to seek more joint tasks → more Cred →
  more amplification. Diagnostic: mean_cred trending upward >5% per 100 steps at t>500.
- Behavioral collapse: if amplification is so strong that all high-φ agents converge to
  pure status-seeking, population diversity collapses. Diagnostic: std(w_C) → 0.

---

## 1. What changes in Stage 3.2 (delta from Stage 3.1)

One addition only: the status amplification term in the Carbon utility weight.

### 1.1 Modified utility weight

The effective Cred-seeking weight becomes:

$$w_C^{(i)}(t) = \phi_i \cdot \underbrace{\left(1 + \beta \cdot \tanh\!\left(\frac{\mathcal{C}_i}{\mathcal{C}^{**}}\right)\right)}_{\text{status amplification}} \cdot \underbrace{\text{sigmoid}\!\left(\frac{v_i}{v_0}\right)}_{\text{stress suppression}}$$

where:
- $\phi_i$ — born-trait (fixed at birth, unchanged)
- $\beta$ — amplification ceiling. New parameter. Default 1.0.
- $\mathcal{C}^{**}$ — Cred scale for amplification. **Pinned to C*=10.0** for Stage 3.2.
- $v_i$ — wealth velocity EMA (unchanged from Stage 2.1)
- $v_0$ — velocity scale (unchanged, 1.0)

**Behaviour at limits:**

| Condition | Amplification term | Stress term | Net w_C |
|---|---|---|---|
| New agent (𝒞=0, v=0) | 1.0 | 0.5 | φ_i / 2 |
| Thriving, low Cred | 1.0 | → 1 | → φ_i |
| Thriving, high Cred | → 1+β | → 1 | → φ_i(1+β) |
| Struggling, high Cred | → 1+β | → 0 | → 0 |

The stress suppression still dominates when agents are struggling — even high-Cred
agents refocus on resources when wealth velocity is negative. Status amplification
only activates when the agent can afford it (thriving). This is the intended interaction:
ambition is a luxury of success.

**Note:** w_C can exceed φ_i when β > 0 and the agent is thriving with high Cred.
The utility normalization (divide by max over candidates) prevents this from breaking
the softmax — only the *relative* weights matter.

### 1.2 New config parameter

Added to the `carbon:` block:

```yaml
carbon:
  # ... all existing parameters unchanged ...
  status_amplification_beta: 1.0   # β — amplification ceiling
  # C** is pinned to cred_scale (C*=10.0) — no new parameter needed
```

### 1.3 New metrics

| Metric | Definition |
|---|---|
| `mean_amplification` | mean of (1 + β·tanh(𝒞_i/C**)) over living agents |
| `std_w_C` | std of effective w_C^(i) over living agents — diversity diagnostic |
| `frac_amplified` | fraction of agents with amplification term > 1.1 (i.e., 𝒞_i > C**·atanh(0.1/β)) |

---

## 2. Sweep

### 2.1 Runs

Four configs, identical to `stage3_carbon_seed42.yaml` (f_C=0.25) except β:

| Run name | β | Note |
|---|---|---|
| `stage32_beta00_seed42` | 0.0 | Recovers Stage 3 behavior — load from parquet |
| `stage32_beta05_seed42` | 0.5 | Mild amplification |
| `stage32_beta10_seed42` | 1.0 | Moderate — default |
| `stage32_beta20_seed42` | 2.0 | Strong amplification |

**Critical:** β=0.0 is identical to Stage 3 canonical C (f_C=0.25). Load metrics from
`outputs/stage3_carbon_seed42/metrics.parquet` — do not re-run.

Seed=42 for all. 1000 steps.

### 2.2 Report format

Single report `outputs/stage32_beta_sweep_seed42/report.md`:

#### Primary comparison table

| Metric (final 100 steps) | β=0.0 | β=0.5 | β=1.0 | β=2.0 |
|---|---|---|---|---|
| Mean wealth | 44.7 | ? | ? | ? |
| Gini wealth | 0.462 | ? | ? | ? |
| Spatial dispersion | 17.8 | ? | ? | ? |
| Deaths/step (starvation) | 2.85 | ? | ? | ? |
| Deaths/step (newborn) | 2.25 | ? | ? | ? |
| Deaths/step (established) | 0.60 | ? | ? | ? |
| Mean Cred | 7.555 | ? | ? | ? |
| Gini Cred | 0.684 | ? | ? | ? |
| Mean sigma | 1.194 | ? | ? | ? |
| Joint tasks/step | 25.93 | ? | ? | ? |
| mean_w_C | 0.287 | ? | ? | ? |
| std_w_C | ? | ? | ? | ? |
| mean_amplification | 1.000 | ? | ? | ? |
| frac_amplified | 0.000 | ? | ? | ? |

#### Starvation by Cred quartile

| Cred quartile | β=0.0 | β=0.5 | β=1.0 | β=2.0 |
|---|---|---|---|---|
| Q1 (lowest Cred) | 0.796 | ? | ? | ? |
| Q2 | 0.902 | ? | ? | ? |
| Q3 | 1.116 | ? | ? | ? |
| Q4 (highest Cred) | 0.310 | ? | ? | ? |

**Watch:** if Q4 starvation rises sharply with β, high-Cred agents are being driven
into status-seeking at the expense of survival. That is utility saturation — the
amplification is too strong.

#### Overlay plots (all four β values)

- mean_w_C over time
- std_w_C over time (behavioral diversity)
- Deaths/step (established) over time
- Mean Cred over time
- Joint tasks/step over time

### 2.3 β selection guidance (for the supervisor — not pass/fail)

Prefer β where:
1. No Cred runaway (mean_cred growth < 5% per 100 steps after t=500)
2. std_w_C is meaningfully above zero — population retains behavioral diversity
3. Q4 starvation does not exceed Q3 starvation (high-Cred agents are not
   being disproportionately killed by their own ambition in a static world)
4. Established deaths do not rise above β=0.0 baseline (0.60/step) by more
   than 50% — amplification should not be net harmful in a static environment

---

## 3. Module structure (changes only)

```
src/sic_games/
└── agents/
    └── strategies/
        └── carbon.py     # MODIFIED: add amplification term to w_C computation
tests/
└── test_status_amplification.py   # NEW
configs/
└── stage32_beta{05,10,20}_seed42.yaml  # NEW (three configs)
```

---

## 4. Tests

`tests/test_status_amplification.py`:

1. **Amplification at limits:** verify amplification term = 1.0 at 𝒞=0, approaches
   1+β as 𝒞 → ∞, equals 1 + β·tanh(1) at 𝒞=C**.

2. **Stress suppression still dominates:** construct agent with φ=1.0, β=2.0,
   𝒞=50 (saturated amplification), v=-10 (strongly struggling). Verify w_C < 0.1
   (stress suppression wins over amplification).

3. **Thriving high-Cred agent reaches ceiling:** construct agent with φ=0.8,
   β=1.0, 𝒞=50, v=+10. Verify w_C ≈ φ·(1+β) = 0.8·2.0 = 1.6 (capped by
   normalization in softmax, but weight itself is correct).

4. **β=0 recovers Stage 3 behavior:** verify w_C = φ_i · sigmoid(v_i/v_0)
   exactly when β=0, regardless of 𝒞_i.

5. **No effect on BoundedRationalSi:** verify Si utility function is unchanged
   by the new parameter.

---

## 5. Success criteria

1. **Population stable.** N(t) in [200, 300] for all β values throughout 1000 steps.
2. **No Cred runaway** for any β value (growth < 5% per 100 steps after t=500).
3. **Behavioral diversity preserved.** std_w_C > 0.05 at steady state for all β —
   the population is not collapsing to uniform behavior.
4. **Tests pass.**
5. **Reproducibility** confirmed for β=0.5, 1.0, 2.0 runs.

---

## 6. Coding-agent directives

1. **One change only.** The amplification term is added to `CarbonDecision` and
   nowhere else. Do not touch joint_task.py, world.py, metrics beyond the three
   new fields, or any Stage 1/2 files.
2. **Load β=0.0 from parquet.** Do not re-run the Stage 3 canonical C run.
   `outputs/stage3_carbon_seed42/metrics.parquet` is the confirmed baseline.
3. **C** is pinned to C*=10.0.** Do not add a separate config parameter for C**.
   It reads `cred_scale` from the existing carbon config block.
4. **Run in order:** β=0.5 → β=1.0 → β=2.0. Confirm no runaway or collapse at
   each step before proceeding to the next.
5. **Log β rationale in LITERATURE.md.** Note the Roll (1986) hubris hypothesis
   as the empirical basis — high-status decision-makers escalate commitment to
   status-seeking strategies. β is the quantification of that escalation rate.

---

## 7. Deferred

- C** as independent parameter (separate from C*). → Evaluate after Stage 3.2
  results; add only if data suggests σ and utility amplification should saturate
  at different Cred levels.
- β as a born-trait (heterogeneous amplification across agents). → Stage 7+.
- Heuristic drift of φ_i. → Stage 5+.
- Biparental reproduction. → Stage 3.5.
- Mixed populations. → Stage 3.4.
- Environmental perturbations. → Stage 4.
