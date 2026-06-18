# SiC Games — Phase 1 Demographic Mechanics Blueprint
## Siler Mortality + IBI Reproduction + Terrain-Modulated Hazard

**Status:** DRAFT — for supervisor review and an independent red-team pass before lock.
**Created:** 2026-06-18
**Phase:** 1 (Terrain & Resource Ecology). Stage number to be assigned by the supervisor.
**Precursor:** A-3 First-Light Shakedown (`SiC_Games_P1_A3_FirstLight_Shakedown.md`) and
`handoffs/SiC_Games_Progress_Report_2026-06-18.md`.

---

## 0. The ONE question

> "What is the smallest literature-anchored set of demographic mechanics that turns the frozen
> carrying-capacity equilibrium into a living population — continuous, balanced birth and death —
> and reproduces a real hunter-gatherer (Aché) life table?"

**Non-goals (explicitly out of scope here):** biparental/Cred-weighted C reproduction (deferred,
stays in Phase-1 demographic-stage 2); Si demography; intergroup violence/warfare; climate-shock
events; game depletion (GD-1); age-graded juvenile yield (JV-1, separate seam). This blueprint is
**C-only, forage-only**, single-population demography on the existing terrain economy.

---

## 1. Motivation — the frozen-equilibrium finding (A-3)

A-3 discovered a clean, placement-independent food-capacity ceiling (~133.4k on 100×100), but at
equilibrium **births and deaths both go to zero**: the only death causes are density-dependent
starvation (transient only) and a hard senescence age-cap (never fires / fires as a synchronized
wave). Real foraging populations sit at carrying capacity with *continuous turnover*. The model
lacks **density-independent baseline mortality** and **literature-anchored fertility**. This stage
supplies both.

---

## 2. The mortality engine — sex-specific Siler competing-hazard

Replace the hard age cap with the **Siler (1979) 3-component hazard**, the standard model for
hunter-gatherer mortality (fit to the Aché by Hill & Hurtado 1996; to the cross-HG composite by
Gurven & Kaplan 2007). Continuous monthly hazard of death at age `a` (in months), per sex `s`:

```
h_s(a) = a1_s · exp(−b1_s · a)      # infant/juvenile decline
       + a2_s                        # age-independent baseline (Makeham)  ← the world modulates THIS
       + a3_s · exp( b3_s · a)       # Gompertz senescence (no hard cap)
```

Per step (1 month) each living agent dies with probability `p = 1 − exp(−h_s(a)·Δ)` where Δ = 1
month (rate→probability conversion; keeps small-rate additivity). Cause attribution keeps the three
terms separable for diagnostics (`deaths_infant`, `deaths_baseline`, `deaths_senesc`), plus the
existing `deaths_starv` (hard energetic floor, retained as a backstop).

**Parameterization (LOCKED to Aché; exact coefficients fit in Step-1 calibration, §9):**
Targets the schedule must reproduce (Hill & Hurtado 1996; Gurven & Kaplan 2007):

| Quantity | Aché / HG anchor |
|---|---|
| Life expectancy at birth e₀ | ≈ 35–37 yr (low — dominated by infant term) |
| Survival to age 15 | ≈ 55–60% |
| Life expectancy at 15, e₁₅ | ≈ 50 further yr (→ modal adult lifespan) |
| Modal adult age at death | ≈ 70–72 yr; **females outlive males ~2–5 yr** |
| Senescence onset | gradual; **NOT a 75-yr cap** — the trap A-3 would otherwise repeat |

> **Demographic trap to avoid:** the ~35-yr "life expectancy" is low *only because of infant
> mortality*. The senescence term must anchor to **modal adult death (~70)**, not the ~35 mean,
> or the population dies decades too young.

---

## 3. Baseline modulation — the `a2` term is where the world acts

The infant (`a1`) and senescence (`a3`) terms are intrinsic and fixed by sex. Only the **baseline
`a2`** is modulated by environment and density, via independent multipliers, each behind its own
flag so effects can be decoupled in analysis:

```
a2_eff = a2_s · R(cell)^[flag_risk] · D(ρ)^[flag_density] · P(cell)^[flag_pathogen] · M(reserve)^[flag_synergy]
```

With every flag off, `a2_eff = a2_s` (pure Aché schedule). Each component:

### 3.1 Terrain accident/exposure risk — `R(cell)` (flag: `enable_terrain_risk`)
Wire the **already-computed but dormant** terrain `risk` field (`terrain.py:494`, range [0.02, 1];
exposure + thirst − shelter, water = 0.85). It encodes physical/accident hazard, **not disease**.
Normalize so an average-risk land cell ≈ 1.0: `R(cell) = risk(cell) / risk_ref`, where
`risk_ref` = mean land risk (a **free knob**, calibrated in Step 2).

