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

## Key established numbers (quick reference — full context in the reports above)

| Quantity | Value | Source artifact |
|---|---|---|
| Stage 1 substrate | Gini=0.47, N=250, peaks=63%, seed=42 | (ROADMAP status) |
| N-runtime exponent (post-audit) | 1.053 | Perf Audit 2026-05-28 |
| grid-runtime exponent (post-audit) | 2.957 | Perf Audit 2026-05-28 |
| ms/step B2 (100×100, N=1000) | 110.2 | Perf Audit 2026-05-28 |
| ms/step B4 (150×150, N=2000) | 409.7 | Perf Audit 2026-05-28 |
| Si extinction (A=0.75/T=200) | both seeds, by t≈1500 | Stage 5.1 (confirm artifact) |
| c2 defection rate (steady state) | 0.0374, defector-c2 ≈ cooperator-c2 | Stage 5.2 report |
| test count (Stage 5.2) | 233 passed | Stage 5.2 report |

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

*End of ARTIFACTS — seeded 2026-05-29; reorg reconciliation 2026-06-05; MODEL_SPEC split 2026-06-06.*
