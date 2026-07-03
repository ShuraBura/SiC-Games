# SiC Games — Phase 1 — Central-Place Co-Movement (the biome→society fix)

**Status:** BUILT + COMPARED 2026-07-03 (R-42). Three ablatable prototypes; FOOTPRINT recommended; canonicalization pending supervisor sign-off.
**Anchors:** Isaac, G. (1978) "The food-sharing behavior of protohuman hominids" (central-place foraging); Hawkes/O'Connell/Marlowe (Hadza dispersed foraging + sharing); Lee 1979 (Ju); Kaplan 2000 (children provisioned, not self-extracting). [INLINE — PDFs not filed.]
**Motivates:** R-41 — F.3b family co-movement snaps the whole family onto the mother's single 100 km² cell, where each member extracts `S/n`; this over-subscribes her cell (occ 3.73 vs mean 1.71) → energetic-fertility collapse in marginal biomes (savanna births 4× lower) → the biome→society collapse.

## 1. The missing physics
The model conflated **co-residence** (sleep/share at a camp — real) with **co-foraging** (extract from the same cell — an artifact). Real foragers are CENTRAL-PLACE: co-reside + pool food, but forage dispersed by day; dependents eat the shared return. The fix is to restore that decoupling.

## 2. Three prototypes (all `enable_pair_bonds`-gated, default OFF ⇒ bit-exact exact-snap)
- **(i) `comove_anticipate`** — the family-root's move utility counts its followers (`extra_occupants` → per-capita `S/(n+family)`); she picks emptier/richer ground. Seam: `substrate.py::diffusion_select_target(extra_occupants=)`.
- **(ii) `comove_footprint=k`** — followers take the lowest-occupancy land cell within Chebyshev `k` of the head (deterministic, tie-break toward the head) — a dispersed camp, not a stack. Seam: the follower-snap loop in `phase1_model`.
- **(iii) `comove_provision_exclude`** — JUVENILE followers take no forage share (`_forage_excl` splits forage among actual foragers; juveniles fed via the provision pool + band-pooled meat). Seam: the per-cell harvest split.

## 3. Comparison result (R-42; savanna=collapse, forest=control; 3 seeds × 900 steps)
| arm | savanna pop | forest pop |
|---|---|---|
| A canon (exact snap) | 8 | 145 |
| (i) anticipate | 4 | 133 |
| (ii) footprint=1 | 243 | 426 |
| (ii) footprint=2 | **378** | 451 |
| (iii) provision-exclude | 22 | 221 |
| (i)+(ii) fp1 | 393 | 408 |
| OFF (no pair_bonds) ref | 461 | 808 |

**FOOTPRINT is load-bearing** (physically spreads the family → kills over-subscription); anticipation alone barely helps (family still lands on one cell); provision-exclude is partial (only juveniles). Recommend **footprint** as canonical; radius (1 vs 2) + optional `+anticipate` to be locked with supervisor. footprint=1 ≈ a ~30 km camp span on the 100 km² grid (a plausible Hadza day-range); footprint=2 is stronger but coarser.

## 4. Red-team
- **RT-1 — footprint just relabels "no co-movement".** No: the family still co-resides within a tight `k`-cell camp (shared band, mate-gate, provisioning intact), it simply doesn't stack on one point. At `k=1` the camp is a 3×3 block ≈ one band territory.
- **RT-2 — forest pop RISES under footprint (145→451).** Expected: exact-snap over-subscription was suppressing forest too (145 vs OFF 808), just not fatally. Relieving it everywhere is correct, not a regression — but the forest E.3 status→RS validation must be re-checked before canonicalizing (co-residence density feeds the Carbon channels).
- **RT-3 — provision-exclude could starve juveniles.** Mitigated: excluded only from FORAGE; still receive band-pooled meat + the (now larger) maternal provision. Not recommended as the primary fix anyway.
- **RT-4 — determinism.** Footprint scatter is deterministic (lowest-occ, Chebyshev tie-break); `occ_count` updated incrementally so within-step ordering is stable. Default-OFF bit-exactness locked by `test_default_off_matches_canonical`.

## 5. Pending before canonicalization (supervisor gate)
Pick fix + radius; re-run the FULL biome→society table (all archetypes) + confirm forest E.3 status→RS and the full-stack results survive; then flip the chosen flag into `realistic_forager_demog` and update PARAMETERS §18 to CANONICAL.
