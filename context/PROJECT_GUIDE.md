# SiC Games — PROJECT GUIDE (START HERE)

> **Read this first.** This is the one-stop orientation for the SiC Games project: what it is, where it stands, what every document holds, the rules you must not break, a glossary, and how to plan a blueprint. It is **derived / non-authoritative** (it lives in `context/`, not the charter homes) — it *explains and points*, it does not own facts. On any conflict, the `docs/` homes win.
>
> **Companion files in `context/`:** `CANONICAL_FACTS.md` (the live current-state fact cache — read it right after this), `PENDING_CC.md` (chat-side decisions not yet drained into homes). **Last guide update: 2026-06-15.**

---

## 1. The 60-second orientation

**SiC Games is an agent-based model (Python / Mesa) comparing two civilization types on matched worlds:**
- **C (Carbon)** — hierarchical / status-driven. Decision noise is coupled to **Cred** (status earned from joint tasks); biparental reproduction; status-mediated support.
- **Si (Silicon)** — egalitarian / individualist. Fixed decision noise; single-parent fission; reciprocal (non-status) support; a dormancy survival mechanic.

**Central question — H1(ii):** which strategy is more resilient to periodic resource shocks? *(Phase 0 Sugarscape result: inverted — C survived, Si collapsed, robust 5/5 seeds at A=0.75/T=200. This is NOT yet re-confirmed on the Phase 1 terrain substrate — see HYPOTHESES `§H1ii-RETEST` / RESULTS `R-1`.)*

**The arc:** Phase 0 built all the social mechanics on the Epstein & Axtell **Sugarscape** sugar grid (Stages 1–7.5, complete 2026-06-11). Phase 1 replaces the sugar scaffolding with a **terrain-driven resource ecology** (real biomes, kcal economy) while keeping the social apparatus, then re-validates H1(ii) on it.

**The human supervisor directs the science; the coding agent (CC) implements blueprints exactly and never changes science without explicit approval.**

---

## 2. Where the project stands  →  read `context/CANONICAL_FACTS.md` for the live detail

This section is a stable pointer, not a status feed (status lives in CANONICAL_FACTS + ROADMAP, which are kept current). As of the last guide update:
- **Frontier:** Phase 1. Terrain generator built (Stage 7) and validated; ForageField + water-guard diagnostics (Stages 1/1b/1c) done; **Blueprint A** (agent↔terrain migration + kcal economy + static game) complete and committed.
- **Resource layer:** each biome's `forage_kcal` / `game_kcal` cell is drawn from a **literature-anchored lognormal (mean, std)**, terrain-coupled and deterministic (MECHANISMS §9a.6).
- **Next up (per ROADMAP):** A-3 performance audit, then seasonal-forage; the H1(ii) re-confirmation (OWE-14) is deferred pending the substrate work.

> If this paragraph and CANONICAL_FACTS/ROADMAP ever disagree, **CANONICAL_FACTS/ROADMAP win** — and that's a signal this guide's §2 needs a refresh.

---

## 3. The locked spine (do not re-litigate these)

These are standing invariants. Changing any of them requires explicit supervisor approval and usually a full recalibration.

| Invariant | Value | Home |
|---|---|---|
| Temporal resolution | **1 step = 1 month** | PARAMETERS §1 / ARCH §9.3 |
| Grid | **100×100 cells**, 1 cell ≈ **100 km²** (10×10 km) | PARAMETERS §1 / ARCH §9.3 |
| Substrate lineage | Sugarscape (Phase 0 scaffolding) → terrain forage/game fields (Phase 1) | ARCH §9 / ROADMAP phase boundary |
| C vs Si mechanics | **Different civilizations** — never assign a C mechanic to Si or vice-versa | ROADMAP "C/Si distinction table" |
| Economy | **kcal** reserve (C); burn 75,000 kcal/step; the Sugarscape sugar economy is DORMANT-SUPERSEDED-FOR-C | PARAMETERS §13 / ARCH §12.1-L |
| Determinism | same `(knobs, seedStr)` → byte-identical terrain; equivalence gate before any non-science refactor | CLAUDE.md rules 2 & 13 |

---

## 4. The documentation system — every document explained

**The model:** one fact has exactly **one home**. Every other mention is a pointer. There are **11 authoritative charter homes** under `docs/`, plus a few derived views, a non-canonical `context/` layer, and governance files. If you find the same fact stated in two places, one is a bug.

### 4.1 The 11 charter homes (authoritative — `docs/`)

