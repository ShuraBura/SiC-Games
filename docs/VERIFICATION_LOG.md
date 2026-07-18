# Verification Log — dated constant + code checks (the "skip-list")

**Purpose.** A single authoritative record of *what has been verified, when, and against exactly where in the source*,
so future audits SKIP already-verified items. Two registers: **(A) Constants** (value ↔ exact source location ↔ date),
**(B) Code/architecture checks**. Convention going forward: when a constant is verified, add/update its row here with
the **exact source location** (page / table / figure / eq / paragraph) and the **UTC date-time** of verification; the
per-section PARAMETERS.md / LITERATURE.md tables point here rather than duplicating the audit trail.

Verdict key: **CONFIRMED** (matches source exactly) · **ANCHORED** (newly set from source) · **PLAUSIBLE** (in range,
not exact) · **PROVISIONAL** (design/uncalibrated) · **BUG→FIXED** · **OPEN** (needs primary-source check).

---
## (A) Constants verification register

| Constant | Value | Source — EXACT location | Method | Verified (UTC) | Verdict |
|---|---|---|---|---|---|
| Binford packing threshold | 0.091 /km² (9.098 /100 km²) | Binford 2001 *Constructing Frames of Reference* — packing index (value widely secondary-cited; **primary page OPEN**) | WebSearch cross-check | 2026-07-09 13:11 | CONFIRMED (value) / location OPEN |
| `MEAT_FRAC` forest/desert/savanna/grass | 0.55 / 0.45 / 0.38 / 0.66 | Cordain et al. 2000 *AJCN* 71:682–692 — **Table 2** (mean subsistence dependence by primary environment), class-interval midpoints, fished column dropped | Arithmetic re-derived from Table 2 (50.5/91=0.555 …) | 2026-07-09 13:11 | CONFIRMED |
| `reserve_full_kcal` / `reserve_floor_kcal` | 130,000 / 20,000 | Cahill 1970 "Starvation in man" *NEJM* 282:668–675 — total fuel ~166k (70 kg ref); death at **fat < 3 kg AND protein > 50 % depleted** | WebSearch (figures widely cited; **PDF not filed**) | 2026-07-09 13:11 | ANCHORED |
| `settle_min_pool` | 40 | Bar-Yosef 1998 *Evol. Anthropol.* 6:159–177 — Natufian settlement sizes (small ~dozens → medium 100–150) | WebSearch (**PDF not filed**) | 2026-07-09 13:11 | ANCHORED (lower bound) |
| `TREELINE_WARMEST_MONTH_C` | 10.0 °C | Köppen ET boundary (warmest-month 10 °C isotherm); cross-check Körner & Paulsen 2004 *J. Biogeog.* 31:713–732 — 6.7 °C growing-season **soil** mean (abstract/results) | WebSearch (corrected from a mis-slotted 6.4) | 2026-07-09 13:11 | CONFIRMED |
| `mu_max` (nutrition-mortality synergy) | 2.5 | Pelletier 1994 *Nutr. Reviews* 52:409–415 — malnutrition potentiates mortality multiplicatively/exponentially (body) | WebSearch (severe 5–8× ⇒ 2.5 cap conservative) | 2026-07-09 13:11 | PLAUSIBLE |
| Siler a1..b3 (Aché forest) | a1 0.157, b1 0.721, a2 0.013, a3 4.80e-5, b3 0.103 | Gurven & Kaplan 2007 — **Table 2** (Aché forest) | pdfplumber extract + PDF spot-check (per LITERATURE.md) | 2026-06-18 (prior) | CONFIRMED |
| Miami NPP(T,P) coeffs | eqs (12-1)/(12-2) | Lieth 1975 *Modeling the Primary Productivity of the World* — **p. 9, eqs 12-1 & 12-2** | PDF filed + spot-check | 2026-07-03 (prior) | CONFIRMED |
| Tallavaara NPP→density | segmented regression | Tallavaara et al. 2018 *PNAS* — regression + SI (Dataset_4) | fitted + validated (R-36) | 2026-07-02 (prior) | CONFIRMED |
| Johnson scalar stress + society dissipation | `size_repulsion` shape + REPULSION_SOCIETY_FACTOR | Johnson 1982 (PDF filed) — org structure ABSORBS scalar stress; hierarchy relieves size penalty | PDF read | 2026-07-09 | CONFIRMED (shape; midpoint bracketed) |
| `settlement_ss_midpoint` (village fission) | 150 | Bar-Yosef 1998 — egalitarian-village upper bound (medium settlement) | secondary | 2026-07-09 | ANCHORED |
| Standing / hxaro (`standing_tenure_rate`) | 0.083 (~1 yr to firm) | Wiessner 1977 *Hxaro* diss. — ≥1 yr reciprocal exchange to "firm" | WebSearch (PDF not filed) | 2026-07-09 | ANCHORED |
| Sedentism IBI / NDT | 30/22/14 mo (~2× birth rate) | Bocquet-Appel 2011 *Science* 333:560; Sellen & Mace 2007 (weaning×subsistence); Howell !Kung 44 mo | WebSearch (PDFs not filed) | 2026-07-09 | ANCHORED |
| Vita-Finzi & Higgs site-catchment | ~5 km forager reach | Vita-Finzi & Higgs 1970 (filed above) | prior | 2026-07-09 | CONFIRMED (radius calibration OPEN) |

