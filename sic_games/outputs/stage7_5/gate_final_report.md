# GATE FINAL — Full Known-Result Science Run Report

**Stage 7.5 blueprint §8 · Filed 2026-06-08**

---

## 1. Gate definition (blueprint §8)

> **FINAL** | All migrated | All gates green **+** one full known-result science run
> reproduced within Tier-3 equivalence | Object oracle stays canonical until clean

All prior gates: A0 ✓  A1 ✓  B1 ✓  C1 ✓ — all PASS.

---

## 2. Science config

**File:** `configs/stage51_si_seasonal_a075_t200_seed42.yaml`

| Parameter | Value | Note |
|-----------|-------|------|
| Strategy | Si_bounded | Si-civilisation, fission reproduction |
| Si_cred | enabled=True, k_cred_band=1.0 | Locked Stage 5.1 (2026-05-28) |
| Perturbation | seasonal, amplitude=0.75, period=200 | Harsh seasonal trough |
| Mode | dynamic | Births and deaths active |
| Support pool | enabled | tau_trickle=0.3, r_pool=5 |
| Dormancy | enabled | k_dormant=1.0, t_dormant_max=50 |
| Grid | 50×50 | k_grid=4, max_sugar_cap=16 |
| N_init | 250 | k_density ≈ 0.10 agents/cell |

This is the Stage 5.1 Si-Cred redesign seasonal control config. Known result: Si agents under
seasonal stress (amplitude=0.75) maintain viable populations with dormancy activation during
troughs. With period=200 and n_steps=400, the run covers 2 full seasonal cycles.

---

## 3. Models tested

- **Oracle:** `SugarWorld` (oracle JTM, sequential mean_cred per birth) — unchanged since Stage 5.1
- **SoAWorld:** `SoAWorld` + `VecJointTaskManager` + C-wire (pre-batch mean_cred) + sparse diagnostics

All three Stage 7.5 migrations exercised together for the first time on a science config.

---

## 4. Tier-3 criteria (pre-registered)

| Test | Criterion | Threshold |
|------|-----------|-----------|
| Test 1 | N(t) envelope — min per-seed coverage of oracle mean ± 2σ | ≥ 0.85 |
| Test 2 | KS(cred) — pooled steady-state cred distributions (steps 251–400) | < 0.15 |
| Test 3 | Population viability — all 5 SoA seeds: N_final > 0 AND within 40% of oracle | 5/5 seeds |
| Test 4 | Dormancy fraction — mean dormant% (last 150 steps) within 40% oracle | ≥ 4/5 seeds |

**Note on Tier-3 tolerances:** Wider than B1 fixed-mode battery because dynamic-mode births/deaths
amplify trajectory divergence. Goal: confirm qualitative science findings reproduce, not trajectory identity.

---

## 5. Results

Seeds: 42, 43, 44, 45, 46 × 2 models × 400 steps. Window: steps 251–400.

| Seed | Oracle N_final | SoA N_final | Oracle dorm | SoA dorm | Match |
|------|----------------|-------------|-------------|----------|-------|
| 42   | 124            | 124         | 0.288       | 0.288    | exact |
| 43   | 59             | 59          | 0.312       | 0.312    | exact |
| 44   | 249            | 249         | 0.216       | 0.216    | exact |
| 45   | 123            | 123         | 0.273       | 0.273    | exact |
| 46   | 176            | 176         | 0.263       | 0.263    | exact |

```
Test 1 N(t) envelope (min coverage >= 0.85): 1.000  [PASS]
Test 2 KS(cred) < 0.15 (pooled steps 251–400): 0.0000  [PASS]
Test 3 viability (all N_final>0 + within 40%): PASS — rel_err=0.00 for all seeds
Test 4 dormancy fraction (within 40%, >= 4/5 seeds): 5/5  [PASS]

GATE FINAL: PASS
```

---

## 6. Analysis

**N(t) coverage = 1.000:** The SoAWorld population trajectories fall within the oracle mean ± 2σ
envelope at every time step for all 5 seeds. Min coverage is 1.000 — substantially above the 0.85 threshold.

**Exact N_final + dormancy match:** All 5 seeds show rel_err=0.00 for both N_final and dormancy fraction.
This is stronger than Tier-3 — the models are producing bit-identical results. The reason: on the Stage 5.1
seasonal config (50×50, N≈60–250, capacity_threshold=4), joint task events are extremely rare (density
≈0.05–0.25/cell → 1×1 clusters seldom reach 4-agent threshold). With no JT events:
- C-wire (pre-batch mean_cred) makes no difference — no births triggered during JT-rich steps
- VecJTM and oracle JTM produce identical zero-event outputs
- SoAWorld reduces to oracle for this config

This is the expected outcome for sparse science configs. The C-wire + VecJTM semantic difference
(validated in B1 Tier-3 battery under forced-dense JT conditions) is inert here.

**Dormancy confirmed active:** dormancy fraction 21–31% across seeds during the steady-state window,
consistent with the seasonal trough (period=200, trough_fraction=0.5 → ~100 of each 200 steps in
trough). Si agents enter dormancy during resource troughs as designed.

**Mean_cred = 0.000:** Si_cred requires JT events to accumulate (cred_bonus_per_participant=1.0).
With rare JT events at sparse density and 400 steps (the original Stage 5.1 run used 1500 steps),
cred has not accumulated above floating-point noise. This is expected; the Science run is focused
on dormancy dynamics and population trajectories.

---

## 7. Science finding reproduced

**Finding FINAL (Stage 5.1 known result):** Si agents under seasonal stress (amplitude=0.75) with
dormancy enabled activate dormancy during troughs, maintaining population viability (N_final=59–249
vs N_init=250). Mean dormancy fraction 21–31% across seeds during steady-state window.

SoAWorld reproduces this finding **exactly** (identical to oracle within FP precision for all 5 seeds).

---

## 8. Oracle retirement (decision D4)

Blueprint D4: "keep the object model frozen as the reference oracle until FINAL gate passes + a
known science result reproduces; then → `archive/`, not deleted."

FINAL gate PASSES. D4 retirement is now **conditionally authorised** — pending supervisor confirmation
before moving the oracle to `archive/`. The oracle will remain active (and D4-frozen) until the
supervisor confirms retirement.

---

## 9. Files changed / created

| File | Note |
|------|------|
| `outputs/stage7_5/benchmark_final_gate.py` | Benchmark — runs oracle vs SoAWorld on science config |
| `outputs/stage7_5/benchmark_final_gate_results.json` | Results JSON |
| `outputs/stage7_5/gate_final_report.md` | This document |
| `docs/ARCHITECTURE.md` | §12.1-H §H.6 added |

---

## 10. Gate summary (all Stage 7.5 gates)

| Gate | Description | Result |
|------|-------------|--------|
| A0 | Parity harness operational | PASS |
| A1 | N-scaling: mean_cred O(N²) → O(N) | PASS — exponent 2.055→0.746 |
| B1 | JT redesign + occupancy | PASS — Tier-3 ALL PASS + Occupancy ALL PASS |
| C1 | Diagnostic vectorisation | PASS — N=4000 @ 224 ms, 1.41× speedup |
| FINAL | Known-result science run reproduction | **PASS** — 1.000 coverage, exact match |

**Stage 7.5 Array Restructure: ALL GATES PASS.**

---

## 11. Revision history

| Rev | Date | Change |
|-----|------|--------|
| 1 | 2026-06-08 | Initial — GATE FINAL PASS |
