# SiC Games · Phase 1 · **Biome Mortality** — total age-specific mortality per dwelling biome

**Status:** DRAFT for red-team (2026-06-20). Supersedes the cause-decomposition framing of the Phase C
provisioning blueprint per supervisor scoping: **the deliverable is *total* mortality q(x) by age × biome,
not separate cause channels** (channels only where needed for correctness).

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

## 2. Conceptual model (the "logic" to red-team)

`mortality(age, biome, t) = Siler_baseline(age)` with its **biome-sensitive fraction f_s modulated** by the
biome/condition modulators, **mean-normalised** so the **Aché-forest** biome reproduces the validated
baseline:

- **Biome→mortality is carried mainly by DISEASE ECOLOGY** (pathogen load varies strongly by biome —
  humid-tropical high, arid low; Guernier 2004 / Tallavaara), via `terrain-pathogen` + `density-disease`
  on the disease portion. Hypothesis, **exploratory not calibrate-hard** (the true gradient strength is
  uncertain; it may be modest — see RT-L1).
- **Nutrition is a SEASONAL, infant-concentrated modifier** (C.2b/seasonal), not the main biome signal —
  foragers self-regulate to their CC and are broadly fed regardless of biome richness (R-5/6, plausibly
  *correct* under this framing).
- **Baseline = validated Aché Siler kept AS-IS** (do NOT re-derive). Only the biome-sensitive fraction
  f_s ≈ 0.36 (Aché illness ~24% + accident ~12%, §4.2.7) is modulated; warfare/congenital remainder is a
  **constant, non-distorting offset** → frontier violence is never a dynamic (supervisor directive), and
  the biome *gradient* is clean. Absolute-level Aché offset noted as a caveat.
- **Violence = separate module, OFF by default** (§5). **Bands seeded far apart → isolated per-biome
  populations, no mixing** (§6).

## 3. Build stages

- **S1 — Child-priority provisioning.** Shortfall-sharing that protects children first → the seasonal
  *starvation* pulse (R-10, 68×) collapses toward ≈0 (matching the data). Re-run 2j as the check. Goal: stop
  the model *over*-killing children; child mortality should sit at realistic levels via the baseline, not
  the floor.
- **S2 — Biome-sensitive fraction + a1/a2 reach + mean-normalisation.** Split the baseline so the
  modulators scale only f_s, **on a1 (infant) AND a2 (Makeham)** — infant disease lives in a1 (RT-I2).
  Normalise so modulators ≈1 at the **Aché-forest reference NPP** (RT-I4).
- **S3 — Activate disease-ecology modulators.** `terrain-pathogen` (NPP/temperature/humidity-driven) +
  `density-disease`. Calibrate the *gradient* (not a single rate) against the cross-forager disease range,
  with explicit caveats (RT-I1: pathogen *richness* → mortality is an inferential leap).
- **S4 — Multi-biome validation.** Isolated populations in ≥3 distinct biomes (low/med/high NPP) →
  equilibrate → total q(x) by age × biome. Compare age-shape to Aché; report the emergent biome gradient
  (expect *modest*). Nutrition enters as the seasonal infant modifier.

## 4. Mean-normalisation (correctness, not cosmetics)

Modulator `M(biome) = raw(biome) / raw(Aché-forest-NPP)`, applied as `a_s' = a_s · M` on the sensitive
fraction only. ⇒ Aché-forest biome reproduces the validated baseline exactly; other biomes deviate. Prevents
the biome gradient from scaling the invariant (warfare/congenital) fraction.

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

## 8. Out of scope / deferred

Inter-band warfare + cultural mixing (→ conflict subsystem); full baseline de-warfaring; cause-decomposed
outputs; the absolute-level Aché offset cleanup.
