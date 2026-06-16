# SiC Games — Parameters (PARAMETERS.md)

**The ONE question:** "What is parameter X — value, range, status, grounding, lock/sweep history?"
(charter §2, home 5; charter §4 format).

**Status:** AUTHORITATIVE. Extracted 2026-06-08 from the interim locked-param tables in
`sic_games/CLAUDE.md` and `docs/ROADMAP.md`, resolving the D1–D3 discrepancies logged in
`ARCHITECTURE.md §15`. This document supersedes both interim tables as the single source of
parameter truth; ROADMAP, MECHANISMS, CLAUDE.md, and all blueprints point here.

**Format (charter §4):**
`name · current value · range · status · mechanism ref · lock/sweep/retire history`

**Status vocabulary:** `LOCKED` (changed only by supervisor approval + dated entry here) ·
`OPEN` (not yet swept; default value in use) · `UNDER-REVIEW` (sweep in progress) ·
`RETIRED` (removed from model; entry kept for history).

**Update trigger:** any parameter lock, sweep, retirement, or status change → append a dated
entry in the "Lock / sweep / retire" column; never overwrite the old entry.

**Grounding sources:** `BP = blueprint §x.y`; `ARCH = ARCHITECTURE.md §x`; `MECH = MECHANISMS.md §x`.

---

## §1 — World / resource substrate
*(MECH §9 pointer; ARCH §9 narrative)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| Grid scale factor | k_grid | **4** | {1,2,3,4,…} | LOCKED | MECH §9 | Stage 4.4: minimum k where β_Si=5 Si null control passes. k=3: permanent dormancy. |
| Max sugar capacity | c_max | **16** (=4·k_grid) | ≥1 | LOCKED | MECH §9 | Derived from k_grid; changes with it. Stage 4.4. |
| Sugar growback rate | α_growback | **4** (=k_grid) | ≥1 | LOCKED | MECH §9 | Derived from k_grid. Stage 4.4. |
| Band width | k_band | **6** | ≥1 | LOCKED | MECH §9 | Stage 1. Original Epstein & Axtell value. |
| Grid size (production) | — | **100×100** | — | LOCKED | ARCH §9.3 | OWE-1 (2026-05-30): 1 cell = 100 km²; 10 000 cells total = 1 000 000 km² plausible territory. |
| Temporal resolution | — | **1 step = 1 month** | — | LOCKED | ARCH §9.3 | OWE-1 (2026-05-30): standing constraint — changing requires full recalibration. |
| Cell area | cell_area_km2 | **100.0** | — | LOCKED | ARCH §9.3 | Stage 6.0a (2026-06-03): declared for density-vs-ethnography reporting. 1 cell ≈ 10×10 km patch. |
| Sugar peaks (50×50) | — | **[(10,40),(40,10)]** | — | LOCKED | MECH §9 | Stage 1. Twin-peak Sugarscape. Production grid below uses 4 peaks. |
| Sugar peaks (100×100) | — | **[(25,25),(25,75),(75,25),(75,75)]** | — | LOCKED | MECH §9 | OWE-1 calibration 4-peak layout. |

---

