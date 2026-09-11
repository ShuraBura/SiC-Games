# Handoff — R-106 forager e0 arc (2026-09-10)

This note points the next session to the right files. It is a map, not the record: the formal record is
`docs/RESULTS.md` (Addenda 72–75) and the git history; the working state is in the assistant memory files listed
below.

## Status in one line

The harsh-biome e0 deficit is ANSWERED: it is a juvenile starving tail (a food-DISTRIBUTION problem, not a
quantity one). `enable_band_provisioning` is the grounded fix (temperate hits its survival anchor). Both new
mechanisms are default-OFF and NOT adopted — the canonical config is unchanged. `origin/main` is at `556a569`.

## Where the state lives

- **Formal record** — `docs/RESULTS.md`, Addenda 72–75 (append-only):
  - 72 — band autonomy: the preventive check is neither selectable nor consequential.
  - 73 — the e0 gap is the global packing paradox (a battery-harness artefact correction).
  - 74 — exogenous emigration hits the e0 anchors (later shown to be a density trade — see 75).
  - 75 — the deficit is a juvenile starving tail; band (alloparental) provisioning is the grounded fix.
- **Git** — `origin/main` @ `556a569`, pushed and in sync. Arc commits: `6617b05` (72), `46e51ac` (73),
  `5e190ef` (74), `556a569` (75).
- **Assistant memory** (the working handoff, per-project):
  - `project_sic_games_emigration_e0.md` — the full e0 arc: diagnosis chain, the fix, open items, the traps.
  - `project_sic_games_band_autonomy.md` — Addenda 72/73 detail.
  - `project_sic_games_mortality_metabolism.md` — the older mortality/metabolism arc context.

## The answer, briefly

1. On the CANONICAL config the population is NOT food-limited: mean intake is 3.2–5.25× maintenance.
2. The whole e0 deficit is starvation, but the Siler baseline schedule is generous (baseline-only e0 = 43–48,
   above the anchors). Removing starvation clears the deficit.
3. It is DISTRIBUTIONAL: ~41% of agent-observations are below maintenance, 99–100% of them on RICH cells, and
   they are LOW-efficiency YOUNG agents (eta ~0.4, age ~13–16). Realised intake = eta × forage-capped share
   ~0.7× burn for a juvenile. The mother-linked provisioning does not reach them.
4. FIX — `enable_band_provisioning` (default-off): co-resident adults feed the deficit of ANY juvenile in their
   food-sharing group from surplus, down to `band_provision_self_keep`·cap. Ethnographically foragers are net
   consumers until ~18–20 (Kaplan/Hill). On CANON, keep=0.5: temperate survival-to-15 0.61 → 0.67 (anchor),
   e0 32.8 → 34.4, adult mortality flat, DENSITY PRESERVED.
5. Emigration (`enable_sub_k_regulation`) is FALSIFIED as an adoption: grounding against the Tallavaara density
   anchor (which IS the ethnographic forager density) showed it hits e0 only by pushing density further below
   the anchor. Kept default-off as an ablatable instrument.

## Open items (next-session pickup)

- **Savanna adult-scarcity residual — DIAGNOSED + CLOSED (Addendum 76, 2026-09-10).** The PRE-transfer probe
  (`phase1_model.py` `_bp_probe` hook, bit-exact; `scratchpad/bp_savanna_probe.py`), on a 3-world × 3-replicate
  low-noise panel, shows the residual is Malthusian RELOCATION, not a donor-flow defect. Band provisioning is
  ZERO-SUM on starvation hazard in BOTH biomes (temperate Δ +0.01 ± 0.07, savanna Δ −0.00 ± 0.14 /1000
  person-months); it only ages the deaths (temperate +5.9y, savanna +8.2y, z=13). The 2-world "temperate −27%
  reduction" was world-lottery noise (RETRACTED). Temperate's Addendum-75 e0 gain is the age-shift, not fewer
  deaths; savanna's 2.6× higher death flux cancels it. No provisioning variant can close savanna e0; the fix is a
  food-economy / carrying-capacity change (tier-1/2). Addendum 76 + the probe hook are NOT yet committed.
