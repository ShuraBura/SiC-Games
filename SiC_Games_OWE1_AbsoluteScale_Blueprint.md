# SiC Games — OWE-1: Absolute-Scale Calibration (Measurement → Calibration → Report)

**Version:** 1.0
**Type:** Measurement-then-calibration blueprint. Tasks 1–2 are measurement gates
  that feed Tasks 3–4. Do them in order; later tasks consume earlier outputs.
**Scope:** NO science changes, NO new mechanics, NO parameter retuning of locked
  values. This blueprint *measures* runtime and carrying capacity at the target
  geometry, then *assigns physical units* (cell→km, metabolic-unit→kcal, step→time)
  to the existing locked model, and reports the implied timescale and compute budget.
**Output dir:** `outputs/owe1_calibration/`
**Authoritative-doc fold-in:** This blueprint also executes the standing
  documentation directive (see §0). Do that in the same pass.

---

## 0. Standing documentation directive (execute in this pass)

Per the 2026-05-30 Standing Handoff, every step blueprint must also fold owed/
conceptual items into the **live** authoritative docs. The `/mnt/project/` copies are
stale (ROADMAP is a Stage-4.1 snapshot); the **live drive copies are current through
Stage 5.2** and are the only ones you can see and edit. Reconcile against those.

**Merge discipline (MANDATORY — idempotent + conflict-surfacing):**
For each item below, check whether an equivalent entry already exists in the live doc.
- **Absent** → append it.
- **Present and consistent** → skip (note "already present" in the report).
- **Present and CONTRADICTORY** (a locked value, citation, or parameter that has
  moved since 2026-05-30) → **STOP. Do not auto-resolve.** Record the conflict in
  the report (`§5 Doc-fold-in`) and flag for supervisor. A stale handoff silently
  clobbering live state is the §2-rule failure mode in reverse and is forbidden.

Items to fold in:
1. **ROADMAP** — append the Sweep-Matrix ⟨ρ⟩ axis (Handoff §4) and the Deferred/Owed
   table (Handoff §5, OWE-1..OWE-10) to the "Owed" section if not present. **Add the
   new owed items registered this session** (see §6 below): OWE-11, OWE-12, OWE-13.
2. **MODEL_SPEC** — fold the resolved Davies/Loihi citation (Handoff §3, OWE-4) into
   the energy-substrate discussion. **Create MODEL_SPEC §9 (world/resource substrate)**
   if absent — it is listed in the §7 full-extraction schema but the file is still
   PILOT scope and §9 does not yet exist. OWE-1's calibration output (this blueprint's
   §3–§4 results) becomes the first content of §9.
3. **HYPOTHESES** — register the Handoff §6 conceptual hypotheses (H-ORTHOGONALITY,
   instinct-debt) as `OPEN` pre-registrations *before* any run that could test them.
   This blueprint runs no such test, so registration-only; no HARKing risk here.
4. **Honour the process rule** — all deferred items go to the tracked ROADMAP "Owed"
   section, never chat-only.

---

## 1. Task 1 — Benchmark the ACTUAL target geometry (measurement gate)

**Why:** every timescale/budget figure in the session analysis rests on an
*interpolated* ~130 ms/step between B2 (100×100, N=1000) and B4 (150×150, N=2000).
The target geometry — **100×100, N=2000** — was never benchmarked directly. One real
measurement replaces the soft number. Also confirm the session claim that N-scaling is
shallow relative to grid-scaling, because that determines whether "more agents" is a
cheap lever (see OWE-11).

### 1.1 Configs to benchmark

Use the current committed model state (v5.1 post-opt if the optimisation pass landed;
otherwise post-audit — state which in the report). Static world, C strategy, seed=42,
500 steps, same abort rule as prior benchmarks (abort any run > 20 min, skip larger).

