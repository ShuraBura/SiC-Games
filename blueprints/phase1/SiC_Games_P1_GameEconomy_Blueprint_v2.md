# SiC Games · Phase 1 · **Game / Hunting Economy — v2 (the C-vs-Si substrate)**

**Status:** DRAFT for red-team (2026-06-21). Supersedes v1 (`SiC_Games_P1_GameEconomy_Blueprint.md`),
whose motivation ("add game *before* calibrating δ") was overtaken by R-13/R-15/R-16/R-17. v1 + its
sub-agent red-team (§5b there) are kept as the audit trail; this v2 carries every v1 red-team fix forward
(RT-1…RT-5) and re-frames the purpose around the now-settled demographic substrate.

---

## 1. What changed since v1 — the purpose is no longer "fix the calibration"

v1 argued game must precede the δ calibration. The intervening results falsified that premise:

- **R-13** got density-disease to regulate (r→0, starvation→0) on the **forage-only** NPP economy, *no game*.
- **R-15/R-16/R-17** settled e₀: the regulated stationary e₀ (~28) is **fertility-pinned** and correct; the
  growth-phase e₀ recovers the Aché (38≈37). The e₀ question does **not** depend on game.
- **R-14** ruled per-agent (intra-band) nutritional variance **non-physical** at this scale — which kills
  v1's central rationale for game (G.2 "the variance source we kept needing"). Band-pooling washes
  per-hunter variance out (v1 RT-2), and that wash-out is *correct*, not a bug.

So game is **not** a δ patch and **not** a per-agent mortality modulator. Its real, surviving motivations:

