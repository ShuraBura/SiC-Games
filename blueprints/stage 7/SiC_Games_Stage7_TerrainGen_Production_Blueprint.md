# SiC Games — Stage 7 Terrain Generator (Production Port) — CC Blueprint

**Status:** Ready for implementation
**Owner of strategy/design:** Dr Horrible (chat)
**Executor:** Claude Code (CC)
**Companion artifact:** `SiC_Games_Terrain_Oracle_Battery.json` (the equivalence oracle — REQUIRED, see §6)
**Reference implementation:** the confirmed HTML/JS prototype `sic_terrain_prototype.html` (the validated judgment tool; this blueprint ports it)

---

## §0 — Reading order & non-negotiables

1. Read this entire blueprint before writing code.
2. This is a **port with equivalence**, not fresh authorship. The prototype is the authoritative reference for every formula and cutoff. CC does not redesign, "improve," or re-derive the pipeline. Where this document and the prototype disagree, **STOP and ask** — do not silently choose.
3. A **failed gate (§6, §7) is a blocking STOP** per CLAUDE.md Rule 11. It is not a coding-agent judgment call to relax a threshold or proceed.
4. CC must not self-upgrade any citation to `[VERIFIED]` beyond what §10 explicitly authorises with stated provenance.
5. Run the blueprint straight through to completion. The only mid-run stop is a failed acceptance check.

---

## §1 — Objective & scope

Port the derive-from-primitives terrain generator into the Python/Mesa codebase as **precomputed static arrays**, plus the per-map `characterize_map()` diagnostic. The generation pipeline is:

```
elevation (fbm + ridge)
  → water level / open-water mask
  → flow accumulation → rivers
  → water-accessibility decay field
  → moisture → NPP → forestness
  → forage / game / cost / risk fields
  → biome classification (woody-cover ladder)
```

### In scope
- Deterministic terrain generation from the 5 knobs + seed → frozen `(100,100)` field arrays.
- Precomputed `(100,100,4)` neighbour cost-to-cross array.
- `characterize_map()` → the per-map diagnostic vector, **saved with every generated map**.
- Tests, equivalence gate, acceptance checks.

### Explicit non-goals (do NOT implement)
- No agent logic, no Mesa agent classes, no scheduler.
- No Si mechanics. (Architecture seam only — see §3.4.)
- No seasonal resources, migration, or game dynamics over time — that is **Stage 2**.
- No changes to the validated formulas or cutoffs in §2.
- No new biomes, no reclassification scheme beyond the woody-cover ladder.

---

## §2 — The locked pipeline spec (transcribe, do not re-derive)

Grid: **N = 100** (100×100 cells). Each cell = **100 km²** → cell edge = **10 000 m**.

### §2.1 Knobs (all in [0,1])
| Knob | Symbol | Meaning |
|---|---|---|
| Mountainousness | `relief` | amplitude of high ground; gates mountain biome |
| Roughness | `rough` | octave gain / high-frequency detail |
| Water abundance | `waterK` | open-water level + rainfall contribution |
| Forest coverage | `forestK` | tree bias on the woody-cover axis |
| Aridity | `aridK` | global productivity suppressor |
| Seed | `seedStr` | RNG seed (string hashed → uint32) |

Determinism contract: **same (knobs, seed) → byte-identical arrays.** Use a seeded PRNG (mulberry32-equivalent) and a value/fbm noise built from it. Seed hashing must match the prototype's `hashSeed` (string → uint32). Two independent noise fields are derived: primary from `seed`, secondary from `seed XOR 0x9e3779b9`.

### §2.2 Elevation
- fbm noise (multi-octave) with octave gain driven by `rough`.
- ridge component (1 − |noise|, sharpened) for high ground.
- `raw = fbm*(1 - relief*0.6) + ridge*(relief*0.6)`.
- **Normalise** raw to [0,1] via min-max over the field (record raw min/max span as diagnostic only).

