# SiC Games — Stage 3.3 Blueprint: Trait Vector H_i and Biparental Reproduction

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 3.3 only. All prior stages locked — do not refactor them.
**Prerequisite:** Stage 3.2 complete. Confirmed parameters: β=1.0, f_C=0.25, κ=2.0, σ_Si=1.051.

---

## 0. North Star (read first, every session)

**Stage 3.3 goal:** introduce the trait vector H_i = [φ_i, ψ_i, c1_i, c2_i] and
biparental reproduction. φ_i already exists — Stage 3.3 adds ψ_i (sociability),
c1_i (conformism ↔ individualism), and c2_i (cooperation ↔ competition) to the
agent state. ψ_i becomes behaviorally active immediately. c1_i and c2_i are
carried and inherited but not yet behaviorally active — they are observable traits
only in Stage 3.3, becoming mechanically active in later stages. Biparental
reproduction replaces the random fresh-agent replacement rule.

**What Stage 3.3 is not.** It is not a cultural dynamics stage. No Deffuant-style
updating, no prestige bias in transmission, no generational oscillation, no shock
coupling. Those are Stage 4+ additions. Stage 3.3 is infrastructure: the trait
vector exists, is inherited, and one dimension (ψ_i) is active.

**Null Si Cred infrastructure** is also added in Stage 3.3 — a skeleton Cred
accumulation system for Si agents, currently inactive (accumulation rate = 0),
that can be activated in Stage 5+ without refactoring. See §1.4.

**Scope discipline.** If the coding agent finds itself implementing Deffuant
updating, prestige bias, c1/c2 behavioral hooks, or Si Cred accumulation logic,
stop and consult the supervisor. Those are explicitly deferred.

**Before coding:** search LITERATURE.md and the following sources for established
models of continuous cultural trait vectors in mobile-agent ABMs, and log findings
before writing any code:
- Deffuant et al. (2000) "Mixing beliefs among interacting agents" — bounded
  confidence opinion dynamics
- Hegselmann & Krause (2002) — HK model of opinion dynamics
- Epstein & Axtell (1996) ch. 3 — Sugarscape cultural transmission
- Turchin (2003) — secular cycles and generational cultural oscillation
- Boyd & Richerson (1985) ch. 5 — prestige bias in cultural transmission
Log what was lifted, what was rejected, and why in LITERATURE.md.

**Failure modes to watch for:**
- ψ_i crowding collapse: high-ψ agents cluster so densely near peaks that they
  block each other and starve. Diagnostic: deaths_established rising, concentrated
  spatially near peaks.
- Trait homogenization: biparental averaging collapses trait variance to near zero
  within 500 steps. Diagnostic: std(φ), std(ψ), std(c1), std(c2) all → 0.
- Reproduction fallback overuse: if r=3 fallback to random pair fires > 20% of
  replacements, the population is too sparse near death locations — investigate.

---

## 1. What changes in Stage 3.3 (delta from Stage 3.2)

### 1.1 Trait vector H_i

Each agent carries a trait vector H_i = [φ_i, ψ_i, c1_i, c2_i]:

| Dimension | Meaning | Range | Init distribution |
|---|---|---|---|
| φ_i | Status-seeking weight | [0,1] | N(0.5, 0.2²) clipped — already exists |
| ψ_i | Sociability / proximity preference | [0,1] | N(0.5, 0.2²) clipped |
| c1_i | Conformism (0) ↔ Individualism (1) | [0,1] | N(0.5, σ_c²) clipped |
| c2_i | Cooperation (0) ↔ Competition (1) | [0,1] | N(0.5, σ_c²) clipped |

Default σ_c = 0.2 for both c1 and c2 (same as φ). All dimensions clipped to [0,1].

φ_i already exists on BaseAgent — no change to its initialization or use.
ψ_i, c1_i, c2_i are new fields on BaseAgent, initialized at birth.

### 1.2 ψ_i behavioral hook (sociability)

ψ_i adds a proximity term to the agent utility function. For candidate cell j:

