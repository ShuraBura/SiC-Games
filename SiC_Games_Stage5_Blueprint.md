# SiC Games — Stage 5 Blueprint: Multi-Seed Ensemble, A=0.9, Si Cred

**Version:** 1.0
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Five tasks in order. Tasks 0–1 are infrastructure + validation and
  gate everything downstream. Tasks 2–4 are expansion. Task 5 is synthesis.
**Prerequisites:**
  Stage 4.5 + patch complete. All parameters locked:
  k=4, β_Si=5, p_fission_Si=0.28, p_max_C=0.12, N_carry=400, alpha_carry=1.0,
  τ_pool=0.05, ρ=0.3, λ=0.1, ψ~Beta(2,2), age_init_upper_frac=0.25,
  wealth_init_scale_k=True, cluster_init=True (C only).
  Si pool: enabled. Si k_carry: disabled.
  182 tests passing.
  H_cc pre-registered (Stage 4.5 patch §7.3).
**ROADMAP:** `G:\My Drive\docs\SiC Games\ROADMAP.md`
**Output dir:** `outputs/stage5/` (task sub-folders below)

---

## 0. North Star (read first, every session)

**Stage 5 goals:**
1. Build the `BatchRunner` infrastructure that all multi-seed work depends on.
2. Validate the Stage 4.5 single-seed findings (H1(ii) inversion, H_cc) across
   5 environmental seeds using common-random-numbers (CRN) pairing.
3. Extend the amplitude sweep to A=0.9 and tighten Si T* at A=0.75.
4. Activate Si Cred — the skeleton has been dormant since Stage 3.3.
5. Test whether ψ differentiates under sustained seasonal stress.

**What Stage 5 is not.** No c1/c2 behavioral hooks. No Deffuant updating. No
HiveMind. No inter-pool connectivity. No full nD LHS scan (deferred to Stage 5.x
pending Stage 6 statistical framework). No β or ρ sweeps.

**Failure mode to watch for.** The H1(ii) inversion at A=0.75 rests on a single
seed. If multi-seed runs show it is seed-dependent (C collapses in some seeds,
Si survives), the inversion evaporates. Report robustly — do not suppress seeds
where Si outperforms C.

---

## 1. Task 0 — BatchRunner infrastructure

### 1.1 What to build

`src/sic_games/batch.py` — a minimal batch runner that enables multi-seed
and multi-config runs with common-random-numbers support. Required API:

```python
class BatchRunner:
    def __init__(self, configs: list[Path], seeds: list[int],
                 crn: bool = True, n_workers: int = 4):
        ...

    def run(self) -> pd.DataFrame:
        """Run all (config, seed) pairs. Return tidy summary DataFrame."""
        ...
```

**Common-random-numbers (CRN):** when `crn=True`, all runs sharing the same
seed use the same sequence of environmental draws (sugar growback, peak
placement, any stochastic world events). Agent-level draws (birth, death,
decision) still use the config-specified seed. This ensures C vs Si differences
at the same seed are attributable to agent behavior, not environmental variance.
Implementation: split the RNG into two streams — `env_rng = np.random.default_rng(seed)`
and `agent_rng = np.random.default_rng(seed + 10000)`. Pass `env_rng` to world
updates, `agent_rng` to agent actions. Both configs (C and Si) at the same seed
receive identical `env_rng` sequences.

**Output naming:** `outputs/stage5/{task_id}/{config_stem}_seed{N}/`

**Tidy summary DataFrame** columns (minimum):
`config`, `seed`, `strategy`, `A`, `T`, `tf`, `N_lo`, `N_hi`, `N_mean`,
`collapse` (bool), `collapse_step`, `dormancy_rate` (Si), `carry_disc_mean` (C),
`est_starv`, `births_per_step`, `senes_per_step`.

### 1.2 New tests

Add `tests/test_batch.py`:

```python
def test_batchrunner_produces_output():
    """BatchRunner with 2 configs × 2 seeds produces 4 rows in summary."""
    runner = BatchRunner([c_config, si_config], seeds=[42, 43], crn=True)
    df = runner.run()
    assert len(df) == 4

def test_crn_env_identical():
    """CRN=True: env_rng draws are identical for same seed, different configs."""
    ...

def test_crn_agent_independent():
    """CRN=True: agent_rng draws differ between configs at same seed."""
    ...
```

