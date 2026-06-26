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
