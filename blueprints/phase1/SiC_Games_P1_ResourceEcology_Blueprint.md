# SiC Games — Phase 1 Resource-Ecology Stage Blueprint
## Nutritional variance: seasonality → per-class reserves → family/provisioning → (depletion)

**Status:** DRAFT — for supervisor review and an independent red-team pass before any code.
**Created:** 2026-06-19
**Phase:** 1. Precursors: the demographic stage (Siler + IBI + the wired-but-INERT `a2` modulators),
RESULTS R-5 (the modulators are inert on the constant economy; they need nutritional *variance*),
TARGETS T-4 (emergent nutritional child mortality), DEFERRED_MECHANICS GD-1/CL-1/MR-1/MR-2/FD-1.

---

## 0. The ONE question

> "What economy gives the demographic `a2` modulators **nutritional variance** to act on — so the
> population regulates *below* the food ceiling at a realistic density, `μ_max` becomes calibratable,
> and the **T-4 emergent-child-mortality** validation becomes possible — without over-tuning?"

Today the economy is a **constant, undepletable, aseasonal faucet**: every cell offers `E = K·burn`
every step, agents spread food-rationally and stay fully fed, so synergy = 1, density ≈ 1, risk ≈ 1.
The demographic mechanisms are validated but **dormant**. This stage supplies the variance that makes
them live.

**Design principle (the anti-overtune rule, supervisor 2026-06-19):** design the economy as a *coherent
whole*; do NOT hand-tune movement/spreading in isolation (movement realism should *emerge* from
depletion, not be fitted to compensate for its absence). Calibrate against data, not against symptoms.

---

## 1. The four components (one coherent economy)

| # | Component | What it adds | Deferred-mech |
|---|---|---|---|
| **A** | **Seasonality** | a lean season where forage drops below maintenance → reserves fall → synergy/starvation bite. The *primary, cheapest* variance source. | CL-1 |
| **B** | **Per-class reserves** | per-agent `reserve_full ~ N(sex×age)` → differential vulnerability under scarcity (children starve first; women buffer best). | MR-1 |
| **C** | **Family / provisioning** | family unit co-resides; children provisioned by mother until maturation → maternal nutritional load + child dependency. | FD-1 / MR-2 / JV-1 |
| **D** | **Depletion** | local resource stock drawn down by harvest + regrowth → spatial scarcity + emergent mobility. The biggest; likely its own sub-stage. | GD-1 |

They interact: seasonality + depletion create *when/where* scarcity happens; per-class reserves set
*who* is vulnerable; family/provisioning sets *how* scarcity propagates (mother → children).

---

## 2. Phased build (coherent design, incremental delivery)

Each phase is runnable and gated, but designed knowing the others (so no phase hand-tunes around a
missing one).

- **Phase A — Seasonality (the unblock).** A seasonal multiplier `s(t) ∈ [s_min, 1]` on the cell harvest
  so a lean season pushes `S/n` below `burn` for a stretch → reserves draw down → **synergy and
  starvation finally vary**. Scaffolding exists: the seasonal-oscillation mechanic + the resource-layer
  seasonal signal (MODEL_SPEC §4.1.4–4.1.6) + the CL-1 climate seam. Amplitude lit-anchored (De Vynck
  fynbos, Hurtado Hiwi seasonality — both filed). **Gate:** synergy is no longer flat (a distribution of
  `synergy_mult` appears in the lean season); the population settles *below* the food ceiling; CDR in the
  Aché band; `μ_max` now has something to calibrate against.
- **Phase B — Per-class reserves (MR-1).** `reserve_full ~ N(mean_class, sd_class)` by sex×age, lit-anchored
  (women > men absolute fat; children low; seniors decline). **Reconcile against the all-cause Siler** to
  avoid M-3-style double-counting (the reserve/nutrition channel = scarcity *deviation*, not a restatement
  of the average sex/age mortality already in the Siler). **Gate:** realistic differential seasonal
  mortality (children & lean adults first), without breaking the Aché aggregate l(x).
