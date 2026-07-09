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
| Mountain elevation threshold (DEFAULT gate) | mtn_elev_thresh | **0.72 + (1−relief)·0.5** | (0,1) (relief-dependent) | LOCKED (default only) | terrain.py §9.5 biome ladder | Stage 7 (2026-06-10): joint high∧steep gate. Unanchored design constant. Still the default; the `orogenK` alpine path bypasses it (tree-line classification). Do NOT lower to hit a coverage target — orogeny is the sanctioned mountain-dominant route. |
| Mountain slope threshold (DEFAULT gate) | mtn_slope_thresh | **0.18 + (1−relief)·0.4** | (0,1) (relief-dependent) | LOCKED (default only) | terrain.py §9.5 biome ladder | Stage 7 (2026-06-10): joint-condition with elev. NB `slope` is the PER-WORLD max-normalized gradient (dimensionless), not a physical grade — doubly unanchored; another reason orogeny uses tree-line, not slope. |
| Orogeny massif gain | OROGEN_MASSIF_GAIN | **1.6** | ≥0 | LOCKED | terrain.py; RESULTS §R-59 | 2026-07-08: additive low-freq uplift dome weight (pre-normalization) — real topographic prominence. orogenK=0 ⇒ off, bit-exact. |
| Orogeny relief boost | OROGEN_RELIEF_BOOST_M | **2000.0 m** | ≥0 | LOCKED | terrain.py; RESULTS §R-59 | 2026-07-08: extra peak-to-trough added to reliefAmpM under orogeny → ~4 km range so lapse-cooling clears the tree-line. |
| Alpine tree-line isotherm | TREELINE_WARMEST_MONTH_C | **10.0 °C** | — | LOCKED (lit-anchored) | terrain.py; `LITERATURE.md` (Köppen; Körner & Paulsen 2004) | 2026-07-08: Köppen 10 °C WARMEST-MONTH air isotherm (forest/alpine-tundra ET boundary), consistent with Körner 2004's 6.7 °C growing-season soil mean. Replaces the unanchored high∧steep gate for the orogenic alpine biome. **Corrected from a mis-slotted 6.4 (soil growing-season) value 2026-07-08.** |

### §12.2 — Mountain ceiling (structural finding)

| Name | Symbol | Value | Range | Status | Source | Lock history |
|------|--------|-------|-------|--------|--------|-------------|
| Mountain fraction ceiling (DEFAULT gate) | mtn_ceiling | **0.317** | — | RESOLVED — bounds the DEFAULT high∧steep gate only; SUPERSEDED for mountain-dominant worlds by orogeny (2026-07-08). See §H-TERRAIN-ASYMMETRY. | `HYPOTHESES.md §H-TERRAIN-ASYMMETRY` (canonical); `ARCHITECTURE.md §9.5.1` (mechanism). | Phase 1 Stage 1 (2026-06-13): 448-world coarse search. Structural property of the joint high∧steep gate. Still bounds the default gate. The `orogenK` alpine preset (real uplift massif + Körner tree-line, RESULTS §R-59) reaches alpine ≈ 0.59 (temperate) — the "redesigned generator" the finding deferred. |

### §12.3 — Water guard constants

| Name | Symbol | Value | Range | Status | Source | Lock history |
|------|--------|-------|-------|--------|--------|-------------|
| Largest-body ceiling | LARGE_BODY_CEILING | **0.08** | (0,1) | LOCKED (§DECISION-LAKE-BODY-CEILING, 2026-06-13) | terrain.py; `ROADMAP.md §DECISION-LAKE-BODY-CEILING` (rationale) | Stage 1c provisional: 0.10. **Supervisor-locked 2026-06-13: 0.08.** 0.08 ≈ 80,000 km² at 100 km²/cell — just below Lake Superior (~82,000 km²). Guard: largest_water_body_fraction > 0.08 and nothing else. |
| Exterior water ceiling | EXTERIOR_WATER_CEILING | **0.12** | (0,1) | RETIRED | terrain.py | Stage 1b: installed as world-acceptance guard. Stage 1c: RETIRED as acceptance guard (mis-specified — area measure on edge-connectivity event). Kept as a diagnostic constant. |

### §12.4 — Foraging returns (Phase 1 Stage 1)

Cell values use the **lognormal `(mean, std)`** draw (MECHANISMS §9a.6). `FORAGE_KCAL_STD[b]` = std where literature-anchored; biomes absent from that dict use **std = 10% of the mean** (`DEFAULT_STD_FRAC`, supervisor rule 2026-06-15).

