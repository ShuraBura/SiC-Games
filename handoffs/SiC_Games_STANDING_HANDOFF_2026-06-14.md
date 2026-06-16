# SiC Games — Standing Handoff (2026-06-14)

This document is written for a cold agent or a returning supervisor who needs to orient
quickly. It contains: project identity, file locations, CC's maintenance duties, current
state, open items, and ground rules. Read in order.

---

## 1. Project identity

**SiC Games** is an agent-based model (Python / Mesa + Pydantic, tested with pytest) that
compares two civilizational archetypes under ecological resource pressure:

- **C (Carbon):** hierarchical, status-seeking, high-variance extractors.
- **Si (Silicon):** egalitarian, bounded-rational, cooperation-oriented.

**Core hypothesis H1(ii):** Si out-resiliences C in the long run despite C's apparent
short-run advantages. Both types compete on the same terrain substrate; the simulation
tests whether cooperation norms and egalitarian sharing survive ecological volatility better
than hierarchy.

**Design philosophy:** covariance through shared cause — terrain primitives (elevation →
water flow → derived fields) generate emergent forager/hunter spatial specialization rather
than painting it in. The model is built to be legible and falsifiable; every mechanism is
literature-grounded or explicitly UNANCHORED.

---

## 2. Where the project lives

| Location | Path |
|---|---|
| **Main repo (working tree)** | `C:\Users\syatom\Projects\SiC Games\` |
| **Literature PDFs** | `G:\My Drive\docs\SiC Games Docs\lit\` |
| **Python executable** | `C:\Users\syatom\AppData\Local\Python\bin\python.exe` (v3.14.3) |
| **CC memory** | `C:\Users\syatom\.claude\projects\C--Users-syatom-AppData-Roaming-Microsoft-Windows-Start-Menu-Programs-Git\memory\` |

**GitHub remote:** May exist (the 2026-06-09 infrastructure flag notes "git's GitHub remote
is already the cross-machine sync") but the URL has never been confirmed to CC. Do NOT
assume a remote exists; verify with `git remote -v` before pushing anything.

**Infrastructure warning (from 2026-06-09 handoff):** The repo sits inside a Google-Drive-
synced folder. Drive is live-syncing `.git/`, which risks corruption and conflict copies
(`ROADMAP (1).md` disease has already struck once). Access has been serialized so far.
Recommended fix: move working tree to a non-synced local path; GitHub remote is the real
cross-machine sync. This is deliberate surgery — do it with CC walking through it live, not
casually.

---

## 3. Tech stack

| Layer | Tool |
|---|---|
| Agent framework | Mesa (Python) |
| Config / validation | Pydantic |
| Tests | pytest |
| PDF extraction | pdfplumber (installed 2026-06-14) |
| Python version | 3.14.3 |

Run tests: `python -m pytest` from the repo root (or `C:\Users\syatom\AppData\Local\Python\bin\python.exe -m pytest`).

---

## 4. Files CC routinely maintains

These are the **11 authoritative homes** (see `docs/INDEX.md` for the routing table). CC
updates each one on the trigger listed.

| File | Update trigger |
|---|---|
| `docs/ROADMAP.md` | End of every stage or directive |
| `docs/ARTIFACTS.md` | Every run, report, or diagnostic emitted |
| `docs/LITERATURE.md` | Every source consulted (full read) or explicitly rejected |
| `docs/PARAMETERS.md` | Every parameter lock, sweep, or retirement |
| `docs/ARCHITECTURE.md` | Seam/decomposition/world-substrate change; design decision taken |
| `docs/MECHANISMS.md` | Construct introduced or redefined; lock-status change |
| `docs/HYPOTHESES.md` | Before any analysis that could HARK; on resolution |
| `docs/RESULTS.md` | When a finding is established (append-only) |
| `docs/INDEX.md` | When a document is added or retired |
| `docs/MODEL_SPEC.md` | Resource-layer formula, denominator rule, or seasonal seam changes |
| `docs/SiC_Games_Game_Return_Rate_Table.md` | Game biome cell anchored, updated, or UNANCHORED policy changes |
| `sic_games/CLAUDE.md` | Any code change; the master agent contract |

**Single-home discipline (mandatory):** one fact, one home; everywhere else is a pointer.
If the same value appears in two documents, one is wrong. Do not duplicate; cross-reference.

---

## 5. Reading order for a cold agent

Read these in sequence before touching any file:

1. **`docs/INDEX.md`** — routing table; tells you which document owns which fact.
2. **`sic_games/CLAUDE.md`** — master agent contract; behavioral rules for CC.
3. **`docs/ROADMAP.md`** — where the project is and what comes next.
4. **`docs/ARCHITECTURE.md`** — system structure, seams, decision log.
5. **`docs/MODEL_SPEC.md`** — resource-layer methodology (new 2026-06-14); formula, constants, seasonal seams, unanchored-cell policy.
6. **`docs/SiC_Games_Game_Return_Rate_Table.md`** — game return-rate table (new 2026-06-14); all biome cells, forest species sub-table.

For literature context: **`docs/LITERATURE.md`** (large; ctrl-F to the section you need).

---

## 6. Current state (as of 2026-06-14)

### Phase / Stage

- **Phase 0** (flat Sugarscape substrate): complete and archived.
- **Phase 1** (terrain-grounded substrate): in progress.
  - Stage 7 (terrain generator + F5 patch + J&H 2016 integration): COMPLETE 2026-06-11.
  - Phase 1 Stage 1 (ForageField + TerrainDiagnostics): GATE GREEN 2026-06-13.
  - Phase 1 Stage 1c (largest-lake-body guard): COMPLETE 2026-06-13.
  - **Current position: between Stage 1c and Stage 2. Stage 2 not yet started.**

### Test suite

404 tests passing (as of 2026-06-13). No tests were added in the 2026-06-14 session
(that session was documents-only).

### What this session completed (2026-06-14)

Blueprint `SiC_Games_BP_Game_Return_Rate_Table_v2.md` — all three tasks complete:

**Task 1 — LITERATURE.md Survey B:**
- Amended 3 existing entries (Hill 1987 game role, Hurtado & Hill 1987 game role, Morin 2024 clarification).
- Appended new section "## Survey B: Game Return-Rate Sources" with 9 entries:
  Hawkes et al. 1991, Bird et al. 2009, Bliege Bird et al. 2001, Smith & Bliege Bird 2000,
  Hill et al. 1997 (negative), Gurven & Hill 2009 (negative), Redford & Robinson 1987 (negative),
  Ugan & Simms 2012 (methodological), Janssen & Hill 2014 (corrected finding noted).
- Mandatory costly-signaling caveat on Bliege Bird 2001 (hunters retain no meat; gross rate only).
- No [VERIFIED] tags added (none of the new entries had prior [VERIFIED] status).

**Task 2 — `docs/SiC_Games_Game_Return_Rate_Table.md` (NEW FILE):**
- §F.1 Methodology: formula, constants, denominator rule, NATIVE/CONVERTED, UNANCHORED policy, fat-season multiplier.
- §F.2 Main table: 8 biome rows (Forest LOCKED, Savanna LOCKED, Grassland LOCKED, Desert LOCKED, Wetland UNANCHORED, Mountain UNANCHORED permanent, Intertidal LOCKED with mandatory caveat, Open water ZERO — model scope).
- §F.3 Forest species sub-table: 7 species from Hill 1987 Table 2, extracted via pdfplumber from `G:\My Drive\docs\SiC Games Docs\lit\SiC_Games_A1.1_Hill1987_AcheForaging.pdf`.
- §F.4 Savanna soft-gate note (sigmoid, not step-function; grounded in Morin 2024).
- §F.5 Source list with role tags.

**Task 3 — `docs/MODEL_SPEC.md` (NEW FILE):**
- Scoped to resource-layer methodology only; does NOT reconstitute former MODEL_SPEC v0.2
  (split into ARCHITECTURE + MECHANISMS 2026-06-06; archived at `archive/superseded/`).
- §4.1.1 Formula and constants.
- §4.1.2 NATIVE/CONVERTED; forest construct-seam (handling-only denominator documented, harmonisation prohibited without primary-source replacement).
- §4.1.3 UNANCHORED cells policy.
- §4.1.4 Forage seasonal signal (phenomenological; biome anchors: Ache flat, Hiwi high, Hadza moderate, De Vynck 2016 moderate).
- §4.1.5 Game seasonal signal (two mechanisms: value-via-fat for forest; access-via-aggregation for savanna/llanos — must not be collapsed into one sine).
- §4.1.6 Star-mechanics seam (amplitude is the ONLY coupling point; no insolation→NPP transfer function inside agent loop).
- §4.1.7 Climate catastrophe seam STUB (interface defined; writes to amplitude modifier only; must not touch cell values, biome assignments, or agent state).

**INDEX.md updated:** routing rows added for MODEL_SPEC.md and SiC_Games_Game_Return_Rate_Table.md; Phase 1 resource-layer routing block (11 rows) added.

### Locked resource-layer constants

| Constant | Value | Source | Status |
|---|---|---|---|
| edible_fraction | 0.50 | Hurtado & Hill 1987 | LOCKED |
| energy_density | 1,460 kcal/kg | Hill et al. 1987, fn 3 | LOCKED |
| mtn_ceiling | 0.317 | Terrain generator | Pre-registered |
| LARGE_BODY_CEILING | 0.10 | Stage 1c | Provisional |

Authoritative values in `docs/PARAMETERS.md`.

---

## 7. Open items

### OWE (Open Work Entries) — pre-existing, not started

| ID | Description |
|---|---|
| **OWE-9** | σ_inherit corrective sweep — ≥8 seeds targeting c1/c2 diversity |
| **OWE-14** | H1(ii) re-test at calibrated N_carry=4100, ≥3 seeds (pre-registered) |
| **OWE-4** | Davies et al. 2018 (Loihi) LITERATURE.md entry needed to upgrade [INLINE]→[VERIFIED] in ARCHITECTURE.md §15.1 |

### Citation debts — [INLINE] citations that need LITERATURE.md entries

These citations appear in MODEL_SPEC.md §4.1.6 and §4.1.7 but are not yet in LITERATURE.md:
- Berger 1978 (orbital parameters — obliquity/eccentricity)
- Spiegel 2009/2010 (stellar/planetary habitability)
- Kopparapu 2013 (habitable zone)
- Kasting 1993 (habitable zone)
- Timmermann 2018, Cane 2005, Cook 2010, Sigl 2015, Wanner 2008, Mayewski 2004 (shock distribution — in §4.1.7 STUB)

These can be deferred until the seasonal-amplitude build stage is scheduled, but they exist as
acknowledged debts.

### UNANCHORED game cells

| Biome | Status | Note |
|---|---|---|
| Wetland | UNANCHORED (current) | Three candidates checked, all negative for kcal/hr. Gap accepted; zero yield at model-build time. |
| Mountain | UNANCHORED (permanent) | No HG literature for mountain-specific game return rates. |

---

## 8. Key resource-layer facts a cold agent must not re-derive

- **Formula:** `kcal/hr = mass_live_per_hr × 0.50 × 1,460` for CONVERTED cells only.
- **Forest construct seam:** Hill 1987 Table 2 uses handling-only denominator (pursuit attempts + processing; search excluded). All other biomes search-inclusive. This asymmetry is accepted — do NOT harmonise without a replacement primary source and supervisor approval.
- **Forest game:** [NATIVE] — 7 species from Table 2; range 1,370–15,398 kcal/hr. Capuchin (1,370) is lowest-ranked. Red brocket deer (15,398) is highest. Tapir is hunted but absent from Table 2 (insufficient sample).
- **Savanna game:** [CONVERTED] from Hawkes 1991 kg/hr data — 518 kcal/hr (encounter, all seasons); 745 kcal/hr (intercept, dry season only at water aggregation sites). Group-size modifier is a sigmoid (soft gate), NOT a step function.
- **Grassland:** [NATIVE] 3,001 kcal/hr from Hurtado & Hill 1987 (whole-activity, search-inclusive). Corroborated ~2,700 kcal/hr by Gurven & Hill 2009.
- **Desert:** [NATIVE] 641–1,761 kcal/hr by species from Bird et al. 2009 Table 1.
- **Intertidal:** [NATIVE] 4,653 ± 1,213 kcal/hr from Bliege Bird 2001 — **MANDATORY CAVEAT:** costly-signaling context; hunters retain no meat; gross rate only. Net hunter yield ≈ 0.
- **Two game seasonal mechanisms (must not be collapsed):**
  - Value-via-fat (forest): ×1.25 multiplier Apr–Jun on kill value; not applied to static cells.
  - Access-via-aggregation (savanna/llanos): threshold-like on encounter rate; switches on at dry-season water concentration (intercept hunting).
- **Star-mechanics seam:** seasonal amplitude is the ONLY coupling between orbital/stellar parameters and resource curves. No insolation→NPP→forage transfer function inside the agent loop.

---

## 9. Ground rules (from CLAUDE.md / DOCS_CHARTER)

1. **No [VERIFIED] tags on new entries** unless the entry already had [VERIFIED] in the
   existing file. Verification requires full-text read of the source and explicit note.
2. **No fabricated values.** UNANCHORED cells get `—` in the table, not a guess.
3. **Single-home discipline.** One fact, one home; everywhere else is a pointer. If you
   update a parameter value, update PARAMETERS.md — not ROADMAP, not MECHANISMS.
4. **Append-only logs.** HYPOTHESES.md, RESULTS.md, DEAD_ENDS.md: supersede with a dated
   note; never silently delete.
5. **Edit efficiency.** Plan all edits to a file before touching it. Batch into one Edit
   call or use Write for small files. Do NOT make 4 sequential Edit calls on the same file.
6. **No model runs during documentation directives** (Blueprint tasks). Documentation is
   separate from simulation runs.
7. **Hard STOP on gate failure.** If a blueprint acceptance gate cannot be met (missing
   data, missing source), file a BLOCKED report and wait for supervisor resolution.

---

## 10. What comes next (from ROADMAP.md perspective)

Stage 2 (seasonal/migration mechanics) is the next scheduled stage. Before Stage 2 begins,
the supervisor may want to:
- Resolve the OWEs above (OWE-9, OWE-14 are simulation runs; OWE-4 is a doc task).
- Fill the [INLINE] citation debts in MODEL_SPEC.md.
- Confirm Stage 2 scope (which seasonal mechanisms to implement first: fat-value vs.
  access-via-aggregation; game-migration vs. modulated-in-place density).

The savanna gate-shape design question (step-then-plateau vs. Janssen & Hill 2014 smooth
7–8 optimum) was marked unresolved in the 2026-06-09 handoff and is still live.

---

*End of standing handoff. Written 2026-06-14.*
