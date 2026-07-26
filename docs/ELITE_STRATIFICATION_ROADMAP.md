# Elite / stratification mechanism roadmap — the systematic digestion (Step 0 inventory)

**Purpose.** Replace the reactive "chase one hypothesis at a time" mode (which produced a five-deep dead-end
chain on 2026-07-23) with a **dependency-ordered, benchmarked** build of the lit's inequality mechanisms. This
document is the working catalog: what is built, what it anchors, what it must be built ON, and its benchmark
target. Scope: **egalitarian → big-man → rank → early chiefdom/stratification** (the model's HG→proto-ag horizon).
Flannery Parts IV–V (kingdoms/empires) are out of scope.

**Organizing spine (to digest next):** Johnson & Earle *Evolution of Human Societies* (the staged sequence);
Earle *How Chiefs Come to Power* (**staple- vs wealth-finance** — the direct anchor for the tribute problem);
Fried / Service (rank vs stratification definitions, filed). Mechanism sources: Flannery & Marcus (filed, 24 ch),
Boehm, Hayden, Testart, Goody (filed), Friedman, Carneiro.

---

## THE DEPENDENCY CHAIN (discovered 2026-07-23, rendered forward)

Each link REQUIRES the ones before it. This is why isolated mechanisms went inert — a link with a missing
predecessor cannot bite. Build and benchmark in THIS order.

```
(0) STATUS HIERARCHY        cred won by merit=cred·prowess           [BUILT: cred_status, prowess, leader_office]
        │                   → big men (achieved, non-heritable)       BENCHMARK: R-83/84 leaders 3.68× ahead ✓
        ▼
(1) LEGITIMATION            achieved success → ascribed rank LABEL     [BUILT: legitimacy, delegitimation, ascription]
        │                   (Friedman "descended from higher nats")    BENCHMARK: Hayden 75% feast (R-86) ✓
        ▼
(2) TRIBUTE / COUPLING  ◄── THE GAP. status elite must become the      [PARTIAL: leader levy exists but weak;
        │                   WEALTH elite. material is aggrandizer-       material⊥status by design, corr −0.018]
        │                   captured, DECOUPLED from status.            BENCHMARK: Earle staple/wealth finance — TBD
        │                   → per-lineage legitimacy-gated tribute
        │                     (KEEP decoupling as default: enables
        │                     'poor influencers' — prophets/warriors,
        │                     Flannery ch.10 three paths; ch.11 triad)
        ▼
(3) EXEMPTION FROM LEVELING legitimate accumulation is 'his by right', [BUILT this session: noble_leveling_exemption]
        │                   not overreach-grievance (Flannery ch.16)    BENCHMARK: none direct — outcome-based
        ▼                   INERT without (2): nobles hold no material
(4) INHERITANCE             bequeath the estate (Flannery: big men     [BUILT this session: material_inheritance,
        │                   "no way of bequeathing"). Regime rule.       heir_by_status]  ANCHOR: Goody/EA075×EA028 ✓
        ▼                   INERT without (2): dilutes a levy-hoard      BENCHMARK: EA distribution shares
(5) HEREDITARY ESTATE       a lineage compounds wealth+rank across      [EMERGES from 2+3+4; not yet observed]
        │                   generations → a CHIEF                        BENCHMARK: noble_material_lift > 1 durably
        ▼
(6) THE BREAK               endogamous noble stratum, a GAP not a       [endogamy BUILT (ascribed_mate); gap
        │                   continuum (Flannery ch.16; Fried)            detector village_gap_d BUILT]
        ▼                   INERT without (5): nothing to guard          BENCHMARK: bimodal cred/material, d large
(7) CLASSIFY STRATIFIED     detect the break (NOT gini — gini measures  [inequality_gate BUILT but criterion wrong;
                            spread, stratification is a discontinuity)   needs gap-based]  BENCHMARK: EA066 ~few %
```

**Today's terminal finding:** the chain is broken at **(2)**. Everything downstream (3,4,6,7) was built and is
INERT because material is decoupled from status. (2) is the next thing to build — as a per-lineage,
legitimacy-gated tribute, preserving the decoupling as the default so poor influencers survive.

---

## BUILT-MECHANISM INVENTORY — elite/stratification subset (of 72 total toggles)

| toggle | link | what it does | lit anchor | benchmark |
|---|---|---|---|---|
| `enable_cred_status` | 0 | status currency (cred) | von Rueden; BHM relational | status→RS r≈0.19 ✓ |
| `enable_prowess_facet` | 0 | achieved ability | Goldman toa/tohunga (ch.11) | — (conflated; split TBD) |
| `enable_leader_office` | 0 | tenured office, challenge-succession | Boehm; Sahlins | R-84 depose/desert ✓ |
| `enable_leveling` | 0 | Boehm leveling of aggrandizers | Boehm 38/48 | ✓ |
| `enable_legitimacy` | 1 | achieved→ascribed cred | Hayden; Friedman (ch.10) | Hayden 75% (R-86) ✓ |
| `enable_delegitimation` | 1 | gumsa/gumlao reversion | Leach/Friedman (ch.10) | ~60–100 yr cycle |
| `enable_rank_hierarchy` | 1 | ranked lineages unlock a rung | Hill; Testart | R-99 (superseded gate) |
| `enable_*_ascription`, `relative_legitimacy`, `*_resentment` | 1 | scale-free ascription + revolt | R-89…R-96 | R-64 9–16% strat |
| `enable_material_capture` | 2 | durable capital by aggrandizers | Hayden 1995 | corr(cred,mat) −0.018 ✓ |
| **TRIBUTE (to build)** | **2** | **legit lineage levies a share of others' `material`** (WEALTH finance — the existing leader levy, strengthened + hereditary + legit-gated) | D'Altroy&Earle 1985 (staple vs wealth); gumsa "a thigh" ≈10–15%/kill (DM-F6); Friedman | **OUTCOME-based** (no rate exists — verified neg): noble_material_lift>1, gini_material & elite-share in BHM/EA range |
| `enable_noble_leveling_exemption` | 3 | nobles exempt from wealth-leveling | Flannery ch.16 | outcome-based |
| `enable_material_inheritance` (+`heir_by_status`) | 4 | bequeath estate; rule=Goody | Goody 1976; EA074-077 | EA distribution |
| `enable_ascribed_mate_choice` | 6 | class endogamy | Flannery ch.16 | bimodality |
| `enable_stratification_inequality_gate` | 7 | classify stratified (gini — WRONG) | Fried/Flannery | EA066; needs gap-based |
| `enable_lineage_branching` / `_split` | — | Y-lineage dynamics (T-9) | Karmin/Yan/Zerjal | top_share ≈0.16 ✓ |

**Substrate these stand on** (not elite-specific but prerequisite): `morph`, `improved_land`, `agriculture`,
`soil_depletion`, `landscape_packing`, `settlement_scalar_stress`, `aggregation_sedentism`, `village_budding`,
`emergent_band_size`, `marriage_aggregation`, `exogamy`, `genome`.

---

## GAPS & CORRECTIONS FOUND (to carry into the digestion)

1. **(2) tribute is the load-bearing gap.** Design agreed: per-lineage, legitimacy-gated; lineage- not
   office-based (hereditary estate, Friedman). Anchor to digest: Earle staple- vs wealth-finance.
2. **Classifier (7) uses the wrong shape.** Gini measures spread; stratification is a GAP/discontinuity. Replace
   with a bimodality/gap detector on the (eventually real) noble/commoner split.
3. **Nobility is too broad** (ascribed_frac 25–44%; EA true-elite few %). An ascription-tightening lever is
   needed regardless of tribute.
4. **`prowess` conflates tohunga (expertise) + toa (martial/mobility)** — Goldman/Flannery ch.11 split; the toa
   facet is the commoner's mobility channel and the 'poor influencer / revolt leader' path.
5. **Benchmark targets are the bottleneck.** Several mechanisms have no direct number (levy rate, exemption,
   endogamy) — benchmark on OUTCOMES, and say so. Digestion must extract every available target (like T-5/T-9).

## R-105 — CARRYING-CAPACITY BUG: agglomeration escaped the ceiling (2026-07-26) **[FIX UNVERIFIED]**

**The bug.** Point-mode agglomeration adds a SUPERLINEAR occupancy bonus `aggl_R*(n**aggl_a - n)` to ANY occupied
cell (phase1_model.py ~1602), but the R-63 carrying-capacity ceiling was gated on `(cx,cy) in _settlement_sites`
(~1606). Non-settlement cells therefore had UNCAPPED increasing returns: more crowding -> superlinearly more food
-> more people. No Malthusian limit exists on that path.

**Evidence (R-104 arm coastal-tropical seed 3, specimen `campaign_trajectory_r104_ctrop_forage_s3.json`):** sat at
pop ~3000 for 1750 steps, then surplus_med climbed 0.50->0.70->0.94->**1.00 (saturated)** and pop went
3259->4794->8340->17800->40919->**97551** in 1250 steps, with **ZERO starvation deaths** at 61 agents/cell and
mean_reserve unchanged at 0.316. n_settle stayed FLAT at ~32 (capped path) while n_villages exploded 20->751
(uncapped path) — the signature that localises it. Tier-1 foraging is NOT at fault (occupants split a cell via
compute_harvest_shares).

**The fix (committed c2c6067, NOT yet suite-tested).** `enable_aggl_ceiling` applies the ceiling wherever the
agglomeration bonus applies. Default OFF in config (every pre-R-105 result reproduces bit-exactly); ON in the
campaign harness via `C_AGGLCEIL` (set 0 to reproduce the gap for A/B).
Partial verification: re-running the exploding specimen with the fix showed starvation RETURN (74 deaths by step
500 vs 0 during the explosion) and surplus FALLING (0.609->0.536) instead of saturating; stable at pop 5023 @1250.
Needs to clear step 2000 (where the buggy arm tipped) to be conclusive.

**CONSEQUENCES — carry into every downstream reading.**
- Expect the fix to LOWER carrying capacity in dense runs. **R-64's validated 9-16% stratification, and any
  population-equilibrium/village-count result, are PROVISIONAL until re-validated with C_AGGLCEIL=1.**
- The R-103h flat-tropical 40k explosion and the R-104 "seed bifurcation" (seeds 0/1/2 -> 5937-8504; seed 3 ->
  97551) are almost certainly this bug, NOT ecology or bistability.

## R-103h — DIVERSE-WORLD DIAGNOSTIC (overnight, 8 arms x ~15k budget-capped, 2026-07-24)

4 worlds x {forage, agri=improved_land}. Current validated stack (R-89..R-101; R-103 goods OFF). No machine-sleep.

1. **R-103g ROBUST — CONFIRMED.** The wealth-in-people aristocracy replicates across ALL biomes: noble
   lineage_size_lift **3.3-5.8x** and lineage_size_gini **0.51-0.68** (BHM stratified range) in 7 of 8 arms, while
   GOODS (material lift) stays flat **1.0-1.14** everywhere. Not a coastal-tropical artifact. The elite is in people.
2. **Nieboer-Domar fork NOT demonstrated with this proxy.** improved_land (worked/ownable land) did NOT wake the
   goods axis (material lift ~1.0-1.1 in both forage AND agri arms). Worked land != true circumscription (resources
   still not scarce enough to trap labour). A real goods-elite needs a CIRCUMSCRIPTION mechanism (bounded
   resources), not just claimable land. Open question, not closed.
3. **ANOMALY (n=1): coastal-tropical + agri** — the one arm where the people-elite INVERTED: lineage_size_lift 1.11
   (vs 3.97 forage), noble cred lift 0.50 (nobles LOWER cred). Ascription attached to small/low-cred lineages here.
   Seed fluke or a real aquatic-rich x agriculture interaction — needs replication (matched seeds).
4. **ISSUE FLOATED UP (checker false-positive):** invariants.py flags `leader_tenure_yr` as STUCK, but it is
   CONVERGING to a sensible ~7.8yr equilibrium, not frozen. The STUCK detector should exempt metrics that have
   legitimately reached equilibrium. Checker tuning, NOT a model bug. (No extinctions; budgets fired cleanly.)

## R-103g — THE ELITE WAS IN PEOPLE, NOT GOODS (2026-07-23, reframing finding)

The whole R-103 arc measured GOODS (material/cred/food) and found the noble lineage flat (~1.0) → "big men not
chiefs". Measuring the PEOPLE axis instead: **noble lineages command 2.9x the followers of commoner lineages**
(noble_lineage_size_lift), with **lineage_size_gini 0.50** (BHM stratified range 0.4-0.6) — while STILL flat in
every goods currency. The chiefly elite EXISTS; it is a WEALTH-IN-PEOPLE aristocracy (Guyer; Kopytoff&Miers), and
every prior diagnostic was one axis over (the R-103c 'wrong currency' trap, again).

**Nieboer-Domar, confirmed in the model:** in a LAND-ABUNDANT / open-resource world you cannot hold an elite in
goods (dependents just leave and forage elsewhere — which is why material never compounded, all day). Elites here
form in PEOPLE. The material machinery (tribute/inheritance/exemption, R-103d-f) is the right tool for a
CIRCUMSCRIBED (land-scarce) world, NOT this one — a real biome-dependence fork to test.

**Substrate-driven, not the stack:** lineage_size_lift is 2.9 in BASE and 2.5 with the full tribute stack — the
aristocracy comes from polygyny + status->RS + lineage branching, NOT from anything built this session. It is
stable (~2.7x), Kachin-scale, not runaway.

**CONSEQUENCES (rewrite the spine):**
1. Stratification classifier + elite diagnostics must key on FOLLOWING (lineage/dependent concentration), not goods.
2. Goods-accumulation (tribute etc.) is deferred to the circumscribed-world arm; it is not this world's elite axis.
3. No new mechanism needed to CREATE the elite. To make it COMPOUND further: the non-decaying wealth-in-people
   forms — clientage -> bridewealth -> slavery (Flannery ch.5 NW Coast; Kachin mayu-dama). Lit to FILE: Guyer 1993,
   Kopytoff & Miers 1977, Nieboer 1900 / Domar 1970.
CAVEAT: lineage_size is a PROXY for a following (Nootka/conical-clan reading); causation likely size->ascription.

## R-103e/f PROGRESS (2026-07-23, link 2 build)

- **Office-levy shortcut RULED OUT (R-103e).** Strengthening + exempting the existing `leader_share` levy raised
  leader_material_lift (1.26) but NOT noble_material_lift (1.10) — it fills the rotating OFFICE, not a hereditary
  LINEAGE. An office levy makes a big-man's hoard, not a duke's estate. Also found + fixed: the exemption covered
  only the overreach DEPOSITION (line ~3146), not the wealth DISGORGEMENT (line ~2347) — both now exempted.
- **Per-lineage tribute BUILT (R-103f, `enable_lineage_tribute`).** The band's CHIEF (top-cred member of an
  ascribed lineage) levies `lineage_tribute_frac` (~0.15, gumsa a-thigh) of non-lineage production. 2000-step
  benchmark: STRUCTURE moves toward chiefdom — ascribed_frac 0.32→0.22 (elite NARROWS), %stratified 3.8→5.9,
  village_gap_d 0.137→0.216, noble_cred_lift 1.05→1.24 — but the MATERIAL estate does NOT compound
  (noble_material_lift oscillates ~1.0–1.16; gini_material flat ~0.16). The estate drains as fast as it fills.
