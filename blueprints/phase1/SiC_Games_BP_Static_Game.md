# SiC Games — Blueprint: Static Game Layer + Energy-Balance Decision System

**Document:** `SiC_Games_BP_Static_Game.md`
**Status:** READY FOR EXECUTION
**Stage:** Static game (step 1 of the temporal-dynamics arc: static-game → seasonal-forage → seasonal-game)
**Scope:** C agents only. Si excluded entirely (architecture-lens only this round).
**Must-be-seen artifacts:** None — empty set. This is a wiring-and-mechanism stage. Acceptance is fully mechanical. No outcome readings. No prose report on green.

---

## §0 Stage philosophy — read first

This stage validates **mechanism wiring**, not **outcomes**. It builds the game layer and the agent energy-balance decision system against a *provisional* resource ceiling. Because the real, literature-grounded cell carrying capacity is deferred (see DEFERRED_MECHANICS.md entry CC-1), every dynamic produced by this stage is conditional on a placeholder and must NOT be read as a finding.

**Hard rule:** no acceptance check in this blueprint may assert on an outcome that depends on the ceiling being correct. Forbidden in acceptance: agent density verdicts, starvation-rate verdicts, population trajectory shape, any resilience reading. Permitted in acceptance: does the switch fire when energy balance demands it, does game yield read off the correct biome, does the reserve integrate correctly, does the sex ratio match the parameter. Mechanism, not outcome. Letting an outcome reading into acceptance here is the conditional-artefact trap.

---

## §1 Task 1 — Create and seed DEFERRED_MECHANICS.md

Create `DEFERRED_MECHANICS.md` in the project docs directory. This is the running home for discussed-agreed-good-but-deferred mechanics. It closes the documented failure mode of good ideas being discussed and then lost between sessions.

**Format — one entry per mechanic, each with exactly these fields:**

```
### [ID] — [Short name]
- **What:** one-paragraph description of the mechanic
- **Why deferred:** TMTS / depends-on-X / needs-literature / conditional-artefact-risk
- **Literature / rationale anchor:** named sources or stated rationale
- **Seam:** where it will hang off when built; what interface it writes to
- **Status:** DEFERRED / SURVEY-PENDING / RECAL-ADJACENT
```

### 1.1 Seed entries (write all seven verbatim in substance)

---

**GD-1 — Game depletion**
- **What:** Game becomes a depletable local stock that hunting pressure draws down, with regrowth. Standing stock per cell, reduced by local hunting, recovering on a schedule.
- **Why deferred:** TMTS for static game; depends on game-as-stock seam (built here) plus carrying-capacity rate (CC-1). Depletion without a real ceiling divides a placeholder by a placeholder.
- **Literature / rationale anchor:** Redford & Robinson 1987; Vickers settlement-age data; Ross 1978. Key finding: local game depletion is a *sedentism* phenomenon — it emerges where agents stop moving and hunt out a catchment radius. Mobile bands avoid it via trekking, outlier camps, zone rotation. Large slow-breeders deplete first; small fast-breeders persist.
- **Seam:** hangs off the game-as-stock quantity (built in this blueprint, §4) + local hunting pressure + agent mobility/residence time. Couples to density/co-location work, not just seasonality.
- **Status:** DEFERRED

---

**JV-1 — Age-graded juvenile productivity**
- **What:** Replace the binary child age-gate (built here: under-age contributes zero) with a graded productivity-by-age curve, so juveniles forage at age-increasing rates rather than switching from useless to fully productive at one threshold.
- **Why deferred:** TMTS; the binary gate is the minimal correct version. The graded curve is an enhancement.
- **Literature / rationale anchor:** Bird & Bliege Bird 2000 (Meriam juvenile foragers — age-graded shellfishing return rates). Real productivity-by-age curve extractable from that source.
- **Seam:** the age-gate hook built in §6 of this blueprint. Age attribute already exists on agents (Phase-0 lifespan/cred-over-time/age-gated-reproduction work). The graded curve replaces the binary multiplier; nothing else changes.
- **Status:** DEFERRED

