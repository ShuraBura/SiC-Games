# SiC Games — Blueprint: A-3 First-Light Shakedown (50×50, C-only)

**Type:** Exploratory shakedown. **NOT a gate.** First run of the C agent layer on the
Phase 1 terrain substrate. Three of its aims (correctness, dynamics-sanity, capacity
intuition) have no pre-committable thresholds — the output is **must-be-seen** trajectories,
maps, and distributions the supervisor reads. It carries **assertable guards** (bug-catching
rails) but the *findings* are shapes, not a green/red verdict. Do not invent thresholds for
shape-dependent outputs to make them assertable (that is HARKing) — leave them must-be-seen.

This is the **workbench pass** (50×50). The 100×100 confirmation + heavy scaling sweep
(1K→10K→100K, map-size limits) is a **separate downstream blueprint**, run only after this
one confirms the model behaves. Do not attempt 100K agents or map-size sweeps here.

**Substrate note:** the live tree (`origin/main 1447c75`) has `TerrainWorld`,
`TerrainField`, `WorldFields`, `generate_world`, `GAME_KCAL_TARGETS`/`FORAGE_KCAL_TARGETS`
+ `_STD`, lognormal resource draw. Bind to the **actual live signatures** — do not invent
parameter names. If a needed entry point (init-agent-count, seed string, placement hook)
does not exist or is not parameterisable, **STOP and report** rather than inferring.

---

## §0 Scope lock

- **Substrate:** 50×50 terrain (workbench size; smaller than the locked 100×100 science
  substrate, chosen for fast iteration and legible spatial output). Resource fields:
  `forage_kcal`, `game_kcal` lognormal(mean,std), all PROVISIONAL pending CC-1.
- **Civilisation:** **C only.** Si is not in the Phase 1 terrain path; do not exercise Si.
- **Horizon:** **1,500 steps** (1 step = 1 month → 125 model-years). Long enough that a
  clustered start fully migrates, sorts onto terrain, and settles, with margin so the
  post-equilibrium window is unambiguous.
- **No new science parameters.** This blueprint adds *diagnostics and an initial-placement
  routine*, not mechanics. The carrying capacity on terrain is **unknown and discovered by
  this run** — do NOT initialise at the stale Phase-0 N_carry=400 (that was a Sugarscape/50²
  value, not a terrain value).

---

## §1 Initial-placement routine (founder clusters, biome-blind)

Build a deterministic placement function: given `(n_clusters, patch_size, total_N, seed)`,
place `total_N` C agents into `n_clusters` founder groups.

1. **Seed points on an even spatial lattice** across the 50×50 grid (e.g. for 4 clusters a
   2×2 lattice of cell-centres, for 6 a 2×3, for 8 a 2×4), inset from edges. Seed points are
   chosen **blind to biome quality** — accept whatever terrain each lands on. If a lattice
   point lands on water/impassable, displace to the nearest land cell deterministically
   (fixed rule, seed-reproducible) and log the displacement.
2. **Patch:** distribute each cluster's agents over the `patch_size × patch_size` block
   centred on its seed point (3×3 = 9 cells, 5×5 = 25 cells), as evenly as possible. Avoid
   stacking all of a cluster on one cell at t=0.
3. **Fixed total N across all combos:** N=1,000 always. 4 clusters → 250 each; 6 → ~167;
   8 → 125. Vary *placement*, never *population* — varying both would confound the two.
4. Deterministic: same `(n_clusters, patch_size, N, seed)` → byte-identical initial agent
   set. Verify under the existing determinism gate.

**Acceptance §1 (assertable):** placement is deterministic (repeat → identical); total agents
placed = 1,000 for every combo; no cluster stacked entirely on a single cell; water-landing
seed points displaced-and-logged, not silently dropped.

---

## §2 The placement sweep (the experiment)

Run the **6-combo factorial**, fixed N=1,000, on the **same 3 seeds** (3 terrain worlds):

| Combo | clusters | patch | agents/cluster |
|---|---|---|---|
| 1 | 4 | 3×3 | 250 |
| 2 | 4 | 5×5 | 250 |
| 3 | 6 | 3×3 | ~167 |
| 4 | 6 | 5×5 | ~167 |
| 5 | 8 | 3×3 | 125 |
| 6 | 8 | 5×5 | 125 |

3 seeds × 6 combos = **18 runs**, 1,500 steps each, 50×50. Same seed = same terrain across
combos, so placement effects are isolated from world effects.

**The sweep's purpose is a convergence-vs-divergence read** (must-be-seen, §5): does
equilibrium population + settlement structure converge regardless of placement (→ the model
has its own terrain-driven attractor, reassuring), or does initial placement leave a lasting
fingerprint at t=1,500 (→ path-dependence, a yellow flag)? Do **not** pre-commit a
convergence threshold — report the spread and let the supervisor read it.

---

## §3 Correctness + dynamics guards (assertable rails — bug catching)

These are the bug-catching rails. A rail failure is a **STOP-and-report** (CLAUDE.md Rule
11/13) — it means the infrastructure is broken, not that the science is interesting.

Per run, assert:
1. **Determinism:** same `(knobs, seed, placement)` → byte-identical trajectory. (Rule 2.)
2. **No NaN/Inf** in agent reserves, kcal intake, or any resource field at any step.
3. **Population never hits 0** before step 1,500 (total extinction = a breakage signal at
   this stage, flag hard).
4. **No negative harvest / no negative reserve** that isn't an intended dormancy/deficit path.
5. **No agents on impassable cells** (water/illegal terrain) post-migration.
6. **Conservation sanity:** harvested kcal ≤ available field kcal per cell per step
   (non-rivalrous read is allowed per CC-1 seam, but flag if intake is physically impossible).