| Name | Symbol | Mean | Std (kcal/hr) | Status | Source / lock history |
|------|--------|------|------|--------|--------|
| NPP scale factor | NPP_GM2_SCALE | **3400.0** | — | LOCKED | npp_gm2 = npp × 3400. Tallavaara 2018 anchor: npp≈0.4 → 1360 g/m²/yr (2026-06-13). |
| Shore bonus | SHORE_BONUS_KCAL | **1491.5** | — | LOCKED | Bird 1997 Meriam reef-flat intertidal mean; additive on land-shore cells (2026-06-13). |
| Wetland forage | FORAGE_KCAL_STD[WETLAND] | **1428.3** | **3362** [LIT] | LOCKED (mean) | Cunningham diss (A1.4): mean(Wet)=1428.3, median(Wet)=558.7 (n≈286, skewed) → lognormal std (CV 2.35). Real USO-foraging spread (2026-06-15). |
| Forest forage | FORAGE_KCAL_STD[FOREST] | **2630.0** | **600** [LIT] | LOCKED (mean) | Hill 1987, Ache palm. Std = spread across palm-product rates {2356,3219,2436,2243,1331} (p.20). |
| Savanna forage | FORAGE_KCAL_STD[SAVANNA] | **257.7** | **182.1** [LIT] | LOCKED (mean) | Berbesque & Marlowe 2009 Table 4: female tuber mean 257.7, **SD 182.1** (CV 0.71) — direct literature SD (2026-06-16). |
| Grassland forage | — | **1125.0** | **112.5** [10%-DEFAULT] | LOCKED (mean) | Hurtado & Hill 1987, Cuiva root. Std: 10% default (source not in repo). |
| Desert forage | FORAGE_KCAL_STD[DESERT] | **1200.0** | **368** [RANGE-DERIVED] | PROVISIONAL | O'Connell & Hawkes 1984 range 650–1925. Midpoint mean; std = (1925−650)/√12 (uniform-range) — 2026-06-15. |
| Mountain forage | — | **5387.0** | **538.7** [10%-DEFAULT] | LOCKED (mean) | Rhode & Rhode 2015, limber pine unhulled. Std: 10% default (source not in repo). |

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
| Kcal reserve (full) | reserve_full_kcal | **130,000** | kcal | ANCHORED (Cahill 1970) — was 100,000 [PLACEHOLDER] | KcalEconomyConfig; phase1_model.py | Cahill 1970 "Starvation in man": lean adult total mobilizable fuel ≈130k (70 kg/166k reference → ~60 kg lean). Flat-burn model ⇒ survival=(full−floor)/BURN=110k/2500≈44 d total starvation (lean-adult range; hunger-strike ~45–61 d). Corrected 2026-07-08 (100k gave 32 d = too fragile). |
| Kcal reserve (floor) | reserve_floor_kcal | **20,000** | kcal | ANCHORED (Cahill 1970) | KcalEconomyConfig; base.py (reserve_floor) | Starvation-death residual ≈ 3 kg fat (Cahill: death when fat<3 kg & protein>50% depleted); 20k conservative (≈2.1 kg fat). |
| Burn rate | burn_kcal_per_day | **2,500** | kcal/day | OPEN [NOMINAL] | KcalEconomyConfig | Nominal adult HG energy expenditure. Tunable. Grounding-refinement pending. |
| Days per month | days_per_month | **30** | days/step | LOCKED | KcalEconomyConfig; ARCH §9.3 OWE-1 | 1 step = 1 month = 30 days (standing constraint). Burn per step = 75,000 kcal. |
| Foraging hours per day | foraging_hours_per_day | **6** | hrs/day | OPEN [NOMINAL] | KcalEconomyConfig | Nominal time-allocation (Ache/Hadza active-foraging hours). Tunable. Grounding pending. |
| Intake per step | — | rate × 6 × 30 = rate × 180 | kcal/step | — | phase1_model.py | Derived: intake = forage_kcal_rate × foraging_hours_per_day × days_per_month. |
| Sex ratio | p_female | **0.5** | — | OPEN | KcalEconomyConfig | Neutral 0.5 default; no environmentally-driven sex-ratio mechanic. Tunable for experiments. |
| Non-rivalrous cap | — | (each agent gets full rate) | — | PROVISIONAL [CC-1] | terrain_field.py game_level | Non-rivalrous harvest: each agent gets full cell rate independently. Rivalry deferred to CC-1 (DEFERRED_MECHANICS.md). |
| Lifespan | lifespan_months | **900** | months | OPEN [PLACEHOLDER] | KcalEconomyConfig | Unit-conversion of legacy max_age_dist (60–100 steps) to months at 1 step=1 month: 900 = 75-year midpoint. Conflict surfaced ARCHITECTURE.md §15. |

### §13.3 — Game return rates (Blueprint A A1.2)

[PROVISIONAL — biome-scaled from return-rate table, pending CC-1 ceiling]

**Value home (one-fact-one-home):** the authoritative derivation of every value below is `SiC_Games_Resource_Return_Rate_Table.md §3.2` (Representative-value derivation). This table restates the resulting number with a pointer; it does not lead. Reconciled 2026-06-15 (reconcile directive §2/§5).

**Cell-value distribution (2026-06-15, supervisor-directed):** each biome's cells are drawn from a literature-anchored **lognormal `(mean, std)`** via a terrain-coupled deterministic rescale — see MECHANISMS §9a.6 / ARCHITECTURE §12.1-N. `GAME_KCAL_TARGETS[b]` = mean; `GAME_KCAL_STD[b]` = std. Where std is **PENDING** (not yet sourced) the field falls back to legacy mean-only scaling.

| Name | Symbol | Mean | Std (kcal/hr) | Status | Source |
|------|--------|------|------|--------|--------|
| Forest game | GAME_KCAL_TARGETS / STD[FOREST] | **5,541** | **4,043** [NATIVE] | PROVISIONAL [NATIVE, handling-only] | Mean: pursuit-weighted of 7 Hill 1987 species (1,462,745/264). Std: weighted std of the 7 species (CV 0.73). §3.2 |
| Savanna game | GAME_KCAL_TARGETS / STD[SAVANNA] | **518** | **1158** [LIT-DERIVED] | PROVISIONAL [CONVERTED] | Mean: all-seasons base encounter (745 dry-season = seasonality hook). Std: Hawkes 1991 small-game income 0.162±0.362 animals/day → CV 2.24 × mean (hunting is high-variance; 10% would understate). **Supervisor-review** — derived from income variance, not a direct rate-SD. §3.2 |
| Grassland game | GAME_KCAL_TARGETS[GRASS] | **3,001** | **300.1** [10%-DEFAULT] | PROVISIONAL [NATIVE] | Mean: Hurtado & Hill 1987 direct lift. Std: 10% default (single-source mean, no spread). §3.2 |
| Desert game | GAME_KCAL_TARGETS / STD[DESERT] | **730** | **210** | **SET 2026-06-15 (supervisor-approved)**; PROVISIONAL pending CC-1 | **1,201 → 730:** bout-frequency-weighted mean of search-incl. overall hunt-type rates — sand monitor (641, n=612), perentie (765, n=78), bustard (~1,300, n=91) = 570,262/781 (median 765). Std: weighted std of the 3 rates (CV 0.29). Bird 2009 (Am. Antiquity 74(1)), read via image render. §3.2 |
| ~~Intertidal game~~ | — | — | — | **RECLASSIFIED → FORAGE (2026-06-15)** | Intertidal shellfishing is forage, not game (double-count fix); see SHORE_BONUS_KCAL=1491.5 and game table §3.1/§3.2. No GAME_KCAL_TARGETS key |
| Wetland game | — | **0** (UNANCHORED) | — | UNANCHORED | No source found (SiC_Games_Resource_Return_Rate_Table.md §3.1) |
| Mountain game | — | **0** (UNANCHORED permanent) | — | UNANCHORED-PERMANENT | No source exists in HG literature |
| Water game | — | **0** (out of scope) | — | OUT-OF-SCOPE | Fish/aquatic game out of model scope |

---

## §14 — Demographic core: Siler mortality + IBI fertility + life-history (R-2…R-9; MODEL_SPEC §4.2, §4.5)

