# Social-Dynamics Locked Parameter Triage Table
## Consolidated Reconciliation Directive — Task 9

**Date:** 2026-06-13  
**Method:** Triage from Phase 0 run outputs, event logs, and production YAML configs. Binary criterion: did the mechanic this parameter governs produce events in Phase 0 runs?  
**ACTIVE** = mechanic fired, parameter was operative against real behavior → guidepost; confirm on new substrate (sanity-check, not re-derive).  
**DORMANT** = mechanic zero-value disabled or never produced events → placeholder; see Task 10 PROVISIONAL marking.  
**INDETERMINATE** = cannot determine from available outputs without additional logging.

Evidence sources used (no model runs launched under this directive):
- Stage 5.1 gate report: dormancy 21–31%, perm_deaths=0, N_mean=335
- Stage 5.2 report: c2 defection_rate=3.74%
- Stage 5 multi-seed ensemble: H1(ii) confirmed 5/5 seeds; births/deaths occurring
- Stage 7.5 GATE FINAL: Si seasonal run (5 seeds, 400 steps); dormancy 21–31% exact
- Stage 4.3 ROADMAP note: T_dormant_max governs permanent death cliff (Si extinction at A=0.75/T=200)
- R0 confound check: C-only at 100×100, N_carry=4100, settled≈2399 (carry_discount operative)
- Production YAML configs: τ_parent=0.0 and k_pool_cap=0.0 in all Stage 5+ runs

---

