# Documentation Directive — Terrain-Design Session (2026-06-09)

**For:** Claude Code
**Type:** Documentation update only. No model code. No runs.
**Source of authority:** the supervisor design decisions recorded in
`SiC_Games_STANDING_HANDOFF_2026-06-09.md`. This directive turns those decisions into canonical
doc edits so they stop living in chat scrollback (one fact, one home).

**Standing caution:** the repo is a Drive-synced folder (see Task 6 / the migration walkthrough).
Make these edits through normal git on the machine where the repo lives; commit and push. Do not
rely on Drive to propagate them.

---

## Task 1 — Correct the Resource Concept Map coordination semantics

File: `SiC_Games_Resource_Concept_Map.md` (currently v0.1, 2026-06-02).

The map predates this session's literature check and is now wrong on one point. Edit:

1.1 **§2 tier table** — the "Foraging (mobile) / Game" row currently lists coordination role as
"Multiplier — strongest here (cooperative hunting)." Change the coordination role for the game
tier to reflect that cooperative hunting provides **variance/risk-reduction, NOT a mean-yield
multiplier** (empirical: Hawkes et al. 1982; Bliege Bird et al. 2012; Janssen & Hill 2013/2014 —
coop hunting gives lower probability of no food, not higher mean returns). Yield-superadditivity
survives only at the **cultivation** tier.

1.2 **§2 — add the savanna access-gate distinction.** The game tier splits by biome:
   - forest game: huntable solo → optional-multiplier (solo viable).
   - savanna/open game: ~zero solo, unlocks only above a **band-size access threshold** →
     **access gate**, return curve = step-then-plateau (zero below threshold, jumps to viable,
     then flat/declining). This is the *same access-gate mechanic* §2/§4 reserve for cultivation,
     but in minimal form (no settlement dimension).

1.3 **§4 access table** — add savanna cooperative hunting as an **access gate** entry
(requires: party size assembled here-now; does NOT require settlement, unlike cultivation).

1.4 **§5 C/Si table** — the game-tier C advantage is **insurance / variance-reduction**, not
"hunts more efficiently." Reframe the mobile-game cell accordingly. (Note: Si is out of current
discussion; this is a forward note only.)

1.5 **§12 build-order sketch** — annotate that the access-gate mechanic may **debut in stage 2
(savanna hunting)**, proven, before cultivation adds the settlement dimension. Do not rewrite the
sketch; add the annotation.

Bump the map to v0.2 with a revision-history line: "v0.2 (2026-06-09): game-tier coordination
corrected to variance-reduction not yield-multiplier; savanna access-gate added; terrain section
expanded (Task 2)." Keep the REFERENCE-ONLY / no-build-commitment header intact.

---

## Task 2 — Expand the Resource Concept Map terrain section (§9) and add a risk section

File: `SiC_Games_Resource_Concept_Map.md`.

2.1 **§9 (Terrain & metabolism)** — expand from the current two-line stub to record the
derive-from-primitives architecture decided this session (supervisor-confirmed):
   - primitives: elevation (relief + roughness) → water by flow accumulation → derived fields.
   - derived fields (all static arrays, computed once at world init): forage capacity (tracks
     NPP), game capacity (hump-shaped in NPP, peaks at savanna/edge), movement cost (slope-
     derived, edge property), cost-to-exist, water accessibility, base mortality risk.
   - six biomes + water: water, wetland/floodplain, forest, savanna/edge, steppe, desert, mountain.
   - **forage≠game inversion** as the engine of the H/G spatial split (forage peaks forest/wetland;
     game peaks savanna/edge; the separation is load-bearing).
   - **water = distance-decayed accessibility field → metabolic penalty, NOT inventory** (decided).
   - **vectorization constraint (hard):** terrain is precomputed static / seasonal-static arrays;
     only per-step contact is gather-at-agent-positions + one seasonal broadcast; no terrain
     computation in the agent loop; cost-to-cross is a precomputed (100,100,4) neighbour-cost
     array and is the only terrain field touching the movement hot path.
   - move "variable metabolism by terrain" from 🔵 DEFERRED to 🟡 DISCUSSED-CONFIRMED (it is now
     part of the terrain stage as cost-to-exist + terrain-modulated metabolism).

