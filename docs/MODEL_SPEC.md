# SiC Games — Model Specification: Resource Layer

**Document:** `MODEL_SPEC.md`  
**Scope:** Resource-layer literature treatment and seasonal architecture. This document does NOT reconstitute the former MODEL_SPEC v0.2 (split into `ARCHITECTURE.md` and `MECHANISMS.md` on 2026-06-06; archived at `archive/superseded/`). It is a new, focused methodology record for the resource layer only.  
**Status:** LIVE (created 2026-06-14)  
**Maintainer protocol:** Updated when a resource-layer constant, formula, or seam is introduced, changed, or locked. Every factual claim carries a LITERATURE.md citation. No parameter values are authoritative here — route to `docs/PARAMETERS.md` for all locked values.

---

## Resource Layer: Literature Treatment and Seasonal Architecture

### §4.1.1 Return-rate formula and constants

**Canonical formula:**

```
kcal/hr = mass_live_per_hr (kg/hr) × edible_fraction × energy_density (kcal/kg)
```

Applied only to [CONVERTED] cells (raw kg/hr data from source). [NATIVE] cells have kcal/hr reported directly in the source and do not use this formula.

**Constants:**

| Constant | Value | Source | Rationale |
|---|---|---|---|
| edible_fraction | 0.50 | Hurtado & Hill 1987 (grassland subsistence ecology) | Conservative/consumed fraction — the proportion of live mass that is actually edible and consumed. Intentionally conservative to avoid overestimating yields. |
| energy_density | 1,460 kcal/kg | Hill et al. 1987, fn 3 (Ache foraging decisions) | Standard mixed-game tissue value. Applied only when the source reports mass rather than energy directly. |

**Lock:** These constants are locked and must not be changed without a supervisor-approved `LITERATURE.md` update citing a replacement primary source. Any change requires updating both the constant table in `docs/PARAMETERS.md` and all [CONVERTED] cells in `SiC_Games_Resource_Return_Rate_Table.md` that depend on it.

---

### §4.1.2 Native rates vs. converted rates

**Definitions:**

| Tag | Meaning | Applied to |
|---|---|---|
| [NATIVE] | Rate taken directly from source in kcal/hr — no formula applied | Forest (Hill 1987 Table 2), Desert (Bird 2009 Table 1), Intertidal (Bliege Bird 2001 Table 2) |
| [CONVERTED] | Formula applied to raw kg/hr data from source | Savanna (Hawkes 1991 raw kg/hr → kcal/hr) |

**Construct seam — forest cell (handling-only denominator):**

The forest game cell (Hill et al. 1987) uses a handling-only denominator: "Includes time spent in acquisition attempts plus all relevant processing" (Table 2, footnote a). Search time is excluded. All other game biome cells use search-inclusive denominators (time from departure to return, including travel and search).

This asymmetry is an accepted and documented consequence of the available literature. It is not a calibration error. The forest cell is not directly comparable to all other cells on a pure time basis — it will appear artificially high relative to its search-inclusive equivalent.

**Harmonisation prohibition:** Any future attempt to harmonise the forest cell to a search-inclusive denominator requires: (a) a primary-source replacement that reports search-inclusive forest game rates, (b) a `LITERATURE.md` update, and (c) supervisor approval. The existing forest cell must not be adjusted by an assumed search-time multiplier without a primary-source basis.

---

### §4.1.3 Unanchored cells policy

Two game biome cells are permanently or currently UNANCHORED:

| Cell | Type | Status | Reason |
|---|---|---|---|
| Wetland | UNANCHORED (current) | No primary-source kcal/hr found | Three candidates checked (Hill et al. 1997, Gurven & Hill 2009, Redford & Robinson 1987): all negative for time-denominated energetics. Hill 1997 records caiman as trace Ache prey (5 individuals, 25 kg, no time denominator); Redford & Robinson use a dimensionless harvest-rate metric, not kcal/hr. |
| Mountain | UNANCHORED (permanent) | No source exists | No HG literature reports mountain-specific game return rates. Gap is structural, not a search failure. |

**Model behaviour at UNANCHORED cells:** zero game yield by default. If the build requires a non-zero placeholder, the placeholder must be:
1. Documented explicitly as a placeholder (not an empirical anchor)
2. Never cited as evidence for any kcal/hr claim
3. Flagged for removal as soon as a primary source is found

