# SiC Games — Phase 1 Demographic Stage · STEP 2 Blueprint
## Terrain-Modulated Demography on the Full World

**Status:** DRAFT v3 (red-teamed 2026-06-18; **B-1 BLOCKER RESOLVED 2026-06-18**). The 2a-pre stability
test **PASSED** — bounded settling, food density-dependence stabilizes the +3.3%/yr population (no
overshoot/oscillation/collapse; the food brake is ~1 step). **M-3 sex-split landed.** Remaining before
lock: **the 2b knob-anchoring** (Tallavaara pathogen SEM, μ_max, risk scale). Dispositions in §11.
**Created:** 2026-06-18
**Phase:** 1 (Terrain & Resource Ecology). Builds directly on Step 1.
**Precursors:** `SiC_Games_P1_Demography_Siler_Blueprint.md` (the locked stage spec) and Step-1
(`outputs/phase1_demography_calib/`, RESULTS R-3 — the Aché-calibrated Siler+IBI core).

---

## 0. The ONE question

> "When the Aché-calibrated demography (fixed Siler + IBI, from Step 1) runs on the Phase-1 terrain
> with the baseline-mortality (`a2`) modulators live, **where does the population equilibrate (r→0),
> and how does that *demographic* carrying capacity compare to the A-3 ~133k *food* ceiling?**"

A-3 found a frozen food-capacity ceiling (~133k). Step 1 restored continuous turnover and reproduced
the Aché vital rates off-terrain, but the Aché-calibrated population *grows* (r=+3.3%/yr). Step 2 puts
that growing demography on the terrain and lets density-dependent mortality (food + crowding + disease)
**check the growth at a spatial equilibrium** — the demographic carrying capacity.

**Non-goals:** Si demography; biparental/Cred C reproduction; game depletion; intergroup violence;
climate shocks. C-only, forage-only, single population.

---

## 1. What is FIXED (inherited, not re-tuned)

From Step 1, **locked**: the Siler coefficients (Aché, Gurven & Kaplan 2007; confirmed vs filed PDF)
and the fertility schedule (menarche/menopause/IBI/fecundability/SRB/maternal) calibrated to Aché
IBI=37/TFR=7.9. **Step 2 does NOT re-tune these.** It only (a) wires them into the spatial model and
(b) calibrates the small set of terrain-modulator knobs.

---

## 2. Wiring the demographic core into `phase1_model.py`

Replace the A-3 shakedown mortality+reproduction (starvation + hard age-cap + asexual reserve-gated
budding) with the Step-1 core (`sic_games.demography`):

- **Mortality:** per agent per step, `monthly_death_prob(age_months, a2_mult)` where `a2_mult` is the
  product of the live modulators (§3). Hard **starvation backstop** retained (`reserve ≤ floor`).
  Cause-attributed: `deaths_baseline / deaths_senesc / deaths_infant / deaths_starv / deaths_maternal`.
- **Reproduction:** female-only IBI engine (`is_fertile` + fecundability + SRB + maternal-after-birth);
  energetic modifier now LIVE (couples birth probability to the agent's kcal reserve — was neutral in
  Step 1). Infanticide flag available, off.
- **Founders:** staggered ages from the Siler-stable distribution (Step-1 `stationary_ages`).
- **Economy unchanged:** CC-1 cell capacity + kcal reserve (A-3) stay — food is the link to the
  nutrition×disease synergy and the starvation backstop.

The A-3 multi-occupancy substrate, diffusion movement, water guard, and CC-1 harvest field are kept.

---

## 3. The `a2` modulators (each flagged; the ONLY new free knobs)

Per the locked stage spec §3: `a2_eff = a2 · R(cell)^[risk] · D(ρ)^[dens] · P(cell)^[path] · M(reserve)^[syn]`,
capped (n-1). With all flags off → the pure Aché schedule (= Step-1 on terrain).

| Modulator | form | knob | how the knob is set |
|---|---|---|---|
| Terrain risk `R` | `risk(cell)/risk_ref`, **max-capped** | `risk_ref`, max-cap | mean PINNED (norm ≈1); but the risk *scale/gradient* must ALSO be pinned — cap the max risk multiplier to a lit accident-mortality elevation (red-team M-2) |
| Density-disease `D` | `1 + δ·ρ/(ρ+ρ_half)`, **ρ = agents/km²** | `δ, ρ_half` | **primary free lever** (endemic/zoonotic; modest — Dunn/Houldcroft). ρ as DENSITY not raw occupancy (red-team m-3: occupancy is cell-size-dependent) |
| Pathogen `P` | `1 + π·norm(wateracc)·s(NPP)` | `π, NPP_half` | **FREE until extracted** — Tallavaara SEM coeffs (Zenodo 1069787) not yet pulled; mapping onto the `wateracc` proxy (no temp field) unproven (red-team M-2) |
| Nutrition synergy `M` | `1+(μ_max−1)(1−clamp(reserve))` | `μ_max` | **soft-free** — lit gives a *range* (~2–3×), reference still to find; 2× vs 3× moves the CC (red-team M-2) |

