# 07 — Review of the external audit report (2026-10-26, evening)

**Subject.** `sic_games_audit_2026_10_26.md` (in this folder; written by the external auditor on commit `07c1ef7`;
not edited). **Method.** Each finding was checked against the code, the configuration and the run outputs on the
supervisor's machine — by reading the cited lines and, where a number was at stake, by measuring it. Verdicts:
**CONFIRMED** (the defect exists as described or in substance), **PARTLY** (real, but a part of the description or the
consequence is wrong), **NOT CHECKED** (plausible; no check made yet), **NOT CONFIRMED** (the code does not show it),
**REFUTED** (the cited code, file, flag or number does not exist or says otherwise).

**Bottom line.** The report finds real and important defects — in the model (F-01, F-02, F-03, F-05, F-06), in the
configuration (F-10, F-11) and in this package's own tools (F-09). It ALSO contains claims that are false: rows and
functions that do not exist in `tools/scorecard.py` and `tools/benchmark_history.py`, a flag that does not exist
(`enable_paternity_tracking`), a run snapshot that does not exist (`add110_vgran`), canon flag values stated wrongly,
and several numbers that match no output. **Do not act on a number or a line reference in the report without this
review.** No model code was changed in response; the fixes below are proposals for the supervisor. The defects in the
package's own tools were fixed (§4).

---

## 1. Model defects