## §2 — Decision / σ-coupling (C and Si)
*(MECH §3)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| C base exploration | σ_base | **0.5** | (0,∞) | LOCKED | MECH §3 | Stage 2. Default; not yet swept. |
| C Cred–σ coupling | κ | **2.0** | ≥0 | LOCKED | MECH §3 | Stage 2.2: κ sweep (κ=1.0, 2.0, 3.0). Stage 3.4: 2D scan; cell (2,3) → κ=2.0 confirmed. |
| C Cred scale (σ-coupling) | C\* | **10.0** | >0 | LOCKED | MECH §3 | Stage 2. Not swept; pinned. C\*\* and C\*\*\* are pinned to C\*. |
| Status amplification scale | C\*\* | **10.0** (= C\*) | >0 | LOCKED | MECH §3 | Stage 3.2: deferred independent sweep (Q11 open). |
| Birth Cred-modulation scale | C\*\*\* | **10.0** (= C\*) | >0 | LOCKED | MECH §5 | Stage 4.2. Pinned to C\*. |
| Si fixed exploration | σ_Si | **1.238** | (0,∞) | LOCKED | MECH §3 | Stage 3.4: 2D (κ,α) scan; cell (2,3) σ_Si recalibrated to mean_sigma at that cell. |
| Wealth-velocity EMA window | v_tau | **10** | ≥1 | LOCKED | MECH §3 | Stage 2.1. Mode-switch EMA. |
| Wealth-velocity sigmoid scale | v_0 | **1.0** | >0 | LOCKED | MECH §3 | Stage 2.1. |
| Status amplification | β | **1.0** | ≥0 | LOCKED | MECH §3 | Stage 3.2: β sweep (0.5, 1.0, 2.0). β=1.0 selected. |
| Si Cred–σ coupling | κ_Si | **0.5** | ≥0 | LOCKED | MECH §3 | Stage 5 Task 3. Smaller than C's κ=2.0 (no JT amplification for Si). |
| Si Cred ceiling | C\*_Si | **10.0** | >0 | LOCKED | MECH §3 | Stage 5 Task 3. Matches C\*. si_cred clamped to [0, C\*_Si]. |

---

## §3 — Deffuant cultural updating
*(MECH §3.2)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| Confidence bound | epsilon | **0.2** | (0,1) | LOCKED | MECH §3.2 | Stage 5.2 Task 2. |
| Convergence rate | mu | **0.3** | (0,0.5] | LOCKED | MECH §3.2 | Stage 5.2 Task 2. |
| Cred weighting scheme | cred_weight | **relative** (w = cred_j/(cred_i+cred_j+eps_div)) | — | LOCKED | MECH §3.2 | Stage 5.2 Task 2. |

---

## §4 — Joint task
*(MECH §4)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| JT participation radius | d | **1** | ≥1 | LOCKED | MECH §4 | Stage 2. Manhattan/Chebyshev distance. |
| Cell capacity threshold | θ_c | **4** | ≥2 | LOCKED | MECH §4 | Stage 2. Min occupants for JT to fire. |
| Matthew partition power | α_matthew | **2.0** | ≥0 | LOCKED | MECH §4 | Stage 2 (α=1.0); Stage 3.4: 2D scan → 2.0 selected. |
| Laplace smoothing | ε_laplace | **0.01** | >0 | LOCKED | MECH §4 | Stage 2. Prevents divide-by-zero in Matthew shares. |
| Cred bonus per participant | cred_bonus | **1.0** | ≥0 | LOCKED | MECH §4 | Stage 2. |
| c2 defection enabled | c2_defection | **True** | bool | LOCKED | MECH §4 | Stage 5.2 Task 1: defection_rate=3.74%, N∈[150,400] stable. |

---

## §5 — Cred economy
*(MECH §5; Si Cred MECH §5.2)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| C Cred decay | δ_C | **0.01** | [0,1] | LOCKED | MECH §5 | Stage 2. Per-step decay: C_i ← C_i·(1−δ). Not yet swept. |
| Newborn Cred endowment fraction | f_C | **0.25** | [0,1] | LOCKED | MECH §5 | Stage 3.1: f_C sweep (0.125, 0.25, 0.50). 0.25 selected. |
| Cred-modulated birth rate (C only) | γ | **0.2** | ≥0 | LOCKED | MECH §5 | Stage 4.2. P_birth_C × (1 + γ·tanh(C/C\*\*\*)). Boost mean ≈1.09. No runaway. |
| Si near-dormancy Cred band width | k_cred_band | **1.0** | >0 | LOCKED | MECH §5.2 | Stage 5.1: Δsi_cred=1 if wealth ∈ [k_dormant, k_dormant+k_cred_band)×cost_i. Counter-cyclicality gate PASSED both seeds. |
| Si Cred accumulation rate | r_cred_Si | **RETIRED** | — | RETIRED | MECH §5.2 | Stage 5.1: replaced by binary near-dormancy trigger (k_cred_band). Surplus-based mechanism was pro-cyclical. |

