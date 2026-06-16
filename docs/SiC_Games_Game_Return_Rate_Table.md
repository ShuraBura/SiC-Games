# SiC Games — Game Return-Rate Table

**Document:** `SiC_Games_Game_Return_Rate_Table.md`  
**Status:** COMPLETE — all 8 biome rows present; forest species sub-table populated from Table 2  
**Created:** 2026-06-14  
**Derived from:** LITERATURE.md Survey B entries. All authoritative citations live in LITERATURE.md; this document is the derived view. Correct citation details in LITERATURE.md first; this table follows.  
**Companion document:** `SiC_Games_Forage_Return_Rate_Table.md` (forage layer; this document is game only)

**Forage vs game category boundary (added 2026-06-15):** terrestrial vertebrate prey (hunting) = **game**; intertidal/shellfishing, roots, tubers, and plant resources = **forage**. Intertidal is therefore NOT a game cell — see the struck Intertidal row in §F.2 and §F.2.1.

---

## §F.1 Methodology

### Formula

```
kcal/hr = mass_live_per_hr (kg/hr) × edible_fraction × energy_density (kcal/kg)
```

### Constants

| Constant | Value | Source | Notes |
|---|---|---|---|
| edible_fraction | 0.50 | Hurtado & Hill 1987 | Conservative/consumed fraction; applied to all [CONVERTED] cells |
| energy_density | 1,460 kcal/kg | Hill et al. 1987, fn 3 | Used only for [CONVERTED] cells; [NATIVE] cells have kcal/hr reported directly |

**Lock:** These constants are locked and must not be changed without a supervisor-approved LITERATURE.md update citing a replacement source.

### Denominator standardisation rule

All cells use **search-inclusive** denominators (time from departure to return, including travel and search time).

**Exception — construct seam:** The forest cell (Hill et al. 1987) uses a **handling-only** denominator (search-time excluded). This asymmetry is accepted and documented; it is not a calibration error and cannot be harmonised to search-inclusive without a primary-source replacement and supervisor approval. The forest cell is therefore not directly comparable to all other cells on a time basis.

### [NATIVE] vs [CONVERTED]

| Tag | Meaning |
|---|---|
| [NATIVE] | Rate taken directly from source in kcal/hr — no formula applied |
| [CONVERTED] | Formula applied to raw kg/hr data from source |

### UNANCHORED policy

UNANCHORED cells are accepted gaps, not errors. They carry `—` in the cell value column. Model behaviour at UNANCHORED cells: zero game yield, or a flagged default placeholder if the build requires a non-zero value. Any placeholder must be documented as such and must never be cited as an empirical anchor. Filling an UNANCHORED cell requires: (a) a primary journal-article source, (b) LITERATURE.md update, (c) supervisor approval before implementation.

### Fat-season multiplier

×1.25 documented for forest game in April–June (ungulate and small-bodied game fat accumulation at warm→cold season transition; Hill et al. 1987). **Not applied to static cells.** Applied only when the seasonal layer is active.

---

## §F.2 Main table

| Biome | Status | Cell value (kcal/hr) | Denominator type | Source | Notes / caveats |
|---|---|---|---|---|---|
| Forest | LOCKED | By species — see §F.3 (range: 1,370–15,398 kcal/hr) | Handling-only | Hill et al. 1987, Table 2 [NATIVE] | Construct-seam exception: handling-only denominator (pursuit attempts + processing; search excluded). All other biomes search-inclusive. Fat-season multiplier ×1.25 (Apr–Jun) documented but NOT applied to static cell. |
| Savanna | LOCKED | ~518 kcal/hr (encounter/scavenge, all seasons); ~745 kcal/hr (intercept, dry season only) [CONVERTED] | Search-inclusive | Hawkes et al. 1991; Morin et al. 2024 | Intercept hunting ONLY in late dry season (Aug–Oct) at water aggregation sites. Group-size soft-gate sigmoid applies (see §F.4). Base encounter = 518 kcal/hr; dry-season intercept peak = 745 kcal/hr. |
| Grassland | LOCKED | 3,001 kcal/hr | Search-inclusive (whole-activity) | Hurtado & Hill 1987 | Corroborated at ~2,700 kcal/hr by Gurven & Hill 2009. Dry-season aggregation mechanism confirmed (caiman 44→489 kg/km², ~11× swing). |
| Desert | LOCKED | 641–1,761 kcal/hr by species | Search-inclusive | Bird et al. 2009, Table 1 [NATIVE] | Range reflects prey species composition. Individual species rates in Table 1 of source. Reptiles at low end; larger game at high end. |
| Wetland | UNANCHORED | — | — | — | No journal-article kcal/hr source found. Three candidates checked (Hill et al. 1997, Gurven & Hill 2009, Redford & Robinson 1987): all negative for time-denominated energetics. Gap accepted; cell remains empty at model-build time. |
| Mountain | UNANCHORED (permanent) | — | — | — | No source exists in the HG literature for mountain-specific game return rates. Permanent gap; fill requires primary-source discovery. |
| ~~Intertidal~~ | **NOT GAME → FORAGE** | — | — | ~~Bliege Bird et al. 2001~~ (cross-ref only) | **RECLASSIFIED 2026-06-15 (reconcile directive §4).** Intertidal foraging (shellfishing) is **forage**, not game — anchored in the forage layer (Bird 1997 Meriam) and applied in code as `SHORE_BONUS_KCAL = 1491.5` on `forage_kcal` (terrain.py:40). Holding it as a game cell **double-counts the same activity** across both fields. Provenance preserved: Bliege Bird et al. 2001, Table 2 reported 4,653 ± 1,213 kcal/hr [NATIVE], **gross pre-sharing only — net hunter yield ≈ 0** (costly-signaling; hunters retain no meat). Excluded from the game field; `GAME_KCAL_TARGETS` has no intertidal key. |
| Open water | ZERO — model scope | — | — | — | Fish/aquatic game outside current model scope. No source required until water-game stage is scheduled. |

