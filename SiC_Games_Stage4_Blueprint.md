# SiC Games — Stage 4 Blueprint: Seasonal Oscillation

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 4 only. All prior stages locked — do not refactor them.
**Prerequisite:** Stage 3.4 complete. Fully-formed agent confirmed.

---

## 0. North Star (read first, every session)

**Stage 4 goal:** introduce the first environmental perturbation — seasonal sugar
oscillation — and test whether C civilizations are more resilient than Si
civilizations under environmental stress. This is the first real test of H1(ii):
*C populations survive higher-volatility perturbations than variance-matched Si.*

The static world favored neither C nor Si meaningfully after variance-matching
(Stage 3). Stage 4 is where the exploration cost C pays in a static world should
begin to pay off. If C populations collapse at lower amplitude than Si, the
hypothesis is wrong. If C populations survive longer or recover faster, it is
supported.

**The comparison:** C (fully-formed, Stage 3.4 parameters) vs BoundedRationalSi
(σ_Si=1.238) on identical seasonally-oscillating worlds. Same seed, same
oscillation, same substrate. The only difference is the agent population.

**What Stage 4 is not.** It is not a sweep stage. Stage 4 runs a single canonical
perturbation (T=200, A=0.5) to establish that the mechanic works and produces
interpretable results. Amplitude sweep, period sweep, and asymmetry variations
are Stage 4.2+. Do not pre-build them.

**Scope discipline.** The WorldPerturbation hook (flagged in Stage 1 §5.3 and
ROADMAP.md) gets built in Stage 4. This is the one new architectural addition.
If the coding agent finds itself modifying agent mechanics, joint_task.py, the
Matthew partition, or the replacement rule beyond what is specified here,
stop and consult the supervisor.

**Failure modes to watch for:**
- Population collapse: N(t) < 200 sustained for > 50 steps in either run.
  If both populations collapse, A=0.5 is too severe — halt and report.
  If only Si collapses, that is a result, not a failure.
- Oscillation not firing: verify sugar capacity is actually oscillating by
  checking min/max capacity at a peak cell over the first 400 steps. If
  capacity is constant, the WorldPerturbation hook is not connected.
- Trait variance collapse: std(φ) dropping below 0.05 under stress. Biparental
  reproduction under high turnover may homogenize faster than expected.

---

## Step 0 — σ_Si update (do this before any other code change)

Update `configs/stage4_si_bounded_seed42.yaml` (and the Si bounded config
template) to set `sigma_si: 1.238`. This replaces the Stage 3 value of 1.051.

Verify: run a single Si bounded agent through 10 steps on a static world and
confirm mean_sigma = 1.238 ± 0.001. Do not proceed to seasonal oscillation
implementation until this is confirmed.

---

## 1. What changes in Stage 4 (delta from Stage 3.4)

### 1.1 WorldPerturbation protocol

New file: `src/sic_games/world_perturbation.py`

```python
class WorldPerturbation:
    """Protocol for time-varying modifications to world state.
    Called once per step, after growback and before joint-task detection.
    """
    def apply(self, world: "World", t: int, rng) -> None:
        """Modify world state in-place for step t."""
        ...

class NullPerturbation(WorldPerturbation):
    """No-op perturbation — recovers Stage 3 behavior."""
    def apply(self, world, t, rng):
        pass

class SeasonalOscillation(WorldPerturbation):
    """Sinusoidal oscillation of sugar capacity.
    c_eff(i,j,t) = c_max(i,j) * (1 - A * sin²(π*t/T))
    """
    def __init__(self, amplitude: float, period: int):
        self.A = amplitude
        self.T = period

    def apply(self, world, t, rng):
        # Modify world.effective_capacity in-place
        # Do not modify world.max_capacity (the static ceiling)
        ...
```

**Critical design note:** the oscillation modifies `effective_capacity` — a new
per-cell field that caps sugar growth each step — not `max_capacity` (the static
ceiling from Stage 1). At trough, effective_capacity = c_max * (1 - A). At peak,
effective_capacity = c_max. Sugar that has already grown above effective_capacity
at trough is shed (set to effective_capacity). This prevents sugar from
accumulating above the seasonal ceiling.

The growback rule G_α applies to current sugar up to effective_capacity, not
max_capacity, during oscillation. One line change in world.py:
`sugar = min(sugar + alpha, effective_capacity)` instead of
`sugar = min(sugar + alpha, max_capacity)`.

### 1.2 Scheduling change

Updated step order for Stage 4:

1. **WorldPerturbation.apply():** update effective_capacity for this step.
2. **Sugar shedding:** for each cell where current sugar > effective_capacity,
   set current sugar = effective_capacity.
