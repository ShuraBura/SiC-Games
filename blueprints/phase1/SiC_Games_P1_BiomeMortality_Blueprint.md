# SiC Games · Phase 1 · **Biome Mortality** — total age-specific mortality per dwelling biome

**Status:** vNext — red-team v1 addressed (§7b); **building S0**. Supersedes the cause-decomposition framing
of the Phase C provisioning blueprint per supervisor scoping: **the deliverable is *total* mortality q(x) by
age × biome, not separate cause channels** (channels only where needed for correctness). §2/§3 are the live
plan; §7/§7b retain the red-team record.

---

## 1. Goal & scope

Produce **emergent total age-specific mortality** for agents, and characterise **how it varies across the
dwelling biome** (terrain productivity / disease ecology). Validate the age-shape against the ethnographic
forager range (Aché forest baseline; cross-forager spread). **Not** a cause-decomposed output.

**Established upstream (RESULTS R-3…R-10):** demographic core (Siler+IBI) validated to the Aché; resource
ecology (seasonality, depletion, movement) only moves the carrying capacity — the population self-regulates
to "broadly well-fed at the biome's CC" (R-5/R-6); provisioning rescues the dependent class and, with
seasonality, produces a seasonal infant nutritional signal that currently routes (wrongly) through the hard
starvation floor (R-10). Cause data (MODEL_SPEC §4.2.7): precontact forager child **nutritional death ≈ 0**;
mortality is disease-dominated (+ frontier violence, excluded).

## 2. Conceptual model (vNext — red-team-corrected 2026-06-20)

Mortality from the **de-warfared Aché Siler** ("natural mortality" baseline, §4.6.1; e₀≈42–44), with the
**disease hazard** modulated by biome + body-condition, **mean-normalised per channel** so the Aché-forest
reference biome reproduces the baseline.

- **Disease-channel formulation (fixes red-team L-1 — "f_s≈0.36 of a2" was incoherent).** `a2` (Makeham) is
  the age-independent exogenous term; `a1` carries infant disease *but also infanticide* (do NOT scale
  that). Modulate the **disease-attributable hazard** by `M = condition × pathogen(biome) × density`,
  threaded through `hazard()` ONLY (never `cumulative_hazard()`/`survivorship()` — founder sampling + ×12
  guard + life-table test). Realised as **`a2` wholesale + an a1 infant-disease component above weaning**
  (so infanticide, unweaned, is untouched) — NOT "a fraction of a2."
- **Body condition (S0 — the critical path).** Disease potentiation reads a slow EMA of nutritional status
  (`_condition`, immune competence; α=0.25), so *sustained* undernutrition raises DISEASE mortality
  (Pelletier), routing the seasonal squeeze through **graded disease**, not the bang-bang starvation floor
  (R-8/R-10). Matches the data: child nutritional death ≈0, disease-dominated (§4.2.7).
- **pathogen(biome).** Anchored to **Cashdan 2014** prevalence-index-by-climate (temperature / frost-free /
  precipitation; SCCS societies incl. foragers; §4.6.3) for the **sign + shape + relative magnitude**; the
  residual prevalence→mortality is **bracketed** (low/mid/high) and reported as a sweep. Maps to terrain
  temperature+humidity (CL-1) + NPP. Crowd/zoonotic diseases excluded (agriculture-era).
- **Nutrition = seasonal, infant-concentrated modifier** (C.2b/seasonal), NOT the main biome signal —
  foragers self-regulate to CC, broadly fed regardless of biome richness (R-5/6, plausibly *correct*).
- **Baseline de-warfared** (frontier violence excluded as a dynamic); **violence module OFF** (§5); **bands
  seeded far apart → isolated per-biome populations, no mixing** (§6).

## 3. Build stages (resequenced per red-team — S0 is the critical path)

- **S0 — body-condition signal** [DONE → BANKED OFF; RESULTS R-11]. Built (`_condition` EMA, opt-in
  `enable_condition`), 444 green, **correct-but-inert** (provisioning tops children to cap → survivors at
  condition ≈1.0; under-cap children starve in ~1 step before the EMA moves; self-regulation attractor
  compounds). The *fine* graded-nutrition→disease channel is **over-engineering for total-mortality-by-biome**
  → **deferred to T-4** (two-part fix recorded there); kept as an opt-in flag.
