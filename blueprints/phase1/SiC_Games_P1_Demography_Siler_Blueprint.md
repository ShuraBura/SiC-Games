# SiC Games — Phase 1 Demographic Mechanics Blueprint
## Siler Mortality + IBI Reproduction + Terrain-Modulated Hazard

**Status:** DRAFT v2 (independently red-teamed 2026-06-18) — for supervisor review and lock. Inline
errors caught by the red-team are corrected; remaining open items + dispositions are in §13.
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

> **UNITS (red-team M-4 — guards a classic ×12 bug):** `a` is in **months**; {a1,a2,a3} are
> **per-month** rates and {b1,b3} per-month. Published Aché / Gurven-&-Kaplan coefficients are
> **annual** — convert before use (`a_month = a_year/12`; keep `b·a` in consistent per-month units).
> A unit test must assert the integrated monthly hazard reproduces the published annual `l(x)`.

**Parameterization (LOCKED to Aché; exact coefficients fit in Step-1 calibration, §9):**
Targets the schedule must reproduce (Hill & Hurtado 1996; Gurven & Kaplan 2007):

| Quantity | Aché / HG anchor |
|---|---|
| Life expectancy at birth e₀ | ≈ 35–37 yr (low — dominated by infant term) |
| Survival to age 15 | ≈ 55–60% |
| Life expectancy at 15, e₁₅ | **≈ 37–40 *remaining* years** (VERIFY vs Hill & Hurtado; gate band ±3). NOT "50 further". |
| Modal adult age at death | ≈ 70–72 yr (weak statistic — gate on the l(x) curve, not this); **females outlive males ~2–5 yr (verify in Aché — maternal mortality can reverse it)** |
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

> **Scope (Dunn 1968; Houldcroft 2023):** HG bands are too small to sustain crowd/epidemic
> diseases (measles, influenza need large host pools and post-date agriculture). So this channel
> represents **endemic/zoonotic transmission rising modestly with local aggregation**, not
> epidemic crowd disease. Keep `δ` modest — a gentle density check, not a population crash.

### 3.3 Terrain pathogen field — `P(cell)` (flag: `enable_terrain_pathogen`)
A **new** terrain field, separate from `risk`. **Now literature-anchored** (lit search 2026-06-18):

- **Tallavaara et al. 2018 PNAS** — the *same* framework we already use for the CC-1 NPP→density
  anchor — finds **pathogen stress is a major driver that lowers HG population density, dominant in
  high-productivity regions (NPP > 1,360 g/m²/yr, our exact CC-1 threshold) and the tropics**,
  while NPP/biodiversity dominate in low-productivity/high-latitude regions. So the pathogen penalty
  should bite hardest in our **high-NPP cells (wetland, forest)** — making them a genuine
  productivity-vs-disease tradeoff, not a free lunch.
- **Guernier et al. 2004 (PLoS Biol)** — human pathogen richness rises with **temperature and
  precipitation** (precipitation range the single best predictor) and falls with latitude.
- **Vector/water mechanism** — malaria transmission is temperature-bounded (~16–36 °C) and needs
  **standing water** breeding habitat; waterborne load tracks water contact.

Operationalized from the terrain's available proxies (no explicit temperature field):

```
pathogen_raw ∝  wateracc                    (standing water → vector/waterborne habitat; primary driver)
P(cell) = 1 + π · normalize(pathogen_raw) · s(NPP),   s(NPP) = NPP / (NPP + NPP_half)
```
`s(NPP)` is a **smooth** NPP weighting — NOT a hard step at 1360 (red-team m-1: Tallavaara's path is
a *continuous* SEM coefficient, pathogen load is not zero below the threshold). The NPP-derived
"warmth proxy" of v1 is **dropped** (red-team m-2: it was circular with NPP, collapsing four knobs to
one axis). Pathogen is held to **≤2 free knobs** (`π` and `NPP_half`), driven by `wateracc` × `s(NPP)`.
Magnitude calibrated against Tallavaara's SEM coefficients (Zenodo 1069787) in Step 2.
Terrain-generator change (`terrain.py`). Anchored — **may be ON in Step 2** with a flag-off ablation
and sensitivity sweep.

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
starts near-stationary — no synchronized senescence wave, no multi-generation warm-up.

**Bootstrap resolution (red-team m-4):** the stable distribution depends on the calibrated schedule,
which itself seeds founders from that distribution — chicken-and-egg. Resolve by using the **Aché
empirical age pyramid (young; ~40% under 15, median ≈ 20) as the Step-1 default**, and deriving the
true Siler-stable distribution only after the schedule locks (for Step 2).

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

1. **Continuous turnover at equilibrium: births ≈ deaths > 0**, with a **crude death rate in the
   Aché stationary band (~40–60 per 1,000/yr)** over a fixed measurement window ± tolerance — not a
   few-events/yr trickle (red-team m-5). Direct fix to the A-3 finding (frozen → flowing).
2. **Growth rate r ≈ 0.** In Step 1 this is a *fertility-shape* check; on terrain the baseline/
   fertility scaler is **re-balanced** to restore r≈0 — Step-1's equilibrium does NOT transfer
   unchanged, because the all-≥1 modulators raise mean hazard (red-team M-2; see §7).
3. **Full survivorship curve l(x) matches the Aché H&H life table** (RMSE / max-deviation at decadal
   ages) — not just scalar summaries (red-team B-2). Anchor points: **e₀ ≈ 35**, survival-to-15
   ≈ 55–60%, **e₁₅ ≈ 37–40 remaining yr (VERIFY vs H&H)**, Gompertz mortality-rate-doubling-time
   ~7–8 yr.
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
| Terrain pathogen field | **ANCHORED** (Tallavaara 2018 / Guernier 2004, lit search 2026-06-18); structure fixed; magnitude (`π`, `w_*`) from Tallavaara SEM coefficients (Zenodo 1069787) in Step 2 |
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

