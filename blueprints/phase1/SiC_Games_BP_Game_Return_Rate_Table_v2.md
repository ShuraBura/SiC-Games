# SiC Games — Blueprint: Game Return-Rate Table, MODEL_SPEC Methodology Block, and LITERATURE.md Updates

**Document:** `SiC_Games_BP_Game_Return_Rate_Table_v2.md`  
**Status:** READY FOR EXECUTION  
**Deliverables:** (1) `SiC_Games_Game_Return_Rate_Table.md`, (2) methodology block written to `MODEL_SPEC.md`, (3) LITERATURE.md entries for all 13 sources  
**Must-be-seen artifacts:** None — empty set. Green acceptance block = stage complete. No prose report required.

---

## §1 Context and scope

This blueprint closes the game return-rate literature survey and writes the resource-layer methodology into MODEL_SPEC.md. Three tasks run in sequence: LITERATURE.md first (entries must exist before any citation tag is written elsewhere), then the game return-rate table (cites those entries), then the MODEL_SPEC.md methodology block (references both). No simulation code is touched. No parameters are derived or changed.

---

## §2 Task 1 — LITERATURE.md entries

For each source below: check whether an entry already exists (match on DOI or author-year). If present and complete, skip. If absent or incomplete, write or complete the entry using the specification given. Entries must follow the existing LITERATURE.md format exactly (do not invent a new format).

**Do not** mark any entry `[VERIFIED]` unless it already carries that tag in the existing file. Sources checked for content and found negative are logged with explicit negative finding — this is required, not optional.

### 2.1 Sources to log

---

**Hill et al. 1987** — Ache foraging decisions  
DOI: 10.1007/BF02692976 (Ethology and Sociobiology 8:1–36)  
Role: Forest game return rates [NATIVE]. Primary anchor for forest biome. Post-encounter rates by species from Table 2 entered directly without formula conversion. Handling-time denominator only (search time excluded) — flagged as construct-seam exception; all other biomes use search-inclusive rates.  
Negative check: not checked for wetland (not relevant scope).

---

**Hawkes et al. 1991** — Hadza hunting income patterns  
DOI: 10.1098/rstb.1991.0106 (Phil. Trans. R. Soc. B 334:243–251)  
Role: Savanna game return rates [CONVERTED]. Anchor for savanna biome. Raw kg/hr rates converted to kcal/hr via formula (edible_fraction=0.50, energy_density=1,460 kcal/kg). Dry-season intercept hunting (water aggregation) confirmed as the savanna game access mechanism.  
Negative check: not applicable.

---

**Morin et al. 2024** — Why do humans hunt cooperatively  
DOI: 10.1086/732354 (Current Anthropology 65)  
Role: Savanna cooperative hunting soft-gate. Communal drive success 67.2% vs solo encounter 42%; herding/flocking species ~2× communal advantage. Grounds the soft-gate sigmoid for group-size effect on savanna game yield. Per-capita CDH return rates by species available in Table 1. Not used as primary kcal/hr anchor (Hawkes 1991 holds that role); used for cooperation mechanic parameterisation only.  
Negative check: not applicable.

---

**Janssen & Hill 2014** — Cooperative hunting among Ache, ABM insights  
DOI: 10.1007/s10745-014-9693-1 (Human Ecology 42)  
Role: Forest cooperative hunting calibration. Cooperative hunting net −4% on mean yield (2.82 vs 2.95 kg/day) but cuts zero-meat-day probability 52%→9% (83% reduction). Optimal band 7–8 hunters. Risk/return tradeoff, not a feasibility cliff. Used for forest cooperation mechanic parameterisation. **Corrected finding:** prior project notes incorrectly described a feasibility cliff; this entry carries the corrected reading.  
Negative check: not applicable.

---

**Hurtado & Hill 1987** — Early dry season subsistence ecology of Hiwi/Cuiva foragers  
DOI: 10.1007/BF02692303 (Human Ecology 15:163–187) [confirm DOI with file]  
Role: (1) Grassland game anchor at 3,001 kcal/hr (search-inclusive, whole-activity denominator). (2) Source of edible_fraction constant = 0.50 (conservative/consumed fraction). (3) High-amplitude seasonal anchor: ~90% annual rain in wet season, wet=lean (flood suppresses access), dry=game-fat via aggregation (caiman 44→489 kg/km², ~11× swing).  
Negative check: not applicable.

---

