# SiC Games — Phase 1 Resource-Ecology Stage Blueprint (v2)
## Nutritional variance: seasonality × depletion → per-class reserves → family/provisioning

**Status:** DRAFT **v2** (independently red-teamed 2026-06-19; v1 verdict: NOT implementable as written —
revised). For supervisor review. Dispositions in §7.
**Phase:** 1. Precursors: demographic stage (Siler + IBI + INERT `a2` modulators), RESULTS R-5 (modulators
need nutritional *variance*), TARGETS T-4, DEFERRED_MECHANICS GD-1/CL-1/MR-1/MR-2/FD-1.

---

## 0. The ONE question

> "What economy gives the demographic `a2` modulators **nutritional variance** to act on — so the
> population regulates *below* the food ceiling at a realistic density, `μ_max` is **identified** (not
> just adjustable), and the **T-4 emergent-child-mortality** validation becomes possible — without
> over-tuning?"

**The central mechanism insight (red-team A/E):** seasonality alone is **not** the unblock. On an
*undepletable* per-step flow, a seasonal multiplier doesn't trap anyone — agents re-spread to whatever
cell/biome is currently in-season and stay fed, exactly as they dodged density-disease. **Depletion is the
load-bearing mechanism: it's the *trap* that makes an agent actually experience scarcity.** Seasonality
supplies *when* scarcity can happen; depletion supplies *that it cannot be cheaply fled.* So the unblock is
**seasonal flow × a depletable local stock, together** — not seasonality first and depletion "someday."

**Anti-overtune rule (supervisor):** design the economy as a coherent whole; do NOT hand-tune
movement/spreading to fake a missing trap (that's tuning around absent depletion). Pin parameters from
literature; leave exactly one free knob per gate.

---

## 1. Components (one coherent economy)

| # | Component | What it adds | Deferred-mech | Note |
|---|---|---|---|---|
| **A** | **Seasonal flow × depletion-lite (TOGETHER)** | a lean season *and* a depletable local stock → an agent in a depleting catchment can't cheaply flee → reserves actually draw down per-agent. The real unblock. | CL-1 + GD-1 | A is **net-new TerrainField code** (red-team B) |
| **B** | **Per-class reserves** | per-agent `reserve_full ~ N(sex×age)` → differential vulnerability (children starve first; women buffer). | MR-1 | **hard data prereq** (body-comp) |
| **C** | **Family / provisioning** | family co-resides; children provisioned by mother to maturation → maternal load + child dependency. | FD-1/MR-2/JV-1 | O(N) cohesion pass |
| **(D)** | **Full depletion (calibrated stock + regrowth)** | the real extractable-rate dynamics + mobility. | GD-1 | **its own stage — blocked on CC-1** (red-team F) |

---

## 2. Build (revised order — depletion is the unblock, not the finale)

- **Phase A — Seasonal flow × depletion-lite (net-new, small grid, forage-only).**
  - **Net-new code (red-team B):** the Sugarscape `SeasonalOscillation` is hard-wired to `SugarField`
    (`.capacity`/`.effective_capacity`/`growback`), which `TerrainField` LACKS — it cannot be reused. Build
    a `season_multiplier(step)` factor on the harvest field's `level()` (forage-only; game's seasonality is
    a *different* threshold mechanism — MODEL_SPEC §4.1.5 — out of scope for A).
  - **Depletion-lite:** the cell holds a **provisional stock** (a multiple of `S`) drawn down by harvest and
    regrowing per step. **PROVISIONAL** and tagged so (GD-1: depletion without the CC-1 ceiling is
    placeholder-on-placeholder; the real stock magnitude is CC-1 / its own stage). The point of A is *not* a
    calibrated carrying capacity — it's to test the trap.
  - **Gate (the real test, red-team A/E):** an agent in a lean+depleting catchment **gets trapped** — reserves
    draw down *per agent* (verify NO cheap re-spread escape) → a **per-agent distribution of `synergy_mult`
    appears**, not a time-flat one. If agents still dodge, STOP — the mechanism is wrong, report it.
- **Phase B — Per-class reserves (MR-1).** `reserve_full ~ N(mean_class, sd_class)` by sex×age; thread a
  **per-agent** `reserve_full` into synergy + energetic-fertility + the starvation floor (red-team NIT: these
  currently read the *global* constant — 3 touch points). **Hard prereq:** body-composition means/sds (women
  > men absolute fat; children low; seniors decline) — source from lit (may need `sci-hub-paper-downloader`).
- **Phase C — Family / provisioning (FD-1/MR-2/JV-1).** Family unit co-resides + moves together; children
  provisioned until maturation (O(N) cohesion pass). Creates realistic local aggregation → density-disease
  finally meaningful.

Full depletion **(D)** is split out as its **own stage with a hard CC-1 prerequisite**.

---

## 3. The Siler ↔ nutrition reconciliation — a procedure, not a slogan (red-team C)

The all-cause Aché Siler already prices in *average* undernutrition mortality. The moment Phase A makes
reserves dip, `synergy_mult > 1` fires **on top of** it → an M-3-style **double-count, live in the code.**
Fix = a **mean-preservation constraint** (not a re-fit):
1. **[HARD DATA PREREQ]** From Hill & Hurtado cause-of-death, get the nutritional fraction `f_nut(age)` of
   mortality. **This does not exist in the repo yet** — it must be sourced/extracted before B/T-4.
