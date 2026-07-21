# SiC Games — Dead Ends

**The ONE question:** "What did we try and abandon, and why?" (charter §2, home 11).

**Discipline:** append-only. Records approaches retired or deprioritized so they are not silently re-attempted. A dead end may be *revived* by a dated note if circumstances change — it is a record, not a tombstone.

---

## DE-1 — H-ORTHOGONALITY as a live pre-registration (deprioritized 2026-06-05)

**What it was:** a pre-registered hypothesis that C and Si home-range distributions occupy *orthogonal* axes of the foraging×social movement space (C social-pull-weighted, Si foraging-pull-weighted) — a difference-set, not a scale difference.

**Why deprioritized (not deleted):** the asymmetry is **near-implied by construction** — the C2 classification (ψ = proximity-to-agents for C vs proximity-to-foraging-spots for Si) already builds it in, so a "confirmation" would largely restate the design rather than risk it (low capacity to embarrass us). It also has no scheduled run and requires the OWE-13 movement-decomposition diagnostic, which is not built. It therefore fails the HYPOTHESES test ("could a pending run prove it wrong?") and was routed out of HYPOTHESES.md.

**Where it lives now:** **TARGETS.md T-2** — retained as an aspiration worth *measuring* if/when OWE-13 is built, with its original test spec preserved. It graduates back to a HYPOTHESIS if/when OWE-13 is scheduled and a magnitude threshold for "orthogonal vs parallel-but-scaled" is pre-committed.

---

## DE-2 — The bare `forage_kcal` field as the bands substrate (abandoned 2026-06-26)

**What it was:** running emergent bands on `TerrainField.level` (forage_kcal × hours, ~1–8 persons/cell).
**Why abandoned:** a 100 km² cell can't feed a 25-person band on it (median land cell <1 person, ~1-step reserve buffer) → a seeded band wipes out in ~2 steps; "bands" only "persisted" as corpse piles (R-22). **Replaced by** the CC-1 NPP-capacity field (`NPPCapacityField`, ~30–50/cell), the regime where a cell holds a band and crowding is density-disease-regulated. The bare field's own docstring already flagged it provisional. (See RESULTS R-22; MODEL_SPEC §4.8.4.)

## DE-3 — Storage-tethering (`storage_tether_reserves`) (retired 2026-06-29)

**What it was:** freezing a stocked band in place so it concentrates past Binford packing → the morph trigger.
**Why retired:** a band-aid for the *pre-bands* max-occupancy-2 dispersal. With emergent bands (grouping + bonded mating) the morph fires from emergent density+storage alone (R-23); the tether only added over-concentration artifacts (≈4× pop, spurious stratified_chiefdom). Config field + movement guard deleted. *Revive only if a future substrate again can't reach packing emergently.*

## DE-4 — Risk-dilution as a MORTALITY penalty (`enable_band_risk`) (shelved 2026-06-29)

**What it was:** a loner/small-band mortality penalty (safety-in-numbers wired into the death schedule).
**Why shelved:** it's a **death spiral, not a stabilizing optimum** — mortality culls but does not aggregate (penalty 0→6: pop 281→64, R-24). Risk-dilution is already expressed *behaviorally* via the E.1 movement drive; banding's fitness teeth are the F.1 mate-gate. Flag **kept in, default-OFF, with a caveat** (not deleted — available for future experiments). *Revive only with a mechanism where the penalty drives aggregation, not just death.*

## DE-5 — The per-conception paternity LOTTERY as the reproduction model (superseded 2026-06-29)

**What it was:** assign a fresh prowess-weighted father at every birth (`enable_paternity` without pair-bonds).
**Why superseded:** an idealized "any high-prowess male fathers any birth" mechanism = polygyny-like → it reproduces the von Rueden *cross-system* average (0.19), not a marriage-system-specific value. The **family stack (persistent pair-bonds + modest polygyny)** replaces it as the realistic reproduction model → status→RS ≈0.13 (the monogamy-dominant value, R-26). The lottery's m=5→0.19 calibration (E.3-proper, R-21) is **retained as the superseded simpler-mechanism reference**, not the current model. (MODEL_SPEC §4.8.12.)

## DE-6 — Forcing the full-stack status→RS to 0.19 (not pursued 2026-06-29)

