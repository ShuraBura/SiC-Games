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
| Stage 5.2 report (Cultural Dynamics) | 2026-05-29 | run report | Do c2 defection, Deffuant, and the σ_inherit sweep behave as designed? | Cultural layer stable; c2 defection rare (3.7%) and **uncorrelated with c2** (no selection differential); Deffuant homogenises ψ as designed; **σ*=0.10 selection was mis-gated on ψ — RETIRED** (see DEAD_ENDS, MODEL_SPEC §5.1-D). | `[CHAT-ONLY]` report.html — confirm repo location |
| Perf Audit + Optimisation report | 2026-05-28 | benchmark + audit | Step-time breakdown; scaling exponents; feasible grid/N for LHS | LOW-risk fixes applied, **science unchanged to 1e-9**; **N exponent 1.05** (≈linear), **grid exponent 2.957** (near-cubic, target ≤2.0); B0(50²,250)=13 ms/step, B2(100²,1000)=110 ms/step, B4(150²,2000)=410 ms/step; LHS feasible to N=2000/150² as weekend batch. MED/HIGH-risk items deferred (§6 backlog). | `[CHAT-ONLY]` report_perf_audit.html — confirm repo location |

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

*End of ARTIFACTS — seeded 2026-05-29, incomplete, awaiting Code reconciliation.*
