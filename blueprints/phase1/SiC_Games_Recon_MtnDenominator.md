# SiC Games — Recon Directive: Mountain-Fraction Denominator

**Type:** Reconnaissance only. No code changes. No re-runs. Report findings, then STOP.

**Why:** The Phase 1 Stage 1 handoff carries one open verify — whether `mountain_fraction`
(used to derive the `mtn_ceiling = 0.317` figure in pre-registered finding §H-TERRAIN-ASYMMETRY)
uses **total cells** or **land cells** as its denominator. The ceiling was characterised at
`waterK = 0.99`. If the denominator is total cells, the ceiling is partly an artefact of that
water setting (ocean inflates the denominator) rather than a structural terrain limit. The
diagnostic functions `characterizeMap()` and `runSweep()` are NOT present in the
`sic_terrain_prototype.html` snapshot available to the supervisor's chat instance, so their
actual denominator cannot be confirmed from here.

## Tasks

1. **Locate the diagnostic source.** Search the project tree (`G:\My Drive\docs\SiC Games\`
   and any subdirectories, including the headless validation harness) for the definitions of
   `characterizeMap` and `runSweep`. Report:
   - the file path(s) where each is defined, OR
   - explicit confirmation that they do not exist as committed source (i.e. they only ever ran
     inline in a throwaway headless script that was not saved).

2. **If found — report the denominator.** For the `mountain_fraction` (or equivalently named
   mountain-composition) field returned by `characterizeMap()`, quote the exact line(s) that
   compute it. State unambiguously whether the denominator is:
   - total cells (`N*N` / grid length), or
   - land cells (water excluded).
   Also report the denominator used for any other biome-fraction fields in the same vector
   (desert%, etc.), in case the convention is mixed within the function.

3. **Cross-check against the prototype.** Note for comparison: in `sic_terrain_prototype.html`,
   `computeStats()` uses two conventions — biome composition bars divide by total cells
   (`counts[k]/n`, n=N*N, line ~450), while mean forage/game/risk divide by `landCount`
   (line ~427). Report whether `characterizeMap()` inherited the total-cell convention, the
   land-cell convention, or something else.

## Stopping rule

Stop after reporting. Do NOT change any denominator, do NOT re-run any sweep, do NOT touch
§H-TERRAIN-ASYMMETRY or any logged document. Whether the ceiling finding needs correction is a
supervisor decision that depends on this report.

## Report

A short prose finding (no formal report doc needed) answering: where the functions live (or that
they don't), what denominator `mountain_fraction` uses, and whether the convention is consistent
within the diagnostic layer.
