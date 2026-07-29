# Marker matrix — the scorecard for a well-working model

**Purpose.** One table, scored on every significant run, that says whether the model reproduces the
ethnographic and archaeological record. A run that does not carry these numbers cannot be said to have been
validated, however long it ran.

**Binding rules, each earned the hard way:**

1. **Every band is re-verified against `LITERATURE.md` at run time.** A benchmark whose anchor has been retired
   is **skipped with a note, never scored** — Battery 5 reported "connubium 0/7" against a target this project
   had retired two weeks earlier, manufacturing a defect that did not exist.
2. **A marker with no documented band is not scored.** `ascribed_frac` has been reported as a headline failure
   for weeks against a 3.6–7.8% band that appears nowhere in `docs/`. Unverifiable is not the same as failing.
3. **Seeds must beat the variance.** R-65 documented 30× seed variance in `%stratified`. Single-point verdicts
   on high-variance markers are not evidence.
4. **Markers travel together.** A wealth marker read on a steeply growing population means something different
   from one read at stationarity, which is why the demographic-engine block is scored alongside, not separately.

---

## The matrix

| # | marker | field | band | source | status |
|---|---|---|---|---|---|
| 1 | band size | `band_med` | 25 [18–35] | Johnson scalar stress; R-72 | **23/25** |
| 2 | settlement size | `settle_med` | 100 [50–150] | Bar-Yosef; R-63/R-64 | **21/25** |
| 3 | village size | `settle_med` | [50–250] | Alvard 2009 | **21/25** |
| 4 | connubium reach | `connubium_med` | 150 [79–332] | White 2017 MVP; Wobst simulated MES | 15/25 — density-dependent, see note |
| 5 | lineage size Gini | `lineage_size_gini` | [0.51–0.68] | BHM 2009 | 17/25 |
| 6 | lineage top share | `lin_top_share` | 0.16 [0.08–0.30] | T-9 Karmin 2015 | **7/25 — weakest** |
| 7 | nobility share | `ascribed_frac` | *undocumented* | EA "true-elite few %" | **NOT SCORED — band not in docs/** |
| 8 | fission rate | `bud_events` | 2–5×10⁻³ /large-village-yr | Bandy 2004 (3 events, largest village each phase) | 5.6×10⁻³ ✓ |
| 9 | hierarchy ordering | T-7 | structure range > productivity range | Smith & Codding 2021 | 2 of 3 proxies — unstable |
| 10 | **polygyny** | `frac_polygynous_m` | **~0.04** | Marlowe, *The Hadza* | **was 15× off; now 1.0×** |
| 11 | **status → RS** | `status_rs_r` | 0.15 monogamous / 0.19 cross-system | von Rueden & Jaeggi | re-measuring — old value was a polygyny artefact (R-77) |
| 12 | **rank-size slope** | `zipf_slope` | ≈ −1.0 (Zipf) | Johnson rank-size | **never previously scored**; first read −0.98 |
| 13 | **primacy** | `primate_ratio` | ≈1 = no primate centre | Johnson | **never previously scored** |
| 14 | **wealth concentration** | `material_gini`, `material_top10_share` | BHM by society type | BHM 2009 (T-5) | low — the open question |
| 15 | orphanhood | `frac_motherless` | ~0.02 | Aché, Hill & Hurtado | tracks |
| 16 | demographic engine | `median_age_yr`, `dependency_ratio`, `sex_ratio_m_f`, `frac_child` | sanity/context | — | context for 1–15 |

Markers **10–14 and 16 were wired on 2026-07-27**; before that they were computed by `demography()` every step
and never carried into a campaign trajectory, so **no long run in this project's history has ever scored them.**
That is how polygyny sat 15× off Marlowe unnoticed: nothing was looking.

---

## Notes that must travel with specific markers

**#4 connubium is density-dependent — do not score it pooled.** Measured corr(density, connubium) = **+0.55**
across 25 arms: sparse boreal worlds give 7.5–48, dense worlds give 85–173, straddling the ~150 anchor. A
pooled "15/25" reads as a failure and is mostly an artefact of including near-dead worlds. Score it against
density, or restrict to arms above a density floor.

**#7 nobility share is not scoreable.** `docs/` record only "EA true-elite few %". The precise 3.6–7.8% band
came from somewhere and was never filed. File the Ethnographic Atlas source with its numbers and this marker
starts scoring automatically.

**#9 the T-7 ordering is unstable.** It holds on 2 of 3 hierarchy proxies, but *which* proxy violates has moved
between runs (`gini_cred` once, `lineage_size_gini` the next). Pre-register one proxy as *the* hierarchy index
before scoring, or the verdict is chosen after the fact.

**#11 status→RS must be re-measured, not carried over.** R-77 established the old +0.170 was an artefact of 6×
excess polygyny. With polygyny corrected the expectation was ~+0.019; a first short run reads 0.117. Needs a
full-length run before it means anything.

**#14 is the live open question.** Material does not concentrate in the elite (`noble_material_lift` 0.87–1.04)
even with inheritance, tribute, noble exemption, zero decay and a narrow elite. Diagnosed as **no return on
capital**: `material` is a terminal stock that cannot buy anything, whereas Sahlins' big-man "uses wealth to
place others in his debt … he constructs a following whose production may be harnessed to his ambition."
