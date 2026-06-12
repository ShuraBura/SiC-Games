# SiC Games — Stage 6.0a Blueprint: Spatial Scale + Multi-Occupancy Substrate

**Version:** 1.0
**Stage:** 6.0a — substrate layer of the resource-ecology arc. Precedes 6.0b (graded
terrain + metabolic multiplier), which stands on this.
**Scope:** Replace the one-agent-per-cell substrate with a multi-occupancy substrate where
per-cell density emerges from resource competition. Declare the spatial scale. Convert harvest
to a shared split (Cred-weighted contest for C). Convert movement to local-gradient diffusion.
Port the spatial hash, partner search, pool grouping, and replacement to multi-occupancy. Make
the minimal trait-semantics ruling required so existing social mechanics don't silently break.
**Output dir:** `outputs/stage6_0a_substrate/`

---

## 0. Why this stage exists (read before coding)

The current model is classic Epstein–Axtell: **one agent per cell**. Movement is argmax over
visible *unoccupied* cells; harvest is "take all the cell's sugar, zero it"; deaths respawn at a
random *unoccupied* cell (Stage 1 §227, §231, §243). That convention encodes a hidden claim —
every cell, regardless of what it represents, sustains exactly one agent, so population density
is uniform everywhere. The resource-ecology arc makes that claim false on purpose: density must
be able to vary by terrain. So the one-agent-per-cell rule must go *before* terrain is graded
(6.0b), or the terrain stage would grade capacity while density stays pinned at 1/cell.

**Design principle for this stage (the organising rule):** build the substrate **and the
seams**, with every trait-driven / social modulation present in the code but defaulted to its
neutral value that recovers current behaviour. This matches the project's existing house pattern
(MODEL_SPEC §188: "coupling term with λ_int=0 → bit-identical to current utility"). Build the
socket now; the bulb (affinity, crowd-response behaviour) goes in later stages, one at a time.

**Per-stage gate discipline (resource-ecology build phase, per supervisor 2026-06-02):**
equivalence/recovery gate (build hygiene) + C-behavioural check (does it do what we expect to C;
is C viable) + Si-portability note (toggleable? clean port?). **No Si runs, no inversion
protection, no H1(ii) work during the build.** A failed gate is a blocking STOP (CLAUDE.md):
halt, report, wait.

---

## 1. Spatial scale declaration (do this first; everything is downstream)

**Declare: 1 cell = 100 km² (10 km × 10 km).** The 100×100 grid is therefore a
**1,000,000 km² continental forager landscape**. This is the spatial analogue of the locked
monthly time-step (OWE-1 Route A) — a declared physical constant, recorded once, defended in
writing, not silently assumed.

Rationale (record in MODEL_SPEC and config comment):
- A band's monthly foraging catchment is ~100–300 km² → one cell ≈ one band's monthly range.
- 1,000,000 km² is continental — room for many bands, migration, regional structure.
- It places ethnographic hunter-gatherer densities at workable integer headcounts per cell
  (§4 validation): harsh ~1–5, neutral ~10–50, fertile ~50–200+ agents/cell.

Add `cell_area_km2: 100.0` to config. All density reporting (§4) converts agents/cell →
persons/km² using this constant.

---

## 2. Multi-occupancy substrate

### 2.1 Remove the one-agent-per-cell constraint

A cell may hold any number of agents. Three code sites assume single occupancy and must change:

1. **Movement candidate set** (Stage 1 §227): currently "visible *unoccupied* cells." Remove the
   unoccupied filter — all visible cells in the von Neumann neighbourhood (including current
   cell) are candidates regardless of occupancy. Occupancy now enters via the *utility* (§3),
   not as a hard exclusion.
2. **Replacement placement** (Stage 1 §183, §243): deaths currently respawn at a random
   *unoccupied* cell. For this stage, **offspring spawn on the parent's cell** (see §2.3); the
   random-unoccupied-respawn path for the *null/initialisation* replacement should place on a
   random cell **without** the unoccupied constraint (cells can co-host).
