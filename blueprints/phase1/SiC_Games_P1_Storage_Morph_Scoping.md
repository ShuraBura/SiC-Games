# SiC Games P1 — Collective Storage → the Society Morph (scoping + build)

**Goal:** turn the storage stock (just shipped, MODEL_SPEC §4.5.11) into the **delayed-return → inequality →
society-morph** engine the model has been "awaiting" (§4.5.10). Refactor storage from per-agent to a **collective
band granary** drawn **cred-weighted** (the inequality engine), add **maintenance/spoilage**, then **wire the
morph** (`society_from_character` / `morph_to_society` — currently defined but NEVER called) so a settled,
storing, dense band transitions `egalitarian_forager → complex_forager / stratified_chiefdom`.

## §1. Literature anchors

| Anchor | Value/claim used | Source |
|---|---|---|
| Storage zone | obligatory where Effective Temperature ≤ **15.25 °C** (overwintering) | Binford 2001 |
| Packing | **0.091/km²** (= model `BINFORD_PACKING_PER_KM2` ✓) | Binford 2001 |
| Storage = prime mover | storage → sedentism + density + **inequality** | Testart 1982 |
| Immediate vs delayed return | storage is the **egalitarian→hierarchical pivot**; delayed-return → differential access | Woodburn 1982 |
| **Control, not hoarding** | inequality from **controlling the surplus's redistribution** (feasting); "misers are despised — *control* of wealth is the universal pathway to power" | **Hayden, *Pathways to Power*** |
| Status-weighted sharing | complex foragers share the stored surplus by RANK | Ames 1994 (already in `complex_forager` preset) |
| Storage defense | stored surplus must be **defended** → territoriality/exclusion | Testart 1982 ("storage defense") |

## §2. The mechanic (collective store + cred-weighted draw)

- **Collective per-cell granary** (replaces the per-agent store). Co-resident occupants' harvest **overflow**
  (intake above the personal reserve cap — the cap stays the *individual* buffer, which already covers solo
  survival beyond the 2–3-day carry, Woodburn) is **enforced** into the cell's store, in the overwintering zone
  (cell temp ≤ `storage_temp_threshold_c`). Mobile bands barely accumulate (you can't store if you move,
  Testart) → storage ↔ sedentism reinforce.
