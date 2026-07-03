# SiC Games — Phase 1 — GD-1: Finite resources + biome/season-specific depletion & regrowth

**Status:** SCOPED + LIT-ANCHORED + RED-TEAMED 2026-07-03. Foundational substrate (turns the standing carrying-capacity FLOW into a depletable STOCK). Needs supervisor sign-off; biome/season rates are science-calibration.
**Motivates:** the substrate under sedentism/complexity. Today a cell is an INFINITE standing flow (`E` kcal/step, non-depleting) — so a concentrated band never hunts-out its catchment, sedentism is a free lunch, and there is no boom→bust. GD-1 was always flagged as *"a sedentism effect — hunt-out of a fixed catchment; mobile bands avoid it via movement"* (DEFERRED_MECHANICS GD-1). Supervisor: build GD-1, biome- AND season-specific, strong lit anchors.

## 1. The model — a depletable stock with logistic regrowth
Each land cell holds a resource STOCK `S` (persons-supported, or kcal), regenerating logistically toward its carrying capacity `K` (the current NPP/aquatic capacity field — unchanged) at a **biome- and season-specific** rate, depleted by harvest:
```
S(t+1) = S(t) + r_biome · season(month) · S(t) · (1 − S(t)/K)  −  harvest(t)      (0 ≤ S ≤ K)
yield(t) = min(harvest_demand, S(t))                                              (can't take more than the stock)
```
- **K** = carrying capacity (Miami-NPP / Tallavaara / aquatic; already biome-scaled — Coe: game stock ∝ rainfall/NPP). Unchanged.
- **r_biome** = intrinsic regrowth rate (per month = per-year/12); biome-specific (§2).
- **season(month) ∈ [0,1]** = the growing-season pulse (EFC seasonal amplitude / a_seas): regrowth concentrated in the productive half → the stock peaks after the growing season = the seasonal **GLUT**, drawn down through the lean season + by harvest.
- **Depletion** = harvest removes stock; if harvest > regrowth, `S` falls → the cell's yield drops → the hunt-out halo → movement pressure.

## 2. Biome- & season-specific regrowth rates (LIT-ANCHORED)
`r_biome` = the resource's intrinsic rate of increase / turnover, biome-specific (PROVISIONAL values → sweep + sign-off):
| biome / resource | r (per year) | anchor |
|---|---|---|
| grassland / savanna (small fast grazers; high production:biomass) | ~0.5–0.8 | Coe, Cumming & Phillipson 1976 (high production ∝ rainfall); fast grassland turnover |
| tropical forest (browsers, megafauna, large slow-turnover standing biomass) | ~0.10–0.20 | Wang 2021 (forest biomass turnover slow); forest-megafauna slow r_max |
| temperate / boreal forest | ~0.15–0.30 | ungulate r_max medium (muntjac 0.44, gaur 0.31 — Cortés 2016; SE-Asian recovery) |
| desert / marginal (sparse, slow) | ~0.10–0.20 | low productivity → slow rebuild |
| aquatic (salmon run / shellfish — fast-renewing, migratory restock) | ~0.6–1.0 | anadromous restock annually from the sea → fast catchment recovery (the sedentism enabler) |
**Season:** `r_max` applies during the growing season; ≈0 in the lean season → the seasonal glut. Anchor: growing-season length ∝ productive months (from the climate seasonality).
**Body-size gradient (future):** megafauna deplete first + recover slowest (elephant → decades); small/fast recover in a few years — Cortés 2016. First cut: one stock per cell at `r_biome`; a per-size split is a refinement.

