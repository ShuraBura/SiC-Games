# SiC Games — Artifact Index

**Purpose:** The authoritative index of every *output* the project has produced — reports, benchmarks, diagnostics, run logs. This is the document that answers "where is the run that showed X?" It exists because the project has repeatedly lost track of results that *did* exist (the Stage 5.2 ψ definition, the trait-layer citations, and the 2026-05-28 perf audit were each reasoned-around rather than retrieved). One row per artifact.

**Discipline:**
- **Code adds a row whenever it emits any report, benchmark, or diagnostic** — this trigger must be in CLAUDE.md or the index rots.
- Columns: artifact name · date · type · the question it answered · headline result (one line) · location.
- **Location is mandatory.** An artifact not findable from this index is, for project purposes, lost. If a file lives only in a chat upload, record that and ask Code to commit it to the repo.
- This index records *where* and *what-headline*; the substantive findings live in **RESULTS.md**, the methods/specs in the blueprints. Point to those, don't restate them.

**Seeding note (2026-05-29):** This initial fill is built from artifacts visible in the project files and this session's uploads. It is **certainly incomplete** — Code should reconcile it against the actual repo (run logs, parquets, any reports not surfaced here) and mark the gaps. Items marked `[CHAT-ONLY]` were provided as chat uploads and may not be committed to the repo; Code should confirm and relocate.

---

## Directives & blueprints that commissioned runs
*(These are specs, not results — listed so each result below can be traced to the directive that ordered it. Full blueprint set is in the project root; only run-commissioning ones are indexed here.)*

| Artifact | Date | Type | Question | Location |
|---|---|---|---|---|
| SiC_Games_Benchmark_Runtime.md | — | benchmark directive | How does runtime scale with grid and N? What grid is feasible for LHS? | project root |
| SiC_Games_Perf_Audit.md | — | audit directive | Where is step time spent; what can be optimised without changing science? | project root |
| SiC_Games_Perf_Opt_Blueprint.md | — | optimisation blueprint | Optimisation plan | project root |
| SiC_Games_JT_Fix_Benchmark.md | — | benchmark directive | Joint-task neighbour-cost fix verification | project root |
| SiC_Games_Stage4_4_k3_Feasibility.md | — | feasibility | k3 feasibility (Stage 4.4) | project root |

## Reports & results

| Artifact | Date | Type | Question answered | Headline result | Location |
|---|---|---|---|---|---|
| Stage 5.2 report (Cultural Dynamics) | 2026-05-29 | run report | Do c2 defection, Deffuant, and the σ_inherit sweep behave as designed? | Cultural layer stable; c2 defection rare (3.7%) and **uncorrelated with c2** (no selection differential); Deffuant homogenises ψ as designed; **σ*=0.10 selection was mis-gated on ψ — RETIRED** (see DEAD_ENDS, ARCHITECTURE §12.1-D). | `[CHAT-ONLY]` report.html — confirm repo location |
| Perf Audit + Optimisation report | 2026-05-28 | benchmark + audit | Step-time breakdown; scaling exponents; feasible grid/N for LHS | LOW-risk fixes applied, **science unchanged to 1e-9**; **N exponent 1.05** (≈linear), **grid exponent 2.957** (near-cubic, target ≤2.0); B0(50²,250)=13 ms/step, B2(100²,1000)=110 ms/step, B4(150²,2000)=410 ms/step; LHS feasible to N=2000/150² as weekend batch. MED/HIGH-risk items deferred (§6 backlog). | `[CHAT-ONLY]` report_perf_audit.html — confirm repo location |
| Stage 7.5 GATE A0 (array restructure) | 2026-06-06 | parity gate | Does the SoA+harness reproduce the oracle's per-agent updates? | **PASS.** SoA container + parity harness stood up; Tier-1 per-agent updates migrated bit-identically (cred decay, metabolize C/greedy + Si dormancy state machine, Si-cred band, η); σ is **Tier-2 (rtol 1e-9)** — finding: np.tanh ≠ math.tanh by ~1 ULP (ARCHITECTURE §12.1-G). Oracle untouched. Suite 287 passed. | `sic_games/outputs/stage7_5/gate_A0_report.md` |
| Stage 7.5 GATE A1 (reductions) | 2026-06-06 | parity gate + N-scaling benchmark | Do vectorised reductions match the oracle at rtol 1e-9? Does killing mean_cred-per-birth eliminate the O(N²) tail? | **PASS.** `mean_cred_vec`, `mean_wealth_vec`, `gini_vec`, `harvest_split_segment` all Tier-2 (rtol 1e-9, actual deltas < 1e-13). **Oracle 10k→19k exponent: 2.055** (confirms O(N²)); **vec: 0.746** (sub-linear SIMD, hotspot gone). Speedup 26,635× at N=19k. Numba eligibility confirmed by inspection (no agent-object access). Oracle untouched. Suite 292 passed. | `sic_games/outputs/stage7_5/gate_A1_report.md` |
| Stage 7.5 GATE B1 (VecJTM) | 2026-06-06 | parity gate + occupancy benchmark | Does VecJTM eliminate the occupancy cliff and achieve statistical equivalence? | **STOP — two gate failures.** OCC_1600: 115.5 ms/step (32% speedup vs oracle 170.6 ms). OCC_3200: hard-infeasible (both oracle and VecJTM) due to O(N²) `mean_cred()` per birth at run.py line 784 (the GATE A1 hotspot; oracle is frozen so it cannot be fixed yet). Tier-3 battery FAIL: population extinct before WINDOW_START=251; min N(t) coverage = 0.845 < 0.90 threshold. **Undeclared behavioral difference found:** oracle allows agent double-participation across adjacent JT cells (processed_cells tracks cells not agents); VecJTM consumed mask prevents it. Supervisor decisions required: (A) match oracle semantics or accept improvement; (B) revise battery config; (C) performance path. Unit tests: 9 new pass; suite 301 total. | `sic_games/outputs/stage7_5/gate_B1_report.md` |

