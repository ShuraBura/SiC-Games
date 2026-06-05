# SiC Games — MODEL_SPEC Full Extraction Blueprint

**Version:** 1.0
**Intended consumer:** Claude Code
**Scope:** Extend the existing `MODEL_SPEC.md` **pilot (v0.1)** from its current
trait/inheritance/reproduction cluster to a full-model specification covering every
stage through Stage 5.2, following the schema the pilot defines in its own §7.
**This is a documentation-only pass. CC writes NO code and NO tests, and MODIFIES
NO model behaviour, config, or existing tests.** The only file written is
`MODEL_SPEC.md` (plus the extraction report in §8).
**Prerequisite:** the `MODEL_SPEC.md` pilot exists and is the structural template.
Read it in full as Task 0 and conform to it exactly — do not invent a parallel
structure.
**Backup before starting:** copy `MODEL_SPEC.md` → `MODEL_SPEC.md.bak_pre_fullextract`.

---

## 0. North Star

The pilot already fixed every convention this extraction needs: the three-way
**C1/C2/C3** mechanism classification + **SEAM** status (pilot §0), the
provenance-tag system (`[VERIFIED]`/`[INLINE]`/`[UNVERIFIED]`, pilot header), the
"one infrastructure, C and Si as parameterised configurations" framing (pilot §0),
the design-decisions log format (pilot §5), and the **§7 section ordering for the
full extraction**. **This blueprint does not redefine any of those. CC's job is to
apply the pilot's established conventions across the rest of the model.**