$$U_{ij} = w_R^{(i)} \cdot \hat{\Delta\mathcal{R}}_{ij} + w_C^{(i)} \cdot \hat{\Delta\mathcal{C}}_{ij} + \psi_i \cdot \hat{N}_{ij}$$

where $\hat{N}_{ij}$ is the normalized agent count near cell j:

$$\hat{N}_{ij} = \frac{N_{ij}}{\max_{k \in J_i} N_{ik}}$$

$N_{ij}$ = number of agents within distance d=1 of candidate cell j (same distance
as joint-task detection). Normalization is across candidate set J_i — if max is 0
(no neighbors visible), $\hat{N}_{ij} = 0$ for all candidates.

Each of the three utility terms ($\hat{\Delta\mathcal{R}}$, $\hat{\Delta\mathcal{C}}$,
$\hat{N}$) is normalized independently to [0,1] before the softmax. ψ_i is its own
weight — it does not compete with w_R or w_C in scale.

**For BoundedRationalSi:** ψ_i exists in state but the utility function for Si
agents does NOT include the proximity term in Stage 3.3. Si sociability is deferred
to Stage 5+ alongside the Si Cred economy. Si utility remains:

$$U_{ij}^{(Si)} = \hat{\Delta\mathcal{R}}_{ij}$$

### 1.3 Biparental reproduction

Replaces the random fresh-agent replacement rule R from Stage 1. When an agent
dies at location (x, y):

**Parent selection:**
1. Find all living agents within toroidal distance r=3 of (x, y).
2. If ≥ 2 candidates exist: select two parents uniformly at random from candidates.
3. If < 2 candidates exist (sparse area): fall back to random pair from full
   population. Log this event to a `reproduction_fallback_count` metric.

**Trait mixing:**
For each dimension h ∈ {φ, ψ, c1, c2}:
$$h_{\text{child}} = \text{clip}\!\left(\frac{h_A + h_B}{2} + \varepsilon_h,\; 0,\; 1\right)$$

where $\varepsilon_h \sim \mathcal{N}(0, \sigma_{\text{inherit}}^2)$ is independent
copy-error noise per dimension. Default $\sigma_{\text{inherit}} = 0.05$.

**Non-trait attributes** (vision, metabolism, max-age, initial wealth): still drawn
fresh from canonical distributions (§6.3 of Stage 1 blueprint). These are
biological attributes, not cultural traits.

**Cred at birth:** C agents receive f_C · mean_cred as before. Si agents receive 0.

**Age:** offspring start at age 0 as before.

**Fallback behavior:** when fallback fires, the offspring's trait vector is drawn
fresh from the canonical distributions (same as Stage 1 random replacement). This
preserves the original behavior in sparse regions.

### 1.4 Null Si Cred infrastructure

Add a `si_cred` field to BaseAgent (default 0.0) and a `SiCredConfig` block to
the config schema. The accumulation rate is 0 — Si Cred does not change during
Stage 3.3. The infrastructure exists so Stage 5+ can activate it with a config
change.

```yaml
si_cred:
  enabled: false           # set true in Stage 5+ to activate
  accumulation_rate: 0.0   # mechanism TBD — literature search pending
  decay: 0.01              # mirror of C Cred decay, inactive until enabled
```

Do not implement any Si Cred accumulation logic. The field exists, the config
block exists, the value stays 0. That is the full scope of Stage 3.3 Si Cred work.

---

## 2. New config parameters

```yaml
agents:
  # ... existing parameters unchanged ...
  psi_mean: 0.5            # ψ_i sociability mean
  psi_std: 0.2             # ψ_i sociability std
  c1_mean: 0.5             # c1_i conformism↔individualism mean
  c1_std: 0.2
  c2_mean: 0.5             # c2_i cooperation↔competition mean
  c2_std: 0.2

reproduction:
  mode: "biparental"       # "biparental" or "random" (Stage 1 behavior)
  parent_radius: 3         # r — toroidal distance for parent search
  inherit_sigma: 0.05      # σ_inherit — copy-error noise per trait dimension

si_cred:
  enabled: false
  accumulation_rate: 0.0
  decay: 0.01
```

