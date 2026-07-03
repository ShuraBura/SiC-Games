# SiC Games — Master Roadmap & Deferred Items

**Last updated:** 2026-07-01
**Maintainer:** Claude Code updates this file at the end of every stage or directive.
**Review protocol:** supervisor reviews this file at the start of every new stage conversation.

---

## Phase boundary (declared 2026-06-12)

**Phase 0 — Social Mechanics: Stages 1–7.5 (complete, 2026-06-11).**
Built on the Epstein & Axtell Sugarscape base model. Historical stage numbers (Stage 1
through Stage 7.5) in all existing docs refer to this phase. Blueprint folder:
`blueprints/phase0/`. Do not retroactively rename Phase 0 stage numbers.

**Phase 1 — Terrain & Resource Ecology: Stage 1 onward (active).**
Fresh terrain-driven foundation; stage numbering restarts at 1. Active blueprint:
`blueprints/phase1/SiC_Games_Phase1_Stage1_ForageField_TerrainDiagnostics_Blueprint.md`.
All new blueprints and directives are Phase 1 unless explicitly marked otherwise.

### Phase 1 Stage 1 — ForageField + Terrain Diagnostics (complete 2026-06-13)

Status: **COMPLETE — all A-gates GREEN.** Acceptance: `outputs/phase1_stage1/acceptance_and_artifacts.py`.

New fields: `forage_kcal` (per-biome mean-scaled kcal/forager-hr + shore bonus), `npp_gm2` (npp × 3400 g/m²/yr), `is_shore` (land cells with ≥1 water neighbor). Coast diagnostics and validity guards in `characterize_map()`.

**Deferred items from Phase 1 Stage 1:**
- **Offshore/boat-fishing (Task 3.4):** water-cell foraging via boats deferred. Current model: foraging reward is zero for water cells (not modelled). Shore bonus (+1491.5 kcal/hr, Bird 1997) covers reef/littoral foraging from land. Open-ocean / deep-sea boat fishing is a distinct mechanic; leave for a dedicated stage when social structures that support it (C multi-family coordination or Si information-sharing) are implemented.
- **Desert provisionally uninhabitable (Task 1.4):** desert cells are excluded from `habitable_cell_count` as a baseline. This is PROVISIONAL — see `HYPOTHESES.md § H-TERRAIN-ASYMMETRY` and the desert flag. Revisit when agent movement and metabolism on desert terrain is calibrated.
- **Mountain foray-not-residence (Task 1.5):** mountain cells currently included in habitability. Pre-registration that mountain cells are visited but not permanently inhabited (foray model) deferred to Stage 2 movement mechanics.

**Generator design note:** mountain_fraction is structurally capped at ≈ 0.317 (mtn_ceiling). See `HYPOTHESES.md § H-TERRAIN-ASYMMETRY` and `ARCHITECTURE.md § 9.5.1`.

### Phase 1 Stage 1b — Water Decomposition Diagnostic (complete 2026-06-13)

Status: **COMPLETE — A1-A6 GREEN.** Acceptance: `outputs/phase1_stage1b/acceptance_and_artifacts.py`.

Exterior/interior water decomposition: `_classify_water_components()` 4-nbr BFS; new `characterize_map()` fields (`exterior_water_fraction`, `interior_water_fraction`, `n_interior/exterior_bodies`, `shoreline_fraction`, `largest_exterior_body_cells`, `largest_exterior_shore_to_area`). Exterior-water validity guard: `EXTERIOR_WATER_CEILING = 0.12` (PROVISIONAL — see below). Sweep: waterK [0,1], 21 steps × 5 seeds = 105 maps; guard onset at waterK≈0.80 (12/105 fires).

**Open items from Stage 1b (resolved in Stage 1c):**
- **Exterior-water threshold (RESOLVED — guard retired):** exterior_water_fraction guard was mis-specified (area measure on edge-connectivity event). Replaced in Stage 1c by `largest_water_body_fraction > LARGE_BODY_CEILING`. `EXTERIOR_WATER_CEILING` stays as a diagnostic constant.
- **§H-NO-COASTAL-MORPHOLOGY RETRACTED:** the M2 finding was based on `largest_exterior_shore_to_area` (crinkliness-per-unit-water, not coastline length). Retracted; see `ARCHITECTURE.md § 12.1-J`.
- **§STAGE-GEOSTRUCT deferred** (see below).

### Phase 1 Stage 1c — Largest-Lake-Body Guard (complete 2026-06-13)

Status: **COMPLETE — A1-A8 GREEN.** Acceptance: `outputs/phase1_stage1c/acceptance_and_artifacts.py`.

**Guard swap:** replaced `exterior_water_fraction > EXTERIOR_WATER_CEILING (0.12)` with `largest_water_body_fraction > LARGE_BODY_CEILING (0.10)` as the sole large-water world-acceptance guard. Old guard retired: it was an area measure firing on an edge-connectivity event (interior lakes merging to the boundary), so it over-rejected valid large-lake continental worlds. New guard cuts on the single largest connected water body — the ecologically meaningful statistic (body too large to walk around → inland-sea class → deferred to §STAGE-GEOSTRUCT).

**New `characterize_map()` fields:** `largest_water_body_fraction`, `water_body_count`, `characteristic_water_body_size` (median, cells), `characteristic_interlake_patch_size` (median land-component size, cells). Helper `_component_sizes(mask)` added (4-nbr BFS, generic boolean mask). `guard_exterior_water_fail` kept as diagnostic (not in `invalid_substrate`). `guard_large_body_fail` added to `invalid_substrate`.

**Discovery branch 1B:** `largest_body_fraction` pre-existed from `_water_bodies()`. Exposed canonically as `largest_water_body_fraction`; `largest_body_fraction` kept as backward-compat alias.

**Sweep:** waterK [0,1], 21 steps × 5 seeds. Guard fires at waterK=0.85 (seeds 42, 7 first). Guard does NOT fire at wK=0.80 under new metric (contrast: old exterior guard fired there). ARTIFACT 1 in sweep output shows the full distribution; ceiling confirmed by supervisor.

**Open items from Stage 1c:**
- ~~**LARGE_BODY_CEILING = 0.10 (PROVISIONAL):**~~ **Resolved 2026-06-13: supervisor-locked at 0.08.** See §DECISION-LAKE-BODY-CEILING below.
- **Forward note (flood dynamics):** flooded cells must NOT trip the single-body guard. A flood event is a transient wetland/swamp state, not a water body. Handled when stochastic-shock stage is built.

### Phase 1 Blueprint A — Agent-Terrain Migration + Static Game (complete 2026-06-14)

Status: **COMPLETE — Gate A-1 GREEN (all 4 rails), A-2 blocks GREEN, 430 tests.** Gate: `outputs/phase1_blueprintA_gate/gate_a1.py`. Results: `outputs/phase1_blueprintA_gate/gate_a1_results.json`.

**Phase A-1: C agent substrate migration.** SugarField removed from the C harvest path. C agents now harvest from `forage_kcal` (WorldFields) via `TerrainField` adapter. kcal economy: burn=75,000 kcal/step (2,500 kcal/day × 30 days/step [NOMINAL]), intake=rate_kcal/hr × 180 kcal/step (6 hr/day × 30 days [NOMINAL]). Reserve: `reserve_full=100,000 kcal` [PLACEHOLDER MR-1], `reserve_floor=20,000 kcal` [PLACEHOLDER MR-1]. Non-rivalrous harvest [PROVISIONAL, CC-1 seam]. New: `TerrainField` adapter (`terrain_field.py`), `TerrainWorld` Mesa model (`phase1_model.py`), `KcalBurnModel` (`agents/costs.py`), `KcalEconomyConfig` (`config.py`). Old Sugarscape sugar-cluster constants declared DORMANT-SUPERSEDED-FOR-C (PARAMETERS.md §13.1; ARCHITECTURE.md §12.1-L).

**Phase A-2: Static game mechanics.** `game_kcal` field in `WorldFields` (biome-scaled via `GAME_KCAL_TARGETS`; zeroed at water/wetland/mountain; tagged PROVISIONAL). `sex` attribute on `BaseAgent` ("female"/"male"; A2.1). Sex-based stream selection: female default=forage; male default=game; switch only under deficit when other stream covers better (A2.2). Child age-gate binary: intake=0 below `age_productive_min=15` [JV-1 seam] (A2.4). Three seams registered in DEFERRED_MECHANICS.md: GD-1 (game depletion), CC-1 (non-rivalrous cap + kcal re-derivation), JV-1 (juvenile curve).

**Gate A-1 rails (correctness-only, forage-only path):** L_short=500 steps, S=3 seeds (42/43/44), n_agents=250, occ_cap_loose=10/cell. RAIL 1: pop>0 ✓ (240–243); RAIL 2: pop≤100,000 ✓ (max=250); RAIL 3a: no alive-below-floor ✓; RAIL 3b: max_mean_reserve<10×reserve_full ✓ (capped at 100,000).