- **Phase C — Family / provisioning (FD-1/MR-2/JV-1).** Family unit (mother + dependent children) co-resides
  & moves together; children provisioned (don't self-forage) until maturation. **Gate:** child survival
  tracks maternal condition; family structure produces realistic local aggregation (which finally makes
  density-disease meaningful).
- **Phase D — Depletion (GD-1).** Cell stock drawn down + regrowth → mobility. **Likely a separate stage**
  (its own regrowth calibration); scoped here for coherence but built last / separately.

---

## 3. Calibration targets (what "right" means)

After Phases A–C, on the seasonal economy:
1. **Demographic carrying capacity BELOW the food ceiling**, at an ethnographically realistic density
   (~0.1–0.3 / km²), set by the *combined* mortality (seasonal undernutrition + baseline), not by the
   bare food wall.
2. **`μ_max` calibrated** so the synergy contribution makes the seasonal mortality pulse + the equilibrium
   density match the Aché — the first time μ_max is meaningfully calibratable.
3. **CDR in the Aché stationary band** (~40–60 / 1000 / yr) at r ≈ 0; the aggregate l(x) still reproduces
   the Aché (Phase B must not break it).
4. **Seasonal mortality pulse** realistic (lean-season death spike), per the ethnographic seasonality.
5. **Capstone — TARGET T-4:** decouple the nutritional fraction of child mortality from the Siler (keep
   the H&H non-nutritional residual), let it emerge from B+C under A's scarcity, and compare emergent
   child mortality to the Aché schedule.

---

## 4. Seams & code-touch map

- **Seasonality (A):** a `season_multiplier(step)` applied to the harvest field's `level()` (or a wrapper
  capacity field), period = 12 steps (1 yr), amplitude lit-anchored. Reuses the seasonal signal
  architecture; no agent-side change.
- **Per-class reserves (B):** `_make_agent` draws `reserve_full` from the class distribution (sex known;
  age-class from age); the synergy/starvation already read `reserve` relative to per-agent `reserve_full`.
  New `DemographyConfig`/`KcalEconomyConfig` per-class params.
- **Family/provisioning (C):** `_do_births_ibi` links child→mother; a family-cohesion movement (child
  inherits mother's target until maturation); provisioning routes child subsistence through the mother
  (JV-1 age-gate + MR-2). New state: `mother_id`, `dependent` flag.
- **Depletion (D):** the harvest field becomes a mutable stock + regrowth kernel (GD-1 seam).
- **Harnesses:** `outputs/phase1_resource_ecology/` — per-phase runs + the T-4 validation.

---

## 5. Open decisions / dependencies

| Item | State |
|---|---|
| Seasonal amplitude `s_min` | lit-anchor from De Vynck / Hurtado seasonality (filed); pin in Phase A |
| Per-class reserve means/sds | body-composition lit; HG anthropometry (Aché/Hadza) if available — may need a fetch (`sci-hub-paper-downloader`) |
| Siler ↔ nutrition reconciliation | the M-3-style split: nutrition = scarcity deviation, not restated average (Phase B) |
| Depletion regrowth rates | GD-1 — likely a separate stage |
| Movement | **do NOT hand-tune** — realism emerges from depletion (Phase D), not Phase A/B/C |

---

## 6. Independent-review checkpoint (required before code)
Per the standing workflow: an independent, repo-grounded red-team + supervisor review this plan before
implementation. Focus: (a) is seasonality the right first unblock, or must depletion come first? (b) is
the Siler↔nutrition reconciliation (B) actually double-count-free? (c) are the calibration targets
falsifiable and sufficient? (d) does the phasing avoid the over-tune trap? (e) scale/perf realism.

---

*Resource-Ecology Stage · DRAFT 2026-06-19 · Phase 1 · supplies the nutritional variance that makes the
demographic modulators live; phased A (seasonality) → B (per-class reserves) → C (family/provisioning) →
D (depletion, likely separate); capstone = T-4 emergent child mortality. Anti-overtune: design whole,
don't hand-tune movement.*