| Home | Owns | How it's structured | Read it when… |
|---|---|---|---|
| **INDEX.md** | The routing table (which home owns which kind of fact) | A "if your question is about X → go to Y" table + doc registry | You don't know where a fact lives |
| **ROADMAP.md** | Stage sequence, status, deferred items, open questions (Q-list), owed-items (OWE) backlog, phase boundary | Phase/stage sections + status table + Q-list + OWE table; append decisions | "Where are we / what's next / what was deferred" |
| **ARCHITECTURE.md** | System structure: §0 principle, §9 world/terrain substrate, **§12 decision-log (append-only, dated)**, §13 seams, §15 known-gaps | Numbered sections; §12.1-A…N is the dated decision log | A design decision, a seam, how the world is built |
| **MECHANISMS.md** | Per-construct definitions (the rules/equations), C/Si classification, §9a kcal economy, §14 param index | §0 classification, §1–§11 constructs, §9a Phase-1 economy | "How does mechanic X actually work" |
| **PARAMETERS.md** | The authoritative value + lock/sweep/retire history of **every** parameter | §1–§13 by mechanism; discrepancy-resolution log at end | Any parameter value, lock date, or status |
| **TARGETS.md** | Aspirations not yet falsifiable (graduate to HYPOTHESES when test-specced) | T-1, T-2, T-3 entries | "What do we hope to show (no test yet)" |
| **HYPOTHESES.md** | Pre-registrations + resolution status (falsifiable, test-specced) | Append-only; H-EMERGE-1, §H1ii-RETEST, H_cc, … | Before any analysis that could HARK; on resolution |
| **RESULTS.md** | Established findings, in prose | Append-only findings ledger (R-1, …) | "What do we actually know" |
| **ARTIFACTS.md** | Index of every report/benchmark/diagnostic + location + headline | One row per artifact; phase sections | "Where is the run that showed X" |
| **LITERATURE.md** | Citations: what was lifted, what rejected, why; Survey A/B | Bibliography + survey sections + tags | Grounding a mechanic / checking a source |
| **DEAD_ENDS.md** | Retired directions + why each was abandoned | Append-only (DE-1, …) | "Did we try X already; why was it dropped" |

### 4.2 Derived views & resource-layer docs (`docs/`)

| Doc | Owns | Note |
|---|---|---|
| **MODEL_SPEC.md** | Resource-layer methodology: kcal formula, edible_fraction/energy_density, denominator rules, UNANCHORED policy, seasonal-signal architecture | §4.1.x; the "how literature → resource inputs" record |
| **SiC_Games_Resource_Return_Rate_Table.md** | **The exhaustive resource table (forage + game).** §1 shared methodology, §2 forage (mean/std/derivations), §3 game (mean/std/derivations, per-species), §4 combined source list. Feeds `FORAGE/GAME_KCAL_TARGETS` + `_STD` | Derived view; LITERATURE.md owns citations, PARAMETERS owns the value mirror. (Former game-only table retired → stub redirect.) |
| **DEFERRED_MECHANICS.md** | The 7 agreed-but-deferred mechanics (seam + literature anchor + status) | GD-1, JV-1, CC-1, RS-1, MR-1, MR-2, PL-1 |

*(Forage + game return values are now consolidated in the unified Resource Return-Rate Table above, with the value mirror in PARAMETERS §12.4 (forage) / §13.3 (game) and the constants in `terrain.py`.)*

### 4.3 The `context/` layer (non-canonical — bridges chat-to-chat)

| File | Purpose | Discipline |
|---|---|---|
| **PROJECT_GUIDE.md** (this file) | Stable orientation: doc-map, locked spine, glossary, how-to-plan | Update when the doc system or workflow changes |
| **CANONICAL_FACTS.md** | Live projection (cache) of the homes' current state; every line `→ home` | Regenerated by CC whenever a run changes a projected fact; **re-uploaded to project knowledge** (CLAUDE.md rule 15) |
| **PENDING_CC.md** | Append-only buffer of chat-side decisions not yet drained into a home | Drained at the start of every run (CLAUDE.md rule 14); entries struck `[DRAINED]`, never deleted |
| **README.md** | States that `context/` is derived / non-authoritative | — |

### 4.4 Governance & the agent contract

- **`docs/DOCS_CHARTER.md`** — the governance document the home system implements (closed set of homes, single-home discipline).
- **`sic_games/CLAUDE.md`** — the coding-agent contract: **15 standing rules** (science-change approval, equivalence gate, test-after-change, citation tags, phase disambiguation, failed-gate-STOP, buffer-drain, fact-file-regen) + **report rules R1–R7** (terminal-state accounting, gate-vs-finding separation, anomalies section, synthesis).

---

## 5. How to navigate for a task (recipes)

