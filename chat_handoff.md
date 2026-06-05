# SiC Games — Chat Handoff

**Paste this as the first message in the new project chat.**

---

## Current model state: v5.1-postaudit-clean

We are resuming the SiC Games project. The previous chat completed Stages 4.4
through 5 and a full performance optimisation pass. Here is everything you need
to continue without prior context.

---

## What SiC Games is

An agent-based model (Python/Mesa) comparing two civilisational strategies on
matched 50×50 toroidal Sugarscape worlds:
- **C** — cooperative: Cred-coupled softmax decisions, joint tasks, biparental
  reproduction, support pool, wealth inheritance, carrying-cost birth ceiling
- **Si** — individualist: bounded rationality, dormancy during resource troughs,
  fission reproduction, Si Cred (surplus-based)

Central research question: **H1(ii)** — which strategy is more resilient to
periodic resource shocks (sinusoidal amplitude A, period T)?

---

## Key confirmed findings

- **H1(ii) INVERTED, robust 5/5 seeds:** C survives A=0.75, T=200; Si collapses.
  C also survives A=0.9 at both T=100 and T=200. C's amplitude limit A* > 0.9.
- **Si T* ∈ (68, 87) at A=0.75.** C T* > 500. Gap > 413 steps.
  Si's dormancy mechanic creates a synchronised mass-death cliff when trough
  duration exceeds T_dormant_max=50 steps.
- **H_cc pre-registered:** The carrying-cost birth ceiling (carry_discount =
  max(0, 1 − N_C/N_carry)) produces a counter-cyclical birth boost during
  troughs. Regression-supported (Stage 5) but pending full multi-seed test at A=0.9.
- **Si Cred (surplus-based) is pro-cyclical** — reduces σ_Si_eff during stress.
  Did not rescue Si at A=0.75. Needs redesign.
- **ψ co-evolution null at 3000 steps:** σ_inherit=0.05 collapses Gini from
  0.25 to 0.09 within 500 steps. σ_inherit needs redesign.

---

## All locked parameters

| Parameter | Value | | Parameter | Value |
|---|---|---|---|---|
| k_grid | 4 | | σ_Si | 1.238 |
| β_Si | 5.0 | | κ (Cred-σ) | 2.0 |
| p_fission_Si | 0.28 | | α (Matthew) | 2.0 |
| p_max_C | 0.12 | | β (status) | 1.0 |
| N_carry | 400 | | f_C | 0.25 |
| α_carry | 1.0 | | σ_inherit | 0.05 |
| τ_pool | 0.05 | | age_init_upper_frac | 0.25 |
| ρ | 0.3 | | wealth_init_scale_k | True |
| λ | 0.1 | | cluster_init (C only) | peak_index=0, r=10 |
| T_dormant_max | 50 | | k_density | 10 |
| k_dormant | 1.0 | | k_moran | 10 |
| τ_trickle | 0.05 | | r_cred_Si | 0.1 |
| k_reactivate | 3.0 | | κ_Si | 0.5 |

---

## Performance state (post-optimisation)

All grid sizes B0–B5 are LHS-feasible (< 4h for 300 runs, 4 workers).
Working grid for Stage 5.x: **100×100**.

| Config | ms/step | LHS (300r, 4w) |
|---|---|---|
| B1 100×100 N=500 | 53ms | 0.55h |
| B3 150×150 N=1000 | 141ms | 1.47h |
| B5 200×200 N=1500 | 215ms | 2.24h |

Cumulative speedup from original baseline: **40× at B0, 140× at B1.**

---

## Infrastructure

- BatchRunner with CRN (env_rng/agent_rng split), 4 workers — Stage 5
- 201 tests passing
- Backup at: `G:\My Drive\docs\SiC Games\Model\v5.1_2026-05-28_0637`
- No git repo — version control is logical labels + directory backups

---

## Stage 5.x agenda (what comes next, in order)

**1. Si Cred redesign** (small, targeted)
The current Si Cred accumulates on surplus, making it pro-cyclical — σ_Si_eff
drops exactly when Si is most stressed. Redesign: accumulate on near-dormancy
survival (agent stays active when wealth is between k_dormant and k_dormant+δ).
This makes high-Cred Si agents more explorative under stress.

**2. Stage 5.2 — Cultural dynamics**
- c2 behavioral hook: c2_i modulates joint-task defection (high c2 → defect
  when solo harvest > Matthew share). c2 is already carried and inherited; just
  needs wiring into the decision.
- Deffuant cultural updating + c1 hook: agents update traits toward neighbours
  within confidence bound; c1_i scales resistance to copying; C uses
  Cred-weighted (prestige) transmission.
- σ_inherit sweep: test 0.10 and 0.20 to address the ψ homogenisation problem.

**3. Terrain topography**
Add spatially varying resource abundance AND metabolic cost to the grid.
Valley (between peaks) = lower sugar capacity + lower metabolism multiplier.
Peaks = higher sugar capacity + higher metabolism multiplier.
This decouples "rich environment" from "easy environment" — currently conflated.
Target grid: 100×100. Implementation: terrain_multiplier(row, col) lookup,
one call per agent per step.

**4. Stage 5.1 — LHS parameter sensitivity scan**
5D Latin Hypercube Sampling over A × T × N_carry × T_dormant_max × α_carry.
~30 points. BatchRunner makes this fast (0.55h at B1).
Purpose: identify which parameters most affect C/Si resilience ordering
before Stage 6 statistical framework.

**5. Stage 6 (after 5.x complete)**
Statistical framework, power analysis, effect sizes. Separate Si and C
civilisations on matched worlds (CRN). No mixed populations.

---

## What is NOT in scope

- Mixed C+Si populations (explicitly excluded — separate civilisations on matched worlds)
- HiveMind (Stage 7+)
- Biparental Si reproduction (Stage 7+)
- Inter-pool connectivity (Stage 6+)
- Full nD LHS (Stage 5.1, after 5.2 mechanics)

---

*Begin the new chat by confirming you have read this handoff and stating
what the first task should be.*
