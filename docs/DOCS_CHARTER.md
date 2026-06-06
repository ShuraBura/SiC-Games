# SiC Games — Documentation Charter (DOCS_CHARTER.md)

**Status:** AUTHORITATIVE. This document governs the documentation system itself.
**Maintainer:** Supervisor authors/amends in chat; Claude Code (CC) enforces.
**Created:** 2026-06-05.

---

## 0. Why this document exists

The project has repeatedly produced **two homes for the same fact**, and they drift.
The realised failures: a second `HYPOTHESES.md` that diverged from the first (each held
a pre-registration the other lacked — `H-EMERGE-1` in one, the `H-ORTHOGONALITY /
H-instinct-debt / H_cc / H-SUBSTRATE-6.0a` block in the other); `LITERATURE.md` and
`CLAUDE.md` each existing in two or three folders at once; the τ_trickle / σ_inherit /
p_fission_Si parameter discrepancies (ARCHITECTURE §15 D1–D3) caused by values living in
both a doc and the ROADMAP table.

The cure is not "more documents." It is a fixed set of homes, each answering exactly one
question, with a rule that prevents a second home from being born. **This charter is that
rule.** It is the one document CC consults before creating, splitting, or merging any
other document.

---

## 1. The governing principles (binding on every doc)

1. **One fact, one home.** Every fact has exactly one authoritative document. If the same
   fact appears in two docs, one is a bug — the authoritative home wins, the copy is
   replaced with a pointer.
2. **Pointers, not copies.** If doc B needs a fact owned by doc A, B writes "see A §x" — it
   does not restate the fact. Copies drift; pointers cannot.
3. **The homes are a closed set.** The eleven homes in §2 are the complete list. **No new
   top-level document may be created without first amending §2 of this charter** (adding the
   home, its single question, and its update trigger). This is the clause that stops the
   next duplicate.
4. **Append, don't rewrite, the ledgers.** HYPOTHESES, RESULTS, DEAD_ENDS, and the
   MECHANISMS / ARCHITECTURE design-decision logs are append-only. Supersede an entry with a
   dated strike-through + note; never silently delete, or the record of what was believed
   when is lost.
5. **Every home has an enforced update trigger.** The trigger (§2, last column) is mirrored
   in `CLAUDE.md` as a report-standard so CC maintains it. A home with no enforced trigger
   rots. Add a home → add its trigger to CLAUDE.md in the same change.
6. **The test of the taxonomy:** for any question, exactly one home is the obvious place to
   look. If a question has two plausible homes, the boundary between them is wrong — fix the
   boundary here, do not let both answer.

---

## 2. The eleven homes (the closed set)

Each home answers ONE question. `docs/INDEX.md` is the router that points a question at its home.

| # | Home (in `docs/`) | The ONE question it answers | Update trigger |
|---|---|---|---|
| 1 | **INDEX.md** | "Which document answers my question?" | A home is added, split, merged, or retired (i.e. any §2 amendment). |
| 2 | **ROADMAP.md** | "Where is the project, what's next, what's deferred?" | End of every stage / directive. |
| 3 | **ARCHITECTURE.md** | "How does the world work — substrate, the step loop, how agents read the world and each other, the physical/social 'laws,' the architecture seams?" | A structural/infrastructure change or a new seam is introduced. |
| 4 | **MECHANISMS.md** | "How does *this specific* interaction work?" — the single mechanism registry (see §3). | A mechanism is introduced, redefined, or re-classified (C1/C2/C3). |
| 5 | **PARAMETERS.md** | "What is parameter X — value, range, status, grounding, lock/sweep history?" (see §4) | Any parameter lock, sweep, retirement, or status change. |
| 6 | **TARGETS.md** | "What emergent behaviour are we shooting for?" — qualitative target phenomenology, *not yet* a formal prediction (see §5). | A target is added, refined, or graduates to a HYPOTHESIS. |
| 7 | **HYPOTHESES.md** | "What did we predict *before looking*, and how did it resolve?" — pre-registered, falsifiable, dated. | Before any analysis that could HARK; on resolution. |
| 8 | **RESULTS.md** | "What do we actually *know* now?" — established findings, in prose. | When a finding is established. |
| 9 | **LITERATURE.md** | "What grounds this in the literature — what we took, what we rejected, why?" | When a source is consulted or a citation's tag changes. |
| 10 | **ARTIFACTS.md** | "Where is the run / report / benchmark that showed X?" — index + location + headline. | When any report, benchmark, or diagnostic is emitted. |
| 11 | **DEAD_ENDS.md** | "What did we try and abandon, and why?" | When an approach is retired. |

Plus this charter (`docs/DOCS_CHARTER.md`) and `CLAUDE.md` (coding-agent instructions +
the enforced triggers, single master at the **code root**, carrying pointers *into* `docs/`).

