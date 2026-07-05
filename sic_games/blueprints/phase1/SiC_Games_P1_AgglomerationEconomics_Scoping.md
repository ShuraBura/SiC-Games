# SiC Games — Phase 1 — Agglomeration Economics (the "grand unification": settlements emerge from returns-to-co-location)

**Status:** SCOPED 2026-07-04 on branch `agglomeration-rework` — **REWORK, NOT YET BUILT.** Replaces the DISCRETE settlement machinery of the aggregation-sedentism arc (R-52/R-53, Layer A/B1 — preserved on `main` / `settlement-discrete-v1`) with a single CONTINUOUS mechanism from which villages, packing, optimal size, relocation, bust, and Carneiro all **emerge**. Motivated by the supervisor's B3-emergence question: the discrete lifecycle (form/hold/dissolve/relocate thresholds + residence pin + binary tier-2 unlock) is *scripted*; every scripted rule we'd add (B2/B3) is scaffolding to unwind. The foundational version has one idea and derives the rest.

**The core idea — increasing returns to co-location.** Plain IFD has CONSTANT returns: per-capita = `S/n`, monotonically falling → agents disperse (GATE-3; why we needed the discrete unlock at all). Real settlement exists because **co-location raises per-capita** — intensive fishing/farming (weirs, terraces, irrigation), storage, defense, and division of labour need *many hands* and only pay above a threshold. So make per-capita **single-peaked in the local co-located population `n`**: rising (increasing returns) then falling (the catchment saturates). Under IFD, agents then *aggregate* to the peak size `n*` — **packing emerges** — and no further. Everything else follows.

**Anchors:** Marshall 1890 / Krugman 1991 (agglomeration economies — increasing returns → spatial clustering); Boserup 1965 (labour intensification); Johnson 1982 / Bettencourt 2013 (scaling — output super-linear in population up to congestion); Testart 1982 (storage/defence economies of scale); the discrete-tier findings R-52/R-53 (what the emergent version must reproduce: stable fisheries, packed villages, swidden bust).

## 1. Mechanism
The exploitable resource of cell `c` (worked from a co-located village) is its **catchment resource** `R(c) = Σ_{catchment} S_pot · soil` (residence ≠ foraging — the pool works a radius). The village's **total output** with `n` co-located workers is `Y(n) = R(c) · L(n)`, where `L(n)` is a **returns-to-labour** function that is convex (increasing returns) then saturating. Per-capita:

`p(c, n) = R(c) · L(n) / n`

designed to be **single-peaked at `n*`** (the emergent optimal village size). Simplest tractable form: `L(n) = min(n^α, C)` with `α > 1` (increasing returns) and `C` = catchment labour-saturation, so
- `n < n*`: `p ∝ R · n^{α−1}` — **rises with n → aggregation/packing emerge**;
- `n ≥ n* = C^{1/α}`: `p ∝ R · C / n` — **falls → the village stops growing at `n*`**.

(Other single-peaked forms — `n^{α−1}e^{−n/K}`, logistic — are interchangeable; the point is the *shape*.) Then, with NO other rules:
- **Villages emerge:** agents under IFD climb the per-capita gradient → pile onto high-`R` cells up to `n*`.
- **Optimal size emerges:** `n*` from `α`, `C` — calibrate to ~100–300 (Natufian / NW-Coast).
- **Multiple villages, not one megacity:** `R` is LOCAL (per-catchment) and saturates at `n*` → distributed villages, each ~`n*`.
- **Relocation emerges:** farming depletes `soil` → `R` falls where the village sits → the per-capita peak shifts to fresher cells → the cluster **drifts** = shifting cultivation (B3, emergent).
- **Bust / Carneiro emerge:** when every reachable cell is low-`soil`/occupied, no cell beats dispersal → the village breaks (bust); when land is full so there's nowhere fresher, it *can't* escape → forced low-yield or collapse (Carneiro).
- **Fisheries vs farming:** same `L(n)`; fisheries have non-depleting `soil≡1` (→ stable villages at `n*`, reproduces R-53), farming depletes `soil` (→ the swidden drift). One mechanism, resource-agnostic via `S_pot` + the soil dynamics.