| ID | Grid | N | Purpose |
|---|---|---|---|
| T1 | 100×100 | 2000 | **The target geometry.** Primary number. |
| T2 | 100×100 | 3000 | N-scaling probe at fixed grid (cheap-lever test). |
| T3 | 100×100 | 4000 | N-scaling probe, upper. |
| T4 | 110×110 | 2000 | One grid-step up at fixed N (grid-vs-N trade surface). |
| T5 | 120×120 | 2000 | Second grid-step up. |

### 1.2 Report

- ms/step for each config that ran.
- **N-exponent** fitted across T1/T2/T3 (fixed grid, varying N).
- **Grid-exponent** fitted across T1/T4/T5 (fixed N, varying grid).
- Confirm or refute: "N-scaling is shallow; grid-scaling is steep" (session claim,
  based on B1→B2 ≈ +16% for 2× N vs B2→B3 ≈ 3× for grid 100→150).
- State explicitly whether T1 (the target) ran under the 20-min abort or was skipped.

---

## 2. Task 2 — Re-derive carrying capacity for 100×100 (correctness gate)

**Why:** `N_carry` is locked at **400**, set for a **50×50** world (Stage 4.5 Task 0).
The target world has **4× the cells**. If `N_carry` scales with grid area the new
ceiling is ~1600 and **N=2000 would be ABOVE carrying capacity** — the population would
crash on initialisation regardless of strategy, contaminating every downstream H1(ii)
reading. This must be settled before calibration, not after.

### 2.1 Determine the scaling rule actually in code

```bash
grep -rn "N_carry\|carry_discount\|N_carry_proportional\|grid_area" src/ --include="*.py" | grep -v test_
```

Report: is `N_carry` a hard constant (400) or already grid-area-scaled? The perf
benchmarks reference "N_carry proportional to grid area" as a *scaling rule* applied at
benchmark time — confirm whether that rule lives in the model/config or only in the
benchmark harness. State which.

### 2.2 Compute the 100×100 ceiling

If area-scaled: N_carry(100×100) = 400 × (100×100)/(50×50) = **1600**.
Report the value the code actually produces for a 100×100 config.

### 2.3 Correctness gate (MANDATORY)

Run T1's config (100×100, N=2000, C, static, seed=42, **2000 steps** — long enough to
see an init transient settle) and report N(t).

- **PASS:** N=2000 sits at a sensible fraction of carrying capacity (population settles
  to a quasi-steady band *below* the ceiling, leaving headroom for a cycle's boom
  phase). Report the settled N and the ratio settled-N / N_carry.
- **FAIL:** population crashes monotonically from init (N=2000 > capacity) OR pins at the
  ceiling with no headroom. If FAIL → **stop before Task 3** and report the corrected
  initial-N (or corrected N_carry) needed to place the population below capacity with
  boom headroom. Do not proceed to calibration on a geometry that crashes on init.

This is a population-ecology gate: we must be able to attribute a trough-phase band
extinction to the *modelled mechanism*, not to starting above carrying capacity or to
finite-size drift (see OWE-12, minimum-band-size diagnostic — register, do not run here).

---

## 3. Task 3 — OWE-1 proper: assign physical units under the monthly-step constraint

**Route A is LOCKED (supervisor decision, 2026-05-30):** we declare the existing locked
step to **BE one month**, preserving all Stage 4.x locked science. We do NOT rescale
rates and we do NOT reopen locked parameters. The anchors are therefore *solved for*
under the monthly-step constraint — they are not free choices.

**⚠️ STANDING CONSTRAINT (write into MODEL_SPEC §9 verbatim):** *Temporal resolution is
changeable, but any change requires full recalibration — every per-step rate
(`growback_alpha`, metabolism, `p_fission_Si`, `p_max_C`, pool contribution, etc.) must
be rescaled by the duration ratio AND the key locked findings (H1(ii) inversion, T*,
A*) must be re-confirmed at the new resolution. Resolution is not a free knob; it is a
calibration-defining commitment. The current commitment is: 1 step = 1 month.*

### 3.1 Empirical anchors (verified this session)