1. **PRIMARY — the C-vs-Si substrate (the project's central question).** Forage is low-variance and
   household-level; the **κ (Cred-weighted) sharing lever does almost nothing on it**. **Meat is the
   high-variance, band-shared, status/reciprocity resource** (Kaplan & Hill 1985; Gurven 2004) — the
   resource whose *sharing topology* is exactly where Carbon (status-weighted, κ>0) and Silicon
   (egalitarian, κ=0) diverge, and whose *failure* (seasonal trough / catastrophe / inter-band run of bad
   luck) is the shock that the resilience test (R-1 anti-fragility) measures. **Without a high-variance
   shareable resource, κ>0 has almost nothing to act on** → the C-vs-Si layer would be economically thin.
   This stage builds the substrate the central experiment needs.
2. **SECONDARY / diagnostic — diet realism + the open density question.** (a) The Cordain-2000
   meat-fraction-by-biome is a real validation target the forage-only model can't speak to. (b) R-16/R-17
   left **density** as one open quantitative gap (starvation-free density 0.065 < Tallavaara floor 0.1).
   **Lead with the null (RT-E):** energy is conserved in the split (`S_meat + S_forage = S_cell`, all
   NPP-derived kcal), so the two-stream split **cannot** raise equilibrium density — density = total kcal ÷
   per-capita need, invariant to relabeling calories. R-17's passing phrase "game raises per-cell K for
   density" was a *misconception* this stage retires. The honest reading: **0.083/km² @ δ=3 with ~9%
   famine-fraction is already an acceptable Hiwi-like forager state** (real foragers experience periodic food
   stress; "starvation=0" was over-strict). The *only* residual channel is **second-order and G.3-contingent**
   — if band-sharing reduces inter-band intake *variance* near K, fewer bands cross the starvation threshold —
   a diagnostic to measure *if* G.3 is on, not a goal of the split.

**Key code fact (verified `phase1_model.py:269–326`, `substrate.py:22`):** the rivalrous/demographic path
*already* contains the κ machinery — `compute_harvest_shares(occ, S, kappa, phi_eps)` splits each cell's
pool equally (κ=0) or by Carbon Cred weight `(φ+ε)^κ` (κ>0). **In the validated R-13/R-15/R-16 runs it is
applied to the *total* NPP capacity field** (`harvest_field=cap`, the Tallavaara `SubWindowCapacity`) — i.e.
to *all* per-cell energy, not to a "forage" stream specifically (`tf.level` only equals `forage_kcal` on the
non-biome path). Lit says κ-weighting belongs on **meat**, not on total/plant energy. This stage's core move
is therefore (a) split the total into forage + meat, (b) **call the forage split with a literal `kappa=0`
(always equal/household), and route only the meat split through the config κ** — so κ acts on meat alone. If
the forage split is left on the model-wide κ after the split, κ is **double-applied** to both halves of the
same energy at κ>0 (RT-B): the literal-`kappa=0`-on-forage is a *code requirement*, not an emergent property.

---

## 2. What this stage is explicitly NOT (dead-ends closed by the red-team + R-14)

- **NOT** a per-agent nutritional-variance generator for the inert modulators (R-14: wrong level; v1 RT-2).
- **NOT** a productivity/return-rate split of the carrying capacity (v1 RT-1 units error). The diet split is
  by **Cordain diet composition**, not the `forage_kcal:game_kcal` ratio. Return-rate fields stay
  **diagnostic / movement-only**.
- **NOT** a father→child meat route (there is no father-link; v1 RT-3). Meat reaches dependents **via the
  band pool** (the band-scale route, MODEL_SPEC §4.5.4) — no father-link needed.
- **NOT** the migration mechanic (v1 RT-4; deferred to the open-biome stage; `game_mobility` seam already
  wired, §4.1.8) and **NOT** seasonality (v1 RT-5; calibration biomes are flat; savanna/llanos phenomenon).
- **NOT** claimed to "break the NPP-monoculture" (RT-A correction): `meat_frac(biome)·S_cell` is a per-biome
  *constant* × the NPP total, so it is NPP-shaped *within* a biome and only re-scaled *across* biomes — it does
  **not** add an NPP-independent spatial driver. Genuine independence would require keying `meat_frac` to a
  non-NPP axis (the `temperature`/`humidity`/latitude seam, terrain.py:275–276); deferred. The honest claim is
  only: the meat *fraction* of diet varies by biome (Cordain), not that game productivity has its own field.

---

## 3. Architecture — split the existing total, re-home κ onto meat

The NPP carrying capacity (`SubWindowCapacity`, `S = tf.level(cx,cy)`) is **total** HG energy (Tallavaara
density × burn), so game is **already implicit** in it. We **decompose, not add** (no double-count):

```
S_cell            = tf.level(cx, cy)                      # total energy (unchanged)
meat_frac(biome)  = Cordain-2000 animal-fraction          # diet-composition split (NOT return-rate ratio)
S_forage          = (1 - meat_frac) · S_cell              # low-variance, per-capita / household
S_meat            = meat_frac · S_cell                    # high-variance, BAND-pooled, κ-weighted
```

- **Total `S_cell` preserved** ⇒ the validated CC / R-3 / 444 baseline is unchanged when `meat_frac=0`
  (forest can be ≈0; the default config leaves the stream off → exact back-compat).
- **`meat_frac(biome)`** sets the *diet-composition* split by biome (Cordain); it re-scales the NPP total
  across biomes, it is **not** an NPP-independent productivity field (RT-A; §2).
- **Forage stream** is split with a **literal `kappa=0`** — `compute_harvest_shares(occ, S_forage, 0.0,
  phi_eps)`, NOT the model-wide κ (household / mother-linked provisioning, S1 tier) — plant food is not the
  status resource. **This is a code requirement (RT-B):** leaving the forage split on `sc.contest_exponent`
  would double-apply κ to both halves at κ>0. Gate: at κ>0, forage shares are equal while meat shares are
  Cred-weighted.
- **Meat stream** is **band-pooled** (cell = band) and distributed by `compute_harvest_shares(occ, S_meat,
  kappa, phi_eps)` — **this is where κ lives.** κ=0 → egalitarian per-capita meat (Silicon); κ>0 → Cred-
  weighted meat (Carbon). **Dependents are band members** → they receive meat *directly* via this split (the
  band-scale route), so no father-link is needed (RT-3). Meat counts toward `_fed_reserve` (condition/
  fertility) but **must not inflate the forage provisioning overflow** (v1 RT-3): it is its own intake channel,
  summed into `a.wealth`/`_fed_reserve` before the cap, not routed through `provision_pool`.
- **Known benign interaction (RT-C):** a meat-fed mother needs less of her *forage* for self-maintenance, so
  her forage overflow into `provision_pool` rises → dependents get marginally more *forage* provisioning too.
  This is not a double-count (meat and forage are distinct kcal), but the validation must confirm it does not
  over-smooth (watch the lean-season child-mortality pulse from R-10).

**"Total CC preserved" is only nominal (v1 RT-1 caveat, retained):** variance (§G.3) + the κ topology change
the *effective* CC through nonlinear mortality. That is precisely the object of interest for C-vs-Si, and the
reason the density question (§5) is a test, not an assumption.

---

## 4. Build stages (minimal, sequenced; all opt-in, 444 green throughout)

### G.1 — Two-stream split via Cordain diet composition  *(the honest core; v1 RT-1 fix)*
Add `meat_frac(biome)` from **Cordain et al. 2000** (animal-food fraction by latitude/environment; exact
per-biome extraction → MODEL_SPEC methods home, with the table and the scaling). Split `S_cell` per §3;
forage stream unchanged, meat stream summed into intake. **Default `meat_frac=0` ⇒ back-compat / 444 green.**
- **Gate:** emergent **meat fraction by biome** matches Cordain (forest low ~0.2–0.35 → high-latitude ≥0.5);
  with all streams summed, the demographic CC / vital rates **reproduce R-3 within tolerance** (the split is
  energy-conserving, so it must).

### G.2 — Meat as the band-pooled, κ-ready stream  *(the C-vs-Si SEAM; v1 RT-3 fix)*
Route `S_meat` through a **band (cell) pool** split by `compute_harvest_shares(occ, S_meat, kappa, phi_eps)`,
**and** switch the forage split to a literal `kappa=0` (RT-B). **Scope honesty (RT-F):** G.2 ships the *seam*
at the default κ=0 (= Silicon = current behavior); the **κ>0 experiment itself is the C/Cred stage's job**, not
this one. So G.2 is thin wiring — re-pointing an existing call at `S_meat` + the forage-κ=0 fix — and the only
*true* pre-req for the C/Cred stage is the G.1 energy-conserving split.
- **Gate (RT-B, two-pronged):** (i) at κ=0 the two-stream run reproduces a single-stream run's vital rates
  (decomposition inert until strategy/variance on); (ii) at κ>0, **forage shares stay equal while meat shares
  are Cred-weighted** (proves κ is not double-applied).

### G.3 — Stochastic meat returns  *(scoped per v1 RT-2 / R-14 — inter-band & temporal, NOT per-agent)*
Per-hunter per-step meat is a **stochastic draw** (lognormal; **per-biome CV** — forest 0.73 / desert 0.29 /
savanna 2.24, v1 RT-2b — *not* a single global CV), drawn from the **agent's own RNG** (`agent.random`, v1
RT-2b determinism). **Framing (explicit, to avoid re-litigating R-14):** this is built so the **band-level
meat total fluctuates over time and across bands** (the *operative* inter-band/temporal variance) and so
κ>0 allocates a *fluctuating* pool under stress — **NOT** to inject per-agent intra-band variance (which
band-pooling correctly washes out). 
- **Draw level matters (RT-D):** N *independent* per-hunter lognormals summed give band-total CV ≈
  CV_hunter/√N — for a 5–10-hunter band this shrinks the very signal G.3 wants. **Pre-register a band-level
  (correlated) draw** (a shared per-cell encounter shock, optionally × per-hunter idiosyncratic) so the
  band-total CV stays meaningful, rather than N independent draws that self-cancel.
