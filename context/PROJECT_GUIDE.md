# SiC Games — PROJECT GUIDE / FULL BRIEFING (START HERE)

> **This is the single hand-off doc.** Read it (and `CANONICAL_FACTS.md` for the bleeding-edge status line) and you are current: what the project is, what is in the model **now**, what is in the **plan**, where every fact is **documented**, the invariants you must not break, a glossary, and how to plan a blueprint.
>
> **Derived / non-authoritative** (lives in `context/`, not the charter homes) — it explains and points; on any conflict the `docs/` homes win. **Current as of 2026-06-16.** Regenerate the §5–§6 inventories when the model materially changes; the live status line lives in `CANONICAL_FACTS.md`.

---

## 1. The 60-second orientation

**SiC Games is an agent-based model (Python / Mesa) comparing two civilization types on matched worlds.**
- **C (Carbon)** — hierarchical / status-driven. Decision noise coupled to **Cred** (status from joint tasks); biparental reproduction; status-mediated support.
- **Si (Silicon)** — egalitarian / individualist. Fixed decision noise; single-parent fission; reciprocal support; a dormancy survival mechanic.

**Central question — H1(ii):** which strategy is more resilient to periodic resource shocks? *(Phase 0 Sugarscape result: inverted — C survived, Si collapsed, robust 5/5 seeds at A=0.75/T=200. NOT yet re-confirmed on the Phase 1 terrain substrate — HYPOTHESES `§H1ii-RETEST` / RESULTS `R-1`.)*

**The arc:** Phase 0 built the social mechanics on the Epstein & Axtell **Sugarscape** sugar grid (Stages 1–7.5, complete 2026-06-11). Phase 1 replaces the sugar scaffolding with a **terrain-driven resource ecology** (real biomes, kcal economy), keeps the social apparatus, and re-validates H1(ii) on it.

**Working rule:** the human supervisor directs the science; the coding agent (CC) implements blueprints exactly and **never changes science without explicit approval**.

---

## 2. Where the project stands (pointer)

Frontier as of this writing: **Phase 1, Blueprint A complete and committed** (agent↔terrain migration + kcal economy + static game); resource cells now drawn from a **literature-anchored lognormal (mean, std)**. **Next:** A-3 performance audit, then seasonal-forage. The live, always-current status line is in **`CANONICAL_FACTS.md`** — read it after this. If this paragraph and CANONICAL_FACTS/ROADMAP disagree, they win.

---

## 3. The locked spine (do not re-litigate)

| Invariant | Value | Home |
|---|---|---|
| Temporal resolution | **1 step = 1 month** | PARAMETERS §1 / ARCH §9.3 |
| Grid | **100×100 cells**, 1 cell ≈ **100 km²** | PARAMETERS §1 / ARCH §9.3 |
| Substrate lineage | Sugarscape (Phase 0 scaffolding) → terrain forage/game fields (Phase 1) | ARCH §9 / ROADMAP |
| **C vs Si** | **different civilizations** — never assign a C mechanic to Si or vice-versa | ROADMAP "C/Si distinction table" |
| Economy (C, Phase 1) | **kcal** reserve; burn 75,000 kcal/step; Sugarscape sugar DORMANT-SUPERSEDED-FOR-C | PARAMETERS §13 / ARCH §12.1-L |
| Determinism | same `(knobs, seedStr)` → byte-identical terrain; equivalence gate before any non-science refactor | CLAUDE.md rules 2 & 13 |

---

## 4. The documentation system — every document explained

**One fact, one home.** 11 authoritative charter homes under `docs/`, plus derived views, a non-canonical `context/` layer, and governance files. Same fact in two places = a bug.

