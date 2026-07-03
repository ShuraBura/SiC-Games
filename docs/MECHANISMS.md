# SiC Games — Mechanisms (MECHANISMS.md)

**The ONE question:** "How does a specific mechanism *work* — the rule, the equation, the range, the inheritance channel, the C/Si classification?" (charter home: MECHANISMS).

**Status:** construct registry, split from `MODEL_SPEC.md` v0.2 on 2026-06-06 (charter §6). This file holds the **per-construct mechanism content**; the architectural principle, design-decisions log, seams, and known-gaps ledger moved to **`ARCHITECTURE.md`**. Section numbers are **inherited verbatim from MODEL_SPEC v0.2** so existing cross-references ("MODEL_SPEC §3", "§5.2", …) still resolve — this file owns §0-classification, §1–§8, §10, §11, and §14 (§9 world-substrate is a pointer stub → `ARCHITECTURE.md` §9, per charter §2.1); ARCHITECTURE owns §0-principle, §9, §12, §13, §15.

**Purpose:** The single authoritative reference for *what each construct in the model is, what real-world dynamic it represents, where it came from in the literature, how SiC departs from that precedent, its support/range, its inheritance channel, and its lock status.* Consult this instead of grepping the stage blueprints. It is an ODD-style construct registry (Grimm et al. 2006/2020).

**Maintainer protocol:** Updated whenever a construct is introduced, redefined, or has its lock status changed. Reviewed at the start of every stage conversation, like `ROADMAP.md`. Where this document and a stage blueprint disagree, **the blueprint is the historical record and this document is the current truth** — reconcile and log the discrepancy in `ARCHITECTURE.md` §15.

**Provenance discipline:** Every factual row carries a provenance tag pointing at the source blueprint + section. Citations are tagged `[VERIFIED]` (present in `LITERATURE.md`), `[INLINE]` (cited in a blueprint but *not* in `LITERATURE.md`), or `[UNVERIFIED]` (Claude believes this is the source but it has not been confirmed against the paper — **must be checked before use in any write-up**).

**Parameter values:** authoritative values + lock/sweep history live in **`docs/PARAMETERS.md`** (extracted 2026-06-08, supersedes all interim tables). This file *references* values; §14 indexes parameter names by owning mechanism section. Do not restate values as facts here.

---

## 0. How to read this registry — the mechanism classification

Every mechanism is classified into one of three categories. **The classification is load-bearing**: misclassifying a mechanism is how the model can end up running correctly and being theoretically wrong. (The *architectural* rationale for this — "one civilizational-mechanics infrastructure, C and Si as parameterised configurations" — and the orthogonal **SEAM** status live in `ARCHITECTURE.md` §0/§13.)

| Category | Meaning | Architectural treatment | Failure mode if misclassified |
|---|---|---|---|
| **C1 — Shared, parameter-differentiated** | One mechanism; C and Si differ only by parameter values (including a parameter set to zero to disable a term). | Build once, expose knobs. | None major — this is the safe default. |
| **C2 — Shared machinery, semantically re-pointed** | Same machinery, but the *signal it reads* or the *meaning of the trait* differs by civilization. | Build once, but the spec **flags in bold** that interpretation/signal-source is civilization-dependent. | Wiring Si's mechanism to C's signal produces a theoretically inverted agent that still runs (e.g. an individualist that likes crowds). **The dangerous category.** |
| **C3 — Genuinely different architecture** | The *locus or shape* of the decision differs (e.g. individual vs. collective decision). | A strategy/coordinator *interface* with distinct implementations — **not** a flag on one implementation. | Forcing a flag-based design onto a C3 mechanism either fails or silently degrades it. Reserved and rare; named explicitly. |

---

## 1. State variables — all of them

### 1.1 Quick-reference table

The trait vector is `H_i = [φ_i, ψ_i, c1_i, c2_i]`. Physical attributes are separate (see §2.2 on the proposed dual-channel split). All trait dimensions are clipped to `[0,1]`.

| Symbol | Name / meaning | Range | Init dist. | Inheritance channel | Horizontal (Deffuant)? | Behavioural hook | Category | Provenance |
|---|---|---|---|---|---|---|---|---|
| φ_i | Status-seeking weight | [0,1] | N(0.5, 0.2²) clipped | Cultural (vertical) | Not currently | Weights status/Cred term in C utility | C1 | Stage 1 (origin); 3.3 §1.1 |
| ψ_i | Sociability / proximity preference | [0,1] | Beta(2,2) clipped (Stage 4.4+); prior: N(0.5, 0.2²) | Cultural (vertical) — *see §2.3, candidate move to physical* | **Yes (C), intentional** — see note | C: proximity-to-*agents* term in movement utility. **Si: proximity-to-good-foraging-spots (different signal) — deferred, inactive** | **C2** | 3.3 §1.1–1.2; Si meaning ROADMAP "Pending — Si" |
| c1_i | Conformism (0) ↔ Individualism (1) | [0,1] | N(0.5, σ_c²) clipped, σ_c=0.2 | Cultural (vertical) | Yes | Scales resistance to Deffuant copying: `mu_eff = mu·(1−c1_i)` | C1 | 3.3 §1.1; 5.2 §3.2 |
| c2_i | Cooperation (0) ↔ Competition (1) | [0,1] | N(0.5, σ_c²) clipped, σ_c=0.2 | Cultural (vertical) | Yes | Defection hook: high-c2 defects from joint task when solo harvest > Matthew share | C1 | 3.3 §1.1; 5.2 §2 |
| 𝒞_i | C Cred (dominance/status) | ≥0 | f_C·mean_cred at birth; 0 at t=0 | Not inherited; accumulated via joint tasks | No | σ_i coupling (§3); utility weight via status amplification | **C2** | Stage 2 §2.1; Stage 3 f_C |
| si_cred_i | Si Cred (reciprocal/near-dormancy) | [0, C*_Si] | 0 at birth | Not inherited; accumulated via near-dormancy band | No | σ_Si_eff modulation; inactive if enabled=False | **C2** | Stage 5 (skeleton); 5.1 §2 |
| m_i | Metabolic rate | {1,2,3,4} | discrete uniform | **None (re-drawn fresh) — proposed change to physical-vertical, see §2.2** | No | Wealth drain per step; survival driver; × β_Si for Si | C1 | Stage 1 §6.3 |
| v_i | Vision | {1,…,6} | discrete uniform | None (re-drawn fresh) | No | Foraging reach (Von Neumann neighbourhood within v_i) | C1 | Stage 1 §6.3 |
| τ_i | Maximum age | {60,…,100} | discrete uniform | None | No | Age-cap mortality | C1 | Stage 1 §6.3 |
| a_i | Age | 0 at birth | N/A | N/A | No | η(a) efficiency ramp; reproduction window | C1 | Stage 1 §6.3; 4.1b §1.2 |
| w_i | Wealth | ≥0 | Uniform[5,25]·k (Stage 4.4+) | None for Si (λ=0); C: + λ·mean-parent-wealth | No | Survival (w>0 required); reproduction threshold | C1 | Stage 1 §6.3 |
| v_i_vel | Wealth velocity | ℝ | 0 at birth | None | No | EMA of Δwealth; modulates C utility via stress-suppression sigmoid | C1 | Stage 2.1 §1 |
| dormant | Dormancy flag | bool | False | N/A | No | Si only: suspends behaviour when wealth < k_dormant × cost_i | C1 (Si only) | Stage 4.3 §1.2 |
| dormant_steps | Steps dormant | int≥0 | 0 | N/A | No | Counts toward T_dormant_max | C1 (Si only) | Stage 4.3 §1.2 |