3. **Growback** G_α: sugar grows up to effective_capacity (not max_capacity).
4. **Joint-task detection:** unchanged.
5. **Agent step:** unchanged.
6. **Cred update:** unchanged.
7. **Replacement R:** unchanged.
8. **Metrics:** expanded (see §3).

### 1.3 New config section

```yaml
perturbation:
  type: "seasonal"         # "null" for static world (Stage 3 behavior)
  amplitude: 0.5           # A — fraction of capacity lost at trough
  period: 200              # T — steps per full cycle (~5 seasons per 1000 steps)
```

Setting `type: "null"` recovers Stage 3 behavior exactly. This is used for
the control runs.

---

## 2. Math specification

### 2.1 Seasonal oscillation form

At step t, the effective capacity of cell (i,j) is:

$$c_{\text{eff}}(i,j,t) = c_{\max}(i,j) \cdot \left(1 - A \cdot \sin^2\!\left(\frac{\pi t}{T}\right)\right)$$

At t=0: $c_{\text{eff}} = c_{\max}$ (full capacity, peak season).
At t=T/2: $c_{\text{eff}} = c_{\max}(1-A)$ (minimum capacity, trough).
At t=T: $c_{\text{eff}} = c_{\max}$ (full capacity again).

For A=0.5, T=200: peak cells oscillate between capacity 4 (peak) and capacity 2
(trough). Non-peak cells (c_max < 4) oscillate proportionally.

### 2.2 Sugar shedding

When effective_capacity drops below current sugar (entering trough), excess sugar
is shed immediately:

$$s(i,j,t) \leftarrow \min\!\big(s(i,j,t),\; c_{\text{eff}}(i,j,t)\big)$$

This is applied after WorldPerturbation.apply() and before growback.

---

## 3. Metrics and report

### 3.1 New per-step metrics

| Metric | Definition |
|---|---|
| `mean_effective_capacity` | mean c_eff across all cells — tracks seasonal phase |
| `season_phase` | t mod T / T — normalized phase [0,1] |
| `peak_sugar_mean` | mean sugar at the two peak cells specifically |
| `population_trough_min` | minimum N(t) observed during each trough |

### 3.2 New per-season metrics (aggregated over each T=200 step cycle)

| Metric | Definition |
|---|---|
| `season_survival_rate` | fraction of agents alive at trough who survive to next peak |
| `season_cred_delta` | change in mean_cred from peak to trough |
| `season_starvation_total` | total starvation deaths per season |

### 3.3 Trait dynamics under stress

