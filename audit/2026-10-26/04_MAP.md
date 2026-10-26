# 04 — MAP: code, configuration, data, results, references, tests, tools, documents (2026-10-26)

Paths are relative to the repository root. For a single mechanism, use the generated **`MAP_mechanisms_to_code.md`**
(flag → definition → read sites → tests → RESULTS entries). For a single parameter or flag value, use
**`docs/REGISTRY.md`** (generated).

---

## 1. Code — the canonical model (`sic_games/src/sic_games/`)

| module | lines | role |
|---|---|---|
| `phase1_model.py` | 6.1k | **`TerrainWorld`**, the Mesa model. Step order: movement (IFD diffusion + residence pin + releases) → harvest and sharing (forage, meat, caps, storage and the village granary, provisioning tiers) → metabolism, mortality (`_a2_mult`: risk × density × synergy on the Siler a2; starvation floor; orphan hazard) and fertility → settlements (founding, budding, abandonment) → bands, mating, lineages, elite layer → diagnostics (`life_table`, `spatial_health` inputs, per-factor observers) |
| `demography.py` | 2.6k | **`DemographyConfig`**: almost every flag and parameter, each with its provenance comment. Siler schedules (`ACHE_FOREST`, `ACHE_FOREST_NATURAL` = canon), hazard modulators (`risk_mult`, `density_mult`, `pathogen_mult`, `synergy_mult`), `DEMOG_ANCHORS` + `demography_health()` (the monitor), `spatial_health()` |
| `substrate.py` | 0.3k | harvest shares (`compute_harvest_shares`), the IFD movement choice (`diffusion_select_target`, incl. the store anchor), `base_status` |
| `terrain.py`, `terrain_field.py` | 1.4k | world generation (Economy-from-Climate: temperature, precipitation, Miami NPP, Whittaker biome, rivers, aquatic food); `world_lottery_climate` |
| `climate.py`, `capacity.py` | 1.0k | climate fields and channels (`ClimateConfig`, health check); the NPP carrying-capacity harvest field (CC-1, Tallavaara) |
| `config.py`, `runconfig.py`, `runspec.py` | 0.8k | config classes (`SubstrateConfig`, `CarbonConfig`, `KcalEconomyConfig`); loading `config/*.toml`; "a run is a file" |
| `invariants.py`, `genome.py`, `group.py`, `agents/` | 0.6k | snapshot consistency checks (R-91); neutral-marker genome; the group vector; agent base class, costs, perception, reproduction rules |
| `stage*.py`, `soa*.py`, `oracle.py`, `parity.py`, `benchmark*.py`, `owe1*.py`, `perf_audit.py`, `sweep.py`, `fc_sweep.py`, `beta_sweep.py`, `world*.py`, `joint_task.py`, `support_pool.py`, `metrics.py`, `report.py`, `visualize.py`, `main.py`, `run.py`, `batch.py`, `r0_confound.py`, `runtime_monitor.py` | — | **Phase-0 (C/Si, Sugarscape) code and its tooling.** Kept for history and its own tests; NOT on the canonical path |

## 2. Harnesses (`sic_games/outputs/`)

| path | role |
|---|---|
| `substrate_run/run_campaign.py` | **THE canonical campaign.** Reads `--config` or `C_*` env; `C_ALLON=1` = the canonical stack; `_skip` = the held flags with reasons; writes `campaign_trajectory_<tag>.json` (rows every `C_LOGEVERY` steps + `meta` incl. life-table counters), `campaign_spatial_*`, `campaign_progress_*` |
| `phase1_social_evolution/run_se0_controlled_climate.py` | the canon BUILDERS: `realistic_forager_demog()`, `emergent_village_demog()` (canon base incl. `paternal_provision_frac=0.5`) |
| `mechanism_battery/battery1_liveness.py` | a small fast world used by many tests. **Not canon:** builds from `emergent_village_demog()` and does not apply the run file |
| `phase1_biome_mortality/audit_flag_invariants.py` | the charter TYPE table and PREREQ chains for every flag; the differential flag audit |
| `substrate_run/plot_spatial.py` | the worked example of the mandatory map figure (terrain, people, settlements) |
| other folders | outputs and harnesses of earlier stages (Phase 0 and Phase 1 arcs); see `docs/ARTIFACTS.md` |

## 3. Configuration