**OPEN (not yet primary-verified; used in run A/A2/A3):** `fecundability=0.12` [FREE], `ibi_refractory=30` [FREE],
`SEDENTISM_IBI` 30/22/14 (anchored to Howell/Sellen-Mace/Bocquet-Appel — **exact page/table OPEN**), return-rate
FORAGE/GAME kcal tables (provenanced but PROVISIONAL — Hill 1987 / Berbesque-Marlowe 2009 / Bird 2009 / etc., exact
table locations to log), `village_gain=5.0` (UNANCHORED design knob), morph gates (Testart 0.5/0.7, morph_npp_floor
500 = R-47 data-derived), storage (`store_capacity_reserves=12`, decay 0.02) — Halstead/Testart/Kuijt survey.

---
## (B) Code / architecture check register

| Area | Check | Verified (UTC) | Finding |
|---|---|---|---|
| Births | double-count? (`_do_births` vs `_do_births_ibi`) | 2026-07-09 | CLEAN — `if/elif` mutually exclusive (phase1_model:495/497) |
| Mortality | double-count? (Siler + max_age + starvation) | 2026-07-09 | CLEAN — Siler roll → `elif age≥max_age` backstop → starvation; not additive |
| Morph surplus | `surplus_frac` scaling | 2026-07-09 | **BUG→FIXED** — summed whole-cell granaries / band members ⇒ 6–14; fixed to band-share (0–1) |
| Morph packing | "packed" density measure | 2026-07-09 | **BUG→FIXED (opt-in)** — band-members/footprint ⇒ never packs; `enable_landscape_packing` uses landscape density |
| Genome | relatedness coefficients | 2026-07-09 | CLEAN — parent-child ≈0.5, sib ≈0.5, unrelated ≈0 (unit-tested) |
| Exogamy/connubium | kin/clan rejection rule | 2026-07-09 | CLEAN — sibling/clan/cousin correctly rejected (unit-tested) |
| `enable_infanticide` | wired? | 2026-07-09 | DEAD STUB — no logic reads it (harmless, off). Candidate for deletion |
| Economic defensibility | does the tether anchor? | 2026-07-09 | **INERT + not a payoff** — its docstring: "a perception change only"; A/B shows only 3–14 cells ever claimed (`D_min=0.15` rarely passes) ⇒ no effect (occ_cells 889 vs 899) |
| Movement payoff ledger | do any terms scale to VILLAGE size? | 2026-07-09 | **NO** — `group_safety` saturates at g_s=15, mating caps at 15, granary absent from decision, security never touches mortality, dwellings absent; only `Rv·(n^0.15−1)` (gated to S_pot). Measured utility peaks at **n=15** and falls monotonically (R-62) |
| `enable_aggregation_sedentism` | wired? active? | 2026-07-09 | **OFF, and doubly gated** — settlements are founded inside `_do_gathering`, so it ALSO needs `enable_marriage_aggregation`. ⇒ `_settlement_sites=0` in every run ⇒ residence≠foraging catchment never ran (root cause, R-62) |
| P6 standing / P1 store anchor | correctness | 2026-07-09 | Built, default-OFF. Standing cannot anchor alone (relative weight cancels when `Wsum=0`); first store cut was BUGGY (ungated + per-capita ⇒ rewarded dispersal) → fixed to community-gated |
| Campaign diagnostics | do `dynasties()`/`settlements()`/`instability()`/`genetics()` perturb the model? | 2026-07-13 | CLEAN — all read-outs route RNG through a dedicated `_diag_rng`; `test_campaign_readouts_are_observer_only` shows identical population/unique_ids with the read-outs interleaved every step (genome ON). Genealogy logger enriched to the 17-col `GENEA_HEADER`, still observer-only + bit-exact when off (`test_genealogy`) |
| Economic defensibility (RE-CHECK) | still inert (cf. line 50)? | 2026-07-13 | **CONFIG-DEPENDENT** — INERT in dispersed run-A (few cells pass `D_min`), but ACTIVE in the CAMPAIGN config: the settlement stack packs agents onto high-aquatic cells so `D_min=0.15` passes ⇒ `inst`=23–27 contest-events/step, cells owned >0. Requires `enable_economic_defensibility=True` (default OFF; the C_DEFEND arm). Params still PROVISIONAL (`D_min` 0.15, dwell 6, min 3); ~2× stratification at the 800-founder smoke but ~parity at 3000 founders (step 250) — divergence to be resolved by the OFF/ON campaign arms |

