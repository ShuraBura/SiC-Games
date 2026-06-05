# SiC Games — Documentation Index

**This is the entry point.** It does not contain project facts; it routes you to the document that does. Every kind of fact has exactly one authoritative home. If you find the same fact in two documents, one is wrong — the authoritative home wins and the copy is a bug to be replaced with a pointer.

**Last updated:** 2026-05-29.

---

## The routing rule

| If your question is about… | Go to | The "home" owns |
|---|---|---|
| Where am I, what's next, what's been tried/deferred | **ROADMAP.md** | Stage sequence, status, pending/deferred items, open questions (Q-list), architecture hooks |
| What *is* this construct / how does this mechanism work | **MODEL_SPEC.md** | Definitions, ranges, inheritance channels, mechanism logic, the three-way C/Si classification, design-decisions log, architecture seams |
| What is parameter X, its value, when it was locked, its sweep history | **PARAMETERS.md** | The authoritative value + lock/sweep/retire history of every parameter |
| What did we predict (before seeing data), and how did it resolve | **HYPOTHESES.md** | Pre-registrations and their resolution status |
| What do we actually *know* (established findings) | **RESULTS.md** | Headline findings ledger, in prose |
| Where is the run/report/benchmark that showed X | **ARTIFACTS.md** | Index of every report/benchmark/diagnostic + its location + headline |
| What grounds this mechanic in the literature | **LITERATURE.md** | Citations: what was lifted, what rejected, why |
| Did we try X already, and why was it abandoned | **DEAD_ENDS.md** | Retired directions + the reason each was retired |

---

## Authoritative-home discipline (read before editing any doc)

1. **One fact, one home.** A parameter's value lives in PARAMETERS.md. ROADMAP, MODEL_SPEC, and blueprints *reference* it; they do not restate it. When a value changes, it changes in one place.
2. **Pointers, not copies.** If document B needs a fact owned by document A, B writes "see A" — not the fact itself. Copies drift; pointers don't.
3. **Update triggers are enforced in CLAUDE.md.** Each document below has an update trigger. Those triggers are encoded as report-standards in CLAUDE.md so the coding agent maintains them. A document with no enforced trigger will rot — if you add a document, add its trigger to CLAUDE.md in the same change.
4. **Append, don't rewrite, the logs.** HYPOTHESES, RESULTS, DEAD_ENDS, and the MODEL_SPEC decisions-log are append-only ledgers. Supersede entries with a dated strike-through + note; never silently delete, or you lose the record of what was believed when.
5. **Macro to micro.** ROADMAP is the macro view (where the project is going). MODEL_SPEC is the micro view (what every piece is). The other docs are the connective tissue (why, what was learned, where it lives, what was grounded, what failed).

---

## Document registry

| Document | Status | Maintainer | Update trigger |
|---|---|---|---|
| INDEX.md | live | supervisor + Code | when a document is added or retired |
| ROADMAP.md | live | Code (end of stage) | end of every stage / directive |
| MODEL_SPEC.md | **pilot (v0.1)** — trait/inheritance/reproduction cluster only | Code + supervisor | construct introduced or redefined; lock-status change |
| PARAMETERS.md | **pending extraction** | Code | any parameter lock, sweep, or retirement |
| HYPOTHESES.md | live (seeded) | supervisor | before any analysis that could HARK; on resolution |
| RESULTS.md | **pending backfill** | Code | when a finding is established |
| ARTIFACTS.md | live (seeded) | Code | when any report/benchmark/diagnostic is emitted |
| LITERATURE.md | live (thin — Si Cred only) | Code + supervisor | when a source is consulted |
| DEAD_ENDS.md | **pending backfill** | Code + supervisor | when an approach is retired |

---

## Build order (proposed)

Three docs are seeded now (this file, HYPOTHESES, ARTIFACTS) because their content exists and needs no further decisions. The remaining four require an extraction or backfill pass:

1. **PARAMETERS.md** — extract from ROADMAP's locked-param table + every blueprint's parameter blocks; make it authoritative; replace ROADMAP's table with a pointer. Mechanical, low-risk.
2. **MODEL_SPEC.md full extraction** — extend the pilot across all stages per the pilot's §7 ordering. Largest single job.
3. **RESULTS.md backfill** — extract established findings from the stage reports (needs ARTIFACTS.md first, to know which reports exist).
4. **DEAD_ENDS.md backfill** — extract retired directions (σ*=0.10, r_cred_Si, the Stage-3.3 biparental-Si error, etc.) from blueprints, patches, and bug history.

Each needs a matching CLAUDE.md trigger added in the same change so it stays maintained.

*End of INDEX.*
