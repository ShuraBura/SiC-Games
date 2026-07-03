# SiC Games — Phase 1 — Storage-Sedentism (the general delayed-return / settlement mechanism)

**Status:** SCOPED + RED-TEAMED 2026-07-03. Foundational behavioural mechanism — needs supervisor sign-off before build. Resource-agnostic (aquatic first, proto-agriculture later); the settlement substrate the Ibn Khaldun dynastic arc needs.
**Anchors:** Woodburn 1982 (immediate- vs delayed-return); Testart 1982 (storage → sedentism → inequality); Binford 2001 (packing/logistical mobility); Ames 1994 (NW-Coast affluent foragers); Carneiro 1970 (circumscription); Bettinger (foraging→farming transitions).
**Motivates (GATE 3, R-50 line):** the aquatic capacity subsidy (C8) alone does NOT concentrate bands — **IFD movement is myopic** (each agent maximises this month's per-capita share `S/(n+1)`), so a rich cell fills only until per-capita ≈ landscape average (~3 people on a 119-capacity cell), then agents spread. Bands roam as loose clusters (~26 people over ~15–20 cells, density ~0.013/km²), far below Binford packing 0.091. IFD is blind to a cell's FUTURE storable value. Concentration/complexity requires a DELAYED-RETURN decision — stay, store, intensify — that IFD cannot express.

## 1. The mechanism (resource-agnostic)
`storability → storage → sedentism → concentration → intensification → complexity`. One new coupling — **storage ↓ mobility** — on top of the existing storage-accumulation mechanic:
- A per-cell **storable-surplus potential** `S_pot ∈ [0,1]` — how much delayed-return glut a band can bank by staying. `aquatic_food` (C7) feeds it now; a future `cultivability` field feeds it for proto-agriculture. **One field, many resource sources** (the generality the supervisor asked for).
- A band that meets the CONDITIONS (§2) becomes **sedentary**: its mobility drops (it stops roaming) AND its footprint tightens onto the high-`S_pot` cells (the village) — overriding IFD dispersal + the normal loose-cluster cohesion.
- Sedentism → the band packs onto few cells → band density crosses Binford packing → the existing `society_from_character(density, surplus)` fires complex/stratified NATURALLY (retires the R-46/47/48 heuristics; makes `stratified` reachable).
- **Collapse**: if the resource/stores fail, the CONDITIONS lapse → the band de-sediments (mobility resumes) — the boom→bust that feeds the dynastic cycle.

## 2. THE CONDITIONS a band must fulfil to attempt + realise the gains  ← (supervisor's focus)
A band shifts from immediate-return roaming to delayed-return sedentism only when ALL of these align (each a gate; anthropologically grounded):

- **C-RESOURCE (a storable, dense, predictable glut).** The band occupies (or reaches) cells whose `S_pot ≥ S_pot_min` — a genuinely storable, dense resource (salmon run / cereal stand), not a dispersed unpredictable one. *Anchor: Testart's three conditions — storage technology, a seasonal abundance, a resource dense+predictable enough to sediment on.*
- **C-GLUT/SEASONALITY (a harvestable surplus window).** The resource has a SEASONAL peak that EXCEEDS immediate consumption, so there is a surplus to bank. Needs the model's seasonality (EFC seasonal NPP / ClimateField.season) to deliver a glut. *(A flat year-round resource gives no glut to store → no delayed-return payoff.)*
- **C-LABOUR (enough hands to work the glut in its window).** The band must be large enough to HARVEST + PROCESS + STORE the glut before it spoils (the salmon-processing bottleneck). Below a minimum size the glut can't be captured → no surplus. *Anchor: NW-Coast labour/processing constraints; Ames.* → sedentism needs a band ≥ `sed_labour_min`.
- **C-PAYOFF (delayed-return beats immediate-return HERE).** The storable surplus the band can bank must buffer the lean season BETTER than mobility would — i.e., `expected_stored_surplus_value > IFD_move_value`. Only then is staying rational. *(This is the myopia fix: the band compares the FUTURE value of staying+storing against the instantaneous value of moving.)*
- **C-COMMITMENT (investment threshold + hysteresis).** Once the band has ACCUMULATED stored surplus above `sed_commit_threshold`, it is "invested" — sedentism becomes self-reinforcing (you don't abandon a full granary + built weirs/stores). Mobility drops with a hysteresis so it doesn't flip-flop. *Anchor: Carneiro circumscription / sunk investment.*

**Realisation (the payoff loop):** meeting C-RESOURCE…C-COMMITMENT → the band anchors + tightens → concentration → density crosses packing → morph → complexity/stratification; the accumulated surplus also feeds assabiyah (already wired). **De-sedentise** when C-RESOURCE or C-PAYOFF lapses (glut fails / stores exhausted / climate shift).

## 3. Implementation seams
- `S_pot` field = `aquatic_food` now (a `cultivability` OR-term added later); one accessor.
- Band-level `sedentary` state + `_sed_surplus` (reuse the existing per-band `_band_surplus`/storage granary). Decision (§2 conditions) evaluated in `_maintain_bands`.
- Movement: a `sedentism_factor(band) ∈ [0,1]` that (a) reduces the band's move/stride toward 0 and (b) pulls the footprint onto the top-`S_pot` cell(s) — reuse the co-movement footprint (C4) + band-cohesion (E.1) machinery, inverted (tighten instead of spread).
- Morph: unchanged — it already reads density+surplus; sedentism just delivers the density.

## 4. Red-team
- **RT-1 [over-sedentism].** If the gate is loose, everyone settles everywhere → no egalitarian foragers. Mitigation: C-RESOURCE + C-GLUT + C-LABOUR + C-PAYOFF are ALL required; `S_pot_min` set so only genuinely rich storable cells (rare — aquatic 1–6% of cells) qualify. Most bands never meet the conditions → stay mobile-egalitarian (correct: sedentism is the exception).
- **RT-2 [death-trap].** A band settles, the glut fails, it can't leave → mass starvation. Mitigation: the de-sedentise rule (C-PAYOFF/C-RESOURCE lapse → mobility resumes); starvation still culls; hysteresis bounded so a sustained failure releases the band.
- **RT-3 [conflict with C4 co-movement footprint].** C4 footprint SPREADS families (dispersed camp, fixes the marginal-biome collapse); sedentism TIGHTENS onto the fishery — opposite directions. Mitigation: sedentism overrides footprint ONLY when the conditions hold (rich storable cell); elsewhere the C4 dispersal stands. They act in different regimes (marginal-dispersed vs rich-concentrated) — reconcile explicitly, test both.
- **RT-4 [seasonal glut may be absent].** C-GLUT needs a real seasonal surplus. The model has seasonality (a_seas / EFC seasonal amplitude) but seasonal NPP/food is not yet fully wired (C3 is annual). If there is no glut, delayed-return has no payoff. Mitigation: verify a storable seasonal surplus exists (or wire seasonal aquatic yield) before relying on C-GLUT; interim, use the annual `S_pot` as a glut proxy.
- **RT-5 [IFD still fights it].** Even sedentary, per-step IFD may pull individuals off the village. Mitigation: sedentism must dominate the movement utility on the village cells (a strong anchor), not a soft nudge — calibrate so a committed band holds.
- **RT-6 [calibration + circular validation].** Many new thresholds (`S_pot_min`, `sed_labour_min`, `sed_commit_threshold`, payoff horizon). Ship ablatable/default-OFF; sweep; validate by MECHANISM (do bands settle on cold salmon rivers / rich coasts WITHOUT tuning to a target society mix?), not by curve-fitting to a desired stratification rate.
- **RT-7 [generality is real, not aspirational].** The mechanism must take `S_pot` as its only resource input so proto-ag drops in by adding a `cultivability` source — NO aquatic-specific logic in the sedentism/morph path. Enforce in code review.
- **RT-8 [packing metric].** Confirm the concentrated band's `members/footprint` actually crosses Binford 0.091 (the diagnostic showed capacity alone doesn't; sedentism must physically shrink the footprint). Measure post-build.

## 5. Validation
- Aquatic worlds: bands MEETING the conditions concentrate on cold salmon rivers / rich coasts → footprint shrinks → density crosses packing → morph → complex/stratified; bands NOT meeting them stay mobile-egalitarian. GATE 3 re-run (viable, no death-trap, interior egalitarian preserved).
- Generality smoke-test: swap `S_pot` to a synthetic cultivability field → same concentration behaviour (proves resource-agnosticism).
- Regression: default-OFF ⇒ bit-exact; the R-18/19/E.3 mobile-forager equilibria unchanged when no cell meets the conditions.

## 6. Recommendation
Build the general storage-sedentism mechanism with `aquatic_food` as the first `S_pot` source, gated by the §2 conditions, ablatable/default-OFF. This unlocks C9 (aquatic → stratification), IS the settlement substrate for the dynastic arc, and drops proto-agriculture in later for free. Sweep the condition thresholds; validate by mechanism; retire the R-46/47/48 morph heuristics once density-driven stratification fires.
