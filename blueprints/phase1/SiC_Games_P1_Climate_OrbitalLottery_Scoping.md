# SiC Games · Phase 1 · **Climate — orbital-lottery variability** (+ catastrophe seam) — Scoping

**Status:** SCOPING for red-team (2026-06-21). Builds the §4.1.6 star-mechanics seam + §4.1.7 catastrophe stub
into a live, lit-anchored climate-forcing stage. **Discipline (locked, §4.1.6):** stellar mechanics *bound the
parameter draws*; they do **NOT** run tick-by-tick (no insolation→NPP transfer function in the agent loop).
Supervisor scope: **full (ε, e, S) trio, in 2 verified steps** (obliquity→seasonal first, then add e/S); one
orbital draw **per world/run** with temporal variability layered on top; **catastrophe = a separate later step**.

---

## 1. The two-stage per-world lottery

**Stage 1 — draw orbital/stellar parameters** from habitability-bounded ranges (the star lottery):
- **obliquity ε** (axial tilt) ∈ ~[0°, 60°] as a **conservative habitable-relevant envelope** (RT-1 fix:
  Spiegel 2009 actually finds habitability across a *broad* obliquity band with **no clean monotone
  obliquity→snowball threshold** — snowball susceptibility keys on ocean fraction + CO₂, not a tidy ε limit;
  the equator-freezes-at-high-ε intuition is Williams & Kasting 1997, not Spiegel). Earth ε=23.4°.
- **eccentricity e** ∈ ~[0, 0.6], **upper third marginal** (Spiegel 2010: habitability is sharply cut at the
  snowball transition for 0.4<e<0.6) → favor a weighted/Earth-leaning prior over uniform (Q3). Earth e=0.017.
- **stellar flux S** ∈ ~[0.34, 1.05] S⊕ (Kopparapu 2013 verified: max-greenhouse outer **0.344**, moist/runaway
  inner **1.014–1.051**). Earth = 1.0.

**Stage 2 — map orbital → climate-forcing parameters** (lit *bounds* not tick-transfer; the ε→amplitude map is
a **bounding HEURISTIC, PROVISIONAL** — it sets *where in the Earth range* a world sits, it does NOT compute
forage amplitude from insolation [forage amplitude is rain/phenology-driven, §4.1.4], RT-1):
- **ε → seasonal amplitude A_seas.** Insolation contrast rises ∝ ~sin ε, monotone until **ε≈54°** (verified:
  pole/equator annual-insolation ratio crosses 1.0 at 54.0° — poles then out-heat the equator). An assumed
  monotone map of ε onto the **Earth-anchored §4.1.4 range** (forest≈flat ↔ llanos≈0.5–0.7 drawdown); Earth
  ε=23.4° → mid-range. *Step 1.*
- **e → intra-annual flux asymmetry + a high-e mean brightening.** Perihelion/aphelion swing = `((1+e)/(1−e))²`
  (verified: e=0.017→1.07, e=0.3→3.45) — **intra**-annual (interannual only via precession, correctly hedged);
  AND fold the **annual-mean brightening ∝ (1−e²)^(−½)** (Spiegel 2010; +25% at e=0.6, negligible at Earth)
  into mean-T/CC. *Step 2.*
- **S → mean temperature.** `T_eff ∝ S^¼` (equilibrium) is ~33 K BELOW surface temp (RT-3) — so **anchor S=1 →
  14°C (§4.3.2 placeholder) and scale ΔT from there** (an effective greenhouse offset), so the pathogen channel
  (§4.6.3, keyed on *surface* T) gets a plausible surface temperature, not the bare effective temp. *Step 2.*

## 2. The forcing application (the field wrapper, §4.1.7-isolated)

