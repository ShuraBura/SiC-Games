# SiC Games — Stage 2 Blueprint

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 2 only. Stage 1 is complete and its substrate is locked — do not refactor it.
**Prerequisite:** Stage 1 report passing all success criteria (confirmed seed=42, Gini=0.47, population=250, peaks=63%).

---

## 0. North Star (read first, every session)

**Stage 2 goal:** produce the *first comparative result* — a C (Carbon) population running on the same Sugarscape substrate as Stage 1's greedy-Si, on identical worlds, with a report that shows whether and how the two populations differ on primary metrics.

**What Stage 2 is not.** It is not the variance-matched comparison (Stage 3). The greedy-Si baseline from Stage 1 is the comparison partner here. We are not yet calibrating σ_Si to match C's mean decision entropy — that requires Stage 2 data, which this stage generates. Stage 2 is the *instrument calibration run*, not the definitive experiment.

**Scope discipline.** The two new mechanisms in Stage 2 are: (1) the Carbon decision strategy (status-coupled softmax), and (2) the minimal joint-task mechanic (which is the only source of Cred). Nothing else changes. If the coding agent finds itself touching world.py, the replacement rule, or the growback logic, **stop and consult the supervisor.**

**Failure modes to watch for:**
- Cred monopoly: one agent accumulates all Cred and σ pegs at σ_base + κ permanently. Diagnostic: max_cred_fraction > 0.5 at steady state.
- Absorption: entire population starves because σ is too high and agents stop finding sugar. Diagnostic: population < 200 sustained for > 100 steps.
- Zero joint tasks: the joint-task mechanic never fires because d or the capacity threshold is too restrictive. Diagnostic: mean_joint_task_count = 0 after step 50.

If any of these occur, **halt and report** — do not adjust parameters silently.

---

## 1. What changes in Stage 2 (delta from Stage 1)

Stage 1 is fully preserved. Stage 2 *adds* the following, with no modification to existing files except where explicitly noted:

### New agent state (additions to BaseAgent or CarbonAgent)

| New field | Type | Init | Description |
| :--- | :--- | :--- | :--- |
| `cred` | float | 0.0 | Accumulated social status $\mathcal{C}_i$ |
| `phi` | float | drawn at birth | Born-rationalist (0) ↔ egomaniac (1) trait |

These fields are added to `BaseAgent` (with defaults that make greedy-Si unaffected) or to a new `CarbonAgent` subclass. The architectural choice is: **add to BaseAgent** with defaults `cred=0.0`, `phi=0.5`. This preserves code symmetry (§15.6 of the Stage 1 blueprint) — Si agents carry the fields but ignore them.

### New strategy file

`src/sic_games/agents/strategies/carbon.py` — implements `CarbonDecision`, a new `DecisionLogic` that replaces `GreedyMaximizer` for C-type runs.

### New world mechanic

Joint-task detection and payoff distribution, implemented in a new `src/sic_games/joint_task.py` module. Called from the run loop after growback and before agent movement.

### New metrics

`mean_cred`, `gini_cred`, `max_cred_fraction`, `joint_task_count`, `joint_task_participants`, `mean_sigma` added to `metrics.py`.

### New config section

`carbon:` block added to the YAML schema. Existing `decision.strategy: "greedy"` still works unchanged.

### New test files

`tests/test_carbon_decision.py`, `tests/test_cred_update.py`, `tests/test_matthew_partition.py`, `tests/test_joint_task.py`.

### New config file

`configs/stage2_carbon_seed42.yaml` — C run. The Stage 1 config is untouched.

---

## 2. Math specification (Stage 2 additions)

### 2.1 Carbon agent state

Each C agent carries two additional scalar attributes:

**Born-trait φ_i** — drawn once at birth, fixed for life:
$$\phi_i \;\sim\; \mathcal{N}(0.5,\; \sigma_\phi^2)\;\text{clipped to }[0, 1]$$
Default $\sigma_\phi = 0.2$.

**Social Cred $\mathcal{C}_i$** — mutable, initialized to 0 at birth:
$$\mathcal{C}_i(t+1) \;=\; (1 - \delta)\,\mathcal{C}_i(t) \;+\; \Delta\mathcal{C}_i(t)$$
where $\delta \in (0, 1)$ is per-step decay and $\Delta\mathcal{C}_i(t) = 0$ in any step the agent did not participate in a joint-task event (see §2.3).

Default $\delta = 0.01$.

### 2.2 Carbon decision noise (σ form)

For each C agent, the per-step decision temperature is:
$$\sigma_i^{(C)} \;=\; \sigma_{\text{base}} \;+\; \kappa \cdot \tanh\!\big(\mathcal{C}_i / \mathcal{C}^{*}\big)$$