### 4.1 The 11 charter homes (`docs/`)
| Home | Owns | Read it when… |
|---|---|---|
| **INDEX.md** | the routing table (which home owns which kind of fact) | you don't know where a fact lives |
| **ROADMAP.md** | stage sequence, status, deferred items, open questions (Q-list), owed-items (OWE) backlog | "where are we / what's next" |
| **ARCHITECTURE.md** | system structure: §9 world/terrain substrate, **§12 dated decision-log**, §13 seams, §15 known-gaps | a design decision / seam / how the world is built |
| **MECHANISMS.md** | per-construct rules/equations, C/Si classification, **§9a kcal economy** | "how does mechanic X work" |
| **PARAMETERS.md** | the value + lock/sweep history of **every** parameter (§1–§13) | any parameter value/status |
| **TARGETS.md** | aspirations not yet test-specced (T-1/2/3) | "what we hope to show" |
| **HYPOTHESES.md** | pre-registrations + resolution (H-EMERGE-1, §H1ii-RETEST, H_cc) | before any analysis that could HARK |
| **RESULTS.md** | established findings in prose (R-1) | "what do we know" |
| **ARTIFACTS.md** | index of every report/benchmark + location + headline | "where's the run that showed X" |
| **LITERATURE.md** | citations: what lifted/rejected/why; Survey A/B | grounding a mechanic / checking a source |
| **DEAD_ENDS.md** | retired directions + why (DE-1) | "did we try X already" |

### 4.2 Derived views & resource-layer docs (`docs/`)
| Doc | Owns |
|---|---|
| **SiC_Games_Resource_Return_Rate_Table.md** | **the exhaustive resource table** — §1 methodology, §2 forage (mean/std/derivations), §3 game (mean/std/derivations + per-species), §4 source list. Feeds `FORAGE/GAME_KCAL_TARGETS` + `_STD`. *(Replaced the former game-only table, now a stub redirect.)* |
| **MODEL_SPEC.md** | resource-layer methodology record (formula, denominator rules, seasonal architecture, catastrophe seam stub) |
| **DEFERRED_MECHANICS.md** | the 7 agreed-but-deferred mechanics (seam + literature anchor + status): GD-1, JV-1, CC-1, RS-1, MR-1, MR-2, PL-1 |

### 4.3 The `context/` layer (non-canonical — bridges chat-to-chat)
| File | Purpose |
|---|---|
| **PROJECT_GUIDE.md** (this file) | the complete briefing — hand this to a chat |
| **CANONICAL_FACTS.md** | live current-state cache (every line `→ home`); regenerated + re-uploaded whenever a run changes a projected fact (rule 15) |
| **PENDING_CC.md** | append-only buffer of chat-side decisions not yet drained into a home; drained at every run start (rule 14) |

### 4.4 Governance & agent contract
- **DOCS_CHARTER.md** — the governance the home system implements (closed home set, single-home discipline).
- **sic_games/CLAUDE.md** — the coding-agent contract: **15 standing rules** + **report rules R1–R7**.

---

## 5. CURRENT MODEL — what is implemented now

> Inventory of every live mechanic + key locked value, grouped by layer. Depth lives in MECHANISMS (rules) and PARAMETERS (values); this is the "what exists and where" map. *Phase 0 mechanics are validated on Sugarscape and carry into Phase 1; the C resource/economy layer is being re-based onto terrain (Blueprint A done).*

### 5.1 World / substrate
- **Phase 0 Sugarscape** — grid (50×50 science / 100×100 production), sugar peaks, growback (α=4, c_max=16, k_grid=4), `SeasonalOscillation` perturbation (amplitude A, period T), `effective_capacity`. **DORMANT-SUPERSEDED-FOR-C** in Phase 1. → MECH §9 / ARCH §9
- **Phase 1 terrain generator** (`terrain.py`) — deterministic pipeline: fbm+ridge elevation → water → rivers → moisture → NPP/forestness → **biomes** {water 0, wetland 1, forest 2, savanna 3, grass 4, desert 5, mountain 6}. Byte-identical per `(knobs, seedStr)`. Guards: largest-water-body ceiling 0.08, mtn ceiling ≈0.317. Diagnostics: `characterize_map`, water-component decomposition, shore detection. → ARCH §9.5
- **Resource fields** — `forage_kcal`, `game_kcal` (per-biome **lognormal(mean, std)**, terrain-coupled, deterministic), `npp_gm2` (npp×3400), `is_shore` (+shore bonus 1491.5). All values literature-anchored (Resource table) and **PROVISIONAL pending CC-1**. → Resource table / MECH §9a.6

