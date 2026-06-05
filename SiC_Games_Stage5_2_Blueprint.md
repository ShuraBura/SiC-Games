# SiC Games — Stage 5.2 Blueprint: Cultural Dynamics

**Version:** 1.0
**Intended consumer:** Claude Code
**Scope:** Three cultural-transmission mechanics for C — c2 joint-task defection,
Deffuant horizontal updating with c1 resistance, and a σ_inherit sweep to address
the ψ homogenisation null. C only; Si trait vector carries c1/c2/ψ but no hooks fire.
**Prerequisite:** v5.1.1 post-Stage-5.1, 207 tests passing, `k_cred_band=1.0` locked.
**Backup before starting:** create `v5.1.2_pre_cultural` before any code changes.
**Reporting:** all reporting in this stage follows the CLAUDE.md Report Standards
(R1–R7). Terminal-state rows (R1) are mandatory in every results table even though
extinction is not expected in most runs here.

---

## 0. North Star

Stage 5.2 activates the cultural layer of the C civilisation. Three mechanics,
implemented and gated independently and in order:

1. **c2 defection hook** makes joint-task cooperation defectible. A high-c2 agent
   abandons a joint task when acting alone would out-earn its Matthew share. This
   introduces free-riding as a genuine possibility (previously cooperation was
   unconditional), which the evolutionary-game-theory lens requires for the pool
   to be a credible collective-action model.

2. **Deffuant updating + c1** adds horizontal (prestige-weighted) cultural
   transmission: C agents move their cultural traits toward similar neighbours
   within a confidence bound, copying higher-Cred neighbours more strongly. c1
   scales resistance to being copied-toward.

3. **σ_inherit sweep** addresses the Stage 5 ψ null (Gini collapsed 0.25→0.09 in
   500 steps under σ_inherit=0.05 + biparental averaging). The sweep tests whether
   higher inheritance variance sustains ψ diversity. **Critical design point:**
   Deffuant is itself a homogenising force, so the sweep isolates the genetic
   channel (Deffuant OFF) before measuring the interaction (Deffuant ON).

Tasks 1 and 2 are gated independently. Task 3 depends on Task 2 being wired
(for the Deffuant-ON interaction cell) but tests the genetic channel first.

---

## 1. Task 0 — Backup and pre-flight

1. Copy working directory to `v5.1.2_pre_cultural`.
2. Run full test suite. Confirm **207 tests pass**. Record the count. If not 207,
   stop and report — do not proceed on a degraded baseline.
3. Confirm `seasonal_phase` metric (Stage 4.2) and the R6 terminal-state fields
   (`extinction_step`, `N_min`, `argmin_t N_active`, `N_active_t_end`) are emitted
   for all runs. If `extinction_step` / `N_min` are not yet emitted, **add them as
   the first sub-task** (this is the tracking fix from the Stage 5.1 review) and
   add one test confirming `extinction_step` is null for a surviving run and equals
   the first zero-population step for a forced-extinction fixture.

---

## 2. Task 1 — c2 joint-task defection hook (C only)

### 2.1 Config

```yaml
c2_defection:
  enabled: true        # false => bit-identical to Stage 5.1 (no defection)
```

c2_i ∈ [0,1] is already carried and inherited. No new scalar parameters; c2_i is
used directly as the defection probability (see 2.2).

### 2.2 Logic

For a C agent engaged in / offered a joint task at step `t`:

```
matthew_share = agent's share of joint output under the Matthew partition (α=2.0)
solo_harvest  = harvest the agent would obtain acting alone on its current cell

if solo_harvest > matthew_share:
    p_defect_i = c2_i
else:
    p_defect_i = 0.0          # no incentive to defect; cooperation dominates

draw u ~ agent_rng.uniform(0,1)
if u < p_defect_i:
    agent defects: leaves the joint task and harvests solo this step
else:
    agent cooperates as before
```

