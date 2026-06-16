# SiC Games — Directive: Game-Table Locate + State-of-Repo Reconciliation

**Type:** Reconnaissance + buffer-drain. **NOT a build.** No model code changes, no
parameter changes, no wiring. Read, locate, report. The only writes permitted are to
the two non-canonical `context/` files and (if a home is factually wrong vs the working
tree) a `[CONFLICT]` flag — never a silent home edit.

**Why this exists:** the chat side and the committed repo have drifted. A 2026-06-14
handoff describes game-field kcal wiring (Task A1.2), a `SiC_Games_Game_Return_Rate_Table.md`,
a `DEFERRED_MECHANICS.md`, rules 14/15, and a kcal economy — none of which a fresh clone
of the public repo can confirm. This directive establishes ground truth before any wiring
blueprint is written. Do not wire anything. Report only.

---

## §0 Preconditions

1. Run on the supervisor's **local working tree** (which may hold uncommitted files the
   public snapshot lacks), not only on a fresh clone. State explicitly in the report which
   tree was inspected and whether it is clean (`git status --porcelain`).
2. If any check below would require a model-code or home edit to "fix" something, **STOP**
   and report it as a finding instead. This directive changes nothing load-bearing.

---

## §1 Task R1 — Drain the standing handoff line into the buffer

Append the following entry **verbatim** to `context/PENDING_CC.v0.md` under `## Entries`
(append-only; do not edit existing entries except as R2 directs). Use today's date.

```
- [PENDING] <today> | flag | Repo frontier (real, repo-grounded): Phase 1 Stage 1c (largest-lake-body water guard) complete 2026-06-13; continental scope (interior lakes only, no ocean/coast). Next queued model work: prototype forest<->savanna tradeoff verdict (supervisor eyeball), then production terrain-generator blueprint, then wire to world; seasonal/temporal arc after that. Do NOT inherit the earlier phantom "static-game / seasonal-forage / p_female / kcal / 430-tests" handoff — it does not match the repo. Still open: k_pool_cap/tau_parent build-or-cut (deferred to recal-time) and the Stage 6 namespace collision (awaiting supervisor renumber). | home-target: ROADMAP (frontier note) + PARAMETERS §6 (build-or-cut) + ROADMAP (Stage 6 collision)
- [PENDING] <today> | decision | LARGE_BODY_CEILING confirmed = 0.08 (was PROVISIONAL 0.10, Stage 1c). Supervisor eyeball call on ARTIFACT 1 curve. | home-target: PARAMETERS (terrain guards) + ARCHITECTURE §12.1-K + ROADMAP §DECISION-LAKE-BODY-GUARD
```

**Acceptance R1:** both lines present in `context/PENDING_CC.v0.md`; existing entries
untouched except per R2. Failed = blocking STOP (Rule 11).

---

## §2 Task R2 — Update the stale σ_inherit buffer entry

The first buffer entry (σ_inherit, `[PENDING] 2026-06-14 | correction`, marked UNCONFIRMED)
was investigated in chat this session. **Verdict reached:** σ_inherit, locked 0.10, actually
**ran at 0.05** in the Stage 5.2 headline configs (c2 defection gate, Deffuant equivalence
gates); only the Task 3 sweep cells used 0.10. Status: **PARTIALLY UNEXERCISED** — headline
findings rest on the off-spec value. **Decision: PARKED** — caveat to be logged in
PARAMETERS §7; sensitivity re-run deferred to RECAL where σ_inherit is re-derived on the new
substrate anyway.

1. Replace the UNCONFIRMED σ_inherit entry's status with the resolved verdict above
   (keep it `[PENDING]` for the PARAMETERS §7 caveat-write, but change the body from a
   "CC: check YAML" instruction to the **resolved verdict + PARKED decision**).
2. Do **not** run the YAML sensitivity check — it is deferred to RECAL.
3. Confirm whether the PARAMETERS §7 caveat is already written. If not, this is a buffer
   item awaiting drain, not an action for this run.

**Acceptance R2:** σ_inherit entry reflects PARTIALLY-UNEXERCISED / PARKED, not UNCONFIRMED.
Failed = blocking STOP.

---

## §3 Task R3 — Locate the game return-rate table (the central unknown)

