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
*Verification Log opened 2026-07-09. Append/update rows as checks are performed — this is the skip-list.*
