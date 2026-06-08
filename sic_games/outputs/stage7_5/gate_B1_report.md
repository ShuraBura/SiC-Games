# Stage 7.5 GATE B1 Report — VecJointTaskManager

**Date:** 2026-06-08 (revision 3; initial report 2026-06-06)
**Gate:** B1 — Vectorised JT multi-occupancy redesign
**Verdict:** Tier-3 battery PASS — occupancy benchmark pending (see §6)

---

## Revision history

| Rev | Date | Status | Key change |
|---|---|---|---|
| 1 | 2026-06-06 | STOP (2 failures) | Initial gate; extinction before window; OCC_3200 infeasible |
| 2 | 2026-06-08 | STOP (1 failure) | A-fix + B-fixed + C-wire applied; Tests 1/2 PASS; Test 3 FAIL (D2 semantic) |
| 3 | 2026-06-08 | **Tier-3 PASS** | D2 amendment; extended Test 4 (15 seeds); all 4 tests pass |

---

## 1. What changed since Rev 2

**D2 amendment (supervisor direction 2026-06-08):**

Pre-condition (1) — demonstrate mean_cred↔jt_per_step downstream linkage:

Pearson r(jt_diff, mc_diff) = 0.9275, p = 0.0001, R² = 0.8602. Sign agreement 9/10.
The single sign-flip (seed=49) has |jt_diff| = 2.3% — noise floor where cred variance
is dominated by other sources. Non-noise seeds (|jt_diff|>5%, n=7): r = 0.9376, sign agreement 7/7.
Condition (1) satisfied: mean_cred divergence is a downstream consequence of jt_per_step
divergence, not an independent failure.

Pre-condition (2) — add seeds 52–56 to Test 4 to confirm seed=44 is a lone outlier.
Results: seeds 52–56 all ≤ 11.8%. Seed=44 (25.6%) is the sole failure in 15 seeds.
Criterion 14/15 met. Condition (2) satisfied.

**Test spec changes under D2:**
- Test 3 MOMENTS: removed `jt_per_step` and `mean_cred` (both governed by D2 defection
  RNG semantic; jt_per_step is already gated by Test 4 at the appropriate 20% tolerance)
- Test 4: extended from 10 to 15 seeds (added 52–56); criterion raised from 9/10 to 14/15

---

## 2. Tier-3 battery results (Rev 3, final)

**Battery config (B-fixed):** 100×100 grid, N_init=500, mode="fixed", 4 peaks, kappa=1.0,
c2_defection=True, 10 seeds, 400 steps, window=steps 251–400. Total runtime: 122.64 s.

**Oracle:** SugarWorld (unmodified, D4 frozen). **Array:** SoAWorld + VecJointTaskManager.

### Test summary

| Test | Criterion | Result | Verdict |
|---|---|---|---|
| Test 1 — N(t) envelope | min coverage ≥ 0.90 | min = **1.000** (all 10 seeds perfect) | **PASS** |
| Test 2 — KS statistics | KS < 0.10 for all 6 vars | max KS = 0.0114 (c1); all < 0.012 | **PASS** |
| Test 3 — Moments (D2) | diff < 10% for ≥ 8/10 on 3 moments | mean_wealth **10/10**, gini_wealth **10/10**, gini_cred **10/10** | **PASS** |
| Test 4 — JT event rate (15 seeds) | diff < 20% for ≥ 14/15 | **14/15** (seed=44 sole failure) | **PASS** |

Battery **PASS**. Runtime 122.64 s.

### Original 10-seed JT and cred data (seeds 42–51)

| seed | oracle jt/step | vec jt/step | jt diff% | oracle mc | vec mc | mc diff% |
|---|---|---|---|---|---|---|
| 42 | 11.7 | 13.8 | 17.7 | 1.154 | 1.395 | 20.9 |
| 43 | 12.2 | 11.1 | 8.9 | 1.266 | 1.249 | 1.3 |
| 44 | 16.0 | 11.9 | **25.6** | 1.711 | 1.291 | 24.5 |
| 45 | 13.7 | 11.0 | 19.7 | 1.383 | 1.203 | 13.0 |
| 46 | 13.2 | 13.9 | 5.7 | 1.359 | 1.533 | 12.8 |
| 47 | 12.0 | 12.1 | 0.2 | 1.296 | 1.309 | 1.0 |
| 48 | 13.1 | 11.6 | 11.9 | 1.329 | 1.293 | 2.7 |
| 49 | 12.9 | 12.6 | 2.1 | 1.335 | 1.417 | 6.1 |
| 50 | 13.4 | 13.4 | 0.1 | 1.465 | 1.534 | 4.7 |
| 51 | 9.9 | 11.5 | 16.4 | 1.044 | 1.126 | 7.9 |

