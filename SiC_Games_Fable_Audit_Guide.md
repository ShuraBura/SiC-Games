# SiC Games — Full Simulation (ABM) Review Guide — LOCAL / CC (read-only)

**Auditor:** A Claude Code (CC) instance acting **strictly as a read-only reviewer** for this task.
**You are reviewing, not building.** For the duration of this task you did not author this repository. Do not defend design choices — evaluate them. If you recognise code as your own prior work, review it as if a stranger wrote it.

**Mode — RUN freely, WRITE nothing but the report, FIX nothing:**
- ✅ **Permitted (and encouraged):** read every file; enumerate the tree; `grep` across the repo; **run the test suite, determinism checks, and any acceptance gates; execute scripts; compute values** to cross-check against the docs and literature. Executing code to verify behaviour is the core value of this review — do it.
- ❌ **Forbidden:** editing, creating, or deleting any repository file; "fixing" a failing test, bug, or inconsistency you find; staging, committing, pushing, or branching. The ONLY file you write is the review report (§6), saved to a scratch location OUTSIDE the tracked repo (e.g. `../audit_scratch/` or a gitignored dir). Any intermediate artifacts (test logs, computed values, plots) also go to scratch, never into the tracked tree.
- If you find a broken test or a bug: **document it** (the command, the output, why it's wrong). Do **not** repair it. Repairs are a separate task the supervisor directs afterward.

**Repo:** the **local working copy** of `ShuraBura/SiC-Games` (recently migrated off Google Drive). Review the whole local tree. Confirm at the start that it is the local folder you were pointed at, and note the current git commit/hash (read-only: `git log -1`, `git status` — do not change anything).

**Deliverable:** ONE report file, written to scratch (§6).
**Project context:** SiC Games is an agent-based **simulation** (Python/Mesa) comparing two civilisational strategies — **C** (cooperative, socially embedded) and **Si** (individualist, self-reliant) — on matched Sugarscape-derived resource worlds. Central question H1(ii): which strategy is more resilient to periodic resource shocks? Science is pre-registered or locked before results are examined.

## §0 — The core review principle

**Separate three things, and label every finding as exactly one:**

1. **INCONSISTENCY** — something contradicts itself or another part of the repo. A literature value that disagrees with its cited source; a parameter stated differently in two documents; a rationale whose conclusion doesn't follow from its premises; code that doesn't implement what its spec says; a `[VERIFIED]` citation tag with no traceable source. These are the most useful to surface.
2. **UNSUPPORTED CLAIM** — an assertion (value, mechanism, conclusion) with no traceable backing in code, data, or a cited source. Includes parameters that trace only to a "session summary" or "handoff" rather than an authoritative config or paper.
3. **DESIGN PREFERENCE** — "I would have done this differently." A modelling choice that is internally consistent and defensible, but not how you'd do it. **These are LOW priority and MUST be labelled as such.** Do not let preferences dominate the report. If you cannot show a choice is inconsistent or unsupported, it is a preference — say so and rate it minor.

**Why this matters:** you are new to this project and have not yet earned calibration on its design rationale. A review full of preferences is hard for the supervisor to act on. A review of genuine inconsistencies and unsupported claims is directly actionable. When in doubt about which category a finding is, default to the *weaker* claim (preference over inconsistency) and say what evidence would upgrade it.

---

## §1 — First step: enumerate AND execute, don't pattern-match

Before any analysis:
1. **List the entire local repo tree** (`find` / `ls -R`). Every file. Do not infer contents from filenames. Note the git commit/hash and working-tree status (read-only).
2. **Identify the authoritative documents** and read them in full. The project uses a single-responsibility documentation system; the authoritative docs are (names may vary — confirm against the actual tree):
   - `ROADMAP.md`, `HYPOTHESES.md`, `LITERATURE.md`, `MODEL_SPEC.md`, `INDEX.md`, `ARTIFACTS.md`, `CLAUDE.md`
   - Stage blueprints `SiC_Games_Stage*_*.md`
   - The Python/Mesa implementation (the actual model code)
   - Reference models if present (NetLogo `Ache_v1_01.nlogo`, `Ache-v1_1b.nlogo`)
3. **Read the code, not just the docs.** A doc-only audit cannot catch spec-vs-implementation drift, which is one of the highest-value finding types.
4. **Run what can be run.** Locate and execute the test suite, determinism checks, and any acceptance/gate scripts. Record actual pass/fail and outputs — these are primary evidence. If the project has a documented way to generate a world / characterize a map / run a gate, run it and compare the result to what the docs claim.
5. Note anything you **could not access, read, or run** explicitly in the report (a review with silent gaps is misleading).

---

## §2 — Known-open items: DO NOT re-litigate these

The following are already known, pre-registered, and logged. They are **not findings.** Do not "discover" them. You may note if you find them *more* broken than documented, but do not list the known state as a problem:

- **The `game` field is PROVISIONAL** (intended `hump(NPP) × openness`, but openness is mechanically near-inert because NPP and forestness are both moisture-driven, so game tracks the NPP hump and peaks in forest rather than open ground). This is logged as a finding and scoped to a future **Stage 7.2** rework. The hunter/gatherer resource split is a known *missing mechanic*, not a bug to report.
- **Si is not yet implemented.** Si is an architecture lens only during the C build phase; no Si runs exist yet. Absence of Si code is intended, not a gap.
- **Seasonal resources / game migration (Stage 2)** are not built yet.
- **A7.4 (terrain game-hump gate) was restated twice** during development (biome-comparison → peak-position → unimodality). The current unimodality form is intended. Do not flag the history as instability.
- Any item explicitly marked PROVISIONAL, watch-item, or "deferred to Stage X" in the docs.

If you believe a known-open item is *mis-scoped* (e.g. should block something it currently doesn't), that is a legitimate finding — but frame it as "known item X has under-appreciated consequence Y," not as a fresh discovery.

---

## §3 — Audit dimensions (go deep on each; these are the lenses)

For each dimension, the question is always: **is it consistent, is it supported, does it do what it claims?** — not "would I have done it this way."

### 3.1 Logic & rationale
- Does each hypothesis (HYPOTHESES.md) have a falsifiable test specification? Was it pre-registered (logged *before* the analysis that bears on it), or does it look reverse-engineered from a result (HARKing)?
- Do stated conclusions follow from the evidence cited for them?
- Are there claims of the form "X causes Y" where the simulation only shows correlation or where X and Y are coupled by construction (e.g. the NPP/forestness coupling — check for *other* instances of confounded comparisons)?
- Does the C-vs-Si simulation comparison rest on genuinely *matched* worlds (same seed, same terrain), and is that matching actually enforced in code, not just asserted in docs?

### 3.2 Literature & literature VALUES (highest-value dimension)
- For every quantitative value attributed to a paper, **re-derive it from the cited source** where the source is in the repo or publicly checkable. Flag any value that does not match its source.
- Specifically scrutinise: **Janssen & Hill 2014** (cooperative hunting should be logged as net slightly-negative on mean yield ~−4%, positive only on variance — NOT yield-superadditive; the 7–8 optimum is a smooth tradeoff tangent, not a feasibility threshold). **Morin et al. 2024** (CDH success 67.2% vs 42% encounter; FID 177m vs 45m at 40kg; herding ~2× CDH probability). Verify these are stated correctly wherever they appear.
- Check every `[VERIFIED]` citation tag: is there a traceable full-text basis, or was it self-upgraded? Per CLAUDE.md, `[VERIFIED]` requires a logged full-text read. Flag any `[VERIFIED]` without one. Check `[SECONDARY]` tags are not over-claimed.
- Do parameters in MODEL_SPEC trace to a literature source or a derivation, or only to a "we picked this"? (Picked-without-justification is an UNSUPPORTED CLAIM, not necessarily wrong — flag for justification.)
- Are there literature claims used to justify design decisions that the paper doesn't actually support (over-reading an abstract, citing a forest study for a savanna mechanic, etc.)?

### 3.3 Documentation (single-responsibility integrity)
- The system claims "one fact, one home." Find facts stated in **two places** — and check they **agree**. Disagreement between two docs on the same parameter/value is a high-priority INCONSISTENCY.
- Find facts with **no home** (referenced but never authoritatively defined).
- Is any project question un-answerable from the docs macro→micro without grepping stage blueprints? (The docs claim this should be possible.)
- Are locked parameters actually marked locked, and read from an authoritative config rather than restated (and potentially drifting) across documents?

### 3.4 Architecture
- Is terrain genuinely precomputed as static arrays, with no terrain computation inside any agent loop? (Locked principle.) Verify in code.
- Is the Si seam real — is every mechanic toggleable with a clean port path — or are C-only assumptions hard-wired in ways that would make Si porting painful? (Architecture finding, not a demand to implement Si.)
- Is `step ≠ time` respected — is the model step an event-ordering index, with extinction-time never read as a duration without the τ (1 step = 1 month) conversion? Flag any place a step count is treated as a duration directly.
- Are there computations repeated in the agent loop that should be precomputed?

### 3.5 Code
- Does the code implement what its spec/blueprint says? **Verify by running it**, not only by reading. Flag spec-vs-implementation drift with the command + output that shows it.
- Determinism: same seed + same params → identical results? **Run it twice and check**, don't just look for a test. Is it enforced?
- Are there silent failure modes — gates that can pass without actually checking, exceptions swallowed, NaN/edge cases unhandled?
- Mixed C+Si populations must **never** be instantiated (civilisations run separately on matched worlds). Verify nothing can accidentally create a mixed population.
- Test coverage: are the load-bearing mechanics actually tested, or only the easy ones?

### 3.6 Scientific methodology (ABM-specific)
- Are identified equilibria/attractors genuine, or possibly numerical/initialisation artefacts? Is bistability (if claimed) robust across seeds?
- Are results ever reported from a single seed where multi-seed robustness is needed?
- Are adverse results (gate failures, extinctions) surfaced as primary findings, or buried? (The project principle is "never bury adverse results" — check it's honoured.)
- Does the model match any stylised facts it claims to match? Are those claims tested or asserted?

---

## §4 — How to verify a finding before you report it

For EACH candidate finding, before it goes in the report, confirm:
- **Location:** exact file + line/section. No finding without a location.
- **Evidence:** quote or cite the specific text/code/value. For literature, cite the source value vs the repo value.
- **Category:** INCONSISTENCY / UNSUPPORTED CLAIM / DESIGN PREFERENCE (§0).
- **You checked it isn't a known-open item (§2).**
- **You checked it isn't already addressed elsewhere in the repo** (don't flag X as missing if it's defined in a file you didn't read — §1.4).

A finding that fails any of these is not ready. Downgrade it to a "question" (§6) instead of asserting it.

---

## §5 — Severity model

Rate every finding:
- **BLOCKING** — invalidates a result, a locked parameter, or a core claim. The simulation or a stated result is unsupported in a way that affects conclusions. (Expected to be rare. If you find many "blocking" issues, re-check you're not over-rating preferences.)
- **MAJOR** — real inconsistency or unsupported claim that should be fixed before building further, but doesn't (yet) invalidate a published result.
- **MINOR** — small inconsistencies, doc drift with low consequence, missing-but-non-critical justification.
- **QUESTION** — you suspect an issue but couldn't verify it read-only, OR you need supervisor knowledge to judge. Phrase as a specific question, not an assertion.
- **PREFERENCE** — design choices you'd make differently but cannot show are wrong. Lowest priority. Group these together; do not interleave them with real findings.

---

## §6 — Report format (ONE file)

```
# SiC Games — Simulation Review Report
Date · repo commit/hash audited · what you could NOT access

## 1. Executive summary (≤ 1 paragraph)
Overall health in plain terms. Count of findings by severity. The single
most important thing to fix first.

## 2. Findings table (severity-sorted, the triage view)
| ID | Severity | Category | Dimension | Location | One-line summary |
(BLOCKING first, then MAJOR, MINOR, QUESTION; PREFERENCE excluded from this table)

## 3. Detailed findings (one block each, BLOCKING→MINOR)
For each:
- ID, severity, category, dimension
- Location (file + line/section)
- Evidence (quote/cite the specific text, code, or literature value)
- Why it's a problem (the reasoning, explicitly)
- Suggested direction (brief — the supervisor decides the actual fix)

## 4. Literature values audit (dedicated table)
| Value | Attributed to | Stated in repo | Source says | Match? | Location |
Every quantitative literature value you could check.

## 5. Questions for supervisor
Specific, answerable questions where you lacked context or repo access.

## 6. Design preferences (clearly separated, lowest priority)
Things you'd do differently but cannot show are wrong. Brief.

## 7. Coverage statement
What you audited, what you could not, and how confident each section is.
```

---

## §7 — Stance
- Aim for accuracy and usefulness: a careful, evidence-based review that the supervisor can act on. This is a constructive quality check, not a critique exercise — surfacing a real inconsistency is a helpful contribution.
- Show your reasoning so every finding is checkable. A finding you can't support is better left as a question.
- Rate findings honestly in both directions: don't inflate design preferences into major findings, and don't under-rate a well-evidenced one.
- Where a dimension is in good shape, say so plainly — a clean result on a real check is useful information.
- Where you're uncertain, say so and note what would resolve it. Stay within your evidence.

**Final reminder:** This is a READ-ONLY review. Produce the report only; make no changes to the repository or files.