| finding | verdict | evidence (checked 2026-10-26) |
|---|---|---|
| **F-01** juvenile efficiency η applied twice under `enable_eta_weighted_shares` | **CONFIRMED** | `_claim` weights by `consumption_factor × η` (`phase1_model.py:1609-1617`), then `intake = a.eta() * sh` (`:2151`). The flag's own docstring says its intent is "a person claims what they can actually harvest", so the second η contradicts it: the unconverted (1 − η)·share still leaves the economy, and a juvenile's take scales as η². Size of the effect NOT measured. |
| **F-02** 12× timescale error in the revolt accumulator | **CONFIRMED** | `_do_delegitimation` runs every step (via `_do_births_ibi`, every step); it adds `priv / ytr` with `ytr = resent_years_to_revolt = 80` (years). At unit privilege the threshold 1.0 is crossed after 80 steps = 6.7 yr, not 80 yr. The report's consequence ("explains the nobility share below its band") is UNSUPPORTED: #7 has no documented band. The quoted "years × 12" line in `_do_legitimacy` was not found. |
| **F-03.1** `enable_ascribed_mate_choice` dead in canon | **CONFIRMED** | Canon runs `_do_connubium` (adaptive connubium ON, `:706`); only `_pair_from_pool` reads the ascribed flag (`:5050`), and `_do_connubium` never calls it. |
| **F-03.2** `enable_marriage_aggregation` shadowed | **CONFIRMED** | `if adaptive_connubium … elif marriage_aggregation` (`:706-709`). |
| **F-03.3** band family knobs dead for mate choice | **CONFIRMED (partly as stated)** | `mate_choice_strength` via `_band_knob` is read only in `_pair_from_pool` (`:5075`); the knob's other effects (`patriline_weight`, `lineage_reversion`, `:3197, :3206`) are live. |
| **F-03.4** `enable_energetic_fertility` shadowed by intake fertility | **CONFIRMED** | `if intake_fertility … elif energetic_fertility` (`:3095-3102`); the code says "SUPERSEDES". An ON flag with no effect. |
| **F-03.5** `aggregation_site_sep` computed and discarded | **CONFIRMED** | cost only, no behaviour (`:5205-5214`). |
| **F-03.6** `rank_hierarchy_frac` + `asc_n` dead | **CONFIRMED for the parameter** | `asc_n` and `rank_frac` (`:2294-2302`) are never used — left over from R-98. The FLAG is live: R-99 (commit `a881ba5`) replaced it with a graded weight (`:5460`). |
| **F-03.7** village tier-2 yield negligible ⇒ `tier2_shock`, soil depletion, alluvial renewal, worked-land yield act on ~nothing | **CONFIRMED by measurement** | `settle_tier2_yield = 40` × Σ S_pot over 9 cells. Measured (test world, canon value): tier-2 term 258 kcal/step vs the site cell's 6.0 × 10⁶ kcal/step = **4.3 × 10⁻⁵**. The yield SHOCK, soil depletion, alluvial renewal and worked-land yield therefore barely touch food. **[Corrected the same evening:** this does NOT block a drought test — what binds at a village is the catchment ceiling (Σ of the 9 cell yields; measured median 6.7× need, binding at every occupied site), and the climate regime channel / `ClimateDriver` scales every cell yield, so a climate drought reaches village food. The drought test was run that way: RESULTS Add.117.**]** The report's attribution to "known issue #13" and a "400,000" comment is FALSE (no such issue or comment). |
| **F-04** village density disease uses a 25-cell regional density against the same reference as a 1-cell local density | **CONFIRMED (numbers corrected)** | With canon δ = 3, ρ½ = 0.2, ρref = 0.091: a 100-person village → multiplier 0.77; a 10-person mobile camp → 1.03. Two density definitions (regional vs local) are scored against one reference. |
| **F-05** `modal_adult_death = 75` is the 900-month lifespan cap | **CONFIRMED exactly** | Period table, temperate s0: exposure(75) = deaths(75) = 20,222 ⇒ m(75) = 12/yr, l(76) = 0, d(75) = 0.099 vs the natural peak ~0.013. ~10% of births die at exactly 75; e0/e15/e45 are truncated. |
| **F-05a.1** planar distances on a toroidal grid in several methods | **CONFIRMED (spot check)** | `_do_connubium` clips `max(0, fx − r)` (`:5152`), movement wraps. Impact probably small (central capacity patch); not measured. |
| **F-05a.2** metabolic down-regulation differs from MODEL_SPEC §4.6.7 | **PARTLY** | A mismatch exists, but not the one described: the spec drives `d` by the INTAKE EMA with max 0.25; the code drives it by the RESERVE fill fraction, and canon runs max 0.40. The report's "mirror-image ramp" is false (same shape). |
| **F-05a.3** infant males counted as hunters | **REFUTED** | The code counts males with `age >= menarche_months` (`:2139`); the quoted line does not exist. |
| **F-05a.4** the genome is not a pure observer | **CONFIRMED** | Founders draw from the world RNG (`:505`); budding cleaves by genome kinship. Known in the Stage-2 driver docstring, but it contradicts the "neutral marker" description. |
| **F-06a** `legit_frac_pop` always 0 under local ascription | **CONFIRMED** | tests the integer `a._lineage` against rank keys that are tuples (`:4563`); the line above uses `rk[a]` correctly. The `legit_threshold` vs relative-multiplier claim: NOT CHECKED. |
| **F-06b** `mean_resentment`/`max_resentment` always 0 | **CONFIRMED by data** | Temperate canon s0: both 0.0 for the whole run, while 1,235 revolts happened. The observer reads integer band ids; the accumulator keys `("v", site)`/`("b", band)`. |

## 2. Diagnosis of the standing anomalies (report Part III)