---

**CC-1 — Carrying-capacity-from-NPP (cell extractable rate + rivalry)**
- **What:** Replace the provisional biome-scaled cell yield with a literature-grounded cell carrying capacity. Cell characterized by a total extractable caloric rate = f(biome carrying capacity, replenishment rate). Agents drawing on a cell compete for that finite rate — rivalry/competition between co-located agents emerges automatically from dividing the finite rate among workers. Permissible agent density and starvation then *emerge* from energy balance rather than being tuned.
- **Why deferred:** Foundational substrate change touching the entire resource economy (same economy the density calibration rests on — Stage 6.0a). Bundling it with static-game wiring would change the ceiling AND add game AND add the decision rule simultaneously — cannot attribute dynamics. Conditional-artefact risk. Rivalry is *part of* this entry, not separate: rivalry = agents dividing the finite extractable rate, which requires the real rate to exist.
- **Literature / rationale anchor:** Tallavaara 2018 (HG population density as a function of climate/NPP — already in corpus) for the forage/plant ceiling. Ungulate-biomass-from-NPP ecology (Coe-Cumming-Phillipson-type herbivore-biomass-vs-rainfall/productivity relationships) for the game ceiling. Path: NPP → plant biomass (forage ceiling) and NPP → herbivore biomass (game ceiling), both biome-resolved.
- **Seam:** the decision rule (built here, §3) reads cell yield but does not define it. Swapping provisional yield for the derived rate changes the numbers read, not the decision logic. Rivalry switches on when the real rate lands. Likely belongs inside or immediately before RECAL-A (it is precisely the "re-derive fired params from literature" work RECAL-A freezes).
- **Status:** RECAL-ADJACENT

---

**RS-1 — Risk-sensitivity / variance-reduction foraging**
- **What:** Agents value variance reduction, not just mean return. The reason a band runs both subsistence streams in parallel is risk-spreading: game is high-mean/high-variance, forage is low-mean/low-variance. A pure mean-maximizer misses this.
- **Why deferred:** TMTS. The static-game decision rule is a survival-fallback switch (hunt unless starving-and-no-game), not a variance calculation. Risk-sensitivity is its own mechanic and maps directly onto the H1(ii) resilience question.
- **Literature / rationale anchor:** Janssen & Hill 2014. Cooperative hunting net −4% on mean yield but cuts zero-meat-day probability 52%→9%. The band buys variance reduction, not mean.
- **Seam:** modifies the stream-choice input in the decision rule (§3) from affinity/sex-weighted mean return to a risk-adjusted objective. Decision machinery already present; this changes the objective function.
- **Status:** DEFERRED

---

**MR-1 — Physiological reserve anchoring**
- **What:** Ground the agent's physiological energy reserve (body-fat survival store) and the starvation floor in literature, replacing the interim physiology-estimate placeholders.
- **Why deferred:** Literature survey is its own deliverable; bundling a survey into a wiring build mixes task types. Static game uses tagged placeholders.
- **Literature / rationale anchor:** Interim placeholders are textbook physiology, NOT HG-field numbers: reserve-at-full ≈ 100,000 kcal (adult body-fat store); starvation floor ≈ 15,000–25,000 kcal remaining (critical fat depletion, classically ~40% body-weight loss). Survey should confirm/replace with HG-specific values and a literature-defined starvation threshold (caloric-intake-deficit based).
- **Seam:** the reserve state and starvation floor in the energy-balance system (§3). Decision logic unchanged when real values land — only the numbers change.
- **Status:** SURVEY-PENDING

---

