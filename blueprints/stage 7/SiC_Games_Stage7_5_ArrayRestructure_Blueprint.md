# SiC Games — §7.5 Array Restructure Blueprint ("agents as matrix rows")

**Status:** DIRECTIVE for Claude Code (CC). **Authored:** 2026-06-05 (supervisor, in chat).
**Obeys:** `DOCS_CHARTER.md`. Behaviour-change discipline (TMTS guard) applies: this is a
**performance-equivalent refactor**, not a model redesign. Any change to *what the model does*
(as opposed to *how fast*) is a bug unless it is a consciously-registered Tier-3 semantic
(see §3) logged in the ARCHITECTURE/MECHANISMS decision log.
**Suggested home:** `blueprints/perf/` (or a new `blueprints/restructure/`).

---

## §0 Why this blueprint is shaped differently

A normal stage blueprint leans on the **bit-identical recovery gate** for validation. This
refactor *breaks that gate by construction* for the order-dependent mechanics: a vectorised
step is **simultaneous-update**, the current loop is **sequential**, and for any mechanic where
agents read state that earlier agents mutated *within the same step* (Deffuant, the JT
contest, per-birth endowment), simultaneous ≠ sequential at the bit level. That is not a
defect to engineer around — it is a different, legitimate update semantics. The risk is that
the gate silently goes from "proves correctness" to "always red, ignored."

So the spine of this blueprint is **§3, the equivalence methodology**: a per-mechanic
classification that says exactly which gate each mechanic must pass. Get that right and the
rest is careful engineering.

---

## §1 Objective and the three coupled workstreams

The 2026-06-05 perf recon (ARTIFACTS.md) established the cost ordering **occupancy ≫ N ≫
grid-cells** and named the enabling path. Proto-ag density (~100 agents/cell) is unreachable
on the object/Mesa path; it requires all three of these, together:

