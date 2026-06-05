# SiC Games — ROADMAP Table Repair Directive

**Version:** 1.0
**Intended consumer:** Claude Code
**Scope:** Surgical repair of the corrupted locked-parameter / status region of
`ROADMAP.md`. **Documentation only — no code, no tests, no model behaviour touched.**
**Backup before starting:** copy `ROADMAP.md` to `ROADMAP.md.bak_pre_tablefix`
before any edit. This is a text edit to one file; if anything looks ambiguous, stop
and report rather than guess.

---

## 0. The problem

The "Locked parameters" region of `ROADMAP.md` has accreted three distinct defects
from repeated append-without-dedup edits during Stages 4.4–4.5:

1. **Duplicated rows.** The pair `N_carry | 400 | Stage 4.5 | C birth ceiling
   (carrying_cost)` and `alpha_carry | 1.0 | Stage 4.5 | C birth ceiling steepness`
   is repeated **twelve times** in the block that currently sits between the
   `p_max_C_bare` row and the `T*_C_A075` row. All twelve carry identical values,
   so no information is lost by collapsing them to one each — but twelve copies of a
   "locked" value is a maintenance hazard: a future re-sweep must find and fix all
   twelve, and the first missed copy becomes a stale lock that still reads authoritative.

2. **Schema collision.** The "Pool diagnostics table format" header row
   (`| Config | Mean contributed/step | Mean drawn/step | Mean unmet (t≥500) |
   Peak unmet (t≥500) | Gate (mean<20%) |`, 6 columns) is immediately followed by
   4-column locked-parameter rows. A 4-column row rendered under a 6-column header
   is malformed Markdown and misleads any reader (human or agent) about which table
   they are in.

3. **Misfiled status rows inside the parameter table.** Two rows that are *stage
   status / outcome notes*, not parameters, are wedged into the parameter region:
   - `| Stage 4.4 k=3 Feasibility | ⚠ Si Fail | k=3 Si population explosion ... |`
   - `| Stage 4.5 Task 0 | ⚠ T0 fail | carry_discount ... Tasks 2-4 pending. |`
   - `| Stage 4.5 patch | ✓ complete | T* complete (see §7.2) ... Ready for Stage 5. |`
   These belong in the status narrative, not the locked-parameter table.

**This directive fixes the three defects without changing any parameter value.**
No locked value is altered, retired, or re-interpreted. This is a formatting and
de-duplication pass only.

---

## 1. Task 0 — Backup and inventory

1. Copy `ROADMAP.md` → `ROADMAP.md.bak_pre_tablefix`.
2. Locate the corrupted region (currently approximately lines 416–449, but **find it
   by content, not line number** — line numbers will have drifted). The region begins
   at the "Pool diagnostics table format" header and ends at the
   `| Stage 4.5 patch | ✓ complete | ... |` row immediately before the
   "## Pre-registered Hypotheses" heading.
3. Before editing, extract and list every **distinct** parameter row in the region.
   Report this inventory (the deduplicated set) so the supervisor can confirm no
   parameter is dropped. Expected distinct parameters in this block:
   `p_max_C_bare`, `N_carry`, `alpha_carry`, `p_max_C_final`, `tau_pool`, `lambda`,
   `T*_C_A075`. If you find any distinct parameter row **not** in that list, STOP
   and report — there may be a non-duplicate hiding in the repetition.

---

## 2. Task 1 — Collapse duplicate parameter rows

In the canonical "Locked parameters" table (the table whose header is
`| Parameter | Value | Locked at | Rationale |`):

1. Ensure each of these appears **exactly once**, with these values (do not change
   the values — these are the confirmed locks, restated here only so you can verify
   you kept the right ones):

   | Parameter | Value | Locked at | Rationale |
   |---|---|---|---|
   | p_max_C_bare | 0.11 | Stage 4.5 | C null control (bare, carry_cost) |
   | N_carry | 400 | Stage 4.5 | C birth ceiling (carrying_cost) |
   | alpha_carry | 1.0 | Stage 4.5 | C birth ceiling steepness |
   | p_max_C_final | 0.12 | Stage 4.5 | C final (pool+λ) |
   | tau_pool | 0.05 | Stage 4.5 | Pool contribution fraction |
   | lambda | 0.1 | Stage 4.5 | C wealth inheritance |
   | T*_C_A075 | > 500 | Stage 4.5 patch | C T* at A=0.75; Si T* ∈ (50,200) from sweep |

