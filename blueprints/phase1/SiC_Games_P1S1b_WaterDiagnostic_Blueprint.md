# SiC Games — Phase 1 Stage 1b: Water Decomposition Diagnostic

**Type:** Diagnostic + validity guard + characterisation sweep. Measurement only — **no generator change.**
**Depends on:** Phase 1 Stage 1 (forage field + terrain diagnostics), COMPLETE/GREEN.
**Hands to:** Claude Code (CC). Run straight through to completion. The only blocking mid-run stop is a
failed acceptance check (CLAUDE.md failed-gate STOP).

---

## 1. Why this stage exists

The Stage 1 open verify (mountain-fraction denominator) resolved as follows: `mountain_fraction` uses a
**land-cell** denominator (`terrain.py:491–492`, `counts[BIOME_MOUNTAIN] / land`). This is correct and is
**not** changed by this stage. However, resolving it surfaced the real problem: the `mtn_ceiling = 0.317`
figure in pre-registered finding **§H-TERRAIN-ASYMMETRY** was characterised at `waterK = 0.99`, a
near-fully-flooded world. At that setting both numerator and denominator of `mountain_fraction` are
distorted (most land is flooded away → tiny denominator of residual high peaks → inflated ratio). The
ceiling is therefore a *conditional* figure measured on a sliver of residual land, not the *structural*
limit the finding claims. **This blueprint does NOT correct §H-TERRAIN-ASYMMETRY** (supervisor decision,
pending). It builds the measurement layer that makes a correct re-derivation possible in a later stage.

The deeper issue: the generator collapses all water into one `waterK` knob and `characterize_map()`
measures water as one undifferentiated quantity. Water plays two distinct roles for a non-seafaring
civilisation:

- **Interior water (lakes):** fully enclosed by land. Habitability-positive — adds shoreline (shore-forage
  modifier), fragments land into mosaic, wastes no map. A lake-dense world is a fully valid testbed.
- **Exterior water (ocean/sea):** edge-connected. For a non-seafaring civ this is dead, inaccessible map.
  A mostly-ocean world is not a testbed — it is absence of world.

The current diagnostic cannot tell these apart. This stage adds that decomposition.

---

## 2. Locked design decisions (pre-registered, do not relitigate in code)

| Item | Decision |
|---|---|
| Lake vs ocean definition | **Connectivity-to-edge.** A water connected-component is *exterior* if it touches the map boundary, *interior* (lake) otherwise. 4-connectivity for component labelling. |
| Exterior water fraction | **Validity guard** — maps above threshold are discarded as "not a testbed" (same class as the existing no-biome-≥95% guard). NOT a coordinate. |
| Interior water fraction | **Coordinate** — kept, recorded, studied (like desert% / mtn%). |
| Shoreline length | **Coordinate.** |
| Shoreline-to-area ratio of largest exterior body | **Coordinate** — measured specifically to test whether coastal worlds and ocean-blob worlds separate (see §6). |
| Provisional guard threshold | **exterior_water_fraction ≤ 0.12**, provisional. Derived from thin-rim island edge case (see §3). Flagged for confirmation against the sweep distribution — do NOT treat as final. |
| Coast-vs-ocean shape-aware guard | **Deferred.** Decided after the sweep shows whether coast and ocean separate on shoreline-to-area ratio. Not built here. |
| Rivers | **§DECISION-NO-RIVERS** — not implemented as a distinct feature or mechanic. Channel-like fragments from flow accumulation are left as-is, classified as interior or exterior water by the connectivity rule like any other water. Riparian productivity is preserved via the existing shore-forage modifier on water-edge land cells. Do NOT add river tracing, river labelling, or any crossing/traversal logic. |

### §DECISION-NO-RIVERS (log to the appropriate design-decision document)
> Rivers are not implemented as a distinct terrain feature or mechanic. A river's only model-relevant
> function over generic interior water is as a movement barrier or corridor; no movement/traversal mechanic
> exists or is planned in the current arc. Absent that, a river is mechanically identical to narrow interior
> water and is fully captured by the connectivity-to-edge water diagnostic plus the existing shore-forage
> modifier. Riparian productivity is preserved via shore forage on water-edge cells. Revisit only when a
> movement/traversal stage is designed, at which point channels are traced against that model's actual
> requirements.