| claim | verdict | evidence |
|---|---|---|
| The body-condition signal is capped by post-burn sampling, so the synergy term is a constant | **CONFIRMED by data** | `condition_mean` = 0.321 on all three worlds; `a2_syn_mean` 1.47–1.48. The malnutrition × disease synergy acts as a FIXED ×1.47 on the hazard of everyone, not as a malnutrition signal. This also bears on the Add.112/113 risk calibration. |
| The synergy's under-5 multiplier (μ 2.5) is applied up to age 15 | **NOT CHECKED (plausible)** | the code switches at `menarche_months` (15 yr); MODEL_SPEC §4.3.3 itself calls μ "child-mortality data extrapolated". The age range of Pelletier 1994 must be read in the source. |
| `dep_load` charges the child's raw foraging deficit to the mother, whatever the granary or the father provide | **CONFIRMED in code; effect NOT measured** | `dep_load` uses `c._last_intake` (own foraging, `:2588`). That this lowers fertility after Add.108/113 is a hypothesis. |
| A stationary population with higher l(15) MUST have a lower TFR; the TFR band is from growing populations | **VALID CONSIDERATION, not settled** | The identity is correct in form, and `isogrowth_check()` exists to test it. But the band's lower end (4.69) is a low-growth contact population, so "must fall below" is not proven. A measured iso-growth check is needed. |
| The density-fill radius mismatch brakes fertility | known (Add.106; the fix is held dark) | the report's added factors (×1.29, total 3.59×) NOT CHECKED |
| Spousal band desynchronisation sterilises married women | **PARTLY** | the rule is real (conception needs the same band, `:3088`); how often spouses desynchronise is NOT measured |
| Orphan prevalence rose because the granary keeps orphans alive longer | **PLAUSIBLE; evidence FALSE** | the mechanism is reasonable; the cited "jump at add110_vgran" does not exist in `benchmark_history` (no such snapshot) and its numbers are wrong |
| Spatial traps: `enable_colonizing_budding = false`, `enable_bud_requires_occupancy = true` | **REFUTED** | canon is the opposite (colonizing ON, occupancy OFF) |
| Spatial traps: `_store_at` reads `self._granary` within the settle radius | **REFUTED** | no such code; the IFD values the store at the site key only |

## 3. Instrument and documentation findings

| finding | verdict | evidence |
|---|---|---|
| **F-07.1** monitor rows (TFR, IBI, m(5–15), orphanhood) are cumulative from step 0 | **CONFIRMED (core); effect small where measurable** | `run_campaign.py:493-494` call `life_table()`/`fertility_schedule()` without `since`. Measured: period vs cumulative m(5–15) agree within 5% in every arm, so "never hit" stands. TFR has no period snapshot, so its bias cannot be measured. The report's example numbers (e0 28.5) are FALSE; `load_addendum` does not exist. |
| **F-07.2** scorecard scores #18 against [30, 42] and #19 against [0.55, 0.75] | **REFUTED** | `tools/scorecard.py:64-65` use 21–37 and 0.45–0.66. (The real difference — the monitor scores Aché points ± tolerance, the matrix the G&K band — is stated in `02_BENCHMARKS.md`.) |
| **F-07.3** #1 weights adults-per-cell by all persons, not by adults | **OPEN definitional question** | the code is deliberately "person-weighted" (`phase1_model.py` comment at the field); whether Hill 2011's 28.2 is person- or adult-weighted must be read in the source |
| **F-07.4** `frac_fatherless` is 0 unless `enable_paternity_tracking` | **REFUTED** | no such flag; `frac_fatherless` is ~0.07 in every canon |
| **F-07.5** scorecard bands for #5 (5, 250), #6, #7 (1, 1e9), #8, #11 (0.05, 0.35), #17 unanchored | **REFUTED** | no such rows; #5, #7, #8, #11 are report-only; #17 is scored ≤ 250 on `settle_max` |
| F-07 vgran temperate seed 2 stopped at 14,460 steps | **REFUTED** | it ran to 15,000 |
| **F-09.1** `gen_registry.py` tag regex broken (`r"b"`) ⇒ "untagged 253" | **CONFIRMED — my bug, FIXED** | a shell edit earlier on 2026-10-26 turned `\b` into a literal `b`; the committed REGISTRY said 253 untagged while the package quoted 165/38/14/8. Fixed; counts now 164/39/14/8 (heuristic). |
| **F-09.2** `ClimateConfig` missing from class defaults | **CONFIRMED — FIXED** | climate flags showed "?" |
| **F-09.3** descriptions attributed to the wrong field | **CONFIRMED — mitigated** | the source places a field's comment above, below, or shared; no rule attaches it reliably. REGISTRY now gives each field's DEFINITION LINE and labels the description column a heuristic. |
| **F-10.1–3** `doc_audit.py` skips boolean/string and multi-name rows; stale rows hidden | **CONFIRMED** | stale PARAMETERS.md rows: `comove_footprint_scaled` (doc False / "not chosen"; canon true), `enable_condition` (doc "opt-in OFF"; canon ON), `ascribed_mate_strength` (doc 2.5; canon 1.5), `aggregation_site_sep` (doc 4; canon 10). My "0 disagreements" was true for numeric rows only. |
| **F-10.4** reference counts in the package are stale | **CONFIRMED (minor)** | counts move with each commit (73 → 71 after the package was committed) |
| **F-11.1** `comove_footprint_scaled = true` bypasses `comove_footprint` | **CONFIRMED — worse than known issue #15** | `phase1_model.py:1858-1860`. Canon runs the NPP-scaled footprint that PARAMETERS.md/R-43 call FALSIFIED; the unexplained `comove_footprint = 0` has no effect. |
| **F-11.2** `CarbonConfig` (κ 1.5 hardcoded) and `KcalEconomyConfig` absent from the run file and `config/*.toml` (κ 2.0) | **CONFIRMED; impact NOT measured** | `run_campaign.py:1323`; `config/parameters.toml` `[kappa] value = 2.0`. The run file is therefore NOT a complete statement of the run — the precedence rule in `00_START_HERE.md` must carry this exception. |
| **F-11.3** `genealogy = true` vs `enable_genealogy_log = false` in the run file | NOT CHECKED in effect | both lines exist as stated |
| **F-11.4** 141 of 145 run files fail `runspec.coverage()` | NOT CHECKED | — |
| **F-11.5** allowed-dark lists keep flags that are now ON; one-sided subset tests | **CONFIRMED** | `enable_density_reference`, `enable_energetic_refractory` are listed and ON |
| F-11.5b `enable_pair_bonds` disables `enable_bonded_mating` | **NOT CONFIRMED** | with pair bonds the bonded path checks the partner (`:3086-3092`); not an inversion as far as read |

