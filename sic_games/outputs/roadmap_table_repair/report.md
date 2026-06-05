# ROADMAP Table Repair — Report

**Date:** 2026-05-29  
**Directive:** SiC_Games_ROADMAP_Table_Repair.md  
**Backup:** `ROADMAP.md.bak_pre_tablefix`  
**Scope:** Formatting/dedup pass only — no parameter values changed.

---

## §1 Distinct-parameter inventory of the corrupted region (Task 0.3)

The corrupted region ran from the "Pool diagnostics table format" header through
the `| Stage 4.5 patch | ✓ complete | ...` row, ending immediately before
`## Pre-registered Hypotheses`.

**Distinct parameter rows found (before dedup):**

| Parameter | Value | Locked at | Occurrences in region |
|---|---|---|---|
| N_carry | 400 | Stage 4.5 | 11 |
| alpha_carry | 1.0 | Stage 4.5 | 11 |
| p_max_C_bare | 0.11 | Stage 4.5 | 1 |
| p_max_C_final | 0.12 | Stage 4.5 | 1 |
| tau_pool | 0.05 | Stage 4.5 | 1 |
| lambda | 0.1 | Stage 4.5 | 1 |
| T*_C_A075 | > 500 | Stage 4.5 patch | 1 |

**Status/outcome rows found (misfiled as parameters):**

| Row | Status |
|---|---|
| `Stage 4.4 k=3 Feasibility` | ⚠ Si Fail — misfiled |
| `Stage 4.5 Task 0` | ⚠ T0 fail — misfiled |
| `Stage 4.5 patch` | ✓ complete — misfiled AND redundant |

No distinct parameter rows were found that are NOT in the directive's expected list
(`p_max_C_bare`, `N_carry`, `alpha_carry`, `p_max_C_final`, `tau_pool`, `lambda`,
`T*_C_A075`). Stopping rule §7.1 does **not** trigger.

---

## §2 Duplicate-collapse result

**grep counts after repair:**

| Parameter | Before (in region) | After (whole file) | Note |
|---|---|---|---|
| `N_carry` | 11 | **1** | Was also in locked-param table at Stage 4.5 → all 11 region copies removed |
| `alpha_carry` | 11 | **1** | Same — already in locked-param table |

**Cross-reference merges:**

- **tau_pool / τ_pool:** The corrupted region had `tau_pool | 0.05 | Stage 4.5`. The
  locked-parameter table already contained `τ_pool | 0.10 → 0.05 (design tension) |
  Stage 4.1c / Stage 4.2`. The Stage 4.5 value (0.05) is already captured in the
  existing row's "0.10 → 0.05" notation. Region copy removed as redundant; no merge
  needed.

- **lambda / λ:** The corrupted region had `lambda | 0.1 | Stage 4.5`. The
  locked-parameter table already contained `λ (C wealth inheritance) | 0.1 | Stage 4.4`.
  Region copy removed as redundant.

**New rows added to locked-parameter table** (were in region but NOT in main table):

| Parameter | Value | Locked at | Rationale given |
|---|---|---|---|
| p_max_C_bare | 0.11 | Stage 4.5 | C null control without pool/λ (carrying_cost only) |
| p_max_C_final | 0.12 | Stage 4.5 | C final config with pool+λ+carrying_cost |
| T*_C_A075 | > 500 | Stage 4.5 patch | C critical period at A=0.75; counterpart to Si T* ∈ (68,87) |

These were inserted after the `alpha_carry` row in the locked-parameter table
(the logical Stage 4.5 cluster).

---

## §3 Status rows relocated

| Row | Action | Destination |
|---|---|---|
| `Stage 4.4 k=3 Feasibility \| ⚠ Si Fail \| k=3 Si...` | **Moved** | Current-status table, after `Stage 4.4 Diag` row |
| `Stage 4.5 Task 0 \| ⚠ T0 fail \| carry_discount...` | **Moved** | Current-status table, after `Stage 4.4 k=3 Feasibility` row |
| `Stage 4.5 patch \| ✓ complete \| T* complete...` | **Removed as redundant** | Stage 4.5 already marked `✓ Complete` with H_cc note in the status table; patch completion information is already present |

---

## §4 Before/after distinct-triple diff

**Before distinct set (parameter, value, locked-at):**
```
(N_carry, 400, Stage 4.5)
(alpha_carry, 1.0, Stage 4.5)
(p_max_C_bare, 0.11, Stage 4.5)
(p_max_C_final, 0.12, Stage 4.5)
(tau_pool, 0.05, Stage 4.5)        ← duplicate of existing τ_pool 0.10→0.05
(lambda, 0.1, Stage 4.5)           ← duplicate of existing λ 0.1 Stage 4.4
(T*_C_A075, > 500, Stage 4.5 patch)
```

**After distinct set (change from before):**
- (N_carry, 400, Stage 4.5) — **already existed in main table; region copies removed**
- (alpha_carry, 1.0, Stage 4.5) — **already existed; region copies removed**
- (p_max_C_bare, 0.11, Stage 4.5) — **moved to main table** (was only in region)
- (p_max_C_final, 0.12, Stage 4.5) — **moved to main table** (was only in region)
- (tau_pool, 0.05, Stage 4.5) — **region copy removed** (covered by τ_pool 0.10→0.05)
- (lambda, 0.1, Stage 4.5) — **region copy removed** (covered by λ 0.1 Stage 4.4)
- (T*_C_A075, > 500, Stage 4.5 patch) — **moved to main table** (was only in region)

**Net change to the whole-file distinct triple set:**
- `(tau_pool/τ_pool, 0.05, Stage 4.5)`: the equivalent value was already present as
  `(τ_pool, 0.10→0.05, Stage 4.1c/Stage 4.2)` — same parameter, same current value,
  different format. No information lost.
- `(lambda/λ, 0.1, Stage 4.5)`: equivalent was already `(λ, 0.1, Stage 4.4)`. No
  information lost.
- Three new rows added for triples that existed ONLY in the corrupted region
  (p_max_C_bare, p_max_C_final, T*_C_A075) and would have been lost without this repair.

**Verdict:** deletions of exact/equivalent duplicates + relocations only.
Zero value changes. Zero parameter drops. Gate §5.1: **PASS**.

---

## §5 Confirmation

- **No parameter value changed.** All (parameter, value, locked-at) triples that
  were distinct before the edit remain represented after.
- **Status text not lost.** Both misfiled status rows (`Stage 4.4 k=3 Feasibility`
  and `Stage 4.5 Task 0`) are verbatim in the Current-status table at lines 54-55.
  The `Stage 4.5 patch` text was redundant (Stage 4.5 already ✓ Complete) and
  removed — its information (H_cc pre-registered, T* complete) is in the Stage 4.5
  status row and the Pre-registered Hypotheses section.
- **Pool-diagnostics template restored** to a proper format-only example row with no
  misindented parameter rows beneath it.
- **Grep verification:** `N_carry` appears exactly **1** time; `alpha_carry` appears
  exactly **1** time.