### 3.2 Density-dependent disease — `D(ρ)` (flag: `enable_density_disease`)
Crowding raises transmission. Driven by **within-cell occupancy** `ρ` (simplest defensible scale),
saturating:  `D(ρ) = 1 + δ · ρ / (ρ + ρ_half)`. `δ` (max excess) and `ρ_half` are **free knobs**.
Gives a second density-dependent population check beyond starvation.

### 3.3 Terrain pathogen field — `P(cell)` (flag: `enable_terrain_pathogen`, **OFF by default**)
A **new** terrain field, separate from `risk`. **Least literature-anchored piece** — there is no
HG disease-ecology paper in the lit folder yet, and terrain has no temperature field. Provisional
form, pending the open lit search (§10):

```
pathogen ∝ wateracc (standing water → malaria/waterborne)
         + wetland indicator
         + low-elev/high-npp warmth-proxy
         − aridity
```
Ships **off** and sensitivity-tested until anchored. If adopted, wetlands become a
productivity-vs-disease tradeoff. Terrain-generator change (`terrain.py`).

### 3.4 Nutrition × disease synergy — `M(reserve)` (flag: `enable_nutrition_synergy`)
Undernutrition amplifies infectious mortality (the dominant real HG death pathway is *infection in
the malnourished*, not outright starvation). Multiplier rising from 1 at full reserve to `μ_max`
(≈2–3) near the floor: `M(reserve) = 1 + (μ_max − 1)·(1 − clamp((reserve − floor)/(full − floor)))`.
Hard starvation (`reserve ≤ floor`) retained as the backstop. **Run coupled vs decoupled** to
isolate the synergy's effect on equilibrium turnover.

---

## 4. Reproduction — female-only, IBI-gated (replaces the reserve threshold)

The kcal reserve-threshold is the wrong primitive. Reframe to the real HG fertility drivers
(Hill & Hurtado 1996 Aché; Howell !Kung; Blurton Jones Hadza):

- **Female-only births** (no male-pairing requirement this stage; biparental/Cred deferred).
- **Fertile window:** menarche ≈ 15 yr → last birth ≈ 42 yr (menopause ≈ 45–50).
- **Inter-birth interval (IBI) refractory:** per-agent "months since last birth" counter enforces
  a lactational refractory ≈ **36–48 months** (Aché ≈ 37, !Kung ≈ 44, Hadza ≈ 38).
- **Energetic modifier (not gate):** birth probability scales with maternal reserve, so lean years
  depress fertility without a hard cliff.
- **Sex ratio at birth:** SRB = **0.512 male** (anchored human constant ~105:100; confirm Aché
  figure from Hill & Hurtado in calibration).
- **Maternal mortality:** per-birth female hazard ≈ 1–1.5% (natural-fertility populations) — couples
  fertility to female mortality. Counts as `deaths_maternal`.
- **Calibration target:** realized **TFR ≈ 8 (Aché)**, IBI in band, age-specific fertility curve.