---

## §6 — Support pool
*(MECH §6)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| Self-support fraction | τ_parent | **0.0** | [0,1] | LOCKED — **PROVISIONAL (DORMANT)** | MECH §6 | Stage 4.1c: 0.10. Set to 0.0 in Stage 4.3+ production configs (full pool replaced self-support). Governs parental-transfer mechanic; mechanic produces zero transfer at this value — never fired in Phase 0. Re-derive on rebuilt substrate. |
| Pool contribution rate | τ_pool | **0.05** | [0,1] | LOCKED | MECH §6 | Stage 4.1c: 0.10. Stage 4.2: reduced to 0.05 (design tension — dual role: pool buffer + N suppressor). Full resolution deferred. |
| Wealth reserve multiple | k_reserve | **5.0** | >0 | LOCKED | MECH §6 | Stage 4.1c / 4.2 recalibration. |
| Draw threshold multiple | k_draw | **3.0** | >0 | LOCKED | MECH §6 | Stage 4.1c / 4.2. |
| Pool→Cred transfer rate | τ_cred | **0.5** | [0,1] | LOCKED | MECH §6 | Stage 4.x production configs. |
| Pool→Cred reward rate | τ_cred_reward | **0.1** | [0,1] | LOCKED | MECH §6 | Stage 4.x production configs. |
| Granary carryover fraction | ρ_carryover | **0.3** | [0,1] | LOCKED | MECH §6 | Stage 4.3: pool_t+1 = ρ·leftover_t + contributions. Narrowed T* from (100,200)→(100,112). |
| Pool cap multiplier | k_pool_cap | **0.0** (production) | ≥0 | LOCKED — **PROVISIONAL (DORMANT)** | MECH §6 | Stage 4.3 design: 20.0 (cap=20·N_active·mean_metabolism). Production YAML uses 0.0 (cap disabled). Governs pool-cap mechanic; mechanic never engaged at 0.0 — cap disabled in all Phase 0 production runs. Re-derive on rebuilt substrate. |
| Pool proximity radius | r_pool | **5** | ≥1 | LOCKED | MECH §6 | Stage 4.4: c_proximity redesign. |

---