---

## §F.2.1 Representative-value derivation (feeds `GAME_KCAL_TARGETS`)

Each biome's single **representative value** — the number `terrain.py:GAME_KCAL_TARGETS` scales toward — is derived here with explicit arithmetic, mirroring the forage layer's per-cell working. **This subsection is the authoritative home for the matching code constant** (reconcile directive §5). Every value carries `[PROVISIONAL — pending CC-1 ceiling]` until CC-1 lands.

### Forest — encounter(pursuit)-weighted mean  [method LOCKED by supervisor]

Table 2 (§F.3) reports per-species **pursuit counts `n`** = encounter frequencies, so the supervisor-locked method applies: weight each species' post-encounter rate by its pursuit count (a flat mean of the 1,370–15,398 spread overstates typical yield).

Dual-value resolution (Table 2 denominator, footnote a = "acquisition attempts plus all relevant processing"; search excluded):
- **White-lipped peccary → 5,323** (footnote d: "includes time spent following tracks"). Tracking is part of the *acquisition attempt*, so 5,323 matches the table-wide denominator; the alternative 8,755 ("only after animal is heard or seen") uses a narrower post-detection denominator and is rejected for consistency.
- **9-banded armadillo → kept as two genuine encounter modes**: surface 13,782 (n=26) and burrow 2,662 (n=31); both are post-encounter handling rates.

| Species | rate (kcal/hr) | n (pursuits) | rate × n |
|---|---|---|---|
| White-lipped peccary | 5,323 | 21 | 111,783 |
| Deer (red brocket) | 15,398 | 12 | 184,776 |
| Collared peccary | 6,120 | 51 | 312,120 |
| Paca | 4,705 | 53 | 249,365 |
| 9-banded armadillo (surface) | 13,782 | 26 | 358,332 |
| 9-banded armadillo (burrow) | 2,662 | 31 | 82,522 |
| Coati | 7,547 | 11 | 83,017 |
| Capuchin monkey | 1,370 | 59 | 80,830 |
| **Σ** | | **264** | **1,462,745** |

**Weighted mean = 1,462,745 / 264 = 5,540.7 ≈ 5,541 kcal/hr**  `[NATIVE, handling-only, PROVISIONAL]`.

*Cross-check (median):* 7 single-species values (armadillo internally pursuit-weighted to (13,782·26 + 2,662·31)/57 = 7,734) ranked = {1,370; 4,705; 5,323; 6,120; 7,547; 7,734; 15,398} → **median = 6,120**. The encounter-weighted mean (5,541) sits **below** the median because the most-frequently-pursued species (capuchin n=59 @ 1,370; paca n=53 @ 4,705; collared peccary n=51 @ 6,120) are mid-to-low value — weighting by how often each is actually hunted pulls the representative rate down, exactly the tail-resistance intended. Both 5,541 and 6,120 are far below the retired flat-mean 7,749.

**Result: forest representative value 7,749 → 5,541 kcal/hr.**

### Savanna — base encounter rate is the static cell  [CONVERTED]