**Architecture notes:** `lifespan_months=900` [PLACEHOLDER] added to `KcalEconomyConfig` to resolve max_age unit-conversion conflict (legacy Sugarscape `max_age_dist` was in steps, not months; 80 steps at 1 step=1 month = 6.7 years → all agents extinct by step 80). ARCHITECTURE.md §15.7. 7 agreed-but-deferred mechanics in DEFERRED_MECHANICS.md.

**Deferred items from Blueprint A:**
- **GD-1 (game depletion):** `game_kcal` per-cell field is read-only (non-destructive harvest). Stock + regrowth mechanic deferred. DEFERRED_MECHANICS.md GD-1.
- **CC-1 (non-rivalrous cap):** Each agent gets full per-cell rate independently (no sharing). Rivalry and NPP ceiling re-derivation deferred. DEFERRED_MECHANICS.md CC-1.
- **JV-1 (juvenile income curve):** Binary gate only (0 below 15, full adult above). Graded age curve deferred. DEFERRED_MECHANICS.md JV-1.
- **RS-1 (risk-sensitivity), MR-1/MR-2 (reserve anchoring/provision), PL-1 (pool scale):** In DEFERRED_MECHANICS.md.
- **A-3 performance audit:** Separate blueprint. TerrainWorld step-time profiling at Phase 1 agent counts needed before long campaigns. Not started.
- **Seasonal forage:** Amplitude modulation on `forage_kcal` (and `game_kcal`); deferred to a future stage.

### §DECISION-LAKE-BODY-GUARD (decisions register, 2026-06-13)

**Decision:** Replace `exterior_water_fraction` guard with `largest_water_body_fraction > LARGE_BODY_CEILING` (Stage 1c). See `ARCHITECTURE.md § 12.1-K`.

**Rationale:** exterior_water_fraction fires when interior lakes merge to the map boundary (edge-connectivity event, not ecological). The correct criterion is a single water body large enough to be functionally an inland sea (Lake Superior class — cannot be walked around; produces coastal dynamics not yet implemented in this arc).

**Known scope gap:** excluding single-body-dominated worlds removes large-water-barrier geography from the C vs Si comparison. Deferred to §STAGE-GEOSTRUCT.

### §DECISION-LAKE-BODY-CEILING (decisions register, 2026-06-13)

**Decision (supervisor-locked 2026-06-13):** LARGE_BODY_CEILING = **0.08**. See `PARAMETERS.md §12.3` for the parameter entry; `ARCHITECTURE.md §12.1-K` for implementation detail.

**Rationale:** 0.08 ≈ 80,000 km² at 100 km²/cell — just below Lake Superior (~82,000 km²). A single connected water body exceeding 0.08 of map area is rejected as functionally an inland sea: it cannot be walked around and produces coastal dynamics (fetch, boat-crossing, regional fragmentation) this continental arc does not implement. Conservative-side choice: reject at below-Superior scale, not above it. The Stage 1c sweep showed the guard fires at wK=0.85 under this ceiling (waterK range in which no scientifically meaningful world is lost); at wK=0.80 the guard does not fire. This is deferral, not exclusion — large-water dynamics committed to §STAGE-GEOSTRUCT.

**Guard logic (single condition):** `largest_water_body_fraction > LARGE_BODY_CEILING`. NO conjunctive condition; no dominance/body-count term. A single body large enough is rejected regardless of surrounding lakes.

### §STAGE-RECAL — Recalibration on rebuilt substrate (DEFERRED, committed)

**Status:** Deferred. Pre-registered, gated recalibration stage. Do NOT build now.

**Scope:** After continental terrain + resource ecology are built, §STAGE-RECAL re-derives the PROVISIONAL (dormant) parameter set on the new substrate and re-tests superseded hypotheses (including H1(ii) — see `HYPOTHESES.md §H1ii-RETEST`).

**What §STAGE-RECAL must do:**
1. **Re-derive DORMANT parameters**: τ_parent (0.0) and k_pool_cap (0.0) were set against inactive mechanics in Phase 0. Once terrain makes those mechanics fire for the first time, their values must be calibrated against observed behavior, not inherited from inactive-mechanic runs.
2. **Re-test H1(ii)**: The Sugarscape-era inversion finding (C > Si at A=0.75/T=T*) does not carry forward as confirmed on the terrain substrate. The re-test is pre-registered in `HYPOTHESES.md §H1ii-RETEST`.
3. **Confirm ACTIVE guideposts**: ACTIVE locked params (τ_trickle, σ_inherit, p_fission_Si, p_max_C, c2_defection) are guideposts, not re-derived from scratch — sanity-check they remain plausible at the new substrate scale.

**What §STAGE-RECAL is NOT:**
- NOT open knob-tuning. Each parameter must have a pre-committed calibration target and an acceptance check. Recalibration must not be a free search.
- NOT the writing of document updates. Document rewrites flow FROM the stage's results, not from deliberation or web search (web supplies calibration *anchors* only).
- NOT reachable until the mechanics those parameters govern actually fire in terrain runs.

**Pre-registration requirement:** before §STAGE-RECAL runs, the following must be pre-committed: which parameters are targets, the calibration target per parameter, and the acceptance check. This pre-commitment must be logged in HYPOTHESES.md before the stage executes.

### §STAGE-GEOSTRUCT — Geographic-structure generation (DEFERRED, stage number TBD)

**Status:** Deferred. On the roadmap as a committed-but-unscheduled destination. Do NOT build now.

**Scope decision (supervisor, 2026-06-13):** The current arc stays **continental** — interior water (lakes) only; no ocean/sea coast; no exterior coastline generation. The `LARGE_BODY_CEILING` guard (Stage 1c) enforces this by rejecting inland-sea worlds; excluding coastal/ocean worlds is the desired behaviour for the current arc. (Note: `EXTERIOR_WATER_CEILING = 0.12` is retained as a diagnostic constant but no longer gates world acceptance.)

Geographic-structure generation is a large deliverable and is deferred to its own stage, to be built **only alongside the dynamics that make geographic structure meaningful** (seafaring / tier-3 offshore resources, regional connectivity, traversal). Consistent with §DECISION-NO-RIVERS: terrain is not built ahead of its mechanic.

**Contemplated content (reference map, not a build commitment):**
- **Continental-margin / long-coastline generator** — decouples sea extent from the `waterK` knob; controllable exterior coastline with land behind it. Requires independent control of exterior water morphology (a boundary-distance bias in the elevation primitive so low ground concentrates against chosen edges, rather than exterior sea emerging incidentally from `waterK`).
- **Archipelago generator** — multiple land bodies separated by sea; high coastline, fragmented land.

**Diagnostics deferred with this stage:**
- Replace `largest_exterior_shore_to_area` (confirmed unfit for coastline measurement: it is shoreline / body-area, not shoreline length) with **absolute exterior shoreline length** + a minimum-exterior-body-size gate to exclude sub-5-cell edge noise.
- Target-statistic benchmarks (coastline-length distribution, land-body-count/size, exterior/interior split) to make generator builds CC-iterable to convergence.

**Methodological boundary (pre-registered):**
- World *generation* (terrain to spec) is assertable and CC-iterable against target statistics.
- *Dynamics* that make geographic features meaningful (seafaring, traversal, regional shock response) are model science — NOT one-prompted or iterated-to-convergence. Each enters as its own pre-registered stage with its own hypothesis and gate. Geostruct terrain sits inert as substrate until its dynamics stage arrives.

---

**Disambiguation rule:** bare "Stage N" in documents dated before this boundary, or in
`archive/`, refers to Phase 0. New work carries the "Phase 1 Stage N" marker. When in
doubt, ask — do not assume.

---

### Phase 1 — A-3 First-Light Shakedown (exploratory, 2026-06-18)

Status: **DONE (not a gate).** C agents on Phase-1 terrain, rivalrous Stage-6.0a multi-occupancy on a CC-1 cell-capacity field (Tallavaara NPP density, PROVISIONAL), opt-in reproduction. Found a **placement-independent food-capacity ceiling ~133.4k** on 100×100 (RESULTS R-2), but a **demographically frozen equilibrium** (births=deaths=0; no baseline mortality). Harness: `outputs/phase1_a3_firstlight/run_a3.py`. Bugs fixed: per-forager-rate-as-cell-total (→ CC-1 cell capacity), water-blind diffusion movement (→ water guard).

### Phase 1 — Demographic Mechanics stage (DRAFTED + red-teamed, 2026-06-18)

