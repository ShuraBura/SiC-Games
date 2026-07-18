# MECHANISM CHARTER — the operator discipline

**Status:** ADOPTED 2026-07-18 (supervisor). Binding on **every mechanism added from this point**, and the
retrofit classification of the existing 60 is recorded in §4.

This is to mechanisms what `DOCS_CHARTER.md` is to documents: a contract, not a description. Its companion is
`ARCHITECTURE.md` §0 (how to read the model); this document says **what a mechanism is allowed to be**.

---

## 1. Why this exists

The project is positioned as physics benchmarked by anthropology. Audited honestly (2026-07-18), that was only
half true:

- **The terrain layer genuinely is field physics.** NPP, wateracc, cultivability, soil and climate are scalar
  fields on a lattice; IFD movement is gradient response; harvest is local field sampling.
- **A few social pieces are genuinely operator-shaped.** The cred-weighted draw `cred^κ/Σcred^κ` is a projection.
  Deffuant updating is a contraction. The cred homeostat is a contraction with spectral radius < 1 — and that is
  not decorative: R-81's bug was exactly *"the co-moving population mean is not a contraction."*
- **Everything else was procedural accretion.** Three unrelated status scalars with ad-hoc couplings, no shared
  basis, 60 flags with no type, an operation order that is historical rather than principled, and nothing
  declaring what it conserves.

Two of this month's bugs were *type errors wearing domain clothes*:

- **DE-18 / R-82** — a redistribution operator applied to a group of size 1–2. Read as "the mechanism is inert."
  It was the **unit**, not the mechanism.
- **DE-19 / R-84** — an affiliation operator whose ON/OFF output was bit-identical. It **passed while doing
  nothing**.

A typed system catches both mechanically, because **every category carries an invariant, and an invariant is a
test**.

## 2. What "operator" means here — and what it does not

**It means: a declared transformation with a declared invariant.** It does **not** mean a linear map.

Do not attempt to force the model into linear-operator/eigenvalue formalism globally. Birth and death change the
dimension of the state space; mate choice is combinatorial; fission triggers are hysteretic switches. No global
linear operator exists for that, and asserting one would be numerology. The spectral language is legitimate
**locally**, about a linearization around an equilibrium (§5), and nowhere else.

## 3. The type system

**State** (what operators act on):

| Type | Meaning | Examples |
|---|---|---|
| **S — Substrate** | Scalar fields on the lattice; the gradients everything else responds to | NPP, wateracc, cultivability, soil, capacity |
| **F — Forcing** | Exogenous, time-varying drivers | climate, season, ENSO, volcanic, `enable_tier2_shock` |

**Operators** (the eight kinds of thing a mechanism may be):

| Type | Does | **Invariant (= the test)** | Vectorization |
|---|---|---|---|
| **T — Transport** | moves agents in space | agent count AND every per-agent quantity unchanged | **full** — elementwise on position arrays |
| **P — Production** | field → agent quantity (source) | Σ extracted ≤ field availability; field debited by exactly that | **full** — gather by index |
| **D — Dissipation** | destroys quantity (sink) | every affected quantity non-increasing | **trivial** — elementwise multiply |
| **X — Exchange** | moves quantity *between agents* | **Σ quantity conserved** (to float tolerance) | **full** — segment-sum (`np.add.at`/`bincount`) |
| **C — Conversion** | capital type → capital type (**the operator-matrix off-diagonals**) | must declare **debited** or **catalytic** | **full** — grouped normalize |
| **A — Affiliation** | changes the graph (who is bonded/grouped/owns) | **no quantity may change**; and it MUST demonstrably change the graph | partial — graph ops |
| **N — Demographic** | changes the agent set | dimension-changing; must declare what a birth inherits and a death releases | hard — batch by mask |
| **H — Inheritance** | copies state across an N event | acts **only** at birth events; a declared parent→child map | **full** — gather from parent index |

**Read-only:**

| Type | Rule |
|---|---|
| **O — Observer** | zero mutation, **and must not consume the model RNG** |

O is not aspirational — it is already enforced in code by `_diag_rng` (a dedicated diagnostic RNG so read-outs
never perturb `self.random`). That the taxonomy has an existing, independently-arrived-at member is evidence it
describes the model rather than being imposed on it.

### 3.1 The declaration requirement (binding)

Every new mechanism must, **in its docstring**, state:

