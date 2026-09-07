# SiC Games — Resource Return-Rate Table (Forage + Game)

**Status:** live (created 2026-06-16; merges the former `SiC_Games_Game_Return_Rate_Table.md` and the previously-scattered forage values into one home).
**Role:** the **authoritative derived view** for every per-biome resource cell value feeding `terrain.py` — `FORAGE_KCAL_TARGETS` / `FORAGE_KCAL_STD` (§2) and `GAME_KCAL_TARGETS` / `GAME_KCAL_STD` (§3). This document derives each `(mean, std)` with explicit arithmetic and cites every source.
**Authority:** citations live in `LITERATURE.md` (this is a derived view — correct LITERATURE.md first, this follows). Parameter-value mirror: `PARAMETERS.md §12.4` (forage) / `§13.3` (game). Mechanic: `MECHANISMS.md §9a`. Decision log: `ARCHITECTURE.md §12.1-N`.

---

## §0 Load-bearing status — WHAT THESE NUMBERS ACTUALLY CONTROL (measured 2026-08-08)

**Read this before using any value below to explain a run.** These fields are **not** the model's food supply.
A cell's extractable kcal/step comes from the NPP-derived `NPPCapacityField` (`capacity.py`; Tallavaara 2018),
which the campaign passes as `harvest_field`. The two return-rate fields are separate quantities with narrower
jobs, established by **perturbation** (scale the field ×1000 or ×0, re-run, compare) rather than by reading call
sites — see `sic_games/tests/test_field_load_bearing_ctb.py`, which pins every statement here.

| Field | Live surfaces in a campaign run | Effect of ×1000 |
|---|---|---|
| `forage_kcal` (§2) | **(1)** founder **band placement** (`seed_band_positions*`, computed outside the model); **(2)** the per-person **forage cap** (`enable_forage_cap`); **(3)** the **agglomeration base** `A_cell = aggl_tier2 · S_pot · (forage_kcal · forage_cap_hours)` (`enable_agglomeration`) | placement collapses 67 → 8 distinct cells; harvest pool ×3.2 |
| `game_kcal` (§3) | **none** | **bit-identical** |

**`game_kcal` has never affected a run.** It is read only by `TerrainField.game_level`, called only from
`_step_agent`, which executes only when the multi-occupancy substrate is **disabled** *and* `game_stream=True`.
Every campaign is rivalrous and sets `game_stream=False`, and **no harness in the repository sets it True** —
only `tests/test_phase1_kcal.py`. Zeroing the whole game field or multiplying it by a thousand leaves the
trajectory bit-identical.

Consequences, stated plainly because they change how §3 should be read:

- **Meat in a campaign is `game_meat_frac × S`** — a **scalar** (0.55, the forest value), so the *same fraction
  of the capacity pool in every biome* (`phase1_model.py`, the rivalrous harvest). The per-biome hunting
  variation §3 encodes is **not in the model**. Two things that ARE still live and must not be swept in with
  this: the climate `meat_factor` (caribou herd swing) modulates meat in *time* on GRASS_STEPPE, and Cordain's
  per-biome `terrain.MEAT_FRAC` reaches the model by a different route — `terrain.RETURN_CV` →
  `enable_emergent_band_size`, on in `full_campaign.toml`. What is missing is a biome-varying **harvest split**,
  not every biome-varying diet term.
- **The §3 UNANCHORED zeros (wetland, mountain) cost nothing at present.** They are honest gaps in the table
  (§1.4) and `tests/test_phase1_kcal.py::test_game_kcal_zeroed_at_wetland` guards them, but no run outcome
  currently depends on them. Anchoring them is a prerequisite for a two-stream economy, not a fix for a live
  defect. *(A claim that the wetland zero causes a measurable failure was made on 2026-08-08 and retracted the
  same day — see RESULTS Addendum, commit `25df603`.)*
- **`forage_kcal`'s in-model influence is exhaustively two flags.** With `enable_agglomeration` and
  `enable_forage_cap` both off it is inert in-model; only the placement surface remains. That exhaustiveness is
  itself a test (`test_both_consumers_off_makes_it_inert`), so a third consumer added later fails loudly.