| Name | Value | Status | Grounding / history |
|------|-------|--------|---------------------|
| Siler a1 (infant) | **0.157**/yr | LOCKED | Aché forest, Gurven & Kaplan 2007 Tbl 2 (M-1). Sex-split a1 ♀0.184/♂0.130. §4.2.1/§4.2.3 |
| Siler b1 | **0.721** | LOCKED | " |
| Siler a2 (Makeham) | **0.013**/yr | LOCKED | " — the ONLY term the world modulates (a2_mult) |
| Siler a3 (Gompertz) | **4.80e-5**/yr | LOCKED | " . Sex-split ♀3.89e-5/♂5.71e-5 |
| Siler b3 | **0.103** | LOCKED | " . Reproduces e₀=36.5, e₁₅=38.3, mode=71 |
| **De-warfared Siler** (ACHE_FOREST_NATURAL) | a1=**0.1611**, b1=**0.6775**, a2=**0.00813**, a3=**3.781e-5**, b3=**0.1025** → e₀=**42.7** | OPT-IN (biome runs) | Aché-total minus external-warfare (w(x): 0 unweaned / 0.35 ages 4–59 / 0.25 ≥60); re-fit. Change in a2 (warfare = adult Makeham). Fixes the R-15 double-count → density-disease regulates to ~34–36 (Aché-matched). §4.6.1 |
| Childhood M:F ratio | **0.71** | LOCKED | H&H 1996 Ch.6 forest (M-3); scales a1 (female-higher) |
| Adult M:F ratio | **1.47** | LOCKED | " ; scales a3 (male-higher) |
| Fecundability | **~0.12**/mo | LOCKED (calibrated) | bisection to Aché IBI=37 mo / TFR≈8; r=+3.3%/yr emergent. §4.2.5 |
| Menarche / menopause | **180 / 504** mo | LOCKED | 15/42 yr fertile window |
| IBI lactational refractory | **30** mo | LOCKED | Aché |
| SRB (male) | **0.512** | LOCKED | 105:100 |
| reserve_full | **130 000** kcal | ANCHORED (Cahill 1970) | lean-adult total mobilizable fuel; ~44 d flat-burn survival. Was 100k. §4.5.3 |
| reserve_floor | **20 000** kcal | ANCHORED (Cahill 1970) | starvation-death residual ≈3 kg fat |
| burn (maintenance) | **75 000** kcal/mo | LOCKED | 2500 kcal/day × 30 |
| forage_age_min | **180** mo | PROVISIONAL | foraging competence (15 yr); Kaplan 2000. η + cons + reserve scaling key. §4.5.1 |
| eta_min | **0.0** | PROVISIONAL | newborn production (linear JV-1 approx; convex Kaplan deferred) |
| eta_old | **0.4** | PROVISIONAL | elder efficiency |
| cons_min | **0.3** | PROVISIONAL | neonate maintenance fraction; Kaplan 2000 / FAO. §4.5.2 |
| reserve_min | **0.3** (= cons_min) | LOCKED (constraint) | cap ≥ 1-step burn (C.2b/R-9); Pontzer body-mass. §4.5.3 |

## §15 — a2 mortality modulators + condition + provisioning (Phase C / biome; R-5…R-14; §4.3.3, §4.5.4, §4.6)

| Name | Value | Status | Grounding / history |
|------|-------|--------|---------------------|
| μ_max (nutrition synergy) | **2.5** | PROVISIONAL / BANKED | Pelletier 1994 (~2–3× malnutrition mortality). The **Carbon mechanism** (R-14) — inert under egalitarian sharing. §4.3.3 |
| risk_cap (terrain accident) | **3.0** | LOCKED | M-2; accidents ~10% HG deaths (Hiwi). Off in biome runs |
| dens_delta (density-disease) | **1.0** default; **δ≥4 regulates** (R-13) | OPEN / FREE | the free lever. δ≥4 holds pop below food ceiling → starvation→0 (R-13). **δ calibration pending** |
| dens_rho_half | **0.2** agents/km² | OPEN | density-disease half-saturation |
| a2_cap | **5.0** | LOCKED | cap on a2_eff multiplier (red-team n-1) |
| pathogen_gamma | **0.0** (off); bracketed {0.5, 1.0} | OPEN / BRACKETED | NPP-proxy exponent; Cashdan 2014 direction; magnitude bracketed (prevalence→mortality leap). §4.6.3 |
| pathogen_cap | **3.0** | PROVISIONAL | symmetric cap [1/cap, cap] |
| pathogen_npp_ref | **0** → terrain-mean NPP | PROVISIONAL | Aché-forest reference (neutral biome) |
| condition_alpha (S0) | **0.25** | BANKED (opt-in OFF) | EMA ~2.4-mo half-life; S0 = Carbon mechanism (R-11/R-14); `enable_condition` default off |
| provision_self_keep (S1) | **1.0** (=C.2b overflow); <1 = child-priority | OPEN / KEPT | shortfall-sharing knob; band-level supersedes as variance vehicle (R-14). §4.5.4 |

## §16 — Resource-ecology + biome + game seams (R-6…R-14; §4.1.4–8, §4.3, §4.4)

| Name | Value | Status | Grounding / history |
|------|-------|--------|---------------------|
| **CC-1 capacity mode** | **'linear' (default) / 'tallavaara' (FITTED)** | linear PROVISIONAL, tallavaara **FITTED 2026-07-02** | `NPPCapacityField(…, mode=…)`. linear = provisional rows below; tallavaara = the fitted segmented regression (next 4 rows). §4.3.1; R-36 |
| CC-1 density slope | **0.3** | PROVISIONAL (linear mode) | Tallavaara 2018; density = min(0.5, 0.3·npp_gm2/1360). §4.3.1 |
| CC-1 density cap | **0.5**/km² | PROVISIONAL (linear mode) | Tallavaara high bound |
| NPP threshold | **1360** g/m²/yr | PROVISIONAL (linear mode) | Tallavaara low/high |
| NPP_GM2_SCALE | **3400** | PROVISIONAL | npp_gm2 = npp × 3400 (both modes) |
| CC-1 Tallavaara coeffs (TALL_INT / TALL_B1 / TALL_U1 / TALL_BP) | **−0.1352714 / 0.0028623 / −0.0030745 / 1371.664** | **FITTED 2026-07-02** | `ln(density#/100km²) = INT + B1·NPP + U1·(NPP−BP)₊`; extracted from Tallavaara data-analyses SI, cross-checked vs Dataset_4 (357 groups, median 11.9). ~57% of linear capacity. `capacity.py::density_tallavaara`. §4.3.1; R-36 |
| world-lottery archetypes | forest/savanna/desert/montane/mixed (NPP ~175→856) | DIAGNOSTIC | `terrain.py::world_lottery(seed, archetype=None)`, `WORLD_ARCHETYPES` — per-world knob draws to characterize CC-1 across productivity; arid-biased (median ~500 vs forager ~900). R-36/R-37 |
| seasonality s_min | **0.4** (test) | PROVISIONAL | forage seasonal trough; biome-specific per §4.1.4 (forest flat, llanos high) — NOT yet biome-wired. R-6/R-10 (forest-as-seasonal = artifact, R-14) |
| depletion deplete_rate | **0.30** | PROVISIONAL (phenomenological, NOT lit-anchored) | GD-1 freshness. §4.4.2 |
| depletion regrow_rate | **0.10** | PROVISIONAL (phenomenological) | " |
| move_cost_flat | **0.0** (realistic) | OPEN | decision-friction mobility knob; model under-mobile vs Binford (R-8); realistic ≈0. §4.4.3 |
| temperature (climate seam) | **14.0** °C | PLACEHOLDER | constant; spatial/seasonal field = CL-1 deferred. §4.3.2 |
| humidity (climate seam) | **0.70** | PLACEHOLDER | " |
| game_mobility | **FOREST 0, DESERT 0, SAVANNA 0.2, GRASS 1.0** | SEAM (mechanic deferred) | Binford 2001 / forager-collector; ≈0 in calibration biomes by construction. §4.1.8 |
| enable_game | **False** (default) | OPT-IN | Two-stream forage+meat economy (G.1+G.2). Default off = forage-only back-compat. §4.5.5 |
| game_meat_frac (mf) | **FOREST 0.55, DESERT 0.45, SAVANNA 0.38, GRASS 0.66** | LIT-ANCHORED (Cordain 2000 Table 2) | diet animal fraction = hunted/(plant+hunted), terrestrial-renormalized (fished dropped). `terrain.MEAT_FRAC`. §4.5.5 |
| meat sharing κ | = substrate `contest_exponent` | STRATEGY LEVER | meat split Cred-weighted (φ+ε)^κ for Carbon; forage forced κ=0. κ=0 ⇒ energy-conserving/inert (Silicon). §4.5.5 |

