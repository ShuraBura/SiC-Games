# SiC Games — Documentation Hygiene Directive F2–F7

**Issued by:** Supervisor (via Claude chat)  
**Assigned to:** Claude Code  
**Date:** 2026-06-11  
**Scope:** Six stale-documentation fixes. No model code changes. No simulation runs.

---

## Ground rules

- All fixes are purely textual. No logic changes, no parameter changes to running code beyond what F5 explicitly permits.
- For any fix that reconciles a secondary document to an authoritative source, **read the authoritative source first**, confirm the value, then edit the secondary document to match. Never edit from memory or from this directive's prose — the authoritative source is the ground truth.
- Run the acceptance check for each task before moving to the next. A failed acceptance check is a blocking STOP (CLAUDE.md Rule 11). Report the failure to the supervisor; do not attempt a workaround.
- After all six tasks pass, produce a single summary report (see §8).

---

## Task F2 — Reconcile τ_parent in MECHANISMS to PARAMETERS

**Problem:** `MECHANISMS.md` states τ_parent = 0.1. `PARAMETERS.md` (authoritative) states τ_parent = 0.0. MECHANISMS is wrong.

**Action:**
1. Open `PARAMETERS.md`. Read the locked value for τ_parent. Confirm it is 0.0 (or record whatever value is actually there — the directive does not hardcode it; PARAMETERS is authoritative).
2. Search `MECHANISMS.md` for every occurrence of `τ_parent` (and any aliases: `tau_parent`, `parent_transfer`, or equivalent). Confirm exactly one numerical value is stated.
3. Replace that value with the value read from PARAMETERS. Do not change surrounding prose unless it is factually wrong as a direct consequence of the number change.
4. Confirm no other document except MECHANISMS required a τ_parent number fix (a grep across the doc tree for the old value is sufficient; patch any additional occurrences found).

**Acceptance check:**
```
grep -r "τ_parent\|tau_parent" docs/  # or wherever the doc tree lives
```
No occurrence of the pre-fix value remains. The value present in MECHANISMS matches PARAMETERS exactly.

---

## Task F3 — Regenerate CLAUDE.md file-structure block from actual tree

**Problem:** The file-structure block in `CLAUDE.md` names at least one non-existent file (`silicon.py`), has a wrong tree root, and shows a wrong test count. It is stale.

**Action:**
1. From the repo root, run:
   ```bash
   find . -not -path './.git/*' -not -path './outputs/*' -not -path './__pycache__/*' \
     | sort | head -120
   ```
   Capture the output. This is the authoritative current tree.
2. Locate the file-structure block in `CLAUDE.md` (it is a fenced code block, likely labelled something like `# project tree` or similar).
3. Replace the entire fenced block with a freshly generated tree. The tree should show:
   - Correct root name.
   - All currently existing source files, test files, config files, and doc files.
   - No phantom files (`silicon.py` or any other file that does not exist on disk).
   - Directories collapsed to one level of children (do not flatten the whole tree into a flat list, and do not expand every subdirectory to leaf level — match whatever depth convention the existing block used, defaulting to 2 levels).
4. Do not alter any other content in CLAUDE.md.

**Acceptance check:**
Every filename listed in the regenerated block must exist on disk (`xargs -I{} test -e {}` or equivalent). Zero phantom filenames. `silicon.py` does not appear anywhere in the block.

---

## Task F4 — Replace hard-coded test counts in CLAUDE.md with "the full suite"

**Problem:** CLAUDE.md states hard-coded test counts (256/303 vs actual 344) that are already stale and will continue to drift.

**Action:**
1. Search CLAUDE.md for every occurrence of a hard-coded test count (any integer adjacent to words like "test", "tests", "passing", "suite", e.g. "256 tests", "303 tests", "344 tests", or similar).
2. Replace each such phrase with the formulation **"the full test suite"** (or the grammatically natural equivalent in context, e.g. "all tests pass" instead of "N tests pass"). Do not replace counts that refer to something other than the test suite (e.g. a line count, a parameter count).
3. Verify with `pytest --collect-only -q 2>/dev/null | tail -1` to confirm the actual current test count and record it in the §8 summary — but do **not** hardcode it back into CLAUDE.md.

**Acceptance check:**
```bash
grep -nE '[0-9]{2,} tests?' CLAUDE.md
```
Returns zero matches (no hard-coded test counts remain).

---

## Task F5 — Fix config.py: stale σ_Si comment and pre-lock defaults

**Problem:** `config.py` defaults for σ_Si, matthew_alpha, and f_C still show pre-lock values. The σ_Si comment is affirmatively wrong. No science impact (runtime configs override), but the stale values are a latent trap for any code path that instantiates without an override (unit tests, REPL, future refactors).

**Decision (supervisor-delegated, confirmed):** Set defaults to locked values AND fix the σ_Si comment.

**Action:**
1. Open `PARAMETERS.md`. Read the locked values for **σ_Si**, **matthew_alpha**, and **f_C**. Record all three. These are the ground-truth values; do not use any value from memory, from this directive's prose, or from config.py's current content.
2. Open `config.py`. For each of the three parameters:
   a. Replace the default value with the locked value from PARAMETERS.
   b. If the parameter has an inline comment, rewrite the comment to accurately describe what the parameter does and what value it is set to. In particular, the σ_Si comment is known to be affirmatively wrong — rewrite it from scratch based on what σ_Si actually controls in the model.
3. Do not change any other defaults, logic, or structure in config.py.

