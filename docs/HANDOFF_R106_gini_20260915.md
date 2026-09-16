# Handoff — R-106 ladder-miss arc (2026-09-15 20:29 EDT)

> **UPDATE 2026-09-15 (Add.86, origin/main @ 7d715e6):** the graded-leveler mechanism below is now BUILT + calibrated.
> `leveling_tolerance` + `feast_tolerance` (both default 0.0, bit-exact OFF) reach material Gini 0.367 in BOTH biomes
> at `lt1.0 / ft1.5` with tier-11 intact and the feast kept on. NOT adopted — canon unchanged. The remaining work is
> the ADOPTION path, gated on GROUNDING `material_capture_frac` (Hayden aggrandizer-skim anchor) then re-calibrating,
> then the full CTB suite. Do NOT rebuild the mechanism; see RESULTS Add.86 + memory `project_sic_games_material_gini`.

This note points the next session at the graded-leveler arc, the live frontier. It is a map, not the record:
the formal record is `docs/RESULTS.md` (Addenda 76–85) and the git history; the working state is in the assistant
memory files listed below.

## Status in one line

Five ladder misses were diagnosed this arc (e0, packing, band size, age structure, wealth Gini). Four are
STRUCTURAL or STALE (not tunable); tier-10 wealth Gini is the one with a live, scoped fix — the GRADED-LEVELER
redesign — NOT yet built. `origin/main` is at `d076969`, pushed and in sync. Canonical config UNCHANGED.

## Where the state lives

- **Formal record** — `docs/RESULTS.md`, Addenda 76–85 (append-only):
  - 76 — savanna e0 residual = Malthusian relocation (demographic layer ruled out).
  - 77 — the carrying-capacity shortfall = the packing paradox (spatial, ~14% land use).
  - 78 — hunger dispersal unpacks but crashes temperate e0 (clusters are adaptive).
  - 79 — intake mobility inert; both spatial levers exhausted; e0 arc CLOSED (model calibrated).
  - 80 — tier-5 band size is a spatial limit, not a cohesion cap (savanna natural control).
  - 81 — tier-3 age structure RE-SCORED PASS (ladder "too many children" was stale). Probe-bug retraction.
  - 82 — tier-10 material Gini 0.16 vs BHM 0.36 = a weak status→material coupling.
  - 83 — tier-10 is MOVABLE (knobs span 0.17→0.78); root = dead capture knob + status-blind inheritance.
  - 84 — tier-10 is BIMODAL: levelers near-bang-bang, 0.36 has no grounded landing.
  - 85 — config debt resolved; the bang-bang is the SHAPE (pull-to-mean, no tolerance band); the levelers are
    load-bearing for tier-11; the graded-leveler arc is scoped.
- **Git** — `origin/main` @ `d076969`, all pushed. Arc commits: `556a569`(75) → `5a1bb4d`(76–79) →
  `c8aa849`(80–81) → `854fd45`(ladder re-score) → `49b5c2b`(82) → `6b14fde`(83) → `9a8d6c1`(84) → `d076969`(85).
- **BENCHMARK_LADDER.md** — tier-3 re-scored PASS, tier-5 marked a structural packing limit (dated update block).
- **Assistant memory** (per-project, the working handoff):
  - `project_sic_games_material_gini.md` — the tier-10 arc: the bimodal result, the shape diagnosis, the arc scope.
  - `project_sic_games_packing_paradox.md` — Addenda 77–79 (adaptive equilibrium, e0 arc closed).
  - `project_sic_games_bandsize_mean.md` — tier-5 + the tier-3 pass.
  - `project_sic_games_emigration_e0.md` — the e0 chain and the low-noise instrument + traps.

## The through-line

The model is well-calibrated. Temperate sits at its anchors; savanna sits in the harsh-biome forager range;
tier-3 passes. Most "misses" are STRUCTURAL adaptive equilibria (the packing paradox caps e0, density, and band
size) or STALE (tier-3), not tunable defects. Tier-10 wealth Gini is the exception with a real, scoped lever.

## NEXT STAGE — the graded-leveler arc (build + calibrate + adopt)

**Goal.** Raise the whole-population material Gini from ~0.17 to BHM 2009's 0.36 (marker #14), which the current
mechanisms cannot reach because the levelers are near-bang-bang.

**Why it is blocked now (Addendum 84/85).** Leveling (`phase1_model.py:~3233`) and feasting (`~4063`) both pull
each agent's material EXCESS ABOVE THE CELL MEAN back down every step and redistribute PER-CAPITA, with NO
tolerance band. So any nonzero strength cumulatively levels to the mean → Gini pinned ~0.2; only fully removing
BOTH lets it run away to ~0.78. 0.36 sits in the unreachable gap. Dialing the STRENGTH is inert — the defect is
the redistribution SHAPE, not the gain.

