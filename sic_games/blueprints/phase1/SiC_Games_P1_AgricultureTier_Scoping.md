# SiC Games — Phase 1 — Agriculture Tier (cultivability S_pot + soil-depletion + landesque learning → the dynastic bust)

**Status:** SCOPED + RED-TEAMED 2026-07-04 — **NOT YET BUILT** (supervisor sign-off + §7 open questions first). The natural continuation of aggregation-sedentism (R-52/R-53): a settlement's tier-2 is RESOURCE-AGNOSTIC (reads `S_pot`), so agriculture drops in as a **second `S_pot` source (`cultivability`)** — *no new settlement/morph machinery*. But agriculture has the dynamics fisheries lack: R-53 showed rich fisheries give *stable* villages (correct — salmon self-renews), so the **acute dynastic bust (boom→intensify→degrade→relocate) is an AGRICULTURE phenomenon** — driven by **soil depletion** (the resource *does* degrade under farming) in tension with **landesque-capital learning** (investment durably raises yield), mediated by **population pressure** (Boserup). This tier is the road from foraging/fishing to dense sedentary society.

**Anchors:** Boserup 1965 (*The Conditions of Agricultural Growth* — population pressure → **intensification**, the anti-Malthus: people intensify before they starve); Blaikie & Brookfield 1987 / Håkansson & Widgren 2014 (**landesque capital** — durable land improvements: terraces, irrigation, cleared/manured fields); Conklin 1957 (Hanunoo **swidden** — farm 2–3 yr → yields drop → **fallow 10–20 yr** → relocate); Netting 1993 (smallholder **intensification**); Bocquet-Appel 2011 (**Neolithic Demographic Transition** — sedentary farming → fertility rise → population growth); Bar-Yosef (Natufian → farming); Flannery 1969 (broad-spectrum → domestication); FAO agro-ecological zones / growing-degree-days (cultivability from climate).

## 1. What agriculture adds that fishing didn't (the point)
| | Fishery (R-53, built) | Agriculture (this) |
|---|---|---|
| resource | salmon/shellfish — self-renewing, oceanic | soil fertility — **degrades under use** |
| dynamic | seasonal glut + storage + shock → **STABLE village** | boom → **soil depletion** → yield fall → relocate/collapse → fallow → reboom |
| intensification | limited (weirs) | **landesque capital** (terraces/irrigation) → durable yield → *permanent* dense villages |
| where | cold rivers / rich coast (rare) | **temperate/subtropical arable land** (widespread) |
So agriculture is where the **dynastic cycle** (§10 of the aggregation blueprint) and the **Malthus↔Boserup** tension live, and where **regional density can climb far past the Binford threshold** (dense villages → the road to complexity/stratification).

