# SiC Games — Connubium (emergent mating-network scale) Blueprint (v1.0, 2026-07-08)

**Goal.** Make the ~500 regional mating network (Wobst 1974 "magic numbers" 25/500) **emerge** from an
individual-level **exogamy rule** on the agents we already track, replacing the hard-coded spatial `aggregation_radius`
that causes the "thousands pile up during the gathering" pathology. Success = the realized mating-network size is a
*prediction* (~475, Wobst) that also **varies with the kinship-taboo stringency** — not an input.

## The physics: connubium = minimum mate-availability network
A band (~25) is far too small to be a self-sufficient breeding pool: under any real incest/exogamy prohibition almost
everyone in your band is kin, so you *must* marry out. The connubium is the smallest network that reliably contains
enough eligible (non-kin, opposite-sex, age-compatible) partners. Mate-availability math (validated bracket):

    N* ≈ m* / ( ½ · b · ℓ(a_m) · τ · c · (1−k) )

with the model's own constants b = 1/e₀ = 1/36.5 ≈ 0.027, ℓ(15) = 0.66 (menarche), m* = famine-safety margin (~3,
the 5 %-mate-famine Poisson point), τ ~ search years, c age-compat, (1−k) non-kin fraction ⇒ **N* ≈ 300–600, centres
~400, straddles Wobst 475.** But c/k/τ are fudge factors *only in the closed form* — in-sim they are computed exactly
from real ages and the real genealogy, so we let the pool self-organize and VALIDATE against ~475 + this bracket.
(Structural parallel: band g* = (CV/cv_safe)² from subsistence variance; connubium N* from mate-availability — both
"emergent minimum viable group size from a stochastic shortfall.")

## The mechanism (what replaces `aggregation_radius`)
1. **Real exogamy rule** (the driver) in `_pair_from_pool` — reject a candidate who is:
   - the same `_lineage` (clan/patriclan exogamy — the cultural rule, strongest driver), AND/OR
   - a sibling (shared `_mother` or `_father`) / parent / child (nuclear incest — exact from existing pointers), AND/OR
   - (optional depth) relatedness > r* via the neutral `genome` (cousin+; needs enable_genome).
   Degree is set by `exogamy_degree ∈ {lineage, nuclear, cousin}` — the anthropological lever.
2. **Search-to-eligibility** (the scale) — an unpaired adult expands its mate search ring-by-ring (Chebyshev r =
   1,2,3,…) until it accumulates ≥ m* eligible non-kin candidates (or a max reach). Pair prowess-weighted as now.
   The realized catchment self-organizes; no target number is set. This supersedes the fixed radius (whose blindness
   to *who* is in the circle is the pile-up bug — a size/eligibility-driven search self-limits).
3. **Connubium diagnostic** — `world.connubium()`: the realized mating-network size = the connected component of
   agents linked by (marriage ∪ shared-catchment), or the mean distinct-person count within realized search reach.
   Validate its median lands ~475 (300–600 bracket) and RISES with taboo stringency (lineage < nuclear < cousin).

## Parameters (all new, default OFF ⇒ bit-exact)
- `enable_exogamy: bool = False` — master switch for the real kin/clan prohibition.
- `exogamy_degree: str = "lineage"` — {"nuclear" (parents/sibs only), "lineage" (+ patriclan), "cousin" (+ genome r>r*)}.
- `exogamy_relatedness: float = 0.125` — r* for the cousin degree (first-cousin threshold), needs `enable_genome`.
- `mate_search_min_eligible: int = 3` — m*, the famine-safety margin (the connubium's `cv_safe`; anchor ~3 / sweep).
- `mate_search_max_radius: int` — cap on ring expansion (a real travel limit; the OLD `aggregation_radius` becomes this).

## Validation
- **Median connubium ≈ 475** emerges (single most important check; 300–600 bracket acceptable).
- **Stringency gradient:** connubium rises lineage → nuclear → cousin (a prediction the fixed radius cannot make).
- **Pile-up fixed:** no thousands-on-a-cell during gatherings once search is eligibility-driven.
- Downstream sanity: eq-pop, band size (~24, R-battery), status→RS still hold (this touches the validated pairing path
  → full re-validation; expect headline mating numbers to move, re-validate on the branch).
- Population genetics (if enable_genome): exogamy should RAISE heterozygosity / LOWER inbreeding vs. endogamy (a
  cross-check that the rule does real genetic work).

## Cuts
- **Cut 1** — exogamy rule (lineage + nuclear, existing fields) in `_pair_from_pool` + `connubium()` diagnostic;
  measure the emergent pool on the CURRENT gathering pool. Default OFF, bit-exact. (This turn.)
- **Cut 2** — search-to-eligibility ring expansion replacing the fixed `aggregation_radius` (the real emergent scale).
- **Cut 3** — cousin-degree via `genome` relatedness; stringency-gradient validation; retire the fixed radius.

## Relation to the rest
Sits atop the `genome` substrate (046a32f — optional cousin depth + inbreeding cross-check) and the band-size work
(bands are the connubium's units). The connubium is the mating-network layer BELOW villages; the village endogamy
correction (a large co-resident village ≈ a local connubium ⇒ relaxed gathering) is a later thin modifier on top.

*Blueprint 2026-07-08. Implementation tracked in RESULTS as it lands.*
