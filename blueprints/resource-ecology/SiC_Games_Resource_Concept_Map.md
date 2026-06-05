# SiC Games — Resource Concept Map (Reference, NOT a Build Commitment)

**Version:** 0.1 (living reference)
**Status of this document:** REFERENCE ONLY. This maps the resource-ecology *concept* as
discussed (2026-06-02). Writing something here does **not** commit it to the build. The
"Reality" tags show what is actually in the code today versus what is discussed/deferred.
The build sequence is a *separate, shorter* commitment made after looking at this map.
**Purpose:** get the whole resource picture onto one page so design decisions are made from
*seeing* it, not holding it in working memory.

**Reality tag legend:**
- 🟢 **BUILT** — in the code today.
- 🟡 **DISCUSSED** — designed in conversation, not built.
- 🔵 **DEFERRED** — explicitly parked (may build later).
- ⚪ **MAYBE/OUT** — raised, possibly out of scope (e.g. Scenario-1 tech tree).

---

## 1. The founding frame (one paragraph)

A **fixed energy chain** of resource tiers (no tech-tree menu expansion — Scenario 2/3, not
Scenario 1). Agents are *converters* tapping different points of the chain. What develops over
a run is not *access* but **per-tier efficiency**, via heritable affinity + experience, damped
so it rises and decays rather than ratcheting. The C/Si difference is **emergent** from who can
pay coordination costs, not stipulated. Seasonality is one insolation forcing propagating *up*
the chain with lags; disasters split into field-editing vs converter-editing.

---

## 2. The resource tiers

| Tier | Example | Yield | Access | Coordination role | Mobility | Reality |
|---|---|---|---|---|---|---|
| **Base (diffuse)** | Solar, gleaning | Low | Individual, immediate | **None** — no coop benefit | Static | 🟡 DISCUSSED |
| **Foraging** | Vegetation | Moderate | Individual, immediate | **Multiplier** — coop *increases* gain, solo still works | Static | 🟡 (current single resource ≈ this, but untiered) |
| **Foraging (mobile)** | Game | Moderate–high, high-variance | Individual, immediate | **Multiplier** — strongest here (cooperative hunting) | **Mobile** — migrates | 🟡 DISCUSSED |
| **Cultivation** | Agriculture | High | **Gated** — requires sociality + settlement to unlock at all | **Prerequisite** — mandatory, not optional | Static (tied to settlement) | 🟡 DISCUSSED |

**Key distinction (the thing that was being conflated):** coordination plays a *different
role* at each tier — irrelevant (base) → optional multiplier (foraging) → mandatory gate
(cultivation). "Activation price" is therefore **two distinct mechanics**, not one parameter:
a **yield multiplier** (foraging) and an **access gate** (cultivation).

**Current code reality:** ONE resource type, fast renewal, instant access, static, no tiers,
no coordination coupling. Everything in the table above is the *target*, not the present.
(🟢 = the current single fast-renewal field; it maps loosely onto an untiered "foraging" cell.)

---

## 3. How resources change — renewal, depletion, mobility

| Property | Behaviour (target) | Tier dependence | Reality |
|---|---|---|---|
| **Renewal rate** | Fast (base) → slow (cultivation). Concentrated tiers renew slower. | Co-varies with tier (thermodynamic concentration takes time) | 🟢 single fast α today / 🟡 tiered |
| **Renewal lag** | Higher tiers replenish with a *lag* after depletion | Higher tier = longer lag | 🟡 DISCUSSED |
| **Depletion response** | Over-working a tier depletes it → forces diversification/move | All tiers; sharper at concentrated tiers | 🟡 DISCUSSED (this is a *damping* mechanism, §6) |
| **Mobility** | Game migrates; others static. Mobility = class attribute, NOT a grid op (keeps grid size fixed — the expensive axis) | Mobile sub-class of foraging tier | 🟡 DISCUSSED |
| **Parameter coupling** | yield, renewal, mobility, diffuseness **co-vary along the chain** by energy-concentration logic — NOT independent knobs (falsifiability win) | — | 🟡 DISCUSSED |

---

## 4. How resources are unlocked / accessed

