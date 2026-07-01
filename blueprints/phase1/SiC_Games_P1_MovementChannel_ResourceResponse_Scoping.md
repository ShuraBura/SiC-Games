# SiC Games P1 — Movement-Channel Resource Response (SCOPING + RED-TEAM)

**Goal.** Recast the resource→band-size response as a **non-monotonic drive on the MOVEMENT channel** (where band
size is actually set), replacing the mis-signed and inert `season_aggregation` fission term. As a band's realized
per-capita food adequacy falls: **abundant → mild cohesion · moderate lean → PEAK cohesion (aggregate / risk-pool)
· severe scarcity → dispersion (fission-as-movement) · catastrophic → mortality (failure mode).** This makes the
resource response bind on the equilibrium (the movement channel controls central band size), keeps the fission
threshold as a tail safety-valve, and de-double-counts by mapping each resource regime to ONE response.

**Governing principle (supervisor, standing): FULL CUSTOMIZABILITY.** Every drive below is an independent opt-in
flag (default OFF, bit-exact when off). `season_aggregation` is RETIRED into this redesign (dead-ended, not
silently kept).

---

## Motivating review findings (2026-07-01; RESULTS R-29 corrected, R-31)

1. **The fission threshold is DORMANT at equilibrium.** Controlled probe (realistic full-stack config): **0/26
   bands sit near their `tolerable_size`** — bands equilibrate at N≈20 while tolerable≈42. So the whole
   cohesion−dispersion balance (assabiyah + leader − repulsion − season) is INERT for setting *central* band size;
   size is set upstream by **movement (diffusion) + mortality + the mate-gate**.
2. **R-29 correction.** Repulsion's clean effect (controlled off-vs-on) is **max band 37→36, mean 20.7→20.0** + a
   modest pop drop (539→441 via tail-fission) — NOT the "44→31 cap" first reported (unclean baseline). It trims the
   tail, it does not cap the typical band, because the threshold it acts on isn't binding.
3. **`season_aggregation` is mis-signed AND inert.** It makes *lean → fission* (monotone), but the ethnography says
   *moderate* lean → **aggregation** (risk-pooling; Hadza dry-season water aggregation). And it does nothing anyway
   (bands sit below tolerable). Wrong sign, wrong channel, no effect.

## The three-channel architecture (the frame this blueprint commits to)

| Channel | Role | Drivers | Binds on |
|---|---|---|---|
| **Movement / spatial** | sets *central* band size (~20–25) | selfish-herd safety *(built, E.1)*, **risk-pool aggregation (moderate lean)** *(M1, new)*, **starvation dispersal (severe scarcity)** *(M2, new)*, IFD + local depletion *(built)* | the equilibrium |
| **Fission threshold** | tail safety-valve + settled/dynastic regime | assabiyah, leader, scalar-stress repulsion | runaway prevention, transients |
| **Mortality** | failure mode (dispersal failed) | starvation + density-disease | absolute deficit |

The resource-responsive drives (M1, M2) go on the **movement channel** (the binding one); the threshold keeps its
tail/dynastic job; mortality stays the failure mode. `season_aggregation` (a threshold term) is removed.

---

## The signal — realized per-capita adequacy `a = ypc / need`

`diffusion_select_target` already computes each candidate cell's per-capita yield `ypc` (§substrate.py). Define the
adequacy `a = ypc / subsistence_need` (need = the monthly burn already in the kcal economy). `a ≫ 1` abundant,
`a ≈ 1` balanced, `a < 1` lean, `a ≪ 1` severe. This signal **already carries season × ENSO × regime × local
depletion** (they all move `ypc` through the harvest field), so ONE signal drives the whole non-monotonic response
— no separate season/ENSO/regime/acute subtractors (the de-double-count, by construction). Smoothing / hysteresis
per red-team #4 below.

---

## Stage M1 — Risk-pool aggregation (moderate lean → aggregate)  `[enable_riskpool_aggregation]`