**CC authority (per supervisor):** CC **fixes outright bugs freely** (e.g. a negative-harvest
clamp, an off-by-one in placement, an NaN guard) and reports the fix. CC **does NOT
self-adjust any science parameter** to make dynamics look better — any dynamics/tuning
concern (population oscillation, implausible equilibrium, biome avoidance) is **flagged for
the supervisor**, not silently tuned. Bug vs. tuning ambiguous → treat as tuning → flag.

---

## §4 Diagnostics

### 4.1 Temporal (Phase-0 carry-overs, per run; the settling curve is the headline)
- **Population over time** — *the* primary plot. Where it flattens = discovered terrain
  carrying capacity. CC marks the approximate equilibrium-onset step from this curve (used
  by §4.3).
- Mean agent **reserve (kcal)** over time — economy stable vs. starving.
- **Births and deaths per step** — turnover sane vs. thrashing.
- Mean agent **age** over time — age structure plausible vs. collapsing.

### 4.2 Spatial density (per run, light version)
- **Population-density heatmap over the 50×50 grid, paired with the biome map**, at
  **t=0, t=mid, t=final**. Shows founder clusters radiating/migrating/dying and whether
  agents sort onto high-kcal terrain. Visual, no threshold.

### 4.3 Settlement structure (per-cell mean population — the persistence diagnostic)
- For each cell, compute **mean agent occupancy over the post-equilibrium window**
  (equilibrium-onset step from §4.1 → t=1,500). Averaging over time *is* the
  persistent-vs-transient filter by construction: a briefly-mobbed cell has near-zero mean;
  a durably-held cell has high mean. **Do not** average over the whole run (the settling
  transient would smear founder positions into the mean).
- Render as **(a) a map** (per-cell mean occupancy, biome-overlaid — where durable
  concentrations sit) and **(b) a histogram** (distribution of per-cell mean occupancy across
  occupied cells).
- **The histogram shape is the finding.** A long right tail / bimodality = durable
  settlements emerge (a few cells hold high mean occupancy); a smooth unimodal spread = no
  settlement structure. **The break in the histogram, if any, defines the settlement
  threshold — read off the data, not pre-baked.** No-gap is a legitimate finding ("no
  settlement structure at this stage"). Do NOT hardcode a "hot-cell" cutoff into a verdict.

---

## §5 Must-be-seen report (the deliverable)

This blueprint produces a **report** — its core outputs are shapes that cannot be reduced to
a green line. Structure it tightly:

1. **Settling-population curves** — all 18 runs (small-multiple by combo, coloured by seed).
   Where does population equilibrate? Is the discovered terrain carrying capacity on 50×50
   roughly consistent across combos/seeds? **This supersedes the stale N_carry=400 as the
   terrain-substrate carrying anchor** (flag for the supervisor; do not lock it into a home
   here — propose it).
2. **Convergence-vs-divergence read** — does equilibrium population + settlement structure
   converge across the placement sweep, or does placement leave a t=1,500 fingerprint?
   Report the spread; supervisor interprets.
3. **Per-cell mean-occupancy histogram + map** — per combo (or a representative subset if 18
   is too many to show; pick the clearest contrast). Does durable settlement structure
   emerge? Where (which biomes)?
4. **Spatial density snapshots** — t=0/mid/final for ≥1 representative run, biome-overlaid.
5. **Dynamics sanity** — reserves/births/deaths/age curves; explicitly state whether
   anything looks implausible (and is therefore flagged for tuning, not auto-fixed).
6. **Guards** — one-line green per §3 rail, OR the STOP if any failed.
7. **Bugs fixed** — list every bug CC fixed (with what + why), separate from tuning flags.
8. **Tuning flags** — anything CC thinks needs a science adjustment, left for the supervisor.

### Assertable block (green = these passed; they are guards, not the finding)
- §1 placement determinism + count + no-single-cell-stack + water-displacement-logged
- §3 rails 1–6 (determinism, no NaN, no extinction, no illegal harvest/reserve, no agents on
  impassable cells, conservation sanity)
- Full existing pytest suite green after any bug-fix (Rule 3)

---

## §6 Doc-update (definition-of-done)

- Register the run in **ARTIFACTS.md** (location + headline: discovered 50×50 terrain
  carrying capacity, convergence read, settlement-structure verdict).
- **Propose** (do not lock) the discovered terrain carrying capacity as the candidate
  N_carry anchor for the 50×50 substrate, flagged for supervisor + as a recal-time input —
  the stale 400 is a Sugarscape value. Home: PARAMETERS §7 (proposed entry) / ROADMAP.
- If any bug-fix changed behaviour, note it in ARCH §12 decision-log with old→new.
- Drain nothing new unless a buffer item is touched; if PARAMETERS/ROADMAP changed,
  regenerate CANONICAL_FACTS per Rule 15 and prompt re-upload.
- This run does **not** touch H1(ii), does not run Si, does not lock any science value.

---

## §7 Stopping rules

- Any §3 rail fails → **STOP, report** (broken infrastructure, supervisor's call).
- A needed entry point (init-count, seed, placement hook) missing/non-parameterisable →
  **STOP, report** (do not infer signatures).
- Dynamics look implausible but rails pass → **complete the run, flag for tuning** (do not
  STOP, do not auto-tune a science parameter).
- Do **not** proceed to 100×100, 10K+ agents, or map-size sweeps — that is the separate
  downstream scaling blueprint.
- Failed acceptance in the assertable block = blocking STOP (Rule 11).
