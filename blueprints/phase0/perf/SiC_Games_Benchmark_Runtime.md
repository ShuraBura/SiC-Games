# SiC Games — Runtime Benchmark Directive

**Version:** 1.0
**Scope:** Performance measurement only. No science. No new mechanics.
  No parquet outputs beyond timing data. No ROADMAP entry required.
**Purpose:** Inform grid size and agent count decisions for Stage 5.x
  terrain topography work.
**Output dir:** `outputs/benchmark/`

---

## 0. What we need to know

Four questions, in priority order:

1. **How does runtime scale with grid size?** Is it O(grid²) or worse?
2. **How does runtime scale with N?** Is it O(N) or O(N²)?
3. **Where is the bottleneck?** Grid update, agent step, pool, or metrics?
4. **What is the feasibility boundary?** Which configurations keep a single
   run under 5 minutes (the target for LHS-scale work)?

---

## 1. Benchmark configurations

Use the full Stage 5 C model (all mechanics active: pool, carry_discount,
biparental, DTM birth, age-efficiency ramp, Cred, ψ). Seasonal perturbation
OFF (static world — removes seasonal variance from timing signal).

Peak positions scale proportionally to grid: relative positions fixed at
(0.2, 0.8) and (0.8, 0.2) of grid size. band_width_k scales with grid /
50 × 6 (preserving peak gradient shape). k_grid=4 throughout (max_sugar
and growback_alpha unchanged — resource density stays constant per cell).

| ID | Grid | N | Density | Steps | Purpose |
|---|---|---|---|---|---|
| B0 | 50×50 | 250 | 10.0% | 500 | Current baseline — load from Stage 5 if possible, else re-run |
| B1 | 100×100 | 500 | 5.0% | 500 | 2× grid, half density |
| B2 | 100×100 | 1000 | 10.0% | 500 | 2× grid, same density |
| B3 | 150×150 | 1000 | 4.4% | 500 | 3× grid, lower density |
| B4 | 150×150 | 2000 | 8.9% | 500 | 3× grid, same density |
| B5 | 200×200 | 1500 | 3.75% | 500 | 4× grid, lower density |
| B6 | 200×200 | 3000 | 7.5% | 500 | 4× grid, near-same density |

All runs: seed=42, no seasonal perturbation, CRN not required (single seed).

**Run order:** B0 → B1 → B2 → B3. If B3 total time > 10 minutes: skip B4,
run B5 only. If B5 total time > 20 minutes: skip B6 and flag. Never run
the next config if the previous one exceeded 20 minutes — it won't be useful.

---

## 2. What to measure

### 2.1 Wall-clock timing

Use `time.perf_counter` wrapped around the full run loop. Record:

```python
t_total          # total wall-clock seconds for all N_steps steps
t_per_step_mean  # mean seconds per step
t_per_step_std   # std of per-step time (should be stable — spikes indicate GC)
t_warmup         # time for first 50 steps (JIT warmup if using numba/etc.)
```

Record per-step times as a list — plot the time series to check for drift
(memory pressure) or spikes (GC pauses).

### 2.2 Component breakdown (for B0 and B2 only)

Instrument the run loop with `time.perf_counter` around each component:

```python
t_grid_update    # WorldPerturbation.apply() + growback step
t_agent_step     # full agent loop: vision scan + decision + move + harvest + pay + age
t_pool_step      # support pool contribute + distribute
t_repro_step     # DTM birth check + biparental reproduction
t_metrics_step   # parquet logging and metric computation
```

Report as mean ms/step and % of total for each component.

**This is the bottleneck map.** If `t_agent_step` is >70% of total: the
agent loop is the bottleneck (vision scan, softmax). If `t_grid_update` is
>30% at large grid sizes: numpy vectorization of growback is needed. If
`t_pool_step` is >20%: pool pair-checking is O(N²).

### 2.3 Memory

Use `tracemalloc` snapshots at t=0, t=250, t=500:

```python
mem_t0_mb     # peak memory at start (MB)
mem_t250_mb   # peak memory at step 250
mem_t500_mb   # peak memory at step 500
mem_delta_mb  # mem_t500 - mem_t0 (should be near 0 — check for leaks)
```

A growing `mem_delta` across steps indicates a memory leak in parquet
buffering or metric accumulation.

### 2.4 Throughput summary metric

```python
agent_steps_per_second = (N × n_steps) / t_total
```

This single number allows cross-configuration comparison independent of N
and step count. Higher is better.

---

## 3. Scaling analysis

After all runs complete, compute:

**Grid scaling exponent** (N held roughly constant between B1 and B3):
```
fit log(t_total) ~ exponent × log(grid_size) + const
```
Expected: exponent ≈ 2 if grid update dominates, exponent ≈ 1 if agent
loop dominates (agent loop is O(N × v²), independent of grid beyond
vision range).

**N scaling exponent** (grid held constant — compare B1 vs B2, B3 vs B4,
B5 vs B6):
```
fit log(t_total) ~ exponent × log(N) + const
```
Expected: exponent ≈ 1 if O(N) (no all-pairs checks), exponent ≈ 2 if
pool or joint-task detection is doing O(N²) work.

Report both exponents in the summary table. If N exponent > 1.3, there is
a super-linear bottleneck that needs fixing before scaling to large grids.

---

## 4. Report format

HTML, self-contained: `outputs/benchmark/report_benchmark.html`

### §0 — Configuration table
All 7 configs with grid, N, density, steps. Indicate which ran and which
were skipped (with reason).

### §1 — Timing results table

| ID | Grid | N | t_total (s) | ms/step | agent-steps/s | Run? |
|---|---|---|---|---|---|---|
| B0 | 50×50 | 250 | ? | ? | ? | ✓ |
| ... | | | | | | |

Highlight in green any config where ms/step < 600 (i.e., 500 steps < 5
minutes). Highlight in red any config > 2400ms/step (> 20 min for 500 steps).

### §2 — Component breakdown (B0 and B2)
Two stacked bar charts: ms/step per component for B0 and B2. One row per
component: grid, agent, pool, repro, metrics. Percentage labels.

### §3 — Scaling plots
Two log-log scatter plots: t_total vs grid_size (N constant) and t_total
vs N (grid constant). Fitted line with slope annotation.

### §4 — Memory table
mem_t0, mem_t250, mem_t500, mem_delta for each config that ran.

### §5 — Feasibility verdict

Explicit text answers to the four questions from §0:

1. Grid scaling: "Runtime scales as O(grid^X) based on B0/B1/B3 comparison."
2. N scaling: "Runtime scales as O(N^Y) based on B1/B2 and B3/B4 comparisons."
3. Bottleneck: "The dominant cost at current scale is [component] at Z% of step time."
4. Feasibility boundary: "Configurations feasible for LHS-scale work (500 steps
   < 5 min): [list]. Configurations requiring optimisation: [list]."

### §6 — Recommended grid sizes for Stage 5.x
Based on the feasibility verdict, state explicit recommendations:
- **Safe (no changes needed):** grid sizes where 30-run LHS × 5 seeds × 2
  strategies = 300 runs completes in < 4 hours wall-clock with 4 workers.
- **Feasible with care:** grid sizes where the above takes 4–12 hours
  (weekend batch viable).
- **Needs optimisation first:** grid sizes where single runs exceed 5 minutes.

---

## 5. Coding-agent directives

1. **No science in this run.** Do not record parquets for population dynamics,
   Cred, wealth, or any substantive metric. Record timing only. The model runs
   to completion but only the timing data is saved.

2. **Instrument before running.** Add timing instrumentation to the run loop
   before any benchmark run. Confirm timing code is active with a 10-step
   smoke test before committing to 500-step runs.

3. **B0 from cache if possible.** If Stage 5 runs already have a 500-step
   timing log for seed=42 static world C, extract it. Only re-run B0 if no
   timing data exists.

4. **Per-step time list is required for B0, B2, B4.** Plot as line chart
   alongside mean ± std. A flat line confirms steady-state timing; an upward
   drift indicates memory pressure.

5. **Respect the stopping rule.** If any config exceeds 20 minutes wall-clock
   for 500 steps, stop that run cleanly, record what completed, and skip
   larger configs. Do not let a benchmark run overnight.

6. **No code changes to the model.** Benchmarking instruments the existing
   code with timers — it does not optimise or refactor. Optimisation decisions
   come after the report is reviewed by the supervisor.

7. **Report the Python version and hardware summary in §0.** CPU model, core
   count, RAM, Python version, numpy version. This anchors the timings.

---

## 6. Success criteria

| Criterion | Target |
|---|---|
| B0 timing confirmed | ms/step reported |
| At least B0–B3 complete | 4 configs minimum |
| Component breakdown for B0 and one large config | Two stacked bar charts |
| Both scaling exponents reported | Grid exponent + N exponent |
| Feasibility verdict stated | Explicit grid size recommendations |
| Memory delta ≈ 0 | No leak (mem_delta < 10 MB across 500 steps) |
| Hardware/software summary in report | CPU, RAM, Python, numpy |

---

*End of Runtime Benchmark Directive*
