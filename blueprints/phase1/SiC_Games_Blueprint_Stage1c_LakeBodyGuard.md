# SiC Games — Stage 1c Blueprint: Largest-Lake-Body Guard

**Status:** READY FOR CC
**Depends on:** Stage 1b (water decomposition) COMPLETE
**Supersedes:** the `exterior_water_fraction > 0.12` world-acceptance guard (to be retired by this stage)

---

## 0. Context (read before starting)

The current world-acceptance guard rejects worlds on `exterior_water_fraction > 0.12`. M1 data
showed this guard is mis-specified: it is an **area** measure firing on an **edge-connectivity**
event (interior lakes merging to the map boundary), so it both over-rejects valid large-lake
continental worlds and bisects a continuous distribution at a seed-fragile point. It cannot be
locked. See §DECISION-LAKE-BODY-GUARD below for the replacement rationale.

The replacement cuts on **largest single connected water body as a fraction of map area**. A body
too large to walk around is functionally an inland sea (Superior/Caspian-class) and produces
coastal dynamics this arc does not yet implement — so it is rejected and **deferred** to the future
coastal/archipelago generators, NOT excluded from the science. Many small-to-medium lakes
(land-of-lakes / Minnesota / Finland morphology) are explicitly **wanted** and must be retained.

**World dimensions (VERIFY against authoritative config — do not trust this prose):**
expected 1 cell = 100 km² (10 km × 10 km), map 100×100 cells = 1,000,000 km². The single-body
ceiling rationale depends on this. If config disagrees, STOP and report the discrepancy before
proceeding — the ceiling anchor is invalid under different dimensions.

---

## 1. First task — resolve the discovery question

Determine whether `characterize_map()` already computes a **largest connected water body** size
statistic (connected-component sizing over the water mask, not `exterior_water_fraction` /
`interior_water_fraction`, which are area-by-connectivity-class and do NOT answer this).

Branch:

- **1A — statistic does NOT exist (expected):** proceed to §2 (add diagnostics) then §3+.
- **1B — statistic DOES exist:** skip §2; verify it is a true largest-connected-component fraction
  (single body, not summed bodies), then proceed to §3+. Report in the must-be-seen block that the
  statistic pre-existed and what its exact definition was.

Report which branch was taken in one line at the top of the run output.

---

## 2. Add diagnostics to `characterize_map()` (branch 1A only)

Compute over the **water mask** using connected-component labelling (4-connectivity for water
bodies — match whatever connectivity Stage 1b's exterior/interior decomposition already uses;
report which, and use it consistently). Add the following fields to the returned characterization
vector:

| Field | Definition |
|---|---|
| `largest_water_body_fraction` | size of the single largest connected water component / total map cells |
| `water_body_count` | number of distinct connected water components |
| `characteristic_water_body_size` | **median** component size (cells), over all water components |
| `characteristic_interlake_patch_size` | **median** connected-land-component size (cells), land mask, same connectivity convention applied to land |

Notes:
- `largest_water_body_fraction` is the **guard statistic**. The other three are descriptors that
  let a land-of-lakes world be *recognised* (many bodies, modest median body size, substantial
  interlake land) rather than mistaken for a drowned map.
- Use median, not mean, for the characteristic sizes — body-size distributions are heavy-tailed and
  the mean is dominated by the largest body, which is exactly what these descriptors must NOT track.
- Do not remove or alter `exterior_water_fraction` / `interior_water_fraction` — they stay as
  reported diagnostics. Only their **use as the acceptance guard** is retired (§4).

---

## 3. Re-run the M1 waterK sweep with the new diagnostics

Re-run the existing M1 waterK sweep (same seeds: 42, 7, 1001, 13, 99; same waterK grid, at least
0.40–0.85 inclusive at the existing step) emitting the four new fields per seed per waterK, in
addition to the existing exterior/interior fractions.

Output: a CSV in `outputs/stage1c_seed[N]/` (or the established sweep-output pattern) with
per-seed and mean columns for `largest_water_body_fraction`, `water_body_count`,
`characteristic_water_body_size`, `characteristic_interlake_patch_size`.

---

## 4. Swap the guard

Replace the world-acceptance guard:

- **Remove:** rejection on `exterior_water_fraction > 0.12`.
- **Add:** rejection on `largest_water_body_fraction > LARGE_BODY_CEILING`.
- `LARGE_BODY_CEILING` is a **named config parameter**, sourced from authoritative config, NOT a
  literal in code. Provisional value **0.10** (rationale in §DECISION below). It is a logged scope
  decision, **not** a discovered/locked acceptance threshold — see §6.