- **Food-economy diagnosis — DONE (Addendum 77, 2026-09-10). NEXT ARC = the spatial lever.** The
  carrying-capacity shortfall is the PACKING PARADOX (`scratchpad/bp_foodchain.py`, `bp_reach.py`): the population
  uses only ~14% of the food-bearing land, clusters, and starves next to empty food — NOT seasonality (13–30%
  loss) or food quantity (aggregate density temperate ~74% / savanna ~46% of the ethnographic anchor). Two
  biome-specific channels for adult food-short agents (full-eta, not the juvenile tail): TEMPERATE = PULL (empty
  feeding cell adjacent + 97% reachable, but 59% stay put — sedentism/agglomeration override the food gradient);
  SAVANNA = REACH (feeding cells ~5 cells away, only 32% within the 1-cell/step move). The lever is SPATIAL
  movement (tier-1/2), not the food base. NEXT: tune ONE channel (cut the temperate pull / add a hunger-scaled
  residential stride for savanna) and re-measure density AND e0 together on the low-noise panel. NOT yet committed.
- **Adoption decisions deferred.** Emigration — keep off. Band provisioning — validated for temperate; decide
  adoption once the savanna residual is understood; `band_provision_self_keep` is [PROVISIONAL].
- **Other ladder misses** (independent of e0): band size (tier 5, model ~12 adults vs Hill 28.2 — the oldest
  failure and the lowest unvalidated tier); wealth Gini (tier 10, 0.16 vs BHM 0.36); fission ceiling (tier 9).

## Traps that cost time this arc (do not repeat)

- **`battery1_liveness._build(update, ...)` does NOT apply the canonical runconfig.** Its base is
  `emergent_village_demog + VILLAGE + ELITE` with ~45 adopted mechanisms OFF. ALWAYS pass
  `cfg = dict(runconfig.load()['DemographyConfig']); cfg.update(overrides)`. Omitting this understated e0 by
  ~10 yr and inverted several intermediate conclusions.
- **A new `enable_*` flag leaks ON via the C_ALLON campaign** unless it is added to the `_skip` set in
  `sic_games/outputs/substrate_run/run_campaign.py`. `gen_runconfig` resolves the canonical from C_ALLON, so a
  missing `_skip` entry writes the flag `true` into `config/mechanisms.toml` and breaks the CTBs that load
  canonical (density_fertility, age_structure, ...).
- **e0 noise is dominated by the WORLD LOTTERY** (each seed draws a different world). Fix the world seed and vary
  only the demographic seed to cut the SD 2–3×; calibrate on a panel of a few worlds × a few demographic reps.
- Registering a new mechanism flag means FIVE places: `run_campaign.py` `_skip`, the flag audit TYPES + PREREQ
  (`audit_flag_invariants.py`), the benchmark ladder tier (`docs/BENCHMARK_LADDER.md`), and the allowed sets in
  `test_campaign_knobs.py` + `test_runconfig_sync.py`; then regenerate configs
  (`tools/gen_runconfig.py`, `tools/make_runconfig.py full_campaign`) and tag new params `[PROVISIONAL]`.

## New flags added this arc (all default-off, bit-exact off)

- `enable_sub_k_regulation` (+ `sub_k_target_fill`, `sub_k_sharpness`, `sub_k_by_emigration`,
  `sub_k_emigration_rate`) — the emigration/hold-below-margin lever (falsified as adoption).
- `enable_band_provisioning` (+ `band_provision_self_keep`) — the grounded fix.
- `enable_fertility_restraint_gene`, `enable_restraint_group_transmission`, `enable_heritable_density_response`,
  `enable_band_territory` — the band-autonomy / preventive-check instruments (Addendum 72).