**Open, and deliberately not decided here:** whether to wire the two-stream economy so §3 becomes load-bearing,
or to retire §3 to a reference table and say so. That is a modelling decision for the supervisor.

---

## §1 Shared methodology

### §1.1 Formula & constants

```
kcal/hr = mass_live_per_hr (kg/hr) × edible_fraction × energy_density (kcal/kg)
```
applied only to `[CONVERTED]` cells; `[NATIVE]` cells report kcal/hr directly.

| Constant | Value | Source |
|---|---|---|
| edible_fraction | 0.50 | Hurtado & Hill 1987 (conservative consumed fraction) |
| energy_density | 1,460 kcal/kg | Hill et al. 1987, fn 3 (mixed-game tissue) |

**LOCKED** — change only via a supervisor-approved LITERATURE.md update.

### §1.2 [NATIVE] vs [CONVERTED]
`[NATIVE]` = rate taken directly from source in kcal/hr. `[CONVERTED]` = formula applied to raw kg/hr.

### §1.3 Denominator standardisation rule
All cells use **search-inclusive** denominators (departure→return, incl. travel + search). **Exception (construct seam):** forest *game* (Hill 1987) uses a **handling-only** denominator (search excluded) — accepted, documented, not harmonisable without a primary-source replacement.

### §1.4 UNANCHORED policy
UNANCHORED cells are accepted gaps (`—` in the value column → model yield 0, a gap not a measured zero). Filling one requires a primary source + LITERATURE.md update + supervisor approval.

### §1.5 Cell-value distribution — terrain-coupled lognormal `(mean, std)`
Each biome's cells are drawn from a literature-anchored **lognormal**, deterministic (no RNG), preserving terrain spatial structure (`terrain.py:_lognormal_rescale`; full spec MECHANISMS §9a.6):
1. rank biome cells by terrain field value → Hazen quantiles `q = (rank+0.5)/n`;
2. lognormal params: `σ² = ln(1+(std/mean)²)`, `μ = ln(mean) − σ²/2`;
3. `value = exp(μ + σ·Φ⁻¹(q))`, re-normalised to the exact biome mean.

Positive-only, right-skewed (matches foraging-return data), terrain-coupled ("game peaks in forest"), reproducible.

### §1.6 Std sourcing rule (supervisor, 2026-06-15)
Mine the std from the literature where the source reports a spread (SD / range / multi-value set); **else std = 10% of the mean** (`DEFAULT_STD_FRAC = 0.10`). Tags: `[LIT]` direct, `[LIT-DERIVED]` computed from a related statistic, `[RANGE-DERIVED]` from a min–max, `[10%-DEFAULT]` fallback.

### §1.7 Category boundary, shore bonus, fat-season
- **Forage vs game:** terrestrial vertebrate prey (hunting) = game; intertidal/shellfish, roots, tubers, plant resources = forage.
- **Shore bonus** (`SHORE_BONUS_KCAL = 1491.5`, Bird 1997 Meriam): additive on land cells with ≥1 water neighbour (forage layer).
- **Fat-season multiplier** ×1.25 (forest game, Apr–Jun; Hill 1987) — documented, **not** applied to static cells (seasonal layer only).

---

## §2 Forage return-rate table

### §2.1 Main table (`FORAGE_KCAL_TARGETS` / `FORAGE_KCAL_STD`)

| Biome | Mean (kcal/hr) | Std | Std tag | Source |
|---|---|---|---|---|
| Wetland | 1,428.3 | **3,362** | [LIT] | Cunningham diss (A1.4), Okavango "Wet" |
| Forest | 2,630.0 | **600** | [LIT] | Hill 1987, Aché palm products |
| Savanna | 257.7 | **182.1** | [LIT] | Berbesque & Marlowe 2009, Hadza tuber (Table 4) |
| Grassland | 1,125.0 | 112.5 | [10%-DEFAULT] | Hurtado & Hill 1987, Cuiva root collecting |
| Desert | 1,200.0 | **368** | [RANGE-DERIVED] | O'Connell & Hawkes 1984, Alyawara |
| Mountain | 5,387.0 | 538.7 | [10%-DEFAULT] | Rhode & Rhode 2015, limber pine unhulled |
| (Shore bonus) | +1,491.5 | — | [LIT] | Bird 1997 Meriam (additive, land-shore cells) |
| Water | 0 | — | OUT-OF-SCOPE | — |