### §2.3 Physical relief envelope (declared, not recovered)
The normalised field discards magnitude, so relief is **declared** from the relief knob:
```
RELIEF_FLOOR_M = 120     # peak-to-trough at relief=0
RELIEF_CEIL_M  = 2500    # peak-to-trough at relief=1
SEA_LEVEL_M    = 0
reliefAmpM = RELIEF_FLOOR_M + (RELIEF_CEIL_M - RELIEF_FLOOR_M) * relief
```
Absolute elevation of a land cell (metres) = `elev_norm * reliefAmpM + SEA_LEVEL_M`.

### §2.4 Water level & open-water mask  ← contains the linearisation fix
```
waterLevel = (waterK ** 1.2) * 0.42        # NOTE: power 1.2, NOT waterK*waterK
isWater[i] = elev_norm[i] < waterLevel
```
**Critical:** the power is **1.2**, not 2. The old `waterK*waterK` squaring suppressed water to <10% until `waterK≈1` and is a fixed bug. Do not reintroduce it.

### §2.5 Flow accumulation → rivers
- Process land cells in descending elevation order; accumulate flow downslope to the lowest of the 4-neighbours.
- `riverThresh` set from the flow distribution (prototype: relative to `fmax`); `isRiver[i] = (!isWater[i] && flow[i] > riverThresh)`.

### §2.6 Water-accessibility field
- BFS distance `dist[i]` from the nearest water OR river cell (4-neighbour).
- `wateracc[i] = isWater ? 1 : exp(-decay * dist[i])`.

### §2.7 Moisture / NPP / forestness
```
moist[i]      = (noise2-derived rainfall) blended with wateracc
wet[i]        = clamp( 0.45*moist[i] + 0.55*wateracc[i] ) * (1 - aridK*0.92)
elevPenalty   = 1 - max(0, elev-0.6)/0.4
slopePenalty  = 1 - slope*0.7
npp[i]        = max(0, wet[i] * elevPenalty * slopePenalty)        # 0 on water
forestness[i] = clamp( wet[i]*0.7 + forestK*0.5 - elev[i]*0.3 )    # 0 on water
```

### §2.8 Forage / game / cost / risk
```
forage[i] = min(1, npp[i] * (0.6 + 0.6*forestness[i]))                        # 0 on water
# game: hump-shaped in NPP, peaks at MODERATE npp and OPEN (low forestness)
hump      = exp(-((npp[i]-0.5)/0.22)**2)
openness  = 1 - forestness[i]
game[i]   = min(1, hump * (0.35 + 0.75*openness))                            # 0 on water
cost[i]   = isWater ? 1 : min(1, 0.15 + slope*0.85 + (elev>0.7 ? elev-0.7 : 0))
risk[i]   = isWater ? 0.85 : clamp_low(0.02, 0.12 + exposure + thirst - shelter)
            exposure = slope*0.5 + max(0,elev-0.55)*0.6
            thirst   = (1-wateracc)*0.4
            shelter  = forestness*0.15
```
`game` is a **cell property**, NOT a biome-defining gate. (This matters — see §2.9.)

### §2.9 Biome classification — the woody-cover ladder
Biome codes: `0 water · 1 wetland · 2 forest · 3 savanna/woodland · 4 grassland · 5 desert · 6 mountain`.

Forest / savanna-woodland / grassland are **three rungs on one woody-cover axis (`forestness`)**, per the forest–savanna mosaic literature (§ Scientific grounding). Game does **not** define savanna; it is a property that already peaks in open moderate-NPP cells, so the open→closed woody gradient *is* the hunter(open)↔gatherer(closed) resource gradient with no special-casing.

```
W_FOREST = 0.45     # forestness >= this  → forest (closed canopy)
W_SAV    = 0.18     # forestness in [W_SAV, W_FOREST) → savanna/woodland (mosaic matrix)
                    # forestness < W_SAV  → open grassland
mtnElevThresh  = 0.72 + (1-relief)*0.5     # relief=0 → unreachable → no mountains
mtnSlopeThresh = 0.18 + (1-relief)*0.4

for each land cell (isWater handled first → biome 0):
    if elev > mtnElevThresh and slope > mtnSlopeThresh:        biome = 6   # mountain
    elif npp < 0.10:                                          biome = 5   # desert
    elif dist <= 2 and npp > 0.45 and slope < 0.12:           biome = 1   # wetland/floodplain
    elif forestness >= W_FOREST:                              biome = 2   # forest
    elif forestness >= W_SAV:                                 biome = 3   # savanna/woodland
    else:                                                     biome = 4   # grassland
```
Evaluation order is **mandatory** (mountain → desert → wetland → forest → savanna → grassland).

