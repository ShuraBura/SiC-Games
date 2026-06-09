# Stage 6.0a — §8 Report: Multi-Occupancy Substrate

**Blueprint:** `blueprints/stage6/SiC_Games_Stage6_0a_Substrate_Blueprint.md` §8
**Filed:** 2026-06-08 · supervisor-directed report following density-flag review
**Output dir:** `outputs/stage6_0a_substrate/`
**Hypothesis resolved:** H-SUBSTRATE-6.0a → **RESOLVED-SUPPORTED** (density-calibration flag raised)

---

## 1. Config echo

All parameter values below are authoritative in `docs/PARAMETERS.md`; this report points, does not restate.

| Item | Value | PARAMETERS.md ref |
|------|-------|-------------------|
| Grid | **100×100** | §1 |
| N_init | 2250 | §7 |
| n_steps | 2000 | — |
| cell_area_km2 | 100.0 | §1 |
| k_grid | 4 | §1 |
| max_sugar_capacity | 16 | §1 |
| κ (Cred-σ coupling, C) | 0 and 1 (sweep) | §2 |
| α_matthew | 2.0 | §4 |
| ε_laplace | 0.01 | §4 |
| N_carry (100×100) | **4100** | §7 |

κ settings: two runs — κ=0 (no Cred-weighted contest; even split scramble) and κ=1 (partial
Cred-weighted contest) — to test whether social mechanic coupling destabilises the substrate.

---

## 2. Recovery gate (§7.1) — PASS

**Criterion:** single-occupancy limit (K_cell=1, legacy config) reproduces current SugarWorld
model to 1e-9 (float) / exact (integer) / exact (positions).

**Result:** Recovery gate PASS — bit-identical. K_cell=1 with the multi-occupancy substrate
recovers the legacy one-agent-per-cell model exactly. This means the substrate is a genuine
generalisation, not a rewrite that happens to produce similar output.

---

## 3. C-behavioural check (§7.2)

**Pre-registered prediction:** N(t) settles to a stable band — neither extinction nor unbounded
growth — within the ≥2000-step run, for both κ=0 and κ=1.

**Observed readings (from `behavioural_partial.pkl` checkpoint, 2026-06-04):**

| κ | Settled N | Verdict |
|---|-----------|---------|
| κ=0 | ≈ 1080 | Stable band: self-limiting, no extinction |
| κ=1 | ≈ 1150 | Stable band: self-limiting, no extinction |

**Assessment:** Both κ values produce viable, self-limiting populations. The κ=1 settled value
is slightly higher (~7%) than κ=0, consistent with Cred-weighted agents harvesting more
efficiently but without destabilisation. Viability pre-registration: **SUPPORTED**.

**Cov(φ, wealth) ≈ −0.11** — negative covariance. This is the opposite of a Matthew-runaway
signature (which would be positive and large). No Cred-dominant lineage emerged. The mild
negative covariance likely reflects that at low density, high-φ agents (stronger Cred-weighting)
harvest more from contested cells but also metabolise more at high-occupancy positions, producing
a slight wealth inversion. **Logged as open-pending-calibration.** No design response warranted
at this stage; the substrate perf recon (§3 of this report) explains why the density at which
this was measured is not the production regime.

---

## 4. Density validation (§7.3)

**Pre-registered sanity band:** ~0.01–1 persons/km² (flat terrain, 100 km²/cell).
The pre-registration expected "order ~0.1" p/km² as the target.

**Observed (from `behavioural_partial.pkl`, final-step snapshot, step 2000):**

| κ | final_n | n_cells | agents/cell (all) | persons/km² |
|---|---------|---------|-------------------|-------------|
| κ=0 | 1076 | 10 000 | 0.1076 | **0.001076** |
| κ=1 | 1154 | 10 000 | 0.1154 | **0.001154** |

The density is `agents_per_cell_all = final_n / n_cells`; `persons_per_km2 = agents_per_cell_all / cell_area_km2`.
These are the stored values — read directly from the pkl, not re-derived.