Setting `reproduction.mode: "random"` recovers Stage 1/2/3 behavior exactly —
useful for isolating the biparental effect in comparisons.

---

## 3. New metrics

### 3.1 Per-step trait distribution metrics

| Metric | Definition |
|---|---|
| `mean_phi`, `std_phi` | mean and std of φ_i over living agents |
| `mean_psi`, `std_psi` | mean and std of ψ_i |
| `mean_c1`, `std_c1` | mean and std of c1_i |
| `mean_c2`, `std_c2` | mean and std of c2_i |
| `corr_phi_psi` | Pearson correlation between φ_i and ψ_i |
| `corr_c1_c2` | Pearson correlation between c1_i and c2_i |
| `reproduction_fallback_count` | number of fallback reproductions this step |

### 3.2 Spatial clustering coefficient (new)

For each trait dimension, compute the spatial autocorrelation (Moran's I) of
that trait across the agent population. A value near +1 indicates strong spatial
clustering (trait clusters have formed); near 0 indicates random spatial
distribution.

| Metric | Definition |
|---|---|
| `morans_i_phi` | Moran's I for φ_i spatial distribution |
| `morans_i_psi` | Moran's I for ψ_i spatial distribution |
| `morans_i_c1` | Moran's I for c1_i |
| `morans_i_c2` | Moran's I for c2_i |

Moran's I requires a spatial weights matrix — use inverse toroidal distance between
agent pairs, clipped to agents within distance 5 (for computational efficiency).

### 3.3 New static plots

- Trait distribution histograms at t=0, t=500, t=1000 (all four dimensions)
- Moran's I over time (all four dimensions, same axes)
- std of each trait dimension over time (trait variance preservation diagnostic)
- Spatial scatter: agent positions colored by c1_i and c2_i at t=1000

---

## 4. Runs to execute

Two runs, in order:

| Run | Config | Purpose |
|---|---|---|
| 1 | `stage33_carbon_seed42.yaml` | C with biparental reproduction |
| 2 | `stage33_carbon_random_seed42.yaml` | C with random replacement (mode="random") |

Run 2 is the control — identical to Stage 3.2 canonical C except reproduction mode.
Comparing Run 1 vs Run 2 isolates the biparental effect.

**Output directories:**
- `outputs/stage33_carbon_seed42/`
- `outputs/stage33_carbon_random_seed42/`

Do not overwrite any Stage 3.2 outputs.

---

## 5. Report format

Single report `outputs/stage33_seed42/report.md`:

### Primary comparison table

| Metric (final 100 steps) | C random (control) | C biparental |
|---|---|---|
| Mean wealth | ? | ? |
| Deaths/step (starvation) | ? | ? |
| Deaths/step (established) | ? | ? |
| Mean sigma | ? | ? |
| Joint tasks/step | ? | ? |
| mean_psi | ? | ? |
| std_phi | ? | ? |
| std_psi | ? | ? |
| std_c1 | ? | ? |
| std_c2 | ? | ? |
| corr_phi_psi | ? | ? |
| corr_c1_c2 | ? | ? |
| morans_i_c1 (t=1000) | ? | ? |
| morans_i_c2 (t=1000) | ? | ? |
| reproduction_fallback_rate | — | ? |

### Trait variance preservation

Key diagnostic: do std(φ), std(ψ), std(c1), std(c2) collapse toward zero
(homogenization) or remain stable? Report final 100-step mean ± std for each.

### Spatial clustering

Are cultural clusters forming? Report Moran's I at t=1000 for c1 and c2,
and whether it is significantly above 0 (clustering) or near 0 (random).

---

## 6. Success criteria

1. **Population stable.** N(t) in [200, 300] for all 1000 steps.
2. **Trait variance preserved.** std of each H_i dimension remains > 0.05 at
   t=1000. Collapse toward 0 indicates the biparental averaging is homogenizing
   the population too fast — increase σ_inherit.
3. **ψ_i is behaviorally active.** Moran's I for ψ_i > Moran's I in random
   run — sociable agents are clustering spatially as expected.
4. **Fallback rate acceptable.** reproduction_fallback_rate < 20% of all
   replacements. If above 20%, parent radius r=3 is too small.
5. **Tests pass.**
6. **Reproducibility** confirmed for both runs.

---

## 7. Tests

`tests/test_trait_vector.py`:

1. **H_i initialization:** verify all four dimensions drawn correctly at birth,
   clipped to [0,1], independent across agents.

2. **Biparental mixing:** given two parents with known H_A and H_B, verify
   offspring H_child = mean(H_A, H_B) + ε where ε ~ N(0, σ_inherit²), all
   dimensions clipped to [0,1].

3. **Fallback triggers correctly:** construct a world with < 2 agents within
   r=3 of death location, verify fallback fires and offspring gets fresh traits.

4. **ψ_i utility term:** construct 3-cell candidate set with known N_ij values,
   verify proximity term normalized correctly and added to utility independently.

5. **ψ_i = 0 recovers Stage 3.2 behavior:** verify utility function is identical
   to Stage 3.2 when ψ_i = 0 for all agents.

6. **Si utility unchanged:** verify BoundedRationalSi utility function does not
   include proximity term regardless of ψ_i value.

7. **Si Cred stays zero:** verify si_cred field remains 0.0 for all Si agents
   across 100 steps with enabled=false.

---

## 8. Coding-agent directives

1. **Literature search first.** Before writing any code, search and log the
   sources listed in §0. Focus on: how do mobile-agent ABMs handle cultural
   trait transmission? What transmission mechanisms produce stable clusters
   vs homogenization? Log in LITERATURE.md.

2. **H_i as a dataclass or named tuple on BaseAgent.** Do not implement as
   four separate scalar fields — group them as a single `traits` attribute for
   clean extensibility. Accessing agent.traits.phi, agent.traits.psi, etc.

3. **ReproductionRule abstraction.** Implement biparental reproduction as a
   `ReproductionRule` protocol (flagged in Stage 1 §5.3). The run loop calls
   `reproduction_rule.replace(world, dead_agent, rng)` — the rule handles
   parent selection, mixing, and fallback internally. This is the architectural
   hook that was deferred from Stage 1.

4. **Do not touch CarbonDecision beyond adding the ψ_i term.** The utility
   function change is one line. Do not refactor the softmax or normalization.

5. **c1_i and c2_i are inert in Stage 3.3.** They are stored, inherited, and
   measured. They do not affect any decision, utility, or world mechanic.
   Do not add behavioral hooks for them — flag as TODO for Stage 4+.

6. **Run control first.** Run the random-replacement control before the
   biparental run. Confirm the control matches Stage 3.2 canonical C results
   (mean wealth ~42.4, deaths ~2.99) before running biparental. Any deviation
   indicates a regression in the base code.

7. **Moran's I implementation.** Use scipy.spatial for distance matrix
   computation. Clip to agents within distance 5 for efficiency. Document
   the implementation in a docstring — this metric will be used in every
   subsequent stage.

8. **Update ROADMAP.md** at completion: mark Stage 3.3 complete, update
   locked parameters table, add any new deferred items discovered during
   implementation.

---

## 9. Deferred

- c1_i behavioral hook (conformism affects cultural transmission probability). → Stage 4+.
- c2_i behavioral hook (competition affects joint-task strategy). → Stage 4+.
- Prestige bias in trait transmission (Cred-weighted parent influence). → Stage 4+.
- Deffuant-style bounded confidence cultural updating. → Stage 4+.
- Generational oscillation dynamics. → Stage 5+.
- Shock coupling of cultural trait mean T(t). → Stage 4.
- Si Cred accumulation mechanism (literature search pending). → Stage 5+.
- Si ψ_i behavioral hook. → Stage 5+.
- ψ_i for Si agents in utility function. → Stage 5+.
- Parent radius r as sweep parameter. → Stage 5+.
- σ_inherit as sweep parameter. → Stage 5+.
- H_i extension beyond 4 dimensions. → As motivated by data.