| Stage 7 terrain generator (module) | 2026-06-10 | code module | Port the JS prototype terrain pipeline to Python as precomputed static arrays | `generate_world(knobs) → WorldFields`; all arrays frozen; byte-identical to JS prototype. 16/16 unit tests pass. | `sic_games/src/sic_games/terrain.py` |
| Stage 7 oracle battery | 2026-06-10 | equivalence reference | 27 prototype-computed characterization vectors (9 configs × seeds 42/7/1001) used as the equivalence gate | D4-frozen. Equivalence gate: 27/27 worlds within tolerance (±3pp biome, ±3pp water pcts, ±5% relief, ±0.3° slope, ±0.05 gameHumpPeak). | `SiC_Games_Terrain_Oracle_Battery.json` (project root) |
| Stage 7 equivalence gate | 2026-06-10 | gate script | Does the Python terrain generator reproduce the JS prototype within pre-committed tolerances? | 27/27 GREEN. | `sic_games/outputs/stage7_terrain/gate_equivalence.py` |
| Stage 7 acceptance gate | 2026-06-10 | gate script | A7.1 forest gradient; A7.2 coexistence band; A7.3 no matrix-dominance; A7.4 game unimodal in NPP | A7.1–A7.4 all GREEN. LHS sweep 150×4=600 worlds: 600/600 unimodal, 0 exempt. gameHumpPeak (diagnostic): min=0.20 max=0.50 mean=0.41. | `sic_games/outputs/stage7_terrain/gate_acceptance.py` |
| Stage 7 forest-knob gradient chart | 2026-06-10 | figure | Is the full forest↔grassland gradient reachable by the forestK knob? | Smooth monotone gradient from 0% forest (forestK=0) to 73.8% forest (forestK=1). | `sic_games/outputs/stage7_terrain/a71_forest_gradient.png` |
| Stage 7 mosaic_mid biome map | 2026-06-10 | figure | Spatial mosaic structure of the canonical mixed world (mosaic_mid, seed=42) | Forest patches embedded in savanna/woodland matrix; wetland fringe; small desert patches. | `sic_games/outputs/stage7_terrain/mosaic_mid_seed42_biome.png` |

**`characterize_map()` convention:** every generated world must have its `characterize_map()` output saved alongside the world as `map_vector.json` in the run output directory (e.g. `outputs/[stage_label]_seed[N]/map_vector.json`). This vector is the permanent measurement layer; downstream runs validate against it.