**World state variables:**

| Symbol | Name / meaning | Range | Provenance |
|---|---|---|---|
| s(x,y,t) | Cell sugar level | [0, c(x,y)] | Stage 1 §6.1 |
| c(x,y) | Cell sugar capacity (static ceiling) | [0, c_max] | Stage 1 §6.1 |
| c_eff(x,y,t) | Effective capacity (seasonal ceiling) | [0, c(x,y)] | Stage 4 §1.1 |

**ψ Deffuant note.** Updating ψ via Deffuant in Stage 5.2 was *deliberate*, not accidental: the Stage 5.2 blueprint (§3.2) states it is "intentional and is the homogenising force tested against in Task 3." The confusion that motivated this document arose not from the bundling itself but from the Stage 5.2 *report* then gating σ_inherit on ψ diversity while ψ was simultaneously subject to that homogenising force. See §3.3 and the design-log entry `ARCHITECTURE.md` §12.1-D.

### 1.2 Narrative — what these variables model and why

*(Pilot §1.2 text preserved verbatim — see §1 of MODEL_SPEC v0.1; expanded in relevant mechanism sections §3–§9 below.)*

**φ, ψ, c1, c2 as a continuous cultural trait vector.** SiC represents civilizational strategy not as a discrete C/Si label but as a continuous, heritable, multi-dimensional disposition. This follows the cultural-evolution tradition of treating culture as a vector of continuous traits transmitted with copy-error, rather than discrete memes. The proximate ABM precedents are Axelrod's (1997) "Dissemination of Culture" (discrete trait features diffusing by local interaction) and the bounded-confidence opinion-dynamics line (Deffuant et al. 2000; Hegselmann & Krause 2002), generalised here to continuous traits on mobile foraging agents. **Departure from precedent:** Axelrod and the opinion-dynamics models are static-lattice or well-mixed; SiC carries the trait vector on *mobile agents in a resource economy*, so trait dynamics couple to foraging success and mortality. Klemm et al. (2003) found noise has a *non-monotonic* effect on cultural diversity; SiC's specific contribution is to ask whether *status-coupled* noise (the C decision-σ mechanism) produces a different functional form than uniform noise. `[INLINE]` Axelrod 1997; Klemm et al. 2003 — cited Stage 1 §1, **not yet in LITERATURE.md**.

**ψ (sociability) is the trait whose mechanical footprint is narrowest and whose interpretation is civilization-dependent — hence its C2 classification.** For C, ψ is the weight on a proximity-to-other-agents term in movement utility (3.3 §1.2): high-ψ C agents prefer cells near other agents. For Si, ROADMAP specifies ψ means "proximity to known-good foraging spots, not proximity to other agents." This is the canonical C2 trap. **Si ψ is currently inactive and must be implemented against the foraging-spot signal, not the agent-count signal, when activated.**

**c1 and c2 carry the actual C-vs-Si theoretical content.** c1 governs resistance to Deffuant copying; c2 governs joint-task defection. Both are inherited and behaviourally coupled to payoff. See §10 (selection) for why these are the traits the selection apparatus targets.

**Physical attributes (m, v, τ, w0) are canonical Sugarscape endowments,** drawn fresh at every birth (Stage 1 §6.3). Deliberate confound-control choice; pending revision under §2.2. `[VERIFIED]` Epstein & Axtell 1996 — Sugarscape substrate documented in LITERATURE.md.

---

## 2. The inheritance model — two channels

### 2.1 Current state (as implemented through Stage 5.2)

*(Pilot §2.1 preserved verbatim.)*

Reproduction produces offspring traits by **biparental averaging plus copy-error** for the cultural vector, and **fresh re-draw** for physical attributes. For each cultural dimension `h ∈ {φ, ψ, c1, c2}` (3.3 §1.3):

```
h_child = clip( (h_A + h_B)/2 + ε_h , 0, 1 ),   ε_h ~ N(0, σ_inherit²),  σ_inherit = 0.10 (locked Stage 5.2)
```

Physical attributes (m, v, τ, w0) are drawn fresh from the canonical distributions for every newborn — **no transmission**. Si uses single-parent near-copy (`h_child = h_parent + ε`) rather than biparental averaging (§7).

### 2.2 Narrative — the cultural/physical dual-inheritance split (PROPOSED)

*(Pilot §2.2 preserved verbatim.)*

The current model labels H_i "cultural traits" and m/v/τ/w0 "biological attributes" but then makes the biological side *inert* (re-drawn, never transmitted). This is the worst of both worlds: it is *described* as a dual-inheritance system but only one channel actually inherits.

**Proposed (supervisor-initiated): make the two channels explicit and parallel.**

- **Cultural channel** — φ, c1, c2 (and Cred-related dispositions). Transmitted vertically (parent→child with copy-error) *and*, for the genuinely cultural traits, horizontally (Deffuant).
- **Physical channel** — metabolism, vision, max-age, and (prospectively) fecundity. Transmitted **vertically only** — there is no horizontal transmission of metabolism.

This is dual inheritance theory done properly. `[UNVERIFIED]` Richerson & Boyd 2005 *Not by Genes Alone* — Claude's attribution; confirm.

**Status: PROPOSED, not implemented.** See design-log `ARCHITECTURE.md` §12.1-A.

### 2.3 ψ's home — cultural or physical channel? (OPEN)

*(Pilot §2.3 preserved verbatim.)*

ψ (sociability) sits awkwardly between the cultural and physical channels. Moving ψ to physical-vertical-only would remove it from the Deffuant contracting force entirely, dissolving the Cell B tension. Status: **OPEN.** See `ARCHITECTURE.md` §15 open decisions.

---

## 3. Decision / σ economy

### 3.1 Mechanism table

| Mechanism | C | Si | Category | Provenance |
|---|---|---|---|---|
| Base noise σ | σ_base = 0.5; coupled to Cred + status | σ_Si = 1.238 (fixed, from Stage 3.4 scan) | **C2** | Stage 2 §2.2; Stage 3.4 |
| σ formula | σ_i = σ_base + κ·tanh(𝒞_i/C*); κ=2.0, C*=10.0 | σ_Si fixed; no Cred coupling | **C2** | Stage 2 §2.2; Stage 3.4 |
| Si Cred modulation | N/A | σ_Si_eff = σ_Si + κ_Si·tanh(si_cred/C*_Si); κ_Si=0.5 | C2 (Si only) | Stage 5.1 §2.2 |
| Status amplification | w_C = φ_i·(1+β·tanh(𝒞_i/C**))·sigmoid(v_i/v_0); β=1.0, C**=C*=10.0 | No status amplification | C1 (β_Si=0) | Stage 3.2 §1.1 |
| Stress suppression | sigmoid(v_i/v_0) in w_C; v_0=1.0 | No stress suppression | C1 | Stage 2.1 §2 |
| Decision rule | Softmax over visible cells with σ_i | Softmax over visible cells with σ_Si_eff | C1 (same rule, different σ) | Stage 2 §2.4; Stage 3 |
| Utility components (C) | U_ij = w_R·ΔR̂_ij + w_C·ΔĈ_ij | Si: U_ij = ΔR̂_ij (resource-only) | **C2** | Stage 2 §2.4; Si design |
| ψ proximity utility | += ψ_i · c_proximity_i (C); C2 for Si | Si ψ inactive | **C2** | Stage 3.3 §1.2; Stage 4.4 |