| WS | Workstream | What it fixes | Report basis |
|---|---|---|---|
| **A** | Array reformulation (SoA: agents as numpy columns) | Removes per-agent-object Python loops; kills the `mean_cred` O(N²); makes Numba/GPU *possible* | §5 "THE enabling path"; §2 hotspots |
| **B** | Joint-task multi-occupancy redesign | The **occupancy cliff** — JT rebuilds cohorts O(grid×occupancy×cohort) | §2 (~29% hotspot), §3 (cliff at ~2.5/cell) |
| **C** | Diagnostics subsampling/vectorisation (Moran's I, c_spatial_density) | The O(N²) diagnostics add ~40% on full steps and gate any high-N run *regardless of substrate* | §2, §3 |

A is the substrate; B is the proximate density gate; C gates measurement at high N. **All
three are required** — A alone leaves the occupancy cliff (B) and the diagnostic wall (C)
standing.

---

## §2 Data model (Structure-of-Arrays)

Replace per-agent Python objects with parallel numpy columns indexed by a stable agent id:

- **State columns:** `pos` (linear cell index `y*W+x`, not (x,y) tuples), `wealth`, `phi`,
  `cred`, `si_cred`, `strategy` (enum int), `age`, `c1`, `c2`, `psi`, `alive` (bool mask),
  `parent_id` / `lineage_root` (for T-1 lineage analysis later).
- **Births/deaths:** **preallocate with capacity** (`n_carry`-scaled headroom) + an `alive`
  mask + periodic compaction; avoid per-step array resize. Deaths flip the mask; births fill
  free slots. *(Decision D3, §10.)*
- **Cell bucketing primitive:** sort/group agent indices by `pos` (argsort on the cell-index
  column, or `np.add.at` segment ops). This single primitive serves harvest-split, the JT
  contest (WS-B), local density, and ψ-proximity. Build it once, reuse everywhere.
- **RNG:** **counter-based / per-agent-keyed** draws — every stochastic draw keyed by
  `(seed, step, agent_id, stream_label)` so the result is **independent of evaluation order**.
  This is what lets the non-interacting stochastic mechanics stay reproducible (and Tier-1/2
  identical) under vectorisation, and makes the interacting ones (pairing) reproducible under
  a *chosen* scheme. *(Decision D2, §10.)*

---

## §3 The equivalence methodology (the spine)

Keep the current object model **frozen as the reference oracle** for the whole migration.
Every mechanic is migrated against it under one of three gates. The gate is chosen by the
mechanic's *interaction structure*, not by preference:

### Tier 1 — Bit-identical (simultaneous == sequential; no intra-step shared mutation)
Per-agent independent updates: Cred decay, the σ formula `σ=σ_base+κ·tanh(𝒞/C*)`, Si-cred
band + `σ_Si_eff`, status amplification `w_C`, stress sigmoid, metabolism/wealth/age, η(a),
DTM `P_birth`, the γ Cred-modulation, `carry_discount`, dormancy flags; sugar growback and
seasonal `c_eff` (elementwise on the grid). **Gate: exact bit-match to the oracle.** These
keep the old discipline intact.

### Tier 2 — Numerical tolerance (algebraically exact; FP reduction-order differs)
Reductions and segment ops where associativity shifts the last bits: `mean_cred` (now one
cached column-mean — **this is where the O(N²) dies**), `mean_wealth`, harvest-split
(segment-sum by cell), Gini. **Gate: match to `rtol≈1e-9`** — the same tolerance the
2026-05-28 audit used ("science unchanged to 1e-9").

### Tier 3 — Statistical equivalence (simultaneous ≠ sequential as a semantics choice)
The order-dependent mechanics, where vectorisation forces a deliberate update scheme:
- **Deffuant** (pairwise bounded-confidence, `μ_eff=μ(1−c1)`): commit to a **simultaneous
  pairing** scheme (e.g. one random matching per neighbourhood per step, all pairs resolve
  off the pre-step state). Will not bit-match a sequential loop.
- **JT + Matthew contest:** the partition `Δ𝒲_i=s·(𝒞_i+ε)^α/Σ_j(𝒞_j+ε)^α` is exact as a
  segment op, but the cell-resolution order (cell zeroed after) and the `Bernoulli(c2_i)`
  defection draws are order-sensitive — keyed RNG (§2) fixes the draws; the resolution scheme
  must be declared.
- **Biparental reproduction:** parent **pairing** is the relational step; the per-birth
  endowment now uses the **pre-batch** `mean_cred` (all same-step newborns see one mean) — a
  conscious semantic change from "each newborn sees earlier same-step newborns" (report §4).

**Gate for Tier 3: pre-registered statistical equivalence.** Before running the comparison,
write the acceptance criteria (this echoes the HYPOTHESES anti-HARKing discipline — equivalence
is itself a prediction stated before looking): run oracle vs array across **≥10 matched
seeds** and require (a) N(t) trajectory envelopes overlap, (b) steady-state distributions of
{Cred, wealth, Gini, Cov(φ,wealth), trait means} agree by KS test at a pre-committed
threshold, (c) summary moments within CI. A Tier-3 mechanic that *fails* equivalence is either
a bug or an unintended semantic change — investigate before proceeding; do not re-interpret
the criteria after seeing the result.

> The recovery gate (`enabled=False` recovers the prior stage) still applies and must pass at
> Tier 1/2 for every toggled-off path.

---

## §4 Workstream A — migration order (parity-checked at every step)

Infrastructure before migration; cheapest/safest mechanics first to prove the harness:

1. **Stand up the SoA container + the parity harness (§7) FIRST.** No mechanic migrates until
   the harness can run oracle-vs-array on a shared seed and diff per-column.
2. **Tier-1 per-agent updates** (metabolism, wealth, age, cred decay, σ, dormancy) → bit gate.
   Proves the harness on the safe cases.
3. **Grid ops** (growback, seasonal, harvest-split via the cell-bucket primitive) → Tier-2.
4. **Movement** (diffusion + foraging-pull sugar-gradient + social-pull ψ; the softmax over
   the ragged `v∈{1..6}` vision as a masked bounded gather) → Tier-2 (ties broken by keyed RNG).
5. **Reductions** (`mean_cred` → cached column-mean) → Tier-2. **O(N²) hotspot removed.**
   → **GATE A1 (§8): re-measure N-scaling — expect ~linear, Numba now structurally eligible.**
6. **Births/deaths** (mask + capacity + the pre-batch endowment semantic) → Tier-3.
7. **Deffuant** (commit + document the simultaneous pairing scheme) → Tier-3.

---

## §5 Workstream B — JT multi-occupancy redesign (the cliff)

This is the highest-value single rewrite — it is *the* occupancy gate. The legacy mechanic
rebuilds co-occupant cohorts by scanning O(W×H) candidate cells in Python per candidate. The
numpy candidate-scan win the recon found (2.6×, exact) is a minor slice; the cohort-build is
the cost. Replace the whole thing with a segment computation over the cell-bucket primitive:

1. Bucket agents by `pos` (argsort once per step — shared with harvest-split).
2. Identify qualifying JT cells: occupancy `≥2` **and** cell capacity `≥θ_c` — a vectorised
   mask over the bucketed counts.
3. Compute the Matthew denominator `Σ_j(𝒞_j+ε)^α` per qualifying cell as a **segment-sum**
   (`np.add.at` / `bincount`-style), then `Δ𝒲_i = s·(𝒞_i+ε)^α / denom[cell_i]` by gather.
4. Apply the `c2` defection hook as a vectorised `Bernoulli(c2_i)` using keyed RNG.

Target: turn **O(grid×occupancy×cohort) → O(N) + O(occupied cells)**, removing the cliff.
→ **GATE B1 (§8): re-run the perf recon's occupancy axis — the cliff at ~2.5/cell must be
gone and affordable occupancy must climb toward the proto-ag target.** This gate is the
go/no-go on whether proto-ag is reachable on CPU-numpy or whether GPU/JAX (the *next* tier) is
required.

---

## §6 Workstream C — diagnostics subsampling / vectorisation

Moran's I (6.85 s) + `c_spatial_density` (4.74 s) are O(N²) and add ~40% on full steps; they
gate high-N runs independent of substrate. Two moves, either/both:
- **Vectorise** on the grid/cell-bucket representation (Moran's I as a sparse
  neighbour-weight operation; density as a segment count).
- **Subsample** for in-run monitoring (compute on a sampled subset / coarser cadence), full
  computation only at checkpoints. The existing `metrics_every` knob is the hook.
→ **GATE C1 (§8): full-step affordable N no longer collapses to ~3–4k.**

---

## §7 The parity / equivalence harness (validation infrastructure)

A standing test module, built first (§4.1), kept permanently:
- Runs oracle (object) and array models on **matched seeds**, same config.
- Per-mechanic mode: isolate one mechanic, diff per-column at the declared gate (bit / `1e-9`
  / statistical).
- Full-model mode: the Tier-3 statistical battery (§3) across ≥10 seeds.
- Wires into the existing 256-test suite as a parity sub-suite; CI-gated.
- Emits a parity report → ARTIFACTS.md per migration step.

---

## §8 Staging with go/no-go gates

| Gate | After | Pass criterion | If fail |
|---|---|---|---|
| **A0** | Harness + Tier-1 migrated | Bit-identical on per-agent updates | Harness bug — fix before any further migration |
| **A1** | Reductions migrated | N-scaling ~linear; `mean_cred` O(N²) gone; Numba path compiles | Investigate residual super-linearity before B |
| **B1** | JT redesign | Occupancy cliff gone; affordable occupancy climbs toward target | **Go/no-go: escalate to GPU/JAX tier or re-scope density** |
| **C1** | Diagnostics | Full-step affordable N no longer ~3–4k-capped | Subsample harder / defer some diagnostics to checkpoints |
| **FINAL** | All migrated | All gates green **+** one full known-result science run reproduced within Tier-3 equivalence | Object oracle stays canonical until clean |

---

## §9 Scope boundaries (named so they aren't silently swept in)

- **No GPU/JAX in this pass.** It is the *next* enabling tier, unlocked by A; the report flags
  it high-effort (scatter/segment + divergent control on dynamic births/deaths). GATE B1
  decides if it's even needed.
- **Numba is validation, not a requirement** — once arrays land, confirm the `njit` path
  compiles and measure (it's blocked *today* only by agent-object attribute access). The pass
  succeeds on numpy alone.
- **No new science mechanics, traits, or terrain (6.0b).** Pure performance-equivalent refactor.
- **The one sanctioned behaviour change** is the pre-batch birth-endowment semantic (§3, Tier-3),
  logged in the decision log and validated as distributionally equivalent — not bit-matched.

---

## §10 Decisions for supervisor (genuine forks; recommended defaults)

- **D1 — Tier-3 equivalence standard.** *Default: pre-registered statistical equivalence (§3).*
  Alternative: write the vectorised code to *replay* sequential order exactly (preserves
  bit-match but forfeits most of the Deffuant/JT speedup — self-defeating). Recommend default.
- **D2 — RNG scheme.** *Default: counter-based / per-agent-keyed (§2).* Makes results
  order-independent and reproducible; the right foundation. Recommend default.
- **D3 — births/deaths memory.** *Default: preallocate-with-capacity + compaction.* Better
  perf than dynamic resize at high N. Recommend default.
- **D4 — oracle retirement.** *Default: keep the object model frozen as the reference oracle
  until FINAL gate passes + a known science result reproduces; then → `archive/`, not deleted.*

---

## §11 Roadmap impact

This **inserts before** resource-economy calibration *at proto-ag density* (you can't calibrate
a density you can't run). But it does **not** block everything: calibration and live science in
the **affordable ~2/cell regime can proceed in parallel** — including first exploration of
**T-1 (microscale secular cycles)**, which is observable at affordable densities. So the team
isn't idle during the rewrite. ROADMAP should be updated: perf-recon (done) → **§7.5
restructure (this)** → re-run recon (GATE B1) → resource-economy calibration at target density
→ 6.0b terrain, with affordable-regime work running alongside.

---

*End of §7.5 Array Restructure Blueprint — 2026-06-05. Gates A0, A1, B1, C1, FINAL. Decisions
D1–D4 pending supervisor confirmation.*