## Key established numbers (quick reference — full context in the reports above)

| Quantity | Value | Source artifact |
|---|---|---|
| Stage 1 substrate | Gini=0.47, N=250, peaks=63%, seed=42 | (ROADMAP status) |
| N-runtime exponent (post-audit) | 1.053 | Perf Audit 2026-05-28 |
| mean_cred oracle hotspot 10k→19k exponent | 2.055 | Stage 7.5 GATE A1 2026-06-06 |
| mean_cred vec 10k→19k exponent | 0.746 (sub-linear SIMD) | Stage 7.5 GATE A1 2026-06-06 |
| OCC_1600_g40 VecJTM ms/step | 115.5 (vs oracle 170.6, −32%) | Stage 7.5 GATE B1 2026-06-06 |
| OCC_3200_g40 VecJTM status | hard-infeasible (O(N²) mean_cred() per birth; run.py line 784, the GATE A1 hotspot, unfixed in frozen oracle) | Stage 7.5 GATE B1 2026-06-06 |
| Tier-3 battery min N(t) coverage | 0.845 (FAIL; threshold 0.90) | Stage 7.5 GATE B1 2026-06-06 |
| grid-runtime exponent (post-audit) | 2.957 | Perf Audit 2026-05-28 |
| ms/step B2 (100×100, N=1000) | 110.2 | Perf Audit 2026-05-28 |
| ms/step B4 (150×150, N=2000) | 409.7 | Perf Audit 2026-05-28 |
| Si extinction (A=0.75/T=200) | both seeds, by t≈1500 | Stage 5.1 (confirm artifact) |
| c2 defection rate (steady state) | 0.0374, defector-c2 ≈ cooperator-c2 | Stage 5.2 report |
| test count (Stage 5.2) | 233 passed | Stage 5.2 report |
| test count (Phase 1 Stage 1c + guard + config guard) | **404 passed** (2026-06-13) | Full suite post-directive |
| test count (Blueprint A complete) | **430 passed** (2026-06-14) | Full suite post-Blueprint A |

---

## Gaps to reconcile (Code)
- Locate and commit the Stage 5.1 closure report (Si Cred near-dormancy result, the extinction finding) — referenced in the handoff but not surfaced as a file.
- Confirm repo paths for the two `[CHAT-ONLY]` reports above; if they exist only as chat uploads, commit them.
- Index any run parquets / batch outputs from Stages 4.x that established locked parameters (κ sweep, 2D κ×α scan, f_C sweep, β sweep) — these are referenced in PARAMETERS history but their artifacts aren't indexed.
- Backfill dates for the undated directives above.

---

## Reorg reconciliation report (2026-06-05)

The whole project tree was reorganised into the DOCS_CHARTER structure. Every move
was a history-preserving `git mv` (or, for gitignored `.bak` litter, a filesystem
relocate) — **nothing was hard-deleted**. Baseline commit: `f31eebd`.

**What moved where (homes):**
| From | To | Note |
|---|---|---|
| `Model/ROADMAP.md`, `Model/MODEL_SPEC.md`, `Model/ARTIFACTS.md`, `Model/INDEX.md` | `docs/` | the four homes that were under `Model/` |
| `ROADMAP.md` (root) | `docs/ROADMAP.md` | root duplicate folded in earlier in pass |
| `SiC_Games_DOCS_CHARTER.md` | `docs/DOCS_CHARTER.md` | governance |
| `SiC_Games_TARGETS_seed.md` | `docs/TARGETS.md` | seeded T-1/T-2/T-3 |
| `sic_games/LITERATURE.md` (fuller) | `docs/LITERATURE.md` | promoted as unify base |
| Carbon-Prototype `.md` | `origin/` | founding spec, canonical |

**Homes created (new content this pass):** `docs/RESULTS.md` (R-1), `docs/DEAD_ENDS.md`
(DE-1), `docs/HYPOTHESES.md` (consolidated). `docs/INDEX.md` rewritten to the 11-home
routing table. `README.md` created at root.