Repeat Stage 3.3 trait metrics (std(φ), std(ψ), std(c1), std(c2), Moran's I)
for both C and Si runs. Key question: does environmental stress drive spatial
trait clustering (Moran's I > 0) that was absent in the static world?

### 3.4 Report structure

Single report covering four runs (see §4). Primary comparison table:

| Metric (final 100 steps) | Stage 3 C (static) | Stage 4 C (seasonal) | Stage 3 Si (static) | Stage 4 Si (seasonal) |
|---|---|---|---|---|
| Mean wealth | ? | ? | ? | ? |
| Gini wealth | ? | ? | ? | ? |
| Spatial dispersion | ? | ? | ? | ? |
| Deaths/step (starvation) | ? | ? | ? | ? |
| Deaths/step (newborn) | ? | ? | ? | ? |
| Deaths/step (established) | ? | ? | ? | ? |
| Population trough min | — | ? | — | ? |
| Mean Cred | ? | ? | — | — |
| Gini Cred | ? | ? | — | — |
| Mean sigma | ? | ? | ? | ? |
| Joint tasks/step | ? | ? | ? | ? |
| std(φ) | ? | ? | ? | ? |
| Moran's I (c1) | ? | ? | ? | ? |

Stage 3 static values loaded from confirmed parquets — do not re-run.

### 3.5 Season-by-season survival plot

For both C and Si: plot N(t) over all 1000 steps with seasonal phase overlaid
(shaded trough periods). This is the primary visual for H1(ii) — does C maintain
higher N(t) during troughs?

---

## 4. Runs to execute

Four runs, in strict order:

| Run | Config | Purpose |
|---|---|---|
| 1 | `stage4_si_null_seed42.yaml` | Si static control (σ_Si=1.238 verification) |
| 2 | `stage4_c_null_seed42.yaml` | C static control (full Stage 3.4 agent, no oscillation) |
| 3 | `stage4_si_seasonal_seed42.yaml` | Si under seasonal oscillation |
| 4 | `stage4_c_seasonal_seed42.yaml` | C under seasonal oscillation |

Runs 1 and 2 are null-perturbation controls — they verify that σ_Si=1.238 update
and WorldPerturbation infrastructure don't break existing behavior before
oscillation is activated. Compare against Stage 3.4 parquets. If runs 1 or 2
deviate significantly from Stage 3.4 results, halt and diagnose before running 3 or 4.

Stage 3 static reference values loaded from:
- Si static: `outputs/stage3_si_bounded_seed42/metrics.parquet`
- C static: `outputs/stage34_k20_a20_seed42/metrics.parquet` (canonical cell 2,3)

---

## 5. Success criteria

1. **Oscillation confirmed firing.** Peak cell capacity oscillates between 4.0
   (peak) and 2.0 (trough) with period T=200. Verify in first 400 steps.

2. **Neither population immediately collapses.** Both C and Si maintain N(t) > 150
   for at least the first 200 steps (first full season). If either collapses in
   season 1, A=0.5 is too severe — halt and report.

3. **Null controls match Stage 3.4.** Run 1 (Si null) and Run 2 (C null) produce
   metrics within 5% of their Stage 3.4 counterparts on mean wealth, starvation,
   and Gini wealth. If not, the infrastructure change broke something.

4. **Seasonal signal visible.** N(t) shows clear oscillatory pattern correlated
   with seasonal phase — population dips during troughs and recovers at peaks.
   If N(t) is flat, agents are insensitive to the oscillation (unlikely at A=0.5).

5. **Tests pass.**

6. **Reproducibility** confirmed for all four runs.

---

## 6. Tests

`tests/test_seasonal_oscillation.py`:

1. **Capacity formula:** for known (t, T, A, c_max), verify c_eff matches
   analytic formula to 6 decimal places at t=0, T/4, T/2, 3T/4, T.

2. **Sugar shedding:** construct cell with sugar=4, c_eff=2, verify sugar
   set to 2 after shedding step.

3. **Growback respects c_eff:** verify sugar grows to c_eff (not c_max) during
   trough phase.

4. **NullPerturbation recovers Stage 3:** verify effective_capacity = max_capacity
   always when NullPerturbation is active.

5. **WorldPerturbation protocol:** verify SeasonalOscillation and NullPerturbation
   both implement the protocol correctly (duck-typing check).

---

## 7. Coding-agent directives

1. **Step 0 first.** Update σ_Si and verify before touching anything else.
   One config change, one verification run. Do not proceed until confirmed.

2. **WorldPerturbation as a protocol, not a class hierarchy.** Duck-typing is
   sufficient — SeasonalOscillation and NullPerturbation need not share a base
   class. The run loop calls `.apply(world, t, rng)` and that is the full
   interface contract.

3. **effective_capacity is a new world field.** Add it to World.__init__ as a
   copy of max_capacity. WorldPerturbation.apply() modifies it in-place each step.
   Sugar shedding and growback read from effective_capacity. max_capacity is never
   modified after initialization.

4. **One line change in world.py.** The growback rule changes from
   `min(sugar + alpha, max_capacity)` to `min(sugar + alpha, effective_capacity)`.
   That is the only change to world.py. Do not refactor anything else.

5. **Run null controls first.** Runs 1 and 2 before Runs 3 and 4. Confirm null
   controls match Stage 3.4 before activating oscillation.

6. **Load Stage 3 static references from parquet.** Do not re-run Stage 3 configs.

7. **Season-by-season survival plot is mandatory.** N(t) with shaded trough
   periods for both C and Si on the same axes. This is the primary visual
   deliverable of Stage 4.

8. **Update ROADMAP.md** at completion: mark Stage 4 complete, record first
   H1(ii) result, flag any new deferred items.

---

## 8. Open questions for Stage 4.2+

| Q | Topic |
|---|---|
| Q15 | Amplitude A sweep: {0.25, 0.50, 0.75} — Stage 4.2 |
| Q16 | Period T sweep: {50, 100, 200} — Stage 4.2 |
| Q17 | Asymmetry: longer trough than peak — Stage 4.2 |
| Q18 | c1/c2 behavioral hooks: does conformism vs individualism predict trough survival? — Stage 4+ |
| Q19 | Prestige bias in cultural transmission under stress — Stage 4+ |
| Q20 | Deffuant-style cultural updating — Stage 4+ |

---

## 9. Deferred

- Amplitude sweep. → Stage 4.2.
- Period sweep. → Stage 4.2.
- Mobile resources. → Stage 4.3+.
- Scheduled shocks. → Stage 4.4+.
- c1/c2 behavioral hooks. → Stage 4+.
- Prestige bias. → Stage 4+.
- Deffuant updating. → Stage 4+.
- Full nD parameter scan (LHS). → Stage 5.x.
- Multi-world batch runs. → Stage 5.
- Heuristic drift. → Stage 5+.
- Statistical testing of H1. → Stage 6.
