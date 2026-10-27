# 02 — Benchmarks: what the model hits, what it misses, what it has never hit (2026-10-26)

**Two benchmark sets are scored.** (a) The **marker table** (`docs/MARKER_MATRIX.md`): the project's scorecard, each
marker with a verified anchor, a band, a unit and a statistic. (b) The **demography monitor** (`demography_health()` in
`sic_games/src/sic_games/demography.py`, anchors in `DEMOG_ANCHORS`): runs in every campaign snapshot. Some monitor
entries are a single Aché value with a tolerance; the code calls those a REPORTING threshold, "never a calibration
target" — they are scored here as the band [anchor·(1−tol), anchor·(1+tol)] and marked as such.

**Rule** (`tools/benchmark_history.py`): per run, the sustained-window mean (last 15% of rows); #18–#21 from the
period life table. Per world, mean ± SE over the runs; **PASS** = the 1-SE interval inside the band; **FAIL** = outside
it; **unresolved** = it straddles an edge. **History window:** five canons whose full-length runs are on disk —
Add.100 (2026-09-18, 1 run per world, no period table), Add.106 (09-22), Add.108 (09-24, + food-viable daughter
sites), Add.109 (09-24, + fathers' provisioning), Add.113 (09-26, + village granary and terrain risk as a 10% accident
share = TODAY; 3 runs per world each). RESULTS records older canons; "never hit" below means never in THIS window.

---

## 1. The categories

### ✅ HITS NOW — passes on all three worlds (24)
Marker table: **#3** village size (median) · **#4** connubium reach · **#10** polygyny · **#12** rank-size slope ·
**#13** primacy · **#14** material Gini (adults and within-camp) · **#16** dependency ratio, share under 15, sex ratio ·
**#18** e0 · **#19** survival to 15 · **#20** e15 · **#21** survival to 45.
Monitor: frac_child · dependency_ratio · sex_ratio_m_f · realised_e0 · e15 · e45 · surv_to_15 · surv_to_45 ·
modal_adult_death · age_first_birth_yr. **[Corrected after the external audit: `modal_adult_death` = 75 is an artifact of the 900-month lifespan cap — m(75) = 12/yr, l(76) = 0, ~10% of births die at exactly 75 (F-05, verified). Its "pass" is not evidence. The monitor rows (TFR, IBI, m(5–15), orphanhood) are cumulative from step 0, not period values (F-07, verified); for m(5–15) the period value agrees within 5%.]**
**Newly hit at Add.113** (failed on some world in every earlier canon): #19 and #21 (savanna and montane), the
monitor's surv_to_15 and surv_to_45, and #14 adults on temperate (was 0.42 at the band edge).

### ⚠️ PARTLY NOW — passes on one or two worlds (4)
- **#1 band size:** temperate 40.2 ± 1.6 unresolved (≤ 40); savanna, montane pass. Temperate unresolved since Add.108.
- **#17 fission ceiling:** temperate 232 ± 19 unresolved (≤ 250); savanna, montane pass. Same since Add.108.
- **monitor realised_ibi_med:** temperate 36.2 PASS, savanna 34.6 unresolved, montane 32.3 FAIL (band 34.4–49.4).
  Short on every world through Add.106; improving since.
- **monitor frac_motherless:** savanna in band; temperate and montane 0.033 above the reporting range (0.01–0.03).
  Rose from ~0.015 (Add.100–108) to ~0.03 at Add.113.

### ❌ MISSES NOW, HIT BEFORE (2)
- **monitor realised_tfr** (band 4.69–8.03, Hill & Hurtado Tables 8.1/8.2): in band on every world at Add.100 and
  Add.106 (temperate 4.7–4.9, savanna ~5.9, montane ~6.1). **Temperate fell below at Add.108 (4.21)**; **savanna and
  montane fell at Add.113 (5.9 → 4.58, 5.7 → 4.53).** The adoptions that raised survival lowered fertility. A possible
  reading — density-dependent fertility (`enable_density_fertility`, ON) compensating for lower mortality at a stationary
  population — is NOT measured.
- **monitor frac_fatherless** (reporting range 0.025–0.075): ~0.07 on every world through Add.109; **0.08 at Add.113**.