---

## 3. Provisional threshold derivation (record in the diagnostic's docstring/comment)

The provisional guard threshold is derived from the maximally-admissible edge case: a whole-map island with
the thinnest naturalistic ocean rim. For an N×N grid with a perimeter rim of thickness `t`, rim area =
`N² − (N−2t)²`. For N=100:

| rim thickness t | rim cells | exterior fraction |
|---|---|---|
| 1 | 396 | 0.040 |
| 2 | 784 | 0.078 |
| 3 | 1164 | 0.116 |

A 2–3 cell rim (natural roughness allowed) gives ~0.08–0.12. **Provisional threshold = 0.12** (t=3 bound).
Anything above wastes interior area on open sea beyond what a thin-rim island requires. This is provisional
pending the sweep — the coastal-heavy case (long contiguous sea on one/two edges) may exceed it, which is
exactly what the shoreline-to-area measurement in §6 exists to detect.

---

## 4. What to build

All additions go in `characterize_map()` in `sic_games/src/sic_games/terrain.py`. Reuse the existing
water mask (`isWater`) and the existing `land` count. Do not recompute water.

### Task 4.1 — Connected-component labelling of water
Label water cells into connected components (4-connectivity). For each component record its cell set and
whether any cell lies on the map boundary (row 0, row N−1, col 0, or col N−1).

### Task 4.2 — Exterior / interior classification
- A component is **exterior** if it touches the boundary; **interior** otherwise.
- `exterior_water_cells` = sum of cells in all exterior components.
- `interior_water_cells` = sum of cells in all interior components.
- Sanity: `exterior_water_cells + interior_water_cells == total water cells`.

### Task 4.3 — New fields on the returned vector
| Field | Definition | Denominator |
|---|---|---|
| `exterior_water_fraction` | exterior_water_cells / (N*N) | total cells |
| `interior_water_fraction` | interior_water_cells / (N*N) | total cells |
| `n_interior_bodies` | count of interior (lake) components | — |
| `n_exterior_bodies` | count of exterior components | — |
| `shoreline_fraction` | (land cells adjacent — 4-neighbour — to any water) / land | land cells |
| `largest_exterior_body_cells` | cell count of the largest exterior component (0 if none) | — |
| `largest_exterior_shore_to_area` | (land cells adjacent to the largest exterior body) / (cells in that body); 0 if no exterior body | ratio |

**Denominator convention note (record in comment):** water-extent fields (`exterior_water_fraction`,
`interior_water_fraction`) use **total cells**, consistent with the existing `shore_cell_fraction`,
`largest_body_fraction`, `habitable_cell_fraction`, and `waterPct` fields. `shoreline_fraction` uses
**land cells**, consistent with the existing per-biome fractions and mean fields. This matches the
already-mixed-but-internally-consistent convention in `characterize_map()` — do NOT change any existing
field's denominator.

### Task 4.4 — Exterior-water validity guard
Add a guard alongside the existing validity guards (≥FLOOR habitable cells; no biome ≥95%):
- `guard_exterior_water_fail = exterior_water_fraction > EXTERIOR_WATER_CEILING`
- `EXTERIOR_WATER_CEILING = 0.12` (provisional; named constant, single definition site, commented as
  provisional-pending-sweep with the §3 derivation).
- A map failing this guard is **invalid** (discarded from the admissible set), reported as such — same
  treatment as the existing guards. It is NOT silently dropped: invalid maps are counted and their
  exterior fraction recorded so the sweep can show how much of knob-space the guard removes.

---

## 5. Characterisation sweep

Extend the inline sweep in `outputs/phase1_stage1/acceptance_and_artifacts.py` (or a sibling
`outputs/phase1_stage1b/` script — CC's call, keep outputs under the stage-label pattern
`outputs/phase1_stage1b_seed[N]/`).

- Sweep `waterK` across its **full** range `[0, 1]` (do NOT restrict — the point is to see the whole
  reachable water-space, including where exterior fraction degenerates). Hold other knobs at their
  established sweep defaults; use the existing multi-seed protocol.