3. **Sequential-processing rationale** (Stage 1 §252): agents are processed in shuffled
   sequential order *specifically because* the unoccupied-cell constraint makes order matter
   (one agent claiming a cell blocks another). With the constraint gone, that specific reason
   dissolves. **Keep shuffled sequential order for now** (it still matters for harvest-split
   ordering and Cred-contest determinism — see §3.4), but record in a comment that the original
   justification (occupancy blocking) no longer applies; the new justification is split/contest
   determinism. Do not switch to parallel update in this stage.

### 2.2 The spatial hash → multi-occupancy (the main refactor)

The spatial hash (JT-fix performance work) and every consumer currently assume
`pos → at most one agent`. Convert to `pos → list/set of agents`:

- The hash maps each occupied cell to the **collection** of agents on it.
- **Consumers to fix** (find all; these are the known ones — grep for hash lookups):
  - **Partner search** (C biparental reproduction, proximity r): must handle multiple agents
    per cell, including co-located partners on the *same* cell.
  - **Pool grouping** (support pool L1–L3): grouping logic that assumed one-agent-per-cell
    membership must handle bands (many agents per cell).
  - **Joint-task partner identification**: co-occupants are now the natural joint-task cohort
    (see §5 trait-semantics ruling).
  - **Any neighbourhood/proximity count** (notably the ψ proximity term — §5).

This is the bulk of the implementation labour and the most likely site of a silent correctness
regression. Every consumer that does `agent_at(pos)` must become `agents_at(pos) -> collection`
and handle 0, 1, or many.

### 2.3 Reproduction under co-occupancy

- **Parents must be co-located** (same cell) to reproduce. Partner search finds candidate
  partners *on the same cell* (the band), per the C biparental rule, subject to existing
  fertility/wealth conditions.
- **Offspring spawns on the parent's cell** (joins the cell's occupant set and its harvest
  split). No dispersal in this stage. Record that dispersal (offspring pushed to a neighbour) is
  a *deferred* alternative with known interaction with the Allee/C-extinction diagnostics — not
  built here.

---

## 3. Harvest: resource-split, with Cred-weighted contest for C

### 3.1 The split (substrate floor — applies to all agent types)

Current harvest (Stage 1 §231): `w_i += s(cell); s(cell) ← 0` — sole occupant takes everything.
Replace with a **shared split** of the cell's available sugar among its occupants, resolved once
per step for each occupied cell:

- Let `S = s(cell, t)` be the cell's available sugar this step, and `O` the set of occupants
  after movement.
- Each occupant `i` receives share `share_i`, with `Σ share_i = S` (the cell is fully harvested;
  `s(cell) ← 0` after the split, as before).
- After receiving its share: `w_i += share_i`.

### 3.2 Even split (scramble) — the neutral baseline

Default / Si / contest-off: **even split**, `share_i = S / |O|`. This is pure scramble
competition: density self-limits because per-capita intake `S/|O|` falls as occupancy rises,
until it drops below metabolic need and the cell stops sustaining additions.

### 3.3 Cred-weighted split (contest) — C, active in this stage

For C agents, share is weighted by Cred (φ), giving high-status agents a larger material share —
the concrete material payoff that gives Cred teeth (the whole point of the Cred parameter):

```
share_i = S × ( φ_i^κ / Σ_j φ_j^κ )      over occupants j on the cell
```

- `κ = contest_exponent` (config). **κ = 0 recovers even split exactly** (every weight → 1) —
  this is the neutral default used as the validation reference (§4), the same seam pattern as
  ψ=0 / λ_int=0 elsewhere.
- For this stage set the **active C value κ = 1** (linear Cred weighting). Si uses κ = 0
  (even split) — Si has no Cred, so its weights are uniform regardless.
- Guard φ ≥ ε > 0 (or use (φ+ε)) so a zero-Cred agent still gets a nonzero share and the
  denominator never vanishes.

**Intended consequence (state in design, do not tune toward):** contest makes resource decisions
*noisier* — an agent now chases both yield and status, and a crowded cell rich in sugar may still
be worth joining for a high-Cred agent who will claim a large share, while a low-Cred agent does
better leaving. This is a feature (socially-textured movement), not a bug to smooth out.

