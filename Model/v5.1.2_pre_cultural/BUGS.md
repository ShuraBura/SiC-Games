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