- $\sigma_{\text{base}}$: baseline exploration noise. Default 0.5.
- $\kappa$: maximum additional noise that Cred can add. Default 2.0.
- $\mathcal{C}^{*}$: Cred level at which hubris is at half maximum. Default 10.0.

At $\mathcal{C}_i = 0$: $\sigma_i = \sigma_{\text{base}}$. As $\mathcal{C}_i \to \infty$: $\sigma_i \to \sigma_{\text{base}} + \kappa$.

### 2.3 Joint-task mechanic (Stage 2 minimal version)

**Detection (per step, before agent movement):**

For each grid cell $(x, y)$ with sugar capacity $c(x, y) \ge \theta_c$ (capacity threshold), check whether $|\mathfrak{C}_{xy}| \ge 2$, where:
$$\mathfrak{C}_{xy} \;=\; \{\,i \;:\; d_{\text{tor}}\big((x_i, y_i),\, (x, y)\big) \le d\,\}$$
is the set of agents within toroidal distance $d$ of the cell. Default $d = 1$, default $\theta_c = c_{\max} = 4$ (only peak-capacity cells trigger joint tasks in Stage 2).

If $|\mathfrak{C}_{xy}| \ge 2$, cell $(x,y)$ becomes a **joint-task cell** for this step.

**Payoff distribution (Matthew rule):**

For a joint-task cell $(x, y)$ with current sugar $s(x, y, t)$ and cluster $\mathfrak{C}$:

$$\Delta\mathcal{R}_i \;=\; s(x, y, t) \cdot \frac{(\mathcal{C}_i + \varepsilon)^{\alpha}}{\sum_{j \in \mathfrak{C}} (\mathcal{C}_j + \varepsilon)^{\alpha}}, \qquad \forall\, i \in \mathfrak{C}$$

$$\Delta\mathcal{C}_i \;=\; \mathcal{C}_{\text{bonus}} \cdot \frac{(\mathcal{C}_i + \varepsilon)^{\alpha}}{\sum_{j \in \mathfrak{C}} (\mathcal{C}_j + \varepsilon)^{\alpha}}, \qquad \forall\, i \in \mathfrak{C}$$

where $\mathcal{C}_{\text{bonus}}$ is the total Cred dispensed by this joint-task event (default: $\mathcal{C}_{\text{bonus}} = |\mathfrak{C}| \cdot 1.0$, i.e., 1.0 Cred unit per participant if split equally, more to high-Cred agents). Default $\alpha = 1.5$, $\varepsilon = 0.01$.

After payoff distribution, set $s(x, y, t) \leftarrow 0$ (the cell is harvested).

Each agent $i \in \mathfrak{C}$ receives $w_i \mathrel{+}= \Delta\mathcal{R}_i$ immediately. Their Cred update $\Delta\mathcal{C}_i$ is applied at the *end* of the step (after movement), as part of the Cred update rule in §2.1.

**Effect on movement:** joint-task cells are treated as empty (sugar = 0) for the purpose of movement this step — they've been pre-harvested. Agents whose greedy/softmax target was a joint-task cell will not harvest again; they still move there (or elsewhere) normally.

**Note:** In Stage 2, the barrier-reduction term $E_a^{\text{eff}} = E_a \cdot \exp(-\gamma\,\mathcal{S}(\mathfrak{C}))$ from §15.5 of the Stage 1 blueprint is **not implemented** (set $\gamma = 0$ implicitly). This is deliberate — Mines and the activation-energy mechanism are Stage 4. Do not pre-build it.

### 2.4 Carbon utility function (softmax decision)