Run full test suite. All 182 prior tests must pass; suite should reach ≥187.

### 1.3 Parallelism

Use `concurrent.futures.ProcessPoolExecutor(max_workers=n_workers)`. Each
(config, seed) pair is one worker job. Confirm no shared mutable state between
workers. Parquet files are written per-run before summary is assembled.

---

## 2. Task 1 — Multi-seed ensemble (H1(ii) robustness)

### 2.1 Conditions

Three Stage 4.5 conditions chosen to span the resilience landscape:

| Condition ID | A | T | tf | Rationale |
|---|---|---|---|---|
| `mod_stress` | 0.5 | 200 | 0.5 | Both survived — baseline parity |
| `high_stress` | 0.75 | 200 | 0.5 | H1(ii) inversion — C survived, Si collapsed |
| `si_low_N` | 0.5 | 100 | 0.5 | Si N dropped to [13,128] — fragility check |

Seeds: 42, 43, 44, 45, 46 (seed=42 results already exist — load from
Stage 4.5 parquets, do not re-run).

Strategies: C (full Stage 4.5 mechanics), Si (full Stage 4.5 mechanics,
pool ON). CRN=True within each (condition, seed) pair.

Total new runs: 3 conditions × 2 strategies × 4 new seeds = 24 runs.
Plus seed=42 loaded from Stage 4.5: 6 runs. Total ensemble: 30 rows.

### 2.2 Summary statistics per condition

| Metric | C | Si |
|---|---|---|
| Survival rate (N > 0 at t=1000) | X/5 | X/5 |
| Mean N (t≥500) across surviving seeds | ? | ? |
| Collapse rate | X/5 | X/5 |
| Mean collapse step (collapsed runs only) | ? | ? |

**For H1(ii) inversion at `high_stress`:**
- If C survival rate > Si survival rate across 5 seeds: inversion confirmed robust.
- If ≤ 2 seeds show C surviving where Si collapses: inversion is seed-dependent — report mixed, do not over-interpret.
- If Si outperforms C in ≥ 3 seeds: inversion was a seed artefact — report null.

**For H_cc at `high_stress`:**
Record `carry_disc_mean` per step per seed. H_cc predicts carry_discount rises
during trough phases (as N_C drops). Plot carry_discount_mean over time for
the surviving C seeds — a visible rise during troughs is supporting evidence.
Regress trough recovery time on N_min/N_carry across seeds. Negative slope
supports H_cc (§7.3 test specification).

### 2.3 Seed-level survival table (required in report)

| Seed | Condition | C survive? | C N_mean | Si survive? | Si N_mean | Si dorm_rate |
|---|---|---|---|---|---|---|
| 42 | mod_stress | (load) | (load) | (load) | (load) | (load) |
| ... | ... | ... | ... | ... | ... | ... |

Every cell must be filled. No aggregated reporting that obscures seed-level
heterogeneity.

---

## 3. Task 2 — Extended amplitude sweep + Si T* tightening

### 3.1 A=0.9 sweep

| Run ID | A | T | Strategy | Seeds |
|---|---|---|---|---|
| A09_T100_C | 0.9 | 100 | C | 42, 43 |
| A09_T200_C | 0.9 | 200 | C | 42, 43 |
| A09_T100_Si | 0.9 | 100 | Si | 42, 43 |
| A09_T200_Si | 0.9 | 200 | Si | 42, 43 |

8 runs. CRN=True within (A, T, seed) pairs.

**Gate:** survival (N > 0 at t=1000) — binary pass/fail per seed.
Record collapse_step if collapsed.

**H_cc test at A=0.9:** A deeper trough (A=0.9) should produce a stronger
carry_discount counter-cyclical kick if H_cc holds. Record N_min/N_carry and
trough recovery time for surviving C seeds. Compare to A=0.75 values.

**If C collapses at A=0.9, T=100 but survives T=200:** the longer period
provides more recovery steps between troughs — this is consistent with H_cc
(longer period = more time for counter-cyclical recovery per cycle).

**If C collapses at all A=0.9 conditions:** record A* (critical amplitude for
C) as ∈ (0.75, 0.9). Do not run further amplitude values without supervisor
approval.

### 3.2 Si T* tightening at A=0.75

