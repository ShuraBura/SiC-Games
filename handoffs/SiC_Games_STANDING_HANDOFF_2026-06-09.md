# HANDOFF — SiC Games, terrain-design chapter opened (2026-06-09)

## Where we are

The density/calibration chapter that opened the previous handoff was **reframed, not
executed**. Investigation of the §8 substrate data showed the problem is not a density scalar
to tune but a **missing mechanic** — there is nothing in the model that makes co-location
productive, so grouping never pays and the social layer stays inert. This redirected the
project into a **terrain → seasonal-resource build sequence**, with terrain as the foundation
layer. This session was a design pass on terrain. No model code changed. One prototype artifact
was produced (a terrain-generator judgment tool).

## What the §8 data actually showed (corrections to prior state)

Working from `behavioural_partial.pkl` directly:

- **The §8 report had the grid wrong.** Config echo said 50×50/N=250 (legacy Stage 5.1 values);
  the run was **100×100, N_init=2250, N_carry=4100**. All of §4's density arithmetic was on the
  wrong denominator. CC has since corrected §1/§4/§5 and HYPOTHESES in place. Real grid-wide
  density ≈ 0.00108–0.00115 p/km² (~9× below band floor of 0.01, ~90× below the ~0.1 proto-ag
  midpoint). The "≈100×" shorthand is ≈90× vs midpoint.
- **The denominator question dissolved.** Run is flat-resource (NullPerturbation), single-step
  snapshot. No seasonal cycle → no envelope-over-cycle distinction to agonise over. Inhabited-
  cells-only ≈ 0.016 (a ceiling, conditions denominator on numerator); grid-wide ≈ 0.0011.
  Positions were never dumped — only aggregate summary in the pkl.
- **The real finding is the occupancy distribution.** occ_hist (cells at occupancy 1..6):
  κ=0 [420,138,69,28,11,1], κ=1 [494,163,62,30,2,3]. Read two ways:
  - by **cells**: ~63–65% of occupied cells are singletons → "contest inert" (the prior framing).
  - by **agents**: ~57–61% of agents are in multi-occupancy cells → contest already fires on a
    majority of agents.
  Both true. The contest is **on but weak**: max occ only 6, mass in doublets/triplets, κ=0 vs
  κ=1 settled populations differ only ~7%. So the problem is not "make the contest fire" — it
  is "make co-location *productive*," which the current scramble-only economy never does.
- **Cov(φ,wealth):** corr is small-negative both κ (κ=0 −0.12, κ=1 −0.016). The handoff's
  "−0.11" was the κ=0 covariance conflated with correlation. Use correlation (scale-free).
  Still open-pending-calibration; not a finding.

## What this session decided (design, no build commitment beyond the prototype)

**Build sequence (supervisor-set):**
1. **Terrain** — the big one; foundation layer. Static terrain, moving resources later.
2. **Seasonal resources** — game migrates; other resources locked-in-place but density cycles
   with seasons. (Mental note logged: seasonality acts by *modulating terrain-derived fields*,
   not by moving resources independently — keeps migration endogenous.)
   Cultivation / proto-ag is a *later* stage, not next.

**Terrain architecture — derive-from-primitives (CONFIRMED by supervisor):**
- Two/three primitive fields → everything else is a deterministic function of them. Covariance
  through shared cause is what makes social dynamics emergent rather than painted-in.
- Primitives: **elevation** (tunable roughness + relief) → **water** by flow accumulation
  (rivers/lakes emerge, not placed) → derived fields.
- Derived fields: forage capacity, game capacity, movement cost (slope-derived), cost-to-exist,
  water accessibility, base mortality risk. All static numpy arrays computed once at world init.
- **Vectorization constraint (hard):** terrain is precomputed static (and seasonal-static)
  arrays. Only per-step terrain contact is gather-at-agent-positions + one broadcast for seasonal
  modulation. **No terrain computation inside the agent loop.** Cost-to-cross is an *edge*
  property → precompute a (100,100,4) neighbour-cost array; it is the only terrain field that
  touches the movement hot path and must be designed into the movement kernel, not bolted on.

