# SiC Games — Phase 1 — Storability-Gated Society Morph (biome → society, the complexity axis)

**Status:** SCOPED 2026-07-03. Ablatable build (default OFF, bit-exact); canonicalization pending supervisor sign-off.
**Anchors:** Testart 1982 (storage → delayed-return → hereditary inequality); Binford 2001 (ET/seasonality → storage dependence); Woodburn 1982 (immediate- vs delayed-return); the lit-anchored `climate.py::BIOME_SEASONAL_AMPLITUDE` (Aché forest 0.05 aseasonal / Hadza savanna 0.40 / Hiwi llanos 0.60).
**Motivates:** R-45 — biome→society now runs in every biome, but the MORPH is "complex everywhere" (80–100%), not biome-graded. Diagnosis: no band is ever "packed" (density ~0.011 ≪ Binford 0.091 → stratified unreachable, needs settlement), and `surplus_frac ≥ 0.5` in EVERY biome (even leanest 0.94) → all → complex. Root: storage (the surplus/Testart enabler) is **not biome-gated** — the canonical `storage_temp_threshold_c=100°C` + a constant-14°C placeholder temperature field mean storage fires everywhere.

## 1. The idea
Complexity (egalitarian→complex) should require **storable surplus**, and storability is a biome property: an **aseasonal** biome (equatorial forest) has no glut→lean cycle → immediate-return → egalitarian (Mbuti); a **seasonal** biome (savanna/grassland/temperate) has a storable glut → delayed-return → complexity (NW-Coast-style). So gate storage on **biome seasonal amplitude**, not the placeholder temperature.

## 2. Mechanism (ablatable, default OFF ⇒ bit-exact)
- New per-cell **seasonal-amplitude field** from `F.biome` via `BIOME_SEASONAL_AMP_BY_CODE` (extends the lit table to all 7 codes; forest 0.05 / savanna 0.40 / grass 0.60 lit-anchored, desert 0.45 / mountain 0.55 / wetland 0.30 PROVISIONAL, water 0).
- New flag `storage_seasonality_gated` (default False): the storage overwintering gate becomes `in_owz = amp[cell] ≥ storage_seasonality_threshold` (default 0.25 — above forest 0.05, below savanna 0.40) INSTEAD of `temperature ≤ storage_temp_threshold_c`. Off ⇒ the temperature gate (bit-exact).
- Consequence: aseasonal forest → no storage → surplus→0 → **egalitarian**; seasonal biomes → storage → surplus → **complex** (once accumulated). Stratified still needs packing/settlement (separate, roadmap).

## 3. Seams
- `climate.py`: `BIOME_SEASONAL_AMP_BY_CODE` + `seasonal_amplitude_field(biome)`.
- `demography.py`: `storage_seasonality_gated`, `storage_seasonality_threshold`.
- `phase1_model.py`: cache the amp field (from `self._fields.biome`); the `in_owz` line (~705) reads it when the flag is on.

## 4. Validation
- Unit: amp field maps biome codes correctly; gate off ⇒ bit-exact `in_owz`.
- Behavioural (biome table): forest → mostly EGALITARIAN; seasonal biomes stay COMPLEX; forest must still SURVIVE (it's rich, per-cap 4–8× burn — losing the storage buffer should not collapse it) and status→RS/band preserved.

## 5. Red-team
- **RT-1 — ordering is SEASONALITY, not productivity.** Under storability, savanna (seasonal, marginal) can be COMPLEX while forest (rich, aseasonal) is EGALITARIAN — the OPPOSITE of a productivity ordering. This is INTENDED + correct (NW Coast was storable-seasonal, not highest-NPP; Mbuti forest is rich but egalitarian). Flag clearly so the result isn't misread as "rich→complex."
- **RT-2 — forest loses its storage buffer → collapse?** Forest is resource-rich; storage was a winter buffer. Validate forest survival; if it dips, the storage buffer was load-bearing there (unlikely given surplus 4.54). 
- **RT-3 — desert/mountain/wetland amplitudes are PROVISIONAL** (not directly lit). Flag; they set which marginal biomes count as "seasonal/storable." Supervisor to confirm before canonical.
- **RT-4 — surplus threshold still 0.5.** Even seasonal biomes must accumulate surplus ≥0.5 to morph; if a seasonal-but-poor biome (savanna) can't, it stays egalitarian too — which is arguably MORE correct (Hadza savanna ARE egalitarian despite seasonality — storage needs a big enough glut). Watch whether savanna lands egalitarian or complex; either is defensible, report which.
- **RT-5 — constant-temperature substrate.** This REPLACES the (inert) temperature gate; it does not fix the missing real temperature field (CL-1 deferred). Storability here = biome seasonality, a proxy for the full ET/temperature story.

## 6. Pending before canonicalization (supervisor gate)
Confirm the biome→society morph gradient is sensible + forest survives + status→RS/band preserved; confirm the PROVISIONAL desert/mountain/wetland amplitudes; then flip `storage_seasonality_gated=True` into `realistic_forager_demog`.
