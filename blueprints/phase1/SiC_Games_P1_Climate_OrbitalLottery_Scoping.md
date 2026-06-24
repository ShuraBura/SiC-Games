# SiC Games · Phase 1 · **Climate — orbital-lottery 4-layer variability** (comprehensive blueprint)

**Status:** BLUEPRINT for re-red-team (2026-06-21). Supersedes the v1 scoping (same file). Implements the
§4.1.6 star-mechanics seam + §4.1.7 catastrophe stub as a **4-timescale climate-forcing stage**. **Locked
discipline (§4.1.6):** stellar mechanics *bound the parameter draws*; they do NOT run tick-by-tick (no
insolation→NPP transfer inside the agent loop). **Supervisor decisions:** Q1 **(B)** — obliquity maps onto the
*empirical Earth §4.1.4 amplitude band* (a scaling dial, NOT a sunlight→food transfer function); Q3 **uniform**
draws over the (forager-sustainable) habitable range, no Earth-leaning prior; the **4th (regime-shift) layer**
is added as the society-morph driver; catastrophe is a separate step.

---

## §0. The four timescales (architecture)

| # | layer | period / scale | orbital/lit driver | role in the model |
|---|---|---|---|---|
| 1 | **Seasonal** | 12 mo (within-year) | obliquity ε (Spiegel 2009) | the within-year lean-season bottleneck (R-6) |
| 2 | **Interannual** | 2–7 yr | eccentricity e + ENSO (Spiegel 2010; Timmermann 2018) | good/bad years |
| 3 | **Regime-shift** | ~1–5 centuries (a few generations) | Holocene variability / Bond / LIA (Wanner 2008; Mayewski 2004) | **the SOCIETY-MORPH driver** — sustained CC shift pushes density across Binford packing → §4.5.10 transition |
| 4 | **Catastrophe** | shock, yrs–decades | megadrought / volcanic / caribou-crash (Cook 2010; Sigl 2015; Bergerud) | the resilience SHOCK (push band ≪ K) |

**The forcing (one product, peak-normalized, on the `harvest_field` — §4.1.7 isolated):**
`M(t) = season(t) · interannual(t) · regime(t) · catastrophe(t)`, each layer ∈ (0, 1] with peak pinned at 1.0.
The demographic substrate is **unchanged code** — it just reads a time-varying carrying-capacity field (the
R-6 `run_2d` wrapper pattern). **No double-count** (the legacy `s_min` lives only in the opt-in harness).

## §1. The per-world orbital lottery

**Stage 1 — draw orbital/stellar parameters (uniform over the sustainable-habitable range):**

| param | symbol | draw range | Earth | distribution | citation |
|---|---|---|---|---|---|
| obliquity | ε | **[0°, 60°]** (conservative habitable envelope) | 23.4° | uniform | Spiegel 2009 (no clean monotone ε→snowball threshold; broad habitable band) |
| eccentricity | e | **[0, 0.6]** (upper third marginal) | 0.017 | uniform (sustainable-bounded) | Spiegel 2010 (annual-mean flux governs; snowball cut 0.4<e<0.6) |
| stellar flux | S | **[0.34, 1.05] S⊕** | 1.0 | uniform | Kopparapu 2013 (max-greenhouse outer 0.344; moist/runaway inner 1.014–1.051) |

*"Forager-sustainable" = the demographic substrate still sustains a population; extreme worlds that extinct it
define the practical edge (measured, not assumed). Milankovitch long-term drift of (ε, e) is negligible within
a centuries-long run → one draw per world.*

**Stage 2 — map orbital → climate-forcing parameters (methods):**

