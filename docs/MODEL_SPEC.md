# SiC Games — Model Specification (methodology record: resource, demographic & climate layers)

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

### §4.1.8 Game-mobility seam — per-biome migratory game / herd-following (added 2026-06-20)

**Status: SEAM — parameter wired, MECHANIC DEFERRED to the open-biome migration stage.**

A per-biome **`game_mobility` ∈ [0,1]** (terrain.py `GAME_MOBILITY` dict → `WorldFields.game_mobility`
per-cell field): **0 = resident game** (HG mobility comes from seasonal/patchy resource tracking, not herds);
**1 = fully migratory megafauna** (logistical **herd-following** dominates mobility — Binford's *collector*
end). **Architecture rationale:** migration is a *biome attribute*, not a monolithic mechanic — so it's
≈0 in the calibration biomes (forest/desert) **by construction** (resolves Game-Economy red-team RT-4:
migration cannot affect arid/temperate/lush), and the open-biome stage activates only where the parameter
is finite. Fits the existing seam pattern (climate §4.3.2, pathogen §4.3.3, catastrophe §4.1.7).

**Values (anchor: Binford 2001 — residential/logistical mobility + range size by biome / effective
temperature; the forager↔collector continuum):** `FOREST 0.0` (Aché — resident forest game), `DESERT 0.0`
(!Kung — resident, residential foragers), `SAVANNA 0.2` (Hadza — dry-season *aggregation*/access, not true
range-shift, §4.1.5), `GRASS/steppe 1.0` (Nunamiut caribou, plains bison — migratory ungulates, logistical
herd-following). Wetland/mountain/water → 0. **[PROVISIONAL values; the mechanic — a seasonally-translating
herd field + agent following, with biome-specific *radius* and *rate* sub-parameters — and the precise
Binford rate/radius extraction are the open-biome stage.]** Also addresses R-8 under-mobility there (the
resource-tracking driver that's missing).

**Interface contract:** the future migration mechanic reads `game_mobility` (and the game field) and writes
the herd position + the agent-following movement — it MUST NOT touch the demographic state, the NPP capacity,
or other terrain fields directly.

---

### §4.1.9 Climate stage — IMPLEMENTED orbital-lottery model (C.1–C.3, added 2026-06-24)

**Status: BUILT (C.1 seasonal, C.2 eccentricity+flux+interannual, C.3 regime-shift). C.4 catastrophe / C.5
water-aggregation pending.** Code: `sic_games/src/sic_games/climate.py`; blueprint:
`blueprints/phase1/SiC_Games_P1_Climate_OrbitalLottery_Scoping.md`.

**Design discipline (honours §4.1.6/§4.1.7).** The `ClimateField` wraps the carrying-capacity field and
multiplies it by a time-varying climate factor; the demographic substrate is UNCHANGED code that merely reads
a time-varying field (R-6 `run_2d` isolation). Stellar/orbital mechanics **BOUND the per-world parameter
draws** (a one-time lottery) — they do NOT run tick-by-tick; there is no insolation→NPP transfer function.

**Carrying-capacity factor (peak-normalised to 1.0):**

> `level(x,y,t) = base.level(x,y) · mean_factor · season(t) · interannual(t) · regime(t)`

where `mean_factor ≥ 1` is the per-world eccentricity brightening (a baseline scalar, outside the [0,1]
temporal product) and the three temporal layers each ∈ (0,1] with peak pinned at 1.0.

**The per-world lottery** (`draw_world_climate`, Q3 = UNIFORM draws over the habitable range, no Earth-leaning
prior): draws obliquity ε, eccentricity e, stellar flux S, and the ENSO/regime nuisance params, then maps
them to the field params below.

**Parameter & literature table (all values used as anchors):**

| Param | Draw range (uniform) | Map → field param | Anchor (citation) | Method / transform |
|---|---|---|---|---|
| obliquity ε | [0°, 60°] | `A_seas = a_earth·sin ε / sin 23.4°` (clamped [0,1]) | Spiegel 2009 (broad habitable band); Williams & Kasting 1997 | **Q1-(B):** scales the *empirical* Earth per-biome amplitude (§4.1.4) by the insolation-contrast ratio — a provisional BOUNDING heuristic, NOT a sunlight→food transfer fn. Earth ε→Earth amplitude by construction. |
| — Earth amplitudes `a_earth` | (fixed) forest 0.05 / savanna 0.40 / llanos 0.60 | seeds `A_seas` | Hill 1984; Hawkes 1991; Hurtado & Hill 1987 | §4.1.4 empirical seasonal amplitude `A_seas≡1−s_min` per biome at Earth tilt. |
| eccentricity e | [0, 0.6] | `mean_factor = (1−e²)^(−½)` | Spiegel 2010 (e>0.6 snowball-marginal) | Annual-mean flux brightening. e=0.017→1.0001, e=0.6→1.25. A baseline CC scalar (not temporal). |
| stellar flux S | [0.34, 1.05] S⊕ | `T̄ = 14 + 255·(S^¼ − 1)` °C | Kopparapu 2013 (HZ edges); Stefan-Boltzmann | `T_eff ∝ S^¼`, anchored S=1→14°C via a fixed effective-greenhouse offset (RT-3: bare T_eff ~33 K too cold). **A world property/seam — currently NOTHING reads it** (pathogen reads NPP, not T; §4.6.3). |
| ENSO amplitude | [0.20, 0.40] | `interannual_amp` | Timmermann 2018 | Layer-2 quasi-periodic DEPRESSION (bad years only, ≤1): `interannual(t)=1−amp·max(0,sin(2πt/P+φ))`. |
| ENSO period | [2, 7] yr ×12 | `interannual_period` (steps) | Timmermann 2018 | Single drawn period (irregular/stochastic ENSO = a refinement). |
| regime amplitude A_reg | **central [0.10, 0.15]** | `regime_amp` | Wanner 2008 (LIA global-mean ~0.5°C → ±10–15% CC) | Layer-3 depression while in excursion. **Tails (±30% / ~1°C, `REGIME_AMP_TAIL`) reserved for C.4-flagged 8.2-kyr/YD events**, not the routine lottery (v2 red-team). °C→CC% is interpretive (no NPP transfer fn). |
| excursion **duration** | [100, 500] yr ×12 | `regime_duration` (steps) | LIA ≈ 500 yr; Wanner 2008 / Mayewski 2004 | Mean dwell in the excursion state, P(end)=1/duration. |
| excursion **recurrence** | [1000, 2000] yr ×12 | `regime_recurrence` (steps) | Bond ~1500 yr; Mayewski RCC | Mean onset spacing, P(onset)=1/recurrence. **≠ duration** (v2 fix: the two were conflated). |

**Layer 3 process (the key C.3 correction).** `regime(t) = 1 − A_reg·state(t)` where `state ∈ {0,1}` is a
**two-state Markov / telegraph** chain with geometric dwell times (NOT an Ornstein-Uhlenbeck wiggle — v2
red-team). It produces a *sustained multi-generational plateau*: the level holds depressed for the whole
excursion (~100–500 yr ≫ a ~25-yr generation) and then switches back. Stationary occupancy =
`duration/(duration+recurrence)` (≈1500 yr recurrence × ~300 yr duration ⇒ excursions are the Earth-rare
minority state). `regime_amp=0` ⇒ `regime≡1`, nesting bit-exact to C.2.

**Seasonal form (validated R-6, unchanged).** `season(t)=s_min+(1−s_min)·½(1+cos(2πt/P−φ))`,
`A_seas≡1−s_min`, range `[s_min,1]`, peak-normalised; `A_seas=0 ⇒ season≡1` (aseasonal baseline bit-exact).
Per-biome phase φ. **The §4.1.5 game threshold-access signal must NOT be smoothed by this multiplier.**

**Validation (gates).** C.1: on R-6's exact config the multiplier reproduces the 37% trough bit-for-bit (unit
test on the algebraic identity); the regime-dependent 61%/96% eq_pop responses are correct (at-ceiling bites
hard, below-K bites less). C.3: forced excursion = a perfectly flat depressed plateau (zero variance) +
occupancy within 3% of the duty cycle; a 900-step demographic run at A_reg=0.15 → eq_pop ratio 0.891
(sustained, proportional; population as stable as baseline = a held plateau, not a collapse/wiggle). Full
suite green at each step (C.1 cf74bda 492; C.2 e4ccd33 499; C.3 18 climate tests).

**Honest seams / deferred.** (a) `flux_to_temperature` sets a dormant world property — wiring pathogen→T (or
→the climate-modulated CC) is a future step, NOT free. (b) The regime layer ENABLES but does NOT CAUSE the
§4.5.10 society morph — that needs the deferred storage/surplus mechanic (Testart) + a periodic
`society_from_character` call; C.3 ships the climate layer only.

