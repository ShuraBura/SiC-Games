# The Benchmark Ladder — validate in the order things evolved

**Adopted 2026-08-07 by the supervisor.** Benchmark behavioural groups in the order they appear in
evolution, not in order of size, novelty, or how interesting the result would be.

**Why.** Every tier of this model is causally downstream of the ones beneath it. Band size depends on
movement, which depends on the energy economy. Surplus depends on storage, which depends on seasonality.
Stratification depends on surplus. Validating a high tier while a low one is unverified is calibrating on
sand: the number you fit absorbs the error underneath it, and the fit looks good until the foundation moves.

**How this changed a decision the day it was written.** The `noble_*_lift` family was proposed as the next
CTB target because it was the largest uncovered block — nine diagnostics carrying the whole stratification
story. It is **tier 12, the top of the ladder**. Meanwhile the two known model failures sit at **tier 3**
(age structure carrying too many children) and **tier 5** (`band_med` 11.8 adults against Hill's 28.2). Any
elite-layer result validated now would be validated on a demographic base we already know is wrong.
Size was the wrong criterion; depth is the right one.

**UPDATE 2026-09-12 (R-106, RESULTS Addenda 76–81) — the two "known failures" are resolved.**
- **Tier 3 is RE-SCORED PASS.** On current canon (low-noise 3-world panel, period 400–800) every temperate
  age-structure marker is inside its forager anchor band: frac_child 0.37, dependency 0.81, TFR 5.5, e0 36.3,
  survival-to-15 0.61; savanna is in-band on frac_child/TFR/e0 with dependency (0.95) and survival (0.44)
  marginally out on the harsh-biome side. The "age structure carrying too many children" fault is stale — closed
  by the mechanisms adopted since (metabolic down-regulation and others). The run is near-stationary (r ≈ +1 %/yr)
  and GK07 iso-growth consistent (Addendum 81).
- **Tier 5 band size is RE-SCORED — NO DEFICIT (R-106 Add.89, 2026-09-16).** The apparent miss (`band_med_adults`
  ≈ 10.5 vs 28.2) was the wrong STATISTIC and the wrong UNIT. Hill's 28.2 is the PERSON-WEIGHTED "mean experienced"
  adult band size (verbatim), not a median; and Hill's "band" is a RESIDENTIAL group (a camp), which is the model's
  CELL (the co-residence unit: leveling coalition is `by_cell`, consumption is per-cell), not `band_id` (a ~8-cell
  affiliation). Measured with Hill's statistic on the model's co-residence unit, the mean-experienced adult band size
  is **33 temperate / 23 savanna ≈ Hill 28.2** (inside the per-society range ~12–40). The model reproduces Hill-scale
  camps. RETRACTED: Add.80's "structural packing limit, not fixable" — its sub-findings hold (the `band_id`-median
  does not reach 28.2, and cohesion/food/repulsion do not move it) but they chased a mis-specified target, so tier-5
  is not a genuine miss. `scratchpad/bp_bandsize_unit.py`.

---

## The rule

> **A tier may be benchmarked when every tier beneath it is validated.**
> A result from an unvalidated lower tier is provisional no matter how carefully the upper tier was measured.

Three corollaries, each earned:

- **A failure at tier N is diagnosed at tier N or below, never above.** `band_med` (tier 5) failing does not
  license a fix in settlement (tier 9); look down, not up.
- **An anchor verified is not a mechanism validated.** Hawkes' 518/745 kcal/hr was verified against the paper
  on 2026-08-06 (Addendum 29). The code consuming it has never been checked against a constructed case. Those
  are different claims and the ladder tracks them separately.
- **CTB before benchmark.** A tier's diagnostics are validated against constructed truth before the tier's
  numbers are compared to literature. Three of the last four "findings" in this project were instrument
  defects (Addenda 24/25, 31).

---

## The ladder

Coverage measured 2026-08-07. **"tested"** counts mechanisms named in any test; **"CTB"** counts those named
in a file whose NAME marks it constructed-truth (`*_ctb.py`, `*_ground_truth.py`).

