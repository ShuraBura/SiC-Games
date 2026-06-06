# SiC Games — Pre-Registered Hypotheses

**Purpose:** The authoritative record of what the project *predicted before looking at the data*, and how each prediction resolved. This document exists to prevent HARKing (Hypothesising After Results are Known). A hypothesis written here *before* the run that tests it is a genuine prediction; a "hypothesis" written after seeing results is a description, and the project does not count it as confirmation.

**Discipline:**
- **Append-only.** Never edit a hypothesis after its test has run. Add a dated **Resolution** block beneath it instead.
- Every entry has: an ID, the date registered, the claim (falsifiable), the test specification (what run, what statistic, what threshold), the pre-committed interpretation of each outcome, and the stage/artifact that will test it.
- "Pre-committed interpretation" means: state *before the run* what each possible outcome would mean, so the result cannot be reinterpreted to fit.

**Status key:** `OPEN` (registered, not yet tested) · `RESOLVED-SUPPORTED` · `RESOLVED-REFUTED` · `RESOLVED-AMBIGUOUS` · `SUPERSEDED`.

---

## H1(ii) — Strategy resilience (the project's central question)

**Status:** partially RESOLVED (and inverted from the naive prior).
**Claim:** Of the two civilisational strategies, one is more resilient to periodic resource shocks than the other.
**Standing result (Stage 5.x):** Si goes extinct at A=0.75 / T=200 (both seeds, by t≈1500), while C persists — the resilience comparison *inverts* the naive "individualist self-reliance is robust" prior, and the inversion is robust to a more capable Si (Stage 5.1 Si Cred). Full resolution awaits the multi-condition (topology × forcing) ensemble. See RESULTS.md for the finding, ARTIFACTS.md for the runs.
*This entry is a back-reference to the pre-existing central hypothesis; it is recorded here so the ledger is complete. The hypotheses below are the ones registered going forward.*

---

## H-EMERGE-1 — Emergent group structure from topographic heterogeneity

**Registered:** 2026-05-29.
**Status:** OPEN.
**Centrality:** HIGH. This is a load-bearing pre-registration: the group-level dynamics the project intends to study later (differential cohesion, asabiyyah, between-group effects) are only legitimate to pursue if group structure *emerges* from existing mechanisms rather than being imposed. This hypothesis tests that precondition. It is registered now, before the terrain-topography stage exists, precisely because it would be tempting to assert after the fact ("groups emerged, as expected") — writing the prediction first is the honest order.

**Claim (falsifiable):**
On a single world with sufficiently large spatial extent and heterogeneous topography (distinct resource regimes — e.g. a highland regime and a valley regime), and at a population large enough to sustain a viable sub-population in each region, the existing mechanisms (local-neighbour Deffuant cultural transmission + spatial sorting + biparental/fission reproduction) will produce **spatially-partitioned cultural differentiation** — regions will develop measurably different distributions of the cohesion-relevant traits (c1, c2, and ψ) — **without any group-level mechanism being added.** Group structure is predicted to be an *emergent partition*, not a coded construct.

**Mechanistic grounding (see LITERATURE.md once logged):**
- Epstein & Axtell (1996), Sugarscape "tribes": spatial structure + local interaction produces persistent cultural groups with no group-level rule. `[INLINE]`
- Turchin (2003) asabiyyah-on-frontiers: cohesion differentiates most sharply at high-contrast regime boundaries — i.e. exactly where topography creates them. `[INLINE]`
- Metapopulation / habitat-heterogeneity (population ecology): regions of differing carrying capacity structure local interaction and persistence. `[UNVERIFIED — general]`

**Test specification:**
- **Run:** the terrain-topography stage (roadmap: terrain → LHS → Stage 6), single world, heterogeneous topography with ≥2 distinct resource regimes, C strategy (and separately Si), Deffuant ON, existing mechanics only — **no group-membership code, no group-level cohesion variable, no between-group mechanism.**
- **Scale (from the 2026-05-28 perf audit, see ARTIFACTS.md):** N ≈ 1000–2000 (the N-axis is ~linear, exponent 1.05 — affordable), grid 150×150 as the first test point (B3/B4: 343–410 ms/step, 3.6–4.3 h for a 300-run LHS at 4 workers). **The binding constraint is grid extent, not N** — the grid exponent is 2.957 (near-cubic), so spatial separation is the expensive axis. Test 150×150 for sufficient regime separation *before* reaching for 200×200+; if 150×150 is too cramped, do the deferred grid-cost optimisation (perf audit §6, target exponent ≤2.0) rather than brute-forcing a larger grid.
- **Primary statistic:** Moran's I for c1, c2, ψ at steady state (the diagnostic already exists, present since Stage 3.3). High Moran's I = spatial autocorrelation = regional clustering of traits.
- **Secondary statistic:** regional trait distributions — partition agents by topographic region and compare per-region trait means and dispersions (SD, not Gini — see MODEL_SPEC §6 statistic note). Bimodality of a trait *across* the whole world that resolves into *unimodal-but-different* distributions *within* regions is the signature of emergent groups.
- **Seeds:** ≥8 (a 2-seed result cannot distinguish genuine structure from a single lucky partition; cf. the Stage 5.2 σ-sweep bistability problem).

**Pre-committed interpretation (state before the run):**
- **Supported:** Moran's I for c1/c2 is high and stable, and regional trait distributions differ significantly and consistently across seeds, with no group-level code present. → Emergent group structure is real on existing mechanisms; the asabiyyah / differential-cohesion programme is empirically grounded and may proceed to *measurement* (still not to imposed-group mechanisms).
- **Refuted:** Moran's I stays low / traits stay well-mixed across regions despite topography. → Existing interaction/movement ranges are too long relative to world extent for groups to persist. The correct response is **geometric** (larger world or shorter interaction radius), **not** a new mechanism. Re-test before concluding groups cannot emerge.
- **Ambiguous:** structure appears in some seeds/regions but not others, or depends sensitively on grid size. → Likely a marginal-separation regime (interaction range ≈ inter-region distance); characterise the dependence on grid/radius before any group-level work.

**Explicitly NOT licensed by this hypothesis (TMTS guard):**
A *supported* result licenses **measuring** emergent group properties. It does **not** license adding: hierarchical lumping / family-cell base units (circular — pre-imposes the group structure being explained, and destroys the within-group trait heterogeneity that is the object of study), group-membership tracking, group-level cohesion variables, or between-group competition. Those remain deferred and would each need their own registration. The coupled-metapopulation architecture (worlds linked by migration, between-group selection) is a separate, distant evolution (architecture 2; ROADMAP BatchRunner is architecture 1 — *independent* ensemble worlds — and does not provide between-group selection).

**Resolution:** *(none yet — OPEN)*

---

*End of HYPOTHESES — 2026-05-29.*