**Scope.** Under *moderate* lean (a in a band around, say, 0.6–0.95), STRENGTHEN the group-attraction in the
movement utility — a band pulls together to pool risk / share / aggregate at concentrating resources. Mechanically:
a resource-gated boost to the existing E.1 safety multiplier (or an additive aggregation multiplier on `ypc` that
rises with post-move group size `g`), scaled by a hump function of `a` that peaks at moderate lean and → 0 at both
abundance (no need) and severe scarcity (M2 takes over).
**Lit.** Cashdan 1985 (*Coping with risk*, Man) — sharing/reciprocity intensifies under variance; Wiessner 1982
(hxaro risk-reduction); Kaplan & Hill 1985 (food-sharing as variance reduction); Hawkes 1991 (Hadza dry-season
aggregation at water); Dyson-Hudson & Smith 1978 (economic defensibility → aggregate at concentrated resources);
Hamilton 1971 (the existing selfish-herd safety drive this modulates).
**RED-TEAM.**
1. **Double-count vs. E.1 safety (`group_safety_max`).** E.1 is an ALWAYS-ON risk dilution; M1 is a RESOURCE-GATED
   aggregation. Must be either (a) a *modulation of* the E.1 term by `a` (cleanest — one aggregation drive, resource-
   gated), or (b) a clearly additive, separately-ablatable term. Decide up front; do NOT stack two always-on
   safety terms.
2. **Concentration vs. spreading (biome direction).** "Lean → aggregate" holds when scarcity CONCENTRATES resources
   (waterholes: Hadza); it flips to disperse when scarcity SPREADS resources thin (!Kung). M1 should couple to the
   resource's spatial structure (the aggregation biomes / `wateracc` seam already exist) OR be scoped to the
   concentrating case and documented. Don't assume aggregation universally.
3. **Stability (oscillation).** aggregate → crowd → `ypc`↓ → `a`↓ → M2 disperse → `a`↑ → aggregate … a limit cycle.
   Needs the hump + M2 to compose to a STABLE optimum group size at each `a` (as E.1×IFD already does), not a
   flip-flop → hysteresis or a smooth `a`→drive map; validate for band-size stability.
4. **Magnitude unanchored.** The strength of the aggregation boost is not measured → BRACKET/sweep, report
   sensitivity, don't fit.
**Gate.** Under a scripted **moderate-lean** climate step (run_se0 driver), mean band size / band membership RISES
vs. the flat control; eq_pop preserved; the effect vanishes at both abundance and severe scarcity.

## Stage M2 — Starvation dispersal (severe scarcity → disperse, before death)  `[enable_scarcity_dispersion]`