**Degrees-of-freedom discipline — RED-TEAM M-2 CORRECTION.** The earlier "3-of-4 pinned, ≤2 free" claim
was overstated. Honest count: `risk_ref` pins only the *mean* (not the risk scale/gradient that drives
the sorting); `π, NPP_half, μ_max` are *aspirationally* pinned but their anchors are still §8 open items
(so **free until extracted**); plus `fertility_energetic_slope` (§7). **Realistic free/soft-free count ≈ 6,
not 2.** To lock: either extract the pathogen + synergy anchors NOW (move out of §8) and pin the risk
scale, OR reclassify them free and add enough independent *quantitative* gate targets (§6) so that
**# free knobs ≤ # independent gate targets** holds honestly. New terrain `pathogen` field added to
`terrain.py`.

---

## 4. How r→0 emerges (the mechanism — read before the gate)

**HYPOTHESIS — to be tested empirically (red-team B-1), NOT assumed:** that density-dependent food
checks the growth at a *stable* equilibrium. The CC-1 cell capacity makes food density-dependent —
per-capita share `S/n` (scramble competition, **no per-capita floor**) falls as local density rises →
reserves drain → nutrition-synergy raises `a2` and, at the extreme, the starvation backstop fires.
**BUT** this is a system with a **mortality lag** (~`reserve_full/burn` steps): an intrinsic +3.3%/yr
growth + a saturating resource + a lagged mortality response is the textbook recipe for
**overshoot-and-collapse or oscillation**, NOT guaranteed smooth logistic settling. A-3's clean 133k
attractor is **no evidence** — it was a *frozen, non-reproducing fill* (births=deaths=0), not a growing
population hitting a wall. **§5 stage 2a-pre tests this empirically before anything else.** If 2a-pre
shows collapse/oscillation, the modulators become load-bearing for *stability*, not just for shifting
the equilibrium down — which changes §3's whole free-knob framing. IF settling is stable, the
modulators then shift the equilibrium **downward**:
- terrain risk → high-exposure cells under-populated;
- density-disease → crowding penalized before starvation;
- pathogen → high-NPP (wetland/forest) cells become productivity-vs-disease tradeoffs.

**IF 2a-pre confirms stable settling**, Step 2 is **not** "tune knobs until r=0" — it is "the
lit-anchored modulators set *how far below the food ceiling* the carrying capacity sits, and *how the
population sorts* across terrain." The deliverable is that number, that spatial structure, **and the
demonstrated stability**.

---

## 5. Staging within Step 2

- **2a-pre — STABILITY TEST (red-team B-1; do FIRST).** Run the Step-1 demography on a *small* terrain,
  modulators OFF, and **plot the population trajectory**: does the +3.3%/yr population settle smoothly, or
  overshoot → oscillate / collapse against the food wall? Resolves the §4 hypothesis *empirically* before
  any modulator work. **Gate: bounded settling** (post-peak trough not below a pre-registered % of
  equilibrium; no extinction across seeds). If it collapses/oscillates, **STOP** and redesign (per-capita
  harvest floor? movement damping? modulators promoted to stabilizers) before proceeding.
- **2a — demography on terrain, modulators OFF.** With stability established, confirm Step-1 vital rates
  survive the spatial economy and the **modulators-off equilibrium lands within a tight band of the A-3
  133k food ceiling** (the conservation invariant, §6) — the upper bound.
- **2b — modulators ON (ablation).** Enable each flag in turn, then all together; measure each one's
  downward shift of the carrying capacity and its spatial fingerprint; calibrate the density-disease lever.
- **Scale discipline (red-team m-1):** a *rescaled* 50×50 world is a DIFFERENT world (different biome mix;
  doubled perimeter:area → different edge crowding) and does NOT transfer to 100×100. Calibrate on a
  **100×100 sub-window / same-resolution patch**, not a shrunk world. The 100×100 confirmation is itself a
  falsifiable check (small-scale `δ, ρ_half` must reproduce the CDR band + spatial correlations within
  tolerance, else transfer rejected). **Runtime: generations of turnover (thousands of steps) with
  per-agent Siler draws at ~10⁵ agents — plausibly hours and OOM-risky** (A-3 was 2.8 GB / ~20 min
  *frozen*); use `progress.txt`, crash-safe saves, population-cap lessons; budget it before the full run.