Status: **BLUEPRINT v3 LOCKED for implementation (2026-06-18).** `blueprints/phase1/SiC_Games_P1_Demography_Siler_Blueprint.md`. Red-teamed; supervisor resolved all blockers (M-1 fix Siler from a published Aché fit, not re-fit; M-3 female Siler fit maternal-removed + add maternal back; M-5 `_do_births` rewrite).

**Step-1 (non-spatial Aché calibration) — COMPLETE 2026-06-18 (RESULTS R-3).** `src/sic_games/demography.py` (Siler + IBI core, 8 tests) + `outputs/phase1_demography_calib/`. The A-3 frozen equilibrium is FIXED (CBR 61 / CDR 27, births≈deaths>0); fixed Aché Siler reproduces the life table (e₀=36.5, e₁₅=38.3, mode=71); fertility tuned to Aché IBI=37/TFR=7.9; realized r=+3.3%/yr (Aché growth — r≈0 deferred to Step-2). 439 tests pass.

### Phase 1 — Demographic Mechanics Step-2 (terrain layer; IN PROGRESS, 2026-06-18)

Blueprint `blueprints/phase1/SiC_Games_P1_Demography_Step2_Terrain_Blueprint.md` (v3, red-teamed). **M-3 sex-split LANDED** (sex-specific Aché Siler). **TerrainWorld** gains an opt-in `demography_cfg` (Siler+IBI core; max_age cap removed; 443 tests). **2a-pre stability test PASSED** (RESULTS R-4): the +3.3%/yr population settles smoothly at ~95% of the food ceiling (settled-peak 1.01×, no overshoot/oscillation/collapse) — the red-team's B-1 blocker is RESOLVED (food's ~1-step brake stabilizes). **Next: 2b** — wire the `a2` modulators (terrain-risk / density-disease / pathogen / nutrition-synergy) + anchor their knobs (Tallavaara pathogen SEM, μ_max, risk scale), then measure the demographic carrying capacity vs the A-3 ~133k food ceiling. Pathogen field will use the new T/humidity climate seam (CL-1) once the climate stage lands. Sex-specific **Siler 3-term mortality** (Aché-anchored) replacing the hard age-cap and supplying baseline mortality; disease via density + terrain-pathogen channels (flagged; pathogen anchored to Tallavaara 2018 / Guernier 2004); nutrition×disease synergy (flagged); **female-only IBI-gated reproduction** + maternal mortality + SRB 0.512 + infanticide flag; staggered founder ages; **two-step staging** (non-spatial Aché calibration → terrain). GATES on reproducing the Aché life table (full l(x) curve + IBI/TFR + r≈0 + births≈deaths>0). Red-team dispositions in bp §13. Stage number TBD by supervisor.

## ⚠️ CRITICAL DESIGN CONSTRAINTS (read before every stage)

**C and Si are fundamentally different civilizations with different mechanics.**
Before implementing ANY mechanic, check this table. Assigning a C mechanic to Si
or vice versa without explicit supervisor approval is a design error.

| Mechanic | C | Si | Notes |
|---|---|---|---|
| Decision noise | Status-coupled σ (Cred-driven) | Fixed σ_Si | Core hypothesis |
| Cred type | Dominance/status from joint tasks | Reciprocal reputation (Stage 5+) | Different economies |
| Reproduction | Biparental, proximity-based, wealth+Cred modulated | Single-parent fission, wealth-threshold only | NEVER biparental for Si |
| Support structure | Self + proximity pool + status-mediated (L1+L2+L3) | Self + proximity pool only (L1+L2) | No status component for Si |
| Trait vector | H_i = [φ,ψ,c1,c2] all active eventually | H_i carried, hooks deferred | Same fields, different activation |
| ψ_i utility hook | Active (proximity term in utility) | Deferred to Stage 5+ | |
| Wealth inheritance | λ fraction of mean parent wealth | λ=0 (no inheritance) | Si wealth is earned |
| HiveMind | N/A | Skeleton only, Stage 7+ | Orthogonal to C mechanics |
| Newborn Cred | f_C · mean_cred_C | 0 for now (Stage 5+ when Si Cred defined) | |

**BUG HISTORY:** Stage 3.3 incorrectly implemented biparental reproduction for Si agents
because the ReproductionCoordinator was not C/Si-aware. This was caught but cost a stage.
Always check the C/Si distinction table above before implementing reproduction mechanics.

---

## Current status