### 2.1 What changed from the pre-charter doc set
- `MODEL_SPEC.md` **splits** into **ARCHITECTURE.md** (the "how the world works" half:
  old §0, §9, §13) and **MECHANISMS.md** (the per-mechanism registry: old §1–§8, §10). It
  was a 583-line monolith doing two jobs. *(Executed 2026-06-06 per this mapping — §12 design
  log and §15 gaps → ARCHITECTURE; §11 metrics + §14 param index → MECHANISMS; section numbers
  preserved. See ARCHITECTURE §12.1-F. PARAMETERS extraction still pending.)*
- **TARGETS.md** is **new** — the project had no home for "expected emergent behaviour."
- **PARAMETERS.md** becomes authoritative for values, retiring the ROADMAP locked-param
  table (the source of the D1–D3 drift); ROADMAP points to it.
- **Implementation notes are NOT a document** — see §6.

---

## 3. MECHANISMS.md — one registry, four columns, not four documents

The supervisor confirmed: principles, theory, and math are **columns of one table, not
separate docs.** A mechanism's meaning, the principle behind it, its theoretical/literature
basis, and its math are the same fact viewed four ways — splitting them guarantees that
tuning one (e.g. the Matthew exponent α) silently de-syncs the others.

Each mechanism is one row / block carrying:
1. **Name & what it is** (e.g. "C Cred — dominance/status capital").
2. **Principle** it embodies (e.g. cumulative advantage; bounded-confidence convergence).
3. **Theory / citation** — tagged `[VERIFIED]` / `[INLINE]` / `[UNVERIFIED]`, pointer to
   LITERATURE.md (never restate the citation body here).
4. **Math** — the analytical form (e.g. `share_i ∝ (𝒞_i + ε)^α`).
5. **Category** — C1 (shared, parameter-differentiated) / C2 (shared machinery,
   semantically re-pointed) / C3 (genuinely different architecture). The C1/C2/C3 scheme is
   load-bearing and carries over from MODEL_SPEC §0.
6. **Implementation pointer** — `src/...::function` (a path, not prose; see §6).
7. **Parameter pointer** — names only; values live in PARAMETERS.md.

---

## 4. PARAMETERS.md — value, range, and status are one row

Ranges and settled values are **not** two documents (that split is exactly how the D1–D3
discrepancies arose). One row per parameter:

`name · current value · range · status · grounding · lock/sweep/retire history`

Status ∈ `{OPEN, UNDER-REVIEW, LOCKED}`. A LOCKED parameter changed only by a dated
sweep/retire entry (append-only). This document is the **single** authoritative source of
parameter values; ROADMAP, MECHANISMS, and the blueprints all point here.

---

## 5. TARGETS vs HYPOTHESES — the graduation rule (protects the HARKing discipline)

The line is bright and it matters:

- A **TARGET** is an aspiration: "we are shooting for spatially-partitioned cultural groups
  to emerge." Qualitative, not dated-before-a-specific-run, not falsifiable-as-written.
  Lives in TARGETS.md.
- A **HYPOTHESIS** is a pre-registration: a falsifiable claim with a test spec (which run,
  which statistic, which threshold) and a pre-committed interpretation of each outcome,
  dated *before* the run. Lives in HYPOTHESES.md.

**Graduation:** a target becomes a hypothesis the moment it acquires a falsification spec —
at which point it is *moved* (not copied) into HYPOTHESES.md with its registration date, and
the TARGETS entry is replaced by a pointer. An aspiration may never be recorded as a
confirmed prediction. CC enforces: nothing enters HYPOTHESES without a test spec + pre-
committed interpretation; nothing in TARGETS is ever marked "supported/confirmed."

---

## 6. Why implementation is a pointer, not a document

"How it's implemented in code" deliberately has **no document of its own.** Code changes
faster than any prose doc is updated, so an implementation-notes doc is the single hardest
artifact to keep honest and the most certain to drift. Instead:
- **What/why of the design** lives in ARCHITECTURE / MECHANISMS (durable — changes rarely).
- **How it's coded** lives *with the code* (docstrings, a per-module README the code owns).
- MECHANISMS carries a **pointer** (`src/model/cred.py::accumulate`) — a path can't drift
  the way restated prose can, and a broken path is catchable by tooling.

The one exception: when the *why* of an implementation choice is itself a decision worth
recording (e.g. "we cache mean_cred per step because the birth batch is simultaneous"),
that rationale goes in the relevant design-decision log (ARCHITECTURE or MECHANISMS), not in
a standalone implementation doc.

---

## 7. Maintenance model

- **Supervisor** authors and amends this charter and the docs' *content decisions* in chat.
- **CC** enforces and maintains: applies the update triggers, refuses to create an
  off-charter top-level doc, keeps pointers valid, runs the append-only discipline.
- **Doc-maintenance directives are a distinct blueprint set** (`blueprints/meta/`),
  authored in chat like any other directive, so doc changes are reviewable and dated rather
  than ad hoc.
- **CLAUDE.md** mirrors §2's triggers as report-standards; amending §2 requires the matching
  CLAUDE.md edit in the same change (principle 5).

---

*End of DOCS_CHARTER — created 2026-06-05. Amend §2 before adding any home.*