### 5.2 C (Carbon) agent mechanics — all live
- **Decision:** softmax with **Cred-coupled noise** σ = σ_base + κ·tanh(𝒞/C*) (σ_base **0.5**, κ **2.0**, C* **10**). Greedy baseline exists.
- **Cred 𝒞** — earned from **joint tasks** (Matthew partition α=**2.0**, capacity θ=**4**, radius d=**1**, cred_bonus 1.0), decay δ=**0.01**.
- **Status amplification** β=**1.0**; **wealth-velocity mode switch** (v_tau **10**, v_0 **1.0**).
- **Trait vector H=[φ,ψ,c1,c2]** — φ status-weight, ψ sociability (proximity-to-agents utility term, active for C), c1 conformism (scales Deffuant copy), c2 cooperation (defection hook).
- **Reproduction** — biparental, proximity r=**3**, σ_inherit=**0.10**, wealth inheritance λ=**0.1**; DTM unimodal P_birth, **Cred-modulated** (γ=**0.2**); **carrying-cost ceiling** (N_carry **400**@50² / **4100**@100², α_carry **1.0**); newborn Cred f_C=**0.25**.
- **Age-efficiency** ramp η(a) (η_min **0.3**, η_old **0.4**, a_forage_min ≈15).
- **Support pool** L1 self / L2 proximity / L3 status (τ_pool **0.05**, k_reserve **5**, k_draw **3**, ρ **0.3**; **τ_parent 0.0** and **k_pool_cap 0.0** = dormant, re-derive at RECAL).
- **Cultural** — Deffuant updating (ε **0.2**, μ **0.3**, cred-weighted); **c2 defection** enabled (rate ≈3.7%).
→ MECH §1–§6, PARAMETERS §2–§9

### 5.3 Si (Silicon) agent mechanics — all live
- **Decision:** bounded-rational **fixed** σ_Si=**1.238** (no Cred coupling by default); Si Cred = near-dormancy accumulation (k_cred_band **1.0**, κ_Si **0.5**, C*_Si 10) — counter-cyclical.
- **Reproduction:** single-parent **fission** (p_fission **0.065**, wealth-threshold), near-copy + noise, **λ=0** (no wealth inheritance), η=**1.0** (no ramp).
- **Differential metabolism** β_Si=**5.0**.
- **Dormancy** (replaces starvation death): k_dormant **1.0**, τ_trickle **0.3**, k_reactivate **3.0**, T_dormant_max **50**.
- **No L3 pool** (reciprocal only). ψ hook **deferred/inactive**. **HiveMind** reproduction coordinator = skeleton only.
→ MECH §3/§5.2/§8, PARAMETERS §7/§8

### 5.4 Phase 1 kcal economy (Blueprint A — C agents on terrain)
- **`TerrainWorld`** (mesa model); C agents harvest terrain kcal via the **`TerrainField`** drop-in adapter (no SugarField in the harvest path).
- **Per-month conversion** (1 step = 1 month): burn **75,000 kcal/step** (2,500/day × 30); intake = rate × **180** (6 hr/day × 30). Reserve: `reserve_full` **100,000**, `reserve_floor` **20,000** (both [PLACEHOLDER MR-1]); `lifespan_months` **900** [PLACEHOLDER].
- **Sex** attribute; **sex-based stream selection** (female→forage, male→game; switch only under deficit). **Binary child age-gate** (intake 0 below age 15; JV-1 seam).
- **Non-rivalrous harvest** (CC-1 seam); **game-as-stock read-only** (GD-1 seam, no depletion).
- Gate A-1 GREEN (3 seeds, 500 steps, forage-only). → ARCH §12.1-L, MECH §9a, PARAMETERS §13

### 5.5 Resource return rates (the layer you just consolidated)
- Per-biome **(mean, std)** for forage + game, drawn via terrain-coupled lognormal; std literature-anchored where a source reports a spread, **else 10% of mean**.
- Literature-anchored: game forest 5,541±4,043 · game desert 730±210 · forage wetland 1,428±3,362 · forage forest 2,630±600 · forage savanna 257.7±182.1 · forage desert 1,200±368 · game savanna 518±1,158 (derived, review).
- 10%-default: game grass 3,001±300 · forage grass 1,125±113 · forage mountain 5,387±539.
- **All PROVISIONAL pending CC-1.** → Resource table §2/§3

