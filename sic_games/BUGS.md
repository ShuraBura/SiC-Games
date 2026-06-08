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
