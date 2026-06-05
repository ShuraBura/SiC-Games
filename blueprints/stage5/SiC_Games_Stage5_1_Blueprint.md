# SiC Games — Stage 5.1 Blueprint: Si Cred Redesign (Near-Dormancy Accumulation)

**Version:** 1.0  
**Intended consumer:** Claude Code  
**Scope:** Si Cred accumulation rule replacement only. No other mechanics change.  
**Prerequisite:** v5.1-postaudit-clean, 201 tests passing.  
**Backup before starting:** `G:\My Drive\docs\SiC Games\Model\v5.1_2026-05-28_0637` (already done per handoff). Create `v5.1.1_pre_sicred_redesign` before touching any code.

---

## 0. North Star

The Stage 5 Si Cred accumulation rule (`Δcred = surplus × r_cred_Si`) was confirmed
pro-cyclical: `si_cred_mean` fell during resource troughs, which is exactly when Si
agents are most stressed and most need elevated `σ_Si_eff`. The redesign replaces the
accumulation trigger with a near-dormancy survival signal. An agent that stays active
while its wealth sits in the band `[k_dormant, k_dormant + k_cred_band] × metabolism_i`
is operating under genuine stress without collapsing — this is the behavioural signature
that should be rewarded with accumulated Cred. The result is a counter-cyclical Cred
signal: during resource troughs, more agents fall into the near-dormancy band, more
Cred accumulates, and `σ_Si_eff` rises, making survivors more explorative precisely
when the environment demands it.

Everything downstream of `si_cred_i` — the σ modulation formula, decay, ceiling,
`κ_Si` — is unchanged. Only the accumulation step changes.

---

## 1. Task 0 — Backup and pre-flight

1. Copy working directory to `v5.1.1_pre_sicred_redesign` before any code changes.
2. Run the full test suite. Confirm **201 tests pass**. Record the count. If it is
   not 201, stop and report — do not proceed with a degraded baseline.
3. Confirm `si_cred.enabled: true` and `si_cred.accumulation_mode: surplus_based`
   in the Si config (or equivalent flag in code) so the starting point is
   unambiguous before replacement.

---

## 2. Task 1 — Accumulation rule replacement

### 2.1 Config schema change

Add `accumulation_mode` and `k_cred_band` to the `si_cred` config block.
Remove `accumulation_rate` (it was only meaningful for the surplus-based rule).
The final Si Cred config block is:

```yaml
si_cred:
  enabled: true
  accumulation_mode: near_dormancy   # replaces surplus_based
  k_cred_band: 1.0                   # band width in units of k_dormant; NEW parameter
  decay: 0.01                        # unchanged
  C_star_Si: 10.0                    # unchanged
  kappa_Si: 0.5                      # unchanged
```

`enabled: false` must still recover Stage 4.5 / Stage 5 behaviour exactly —
`si_cred_i` stays 0 and `σ_Si_eff_i = σ_Si` for all agents.

### 2.2 Accumulation logic

Replace the surplus-based accumulation step with the following.

The near-dormancy band for agent `i` at step `t`:

```
w_lo_i = k_dormant × metabolism_i
w_hi_i = (k_dormant + k_cred_band) × metabolism_i
```

The accumulation increment:

```
in_band_i(t) = 1  if  w_lo_i ≤ wealth_i(t) < w_hi_i  else  0

Δsi_cred_i(t) = in_band_i(t)          # binary: 1 if in band, 0 otherwise

si_cred_i(t)  = clamp(
    si_cred_i(t-1) × (1 - decay) + Δsi_cred_i(t),
    0,
    C_star_Si
)
```

**Implementation notes:**

- `k_dormant` and `metabolism_i` are already available on the agent object —
  no new lookups required.
- `Δsi_cred_i` is intentionally binary (0 or 1). This keeps the accumulation
  rate fixed and independent of how deeply inside the band the agent sits,
  avoiding an implicit wealth-level bias.
- The upper bound of the band is a **strict inequality** (`< w_hi_i`): an agent
  at exactly `(k_dormant + k_cred_band) × metabolism_i` does not receive Cred.
- Apply decay and clamp **after** the increment, not before.

The σ modulation formula is **unchanged**:

```
σ_Si_eff_i(t) = σ_Si + κ_Si × tanh(si_cred_i(t) / C_star_Si)
```

### 2.3 Locate and edit

The accumulation logic lives in the Si agent's step method (likely
`src/sic_games/agents/strategies/si_bounded.py` or equivalent). Find the block
that currently computes `Δsi_cred_i` from surplus and replace it with the
near-dormancy block above. Do not touch any other part of the method.

If `accumulation_mode` is read at runtime (config dispatch), ensure that passing
`accumulation_mode: surplus_based` in a config still routes to the old logic for
test isolation. If a clean switch without backward compatibility is simpler, remove
`surplus_based` entirely and update the tests accordingly; document the choice
explicitly.

