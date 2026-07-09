# SiC Games — Pre-Run Audit (substrate scale run "A"), 2026-07-08

**Purpose.** Before committing hours to the substrate scale run, confirm it is *valuable and not reliant on
errors/typos*. Two gates: (1) diagnostics correctly wired; (2) re-check every constant for — incorrect lit read,
memory-value-not-verified, bad code, unwired/off mechanism, placeholder due for update.

**Framing (important).** Run A is a **qualitative prerequisite probe** — "does the population overshoot/bust? does
stratification emerge at capacity?" Its VALIDITY therefore depends on **mis-wiring / bad code / order-of-magnitude
errors / dead mechanisms**, NOT on the precision of every PROVISIONAL constant (that is *quantitative calibration*,
a concern for later calibrated runs). So this audit prioritizes: does anything make the qualitative answer an
artifact? Provisional-value precision is logged as an interpretability caveat, not a blocker.

---
## Gate 1 — Diagnostics wiring

**Raw state present & correct:**
- `births_this_step`, `deaths_starv_this_step`, `step_count` — reset each step, incremented in the live paths. ✓
- Reproduction paths **mutually exclusive** (`_do_births_ibi` for the demographic stack vs legacy asexual `_do_births`
  — `if/elif` at phase1_model.py:495/497). **No double-count.** ✓
- Mortality: Siler roll → `elif age≥max_age` **backstop** (not additive) → starvation death path. No double mortality. ✓
- `_cell_society` / `_band_society` dicts = the **stratification signal** (society type per cell/band). ✓
- Accessors exist: `bands()`, `genetics()` (H, mean relatedness), `connubium()`.

**GAP — derived metrics the run needs have NO accessor; the harness MUST compute them (and be verified):**
1. **Total deaths** — only `deaths_starv_this_step` is tracked. Total deaths = infer from Δpop + births, or add a counter.
2. **Inequality (Gini)** of cred/wealth — pieces exist (cred, wealth) but no aggregate is computed.
3. **Society mix / % stratified** — compute from `_cell_society`/`_band_society` (the key stratification-emergence metric).
4. **Village count / size** — from `_settlement_sites`.
5. **Instability proxy** — does not exist (no conflict/PSI mechanism; see the Turchin-layer gap, separate note).

→ Action: build these in the harness with unit-checks; they are the run's actual output.

---
## Gate 2 — Constants register (run-A-critical first)

### VERIFIED wired + anchored (spine)
| Constant | Value | Status |
|---|---|---|
| Siler mortality a1..b3 | Aché-anchored | VALIDATED (e₀=36.5, l15=0.66; PDF spot-checked, per memory/LIT) |
| Binford packing (morph trigger) | 0.091/km² | Lit-anchored (Binford 2001); morph fires per-cell at capacity ✓ |
| Testart surplus morph gates | 0.5 / 0.7 surplus_frac | Lit-concept (Testart 1982); thresholds reasonable |
| BURN | 2500 kcal/day | NOMINAL adult HG — standard ✓ |
| Capacity (Tallavaara) | segmented NPP→density | VALIDATED (R-36/R-58) |
| GD-1 depletion r/yr | per-biome | Lit-anchored (Coe/Cortés/Tallavaara, R-58) — PROVISIONAL magnitudes but grounded |
| Alpine tree-line | 10.0 °C warmest-month | CORRECTED this session (was mis-slotted 6.4; Köppen/Körner) |

### FLAGGED — by the requested risk categories (run-A relevance noted)

**(a) Incorrect lit read** — one found & fixed this session (**tree-line 6.4→10.0**, soil-vs-air framing). No other
confirmed lit-read error yet; highest remaining risk = LITERATURE entries marked "REFERENCE (web abstracts; PDF not
filed)" (river temp, salmon coldness, mobility gradient) — NONE are run-A-critical. **Recommend: targeted re-read of
the run-A-critical anchors only** (return-rate kcal tables, mu_max, storage thresholds) if we later go quantitative.

**(b) Value from memory, not verified lit** — the *emergent* thresholds we derived are model-internal, not lit:
`cv_safe=0.14`, `band_size_min=15`, `cv_min=0.4` (band size); `mate_search_min_eligible m*=3` (connubium). These are
DESIGN choices validated against outcomes (band ~24), not lit values — fine for a qualitative run, label as such.

**(c) Bad code** — none found in the run-A hot paths (repro dispatch, mortality, morph, births/deaths counters all
clean). Broader scan pending but no defect surfaced.

**(d) Unwired / off mechanisms**
- `enable_infanticide` — **DEAD STUB** (no logic reads it); documented. Harmless (off). Consider deleting.
- `society_from_character` — WIRED (was historically "never called"); fires at capacity. ✓
- Turchin structural-demographic layer (elites/extraction/overproduction/instability→mortality) — **ENTIRELY ABSENT**
  (separate strategic note). Run A cannot show *secular cycles*, only Malthusian dynamics + stratification emergence.

**(e) Placeholders due for update** (drive run-A dynamics — plausible but not anchored):
- `reserve_full_kcal=100k`, `reserve_floor_kcal=20k` [PLACEHOLDER MR-1] — set the **starvation-bust threshold**.
  Physiologically plausible (~body-fat store / ~40% BW-loss death) but not rigorously anchored. **Matters for the bust.**
