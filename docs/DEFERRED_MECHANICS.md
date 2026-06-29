# SiC Games — Deferred Mechanics

**The ONE question:** "What mechanics have been agreed on and designed in principle but explicitly deferred from the current blueprint?"

**Created:** 2026-06-14 (Blueprint A: Agent↔Terrain Migration and Static Game Mechanics)

**Discipline:** each entry is a mechanic that is (a) designed well enough to name, (b) has a seam or hook in the code, (c) deferred because the current blueprint is the wrong time to build it. Do NOT add mechanics here that are merely "possible future work" — they belong in ROADMAP.md. An entry here means: seam exists, literature anchor exists, decision to defer is deliberate.

**Format:** ID / What / Why deferred / Literature-rationale anchor / Seam / Status

**Update trigger:** when a mechanic is added, deferred, promoted to a live blueprint, or its seam changes.

---

## GD-1 — Game depletion

**What:** Depletable local game stock drawn down by hunting, with regrowth. Agents who hunt a cell reduce its `game_kcal` stock; the stock regrows at a biome-specific rate.

**Why deferred:** TMTS (Too Much Too Soon). Depends on the game-as-stock seam (A-2 §11) being live first. Depletion without a literature-grounded ceiling (CC-1) is placeholder stacked on placeholder — the depletion dynamics cannot be calibrated without knowing the real extractable rate.

**Literature-rationale anchor:** Redford & Robinson 1987; Vickers (various); Ross 1978 — depletion is a *sedentism* effect (hunt-out of a fixed catchment). Mobile bands avoid it via movement; large slow-breeders go first. [INLINE — in Blueprint A; not yet in LITERATURE.md]

**Seam:** Game-as-stock field (`game_kcal` per cell, readable, A-2 §11). GD-1 switches the field from read-only to a mutable stock with regrowth. No other code path needs to change; the seam is a writeable field + per-step regrowth kernel. Also depends on: local hunting pressure counter (new) + residence time metric (new).

**Status:** DEFERRED — seam placed (A-2, 2026-06-14); depletion OFF.

---

## JV-1 — Age-graded juvenile productivity

**What:** Replace the binary child age-gate (A-2 §12: below `age_productive_min` → zero subsistence) with a graded productivity-by-age curve. Curve rises from ~0 at birth to full adult productivity by early adulthood, with a faster-than-linear acceleration in adolescence.

**Why deferred:** TMTS. The binary gate is minimal-correct and sufficient for the current economy calibration. A graded curve adds a parameter sweep burden at a stage where the kcal ceiling is provisional (pending CC-1). Build the binary gate first; replace with the curve once the economy is calibrated.

**Literature-rationale anchor:** Bird & Bliege Bird 2000 (Meriam juvenile age-graded rates: children begin productive foraging by ~6 years and ramp to adult levels by late adolescence). [INLINE — not yet in LITERATURE.md]

**Seam:** Age-gate hook at A-2 §12. The existing `is_juvenile()` / `a_forage_min` (= `age_productive_min`) structure is the seam: replace the binary `if is_juvenile(): intake = 0` with a curve `intake *= age_productivity_curve(age)`. The age attribute and `lh_config.forage_age_min` already exist; no new state needed. Tagged with JV-1 in any code that implements the binary gate.

**Status:** DEFERRED — binary gate placed (A-2, 2026-06-14).

---

## CC-1 — Carrying-capacity-from-NPP (cell extractable rate + rivalry)

**What:** Replace provisional biome-scaled cell yields (`forage_kcal`, `game_kcal`) with a literature-grounded ceiling: cell characterized by total *extractable* kcal rate = f(biome carrying capacity, replenishment rate); co-located agents divide the finite rate → rivalry emerges; density and starvation become emergent properties of the resource ceiling, not tuned parameters. This is also where the superseded sugar-cluster resource ceiling is re-derived in kcal.