**OPEN code checks (the running to-do — build out next passes):**
1. **Storage granary fill/cap** — the per-cell cap `store_cap_mult·reserve_full·occ` and the 84M-kcal stores; is the cap right, does it overfill?
2. **Proto-agriculture unlock + soil depletion** — CHECKED 2026-07-09: the swidden soil mechanism (`_update_settlement_soil`) is CORRECT as designed (farm soil exhausts progressively → relocate; fisheries exempt; "Landesque capital B2" damping is the unbuilt intensification seam). BUT it is **INACTIVE** in `emergent_village_demog` (`_settlement_sites`=0 the whole run — villages come from agglomeration+band-morph, not the discrete settlement machinery). So the A3 "packing de-packs" is NOT soil-driven — both the supervisor's and Claude's swidden hypotheses FALSIFIED for this config. **Verified real driver: IFD DISPERSAL** — the population spreads to fill the landscape (occ_cells 641→1067 as pop grows), local density → the sub-packing regional average (~0.06/km²), so the stratified cores de-concentrate and de-morph (absolute N_stratified 1219→51). Depletion ACCELERATES but is not the cause (depletion-OFF A/B still collapses). The early stratification is a TRANSIENT of the concentrated founder placement. Same root as R-54 "assembly binds" / the original "continuous spread." To SUSTAIN: hold concentration vs dispersal (emergent circumscription / stronger agglomeration-defensibility), NOT soil-renewal.
3. **GD-1 depletion** `deplete_and_regrow` — behaviour at scale/high occupancy.
4. **Movement** `diffusion_select_target` — the perf hot path; correctness of the group_safety / site / band_opt terms.
5. **Agglomeration** point-superlinear `A_cell·(n^{β−1}−1)` — assembly vs economics (R-54).
6. **Per-cell vs per-band morph** paths — consistency (two code paths for the same ladder).
7. **[FREE]/[PROVISIONAL] demographic knobs** — fecundability, IBI, dens_delta/rho_half, storability — grounding review.
8. **Climate/season** fields — `ClimateField.season/regime`, seasonal amplitude per biome (PROVISIONAL).

---

## Elite layer - source verification (2026-07-18; R-82/R-83/R-84/R-84b)

