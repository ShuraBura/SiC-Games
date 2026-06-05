# SiC Games — Stage 4.1c Blueprint: Proximity Support Pool

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 4.1c only. Proximity support pool for juveniles and elders.
**Prerequisite:** Stage 4.1b patch complete. η formula confirmed correct.
Locked P_max values: C static 0.12, Si static 0.14, C seasonal 0.14, Si seasonal 0.17.

---

## 0. North Star (read first, every session)

**Stage 4.1c goal:** address the structural juvenile starvation finding from
Stage 4.1b. Newborns exhaust their initial wealth endowment at steps 3-5,
long before reaching foraging break-even age (~9-10). The fix: parental wealth
transfer at birth plus a local proximity pool that supports non-active agents
(juveniles and elders) from active adult surplus.

**The specific mechanism:** two-level support:
- **Level 1 (parental transfer):** at birth, the parent(s) transfer a fraction
  τ_parent of their current wealth to the offspring. Reduces parent wealth,
  boosts offspring starting capital. Applies at the moment of birth.
- **Level 2 (proximity pool):** each step, active adults contribute a fraction
  τ_pool of their harvest surplus (above metabolic cost) to a local pool.
  Non-active agents (age outside foraging window) draw from the pool to cover
  their metabolic deficit if their own wealth is insufficient.

**C vs Si distinction — read carefully:**
- C: Level 1 + Level 2 with status-mediated contribution (high-Cred agents
  contribute more; contribution earns Cred increment).
- Si: Level 1 + Level 2 without status component. Purely proximity-based.
  No Si Cred involvement yet (Si Cred economy deferred to Stage 5+).

**What Stage 4.1c is not.** No inter-pool connectivity. No Cred-modulated birth.
No wealth inheritance λ > 0. No Si Cred. Pool is local and independent.

**Primary success metric:** juvenile starvation % drops below 60% in null
controls. This is the deferred Stage 4.1b criterion being resolved here.

**Read ROADMAP.md C/Si distinction table before touching any agent code.**

**Failure modes to watch for:**
- Pool depletion: active adults don't generate sufficient surplus to cover
  juvenile + elder deficits. Diagnostic: pool_draw_unmet > 20% of total
  draw requests. Increase τ_pool or accept as resource-constrained behavior.
- Population explosion: support pool boosts juvenile survival dramatically,
  juveniles mature and reproduce, population overshoots. Diagnostic: N > 500
  sustained > 100 steps. May require P_max reduction after pool is active.
- Status contribution lock: high-Cred C agents contribute so much to the pool
  that they deplete their own wealth and starve. Diagnostic: established
  starvation rising sharply with pool active.
- Pool free-rider: agents draw from pool without contributing (not a mechanic
  issue — agents can't choose not to contribute; contribution is automatic).
  But watch for mean_eta agents contributing near-zero surplus (low-η agents
  contribute little because they harvest little).

---

## 1. What changes in Stage 4.1c

### 1.1 Parental wealth transfer (Level 1)

At birth, before the offspring is placed in the world:

**C (biparental):**
$$w_{\text{child}}(0) = w_{\text{init}} + \tau_{\text{parent}} \cdot \frac{w_A + w_B}{2}$$
$$w_A \leftarrow w_A \cdot (1 - \tau_{\text{parent}})$$
$$w_B \leftarrow w_B \cdot (1 - \tau_{\text{parent}})$$

where $w_{\text{init}}$ is the standard initial wealth draw from Uniform[5,25]
and $\tau_{\text{parent}}$ is the parental transfer fraction. Default
$\tau_{\text{parent}} = 0.1$ (parents each give 10% of their current wealth).

**Si (fission):**
$$w_{\text{child}}(0) = w_{\text{init}} + \tau_{\text{parent}} \cdot w_{\text{parent}}$$
$$w_{\text{parent}} \leftarrow w_{\text{parent}} \cdot (1 - \tau_{\text{parent}})$$

Single parent gives τ_parent fraction of their wealth. Same default τ_parent=0.1.

**Minimum parent wealth:** parents must retain at least 2× their own metabolism
after transfer. If the transfer would drop parent below this floor, transfer
the maximum possible (parent wealth - 2×metabolism), or zero if already below.

### 1.2 Proximity support pool (Level 2)

**Pool structure:** one pool per proximity cluster. A cluster is defined as
all agents within radius r_pool=5 of a focal cell, computed once per step.
Pools are independent — no inter-pool flow.

**Contribution (each step, after harvest):**

For each active adult (age in [a_forage_min, a_forage_max]):
$$\text{surplus}_i = \max(0,\; w_i - w_{\text{reserve}})$$
$$\text{contribution}_i = \tau_{\text{pool}} \cdot \text{surplus}_i$$
$$w_i \leftarrow w_i - \text{contribution}_i$$

where $w_{\text{reserve}} = k_{\text{reserve}} \times \text{agent metabolism}$
is the wealth the agent keeps before contributing (default $k_{\text{reserve}}=5$,
so agents keep 5 steps of metabolic reserve).

Default $\tau_{\text{pool}} = 0.1$ (10% of surplus contributed).

**C status-mediated contribution:** for C agents, contribution is scaled by
Cred level:
$$\text{contribution}_i^C = \tau_{\text{pool}} \cdot \text{surplus}_i \cdot
\left(1 + \tau_{\text{cred}} \cdot \tanh\!\left(\frac{\mathcal{C}_i}{\mathcal{C}^*}\right)\right)$$

where $\tau_{\text{cred}}=0.5$ (high-Cred agents contribute up to 50% more).
High-Cred agents that contribute above the base rate receive a Cred increment:
$$\Delta\mathcal{C}_i^{\text{pool}} = \tau_{\text{cred\_reward}} \cdot
(\text{contribution}_i^C - \tau_{\text{pool}} \cdot \text{surplus}_i)$$

Default $\tau_{\text{cred\_reward}} = 0.1$ (small Cred reward for generosity).

**Si contribution:** flat τ_pool only. No Cred scaling. No Cred reward.

**Pool draw (each step, after contributions):**

For each non-active agent (age < a_forage_min OR age > a_forage_max_i) within
the cluster that has a metabolic deficit (wealth < metabolism × k_draw_reserve):
$$\text{need}_i = \text{metabolism}_i \cdot k_{\text{draw}} - w_i$$
$$\text{draw}_i = \min(\text{need}_i,\; \text{pool\_balance} \cdot \text{share}_i)$$

where $\text{share}_i$ is the agent's proportional claim on the pool (equal
shares among eligible drawers this step), and $k_{\text{draw}}=3$ (agents
draw to cover 3 steps of metabolism). Pool balance is updated after each draw.