### 5.6 Infrastructure
- **SoA / vectorisation** (Stage 7.5 — partial; oracle parity gates), **BatchRunner** (CRN — pending), **HTML reports** (base64 figures), **equivalence gates** (B0). → ARCH §12 / ARTIFACTS

---

## 6. THE PLAN — what is next and deferred

### 6.1 Immediate next
- **A-3 performance audit** — `TerrainWorld` step-time at Phase 1 agent counts before any long campaign (separate blueprint). → ROADMAP
- **Seasonal-forage** — amplitude modulation on `forage_kcal`/`game_kcal` (the seasonal layer; star-mechanics seam in MODEL_SPEC). → ROADMAP / MODEL_SPEC §4.1.6

### 6.2 The big deferred pieces
- **CC-1 (RECAL-ADJACENT)** — re-derive each cell's carrying-capacity / extractable kcal rate from NPP, add **rivalry** (currently non-rivalrous). **Every resource value is PROVISIONAL until this lands.** → DEFERRED_MECHANICS.md
- **The 7 deferred mechanics** — GD-1 game depletion · JV-1 age-graded juvenile curve · CC-1 · RS-1 risk-sensitivity foraging · MR-1 reserve anchoring · MR-2 carried-provision · PL-1 pool scale-dependence. → DEFERRED_MECHANICS.md
- **§STAGE-RECAL** — re-derive dormant params (τ_parent, k_pool_cap) on the terrain substrate and **re-test H1(ii)** (pre-registered). → ROADMAP §STAGE-RECAL
- **OWE-14** — re-confirm the H1(ii) inversion at calibrated 100×100 (≥3 seeds) — deferred pending substrate + perf. → RESULTS R-1
- **Stage 6 statistics framework** — power analysis, effect sizes, pre-registered metrics (unnumbered Phase-1 backlog). → ROADMAP / OWE-10
- **§STAGE-GEOSTRUCT** — coastline/archipelago terrain (only when seafaring dynamics need it). → ROADMAP

### 6.3 OWE backlog (tracked owed items)
OWE-2 terrain topography metabolism multiplier · OWE-5 Si ψ utility hook · OWE-6 physical-channel inheritance · OWE-8/13 movement-decomposition (for H-ORTHOGONALITY) · OWE-9 σ_inherit corrective sweep. → ROADMAP "Owed items"

### 6.4 Open decisions / provisional values awaiting the supervisor
- **Savanna game std = 1,158** — derived from Hawkes income variance, flagged supervisor-review.
- **Placeholders** to ground at recal: reserve_full/floor (MR-1), lifespan_months, burn/hours nominals.
- **σ_inherit PARTIALLY-UNEXERCISED** caveat (0.10 locked but Stage 5.2 headline ran at 0.05) — parked to RECAL. → PARAMETERS §7
- **Mislabeled file:** `literature/SiC_Games_A1.6b_Hurtado1987_HiwiFoodProc.pdf` actually holds a Dressler blood-pressure paper.
- Live in **`PENDING_CC.md`** (the running list).

---

## 7. How to navigate for a task (recipes)
| You want to… | Read, in order |
|---|---|
| Get oriented from cold | this guide → `CANONICAL_FACTS.md` → `PENDING_CC.md` |
| A parameter's value/history | `PARAMETERS.md` (search the symbol) |
| How a mechanic works | `MECHANISMS.md` → `ARCHITECTURE.md §12` (why) |
| A resource cell value/std + derivation | `SiC_Games_Resource_Return_Rate_Table.md` §2/§3 |
| What's next / deferred | `ROADMAP.md` + `DEFERRED_MECHANICS.md` |
| A past result/run | `ARTIFACTS.md` → `RESULTS.md` |
| Ground a number in literature | `LITERATURE.md` + Resource table |
| What was already abandoned | `DEAD_ENDS.md` |

---

