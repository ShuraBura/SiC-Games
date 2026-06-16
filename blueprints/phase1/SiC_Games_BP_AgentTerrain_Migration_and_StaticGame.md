# SiC Games — Blueprint A: Agent↔Terrain Migration (A-1) + Static Game Mechanics (A-2)

**Document:** `blueprints/phase1/SiC_Games_BP_AgentTerrain_Migration_and_StaticGame.md`
**Status:** READY FOR EXECUTION
**Supersedes:** `SiC_Games_BP_Static_Game.md` (assumed an agent↔terrain coupling that was never built).
**Stage:** First stage of the temporal-dynamics arc. Two internally-gated phases: A-1 (substrate migration) → A-2 (game mechanics on the frozen substrate). A separate perf-audit blueprint (**A-3**) follows once the coupled economy exists and returns green.
**Scope:** C agents only. Si excluded entirely (architecture-lens only this round).
**Economy:** kcal throughout. The legacy sugar/`c_max` economy is **superseded** — see §0.2 (this is a locked-cluster change, not a unit rename).
**Step:** locked 1 month (project decision; ROADMAP §"12,000 steps = 1000 yr at 1 step = 1 month"). No τ derivation here — the 1-month step is applied to convert kcal/hr and kcal/day rates to per-step quantities.

---

## §0 Premises and corrections — read first

### 0.1 The coupling gap
The superseded BP assumed C agents harvested on the terrain biome layer. They do not. Agents run on `SugarField`; the terrain layer (`world/terrain.py` → `WorldFields`: `biome`, `forage_kcal`, normalized `game`) has never been referenced by any agent or run-loop code. Phase 1 Stages 1–1c built terrain *diagnostics* only. A-1 performs the live migration; A-2 builds game mechanics on top.

### 0.2 The kcal economy supersedes a LOCKED, COUPLED cluster — not a unit rename
The existing economy is not a free placeholder currency. It is a locked, co-designed cluster (PARAMETERS.md, all LOCKED): `c_max=16 (=4·k_grid)`, `α_growback=4 (=k_grid)`, `k_grid=4`, tuned *together with* `β_Si=5` so that mean harvest (~10–15/step) exceeds Si cost (~12.5/step) with dormancy absorbing shortfalls (ARCH §12, Stage 4.4). The reserve/draw multiples (`k_reserve=5.0`, `k_draw=3.0`) and pool rates are denominated in this same sugar scale.

**Consequence:** moving to kcal is a substrate-economy change that **supersedes this locked cluster**, not a cosmetic swap. A-1 does NOT silently re-express locked parameters. It declares the sugar cluster **SUPERSEDED-FOR-C** (Si is out of scope this round, so β_Si coupling is dormant and not exercised), introduces the kcal economy alongside, and records the supersession in PARAMETERS.md and ARCHITECTURE §12 (decision-log) with a dated note. Any locked sugar-cluster parameter that has no kcal analogue is marked DORMANT-SUPERSEDED, not deleted (nothing is hard-deleted; archive discipline per DOCS_CHARTER). The full re-derivation of the kcal resource ceiling is **CC-1 (RECAL-adjacent)** — A-1 uses provisional kcal values; the locked-cluster *replacement* is RECAL-A-class and is not done here.

### 0.3 Cost is unmeasured on this substrate — gates are correctness, not cost
Stage 6.0a-perf (the only perf audit) profiled the **pre-terrain** substrate. Its findings — N linear, grid-cells sub-dominant, **occupancy the wall** (feasible ≤~2.3/cell; proto-ag density NOT reachable on the Python path without array-restructuring + JT redesign) — are the best numbers available but are **stale w.r.t. the terrain substrate**, which agents have never run on. Therefore:

- The A-1 and A-2 exit gates are **small-scale correctness rails** (short run, modest N: no-extinction / no-explosion / economy-coherent). The explosion bound is a loose grid-capacity check, NOT a costed proto-ag threshold.
- The **cost envelope is deferred to A-3** (a separate perf-audit blueprint, report-is-deliverable), run on the coupled economy after this blueprint returns green.
- A-3 measures the **subsistence loop** on the new substrate. The JT/social-layer proto-ag-occupancy wall (the Stage 6.0a blowup) is NOT exercised by subsistence alone and is re-measured in a later, separate audit when the social layer next runs at scale.