- **HYPOTHESIS (reversion collapses the estate) — FALSIFIED (2026-07-23).** Tribute with `enable_delegitimation`
  OFF did NOT compound; it was WORSE — noble_material_lift 1.16→1.05, village_gap_d 0.22→0.06, and ascribed_frac
  ratcheted to **0.45** (the nobility-universal degeneracy returns). The reversion is PROTECTIVE — it culls the
  elite to keep it narrow and the break open. It is not the blocker.
- **The real blocker (diagnosed):** the CHIEF is recomputed each step (top-cred ascribed member), so tribute
  sprays across a CHURNING set of chiefs and never accumulates in ONE persistent lineage. Material also decays
  (~0.002/step) faster than a churning chief can refill. **NEXT LINK = a genuinely HEREDITARY chiefly office**
  (succession → the heir, so the tribute-right + estate stay with one lineage across generations). The
  achieved-leadership model (merit=cred·prowess, recomputed) structurally lacks this — it is the (5→6) step.
  Companion levers: slower material_decay for durable prestige goods (staple vs wealth, D'Altroy&Earle);
  endogamy sealing the break. STATUS axis already responds; only the WEALTH axis needs the hereditary office.

## NEXT (the digestion session, dependency order)
1. Digest Johnson & Earle + Earle (staple/wealth finance) → the sequence + tribute target.
2. Build **(2) tribute** (legitimacy-gated per-lineage), benchmark: does noble_material_lift rise > 1?
3. Then (3)+(4) already built become live → benchmark hereditary estate (5).
4. Then (6) endogamy guards it; (7) gap-classifier detects it. Benchmark each against EA/Flannery.