| file | content |
|---|---|
| `config/runs/full_campaign.toml` | **what a canonical run executes**: `[run]`, every `[mechanisms]` flag, every `[parameters]` value |
| `config/mechanisms.toml`, `config/parameters.toml` | generated from the code by `tools/gen_runconfig.py`, with provenance comments (beware: a field without its own comment inherits a neighbour's block — use REGISTRY or the source) |
| `config/runs/*.toml` | other run files; `ctb_*.toml` are test fixtures (git-ignored) |

## 4. Data and outputs

| what | where | in git? |
|---|---|---|
| canonical campaign trajectories (incl. the Stage-2 sets of Add.106–113) | `sic_games/outputs/substrate_run/campaign_trajectory_*.json` | **no** (git-ignored by design); regenerate — `05_HOW_TO_RUN_AND_VERIFY.md` |
| compact evidence of the current and previous canon | `docs/evidence/scorecard_add113_canon.{json,png}`, `scorecard_add109_canon.json` | yes |
| benchmark history across five canons | `audit/2026-10-26/evidence/benchmark_history.{json,md}` | yes |
| documentation audit before/after | `docs/evidence/doc_audit_2026-10-26_{before,after}.txt` | yes |
| probe outputs of Add.105–110 (~112 MB JSON) and run logs | `scratchpad/*.json`, `scratchpad/*.log` | **no**; regenerate with the probe's `*_run.py` |
| small data arrays of the recent arcs | `scratchpad/*.npz`, `scratchpad/malthus_ratios.jsonl` | yes |
| archived Phase-0 outputs and superseded docs | `archive/` | partly |

## 5. Results — the ledger and its arcs

`docs/RESULTS.md` (append-only, ~10k lines) — navigate with **`docs/RESULTS_INDEX.md`** (generated: line, entry,
status words, heading). Arcs (line numbers in RESULTS.md):

| lines | entries | arc |
|---|---|---|
| 9 | R-1 | Phase 0: C vs Si on Sugarscape (historical) |
| 25–235 | R-2 … R-17 | the demographic core: Siler, fertility, density dependence, seasonality, the e0 calibration |
| 236–329 | R-18 … R-26 | Carbon status hierarchy, families, bands, band society, assabiyah |
| 330–543 | R-27 … R-48 | climate integration, leaders, malnutrition fission, mate choice, CC-1 carrying capacity, life history, co-movement, the biome → society morph |
| 544–565 | R-49 … R-51 | Economy-from-Climate (EFC) world generation; GD-1 finite resources |
| 566–1266 | R-52 … R-71 | settlements → villages → the settlement hierarchy; the deep-time campaign; connubium; budding; agriculture; abandonment |
| 1267–1746 | R-72 … R-81 | band size rebuilt; game variance; orphan mortality; the demographic dashboard; polygyny; divorce; status→RS; the cred homeostat |
| 1747–2847 | R-82 … R-98 | the ELITE layer: material wealth, leader rights, succession, legitimacy (R-86), delegitimation and cycles (R-87, R-87d), lineages, relative legitimacy, resentment, rank (R-96, R-98); R-97 "the elite layer works and still does not cycle" |
| 2848–6326 | R-106 + Addenda 1–41 | "nothing in this model can be hungry": config/reachability audits, climate wiring, CTB adoption, the benchmark ladder, game and energetics fixes (Addenda 1–41 have no headings) |
| 6327–7074 | Add.42–51 | fertility brake, the demography monitor, Malthus, refractory, crowding |
| 7075–7585 | Add.52–63 | the settlement mesh, colonization, the settlement pair (Add.61), the relational stratification criterion (Add.62) |
| 7586–8325 | Add.64–81 | e0 and hunger, density fertility, sedentism, the preventive check (negative), emigration, band provisioning, the packing paradox, age structure |
| 8326–8740 | Add.82–92 | material Gini (#14): graded levelers, adoption, the marker audit correction |
| 8741–9316 | Add.93–104 | the marker audit: #17, #3, #12–13, #11 (wrong channel), Add.100 the definitive full-length scorecard, montane |
| 9317–9889 | Add.105–113 | Malthus churn; the density-fill radius; starvation causes; food-viable sites; fathers; the granary access gap; the risk-term defect; the adopted pair |
| 9890–9958 | Add.114 | the audit preparation: full re-score, adoption side effects, documentation audit |
| 9959– | Add.115 | the benchmark history across five canons (fertility traded for survival; m(5–15) never in band); this audit package |

**Retired or refuted findings:** `docs/DEAD_ENDS.md` (DE-1 … DE-23; DE-23 indexes the R-106 dead ends, including
Add.79's refuted "adaptive equilibrium" and Add.80's retracted "packing limit").

**Instruments and figures of the recent arcs:** `scratchpad/bp_<arc>_*.py` and `scratchpad/bp_*.png`, mapped by arc
in `docs/ARTIFACTS.md` (last section). Each RESULTS addendum names its own instruments at its end.

## 6. References and literature

| what | where |
|---|---|
| every citation, what was lifted from it, and its status tag | `docs/LITERATURE.md` (~210 kB) |
| constants verified against an exact source location, with dates | `docs/VERIFICATION_LOG.md` |
| the registered anchors (32 rows), checked against the PDF text | `tools/verify_anchor.py --list` |
| the source PDFs | `literature/` — 54 of 133 in git; **12 of the 15 registered-anchor PDFs are NOT in the public repo** (copyright); they are on the supervisor's machine (local branch only) |
| literature values behind the resource layer | `docs/MODEL_SPEC.md` §4.1, `docs/SiC_Games_Resource_Return_Rate_Table.md` |
| the forager life-table anchors (#18–#21) | `docs/LITERATURE.md` Gurven & Kaplan 2007 entry (Table 2, all hunter-gatherer rows) |

## 7. Tests (`sic_games/tests/`, 155 files, ~1,780 tests)

| area | test files (prefix `test_`) |
|---|---|
| constructed-truth benchmarks of the ladder tiers | `tier2_energetics_ctb`, `tier3_agesex_ctb`, `tier3_demography_ctb`, `tier4_movement_ctb`, `tier5_bands_ctb`, `tier6_family_ctb`, `benchmark_ladder`, `canonical_worlds_ctb` |
| instruments (CTB of the diagnostics) | `demography_health_ctb`, `demography_panel_ctb`, `spatial_health_ctb`, `marker_diagnostics_ctb`, `realised_demography_ctb`, `climate_health_ctb`, `diagnostics_ground_truth`, `settlement_ground_truth`, `lineage_ground_truth`, `density_ground_truth`, `invariants` |
| configuration, canon and provenance | `campaign_knobs`, `config*`, `runconfig_sync`, `runspec_ctb`, `registry_sync`, `mechanism_audit_coverage`, `mechanism_reachability`, `on_but_dead_gate`, `provenance_coverage`, `anchor_provenance`, `retraction_propagation` |
| pinned known defects (designed to fail when the fact changes) | `cohesion_headroom`, `risk_accident_share` (the whole-a2 defect), `pressure_mobility` (pinned world) |
| mechanisms (one file per mechanism or group) | the remaining `*_ctb` and named files, e.g. `supply_gap_repairs`, `colonizing_budding_ctb`, `village_density_disease_ctb`, `storage*`, `legitimacy`, `lineage_*`, `orphan_mortality`, … — see `MAP_mechanisms_to_code.md` for the tests of each flag |
| Phase 0 | `si_*`, `soa*`, `joint_task`, `support_pool`, `deffuant`, `dormancy`, `growback`, `world`, `parity`, `mode_switch`, `seasonal_oscillation`, … |

## 8. Tools (`tools/`)

| tool | does |
|---|---|
| `doc_audit.py` | documentation ↔ code/config consistency (paths, PARAMETERS vs run file, undocumented flags, freshness) |
| `gen_registry.py` | writes `docs/REGISTRY.md` and `docs/RESULTS_INDEX.md` (a sync test keeps them current) |
| `scorecard.py`, `scorecard_fig.py` | score any set of campaign trajectories against every marker; plot it |
| `benchmark_history.py` | the benchmark history across canon snapshots (this package's `evidence/`) |
| `gen_code_map.py` | this package's `MAP_mechanisms_to_code.md` |
| `verify_anchor.py` | show the quoted source text behind each registered anchor |
| `gen_runconfig.py`, `make_runconfig.py`, `audit_provenance.py` | generate `config/*.toml`; author a run file; provenance audit |

## 9. Documents (`docs/` and the root)

| document | owns | state |
|---|---|---|
| `docs/INDEX.md` | the routing table (one home per kind of fact) | updated 2026-10-26 |
| root `CLAUDE.md` | the working rules and methodology (CTB, build-it-on, the visual rule, the spatial check, the demography panel) | current — read it |
| `docs/MARKER_MATRIX.md` | markers, bands, units, binding rules 1–5; CURRENT SCORECARD at the top | current |
| `docs/BENCHMARK_LADDER.md` | the 12-tier validation order and tier membership | current |
| `docs/MECHANISM_CHARTER.md` | operator types and the diagnostic/propagation disciplines | binding; 2026-08-07 |
| `docs/RESULTS.md` · `docs/RESULTS_INDEX.md` | findings (append-only) · its index | current |
| `docs/PARAMETERS.md` · `docs/REGISTRY.md` | grounding/history of 81 parameters · all flags and parameters (generated) | rows agree with canon |
| `docs/MODEL_SPEC.md`, `docs/MECHANISMS.md`, `docs/ARCHITECTURE.md` | mechanism specifications; construct definitions; architecture | last full edits Sept 5 / Aug 10 / Jul 8; dated notes added |
| `docs/LITERATURE.md`, `docs/VERIFICATION_LOG.md` | citations; verified constants | current to Sept 24 |
| `docs/DEAD_ENDS.md`, `docs/HYPOTHESES.md`, `docs/TARGETS.md`, `docs/DEFERRED_MECHANICS.md` | retired directions; pre-registrations; aspirations; deferred mechanics | DE-23 added; statuses last set Jun–Aug (dated review notes); DEFERRED's DM-F section is stale |
| `docs/ROADMAP.md` | CURRENT STATUS (2026-10-26) + history of earlier stages | current section |
| `docs/ARTIFACTS.md` | index of reports, instruments, figures | R-106 map added |
| `docs/AUDIT_GUIDE.md`, `docs/MODEL_STATE.md` | stubs pointing into this package | — |
| STALE / HISTORICAL (bannered): `context/*`, `sic_games/CLAUDE.md`, `sic_games/BUGS.md`, root `SiC_Games_*.md`, `docs/HANDOFF_*` | — | kept for history |