**Why deferred:** Foundational substrate change (RECAL-A-class). Bundling CC-1 with Blueprint A means you cannot attribute any dynamics to the economy change vs the ceiling change — two confounded migrations in one step. Build the economy first (A-1), gate it, then re-derive the ceiling (CC-1) as a separate pass.

**Literature-rationale anchor:** Tallavaara 2018 (HG population density vs NPP) for forage ceiling. Coe, Cumming & Phillipson (ungulate biomass from NPP) for game ceiling. [INLINE — Tallavaara in LITERATURE.md; ungulate-NPP source not yet in LITERATURE.md]

**Seam:** Decision rule in A-2 §10 reads cell yield but does not define it — the yield is read from `forage_kcal` / `game_kcal` per-cell fields. Swapping out how those fields are populated (from biome-scaled → NPP-derived extractable rate) changes numbers, not logic. Rivalry switches on by dividing the per-cell extractable rate among co-located agents (currently non-rivalrous, tagged CC-1). Also re-derives the superseded `c_max` / `α_growback` sugar cluster ceiling in kcal.

**Status:** RECAL-ADJACENT — not built here; all current cell yields are PROVISIONAL pending CC-1. **NB (2026-06-29):** the demographic/bands validations run on the *provisional* CC-1 capacity field (`SubWindowCapacity`: `E = density(NPP)·100·burn`, ~30–50 persons/cell; MODEL_SPEC §4.3.1/§4.8.4), NOT the bare `forage_kcal` field (~1–8/cell), which is too poor to hold a band (a stacked 25-band starves instantly). **Emergent bands REQUIRE the CC-1 capacity field** — this is the regime where a cell can hold a band and crowding is density-disease-regulated rather than starvation-limited. The full Tallavaara-regression CC-1 still supersedes this provisional field.

---

## RS-1 — Risk-sensitivity / variance-reduction foraging

**What:** Agents value variance reduction in daily returns, not just mean intake. A stream with lower mean but lower variance of zero-return days may be preferred by risk-sensitive agents. The switch logic in A-2 §10 is currently mean-only (does default stream cover burn?); RS-1 adds a variance term.

**Why deferred:** TMTS. The A-2 switch is a survival-fallback (cover burn or die), not a risk-management calculation. Adding variance requires: (a) empirical zero-day frequencies by biome and sex, (b) a risk-sensitivity parameter, (c) a reason to believe risk sensitivity varies C vs Si. All three are open. Build the binary switch first.

**Literature-rationale anchor:** Janssen & Hill 2014 — cooperative hunting reduces zero-meat-days from 52% to 9% at only −4% mean cost. This is the core variance-reduction finding; it motivates the mechanic but does not pin the parameters. [INLINE — not yet in LITERATURE.md]

**Seam:** Stream-choice objective in A-2 §10. Currently: "does default_stream_rate ≥ burn?" RS-1 replaces / augments this with: "does default_stream expected utility (mean - λ·variance) ≥ threshold?" The switch hook is the same; only the objective function changes. No new state on the agent; λ (risk-aversion coefficient) is a new parameter.

**Status:** DEFERRED — mean-only switch placed (A-2, 2026-06-14).

---

## MR-1 — Physiological reserve anchoring

**What:** Ground the kcal reserve (body-fat store) and starvation floor in HG physiology literature. Replace the current physiology-estimate placeholders: `reserve_full ≈ 100,000 kcal` [PLACEHOLDER] and `reserve_floor ≈ 20,000 kcal` [PLACEHOLDER].

**Why deferred:** The calibration is its own deliverable (survey + synthesis). The placeholders are self-consistent (reserve_full > burn_per_step × survival_window > reserve_floor) and sufficient for the correctness gate. Anchoring to real physiology requires a primary-source survey of HG body composition and starvation thresholds — not done in this blueprint.