| Stage | Status | Key output |
|---|---|---|
| Stage 1 | ✓ Complete | Sugarscape substrate. Gini=0.47, N=250, peaks=63%. seed=42 confirmed. |
| Stage 2 | ✓ Complete | Carbon decision + joint-task mechanic. κ=2.0 locked. |
| Stage 2.1 | ✓ Complete | Behavioral mode switch (wealth velocity). v_tau=10, v_0=1.0 locked. |
| Stage 2.2 | ✓ Complete | Baseline fix (BUG-001). κ sweep. σ_Si=1.051 (later updated). |
| Stage 3 | ✓ Complete | Bounded-rational Si. f_C=0.25 locked. Newborn/established split added. |
| Stage 3.1 | ✓ Complete | f_C sweep. f_C=0.25 locked. |
| Stage 3.2 | ✓ Complete | Status amplification. β=1.0 locked. C** pinned to C*=10.0. |
| Stage 3.3 | ✓ Complete | Trait vector H_i=[φ,ψ,c1,c2]. Biparental repro for C. Null Si Cred skeleton. |
| Stage 3.4 | ✓ Complete | 2D scan κ×α. Cell (2,3) selected: κ=2.0, α=2.0, σ_Si=1.238 locked. |
| Stage 4 | ✓ Complete | Seasonal oscillation A=0.5, T=200. N=250 fixed — no pop-level stress visible. |
| Stage 4.1a | ✓ Complete | Variable population. Birth/death decoupled. p_max exploratory. |
| Stage 4.1b | ✓ Complete (patched) | Age-efficiency ramp η(a). η_min=0.3 confirmed. P_max locked: C 0.12, Si 0.14, C seas 0.14, Si seas 0.17. |
| Stage 4.1c | ✓ Complete (patched) | Proximity support pool. Juv starvation: 0.3% C / 0.0% Si. P_max retuned: C static 0.065, Si static 0.28, Si seasonal 0.35. C seasonal: Allee bistability — deferred. Established starvation FAIL flagged (τ_pool=0.10 too aggressive). Cred pool contribution = 0.0 flagged. Both carry to Stage 4.2. |
| Stage 4.2 | ✓ Complete | τ_pool=0.05 locked (design tension — dual N-equilibrium role, see notes). γ=0.2 locked (Cred-modulated birth). BUG-003 fixed (cred_pool_contribution: 0→3.65/step). Seasonal sweep 8 runs. H1(ii): C collapses at T=200 (Allee+trough duration), survives T=100/T=50; Si survives all. Period-dependent bistability is primary finding. λ=0 (wealth inheritance) deferred to 4.3. Output: `outputs/stage42_seed42/`. |
| Stage 4.3 | ✓ Complete | Si differential metabolism β=2.0 (grid-calibrated; blueprint β=5 infeasible on max_sugar=4 grid). Si dormancy mechanic (τ_trickle=0.3, k_reactivate=3.0, t_dormant_max=50). Pool carry-over ρ=0.3 + cap k=20. Per-agent death_events.parquet. ψ_i quartile analysis: flat distribution (Q25 flagged). T*∈(100,112). H1(ii) MIXED: Si 3/4 survived (A=0.5 all T; A=0.75 T=200 collapse), C 0/4. Locked: p_max_C=0.07, p_fission_Si=0.15. Output: `outputs/stage43_seed42/`. |
| Stage 4.4 | ✓ Complete | β_Si=5.0 restored (grid rescaled k=4: max_sugar=16, α=4). λ=0.1 C wealth inheritance active. ψ redesigned: Beta(2,2) + c_proximity(r_pool=5). 8-run seasonal sweep: Si survives all conditions; C collapses all conditions (Allee bistability — see Diagnostic). H1(ii) result: Si-dominant. Locked: k_grid=4, p_fission_Si=0.065, p_max_C=0.03 (best effort). Output: `outputs/stage44_seed42/`. Report: `outputs/stage44_seed42/report.html`. |
| Stage 4.4 Diag | ✓ Complete | Factorial Run A/B/C/D (pool×λ) to diagnose C null control failure at k=4. Spatial diagnostic (pct_isolated_C, mean_nearest_C_dist) added to metrics. **Finding: Hypothesis A (Allee dispersal) RULED OUT** — pct_isolated_C=4.9% (threshold 40%). **Hypothesis B (birth-rate/age-out) CONFIRMED.** C is bistable at k=4: p≤0.05 → collapse (age-out faster than births); p≥0.07 → explosion (N~1600, no carrying-capacity ceiling). No p_max gives stable N∈[150,400]. Root cause: k=4 grid (max_sugar=16) eliminates resource competition — agents never starve, so no natural N ceiling. Pool and λ do not change the outcome (Run D replicates Stage 4.4 failure). **Recommended action: density-dependent birth suppression for Stage 4.5 (carrying-cost redesign).** Output: `outputs/stage44_diag_seed42/`. Report: `outputs/stage44_diag_seed42/report_diag.html`. |
| Stage 4.4 k=3 Feasibility | ⚠ Si Fail | k=3 Si population explosion + dorm_rate>20%: p=0.28:28%(bomb) p=0.35:32%(bomb) p=0.2:23%(bomb). k=4 minimum confirmed. |
| Stage 4.5 Task 0 | ⚠ T0 fail | carry_discount N_carry=400 alpha=1.0. p_bare=None. p_final=None. Tasks 2-4 pending (historical intermediate note). |
| Stage 4.5 | ✓ Complete | Carrying-cost birth ceiling. H_cc pre-registered. T*(C)>500, T*(Si)∈(68,87) at A=0.75. Seasonal sweep 10 runs. report_45.html. |
| Stage 5 | ✓ Complete (2026-05-27) | Multi-seed ensemble (30 rows). A=0.9 sweep. Si T* tightened to (68,87). Si Cred activated. ψ co-evolution 3000-step probe. **H1(ii) ROBUST: C 5/5 vs Si 0/5 at A=0.75.** report_stage5.html. |
| Stage 5.1 | ✓ Complete (2026-05-28) | Si Cred redesign: near-dormancy accumulation replaces surplus-based. accumulation_rate (r_cred_Si) retired; k_cred_band=1.0 locked. Counter-cyclicality gate PASSED both seeds (trough/peak: 1.13/0.49 seed=42, 1.58/0.66 seed=43). Null control gate PASSED (N_mean=335, dorm=4.9%, perm_deaths=0). 207 tests. report.html in outputs/stage51_sicred_redesign/. |
| Stage 5.2 | ✓ Complete (2026-05-29) | Cultural dynamics: c2 defection (def_rate=3.74%, N stable), Deffuant updating (all 3 equiv gates PASS), sigma_inherit sweep (sigma*=0.10). Cell B: Deffuant partially re-collapses psi diversity. psi co-evolution viable at sigma*=0.10 but Deffuant is a contracting force. 233 tests. report.html in outputs/stage52_cultural/. |
| R0 confound check | ✓ Complete (2026-06-02, supervisor-approved) | Seasonal-at-scale confound + marginal-distance diagnostic on 100×100/N_carry=4100, 12k/3-seed. Task 0 gate PASS (seasonal fires: CV≈0.42, trough phase-aligned at T/2). Task 1: settled≈2399 and est_starv=0.0000 PASS cleanly → **confound CLOSED on the est_starv=0.000 basis** (calibration confirmed STATIC). rel_std=0.0194 exceeded the old tolerance by ~2%; resolved as a **baseline correction** (old 0.014 was a single-run value with no distribution → corrected to 3-seed static rel_std≈0.019; tolerance widened ±0.005→±0.007). NOT a clean 3/3 match — confound closed on est_starv, with this minor rel_std caveat. **Headline: R1-LEADS** — est_starv rises 0.0000(static)→0.0000(A=0.5)→**0.0612(A=0.75, 3 seeds)**, monotonic threshold/cliff (only the deep trough engages mortality); D1 5th-pctile drops to ≈3.4 steps-to-starvation at trough and recovers at peak (margins breathe — rules out the buffered third outcome). Seasonal trough RESTORES resource-driven mortality at scale → design-doc spine leads with R1 (terrain); R2 (resource-lifetime) becomes enrichment. Diagnostic only — nothing locked changed; H1(ii) verdict untouched. report_r0.html. |
| Stage 6.0a | ✓ Substrate built (2026-06-04) | Multi-occupancy substrate: cells hold many agents (K_cell ceiling), harvest resource-SPLIT (even κ=0 + Cred/φ contest κ>0), diffusion movement (von-Neumann r=1, per-capita-yield utility, neutral affinity/crowd hooks), ψ re-pointed to occupancy (held neutral), consumer ports (JT cohort, partner search → same-cell, offspring-on-parent-cell). **Recovery gate §7.1 PASS bit-identical** (K_cell=1/legacy → legacy model, 1e-9/integer/positions exact). §7.2 behavioural: C viable both κ (settles ~1080/1150), self-limiting; **density 0.0011 p/km² ~100× below ethnographic target → calibration flag** (reported to supervisor); no Matthew-runaway (Cov(φ,wealth)≈−0.11). 250 tests. Substrate opt-in (default off → legacy untouched). §8 report/docs pending density-flag review. |
| Stage 6.0a-perf | ✓ Complete (2026-06-05) | Substrate perf reconnaissance (named exception — report IS deliverable). Cost surface across grid/N/occupancy; two-tier cutoff; flushed logs; 5 plausibility rails. Findings: N-exponent ≈1 (linear), grid-cells ≈0 (sub-dominant), **occupancy is the wall** (feasible ≤~2.3/cell; >~2.5/cell hard-infeasible via legacy JT-cohort O(grid×occ×cohort) blowup). Affordable ≤~300ms: low-occ N≤~10k @100×100 (≤~3–4k with O(N²) diagnostics on). **Proto-ag density NOT reachable on Python path** → needs array-restructuring + JT redesign + diagnostic subsampling (forward assessment, analysis only). Added `runtime_monitor` (wall-vs-CPU suspension detector). 256 tests. report_stage6_0a_perf.html. |
| Stage 5.3 | ⏳ Pending | Terrain topography (6.0b — stands on the 6.0a substrate). |
| Stage 5.x | ⏳ Pending | Full nD LHS scan (pyDOE2). c1/c2 hooks. Extended ψ co-evolution. Inter-pool connectivity. |
| Stage 6 (Phase 0 label) | ✓ Disambiguated 2026-06-15 | **RESOLVED (supervisor, 2026-06-15):** in Phase 0 records the "Stage 6" label refers **exclusively to the resource-ecology substrate arc** (6.0a substrate, 6.0a-perf, 6.0b terrain). The old "Statistical framework" meaning is retired from this number. The statistics/power-analysis framework is **unnumbered backlog** (see OWE-10) and will be scheduled as a **Phase 1 stage** when it is built — it does not reclaim a Phase 0 number. No live collision remains; the Phase boundary (Phase 1 restarts at Stage 1) already prevents recurrence. |
| Stage 7+ | ⏳ Pending | Heuristic drift, HiveMind, biparental for Si (if designed), full 100-world run. |