**MR-2 — Carried-provision anchoring**
- **What:** Distinct from physiological reserve: the food a forager physically carries while travelling ("on the belt"). Small, short-horizon (days, not months), buffers a single bad foraging day or a travel leg between patches. Governs the short-term "do I have food right now" buffer; physiological reserve governs the long-term starvation floor. These are two different quantities and should be modelled separately.
- **Why deferred:** Needs ethnographic anchor; not required for static-game wiring.
- **Literature / rationale anchor:** Ethnographic foraging-trip literature — trip duration and carried load are recorded in some Ache/Hadza/Martu trip data already in corpus. Placeholder TBD; possibly extractable from existing trip-length data.
- **Seam:** a second, short-horizon buffer in the energy-balance system, sitting above the physiological reserve. Static game does NOT build this — single reserve only. Entry records the eventual split.
- **Status:** SURVEY-PENDING

---

**PL-1 — Pool scale-dependence (personal-carry vs institutional surplus)**
- **What:** Re-scope the existing communal pool mechanic as density-dependent. A small band's "pool" is the sum of what members personally carry — informal, immediate-return redistribution of currently-held food, not accumulation. A true institutional communal pool (standing surplus beyond personal carry) becomes meaningful only at higher population density / greater sedentism.
- **Why deferred:** This is a change to an existing mechanic (the pool exists from earlier stages), not a static-game task. Belongs with the density/co-location revisit.
- **Literature / rationale anchor:** Immediate-return vs delayed-return foraging economies. Immediate-return sharing in small bands is real but hand-to-mouth; institutional surplus pooling is associated with larger, denser, more sedentary groups.
- **Seam:** the existing pool mechanic; adds a density gate distinguishing personal-carry redistribution from institutional surplus. Maps onto the co-location-must-pay thread and the density work.
- **Status:** DEFERRED

---

### 1.2 Acceptance check — Task 1

```
ASSERT: DEFERRED_MECHANICS.md exists in project docs directory
ASSERT: contains exactly 7 entries with IDs GD-1, JV-1, CC-1, RS-1, MR-1, MR-2, PL-1
ASSERT: every entry has all 5 fields (What, Why deferred, Literature/rationale anchor, Seam, Status)
ASSERT: CC-1 status is RECAL-ADJACENT and names Tallavaara 2018
ASSERT: MR-1 and MR-2 status is SURVEY-PENDING
```

Failed gate = blocking STOP (CLAUDE.md Rule 11). Do not proceed to Task 2.

---

## §2 Task 2 — Sex attribute

Add a sex attribute to the C agent.

1. **Attribute:** binary sex (female/male) drawn at agent initialization.
2. **Parameter:** `p_female` — probability an agent is female at init. Default `0.5`. **Tunable** (lives in config/PARAMETERS.md, not hardcoded), so the ratio can be shifted in future without code change.
3. **Rationale note for PARAMETERS.md:** no external-parameter mechanic drives sex ratio in the human case (secondary sex ratio ~105:100, not environmentally driven in any modellable way). 50/50 default is the defensible neutral; tunability is for future experiments, not literature-grounded asymmetry.
4. **Si:** not applicable. Si reproduces by fission and has no sex. Si is out of scope this round; the sex attribute is C-only. The decision rule (§3) does not need a sexless fallback because no sexless agent runs in this stage.

### 2.1 Acceptance check — Task 2

```
ASSERT: C agent carries a sex attribute set at initialization
ASSERT: p_female exists as a tunable parameter, default 0.5
ASSERT: over a large init sample (n >= 5000), observed female fraction is within 0.5 +/- 0.02
ASSERT: no Si agent path references the sex attribute
```

Failed gate = blocking STOP.

---

## §3 Task 3 — Energy-balance decision system

This is the core of the stage. The agent's subsistence behaviour falls out of an energy-balance system; the stream-switch is a consequence of energy balance, not a fixed threshold.

### 3.1 State

Each C agent has:
- **Metabolic burn rate** (kcal/step) — use the existing metabolic burn already in the model (this drives current starvation mortality). Do not introduce a new burn parameter.
- **Energy reserve** (kcal) — integrating store. If an integrating reserve already exists, use it. If only instantaneous intake-vs-burn exists, add a single integrating reserve. Placeholder values, tagged `[PLACEHOLDER — physiology-estimate, pending MR-1 survey]`:
  - reserve-at-full ≈ 100,000 kcal (adult)
  - starvation floor ≈ 20,000 kcal (midpoint of 15k–25k range)
