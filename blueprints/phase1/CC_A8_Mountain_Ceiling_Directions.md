# A8 Mountain-Corner Resolution — CC Directions

**Context:** A8 gate RED — mountain_fraction caps at ~0.28 in LHS sweep; blueprint's ≥0.5 was an arbitrary threshold. Resolution: measure the true generator ceiling, make A8 generator-relative, pre-register the asymmetry as a finding. Do steps in order.

## 1. Focused ceiling-search (do FIRST)
- Pin `relief` at max.
- Coarse grid over `roughness` × `water-abundance` × `aridity` (~4 points each). **Not a single-knob line** — roughness interacts non-monotonically with relief (more roughness = more steep cells, but can fragment high massifs into steep-but-low gullies that fail the `elev>0.72 AND slope>0.18` joint condition).
- Several seeds per grid point (5–10); report the **max over seeds** so the ceiling isn't one lucky terrain.
- Report `mtn_ceiling` = max mountain_fraction over the grid, plus the knob-combo that produced it and confirmation it held across seeds.
- This is ceiling-finding, not optimization — coarse grid is fine.

## 2. Rewrite A8 mountain criterion (AFTER step 1 returns)
- New criterion: sweep must reach `mountain_fraction ≥ 0.9 × mtn_ceiling`.
- Desert criterion stays absolute at ≥0.5 (clears comfortably at 0.76).
- Criterion can only be evaluated after `mtn_ceiling` is known — do not check against a placeholder.
- Document the criterion change and reasoning.

## 3. Pre-register the asymmetry finding (HYPOTHESES.md + MODEL_SPEC.md)
- The generator's reachable world-space is asymmetric in biome dominance: desert_fraction reaches ≥0.76; mountain_fraction is structurally capped at ≈`mtn_ceiling`.
- Structural cause: joint `elev>0.72 AND slope>0.18` condition under spatial autocorrelation of elevation/slope makes high-and-steep cells self-limiting (plateaus are high-but-flat; valleys steep-but-low).
- Consequence: mountain-dominant worlds are not producible; this bounds the conditions under which mountain-related dynamics can be studied / tested against H1(ii).

## 4. Proceed
- M3 must-be-seen (mountain-axis spread) spreads **up to `mtn_ceiling`**, not 0.5 — show the harshest mountain world the generator can actually make. M3 generation waits on step 1.
- Then continue: docs → remaining artifacts → commit.

**Out of scope (do NOT):** lower `mtn_elev_thresh` / `mtn_slope_thresh` — redefining "mountain" to hit a coverage number corrupts a terrain primitive.