### 🚫 NEVER HIT in the window (1)
- **monitor m_5_15** (deaths per person-year at ages 5–15; Aché ~0.010, G&K p.330): 0.020–0.044 in every canon. It
  improved at Add.113 (savanna 0.040 → 0.028, montane 0.035 → 0.026) but is still 2–3× the anchor on every world.
  Note: #19 (survival to 15) passes because it is scored against the cross-forager BAND, not the Aché value.

### ▫️ NOT SCORED — no documented band, or report-only by a recorded decision (9)
| benchmark | why no verdict | record |
|---|---|---|
| #3 village size (max, Voronoi catchment) | the ceiling is scored at #17 on the co-residence unit | RESULTS Add.104 |
| #5 lineage dynamics | needs per-generation extinction/growth rates; the scorecard reports the lineage count only | MARKER_MATRIX #5 |
| #7 nobility share | no documented band (MARKER_MATRIX rule 2) | MARKER_MATRIX #7 |
| #8 fission rate | needs a per-large-village-year rate; the scorecard reports cumulative bud events only | MARKER_MATRIX #8 |
| #9 hierarchy ordering | a pre-registered CROSS-WORLD test on `gini_cred`, not a band | MARKER_MATRIX #9; RESULTS Add.99 |
| #11 status → reproductive success | NOT COMPARABLE: the model lacks the anchor's channel | RESULTS Add.102 |
| #15 orphanhood | a point (~0.02), no band | MARKER_MATRIX #15 |
| #16 median age | reported with #16, no band | MARKER_MATRIX #16 |
| monitor band_med_adults | the statistic was RETRACTED (Add.89); #1 uses the corrected one — the monitor is an instrument defect to fix | RESULTS Add.89, Add.114 |

---

## 2. Current values (Add.113 canon; temperate / savanna / montane)

| benchmark | value | band / anchor |
|---|---|---|
| #1 band size | 40.2 / 29.9 / 27.7 | Hill 2011 28.2, range ~12–40 |
| #3 village size median / max | 101 / 100 / 130 · max 350 / 305 / 546 | Alvard 50–250 |
| #4 connubium reach | 519 / 569 / 526 | Wobst ~475, floor 150 |
| #10 polygyny | 0.031 / 0.038 / 0.023 | Marlowe ~0.04 [0.02, 0.06] |
| #11 status→RS | 0.22 / 0.12 / 0.24 | not comparable |
| #12 rank-size slope / #13 primacy | −0.79 / −0.66 / −0.91 · 1.22 / 1.40 / 1.56 | ≈ −1 · ≈ 1 |
| #14 material Gini adults / within-camp | 0.41 / 0.38 / 0.38 · 0.31 / 0.30 / 0.28 | BHM 0.36 · Agta 0.23 [0–0.44] |
| #16 dependency / under-15 / sex ratio | 0.71 / 0.74 / 0.75 · 0.33 / 0.34 / 0.35 · 1.07 / 1.05 / 1.07 | H&H 1996 T4.4 bands |
| #17 fission ceiling | 232 / 119 / 103 | ≤ 250 (Alberti 158) |
| #18 e0 / #19 l(15) | 34.2 / 30.3 / 30.8 · 0.62 / 0.55 / 0.58 | 21–37 · 0.45–0.66 |
| #20 e15 / #21 l(45) | 37.3 / 35.9 / 34.8 · 0.39 / 0.33 / 0.33 | 28.6–42.5 · 0.26–0.43 |
| monitor TFR / IBI (months) | 4.05 / 4.58 / 4.53 · 36.2 / 34.6 / 32.3 | 4.69–8.03 · 34.4–49.4 |
| monitor m(5–15) | 0.022 / 0.028 / 0.026 | Aché ~0.010 |
| monitor motherless / fatherless | 0.033 / 0.029 / 0.032 · 0.084 / 0.084 / 0.079 | Aché ~0.02 · ~0.05 |

Full numbers with SE and per-seed values: `docs/evidence/scorecard_add113_canon.json` and the figure
`docs/evidence/scorecard_add113_canon.png` (current canon in colour, Add.109 in grey).

---

## 3. The full history table (generated)

Cell = temperate · savanna · montane: ✅ PASS · ⚠️ unresolved · ❌ FAIL · ▫️ no verdict · · no data (Add.100 has no
period life table).