**Duplicates resolved:**
- **HYPOTHESES** — two divergent copies (`./HYPOTHESES.md`, `Model/HYPOTHESES.md`)
  consolidated into one `docs/HYPOTHESES.md` (3 live entries); H1(ii)→RESULTS R-1,
  H-ORTHOGONALITY→TARGETS T-2 + DEAD_ENDS DE-1, H-instinct-debt→TARGETS T-3.
- **LITERATURE** — two copies; fuller `sic_games/LITERATURE.md` promoted as base, the
  root copy's unique Si-Cred synthesis appended (merge note in-file).
- **CLAUDE.md** — root master kept; old `sic_games/CLAUDE.md` superseded; path-triggers
  re-pointed into `../docs/`.

**Archived (in `archive/superseded/`, never deleted):**
`HYPOTHESES_root_2026-06-05.md`, `HYPOTHESES_Model-Hemerge_2026-06-05.md`,
`LITERATURE_root-SiCred_2026-06-05.md`, `CLAUDE_sic_games-OLD_2026-06-05.md`,
Carbon-Prototype `.pdf` (the `.md` is canonical in `origin/`). Pre-existing `.bak`
litter and prior code snapshots (`archive/v5.1*`) retained as-is.

**Stale path refs:** grep of the live homes found none broken; `sic_games/CLAUDE.md`
tree + triggers updated to point at `../docs/`. Test count corrected (201→256).

**Still open (charter §6, separate later directive):** split MODEL_SPEC →
ARCHITECTURE + MECHANISMS; extract PARAMETERS. Until then MODEL_SPEC.md is their
interim home and the CLAUDE.md locked-param table is the interim PARAMETERS home.

---

## MODEL_SPEC split (2026-06-06)

