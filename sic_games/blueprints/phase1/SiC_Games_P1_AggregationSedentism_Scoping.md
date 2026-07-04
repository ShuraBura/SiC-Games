# SiC Games — Phase 1 — Aggregation-Sedentism (settlements as multi-band coalescence; v2 logistical catchment)

**Status:** **Layer 1 + Layer 2a BUILT + VALIDATED (R-52, commits `5b72ce0` / `b08af7c`, 2026-07-04)** — the packing→morph chain closes (band_dens 0.19–0.34, %packed 38–75%, settlements persist, population survives). **Layer 2b SCOPED + RED-TEAMED below (§10) — NOT YET BUILT** (supervisor sign-off first). Supersedes the *single-band cell-packing* approach of `…_EconomicDefensibility_Scoping.md` (DE-10), which failed: forcing one ~25-band onto a cell is either inert or a death spiral. Reframes settlement as **multi-band aggregation** at a rich node — the correct anthropological unit — reusing the aggregation + fission–fusion + morph machinery already built.

**Anchors:** Mauss & Beuchat 1904/1979 (seasonal aggregation↔dispersal — sedentism = the aggregation phase gone year-round); Binford 2001 (forager↔**collector** logistical mobility; the ~0.091/km² **packing threshold** = a *regional* density = `BINFORD_PACKING_PER_KM2`); Vita-Finzi & Higgs 1970 (**site-catchment** analysis — the forage territory around a residential base); Johnson 1982 (**scalar stress** — aggregation size → integrative hierarchy); Bandy 2004 (village fissioning vs the hierarchy that holds a pool together); Testart 1982 (storable dense predictable resource → delayed return); Ames & Maschner 1999 (NW-Coast winter villages = coalesced House-groups); Bar-Yosef & Belfer-Cohen (Natufian hamlets = multi-household aggregations, dozens–~150); Dyson-Hudson & Smith 1978 (economic defensibility → the defended object is the **catchment**); Carneiro 1970 (circumscription emerges when catchments **overlap**).

**Motivation (what the runs taught us):**
- **R-51 + the defensibility A/Bs:** on the natural substrate the landscape sits at ~0.015/km² — ~6× **below** Binford packing — so it is genuinely *under-populated relative to where real foragers settled*, and no local mechanism can manufacture density a sparse population doesn't have. Every concentration attempt (C8 subsidy GATE-3; defensibility inert→fitness-edge→death-spiral) failed for this one reason.
- **Q1 (lit):** settlements form by **coalescence of multiple bands/households** at a rich node (crystallised seasonal aggregation), not a single band settling — the founding unit is ~100–300 people, not ~25. Between-band *cell* exclusion (my defensibility v1) actively *prevents* the coalescence that makes villages.
- **Q2 (lit):** sedentism onset clusters at/above the ~0.091/km² regional density; complex foragers ran ~0.5–5/km². Our equilibrium is well below → too few people. The fix is to raise *regional* density and let bands *aggregate*, not to force one band to pack.

## 1. The mechanism — "the gathering that stops dispersing"
The built `_do_gathering` (phase1_model.py) already realises Mauss's aggregation phase: every `aggregation_period` steps in the abundance window it finds abundant sites (top-capacity, min-separated), pools the bands nearest each site into a **connubium**, pairs across bands, then everyone **disperses**. The single new idea:

> **At a *persistently* abundant, storable, defensible site, the pooled bands do not disperse — they co-locate and *stay*, forming a SETTLEMENT.**

A settlement is therefore a **multi-band aggregation** (the pool), which supplies the residential density that a single band never could → residential packing crosses Binford 0.091 → the density morph fires; scalar stress from pool size drives hierarchy (Johnson) → complex/stratified *emerges*, not forced. Collapse (resource/payoff failure) → the pool fissions back to mobile bands — the boom→bust seam for the dynastic cycle.