**⚠ THE CTB COLUMN UNDERCOUNTS, and the error was found the same night it was written.** It is a filename
heuristic, and genuine constructed-truth tests live in ordinarily-named files —
`test_bands.py::test_bands_method_connected_components` hand-places five agents at known positions and asserts
`bands()` returns the partition `[1, 2, 2]`, which is textbook CTB in a file the heuristic scores as zero.

The direction of the error is known (it can only undercount) and it is roughly uniform across tiers, so the
ORDERING the ladder prescribes is unaffected. But no tier should be called "uncovered" on this column alone —
read it as "has no dedicated CTB file", not as "has never been checked against a constructed case".

| # | tier | mechs | tested | CTB | primary anchors | markers scored here |
|---|---|---|---|---|---|---|
| 1 | **Physical world** — terrain, climate, soil, water | 13 | 11 | 2 | Timmermann 2018, Wanner 2008, Sarmiento 2004, St. John 2022, Berger 1978, Spiegel 2009/10, Kopparapu 2013, Lieth (Miami NPP), Tallavaara 2018 | — |
| 2 | **Energetics** — forage/game return, storage, shock | 8 | 7 | **0** | Hawkes 1991 (518/745 kcal·hr⁻¹), Hill 1987 (forest 5,541), Hurtado & Hill 1987 (grassland 3,001), Bird 1997 (intertidal), Testart 1982 (storage) | — |
| 3 | **Demography** — mortality, fertility, orphanhood | 8 | 8 | 1 | Gurven & Kaplan 2007 (Siler), Hill & Hurtado 1996 (sex split; Table 13.1 orphan), Pelletier 2009 | #15 orphanhood ✓, #16 engine; **age structure PASS (R-106 Add.81)** |
| 4 | **Movement** — mobility, packing, site choice | 3 | 2 | **0** | Kelly / Binford mobility bands | — |
| 5 | **Bands** — grouping, cohesion, assabiyah, fission | 9 | 9 | **0** | **Hill et al. 2011 (28.2 ADULTS)**, Birdsell 1953 (~25), Marlowe (25–50) | **#1 band size — NO DEFICIT: re-scored 33/23 ≈ 28.2 on the mean-experienced statistic + the cell (co-residence) unit (R-106 Add.89); the old "miss" was median-over-band_id, wrong statistic + wrong unit** |
| 6 | **Family** — pair bonds, paternity, polygyny | 3 | 3 | **0** | Marlowe *The Hadza* (polygyny ~0.04), von Rueden & Jaeggi | #10 polygyny ✓ |
| 7 | **Kin & lineage** — descent, exogamy, genome | 7 | 7 | 1 | **none at forager scale** (#6 retired 2026-08-07; #5 anchor withdrawn) | #5 not scoreable, ~~#6 retired~~ |
| 8 | **Connubium** — between-band mating networks | 2 | 2 | **0** | White 2017 (MVP), Wobst 1974 (MES 79–332) | #4 connubium 15/25 |
| 9 | **Settlement** — sedentism, villages, budding, agriculture | 10 | 9 | **0** | Alvard 2009 (50–250), Alberti 2014 (127 / 158), Hamilton 2007 (165), Bandy 2004 (fission rate), Johnson (rank-size) | #3 ✓ 46/52, #8 ✓, #12, #13, **#17 fission ceiling — MISSES** |
| 10 | **Surplus & material** — wealth, status, obligation | 6 | 4 | **0** | BHM 2009 Table S5 (HG material Gini **0.36**, age-adjusted ADULTS) | #11 status→RS, **#14 wealth — MET on the corrected marker: `material_gini_adults` 0.386 temp / 0.357 sav ≈ 0.36 (R-106 Add.92). Bands re-calibrated to the ADULTS statistic (lt3.0/ft4.0); tier-11 intact, corr(cred,mat) +0.26/+0.16** |
| 11 | **Stratification** — morph, rank, the inequality gate | 4 | 4 | **0** | Hayden 1995 Fig. 6, Smith & Codding 2021 (r = 0.881) | #9 hierarchy 2 of 3 |
| 12 | **Elite** — leveling, legitimacy, tribute, nobility | 9 | 9 | 1 | EA "true-elite few %" — **undocumented** | #7 not scored (no band in `docs/`) |

**Read the CTB column downward.** It is 2, then zero, and stays near zero all the way up. Only tier 1 has real
constructed-truth coverage, and that is an accident of where the work happened to land on 2026-08-06.

---

## What "validated" means at a rung

A tier is validated when **all four** hold. Anything less is stated as partial, not rounded up.

1. **Reachable.** Every mechanism in the tier can act in at least one world we actually run. An empty mask or
   a clock longer than the run makes a mechanism inert while it reads as ON — see `ClimateField.health()`'s
   `UNREACHABLE` / `NEVER-FIRED` verdicts, which found three dark channels on their first real run.
2. **Live, not fake-on.** No flag is on with its magnitude at neutral. Enforced by `runconfig.dead_flags()`,
   which halts a run rather than letting it report a mechanism it is not running.
3. **Diagnostics CTB'd.** Every diagnostic the tier's markers read has been measured against a constructed
   population whose answer is known. **This is the gate that is almost entirely unmet above tier 1.**
4. **Markers scored, with the unit stated.** Compared to a verified anchor, on the anchor's own quantity and
   unit. Four separate failures in this project were a real number read against the wrong denominator, unit,
   or statistic — never a wrong number.

---

## Tier membership

Assigned 2026-08-07. Where a mechanism could sit in two tiers it is placed at the **lowest** one it depends
on, because the ladder is about prerequisites rather than about subject matter.

- **1 Physical world** — `climate_lottery`, `seasonality`, `biome_seasonality`, `eccentricity_mean`, `interannual`, `regime_shift`,
  `caribou_swing`, `llanos_flood`, `intercept_hunting`, `terrain_risk`, `terrain_move_cost`, `soil_depletion`,
  `alluvial_renewal`, `resource_storability`, `catchment_depletion`, `village_density_disease`
- **2 Energetics** — `game`, `biome_meat_frac`, `biome_meat_cv`, `forage_cap`, `provisioning`, `band_provisioning`,
  `nutrition_synergy`, `condition`, `store_anchor`, `storage`, `storage_seasonal_union`, `tier2_shock`,
  `energetic_fertility`, `intake_fertility`, `need_weighted_shares`, `eta_weighted_shares`
- **3 Demography** — `orphan_mortality`, `density_disease`, `density_reference`, `society_regional_density`, `terrain_pathogen`, `dependent_load`, `synergy_age_grade`, `density_fertility`,
  `sedentism_fertility`, `energetic_refractory`, `life_history`, `malnutrition_fission`, `metabolic_downreg`,
  `fertility_restraint_gene`, `restraint_group_transmission`, `heritable_density_response`, `sub_k_regulation`
- **4 Movement** — `landscape_packing`, `site_appraisal`, `productivity_mobility`, `hunger_dispersal`, `founding_delay`
- **5 Bands** — `band_affiliation`, `dynamic_bands`, `band_family_knobs`, `emergent_band_size`,
  `leader_coherence`, `size_repulsion`, `resource_directed_fusion`, `leaky_assabiyah`,
  `marriage_aggregation`, `aggregation_sedentism`
- **6 Family** — `pair_bonds`, `bonded_mating`, `paternity`
- **7 Kin & lineage** — `genome`, `genealogy_log`, `lineage_branching`, `lineage_split`, `exogamy`,
  `local_ascription`
- **8 Connubium** — `adaptive_connubium`, `ascribed_mate_choice`
- **9 Settlement** — `village_budding`, `village_scaling`, `bud_hazard`, `settlement_scalar_stress`,
  `catchment_ceiling`, `agglomeration`, `aggl_ceiling`, `emergent_abandonment`,
  `economic_defensibility`, `improved_land`, `agriculture`, `emergent_village_founding`,
  `bud_requires_occupancy`, `bud_site_separation`, `exclusive_village_membership`,
  `village_identity`, `storable_founding`, `worked_land_yield`, `village_catchment_spread`, `colonizing_budding`,
  `band_territory`
- **10 Surplus & material** — `material_capture`, `material_inheritance`, `wealth_obligation`, `standing`,
  `cred_status`, `cred_renorm`, `prowess_facet`
- **11 Stratification** — `morph`, `rank_hierarchy`, `stratification_inequality_gate`, `relational_stratification`
- **12 Elite** — `leveling`, `legitimacy`, `relative_legitimacy`, `delegitimation`, `leader_office`,
  `leader_share`, `lineage_tribute`, `resentment_accumulator`, `relative_resentment`,
  `village_resentment`, `noble_leveling_exemption`

`band_risk` and `infanticide` were **deleted** on 2026-08-06 — a death spiral at any live value and inert at
its default; and a stub no line of code ever read. They appear in no tier because they no longer exist.

**THIS LIST DRIFTED BEFORE IT WAS EVEN COMMITTED.** Its first draft invented five flags that do not exist
(`band_cohesion`, `divorce`, `patriline_weight`, `pressure_mobility`, plus the deleted `band_risk`) and missed
eight that do. `test_benchmark_ladder.py` now checks it against the config classes, because a hand-maintained
list of 86 names is a second copy and Charter P4 gives second copies two options: tested, or deleted.

---

## Order of work

**Tier 1 is done** (2026-08-06): all six climate channels wired, health-instrumented and CTB'd; four anchors
verified against their PDFs; one retracted; one corrected on the paper's arrival.

**Tiers 2–5 done** (2026-08-07 overnight, RESULTS Addendum 33). Summary of what each rung produced:

| tier | verdict |
|---|---|
| **2 energetics** | anchors land correctly (game exact; forage exact off-shore, the Bird shore bonus being additive on top). **But the canonical world contains NO SAVANNA**, so Hawkes' 518 kcal/hr — the best-verified anchor in the project — never enters a canonical run, and the intercept/llanos channels are `UNREACHABLE` for that reason and not because they are broken |
| **3 demography** | the Siler schedule is CORRECT (e₀ = 36.5 vs Aché ~37, no early-adult collapse). The standing diagnosis "people die in early adulthood" was **wrong**. The pyramid is young because of a HIGH-TURNOVER regime: births 5.66 %/yr and starvation deaths 3.80 %/yr, the latter larger than the entire anchored life table. **RE-SCORED PASS (R-106 Add.81, 2026-09-12):** on current canon every temperate marker is in-band (frac_child 0.37, dependency 0.81, TFR 5.5, e0 36.3, surv-15 0.61), the run is near-stationary (r ≈ +1 %/yr, iso-growth consistent). The old fault is closed |
| **4 movement** | Kelly/Binford implemented correctly. A real unit hazard between the two pressure sources is **silent in both directions** and **cannot be guarded from the value** — two attempts both fired on legitimate data. Documented, not fixed |
| **5 bands** | marker #1 decomposes into **two faults on two tiers**: fixing tier 3's age structure closes ~¼ of the gap (9.4 → 13.8 adults), and the residual to Hill's 28.2 is a genuine tier-5 band-size shortfall. A band would need 69 people to hold 28.2 adults at the measured child fraction; it produces 23. **UPDATE (R-106 Add.77–81):** tier 3 now passes, so its ¼ is already realised and the whole residual is tier 5 — and that residual is a STRUCTURAL packing limit, not a tunable cohesion fault. Bands sit at 0.27–0.55 of their fission cap; the unsaturated biome (savanna) has the smaller bands, falsifying de-saturation. **RE-SCORED — NO DEFICIT (R-106 Add.89, 2026-09-16):** the whole "shortfall" was a mis-specified marker. Hill's 28.2 is the PERSON-WEIGHTED mean-experienced adult size on a RESIDENTIAL group (= the model's CELL, the co-residence unit), not a median over `band_id` (a ~8-cell affiliation). Measured correctly the model gives 33/23 ≈ 28.2 — Hill-scale camps. The earlier "genuine shortfall / packing limit / not fixable" is retracted; the sub-findings (median doesn't reach 28.2; cohesion/food/repulsion inert) stand but chased the wrong target |

| **6 family** | Marlowe's polygyny sentence **verified verbatim**, and marker #10's reported PASS is on the **wrong denominator** — he counts *all men*, we divide by *married* men. 0.0362 reads ~1.0×; on his unit it is 0.0307 = **0.77×**, and because the bias IS the marriage rate it **moves between arms**. First unit mismatch here to turn a PASS rather than a failure into an artefact |
| **7 kin & lineage** | **NO NEW CTB NEEDED — and no anchor to benchmark against.** Already covered by constructed-truth tests in ordinarily-named files: `test_lineage_ground_truth.py` (7 tests, including the rank-key vs patriline unit divergence) and `test_connubium.py::test_lineage_exogamy_rejects_sibling_and_clan_pairs_outsider`, which hand-builds kin relations and asserts the pairing. Its two markers are **#5 (anchor withdrawn)** and **#6 (retired 2026-08-07)**, so the tier has nothing scoreable. The gap here is a SOURCE, not a test |

**Tier 8 (connubium) is next**, then 9.

**Tiers 9–12 still wait.** Of the markers once called surviving failures: **tier-5 band size was never a real
deficit** (Add.89, marker mis-specification); **#14 wealth is now MET** on the corrected marker (`material_gini_adults`
≈ 0.36 both biomes, R-106 Add.90→92, after re-calibrating the bands to the adults statistic); and **#17 fission
ceiling** remains the one quoted miss. The lesson —
proven three times this arc (band size, #14, and the earlier polygyny/lineage cases) — is: **check a marker's
STATISTIC and UNIT before believing a miss or building a fix.** Instrument-hygiene backlog: #1 and #10 code still
compute the wrong statistic (see Add.90).

**UPDATE — #14 wealth has a built, calibrated fix (R-106 Add.82–86, 2026-09-15).** The miss decomposes to a
near-bang-bang shape in the two levelers (Boehm sanction + feast): each pulls material to the cell/band mean with no
tolerated band, so any nonzero strength pins the material Gini at ~0.2 (Add.84). Add.86 builds two tolerance-band
knobs (`leveling_tolerance`, `feast_tolerance`, both default 0.0 ⇒ bit-exact OFF). With the concentrators on, both
bands open (`lt 1.0 / ft 1.5`) reach material Gini **0.367 in both biomes**, guardrails and tier-11 stratification
intact, feast kept on. **ADOPTED into canon (R-106 Add.87, 2026-09-16):** the aggrandizer skim was grounded to the
gumsa "thigh from every animal" rate (`material_capture_frac = 0.15`), the bands re-calibrated, and the four values
written into the canonical stack. Full-suite churn was 3/1740, all resolved; the canonical baseline is now a
stratified world. **CORRECTION (R-106 Add.90):** that 0.363/0.372 is the ALL-AGES material Gini, but BHM's 0.36 is
age-adjusted over ADULTS. On the comparable ADULTS statistic the adopted canon read **0.16–0.22**, so the first
"#14 PASS" was RETRACTED. **RESOLVED (R-106 Add.92):** the band width is the lever (the capture skim plateaus); at
grounded concentrators, widening the bands to `leveling_tolerance = 3.0`, `feast_tolerance = 4.0` lands
`material_gini_adults` at **0.386 temperate / 0.357 savanna ≈ 0.36**, biome-invariant, with tier-11 stratification
(66–69%), e₀, frac_child and pop intact, and corr(cred,material) improved to +0.26/+0.16. RE-ADOPTED into canon; full
suite 1743 passed / 0 failed. **#14 is CLOSED on the corrected marker.** (The all-ages `material_gini` is now ~0.53,
child-inflated and deprecated.)

---

*Ladder adopted 2026-08-07. Amend by dated note. Coverage figures are measured, not estimated — regenerate
them before quoting.*
