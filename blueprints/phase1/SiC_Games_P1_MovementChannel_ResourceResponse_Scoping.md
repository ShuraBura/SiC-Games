# SiC Games P1 — Resource → Band-Size Response, corrected (SCOPING + RED-TEAM)

**Goal.** Fix the mis-signed, inert `season_aggregation` (lean → fission) and give the band-size model the *correct*
resource response, honestly scoped after a design review (R-31) that (a) found the fission threshold DORMANT at
equilibrium and (b) tested each candidate driver against "does it actually help food-wise?". The surviving design
is deliberately minimal:
- **Retire `season_aggregation`** — moderate lean should NOT drive fission. Removing it is the whole fix for the
  moderate range (bands then just carry on, following food via existing movement). No aggregation force is added.
- **M2 — malnutrition fission** (severe scarcity → large bands break up), anchored to the model's OWN starvation
  onset (`_condition`), and intrinsically size-gated to large bands.
- **F — resource-directed fusion** (a starving/small band joins the RICHEST reachable neighbour, not the nearest)
  — the "starving families join the big pool" behaviour, cleanly a fusion refinement (resource-seeking), NOT
  anti-fission cohesion.

**M1 (moderate-lean aggregation cohesion) — DROPPED (review 2026-07-01).** It failed the food-wise test: the one
real payoff (risk-pooling variance reduction) is already implicit in within-cell meat sharing, and bands already
equilibrate at ~20 ≈ Wobst 25 (not under-aggregated). The "Hadza waterhole aggregation" case is agents *following
concentrated resources* — already the IFD movement, not a new anti-fission force. So there is no needed
moderate-lean cohesion driver; the correct moderate-lean behaviour is simply "no fission pressure" (= retire
season_aggregation). See DEAD_ENDS DE-8.

**Governing principle: FULL CUSTOMIZABILITY.** Each of M2, F is an independent opt-in flag (default OFF, bit-exact).

---

## Motivating review findings (R-29 corrected, R-31, 2026-07-01)

1. **Fission threshold DORMANT at equilibrium** (0/26 bands near `tolerable_size`; bands ~20, tolerable ~42). Band
   size is set by movement + mortality + mate-gate, not the cohesion−dispersion balance. **This is correct** — the
   threshold SHOULD be dormant in normal times and bind only under stress. M2 is precisely what makes it bind under
   severe scarcity (for large bands). So M2 does not fight the dormant-threshold finding — it completes it.
2. **R-29 corrected:** repulsion trims the tail (max band 37→36, pop 539→441), does not cap the typical band.
3. **`season_aggregation` mis-signed + inert** → retired (DE-7).

## The three-channel architecture (the frame)

| Channel | Role | Drivers | Binds |
|---|---|---|---|
| Movement / spatial | central band size (~20–25) | selfish-herd safety, IFD, local depletion *(all built)* | always (the equilibrium) |
| **Fission threshold** | tail valve + **stress response** | assabiyah, leader, scalar-stress repulsion, **M2 malnutrition** *(new)* | under stress / large size |
| Fusion | re-absorb small bands | nearest-neighbour join → **F resource-directed** *(new)* | when band < merge_size |
| Mortality | failure mode | starvation + density-disease | absolute deficit |

---

## The signal — band mean body-condition `cond = mean(a._condition)`