## 2. v2 — residence ≠ foraging + a settlement-unlocked TIER-2 resource (the target)
Two coupled facts make this work, both from the supervisor:
- **Single-cell residence.** A settlement of ~dozens is « one 100 km² cell (10×10 km), so **all residents live on the SINGLE site cell** (residence pin — step onto the site, stay). Residential density there is then ~0.5–1/km² ≫ Binford packing (0.091) *automatically* → the per-cell/per-band morph fires with no forcing. This is why every prior single-band cell-*tether* died: it coupled residence to foraging (pile up → starve on your own cell). Decoupling makes single-cell residence both correct AND safe.
- **Tier-2 unlock (why the settlement doesn't starve).** Sedentism is *enabled by* shifting to an intensive, storable, high-yield resource — the delayed-return bargain (Testart) / intensification (Boserup): you commit to staying, invest labour (weirs/processing/storage, or cultivation), and unlock a yield a mobile band cannot get. So a settlement **forages its catchment** (Binford collectors; Vita-Finzi & Higgs) for an intensive **TIER-2** yield = `settle_tier2_yield × Σ_catchment S_pot`, **GATED on settlement** (a mobile band gets only the small tier-1 cell return). This sustains the packed pool that reside-on-cluster starved, and — being gated — also **explains GATE-3** (mobile bands never pile on reaches because the big payoff requires committing to settle first).
- **RESOURCE-AGNOSTIC.** Tier-2 reads `S_pot` (= `aquatic_food` now — a fishery; a `cultivability` source drops in later — proto-agriculture). The settlement/morph/collapse logic never names the resource — one field, many sources, so farming villages are the *same* mechanism with a different input.
- **Depletion halo → collapse (Layer 2b).** Tier-2 degrades under sustained intensive extraction (over-fishing / soil) → the central-place depletion halo (LITERATURE.md) → catchment can't feed the pool → dissolve → disperse: the dynastic bust, endogenous.
- **Carneiro for free.** When regional density rises and **catchments overlap**, settlements can no longer relocate to escape a spent halo → intensify or contest → circumscription-driven complexity/conflict emerges *endogenously* (the contested-catchment follow-on, §8-Q1).

## 3. Two-layer build path (de-risk: aggregation logic ⟂ harvest model)
- **Layer 1 — settlement lifecycle.** Extend `_do_gathering`: pools at *persistent-abundant* sites PERSIST (form → hold → collapse) via the existing fission–fusion. Harvest stays reside-on-cluster (v1) for this layer. **Validate the lifecycle in isolation:** do multi-band pools form at reaches, stay, pack (density), morph, and disperse when the site fails? (No harvest-core change yet.)
- **Layer 2 — v2 catchment foraging.** Swap the settled pool's harvest to pooled catchment + GD-1 depletion of the catchment. **Validate:** residential packing → morph → depletion halo → catchment defense → Carneiro-on-overlap. Each layer validated separately so a misbehaviour is localised (the lesson from the murky tether iterations).

## 4. Conditions for a pool to settle + persist (lit-anchored gates)
- **C-PERSISTENT** — site resource high *outside* the seasonal window (storable glut ≥ threshold), so there is a reason to stay past the festival. *(Testart.)*
- **C-CARRYING** — catchment can feed the pool (`pool ≤ catchment_carrying`). *(Anti-over-subscription; the payoff gate.)*
- **C-POOL** — a genuine multi-band aggregation assembled (pool ≥ `settle_min_pool`, several bands). *(Q1: the unit is the coalescence; a lone band does not settle.)*
- **C-DEFENSIBLE** — the catchment is dense+predictable enough to defend (DH&S); the settlement excludes non-member bands from its **catchment** (not the cell). *(Folds the working defensibility claim/fitness-edge in at the correct grain; retires cell-vs-cell exclusion.)*
- **Release** — resource/payoff fails, halo spent with no relocation, or pool outgrows catchment → fission to mobile bands.

## 5. Implementation seams (all reuse existing machinery)
- `_do_gathering`: after pooling, flag pools meeting §4 as settlements → `self._settlement: dict[site → member_band_ids]`, persisting across seasons while conditions hold.
- **Hold** settled members on the site cluster at the **pool** level (suppress diffusion / point cohesion at the site for settled bands) — density makes this stable, unlike the single-band tether that collapsed.
- **Morph** reads the *settlement's* residential density (members / cluster cells) → packing → `society_from_character` complex/stratified; scalar stress (pool size) → hierarchy weight.
- **v2 harvest** (Layer 2): a `catchment_pool(site)` yields the summed catchment resource; settled residents split it; GD-1 depletes catchment cells by settlement pressure.
- **Defensibility** retargeted to catchment: reuse `_cell_owner`/claim logic but keyed to the settlement's catchment vs non-member bands.
- **Collapse**: fission via the existing band-split path.
- **Default OFF** (`enable_aggregation_sedentism`) ⇒ `_do_gathering` unchanged ⇒ bit-exact.

## 6. Red-team
- **RT-1 [regional density still too low].** If the landscape stays at 0.015/km², pools never assemble (Q2). *Mitigation:* this mechanism is *downstream of* raising regional density — pair it with growth-to-carrying / circumscription (R-51); validate first on a productive aquatic region where local capacity (~0.8/km²) supports a pool. If pools still don't form, density is the binding constraint, not this mechanism (a clean diagnostic).
- **RT-2 [over-subscription death, again].** A pool that exceeds catchment carrying starves. *Mitigation:* C-CARRYING gates settlement on `pool ≤ catchment_carrying`; past it → fission, not starvation. Layer 2's catchment (not single-cell) is what makes the carrying real.
- **RT-3 [everything settles / no mobile foragers left].** *Mitigation:* C-PERSISTENT + C-DEFENSIBLE only qualify rare storable dense sites (aquatic 1–6% of cells); most bands never meet them → stay mobile-egalitarian (correct — sedentism is the exception).
- **RT-4 [scalar-stress hierarchy is asserted, not earned].** Pool-size→hierarchy must be a *mechanism*, not a relabel. *Mitigation:* route it through the existing size-repulsion / society-gated cohesion (Johnson/Bandy: large pools fission UNLESS integrative hierarchy raises cohesion) — hierarchy emerges as the pool's answer to scalar stress, testable via fission rates.
- **RT-5 [v2 harvest breaks determinism / bit-exactness].** Catchment pooling touches the forage/split core. *Mitigation:* Layer 2 behind the flag; assert R-18/19/E.3 bit-exact when OFF; validate Layer 1 (no harvest change) before enabling Layer 2.
- **RT-6 [catchment radius / depletion calibration].** New knobs (`catchment_radius`, carrying, depletion pressure, `settle_min_pool`, persistence threshold). *Mitigation:* ship ablatable/default-OFF; anchor radius to logistical-foraging lit (~1–2 cells); validate by MECHANISM (do settlements form on cold salmon reaches / rich coasts, degrade catchments, and collapse when spent — WITHOUT tuning to a target society mix?).
- **RT-7 [double-counting food].** Catchment cells foraged by a settlement must not *also* be foraged full-rate by passing mobile bands (or the resource is spent twice). *Mitigation:* the catchment-defense (C-DEFENSIBLE) excludes non-members; reconcile settlement vs mobile harvest on shared cells explicitly.
- **RT-8 [generality].** No aquatic-specific logic — read `S_pot`/persistence so proto-agriculture `cultivability` drops in (a farmed catchment = the same structure). Enforce in review.

## 7. What this retires / folds in
- **Retire:** single-band cell-packing tether + cell-vs-cell exclusion (wrong unit + wrong grain; DE-note the tether/cohesion-redirect dead-ends).
- **Fold in (keep):** the defensibility claim/ownership lifecycle + the observed **fitness edge**, re-based to the **catchment** grain (the settlement owns+defends its catchment). `enable_economic_defensibility` becomes the catchment-defense sub-component of the settlement.
- **Defer (still):** heritable-ownership → `cred` ascribed-rank bridge (blueprint 5b/Q7) — now naturally hung on *settlement/House* ownership of a catchment; wire after the lifecycle validates, as a separate signed-off step (keeps clear of the held R-19/R-21/R-26 status→RS reframe).

## 8. Open questions — need discussion before build
- **Q1 — Catchment ownership: private or contested?** Each settlement forages its *own* radius (simple), or nearby settlements *contest* a shared catchment (produces Carneiro conflict + is where raiding/defensibility bites, but heavier)? *Recommend private v2-Layer-2 first, contested as the Carneiro follow-on.*
- **Q2 — Catchment radius.** 1 cell (10 km, tight) vs 2 (20 km, a day's logistical range)? *Recommend 1–2, anchored to logistical-foraging lit, swept.*
- **Q3 — Hold mechanism for settled members.** Suppress diffusion (freeze) vs point cohesion at the site? *Recommend cohesion-at-site at the POOL level (stable because dense), not the single-band freeze that collapsed.*
- **Q4 — Persistence signal.** Annual `aquatic_food`/`S_pot` ≥ threshold, or a true off-season resource floor (needs seasonal yield wiring)? *Recommend annual S_pot proxy v1, flagged PROVISIONAL.*
- **Q5 — Does raising regional density come first (R-51 lever) or in parallel?** *Recommend validating Layer 1 on an already-productive region first (isolates this mechanism from the density lever), then couple.*

## 9. Recommendation
Build aggregation-sedentism as the settlement mechanism, target **v2 logistical catchment**, via the **two-layer** path (lifecycle first, catchment-harvest second), `enable_aggregation_sedentism` default-OFF, resource-agnostic. **DONE for Layer 1 + 2a (R-52).** It is the anthropologically-correct unit (multi-band coalescence), reuses the gathering + fission–fusion + morph code we trust, gives defensibility its correct **catchment** grain, and makes Carneiro circumscription + the depletion halo + the dynastic collapse emerge endogenously. Layer 2b (§10) is next.

---

## 10. Layer 2b — tier-2 depletion → central-place halo → collapse (SCOPE + RED-TEAM, 2026-07-04)

**Why:** in Layer 2a the tier-2 yield is STATIC (`settle_tier2_yield · Σ_catchment S_pot`), so a settlement **never exhausts its catchment** → it can only die from demographic dips, never from over-intensifying its resource. Real settlements degrade their catchment (over-fishing / soil exhaustion) → the **central-place depletion halo** (LITERATURE.md) → relocation or collapse. This is the missing **boom→bust** that seeds the dynastic cycle (Ibn Khaldun) and, once catchments overlap, Carneiro conflict.

**The mechanism — make tier-2 a DEPLETABLE stock, reusing GD-1:** the intensive yield of a catchment cell becomes `settle_tier2_yield · S_pot(cell) · B(cell)`, where `B(cell) ∈ [B_FLOOR,1]` is the **existing GD-1 stock** (not a new field). The wrinkle: GD-1 currently depletes by RESIDENCE occupancy, but settled residents all stand on the site cell, so the catchment never depletes today. Fix = a **foraging-pressure remap**: a settlement's `N` residents exert extraction pressure **distributed over its catchment cells** (≈ `N / n_catchment_cells` each), and GD-1's `deplete_and_regrow` runs on THAT pressure map for catchment cells (the residents contribute NO depletion to the site cell they merely reside on). Then:
- **Boom:** fresh catchment (`B≈1`) → full tier-2 → pool grows.
- **Over-intensification:** growing pool → rising per-cell pressure → catchment `B` falls (the halo, spatial: nearest cells hit hardest) → tier-2 yield falls.
- **Bust:** yield < the pool's subsistence → starvation/out-migration → pool drops below `settle_min_pool` → settlement dissolves (existing lifecycle).
- **Fallow → reboom:** dispersed, the catchment `B` regrows (`AQUATIC_R_PER_YR`) → the reach becomes settle-able again later → a *cycle*, not a one-shot.

**Equilibrium target (the calibration crux):** a *healthy* settlement should sit at a **sustainable** extraction where `B` settles at some `B* > collapse` and holds for generations; collapse should fire only on **overshoot** (pool grows past catchment carrying — Boserup) or a resource shock. i.e. tune so the *default* is a stable village and the bust is an *earned* overshoot, not an inevitability.

**Seams:** (a) build a `settlement_forage_pressure` map each step (residents → catchment cells); (b) feed it (plus non-settled residence occ) to `deplete_and_regrow`; (c) `_settlement_catchment_yield` multiplies each cell's `S_pot` by its GD-1 `B`; (d) collapse rides the existing `_maintain_settlements` hysteresis. New sub-flag `enable_tier2_depletion` (default OFF ⇒ Layer 2a static behaviour, bit-exact). Requires `enable_depletion=True` on the capacity field.

**Red-team:**
- **RT-1 [double-collapse / over-fragility].** Density-disease AND depletion both cull → settlements never last. *Mitigation:* calibrate regrowth vs extraction so `B*` is comfortably above collapse at the *equilibrium* pool; collapse only on overshoot/shock. Validate the CYCLE length is generational (decades+), not a few steps.
- **RT-2 [permanent land ruin].** `B` never recovers → a reach is settle-once-then-dead. *Mitigation:* GD-1 logistic regrowth + `B_FLOOR` trickle guarantee fallow recovery once the settlement disperses; check reboom actually happens.
- **RT-3 [double-depletion bookkeeping].** Residents deplete BOTH their residence cell (residence occ) AND the catchment (foraging pressure). *Mitigation:* remap — settled residents contribute foraging pressure to the catchment and are REMOVED from residence-cell depletion (they don't forage where they sleep). Assert conservation.
- **RT-4 [thrashing].** Form → collapse → reform every few steps = noise, not a cycle. *Mitigation:* `settle_release_steps` hysteresis + regrowth timescale ≫ formation cadence; the aggregation is seasonal so re-formation is gated to gatherings.
- **RT-5 [calibration explosion].** New coupling of extraction efficiency × regrowth × carrying × pool dynamics. *Mitigation:* default-OFF sub-flag; sweep the 2–3 new knobs; validate by MECHANISM (does a rich reach boom, degrade, bust, and later reboom without tuning to a target cycle length?).
- **RT-6 [bit-exactness].** Touches the GD-1 hook. *Mitigation:* `enable_tier2_depletion` gate; when OFF, the pressure remap and `B`-multiply are skipped ⇒ Layer 2a bit-exact; assert on the suite.
- **RT-7 [generality].** Depletion reads `S_pot · B`, no aquatic-specific logic → a `cultivability` tier-2 depletes the same way (soil exhaustion) for free. Enforce in review.

**Open questions (Layer 2b):**
- **Q1 — Collapse = disperse or RELOCATE?** v1 disperses (pool fissions to mobile bands); **relocation** (the settlement hops to a fresh nearby reach) is the richer behaviour and the Carneiro pivot when no fresh reach exists (circumscription → can't relocate → intensify/fight). *Recommend disperse v1, relocation as the Carneiro follow-on with §8-Q1 contested catchments.*
- **Q2 — Depletion stock: reuse GD-1 `B` or a separate tier-2 stock?** *Recommend reuse GD-1 `B`* (one depletion model, gives the spatial halo for free); a separate stock only if tier-2 must degrade on a different timescale than tier-1.
- **Q3 — Extraction pressure shape:** uniform `N/n_cells` over the catchment, or distance-weighted (nearer cells worked harder → a sharper halo)? *Recommend uniform v1, distance-weighted if the halo needs to bite spatially.*

**Recommendation:** build Layer 2b as GD-1-reuse tier-2 depletion with the foraging-pressure remap, `enable_tier2_depletion` default-OFF, disperse-on-collapse v1, resource-agnostic. Validate the **boom→degrade→bust→fallow→reboom cycle** on the aquatic world (does a rich reach cycle on a generational timescale without tuning to a target?), confirming the equilibrium village is *sustainable* and the bust is an *earned overshoot*.

## 10b. Reframe + the TRACTABLE CORE we build now (2026-07-04)

Straightening the resource ecology (supervisor) corrected §10's pure-depletion model — the tiers differ sharply:
- **Fisheries ≈ SUSTAINABLE.** Salmon self-renews (oceanic stock); NW-Coast villages were stable for *millennia* (Ames). So a salmon settlement should PERSIST, not boom-bust from depletion. Its dynamic is seasonal **GLUT + STORAGE buffer + episodic SHOCK**, not slow exhaustion.
- **Only proto-ag (swidden) has the generational soil-depletion → relocation cycle** (Boserup 1965; Blaikie & Brookfield 1987 landesque capital) — **DEFERRED to the `cultivability` tier** (§10 is that path).
- **LEARNING / landesque capital** (yield rises durably with sustained investment — weirs/terraces/irrigation/skill) is a *stabilizing* positive feedback — **DEFERRED with ag**.
- **Dispersal triggers are NOT inevitable depletion.** Four distinct: (1) **OVERSHOOT** (pop > carrying; Malthus/Boserup), (2) **SHOCK** (a bad year, buffered by storage), (3) soil-exhaustion (ag only — deferred), (4) **social scalar-stress** (already covered by size-repulsion).

**THE CORE BUILD (this):** sustainable tier-2 (no long-term depletion) + seasonality + a regional **SHOCK** + **storage buffer** → dispersal EMERGES on deficit (unbuffered shock or overshoot). Soil-depletion + learning deferred to proto-ag.

**SHOCK mechanism.** Once per `aggregation_period` (a year), a **mean-preserving regional lognormal multiplier** `s ~ LN(CV = shock_cv)` scales that year's `_settlement_catchment_yield` (reuses the `game_meat_cv` draw pattern already in `_step_rivalrous`; **shared across the region** — a correlated climate bad year, which cannot be insured away by exchange). Anchor: salmon run inter-annual CV ~0.5–1+ (ENSO/ocean regimes — *why* NW-Coast stored obsessively and occasionally relocated). **Storage buffers it** (`_cell_store`, already built — this finally makes storage *load-bearing*): full granaries ride out a bad year; thin ones → deficit. **Dispersal is EMERGENT** — the deficit runs the existing starvation mortality → the pool shrinks below `settle_min_pool` → `_maintain_settlements` hysteresis dissolves the settlement → residents revert to mobile. *No scripted dispersal rule.* (Optional v1.1: deficit-driven **out-migration**, settled→mobile, before death.)

**Calibration target:** `shock_cv`/frequency tuned so a **well-stored equilibrium village survives ordinary bad years** (stable fishery = the NW-Coast benchmark) and only a **severe/multi-year shock or an OVERSHOT/under-stored village disperses** → "bust = *earned*".

**New knobs:** `enable_tier2_shock` (default OFF ⇒ bit-exact), `shock_cv` [PROVISIONAL, salmon-anchored]; seasonality reuses `ClimateField.season()`.

**Red-team (core):** RT-1 *shock too harsh → nothing survives* → tune so storage covers ordinary years; validate a stored village is stable. RT-2 *storage doesn't actually buffer settlements* → verify settled surplus banks to `_cell_store` and is drawn on deficit (may need wiring — check first). RT-3 *idiosyncratic vs regional* → regional (shared draw) so shocks are correlated (realistic, and produces real collapse events). RT-4 *bit-exact* → `enable_tier2_shock` gate. RT-5 *overshoot never bites* → confirm a village grown past carrying disperses on the first shock.

**Validation:** salmon world → settlements PERSIST through ordinary shocks (stable villages); a severe/multi-year shock or an overshoot disperses; **storage level predicts survival**. Swidden relocation cycle + landesque intensification deferred to the `cultivability` tier (§10).
