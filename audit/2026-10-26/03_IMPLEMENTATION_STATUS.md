# 03 — Implementation status: implemented and ON, implemented but OFF, NOT implemented (2026-10-26)

**Sources.** The canonical run file `config/runs/full_campaign.toml` (which flags run), `docs/REGISTRY.md` (every flag
and parameter, generated), `run_campaign.py` `_skip` (the recorded reason for each flag held OFF), `MAP_mechanisms_to_code.md`
(where each flag is defined and read), `docs/DEFERRED_MECHANICS.md`, `docs/ELITE_STRATIFICATION_ROADMAP.md`, and the
RESULTS entries cited. **Every mechanism is a flag** whose class default is OFF (bit-exact reproducibility of
historical runs); the canonical stack switches on every built mechanism except the `_skip` set, plus the climate
channels that the Earth-baseline climate leaves off.

**Totals:** 125 flags — **98 ON** in canon, **27 OFF** (21 held by `_skip`, 6 climate-variability channels). Every
flag is read by model code (`MAP_mechanisms_to_code.md`: no flag without a read site). Parameters: 253 in the canonical
run; 14 ANCHORED, 8 VERIFIED, 39 PROVISIONAL, 164 without a tag in their own source comment (REGISTRY §2; a heuristic count — comments in the source are not reliably attached to one field).

---

## 1. Implemented and ON in canon (98), by benchmark-ladder tier

Names without the `enable_` prefix. What each does: REGISTRY.md (one line) → its definition in `demography.py`
(full provenance comment) → its read sites (MAP). "Validated" means a scored marker or a RESULTS entry; see column notes.

| tier | ON | flags |
|---|---|---|
| 1 Physical world | 10 | alluvial_renewal, biome_seasonality, catchment_depletion, intercept_hunting, resource_storability, seasonality, soil_depletion, terrain_move_cost, terrain_risk, village_density_disease |
| 2 Energetics | 16 | biome_meat_cv, biome_meat_frac, condition, energetic_fertility, eta_weighted_shares, forage_cap, game, intake_fertility, need_weighted_shares, nutrition_synergy, provisioning, storage, storage_seasonal_union, store_anchor, tier2_shock, **village_granary** (Add.113) |
| 3 Demography | 12 | density_disease, density_fertility, density_reference, dependent_load, energetic_refractory, life_history, metabolic_downreg, orphan_mortality, **risk_accident_share** (Add.113), sedentism_fertility, society_regional_density, synergy_age_grade |
| 4 Movement | 3 | landscape_packing, productivity_mobility, site_appraisal |
| 5 Bands | 9 | aggregation_sedentism, band_affiliation, band_family_knobs, dynamic_bands, emergent_band_size, leader_coherence, marriage_aggregation, resource_directed_fusion, size_repulsion |
| 6 Family | 3 | bonded_mating, pair_bonds, paternity (+ `paternal_provision_frac` 0.5, Add.109) |
| 7 Kin & lineage | 5 | exogamy, genome, lineage_branching, lineage_split, local_ascription |
| 8 Connubium | 2 | adaptive_connubium, ascribed_mate_choice |
| 9 Settlement | 16 | aggl_ceiling, agglomeration, agriculture, **bud_viable_site** (Add.108), catchment_ceiling, colonizing_budding, economic_defensibility, emergent_abandonment, emergent_village_founding, improved_land, settlement_scalar_stress, storable_founding, village_budding, village_identity, village_scaling, worked_land_yield |
| 10 Surplus & material | 7 | cred_renorm, cred_status, material_capture, material_inheritance, prowess_facet, standing, wealth_obligation |
| 11 Stratification | 3 | morph, rank_hierarchy, relational_stratification |
| 12 Elite | 11 | delegitimation, leader_office, leader_share, legitimacy, leveling, lineage_tribute, noble_leveling_exemption, relative_legitimacy, relative_resentment, resentment_accumulator, village_resentment |
| no tier assigned | 1 | capacity_scaled_grouping (not in the BENCHMARK_LADDER tier membership — a documentation gap) |

**Weak signals worth a look** (text search, `MAP_mechanisms_to_code.md`):
- **6 ON flags that no test names by their code name:** eta_weighted_shares, site_appraisal, standing, store_anchor,
  terrain_move_cost, wealth_obligation. Generic tests (the flag audit `audit_flag_invariants.py`, the liveness battery)
  may still exercise them; the absence of a NAMED test is a lead, not a finding.
- **28 flags that no RESULTS entry names by their code name** (listed in the MAP); many are described in prose
  instead (for example `legitimacy` → R-86, `delegitimation` → R-87). Again a lead.
- **Tiers with no scored marker:** tier 1 (physical world), tier 2 (energetics), tier 4 (movement) and tier 12 (elite)
  carry no marker in the CURRENT SCORECARD; tier 11 has only the pre-registered, unscored #9. Their validation lives
  in RESULTS entries (for example EFC gates R-49/R-50; legitimacy R-86; delegitimation R-87, R-87d) and in the
  `docs/TARGETS.md` T-5…T-9 statuses (last set July–August).

## 2. Implemented but OFF in canon (27) — and why