**The build.**
1. Add `leveling_tolerance` (a setpoint of tolerated inequality; default = neutral so OFF is bit-exact) to the
   leveling sanction: fire only on the excess BEYOND `tolerance` (e.g., sanction `max(0, excess − tolerance·mean)`
   rather than all `excess`). Add the feast equivalent. This lets the equilibrium Gini settle at the tolerated
   band instead of at the mean.
2. PRESERVE the noble exemption (`enable_noble_leveling_exemption`, `phase1_model.py:~3248`) and the
   legitimacy-feast channel — the levelers are load-bearing for tier-11 stratification (Flannery ch.16). Apply the
   band to COMMONER leveling; nobles stay exempt.
3. Register the new knob the FIVE places (per the e0-arc trap note): `run_campaign.py` `_skip`,
   `audit_flag_invariants.py` TYPES+PREREQ, `docs/BENCHMARK_LADDER.md` tier, `test_campaign_knobs.py` +
   `test_runconfig_sync.py` allowed sets; then regenerate configs (`tools/gen_runconfig.py`,
   `tools/make_runconfig.py full_campaign`) and tag new params `[PROVISIONAL]`.

**The calibration + validation.**
- Sweep `leveling_tolerance` on the low-noise panel (fix world seed, vary demographic seed; `bp_gini_calib.py`
  is the harness) to land material Gini at 0.36.
- VALIDATE TOGETHER, not alone: material Gini 0.36 AND the tier-11 stratification markers AND the lower tiers
  (e0, frac_child, band size, pop). A leveler change touches the egalitarian↔stratified morph.
- Then the FULL suite (~1740 tests). Changing a canonical value breaks bit-exact CTBs that assert canon outputs —
  budget time to update them; that churn is expected for a canonical change.
- The concentrators must be ON for the band to have anything to hold: set `material_capture_frac` > 0 and
  `material_heir_by_status = True` as part of the same adoption (they are the parked levers documented in
  Addendum 85). Choose grounded values, not a fit to 0.36.

**Bonus hypothesis to test in the same arc.** The band-cohesion budget (Addendum 22) is the SAME near-bang-bang
class (saturates at 1.0; `leaky-assabiyah` built, never adopted). A graded fix there may move tier-5 band size.
Worth a check once the leveling tolerance-band pattern is proven — one graded-mechanism idea, two benchmarks.

## Traps + instrument notes (do not repeat)

- **`material_capture_frac = 0.0` is NOT a dead advertise-nothing flag.** `enable_material_capture=True` runs the
  hide economy (everyone accrues durable goods); only the aggrandizer SKIM is zero. Reaching 0.36 needs the
  tolerance-band redesign, not just flipping this.
- **Dial the RIGHT knob.** The concentrating capture is `material_capture_frac` (`phase1_model.py:~2082`), NOT
  `material_hide_frac` (which only sizes the hide pool). A first probe this arc tuned the wrong one and read inert.
- **`fert_births[mother_age]` is ONE PER BIRTH (total births), not female-only.** Dividing by the female fraction
  double-counts CBR (a probe bug this arc; it manufactured a false r ≈ +5%/yr). The runs are near-stationary,
  r ≈ +1%/yr, iso-growth consistent.
- **`leveling_strength = 0` ≡ `enable_leveling = False`** (verified). The FEAST is the dominant binding leveler in
  the concentrated regime.
- **e0/Gini noise is dominated by the world lottery.** Fix the world seed and vary the demographic seed
  (`bp_savanna_probe.build()` decouples them); use a 3-world panel. `battery1_liveness._build` does NOT apply the
  canonical runconfig — merge `runconfig.load()['DemographyConfig']`.
- **`config/parameters.toml` + `mechanisms.toml` are GENERATED** by `tools/gen_runconfig.py` from the field
  comments in `demography.py`. Put provenance in the field comment, then regenerate; do not hand-edit the TOML.

## Scratchpad probes (reusable, in `scratchpad/`)

`bp_savanna_probe.py` (the low-noise build + e0/panel harness), `bp_gini.py` + `bp_gini_isolate.py` +
`bp_gini_calib.py` (the tier-10 harnesses), `bp_bandsize.py`, `bp_agestruct.py`, `bp_foodchain.py`, `bp_reach.py`,
and their `_plot.py` companions. All reuse `bp_savanna_probe.build()`.
