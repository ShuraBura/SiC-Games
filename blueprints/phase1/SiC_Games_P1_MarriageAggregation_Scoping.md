# SiC Games P1 — Seasonal Marriage-Aggregation ("the gathering") (SCOPING + RED-TEAM)

**Goal.** Dispersed bands **periodically aggregate at an abundant site** (in the resource-abundance window), where
**unpaired adults pair ACROSS bands** (exogamy → the regional connubium), then disperse. This fixes the biome→
society bug (the fixed daily co-residence mate-gate collapses low-density savanna/desert populations — R-37) the
*right* way: marriage operates at the **regional/connubium scale via seasonal aggregation**, not a permanently wide
radius. Result: families + bands form in EVERY biome (as they must — Hadza/Ju/'hoansi have families), and the
biome→society difference shows up where it belongs (mobility · band size · sedentism · stratification), not in
whether families exist.

**Governing principle: FULL CUSTOMIZABILITY.** An opt-in flag (default OFF, bit-exact = today's daily-local
pairing). Touches reproduction → supervisor sign-off; re-validate.

---

## Motivation

- **R-37 (biome→society):** on the realistic Tallavaara CC-1 substrate, forest thrives (complex-forager society) but
  savanna/desert/montane **collapse** — NOT for lack of capacity (simple reproduction sustains 355–896) but because
  the bonded mate-gate needs an unrelated adult male within **1 cell (~900 km²)** of the mother every step. At CC-1's
  realistic low densities, sparse bands can't meet that → births stall → extinction. **This is a bug** (marginal
  foragers DO have families), not a finding.
- **The real dynamic (well-attested):** the **aggregation–dispersal cycle** — dispersed small bands most of the year,
  periodic large gatherings for marriage/exchange/ritual timed to a resource peak (so the crowd can be fed). Marriage
  is a **connubium-scale** event (Wobst ~500), realized through these gatherings — not daily co-residence.

## Design — "the gathering"

Every `aggregation_period` steps (≈annual = 12), during the seasonal-abundance window, dispersed bands converge on
abundant sites and pair across bands:

1. **WHEN (season-gated).** Fires when `ClimateField.season()` is near its peak (the abundance window — the user's
   "spring"), once per year (period). On a static/no-climate field, fire on a fixed phase of the period. Gate:
   `season() ≥ aggregation_season_threshold`.
2. **WHERE (abundant sites).** Aggregation sites = the top-capacity cells (`harvest_field.level`), min-separated
   (`aggregation_site_sep`) so ~one site per region. (Ties to the C.5 water-aggregation seam — abundant cells are
   often near water.)