Do **not** add an aggregate-water ceiling as a hard guard. Aggregate water is reported (via the
descriptors) but a land-of-lakes world may legitimately run high aggregate water; gating on it
would reject the morphology we want to keep.

---

## 5. Acceptance block (verdict-by-assertion — all must pass)

1. World dimensions verified against authoritative config (1 cell = 100 km², 100×100 map) — or
   discrepancy reported and run halted.
2. Discovery branch (1A/1B) resolved and reported in one line.
3. `largest_water_body_fraction` is a single-largest-connected-component fraction (assert: equals
   max component size / total cells on a constructed test map with ≥3 disjoint water bodies of
   known sizes; assert it does NOT equal the sum).
4. Connected-component labelling correctness: on a synthetic map with known component count and
   sizes (e.g. 3 disjoint blobs + 1 diagonal-touching pair under 4-connectivity), `water_body_count`
   and component sizes match hand-computed truth.
5. Characteristic sizes use median (assert against a synthetic heavy-tailed body-size set where
   median ≠ mean).
6. Guard swap complete: `exterior_water_fraction > 0.12` no longer gates world acceptance anywhere;
   `largest_water_body_fraction > LARGE_BODY_CEILING` is the sole large-water acceptance guard;
   `LARGE_BODY_CEILING` read from config, not hardcoded.
7. All pre-existing Stage 1b tests still pass (exterior/interior fractions unchanged).
8. M1 sweep CSV (§3) produced with all four new fields, per-seed and mean, across the full waterK grid.

A green acceptance block closes the build. The **ceiling value itself is not asserted** (it is a
judgment call against the seen distribution — see §6); CC runs straight through.

---

## 6. Must-be-seen artifacts (carry to report; the rest is a one-line green)

1. **`largest_water_body_fraction` across the waterK sweep** — per-seed and mean. This is the curve
   the supervisor cuts the ceiling against. Its shape (continuous ramp vs. gap, seed spread, where
   it crosses candidate ceilings 0.08 / 0.10 / 0.12) cannot be reduced to a threshold and must be seen.
2. **The three land-of-lakes descriptors at the high-waterK end** (`water_body_count`,
   `characteristic_water_body_size`, `characteristic_interlake_patch_size`) — so the supervisor can
   confirm that worlds near/above the candidate ceiling are inland-sea worlds (one dominant body,
   low count) and NOT land-of-lakes worlds (many bodies, substantial interlake land). If a
   land-of-lakes world sits above the ceiling, that is a finding: the single-body cap alone may be
   mis-rejecting and the descriptors must inform a revised cut.

CC does **not** lock the ceiling. CC reports these two artifacts and stops; the ceiling is a
supervisor decision against the seen curve.

---

## §DECISION-LAKE-BODY-GUARD (log to ROADMAP / decisions register)

The continental arc retains worlds with many lakes, including large ones, including land-of-lakes
morphology. It rejects worlds containing a **single water body large enough to behave as an inland
sea** — provisionally `largest_water_body_fraction > 0.10` (≈100,000 km² at current dimensions,
larger than Lake Superior, unambiguously inland-sea class). Rationale: such a body is too large to
be walked around and produces coastal dynamics (fetch, boat-crossing, network fragmentation) that
this arc does not implement; until that dynamics layer exists, the body is dead area that wastes
the map. This is **deferral, not exclusion** — large-water geography and its dynamics are committed
to the future coastal/archipelago generators (§STAGE-GEOSTRUCT), where a large body will have
coastal dynamics toggled on. The ceiling is a logged scope choice anchored on real largest-lake
ratios, NOT a discovered acceptance threshold; it does not enter an acceptance gate as a
pre-committed value.

**Known scope gap (population-ecology lens, on record):** rejecting large-single-body worlds removes
large-water-barrier geography from the C-vs-Si comparison in this arc. If a large interior barrier
would differentiate cooperative (C) network fragmentation from self-reliant (Si) constraint, those
worlds are deferred, not tested here. Logged as a deliberate gap, to be closed by §STAGE-GEOSTRUCT.

## Forward note (log against the stochastic-shock stage; do NOT build now)

Flood dynamics are distinct from lakes and must not be modelled as large-lake instances. A flooded
cell is a **transient wetland/swamp state**: non-traversable on foot, non-navigable by boat,
functionally edge/shore (fishing, riparian resource) rather than open water, and temporary. A flood
event does not create one large lake and must not trip the single-body guard. This is a terrain
*state*, to be specified in the seasonal/catastrophe shock stage with its own hypothesis and gate.