Two figures exist (§F.2): base encounter/scavenge **~518 kcal/hr** (all seasons) and dry-season intercept **~745 kcal/hr** (Aug–Oct, water-aggregation sites only). The **static cell = 518** (all-seasons base, [CONVERTED] via mass × edible_fraction 0.50 × energy_density 1460 at Survey-B time). The 745 dry-season intercept is a **seasonality hook** — it gates on at aggregation sites in the late dry season (§F.4) — not the static value. No constant change (already 518.0).

### Grassland — direct lift  [NATIVE]

**3,001 kcal/hr** stated directly as kcal/hr in Hurtado & Hill 1987 (single source, no spread, no arithmetic — direct lift). Corroborated ~2,700 by Gurven & Hill 2009 but not blended. No constant change (already 3001.0).

### Desert — TO RESOLVE; left PROVISIONAL (supervisor-deferred)

**Source confirmed and read (2026-06-15):** Bird, Bliege Bird & Codding 2009, "In Pursuit of Mobile Prey: Martu Hunting Strategies and Archaeofaunal Interpretation," *American Antiquity* 74(1):3–29 — now in `literature/` and **read via page-image rendering** (pypdfium2; `pdftoppm`/poppler is absent, but pypdfium2 renders pages directly — §3.1's "page image, not OCR" was satisfied). **Note a source-identity point:** the game table's §F.5 list cited "Bird et al. 2009, *Journal of Human Evolution* 57:217–233" for desert; the PDF supplied is the *American Antiquity* paper. Both are Bird-et-al-2009 Martu studies; the numbers below are from the Am. Antiquity paper actually in hand.

**Two denominators in the paper — do not conflate them:**
- **Search-inclusive *overall hunt-type* return rate** (the paper's EIT = kcal/hr searching + handling). Sand-monitor hunting all-seasons average **≈ 641 kcal/hr** (519 kcal/hr search+handling, n = 612 bouts; p.13); perentie / bustard / hill-kangaroo hunt types run higher. **This is the measure the game table's "641–1,761" range refers to, and it is the correct basis for desert** because §F.1 fixes a *search-inclusive* denominator for all cells except forest.
- **Post-encounter return rate** (Table 2 / Figure 5, search *excluded*): much higher — sand monitor ≈ 4,931 kcal/hr/follow; bustard a massive right tail (≈ 68,000 without-pursuit mean; figure points > 100,000). **NOT the desert basis** under the search-inclusive convention; using these thousands would be a denominator error.

Hunted (game) species in the source: sand monitor (*Varanus gouldii*), perentie, python, blue-tongue/skink, feral cat, bustard, hill kangaroo (euro). (Cossid larvae, honey, bush tomato/raisin, grass seed, pencil yam = *collected* → forage, not game.)

**Verdict:** the **1,201 midpoint remains indefensible**, but for the right reason — the principled value is a **frequency-weighted mean (or median) of the search-inclusive *overall hunt-type* rates**, not the post-encounter figures. Because sand-monitor hunting is the single most common activity (≈ 641), a frequency-weighted value skews **below** the midpoint, likely ≈ 700–900 kcal/hr. Firm read so far: sand monitor ≈ 641; the per-hunt-type overall rates for perentie/bustard/kangaroo/cat still need extraction from the paper's results text before a number can be proposed. **Desert constant left UNCHANGED at 1,201 PROVISIONAL** (§3.4 supervisor-gated) — recommend the supervisor confirm the search-inclusive basis and the collapse rule (frequency-weighted vs median). O'Connell & Hawkes 1984 (Alyawara sandplain ~3,200 / mulga ~650; `Alyawara_plant_use_and_optimal_foraging.pdf` in `literature/`) is a patch-level sanity band only, never an override.

### Wetland / Mountain — UNANCHORED → 0

No journal kcal/hr source (§F.2, §F.5). `game_kcal = 0` at these biomes is a **gap (absence of data), not a measured zero**. Neither appears in `GAME_KCAL_TARGETS`; the mean-scaling loop (terrain.py:498) zeroes any biome absent from the dict.

---

## §F.3 Forest game: per-species post-encounter rates

**Source:** Hill et al. 1987, Table 2 — "Returns in Calories per Hour After Encounter with Various Ache Resources" (pp. 20–21). Extracted 2026-06-14 from `SiC_Games_A1.1_Hill1987_AcheForaging.pdf`.

**Denominator (Table 2 footnote a):** "Includes time spent in acquisition attempts plus all relevant processing." Search time excluded — handling-only. This is the construct-seam exception: all other game biomes in this document use search-inclusive denominators.

**Dual-value footnotes from source:**
- *Footnote d (white-lipped peccary):* "First number includes time spent following tracks. Second number only includes time after animal is heard or seen."
- *Footnote e (armadillo):* "First number is for animals encountered on the surface. Second number is for animals dug up."

**Note on tapir:** Tapir is mentioned in the paper as hunted by the Ache ("peccaries and tapir, and neither were ever ignored," p. 24) but does not appear in Table 2. Sample size was apparently insufficient to produce a reliable per-encounter rate estimate.

**Sub-table: Forest game — per-species post-encounter rates [Hill et al. 1987, Table 2, NATIVE]**

| Species (common name) | Scientific name (source taxonomy) | Pursuits (n) | Post-encounter rate (kcal/hr) | Notes |
|---|---|---|---|---|
| White-lipped peccary | *Tayassu pecari* | 21 | 5,323 / 8,755 | Footnote d: 5,323 includes tracking time; 8,755 from point animal heard/seen only |
| Deer (red brocket) | *Mazama americana* | 12 | 15,398 | |
| Collared peccary | *Tayassu tajacu* | 51 | 6,120 | |
| Paca | *Cuniculus paca* | 53 | 4,705 | |
| 9-banded armadillo | *Dasypus novemcinctus* | 26 (surface) / 31 (burrow) | 13,782 / 2,662 | Footnote e: 13,782 = surface encounter; 2,662 = burrow excavation |
| Coati | *Nasua nasua* | 11 | 7,547 | |
| Capuchin monkey | *Cebus apella* | 59 | 1,370 | Lowest-ranked game item; excluded from Ache diet when hunting with shotguns (return rate below opportunity cost) |

*All 7 rows extracted directly from Table 2. No values estimated or fabricated. Species are the complete game subset of Table 2 as printed (plant items, larvae, and honey excluded).*

---

## §F.4 Savanna soft-gate note

The savanna game mechanic uses a two-component parameterisation. The base encounter rate anchors on the all-seasons encounter/scavenge rate from Hawkes et al. 1991 (~518 kcal/hr converted, search-inclusive). A group-size modifier applies a soft-gate sigmoid — not a step function or hard access threshold — grounded in Morin et al. 2024. Success probability rises steeply but finitely with group size, peaking for high flight-initiation-distance (FID), herding or flocking prey species (the ungulate/savanna prey type most benefiting from coordinated intercept). The sigmoid shape is to be specified at model-build time; this table documents the empirical anchor and the functional form, not the fitted parameters. The dry-season intercept mechanism (switching on at water aggregation sites) is modelled as a seasonal-access modifier, not as a soft-gate parameter — it gates the 745 kcal/hr peak rather than the baseline encounter rate.

---

## §F.5 Source list

| Source | Role | Tag |
|---|---|---|
| Hill, K. et al. (1987). *Ethology and Sociobiology* 8, 1–36. | Forest game [BLOCKED] | [NATIVE] |
| Hawkes, K. et al. (1991). *Phil. Trans. R. Soc. B* 334, 243–251. | Savanna anchor | [CONVERTED] |
| Morin, D. et al. (2024). *Current Anthropology* 65(5), 876–921. | Savanna soft-gate | [CORROBORATION — cooperation mechanic] |
| Hurtado, A.M. & Hill, K. (1987). *Human Ecology* 15(2), 163–187. | Grassland anchor | [NATIVE kcal/hr stated] |
| Gurven, M. & Hill, K. (2009). *Current Anthropology* 50(1), 51–74. | Grassland corroboration | [CORROBORATION] |
| Bird, D.W. et al. (2009). *Journal of Human Evolution* 57, 217–233. | Desert anchor | [NATIVE] |
| Bliege Bird, R. et al. (2001). *Behav. Ecol. Sociobiol.* 50, 9–19. | Intertidal anchor | [NATIVE] |
| Smith, E.A. & Bliege Bird, R. (2000). *Current Anthropology* 41(4), 587–609. | Intertidal corroboration | [CORROBORATION] |
| Hill, K. et al. (1997). *Conservation Biology* 11(6), 1339–1353. | Wetland check — negative | [CHECKED-NEGATIVE] |
| Gurven, M. & Hill, K. (2009). *Current Anthropology* 50(1), 51–74. | Wetland check — negative | [CHECKED-NEGATIVE] |
| Redford, K.H. & Robinson, J.G. (1987). *American Anthropologist* 89(3), 650–667. | Wetland check — negative | [CHECKED-NEGATIVE] |
| Ugan, A. & Simms, S.R. (2012). *Journal of Ethnobiology* 32(2), 163–181. | Construct-reconciliation rule | [METHODOLOGICAL] |