The first half of charter §6 is **done**: `MODEL_SPEC.md` (v0.2 full extraction) was split
into two charter homes ahead of the §7.5 array-restructure (which writes per-mechanic
equivalence-tier classifications into MECHANISMS and decisions into the ARCHITECTURE log):
- **`docs/MECHANISMS.md`** — construct registry: §0 classification, §1–§8, §10, §11, §14 param index.
- **`docs/ARCHITECTURE.md`** — §0 principle, §9 world/resource substrate (charter §2.1 "how-the-
  world-works half"), §12 decision-log (new entry §12.1-F records the split), §13 seams, §15 known-gaps.

Method: content moved verbatim, no facts altered; section numbers preserved across both files
so every existing "MODEL_SPEC §N / §12.x / §15.x" pointer still resolves. Live pointers updated
(INDEX, ROADMAP OWE-4/5/6/7/9, CLAUDE rule 10, this index). Source archived at
`archive/superseded/MODEL_SPEC_v0.2_pre-split_2026-06-06.md`. **Still open:** PARAMETERS
extraction (the §6 second half) — interim home remains the CLAUDE.md locked-param table.

---

---

## Phase 1 Artifacts (Phase 1 Stage 1 onward, 2026-06-13)

| Artifact | Date | Type | Question answered | Headline result | Location |
|---|---|---|---|---|---|
| Phase 1 Stage 1 acceptance | 2026-06-13 | gate script | ForageField + TerrainDiagnostics: all A-gates GREEN? | A1–A7 all GREEN. forage_kcal, npp_gm2, is_shore live. | `outputs/phase1_stage1/acceptance_and_artifacts.py` |
| Phase 1 Stage 1b acceptance | 2026-06-13 | gate script | Water decomposition diagnostic: A1–A6 GREEN? | A1–A6 GREEN. exterior/interior BFS, shoreline, diagnostic guard. | `outputs/phase1_stage1b/acceptance_and_artifacts.py` |
| Stage 1b waterK sweep (M1/M2) | 2026-06-13 | sweep | Where does exterior guard fire? Is coastline morphology detectable? | Guard fires at wK≈0.80. M2 finding retracted (s2a = crinkliness/area, not coastline length). | `outputs/phase1_stage1b/` |
| Phase 1 Stage 1c acceptance | 2026-06-13 | gate script | Largest-lake-body guard: A1–A8 GREEN? | A1–A8 all GREEN. Guard fires at wK=0.85 under LARGE_BODY_CEILING=0.08; does NOT fire at wK=0.80. | `outputs/phase1_stage1c/acceptance_and_artifacts.py` |
| Stage 1c waterK sweep (ARTIFACT 1) | 2026-06-13 | sweep | Largest-body distribution vs waterK; ceiling sensitivity | Guard fires wK=0.85 (seeds 42, 7 first). Ceiling 0.08 confirmed conservative (well below any wK≤0.80 world). | `outputs/phase1_stage1c/` |
| Mountain ceiling coarse search | 2026-06-13 | sweep | What is the structural mtn_ceiling? | mtn_ceiling = 0.317; held across 7 seeds (mean≈0.225). Structural property of joint mtn condition. | `outputs/phase1_stage1/` (A8 sweep) |
| Docs lint pass | 2026-06-13 | REPORT-ONLY | Consistency across 12 authoritative docs: 5 check types | 15 findings; 5 C-type categories. No docs modified. | `outputs/docs_lint_20260613/lint_report.md` |
| Consolidated Reconciliation directive | 2026-06-13 | maintenance | Config default reconciliation, guard finalization, param triage, single-home consolidation | Tasks 1–11 complete. 5 C2-1 defaults reconciled; LOCKED guard added; terrain §12; PROVISIONAL marks; §STAGE-RECAL stub. See triage table. | `outputs/docs_lint_20260613/triage_table.md` |
| Blueprint A Gate A-1 | 2026-06-14 | gate run | Do C agents survive 500 steps on terrain kcal with burn=75k/step, reserve_full=100k, forage-only (3 seeds)? | **PASS — all 4 rails GREEN.** pop 240–243 (RAIL 1); max=250 (RAIL 2); no alive-below-floor (RAIL 3a); max_mean_res=100,000 (RAIL 3b). 430 tests passing. | `outputs/phase1_blueprintA_gate/gate_a1_results.json` |
| A-3 First-Light Shakedown | 2026-06-18 | exploratory run (not a gate) | C on Phase-1 terrain: what carrying capacity does the rivalrous CC-1 economy discover, and is the demography healthy? | **Food-capacity ceiling ~133.4k, placement-independent** (2 placements, spread ~0.06%; onset ~173; rails clean). But **equilibrium is demographically FROZEN (births=deaths=0)** — model lacks baseline mortality (RESULTS R-2). Number PROVISIONAL — superseded by demographic stage. | `outputs/phase1_a3_firstlight/partial_finals.json` (runs 1–2) + `run_a3.py`; narrative `handoffs/SiC_Games_Progress_Report_2026-06-18.md` |
| Demographic-stage blueprint (Siler+IBI) | 2026-06-18 | blueprint (DRAFT, red-teamed) | Smallest lit-anchored mechanic set to turn the frozen equilibrium into balanced birth–death turnover reproducing the Aché life table | DRAFT v2 — Siler mortality + disease channels (flagged) + IBI reproduction + staggered ages; two-step Aché-gated staging. Independent red-team done (verdict: 1 revision pass before lock). | `blueprints/phase1/SiC_Games_P1_Demography_Siler_Blueprint.md` |
| Demography Step-1 — Aché calibration | 2026-06-18 | calibration run (non-spatial) | Does Siler+IBI fix the frozen equilibrium and reproduce the Aché? | **YES.** Turnover restored (CBR 61/CDR 27, births≈deaths>0); fixed Aché Siler reproduces life table (e₀=36.5, e₁₅=38.3, mode=71); IBI=37.0/TFR=7.9; r=+3.3%/yr (Aché growth; r≈0 is Step-2). 439 tests pass. (RESULTS R-3) | `outputs/phase1_demography_calib/report.html` + `results.json`; core `src/sic_games/demography.py` |
| Demography Step-2 2a-pre — stability test | 2026-06-18 | stability run (spatial, sub-window) | Does the +3.3%/yr population settle against the food wall, or overshoot/oscillate/collapse (red-team B-1)? | **BOUNDED SETTLING** (3 seeds): plateau ~95% of food ceiling, settled-peak 1.01×, no overshoot/extinction. B-1 RESOLVED — food's ~1-step brake stabilizes; modulators not load-bearing for stability. (RESULTS R-4) | `outputs/phase1_demography_step2/report.html` + `results.json` |
| Step-2 2b/2c modulators + diagnostic | 2026-06-19 | ablation + diagnostic | Why do the a2 modulators produce dramatic CC collapse / reserve pinning? | **READ-TIMING BUG**, not dynamics: synergy read post-burn reserve (25k for any fed agent). FIXED → post-harvest read. On the constant economy all modulators INERT (agents fed + spread). (RESULTS R-5) | `outputs/phase1_demography_step2/` |
| A.1 seasonality | 2026-06-19 | resource-ecology run | Does a lean season make the modulators bite at equilibrium? | **INERT** — seasonality regulates CC to the lean-season bottleneck (95%→37%) but everyone stays fed (reserves full, synergy ~1). (RESULTS R-6) | `outputs/phase1_resource_ecology/report_2d.html` |
| A.2 depletion (GD-1) | 2026-06-19 | resource-ecology run | Does depletion create per-agent scarcity? | **INERT** — lowers CC further (cells stripped to f=0.32) but 0% under-fed; the IFD washes out per-agent variance. (RESULTS R-7) | `report_2e.html` |
| B movement constraint | 2026-06-19 | sweep | Does breaking the IFD (move-cost) create variance? | Clean mobility knob (moves/yr 0.93→0.15) but **0% under-fed**; spatial trapping ruled out. Model UNDER-mobile vs Binford. (RESULTS R-8) | `report_2f.html` |
| C.1 / C.2a childhood deficit + per-class reserves | 2026-06-20 | runs | Does the η/consumption deficit + body-sized reserve bite? | C.1 deficit masked by adult-sized neonatal reserve; **C.2a body-sized reserve → extinction without provisioning** (deficit real). (RESULTS R-9) | `report_2g.html`, `report_2h.html` |
| C.2b provisioning (+ seasonal) | 2026-06-20 | runs | Does mother-linked provisioning rescue + create the lean dependent class? | Provisioning **rescues** (0→~5000); over-smooths on constant economy; **seasonality+provisioning → seasonal child mortality** (68× lean-trough pulse) — but via the floor, not graded synergy. (RESULTS R-10) | `report_2i.html`, `report_2j.html` |
| S0 condition / S1 shortfall-sharing | 2026-06-20 | runs + sub-agent red-team | Can a lagged condition signal + child-priority route the squeeze to graded disease? | **CORRECT-BUT-INERT** (provisioning tops children to cap); fine channel = over-engineering for total-mortality; per-agent variance is the wrong level (R-14). S1 KEPT, S0 banked. (RESULTS R-11) | `report_2k.html`, `report_2l.html` |
| Biome-Mortality S2/S3.5/S4 — multi-biome | 2026-06-20 | multi-biome sweep (period life tables) | Total q(x) by biome; does the pathogen channel produce a gradient? | Pathogen channel WORKS (lush e₀ 43.8→32.1, pop 11936→1955) BUT biome mortality is **food-starvation-dominated + over-strong** vs data (R-5…R-13 acute margin at biome scale). (RESULTS R-12) | `outputs/phase1_biome_mortality/report_2m.html` |
| Density-disease regulation test | 2026-06-20 | δ-sweep | Can density-disease regulate r→0 below the food ceiling (tame starvation)? | **YES** — δ≥4 holds pop below the ceiling, **starvation 49%→0%** → disease-regulated (realistic). Bites because agents are confined to the finite patch. (RESULTS R-13) | `outputs/phase1_biome_mortality/report_2n.html` |
| Scale / architecture resolution | 2026-06-20 | design decision (no run) | Agents vs density? Why are the modulators "inert"? | Per-agent variance is non-physical (band-level); operative variance is inter-band; individuality lives in the Cred sharing-rule (Si=0 / C=Cred-weighted). Keep agents + band-ecology; fallbacks deferred. (RESULTS R-14) | RESULTS R-14 + MODEL_SPEC §4.7 |

---

### Carbon status → emergent bands → full social stack (R-18…R-27; all under `outputs/phase1_biome_mortality/`)
| Artifact | Date | Type | Question | Headline | Location |
|---|---|---|---|---|---|
| Carbon Tier-1 statval | 2026-06-21 | multi-seed statval | Does the Cred sharing-rule create a compositional survival gradient? | R-18: κ>0 + meat variance → starvation kills low-cred (death-deficit>0); eq_pop κ-invariant. | `run_3b_carbon_statval.py` + `results_3b.json` |
| Cred-vector B+ statval | 2026-06-21 | calibration | status→RS r≈0.19? homeostat? N_e? | R-19: m≈4 (IFD) → status→RS 0.19; homeostat bounded; N_e healthy. | `run_3c_bplus_statval.py` + `results_3c.json` |
| B++ assortment | 2026-06-21 | paired control | does assortment consolidate dynasties? | R-20: NO — homogamy spreads RS, doesn't skew it (counterintuitive). | `run_3e_bpp_assortment.py` |
| **E.3-proper** | 2026-06-29 | recalibration + ablation | m for status→RS 0.19 on bands; does lumping collapse it? | R-21: **m=5 → +0.190**; lumping revised (R-18 mortality-selection is load-bearing, not the RS skew). | `run_3g_e3_proper.py` + `results_3g.json` |
| Tether retirement | 2026-06-29 | comparison | does the morph fire without the storage tether? | R-23: YES — emergent bands reach packing; tether deleted. | `run_3h_tether_retirement.py` |
| F.2 risk-mortality proto | 2026-06-29 | sweep | does risk-as-mortality yield an optimal band size? | R-24: NO — death spiral; SHELVED. | `run_3i_band_risk_proto.py` |
| Band life-cycle | 2026-06-29 | diagnostic | merge/split/collapse + size distribution | R-24: balanced fluid equilibrium; ~30% in durable bands (persistence filter). | `run_3j_band_lifecycle.py` |
| Band affiliation (F.3c-1) | 2026-06-29 | validation | ~25 non-kin band entity? | R-25: agent-wt 28.7/median 25.3; dominant-lineage 0.38 (non-kin). | `run_3k_band_affiliation.py` |
| Dynamic bands + assabiyah (F.3c-3) | 2026-06-29 | validation | does assabiyah make band size condition-dependent? | R-25: corr(assabiyah,size)=+0.27; eq_pop preserved. | `run_3l_dynamic_bands.py` |
| **Full-stack integration** | 2026-06-29 | integration gate | does the whole social stack cohere + keep its results? | R-26: coheres; status→RS **≈0.13** (monogamy-appropriate); R-18 intact. | `run_3m_fullstack.py` |
| Climate integration (Stage 0) | 2026-06-29 | integration | does the social stack run on a varying (ClimateField) world? | R-27: coheres but TROUGH-LIMITED (eq_pop −27%…4× crash); social response needs a controlled driver. | `run_3o_climate_social.py` |
| **Controlled-climate harness** (SE Stage 0) | 2026-06-30 | benchmark tool | can a deterministic driver isolate the climate-attributable social response? | R-28: YES — FLAT vs PULSE diff-in-diff, ΔPRE=−0.00 placebo, −70 pop footprint / −135 lagged scar; reusable `run_controlled`. | `outputs/phase1_social_evolution/run_se0_controlled_climate.py` |
| **Leader coherence + size repulsion** (SE Stage 1) | 2026-07-01 | mechanism + cohort event study | does the band-size cohesion↔dispersion balance work; does leader-death fission a band? | R-29: repulsion BINDS (max band 44→31) + fixes assabiyah saturation. R-30: leader-death→fission a principled NULL in the complex regime (Δ≈−0.02..−0.25) → deferred to dynastic stage. | `outputs/phase1_social_evolution/run_se1_leader_coherence.py` |

### Blueprints commissioned this arc (specs, not results)
`…_Climate_OrbitalLottery_Scoping`, `…_Storage_Morph_Scoping`, `…_EmergentBands_Scoping`,
`…_F3c_PerBandSociety_Scoping`, `…_SocialEvolution_Dynamic_Scoping` (all `blueprints/phase1/`).

---

*End of ARTIFACTS — seeded 2026-05-29; reorg reconciliation 2026-06-05; MODEL_SPEC split 2026-06-06; Phase 1 artifacts 2026-06-13; Blueprint A gate 2026-06-14; resource-ecology + biome-mortality + scale-resolution arc (R-5…R-14) 2026-06-20; Carbon → emergent bands → full social stack (R-18…R-27) 2026-06-29.*