**What it was:** the temptation to bump `mate_choice_strength` until the monogamy-dominant family model hits 0.19.
**Why not pursued:** 0.19 is the polygyny-inflated cross-cultural *average*; von Rueden's monogamous-society value is r≈0.15, so forcing 0.19 would *over*-skew a monogamy-dominant society relative to the evidence. **0.13 is accepted as the marriage-system-appropriate target** (R-26). The honest route to a higher per-band skew is *condition-dependent polygyny* (rich bands) + a future *wife-quality* channel, not a global m bump.

## DE-7 — `season_aggregation` as a threshold cohesion-multiplier (RETIRED — field removed 2026-07-01)

**What it is:** `season_aggregation` scales the `tolerable_size` headroom by `ClimateField.season()` — so a lean season LOWERS tolerable → *fission* (lean → disperse), a threshold-channel term.
**Why retired:** two faults found in the fission-driver review (R-31). **(1) Mis-signed:** the ethnography says *moderate* lean drives **aggregation** (risk-pooling — Cashdan 1985, Wiessner 1982; Hadza dry-season water aggregation — Hawkes 1991), not fission; only *severe* scarcity fissions (and that as movement-dispersal, ahead of mortality). **(2) Inert:** it acts on the fission threshold, which is DORMANT at equilibrium (0/26 bands near tolerable, R-31) — so it does nothing anyway. **Superseded by** the movement-channel non-monotonic resource response (blueprint `…_MovementChannel_ResourceResponse_Scoping.md`, stages M1 risk-pool aggregation / M2 starvation dispersal): seasonal lean now enters through realized per-capita adequacy `a = ypc/need` on the *binding* movement channel, with the correct sign. `season_aggregation=0` was already the default ⇒ removal is bit-exact. **DONE 2026-07-01:** config field + the `_maintain_bands` `season_ab` factor deleted; callers (run_3o, run_se0, test_morph) updated; full suite green. *Revive only if a threshold-channel seasonal term is ever shown to bind.*

## DE-8 — M1 moderate-lean aggregation cohesion (dropped 2026-07-01)

**What it was:** a proposed anti-fission cohesion drive under *moderate* lean ("risk-pool → aggregate → don't split").
**Why dropped:** failed the "does it help food-wise?" test (supervisor review). The one real payoff — risk-pooling variance reduction — is **already implicit** in within-cell meat sharing, and bands already equilibrate at ~20 ≈ Wobst 25 (not under-aggregated), so M1 solved a non-problem. The "Hadza waterhole aggregation" motivation is agents *following spatially-concentrated resources* — that is the existing IFD movement, not a new anti-fission force. And the distinction matters: a starving family joining a resource-rich band is resource-SEEKING **fusion** (built as F, DE-none) — NOT the anti-fission cohesion M1 posited. The correct moderate-lean behaviour is simply *no fission pressure* (achieved by retiring `season_aggregation`, DE-7), not an added aggregation force. **Revive only** if a functional payoff for moderate-lean anti-fission cohesion is identified, or if biome-dependent concentration-vs-spreading dynamics are modelled and demand it. (See MODEL_SPEC §4.8.14; the surviving design is M2 severe-scarcity fission + F resource-directed fusion.)

---

## DE-9 — Productivity-scaled mobility as the biome→society collapse fix (falsified 2026-07-03)

**What it was:** the hypothesis (R-39, supervisor-flagged) that the low-NPP (savanna/desert/mixed) biome→society collapse is caused by **fixed-r=1 diffusion mobility** — agents can't spread over sparse territory, pile onto the few rich cells, overcrowd, and starve — fixable by a productivity-scaled movement stride (Kelly/Binford mobility ∝ 1/productivity).
**Why falsified:** the mechanism was BUILT (`enable_productivity_mobility`, §4.8.19, default-OFF, bit-exact, 10 unit tests) and ablated (R-40). It does **not** rescue the collapse and is consistently **mildly harmful** (savanna survival 2/3→0/3; every archetype eq_pop ON ≤ OFF). Two probes killed the pile-up premise: (1) the founder seed-stack decompresses to occ/cell ~1.7 within 25 steps in BOTH arms — **there is no persistent pile-up**; the collapse is a slow chronic bleed. (2) The **actual** lever is FAMILY CO-MOVEMENT: savanna @900 steps → pop 3 with co-movement, **327 without**, 3 with mobility ON. Co-movement forces dependents onto the head's cell, coupling the family to one marginal cell's yield → chronic per-capita deficit. Ranging farther worsens dispersal below mate/band viability without touching the co-location cause.
**Status of the code:** the mobility mechanism is **kept** — valid, ablatable, default-OFF; it is simply not the biome fix, and its calibration was never locked. **Revive** the mobility LINE only for its own purpose (residential-mobility gradients / annual range, seasonal transhumance), not as the biome→society remedy. The live next lever is the co-movement mechanic (footprint / provisioning-off-head / productivity-gated co-movement) — see R-40. (MODEL_SPEC §4.8.19; R-39→R-40.)