### 4.1 Infanticide (flag: `enable_infanticide`, OFF by default)
Aché-documented (Hill & Hurtado record infanticide, incl. circumstances tied to a father's death).
A behavioral post-birth mechanic, **not** folded into the SRB. Optional **sex-biased** variant.
Shifts the effective child sex ratio / lowers realized fertility. Off by default; behind its own
flag because it is a choice, not biology.

---

## 5. Staggered founder ages

Seed founders from the **Siler-implied stable age distribution** (derived from the calibrated
mortality+fertility schedule), so the founding population is demographically self-consistent and
starts near-stationary — no synchronized senescence wave, no multi-generation warm-up. Interim
fallback if the stable solve is not ready: the Aché empirical age pyramid (young; ~40% under 15,
median ≈ 20).

---

## 6. Configuration (new `DemographyConfig`)

All flags independent; all-off = pure Aché schedule + IBI fertility.

```
DemographyConfig:
  # mortality (Siler, sex-specific; LOCKED to Aché after Step-1)
  siler: {a1,b1,a2,a3,b3} per sex
  # baseline modulators (each flagged)
  enable_terrain_risk:      bool   # wire dormant risk field; free knob risk_ref
  enable_density_disease:   bool   # free knobs δ, ρ_half
  enable_terrain_pathogen:  bool = False   # provisional; pending lit
  enable_nutrition_synergy: bool   # free knob μ_max
  # fertility
  menarche_months, menopause_months, ibi_min_months
  srb_male: 0.512
  maternal_mortality_per_birth
  fertility_energetic_slope
  enable_infanticide:       bool = False   # optional sex-biased
  # init
  founder_age_source: "siler_stable" | "ache_pyramid"
```

**Degrees-of-freedom discipline:** everything in `siler` and the fertility block is **locked to
the Aché life table**. Only the wiring multipliers — `risk_ref`, `δ`, `ρ_half`, `μ_max`, and (if
used) pathogen slope — are **free knobs**, calibrated in Step 2 against r≈0. Keep free knobs minimal.

---

## 7. Two-step staging

**Step 1 — Pure demography (non-spatial / small harness, fast, NO terrain).**
A well-mixed population (or a tiny grid) under Siler + IBI fertility, all baseline modulators OFF.
Tune `siler` + fertility until the Aché targets (§8) are met and growth r≈0. Cheap — no 100k-agent
terrain runs. This is where the schedule is fit and **locked**.

**Step 2 — Terrain layer (full 100×100 world).**
Lock Step-1 params; enable the baseline modulators (`risk`, density-disease, synergy; pathogen if
anchored) and re-run on terrain. Calibrate only the free wiring knobs against the spatial
equilibrium. Measure the new (demographic) carrying capacity vs the A-3 food ceiling.

Rationale: the life-table fit is terrain-independent, and the full-terrain run is heavy
(A-3 hit 2.8 GB, ~20 min/run *frozen*; demographic stationarity needs generations). Decoupling
removes that risk from the calibration loop.

---

## 8. Validation gate (this stage GATES on reproducing the Aché)

GREEN requires **all**:

1. **Continuous turnover at equilibrium: births ≈ deaths > 0** (direct fix to the A-3 finding —
   frozen → flowing).
2. **Stable population, growth rate r ≈ 0** at carrying capacity (Step 1; and bounded on terrain).
3. **e₀ ≈ 35**, survival-to-15 ≈ 55–60%, **e₁₅ ≈ 50 further yr**, **modal adult death ≈ 70–72**.
4. **Age pyramid** matches the Aché shape (young, ~40% under 15).
5. **Realized IBI ≈ 37 mo** and **TFR ≈ 8** (Aché), within band.
6. **Sex-specific mortality** ordered correctly (females outlive males).
7. Rails clean: no NaN/Inf, no sub-floor reserve, no agents on water, determinism PASS.

Ablation deliverable: synergy coupled-vs-decoupled, and each baseline-modulator flag on/off, so the
report shows each mechanic's isolated contribution to equilibrium turnover.

---

## 9. Seams & code-touch map

- **`phase1_model.py` metabolism/mortality block (`_step_rivalrous` §4, `_step_agent` §5):** replace
  the `wealth ≤ floor` / `age ≥ max_age` branch with the Siler hazard draw + retained starvation
  backstop + cause attribution. Add per-agent `months_since_birth`, `sex` already present.
- **`_do_births`:** replace reserve-threshold rule with female-only + fertile-window + IBI + energetic
  modifier + SRB + maternal-mortality + optional infanticide.
- **`_init_agents`:** founder age sampling from the stable distribution.
- **`terrain.py`:** new `pathogen` field (flagged); `risk` field already exists (wire-only).
- **`config.py`:** `DemographyConfig`.
- **New non-spatial harness** for Step-1 calibration (`outputs/phase1_demography_calib/`).

---

## 10. Open decisions / provisional items

| Item | State |
|---|---|
| Terrain pathogen formula | **PENDING disease-ecology lit search** — ships OFF until anchored; sensitivity-tested |
| Exact Siler coefficients | fit from Hill & Hurtado Aché life table in Step 1 |
| Free wiring knobs (`risk_ref`, δ, ρ_half, μ_max) | calibrated in Step 2 vs r≈0 |
| Stage number | supervisor-assigned |

---

## 11. Literature anchors

- **Siler 1979** — competing-hazard 3-component mortality model.
- **Hill & Hurtado 1996**, *Aché Life History* (lit folder) — Aché life table, age-specific
  mortality & fertility, IBI, infanticide, maternal mortality. **Primary anchor.**
- **Gurven & Kaplan 2007**, "Longevity Among Hunter-Gatherers" (*Pop. Dev. Rev.*) — cross-HG
  mortality composite; modal adult lifespan ≈ 68–78. *(Confirm availability / add to LITERATURE.md.)*
- **Howell** (!Kung), **Blurton Jones** (Hadza) — IBI and fertility comparanda.
- Disease-ecology anchor for the pathogen field — **TO FIND** (open action).

---

## 12. Independent-review checkpoint (required before lock)

Per the workflow agreed 2026-06-18: this blueprint must pass an **independent, repo-grounded
red-team** before any code is written — a fresh-context reviewer (fresh CC session, spawned
sub-agent, or `/code-review ultra` once a draft exists) plus the supervisor. The authoring agent
must not be its own sole reviewer on the science. Review focus: (a) Aché anchors are faithful and
not over-fit; (b) the free-knob set is truly minimal; (c) the Step-1/Step-2 decoupling is valid;
(d) the validation gate genuinely falsifies a wrong schedule.

---

*Phase 1 Demographic Mechanics Blueprint · DRAFT 2026-06-18 · C-only, forage-only · Siler mortality
locked to Aché; pathogen layer provisional pending literature; all flags decoupled for ablation.*