**Fill protocol:** Filling an UNANCHORED cell requires: (a) a primary journal-article source reporting kcal/hr or a convertible kg/hr rate, (b) a `LITERATURE.md` update logging the source, (c) supervisor approval before implementation in the model.

---

### §4.1.4 Forage seasonal signal

**Functional form:** One periodic signal per biome, parameterised by (amplitude A, phase φ, lean-season cause). This is a phenomenological model — not a mechanistic NPP model. Curves are fit to the HG forage-availability literature; no insolation→NPP transfer function is used.

**Empirical anchors by biome:**

| Biome | Anchor source | Amplitude | Phase / lean-season cause |
|---|---|---|---|
| Forest (Ache, Paraguay) | Hill et al. 1984 (seasonal variance in Ache diet) | **Low** — total caloric intake does not differ significantly across quarterly periods; compositional variance only (honey peaks Q4, vegetable Q3) | No lean season in calories. Fat season (Apr–Jun) raises game caloric value ~25% (ungulate fat accumulation) but does not depress other resources. The flat anchor. |
| Llanos/grassland (Hiwi, Venezuela) | Hurtado & Hill 1987 | **High** — ~90% of annual rain (~1,665 mm) falls in wet season (May–Nov); wet=lean (flood suppresses access); dry=game-fat via aggregation | Wet = lean (Liebig's Law: flood as access constraint, not calorie shortage per se). Dry = game-fat via prey aggregation (caiman: 44→489 kg/km², ~11× wet→dry swing). The sharp anchor. |
| Fynbos/shrubland (Cape Floristic Region, South Africa) | De Vynck et al. 2016 | **Moderate** | USO availability peaks July–December (southern hemisphere winter through early summer). Lean season: December–February (hot-dry austral summer). |
| Savanna (Hadza, Tanzania) | Hawkes et al. 1991; Berbesque & Marlowe 2009 | **Moderate** | Dry-season water aggregation makes game accessible (intercept hunting activates Aug–Oct). Tubers available year-round as floor resource; moderate seasonal amplitude on game access rather than total forager caloric intake. |

**Amplitude range:** Forest (Ache) ≈ flat (low end); llanos (Hiwi) ≈ 90% rain in half the year (high end). This Earth reference range bounds the star-mechanics lottery for seasonal amplitude draws (see §4.1.6).

**Signal is world-level, not layer-level:** one insolation/seasonal signal per world, read independently by both forage layer and game layer. The forage≠game distinction is carried in curve shape (caloric-value signal for forage; encounter-rate/access signal for game), not in separate timing systems.

---

### §4.1.5 Game seasonal signal

The game seasonal signal differs mechanistically from the forage signal. Two distinct mechanisms must not be collapsed into a single sine:

**Mechanism 1 — Value-via-fat (forest, Ache):**

- Encounter rate is roughly aseasonal (men encounter prey year-round at similar rates).
- Caloric *value* per kill rises ~25% in April–June due to ungulate and small-bodied game fat accumulation at the warm→cold season transition (Hill et al. 1987; documented in Table 2 context and armadillo weight data in Table 3).
- Fat-season multiplier ×1.25 applied only when seasonal layer is active. NOT applied to static cell values in the game return-rate table.
- Armadillo shows extreme within-year fat variation: body fat may range from <1% (early wet season, Oct–Dec) to ~20% (late wet season, Mar–Apr). Men avoid burrow excavation in early wet season (low-ranked below mean foraging return rate at that time).

**Mechanism 2 — Access-via-aggregation (savanna, llanos):**

- Encounter rate rises sharply as water sources shrink in the dry season.
- Prey aggregate at predictable locations (waterholes, shrinking water bodies), making intercept hunting viable.
- Empirical anchors:
  - Hiwi (Venezuela): caiman 44→489 kg/km², ~11× wet→dry density swing (Hurtado & Hill 1987).
  - Hadza (Tanzania): intercept hunting (night, at water blinds, ~745 kcal/hr converted) practiced ONLY in late dry season Aug–Oct; encounter hunting year-round (~518 kcal/hr converted) (Hawkes et al. 1991).
- Functional form: threshold-like modifier on encounter rate (not a smooth multiplicative modifier on value). Intercept hunting switches on at a dry-season access threshold, not continuously.

**These two mechanisms are functionally distinct and must be implemented separately:**
- Fat-value modifier: smooth multiplicative on kill value (continuous, season-length signal).
- Aggregation-access modifier: threshold-like on encounter rate (switches on late dry season).

**Game migration signal:** Dry-season water aggregation confirmed independently in two systems (Hiwi, Hadza). Broader ungulate range shift (true migration, not aggregation) is thin in the current literature and is deferred to the seasonal-game build stage. The game return-rate table documents static encounter rates; migration is a future mechanic.

---

### §4.1.6 Star-mechanics seam: seasonal amplitude range

**What star mechanics do:**

The per-world lottery draws a seasonal amplitude from a literature-grounded range. Stellar and orbital parameters (obliquity, eccentricity — Berger 1978 [INLINE]; Spiegel 2009/2010 [INLINE]; Kopparapu 2013 [INLINE]; Kasting 1993 [INLINE]) set the bounds of what is physically plausible for a habitable world. The drawn amplitude parameterises the forage and game seasonal curves for that world.

**What star mechanics do NOT do:**

Star mechanics do not drive the resource curves tick-by-tick. There is no insolation→NPP→forage transfer function. The astronomical papers earn their place in the project by bounding the parameter draws, not by running inside the agent loop.

**The single explicit coupling point:**

The seasonal amplitude parameter is the only direct coupling between the stellar/orbital literature and the resource curves. The star lottery sets amplitude; the phenomenological curve (anchored to the HG literature, §4.1.4) determines the shape. No other per-step coupling exists at this stage.

**Earth reference range (from empirical anchors):**
- Lower bound: forest (Ache) ≈ flat (amplitude ≈ 0)
- Upper bound: llanos (Hiwi) ≈ 90% of annual rain in ~6-month wet season (amplitude ≈ high)

The star lottery extends or contracts draws within the habitable-zone physics bounds; the Earth anchors define the central reference region of that distribution.

**Shock stochasticity (separate thread):**

The stochastic shock distribution (ENSO, megadroughts, volcanic forcing — Timmermann 2018 [INLINE], Cane 2005 [INLINE], Cook 2010 [INLINE], Sigl 2015 [INLINE], Wanner 2008 [INLINE], Mayewski 2004 [INLINE]) is a separate derivation from the periodic seasonal signal. These two threads are kept distinct:
- Orbital papers bound the seasonal range (periodic, predictable).
- Climate-variability papers ground the shock distribution (aperiodic, stochastic).

They are not folded together. Shocks are multiplicative perturbations on top of the seasonal signal, not a modification of the seasonal amplitude parameter.

---

### §4.1.7 Climate catastrophe seam (STUB)

**Status: STUB — interface defined, mechanic not implemented.**

**Seam definition:**

The catastrophe hook is a world-level amplitude modifier applied to the insolation/seasonal signal before the resource curves read it. A catastrophe event fires a multiplier (< 1.0 for a resource crash) or a floor suppressor against the seasonal amplitude for a defined number of steps.

**Interface contract:**

Any future catastrophe mechanic must write to this interface and to nothing else in the resource layer. Specifically:
- It MUST NOT directly modify cell kcal/hr values.
- It MUST NOT modify biome assignments or terrain structure.
- It MUST NOT write directly to agent state variables.
- It writes only to the amplitude modifier that the seasonal signal reads.

This constraint isolates the catastrophe mechanic from the resource substrate and prevents coupling explosions when the seasonal-game and catastrophe builds overlap.

**Literature in hand (for when this stage is scheduled):**

Timmermann 2018 [INLINE], Cane 2005 [INLINE], Cook 2010 [INLINE], Sigl 2015 [INLINE], Wanner 2008 [INLINE], Mayewski 2004 [INLINE] — shock-distribution papers grounding the amplitude and frequency of catastrophe events. These are noted but not yet extracted into `LITERATURE.md`.

---

*End of MODEL_SPEC.md resource-layer section.*

> **Cross-reference:** Parameter values (energy density, edible fraction, forage kcal targets, terrain constants) are authoritative in `docs/PARAMETERS.md`. This document records methodology and architecture; it does not own parameter values.