**Gurven & Hill 2009** — Why do men hunt?  
DOI: 10.1086/596611 (Current Anthropology 50:51–74)  
Role: Grassland corroboration only. Hiwi grassland hunting ~2,700 kcal/hr consistent with Hurtado & Hill 1987 anchor (3,001 kcal/hr). Theory/review paper — no new energetics data. **Checked for wetland game kcal/hr: negative.** Does not anchor wetland.  
Citation tag: [CORROBORATION — do not use as primary anchor]

---

**Bird et al. 2009** — Martu hunting strategies  
DOI: 10.1016/j.jhevol.2008.11.004 (Journal of Human Evolution 57:217–233)  
Role: Desert game return rates [NATIVE]. Primary anchor for desert biome. Table 1 rates by species entered directly (641–1,761 kcal/hr range), search-inclusive denominator. No formula conversion applied.  
Negative check: not applicable.

---

**Ugan & Simms 2012** — Prey mobility, prey rank, and foraging goals  
DOI: 10.1007/s10963-012-9055-4 (Journal of Ethnobiology 32:163–181) [confirm DOI with file]  
Role: Construct-reconciliation rule. Grounds the forage≠game distinction: mobile prey ranks differ from sedentary resource ranks; mobile prey mobility and detectability must be factored into encounter rates. Used as methodological anchor for the biome-binning rule (why game peaks at savanna/edge rather than forest, despite forest having high NPP).  
Negative check: not applicable.

---

**Bliege Bird, Smith & Bird 2001** — Hunting handicap / costly signaling  
DOI: 10.1007/s002650100338 (Behavioral Ecology and Sociobiology 50:9–19)  
Role: Intertidal game anchor [NATIVE]. Gross pre-sharing turtle hunting rate 4,653 ± 1,213 kcal/hr (hunting season, search-inclusive, Table 2). Net consumption is negative (costly-signaling context; hunters retain no meat). **Mandatory caveat:** cell value represents gross pre-sharing return rate only; functional forager yield is near zero. Do not use net yield figure for this biome without explicit justification.  
Negative check: not applicable.

---

**Smith & Bliege Bird 2000** — Turtle hunting and tombstoning  
DOI: 10.1086/317987 (Current Anthropology 41:587–609) [confirm DOI with file]  
Role: Intertidal yield corroboration only. Confirms mean edible turtle yield ~50.1 kg. No hunt-time denominator — cannot compute kcal/hr independently. Superseded for rate purposes by Bliege Bird et al. 2001.  
Citation tag: [CORROBORATION — rate superseded by Bliege Bird et al. 2001]

---

**Hill et al. 1997** — Mbaracayu hunting impact  
DOI: 10.1046/j.1523-1739.1997.96048.x (Conservation Biology 11:1339–1353) [confirm DOI with file]  
Role: Conservation/impact paper. **Checked for wetland game kcal/hr: negative** — zero energetics data. Caiman appears as trace Ache prey (5 individuals, 25 kg total) with no time denominator. Does not anchor wetland. Corroborates Ache forest prey composition only.  
Citation tag: [CHECKED — negative for wetland; forest prey composition corroboration only]

---

**Redford & Robinson 1987** — Game of choice: Indian and colonist hunting in the Neotropics  
DOI: 10.1525/aa.1987.89.3.02a00070 (American Anthropologist 89:650–667)  
Role: **Checked for wetland game kcal/hr: negative.** Paper's metric is a dimensionless Harvest Rate (animals killed per consumer per year), not a time-denominated energetics figure. Capybara (*Hydrochaeris hydrochaeris*) harvest rate = 0.154 animals/consumer-year (range 0.013–0.580, n=5 studies). Caiman appears in qualitative ranking only. No kcal/hr data for any species. Cannot feed the return-rate formula.  
Citation tag: [CHECKED — negative for wetland; offtake index only, no energetics]

---

**De Vynck et al. 2016** — Seasonal availability of edible underground carbohydrate resources  
DOI: [confirm DOI with file — South African Journal of Science or similar]  
Role: Forage seasonality anchor for the phenomenological seasonal curve. USO availability peaks ~6-month window July–December; lean season December–February (hot-dry summer). Primary empirical anchor for the fynbos/low-latitude forage seasonal signal shape. Amplitude: moderate (not the flat-forest end, not the high-llanos end).  
Negative check: not applicable.

---

### 2.2 Acceptance check — Task 1

```
ASSERT: all 13 entries present in LITERATURE.md (match on DOI or author-year)
ASSERT: all entries with negative findings carry explicit negative-finding text
ASSERT: Bliege Bird 2001 entry contains mandatory costly-signaling caveat
ASSERT: Janssen & Hill 2014 entry contains corrected-finding note
ASSERT: no entry carries [VERIFIED] tag unless it pre-existed with that tag
```