| Source | Status | What was verified, and how |
|---|---|---|
| Boehm 1993, *Curr. Anthro.* 34(3) | **[VERIFIED]** | Full text + **Table I recovered by POSITIONAL extraction** (linear dump destroys the x-mark matrix). Counts: Public opinion 10, Criticism 6, Ridicule 5, Disobedience 7, **Deposition 9**, **Desertion 17**, Exile 2, Execution 10. Consistency check: 66 marks over 48 societies, consistent with Boehm's "in many cases a single society exhibited both types". Also the 47-motivation tally (13/14/10/5/3/2) and the 38/48 removal aggregate that `leveling_strength` already used. |
| Hayden 1995 (`literature/hayden1995.pdf`) | **[VERIFIED]** | "MANAGERIAL RIGHTS over the resource locations and facilities of the group" (NW Coast, spatially restricted resources) vs New Guinea "more ubiquitous access ... limited the development of social stratification". **"About 75% of New Guinea Entrepreneur Big Men had fathers that were also Big Men"** - transmitted via moka partners and wives, NOT the position. Strict positional inheritance appears only at the Ahousaht chiefdom (Rosman & Rubel 1971:80). |
| Sahlins 1972 *Stone Age Economics* | **[VERIFIED]** | Full text layer, 363 pp. p.209 Siuai-vs-Nootka office/achievement contrast (the succession dichotomy); p.136-137 the big-man MOBILISES via debt rather than levying, while the NW Coast chief is "accorded a certain right to group resources". |
| Borgerhoff Mulder et al. 2009 *Science* 326:682 | **[VERIFIED]** | Tables 1 and 2 of the NIH-PA author manuscript; **Table 2 recovered by POSITIONAL extraction** (landscape layout transposes under linear dump). Cross-checks passed: alpha rows sum to 1.000 per system; recovered forager/horticultural Ginis 0.25/0.27 reproduce the paper's own Nordic-comparison statement (0.24). |
| Ames 1994 (AGG6) | **[VERIFIED - NEGATIVE]** | Full text searched for a chiefly extraction RATE. **None exists.** Qualitative elite control of production only. |
| Sahlins 1972 (rate search) | **[VERIFIED - NEGATIVE]** | Full text searched for a chiefly-due PERCENTAGE. **None exists.** This is why `leader_share_frac` is anchored on outcome (BHM composite Gini), not on a rate. |
| Smith & Codding 2021 *PNAS* | **[VERIFIED]** | Full text read 2026-07-18 (open access, PMC8020663). **r = 0.881, n = 89 CONFIRMED** (HI ~ RI, full sample). Plus: NPP effect size **0.04** (productivity nearly irrelevant) vs Resource Index 0.37; fishing-site OWNERSHIP a significant direct pSEM predictor (b_std 0.96, P=0.043); offensive raiding -0.01. **Process note:** a first summarised fetch reported the 0.881 as ABSENT and was wrong - a single fetch summary is not verification. |

**Code checks performed (R-84, all found by MEASUREMENT not inspection - added to the standing skip-list):**
1. **Tenure keyed to the wrong object** - office was keyed to `band_id`; band_ids churn on every fusion/fission, capping tenure at ~4 yr even with sanctions OFF. Re-keyed to the MAN. *Lesson: when a diagnostic is flat against a knob that should move it, check what the clock is attached to before tuning the knob.*
2. **Collision resolution by dict order** - ended 106 of 135 tenures (death only 29). Now by merit.
3. **Eligibility unbounded** - `max(ms, ...)` over ALL band members let a high-cred CHILD hold office; mean leader age 23.5 yr vs adult mean 34.1. Gated on `menarche_months`.
4. **Vacuous flag** - `succession_dissolve` measured against the band MEAN had literally zero effect (identical output, 0 vacancies), because the max of ~25 draws clears +25% over the mean essentially always. Re-specified against the nearest RIVAL. *Same failure class as the R-74 vacuous test: a mechanism that "passes" while doing nothing.*