### Phase 1 — Demographic → Carbon → Climate → Bands → Social arc (the active line; detail in RESULTS R-2…R-27, MODEL_SPEC §4.2–§4.8)
| Milestone | Status | Key output |
|---|---|---|
| Demographic core (Siler + IBI) | ✓ | sex-specific Aché Siler + energetic fertility + provisioning; e₀ validated. R-2…R-14. §4.2/§4.5 |
| Carbon-on-substrate Tier-1 + Cred-vector B+ | ✓ | heritable cred + achieved prowess + paternity; status→RS r≈0.19 (IFD m≈4). R-18/R-19/R-20. §4.5.6–9 |
| Climate (orbital lottery C.1–C.5) + catastrophes | ✓ built (SEAMS) | seasonal/eccentricity/ENSO/regime + caribou/llanos + intercept hunting; gate-validated **in isolation**. **NOT yet wired into the live social runs** (Stage 0 below). §4.1.9 |
| Storage (delayed-return) + per-cell society morph | ✓ | collective granary (Binford ET), cred-weighted draw (Hayden), egal→complex→stratified morph. §4.5.11 |
| Emergent bands + E.3-proper + turnover fix | ✓ | corpse-bug fixed; bands on CC-1 + bonded_mate_radius=1; m=5→status→RS 0.19; lumping revised. R-21/R-22. §4.8.1–5 |
| Storage-tethering RETIRED | ✓ | morph fires from emergent bands; CC-1 capacity → lib `capacity.py`. R-23. §4.8.5 |
| F.2 risk-mortality (SHELVED) + band life-cycle | ✓ | risk-as-mortality = death spiral (shelved); balanced fluid band equilibrium. R-24. §4.8.6 |
| F.3 — persistent families → non-kin ~25 band → per-band society → assabiyah | ✓ | the complete dynamic band (collective-identity vector; Hill-2011 non-kin; Ibn Khaldun solidarity). R-25. §4.8.7–11 |
| Full-stack integration + modest polygyny + prowess fix | ✓ | architecture coheres; status→RS ≈0.13 (monogamy-appropriate); prowess-credit + reputation fixes. R-26. §4.8.12 |
| **Dynamic Social Evolution (NEW STAGE — active)** | ⏳ in progress | Stage 0 climate integration + controlled-climate harness done (R-27/R-28). **Stage 1 done:** the band-size force balance — size-repulsion (Johnson scalar stress) BINDS + fixes assabiyah saturation (R-29, the Stage-1 deliverable); leader coherence built + unit-valid but leader-death→fission is a principled null in the complex-forager regime → benchmark DEFERRED to the dynastic stage (R-30). **Fission-driver review done (R-31):** the fission threshold is DORMANT (band size is movement-set, not fission-set); the resource→size response is non-monotonic (moderate lean→aggregate, severe→disperse). **Resource-response redesign built** (`…_ResourceResponse_Scoping.md`): M1 aggregation DROPPED (DE-8, no food-wise payoff); **M2 malnutrition fission** (severe-scarcity → large bands break up; dispersal substitutes for death) VALIDATED via the substitution test (R-33); realized-starvation signal (R-32: `_condition` survivor-biased); **F resource-directed fusion** built. `season_aggregation` RETIRED (DE-7, field removed). **Stage 2 genealogy logger DONE** (`enable_genealogy_log`, pure observer, bit-exact, `dump_genealogy` CSV — the Stage-3 analytic substrate). **NEXT: Ibn Khaldun dynastic cycle** — BUT it needs a large settled/stratified polity (a keystone chief + succession crisis); the current model tops out at mobile-forager bands ~25 (hard cap 45), so the **settlement/high-tier-resource substrate is a PREREQUISITE** (see blueprint Stage 3 note). Then dynamic polygyny. Fully-ablatable flags. Blueprints `…_SocialEvolution_Dynamic_Scoping.md` + `…_ResourceResponse_Scoping.md`. **Reconciled 2026-07-02 (adds since R-33):** **CC-1 Tallavaara capacity FITTED** (`mode='tallavaara'`, ~57% of provisional, R-36) + **world-lottery** diverse worlds (forest/savanna/desert/montane/mixed). **status→RS re-estimated** (R-35): the R-26 0.13 was 6-seed optimism (16-seed ≈0); decomposes to prowess→RS +0.10 / cred→RS −0.07 → built **society-gated ascribed(cred) mate-choice**, CANONICAL a=2.5 → composite +0.128 *(headline reframe of R-19/R-21/R-26 HELD pending settlement-arc validation)*. **Newborn→adult life-history WIRED canonical** (was OFF; retires JV-1; 3 latent bugs fixed, R-38). **The gathering BUILT** (`…_MarriageAggregation_Scoping.md`; seasonal cross-band exogamous pairing, residence viri/uxori/flexible + rank-homogamy) — fixes mate-finding but **biome→society still shows the collapse (R-37/R-39)**: bonded-family co-movement piles family on one cell → overcrowd → starve, and the DEEPER root is **fixed-r=1 mobility** (no biome-aware ranging). **BIOME→SOCIETY COLLAPSE — ROOT-CAUSED + FIXED (R-40→R-43).** (1) Productivity-scaled mobility BUILT but FALSIFIED as the fix (R-40, DE-9 — no pile-up; mildly harmful). (2) Decomposition (R-41): the killer is FAMILY CO-MOVEMENT over-subscribing the mother's single cell → energetic-FERTILITY collapse (savanna births 4× lower; food NOT scarce). (3) Missing physics = **central-place foraging** (co-reside but forage DISPERSED + share; Isaac 1978 — the model conflated co-residence with co-foraging). (4) FIX BUILT (R-42): three ablatable prototypes; **FOOTPRINT (dispersed camp) is load-bearing**. (5) Full biome table (R-43): **uniform `comove_footprint=1` recovers the collapse in EVERY biome** (savanna 8→243, montane 14→276, mixed 18→519, forest 145→426, desert 0→64); the NPP-scaled footprint is falsified (agents self-select onto local NPP maxima → reads rich → k=0). Cell-size design answer: uniform lattice + behavioural footprint, NOT coarser per-biome cells (breaks the grid + double-counts Tallavaara capacity). **DONE: safety-gate (R-44, status→RS/band/Gini preserved, eq_pop ~2×) → CANONICALIZED `comove_footprint=1` (44b1422) → biome→society re-run SUCCEEDS (R-45): all biomes sustain societies; productivity shapes density (0.05→0.33), pop, starvation (23%→66%), and the status→RS gradient (forest 0.19 vs marginal 0.13). The R-37 collapse is CLOSED.** **NEXT (open refinement): the society MORPH is not biome-graded (80–100% complex everywhere) — couple the egal→complex→stratified ladder to productivity/storage (marginal→immediate-return egalitarian; rich/storage→stratify) to complete biome→society.** THEN the settlement/high-tier-resource substrate → Ibn Khaldun dynastic cycle. **THEN: Ibn Khaldun dynastic cycle** — needs a large settled/stratified polity (keystone chief + succession crisis); the model tops out at mobile-forager bands ~25 (hard cap 45), so the **settlement/high-tier-resource substrate is a PREREQUISITE**. Then dynamic polygyny. **Long-term studies flagged:** virilocal-vs-uxorilocal societies (whole-world compare; both directions wired); biome-localized residence (Ember&Ember subsistence→residence link); random-per-world residence lottery (comparisons deferred). |

> **Currency note (2026-06-29):** the Current-status table had not been updated since 2026-06-14 (through Stage
> 6.0a); the entire Phase 1 demographic/carbon/climate/bands/social arc is consolidated in the block above (full
> per-stage detail lives in RESULTS R-2…R-27 + MODEL_SPEC §4.2–§4.8 — pointers, not restated here).

---

## Locked parameters

> **Authoritative home: `docs/PARAMETERS.md`** (extracted 2026-06-08, charter §6).
> This section previously held the interim locked-param table. It has been replaced by a
> pointer now that PARAMETERS.md is live. Do NOT restate parameter values here — that creates
> two-homes drift. For any parameter value, lock date, sweep history, or status, see PARAMETERS.md.

The full authoritative table is in **`docs/PARAMETERS.md`**, organised by mechanism section
(§1 World/substrate · §2 Decision/σ · §3 Deffuant · §4 Joint task · §5 Cred economy ·
§6 Support pool · §7 Reproduction · §8 Dormancy · §9 Initialization · §10 Diagnostics).
Discrepancy resolution log (D1–D3 + two new items) is in PARAMETERS.md final section.

---

## Population mechanics (PM) — full tracker

### Implemented (C)
- [x] Greedy decision (Stage 1)
- [x] Softmax with Cred-coupled σ: σ_i = σ_base + κ·tanh(𝒞_i/C*) (Stage 2)
- [x] φ_i born-trait in H_i vector (Stage 2, extended Stage 3.3)
- [x] Cred state 𝒞_i with decay δ (Stage 2)
- [x] Joint-task mechanic, Matthew partition α=2.0 (Stage 2, α updated Stage 3.4)
- [x] Behavioral mode switch: w_C modulated by wealth velocity (Stage 2.1)
- [x] Newborn Cred endowment f_C=0.25 (Stage 3)
- [x] Status amplification β=1.0: w_C = φ·(1+β·tanh(𝒞/C**))·sigmoid(v/v_0) (Stage 3.2)
- [x] Trait vector H_i = [φ_i, ψ_i, c1_i, c2_i] (Stage 3.3)
- [x] ψ_i proximity utility term: U += ψ_i · N_hat_ij (Stage 3.3)
- [x] Biparental reproduction: proximity r=3, arithmetic mean + noise σ_inherit (Stage 3.3)
- [x] Wealth inheritance λ: w_child = w_floor + λ·mean(w_A, w_B) (Stage 4.1a — λ=0 default)

### Implemented (Si)
- [x] BoundedRationalSi with fixed σ_Si=1.238 (Stage 3, updated Stage 3.4)
- [x] Trait vector H_i carried and inherited (Stage 3.3) — hooks INACTIVE
- [x] Null Si Cred skeleton: si_cred field, config block, enabled=false (Stage 3.3)
- [x] ReproductionCoordinator protocol with HiveMind skeleton (Stage 4.1a)
- [x] Single-parent fission reproduction: wealth-threshold, near-copy + noise (Stage 4.1a)

### Implemented — C (Stage 4.1x / 4.2)
- [x] Variable population — birth/death decoupled (Stage 4.1a)
  - DTM-based unimodal birth probability: P_birth(w_i) — wealth-dependent
  - Reproductive age window [a_rep_min, a_rep_max]
  - Population collapse to zero allowed — no N_min floor
- [x] Age-efficiency ramp η(a) — Cobb-Douglas motivated (Stage 4.1b)
  - η_min=0.3 at birth (juvenile), linear ramp to 1.0 at a_forage_min≈15
  - η=1.0 during active adult phase
  - η_old=0.4 at death, linear decline from a_forage_max=τ_max-10
  - Asymmetric: elder decline shallower than juvenile ramp (skill retention)
  - Literature: Gurven & Kaplan (2006) Cobb-Douglas P(x)=S(x)^α·K(x)^β