**Acceptance check:**
```python
# Run this as a one-liner after the edit:
python - <<'EOF'
import ast, sys
src = open('config.py').read()
tree = ast.parse(src)
# Collect all assignments at module level or inside a config class/dataclass
# and assert the three parameters match PARAMETERS locked values.
# (CC: implement the specific assertion once you have the locked values in hand.)
print("F5 check: implement after reading PARAMETERS locked values")
EOF
```
Concretely: after the edit, `grep -E 'σ_Si|sigma_Si|matthew_alpha|f_C' config.py` shows values that match PARAMETERS exactly, and the σ_Si comment no longer contains the incorrect description.

---

## Task F6 — Bump ROADMAP header date

**Problem:** The date in the `ROADMAP.md` header is stale.

**Action:**
1. Locate the date field in the ROADMAP.md header (first 20 lines).
2. Replace it with today's date: **2026-06-11**.
3. Do not alter any other content.

**Acceptance check:**
```bash
head -20 ROADMAP.md | grep "2026-06-11"
```
Returns a match.

---

## Task F7 — Correct J&H 2014 page range in LITERATURE.md

**Problem:** The page range for Janssen & Hill (2014) differs between the session handoff and LITERATURE.md. The authoritative page range, verified directly against the published article, is **pp. 823–835**.

**Authoritative citation:**  
> Janssen, M.A. & Hill, K. (2014). Benefits of Grouping and Cooperative Hunting Among Ache Hunter–Gatherers: Insights from an Agent-Based Foraging Model. *Human Ecology*, 42, 823–835. https://doi.org/10.1007/s10745-014-9693-1

**Action:**
1. Open `LITERATURE.md`. Find the entry for Janssen & Hill 2014 (DOI: 10.1007/s10745-014-9693-1).
2. Confirm that the page range field is present. If the current value is anything other than 823–835, replace it with 823–835.
3. While in this entry, verify the following fields are present and correct. If any are missing or wrong, add/correct them:
   - Full author names: Marco A. Janssen & Kim Hill
   - Year: 2014
   - Journal: *Human Ecology*
   - Volume: 42
   - DOI: 10.1007/s10745-014-9693-1
   - CoMSES model codebase: 3902
4. Additionally, confirm that the **corrected findings** from the prior literature-verification session are present in this entry. The entry must state (in whatever prose style LITERATURE.md uses):
   - Cooperative hunting (CCSP model) yields **−4% mean harvest vs solitary** (2.82 vs 2.95 kg/day/hunter).
   - Risk reduction is large: zero-return day probability **83% lower** (9% cooperative camp vs 52% solitary).
   - Optimal band size of **7–8 hunters** is a smooth budget-constraint tangent (Fig. 7 indifference curve), **not** a threshold cliff or access gate.
   - The −4% mean-yield cost and 83% risk-reduction are net effects of the full CCSP strategy (coordinated search + cooperative pursuit) relative to solitary IRM(depletion); the intermediate CUS step (group living, uncoordinated) itself drops yield further, and cooperative pursuit partially recovers it (+17% over CUS).
   - No hard threshold or access-gate exists in the model. Group-size effects are smooth and monotonic in the relevant range.
   - Recruitment distance Dmax ~200m (2 cells); rarely larger.
   - Model environment: Mbaracayu Reserve, Paraguay (tropical forest; 100 replicate runs per condition over 1 simulated year; 100 simulated years for group-size sweep).
   
   If any of these findings are absent, add them. If any prior entry contradicts them (e.g. describes cooperative hunting as providing a mean-yield benefit or describes the 7–8 optimum as a threshold), **replace** the incorrect text with the correct formulation.

5. If LITERATURE.md also contains the Janssen & Hill 2016 entry (DOI: 10.1007/978-3-319-31481-5_3, CoMSES 4538), verify that entry's page range and citation fields are internally consistent; flag any discrepancy in the §8 summary but do not alter that entry without supervisor confirmation.

**Acceptance check:**
```bash
grep "823" LITERATURE.md  # page range present
grep "10.1007/s10745-014-9693-1" LITERATURE.md  # DOI present
grep -i "4%" LITERATURE.md  # −4% finding present
grep -i "83%" LITERATURE.md  # 83% risk-reduction present
```
All four return matches. No occurrence of language describing a hard threshold, access gate, or mean-yield benefit for cooperative hunting in the J&H 2014 entry.

---

## §8 — Summary report (produce after all tasks pass)

After all six acceptance checks are green, produce a single report with the following structure and nothing else:

```
DOC HYGIENE F2–F7 — COMPLETE
Date: 2026-06-11

F2  τ_parent: MECHANISMS updated. Value confirmed from PARAMETERS: [value].
F3  File-structure block regenerated. Phantom files removed: [list]. New root: [root].
F4  Hard-coded test counts removed. Current actual test count (not stored): [N].
F5  config.py defaults updated. Locked values confirmed from PARAMETERS:
      σ_Si = [value], matthew_alpha = [value], f_C = [value].
    σ_Si comment rewritten.
F6  ROADMAP date bumped to 2026-06-11.
F7  LITERATURE.md J&H 2014 page range set to 823–835.
    Corrected findings block: [present / added / corrected — specify which].
    J&H 2016 entry: [consistent / discrepancy flagged: describe].

GATE: all acceptance checks GREEN.
```

If any task produced a STOP, replace its line with `STOPPED — [reason]` and do not mark the overall gate GREEN.

---

*End of directive.*