### §2.2 Forage per-cell std derivations
- **Wetland — 3,362 [LIT].** Cunningham diss p.72: mean(Wet) 1,428.3, **median(Wet) 558.7** (n≈286, skewed). Lognormal from mean+median: mean/median = 2.557 → σ = 1.37 → std = mean·√(exp(σ²)−1) ≈ **3,362** (CV 2.35 — real skewed USO-foraging spread).
- **Forest — 600 [LIT].** Hill 1987 (p.20) palm-product rates {2,356; 3,219; 2,436; 2,243; 1,331} → cross-product std ≈ **600** (CV 0.23). Confirms the 2,630 mean ("2630 calories of palm products", p.11).
- **Savanna — 182.1 [LIT].** Berbesque & Marlowe 2009 **Table 4**: female tuber mean **257.7**, **SD 182.1** (CV 0.71). Direct literature SD.
- **Desert — 368 [RANGE-DERIVED].** O'Connell & Hawkes 1984 range 650–1,925 → uniform std = (1,925−650)/√12 = **368**. (Midpoint mean 1,200.)
- **Grassland — 112.5 [10%-DEFAULT].** Hurtado & Hill 1987 Table II states root collecting = 1,125 cal/hr as a **point mean**; no per-bout rate-SD published (paper SDs are minutes/person-days of effort) → 10% fallback. (1990 Hiwi paper corroborates 1,127; also no rate-SD.)
- **Mountain — 538.7 [10%-DEFAULT].** Rhode & Rhode 2015 gives limber-pine-unhulled as a single **calculated** value (5,387 = hulling rate × kernel fraction × energy); no SD/range for it → 10% fallback.

---

## §3 Game return-rate table

### §3.1 Main table (`GAME_KCAL_TARGETS` / `GAME_KCAL_STD`)

| Biome | Mean (kcal/hr) | Std | Std tag | Denominator | Source |
|---|---|---|---|---|---|
| Forest | 5,541 | **4,043** | [LIT, NATIVE] | Handling-only | Hill 1987 Table 2 (7 species) |
| Savanna | 518 | **1,158** | [LIT-DERIVED]* | Search-inclusive | Hawkes 1991 (base encounter, [CONVERTED]) |
| Grassland | 3,001 | 300.1 | [10%-DEFAULT, NATIVE] | Search-inclusive | Hurtado & Hill 1987 Table II (hunting) |
| Desert | 730 | **210** | [LIT] | Search-inclusive | Bird 2009 (overall hunt-type rates) |
| Wetland | 0 | — | UNANCHORED | — | no source |
| Mountain | 0 | — | UNANCHORED (permanent) | — | no source |
| ~~Intertidal~~ | — | — | **→ FORAGE** | — | reclassified (§3.5) |
| Open water | 0 | — | OUT-OF-SCOPE | — | — |

\* **Savanna game std is DERIVED + supervisor-review** — see §3.2.

### §3.2 Game representative-value + std derivations

**Forest — mean 5,541, std 4,043 [LIT, handling-only].** Pursuit-weighted mean of the 7 Hill 1987 Table 2 species (§3.3), weighting each post-encounter rate by pursuit count `n`; dual-value picks denominator-consistent (peccary 5,323 tracking-inclusive; armadillo kept as two encounter modes). Σ(rate·n)=1,462,745, Σn=264 → **mean = 5,541** (median cross-check 6,120; both ≪ the retired flat-mean 7,749). **Std** = pursuit-weighted std of the same species = **4,043** (CV 0.73).

