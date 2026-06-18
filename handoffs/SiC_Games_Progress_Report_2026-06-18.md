# SiC Games — Progress Report (2026-06-18)

**Scope.** Bridges from the last standing handoff (2026-06-14, Blueprint A) and the A-3
First-Light Shakedown to the present. Covers what was built, what A-3 found (including the
finding that motivates the next stage), what was tried and failed, and the design decisions
reached for the demographic stage. Companion document: the demographic-stage blueprint
`blueprints/phase1/SiC_Games_P1_Demography_Siler_Blueprint.md`.

**Status in one line.** The C agent layer runs on Phase-1 terrain and discovers a clean,
placement-independent carrying capacity — but at equilibrium the population is demographically
**frozen** (zero births, zero deaths), because the model has no continuous mortality. That gap
is the subject of the next stage.

---

## 1. What was built since Blueprint A

All changes are opt-in seams; the default Blueprint-A path is byte-unchanged (431 pytest pass).

| Addition | Where | What it does |
|---|---|---|
| **Multi-occupancy substrate (Stage 6.0a)** | `src/sic_games/substrate.py` | A cell's total return rate `S` is split among its occupants (`compute_harvest_shares`); `diffusion_select_target` moves agents by per-capita yield. κ=0 → even split ("Cred=1 for all"); affinity/crowd hooks held neutral. |
| **Rivalrous path wiring** | `phase1_model.py:_step_rivalrous` | When a `SubstrateConfig` is supplied, the model adopts the 6.0a substrate over the terrain field. |
| **CC-1 cell-capacity field (PROVISIONAL)** | `outputs/phase1_a3_firstlight/run_a3.py:CapacityField` + `harvest_field` param in `phase1_model.py` | A swap-in harvest field whose per-cell level is the cell's **total** sustainable yield `E = K·burn`, with `K = density(NPP)·100 km²` and density anchored to Tallavaara 2018 (`min(0.5, 0.3·npp_gm2/1360)`). Fixes the root bug below. |
| **Opt-in reproduction (MR, shakedown)** | `phase1_model.py:_do_births` | Asexual, reserve-gated budding so the population can settle: eligible = alive, age ≥ `repro_min_age`, reserve ≥ `birth_threshold`, prob `p_birth`. All params PROVISIONAL. |
| **Water guard** | `phase1_model.py:_step_rivalrous` | The shared diffusion rule is water-blind; a guard vetoes any step onto a water cell. No science parameter touched. |
| **Harness robustness** | `run_a3.py` | `progress.txt` (live ETA), `partial_finals.json` (crash-safe per-run save), `gc.collect()` between runs. |

---

## 2. A-3 First-Light Shakedown — results

**Configuration.** 100×100 terrain, C-only, rivalrous multi-occupancy on the CC-1 capacity
field, opt-in reproduction. Founders = 1000, placed in deterministic clusters. 1 step = 1 month.
Burn = 75,000 kcal/step; reserve_full = 100k (≈40 days fat), reserve_floor = 20k; lifespan = 900
months. Not a gate — findings are shapes; rails are bug-catchers.

**Habitability check (per-cell capacity K, mean over 3 seed worlds).** Every habitable biome
supports a real band:

| Biome | foragers/cell (K) |
|---|---|
| Wetland | 36.3 |
| Forest | 25.6 |
| Savanna | 13.4 |
| Grass | 8.0 |
| Desert | 5.9 |
| Mountain | 0.7 |

Total terrain capacity ≈ **138,021** over 1,000,000 km² (≈0.14/km² — ethnographically realistic).
Land cells with K≥1: **99.9%** (only the lone barren-mountain cell falls below one person).

**Discovered carrying capacity.** Two placement runs of the reduced sweep completed before it was
stopped:

| Run | final population (last-500 mean) |
|---|---|
| 4 clusters / 3×3 patch, seed 42 | 133,334 |
| 4 clusters / 5×5 patch, seed 42 | 133,408 |

→ **~133,400, spread ≈ 0.06%** across two different placements. The equilibrium is a strong,
**placement-independent, terrain-driven attractor** (≈97% of the 138k food ceiling). Settling
onset ≈ step 173 (fast). Determinism PASS; rails clean (no NaN/Inf, no sub-floor reserve, no
agents on water, no early extinction).

> **NOTE — this number is provisional and will be superseded.** Under real demographics
> (next stage) equilibrium is set by birth–death balance, not the food ceiling, and will likely
> land **below** 133k. Treat 133.4k as the *food-capacity ceiling*, not the demographic carrying
> capacity. Supersedes the stale `N_carry=400` (a Sugarscape/50² value).

---

## 3. The key finding — frozen equilibrium (the reason for the next stage)

In the dynamics, **deaths occur only during the crowded founding transient, then drop to zero
once agents spread.** Diagnosis (the model has exactly two death causes,
`phase1_model.py:286–291`):

