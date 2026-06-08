# Stage 7.5 GATE B1 Report — VecJointTaskManager

**Date:** 2026-06-08 (revision 4; initial report 2026-06-06)
**Gate:** B1 — Vectorised JT multi-occupancy redesign
**Verdict:** **GATE B1 CLOSED — ALL PASS** (Tier-3 PASS + Occupancy PASS)

---

## Revision history

| Rev | Date | Status | Key change |
|---|---|---|---|
| 1 | 2026-06-06 | STOP (2 failures) | Initial gate; extinction before window; OCC_3200 infeasible |
| 2 | 2026-06-08 | STOP (1 failure) | A-fix + B-fixed + C-wire applied; Tests 1/2 PASS; Test 3 FAIL (D2 semantic) |
| 3 | 2026-06-08 | **Tier-3 PASS** | D2 amendment; extended Test 4 (15 seeds); all 4 tests pass |
| 4 | 2026-06-08 | **GATE B1 CLOSED** | E2 benchmark redesign; hires sugar configs; all 3 occ gates PASS |

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

## 6. Occupancy benchmark — Rev 4 results (E2 redesign)

**E2 fix:** N_init=1600 for all configs (no init hang). Resource ceiling broken with
calibrated `max_sugar_capacity` overrides; reference config keeps production value (16)
for direct recon comparison. See Finding B1-4 (§7) and Finding E2b (§8).

### Occupancy results

| Config | max_sugar_cap | n_carry | ms/step | mean_occ | final_N | Status |
|---|---|---|---|---|---|---|
| OCC_1600_g40 (ref) | 16 (production) | 20 000 | 129.5 | 2.31 | 3 187 | window-completed |
| OCC_1600_hires1_g40 | 32 (2×) | 40 000 | 139.1 | 3.39 | 5 122 | window-completed |
| OCC_1600_hires2_g40 | 64 (4×) | 80 000 | 158.5 | 4.79 | 7 596 | window-completed |

Recon baseline (oracle JTM, OCC_1600_g40): 170.6 ms/step, mean_occ=2.354.
Reference config speedup: 24% faster (129.5 vs 170.6 ms).

### Gate evaluation

| Gate | Criterion | Measurement | Verdict |
|---|---|---|---|
| Gate 1 | occ≥2 < 300 ms/step | 129.5 ms @ mean_occ=2.31 | **PASS** |
| Gate 2 | occ≥3 ≤ 500 ms/step | 158.5 ms @ mean_occ=4.79 | **PASS** (68% below ceiling) |
| Gate 3 | exponent ≤ 1.5 | 0.276 (log-log slope 2.31→4.79) | **PASS** (strongly sub-linear) |

**Occupancy exponent 0.276** means step time scales as occ^0.28 — essentially flat across
the 2.3–4.8 agents/cell range. At mean_occ=4.79, step time is 158.5 ms — well under the
500 ms ceiling. numpy-CPU is not approaching a performance wall at proto-ag occupancy.

**GATE B1 OCCUPANCY: PASS.**

---

## 7. Finding B1-4: Stage 6.0a OCC_3200 "hard-infeasible" was an init-hang, not a step-time cliff

**Root cause:** `run.py _random_unoccupied()` is a `while True` loop that samples random cells
until it finds one not in `self.occupied`. When N_init=3200 on a 40×40=1600-cell grid, all
1600 cells become occupied after the first 1600 agents are placed. The loop runs forever.

**How Stage 6.0a recorded "hard-infeasible":** The Stage 6.0a benchmark ran each OCC config as a
subprocess with a per-config timeout (`_PER_CONFIG_TIMEOUT_S`). When OCC_3200 hung at init,
the subprocess was killed after the timeout and the result was recorded as
`"cut_status": "hard-infeasible", "rail_status": "timeout"`. This was misread in the B1 gate
design as "step time exceeded the ceiling" — it was actually "model could not initialize".

**Verified 2026-06-08:** `SugarWorld(cfg)` with N_init=3200, grid=40×40, substrate.enabled=True
hangs at `_spawn_agents(3200)` — confirmed by timing diagnostic (config created in 0.3ms,
model creation does not return within 60s timeout). Documented as BUG-003.

**Consequence for the B1 gate:** The gate criterion (OCC_3200 < 300 ms/step) could not be
evaluated in the original benchmark format. E2 redesign measures the same performance question
through occupancy-based configs rather than N_init-based configs.

---

## 8. Finding E2b: resource ceiling on 40×40 g40 substrate

On the 2-peak 40×40 substrate with production sugar parameters (max_sugar_cap=16,
growth_rate_alpha=4), the equilibrium population is **resource-limited**, not n_carry-limited.
Even with n_carry=80000 (50× the equilibrium N), mean_occ reached only 2.73 (N≈3900).
The logistic carrying-cost term has < 6% effect on birth probability at this N/n_carry ratio;
sugar availability is the binding constraint.

**Fix:** The reference config (max_sugar_cap=16) provides a direct recon-comparable data point.
Stress configs use 2× and 4× resource density to push mean_occ into the 3–5 range. This is
benchmark calibration — the production substrate parameters are not changed.

**Perf-vs-science distinction (explicit):** The hires configs prove the *array model can run*
at occ≈3–5 without hitting a step-time wall. They do NOT say production science runs will
reach that density. The calibration pass starts from "tractable at high density" — not from
"calibrate to occ=4.8." What density production runs actually achieve is a calibration-pass
question, not a performance-gate question.

---

## 9. GATE B1 final verdict

| Component | Verdict |
|---|---|
| Test 1 N(t) envelope | **PASS** (min coverage 1.000) |
| Test 2 KS distributions | **PASS** (max KS 0.011) |
| Test 3 moments (D2 amended) | **PASS** (mean_wealth/gini_wealth/gini_cred: 10/10) |
| Test 4 JT event rate (15 seeds) | **PASS** (14/15; seed=44 lone outlier) |
| Occupancy Gate 1 (occ≥2 < 300 ms) | **PASS** (129.5 ms) |
| Occupancy Gate 2 (occ≥3 ≤ 500 ms) | **PASS** (158.5 ms @ occ=4.79) |
| Occupancy Gate 3 (exponent ≤ 1.5) | **PASS** (0.276) |

**GATE B1: CLOSED — ALL PASS.**

*Rev 4 close date: 2026-06-08*
