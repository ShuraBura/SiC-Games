# SiC Games — Docs Lint Report
**Date:** 2026-06-13  
**Mode:** REPORT-ONLY. No docs were modified. Every item below is a suggested resolution for supervisor action.

---

## Docs enumerated (coverage audit)

| File | Last-updated claim | Notes |
|---|---|---|
| `docs/ROADMAP.md` | 2026-06-13 (Stage 1c complete) | Authoritative; updated this session |
| `docs/HYPOTHESES.md` | 2026-06-13 (H-TERRAIN-ASYMMETRY added) | Authoritative |
| `docs/ARCHITECTURE.md` | 2026-06-13 (§12.1-K added) | Authoritative; updated this session |
| `docs/MECHANISMS.md` | 2026-06-06 (split from MODEL_SPEC) | Not updated since Stage 7 |
| `docs/PARAMETERS.md` | 2026-06-08 (extracted) | Authoritative; covers §1–§10 |
| `docs/INDEX.md` | 2026-06-08 | Not updated since extraction |
| `docs/ARTIFACTS.md` | 2026-06-06 | Not updated since Stage 7.5 |
| `docs/LITERATURE.md` | 2026-06-12 (Survey A reorg) | Phase 1 forage sources added |
| `docs/TARGETS.md` | (not dated) | Read; no issues found |
| `docs/RESULTS.md` | (not dated) | Read; R-1 |
| `docs/DEAD_ENDS.md` | (not dated) | Read; DE-1 |
| `sic_games/CLAUDE.md` | 2026-06-08 (PARAMETERS.md handoff) | Partially stale — see Check 1, Check 5 |

`MODEL_SPEC.md` named in directive does not exist (split into ARCHITECTURE.md + MECHANISMS.md on 2026-06-06 per §12.1-F). Both halves scanned in its place.

Config file read as source of truth for parameter values: `sic_games/src/sic_games/config.py`.

---

## Check 1 — Cross-doc contradictions

### C1-1 — INDEX.md hypothesis listing stale (missing H-TERRAIN-ASYMMETRY)

**What:** INDEX.md HYPOTHESES.md entry says the file contains `(H-EMERGE-1, H-SUBSTRATE-6.0a, H_cc)`. HYPOTHESES.md now has a fourth entry, H-TERRAIN-ASYMMETRY, added 2026-06-13.

**Locations:**
- `docs/INDEX.md` — line ~49: `"HYPOTHESES.md: live (H-EMERGE-1, H-SUBSTRATE-6.0a, H_cc)"`
- `docs/HYPOTHESES.md` — H-TERRAIN-ASYMMETRY section (added 2026-06-13): `"Status: RESOLVED-CONFIRMED. mtn_ceiling = 0.317 pre-registered and confirmed."`

**Suggested resolution:** Add H-TERRAIN-ASYMMETRY to the HYPOTHESES.md line in INDEX.md.

---

### C1-2 — σ_inherit lock status: PARAMETERS.md says LOCKED; MECHANISMS.md says OPEN/under review

**What:** PARAMETERS.md §7 marks σ_inherit as `LOCKED` at 0.10. MECHANISMS.md §7.2 explicitly says it should be treated as OPEN/under review pending a corrective sweep targeting c1/c2 diversity (gate used wrong statistic: Gini(ψ) instead of SD(c1/c2)).

**Locations:**
- `docs/PARAMETERS.md` §7 line ~124: `"| Trait inheritance noise | σ_inherit | **0.10** | ≥0 | LOCKED | MECH §7 | Stage 3.3: 0.05. Stage 5.2 Task 3: raised to 0.10 …"`
- `docs/MECHANISMS.md` §7.2 line ~260: `"σ_inherit=0.10 should be treated as **OPEN/under review** pending a corrective directive targeting c1/c2 diversity. See ARCHITECTURE.md §12.1-D."`
- `docs/ARCHITECTURE.md` §15.3 item 5: `"σ_inherit corrective sweep — targeting c1/c2, ≥8 seeds, correct statistic (SD not Gini). σ_inherit=0.10 current lock is under review (§12.1-D)."`