---

## §3 — Precompute-as-static-arrays (locked architecture principle)

### §3.1 Terrain is frozen
All terrain fields are computed **once at world initialisation** and never recomputed inside any future agent loop. Store as read-only arrays (e.g. numpy arrays flagged non-writeable after generation).

### §3.2 Neighbour cost array
Precompute a `(100, 100, 4)` array `neighbour_cost[y, x, d]` for the 4 directions, derived from `cost`. Cost-to-cross from a cell to a neighbour uses this precomputed array — **no terrain computation in the step loop** (locked principle: "cost-to-cross as a precomputed (100,100,4) neighbour-cost array").

### §3.3 Field set returned
`generate_world(knobs) → WorldFields` containing: `elev, slope, slopeDeg, wateracc, isWater, isRiver, forage, game, cost, neighbour_cost, risk, biome, npp, forestness, reliefAmpM, SEA_LEVEL_M`.

### §3.4 Si seam (architecture only — do NOT implement Si)
Structure generation so every terrain field is consumed through a thin accessor, so an eventual Si port can run on the *same matched world* without touching generation. No Si code now; just don't hard-wire C-only assumptions into the field layout.

---

## §4 — `characterize_map()` (the durable per-map mechanic)

Port the prototype's `characterizeMap`. This runs **once per generated map** and its output vector is **saved alongside the map** in `outputs/[stage_label]_seed[N]/` (e.g. `map_vector.json`). Downstream model runs validate against this saved vector. It is not throwaway analysis — it is a permanent measurement layer.