---

## 6. Validation gate (Step-2 GREEN requires all)

0. **Bounded stability (red-team B-1):** post-settling population is bounded — peak-to-trough oscillation
   below a pre-registered threshold, no extinction across seeds. "r→0 over the back half" alone is NOT
   sufficient (a collapsing/oscillating run can spuriously satisfy it).
1. **r → 0 at a spatial equilibrium** with **births ≈ deaths > 0** and **CDR in the Aché stationary band
   (~40–60 per 1000/yr)** — the stationary CDR band applies here (unlike Step-1's growing population).
2. **Aché vital rates survive on terrain:** realized IBI/TFR and l(x) within band of Step-1 — measured
   **with the energetic fertility modifier LIVE** (red-team M-3: it was neutral in Step-1, so turning it
   on will drift the rates → re-confirm).
3. **Conservation invariant (red-team M-1):** with all modulators OFF, the demographic CC lands **within a
   tight band of the A-3 133k food ceiling** — NOT just "below it" (near-tautological, since every
   modulator is ≥1). Far-below-with-modulators-off ⇒ the demographic core is silently breaking the economy.
4. **Pre-registered QUANTITATIVE spatial predictions (red-team M-1)** — declared before the run, with
   magnitudes: e.g. occupancy–risk rank correlation ρ ≤ −0.4; occupancy–pathogen ρ ≤ −0.3. "Correlates"
   without a signed magnitude is unfalsifiable.
5. **Ablation-additivity check (red-team M-1):** the sum of isolated single-modulator CC shifts ≈ the
   all-on shift (within a stated interaction tolerance). A miswired modulator breaks additivity — the test
   a wrong wiring FAILS.
6. **`a2_eff` cap diagnostics (red-team m-4):** report the fraction of agent-steps where the cap binds; if
   non-trivial, the cap is doing demographic work (flattening the sorting) and must be a parameter, not a
   guardrail.
7. **Rails:** no NaN/Inf, no sub-floor reserve survivors, no agents on water, determinism PASS; inherited
   ×12 units guard holds; **no `deaths_senesc` from a hard cap** (red-team M-3 — `max_age` removed, §7).

Ablation deliverable: each modulator flag on/off — its isolated effect on carrying capacity and turnover.

---

## 7. Seams & code-touch map

- **`phase1_model.py`:** swap the A-3 mortality/repro block for the `sic_games.demography` core (Siler
  `a2_mult` mortality + IBI reproduction + maternal + staggered founders); compute `a2_mult` per agent
  from the live modulators; keep CC-1 harvest field, substrate, water guard.
  - **REMOVE the hard `max_age` senescence cap** (`_make_agent` ~line 188; `age ≥ max_age` deaths). The
    Siler hazard has no cap — leaving it gives Siler + a residual hard cap → the synchronized senescence
    wave A-3 warned about. Add a rail asserting no hard-cap senescence deaths (red-team M-3).
  - **Separate mortality channels in reserve-space (red-team M-3):** the starvation backstop fires ONLY at
    `reserve ≤ floor`; nutrition-synergy `M(reserve)` operates ONLY for `floor < reserve < full`. No agent
    charged for "death by undernutrition" twice/step; verify with cause counters (`deaths_starv` vs
    `deaths_baseline`).
  - **Confirm the harness passes the CC-1 `harvest_field`** (red-team n-2): the A-3 default falls back to
    raw `terrain_field` forage (under-estimates extractable rate) — the fallback would make the 133k
    comparison apples-to-oranges.
- **`terrain.py`:** new `pathogen` field (flagged); `risk` field wired (already exists).
- **`config.py` / `demography.py`:** add the modulator constants (`risk_ref` + risk max-cap, `π`,
  `NPP_half`, `μ_max`, `δ`, `ρ_half`) AND `fertility_energetic_slope` — **count the last as a free knob**
  (the energetic modifier going live is a new, unvalidated coupling; red-team M-3).
- **New harness:** `outputs/phase1_demography_step2/` — 2a-pre / 2a / 2b runs + ablation + report.

---

## 8. Open items / dependencies

| Item | State |
|---|---|
| **M-3 sex-split** | **LANDED 2026-06-18** — sex-specific Siler via the H&H 1996 forest ratios (childhood M:F 0.71 → female-higher `a1`; adult M:F 1.47 → male-higher Gompertz `a3`; Makeham `a2` shared). Maternal folded in (approach (ii)). Vital rates hold (IBI 37/TFR 8, r=+3.3%), 11 demography tests, suite 442. **The headline-CC blocker is cleared.** *Remaining (not a Step-2 blocker):* approach-(a) maternal-removed fit (needs the Aché maternal rate); the ratio-split is a level approximation (age-specific sex curves are in monograph figures). |
| Pathogen SEM coefficients (`π`, `NPP_half`) | extract from Tallavaara Zenodo 1069787 (RTL-table parse, as for G&K) |
| Synergy `μ_max` | undernutrition×infection lit anchor (find/confirm a reference) |
| Scale/perf at 100×100 | calibrate on 50×50; confirm once at 100×100 |
| Infanticide | flagged, off (optional) |

---

## 9. Literature anchors

Inherited: Gurven & Kaplan 2007 (Siler, confirmed), Hill & Hurtado 1996 (Aché life table + fertility +
sex tables), Siler 1979, Tallavaara 2018 (pathogen + NPP), Guernier 2004, Dunn 1968 / Houldcroft &
Underdown 2023 (density-disease scope). Comparanda: Howell (!Kung), Blurton Jones (Hadza). New for
Step 2: an undernutrition×infection-mortality reference for `μ_max` — **to find**.

---

## 10. Independent-review checkpoint (required before lock)

Per the 2026-06-18 workflow: an **independent, repo-grounded red-team** (fresh-context sub-agent /
fresh session / `/code-review ultra`) + the supervisor must review before any code is written. Focus:
(a) does r→0 genuinely emerge, or is it smuggled in by a free knob? (b) is the free-knob set really ≤
the gate targets, given four modulators? (c) is the "food provides r→0, modulators only shift it down"
mechanism sound? (d) does the gate falsify a wrong wiring? (e) scale/perf realism.

---

## 11. Red-team revision log (v2 — independent review 2026-06-18)

Independent repo-grounded red-team. **Verdict: NEEDS REVISION before lock** (the central food→stable-r≈0
claim was unproven). Dispositions:

**Applied in v2 (inline):**
- **B-1 (BLOCKER) — food→stable r≈0 asserted; A-3 evidence invalid (frozen fill ≠ growing pop).** Reframed
  §4 as a HYPOTHESIS; added stage **2a-pre stability test** (§5) + a **bounded-stability gate item 0** (§6).
  Lock now depends on the 2a-pre empirical result.
- **M-1 — gate couldn't falsify a wrong wiring; "CC below 133k" tautological.** Added the **conservation
  invariant** (modulators-off ≈ 133k), **pre-registered quantitative spatial predictions** (signed ρ
  magnitudes), and the **ablation-additivity check** (§6 items 3–5).
- **M-2 — free-knob count understated (~6, not ≤2).** §3 reclassified: pathogen + synergy are FREE until
  anchors extracted; risk needs its *scale* pinned (max-cap), not just the mean.
- **M-3 — three seam collisions.** §7: (1) **remove the hard `max_age` cap** (+ rail); (2) **separate
  starvation vs synergy in reserve-space** (no double-count); (3) the **energetic fertility modifier going
  live is a new coupling** → re-validate IBI/TFR with it on (§6.2), count `fertility_energetic_slope` free.
- **m-1 — scale transfer.** §5: calibrate on a 100×100 **sub-window**, not a rescaled 50×50 world; 100×100
  confirmation is a falsifiable transfer check; runtime/OOM budgeted.
- **m-2 — both-sexes CC biased LOW.** §8: M-3 sex-split is a **hard dependency** for the headline CC.
- **m-3 — density-disease ρ** defined as **agents/km²**, not cell-size-dependent occupancy (§3).
- **m-4 — `a2_eff` cap.** §6.6: report the cap-binding fraction; if non-trivial, treat as a parameter.
- **n-1/n-2/n-3:** wetland tradeoff phrased as a prediction; confirm the harness passes the CC-1 harvest
  field; the +3.3% start rate is itself provisional (both-sexes).

**Net (updated 2026-06-18):** (1) 2a-pre RUN → **BOUNDED SETTLING** (settled_peak 1.01× / trough 0.90×,
3 seeds, plateau ~95% of food ceiling) — **B-1 RESOLVED**: food alone stabilizes (the fast ~1-step
reserve brake gives smooth logistic settling, no overshoot), so the modulators are NOT load-bearing for
stability and the free-knob accounting stands; (2) M-3 sex-split **LANDED**; (3) the pathogen/synergy/risk
anchors remain — **the only gate left before lock.**

---

*Phase 1 Demographic Stage · Step 2 · **DRAFT v2** 2026-06-18 (red-teamed) · C-only, forage-only · Step-1
demography FIXED; the food→stable-r≈0 mechanism is a HYPOTHESIS pending the 2a-pre test; ~6 free/soft-free
knobs to pin or cover; M-3 sex-split is a hard prerequisite. Open items: §8, §11.*
