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
| 1 | band size | `band_med` | **28.2 ADULTS** (Hill 2011, 32 societies) — the all-ages [18–35] is mis-attributed | Hill et al. 2011 `[VERIFIED, PDF read]`; ~~Johnson~~ | **FAILS 16/16 on adults** — model 11.8 adults/band = 0.42×. The 23/25 all-ages pass is carried by excess children |
| 2 | settlement size | `settle_med` | 100 [50–150] — **UNVERIFIED** | Bar-Yosef 1998, PDF now filed and read: gives site size comparatively ("three to eight times larger"), no population figure in the text | **21/25** against an unverified band; figures not machine-readable — needs a human read |
| 3 | village size | `settle_med` | [50–250] | Alvard 2009 — **VERIFIED VERBATIM** (Yanomamö "50 or so up to 250") | **21/25** |
| 4 | connubium reach | `connubium_med` | 150 [79–332] | White 2017 MVP; Wobst simulated MES | 15/25 — density-dependent, see note |
| 5 | lineage size Gini | `lineage_size_gini` | **ANCHOR WITHDRAWN 2026-08-04** | ~~BHM 2009~~ — see note | **NOT SCOREABLE** |
| 6 | lineage top share | `lin_top_share` | 0.16 [0.08–0.30] — **MIS-CITED, no replacement found** | 0.16 = **Yan 2014** Oα; 0.08 = **Zerjal 2003**; Karmin has neither. Hill 2011 was proposed as a forager-scale replacement and is NOT viable — it contains no lineage data at all | **7/25** — both sources are post-Neolithic/state-scale |
| 7 | nobility share | `ascribed_frac` | *undocumented* | EA "true-elite few %" | **NOT SCORED — band not in docs/** |
| 8 | fission rate | `bud_events` | 2–5×10⁻³ /large-village-yr | Bandy 2004 (3 events, largest village each phase) | 5.6×10⁻³ ✓ |
| 9 | hierarchy ordering | T-7 | structure range > productivity range | Smith & Codding 2021 — **VERIFIED VERBATIM** (r = 0.881, n = 89) | 2 of 3 proxies — unstable |
| 10 | **polygyny** | `frac_polygynous_m` | **~0.04** | Marlowe, *The Hadza* | **was 15× off; now 1.0×** |
| 11 | **status → RS** | `status_rs_r` | 0.15 monogamous / 0.19 cross-system | von Rueden & Jaeggi | re-measuring — old value was a polygyny artefact (R-77) |
| 12 | **rank-size slope** | `zipf_slope` | ≈ −1.0 (Zipf) | Johnson rank-size | **never previously scored**; first read −0.98 |
| 13 | **primacy** | `primate_ratio` | ≈1 = no primate centre | Johnson | **never previously scored** |
| 14 | **wealth concentration** | `material_gini`, `material_top10_share` | HG **0.36** / hort 0.52 / pastoral 0.51 / agric 0.57 (BHM Table S5, material column) | BHM 2009 (T-5) | **0.162** measured (0.131–0.185, 16 arms) — ~2× below the HG anchor |
| 15 | orphanhood | `frac_motherless` | ~0.02 | Aché, Hill & Hurtado | tracks |
| 16 | demographic engine | `median_age_yr`, `dependency_ratio`, `sex_ratio_m_f`, `frac_child` | sanity/context | — | context for 1–15 |

**HILL 2011 IS NOT A LINEAGE SOURCE (2026-08-06, PDF read).** `MODEL_SPEC` §4.8.8, `TARGETS` and `PARAMETERS`
all carry *"dominant-lineage share 0.38, ~7 lineages/band (Hill et al. 2011)"*. **The word "lineage" occurs
zero times in that paper.** Its unit is co-residence of PRIMARY KIN (brothers, sisters, parents, offspring);
the three "0.38"s are Table 1 cells (Nunamuit, Hadza, and a column average). This propagates:
`rank_hierarchy_frac = 0.15` is documented as DERIVED from the ~1/7. What Hill 2011 does give, verified:
**mean experienced band size 28.2 ADULTS**, **1.8 co-resident adult primary kin per band**, and that most band
members are genetically unrelated.

**ANCHOR-PROVENANCE SWEEP (2026-08-04, RESULTS Addendum 27).** Every cited source was located in
`literature/` and searched for its number. Of nine rows with a numeric band and a named paper: **2 verify**
(#3 Alvard verbatim, #14 BHM Table S5), **2 are mis-attributed** with the real numbers elsewhere in the folder
(#1, #6), **1 is withdrawn** (#5), **2 have no source in the repo at all** (#2, #9), and 2 name their
derivation well enough to trust (#8 Bandy, #15 Hill & Hurtado Table 13.1).

**The rows that survived are the ones whose citation named a table, a page or a sentence. Every row that
failed cited only an author and a year.** Charter §11 P5 as an acceptance criterion: **an anchor names its
table, or it is not an anchor.**

**#5's ANCHOR IS WITHDRAWN — BHM 2009 contains no lineage-size Gini (2026-08-04, the paper read).**
`literature/borgerhoff-mulder.som.pdf` is the SOM for *Intergenerational Wealth Transmission and the Dynamics
of Inequality in Small-Scale Societies* (Science 326:682). Every Gini in it is a **wealth** Gini: *"Population-
and wealth-type-specific Gini coefficients were calculated using the maximal sample of individuals … for whom
**wealth** and age data were available"*, age-adjusted against a quadratic in age, over 43 **wealth types**.
Table S5's material-wealth column reads pastoral **0.51**, horticultural **0.52**, agricultural **0.57** —
which is where [0.51–0.68] came from. It was a MATERIAL-WEALTH band applied to a LINEAGE-SIZE distribution,
i.e. the wrong quantity, not merely the wrong unit. (`ELITE_STRATIFICATION_ROADMAP` also quotes two
incompatible BHM ranges for this same marker, "0.51–0.68" at line 173 and "0.4–0.6" at line 190.)

BHM's band belongs on **#14**, where the project had already put it — and scored there against the
hunter-gatherer row (material Gini **0.36**) the model reads **0.162**, about half. #5's apparent 17/25 was a
pass against a borrowed band.

**#5 also has a UNIT problem, independent of the anchor.** `lineage_size_gini` is a Gini over `_rank_keys()`,
which under `enable_local_ascription` (ON in the canonical stack) returns **(community, lineage) pairs** — so
one patriline fragments into one unit per community. `lin_size_gini`, in the same row, is the Gini over
`_lineage` itself. They differ in 16/16 long arms and the sign of the difference flips between arms, which
reverses the reading: on the rank-key unit the full stack goes 1/8 → 8/8 in the old band; on the patriline it
goes 6/8 → 4/8. Both the quantity and the unit need deciding before #5 is scored again.

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

**#4/#5 the AGE-STRUCTURE markers had a single upstream cause (R-106, 2026-07-30).** `median_age_yr` ~13 and
`frac_motherless` 8–11% were not two failures but one: the fertility brake read a reserve level that cannot
vary, so births could not respond to crowding and **mortality did 100% of the regulating**. In a stationary
population e₀ = 1/CDR, so a CDR of ~50–77/1000 forces e₀ ≈ 20.7, a median age of 13 and a high orphan rate.
`enable_intake_fertility` closes **26–40%** of the gap on all four demographic markers at once:

| marker | before | after | anchor |
|---|---|---|---|
| e₀ (yr) | 19.1 | **21.4** | ~28 stationary (R-16) |
| `median_age_yr` | 13.4 | **15.2** | ~20 (Aché) |
| `frac_child` | 54.5% | **49.6%** | ~40% |
| `frac_motherless` | 11.8% | **7.9%** | ~2% (Hill & Hurtado) |

**Score these four TOGETHER, never singly** — they share a denominator in the vital-rate identity, so moving one
without the others is a sign of forcing rather than a fix. Still short of every anchor; next lever is counting
dependents in the fertility requirement (PARAMETERS §21.10).

**#14 is the live open question.** Material does not concentrate in the elite (`noble_material_lift` 0.87–1.04)
even with inheritance, tribute, noble exemption, zero decay and a narrow elite. Diagnosed as **no return on
capital**: `material` is a terminal stock that cannot buy anything, whereas Sahlins' big-man "uses wealth to
place others in his debt … he constructs a following whose production may be harnessed to his ambition."