| Parameter | PARAMETERS.md §ref | Governing mechanic | Classification | Evidence |
|---|---|---|---|---|
| σ_base = 0.5 (C base exploration) | §2 | C softmax decision-σ (every step) | **ACTIVE** | Decision fires every step in every run. Guidepost. |
| κ = 2.0 (C Cred-σ coupling) | §2 | C σ = σ_base + κ·tanh(𝒞/C*) | **ACTIVE** | C Cred accumulated in every Stage 5+ C run; σ-coupling drove exploration modulation. Guidepost. |
| σ_Si = 1.238 (Si fixed exploration) | §2 | Si softmax decision-σ | **ACTIVE** | Si moves every step in every Si run. Guidepost (locked by Stage 3.4 scan against C entropy). |
| κ_Si = 0.5 (Si Cred-σ coupling) | §2 | Si σ_eff = σ_Si + κ_Si·tanh(si_cred/C*_Si) | **ACTIVE** | Stage 5.1: Si Cred activated, σ_Si_eff_mean=1.28 > σ_Si=1.238 confirmed modulation. Guidepost. |
| β = 1.0 (status amplification) | §2 | C utility weight φ·(1+β·tanh(𝒞/C**)·sigmoid(v/v_0) | **ACTIVE** | Status amplification active in all C runs post Stage 3.2. Guidepost. |
| ε = 0.2, μ = 0.3 (Deffuant) | §3 | Bounded-confidence cultural updating | **ACTIVE** | Stage 5.2: Deffuant installed and gated (3 equivalence gates PASS); homogenisation observed (Cell B). Guidepost. |
| c2_defection.enabled = True | §4 | c2 defection hook (C only) | **ACTIVE** | Stage 5.2: defection_rate = 3.74%, N stable. Direct event observation. Guidepost. |
| k_cred_band = 1.0 (Si near-dormancy band) | §5 | Si Cred accumulation trigger | **ACTIVE** | Stage 5.1: counter-cyclicality gate PASSED (trough/peak 1.13/0.49 seed=42); si_cred_mean=0.97 confirmed accumulation. Guidepost. |
| f_C = 0.25 (C newborn Cred endowment) | §5 | C newborn endowment fraction | **ACTIVE** | C births occurred in every C run post Stage 3.1; newborn Cred assigned at each birth. Guidepost. |
| γ = 0.2 (Cred-modulated birth) | §5 | P_birth_C × (1 + γ·tanh(𝒞/C***)) | **ACTIVE** | Stage 4.2: gamma_birth_boost mean ≈1.09 at steady state; confirmed operative. Guidepost. |
| τ_pool = 0.05 (pool contribution) | §6 | L2 proximity pool contribution | **ACTIVE** | Pool active in all Stage 4.1c+ runs; pool draw diagnostics logged. Guidepost (design tension on dual regulator role noted). |
| τ_cred = 0.5, τ_cred_reward = 0.1 | §6 | L3 status pool contribution (C only) | **ACTIVE** | Stage 4.2 BUG-003 fix confirmed cred_pool_contribution = 3.65/step post-fix; L3 operative. Guidepost. |
| ρ_carryover = 0.3 (pool carry-over) | §6 | Granary: pool_{t+1} = ρ·leftover | **ACTIVE** | Stage 4.3: T* narrowed (100,200)→(100,112) from pool carry-over effect; confirmed operative. Guidepost. |
| **τ_parent = 0.0** (parental transfer) | §6 | L1 parental transfer at birth: offspring += τ_parent·mean(w_A,w_B) | **DORMANT** | τ_parent=0.0 in all Stage 4.3+ production configs. Mechanic receives zero-value parameter — produces zero transfer. Never transferred non-zero wealth in Phase 0. **PROVISIONAL — see PARAMETERS.md §6.** |
| **k_pool_cap = 0.0** (pool cap) | §6 | Pool capacity ceiling: cap = k·N_active·mean_metabolism | **DORMANT** | k_pool_cap=0.0 in all Stage 5.1+ production configs. Cap disabled — mechanic never enforced an upper bound. **PROVISIONAL — see PARAMETERS.md §6.** |
| p_max_C = 0.12 (C max birth prob) | §7 | C DTM birth ceiling × carry_discount | **ACTIVE** | Stage 5 multi-seed: C viable population with births confirmed. Carry_discount operative (settled N < N_carry → discount > 0). Guidepost. |
| p_fission_Si = 0.065 (Si fission prob) | §7 | Si fission trigger: w_i ≥ θ_fission → P_fission_max | **ACTIVE** | Stage 5.1: N_mean=335, fissions occurred. Guidepost. |
| σ_inherit = 0.10 (trait noise) | §7 | Biparental/fission copy-error at every birth | **ACTIVE** | Every birth in every run with trait vectors applied copy-error. Guidepost (corrective sweep OWE-9 pending — value may be revised, not retired). |
| λ = 0.1 (C wealth inheritance) | §7 | w_child += λ·mean(w_A, w_B) (C only) | **ACTIVE** | Stage 4.4: λ=0.1 activated for C; λ=0 for Si by design. C births include wealth term. Guidepost. |
| η_min = 0.3, η_old = 0.4 (age efficiency) | §7 | η(a) ramp (C only; Si always 1.0) | **ACTIVE** | Stage 4.1b: ramp operative; juvenile starvation observed (0.3% C Stage 4.1c). Guidepost. |
| β_Si = 5.0 (Si differential metabolism) | §7 | Si metabolic cost = m_i × β_Si | **ACTIVE** | Stage 4.4: β=5 viable at k=4 grid. Si metabolism drives dormancy dynamics in every Si run. Guidepost. |
| N_carry_50 = 400 (50×50 C ceiling) | §7 | carry_discount(N_C) = max(0, 1 - N_C/N_carry) | **ACTIVE** | Stage 4.5–5: C settled in [150,400] band; carry_discount confirmed constraining births. Guidepost. |
| N_carry_100 = 4100 (100×100 C ceiling) | §7 | Same carry_discount, 100×100 grid | **ACTIVE** | R0 confound check: settled≈2399 at N_carry=4100; carry_discount = 1−2399/4100 ≈ 0.41 operative. Guidepost. Note: this is a scale-setting calibration choice, not a calibrated scientific parameter — confirm on terrain substrate in OWE-14. |
| k_dormant = 1.0 (dormancy threshold) | §8 | Dormancy trigger: w_i < k_dormant × cost_i | **ACTIVE** | Stage 5.1: 21–31% dormancy fraction during troughs. Guidepost. |
| τ_trickle = 0.3 (passive absorption) | §8 | Dormant agent trickle: τ_trickle × cell_sugar/step | **ACTIVE** | Stage 5.1 + Stage 7.5 GATE FINAL: dormancy mechanics confirmed operative. τ_trickle governs recovery rate in dormancy. Guidepost. |
| k_reactivate = 3.0 (reactivation threshold) | §8 | Reactivate if w_i ≥ k_reactivate × cost_i | **ACTIVE** | Reactivation events implied by oscillating dormancy fraction. Guidepost. |
| T_dormant_max = 50 (permanent dormancy limit) | §8 | Permanent death after >T_dormant_max dormant steps | **ACTIVE** | Stage 5.1 null control: perm_deaths=0 (dormancy never exceeded 50 steps in null). Stage 4.3 + Stage 5 A=0.75/T=200: Si extinction IS driven by T_dormant_max cliff (dormancy duration exceeds limit during long trough). Mechanic fires in high-stress scenarios. Guidepost. |

---

## INDETERMINATE parameters (supervisor decision required — do NOT auto-mark)

None identified from available outputs. All parameters could be classified from run reports, event logs, and config YAMLs.

---

## Summary

| Classification | Count | Parameters |
|---|---|---|
| **ACTIVE** (guidepost; confirm on new substrate) | 23 | All §2 σ/decision, §3 Deffuant, §4 JT/defection, §5 Cred, §6 pool/carry-over, §7 birth/reproduction, §8 dormancy (except noted) |
| **DORMANT** (PROVISIONAL — re-derive on rebuilt substrate) | 2 | τ_parent=0.0, k_pool_cap=0.0 |
| **INDETERMINATE** (supervisor decides) | 0 | — |

**PROVISIONAL marking applied** in PARAMETERS.md §6 for the two DORMANT parameters. ACTIVE parameters retain LOCKED status.
