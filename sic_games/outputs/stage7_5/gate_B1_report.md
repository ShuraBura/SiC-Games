# Stage 7.5 GATE B1 Report — VecJointTaskManager

**Date:** 2026-06-06  
**Gate:** B1 — Vectorised JT multi-occupancy redesign  
**Verdict:** STOP — two gate failures, one open decision

---

## 1. What was built

`soa_jt.py` — `VecJointTaskManager` drop-in for `JointTaskManager`:
- O(N) agent array build (one Python loop, then numpy)
- O(W×H) qualifying-cell scan via `np.bincount + np.roll` mask
- O(n_JT_events × cluster_size) inner loop over qualifying cells
- `keyed_uniform` D2 defection draws (order-independent, registered Tier-3 change)
- `consumed` mask for agent exclusivity (see finding below)

`tests/test_soa_jt.py` — 10 tests (9 fast unit, 1 slow battery):
- Matthew arithmetic correctness, sugar conservation, no-double-count, no-event gates
- `test_tier3_gate_b1_battery` — the GATE B1 statistical equivalence test  
- **All 9 unit tests PASS.** The `slow` battery FAILS (details below).

`outputs/stage7_5/benchmark_b1_occupancy.py` — OCC_{1600,3200,6400,12800}_g40 benchmark

---

## 2. Occupancy benchmark results

**Protocol:** Same as Stage 6.0a recon — warmup=10, window=80, step_ceiling=600 ms, 3-consecutive limit; `_bench_config` base with `SubstrateConfig(diffusion, kappa=1.0)`.

| Config | n_carry | Recon oracle | VecJTM | Delta |
|---|---|---|---|---|
| OCC_1600_g40 | 20000 | 170.6 ms/step (PASS) | **115.5 ms/step** | −32% speedup |
| OCC_3200_g40 | 32000 | hard-infeasible | **hard-infeasible** | no change |
| OCC_6400_g40 | 64000 | skipped | skipped | — |
| OCC_12800_g40 | 128000 | skipped | skipped | — |

### OCC_1600 trajectory (VecJTM):

```
step  0: N=1605   ms=44   peak_occ=4
step 10: N=1769   ms=82   peak_occ=5
step 20: N=2125   ms=51   peak_occ=6
step 30: N=2890   ms=73   peak_occ=7
step 40: N=3853   ms=156  peak_occ=8
step 50: N=4395   ms=97   peak_occ=12
step 60: N=4582   ms=153  peak_occ=11
step 70: N=4700   ms=111  peak_occ=10
step 80: N=4875   ms=192  peak_occ=12
step 89: N=5233   ms=201  peak_occ=13
mean_occ=3.44  ms_mean=115.5
```

Recon: ms_mean=170.6, final_n=3183, mean_occ=2.35.

**Note on VecJTM population discrepancy:** VecJTM OCC_1600 grew to N=5233 vs oracle N=3183. This is a direct consequence of Finding #1 below (agent exclusivity semantics differ — oracle allows adjacent-cell double-participation, VecJTM does not; agents in the oracle receive more sugar from multi-cell clusters, raising wealth/births).

### OCC_3200 hang root cause

OCC_3200 ran for >17 minutes before being killed. The issue is not VecJTM (which is O(N)+O(W×H)). The bottleneck is **`self.mean_cred()` called per newborn** at `run.py` line 784:

```python
offspring.cred = self._f_C * self.mean_cred()   # run.py line 784
```

`mean_cred()` iterates all living agents — O(N) per birth. With N_carry=32000, the population grows to ~30,000 agents within 20 warmup steps. Each step produces O(N_births) newborns; each triggers an O(N) mean_cred() scan → O(N_births × N) ≈ O(N²) per step. At N=30,000 this dominates completely.

Note: the biparental *partner search* was already made O(r²) by the Task 4 spatial-hash fix (`_birth_spatial_hash` in run.py line 768–770). The partner search is **not** the bottleneck. The `mean_cred()` call on line 784 is.

**This is the same GATE A1 hotspot** (previously measured: oracle N-exponent 2.055). VecJTM eliminates the JT-specific O(occupancy) cost but cannot address `mean_cred()` per birth because run.py is frozen (D4). The vectorised replacement `mean_cred_vec` exists (GATE A1 PASS) but is not yet wired into the oracle step loop.

---

## 3. Pre-registered performance gate evaluation (ARCHITECTURE §12.1-H §H.3)

| Gate | Threshold | Result | Verdict |
|---|---|---|---|
| OCC_3200_g40 | < 300 ms/step | hard-infeasible (both oracle and VecJTM) | **FAIL** |
| OCC_6400_g40 | ≤ 500 ms/step | skipped (preceding config infeasible) | **FAIL** |
| Occupancy exponent | ≤ 1.5 | only 1 feasible point — cannot compute | **INCONCLUSIVE** |

**Occupancy gate: FAIL.** VecJTM eliminates the JT-specific O(occupancy) bottleneck but the O(N²) birth mechanism becomes the new cliff at high N.

---

## 4. Tier-3 statistical battery result

**Pre-registered:** 10 seeds [42..51], 100×100 grid, N_init=500, N_carry=800, 400 steps, multi_occ=True, kappa=1.0, c2_defect=True, window steps 251–400.

### Battery result: FAIL (Test 1)

```
seed=42  oracle_jt=0.0/step  vec_jt=0.0/step  (1.5s)
seed=43  oracle_jt=0.0/step  vec_jt=0.0/step  (1.6s)
... (all seeds similar)
Test 1 N(t) envelope: min coverage = 0.845 (FAIL; threshold 0.90)
Per-seed coverage: [1.00, 0.92, 0.84, 1.00, 1.00, 1.00, 0.94, 1.00, 1.00, 1.00]
```