---

## 3. Task 2 — Test suite update

### 3.1 Tests to remove or replace

The following Stage 5 tests are now mechanically incorrect. Remove them from
`tests/test_si_cred.py`:

- `test_si_cred_accumulates_on_surplus` — new rule does not accumulate on surplus
- `test_si_cred_stable_on_deficit` — no longer meaningful

### 3.2 New tests (add to `tests/test_si_cred.py`)

```python
def test_si_cred_accumulates_when_in_near_dormancy_band():
    """
    Agent with wealth in [k_dormant, k_dormant + k_cred_band) × metabolism
    receives Δsi_cred = 1 after one step.
    """

def test_si_cred_no_accumulation_below_band():
    """
    Agent with wealth < k_dormant × metabolism (dormant) receives Δsi_cred = 0.
    Dormant agents do not accumulate Cred.
    """

def test_si_cred_no_accumulation_above_band():
    """
    Agent with wealth ≥ (k_dormant + k_cred_band) × metabolism receives
    Δsi_cred = 0. Comfortable agents do not accumulate Cred.
    """

def test_si_cred_upper_band_boundary_exclusive():
    """
    Agent with wealth exactly equal to (k_dormant + k_cred_band) × metabolism
    receives Δsi_cred = 0 (strict upper inequality).
    """

def test_si_cred_decays_outside_band():
    """
    Agent outside the band for N consecutive steps: si_cred decays by
    (1-decay)^N from its initial value. Verify at N=10.
    """

def test_si_cred_clamped_at_C_star():
    """
    Agent in band every step for sufficient steps: si_cred does not exceed
    C_star_Si. Confirm clamp is applied correctly.
    """

def test_si_sigma_eff_increases_with_cred():
    """
    σ_Si_eff_i > σ_Si when si_cred_i > 0. (Carry over from Stage 5 — keep.)
    """

def test_si_cred_disabled_no_effect():
    """
    With enabled=False: si_cred stays 0 and σ_Si_eff = σ_Si for all agents.
    (Carry over from Stage 5 — keep.)
    """
```

Net change: −2 removed, +8 new = **+6 tests**.  
Target after Task 2: **≥ 207 tests passing** (201 − 2 + 8).

Run the full suite after implementing the tests. Confirm the count explicitly.
Do not proceed to Task 3 if the suite is red.

---

## 4. Task 3 — Calibration runs

### 4.1 Run A: Si static null control

**Purpose:** confirm the redesigned Cred does not destabilise the null control
that passed in Stage 5.

**Config:** Si, k=4, β_Si=5, p_fission=0.28, dormancy locked
(k_dormant=1.0, T_dormant_max=50, k_reactivate=3.0), pool ON,
near-dormancy Si Cred enabled (k_cred_band=1.0, decay=0.01, C*_Si=10.0,
κ_Si=0.5). Seed=42, 1000 steps.

**Population gate — must pass before proceeding to Run B:**

| Metric | Target |
|---|---|
| N_active at t ≥ 500 | ∈ [150, 400] |
| dormancy_rate at t ≥ 500 | < 20% |
| perm_deaths/step | ≤ 0.5 |

**Cred diagnostics — report but do not gate on:**

| Metric | Expected direction | Notes |
|---|---|---|
| si_cred_mean (t ≥ 500) | > 0 | Accumulation is firing |
| si_cred_std (t ≥ 500) | > 0 | Variance across agents exists |
| σ_Si_eff_mean (t ≥ 500) | > σ_Si = 1.238 | σ modulation active |
| Gini(si_cred) (t ≥ 500) | > 0.10 | Meaningful inequality |
| frac_agents_in_band (t ≥ 500) | > 0 | Non-zero fraction in band at any step |

**If population gate fails:** reduce κ_Si to 0.2 (one attempt). If still failing:
disable Si Cred, report the failure with full diagnostics, and halt — do not
proceed to Run B. Maximum 2 attempts.

### 4.2 Run B: Counter-cyclicality check at A=0.75, T=200

**Purpose:** this is the specific check that Stage 5 failed. The near-dormancy
rule must produce a Cred signal that *rises* during troughs, not falls.

**Config:** Si with near-dormancy Cred enabled (same as Run A), A=0.75, T=200.
Seeds: 42 and 43. CRN=True, paired with Stage 5 C runs at same conditions.
1500 steps (≥ 7 full periods at T=200).

**Counter-cyclicality gate:**

Compute `si_cred_mean(t)` averaged over each trough phase (resource amplitude
below 50% of peak) versus each peak phase (resource amplitude above 50% of peak):

```
mean(si_cred_mean during troughs) > mean(si_cred_mean during peaks)
```

This must hold for **both seeds**. A single-seed pass is not sufficient.

**Additional metrics — report but do not gate on:**