> **§14–16 currency note (2026-06-20):** added to close the audit gap — PARAMETERS.md had not been updated
> since 2026-06-14 (§13) through the entire demographic + resource-ecology + biome + game arc (R-2…R-14).
> Many are PROVISIONAL/OPEN by design (the model is mid-build); the key **un-calibrated** value is the
> density-disease **δ** (R-13 shows it regulates; the forager-e₀/density calibration is the pending step).

---

## §17 — Carbon status: Cred-vector + prowess + paternity (R-18…R-21; MODEL_SPEC §4.5.6–9, §4.8.5, §4.8.12)

| Name | Value | Status | Grounding / history |
|------|-------|--------|---------------------|
| enable_cred_status | **False** (default) | OPT-IN | meat/contest weight reads accumulated `cred` not `φ`. §4.5.6 |
| cred_seed_sigma | **0.5–0.6** | LOCKED (run-config) | founder log-status spread (lognormal median 1). §4.5.6 |
| cred_inherit_sigma | **0.1** | LOCKED | lineage-copy noise (mean-1 lognormal). §4.5.7 |
| enable_prowess_facet | **False** (default) | OPT-IN | achieved (hunting-reputation) facet joins the Cobb–Douglas contest weight. §4.5.7 |
| **prowess_decay** (λ) | **0.05** (family stack) / 0.10 (E.3 lottery) | **LOCKED 2026-06-29** | prowess EMA rate = reputation persistence (Smith 2004). Family stack RAISED 0.10→0.05 (half-life ~7→~14 mo) to lift full-stack status→RS 0.08→0.13; E.3 lottery keeps 0.10 (m=5→0.19). §4.8.12 |
| sex_division | **1.0** (full-stack) | OPT-IN | prowess prod-credit split among ADULT producers (age≥menarche), NOT dependent sons (the §4.8.12 corruption fix). §4.5.7 |
| enable_paternity | **False** (default) | OPT-IN | a father assigned at conception (lottery) or = the durable partner (pair-bonds). §4.5.7 |
| **mate_choice_strength** (m) | **5** (banded) / 4 (IFD) | **LOCKED 2026-06-29** | prowess-weighted mate-choice skew → status→RS r≈0.19 (von Rueden). Banded substrate needs m=5 (band-territory gate dilutes skew); IFD m=4 (R-19). §4.8.5 |
| patriline_weight (pw) | **0.5** | LOCKED | father-vs-mother weight in bilateral lineage inheritance. §4.5.7 |
| lineage_reversion (ρ) | **0.1** | LOCKED | mean-reversion of inherited lineage toward the fixed founder anchor (the homeostat). §4.5.7 |
| paternal_provision_frac | **0.5** (forager societies) | OPT-IN | father gives this frac of overflow to own children. §4.5.7 |
| assortative_strength (α) | **0** (B+ paired control) | OPT-IN | B++ status-similarity mate kernel; 0 = no assortment. §4.5.8 |
| homogenize_cred / _prowess | **False** | ABLATION-ONLY | flatten within-band status (lumping test); flatten within the connected band (mate-gate hood), not the cell. §4.8.5 |

## §18 — Social structure: storage · morph · bands · families · band-society · polygyny (F.1–F.3c; §4.5.11, §4.8.1–12)