- **S1 — child-priority shortfall-sharing** [DONE → KEPT ON; `provision_self_keep`<1.0]. Cuts lean-trough
  child starvation 33.7→18.2 (mothers absorb the squeeze; residual = orphans/failed-support = the data's
  infanticide cohort). Earns its place: drives child **nutritional** death → the Aché ≈0, giving the
  **coarse** cause-split (starvation-floor vs Siler-baseline `deaths_senesc`) the Biome stage validates.
- **S2 — disease-hazard formulation.** `a2`-wholesale + a1 infant-disease (weaning-gated) modulated by
  condition × pathogen × density, threaded through `hazard()` only, per-channel mean-normalised to the
  Aché-forest reference. **Regression test:** unmodulated life table byte-identical (RT-I2/I6).
- **S3 — de-warfared baseline + pathogen channel.** Re-fit the Siler to the de-warfared schedule
  (e₀≈42–44), re-validate the core; wire Cashdan-anchored pathogen(biome) + density-disease; calibrate μ_max
  + the bracketed pathogen magnitude.
- **S3.5 — multi-biome harness** [from scratch — none exists; RT-I3]. ≥3 isolated populations in
  low/med/high-NPP windows; per-population q(x); determinism; compute budget.
- **S4 — bracketed validation.** Total q(x) by age × biome; report **gradient vs pathogen-strength bracket**
  (not a point estimate, RT-L2); age-shape vs Aché; nutrition as the seasonal modifier; honest level offset
  (gradient+shape, Aché-anchored level — RT-L3).

## 4. Mean-normalisation (correctness, not cosmetics)

Per channel, `M(biome) = raw(biome) / raw(Aché-forest reference)`, applied to the **disease-attributable
hazard** (`a2` wholesale + the a1 infant-disease component) via `hazard()` — NOT to the whole Siler. ⇒ the
Aché-forest reference biome reproduces the (de-warfared) baseline exactly; other biomes deviate; the a3
senescence term and the a1 *infanticide* portion stay invariant (they are not biome/disease-driven). This is
what keeps the biome gradient from scaling non-disease mortality.

## 5. Violence module (designed, OFF by default)

Toggleable `enable_violence`. Hazard `h_v = base_v · scarcity_gate(local resource adequacy) · biome_gate`.
- **Intra-band interpersonal** (homicide/dispute): runnable in an isolated band; scarcity-gated. Default OFF
  (minor driver for mobile egalitarian foragers — Fry & Söderberg 2013).
- **Inter-band warfare**: requires contact ⇒ coupled with **mixing** ⇒ **deferred to the C-vs-Si conflict
  subsystem** (a future phase; emergent from civ competition over territory/resources, not a tuned rate).
- Frontier/colonial violence: **excluded permanently** (artifact).

## 6. Population seeding & isolation

Seed each biome's band **far apart** (separated by distance / uninhabitable terrain) so bands do **not mix**
→ each per-biome population evolves independently; no cultural-mixing dynamics to model. This is what makes
the per-biome mortality clean AND what defers the mixing question alongside inter-band conflict.

## 7. Red-team targets (challenge these)

**Logic.** RT-L1: the biome→mortality gradient may be *weak* once non-biome violence is removed — is
disease-ecology really the dominant biome channel, or is near-invariance the right answer? RT-L2: marginal
biomes (desert/arctic) do show higher mortality — is the channel disease, nutrition, or exposure/accident?
RT-L3: f_s≈0.36 is one coarse Aché number; sensitivity-test it. RT-L4: keeping the frontier-inflated baseline
as a constant offset — is the absolute level acceptable, or must we de-warfare (risking unrealistic e₀)?

**Implementation.** RT-I1: pathogen *richness* (Guernier) → mortality *rate* is unvalidated — is the
calibration honest/identifiable? RT-I2: modulators currently touch only a2; infant disease needs a1 — verify
the a1 reach is correct and doesn't double-count the sex-split. RT-I3: multi-biome infra — do isolated
per-biome populations reach stable equilibria; compute cost; determinism. RT-I4: mean-normalisation
reference = Aché-forest NPP — is it pinned correctly. RT-I5: S1 child-priority must not over-correct (drive
child mortality *below* realistic) — gate it. RT-I6: opt-in safety — every change flagged so the 444 suite
stays green.