**Six biomes + water:** water, wetland/floodplain, forest, savanna/edge, steppe/grassland,
desert, mountain.

**The forage≠game inversion (literature-grounded, load-bearing):**
- Forage tracks NPP → peaks in forest/wetland.
- Game tracks palatable-grass × turnover → **hump-shaped in NPP, peaks at savanna/grassland/edge**,
  low in both desert and dense forest. (Forest productivity is locked in inaccessible wood;
  savanna grass is palatable + high-turnover → large huntable biomass.)
- **This spatial separation is the engine of the hunter/gatherer split** — gatherers want
  forest/wetland, hunters want savanna/edge. If forage and game co-located, no distinct modes.

**Water as accessibility, not inventory (CONFIRMED):** consumed resource, but modelled as a
distance-decayed `water_access` field → metabolic penalty when low, NOT agent-carried inventory.
Zero new agent state. Dry areas are crossable but costly. (Deliberate water storage/provisioning
is a far-horizon cultivation-era behaviour, parked.)

**Savanna hunting = band-size access gate (supervisor refinement):**
- Forest game: huntable solo (individual has real success chance) → optional-multiplier tier.
- Savanna game: ~zero solo (open ground, herds), unlocks only for a large cooperating party →
  **access gate**, the same mechanic the concept map reserved for cultivation, but in *minimal*
  form (no settlement dimension). Return curve = **step-then-plateau**: zero below threshold,
  jumps to viable, then flat/declining per the ethnography.
- Reconciles with the lit finding (cooperative hunting does NOT raise mean per-capita yield):
  the gate is about *crossing into feasibility at all*, not marginal returns above it. Benefit is
  enormous **variance-reduction** (zero-alone → shared-together), which is what the social
  apparatus exists to run.
- Possible stage reordering: the access-gate mechanic may debut in stage 2 (savanna hunting),
  proven, before cultivation adds settlement on top.

**Mortality-risk field (supervisor raised; ruled a genuine driver, staged carefully):**
- A base-risk field derived from terrain (exposure on steep/high ground, thirst far from water,
  shelter in cover, drowning at water edges) — agent-agnostic, generated in the terrain stage
  as just another derived field. **Generated and rendered now; no agent response yet.**
- The *company-reduces-risk* social modifier (safety-in-numbers) is the candidate **primary
  social-aggregation driver** — the first mechanic that makes proximity intrinsically valuable
  independent of resources, matching the ethnography (people group for safety/kinship/reputation,
  not yield). It gets its **own dedicated stage**, introduced alone, with a decomposition
  diagnostic alongside, so risk-aggregation can be separated from resource-aggregation.
- Open core question for that stage: **risk currency and the risk/energy tradeoff** — mortality
  and starvation are both death; the agent needs a decision rule for "safe but starving" vs.
  "fed but dangerous." That tradeoff IS the interesting dynamic; needs explicit operationalization.

## Concept-map corrections this session produced (predate the map; need to land canonically)

The `SiC_Games_Resource_Concept_Map.md` (v0.1, 2026-06-02) §2/§4/§5 say the foraging/game tier
gets a **yield multiplier** from cooperation. This session's lit check **overturns that for
hunting**: game-tier cooperation is **variance-reduction, not mean-yield**. True yield-
superadditivity survives only at the **cultivation** tier. Savanna hunting is an **access gate**,
a second (and earlier/minimal) home for the gate mechanic the map reserved for cultivation.
See the documentation BP for the exact edits.

## The prototype artifact

`sic_terrain_prototype.html` — a self-contained interactive terrain-generator **judgment tool**
(not the production algorithm). Five knobs (mountainousness, roughness, water abundance, forest
coverage, aridity) + seed. Renders biome + elevation/forage/game/water-access/cost/risk overlays,
plus feasibility readouts (water/land split, rivers, drainage density, mean fields, biome
composition bar, game-forage hump check with verdict, slope histogram, hypsometry). Knob corners
verified: total-desert config → 100% desert; mountainousness=0 → no mountains; water=0 → no
standing water. **Render math is tuned for legibility, NOT the production field equations.**
Game-hump verified peaking at moderate NPP across configs.