## 4. Fixed now (tools and documents only — no model code)

`tools/gen_registry.py` (F-09.1 regex; F-09.2 ClimateConfig; F-09.3 definition lines + heuristic labels), the
regenerated `docs/REGISTRY.md`, the tag counts in this package, and "[Corrected after the external audit]" notes in
`01_CURRENT_STATE.md` (modal adult death; "0 disagreements") and `02_BENCHMARKS.md` (modal adult death; cumulative
monitor rows). Recorded in RESULTS Addendum 116.

## 5. Additional findings made during the review

1. **R-99 … R-105 have no ledger entries of their own.** They exist as commits (R-99 `a881ba5`, R-101 `be2311f`,
   R-102/103 `5f6add5`, R-104/105 in `dff049f`, `46eb0c9`) and are cited throughout, but `docs/RESULTS.md` has no
   `R-99` … `R-105` entry.
2. **The body-condition signal is constant at 0.321** (above) — a whole mechanism (`enable_condition` +
   `enable_nutrition_synergy`) reduced to a constant multiplier.

## 6. Proposed fixes, in order of consequence (supervisor's decision; each behaviour change needs the staged test)

1. **The food-shock channel (F-03.7):** the yield shock, soil and renewal act on a term 10⁻⁵ of the food supply
   (rescale `settle_tier2_yield` with an anchor, apply them to the binding catchment ceiling, or retire them). **[Corrected:
   this does not block the drought test — a climate drought reaches the binding ceiling; the supervisor chose to run that
   test first (Add.117).]**
2. **Mortality structure:** the lifespan cap (F-05), the constant synergy (§2), the regional-vs-local density
   reference (F-04), and the double η (F-01) — all four shape e0, l(15), m(5–15) and therefore the Add.113 adoption,
   which was calibrated with them in place.
3. **The elite layer's clock (F-02)** and its observers (F-06a/b).
4. **Dead ON flags (F-03.1–6) and stale documentation (F-10, F-11.1):** decide each flag (wire it or turn it off) and
   correct PARAMETERS.md / MODEL_SPEC.md for the footprint, condition and mate-choice rows.
5. **Configuration completeness (F-11.2):** put `CarbonConfig`/`KcalEconomyConfig` in the run file.
6. **Ledger:** write R-99 … R-105 entries (§5.1).