Returned vector (keys must match the oracle JSON):
- `biomeFrac`: `{forest, savanna, grassland, wetland, desert, mountain}` — each as **% of land** cells.
- `waterPct` (open water, % of all cells), `riverPct` (% of land), `wetlandPct` (% of land), `hydratedPct` (open water + rivers + wetland, % of all cells).
- `reliefEnvelopeM`, `elevMinM`, `elevMaxM`, `elevMeanM`, `meanSlopeDeg`, `maxSlopeDeg`, `steepLandPct` (>15°).
- `gameHumpPeak` (NPP bin position where mean game is maximal, 0..1 or null).
- `adjacency`: 7×7 shared-edge count matrix (4-neighbour, land-land), biome-code indexed.
- `forestTouchSavanna`, `forestTouchGrassland` (fraction of forest's external edges), `forestSavannaSharedEdges` (raw count).

**Reporting emphasis (locked decision):** `hydratedPct` is the headline water figure; `waterPct` (open water) is a sub-figure. Open-water alone understates wetness because rivers + wetland fringe carry most forager-relevant hydration.

---

## §5 — Tests CC must write (pytest)

1. **Field sanity:** every field within its documented range; no NaN/Inf; `npp/forage/game/forestness == 0` wherever `isWater`.
2. **Determinism:** `generate_world(same knobs, same seed)` twice → arrays byte-identical (`np.array_equal`). Different seed, same knobs → different but same-distribution (not equal).
3. **Water-mask correctness:** fraction of `isWater` matches `waterLevel` cutoff on the normalised elevation field.
4. **Precompute immutability:** terrain arrays are non-writeable after `generate_world` returns; attempting to write raises.
5. **Biome ladder ordering:** synthetic forestness ramps map to grassland→savanna→forest at exactly `W_SAV`/`W_FOREST`.
6. **`neighbour_cost` consistency:** equals `cost` of the target neighbour (or impassable sentinel at edges).

---

## §6 — Equivalence gate (verdict-by-assertion) — BLOCKING

The companion file **`SiC_Games_Terrain_Oracle_Battery.json`** contains **27 reference worlds** (9 knob configs × 3 seeds: `42, 7, 1001`) each with its prototype-computed characterization vector.

**CC must:** generate each of the 27 worlds in Python with the identical knobs+seed, run `characterize_map()`, and compare to the reference vector.

**Pass thresholds (pre-committed):**
- Every `biomeFrac` component within **±3 percentage points** of the reference.
- `waterPct`, `riverPct`, `wetlandPct`, `hydratedPct` within **±3 pp**.
- `reliefEnvelopeM` within **±5 %** (it is a deterministic function of `relief`, so expect near-exact).
- `meanSlopeDeg` within **±0.3°**.
- `gameHumpPeak` within **±1 bin** (±0.05).

If the Python noise/PRNG cannot be made byte-identical to the JS prototype, biome fractions may drift beyond ±3 pp. **If that happens: STOP and report** — do not widen the tolerance unilaterally. The resolution (re-implement the exact JS PRNG/noise, or re-baseline the oracle from Python with Dr Horrible's sign-off) is a supervisor decision.

Representative reference points (full set in JSON):
| config (seed 42) | forest | savanna | grassland | desert | open water / hydrated |
|---|---|---|---|---|---|
| `mosaic_mid` | 5.3 | 76.0 | 5.1 | 12.6 | 2.4 / 7.9 |
| `forest_dom` | 86.9 | 4.5 | 0.0 | 5.9 | 2.4 / 9.5 |
| `wet_lakes` | 36.8 | 54.7 | 0.0 | 2.3 | 30.8 / 45.0 |

---

## §7 — Acceptance checks (pre-registered readings) — BLOCKING

Run in Python after the equivalence gate passes. These are green-block findings; if all pass, the stage is done with no prose report.

**A7.1 — Full forest gradient reachable.** Sweep `forestK ∈ {0, 0.2, 0.4, 0.6, 0.8, 1.0}` (relief 0.4, rough 0.5, waterK 0.5, aridK 0.35, mean of seeds 42/7/1001). Forest coverage must rise monotonically (allow ±1 pp noise) from **< 2 % at forestK=0** to **> 70 % at forestK=1.0**. Reference gradient (mean of 3 seeds), reproduce within ±3 pp:
```
fK=0.0 → forest 0.0,  sav 7.7,  grass 76.7
fK=0.2 → forest 0.0,  sav 28.1, grass 56.2
fK=0.4 → forest 1.9,  sav 61.2, grass 21.2
fK=0.6 → forest 11.9, sav 72.4, grass 0.0
fK=0.8 → forest 37.9, sav 46.5, grass 0.0
fK=1.0 → forest 73.8, sav 10.5, grass 0.0
```

**A7.2 — Coexistence band exists.** Derive the habitable envelope (cap aridity where desert > 50 % of land, cap relief where mountain > 50 %; reproduce prototype caps ~aridity≤0.75, relief≤1.0). LHS-sample the habitable box (≥150 samples × 4 seeds). Fraction of samples with **forest ≥ 10 % AND savanna ≥ 10 %** (whole-map, mean across seeds) must be **≥ 0.20**. (Prototype reference: ~0.29.)

**A7.3 — No matrix-dominance artifact.** In the same LHS sweep, mean **grassland** coverage must **not** exceed mean savanna/woodland coverage, and grassland mean must be **< 35 %**. (This guards against regressing to the old steppe-flood bug. Prototype reference: grassland ~20 %, savanna ~38 %.)

**A7.4 — Game field is unimodal (hump-shaped) in NPP.** Bin land cells by NPP into 20 bins; compute mean `game` per bin over bins with ≥3 cells. The resulting curve must be **unimodal**: non-decreasing up to its peak bin and non-increasing after, allowing a per-step noise tolerance of **0.03**. Worlds with **fewer than 4 populated bins** (extreme near-desert with almost no NPP range) are **exempt** — there is insufficient NPP range to define a hump. `gameHumpPeak` is recorded as a diagnostic but is **NOT gated** (see note). Verified: 600/600 habitable-box LHS worlds pass, 0 exempt, across the full aridity range to `aridity_cap`.

> **A7.4 history (two restatements — both surfaced via Rule 11 STOPs, both supervisor-approved):**
> 1. *Original (wrong):* "mean game higher in grassland+savanna than forest." Confounded — biome assignment correlates with NPP, inverting the openness effect. The prototype does not exhibit this; prototype is authoritative (§0.2).
> 2. *First fix (incomplete):* `gameHumpPeak ∈ (0.25,0.72)`. Failed on the arid edge of the LHS box (89/600 worlds, aridK 0.76–0.82): in near-desert worlds the NPP distribution truncates so the measured "peak" is the left flank of a hump whose right half has no land to sit on. The band was calibrated on the battery (aridK ≤ 0.65) and never saw the dry edge the sweep reaches. Peak-position is undefined when NPP range is truncated.
> 3. *Current (correct):* assert **unimodality** (the property that actually holds across the whole box) and demote peak-position to a recorded diagnostic. The hump *shape* is robust to the arid shift; the hump *location* is not a meaningful gate near desert. This is the same lesson twice: assert the curve shape, not a summary statistic of it.

---

## §8 — Must-be-seen artifacts (everything else is assertion)

Only outputs whose **shape** carries science and cannot reduce to a threshold:

1. **Forest-knob gradient stacked bar** — biome composition (forest/savanna/grassland) across `forestK ∈ {0…1}`. Shows the gradient is smooth and spans the full range.
2. **One `mosaic_mid` biome map render** (PNG) — the canonical mixed world, so the spatial mosaic structure is eyeballable once.

No prose report beyond a one-line green if §5–§7 all pass. Save artifacts to `outputs/stage7_terrain/`.

---

## §9 — Definition of done

- [ ] §5 unit tests all pass.
- [ ] §6 equivalence gate green (27/27 worlds within tolerance) **or** documented STOP escalated to supervisor.
- [ ] §7 acceptance checks A7.1–A7.4 all green.
- [ ] §8 artifacts emitted.
- [ ] §10 doc-update sub-directives complete (independently verifiable).
- [ ] Terrain fields confirmed precomputed & immutable; `neighbour_cost` present.

Terrain gates and doc-updates are each checkable independently; the stage is done only when both are green.

---

## § Scientific grounding (why the design is what it is — reference, not the authoritative log)

The classifier and field design are literature-grounded; full entries are logged in §10.

- **Woody-cover ladder (§2.9):** forest–savanna mosaic ecology treats forest / savanna-woodland / grassland as points on a continuous woody-canopy-cover axis (savanna ≈ 5–10 % up to ~25–30 % canopy; forest above; grassland below), with savanna/woodland as the mosaic *matrix* and forest as a water-associated element. This is why savanna is a ladder rung, not a game-gated special class, and why the old residual-"steppe" default (which flooded the map) was wrong.
- **Game as open-peaking property (§2.8):** communal-drive-hunt savanna game (large gregarious ungulates, high flight-initiation-distance, herding) is conceptually an *open-ground* resource; forage (NPP, plant) peaks in closed canopy. The intended form is `hump(NPP) × openness`. **Caveat (see §12):** as built, NPP and forestness are coupled through moisture, so the openness term is mechanically near-inert and game tracks the NPP hump (peaking in productive *forest*), NOT open ground. The hunter↔gatherer resource separation is therefore NOT yet expressed by the terrain substrate alone — it is deferred to the game/migration rework. (Morin et al. 2024.)
- **Full gradient, not minority-forest (§7 A7.1):** foragers occupy the entire forest↔savanna gradient (closed-forest Aché through woodland-savanna Hadza), so forest-dominated worlds must be reachable, not capped as a minority. (Marginal-habitat literature; corrects an earlier over-read.)

---

## §10 — Doc-update sub-directives (execute as part of this stage)

Each is independently verifiable (provenance + numbers correct). Apply to the authoritative docs on the local drive.

### §10.1 — LITERATURE.md: three entries

**Entry — Morin, Bird, Winterhalder & Bliege Bird (2024).** "Why Do Humans Hunt Cooperatively? Ethnohistoric Data Reveal the Contexts, Advantages, and Evolutionary Importance of Communal Hunting." *Current Anthropology* 65(5):876–921. DOI 10.1086/732354.
- Role: **savanna-game / communal-drive-hunt (CDH) anchor** — grounds the soft-gate (steep-but-finite, not hard step) for open-ground game.
- Logged findings (numbers): ungulate CDH success **67.2 %** (85% CI 56.5–80.1) vs **42 %** encounter (CI 36.1–49.0); flight-initiation distance at 40 kg **177 m** (ungulates) vs **45 m** (non-ungulates); escape velocity 59 vs 39 km/h; herding roughly **doubles** CDH probability (0.76 vs 0.41 at 40 kg). Patch-creation framing: open environments = steering herds to vulnerable locations; forests = funnel/beater patch-creation. CDH advantage is **episodic / seasonal-aggregation-dependent**, not a steady tap.
- Provenance: **full text read** (chat session); tables 1, 4, 5, figs 5–8. Tag `[VERIFIED]` authorised on this provenance.

**Entry — Janssen & Hill (2014).** "An agent-based model of resource distribution... cooperative hunting among Aché." DOI 10.1007/s10745-014-9693-1.
- Role: **forest-game anchor.**
- **CORRECTED reading (supersedes any prior abstract-only summary):** cooperative hunting is **net slightly negative on mean yield (~−4 %)**, positive only on **variance reduction**; the ~7–8 optimal-band figure is a **smooth risk/return tradeoff tangent, NOT a feasibility threshold**; there is **no access gate** anywhere in the model — solo hunting works, just worse. Any concept-map text treating cooperative hunting as yield-superadditive is wrong and must be corrected (see §10.2).
- Provenance: full text read (chat session). Tag `[VERIFIED]` authorised.

**Entry — Forest–savanna mosaic / woody-cover coverage anchor.** (Ecoregion + savanna-ecology literature; e.g. WWF forest–savanna mosaic ecoregions; savanna woody-cover definitions ~5–10 % lower / ~25–30 % upper canopy.)
- Role: **terrain coverage target / classifier grounding** for the woody-cover ladder.
- Logged: savanna = wooded grassland on a woody-cover continuum; mosaic = savanna/woodland matrix + minority gallery/patch forest + grassland; **foragers span the full gradient** (do not force forest-minority).
- Provenance: secondary/encyclopedic + ecology sources (web). Tag **`[SECONDARY]`** — do **NOT** mark `[VERIFIED]` (no single primary full-text read); flag for a future primary-source pass if a hard numeric cutoff is ever locked.

### §10.2 — Concept map corrections
Apply the J&H-2014 correction wherever the resource/hunting concept map treats cooperative hunting as increasing mean yield: change **yield-multiplier framing → variance-reduction framing** in the affected sections (the §2/§4/§5 cooperative-hunting nodes per the standing concept map). Cooperative hunting: mean yield ≈ flat-to-slightly-negative; benefit = reduced failure variance.

### §10.3 — Watch-item (log as a question, not a finding)
**Forest/savanna bistability.** Forest and savanna are alternative stable states in the medium-tree-cover zone (fire-mediated). Flag as a potential **thematic resonance OR confound** for a model about *civilisational* bistability — the substrate may exhibit vegetation bistability in the same parameter region where civ-strategy coexistence is studied. Revisit; do not act on it now.

### §10.4 — ARTIFACTS.md / MODEL_SPEC.md / INDEX.md
- **ARTIFACTS.md:** register the new terrain module, `generate_world`, `characterize_map`, the saved per-map `map_vector.json` convention, and the oracle battery file.
- **MODEL_SPEC.md:** record the locked pipeline (§2) verbatim — knobs, `waterLevel = waterK**1.2 * 0.42`, the woody-cover ladder cutoffs `W_FOREST=0.45 / W_SAV=0.18`, desert `npp<0.10`, relief envelope 120–2500 m, cell = 100 km². Mark these **locked** — EXCEPT the `game` field (§2.8), which is marked **PROVISIONAL — reworked in Stage 7.2** (see §12). Terrain geometry, water, biomes, forage, cost, risk are locked; game is a placeholder.
- **INDEX.md:** add Stage 7 terrain entries so the pipeline is answerable macro→micro without grepping this blueprint.

### §10.5 — Citation-tag guard (CLAUDE.md)
CC logs `[VERIFIED]` ONLY for Morin 2024 and J&H 2014 (full-text-read provenance stated above). The mosaic/woody-cover anchor is `[SECONDARY]`. CC must not upgrade `[SECONDARY]`→`[VERIFIED]` without a logged primary full-text read.

---

## §11 — Stopping rules summary
- Failed §6 equivalence (cannot reach ±3 pp after matching PRNG/noise) → **STOP**, escalate (re-implement exact noise vs re-baseline oracle is a supervisor call).
- Any §7 acceptance check red → **STOP**, report which and the observed values.
- Prototype vs blueprint disagreement on any formula/cutoff → **STOP**, ask.
- Everything green → emit §8 artifacts, complete §10, report one-line green. No prose report otherwise.

---

## §12 — Pre-registered finding: game-field openness inertia (→ Stage 7.2)

**Logged BEFORE Stage 7.2 analysis runs, per the pre-register-before-running principle. This is a finding, not a footnote.**

### The finding
The game field (§2.8) is intended as `game = hump(NPP) × openness`, encoding savanna game as an open-ground resource distinct from closed-canopy forage. **As built, the openness term is mechanically near-inert.** Because `forestness` and `npp` are *both* increasing functions of moisture (`forestness = wet*0.7 + forestK*0.5 − elev*0.3`; `npp` driven by the same `wet`), NPP and forestness are positively coupled. Consequence: **open cells (low forestness) exist only where it is dry (low NPP)**, so "open AND productive" is an empty region of the field. Verified headless: across 12 worlds, zero cells satisfy NPP ∈ [0.4,0.6] AND forestness < 0.25.

Therefore mean game is **highest in forest** (which owns the productive NPP-hump zone) and lowest in grassland (dry, hump≈0) — the *opposite* of the open-ground-game intent. Example (`mosaic_mid`, seed 42): forest game 0.543 (NPP 0.394) vs savanna 0.177 (NPP 0.208) vs grassland 0.047 (NPP 0.115).

### What this does and does NOT break
- **Does NOT break terrain (Stage 7).** Geometry, water, biomes, coverage, forage, cost, risk are all sound and gate-green. The game *field shape* (hump in NPP) is correct and asserted by A7.4.
- **DOES mean the hunter↔gatherer resource separation is NOT expressed by the terrain substrate alone.** Game and forage currently co-peak in forest. The earlier design claim that the woody-cover ladder yields the hunter/gatherer gradient "for free" is **corrected**: the ladder fixes biome *coverage* (the steppe-dominance bug, genuinely solved), but it does not by itself produce a savanna-game vs forest-forage split.

### Hypothesis for Stage 7.2 (pre-registered, to be tested then, NOT now)
The hunter/gatherer split is a **missing mechanic**, not a tuning problem (cf. the density-problem learning). Candidate fix: **decouple savanna game from the general NPP hump** — make game key off a savanna/open-woody-grassland *herd-density* field (Morin: large gregarious ungulates, clustered, high-FID, open-ground), so game is a genuine resource peak in the open-woody zone, distinct from forest forage. This likely ties into the Stage 2 seasonal-resources / game-migration arc (game aggregates seasonally — Morin's episodic-CDH finding), so Stage 7.2 may merge with or directly precede that work.

### Stage 7.2 scope (placeholder — to be blueprinted separately)
Rework the game field so savanna/open-ground game is a real, separable resource peak; re-assert a *corrected* hunter/gatherer-separation gate (one that is not confounded by NPP–forestness coupling — e.g. a herd-density field compared on its own terms, not biome-sorted game means). Until then, `game` is **PROVISIONAL** in MODEL_SPEC.