Known tradeoff to watch when driving it: forest and savanna compete for middle-NPP ground, so
maximally-forested worlds have ~0% savanna. The interesting worlds (both hunters and gatherers
thrive) are where both coexist; if that band is too narrow the game/forest formulas need
rebalancing before production spec.

## What comes next

1. **Supervisor drives the prototype** — judge whether the terrain model produces rational
   worlds; note good knob ranges and any failure modes. This calibrates the eye + becomes the
   acceptance target for the production generator.
2. Then one of: **production terrain-generator blueprint** for CC (field equations specified,
   feasibility statistics as the verdict-by-assertion acceptance gate, SoA/precompute constraint
   baked in) — OR prototype rebalancing if the eyeball test fails — OR back to design.
3. Stage 1 sub-pieces: 1a prototype (done, pending verdict) → 1b production generator spec →
   1c wire generator output into SoAWorld.
4. Stage 2 (seasonal/migration) after terrain confirmed.

## Deferred-mechanics ledger (see documentation BP for homes/triggers)

base-risk field (stage 1, render-only) · company-reduces-risk modifier (own stage + diagnostic) ·
risk/energy tradeoff (top of risk stage) · savanna-hunt payoff = participant-only vs area-shared
public good — the free-riding fork (stage 2) · water storage/provisioning (far horizon) ·
game ecotone/edge peak (stage 1 game field) · terrain feasibility statistics (production
generator acceptance gate) · defensibility/visibility terrain (horizon, may fold into risk) ·
N_carry re-derivation for multi-occupancy (still queued from prior handoff).

## INFRASTRUCTURE FLAG (deliberate task, not urgent)

**The repo is a Google-Drive-synced folder.** Running git/CC against a working tree that Drive
is live-syncing risks `.git` corruption and conflict-copies (`ROADMAP (1).md` — the exact
duplication disease already cured once). It has worked so far only because access has been
serialized (one machine at a time). **Recommended fix:** move the working repo to a non-synced
local path; git's GitHub remote is already the cross-machine sync, making Drive redundant for the
repo. Keep Drive (if wanted) only as a separate flat-file export mirror, never the live clone.
**This is deliberate surgery on the single source of truth — do it with CC walking through it on
the machine where the repo lives, not casually.** See the migration walkthrough BP.

## CONTINUATION STATE — read this to resume the conversation as if uninterrupted

This section exists so a fresh chat can pick up the *live thread*, not just the settled
decisions. The design conversation was mid-flight when the session ended for chat-length reasons.
Where things actually stand:

**The immediate live task (not yet done):** the supervisor is going to **drive the terrain
prototype and deliver a verdict** — do the generated worlds look like rational places people
would live and fight over? Nothing downstream (production generator spec) should be written until
this verdict is in. The specific thing to judge: **the forest↔savanna tradeoff.** They compete
for middle-NPP ground, so heavily-forested worlds have ~0% savanna. The interesting world — where
hunters AND gatherers both thrive — needs both forest and savanna present. Open question the
supervisor is resolving by eye: is that coexistence band comfortably wide, or too narrow? If too
narrow, the game/forage field formulas need rebalancing (a prototype edit, no CC) BEFORE any
production spec.

**What the supervisor is also doing in parallel:** reading the Janssen & Hill papers (see below)
before they harden into project anchors.

**The single sharpest unresolved design tension** (surfaced right at session end, NOT yet
worked through): the **savanna access-gate shape vs. the Janssen & Hill optimum.** This session
proposed savanna hunting as a hard **step-then-plateau** access gate: zero return below a band-
size threshold, jumps to viable, then flat. BUT Janssen & Hill (2014) found a *smooth* optimum
around **7–8 hunters** — a rising-then-leveling curve, not a hard zero-below-threshold. These are
different claims. The supervisor's reading of the paper is meant to settle which shape the savanna
mechanic takes. **Do not treat the step-then-plateau gate as locked** — it is a proposal in
tension with the empirical precedent, and resolving that tension is the next mechanics-design
task. This is the thing to pick up first on the mechanics side.