If pool is exhausted before all needs are met, remaining agents receive nothing.
Track `pool_draw_unmet` per step.

**Pool resets to zero each step** — surplus not carried over. Agents contribute
fresh each step from their harvest.

### 1.3 New config section

```yaml
support_pool:
  enabled: true
  r_pool: 5                    # proximity radius for pool cluster
  tau_parent: 0.1              # parental wealth transfer fraction
  tau_pool: 0.1                # active adult contribution fraction
  k_reserve: 5                 # metabolic reserve before contributing
  k_draw: 3                    # steps of metabolism covered by draw
  tau_cred: 0.5                # C only: Cred scaling of contribution
  tau_cred_reward: 0.1         # C only: Cred reward for above-base contribution
```

Setting `enabled: false` recovers Stage 4.1b behavior exactly.

### 1.4 n_mvp metric

Add `n_mvp_threshold` diagnostic: the minimum N observed before population
recovers to above 200 in any 100-step window. This is the operational measure
of the Allee threshold identified in Stage 4.1a. Track per run.

---

## 2. New metrics

| Metric | Definition |
|---|---|
| `pool_total_contributed` | total wealth contributed to all pools this step |
| `pool_total_drawn` | total wealth drawn from all pools this step |
| `pool_draw_unmet` | draw requests that could not be filled (pool exhausted) |
| `pool_draw_unmet_frac` | pool_draw_unmet / total draw requests |
| `mean_parental_transfer` | mean wealth transferred per birth this step |
| `juv_starvation_pct` | juvenile starvation as % of total starvation |
| `elder_starvation_pct` | elder starvation as % of total starvation |
| `n_mvp_threshold` | minimum N before recovery (running minimum) |
| `cred_pool_contribution` | C only: Cred earned from pool contribution this step |

---

## 3. Runs to execute

Four runs in strict order:

| Run | Config | Purpose |
|---|---|---|
| 1 | `stage41c_c_static_seed42.yaml` | C null control — pool active |
| 2 | `stage41c_si_static_seed42.yaml` | Si null control — pool active |
| 3 | `stage41c_c_seasonal_seed42.yaml` | C seasonal with pool |
| 4 | `stage41c_si_seasonal_seed42.yaml` | Si seasonal with pool |

Runs 1+2 gate Runs 3+4. Gate criterion: juvenile starvation % < 60% AND
N(t) quasi-stationary in [150, 400] by t=500.

All runs use locked P_max values from Stage 4.1b patch:
C static 0.12, Si static 0.14, C seasonal 0.14, Si seasonal 0.17.

**If gate passes but N overshoots [150,400]:** the pool has boosted juvenile
survival enough to push equilibrium N above 400. Reduce P_max by 0.01 and
re-run. Document in report. Accept up to 2 P_max reductions before flagging
as a design issue.

---

## 4. Report format

### Primary comparison table