Notes:
- C only. Si has no joint tasks; the hook never fires for Si even with the trait present.
- Use `agent_rng` (CRN split), not `env_rng`, so seasonal environment streams are unaffected.
- Defection is a per-step decision; it does not permanently dissolve the partnership.

### 2.3 Equivalence gate

With `enabled: false` (or all c2_i forced to 0), the run must be **bit-identical**
to the Stage 5.1 baseline: identical N(t), identical wealth/Gini/Cred series,
`max_reldiff = 0`. This is the gate; report it explicitly.

### 2.4 Tests (add to `tests/test_c2_defection.py`)

```python
def test_c2_no_defection_when_share_exceeds_solo():
    """solo_harvest <= matthew_share => p_defect = 0 regardless of c2."""

def test_c2_defection_probability_equals_c2_when_incentive():
    """solo_harvest > matthew_share => p_defect == c2_i (statistical, fixed seed)."""

def test_c2_high_agent_defects_more_than_low(): ...
def test_c2_disabled_bit_identical_to_baseline(): ...
def test_c2_never_fires_for_si(): ...
```

### 2.5 New metrics
`defection_rate` (defections / joint-task opportunities per step), mean c2 of
defectors vs cooperators, joint-task participation rate.

### 2.6 Verification run
C static null control with c2 active. Gate: N_active ∈ [150,400] at t≥500,
established starvation within Stage 5 bounds. Report `defection_rate` at steady
state and confirm population stability is not destroyed by defection.

---

## 3. Task 2 — Deffuant updating + c1 resistance (C only)

### 3.1 Config (proposed values — confirm or override)

```yaml
deffuant:
  enabled: true
  epsilon: 0.2          # confidence bound; copy only if |trait_self - trait_nbr| < epsilon
  mu: 0.3               # base convergence rate
  update_every: 1       # steps between updates (raise to throttle cost)
  traits: [c1, c2, psi] # cultural traits subject to horizontal transmission
  cred_weight: relative # prestige bias form (see 3.2)
```

### 3.2 Logic

Each `update_every` steps, each active C agent `i` selects one C neighbour `j`
within the interaction radius (use the existing neighbour lookup; if none, skip).
For each trait `T` in `traits`:

```
if |T_i - T_j| < epsilon:
    w = prestige_weight(cred_i, cred_j)          # see below
    mu_eff = mu * (1 - c1_i)                      # c1 scales resistance to copying-toward
    T_i += mu_eff * w * (T_j - T_i)
    clamp T_i to [0, 1]
```

Prestige weight (`cred_weight: relative`):
```
w = cred_j / (cred_i + cred_j + eps_div)          # higher-Cred neighbours pull harder
```
(eps_div small constant to avoid div-by-zero when both Creds are 0.)

Notes:
- C only.
- c1_i ∈ [0,1]: c1_i = 1 means total resistance (mu_eff = 0, agent never moves).
- Updating ψ here is intentional and is the homogenising force tested against in Task 3.
- Use `agent_rng` for neighbour selection.

### 3.3 Equivalence gates
- `enabled: false` => bit-identical to Task 1 state (`max_reldiff = 0`).
- `mu: 0` => bit-identical (no movement).
- `epsilon: 0` => bit-identical (no neighbour ever within bound).
Report all three.

### 3.4 Tests (add to `tests/test_deffuant.py`)

```python
def test_deffuant_no_update_outside_confidence_bound(): ...
def test_deffuant_moves_toward_neighbour_within_bound(): ...
def test_deffuant_c1_one_blocks_all_updates():
    """c1_i = 1 => agent never changes any trait."""
def test_deffuant_prestige_higher_cred_neighbour_pulls_harder(): ...
def test_deffuant_clamped_to_unit_interval(): ...
def test_deffuant_disabled_bit_identical(): ...
def test_deffuant_mu_zero_bit_identical(): ...
def test_deffuant_never_fires_for_si(): ...
```

