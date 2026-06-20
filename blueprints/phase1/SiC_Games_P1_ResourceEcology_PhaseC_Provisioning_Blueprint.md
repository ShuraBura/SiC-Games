# SiC Games · Phase 1 · Resource-Ecology **Phase C — Provisioning / Dependency**

**Status:** DRAFT for red-team (2026-06-20). The empirically-forced unblock from R-6/R-7/R-8.

---

## 1. Why this stage (the forcing argument)

Three experiments converge (RESULTS R-6, R-7, R-8):

| stage | lever | result |
|---|---|---|
| A.1 | seasonality | only lowers the CC to the lean-season bottleneck; everyone fed |
| A.2 | depletion | only lowers the CC further; cells stripped to f=0.32, **0% under-fed** |
| B | constrained movement | clean mobility knob, but **0% under-fed at every level**, occupancy invariant |

**Diagnosis (R-8):** the demographic `a2` modulators (synergy, density-disease) need a *sustained* "chronically lean but alive" population to act on. The food economy can't produce one for **self-feeding adults** — under the (near-)bang-bang reserve an adult is either fed (intake ≥ burn → reserve pinned at the 100k cap → synergy 1) or culled (intake < burn → floor in ~1 step). No mean-lowering or spatial mechanism manufactures the lean band. **Only DEPENDENTS** — who cannot forage to maintenance, are partially provisioned, and drain slowly — can occupy it.

**Current state (the gap):** in the demographic path `_use_eta` is **off**, so `is_juvenile()` is always False and **newborns forage at full adult capacity**. There is *no childhood dependency at all*. That is exactly why the core is stable *and* why no dependent class exists. Phase C introduces the dependency.

**This stage is also the T-4 prerequisite:** emergent nutritional child mortality (TARGETS T-4) *is* the synergy acting on under-provisioned children — validated against the Aché child-mortality schedule.

---

## 2. Mechanism

Three coupled pieces, each lit-anchored, reusing the dormant life-history scaffolding.

### C.1 — Age-graded production AND consumption (the childhood deficit)
- **Production** (exists): own intake `= η(age) · harvest_share`, with `η(a)` the base.py ramp. Replace the **binary** juvenile gate (`intake=0` below `forage_age_min`) with the **graded** `η` curve (this is the deferred **JV-1**). Anchor `eta_min`, `forage_age_min`, and curve shape to the **Kaplan, Hill, Lancaster & Hurtado 2000** net-production-by-age data (Aché/Hiwi/Machiguenga): children produce ≈0 until ~5 yr, rising, net-positive only at **~18–20 yr**; peak male production ~30–45 yr.
- **Consumption** (new): age-scale `burn` — a child's maintenance is below an adult's (metabolic body-mass scaling + activity). Anchor to the **consumption-by-age** curve (same Kaplan 2000 / FAO requirements): child requirement ramps ~0.3→1.0 across childhood. New `burn(age) = burn_adult · c(age)`.
- **Net deficit** `= burn(age) − η(age)·share` is **positive through the whole juvenile period** — the Kaplan "downward transfer" the band must fund.

### C.2 — Provisioning (transfers fund the deficit)
- Each step, after harvest, adults on a cell that ate to maintenance contribute their **surplus** (reserve above a target band) to a **provisioning pool**; dependents (juveniles; optionally elders via `is_elder`, pregnant/lactating via a requirement bump) draw from it to cover their deficit, up to availability.
- **Topology decision (red-team Q):** start with **cell-pooled** provisioning (everyone on a cell shares — matches the existing within-cell scramble and band-sharing norms; Kaplan-Hill reciprocity), NOT mother-only. Mother-linkage is a later refinement (FD-1) if cell-pooling over-smooths.
- **The bite:** on a lean/depleted cell the adult surplus shrinks → the pool can't cover the child deficit → children draw down their reserve → **dwell lean** (the graded reserve the bang-bang adult economy lacked) → synergy/disease grade their mortality.

### C.3 — Graded child reserve (the lean band)
- A partially-provisioned child has intake ∈ (0, requirement) → **slow** reserve drain → it lingers in the synergy zone rather than dying in one step. This is the structural fix for the bang-bang limiter (R-8). No new mechanic — it falls out of C.1+C.2 once intake is graded.