| Metric (t≥500) | 4.1b C | 4.1c C | 4.1b Si | 4.1c Si |
|---|---|---|---|---|
| N mean | 306.8 | ? | 269.7 | ? |
| N range (t≥500) | [231,376] | ? | [218,330] | ? |
| Mean wealth | 36.88 | ? | 41.05 | ? |
| Juv starvation % | 84.7% | ? | 77.3% | ? |
| Elder starvation % | — | ? | — | ? |
| Pool draw unmet % | — | ? | — | ? |
| Mean parental transfer | — | ? | — | ? |
| Cred pool contribution | — | ? | — | ? |
| n_mvp_threshold | — | ? | — | ? |

### Seasonal comparison (H1(ii) update)

| Metric (t≥500) | 4.1b C seas | 4.1c C seas | 4.1b Si seas | 4.1c Si seas |
|---|---|---|---|---|
| N mean | 318.8 | ? | 228.8 | ? |
| N min (all) | 262 | ? | 160 | ? |
| N max (all) | 400 | ? | 351 | ? |
| Juv starvation % | 82.4% | ? | 75.4% | ? |

### Pool diagnostics

Report pool_draw_unmet_frac over time (plot). If > 20% sustained, pool is
under-resourced — flag for supervisor. Do not silently increase τ_pool.

---

## 5. Success criteria

1. **Juvenile starvation < 60%** in both C and Si null controls. This is the
   primary criterion carried forward from Stage 4.1b.

2. **Pool not depleted.** pool_draw_unmet_frac < 20% at steady state in null
   controls. If pool is frequently exhausted, active adults aren't generating
   enough surplus — this is a resource constraint, not a bug.

3. **N quasi-stationary [150, 400]** in null controls by t=500.

4. **No established-agent starvation spike.** Deaths/step (established) does
   not increase more than 30% relative to Stage 4.1b (0.60 C, 0.90 Si) with
   pool active. Pool contribution should not impoverish active adults.

5. **Tests pass.**

6. **Reproducibility** confirmed.

---

## 6. Tests

`tests/test_support_pool.py`:

1. **Parental transfer C:** given two parents with known wealth, verify
   offspring receives τ_parent × mean(w_A, w_B) added to w_init, and both
   parents are reduced by τ_parent fraction.

2. **Parental transfer Si:** single parent gives τ_parent × w_parent to
   offspring.

3. **Minimum parent wealth respected:** parent at 2× metabolism floor —
   verify transfer is capped, not full τ_parent.

4. **Pool contribution:** agent with known surplus, verify contribution =
   τ_pool × surplus, wealth reduced correctly.

5. **C status contribution:** high-Cred agent (𝒞=20) vs low-Cred agent (𝒞=0),
   same surplus — verify high-Cred contributes more by τ_cred factor.

6. **C Cred reward:** verify Cred increment received for above-base contribution.

7. **Pool draw:** non-active agent with deficit, known pool balance — verify
   draw = min(need, pool × share), pool balance reduced.

8. **Pool exhaustion:** two non-active agents, pool insufficient for both —
   verify pool_draw_unmet increments, agents receive proportional shares.

9. **Pool resets each step:** verify pool balance = 0 at start of each step
   before contributions.

10. **Si pool no Cred scaling:** verify Si contribution = τ_pool × surplus
    regardless of si_cred value.

11. **enabled=false recovers 4.1b:** verify no pool contribution or draw
    occurs when support_pool.enabled=false.

---

## 7. Coding-agent directives

1. **Pool is local, not global.** Each step, identify proximity clusters
   (agents within r_pool=5 of each other). Contributions and draws happen
   within clusters. Do not implement a single global pool.

2. **Pool resets each step.** Do not carry surplus forward. Fresh contribution
   cycle every step.

3. **C and Si contribution logic are separate methods** in SupportPool class.
   Never apply C status-scaling to Si agents.

4. **Contribution happens after harvest, before metabolism.** Agents harvest,
   then contribute surplus, then pay metabolism. This ordering ensures agents
   contribute from real harvest, not from reserves.

5. **Draw happens after all contributions are collected.** Non-active agents
   draw from the accumulated pool, not from individual contributors directly.

6. **Report completeness rule applies.** All tuning attempts documented.
   Pool_draw_unmet_frac must appear in report with numbers, not just
   "pool functioning normally."

7. **If P_max needs reduction after pool active:** document each attempt in
   the report tuning history. Maximum 2 reductions before flagging as design
   issue.

8. **Update ROADMAP.md** at completion: mark Stage 4.1c complete, record
   juvenile starvation % achieved, note any P_max adjustments.

---

## 8. Deferred

- Inter-pool connectivity / exchange. → Stage 5+.
- Cred-modulated birth γ. → Stage 4.2.
- Wealth inheritance λ > 0. → Stage 4.2.
- Si Cred economy. → Stage 5+.
- Elder knowledge bonus for Si. → Stage 5+.
- Defection/criminal emergence from pool free-riding. → Stage 6+
  (requires c2 behavioral hook active).
- τ_pool, τ_parent, τ_cred as sweep parameters. → Stage 5.x nD scan.