`agent._condition` (phase1_model.py:402/820) is a slow EMA of nutritional status ∈ [0,1] (1 = chronically well-fed;
→0 = chronically at the starvation reserve-floor). It already potentiates mortality (line 1337:
`m *= 1 + (mu_max−1)·(1−cond)`) — so it IS the model's starvation-onset variable, and being an EMA it is
pre-smoothed (no per-step thrash; red-team #4 handled by construction). M2 reads each band's mean `_condition`.
This carries season × ENSO × regime × local depletion through realized intake → one signal, no double-count.

## Stage M2 — Malnutrition fission (severe scarcity → large bands break up)  `[enable_malnutrition_fission]`

**Scope.** When a band's mean `_condition` falls below a threshold (chronic malnutrition), add a DISPERSIVE term to
the threshold balance that lowers effective `tolerable_size` toward `band_base_tolerable` — so a LARGE band splits
(the child band gets a new band_id, its members diffuse apart → lower local density). Form: a scarcity term on the
dispersion side, `malnutrition_pressure = gain · smoothstep(threshold − cond)`, subtracted from `cohesion_frac`
alongside repulsion (`cohesion_frac = clamp(assabiyah + leader − repulsion − malnutrition, 0, 1)`).
**Intrinsic size-gate (the key property):** because `tolerable_size` floors at `band_base_tolerable`=25 (the Wobst
viability floor, the `[0,1]` clamp), malnutrition can ONLY fission bands LARGER than 25 — small bands are untouched.
That is "large bands, not small ones" for free, no explicit size test.
**Anchor (supervisor choice):** the threshold is tied to the model's OWN starvation onset — `cond` at which the
mortality synergy `1 + (mu_max−1)(1−cond)` becomes serious (default ~0.5, halfway to the floor; bracketed). NO
invented quantitative "malnutrition% → fission" number (the lit gives this only qualitatively).
**Lit (qualitative — direction + "large bands first"):** Colson 1979 (*In good years and in bad*, famine
coping/fragmentation — PENDING JSTOR, supporting only); Turnbull 1972 (*The Mountain People* / Ik — social
fragmentation under famine); Kelly 1995 (fission-fusion, foraging spectrum, *filed*); Layton et al. 2012 (dispersal
pull under resource stress, *filed*).
**RED-TEAM.**
1. **Double-count vs. mortality (THE one).** Scarcity already kills. M2 must ROUTE the scarcity cost from death to
   dispersal, not add to it. VALIDATION (the substitution test): a scarcity pulse with M2 on → the fissioned
   members diffuse apart → local density falls → density-mortality relaxes → M2-on shows *lower* starvation
   mortality + *higher* dispersal than M2-off. If mortality does NOT relax, M2 is double-charging → reconsider.
2. **Mate-gate collapse / death spiral (DE-4 trap).** Over-fissioning drops sub-bands below mate-viable size → birth
   collapse. The `band_base_tolerable`=25 floor + the E.2 `group_mate_min` movement floor jointly guard this;
   validate births survive a pulse.
3. **Threshold vs. graded.** Use a smoothstep in `cond` (steep but continuous) to avoid a hard-step thrash; the
   `_condition` EMA already smooths the signal. Bracket the threshold + gain.
4. **Interaction with repulsion.** M2 and size-repulsion both lower `tolerable` for large bands — but repulsion is
   size-driven (always), M2 is malnutrition-driven (stress-gated). Additive on the dispersion side, separately
   ablatable; a large well-fed band feels only repulsion, a large starving band feels both (correctly harsher).
**Gate.** Scripted **severe-scarcity** climate pulse (run_se0 driver): large bands fission / band count rises,
mean band size falls; **starvation mortality is LOWER with M2 on than off** (substitution); births survive; the
population recovers when the pulse lifts (transient, not a permanent scar); small bands (<25) untouched; baseline
(no pulse) bit-exact-ish (M2 near-silent when well-fed).

## Stage F — Resource-directed fusion (starving/small band → richest neighbour)  `[enable_resource_directed_fusion]`

**Scope.** Currently a band below `band_merge_size` joins its NEAREST neighbour (`_maintain_bands`). Change: it
joins the RICHEST reachable neighbour — highest `_band_surplus` (or mean `_condition`) among bands within a bounded
radius — so starving remnants merge INTO well-provisioned bands (improving their nutrition via the larger shared
pool), rather than merging blindly by distance. Score = resource-state, restricted to nearby bands (bounded so a
remnant doesn't teleport across the map). Default OFF ⇒ nearest-neighbour join, bit-exact.
**Lit.** Wiessner 1982 (hxaro — relocate to well-provisioned exchange partners in hard times); Cashdan 1985
(reciprocity/sharing draws the needy to surplus holders); Kelly 1995 (fusion-fusion demography).
**RED-TEAM.**
1. **Runaway aggregation.** Everyone piling into the one rich band → a mega-band → then M2/repulsion should split
   it back (the balance). Validate the rich band doesn't grow unbounded (repulsion + M2 cap it).
2. **Distance bound.** Must stay LOCAL (a remnant joins a nearby rich band, not the global richest) — keep the
   nearby-radius restriction; bracket it.
3. **Signal choice.** `_band_surplus` (stored granary) vs mean `_condition` (current nutrition) — surplus = "who has
   the reserve to absorb us"; pick surplus (the pool the needy seek), document.
**Gate.** Under a scarcity pulse, remnant small bands preferentially merge into higher-surplus neighbours (measure
the surplus of chosen targets vs the nearest-neighbour baseline); eq_pop preserved; no unbounded mega-band.

## Retire `season_aggregation`  `[DEAD-END DE-7]`

Superseded: seasonal lean now enters (correctly) through realized nutrition — moderate lean → nothing (bands carry
on), severe lean → M2 fission via `_condition`. Remove the config field + the `_maintain_bands` `season_ab` factor
(default 0 → bit-exact removal). DE-7 already pre-registered.

---

## Validation plan

1. **Substitution test (M2 red-team #1 — the decisive one):** scarcity pulse, M2 on vs off → M2-on shows LOWER
   starvation mortality + HIGHER dispersal (fission). Dispersal reroutes the cost; it does not add to death.
2. **Size-gate check:** under the pulse, bands > 25 fission; bands < 25 untouched (falls out of the base floor).
3. **Transient, not scar:** population recovers after the pulse lifts.
4. **F check:** remnant bands merge into higher-surplus neighbours (vs nearest baseline); no unbounded mega-band.
5. **Baseline preservation:** no-pulse realistic config keeps eq_pop, ~25 non-kin bands, status→RS ≈0.13,
   R-18 death-deficit > 0. Both flags off ⇒ current model bit-exact.

## Open items

- **Colson 1979** — FILED + verified (2026-07-01). Directly anchors M2: famine → "the breakup into small family
  groups which comb the region" (verbatim); "refusal to share" corroborates that cohesion can't avert absolute deficit.
- **Concentration vs. spreading** (biome-dependent direction of the resource response) — deferred; the surviving
  design doesn't add moderate-lean aggregation, so this only matters if M1 is ever revived.

**Sequencing:** M2 (malnutrition fission) → F (resource-directed fusion) → retire season → substitution/size-gate
validation. Each: scope → lit → RED-TEAM → implement → gate → commit.

---

## RESULTS (built 2026-07-01, R-32/R-33)

**Signal red-team catch (R-32).** M2 was first built on mean band `_condition`, but a probe showed `_condition`
stays pinned ~1.0 under a population-crashing pulse (it samples the post-harvest FED reserve + survivor bias). So
scarcity here is expressed as DEATH, not lingering low condition. **Supervisor steer:** disperse on REALIZED
starvation (reactive), not a forecast (anticipatory = future "wise leadership"). M2 re-anchored to a per-band
realized starvation-rate EMA (`_band_starv_ema`).

**M2 VALIDATED — the substitution test (run_se2).** Severe −50 % pulse, M2 off vs on, 3 seeds: **starvation deaths
−120 / −31 / −24 (all lower)**, M2 fires (pressure 0.6–1.2), 2/3 seeds higher end-pop. Dispersal reroutes the
scarcity cost from death (spread → higher per-capita yield → fewer subsequent deaths). Size-gate confirmed (base
floor → large bands only). REACTIVE, ablatable, off ⇒ bit-exact.

**F built.** Resource-directed fusion (richest nearby band, radius-bounded, else nearest); unit-tested; off ⇒
nearest bit-exact.

**M1 DROPPED (DE-8)** — no food-wise payoff. **`season_aggregation` superseded by M2 (DE-7)** — physical field
removal is a pending cleanup (inert meanwhile). 9 M2/F unit tests; full suite 588 passed / 1 xfailed.