| orbital | → forcing param | mapping (math) | citation / status |
|---|---|---|---|
| ε | seasonal amplitude **A_seas** | **(B)** linear map of ε onto the empirical §4.1.4 band: `A_seas = clamp(A_earth · sin ε / sin 23.4°, 0, A_max)`; monotone to ε≈54° (pole annual-insolation crosses equator — verified 54.0°). PROVISIONAL bounding heuristic, NOT a derived transfer fn (forage amplitude is rain/phenology-driven). | §4.1.4 (Earth band) + Spiegel 2009 (bounds) |
| e | interannual amp **A_e** + mean brightening | intra-annual flux swing `((1+e)/(1−e))²` (e=0.017→1.07, e=0.3→3.45); fold annual-mean `(1−e²)^(−½)` (+25% at e=0.6) into mean-CC. Interannual coupling only via precession (slow). | Spiegel 2010 |
| S | mean temperature **T̄** | `T̄ = 14°C + ΔT`, `ΔT ∝ S^¼` anchored at S=1→14°C (§4.3.2) — an effective-greenhouse offset so the *surface* T (not the −33 K effective temp) feeds the pathogen channel §4.6.3. | Kopparapu 2013 / §4.3.2 |

## §2. The four forcing layers (parameter tables + math)

**Layer 1 — Seasonal** (PINNED to the validated R-6 form): `season(t) = s_min + (1−s_min)·½(1+cos(2πt/12 − φ_b))`,
range [s_min, 1], **`A_seas ≡ 1 − s_min`**, period 12 steps, **phase φ_b per-biome** (forest fat-season vs
llanos wet-season are opposite-signed — keep the biome's own calendar). §4.1.5 game *threshold*-access shape
must NOT be smoothed by the amplitude knob.

| biome | A_seas (= 1−s_min) | lean-season cause | citation |
|---|---|---|---|
| forest (Aché) | ~0.0–0.1 (flat) | calories ~aseasonal | Hill 1984 |
| llanos/savanna (Hiwi) | **0.5–0.7** | wet-season flood access loss (Liebig) | Hurtado & Hill 1987 |
| Hadza savanna | ~0.3–0.5 (moderate) | dry-season water aggregation | Hawkes 1991 |

**Layer 2 — Interannual** (ENSO-like): `interannual(t) = 1 − A_inter·max(0, ξ(t))`, ξ = an AR/quasi-periodic
noise, period 2–7 yr.

| param | value/range | citation |
|---|---|---|
| period | 2–7 yr (quasi-periodic) | Timmermann 2018; Cane 2005 |
| amplitude A_inter | ±20–40% CC in marginal biomes; ≤10% in buffered (forest) | Timmermann 2018 (ENSO drought/flood) |

**Layer 3 — Regime-shift** (the morph driver): `regime(t) = 1 − A_reg·R(t)`, R = a slow Ornstein-Uhlenbeck /
piecewise excursion, period ~1–5 centuries.

| param | value/range | citation | note |
|---|---|---|---|
| period | ~100–500 yr (≈ a few–20 generations) | Wanner 2008; Mayewski 2004 (Holocene/Bond) | NOT glacial cycles (10⁴–10⁵ yr, too slow) |
| amplitude A_reg | **±10–30% CC** (Little-Ice-Age-scale ~0.5–1°C → CC effect; bigger for 8.2-kyr/Younger-Dryas tails) | Wanner 2008; Mayewski 2004 | drives density past/below **Binford packing 0.091/km²** → §4.5.10 morph |

**Layer 4 — Catastrophe** (per-biome Poisson; §3).

## §3. Catastrophe — per-biome table (the resilience shock)

| biome / setting | type | amplitude (CC drop) | duration | recurrence | citation | note |
|---|---|---|---|---|---|---|
| arid / grass / temperate flats | **megadrought** | 30–60% **(INTERPRETIVE — not a Cook number)** | decadal–multidecadal | ~0.1–0.5 %/yr | Cook 2010 | duration anchored; magnitude derived |
| tropical forest | **ENSO drought + wildfire** | 20–40% | 1–3 yr | ENSO 2–7 yr | Timmermann 2018 | |
| ALL (global) | **volcanic cooling** | **−0.3 to −0.6 °C common** (CC ~10–20%); **1–3 °C VEI7 tail** | 1–10 yr | common ~1 %/yr; VEI7 ~millennial | Sigl 2015 (19 largest CE tropical −0.6±0.2°C) | amplitude split common vs tail |
| migratory-game (grass/steppe/tundra, `game_mobility`≈1) | **caribou/herd crash** | **~50–66 % (game collapse)** | multi-year | **~40–70 yr cycle** | Bergerud; Zalatan 2006 (tree-ring, 5–10× swings); **Usher 2022 CAVEAT** (famine record confounded by colonial policy — discount the pure-ecological signal) | the high-latitude megadrought-analog |
| llanos / savanna (wet-season) | **flood** | **NEEDS OWN ANCHOR** (don't reuse the §4.1.4 caiman datum — that's the seasonal SHAPE) | seasonal | annual+extreme | (re-anchor) | |

**Resilience-test design point** (R-16/R-18: push band ≪ K) = a **~40–50 % CC drop sustained a few years**
(megadrought / caribou-crash scale). Implemented as the §4.1.7 amplitude modifier (writes ONLY to the field).

## §4. Deeper seasonal couplings (the realism ties — ranked)

| coupling | mechanism | lit-anchorage | priority | status |
|---|---|---|---|---|
| **water → season → aggregation** | dry-season shrink of small water → game + forager concentration at permanent water → packing (→ §4.5.10 morph) | dry-season aggregation documented (Hawkes 1991 Hadza; Hurtado & Hill Hiwi); per-biome **ephemeral-stream %** needs extraction (dryland hydrology) | **HIGH** (feeds morphing) | C.5 (after C.1–C.3) |
| **T/humidity → pathogen seasonality** | seasonal T/humidity → seasonal pathogen pressure | the pathogen channel (§4.6.3, Cashdan 2014) already reads T/humidity → **free** once they're seasonal | HIGH (free) | falls out of C.2 |
| **T → metabolic burn** | cold season → thermoregulation cost → higher burn | cold-climate forager energetics | MODEST | optional |
| **birth seasonality** | seasonal nutrition → clustered births | `energetic_fertility_factor` reads `_fed_reserve` → **emergent** | — | already emergent |

## §5. Math-mapping to the current structure (how it wires in)

- **The field wrapper:** a `ClimateField` wraps the existing `harvest_field` (`SubWindowCapacity`/`TerrainField`):
  `level(x,y) = base.level(x,y) · M(t)`. The model's `_step_rivalrous` reads `tf.level(...)` unchanged (R-6
  `run_2d` precedent: `level = E × season()`). **Isolation (§4.1.7):** the climate writes ONLY to this
  multiplier; nothing else in the resource/agent loop changes → no R-3/R-17 regression.