## §7 — Reproduction and population dynamics
*(MECH §7)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| C max birth probability (50×50, full config) | p_max_C | **0.12** | (0,1) | LOCKED | MECH §7 | Stage 4.5: with pool+λ+carrying_cost. Supersedes Stage 4.4 (0.03) and Stage 4.2 (0.07). |
| C max birth probability (bare, without pool/λ) | p_max_C_bare | **0.11** | (0,1) | LOCKED | MECH §7 | Stage 4.5 Task 0. |
| Si fission probability (β=5, k_grid=4) | p_fission_Si | **0.065** | (0,1) | LOCKED | MECH §7 | **Stage 4.4.** N_active=[174,364], dorm_rate=5.1%, perm_dorm=0.0. Supersedes Stage 4.3 (0.15 at β=2) and Stage 4.2 (0.24 at β=2 / τ_pool=0.05). CLAUDE.md interim table had stale value 0.28 (Stage 4.3) — corrected here. |
| Trait inheritance noise | σ_inherit | **0.10** | ≥0 | LOCKED | MECH §7 | Stage 3.3: 0.05. **Stage 5.2 Task 3: raised to 0.10** — lowest value sustaining Gini(ψ)≥0.15 in ≥1 seed with Deffuant OFF. CLAUDE.md had both 0.05 and 0.10 — 0.10 is current. **CAVEAT (verified 2026-06-15, DIRECTIVE_context_sync §5.1):** YAML key is `inherit_sigma`. Stage 5.2 Tasks 1+2 (c2 defection gate, Deffuant equivalence gates: `ver1`, `ver2`, `gate_deffuant_*`) all ran at `inherit_sigma: 0.05`. σ_inherit=0.10 was exercised only in Task 3 (the sweep cells `task3_cell*_sigma010_*`). **The Stage 5.2 headline findings (c2 defection=3.74%; Deffuant homogenisation equivalence) were produced at 0.05, not 0.10. Verdict: PARTIALLY UNEXERCISED.** |
| C wealth inheritance | λ | **0.1** | [0,1] | LOCKED | MECH §7 | Stage 4.4: activated. λ=0 for Si always (never changes). Stage 4.1a: λ=0 default introduced. |
| Biparental parent radius | r | **3** | ≥1 | LOCKED | MECH §7 | Stage 3.3. |
| C min age-efficiency | η_min | **0.3** | [0,1] | LOCKED | MECH §7 | Stage 4.1b: juvenile ramp floor. C-only (Si: η=1.0 always). |
| C elder age-efficiency | η_old | **0.4** | [0,1] | LOCKED | MECH §7 | Stage 4.1b: elder decline floor. |
| Si differential metabolism | β_Si | **5.0** | ≥1 | LOCKED | MECH §7 | Stage 4.4: restored from Stage 4.3 interim β=2. k_grid=4 makes β=5 viable. Mean Si cost ≈12.5/step; mean harvest ≈10–15/step (dormancy handles shortfall). |
| C carrying capacity (50×50) | N_carry_50 | **400** | >0 | LOCKED | MECH §7 | Stage 4.5: carry_discount(N_C)=max(0,1−N_C/N_carry). Scale-setting calibration for 50×50 science runs. |
| C carrying capacity (100×100, production) | N_carry_100 | **4100** | >0 | LOCKED | MECH §7 | OWE-1.1 (2026-05-31): settled N ≈ 2357 (target 2000–3000). Map: settled ≈ 0.754·N_carry − 566. H1(ii) re-test pre-registered — see `HYPOTHESES.md §H1ii-RETEST` and OWE-14. |
| Carrying-cost discount exponent | α_carry | **1.0** | >0 | LOCKED | MECH §7 | Stage 4.5. Linear discount. Non-linear alternatives unnecessary at current N range. |

---

## §8 — Dormancy (Si only)
*(MECH §8)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| Dormancy wealth threshold | k_dormant | **1.0** | >0 | LOCKED | MECH §8 | Stage 4.3. Dormant if wealth < k_dormant × metabolism. |
| Passive trickle absorption | τ_trickle | **0.3** | [0,1] | LOCKED | MECH §8 | Stage 4.3: blueprint said 0.05; raised to 0.3 so dormant agents recover on partially-depleted cells. CLAUDE.md interim had stale value 0.05 — **corrected here to 0.3** (see ARCHITECTURE §15 D1). |
| Reactivation threshold | k_reactivate | **3.0** | >k_dormant | LOCKED | MECH §8 | Stage 4.3. Reactivate if wealth ≥ k_reactivate × metabolism. |
| Max dormancy duration | T_dormant_max | **50** | ≥1 | LOCKED | MECH §8 | Stage 4.3. Permanent death if dormant > T_dormant_max steps. |

---

## §9 — Initialization
*(implementation)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| Age init upper fraction | age_init_upper_frac | **0.5** | (0,1] | LOCKED | — | Stage 4.4 patch: realistic age distribution. Production YAML (stage51_si_null_seed42.yaml): 0.5. CLAUDE.md had 0.25 — stale; corrected here. |
| Wealth init scale by k | wealth_init_scale_k | **True** | bool | LOCKED | — | Stage 4.4 patch: initial wealth drawn from Uniform[5,25]·k_grid. |
| Cluster init (C only) | cluster_init | **True** (C), peak_index=0, radius=10 | bool | LOCKED | — | Stage 4.4 patch. Si: cluster_init=False. |

---

## §10 — Diagnostics / monitoring
*(ARCHITECTURE §12.1-H §H.5)*