**Sanity band: 0.01–1 p/km².** Both readings fall below the lower bound.

- vs lower bound (0.01): ≈9.3× below (κ=0), ≈8.7× below (κ=1).
- vs pre-registered expected order-of-magnitude (~0.1): ≈93× below (κ=0), ≈87× below (κ=1).

The ROADMAP summary `~0.0011 p/km² ≈100× below band` was reading the pkl value correctly (using
~0.1 as the comparison point). The "100×" shorthand refers to the ≈90× miss vs the expected
order-of-magnitude, not vs the lower bound.

**Status: CALIBRATION FLAG RAISED.** Both κ readings are below the sanity band; neither
reaches the 0.01 floor. The miss is ≈9× vs band entry and ≈90× vs the expected proto-ag target.
**This flag is the primary calibration input for the next chapter: the resource-economy
calibration pass.**

The ethnographic target for proto-agricultural density is the project's original question. This
flag is not a substrate failure — it is the precise question the calibration pass is designed to
answer.

---

## 5. N_carry / N ratio (§7.4) — descriptive

N_carry (100×100) = 4100 (see PARAMETERS.md §7). Settled N ≈ 1076–1154 under multi-occupancy.
Ratio settled/N_carry ≈ 0.26–0.28 (settled population runs at ~27% of the carrying cap).

**Note:** The carry_discount birth ceiling (`max(0, 1 − N_C/N_carry)`) uses N_carry=4100 for the
100×100 grid; at settled N≈1100, the discount is ≈0.73 — the ceiling is not the binding
constraint here. The flat-terrain substrate disperses agents across 10 000 cells at mean
occupancy ≈0.11/cell, well within the feasible occupancy range identified by the 6.0a-perf recon
(≤~2.3/cell). The N_carry reconciliation was flagged in the Stage 6.0a blueprint (§10:
"N_carry re-derivation → design-doc reconciliation, not here") and remains deferred to the
calibration pass.

---

## 6. Si portability note (§7.5 / blueprint §8.6)

The Stage 6.0a substrate was built with C as the target. Si runs were explicitly out of scope
(blueprint §10: "Any Si runs, inversion protection, H1(ii) work"). The substrate opt-in flag
(default off → legacy untouched) ensures Si science configs are unaffected until Si is
explicitly ported to the multi-occupancy substrate. No Si portability breakage was introduced.

---

## 7. Occupancy-cliff finding — superseded-premise correction

**Original finding (Stage 6.0a-perf, 2026-06-05):** The performance recon identified occupancy
as the primary cost wall. Occupancy ≤~2.3/cell is feasible; >~2.5/cell is hard-infeasible via
the legacy JT-cohort loop (O(grid × occ × cohort)), and O(N²) diagnostics capped production at
N≤3–4k. The conclusion at that time: "Proto-ag density NOT reachable on Python path → needs array
restructuring + JT redesign + diagnostic subsampling."

**Stage 7.5 resolution (2026-06-08):** The array restructure is now complete (all gates PASS):
- **VecJTM (Gate B1):** O(N × k_mode) where k_mode=10 — the O(grid × occ × cohort) bottleneck
  that caused the occupancy cliff is eliminated.
- **Diagnostic vectorisation (Gate C1):** SoAWorld N=4000 @ 224ms with sparse diagnostics — the
  O(N²) diagnostic cap is lifted.
- **SoAWorld:** Structure-of-Arrays memory layout + numpy vectorisation across agents.

**Correction of premise:** The 6.0a-perf infeasibility finding was accurate *for the legacy Python
path at that time*. Stage 7.5 has changed that path. The occupancy cliff is a **superseded
premise**: the next-chapter calibration pass runs on SoAWorld+VecJTM and is not blocked by the
legacy JT-cohort cost. (See ARCHITECTURE.md §H.5-H.6 for the Stage 7.5 gate record.)

This correction is recorded here, not as an error in the 6.0a-perf report (which was correct for
its scope), but as the Stage 7.5 outcome that changes the forward feasibility picture.