**C.4 catastrophe — the two biome-specific shocks (sub-biome split BUILT; layers pending).** A v3 red-team
(2026-06-24) caught that the single `BIOME_GRASS` code conflates *tropical-llanos* (Hurtado & Hill forage/game
anchors) and *temperate-arctic steppe* (caribou/bison mobility + meat_frac anchors), so the two approved shocks
targeted identical cells. **C.4a (BUILT, `terrain.py`):** the dormant `temperature` placeholder (verified:
nothing read it) becomes a **latitudinal gradient** (equator `TEMP_EQUATOR_C=27 °C` → high-lat
`TEMP_HIGHLAT_C=1 °C`, 14 °C area-mean preserved); a new per-cell `grass_subtype` splits GRASS by the
`GRASS_TROPICAL_THRESHOLD_C=18 °C` Köppen isotherm → `GRASS_LLANOS` (warm) / `GRASS_STEPPE` (cool). Gate:
non-degenerate split on 4 seeds; tag exhaustive on grass; T-mean 14.00. **C.4b (BUILT, ON since 2026-08-06):** a
**23–67 yr** caribou quasi-cycle (St. John 2022 — median period 40.5, observed range 23–67 over the **19 cyclic
herds of 43 collected**; amplitude 0.871-about-mean ⇒ ~93% peak-to-trough; Vors & Boyce 57% corroboration only,
and still not filed). **This read "40–90 yr" until the thesis was filed and read — see Addendum 32; the old band
excluded everything below the median and ran past the longest cycle measured.** St. John is an UNDERGRADUATE
thesis, not peer-reviewed: the weakest anchor in the climate layer.)
on `GRASS_STEPPE` **meat only** (supervisor choice B). ClimateField exposes `meat_factor(x,y)` =
`(1+a·cos(2πt/P+φ))/(1+a)` (peak-pinned, trough ≈0.069), masked to steppe cells; the economy applies it as
`meat_pool *= tf.meat_factor(cx,cy)` (phase1_model.py:354) — the forage slice `(1−meat_frac)·S` is untouched,
so a herd crash is not a plant crash. Duck-typed (no-climate runs bit-exact). Gate: 700-step run at trough,
meat_frac=0.66 → eq_pop ratio 0.614; meat_frac=0 → ratio 1.000 exactly (meat-only, no forage leakage). **C.4c (BUILT):**
the llanos flood as the heavy TAIL of Layer-2 interannual on `GRASS_LLANOS` forage (Hamilton et al. inundation
1,278–105,454 km², median 25,374). Because both flood extremes hurt the forager, the llanos interannual is
**two-sided** `1 − amp·|sin θ|` (worst at either extreme), vs the generic one-sided ENSO, on the same Layer-2
clock — REPLACING the ENSO form on llanos cells (one process per cell, no double-count). `level()` routes
through a per-cell `interannual_at(x,y)` (== generic off-llanos → bit-exact). The amplitude is **drawn per world
over the lit-bounded band [0.15, 0.45]** (the km²→kcal mapping stays interpretive within the band): lower 0.15 =
Castello et al. 2015 Lower-Amazon flood-pulse fishery (climate ~18% of yield variance; per-extreme swings
~15–20%; "high & low waters exert EQUAL forcing" → the two-sided basis); upper 0.45 = **Sarmiento et al. 2004
MEASURED** Apure-llanos production drop in an exceptional-flood year (TotalANPP 1996 flood 265–418 vs 1997
normal 601–659 g/m² ungrazed → −37 to −56%, central ~45%; "both drought & water excess limit production, even
more in wet years" confirms two-sidedness; Welcomme 1979 corroborates) — a direct flood-year→production
measurement, not interpretive. Gate: 700-step run, full-llanos mask at |sin θ|=1, amp 0.45 →
eq_pop ratio 0.872 (sustained forage depression; below-K slack absorbs part). A stochastic heavy-tail (vs the
regular two-sided swing) is a noted refinement.

**C.5 water→aggregation = dry-season INTERCEPT HUNTING (BUILT; on/off flag, ON by default).** Two scoping
findings: (1) no aggregation MECHANIC existed to "reuse" (`game_mobility` is a deferred seam, §4.1.8; the true
logistical migration is the thin/deferred open-biome stage); (2) the ALWAYS-ON "good hunting near water" is
already in the terrain (`wateracc` is 55% of the moisture term → NPP → forage+game, terrain.py:529). So C.5 adds
only the genuinely-seasonal piece: the **intercept-hunting peak** — as ephemeral water dries, game funnels to
permanent waterholes and night-water-blind hunting switches on, ONLY in the late dry season (§4.1.5,
threshold-like). Built as a **meat-channel BOOST** (a red-team corrected an earlier mean-conserved
*redistribution* that had the wrong sign): `_intercept_factor = 1 + INTERCEPT_BOOST·wateracc(x,y)` on
savanna+llanos cells, gated ON when `(1−season)/A_seas ≥ INTERCEPT_DRY_THRESHOLD=0.75`; `INTERCEPT_BOOST =
745/518 − 1 ≈ +0.44` (Hadza intercept vs encounter hunting, Hawkes 1991). Economy: `meat_pool *= meat_factor`
(= `_caribou_factor · _intercept_factor`, disjoint biomes); forage capacity untouched. Gate (correct metric =
realized return): late-dry near-water **meat/forager ×1.25–1.41** (≈ the +44% anchor); eq_pop unchanged within
noise (density-regulated regime — the boost fattens foragers, doesn't add bodies); `meat_frac=0 → 1.000`
(meat-only). Lit: Hadza 518→745 kcal/hr; Hiwi caiman ~11× (game-at-water corroboration); always-on baseline in
terrain.py:529.

**§4.1.9 Controlled-climate benchmark harness — the `ClimateDriver` (BUILT 2026-06-30; methods home).** A
**methodological tool**, not a climate mechanic: it lets the dynamic-social stages be benchmarked against *known*
climate, separating a social response from the production telegraph's noise. **Motivation (R-27 red-team #3):** on
the stochastic `ClimateField` telegraph a single run gives a noisy, lag-confounded "response" — a band fission or
pop crash cannot be told from a *random* climate excursion. **Construct:** `ClimateDriver` is a deterministic,
pure callable `t → regime multiplier ∈ [0,1]` (1.0 = good times; <1 = a depressed multi-generation period) that,
when passed as `ClimateField(regime_driver=…)`, **overrides the stochastic telegraph on the regime channel** (the
seasonal/ENSO/caribou/llanos layers are untouched; `regime_driver=None` ⇒ telegraph, bit-exact). Named waveform
factories — `flat` (the control arm), `step` (a permanent downshift / press), `pulse` (a single catastrophe of
known onset+length), `ramp` (a slow squeeze), `square` (a deterministic good/bad alternation), and `piecewise`
(an arbitrary "known-times" trajectory). These are **experimental-design constructs, NOT lit-anchored climate**;
for realism-bounded stress set the depressed multiplier within the C.3 band (1−[0.10,0.15]), or use
1−`REGIME_AMP_TAIL`=0.70 for an explicit catastrophe. **Estimator (the harness's point):** because the control
and shock arms are *bit-identical until the scripted onset*, the clean climate-attributable response is the
**between-arm difference at matched times** (a difference-in-differences read: ΔPRE ≈ 0 is the common-trend /
placebo check, and ΔDURING / ΔPOST are the response) — free of the underlying population-growth trend that
confounds a within-arm PRE→POST comparison. The harness (`run_se0_controlled_climate.py`) exposes a reusable
`run_controlled(driver, …)` returning a per-step trajectory; Stage 1+ import it and pass their own driver +
mechanism flags. The stochastic telegraph remains the *production* substrate once a mechanism is validated here.
Validation: R-28 (5 driver unit tests: waveform shapes, purity/determinism, telegraph override, `None`
bit-exactness, `flat`=no-regime; + the demo's ΔPRE = −0.00 placebo).

---

## Demographic Layer: Literature Treatment (added 2026-06-18)

Mortality + fertility methodology — same discipline as the resource layer: each value records its source,
extraction, and the **exact transformation** of the literature number. Values authoritative in
`PARAMETERS.md`; findings in `RESULTS.md`.

### §4.2.1 Siler mortality coefficients — Aché forest (M-1)
**Value:** `a1=0.157, b1=0.721, a2=0.013, a3=4.80×10⁻⁵, b3=0.103` (annual; age in years), form
`h(x)=a1·exp(−b1·x)+a2+a3·exp(b3·x)`. **Source:** Gurven & Kaplan 2007 (PDR 33:321–365), Table 2,
"Aché forest (e₀=37)", both sexes. **Extraction:** Table 2 renders right-to-left in the filed PDF; pulled
via pdfplumber word-coordinate reconstruction (group by `top`, sort by `x0`, reverse each token),
cross-checked two ways, **confirmed against the filed copy 2026-06-18**. **Transformation:** none —
published constants (FIXED, not re-fit). **Validation:** closed-form `l(x)=exp(−H(x))`,
`H(x)=(a1/b1)(1−e^{−b1x})+a2x+(a3/b3)(e^{b3x}−1)`, reproduces e₀=36.5 / e₁₅=38.3 / e₄₅=21.3 / l(15)=0.66
/ l(45)=0.43 / mode=71 / MRDT=6.7 — matching the paper.

### §4.2.2 Monthly hazard conversion (×12 guard)
1 step = 1 month; coefficients annual → `p_month = 1 − exp(−h_year(age)/12)`. Unit test asserts the
month-stepped survivorship equals the closed-form annual `l(x)` (guards the classic ×12 error).

### §4.2.3 Sex split — sex-specific Siler (M-3)
**Source:** Hill & Hurtado 1996, Ch. 6, forest period: male childhood mortality = **0.71×** female;
male adult mortality = **1.47×** female. **Extraction:** age-specific sex curves are in figures
(not machine-readable) → the two documented ratios applied to the both-sexes Siler as a *level* split.
**Transformation (preserving the sex-average):**
- childhood ratio `r_c=0.71` scales `a1`: `a1_F = a1_both·2/(1+r_c) = 0.1836`, `a1_M = r_c·a1_F = 0.1304`.
- adult ratio `r_a=1.47` scales the **Gompertz** `a3`: `a3_F = a3_both·2/(1+r_a) = 3.89e-5`, `a3_M = r_a·a3_F = 5.71e-5`.
- Makeham `a2 = 0.013` **shared**; `b1,b3` common. `0.5(F+M)=both` for each scaled term → reproduces the life table.
**Why `a3` not `a2`:** `a2` is age-independent; scaling it crosses the sexes over at ~age 4, but the
monograph has females disadvantaged throughout childhood (crossover ~age 20). Scaling the Gompertz `a3`
lands the crossover in adolescence (verified by the ordering test). **Result (F/M):** a1 0.1836/0.1304 ·
a2 0.013/0.013 · a3 3.89e-5/5.71e-5 · b1 0.721 · b3 0.103. **Caveat:** level approximation; exact crossover
age approximate (figures not digitized).

### §4.2.4 Maternal mortality — approach (ii)
First pass folds maternal into the all-cause female Siler (the H&H ratios are all-cause) → explicit
per-birth term = 0 (no double-count). Maternal-removed fit (approach (a)) deferred — needs the Aché
maternal rate.

### §4.2.5 Fertility (Aché)
Menarche/menopause 15/42 yr → fertile window [180,504] mo. SRB 0.512 male (105:100). Target **IBI ≈ 37 mo**
(H&H); `fecundability` (monthly birth prob past the ~30-mo lactational refractory) is the **only free
fertility knob**, bisection-calibrated to IBI=37 → ≈0.12/mo. TFR=7.9 emergent (Aché ~8; a *check*).
Growth r=+3.3%/yr emergent (forest Aché grew ~2.5%; r≈0 is a Step-2 property).

### §4.2.6 Founder ages
Sampled ∝ `l(x)` (the stationary / Aché-shaped young pyramid).

### §4.2.7 Child mortality — cause structure (Resource-Ecology Phase C / T-4 calibration targets, 2026-06-20)
Extracted from the filed monographs to ground how emergent child mortality should decompose. **Both
precontact forager populations show ≈ZERO nutritional/starvation child death** — children are buffered;
nutritional stress acts by *potentiating disease*, not by direct starvation.

**Aché forest period** (Hill & Hurtado 1996, *Aché Life History*, Ch. 5 "Causes of Mortality", Table 5.1;
382 deaths). Four categories, NO nutritional category: **conspecific violence ~50%+** (Ache-initiated
homicide/**infanticide** = ~40% of violent deaths, concentrated in *unweaned* infants 0–3; external warfare
= ~60% of violent deaths, older ages), **illness/disease ~24%** (lethal mainly in unweaned infants; weaned
children 4–14 are *"the healthiest age group,"* killed mostly by accident/violence), **accident ~12.5%**
(rises with age, food-acquisition-related, rare in young children), degenerative/congenital the remainder.
Infanticide is **condition-dependent** in the ethnography: too-short birth interval (the next child killed),
parental death/orphan, lack of a sponsor/support, deformity.

**Hiwi precontact** (Hill, Hurtado & Walker 2007, *J. Hum. Evol.* 52:443, Table 5 — cause-specific rates
per 1000 risk-years; Table 4 — % by cause): mid-childhood (1–9 yr) **disease 21♂/16♀**, congenital 3/2,
accident 7/2, violence 5/2; infant (0) disease 51/68, congenital 51/68, accident 13/27, violence 64/108.
**Nutritional row ≈0 precontact** (3–13% only *post*-contact, from parental incapacitation). Disease ≈45%
of all Hiwi deaths vs ≈24% Aché (Aché more warfare-dominated).

**Implications for the model (T-4):** (a) the nutrition→mortality channel is **disease-potentiation**
(synergy multiplies the *disease* portion of `a2`, the Pelletier 2009 malnutrition×infection mechanism),
NOT starvation; calibrate child *disease* mortality to ~16–21/1000 (mid-child) and child *starvation* to
≈0 (child-priority high). (b) It matters mainly for **unweaned infants** (the η≈0 dependent class); weaned
children are robust as η closes the deficit — emergent, not imposed. (c) **Infanticide** is the dominant
*infant* cause and is condition-dependent (short IBI / orphan / no support) → a non-disease infant channel
keyed to state we already track; worth wiring this stage. (d) **External warfare** (≈60% of violent deaths,
older ages) is the inter-group conflict subsystem — deferred to the C-vs-Si conflict phase. PDFs filed in
`literature/`.

---

## Terrain / Climate methodology

### §4.3.1 CC-1 cell capacity — NPP → density [FITTED 2026-07-02; provisional form kept selectable]
`K = density(NPP)·100 km²`, `E = K·burn`; `density` has two modes on `NPPCapacityField(…, mode=…)`:
- **`mode='linear'` [PROVISIONAL, default for back-compat]** — `density = min(0.5, 0.3·npp_gm2/1360)` people/km²;
  a linear density–NPP relation anchored to the ethnographic ~0.1–0.5/km² band, capped 0.5, slope 0.3 so
  density(1360)=0.3; `npp_gm2 = npp·3400`. Over-generous at low NPP (where ~97% of our cells sit).
- **`mode='tallavaara'` [FITTED 2026-07-02, CC-1]** — the actual Tallavaara 2018 (PNAS) segmented regression,
  `ln(density) = −0.1352714 + 0.0028623·NPP_gm2 − 0.0030745·(NPP_gm2 − 1371.664)₊` (density in #/100 km² =
  persons/cell; hump-shaped, peaking near the 1372 g/m²/yr breakpoint). **Extraction:** coefficients read from the
  Tallavaara data-analyses SI (`TALL_INT/TALL_B1/TALL_U1/TALL_BP` in `capacity.py::density_tallavaara`) and
  cross-checked against Dataset_4 (357 HG groups, median density 11.9/100 km²). **Impact:** ~57% of the linear
  patch capacity → eq_pop ~40% lower — a **correctness** gain (Tallavaara ~0.05/km² at NPP 633 matches the record).
  See LITERATURE.md (Tallavaara) and R-36.

**Library home (2026-06-29):** the field is `sic_games/capacity.py: NPPCapacityField(fields, burn, patch=None,
mode='linear')` (`E = density·100·burn`; optional patch mask bounds K so the population equilibrates). It is the
substrate the demographic + emergent-bands + morph validations run on (R-18/19, E.3-proper §4.8.5, the morph
§4.5.11) — **not** the bare `forage_kcal` field (§4.8.4). (The validated R-18/19 harnesses still carry their own
inline copy, `SubWindowCapacity`, numerically identical to the linear mode.) **World-lottery (2026-07-02):**
`terrain.py::world_lottery(seed, archetype=None)` draws per-world knob sets cycling the archetypes
forest/savanna/desert/montane/mixed (`WORLD_ARCHETYPES`, NPP ~175→856) so CC-1 is characterized across a
productivity range; NB the archetype set is arid-biased (median NPP ~500 vs forager-median ~900).

### §4.3.2 Climate seam — temperature & humidity [PLACEHOLDER; SUPERSEDED under mode="climate" by §4.3.4]
**NB (2026-07-04):** under `generate_world(…, mode="climate")` the temperature field is a real annual mean
(latitude − elevation lapse + maritime) with a seasonal amplitude — see the EFC C1 methods, **§4.3.4**. The
placeholder below is the LEGACY-mode value (and `humidity` stays the constant placeholder in both modes).
`temperature=14.0 °C`, `humidity=0.70`, **homogeneous (constant)**. **Source:** global mean surface air
temperature ~14 °C; near-surface relative humidity land-ish ~70%. PLACEHOLDER seam
(`terrain.py: MEAN_GLOBAL_TEMP_C, MEAN_REL_HUMIDITY`); the spatial/seasonal **solar-forced** field is the
deferred climate-season stage (`DEFERRED_MECHANICS` CL-1; Berger 1978 / ENSO / Holocene). Exists so the
Step-2 **pathogen field** reads real T/humidity rather than a `wateracc × NPP` proxy.

### §4.3.3 Step-2 `a2`-modulator anchors (2026-06-19)
- **Nutrition × disease synergy `μ_max`:** undernutrition **multiplicatively** potentiates mortality
  (not additive) — **Pelletier 1994** (*Nutrition Reviews* 52(12):409–415); Scrimshaw et al. 1968.
  Mild-to-moderate malnutrition ≈ **2× mortality risk**, severe higher. **Value: `μ_max ≈ 2–3`** (the
  multiplier on `a2` rising from 1 at full reserve to `μ_max` near the floor). **[PROVISIONAL — Pelletier
  1994 NOT yet in `literature/` (paywalled; supervisor to fetch); the RR is child-mortality data
  extrapolated to adult reserve depletion; confirm the RR-by-severity table.]**
- **Terrain risk scale `R`:** accidents ≈ **10% of all HG deaths** — **Hill, Hurtado & Walker 2007**
  (*J. Hum. Evol.* 52:443–454, Hiwi: accidental ~297/100k person-yr; FILED `literature/`), corroborated
  by Gurven & Kaplan 2007 cause-of-death. **Calibration:** set the (max-capped) risk multiplier so
  terrain accident-mortality ≈ **10% of baseline `a2`** in average-risk terrain, scaling with the `risk`
  field. Pins the risk *scale*, not just the mean (red-team M-2).
- **Density-disease `D` (`δ, ρ_half`):** the **free calibration lever** (endemic/zoonotic transmission;
  Dunn 1968 / Houldcroft & Underdown 2023 — modest, not crowd-epidemic). No external anchor — calibrated
  to the spatial equilibrium. `ρ` defined as **agents/km²** (red-team m-3), not raw cell occupancy.
- **Pathogen field `P` (`π, NPP_half`): DEFERRED — OFF in 2b.** Tallavaara's standardized SEM
  coefficients live in **Fig. 3 (PDF p3) + Table S1 (SI)** — a figure + an SI table (the SI is NOT in the
  filed 6-page main-text PDF, and figure arrow-labels are not text-extractable). Rather than force the SEM
  onto the `wateracc × NPP` proxy (dimensionally questionable — red-team M-2), the pathogen field is
  anchored to **real temperature/humidity** (Guernier 2004 climate drivers) when the **climate-season
  stage** lands (DEFERRED_MECHANICS CL-1; §4.3.2). 2b runs with pathogen OFF.

**Implementation note (synergy read; 2026-06-19).** The synergy (and energetic-fertility) modulator reads
the **post-harvest** reserve (`_fed_reserve`, the nutritional state), NOT the post-burn value — which is
`reserve_full − burn` for *any* fed agent and falsely reads as starvation (this was the 2b/2c artifact;
RESULTS R-5). `reserve_full = 100k` is ~physiologically right (~1.3–1.5 months of fat); the bug was the
read timing, not the magnitude. **On the current constant/undepletable economy all three modulators are
INERT** (agents fully fed + spread) — they need nutritional *variance* (Resource-Ecology stage:
seasonality + depletion) to act, so `μ_max` is not calibratable until then.

---

## Economy-from-Climate (EFC) — first-principles food yield from climate (added 2026-07-04; RESULTS R-49/R-50/R-51)

**Status: BUILT as an OPT-IN world-generation MODE.** `generate_world(knobs, mode="legacy"|"climate")` in
`terrain.py`; **legacy is the DEFAULT and bit-exact** (a pure migration toggle — R-2…R-48 stay valid until EFC
is validated and cut over). Blueprints: `…_ClimateEconomy_Scoping.md` (the umbrella; subsumes
`…_BiomeClimate_AquaticFood_Scoping.md`). This is the deep first-principles substrate that makes the food
economy EMERGE from climate rather than being a fractal-noise moisture field × terrain penalties with biome as
a label (the pre-EFC substrate; §4.3.2 was the placeholder). The chain is C1 temperature → C2 precipitation →
C3 Miami NPP → C4 Whittaker biome → C6 river-source temperature → C7 aquatic-food → C8 aquatic capacity
subsidy. All EFC fields are 0 in legacy mode. This section is the METHODS home for every EFC lit-derived value;
the pipeline narrative is MECHANISMS §9b; the constants table is PARAMETERS §19; findings are RESULTS
R-49/R-50/R-51. **All EFC science constants are PROVISIONAL (pending supervisor sign-off + per-step sweeps).**

**Grid geometry (shared by legacy + climate).** `N=100` cells, `CELL_EDGE_M=10000` (10 km × 10 km = 100 km²/
cell), so the grid is 1000 × 1000 km. At ~111 km/degree that N–S extent is a **~9° swath** (`GRID_SPAN_DEG=9.0`),
which is why the WITHIN-GRID latitudinal temperature gradient is MODEST — the big spatial variability is
elevation (lapse) + rain-shadow + coast, so a mountainous coastal region legitimately holds 4–6 biomes.

### §4.3.4 C1 — temperature field (`terrain.py`, `mode="climate"`)
**Annual-mean T** `= regional-latitude base − elevation lapse`, with a per-cell seasonal HALF-amplitude
`temp_seas_amp` (the monthly wave `T̄ ± amp·cos(2π·month/12)` is applied by the climate layer; in legacy mode
`temperature` is the latitudinal placeholder and `temp_seas_amp=0`).
- **Regional latitude.** The world sits at `climate_latitude ∈ [0,1]` (knob; 0 = equator, 1 = subpolar edge,
  `CLIMATE_FULL_LAT_DEG=65°`; default `CLIMATE_LATITUDE_DEFAULT=0.5`). Each cell's ABSOLUTE latitude fraction
  is `climate_latitude + REGIONAL_SPAN_FRAC·(lat_frac − 0.5)`, where `REGIONAL_SPAN_FRAC = GRID_SPAN_DEG /
  CLIMATE_FULL_LAT_DEG ≈ 0.14` — so only ~14% of the full equator→subpolar span is traversed within one grid.
  The base T at that cell-latitude interpolates the same endpoints the C.4a placeholder uses: `TEMP_EQUATOR_C
  = 27 °C` (equator) → `TEMP_HIGHLAT_C = 1 °C` (subpolar), 14 °C area-mean by construction.
- **Elevation lapse.** `− LAPSE_C_PER_KM·(elev·reliefAmpM)/1000`, `LAPSE_C_PER_KM = 6.5 °C/km` — the standard
  **environmental lapse rate** (montane cooling). Anchor: standard atmospheric physics (6.5 °C/km is the ICAO/
  environmental mean). This fixes the pre-EFC savanna-cold/montane-warm inversion (a montane cell at ~1550 m
  reads 14 → ~3.9 °C, not warm). Elevation enters climate-NPP only through T (no separate elev penalty).
- **Seasonal amplitude.** `temp_seas_amp = TEMP_SEAS_AMP_MAX·cell_lat·(1 − MARITIME_DAMP·wateracc)`,
  `TEMP_SEAS_AMP_MAX = 15 °C` (max half-amplitude ⇒ ~30 °C annual range at a high-latitude CONTINENTAL interior,
  cf. continental temperate/boreal interiors), `MARITIME_DAMP = 0.6` (maritime moderation: near-water cells DAMP
  the swing — oceans buffer the annual cycle). Amplitude ∝ absolute latitude (tropics aseasonal, high-lat
  strongly seasonal). PROVISIONAL.

### §4.3.5 C2 — structured annual precipitation (mm/yr)
`precip_mm` = Hadley/ITCZ latitude bands × orographic (uplift × multi-cell rain-shadow) × maritime × noise ×
continental aridity × polar-dry. Ranges tuned so the latitudinal profile lands in Earth-like biome bins
(R-49 realized: equator ~2865 mm rainforest, subtropical ~30° ~340 mm desert, mid-lat ~1489 mm temperate
forest, subpolar ~501 mm). All constants PROVISIONAL.
- **Latitude bands (the regional air-moisture supply).** `p_band = (P_BASE_MM + itcz + midlat)·polar_dry·
  aridity`, with `P_BASE_MM = 250` (dry background — subtropical/polar desert floor), an equatorial ITCZ
  Gaussian `itcz = P_ITCZ_MM·exp(−(cell_lat/P_ITCZ_WIDTH)²)` (`P_ITCZ_MM = 2400`, `P_ITCZ_WIDTH = 0.15`), and a
  mid-latitude storm-track Gaussian `midlat = P_MIDLAT_MM·exp(−((cell_lat − P_MIDLAT_CENTER)/P_MIDLAT_WIDTH)²)`
  (`P_MIDLAT_MM = 1100`, `P_MIDLAT_CENTER = 0.70` ≈ 50° on the span, `P_MIDLAT_WIDTH = 0.18`). Anchor: the
  Hadley-cell / ITCZ general-circulation pattern (equatorial ascent wet, ~30° subsidence dry, mid-lat storm
  track wet).
- **Polar dryness.** `polar_dry = 1 − POLAR_DRY_GAIN·clip((cell_lat − POLAR_DRY_ONSET)/(1 − POLAR_DRY_ONSET),
  0,1)`, `POLAR_DRY_ONSET = 0.72`, `POLAR_DRY_GAIN = 0.55` — descending dry polar air past the storm track.
- **Continental aridity.** `aridity = 1 − CLIMATE_ARIDITY_DAMP·climate_aridity`, `CLIMATE_ARIDITY_DAMP = 0.75`
  — the `climate_aridity ∈ [0,1]` knob scales precip DOWN by up to 75% (continental/leeward dryness independent
  of latitude, e.g. a temperate-but-arid interior; the axis that lets a subtropical world be a genuine Sahara).
- **Orographic uplift (moisture-limited).** `uplift = 1 + P_ELEV_UPLIFT·elev·moist_avail`, `P_ELEV_UPLIFT =
  1.6` (elev=1 ⇒ ×2.6 at full moisture). Uplift is MOISTURE-LIMITED: `moist_avail = clip(p_band/P_MOISTURE_REF_MM,
  P_UPLIFT_MIN_AVAIL, 1)`, `P_MOISTURE_REF_MM = 1500` (base precip at which uplift is full), `P_UPLIFT_MIN_AVAIL
  = 0.12` (dry air still gives a little orographic rain) — a mountain can only wring out the moisture the air
  carries, so dry subtropical highlands stay arid.
- **Multi-cell rain-shadow.** Prevailing wind = +x (westerlies, `P_ORO_WIND_DX = 1`; upwind is −x). The max
  upwind elevation is taken over `P_ORO_SHADOW_CELLS = 6` cells (~60 km reach); `shadow = clip(1 −
  P_ORO_SHADOW_GAIN·max(0, upwind_max − elev), P_ORO_MIN, 1)`, `P_ORO_SHADOW_GAIN = 1.6`. The combined
  orographic multiplier `oro = clip(uplift·shadow, P_ORO_MIN, P_ORO_MAX)`, `P_ORO_MIN = 0.25` (deep lee),
  `P_ORO_MAX = 3.2` (windward/peak enhancement). Anchor: e.g. Cascades → high desert (a big range dries tens of
  km to its lee).
- **Maritime + noise.** `precip_mm = clip(p_band·oro·(1 + P_MARITIME_GAIN·wateracc)·(0.7 + 0.6·moist), 0, None)`,
  `P_MARITIME_GAIN = 0.3` (near-water moisture supply); `moist` is the legacy fractal moisture-noise field
  (texture). Water cells → 0.

### §4.3.6 C3 — the MIAMI model: NPP from temperature & precipitation [VERIFIED]
`NPP = min(NPP_T, NPP_P)` g dry-matter/m²/yr — cold OR dry both cap productivity (Liebig-style minimum). Source:
**Lieth 1972/1975** (the Miami model), the published least-squares fit to ~50 sites across 5 continents. The
primary PDF is filed (`literature/Lieth - 1975 …pdf`); the two limbs are **eqs 12-1 / 12-2, VERIFIED against
the primary PDF** (LITERATURE.md).
```
NPP_T = MIAMI_MAX / (1 + exp(MIAMI_T_A − MIAMI_T_B·T))          T in °C
NPP_P = MIAMI_MAX · (1 − exp(−MIAMI_P_C·P))                     P in mm/yr
NPP   = min(NPP_T, NPP_P)
```
Constants (the published coefficients, used exactly — no re-fit): `MIAMI_MAX = 3000` (asymptotic ceiling of
both limbs, g/m²/yr), `MIAMI_T_A = 1.315`, `MIAMI_T_B = 0.119` (temperature limb), `MIAMI_P_C = 0.000664`
(precipitation limb). Helper `miami_npp(T, P)` (vectorized). **Sanity (R-49):** −5 °C/2000 mm → 387; 28 °C/150 mm
→ 284; 28 °C/2500 mm → 2430; 15 °C/1200 mm → 1648 (matches the published Miami surface). Under `mode="climate"`
NPP is stored normalized: `npp = min(3000, Miami(T,P))/NPP_GM2_SCALE` with `NPP_GM2_SCALE = 3400` (§4.3.1), so
the downstream `npp_gm2 = npp·3400` recovers the real Miami g/m²/yr (Miami ≤ 3000 < 3400 ⇒ npp ≤ 0.88) and feeds
the Tallavaara capacity (§4.3.1) — a coherent real-NPP pairing. NPP is now temperature-limited (cold → tundra)
AND precipitation-limited (dry → desert).

### §4.3.7 C4 — the WHITTAKER biome (biome as a climate OUTCOME)
`whittaker_biome(T, P)` maps annual mean T (°C) × annual P (mm/yr) onto the model's coarse codes — biome
EMERGES from climate rather than being a moisture label. Thresholds RISE with temperature (evapotranspiration:
warmer needs more rain for the same class):
- `desert_thr = WHIT_DESERT_BASE + WHIT_DESERT_SLOPE·max(T,0)`, `WHIT_DESERT_BASE = 200`, `WHIT_DESERT_SLOPE =
  15`. `P < desert_thr` → DESERT.
- `forest_thr = WHIT_FOREST_BASE + WHIT_FOREST_SLOPE·max(T,0)`, `WHIT_FOREST_BASE = 500`, `WHIT_FOREST_SLOPE =
  35`. `P ≥ forest_thr` → FOREST; the intermediate band (`desert_thr ≤ P < forest_thr`) is SAVANNA if warm
  (`T ≥ GRASS_TROPICAL_THRESHOLD_C = 18 °C`, the Köppen tropical-A isotherm) else GRASS (cool grassland-steppe).
- **Cold cap (tundra/taiga):** a would-be FOREST below `WHIT_TUNDRA_T = −5 °C` becomes GRASS (too cold for
  trees → tundra); cold+dry stays DESERT; cold+wet stays FOREST (taiga). Terrain overrides MOUNTAIN / WETLAND /
  WATER apply on top (WETLAND = low-slope near-water high-NPP cells; MOUNTAIN = the joint elev×slope condition;
  §4.3.1 biome ladder). Anchor: the Whittaker biome climate-diagram (T×P → biome). Thresholds PROVISIONAL.

**Terrain × climate world lottery.** `world_lottery_climate(seed, terrain, climate)` draws INDEPENDENT
`TERRAIN_PRESETS` (flat / hilly / mountainous / coastal — relief + water knobs) × `CLIMATE_PRESETS` (tropical /
subtropical / temperate / boreal — `climate_latitude` + `climate_aridity` bands), cycling both on co-prime
periods (4 × 4 = 16 pairings over seeds 0–15); the legacy moisture knobs `forestK`/`aridK` are neutralised
(climate, not a knob, sets moisture). Any pairing is legal (tropical-lowland → rainforest; subtropical-flat-arid
→ Sahara; temperate-montane → Rockies; boreal-flat → taiga). Emergent worlds validated + visualized in R-50.

### §4.3.8 C6 — river-source (water) temperature by flow-routing
A river carries the cold of its montane HEADWATER (snowmelt), not the local air — so a valley river can be cold
where the air is warm (the salmon-fishery enabler). The D8 flow routing propagates the max upstream (headwater)
elevation `src_elev` downstream; then `water_temp = air_T − RIVER_COLD_RETENTION·LAPSE_C_PER_KM·(src_elev −
elev)·reliefAmpM/1000`, `RIVER_COLD_RETENTION = 0.6` (fraction of the headwater-elevation cooling a river
retains by the time it reaches a cell). 0 in legacy mode. Anchor (LITERATURE.md): river temperature set by
source — snowmelt/montane headwaters cold, lowland/pluvial warm. RT-B (the crux): agents live in warm valleys,
not cold peaks, so local-air lapse does NOT cool occupied cells — the salmon signal REQUIRES the river to carry
cold water down. `RIVER_COLD_RETENTION` PROVISIONAL.

### §4.3.9 C7 — aquatic-food field ∈ [0,1] (`aquatic_food_field`)
The dense STORABLE aquatic resource that underwrites forager complexity (Testart/Ames). On land cells (0 on
open water) it is `max(anadromous, shellfish)`:
- **Anadromous limb (salmon).** `coldness = clip((SALMON_T_LETHAL − water_temp)/(SALMON_T_LETHAL −
  SALMON_T_OPT), 0, 1)`, `SALMON_T_OPT = 16 °C` (coldness FULL at/below), `SALMON_T_LETHAL = 21 °C` (coldness 0
  at/above). `river_cold = coldness · isRiver · sea_conn`, where `sea_conn = 1` if the cell drains to the sea
  else `AQUATIC_SEA_CONN_FLOOR = 0.25` (endorheic rivers get some lacustrine fish). `drains_to_sea` is
  propagated upstream from open water along the flow routing. The river fishery is spread to the 4-neighbour
  BANK cells (max) — foragers harvest from the bank. Anchor (LITERATURE.md): salmonid thermal tolerance (opt
  ~16 °C, lethal ~21 °C).
- **Shellfish limb.** `shellfish = is_shore · SHELLFISH_RICHNESS · (0.5 + 0.5·npp01)`, `SHELLFISH_RICHNESS =
  0.7` (coastal littoral level; Bird 1997 reef/intertidal richness), productivity-scaled by normalized NPP.
  Warm-tolerant (coastal, unlike the cold-water salmon limb).

0 in legacy mode. Constants PROVISIONAL.

### §4.3.10 C8 — aquatic capacity subsidy (`capacity.py: NPPCapacityField(aquatic=True)`)
A dense storable aquatic resource subsidises carrying capacity ABOVE the terrestrial Tallavaara ceiling —
coastal complex foragers reached ~8–10× typical forager density (NW Coast). `ppl_per_cell += AQUATIC_DENSITY_MAX·
aquatic_food`, `AQUATIC_DENSITY_MAX = 80.0` (persons/cell added by a full `aquatic_food=1` cell — ~8× the
Tallavaara median ~12). Opt-in: interior (`aquatic_food=0`) or `aquatic=False` ⇒ identical to the base field
(inland equilibria bit-exact). This is the super-density that lets a concentrated band cross Binford packing —
the substrate for stratification. Anchor: Ames 1994 (NW-Coast affluent foragers). PROVISIONAL. **GATE-3
finding (R-51):** the subsidy ALONE does NOT concentrate bands — IFD movement disperses; concentration needs
circumscription/saturation (GD-1 was built to test whether depletion supplies it — it does not either; the
population is demographically, not resource, limited).

### §4.3.11 GD-1 — finite resources: the depletable stock (`capacity.py`; RESULTS R-51)
Testart's delayed-return substrate: a cell is a depletable STOCK, not an infinite standing flow.
`NPPCapacityField(…, enable_depletion=True)` holds `B ∈ [B_FLOOR, 1]` per cell (fraction of the cell's ceiling
flow `base_E = K·burn`); the effective yield is `E = base_E·B`. Each step,
```
deplete_and_regrow(occ_count, season):
    pressure = occ / K_persons                              # foragers per unit capacity
    B += r_step · season · ((1 − B) − DEPLETE_FRAC · pressure)
    B = clip(B, B_FLOOR, 1)
    E = base_E · B
```
so a lightly-used cell stays full; sustained/over-use hunts it out (equilibrium `B ≈ 1 − DEPLETE_FRAC·pressure`);
it recovers logistically at the biome rate. `r_step = r_yr/12` (1 step = 1 month). Constants:
- **`DEPLETE_FRAC = 0.5`** — depletion strength: at foraging pressure = 1 (occ = capacity) B equilibrates at
  ~1−0.5. PROVISIONAL.
- **`B_FLOOR = 0.05`** — a hunted-out cell never quite hits zero (refugia / trickle).
- **Biome-specific logistic regrowth `R_BIOME_PER_YR`** (per year; `{water 0.0, wetland 0.40, forest 0.15,
  savanna 0.60, grass 0.70, desert 0.15, mountain 0.20}`) — grassland/savanna fast, forest/desert slow.
  **`AQUATIC_R_PER_YR = 0.80`** (a fast annual restock of a salmon/shellfish catchment — the sedentism enabler;
  applied as `r = max(r_biome, 0.80·aquatic_food)`). Anchor (LITERATURE.md): **Coe 1976** (game/resource stock
  K ∝ rainfall/NPP), **Cortés 2016** (intrinsic rate of increase `r_max` by taxon — grassland ungulates high,
  forest/desert slow-breeders low; salmonids fast), central-place depletion halos. r/yr values PROVISIONAL
  (sweep + sign-off pending).

**Hook** (`phase1_model.py::_step_rivalrous`, end of step): `if hasattr(tf, "deplete_and_regrow"): season =
tf.season() if hasattr(tf,"season") else 1.0; tf.deplete_and_regrow(occ_count, season)`. Default OFF ⇒
non-depleting standing flow (bit-exact; full suite 660). **Finding (R-51):** GD-1 built + viable (deplete/
recover validated; eq_pop stays viable ON), but emergent sedentism did NOT fire — the population equilibrates
at ~320 against a patch ceiling of ~71,246 (land 0.4% filled), so it is DEMOGRAPHICALLY limited, not
resource/space limited → IFD always has empty high-per-capita cells to disperse into → no circumscription →
Carneiro 1970 circumscription/saturation is the missing keystone. This is why the DEFERRED_MECHANICS GD-1 entry
(originally scoped as GAME depletion of `game_kcal`) is realized here as GENERAL resource depletion of the NPP
capacity stock.

**Catchment-foraging pressure (`enable_catchment_depletion`; added 2026-09-02, R-106; RESULTS Addendum 57).**
The hook above keys on `occ_count` — where an agent STANDS. A settled village forages its whole catchment
(tier-2, pooled) yet stands on the site cell, so a foraged-but-unoccupied catchment cell never depletes. When
on, `_catchment_foraging_pressure` replaces `occ_count` with a FORAGING map: each settled villager's unit is
spread over its catchment ∝ each cell's yield (Σ conserved = population); a mobile band forages the cell it
stands on. So the catchment depletes ∝ how hard it is foraged, and its carrying-capacity ceiling falls with it.
A/B (4 seeds) is baseline-dependent: it drops median village size but its net demographic effect is a wash
with tail risk (one −39% seed = the ceiling biting an over-hunted catchment) — it corrects the resource economy without a large behavioural swing, because the
adopted `village_identity` / `bud_requires_occupancy` fixes already tamed the peak crowding. It confirms
catchment inexhaustibility is NOT the over-clustering engine; the point-mode agglomeration return (β=1.15)
is. Default OFF ⇒ pressure = standing occupancy ⇒ bit-exact; adopted ON in canonical.

---

## Resource-Ecology economy methods (added 2026-06-20; RESULTS R-6…R-8)

The economy layer added to give the demographic modulators nutritional *variance*. Harnesses
`outputs/phase1_resource_ecology/run_2d…2f`. **Headline (R-6/7/8):** all three are NEGATIVE — none makes
the graded modulators bite at equilibrium, because the density-regulated population self-organises to
"broadly fed at the biome carrying capacity." Each only moves the *carrying capacity*.

### §4.3.12 THE RESOURCE DISTRIBUTIONS — how concentrated each stream is, and what is anchored

**WHY THIS SECTION EXISTS.** Every resource field's RETURN RATE is anchored (§4.1.5, §4.3.6, the Game
Return-Rate Table). Until 2026-08-15 the **DISTRIBUTION** — how unevenly that return is spread across a
landscape, and what fraction of cells qualify as a good site — was documented nowhere, even though it decides
how rare a village is, how much reason a band has to move, and how much of the intake variance is
environmental rather than social. It is the difference between "a forager gets 5,541 kcal/hr in forest"
(anchored) and "1 cell in 20 is worth settling" (was not).

**MEASURED, coastal-temperate, 1584 habitable cells, `world_seed=0`** (2026-08-15):

| field | Gini | CV | p90/p50 | lag-1 spatial r |
|---|---|---|---|---|
| `aquatic_food` | **0.817** | 2.21 | ∞ (median 0) | +0.80 |
| `cultivability` | **0.502** | 0.94 | 4.5 | +0.90 |
| `game_kcal` | 0.305 | 0.74 | 3.0 | +0.94 |
| `forage_kcal` | 0.220 | 0.46 | 2.3 | +0.93 |
| `forage` (normalised) | 0.111 | 0.20 | 1.3 | +0.98 |
| `npp` | 0.100 | 0.17 | 1.2 | +0.99 |

**THE VARIATION IS PATCHY, NOT NOISY.** Lag-1 spatial autocorrelation runs +0.80 to +0.99 on every field, so
good cells form regions rather than scattered pixels. A white-noise landscape would give nonsense IFD
movement — a band would have no gradient to climb and no reason to persist anywhere.

**THE ORDERING IS RIGHT AND WAS NOT IMPOSED.** aquatic ≫ cultivable > game > forage. Fisheries most
concentrated (median ZERO, Gini 0.82 — the salmon-run choke-point structure, §4.3.9), plant gathering flattest.
That is the ethnographic pattern: gathering is the reliable, spatially uniform fallback, which is why foragers
rely on it. It emerges from the field constructions rather than from a distributional parameter.

**WHAT IS ANCHORED, AND WHAT IS A TERRAIN-GENERATOR ARTEFACT — read this before tuning anything.**

- **ANCHORED — the return rates.** Hill 1987 (forest 5,541 kcal/hr), Hurtado & Hill 1987 (grassland 3,001),
  Hawkes et al. 1991 (encounter 518 / intercept 745 kcal/hr), Bird 1997 (intertidal); Lieth 1973 Miami NPP;
  Tallavaara 2018 NPP→density. All `[VERIFIED]`, see LITERATURE.md.
- **ANCHORED — the storabilities.** `STORABILITY_BY_RESOURCE` grain 0.85 / fish 0.80 / forage 0.15 / game
  0.35, Testart 1982 (§4.5.10). This is what makes grain-and-fish cells the sedentism-capable ones.
- **PARTIALLY ANCHORED — the aquatic pass fraction.** Measured 5.9% temperate / 3.5% boreal / 4.2% tropical
  of habitable land. Derived target **4–8% temperate and boreal**: Testart 1982:529 records **10 of 40** HG
  societies as storing (25% **by society count**), and Cunningham 2020 gives **7 of 36** SCCS foragers at
  medium/high density, **6 of them** fished. **DENOMINATOR CORRECTION (load-bearing):** storing societies sit
  at Testart's density codes C–D (>1.1 persons/sq mi) against A–B (<1) for the rest, so they hold 5–25× LESS
  LAND per society. Converting a society count to a land fraction divides by roughly three: **25% of
  societies ≈ 5–14% of land.** Temperate and boreal are therefore DEFENSIBLE AS THEY STAND. **Tropical at
  4.2% is TOO HIGH — target 0.5–2%**, and the reason is Binford's ET = 15.25 storage threshold suppressing
  storage in the tropics, not fishery productivity. Testart's 40-society sample contains NO tropical storer.
- **NOT ANCHORED, AND WRONG — the cultivable pass fraction.** Measured **39.6% temperate / 28.1% tropical**.
  FAO global arable is **10.9% of FAO land area**, and FAO land area (13.0 Bha, excluding inland water and
  Antarctica) is NOT the model's denominator; against HABITABLE land (~10.4 Bha) arable is **~13.5%**. That
  is a **CEILING, not a target** — it is the product of the plough, irrigation, drainage and fertiliser, so
  early rain-fed pre-plough agriculture must fall strictly below it. **The model exceeds the modern
  industrial ceiling by a factor of ~3.** Bar-Yosef gives the qualitative bound: the earliest Levantine
  farming communities sat on a LINE, "along today's boundary between the Mediterranean and the
  Irano-Turanian steppic vegetational belts" — a one-dimensional feature in a two-dimensional landscape.
  Provisional target **5–12% temperate / 3–10% tropical / 0–2% boreal**, all LOW CONFIDENCE, to be swept.
- **UNANCHORED — everything else in the table.** The Ginis and autocorrelations above are MEASUREMENTS of
  what the generator produces, not calibrations against a source. No literature was found reporting a
  landscape-wide concentration statistic for forager resources. Treat them as a baseline to detect drift
  against, NOT as validated values.

**`cultivability` IS NEARLY BIMODAL** — median 0.219 but p90 0.995, with 20.8% of land ≥ 0.6. It is
mostly-bad-or-excellent rather than a gradient, so `settle_persist_threshold` JUMPS rather than glides. If a
target fraction of ~10% is wanted against a measured 39.6%, the honest instrument is the field's GENERATION,
not the threshold.

**THE VARIANCE AGENTS ACTUALLY EXPERIENCE IS SOCIAL, NOT ENVIRONMENTAL.** Realised per-agent intake spans p10
1.36 / p50 2.64 / p90 9.30 — about 7×, far wider than any single resource field. The excess comes from
rivalrous harvest (`S/n`, §4.5) and the agglomeration exponent (`aggl_beta` = 1.15, §4.8.21), not from the
land. Any diagnosis of starvation, of the energetic fertility brake, or of the age structure must start
there; the landscape statistics above are not the cause. See RESULTS Addenda 42–45.

### §4.4.1 Seasonality (A.1) — `s(t)` harvest multiplier
Uniform annual cosine `s(t) = s_min + (1−s_min)·½(1+cos(2π·t/12))`, period 12 steps = 1 yr. **`s_min`
PROVISIONAL** (no lit anchor yet; tied to the deferred climate-season stage CL-1 / Berger insolation). On
`level = E·s(t)`. **Established:** regulates the demographic CC down to the **lean-season bottleneck**
(Liebig's law of the minimum; 95%→37% of peak food ceiling at s_min=0.4) but agents self-adjust and stay
fed year-round (reserves ~full, synergy ~1) — **inert on its own**.

### §4.4.2 Depletion (A.2, early freshness `f`) — SUPERSEDED by the GD-1 stock (§4.3.11) [PROVISIONAL]
**NB (2026-07-04):** this is the EARLY Resource-Ecology `consume()`/freshness mechanic (R-7). The canonical
finite-resource substrate is now the GD-1 depletable STOCK `B` in `capacity.py` (biome/season/aquatic-specific
logistic regrowth; §4.3.11, RESULTS R-51); this freshness field is the phenomenological predecessor.
Each cell carries `f ∈ [0.05, 1]` (fraction of standing stock); `level = E·f·s(t)`. After harvest,
`consume(occ_count)`: occupied cells `f −= deplete_rate·min(1, occ/K)`; all cells regrow
`f += regrow_rate·(1−f)`. **Values `deplete_rate=0.30`, `regrow_rate=0.10` are PROVISIONAL — phenomenological,
NOT lit-anchored** (a mechanistic biomass/logistic-regrowth model with prey/tuber population dynamics is the
proper version, deferred). Opt-in: the model calls `tf.consume()` only if the field exposes it (`hasattr`
guard) → no-op for non-depletable fields, 444-suite unchanged. **Established:** lowers the CC further
(to ~26% peak; cells stripped to f≈0.32) but **0% under-fed** — the ideal-free-distribution movement washes
out per-agent variance.

### §4.4.3 Movement / `move_cost_flat` (B) — a mobility knob, not a variance source
`move_cost_flat` is a **decision friction** subtracted from cell utility (`ypc − move_cost`), **NOT a wealth
debit** — it changes the chosen cell without burning kcal (so it adds stickiness without re-lowering the
mean). **Established:** clean monotone mobility control (residential moves/yr 0.93→0.15 as cost 0→0.35·burn)
but **0% under-fed at every level, occupancy CV invariant** → spatial trapping RULED OUT as the variance
source. **Incidental realism finding:** the model is *under*-mobile (0.93 moves/yr vs Binford 2001 forager
envelope ~10–40/yr) — the lit-realistic setting is **`move_cost ≈ 0`** (the baseline); restoring HG mobility
is a resource-tracking realism issue, separate from mortality. **Diagnosis (R-8):** the limiter is the
near-**bang-bang reserve** (fed-at-cap or culled-in-~1-step; no stable "lean but alive" band) — the needed
variance is **structural (dependency), not spatial**.

---

## Life-history & provisioning methods (Phase C; added 2026-06-20; RESULTS R-9/R-10)

Introduces the **dependent class** (children who can't self-feed) — the only structure the
ideal-free-distribution can't wash out. All opt-in via `lh_cfg`/`enable_provisioning`; 444-suite green
throughout. `LifeHistoryConfig`, `agents/base.py: eta()/consumption_factor()/reserve_scale()`,
`phase1_model.py` harvest+metabolism+births.

### §4.5.1 Graded production η(age) (C.1) — the Kaplan childhood deficit
Own intake `= η(age)·harvest_share`. `η` is the existing piecewise-linear ramp: `eta_min` at birth → 1.0 at
`forage_age_min`, elder decline to `eta_old`. **`forage_age_min = 180 mo (15 yr)`, `eta_min = 0`** (newborn
produces nothing). **Source:** Kaplan, Hill, Lancaster & Hurtado 2000 (net-production-by-age; children
net-positive ~18–20 yr). **The LINEAR ramp is the JV-1 approximation** — overstates older-child production;
the convex Kaplan curve is **deferred**. Replaces the old **binary** juvenile gate (`intake=0` below age).

### §4.5.2 Age-scaled consumption c(age) (C.1)
`burn = burn_adult · c(age)`; `c` ramps `cons_min → 1.0` over `[0, forage_age_min]`. **`cons_min = 0.3`**
(neonate maintenance ~30% of adult absolute). **Source:** Kaplan 2000 / FAO requirement-by-age. The net
deficit `c(age) − η(age)·share` is positive through early childhood (consumption rises faster than
production) — the transfer the band must fund.

### §4.5.3 Per-class reserves `reserve_scale(age)` (C.2a) — body-sized neonatal reserve
Scales the energy reserve (= starvation **floor** AND **cap** AND **birth endowment**) by body size:
`reserve_min` at birth → 1.0 at `forage_age_min`. **Source:** Pontzer 2012 (Hadza body composition: ♀24.2%
/♂8.6% fat → ♀~109k/♂~43k kcal — men *below* the 100k constant) + body-mass scaling. **HARD CONSTRAINT
(C.2b finding): `reserve_min` must = `cons_min` (= 0.3)** — a neonate's cap must cover ≥1 step's burn, else
the monthly timestep + once-per-step provisioning make a dependent unsustainable *even when fully
provisioned*. So reserve and consumption scale together (uniform ~1.3-month buffer across ages); the
**deficit comes from η lagging, not from storage**. **Established (R-9):** the deficit only *bites* with a
body-sized neonatal reserve — the old adult-sized 100k masked it (C.1 didn't wall; C.2a → extinction without
provisioning).

### §4.5.4 Provisioning (C.2b) — mother-linked, flow-based
`child._mother` set at IBI birth. A mother's harvest that **overflows her cap** (otherwise wasted) is
**redirected to her dependent children** (age < forage_age_min), filling each toward its cap. **Flow-based**
because adults at the cap have no reserve headroom to give. **Topology — LIT-RESOLVED to mother/kin-linked**
(Gurven 2004; Kaplan & Hill 1985; Hawkes): gathered-*plant* food is shared **within household/close kin**;
band-wide pooling is the **meat** pattern, correct only with the game stream on (deferred). Forage-only =
the plant tier = mother-linked. **Feeding priority (micro):** adults eat to maintenance (own cap) first →
surplus to own children → child draws deficit toward its cap → mother death = orphan (no provisioning).
**Established (R-10):** provisioning *rescues* the dependent class (C.2a extinction → stable ~5000, normal
34% juvenile); on a self-adjusting economy it **over-smooths** (children always fully provisioned); but
**seasonality + provisioning → emergent SEASONAL CHILD MORTALITY** (lean-trough starvation 34/step vs good
0.3 = 68× pulse, on children; adults stay fed). **CAVEAT:** routes through the hard starvation floor, NOT
graded synergy — the bang-bang reserve sends a squeezed child to the floor in ~1 step, too fast to dwell.

### §4.5.5 Game/meat two-stream economy (G.1+G.2; the Carbon substrate; added 2026-06-21)

**Purpose (blueprint v2):** the validated economy is forage-only and **low-variance**, so the Cred-weighted
sharing lever (κ) has almost nothing to act on. **Meat** is the high-variance, **band-shared**, status/
reciprocity resource (Kaplan & Hill 1985; Hawkes 1991; §4.5.4) — the resource where a hierarchical (Carbon)
vs egalitarian (Silicon) sharing rule diverges. This stage splits the cell yield into the two streams so the
Carbon mechanism has a substrate. **Not** a δ/e₀ fix (settled, R-13/R-15/R-16/R-17) and **not** a density fix
(energy is conserved — RT-E); it is the economic substrate for the status hierarchy.

**Mechanism (`phase1_model.py:_step_rivalrous`, opt-in `DemographyConfig.enable_game`/`game_meat_frac`):**
the per-cell yield `S` is split `S_forage = (1−mf)·S`, `S_meat = mf·S`, and distributed by two calls to
`compute_harvest_shares`: **forage at a literal `κ=0`** (household / equal — plant food is not the status
resource) and **meat at the substrate `κ` (`contest_exponent`)** — band-pooled, Cred-weighted `(φ+ε)^κ` for
Carbon agents. Intake `= η(age)·(forage_share + meat_share)`. **Energy-conserving:** at κ=0 the sum is
identical to the single stream (exact back-compat — the inertness gate, `test_game_economy.py`); at κ>0 meat
redistributes toward high-Cred Carbon agents while forage stays equal (RT-B: κ is applied to meat only, never
double-applied to both halves).

**`mf` = `game_meat_frac` = diet animal fraction by biome — Cordain et al. 2000, AJCN 71:682, Table 2**
(mean subsistence dependence by primary living environment, n=63). The model has a forage+game economy with
**no aquatic stream**, so `mf` is the **terrestrial-renormalized** hunted fraction `hunted/(plant+hunted)` at
class-interval midpoints, **fished column dropped** (`terrain.MEAT_FRAC`):

| Model biome | Cordain environment | plant / hunted / fished (%) | `mf` = h/(p+h) |
|---|---|---|---|
| FOREST (Aché) | Subtropical rain forest | 40.5 / 50.5 / 10.5 | **0.55** |
| DESERT (!Kung) | Desert grasses & shrubs | 50.5 / 40.5 / 10.5 | 0.45 |
| SAVANNA (Hadza) | Tropical grassland | 50.5 / 30.5 / 20.5 | 0.38 |
| GRASS (steppe/plains) | Temperate grasslands | 30.5 / 60.5 / 10.5 | 0.66 |

Cordain finding used: hunted-animal dependence is ~latitude-invariant (~26–35%, r=0.08 n.s.); the latitude
gradient is fishing↔plant, not hunting — so the terrestrial `mf` is set by environment, not a latitude law.
**`mf` is a scalar config** (the dwelling biome's value) for the single-biome demographic runs. **The per-cell
wiring exists as of 2026-08-08 (Addendum 37):** `enable_biome_meat_frac` reads `mf` per cell from
`terrain.MEAT_FRAC`, and `enable_biome_meat_cv` reads the G.3 draw's CV per cell from `terrain.MEAT_CV`
(fallback `terrain.HUNT_CV` = 2.11). Both default OFF in the class and ON in `config/mechanisms.toml`. A biome
absent from `MEAT_FRAC` (wetland) keeps the scalar, never 0.0 — the omission is a gap, not a measured zero.

**WHERE THE MEAT COMES FROM, stated because it is easy to assume otherwise (measured 2026-08-08, Addendum 36).**
The meat pool is `mf · S` where `S` is the **NPP capacity field** pool for the cell — it is **not** drawn from
`terrain.game_kcal`, and the per-biome GAME return-rate table (Return-Rate Table §3) does not enter this or any
other campaign path. `game_kcal` is reachable only through `TerrainField.game_level` ← `_step_agent`, i.e. only
with the substrate disabled *and* `game_stream=True`, which no harness in the repository sets. Perturbation
evidence and the exhaustive surface list: `tests/test_field_load_bearing_ctb.py`; status table: Return-Rate
Table §0. Since `mf` is also a scalar, a campaign's meat is the **same fraction of capacity in every biome** —
so "wire per-cell `MEAT_FRAC`" and "make `game_kcal` load-bearing" are the same piece of unbuilt work, not two.
(`MEAT_FRAC` itself is not idle: it reaches the model via `terrain.RETURN_CV` → `enable_emergent_band_size`.)

**DEFERRED (documented, not built):** (a) **meat not η-discounted** — currently η(age) multiplies the *summed*
intake, so a child's received meat share is production-discounted; the lit-faithful refinement (band sharing
feeds dependents regardless of their own production → meat share *not* η-scaled) would let meat-sharing buffer
the dependent class, a separate increment. (b) **G.3 stochastic meat returns** (per-biome CV `terrain.MEAT_CV`;
**band-level correlated** draw) — NOT a "shock": this is the **ordinary foraging variance** (forest/Aché **1.97**,
desert/Martu **2.92** — measured; *these read `GAME_KCAL_STD/mean` = 0.73/2.24/0.29 until R-72, which was a
SPATIAL spread fed to a TEMPORAL draw*) whose *bad streaks* push the band below cap-for-all, the regime where
Cred-weighted sharing
decides who crosses the starvation floor. **It is the CORE mechanism of the Carbon stage** (a deterministic
meat economy is cap-pinned → Cred-inert), scoped INTO the first Carbon build (see the Carbon-substrate scoping
blueprint). (c) **Cred dynamics in the rivalrous path** — the meat/contest weight reads `φ` (uniform 0.5), not
`cred`; under the Carbon stage a `status_of` hook reads `cred`, seeded + heritable. The Carbon advantage is
**compositional** (κ-weighted meat concentrates bad-streak mortality on the low-Cred periphery while
density-disease pins only the *aggregate* rate, R-16) — to be demonstrated by the model, not asserted.

### §4.5.6 Carbon-on-substrate Tier-1 (the Cred hierarchy on the meat economy; built 2026-06-21)

Scoping: `blueprints/phase1/SiC_Games_P1_CarbonSubstrate_Scoping.md`. Brings the Cred/status hierarchy onto
the demographic substrate so κ-weighted meat sharing produces a **compositional** survival advantage. All
opt-in (default flags off → the 452-baseline unchanged; suite now 461).

**Mechanics built (D1 + G.3 + D3, "C-first"):**
- **D1 `status_of(agent)` hook (`substrate.py`):** the meat/contest weight is `(status_of(a)+ε)^κ` where
  `status_of` returns `cred` when `agent.use_cred_status` is set (the Carbon-substrate run), else the `φ` trait
  (default — preserves the Sugarscape contest tests). Applied in `compute_harvest_shares`, the diffusion
  `w_self`, and the `occ_wsum` movement weights.
- **G.3 stochastic meat (`DemographyConfig.game_meat_cv`):** the cell meat pool is a **mean-preserving
  lognormal draw**, ONE per cell (band-level correlated; all occupants share it), `μ=ln(M)−σ²/2`,
  `σ=√ln(1+CV²)`. **Per-biome CV anchor: `terrain.MEAT_CV`** — the measured DAY-TO-DAY meat CV (forest/Aché
  **1.97**, n=14,071 observed trips, 51.6% of days return nothing; desert/Martu **2.92**; Hadza big game 5.29),
  or `terrain.HUNT_CV`=2.11 generically. This is the *ordinary bad-streak variance* that pushes a band below
  cap-for-all so the share rule decides who crosses the floor — **the core mechanism** (a deterministic meat
  economy is cap-pinned → Cred-inert).
  **[R-72 CORRECTION, 2026-07-16]** This anchored to `GAME_KCAL_STD` (forest 0.73, savanna 2.24, desert 0.29)
  from the Carbon build until R-72. Those are **SPATIAL** cross-cell spreads — forest's is the spread across 7
  species' *means*, desert's across 3 hunt types — while this draw is **TEMPORAL** (fresh per step, per cell).
  The old anchor understated forest **2.7×** and desert **10×**. Savanna's 2.24 was the lone temporal number
  (Hawkes small-game income/day) but describes small game, ≈1% of Hadza animal tissue by mass. All runs
  predating R-72 (R-18/19/20, society benchmark, paternal calibration) hardcode 0.73 = the mis-anchored forest.
- **D3(i) heritable Cred (`enable_cred_status`, `cred_seed_sigma`, `cred_inherit_sigma`):** founders seeded
  `cred ~ lognormal(median 1)`; at IBI birth `child.cred = mother.cred·exp(N(0,σ))` (noisy lineage copy).
  Decay/earning OFF in Tier-1 (persistent heritable status). Movement temperature held at σ_base
  (`carbon_cfg.kappa=0`) to isolate the meat-share effect from the cred→exploration channel.

**VALIDATED — RESULTS R-18 (`run_3b_carbon_statval.py`, N=20 seeds, κ×CV sweep, 2026-06-21).** The thesis
holds strongly: at every κ>0 the Cred hierarchy **concentrates starvation on the low-Cred periphery** (direct
cred-death-deficit t=6.5–7.5, monotone in κ; mean(cred|alive) lift t=2.4–4.2) while **eq_pop stays κ-invariant**
(fertility-pinned, R-16) — compositional anti-fragility (R-1) on real demography. **A prediction was falsified:**
the **CV=0 control did NOT vanish** (κ=2: deficit t=7.2) — **meat temporal variance (G.3) is NOT the switch.**
The operative heterogeneity is **spatial competition near K** (cells crowded/poor → per-capita shares sub-cap
*deterministically*, so the cap-pinning wash-out is false near K), through TWO Cred channels: the meat harvest
split AND the **cell-occupancy movement contest** (`occ_wsum`/`w_self` are also `(cred+ε)^κ`). G.3 only
*modulates* — the effect **peaks at moderate forest-CV (0.73)** and falls at CV=0 (spatial only) and CV=2.24
(savanna meat too bursty to leverage). **Caveat:** κ weights harvest *and* movement together → a harvest-only
vs movement-only **ablation** is the next step. **Deferred (Tier-2):** earned/endogenous Cred + the
leadership/Couzin–Henrich movement model (§6b of the scoping bp); decay; β.

### §4.5.7 Cred-vector + B+ paternity (multifaceted status; building 2026-06-21)

Generalizes the scalar Carbon hierarchy (R-18) to a **multifaceted status vector** with **earned prowess** and
(forthcoming) **paternity**, all knob-tunable to collapse back to R-18. Blueprint:
`SiC_Games_P1_CredVector_BplusPaternity_Scoping.md` (scoped + red-teamed APPROVE-WITH-FIXES). Opt-in; default
flags off → R-18/461-baseline unchanged.

**Lit anchors** (PDFs in `literature/`): **von Rueden & Jaeggi 2016** — male status→reproductive success
**r≈0.19** (modest in humans; 4 dims [formidability, hunting, wealth, influence] ~equal weight; mating channel
> survival; polygyny amplifies ~⅓) → *calibrate mate-choice skew LOW.* **Smith 2004** — *reputation*, not
instantaneous return, predicts RS → *prowess = an accumulated EMA, not raw yield.* **Marlowe 2003** — male
provisioning **43% baseline → 58% (child <3) → 69% (child <1)**, conditional on biological paternity → the
`paternal_provision_frac` calibration target + cohort. **Descent** — foragers predominantly bilateral/bilocal
→ **`patriline_weight = 0.5`**. Forager polygyny ~4–11% (modest) / serial monogamy / Aché partible paternity
(2.1 fathers) → per-conception mate-choice lottery captures the real skew without pair-bonds.

**Facets (2, minimal):** **c_lineage** (= `cred`, ascribed: seeded + inherited, *mean-reverting* — its only
homeostat, since decay touches prowess only [red-team RT-3]) and **c_prowess** (achieved). Contest weight per
domain = **Cobb–Douglas** `Π_f (c_f+ε)^{κ_{d,f}}` with equal within-domain exponents (identifiability).

**BUILT (steps 1–2):**
- **Step 1 — facet machinery (`base_status`, `substrate.py`):** `base_status(agent,eps)` = `(cred+ε)` ×
  `(prowess+ε)` when `enable_prowess_facet`, else `(cred+ε)` — replaces the scalar `(status_of+ε)` at all three
  contest sites (harvest split, movement `w_self`, `occ_wsum`). The caller applies κ. **Collapses to R-18
  exactly** with prowess off; a *uniform* prowess cancels in the share ratio (so the seam-on/un-earned run
  reproduces R-18 — tested).
- **Step 2 — prowess growth (`prowess_decay` λ):** `prowess ← (1−λ)·prowess + λ·(meat_i / mean_meat)` — a
  **decaying EMA of RELATIVE meat intake** (reputation, Smith). **Relative ⇒ mean-pinned ⇒ runaway-safe by
  construction** (mean prowess → ~1; verified). G.3 supplies the skill/luck component.
- **Step 3 — sex-divided production (`sex_division`∈[0,1]):** the prowess SIGNAL becomes sex-specific
  **production credit** — meat → male hunters, forage → female gatherers — normalized within sex; the
  *consumption* economy is unchanged in aggregate (total food conserved → e₀/density pinned, only redistributed
  by prowess, as in R-18). **Resolves the step-2 independence question** (calibrated 1-seed, δ=3, forest):
  `corr(cred, prowess|male)` **drops +0.29 → +0.14** with sex-division — male prowess decouples from inherited
  lineage because it's earned from meat *production*, not the Cred-weighted *consumption* share → the 2nd facet
  is a genuinely independent (hunting) axis. (Full multi-seed validation pending, as for R-18.)

- **Step 4 — B paternity (`enable_paternity`, `mate_choice_strength` m, `patriline_weight`, `lineage_reversion`
  ρ):** at each IBI conception a father is assigned by **prowess-weighted mate-choice** `P(j)∝(prowess_j+ε)^m`
  among living adult males (m=0 = random = the drift-control); the child's **lineage** inherits a **bilateral
  blend of the parents' TOTAL standing** (`cred·prowess` — folds the father's hunting record into the child's
  ascribed rank), with **mean-reversion ρ** toward the population mean (the c_lineage homeostat — RT-3, since
  lineage has no decay). Fertility itself is unchanged (female-IBI); R-14 reopened minimally. `enable_paternity`
  off → matrilineal (step-1 exact). **Validated** (calibrated 1-seed, δ=3, forest, 500 steps): mate-choice
  produces reproductive skew **`corr(prowess,offspring)` +0.06 (m=0) → +0.15 (m=2)** (the von Rueden status→RS
  loop, calibratable to r≈0.19); the homeostat **bounds Gini(cred) 0.29 (ρ=0) → 0.25 (ρ=0.1)**; male **N_e
  stays healthy (~64–82)** → no small-N drift collapse (RT-4). m PROVISIONAL pending the full r≈0.19 calibration.

- **Step 5 — B+ paternal provisioning (`paternal_provision_frac`):** a father gives that fraction of his harvest
  OVERFLOW (above his cap, otherwise wasted) to his OWN children, drawn against the child's **residual need
  AFTER the two maternal tiers** (RT-2: conserved like the mother's tier-1, no double-feed; child never filled
  past cap — tested). It therefore bites only on the **constrained-mother / orphan cohort** (the orphan path is
  now reached — the loop no longer `continue`s on a dead mother), the Marlowe critical-period target. 0 = pure
  B. Calibrate so emergent male share of <3-yr provisioning ≈ 58% (Marlowe) — PROVISIONAL pending the run.

**ALL 5 STEPS BUILT + DEEP-RED-TEAMED (2026-06-21).** A fresh repo-grounded code audit of the whole stage
confirmed R-18 collapse, prowess mean-pinning, paternal-provisioning conservation, and determinism all hold in
the code — and found **one BLOCKER (now fixed):**
- **Lineage homeostat was not a contraction → unbounded `cred` drift.** The inheritance noise `exp(N(0,σ))`
  has mean `exp(σ²/2)>1` (a per-generation multiplicative *upward bias*), and reverting toward the **co-moving**
  population mean is not a contraction, so `cred` drifted up without bound (latent only because the forage-only
  shakedown goes extinct first; an isolated 2000-generation recursion ran to ~10⁴). **Fix:** (a) **mean-1
  noise** `exp(N(−σ²/2, σ))` (mean-preserving, no bias) and (b) reversion toward a **FIXED anchor (1.0 = founder
  median)** — a true contraction. `lineage_reversion=0` ⇒ a pure mean-1 multiplicative copy (R-18/step-1). A
  2000-generation regression test now guards boundedness. *(Note: R-18's recorded result used the old noise but
  ran only ~2 generations — drift was ~1%, so its relative/compositional conclusion is unaffected.)*
- Plus a MINOR robustness fix (unisex prowess-EMA now normalizes over `_use_prowess` agents only) — behavior-
  neutral in current configs.

**VALIDATED — RESULTS R-19** (run_3c, N=8 seeds × 1500 steps): **`mate_choice_strength` m≈4 → status→RS
r=+0.190 = von Rueden r≈0.19** (the calibrated value, **on the IFD/dispersed substrate**); the homeostat holds
live (mean cred bounded 1.2–3.1, Gini 0.18–0.23 — the BLOCKER fix works in practice); the compositional
anti-fragility (R-18) survives on the **combined** status (death-deficit +0.04→+0.11); male N_e healthy (111–170).
**Operating envelope: m≲4, ρ≥0.1** *(NB: on the BANDED substrate the band-territory mate-gate dilutes the skew, so
r≈0.19 recalibrates to **m≈5** — see §4.8.5, R-21. This IFD m≈4 is uncontaminated and stands for the IFD case.)*
(the cred equilibrium rises with m but is scale-invariant in the shares; Gini is the meaningful inequality).
**`paternal_provision_frac` calibration (life-history run, run_3d, 2026-06-21) — Marlowe 58% is ALREADY captured,
by a different channel.** Sweeping the knob, the male share of *deficit-provisioning* to <3-yr children saturates
at **~17%** (it can't reach 58%) — because the RT-2 residual-need design makes the father a **safety-net** (he
fires only when the mother fails / orphans, ~17% of cases), and because *deficit-provisioning* is the wrong
analog for Marlowe's *camp-calorie* share. The father's PRIMARY caloric contribution to young children is the
**band meat share**: with sex-division, males produce the meat (= `meat_frac` ≈ 0.55 of the diet, Cordain),
band-shared to women + children → **male caloric contribution ≈ 55% ≈ Marlowe's 58%**, by construction. So
Marlowe is matched via `meat_frac` + sex-division (validating those), and **`paternal_provision_frac` is a
separate safety-net for failing/orphan mothers — set ≈ 0.5** (saturation, fully covers the residual deficit).
A *proactive* paternal-provisioning redesign (father as primary, to push deficit-share higher) would risk the
RT-2 double-count and is unnecessary.

### §4.5.8 B++ assortative mating + lineage tracking (built 2026-06-21)

**`assortative_strength` α** adds status-similarity to the mate-choice draw: father weight = `prowess^m ×
exp(−α·(ln s_j − ln s_i)²)`, s=cred·prowess (high-status mothers pair with high-status fathers). α=0 = B+ (the
paired control). **Lineage tracking:** each founder seeds a unique `_lineage`; children inherit the **father's**
`_lineage` (patrilineal; matriline fallback) — diagnostics: #surviving lineages, largest-patriline fraction,
lineage-size Gini, mate-status correlation. **RESULTS R-20 (counterintuitive, control-revealed):** assortment
*works* (mate-status corr 0.04→0.80) but **does NOT consolidate dynasties** (largest patriline 10%→9%) and
**REDUCES the status→RS skew** (0.19→0.10) — homogamy ≠ reproductive skew; assortment constrains top males to a
limited top-status mate pool, *spreading* reproduction. The dynastic lever is `mate_choice_strength` (monopoly),
NOT assortment. The two are independently tunable.

### §4.5.9 Switchable society types (lit-anchored family-dynamics presets; built 2026-06-21)

**`demography.SOCIETY_PRESETS` + `society_knobs(name)`** bundle the family/status knobs (κ status-weighted
sharing · mate-choice skew m · assortment α · descent `patriline_weight` · status-mobility ρ · paternal
investment · sex-division) into named, **switchable**, lit-anchored ethnographic types — so we can run different
societies (and, later, *evolving* societies) by selecting a name. The presets capture each type's family-
dynamics *signature*, not every institution (bridewealth, the avunculate, persistent households are
*approximated* via the knobs). Five types:

| type | anchor | knob signature |
|---|---|---|
| **egalitarian_forager** | !Kung/Hadza/Aché; Woodburn 1982, Boehm 1999 | κ=0, m=1, α=0, bilateral, **high ρ (mobility)** |
| **complex_forager** | NW Coast; Ames 1994, Service 1962 | κ=1.5, m=3, α=1, heritable rank (low ρ) |
| **patrilineal_pastoralist** | Nuer/Maasai; Evans-Pritchard 1940, Betzig 1986 | **patriline 0.9**, m=4, α=2 |
| **matrilineal_horticulturalist** | Trobriand/Hopi; Malinowski 1929 | **patriline 0.1**, low paternal-provision (avunculate) |
| **stratified_chiefdom** | Polynesia; Sahlins 1958, Fried 1967 | **κ=2, very low ρ (rigid rank)**, m=4, α=2 |

**Benchmark (run_3f, 3 seeds, forest-Aché):** the types produce **distinct signatures**, headlined by the
**status-inequality gradient Gini(cred) 0.13 (egalitarian) → 0.36 (stratified)** — the anthropological
egalitarian↔stratified axis, emergent from the knobs (Boehm leveling vs chiefly stratification). Mate-homogamy
(−0.01→+0.73) and mean status (1.1→2.3) also separate as designed. **Caveat:** lineage *tracking* is currently
always **patrilineal** (child inherits the father's `_lineage`), independent of `patriline_weight` (which sets
the *cred* blend) — so the matrilineal type's lineage IDs still follow the father; a descent-aware tracking
(matriline when `patriline_weight` low) is a refinement.

### §4.5.10 Biome→society mapping + the evolving-society morph hooks (built 2026-06-21)

**Is there a clean biome→society-type mapping? Mostly NO — the lit-anchored finding.** Society type is driven by
**resource STRUCTURE (storability + density + predictability)**, not biome label (Testart 1982 storage; Binford
2001 packing). For the model's *forager* biomes (forest/desert/savanna/grass = dispersed, low-storability) the
mapping is nearly flat → **egalitarian_forager**; the one clean enabler of forager complexity is a dense
**storable/aquatic** base (NW-Coast salmon) → **complex_forager**. So `biome_default_society(biome, aquatic_rich)`
returns egalitarian for terrestrial forager biomes, complex only for aquatic-rich — the honest, weak mapping.

**The real driver is band CHARACTER → type (the morph hook).** `society_from_character(density_per_km2,
surplus_frac)` implements the lit ladder: below **Binford packing (0.091/km²)** + no surplus → egalitarian;
packed + large sustained surplus (Testart storage) → stratified; else (packed OR storable surplus) → complex.
`TerrainWorld.morph_to_society(name)` is the evolving hook — it re-bundles the family/status knobs (swaps the
demog config + substrate κ) mid-run. **Milestones** = Binford packing 0.091/km², Testart storage/surplus,
sedentism, Carneiro circumscription. **Honest limit:** in the current forage-only model the equilibrium density
(~0.065–0.1/km², Tallavaara) sits AT/below packing, so a band **stays egalitarian** until a **surplus/storage
mechanic** (the deferred climate/storage stage — abundance enables surplus, catastrophe selects for storage)
lifts density past the threshold. The hook is wired; the trigger awaits that mechanic. (The descent types —
patrilineal/matrilineal — are set by history/biome, NOT reached by the density ladder.) **C (full pair-bonding)
deferred.**

**STORABILITY-GATED MORPH (built 2026-07-03; R-46) — the biome differentiator.** On the canonical footprint=1
substrate the morph was "complex everywhere" (R-45): no band is ever packed (density ~0.011 ≪ 0.091 → `stratified`
unreachable without settlement) and `surplus_frac ≥ 0.5` in every biome (storage was NOT biome-gated — the canonical
`storage_temp_threshold_c=100°C` + constant-14°C placeholder temperature fired storage everywhere). Fix:
`storage_seasonality_gated` gates the overwintering store on the cell's **biome SEASONAL AMPLITUDE** (the
Testart/Binford storability signal — aseasonal biome → no glut→lean cycle → no storage → immediate-return
egalitarian; seasonal biome → storable glut → surplus → complex) via `climate.py::BIOME_SEASONAL_AMP_BY_CODE`
(forest 0.05 / savanna 0.40 / grass 0.60 LIT; desert 0.45 / mountain 0.55 / wetland 0.30 PROVISIONAL), threshold
0.25. **Result:** aseasonal FOREST flips 88% complex → **99% egalitarian** while seasonal biomes stay complex (forest
survives, 588) — the morph now FITS the biome. Ordering is **seasonality-driven, not productivity** (rich-but-
aseasonal forest = egalitarian like the Mbuti; seasonal biomes complex — the intended Testart pattern). Off ⇒ the
temperature gate (bit-exact). **SUPERSEDED (R-47):** the seasonality gate mis-orders desert (→ complex; real desert
foragers are the paradigm egalitarians) — the correct driver is AQUATIC.

**AQUATIC-GATED MORPH (built 2026-07-03; R-47) — the corrected driver.** Most foragers in most biomes are
EGALITARIAN (Mbuti/Hadza/Ju); complex foragers are the rare exception, tied to a dense STORABLE AQUATIC resource
(NW-Coast salmon, Calusa, Jomon; Testart/Kelly/Ames). **Two-role fix:** storage plays two roles — a survival BUFFER
and the complexity trigger; gating STORAGE on water removed the buffer from dry biomes → desert EXTINCT. So keep
storage a broad buffer (marginal biomes survive) and gate only the **MORPH** (R-48 final form): `morph_aquatic_gated`
forces a band to `egalitarian_forager` unless BOTH (a) **seasonal aquatic glut** `mean(wateracc × seasonal_amp) ≥
morph_aquatic_threshold` (0.15) — the anadromous-run/seasonal-fishery signature, so an aseasonal watery forest
(Mbuti) stays egalitarian despite rivers — AND (b) **productive setting** `mean(npp_gm2) ≥ morph_npp_floor` (500) —
the true-desert vs river-desert distinguisher (diagnosed R-48: wateracc/seasonality DON'T separate desert, which has
the HIGHEST of both; only absolute productivity does — a desert oasis npp≈400 is a waterhole not a fishery; a Nile
floodplain ≳550 can be complex). **Result:** forest EGALITARIAN (aseasonal), **desert EGALITARIAN + surviving** (poor
setting — Kalahari/Ju), montane/savanna COMPLEX (seasonal productive rivers — Plateau/Columbia salmon). The correct
forager-complexity signature (Testart/Ames/Kelly): complexity rare + water×season×productivity-linked. Off ⇒ ungated
morph (bit-exact). `stratified` still awaits settlement density. Recommend canonical `morph_aquatic_gated=True,
morph_aquatic_threshold=0.15, morph_npp_floor=500` (PROVISIONAL); pending sign-off.

---

### §4.5.11 Storage — the delayed-return economy (built 2026-06-25; the morph trigger's first piece)

**Status: BUILT (flaggable, default OFF). The first piece of the §4.5.10 morph trigger the model "awaits".**
Anchors: **Binford 2001** (storage threshold Effective Temperature **ET ≤ 15.25 °C** — an "overwintering tactic";
packing 0.091/km² = our `BINFORD_PACKING_PER_KM2` ✓), **Testart 1982** (storage = prime mover → sedentism,
density, inequality), **Woodburn 1982** (immediate- vs delayed-return: storage is the egalitarian→hierarchical
pivot). Config: `DemographyConfig.enable_storage / storable_fraction / store_capacity_reserves /
storage_temp_threshold_c`.

**Mechanic (COLLECTIVE band granary; blueprint `…_Storage_Morph_Scoping.md` S.1).** In the **overwintering
zone** — cell mean temperature ≤ `storage_temp_threshold_c` (≈ Binford's ET 15.25 °C, mapped onto the C.4a
latitudinal temperature field) — co-resident occupants' harvest **OVERFLOW** (intake above the *personal*
reserve cap, which stays the individual buffer — itself already covering solo survival beyond the 2–3-day carry,
Woodburn) is **ENFORCED** into a **per-cell collective store** (`_cell_store`), capped at
`store_capacity_reserves × reserve_full × band_size`. In the **lean season** the granary is **drawn down to top
occupants toward their caps** — the band lives off the store through winter. **S.2 (BUILT):** the draw is
**cred-weighted** — `allocate_store_draw` allocates the granary by **status^κ** (the same `base_status`/κ as the
meat pool), capped at each agent's deficit = the **Hayden control-of-redistribution inequality engine** (κ=0 →
equal/egalitarian; κ>0 → high-cred fill more of their reserve, bounded/graded so commoners get a smaller-not-zero
share). The mechanism is deterministically unit-tested; the *society-level* inequality output is the **S.4 morph**
(a `stratified_chiefdom` emerging) — in the density-regulated regime winter starvation is ~nil (baseline mortality
trims first), so the draw surfaces as a winter-wealth differential, not death. A
*mobile* band barely accumulates (you can't store if you move, Testart) ⇒ storage ↔ sedentism reinforce.
**S.3 spoilage:** `storage_decay` erodes every granary each step — high spoilage (fresh meat/fruit, tropical)
makes delayed-return not worth it (eq_pop reverts toward the immediate-return baseline: harsh-winter ON
0→447, 0.2→311, 0.5→230 vs OFF 199), a second reason tropical foragers don't store beyond the ET gate.
**Warm/aseasonal cells never accumulate** ⇒ immediate-return ⇒ egalitarian *by construction* — capturing why
the four tropical calibration foragers (Aché/Hadza/Hiwi/!Kung) don't store. Default OFF ⇒ bit-exact back-compat
(the overflow refactor is numerically identical when off). *(v1 used a per-agent store; the red-team replaced it
— individual survival is the existing reserve, the morph-driving store is collective.)*

**Gate (winter survival = carrying capacity).** Harsh winter (`a_seas=0.85`, trough 15% of peak, threshold=100
so storage is active everywhere to isolate the survival function): **storage ~doubles the sustainable population,
eq_pop 199 → 447 (2.25×)** (collective; per-agent v1 was 188→380), because the unstored population is capped by
what the *lean season* can feed, while the stored one lives off the band granary (369 stocked cells, ~207k each).
This is exactly Binford's overwintering logic. 4 unit tests (off ⇒ no store; accumulates in the cold zone;
temperature-gated off in warm cells; the harsh-winter capacity lift). **Provisional:** `storable_fraction=0.5`
(QSTOR exact % is in the Binford 2001 print volume, not web-accessible); the ET→model-temp mapping is a
calibration point.

**S.4 society morph (BUILT, per-cell; blueprint S.4).** The `society_from_character` hook is finally CALLED.
Per-cell state (`_cell_society`/`_cell_settle`); the harvest loop reads `kappa_cell` (the cell's society κ:
egalitarian 0 … stratified 2) for the meat pool + the store draw; a settlement detector computes density +
surplus (store/cap) each step and morphs `egalitarian→complex→stratified` with a `morph_settle_steps` (≈1
generation) hysteresis timer; abandoned/collapsed cells decay back to egalitarian. **Per-cell (RT-1 decision):**
a "band" = a cell's occupants (no band entity; the cell is the sharing unit), so society attaches to the cell;
stratified bands are sedentary so this is stable. **Storage TETHERING — RETIRED 2026-06-29
(`storage_tether_reserves` deleted; was: a stocked band STAYS PUT → forced concentration).** It was a band-aid for
the pre-bands max-occupancy-2 dispersal (no cell ever reached packing, so the morph couldn't fire). With the
emergent bands of §4.8 (grouping drives + bonded mating) now providing real cohesion, **the morph fires from
emergent density + storage alone** — verified in `run_3h_tether_retirement.py` (5 seeds × 800 steps, corrected
substrate: packing reached, 220 cells morph to `complex_forager` with NO tether). The tether's only distinct
effects were over-concentration artifacts (≈4× pop; a few cells forced to surplus ≥ 0.7 → `stratified_chiefdom`,
itself an artifact since stratified chiefdoms need a delayed-return surplus base, not generic foraging). The morph
scenario tests (`test_morph.py`) now run on the corrected substrate without it. See §4.8.5.
**Scenario gates:** cold/storable+tether → `complex_forager` emerges; no tether → no morph; warm world
(ET-gated off) → never morphs (immediate-return geography); **sustained famine → cells collapse back to
egalitarian**; flag off → no morph state. `stratified_chiefdom` is the rare apex (needs packed AND surplus≥0.7).
The **collective-vs-individual** grain is settled (collective, S.1); per-cell **family-knob** localization
(mate-choice etc. — reproduction still global) + proto-ag yields (DEFERRED_MECHANICS **PA-1**) remain.

---

## Mortality architecture — decisions, decouplings, neglects (added 2026-06-20; Biome-Mortality blueprint)

**DELIVERABLE (supervisor scoping 2026-06-20):** emergent **total** age-specific mortality `q(x)` and how it
varies by **dwelling biome** — NOT cause-decomposed output channels (channels only where needed for
correctness). Blueprint: `blueprints/phase1/SiC_Games_P1_BiomeMortality_Blueprint.md` (+ red-team v1 §7b).

### §4.6.1 Baseline de-warfaring (DONE 2026-06-20; RESULTS R-15)
Frontier/colonial violence **excluded entirely** — never a modeled dynamic (it is a contact-era artifact;
Aché ≈50%+ of forest-period deaths are conspecific violence, mostly **external warfare vs Paraguayan
colonists**, §4.2.7). **Procedure:** strip the **external-warfare** hazard fraction by age `w(x)` from the
Aché-total Siler (KEEP infanticide + disease + accident — pristine), `h_dewar(x) = h_total(x)·(1−w(x))`, and
**re-fit a Siler** by least-squares. **`w(x)`:** ≈0 for unweaned (0–3 yr; their violence is infanticide,
kept), **0.35** for ages 4–59, **0.25** for ≥60 (documented Aché aggregate + age-pattern; Table 5.1 age×cause
%s are a non-text-extractable formatted table — cross-checked against the Hiwi Table 5 rates).
**Result — `ACHE_FOREST_NATURAL` (demography.py):** `a1=0.1611, b1=0.6775, a2=0.00813, a3=3.781e-5,
b3=0.1025` → **e₀=42.7, e₁₅=45.0** (vs Aché-total 36.4/38.3; fit residual negligible). The change is
concentrated in the **Makeham a2 (0.013→0.0081)** — external warfare was the age-independent *adult* hazard;
infant a1 ≈ unchanged (infanticide kept). NOT the ~50 a full violence-strip would give. **Status:** OPT-IN
(passed via `DemographyConfig.siler_*` in biome runs; the default config keeps the validated Aché-total so
R-3 + the 444 suite are unchanged — this is *not* a silent change to the core). **Why it was the prerequisite
(R-15):** density-disease on the Aché-*total* baseline double-counts the disease the Siler already encodes →
e₀ caps at ~28 (Hiwi-like). On `ACHE_FOREST_NATURAL` (e₀=42.7), density-disease regulates *down* to the
realistic ~34–36 (Aché-matched) without the double-count.

### §4.6.2 Biome → mortality channel
Primary channel is **disease ecology** (pathogen load by climate/NPP), with **nutrition a seasonal,
infant-concentrated modifier** (foragers self-regulate to the biome CC → broadly fed regardless of richness;
R-5/6 — plausibly *correct*, not a bug). Exploratory (discover the gradient), **not calibrate-hard** — the
true gradient strength is uncertain and may be modest.

### §4.6.3 Pathogen channel — data status & approach
Tallavaara SEM coefficient + Guernier 2004 numeric slopes are **non-text-extractable** (formatted
tables/figures) and Guernier gives pathogen **richness, not mortality** (an unvalidated leap). **Redirect
to general disease-ecology / biogeography (not HG-gated) — FETCHED 2026-06-20** (both fully text-extractable,
in `literature/`):
- **Cashdan 2014** (*PLoS ONE* 9(10):e106752, open access) — THE anchor. A **pathogen *prevalence* index**
  (10 pathogens, ordinal 1–4 = absent→epidemic) across **SCCS societies** (Standard Cross-Cultural Sample —
  *includes foragers/traditional societies, pre-modern-medicine*), OLS-modelled on **mean annual
  temperature, # frost-free months, temperature extremes, precipitation, habitat diversity, population
  density** (adj. R²≈0.48). **Shape:** prevalence ↑ with temperature + frost-free climate + seasonal-dry-
  extremes; **predictors switch by latitude** — high-latitude pathogen load is temperature-driven, low-
  latitude is precipitation-driven (precip. effect peaks at *intermediate* rainfall, not monotone).
  Standardized (β) coefficients reported (the magnitude). Maps directly onto our terrain **temperature +
  humidity (CL-1 seam) + NPP**.
- **Dunn et al. 2010** (*Proc. R. Soc. B* 277:2587, via Europe PMC GREEN OA) — corroborates: pathogen
  *richness* GLM pseudo-r²=0.82, driven by **reservoir-host (bird+mammal) diversity** + temperature /
  precipitation / AET.

**Holocene-stability split:** *environmental* pathogens (malaria, soil helminths, arboviruses, diarrheal)
track temperature/humidity/productivity and their climate envelope is **stable** → these biogeographic maps
apply to the pre-agricultural world; *crowd/zoonotic* diseases (measles, TB) are **agriculture-era** and
**excluded** (Houldcroft & Underdown 2023). **Approach:** anchor the channel's **sign + shape + relative
magnitude** to Cashdan's prevalence-index-by-climate (the prevalence→mortality step is a *small* honestly-
bracketed leap, far better than richness→mortality); report the biome gradient as a bracketed sweep over the
residual magnitude until CL-1 climate lands real T/humidity. Precise β extraction deferred to the S2/S3 wire.

### §4.6.4 Modulation correctness (red-team v1 corrections)
- **"Modulate 36% of a2" was INCOHERENT** (B1/L-1): `a2` is a scalar Makeham constant; 0.36 is a fraction of
  *total* mortality; the causes spread across a1/a2/a3. **Correct formulation:** modulate `a2` wholesale (it
  IS the age-independent exogenous term; warfare/congenital largely live in a1/a3, already invariant) OR add
  an explicit additive biome-disease hazard component — **drop the "0.36-of-a2" claim**.
- **a1 reach (I-2):** infant disease lives in `a1`, but `a1` also contains **infanticide** (do NOT scale it
  by pathogen) and is **sex-scaled** (childhood ratio). Any new modulator must thread through `hazard()`
  ONLY — never `cumulative_hazard()`/`survivorship()` (founder-age sampling + the ×12 guard + the life-table
  validation depend on the unmodulated forms). Add a regression test that the unmodulated life table is
  byte-identical.
- **Mean-normalisation reference = Aché-forest NPP**, per-channel (risk normalised; density currently
  absolute; pathogen TBD).
- **The R-8/R-10 bang-bang blocker — RESOLVED BY SCOPING (2026-06-20; RESULTS R-11).** S0 (lagged
  body-condition EMA; `enable_condition`, `condition_alpha`) + S1 (child-priority shortfall-sharing;
  `provision_self_keep`) were built (444 green) and red-teamed → **CORRECT-BUT-INERT**: provisioning tops
  children to their cap, so survivors sit at condition ≈1.0 and the only under-cap children starve at the
  floor in ~1 step (the bang-bang) before the EMA moves; the self-regulation attractor (R-5…R-8) compounds
  it. The fine graded-nutrition→disease channel is **over-engineering for a TOTAL-mortality-by-biome
  deliverable** (it only relabels the *same* weaning-age deaths starvation↔disease, which the total sums
  over). **Decision:** **S1 ON** (drives child nutritional death → the Aché ≈0; coarse cause-split = the two
  existing buckets, starvation-floor vs Siler-baseline `deaths_senesc`); **S0 banked OFF** (opt-in, for the
  deferred fine effort). **The biome gradient does NOT depend on this** — it comes from the *exogenous*
  pathogen × `a2` channel (no dwell problem). The **fine** mechanistic synergy is deferred to **T-4**, where
  the two-part fix it needs (burn-cap provisioning + slow child-drain / stochastic returns) is recorded as
  the mark for later.

### §4.6.5 Violence module (DESIGNED, OFF by default)
Separate, toggleable, **scarcity/biome-gated** (resource-poor band → higher conflict hazard). Tiers:
*intra-band interpersonal* (runs in an isolated band; minor for mobile egalitarian foragers — Fry &
Söderberg 2013 → default OFF) and *inter-band warfare* (requires **contact** → coupled with **mixing** →
**deferred to the C-vs-Si conflict subsystem**, where it emerges from civ competition over territory).

### §4.6.6 Neglected / deferred (the explicit "what we left out" ledger)
External warfare + inter-band conflict + cultural **mixing** (→ conflict subsystem; **isolated far-apart
seeding** avoids both now and keeps per-biome mortality clean); intra-band interpersonal violence (separate
module, OFF); accidents (terrain-risk modulator, can promote to a tracked cause); crowd/zoonotic diseases
(agriculture-era, excluded); the convex Kaplan η production curve (linear JV-1 approximation in use);
maternal-removed female Siler (approach (a), deferred); full pathogen calibration (data non-extractable →
bracketed); the multi-biome harness (S3.5 — to build; every run so far is one 40×40 window); cause-decomposed
mortality outputs (out of scope — total q(x) only).

### §4.6.7 Adaptive metabolic down-regulation under deficit (`enable_metabolic_downreg`; added 2026-08-28, R-106)
**The gap (RESULTS Addendum 52–54 diagnosis).** The starvation reserve (`wealth`, Cahill §PARAMETERS) is
spent at a FLAT burn: `wealth += intake − burn`, death at `wealth ≤ floor`, and `burn` never falls no matter
how little the agent eats. So ANY sustained intake below 100% of the fixed burn is inexorably fatal — even 70%
of requirement kills in ~5 months — and there is no thin-but-alive state. Measured consequence at equilibrium:
**96% of starvation deaths are ACUTE one-step crashes** (reserve still >50% the step before), the dying agent's
intake-EMA is **2.4× requirement** (well-fed on average) and its realised e₀ is **23.5 vs the Siler schedule
36.5**. The deaths are volatility on a crowded cell, not scarcity — food is ample on average — but the flat
burn plus the ~1.7-month capped reserve cannot ride a transient dip.

**The mechanism (Keys 1950, LITERATURE.md — Minnesota Starvation Experiment).** Under a sustained deficit a real
body turns its metabolism down; the adaptive (mass-independent) component reaches ~10% at wk 4, ~20% at wk 12,
~25% at wk 24 of prestarvation BMR, and men held at ~50% intake for 6 months lost ~25% of body weight and
SURVIVED. Modelled: `burn_eff = burn · (1 − d)` where `d = downreg_max · clamp((1 − intake_ema)/downreg_span, 0, 1)`,
`downreg_max = 0.25` (Keys wk-24 adaptive), `downreg_span = 0.5` (full down-regulation at ≤50% intake). The
agent's own `_intake_ema` supplies the weeks-scale ramp (a single bad step barely moves it; a sustained deficit
drives `d` to its cap). Well-fed agents (`intake_ema ≥ 1`) get `d = 0` ⇒ **bit-exact when off, and inert for the
well-fed even when on**. It buffers TRANSIENT crashes without saving a CHRONICALLY starving agent: at a true
mean deficit below ~0.75× the reduced burn still exceeds intake and the agent dies, so the Malthusian ceiling
for real scarcity is preserved (contrast the subsistence-floor experiment, Addendum 55, which only relocated
death and was reverted). Diminishment couplings (strength/harvest, fertility) are documented in the Keys anchor
and deferred to a follow-up; the first build is the survival term only.

---

## Model architecture — scale, agents, family, fallbacks (added 2026-06-20; RESULTS R-14)

### §4.7.1 Two scales, one architecture
The model is **agent-based individuals** running on a **band/biome-level ecology**. Different layers live
at different scales, deliberately:
- **Ecology / demography** (food capacity, mortality schedule, disease, density, birth/death rates, age
  structure) — **band/biome-level**. Within a cell the harvest is split **per-capita**, so a cell is the
  *harvest sharing unit*; a cell's occupants are fed or not *as a unit*. **Per-agent (intra-cell) nutritional
  variance is ≈0 by construction, and that is physically correct** for a monthly step + sharing (R-14). *(NB: the
  HARVEST grain is the cell, but the **social/spatial band** — for mating, lumping, society — is the larger
  **mate-gate NEIGHBOURHOOD** (`bonded_mate_radius`): a band of ~25 spreads ~1/cell over a multi-cell territory,
  §4.8. "Cell = band" holds for sharing; "band = territory" holds for social structure.)*
- **Strategy / Cred / status** — **individual-level**, entering through the **sharing-rule weights** and the
  Carbon decision logic. This is where individuality is load-bearing and is *not* lumped.

### §4.7.2 The sharing rule is the strategy locus (where per-agent variance is/ isn't)
`compute_harvest_shares(occupants, S, kappa, phi_ε)`:
- **kappa = 0 (Si / egalitarian):** equal split `S/n` → **no per-agent variance** → band-level. This is the
  baseline every demographic run (R-1…R-13) used (`contest_exponent=0`).
- **kappa > 0 (Carbon / hierarchical):** shares ∝ `(phi+ε)^kappa` for Carbon agents → **Cred/status-weighted**
  → **per-agent variance BY STATUS** (high-Cred eat more). Carbon decisions are Cred-coupled
  (`σ = σ_base + kappa·tanh(cred/cred_scale)`; status amplification `1 + β·tanh(cred/cred_scale)`).
- ⇒ **per-agent nutritional variance is STRATEGY-SPECIFIC.** The R-5…R-13 "modulators inert" finding is the
  **Si baseline** (correctly ≈0); the **C case has real status-graded variance**. The banked S0/S1
  condition/provisioning machinery (R-11) is the **Carbon mechanism** — inert under equal sharing, live under
  Cred-weighted sharing. The C-vs-Si anti-fragility (R-1) *is* the individualism: C's hierarchy protects the
  high-Cred core under shock; Si's equal sharing crashes together (the dormancy cliff).

### §4.7.3 Family structure — a fecundity ensemble, NOT explicit families
The demographic model has **no marriage, no household, no father-role** (the biparental "partner" code in
`reproduction.py` is the unused Sugarscape path):
- **Reproduction is female-only and statistical** (`_do_births_ibi`): each fertile female has a per-month
  `fecundability` (~0.12), gated by the fertile window (menarche–menopause) + the IBI lactational refractory;
  SRB sets offspring sex. No pairing — births are individual female fecundity draws.
- **Males are demographically near-inert** — they carry the sex ratio + sex-specific Siler mortality, but do
  not pair, father, or provision. The only "family" is the **mother→child link** (`_mother`, for C.2b
  provisioning). "Single vs married" is not tracked — there is no marriage. **Implication:** band-level meat
  sharing (a future game tier) reaches children via the *band*, so the missing father-link is a non-issue at
  band scale (R-14 / Game-Economy RT-3).

### §4.7.4 Scale decision & fallbacks (R-14)
**Decision: keep individual agents** — the Cred/strategy/resilience core is **path-dependent** (Matthew
effect → heavy-tailed Cred; mean-field moment-closure fails), **discrete** (HG bands ~25–50 → demographic
stochasticity *is* the substance; extinction is a discrete event), and **emergent** (the R-1 dormancy cliff
is a synchronized threshold mass-death that mean-field DENSITY smooths into a smooth decline — it would
*erase the defining result*). Agents are affordable at HG scale (thousands, runs in minutes), so the
density compute-win is not worth the loss.

**Fallbacks, deferred to concrete triggers (NOT built now — YAGNI):**
- **Band-as-super-agent** (bands as discrete units; intra-band hierarchy → a Cred-inequality/Gini summary):
  *trigger* = continental / deep-time / many-bands scale where O(individuals) is prohibitive but inter-band
  discreteness (extinction, inter-band C-vs-Si conflict/migration) still matters. *Loses* the intra-band Cred
  path → valid only once the intra-band hierarchy has stopped being the question.
- **Mean-field / density:** *trigger* = fast parameter sweeps / equilibrium / sensitivity analysis. Use only
  as a **surrogate / cross-check**, never the main model (it smooths the R-1 cliff).
- **The cheap future-proofing is discipline, not architecture:** keep the **ecology-rates ↔ individual-
  strategy boundary clean** so a future coarsening is a swap-the-consumer job, not a rewrite. No swappable
  representation layer is built until a trigger arises.

---

## Emergent bands, bonded mating & the corrected band substrate (built 2026-06-26 … re-validated 2026-06-29; RESULTS R-21)

**The social/spatial grain.** Earlier stages treated "a cell = the band = the sharing unit" (§4.7.1) — correct for
the *harvest* mechanic (per-cell per-capita split), but a band of ~25 cannot live on one 100 km² cell: at forager
densities (**Binford 2001** packing ≤ 9.1 persons/100 km²; **Tallavaara 2018** NPP-density ~0.1–0.5/km²) a single
cell supports ~1–9 people, so **a real band is a spatially-EXTENDED entity, spread ~1 agent/cell over a multi-cell
territory.** This section builds the band as that extended entity and corrects the substrate it runs on.

### §4.8.1 Emergent-bands grouping drives (E.1 safety, E.2 mating-access) — movement utility (built abc5435)
Bands EMERGE from two multipliers on the per-cell movement utility (`substrate.py: diffusion_select_target`),
traded against the falling per-capita yield so an optimal band size self-organizes (not an imposed N). For
post-move group size `g`: **E.1 safety** (risk dilution — **Hamilton 1971** selfish-herd) `ypc ×= 1 + s_max·(1 −
e^{−g/g_s})` (saturating safety-in-numbers); **E.2 mating access** (**Wobst 1974** minimum-viable connubium ~25)
`ypc ×= floor + (1−floor)·min(1, g/g_mate)` (being below the minimum band size is actively penalized). Both default
0 ⇒ bit-exact IFD. Result: agents in groups ≥ 5 rose 29% → 62%.

### §4.8.2 Bonded mating (F.1) + the neighbourhood mate-gate (F.2) — the band = the mate-gate territory
**F.1** (`enable_bonded_mating`, built 67950d1) makes being a loner bad for FITNESS, not just movement: a female
reproduces only if a co-resident **non-son adult male** is present — loner lineages die out, the population
concentrates in bands by *selection*. **F.2** (`bonded_mate_radius`, Chebyshev; built a6a4ccf): because a band
spreads ~1/cell over its territory (above), a mate co-resident in the BAND is rarely on the mother's exact 100 km²
cell. radius 0 = the original per-cell gate; **radius ≥ 1 = an unrelated adult male anywhere within the band
territory.** This is **the operative definition of "the band" everywhere downstream** (the lumping ablation,
§4.8.5, flattens within the same neighbourhood). *Why it is required:* on the IFD substrate agents disperse to
~1/cell (per-capita-yield maximization), so the per-cell gate (r=0) finds no mate → extinction; **r=1 sustains a
turning-over population** (CC-1 substrate: r=0 → extinct 227→3; r=1 → 250→1624; r=2 → 250→4192, over 1500 steps).
Methods: `scripts/calib_bands_cc1.py`.

### §4.8.3 Banded seeding + founder mobile reserve — surviving the founding transient
Real foragers START banded (a gas of singletons can't bootstrap bands — no co-resident mates → ~0 births), so
bands are SEEDED. `seed_band_positions` (67950d1): ~n/25 kin bands of 25, allocated per-biome by capacity,
territory-spaced. `seed_band_positions_spread` (a6a4ccf): capacity-gated — spreads each band's members over the
viable cells of its territory (≤ ~`S_cell/burn` per cell) rather than stacking 25 on one cell (which starves
instantly, §4.8.4). **Founder mobile reserve** (`founder_buffer_steps`, a6a4ccf): each FOUNDER carries
`founder_buffer_steps × burn` kcal, drawn down to cover any per-step shortfall during the dispersal transient —
the carried/body-fat reserve a mobile band lives off the land with (**Kelly 1995** forager mobility; the model's
~1-step wealth buffer = (reserve_full−floor)/burn ≈ 1.07 cannot bridge it). Founder-only + decaying ⇒ no
steady-state effect on prior validations. Calibration (`scripts/calib_band_survival.py`): **spread seeding +
buffer ≥ 3 steps** survives the first season and sustains a live population; stacked seeding crashes at any buffer
(one cell can't feed 25). [PROVISIONAL founding device — `founder_buffer_steps` is a transient-bridge number, not a
fitted ethnographic value.]

### §4.8.4 Two corrections the bands work forced (a6a4ccf)
**(a) Measurement — corpse counting.** `phase1_model` pruned `agent_list` on death but never called
`agent.remove()`, so dead agents lingered in Mesa's `self.agents` AgentSet, frozen at their death cell. Any metric
read off `self.agents` counted CORPSES: the seeded-bands test was passing on 25-deep corpse piles (254 "agents",
12 alive; the **"96% in bands" claim was this artifact** — live ≈ 0% on bare forage). Fix: `agent.remove()` on
death; band metrics read live `agent_list`. The DYNAMICS were always correct (they run off `agent_list`), so this
is a measurement-correctness fix. **Audit:** morph (per-cell state on live occupancy) and storage (eq_pop on live
counts) claims survive; **R-18/19 used `agent_list` + the CC-1 field and STAND.**
**(b) Capacity — bare forage vs CC-1.** The emergent-bands runs used the **bare forage field**
(`TerrainField.level` = forage_kcal × hours; ~1–8 persons/cell) — its own §4.1 docstring flags it as a provisional
under-estimate. The validated demographic substrate (R-18/19) uses the **CC-1 NPP-capacity field** (§4.3.1, `E =
density(NPP)·100·burn`; ~30–50 persons/cell). On the bare field a band starves instantly; on the CC-1 field the
population thrives (non-bonded 250 → 9113 / 1500 steps) and **density-disease** regulates it. **⇒ bands must run on
the CC-1 capacity field, not the bare forage field** — the regime where a cell can hold a band and crowding is
disease-regulated rather than starvation-limited.

### §4.8.5 E.3-proper — m recalibration on the banded substrate + the lumping ablation (RESULTS R-21; run_3g, 2026-06-29)
Supersedes the contaminated E.3 (0f39c2d — bare forage + per-cell gate + `w.agents`). Substrate: CC-1
`SubWindowCapacity` (bounded-K patch → equilibrates) + `bonded_mate_radius=1` + banded seeding + grouping drives;
otherwise identical to R-19 (de-warfared Siler, δ=3, meat_frac 0.55, CV 0.73, ρ=0.1, full B+). 6 seeds × 1200 steps.

**Calibration: `mate_choice_strength` m=5 → status→RS r = +0.190 = von Rueden 0.19 exactly** (m=4 → 0.162; m=6 →
0.216). The banded substrate needs a **higher m than R-19's IFD m≈4** because the band-territory mate-gate dilutes
the skew (mate competition spans the whole band, not the cell). Homeostat holds (mean_cred ~2.2–2.7, Gini ~0.20),
N_e healthy 37–58, eq_pop fertility-pinned ~435–500. *(R-19's IFD m≈4 calibration, §4.5.7, is uncontaminated and
stands for the IFD substrate; m=5 is the BANDED-substrate value.)*

**Lumping ablation (band-aware homogenize — flatten WITHIN the connected band via `_band_groups` union-find, not a
1-agent cell; `homogenize_cred` = lineage facet, `homogenize_prowess` = achieved facet flattened *after* its EMA =
the strict band-as-unit lump).** The old claim ("homogenizing collapses status→RS 0.48→0.13") **does NOT
replicate** — it was a bare-forage/corpse artifact. Corrected three-part finding (m=5):

| arm | status→RS | offspring-Gini | cred-Gini | death-deficit (R-18) |
|---|---|---|---|---|
| IFD | +0.233 | 0.854 | 0.22 | +0.021 |
| bands-full | +0.190 | 0.831 | 0.21 | **+0.127** |
| bands, cred flat | +0.269 | 0.845 | 0.01 | **−0.071** |
| bands, full lump (cred+prowess) | +0.162 | 0.793 | 0.005 | **−0.087** |

1. The status→RS *correlation* is **prowess-driven** (the achieved/hunting axis, Smith 2004) → flattening cred
   barely dents it; cred-only flattening even *raises* it (skew shifts onto prowess).
2. RS *inequality* (offspring-Gini) is mostly **demographic** (age/Poisson) → full lumping trims it only ~5%.
3. The load-bearing role of within-band individualism is **R-18 compositional anti-fragility (death-deficit)**:
   flattening within-band status **FLIPS** mortality from concentrating on the low-status (+0.127) to not (−0.087).

⇒ **"Do NOT lump to band-as-unit" STANDS — but for the MORTALITY-SELECTION mechanism, not the von Rueden RS
skew** (the corrected, sharper replacement for the old E.3 claim). Methods/data:
`outputs/phase1_biome_mortality/run_3g_e3_proper.py`, `results_3g.json`.

**Cleanup DONE — storage-tethering RETIRED (2026-06-29; run_3h).** The tether band-aid (§4.5.11) was deleted:
on the corrected substrate the emergent bands (§4.8.1–2) reach Binford packing on their own and the
egalitarian→complex morph fires from emergent density + storage alone (5 seeds × 800 steps: packing reached, 220
cells → `complex_forager`, no tether). The tether's distinct effects were over-concentration artifacts (≈4× pop;
a few cells forced to `stratified_chiefdom` — itself an artifact, as stratified chiefdoms need a delayed-return
surplus base, not generic foraging). `test_morph.py` now validates the morph on the corrected substrate. The CC-1
capacity field used here is now a library module (`sic_games/capacity.py: NPPCapacityField`, §4.3.1).

---

### §4.8.6 F.2 — risk-dilution mortality (SHELVED, negative result) + band life-cycle diagnostics (2026-06-29)

**Risk-dilution-as-mortality — TESTED and SHELVED (`enable_band_risk`, default OFF).** Hypothesis: a group-size
risk-dilution penalty on the exogenous biome hazard (a loner loses the safety-in-numbers mitigation that the lit
biome accident rate — Hill/Hurtado/Walker 2007, measured on *band-living* people — already bakes in; **Hamilton
1971** selfish-herd), scaled by the cell's incident rate, would — together with density-disease (which *rises*
with crowding) — yield an emergent **optimal band size**. **It does not** (prototype `run_3i`, 5 seeds × 800
steps): higher penalty → *fewer* people in *smaller* bands (penalty 0→6: pop 281→64, mean band 56→5), a **death
spiral, not an optimum**. The reason is mechanistic: **mortality does not cause aggregation** — aggregation is the
**E.1 movement safety-drive's** job (§4.8.1); a loner-mortality penalty just *culls* the population, lowering
density → smaller bands → more loners → more penalty. So **risk-dilution belongs in movement (E.1), not
mortality**, and banding already has *fitness teeth* via the **F.1 mate-gate** (loners can't reproduce). The
channel is left in, default-OFF with a caveat, for future experiments only — it is not used.

**Band life-cycle diagnostics — BUILT (`TerrainWorld.bands()`; `run_3j`).** `bands(radius)` partitions the live
population into spatially-connected components (incl singletons) at the mate-gate radius — the band unit for
tracking. A **time-together (persistence) filter** then excludes transient elements: band lineages are tracked
across debounced samples (every 20 steps) by member overlap (a band continues if it retains ≥ half its members),
and only a lineage that has survived ≥ 3 samples (~60 steps / ~5 yr) counts as a REAL band. Characterization on
the corrected substrate (CC-1 patch + bonded r=1, 5 seeds × 1000 steps):
- **Instantaneous (RAW) size distribution is transient-polluted:** median ~3 (every momentary 2–3-person
  splinter counted), agent-weighted ~46, max ~138, ~17 % solo.
- **Persistence-filtered (the real bands):** **median band ~17** (the splinters drop out — an ethnographic band
  core), **~30 % of the population in a durable band** (≥60 steps stable), the rest in fluid/transient
  aggregations. (The agent-weighted/max stay high, ~63/~137, because the `r=1` connectivity definition durably
  *chains adjacent territories into one macroband* — a separate over-merge artifact that a stricter spatial band
  definition (separation gap / density core), not the time filter, would resolve.)
- **A balanced dynamic equilibrium:** **merge ≈ split (~20–21 / 100 steps)** and **collapse ≈ form (~6–7 / 100
  steps)** — bands are *fluid* (members flow between them) and turn over at matching rates, not rigid persistent
  units. (Collapse of sub-viable/isolated bands happens on its own from ordinary mortality — no risk penalty
  needed.) This is the merge/split/collapse the E.1/E.2 grouping + F.1/F.2 bonded-mating mechanisms produce.
- **Implication for F.3:** only ~30 % of agents are in a *durable* band because there is **no persistent social
  bond yet** (reproduction is statistical; no family moves as a unit). The fluidity is exactly what **F.3**
  (persistent pair-bonds / families that move together) would reduce — the diagnostic motivates it.

### §4.8.7 F.3a/b — persistent families: pair-bonds + nuclear-family co-movement (built 2026-06-29)

The deferred "C" / core of FD-1: replace the per-conception statistical paternity with **durable family units that
co-reside and move together**. Anchors: **Hill et al. 2011** (HG bands are mostly *unrelated* individuals linked by
**marriage** — bands = multiple families + maturing singles); **Marlowe 2004** (forager **monogamy**-dominant,
modest polygyny, multilocal residence); **Kaplan/Hill/Lancaster/Hurtado 2000** (juvenile dependence to ~15–18).
Config (`DemographyConfig`, default OFF): `enable_pair_bonds`, `divorce_rate`, `family_maturity_months` (~180 = 15 yr).

- **F.3a persistent pair-bonds (`enable_pair_bonds`).** Each step `_do_pairing()` matches unpaired adults WITHIN
  each band (mate-gate neighbourhood) into **mutual, monogamous** bonds — prowess-weighted by `mate_choice_strength`,
  kin-avoiding (not son/father). The bond **persists across births** (the partner is the father — no per-conception
  lottery) and dissolves on **partner death** (the widow(er) re-enters the pool → **serial monogamy**) or at
  `divorce_rate`/step. A female reproduces only with a **living, co-resident partner** (the gate replaces the
  F.1/F.2 band-mate gate when pair-bonds are on).
- **F.3b nuclear-family co-movement.** In the movement step the family — **mother + bonded father + dependent
  children (age < `family_maturity_months`)** — moves as a **unit**: the mother (root) diffuses with the grouping
  drives; her bonded father and dependent children **co-locate to her cell** (`_family_head`). Children **detach at
  maturity** → independent movement → exogamous dispersal. (Orphaned dependents — dead mother — disperse alone.)

**RESULTS (run_3j, CC-1 patch + bonded r=1, 5 seeds × 1000 steps; vs the F.2 baseline):**
- **Durable-band fraction 0.30 → 0.41** — families create more stable cores (the predicted F.3 effect); bonds are
  monogamous (mutual) and co-residence is exact (every paired female shares her partner's cell).
- **The §4.8.6 macroband over-merge artifact RESOLVED for free:** agent-weighted band 63 → **7**, max 137 → **26**
  — nuclear families move as cohesive units, so the population organises into **discrete family-cored bands**
  instead of one connectivity-glued component. Fewer solos (0.17 → 0.10) and collapses (7.2 → 3.9 /100).
- **Open (F.3c / calibration):** bands are now **nuclear-family-sized (~7)**, *below* the Hill-2011/Wobst
  **multi-family** band (~25) — each family tracks its own mother and they don't aggregate into multi-family bands.
  Reaching ~25 needs multi-family *band affiliation* (or stronger aggregation), a follow-on.

### §4.8.8 F.3c-1 — the band as a first-class entity: the collective-identity vector + band affiliation (built 2026-06-29)

The band becomes a **persistent multi-family entity** (~25), not the fluid connected-component of F.2. Anchors:
**Birdsell** (the "magic number" ~25 band, nesting in a ~500 connubium); **Hamilton et al. 2007** (HG social
structure is nested/self-similar, family→band→community, ratio ≈3.8); **Hill et al. 2011** (bands mostly NON-kin,
marriage-linked). *(Birdsell + Hamilton 2007 now web-verified — vol/pages/DOI confirmed; PDFs not yet filed. NB:
Birdsell's ~500 connubium is contested in the lit; the ~25 band — what we target — is independently corroborated.)*

**The collective-identity vector (`agent._group`, `sic_games/group.py: GroupVector`).** The affiliation is a
**vector, not a scalar** — the Carbon "hive-mind": `band_id` is the ACTIVE cell (F.3c band membership); `assabiyah`
(Ibn Khaldun group solidarity / cohesion) and `religion` are **reserved SEAMS** (present, inert) for later stages,
biome-linked. Newborns inherit the mother's vector; marriage updates `band_id`.

**Mechanism (`enable_band_affiliation`, default OFF; needs `enable_pair_bonds`).**
- **Seed:** founder `band_id`s = the initial spatial clusters (the seeded territory-bands).
- **Inherit:** a newborn copies its mother's vector (`GroupVector.inherit()`).
- **Exogamy/residence (D2 flexible/multilocal):** at marriage the spouse from the **smaller** band joins the
  **larger** (tie → the female's band) → mixes lineages across bands → bands stay non-kin.
- **Cohesion (movement):** a bounded per-step nudge toward the band centroid in `diffusion_select_target`
  (`band_cohesion`; gain 1±coh on a step toward/away from the centroid) — food stays the dominant term.
- **Fission/fusion (`_maintain_bands`, hysteretic):** a band > `band_split_size` (45) splits along its wider
  spatial axis at the median (a SPATIAL cut → cuts across lineages, keeps bands non-kin); a band <
  `band_merge_size` (10) fuses into its nearest neighbour band.

**RESULTS (run_3k, CC-1 patch, 5 seeds × 1000 steps) — VALIDATED on all four targets:**
- **Band size ~25:** agent-weighted **28.7**, median **25.3**, ~11 bands (Birdsell/Wobst ✓).
- **Non-kin / multi-family (Hill 2011 ✓):** dominant-lineage share **0.38** (1.0 = single-lineage clan), **~7
  distinct lineages/band**, only **30 % of adults** co-reside with a parent — bands are multi-family assemblages of
  mostly-unrelated adults, not clans.
- **eq_pop preserved (~330)** — band cohesion did not over-constrain movement or starve the population (red-team §3.3 OK).
- Band counts stable (no fission/fusion thrash) under the split=45 / merge=10 hysteresis.

### §4.8.9 F.3c-2 — per-band society (the morph relocates from the cell to the band; built 2026-06-29)

The society morph (§4.5.11 S.4) now attaches to the **band** (band_id), not the cell — the agent-based society the
handoff deferred. Active when `enable_band_affiliation` AND `enable_morph` (`band_society_on`); else the original
per-cell path (back-compat).
- **Per-band settlement detector.** Each step, per band: **density = members / occupied-FOOTPRINT area** (D3 — a
  tight band reads as packed even on a large territory, vs the cell metric), **surplus = the band's pooled cell
  granaries / its band-scaled capacity**; `society_from_character(density, surplus)` → the band's society, with the
  `morph_settle_steps` hysteresis. Bands not seen this step (extinct/merged) decay to egalitarian.
- **Per-band κ.** A cell's contest exponent (the meat-pool + store-draw inequality lever) reads its occupants'
  **band** society κ (`_band_society` → `SOCIETY_PRESETS[...]["kappa"]`), not the cell's. The per-cell detector +
  abandoned-cell collapse are bypassed under per-band.

**RESULTS (run_3k config + storage/morph, 600 steps):** society is a **band property** — all live bands morph
**egalitarian→complex_forager** (via the Testart storage-SURPLUS route, the correct delayed-return path; their
footprint density ~0.03/km² is below Binford packing so the packing-driven `stratified` apex does not fire — bands
aren't tight enough, a fair follow-on), `_cell_society` stays empty (per-cell bypassed). Tests: per-band morph
fires + bypasses cells; warm-world (no surplus) stays egalitarian. Back-compat: `enable_band_affiliation` off ⇒
the per-cell morph is bit-exact (the per-cell `test_morph` scenarios unchanged).

### §4.8.10 F.3c-3 — dynamic, condition-dependent fission/fusion + the assabiyah seam (built 2026-06-29)

The hard `band_split_size` constant becomes a **condition-dependent `tolerable_size`**, activating the
**`assabiyah`** cell of the collective-identity vector (Ibn Khaldun group solidarity). `enable_dynamic_bands`
(default OFF; needs `enable_band_affiliation`):
- **Assabiyah dynamics (per band, `_band_assabiyah`):** `assabiyah ← clamp(assabiyah + assabiyah_gain·surplus −
  assabiyah_decay, 0, 1)` — a band builds solidarity from its **surplus** (success → solidarity; the per-band
  surplus_frac F.3c-2 computes) and erodes it with a baseline decay (luxury/turnover). Mirrored onto each member's
  `GroupVector.assabiyah` (inherited; the seam later religion/biome will modulate).
- **Tolerable size:** `tolerable = band_base_tolerable + (band_split_size − band_base_tolerable)·assabiyah`. A
  band **fissions only above its own tolerable size** — so a rich, high-solidarity band **stays together larger**
  (toward the hard cap), a poor (low-surplus) band fissions at the base (~25). `band_split_size` remains the
  absolute runaway cap, `band_merge_size` the viability floor.

**RESULTS (run_3l, realistic storage threshold so surplus varies, 5 seeds × 1000 steps):** assabiyah builds
(mean **0.83**) and is **condition-dependent** — **corr(assabiyah, band size) = +0.27** (richer/higher-solidarity
bands are larger; poor ones fission smaller), with **eq_pop preserved** (497 vs the hard-threshold 496 — no
destabilization). Tests: assabiyah builds from surplus + mirrors to the vector; warm-world (no surplus) → assabiyah
~0; default-off back-compat.

**SEASON factor — RETIRED 2026-07-01 (`season_aggregation`, DE-7).** It scaled `tolerable_size`'s headroom by
`ClimateField.season()` (lean → *fission*). Removed on two grounds (R-31 review): **mis-signed** — moderate lean
should drive *aggregation*, not fission (Cashdan/Wiessner risk-pooling; Hadza dry-season water aggregation) — AND
**inert** (the threshold is dormant, bands sit below it, realized effect ≈ 0.05). The only legitimate
resource→fission role (severe scarcity) is now carried by **M2 malnutrition fission** (§4.8.14) via REALIZED
starvation, on the correct sign. Field + `season_ab` factor deleted; `season_aggregation=0` was the default, so
removal is bit-exact for all prior configs.

### §4.8.11 F.3c-2b — per-band family-knob localization (built 2026-06-29)

Reproduction reads the mother's **band-society** family knobs instead of the global config (`enable_band_family_knobs`,
default OFF; needs per-band society). **Decision (so it never overrides the E.3 m calibration):** the global config
is the **egalitarian baseline**; a band applies the **additive delta** of its society preset from the egalitarian
preset (`_band_knob` = `global + (preset[society][knob] − preset["egalitarian_forager"][knob])`, clamped). An
egalitarian/un-morphed band returns the global value EXACTLY; only a morphed band deviates. Localized: **mate-choice
strength** (`_do_pairing` — the partner-choice skew, per the female's band), **patriline_weight + lineage_reversion**
(births — descent + heritability, per the mother's band). **Validated:** a `complex_forager` band reads
mate_choice_strength **5 → 7** (global 5 + (3−1)) and lineage_reversion **0.1 → 0** (more dynastic), while
egalitarian bands keep 5 — so complex bands run a sharper, more heritable status hierarchy than egalitarian ones,
on the same world. (For the forager societies that fire, `patriline_weight`/`paternal_provision` deltas are 0; they
localize too, inert until a stratified/pastoralist society arises.)

**Open enrichments (remaining):** the full Ibn Khaldun **dynastic cycle** (assabiyah luxury→decay→collapse, not
just rise); **religion** (the other vector seam) amplifying assabiyah → larger polities + biome differences;
season-coupled **fusion** for stronger seasonal aggregation.

### §4.8.12 Full-stack integration validation — the monogamy↔von-Rueden tension (run_3m, 2026-06-29)

The whole social architecture turned on at once (Carbon status + game + density-disease + F.1/F.2 bonded mating +
F.3a/b families + F.3c-1 band affiliation + F.3c-2 per-band society + F.3c-2b family knobs + F.3c-3 dynamic bands/
assabiyah), CC-1 substrate, 6 seeds × 1500 steps. **Coheres:** 6/6 sustain, eq_pop 353, N_e 55; bands
agent-weighted **26.4** non-kin (dominant-lineage 0.35), 98 % morphed, assabiyah 0.95; cred homeostat bounded
(mean 2.27, Gini 0.30); **R-18 survival anti-fragility SURVIVES** (death-deficit **+1.077** — low-status die first).
**The one failure — status→RS collapsed:** corr(prowess, surviving offspring) = **−0.04** (E.3 was +0.19), and it
is *not* an age artifact (corr(age,prowess)≈0; prime-age-controlled still −0.55; cred→RS≈0).
**Diagnosis (lit-grounded — von Rueden & Jaeggi 2016, PDF read):** the status→RS skew runs through the
**mating/fertility** channel, and is **marriage-system specific** — polygyny (more mates) is the main amplifier,
and even monogamy gives r≈0.15 only via **wife quality**. The model under **strict monogamy (F.3a)** has *neither*
channel (no polygyny; partner fertility is status-blind), so status decouples from reproduction (it still drives
SURVIVAL via R-18, just not reproduction). **Resolution attempt 1 — modest polygyny (BUILT, `polygyny_rate`/`max_wives`):** a female may pair with an
already-married high-status male (gated, prowess-weighted) → high-status males accumulate ≤`max_wives` wives. The
polygyny MACHINERY works (run_3m, polygyny_rate=0.3/max_wives=3: corr(#wives, offspring) = **+0.71**; modest, max
3 wives) — **but status→RS did NOT recover** (+0.010 vs monogamy +0.012).

**Deeper root cause found — the PROWESS facet is corrupted under co-residence.** The achieved-status proxy
`prod_credit = meat_pool / n_males_in_cell` is **diluted by co-resident males, including a father's own dependent
sons**: corr(prowess, #males-in-cell) = **−0.396**, so reproductive success *depresses* a father's "hunting
reputation." This **cancels** the polygyny signal (prowess→#wives only +0.12, then offspring→sons→lower prowess
−0.40 ⇒ net corr(prowess, offspring) ≈ 0). So polygyny was necessary-but-insufficient: the broken link is
**prowess→pairing**, not the marriage system. (E.3 got +0.19 because the per-conception lottery re-selected
fathers by CURRENT prowess each birth; a fixed pair-bond lets the son-dilution accumulate over the bond.)
**Resolution attempt 2 — fix the prowess prod-credit (BUILT, supervisor-chosen option a):** the sex-divided
production credit now splits among **adult producers (age ≥ menarche)**, not all occupants — so a hunter's
reputation is no longer diluted by co-resident **dependent children (incl. his own sons)**, and juveniles are
excluded from the prowess EMA. **Effect:** the corruption halves (corr(prowess, #males-in-cell) −0.40 → −0.15) and
**full-stack status→RS recovers from ~0 to +0.057 (monogamy) / +0.079 (polygyny — polygyny now adds skew as it
should)**, while **E.3 in isolation is PRESERVED** (m=5 → status→RS **+0.194** ≈ 0.19, unchanged). (Side effects:
the cleaner prowess shifts the equilibrium — eq_pop 357→~530, mean_cred 1.9→1.4, Gini 0.28→0.20 — all still
healthy/bounded, R-18 death-deficit still >0.)
**Resolution attempt 3 — stickier reputation (BUILT) → the finding RESOLVED at status→RS ≈ 0.13.** The residual gap
after the prod-credit fix was prowess **volatility**: mate-choice acts on prowess AT PAIRING, but a fast mean-pinned
EMA regresses, so the end-snapshot under-measures the pairing-time skew. Slowing the EMA (`prowess_decay` 0.10 →
**0.05**; half-life ~7 → ~14 months — a *reputation*, not last week's catch, **Smith 2004**) lifts the full-stack
skew and it **plateaus at ≈ 0.13** (sweep: 0.10→+0.08, 0.05→+0.13, 0.02→+0.13). The family stack adopts
`prowess_decay = 0.05`; **the realistic forager config (families + modest polygyny 0.3/cap-3) lands status→RS
≈ +0.13** (eq_pop ~540, N_e ~65, Gini 0.19, R-18 death-deficit +0.23 — all healthy).

**Why ≈ 0.13 and NOT 0.19 — the justification (this is the model's status→RS for a monogamy-dominant society, and it
is CORRECT, not a shortfall):**
1. **0.19 is a CROSS-CULTURAL average.** Von Rueden & Jaeggi 2016 meta-analyse 288 associations across 33 societies
   of ALL marriage systems; the 0.19 is inflated by strongly **polygynous** pastoralists/horticulturalists. Their
   own **marriage-system breakdown**: status↔RS in **MONOGAMOUS** societies runs only via *wife quality*
   (**r ≈ 0.15**), and **polygyny is the main amplifier**.
2. **Our family model is a monogamy-DOMINANT forager society** (only modest polygyny), so its status→RS *should* sit
   at the monogamous-to-modest-polygyny value (~0.13–0.15), **below** the polygyny-inflated cross-system 0.19.
3. **The earlier E.3 "0.19" was the LOTTERY reproduction model** (no families): per-conception, *any* high-prowess
   male can father *any* birth — an idealised, polygyny-like "any-father" mechanism that reproduces the cross-system
   average. The family stack replaces it with realistic monogamous pair-bonds → the marriage-appropriate ≈ 0.13.
   (Confirming the mechanism: on the lottery substrate the SAME prowess_decay=0.05 gives status→RS ≈ 0.28 — the
   lottery over-skews; the regimes are intrinsically different, so no single `prowess_decay` makes both "0.19," and
   that's expected.)
4. **The skew is polygyny-carried in our model.** Strict monogamy alone gives only ≈ +0.03, because the model has
   **no "wife-quality" channel** (partner fertility is status-blind) — the monogamous von Rueden route. The modest
   POLYGYNY channel supplies the skew (+0.03 → +0.13). *(A status→partner-fertility "wife-quality" channel is a
   noted future enrichment that would add the monogamous r≈0.15 route on top.)*

**Net:** the full-stack finding is RESOLVED. The original collapse to ~0 was two bugs — prowess **corruption**
(dependent-son credit dilution) and **volatility** (too-fast EMA) — both fixed (adult-producer credit; decay 0.05).
The family model then lands status→RS ≈ **0.13**, the marriage-system-appropriate value for a monogamy-dominant
forager society with modest polygyny (von Rueden monogamous r≈0.15), a **refinement** over the lottery's cross-system
0.19. The lottery E.3 result (m=5 → 0.19 at decay 0.10) stands as the historical/simpler-mechanism calibration,
superseded by the family stack for the full model. **Remaining limitation (future):** the monogamous "wife-quality"
channel (status→partner fertility) is absent; adding it would let strict monogamy reach r≈0.15 on its own.

### §4.8.13 Social-Evolution Stage 1 — the band-size FORCE BALANCE: leader coherence + size repulsion (built 2026-07-01)

`tolerable_size` becomes an explicit **cohesion − dispersion** balance (Layton et al. 2012 two-force frame), each
term an independent opt-in flag (default OFF, bit-exact). The combination, per band, in `_maintain_bands`:
`cohesion_frac = clamp(assabiyah + leader_term − repulsion, 0, 1)`; `tolerable = base + (cap−base)·cohesion_frac·
season_ab`. The `[0,1]` clamp keeps `band_split_size` the absolute hard cap and `band_base_tolerable` (Wobst floor)
the minimum — the new terms only redistribute *within* that envelope. All three prior terms nest bit-exact when the
new flags are off (both new terms → 0 ⇒ `min(1, assabiyah+0)`, the §4.8.10 form).

**(1a) LEADER COHERENCE (`enable_leader_coherence`, `leader_coherence_gain`).** A SECOND cohesion source (distinct
from assabiyah — solidarity-from-success — this is charismatic/organizational): a band's top-status member lends
`leader_term = gain · weight(society) · leader_strength`, where `leader_strength = 1 − mean_status/top_status`
(self-normalizing ∈[0,1), read FRESH each step — no accumulated state, so a leader's death drops it immediately) and
`weight` is the **Boehm 1999 reverse-dominance gate** (`LEADER_SOCIETY_WEIGHT`: egalitarian **0** — mobile bands
LEVEL leaders → the mechanism is INERT, not just weak — complex **0.5**, stratified **1.0**). Magnitude UNANCHORED
(bracket/sweep, don't fit). Lit: Hooper/Kaplan/Boone 2010; Boehm 1999. Diagnostic: `band_leaders()` (top cred·prowess
per band) — also the controlled-experiment hook for scripted leader removal.

**(1b) SIZE REPULSION (`enable_size_repulsion`, `repulsion_gain/midpoint/width`).** Johnson 1982 **scalar stress** as
a DISPERSIVE term — a logistic in band size (Alberti 2014 shape), `size_repulsion = gain · factor(society) ·
1/(1+exp(−(N−midpoint)/width))` — SUBTRACTED from cohesion, so a large band needs MORE cohesion to stay whole.
**Resource-INDEPENDENT** (pure coordination cost — DISTINCT from the existing resource-scarcity fission that runs
through assabiyah↓ when surplus falls). **Johnson-coupled society relief** (`REPULSION_SOCIETY_FACTOR`: egalitarian
**1.0** — full scalar stress, mobile bands stay small — complex **0.5**, stratified **0.25** — hierarchy ABSORBS the
coordination cost → settling/institutions unlock larger groups). The `midpoint≈25` is the band-scale scalar-stress
onset (Wobst-minimal band); `width≈6` is Alberti's logistic shape **re-anchored from village scale (N≈127) to band
scale** — a bracket, not a fit (cf. the regime °C→CC% re-anchoring; Alberti's absolute 127 is a category error at
band scale). Magnitudes UNANCHORED.

**RESULTS (run_se1, 6 seeds × 900-step burn, realistic full-stack config).**
- **R-29 — repulsion BINDS + resolves assabiyah saturation.** With repulsion ON, max band size dropped **44 → 31**
  and the cohesion balance came **off the ceiling** (assabiyah 0.86 + leader 0.23 − repulsion 0.19 ≈ 0.89, no
  longer clamped at 1.0) — restoring headroom so *any* second cohesion term can move `tolerable_size` again. 7 unit
  tests (shape, Boehm/Johnson society relief, large-mobile-band fission, hierarchy-relieved persistence, hard-cap
  guard, headroom restoration).
- **R-30 — leader-death→fission is a PRINCIPLED NULL in the complex-forager regime (benchmark deferred).** A
  cohort-specific event study (kill each complex/stratified band's leader vs. a matched random adult; track how the
  bereaved band's ORIGINAL member cohort fragments) found **no leader-specific fission** — Δ(leader−placebo) distinct
  bands ≈ **−0.02 … −0.25** across checkpoints (slightly NEGATIVE, robust over 6 seeds). Two structural reasons, both
  correct-by-design: **(i) fission is not the equilibrium-binding size constraint** — bands settle ~20 (mortality +
  mate-gate + movement) *below* tolerable_size, so a small leader-loss tolerable drop rarely crosses the split
  threshold; **(ii) leadership is a DISTRIBUTIONAL property here** (top/mean-status ratio), so killing the top
  instantly promotes a near-identical runner-up — no irreplaceable KEYSTONE, no succession gap, no collapse. This is
  anthropologically right for the regime: Boehm's foragers have *no fixed keystone chiefs*; the leader-death-collapse
  signature belongs to **hereditary chiefs with succession crises** — the STRATIFIED **Ibn Khaldun dynastic-cycle
  stage (Stage 3)**, where a keystone chief + a succession gap makes a leader's loss consequential. **Verdict:** leader
  coherence is BUILT + unit-valid (a correct, ablatable cohesion source); its behavioural benchmark is **deferred to
  the dynastic stage**, not claimed here. Repulsion is the validated Stage-1 deliverable.

### §4.8.14 Resource → band-size response, corrected (M2 malnutrition fission + F resource-directed fusion; built 2026-07-01)

The fission-driver review (R-31) found the threshold DORMANT and, testing each candidate "does it help food-wise?",
DROPPED the moderate-lean aggregation cohesion (M1 — no functional payoff: the risk-pooling benefit is already
implicit in within-cell meat sharing, bands aren't under-aggregated at ~20≈Wobst-25, and "Hadza waterhole
aggregation" is just following concentrated resources = the existing IFD movement). Surviving design:

**M2 — malnutrition fission (`enable_malnutrition_fission`, `malnutrition_fission_gain`, `malnutrition_starv_rate`,
`malnutrition_ema_alpha`).** A DISPERSIVE term on the threshold balance:
`cohesion_frac = clamp(assabiyah + leader − repulsion − malnutrition, 0, 1)`, `malnutrition = gain·min(1, ema/rate)`,
where `ema` is a per-band EMA of the **realized per-capita starvation-death rate** (`_band_starv_ema`; each starvation
death is attributed to its band via `_note_band_starv`). Fissioning a large band gives the child a new band_id → it
diffuses apart → lower local density → higher per-capita yield → fewer SUBSEQUENT starvation deaths: **dispersal
substitutes for death.** **Intrinsically size-gated** — `tolerable` floors at `band_base_tolerable` (the `[0,1]`
clamp), so only bands LARGER than base fission; small bands just shrink/die ("large bands, not small," no explicit
test). **REACTIVE, not a forecast** (supervisor: bands disperse when starvation bites, not on anticipation;
anticipatory dispersal is a future "wise-leadership" feature). **Signal choice is load-bearing (R-32):** M2 does NOT
read `_condition` — that samples the post-harvest FED reserve and stays pinned ~1.0 under scarcity (survivor-biased),
so a condition-gated M2 never fires; scarcity here is expressed as death, so realized starvation is the honest signal.
Magnitude/rate UNANCHORED (bracket). Lit (qualitative — direction + fragmentation pattern): **Colson 1979** (FILED —
famine → "the breakup into small family groups which comb the region"), Turnbull 1972 (Ik), Kelly 1995, Layton 2012. **Validation (run_se2 substitution test):** severe −50% pulse, M2 off
vs on, 3 seeds → starvation deaths −120/−31/−24 (all lower), M2 fires (pressure 0.6–1.2), 2/3 seeds higher end-pop.
Off ⇒ bit-exact.

**F — resource-directed fusion (`enable_resource_directed_fusion`, `fusion_search_radius`).** A band below
`band_merge_size` joins the RICHEST neighbour (highest `_band_surplus`) within `fusion_search_radius` cells (else
falls back to nearest), instead of the nearest — a starving remnant merges into a well-provisioned band (Wiessner
hxaro; resource-SEEKING fusion, NOT anti-fission cohesion). Off ⇒ nearest-neighbour, bit-exact.

**M1 DROPPED (DE-8); `season_aggregation` RETIRED (DE-7, field removed).**

### §4.8.15 Genealogy logger — the Stage-3 analytic substrate (built 2026-07-01)

`enable_genealogy_log` — a PURE OBSERVER (no dynamics/RNG change; write-AFTER-step; bit-exact on↔off, locked by
`test_genealogy_is_observer_only_bit_exact`). Appends a flat record per birth/death — `(step, event, uid,
mother_uid, father_uid, lineage, band_id, cred)` — to an in-memory buffer (O(births+deaths), not a live tree per
the red-team); uses Mesa's stable monotonic `unique_id` (not `id()`); `dump_genealogy(path)` writes a CSV for
OFFLINE analysis. Enables lineage-extinction curves, time-to-MRCA, dynasty depth vs. assabiyah, and who-fathered-
dynasties — the substrate the Ibn Khaldun dynastic-cycle stage (Stage 3) will need. Names/viewer deferred.

### §4.8.16 Ascribed-status mate-choice — the cred→RS channel (built + canonical 2026-07-02)

**Problem (R-35):** the 16-seed re-estimate found the composite (cred·prowess)→RS ≈ 0 [CI −0.035,+0.037], NOT the
6-seed 0.13 of R-26. It decomposes into **prowess(achieved)→RS +0.10** (the working von-Rueden channel) and
**cred(ascribed)→RS −0.07** — because mate-choice weighted *prowess only* (`_do_pairing`), cred had no mating
channel and its RS sign was a weak diffuse non-causal confound. **Mechanism:** `enable_ascribed_mate_choice` makes
the female's mate-weight `(prowess · cred^(a·sw))^mate_choice_strength`, where `sw = MATE_ASCRIBED_WEIGHT[society]`
society-gates the ascribed pull (egalitarian **0.25** floor / complex **0.6** / stratified **1.0**) — family sways
marriage even among egalitarians (Ember & Ember), harder as society stratifies — and `a = ascribed_mate_strength`.
**Calibration:** swept `a`; **canonical `a=2.5`** → composite **+0.128 ≈ von-Rueden 0.13**, Gini stable (no dynastic
runaway; the rank-homogamy + virilocal knobs of the gathering §4.8.18 prevent lineage-flattening). Off ⇒ bit-exact
prowess-only. **The full reframe of R-19/R-21/R-26's 0.13/0.19 headline is HELD** pending settlement-arc validation
of the stratified ~0.19 endpoint. Blueprint `…_AscribedMateChoice_Scoping.md`.

### §4.8.17 Newborn→adult life-history — canonical wiring + latent-bug fixes (built 2026-07-02)

The Kaplan-2000 childhood machinery (§4.4/§4.5: graded η production, `consumption_factor` maintenance,
`reserve_scale` neonatal reserve, provisioning) was **fully built but never engaged** — no `LifeHistoryConfig` was
passed, so newborns foraged at full adult rate. **Canonical:** `enable_life_history` auto-builds a MONTH-scaled
config (`forage_age_min=180`, `forage_age_max_offset=120` — the class defaults are legacy YEARS) + `enable_provisioning`.
**Three latent bugs fixed** (R-38): (1) the hard `max_age` cap was DEAD CODE under demog (an `elif` on the
`demog is None` branch) → Siler-tail agents reached age 1111 → now enforced inside the demog branch (maxage 899);
(2) the elder η ramp went NEGATIVE past max_age → `base_status<0` → `base_status**κ` returned a COMPLEX number →
movement crash → η now clamped at `eta_old` (`base.py::eta`); (3) founders received lh from the constructor param,
not the auto-built `self._lh_cfg` → fixed (`_init_agents(n, kcal_cfg, self._lh_cfg)`). Forest childhood-ON eq_pop
322, 41% children foraging at η 0.57. Retires DEFERRED JV-1 (juvenile curve now live, not a binary gate).

### §4.8.18 The gathering — seasonal cross-band exogamous marriage-aggregation (built 2026-07-02)

**Why (R-39):** at low band density a bonded-pair society can't *find* mates locally — reproduction (year-round via
pair-bond) was coupled to mate-finding (needs an eligible unbonded partner in range). The gathering DECOUPLES them:
`enable_marriage_aggregation` convenes bands at abundant sites every `aggregation_period` months when the season
exceeds `aggregation_season_threshold` (spring pulse; Mauss/Steward/Lee/Conkey — the ethnographic aggregation
festival), draws sites `aggregation_site_sep` apart, and pairs across bands within `aggregation_radius`
(connubium; terrain/lit-sourced). **Residence wired both ways** (`aggregation_residence` ∈ virilocal/uxorilocal/
flexible — Marlowe 2004/Hill 2011/Ember&Ember 1971; whole-world comparison deferred to long-term studies) + optional
`aggregation_rank_homogamy` (similarly-ranked lineages marry — the R-35 anti-flattening knob). Implemented by
refactoring `_do_pairing` into a reusable `_pair_from_pool(females, males, residence, rank_homogamy, band_sizes)`
(bit-exact via residence="flexible"/homogamy=0) + `_do_gathering`. **Result:** fixes mate-finding (savanna 50 pairs
at the first gathering; forest 93% paired, eq_pop 433) — but savanna still collapses, because the residual root is
**family co-movement piling the family on one cell → overcrowd → starve** (savanna+co-movement=5, without=279), and
the DEEPER root is **fixed-r=1 diffusion mobility** (no biome-aware ranging; Kelly/Binford mobility ∝ 1/productivity).
The next stage (productivity-scaled movement range) supersedes the family-spread band-aid. Blueprint
`…_MarriageAggregation_Scoping.md`.

### §4.8.19 Productivity-scaled mobility — biome-aware movement range (built 2026-07-03)

**Why (R-39):** diffusion movement was hard-coded to a **r=1** von-Neumann step (`diffusion_select_target`'s `cands`
= 4 cardinals at distance 1). Real foragers spread over sparse territory by **ranging farther** where productivity
is low (Kelly 1995 / Binford 2001: residential mobility ∝ 1/productivity) — our low-NPP agents couldn't, so they
piled onto the few rich cells and starved (the savanna collapse). **Mechanism:** `enable_productivity_mobility`
makes the cardinal-candidate distance a per-agent **stride** `r = clamp(round(base·(npp_ref/max(local_npp,
npp_floor))^exponent), base, r_max)`, computed in the model from the **STATIC** local `npp_gm2` (geographic, NOT the
ClimateField instantaneous level — so the *range* doesn't oscillate with the season; transhumance is a deferred
extension). Low NPP → long stride → agents spread out; high NPP (forest) → `r→base=1` → the validated dense-forest
dynamics are untouched. **Water-aware glide:** each cardinal ray walks 1..r and takes the farthest reachable LAND
cell, **stopping at the first water** (foragers don't cross a lake; the `isWater` mask is passed into the mover).
`enable…=False` or `base=1`+`water=None` ⇒ **bit-exact** legacy r=1. **Calibration** (`exponent`/`npp_ref`/`r_max`)
is PROVISIONAL (bracket) — the mechanism ships ablatable/default-OFF; **locking the scaling law for canonical runs
needs supervisor sign-off** (Kelly gives the ∝1/productivity direction, Binford the cross-cultural magnitude).
Helper `demography::mobility_radius`; blueprint `…_ProductivityScaledMobility_Scoping.md`. **OUTCOME (R-40): this is
NOT the biome→society fix** — the ablation is negative (mildly harmful) and the pile-up premise is falsified (no
persistent crowding; the real lever is family CO-MOVEMENT, savanna 3 w/ co-move vs 327 w/o). The mechanism is
retained (valid, ablatable, default-OFF) for its own uses (mobility gradients / transhumance), NOT as the collapse
remedy (DEAD_ENDS DE-9).

### §4.8.20 Central-place co-movement — the family forages dispersed and shares (built 2026-07-03)

**Why (R-41→R-42):** F.3b family co-movement snapped the whole family onto the mother's (root's) single 100 km²
cell, where each member extracted `S/n` — self-competition that over-subscribed her cell (occ/head-cell 3.73 vs
population-mean 1.71) and collapsed her energetic fertility in marginal biomes (savanna births 4× lower → the
biome→society collapse). **The missing physics:** real foragers are CENTRAL-PLACE (Isaac 1978; Hadza/Ju) — they
co-reside + share but forage DISPERSED; dependents eat the pooled return, not the patch they stand on. The model
conflated co-residence with co-foraging. **Three ablatable prototypes** (all default OFF ⇒ bit-exact exact-snap;
need `enable_pair_bonds`): **(i) `comove_anticipate`** — the root's move utility counts its followers
(`extra_occupants` → per-capita on `S/(n+family)`), so she picks emptier/richer ground; **(ii)
`comove_footprint=k`** — followers take the lowest-occupancy land cell within Chebyshev `k` of the head (a dispersed
camp, not a stack); **(iii) `comove_provision_exclude`** — JUVENILE followers take no forage share (Kaplan: children
are provisioned, not self-extracting) so they don't dilute the mother's cell. **Comparison (R-42): FOOTPRINT is the
load-bearing fix**; anticipation alone barely helps (the family still lands on one cell); provision-exclusion is
partial (only juveniles). **CANONICAL 2026-07-03: `comove_footprint=1`** (a 3×3 ≈ 900 km² monthly camp on the
uniform grid). Full biome table (R-43): uniform footprint=1 recovers the collapse in EVERY biome (savanna 8→243,
montane 14→276, mixed 18→519, forest 145→426, desert 0→64); the NPP-scaled footprint (`comove_footprint_scaled`) is
FALSIFIED (agents self-select onto local NPP maxima → occupied-cell NPP reads "rich" → k=0 → collapse). Cell-size
design answer: keep the uniform lattice + behavioural footprint, NOT coarser per-biome cells (which break the grid +
double-count the Tallavaara capacity). Safety gate (R-44): footprint=1 PRESERVES status→RS +0.127 / band_awt 26 /
Gini 0.21 / %complex 83 / assabiyah; eq_pop re-baselines ~2× up (the co-movement brake removed — a correctness gain,
so absolute-population claims re-read on the footprint=1 substrate). Helpers
`substrate::diffusion_select_target(extra_occupants=…)`, `demography::footprint_radius`, `phase1_model` footprint
scatter + `_forage_excl`; blueprint `…_CoMovementCentralPlace_Scoping.md`; R-41→R-44.

### §4.8.21 Settlement & agglomeration benchmarks — lit-derived values + extraction (2026-07-05; agglomeration-economics rework)

The empirical standards the settlement / agriculture / agglomeration arc is calibrated + validated against — the "training set" for the reduced-order approach. Cell = 100 km² (10×10 km). (Already homed elsewhere: population density → §4.3.1 [Tallavaara median 11.9/100 km²]; packing threshold 0.091/km² + storage ET 15.25 °C → §4.5.11; band size ~25/500 + scalar-stress N≈127 → §4.8.8/§4.8.13. Not duplicated here.) Values route to `PARAMETERS.md`; citations to `LITERATURE.md`.

**Agglomeration exponent — returns-to-co-location (Bettencourt 2013 [VERIFIED, pypdf 2026-07-05]).** Urban output scales `Y = Y0·N^β`: socioeconomic **super-linear β ≈ 1.15** (empirical Gross-Metropolitan-Product **1.126 ± 0.023**, 95% CI R²=0.96; theoretical **7/6 ≈ 1.167**); infrastructure **sub-linear β ≈ 0.85** (0.849 ± 0.038; 5/6). **Extraction →** the agglomeration production-function exponent `L(n)~n^α`, **α ≈ 1.13–1.17 (≈1.15)**, NOT the P0 provisional 1.5. **CAVEAT:** measured on MODERN CITIES (socioeconomic output) — an explicit cross-domain borrowing; subsistence returns-to-co-location (weirs/terraces/defense/storage) may be sharper — a *testable prediction*, not a fit. **FINDING (production-function math):** at α=1.15 the per-capita `L(n)/n` optimum sits at **BAND scale (~25)**, flat out to ~150 → the measured exponent predicts *band-sized* aggregation (matching the mobile-band default); **village-scale nucleation (~150) requires a sharper α (~1.4–1.6) or a supplementary force** (storage / circumscription). Hence α is SWEPT in P1: 1.15 = the measured floor, the village-producing α = the reported finding.

**Site-catchment radius (Vita-Finzi & Higgs 1970 [VERIFIED, pypdf]).** Site exploitation territory = walking-time perimeter: **HG / non-agricultural ≈ 10 km radius** (2-hour perimeter); **agricultural ≈ 5 km radius** (return declines beyond 3–4 km; topography appreciable 3–5 km). **Extraction →** in 10 km cells, farming catchment ≈ radius 0–1, HG ≈ radius 1. **CORRECTION:** the built `settle_catchment_radius=2` (~20 km) exceeds the HG value → **trim to 1**.

**Complex-forager village size (Ames 1994 [VERIFIED, pypdf]).** NW-Coast villages/towns **"a few score to over a thousand people"** (~40–1000+ residents); coast pre-contact population ≈ **188,000** (Boyd); complexity driven by salmon + reliance on **STORAGE** + population-size thresholds; **owned** resource rights (individuals → villages). **Extraction →** the emergent-village-size target (~100s); the fishery-stability + storage benchmark (R-53); the heritable-ownership → ascribed-rank material basis (deferred bridge, blueprint 5b/Q7).

**Economic defensibility (Dyson-Hudson & Smith 1978 [VERIFIED concept]).** Defend a resource iff **dense × predictable** → the defensibility index `D = density × predictability` (DE-10; re-based to the catchment grain in the aggregation arc).

**Swidden crop→fallow (Conklin 1961 [filed, concept]).** Short cropping → long fallow, field-forest rotation → the warrant for Layer-B1 progressive soil exhaustion + fallow recovery. Specific durations are system-specific (the quantitative R-value synthesis is Ruthenberg 1971, unfiled); `soil_regrow_per_yr≈0.06` is a provisional bracket, not a Conklin-fitted value.

**Two calibration corrections this benchmark pass produced:** (1) `settle_catchment_radius` **2 → 1** (Vita-Finzi); (2) agglomeration α **1.5 → ~1.15** (Bettencourt; swept).

**Reduced-order framing (supervisor 2026-07-04).** The rows above form a condition × observable matrix `M`; plan: SVD → ~2–3 characteristic modes (productivity / storability / aridity) → project a local condition → its canonical configuration (village size, density, catchment) cheaply; agents evolve the **deviations** (aggregation onset, swidden bust, Carneiro). Honest reduced-order / ML framing — architecture = the mechanisms, parameters = these benchmarks, generalization = the emergent transitions; discipline: **free parameters < independent benchmark rows** (compression). Blueprints `…_AggregationSedentism`, `…_AgricultureTier`, `…_AgglomerationEconomics`.

#### §4.8.21b Emergent village stack — lit-anchored values (branch `gu-point-superlinear`, 2026-07-06/07; see RESULTS R-54…R-56, DEAD_ENDS DE-11)

The emergent alternative to the discrete settlement machinery (villages from co-location economics + band dynamics, no residence pin). All flags default-OFF ⇒ bit-exact.

- **Point-superlinear agglomeration** `aggl_beta ≈ 1.15` — the Bettencourt urban-scaling exponent (β, *super-linear socioeconomic output*; Bettencourt 2013, AGG1). Applied as the cell's OWN intensive output ∝ n^β ⇒ per-capita premium `A_cell·(n^(β−1)−1)` (0 for a lone agent). `A_cell = aggl_tier2·S_pot·cv_ref`; `aggl_tier2` a dimensionless intensification multiple (~1–5). The FALSIFIED catchment form (`L(n)` logistic; α is a saturation sharpness, **not** β) is retired — DE-11.
- **Forage cap** `forage_cap_hours` — per-person intake ≤ forage_kcal·hours (grounds the economy in Survey-A return rates). The village-nucleation lever (5.8→31.7% packed); optimum ~cv ≈ 5×BURN (non-monotone).
- **Terrain movement metabolism** `move_cost_kcal ≈ 750` (≈0.01·BURN) — a ~10 km residential relocation at human load-carriage locomotion energetics (~50–75 kcal/km; Pandolf grade term, Minetti gradient walking). Realized = ·cost[dest] (cost∈[0.15,1], slope/elev). Baseline metabolism kept ~fixed (Pontzer *constrained-TEE*, Hadza ≈ Western) — terrain modulates *returns* (forage_kcal), climate modulates baseline; NOT terrain-additive.
- **Catchment site-appraisal** `site_radius = 2` (Vita-Finzi 5–10 km catchment, AGG4), `site_lambda ≈ 1.0` (cost-distance decay, unanchored). Suitability = Σ_catchment S_pot·exp(−λ·dist·(0.5+cost)) — Kennett-Winterhalder IFD-settlement suitability + Orians-Pearson central place. Produces emergent Carneiro circumscription (packing only where prime land is scarce).
- **Fission ceiling / scalar stress / hierarchy** — `band_base_tolerable = 25` (Wobst/Birdsell magic-number band; AGG-context), `band_split_size = 45` (community rung), `repulsion_midpoint = 25` + `repulsion_width ≈ 6` (Johnson 1982 scalar stress; Alberti 2014 logistic shape, SET3), leader/hierarchy weight ladder egalitarian 0 / complex 0.5 / stratified 1.0 and scalar-stress relief 1.0 / 0.5 / 0.25 (Johnson: hierarchy dissipates scalar stress). `village_gain` (unanchored) lets payoff-above-saturation exceed the hard cap → villages 55–77, hierarchy-gated.
- **Resource-dependent storability** `STORABILITY_BY_RESOURCE` = grain 0.85 / fish 0.80 / forage 0.15 / game 0.35 (Testart 1982 delayed-return: storable seasonal resources enable sedentism; SET-context). storable_fraction becomes a per-cell weighted average of the resource mix. Confirmed **second-order** (R-57): even an 18× contrast on a scarce seasonal world doesn't move settlement — a fill-*rate* modifier, granaries fill from abundant overflow regardless. Gates complexity only in a marginal economy.
- **Storage capacity / fraction / decay — lit-calibrated** (storage survey; LITERATURE.md): `store_capacity_reserves = 12` (reserve_full ≈ 1.73 mo BURN [Cahill-anchored 130k, 2026-07-08; was 1.33 mo] ⇒ ~21 mo ≈ Halstead 1–2 yr granary = annual cycle + bad-year "normal-surplus" buffer; the old 3 = 5 mo was < one annual cycle), `storable_fraction = 0.7` (lit 0.5–0.8: strongly-seasonal storers live mostly off stores), `storage_decay = 0.02/mo` (~22%/yr; lit traditional 10–30%). Trajectory (per-capita granary, months, seasonal world): capacity now ~1–1.3 yr, cycles seasonally (drawdown 12→26% as the lean deepens), maintaining a ~1-yr buffer floor = the "normal-surplus" prudence pattern (a well-sited village works the top layer, holds the rest as insurance; deeper draw only in a marginal economy or a bad-year `shock_rho` regime). `fill = storable_fraction·(harvest + reserve − nutrition)` — i.e. `harvest − nutrition − waste`, cell-bound granary (mobile bands carry only body reserve ≈ 1.7 mo).

Lit added this arc (docs/LITERATURE.md): AGG1 Bettencourt; SK1–3 Walker/Gurven/Koster (skill-by-age); SET2 Handley & Mathew 2020, SET3 Alberti 2014 (SAVED); Binford 1980, Testart 1982, Johnson 1982, Kennett/Winterhalder, Turchin (TO-GRAB, paywalled). **Open (next):** Stage 2 military/competition payoff (Turchin/Carneiro — completes the `assabiyah` seam with its native warfare driver); scarcity calibration (river-ribbon prime land + deeper seasonality) to activate the dormant Carneiro/Testart/storage half.


---

*End of MODEL_SPEC.md — resource layer (§4.1), demographic layer (§4.2), terrain/climate methodology (§4.3),
resource-ecology/life-history/mortality (§4.4–§4.6), model architecture (§4.7), emergent bands & corrected band
substrate (§4.8).*

### §4.9 Elite layer - extraction methodology (2026-07-17...18; RESULTS R-82/R-83/R-84/R-84b)

#### §4.9.1 Boehm 1993 Table I - recovering the sanction COUNTS (the succession anchor)

Boehm's "World Survey of Egalitarian Sanctioning" is an x-marked matrix: 48 societies (rows) x 8 sanction types
(columns). The narrative gives only the aggregate ("38 of the 48 societies"), which is what `leveling_strength`
already used; the PER-SANCTION counts needed for succession are only in the matrix.

**A linear `get_text()` dump DESTROYS this table** - it emits the header words and then a flat run of bare `x`
tokens with no column association, so the counts cannot be read off. **Method: positional extraction.** Take
`page.get_text("words")` (each word carries x0,y0,x1,y1), locate the x-centre of each column HEADER word, bucket
every remaining word into a row by rounding y0, then assign each `x` mark to the column whose header centre is
nearest its own x-centre. Script: `sic_games/outputs/phase1_biome_mortality/` (probe series); the same technique
is required for Bird 2009 (§ image-table note) and for BHM Table 2 below.

**Recovered counts (2026-07-18):** Public opinion 10 - Criticism 6 - Ridicule 5 - Disobedience 7 - **Deposition 9**
- **Desertion 17** - Exile 2 - Execution 10. (Total 66 marks over 48 societies; Boehm notes "in many cases a
single society exhibited both types of behavior", so marks exceed societies as expected - a consistency check
that the bucketing did not double-count.)

**Transformation to parameters.** Removal-type sanctions are deposition and desertion; the rest are pressure.
`office_deposition_share = 9/(9+17) = 0.346`. This is the ratio of sanctions **ATTEMPTED** - what a society
practises - not of leaders actually unseated, because a deposition can FAIL against the challenge margin while a
desertion cannot fail. The model therefore counts `challenges_this_step` (attempts) separately from
`depositions_this_step` (successes), and only the attempt ratio is compared to Boehm.

**The trigger weights** come from Boehm's separate tally of 47 coded motivations: too aggressive 13, dominating
others as leader 14, ineffectiveness/partiality/unresponsiveness in a leadership role 10, lack of generosity or
monopolizing resources 5, moral transgressions 3, meanness 2. Restricting to LEADERSHIP conduct (14 + 10 + 5 = 29
of 47, i.e. 62%) and splitting it into overreach (14 + 5 = 19) vs failure-to-deliver (10) gives
`office_overreach_weight = 19/29 = 0.655`.

#### §4.9.2 Sahlins 1972:209 - the two succession regimes (qualitative -> a boolean)

The Siuai-vs-Nootka contrast is the operative distinction and is coded as a single flag rather than a rate,
because Sahlins states it as a structural dichotomy, not a frequency: the Nootka leader's "central economic
position is ascribed by right of chiefly due ... So centricity is built into the structure", whereas in Siuai "the
whole structure will as such dissolve with the demise of the pivotal big-man" => `succession_dissolve`.

**Implementation note that follows from the same page.** Sahlins is explicit that the big-man does NOT levy - he
mobilises through debt ("uses wealth to place others in his debt"), while the Nootka chief "is necessarily
accorded a certain right to group resources". **Therefore a non-zero `leader_share_frac` IS the chiefly regime by
construction**, and pairing it with `succession_dissolve=True` models a mixed case that Sahlins does not describe.
Flagged so a future run does not silently combine them and call the result ethnographic.

**Dissolution bar.** In dissolve mode a successor must clear his NEAREST RIVAL by `office_challenge_margin`, not
the band MEAN. Measured reason: against the mean, the max of ~25 lognormal-ish merit draws clears +25% essentially
always, so the flag had literally zero effect (identical output, 0 vacancies). Against the nearest rival it leaves
2/18 bands leaderless, which is the intended interregnum.

#### §4.9.3 Borgerhoff Mulder et al. 2009 Table 2 - the composite-Gini anchor

**Extraction.** The NIH-PA author manuscript renders Table 2 in landscape, so a linear dump transposes it: rows of
the printed table appear as interleaved column fragments. Recovered by the same positional method as §4.9.1
(bucket `get_text("words")` by rounded y, read each recovered line as one printed COLUMN). Cross-check that the
extraction is correct: the recovered alpha rows sum to 1.000 within each economic system (0.46+0.39+0.15 = 1.00;
0.27+0.14+0.59 = 1.00), and the recovered forager/horticultural Ginis (0.25/0.27) reproduce the paper's own
narrative statement that they sit "almost exactly [at] the average of the Gini measure of disposable income for
Denmark, Norway and Finland (0.24)".

**The class->facet mapping is read off their Table 1, not assumed** - i.e. from what each class was operationalised
as in the forager populations: embodied = Ache hunting returns / Ache and Hadza body weight / Hadza grip strength /
Hadza foraging returns (=> `prowess`); relational = Ju/'hoansi exchange partners, Lamalera food-share partners
(=> `cred`); material = Lamalera quality of housing, Lamalera boat shares (=> `material`).

**Composite computation (the comparison the model must be judged on).** Per-facet Gini is computed over ADULTS
(`age >= menarche_months`) with the standard sorted-rank estimator, then combined as
`G_composite = a_e * G(prowess) + a_r * G(cred) + a_m * G(material)` using the alpha row for the society type
being modelled. **The model's `material_gini` must NOT be compared to BHM's headline number directly** - the
headline is the alpha-weighted composite across all three classes, and the paper states separately that material
wealth types display HIGHER Ginis than the composite. Per-class Ginis are in their Table S5 (supplementary, absent
from the author manuscript), so the composite is the only like-for-like comparison currently available.

**Verified negative recorded here so it is not re-searched.** No chiefly-due PERCENTAGE - the fraction of group
product a leader receives - exists in Sahlins 1972 (Stone Age Economics, full text searched) or Ames 1994 (NW
Coast, full text searched). Both were read directly for one. This is why `leader_share_frac` is anchored on
outcome rather than rate. If a future source supplies a direct rate (Earle on staple finance is the obvious
candidate), it supersedes the outcome calibration.

> **Cross-reference:** Parameter values (energy density, forage kcal targets, terrain constants, Siler
coefficients, fertility params) are authoritative in `docs/PARAMETERS.md`. This document records
**methodology — how each literature value was extracted and transformed** — not the values themselves.
