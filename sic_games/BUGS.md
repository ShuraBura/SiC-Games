# Known bugs and discrepancies

## BUG-001 — Stage 2 pre-patch baseline parquet overwritten

**Severity:** Data integrity (affects three-way comparison table only; no simulation correctness impact)

### What happened

The Stage 2 confirmed baseline run (pre ModeSwitch patch, `strategy=carbon`) produced:

| Metric | Confirmed pre-patch value |
|---|---|
| Mean wealth | 42.0 |
| Mean Cred | 6.923 |
| Joint tasks/step | 30.41 |

These were generated when `CarbonDecision.select_target` used `w_C = agent.phi` (fixed trait, no velocity modulation).

During the Stage 2.1 ModeSwitch patch session, `configs/stage2_carbon_seed42.yaml` was re-run **after** the decision formula was changed to `w_C = agent.phi * sigmoid(v_i / v0)`. This overwrote `outputs/stage2_carbon_seed42/metrics.parquet` with patched-code values (mean_wealth=45.1, mean_cred=9.477, joint_tasks=39.46).

### Root cause

The decision logic changed from `w_C = phi` (pre-patch) to `w_C = phi * sigmoid(v/v0)` (post-patch). Even with the same seed=42, different utility weights produce different agent choices → different trajectories → different aggregate metrics. The RNG sequence itself was not affected.

Additionally, the `stage2_carbon_seed42.yaml` config was re-run during the patch session without preserving the original parquet, permanently overwriting the ground truth.

### Fix applied (Stage 2.2)

The three confirmed pre-patch values are hardcoded as `_S2_PRE_SWITCH` in `report.py`. The three-way comparison table in patched reports reads from these constants for the "C no-switch" column, and the remaining metrics use the best available approximation (the `stage2_carbon_noswitch_seed42` run with `velocity_tau=0`).

The `outputs/stage2_carbon_noswitch_seed42` run uses `w_C = phi * sigmoid(0/v0) = phi * 0.5` — intermediate between the pre-patch `w_C = phi` and the fully adaptive patched behavior. It cannot reproduce the exact pre-patch numbers without restoring the original decision formula, which is out of scope for Stage 2.2.

### Prevention

Future sessions should snapshot `outputs/` to a versioned archive (e.g., `outputs/snapshots/<tag>/`) before running any config that overwrites existing parquets.

---

## BUG-002 — Population extinction under diffusion+multi-occ at N_carry=800 (GATE B1)

**Severity:** Test-config only (no science correctness impact; documents an environmental
viability observation)

### What happened

The pre-registered Tier-3 battery config for GATE B1 (ARCHITECTURE §12.1-H §H.2, 2026-06-06)
used `mode="dynamic"`, `N_carry=800`, default `WorldConfig` (max_sugar_capacity=4, alpha=1).
Under `movement_mode="diffusion"` and `multi_occupancy.enabled=True`, the population went
extinct before step 254 in all 10 seeds. WINDOW_START=251 was never reached.

A retry with production parameters (`_bench_config`, max_sugar_capacity=16, alpha=4) also
caused extinction at step ~254, just before the window.

### Possible causes

1. **Diffusion spreads agents uniformly**, reducing concentration near sugar peaks and
   increasing metabolic death rate.
2. **Multi-occupancy** means agents compete for the same cell's sugar, reducing mean harvest.
3. **Default WorldConfig** is calibrated for the legacy single-occupancy path; the
   diffusion+multi-occ combination is more resource-stressful.
4. This may signal that the substrate viability region for diffusion+multi-occ at these
   parameters is narrower than the legacy path (a genuine science signal worth investigating).

### Fix applied

Battery config changed to `mode="fixed"` (B-fixed, 2026-06-08) — one-for-one replacement,
no demographic dynamics. This isolates the JT parity test from demographic confounds.

### What was NOT done

The dynamic-population viability question under diffusion+multi-occ was not further
investigated (out of scope for GATE B1 performance refactor). The supervisor flagged this as
a signal worth preserving: *"it may be telling you something about substrate viability at
these settings that the original §7.2 readings didn't catch."* Candidate future investigation:
measure minimum N_carry for stable C-strategy population under diffusion+multi-occ on 100×100.

### Files

- Original battery config: `tests/test_soa_jt.py` `_make_battery_cfg` (dynamic config
  preserved in the commit history at `5ae71cf`)
- GATE B1 report: `outputs/stage7_5/gate_B1_report.md`

---

## BUG-003 — `_random_unoccupied()` infinite loop when N_init > grid_cells

**Severity:** Benchmark-protocol only (blocks OCC_3200+ measurement; no science correctness impact)

### What happened

`run.py _random_unoccupied()` (line 261) is a `while True` loop that samples random (x,y)
until `(x,y) not in self.occupied`. With `N_init=3200` on a 40×40=1600-cell grid, all
1600 cells are occupied after the first 1600 agents are placed. The loop runs forever.

Stage 6.0a's OCC_3200 `perf_results.json` entry (`"cut_status": "hard-infeasible",
"rail_status": "timeout"`) was the result of the stage6_0a_perf subprocess being killed
by `_PER_CONFIG_TIMEOUT_S`. The "hard-infeasible" label was misread in the B1 gate design
as "step time exceeded the ceiling" — it was actually "model init hung forever". Verified
2026-06-08 by diagnostic: `SugarWorld(cfg)` with N_init=3200, grid=40×40 does not return
within 60s; `_bench_config` itself completes in 0.3ms.

### Root cause

`_random_unoccupied()` does not handle the case where N > grid_cells. This function is
only correct for single-occupancy mode (N ≤ grid_cells). With `substrate.enabled=True`
(multi-occupancy), `_spawn_agents(N)` with N > grid_cells calls `_random_unoccupied()`
which cannot find an unoccupied cell once the grid is full.

### What was NOT done

Fixing `_random_unoccupied()` requires changing `run.py` (oracle, D4 frozen). The fix
would add a multi-occupancy path: if `len(self.occupied) == grid_cells`, return a random
cell without checking occupancy. This is deferred to the D4-unfreeze phase (FINAL gate).

### Impact

OCC_3200, OCC_6400, OCC_12800 configs cannot be initialized in the current oracle.
Only OCC_1600 (N_init=1600 = exactly 40×40 cells) is measurable. The B1 occupancy gate
thresholds (OCC_3200 < 300 ms/step, OCC_6400 ≤ 500 ms/step) cannot be evaluated.

### Files

- `src/sic_games/run.py` lines 261–267 (`_random_unoccupied`)
- `src/sic_games/stage6_0a_perf.py` lines 166–180 (subprocess with timeout)
- `outputs/stage7_5/gate_B1_report.md` §7 (Finding B1-4)
