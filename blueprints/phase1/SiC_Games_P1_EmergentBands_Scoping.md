# SiC Games P1 — Emergent Bands (movement-utility grouping drives)

**Goal:** make forager **bands (~25–50, ~7–8 active foragers)** EMERGE from the cost–benefit of grouping, instead
of the IFD diffusion that spreads agents to ~2/cell (anti-clustering) and the storage-tethering band-aid. Put the
real benefits of co-residence into the movement utility; optimal band size emerges where marginal grouping
benefit = marginal per-capita-food cost (Smith & Winterhalder aggregation economy). A devastated band's survivors
re-aggregate automatically (they climb the nearest benefit gradient — no band redefinition needed).

## §1. Anchors

| Quantity | Value/form | Source |
|---|---|---|
| Minimal band size | **~25–50** (≈7–8 active foragers); kin-dominated; nests in ~500 community | Wobst 1974; Kelly *Lifeways*; Hill et al. 2011 |
| Risk dilution | per-capita risk ↓ ~1/g + many-eyes; **declines ~exp → saturating threshold** | Hamilton 1971; dilution/many-eyes lit |
| Variance pooling | pooled-intake CV ~ **1/√n** (n independent sharers); saturating | Kaplan & Hill 1985; Winterhalder |
| Mating access | **minimum viable band** (~25); sharp penalty below the mate-pool threshold | Wobst 1974 (connubium) |
| Cost (dispersal) | per-capita yield `S/(g+1)` falls with crowding | ideal-free distribution (existing rule) |

## §2. Design (minimal-first)

Extend `diffusion_select_target`'s per-cell utility from `U = per_capita_yield − move_cost` to include the
grouping benefits as a function of the target cell's group size g:

> `U(cell) = per_capita_yield(cell) · grouping(g) − move_cost`,  `grouping(g) = 1 + Σ benefit_k(g)`