| Anchor | Value | Source | Use |
|---|---|---|---|
| Forager day-range | ♀ ~8 km/day, ♂ ~14 km/day; Aché ~10–12 km/day | Pontzer Hadza GPS; Hill Aché | Cell-size sanity (NOT a per-step gate at monthly res — see 3.3) |
| Total daily energy expenditure (TEE) | ~1800–2500 kcal/day (~2000 working) | Pontzer et al. 2012 (doubly-labeled water, Hadza) | Metabolic-unit → kcal anchor |
| Forager home-range | !Kung ~100 km²; Chumash density ~21.6 persons/mi² (high-⟨ρ⟩ endpoint) | H-G synthesis | **Home-range validation gate (the live gate at monthly res)** |

### 3.2 Fixed geometry inputs (supervisor-committed, 2026-05-30)

- Grid: 100×100 cells.
- Cell length target: ~10 km (→ ~10×10 km cell, ~1000×1000 km world ≈ 10⁶ km²).
- Agents: ~2000 (subject to Task 2 gate), → 20–60 ethnographic bands.
- Step: 1 month (Route A).

### 3.3 The calibration logic — home-range gate, NOT day-range gate

At monthly resolution, within-step movement is **sub-grid and unobserved**: a step spans
~30 days × ~10 km/day ≈ ~300 km of potential travel, far exceeding one cell. **Day-range
is therefore abstracted below the step and is NOT a valid per-step validation gate.** Use
it only as a coarse sanity check on cell-size (a ~10 km cell is the right *order* for a
day's foraging reach), not as an emergent quantity to match.

**The live gate is emergent HOME-RANGE** — the territory an agent occupies over a season-
to-year — which IS observable at monthly resolution and IS the right scale to compare
against forager territory (~100 km² order).

**Home-range is legitimately JOINT (foraging + social), and that is empirically correct.**
Forager home-range is foraging-driven in distribution but socially modulated in realisation
(camp location, kin proximity, central-place provisioning). The model's movement utility
already reads a **C-side agent-proximity (ψ) social term** alongside the foraging/sugar
gradient (MODEL_SPEC §1.1 ψ row: C reads proximity-to-agents; the Si foraging-proximity
variant is deferred/inactive). So the emergent home-range is the joint product of foraging
pull + social pull — as it should be. **Do not attempt to isolate a foraging-only range.**

### 3.4 Reference configuration for the gate (pre-committed — do not tune away divergences)

Validate the calibration on **ONE pre-committed reference**: the **C arm, static
(unshocked) world, medium-⟨ρ⟩**. Rationale: C is the socially-embedded arm, and forager
ethnography (Hadza/Aché/!Kung) *is* socially-embedded foraging, so C-on-medium-static is
the closest analogue to the data we anchor to.

**CRITICAL — calibration honesty rule:** Anchor cell-size and metabolic-unit so the
**C-static-medium** emergent home-range lands in the forager band (~100 km² order). Then:
- **C-vs-Si home-range differences** are RECORDED AS EMERGENT OUTPUTS, never used to adjust
  the anchors.
- **Across-⟨ρ⟩ home-range differences** are likewise recorded, not tuned.
Tuning the world until the C/Si social-movement difference disappears would erase exactly
the signal H1(ii) and orthogonality exist to detect. The gate is "C-static-medium hits the
band," NOT "both arms hit the band."

### 3.5 Procedure

1. Define an **emergent home-range estimator** (metrics, diagnostic-only, logged not gating
   the sim): per-agent area covered over a rolling window (e.g. convex hull or occupied-cell
   count over the agent's lifetime, in cells → km²). Report population median and IQR.
2. Run the reference config (C, static, medium-⟨ρ⟩, seed=42, ≥2000 steps post-transient).
   Measure median home-range in cells.
3. Solve cell-length ℓ (km/cell) so median home-range × ℓ² lands in the ~100 km² forager
   band. Report ℓ. Sanity-check ℓ against the ~10 km target and against the day-range order.
4. Solve metabolic-unit → kcal: anchor the per-step metabolic debit (m_i drain) to TEE.
   At 1 step = 1 month, per-step debit ↔ ~30 × daily TEE ≈ ~60,000 kcal/agent/month for a
   ~2000 kcal/day forager. Report the implied kcal-per-metabolic-unit and per-sugar-unit.
5. Report whether ℓ (from home-range) and the cell-size implied by the day-range sanity
   check are mutually consistent (order-of-magnitude). A gross inconsistency is itself a
   finding — report it, do not force it.

### 3.6 Movement-decomposition diagnostic (REGISTER + note for build — OWE-13)

Per supervisor (2026-05-30): when the movement instrumentation is built, **implement a
movement-decomposition diagnostic** logging, per agent per step, how much of realised
displacement is attributable to foraging-pull (sugar gradient) vs social-pull (ψ agent-
proximity term). This is nearly a direct measure of one difference-set axis (feeds OWE-8
enumeration and H-ORTHOGONALITY) and directly informs MODEL_SPEC §217 open decision 1
(ψ channel: cultural vs physical).

**This blueprint does NOT build it** (it is a metrics addition for the movement-
instrumentation stage). Register it as OWE-13 in ROADMAP Owed (§6 below) AND note it in
MODEL_SPEC §9 as a planned diagnostic, so it is captured in two tracked places per the
§2 rule. Do not let it evaporate into chat.

---

## 4. Task 4 — Report the implied timescale + full-matrix compute budget

Pure report. **Do NOT rescope H-EMERGE-1 or adjust run-lengths here** (Handoff §7
discipline — report the consequence, let the supervisor decide the rescope).

### 4.1 Timescale table

Using 1 step = 1 month, report for standard/affordable run-lengths:

| Run length (steps) | Simulated duration (yr) | Secular cycles contained (@~250 yr/cycle) | Wall-clock/seed @ measured ms (Task 1) |
|---|---|---|---|
| 10,000 | 833 | ~3.3 | ? |
| 12,000 | 1000 | ~4 | ? |
| 24,000 | 2000 | ~8 | ? |

Fill the wall-clock column from the **measured** T1 ms/step, not the interpolated 130 ms.

### 4.2 Phenomenon adequacy (state explicitly, pass/fail each)

For monthly resolution, confirm each samples adequately (characteristic timescale ≫ step):
secular cycles (~250 yr) ✓; asabiyyah rise/decay (decades) ✓; demographic generations
(~25–30 yr ≈ ~300–360 steps) ✓; seasonal-to-multiseasonal shocks (the A axis) — state the
shock period in steps and confirm ≥ ~12–26 steps/period (above Nyquist). Note that
sub-monthly shocks are **out of scope by design** (absorbed by the buffer mechanism;
supervisor decision 2026-05-30).

### 4.3 Full-matrix campaign budget

For the sweep matrix ⟨ρ⟩ × A × T × seeds × {C, Si}: state assumed cell counts per axis,
total run count, and wall-clock at 4 workers using measured ms/step, for monthly resolution
at the chosen standard run-length. Report as a single campaign-hours figure with the
resolution sensitivity noted (fortnightly ≈ 2× monthly for identical science).

### 4.4 H-EMERGE-1 consequence (flag only)

State in one paragraph what timescale/structure the chosen standard run reaches and whether
it is adequate for secular-cycle *emergence* (needs ≥ several cycles). **Flag** the
consequence for H-EMERGE-1 run-length adequacy; do **not** change any run-length in this
blueprint.

---

## 5. Report format

HTML: `outputs/owe1_calibration/report_owe1.html`

- **§0 Model state** — which committed version (post-audit / post-opt); test count; git ref.
- **§1 Target-geometry benchmark** — Task 1 table, N-exponent, grid-exponent, claim verdict.
- **§2 Carrying-capacity gate** — N_carry scaling rule found in code; 100×100 ceiling;
  settled-N/N_carry ratio; PASS/FAIL with corrected init-N if FAIL.
- **§3 Absolute-scale calibration** — ℓ (km/cell), kcal-per-unit, home-range gate result
  (C-static-medium median home-range in km² vs forager band); C-vs-Si and ⟨ρ⟩ home-range
  divergences recorded as outputs; day-range/home-range consistency check.
- **§4 Timescale + budget** — Task 4 tables; phenomenon-adequacy pass/fail; campaign hours;
  H-EMERGE-1 flag.
- **§5 Doc-fold-in** — what was appended/skipped/conflict-flagged in each live doc
  (ROADMAP, MODEL_SPEC §9 created, HYPOTHESES registrations). List any CONTRADICTORY
  entries surfaced and STOPPED on.

---

## 6. Owed items registered this session (fold into live ROADMAP "Owed")

| ID | Item | Status | Notes |
|---|---|---|---|
| OWE-11 | **Larger-N feasibility** | OPEN — measured in Task 1 | N-scaling is cheap relative to grid (confirm via T1/T2/T3 exponent). If larger N is desired and Task 2 shows N_carry headroom, larger N may not need recalibration — but VERIFY against the §3 standing constraint (anything that shifts per-step dynamics does). Decide after Task 1+2 numbers. |
| OWE-12 | **Minimum-band-size-in-trough diagnostic** | OPEN — design | In deep secular-cycle troughs, per-band N can fall into the finite-size/Allee regime, contaminating H1(ii) terminal extinction readings with drift. Add a diagnostic logging min-band-size across seeds in trough phase; if finite-size-driven, raise N (cheap per OWE-11) or floor band size. Do not run here; register. |
| OWE-13 | **Movement-decomposition diagnostic** | OPEN — build at movement-instrumentation stage | Per-agent per-step decomposition of displacement into foraging-pull vs social-pull (ψ). Near-direct measure of one difference-set axis; feeds OWE-8 + H-ORTHOGONALITY; informs MODEL_SPEC §217 decision 1 (ψ channel). See §3.6. |

---

## 7. Success criteria

| Criterion | Target |
|---|---|
| Target geometry benchmarked directly | T1 (100×100, N=2000) ms/step measured, not interpolated |
| N- and grid-exponents reported | Both fitted; cheap-lever claim adjudicated |
| N_carry scaling rule identified in code | Constant vs area-scaled stated |
| Carrying-capacity gate run | PASS (headroom) or FAIL (+ corrected init-N) |
| Calibration on pre-committed reference only | C-static-medium; divergences recorded not tuned |
| Home-range gate result reported | Median home-range km² vs ~100 km² forager band |
| Cell→km and unit→kcal reported | ℓ and kcal-per-unit stated with consistency check |
| Timescale + cycles-contained table | Filled from measured ms/step |
| Phenomenon-adequacy pass/fail | Each mechanism vs monthly step |
| Campaign budget | Full-matrix wall-clock at 4 workers |
| Doc fold-in executed | ROADMAP/MODEL_SPEC §9/HYPOTHESES; conflicts surfaced not auto-resolved |
| OWE-11/12/13 registered | In live ROADMAP Owed |

---

## 8. Out of scope

- Any rescaling of locked per-step rates (Route A: step ≡ month, no rescale).
- Reopening locked parameters (k_grid, β_Si, N_carry value itself unless Task 2 FAILS,
  etc.) — Task 2 may CORRECT N_carry for the new grid if the code uses a stale constant,
  but that is a geometry-consistency fix, not a science retune; flag it as such.
- Running any H-ORTHOGONALITY / instinct-debt test (registration only this pass).
- Building the movement-decomposition diagnostic (OWE-13, later stage).
- Changing temporal resolution (locked at monthly; changing it = full recalibration).
- Rescoping H-EMERGE-1 run-lengths (flag the consequence only).

---

*End of OWE-1 Absolute-Scale Calibration Blueprint — 2026-05-30.*