### 0.4 Must-be-seen artifacts
None in either phase. The A-1 gate is assertable rails, not a human-judged artifact. No prose report on green.

---

# PHASE A-1 — Substrate migration (Sugarscape → terrain, kcal economy)

## §1 Task A1.1 — Create and seed DEFERRED_MECHANICS.md

Create `docs/DEFERRED_MECHANICS.md` (register it in INDEX.md as a new home; add its update trigger per charter discipline). Running home for discussed-agreed-good-but-deferred mechanics.

**Format — one entry, exactly these fields:** What / Why deferred / Literature-rationale anchor / Seam / Status.

Seed seven entries:

- **GD-1 — Game depletion.** Depletable local game stock drawn down by hunting, with regrowth. Deferred (TMTS; depends on game-as-stock seam A-2 + ceiling CC-1; depletion without a real ceiling is placeholder/placeholder). Anchor: Redford & Robinson 1987, Vickers, Ross 1978 — depletion is a *sedentism* effect (hunt-out of a fixed catchment), mobile bands avoid it via movement; large slow-breeders go first. Seam: game-as-stock field (A-2 §11) + local hunting pressure + residence time. Status: DEFERRED.
- **JV-1 — Age-graded juvenile productivity.** Replace the binary child age-gate (A-2) with a graded productivity-by-age curve. Deferred (TMTS; binary is minimal-correct). Anchor: Bird & Bliege Bird 2000 (Meriam juvenile age-graded rates). Seam: age-gate hook A-2 §12; age attribute exists (Phase-0). Status: DEFERRED.
- **CC-1 — Carrying-capacity-from-NPP (cell extractable rate + rivalry).** Replace provisional biome-scaled cell yield with a literature-grounded ceiling; cell characterized by total extractable kcal rate = f(biome carrying capacity, replenishment); co-located agents divide the finite rate → rivalry emerges; density and starvation become emergent not tuned. **This is also where the superseded sugar-cluster's resource ceiling is re-derived in kcal.** Deferred (foundational substrate change; bundling = can't attribute dynamics; RECAL-A-class). Anchor: Tallavaara 2018 (HG density vs NPP) for forage ceiling; ungulate-biomass-from-NPP ecology (Coe-Cumming-Phillipson) for game ceiling. Seam: decision rule (A-2 §10) reads cell yield but doesn't define it; swap changes numbers not logic; rivalry switches on with the real rate. Status: RECAL-ADJACENT.
- **RS-1 — Risk-sensitivity / variance-reduction foraging.** Agents value variance reduction, not just mean. Deferred (TMTS; A-2 switch is survival-fallback, not variance). Anchor: Janssen & Hill 2014 (coop hunting −4% mean, zero-meat-days 52%→9%). Seam: stream-choice objective in A-2 §10. Status: DEFERRED.
- **MR-1 — Physiological reserve anchoring.** Ground the kcal reserve (body-fat store) and starvation floor; replace physiology-estimate placeholders. Deferred (survey is its own deliverable). Anchor: textbook physiology placeholders (reserve-full ≈ 100,000 kcal; floor ≈ 20,000 kcal, ~40% body-weight loss) — NOT HG-field numbers; survey to confirm/replace + literature starvation threshold. Seam: reserve + floor in A-2 §10 / A-1 §3. Status: SURVEY-PENDING.
- **MR-2 — Carried-provision anchoring.** Food carried while travelling ("on the belt"), short-horizon (days), distinct from the long-horizon physiological reserve; two separate quantities. Deferred (needs ethnographic anchor; not needed for wiring). Anchor: foraging-trip duration/load in Ache/Hadza/Martu corpus. Seam: a second short-horizon buffer above the reserve; not built now (single reserve only). Status: SURVEY-PENDING.
- **PL-1 — Pool scale-dependence.** Re-scope the existing pool as density-dependent: small-band pool = sum of personal carry (immediate-return); institutional surplus pool meaningful only at higher density/sedentism. Deferred (change to an existing mechanic, belongs with density/co-location revisit). Anchor: immediate-return vs delayed-return foraging economies. Seam: existing pool mechanic + density gate; maps to co-location-must-pay. Status: DEFERRED.