| You want to… | Read, in order |
|---|---|
| Get oriented from cold | This guide → `CANONICAL_FACTS.md` → `PENDING_CC.md` |
| Know a parameter's value/history | `PARAMETERS.md` (search the symbol) |
| Understand how a mechanic works | `MECHANISMS.md` (construct) → `ARCHITECTURE.md` §12 (why it's built that way) |
| See what's next / deferred | `ROADMAP.md` (status table, Q-list, OWE backlog) + `DEFERRED_MECHANICS.md` |
| Find a past result/run | `ARTIFACTS.md` (location) → `RESULTS.md` (the finding) |
| Check a hypothesis status | `HYPOTHESES.md` |
| Ground a number in literature | `LITERATURE.md` + the relevant return-rate table / `MODEL_SPEC.md` |
| Check what was already abandoned | `DEAD_ENDS.md` |

---

## 6. How to plan a blueprint (conventions)

A blueprint is a supervisor directive CC executes exactly. Strong blueprints follow the project's discipline:
1. **Pre-register** the hypothesis/acceptance before running (HYPOTHESES.md), so results can't be HARKed.
2. **Gate-first:** define explicit pass/fail *rails* and confirm them as a *blocking* checkpoint before the gated run (CLAUDE.md rule 13 — a failed gate is a STOP, not a judgment call).
3. **One new parameter per stage**, with a pre-committed calibration target + acceptance check (no free knob-tuning).
4. **Tag provenance:** `[VERIFIED]`/`[SECONDARY]`/`[INLINE]`/`[UNVERIFIED]` for citations; `[PROVISIONAL]`/`[PLACEHOLDER]`/`[NOMINAL]` for values; never fabricate — UNANCHORED cells get `—`.
5. **Respect the C/Si distinction** (check the ROADMAP table before any mechanic).
6. **Definition of done** spells out: gate green + all blocks green + doc-home updates applied + all provisional values tagged + existing suite green.
7. **Reports** obey R1–R7 (terminal-state row per seed, gate-vs-finding sentence, magnitudes not just direction, an Anomalies section, a synthesis).

When drafting a blueprint in chat, pull current state from CANONICAL_FACTS (not memory), name the home each change will update, and list the seams it touches (DEFERRED_MECHANICS.md).

---

## 7. Glossary (the terms that cost catch-up time)

- **C / Si** — the two civilizations (Carbon/hierarchical, Silicon/egalitarian). Run on *matched* worlds, never mixed.
- **Cred (𝒞)** — C-only status capital from joint tasks; drives C's decision noise σ and reproduction. Si has a separate near-dormancy Cred (Stage 5.1).
- **H1(ii)** — the resilience hypothesis (C vs Si under periodic shocks). Phase 0: inverted (C-resilient); re-test pending on terrain.
- **Sugarscape** — the Epstein & Axtell base model; Phase 0 scaffolding, superseded for C by the kcal economy.
- **kcal economy** — Phase 1 C economy: per-month reserve, burn 75,000 kcal/step, intake = rate × 180; reserve_full/floor placeholders (MR-1).
- **forage_kcal / game_kcal** — terrain resource fields; per-biome lognormal(mean, std), terrain-coupled (MECHANISMS §9a).
- **Biomes** — water(0), wetland(1), forest(2), savanna(3), grass(4), desert(5), mountain(6).
- **CC-1** — deferred re-derivation of the cell carrying-capacity/extractable rate from NPP, with rivalry (RECAL-ADJACENT). All current resource values are PROVISIONAL pending CC-1.
- **GD-1 / JV-1 / RS-1 / MR-1 / MR-2 / PL-1** — the other deferred mechanics (game depletion, juvenile curve, risk-sensitivity, reserve/provision anchoring, pool scale-dependence). See DEFERRED_MECHANICS.md.
- **Trait vector H = [φ, ψ, c1, c2]** — φ work-orientation, ψ sociability, c1 conformism axis, c2 cooperation axis.
- **σ, κ** — decision noise and its Cred-coupling slope.
- **Deffuant** — bounded-confidence cultural updating (Stage 5.2).
- **Dormancy** — Si survival state replacing starvation (τ_trickle, k_reactivate, T_dormant_max).
- **Pool** — proximity support pool (L1 self / L2 proximity / L3 status; C has L3, Si doesn't).
- **Fission** — Si single-parent reproduction (wealth-threshold).
- **N_carry** — carrying-cost birth ceiling (50×50: 400; 100×100: 4100).
- **Phase 0 / Phase 1** — social-mechanics arc (Sugarscape) vs terrain-resource-ecology arc. "Stage N" before 2026-06-12 = Phase 0.
- **Blueprint A** — the agent↔terrain migration + kcal economy + static game (complete).
- **Gate / rails** — a blocking pass/fail checkpoint; rails are the individual criteria.
- **OWE-n** — owed/tracked backlog items in ROADMAP.
- **RECAL** — the deferred recalibration stage (re-derive dormant params on the new substrate).
- **TMTS** — "too much too soon" (a reason to defer a mechanic).
- **HARK** — hypothesizing after results known (forbidden; hence pre-registration).

---

## 8. Keeping this useful (maintenance discipline)

The whole point is that a fresh chat reads **this guide + CANONICAL_FACTS** and is current — no archaeology. To keep that true:
- **CC regenerates `CANONICAL_FACTS.md`** whenever a run changes a projected fact, then **prompts the supervisor to re-upload it** to project knowledge (rule 15). Volatile state lives there, not here.
- **CC drains `PENDING_CC.md`** at the start of every run (rule 14): each chat-side decision is reconciled into its home or surfaced as a `[CONFLICT]`.
- **This guide changes rarely** — only when the doc *system*, the locked spine, or the planning workflow changes. Its §2 "where we stand" is a pointer; don't turn it into a changelog (that's ROADMAP/CANONICAL_FACTS).
- **One fact, one home** stays sacred: this guide and CANONICAL_FACTS hold *pointers and explanations*, never the authoritative copy of a value.

*End of PROJECT_GUIDE — created 2026-06-15. Non-authoritative; the `docs/` homes win on any conflict.*