From Stage 4.5: Si collapses at A=0.75, T=200 but survives A=0.5, T=100 with
N=[13,128]. Si T* at A=0.75 is bracketed in (50, 200) — a range of 150 steps.
Tighten to ≤ ±25 steps using binary search.

| Run | A | T | Bracket after run |
|---|---|---|---|
| SiT*-1 | 0.75 | 100 | If survive: (100,200); if collapse: (50,100) |
| SiT*-2 | 0.75 | bisect | Narrow bracket |
| SiT*-3 | 0.75 | bisect | Narrow to ≤ ±25 |

Seeds: 42 and 43 per run (2 seeds for robustness). Max 3 binary search runs.
Report Si T* range at A=0.75 in ≤ ±25 steps.

Compare Si T* (A=0.75) to C T* > 500 (A=0.75, Stage 4.5 patch §7.2).
State the T* gap explicitly: how much wider is C's stable period range than Si's
at this amplitude?

---

## 4. Task 3 — Si Cred activation

### 4.1 Literature search (mandatory before implementation)

Q24 (ROADMAP): "Si Cred accumulation mechanism — literature search pending Stage 5+."
Before writing any code, search LITERATURE.md and the following sources and log
findings:
- Epstein & Axtell (1996) Sugarscape: agent wealth tracking and information asymmetry
- Axelrod (1984) Evolution of Cooperation: reputation as a coordination device
- Nowak & May (1992) spatial prisoner's dilemma: local reputation and defection
- Any bounded-rationality model that uses performance history to modulate decision temperature

**Document in LITERATURE.md:** what mechanisms were considered, what was adopted,
what was rejected and why.

### 4.2 Mechanism specification

**Default mechanism (adopt unless literature search yields a better option —
consult supervisor if alternative is found):**

Si Cred accumulates per step as a function of recent foraging efficiency:

```
Δsi_cred_i(t) = max(0,  harvest_i(t) - metabolism_i(t))  ×  r_cred_Si
si_cred_i(t)  = si_cred_i(t-1) × (1 - δ) + Δsi_cred_i(t)
```

Where:
- `r_cred_Si` = accumulation rate (config, default 0.1)
- `δ` = 0.01 (same decay as C Cred, locked from Stage 2)
- `si_cred` is clamped to [0, C*_Si] where `C*_Si` = 10.0 (config, default = C*)

**Effect on behavior:** Si Cred modulates decision temperature, mirroring C's
σ-Cred coupling:

```
σ_Si_eff_i(t) = σ_Si + κ_Si × tanh(si_cred_i(t) / C*_Si)
```

Where `κ_Si` = 0.5 (config, default; smaller than C's κ=2.0 because Si has no
joint-task signal amplification). High-Cred Si agents become more explorative.

**Config (Si only):**
```yaml
si_cred:
  enabled: true           # was false since Stage 3.3
  accumulation_rate: 0.1  # r_cred_Si
  decay: 0.01             # δ — matches C Cred decay
  C_star_Si: 10.0         # Cred ceiling — matches C*
  kappa_Si: 0.5           # σ modulation strength
```

`enabled: false` recovers Stage 4.5 behavior exactly.

### 4.3 New tests

Add to `tests/test_si_cred.py`:

```python
def test_si_cred_accumulates_on_surplus():
    """Si Cred increases when harvest > metabolism."""
    ...

def test_si_cred_stable_on_deficit():
    """Si Cred does not increase when harvest < metabolism (Δ clamped to 0)."""
    ...

def test_si_cred_decays():
    """Si Cred decays by factor (1-δ) each step when no surplus."""
    ...

def test_si_sigma_eff_increases_with_cred():
    """σ_Si_eff_i > σ_Si when si_cred_i > 0."""
    ...

def test_si_cred_disabled_no_effect():
    """With enabled=False, si_cred stays 0 and σ_Si_eff = σ_Si."""
    ...
```

Full test suite after implementation: target ≥193 passing (187 + 5 new Si Cred).

### 4.4 Si Cred null control

Run Si static null control with Si Cred enabled.
Config: k=4, β_Si=5, p_fission=0.28, dormancy locked, pool ON, Si Cred enabled
(r_cred_Si=0.1, κ_Si=0.5). Seed=42, 1000 steps.

Gate: N_active ∈ [150, 400], dormancy_rate < 20%, perm_deaths ≤ 0.5/step.