| Mechanism | Applies to | What it requires | Reality |
|---|---|---|---|
| **Immediate individual access** | Base, foraging | Nothing — agent forages on arrival | 🟢 (current model) |
| **Coordination multiplier** | Foraging (esp. mobile game) | Joint-task machinery; more agents → higher per-agent yield; solo still viable | 🟡 (joint-task mechanic 🟢 exists, not coupled to resources) |
| **Access gate** | Cultivation | Sociality threshold + **sustained settlement** (long residence) | 🟡 DISCUSSED |
| **Heritable affinity** | All tiers | Birth trait biasing which tier an agent engages when multiple attainable | 🟡 (trait vector H_i 🟢 exists; affinity = new component) |
| **Per-tier skill (experience)** | All tiers | Working a tier improves skill at *that* tier (per-agent, per-tier state) | 🟡 DISCUSSED (new state) |

---

## 5. C / Si asymmetry (EMERGENT, not stipulated)

| | C | Si | Mechanism source |
|---|---|---|---|
| **Base (solar)** | Usable, low priority | **Primary** | Diffuse, no coop needed |
| **Foraging** | Usable + **gets the coop multiplier** | Usable, **solo only** (no joint-task machinery) | C has joint-task/Cred; Si doesn't |
| **Mobile game** | Cooperative hunting (multiplier) | Solo only | Same |
| **Cultivation** | **Can pay the gate** (sociality + settlement) | **Structurally closed** until Si sociality designed | C has the social apparatus; Si doesn't (yet) |
| **Skill transmission** | Prestige-weighted (fast, concentrating) | Egalitarian/reciprocal (slow, flat) — when Si Cred exists | C Cred = dominance; Si Cred = reciprocity (ROADMAP table) |

**Architecture principle (Si-as-design-lens):** every resource mechanic is built so C's mode
is *one implementation* against a shared resource state, leaving the seam for Si's mode to
attach later. The resource field is shared world; *how a type extracts from it* is pluggable.
The C/Si access difference is expressed **through the tier/coordination structure**, not as a
separate Si module.

---

## 6. Skill, affinity, and the damping (the developmental dynamic)

| Element | Behaviour | Reality |
|---|---|---|
| **Heritable affinity** | Trait-vector component; seeds specialization; inherited w/ copy-error | 🟡 (H_i vector 🟢; affinity new) |
| **Per-tier skill via experience** | Accumulates with use, per agent per tier | 🟡 DISCUSSED |
| **Lifetime efficiency curve η(a)** | Juvenile ramp → adult peak → elder decline (Cobb-Douglas) | 🟢 BUILT (currently scalar, not per-tier) |
| **Damping 1 — tier depletion** | Over-use depletes → forces diversification | 🟡 DISCUSSED |
| **Damping 2 — aging** | Individual skill dies with the agent | 🟢 (η exists) / 🟡 (per-tier skill new) |
| **Damping 3 — lossy probabilistic transmission** | Only a *small fraction* of skill transmits, stochastically → edge **decays without reinforcement** | 🟡 DISCUSSED |

**Why the damping matters (state explicitly in design):** lossy stochastic transmission gives
asabiyyah a **half-life** — group skill/cohesion rises with successful joint action and
*decays* without it. This produces **endogenous rise-and-decay** (Turchin secular-cycle shape)
instead of ratchet-up-forever. The damping is not just a safety knob against runaway feedback;
it is what makes the cliodynamic target *reachable*.

**Entanglement caution:** affinity (heritable) + experience (accumulates) + transmission
(prestige-biased for C) together mean specialization has THREE entangled sources. The
**OWE-13 movement/specialization-decomposition diagnostic must be built WITH the affinity/
experience mechanic**, not after — or specialization can't be attributed to its source. (This
is also the H-orthogonality payload.)

---

## 7. Seasonality (ONE forcing, class-specific response)

| Aspect | Behaviour (target) | Reality |
|---|---|---|
| **Driver** | Single **insolation** cycle (cold season = less incoming energy at chain base) | 🟢 SeasonalOscillation exists (but as scalar A-multiplier on capacity, NOT insolation-through-chain) |
| **Propagation** | Forcing propagates *up* the chain with **lags**: sunlight drops immediately → vegetation depletes over weeks → game migrates (follows vegetation) | 🟡 DISCUSSED |
| **Visible case** | **Game migration in winter** — the "resources migrate in long cold season" picture, emergent from chain not hand-authored | 🟡 DISCUSSED |
| **Inversion driver note** | Trough depth was the H1(ii) inversion driver (now de-emphasised — see §10); insolation trough is the natural home for it if revisited | 🟢 forcing / context |

**Current reality:** seasonality is a scalar multiplier on a uniform capacity field (confirmed
firing at 100×100 by R0). The "propagates up a tiered chain with lags" behaviour is target,
not built — and is **unbuildable without tiers first** (§9 ordering consequence).

