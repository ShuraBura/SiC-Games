# Stage 7.5 Array Restructure — GATE A0 report

**Gate (blueprint §8):** *Harness + Tier-1 migrated → bit-identical on per-agent updates.*
**Date:** 2026-06-06. **Verdict: PASS** (with one classification refinement — σ is Tier-2, see below).
**numpy:** 2.4.3. **Oracle:** the object model (`run.py`) is frozen and untouched (decision D4).

---

## What was built

**Infrastructure (§4.1.1, §2, §7):**
- `src/sic_games/soa.py` — Structure-of-Arrays `AgentArray` (explicit column schema mirroring
  `BaseAgent`), the **D2** counter-based per-agent-keyed RNG (`keyed_uniform`, splitmix64;
  order-independent), the **D3** capacity + alive-mask + `alloc/kill/compact` birth-death
  machinery, and the **cell-bucket primitive** (`bucket_by_cell` → `CellBuckets`).
- `src/sic_games/parity.py` — the equivalence harness: `snapshot()` + `compare()` diff two
  snapshots per-column at the declared tier (bit / rtol 1e-9 / statistical-skip), aligned by
  `unique_id` (order-independent). `assert_identity()` proves the snapshot+diff path.

**Tier-1 per-agent updates migrated (§4.1 step 2):** `src/sic_games/soa_tier1.py`.

| Mechanic | Function | Tier | Gate result |
|---|---|---|---|
| Cred decay + pending flush (C) | `cred_decay` | 1 — bit | ✅ bit-identical |
| Metabolize C/greedy (cost/wealth/velocity-EMA/age/alive) | `metabolize_basic` | 1 — bit | ✅ bit-identical |
| Si Cred near-dormancy band accumulation | `si_cred_band` | 1 — bit | ✅ bit-identical |
| η(a) age-efficiency ramp | `eta` | 1 — bit | ✅ bit-identical |
| Si dormancy-aware metabolize state machine | `metabolize_si_dormancy` | 1 — bit | ✅ bit-identical (all 7 branches + k_carry) |
| Decision σ (C): σ_base+κ·tanh(𝒞/C*) | `temperature_carbon` | **2 — rtol 1e-9** | ✅ within 1e-12 |
| Decision σ (Si): σ_Si_eff = σ_Si+κ_Si·tanh(si_cred/C*) | `temperature_si` | **2 — rtol 1e-9** | ✅ (κ_Si=0 path is bit-identical) |

**Validation:** `tests/test_soa.py` (12) + `tests/test_parity.py` (8) + `tests/test_soa_tier1.py` (11).
Per-mechanic parity is asserted against the frozen oracle: bit-identical (`np.array_equal`) for the
arithmetic updates; rtol 1e-9 for σ; one end-to-end metabolize check through `parity.compare()`.
**Full suite: 287 passed** (was 256 pre-Stage-7.5).

---

## Finding — σ is Tier-2, not Tier-1 (refines blueprint §3)

Blueprint §3 listed the σ formula under Tier-1 (bit-identical). Empirically, on numpy 2.4.3 here,
**`np.tanh` is not bit-identical to Python `math.tanh`** — it differs by up to ~1 ULP (max relative
2.2e-16). (`np.exp` *is* bit-identical, so the stress sigmoid is unaffected.) Computing σ with
vectorised `np.tanh` is therefore **Tier-2 (rtol 1e-9)** — it clears the 1e-9 gate with ~10⁷ margin
but is not bit-identical without applying tanh scalar-wise (which forfeits vectorisation, the point of
the rewrite). The genuinely pure-arithmetic per-agent updates remain true Tier-1. Logged: ARCHITECTURE
§12.1-G. The ~1-ULP σ shift feeds a softmax; a vanishingly-rare movement-tie flip is folded into the
Tier-3 statistical battery at the full-model (FINAL) gate.

---

## Verdict & next

**A0 PASS** — the harness runs oracle-vs-array and diffs per column; the per-agent independent
updates reproduce the oracle (bit-identical for arithmetic; 1e-9 for σ). No harness bug.

**Next → GATE A1 (§8):** migrate the reductions — `mean_cred` (→ cached column-mean, **the O(N²)
hotspot dies here**), `mean_wealth`, harvest-split (segment-sum over the cell-bucket primitive),
Gini — at Tier-2 (rtol 1e-9); then re-measure N-scaling (expect ~linear; Numba structurally eligible).