2. Delete the eleven redundant `N_carry` rows and eleven redundant `alpha_carry`
   rows (keeping one of each). **Verify by count:** after the edit, `grep -c` for
   `^| N_carry ` and `^| alpha_carry ` in `ROADMAP.md` must each return the number
   of *genuinely distinct* N_carry/alpha_carry locks (expected: 1 each, unless a
   distinct second lock exists elsewhere in the file — if so, report it).

3. Note: `tau_pool` may already appear earlier in the locked-parameter table as
   `τ_pool | 0.10 → 0.05`. If so, the Stage 4.5 `tau_pool | 0.05` row is a
   **duplicate of an existing lock** and should be merged into that row, not added
   as a second row. Same for `lambda` if a `λ` row already exists. **Check for these
   cross-references before adding rows; report any merge you make.**

---

## 3. Task 2 — Move misfiled status rows out of the parameter table

The three status/outcome rows listed in §0 defect 3 are not parameters. Move them
to the **status narrative** where stage outcomes are recorded:

- `Stage 4.4 k=3 Feasibility` (⚠ Si Fail) and `Stage 4.5 Task 0` (⚠ T0 fail) and
  `Stage 4.5 patch` (✓ complete) → relocate into the relevant stage rows of the
  **"Current status"** table at the top of the file, or into a clearly-labelled
  status-notes subsection if they do not fit a single status cell.
- Preserve their full text verbatim — these are historical outcome records and must
  not be summarised away or deleted. Only their **location** changes.
- If the information in a moved row already exists in the Current-status table (e.g.
  the Stage 4.5 patch completion is likely already recorded), do **not** duplicate
  it — note in the report that it was already present and the misfiled copy was
  removed as redundant.

---

## 4. Task 3 — Repair the pool-diagnostics header

The "Pool diagnostics table format" 6-column header is a *format template* embedded
in Standing Rule 12, not a populated table. Ensure it reads as a template (an empty
example table or a clearly-labelled format spec) and is **not** followed by
4-column parameter rows. The parameter rows that were sitting under it move to the
canonical locked-parameter table (Task 1) or the status narrative (Task 2); nothing
parameter-shaped should remain under the pool-diagnostics header.

---

## 5. Equivalence check (the gate for this directive)

Because no value changes, there is a strict check that the repair was lossless:

1. **Value-set invariance.** The *set* of (parameter, value, locked-at) triples in
   the locked-parameter table after the edit must equal the *distinct set* before
   the edit. Produce a before/after diff of the distinct triple set. It must show
   **only deletions of exact duplicates and relocations — zero value changes, zero
   parameter drops, zero additions.** Report this diff. If it shows anything else,
   STOP — the repair has altered content and must be reverted from the backup.
2. **No status text lost.** The three moved status rows' text must appear somewhere
   in the file after the edit (relocated, not deleted). Confirm by string search.

---

## 6. Report

A short plaintext or markdown note (`outputs/roadmap_table_repair/report.md`):

| § | Content |
|---|---|
| §1 | Distinct-parameter inventory of the corrupted region (Task 0.3). |
| §2 | Duplicate-collapse result: grep counts before/after for N_carry, alpha_carry; any cross-reference merges made (tau_pool, lambda). |
| §3 | Status rows relocated, with destination; any found already-present and removed as redundant. |
| §4 | Before/after distinct-triple diff (the §5.1 gate). Must be deletions + relocations only. |
| §5 | Confirmation that no parameter value changed and no status text was lost. |

---

## 7. Stopping rules

| Condition | Action |
|---|---|
| A distinct parameter is found that is not in the Task-0.3 expected list | Stop. Report. Do not delete it as a "duplicate." |
| The before/after triple diff shows any value change or parameter drop | Stop. Revert from backup. Report. |
| Ambiguity about whether a row is a parameter or a status note | Stop. Report the row and ask. Do not guess. |

---

## 8. Out of scope

- Any change to a locked **value** (this is formatting/dedup only).
- Any change to model code, config, or tests.
- Any edit outside the corrupted region and its relocation destinations.
- The broader PARAMETERS.md extraction (separate, later directive). This repair
  makes the ROADMAP table clean *in place*; it does not migrate it to a new file.

*End of directive.*