| flag | tier | why OFF (the recorded reason) | record |
|---|---|---|---|
| band_provisioning | 2 | **REJECTED:** zero-sum — saves children by killing adults (savanna e15 below the forager floor) | RESULTS Add.75, Add.108 |
| sticky_pin_release | 9 | **REJECTED:** worse on savanna and temperate; the one-step pin flicker protected families | Add.111 |
| hunger_dispersal | 4 | **FALSIFIED as canon:** unpacks the population but crashes temperate e0 | Add.78 |
| stratification_inequality_gate | 11 | **criterion known wrong** (within-band Gini is ~uniform); the RELATIONAL criterion is ON instead | R-103 record, Add.62 |
| band_territory, fertility_restraint_gene, restraint_group_transmission, heritable_density_response | 9, 3 | **negative result:** the preventive check is neither selectable nor consequential; kept as instruments | Add.70–72 |
| sub_k_regulation | 3 | exogenous emigration closes the e0 gap but is a density-for-e0 trade and cannot evolve; not adopted | Add.74–75 |
| density_fill_matched_radius | 3 | a real CORRECTION (numerator/denominator radius mismatch) but lowers juvenile survival alone; held | Add.106 |
| bud_household_closure | 9 | repairs a contradiction between two adopted mechanisms; works, but buys no measurable population; held | Add.105 |
| village_catchment_spread | 9 | fixes over-clustering but removes the density-disease brake → population runaway; needs a replacement brake | run_campaign `_skip` note (2026-09-02) |
| founding_delay | 4 | marginal effect; trips the age-structure test through a startup transient; no anchor for the delay length | `_skip` note |
| leaky_assabiyah | 5 | measured and defensible, but only restores cohesion headroom with an UNANCHORED weight; not adopted | RESULTS Add.23 |
| bud_hazard | 9 | a mutually exclusive alternative to the legacy budding path | `_skip` note |
| bud_requires_occupancy | 9 | adopted at Add.53, then SUPERSEDED by colonizing budding (Add.61) and retired | Add.53, Add.61 |
| bud_site_separation | 9 | works but imposes 50 km against the ~10 km catchment anchor; kept as the "geometry alone" control | `_skip` note (2026-08-12) |
| exclusive_village_membership | 9 | no spacing on its own, raises churn; a settlement-runaway candidate not chosen | `_skip` note (2026-08-12) |
| terrain_pathogen | 3 | magnitude `pathogen_gamma` has an anchor direction (Cashdan 2014) but the required low/mid/high sweep was never run | `_skip` note; PARAMETERS §15 |
| malnutrition_fission | 3 | its gain was zeroed to serve as a negative control; the gain is UNANCHORED | `_skip` note; R-33 |
| genealogy_log | 7 | an observer (logging), not a dynamic; costly — switched on per run when needed | `_skip` note |
| caribou_swing, climate_lottery, eccentricity_mean, interannual, llanos_flood, regime_shift | 1 | climate-variability channels; the canonical climate is the EARTH BASELINE, which carries no variability | RESULTS Add.48; `test_campaign_knobs.py` |

## 3. NOT implemented

| item | status | record |
|---|---|---|
| **Malthusian contraction under a shock** (drought) as a TEST | the arc's open goal; the tier-2 yield shock exists (`tier2_shock` ON), but no shock-response test has been run on the current canon | `docs/ROADMAP.md` CURRENT STATUS |
| **A cause-of-death structure** (illness vs accident vs violence vs starvation) and its marker | missing; illness is not a separate cause — it is the Siler baseline × modulators | RESULTS Add.112 |
| **Status → partner-fertility channel** (von Rueden's dominant channel) | missing; makes #11 not comparable | RESULTS R-80, Add.102; LITERATURE.md |
| **Secular cycles / state-scale or urban density layer** | not built; four negatives on the current scale | R-97; Add.105 |
| **Si (individualist) strategy on the Phase-1 substrate** | not built; the C/Si comparison is Phase-0 only | R-1; HYPOTHESES §H1ii-RETEST (OPEN, never run) |
| RS-1 risk-sensitive (variance-reducing) foraging | DEFERRED — mean-only choice in place | DEFERRED_MECHANICS RS-1 |
| PL-1 pool scale-dependence | DEFERRED — the Phase-0 support pool is dormant in the kcal economy | DEFERRED_MECHANICS PL-1 |
| PA-1 proto-agriculture yields per biome + seasonality | DEFERRED (agriculture is ON with one yield model) | DEFERRED_MECHANICS PA-1 |
| MR-2 carried provisions | PARTIAL — founders only | DEFERRED_MECHANICS MR-2 |
| FD-1 family dynamics | PARTIAL — provisioning and bonded mating built; the rest deferred | DEFERRED_MECHANICS FD-1 |
| DM-F2 split `prowess` into expertise and martial facets | not built | DEFERRED_MECHANICS (Flannery digest) |
| DM-F4 sacred/secular office split | not built | DEFERRED_MECHANICS |
| DM-F5 slavery (incl. debt slavery) as the bottom rung | not built | DEFERRED_MECHANICS |
| DM-F1 legitimacy; DM-F3 gumsa/gumlao switch; DM-F6 tribute | **BUILT later** in some form (R-86 legitimacy ratchet; R-87 delegitimation; `lineage_tribute`) — but DEFERRED_MECHANICS still says "none is built" (a stale entry) | R-86, R-87; DEFERRED_MECHANICS |
| Elite roadmap step (2): tribute / status–wealth coupling | PARTIAL — "the gap" in the roadmap; the levy exists but is weak | ELITE_STRATIFICATION_ROADMAP |
| An instrument fix: the demography monitor's band-size check | not done — it still uses the retracted `band_med_adults` | RESULTS Add.89, Add.114 |
| Automated scoring of markers #5, #8, #9 | not built in `tools/scorecard.py` | MARKER_MATRIX |
| Replication of the canon on other planets (world seeds) | not run | MARKER_MATRIX rule 3 |