If any assertion fails: STOP. Log which entry failed. Do not proceed to Task 2.

---

## §3 Task 2 — Build `SiC_Games_Game_Return_Rate_Table.md`

Build the game return-rate table as a standalone markdown document. Mirror the structure of `SiC_Games_Forage_Return_Rate_Table.md` (header block, methodology note, table body, footnotes, source list). Do not copy forage values into this document — it is game only.

### 3.1 Table structure

The table has one row per biome. Columns:

| Column | Content |
|---|---|
| Biome | Terrain biome name (match terrain prototype biome names exactly) |
| Status | LOCKED / PARTIAL / UNANCHORED |
| Cell value (kcal/hr) | Point estimate or range; UNANCHORED cells: `—` |
| Denominator type | Search-inclusive / Handling-only / Whole-activity |
| Source | Author-year; tag [NATIVE] or [CONVERTED] as applicable |
| Notes / caveats | Mandatory flags; empty if none |

### 3.2 Cell values

| Biome | Status | Cell value | Denominator | Source | Notes |
|---|---|---|---|---|---|
| Forest | LOCKED | Hill 1987 Table 2 by species (multi-row — see §3.3) | Handling-only | Hill et al. 1987 [NATIVE] | Construct-seam exception: handling-only denominator. All other biomes search-inclusive. Fat-season multiplier ×1.25 documented but NOT applied to static cell (Apr–Jun forest only). |
| Savanna | LOCKED | Hawkes et al. 1991 [CONVERTED]; soft-gate sigmoid from Morin 2024 | Search-inclusive | Hawkes et al. 1991; Morin et al. 2024 | Cooperation mechanic: soft-gate sigmoid, not hard step. See §3.4. |
| Grassland | LOCKED | 3,001 kcal/hr | Search-inclusive (whole-activity) | Hurtado & Hill 1987 | Corroborated at ~2,700 kcal/hr by Gurven & Hill 2009. |
| Desert | LOCKED | 641–1,761 kcal/hr by species | Search-inclusive | Bird et al. 2009 [NATIVE] | Range reflects species composition. See Table 1 in source. |
| Wetland | UNANCHORED | — | — | — | No journal-article source found. Three candidates checked (Hill 1997, Gurven & Hill 2009, Redford & Robinson 1987): all negative for kcal/hr. Gap accepted; cell remains empty at model-build time. |
| Mountain | UNANCHORED (permanent) | — | — | — | No source exists in the literature for mountain-specific game return rates. Permanent gap. |
| Intertidal | LOCKED | 4,653 ± 1,213 kcal/hr | Search-inclusive | Bliege Bird et al. 2001 [NATIVE] | MANDATORY CAVEAT: gross pre-sharing rate only. Net hunter yield ≈ 0 (costly-signaling context). Do not use as functional forager return rate without explicit justification. |
| Open water | ZERO — model scope | — | — | — | Fish/aquatic game outside current model scope. |

### 3.3 Forest species sub-table

The forest cell is not a single number. Write a sub-table beneath the main table with the per-species post-encounter rates from Hill 1987 Table 2. Include: species common name, species scientific name (where available in source), post-encounter return rate (kcal/hr), and sample size if reported. Label this sub-table explicitly as "Forest game: per-species post-encounter rates [Hill et al. 1987, Table 2, NATIVE]."

CC: extract these values from the Hill 1987 PDF already in project files (`SiC_Games_A1_1_Hill1987_AcheForaging.pdf`). Do not fabricate or estimate values not present in the source. If a species row is illegible or absent from the PDF, flag it as [NOT READABLE — omit].

### 3.4 Savanna soft-gate note

Below the main table, include a short methodology note (3–5 sentences) describing the savanna cooperation mechanic: the base encounter rate anchors on Hawkes et al. 1991; the group-size modifier applies a soft-gate sigmoid (not a step function) grounded in Morin et al. 2024; success probability rises steeply but finitely with group size, peaking for high-FID herding/flocking prey. State that the sigmoid shape is to be specified at model-build time; this table documents the empirical anchor and the functional form, not the fitted parameters.

### 3.5 Methodology header block

At the top of the document, before the table, write a methodology block covering:

1. **Formula:** `kcal/hr = mass_live_per_hr × edible_fraction × energy_density`
2. **Constants:** `edible_fraction = 0.50` (Hurtado & Hill 1987, conservative/consumed); `energy_density = 1,460 kcal/kg` (Hill 1987, fn 3)
3. **Denominator standardisation rule:** all cells use search-inclusive denominators (time from departure to return, including travel and search). Exception: forest (Hill 1987) uses handling-only denominator — flagged as construct-seam, noted in table.
4. **Native vs. converted:** [NATIVE] = rate taken directly from source without formula application. [CONVERTED] = formula applied to source data.
5. **Unanchored policy:** UNANCHORED cells are accepted gaps, not errors. They remain empty at model-build time. Any future fill must cite a primary source and update LITERATURE.md before implementation.
6. **Fat-season multiplier:** ×1.25 documented for forest April–June (ungulate fat content; Hill 1987). Not applied to static cells. Applied only when the seasonal layer is active.

### 3.6 Acceptance check — Task 2

```
ASSERT: file SiC_Games_Game_Return_Rate_Table.md exists in project docs directory
ASSERT: table contains exactly 8 biome rows (Forest, Savanna, Grassland, Desert, Wetland, Mountain, Intertidal, Open water)
ASSERT: all LOCKED cells have a non-empty source citation
ASSERT: all UNANCHORED cells contain "—" in the cell value column, not a number
ASSERT: Intertidal row contains the mandatory costly-signaling caveat text
ASSERT: forest species sub-table is present and contains at least 5 species rows
ASSERT: savanna soft-gate note is present
ASSERT: methodology header block is present and contains all 6 items listed in §3.5
ASSERT: no cell value is fabricated — every number traces to a named source
```

If any assertion fails: STOP. Log which assertion failed. Do not proceed to Task 3.

---

## §4 Task 3 — MODEL_SPEC.md methodology block

Write a new section to MODEL_SPEC.md titled **"Resource Layer: Literature Treatment and Seasonal Architecture"** (or insert under the existing resource section if one exists — check first). This section documents how literature values were processed into model inputs and how the seasonal and star-mechanics layers connect to the resource curves. It is a permanent methodological record, not implementation code.

### 4.1 Subsections to write

---

#### 4.1.1 Return-rate formula and constants

Document the canonical formula, the two constants (edible_fraction, energy_density), their sources, and the rationale for each. State that these constants are locked and must not be changed without a supervisor-approved LITERATURE.md update citing a replacement source.

---

#### 4.1.2 Native rates vs. converted rates

Define the [NATIVE] and [CONVERTED] distinction. State which biomes use which. Explain the construct-seam: the forest cell uses a handling-only denominator while all others use search-inclusive denominators. This asymmetry is accepted and documented; it is not a calibration error. Any future attempt to harmonise the forest cell to a search-inclusive denominator requires a primary-source replacement and supervisor approval.

---

#### 4.1.3 Unanchored cells policy

State: wetland and mountain game cells are UNANCHORED (no primary-source kcal/hr exists). Model behaviour at UNANCHORED cells: zero game yield, or a flagged default value if the build requires a non-zero placeholder. Any placeholder must be documented as such and must never be cited as an empirical anchor. Filling an UNANCHORED cell requires: (a) a primary journal-article source, (b) LITERATURE.md update, (c) supervisor approval before implementation.

---

#### 4.1.4 Forage seasonal signal

Document the phenomenological architecture of the forage seasonal curve:

- **Functional form:** one periodic signal per biome, parameterised by (amplitude A, phase φ, lean-season cause). Not a mechanistic NPP model. Curves are fit to the HG forage-availability literature; no insolation→NPP transfer function is used.
- **Empirical anchors by biome:**
  - Forest (Ache): low amplitude; caloric availability roughly flat year-round; compositional variance only.
  - Llanos/grassland (Hiwi): high amplitude; wet season = lean (flood suppresses access); dry season = game-fat via aggregation. Approximately 90% of annual rain in 7-month wet season.
  - Fynbos/shrubland (De Vynck 2016): USO availability peaks July–December; lean season December–February (hot-dry summer).
  - Savanna (Hadza): dry-season water aggregation makes game accessible; intercept hunting switches on late dry season. Moderate amplitude.
- **Amplitude range:** forest ≈ flat (low end); llanos ≈ 90% rain in half the year (high end). This empirical range is the Earth reference; the star-mechanics lottery extends or contracts within it (see §4.1.6).
- **Signal is world-level, not layer-level:** one insolation signal per world, read independently by both forage layer and game layer. The forage≠game distinction is carried in curve shape (caloric-value signal for forage; encounter-rate/access signal for game), not in separate timing systems.

---

#### 4.1.5 Game seasonal signal

Document how the game seasonal signal differs mechanistically from the forage signal:

- **Two distinct seasonal mechanisms, not one:**
  - *Value-via-fat* (forest, Ache): encounter rate is roughly aseasonal; caloric value per kill rises ~25% in April–June due to ungulate fat accumulation. The fat-season multiplier (×1.25) is documented in Hill 1987 and applied only when the seasonal layer is active.
  - *Access-via-aggregation* (savanna/llanos, Hadza/Hiwi): dry-season water concentration drives prey into predictable locations; encounter rate rises sharply as water sources shrink. Caiman 11× seasonal swing (Hiwi) and Hadza intercept-hunting activation (late dry season, Hawkes 1991) are the empirical anchors.
- **These mechanisms must not be collapsed into a single sine.** They have different functional forms: fat-value is a smooth multiplicative modifier on kill value; aggregation-access is a threshold-like modifier on encounter rate.
- **Game migration signal:** dry-season water aggregation confirmed in two independent systems (Hiwi, Hadza). Broader ungulate range shift (true migration) is thin in the current literature and deferred to the seasonal-game build stage. The game table documents static encounter rates; migration is a future mechanic.

---

#### 4.1.6 Star-mechanics seam: seasonal amplitude range

Document the architecture of the star-mechanics coupling:

- **What star mechanics do:** the per-world lottery draws a seasonal amplitude from a literature-grounded range. Stellar/orbital parameters (obliquity, eccentricity — Berger 1978, Spiegel 2009/2010, Kopparapu 2013, Kasting 1993) set the bounds of what is physically plausible for a habitable world. The drawn amplitude parameterises the forage and game seasonal curves for that world.
- **What star mechanics do not do:** they do not drive the resource curves tick-by-tick. There is no insolation→NPP→forage transfer function. The B-series physics papers earn their place by bounding the parameter draws, not by running inside the agent loop.
- **Coupling point:** the single explicit coupling between the stellar/orbital literature and the resource curves is the seasonal amplitude parameter. The star lottery sets amplitude; the phenomenological curve (anchored to the HG literature) determines the shape. No other per-step coupling exists at this stage.
- **Shock stochasticity:** the stochastic shock distribution (ENSO, megadroughts, volcanic forcing — Timmermann 2018, Cane 2005, Cook 2010, Sigl 2015, Wanner 2008, Mayewski 2004) is a separate derivation from the periodic seasonal signal. These two threads are kept distinct: the orbital papers bound the seasonal range; the climate-variability papers ground the shock distribution. They are not folded together.

---

#### 4.1.7 Climate catastrophe seam (stub)

Document the seam/hook only. The catastrophe mechanic is not built at this stage.

- **Seam definition:** the catastrophe hook is a world-level amplitude modifier applied to the insolation signal before the resource curves read it. A catastrophe event fires a multiplier (< 1.0 for a resource crash) or a floor suppressor against the seasonal amplitude for a defined number of steps.
- **Interface contract:** any future catastrophe mechanic must write to this interface and to nothing else in the resource layer. It must not directly modify cell values, biome assignments, or agent states.
- **Status:** STUB — interface defined, mechanic not implemented. The shock-distribution literature (Timmermann, Cook, Sigl, Cane) is in hand for when this stage is scheduled.

---

### 4.2 Acceptance check — Task 3

```
ASSERT: MODEL_SPEC.md contains section "Resource Layer: Literature Treatment and Seasonal Architecture" (or equivalent heading)
ASSERT: all 7 subsections (§4.1.1–4.1.7) are present
ASSERT: §4.1.7 is labelled STUB and contains the interface contract
ASSERT: no subsection invents a parameter value not grounded in the literature inventory above
ASSERT: the catastrophe seam subsection does not describe a built mechanic — stub only
ASSERT: the star-mechanics coupling section names amplitude as the single explicit coupling point
```

If any assertion fails: STOP. Log which assertion failed.

---

## §5 Stopping rules and definition of done

Tasks run in sequence: Task 1 → Task 2 → Task 3. A failed acceptance check in any task is a blocking STOP (per CLAUDE.md Rule 11). CC does not proceed to the next task after a failed gate.

Definition of done: all three acceptance blocks green, no fabricated values, no mid-run check-ins with supervisor unless a gate fails.

**Must-be-seen artifacts:** none. This blueprint produces no shape-dependent output requiring human review. A green acceptance run requires no prose report — one-line confirmation of green is sufficient.

---

## §6 Files touched

| File | Action |
|---|---|
| `LITERATURE.md` | Add/complete 13 entries (skip if already present and complete) |
| `SiC_Games_Game_Return_Rate_Table.md` | Create |
| `MODEL_SPEC.md` | Add section §"Resource Layer: Literature Treatment and Seasonal Architecture" |

No other files are modified. No simulation code is touched.