## 8. How to plan a blueprint (conventions)
1. **Pre-register** the hypothesis/acceptance before running (HYPOTHESES.md) — no HARKing.
2. **Gate-first:** explicit pass/fail *rails*, confirmed as a *blocking* checkpoint before the gated run (rule 13: a failed gate is a STOP).
3. **One new parameter per stage**, with a pre-committed calibration target + acceptance check.
4. **Tag provenance:** `[VERIFIED]/[SECONDARY]/[INLINE]/[UNVERIFIED]` for citations; `[PROVISIONAL]/[PLACEHOLDER]/[NOMINAL]` for values; never fabricate — UNANCHORED cells get `—`.
5. **Respect the C/Si distinction** (check the ROADMAP table before any mechanic).
6. **Definition of done:** gate green + all blocks green + doc-home updates applied + provisional values tagged + existing suite green.
7. **Reports** obey R1–R7 (terminal-state row per seed, gate-vs-finding sentence, magnitudes, an Anomalies section, a synthesis).
8. Pull current state from CANONICAL_FACTS (not memory); name the home each change updates; list the seams touched (DEFERRED_MECHANICS.md).

---

## 9. Glossary (the terms that cost catch-up time)
- **C / Si** — the two civilizations (Carbon/hierarchical, Silicon/egalitarian); matched worlds, never mixed.
- **Cred (𝒞)** — C-only status capital from joint tasks; drives C's σ and reproduction. Si has a separate near-dormancy Cred.
- **H1(ii)** — the resilience hypothesis (C vs Si under periodic shocks). Phase 0: inverted (C-resilient); re-test pending on terrain.
- **Sugarscape** — Epstein & Axtell base model; Phase 0 scaffolding, superseded-for-C by kcal.
- **kcal economy** — Phase 1 C economy: per-month reserve, burn 75k/step, intake = rate×180.
- **forage_kcal / game_kcal** — terrain resource fields; per-biome lognormal(mean,std), terrain-coupled.
- **Biomes** — water(0) wetland(1) forest(2) savanna(3) grass(4) desert(5) mountain(6).
- **CC-1** — deferred re-derivation of cell carrying-capacity/extractable rate from NPP + rivalry; all resource values PROVISIONAL until it lands.
- **GD-1 / JV-1 / RS-1 / MR-1 / MR-2 / PL-1** — the other deferred mechanics (DEFERRED_MECHANICS.md).
- **Trait vector H = [φ, ψ, c1, c2]** — φ status-weight, ψ sociability, c1 conformism, c2 cooperation.
- **σ, κ** — decision noise and its Cred-coupling slope. **β_Si** — Si differential metabolism (5.0).
- **Deffuant** — bounded-confidence cultural updating. **Dormancy** — Si survival state replacing starvation.
- **Pool** — proximity support pool (L1 self / L2 proximity / L3 status; C has L3, Si doesn't).
- **Fission** — Si single-parent reproduction. **N_carry** — carrying-cost birth ceiling (400 / 4100).
- **Phase 0 / Phase 1** — social-mechanics (Sugarscape) vs terrain-resource-ecology arc. "Stage N" before 2026-06-12 = Phase 0.
- **Blueprint A** — agent↔terrain migration + kcal economy + static game (complete).
- **Gate / rails** — a blocking pass/fail checkpoint; rails = the individual criteria.
- **OWE-n** — owed/tracked backlog items (ROADMAP). **RECAL** — deferred recalibration stage. **TMTS** — "too much too soon" (a reason to defer). **HARK** — hypothesizing after results known (forbidden).
- **lognormal draw / 10% rule** — resource cells drawn from a literature-anchored lognormal(mean,std); std = literature spread, else 10% of mean.

---

## 10. Keeping this useful (maintenance)
- A fresh chat reads **this guide + CANONICAL_FACTS** and is current — no archaeology.
- **CC regenerates `CANONICAL_FACTS.md`** when a run changes a projected fact, then prompts re-upload (rule 15). Volatile status lives there.
- **CC drains `PENDING_CC.md`** at every run start (rule 14).
- **This guide's §5–§6 inventories** change at the pace of stages — refresh them when a mechanic/parameter is added or the plan shifts; the §2 status line stays a pointer.
- **One fact, one home** stays sacred: this guide holds *pointers and structure*, never the authoritative copy of a value.

*End of PROJECT GUIDE / FULL BRIEFING — created 2026-06-15, upgraded to full briefing 2026-06-16. Non-authoritative; the `docs/` homes win on conflict.*