- [x] Proximity support pool (τ_parent=0.10, τ_pool=0.05, k_reserve=5, k_draw=3). Stage 4.1c / Stage 4.2 recalibration.
  - BUG-003 FIXED (Stage 4.2): `agent._cred_scale` was always missing → tanh=0 → zero above-base Cred pool contribution for all 4.1c runs. Fixed: read from `agent._decision.cred_scale`. cred_pool_contribution: 0.0 → 3.65/step.
  - Criterion 4 (established starvation): still fails at τ_pool=0.05 — τ_pool is dual regulator (pool buffer + N equilibrium suppressor). Deferred to Stage 4.3.
- [x] Cred-modulated birth: P_birth_C × (1 + γ·tanh(𝒞/C***)). γ=0.2. Stage 4.2.
  - C only (NEVER Si). C***=C*=10.0. New metric: gamma_birth_boost (mean birth factor per step).
  - γ boost mean ≈1.09 at steady state; no Cred runaway detected.

### Implemented — Si (Stage 4.1x / 4.2 / 4.3)
- [x] Single-parent fission birth rule (Stage 4.1a)
  - Wealth-threshold only: w_i > θ_fission → reproduce with P_fission
  - Near-copy: offspring H_i = parent H_i + ε, all non-trait attributes fresh
  - No Cred modulation — Si reproduction is purely individual
- [x] Si proximity support pool (Stage 4.1c)
  - Same Level 1+2 as C (self-support + proximity pool)
  - NO Level 3 (no status-mediated component)
  - Reciprocal only: contribution history determines support priority
  - This is the foundation for Si Cred economy (Stage 5+)
- [x] Si differential metabolism β=2.0 (Stage 4.3)
  - ScaledMetabolicCost(beta=2.0) in agents/costs.py — not hardcoded in BaseAgent
  - C metabolism unchanged (β=1.0). β is a free parameter; sweep {2,5,10} in Stage 4.4.
- [x] Si dormancy mechanic — replaces starvation death (Stage 4.3)
  - Triggered: wealth < k_dormant×metabolism. Agent suspends instead of dying.
  - Passive trickle absorption: τ_trickle×cell_sugar/step. Does NOT consume cell sugar.
  - Reactivation: wealth ≥ k_reactivate×metabolism. Permanent death: >T_dormant_max steps.
  - Parameters: k_dormant=1.0, τ_trickle=0.3, k_reactivate=3.0, T_dormant_max=50.
  - C agents NEVER use dormancy (always starvation death).
- [x] Si η=1.0 (no juvenile ramp) — Stage 4.3
  - η(a) age-efficiency ramp is C-only from Stage 4.3. Si fission offspring start at η=1.0.
  - _use_eta=False for all Si agents regardless of life_history config.
- [x] Per-agent death_events.parquet (Stage 4.3)
  - Schema: step, cause, age, wealth, psi, cred, agent_type, season_phase, dormancy_duration
  - Causes: starvation, senescence, permanent_dormancy. psi/cred NaN for Si.
- [x] Si Cred economy — near-dormancy accumulation, counter-cyclical (Stage 5.1)
  - Stage 5 (surplus-based): si_cred_i += max(0, harvest−cost) × r_cred_Si — was PRO-CYCLICAL (cred fell in troughs)
  - Stage 5.1 (near-dormancy): Δsi_cred=1 if wealth ∈ [k_dormant, k_dormant+k_cred_band)×cost_i else 0 — COUNTER-CYCLICAL
  - σ_Si_eff_i = σ_Si + κ_Si × tanh(si_cred_i / C*_Si) — unchanged (high-Cred agents more explorative)
  - Null control (Stage 5.1): N_mean=335, dorm=4.9%, si_cred_mean=0.97, σ_eff_mean=1.28 (>σ_Si=1.238) ✓
  - Counter-cyclicality gate PASSED: trough/peak = 1.13/0.49 (seed=42), 1.58/0.66 (seed=43)
  - Si still collapses at A=0.75 T=200 (H1(ii) inversion structural — dormancy cliff)
  - H1(ii) inversion is structural (dormancy cliff), not a model artifact from missing Cred
- [ ] Si ψ_i utility hook (Stage 5+)
  - Currently ψ_i carried but inactive for Si
  - Si sociability has different meaning: proximity to known-good foraging spots
    not proximity to other agents
- [ ] Si HiveMind reproduction coordinator (Stage 7+)
  - Skeleton already in ReproductionCoordinator protocol
  - Population-level collective reproduction decision
  - Config: reproduction.coordinator="hivemind"
  - Raises NotImplementedError until implemented
  - Orthogonal to C mechanics — Si-only

### Pending — both C and Si (Stage 4+)
- [ ] c1_i behavioral hook: conformism→individualism axis (Stage 4+)
  - Currently carried and inherited, not behaviorally active
  - Hook: c1_i affects cultural transmission probability (Deffuant updating)
  - Low c1 (conformist): copies nearby agents' traits more readily
  - High c1 (individualist): resists copying, drifts independently
  - Klemm prediction: C civilization bimodal c1 distribution at steady state
- [ ] c2_i behavioral hook: cooperation→competition axis (Stage 4+)
  - Currently carried and inherited, not behaviorally active
  - Hook: c2_i modulates joint-task strategy
  - Low c2 (cooperative): seeks joint tasks even at personal resource cost
  - High c2 (competitive): defects from joint tasks when solo harvest > Matthew share
  - Prerequisite for defection/criminal emergence mechanics (Stage 6+, TMTS now)
- [ ] Deffuant-style bounded confidence cultural updating (Stage 4+)
  - Agents update cultural traits toward neighbors within confidence bound
  - For C: weighted by Cred (prestige bias — Boyd & Richerson)
  - For Si: unweighted (egalitarian)
  - Literature: Deffuant et al. (2000), Hegselmann & Krause (2002)
- [ ] Prestige bias in cultural transmission (Stage 4+)
  - C agents preferentially copy high-Cred neighbors' traits
  - Connects Cred economy to cultural evolution
  - Literature: Boyd & Richerson (1985) ch.5
- [ ] Generational oscillation in cultural trait mean T(t) (Stage 5+)
  - Intergenerational transmission with reactive bias
  - Offspring partially react against parent extremes → damped oscillation
  - Literature: Turchin secular cycles
- [ ] Heuristic drift of φ_i (Stage 5+)
  - Cultural transmission with copy-error across generations
  - Needs high turnover (perturbations) to produce interpretable signal
- [ ] β as per-agent born-trait (Stage 7+)
  - Currently population-uniform
- [ ] C** as independent parameter from C* (deferred Q11)
  - Evaluate after Stage 4 data

---

## World mechanics (WM) — full tracker

### Implemented
- [x] 50×50 toroidal grid, twin sugar peaks (Stage 1)
- [x] Growback rule G_α, α=1 (Stage 1)
- [x] Replacement rule R — being replaced by variable population (Stage 4.1a)
- [x] Joint-task detection: proximity-based, d=1, capacity threshold=4 (Stage 2)
- [x] WorldPerturbation protocol: NullPerturbation, SeasonalOscillation (Stage 4)
- [x] effective_capacity field on World (Stage 4)

### Pending — Stage 4.1+
- [ ] Variable population dynamics (Stage 4.1a)
  - Fixed N=250 constraint removed
  - Population can collapse to zero under extreme stress
  - Season-by-season N(t) becomes primary H1(ii) diagnostic

### Implemented — Stage 4.2
- [x] Seasonal amplitude × period sweep: A∈{0.5,0.75} × T∈{50,100,200} + null controls (8 runs). Stage 4.2.
  - H1(ii) primary finding: C collapses at T=200 (Allee+100-step trough), survives T=100/T=50. Si survives all.
  - Period-dependent bistability: C's Allee mechanism is a period-selective vulnerability, not a general weakness.

### Implemented — Stage 4.3 (pool)
- [x] Pool carry-over ρ=0.3: pool_t+1 = ρ×leftover_t + contributions_t+1 (Stage 4.3)
  - _balance persistent in SupportPool across steps
  - ρ=0 recovers Stage 4.1c behaviour exactly
  - Effect: T* narrowed (100,200)→(100,112); higher baseline C stress offset the buffering
- [x] Pool cap k_pool_cap=20: cap = k×N_active_C×mean_metabolism_C (Stage 4.3)
  - Available-room approach in contribution loop
  - Non-limiting at observed N; prevents unbounded peak accumulation