1. **Type** — one of `S F T P D X C A N H O`. If it needs two, it is **two mechanisms**; split it.
2. **Unit** — the entity it operates on: agent · pair · household · **band** · settlement · cell · region.
   *This line exists because of R-82.* A social operator on a unit of size 1–2 is inert by construction.
3. **Invariant** — the category's invariant, plus how it is asserted in tests.
4. **Anchor** — `[VERIFIED source]`, `[DESIGN]`, or `[PROVISIONAL]`. Unchanged from existing practice.

### 3.2 Composite mechanisms

Some mechanisms genuinely span types — village budding is **A** (fission of the settlement graph) **+ T**
(relocation of the daughter). Split them into typed sub-steps rather than declaring a hybrid, so each piece keeps
a checkable invariant. `_maintain_leader_office` is the worked example: **A** (office succession, changes no
quantity) + **T** (desertion, moves an agent between bands, conserves everything he carries).

## 4. Retrofit classification of the existing 60 flags

Recorded 2026-07-18. Where a flag is composite the **primary** type is given first.

- **T Transport** — `enable_productivity_mobility`, `enable_terrain_move_cost`, `enable_emergent_abandonment`,
  `enable_site_appraisal`, `enable_landscape_packing`
- **P Production** — `enable_game`, `enable_agriculture`, `enable_agglomeration`, `enable_forage_cap`,
  `enable_catchment_ceiling`, `enable_resource_storability`, `enable_improved_land`, `enable_alluvial_renewal`
  (a *source*, not a sink — it renews soil)
- **D Dissipation** — `enable_soil_depletion`; `material_decay`, metabolic burn, storage spoilage (not flags)
- **X Exchange** — `enable_storage`, `enable_store_anchor`, `enable_provisioning`, `enable_leveling`,
  `enable_leader_share`
- **C Conversion** — `enable_cred_status` (cred → food share, exponent κ), `enable_prowess_facet`,
  `enable_ascribed_mate_choice` (status → mating), `enable_material_capture` (production → durable capital),
  `enable_standing`, `enable_cred_renorm` (**gauge fixing**, not conversion — see below)
- **A Affiliation** — `enable_pair_bonds`, `enable_bonded_mating`, `enable_marriage_aggregation`,
  `enable_exogamy`, `enable_adaptive_connubium`, `enable_band_affiliation`, `enable_dynamic_bands`,
  `enable_emergent_band_size`, `enable_size_repulsion`, `enable_malnutrition_fission`,
  `enable_resource_directed_fusion`, `enable_aggregation_sedentism`, `enable_settlement_scalar_stress`,
  `enable_village_scaling`, `enable_village_budding` (+T), `enable_morph`, `enable_economic_defensibility`
  (ownership = the topology of claims), `enable_leader_office` (+T), `enable_leader_coherence`,
  `enable_band_family_knobs`
- **N Demographic** — `enable_orphan_mortality`, `enable_energetic_fertility`, `enable_sedentism_fertility`,
  `enable_life_history`, `enable_condition`, `enable_nutrition_synergy`, `enable_terrain_risk`,
  `enable_density_disease`, `enable_terrain_pathogen`, `enable_band_risk` (shelved, DE-4),
  `enable_infanticide` (**UNIMPLEMENTED STUB — no logic reads it; a trap, see §6**)
- **H Inheritance** — `enable_genome`, `enable_paternity`
- **F Forcing** — `enable_tier2_shock`
- **O Observer** — `enable_genealogy_log`

**Two classification findings worth keeping:**

1. **`enable_cred_renorm` is not a Conversion — it is gauge fixing.** It rescales cred to population-mean 1, and
   every downstream use is *relative* (`cred^κ/Σ`, normalised mate weights). It changes no observable. That is
   exactly a choice of gauge, and it explains why R-81 could adopt it without disturbing R-19: a gauge change
   cannot move a physical quantity. **New rule: a mechanism that changes no observable must be declared as gauge
   fixing and must be shown to leave the diagnostics invariant.**
2. **Affiliation is over-represented — 20 of 60 flags.** The model's social layer is overwhelmingly *topology*.
   That is the honest shape of the thing we built, and it says where the remaining compute cost lives (§7).

## 5. Dynamics: what kind of feedback produces what behaviour

Not a mechanism — a **design criterion**, applied when choosing one. This is the one place spectral language is
legitimate, and it is about a linearization around equilibrium, not the model as a whole.