3. **WHO (the regional connubium).** Each band is assigned to its nearest site within `aggregation_radius`; the bands
   sharing a site are that gathering's marriage pool = the emergent **community/connubium** (the band→community nest).
   **Radius = a realistic TRAVEL-TO-GATHERING distance**, lit-anchored: Wobst 1974 connubium (~500 people) + forager
   marriage/mobility ranges ≈ tens–~100 km → **~5–10 cells** (cell edge = 10 km, cell = 100 km²). NOT density-
   adaptive (people won't walk 1000 km for a wedding); a fixed travel radius. **A band with no other band within
   range gets no gathering → no cross-mating → it may die out. That is ACCEPTABLE/realistic** (isolated marginal
   bands do go extinct — supervisor "se la vi"); do NOT artificially rescue it.
4. **MARRIAGE (cross-band, exogamous — with virilocal absorption + rank homogamy; red-team #2).** For each site,
   pool the site's bands' **unpaired adults** → run the prowess·cred-weighted, kin-avoiding `_do_pairing` on that
   REGIONAL pool → durable pair-bonds (F.3a). Two lineage-preserving rules: **(i) virilocal residence** — the bride
   joins the GROOM's band + adopts his lineage (children patrilineal; the wife's natal lineage doesn't propagate),
   preventing male-line flattening; **(ii) rank homogamy** — pairing weights combine the directional ascribed-mate-
   choice (high-cred groom preferred) with B++ status assortment (like-cred pairs), so the cred gradient survives the
   mixing. So a low-density band's members find spouses at the gathering even though their daily neighbourhood is
   empty — without dissolving lineages. **Residence is a switchable ENUM** `aggregation_residence ∈ {virilocal
(bride→groom, default), uxorilocal (groom→bride), flexible (the existing smaller→larger-band rule)}` — both
directions wired so we can run virilocal- vs uxorilocal-world experiments (Ember & Ember subsistence link;
biome-localized residence is a future study, not hard-coded). **Rank matching is a switch** `aggregation_rank_
homogamy ∈ [0,1]` (0 = random/directional only; 1 = strong like-cred homogamy).
5. **DISPERSE + REPRODUCE year-round.** After the window, no new pairing until next gathering; **births proceed
   throughout the year via the persistent pair-bond** (the bond, set at the gathering, is the birth licence — the
   daily co-residence mate-gate is replaced by "has a living partner"). Bands disperse via the normal movement.

**Key insight:** this DECOUPLES *finding a mate* (hard at low density → solved by seasonal regional aggregation)
from *reproducing* (year-round via the durable bond). It reuses `_do_pairing` + pair-bonds; the only new thing is
**widening the pairing POOL to the regional connubium at the seasonal gathering**, instead of daily-local.

**Config:** `enable_marriage_aggregation: bool=False`, `aggregation_period:int=12`, `aggregation_season_threshold:
float` (peak window), `aggregation_radius:float≈5–10` (connubium/travel range, cells), `aggregation_site_sep:float`,
`aggregation_residence ∈ {virilocal,uxorilocal,flexible}`, `aggregation_rank_homogamy:float∈[0,1]`. When ON, the
daily bonded-mate-gate for *pairing* is superseded by the gathering; births gate on the pair-bond.

## Literature (to file — supervisor to grab the gated ones)

- **Mauss & Beuchat (1904/1979), *Seasonal Variations of the Eskimo*** — seasonal social morphology (dense
  winter aggregation ↔ summer dispersal); the foundational aggregation–dispersal text.
- **Steward (1938), *Basin-Plateau Aboriginal Sociopolitical Groups*** — Great Basin Shoshone "fandangos": dispersed
  family bands aggregating at pine-nut/antelope-drive abundance for marriage + socializing. The closest analogue.
- **Lee (1979), *The !Kung San*** — dry-season **waterhole** aggregation (marriage, hxaro, trance-dance) ↔ wet-season
  dispersal. Anchors the abundant-site + season timing.
- **Conkey (1980), "Prehistoric HG aggregation sites: Altamira," *Current Anthropology*** — the archaeological
  signature of periodic aggregation.
- **Wobst (1974)** (FILED) — the connubium (~500) is viable only via periodic gatherings; daily co-residence is far
  too small a mating pool. Anchors the connubium scale.
- **Hamilton et al. 2007** (FILED) — the nested band→community→connubium (~4× ratio) that aggregation realizes.

*Residence-mode (virilocal/uxorilocal):* **Marlowe 2004, "Marital residence among foragers"** (FILED) — foragers
modally multilocal with a virilocal lean; **Hill et al. 2011** (FILED) — bilateral, flexible, low-relatedness co-
residence; **Ember & Ember 1971, "Conditions Favoring Matrilocal vs Patrilocal Residence"** (*to grab*) — matri-
locality where women's subsistence dominates + external warfare, patrilocality where male hunting dominates — the
subsistence→residence link that motivates a (future) biome-localized residence rule; Divale 1974 corroborates.

## RED-TEAM

1. **Provisioning the crowd (the founder-overcrowding trap again).** If all bands physically STACK on one cell, that
   cell starves them (cf. R-37 seeding). → the gathering is a brief PAIRING event, modelled as a **regional pairing
   POOL** (pool the unpaired adults for `_do_pairing` WITHOUT forcing physical co-location), not a sustained
   residence. Physical convergence-to-site (a movement drive during the window) is a REFINEMENT, deferred; if built,
   it must be transient (pair then disperse before starving) and the site genuinely abundant.
2. **Over-mixing / erasing lineage structure — RESOLVED by two real mechanisms (supervisor 2026-07-02).** Regional
   exogamy mixes *who marries whom*, but real societies keep it from dissolving lineages via: **(a) virilocal +
   patrilineal absorption** — the bride joins the GROOM's band and adopts his lineage; children are reckoned
   patrilineally, so the wife's natal lineage does NOT propagate through her and the male line carries through
   (Marlowe 2004 virilocal-modal residence; the model has `patriline_weight` + the exogamy-residence rule — make
   residence strictly bride→groom's-band at the gathering). **(b) rank homogamy** — similarly-ranked lineages marry
   (status assortment / hypergamy; bride-wealth + family negotiation), so the cred gradient is preserved, not
   averaged. The model already has the B++ assortment machinery + the new ascribed mate-choice (high-cred grooms
   preferred, directional) — combine them at the gathering for directional-preference × assortative-matching =
   like-marries-like. **Reconciliation with R-20** (assortment SPREADS RS, doesn't CONSOLIDATE dynasties): that is
   about dynastic concentration, not lineage preservation, and predates ascribed-mate-choice/aggregation — no
   contradiction; preserving the rank STRUCTURE is the goal. **VALIDATE** in the re-run: with virilocal + rank-
   homogamy on, the connubium does NOT flatten cred Gini / status→RS / the dominant-lineage signal. `aggregation_
   radius` remains a secondary lever (smaller = more local = less mixing).
3. **Timing/period sensitivity + adult backlog.** Annual gathering ⇒ an adult who matures just after a gathering
   waits ~a year to pair. If the period is long or the window short, reproduction lags → check eq_pop isn't
   throttled; a maturing adult should pair at the NEXT gathering (not miss several). Bracket period + threshold.
4. **Connubium stability.** Site selection each gathering must be stable enough that roughly the same bands re-meet
   (a persistent marriage network), not a random re-shuffle. → sites = top-capacity cells (stable terrain feature),
   min-separated; verify connubium membership is reasonably persistent across gatherings.
5. **Interaction with the fixed mate-gate.** When aggregation is ON, the daily co-residence *pairing* is off (pairing
   only at gatherings); *births* gate on the pair-bond. Ensure no double-gate (a band both aggregation-paired AND
   blocked by the old daily gate). Off ⇒ old behaviour bit-exact.
6. **Static / no-climate worlds.** No `season()` ⇒ fire on a fixed phase of `aggregation_period` (deterministic), so
   the mechanism works on the biome→society harness (which is static Tallavaara).
7. **Isolated bands (no connubium in range) — DIE, and that's fine.** A band with no other band within
   `aggregation_radius` gets no gathering → no cross-mating → it may go extinct. Do NOT artificially rescue it
   (supervisor "se la vi") — isolated marginal bands going extinct is realistic and a feature, not a bug. (The
   radius is set to a realistic travel distance so this happens only to genuinely isolated bands, not normal ones.)

## Validation

- **The R-37 re-run (headline):** biome→society on Tallavaara CC-1 WITH aggregation → **families + bands persist in
  ALL biomes** (savanna/desert/montane no longer collapse); the difference is now **band size · mobility ·
  %complex/stratified** (small mobile egalitarian desert ↔ larger sedentary complex forest), not family presence.
- **Connubium emerges:** bands cluster into persistent marriage networks (band→community nest, Hamilton ~4×).
- **Preserve forest:** the productive-biome complex society (R-37 forest) is unchanged/robust.
- **Lineage dynamics survive** (red-team #2): cred Gini / status→RS / dominant-lineage not flattened.
- **Off ⇒ bit-exact** (locked by test).

## Long-term studies (flagged now; not this build)

- **Virilocal vs uxorilocal societies** — compare whole-world runs at each residence mode: does descent direction
  change band composition, lineage concentration, status→RS, dynastic dynamics? (Both wired now; the comparison is
  its own study.)
- **Biome-localized residence** — a rule that sets residence from the biome's subsistence balance (male-hunting →
  virilocal, female-gathering → uxorilocal; Ember & Ember). Would let *residence itself* be part of the biome→
  society signal. Deferred — wire the options first, study the correlation, then decide whether to make it emergent.
- **Random per-world residence** — assign residence mode per world (lottery) to see its effect across the ensemble.

## Sequencing

scope (this) → lit (file Mauss/Steward/Lee/Conkey; Wobst/Hamilton filed) → RED-TEAM → implement (flag + gathering:
season-gate + site selection + regional pairing pool + births-gate-on-bond) → unit tests → **biome→society re-run**
(families everywhere; society varies by biome) → gate → commit. Refinement (deferred): physical convergence-to-site
movement drive. Ties into: the dynastic/settlement arc (connubium = the community level), and the ascribed-status
mate-choice (which now operates in the regional pool).