### Pending — Stage 4.4+
- [ ] β sweep {2,5,10} for Si differential metabolism (Stage 4.4). β=2 grid-calibrated in 4.3; sweep to establish sensitivity.
- [ ] λ>0 wealth inheritance (C only). (λ=0 default confirmed in 4.1a; deferred from 4.3.)
- [ ] τ_pool architectural tension resolution. (Deferred from 4.3.)
- [ ] Amplitude asymmetry sweep: longer trough than peak. (Deferred from 4.3.)
- [ ] ψ_i hook redesign (Q25): flat quartile distribution found in Stage 4.3; ψ redesign required.
- [ ] Mobile resources (Stage 4.4)
- [ ] Scheduled shocks (Stage 4.4)

### Pending — Stage 5+
- [ ] Inter-pool connectivity / exchange (Stage 5+)
  - Weak connectivity between proximity pools
  - Foundation for inter-group trade mechanics
  - TMTS until pool mechanics validated in Stage 4.1c
- [ ] Connectivity sweep: Pangea ↔ Archipelago axis (Stage 5)
- [ ] Multi-world batch runner (Stage 5)
  - BatchRunner, Common-random-numbers (CRN) method

### Pending — Stage 6
- [ ] Statistical framework
  - Pre-registered metrics, effect sizes, power analysis

---

## Life history mechanics — design decisions record

These are design decisions made in conversation that must not be re-litigated or
accidentally implemented differently.

### Age windows
- **Reproductive window** [a_rep_min, a_rep_max]: who can produce offspring
  - a_rep_min ≈ 15 steps, a_rep_max = τ_max - 10 steps
- **Active foraging window** [a_forage_min, a_forage_max]: full harvest efficiency
  - a_forage_min ≈ 15 steps, a_forage_max = τ_max - 10 steps
  - Outside this window: harvest at η(a) < 1 per Cobb-Douglas curve
- These are TWO SEPARATE windows, not one. Reproductive senescence ≠ foraging senescence.

### Birth rate model
- DTM-based unimodal wealth-dependent function
- Three regimes: starvation floor (P=0), stress zone (P=P_max), prosperity zone (declining)
- Thresholds relative to mean population wealth, not absolute values
- C birth additionally modulated by Cred (Turchin elite overproduction term γ)
- Literature: Thompson-Notestein DTM, Turchin (2003), Sugarscape fertility ABM (arxiv 2406.13816)

### Support structure
- Three levels: (1) self, (2) proximity pool, (3) status-mediated (C only)
- Pool is local (radius r=3), independent per cluster
- Si: levels 1+2 only. No status component. Reciprocal priority for support.
- C: levels 1+2+3. High-Cred agents contribute more and earn Cred for it.
- Inter-pool connectivity: TMTS, Stage 5+

### Secular cycles prediction (Turchin)
- C civilizations should show more pronounced boom-bust cycles than Si
- Mechanism: Cred-amplified reproduction → elite overproduction → resource compression → crisis → reset
- Si civilizations: smoother dynamics (wealth-only reproduction, reciprocal not dominance Cred)
- Testable in Stage 4.2+ with variable population and amplitude sweep

---

## Open design questions (unresolved)

| Q | Topic | Status |
|---|---|---|
| Q6 | Cred_bonus_per_participant scaling | TBD — scale with cell capacity or sugar harvested? Stage 4+. |
| Q11 | C** independent from C* | Deferred. Evaluate after Stage 4 data. |
| Q15 | Amplitude A sweep values | Stage 4.2: {0.5, 0.75} |
| Q16 | Period T sweep values | Stage 4.2: {50, 100, 200} |
| Q17 | Asymmetry of seasonal cycle | Stage 4.2 |
| Q18 | c1/c2 behavioral hooks design | Stage 4+ after c1/c2 Deffuant design |
| Q19 | Prestige bias strength parameter ω | Stage 4+ |
| Q20 | γ (Cred-modulated birth rate) value | ✓ Resolved Stage 4.2: γ=0.2 locked. Mean boost ≈1.09. Sweep to Stage 5+. |
| Q21 | λ (wealth inheritance fraction) | Default λ=0 confirmed. Sweep Stage 4.3 (C only). |
| Q22 | τ_pool recalibration | ✓ Partial resolution Stage 4.2: τ_pool halved 0.10→0.05. Criterion 4 still fails — design tension (dual regulator role). Full resolution deferred to Stage 4.3. |
| Q28 | H1(ii) test at T=200 — C vs Si seasonal resilience | ✓ Stage 4.3 revised finding: C collapses all 4 seasonal conditions (A=0.5 and 0.75, T=50/100/200). Si survives 3/4 (A=0.5 any T; A=0.75 T=200 collapses). H1(ii) MIXED: Si dominates at moderate amplitude regardless of period; both collapse at high amplitude+long period. Stage 4.2 result superseded (equal-metabolism confound corrected). |
| Q29 | ψ_i starvation quartile analysis | ✓ Stage 4.3: flat distribution across quartiles. Deaths perfectly split 25/25/25/25% across ψ quartiles. No mortality selection by ψ. Flagged for ψ redesign (Q25). |
| Q30 | β_Si calibration — what value is scientifically valid? | Stage 4.3: β=5 (blueprint) infeasible on max_sugar=4 grid. β=2 locked as Stage 4.3 value. Sweep {2,5,10} planned Stage 4.4. Larger β requires grid parameter co-design. |
| Q31 | T* narrowed under ρ=0.3 — unexpected fragility of Stage 4.3 C | T* narrowed from (100,200) to (100,112) despite pool carry-over. Root cause: higher baseline C starvation (est_starv=2.19 vs ~0.5 Stage 4.2) likely from η-ramp young-adult starvation. Investigate in Stage 4.4. |
| Q32 | C bistability at k=4 — no stable N∈[150,400] achievable | Stage 4.4 Diagnostic: k=4 grid eliminates resource competition (max_sugar=16 → agents never starve at any N). Without a natural carrying-capacity ceiling, C is bistable: p≤0.05 → Allee collapse; p≥0.07 → explosion to N~1600. Solution requires density-dependent birth suppression (births decline as N approaches carrying capacity K). Design options: (a) logistic birth multiplier (1−N/K), (b) per-cell competition penalty, (c) resource-depletion ceiling at k=4. Decide at Stage 4.5. |
| Q23 | θ_birth thresholds | DTM-motivated, relative to mean wealth |
| Q24 | Si Cred accumulation mechanism | Literature search pending Stage 5+ |
| Q25 | Si ψ_i meaning | "Proximity to good foraging spots" not "proximity to agents" |
| Q26 | HiveMind coordination mechanism | Design pending Stage 7+ |
| Q27 | Defection/criminal emergence | Requires c2 hook active. TMTS. Stage 6+. |

---

## Architecture hooks — built and pending

| Hook | Status | Where | Stage |
|---|---|---|---|
| `WorldPerturbation` protocol | ✓ Built | world_perturbation.py | Stage 4 |
| `ReproductionCoordinator` protocol | ✓ Built skeleton | reproduction.py | Stage 4.1a |
| HiveMind coordinator stub | ✓ Built skeleton (Si only) | reproduction.py | Stage 4.1a |
| `BatchRunner` for multi-world runs | ⏳ Pending | batch.py | Stage 5 |
| Common-random-numbers RNG | ⏳ Pending | batch.py | Stage 5 |
| c1/c2 behavioral hook points | ⏳ Pending | carbon.py, si_bounded.py | Stage 4+ |
| Deffuant update protocol | ⏳ Pending | cultural.py (new) | Stage 4+ |
| Inter-pool exchange protocol | ⏳ Pending | support_pool.py | Stage 5+ |

---

## Known bugs and data integrity notes

| ID | Description | Resolution |
|---|---|---|
| BUG-001 | Stage 2 pre-patch baseline overwritten. Three key values hardcoded as _S2_PRE_SWITCH. | Load confirmed baselines from parquet always. |
| BUG-002 | Stage 3.3 incorrectly applied biparental reproduction to Si agents. Si agents should use single-parent fission. | Fixed in Stage 4.1a. ReproductionCoordinator is now C/Si-aware. Always check C/Si distinction table before implementing reproduction mechanics. |
| BUG-003 | `support_pool.py`: Cred-scaled pool contribution used `agent._cred_scale` (never existed on BaseAgent). `hasattr()` always returned False → tanh factor = 0 → zero above-base Cred pool contribution for all 4.1c runs. `cred_pool_contribution` was 0.0 in all 4.1c data. | Fixed Stage 4.2 Task 0: replaced with `getattr(getattr(agent, '_decision', None), 'cred_scale', 10.0)`. After fix: cred_pool_contribution = 3.65/step. All 4.1c parquets are silently invalid for Cred-scaled pool metrics. |

---

## Standing rules (apply to every stage)