### 3.4 Determinism

The split is computed per cell from the post-movement occupant set, so it is order-independent
*within* a cell. Keep the shuffled-sequential agent order (§2.1.3) for reproducibility of the
movement phase and any tie-breaks; seed as usual. Record that split values do not depend on
intra-cell ordering (a correctness property worth a test — §6).

---

## 4. Movement: local-gradient diffusion (not navigation)

Movement is **diffusion up a local gradient**, not planned travel to a known distant target. A
forager band without maps or long-range communication feels the local resource gradient and
steps to the best *neighbouring* cell; migration emerges as a chain of local steps, never as an
executed route. This is the model decision that makes crossing-cost trivial (one move = one
known cell) and removes any need for step-wise locomotion or path-integrated cost.

### 4.1 Awareness range = local neighbourhood only

Candidate cells = the **von Neumann neighbourhood** (4 cardinal + current cell), per the existing
rule but **without** the unoccupied filter. **Drop long-range awareness** — no 2–3-cell "word of
distant rich lands." The gradient is strictly local; this is deliberate (diffusion, not
navigation).

> **Vision-range sanity note:** vision `v ∈ {1..6}` (MODEL_SPEC §43) was a perception radius in
> abstract cells. At 100 km²/cell, v=6 is a ~600 km perception radius — implausible for monthly
> forager decision-making. For the diffusion model, evaluation is over immediate neighbours, so
> effective decision-radius is 1 cell. **Do not silently keep v up to 6 driving candidate-set
> size.** Ruling: candidate set is the immediate von Neumann neighbourhood (radius 1) for the
> gradient step; if `v` is retained anywhere it must be documented as vestigial/inactive for the
> movement candidate set, not silently shaping it. Report what `v` still affects, if anything.

### 4.2 Cell-evaluation utility — built in FULL FORM, trait terms neutral

The agent scores each candidate cell with the **full** utility function, but in 6.0a the
trait-driven terms are at neutral values that recover current behaviour. This is the socket;
later stages flip the parameters to activate the bulbs.

For agent `i` evaluating candidate cell `j` with occupant set `O_j` (post-hypothetical-move):

```
U_ij =  expected_per_capita_yield_ij              # ACTIVE
      × resource_affinity_i(type_j)               # HOOK — neutral = 1.0 in 6.0a (no terrain types yet anyway)
      × crowd_response_i(|O_j|)                    # HOOK — see §5; neutral = 1.0 in 6.0a
      − move_cost_ij                               # ACTIVE (§4.3)
```

- `expected_per_capita_yield_ij`: the agent's *anticipated share* if it moves to `j`. For even
  split, `S_j / (|O_j| + 1)` (it would be one more occupant). For C contest, the agent's
  Cred-weighted share estimate given the cell's current occupants. **This is the term that makes
  diffusion self-limiting**: a mobbed rich cell offers a small per-capita share, so it stops
  attracting. Note this is "best *per-capita* prospect," not "richest cell."
- `resource_affinity_i(type_j)`: **hook, inactive.** No terrain types exist until 6.0b and no
  heritable affinity until the trait stage. Default 1.0. Present in the equation so 6.0b/affinity
  stages flip it on without rewriting the evaluator.
- `crowd_response_i(|O_j|)`: **hook, inactive (=1.0).** This is where ψ (sociability) will act —
  see §5. It is NOT a global saturation force; it is a per-agent response to occupancy. Inactive
  here.
- `move_cost_ij`: active — §4.3.

**Neutrality requirement (recovery-gate-critical):** with affinity=1.0, crowd_response=1.0, and
move_cost configured off, `U_ij` must reduce to "best per-capita yield," and in the
single-occupancy regime (§7 recovery gate) must reproduce the current greedy-argmax-over-yield
behaviour exactly. Build and test that reduction.

### 4.3 Move cost

Two move-cost components, both cheap because every move is a single step onto a known cell:

- **Flat move cost** `move_cost_flat` (config, default 0): energy lost for moving at all,
  regardless of destination. Staying put (choosing current cell) costs 0. Makes agents sticky —
  they don't relocate for marginal gains. Default 0 recovers current (free) movement for the
  recovery gate.