**Scope.** Under *severe* scarcity (a below a threshold, say ≲ 0.5), add a CROWDING PENALTY to the movement utility
— a band fragments and sub-groups disperse to spread the load / access more patches, BEFORE starvation kills. This
lowers local density, which (via the existing density-disease + per-capita competition) auto-relieves the very
mortality it precedes: **dispersal substitutes for death, not adds to it.** A push (repulsion from crowded cells)
that switches on only when `a` is severely low; 0 in the moderate/abundant range (M1's domain).
**Lit.** Colson 1979 (*In good years and in bad* — famine coping / relocation; PENDING, JSTOR); Wiessner 1982
(relocate to exchange partners in famine); Kelly 1995 (fission-fusion, foraging spectrum); Layton et al. 2012
(dispersal pull vs. cooperation pull — the band as their balance); Fretwell & Lucas 1970 (IFD, the existing
dispersal baseline M2 sharpens under deficit).
**RED-TEAM.**
1. **Double-count vs. IFD / depletion.** The diffusion movement ALREADY disperses agents from crowded/depleted
   cells (falling `ypc`). M2 must be the ACUTE EXTRA push under severe deficit (a distinct regime), OR recast as
   "IFD gets steeper when `a` is severely low." Don't add a second generic dispersal on top of IFD.
2. **Double-count vs. mortality (the key one).** Scarcity currently KILLS (mortality). If M2 disperses AND mortality
   still fires at the old rate, scarcity is double-charged. **Requirement:** M2 dispersal must measurably lower local
   density → the density-dependent mortality relaxes → net scarcity cost is rerouted from death to movement, not
   added. VALIDATE: a scarcity pulse with M2 on should show *lower* mortality + *higher* dispersal than M2 off (a
   substitution, not an addition). If density-mortality doesn't relax enough, gate it under M2.
3. **Over-dispersal → mate-gate collapse.** Fragmenting too hard drops bands below the mate-viable size (Wobst ~25 /
   the E.2 `group_mate_min` floor) → birth collapse → a death spiral (cf. the SHELVED band-risk mortality, DE-4).
   The E.2 mating-access penalty must remain the floor M2 can't push through; validate births survive a scarcity
   pulse.
4. **Threshold vs. graded.** Severe-scarcity dispersal is threshold-like (kicks in below `a*`), not a gentle slope
   — but a hard step risks thrash (red-team #3 of M1). Use a smooth-but-steep sigmoid in `a`; bracket `a*`.
**Gate.** Under a scripted **severe-scarcity** climate pulse (run_se0 driver): band size DROPS / spatial spread
RISES vs. flat control; **mortality is LOWER with M2 on than off** (substitution); births survive (no mate-gate
collapse); the population recovers when the pulse lifts (transient dispersal, not a permanent scar).

## Retire `season_aggregation`  `[DEAD-END]`

`season_aggregation` (a threshold cohesion-multiplier, lean→fission) is superseded by M1/M2 on the movement channel:
seasonal lean now enters through `a = ypc/need` (the harvest field already carries `season()`), driving aggregation
(moderate) or dispersal (severe) on the binding channel, with the correct sign. Remove the config field + the
`_maintain_bands` `season_ab` factor (or hard-default it to inert); add a DEAD_ENDS entry (DE-7). Confirm bit-exact
removal (season_aggregation=0 was already the default → no baseline change).

---

## Validation plan (the binding test + substitution test)

1. **Binding test (the point).** Unlike the dormant threshold, the movement channel should make **central band size
   RESPOND to resource level**: sweep a flat climate driver at several `a` levels (run_se0 `ClimateDriver.flat` at
   scaled capacities); mean band size should trace the hump (rise into moderate lean, fall at severe). This is the
   test the threshold failed (R-31).
2. **Substitution test (M2 red-team #2).** Scarcity pulse, M2 on vs off: M2 on → higher dispersal + LOWER mortality
   (rerouting), not higher dispersal + same mortality (double-charge).
3. **Non-monotonic shape.** The moderate-lean-step (M1) and severe-scarcity-pulse (M2) gates above, back to back on
   one driver trajectory, reproduce the aggregate-then-disperse curve.
4. **Baseline preservation.** At a moderate/balanced config the realistic full-stack anchors hold: eq_pop, ~25
   non-kin bands (Wobst/Hamilton), status→RS ≈ 0.13, R-18 death-deficit > 0.
5. **Ablation.** Each flag independently off → bit-exact; both off → the current model exactly.

## Open questions / deferred refinements

- **Concentration vs. spreading (M1 red-team #2):** couple the aggregation *direction* to the resource's spatial
  structure (aggregation biomes / `wateracc`) so lean→aggregate fires only where scarcity concentrates resources,
  and lean→disperse where it spreads them. A refinement after the core M1/M2 land.
- **The abundant end:** does super-abundance actively *reduce* cohesion (no need to band)? Probably neutral; leave
  M1's hump → 0 at high `a` and revisit only if a signal demands it.
- **Colson 1979** to be obtained (JSTOR) for the M2 famine-dispersal anchor.

**Sequencing:** M1 (aggregation) → M2 (dispersal) → retire season → full non-monotonic validation. Each stage:
scope → lit → RED-TEAM → implement → gate → commit. Build only after this blueprint is reviewed.