**Savanna — mean 518, std 1,158 [LIT-DERIVED, supervisor-review].** Mean = all-seasons base encounter/scavenge rate (Hawkes 1991, [CONVERTED]); the 745 kcal/hr dry-season intercept is a **seasonality hook**, not the static value. **Std**: Hawkes 1991 reports small-game income 0.162 ± 0.362 animals/day → **CV 2.24**; applied to the mean → std ≈ **1,158**. Derived from income variance (not a direct rate-SD) — flagged for supervisor review; hunting is high-variance, so the 10% default (51.8) badly understated it.

**Grassland — mean 3,001, std 300.1 [10%-DEFAULT, NATIVE].** Hurtado & Hill 1987 Table II: men 20–60 (n=414 person-days), wild-game hunting (domestic-origin excluded) = **3,001 cal/hr** (direct). No per-bout rate-SD published → 10% fallback. Corroborated lower by Gurven & Hill 2009 (~2,700) and Hiwi 1990 (2,593) — different samples; 3,001 stands as the anchor.

**Desert — mean 995, std 490 [LIT].** R-79 CORRECTION (2026-07-17, supervisor-approved; supersedes the
2026-06-15 value 730). Bird 2009 (Am. Antiquity 74(1)) **Table 1, Return Rate/Bout (kcal/hr)** = the
search-inclusive overall basis (§1.3), read via image render. Bout-frequency-weighted mean of the four main
hunt types {sand monitor 641 (n=612), perentie 697 (n=78), bustard 1,761 (n=289), hill kangaroo 1,203 (n=91)}
= 1,065,060 / 1,070 = **995**. **Std** = bout-weighted std of those four rates = **490** (CV 0.49). Feral cat
(n=25) excluded as opportunistic. *Note:* the Bird 2009 **post-encounter** rates (Table 2/Fig 5, thousands;
bustard tail >100,000) are a *different denominator* — not the basis.
**Why the prior 730 was wrong (R-79):** it was an EXTRACTION ERROR against Table 1. It used perentie 765
(the table says **697**) and a third species labelled "bustard ~1,300 (n=91)" that was in fact **hill kangaroo**
(1,203, n=91), while "excluding kangaroo (n=289)" that was in fact **bustard**. So it silently dropped the
Martu's 2nd-most-frequent hunt (bustard, n=289) and swapped kangaroo in under bustard's name — computing
570,262/781 = 730 from {sand monitor, perentie, kangaroo}. The corrected all-four-hunts mean is **995 (+36%)**.

**Wetland / Mountain — UNANCHORED → 0.** No journal kcal/hr source; absent from `GAME_KCAL_TARGETS` (the loop zeroes any biome not in the dict). A gap, not a measured zero.

### §3.3 Forest game: per-species post-encounter rates

**Source:** Hill et al. 1987, Table 2 — "Returns in Calories per Hour After Encounter with Various Aché Resources" (pp. 20–21). **Denominator (footnote a):** acquisition attempts + processing; search excluded (handling-only — the §1.3 construct-seam exception).

| Species | Scientific name | Pursuits (n) | Post-encounter rate (kcal/hr) | Notes |
|---|---|---|---|---|
| White-lipped peccary | *Tayassu pecari* | 21 | 5,323 / 8,755 | fn d: 5,323 incl. tracking; 8,755 from heard/seen only |
| Deer (red brocket) | *Mazama americana* | 12 | 15,398 | |
| Collared peccary | *Tayassu tajacu* | 51 | 6,120 | |
| Paca | *Cuniculus paca* | 53 | 4,705 | |
| 9-banded armadillo | *Dasypus novemcinctus* | 26 (surface) / 31 (burrow) | 13,782 / 2,662 | fn e: surface vs burrow excavation |
| Coati | *Nasua nasua* | 11 | 7,547 | |
| Capuchin monkey | *Cebus apella* | 59 | 1,370 | lowest-ranked game |

*All 7 rows extracted directly from Table 2; the complete game subset (plant items, larvae, honey excluded). Denominator-consistent single-values used in §3.2: peccary 5,323; armadillo as two modes.*

### §3.4 Savanna soft-gate note
Savanna game uses a two-component parameterisation: a base encounter rate (Hawkes 1991 ~518, search-inclusive) plus a **group-size soft-gate sigmoid** (not a step/threshold; Morin et al. 2024) — success rises steeply but finitely with group size, peaking for high-FID herding/flocking prey. The sigmoid shape is specified at model-build time. The dry-season intercept (745 kcal/hr peak, at water-aggregation sites) is a **seasonal-access modifier**, not a soft-gate parameter.