- **Destination-terrain move cost** `move_cost_terrain[type]` (config): extra cost for stepping
  *onto* a given terrain type, read directly off the destination cell's type. **Hook, inactive
  in 6.0a** (no terrain types yet) — wire it into the evaluator as a lookup defaulting to 0,
  activated in 6.0b.

> **Crossing/path cost is NOT needed and NOT built.** Because movement is single-step diffusion,
> every move crosses exactly one boundary onto one cell of known terrain, so "crossing cost" =
> destination-terrain move cost. There is no multi-cell path to integrate, hence no step-wise
> locomotion rewrite. The previously-deferred traversal-cost mechanic is **dissolved**, not
> deferred: the diffusion model means it never arises.

---

## 5. Trait semantics under co-occupancy (minimal don't-break ruling)

Multi-occupancy breaks the **adjacency** assumption that the social traits were built on. The
instant a whole band shares one cell, "interact with / be near other agents" changes meaning.
This stage makes the **minimal ruling needed so nothing silently no-ops or misfires**; the full
re-expression of the trait vector for the band-on-a-cell reality is the **next deliverable** and
is out of scope here.

**ψ (sociability) — the trait most affected.** MODEL_SPEC §39/§54: for C, ψ weights a
"proximity-to-other-agents" term in movement utility; high-ψ C agents prefer cells near other
agents; its only resource consequence is indirect, via crowding ("ψ crowding collapse"). Under
single occupancy, "proximity to agents" meant *adjacent* agents. Under multi-occupancy the
natural reading is **occupancy of the cell itself (band size)**. So ψ is exactly the
`crowd_response_i(|O_j|)` hook in §4.2.

**Ruling for 6.0a:** ψ's proximity term is **re-pointed** from adjacent-agent count to cell
occupancy `|O_j|`, BUT held **inactive (neutral)** this stage — i.e. `crowd_response_i ≡ 1.0`,
equivalently the ψ weight is forced to its no-effect setting — so 6.0a does not change movement
via ψ. The point is to (a) prevent ψ from reading a now-meaningless adjacency signal, and (b)
lay the corrected socket. Activating ψ-as-crowd-response (high-ψ agents tolerate/prefer crowded
band cells; low-ψ individualists avoid them) is part of the trait re-expression deliverable.
**Si ψ remains inactive/different-signal as already specified (MODEL_SPEC §54) — untouched.**