- **Single reserve only** at this stage. The carried-provision/physiological split (MR-2) is deferred — do not build two buffers now.

### 3.2 Intake

- Per step, an agent working a stream acquires kcal = (stream return rate × time worked), where the return rate is the biome-resolved value from the game and forage tables.
- **Capped by cell yield — NON-RIVALROUS at this stage.** Each agent receives its own return rate independently; the cell yield is not divided among co-located agents. Rivalry (agents dividing a finite cell rate) is deferred and folds into CC-1, because rivalry requires the real extractable rate to be meaningful. Tag the non-rivalrous cap `[PROVISIONAL — rivalry deferred to CC-1]`.
- Net per step: reserve += intake − burn.

### 3.3 Stream default by sex

- **Male default:** game (hunt).
- **Female default:** forage.
- This is the strong default — the population mix of both streams emerges from the sex distribution without hardcoding a band-level division of labour.

### 3.4 The switch (energy-balance driven)

The agent switches stream when its energy balance under the current stream is worse than under the alternative, bounded by the starvation floor. Concretely:

- A male defaults to hunting. If the cell has low/no game such that projected intake under hunting fails to cover burn AND the reserve is falling toward the starvation floor, the agent switches to forage **if** forage in this cell covers the deficit better.
- Symmetric for females (switch to game if forage is inadequate and game covers the deficit better), though the female→forage default will rarely trigger a switch given forage's lower variance.
- The switch fires off **cell state (what's available here) + agent energy balance (am I covering burn / approaching floor)** — not a fixed hunger parameter. No new tunable threshold. The "when" is emergent from burn, intake, and reserve relative to the starvation floor.

**Implementation note for CC:** the switch is a per-step evaluation: given this cell's game and forage yields, this agent's burn, and its reserve, choose the stream that best protects the agent from the floor; default to the sex-preferred stream when both streams cover burn comfortably (i.e. only deviate from sex default under deficit pressure). Do not implement a risk/variance calculation — that is RS-1, deferred.

### 3.5 Acceptance check — Task 3

All mechanical. No outcome readings.

```
ASSERT: agent has metabolic burn (reused, not new) and an integrating energy reserve
ASSERT: reserve placeholders tagged [PLACEHOLDER — physiology-estimate, pending MR-1 survey]
ASSERT: reserve integrates correctly — unit test: known intake/burn sequence yields expected reserve trajectory
ASSERT: male agent in a cell with adequate game hunts (does not switch)
ASSERT: male agent in a cell with zero game and falling reserve toward floor switches to forage when forage covers the deficit
ASSERT: male agent in a cell with zero game AND zero forage does not spuriously switch (no stream covers deficit; agent declines toward floor — starvation mortality handled by existing mechanism)
ASSERT: female agent default is forage
ASSERT: intake cap is non-rivalrous and tagged [PROVISIONAL — rivalry deferred to CC-1]
ASSERT: no risk/variance calculation present in the switch (RS-1 not built)
ASSERT: no new hunger/starvation tunable introduced beyond the tagged placeholders
```

Failed gate = blocking STOP.

---

## §4 Task 4 — Game-as-stock seam

Build the seam that lets game later become a depletable stock, without building depletion now.

1. **Cell carries a game quantity** the decision rule reads (used in §3.4 to answer "is there game here?"). At this stage the quantity is a **provisional biome-scaled value** derived from the game return-rate table's biome cells (hump-shaped: peak at savanna/edge, zero at UNANCHORED wetland/mountain and at open water). Tag `[PROVISIONAL — biome-scaled, pending CC-1 ceiling]`.
2. **Depletion is OFF.** Hunting does not reduce the cell's game quantity at this stage. The quantity is a standing readable value, not yet a drawn-down stock.
3. **Rivalry is OFF** (per §3.2; folds into CC-1).
4. The seam is the interface: the game quantity is a per-cell readable field that a future depletion mechanic (GD-1) and the real ceiling (CC-1) will write to. Document the interface so GD-1 and CC-1 write here and nowhere else in the resource layer.

### 4.1 Acceptance check — Task 4

```
ASSERT: each cell exposes a readable game quantity field
ASSERT: game quantity follows biome shape (zero at wetland/mountain/open-water; nonzero peak at savanna/edge)
ASSERT: game quantity tagged [PROVISIONAL — biome-scaled, pending CC-1 ceiling]
ASSERT: hunting does NOT reduce the cell game quantity (depletion off)
ASSERT: interface documented for GD-1/CC-1 write access
```

Failed gate = blocking STOP.

---

## §5 Task 5 — Child age-gate seam

1. **Age attribute already exists** (Phase-0 lifespan/age-gated-reproduction work). Use it; do not add a new age attribute.
2. **Binary gate:** agents under a juvenile-age threshold contribute **zero** subsistence (neither hunt nor forage productively). At/above the threshold, full adult productivity.
3. **Graded curve is OFF** — deferred to JV-1. The binary gate is the seam the graded curve will replace.
4. Use the existing age threshold associated with productivity/maturity if one exists in PARAMETERS.md; if none exists, introduce a single tunable `age_productive_min`, tagged `[PROVISIONAL — binary gate, graded curve deferred to JV-1]`.

### 5.1 Acceptance check — Task 5

```
ASSERT: agents below age_productive_min contribute zero subsistence
ASSERT: agents at/above the threshold contribute full adult productivity
ASSERT: gate uses the existing age attribute (no new age attribute added)
ASSERT: binary gate tagged with JV-1 deferral note
```

Failed gate = blocking STOP.

---

## §6 Document updates (definition of done)

As part of completion, CC updates:

1. **PARAMETERS.md** — register `p_female` (0.5, tunable), the reserve placeholders (MR-1-tagged), the non-rivalrous cap (CC-1-tagged), `age_productive_min` if newly introduced (JV-1-tagged). Each provisional/placeholder value carries its deferral tag.
2. **MODEL_SPEC.md** — add a subsection under the resource/agent layer describing the energy-balance decision system, the sex-based stream default, and the three seams (game-as-stock, child age-gate, non-rivalrous cap), each pointing to its DEFERRED_MECHANICS.md entry.
3. **MODEL_SPEC.md §15 (conflict surfacing)** — if any existing forage test or agent mechanic conflicts with the new decision system, surface the discrepancy here; do not silently fix.
4. **ROADMAP.md** — mark static-game complete; next = seasonal-forage (signal-standalone-first sub-step, then forage coupling).

---

## §7 Stopping rules and definition of done

Tasks run in sequence 1→5. Any failed acceptance check is a blocking STOP (CLAUDE.md Rule 11); CC does not proceed past a failed gate.

**Existing-tests guard:** all pre-existing forage-layer and agent tests must remain green. If the energy-balance system changes forage-layer behaviour, that is a conflict to surface in MODEL_SPEC.md §15, not a silent change.

Definition of done: all five acceptance blocks green, all document updates applied, all provisional values carry deferral tags, existing tests green.

**Must-be-seen artifacts:** none. Empty set. A green run requires no prose report — one-line green confirmation is sufficient. No outcome readings are produced or claimed at this stage.

---

## §8 Files touched

| File | Action |
|---|---|
| `DEFERRED_MECHANICS.md` | Create + seed 7 entries |
| C agent class / model code | Add sex attribute; energy-balance decision system; child age-gate |
| Cell / resource layer | Add game-as-stock readable field (provisional, depletion off) |
| `PARAMETERS.md` | Register p_female, reserve placeholders, non-rivalrous cap, age_productive_min |
| `MODEL_SPEC.md` | Energy-balance subsection + 3 seams; §15 conflicts if any |
| `ROADMAP.md` | Mark static-game complete; next = seasonal-forage |

No Si code touched. No depletion, rivalry, risk-sensitivity, graded juvenile curve, carried-provision, or carrying-capacity mechanic built — all deferred and documented.