### §3.5 Intertidal — reclassified game → forage (2026-06-15)
Intertidal shellfishing is **forage**, not game — anchored as `SHORE_BONUS_KCAL = 1491.5` (Bird 1997). Holding it as a game cell double-counted the same activity. Provenance preserved: Bliege Bird et al. 2001 Table 2 reported 4,653 ± 1,213 kcal/hr [NATIVE], **gross pre-sharing only — net hunter yield ≈ 0** (costly-signalling). Excluded from the game field; no `GAME_KCAL_TARGETS` intertidal key.

---

## §4 Day-to-day (TEMPORAL) return CV — `terrain.HUNT_CV` / `GATHER_CV` / `RETURN_CV`

**Role:** the variance a band **pools away by sharing**. Feeds the emergent-band-size risk-pooling optimum
`g* = CV/cv_safe` (PARAMETERS §21.1; RESULTS R-72). Added 2026-07-16.

### §4.1 Why this is a SEPARATE quantity from §2/§3's std (the v1/v2 bug)
`FORAGE_KCAL_STD` / `GAME_KCAL_STD` are **SPATIAL** — cross-cell spreads parameterising the terrain-coupled
lognormal *cell-value* draw (§1.5). §1.6's sourcing rule ("mine the std where the source reports a spread")
is **correct for that purpose**, and those values stand unchanged.

Risk-pooling asks a different question: *how much of one forager's DAY-TO-DAY luck does the group average
away?* Sharing cannot smooth a spread across habitat patches; it smooths the variance between a hunter's
good day and his empty day. Emergent-band-size v1/v2 fed the spatial field to a temporal law — a category
error in the **reuse**, not in the §2/§3 extraction. It produced incoherent CVs, because each biome's std
measures a different thing:

| biome | §2/§3 std is a spread across… | CV | kind |
|---|---|---|---|
| Forest | 7 species' post-encounter **means** (§3.3) | 0.73 | spatial/between-category |
| Desert | 3 hunt types' **rates** | 0.29 | spatial/between-category |
| Wetland | ~286 habitat samples (mean-vs-median skew) | 2.35 | spatial |
| Savanna | Hawkes small-game **income/day** | 2.24 | **temporal** (the lone exception; §3.2 already flagged it "for supervisor review") |
| Grass, Mountain | *(no data → 10%-DEFAULT)* | 0.08–0.10 | none |

Which side of the old `[15,45]` clamp a biome landed on was decided entirely by which *kind* of statistic its
source happened to report. That is a measurement artifact, not an environmental signal.

### §4.2 `HUNT_CV = 2.11` [LIT, measured — cross-cultural]
**Source:** `cchunts` (McElreath & Koster, GPLv3; archived at `literature/cchunts/`) — the per-trip data behind
**Koster et al. 2020**, *Sci. Adv.* 6:eaax9070, "The life history of human foraging". Per-trip harvests in kg
**including zero-return trips**. Extraction: `sic_games/outputs/climate_viz/extract_cchunts_cv.py`.

**Filter (each clause load-bearing):** `observed==1` — most cchunts datasets are *verbally reported*, and recall
bias under-reports empty-handed days, deflating the failure rate; `day_trip==1` — the statistic is per *day*;
`pooled==0` — individual attribution, not a group total; `sex=='M'`; adults (`age_dist_1 ≥ 18` where exact).

**Result — 10 societies, ~15,600 trips. Median daily-harvest CV = 2.11** (mean 2.61, range 1.53–4.64):