**Other social mechanics — confirm, don't redesign:** for joint-task cohort identification and
pool grouping, the band = co-occupants of a cell. Confirm in code that these now read the cell's
occupant set (not an adjacency scan) and that none silently returns empty (the failure mode where
"adjacent agents" finds none because they're all co-located). This is a correctness confirmation,
not a behavioural redesign. Anything that needs real redesign → log it for the trait
re-expression deliverable, do not improvise it here.

---

## 6. Tests to write (pytest, alongside existing suite; all existing stay green)

1. **Multi-occupancy allowed:** N agents can occupy one cell; hash returns the full set.
2. **Even split conserves sugar:** `Σ share_i == S` (to 1e-12); `s(cell) ← 0` after.
3. **Even split equal:** k co-occupants each get `S/k`.
4. **Contest split conserves & weights:** `Σ share_i == S`; higher-φ gets larger share; κ=0
   reproduces even split exactly (to 1e-12).
5. **Split order-independence:** shuffling intra-cell occupant order does not change any
   `share_i` (determinism property, §3.4).
6. **Offspring placement:** child spawns on parent cell; joins occupant set and next split.
7. **Movement candidate set:** equals von Neumann neighbourhood incl. current cell, with NO
   unoccupied filter.
8. **Per-capita self-limiting:** given a rich cell with rising occupancy, `expected_per_capita_
   yield` strictly decreases — verify the evaluator returns lower U for the rich cell as it fills.
9. **Move-cost wiring:** flat cost subtracts on move and not on stay; terrain move-cost lookup
   defaults to 0 (no types yet).
10. **Neutrality reduction:** with affinity=1, crowd_response=1, move_cost=0, U reduces to
    per-capita yield; in forced single-occupancy this equals the current greedy rule.
11. **ψ re-point inactive:** crowd_response ≡ 1.0; ψ does not alter movement this stage; ψ does
    NOT read an adjacency count (guard against the stale signal).
12. **Consumers handle bands:** partner search, pool grouping, joint-task cohort each return
    correct results for a cell with 0, 1, and many occupants (no silent empty).

---

## 7. Gates (run in order; each a blocking STOP on failure)

### 7.1 Recovery gate (MANDATORY, blocking) — replaces the usual equivalence gate

Resource-split changes the core harvest rule, so "feature-off = bit-identical" is impossible at
the substrate level. The honest gate is **recovery in the single-occupancy limit**: prove the new
substrate is a correct *generalisation* of the current model, by forcing the regime where it must
coincide.

Force single occupancy via a temporary hard ceiling `K_cell = 1` (the saturation ceiling at its
hard limit — same machinery a saturation penalty would use), with κ=0, move_cost=0, affinity=1,
crowd_response=1. In this regime:

```
Recovery run: 100×100, locked science N (read & assert), seed=42, C, static world, 500 steps,
              K_cell=1, κ=0, move_cost_flat=0, terrain off
→ compare against a reference run from the current committed model, same config.
```
Compare: N(t) exact integer match every step; mean_wealth, gini, mean_cred to 1e-9; births,
deaths exact; final positions exact. **Divergence → halt, report.** (Likely cause: split or
candidate-set change leaking into the K_cell=1 path, or an RNG-draw-order change from removing
the unoccupied filter — guard so draw order is preserved in the recovery regime.)

Then **lift the ceiling** (`K_cell = ∞`) for the real multi-occupancy runs below.

### 7.2 C-behavioural check (report; interpret against pre-registration)

Run with true multi-occupancy: `100×100, locked science N, seed=42, C, static world, ≥2000
steps` (let the init transient settle), at **two contest settings** so contest's effect is
attributable:
- **κ = 0 (scramble reference):** pure even split.
- **κ = 1 (contest, the live C setting):** Cred-weighted split.

Report and plot, for each:
- **Emergent per-cell density distribution** at steady state (agents/cell), and the
  population-weighted mean.
- **C viability:** N(t) settles to a sensible band (not extinction, not unbounded). Compare κ=0
  vs κ=1.
- **Cred–wealth coupling (κ=1 only):** does φ-weighting produce a wealth gradient by Cred? Report
  Cov(φ, wealth) and the Cred distribution — watch for Matthew-runaway (collapsing diversity,
  one dominant high-φ lineage). Do NOT mitigate in this stage; report it as a flag if it appears.
- **Self-limiting confirmation:** density should stabilise (per-capita intake → metabolic
  break-even), not grow without bound or crash to zero from overcrowding.

### 7.3 Density validation against ethnography (report) — the §1-scale payoff

Convert steady-state agents/cell → persons/km² using `cell_area_km2 = 100`. Under flat/uniform
terrain (no types yet) density will be roughly uniform; report the absolute value and check it
is **physically sane for a generalist forager landscape** — order 0.1 persons/km² (the neutral-
terrain band), not 10 and not 0.001. (The full harsh/fertile 10–100× spread is a **6.0b**
target once terrain grades capacity — register that here, do not expect the spread in 6.0a.)
Pre-register: a flat-terrain density wildly outside ~0.01–1 persons/km² is a flag that
per-capita need vs sugar regrowth is miscalibrated for the declared cell scale — investigate
before 6.0b.

### 7.4 N_carry / N ratio flag

The locked science N (≈2300; read & assert the actual value) sits on an unresolved N_carry
re-derivation for 100×100. Multi-occupancy changes effective capacity (density now self-limits
via split, not via a 1/cell cap), so the old N_carry may no longer even be the right construct.
**Do not re-litigate N_carry here.** Report the settled N and whether the population sits in a
viable band; flag if it pins or crashes. This stage's self-limiting density is itself evidence
about effective capacity — note it for the eventual N_carry reconciliation in the design doc.

### 7.5 Si-portability note (report only, NO Si runs)

One paragraph. The substrate is agent-agnostic: Si reads the same cells, harvests via the **even
split** (κ=0, Si has no Cred), moves by the same diffusion gradient with its own utility (no Cred
term, ψ against the foraging-spot signal when activated — MODEL_SPEC §54). Confirm in code that
the split/movement substrate references no C-only state except inside the κ>0 contest branch
(which Si never enters). State whether the port is clean (expected: yes — contest is the only
C-specific harvest path, cleanly branched) or whether anything snagged.

---

## 8. Report

HTML `outputs/stage6_0a_substrate/report_stage6_0a.html`, all plots embedded. Sections:
1. **Config echo** — asserted locked science values; declared `cell_area_km2`; κ settings;
   move-cost settings.
2. **Recovery gate** — "single-occupancy limit reproduces current model to 1e-9" or divergence
   + resolution.
3. **C-behavioural check** — per-cell density distribution, N(t) for κ=0 vs κ=1, Cov(φ,wealth),
   Matthew-runaway flag. Pre-registered reading then observed.
4. **Density validation** — persons/km² vs ethnographic sanity band; calibration flag if outside.
5. **N_carry / N ratio flag.**
6. **Si-portability note.**
7. **Trait-semantics confirmation** — ψ re-pointed & held neutral; joint-task/pool consumers
   read the band correctly with no silent empties; list of anything punted to the trait
   re-expression deliverable.

---

## 9. Success criteria

| Criterion | Target |
|---|---|
| Spatial scale declared | `cell_area_km2=100`, recorded in MODEL_SPEC + config |
| Multi-occupancy substrate | Cells hold many agents; hash returns occupant sets |
| Resource-split harvest | Even split (scramble) as floor; sugar conserved |
| Cred contest for C | κ-weighted split; κ=0 recovers even split exactly |
| Diffusion movement | Local von-Neumann gradient; per-capita self-limiting; no unoccupied filter |
| Move cost | Flat (active, default 0) + destination-terrain (hook, off) |
| Crossing/path cost | Not built (dissolved by diffusion) — confirmed absent |
| Full-form utility w/ neutral hooks | affinity & crowd_response present, =1.0; reduces correctly |
| ψ re-pointed, held neutral | Reads occupancy not adjacency; no movement effect this stage |
| Consumers ported | Partner search, pool, joint-task handle bands; no silent empty |
| Offspring on parent cell | Yes |
| Recovery gate | Single-occupancy limit = current model to 1e-9 / integer-exact |
| C viability under multi-occupancy | Settles to sensible band, κ=0 and κ=1 |
| Density sane vs ethnography | ~0.01–1 persons/km² on flat terrain |
| Existing suite green; new tests pass | Yes |
| Report embeds all plots | Yes |

---

## 10. Out of scope (do NOT build)

- **Graded terrain / terrain types / metabolic multiplier** → Stage 6.0b (this substrate is its
  floor).
- **Resource affinity & crowd-response *behaviour*** → trait re-expression deliverable + later
  stages. Hooks only, neutral, here.
- **Full trait re-expression for band-on-a-cell** → next deliverable. Only the minimal
  don't-break ruling (§5) here.
- **Saturation penalty as a global force** → dropped by design; crowd-response is a per-agent
  trait (ψ), inactive now.
- **Dispersal** (offspring to neighbour) → deferred; offspring on parent cell.
- **Crossing/path move cost & step-wise locomotion** → not needed under diffusion.
- **Long-range awareness / navigation** → dropped; movement is local diffusion.
- **Matthew-runaway mitigation** → only if §7.2 shows pathology; build nothing pre-emptively.
- **N_carry re-derivation** → design-doc reconciliation, not here.
- **Any Si runs, inversion protection, H1(ii) work.**

---

*End of Stage 6.0a Substrate Blueprint v1.0 — 2026-06-02. Followed by Stage 6.0b (graded terrain
+ metabolic multiplier), whose earlier draft `SiC_Games_Stage6_0_Terrain_Blueprint.md` must be
revised to stand on this substrate.*