| Name | Symbol | Value | Range | Status | MECH ref | Lock / sweep / retire history |
|------|--------|-------|-------|--------|----------|-------------------------------|
| c_spatial_density cadence | k_density | **10** | ≥1 | LOCKED | — | Stage 6.0a perf recon (2026-06-05): every-10-step cadence balances signal vs cost. |
| Moran's I cadence | k_moran | **10** | ≥1 | LOCKED | — | Stage 6.0a perf recon (2026-06-05). |

---

## §11 — Critical periods and T* (shock-response findings)
*(MECH §8; findings recorded in RESULTS.md)*

These are not free parameters but measured outputs of the model at locked parameter values.
Recorded here as reference for the calibration pass.

| Name | Value | Conditions | Source |
|------|-------|-----------|--------|
| Si T\* (critical period, A=0.75) | (68, 87) steps | β_Si=5, k=4, N_carry=400, 50×50 | Stage 5 Task 2 binary search |
| C T\* (critical period, A=0.75) | > 500 steps | p_max_C=0.12, N_carry=400, 50×50 | Stage 4.5 patch |

---

## §12 — Phase 1 terrain constants
*(terrain.py; ARCHITECTURE.md §9.5)*

**World dimensions** have their canonical home in **§1** above (Grid size 100×100, Cell area 100 km², world 1,000,000 km²). Terrain-specific constants are indexed here; pointer to §1 for dimensions.

### §12.1 — Generator formulas (locked byte-identical to JS prototype)

| Name | Symbol | Value | Range | Status | Source | Lock history |
|------|--------|-------|-------|--------|--------|-------------|
| Forest threshold | W_FOREST | **0.45** | (0,1) | LOCKED | terrain.py | Stage 7 (2026-06-10): byte-identical to JS prototype. |
| Savanna threshold | W_SAV | **0.18** | (0,1) | LOCKED | terrain.py | Stage 7 (2026-06-10): forestness ∈ [W_SAV, W_FOREST) → savanna/woodland. |
| Relief floor amplitude | RELIEF_FLOOR_M | **120.0 m** | >0 | LOCKED | terrain.py | Stage 7 (2026-06-10): peak-to-trough at relief=0 (gentle rolling). |
| Relief ceiling amplitude | RELIEF_CEIL_M | **2500.0 m** | >RELIEF_FLOOR_M | LOCKED | terrain.py | Stage 7 (2026-06-10): peak-to-trough at relief=1 (mountainous). |
| Mountain elevation threshold | mtn_elev_thresh | **0.72 + (1−relief)·0.5** | (0,1) (relief-dependent) | LOCKED | terrain.py §9.5 biome ladder | Stage 7 (2026-06-10): joint-condition with slope; do NOT lower to hit a coverage target. |
| Mountain slope threshold | mtn_slope_thresh | **0.18 + (1−relief)·0.4** | (0,1) (relief-dependent) | LOCKED | terrain.py §9.5 biome ladder | Stage 7 (2026-06-10): joint-condition with elev. |

### §12.2 — Mountain ceiling (structural finding)

| Name | Symbol | Value | Range | Status | Source | Lock history |
|------|--------|-------|-------|--------|--------|-------------|
| Mountain fraction ceiling | mtn_ceiling | **0.317** | — | OPEN (re-derivation item; see §H-TERRAIN-ASYMMETRY) | `HYPOTHESES.md §H-TERRAIN-ASYMMETRY` (canonical); `ARCHITECTURE.md §9.5.1` (mechanism). | Phase 1 Stage 1 (2026-06-13): 448-world coarse search. Structural property of the joint mtn condition — NOT a calibration failure. A8 criterion: mountain_fraction ≥ 0.9 × mtn_ceiling = 0.285. |

### §12.3 — Water guard constants