Additional metrics:
| Metric | Target | Notes |
|---|---|---|
| si_cred_mean (t≥500) | > 0 | Confirm accumulation is firing |
| si_cred_std (t≥500) | > 0 | Confirm variance across agents |
| σ_Si_eff_mean (t≥500) | > σ_Si=1.238 | Confirm σ modulation is active |
| Gini(si_cred) (t≥500) | > 0.10 | Confirm meaningful inequality |

**If null control fails gate with Si Cred enabled:** reduce κ_Si to 0.2 (one
attempt). If still fails: disable Si Cred for the seasonal sweep and report.
Max 2 attempts.

### 4.5 Si Cred seasonal runs

Run Si with Si Cred enabled at the two most informative Stage 4.5 conditions:
- `high_stress`: A=0.75, T=200 (where Si collapsed in Stage 4.5)
- `si_low_N`: A=0.5, T=100 (where Si survived at marginal N)

Seeds: 42 and 43. CRN=True paired with C Stage 4.5 runs.

**Key question:** does Si Cred change the collapse outcome at A=0.75, T=200?
- If Si now survives: Si Cred provides the additional resilience margin. The
  Stage 4.5 collapse finding was with a less-capable Si model.
- If Si still collapses: Si Cred doesn't rescue dormancy cliff deaths. The
  inversion is robust to Si Cred activation.

Report N_active, dormancy_rate, si_cred_mean, σ_Si_eff_mean for each run.
Compare directly to Stage 4.5 Si results at the same conditions.

---

## 5. Task 4 — Extended ψ co-evolution probe

### 5.1 Rationale

Stage 4.5 Task 2 showed flat ψ quartile starvation (Q1=Q4=0.000). Two
explanations: (a) 1000 steps is insufficient for selection to differentiate
ψ distributions, or (b) pool benefit during troughs is too small to create
meaningful selection pressure at k=4. Task 4 tests (a) by running 3000 steps
with high seasonal stress active — enough for ~25 agent generations.

### 5.2 Runs

| Run ID | Steps | A | T | Seeds |
|---|---|---|---|---|
| psi_coev_A075_T200_3k | 3000 | 0.75 | 200 | 42, 43 |

Two runs only (C strategy, full Stage 4.5 mechanics). 3000 steps each.

Record at t=0, 500, 1000, 1500, 2000, 2500, 3000:
- ψ mean, std, Gini
- ψ quartile starvation rates (est_starv by ψ quartile)
- Gini(ψ) trajectory — should increase if selection is acting

**Pass criterion:** Gini(ψ) at t=3000 > Gini(ψ) at t=0 in at least one seed,
AND Q4 est_starv < Q1 est_starv at t=3000 with a gap > 0.01/step.

**If criterion not met:** ψ co-evolution requires either longer runs, explicit
selection pressure, or a higher-ψ-salience environment. Flag for Stage 5.x
design. Do not tune ψ parameters — report the null finding.

**If criterion met:** report the ψ trajectory, the Gini growth rate, and the
Q1/Q4 divergence point (step at which the gap first exceeds 0.01/step).

---

## 6. Report format

HTML, single self-contained file: `outputs/stage5/report_stage5.html`
All figures base64-embedded.

| § | Content |
|---|---|
| §0 | Stage context. One paragraph. Recap Stage 4.5 H1(ii) and H_cc as the two findings being tested. |
| §1 | Task 0: BatchRunner. Test counts. CRN verification (one sentence). |
| §2 | Task 1: Multi-seed ensemble. Full seed-level table (30 rows). Survival rates per condition. H_cc regression plot (recovery time vs N_min/N_carry). H1(ii) inversion verdict: robust / seed-dependent / null. |
| §3 | Task 2: A=0.9 sweep table. Si T* tightened range stated. T* gap (C vs Si at A=0.75) stated explicitly. C amplitude limit (A* range) stated. |
| §4 | Task 3: Si Cred. Literature search summary (3–5 sentences). Null control table. σ_Si_eff distribution. Seasonal comparison: Si+Cred vs Stage 4.5 Si at high_stress and si_low_N. Collapse verdict. |
| §5 | Task 4: ψ co-evolution. Gini(ψ) trajectory plot. Quartile starvation table at t=0, 1000, 2000, 3000. Pass or null finding stated. |
| §6 | H1(ii) synthesis (≥250 words). Integrate all Stage 4.5 + Stage 5 evidence. Explicit sections: multi-seed robustness, A=0.9 behaviour, Si Cred effect, ψ channel. State whether H_cc is strengthened or weakened by Stage 5 evidence. Give a clear overall H1(ii) verdict with confidence level (robust / provisional / null). |
| §7 | Locked parameters updated table. ROADMAP status. Deferred items for Stage 5.x. |