**Acceptance A1.1:** file exists; registered in INDEX with trigger; exactly 7 entries (GD-1, JV-1, CC-1, RS-1, MR-1, MR-2, PL-1) each with all 5 fields; CC-1 = RECAL-ADJACENT names Tallavaara 2018 and notes it re-derives the superseded ceiling; MR-1/MR-2 = SURVEY-PENDING. Failed = blocking STOP (CLAUDE.md Rule 11).

## §2 Task A1.2 — Terrain field completion (`world/terrain.py`, `WorldFields`)
1. Add **`game_kcal`** (kcal/forager-hr), biome-resolved from `SiC_Games_Game_Return_Rate_Table.md`: hump-shaped (peak savanna/edge), **zeroed** at wetland (UNANCHORED), mountain (UNANCHORED), open water (out of scope). Tag `[PROVISIONAL — biome-scaled from return-rate table, pending CC-1 ceiling]`. (The existing normalized `game`∈[0,1] does not zero non-game biomes; `game_kcal` replaces it for harvest.)
2. Confirm `forage_kcal` units are kcal/forager-hr (per ARCH §9.5 FORAGE_KCAL_TARGETS / Marlowe 2010 + Bird & Bliege Bird synthesis).

**Acceptance A1.2:** `game_kcal` exists in kcal/forager-hr; zeroed at wetland/mountain/open-water; hump shape per table; tagged; `forage_kcal` confirmed kcal/forager-hr. Failed = blocking STOP.

## §3 Task A1.3 — kcal economy + per-month conversion
1. **Reserve (kcal):** existing `wealth` (integrating reserve) becomes the kcal reserve; re-express scale in kcal. Placeholders tagged `[PLACEHOLDER — physiology-estimate, pending MR-1]`: full ≈ 100,000 kcal; starvation floor ≈ 20,000 kcal (existing mortality path `wealth ≤ 0` becomes `reserve ≤ floor`, floor re-expressed).
2. **Burn (kcal/step):** the existing sugar burn is **SUPERSEDED-FOR-C** (sugar and kcal cannot integrate together — this was the unit-incoherence the prior BP carried). Use nominal adult HG expenditure ≈ 2,500 kcal/day → `burn_per_step = 2,500 × days_per_month`. Tag `[NOMINAL — adult expenditure, tunable, grounding-refinement pending]`.
3. **Intake (kcal/forager-hr → kcal/step):** `intake_per_step = rate_kcal_per_hr × foraging_hours_per_day × days_per_month`. `foraging_hours_per_day`: **nominal 6**, tunable, tagged `[NOMINAL — time-allocation literature (Ache/Hadza active-foraging hours), tunable, grounding-refinement pending]`.
4. **Integration:** `reserve += intake_per_step − burn_per_step` (kcal). Death at `reserve ≤ floor` (existing path, kcal floor).
5. **Sugar-cluster supersession:** declare `c_max`, `α_growback` (and the sugar-denominated `k_reserve`, `k_draw` interpretation) **SUPERSEDED-FOR-C / DORMANT-SUPERSEDED** in PARAMETERS.md + ARCH §12 with dated note. Do NOT delete; do NOT silently re-tune. `k_grid` / `β_Si` coupling is Si-side and dormant this round (Si out of scope) — note it, do not touch it. Full kcal-ceiling re-derivation = CC-1 (not here).

**Acceptance A1.3:** reserve kcal + tagged; burn kcal/step from tagged nominal via 1-month step; `foraging_hours_per_day` tunable nominal 6 tagged; intake = rate × hrs/day × days/month; reserve integrates coherently (unit test on known sequence); no sugar quantity remains in the **C** energy economy (grep clean); supersession recorded in PARAMETERS.md + ARCH §12 (dated, nothing deleted). Failed = blocking STOP.

## §4 Task A1.4 — Live-loop migration (forage only)
1. C agents (`strategies/carbon.py` + run loop) read `forage_kcal` at their cell, harvest per A1.3. **Forage only in A-1** (validate migration on the simpler, better-anchored consumer first; game is A-2).
2. Remove `SugarField` from the C harvest path (retain the class for any scaffolding/tests that reference it; the C loop no longer harvests sugar).
3. Movement/placement on the terrain grid; confirm grid + cell area consistent (100×100, 100 km²/cell — both LOCKED, PARAMETERS.md / ARCH §9.3).