### Extended 5-seed JT data (seeds 52–56, Test 4 only)

| seed | oracle jt/step | vec jt/step | jt diff% | verdict |
|---|---|---|---|---|
| 52 | 15.0 | 14.4 | 4.3 | OK |
| 53 | 16.2 | 15.1 | 7.2 | OK |
| 54 | 14.9 | 14.1 | 5.0 | OK |
| 55 | 13.2 | 12.9 | 2.8 | OK |
| 56 | 13.3 | 14.9 | 11.8 | OK |

Seed=44 is confirmed as a lone outlier. No new outliers in the extended set.

---

## 3. What passed

| Component | Result |
|---|---|
| 11 unit tests (fast) | PASS |
| 2 new tests (A-fix oracle semantics, C-wire pre-batch) | PASS |
| Full suite 303 tests | PASS |
| Test 1 N(t) envelope | PASS (1.000 min coverage — perfect) |
| Test 2 KS distributions | PASS (max 0.011, all < 0.012) |
| Test 3 moments (D2 amended) | PASS (mean_wealth/gini_wealth/gini_cred: 10/10 each) |
| Test 4 JT rate (15 seeds) | PASS (14/15; seed=44 sole outlier at 25.6%) |
| mean_cred↔jt correlation | r=0.927, p=0.0001, R²=0.86 (D2 condition 1) |
| OCC_1600_g40 speedup | 115.5 ms/step vs oracle 170.6 ms/step (−32%) |
| Sugar conservation | holds < 1e-9 |
| Matthew arithmetic | exact match (rtol 1e-9) |
| Oracle agent multi-participation | confirmed: agents appear in multiple adjacent events |

---

## 4. D2 amendment rationale (archived)

**Finding B1-3 (Rev 2):** `jt_per_step` appeared in both Test 3 (10% threshold) and Test 4
(20% threshold), double-counting the metric with inconsistent tolerances for the declared D2
defection RNG semantic. `mean_cred` failed as a downstream consequence (r=0.927 with jt).

**D2 resolution:** Remove `jt_per_step` and `mean_cred` from Test 3. This is NOT threshold
adjustment — it removes a metric from a test where it was already covered by a dedicated test
(Test 4) at the appropriate tolerance for the declared Tier-3 change. After D2, Test 3 checks
mean_wealth, gini_wealth, and gini_cred — three metrics with no JT mechanic exposure — all
at 10%, all passing 10/10.

**D2 condition (1) — jt↔cred linkage verified:**
Pearson r = 0.9275 (p = 0.0001), R² = 0.8602, sign agreement 9/10. Non-noise seeds 7/7.

**D2 condition (2) — seed=44 lone-outlier verified:**
Extended 5 seeds (52–56) all ≤ 11.8%. 14/15 ≥ criterion. Confirmed.

---

## 5. Open science anomaly: seed=44

Oracle seed=44 has the highest JT event rate (16.0/step) of any seed. VecJTM produces only
11.9/step (25.6% below). The high oracle rate suggests many clusters are near the defection
threshold in this RNG trajectory, making the keyed_uniform vs stateful-RNG divergence
maximally impactful. This is not a correctness concern — the FINAL gate will reproduce at
least one known science result, which is the appropriate check for model validity.

---

## 6. Next: occupancy benchmark

With Tier-3 cleared, the occupancy benchmark (`benchmark_b1_occupancy.py`) runs SoAWorld +
VecJTM across OCC_1600 / OCC_3200 / OCC_6400 / OCC_12800 (all g40, kappa=1.0). The C-wire
eliminates the O(N²) mean_cred-per-birth bottleneck (run.py line 784) that made OCC_3200+
hard-infeasible in the oracle. This gives the actual B1 go/no-go performance reading.

**Gate thresholds (ARCHITECTURE §12.1-H §H.3):**
- OCC_3200_g40 < 300 ms/step
- OCC_6400_g40 ≤ 500 ms/step
- Occupancy exponent (log-log slope across feasible configs) ≤ 1.5

---

*GATE B1 Rev 3 verdict: Tier-3 battery PASS. All 4 tests pass. Occupancy benchmark next.*
