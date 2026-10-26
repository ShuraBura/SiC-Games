# MODEL STATE — what works, what meets its benchmarks, and what does not (2026-10-26)

**Scope.** The state of the CANONICAL model (`config/runs/full_campaign.toml`, the R-106 Addendum-113 canon) against
every benchmark the project scores, plus the software state. Written for the audit at the supervisor's request.
**Evidence base:** the nine Stage-2 runs of the canon (real `run_campaign.py` pipeline; 3 canonical worlds × 3 paired
demographic seeds; planet fixed at world/climate seed 0; 15,000 steps), scored over the sustained window (last 15% of
rows) and, for #18–#21, the period life table (steps 7,500–15,000). Per world: mean over seeds (± SE where given).
Committed evidence: `docs/evidence/scorecard_add113_canon.{json,png}`; the analysis is RESULTS
Addendum 114. **This is a snapshot.** It becomes stale at the next adoption; re-score with `tools/scorecard.py`.

---

## 1. Bottom line

1. **The marker table passes.** Every banded marker of `docs/MARKER_MATRIX.md` passes on all three worlds at 1 SE,
   except two UNRESOLVED on temperate (#1 band size, #17 fission ceiling). This includes the four life-table markers
   #18–#21, which pass on every world and every seed for the first time (Add.113).
2. **The demography monitor does NOT fully pass.** About 11.7 of its 16 benchmarks are in band. Fertility (TFR) is
   BELOW the forager band on every world; mortality at ages 5–15 is 2–3× the Aché value; orphanhood is high (§3).
3. **The population does not disperse.** The spatial paradox flag is TRUE on every world: packed locally, sparse
   regionally. By the project's own rule (root `CLAUDE.md`), such a population is not food-limited, so carrying-
   capacity conclusions from these runs are void (§4).
4. **No secular cycles,** and the dynastic layer sits in a stable equilibrium. The Malthusian CONTRACTION under a shock
   is not tested yet.
5. **Every result rests on ONE planet** (world/climate seed 0), with three demographic seeds.

---

## 2. Marker table (MARKER_MATRIX), by benchmark-ladder tier

✅ PASS at 1 SE · ⚠️ unresolved (straddles a band edge) · ❌ FAIL · ▫️ reported without a verdict (no documented band,
or report-only by a recorded decision). Values: temperate / savanna / montane.

| tier | marker | values | verdict | note |
|---|---|---|---|---|
| 3 Demography | #16 dependency ratio | 0.71 / 0.74 / 0.75 | ✅✅✅ | Hill & Hurtado T4.4 [0.598, 0.899] |
| 3 | #16 share under 15 | 0.33 / 0.34 / 0.35 | ✅✅✅ | [0.287, 0.454] |
| 3 | #16 sex ratio | 1.07 / 1.05 / 1.07 | ✅✅✅ | [0.896, 1.368] |
| 3 | #18 e0 (period) | 34.2 / 30.3 / 30.8 | ✅✅✅ | G&K forager band 21–37 (Hiwi 27 for savanna) |
| 3 | #19 survival to 15 | 0.620 / 0.554 / 0.577 | ✅✅✅ | band 0.45–0.66 (HG avg 0.57) |
| 3 | #20 e15 | 37.3 / 35.9 / 34.8 | ✅✅✅ | band 28.6–42.5 (HG avg 37.7) |
| 3 | #21 survival to 45 | 0.392 / 0.333 / 0.333 | ✅✅✅ | band 0.26–0.43 |
| 3 | #15 orphanhood (motherless) | 0.033 / 0.029 / 0.032 | ▫️ | Aché point ~0.02, no band; ROSE with Add.113 (savanna was 0.017) |
| 5 Bands | #1 band size (adults per co-residence cell) | 40.2 / 29.9 / 27.7 | ⚠️✅✅ | Hill 2011 28.2, range ~12–40 |
| 6 Family | #10 polygyny (of all men) | 0.031 / 0.038 / 0.023 | ✅✅✅ | Marlowe ~0.04 [0.02, 0.06] |
| 6 | #11 status→RS | 0.22 / 0.12 / 0.24 | ▫️ | NOT COMPARABLE: the model lacks the anchor's channel (Add.102) |
| 7 Kin | #5 lineage dynamics | — | ▫️ | per-generation rates not computed by the scorecard |
| 7 | #7 nobility share | 0.014 / 0.023 / 0.022 | ▫️ | no documented band |
| 8 Connubium | #4 connubium reach | 519 / 569 / 526 | ✅✅✅ | Wobst ~475; floor 150 |
| 9 Settlement | #3 village size (median) | 101 / 100 / 130 | ✅✅✅ | Alvard 50–250 |
| 9 | #3 village size (max, Voronoi catchment) | 350 / 305 / 546 | ▫️ | report-only: the ceiling is scored at #17 (Add.104) |
| 9 | #17 fission ceiling (co-resident max) | 232 / 119 / 103 | ⚠️✅✅ | Alberti 158 / Alvard ≤ 250 |
| 9 | #12 rank-size slope | −0.79 / −0.66 / −0.91 | ✅✅✅ | Zipf ≈ −1 [−1.5, −0.6] |
| 9 | #13 primacy | 1.22 / 1.40 / 1.56 | ✅✅✅ | ≈ 1 [1, 2] |
| 9 | #8 fission rate | — | ▫️ | per large-village-year rate not computed |
| 10 Material | #14 material Gini, adults | 0.410 / 0.381 / 0.377 | ✅✅✅ | BHM 2009 0.36 [0.30, 0.42] |
| 10 | #14 material Gini, within cell | 0.309 / 0.298 / 0.277 | ✅✅✅ | Agta within-camp 0.23 [0, 0.44] |
| 11 Stratification | #9 hierarchy ordering (`gini_cred`) | 0.52 / 0.36 / 0.36 | ▫️ | pre-registered cross-world test, not computed |

Full numbers with SE and per-seed values: MARKER_MATRIX "CURRENT SCORECARD"; figure `docs/evidence/scorecard_add113_canon.png`.

---

## 3. The demography monitor (`demography_health`, 16 benchmarks; RESULTS Add.43)

This panel runs in every campaign snapshot. It overlaps the marker table but scores more quantities, some against a
single Aché point with a tolerance (a DEVIATION, not a failure). Share of sustained-window rows out of band:

| benchmark | anchor | temperate | savanna | montane | state |
|---|---|---|---|---|---|
| frac_child, dependency, sex ratio | H&H 1996 T4.4 bands | in band | in band | in band | ✅ |
| realised_e0, e15, e45, surv_to_15, surv_to_45, modal adult death, age at first birth | G&K 2007 / Walker 2006 | in band | in band | in band | ✅ |
| **realised_tfr** | **[4.69, 8.03]** H&H 1996 T8.1/8.2 | **4.05 (100% out)** | **4.58 (100% out)** | **4.53 (100% out)** | ❌ fertility too LOW on every world |
| realised_ibi_med (months) | [34.4, 49.4] | 36.2 (0%) | 34.6 (38%) | **32.3 (100%)** | ❌ montane intervals too short |
| **m_5_15** (deaths per person-year, ages 5–15) | ~0.01 ±50% (G&K p.330) | **0.022 (100%)** | **0.028 (100%)** | **0.026 (100%)** | ❌ mid-childhood mortality 2–3× Aché |
| frac_motherless | ~0.02 ±50% | 0.033 (66%) | 0.029 (42%) | 0.032 (63%) | ⚠️ high |
| frac_fatherless | ~0.05 ±50% | 0.084 (81%) | 0.084 (76%) | 0.079 (63%) | ⚠️ high |
| band_med_adults | ~28.2 ±25% | 50.1 (62%) | 58.9 (76%) | 24.1 (10%) | **instrument defect, see below** |

**Notes.** (a) `realised_tfr` and `realised_ibi_med` are run-level measures (not the period table of #18–#21); the
founding transient is a small share of a 15,000-step run, but the direction of its bias is NOT measured. (b) A short
IBI with a low TFR is not a contradiction in itself (a short reproductive span, or many women with few births, gives
both); the cause is NOT diagnosed. (c) **Instrument defect:** the monitor still scores band size with
`band_med_adults`, the statistic that RESULTS Add.89 RETRACTED (wrong statistic, wrong unit); marker #1 uses the
corrected `band_experienced_adults`. The monitor's band-size verdict is therefore not evidence either way, and the
monitor should be updated (not done in the audit preparation).

---

## 4. Population dynamics, space, and the macro questions

| question | state | evidence |
|---|---|---|
| Is the population stationary? | yes: growth +0.007 to +0.04 %/yr; `growth_regime` stationary/constrictive | trajectories (Add.114 context) |
| Does it spread over its land? | partly: land use 23% / 15% / 23% (savanna was 5% before Add.113) | scorecard context rows |
| **Does it disperse to its food?** | **NO — spatial paradox TRUE on all worlds:** occupied-cell density 0.16 / 0.14 / 0.12 per km² (above Binford's 0.091) while the regional density is 0.036 / 0.021 / 0.027 per km² (below it) | `spatial_health()` banner; root CLAUDE.md "packing paradox" |
| Is it food-limited? | not established; Add.105 measured 5–10% of carrying capacity on the PREVIOUS canon; NOT re-measured | RESULTS Add.105 |
| Who goes hungry? | savanna: 10% of agents past menarche have an intake EMA below 0.73 of need; temperate/montane p10 above 1.1 | trajectories |
| Starvation share of deaths | 0.15 / 0.29 / 0.21 (forager record: illness dominates); no cause-of-death marker | Add.112–114 |
| Malthusian CONTRACTION on a shock | NOT TESTED | ROADMAP "CURRENT STATUS" |
| Secular cycles | NONE; dynastic concentration settles in a stable equilibrium (dominant-lineage RS edge ~1.7×, effective lineages 78 / 53 / 57) | R-97, Add.100, current runs |
| Society classifier (`pct_stratified`) | 19.9% / 0% / 0% stratified, ~80–99% "complex"; it read 0% everywhere at Add.100. The classifier has a recorded defect history (R-103, Add.62) and is context only | MARKER_MATRIX #9 |
| Band cohesion | assabiyah pinned at its clamp (median 1.000) — the known blocker of Add.22, pinned by a test | `test_cohesion_headroom.py` |

---

## 5. Software, reproducibility and documentation

**Works.**
- Test suite green: 1,773 passed + the new registry tests, 1 xfail (run with `--capture=sys < NUL`, see below).
- **Determinism.** Every control re-run of the arc (Add.108–113) reproduced the stored canon trajectory row for
  row (601 rows, identical life tables), so the new default-OFF flags are bit-exact when off.
- Config ↔ code sync (`test_runconfig_sync.py`); registries ↔ sources sync (`test_registry_sync.py`); 0 PARAMETERS.md
  values disagree with the run file (`tools/doc_audit.py`); 32/32 registered literature anchors verify on the
  supervisor's machine (`tools/verify_anchor.py --list`).

**Does not, or not fully.**
- Five config test files fail INTERMITTENTLY with `WinError 6` under pytest's default capture (a Windows stdin-handle
  artifact; `--capture=sys` avoids it — RESULTS Add.111).
- 12 of the 15 PDFs behind the registered anchors are not in git (copyright); a clone cannot verify them.
- 96 broken file references in live documents (70 in the append-only RESULTS ledger).
- Provenance: 165 of 253 canonical parameters carry no provenance tag in their own source comment; 12 flags have no
  comment of their own; two canon decisions have no recorded reason (`comove_footprint = 0`;
  `village_fission_threshold` 150 vs 170) — REGISTRY.md, RESULTS Add.114.
- Many documents were last fully edited in July–August; their stale parts carry dated banners or notes (AUDIT_GUIDE §4).

---

## 6. Limits on what these results can claim

- **One planet.** World and climate seed 0 for all three worlds; the demographic seed varies (3). Population-scale
  quantities vary most with the planet draw (MARKER_MATRIX rule 3). Not replicated across planets.
- **Adoption decisions scored only targeted markers** until Add.114; the Add.113 adoption moved #3-max, #11 and #15
  without anyone looking (Add.114 §2).
- **Calibration, not prediction.** The forager bands are the training set: several mechanisms were adopted because they
  moved these markers into band. Out-of-sample checks are the other planets, the other biomes, and the markers that no
  adoption targeted.
- **Absolute values are valid only on this canon** (MARKER_MATRIX rule 5).
