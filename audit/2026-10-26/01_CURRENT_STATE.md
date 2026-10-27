# 01 — Current state: what works and what does not (2026-10-26, Add.113 canon)

**Evidence base.** The nine Stage-2 runs of the canon: the real `run_campaign.py` pipeline, 3 canonical worlds × 3
paired demographic seeds, planet fixed (world/climate seed 0), 15,000 steps (≈ 1,250 years). Sustained window = the
last 15% of rows; #18–#21 from the period life table (steps 7,500–15,000). Committed numbers:
`docs/evidence/scorecard_add113_canon.json`; benchmark verdicts and their history: `02_BENCHMARKS.md`.

---

## 1. Bottom line

1. **The marker table passes.** Every banded marker of `docs/MARKER_MATRIX.md` passes on all three worlds at 1 SE,
   except two UNRESOLVED on temperate: #1 band size (40.2 ± 1.6 against ≤ 40) and #17 fission ceiling (232 ± 19 against
   ≤ 250). The four life-table markers #18–#21 pass on every world and every seed — for the first time (Add.113).
2. **The demography monitor does not fully pass.** Fertility is BELOW the forager band on every world (TFR 4.0–4.6
   against 4.69–8.03); it was in band on every world until Add.106 and was lost through the last adoptions. Mortality at
   ages 5–15 is 2–3× the Aché value and has never been in band. Orphanhood is high.
3. **The population does not disperse to its food.** The spatial paradox flag is TRUE on every run: packed locally,
   sparse regionally. By the project's own rule (root `CLAUDE.md`), carrying-capacity conclusions from such runs are void.
4. **No secular cycles;** the dynastic layer settles into a stable equilibrium. The Malthusian contraction under a
   shock is NOT tested.
5. **One planet.** Not replicated across world seeds.

---

## 2. What WORKS — the model

| area | what works | evidence |
|---|---|---|
| Age structure | dependency ratio, share under 15, sex ratio in the Hill & Hurtado band on every world, in every canon since Add.100 | `02_BENCHMARKS.md`; MARKER_MATRIX #16 |
| Mortality schedule | period e0 34.2 / 30.3 / 30.8, l(15) 0.62 / 0.55 / 0.58, e15 37.3 / 35.9 / 34.8, l(45) 0.39 / 0.33 / 0.33 — all inside the Gurven & Kaplan forager band; e45 in band. **[Corrected after the external audit: the "modal adult death 75" is an ARTIFACT of the 900-month lifespan cap (F-05, verified) — not evidence.]** | #18–#21; RESULTS Add.113 |
| Not a zero-sum fix | the Add.113 pair lowered child AND adult death rates on every world (unlike band provisioning, Add.108) | RESULTS Add.113 |
| Settlement system | village size (median 101 / 100 / 130), rank-size slope (−0.79 / −0.66 / −0.91), primacy (1.2–1.6), connubium reach (519–569) | #3, #4, #12, #13 |
| Family | polygyny 2–4% of men (Marlowe ~4%); age at first birth in band | #10; monitor |
| Wealth | material Gini of adults 0.38–0.41 (BHM 0.36); within-camp 0.28–0.31 (Agta 0.23 [0–0.44]) | #14 |
| Population genetics / dynasties | heterozygosity 0.95–0.97; effective lineages 53–78; dominant-lineage reproductive edge ~1.7× and stable | RESULTS Add.100; current runs |
| Spread | land use rose to 23% / 15% / 23% (savanna was 5% before Add.113) | RESULTS Add.113–114 |

## 3. What does NOT work — the model