- For each map record: `waterK`, seed, `exterior_water_fraction`, `interior_water_fraction`,
  `shoreline_fraction`, `largest_exterior_shore_to_area`, `n_interior_bodies`, `n_exterior_bodies`, and
  whether each validity guard fired.
- Emit the raw per-map records (CSV/JSON) AND the must-be-seen plots in §7.

---

## 6. What the sweep is for (do not pre-threshold these)

Two questions the sweep must let the supervisor *see* — neither is asserted against a threshold here, because
inventing one now would be HARKing the very distributions being examined:

1. **Where does the provisional 0.12 ceiling actually fall** relative to the produced
   `exterior_water_fraction` distribution? Is there a natural gap (threshold places itself) or a continuum
   (threshold is a judgment call against seen maps)?
2. **Do coastal worlds and ocean-blob worlds separate on `largest_exterior_shore_to_area`?** A long thin
   coastal sea has high shoreline-to-area (much usable edge per unit sea); a fat wasted ocean blob has low
   shoreline-to-area. If they separate cleanly, a future shape-aware guard is justified and admits coast
   while rejecting blob. If they do not separate, the simple raw-fraction guard stands and the coastal-heavy
   subdivision is dropped for this arc. **This decision is deferred to the supervisor, post-sweep.**

---

## 7. Must-be-seen artifacts (the only outputs that survive into a report)

Shape-dependent, cannot be reduced to a threshold:

1. **Exterior / interior / shoreline vs `waterK`** — three series over the full `waterK` range (multi-seed,
   show spread). The distribution that places the threshold.
2. **`largest_exterior_shore_to_area` vs `exterior_water_fraction`** — scatter, points coloured/marked by
   whether they pass the provisional guard. This is the coast-vs-ocean separation plot; its shape decides
   §6 question 2.

A one-paragraph prose note may accompany these stating what is seen (gap vs continuum; separation vs none).
No other prose report.

---

## 8. Acceptance block (must all pass — green block is the finding)

Mechanical correctness only. All assertable:

1. **Field computation** — all §4.3 fields present on the returned vector, correct types, in valid ranges
   (fractions ∈ [0,1]; ratios ≥ 0; counts ≥ 0).
2. **Conservation** — `exterior_water_cells + interior_water_cells == total water cells` on every test map.
3. **Connectivity classification** — on a hand-built fixture map with one known enclosed lake and one known
   edge-connected sea: the lake is classified interior, the sea exterior, counts exact.
4. **Guard behaviour on fixtures** — `guard_exterior_water_fail` is `True` on a known mostly-ocean fixture
   (exterior fraction > 0.12) and `False` on a known thin-rim-island fixture (exterior fraction < 0.12) and
   on a known lake-dense fixture (high interior, low exterior).
5. **No regression** — all 370 existing tests still pass; no existing field's value or denominator changes.
6. **Constant single-sourced** — `EXTERIOR_WATER_CEILING` defined once, referenced everywhere, commented
   provisional with §3 derivation.

---

## 9. Stopping rule

Run straight through. Block only on a failed acceptance check (§8) — that is a CLAUDE.md failed-gate STOP,
not a judgment call. Do NOT touch §H-TERRAIN-ASYMMETRY, the `mtn_ceiling` figure, or any logged finding —
re-deriving the ceiling against the new diagnostic is a *separate* future stage and a supervisor decision.
Do NOT change the generator. Do NOT implement rivers or any movement/crossing logic. Do NOT build the
shape-aware guard.

## 10. Report

If §8 is fully green: emit the two must-be-seen plots (§7) + the one-paragraph note. Nothing else.
If any §8 check fails: STOP and report the failing check.

## 11. Definition of done

- §4 fields implemented in `characterize_map()`, exterior-water guard wired alongside existing guards.
- §8 acceptance block fully green (incl. 370 existing tests).
- §7 must-be-seen artifacts emitted under `outputs/phase1_stage1b_seed[N]/`.
- §DECISION-NO-RIVERS logged to the design-decision document.
- Provisional `EXTERIOR_WATER_CEILING = 0.12` recorded as provisional-pending-sweep.
- Supervisor's post-sweep decisions (final threshold; whether to build shape-aware guard) are explicitly
  left open — not closed by CC.