**Acceptance A1.4:** C agents harvest `forage_kcal` from their terrain cell in the live loop; C harvest path no longer references `SugarField`; agent grid ≡ terrain grid (100×100, 100 km²/cell); wetland/mountain forage cells deliver biome-correct (incl. zero) `forage_kcal`. Failed = blocking STOP.

## §5 Gate A-1 — small-scale correctness rails + freeze
Run a **short, modest-N, fixed-seed-set** simulation of the migrated forage-only economy (NOT proto-ag scale — this is a correctness check, not a cost measurement; cost is A-3). Pre-commit thresholds in this directive before running:

```
RAIL 1 (no extinction): population > 0 at run end (run length L_short, seeds S)
RAIL 2 (no explosion): population ≤ grid-capacity loose bound B = (100×100 cells × occ_cap_loose)
                       where occ_cap_loose is a deliberately generous correctness ceiling, NOT a cost threshold
RAIL 3 (economy coherent): mean reserve stays in physically meaningful kcal bounds
                       (no alive-but-negative; no unbounded monotonic growth) over the run
RAIL 4 (existing tests green): full suite passes; any forage-layer behaviour change surfaced in ARCH §15 (gaps)
                       / MECHANISMS, not silently fixed
```

**[SUPERVISOR TO SET before issue: `L_short` (suggest ~500–1000 steps, ≥ transient), `S` (suggest 3 seeds), `occ_cap_loose` (suggest generous, e.g. 10/cell — correctness only). These are correctness rails; do not set them to proto-ag cost targets.]**

CC sets no threshold itself; if any rail threshold is absent from this directive at run time, STOP and surface it.

**On pass:** freeze A-1 config; record frozen state; proceed to A-2.
**On fail:** blocking STOP-AND-REPORT — a failed rail is a finding (the migration changed something) to be read before A-2. Do not proceed to A-2 on a failed A-1 gate.

---

# PHASE A-2 — Static game mechanics on the frozen A-1 substrate

Economy is now coherent kcal. A-2 acceptance is fully mechanical — **no outcome readings** (no density, starvation-rate, resilience, or population-shape verdicts; the ceiling is provisional pending CC-1).

## §9 A2.1 — Sex attribute (`world/agents` + init)
Binary sex drawn at C init; `p_female` tunable, default 0.5 (PARAMETERS.md, MECH note: no environmentally-driven human sex-ratio mechanic — 50/50 neutral, tunable for experiments). C-only; no Si path references sex.
**Acceptance:** sex set at init; `p_female` tunable default 0.5; n≥5000 sample female fraction 0.5±0.02; no Si path references sex. Failed = blocking STOP.

## §10 A2.2 — Energy-balance decision system (`strategies/carbon.py`)
On the A-1 kcal economy. **Stream default by sex:** male→game, female→forage (strong default; both-streams mix emerges from sex distribution). **Game intake:** male harvests `game_kcal` via the same per-month conversion; **non-rivalrous** (each agent gets its own rate; cell yield not divided) tagged `[PROVISIONAL — rivalry deferred to CC-1]`. **Switch (energy-balance driven, no new tunable):** deviate from sex-default only under deficit pressure — a male in a low/zero-game cell whose projected intake fails to cover burn AND whose reserve is falling toward the floor switches to forage *if* forage covers the deficit better; symmetric (rare) for females; when both streams cover burn comfortably, hold the sex default. **No risk/variance calc** (RS-1 deferred).
**Acceptance:** male w/ adequate game hunts (no switch); male in zero-game cell w/ falling reserve switches to forage when forage covers deficit; male in zero-game+zero-forage cell does not spuriously switch (declines to floor; existing mortality handles it); female default forage; game cap non-rivalrous tagged CC-1; no risk/variance calc present; no new hunger/starvation tunable beyond A-1 placeholders. Failed = blocking STOP.

## §11 A2.3 — Game-as-stock seam
Cell exposes a readable game quantity (`game_kcal` serves as the value the decision rule consults for "is there game here?"). **Depletion OFF** (hunting does not reduce it). **Rivalry OFF** (folds into CC-1). Document the interface: GD-1 and CC-1 write to this per-cell game field and nowhere else in the resource layer.
**Acceptance:** cell exposes readable game quantity consulted by the rule; hunting does NOT reduce it; interface documented for GD-1/CC-1. Failed = blocking STOP.