For a C agent choosing among candidate cells $J_i$ (the Von Neumann neighborhood within vision, as per Stage 1's §6.4):

**Utility of candidate cell $j$:**
$$U_{ij} \;=\; w_R^{(i)} \cdot \widehat{\Delta\mathcal{R}}_{ij} \;+\; w_C^{(i)} \cdot \widehat{\Delta\mathcal{C}}_{ij}$$

where:
- $w_R^{(i)} = 1 - \phi_i$ (resource weight)
- $w_C^{(i)} = \phi_i$ (Cred weight)

**Estimated resource gain:**
$$\widehat{\Delta\mathcal{R}}_{ij} \;=\; s(x_j, y_j, t)$$
(current sugar at the candidate cell — same as greedy-Si, normalized below)

**Estimated Cred gain:**
$$\widehat{\Delta\mathcal{C}}_{ij} \;=\; \begin{cases} \text{Matthew share of } \mathcal{C}_{\text{bonus}} \text{ if cell } j \text{ is a joint-task cell visible to agent } i \\ 0 & \text{otherwise} \end{cases}$$

The Matthew share uses the agent's own $\mathcal{C}_i$ and the observed Cred of visible cluster members.

**Normalization:** Before computing the softmax, normalize $\widehat{\Delta\mathcal{R}}$ and $\widehat{\Delta\mathcal{C}}$ independently to $[0, 1]$ across the candidate set $J_i$ (divide by the maximum over candidates; if max = 0, leave as 0). This prevents one utility term dominating due to scale.

**Softmax selection:**
$$P(\text{choose cell } j) \;=\; \frac{\exp(U_{ij} / \sigma_i)}{\sum_{k \in J_i} \exp(U_{ik} / \sigma_i)}$$

where $\sigma_i = \sigma_i^{(C)}$ from §2.2. Low σ → nearly greedy. High σ → nearly uniform random.

**Tie semantics:** Unlike the greedy rule, the softmax is probabilistic — ties are broken by the distribution itself, no special-case tie-break needed. However, if all utilities are identical (uniform-sugar neighborhood), the softmax degenerates to uniform random, which is correct behavior.

### 2.5 Scheduling change for Stage 2

The step order is updated:

1. **Growback** $G_\alpha$: same as Stage 1.
2. **Joint-task detection:** identify all joint-task cells and distribute payoffs (§2.3). Update participating agents' wealth. Mark joint-task cells as empty.
3. **Agent step:** all agents processed in random order; each runs: perceive → decide (CarbonDecision or GreedyMaximizer per agent type) → move → harvest (if cell not already emptied) → pay metabolism → age → death check.
4. **Cred update:** for all agents that participated in a joint task this step, apply $\Delta\mathcal{C}_i$ to their Cred state per §2.1. For all agents, apply decay: $\mathcal{C}_i \leftarrow (1-\delta)\mathcal{C}_i$.
5. **Replacement** $R$: same as Stage 1.
6. **Metrics:** record expanded metric set (§3.1).

**Critical ordering note:** joint-task payoff is distributed *before* individual movement so agents receive their Matthew share regardless of which physical cell they end up on. Movement then happens on the depleted field.

---

## 3. Metrics and outputs (additions)

### 3.1 New per-step metrics

| Metric | Definition |
| :----- | :--------- |
| `mean_cred` | mean $\mathcal{C}_i$ over living agents |
| `gini_cred` | Gini coefficient of $\{\mathcal{C}_i\}$ |
| `max_cred_fraction` | $\max_i(\mathcal{C}_i) / \sum_j \mathcal{C}_j$ — monopoly diagnostic |
| `mean_sigma` | mean $\sigma_i^{(C)}$ over living agents |
| `joint_task_count` | number of joint-task cells this step |
| `joint_task_participants` | total agent-participations this step (can exceed joint_task_count) |

All Stage 1 metrics are retained unchanged.

### 3.2 New static plots

- Cred distribution over time (mean ± std)
- Gini of Cred over time
- `mean_sigma` over time (shows whether hubris is accumulating)
- `joint_task_count` over time (verifies the mechanic is active)

### 3.3 Comparison report

At Stage 2, the supervisor will be comparing two `report.md` files side by side: Stage 1 (greedy-Si, seed=42) and Stage 2 (Carbon, seed=42). The Stage 2 `report.md` adds a **Comparison to Stage 1** section:

```markdown
## Comparison to Stage 1 (greedy-Si, same seed)
| Metric (final 100 steps) | Stage 1 (Si) | Stage 2 (C) | Δ |
|---|---|---|---|
| Mean wealth | 52.3 | ? | ? |
| Gini wealth | 0.47 | ? | ? |
| Spatial dispersion | 15.5 | ? | ? |
| Deaths/step (starvation) | 1.8 | ? | ? |
| Deaths/step (senescence) | 2.8 | ? | ? |
| Mean Cred | — | ? | — |
| Gini Cred | — | ? | — |
| Joint tasks/step | — | ? | — |
```

This table is the primary deliverable of Stage 2 — the first look at whether C and Si actually differ.

---

## 4. Configuration

New `configs/stage2_carbon_seed42.yaml`:

```yaml
seed: 42
world:
  grid_size: [50, 50]
  toroidal: true
  sugar_peaks: [[10, 40], [40, 10]]
  max_sugar_capacity: 4
  band_width_k: 6
  growth_rate_alpha: 1
agents:
  initial_population: 250
  vision_dist: [1, 6]
  metabolic_rate_dist: [1, 4]
  max_age_dist: [60, 100]
  initial_wealth_dist: [5, 25]
  phi_mean: 0.5          # born-rationalist (0) <-> egomaniac (1) axis
  phi_std: 0.2
decision:
  strategy: "carbon"     # activates CarbonDecision
carbon:
  sigma_base: 0.5        # baseline softmax temperature
  kappa: 2.0             # max additional noise from Cred
  cred_scale: 10.0       # C* — half-saturation Cred level
  cred_decay: 0.01       # δ — per-step Cred decay fraction
  matthew_alpha: 1.5     # α — Matthew power exponent
  epsilon: 0.01          # ε — Laplace smoothing
  cred_bonus_per_participant: 1.0  # Cred dispensed per participant per joint task
joint_task:
  distance_d: 1           # agents within this toroidal distance are in the cluster
  capacity_threshold: 4   # only cells with c(x,y) >= this trigger joint tasks
run:
  n_steps: 1000
  metrics_every: 1
  output_dir: "outputs/stage2_carbon_seed42"
visualization:
  animate: true
  frames_per_save: 5
  save_static_plots: true
```

The `stage1_baseline.yaml` is **not modified**. Greedy runs are unchanged.

---

## 5. Module structure (additions only)

```
src/sic_games/
├── joint_task.py            # NEW: JointTaskManager
└── agents/
    ├── base.py              # MODIFIED: add cred, phi fields with defaults
    └── strategies/
        └── carbon.py        # NEW: CarbonDecision
tests/
├── test_carbon_decision.py  # NEW
├── test_cred_update.py      # NEW
├── test_matthew_partition.py # NEW
└── test_joint_task.py       # NEW
configs/
└── stage2_carbon_seed42.yaml # NEW
```

Everything else is unchanged from Stage 1.

### `joint_task.py` — key interface

```python
# src/sic_games/joint_task.py

from dataclasses import dataclass, field
import numpy as np

@dataclass
class JointTaskEvent:
    cell: tuple[int, int]
    cluster: list["BaseAgent"]
    total_sugar: float
    total_cred_bonus: float

class JointTaskManager:
    """Detects joint-task cells and distributes Matthew payoffs.

    Called once per step, before agent movement.
    Returns a list of JointTaskEvents (may be empty).
    """
    def __init__(self, distance_d: int, capacity_threshold: float,
                 matthew_alpha: float, epsilon: float,
                 cred_bonus_per_participant: float):
        ...

    def process_step(
        self,
        world: "World",
        agents: list["BaseAgent"],
        rng,
    ) -> list[JointTaskEvent]:
        """
        For each joint-task cell:
          1. Distribute Matthew share of sugar to wealth.
          2. Zero out the cell's sugar.
          3. Record Delta_C for each participant (applied later in Cred update).
        Returns list of events for metric recording.
        """
        ...
```

### `carbon.py` — key interface

```python
# src/sic_games/agents/strategies/carbon.py

class CarbonDecision:
    """Softmax decision with Cred-coupled temperature and Cred utility term.

    Implements DecisionLogic protocol.
    """
    def __init__(self, sigma_base: float, kappa: float, cred_scale: float,
                 joint_task_cells: set[tuple[int, int]] = None):
        # joint_task_cells is injected each step by the run loop
        # (the cells already processed by JointTaskManager this step)
        ...

    def select_target(
        self,
        agent: "BaseAgent",
        perception: "Perception",
        rng,
    ) -> tuple[int, int]:
        """Softmax over utility U_ij = (1-phi)*R_hat + phi*C_hat, temp=sigma_i."""
        ...
```

---

## 6. Success criteria (Stage 2 done = all of these pass)

1. **C population stability.** N(t) for the Carbon run stays in [200, 300] throughout 1000 steps. No sustained extinction or explosion.

2. **Joint tasks are firing.** `mean_joint_task_count` (averaged over steps 100–1000) > 0. The mechanic must actually trigger during a run.

3. **Cred is accumulating and stable.** `gini_cred` reaches a quasi-steady state (std over last 100 steps < 0.05). `mean_cred` > 0.

4. **No Cred monopoly.** `max_cred_fraction` < 0.5 at all steps after t = 100. If one agent holds > 50% of total Cred, the system is in a pathological absorption state.

5. **σ is actually varying.** `mean_sigma` > `sigma_base` at steady state (i.e., Cred is actually driving the noise up for at least some agents).

6. **Tests pass.** All new pytest tests pass:
   - `test_matthew_partition`: for a known cluster with known Cred values, verify each agent receives the correct Matthew share (to 4 decimal places).
   - `test_cred_update`: verify decay formula and Δ𝒞 accumulation on a two-step sequence.
   - `test_carbon_decision`: verify softmax probabilities are correct for a constructed 3-cell candidate set with known utilities and σ. Verify that setting φ=0 (pure resource) recovers near-greedy behavior and φ=1 (pure Cred) weights Cred gains.
   - `test_joint_task`: on a constructed 3×3 world with two agents within d=1 of a high-capacity cell, verify the joint task fires, sugar is zeroed, and wealth increments match the Matthew formula.

7. **Reproducibility.** Two runs with seed=42 produce identical metric traces.

If criteria 1–5 pass but the observed C vs Si differences are small or zero, **that is a valid result** — report it as such. Do not tune parameters to manufacture a difference. The Stage 2 report's comparison table is purely observational.

---

## 7. Out of scope (do not build in Stage 2)

- Variance-matched Si (bounded-rational Si with calibrated σ_Si). → Stage 3.
- Barrier reduction (γ term, E_a^eff). → Stage 4.
- Environmental perturbations. → Stage 4.
- Multi-world / batch runs. → Stage 5.
- Statistical testing of H1. → Stage 6.
- Heuristic vector H, biparental reproduction. → Stage 7+.
- Any modification to world.py, growback, or the replacement rule R.
- Any modification to GreedyMaximizer or Stage 1's greedy config.

---

## 8. Coding-agent directives (Stage 2 specific)

1. **Re-read the Stage 1 blueprint §0 (North Star)** before starting. The discipline applies here too.
2. **Do not touch Stage 1 files** except: (a) adding `cred` and `phi` fields with neutral defaults to `BaseAgent`, and (b) adding new metrics to `metrics.py`. No other existing files change.
3. **Implement and test bottom-up.** Order: Matthew partition math → JointTaskManager (with test) → Cred update logic (with test) → CarbonDecision softmax (with test) → run loop integration → metrics additions → config loading → full run.
4. **Validate the joint-task mechanic fires on a small world first.** Run a 10×10 grid, 20 agents, 50 steps with carbon strategy. Print joint_task_count each step. If it's zero for all steps, the detection distance or threshold is too restrictive — investigate before scaling up.
5. **Watch for monopoly and absorption during development.** If you see max_cred_fraction → 1.0 or population → 0 on the small world, halt, log, and report. These are design failure modes, not implementation bugs.
6. **The comparison table in the report is mandatory.** The Stage 2 report.md must include the Comparison to Stage 1 section (§3.3). Hardcode the Stage 1 values from the confirmed report (Gini=0.47, mean_wealth=52.3, dispersion=15.5, etc.) — they are ground truth.
7. **Random seeds.** All stochastic calls (φ draws, softmax sampling, shuffle) use the seeded RNG from config. No bare `random.random()` or `np.random.X`.
8. **Log the default parameter rationale in LITERATURE.md.** The defaults (σ_base=0.5, κ=2.0, C*=10.0, δ=0.01, α=1.5) are starting points from the literature review. Note in LITERATURE.md that these are exploratory defaults, not tuned values.

---

## 9. Open questions for the supervisor (not the coding agent)

| Q | Topic | Status |
| :- | :---- | :----- |
| Q5 | Default parameter values (σ_base, κ, C*, δ) | **Exploratory** — Stage 2 is the first data. Values above are starting points. Expect to need a short tuning pass after Stage 2 completes. |
| Q6 | Cred_bonus_per_participant scaling | **TBD** — current default (1.0 per participant) is arbitrary. Should it scale with cell capacity? Sugar harvested? Revisit after first run. |
| Q7 | Variance-matching protocol (Q4 from Stage 1) | **Deferred to Stage 3** — Stage 2 data (mean decision entropy of C at quasi-steady-state) is needed to calibrate σ_Si. |
| Q8 | Joint-task detection: cluster is proximity-based, not intent-based | **Design choice confirmed for Stage 2.** Agents don't "choose" to join a joint task — they're included if within d=1. This is the minimal mechanic. Intent-based coordination (agents moving toward joint tasks) is implicitly captured by the utility function (§2.4) but not the detection rule. |

---

## 10. References (Stage 2 additions)

The Stage 1 references apply. Additional:

- **Merton, R.K. (1968).** "The Matthew Effect in Science." *Science* 159(3810). — origin of the Matthew Effect name; super-proportional reward accumulation.
- **Gabaix, X. (2009).** "Power Laws in Economics and Finance." *Annual Review of Economics* 1. — Pareto exponent mechanics; the α parameter is a canonical tuning dial.
- **Roll, R. (1986).** "The Hubris Hypothesis of Corporate Takeovers." *Journal of Business* 59(2). — empirical basis for σ-Cred coupling: high-status decision-makers take higher-variance bets.