1. **Confirmed baseline parquets are read-only.** Load from parquet, never re-run.
2. **New runs write to new output directories.** Never overwrite confirmed outputs.
3. **One parameter per stage.** Each stage sweeps at most one new parameter.
4. **Load before run.** If a config point exists in confirmed outputs, load it.
5. **Report negative results.** Do not silently re-run until success.
6. **Check C/Si distinction table before implementing any mechanic.**
7. **Pre-registration discipline.** Stage 6 onwards strictly.
8. **LITERATURE.md updated** whenever a paper, model, or mechanism is consulted.
9. **ROADMAP.md updated** at the end of every stage or directive.
10. **Report completeness.** Every report must include:
    - A number for every success criterion — PASS/FAIL alone is not sufficient.
    - All tuning attempts documented with values tried and outcomes observed.
    - All diagnostic runs included with results, even if null.
    - Seasonal vs static comparison table if both were run.
    - Any parameter value that changed from the blueprint default, with justification.
    - Full tuning history table for any parameter that required more than one attempt.
    A report missing any of these is incomplete. Claude Code must append missing
    sections before the supervisor reviews results.
11. **Plot embedding (mandatory from Stage 4.2 onwards).** Every report.md must embed its diagnostic plots inline using relative paths. Plots must resolve when report.md is rendered — do not upload plots separately.

    Required output structure:
    ```
    outputs/<run_name>/
    ├── report.md
    └── figures/
        ├── <plot_name>.png
        └── ...
    ```

    In report.md, reference plots as:
    ```markdown
    ![Caption](figures/plot_name.png)
    ```

    A `generate_figures.py` script (or equivalent) must exist that reads from parquets and writes all figures to `outputs/<run>/figures/`. This script must be runnable independently of the simulation (figures regenerable from cache without re-simulation).

    A report without embedded, resolving plot references is incomplete per Rule 10.
13. **HTML reports with base64-embedded figures (mandatory from Stage 4.4 onwards).** All stage reports must be single self-contained HTML files with figures embedded as base64 `<img src="data:image/png;base64,...">` — no external file dependencies. Output: `outputs/<stage_dir>/report.html`. Markdown reports (report.md) remain for diagnostic stages; full-stage reports must be HTML.
12. **Pool gate criterion is mean-based.** `pool_draw_unmet_frac < 20%` is evaluated as the time-mean over t≥500 (or the quasi-stationary window for that stage). Instantaneous peaks above 20% do not constitute a gate failure but must be reported alongside the mean in the pool diagnostics table.

    Pool diagnostics table format (mandatory when pool is active):

    | Config | Mean contributed/step | Mean drawn/step | Mean unmet (t≥500) | Peak unmet (t≥500) | Gate (mean<20%) |
    |---|---|---|---|---|---|
    | *(populate with run data)* | | | | | |

## Pre-registered Hypotheses
| Hypothesis | Description | Registered | Status |
|---|---|---|---|
| H_cc | carry_discount counter-cyclical C recovery | Stage 4.5 patch | Pending Stage 5 |
| H-ORTHOGONALITY | C and Si home-range distributions are orthogonal axes (C home-range is shaped by social pull; Si by foraging pull). Predicted to diverge measurably at medium-⟨ρ⟩ once movement decomposition diagnostic is built. | 2026-05-30 OWE-1 §3.6 | OPEN — pre-registration only; test requires OWE-13 |
| H-instinct-debt | instinct-debt hypothesis (see HYPOTHESES.md §2): registered concept, details in HYPOTHESES.md | 2026-05-30 OWE-1 §0 | OPEN — see HYPOTHESES.md |

---

## Sweep-Matrix axes (planned for Stage 5.x LHS scan)

The primary comparison sweep is: **⟨ρ⟩ × A × T × seeds × {C, Si}**

| Axis | Symbol | Planned range | Notes |
|---|---|---|---|
| Population density (mean agents/cell) | ⟨ρ⟩ | low (~2%), medium (~5%), high (~10%) | Controls resource competition intensity and Allee dynamics |
| Seasonal amplitude | A | {0.5, 0.75, 0.9} | As in Stage 4.2–5 sweeps |
| Seasonal period | T | {50, 100, 200, T*±margin} | T* bracket confirmed in Stage 5 |
| Seeds | — | ≥5 (CRN) | Common-random-numbers |
| Strategy | — | {C, Si} | Matched worlds |

⟨ρ⟩ is the **primary new axis added OWE-1 (2026-05-30)**: scaling from 50×50 to 100×100 at fixed density means ~2000 agents, and density-dependent dynamics (carrying-cost, Allee) need systematic ⟨ρ⟩ coverage to distinguish strategy effects from density effects.

**Locked campaign run-length (OWE-1.1, supervisor 2026-05-31):** standard run-length =
**12,000 steps** (1000 yr at 1 step = 1 month, ~4 secular cycles); **transient exclusion
~500 steps** declared up front (~3.8 productive cycles, clears the ≥3-cycle bar for
cycle-length/amplitude estimation). 24,000 held in reserve only if cycle-length estimation
proves noisy. Applies to the H-EMERGE-1 / sweep campaign.

**Target geometry (OWE-1, locked):** 100×100 cells, 1 step = 1 month. **N_carry = 4100
for the 100×100 geometry** (OWE-1.1, 2026-05-31): measured N_carry→settled-N mapping
settled ≈ 0.754·N_carry − 566 on 100×100; N_carry=4100 → settled N ≈ 2357 (within the
2000–3000 target band), clean settle, est_starv = 0.000. **Static rel_std ≈ 0.019**
(corrected 2026-06-02 from the OWE-1.1 single-run 0.014 to the R0 3-seed mean 0.0181/0.0196/0.0206;
equivalence tolerance widened to ±0.007 to reflect measured seed scatter). N_carry is a
scale-setting calibration choice, NOT an emergent prediction — set once, shared across C
and Si arms, locked before examining H1(ii) at the new scale (OWE-14 re-confirms the
inversion at this scale). Production 50×50 value remains N_carry=400.

---

## Owed items (tracked backlog)

Items registered but not yet implemented. Checked each stage; cleared when done.

| ID | Item | Source | Status |
|---|---|---|---|
| OWE-1 | Absolute-scale calibration: benchmark 100×100 geometry, assign cell→km and metabolic-unit→kcal under 1-step=1-month constraint | OWE-1 Blueprint 2026-05-30 | IN PROGRESS (this pass) |
| OWE-2 | Terrain topography mechanic (spatially varying sugar + metabolism multiplier) | Stage 5.x agenda; chat_handoff §2 | OPEN |
| OWE-3 | Stage 5.1 LHS parameter sensitivity scan (5D: A×T×N_carry×T_dormant_max×α_carry, ~30 pts) | chat_handoff §4 | OPEN |
| OWE-4 | Davies/Loihi neuromorphic citation: confirm and add to LITERATURE.md (currently [INLINE] in MECHANISMS §9) | ARCHITECTURE §15.1 | OPEN |
| OWE-5 | Si ψ utility hook: implement proximity-to-foraging-spots signal (distinct from C's agent-proximity signal) | ROADMAP "Pending — Si"; MECHANISMS §1.1 C2 flag | OPEN |
| OWE-6 | Physical-channel inheritance: add metabolism/vision/max-age vertical transmission with control toggle | ARCHITECTURE §12.1-A; supervisor decision | OPEN — PROPOSED |
| OWE-7 | HiveMind coordinator implementation (Si, collective reproduction decision) | ARCHITECTURE §13; Stage 7+ | DEFERRED |
| OWE-8 | Movement-decomposition enumeration: difference-set axes for C vs Si foraging vs social displacement | OWE-1 §3.6; H-ORTHOGONALITY | OPEN |
| OWE-9 | σ_inherit corrective sweep: target c1/c2 diversity (not ψ), ≥8 seeds, correct statistic (SD not Gini) | ARCHITECTURE §12.1-D | OPEN — corrective directive pending |
| OWE-10 | Stage 6 statistical framework (power analysis, effect sizes, pre-registered metrics) | ROADMAP Stage 6 | OPEN |
| OWE-11 | Larger-N feasibility check: measure N-scaling exponent at 100×100 to confirm "cheap lever" claim | OWE-1 Blueprint §6 | OPEN — measured in OWE-1 Task 1 |
| OWE-12 | Minimum-band-size-in-trough diagnostic: log min per-band N in trough phase; raise N if Allee/finite-size artifacts | OWE-1 Blueprint §6 | OPEN — design stage |
| OWE-13 | Movement-decomposition diagnostic: per-agent per-step decomposition of displacement into foraging-pull vs social-pull (ψ) | OWE-1 Blueprint §3.6 + §6 | OPEN — build at movement-instrumentation stage |
| OWE-14 | Re-confirm H1(ii) inversion at calibrated N_carry (≥3 seeds, C vs Si) before trusting H1(ii) at the new 100×100 scale | OWE-1.1 Directive §B.3 (2026-05-31) | OPEN — authorised separate run, NOT yet run |

---

## Pre-registered Hypotheses