## 7b. Red-team v1 (2026-06-20, sub-agent) — VERDICT: NEEDS REVISION (1 blocker, several majors)

**Blockers.** (B1/L-1) "Modulate only f_s≈0.36 of a2" is **mathematically incoherent**: `a2` is a scalar
Makeham *constant*; 0.36 is a fraction of *total* mortality (illness+accident), and the causes are spread
across a1 (infant disease + infanticide), a2 (exogenous), a3 (adult) — there is no "36% inside a2."
Reformulate: a2 IS the age-independent exogenous term (warfare/congenital largely live in a1/a3, already
invariant to an a2 multiplier) → either modulate a2 wholesale, or build an explicit additive biome-disease
component; drop the 0.36-of-a2 claim. (B2/I-1) The **pathogen modulator does not exist** (only the flag;
no `pathogen_mult`; `_a2_mult` never reads it) AND its Tallavaara SEM target is documented non-extractable
(§4.3.3) → S3 can't be honestly calibrated; re-scope to density-disease + a **bracketed-sensitivity**
pathogen term. (B3/I-3) The **multi-biome harness does not exist** — every run is one 40×40 window; S4 is a
from-scratch infra build (multi-window NPP selection, per-pop q(x), determinism, ~3× compute).

**Majors.** (L-2) "disease-ecology dominant / nutrition marginal" *assumes its conclusion* — with pathogen
unwired and density/synergy inert at equilibrium (R-5/6/7/8), S4 would report a near-zero gradient as an
**artifact**, indistinguishable from "biomes really are invariant." Pre-register a **bracketed gradient
sweep** (report gradient vs channel-strength), not a point estimate. (L-3) Keeping the warfare-inflated Aché
baseline as a constant offset corrupts the *level* of "total mortality" while claiming violence is excluded —
**internally contradictory**; reframe the deliverable to *gradient + age-shape, Aché-anchored level with a
documented offset*, or de-warfare. (I-2) a1 modulation hazards: a1 is sex-scaled AND contains infanticide
(modulating it by disease wrongly scales infanticide); any new mult must thread through `hazard()` only, NOT
`cumulative_hazard()`/`survivorship()` (founder sampling + ×12 guard + life-table test depend on the
unmodulated forms). (I-4) S1 shortfall-sharing-from-reserve fights the overflow-only design and risks
**over-correcting child mortality to ~0**, abolishing the R-10 variance instead of routing it to graded
disease — gate with a child-mortality floor (≥ Aché illness ~16–21/1000 mid-child).

**Critical-path catch (I-5).** The real R-10 blocker — the **bang-bang reserve** (a squeezed agent hits the
floor in ~1 step, too fast to dwell → synergy stays ~1) — is unaddressed; the disease channel stays inert
without a **lagged body-condition / immune-competence signal**. Insert it as **S0, before** the disease
channel, or S2/S4 re-confirm a false near-zero gradient.

**Resequenced plan:** **S0** lagged body-condition signal → **S1** *gated* child-priority provisioning (floor
≥ Aché illness rate; route squeeze to graded disease, don't abolish) → **S2** correct disease-hazard
formulation (explicit biome-sensitive component, threaded through `hazard()`, per-channel mean-norm; don't
scale a1-infanticide) → **S3.5** build the multi-biome harness → **S4** bracketed-gradient validation
(gradient vs channel-strength; honest level offset). Pathogen demoted to bracketed sensitivity until CL-1
climate lands real T/humidity.

## 8. Out of scope / deferred

Inter-band warfare + cultural mixing (→ C-vs-Si conflict subsystem; isolated far-apart seeding sidesteps
both now); cause-decomposed mortality **outputs** (total q(x) only); crowd/zoonotic diseases (agriculture-
era); the convex Kaplan η production curve (linear JV-1 in use); precise Cashdan β extraction (deferred to
the S2/S3 wire); real spatial/seasonal temperature+humidity (CL-1 climate stage — pathogen reads constants
until then). *(De-warfaring is now IN scope at S3, not deferred.)*
