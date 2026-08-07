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
| 2 | ~~settlement size~~ | ~~`settle_med`~~ | **RETIRED 2026-08-06** | Bar-Yosef 1998: PDF filed, read, and confirmed by the supervisor to be maps and burial sites — no village-population figure exists in the text to find | **Retired at zero cost to coverage:** it was a second, unverifiable band on the *same field* as #3, whose band is verified. Nothing was being measured here that #3 does not measure |
| 3 | village size | `settle_med` | [50–250] | Alvard 2009 — **VERIFIED VERBATIM** (Yanomamö "50 or so up to 250") | **46/52 arms PASS** (2026-08-06 re-score over every trajectory on disk; median of arm medians **97.5**) |
| 4 | connubium reach | `connubium_med` | 150 [79–332] | White 2017 MVP; Wobst simulated MES | 15/25 — density-dependent, see note |
| 5 | lineage size Gini | `lineage_size_gini` | **ANCHOR WITHDRAWN 2026-08-04** | ~~BHM 2009~~ — see note | **NOT SCOREABLE** |
| 6 | ~~lineage top share~~ | ~~`lin_top_share`~~ | **RETIRED 2026-08-07 — SCORED AGAINST THE WRONG KIND OF SOCIETY** | 0.16 = **Yan 2014** (Neolithic Chinese super-grandfather haplogroups); 0.08 = **Zerjal 2003** (the Genghis Khan haplogroup). Karmin, also cited, has neither. Hill 2011 was proposed as a forager-scale replacement and contains **no lineage data at all** | **Retired at 7/25.** The diagnostic is UNCHANGED and still reported every run — only the SCORING stops |
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
| 17 | **fission ceiling** | `settle_max` | communities should not persist far past **158 [147–170]** (max scalar stress) and effectively never past **250** (ethnographic maximum) | Alberti 2014 `[VERIFIED VERBATIM]` + Alvard 2009 `[VERIFIED VERBATIM]`; Hamilton 2007 periodic aggregation **165.32 [152.25–181.00]** independently lands on the same scale `[VERIFIED VERBATIM]` | **MISSES — screen only.** Over 52 trajectories the median `settle_max` is **220**; **39/52 exceed 158** and **18/52 exceed 250**. The typical village is right (#3) while the largest one over-runs the size at which both sources say communities break up |

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

**SWEEP CLOSED 2026-08-06 (RESULTS Addendum 29).** The three papers the supervisor fetched settled the two
open rows and the sweep was then extended to the climate layer wired on 2026-08-04, which had never been
checked at all.
- **#2 retired.** Bar-Yosef holds no village-population figure — confirmed by the supervisor's own read. It
  was a duplicate band on #3's field, so retiring it costs no coverage.
- **#17 added.** Alberti 2014 and Hamilton 2007 both verified verbatim and both land on ~160 for the
  aggregation ceiling, giving `settle_max` a two-source anchor where it had none.
- **#6 RETIRED 2026-08-07 (supervisor decision).** Smith & Codding 2021 was fetched and verified, but for
  #9's ordering claim, not for a lineage share, and no forager-scale lineage-concentration source exists
  in the folder. Its band came from **Yan 2014** (Neolithic Chinese super-grandfather haplogroups) and
  **Zerjal 2003** (the Genghis Khan haplogroup) — both measure Y-chromosome dominance in large,
  post-Neolithic, state-scale populations where one man's descendants could out-reproduce everyone for
  forty generations. **A forager band of 20–60 with a mate-gate and high mortality cannot structurally
  reach that concentration**, so the 7/25 was never evidence about the model. Retired rather than left
  visibly broken, because a marker that fails permanently for a reason everyone has to re-learn is a
  warning that trains people to ignore warnings. **The diagnostic is unchanged and still reported.**
- **Climate, first check ever:** Sarmiento, Wanner, Hawkes and Timmermann's *period* all verify (Hawkes via a
  documented conversion that reproduces 518/745 to the unit); **Timmermann's amplitude does not exist in the
  paper** and is now tagged INTERPRETIVE; **St. John 2022 has no PDF** and its channel is default-OFF.
- **The checker is now code:** `tools/verify_anchor.py --list` re-reads every PDF and
  `sic_games/tests/test_anchor_provenance.py` fails the suite if any wired number stops being findable in its
  own source. Prose could drift; this cannot.

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

**#17 — ALBERTI'S 127 IS A THRESHOLD, NOT A CENTRAL BAND. Scoring it as one was nearly the fourth instance of
this project's unit-mismatch bug class (2026-08-06).** Alberti 2014 verified verbatim: *"a critical scalar
stress threshold at community size 127 (95% CI: 122–132), while the maximum probability of critical scale
stress is predicted at size 158 (95% CI: 147–170)."* Those CIs are tight and tempting, and the obvious move —
add `settle_med ∈ [122, 132]` as a row — is **wrong**, and would have scored **0/52**. 127 is the size at
which a community *starts to come apart*; a population whose median village sat there would be a population
permanently mid-fission. The quantity Alberti bounds is the **ceiling**, so the field is `settle_max` and the
test is one-sided. Same family as the three that came before it: `hayden_stage` on occupied vs regional
density, `lineage_size_gini` on rank-keys vs patrilines, `connubium_med` on `pool_n` vs `reach_pop`. **Every
one of them was a real number read against the wrong denominator, unit, or statistic — never a wrong number.**

**#14 AND #17 SURVIVED THEIR OWN CONFOUND TESTS (2026-08-07, `test_marker_diagnostics_ctb.py`).** Both
were reported as failures while the diagnostics computing them had **no test anywhere**, which by CLAUDE.md's
first rule made them claims about the instrument rather than about the model. Both were then CTB'd, and both
held:

- **#14 `material_gini`.** The measured vector runs over the WHOLE population, children included, and children
  hold nothing. Adding zero-holders can only push a Gini **UP** — so the child confound cannot explain a
  reading that is 2× BELOW the anchor; correcting for it widens the gap. Separately, BHM's 0.36 is
  **age-adjusted** (a quadratic in age, removing the life-cycle component), which *lowers* their figure, while
  ours is raw. So we compare a raw-inflated 0.162 against an adjusted-reduced 0.36 and are still 2× under.
  **The miss is real and, if anything, understated.** The methodological mismatch should travel with the
  number.
- **#17 `settle_max`.** A MAXIMUM grows with sample size at a fixed distribution — verified on constructed
  normal draws, where E[max] rises by >15 units from n=5 to n=50 — so an arm with more settlements could
  report a larger `settle_max` without its settlements being any bigger. **Measured across the 52 arms:
  corr(n_settle, settle_max) = +0.024** — essentially nil, against corr(n_settle, settle_med) = −0.328. The
  confound is real in principle and **not operating in this data**, so #17's over-run is not an artefact of
  settlement count.

**#17's status is a SCREEN, not a score.** The 52 trajectories were run for other purposes across different
worlds, run lengths and flag stacks, several predating R-105/R-106 fixes. They establish the *direction* and
that the marker is worth wiring; they do not give a calibrated figure. It needs a proper campaign before the
miss is sized.

**#3 and #17 come from the same field and must be read together.** `settle_med` passing while `settle_max`
over-runs is not a contradiction — it is the diagnosis: fission fires, but not hard enough at the top of the
distribution. A single "village size" verdict would have averaged these into a meaningless pass.

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
