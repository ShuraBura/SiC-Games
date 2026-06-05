# SiC Games Model — Version v5.1-postaudit-clean
**Date:** 2026-05-28_0637
**Git tag:** v5.1-postaudit-clean (NOTE: no git repository present; tag is a logical label only)
**Test count:** 198 passing
**Python:** 3.14.3 | numpy 2.4.3

---

## What this version contains

### World
- 50×50 toroidal grid, 2 sugar peaks at relative positions (0.2,0.8) and (0.8,0.2)
- k_grid=4: max_sugar=16, growback_alpha=4
- Seasonal perturbation: amplitude A, period T, trough fraction tf
- Spatial hash (cell→agent) built once per step; reused by JT, pool, metrics

### C agent — full mechanic stack
- Softmax with Cred-coupled σ: σ_i = σ_base + κ·tanh(C_i/C*)
- Wealth-velocity behavioral mode switch (φ_i ceiling)
- Status amplification β=1.0
- Trait vector H_i = [φ_i, ψ_i, c1_i, c2_i]
  — ψ_i: active (pool proximity utility)
  — c1_i, c2_i: carried + inherited, NOT active (pending Stage 5.2)
- Joint-task mechanic, Matthew partition α=2.0
- Biparental reproduction (r=3, arithmetic mean + σ_inherit=0.05)
- f_C=0.25, λ=0.1, DTM birth, age-efficiency ramp η(a)
- Support pool τ_pool=0.05, ρ=0.3
- Carrying-cost birth ceiling: carry_discount = max(0, 1 − N_C/N_carry)
  N_carry=400, α_carry=1.0

### Si agent — full mechanic stack
- BoundedRationalSi, σ_Si=1.238
- Dormancy: k_dormant=1.0, τ_trickle=0.05, k_reactivate=3.0, T_dormant_max=50
- Fission reproduction, η=1.0 at birth
- Si Cred: surplus-based (r_cred=0.1), σ_Si_eff modulation κ_Si=0.5
- Si pool: enabled, τ_pool=0.05, ρ=0.3
- k_carry for Si: disabled

### Infrastructure
- BatchRunner with CRN (env_rng/agent_rng split), 4 workers
- Patch fixes: age_init_upper_frac=0.25, wealth_init_scale_k=True,
  cluster_init=True (C only, peak_index=0, radius=10)

### Locked parameters

| Parameter        | Value  | Locked at        |
|------------------|--------|------------------|
| k_grid           | 4      | Stage 4.4        |
| β_Si             | 5.0    | Stage 4.4        |
| p_fission_Si     | 0.28   | Stage 4.3        |
| p_max_C          | 0.12   | Stage 4.5 Task 1 |
| N_carry          | 400    | Stage 4.5 Task 0 |
| α_carry          | 1.0    | Stage 4.5 Task 0 |
| τ_pool           | 0.05   | Stage 4.3        |
| ρ                | 0.3    | Stage 4.3        |
| λ                | 0.1    | Stage 4.5 Task 1 |
| σ_Si             | 1.238  | Stage 3.4        |
| κ                | 2.0    | Stage 3.4        |
| α (Matthew)      | 2.0    | Stage 3.4        |
| β (status)       | 1.0    | Stage 3          |
| f_C              | 0.25   | Stage 3          |
| σ_inherit        | 0.05   | Stage 3          |
| age_init_upper_frac | 0.25 | Stage 4.4 patch |
| T_dormant_max    | 50     | Stage 4.3        |
| r_cred_Si        | 0.1    | Stage 5          |
| κ_Si             | 0.5    | Stage 5          |

### Key confirmed findings

- H1(ii) inversion ROBUST (5/5 seeds): C survives A=0.75 T=200; Si collapses.
- C survives A=0.9 at T=100 and T=200. C amplitude limit A* > 0.9.
- Si T* ∈ (68,87) at A=0.75. C T* > 500. Gap > 413 steps.
- H_cc pre-registered (Stage 4.5 patch): carry_discount counter-cyclical
  birth boost during troughs. Regression-supported at Stage 5.
- Si Cred does not rescue Si at A=0.75 collapse — inversion is structural.
- ψ co-evolution null at 3000 steps: σ_inherit=0.05 collapses Gini
  0.25→0.09 within 500 steps (biparental averaging).

### Performance (this version — post-audit-clean)

| Config | Grid  | N    | ms/step | LHS (300r, 4w) |
|--------|-------|------|---------|----------------|
| B0     | 50×50 | 250  | 13.1    | 0.1h           |
| B1     | 100×100 | 500 | 95.1  | 1.0h           |
| B2     | 100×100 | 1000 | 110.2 | 1.1h          |
| B3     | 150×150 | 1000 | 343.1 | 3.6h          |
| B4     | 150×150 | 2000 | 409.7 | 4.3h          |
| B5     | 200×200 | 1500 | 845.6 | 8.8h          |

Cumulative speedup from unoptimised baseline: B0 = 38×, B1 = 77×.

---

## Post-optimisation performance (perf-opt pass, 2026-05-28)

Fixes applied: Task 2 (c_spatial_density periodic, k_density=10),
Task 3 (_moran_W periodic, k_moran=10),
Task 4 (_carbon_birth spatial hash + sort-by-id).
Task 1 REVERTED (mean_cred cache changes newborn endowment semantics).

| Config | Grid  | N    | ms/step | LHS (300r, 4w, 500s) |
|--------|-------|------|---------|----------------------|
| B0     | 50×50 | 250  | 12.5    | 0.13h                |
| B1     | 100×100 | 500 | 53.0  | 0.55h                |
| B2     | 100×100 | 1000 | 58.1 | 0.61h                |
| B3     | 150×150 | 1000 | 140.7 | 1.47h               |
| B4     | 150×150 | 2000 | 117.9 | 1.23h               |
| B5     | 200×200 | 1500 | 214.7 | 2.24h               |

Grid exponent (100→150, N=1000 fixed): 1.09 (target ≤2.0 ✓)
N exponent (N 500→1000, grid=100 fixed): 0.13

### Metric sampling frequencies (post-opt)

| Metric | Every N steps | Type |
|--------|--------------|------|
| c_spatial_density | 10 (k_density) | Diagnostic |
| Moran's I (φ,ψ,c1,c2) | 10 (k_moran) | Diagnostic |
| All other metrics | 1 | Unchanged |
