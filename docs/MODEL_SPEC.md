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

### §4.3.1 CC-1 cell capacity — NPP → density [PROVISIONAL]
`K = density(NPP)·100 km²`, `density = min(0.5, 0.3·npp_gm2/1360)` people/km²; `E = K·burn`. **Source:**
Tallavaara 2018 (PNAS), HG density vs NPP; 1360 g/m²/yr = their low/high threshold. **Transformation:**
linear density–NPP relation anchored to the ethnographic ~0.1–0.5/km² band, capped 0.5, slope 0.3 so
density(1360)=0.3; `npp_gm2 = npp·3400`. **PROVISIONAL** — the full CC-1 stage fits Tallavaara's regression.

### §4.3.2 Climate seam — temperature & humidity [PLACEHOLDER]
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

## Resource-Ecology economy methods (added 2026-06-20; RESULTS R-6…R-8)

The economy layer added to give the demographic modulators nutritional *variance*. Harnesses
`outputs/phase1_resource_ecology/run_2d…2f`. **Headline (R-6/7/8):** all three are NEGATIVE — none makes
the graded modulators bite at equilibrium, because the density-regulated population self-organises to
"broadly fed at the biome carrying capacity." Each only moves the *carrying capacity*.

### §4.4.1 Seasonality (A.1) — `s(t)` harvest multiplier
Uniform annual cosine `s(t) = s_min + (1−s_min)·½(1+cos(2π·t/12))`, period 12 steps = 1 yr. **`s_min`
PROVISIONAL** (no lit anchor yet; tied to the deferred climate-season stage CL-1 / Berger insolation). On
`level = E·s(t)`. **Established:** regulates the demographic CC down to the **lean-season bottleneck**
(Liebig's law of the minimum; 95%→37% of peak food ceiling at s_min=0.4) but agents self-adjust and stay
fed year-round (reserves ~full, synergy ~1) — **inert on its own**.

### §4.4.2 Depletion (A.2, GD-1) — per-cell freshness `f` [PROVISIONAL]
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
**`mf` is a scalar config** (the dwelling biome's value) for the single-biome demographic runs; the per-biome
`terrain.MEAT_FRAC` dict is the home for a future per-cell wiring.

**DEFERRED (documented, not built):** (a) **meat not η-discounted** — currently η(age) multiplies the *summed*
intake, so a child's received meat share is production-discounted; the lit-faithful refinement (band sharing
feeds dependents regardless of their own production → meat share *not* η-scaled) would let meat-sharing buffer
the dependent class, a separate increment. (b) **G.3 stochastic meat returns** (per-biome CV `GAME_KCAL_STD`;
**band-level correlated** draw) — NOT a "shock": this is the **ordinary foraging variance** (forest CV 0.73,
savanna 2.24) whose *bad streaks* push the band below cap-for-all, the regime where Cred-weighted sharing
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
  `σ=√ln(1+CV²)`. Per-biome CV anchors `terrain.GAME_KCAL_STD` (forest 0.73, savanna 2.24). This is the
  *ordinary bad-streak variance* that pushes a band below cap-for-all so the share rule decides who crosses
  the floor — **the core mechanism** (a deterministic meat economy is cap-pinned → Cred-inert).
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
r=+0.190 = von Rueden r≈0.19** (the calibrated value); the homeostat holds live (mean cred bounded 1.2–3.1,
Gini 0.18–0.23 — the BLOCKER fix works in practice); the compositional anti-fragility (R-18) survives on the
**combined** status (death-deficit +0.04→+0.11); male N_e healthy (111–170). **Operating envelope: m≲4, ρ≥0.1**
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
(matriline when `patriline_weight` low) is a refinement. **C (full pair-bonding) and the Silicon comparison
deferred.**

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

---

## Model architecture — scale, agents, family, fallbacks (added 2026-06-20; RESULTS R-14)

### §4.7.1 Two scales, one architecture
The model is **agent-based individuals** running on a **band/biome-level ecology**. Different layers live
at different scales, deliberately:
- **Ecology / demography** (food capacity, mortality schedule, disease, density, birth/death rates, age
  structure) — **band/biome-level**. Within a cell the harvest is split **per-capita**, so a cell IS the
  *band* (the sharing unit); a band is fed or not *as a unit*. **Per-agent (intra-band) nutritional variance
  is ≈0 by construction, and that is physically correct** for a monthly step + band sharing (R-14).
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

*End of MODEL_SPEC.md — resource layer (§4.1), demographic layer (§4.2), terrain/climate methodology (§4.3),
resource-ecology/life-history/mortality (§4.4–§4.6), model architecture (§4.7).*

> **Cross-reference:** Parameter values (energy density, forage kcal targets, terrain constants, Siler
coefficients, fertility params) are authoritative in `docs/PARAMETERS.md`. This document records
**methodology — how each literature value was extracted and transformed** — not the values themselves.
