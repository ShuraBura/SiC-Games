# SiC Games — JointTaskManager Spatial Hash Fix + Verification

**Version:** 1.0
**Scope:** One code change, one verification benchmark. Nothing else.
**File to change:** `src/sic_games/joint_task.py` — `JointTaskManager.process_step()` only.
**Output dir:** `outputs/benchmark_post_fix/`

---

## 1. The fix

### Current behaviour (do not keep)

`process_step()` iterates over every cell in the grid, then for each cell
scans all N agents to find those within d=1. Cost: O(W×H×N) per step.

### Replacement: spatial hash

At the start of each call to `process_step()`, build a cell-keyed dict
mapping each occupied cell to its resident agent. Then for each agent,
look up only the 9 adjacent cells (Moore neighbourhood, toroidal).
No full agent-list scan per cell required.

```python
def process_step(self, agents, world, rng):
    # Step 1: build spatial hash — O(N)
    cell_to_agent = {}
    for agent in agents:
        cell_to_agent[(agent.row, agent.col)] = agent

    # Step 2: for each agent, check 8 Moore neighbours — O(N × 9) = O(N)
    processed = set()
    for agent in agents:
        if agent.id in processed:
            continue
        neighbours = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r = (agent.row + dr) % world.height
                c = (agent.col + dc) % world.width
                neighbour = cell_to_agent.get((r, c))
                if neighbour is not None and neighbour.id not in processed:
                    neighbours.append(neighbour)
        if neighbours:
            self._form_task(agent, neighbours, rng)
            processed.add(agent.id)
            for n in neighbours:
                processed.add(n.id)
```

**Total cost: O(N) per step**, independent of grid size.

### Constraints

- Do not change `_form_task` or any task outcome logic.
- Do not change the public interface of `JointTaskManager`.
- Do not change any config schema or YAML files.
- `processed` set ensures no agent participates in more than one task
  per step — matches existing behaviour.
- Toroidal wrap required on both axes: `% world.height`, `% world.width`.

### New tests

Add to `tests/test_joint_task.py`:

```python
def test_spatial_hash_finds_adjacent():
    """Agents at d=1 are detected as joint-task candidates."""

def test_spatial_hash_misses_distant():
    """Agents at d=2 are not included."""

def test_spatial_hash_toroidal_wrap():
    """Agent at row=0 finds neighbour at row=grid_height-1."""

def test_no_double_participation():
    """Each agent appears in at most one task per step."""

def test_task_outcomes_unchanged():
    """Matthew partition output matches pre-fix reference values on
    seed=42, 50x50, N=250, 100 steps. Generate reference on first
    run and save to outputs/benchmark/b0_jt_reference.parquet;
    load and compare on subsequent runs."""
```

Full suite after change: all 193 prior tests pass, suite reaches ≥198.

---

## 2. Smoke test (before benchmark)

50-step run: 50×50, N=250, seed=42, static world, C strategy.

Confirm:
- `joint_tasks_per_step` > 0 (tasks are firing)
- Population stays in [200, 300]
- No exceptions or assertion errors

**If smoke test fails: stop. Do not run the benchmark.**

---

## 3. Verification benchmark

Same configs and stopping rules as the original benchmark, extended to B4.

| ID | Grid | N | Steps | Run if… |
|---|---|---|---|---|
| B0 | 50×50 | 250 | 500 | Always |
| B1 | 100×100 | 500 | 500 | Always |
| B2 | 100×100 | 1000 | 500 | B1 < 5 min |
| B3 | 150×150 | 1000 | 500 | B2 < 5 min |
| B4 | 150×150 | 2000 | 500 | B3 < 5 min |

Stopping rule: abort any run exceeding 20 minutes, skip larger configs.
Same config scaling: peaks at (0.2W, 0.8H) and (0.8W, 0.2H),
band_width_k = (W/50)×6, k_grid=4, N_carry ∝ grid area, seed=42,
static world, full Stage 5 C mechanics.

---

## 4. Report

HTML: `outputs/benchmark_post_fix/report_benchmark_postfix.html`

### §0 — Fix summary
One paragraph. File changed, method replaced. Test count: 193 → ≥198.

### §1 — Timing comparison table

Pre-fix column loaded from original benchmark. Post-fix from this run.

| ID | Grid | N | Pre-fix ms/step | Post-fix ms/step | Speedup |
|---|---|---|---|---|---|
| B0 | 50×50 | 250 | 499.6 | ? | ?× |
| B1 | 100×100 | 500 | 7378.5† | ? | ?× |
| B2–B4 | — | — | — | ? | — |

†B1 pre-fix was aborted at 200 steps; extrapolated value.

### §2 — Component breakdown (B0 and B1)
Stacked bar charts. State explicitly: "joint-task is now X% of step time
at B0 (was 89%) and Y% at B1."

### §3 — Scaling exponents (post-fix)
Refit grid exponent from B0/B1/B3 (constant density).
Refit N exponent from B1/B2 (same grid, N doubles).
State both values. Expected: grid ≈ 1–2, N ≈ 1.

### §4 — Updated feasibility verdict
Restate the four questions with post-fix answers.
Updated LHS wall-time estimates (300 runs, 4 workers) for each config
that ran.

---

## 5. Success criteria

| Criterion | Target |
|---|---|
| Only `process_step` changed | Confirmed — no other diffs |
| ≥198 tests green | Confirmed count in §0 |
| Smoke test passes | joint_tasks > 0, population stable |
| B0 post-fix ms/step < 100 | ~9× speedup expected |
| B1 post-fix ms/step < 600 | 100×100 now feasible |
| Grid scaling exponent ≤ 2.0 | Was 3.88 |
| JT % of step time < 20% at B1 | Was 89% at B0 |
| `test_task_outcomes_unchanged` passes | No behaviour change |

---

*End of JT Fix + Verification Directive*