2. Split the Siler: `h_nonnut(age) = (1−f_nut)·h_Aché` stays painted-in; **remove** `f_nut·a2` from the
   baseline `a2` the synergy multiplies (else you double-count `f_nut·a2` every lean step).
3. Calibrate **`μ_max` (the SINGLE free knob)** so the *emergent* synergy mortality, averaged over the
   seasonal cycle + equilibrium age/reserve distribution, equals `f_nut·a2`:
   `E_cycle[(synergy_mult−1)·a2] ≈ f_nut·a2`. This *replaces* the painted-in nutritional fraction with a
   mechanistic one of **equal mean but seasonal/per-class variance** — double-count-free, and it IS the
   falsifiable T-4 test.

## 4. Calibration discipline — `μ_max` identified, not just adjustable (red-team D)

The DOF problem: `s_min`, depletion rate, `μ_max`, 4×(per-class reserve mean+sd) ≈ 6+ free knobs vs wide-band
targets ⇒ over-parameterized. **Rule: pin everything but `μ_max` from literature first, freeze it, then
`μ_max` is *identified* by the §3 mean-preservation constraint (a point, not a band):**
- `s_min` / seasonal amplitude ← De Vynck fynbos + Hurtado Hiwi seasonality (filed) — **pin a value**.
- per-class reserves ← body-composition lit (Phase-B prereq).
- depletion-lite rate ← provisional (tagged), not calibrated in A.
- Add a **quantitative seasonal-pulse target** (lean/peak CDR ratio from ethnography) so it can fail.
- Gates: r≈0 with CDR in the Aché band; aggregate l(x) still reproduces Aché (guaranteed by mean-preservation,
  §3); the trap gate (§2 Phase A).

## 5. Seams & code-touch map
- **A:** new `season_multiplier(step)` + a depletable-stock wrapper over the CC-1/terrain harvest field
  (`level()`); regrowth kernel. Forage-only. New harness `outputs/phase1_resource_ecology/`.
- **B:** `_make_agent` draws per-agent `reserve_full`; thread it into `synergy_mult`, `energetic_fertility`,
  and the starvation-floor check (3 sites). New per-class params.
- **C:** `_do_births_ibi` child→mother link; family-cohesion movement; provisioning via the JV-1 age-gate + MR-2.
- **D (separate stage):** mutable stock + regrowth, **after CC-1**.

## 6. Hard prerequisites & dependencies (red-team)
| Item | State |
|---|---|
| `f_nut(age)` nutritional cause-of-death fraction (Hill & Hurtado) | **HARD PREREQ for B/T-4 — not yet extracted** |
| per-class body-composition reserve means/sds | **HARD PREREQ for B — source from lit** |
| `s_min` seasonal amplitude | pin from De Vynck/Hurtado (filed) before calibrating μ_max |
| Full depletion (D) | **blocked on CC-1** (RECAL-class) → its own stage; A uses provisional depletion-lite |
| Movement | do NOT hand-tune; the depletion-lite trap is what creates scarcity, not movement tuning |

## 7. Red-team revision log (v2 — independent review 2026-06-19)
v1 verdict: **NOT implementable as written.** Applied:
- **B (BLOCKER) — false "scaffolding exists / reuse / no agent-side change".** TerrainField has no
  capacity/growback; the SeasonalOscillation is Sugarscape-only; MODEL_SPEC §4.1.x is lit-treatment + STUB;
  CL-1 says the seasonal field is DEFERRED. → Phase A re-labeled **net-new TerrainField code** (§2, §5).
- **A/E (MAJOR) — seasonality alone is inert (agents re-spread to dodge scarcity); the over-tune trap is in
  the order.** → **depletion-lite pulled forward to join seasonality in Phase A**; the gate now tests the
  *trap* (no cheap re-spread escape), §2.
- **C (MAJOR) — reconciliation was a slogan + a live double-count.** → the **mean-preservation procedure**
  (§3) with `f_nut(age)` as a hard prereq and `μ_max` removed from the baseline it multiplies.
- **D (MAJOR) — `μ_max` under-determined (6+ free knobs vs wide bands).** → **pin all but μ_max**, point
  constraint not band, + a quantitative seasonal-pulse target (§4).
- **F — depletion needs CC-1; game≠forage seasonality; per-agent reserve_full is 3 touch-points (NIT, code
  was mis-stated); family cohesion O(N).** → full depletion split to its own CC-1-gated stage; A forage-only;
  §5 lists the 3 sites.

**Net:** the component set is right; the *order* and *"reuse"* framing were wrong. Lock gated on: pinning
`s_min`, sourcing `f_nut(age)` + per-class body-comp, and the Phase-A trap gate passing empirically.

---

*Resource-Ecology Stage · DRAFT v2 2026-06-19 (red-teamed) · Phase 1 · the unblock is **seasonal flow ×
depletion-lite together** (depletion is the trap), net-new TerrainField code; B per-class reserves + the
mean-preservation Siler reconciliation (μ_max the single identified knob); C family/provisioning; full
depletion is its own CC-1-gated stage. Hard prereqs: `f_nut(age)`, per-class body-comp, `s_min`.*