with each `benefit_k` **saturating** (so band size is bounded, not a runaway blob):
- **safety(g)** = `s_max·(1 − e^{−g/g_s})` (risk dilution + many-eyes; rises fast, saturates ~ band threshold g_s).
- **variance(g)** = `v_max·(1 − 1/√g)` (risk-pooling; saturating).
- **mating(g)** = a step/sigmoid **penalty below a minimum band** (≈ the ~25 connubium): low g ⇒ U strongly
  reduced (can't find mates), rising to ~1 by the threshold.

The food term `per_capita_yield = S/(g+1)` is DECREASING in g (competition) ⇒ the dispersal force. Balance ⇒
optimal g\* ~ the minimal band. **Minimal-first build:** start with **safety + mating** (the two strongest,
cleanest, and both reuse existing structure — the `risk` field and reproduction); add variance + cooperative-
hunting-threshold + heritable-sociability ψ as enrichments once the core produces ~25-person bands.

## §3. Build steps

- **E.1 — safety drive. ✅ BUILT 2026-06-25.** `ypc · (1 + s_max·(1−e^{−g/g_s}))` in the movement utility
  (`SubstrateConfig.group_safety_max/scale`; 0 = off → bit-exact IFD). Result: max band 11→27, **multiple
  bands, no blob** ✓ — but a singleton tail remains (it accretes only over the r=1 neighbourhood). (Aside: the
  baseline max is 11, not 2 — the earlier "2/cell" was partly a low-population artifact of the storage+climate
  config.)
- **E.2 — mating-access drive. ✅ BUILT 2026-06-25.** `ypc · (m_floor + (1−m_floor)·min(1, g/g_mate))`
  (`group_mate_min/floor`) — being below the minimum viable band is actively bad. Result (safety+mating):
  agents in groups ≥5 **29%→62%**, singletons ~halve (312→144), bands bounded ~17–27. **Residual:** ~25% stay
  in singletons/pairs — the **r=1 movement locality** (loners in empty regions can't navigate to a distant band
  in one-cell steps; full fix = longer-range aggregation perception, a bigger movement change — flagged).
- **E.3 — re-validate R-18/19** on the new movement (the von Rueden r≈0.19 status→RS; N_e; homeostat bounds) —
  the meat-pool/cred dynamics now run on real bands, not 1–2-agent "bands".
- **E.4 — enrichments (optional):** variance-pooling; cooperative-hunting hump (party size g\*≈3–6); heritable
  sociability ψ (settler/wanderer distribution).
- **Then:** retire storage-tethering; revisit per-cell → per-BAND society + bonded mating (Phase 2).

## §3b. Fitness/selection drives (the REAL emergence — supervisor pivot)

**Root cause found:** the model's fitness landscape *rewards* loners — reproduction is **asexual/female-only**
(`_do_births_ibi`: a lone female breeds; the father is picked globally only for lineage) and the only group-size
mortality term is **density-disease** (crowding *raises* mortality). So a loner is *safer* AND reproduces. The
movement nudge (E.1/E.2) fights this gradient. The realistic fix: make grouping a **fitness** effect so loners
are a *dying margin* (no navigation needed), keeping E.1/E.2 as reinforcement (supervisor choice).

- **F.1 — bonded mating (partner-required reproduction). ✅ BUILT.** A female births only if her cell has ≥1
  co-resident adult male who is **not her own son** (kin-avoidance via `_mother`). Loners ⇒ **no birth**.
  Flaggable (`enable_bonded_mating`). **FINDING (key):** bonded mating CANNOT bootstrap bands from a gas (a
  spread population almost never has a co-resident mate → near-zero births → no densification → 7% in bands).
  It needs bands to ALREADY exist. → the band-SEEDER below.
- **F.1b — banded seeding. ✅ BUILT** (`seed_band_positions`). Real foragers START in bands, not a gas. Seeds
  ~`n/band_size` kin bands of ~25 at good-but-not-best (sampled), TERRITORY-spaced sites, allocated PER BIOME by
  carrying capacity → marginal biomes (desert, mountain) get fewer-but-NON-ZERO bands (desert dwellers + mountain
  clans). Flaggable via `placement_positions`. **GATE met:** 250 agents → 10 bands of 25, biomes {forest 4,
  savanna 4, desert 2}, min spacing 12. **Seeded + bonded mating → 96% of agents in bands of ≥10, population
  stable (254, mates co-resident → reproduction sustains bands), biome-diverse (Desert/Savanna/Forest clans
  persist)** — vs 7% for the gas start. This is the working emergent-band substrate; "emergence" is correctly
  reframed as maintenance/merge/split of bands that always exist, not condensation from a gas.
- **F.2 — risk-dilution mortality.** Effective predation risk = `biome_risk · (floor + (1−floor)/g)`, g = local
  group size (`risk_dilution_floor`; 1 = off). Loner (g=1) gets full biome risk; a band dilutes it to `floor`.
  Balances the existing density-disease cost ⇒ an optimal band size. Wires to the existing `risk` field + `_a2_mult`.

## §3b red-team
- **[BLOCKER — re-validation, again] mate-gated reproduction is a demographic-engine change** → re-opens e₀/Siler
  fertility tuning + R-18/19. Fix: FLAGGABLE (default off ⇒ bit-exact; all validations untouched); the on-config
  re-validation is the deliberate E.3 pass.
- **[MAJOR — population crash] if mates are often unavailable, the birth rate collapses → extinction.** Fix:
  the gate is at the BAND (cell) level — band-members have mates, only true loners don't; GATE checks the
  population PERSISTS (doesn't crash) while loners decline.
- **[MAJOR — incest] mother + her adult sons would "mate".** Fix: exclude `m._mother is a` (her sons);
  founders/unrelated males qualify. (Finer kin-avoidance = refinement.)
- **[MINOR — coexist with B+] mate-choice (m, father assignment) already exists for LINEAGE; F.1 requires a male
  be PRESENT.** They compose: F.1 gates the birth, B+ picks which male fathers.
- **[MINOR — not a double-count] risk-dilution (↓ with g) vs density-disease (↑ with g)** are different channels
  (predation vs disease) that OPPOSE → the optimal-band-size balance. Intended.

## §4. Gates / validation
- Emergent band size **~25–50/occupied-cell** (≈7–8 foragers); **multiple bands**, not one blob (saturation works).
- Devastated band → survivors re-aggregate (the emergence test).
- Flag off ⇒ bit-exact (the current IFD movement).
- **R-18/19 re-validated** on the new movement.

## §5. Red-team (v1, self)
- **[BLOCKER — re-validation] R-18/19 ran on IFD (1–2-agent "bands").** The whole Carbon validation
  (status→RS r≈0.19, N_e, homeostat) was measured where the sharing unit was ~2 agents. Real ~25-person bands
  change the meat-pool/cred contest **fundamentally** → E.3 must re-run those before this is trusted. Non-negotiable.
- **[MAJOR — common currency] combining food (kcal) + safety (mortality) + mating (reproduction) in one utility
  needs a fitness common currency + weights → calibration-heavy.** Fix: express each drive as a **dimensionless
  multiplier** on the cell's food value (`grouping(g)`, ~1 baseline), NOT additive cross-unit terms; start with
  ONE driver (safety) → one new parameter; calibrate band size to the ~25 anchor; add drives only as needed.
- **[MAJOR — runaway blob] if grouping dominates, all agents pile into ONE cell.** Fix: every benefit
  **saturates** (safety ~ band threshold, variance ~1/√g) and the per-capita food cost rises with g ⇒ bounded
  g\*; GATE explicitly checks MULTIPLE bands, not one blob.
- **[MAJOR — myopia] movement is per-step/myopic — agents can't *plan* a band.** Fix: that's fine —
  band formation EMERGES from local gradient-following (Boids/flocking logic); each agent just moves toward
  higher expected fitness, which includes "be with others". Verify emergence, don't assume it.
- **[MINOR — density vs packing] ~25/cell band = 0.25/km² ≫ Binford packing 0.091.** So with real bands packing
  is met BY DEFAULT ⇒ the morph correctly hinges on STORAGE/surplus (Testart prime mover), not density. This
  *fixes* the morph feasibility properly and **retires the tethering band-aid** — a feature, not a bug.
- **[MINOR — water guard / determinism]** keep the water-step guard + id-sorted determinism intact in the new
  target selection.

## §6. Deferred / Phase 2
- Cooperative-hunting threshold (g\*≈3–6, Alvard & Nolin); heritable sociability ψ distribution (settler vs
  wanderer — psych-lit form thin, flag). Per-BAND society + **bonded mating** (durable pair-bonds → families →
  band identity → society per band; the deferred "C"). These build on emergent bands.

**Lit:** Wobst 1974 (band/connubium), Kelly *Lifeways*, Hill et al. 2011 (multilevel HG sociality), Hamilton
1971 (selfish herd), Kaplan & Hill 1985 (variance pooling), Smith & Winterhalder (aggregation economy),
Alvard & Nolin 2002 (cooperation threshold) — to file/extend in LITERATURE.md at build.