**Suggested resolution:** Supervisor decides which status is operative. If OPEN/under review is correct, change PARAMETERS.md §7 status from `LOCKED` to `UNDER-REVIEW` and add a history note. If LOCKED is correct, update MECHANISMS.md §7.2 and ARCHITECTURE.md §15.3 to remove the "under review" language.

---

### C1-3 — sic_games/CLAUDE.md self-contradiction: PARAMETERS.md "not yet extracted" vs "authoritative home"

**What:** Two passages within sic_games/CLAUDE.md contradict each other on whether PARAMETERS.md has been extracted.

**Locations:**
- `sic_games/CLAUDE.md` line ~59: `"PARAMETERS.md not yet extracted — interim param home is the locked-param table below."`
- `sic_games/CLAUDE.md` line ~120: `"*(interim, until the §6 extraction: the locked-param table in THIS file below)*"`
- `sic_games/CLAUDE.md` line ~163: `"> **Authoritative home: docs/PARAMETERS.md** (extracted 2026-06-08, charter §6). This table has been superseded."`

The first two passages say extraction is pending; the third says it is done.

**Suggested resolution:** Delete lines 59 and 120's interim language; replace with a single pointer to PARAMETERS.md. The §161 block already carries the correct message.

---

### C1-4 — MECHANISMS.md header vs §14: parameter home described as pending vs done

**What:** MECHANISMS.md header (line 13) describes PARAMETERS.md extraction as a future event. MECHANISMS.md §14 says it was completed 2026-06-08.

**Locations:**
- `docs/MECHANISMS.md` line ~13: `"interim: the locked-param table in sic_games/CLAUDE.md; → PARAMETERS.md when extracted"`
- `docs/MECHANISMS.md` §14 line ~353: `"Authoritative parameter values + lock/sweep history: docs/PARAMETERS.md (extracted 2026-06-08, charter §6 — supersedes the former interim table in sic_games/CLAUDE.md)."`

**Suggested resolution:** Update MECHANISMS.md header line 13 to drop the "interim"/"when extracted" phrasing; replace with a pointer to PARAMETERS.md matching §14 language.

---

## Check 2 — Stale locked-parameter claims

### C2-1 — Five PARAMETERS.md LOCKED values have different defaults in config.py

PARAMETERS.md does not note that several locked values differ from config.py defaults. A run without a YAML override would silently use wrong values.

| Parameter | PARAMETERS.md locked value | config.py default | Config field |
|---|---|---|---|
| τ_trickle | **0.3** (LOCKED §8) | 0.05 | `DormancyConfig.tau_trickle` |
| σ_inherit | **0.10** (LOCKED §7) | 0.05 | `ReproductionConfig.inherit_sigma` |
| p_fission_Si | **0.065** (LOCKED §7) | 0.02 | `BirthSiConfig.p_fission_max` |
| p_max_C | **0.12** (LOCKED §7) | 0.02 | `BirthCConfig.p_max` |
| c2_defection | **True** (LOCKED §4) | False | `C2DefectionConfig.enabled` |

ARCHITECTURE.md §15.2 D1 and D3 confirm the PARAMETERS.md values are correct (0.3, 0.065). The config.py defaults are pre-lock values retained for backward compatibility with pre-Stage-5 configs.

**Suggested resolution:** Add a note to PARAMETERS.md §8 and §7 (and any other affected section) stating that config.py defaults differ from locked values and that YAML production configs must be used to activate locked values. Not a code change — documentation only.

---

### C2-2 — Phase 1 terrain constants absent from PARAMETERS.md (locked-in-prose-only)

PARAMETERS.md was extracted 2026-06-08, before Phase 1 Stage 1/1b/1c. The following constants are locked or pre-registered in `terrain.py` but have no PARAMETERS.md entry:

| Constant | Value | Status | Source |
|---|---|---|---|
| `mtn_ceiling` | 0.317 | Pre-registered (HYPOTHESES.md H-TERRAIN-ASYMMETRY) | ARCHITECTURE.md §9.5.1 |
| `LARGE_BODY_CEILING` | 0.10 | PROVISIONAL (supervisor must confirm) | terrain.py; ARCHITECTURE.md §12.1-K |
| `EXTERIOR_WATER_CEILING` | 0.12 | Retired-from-guard (Stage 1c); retained as diagnostic constant | terrain.py |
| `FORAGE_KCAL_TARGETS` | dict of 6 biome values | Locked Stage 7 (lit-grounded) | terrain.py |
| `NPP_GM2_SCALE` | (value in terrain.py) | Locked Stage 7 | terrain.py |
| `SHORE_BONUS_KCAL` | 1491.5 | Locked Stage 7 (Bird 1997 `[VERIFIED]`) | terrain.py |

