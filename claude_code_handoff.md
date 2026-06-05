# SiC Games — Claude Code Session Handoff

**Paste this as the first message in a new Claude Code session.**

---

## Context

You are resuming the SiC Games simulation project. The previous session
completed a performance optimisation pass. The model is at v5.1-postaudit-clean.
All tests pass. Science is unchanged. You are ready to begin Stage 5.x work.

---

## What was just done (previous session)

- **Performance optimisation pass complete.** Three fixes applied and verified:
  - `c_spatial_density` now computed every 10 steps (diagnostic metric only)
  - `_moran_W` / Moran's I now computed every 10 steps (diagnostic metric only)
  - `_carbon_birth` partner scan replaced with spatial hash + sort-by-id
- **One fix reverted:** `mean_cred()` cache in birth loop — semantics depend on
  running mean including zero-Cred newborns; pre-caching changes science. Deferred.
- **All 201 tests pass.** Equivalence gate: bit-identical for Tasks 2, 3, 4.
- **Backup written:** `G:\My Drive\docs\SiC Games\Model\v5.1_2026-05-28_0637`

---

## Current performance

| Config | Grid | N | ms/step |
|---|---|---|---|
| B0 | 50×50 | 250 | 12.5 |
| B1 | 100×100 | 500 | 53.0 |
| B3 | 150×150 | 1000 | 140.7 |
| B5 | 200×200 | 1500 | 214.7 |

All B0–B5 LHS-feasible. Working grid for Stage 5.x: 100×100.

---

## Model state

- **Tests:** 201 passing
- **Grid:** 50×50 toroidal, k_grid=4 (max_sugar=16, growback_alpha=4)
- **C mechanics:** softmax + Cred-coupled σ, joint task (spatial hash),
  biparental repro, pool, λ=0.1, carry_discount ceiling (N_carry=400)
- **Si mechanics:** dormancy, fission, Si Cred (surplus-based, active),
  Si pool (enabled)
- **Metrics sampling:** c_spatial_density every 10 steps, Moran's I every 10 steps
- **No git repo** — use directory backups

---

## Key constraints (from CLAUDE.md — read that file too)

1. Never change science without explicit supervisor approval.
2. Numerical equivalence gate after every code change.
3. Full test suite (201) must pass after every change.
4. Implement + test before running any simulation.
5. Apply changes one at a time; verify between each.
6. Report every run with actual numbers — no PASS/FAIL without values.

---

## Locked parameters (do not change)

k_grid=4, β_Si=5.0, p_fission_Si=0.28, p_max_C=0.12, N_carry=400,
α_carry=1.0, τ_pool=0.05, ρ=0.3, λ=0.1, σ_Si=1.238, κ=2.0, α=2.0,
β=1.0, f_C=0.25, σ_inherit=0.05, age_init_upper_frac=0.25,
wealth_init_scale_k=True, cluster_init=True (C only, peak_index=0, r=10),
T_dormant_max=50, k_dormant=1.0, τ_trickle=0.05, k_reactivate=3.0,
r_cred_Si=0.1, κ_Si=0.5, C*_Si=10.0, k_density=10, k_moran=10.

---

## What comes next

Await the next blueprint from the supervisor. Expected first task:
**Si Cred redesign** — replace surplus-based accumulation with
near-dormancy-survival accumulation to make Si Cred counter-cyclical.

Do not begin any task until you receive the blueprint. Read CLAUDE.md
in the project root before doing anything else.

---

## After completing this task

State: "Task complete. Recommended: start a fresh Claude Code session
for the next stage to avoid context compression."

Then provide:
- What was changed (files, functions, test count)
- What the equivalence gate confirmed
- What comes next