- **Pre-registered check:** confirm band-pooling buffers the per-agent level (expected, fine) while leaving
  band-total temporal CV > 0 (the signal the resilience test needs). If even the band-total washes out under
  realistic band sizes, **fall back to deterministic-mean meat** (G.3 cut) — stochastic returns then add
  nothing and the shock comes from seasonality/catastrophe instead.

### Then (this stage's exit) — the density question + hand-off
- **Density (RT-E — lead with the null):** by energy conservation the split **cannot** move equilibrium
  density; **the honest resolution is that 0.083/km² @ δ=3 (~9% famine-fraction) is an acceptable Hiwi-like
  forager state** and "starvation=0" was over-strict. Only *if G.3 is on* is there a second-order diagnostic:
  re-run the temperate δ sweep with stochastic band-shared meat and check whether reduced inter-band variance
  near K lets the starvation-free density tick up. Report it as a contingent diagnostic, not a goal.
- **Hand-off:** G.1+G.2 (±G.3) is the substrate for the **C/Cred resilience stage** (κ>0 + the strategy /
  Cred / cultural dynamics on the demographic core) — the central C-vs-Si experiment.

### DEFERRED (with the v1 red-team reasons, restated)
- **Seasonality** (anti-phase forage/game, fat-value vs aggregation; v1 G.3) — calibration biomes are flat;
  re-activate in the seasonal/open-biome stage. R-10's *mechanism* stands (v1 RT-5); only its amplitude was
  biome-generic.