1. **Starvation** (`wealth ≤ reserve_floor`) is **density-dependent** — it only bites when agents
   stack and split a cell's yield below maintenance. Once they diffuse to carrying capacity,
   per-capita intake ≈ burn, reserves flatline, starvation stops *by construction*.
2. **Senescence** is a **hard age cap** at 900 months. It never fires in short runs, and even in
   long runs it fires as one **synchronized wave** (all founders start at the same age).

At equilibrium intake is pinned to maintenance → no starvation; nobody is old enough → no
senescence; and because `birth_threshold (22k)` sits just above `reserve_floor (20k)`, reserves
pin below it → **births also stop.** Result: a demographically frozen population. Real foraging
populations show continuous turnover (births balanced by density-independent mortality). **The
model lacks baseline mortality.** This is exactly the kind of shape A-3 was built to surface.

---

## 4. Bugs found & fixed during A-3

| Bug | Symptom | Fix |
|---|---|---|
| **Per-forager rate used as whole-cell food** | A 100 km² cell held only ~6 people; savanna held 0 → founders collapsed | CC-1 cell capacity: cell yields `E = K·burn`, K from NPP density (Tallavaara) |
| **Assumed one-agent-per-cell** | — | Confirmed multi-occupancy is intended; cell holds a band |
| **Water-blind diffusion movement** | agents could step onto water | water guard in `_step_rivalrous` |
| **Memory-creep OOM** | the 18-run monolith was killed at ~2h13m with no output; reduced run hit 2.8 GB | crash-safe incremental saves + `gc` + reduced 6-run sweep; demographic calibration to move off-terrain (see blueprint) |

**Process lessons (now standing practice):** (a) long runs must emit a live progress indicator
(`progress.txt`) — Python block-buffers stdout when piped, and a `| grep` pipe re-buffers even
under `python -u`; (b) save per-iteration results incrementally so a crash costs one run, not all;
(c) a single multi-hour monolithic run is fragile — prefer many short, recoverable units.

---

## 5. Decisions reached for the demographic stage

Full spec in the blueprint; summary of what the supervisor approved in this session:

1. **Full Siler 3-term mortality** (infant + baseline + Gompertz senescence), sex-specific,
   Aché-anchored — replaces the hard age cap *and* supplies the missing baseline.
2. **Disease via two channels, both behind decouple flags:** density-dependent transmission
   (within-cell crowding) and a terrain pathogen field. **Pathogen ships off-by-default until a
   disease-ecology literature anchor is found** (open action).
3. **Nutrition × disease synergy: in, flagged** — undernutrition scales the baseline hazard up;
   to be run coupled vs decoupled to isolate the effect.
4. **Reproduction reframed to female-only + inter-birth-interval (IBI) refractory** within a
   fertile window, with reserve as a modifier (not the gate); SRB = 0.512 male (anchored);
   maternal mortality on each birth. **Infanticide = optional flagged mechanic** (sex-biased
   variant available), off by default.
5. **Staggered founder ages** drawn from the Siler-implied stable age distribution (starts the
   population near-stationary, avoids waiting generations).
6. **Two-step staging:** (1) calibrate pure demography in a fast non-spatial harness against the
   Aché life table; (2) lock it, then layer terrain modulators on the full 100×100 world. This
   also de-risks the scale/runtime problem.
7. **Validation gate = reproduce the Aché**: e₀≈35, e₁₅≈70, modal adult death ≈70–72, age
   pyramid, IBI/TFR in band, growth r≈0, and **births ≈ deaths > 0 at equilibrium** (the direct
   antidote to the frozen-equilibrium finding).

---

## 6. Current repo state

- **Committed:** CC-1 capacity model + water guard + harness (`f2df48c`).
- **Uncommitted / pending this session:** the reduced-sweep harness edits (1-seed, gc,
  incremental save, dynamic labels), this progress report, and the demographic blueprint.
- **A-3 outputs:** `sic_games/outputs/phase1_a3_firstlight/` — `partial_finals.json` (runs 1–2),
  `run_a3.py`. No final `report.html` for the real run (the sweep was stopped once the frozen
  finding + design decisions made the remaining runs moot; the keeper report is the demographic
  re-run). The `report.html`/`results.json` dated 19:04 are a 100-step **validation stub**, not
  the real sweep.

## 7. Open actions

1. **Disease-ecology literature search** (HG pathogen load vs environment) — gates the terrain
   pathogen formula; until then the pathogen flag stays off.
2. **Draft → independent red-team → lock** the demographic blueprint (review checkpoint built in).
3. Register the A-3 finding in `RESULTS.md` and `ARTIFACTS.md`; ROADMAP entry for the demographic
   stage.

---

*Progress Report · Phase 1 · 2026-06-18 · A-3 exploratory (not a gate); CC-1 capacity and all
reproduction/mortality values PROVISIONAL pending the demographic stage.*
