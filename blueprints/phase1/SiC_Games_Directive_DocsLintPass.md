# SiC Games — CC Directive: Project-Docs Lint Pass (REPORT-ONLY)

**Type:** Maintenance directive, not a build stage. No model code changes.
**Mode:** REPORT-ONLY. CC produces a findings report. CC does **not** edit, fix, or
regenerate any document. Every proposed change is a line in the report for the
supervisor to action — nothing is auto-applied.

---

## 0. Why

Recurring failure mode: a fact exists in one authoritative doc but is contradicted,
stale, or re-litigated elsewhere (e.g. a handoff asserting a "clean gap" the data did
not show; a locked parameter quoted from memory rather than config; the `/mnt/project/`
snapshot drifting from the local authoritative copies). This pass surfaces those seams.
It is the report-only half of the "wiki maintain/lint" idea — adopted as a principle,
deliberately stripped of any auto-compilation or auto-edit, because this project's
rigour standard forbids machine-generated synthesis entering the authoritative layer
without supervisor review.

## 1. Scope

Scan **only** the authoritative project docs in the repo:
ROADMAP.md, HYPOTHESES.md, LITERATURE.md, MODEL_SPEC.md, INDEX.md, ARTIFACTS.md,
CLAUDE.md (and any `SiC_Games_*.md` in the repo root). Read config files as the source
of truth for parameter values, but do not modify them.

Do **not** scan or judge code logic in this pass. This is a documentation-consistency
audit, not a code review.

## 2. Checks to run

Run each check across all in-scope docs and report findings under that check's heading.

1. **Cross-doc contradictions.** Any claim in one doc that conflicts with a claim in
   another (e.g. a parameter said to be "locked" in one doc and "pending" in another;
   a hypothesis marked confirmed in one place and open in another). Report both
   locations with quoted lines and file:line references.

2. **Stale locked-parameter claims.** For every numeric parameter described as locked
   or final in any doc, compare against the value in authoritative config. Report any
   mismatch, and any parameter described as locked in prose that has **no** corresponding
   config entry (locked-in-prose-only is itself a finding).

3. **Orphan / dangling decision tags.** Every `§DECISION-*`, `§H-*`, `§STAGE-*` tag:
   report any referenced from one doc but defined nowhere; any defined but never
   referenced; and any marked RETRACTED whose retraction is not reflected everywhere it
   is cited (e.g. §H-NO-COASTAL-MORPHOLOGY was retracted — confirm no doc still treats it
   as live).

4. **Single-home violations.** Any fact that has substantive definitions in more than one
   doc (the "one fact, one home" principle). Report the fact and all the homes; the
   supervisor decides which is canonical. Do not guess.

5. **Snapshot-drift flag.** Where determinable, note any doc whose content is plainly
   superseded by a later session's decision (e.g. a handoff line the data has since
   contradicted). Report as a candidate, not a verdict — CC cannot know session order
   with certainty, so flag for supervisor confirmation.

## 3. Output

A single report file `outputs/docs_lint_[YYYYMMDD]/lint_report.md`, structured by the
five check headings above. Each finding: what, where (file:line for both sides of a
contradiction), and a one-line **suggested** resolution clearly marked as a suggestion.
End with a counts summary (findings per check).

No other output. No edits to any scanned doc or config.

## 4. Acceptance (this directive is done when)

1. All in-scope docs enumerated in the report header (so coverage is auditable).
2. All five checks run; each has a heading, populated or explicitly "no findings".
3. Report is the only artifact written; `git status` shows no modifications to any
   scanned doc or config file (assert clean except the new report file).
4. Every suggested resolution is marked as a suggestion, not applied.

## 5. Explicit non-goals (do NOT do these)

- Do not fix, edit, merge, or regenerate any document.
- Do not auto-upgrade, retract, or create any `§` tag.
- Do not change config values, even on a detected mismatch — report it.
- Do not synthesise new articles or summaries. This is an audit, not a compile.
- Do not judge or refactor code.