**Suggested resolution:** Add a Phase 1 / Terrain Generator section (§11 or equivalent) to PARAMETERS.md. At minimum, add `mtn_ceiling` (LOCKED, pre-registered) and `LARGE_BODY_CEILING` (PROVISIONAL — do not mark LOCKED until supervisor confirms). `EXTERIOR_WATER_CEILING` should be marked RETIRED with effective date 2026-06-13.

---

## Check 3 — Orphan / dangling decision tags

### Summary

All §DECISION-* and §H-* tags found in authoritative docs are accounted for:

| Tag | Defined | Referenced | Retraction reflected? |
|---|---|---|---|
| §DECISION-LAKE-BODY-GUARD | ROADMAP.md decisions register; ARCHITECTURE.md §12.1-K | Both docs ✓ | N/A |
| §DECISION-NO-RIVERS | ARCHITECTURE.md §12.1-I | ROADMAP.md Stage 1b section ✓ | N/A |
| §H-NO-COASTAL-MORPHOLOGY | ARCHITECTURE.md §12.1-J (RETRACTED) | ROADMAP.md (RETRACTED) ✓ | Yes — both docs mark RETRACTED |
| §H-TERRAIN-ASYMMETRY | HYPOTHESES.md | ARCHITECTURE.md §9.5.1; ROADMAP.md Stage 1 ✓ | N/A (RESOLVED-CONFIRMED) |
| §H-EMERGE-1 | HYPOTHESES.md | ROADMAP.md open items ✓ | N/A (OPEN) |
| §H-SUBSTRATE-6.0a | HYPOTHESES.md | ROADMAP.md ✓ | N/A (RESOLVED-SUPPORTED) |
| §H_cc | HYPOTHESES.md | CLAUDE.md; ROADMAP.md ✓ | N/A (OPEN) |
| §STAGE-GEOSTRUCT | ROADMAP.md (future stage placeholder) | ARCHITECTURE.md §12.1-J, §12.1-K ✓ | N/A |

**No orphans or dangling tags found.**

### C3-1 — Stale `[INLINE]` tags in ARCHITECTURE.md §15.1 (near-orphan)

Several citations tagged `[INLINE]` in ARCHITECTURE.md §15.1 ("Citations needing LITERATURE.md entries") now appear in LITERATURE.md. The §15.1 table claims they are absent when they are not.

| Citation | ARCHITECTURE.md §15.1 tag | In LITERATURE.md? |
|---|---|---|
| Deffuant et al. (2000) | `[INLINE]` | YES (line ~92) |
| Hegselmann & Krause (2002) | `[INLINE]` | YES (line ~102) |
| Boyd & Richerson (1985) | `[INLINE]` | YES (line ~125) |
| Turchin (2003) | `[INLINE]` | YES (line ~167) |
| Klemm et al. (2003) | `[INLINE]` | YES (line ~75) |
| Gurven & Kaplan (2006) | `[INLINE]` | YES (line ~153) |
| Axelrod (1997) | `[INLINE]` | NO — genuinely missing |
| Davies et al. (2018) Loihi | `[INLINE]` | NO — genuinely missing |

MECHANISMS.md §1.2 also says Klemm et al. "not yet in LITERATURE.md" — stale since the 2026-06-05/06-12 reorg.

**Suggested resolution:** ARCHITECTURE.md §15.1: upgrade the six resolved entries to `[VERIFIED]` and remove them from the "needs entry" table; retain Axelrod (1997) and Davies et al. (2018) as genuinely open. Update MECHANISMS.md §1.2 footnote for Klemm.

---

## Check 4 — Single-home violations

### C4-1 — §DECISION-LAKE-BODY-GUARD ecological rationale in two docs

**What:** The ecological rationale for the largest-body guard (why inland-sea-class bodies are excluded from the continental arc) is stated substantively in both ROADMAP.md and ARCHITECTURE.md §12.1-K.

