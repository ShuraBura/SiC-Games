# SiC Games — Resource Return-Rate Table (Forage + Game)

**Status:** live (created 2026-06-16; merges the former `SiC_Games_Game_Return_Rate_Table.md` and the previously-scattered forage values into one home).
**Role:** the **authoritative derived view** for every per-biome resource cell value feeding `terrain.py` — `FORAGE_KCAL_TARGETS` / `FORAGE_KCAL_STD` (§2) and `GAME_KCAL_TARGETS` / `GAME_KCAL_STD` (§3). This document derives each `(mean, std)` with explicit arithmetic and cites every source.
**Authority:** citations live in `LITERATURE.md` (this is a derived view — correct LITERATURE.md first, this follows). Parameter-value mirror: `PARAMETERS.md §12.4` (forage) / `§13.3` (game). Mechanic: `MECHANISMS.md §9a`. Decision log: `ARCHITECTURE.md §12.1-N`.

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

**Desert — mean 730, std 210 [LIT].** SET 2026-06-15 (supervisor-approved; was the 1,201 midpoint). Bird 2009 (Am. Antiquity 74(1)), read via image render: **search-inclusive overall hunt-type rates** are the correct basis (§1.3). Bout-frequency-weighted mean of {sand monitor 641 (n=612), perentie 765 (n=78), bustard ~1,300 (n=91)} = 570,262/781 = **730** (median 765). **Std** = weighted std of those rates = **210** (CV 0.29). *Note:* the Bird 2009 **post-encounter** rates (Table 2/Fig 5, thousands; bustard tail >100,000) are a *different denominator* — not the basis. Hill kangaroo (n=289) excluded (overall rate not cleanly stated); feral cat opportunistic.

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

## §4 Combined source list

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
