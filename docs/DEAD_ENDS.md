# SiC Games — Dead Ends

**The ONE question:** "What did we try and abandon, and why?" (charter §2, home 11).

**Discipline:** append-only. Records approaches retired or deprioritized so they are not silently re-attempted. A dead end may be *revived* by a dated note if circumstances change — it is a record, not a tombstone.

---

## DE-1 — H-ORTHOGONALITY as a live pre-registration (deprioritized 2026-06-05)

**What it was:** a pre-registered hypothesis that C and Si home-range distributions occupy *orthogonal* axes of the foraging×social movement space (C social-pull-weighted, Si foraging-pull-weighted) — a difference-set, not a scale difference.

**Why deprioritized (not deleted):** the asymmetry is **near-implied by construction** — the C2 classification (ψ = proximity-to-agents for C vs proximity-to-foraging-spots for Si) already builds it in, so a "confirmation" would largely restate the design rather than risk it (low capacity to embarrass us). It also has no scheduled run and requires the OWE-13 movement-decomposition diagnostic, which is not built. It therefore fails the HYPOTHESES test ("could a pending run prove it wrong?") and was routed out of HYPOTHESES.md.

**Where it lives now:** **TARGETS.md T-2** — retained as an aspiration worth *measuring* if/when OWE-13 is built, with its original test spec preserved. It graduates back to a HYPOTHESIS if/when OWE-13 is scheduled and a magnitude threshold for "orthogonal vs parallel-but-scaled" is pre-committed.

---

## DE-2 — The bare `forage_kcal` field as the bands substrate (abandoned 2026-06-26)

**What it was:** running emergent bands on `TerrainField.level` (forage_kcal × hours, ~1–8 persons/cell).
**Why abandoned:** a 100 km² cell can't feed a 25-person band on it (median land cell <1 person, ~1-step reserve buffer) → a seeded band wipes out in ~2 steps; "bands" only "persisted" as corpse piles (R-22). **Replaced by** the CC-1 NPP-capacity field (`NPPCapacityField`, ~30–50/cell), the regime where a cell holds a band and crowding is density-disease-regulated. The bare field's own docstring already flagged it provisional. (See RESULTS R-22; MODEL_SPEC §4.8.4.)

## DE-3 — Storage-tethering (`storage_tether_reserves`) (retired 2026-06-29)

**What it was:** freezing a stocked band in place so it concentrates past Binford packing → the morph trigger.
**Why retired:** a band-aid for the *pre-bands* max-occupancy-2 dispersal. With emergent bands (grouping + bonded mating) the morph fires from emergent density+storage alone (R-23); the tether only added over-concentration artifacts (≈4× pop, spurious stratified_chiefdom). Config field + movement guard deleted. *Revive only if a future substrate again can't reach packing emergently.*

## DE-4 — Risk-dilution as a MORTALITY penalty (`enable_band_risk`) (shelved 2026-06-29)

**What it was:** a loner/small-band mortality penalty (safety-in-numbers wired into the death schedule).
**Why shelved:** it's a **death spiral, not a stabilizing optimum** — mortality culls but does not aggregate (penalty 0→6: pop 281→64, R-24). Risk-dilution is already expressed *behaviorally* via the E.1 movement drive; banding's fitness teeth are the F.1 mate-gate. Flag **kept in, default-OFF, with a caveat** (not deleted — available for future experiments). *Revive only with a mechanism where the penalty drives aggregation, not just death.*

## DE-5 — The per-conception paternity LOTTERY as the reproduction model (superseded 2026-06-29)

**What it was:** assign a fresh prowess-weighted father at every birth (`enable_paternity` without pair-bonds).
**Why superseded:** an idealized "any high-prowess male fathers any birth" mechanism = polygyny-like → it reproduces the von Rueden *cross-system* average (0.19), not a marriage-system-specific value. The **family stack (persistent pair-bonds + modest polygyny)** replaces it as the realistic reproduction model → status→RS ≈0.13 (the monogamy-dominant value, R-26). The lottery's m=5→0.19 calibration (E.3-proper, R-21) is **retained as the superseded simpler-mechanism reference**, not the current model. (MODEL_SPEC §4.8.12.)

## DE-6 — Forcing the full-stack status→RS to 0.19 (not pursued 2026-06-29)

**What it was:** the temptation to bump `mate_choice_strength` until the monogamy-dominant family model hits 0.19.
**Why not pursued:** 0.19 is the polygyny-inflated cross-cultural *average*; von Rueden's monogamous-society value is r≈0.15, so forcing 0.19 would *over*-skew a monogamy-dominant society relative to the evidence. **0.13 is accepted as the marriage-system-appropriate target** (R-26). The honest route to a higher per-band skew is *condition-dependent polygyny* (rich bands) + a future *wife-quality* channel, not a global m bump.

---

*End of DEAD_ENDS — seeded 2026-06-05. Append-only; revive with a dated note.*