- **Cred-weighted lean-season draw** = the inequality engine ("corruption"). The store is distributed to the
  cell's occupants **by cred-weight, REUSING the existing κ machinery** (`compute_harvest_shares(occ, store,
  κ, …)`) — graded/bounded (NOT winner-take-all), so low-cred get a *reduced* share, not zero (commoners
  survive worse, they don't get annihilated — see RT-2). High-cred ride out winter on the commons → differential
  survival → inequality. This is the Hayden control-of-redistribution mechanism.
- **Maintenance / spoilage** — a per-step decay `storage_decay` (food spoils; the store needs upkeep harvest).
- **Individual survival** = the existing `wealth`/`reserve_full` buffer (NOT a separate store — RT removes v1's
  per-agent store as redundant with the reserve).

## §3. The morph wiring

- **Settlement detector** (per cell): sustained **collective store > 0** AND **local density ≥ packing**, held
  for **T ≈ 1 generation** (~300 steps; Bocquet-Appel year-round-over-generations) → the cell is "settled".
- **Trigger**: a settled cell calls `society_from_character(density_per_km2, surplus_frac=store/cap)` →
  `egalitarian_forager → complex_forager` (packed OR surplus) → `stratified_chiefdom` (packed AND large surplus).
- **Apply**: `morph_to_society(name)` swaps the family/status knobs + κ. **Locality decision at S.4 (RT-1).**

## §4. Build steps (each: flaggable, gate, full-suite green, commit)

- **S.1 — Collective store refactor.** Per-cell granary; enforced overflow contribution; drop the per-agent
  store; individual survival = reserve. **Gate:** re-demonstrate the harsh-winter carrying-capacity lift.
- **S.2 — Cred-weighted draw (the inequality engine). ✅ BUILT 2026-06-25.** The lean-season granary is
  allocated by **status^κ** (the same `base_status`/κ as the meat pool), capped at each agent's deficit
  (`allocate_store_draw`). **Gate (mechanism, deterministic unit tests):** κ=0 → equal split (egalitarian);
  κ>0 → high-cred draws more (3:1 weight → 75:25); capped at deficit → leftover stays, low-cred still gets a
  share (RT-2 no annihilation). **Emergent finding:** in this density-regulated regime winter *starvation* is
  ~nil even with a scarce granary (baseline Siler mortality trims the population first), so the draw's
  inequality manifests as a winter-*wealth* differential, not death — subtle + meat-pool-confounded at the
  individual level. **The society-level inequality is therefore the S.4 output** (a `stratified_chiefdom`
  emerging), where it is visible and meaningful. Mechanism proven; emergent demonstration → S.4.
- **S.3 — Maintenance/spoilage. ✅ BUILT 2026-06-25.** `storage_decay` — every granary loses a fraction each
  step (incl. abandoned ones → no stale free stores, addresses the RT free-rider). **Gate met (monotonic):**
  harsh winter, eq_pop OFF=199; ON decay=0→447, 0.05→366, 0.2→311, **0.5→230 (≈ back toward the 199 immediate-
  return level)**; steady-state store shrinks in step. High-spoilage resources (fresh meat/fruit — tropical)
  ⇒ delayed-return not worth it ⇒ immediate-return — a *second* reason tropical foragers don't store, beyond
  the ET gate. Unit test: high decay erodes the capacity lift toward no-storage.
- **S.4 — Morph wiring. ✅ BUILT 2026-06-25 (PER-CELL).** RT-1 DECISION: **per-cell** society state (supervisor:
  a "band" = a cell's co-resident occupants — the model has no band entity, and the cell is the sharing unit, so
  per-cell is both simpler and more correct; stratified bands are sedentary so the place-attached state is
  stable). `self._cell_society`/`_cell_settle`; the harvest loop reads `kappa_cell` (the cell's society κ:
  egalitarian 0 … stratified 2) for the meat pool + store draw; a per-cell settlement detector calls
  `society_from_character(density, surplus_frac=store/cap)` and morphs with a `morph_settle_steps` (≈1 gen)
  hysteresis timer; abandoned cells decay back to egalitarian. **+ STORAGE TETHERING (the feasibility fix):**
  the diagnostic showed agents diffuse so thin (max occupancy **2**) that NO cell ever settled → the morph
  couldn't fire. Added `storage_tether_reserves` — a stocked band STAYS PUT (Testart sedentism; the user's
  "step 4") → max occupancy **2→19**, packed cells appear, surplus persists → the morph fires. **GATES met
  (scenario tests):** (1) cold/storable + tether → `complex_forager` cells emerge; (2) no tethering → no
  concentration → no morph; (3) warm world (ET-gated off) → never morphs (immediate-return geography);
  (4) **sustained famine → all cells COLLAPSE back to egalitarian**; (5) flag off → no morph state. `stratified_
  chiefdom` is reachable-in-principle but rare (needs packed AND surplus≥0.7 — the apex; calibration note).

## §5. Gates / validation

- Back-compat: `enable_storage=False` ⇒ bit-exact (per-agent removal + collective path both gated off).
- S.2 inequality: winter mortality skews to low-cred at κ>0; equal at κ=0.
- S.4 geography: morph fires in the overwintering+storable+packed zone ONLY; the tropical calibration biomes
  stay egalitarian (Woodburn — they don't store).
- No oscillation (RT-3 hysteresis): the morph holds, doesn't flicker year-to-year.

## §6. Red-team record (v1, self, 2026-06-25)

- **[BLOCKER → S.4 decision] κ/society state is GLOBAL, the morph is inherently LOCAL.** `morph_to_society`
  currently swaps the **global** DemographyConfig + substrate κ → it morphs the WHOLE WORLD to one type. But the
  Testart pattern is geographic (a settled river-mouth band stratifies while interior bands stay mobile). **Fix
  options (decide at S.4):** (a) **global-morph-first** — aggregate conditions flip the whole world (simple
  stepping-stone, loses heterogeneity); (b) **per-band-local** — a per-agent `_society` tag + per-agent κ/knobs
  read by the economy (faithful, moderate refactor: the κ-read becomes per-agent). **S.1–S.3 use the existing
  global κ and don't need this; the fork is faced only at S.4.**
- **[MAJOR → fixed in design] free-riders raid an undefended store.** A per-cell store contributed-to by
  transient occupants and drawn by passers-by is incoherent. **Fix:** the store accumulates only under sedentism
  (low turnover), and the cred-weighted draw is over the cell's CURRENT occupants — in a *settled* cell those
  ARE the stable band; before settlement, stores barely build (mobile). Full territoriality/storage-defense
  (Testart) — excluding non-members — is a flagged simplification, not built in v1.
- **[MAJOR → fixed in design] winner-take-all draw would ANNIHILATE commoners.** A pure cred-proportional draw
  could starve all low-cred every winter → the band loses its commoners → unrealistic. **Fix:** reuse the
  GRADED, bounded κ share (`compute_harvest_shares`, the same as the meat pool) — low-cred get a *smaller*
  share, not zero. Inequality in survival, not annihilation.
- **[MAJOR → fixed in design] morph oscillation/flicker.** Without hysteresis a bad year could de-stratify then
  re-stratify. **Fix:** the settlement detector requires conditions SUSTAINED for T≈1 generation; reversion
  likewise → hysteresis. (S.4.)
- **[MINOR] no active leveling.** Real immediate-return foragers *resist* accumulation (Boehm reverse-dominance,
  demand-sharing). The model has no active leveling opposing the morph — so cold-zone egalitarians morph
  "too easily". Per Testart that direction is correct (cold+storable→delayed-return); an active-leveling
  counter-force (some bands resist) is a deferred refinement.
- **[MINOR] spoilage vs cap** are distinct (ongoing loss vs max size) — not a double-count; don't double-penalize.

## §7. Deferred / open

- Proto-ag yields = post-morph consequence (DEFERRED_MECHANICS **PA-1**).
- Full territoriality / storage-defense (exclusion of non-members); active leveling (Boehm); collective→despotic
  escalation. Per-band-vs-global locality = the S.4 decision.

**Lit:** Binford 2001, Testart 1982, Woodburn 1982, Hayden *Pathways to Power*, Ames 1994 — in LITERATURE.md
(storage entry) + to extend at S.2/S.4. MODEL_SPEC §4.5.10 (morph hooks), §4.5.11 (storage).