**Disease ecology (lit search 2026-06-18 — pathogen field anchor):**
- **Tallavaara, Eronen & Luoto 2018**, PNAS 115(6):1232–1237 — productivity + biodiversity +
  pathogen stress drive global HG population density; pathogen stress dominant where NPP > 1,360
  g/m²/yr and in the tropics. *Same paper as the CC-1 NPP anchor.* Data/script: Zenodo 1069787.
- **Guernier, Hochberg & Guégan 2004**, "Ecology Drives the Worldwide Distribution of Human
  Diseases", PLoS Biol 2(6):e141 — pathogen richness ∝ temperature + precipitation, ↓ latitude.
- **Dunn 1968** (in *Man the Hunter*) + **Houldcroft 2023** (Am J Biol Anthropol) — Paleolithic/HG
  disease-scape is **zoonotic/vector-borne/environmental, not crowd-epidemic** (crowd diseases need
  large populations and post-date agriculture). Bounds the density-disease channel (§3.2).
- Malaria thermal/hydrological suitability (vector lit) — transmission ~16–36 °C; standing-water
  breeding habitat. Supports the pathogen-field water + warmth drivers.

---

## 12. Independent-review checkpoint (required before lock)

Per the workflow agreed 2026-06-18: this blueprint must pass an **independent, repo-grounded
red-team** before any code is written — a fresh-context reviewer (fresh CC session, spawned
sub-agent, or `/code-review ultra` once a draft exists) plus the supervisor. The authoring agent
must not be its own sole reviewer on the science. Review focus: (a) Aché anchors are faithful and
not over-fit; (b) the free-knob set is truly minimal; (c) the Step-1/Step-2 decoupling is valid;
(d) the validation gate genuinely falsifies a wrong schedule.

---

## 13. Red-team revision log (v2 — independent review 2026-06-18)

An independent, repo-grounded red-team reviewed v1. **Verdict: direction sound; NOT lockable as v1 —
one revision pass.** Dispositions:

**Applied in this v2 (inline):**
- **B-1 — e₁₅ wrong/inconsistent.** v1 said "e₁₅ ≈ 50 further yr" (progress report said ~70).
  Corrected to **≈37–40 *remaining* years**, flagged VERIFY vs Hill & Hurtado, gate band ±3 (§2, §8).
- **B-2 — gate too weak to falsify.** Added **full survivorship-curve l(x)** comparison + Gompertz
  mortality-rate-doubling-time to the gate; modal-death demoted to a weak secondary (§8.3).
- **M-4 — rate-unit ×12 bug.** Hazard stated **per-month**; annual→monthly conversion documented;
  unit test required (§2).
- **M-2 — Step-1→Step-2 not transferable.** Reframed: Step-1 locks intrinsic terms + fertility
  shape; baseline/fertility **re-balanced in Step-2** (all modulators ≥1 raise mean hazard → r<0 on
  terrain otherwise) (§8.2).
- **m-1 — pathogen hard gate mis-cites Tallavaara.** Replaced step at 1360 with **smooth** `s(NPP)`
  (§3.3).
- **m-2 — pathogen knobs collapse to NPP axis.** Dropped the circular warmth proxy; pathogen ≤2
  knobs (§3.3).
- **m-4 — founder bootstrap.** Aché pyramid is the **Step-1 default**; Siler-stable derived
  post-lock (§5).
- **m-5 — turnover untestable.** Gate now requires a **crude death rate in the Aché band
  (~40–60/1000/yr)** over a window (§8.1).

**Accepted — resolve at implementation / supervisor lock:**
- **M-1 — over-fitting (~20 fitted+free DOF vs ~6 targets).** **FIX Siler coefficients from a
  published Aché competing-hazard fit (H&H / Gurven & Kaplan) as constants — do NOT re-fit.** Add a
  fitted-vs-fixed table; require free params ≤ independent gate targets.
  **[SUPERVISOR: confirm we adopt published coefficients rather than fitting our own.]**
- **M-3 — maternal-mortality double-count.** The Aché life table is all-cause, so a separate
  `deaths_maternal` term on top double-counts. **Choose:** (a) fit the female Siler to a
  maternal-removed schedule and add maternal back explicitly, or (b) fold maternal into the female
  baseline and drop the separate term. **[SUPERVISOR DECISION — recommend (a) for transparency.]**
- **M-5 — `_do_births` is a rewrite, not wiring.** Reclassify §9 as a full reproduction-engine
  rewrite with its own tests; **maternal-death draw must occur AFTER the child is created/counted.**

**Minor/nits noted:** n-1 cap `a2_eff` (or final monthly `p`) against pathological spikes in a
crowded/high-risk/high-pathogen/low-reserve cell; n-2 verify **females>males survival holds in the
Aché data** before gating (§2 note added); n-3 confirm Gurven & Kaplan 2007 is in the lit folder
before relying on it; m-3 add an SRB×infanticide orthogonality test.

Full critique archived with this session's transcript.

---

*Phase 1 Demographic Mechanics Blueprint · DRAFT **v2** 2026-06-18 (red-teamed) · C-only, forage-only ·
Siler mortality anchored to Aché (coefficients to be FIXED from a published fit, not re-fit); pathogen
layer anchored (Tallavaara 2018 / Guernier 2004); all flags decoupled for ablation. Open items: §13.*