- **Migration / herd-following** (v1 G.5) — own open-biome stage after the C/Cred layer; `game_mobility`
  seam wired (§4.1.8); orthogonal to everything here (v1 RT-4). Addresses R-8 under-mobility there.

---

## 5. Validation / gates (summary)
1. **Energy conservation:** total intake with `meat_frac=0` is bit-identical to current; 444 green.
2. **Cordain meat-fraction by biome** (G.1) — direction + bracketed magnitude vs Cordain 2000.
3. **κ=0 inertness** (G.2) — two-stream at κ=0 reproduces single-stream vital rates (the decomposition adds
   nothing until strategy/variance is on). This is the anti-double-count proof.
4. **Band-total temporal CV > 0, per-agent CV ≈ buffered** (G.3) — the R-14-correct variance signature.
5. **Density** (exit) — lead with the null (conservation ⇒ split can't move density; 0.083@δ=3 acceptable);
   *contingent* G.3 diagnostic only.
6. **Determinism** with the new draws (pre-seeded per-agent RNG).

## 6. Red-team targets (for the fresh repo-grounded sub-agent)
RT-A: Is the **Cordain diet-composition split** the right and only split driver, and is `meat_frac(biome)`
identifiable from Cordain 2000 without inventing numbers? Does the independent biome modulation actually
break the NPP-monoculture or only cosmetically?
RT-B: **Re-homing κ onto meat** — is "forage household / meat band-pooled-κ" the correct lit topology
(§4.5.4)? Does leaving the *forage* `compute_harvest_shares` at κ implicitly double-apply κ when both streams
are on? (Forage should be κ-inert.)
RT-C: **Meat → `_fed_reserve` but not `provision_pool`** — verify no over-smoothing / no double-count with
the S1/C.2b forage provisioning; confirm dependents are fed by meat *only* via the band pool.
RT-D: **G.3 framing** — is the inter-band/temporal-variance rationale sound, or is this R-14's washed-out
per-agent variance smuggled back in? Is the deterministic-mean fallback the right default?
RT-E: **Density hypothesis** — is the buffering→higher-density mechanism real (energy is conserved!), or is
the null ("0.083 is fine, starvation=0 too strict") the more honest framing to lead with?
RT-F: **Sequencing & scope** — is G.1→G.2(→G.3) the minimal substrate for the C/Cred stage, and is anything
here actually a prerequisite vs. foldable into the C/Cred stage itself?

## 7. Out of scope / deferred
Pastoralism / herd management (HG following only); intra-herd predator-prey (herd = exogenous field);
full star-mechanics seasonal lottery (Earth biome anchors); inter-band competition over herds (→ C-vs-Si
conflict subsystem); the migration mechanic (open-biome stage).

## 8. Open questions for the supervisor (pre-build)
- **Q1 (framing):** Endorse the re-frame — game's job is the **C-vs-Si substrate + diet realism**, *not* a
  δ/e₀ fix (those are settled)? 
- **Q2 (κ topology):** Agree meat = the κ-weighted band-shared stream, forage = κ-inert household? (This is
  the load-bearing lit decision.)
- **Q3 (scope):** Minimal — **G.1 + G.2 only** (defer G.3 stochasticity until the C/Cred stage needs a live
  shock), or include G.3 now?
- **Q4 (density):** Confirm leading with the **null** (RT-E: conservation ⇒ split can't raise density;
  0.083@δ=3 is an acceptable Hiwi-like state; "starvation=0" was over-strict)? *(Red-team: lead with null.)*
- **Q5 (data):** ~~Is Cordain 2000 in `literature/`?~~ **RESOLVED — yes**
  (`literature/SiC_Games_A2.1_Cordain2000_PlantAnimalRatios.pdf`). Per-biome `meat_frac` extraction → MODEL_SPEC.

## 6b. Red-team v2 (2026-06-21, fresh repo-grounded sub-agent) — VERDICT: APPROVE-WITH-FIXES (all applied)

All five v1 fixes (RT-1…RT-5) confirmed genuinely carried; new errors were in the *new* claims, now fixed:
- **RT-B [MAJOR, fixed]:** "forage κ=0 effectively" was asserted, not coded — the model-wide κ would
  **double-apply** to both halves at κ>0. Now specified: forage split called with **literal `kappa=0`**, with a
  two-pronged gate (κ=0 inert; κ>0 forage-equal/meat-weighted). Also corrected the §1 mis-statement: in the
  validated runs κ is on the **total NPP `cap`**, not a "forage" stream.
- **RT-A [MAJOR-on-the-claim, fixed]:** dropped the false "breaks the NPP-monoculture" claim — `meat_frac·S_cell`
  is a per-biome constant × the NPP total (NPP-shaped within biome). Now states it is only a cross-biome
  diet-fraction re-scaling; genuine independence would need the temperature/latitude seam (deferred).
- **RT-E [MINOR, fixed]:** density now **leads with the null** (energy conserved ⇒ split can't move density;
  0.083@δ=3 acceptable); the buffering effect demoted to a contingent G.3 diagnostic.
- **RT-D [MINOR, fixed]:** G.3 now pre-registers a **band-level (correlated) draw**, since N independent
  per-hunter draws shrink band-total CV by √N and self-cancel.
- **RT-C [SOUND]:** insertion point verified clean (meat → `a.wealth`/`_fed_reserve` before cap, never
  `provision_pool`); benign mother-overflow interaction noted in §3 with an over-smoothing watch.
- **RT-F [SOUND]:** G.1 (energy-conserving split) is the true pre-req; G.2 is thin seam-wiring at κ=0, the κ>0
  experiment belongs to the C/Cred stage — now stated explicitly.

---

**Anchors referenced:** Cordain et al. 2000 (animal-food fraction by latitude — G.1 split;
`literature/SiC_Games_A2.1_Cordain2000_PlantAnimalRatios.pdf`); Kaplan & Hill 1985 / Gurven 2004 (band-wide
meat sharing topology — G.2, MODEL_SPEC §4.5.4); Hawkes et al. 1991 (per-biome game CV — G.3); Binford 2001 +
`game_mobility` §4.1.8 (deferred migration). RESULTS R-13/R-14/R-15/R-16/R-17 (why the purpose changed). Code:
`phase1_model.py:269` `_step_rivalrous`, `substrate.py:22` `compute_harvest_shares`, `terrain.py:269`
`game_kcal` (diagnostic), `agents/base.py:135` `eta`.