**Literature-rationale anchor:** Textbook physiology: a 70 kg adult stores ~12–15 kg adipose tissue (~100,000–115,000 kcal) at normal body composition; clinical starvation floor is ~40% body-weight loss (roughly 20,000–30,000 kcal fat remaining). These are NOT HG-field numbers and NOT locked — they are MR-1-pending placeholders. Ethnographic starvation threshold data needed (Ache/Hadza/Martu corpus). [UNVERIFIED — Claude's textbook recollection; confirm before use in any write-up]

**Seam:** `reserve_full_kcal` and `reserve_floor_kcal` in `KcalEconomyConfig` (config.py); `reserve_floor` attribute on `BaseAgent` (base.py). MR-1 replaces the placeholder values with literature-grounded ones; no code structure changes needed.

**Extension (2026-06-19) — per-class reserves:** MR-1 also extends from one constant to a **per-agent `reserve_full` drawn from a normal distribution keyed on sex × age-class** (male / female / child / senior), lit-anchored to body composition — women carry more *absolute* fat (a reproductive buffer); children's low absolute store → starvation-vulnerable; seniors decline. Dormant on the constant economy (all fed); the differential vulnerability expresses only under nutritional variance (Resource-Ecology stage), where it must be reconciled against the all-cause Siler to avoid M-3-style double-counting (the reserve channel = scarcity *deviation*, not a restatement of the average sex/age mortality). Supports TARGET T-4.

**Status:** SURVEY-PENDING — placeholders live (A-1, 2026-06-14); values tagged [PLACEHOLDER] in PARAMETERS.md.

---

## MR-2 — Carried-provision anchoring

**What:** Food carried while travelling ("on the belt") — a short-horizon (days-scale) buffer distinct from the long-horizon physiological reserve. Two separate quantities: the reserve (body fat, months-scale) and the carried provision (food in hand, days-scale). Currently the model has a single integrating reserve.

**Why deferred:** Needs an ethnographic anchor for typical carry load and trip duration, and a reason to believe the short-horizon buffer changes behaviour differently from the long-horizon reserve. The single-reserve model is sufficient for the current calibration stage.

**Literature-rationale anchor:** Foraging-trip duration and food-load data in the Ache/Hadza/Martu corpus (Kelly 1983; Bird & Bliege Bird ethnographic trip records). [UNVERIFIED — Claude's recollection; confirm literature before use]

**Seam:** A second short-horizon buffer above the reserve; not built now. The integration step `reserve += intake − burn` would split into `provision += intake; reserve += min(provision, provision_capacity) - burn` (simplified). No seam placed yet; the single-reserve variable is the structural predecessor.

**Status:** PARTIALLY REALIZED (founder-only) — `founder_buffer_steps` (a6a4ccf, 2026-06-26; MODEL_SPEC §4.8.3) is a first, *founder-only* carried-provision buffer: each founder carries `founder_buffer_steps × burn` kcal drawn down to cover per-step shortfalls during the band's founding/dispersal transient (Kelly mobile-reserve rationale, now in LITERATURE.md). It is transient (decays, founder-only ⇒ no steady-state effect), NOT the general days-scale provision-vs-reserve split MR-2 describes. The full MR-2 (a standing second buffer for ALL agents, anchored to ethnographic carry load/trip duration) remains SURVEY-PENDING.

---

## PL-1 — Pool scale-dependence

**What:** Re-scope the existing proximity support pool (MECHANISMS §6, Stage 4.1c+) as density-dependent: in a small mobile band, the "pool" is simply individual carry and immediate sharing (immediate-return economy). A meaningful institutional surplus pool only emerges at higher density / partial sedentism (delayed-return economy). Currently the pool applies at all densities; PL-1 would gate pool contributions on a density threshold.

**Why deferred:** Change to an existing mechanic; belongs with the density/co-location revisit (when agents are co-located in meaningful ways, post-CC-1). Also: the pool is currently C-only in the legacy Sugarscape economy; its kcal-economy analogue is deferred until CC-1 re-derives the resource ceiling. Bundling with Blueprint A would mean three confounded changes.

**Literature-rationale anchor:** Immediate-return vs delayed-return foraging economies (Woodburn 1982 — immediate-return vs delayed-return dichotomy). Delayed-return economies enable investment in storage and sharing institutions; immediate-return bands pool food informally. [INLINE — Woodburn 1982 concept; not yet in LITERATURE.md]

**Seam:** Existing pool mechanic in `support_pool.py` + density gate. Maps to the co-location-must-pay constraint: pool draws are only meaningful when co-location is sustained, which in turn requires that agents share a persistent resource patch (sedentism or repeated return). The pool mechanic's `r_pool` radius and `tau_pool` contribution rate are the structural predecessors.

**Status:** DEFERRED — pool mechanics unchanged (2026-06-14); pool is dormant in kcal economy (not wired to kcal reserve yet); PL-1 re-scoping deferred post-CC-1.

---

## CL-1 — Climate field (temperature & humidity, solar-forced seasonality)

**What:** A spatially- and seasonally-varying **temperature and humidity** field, driven by latitude / insolation / **solar forcing** (and ENSO / Holocene variability). `terrain.py` currently ships HOMOGENEOUS constant placeholders (`MEAN_GLOBAL_TEMP_C = 14 °C`, `MEAN_REL_HUMIDITY = 0.70`). CL-1 replaces the constants with a real climate field and ties the existing seasonal-oscillation mechanic to it.

**Why deferred:** It is its own terrain/climate stage — it touches the terrain generator and couples to insolation/orbital forcing. The demographic stage needs only a *reference* T/humidity (a constant is sufficient as a seam); building the full solar-forced climate layer now would confound three changes. The constant placeholder unblocks the pathogen field without it.

**Literature-rationale anchor:** Berger 1978 (insolation / orbital forcing); Timmermann 2018 + Cane 2005 (ENSO); Wanner 2008 / Mayewski 2004 (Holocene climate variability); Sigl 2015 (volcanic forcing). Guernier 2004 (temperature + precipitation drive pathogen richness) motivates the demographic payoff. [all FILED in `literature/` — B-series.]

**Seam:** `terrain.py: temperature, humidity` fields (constant now) + `MEAN_GLOBAL_TEMP_C` / `MEAN_REL_HUMIDITY`. CL-1 makes them spatial (latitude / elevation lapse) + seasonal (insolation cycle, solar-forced). Consumers: (a) the demographic **pathogen field** (Step 2) reads T/humidity instead of the `wateracc × NPP` proxy; (b) the existing **seasonal-oscillation** mechanic (`test_seasonal_oscillation.py`) becomes physically driven rather than a painted-on sine; (c) forage seasonality. Placeholder-value derivation: `MODEL_SPEC.md` §4.3.2.

**Status:** SEAM PLACED — homogeneous constant fields live (2026-06-18, Phase 1); the spatial/seasonal solar-forced field is DEFERRED to the climate-season stage.

---

## FD-1 — Family dynamics (co-residence & provisioning)

**What:** Define a **family unit** (mother + dependent children) that **co-resides and moves together** until child maturation (~age 15), with children **provisioned by the mother** (they do not self-forage). Currently a newborn is dropped on the parent's cell and immediately becomes an independent forager that wanders off — no bond, no provisioning, no co-residence.

**Why deferred:** Belongs in the **Resource-Ecology stage** (with depletion + seasonality + per-class reserves): (a) provisioning load only bites under nutritional scarcity, and (b) family co-residence creates *realistic* local structure (a family ≈ several co-located agents) — which is what makes density-disease and spatial dynamics meaningful, but only once there's scarcity to act on. On the constant economy it would be inert.

**Literature-rationale anchor:** HG juvenile dependence + parental/alloparental provisioning (Kaplan/Hill/Hurtado embodied-capital; Hawkes grandmothering). Ties to JV-1 (age-graded juvenile productivity) and MR-2 (carried provisioning). [INLINE — not yet in LITERATURE.md]

**Seam:** child placement (`_do_births_ibi`: `child.pos = parent.pos`) + the diffusion mover. FD-1 keeps the child bound to the mother's position (move as a unit) until maturation, and routes the child's subsistence through the mother (provisioning) rather than independent harvest. Connects to the JV-1 age-gate (`is_juvenile`) and the MR-2 provisioning seam.

**Status:** PARTIALLY ADVANCED — mother→child provisioning IS built (C.2b/S1 + B+ paternal tiers; MODEL_SPEC §4.5.4/§4.5.7), and the **F.1/F.2 bonded mating** (MODEL_SPEC §4.8.2) added the missing *mate bond* (a birth now requires a co-resident band male). What REMAINS for FD-1 is **persistent co-residence / pair-bonds + per-band society** — the deferred "F.3 / C": a durable mother+children (and father) unit that moves as a unit, and a society entity attached to the *band* (mate-gate neighbourhood) rather than the cell. Children still disperse independently after birth (no move-as-a-unit bond). Targeted next after the storage-tethering retirement (see MODEL_SPEC §4.8.5 "Pending cleanup" and the F.2-then-F.3 roadmap).

> **Resource-Ecology stage grouping (2026-06-19):** GD-1 (depletion) + CL-1 (climate/seasonality) + MR-1 per-class reserves + MR-2 (provisioning) + FD-1 (family) compose the next stage — the economy that gives the demographic `a2` modulators nutritional *variance* to act on (they are inert without it; RESULTS R-5) and that enables the T-4 emergent-child-mortality validation.

---

## PA-1 — Proto-agriculture yields per biome + seasonality

**What:** Per-biome proto-agricultural / intensive-wild-resource yields (and their seasonality) for the **post-morph sedentary state** — what a settled, storing, delayed-return community *produces* (wild-cereal / acorn / salmon intensification → incipient cultivation), distinct from the mobile-forager return rates already in the game return-rate table.

**Why deferred:** It is the **CONSEQUENCE (end state) of the sedentism/storage morph, not the trigger.** The morph *trigger* — Binford's storage threshold (Effective Temperature ≤ 15.25 °C) + storable seasonal surplus + sustained density → delayed-return — is being built first (the storage mechanic, 2026-06-25). Proto-ag yields are only needed once a community has *already morphed* to the sedentary/proto-ag society type and we model its altered productivity. Building the yields before the trigger is placeholder-on-placeholder. **(Explicitly deferred at supervisor request, 2026-06-25.)**

**Literature-rationale anchor:** Binford 2001 (ET 15.25 °C storage threshold; QSTOR quantity-stored); Testart 1982 (storage → delayed-return → inequality); Woodburn 1982 (immediate- vs delayed-return). Post-morph yields to survey: Natufian wild-cereal, California acorn, NW-Coast salmon intensification. [INLINE — not yet in LITERATURE.md]

**Seam:** the society morph (`society_from_character` / `morph_to_society`, demography.py) + the storage stock (`enable_storage`); the proto-ag society type would carry a per-biome yield multiplier read only in the morphed state.

**Status:** DEFERRED — trigger (storage + morph) built first; proto-ag yields surveyed + valued when the post-morph sedentary/proto-ag state is built.

---

*End of DEFERRED_MECHANICS.md — seeded 2026-06-14 from Blueprint A (Agent↔Terrain Migration and Static Game Mechanics). 10 entries: GD-1 (game depletion), JV-1 (juvenile curve), CC-1 (NPP ceiling), RS-1 (risk-sensitivity), MR-1 (reserve anchoring + per-class), MR-2 (carried provision), PL-1 (pool scale-dependence), CL-1 (climate field — temperature/humidity, solar-forced), FD-1 (family dynamics — co-residence & provisioning), PA-1 (proto-agriculture yields — post-morph consequence).*