## DE-10 — Single-band cell-packing to force concentration (superseded 2026-07-04)

**What it was:** the attempt to make ONE band (~25) concentrate onto a rich cell and cross Binford packing by adding a movement force on top of IFD — first the economic-defensibility **tether** (owner-band members get a per-capita bonus on their owned reach, outsiders a penalty; `enable_economic_defensibility`), then a **consolidate-to-primary-reach** tether, then a **cohesion-redirect** (point the band's cohesion at its owned cell).
**Why superseded:** on the natural substrate the mechanism was **inert** — IFD spreads a band ~1.4/cell, so the claim gate (≥3 same-band on a defensible cell) never fires (bootstrapping fails on unsaturated land — the R-51 coupling). With a pioneer claim (`claim_min=1`) and a dense seed it *did* form ownership and conferred a real **survival edge** (DEFEND out-survived OFF), but it **never packed**: the *local* tether only holds members already adjacent, it cannot GATHER scattered ones; and pushing harder (cohesion-redirect) tipped straight to a **death spiral** (300→34) because concentrating a small band onto one cell over-subscribes it (residence coupled to foraging → starve on your own cell). There is a razor-thin band between "inert" and "collapse" with no packing in between. Root cause is the same across all variants and matches R-51/DE-none: **an unsaturated landscape has too few people/area to pack, and no local force manufactures density a sparse population lacks** — AND the *unit* was wrong (Q1 lit: settlements are multi-band coalescences, not one band digging in).
**Status of the code:** the defensibility claim/ownership lifecycle + the observed fitness edge are **kept** (default-OFF) and are **folded, at the correct CATCHMENT grain,** into the aggregation-sedentism settlement (R-52) — the cell-vs-cell exclusion and single-band tether are retired as the concentration mechanism. **Revive** defensibility only as the *between-settlement* catchment defense (the contested-catchment / Carneiro follow-on). Superseded by **R-52** (aggregation-sedentism: multi-band coalescence + single-cell residence + tier-2 unlock — which packs where this could not). (Blueprints `…_EconomicDefensibility_Scoping.md` §7, `…_AggregationSedentism_Scoping.md`.)

## DE-11 — Catchment-agglomeration as a village concentrator (a saturating congestion function, not Bettencourt) (2026-07-06)

**What was tried:** the "grand-unification" agglomeration economy — each cell offers an intensive catchment resource `R(c) = tier2·Σ_catchment(S_pot·…)`, and a co-located group of n captures total `R·L(n)`, `L(n)=n^α/(n^α+half^α)`, so per-capita `R·L(n)/n` was meant to be single-peaked in n → aggregation/packing/villages emerge under IFD (blueprint `…_AgglomerationEconomics`). Applied to movement (perceived) AND harvest (realized).

**Why it fails (fundamental, not tuning):** `L(n)` **saturates** (→1), so the total captured `R·L(n)` hits a CEILING and per-capita `R·L(n)/n` **peaks then falls (∝1/n)** — a congestible common-pool. This is the mathematical *opposite* of an agglomeration economy: Bettencourt has total output ∝ N^β (β>1) so per-capita ∝ N^(β−1) *rises* without bound → cities nucleate; here per-capita *declines* past the peak → dispersal at scale. We had mistaken `α` (a logistic saturation *sharpness*) for Bettencourt's scaling exponent `β` — unrelated. In simulation the term is *areal-dispersive*: it rewards being anywhere in a fertile *catchment* (a 3×3 sum), which competes with packing onto a *single* fertile cell, and — being an additive rider that grows only sub-linearly (n^(α−1)) while GRP's grouping multiplier grows fast — it *dilutes* the packed-vs-empty gradient GRP builds. Cranking `tier2` therefore **monotonically reduces** packing (26→21→15%). A units bug (R mis-scaled ~10⁴ too big — `harvest_field.level()` kcal-capacity used as if a 0–1 fraction → R≈54M ≈18×S) initially masked the sign by letting a huge R defeat the forage cap and re-reward lone agents; fixing R (=tier2·Σ(S_pot·cv_ref)) only shrank the effect, it did not flip its sign.

**Status / superseded by:** replaced by the **POINT** form (Bettencourt-correct, R-54): the cell's OWN output scales super-linearly with its occupancy, per-capita premium `A_cell·(n^(β−1)−1)` *rises* with co-location and composes with (reinforces) GRP+cap packing. `aggl_mode="catchment"` is KEPT for comparison only (default `"point"`). The village-scale concentration ultimately comes from **forage cap + GRP + hierarchy-gated fission ceiling + catchment site-appraisal × resource scarcity** (R-54/R-55), not from any single co-location term.

## DE-12 - "Wide-net -> scatter": connubium REACH as the driver of the boom-bust (REFUTED 2026-07-13, R-67)

**What was tried:** Cut-2 (adaptive exogamous ring-search mating) robustly broke R-66's winner-take-all patriline
fixation (top 0.89 -> 0.21-0.31), proving that fixation was a MATING-STRUCTURE artifact - but every reach setting
boom-busted. The hypothesis was that a WIDE marriage net scatters people across the landscape and collapses the
population, so narrowing the reach should fix it.
**Why it fails:** REFUTED by direct test - **narrower reaches busted HARDER**, the opposite of the prediction. The
real driver is skew-flattening: Cut-2 drops childless males 37% -> 23-28%, which removes the Malthusian brake.
Reach width is not the lever. **Do not retune reach to cure a boom-bust.**
**Status:** connubium arc CLOSED. Cut-2 stays default-OFF on branch `connubium-cut2` (not adopted). A separate
skew-preservation fix is the open option, deferred.

## DE-13 - The m*=25 "recovery" as a secular-cycle seed (NEGATIVE 2026-07-13, R-67)

**What was tried:** at connubium m*=25 the population showed a peak-then-recover shape that looked like the first
period of a Turchin secular cycle. Tested properly: 45k steps x 2 seeds.
**Why it fails:** a **one-off founder-overshoot transient, not cycling** - single peak ~yr170, then a flat low
plateau (~2000, vs Cut-1's 6400 over 43k steps); both seeds concordant. Dynasties slowly re-concentrate
(top 0.02 -> 0.3-0.4) but never fixate and never cycle. **A single peak in a short window is not a cycle** - always
run to multiple would-be periods before calling one.

## DE-14 - Secular cycles from the SUBSISTENCE BASE (three independent negatives; standing as of 2026-07-15)

**What was tried, three times, from three different directions:** (i) mating structure / connubium (R-67);
(ii) the substrate's own attractor dynamics (R-68); (iii) agricultural soil depletion -> abandonment -> re-settle,
the most promising candidate since it is a genuine oscillator in principle (R-71).
**Why it fails:** all three are stable or transient. R-71 is the sharpest: emergent abandonment CURED the
population ratchet (collapse -> equilibrium ~14,421 +/- 4.5%, 25 settlements churning) but produced **no cycles** -
rotating swidden is a STABLE regime, which is also ethnographically correct.
**Conclusion (load-bearing):** **secular cycles are NOT in the subsistence base.** They require either exogenous
shocks (`enable_tier2_shock`, default-OFF) or the explicit Turchin elite/instability layer. **Do not attempt a
fourth subsistence-side route to cycles without a new argument for why it differs from these three.**

## DE-15 - Band size as an ENVIRONMENT-DEPENDENT emergent quantity (FAILED 2026-07-17, R-72)

**What was tried:** `enable_emergent_band_size` v3 - derive band size from risk-pooling against environmental
variance, so that Marlowe's 25-50 range emerges from biome rather than being hardcoded at 25.
**Why it fails:** the environment-dependence does not appear - seeded correlation r = +0.165, n.s. Three separate
explanations for the null were each falsified by measurement. The measured `cchunts` hunting CV (2.11) carries
**no biome signal**, so there is no environmental variance gradient for band size to track in the first place.
**Status:** ARC CLOSED. The mechanism remains but does not deliver environment-dependence; band size stays
effectively ~25. Note the flag is default-OFF, so band size is currently HARDCODED 25 across all biomes - a known
limitation whenever biomes are compared.

## DE-16 - status->RS r~0.19 as a robust standing result (RE-CLASSIFIED as artifact 2026-07-17, R-76/R-77)

**What it was:** R-19/R-20's headline "lineage of chiefs" result - status -> reproductive success at r ~ 0.19,
matching von Rueden's cross-cultural figure.
**Why it is not what it looked like:** the skew was carried by **~6x too much polygyny**. The polygyny mechanism
had no outflow, so the rate knob never actually worked and the realized rate ran far above the configured one. At
a realistic ~4% rate the correlation caps at ~0.07. Wife quality closes only about a third of the gap (0.07 vs
0.19).
**What survives:** von Rueden's 0.19 is a CROSS-CULTURAL average inflated by polygynous societies; the
monogamy-dominant family model should target ~0.13-0.15, which it reaches. **Do not cite 0.19 as a matched
target for a monogamous configuration.**

## DE-17 - The FERTILITY channel for wife quality (structurally inert 2026-07-17, R-80)

**What was tried:** route the wife-quality effect through fertility, so that higher-status men's wives have higher
birth rates.
**Why it fails:** structurally inert - overflow and need are anti-correlated in this economy, so the channel has
no purchase regardless of coefficient. **This is a specification problem, not a tuning problem**; a bigger
coefficient cannot rescue it.

## DE-18 - Aggrandizer capture at the CELL unit (wrong unit 2026-07-17, R-82 -> R-83)

**What was tried:** Hayden-style aggrandizer capture of redistributed output, executed per CELL.
**Why it fails:** a cell holds 1-2 agents under forager dispersal - **there is no group to skim.** Capture stayed
inert at 1.14x even at 80% capture, which reads as "the mechanism does not work" but is really "the unit is
wrong."
**Superseded by R-83:** the same mechanism at the BAND unit (~25) gives leader/other 3.68x. **General lesson:
before concluding a social mechanism is inert, check the SIZE of the group it operates on.**

## DE-19 - `succession_dissolve` measured against the band MEAN (vacuous 2026-07-18, R-84)

**What was tried:** Sahlins' big-man dissolution regime, implemented as "a successor must exceed the band MEAN
merit by `office_challenge_margin` (+25%), else the band stays leaderless."
**Why it fails:** the maximum of ~25 lognormal-ish merit draws clears +25% over the mean essentially always, so
the flag had **literally zero effect** - identical output, zero vacancies, ON and OFF. A mechanism that PASSES
WHILE DOING NOTHING (same failure class as the R-74 vacuous test that asserted `1.0 == 1.0`).
**Fixed, not abandoned:** re-specified against the NEAREST RIVAL rather than the mean - 2/18 bands leaderless,
which is the intended interregnum. **Standing check: if a flag's ON/OFF output is indistinguishable, treat that as
a specification bug, not a small effect size.**

## DE-20 - Per-birth SINGLETON lineage branching (wrong shape 2026-07-20, R-90 -> R-92)

**What it was:** with probability `lineage_branch_rate`, a newborn founds a whole new `_lineage` - the standard
infinite-allele device, already used by `genome_mutation`.

**Why it failed:** a new line starts with exactly ONE member, and a lineage of one usually leaves no
descendants. So it produced a churning tail of ephemeral names: at campaign scale n_lineages rose 5 -> 32 while
`eff_lineages` FELL 3.4 -> 1.8 and `top_share` ROSE 0.42 -> 0.73, and `lineages_per_band` barely moved
(2.14 -> 2.33 against a target of ~7). **Count up, substance down.** Judged on `n_lineages` alone it looked
like a success - the failure is only visible on the effective-diversity measure.

**Superseded by** R-92 segmentation: branching now seeds a heritable `_subclan` tag (singletons harmless at
sub-branch level) and a separate operator promotes one to a full lineage only once it HAS grown. The device is
therefore not dead, only relocated - which is why the flag and rate survive with changed meaning.

## DE-21 - Splitting a lineage by walking ANCESTOR CHAINS (not computable 2026-07-21, R-92)

**What it was:** the textbook definition of a sub-clade - pick a living apical ancestor, split off exactly its
live patrilineal descendants. The first cut of R-92.

**Why it failed, and it is a fact about the model rather than the idea:** MEASURED, live `_father` chains reach
a MAXIMUM DEPTH OF 2 (median 1) even after 400 steps. A chain terminates at the first ancestor born without an
assigned father, and early births largely lack one (father-link rate 19% at step 80, rising to 74% by step 400).
So "the descendants of an ancestor" can never be more than a handful, and the mechanism silently did nothing.
Deep ancestry exists only in the offline genealogy CSV stream, never in memory.

**Superseded by** the heritable `_subclan` tag, which CARRIES the sub-clade instead of reconstructing it - and
which is, conveniently, exactly what a Y-haplogroup label is. **Revive only if** per-agent ancestry is ever
retained in memory; note that was presumably avoided deliberately, since retaining the full ancestry graph over
a 45,000-step run is unbounded.

---

*End of DEAD_ENDS — seeded 2026-06-05. Append-only; revive with a dated note.*