**Locations:**
- `docs/ROADMAP.md` decisions register: rationale paragraph (~4 sentences)
- `docs/ARCHITECTURE.md` §12.1-K: the same rationale in longer form, plus implementation details, sweep findings, and forward note

**Charter guidance:** Decisions register in ROADMAP is for the decision record; ARCHITECTURE is for the implementation spec. The rationale text appearing in both places is the violation — the rationale is substantive content, not a pointer.

**Suggested resolution (supervisor decides):** Option A — shorten the ROADMAP decisions register entry to a one-line pointer to ARCHITECTURE.md §12.1-K for full rationale. Option B — retain both as-is (ROADMAP as high-level summary, ARCHITECTURE as implementation spec) and accept the overlap.

---

### C4-2 — H1(ii) status in two docs

**What:** H1(ii) inversion finding (INVERTED, robust, 5/5 seeds) is stated substantively in both RESULTS.md and sic_games/CLAUDE.md.

**Locations:**
- `docs/RESULTS.md` R-1: H1(ii) inversion finding, partially resolved
- `sic_games/CLAUDE.md` §5 Pre-registered hypotheses: `"H1(ii): Status: INVERTED (robust, 5/5 seeds). C survives A=0.75; Si collapses."`

H1(ii) was routed out of HYPOTHESES.md to RESULTS.md. CLAUDE.md's §5 still carries a substantive status note rather than a pointer to RESULTS.md.

**Suggested resolution:** Replace the substantive H1(ii) status text in CLAUDE.md §5 with a pointer to RESULTS.md R-1. The "do not modify or ignore" instruction can be preserved as a constraint note.

---

### C4-3 — mtn_ceiling = 0.317 in three docs

**What:** The numeric value mtn_ceiling = 0.317 appears as a substantive fact in three documents, not as cross-references.

**Locations:**
- `docs/ARCHITECTURE.md` §9.5.1: `"mtn_ceiling = 0.317; best knobs: rough=1.0, waterK=0.99"`
- `docs/HYPOTHESES.md` H-TERRAIN-ASYMMETRY: `"Result: mtn_ceiling = 0.317 (pre-registered 2026-06-13)"`
- `docs/ROADMAP.md` Phase 1 Stage 1 row: `"mtn_ceiling=0.317 pre-registered"`

ARCHITECTURE and HYPOTHESES each make the value a "result" stated in their own terms (design consequence vs. hypothesis resolution). ROADMAP is a stage-row summary.

**Suggested resolution (supervisor decides):** Designate one canonical home (suggested: HYPOTHESES.md, as it is the pre-registration record and resolution site). ARCHITECTURE.md §9.5.1 and ROADMAP.md Stage 1 row become cross-references. Low priority — three docs being consistent is better than contradicting, but they may drift.

---

### C4-4 — SiC_Games_Forage_Return_Rate_Table.md vs LITERATURE.md forage values

**What:** LITERATURE.md line ~320 declares itself the bibliography of record for all Survey A forage sources and calls `SiC_Games_Forage_Return_Rate_Table.md` a "derived view." The derived file carries the same kcal/hr numbers inline, creating two homes for those numeric facts.

**Location:**
- `docs/LITERATURE.md` line ~320: canonical-home declaration
- `SiC_Games_Forage_Return_Rate_Table.md`: derived view with same values

**Suggested resolution:** This is a controlled two-home situation (LITERATURE.md explicitly names the canonical home). No immediate action needed unless the derived table gets out of sync. Recommend adding a "last synced" date to the derived table header.

---

## Check 5 — Snapshot-drift

### C5-1 — ARTIFACTS.md stale: Phase 1 artifacts absent; test count stale

**What:** ARTIFACTS.md was last updated 2026-06-06 (Stage 7.5). It does not index any Phase 1 artifacts and its test count is stale.

- "Key established numbers" section: test count 328 (Stage 7.5). Current suite: 394 tests.
- Phase 1 Stage 1 artifacts not indexed: `outputs/phase1_stage1/`, acceptance script, `sweep_waterK_stage1.csv`, `acceptance_and_artifacts.py`.
- Phase 1 Stage 1b artifacts not indexed: `outputs/phase1_stage1b/`, `sweep_waterK_stage1b.csv`, M2 scatter.
- Phase 1 Stage 1c artifacts not indexed: `outputs/phase1_stage1c/`, `sweep_waterK_stage1c.csv`, `M1_largest_body_sweep.png`.
- ARTIFACTS.md "gaps" note still lists Stage 4.x run parquets as the outstanding gap — superseded by Phase 1 artifact debt.