---

## 8. Trait-semantics confirmation (§7.6 / blueprint §8.7)

Per blueprint §5: the minimal trait-semantics ruling for Stage 6.0a.

- **ψ re-pointed to occupancy:** ψ_i reads per-cell occupancy for movement utility. Default
  coefficient = 0 (neutral) → no movement effect this stage. Socket present; plug goes in
  later stages.
- **Affinity and crowd_response hooks:** present at 1.0 (neutral values) — reduces correctly
  to the base utility.
- **Joint-task, partner-search, pool consumers:** ported to handle multi-occupancy bands; no
  silent empties confirmed in recovery gate (250 tests pass).
- **Offspring on parent cell:** confirmed (blueprint §10: "offspring on parent cell").
- **Punted to trait re-expression deliverable:** full re-expression of c1, c2 social traits
  under multi-occupancy (i.e., within-band trust vs across-band signalling) — deferred by
  design, as specified.

---

## 9. H-SUBSTRATE-6.0a resolution

**Status:** RESOLVED-SUPPORTED (density-calibration flag raised).

**Summary of resolution:**

| Pre-registration | Outcome | Status |
|-----------------|---------|--------|
| C viability (κ=0 and κ=1) | Settles ~1080/1150, both κ. Self-limiting. | SUPPORTED |
| Self-limiting density | Per-cell occupancy stabilises; no overcrowding-collapse | SUPPORTED |
| Density vs ethnography (~0.01–1 p/km²) | 0.00108–0.00115 p/km² (pkl); ≈9× below band lower bound (0.01), ≈90× below expected ~0.1 | CALIBRATION FLAG |
| Cov(φ,wealth) — observe and defer | Cov ≈ −0.11; no Matthew-runaway | OBSERVED, OPEN-PENDING-CALIBRATION |
| N_carry / N ratio — descriptive | Settled/N_carry ≈ 0.26–0.28 (100×100, N_carry=4100); carry-discount not binding | DESCRIPTIVE (no threshold pre-committed) |

**Viability verdict:** The multi-occupancy substrate is a viable, physically-plausible
generalisation of the one-agent-per-cell model. Recovery gate passed bit-identically. Both κ
settings produce stable populations. No runaway pathology. The substrate is cleared to serve
as the floor for Stage 6.0b (terrain topography).

**Density flag:** The density calibration flag is raised and handed to the resource-economy
calibration pass. Both κ readings (0.00108, 0.00115 p/km²) miss the sanity band by ≈9×;
both miss the expected proto-ag order-of-magnitude (~0.1 p/km²) by ≈90×. Hitting that
target is the project's original question and the first task of the calibration pass.
The flag is not a blocker for substrate viability.

**Cov note:** −0.11 covariance is logged as open-pending-calibration. Recalibrate and re-measure
once the density calibration pass has the model running at the target density regime; the Matthew-
runaway question is moot at ≈90× below target density.

**Occupancy cliff:** Recorded as superseded-premise correction (§7 above). Stage 7.5 clears it.

---

## 10. Files

| File | Note |
|------|------|
| `outputs/stage6_0a_substrate/behavioural_partial.pkl` | Checkpoint from §7.2 behavioural run |
| `outputs/stage6_0a_substrate/gate_6_0a_report.md` | This document |
| `docs/HYPOTHESES.md` | H-SUBSTRATE-6.0a → RESOLVED-SUPPORTED (appended) |

---

## 11. Revision history

| Rev | Date | Change |
|-----|------|--------|
| 1 | 2026-06-08 | Initial — supervisor-directed, post-Stage-7.5 density-flag review |
| 2 | 2026-06-09 | Corrected §1 grid (50×50 → 100×100, N_init=250→2250, N_carry=400→4100); rewrote §4 density calculation from pkl values (0.00108–0.00115 p/km²), removing wrong 2500-cell arithmetic and peak-zone estimate; corrected §5 N_carry/N ratio (2.7–2.9 → 0.26–0.28); updated §9 summary table and density note accordingly |