- **Per-biome φ / shape:** `M` carries the world-level amplitudes; the per-biome curve *shape* + *phase* stay in
  the §4.1.4/4.1.5 biome curves (the lottery scales magnitude, the biome keeps its calendar).
- **Temperature field → pathogen:** C.2's seasonal T̄ + amplitude writes the (currently constant) `temperature`
  field (terrain.py:616), which §4.6.3 `pathogen_mult` already consumes → seasonal disease for free.
- **Regime-shift → society morph:** the slow `regime(t)` shifts equilibrium density; the model periodically
  calls `society_from_character(density, surplus)` (§4.5.10) → `morph_to_society(...)` — i.e. **the regime layer
  is what finally pushes density across Binford packing and fires the morph hook** (currently inert).

## §6. Build steps (each tunable, nesting, gated)
- **C.1 — obliquity → seasonal (Layer 1).** Draw ε; map to A_seas (§1-B); wrap `season(t)` on the field.
  **GATE:** `A_seas=0.6 ⇔ s_min=0.4` reproduces **R-6 CC=37%**; `A_seas=0 ⇒ s(t)≡1.0 bit-exact` (baseline).
- **C.2 — eccentricity + flux (orbital draws complete).** e → interannual + `(1−e²)^−½` mean; S → seasonal T̄
  field (→ pathogen seasonality free). **GATE:** Earth (e=0.017,S=1) ≈ C.1; high-e/low-S shift as predicted.
