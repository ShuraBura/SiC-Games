# SiC Games — Unified Directive: Commit Blueprint A, then Game-Table Derivation + Reconciliation

**Type:** Mixed. §1 is a git operation (supervisor-gated). §2–§5 are a documentation +
constant-reconciliation pass with explicit arithmetic — **not** a model-behaviour change
(the `game_kcal` field already exists and is wired; this makes its values traceable and
fixes one miscategorisation). No sim runs except the pytest gate in §1. The game table is
the **authoritative home** for every game cell value; `GAME_KCAL_TARGETS` in `terrain.py`
must become a lookup that *follows* the table, never leads it.

Run §1 to completion and **STOP for supervisor** before §2 only if pytest is red or the
working tree contains changes you cannot account for. Otherwise proceed straight through.

---

## §1 — Commit Blueprint A (close the chat↔repo drift)

The Blueprint A work (game return-rate table, `DEFERRED_MECHANICS.md`, CLAUDE.md rules
14/15, `game_kcal` wiring across `terrain.py` / `terrain_field.py` / `phase1_model.py`,
context buffer updates) is landed but **uncommitted**. Until it commits, every fresh chat
clones a stale snapshot and re-derives the same confusion.

1. Show `git status` and `git diff --stat`. List every changed/untracked file.
2. Run `pytest`; report pass/fail counts. **This is the verification of the unconfirmed
   "430 tests" claim.** If any test fails → **STOP, report, do not commit.**
3. For each changed file you are **not** committing, name it and say why.
4. Stage the Blueprint A artifacts + the context-sync buffer updates. Commit as ONE commit:
   `Phase 1: game_kcal wiring + game return-rate table + context-sync rules 14/15 (Blueprint A)`
5. Push to origin. Report commit hash + pytest result.

**Acceptance §1:** clean commit pushed; pytest green; hash + count reported; no unaccounted
files swept in. Red tests or unexplained changes = blocking STOP (Rule 11).

---

## §2 — Game table: show the arithmetic for every representative value

**Problem:** the forage table shows its derivation per cell (e.g. savanna prints
`1.02 × 0.50 × 1460 = 744.6`). The game table currently states *conclusions*
("mean of 7 species", "mid-range") without the working, so `GAME_KCAL_TARGETS` reads as
picked constants. Fix: each biome's **representative value** (the single number that feeds
`GAME_KCAL_TARGETS`) must be derived in-table with explicit arithmetic, in a new
**"Representative-value derivation"** subsection per biome — mirroring the forage table's
per-cell working. Read source values from the table's own cells / cited tables; do not
retype from memory.

Per-biome method (locked / to-resolve):

| Biome | Representative-value method | Status |
|---|---|---|
| **Forest** | **Encounter-rate-weighted mean** across the 7 Hill 1987 Table 2 species **if** Table 2 reports encounter frequencies/rates; **else median** of the 7 post-encounter rates (resists the high-value tail — a flat mean of a 1,370–15,398 spread overstates typical yield). Show the weights or the ranked list + median pick. | **LOCKED (supervisor)** |
| **Desert** | **TO RESOLVE — see §3.** Do not keep the bare midpoint 1,201 without justification. | OPEN |
| **Savanna** | State which Hawkes 1991 figure is the static cell: base (~518) or dry-season intercept (~745), or a documented blend. Pick one, show why. Flag the dry-season figure as a future seasonality hook, not the static value, unless supervisor says otherwise. | derive + flag |
| **Grassland** | 3,001 (Hurtado & Hill 1987) — single source, no spread; state it's a direct lift, no arithmetic needed. | direct |
| **Desert/other LOCKED cells** | Where a range is collapsed, show the collapse rule explicitly. | derive |
| **Wetland / Mountain** | UNANCHORED → `game_kcal = 0`. State the zero is a *gap*, not a measured zero. | n/a |

Every derived representative value carries its tag (`[NATIVE]`/`[CONVERTED]`) and the
`[PROVISIONAL — pending CC-1 ceiling]` flag until CC-1 lands. The derivation subsection is
the authoritative source for the matching `GAME_KCAL_TARGETS` constant (§5).

**Acceptance §2:** every biome feeding `GAME_KCAL_TARGETS` has an in-table derivation
subsection showing the arithmetic/selection rule. Forest uses encounter-weighted-mean (or
median with stated reason). No representative value exists only as a code comment.

---

## §3 — Desert representative value: track it down

Supervisor deferred the desert method to CC. The cell is currently a bare midpoint 1,201 of
the 641–1,761 Bird 2009 (Martu) species range.

1. Read Bird et al. 2009 Figure 4 (the in-project PDF — page image, not OCR). Report the
   per-species post-encounter rates actually plotted (hill kangaroo, sand monitor, perentie,
   bustard, python, +others).
2. Check whether the source gives **encounter rates / relative frequencies** per species. If
   yes → propose an **encounter-weighted mean** (same logic as forest). If no → propose the
   defensible collapse: median over the species, or a stated reason for the midpoint.
3. Cross-check O'Connell & Hawkes 1984 (Alyawara) sandplain ~3,200 / mulga ~650 only as a
   *patch-level aggregate* sanity band — do not let the mixed forage+small-game patch figure
   override the Martu species-resolved value.
