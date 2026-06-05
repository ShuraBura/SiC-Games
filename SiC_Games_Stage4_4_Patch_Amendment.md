# SiC Games — Stage 4.4 Patch Amendment: Initial Wealth Scaling

**Version:** 1.0
**Parent:** Stage 4.4 Patch blueprint
**Scope:** One config parameter + Task 2 re-run. No other changes.
**Prerequisite:** Stage 4.4 Patch Task 1 complete (age_init_upper_frac=0.25
  implemented and tested, 162/162 passing).
**Output dir:** `outputs/stage44_patch_seed42/` (same directory — append results)

---

## Problem

With `age_init_upper_frac=0.25` all initial agents start as juveniles
(age < forage_age_min=15) and harvest at η_min=0.2 efficiency. Initial
wealth is still drawn from [5, 25] — the Stage 1 vanilla Sugarscape value,
calibrated to a k=1 grid (max_sugar=4, growback_alpha=1). At k=4
(max_sugar=16, growback_alpha=4) the resource environment is 4× richer,
but agents still start with the same thin wealth buffer. Agents at the low
end of the distribution (wealth=5) with metabolism=4/step exhaust their
wealth in 1–2 steps before they ever reach productive foraging age. The
result is a first-generation juvenile starvation wave that empties the
population before any reproduction can occur.

The fix: scale initial wealth with k_grid.

---

## Change

### New config parameter

```yaml
initialization:
  age_distribution:    "realistic"
  age_init_upper_frac: 0.25
  wealth_init_scale_k: true        # NEW — multiply [w_min, w_max] by k_grid
```

When `wealth_init_scale_k: true`, initial wealth is drawn from:

```
w_i(0) ~ Uniform[w_min × k_grid, w_max × k_grid]
       = Uniform[5 × 4, 25 × 4]
       = Uniform[20, 100]   (at k=4)
```

When `wealth_init_scale_k: false` (default), behaviour is unchanged:
`Uniform[5, 25]` as before. All Stage 4.1x and earlier configs omit this
key and remain unaffected.

### Implementation

In the initialisation routine, after reading `w_min` and `w_max` from
config, apply:

```python
if config.initialization.wealth_init_scale_k:
    w_min = config.agents.initial_wealth_dist[0] * config.world.k_grid
    w_max = config.agents.initial_wealth_dist[1] * config.world.k_grid
else:
    w_min = config.agents.initial_wealth_dist[0]
    w_max = config.agents.initial_wealth_dist[1]
agent.wealth = rng.randint(w_min, w_max)
```

This applies to **all agents at t=0 only**. Newborn agents spawned
during the run still use the standard `initial_wealth_dist` (unscaled) —
they are born into the world mid-simulation and will forage normally.
Do not scale newborn wealth; only the t=0 initialisation is affected.

### New tests

Add to `tests/test_life_history.py`:

```python
def test_wealth_init_scale_k_true():
    """wealth_init_scale_k=True scales initial wealth by k_grid."""
    k = 4
    agents = initialise(N=500, wealth_init_scale_k=True, k_grid=k, seed=42)
    for a in agents:
        assert 5 * k <= a.wealth <= 25 * k, (
            f"Agent wealth {a.wealth} outside [{5*k}, {25*k}]"
        )

def test_wealth_init_scale_k_false():
    """wealth_init_scale_k=False (default) leaves wealth in [5, 25]."""
    agents = initialise(N=500, wealth_init_scale_k=False, k_grid=4, seed=42)
    for a in agents:
        assert 5 <= a.wealth <= 25
```

Run full test suite after the code change. All 162 prior tests must still pass.

---

## Re-run Task 2

Re-run the p_max sweep from the patch blueprint with `wealth_init_scale_k: true`
added to all Task 2 configs. Everything else identical: same 6 p_max values
(0.03, 0.04, 0.05, 0.06, 0.065, 0.07), same stopping rule, same gate, same
additional diagnostics (senescence/step, births/step, juv starvation/step,
mean_age at t=100/300/500).

The existing Task 2 runs (without wealth scaling) are already in the parquet.
Do not delete them — append the new runs to the report as "Task 2b" so the
effect of wealth scaling is visible by comparison.

**If a p_max now passes the gate:** proceed immediately to Task 3 (Runs B/C/D)
as specified in the patch blueprint, with `wealth_init_scale_k: true` in all
Task 3 configs.

**If still no p_max passes:** escalate. Do not attempt further parameter
adjustments without supervisor approval. State which mechanism is still
blocking (births/senescence ratio, birth formula density floor, or other).

---

## Report addendum

Append a **§2b** section to `report_patch.html`:

### §2b — Task 2 re-run (wealth_init_scale_k=true)

Same table format as §2, labelled "Task 2b". Add one column:
`w_init_mean_t0` — the mean initial wealth at t=0 (confirm ≈ 60 for k=4).

State the locked p_max if found, or the escalation condition if not.

Figures: N(t) overlay for Task 2b runs (separate from Task 2a figure so
the before/after contrast is visible).

---

## ROADMAP update

If Task 2b finds a passing p_max, update the Stage 4.4 Patch row to include:
```
wealth_init_scale_k=true (k=4 → [20,100]).
```
Add `wealth_init_scale_k` to the locked parameters table with value `true`
and note "k=4 only; k=1 configs unaffected."

---

## Out of scope

Everything from the patch blueprint out-of-scope list still applies.
Additionally: do not scale newborn wealth, do not adjust metabolism, do not
change the wealth distribution shape (it remains uniform).

---

*End of Stage 4.4 Patch Amendment*