**OPEN for the elite layer:**
- `office_grievance_gain` and `office_challenge_margin` are [DESIGN], calibrated on tenure, not lit-anchored.
- Band-level tenure is bounded by band FUSION (4-6 yr), not by the leader's life. A chiefly 20-yr tenure needs the office attached to the SETTLEMENT - the next rung, and Hayden's precondition.
- `material_invulnerability_min` gate still unexercised in a stressed/high-density regime.
- Father-was-leader lands 53-69% vs Hayden's 75% - same order, somewhat low; worth revisiting once relational capital (exchange partners) is transmissible, since that is Hayden's actual channel.

---
*Verification Log opened 2026-07-09. Append/update rows as checks are performed — this is the skip-list.*

### Elite-layer sources, second pass (2026-07-18)

| Source | Status | Outcome |
|---|---|---|
| D'Altroy & Earle 1985 | **[VERIFIED - NEGATIVE]** | Fetched specifically to find a direct levy RATE that would supersede the outcome-anchoring of `leader_share_frac`. **None exists** - obligation is corvee LABOUR (mit'a) per household, not a share of product. The anchor stands as R-84b left it. **Do not re-fetch for this purpose.** Yields instead a stored-GRAIN decay anchor: **30%/yr maize loss** (our stored-food decay is [DESIGN]); must not be applied to durable prestige goods. |
| BHM 2009 SOM (Table S4) | **[VERIFIED]** | Per-wealth-type Ginis obtained. Model matches facet-by-facet: prowess 0.24-0.26 vs 0.237/0.339; cred 0.27 vs 0.216/0.263; **material 0.237 vs Lamalera housing 0.241**. The remaining gap is entirely **boat shares 0.474 = a PRODUCTIVE ASSET the model lacks**. |
| Hawkes et al. 1991 | **[TEXT LAYER OBTAINED]** | Two searchable copies filed, replacing the image-only scan. Pooled savanna return rates unchanged. |
| Flannery & Marcus 2012 | **TOC ONLY** | Chapters identified for retrieval: **5** (Inequality without Agriculture, p.66 - our current stage), **10** (Rise and *Fall* of Hereditary Inequality in Farming Societies, p.187 - the next rung AND the cycles question), **16** (How to Turn Rank into Stratification, p.313 - T-5's failing agricultural arm), then **11** (Three Sources of Power in Chiefly Societies, p.208) and **9** (Prestige and Equality in Four Native American Societies, p.153). |

### Charter retrofit - code checks (R-85, 2026-07-18)

| Check | Result |
|---|---|
| `enable_leader_office` without `enable_band_affiliation` | **CRASH FIXED** - `_next_band_id` was created only inside the affiliation guard; the office runs outside it. Now initialised unconditionally (bit-exact); regression test `test_office_survives_without_band_affiliation`. |
| `enable_cred_renorm` gauge-invariance | **REFUTED** - moves every observable. The fixed 1.0 inheritance anchor makes cred rescaling non-scale-invariant. Re-typed R (Regulator). |
| `enable_genealogy_log` observer invariance | **PASS** - mutates nothing. First positive confirmation of a charter type. |
| `enable_infanticide` reader search | **CONFIRMED STUB** - no reader outside the config object. |
| Flag-vs-magnitude audit | **5 DEAD KNOBS** - leader_coherence_gain, malnutrition_fission_gain, repulsion_gain, pathogen_gamma, village_gain all 0.0 while their flags are ON. Invalidates the 2026-07-15 config-audit claim that all built mechanisms are correctly ON. |
| Black-box conservation testing | **NOT SOUND** - trajectory coupling makes A-typed flags move conserved quantities legitimately. Conservation must be instrumented around the call. |

**OPEN (R-85 residual):** 6 flags inert at both seeds with a live reader and non-zero magnitude -
`enable_bonded_mating`, `enable_condition`, `enable_energetic_fertility`, `enable_landscape_packing`,
`enable_site_appraisal`, `enable_terrain_move_cost`. Individually inspect before claiming defect or inertness.
**Also open:** the in-step conservation instrumentation (the half of the charter audit this pass could not do).