| people | biome | n | fail% | kg/day | CV |
|---|---|---|---|---|---|
| Piro (Peru) | trop forest | 93 | 34.4% | 8.31 | 1.53 |
| Punan (Indonesia) | trop rain forest | 123 | 66.7% | 20.32 | 1.81 |
| Baka (Cameroon) | trop rain forest | 144 | 31.9% | 4.06 | 1.91 |
| **Aché (Paraguay)** | **forest** | **14,071** | **51.6%** | **3.26** | **1.97** |
| Tsimane (Bolivia) | trop forest | 107 | 39.3% | 8.74 | 2.05 |
| Punan (Indonesia) | trop rain forest | 95 | 68.4% | 17.57 | 2.17 |
| **Martu (Australia)** | **desert** | **612** | **49.2%** | **2.31** | **2.92** |
| Tsimane (Bolivia) | trop forest | 105 | 23.8% | 11.44 | 3.12 |
| Baka (Cameroon) | trop rain forest | 51 | 27.5% | 17.34 | 3.94 |
| Wola (PNG) | montane forest | 218 | 78.0% | 0.05 | 4.64 |

**BIOME-INVARIANT — a measured negative result.** Forest alone spans 1.53–4.64; the Martu desert (2.92) sits
inside that range; two Baka samples (same people, same biome) give 1.91 vs 3.94. Hunting variance tracks prey
choice and technology, not environment ⇒ **a per-biome hunting CV is not supportable**, and the per-biome
gradient must come from the diet mix (§4.4) instead.

*Corroboration, independent of cchunts.* Daily CV from a Bernoulli failure structure is `√((1−p)/p)`:
Bird 2009 Table 1 (Martu) — hill kangaroo 79% fail → 1.94; bustard 56% fail → 1.13; and Hawkes 1991 p.244
(Hadza) — small game 14 animals/75 hunter-days → 2.09. All three bracket 2.11.

*The Hadza big-game outlier.* Hawkes 1991 p.244: "the Hadza took **one large animal every 29 hunter-days**"
→ p=0.034 → CV **5.29**. NOT used as the generic anchor: Hawkes states the Hadza take big game "to the virtual
exclusion of small-bodied prey" and that this "differs sharply from that of other low-latitude hunter-gatherers."
It is the documented extreme, consistent with the cchunts max (4.64), not the central case.

### §4.3 `GATHER_CV = 0.70` [LIT, direct bout-level SD]
**Berbesque & Marlowe 2009, Table 4** (read via image render — the table has no text layer): Hadza **female
tuber 257.7 ± 182.1 kcal/hr, N=56 foraging bouts** → 182.1/257.7 = **0.707**. `N` is bouts, so the SD is
bout-to-bout — the temporal statistic. Same table, other plant foods: baobab 0.85 (♀) / 0.95 (♂), berry 1.09.

*Corroboration.* Bird 2009 Table 1: **every** Martu plant food has **success rate = 1.00** (bulb, desert raisin,
grub, bush tomato, root, grass seed, nectar, tree seed), kcal/bout CV 0.20–0.98. **All gathering variance is
HOW MUCH; all hunting variance is WHETHER AT ALL** — which is why sharing targets meat (Kaplan & Hill 1985;
Hill 1987 p.13: "daily variance in calories acquired is much higher for hunting than it is for gathering").

### §4.4 `RETURN_CV` — per-biome, derived from the diet mix
Gather and hunt are independent streams ⇒ variances add. With `μ_g=(1−m)·μ`, `μ_h=m·μ` the mean cancels:

> **CV(m) = √( (1−m)²·GATHER_CV² + m²·HUNT_CV² )**,  `m` = `MEAT_FRAC` (Cordain 2000 Table 2, §4.5.5)

Because the stream CVs carry no biome signal (§4.2), **the entire per-biome gradient comes from the diet mix**:
meat-dependent foragers ride the high-variance stream and must pool more. Derived in code
(`terrain.biome_return_cv`), never hand-set.

| biome | Cordain environment | `m` | CV | `g*` at cv_safe=0.037 |
|---|---|---|---|---|
| Wetland | *(no Cordain analog → **absent**)* | — | **0.70** (GATHER_CV fallback) | 18.9 |
| Mountain | Temperate forest, mostly mountainous | 0.34 | 0.853 | 23.1 |
| Savanna | Tropical grassland (Hadza) | 0.38 | 0.912 | 24.6 |
| Desert | Desert grasses & shrubs (!Kung) | 0.45 | 1.025 | 27.7 |
| Forest | Subtropical rain forest (Aché) | 0.55 | 1.202 | 32.5 |
| Grass | Temperate grasslands (steppe/plains) | 0.66 | 1.413 | 38.2 |

