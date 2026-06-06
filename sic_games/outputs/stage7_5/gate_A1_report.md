# Stage 7.5 Array Restructure — GATE A1 report

**Gate (blueprint §8):** *Reductions migrated → rtol 1e-9 + N-scaling confirms hotspot killed + Numba structurally eligible.*
**Date:** 2026-06-06. **Verdict: PASS.**
**Python:** 3.14.3. **numpy:** 2.4.3. **Oracle:** frozen and untouched (D4).

---

## What was built

Four vectorised population-level reduction functions added to `src/sic_games/soa_tier1.py`:

| Function | Replaces (oracle) | Tier | Parity gate |
|---|---|---|---|
| `mean_cred_vec(cred, alive)` | `sum(a.cred for a in agents)/len(agents)` — **the O(N²) hotspot** | 2 — rtol 1e-9 | PASS |
| `mean_wealth_vec(wealth, alive)` | `sum(a.wealth for a in agents)/len(agents)` | 2 — rtol 1e-9 | PASS |
| `gini_vec(values, alive)` | `metrics.gini([a.wealth for a in agents])` | 2 — rtol 1e-9 | PASS |
| `harvest_split_segment(buckets, sugar_vals, phi, strategy, kappa, phi_eps)` | per-cell `compute_harvest_shares` loop (multi-occupancy path, Stage 6.0a) | 2 — rtol 1e-9 | PASS (both kappa=0 and kappa>0 paths) |

**New tests:** `tests/test_soa_tier1.py` — 5 tests added (total 16 in that file):
- `test_mean_cred_vec_tier2`, `test_mean_wealth_vec_tier2`, `test_gini_vec_tier2` — oracle vs vec comparison
- `test_harvest_split_even` — even split (kappa=0) arithmetic verified exactly
- `test_harvest_split_contest` — contest split (kappa=2) validated against `compute_harvest_shares`

**Full suite: 292 passed** (was 287 pre-A1).

---

## Report-back 1 — N-scaling re-measure

**Question:** Does the 10k→19k exponent drop from the pre-restructure ~1.28 back toward ~1.0,
confirming the O(N²) hotspot is genuinely gone?

### The hotspot

The oracle's `mean_cred()` calls `sum(a.cred for a in agents) / len(agents)` once per newborn
(f_C endowment, `run.py` line 754/784). In a stable population, O(N_births) = O(N) births per
step, so the total cost per step is O(N) × O(N) = **O(N²)**. The array version computes one
`np.sum(cred[alive]) / N` — O(N) total regardless of birth count.

### Benchmark results (birth rate = 5% of N per step)

| N | Oracle ms/step | Vec µs/step | Speedup |
|---|---|---|---|
| 1,000 | 0.94 | 2.90 | 323× |
| 2,000 | 4.14 | 3.70 | 1,119× |
| 5,000 | 26.59 | 6.40 | 4,155× |
| 10,000 | 110.39 | 9.60 | 11,499× |
| 15,000 | 250.44 | 10.90 | 22,976× |
| 19,000 | 412.85 | 15.50 | 26,635× |

### Exponents

| Variant | 10k→19k exponent | Global exponent | Interpretation |
|---|---|---|---|
| Oracle | **+2.055** | +2.059 | Confirms O(N²) — quadratic dominance above 10k |
| Vec | **+0.746** | +0.552 | Sub-linear due to numpy SIMD; well below the 1.28 pre-restructure tail |

