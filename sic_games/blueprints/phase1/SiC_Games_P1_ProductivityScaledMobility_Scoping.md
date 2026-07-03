# SiC Games — Phase 1 — Productivity-Scaled Mobility (biome-aware movement range)

**Status:** SCOPED + RED-TEAMED 2026-07-03. Mechanism build (default-OFF, ablatable); calibration PROVISIONAL pending supervisor sign-off.
**Anchors:** Kelly 1995/2013 *The Foraging Spectrum* (filed); Binford 2001 *Constructing Frames of Reference* (INLINE). LITERATURE §"the gathering… mobility anchors".
**Motivates:** R-37/R-39 — the biome→society collapse. The DEEPER root of the savanna collapse is that diffusion movement is **hard-coded r=1** (`substrate.py::diffusion_select_target`, `cands` = 4 cardinals at distance 1 + current). Real foragers spread over sparse territory by **ranging farther** where productivity is low (Kelly/Binford: mobility ∝ 1/productivity). Our low-NPP agents *cannot* spread → pile onto the few rich cells → overcrowd → starve.

---

## 1. The mechanism

**One knob changes: the STRIDE of the diffusion step scales inversely with local geographic productivity.**

`diffusion_select_target` builds a 5-candidate set (current + 4 cardinals at distance 1). We make the cardinal
distance a per-agent `move_radius r ≥ 1`, computed in the model from the agent's **static local NPP**
(`F.npp_gm2`, not the climate-modulated instantaneous level — avoids seasonal oscillation of the range):

```
r = clamp( round( base · (npp_ref / max(local_npp_gm2, npp_floor))**exponent ), base, r_max )
```

- **low NPP** (marginal savanna/desert) → large `r` → agents glide farther per step → spread out → lower per-cell
  density → the co-movement pile-up (R-39) dissipates.
- **high NPP** (forest) → `r → base` (=1) → the validated dense-forest dynamics are unchanged.
- `base=1, exponent=0` OR `enable_productivity_mobility=False` ⇒ **bit-exact** with today (r≡1).

**Scaling input = geographic (static) NPP**, so mobility is a property of *where you live*, not this month's weather.
(Seasonal transhumance — mobility tracking the climate trough — is a deliberate FUTURE extension, not this cut.)

## 2. Candidate generation (the "glide", water-aware)

For each cardinal direction, walk 1..r and take the **farthest reachable LAND cell** in that ray; **stop at the
first water cell** (foragers don't walk across a lake — the ray is blocked, not teleported over). If the immediate
neighbour (distance 1) is water, that direction yields no candidate. This requires the `isWater` mask inside the
mover (passed from the model, which already holds `self._fields.isWater`). The existing post-hoc water guard
(`phase1_model.py:531`) becomes redundant for the glide path but is kept as a belt-and-braces revert.

Utility per candidate is UNCHANGED (per-capita yield × grouping multipliers − move_cost). Only the candidate
*positions* change. `move_cost_flat` is still charged once per move regardless of stride (a longer move costs the
same flat friction — see red-team RT-4).

## 3. Config (demography/substrate cfg; all default → bit-exact)

| knob | default | meaning |
|---|---|---|
| `enable_productivity_mobility` | **False** | master flag |
| `mobility_base_radius` | **1** | `r` at/above `npp_ref` |
| `mobility_max_radius` | **6** | cap (bounds cost + jump-over risk) — PROVISIONAL |
| `mobility_npp_ref` | **900** g/m²/yr | forager-median NPP (Tallavaara); `r=base` at/above this — PROVISIONAL |
| `mobility_npp_floor` | **50** g/m²/yr | denom floor (hyper-arid cells don't → ∞ range) — PROVISIONAL |
| `mobility_exponent` | **1.0** | Kelly/Binford slope; 1.0 = strict ∝1/NPP — PROVISIONAL (bracket; supervisor to lock) |

## 4. Seams touched

- `substrate.py::diffusion_select_target` — add `move_radius:int=1`, `water:np.ndarray|None=None`; build cands via the glide. r=1/water=None ⇒ identical `cands` list ⇒ **bit-exact**.
- `phase1_model.py` (~530) — compute per-agent `mr` from `self._fields.npp_gm2` + cfg; pass `mr` + `self._fields.isWater`.
- `demography.py` — the 6 config fields + a `mobility_radius(local_npp, cfg)` pure helper (unit-testable).

## 5. Validation plan

1. **Unit** (`test_productivity_mobility.py`): `mobility_radius` monotone-decreasing in NPP, clamped [base,r_max]; low-NPP → r>1, high-NPP → r=1; glide stops at water; **flag-off / base=1 ⇒ bit-exact** target vs today (seeded).
2. **Behavioural**: re-run `biome_society_20260702` with the flag ON — does the savanna/desert co-movement pile-up dissipate (per-cell density ↓, eq_pop no longer → 5)? Expect marginal biomes to sustain a *mobile-egalitarian* society (Woodburn immediate-return) rather than collapse — the R-37 target.
3. **Regression**: full suite green; forest run unchanged (r≡1 there); E.3 status→RS preserved (mobility must not perturb the dense-forest validation).

## 6. Red-team

- **RT-1 — jump-over.** A big stride can leap over a better/worse cell. *Mitigation:* diffusion is iterative — over steps it still gradient-descends, just coarser; `r_max=6` bounds the leap; and low-r (forest, where gradients are sharp) is unaffected. The glide stops at water, so no leaping across lakes. ACCEPTED as coarse-graining, matched to the coarse info a mobile forager has over a day's range.
- **RT-2 — seasonal oscillation of range.** Avoided by design: scale on STATIC `npp_gm2`, not the ClimateField instantaneous level.
- **RT-3 — co-movement still pins the family to ONE cell.** Mobility spreads *inter-family* crowding (families settle on distinct cells), which is the R-39 killer (many families piling on the few rich cells). The *intra-family* single-cell placement (child.pos=mother.pos) is a separate mechanic; if pile-up persists intra-family, that's the next lever (family dispersal / larger footprint), not this cut. Validation step 2 discriminates.
- **RT-4 — cost of a long move.** A flat `move_cost` for a 6-cell stride under-charges energetically (Binford: longer moves cost more). *Decision:* keep flat for this cut (move_cost_flat=0 in the realistic config anyway → moot); a distance-proportional move cost is a FUTURE refinement noted here, not built.
- **RT-5 — calibration is unanchored.** `exponent/ref/max` are PROVISIONAL brackets. The *mechanism* ships default-OFF (bit-exact); **locking the scaling law for canonical runs needs supervisor sign-off** (science/calibration gate). Kelly gives the ∝1/productivity *direction* and Binford the cross-cultural *magnitude* (residential moves 0→40+/yr across the productivity range) to anchor the lock later.
- **RT-6 — torus wrap + stride.** Current cands wrap (`% w`). With the glide we walk cell-by-cell so wrap is handled per-step; a stride must not wrap *across* the grid edge onto an unintended cell — the glide naturally stops at the water rim / can be bounded to non-wrapping. *Decision:* keep wrap for continuity with today's r=1 (which wraps), but the water-rim glide stop makes edge-wrap rare in practice.

## 7. Out of scope (future)

Distance-proportional move cost (RT-4); seasonal/transhumant range (RT-2 extension); logistical (collector) forays
vs residential moves (Binford's forager–collector axis); vision/perception radius scaling (only the *move* stride
scales here, not what the agent can *see*).
