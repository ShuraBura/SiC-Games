# SiC Games — Benchmarks (BENCHMARKS.md)

**Purpose:** the **quantitative empirical standards matrix** — the ethnographic/archaeological values the model is calibrated to and validated against. This is the "training set" for the reduced-order / benchmark-anchored approach (supervisor, 2026-07-04): condition → canonical configuration, with agent dynamics evolving the *deviations*. See the methodological note (§ end).

**Homes (charter §):** *bibliography of record* = `LITERATURE.md` (citations + what-was-lifted); *model constants* = `PARAMETERS.md` (values used in code); *qualitative aspirations* = `TARGETS.md`. This doc holds the **empirical target values + our-unit conversions + model-current + verification status** in one place. Correct a value in `LITERATURE.md` first (the source), then here.

**Cell = 100 km² (10×10 km).** Density in persons/km² and persons/cell (=persons/100 km²). `[VERIFIED]` = extracted from a filed PDF; `[filed]` = PDF present, value conceptual; `[cited]` = from a source not locally filed.

---

## 1. Population density (regional)

| Economy | Empirical | persons/cell | Source | Status |
|---|---|---|---|---|
| Mobile HG (all) | 0.2–495 /100 km², **median 11.9** | 0.2–495, med **11.9** | Tallavaara (Binford+Kelly data) | [VERIFIED] |
| Mobile HG (typical arid–temperate) | ~0.01–0.5 /km² | ~1–50 | Binford 2001; Kelly | [cited] |
| **Binford PACKING threshold** | **0.091 /km²** | **9.1** | Binford 2001 | [VERIFIED] |
| Complex foragers (NW Coast, Calusa, Chumash) | ~0.5–5 /km² | ~50–500 | Kroeber; Ames 1994 (coast pop ~188,000) | [VERIFIED]-partial (pop ✓; per-km² cited) |
| Swidden / horticultural | ~1–30 /km² | ~100–3000 | Conklin; Boserup 1965 (book, unfiled) | [cited] |
| Intensive agriculture | ~50–1000+ /km² | ~5000+ | Boserup 1965 (unfiled) | [cited] |

**Model-current:** equilibrium ~0.015/km² (~1.5/cell) on the mobile-forager substrate (R-51) — at the arid-lower end, ~6× below packing (the R-51 saturation gap).

## 2. Settlement / village size (residents)

| Unit | Empirical | Source | Status |
|---|---|---|---|
| Foraging BAND (fission unit) | **~25** (Birdsell horde ~40; Wobst) | Birdsell 1953/68; Wobst 1974 | [VERIFIED] |
| Connubium / dialect tribe | ~500 (contested) | Birdsell 1968; Wobst | [VERIFIED, contested] |
| Aggregation camp / Natufian hamlet | dozens–~150 | Bar-Yosef & Belfer-Cohen (unfiled) | [cited] |
| **Complex-forager VILLAGE (NW Coast)** | **"a few score to over a thousand"** (~40–1000+) | Ames 1994 | [VERIFIED] |
| Scalar-stress onset (fission pressure) | p=0.5 at **N≈127** (logistic width ≈6) | Alberti 2014; Johnson 1982 | [VERIFIED] |

**Model-current:** emergent bands ~25 (matches); discrete-settlement villages held ~110 (R-52); agglomeration optimal size `n*` to be set ~100–300.

## 3. Catchment / ranging

| Quantity | Empirical | our cells (10 km) | Source | Status |
|---|---|---|---|---|
| **Agricultural site catchment** | **5 km radius** (return declines beyond 3–4 km) | **radius ~0–1** | Vita-Finzi & Higgs 1970 | [VERIFIED] |
| **HG site catchment** | **10 km radius** (2-hour perimeter) | **radius ~1** | Vita-Finzi & Higgs 1970 | [VERIFIED] |
| Band annual range | ~100s–1000s km² | — | Kelly; Wobst | [cited] |

**Model-current:** `settle_catchment_radius = 2` (~20 km) — **ABOVE the HG value, 2× the farm value → correction: trim to 1** (Vita-Finzi).

## 4. Agglomeration (returns-to-co-location)

| Quantity | Empirical | Source | Status |
|---|---|---|---|
| **Super-linear socioeconomic exponent β** | **≈1.15** (emp. GMP 1.126±0.023; theor. 7/6) | Bettencourt 2013 | [VERIFIED] (MODERN cities — cross-domain borrowing) |
| Sub-linear infrastructure exponent | ≈0.85 (0.849±0.038; theor. 5/6) | Bettencourt 2013 | [VERIFIED] |

**Model-current:** P0 provisional α=1.5 → **correction: re-anchor to ~1.15** (the measured floor; subsistence α may be sharper — a testable prediction, not a fitted value).

## 5. Storage / complexity onset

| Quantity | Empirical | Source | Status |
|---|---|---|---|
| Storage-obligatory threshold | Effective Temperature **ET = 15.25 °C** | Binford 2001 | [VERIFIED] |
| Delayed-return → inequality | salmon/acorn storage → sedentism + density + ranking | Testart 1982; Woodburn 1982; Ames 1994 | [VERIFIED] |
| Economic defensibility | defend iff resource **dense × predictable** | Dyson-Hudson & Smith 1978 | [VERIFIED] (concept) |
| Swidden crop→fallow rotation | short crop, long fallow (durations system-specific) | Conklin 1961 | [filed] (concept) |
| Inter-annual climate variance (shock) | ENSO/PDO multi-year regimes | Timmermann 2018; Cane 2005 | [filed] |

---

## Two calibration corrections the benchmark pass produced
1. **`settle_catchment_radius`: 2 → 1** (Vita-Finzi 5–10 km catchment ≈ radius 1 in 10 km cells).
2. **Agglomeration α: 1.5 → ~1.15** (Bettencourt measured exponent; P0 re-anchor).

## Methodological note — the reduced-order framing
The rows above form a **condition × observable matrix** `M`. The plan (supervisor 2026-07-04): SVD/eigendecompose `M` → a few **characteristic modes** (expected ~2–3: productivity / storability / aridity) → project a local condition → its **canonical configuration** (village size, density, catchment) cheaply; agents evolve the **deviations** (aggregation onset, swidden bust, Carneiro). This is honest reduced-order modelling: the model is a low-parameter *generative re-expression* of these benchmarks (ML framing — architecture = mechanisms, parameters = these values, generalization = the emergent transitions). Discipline: **free parameters < independent benchmark rows** (compression); hold-out where the corpus allows.

---

*End of BENCHMARKS — seeded 2026-07-05. Values sourced in LITERATURE.md; corrections flow to PARAMETERS.md.*
