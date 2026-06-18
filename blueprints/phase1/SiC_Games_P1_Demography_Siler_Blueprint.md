# SiC Games — Phase 1 Demographic Mechanics Blueprint
## Siler Mortality + IBI Reproduction + Terrain-Modulated Hazard

**Status:** **v3 — LOCKED for implementation (supervisor 2026-06-18).** Independently red-teamed; all
blocker/major items resolved and folded into the body (§13). **Step-1 (non-spatial Aché calibration)
is the next build.**
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

**Parameterization — coefficients FIXED from a published Aché fit, NOT re-fit (M-1, supervisor 2026-06-18):**
The Siler coefficients {a1,b1,a2,a3,b3} per sex are taken as **constants** from a published Aché
competing-hazard fit (Gurven & Kaplan 2007), or — if only a life table is published — fit **ONCE** to
Hill & Hurtado's Aché `l(x)` and then **frozen**. They are NOT free parameters in any calibration
loop. The female `a2` is fit to a **maternal-mortality-removed** schedule (M-3, §4). The fixed
schedule must reproduce these Aché anchors at the validation gate (§8 — a *check*, not a fit target):

| Quantity | Aché / HG anchor |
|---|---|
| Life expectancy at birth e₀ | ≈ 35–37 yr (low — dominated by infant term) |
| Survival to age 15 | ≈ 55–60% |
| Life expectancy at 15, e₁₅ | **38.5 *remaining* years** (Gurven & Kaplan 2007 Table 2, Aché forest — VERIFIED; confirms NOT "50 further"). |
| Modal adult age at death | ≈ 70–72 yr (weak statistic — gate on the l(x) curve, not this); **females outlive males ~2–5 yr (verify in Aché — maternal mortality can reverse it)** |
| Senescence onset | gradual; **NOT a 75-yr cap** — the trap A-3 would otherwise repeat |

> **Demographic trap to avoid:** the ~35-yr "life expectancy" is low *only because of infant
> mortality*. The senescence term must anchor to **modal adult death (~70)**, not the ~35 mean,
> or the population dies decades too young.

**SOURCED — Aché forest-period Siler coefficients (Gurven & Kaplan 2007, Table 2; both sexes;
ANNUAL units, age `x` in years):**

| param | value | meaning |
|---|---|---|
| a1 | 0.157 /yr | initial infant mortality rate |
| b1 | 0.721 /yr | infant-mortality decline rate |
| a2 | 0.013 /yr | **Makeham age-independent ("exogenous, environmental") — the term the world modulates** |
| a3 | 4.80×10⁻⁵ /yr | Gompertz initial adult mortality |
| b3 | 0.103 /yr | Gompertz rate (MRDT = ln2/b3 ≈ 6.7 yr) |

Realized anchors (same table): e₀ = 37, **e₁₅ = 38.5 remaining yr**, e₄₅ = 21.1, survival-to-15 =
0.66, survival 15→45 = 0.43, modal adult death = 71. **Convert to per-month (÷12) before use** (UNITS
box above). **Sex note:** G&K Table 2 is both-sexes; the sex-specific split and the maternal-removed
female fit (M-3) come from Hill & Hurtado's sex-specific Aché tables — a Step-1 sub-task.

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
- **Maternal mortality (approach (a), supervisor 2026-06-18):** the female Siler is fit to a
  **maternal-mortality-REMOVED** Aché schedule, and maternal mortality is added back here as an
  **explicit** per-birth hazard (`deaths_maternal`) — avoids double-counting the all-cause life table
  (red-team M-3). Per-birth female hazard ≈ 1–1.5% (verify the Aché figure from Hill & Hurtado). The
  draw occurs **AFTER** the birth is counted (M-5).
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
  # mortality (Siler, sex-specific) — FIXED constants from a published Aché fit, NOT re-fit (M-1)
  #   female a2 fit to a MATERNAL-REMOVED schedule; maternal added back at birth (M-3 approach (a))
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

**Degrees-of-freedom discipline (M-1):** the `siler` block is **fixed constants from a published
Aché fit — zero free parameters.** The fertility block is anchored to Aché IBI/TFR. The ONLY free
knobs are the Step-2 wiring multipliers — `risk_ref`, `δ`, `ρ_half`, `μ_max`, `π`, `NPP_half` —
calibrated against r≈0. **Required invariant: # free knobs ≤ # independent gate targets.**

---

## 7. Two-step staging

**Step 1 — Pure demography (non-spatial / small harness, fast, NO terrain).**
A well-mixed population (or a tiny grid) under Siler + IBI fertility, all baseline modulators OFF.
With the `siler` coefficients FIXED from the published Aché fit (M-1), tune only the **fertility**
parameters (IBI, energetic slope) until Aché IBI/TFR and growth r≈0 are met, and VERIFY the fixed
Siler schedule reproduces the Aché `l(x)`. Cheap — no 100k-agent terrain runs.

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
   *[STEP-1 ✓ 2026-06-18: CBR 61 / CDR 27 per 1000/yr — turnover restored, A-3 freeze fixed. CDR is
   below the 40–60 stationary band because the Aché-calibrated population is **growing** (young
   structure); the stationary-band check applies at the Step-2 r≈0 equilibrium.]*
2. **Growth rate r — Aché vital rates, NOT r≈0, in Step 1.** *[STEP-1 2026-06-18: fertility tuned to
   Aché IBI=37/TFR=7.9 gives **r = +3.3%/yr** — the real forest-period Aché grew (~+2.5%); forcing
   r≈0 needs unrealistic fertility (TFR≈3, IBI≈68). So Step 1 matches the Aché* vital rates*;
   **r≈0 is a Step-2 property** — the all-≥1 terrain/disease modulators raise mean hazard to bring
   r→0 at carrying capacity (red-team M-2; §7).]*