| Name | Symbol | Value | Range | Status | Source | Lock history |
|------|--------|-------|-------|--------|--------|-------------|
| Largest-body ceiling | LARGE_BODY_CEILING | **0.08** | (0,1) | LOCKED (§DECISION-LAKE-BODY-CEILING, 2026-06-13) | terrain.py; `ROADMAP.md §DECISION-LAKE-BODY-CEILING` (rationale) | Stage 1c provisional: 0.10. **Supervisor-locked 2026-06-13: 0.08.** 0.08 ≈ 80,000 km² at 100 km²/cell — just below Lake Superior (~82,000 km²). Guard: largest_water_body_fraction > 0.08 and nothing else. |
| Exterior water ceiling | EXTERIOR_WATER_CEILING | **0.12** | (0,1) | RETIRED | terrain.py | Stage 1b: installed as world-acceptance guard. Stage 1c: RETIRED as acceptance guard (mis-specified — area measure on edge-connectivity event). Kept as a diagnostic constant. |

### §12.4 — Foraging returns (Phase 1 Stage 1)

| Name | Symbol | Value | Unit | Status | Source | Lock history |
|------|--------|-------|------|--------|--------|-------------|
| NPP scale factor | NPP_GM2_SCALE | **3400.0** | g/m²/yr | LOCKED | terrain.py | Phase 1 Stage 1 (2026-06-13): npp_gm2 = npp × 3400. Single-point Tallavaara 2018 anchor: forest-onset npp≈0.4 → 1360 g/m²/yr. |
| Shore bonus | SHORE_BONUS_KCAL | **1491.5** | kcal/forager-hr | LOCKED | terrain.py | Phase 1 Stage 1 (2026-06-13): Bird 1997 Meriam reef-flat intertidal mean. Applied to land cells with ≥1 water neighbor. |
| Wetland forage target | — | **1428.3** | kcal/forager-hr | LOCKED | terrain.py | Phase 1 Stage 1 (2026-06-13): Cunningham, Okavango "Wet." |
| Forest forage target | — | **2630.0** | kcal/forager-hr | LOCKED | terrain.py | Phase 1 Stage 1 (2026-06-13): Hill 1987, Ache palm. |
| Savanna forage target | — | **257.7** | kcal/forager-hr | LOCKED | terrain.py | Phase 1 Stage 1 (2026-06-13): Berbesque & Marlowe 2009, Hadza tuber (Table 4). |
| Grassland forage target | — | **1125.0** | kcal/forager-hr | LOCKED | terrain.py | Phase 1 Stage 1 (2026-06-13): Hurtado & Hill 1987, Cuiva root collecting. |
| Desert forage target | — | **1200.0** | kcal/forager-hr | PROVISIONAL | terrain.py | Phase 1 Stage 1 (2026-06-13): O'Connell & Hawkes 1984 range 650–1925. Midpoint used; range too wide to lock without further grounding. |
| Mountain forage target | — | **5387.0** | kcal/forager-hr | LOCKED | terrain.py | Phase 1 Stage 1 (2026-06-13): Rhode & Rhode 2015, limber pine unhulled. |

---

## §13 — Phase 1 Blueprint A: kcal economy (2026-06-14)

### §13.1 — Sugar-cluster supersession (DORMANT-SUPERSEDED for C)

The Sugarscape sugar economy parameters below are **SUPERSEDED-FOR-C** by the kcal economy introduced in Blueprint A. They are declared DORMANT-SUPERSEDED — not deleted (archive discipline). The full kcal-ceiling re-derivation replacing their function is **CC-1 (RECAL-ADJACENT, DEFERRED_MECHANICS.md)**; that is not done here.