| benchmark | band | Add.100 | Add.106 | Add.108 | Add.109 | Add.113 | category |
|---|---|---|---|---|---|---|---|
| #3 village size (median) | [50, 250] | ✅❌✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #4 connubium reach (median) | [150, ] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #10 polygyny (of ALL men) | [0.02, 0.06] | ✅❌✅ | ✅✅⚠️ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #12 rank-size slope | [-1.5, -0.6] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #13 primacy | [1, 2] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #14 material Gini (adults) | [0.3, 0.42] | ❌✅✅ | ❌✅✅ | ⚠️✅✅ | ⚠️✅✅ | ✅✅✅ | **HITS NOW** |
| #14 material Gini (within-cell) | [0, 0.44] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #16 dependency ratio | [0.598, 0.899] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #16 share under 15 | [0.287, 0.454] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #16 sex ratio (m/f) | [0.896, 1.37] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #18 e0 (period) | [21, 37] | · | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #19 survival to 15 (period) | [0.45, 0.66] | · | ✅⚠️❌ | ✅❌❌ | ✅❌✅ | ✅✅✅ | **HITS NOW** |
| #20 e15 (period) | [28.6, 42.5] | · | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #21 survival to 45 from birth (period) | [0.26, 0.43] | · | ✅⚠️❌ | ✅❌❌ | ✅⚠️❌ | ✅✅✅ | **HITS NOW** |
| monitor: frac_child | [0.287, 0.454] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| monitor: dependency_ratio | [0.598, 0.899] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| monitor: sex_ratio_m_f | [0.896, 1.37] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| monitor: realised_e0 | [21, 37] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| monitor: e15 | [30.8, 46.2] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| monitor: e45 | [15.8, 26.4] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| monitor: surv_to_15 | [0.528, 0.792] | ✅❌❌ | ✅❌❌ | ✅❌❌ | ✅❌❌ | ✅✅✅ | **HITS NOW** |
| monitor: surv_to_45 | [0.323, 0.537] | ❌❌❌ | ❌❌❌ | ✅❌❌ | ✅❌❌ | ✅✅✅ | **HITS NOW** |
| monitor: modal_adult_death | [68, 78] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| monitor: age_first_birth_yr | [16.2, 20.5] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | **HITS NOW** |
| #1 band size (mean-experienced adults/cell) | [12, 40] | ✅✅✅ | ✅✅✅ | ⚠️✅✅ | ⚠️✅✅ | ⚠️✅✅ | **PARTLY NOW** |
| #17 fission ceiling (co-resident max) | [, 250] | ✅✅✅ | ✅✅✅ | ⚠️✅✅ | ⚠️✅✅ | ⚠️✅✅ | **PARTLY NOW** |
| monitor: realised_ibi_med | [34.4, 49.4] | ❌❌❌ | ❌❌❌ | ⚠️❌❌ | ⚠️❌❌ | ✅⚠️❌ | **PARTLY NOW** |
| monitor: frac_motherless | [0.01, 0.03] | ✅✅✅ | ✅✅✅ | ✅✅⚠️ | ✅✅✅ | ❌✅❌ | **PARTLY NOW** |
| monitor: realised_tfr | [4.69, 8.03] | ✅✅✅ | ✅✅✅ | ❌✅✅ | ❌✅✅ | ❌❌❌ | **MISSES NOW, HIT BEFORE** |
| monitor: frac_fatherless | [0.025, 0.075] | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ❌❌❌ | **MISSES NOW, HIT BEFORE** |
| monitor: m_5_15 | [0.005, 0.015] | ❌❌❌ | ❌❌❌ | ❌❌❌ | ❌❌❌ | ❌❌❌ | **NEVER HIT (in window)** |
| #3 village size (max, Voronoi catchment) | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| #5 lineages (count; dynamics per MARKER_MATRIX) | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| #7 nobility share | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| #8 bud events (cumulative; rate per MARKER_MATRIX) | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| #9 hierarchy index gini_cred | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| #11 status->RS (age-controlled) | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| #15 orphanhood (motherless) | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| #16 median age (yr) | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |
| monitor: band_med_adults | — | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | ▫️▫️▫️ | **NOT SCORED** |