- `fecundability=0.12`, `ibi_refractory_months=30` [FREE] — set the **birth rate / growth**; calibrated to IBI~37, ok.
- `lifespan_months=900` [PLACEHOLDER] — backstop only; minor.
- Climate seasonality amplitudes (per-biome) [PROVISIONAL]; `mu_max=2.5` (Pelletier nutrition synergy) [PROVISIONAL].
- Village/settlement/morph thresholds: `settle_min_pool=40`, `village_gain=5.0` (UNANCHORED), `morph_aq/npp` gates,
  `aggl_*`, `soil_*` [all PROVISIONAL] — shape *whether/where villages+stratification form*. **Most run-A-relevant
  provisional cluster** — but as gates on a qualitative "does it emerge" question, order-of-magnitude is what matters.

### Interpretability caveat (headline)
Run A's **quantitative** outputs (exact equilibrium pop, exact densities, exact %stratified) rest on the PROVISIONAL
cluster above and should be read as provisional. Its **qualitative** findings (overshoot vs glide; does stratification
emerge at all; does structure discretize at capacity) are robust to those, *provided* nothing is mis-wired or
grossly wrong — and the spine checks above found no such defect.

---
## Proposed actions (reversible / for consideration)
1. **Harness (new file, additive):** build the time-series logger + the 5 derived metrics (total deaths, Gini,
   society-mix, village count/size, + genome/connubium sampling), progress-flush + checkpoint. No model change.
2. **On a branch (`prerun-audit-fixes`), reversible:** delete the `enable_infanticide` dead stub; add a total-deaths
   counter; (optional) re-anchor `reserve_full/floor` to a cited body-composition figure. Each isolated + bit-exact-off.
3. **Deferred (not blocking run A):** primary-lit re-read of the run-A-critical anchors *if* we move to quantitative
   claims; the Turchin structural-demographic layer (its own project).

---
## Deeper audit — primary-lit re-verification of run-A-critical anchors (2026-07-08)

Per request, re-checked the run-A-critical anchors against primary/secondary lit (web-verified):

| Anchor | Value | Verification | Verdict |
|---|---|---|---|
| **Binford packing** (morph trigger) | 0.091/km² | Binford 2001 = **9.098 persons/100 km²** = 0.091/km² (web-confirmed) | **CORRECT** ✓ — the single most important stratification gate is right |
| **Return-rate FORAGE/GAME kcal** | per-biome | Each value provenance-tagged (Hill 1987, Berbesque&Marlowe 2009, Hurtado&Hill 1987, O'Connell&Hawkes 1984, Bird 2009, Cunningham, Rhode 2015); defers to Resource Table §3.2 | PROVISIONAL but grounded; no lit-read error |
| **MEAT_FRAC** (Cordain 2000 T2) | 0.55/0.45/0.38/0.66 | Arithmetic re-derived from Table 2 midpoints — all four exact (e.g. forest 50.5/91=0.555) | **CORRECT** ✓ |
| **mu_max** (Pelletier 1994) | 2.5 | Pelletier: malnutrition→mortality multiplicative/exponential; severe 5–8× → 2.5 cap is CONSERVATIVE (child data applied broadly) | plausible, provisional, no error |
| **reserve_full/floor** | 100k/20k kcal | body-fat store ~85–113k kcal (60 kg @ 15–20% fat); ~40% BW-loss death limit — magnitudes defensible | PLACEHOLDER, physiologically plausible |
| **village/settle knobs** | `village_gain=5.0` (UNANCHORED), `settle_min_pool=40` (PROVISIONAL "Natufian dozens+") | DESIGN knobs, no primary lit | tuning knobs — shape village SPECIFICS; "do villages form at all" is more robust |

**Deeper-audit conclusion:** the run-A-critical anchors that could make the qualitative answer an *artifact* — the
morph/packing trigger and the biome economy — are **correctly read** (Binford exact, return-rate arithmetic exact,
Cordain exact). No new lit-read error (the tree-line was the only one, fixed). The remaining softness is the
**unanchored village/settle tuning cluster**, which affects village *specifics* not *whether structure emerges*.
**Verdict: run A is safe to run as a qualitative probe; document the provisional cluster as a quantitative caveat.**

---
## Anchoring applied (branch `prerun-anchoring`, 2026-07-08 — reversible, for consideration)

1. **Starvation-bust threshold — ANCHORED to Cahill 1970.** `reserve_full_kcal 100k → 130k` (lean-adult total
   mobilizable fuel; floor 20k kept ≈ 3 kg-fat death residual). Survival runway 32 d → **44 d** total starvation
   (lean-adult range). Rationale: the flat-burn model (no adaptive hypometabolism) at 100k was too fragile (32 d),
   exaggerating bust sharpness — the exact thing run A measures. Sim sane (pop 707, no die-off). **Breaks downstream
   tests that pin the old equilibrium (expected for a recalibration) — adopt only if you accept the new baseline.**
2. **`settle_min_pool=40` — ANCHORED-lower-bound (Bar-Yosef 1998).** Value kept; now cited as the Natufian
   small-settlement lower bound (settlements dozens→100–150).
3. **`village_gain=5.0` — NOT fake-anchored.** It is a pure tuning knob with no single lit value; its *principled*
   anchor is the **emergent-village-size** mechanism (deferred project). Interim: the lit target is villages **50–150**
   (Natufian/Bar-Yosef); **run A should CHECK realized village sizes against 50–150** and we adjust `village_gain`
   (or build emergent village size) accordingly. Flagged as a decision, not silently tuned.
4. **Binford packing 0.091, morph Testart gates, morph_npp_floor (R-47 data-derived)** — left as-is (0.091 verified
   correct; the rest are reasoned design/data thresholds, not single-lit-value anchorable).

*Audit 2026-07-08. Living document — extend as verification continues.*