The single most important property of the output: it must be **faithful, not
plausible.** A model spec that confidently states a wrong mechanic or launders an
unverified citation into `[VERIFIED]` is worse than no spec, because it outranks the
blueprints (per the pilot's status line: "where this document and a stage blueprint
disagree, the blueprint is the historical record and this document is the current
truth"). Every faithfulness guard below exists to prevent that.

---

## 1. Task 0 — Read the pilot and the sources; build a provenance map

1. Read `MODEL_SPEC.md` (the pilot) in full. Internalise: §0 classification table,
   the §1.1 column format, the provenance tags, the §5 design-log entry format, and
   the §7 full-extraction section ordering.
2. Read `ROADMAP.md` (current status table, C/Si distinction table, locked-parameter
   table, PM/WM trackers, design-decisions record, open-questions list, seams table).
3. Read `LITERATURE.md` (currently covers **only** Stage 5 Si Cred — confirm this;
   it defines what is legitimately `[VERIFIED]`).
4. Identify and list the source documents for each stage's mechanics. Blueprints and
   fix/benchmark instruction files are `SiC_Games_*.md` (e.g.
   `SiC_Games_Stage1_Blueprint`, `SiC_Games_Stage4.1a_Blueprint`,
   `SiC_Games_JT_Fix_Benchmark`, `SiC_Games_Perf_Audit`). Stage **reports** are the
   `report*.html` files under `outputs/<stage_dir>/` named in the ROADMAP status rows.
5. Produce a **stage → source-document map** as the first section of the extraction
   report: which blueprint(s) and report(s) ground each mechanic to be documented.
   If a mechanic referenced in ROADMAP has no findable source document, list it as a
   gap — **do not reconstruct it from inference.**

---

## 2. Faithfulness guards (read before writing any section)

These are the load-bearing constraints. Violating any of them is grounds to stop.

### 2.1 Citations — tag-and-float, never self-upgrade
- **Propagate the pilot's existing provenance tags verbatim.** Do not change any tag
  the pilot already set.
- **New citations** pulled in from blueprints/reports that the full extraction now
  covers (e.g. Stage 2 joint-task, Cred, pool sources) enter tagged **`[INLINE]`**
  (cited in a blueprint but not in `LITERATURE.md`).
- A citation may be tagged **`[VERIFIED]` ONLY if it is already present in
  `LITERATURE.md`.** CC does **not** verify papers, does **not** web-fetch sources,
  and does **not** upgrade any tag to `[VERIFIED]` on its own authority.
- Anything CC attributes from general knowledge (not found in a blueprint or
  LITERATURE.md) is **`[UNVERIFIED]`** with the note "Claude's attribution; confirm."
- **Deliverable:** a consolidated **citations-to-verify worklist** (extraction report
  §C below): each row = (claim as stated in SPEC) + (SPEC section using it) +
  (asserted source) + (current tag). This is what the supervisor clears in chat.
  Nothing on it becomes `[VERIFIED]` until then.

### 2.2 Scope — descriptive only
- CC writes **no code, no tests**, and does not modify config or existing tests.
- If, while reading code to document a mechanic, CC finds a **discrepancy** between
  what a blueprint/ROADMAP says and what the code does (e.g. a value, a behaviour, a
  seam that is not actually inert), CC **records it in the SPEC §15 gaps list as a
  flagged discrepancy** — it does **not** fix it. Discrepancies are findings for the
  supervisor to convert into their own directives, not side-effects of this pass.

### 2.3 Contested items stay OPEN
- The pilot records decisions that are **proposed/open, not settled.** Carry them
  forward with their status intact. Specifically:
  - **§5.1-A** cultural/physical dual-inheritance split — **PROPOSED, not implemented.**
  - **§5.1-D** σ_inherit calibration target = c1/c2 not ψ — **supersedes the retired
    Stage 5.2 Task 3 σ* selection; corrective directive pending.** Document the σ_inherit
    lock as its current value with this OPEN/under-review flag attached — do **not**
    present σ*=0.10 as settled.
  - **§2.3** ψ's channel (cultural vs physical) — **OPEN.**
  - The four **§6 open modelling decisions** (ψ channel, physical-channel mixing rule,
    asabiyyah locus, physical-inheritance control design) — **OPEN.**
  - **C\*\* = C\*** pinning (ROADMAP Q11) — documented as **pinned/deferred**, not as
    an independent locked parameter.
- Do **not** resolve, drop, or quietly settle any of these. The SPEC documents *that
  they are open and what the open question is*, exactly as the pilot does.

### 2.4 Design-decisions log — no invented rationale
- The design-decisions log (full-schema §12) **carries forward the pilot's existing
  §5 entries verbatim** (§5.1-A through §5.1-E, §5.2 seams).
- CC may add a new design-log entry **only** if the decision is explicitly recorded
  in a blueprint or report it can cite. **CC must not infer "why" from "what."** If a
  mechanic exists but no document states the rationale, the mechanic is documented in
  its mechanism section with the rationale field marked "rationale not found in
  sources — see gaps," and it does **not** get a fabricated design-log entry.

### 2.5 Statistic discipline
- Carry the pilot §6 statistic note forward: for bounded `[0,1]` traits initialised
  at mean 0.5 / SD 0.2, **SD (or variance) is the dispersion measure, not Gini.**
  Where the extraction documents any diversity/homogenisation diagnostic, state the
  correct statistic and flag any source that used Gini on a bounded trait.

---

## 3. Output structure — the full §7 schema

Extend the pilot to the full section set it specifies in its §7, in this order.
Renumber the pilot's current sections into this scheme; preserve all existing pilot
content (it is the trait/inheritance/reproduction cluster and is already correct).

| § | Section | Source of content | Notes |
|---|---|---|---|
| 0 | How-to-read + C1/C2/C3 classification + SEAM | pilot §0 verbatim | No change. |
| 1 | State variables — **all** of them | pilot §1 + extract metabolism/vision/age/wealth detail, Cred state vars, pool state, world state | §1.1-style table for all; narrative only for load-bearing/contested ones. |
| 2 | Inheritance (cultural + physical channels) | pilot §2 verbatim | No change; already current. |
| 3 | Decision / σ economy | Stage 2 (softmax, Cred-coupled σ), 2.1 (mode switch), 3.2 (status amplification), 4.3 (Si adaptive σ if implemented) | **C2-critical:** C σ is Cred/status-coupled; Si σ is fixed/velocity-modulated. Classify each carefully. |
| 4 | Joint task + Matthew partition | Stage 2, 3.4 (α), 5.2 §2 (c2 defection) | C only. Si has no joint task — state this explicitly (the C2 trap: never wire Si to it). |
| 5 | Cred — C dominance / Si reciprocal | Stage 2–3.2 (C Cred), 3.3 (Si skeleton), Stage 5 + 5.1 (Si Cred near-dormancy redesign) | **C2-critical.** C Cred = dominance/status from joint tasks; Si Cred = reciprocal/near-dormancy reputation. Same field name, different economy. The pilot's si_cred row points here. |
| 6 | Support pool L1–L3 | Stage 4.1c, 4.2 (τ_pool), 4.3 (carry-over ρ, cap), 4.4/4.5 | C = L1+L2+L3 (status-mediated); Si = L1+L2 only. Document the BUG-003 history (cred pool contribution was silently 0 in all 4.1c data). |
| 7 | Reproduction + demography | pilot §3 + Stage 4.1a (birth/death decouple, P_birth, age window, γ Cred-modulated birth), 4.1b (η(a) ramp), 4.5 (carrying-cost ceiling N_carry/alpha_carry) | pilot §3 (C biparental / Si fission / coordinator seam) is current; extend with the birth-death and carrying-cost machinery. |
| 8 | Shocks / perturbations | Stage 4 (SeasonalOscillation A, T; NullPerturbation), 4.2 (amplitude/period sweep), 4.3 (mobile/scheduled — check implemented vs pending) | Document the WorldPerturbation protocol and effective_capacity. |
| 9 | World / resource substrate | Stage 1 (50×50 torus, twin peaks, growback), 4.4 (k_grid rescale to k=4, max_sugar=16, α=4) | Foundational; document the k_grid rescale and why (β_Si=5 viability). |
| 10 | Selection measurement | pilot §4 verbatim (forward note, not yet implemented) | No change; carries the Price-equation intent and the "target c1/c2 not ψ" note. |
| 11 | Metrics & diagnostics | extract from reports + ROADMAP standing rules R1–R12 | Thin/tabular. Note terminal-state fields (extinction_step, N_min, etc.) and the mean-based pool gate. |
| 12 | Design-decisions log | pilot §5 verbatim + only documented additions (§2.4 above) | Append-only; no invented entries. |
| 13 | Architecture seams | pilot §5.2 verbatim | No change. |
| 14 | Parameter registry | ROADMAP locked-parameter table | **Pointer, not copy** (see §4 below). |
| 15 | Gaps & unsourced + discrepancies | pilot §6 + new gaps + §2.2 discrepancies found | The self-correcting to-do; this is where flagged discrepancies land. |

**Detail discipline (pilot's rule, restated):** thin variables stay one-row; only
**contested or load-bearing** constructs get narrative + literature. Do not pad
mechanically-simple mechanics with prose. The pilot's "detail the things worth
detailing" instruction governs.

---

## 4. Parameter registry (§14) — pointer, not copy

`PARAMETERS.md` does not yet exist (it is a later directive). Until it does, the
**ROADMAP locked-parameter table remains the authoritative home** for parameter
values. Therefore SPEC §14:
- Does **NOT** restate parameter values (that would create the exact two-homes drift
  the INDEX "one fact, one home" rule forbids).
- Contains a **pointer**: "Authoritative parameter values + lock/sweep history:
  ROADMAP.md locked-parameter table (to migrate to PARAMETERS.md when that doc is
  built)." Plus, if useful, a bare *index of parameter names* with their owning
  mechanism section — names only, no values.
- When PARAMETERS.md is later created, this pointer retargets to it. Note that as a
  one-line forward reference in §14.

---

## 5. Equivalence / faithfulness gate

This is a documentation pass, so the "gate" is faithfulness, checked three ways:

1. **Pilot content preserved.** Every existing pilot section's content survives the
   renumbering intact (verbatim where this blueprint says "verbatim"). Diff the pilot
   sections before/after; they must be unchanged except for section-number relabeling.
2. **No `[VERIFIED]` not in LITERATURE.md.** Every `[VERIFIED]` tag in the output
   must correspond to an entry actually present in `LITERATURE.md`. Produce the list
   of `[VERIFIED]` tags and the matching LITERATURE.md entry for each. Any `[VERIFIED]`
   without a LITERATURE.md backing is a violation — downgrade to `[INLINE]` or
   `[UNVERIFIED]` and flag.
3. **Every contested item still OPEN.** The §2.3 list (dual-inheritance, σ target, ψ
   channel, the four §6 decisions, C\*\* pin) must each appear in the output with
   OPEN/PROPOSED/pinned status. Confirm each by name in the report.

---

## 6. Stopping rules

| Condition | Action |
|---|---|
| A ROADMAP-referenced mechanic has no findable source document | Document it as a gap in §15; do **not** reconstruct it. Continue. |
| CC is tempted to upgrade a citation to `[VERIFIED]` without a LITERATURE.md entry | Stop that upgrade. Keep it `[INLINE]`/`[UNVERIFIED]`; put it on the worklist. |
| A code/blueprint discrepancy is found | Record in §15 as a flagged discrepancy; do **not** fix. Continue. |
| A mechanic's rationale is not in any source | Mechanism documented; rationale field = "not found in sources"; **no** invented design-log entry. |
| Classification (C1/C2/C3) of a mechanic is genuinely ambiguous | Document it with the ambiguity stated explicitly and flag for supervisor — do not force a category. The C2 cases (σ, Cred, ψ, joint-task) are the dangerous ones; err toward flagging. |
| The pilot's existing content would have to change to fit | Stop. The pilot is current truth for its cluster; report the conflict rather than overwrite. |

---

## 7. Single review checkpoint

CC completes the **entire** extraction, then delivers the finished `MODEL_SPEC.md`
**plus** the extraction report (§8) in one hand-off. The SPEC does **not** become
authoritative until the supervisor reviews that report and clears the citations
worklist in chat. CC does not need section-by-section approval; the pilot already
fixes the conventions, so the review targets CC's *judgement calls* (citations,
discrepancies, classifications, OPEN items), all of which collect into the report.

---

## 8. Extraction report (`outputs/model_spec_extraction/report.md`)

Self-contained markdown. Sections:

| § | Content |
|---|---|
| §A | Stage → source-document map (Task 1.5). Mechanics with no findable source listed as gaps. |
| §B | Section-by-section coverage summary: for each §1–§15, what was added and from which source. |
| §C | **Citations-to-verify worklist** (the main review artifact): table of (claim) + (SPEC section) + (asserted source) + (current tag). All `[INLINE]` and `[UNVERIFIED]` items appear here. |
| §D | Discrepancies found between blueprints/ROADMAP and code (§2.2). Flagged, not fixed. "None found" if clean. |
| §E | Classification calls: every C2 and C3 mechanic, and any C1 that was a close call, with one-line justification. The C2 list (σ, Cred, ψ, joint-task, Deffuant weight) must be explicitly present. |
| §F | OPEN-item confirmation: each contested item (§2.3) and its preserved status. |
| §G | Faithfulness-gate results (§5.1–5.3): pilot-content-preserved diff summary; `[VERIFIED]`-tag audit; OPEN-item presence. |

---

## 9. Out of scope

- Any code, test, or config change (descriptive pass only).
- Building `PARAMETERS.md` (separate directive; §14 is a pointer until then).
- Verifying citations against papers (supervisor + chat, after this pass).
- Resolving any OPEN modelling decision (ψ channel, dual-inheritance, σ target, etc.).
- The corrective σ_inherit directive (separate; this pass only documents the open
  decision §5.1-D, it does not act on it).
- RESULTS.md / DEAD_ENDS.md backfill (separate directives).

---

## Red-team notes (for the supervisor, not Claude Code)

**Philosophy of science / provenance.** The single biggest risk is citation
laundering: an agent doing a "tidy-up" pass tends to resolve uncertainty toward
clean tags. The tag-and-float rule plus the §5.2 `[VERIFIED]`-audit gate are the
guard. Worth confirming on review that the worklist (§C) is *long* — if CC comes
back with most citations already `[VERIFIED]`, that is a red flag it over-credited,
not a sign the literature is solid (LITERATURE.md only covers Si Cred, so almost
everything should still be `[INLINE]`/`[UNVERIFIED]`).

**ABM methodology / faithfulness.** The SPEC outranks the blueprints once blessed,
so an extraction error becomes the authoritative record. The "no invented rationale"
rule (§2.4) and the gap-not-reconstruct stopping rule are what keep CC from
smoothing over holes with plausible fiction. The §D discrepancies list is also a
genuine audit byproduct — documenting the whole model against the code may surface
real spec-vs-code drift (the BUG-003 class of thing), which is a useful finding in
its own right, provided CC flags rather than fixes.

**The C2 classification is where theory can silently invert.** σ, Cred, ψ, and the
joint-task hook are all C2 (same machinery, civilization-dependent signal/meaning).
Misclassifying any as C1 ("just a parameter difference") is how an individualist
that seeks crowds, or a reciprocal-Si wired to dominance-Cred, slips through. §E
forces every C2 call to be stated and justified; review those most carefully.

**Deliverable count this session: this is deliverable 2 of 2** (ROADMAP table-repair
directive + this extraction blueprint). Combined with the analysis/decision work
earlier this chat, you are at roughly 5 substantive deliverables — a natural point
to start a fresh chat after these two are issued. Handoff summary available on request.

*End of blueprint.*