- `σ_Si_eff_mean` during troughs vs peaks (expected: higher during troughs)
- `N_active` trajectory (does Cred elevation during troughs visibly extend survival?)
- Whether Si survives to t=1500 (note outcome; do not draw H1(ii) conclusions
  from 2 seeds)

**If the gate fails at k_cred_band=1.0:** set `k_cred_band: 1.5` and repeat
Run B once. This is the **only permitted tuning decision**. If the gate still
fails at k_cred_band=1.5, report the failure in full, lock k_cred_band=1.0,
disable Si Cred, and halt. Do not attempt further tuning without supervisor
approval.

**If the gate passes at k_cred_band=1.0:** lock `k_cred_band=1.0` and proceed.  
**If the gate passes only at k_cred_band=1.5:** lock `k_cred_band=1.5` and note
the single-step tuning in the report.

---

## 5. Report format

`outputs/stage51_sicred_redesign/report.html` — single self-contained HTML file,
all figures embedded as base64 `<img>` tags.

| § | Content |
|---|---|
| §1 | Pre-flight: baseline test count (must be 201), backup confirmation. |
| §2 | Implementation summary: what changed (accumulation rule), what did not (decay, ceiling, σ formula, κ_Si). One paragraph. |
| §3 | Test suite: count after Task 2 (must be ≥ 207). List removed and added tests by name. |
| §4 | Run A — null control: population gate pass/fail table. Cred diagnostics table. Time-series plot of N_active, si_cred_mean, σ_Si_eff_mean, and frac_agents_in_band over 1000 steps. |
| §5 | Run B — counter-cyclicality: gate result (pass/fail) stated explicitly for each seed. Time-series plot of si_cred_mean overlaid with resource amplitude cycle, both seeds on same axes. Table: si_cred_mean during troughs vs peaks, per seed. Final k_cred_band value locked. N_active trajectory for both seeds. |
| §6 | Locked parameter update: final locked value k_cred_band=[value], accumulation_mode=near_dormancy. Confirm all other Si Cred parameters unchanged. |
| §7 | What was not changed: one short paragraph confirming H1(ii) findings, Si T* bracket, and all Stage 4/5 locked parameters are unaffected by this change. |

---

## 6. Stopping rules

| Condition | Action |
|---|---|
| 201 tests do not pass at Task 0 | Stop. Report. Do not proceed. |
| Test suite not ≥ 207 after Task 2 | Stop. Debug tests. Do not run simulations. |
| Run A population gate fails after 2 attempts | Disable Si Cred. Report. Halt. |
| Run B gate fails at both k_cred_band=1.0 and 1.5 | Lock k_cred_band=1.0. Disable Si Cred. Report. Halt. |
| Run B passes only at k_cred_band=1.5 | Lock k_cred_band=1.5. Note in report. Proceed. |

---

## 7. ROADMAP update

At completion, update `G:\My Drive\docs\SiC Games\ROADMAP.md`:

- Mark Stage 5.1 (Si Cred redesign) complete.
- Lock `k_cred_band` at its final value (1.0 or 1.5).
- Update Si Cred status: "near-dormancy accumulation, counter-cyclical gate [passed/failed]."
- Add note: `accumulation_rate` (r_cred_Si) parameter retired; replaced by binary
  near-dormancy trigger.
- Update Stage 5.2 entry as next task.

---

## 8. Locked parameters unchanged

All of the following carry over from v5.1-postaudit-clean without modification:

| Parameter | Value |
|---|---|
| k_grid | 4 |
| σ_Si | 1.238 |
| β_Si | 5.0 |
| κ (Cred-σ, C) | 2.0 |
| p_fission_Si | 0.28 |
| α (Matthew) | 2.0 |
| p_max_C | 0.12 |
| β (status) | 1.0 |
| N_carry | 400 |
| f_C | 0.25 |
| α_carry | 1.0 |
| σ_inherit | 0.05 |
| τ_pool | 0.05 |
| age_init_upper_frac | 0.25 |
| ρ | 0.3 |
| wealth_init_scale_k | True |
| λ | 0.1 |
| cluster_init (C only) | peak_index=0, r=10 |
| T_dormant_max | 50 |
| k_density | 10 |
| k_dormant | 1.0 |
| k_moran | 10 |
| τ_trickle | 0.05 |
| r_cred_Si | retired — replaced by binary near-dormancy trigger |
| k_reactivate | 3.0 |
| κ_Si | 0.5 |
| decay (Si Cred) | 0.01 |
| C_star_Si | 10.0 |

---

## 9. Out of scope

- Any change to C mechanics, C Cred, joint tasks, pool, or inheritance.
- Any change to σ_Si, κ_Si, decay, C*_Si, or the σ modulation formula.
- Any H1(ii) re-analysis or new sweep runs.
- Stage 5.2 cultural dynamics (c2 hook, Deffuant, σ_inherit sweep).
- σ_inherit redesign.
- Terrain topography.
- LHS parameter scan.

---

*End of Stage 5.1 Blueprint*