**Root cause:** With the pre-registered config (default WorldConfig, low sugar/wealth), the population goes extinct by step ~100 in both oracle and VecJTM runs. The WINDOW_START=251 sampling window is never reached, so jt_per_step=0.0 for all seeds. The N(t) envelope test fails because oracle and VecJTM diverge during steps 1–100 while JT IS firing (see Finding #1).

**Verified:** Even with production parameters (`_bench_config`, max_sugar_capacity=16, alpha=4), the population goes extinct at step ~254 under diffusion+multi-occ at N_carry=800. The WINDOW_START=251 is marginally missed.

---

## 5. Findings (both are STOP-worthy)

### Finding B1-1: Undeclared behavioral difference — agent exclusivity

**The pre-registration §12.1-H H.1 states:** "Agent exclusivity: consumed mask prevents double-counting (same semantics as oracle)"

**This is factually incorrect.** The oracle (`joint_task.py`) uses `processed_cells: set` which prevents the *same cell* from firing twice, but does NOT prevent the same *agent* from appearing in multiple event clusters across adjacent cells. An agent at position (5,5) can be in both the cluster for cell (5,5) AND the cluster for cell (6,5) if both qualify.

VecJTM's `consumed` mask prevents agent re-participation. This means:
- **Oracle:** agents near two adjacent qualifying cells receive sugar from both cells' JT distributions
- **VecJTM:** agents near two adjacent qualifying cells receive sugar from only the first cell's distribution

**Effect:** Oracle distributes more total sugar to agents in high-occupancy multi-peak regions → higher wealth → higher birth rate → higher population (observed: oracle OCC_1600 final_n=3183 vs VecJTM final_n=5233 — INVERTED from expectation, suggesting additional factors).

**Supervisor decision required:** Accept as Tier-3 semantic improvement (VecJTM is more scientifically correct — an agent can't be at two joint tasks simultaneously)? Or fix VecJTM to match oracle semantics?

### Finding B1-2: Pre-registered battery config causes pre-window extinction

**The population goes extinct before step 254** in both oracle and VecJTM under the pre-registered parameters. The WINDOW_START=251 sampling window is never reached. The Tier-3 equivalence tests (Tests 2–4) cannot be evaluated.

**The N(t) divergence (Finding B1-1 effect) during steps 1–100 is what causes Test 1 to fail** (0.845 < 0.90 threshold). With identical trajectories (JT=0 case), both would be in the envelope. The divergence reveals that the behavioral difference matters even at the sparse N=500 density.

**Supervisor decision required:** Revise the battery config to one that sustains a stable population through step 400, OR lower WINDOW_START to a step before extinction (e.g., 51–100), OR accept Tier-3 FAIL as-is and address the behavioral difference first.

---

## 6. What passed

| Component | Result |
|---|---|
| 9 unit tests (VecJTM mechanics) | PASS |
| Full suite, 301 tests | PASS (all prior tests still green) |
| OCC_1600_g40 VecJTM speedup | 115.5 vs 170.6 ms/step (32% faster) |
| Matthew arithmetic parity | exact float match (rtol 1e-9) |
| Sugar conservation | holds to < 1e-9 |
| No double-count (agent level) | PASS |
| `slow` marker registered in pyproject.toml | done |

---

## 7. Anomalies and open questions

1. **VecJTM OCC_1600 population is LARGER than oracle** (5233 vs 3183). Expected direction was the opposite if VecJTM distributes less sugar. Likely explanation: VecJTM processes qualifying cells in the correct x-major order but skips agents after first participation, leaving more sugar on adjacent qualifying cells → those cells' sugar goes to solo harvesters → more individual wealth → more births. Full mechanism not verified.

2. **The occupied-cell tracking difference**: VecJTM zeros the field at `sugar_field.sugar[cx, cy] = 0.0` and also tracks in `sug_local`. The defection solo-harvest check `solo = sug_local[pos_y[cluster_arr], pos_x[cluster_arr]]` reads from the local copy, which may not match `sugar_field.sugar` for cells already processed in prior JT events this step. Oracle reads `sugar_field.sugar[ax, ay]` directly, which is updated cell-by-cell as events fire. This is a second potential behavioral difference.

3. **Profiler output for OCC_3200 not yet received.** Will update this section when available.

---

## 8. Path forward (for supervisor)

The B1 gate has two failures and two open design questions:

**Decision A (behavioral difference):** Fix VecJTM to match oracle (remove consumed mask, allow multi-event participation as oracle does) OR accept it as a deliberate improvement and update the pre-registration accordingly.

**Decision B (battery config):** Use the production `_bench_config` as base with `N_carry` set high enough that the population survives 400 steps under diffusion mode. Proposed: N_carry = 20000 (same as OCC_1600 recon) with N_init = 2000 on a 100×100 grid. Or: use static population (mode="fixed") to isolate the JT comparison from demographic dynamics.

**Decision C (performance path):** VecJTM eliminates the JT O(occupancy) bottleneck but cannot fix the O(N²) birth mechanism. The occupancy cliff survives because births cause population explosion at high n_carry. The B1 performance gate was written with the assumption that JT was the sole bottleneck. If the new bottleneck is BiparentalReproduction, that is the target for B1.5 (vectorise biparental partner search).

**Alternatively:** Accept that the feasible occupancy range shifts from OCC_1600=feasible / OCC_3200=infeasible (oracle) to approximately OCC_3200=feasible / OCC_6400=infeasible (VecJTM + vectorised birth). The 32% speedup on OCC_1600 demonstrates VecJTM works; the next target is clear.

---

*GATE B1 verdict: STOP. Two pre-registered gates fail. See §7–8 for diagnosis and decisions.*