2.2 **Add §13 — Risk & mortality (new section).** Record:
   - base-risk field: terrain-derived (exposure on steep/high ground, thirst far from water,
     shelter in cover, drowning at water edges), agent-agnostic, **generated and rendered in the
     terrain stage; no agent response yet**.
   - company-reduces-risk social modifier: candidate **primary social-aggregation driver**; gets
     its **own dedicated stage**, introduced alone, with a decomposition diagnostic built
     alongside (separate risk-aggregation from resource-aggregation — same discipline as the
     OWE-13 specialization-decomposition concern).
   - open core question for that stage: **risk currency + risk/energy tradeoff** (mortality vs.
     starvation; agent decision rule for "safe but starving" vs. "fed but dangerous").
   - TMTS guard: code the risk *field* and the agent *response curve*; do not code aggregation
     directly — measure whether it emerges.

---

## Task 3 — Log deferred mechanics in their homes

3.1 Ensure each deferred mechanic below has a home. Concept map holds the design idea; ROADMAP
gets a one-line forward pointer where it is a future stage. Do NOT create stage blueprints for
any of these — they are not committed builds.

| Mechanic | Home | Trigger |
|---|---|---|
| base-risk terrain field | concept map §13 | built (render-only) in terrain stage |
| company-reduces-risk modifier | concept map §13 | own dedicated stage, post stage-2, + diagnostic |
| risk/energy tradeoff + currency | concept map §13 (flagged core open Q) | top of the risk stage |
| savanna-hunt payoff: participant-only vs area-shared public good (free-riding fork) | concept map §2/§4 | stage 2 |
| water storage/provisioning | concept map, horizon | far (cultivation era) |
| game ecotone/edge peak | concept map §9 (game-field def) | stage 1 game field |
| terrain feasibility statistics | becomes production-generator acceptance gate | stage 1b production spec |
| defensibility/visibility terrain | concept map, horizon | far; may fold into risk |
| N_carry re-derivation (multi-occupancy) | ROADMAP / PARAMETERS note | density/calibration work |

3.2 In ROADMAP, ensure the build sequence reflects: **Terrain (stage 1: 1a prototype done →
1b production generator → 1c wire into SoAWorld) → Seasonal resources / game migration (stage 2)
→ later: risk-response stage, savanna-hunt mechanics, cultivation.** Annotate that cultivation /
proto-ag is deferred (was previously framed as the near target; it is not).

---

## Task 4 — File the terrain prototype as a project artifact

4.1 Place `sic_terrain_prototype.html` in a versioned location in the repo — suggest
`prototypes/` (create if absent). It is a self-contained HTML judgment tool, no dependencies.

4.2 Add an `ARTIFACTS.md` entry: name, path, one-line purpose ("interactive terrain-generator
judgment tool — derive-from-primitives, 6 biomes, forage/game inversion, feasibility readouts;
NOT the production algorithm"), date 2026-06-09, and the note that the production generator is a
separate future deliverable whose acceptance gate is the feasibility statistics.

4.3 `git add` + commit + push through git (not via Drive sync).

---

## Task 5 — Literature provenance (do NOT upgrade citation status yet)

5.1 Record in `LITERATURE.md` as **raised-not-verified** (per the "CC never self-upgrades
citation status without a backing entry" rule) the three anchors from this session:
   - Janssen & Hill 2014, *Human Ecology* — cooperative-foraging ABM precedent; finding: coop
     hunting = risk-reduction not mean-yield. **Flagged: full paper must be read before it
     becomes a project anchor.**
   - Allee-via-foraging-facilitation (cooperation-term functional response lineage) — the
     superadditivity criterion (per-capita intake must rise with N for coop to give mutualistic
     benefit).
   - MVT-for-groups (social patch-departure model) — deplete-and-move mobility falls out of
     regeneration rate.
5.2 Do not cite these in any spec until the provenance bar is met.

---

## Task 6 — Pointer to the migration walkthrough

The Drive-synced-repo hazard and its fix are handled in a separate interactive walkthrough
(`SiC_Games_RepoMigration_Walkthrough_2026-06-09.md`). Do not act on the migration as part of
this documentation pass — it is deliberate surgery to be done interactively with the supervisor.
This directive's edits should themselves be committed through normal git regardless of where the
repo currently sits.

---

## Definition of done

- Concept map at v0.2: §2/§4/§5 coordination corrected; §9 expanded; §13 risk added;
  deferred mechanics logged; revision history updated.
- ROADMAP build sequence reflects terrain→seasonal→(risk, savanna, cultivation) with cultivation
  explicitly deferred.
- Prototype filed in `prototypes/`, ARTIFACTS.md entry added, committed + pushed.
- LITERATURE.md has the three raised-not-verified entries with the Janssen & Hill read-first flag.
- No stage blueprints created for deferred mechanics. No model code touched. No runs.
- This is documentation-only: verdict is the diff, no prose report needed.