| Name | Value | Status | Grounding / history |
|------|-------|--------|---------------------|
| enable_storage / storable_fraction / store_capacity_reserves | False / **0.7** / **12.0** | OPT-IN, **LIT-CALIBRATED 2026-07-07** | collective band granary. storable_fraction 0.5→**0.7** (lit 0.5–0.8, seasonal storers live off stores); store_capacity_reserves 3→**12** (=~16 mo ≈ Halstead 1–2 yr granary; old 4 mo was < one annual cycle). storage_decay canonical 0.05→**0.02**/mo (~22%/yr, lit 10–30%). Storage survey (Testart 1982, Halstead & O'Shea 1989). §4.5.11 / MODEL_SPEC §4.8.21b |
| storage_temp_threshold_c | **15.25** °C | LIT-ANCHORED (but INERT — temperature is a constant-14°C placeholder; realistic config sets 100 = storage-everywhere) | Binford 2001 ET storage threshold. §4.5.11 |
| storage_seasonality_gated / storage_seasonality_threshold | **False / 0.25** | OPT-IN (SUPERSEDED by morph_aquatic, R-47) | R-46: gate the store on biome SEASONAL AMPLITUDE. Makes forest egalitarian but MIS-ORDERS desert (→complex). Retained ablatable; superseded by the aquatic morph gate. §4.5.10 |
| morph_aquatic_gated / morph_aquatic_threshold / morph_npp_floor | **False / 0.15 / 500** (candidate CANONICAL, pending sign-off) | OPT-IN | R-47/R-48: storage stays a broad survival BUFFER; a band morphs COMPLEX only if BOTH (a) seasonal aquatic glut `mean(wateracc×seasonal_amp) ≥ threshold` (aseasonal watery forest [Mbuti] fails) AND (b) productive setting `mean(npp_gm2) ≥ npp_floor` (poor desert oasis [Kalahari, npp≈400] fails; Nile-floodplain [≳550] can pass — the true-desert vs river-desert distinguisher). → forest EGALITARIAN (aseasonal), desert EGALITARIAN+surviving (poor setting), montane/savanna COMPLEX (seasonal productive rivers). The correct forager-complexity signature (Testart/Ames/Kelly). Off ⇒ ungated morph, bit-exact. thr/floor PROVISIONAL (sweep-chosen from R-47 occupied-cell data). §4.5.10 |
| storage_decay | **0.05** (S.3) | OPT-IN | per-step granary spoilage. §4.5.11 |
| enable_morph / morph_settle_steps | False / **60–300** | OPT-IN | society morph (egal→complex→stratified) hysteresis timer (~1 gen). §4.5.11 |
| ~~storage_tether_reserves~~ | **RETIRED 2026-06-29** | RETIRED | band-aid for pre-bands max-occ-2; morph now fires from emergent bands alone (run_3h). §4.5.11/§4.8.5 |
| group_safety_max / _scale, group_mate_min / _floor | **8 / 15, 15 / 0.2** | OPT-IN | E.1/E.2 movement grouping drives (risk-dilution + mate-access). §4.8.1 |
| founder_buffer_steps | **0** (default) | OPT-IN | carried mobile reserve bridging the founding transient (bare-forage only). §4.8.3 |
| enable_bonded_mating / **bonded_mate_radius** | False / **1** | OPT-IN/**LOCKED** | F.1/F.2 mate-gate: a birth needs an unrelated adult male within the band (Chebyshev r). r=1 sustains turnover; r=0 (per-cell) → extinction. §4.8.4 |
| enable_band_risk / band_risk_penalty | **False (SHELVED)** | SHELVED | F.2 risk-dilution mortality = death spiral; risk-dilution belongs in E.1 movement. Default OFF, do not use. §4.8.6 |
| enable_pair_bonds / divorce_rate / family_maturity_months | False / 0 / **180** | OPT-IN | F.3a/b persistent monogamous pair-bonds + nuclear-family co-movement; child detaches at maturity (Kaplan 2000). §4.8.7 |
| **polygyny_rate / max_wives** | **0.3 / 3** (realistic) / 0 / 1 (monogamy) | OPT-IN | F.3a modest polygyny — high-status males take ≤max_wives wives (von Rueden; the status→RS amplifier). §4.8.12 |
| enable_band_affiliation / band_cohesion | False / **0.3** | OPT-IN | F.3c-1 collective-identity-vector band_id + cohesion movement drive → ~25 non-kin bands. §4.8.8 |
| band_split_size / band_merge_size / band_base_tolerable | **45 / 10 / 25** | OPT-IN | band fission/fusion thresholds (Birdsell/Wobst ~25; band_split = hard cap). §4.8.8/§4.8.10 |
| enable_dynamic_bands / assabiyah_gain / assabiyah_decay | False / **0.05 / 0.02** | OPT-IN | F.3c-3 condition-dependent tolerable_size = base+(cap−base)·assabiyah; solidarity from surplus (Ibn Khaldun). §4.8.10 |
| enable_band_family_knobs | **False** (default) | OPT-IN | F.3c-2b reproduction reads the band-society family knobs via additive-delta-from-egalitarian (egalitarian band = global EXACTLY → E.3 safe). §4.8.11 |
| enable_leader_coherence / leader_coherence_gain | **False / 0** | OPT-IN | Stage 1a: 2nd cohesion source from a band's top-status member, Boehm-gated (`LEADER_SOCIETY_WEIGHT` egalitarian 0 / complex 0.5 / stratified 1.0). Gain UNANCHORED (bracket). Built + unit-valid; behavioural benchmark DEFERRED to the dynastic stage (R-30). §4.8.13 |
| _(dependency, R-34)_ | — | — | `enable_leader_coherence`, `enable_size_repulsion`, `enable_malnutrition_fission` are **no-ops unless `enable_dynamic_bands=True`** (they live in that block). `enable_resource_directed_fusion` + `enable_genealogy_log` are independent. |
| enable_ascribed_mate_choice / ascribed_mate_strength | **True / 2.5** (CANONICAL 2026-07-02) | **CANONICAL** | cred (ascribed) enters mate-choice, society-gated (`MATE_ASCRIBED_WEIGHT` egalitarian 0.25 / complex 0.6 / stratified 1.0). Mate weight = `(prowess·cred^(a·sw))^mate_choice_strength`. **a=2.5 pinned** → composite status→RS ≈0.13 (von Rueden; sweep, Gini stable/no runaway). Stratified ~0.19 endpoint pending settlement-arc validation. Flag OFF ⇒ prowess-only, bit-exact. *Headline-result reframe (R-19/R-21/R-26 → gated von-Rueden) HELD pending settlement-arc validation.* |
| enable_size_repulsion / repulsion_gain / repulsion_midpoint / repulsion_width | **False / 0 / 25 / 6** | OPT-IN | Stage 1b: Johnson scalar-stress DISPERSIVE term (logistic in band size, Alberti shape), society-relieved (`REPULSION_SOCIETY_FACTOR` egal 1.0 / complex 0.5 / stratified 0.25). midpoint=Wobst-band, width=Alberti re-anchored to band scale; gain UNANCHORED. Trims tail (R-29; the "44→31 cap" corrected in R-31 — dormant threshold). §4.8.13 |
| enable_malnutrition_fission / malnutrition_fission_gain / malnutrition_starv_rate / malnutrition_ema_alpha | **False / 0 / 0.05 / 0.3** | OPT-IN | M2: severe-scarcity fission of LARGE bands (dispersal substitutes for starvation death). Signal = per-band REALIZED starvation-rate EMA (`_band_starv_ema`), NOT `_condition` (survivor-biased, R-32). Size-gate from base floor; gain/rate UNANCHORED. Validated substitution test (R-33). §4.8.14 |
| enable_resource_directed_fusion / fusion_search_radius | **False / 25** | OPT-IN | F: a band < merge_size joins the RICHEST (`_band_surplus`) neighbour within radius (else nearest) — starving remnants merge into well-provisioned bands (Wiessner hxaro). Off ⇒ nearest, bit-exact. §4.8.14 |
| enable_genealogy_log | **False** (default) | OPT-IN | Stage 2: pure-observer append-only log of births/deaths (uid, mother, father, lineage, band_id, step, cred) → `dump_genealogy(path)`. Bit-exact when off/on (write-after-step). §4.8.15 |
| ~~season_aggregation~~ | **REMOVED** 2026-07-01 | — | RETIRED (DE-7): mis-signed lean→fission + inert; superseded by M2 malnutrition fission. §4.8.14 |
| enable_life_history / enable_provisioning | **True / True** (CANONICAL 2026-07-02) | **CANONICAL** | Kaplan-2000 childhood: auto-builds a MONTH-scaled `LifeHistoryConfig` (`forage_age_min=180`, `forage_age_max_offset=120` — class defaults are legacy YEARS) → graded η/consumption/reserve + band provisioning of the child deficit. Was OFF (newborns foraged at adult rate). Retires JV-1. Fixed 3 latent bugs (max_age dead code→maxage 899; negative-η complex crash→clamp; founder-lh). §4.8.17; R-38 |
| enable_marriage_aggregation / aggregation_period / aggregation_season_threshold | **False / 12 / 0.6** | OPT-IN | "the gathering": convene bands every `period` months when `ClimateField.season() ≥ threshold` (spring pulse). Decouples mate-finding (seasonal/regional) from reproducing (year-round pair-bond). Mauss/Steward/Lee/Conkey. §4.8.18; R-39 |
| aggregation_radius / aggregation_site_sep / aggregation_residence / aggregation_rank_homogamy | **8 / 4 / "flexible" / False** | OPT-IN | connubium radius (terrain/lit-sourced); site separation; residence ∈ virilocal/uxorilocal/flexible (Marlowe 2004/Hill 2011/Ember&Ember 1971 — whole-world compare deferred); rank-homogamy = similarly-ranked lineages marry (R-35 anti-flattening). residence="flexible"/homogamy=False ⇒ bit-exact legacy pairing. §4.8.18 |
| enable_productivity_mobility | **False** (default) | OPT-IN | diffusion STRIDE scales ∝1/static-local-NPP (Kelly 1995/Binford 2001 mobility∝1/productivity); off ⇒ bit-exact r=1. §4.8.19; R-39 |
| mobility_base_radius / mobility_max_radius / mobility_npp_ref / mobility_npp_floor / mobility_exponent | **1 / 6 / 900 / 50 / 1.0** | **PROVISIONAL (bracket)** | `r = clamp(round(base·(npp_ref/max(local_npp,floor))^exp), base, r_max)`; npp_ref = forager-median g/m²/yr; **locking for canonical runs needs supervisor sign-off**. §4.8.19 |
| **comove_footprint** | **1** (realistic/CANONICAL 2026-07-03) / 0 (default OFF) | **CANONICAL** | central-place dispersed-camp fix (R-42/R-43/R-44): followers scatter to the lowest-occupancy land cell within Chebyshev **1** of the head (a 3×3 ≈ 900 km² monthly camp) instead of exact-snapping onto the mother's cell. **Recovers the biome→society collapse in EVERY biome** (savanna 8→243, montane 14→276, mixed 18→519, forest 145→426, desert 0→64) while PRESERVING status→RS +0.127 / band_awt 26 / Gini 0.21 / %complex 83 (R-44); eq_pop re-baselines ~2× up (removes the co-movement population brake). 0 ⇒ bit-exact exact-snap. §4.8.20 |
| comove_anticipate / comove_footprint_scaled / comove_provision_exclude | **False / False / False** | OPT-IN (NOT chosen) | the other central-place variants: (i) root anticipates its family (barely helps — family still lands on one cell); NPP-scaled footprint (FALSIFIED R-43 — agents self-select onto local NPP maxima → reads rich → k=0); (iii) juvenile followers take no forage share (partial). All default OFF. §4.8.20 |

> **§17–18 currency note (2026-06-29):** added to close the audit gap — PARAMETERS had not been updated through
> the entire Carbon-status (R-18…R-21) → storage/morph → emergent-bands → full F.3 family/band/society arc →
> full-stack work. The **canonical realistic-forager full-stack config** (status→RS ≈ 0.13) = the values flagged
> "realistic"/"family stack" above (run_3m). Most flags default-OFF (bit-exact baseline); the social architecture
> is an opt-in, fully-ablatable bundle (each flag independent).

---

## §19 — Economy-from-Climate (EFC) + GD-1 finite resources (R-49…R-51; MODEL_SPEC §4.3.4–§4.3.11; MECHANISMS §9b)

**All EFC/GD-1 constants are PROVISIONAL** (opt-in `mode="climate"` / `enable_depletion=True`; legacy default is
bit-exact). Values live in `terrain.py` (EFC C1–C7) and `capacity.py` (C8 + GD-1). Extraction/derivation:
MODEL_SPEC §4.3.4–§4.3.11 (methods home). Findings: RESULTS R-49/R-50/R-51.

### §19.1 — EFC grid geometry (`terrain.py`)

| Name | Value | Status | Meaning / grounding (MODEL_SPEC ref) |
|------|-------|--------|--------------------------------------|
| CELL_EDGE_M | **10000.0** m | LOCKED | cell edge = 10 km (100 km²/cell; = §1 Cell area). Shared legacy+climate. §4.3.4 |
| GRID_SPAN_DEG | **9.0**° | PROVISIONAL | N–S extent of the 1000 km grid (~111 km/°) → modest within-grid latitude gradient. §4.3.4 |
| CLIMATE_FULL_LAT_DEG | **65.0**° | PROVISIONAL | latitude at the subpolar edge (climate_latitude=1); equator=0. §4.3.4 |
| REGIONAL_SPAN_FRAC | **≈0.14** (=9/65) | DERIVED | fraction of the equator→subpolar span traversed within one grid. §4.3.4 |
| CLIMATE_LATITUDE_DEFAULT | **0.5** | PROVISIONAL | default regional latitude (temperate mid-lat); knob `climate_latitude` overrides. §4.3.4 |

### §19.2 — C1 temperature (`terrain.py`, mode="climate")

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| LAPSE_C_PER_KM | **6.5** °C/km | PROVISIONAL (std physics) | environmental lapse rate — montane cooling; fixes savanna-cold/montane-warm inversion. §4.3.4 |
| TEMP_SEAS_AMP_MAX | **15.0** °C | PROVISIONAL | max seasonal HALF-amplitude (~30 °C range) at a high-lat continental interior. §4.3.4 |
| MARITIME_DAMP | **0.6** | PROVISIONAL | fraction near-water (high wateracc) cells DAMP the seasonal amplitude (maritime moderation). §4.3.4 |
| TEMP_EQUATOR_C / TEMP_HIGHLAT_C | **27.0 / 1.0** °C | PROVISIONAL | base-T latitude endpoints (14 °C area-mean); shared with the C.4a grass-subtype gradient. §4.3.4 |
| GRASS_TROPICAL_THRESHOLD_C | **18.0** °C | LIT-ANCHORED (Köppen) | tropical-A isotherm: warm intermediate band → SAVANNA, cool → GRASS. §4.3.7 |

### §19.3 — C2 precipitation (`terrain.py`, mode="climate")

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| P_BASE_MM | **250.0** | PROVISIONAL | dry-background precip (subtropical/polar desert floor). §4.3.5 |
| P_ITCZ_MM / P_ITCZ_WIDTH | **2400.0 / 0.15** | PROVISIONAL | equatorial ITCZ wet peak + Gaussian half-width. §4.3.5 |
| P_MIDLAT_MM / P_MIDLAT_CENTER / P_MIDLAT_WIDTH | **1100.0 / 0.70 / 0.18** | PROVISIONAL | mid-latitude storm-track peak, center (~50°), width. §4.3.5 |
| P_ELEV_UPLIFT | **1.6** | PROVISIONAL | elevation → orographic uplift multiplier (elev=1 ⇒ ×2.6 at full moisture). §4.3.5 |
| P_ORO_SHADOW_CELLS | **6** | PROVISIONAL | rain-shadow reach (max upwind elev over ~60 km). §4.3.5 |
| P_ORO_SHADOW_GAIN | **1.6** | PROVISIONAL | drying strength in the lee of upwind high terrain. §4.3.5 |
| P_ORO_MIN / P_ORO_MAX | **0.25 / 3.2** | PROVISIONAL | orographic multiplier clamp (deep lee / windward-peak). §4.3.5 |
| P_MARITIME_GAIN | **0.3** | PROVISIONAL | near-water (wateracc) moisture-supply boost. §4.3.5 |
| P_ORO_WIND_DX | **1** (+x) | PROVISIONAL | prevailing wind = +x (westerlies); upwind = −x. §4.3.5 |
| P_MOISTURE_REF_MM / P_UPLIFT_MIN_AVAIL | **1500.0 / 0.12** | PROVISIONAL | moisture-limited uplift: base precip at full uplift / floor. §4.3.5 |
| POLAR_DRY_ONSET / POLAR_DRY_GAIN | **0.72 / 0.55** | PROVISIONAL | polar dryness onset latitude / max fractional precip reduction. §4.3.5 |
| CLIMATE_ARIDITY_DAMP | **0.75** | PROVISIONAL | `climate_aridity` knob scales precip DOWN by up to this (continental/leeward dryness). §4.3.5 |

### §19.4 — C3 Miami NPP (`terrain.py::miami_npp`) [VERIFIED vs Lieth 1972/1975 PDF, eqs 12-1/12-2]

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| MIAMI_MAX | **3000.0** g/m²/yr | LOCKED (published) | asymptotic NPP ceiling of both limbs. Lieth 1972/1975. §4.3.6 |
| MIAMI_T_A | **1.315** | LOCKED (published) | temperature limb: NPP_T = MAX/(1+exp(A−B·T)). §4.3.6 |
| MIAMI_T_B | **0.119** | LOCKED (published) | temperature-limb slope. §4.3.6 |
| MIAMI_P_C | **0.000664** | LOCKED (published) | precip limb: NPP_P = MAX·(1−exp(−C·P)). §4.3.6 |

### §19.5 — C4 Whittaker biome (`terrain.py::whittaker_biome`)

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| WHIT_DESERT_BASE / WHIT_DESERT_SLOPE | **200.0 / 15.0** | PROVISIONAL | `P < BASE+SLOPE·max(T,0)` → DESERT (warm needs more rain). §4.3.7 |
| WHIT_FOREST_BASE / WHIT_FOREST_SLOPE | **500.0 / 35.0** | PROVISIONAL | `P ≥ BASE+SLOPE·max(T,0)` → FOREST. §4.3.7 |
| WHIT_TUNDRA_T | **−5.0** °C | PROVISIONAL | below this a would-be FOREST → GRASS (tundra; too cold for trees). §4.3.7 |

### §19.6 — C6 river temperature + C7 aquatic-food (`terrain.py`)

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| RIVER_COLD_RETENTION | **0.6** | PROVISIONAL | fraction of the headwater-elevation cooling a river retains at a cell (salmon enabler). §4.3.8 |
| SALMON_T_OPT | **16.0** °C | LIT-ANCHORED (salmonid thermal) | at/below → anadromous coldness FULL. §4.3.9 |
| SALMON_T_LETHAL | **21.0** °C | LIT-ANCHORED (salmonid thermal) | at/above → anadromous coldness 0. §4.3.9 |
| AQUATIC_SEA_CONN_FLOOR | **0.25** | PROVISIONAL | anadromous factor for endorheic rivers (not draining to sea). §4.3.9 |
| SHELLFISH_RICHNESS | **0.7** | LIT-ANCHORED (Bird 1997) | coastal littoral aquatic-food level on shore cells. §4.3.9 |

### §19.7 — C8 aquatic capacity subsidy + GD-1 finite resources (`capacity.py`)

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| AQUATIC_DENSITY_MAX | **80.0** persons/cell | PROVISIONAL (Ames 1994) | persons added by a full aquatic cell (~8× Tallavaara median); opt-in `aquatic=True`. §4.3.10 |
| R_BIOME_PER_YR | **{water 0.0, wetland 0.40, forest 0.15, savanna 0.60, grass 0.70, desert 0.15, mountain 0.20}** /yr | PROVISIONAL | GD-1 biome logistic regrowth rate; grass/savanna fast, forest/desert slow. Coe 1976 / Cortés 2016 r_max. §4.3.11 |
| AQUATIC_R_PER_YR | **0.80** /yr | PROVISIONAL | fast aquatic-catchment restock (salmon/shellfish) — the sedentism enabler. §4.3.11 |
| DEPLETE_FRAC | **0.5** | PROVISIONAL | depletion strength; at pressure=1, B equilibrates ~1−0.5. §4.3.11 |
| B_FLOOR | **0.05** | PROVISIONAL | hunted-out cell floor (refugia/trickle). §4.3.11 |
| enable_depletion / aquatic (NPPCapacityField) | **False / False** (default) | OPT-IN | GD-1 stock / C8 subsidy toggles; off ⇒ non-depleting standing flow, bit-exact (suite 660). §4.3.10/§4.3.11 |
| mode (generate_world) | **"legacy"** (default) / "climate" | OPT-IN | EFC world-generation mode; legacy bit-exact. §4.3.4 |

## §20 — Aggregation-sedentism (settlements) + economic-defensibility (R-52; MECHANISMS §9c; blueprints `…_AggregationSedentism`, `…_EconomicDefensibility`)

Settlements as MULTI-BAND coalescence — "the gathering that stops dispersing". All default-OFF ⇒ bit-exact.

### §20.1 — Aggregation-sedentism lifecycle (Layer 1; `demography.py`, `phase1_model.py`)

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| enable_aggregation_sedentism | **False** (default) | OPT-IN | master toggle; needs enable_marriage_aggregation + enable_band_affiliation. Off ⇒ no settlements, bit-exact. |
| settle_min_pool | **40** persons | ANCHORED-lower-bound (Bar-Yosef 1998) | minimum-viable-hamlet: Natufian settlements range small ~dozens → medium 100–150; 40 = small-settlement lower bound. `village_gain` (max size) should let villages LAND in 50–150 — check in run A. |
| settle_persist_threshold | **0.3** (S_pot) | PROVISIONAL | site `aquatic_food`/S_pot ≥ this = a persistent-abundant (storable) settlement site. |
| settle_radius | **2** cells | PROVISIONAL | Chebyshev radius for membership + formation (a day's logistical range). |
| settle_release_steps | **12** steps | PROVISIONAL | hysteresis: steps a settlement survives below settle_min_pool before dissolving. |
| settlement_cohesion | **1.5** | SUPERSEDED | Layer 1 soft hold; replaced by the Layer 2 residence pin (kept for ablation). |

### §20.2 — Layer 2: residence ≠ foraging + tier-2 unlock (`phase1_model.py`)

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| settle_catchment_radius | **2** cells | PROVISIONAL | catchment the settlement forages tier-2 from (Binford collectors; residence pins to the single site cell). |
| settle_tier2_yield | **40.0** /unit S_pot/cell | PROVISIONAL — sweep | intensive tier-2 yield per unit S_pot per catchment cell, UNLOCKED by settlement (gated; mobile bands get only tier-1). Resource-agnostic (S_pot = aquatic_food now, cultivability later). Note: ~7× a village's need ⇒ fisheries never food-stressed → stable (R-53). |
| enable_tier2_shock | **False** (default) | OPT-IN | Layer 2b regional bad-year shock; off ⇒ shock=1.0 ⇒ bit-exact. |
| shock_cv | **0.6** | PROVISIONAL — salmon-anchored | inter-annual tier-2 yield CV (salmon-run variability). |
| shock_rho | **0.0** (default) | PROVISIONAL | AR(1) persistence: 0 = IID single bad years (bit-identical to pre-AR(1)); →1 = multi-year regimes (ENSO/PDO). Only regimes test storage (R-53). |

### §20.3 — Economic-defensibility (DE-10; kept default-OFF, superseded as concentration mechanism → folded to catchment grain)

| Name | Value | Status | Meaning / grounding |
|------|-------|--------|---------------------|
| enable_economic_defensibility | **False** (default) | OPT-IN | Dyson-Hudson & Smith owned-patch claim/exclusion. Superseded for concentration by R-52; kept for the between-settlement catchment-defense follow-on. |
| defensibility_min / claim_dwell / claim_min | **0.15 / 6 / 3** | PROVISIONAL (DE-10) | claimable S_pot threshold; steps to own; min members to hold. |
| defensibility_exclusion / tether | **0.2 / 6.0** | PROVISIONAL (DE-10) | outsider per-capita ×; owner tether × (did not pack — see DE-10). |

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

## §20 — Emergent village arc (agglomeration rework; R-54…R-57; MODEL_SPEC §4.8.21b; branch merged to main 2026-07-07)

All default-OFF/opt-in; the canonical "everything on" preset is `emergent_village_demog()`. Use with `world_lottery_climate(..., scarce_arable=True)` for riverine villages.

| Name | Value | Status | Grounding |
|------|-------|--------|-----------|
| enable_agglomeration / aggl_mode / aggl_beta | False / **"point"** / **1.15** | OPT-IN | point-superlinear: cell's own output ∝ n^β, per-capita premium `A_cell·(n^(β-1)−1)`. β = Bettencourt 2013 urban-scaling exponent. Catchment mode FALSIFIED (DE-11). |
| aggl_tier2 | **5.0** | PROVISIONAL | intensification multiple A_cell = tier2·S_pot·cv_ref (dimensionless ~1–5) |
| enable_forage_cap / forage_cap_hours | False / **100** | OPT-IN | per-person intake ≤ forage_kcal·hours (solitude fix; the nucleation lever, 5.8→31.7% packed). cv≈5×BURN optimum |
| enable_village_scaling / village_gain | False / **5.0** | OPT-IN, UNANCHORED | net payoff above saturation adds tolerable-size headroom past band_split_size=45 → villages 55–77, hierarchy-gated (Johnson 1982) |
| enable_leader_coherence / leader_coherence_gain | False / **2.0** | OPT-IN, UNANCHORED | hierarchy term (Boehm-gated: egalitarian 0 / complex 0.5 / stratified 1.0). Required to exceed band scale |
| enable_size_repulsion / repulsion_gain / repulsion_midpoint / repulsion_width | False / **0.3** / **25** / **6** | OPT-IN | Johnson 1982 scalar stress (Alberti 2014 logistic); society relief 1.0/0.5/0.25 |
| enable_terrain_move_cost / move_cost_kcal | False / **750** | OPT-IN, **VERIFIED-anchored** | =0.01·BURN ≈ a 10 km move (locomotion energetics 50–75 kcal/km; Pandolf/Minetti). Perceived + drained. Above ~1% over-penalizes |
| enable_site_appraisal / site_gain / site_radius / site_lambda | False / **0.3** / **2** / **1.0** | OPT-IN | catchment central-place suitability (Kennett-Winterhalder IFD + Vita-Finzi radius 2). Emergent Carneiro on scarce land |
| enable_resource_storability | False | OPT-IN (confirmed **second-order**, R-57) | storable_fraction ← per-cell grain 0.85/fish 0.80/forage 0.15/game 0.35 (Testart). Fill-rate modifier only |
| scarce_arable (terrain) / RIVER_RIBBON_LAMBDA | False / **0.8** | OPT-IN | cultivability → thin river ribbons (cult·exp(−d2river/λ)); prime arable 20%→6% (Nile/Mesopotamia) |
| enable_energetic_fertility | **True in preset** (audit 2026-07-07) | OPT-IN | births scale with maternal reserve → self-limiting population (not Malthusian). Validated: higher stable pops across maps |
| enable_terrain_risk / risk_cap | **True in preset** / 3.0 | OPT-IN | biome mortality risk multiplier |
| enable_productivity_mobility / mobility_npp_ref | **True in preset** / 900 | OPT-IN | biome-scaled ranging (Tallavaara forager-median NPP; poor biome → longer stride) |
| enable_infanticide | False | **UNIMPLEMENTED STUB** | no logic; baseline infanticide is already in the Siler infant-mortality curve. Not built (redundant with energetic_fertility) |

---

*PARAMETERS.md extracted 2026-06-08. Supersedes interim locked-param tables in `sic_games/CLAUDE.md`
and `docs/ROADMAP.md`. Maintained by Code; updated any time a parameter is locked, swept, or retired.*