- **C.3 — regime-shift (Layer 3).** Slow OU/excursion modulation; wire to the §4.5.10 morph trigger.
  **GATE:** a sustained warm excursion lifts density past Binford packing → a morph fires (the inert hook lives).
- **C.4 — catastrophe (Layer 4, §3).** Per-biome Poisson events; the resilience shock.
- **C.5 — water→aggregation coupling (§4).** Seasonal water field → aggregation.

## §7. Validation / gates
- **Earth recovers the baseline** (ε=23.4°,e=0.017,S=1; all amplitudes→0 ⇒ `M≡1` bit-exact) → 485 green
  (opt-in cfg). C.1 reproduces R-6 (CC=37% at A_seas=0.6).
- **Transfer functions monotone + bounded** to the habitable ranges (no snowball/runaway leakage).
- **§4.1.7 isolation:** climate touches ONLY the field multiplier (grep — no other write site).
- **Per-world determinism** (orbital draw from seed); temporal layers within-run.
- **C.3 morph gate:** the regime layer demonstrably fires a society transition (the payoff — the inert §4.5.10
  hook becomes live).

## §8. Open questions (resolved + remaining)
- **Q1 RESOLVED (B):** ε → empirical Earth §4.1.4 band, scaling dial (provisional heuristic).
- **Q2 RESOLVED:** cold/high-latitude = **caribou/herd crash** (Bergerud/Zalatan magnitude; Usher 2022 confound
  caveat) on migratory-game biomes — the gap is filled.
- **Q3 RESOLVED:** **uniform** draws over the (forager-sustainable) habitable range.
- **REMAINING Q4:** regime-shift amplitude/period calibration (±10–30% / 100–500 yr) — extract the Wanner/
  Mayewski numbers more precisely? **Q5:** flood catastrophe re-anchor (own source) or drop?

## §9. Red-team record
**v1 (2026-06-21, sub-agent) — APPROVE-WITH-FIXES, all applied** (physics verified: ε≈54° crossover,
`((1+e)/(1−e))²`, Kopparapu bounds, isolation, no live double-count): RT-4 pinned the forcing to the R-6
`s_min` form (A_seas≡1−s_min, C.1 gate); RT-1 corrected the Spiegel-2009 snowball mis-cite (→ heuristic label);
RT-5 volcanic −0.4 to −0.6°C (not 1–3°C); RT-5 flood double-book flagged; +S→T greenhouse offset, `(1−e²)^−½`,
per-biome φ, §4.1.5 threshold preservation.
**v2 NEEDS RE-RED-TEAM** — the NEW material (Layer-3 regime-shift, the caribou-crash catastrophe via the
ecology lit + Usher caveat, the water→aggregation coupling, the regime→morph wiring, the comprehensive tables)
has not been reviewed. Targets: is the regime-shift amplitude/period defensible (Wanner/Mayewski)? is the
caribou-crash magnitude (50–66%) honest given Usher's confound? does the regime→morph wiring stay §4.1.7-clean?
is the 4-layer product `M(t)` conservative/peak-normalized with no cross-layer double-count?

---

**Lit (in `literature/`):** Berger 1978 (Milankovitch), Spiegel 2009 (obliquity), Spiegel 2010 (eccentricity),
Kopparapu 2013 / Kasting 1993 (HZ flux), Timmermann 2018 / Cane 2005 (ENSO), Cook 2010 (megadrought), Sigl 2015
(volcanic), Wanner 2008 / Mayewski 2004 (Holocene/regime-shift), Usher 2022 (caribou-crisis confound caveat).
**To fetch:** caribou population-ecology (Bergerud; Zalatan 2006; Vors & Boyce 2009) for the crash magnitude/
cycle; a flood-catastrophe anchor; dryland ephemeral-stream % per biome (water-coupling). MODEL_SPEC §4.1.4–7
(seams), §4.3.2 (climate field), §4.5.10 (morph hooks), §4.6.3 (pathogen), R-6 (the seasonal anchor).
