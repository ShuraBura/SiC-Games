# SiC Games — Phase 1 Demographic Stage · STEP 2 Blueprint
## Terrain-Modulated Demography on the Full World

**Status:** DRAFT — for supervisor review and an independent red-team pass before lock.
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
| Terrain risk `R` | `risk(cell)/risk_ref` | `risk_ref` | **PINNED** = mean land risk (normalization, ≈1 average); not free |
| Density-disease `D` | `1 + δ·ρ/(ρ+ρ_half)` | `δ, ρ_half` | the **primary free lever** (endemic/zoonotic; Dunn/Houldcroft — modest) |
| Pathogen `P` | `1 + π·norm(wateracc)·s(NPP)` | `π, NPP_half` | **PINNED** to Tallavaara 2018 SEM coefficients (Zenodo 1069787) |
| Nutrition synergy `M` | `1+(μ_max−1)(1−clamp(reserve))` | `μ_max` | **PINNED** to the undernutrition×infection lit (~2–3×) |

**Degrees-of-freedom discipline (M-1 invariant):** three of four modulators are pinned by their lit
anchors; the density-disease pair is the only genuinely free lever, calibrated against the r→0
equilibrium. **# free knobs (≤2) ≤ # gate targets.** New terrain `pathogen` field added to `terrain.py`.

---

## 4. How r→0 emerges (the mechanism — read before the gate)

**r→0 does NOT require the modulators.** The CC-1 cell capacity already makes food density-dependent:
as local density rises, the per-capita harvest share falls below maintenance → reserves drop →
(a) the nutrition-synergy raises `a2`, and (b) at the extreme, the starvation backstop fires. So even
with all modulators OFF, the growing Aché population is checked by **food** at ≈ the A-3 food ceiling —
but now with continuous turnover (not frozen). The modulators then shift the equilibrium **downward**:
- terrain risk → high-exposure cells under-populated;
- density-disease → crowding penalized before starvation;
- pathogen → high-NPP (wetland/forest) cells become productivity-vs-disease tradeoffs.

So Step 2 is **not** "tune knobs until r=0" (r→0 is guaranteed by density-dependent food). It is "the
lit-anchored modulators set *how far below the food ceiling* the demographic carrying capacity sits, and
*how the population sorts* across terrain." The deliverable is that number and that spatial structure.

---

## 5. Staging within Step 2

- **2a — demography on terrain, modulators OFF.** Confirms the population grows from staggered founders
  to a turnover equilibrium at ≈ the A-3 food ceiling (sanity: Step-1 vital rates survive the spatial
  economy; r→0 via food; births≈deaths>0). Establishes the *upper bound*.
- **2b — modulators ON (ablation).** Enable each flag in turn (risk, density-disease, pathogen,
  synergy), then all together. Measure each one's downward shift of the carrying capacity and its
  spatial fingerprint. Calibrate the density-disease lever.
- **Scale discipline:** the full 100×100 (~10⁵ agents, multi-generation) is heavy (A-3: 2.8 GB, OOM
  risk). **Calibrate 2b on a smaller grid (e.g. 50×50) first**, then one confirmation run at 100×100.
  Use the A-3 harness lessons: `progress.txt`, crash-safe incremental saves, unbuffered output.

---

## 6. Validation gate (Step-2 GREEN requires all)

1. **r → 0 at a spatial equilibrium** (the demographic carrying capacity), with **births ≈ deaths > 0**
   and a **crude death rate now in the Aché stationary band (~40–60 per 1000/yr)** — at the *stationary*
   equilibrium the CDR band applies (unlike Step-1's growing population).
2. **Aché vital rates survive on terrain:** realized IBI/TFR and l(x) stay within band of Step-1 (the
   spatial economy must not silently break the calibrated demography).
3. **Demographic carrying capacity reported vs the A-3 ~133k food ceiling** — expected **below** it;
   quantify the gap and attribute it across modulators (ablation table).
4. **Spatial sorting:** occupancy correlates with terrain (low-risk/low-pathogen/high-NPP cells carry
   more); high-risk and high-pathogen cells under-populated. The productivity-vs-disease tradeoff visible
   in wetland/forest occupancy.
5. **Rails:** no NaN/Inf, no sub-floor reserve survivors, no agents on water, determinism PASS; the
   inherited ×12 units guard still holds.

Ablation deliverable: each modulator flag on/off — its isolated effect on carrying capacity and turnover.

---

## 7. Seams & code-touch map

- **`phase1_model.py`:** swap the A-3 mortality/repro block for the `sic_games.demography` core (Siler
  `a2_mult` mortality + IBI reproduction + maternal + staggered founders); compute `a2_mult` per agent
  from the live modulators; keep CC-1 harvest field, substrate, water guard.
- **`terrain.py`:** new `pathogen` field (flagged); `risk` field wired (already exists).
- **`config.py` / `demography.py`:** `DemographyConfig` already has the flags + fertility; add the
  pinned modulator constants (`risk_ref`, `π`, `NPP_half`, `μ_max`) + the free `δ, ρ_half`.
- **New harness:** `outputs/phase1_demography_step2/` — 2a/2b runs + ablation + self-contained report.

---

## 8. Open items / dependencies

| Item | State |
|---|---|
| **M-3 sex-split + maternal-removed female Siler** | The Aché monograph (Hill & Hurtado 1996) is FILED and **machine-readable (digital, 592 pp)** — extract the sex-specific life tables to replace the both-sexes schedule. Do this **before** Step-2 lock so the +3.3% (both-sexes) → real sex-specific rates. |
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

*Phase 1 Demographic Stage · Step 2 (terrain-modulated demography) · DRAFT 2026-06-18 · C-only,
forage-only · Step-1 demography FIXED; only terrain-modulator knobs calibrated; pathogen + synergy
anchors pending; M-3 sex-split to land first. Open items: §8.*