| Name | Symbol | Value | Old status | New status | Supersession note |
|------|--------|-------|------------|------------|-------------------|
| Max sugar capacity | c_max | 16 | LOCKED | **DORMANT-SUPERSEDED-FOR-C** | Sugar and kcal cannot integrate (unit incoherence). Sugar economy replaced by kcal reserve. Si β_Si coupling is dormant this round (Si out of scope). CC-1 re-derives the C resource ceiling in kcal. |
| Sugar growback rate | α_growback | 4 | LOCKED | **DORMANT-SUPERSEDED-FOR-C** | Sugar growback has no kcal analogue in Phase 1. Deferred to CC-1. |
| Reserve threshold k_reserve | k_reserve | 5.0 | LOCKED (pool config) | **DORMANT-SUPERSEDED-FOR-C** | Denominated in sugar units; kcal analogue not yet derived. Pool mechanic is dormant in kcal economy (PL-1 seam). |
| Pool draw k_draw | k_draw | 3.0 | LOCKED (pool config) | **DORMANT-SUPERSEDED-FOR-C** | Same as k_reserve. Pool mechanic dormant. |

*Dated: 2026-06-14. Nothing hard-deleted. See ARCHITECTURE.md §12.1-L for the dated decision-log entry.*

### §13.2 — kcal economy placeholders and nominals

All values tagged [PLACEHOLDER] are pending MR-1 (physiological anchoring, DEFERRED_MECHANICS.md). All values tagged [NOMINAL] are pending literature grounding.

| Name | Symbol | Value | Unit | Status | Source | Notes |
|------|--------|-------|------|--------|--------|-------|
| Kcal reserve (full) | reserve_full_kcal | **100,000** | kcal | OPEN [PLACEHOLDER MR-1] | KcalEconomyConfig; phase1_model.py | Physiology estimate: 70 kg adult ~12–15 kg adipose = 100k–115k kcal at normal body composition. NOT an HG-field number. MR-1 pending. |
| Kcal reserve (floor) | reserve_floor_kcal | **20,000** | kcal | OPEN [PLACEHOLDER MR-1] | KcalEconomyConfig; base.py (reserve_floor) | Physiology estimate: ~40% body-weight loss at clinical starvation threshold. NOT an HG-field number. MR-1 pending. |
| Burn rate | burn_kcal_per_day | **2,500** | kcal/day | OPEN [NOMINAL] | KcalEconomyConfig | Nominal adult HG energy expenditure. Tunable. Grounding-refinement pending. |
| Days per month | days_per_month | **30** | days/step | LOCKED | KcalEconomyConfig; ARCH §9.3 OWE-1 | 1 step = 1 month = 30 days (standing constraint). Burn per step = 75,000 kcal. |
| Foraging hours per day | foraging_hours_per_day | **6** | hrs/day | OPEN [NOMINAL] | KcalEconomyConfig | Nominal time-allocation (Ache/Hadza active-foraging hours). Tunable. Grounding pending. |
| Intake per step | — | rate × 6 × 30 = rate × 180 | kcal/step | — | phase1_model.py | Derived: intake = forage_kcal_rate × foraging_hours_per_day × days_per_month. |
| Sex ratio | p_female | **0.5** | — | OPEN | KcalEconomyConfig | Neutral 0.5 default; no environmentally-driven sex-ratio mechanic. Tunable for experiments. |
| Non-rivalrous cap | — | (each agent gets full rate) | — | PROVISIONAL [CC-1] | terrain_field.py game_level | Non-rivalrous harvest: each agent gets full cell rate independently. Rivalry deferred to CC-1 (DEFERRED_MECHANICS.md). |
| Lifespan | lifespan_months | **900** | months | OPEN [PLACEHOLDER] | KcalEconomyConfig | Unit-conversion of legacy max_age_dist (60–100 steps) to months at 1 step=1 month: 900 = 75-year midpoint. Conflict surfaced ARCHITECTURE.md §15. |

### §13.3 — Game return rates (Blueprint A A1.2)

[PROVISIONAL — biome-scaled from return-rate table, pending CC-1 ceiling]

**Value home (one-fact-one-home):** the authoritative derivation of every value below is `SiC_Games_Game_Return_Rate_Table.md §F.2.1` (Representative-value derivation). This table restates the resulting number with a pointer; it does not lead. Reconciled 2026-06-15 (reconcile directive §2/§5).