4. **Report the proposed desert value + method back in the must-be-seen report; do NOT lock
   it.** Supervisor confirms before it enters `GAME_KCAL_TARGETS`. Until confirmed, leave the
   constant at its current value tagged `[PROVISIONAL — desert method pending supervisor]`.

**Acceptance §3:** desert per-species values reported from the figure; a method proposed
with evidence; value left PROVISIONAL pending supervisor, not silently changed.

---

## §4 — Intertidal: reclassify from game to forage (fix the double-count)

**Error:** the game table carries Intertidal as a LOCKED game row (4,653, Bliege Bird 2001).
Intertidal shellfishing is **forage**, already anchored in the forage table (Bird 1997
Meriam) and applied in code as `SHORE_BONUS_KCAL = 1491.5` on `forage_kcal`. Holding it as a
game cell **double-counts the same activity** across both fields and miscategorises it.

1. In the game table, **strike the Intertidal game row** and replace it with a pointer:
   `Intertidal — NOT GAME. Intertidal foraging (shellfishing) is forage; see forage table
   (Bird 1997) and SHORE_BONUS_KCAL in terrain.py. Excluded from the game field.` Preserve
   the Bliege Bird 2001 citation as a struck/footnoted cross-reference so the provenance
   isn't lost, with its existing caveat (gross pre-sharing, net ≈ 0).
2. Confirm `GAME_KCAL_TARGETS` does **not** contain an intertidal entry (author-time read:
   it correctly omits it). If present, remove it. Code is currently correct on this; the
   table is wrong — reconcile **toward forage**.
3. Add a one-line note in the table preamble: forage vs game category boundary — intertidal,
   roots, tubers, plant resources = forage; terrestrial vertebrate prey = game.

**Acceptance §4:** game table has no LOCKED intertidal game cell (pointer-to-forage only);
`GAME_KCAL_TARGETS` has no intertidal key; citation provenance preserved as cross-reference.

---

## §5 — Reconcile `GAME_KCAL_TARGETS` to the derived table

After §2–§4, make the code follow the table.

1. For each biome key in `GAME_KCAL_TARGETS` (`terrain.py:54`), set the value to the §2/§3
   derived representative value, with an inline comment pointing to the table's derivation
   subsection (mirror how `FORAGE_KCAL_TARGETS:41` cites its sources). Desert stays at its
   current PROVISIONAL value until supervisor confirms §3 — comment it as such.
2. Where a constant changes, the comment states old→new and why (e.g.
   `Forest 7749.0 → <new>  # flat-mean → encounter-weighted-mean per table §F.x`).
3. Do **not** change the `game_kcal` *computation* (biome mean-scaling) — only the target
   constants it scales toward. This is a value-reconciliation, not a mechanic change.
4. Re-run `pytest`. Any game/terrain test asserting old constant values must be updated to
   the table-derived values **and the change noted** (grep-before-fix per CLAUDE.md). If a
   test breaks for any reason other than the intended constant change → STOP and report.

**Acceptance §5:** every `GAME_KCAL_TARGETS` value traces by comment to a table derivation
subsection; changed constants annotated old→new; pytest green; no mechanic change.

---

## §6 — Doc-update + buffer drain (definition-of-done)

1. **PARAMETERS / ARCHITECTURE §9.x:** wherever `GAME_KCAL_TARGETS` is documented, point the
   values' home at the game table's derivation subsections (one-fact-one-home).
2. **Drain the buffer:** the LARGE_BODY_CEILING = 0.08 decision and the σ_inherit
   PARTIALLY-UNEXERCISED/PARKED verdict (already appended) — drain into their homes
   (PARAMETERS / ARCH §12.1-K / ROADMAP §DECISION-LAKE-BODY-GUARD; PARAMETERS §7) and mark
   the buffer entries `[DRAINED <date>]`. Per rule 15, regenerate the fact-file if any home
   changed and prompt re-upload.
3. Register the **intertidal reclassification** and the **forest/desert representative-value
   method** as decisions in their homes (not left in chat).
4. Commit §2–§6 as a second commit:
   `Phase 1: game-table representative-value derivations + intertidal→forage reclass + GAME_KCAL_TARGETS reconcile`.
   Push. Report hash.

**Acceptance §6:** homes updated; buffer entries drained/marked; fact-file regenerated if
needed; second commit pushed.

---

## §7 — Must-be-seen report (the only prose output)

A green acceptance run needs no narrative **except** these shape/judgment items the
supervisor must see and rule on:

1. **Forest representative value:** the method used (weighted-mean vs median), the
   weights/ranked list, and the resulting number — old 7,749 → new.
2. **Desert proposal (§3):** per-species figure values + proposed method + proposed value,
   **left PROVISIONAL** for supervisor confirmation.
3. **Savanna:** which figure (base/dry) became the static cell, and why.
4. **pytest:** result for both commits.
5. **Anything that broke or surprised.**

Everything else (intertidal reclass, constant reconciliation, buffer drain) is assertable —
report one-line green per section. Stop after the report.

**Stopping rules:** red pytest at §1 → STOP before §2. Desert value is **proposed not
locked** — never auto-commit a supervisor-deferred value as final. Any non-intended test
break → STOP. Failed acceptance = blocking STOP (CLAUDE.md Rule 11).