A **time-varying multiplier on the carrying-capacity field** (`harvest_field`) — the R-6 `run_2d` wrapper
pattern, NOT a model-internal change. **The form is PINNED to the validated R-6 envelope (RT-4 fix):**
`s(t) = s_min + (1−s_min)·½(1+cos(2πt/12 − φ))` — range **[s_min, 1], peak-normalized to 1.0** — with the
lottery setting the **amplitude `A_seas ≡ 1 − s_min`** (NOT a "1+A·season" boost-above-ceiling, which would
*not* reproduce R-6's lean-season-bottleneck mechanism). **C.1 acceptance test (exact): `A_seas=0.6 ⇔
s_min=0.4` must reproduce R-6's CC = 37%**, and `A_seas=0 ⇔ s_min=1 ⇒ s(t)≡1.0 exactly` (aseasonal baseline,
bit-for-bit — mirror the harness `s_min=1.0 → season()≡1.0`). Per-biome curve *shape* AND **phase φ** stay the
§4.1.4/5 forms — **the lottery sets the world AMPLITUDE; the biome keeps its SHAPE + PHASE** (RT-7: forest
fat-season vs llanos wet-season are opposite-signed lean seasons — don't force one hemisphere's calendar; and
the §4.1.5 game *threshold*-access mechanism must NOT be smoothed into a sine by the amplitude knob). Interannual
(e) and mean-T (S) layer in C.2; catastrophe (§3) multiplies on top later. §4.1.6 contract.

## 3. Build steps (each tunable, nesting, gated)
- **Step C.1 — obliquity → seasonal amplitude lottery.** Draw ε per world; map to A_seas; wrap a seasonal
  multiplier on the field. **Verify:** Earth ε → the validated forest-flat / llanos-high amplitudes (R-6);
  amplitude=0 (ε→low) reproduces the aseasonal baseline exactly. *(Supervisor: verify before adding e/S.)*
- **Step C.2 — add eccentricity + flux.** e → interannual term + asymmetry; S → mean T (climate-seam field) +
  biome. **Verify:** Earth (e≈0.017, S=1) ≈ C.1 (e/S negligible); high-e/low-S shift amplitude/T as predicted.
- **Step C.3 (SEPARATE, later) — catastrophe seam (§4).**

## 4. Catastrophe step — per-biome lit-anchorage assessment (the supervisor's question)

**Is there enough lit to define catastrophes PER BIOME, with effects + rates? PARTIALLY — solid for the major
types, thin for cold/high-latitude.** Survey:

| biome / setting | catastrophe | amplitude (CC drop) | recurrence | lit anchor |
|---|---|---|---|---|
| arid / grass / temperate flats | **megadrought** | duration anchored, **decadal–multidecadal**; the 30–60% CC-drop is INTERPRETIVE (not a Cook number) | centennial–millennial (~0.1–0.5%/yr) | **Cook 2010** (NA Drought Atlas; Medieval megadroughts) |
| tropical forest | **drought + wildfire** (ENSO) | 20–40% | ENSO 2–7 yr | **Timmermann 2018; Cane 2005** |
| ALL biomes (global) | **volcanic cooling** | **common events −0.3 to −0.6°C** (Sigl: 19 largest CE tropical −0.6±0.2°C); **1–3°C only for the rare VEI7 tail** (Tambora/Samalas) | significant ~1%/yr; VEI7 ~millennial | **Sigl 2015** |
| llanos / savanna (wet-season) | **flood** (access loss) | **NEEDS ITS OWN ANCHOR** — the Hurtado & Hill caiman 44→489 swing is the llanos seasonal-SHAPE datum (§4.1.4), reusing it as a flood-CATASTROPHE magnitude double-books it (RT-5) → drop or re-anchor | — | (re-anchor needed) |
| high-latitude / tundra / mountain | **blizzard / cold-snap / freeze** | — | — | **GAP — no source in repo lit** (RT-5 confirmed) |

**⇒ Catastrophe design (C.3):** a per-biome **Poisson event** with (type, amplitude, duration, rate). Honestly
anchored: **megadrought (Cook, duration only — CC-drop interpretive), volcanic (Sigl, ~0.3–0.6°C common /
1–3°C VEI7-tail), ENSO-drought (Timmermann)**. **Flood needs its own anchor** (don't reuse the §4.1.4 caiman
datum); **blizzard/cold is a lit gap** — fetch a source or omit (Q2). The resilience-test design point (R-16/
R-18: push the band below K) = a **~40–50% CC drop sustained a few years** (megadrought-scale). Implemented as
the §4.1.7 amplitude modifier on the field — **isolated** (writes only to the field wrapper, nothing else).

## 5. Validation / gates
- **Earth recovers the baseline:** (ε=23.4°, e=0.017, S=1) reproduces the validated forest-flat/llanos-high
  seasonality (R-6) and e/S negligible; amplitude→0 = aseasonal baseline exact. 485 green throughout (opt-in).
- **Transfer functions monotone + bounded** to the habitable ranges (no snowball/runaway leakage).
- **Field-wrapper isolation** (§4.1.7): the climate forcing touches ONLY the harvest field multiplier; the
  demographic substrate is unchanged code (just reads a time-varying field) → no R-3/R-17 regression.
- **One draw per world** (deterministic from seed); the temporal layers (seasonal/interannual) are within-run.

## 6. Red-team targets (fresh repo-grounded sub-agent)
RT-1: the **ε→A_seas mapping** — is `sin ε`-scaling onto the §4.1.4 Earth range defensible, and are the
habitable ε bounds (snowball limits) right per Spiegel 2009? RT-2: **e→interannual** — is `((1+e)/(1−e))²` the
right flux-swing, and does eccentricity belong as *interannual* vs *intra-annual asymmetry* (precession
dependence)? RT-3: **S→T** — `T∝S^¼` equilibrium vs the climate-seam field's role (pathogen channel); does
changing S need a biome re-derivation? RT-4: **field-wrapper isolation** — does the multiplier truly stay out
of the model loop (§4.1.7), reproducing R-6's seasonal result, with no double-count vs the existing `s_min`?
RT-5: **per-biome catastrophe** — is the table's lit-anchoring honest (esp. the cold-gap), and are the
amplitudes/rates defensible? RT-6: **scope/nesting** — is C.1→C.2→C.3 right; does Earth-config reproduce the
baseline bit-for-bit at amplitude 0? RT-7: anything missed (Milankovitch long-term drift? the s_min legacy
test value? the seasonal phase per hemisphere?).

## 7. Open questions for the supervisor
- **Q1:** ε→A_seas — map onto the **Earth §4.1.4 range** (forest-flat↔llanos-high), so Earth ε sits mid-range?
- **Q2:** Catastrophe **cold/blizzard gap** — fetch a high-latitude catastrophe source, or omit that biome's
  catastrophe for now (megadrought/flood/volcanic/ENSO cover the rest)?
- **Q3:** Lottery **distribution** — uniform over the habitable range, or weighted toward Earth-like (a
  realistic prior)?

---

## 8. Red-team record (2026-06-21, fresh repo-grounded sub-agent) — VERDICT: APPROVE-WITH-FIXES (applied)

Physics verified correct: **ε≈54° crossover** (integrated to 54.0°), **`((1+e)/(1−e))²`** swing math, **Kopparapu
flux bounds** (0.344 outer / 1.014–1.051 inner), the intra-vs-interannual eccentricity hedge, the field-wrapper
**isolation discipline matches the run_2d code**, and **no live double-count** (`s_min` exists only in the opt-in
harness, not the core model — core T/humidity are constant placeholders per §4.3.2). Four MAJORs, all fixed in
the design:
- **[MAJOR→fixed] RT-4 forcing form:** the proposed `M(t)=1+A·season` ≠ the validated R-6 `s_min+(1−s_min)·½(1+cos)`
  (peak-normalized [s_min,1]) → "reproduces R-6" wasn't guaranteed. **Pinned `A_seas ≡ 1−s_min`; C.1 gate =
  A_seas=0.6 ⇔ s_min=0.4 ⇒ R-6's CC=37%; A_seas=0 ⇒ s(t)≡1.0 bit-exact** (§2). *The load-bearing fix.*
- **[MAJOR→fixed] RT-1 Spiegel mis-cite:** Spiegel 2009 *refutes* a monotone obliquity→snowball threshold
  (snowball keys on ocean/CO₂, not ε); the equator-freeze intuition is Williams & Kasting 1997. Restated ε∈[0,60°]
  as a conservative envelope; the ε→amplitude map labeled a **PROVISIONAL bounding heuristic**, not a transfer
  function (§1).
- **[MAJOR→fixed] RT-5 volcanic magnitude:** "1–3°C" overstates Sigl 2015's **−0.4 to −0.6°C** for the ~1%/yr
  events (amplitude/rate were mismatched to one source). Split: ~0.3–0.6°C common, 1–3°C VEI7-tail (§4).
- **[MAJOR→fixed] RT-5 flood double-book:** the Hurtado & Hill caiman 44→489 datum is the llanos seasonal-SHAPE
  anchor (§4.1.4), not an independent flood-catastrophe magnitude → flagged "needs its own anchor or drop" (§4).
- **[MINOR→fixed]** RT-3 `T∝S^¼` is ~33 K below surface T → anchor S=1→14°C, scale ΔT (§1); RT-2 fold the
  `(1−e²)^−½` annual-mean brightening at high e (§1); RT-7 keep per-biome **phase φ** + the §4.1.5 game
  **threshold-vs-smooth** distinction intact under the amplitude knob (§2); Milankovitch correctly out of scope.
- **[honest, confirmed]** the **cold/blizzard catastrophe is a genuine lit gap** (no high-latitude source in
  `literature/`) — fill or omit (Q2).

**Net:** 4 MAJORs resolved in design; no BLOCKER. Build order (§3) stands: C.1 (obliquity→seasonal, gated on
R-6) → C.2 (e/S) → C.3 (catastrophe).

---

**Lit (in `literature/`):** Berger 1978 (insolation/Milankovitch formalism), Spiegel 2009 (obliquity→
seasonality + snowball bounds), Spiegel 2010 (eccentricity, habitable to high e), Kopparapu 2013 / Kasting 1993
(HZ flux bounds), Timmermann 2018 / Cane 2005 (ENSO), Cook 2010 (megadrought), Sigl 2015 (volcanic), Wanner
2008 / Mayewski 2004 (Holocene variability). MODEL_SPEC §4.1.4–4.1.7 (the seams), §4.3.2 (climate field), R-6
(the validated seasonal result the wrapper must reproduce).