---

## 8. Disasters (TWO distinct mechanics — do not conflate)

| Type | Acts on | Examples | Effect | Reality |
|---|---|---|---|---|
| **Field-editing** | The **resource field** | Flood, earthquake, river shift | **Relocates** resources — buries some tiers, **exposes new** cells/tiers (canyon/river). Spatial map of upper chain is edited | 🟡 DISCUSSED |
| **Converter-editing** | The **agents/population** | Disease, famine | **Depopulates** areas without touching the energy field | 🟡 DISCUSSED |

Both are **irregular, stochastic, heavy-tailed, spatially-local** — distinct from periodic
seasonal forcing. Both use the existing `WorldPerturbation` hook (🟢 protocol exists). Probes
**robustness-to-surprise** (a different resilience property than seasonal buffer-adequacy);
C and Si may rank differently here than on the seasonal channel.

---

## 9. Terrain & metabolism (the foundation layer — and the thing that was getting lost)

| Element | Behaviour (target) | Reality |
|---|---|---|
| **Terrain topography** | Spatially-varying capacity (graded, not flat-within-peak). Foundation all tiers/forcing build on | 🟡 DISCUSSED (OWE-2 / Stage 5.3) |
| **Variable metabolism by terrain** | Per-cell metabolism multiplier tied to terrain type — **RAISED, NOT BUILT, was getting lost** | 🔵 DEFERRED (flagged for re-surfacing — this is the one that nearly fell through the cracks) |

**Note:** terrain is agent-agnostic (symmetric C/Si) → trivial port. Variable metabolism is
the deferred companion; it was on the table and is recorded here so it stops hiding.

---

## 10. Cross-cutting status notes

- **H1(ii) inversion: DE-EMPHASISED as a build-phase goal.** Per supervisor (2026-06-02): the
  current phase is *build the best C model, slowly and surely; port to Si; then run comparative
  scenarios*. The inversion is a *result the eventual comparative phase may produce*, not a
  thing to protect during the build. Per-stage gates are now (a) **equivalence** (feature-off =
  current model — pure build hygiene) and (b) a **C-model behavioural check** (does the feature
  do what we expect to C; is C viable; are dynamics richer) + (c) a **Si-portability
  architecture note** (toggleable? clean port or needs more general abstraction?). No Si runs,
  no inversion protection, during build.
- **Scenario choice: 2/3** (fixed-menu energy ecology w/ developmental *efficiency* texture).
  Scenario 1 (tech-tree menu expansion) is ⚪ MAYBE/OUT — "cool but TMTS."
- **Compute is not binding** (36.4 ms/step). Keep **grid size fixed** (expensive axis); adding
  resource *types/tiers* on a fixed grid is cheap.

---

## 11. The genuinely NEW mechanics (everything else reuses existing machinery)

Only three things here are net-new code; the rest plugs into trait vector / η / λ / Cred /
joint-tasks / WorldPerturbation that already exist:

1. **Tiered resources with two-mode coordination** (yield-multiplier on foraging; access-gate
   on cultivation).
2. **Per-tier skill via experience, with lossy probabilistic transmission** (+ tier-depletion &
   aging damping).
3. **Heritable resource affinity** (new trait-vector component).

Plus the *re-expression* of existing things on the new substrate: seasonality-as-insolation-
through-chain, game mobility, terrain (+ deferred variable metabolism), two disaster types.

---

## 12. Provisional build-order sketch (NOT yet committed — decide after reading this)

Floor-first logic: skill and affinity are *about* tiers, so tiers must exist first.

```
Terrain (foundation, agent-agnostic)        🟡  [+ variable metabolism? 🔵 decide]
   ↓
Tiered resource substrate                    🟡  [the floor everything stands on]
   ↓
Heritable affinity (cheap, seeds dynamic)    🟡
   ↓
Per-tier experience + lossy transmission     🟡  [heavy; build OWE-13 alongside]
   ↓
Seasonality-as-insolation / game migration   🟡  [needs tiers]
   ↓
Disasters: field-editing, then converter     🟡  [two stages]
```

Open ordering question deferred to post-map decision: are **affinity + experience** one stage
(tightly coupled) or two? And does **terrain** carry variable metabolism or defer it (one-
mechanic-per-stage discipline says defer)?

---

*End of Resource Concept Map v0.1 — reference only, no commitments. 2026-06-02.*