3. **Full survivorship curve l(x) matches the Aché H&H life table** (RMSE / max-deviation at decadal
   ages) — not just scalar summaries (red-team B-2). Anchor points: **e₀ ≈ 35**, survival-to-15
   ≈ 55–60%, **e₁₅ ≈ 37–40 remaining yr (VERIFY vs H&H)**, Gompertz mortality-rate-doubling-time
   ~7–8 yr. *[STEP-1 ✓: e₀=36.5, e₁₅=38.3, e₄₅=21.3, modal death=71, MRDT=6.7 — fixed Aché Siler
   reproduces the life table.]*
4. **Age pyramid** matches the Aché shape (young, ~40% under 15).
5. **Realized IBI ≈ 37 mo** and **TFR ≈ 8** (Aché), within band. *[STEP-1 ✓: IBI 37.0, TFR 7.9.]*
6. **Sex-specific mortality** ordered correctly (females outlive males).
7. Rails clean: no NaN/Inf, no sub-floor reserve, no agents on water, determinism PASS.

Ablation deliverable: synergy coupled-vs-decoupled, and each baseline-modulator flag on/off, so the
report shows each mechanic's isolated contribution to equilibrium turnover.

---

## 9. Seams & code-touch map

- **`phase1_model.py` metabolism/mortality block (`_step_rivalrous` §4, `_step_agent` §5):** replace
  the `wealth ≤ floor` / `age ≥ max_age` branch with the Siler hazard draw + retained starvation
  backstop + cause attribution. Add per-agent `months_since_birth`, `sex` already present.
- **`_do_births` (FULL REWRITE, not wiring — M-5):** replace the asexual reserve-threshold rule with
  female-only + fertile-window + IBI refractory + energetic modifier + SRB + maternal-mortality +
  optional infanticide. **The maternal-death draw happens AFTER the child is created and counted**
  (else the birth is lost). Own unit tests: IBI enforced, window boundaries, realized SRB, draw order.
- **`_init_agents`:** founder age sampling from the stable distribution.
- **`terrain.py`:** new `pathogen` field (flagged); `risk` field already exists (wire-only).
- **`config.py`:** `DemographyConfig`.
- **New non-spatial harness** for Step-1 calibration (`outputs/phase1_demography_calib/`).

---

## 10. Open decisions / provisional items

| Item | State |
|---|---|
| Terrain pathogen field | **ANCHORED** (Tallavaara 2018 / Guernier 2004, lit search 2026-06-18); structure fixed; magnitude (`π`, `w_*`) from Tallavaara SEM coefficients (Zenodo 1069787) in Step 2 |
| Exact Siler coefficients | **RESOLVED (M-1, 2026-06-18):** FIXED constants from a published Aché fit (Gurven & Kaplan 2007; or fit once to H&H l(x) then frozen) — not re-fit |
| Maternal mortality | **RESOLVED (M-3, 2026-06-18):** approach (a) — female Siler fit maternal-removed; maternal added back explicitly |
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
- **Dunn 1968** (in *Man the Hunter*) + **Houldcroft & Underdown 2023** (Am J Biol Anthropol) — Paleolithic/HG
  disease-scape is **zoonotic/vector-borne/environmental, not crowd-epidemic** (crowd diseases need
  large populations and post-date agriculture). Bounds the density-disease channel (§3.2).
- Malaria thermal/hydrological suitability (vector lit) — transmission ~16–36 °C; standing-water
  breeding habitat. Supports the pathogen-field water + warmth drivers.

---

## 12. Independent-review checkpoint — **COMPLETE (2026-06-18; findings in §13)**

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

**Supervisor decisions (RESOLVED 2026-06-18) — folded into the body:**
- **M-1 — over-fitting (~20 fitted+free DOF vs ~6 targets). RESOLVED: YES** — fix Siler coefficients
  from a published Aché fit as constants, do NOT re-fit (Gurven & Kaplan 2007; or fit once to H&H
  l(x) then freeze); free knobs ≤ gate targets. → §2, §6, §7, §10.
- **M-3 — maternal-mortality double-count. RESOLVED: approach (a)** — fit the female Siler to a
  maternal-removed schedule and add maternal back explicitly as `deaths_maternal`. → §4, §10.
- **M-5 — `_do_births` is a rewrite, not wiring. ACKNOWLEDGED** — full reproduction-engine rewrite;
  maternal-death draw occurs AFTER the child is created/counted. → §9.

**Minor/nits noted:** n-1 cap `a2_eff` (or final monthly `p`) against pathological spikes in a
crowded/high-risk/high-pathogen/low-reserve cell; n-2 verify **females>males survival holds in the
Aché data** before gating (§2 note added); n-3 confirm Gurven & Kaplan 2007 is in the lit folder
before relying on it; m-3 add an SRB×infanticide orthogonality test.

Full critique archived with this session's transcript.

---

*Phase 1 Demographic Mechanics Blueprint · **v3 — LOCKED 2026-06-18** (red-teamed; supervisor decisions
M-1/M-3/M-5 resolved) · C-only, forage-only · Siler mortality FIXED from a published Aché fit (female
maternal-removed); pathogen anchored (Tallavaara 2018 / Guernier 2004); all flags decoupled for
ablation. Next build: Step-1 non-spatial Aché calibration.*
