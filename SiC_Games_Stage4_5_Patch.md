# SiC Games — Stage 4.5 Patch Directive: T* + Si Pool Clarification

**Version:** 1.0
**Parent:** Stage 4.5 Blueprint (report_45.html received)
**Scope:** Two missing items from Stage 4.5 Task 4. No new mechanics.
**Output dir:** `outputs/stage45_seed42/` (append to existing)

---

## Item 1 — T* binary search for C

The blueprint required a T* search if C survived all seasonal conditions.
C survived all five conditions. The search was not run. Run it now.

**Protocol:** binary search on T (period), A=0.75 fixed (highest stress
condition where C/Si diverge). C survived [207,330] at A=0.75, T=200.
Increase T to find the period at which C first collapses.

| Run | A | T | Config |
|---|---|---|---|
| T*-1 | 0.75 | 400 | C only, all Stage 4.5 final params |
| T*-2 | 0.75 | 300 or 500 | Depends on T*-1 result — see below |
| T*-3 | 0.75 | bisect | Narrow to ±25 steps |

**Stopping rule:** run T*-1 at T=400. If C collapses: T* ∈ (200, 400) →
bisect at T=300 for T*-2. If C survives: T* > 400 → run T*-2 at T=500.
T*-3 narrows the bracket to ≤ ±25 steps. Report T* as a range, e.g.
"T* ∈ (325, 375)". Max 3 runs. If C survives T=500: report T* > 500 and stop.

All C configs: p_max=0.12, N_carry=400, alpha_carry=1.0, τ_pool=0.05,
λ=0.1, cluster_init=True, age_init_upper_frac=0.25, wealth_init_scale_k=True.
Seed=42.

**Do not run Si T\* search.** Si already collapses at T=200, A=0.75.
Its T* at A=0.75 is already bracketed as T* ∈ (50, 200) from the sweep
table. That is sufficient for Stage 5 sweep design.

---

## Item 2 — Si pool status check + conditional re-run

### Step 1: check the Task 4 configs (no new runs yet)

Read the config files used for the five Task 4 Si runs and confirm whether
`support_pool.enabled` was `true` or `false`. Report the value in §7.0.

### Step 2: conditional re-run

**If Si pool was ON in Task 4:** no re-run needed. The A=0.75 collapse
stands with pool support. Record "Si pool confirmed ON in Task 4 runs."

**If Si pool was OFF in Task 4:** re-run A=0.75, T=200, Si with pool ON
(τ_pool=0.05, ρ=0.3). One run only.

| Run ID | A | T | Si pool | Expected |
|---|---|---|---|---|
| T4_Si_A075_T200_pool | 0.75 | 200 | ON | Re-test collapse vs survive |

Report alongside the original A=0.75 Si result. If Si still collapses with
pool ON: collapse finding is robust. If Si survives: flag as a confound in
H1(ii) — C had pool active; Si did not in the original Task 4 run.

---

## Report addendum

Append **§7 (Patch)** to report_45.html. Three sub-sections:

### §7.0 — Si pool config check
State ON or OFF. Quote the config key and value directly.

### §7.1 — Si pool re-run (if applicable)
N(t) plot, collapse/survive verdict, dormancy_rate. State whether the
A=0.75 collapse finding is confirmed or overturned. If no re-run was
needed, write "Si pool confirmed ON — no re-run required."

### §7.2 — T* search
Table: A, T, N_late, collapse_step or "—". T* stated as range ≤ ±25
steps, or "T* > 500". Compare to Stage 4.3 T* if available in parquets.

### §7.3 — Pre-registered hypothesis H_cc
Include the following block verbatim:

---
**PRE-REGISTERED HYPOTHESIS — H_cc (carry_discount counter-cyclical
recovery)**

*Registered: Stage 4.5 patch, prior to Stage 5 multi-seed runs.*

The Stage 4.5 carrying-cost ceiling introduces an emergent counter-cyclical
birth boost: as N_C falls during a resource trough, carry_discount rises,
increasing effective birth probability. This was not an intended design
feature — it is an emergent consequence of the N-dependent discount.

**Hypothesis H_cc:** C's trough recovery speed (time from N_min back to
N_null_control equilibrium) is faster than the DTM birth formula alone
would predict, due to the carry_discount effect. This advantage scales
with trough depth (higher A) and trough duration (longer T).

**Test specification (Stage 5+):** Across multi-seed runs at A∈{0.5, 0.75,
0.9}, regress C trough recovery time on N_min/N_carry. H_cc predicts a
negative slope — deeper troughs recover proportionally faster relative to
a counterfactual without the ceiling. Recovery time is defined as steps
from N_min to first crossing of the null-control equilibrium midpoint.

**Status:** emergent finding from a single seed (seed=42). Held pending
Stage 5 full mechanics (co-evolutionary ψ, Si Cred, extended A sweep,
multi-seed ensemble). Not interpreted as confirmed until that stage.
---

---

## ROADMAP update

Append to the Stage 4.5 status row:
```
T* complete (see §7.2). Si pool Task 4 status confirmed.
H_cc pre-registered (Stage 4.5 patch). Ready for Stage 5.
```

Add a pre-registered hypotheses table if absent, with first entry:
```
| H_cc | carry_discount counter-cyclical C recovery | Stage 4.5 patch | Pending Stage 5 |
```

---

## Success criteria

| Criterion | Target |
|---|---|
| Si pool config confirmed from Task 4 files | ON or OFF with evidence |
| Si A=0.75 re-run (if pool was OFF) | Collapse confirmed or overturned |
| T* search complete | ≤3 runs, range ≤ ±25 steps or ">500" |
| §7 appended to report_45.html | All three sub-sections present |
| H_cc pre-registration text present verbatim | Confirmed in §7.3 |
| ROADMAP updated | Stage 4.5 row + H_cc table entry |
| No new mechanics | Confirmed |
| Test suite unchanged | 182/182 passing |

---

*End of Stage 4.5 Patch Directive*