## 3. The CAMP connection (central-place + depletion + MVT) — discussion
GD-1 makes the residential-mobility ↔ depletion link explicit and gives sedentism a FIRST-PRINCIPLES basis:
- A camp (concentrated band) forages a **catchment** (cells within foraging radius) → harvest depletes the catchment stock → a **depletion halo** forms around the camp (biorxiv 2024 central-place halos; Amazonia PMC5645145).
- As the catchment depletes, its marginal return falls; when it drops below the regional average, the camp **relocates** — Charnov's **marginal-value theorem** at the camp scale (rainforest-patch residential mobility, PMC5373393). This IS the depletion→move mechanism.
- **SEDENTISM EMERGES, it need not be hand-coded:** a camp STAYS wherever `regrowth + stored surplus ≥ harvest` — i.e., where the resource replenishes/stores faster than the concentrated band depletes it. A **salmon river** (aquatic r≈0.8 + storable glut) sustains a stationary dense camp; a **dispersed terrestrial catchment** (slow r, no storage) depletes → forces mobility. So the storage-sedentism CONDITIONS (C-RESOURCE/GLUT/PAYOFF/COMMITMENT) become EMERGENT outcomes of GD-1 + storage + the movement rule, not a separate decision module.
- **This likely supersedes the hand-coded storage-sedentism drive** (`…_StorageSedentism_Scoping.md`): with a depletable stock, the EXISTING IFD movement should concentrate agents onto the fast-replenishing cell as the surrounding cells deplete (the rich aquatic cell becomes the relatively-best patch once neighbours are hunted-out). GD-1 may be the missing piece that makes C8's capacity subsidy finally concentrate bands — to be tested at GD-1 GATE.

## 4. Implementation seams
- Capacity field → a mutable STOCK: `S` array initialised to `K`; per-step logistic regrowth (biome r × season) − harvest. `NPPCapacityField.level()` returns `S` (current stock), not the fixed `E`. Harvest debits `S`.
- Biome r from a `R_BIOME_PER_YR` table (§2) keyed by `fields.biome`; season from `ClimateField.season()` / EFC seasonal amplitude.
- Ablatable flag `enable_depletion` (default OFF ⇒ non-depleting standing flow = bit-exact).
- The band camp (separate, discussed): a central-place concentration where a band co-resides and forages a catchment radius; deplete-then-relocate via MVT. Scope after GD-1 (they interlock).

## 5. Red-team
- **RT-1 [calibration is the crux].** r_biome × season sets everything; wrong values → either infinite abundance (r too high) or extinction (r too low, hunt-out faster than regrowth). Ship ablatable; sweep against the lit rates; validate that a mobile band's catchment depletes-then-recovers on a realistic timescale (years) and eq_pop stays comparable to the non-depleting baseline.
- **RT-2 [re-validation blast radius].** Depletion changes the capacity every prior demographic/bands/morph result runs on. Mitigation: default-OFF (bit-exact); validate the depleting substrate FRESH (like the EFC mode toggle).
- **RT-3 [movement must respond to depletion].** For MVT/mobility to emerge, agents must move off depleted cells — IFD already maximises per-capita, so a depleted (low-S) cell's per-capita drops → agents leave. Confirm the per-step yield uses `S` (not `K`) so IFD sees the depletion.
- **RT-4 [seasonal glut requires seasonal yield].** The glut needs `season(month)` to actually pulse the stock — depends on the EFC seasonal amplitude being wired to regrowth. Verify the stock visibly peaks/troughs seasonally.
- **RT-5 [stock vs flow units].** `E`/`K` are per-step kcal (a flow); `S` is a stock (kcal standing). Must reconcile: `K` = the sustainable standing stock (≈ annual production / turnover), harvest = per-step draw. Get the unit conversion right or the timescales break.
- **RT-6 [interaction with density-disease].** Crowding is currently density-disease-regulated; with depletion, crowding ALSO hunts-out the local stock (starvation). Two crowding penalties — reconcile (depletion is the resource-side, density-disease the pathogen-side; both real, avoid double-count).
- **RT-7 [emergent sedentism may not materialise].** The hopeful claim (§3: GD-1 makes concentration emerge) is a HYPOTHESIS — test it. If IFD still won't concentrate even with depletion, fall back to the hand-coded sedentism drive.

## 6. Recommendation
Build GD-1 as an ablatable depletable-stock substrate (default-OFF, bit-exact) with the §2 biome/season rates; validate a mobile band's deplete→recover→relocate cycle + eq_pop viability (GD-1 GATE). THEN test the §3 hypothesis — does depletion make bands concentrate on fast-replenishing aquatic cells (emergent sedentism)? If yes, sedentism/complexity fall out for free and the storage-sedentism drive is superseded; if no, layer the hand-coded drive. Scope the band camp (central-place catchment + MVT relocation) next — it interlocks with GD-1. Sign-off needed on the r_biome table.