| Name | Symbol | Value | Unit | Status | Source |
|------|--------|-------|------|--------|--------|
| Forest game target | GAME_KCAL_TARGETS[FOREST] | **5,541** | kcal/forager-hr | PROVISIONAL [NATIVE, handling-only] | **2026-06-15: 7,749 → 5,541** (flat-mean → pursuit-weighted mean, 1,462,745/264). Derivation: §F.2.1. Median cross-check 6,120; both << retired flat-mean 7,749 |
| Savanna game target | GAME_KCAL_TARGETS[SAVANNA] | **518** | kcal/forager-hr | PROVISIONAL [CONVERTED] | All-seasons base encounter (static cell); 745 dry-season intercept = seasonality hook, not static. Derivation: §F.2.1 |
| Grassland game target | GAME_KCAL_TARGETS[GRASS] | **3,001** | kcal/forager-hr | PROVISIONAL [NATIVE] | Hurtado & Hill 1987 direct lift. Derivation: §F.2.1 |
| Desert game target | GAME_KCAL_TARGETS[DESERT] | **1,201** | kcal/forager-hr | PROVISIONAL — **desert method pending supervisor + Bird 2009 Fig 4 (PDF absent from repo)** | Bare midpoint of 641–1,761; **NOT a defensible median**. Bird 2009 (Am. Antiquity 74(1)) read via image render: "641–1,761" = search-inclusive *overall hunt-type* rates (sand monitor ≈641) — the correct desert basis (§F.1); Table 2 post-encounter thousands are a different denominator, **not** to be used. Frequency-weighted overall rate skews below midpoint (≈700–900). Unchanged pending supervisor. Derivation: §F.2.1 |
| ~~Intertidal game~~ | — | — | — | **RECLASSIFIED → FORAGE (2026-06-15)** | Intertidal shellfishing is forage, not game (double-count fix); see SHORE_BONUS_KCAL=1491.5 and game table §F.2/§F.2.1. No GAME_KCAL_TARGETS key |
| Wetland game | — | **0** (UNANCHORED) | — | UNANCHORED | No source found (SiC_Games_Game_Return_Rate_Table.md §F.2) |
| Mountain game | — | **0** (UNANCHORED permanent) | — | UNANCHORED-PERMANENT | No source exists in HG literature |
| Water game | — | **0** (out of scope) | — | OUT-OF-SCOPE | Fish/aquatic game out of model scope |

---

## Discrepancy resolution log

The following D-items from ARCHITECTURE.md §15 are resolved by this document:

| ID | Discrepancy | Resolution |
|----|-------------|------------|
| D1 | τ_trickle: ROADMAP=0.3, CLAUDE.md=0.05 | **0.3 is correct** (Stage 4.3 raised from blueprint 0.05). CLAUDE.md was stale. Corrected here (§8 above). |
| D2 | σ_inherit: two entries (0.05 and 0.10) in CLAUDE.md | **0.10 is current** (Stage 5.2 raised from Stage 3.3's 0.05). Both preserved in history column (§7 above). |
| D3 | p_fission_Si: CLAUDE.md=0.28 (Stage 4.3), ROADMAP=0.065 (Stage 4.4) | **0.065 is current** (Stage 4.4 locked). 0.28 was the Stage 4.3 value at β=2 (pre-grid-rescale). Corrected here (§7 above). |
| new | age_init_upper_frac: CLAUDE.md=0.25, production YAML=0.5 | **0.5 is current** (Stage 4.4 patch; production configs). CLAUDE.md was stale. Corrected here (§9 above). |
| new | k_pool_cap: ROADMAP=20.0, production YAML=0.0 | **0.0 is production value** (Stage 5.1 configs). ROADMAP had Stage 4.3 design intent (20.0). Noted as open-flag in §6 above. |

---

*PARAMETERS.md extracted 2026-06-08. Supersedes interim locked-param tables in `sic_games/CLAUDE.md`
and `docs/ROADMAP.md`. Maintained by Code; updated any time a parameter is locked, swept, or retired.*
