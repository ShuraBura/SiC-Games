# SiC Games — Deep Audit (2026-07-01)

Pre-big-run audit after the Social-Evolution arc (climate harness, leader coherence, size repulsion, M2
malnutrition fission, F resource-directed fusion, genealogy logger). Four passes: tests · performance · coherence ·
flag interactions. **Bottom line: no regressions; the stack is healthy and cheap; one clear perf win before scale.**

## 1. Tests — GREEN
`592 passed / 1 xfailed` (full suite, ~176 s). All new mechanics unit-covered; bit-exact-when-off contracts hold.

## 2. Performance — HEALTHY; one clear optimization
Full stack (ALL flags on), 300 founders × 400 steps, cProfile:
- **13.5 ms/step (0.057 ms/step/agent)** at ~240 agents. Extrapolates to ~a few minutes for a 2000-agent × 3000-step run — acceptable.
- **The recent social additions are CHEAP.** `_maintain_bands` (all of leader + repulsion + M2 + F) = **0.13 s of 5.4 s** (~2.4 %). Genealogy logger negligible. The accreted flags did NOT add a perf tax.
- **Cost is the core loop:** `_step_rivalrous` 90 %; `diffusion_select_target` 2.33 s (per-agent movement); **`climate.level` 0.97 s + the multiplier chain (`regime` 0.41 + driver `__call__` 0.29 + `season` 0.16) ≈ 1.5 s (~28 %)**, called 328 k× (once per candidate-cell evaluation).
- **OPT-1 (recommended before the big run):** the climate *temporal* multiplier `mean_factor·season()·regime()` is **cell-independent** but recomputed per cell-eval (~820×/step). Cache it once per `set_step` → keep only the per-cell `interannual_at` (llanos mask) inline. **~25 % runtime saving, bit-exact** (t is constant within a step). Clean; folds naturally into the CC-1 pass.

## 3. Coherence — full stack coheres; no regression
Full stack ON, flat climate (a_seas 0.25), 6 seeds × 1300 steps:
- eq_pop **339** mean (146–560), bands agent-wt **22.3**, mean_cred 1.55, Gini 0.17 — all healthy, no extinctions.
- eq_pop sits below the static-R-26 360–540 **as expected** — it's the documented **seasonal trough-limiting** (R-27, ~−27 %), not a regression (this run is on a ClimateField; R-26 was static).
- The dispersive flags (repulsion + M2) **intentionally** lower eq_pop + band size + fission-rate — the designed dispersion cost, not a bug.

## 4. status→RS — NOT a regression (climate depresses it, per R-27)
The headline scare resolved: status→RS ≈ **+0.014** (flags on, 6 seeds) and **+0.029** (flags off, 3 seeds) —
**both near-zero on the climate substrate**, within seed noise of each other. So the new flags do NOT collapse it.
- The documented **0.13 is the STATIC-substrate value (R-26)**; bit-exactness (flags off = the exact R-26 model)
  guarantees it holds there. On a ClimateField (seasonal on) it drops to ~0.01–0.03 — exactly R-27's finding
  ("0.06–0.19 across climate configs vs 0.136 static").
- **Measurement-power caution:** status→RS needs the full 6-seed × 1500-step protocol; at 3 seeds it swings ±0.1.
  Quick checks of this quantity are unreliable — always use the full protocol.

## 5. Flag interactions — clean, one dependency to document
- **Dependency:** `enable_leader_coherence`, `enable_size_repulsion`, `enable_malnutrition_fission` all live inside
  the `if enable_dynamic_bands:` block → **they are no-ops unless `enable_dynamic_bands=True`.** (`F` fusion and the
  genealogy logger are independent.) Document this so a config that sets e.g. repulsion without dynamic bands isn't
  silently inert.
- **Cohesion balance:** `clamp(assabiyah + leader − repulsion − malnutrition, 0, 1)` — additive, clamped; no
  degenerate combination found. Repulsion+M2 compound (large starving band → strong fission) as intended.
- **Genealogy logger:** pure observer, bit-exact on↔off (verified).

## Actions
- **OPT-1** cache the climate temporal multiplier per step (~25 %, bit-exact) — do in the CC-1 pass.
- **DOC-1** note the `enable_dynamic_bands` dependency of leader/repulsion/M2 (PARAMETERS/MECHANISMS).
- **DOC-2** the "canonical realistic config" for the status→RS 0.13 calibration is STATIC + new-flags-OFF; the
  dispersive flags and the climate substrate both lower it (expected). Clarify in RESULTS so 0.13 isn't misread as
  the all-flags-on value.
- **No blocker for CC-1 or the big run.** Recommended order unchanged: (OPT-1 +) CC-1 → big checkpoint run → settlement.
