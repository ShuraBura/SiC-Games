# SiC Games — Performance Re-Architecture Blueprint (v1.0, 2026-07-07)

**Goal.** Make the model tractable at the Turchin secular-cycle target: **30K–50K agents × ~18,000 steps (1,500 yr)** — the natural carrying capacity of the 1M km² world (~52K agents @ 0.05/km², realistic HG density). Current cost is **~1 ms/agent, superlinear** at scale (32K agents → 128 s/step → a 1,500-yr run ≈ weeks). Target: **≤ ~10–50 µs/agent, linear** → ~50K agents in ~1 s/step → ~5 h/run (parallelizable across seeds).

**Core principle.** SEPARATE *exact-fast* from *approximate*. Most of the step is embarrassingly parallel and can be vectorized/JIT'd **bit-exact**; the only inherently sequential piece (movement's within-step crowding feedback) can be kept exact via numba. **Pay a fidelity price only if the exact tiers are insufficient.** Validate every tier bit-exact (or bounded-divergence) against the current model at small N before scaling.

## Where the time goes (profiled TWICE — small concentrated AND large spread)
- **THE SUPERLINEAR OFFENDER = `_pair_from_pool` / `_do_pairing` (MATING), NOT the band ops** (profile at 8K spread agents: `_pair_from_pool` 55% / 5.97s tottime; `_maintain_bands` only 0.12s). Root cause: `_do_pairing` mates within `self.bands(bonded_mate_radius)` — a SPATIAL connected-cell partition. Under agglomeration, thousands of agents concentrate onto adjacent cells → ONE giant spatial "band" → pairing is **O(clump²)** (every unpaired female × every candidate male, weighted choice). [Corrected 2026-07-07 — the v1 guess of `bands()` being the culprit was wrong; profile-first saved the effort.]
- Movement `diffusion_select_target` ~24–44% — per-agent × ~6 candidates; SEQUENTIAL (occ_count updates as agents move).
- Orchestration `_step_rivalrous` ~8–22% — ~25 O(n) Python passes.
- Per-cell harvest (shares/contest/granary) — O(occupancy) reductions.

## Tier 0 REVISED — bound the mating pool to the SOCIAL band (band_id), not the spatial clump
`_do_pairing` should pool candidates by `band_id` (fission-capped ~25–45) rather than the spatial `bands()` clump → O(Σ band²) = **O(n)**. This is ALSO more realistic: mate choice is band-local (~25–45 people at a seasonal aggregation), matching the ethnographic scale von Rueden measured — the whole-agglomeration pool of thousands is an artifact.
**Fidelity price (must measure):** it changes the mating SKEW — the current huge pool lets a top-prowess male out-compete *thousands* (inflated skew); band-scale pooling gives realistic local competition. This directly touches the **validated status→RS signal (R-19/R-55, ~0.13)** → re-validate. Opt-in flag `mate_within_band_id` (default OFF ⇒ bit-exact).

**A/B RESULT (2026-07-07) — NOT ADOPTED.** Perf win only **~9%** at 8K agents (394→361 ms/step): the profile's 55% was a *pathological transient* (mid-agglomeration huge spatial bands), not a steady cost, and band_id groups can also be large under merging. Mate SKEW preserved (max 3 wives both, mean ~1.03 — status→RS channel intact) BUT **MAXBAND shrinks consistently** (72→42 at 3K, 39→34 at 8K) via the marriage→band-reassignment coupling → a real cost to village-scaling for a 9% gain. **Verdict: kept as opt-in/OFF, not used.** LESSON: piecemeal routine fixes are low-ROI with fidelity costs; the real lever is Tiers 1–2 (SoA + numba/vectorize) — whole-step, exact. Go straight there.

## Tiers (effort × speedup × fidelity price)
| Tier | Change | Speedup | Effort | Fidelity price |
|---|---|---|---|---|
| **0** | Spatial-hash band ops (grid-bucketed neighbor queries; incremental fission/fusion, not full re-partition/step) | kills superlinear creep → linear | low-med | **none** (exact) |
| **1** | Structure-of-Arrays: agent state → numpy arrays; occ_count dict → 2D grid array. Vectorize parallel/cell ops: metabolism, aging, mortality (Siler + one vectorized RNG draw), fertility, harvest shares (scatter/segment reductions), field lookups, granary | 5–20× on ~55% | high | **none** (bit-exact if per-agent RNG draw order preserved) |
| **2** | numba-JIT the SEQUENTIAL movement loop on the SoA arrays — keeps exact within-step feedback at native speed | 20–100× on 44% | med (numba not yet installed) | **none** |
| **3a** | Simultaneous / K-batched movement (decide from start-of-step occupancy) | +2–10× on movement | med | SOME — loses within-step crowding deterrence (transient over-piling). Tunable via K batches (K=1 exact ↔ K=∞ simultaneous) |
| **3b** | Entity lumping: settled/complex bands → cohort super-agents (pop count + aggregate cred/age distributions); individuals only on the egalitarian frontier | large (fewer entities) | high | LARGEST — see ledger |

## Fidelity ledger
- **Tiers 0–2 cost NOTHING** (exact reimplementation; numba keeps movement sequential). Expected to reach ~10–50 µs/agent → **the target is likely met by Tiers 0–2 alone, zero science change.**
- **Tier 3a** trades the within-step self-limiting for speed (IFD lit mostly assumes simultaneous decisions anyway — defensible; validate packing/nucleation unchanged; K-batching dials the error).
- **Tier 3b (lumping)** — biggest lever, first to cost science:
  - LOST: within-village individual heterogeneity — cred/prowess distribution, individual lineages, the **status→RS von Rueden signal (R-19/R-55)**, individual mortality selection (R-18). These validated Carbon-civilization results live at the individual level INSIDE a band.
  - PRESERVED (if aggregate carries summary stats): band size, society type, assabiyah, storage, births/deaths as binomial-on-cohort, band-level competition.
  - Least-damaging in STRONG HIERARCHICAL societies (band already acts as a coordinated unit). Clean design = ADAPTIVE RESOLUTION: individuals where heterogeneity does scientific work (egalitarian frontier, status dynamics), cohort-lumped where the collective is the actor (settled complex/stratified villages). Accept that status→RS inside lumped units is SUMMARIZED, not tracked.

## Sequence
1. **Tier 0** — spatial-hash band ops. Exact, contained, de-risks the rest. (Profile spread case first to confirm culprit.)
2. **Tiers 1–2** — SoA + vectorize + numba movement. The 10–100× lever, STILL EXACT. Incremental (migrate hot paths behind an adapter; keep the rest object-based until migrated). Bit-exact validation at each step.
3. **STOP + measure.** If 50K runs in hours → done, no fidelity price paid.
4. **Tier 3 only if still too slow** — 3a (batched movement, bounded error) before 3b (lumping, sacrifices validated status dynamics).

## Validation protocol (every tier)
Run fast-path vs current model, same seed, small N (≤2K), N steps → assert **bit-exact** (Tiers 0–2) or **bounded divergence** on headline diagnostics (Tier 3: eq-pop, packing, MAXBAND, %complex, status→RS). No tier ships without this.

## Effort
Tier 0 ~days; Tiers 1–2 ~weeks (incremental, validated); Tier 3 ~weeks more. A real performance project — but with a mostly-EXACT path; not a forced trade of science for speed.

*Blueprint 2026-07-07. Supersedes the ad-hoc perf notes. Implementation tracked in RESULTS as it lands.*