A file named `SiC_Games_Game_Return_Rate_Table.md` is referenced by the 2026-06-14 chat
work (Task A1.2) but is **not in the committed public repo**. Find it.

1. Search the **full local tree** (not just the repo dir): the working copy, any synced
   Drive folder, and any output/scratch dirs. Report every path found and the file's
   git status (tracked / untracked / ignored / absent).
2. Search git history across **all refs** for the filename and for distinctive content
   strings (e.g. `Game_Return_Rate`, biome row names, `UNANCHORED`, `Hawkes et al. 1991`,
   `4,653`, `soft-gate`). Note: the public repo is a single squashed "Add files via upload"
   snapshot, so commit-level archaeology may return nothing — say so if so.
3. If found: report its **status column per biome** (LOCKED / PARTIAL / UNANCHORED) and the
   per-biome cell values, verbatim. Do not retype from memory; read the file.
4. If **not found anywhere**: report that explicitly. Do not reconstruct it. The supervisor
   holds the authoritative copy and will upload it.

**Acceptance R3:** report states either (a) the table's path(s) + status/value per biome,
or (b) a clear "absent from all inspected trees and history." No fabricated values.

---

## §4 Task R4 — Game-field ground truth in the live code

Independent of the table, report the **current** state of game in `terrain.py`:

1. Confirm the normalized `game` field expression (lines ~418–419) and its PROVISIONAL
   status (ARCHITECTURE.md §9, line ~79: openness term near-inert; game presently peaks in
   forest, not open ground; rework deferred to Stage 7.2).
2. Confirm whether a `game_kcal` field exists in `WorldFields`. (Working-tree read at
   directive-authoring time: **it does not** — `forage_kcal` is wired, `game_kcal` is
   absent. Verify on the live tree and report any divergence.)
3. Report whether `DEFERRED_MECHANICS.md` exists and, if so, its 7 entries (GD-1, JV-1,
   CC-1, RS-1, MR-1, MR-2, PL-1). If absent, say so.
4. Report whether CLAUDE.md **rules 14/15** (buffer-drain + fact-file regeneration) are
   actually written in `sic_games/CLAUDE.md`. (Author-time read: **not found** — only
   rules 1–13 referenced. Verify.)

**Acceptance R4:** report covers game expression + PROVISIONAL status, `game_kcal`
presence/absence, `DEFERRED_MECHANICS.md` presence/contents, rules 14/15 presence. Each is a
yes/no-with-evidence, not an assumption.

---

## §5 Task R5 — Reconcile the A1.2 substrate divergence

The 2026-06-14 work targeted `world/terrain.py` / `WorldFields.game_kcal`; the live tree has
`src/sic_games/terrain.py` with `WorldFields` **and** `TerrainFields` in one module and no
`game_kcal`. Determine the truth:

1. Is there a `world/` package distinct from `src/sic_games/`? If so, which is the live
   import path the model actually runs? Report both and which `generate_world` / `WorldFields`
   is canonical.
2. State plainly: **did Task A1.2 (game_kcal wiring) ever land in the live tree, or not?**
   Evidence-based yes/no.

**Acceptance R5:** unambiguous statement of which terrain module is live and whether A1.2
landed. Failed = blocking STOP.

---

## §6 Must-be-seen report (the only output)

This directive's deliverable is a **single short status report** in chat — no green-only
shortcut, because the whole point is a state map the supervisor must read. Structure:

1. **Tree inspected** (path, clean/dirty).
2. **Game table:** found-where (+ per-biome status/values) OR absent.
3. **game_kcal:** present / absent in live `WorldFields`.
4. **A1.2 verdict:** landed / never-landed, with evidence.
5. **Live terrain module:** `src/sic_games/terrain.py` vs any `world/terrain.py`.
6. **DEFERRED_MECHANICS.md and rules 14/15:** present / absent.
7. **Buffer:** R1 lines appended, R2 σ_inherit entry updated — confirm.
8. **One-line recommendation:** what the next blueprint should be, given the above
   (e.g. "supervisor uploads table → wire game_kcal" vs "table absent, rebuild from
   LITERATURE anchors" vs "A1.2 already landed, this is a no-op").

**Stopping rule:** stop after the report. Do not wire `game_kcal`. Do not edit homes. Do not
run sims. Any failed acceptance check above is a blocking STOP per CLAUDE.md Rule 11.