---

## 7. Coding-agent directives

1. **Task 0 before any multi-seed runs.** BatchRunner must be tested before it
   runs any production jobs. Confirm CRN produces identical env_rng sequences
   for same seed before the ensemble begins.

2. **Load Stage 4.5 seed=42 results; do not re-run.** Task 1 ensemble uses
   existing parquets for seed=42. The BatchRunner should support a
   `load_existing=True` flag that reads from a given output dir instead of
   re-running.

3. **Report all seeds.** Do not report only mean ± std without the seed-level
   table. Heterogeneity across seeds is a finding, not noise to be averaged away.

4. **Si Cred literature search before any code.** Log in LITERATURE.md. If a
   substantially better accumulation mechanism is found (one that changes the
   spec above materially), consult supervisor before implementing.

5. **CRN pairing for H_cc regression.** The H_cc regression (recovery time vs
   N_min/N_carry) should use CRN-paired C runs so that environmental variance
   does not confound the recovery time measurement. Each seed is one data point.
   5 seeds × 2 A values (0.75, 0.9) = 10 points minimum.

6. **ψ co-evolution: record every 500 steps, not just start and end.** The
   trajectory matters — a Gini that rises then falls tells a different story
   than one that rises monotonically.

7. **H1(ii) synthesis is the deliverable.** The 6 prior sections are evidence;
   §6 is the argument. ≥250 words. Must contain: a claim, evidence for, evidence
   against, confidence statement. "See table" is not acceptable.

8. **Full test suite after Task 0 (≥187) and after Task 3 (≥193).** Confirm
   counts explicitly in the report §1 and §4.

9. **Update ROADMAP.md** at completion:
   - Mark Stage 5 complete.
   - Add BatchRunner to architecture hooks (✓ Built).
   - Add Si Cred to PM tracker (✓ Implemented — Si).
   - Update H_cc status: confirmed (if Stage 5 evidence supports) or held (if
     inconclusive at multi-seed level).
   - Add Stage 5.x entry: "Full nD LHS scan (pyDOE2, 30-point LHS over
     A×T×N_carry×T_dormant_max×α_carry). c1/c2 behavioral hooks. Extended
     ψ co-evolution."

---

## 8. Success criteria

| Criterion | Target |
|---|---|
| BatchRunner implemented + CRN verified | ≥187 tests green |
| Multi-seed ensemble complete (30 rows) | Seed-level table in §2 |
| H1(ii) inversion verdict stated | Robust / seed-dependent / null with evidence |
| H_cc regression run | ≥10 data points (5 seeds × 2 A values) |
| A=0.9 sweep complete | 8 runs, survival per seed stated |
| Si T* tightened | Range ≤ ±25 steps at A=0.75 |
| Si Cred literature search logged | LITERATURE.md updated |
| Si Cred null control passes gate | Or failure documented with attempts |
| Si Cred seasonal runs complete | high_stress + si_low_N, seeds 42 and 43 |
| ψ co-evolution: pass or null | Gini trajectory plotted, verdict stated |
| H1(ii) synthesis ≥250 words | Claim + evidence for + evidence against + confidence |
| ROADMAP updated | Stage 5 complete, Stage 5.x scoped |
| ≥193 tests passing after Task 3 | Confirmed count in §4 |
| Reproducibility | Seeds 42–46, CRN documented |

---

## 9. Out of scope (Stage 5.x / Stage 6+)

- Full nD LHS scan → Stage 5.x
- c1/c2 behavioral hooks → Stage 5.x
- Deffuant cultural updating → Stage 5.x
- HiveMind coordination → Stage 7+
- Inter-pool connectivity → Stage 5.x
- Biparental reproduction for Si → Stage 7+ (design pending)
- Statistical power analysis and effect sizes → Stage 6
- Any change to κ, σ_Si, σ_base, C*, C**, δ, α, ε, velocity_tau, v_0,
  f_C, β, σ_inherit, parent_radius, η_min, τ_max bounds, or grid structure

---

*End of Stage 5 Blueprint*