| Feedback structure | Linearized signature | Behaviour | Where we have seen it |
|---|---|---|---|
| Instantaneous negative | real eigenvalue < 0 | **stable node** — exponential return | R-68 kill-half → recovery in 250 steps; Boehm leveling caps inequality *within the same step* |
| **Delayed** negative | complex pair, Re > 0 | **oscillation** | **not present anywhere in the model** |
| Positive | real eigenvalue > 0 | runaway / fixation | R-66 winner-take-all patriline fixation |

**This unifies three separate negatives into one statement.** DE-14 records connubium (R-67), substrate (R-68)
and soil (R-71) as three independent failures to produce secular cycles. In these terms they are *one* failure:
**every feedback in the model is instantaneous**, so the linearization has no complex pair, so it cannot
oscillate — it can only return to equilibrium or run away.

**The design criterion that follows:** a mechanism intended to produce cycles must introduce a **lag between a
quantity and the correction that removes it**, of order the system's relaxation time (~250 steps, measured in
R-68). Elite recruitment responding to elite wealth with a generational (~20 yr) delay is the canonical
structure. Registered as **H-CYCLES** in `HYPOTHESES.md`.

**Deliberately NOT adopted:** rebuilding as a mean-field/Fokker–Planck field theory. It would make the spectrum
analytically available but would destroy the individual-level results that are the project's actual output — RS
skew, dynasties, kinship, orphan mortality. Mean-field linearization stays available as an *analysis* tool for
H-CYCLES specifically, never as the model.

## 6. What the invariants would have caught (and must catch next time)

| Failure | Category | Invariant that catches it |
|---|---|---|
| R-82 aggrandizer capture inert (DE-18) | X on the wrong unit | the **Unit** declaration — X on a unit of size 1–2 is inert by construction |
| R-84 `succession_dissolve` vacuous (DE-19) | A that changed no graph | A **must demonstrably change the graph** |
| R-74 vacuous test (`1.0 == 1.0`) | N with an untested invariant | N must declare what a death releases |
| `enable_infanticide` stub | N with no implementation | **every declared flag must have a live reader** |

**Standing check, from DE-19:** if a flag's ON/OFF output is indistinguishable, that is a **specification bug**,
not a small effect size — unless it is declared gauge fixing (§4), where invariance is the point.

## 7. Compute: the type tells you the vectorization strategy

Supervisor directive (2026-07-18): *vectorization, not looping, where possible.* The categories map directly onto
how each mechanism should be executed — which is why typing is a prerequisite for the performance work, not a
detour from it.

- **Vectorizable now (T, P, D, X, C, H — 6 of 8):** all are elementwise, gather-by-index, or segment-reduction
  operations. X in particular is `np.add.at` / `bincount` over a group-id array — the current Python loop over
  bands is the textbook case for replacement.
- **Hard (A, N — 2 of 8):** A is graph mutation, N changes dimension. These are where per-agent loops are
  *legitimate*, and where `soa.py` (structure-of-arrays) would pay off via masked batch operations rather than
  vectorized arithmetic.

Since **A is 20 of 60 flags**, the honest expectation is that vectorizing T/P/D/X/C buys real time on the
economy, while the social layer stays loop-bound until the affiliation representation itself changes (agent
objects → id arrays + adjacency). Do not promise a blanket speedup; promise it per category.

## 8. Applying this to new work

For every proposed mechanism, before writing code:

1. **Name its type.** If you cannot, the mechanism is not yet understood well enough to build.
2. **Name its unit.** (R-82.)
3. **Write the invariant assertion first**, as a test. It is cheap and it is the thing that catches the two bug
   classes above.
4. **State the anchor** — `[VERIFIED]` / `[DESIGN]` / `[PROVISIONAL]`.
5. **Default-OFF, bit-exact** when off. Unchanged from existing practice.

**Agent specializations** (warriors, shamans, managers) are the dual of this system: a mechanism is an operator;
a specialization is **which operators an agent is coupled to**. `aggrandizer` is already a de-facto agent type,
and `prowess` generalising from scalar to a per-activity vector is the natural basis. Build only after the typing
retrofit, so specialised couplings inherit the invariants rather than re-introducing the R-82 unit error in new
clothes.

---

*Charter adopted 2026-07-18. Amend by dated note; classifications in §4 are append/update, not rewrite.*