## §12 A2.4 — Child age-gate seam (`reproduction.py` / age attribute)
Use existing age attribute (Phase-0; no new attribute). Binary: below `age_productive_min` → zero subsistence; at/above → full adult. Graded curve OFF (JV-1). Use existing maturity threshold if PARAMETERS.md has one (see `a_forage_min`/`a_rep_min` rows, ROADMAP §age); else introduce tunable `age_productive_min` tagged `[PROVISIONAL — binary gate, graded curve deferred to JV-1]`.
**Acceptance:** below-threshold → zero; at/above → full; uses existing age attribute; tagged with JV-1 note. Failed = blocking STOP.

---

## §13 Document updates (definition of done)
- **PARAMETERS.md:** register kcal reserve placeholders (MR-1), kcal burn nominal, `foraging_hours_per_day` (6, tunable), `p_female` (0.5), non-rivalrous cap (CC-1), `age_productive_min` if new (JV-1); record sugar-cluster supersession (`c_max`, `α_growback`, sugar `k_reserve`/`k_draw` interpretation → DORMANT-SUPERSEDED, dated, not deleted). Every provisional/nominal value tagged.
- **ARCHITECTURE.md §12 (decision-log, append-only):** dated entry — sugar→kcal supersession for C, rationale, and that full ceiling re-derivation is CC-1/RECAL-A.
- **MECHANISMS.md:** kcal economy + per-month conversion (step=1 month, `foraging_hours_per_day`, `days_per_month`); energy-balance decision system; sex-based stream default; three seams (game-as-stock, child age-gate, non-rivalrous cap) each → DEFERRED_MECHANICS.md entry.
- **ARCHITECTURE.md §15 (gaps):** surface any conflict between migrated economy and pre-existing mechanics; do not silently fix.
- **ROADMAP.md:** mark Blueprint A complete (A-1 + A-2); next = **A-3 perf audit** (separate blueprint), then seasonal-forage (world-level insolation signal standalone-first → forage → game).
- **ARTIFACTS.md:** index any A-1 gate output.

## §14 Stopping rules / definition of done
Phases A-1 → A-2; tasks in listed order. Any failed acceptance = blocking STOP (Rule 11). **Gate A-1 is the one STOP-AND-REPORT.** Pass → freeze → A-2 without check-in. Done = A-1 gate green (rails pass, frozen), all A-2 blocks green, all doc updates applied, all provisional/nominal values tagged, existing suite green. **Must-be-seen: none.** One-line green confirmation; no prose report. **No outcome readings** (ceiling provisional pending CC-1). **Cost envelope is NOT assessed here — that is the separate A-3 perf-audit blueprint.**

## §15 Files touched
| File | Action |
|---|---|
| `docs/DEFERRED_MECHANICS.md` | Create + seed 7 entries; register in INDEX |
| `sic_games/.../world/terrain.py` (`WorldFields`) | Add `game_kcal` (provisional, biome-scaled, zeroed non-game); confirm `forage_kcal` units |
| `sic_games/.../strategies/carbon.py` + run loop | Migrate harvest Sugarscape→terrain; kcal economy; per-month conversion; sex; energy-balance decision; game harvest (A-2); age-gate |
| `sic_games/.../reproduction.py` / agent init | Sex attribute; child age-gate |
| `docs/PARAMETERS.md` | Register new kcal params (tagged); record sugar-cluster supersession (dated, not deleted) |
| `docs/ARCHITECTURE.md` | §12 decision-log (supersession); §15 gaps (conflicts) |
| `docs/MECHANISMS.md` | kcal economy, conversion, decision system, 3 seams |
| `docs/ROADMAP.md`, `docs/INDEX.md`, `docs/ARTIFACTS.md` | Stage status; new home registration; artifact index |

No Si code touched. No depletion, rivalry, risk-sensitivity, graded juvenile curve, carried-provision, or carrying-capacity/ceiling re-derivation built — all deferred and documented. Cost/perf assessment is the separate A-3 blueprint.