**Suggested resolution:** Add a Phase 1 section to ARTIFACTS.md. Update test count to 394. Update gaps note.

---

### C5-2 — sic_games/CLAUDE.md lines 59 and 120: PARAMETERS.md "not yet extracted" claim (stale since 2026-06-08)

**What:** CLAUDE.md still has two lines asserting PARAMETERS.md extraction is pending, contradicting the line 163 block that says it was done 2026-06-08.

- Line ~59: `"PARAMETERS.md not yet extracted — interim param home is the locked-param table below."`
- Line ~120: `"*(interim, until the §6 extraction: the locked-param table in THIS file below)*"`

This was flagged in ARCHITECTURE.md §15 D1 as "note for CLAUDE.md update" (confirmed resolved per PARAMETERS.md but the stale text was not removed).

**Suggested resolution:** Delete/rewrite lines 59 and 120. The §161+ block already carries the correct authoritative pointer.

---

### C5-3 — MECHANISMS.md header: "→ PARAMETERS.md when extracted" (stale since 2026-06-08)

**What:** MECHANISMS.md header (line ~13) still reads as if PARAMETERS.md extraction is a future event.

- Line ~13: `"interim: the locked-param table in sic_games/CLAUDE.md; → PARAMETERS.md when extracted"`
- §14 (line ~353): correctly states PARAMETERS.md is authoritative since 2026-06-08

**Suggested resolution:** Update MECHANISMS.md header line 13 to read: "Authoritative values: docs/PARAMETERS.md (extracted 2026-06-08)."

---

### C5-4 — ARCHITECTURE.md §15.1: six `[INLINE]` entries are now in LITERATURE.md (stale since 2026-06-12 reorg)

**What:** §15.1 lists citations that "need LITERATURE.md entries." Six of the listed citations were added to LITERATURE.md during the 2026-06-05/06-12 bibliography reorg and the Phase 1 Survey A work. The §15.1 table was not updated.

Resolved entries (now `[VERIFIED]`, still shown as `[INLINE]` in §15.1): Deffuant et al. (2000), Hegselmann & Krause (2002), Boyd & Richerson (1985), Turchin (2003), Klemm et al. (2003), Gurven & Kaplan (2006).

Still genuinely open: Axelrod (1997), Davies et al. (2018, Loihi).

**Suggested resolution:** Run a targeted §15.1 upgrade pass — move resolved entries to `[VERIFIED]` and remove from the "needs entry" table. Retain Axelrod (1997) and Davies et al. (2018) as open items.

---

### C5-5 — MECHANISMS.md §1.2: "Klemm et al. 2003 — not yet in LITERATURE.md" (stale since 2026-06-12 reorg)

**What:** MECHANISMS.md §1.2 inline footnote says Klemm et al. (2003) is "not yet in LITERATURE.md." It has been in LITERATURE.md since the 2026-06-05/06-12 reorg (line ~75).

**Location:** `docs/MECHANISMS.md` §1.2 line ~66: `"[INLINE] Axelrod 1997; Klemm et al. 2003 — cited Stage 1 §1, not yet in LITERATURE.md."`

**Suggested resolution:** Update MECHANISMS.md §1.2 footnote: mark Klemm as `[VERIFIED]`; retain Axelrod 1997 as `[INLINE]`.

---

## Counts summary

| Check | Findings | No-findings |
|---|---|---|
| 1 — Cross-doc contradictions | 4 (C1-1 through C1-4) | — |
| 2 — Stale locked-parameter claims | 2 (C2-1: 5 params; C2-2: 6 terrain constants) | — |
| 3 — Orphan / dangling §-tags | 0 (all tags accounted for) | Clean except C3-1 (stale inline tags) |
| 4 — Single-home violations | 4 (C4-1 through C4-4) | — |
| 5 — Snapshot-drift | 5 (C5-1 through C5-5) | — |

**Total findings: 15** (4 + 2 + 1-adjacent + 4 + 5)

All items are suggestions. No docs were modified.