## 2. Mechanism (three parts, resource-agnostic integration)
- **(A) `cultivability` field — a second `S_pot` source, EFC-derived.** Like Whittaker/Miami, cultivability EMERGES from climate: high where warmth (growing season / GDD), water (enough precip, not waterlogged/arid), and workable terrain (low slope, not water) coincide — peaking in temperate/subtropical sub-humid land (the fertile-crescent/temperate belt); ~0 in tundra/desert/steep/dense-canopy. Integration: `S_pot = max(aquatic_food, cultivability)` (a settlement exploits its *best* local resource — a reach → fish, a fertile plain → farm), so the *entire* aggregation-sedentism + tier-2 + storage + shock stack works UNCHANGED. **This is the generality payoff — one field swap, farming villages for free.**
- **(B) Soil depletion — the bust driver (the §10 GD-1-reuse, which now MATTERS).** A cultivated catchment's soil is a depletable stock `B_soil ∈ [floor,1]` (reuse GD-1's `B` on catchment cells, via the foraging-pressure remap): tier-2 farm yield `= settle_tier2_yield · cultivability · B_soil`. Sustained farming depletes `B_soil` (the halo); fallow (after relocation/abandonment) regrows it. Swidden regrowth is SLOW (10–20 yr fallow — a much slower `R` than salmon's 0.8/yr). This is what fish lacked → this is what busts a farming village.
- **(C) Landesque capital — the intensification / anti-bust (Boserup).** A per-settlement **investment stock** `L ∈ [0,1]` that accumulates with sustained settlement + labour (rising with pool size / population pressure) and durably (a) RAISES effective yield and/or (b) SLOWS `B_soil` depletion (terraces/irrigation/manuring sustain the soil). `L` decays slowly if abandoned. Boserup: under population pressure a village **intensifies** (`L`↑) rather than relocating → a *permanent* dense village; without the pressure/labour it stays swidden (low `L`) → the relocation cycle. **The Malthus↔Boserup tension is `B_soil`-depletion vs `L`-intensification.**

## 3. The emergent regimes (what we're validating)
- **Swidden** (low `L`): boom → deplete soil → yield falls below subsistence → relocate to fresh land → old field fallows → cyclical shifting cultivation. The **dynastic bust**, endogenous. (Requires fresh land to relocate to — when land fills, see next.)
- **Intensive** (high `L`, driven by population pressure / circumscription): the village invests, `B_soil` sustained, becomes **permanent + dense** → regional density climbs → the road to complex/stratified society. (Boserup + Carneiro: when catchments overlap and you *can't* relocate, you *must* intensify → `L`↑.)
- **Carneiro closes here:** swidden works while empty land exists; once land fills (catchments overlap, no fresh fallow), relocation fails → intensify-or-collapse → circumscription-driven complexity, endogenous.

## 4. Two-layer build (mirrors the fishery build)
- **Layer A — cultivability + farming villages (reuse everything).** Build the `cultivability` field (EFC-derived), wire `S_pot = max(aquatic, cultivability)`. Validate: settlements form on fertile land and behave like the fishery villages (pack, morph) — proves the generality (farming villages via one field). Soil static for this layer.
- **Layer B — soil-depletion + landesque + the cycle.** Add `B_soil` depletion (GD-1 reuse + foraging-pressure remap, §10) and the `L` investment stock (Boserup). Validate the **swidden cycle** (boom→deplete→relocate→fallow→reboom on a generational timescale) AND **Boserup intensification** (population pressure → `L`↑ → permanent dense village) — both from the same code, selected by land-availability / pressure.

## 5. Conditions / seams
- `cultivability_field(EFC)` helper (new); `S_pot = max(aquatic_food, cultivability)` accessor (one line, replaces the aquatic-only read — the *only* change to the settlement code).
- `B_soil`: reuse GD-1 `B` on cultivated catchment cells + the §10 foraging-pressure remap; **slow** regrowth `R_SOIL_PER_YR` (swidden fallow, ~0.05–0.1/yr vs salmon 0.8).
- `L` (landesque): per-settlement stock in `_settlement_*`; grows `∝ pool_size · pressure`, decays on abandonment; multiplies yield and/or damps `B_soil` depletion. Capped.
- Relocation (from §10-Q1): on soil-exhaustion a settlement **relocates** to the best fresh cultivable catchment in range (vs disperse); if none (land full) → intensify (`L`↑) or collapse. This is the Carneiro pivot.
- Everything default-OFF (`enable_agriculture` / `enable_soil_depletion` / `enable_landesque`); bit-exact when off.

## 6. Red-team
- **RT-1 [everything farms → no foragers].** Gate `cultivability ≥ thr` high (only genuinely arable land); tundra/desert/steep/dense-forest ≈ 0 → most of the map stays forager. Validate a forager/farmer mosaic, not universal agriculture.
- **RT-2 [calibration explosion].** Soil-depletion `R_SOIL` × landesque gain/decay × yield coupling × relocation. Ship ablatable/default-OFF; sweep; validate by MECHANISM (does a swidden village cycle on a ~generational fallow, and does population pressure flip it to intensive — WITHOUT tuning to a target?).
- **RT-3 [landesque runaway].** `L` unbounded → infinite yield. Cap `L ∈ [0,1]`; diminishing returns; decay on abandonment.
- **RT-4 [double-count S_pot].** A cell both aquatic and cultivable → `max` (exploit the best), not sum, to avoid double-provisioning. Confirm.
- **RT-5 [cultivability-from-climate is a whole sub-model].** Like Miami/Whittaker it needs its own extraction + lit (GDD/aridity/FAO-AEZ). Scope it as a sub-step with VERIFIED thresholds, PROVISIONAL until sign-off; interim a coarse temperate/subtropical-sub-humid mask.
- **RT-6 [the Neolithic transition is elided].** v1 makes cultivability a latent *potential* the settlement "unlocks" by farming (same gating as fish) — it does NOT model domestication/the broad-spectrum revolution. Flag: the *transition* (why/when foragers adopt farming) is a deeper future question; v1 asks only "given farmable land, do farming villages + the soil cycle + intensification emerge?"
- **RT-7 [bit-exactness].** `S_pot = max(aquatic, cultivability)` with `cultivability≡0` when OFF ⇒ identical to the aquatic-only read; assert on the suite.
- **RT-8 [generality is the whole point].** No agriculture-specific logic in the settlement/morph path — only the `S_pot` source and the soil/landesque dynamics differ. Enforce in review.

## 7. Open questions — discuss before build
- **Q1 — `S_pot` combination.** `max(aquatic, cultivability)` (best resource — recommend) vs additive (a place with both is richer)? *Recommend max* (a village farms OR fishes its best option; avoids double-count).
- **Q2 — Cultivability formula.** Coarse climate mask (temperate/subtropical × sub-humid × arable) for v1, or a proper GDD/aridity extraction now? *Recommend coarse mask v1 (PROVISIONAL), proper extraction as a signed-off sub-step (like Miami/Whittaker).*
- **Q3 — Landesque grain + effect.** Per-settlement `L` (recommend) raising yield, or damping soil-depletion, or both? *Recommend both, capped; start yield-raise + depletion-damp.*
- **Q4 — Relocation vs disperse on soil-exhaustion.** Relocate-to-fresh-land (the swidden/Carneiro pivot — recommend) vs disperse-to-mobile? *Recommend relocate-if-fresh-land-exists, else intensify-or-collapse (this is where Carneiro bites).*
- **Q5 — Model the forager→farmer TRANSITION, or just have both tiers?** *Recommend both-tiers-available v1* (farming emerges where land is farmable); the domestication transition is a deeper future layer.

## 8. Recommendation
Build the agriculture tier as `cultivability` = a second `S_pot` source (generality payoff — farming villages via one field swap), then soil-depletion + landesque capital = the Malthus↔Boserup engine that produces the **swidden cycle**, **intensive permanence**, and **Carneiro-when-land-fills** — the dynastic bust and the road to dense complex society that fisheries (correctly) don't provide. Two-layer (cultivability-villages first, then soil+landesque), all default-OFF, resource-agnostic. Resolve §7 (esp. Q2 cultivability formula and Q4 relocation) with the supervisor, then build Layer A and validate farming villages before Layer B.
