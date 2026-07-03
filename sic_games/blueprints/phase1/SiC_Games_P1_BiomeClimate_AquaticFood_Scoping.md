# SiC Games — Phase 1 — Biome-Climate Realism + Aquatic-Food Fishery (the storable-aquatic-resource substrate)

**Status:** SCOPED 2026-07-03. Foundational substrate stage — needs supervisor sign-off + downstream re-validation before build. Phased so the low-risk part can land first.
**Motivates (R-46→R-48):** the society MORPH now needs a real driver of forager complexity = a dense STORABLE AQUATIC resource (Testart/Ames/Kelly — NW-Coast salmon, Calusa shellfish). Heuristic gates (wateracc, seasonality, npp) can't cleanly get "savanna egalitarian (Hadza) + montane complex (Plateau salmon)" because of two substrate gaps this stage fixes.

## 1. The two diagnosed gaps (with data)
**Gap A — biome ↔ climate are DECOUPLED.** `biome` is classified from elevation/slope/npp/`forestness` (moisture), NOT temperature (`terrain.py` ~L595). `temperature` is applied afterward as a pure **latitudinal** gradient (row 0 equator 27 °C → row N-1 pole 1 °C), with NO elevation lapse. Consequence (occupied-cell means, R-48 probe): **savanna 11.8 °C (coldest!), montane 15.3 °C (warmest)** — the OPPOSITE of Earth (real savanna warm-tropical; real montane cold). A cold-water (salmon) signal on this substrate would make savanna the *most* complex and montane egalitarian — inverted. Root: biomes aren't at realistic temperatures.

**Gap B — no aquatic-FOOD field.** The model has `wateracc` (water proximity — drinking, not food), `is_shore` (coastal mask + Bird-1997 shore bonus), `isRiver`. It has NO signal for a dense STORABLE aquatic FOOD (anadromous fish / shellfish density) — the thing that actually distinguishes a salmon river (complex) from a savanna river / desert oasis (egalitarian). At occupied cells `shore%`/`river%` read 0 (agents sit on land NEAR water), so even the existing aquatic masks don't discriminate.

## 2. Phased build

### Phase 1 — Temperature realism: elevation lapse [LOW RISK]
`T(cell) = T_latitude(row) − LAPSE × elevation_m`, `elevation_m = elev × reliefAmpM`, `LAPSE = 6.5 °C/km` (environmental lapse rate). Montane (high `elev`) → cold; lowlands unchanged. Physical, touches only the `temperature` field. Expected: montane occupied cells 15.3 °C → ~6 °C (cold-water/salmon zone). **This alone flips montane to the salmon-capable side.** Re-check: nothing currently reads `temperature` except the (superseded) storage temp-gate and the new morph seasonal_amp is biome-keyed, so blast radius is small — but confirm.

### Phase 2 — Biome ↔ climate coupling: Whittaker-consistent labels [HIGH BLAST RADIUS]
Real biomes are a function of **temperature × moisture** (Whittaker). Re-derive/relabel so a cold+dry cell is STEPPE/TUNDRA (not "savanna"), a hot+wet cell tropical FOREST, hot+seasonal SAVANNA, etc. — so "savanna" is WARM by construction. **Red-team RT-1 (blast radius):** biome keys FORAGE_KCAL_TARGETS, GAME_KCAL_TARGETS, GAME_MOBILITY, BIOME_SEASONAL_AMP, capacity, and every prior biome→society result (R-37/R-45/R-46/R-48). Re-deriving biomes re-numbers the whole world → ALL those must be re-validated. **Mitigation options:** (a) FULL re-derivation (most correct, big re-validation); (b) LIGHTER — keep biome placement, add a temperature-consistency RELABEL only for cold-misplaced cells (cold "savanna"→steppe) so labels/seasonality are climate-consistent without re-numbering productivity; (c) DEFER Phase 2 — use the PHYSICAL aquatic-food field (Phase 3) for the morph, independent of biome labels, and accept the label imperfection as a reporting caveat. **Recommend (c)/(b) first; (a) only if the biome map itself must be realistic.**

### Phase 3 — Aquatic-food fishery field [THE NEW SIGNAL]
A per-cell `aquatic_food` ∈ [0,1] = the dense-storable-aquatic-food density, from physical fields (independent of biome label):
- **Anadromous (salmon):** `coldness(T) × river/coast-access × productivity × sea-connectivity`. `coldness = clamp((T_salmon_max − T)/range, 0, 1)` (salmon need cold water, T ≲ 15 °C); access from `wateracc`/`isRiver`; `sea-connectivity` from `dist`/river-reaches-water (anadromous fish must reach the sea to spawn); productivity from `npp`.
- **Shellfish/marine:** `is_shore × npp` (coastal littoral, the Bird-bonus zone) — warm-tolerant, coastal.
- `aquatic_food = max(anadromous, shellfish)` (or a weighted sum). Lit anchors: Ames 1994 (NW-Coast storage complexity), Testart 1982, Binford 2001 (aquatic-dependence ~ ET). Constants PROVISIONAL → sweep + sign-off.

### Phase 4 — Morph gate on aquatic_food [REPLACES the R-48 heuristic]
Complexity requires `mean(aquatic_food over band cells) ≥ threshold` (single clean signal), replacing the `wateracc×seasonality × npp_floor` heuristic (R-48). Expected: cold productive salmon rivers/coasts → complex (montane w/ Phase 1, temperate coasts); warm tropical (Mbuti forest, Hadza savanna once warm) → egalitarian; desert → egalitarian. `stratified` still needs settlement density (separate).

## 3. Validation
- Phase 1: montane occupied-cell T drops to salmon zone; nothing else shifts (temperature blast radius check).
- Phase 3/4: the biome→society table gives forest/savanna/desert EGALITARIAN, cold-productive-riverine (montane/temperate coast) COMPLEX; complexity rare + aquatic; status→RS/band/survival preserved; forest survives.
- Regression: full suite bit-exact with all new flags OFF.

## 4. Red-team (beyond RT-1)
- **RT-2 — does elevation lapse make montane survive?** Colder montane may raise mortality/change capacity if anything reads T. Verify montane still sustains a society.
- **RT-3 — sea-connectivity is hard on a torus.** Anadromous needs "river reaches sea." Proxy by `dist`-to-water + `is_shore` proximity rather than true hydrological routing (a full routing is out of scope).
- **RT-4 — warm-water fisheries exist** (tropical reefs, Calusa estuaries — subtropical). The shellfish term (is_shore × npp, temperature-agnostic) covers these so complexity isn't *only* cold. Keep both terms.
- **RT-5 — calibration explosion.** Many new constants (lapse, salmon T-cutoff, term weights, threshold). Ship ablatable/default-OFF; lock only after a sweep + sign-off; keep the R-48 heuristic as the fallback until the fishery field is validated.
- **RT-6 — over-reach.** This is a genuine substrate stage (climate + a new resource field), not a tweak. Phase 1 is cheap and high-value (fixes montane); Phases 2–4 are the real project. Land Phase 1 first, re-assess.

## 5. Recommendation
Build **Phase 1 (elevation lapse)** first — cheap, physical, and it alone flips montane to cold (the salmon-complex side). Then **Phase 3+4** (aquatic-food field + morph gate) using the physical signal, **deferring the full Phase-2 biome re-derivation** (use option (c): physical fishery signal + label caveat) unless the biome MAP realism is independently wanted. Hold canonicalization of the R-48 heuristic — it becomes the fallback the fishery field supersedes.
