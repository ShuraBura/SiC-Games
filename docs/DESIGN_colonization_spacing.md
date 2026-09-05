# DESIGN — Colonization + density-scaled village spacing (R-106, 2026-09-03)

Status: PROPOSED (diagnosis complete; not built). Owner decision required before build.

## 1. The problem

The canonical model reaches a Malthusian plateau (~5,585 people, seed 1) but at **~0.006 persons/km²** — about
8× below the Tallavaara regional anchor (0.05/km²) and **2% of the terrain's own tier-1 carrying capacity**
(Σ Tallavaara local capacity = 329,331 people = 0.35/km²). The world is rich; 94% of the land is rich and
empty. So the population is **trapped, not starved.**

## 2. Diagnosis (evidence)

The population is capped by **crowding-disease in over-packed villages**, and the excess dies in place instead
of colonizing the empty rich land next door. Confirmed by probe (seed 1, 1,800 steps):

| lever | pop | villages | peak cell | density/km² | village spacing |
|---|---|---|---|---|---|
| baseline (canonical) | 4,400 | 32 | 371 | 0.0047 | 3.2 cells |
| `bud_requires_occupancy` OFF | **18,131** | 720 | 245 | **0.0195** | **1.0 cell** |
| search radius 8 → 24 only | 3,517 | 30 | 358 | 0.0038 | 3.0 cells |
| both | 11,779 | 945 | 116 | 0.0127 | 1.0 cell |

- **`bud_requires_occupancy` is the trap.** With it on (adopted, Addendum 53), a shed faction does not found a
  village — it relocates and must independently gather 40 people to establish. On empty land nobody joins it, so
  it fails and the parent grows to 300–500 while budding can only *look* within 8 cells. Turning it off →
  population 4×, villages 22×, density 4× toward the anchor, peak crowding drops.
- **Reach is not the constraint** (radius 8 → 24 alone does nothing). Establishment is.
- **The cost** of turning it off is exactly what it was adopted to fix: spacing collapses to 1.0 cell
  (adjacent villages, overlapping catchments, mutual subsidy).

So the real tension is **colonization vs spacing**, previously seen as separate bugs (Addenda 52–53). It is one
fork: `bud_requires_occupancy` buys spacing by preventing establishment, which traps the population.

## 3. Anchors (literature, 2026-09-03)

- **Village size** — NW Coast winter villages ~250–1,500 people, 8–50 houses (Ames 2003; Maschner & Hoffman).
  The model already produces villages in this range (peak 300–500). Size is not the problem — village *count*
  is.
- **Village spacing** — no clean published "km apart" table; derived from density (well-anchored) + village
  size. Villages/camps sit ~10–35 km apart: ~10–20 km on rich aquatic coasts, ~30–35 km in sparse arid/cold.
  Villages cluster at resource *nodes* (river mouths, salmon streams), NOT on a uniform lattice.
- **The model's own biomes** (density-derived spacing at village size 300):

  | biome | eligible land | K/cell | spacing (median → rich cells) |
  |---|---|---|---|
  | coastal/temperate | 18% | 57 | 2.3 → 1.6 cells |
  | coastal/subtropical | 6% | 24 | 3.5 → 1.9 cells |
  | flat/tropical | 12% | 36 | 2.9 → 2.7 cells |
  | flat/savanna (arid) | 12% | 26 | 3.4 → 2.6 cells |
  | flat/boreal | 2% | 96 | 1.8 → 1.7 cells |

  Two findings: (a) the spacing gradient is **modest** (~1.6–3.5 cells, a 2× range — not 1 vs 3); (b) biome
  sparseness lives in the **eligible-land fraction** (coastal 18% → boreal 2%), NOT the spacing constant.
  Boreal is sparse because only its rare aquatic cells are settleable, not because its villages are far apart.
- **Aquatic richness cap** — the model's own validation data (Tallavaara `Dataset_4`, 357 groups) has observed
  density min 0.2 / median 11.9 / **max 494.9 persons/cell**. The model's aquatic cap (`AQUATIC_DENSITY_MAX =
  80`) lets the richest cells reach ~124/cell — ~8× the median but **~4× below the observed max**. The model
  cannot reproduce the densest (NW Coast) forager cells. Secondary lever: it only bites once colonization lets
  the population reach those cells.

## 4. The design

One coherent rule that gives BOTH colonization and biome-appropriate spacing:

> **A village over its fission threshold sheds its rival faction, which FOUNDS a daughter village directly on
> the nearest open storable cell that lies at least `d(biome)` from every existing village.**

Three parts:

1. **Colonization (found on empty land).** Replace the `bud_requires_occupancy` behaviour: the bud FOUNDS the
   daughter site directly (it does not wait for 40 people to re-aggregate). This is what lifts the population off
   the 2%-of-capacity trap.
2. **Density-scaled spacing `d(biome)`.** The daughter site must clear every existing village by a separation
   that SCALES with local productivity, from the anchors above:
   - rich cells (high K / aquatic) → **~1.6 cells** (~16 km),
   - median cells → **~2.5 cells** (~25 km),
   - poor cells → **~3 cells** (~30 km).
   Concretely: `d = clamp(round(sqrt(V_target / (K_local/100)) / CELL_KM), 1, 3)` — one formula, no free
   constant beyond the anchored village-size target `V_target ≈ 300`. This replaces both the rejected fixed
   50 km `bud_site_separation` and the 1-cell overlap of `bud_requires_occupancy` off.
3. **Eligibility carries biome sparseness.** Keep the storability bar (`settle_persist_threshold`) as-is — it
   already makes boreal sparse (2% eligible) and coastal dense (18%) the right way. Do NOT lower it (the probe
   showed lowering it settles poorer cells and REDUCES density).

Secondary (separate, optional): raise `AQUATIC_DENSITY_MAX` toward the observed forager top end so the richest
coastal cells can reach NW-Coast density — but only after colonization is in, and as its own calibrated change.

## 5. Why this should work

- Colonization frees the population to fill the rich empty land → density rises ~4× toward the anchor (probe).
- Density-scaled spacing keeps villages ~1.6–3 cells apart (the anchor), instead of the 1-cell overlap that
  reintroduces mutual subsidy, or the fixed 3-cell rule that is too sparse for a coast.
- Eligibility keeps each biome's regional density biome-appropriate without touching the spacing rule.

## 6. Validation plan (before adoption)

Build default-OFF, ablatable, CTB'd. Then, per biome (coastal/temperate, flat/savanna, flat/boreal), run to
plateau and check against the anchors:

- **regional density** approaches the biome's Tallavaara value (coastal ~0.05/km²; arid/boreal lower);
- **village spacing** lands in the density-scaled band (~1.6 cells coastal → ~3 cells arid);
- **village size** stays in 250–1,500 (no single-cell runaway);
- **population is stationary** (births ≈ deaths at plateau — the Malthusian equilibrium is preserved, not
  removed as with the catchment-spread experiment).

A CTB must prove the load-bearing invariant: a bud on an over-threshold village FOUNDS a daughter on empty land
at ≥ `d(biome)` from every village, and OFF reproduces the current behaviour bit-exactly.
