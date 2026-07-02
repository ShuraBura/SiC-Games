# SiC Games P1 — CC-1: Full Tallavaara Carrying-Capacity + OPT-1 (SCOPING + RED-TEAM)

**Goal.** Replace the **provisional** cell-capacity field — a hand-drawn linear-clamp `density = min(0.5,
0.3·npp/1360)` people/km² (§4.3.1) — with **Tallavaara et al. 2018's actual fitted NPP→density regression** (the
lit-grounded carrying-capacity ceiling), and fold in **OPT-1** (cache the climate temporal multiplier per step,
~25% perf, bit-exact; audit R-34). Then re-validate the whole stack against the fresh canonical re-baseline.

**Framing correction (important).** CC-1 is NOT the bare-forage→NPP jump — that already happened (the provisional
`NPPCapacityField`/`SubWindowCapacity` is already NPP-derived + Tallavaara-cited, giving the ethnographic ~0.1–0.5
persons/km²). CC-1 is the **linear-approximation → real-regression** fidelity upgrade. So it is a *refinement of a
working field*, not a rescue of a broken one — lower-risk than the original "RECAL-A" framing, but it still shifts
the spatial capacity distribution → the whole social stack must be re-validated.

**Governing principle.** Foundational-substrate change → supervisor sign-off; re-validate every headline result.

---

## What CC-1 changes

1. **Density formula (the core).** Provisional `min(0.5, 0.3·npp_gm2/1360)` → **Tallavaara 2018's fitted
   NPP→density relation** (their result is a *saturating* curve, not linear+hard-cap). The paper's coefficients
   are non-text-extractable (Fig 3 + Table S1, SI not in the filed PDF), BUT **their data + R script are on Zenodo
   record 1069787** — the regression is reconstructed from there. NPP-ONLY main term.
2. **OPT-1 perf.** In `ClimateField.level`, cache `mean_factor·season()·regime()` once per `set_step` (cell-
   independent), keeping only the per-cell `interannual_at` inline. Bit-exact (t constant within a step; R-34).

## What CC-1 does NOT include (stay deferred)

- **Biodiversity + pathogen SEM terms.** Tallavaara's full model is an SEM (NPP + biodiversity + pathogen stress).
  The pathogen path is already deferred to §4.6.3 (anchored to real T/humidity when CL-1 lands) and biodiversity is
  a separate channel. CC-1 = the **NPP→density main effect only**; biodiv/pathogen stay OFF, documented.
- **Full-grid rivalry (drop the patch mask).** The patch sub-window bounds K so the population equilibrates
  (the validated harness). Going full-grid changes the entire population regime → change ONE thing at a time:
  **KEEP the patch mask** for CC-1 (isolate the density-formula effect); defer full-grid to its own step.

## Data / lit step (the key deliverable)

Fetch **Zenodo record 1069787** (Tallavaara 2018 data + R script) → extract the actual NPP→density functional form
+ coefficients + their NPP units (reconcile with our `npp_gm2 = npp·3400`). Deliverable: a documented
`density_tallavaara(npp_gm2)` with the real curve, filed method in MODEL_SPEC §4.3.1 (replacing [PROVISIONAL]).
If the Zenodo fetch fails (supervisor may need to grab it), the provisional stays and CC-1 blocks on the data.
Lit: **Tallavaara, Eronen & Luoto 2018** (PNAS 115(6):1232–1237; FILED) — the density~NPP saturating relation.

## RED-TEAM

1. **Recalibration burden (the big one).** R-18…R-36 all ran on the provisional field. The new curve redistributes
   capacity → eq_pop, band packing, status→RS, R-18 death-deficit all shift. → re-run the canonical validations on
   CC-1; report the deltas vs the re-baseline; re-pin anything that moved (e.g. `ascribed_mate_strength` if
   status→RS drifts off 0.13). Budget for it — that IS the audit→CC-1→compare sequence.
2. **Shape change.** Linear+cap vs a saturating curve differ most at MID and HIGH NPP. → compare the per-cell
   capacity maps (provisional vs Tallavaara) before running; sanity-check the density range stays ethnographic
   (~0.01–1/km²).
3. **Absolute scale / perf.** If Tallavaara's max density > 0.5/km², eq_pop rises → perf (the big run). Check the
   scaled `E/burn` = people/cell stays tractable; OPT-1 helps.
4. **NPP units.** Their NPP (g C/m²/yr? total g/m²/yr?) vs our `npp_gm2`. Get the units right or the whole curve is
   mis-scaled. Verify against the ethnographic density anchor (a rich-forest cell should give ~0.5–1/km²).
5. **Patch-mask retained.** Confirm CC-1 keeps the sub-window mask (comparability); full-grid is a separate step.
6. **OPT-1 bit-exactness.** The climate-cache must reproduce `level()` exactly (unit test: cached == uncached over
   a run). Guard the llanos/caribou per-cell terms (they stay per-cell).
7. **Ablatable / reversible.** Keep the provisional field selectable (a flag or the old class) so the re-baseline
   stays reproducible.

## Validation

- **Re-baseline (running):** canonical config (ascribed a=2.5) on the PROVISIONAL field = the reference.
- **CC-1 run:** same canonical config, Tallavaara field → clean substrate-only diff.
- **Targets:** capacity-map sanity (ethnographic densities); eq_pop shift documented (not a failure — a
  recalibration); bands ~25 preserved; **status→RS ~0.13 preserved or re-pinned**; R-18 death-deficit > 0; no
  extinction; perf acceptable at scale (OPT-1). The **big comparison run** (baseline vs CC-1) is the milestone.

## Sequencing

fetch Zenodo 1069787 → fit `density_tallavaara` (+ units check) → implement `NPPCapacityField` v2 (density swap;
provisional kept selectable) + OPT-1 caching + unit tests → **re-validate vs re-baseline** (deltas; re-pin if
needed) → **big comparison run** → MODEL_SPEC §4.3.1 [PROVISIONAL]→[FITTED], PARAMETERS, RESULTS → commit. Then
the settlement arc (which also revisits the ascribed-mate-choice stratified endpoint). Non-blocking: the model
already works on the provisional field; CC-1 is a fidelity + milestone upgrade.