### 3.2 Narrative

**C decision σ is the project's primary mechanism.** The Cred-coupled σ — `σ_i = σ_base + κ·tanh(𝒞_i/C*)` — is what makes C "status-coupled noise": agents who have accumulated social Cred explore more noisily. This is theoretically the opposite of typical individual-rationality: success raises noise (exploration), not lowers it. The Boltzmann/softmax form is standard in ABM decision models. `[VERIFIED]` Brock & Hommes (1997) — cited in LITERATURE.md (Stage 5 Task 3 section) as precedent for performance-modulated temperature.

**Si σ is fixed by design**, not by laziness. σ_Si=1.238 was locked by a 2D κ×α scan in Stage 3.4, selecting the cell that matches C's mean decision entropy in a static environment — the variance-matching requirement of the project's H1(ii) experimental design. The Stage 3.4 directive explicitly sets σ_Si=1.238. Si Cred (Stage 5.1) adds a *personal* modulation on top of the fixed base: `σ_Si_eff = σ_Si + κ_Si·tanh(si_cred/C*_Si)`, with κ_Si=0.5 (smaller than C's κ=2.0 because Si has no joint-task amplification). `[VERIFIED]` Axelrod 1984 — performance-feedback loop; LITERATURE.md.

**The wealth-velocity stress-suppression term** (Stage 2.1) prevents agents from status-seeking when they cannot afford it: `sigmoid(v_i/v_0)` approaches 0 when recent wealth trend is negative, suppressing Cred-seeking and redirecting agents toward resource foraging. This prevents "mechanically enforced starvation" for high-Cred low-surplus agents (Stage 2.1 North Star). `[INLINE]` no explicit literature citation in Stage 2.1 blueprint.

**C2 classification of σ and utility.** σ is the same softmax machinery for both C and Si, but the *signal driving σ* is entirely different: for C it is dominance Cred from joint tasks; for Si it is near-dormancy reciprocal reputation. The utility function structure is also different (C adds Cred-seeking weight; Si is resource-only). These are not parameter differences — they reflect the civilizational theory. Misclassifying them as C1 would permit wiring Si σ to C's joint-task Cred signal, producing an individualist that values status, which inverts the H1(ii) hypothesis.

---

## 4. Joint task + Matthew partition (C only)

### 4.1 Mechanism table

| Aspect | Value / rule | Category | Provenance |
|---|---|---|---|
| Detection | cell with capacity ≥ θ_c (=4 at k=1; =16 at k=4) AND ≥2 agents within Euclidean distance d=1 | C1 | Stage 2 §2.3 |
| Sugar distribution | Matthew partition: Δ𝒲_i = s(x,y,t) · (𝒞_i+ε)^α / Σ_j(𝒞_j+ε)^α | C1 | Stage 2 §2.3; Stage 3.4 (α) |
| Cred distribution | Same Matthew partition of total Cred bonus (1.0 per participant) | C1 | Stage 2 §2.3 |
| Matthew exponent α | 2.0 (locked Stage 3.4 scan) | C1 | Stage 3.4 |
| Laplace smoothing ε | 0.01 | C1 | Stage 2 §2.3 |
| Cell zeroing | Cell sugar set to 0 after JT payoff | C1 | Stage 2 §2.3 |
| c2 defection hook | When solo_harvest > matthew_share: p_defect_i = c2_i; else 0. Uses agent_rng. | C1 | Stage 5.2 §2 |
| Si joint task | **Not applicable.** Si has no joint task and no JT Cred. | — | ROADMAP C/Si table |

### 4.2 Narrative

**Joint tasks are C-only.** This is a categorical design constraint, not a parameter. Si agents do not participate in joint tasks and do not accumulate Cred through them. The ROADMAP C/Si distinction table is explicit: "C: Cred type = Dominance/status from joint tasks; Si: Cred type = Reciprocal reputation (Stage 5+)." Any code that wires Si to the JT manager's Cred-bonus output is an error.

**The Matthew partition** — `share_i ∝ (𝒞_i + ε)^α` — is a deliberate *super-proportional* reward for already-high-status agents. High-Cred agents receive more of the joint harvest than their numerical share. This is the "Matthew Effect" (cf. Merton 1968 on cumulative advantage in science). `[UNVERIFIED]` Merton (1968) — Claude's attribution; not explicitly cited in Stage 2 blueprint. α=2.0 was locked by the Stage 3.4 2D scan; higher α makes the partition more unequal.

**The c2 defection hook** (Stage 5.2) makes defection possible for the first time: a C agent whose solo harvest would exceed its Matthew share can defect with probability c2_i. This introduces genuine free-riding — previously the model enforced altruism through mandatory participation. The hook uses agent_rng, not env_rng, so seasonal environmental streams are unaffected. `[INLINE]` evolutionary game theory framing — cited in 5.2 North Star, but no specific paper cited; flagged.

---

## 5. Cred — C dominance / Si reciprocal (C2)

**Critical C2 classification: the `cred` / `si_cred` field names are shared, but the accumulation economy is entirely different by civilization.**

### 5.1 C Cred — dominance/status economy

| Aspect | Value / rule | Category | Provenance |
|---|---|---|---|
| Accumulation trigger | Joint-task participation → Matthew-weighted Cred bonus | C only | Stage 2 §2.3 |
| Decay | 𝒞_i(t+1) = (1−δ)·𝒞_i(t) + Δ𝒞_i(t); δ=0.01 | C1 | Stage 2 §2.1 |
| Ceiling | C* = 10.0 (C** = C* pinned, deferred Q11) | C1 | Stage 2 §2.2 |
| Newborn endowment | f_C · mean_cred_C at birth (f_C=0.25 locked Stage 3.1) | C1 | Stage 3 §1.3 |
| Pool contribution scaling | contribution_C = τ_pool · surplus_i · (1 + τ_cred·tanh(𝒞_i/C*)) | C only | Stage 4.1c §1.2 |
| Pool contribution reward | Δ𝒞_i^pool = τ_cred_reward · (above-base contribution) | C only | Stage 4.1c §1.2 |
| Birth modulation (γ) | P_birth × (1 + γ·tanh(𝒞_i/C***)); γ=0.2, C***=C*=10.0 | C only | Stage 4.2; Stage 4.1a |
| σ coupling | σ_i = σ_base + κ·tanh(𝒞_i/C*); κ=2.0 | C only | Stage 2 §2.2 |
| BUG-003 (fixed) | cred_pool_contribution was 0.0 in all Stage 4.1c runs (wrong attribute lookup). Fixed Stage 4.2. | — | ROADMAP BUG-003 |

### 5.2 Si Cred — near-dormancy reciprocal economy

*(Stage 5.1 redesign — accumulation replaced the Stage 5 surplus-based rule.)*

| Aspect | Value / rule | Category | Provenance |
|---|---|---|---|
| Accumulation trigger | Near-dormancy band: Δsi_cred = 1 if w_lo ≤ w_i < w_hi, else 0; where w_lo = k_dormant·cost_i, w_hi = (k_dormant+k_cred_band)·cost_i | Si only | Stage 5.1 §2.2 |
| Accumulation (retired) | Stage 5 surplus-based: Δsi_cred = max(0, harvest−cost)×r_cred_Si — retired as pro-cyclical | RETIRED | Stage 5.1 §0 |
| Decay | si_cred(t) = clamp(si_cred(t−1)·(1−δ) + Δsi_cred(t), 0, C*_Si); δ=0.01 | C1 | Stage 5.1 §2.2 |
| Ceiling | C*_Si = 10.0 | C1 | Stage 5 Task 3 |
| σ modulation | σ_Si_eff = σ_Si + κ_Si·tanh(si_cred/C*_Si); κ_Si=0.5 | Si only | Stage 5 Task 3; 5.1 |
| Band width | k_cred_band = 1.0 (locked Stage 5.1 after counter-cyclicality gate passed both seeds) | Si only | Stage 5.1 §2.2 |
| Newborn Cred | 0 at birth (Si Cred economy separate from C newborn endowment) | C1 (0) | ROADMAP C/Si table |

### 5.3 Narrative

**C Cred is dominance/joint-task capital; Si Cred is near-dormancy survival reputation.** The same state field (`cred` / `si_cred`) has completely different meaning and accumulation paths. C Cred amplifies with success (Matthew partition rewards already-rich in Cred); Si Cred accumulates *under stress* (only near-dormancy active agents earn it). This counter-cyclical design means Si Cred rises during resource troughs, elevating σ_Si_eff exactly when exploration matters most — the correction the Stage 5.1 redesign was built to deliver (Stage 5.1 §0 North Star). `[VERIFIED]` Axelrod 1984 and Brock & Hommes 1997 — Si Cred self-referential performance loop; LITERATURE.md.

**BUG-003 history.** In all Stage 4.1c data, cred_pool_contribution was 0.0 because `agent._cred_scale` did not exist on BaseAgent (always missing → tanh=0 → zero above-base Cred contribution). Fixed Stage 4.2. All Stage 4.1c cred-scaled pool metrics are invalid.

---

## 6. Support pool — L1 (parental), L2 (proximity), L3 (status-mediated)

### 6.1 Mechanism table

| Level | Description | C | Si | Category | Provenance |
|---|---|---|---|---|---|
| L1 Parental transfer | At birth: offspring += τ_parent · mean(w_A,w_B) | τ_parent=0.0 | τ_parent=0.0 | C1 | Stage 4.1c §1.1 |
| L2 Proximity pool contribution | Active adults contribute τ_pool·surplus to local pool | τ_pool=0.05 (locked Stage 4.2) | τ_pool_si=0.05 (flat, no Cred scaling) | **C2** (Cred-scaled vs flat) | Stage 4.1c §1.2; Stage 4.2 |
| L2 Pool draw | Non-active agents draw up to k_draw=3 steps of metabolism from pool | Same | Same (dormant_can_draw=False by default) | C1 | Stage 4.1c §1.2 |
| L3 Status contribution | C: contribution += τ_cred·tanh(𝒞/C*) · surplus (high-Cred contributes more) | Enabled (τ_cred=0.5) | **NOT IMPLEMENTED — Si has no status component** | **C2** | Stage 4.1c §1.3; ROADMAP C/Si table |
| L3 Contribution reward | C: Δ𝒞_pool for above-base contribution (τ_cred_reward=0.1) | Enabled | Not applicable | C only | Stage 4.1c §1.2 |
| Pool carry-over ρ | pool_{t+1} = ρ·leftover_t + contributions_{t+1}; ρ=0.3 (locked Stage 4.3) | Same | Same | C1 | Stage 4.3 §1.3 |
| Pool cap k_pool_cap | cap = k_pool_cap·N_active·mean_metabolism; 0=no cap | k_pool_cap=0.0 (Stage 5+) | Same | C1 | Stage 4.3 §1.3 |
| Pool radius | r_pool=5 (Chebyshev neighbourhood) | Same | Same | C1 | Stage 4.1c §1.2 |

### 6.2 Narrative

**C is L1+L2+L3; Si is L1+L2 only.** This is a categorical constraint from the C/Si distinction table. Si has no status component — contributions are flat τ_pool, not Cred-scaled. ROADMAP: "Si support structure: Self + proximity pool only (L1+L2). No status component."

**Pool carry-over (ρ=0.3)** was added in Stage 4.3 as a "granary mechanism" to buffer multi-step troughs. The intended effect was to shift T* (critical period) upward; the observed effect was the opposite — T* narrowed from (100,200) to (100,112) due to higher baseline C stress (ROADMAP note on ρ_carryover). This is a design tension: the pool simultaneously sets N-equilibrium and buffers C against environmental stress, and ρ tightened rather than relaxed the constraint.

**τ_pool design tension** (ROADMAP §Q22, partially resolved Stage 4.2): τ_pool is entangled with N-equilibrium (dual role: pool buffer + N suppressor). At τ_pool=0.10, established starvation fails; at 0.05, N equilibrium changes. Full resolution deferred; current lock τ_pool=0.05 is an acknowledged compromise.

---

## 7. Reproduction + demography

*(Pilot §3 — C biparental, Si fission, coordinator seam — preserved verbatim below; extended with birth-death and carrying-cost machinery.)*

### 7.1 Mechanism table

| Aspect | C | Si | Category | Provenance |
|---|---|---|---|---|
| Population mode | Dynamic (Stage 4.1a+); legacy mode=fixed preserved | Dynamic | C1 | Stage 4.1a §1.1 |
| Birth trigger (C) | Wealth-dependent DTM: P_birth(w_i) within age window | — | C1 | Stage 4.1a §1.2 |
| Birth trigger (Si) | — | Fission: w_i ≥ θ_fission → P_fission_max | C1 | Stage 4.1a §1.3 |
| Carrying-cost ceiling | P_eff = p_max·DTM·carry_discount(N_C); carry_discount = max(0, 1−α_carry·N_C/N_carry) | **C only** | C1 (C only) | Stage 4.5 §1.2 |
| Cred-modulated birth (γ) | P_birth × (1 + γ·tanh(𝒞_i/C***)); γ=0.2 | **None** | C1 (γ_Si=0) | Stage 4.2 |
| Age-efficiency ramp η(a) | η_min=0.3 at birth, linear to 1.0 at a_forage_min=15, decline to η_old=0.4 at τ_max | **Si: η=1.0 always** (fission offspring start capable) | C1 | Stage 4.1b §1.2; Stage 4.3 |
| Biparental / fission | Biparental (r=3); h_child = clip(mean(h_A,h_B)+ε, 0,1) | Single-parent near-copy | **C1** (mixing rule parameter) | Stage 3.3; 4.1a §1.2 |
| σ_inherit | 0.10 (locked Stage 5.2; raised from 0.05) | Same per-dimension noise | C1 | Stage 3.3; Stage 5.2 Task 3 |
| Wealth inheritance λ | w_child += λ·mean-parent-wealth; λ=0.1 (C only) | λ=0 (Si wealth is earned) | C1 | Stage 4.4; ROADMAP C/Si table |
| Newborn Cred (C) | f_C·mean_cred_C; f_C=0.25 (locked Stage 3.1) | 0 | C1 | Stage 3 |
| Coordinator | individual; hivemind = **SEAM** (Si only, NotImplementedError) | individual | **C3 seam** | Stage 4.1a §1.4; `ARCHITECTURE.md` §13 |

### 7.2 Narrative (pilot §3.1–§3.2 preserved; extended)

*(Pilot §3.2 preserved verbatim:)*

The C-vs-Si reproduction difference is **mostly C1**: same machinery with different parameter values for parent-count (2 vs 1), mixing rule (average vs near-copy), Cred-modulation strength (γ vs 0), and wealth inheritance (λ vs 0). **`NEVER biparental for Si`** — BUG-002 (Stage 3.3) was caused by a non-C/Si-aware coordinator, "cost a stage." The cliodynamics note: the Cred-modulated C birth term is a deliberate Turchin elite-overproduction mechanism. `[INLINE]` Turchin 2003 — cited ROADMAP + 4.1a, not in LITERATURE.md.

**Carrying-cost ceiling (Stage 4.5, C only):** at k=4, grid resources are abundant enough that C's DTM birth formula produces births faster than senescence can remove agents, driving N to ~1500 (Stage 4.4 Diagnostic). The density-dependent discount `carry_discount(N_C) = max(0, 1−N_C/N_carry)` creates a stable equilibrium at N_carry=400. This is grounded in biological carrying-capacity theory — resource competition and crowding suppress reproduction as density rises. `[INLINE]` no specific paper cited in Stage 4.5 blueprint; rationale from blueprint §1.1.

**Age-efficiency ramp η(a)** (Stage 4.1b, C only from Stage 4.3): juvenile agents at age<15 harvest at η_min=0.3, linearly rising to 1.0 at a_forage_min=15; elder agents decline from 1.0 at a_forage_max toward η_old=0.4 at τ_max. Si fission offspring start at η=1.0 (fully capable — fission produces a near-copy of an established adult). `[INLINE]` Gurven & Kaplan 2006 — cited Stage 4.1b §1.2, not in LITERATURE.md.

**σ_inherit (PARAMETERS.md §7, LOCKED at 0.10).** The Stage 5.2 Task 3 gate used Gini(ψ) — the wrong statistic (use SD) and the wrong target trait (c1/c2 carry the theory, not ψ). This is a known methodology problem recorded in `ARCHITECTURE.md` §12.1-D and OWE-9; the corrective sweep (targeting c1/c2 diversity, ≥8 seeds) is on the backlog. However the LOCKED status stands — PARAMETERS.md is authoritative, and the corrective sweep is how the value is *confirmed or revised*, not a reason to treat it as unlocked. See `ARCHITECTURE.md` §12.1-D for the full design-log entry.

---

## 8. Shocks / perturbations

### 8.1 Mechanism table

| Aspect | Value / rule | Category | Provenance |
|---|---|---|---|
| Protocol | WorldPerturbation interface; applied once per step before JT detection | C1 | Stage 4 §1.1 |
| NullPerturbation | No-op; recovers Stage 1–3 behaviour | C1 | Stage 4 §1.1 |
| SeasonalOscillation | c_eff(x,y,t) = c(x,y)·(1 − A·sin²(π·t/T)) | C1 | Stage 4 §1.1 |
| Amplitude A | Locked at {0.5, 0.75} for main sweep; 0.9 in Stage 5 ensemble | C1 | ROADMAP Stage 4.2, Stage 5 |
| Period T | {50, 100, 200} sweep (Stage 4.2); T* search (Stage 4.5, Stage 5) | C1 | ROADMAP |
| Trough fraction | Default 0.5 (symmetric sin²); asymmetric variant implemented Stage 4.5 | C1 | Stage 4.5 blueprint |
| effective_capacity field | Per-cell seasonal ceiling; shed_excess_sugar() clips current sugar when capacity drops | C1 | Stage 4 §1.1 |

### 8.2 Narrative

**The WorldPerturbation protocol** is the clean architecture hook planned in Stage 1 §5.3. It modifies `effective_capacity` (not `max_capacity`) in-place each step. The growback rule `G_α` then grows sugar up to `effective_capacity`, not `max_capacity` — a one-line change from Stage 1's behaviour.

**Critical period T\* analysis:** the main scientific outcome of Stages 4.2–4.5 is the T* bracketing — the period at which C transitions from survival to collapse (T* > 500 for C at A=0.75) and Si collapses earlier (T*_Si ∈ (68,87) at A=0.75, Stage 5). H1(ii) inversion finding: C survives where Si collapses, at high-amplitude long-period shocks.

---

## 9a. kcal economy (Phase 1 Blueprint A, 2026-06-14)

**Supersedes the Sugarscape sugar economy for C agents.** See ARCHITECTURE.md §12.1-L for the dated decision-log entry and PARAMETERS.md §13 for all tagged values. Summary here; authoritative values in PARAMETERS.md.

### 9a.1 Per-month conversion (LOCKED: 1 step = 1 month)

| Quantity | Conversion | Result | Tag |
|---|---|---|---|
| Burn per step | 2,500 kcal/day × 30 days | 75,000 kcal/step | [NOMINAL] |
| Intake per step | rate_kcal/hr × 6 hr/day × 30 days | rate × 180 kcal/step | [NOMINAL, 6 hrs/day] |
| Lifespan | 60–100 years × 12 months/year | 720–1,200 steps; placeholder 900 | [PLACEHOLDER] |

Temporal resolution `1 step = 1 month` is a STANDING CONSTRAINT (ARCH §9.3 OWE-1). All kcal quantities must be expressed per-step for integration.

### 9a.2 Reserve integration

```
reserve_t+1 = min(reserve_t + intake_t, reserve_full)  − burn_per_step
death:  reserve ≤ reserve_floor   (reserve_floor = 20,000 kcal [PLACEHOLDER MR-1])
```

- `reserve_full = 100,000 kcal` [PLACEHOLDER MR-1] — physiological estimate; see PARAMETERS.md §13.2
- `reserve_floor = 20,000 kcal` [PLACEHOLDER MR-1] — starvation floor estimate
- `reserve_floor` attribute on `BaseAgent`; default 0.0 (backward-compatible for Sugarscape runs)

### 9a.3 Sex-based stream selection (A2.2, C only)

**Category: C1** (shared machinery, sex as a parameter-like switch).

| Sex | Default stream | Switch condition | Switch target |
|---|---|---|---|
| Female | Forage (forage_kcal) | forage_rate_step < burn AND game_rate_step > forage_rate_step | Game (if covers deficit better) |
| Male | Game (game_kcal) | game_rate_step < burn AND forage_rate_step > game_rate_step | Forage (if covers deficit better) |
| Either | Default | Both streams < burn AND neither covers better than other | Hold default; fall to floor; mortality handles it |

No new tunable threshold beyond the A-1 placeholders. Risk-sensitivity (variance-reduction) deferred to RS-1 (DEFERRED_MECHANICS.md).

### 9a.4 Three seams

| Seam ID | What is deferred | Hook | Status |
|---|---|---|---|
| GD-1 | Game depletion | `game_kcal` per-cell field (read-only → writeable stock + regrowth) | Depletion OFF; field exposed. DEFERRED_MECHANICS.md. |
| CC-1 | Non-rivalrous cap; kcal ceiling re-derivation | `terrain_field.py harvest()/game_level()` returns full per-agent rate; rivalry switches on here | Rivalry OFF [PROVISIONAL]. DEFERRED_MECHANICS.md. |
| JV-1 | Age-graded juvenile curve | `is_juvenile()` hook in step loop; binary gate now | Binary gate (0 below a_forage_min=15; full above). DEFERRED_MECHANICS.md. |

### 9a.5 forage_kcal and game_kcal computation (terrain.py)

Each biome's cell values are drawn from a **literature-anchored distribution** with a per-biome `(mean, std)`. Two regimes, by whether the std is anchored:

**(a) std anchored in literature → terrain-coupled lognormal (the §9a.6 mechanic).**
**(b) std not yet anchored (`None`) → legacy mean-only scaling** (fallback): `field_kcal[mask] = field[mask] × (mean / mean_norm(field[mask]))` — spread is whatever the terrain field gives, tagged PENDING-std.

Biomes NOT in the target dict (water; wetland/mountain for game) stay at 0. All cell values PROVISIONAL pending CC-1. Means/stds: PARAMETERS.md §12.4 (forage) and §13.3 (game); derivations: `SiC_Games_Resource_Return_Rate_Table.md §3.2`.

### 9a.6 Terrain-coupled lognormal cell-value draw (2026-06-15)

**Category: shared world machinery (C and Si read the same fields).** Supervisor-directed 2026-06-15. Replaces single-point biome values with a draw from a literature-anchored **lognormal**, while preserving the terrain field's spatial structure.

**Mechanic** (`terrain.py:_lognormal_rescale`, deterministic — no RNG):
1. Within a biome, rank the cells by their normalized terrain field value (`forage`/`game`); convert ranks to Hazen quantiles `q = (rank + 0.5)/n ∈ (0,1)`.
2. Lognormal params from the literature `(mean, std)`: `σ² = ln(1 + (std/mean)²)`, `μ = ln(mean) − σ²/2`.
3. `value = exp(μ + σ · Φ⁻¹(q))`, then re-normalised so the realised biome mean equals `mean` exactly.

**Properties:** positive-only (no negative kcal); right-skewed (matches foraging-return data, e.g. the bustard tail); realised biome mean exact, std within ~1% of target; **terrain coupling preserved** (high-terrain-field cells get high values — "game peaks in forest" survives); **deterministic / reproducible** (same `(knobs, seedStr)` → byte-identical field), so the equivalence-gate discipline is intact.

**Distribution-family choice = lognormal; spatial choice = terrain-coupled rescale** (supervisor, 2026-06-15) — see ARCHITECTURE.md §12.1-N.

**Std sourcing rule (supervisor, 2026-06-15):** each biome's std is mined from the literature where the source reports a spread/SD/range; **where the literature std is unavailable, std = 10% of the mean** (`DEFAULT_STD_FRAC = 0.10`). So **every** biome uses the lognormal draw — none fall back to mean-only scaling. Literature-anchored stds: game forest (4,043), game desert (210), forage forest (600), forage desert (368); all other biomes use the 10% default. See PARAMETERS.md §12.4 / §13.3 for the per-biome tag ([LIT] vs [10%-DEFAULT]).

## 9. World / resource substrate → see `ARCHITECTURE.md` §9

*(Per charter §2.1 the world/resource substrate is the "how the world works" half and lives in **`ARCHITECTURE.md` §9**: grid, twin peaks, capacity function, growback G_α, k_grid rescale (§9.1–9.2), and the OWE-1 / OWE-1.1 / R0 physical-unit calibration (§9.3). Pointer kept here so the cross-references from §1.2, §3, etc. still resolve.)*

---

## 10. Selection measurement (forward note — not yet implemented)

*(Pilot §4 preserved verbatim.)*

**The traits worth measuring selection on are c1 and c2, not ψ** — because selection-relevance requires a trait that is *both* (i) inherited *and* (ii) behaviourally coupled to payoff. Metabolism fails (i) (re-drawn). ψ nearly fails (ii) (payoff coupling is a weak spatial side-effect). c1 and c2 pass both. The Stage 5.2 report already provides a null result that, read correctly, *is* a selection measurement: defection_rate 3.7% with defector-c2 ≈ cooperator-c2 is a **near-zero Cov(c2, defection)** — no detectable selection differential on c2 under current conditions.

**Intended apparatus (for a future directive):** the Price-equation decomposition (Price 1970, 1972; operationalised per Frank 1995/1997/2012) splitting Δ(mean trait) into a *selection* term `Cov(w, z)/w̄` and a *transmission* term `E[w·Δz]/w̄`. The split is especially informative here because Deffuant is a *transmission* force, not a selection force. `[UNVERIFIED]` Price 1970/1972, Frank 1995/1997/2012 — Claude's attribution; confirm before any write-up. **Gate vs. measurement:** a dispersion floor (SD of the bounded trait, *not* Gini) is the cheap go/no-go; the covariance is the scientific quantity.

---

## 11. Metrics & diagnostics

### 11.1 Per-step metrics (key subset)

| Metric | Description | When non-zero/valid | Provenance |
|---|---|---|---|
| population | Total living agents | Always | Stage 1 |
| n_active_si | Active (non-dormant) Si agents | Si runs with dormancy | Stage 4.3 |
| dormancy_rate | n_dormant_si / (n_active_si + n_dormant_si) | Si dormancy enabled | Stage 4.3 |
| permanent_dormancy_deaths | Si agents exceeding T_dormant_max | Si dormancy enabled | Stage 4.3 |
| mean_wealth, gini_wealth | Wealth distribution | Always | Stage 1 |
| mean_cred, gini_cred | C Cred distribution | C runs | Stage 2 |
| defection_rate | defections / total JT opportunities | c2_defection.enabled=True | Stage 5.2 |
| si_cred_mean, si_cred_gini, sigma_si_eff_mean | Si Cred diagnostics | Si + si_cred.enabled=True | Stage 5/5.1 |
| frac_in_band | Fraction of active Si agents in near-dormancy band at Phase 1b | Si + si_cred.enabled=True | Stage 5.1 |
| c1_mean/std/gini, c2_mean/std/gini, psi_mean/std | Cultural trait distributions | C runs | Stage 5.2 |
| deffuant_updates_per_step | Fraction of C agents updating a trait each step | deffuant.enabled=True | Stage 5.2 |
| season_phase | t mod T / T | Always | Stage 4.2 |
| pool_draw_unmet_frac | Unmet pool draw requests / total draw requests | Pool enabled | Stage 4.1c |
| carry_discount_mean | Mean carry_discount(N_C) applied to C births | Carrying-cost enabled | Stage 4.5 |

### 11.2 R6 terminal-state summary (per-run, Stage 5.2+)

Per-run fields emitted by `compute_run_summary(df, strategy)`:

| Field | Description |
|---|---|
| extinction_step | Step of first zero-population event; None if population survived |
| N_min | Minimum population over the run |
| argmin_t | Step at which N_min occurred |
| N_active_t_end | Population at the final recorded step |
| n_steps | Total recorded steps |

### 11.3 Standing report standards (R1–R7, CLAUDE.md §7–8)

- **R1** Terminal-state row mandatory in every results table.
- **R2** One-sentence narrative on population stability effect.
- **R3** Magnitudes of trait Gini change (direction + speed).
- **R4** Anomalies & open questions section mandatory.
- **R5** Synthesis ≥150 words: claim + evidence for + against + confidence.
- **R6** Terminal-state fields emitted.
- **R7** HTML reports, base64-embedded figures, self-contained (Stage 4.4+).

Pool gate criterion (ROADMAP Rule 12): `pool_draw_unmet_frac < 20%` evaluated as the **time-mean over t≥500**, not instantaneous peaks. Mean-based gate only.

**Dispersion statistic note (`ARCHITECTURE.md` §12.1-D, §15.4):** for bounded [0,1] traits initialised at mean 0.5 / SD 0.2, **use SD, not Gini**. Gini is mean-sensitive and ill-behaved near a point mass. A collapse to SD < ~0.05 (from SD₀=0.2) is the meaningful homogenisation signal.

---

## 16. Carbon status & social-structure mechanisms (R-18…R-27; added 2026-06-29)

Registry of the Carbon-status + bands/family/society constructs. **The rule/math/lit for each lives in
MODEL_SPEC §4.5–§4.8 (methods home) — referenced here, not restated** (charter §2 "pointers, not copies").
Values: PARAMETERS §17–18. Impl: `sic_games/src/sic_games/{phase1_model,demography,substrate,group,capacity}.py`.
Category: C1 (shared, param-differentiated) / C2 (re-pointed) / C3 (new architecture).

| Mechanism | What it is | Cat | Impl pointer | Ref |
|---|---|---|---|---|
| CC-1 capacity field | NPP→density carrying capacity (the substrate bands/demography run on; NOT bare forage) | C1 | `capacity.py::NPPCapacityField` | §4.3.1/§4.8.4; R-22 |
| Cred-vector + prowess | ascribed lineage `cred` × achieved `prowess` (decaying EMA of relative meat) Cobb–Douglas status | C1 | `substrate.py::base_status` | §4.5.6–7; R-18 |
| Paternity / mate-choice | father by prowess-weighted choice; bilateral lineage blend + mean-reversion homeostat | C2 | `phase1_model::_do_births_ibi` | §4.5.7; R-19/R-21 |
| Storage + per-cell/per-band morph | collective granary (Binford ET) + cred-weighted draw (Hayden); society egal→complex→stratified | C3 | `phase1_model::_step_rivalrous` | §4.5.11/§4.8.9; R-23 |
| Emergent-band grouping drives | E.1 safety + E.2 mating multipliers in the diffusion movement utility | C1 | `substrate.py::diffusion_select_target` | §4.8.1 |
| Bonded mate-gate (F.1/F.2) | a birth needs an unrelated adult male within the band (Chebyshev `bonded_mate_radius`) | C3 | `phase1_model::_do_births_ibi` | §4.8.4; R-22 |
| Band life-cycle diagnostic | bands = connected components; merge/split/collapse + persistence filter | C3 (obs) | `phase1_model::bands` | §4.8.6; R-24 |
| Persistent families (F.3a/b) | durable monogamous pair-bond (`_partner`/`_wives`) + nuclear-family co-movement; detach at maturity | C3 | `phase1_model::_do_pairing,_family_head` | §4.8.7; R-25 |
| Modest polygyny | high-status males take ≤`max_wives` wives (von Rueden status→RS amplifier) | C1 | `phase1_model::_do_pairing` | §4.8.12; R-26 |
| Collective-identity vector | per-agent `GroupVector` (band_id active; assabiyah/religion seams) — the Carbon "hive-mind" | C3 | `group.py::GroupVector` | §4.8.8; R-25 |
| Band affiliation + fission/fusion | persistent band_id + exogamy + cohesion drive + hysteretic split/merge → ~25 non-kin bands | C3 | `phase1_model::_maintain_bands` | §4.8.8 |
| Per-band society + family knobs | morph attaches to band_id; reproduction reads band-society knobs (additive-delta-from-egalitarian) | C2 | `phase1_model::_band_knob` | §4.8.9/§4.8.11 |
| Assabiyah (dynamic bands) | per-band solidarity from surplus → condition-dependent `tolerable_size` (Ibn Khaldun) | C3 | `phase1_model::_maintain_bands` | §4.8.10; R-25 |
| Climate integration | run the social stack on a `ClimateField`-modulated capacity (seasonal/ENSO/regime drive surplus/adversity) | C1 | `climate.py::ClimateField` | §4.1.9/§4.8 Stage 0; R-27 |
| Controlled-climate driver (harness) | deterministic `t→[0,1]` regime waveform (flat/step/pulse/ramp/square/piecewise) overriding the telegraph for clean diff-in-diff social benchmarks | C1 (tool) | `climate.py::ClimateDriver`; `run_se0_controlled_climate.py` | §4.1.9; R-28 |
| Leader coherence (Stage 1a) | 2nd cohesion source from a band's top-status member, Boehm-gated (egal 0 / complex 0.5 / stratified 1.0); read fresh each step | C1 | `phase1_model::_maintain_bands`; `demography::leader_society_weight`, `band_leaders()` | §4.8.13; R-30 (benchmark deferred) |
| Size repulsion (Stage 1b) | Johnson scalar-stress DISPERSIVE term (logistic in band size, Alberti shape), hierarchy-relieved; resource-independent counterweight to cohesion | C1 | `demography::size_repulsion`; `phase1_model::_maintain_bands` | §4.8.13; R-29/R-31 |
| Malnutrition fission (M2) | realized-starvation dispersive term → large bands break up; dispersal substitutes for death; size-gated by base floor | C1 | `phase1_model::_maintain_bands`, `_note_band_starv` (`_band_starv_ema`) | §4.8.14; R-32/R-33 |
| Resource-directed fusion (F) | a sub-merge band joins the RICHEST nearby band (not nearest) — remnants merge into provisioned bands | C1 | `phase1_model::_maintain_bands` | §4.8.14; R-33 |
| Genealogy logger (Stage 2) | pure-observer append-only birth/death log (uid, mother, father, lineage, band_id, step, cred); Stage-3 substrate | C1 (tool) | `phase1_model::_log_genea`, `dump_genealogy` | §4.8.15 |
| CC-1 Tallavaara capacity | NPP→density via the fitted segmented regression (mode='tallavaara'); ~57% of provisional; world-lottery diverse worlds | C1 | `capacity.py::density_tallavaara`, `NPPCapacityField(mode=…)`; `terrain.py::world_lottery` | §4.3.1; R-36 |
| Ascribed(cred) mate-choice | female mate-weight `(prowess·cred^(a·sw))^m`, society-gated `sw` (egal 0.25/complex 0.6/strat 1.0); recovers composite status→RS ≈0.13 at a=2.5 | C2 | `demography::mate_ascribed_weight`, `MATE_ASCRIBED_WEIGHT`; `phase1_model::_pair_from_pool` | §4.8.16; R-35 |
| Life-history wiring (canonical) | Kaplan-2000 graded η/consumption/reserve + provisioning now ENGAGED (`enable_life_history` auto-builds month-scaled cfg); retires JV-1 | C1 | `agents/base.py::eta/consumption_factor/reserve_scale`; `phase1_model::_init_agents` | §4.8.17; R-38 |
| The gathering (marriage aggregation) | seasonal cross-band exogamous pairing at abundant sites; residence (viri/uxori/flexible) + rank-homogamy toggles; decouples mate-finding from reproducing | C2 | `phase1_model::_do_gathering`, `_pair_from_pool` | §4.8.18; R-39 |
| Productivity-scaled mobility | diffusion STRIDE scales ∝1/static-local-NPP (Kelly/Binford); water-aware glide; low-NPP agents spread instead of piling → fixes the biome→society collapse root | C1 | `demography::mobility_radius`; `substrate::diffusion_select_target(move_radius,water)` | §4.8.19; R-39 |

> **SHELVED:** `enable_band_risk` (F.2 risk-dilution-as-mortality — death spiral, DE-4). **RETIRED:**
> `storage_tether_reserves` (DE-3); `season_aggregation` (DE-7, lean→fission mis-signed+inert); M1 moderate-lean
> aggregation (DE-8, never built — no food-wise payoff). Shelved/retired items default-OFF or removed.

## 16b. Band-size driver taxonomy — the cohesion ↔ dispersion balance (design reference, 2026-07-01)

The definitive "what sets band size" map, from the fission-driver review (R-31). Band size is governed by THREE
channels — **movement/spatial** sets the *central* size (~20–25, the binding one), the **fission threshold**
(`tolerable_size = base + (cap−base)·clamp(cohesion − dispersion)`) is a *tail/stress valve* (dormant in normal
times, R-31), and **mortality** is the failure mode. Each driver enters ONE channel; the resource response is
**non-monotonic** (moderate lean → carry on / aggregate at concentrated resources via movement; severe scarcity →
disperse; catastrophe → die). `⟳` = fires per step; `△` = stress/tail only.

**COHESION (raise tolerable / hold together):**
| Driver | Signal | Rationale | Lit | Channel | Status |
|---|---|---|---|---|---|
| Assabiyah | accumulated stored surplus | success → durable solidarity | Ibn Khaldun; Turchin 2003 | threshold △ | ✅ |
| Leader coherence | top-status member | organizational/charismatic pull; Boehm-gated | Hooper/Kaplan/Boone 2010; Boehm 1999 | threshold △ | ✅ (benchmark deferred, R-30) |
| Selfish-herd safety | predation/raid risk | risk dilution in a group | Hamilton 1971 | movement ⟳ | ✅ |
| Cooperative production | big-game / labour division | group needed for returns (~7 hunters) | Janssen & Hill 2014; Layton 2012 | economy | ◐ |
| Mating-pool viability | band < ~25 | stay aggregated to find mates | Wobst 1974; Birdsell 1953 | births (mate-gate) | ✅ |
| ~~Risk-pool aggregation (M1)~~ | moderate lean | (no food-wise payoff — already in meat-sharing) | Cashdan 1985; Wiessner 1982 | — | ❌ DROPPED (DE-8) |

**DISPERSION / FISSION (lower tolerable / split):**
| Driver | Signal | Rationale | Lit | Channel | Status |
|---|---|---|---|---|---|
| Size repulsion | band size N | Johnson scalar stress; hierarchy-relieved | Johnson 1982; Alberti 2014 | threshold △ | ✅ |
| Malnutrition fission (M2) | realized starvation (`_band_starv_ema`) | large band can't feed N → disperse (subsumes death) | Colson 1979 (filed); Kelly 1995; Layton 2012 | threshold △ | ✅ |
| IFD / local depletion | thin/depleted cell yield | spread to cover ground | Fretwell & Lucas 1970; Charnov 1976 | movement ⟳ | ✅ |
| Starvation mortality | absolute food deficit | dispersal failed → death culls | Siler; density-disease | mortality | ✅ |
| ~~Seasonal lean → fission~~ | annual lean | (mis-signed + inert) | — | — | ❌ RETIRED (DE-7) |

**FUSION (re-absorb small bands):** nearest-neighbour join → **F resource-directed** (join the richest nearby
band; Wiessner hxaro).

## 14. Parameter registry (pointer)

**Authoritative parameter values + lock/sweep history: `docs/PARAMETERS.md`** (extracted 2026-06-08, charter §6 — supersedes the former interim table in `sic_games/CLAUDE.md`). Do NOT copy parameter values into this section; that would create two-homes drift.

**Index of parameter names by owning mechanism section:**

| Section | Parameters |
|---|---|
| §3 Decision/σ | σ_base, κ, C*, C**, σ_Si, v_tau, v_0, β (status amplification), κ_Si, C*_Si |
| §4 Joint task | d, θ_c, α (Matthew), ε (Laplace), c2_defection.enabled |
| §5 Cred | δ (decay), f_C, τ_cred, τ_cred_reward, γ (birth modulation), C***, k_cred_band |
| §6 Pool | τ_parent, τ_pool, k_reserve, k_draw, τ_cred, τ_cred_reward, ρ (carryover), k_pool_cap, r_pool |
| §7 Reproduction | P_max_C, P_max_C_bare, P_max_C_final, P_fission_Si, σ_inherit, λ (wealth), f_C, η_min, η_old, a_forage_min, N_carry, α_carry, γ |
| §8 Shocks | A, T, trough_fraction |
| §9 World | k_grid, c_max, k (band_width), α (growback), peaks |
| §5.2 Si Cred | k_cred_band, κ_Si, C*_Si, δ, k_dormant, τ_trickle, k_reactivate, T_dormant_max |
| §3.2 Deffuant | epsilon, mu, update_every, traits, cred_weight |

---

*End of MECHANISMS.md — split from MODEL_SPEC v0.2 on 2026-06-06. The world/resource substrate (§9), architecture principle, decision-log, seams, and known-gaps ledger are in `ARCHITECTURE.md`.*