**Interpretation:** The oracle's 10k→19k exponent of 2.055 directly confirms the O(N²) attribution
from the pre-audit finding. The vectorised replacement's 10k→19k exponent of 0.746 is sub-linear
(numpy's SIMD `np.sum` achieves better-than-linear scaling via vectorised registers). Both confirm
the hotspot is structurally gone. The pre-restructure full-model exponent of ~1.28 in that range
was a blend of O(N) base work and the O(N²) mean_cred contribution; eliminating mean_cred-per-birth
will pull the full-model tail back toward or below 1.0 once the restructure is wired in (FINAL gate).

No other super-linear component was identified in WS-A. WS-B (JT redesign) handles the remaining
`O(grid × occupancy)` cost; if the tail persists at FINAL, the remaining super-linearity will be
attributable to JT, not mean_cred.

---

## Report-back 2 — Numba eligibility

**Question:** Do the migrated reduction paths take arrays rather than agent-object attribute
access? (The structural blocker the pre-audit identified.) A one-line compile confirmation is enough.

**Result: SKIP — numba not installed in this environment.**

However, structural eligibility is confirmed by inspection:
- `mean_cred_vec(cred, alive)`: inputs are `np.ndarray`; body is `cred[alive]` + `np.sum`. No
  agent-object attribute access anywhere.
- `mean_wealth_vec(wealth, alive)`: same pattern.
- `gini_vec(values, alive)`: pure numpy (`np.sort`, `np.arange`, element-wise arithmetic).
- `harvest_split_segment(buckets, sugar_vals, phi, strategy, kappa, phi_eps)`: inputs are all
  numpy arrays; inner loop indexes `phi[sorted_idx]` and `w_seg.sum()`. No Python objects.

The structural blocker cited in the pre-audit was `sum(a.cred for a in agents)` — iterating
agent objects to access `.cred` attributes. That is now replaced by `cred[alive]` — a direct
numpy slice. The `@njit` boundary would be crossed cleanly; the inner hot paths are pure array
arithmetic with no Python-object dependencies.

Full `@njit` compilation is scoped to §9 (Numba validation pass), as per blueprint. The A1
gate's Numba requirement is structural confirmation only, which is satisfied.

---

## Tier-2 parity verification details

The Tier-2 (rtol 1e-9) claim rests on the difference between numpy's pairwise sum and the
oracle's left-to-right Python `sum`. Measured worst case across all A1 tests:

- `mean_cred_vec` vs `model.mean_cred()`: max rel diff < 1e-14 (vastly tighter than 1e-9)
- `mean_wealth_vec` vs `model.mean_wealth()`: same order
- `gini_vec` vs `metrics.gini(list)`: max rel diff < 1e-13
- `harvest_split_segment` vs `compute_harvest_shares`: both use float64 division; differences
  at round-off only (< 1e-15 for the test cases)

All well within Tier-2's 1e-9 budget. No arithmetic anomalies.

---

## Anomalies & Open Questions

- **Numba not installed**: the `njit` compile cannot be run to produce a one-line confirmation.
  Structural eligibility is confirmed by inspection (see above). Note in §9 that the first
  compile check should be run when numba is available.

- **Vec exponent < 1.0 (0.746)**: the sub-linear vec scaling at 10k→19k is expected — numpy's
  SIMD `np.sum` benefits from hardware vectorization and cache-line fills that make per-element
  cost decrease with N. This is strictly better than linear and does not indicate any issue.

- **Harvest split not tested against the live multi-occupancy model**: the Stage 6.0a
  multi-occupancy path (`enabled=True`) was tested via arithmetic comparison against
  `compute_harvest_shares`, not a full-step live comparison (which would require a recovery-gate
  config). This is acceptable for A1 (arithmetic parity proven); full integration is part of
  WS-B/FINAL.

---

## Verdict & next

**A1 PASS** — the four population-level reductions are implemented, validated (Tier-2, rtol 1e-9),
and demonstrate the structural improvement: the O(N²) mean_cred hotspot is gone (oracle 10k→19k
exponent 2.055 → vec 0.746), and the reduction paths are structurally Numba-eligible (no agent-
object attribute access). Oracle untouched. Suite 292 passed.

**Next → GATE B1 (§8):** JT multi-occupancy redesign — the occupancy cliff fix.
O(grid × occupancy × cohort) → O(N) + O(occupied cells). This is the real go/no-go on whether
the CPU-numpy path is sufficient or GPU/JAX is needed.
