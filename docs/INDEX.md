# SiC Games — Documentation Index

**This is the entry point.** It does not contain project facts; it routes you to the document that does. Every kind of fact has exactly one authoritative home (the charter's **11 homes**). If you find the same fact in two documents, one is wrong — the authoritative home wins and the copy is a bug to be replaced with a pointer.

**Last updated:** 2026-06-08 (PARAMETERS.md extracted). All eleven homes live under `docs/`. Governance: `docs/DOCS_CHARTER.md`. Code lives under `sic_games/`; its master agent contract is `sic_games/CLAUDE.md`.

---

## The routing rule (the 11 homes)

| If your question is about… | Go to | The "home" owns |
|---|---|---|
| Where am I, what's next, what's been tried/deferred | **ROADMAP.md** | Stage sequence, status, pending/deferred items, open questions (Q-list) |
| The big-picture structure / seams / how the pieces fit | **ARCHITECTURE.md** | System decomposition, module seams, data flow, design-decisions log |
| How a specific mechanism *works* (the rule/equation) | **MECHANISMS.md** | Per-construct definitions, ranges, inheritance channels, mechanism logic, C/Si classification |
| What is parameter X, its value, when it was locked, sweep history | **PARAMETERS.md** | The authoritative value + lock/sweep/retire history of every parameter |
| What we *aspire* to show (no falsification spec yet) | **TARGETS.md** | Aspirations; each graduates to HYPOTHESES when it gets a test spec |
| What did we predict (before seeing data), and how did it resolve | **HYPOTHESES.md** | Pre-registrations + resolution status (falsifiable, test-specced) |
| What do we actually *know* (established findings) | **RESULTS.md** | Headline findings ledger, in prose |
| Where is the run/report/benchmark that showed X | **ARTIFACTS.md** | Index of every report/benchmark/diagnostic + location + headline |
| What grounds this mechanic in the literature | **LITERATURE.md** | Citations: what was lifted, what rejected, why |
| Did we try X already, and why was it abandoned | **DEAD_ENDS.md** | Retired directions + the reason each was retired |
| Which document owns this kind of fact | **INDEX.md** (this file) | The routing table itself |

> **§6 status (2026-06-08):** the MODEL_SPEC split is **done** — ARCHITECTURE.md and MECHANISMS.md now exist as separate homes (see ARCHITECTURE §12.1-F; the original MODEL_SPEC v0.2 is archived at `archive/superseded/`). **PARAMETERS.md is now live** (extracted 2026-06-08) — route all parameter-value questions to **`docs/PARAMETERS.md`**. The interim locked-param tables in ROADMAP.md and CLAUDE.md have been replaced with pointers.

---

## Authoritative-home discipline (read before editing any doc)

1. **One fact, one home.** A parameter's value lives in PARAMETERS.md (interim: CLAUDE.md table). ROADMAP, MECHANISMS, and blueprints *reference* it; they do not restate it.
2. **Pointers, not copies.** If document B needs a fact owned by document A, B writes "see A" — not the fact itself. Copies drift; pointers don't.
3. **Update triggers are enforced in CLAUDE.md.** Each home has an update trigger, mirrored as a pointer-trigger in `sic_games/CLAUDE.md` so the coding agent maintains it. Add a doc → add its trigger in the same change.
4. **Append, don't rewrite, the logs.** HYPOTHESES, RESULTS, DEAD_ENDS, TARGETS, and the ARCHITECTURE decisions-log (§12) are append-only. Supersede with a dated note; never silently delete.
5. **Macro to micro.** ROADMAP = where the project is going; ARCHITECTURE/MECHANISMS = what every piece is. The rest is connective tissue (why, what was learned, where it lives, what was grounded, what failed).

---

## Document registry

| Home | Status | Maintainer | Update trigger |
|---|---|---|---|
| INDEX.md | live | supervisor + Code | a document is added or retired |
| ROADMAP.md | live | Code (end of stage) | end of every stage / directive |
| ARCHITECTURE.md | live (§0 principle, §9 world substrate, §12 decision-log, §13 seams, §15 gaps) | Code + supervisor | a seam/decomposition/world-substrate change; a design decision is taken |
| MECHANISMS.md | live (§0–§8, §10–§11 construct registry, §14 param index) | Code + supervisor | construct introduced or redefined; lock-status change |
| PARAMETERS.md | **live** (extracted 2026-06-08; supersedes CLAUDE.md + ROADMAP.md interim tables) | Code | any parameter lock, sweep, or retirement |
| TARGETS.md | live (T-1, T-2, T-3) | supervisor + Code | an aspiration is added or graduates to HYPOTHESES |
| HYPOTHESES.md | live (H-EMERGE-1, H-SUBSTRATE-6.0a, H_cc) | supervisor + Code | before any analysis that could HARK; on resolution |
| RESULTS.md | live (R-1) | Code | when a finding is established |
| ARTIFACTS.md | live | Code | when any report/benchmark/diagnostic is emitted |
| LITERATURE.md | live (full bibliography + Si-Cred synthesis) | Code + supervisor | when a source is consulted |
| DEAD_ENDS.md | live (DE-1) | Code + supervisor | when an approach is retired |

*Also under `docs/`:* **DOCS_CHARTER.md** (the governance document this index implements). The former MODEL_SPEC.md was split into ARCHITECTURE + MECHANISMS on 2026-06-06 and archived.

**Stage 7 terrain routing (added 2026-06-10):**
| Question | Home |
|---|---|
| Terrain pipeline locked spec (knobs, waterLevel formula, biome ladder, relief envelope, cell size) | **ARCHITECTURE.md §9.5** |
| Terrain generator `generate_world` / `characterize_map` constructs | **MECHANISMS.md** (future §9 stub) |
| Oracle battery, equivalence/acceptance gate results, biome map artifacts | **ARTIFACTS.md** |
| Morin 2024 (CDH), J&H 2014 (forest hunting), forest-savanna mosaic sources | **LITERATURE.md** (Stage 7 section) |
| Game-field openness inertia pre-registered finding; Stage 7.2 scope | **ARCHITECTURE.md §9.5 PROVISIONAL note** + Stage 7 blueprint §12 |
| Forest/savanna bistability watch-item | **ARCHITECTURE.md §15.6** |

---

## Map of the repo (post-reorg, 2026-06-05)

```
SiC-Games/
├── README.md            one-screen orientation → points here
├── docs/                the 11 homes (+ DOCS_CHARTER)  ← you are here
├── blueprints/          supervisor directives, by stage (stage1…stage6, owe, perf, meta, resource-ecology)
├── handoffs/            session/standing handoffs + project instructions
├── origin/              the founding spec (Carbon-Prototype V1.3, canonical .md)
├── sic_games/           the model code (untouched) + CLAUDE.md (master agent contract)
└── archive/             superseded docs, .bak litter, prior code snapshots (never hard-deleted)
```

*End of INDEX.*
