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
| 3 | **Demography** — mortality, fertility, orphanhood | 8 | 8 | 1 | Gurven & Kaplan 2007 (Siler), Hill & Hurtado 1996 (sex split; Table 13.1 orphan), Pelletier 2009 | #15 orphanhood ✓, #16 engine |
| 4 | **Movement** — mobility, packing, site choice | 3 | 2 | **0** | Kelly / Binford mobility bands | — |
| 5 | **Bands** — grouping, cohesion, assabiyah, fission | 9 | 9 | **0** | **Hill et al. 2011 (28.2 ADULTS)**, Birdsell 1953 (~25), Marlowe (25–50) | **#1 band size — FAILS 16/16** |
| 6 | **Family** — pair bonds, paternity, polygyny | 3 | 3 | **0** | Marlowe *The Hadza* (polygyny ~0.04), von Rueden & Jaeggi | #10 polygyny ✓ |
| 7 | **Kin & lineage** — descent, exogamy, genome | 7 | 7 | 1 | **none at forager scale** (#6 retired 2026-08-07; #5 anchor withdrawn) | #5 not scoreable, ~~#6 retired~~ |
| 8 | **Connubium** — between-band mating networks | 2 | 2 | **0** | White 2017 (MVP), Wobst 1974 (MES 79–332) | #4 connubium 15/25 |
| 9 | **Settlement** — sedentism, villages, budding, agriculture | 10 | 9 | **0** | Alvard 2009 (50–250), Alberti 2014 (127 / 158), Hamilton 2007 (165), Bandy 2004 (fission rate), Johnson (rank-size) | #3 ✓ 46/52, #8 ✓, #12, #13, **#17 fission ceiling — MISSES** |
| 10 | **Surplus & material** — wealth, status, obligation | 6 | 4 | **0** | BHM 2009 Table S5 (HG material Gini **0.36**) | #11 status→RS, **#14 wealth — 0.162 vs 0.36** |
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

- **1 Physical world** — `climate_lottery`, `seasonality`, `eccentricity_mean`, `interannual`, `regime_shift`,
  `caribou_swing`, `llanos_flood`, `intercept_hunting`, `terrain_risk`, `terrain_move_cost`, `soil_depletion`,
  `alluvial_renewal`, `resource_storability`, `catchment_depletion`, `village_density_disease`
- **2 Energetics** — `game`, `biome_meat_frac`, `biome_meat_cv`, `forage_cap`, `provisioning`,
  `nutrition_synergy`, `condition`, `store_anchor`, `storage`, `tier2_shock`, `energetic_fertility`,
  `intake_fertility`, `need_weighted_shares`, `eta_weighted_shares`
- **3 Demography** — `orphan_mortality`, `density_disease`, `density_reference`, `society_regional_density`, `terrain_pathogen`, `dependent_load`,
  `sedentism_fertility`, `energetic_refractory`, `life_history`, `malnutrition_fission`, `metabolic_downreg`
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
  `village_identity`, `storable_founding`, `worked_land_yield`, `village_catchment_spread`, `colonizing_budding`
- **10 Surplus & material** — `material_capture`, `material_inheritance`, `wealth_obligation`, `standing`,
  `cred_status`, `cred_renorm`, `prowess_facet`
- **11 Stratification** — `morph`, `rank_hierarchy`, `stratification_inequality_gate`
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
| **3 demography** | the Siler schedule is CORRECT (e₀ = 36.5 vs Aché ~37, no early-adult collapse). The standing diagnosis "people die in early adulthood" was **wrong**. The pyramid is young because of a HIGH-TURNOVER regime: births 5.66 %/yr and starvation deaths 3.80 %/yr, the latter larger than the entire anchored life table |
| **4 movement** | Kelly/Binford implemented correctly. A real unit hazard between the two pressure sources is **silent in both directions** and **cannot be guarded from the value** — two attempts both fired on legitimate data. Documented, not fixed |
| **5 bands** | marker #1 decomposes into **two faults on two tiers**: fixing tier 3's age structure closes ~¼ of the gap (9.4 → 13.8 adults), and the residual to Hill's 28.2 is a genuine tier-5 band-size shortfall. A band would need 69 people to hold 28.2 adults at the measured child fraction; it produces 23 |

| **6 family** | Marlowe's polygyny sentence **verified verbatim**, and marker #10's reported PASS is on the **wrong denominator** — he counts *all men*, we divide by *married* men. 0.0362 reads ~1.0×; on his unit it is 0.0307 = **0.77×**, and because the bias IS the marriage rate it **moves between arms**. First unit mismatch here to turn a PASS rather than a failure into an artefact |
| **7 kin & lineage** | **NO NEW CTB NEEDED — and no anchor to benchmark against.** Already covered by constructed-truth tests in ordinarily-named files: `test_lineage_ground_truth.py` (7 tests, including the rank-key vs patriline unit divergence) and `test_connubium.py::test_lineage_exogamy_rejects_sibling_and_clan_pairs_outsider`, which hand-builds kin relations and asserts the pairing. Its two markers are **#5 (anchor withdrawn)** and **#6 (retired 2026-08-07)**, so the tier has nothing scoreable. The gap here is a SOURCE, not a test |

**Tier 8 (connubium) is next**, then 9.

**Tiers 9–12 still wait.** Their markers include the two surviving failures (#14 wealth, #17 fission ceiling)
and both are quotable — CTB'd on 2026-08-07 and held — but *diagnosing* them means looking down the ladder,
and tier 5 has just shown what that produces.

---

*Ladder adopted 2026-08-07. Amend by dated note. Coverage figures are measured, not estimated — regenerate
them before quoting.*