| problem | numbers | since | record |
|---|---|---|---|
| **Fertility too low** | TFR 4.05 / 4.58 / 4.53 vs [4.69, 8.03] | temperate since Add.108, savanna/montane since Add.113 | `02_BENCHMARKS.md`; RESULTS Add.114 |
| **Mid-childhood mortality too high** | m(5–15) 0.022 / 0.028 / 0.026 per year vs Aché ~0.01 | never in band (5 canons) | `02_BENCHMARKS.md` |
| **Orphanhood high** | motherless 0.033 / 0.029 / 0.032 (Aché ~0.02); fatherless ~0.08 (Aché ~0.05) | fatherless since Add.113 | RESULTS Add.114 |
| **Birth intervals short on montane** | IBI 32 months vs [34.4, 49.4] | short on every world through Add.106; improving since (temperate now in band) | `02_BENCHMARKS.md` |
| **No dispersal to food** | occupied-cell density 0.16 / 0.14 / 0.12 per km² (> Binford 0.091) while regional density 0.036 / 0.021 / 0.027 | standing; Add.105 measured the population at 5–10% of carrying capacity on an earlier canon | root `CLAUDE.md`; RESULTS Add.47, Add.105 |
| **Starvation as a cause of death** | 15% / 29% / 21% of deaths (the forager record: illness dominates) | no cause-of-death marker exists | RESULTS Add.112 |
| **Band cohesion has no headroom** | assabiyah pinned at its clamp (median 1.000) | standing (Add.22) | `test_cohesion_headroom.py` |
| **#11 status → reproductive success** | 0.22 / 0.12 / 0.24; NOT COMPARABLE to von Rueden — the model lacks the status → partner-fertility channel | Add.102 | MARKER_MATRIX #11 |
| **Society classifier** | `pct_stratified` 19.9% / 0% / 0%; known defect history | R-103, Add.62, Add.100 | MARKER_MATRIX #9 |
| **No secular cycles** | four negatives | R-66, R-71, R-97; re-read in Add.105 | `docs/ROADMAP.md` |
| **Malthusian contraction on a shock** | not tested | — | `docs/ROADMAP.md` |

## 4. Software, reproducibility, documentation

**Works.**
- Test suite: 1,776 passed, 1 xfail (with `--capture=sys < NUL`; see `05_HOW_TO_RUN_AND_VERIFY.md`).
- **Determinism:** every control re-run of the arc (Add.108–113) reproduced the stored canon trajectory row for row
  (601 rows, identical life tables).
- Configuration ↔ code sync (`test_runconfig_sync.py`); registries ↔ sources sync (`test_registry_sync.py`);
  PARAMETERS.md NUMERIC values agree with the run file (0 numeric disagreements, `tools/doc_audit.py`). **[Corrected after the external audit: the tool skips boolean, string and multi-name rows; at least four such rows are stale — `comove_footprint_scaled`, `enable_condition`, `ascribed_mate_strength`, `aggregation_site_sep` (F-10, verified).]**
- Literature anchors: 32/32 registered anchors verify against their PDFs on the supervisor's machine.
- Every mechanism flag is read by model code (no dead switches by text search, `MAP_mechanisms_to_code.md`).

**Does not, or not fully.**
- Five configuration test files fail INTERMITTENTLY with `WinError 6` under pytest's default capture (Windows stdin
  handle; `--capture=sys` avoids it; RESULTS Add.111).
- 12 of the 15 PDFs behind the registered anchors are not in the public repository (copyright); they are committed on
  a LOCAL branch on the supervisor's machine only. Ask the supervisor.
- 73 broken file references in live documents (47 in the append-only RESULTS ledger) — `tools/doc_audit.py`.
- Provenance: 164 of 253 canonical parameters carry no provenance tag in their own source comment (a heuristic count, see REGISTRY §2); 12 flags have no
  comment of their own; two canon values have no recorded reason (`comove_footprint = 0`;
  `village_fission_threshold` 150 against the documented 170).
- The demography monitor still scores band size with `band_med_adults`, the statistic RESULTS Add.89 retracted.
- Many documents were last fully edited in July–August; stale parts carry dated banners (`04_MAP.md` §8).

## 5. Limits on what these results can claim

- **One planet;** population-scale quantities vary most with the planet draw (MARKER_MATRIX rule 3).
- **Adoption scope.** Until Add.114 the adoption tests scored only the targeted markers; the Add.113 adoption moved
  fertility, fatherlessness, #3-max, #11 and #15 without anyone looking.
- **Calibration, not prediction.** The forager bands are the training set: mechanisms were adopted because they moved
  these markers into band. The out-of-sample checks are other planets, other biomes, and markers no adoption targeted.