**MOUNTAIN 0.34** is new: Cordain Table 2's "Temperate forest, mostly mountainous" = 20.5/(40.5+20.5) = 0.336,
an anchor the original lift missed. **WETLAND is deliberately ABSENT from `MEAT_FRAC`, not 0.0** — per §3.2's
own warning about the wetland/mountain game gap ("*A gap, not a measured zero*"), a 0.0 would assert that
wetland foragers eat no meat. `_return_cv_field` falls back to `GATHER_CV` for unanchored biomes: a conservative
choice (no manufactured pooling incentive), flagged as a fallback rather than a measurement.

**Calibration + prediction.** Mean CV 1.017; `cv_safe` = 1.017/27.5 = **0.037**, fitted ONLY to place the mean
band at Hill 2011's ~25–30. The **spread is then a free prediction: 0.70→1.41 = 2.0×, against Marlowe/Kelly's
observed band range 25–50 (also 2×)**, with every biome inside Hill 2011's observed 15–50.

---

## §5 Combined source list

| Source | Layer / role | Tag |
|---|---|---|
| Hill, K. et al. (1987). *Ethology & Sociobiology* 8, 1–36. | Forest game (Table 2); forest forage (palm) | [NATIVE / VERIFIED] |
| Hawkes, K., O'Connell & Blurton Jones (1991). *Phil. Trans. R. Soc. B* 334, 243–251. | Savanna game anchor + income variance | [CONVERTED] |
| Morin, D. et al. (2024). *Current Anthropology* 65(5), 876–921. | Savanna soft-gate (cooperation mechanic) | [CORROBORATION] |
| Hurtado, A.M. & Hill, K. (1987). *Human Ecology* 15(2), 163–187. | Grassland game + forage (Cuiva, Table II) | [NATIVE] |
| Hurtado, A.M. & Hill, K. (1990). *J. Anthropological Research* 46(3). | Grassland corroboration (Hiwi seasonality) | [CORROBORATION] |
| Gurven, M. & Hill, K. (2009). *Current Anthropology* 50(1), 51–74. | Grassland corroboration; wetland check (neg) | [CORROBORATION] |
| Bird, D.W., Bliege Bird & Codding (2009). *American Antiquity* 74(1), 3–29. | Desert game (Martu, overall hunt-type rates) | [NATIVE / VERIFIED] |
| O'Connell, J.F. & Hawkes, K. (1984). Alyawara plant use & optimal foraging. | Desert forage anchor (range) | [RANGE] |
| Cunningham, A. (Harvard diss.). Forager Habitat Quality. | Wetland forage anchor (Okavango) | [NATIVE / VERIFIED] |
| Berbesque, J.C. & Marlowe, F.W. (2009). *Evol. Psychol.* 7(4), 601–616. | Savanna forage anchor (Hadza tuber, Table 4) | [NATIVE / VERIFIED] |
| Rhode, D. & Rhode, J. (2015). *J. Calif. & Gt. Basin Anthropol.* 35(2), 291–298. | Mountain forage anchor (limber pine) | [NATIVE / VERIFIED] |
| Bird, R. Bliege et al. (2001). *Behav. Ecol. Sociobiol.* 50, 9–19. | Intertidal (→ forage cross-ref) | [NATIVE] |
| Bird, D.W. (1997). Meriam intertidal. | Shore bonus (forage) | [NATIVE / VERIFIED] |
| Tallavaara, M. et al. (2018). | NPP anchor (npp_gm2 scale) | [SINGLE-POINT] |

*Negative wetland-game checks (Hill 1997, Gurven & Hill 2009, Redford & Robinson 1987) and intertidal corroboration (Smith & Bliege Bird 2000) retained in LITERATURE.md.*

---

*End of Resource Return-Rate Table — created 2026-06-16 (merges the former Game Return-Rate Table + scattered forage values). Derived view; LITERATURE.md / PARAMETERS.md win on conflict.*
