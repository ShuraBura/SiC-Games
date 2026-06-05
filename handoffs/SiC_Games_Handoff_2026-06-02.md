# SiC Games — Session Handoff (2026-06-02, resource-ecology substrate-design session)

**Awaiting:** Stage 6.0a report from CC.

---

## 1. Current state

The resource-ecology arc opened under fresh **Stage 6** numbering (supersedes the old "OWE-2 /
Stage 5.3 terrain" label). Two blueprints written this session, in dependency order:

- **Stage 6.0a — Substrate** (`/mnt/user-data/outputs/SiC_Games_Stage6_0a_Substrate_Blueprint.md`)
  — written, ready for CC. This is the next thing to run.
- **Stage 6.0b — Graded terrain + metabolic multiplier**
  (`/mnt/user-data/outputs/SiC_Games_Stage6_0_Terrain_Blueprint.md`) — written **but now
  superseded in part**: it was drafted as the first stage and assumes one-agent-per-cell. It
  must be **revised to stand on the 6.0a substrate** (density already variable; affinity &
  move-cost-terrain hooks already present in the utility, just needing activation). Not a
  throwaway — a targeted revision.

Build phase is **C-model-first, slow, layered**: build the best C model one mechanic at a time;
port to Si as an architecture lens; run comparative scenarios later. Per-stage gates =
equivalence/recovery + C-behavioural check + Si-portability note. **No Si runs, no inversion
protection, no H1(ii) work during the build.**

---

## 2. Decisions locked this session

- **Spatial scale declared:** 1 cell = **100 km²** (10×10 km) → 100×100 grid = **1,000,000 km²**
  continental forager landscape. Spatial analogue of the locked monthly step. A band's monthly
  range ≈ one cell. This is a *new declared physical constant* — not yet in any doc (see §4).
- **Multi-occupancy substrate:** one-agent-per-cell removed. Density now **emerges** from
  resource competition, not a 1/cell cap (supervisor chose emergent "C", not capped "A").
- **Harvest = resource-split.** Even split (scramble) is the floor / Si / neutral baseline.
  **Cred-weighted contest for C** (`share ∝ φ^κ`), κ=1 live, **κ=0 recovers even split** (used as
  validation reference). Material payoff is the point of Cred; contest deliberately makes
  resource decisions noisier (yield vs status).
- **Movement = local-gradient diffusion**, not navigation. Von Neumann neighbourhood only;
  **long-range awareness dropped**. Agent steps to best *per-capita* neighbour; migration emerges
  as a chain of local steps.
- **Traversal cost DISSOLVED** (not deferred): diffusion makes every move single-step onto one
  known cell, so crossing cost = destination-terrain move cost (cheap). No step-wise locomotion
  ever needed. (This reverses the earlier "defer traversal cost" note.)
- **Move cost:** flat (active, default 0) + destination-terrain (hook, off until 6.0b). No
  path/crossing cost.
- **ψ (sociability) IS the crowd-affinity hook** (per MODEL_SPEC §39/§54). Re-pointed from
  adjacency (now meaningless under co-occupancy) to **cell occupancy**, held **neutral** in 6.0a.
  Activating ψ-as-crowd-response is part of the trait re-expression deliverable.
- **Saturation-penalty-as-global-force dropped** — replaced by ψ (per-agent crowd response),
  inactive now. The `K_cell` ceiling survives only as the recovery-gate device (=1 forces
  single-occupancy) and an optional safety rail.
- **Reproduction under co-occupancy:** parents co-located; **offspring spawns on parent cell**
  (no dispersal — dispersal deferred, noted for Allee interaction).
- **Utility built in full form with neutral hooks:** per-capita yield (active) × resource-affinity
  (=1) × crowd-response/ψ (=1) − move-cost. Socket now, bulbs later — matches house pattern
  (MODEL_SPEC §188, λ_int=0).

No locked *parameters* (PARAMETERS-owned values) changed this session — κ, move costs, cell_area
are new substrate config introduced by 6.0a, to be recorded when 6.0a lands.

---

## 3. Open items / on the horizon

- **Stage 6.0a report** — awaited. Read against its pre-registered checks (recovery gate;
  C viability at κ=0 vs κ=1; emergent density vs ethnographic ~0.01–1 persons/km²; Matthew-runaway
  flag; N_carry/N ratio flag).
- **Trait re-expression deliverable** — now the formally-next *design* item. Full port of the
  trait vector (ψ, c1, c2, φ, + future resource-affinity) to band-on-a-cell semantics. 6.0a only
  made the minimal don't-break ruling (§5 of that blueprint). Should precede any trait-bearing
  stage (affinity stage).
- **Stage 6.0b revision** — rebase the terrain blueprint onto the substrate (see §1).
- **Then, in order:** tiered substrate (two-tier first, gated/mobile tiers later) → heritable
  affinity → per-tier experience + lossy transmission + OWE-13 → seasonality-as-insolation /
  game migration → disasters (field-editing, then converter).
- **N_carry reconciliation** — N_carry was a 1/cell-era construct; multi-occupancy self-limiting
  density may make it the wrong construct entirely. Resolve in the design doc, not piecemeal.
- **"Rule 11" collision** — "Standing Rule 11 = embed all plots" (old blueprints) vs CLAUDE.md
  "Rule 11 = failed gate is blocking STOP". Same number, two rules. Renumber one in CLAUDE.md.

---

## 4. Doc-update guidance

Doc updates split by owner. **CC-owned updates now live in the 6.0a blueprint §11** ("On
completion — documentation updates"), bound to the stage that causes them and gated on the report
emitting — PARAMETERS (new substrate params), MODEL_SPEC (multi-occupancy/contest/diffusion/ψ
re-point, append-with-strikethrough), ROADMAP (C/Si harvest row + deferred/Q-list incl. dissolved
traversal cost), and the HYPOTHESES pre-reg confirmation. Standing triggers (ROADMAP end-of-stage,
ARTIFACTS on emit) fire as usual. Nothing for you to do there beyond reviewing CC's updates against
INDEX discipline when 6.0a lands.

**Supervisor-owned (yours, outside CC):**

| Update | Home doc | When | Note |
|---|---|---|---|
| **Concept-map edits** — made this session on the read-only copy, **NOT yet persisted** | `SiC_Games_Resource_Concept_Map.md` | **Now** | Re-apply to canonical: §9 promote variable metabolism into 6.0b + **dissolve** traversal cost (was "defer"); §12 record 6.0a/6.0b split, diffusion movement, ψ-as-crowd-response, contest-now, saturation→ψ reframe. I can produce exact diff text. |
| **HYPOTHESES pre-registration** | `HYPOTHESES.md` | **Before reading the 6.0a report** | Anti-HARK, timing-critical. Lift the 6.0a §7 pre-registered readings in *before* the numbers are seen. (CC §11.5 only *confirms* this was done — the entering is yours and must precede analysis.) |
| **Superseded design doc** status | `SiC_Games_ResourceEcology_DesignDoc.md` | At design-doc rewrite (§5) | Carries stale inversion-protection + R1–R4 framing; mark superseded. |
| **"Rule 11" collision** | `CLAUDE.md` | Whenever convenient | Renumber one of the two Rule 11s (plots-embed vs failed-gate-STOP). |

---

## 5. When to build the design doc

**Not yet — and now there's a principled reason, not just caution.** The design doc's job is to
commit the *spine* (the mechanic ordering and how the pieces fit). The arc has just been
restructured at the substrate level this session, and **two things still move the spine**:

1. **6.0a empirical results.** If emergent density comes out wildly off the ethnographic band, or
   if Cred-contest produces Matthew-runaway that needs a mitigation mechanic, the substrate itself
   gets an unplanned sub-stage — which changes what everything downstream stands on. Committing a
   spine before 6.0a returns repeats the exact error the project already named: a conditional
   document with an unresolved fork has a permanently-undecided spine.
2. **The trait re-expression deliverable.** It hasn't been done, and it determines how affinity,
   ψ-crowd-response, c1/c2, and φ-contest interact under co-occupancy. The design doc's
   trait-and-affinity sections can't have a committed shape until that port exists.

**Recommended trigger for the design-doc rewrite:** when **both** (a) 6.0a has returned and the
substrate is confirmed viable (density sane, C survives, runaway either absent or mitigated), and
(b) the trait re-expression deliverable is done. At that point the substrate is empirically solid
and the trait interactions are specified — the spine can be *committed*, not guessed. That's also
the natural moment to fold in the locked-config block (grid, N, N_carry reconciliation, cell_area,
step, the Stage-4.4 params, the new 6.0a params) as the single authoritative source this session's
N≈2300 confusion showed is missing.

Until then the **concept map remains the anchor** (reference, not commitment) and blueprints carry
their own self-contained specs. The design doc is the *third* thing, written once the substrate is
real and the traits are ported — likely 2–3 deliverables from now.

A lighter intermediate option, if you want something more committal than the concept map before
then: a **one-page locked-config + committed-ordering stub** (just the spine decisions already
firm: Stage 6 order, C/Si harvest asymmetry, spatial scale) — cheap, useful as a reference, and it
becomes the skeleton the full design doc fleshes out. Not necessary, but low-cost if the
undecided-spine risk feels uncomfortable in the interim.

---

*End of handoff — 2026-06-02.*
