# Phase 1 — Stage 1: Forage Field + Terrain Diagnostics — CC Blueprint

**Repo:** `ShuraBura/SiC-Games`
**Authoritative docs:** local drive `G:\My Drive\docs\SiC Games\`; commit to GitHub per standard flow.
**Substrate:** `sic_terrain_prototype.html` (terrain generation already built and headless-validated). This stage populates the existing terrain with a literature-anchored forage field and adds two diagnostic layers. **No change to terrain generation primitives** except the NPP scale anchor (Task 4), which is additive.
**Execution mode:** Run to completion. One blocking mid-run checkpoint (Task 4, NPP anchor sign-off — see §Checkpoint). Otherwise default execution: failed acceptance check = CLAUDE.md STOP; passing run reports only must-be-seen artifacts.

---

## Task 0 — Phase-boundary front matter (documentation; do FIRST)

The project has two stage-numbering schemes that collide ("Stage 1" means both the old Sugarscape base model and this new terrain arc; "Stage 7" is the old arc). Resolve by declaring a phase boundary — **no retroactive renaming**.

0.1 — Add to ROADMAP.md (or INDEX.md, wherever canonical project structure lives) a boundary block:
- **Phase 0 — Social Mechanics: Stages 1–7.5 (complete).** Built on the Epstein & Axtell Sugarscape base. Historical stage numbers in older docs refer to this phase.
- **Phase 1 — Terrain & Resource Ecology: Stage 1 onward (active).** Fresh foundation; stage numbering restarts at 1. All new blueprints/directives are Phase 1 unless explicitly marked.

0.2 — Add to CLAUDE.md a disambiguation rule:
- *"Bare 'Stage N' references in documents dated before the Phase-1 boundary, or in `archive/`, are Phase 0. New work is Phase 1 and must carry the marker. When in doubt, ask — do not assume."*

0.3 — Do **not** edit historical stage numbers in any existing doc. The boundary declaration carries the disambiguation; bulk renaming is explicitly out of scope (error-prone, no benefit on completed work).

---

## Task 1 — Per-biome forage field, scaled to literature means, in kcal/forager-hr

**Current state:** the generator computes a normalized forage field:
`forage[i] = min(1, npp[i] * (0.6 + 0.6*forestness[i]))` — a smooth `[0,1]` field tracking NPP, boosted in forest/wetland. It has spatial texture (varies cell-to-cell within a biome). **Preserve this texture.**

**Goal (Option 2, per-biome mean-scaling):** Rescale the smooth field so each biome's *mean* forage equals its literature value in **kcal/forager-hr**, while preserving within-biome relative variation. Output field is in real kcal/hr units, not normalized.

### 1.1 — Per-biome target means (literature anchors; canonical home = LITERATURE.md Survey A)

| Biome (generator class) | Target mean (kcal/forager-hr) | Note |
|---|---|---|
| 1 wetland | 1428.3 | Cunningham, Okavango "Wet" |
| 2 forest | 2630 | Hill 1987, Ache palm |
| 3 savanna/edge | 257.7 | Berbesque & Marlowe 2009, Hadza tuber (Table 4). **See 1.3.** |
| 4 steppe/grass | 1125 | Hurtado & Hill 1987, Cuiva root collecting |
| 5 desert | **PROVISIONAL: 1200** (lean-ish, range 650–1925) | Single-value, undifferentiated desert. **See 1.4.** |
| 6 mountain | 5387 | Rhode & Rhode 2015, limber pine unhulled. **See 1.5 caveat.** |
| 0 water | 0 (land-only field) | Forage is land-only; shore handled in Task 3. |

### 1.2 — Scaling procedure (specify exactly)
For each land biome b:
1. Compute `mean_norm_b` = mean of the existing normalized `forage[i]` over all cells of biome b on the generated map.
2. Compute per-biome multiplier `k_b = target_mean_b / mean_norm_b`.
3. Set `forage_kcal[i] = forage[i] * k_b` for each cell i in biome b.
Result: biome mean = target mean exactly; within-biome relative spatial variation preserved.
- **Edge case:** if `mean_norm_b == 0` or biome b has zero cells on a given map, set those cells' forage_kcal to 0 and skip (do not divide by zero). Log which biomes were absent per map.
- The original normalized `forage[]` is retained as a separate field (do not overwrite — the scaled `forage_kcal[]` is a new field). Both available for downstream use.

### 1.3 — Savanna classifier/forage reconciliation (required note, not a code change)
The generator classifies biome 3 (savanna/edge) by **game density** (`game[i]>0.45 && forestness<0.5`). The forage value (257.7, tuber) is a **forage** quantity. These are different concepts coexisting on the same cell: the *classifier* uses game to identify savanna; the *forage field* assigns the tuber-derived forage mean. This is deliberate, not divergent. Record this explicitly in MODEL_SPEC.md so the dual use is documented.

### 1.4 — Desert value provisional flag
Desert mean is set to 1200 as a provisional lean-ish value (literature range 650–1925, sandplain vs mulga, O'Connell & Hawkes 1984; generator emits single undifferentiated desert). **Pre-register as provisional:** to be revisited once sweep distributions show how much desert appears across generated maps. Log in HYPOTHESES.md / MODEL_SPEC.md as a provisional locked parameter, flagged for reconsideration.

### 1.5 — Mountain foray-not-residence caveat (pre-registered expectation)
Mountain mean = 5387 is the literature-true *forage* return for alpine conifer (unhulled limber pine). **Pre-register the following expectation** in HYPOTHESES.md: ethnographically (Rademaker 2014, high-altitude Andes), high-altitude residence was driven by schedulable **game** (vicuña) plus **imported** lower-elevation carbohydrate — *not* by in-situ forage. Therefore, once the game field and seasonal seam exist (Stage 2+), mountain forage is expected to function as a **foray target, not a residence anchor**. In Stage 1 (static forage, no game/seasonal fields, no traversal-cost coupling active in agent loop), a high mountain forage mean **will temporarily over-attract** — this is an **expected, pre-registered Stage-1 artifact**, not a calibration error. Do not lower 5387 to compensate.

---

## Task 2 — Coast / body-of-water diagnostic (additive to characterizeMap())

Areal water abundance ≠ coastline. Coast is an *interface* property (land cells adjacent to water). A single large lake has less shore-per-area than many small ponds. Add a diagnostic that measures the land–water boundary and water-body structure.

2.1 — **Shore-cell set:** count land cells with ≥1 water neighbor (use the generator's existing neighbor convention — confirm von Neumann vs Moore from the terrain code; match whatever the flow-accumulation/`dist` logic uses). Report `shore_cell_fraction` = shore cells / total cells, and `shore_cell_count`.

2.2 — **Water-body structure:** connected-component labeling on the water mask (`isWater`). Report `n_water_bodies` (count of distinct connected water components) and the size distribution (at least: largest-body fraction, and count of bodies above a small size floor to ignore single-cell speckle). This distinguishes "one big lake" from "many small ponds" at equal water%.

2.3 — Add all fields to the per-map characterization vector returned by `characterizeMap()`. Measurement-only; no change to terrain generation.

---

## Task 3 — Shore forage modifier (intertidal entry; rides on coast diagnostic)

Intertidal/shore is **not a biome** in the generator taxonomy — it is a forage modifier on water-edge land cells. Bring it in via the shore-cell set from Task 2.

3.1 — For each shore cell (land, ≥1 water neighbor), add a shore-forage bonus toward the intertidal literature value **1491.5 kcal/forager-hr** (Bird 1997, Meriam reef-flat mean). The cell's total forage = its biome forage_kcal (Task 1) + shore bonus. **Specify the composition rule:** shore bonus is additive on top of underlying biome forage, capped so a shore cell's total does not exceed the intertidal top-resource ceiling (use 1491.5 as the bonus magnitude; do not stack to the 13064.8 top-resource figure — that is a single-resource max, not a cell mean).
3.2 — **Prevalence, not per-cell value, controls swamping.** The per-cell shore value stays literature-true (1491.5). How much shore exists is governed by map composition (coastline prevalence), measured by Task 2's `shore_cell_fraction`. Do **not** down-weight the 1491.5 value to manage swamping — instead, `shore_cell_fraction` becomes a sweep coordinate (Task 5) so the swamping question is answered empirically.
3.3 — **Shore-fish proxy:** shore fishing/gathering is folded into this shore modifier (same low-capital activity class). No separate fish field in Stage 1.
3.4 — **Offshore/boat fishing is OUT of Stage 1** — deferred capital-gated higher tier, anchor TBD, future stage. Do not implement. Record as deferred in ROADMAP.md.

---

## Task 4 — NPP scale anchor (makes NPP physically legible) — CHECKPOINTED

The generator's `npp[]` is normalized `[0,1]`. Anchor it to real units (g/m²/yr) so productivity is interpretable and the habitability coordinate (Task 5) reads in literature units.

4.1 — **Single-point anchor (pre-registered modeling assertion, not a measurement):** map the generator's forest NPP threshold (`npp ≈ 0.4`, the forest-onset boundary) to Tallavaara 2018's saturation breakpoint **~1,360 g/m²/yr** (Fig. 2A; mean of 1,372±103.4 and 1,349±118.0 SE). With a 0→0 origin, this gives a linear transfer `npp_gm2[i] = npp[i] * (1360 / 0.4) = npp[i] * 3400`.
4.2 — Record this anchor in MODEL_SPEC.md **explicitly as a single-point modeling assertion** (forest-onset ↔ empirical saturation point), with reasoning (Tallavaara: forest = highest HG carrying capacity, sits at/above saturation), **not** as a derived measurement. Flag that a true two-point anchor would need a second biome's empirical NPP range (future refinement, not required now).
4.3 — **Do NOT impose an NPP habitability floor.** Tallavaara shows low-productivity HG density is **biodiversity-limited, not NPP-floored** — there is no single-NPP survival cutoff in the data. Habitability is handled by Task 5 as a coordinate, not an NPP threshold.

### Checkpoint (blocking, mid-run)
After 4.1 is computed, **report the resulting transfer (the multiplier and the implied g/m²/yr values at the desert cutoff npp=0.12 and at npp=1.0) and STOP for supervisor sign-off** before Task 5 consumes the anchored scale. Rationale: a wrong anchor poisons the habitability coordinate and everything downstream keyed to real-unit NPP. This is the only mid-run stop. (Per blueprint convention: checkpoint added because a bad result changes a downstream document — the habitability metric.)

---

## Task 5 — Habitability as a coordinate (NOT a gate)

Desert-heavy and mountain-heavy maps are **interesting cases to study, not failures to filter.** Habitability is a continuous coordinate vector per map, reported and never thresholded for pass/fail.

5.1 — **Habitability coordinate vector** (add to `characterizeMap()`): per map, report
- `desert_fraction`, `mountain_fraction` (biome 5, 6 fractions)
- `mean_npp_gm2` (mean NPP in g/m²/yr via Task 4 anchor)
- `habitable_cell_fraction` (see 5.2 for the cell-level definition)
- (already present / confirm) per-biome composition, water%, shore_cell_fraction
These are **coordinates** — a map's position in habitability-space. No pass/fail threshold on any of them.

5.2 — **Habitable-cell definition (cell-level, for the fraction):** a land cell counts as habitable if it is not in a degenerate-substrate condition — i.e. it is a land cell on a valid-substrate map (see Task 6). Do **not** apply an NPP cutoff per cell (Tallavaara: no survival floor). The `habitable_cell_fraction` = land cells / total cells, reported so it can be cross-read against mean_npp_gm2. (If a more restrictive cell-level habitability is wanted later, it is an additive refinement; for Stage 1, habitable = land, and productivity is read via mean_npp_gm2 alongside.)

5.3 — **Coexistence reported as a function of coordinates.** The biome-coexistence diagnostic (already a permanent measurement layer) is reported across the habitability coordinate space, not gated by it. The *shape* of how coexistence/dynamics vary across the space is a must-be-seen artifact (§Must-be-seen), not an assertable threshold — do not invent a threshold for it (no HARKing).

---

## Task 6 — Degenerate-substrate validity guards (the ONLY pass/fail)

These are validity checks on whether a map is a usable measurement substrate — far out at the pathological edge. They are NOT habitability judgments. Everything inside these guards is a valid map at some coordinate.

6.1 — **Guard A (minimum habitable land):** map is a valid substrate only if `habitable_cell_count ≥ FLOOR`, where FLOOR is tied to the initial agent count (enough land to place a population at all). Set `FLOOR = max(initial_agent_count, 50)` as a provisional default — confirm `initial_agent_count` from the locked agent-config; if unavailable, use 50 and flag. This guards against the "98% water, nine land cells" pathology.
6.2 — **Guard B (no single-biome blob):** map is a valid substrate only if no single biome (including water) occupies ≥ **95%** of cells. Guards against the all-one-biome degenerate blob.
6.3 — Maps failing either guard are flagged `invalid_substrate=true` in the characterization vector and excluded from sweep dynamics runs, but are **counted and reported** (do not silently drop — report how many maps failed each guard, per §Never-bury-adverse-results).

---

## Task 7 — Sweep coordinate coverage

7.1 — Extend `runSweep()` (Latin hypercube) so the characterization vector for every swept map includes all new fields (Tasks 2, 5: shore_cell_fraction, n_water_bodies, desert_fraction, mountain_fraction, mean_npp_gm2, habitable_cell_fraction, invalid_substrate).
7.2 — Confirm the sweep **populates the extreme corners** of habitability-space — including desert-heavy and mountain-heavy maps. If the default knob ranges do not reach high-desert / high-mountain regions, extend the relevant knob ranges (aridity, mountainousness/relief) so the corners are sampled. The corners being reachable-and-sampled is an acceptance check.

---

## Documentation updates (fold into this run)

- MODEL_SPEC.md: forage_kcal field + scaling procedure (Task 1); savanna classifier/forage dual-use note (1.3); NPP anchor as single-point assertion (4.2); shore modifier (Task 3); habitability coordinate definition (Task 5); validity guards (Task 6).
- HYPOTHESES.md: desert provisional value flagged for revisit (1.4); mountain foray-not-residence pre-registered expectation (1.5).
- ROADMAP.md: phase boundary (0.1); offshore/boat-fishing deferred (3.4).
- CLAUDE.md: stage-disambiguation rule (0.2).
- Forage table (`SiC_Games_Forage_Return_Rate_Table.md`): already carries the canonical-home pointer to LITERATURE.md; no change needed beyond confirming consistency.

---

## Acceptance block (all must pass — green block = stage done, no report needed beyond must-be-seen)

**A1 — Forage field.** For every generated test map, each present land biome's mean `forage_kcal` equals its target mean (Table 1.1) within floating-point tolerance (±0.1 kcal/hr). Within-biome variance is non-zero where the source normalized field had non-zero variance (texture preserved, not flattened). Absent biomes logged, not errored.
**A2 — Scaling edge cases.** Zero-cell and zero-mean biomes handled without divide-by-zero; original normalized `forage[]` retained as a separate field.
**A3 — Coast diagnostic.** `characterizeMap()` returns `shore_cell_fraction`, `shore_cell_count`, `n_water_bodies`, largest-body fraction. On a hand-checkable test map (e.g. one central lake), shore_cell_count and n_water_bodies match a manual count.
**A4 — Shore modifier.** Shore cells' total forage = biome forage_kcal + 1491.5 bonus, capped per 3.1; non-shore cells unchanged. Per-cell shore value is exactly 1491.5 bonus (not down-weighted).
**A5 — NPP anchor.** `npp_gm2` field present; transfer multiplier = 3400 (1360/0.4); checkpoint reported and signed off before Task 5 consumed it.
**A6 — Habitability coordinate.** Characterization vector contains desert_fraction, mountain_fraction, mean_npp_gm2, habitable_cell_fraction. No pass/fail threshold applied to any of them. No per-cell NPP habitability cutoff exists in the code.
**A7 — Validity guards.** Guard A (habitable_cell_count ≥ FLOOR) and Guard B (no biome ≥95%) implemented; maps failing are flagged invalid_substrate and counted+reported, not silently dropped.
**A8 — Sweep coverage.** `runSweep()` characterization includes all new fields; the sweep samples desert-heavy AND mountain-heavy corners (knob ranges reach them). Verify by asserting the sweep produces ≥1 map with desert_fraction ≥ 0.5 and ≥1 with mountain_fraction ≥ 0.5 (extend knob ranges if not).
**A9 — Docs.** All documentation updates above committed; phase boundary + disambiguation rule present; no retroactive stage renaming performed.

---

## Must-be-seen artifacts (the only outputs that survive into a report)

These carry shape-dependent science that cannot be reduced to a threshold. Everything else is asserted by the acceptance block.

**M1 — Forage field maps:** render the scaled `forage_kcal` field for 2–3 representative maps, so the spatial texture (within-biome variation preserved) is visually confirmed, not just mean-checked.
**M2 — Habitability-space distribution:** scatter/heat of where the sweep lands in the habitability coordinate space (e.g. desert_fraction × mountain_fraction, colored by mean_npp_gm2). Shows what worlds the generator actually produces.
**M3 — Extreme-corner maps (small spread):** render a **small spread along each axis** — a few maps of increasing desert_fraction, and a few of increasing mountain_fraction — for eyeballing the harsh-world dynamics substrate. Not just the single most-extreme; a spread.
**M4 — Validity-guard failures:** count of maps failing Guard A and Guard B across the sweep (adverse-result reporting; one line if zero).

---

## Stopping rules

- Failed acceptance check → CLAUDE.md failed-gate STOP. Do not self-resolve a failed gate as a coding-agent judgment call.
- Task 4 checkpoint → STOP for sign-off before Task 5.
- Any literature value or anchor that cannot be applied as specified → STOP and report the specific blocker; do not substitute a convenient value.
- Do NOT self-upgrade any citation tag; all forage values trace to LITERATURE.md Survey A entries (canonical).

*End of blueprint.*