### 3.5 New metrics
Per-trait population mean, std, and Gini for c1, c2, ψ; mean number of accepted
updates per agent per step; fraction of agents with no in-bound neighbour.

### 3.6 Verification run
C static null control with Deffuant active (ε=0.2, μ=0.3). Gate: N_active ∈
[150,400] at t≥500. Report the c1/c2/ψ Gini trajectories over 1000 steps — note
whether and how fast each trait homogenises. This trajectory is the baseline the
Task 3 sweep must beat for ψ.

---

## 4. Task 3 — σ_inherit sweep (ψ homogenisation)

### 4.1 Rationale and design

Stage 5 ψ probe: σ_inherit=0.05 + biparental averaging collapsed Gini(ψ) from
0.25 to 0.09 within 500 steps. Higher inheritance variance may sustain diversity.
Because Deffuant (Task 2) is **also** a contracting force on ψ, the sweep must
isolate the genetic channel first.

**Cell A — genetic channel only (Deffuant OFF).** Sweep σ_inherit, measure whether
inheritance variance alone sustains ψ diversity:

| Run | σ_inherit | Deffuant | A | T | Seeds | Steps |
|---|---|---|---|---|---|---|
| psi_005_off | 0.05 (baseline) | OFF | 0.75 | 200 | 42, 43 | 3000 |
| psi_010_off | 0.10 | OFF | 0.75 | 200 | 42, 43 | 3000 |
| psi_020_off | 0.20 | OFF | 0.75 | 200 | 42, 43 | 3000 |

(C strategy; A=0.75/T=200 is the inverted condition where C survives, so the ψ
distribution evolves over a stable population — extinction not expected, but R1
rows are still emitted.)

Record at t = 0, 500, 1000, 1500, 2000, 2500, 3000: ψ mean, std, Gini; ψ quartile
starvation (Q1 low-ψ solitary vs Q4 high-ψ social).

**Cell A pass criterion (per σ_inherit value):**
`Gini(ψ)` at t=3000 ≥ 0.15 in ≥1 seed (sustained diversity — the Stage 5 failure
was a collapse to 0.09), AND Gini(ψ) at t=3000 > Gini(ψ) at t=500 (selection is
not still being out-run by averaging). Identify the **lowest σ_inherit** that
passes; call it `σ_inherit*`.

**Cell B — interaction (Deffuant ON at σ_inherit\*).**

| Run | σ_inherit | Deffuant | A | T | Seeds | Steps |
|---|---|---|---|---|---|---|
| psi_star_on | σ_inherit* | ON (ε=0.2, μ=0.3) | 0.75 | 200 | 42, 43 | 3000 |

**Cell B reported result (not a pass/fail gate):** does horizontal transmission
re-collapse the ψ diversity that the genetic channel sustained? Report Gini(ψ) at
t=3000 for Cell B vs the matching Cell A run, and state plainly whether Deffuant
undoes the σ_inherit fix.

### 4.2 If no σ_inherit value passes Cell A
Report the null in full (R4/R5). Do **not** tune beyond {0.05, 0.10, 0.20} without
supervisor approval. Lock σ_inherit at its current value (0.05) and flag ψ
co-evolution as requiring an explicit selection mechanism (Stage 6+), not just
inheritance-noise tuning.

---

## 5. Report (`outputs/stage52_cultural/report.html`)

Single self-contained HTML, figures base64-embedded. **All sections follow
CLAUDE.md Report Standards R1–R7.** Sections:

| § | Content |
|---|---|
| §1 | Pre-flight: baseline test count (207), backup, confirmation that R6 terminal-state fields are emitted (and the forced-extinction fixture test passes). |
| §2 | Task 1 (c2): equivalence gate result (max_reldiff=0). Verification run with R1 terminal-state row. defection_rate, defectors-vs-cooperators c2. One R2 sentence on what enabling defection did to population stability. |
| §3 | Task 2 (Deffuant): three equivalence gate results (disabled / μ=0 / ε=0). Verification run R1 row. c1/c2/ψ Gini trajectory plot over 1000 steps, with R3 magnitudes (how far each Gini fell and how fast). |
| §4 | Task 3 (σ_inherit): Cell A sweep table with R1 rows per run, Gini(ψ) trajectory plot (all three σ_inherit overlaid, both seeds). Quartile starvation table at t=0/1000/2000/3000. σ_inherit* stated. Cell B result vs matching Cell A, with the plain-language interaction statement from §4.1. |
| §5 | Anomalies & Open Questions (R4). Mandatory; "None identified" if clean. |
| §6 | Synthesis (R5, ≥150 words): did the cultural layer behave as designed; is ψ co-evolution now viable or still null; does defection destabilise C; does Deffuant undo the σ_inherit fix. Claim + evidence for + against + confidence. |
| §7 | Locked-parameter update: c2_defection, deffuant (ε, μ, cred_weight), σ_inherit final value. ROADMAP status. |

---

## 6. Stopping rules

| Condition | Action |
|---|---|
| 207 tests do not pass at Task 0 | Stop. Report. |
| Any equivalence gate (Task 1 or 2) shows max_reldiff > 0 | Stop. The hook is leaking into the disabled path; debug before proceeding. |
| Verification run gate fails after 2 attempts | Disable that mechanic, report with full diagnostics, halt that task; later tasks that do not depend on it may still proceed. |
| No σ_inherit value passes Cell A | Lock σ_inherit=0.05, report null, do not tune further. |
| Test suite count drops below 207 + new tests | Stop. Debug. |

---

## 7. ROADMAP update

- Mark Stage 5.2 complete.
- Lock c2_defection, Deffuant (ε, μ, cred_weight), and σ_inherit final value.
- Update ψ co-evolution status: viable at σ_inherit* / still null (with reason).
- Next: terrain topography, then Stage 5.1 LHS scan, then Stage 6.

---

## 8. Out of scope
- Any change to Si mechanics or to the H1(ii) finding.
- Si Cred (closed at Stage 5.1: works as designed, inversion robust).
- Terrain topography (next stage after 5.2).
- LHS parameter scan.
- Explicit ψ selection mechanisms beyond inheritance noise (Stage 6+).
- Biparental Si reproduction, HiveMind, inter-pool connectivity.

---

## Red-team notes (for the supervisor, not Claude Code)

**Cultural evolution / dual inheritance.** Adding Deffuant on top of biparental
genetic inheritance means ψ now has two transmission channels (vertical with
σ_inherit noise, horizontal via Deffuant) and Deffuant is a contracting map.
Running the σ_inherit sweep with Deffuant ON would confound the two; the Cell A /
Cell B split is the fix. Worth confirming you agree the lowest-passing σ_inherit
(not the highest-Gini) is the right selection rule — I chose lowest to avoid
over-injecting mutation noise that could itself swamp selection signal.

**Evolutionary game theory.** The c2 hook finally makes defection possible, which
is necessary for the support pool to be a credible collective-action model rather
than enforced altruism. But note: defection here is individually rational only
when solo_harvest > matthew_share, and the Matthew partition (α=2.0) is
deliberately unequal — so whether a stable cooperative equilibrium survives
depends on how often that inequality bites. The `defection_rate` and its
correlation with seasonal phase will tell you whether defection is a rare
edge case or a regime that erodes the pool during troughs (the latter would be a
finding in its own right).

**Complexity science.** Three new mechanics in one stage raises the risk that an
interaction effect gets attributed to the wrong mechanic. The independent
equivalence gates (each mechanic must be bit-identical when disabled) are the
guard rail; insist they all report max_reldiff=0 before trusting any downstream result.

**Deliverable count this session: 5** (blueprint, .md file, report analysis,
reporting standard, this blueprint). Recommend a fresh chat after this one — I'll
offer a handoff summary on request.