---

## 3. Knobs & anchors (all → MODEL_SPEC §4.x methods, with citation)

| knob | meaning | anchor |
|---|---|---|
| `forage_age_min` | age own-production reaches adult | Kaplan 2000 net-positive ~18–20 yr |
| `eta_min`, η shape | child production fraction | Kaplan 2000 production-by-age (Aché) |
| `c(age)` consumption ramp | child maintenance fraction | Kaplan 2000 / FAO requirement-by-age |
| provisioning target band | surplus threshold adults share above | derived so adults stay fed (≈ reserve_full band) |
| `mu_max` (synergy) | the ONE free knob | **calibrated so emergent child mortality = Aché (T-4)** |

`mu_max` is finally calibratable here (R-5 said it couldn't be until nutritional variance existed). Seasonality + depletion (A) stay as the CC backdrop; `move_cost ≈ 0` (B, the realistic setting).

---

## 4. Gate / validation (T-4)

**Pre-registered:** with C.1+C.2 on and `mu_max` calibrated, the **emergent** age-specific child mortality (q(x) for x < 15 yr) reproduces the Aché forest schedule (Hill & Hurtado 1996 Ch. 6 / Gurven & Kaplan 2007 l(x)) **within tolerance**, WITHOUT the child-mortality being hard-coded into the Siler `a1` term. Per the mean-preservation procedure (TARGETS T-4): remove the nutritional component from baseline `a1`/`a2`, let provisioning-driven synergy re-supply it, compare. PASS = the emergent curve matches; FAIL = STOP, report.

**Secondary checks:** population still bounded (no collapse / explosion); adults remain fed (the variance lands on dependents, not the whole population); seasonal/depleted cells show elevated child mortality (the mechanism signature).

---

## 5. Staging

- **C.1** — graded η production + age-scaled consumption, provisioning OFF → confirm children now carry a deficit (and, without provisioning, a child-mortality wall appears). Baseline.
- **C.2** — provisioning ON (cell-pooled) → confirm the deficit is funded in good conditions and the band appears in lean/depleted ones (under-fed fraction among *juveniles* > 0; adults still ~0).
- **C.3 / T-4** — calibrate `mu_max`; validate emergent child mortality vs Aché. Gate.

---

## 6. Red-team risks (to harden before build)

1. **Cell-pooling over-smooths** → no child ever goes hungry (variance washed out again, like the IFD). *Mitigation:* pool is finite (only true surplus); on a lean cell it's empty. Measure juvenile under-fed fraction by cell condition. If still smooth, escalate to mother-linked provisioning (FD-1).
2. **Age-scaled burn re-introduces a free parameter that just re-tunes the CC.** *Mitigation:* `c(age)` is fixed from FAO/Kaplan, not tuned; only `mu_max` is free, and it's pinned by T-4.
3. **The graded-η change breaks the validated demographic core** (it's been running with children-as-adults; turning on dependency could destabilize the population or change vital rates). *Mitigation:* C.1 staged separately; re-run the 2a-pre stability + Step-1 vital-rate checks; treat any vital-rate drift as a gate. The 444-suite must stay green (opt-in via lh_config, as today).
4. **Determinism / performance** — provisioning is a new per-cell reduction each step. *Mitigation:* O(occupants) per cell, same shape as the harvest split; reuse `occ_lists`. Keep RNG-free (deterministic pool split).
5. **Double-counting maternal load** — maternal mortality is already folded into the female schedule (approach ii); pregnant/lactating requirement bump must not re-bill it. *Mitigation:* requirement bump affects *consumption/provisioning demand* only, not mortality.

---

## 7. Out of scope (deferred)

- Mother/kin-linked provisioning topology (FD-1) — only if cell-pooling over-smooths (risk 1).
- Sexual division of labour in provisioning (male game → offspring) — game stream is off here.
- Full depletion economy (D, CC-1-gated) — A stays depletion-lite backdrop.
- The realistic non-linear Kaplan production curve if the linear η proves too coarse for T-4.