## 2. What it REPLACES (deletes scaffolding)
- The discrete `_settlement_sites` lifecycle (formation/hold/dissolve thresholds), the **residence pin** (`_toward`), the binary **tier-2 unlock gate**, and the scripted relocation of B3 — all become emergent from `p(c,n)`.
- **Kept:** `S_pot = max(aquatic, cultivability)` (Layer A) and the per-site **soil** dynamics (B1) — these are the *substrate* the emergent villages live on, not scripted behaviour. Storage + shock (R-53) still ride on top. The **morph** reads emergent density (unchanged).

## 3. Build path (prototype-first — de-risk the calibration cheaply)
- **P0 — the curve, offline.** Numerically pick `L(n)` form + `α`, `C` so per-capita peaks at a village-scale `n*` (~100–300) with a sane basin. A table/plot, no model run. Kills the knife-edge risk before touching the core.
- **P1 — agglomeration per-capita in IFD.** Add the `p(c,n)` term to `diffusion_select_target` (gated `enable_agglomeration`, default OFF ⇒ constant-returns bit-exact). Validate villages EMERGE (density crosses packing, size ~`n*`, MULTIPLE villages) on a static `S_pot` — the R-52 packing target, now emergent.
- **P2 — soil coupling.** Turn on B1 soil under the emergent villages → validate the swidden DRIFT (relocation) + Carneiro-when-full emerge; fisheries stay stable (R-53).

## 4. Red-team
- **RT-1 [knife-edge → megacity or dispersal].** `α` too high → singular pile-up; too low → no aggregation. *Mitigation:* the saturation cap `C` gives a BUILT-IN optimal size `n*`; P0 fixes `α,C` offline to a village scale; sweep.
- **RT-2 [one global megacity, not many villages].** *Mitigation:* `R` is per-catchment (local) and saturates → distributed villages; validate ≥ several villages, each ~`n*`, in P1.
- **RT-3 [conflict with existing GRP grouping drives].** `group_safety`/`group_mate` already add agglomeration-ish terms → double-count. *Mitigation:* the agglomeration `p(c,n)` SUBSUMES them; disable/neutralise GRP when `enable_agglomeration` (reconcile explicitly).
- **RT-4 [instability / oscillation].** A strong attractor + depletion can oscillate (pile → deplete → flee → pile). *Mitigation:* soil is SLOW (B1 fallow) and `L(n)` saturates; test stability; some drift is the *intended* swidden signal — distinguish drift from thrash.
- **RT-5 [loses R-52/R-53].** Must re-derive validated packing + stable fisheries. *Mitigation:* P1/P2 explicitly target them as acceptance tests; `main` is the fallback.
- **RT-6 [bit-exactness].** `enable_agglomeration=False` ⇒ per-capita is the legacy `S/(n+1)` ⇒ full suite bit-exact. Assert.
- **RT-7 [morph still reads density].** Emergent villages must still trip `society_from_character`; density is now emergent but the reader is unchanged. Confirm.

## 5. Open questions
- **Q1 — `L(n)` functional form.** `min(n^α, C)` (kinked, simple) vs a smooth logistic/`n^{α−1}e^{−n/K}` (differentiable, softer peak)? *Recommend a smooth single-peaked form for stability; pin `n*` by calibration.*
- **Q2 — Full replace vs coexist.** Delete the discrete `_settlement_sites`/pin now, or keep them dormant behind the old flag and build agglomeration alongside? *Recommend keep the discrete code (default-OFF, still on `main`) and build agglomeration as a NEW parallel path; retire the discrete lifecycle only once agglomeration reproduces R-52/R-53.*
- **Q3 — GRP reconciliation.** Subsume the safety/mate drives into `p(c,n)`, or neutralise them under agglomeration? *Recommend neutralise (set GRP≈0) when agglomeration on, to avoid double agglomeration forces.*
- **Q4 — Does the morph/diagnostic still need a "village" object?** For reading size/soil/relocation we may want to *detect* emergent clusters (connected dense components) as a read-only diagnostic — not a driver. *Recommend a read-only cluster detector for diagnostics/morph.*

## 6. Recommendation
Build the grand-unification as **increasing-returns-to-co-location per-capita in IFD**, prototype-first (P0 offline curve → P1 emergent villages → P2 soil/relocation), `enable_agglomeration` default-OFF (bit-exact), on `agglomeration-rework`. Acceptance = it reproduces R-52 packing + R-53 stable fisheries AND yields emergent relocation/Carneiro that the discrete version needed scripting for. Keep the discrete tier on `main` as the fallback; retire it only on success.
