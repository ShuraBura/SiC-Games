# SiC Games — Phase 1 — Aggregation-Sedentism (settlements as multi-band coalescence; v2 logistical catchment)

**Status:** SCOPED + RED-TEAMED 2026-07-04 — **NOT YET BUILT** (supervisor sign-off + §8 open questions first). Supersedes the *single-band cell-packing* approach of `…_EconomicDefensibility_Scoping.md` / `…_StorageSedentism_Scoping.md`, which repeatedly failed: forcing one ~25-band onto a cell is either inert (too sparse to bootstrap) or a death spiral (over-subscription). This reframes settlement as **multi-band aggregation** at a rich node — the correct anthropological unit — reusing the aggregation + fission–fusion + morph machinery already built.

**Anchors:** Mauss & Beuchat 1904/1979 (seasonal aggregation↔dispersal — sedentism = the aggregation phase gone year-round); Binford 2001 (forager↔**collector** logistical mobility; the ~0.091/km² **packing threshold** = a *regional* density = `BINFORD_PACKING_PER_KM2`); Vita-Finzi & Higgs 1970 (**site-catchment** analysis — the forage territory around a residential base); Johnson 1982 (**scalar stress** — aggregation size → integrative hierarchy); Bandy 2004 (village fissioning vs the hierarchy that holds a pool together); Testart 1982 (storable dense predictable resource → delayed return); Ames & Maschner 1999 (NW-Coast winter villages = coalesced House-groups); Bar-Yosef & Belfer-Cohen (Natufian hamlets = multi-household aggregations, dozens–~150); Dyson-Hudson & Smith 1978 (economic defensibility → the defended object is the **catchment**); Carneiro 1970 (circumscription emerges when catchments **overlap**).

**Motivation (what the runs taught us):**
- **R-51 + the defensibility A/Bs:** on the natural substrate the landscape sits at ~0.015/km² — ~6× **below** Binford packing — so it is genuinely *under-populated relative to where real foragers settled*, and no local mechanism can manufacture density a sparse population doesn't have. Every concentration attempt (C8 subsidy GATE-3; defensibility inert→fitness-edge→death-spiral) failed for this one reason.
- **Q1 (lit):** settlements form by **coalescence of multiple bands/households** at a rich node (crystallised seasonal aggregation), not a single band settling — the founding unit is ~100–300 people, not ~25. Between-band *cell* exclusion (my defensibility v1) actively *prevents* the coalescence that makes villages.
- **Q2 (lit):** sedentism onset clusters at/above the ~0.091/km² regional density; complex foragers ran ~0.5–5/km². Our equilibrium is well below → too few people. The fix is to raise *regional* density and let bands *aggregate*, not to force one band to pack.

## 1. The mechanism — "the gathering that stops dispersing"
The built `_do_gathering` (phase1_model.py) already realises Mauss's aggregation phase: every `aggregation_period` steps in the abundance window it finds abundant sites (top-capacity, min-separated), pools the bands nearest each site into a **connubium**, pairs across bands, then everyone **disperses**. The single new idea:

> **At a *persistently* abundant, storable, defensible site, the pooled bands do not disperse — they co-locate and *stay*, forming a SETTLEMENT.**

A settlement is therefore a **multi-band aggregation** (the pool), which supplies the residential density that a single band never could → residential packing crosses Binford 0.091 → the density morph fires; scalar stress from pool size drives hierarchy (Johnson) → complex/stratified *emerges*, not forced. Collapse (resource/payoff failure) → the pool fissions back to mobile bands — the boom→bust seam for the dynastic cycle.

## 2. v2 — logistical catchment (the target; residence ≠ foraging)
A settlement **resides** on a small site cluster but **forages a catchment** (Binford collectors; Vita-Finzi & Higgs). This is the core of v2 and is what makes real residential densities possible (density decoupled from the residential cell's own food):
- **Catchment pool.** A settled resident's food is drawn from the pooled yield of catchment cells within `catchment_radius` of the site, split among residents; those catchment cells **deplete** (GD-1) under the settlement's foraging pressure.
- **Depletion halo.** The catchment degrades around the settlement (the central-place depletion halo already in LITERATURE.md) → eventual relocation / intensification.
- **Carrying / collapse.** Settlement persists while `pool_size ≤ catchment_carrying`; past it (or when the halo bites) → fission. This is the anti-over-subscription gate the tether-forcing lacked.
- **Carneiro for free.** When regional density rises and **catchments overlap**, settlements can no longer relocate to escape a spent halo → intensify or contest → circumscription-driven complexity/conflict emerges *endogenously*.

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
Build aggregation-sedentism as the settlement mechanism, target **v2 logistical catchment**, via the **two-layer** path (lifecycle first, catchment-harvest second), `enable_aggregation_sedentism` default-OFF, resource-agnostic. It is the anthropologically-correct unit (multi-band coalescence), reuses the gathering + fission–fusion + morph code we trust, gives defensibility its correct **catchment** grain, and makes Carneiro circumscription + the depletion halo + the dynastic collapse emerge endogenously. Resolve §8 (esp. Q1 contested-catchment and Q3 hold-mechanism) with the supervisor, then build Layer 1 and validate the lifecycle before Layer 2.
