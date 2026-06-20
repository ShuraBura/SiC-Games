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

*End of MODEL_SPEC.md — resource layer (§4.1), demographic layer (§4.2), terrain/climate methodology (§4.3).*

> **Cross-reference:** Parameter values (energy density, forage kcal targets, terrain constants, Siler
coefficients, fertility params) are authoritative in `docs/PARAMETERS.md`. This document records
**methodology — how each literature value was extracted and transformed** — not the values themselves.