**Mechanics threads that are open and chat-able now (no CC needed), in rough priority:**
1. **Savanna gate shape** — resolve step-then-plateau vs. smooth 7–8 optimum (gated on the J&H
   read). Highest priority because it's a live contradiction.
2. **Risk/energy tradeoff** — the core open question of the eventual risk stage. How does an agent
   weigh "safe but starving" vs. "fed but dangerous"? Decision-rule design, fully chat-able. This
   is the juiciest untouched piece.
3. **Savanna-hunt payoff distribution** — participant-only vs. area-shared public good (the free-
   riding fork). Parked at "decide when building stage 2," but designable now.
4. **Seasonality → terrain-field modulation** (stage 2 shape) — which derived fields cycle, how
   game-migration falls out of forage cycling across static terrain, what the lags are.

**What is NOT yet written and is the likely next deliverable once the prototype verdict is in:**
the **production terrain-generator blueprint** for CC — real field equations (not the prototype's
legibility-tuned render math), feasibility statistics as the verdict-by-assertion acceptance gate,
SoA/precompute constraints baked in. This is mechanical drafting; it could even wait behind the
mechanics discussions if the supervisor prefers the meatier design work first.

**Prototype calibration facts the next chat needs** (so it doesn't re-derive them): knob corners
verified — total-desert config → 100% desert; mountainousness=0 → no mountains; water=0 → no
standing water; game-hump peaks at moderate NPP across configs. Default knobs lean arid (push
water + forest up from midpoints for lush worlds). Render math is for legibility, NOT production.
The prototype lives as a portable HTML file; if rebalancing is needed it is a chat-side edit to
the field formulas in that file, no repo involvement.

**How to actually resume:** if continuing the design, start by stating "continuing the SiC terrain/
mechanics design" and (ideally) paste this CONTINUATION STATE section, since a fresh chat sees only
this handoff, not the full transcript. Then either (a) take the supervisor's prototype verdict and
proceed to production spec or rebalancing, or (b) pick up the savanna-gate-shape tension / risk-
energy tradeoff. The four resource concept-map corrections and §13-risk addition are queued for CC
(documentation directive) but do NOT block any design discussion — they can be discussed and
refined further in chat before CC ever applies them.

## Working-mode notes

- Literature anchors raised but NOT yet logged to LITERATURE.md (provenance bar not met from
  snippets):
  - **Janssen & Hill 2014**, *Human Ecology* 42(6):823–835, DOI 10.1007/s10745-014-9693-1 —
    the cooperative-hunting / group-size / mobility paper. Findings from abstract: social living
    decreases daily risk of no food, cooperative hunting has only a *modest* effect on mean
    harvest rates, optimal band ≈ **7–8 hunters** moving nearly daily. Model code archived on
    CoMSES ("Ache hunting" v1.0.0, codebases/3902). **READ FULL PAPER before anchoring** — and
    specifically to resolve the gate-shape tension: the 7–8 optimum is a *smooth* rising-then-
    leveling curve, which is in tension with this session's proposed *hard step-then-plateau*
    savanna access gate. The read settles which shape the savanna mechanic takes.
  - **Janssen & Hill 2016** (book chapter, "Clumped Habitats Favor Lower Mobility...") — the
    resource-distribution / patch-clumpiness paper. Finding: optimal group size unaffected by
    resource distribution; clumped resources in patchy environments raise return rates and favor
    adaptive camp-moving. Relevant to terrain clumpiness + mobility (stage 1/2). Grab alongside.
  - Allee-via-foraging-facilitation (cooperation-term functional response lineage) — the
    superadditivity criterion (per-capita intake must rise with N for coop to give mutualistic
    benefit).
  - MVT-for-groups (social patch-departure model) — deplete-and-move mobility falls out of
    regeneration rate.
- This session never touched the repo (Drive-sync caution). All outputs are portable files to
  carry to the repo machine.
