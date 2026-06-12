# SiC Games — Stage 1 Blueprint

**Version:** 0.4 (adds §5.2/5.3 — Perception and CostModel abstractions for future-proofing)
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 1 only. The full multi-stage roadmap is at the end of this document for context. Anything not explicitly in Stage 1 must be deferred — see the "Out of scope" and "Deferred TBD" sections.

---

## 0. North Star (read first, every session)

**Eventual goal.** A controlled, variance-matched ABM comparison of two agent populations — *Carbon* (status-coupled decision noise + super-proportional reward partition) and *Silicon* (uniform-temperature noise + egalitarian reward partition) — on identical Sugarscape worlds. The primary observable is *between-run civilizational diversity*: do independent runs of C produce qualitatively different stable societies, while independent runs of Si converge to similar outcomes?

**Falsifiable claim.** Holding environmental conditions and *total decision variance* fixed, C produces strictly greater between-run trait variance than Si on a pre-registered set of dimensions. Failure of this claim (no significant difference, or the opposite pattern) is the project's null result.

**What this project is *not*.** Not a new framework. Not a paradigm-shift on "antifragility." Not a refutation of rational optimization. The closest existing work (Sugarscape, BTH-status models, Klemm-style cultural noise studies, Gigerenzer's ecological rationality) covers most of the conceptual ground. What's open ground is the specific combination: *status-coupled $\sigma$ mechanism + variance-matched controls + between-run diversity as outcome + civilization-scale Sugarscape substrate*.

**Stage 1's role in the North Star.** Stage 1 is *infrastructure*: a working Sugarscape baseline that reproduces canonical results. It is *not* a comparative result and should not be expected to produce one. Its purpose is to verify the substrate is correctly implemented before C dynamics are added in Stage 2.

If at any point the coding agent finds itself implementing C mechanics, Cred state, or Si-vs-C comparisons during Stage 1, **stop and consult the supervisor.** That is scope creep.

**Design discipline (applies to every stage).** Every mechanism added to the model should serve the four-piece novel slice (status-coupled $\sigma$, variance-matched controls, between-run diversity, Sugarscape substrate). Mechanisms that do not serve it are decoration; defer or remove them. *Before designing any new mechanism, consult `LITERATURE.md` (see §10.9) — if the field has already solved a problem you're tempted to reinvent, lift the existing solution rather than write your own.* The eventual paper will be judged on specific quantitative findings (phase diagrams, critical $\kappa$ values, the converging-vs-diverging trait partition), not on the existence of a C/Si difference, which reviewers will largely assume is real before opening the paper. Build toward those quantitative findings, not toward the abstract framing.

---

## 1. Background and motivation

### 1.1 The big question

There is a long tradition in optimization, organizational theory, and evolutionary biology of asking when *noisy, biased, status-driven* agents outperform *efficient, optimization-driven* agents at the collective level. The dichotomy has many names:

- Exploration vs exploitation (March 1991; Sutton & Barto)
- Ecological rationality vs full optimization (Gigerenzer & Brighton 2009)
- Adaptability vs efficiency (Stuart Kauffman, NK landscapes)
- Antifragility vs fragility (Taleb 2012, though contested)

The empirical record at the *individual decision* level is well-developed: simple heuristics often beat full optimization in complex, uncertain environments. The **claim of this project** is that this finding extends to the *civilization* scale, and that one specific mechanism is responsible: **decision-noise coupling to social status**.

### 1.2 The framing

We define two agent populations, both placed on identical environments:

- **Silicon (Si):** rational/greedy decision-making, low individual variance, no status coupling. Optimizes for energy efficiency.
- **Carbon (C):** softmax decision-making with a noise parameter $\sigma$ that increases with accumulated social status (Cred). "Hubris-with-success." Optimizes for adaptability through stochastic exploration.

### 1.3 The hypothesis

**H1.** Holding total environmental conditions and *total decision variance* fixed, the C population will (i) occupy more niche space, (ii) survive higher-volatility perturbations, and (iii) produce more *between-world* diversity across independent runs than the Si population.

**H0.** No significant difference on these metrics.

A critical methodological point: the Si control must be *variance-matched*. Comparing C against zero-noise Si is comparing against a strawman; the field already knows greedy optimizers fail. The honest comparison is *status-coupled noise vs. equivalent-total-variance uniform noise*.

### 1.4 Where this sits relative to prior work

The closest neighbours in the literature:

- **Sugarscape (Epstein & Axtell, 1996)** — the canonical civilization-scale ABM. We lift this as the substrate. Every project of this kind builds on it.
- **Axelrod (1997), "The Dissemination of Culture"** — diversity emerging from local interaction. Klemm et al. (2003) added noise and found a *non-monotonic* effect on diversity. Our project specifically asks whether *status-coupled* noise produces a different functional form than uniform noise.
- **Cliodynamics (Turchin)** — long-run population/inequality dynamics in real historical societies. Notably, Turchin finds stratification *destabilizing*, which is a competing prediction to our "Cred as gravity well" claim.
- **Boyd & Richerson (cultural evolution)** — formal models of imperfect cultural transmission as adaptive in fluctuating environments. Our "heuristic drift" (Stage 2+) is their copy-error rediscovered.

The likely genuine contribution of this project: **a variance-matched comparison of status-coupled noise vs. uniform noise at civilization scale**, plus a specific prediction about which trait dimensions converge across runs and which diversify. The mechanism (status-coupled individual $\sigma$) is unusual in the ABM literature.

---

## 2. Project roadmap (full vision, for context)

| Stage | Goal | Key additions |
| :---- | :--- | :------------ |
| **1** | **Working vanilla Sugarscape. Substrate verified. Simple-Si baseline reproduced.** | Grid + sugar + growback. Greedy agents (= simple Si). Metrics infrastructure. |
| 2 | First comparative result: C vs simple-Si on identical worlds. | Cred state, status-coupled $\sigma$, Matthew reward partition. C decision strategy as second pluggable agent type. |
| 3 | Honest Si baseline: bounded-rational Si replacing greedy Si. | Proper Si decision logic (softmax with variance-matched fixed temperature, optionally Bayesian belief). Three-way comparison. |
| 4 | Environmental perturbations. | Seasonal sugar oscillation, mobile resources, scheduled shocks. |
| 5 | Multi-world parameter sweep. | Connectivity axis (Pangea ↔ Archipelago), batch runner, reproducibility infrastructure. |
| 6 | Statistical framework. | Pre-registered metrics, effect sizes, power analysis, multi-seed ensembles. |
| 7+ | Heuristic drift, biparental reproduction, full 100-world run. | The V1.3 vision. |

**The 100-world Pangea-Archipelago run is the end of the road, not the beginning.** Do not attempt to scope toward it in Stage 1.

---

## 3. Stage 1 scope

### 3.1 In scope

1. **Sugarscape substrate.** 50×50 toroidal grid, twin sugar peaks, growback rule $G_\alpha$ with $\alpha = 1$.
2. **Greedy agent.** Vanilla Epstein-Axtell movement rule $M$. This *is* the simple-Si baseline.
3. **Replacement rule $R$.** Dead agents replaced to maintain population (needed for the canonical wealth distribution to emerge).
4. **Modular architecture** that supports plugging in alternative decision strategies in Stage 2 without refactoring the substrate.
5. **Metrics infrastructure.** Population $N(t)$, wealth Gini $G(t)$, spatial dispersion $\sigma_{\text{spatial}}(t)$, mean wealth, deaths-per-step (broken down by cause).
6. **Visualization.** Side-by-side animation of sugar field and agent positions. Static plots of metrics over time.
7. **Config-driven runs.** Parameters in a YAML/JSON config file, not hard-coded.
8. **Reproducibility.** Seeded RNG; same seed → same trajectory.
9. **Validation against known reference outputs** (see §8).

### 3.2 Out of scope (deferred)

- Cred, status, ego-noise, Matthew rule.
- Bayesian / bounded-rational Si.
- Heuristic vector $H$, genetic drive $\phi$.
- Environmental perturbations (seasons, mines, beasts).
- Multi-world experiments.
- Connectivity sweep.
- Spatial hashing optimization (population ~250 doesn't need it).
- Inheritance / legacy mechanics.
- Sex / culture / trade / combat / disease (Sugarscape chapters 3+).
- Statistical experimental design (power, effect sizes).

These return in later stages. Do not pre-build for them; the architecture (§5) allows clean addition when needed.

---

## 4. Tech stack

- **Language:** Python 3.11+.
- **ABM framework:** **Mesa** (latest stable, currently 2.x). Active project, large ecosystem, the closest match to canonical Sugarscape. There is an existing Mesa-Sugarscape implementation that can serve as a reference; do not just import it blindly, but read it to understand structure before writing your own.
- **Numerics:** NumPy.
- **Data:** pandas for time-series, polars optional.
- **Plotting:** Matplotlib (static), optionally Plotly for interactive. For animation, Matplotlib's `FuncAnimation` is fine.
- **Config:** YAML via PyYAML.
- **Testing:** pytest.
- **Dependency / project management:** `uv` (preferred) or `poetry`. Avoid bare `pip` in a venv if possible.
- **Linting/formatting:** `ruff` (formatter + linter, fast).

---

## 5. Architecture

### 5.1 Modules (the only modules in Stage 1)

```
sic_games/
├── pyproject.toml
├── README.md
├── LITERATURE.md         # log of consulted papers and lifted ideas (§10.9)
├── configs/
│   └── stage1_baseline.yaml
├── src/sic_games/
│   ├── __init__.py
│   ├── world.py          # Sugarscape environment: grid, sugar field, growback
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py       # BaseAgent: shared state (vision, metabolism, age, wealth)
│   │   ├── decision.py   # DecisionLogic protocol
│   │   ├── perception.py # PerceptionBuilder protocol + LocalVisionPerception (Stage 1)
│   │   ├── costs.py      # CostModel protocol + MetabolicOnly (Stage 1)
│   │   └── strategies/
│   │       ├── __init__.py
│   │       └── greedy.py # GreedyMaximizer (vanilla Sugarscape M)
│   ├── metrics.py        # Gini, dispersion, population stats
│   ├── report.py         # generate_report() — standard run report (§14)
│   ├── visualize.py      # Animation + time-series plots
│   ├── run.py            # Single-run driver
│   └── config.py         # Config loading + validation (use pydantic or attrs)
├── tests/
│   ├── test_world.py
│   ├── test_growback.py
│   ├── test_greedy_decision.py
│   ├── test_perception.py
│   ├── test_costs.py
│   └── test_metrics.py
└── notebooks/
    └── stage1_validation.ipynb   # interactive exploration of results
```

### 5.2 Three pluggable abstractions

The substrate stays fixed; agent behaviour is determined by three swappable strategies. Stage 1 implements only the trivial version of each, but the abstractions exist from day one so Stage 2–7 extensions are pure *additions*, never refactors.

#### Abstraction A — `DecisionLogic` (what the agent decides to do)

```python
# src/sic_games/agents/decision.py
from typing import Protocol
from random import Random

class DecisionLogic(Protocol):
    """How an agent picks its next action, given what it perceives.

    Stage 1: GreedyMaximizer (= simple Si baseline).
    Stage 2: CarbonDecision (status-coupled softmax).
    Stage 3: BoundedRationalSi.
    Stage 7+: BayesianDecision, HeuristicDriftDecision, etc.
    """
    def select_target(
        self,
        agent: "BaseAgent",
        perception: "Perception",
        rng: Random,
    ) -> tuple[int, int]:
        """Return the (x, y) grid cell the agent will move to this step."""
        ...
```

Note the signature change from a naive "agent + world" form: the agent receives a `Perception` object, not raw world access. This isolates *what the agent knows* from *what physically exists*.

#### Abstraction B — `Perception` (what the agent sees / has been told)

```python
# src/sic_games/agents/perception.py
from typing import Protocol

class PerceptionBuilder(Protocol):
    """Constructs an agent's perception from world + (optionally) shared info.

    Stage 1: LocalVisionPerception — sees only own visible cells.
    Stage 5+: SharedVisionPerception — additionally receives messages
              from neighboring agents within communication range.
    Stage 7+: StigmergyPerception — pheromone trails, gossip graphs, etc.
    """
    def build(self, agent: "BaseAgent", world: "World") -> "Perception":
        ...
```

The `Perception` object is a frozen dataclass containing whatever the agent has access to *this step*: visible cells, sugar values, neighbor positions, received signals, etc. Stage 1's `Perception` contains only the locally visible cells and their sugar levels. Stage 5+'s `Perception` can additionally include shared info, with no change required to any existing `DecisionLogic` implementation that ignores the new fields.

This is the key extensibility hinge for information-sharing experiments: vary the `PerceptionBuilder` to control the information regime (local / regional / global / pheromone / gossip), independently of the decision logic and cost model.

#### Abstraction C — `CostModel` (what activities cost)

```python
# src/sic_games/agents/costs.py
from typing import Protocol

class CostModel(Protocol):
    """Computes per-step energetic cost for an agent's activities.

    Stage 1: MetabolicOnly — cost = m_i (constant per agent).
    Stage 4+: ActivityVariableCost — additive costs for moving, deciding,
              communicating, etc., each tunable independently.
    """
    def step_cost(
        self,
        agent: "BaseAgent",
        actions_taken: dict,   # e.g. {"moved": True, "messages_sent": 3, ...}
    ) -> float:
        ...
```

Stage 1's `MetabolicOnly` returns `agent.metabolism` regardless of activity dict. Stage 4+ replaces it with a richer model, e.g.:

$$\text{cost} = m_i + \beta_{\text{move}} \cdot \mathbb{1}_{\text{moved}} + \beta_{\text{send}} \cdot n_{\text{messages}} + \beta_{\text{think}} \cdot |J_i|$$

where $|J_i|$ is the number of candidates evaluated, $n_{\text{messages}}$ is messages sent this step, etc. This lets us run the *"Si is energetically expensive"* experiment as a parameter sweep over the $\beta$'s, without touching agent code.

#### Step structure with the three abstractions

Each agent step now decomposes cleanly:

1. **Perceive:** `perception = perception_builder.build(agent, world)`
2. **Decide:** `target = decision_logic.select_target(agent, perception, rng)`
3. **Act:** agent moves to `target`, harvests sugar (world updates)
4. **Pay:** `agent.wealth -= cost_model.step_cost(agent, actions_taken)`
5. **Age and check for death.**

For Stage 1, this looks like simple Sugarscape: local vision, greedy decision, metabolic-only cost. For Stage 5+, the substrate doesn't change; only the strategy classes are swapped (via config).

### 5.3 What the abstractions enable

The three abstractions cover the future requirements explicitly raised so far:

| Requirement | Stage | Mechanism |
| :---------- | :---- | :-------- |
| Pluggable agent decision rules (C, Si variants) | 2, 3 | New `DecisionLogic` class |
| Status-coupled noise | 2 | New `DecisionLogic` class |
| Information sharing (local → global) | 5+ | New `PerceptionBuilder` class |
| Variable energetic costs per activity | 4+ | New `CostModel` class |
| Si higher metabolism as sweep variable | 4+ | New `CostModel` with population-dependent $m$ |
| Pheromone / stigmergy | 7+ | New `PerceptionBuilder` (+ world hook) |
| Bayesian Si with beliefs | 7+ | New `DecisionLogic` + agent state addition |

What is *not* yet pluggable in this architecture, and may need additional hooks in later stages:

- **Reproduction strategy.** Stage 1's replacement rule R is wired directly into the run loop. Stage 7 (sexual reproduction) will need a `ReproductionRule` protocol added at that point. Flag, defer.
- **Environmental perturbations.** Stage 4's seasonal/shock dynamics will need a `WorldPerturbation` hook on `world.py`. Trivial to add then, but not in Stage 1.
- **Multi-world batch runs.** Stage 5 needs a `BatchRunner` that spawns paired `World` instances with linked RNG seeds (for common-random-numbers comparisons). Stage 1's `run.py` is single-run; a `batch.py` lifts on top without touching the single-run code.

The point: **none of these future additions require touching `world.py`, `agents/base.py`, or the run loop.** They're all clean drop-ins to the strategy slots or new sibling modules. That's the test the architecture passes.

### 5.4 Loop structure

A single simulation step is exactly the Epstein-Axtell scheduling:

1. **Environmental step** ($G_\alpha$): every cell with sugar below capacity gets +$\alpha$ sugar (clamped at capacity).
2. **Agent step** ($M$): all agents processed in **random order** (re-shuffled each step); each runs the five-substep cycle from §5.2 (perceive → decide → act → pay → age). For Stage 1, this collapses to "look within vision, pick the best visible unoccupied cell (greedy argmax), move, harvest, subtract metabolism, age."
3. **Replacement step** ($R$): agents that died this step (wealth ≤ 0 or age ≥ max_age) are removed; for each death, a new agent of age 0 is spawned at a random unoccupied cell with fresh random attributes from the canonical distributions.
4. **Metrics:** every step (or every $k$ steps for speed), compute and log $N$, Gini, dispersion, mean wealth, deaths.

Use Mesa's `RandomActivation` scheduler or roll your own; the random shuffle is essential for correctness.

---

## 6. Math specification (vanilla Sugarscape, chapter 2)

This section is deliberately explicit so the coding agent doesn't have to guess.

### 6.1 Environment

- Grid: 50×50, **toroidal** (wraps around both directions). Each cell indexed by $(i, j)$ with $i, j \in \{0, ..., 49\}$.
- Each cell has two scalar attributes: sugar level $s(i, j, t) \ge 0$ and sugar capacity $c(i, j)$, where $0 \le s(i, j, t) \le c(i, j)$ at all times.
- Sugar capacity field has **two peaks** at $(10, 40)$ and $(40, 10)$ (using the Agents.jl convention). The capacity at $(i, j)$ is:

$$c(i, j) \;=\; \max\!\Big(0,\; c_{\max} - \big\lfloor d(i, j)\,/\,k \big\rfloor\Big)$$

where $d(i, j)$ is the toroidal distance from $(i, j)$ to the *nearest* peak, $c_{\max} = 4$, and $k = 6$ is a band width parameter. Use Euclidean toroidal distance (i.e., minimum over the 9 possible offsets due to wrap-around).

- Initialization: $s(i, j, 0) = c(i, j)$ everywhere (cells start full).

### 6.2 Growback rule $G_\alpha$

For each cell $(i, j)$ at every step:

$$s(i, j, t+1) \;=\; \min\!\big(s(i, j, t) + \alpha,\; c(i, j)\big), \qquad \alpha = 1$$

### 6.3 Agent attributes (drawn once at birth, fixed for life)

| Attribute | Symbol | Distribution |
| :-------- | :----- | :----------- |
| Vision | $v_i$ | discrete uniform on $\{1, 2, ..., 6\}$ |
| Metabolic rate | $m_i$ | discrete uniform on $\{1, 2, 3, 4\}$ |
| Maximum age | $\tau_i$ | discrete uniform on $\{60, ..., 100\}$ |
| Initial wealth | $w_i(0)$ | discrete uniform on $\{5, ..., 25\}$ |

Mutable state: position $(x_i, y_i)$, wealth $w_i(t)$, age $a_i(t)$.

### 6.4 Movement rule $M$ (greedy / simple Si — Stage 1 strategy)

For an agent at $(x, y)$ with vision $v$:

1. **Candidate cells:** all *unoccupied* cells at $(x', y')$ such that $x' = x$ and $|y' - y|_{\text{tor}} \le v$, OR $y' = y$ and $|x' - x|_{\text{tor}} \le v$. **Von Neumann neighborhood** (4 cardinal directions only), *including the agent's current cell*. Toroidal distance.
2. **Filter:** among candidates, find those with maximum sugar level $s(x', y', t)$.
3. **Tie-break:** if multiple candidates tie on sugar, pick the one with smallest toroidal distance to $(x, y)$. If multiple tie on both, choose uniformly at random.
4. **Move:** set agent's position to the chosen cell.
5. **Harvest:** wealth $w_i \mathrel{+}= s(x_{\text{new}}, y_{\text{new}}, t)$; then $s(x_{\text{new}}, y_{\text{new}}, t) \leftarrow 0$.
6. **Metabolize:** $w_i \mathrel{-}= m_i$.
7. **Age:** $a_i \mathrel{+}= 1$.
8. **Death check:** if $w_i \le 0$ or $a_i \ge \tau_i$, mark for replacement.

**Important:** "two agents cannot occupy the same cell" is enforced. The candidate filter excludes occupied cells (other than the agent's own).

### 6.5 Replacement rule $R$

For each agent that died this step:

1. Remove it from the world.
2. Spawn a replacement: new agent with $v, m, \tau, w(0)$ freshly drawn from the canonical distributions (§6.3), age 0, placed at a uniformly random *unoccupied* cell.

This keeps total population constant at $N = 250$. The canonical wealth-distribution result depends on this rule being active.

### 6.6 Scheduling

Each simulation step, in order:

1. Apply $G_\alpha$ to all cells (vectorized).
2. Shuffle agent list. Apply $M$ to each agent in shuffled order (sequential, not parallel — order matters because of the unoccupied-cell constraint).
3. Apply $R$ to all dead agents.
4. Record metrics.

---

## 7. Configuration

A single YAML file `configs/stage1_baseline.yaml` holds all parameters. Example:

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
  vision_dist: [1, 6]            # uniform discrete inclusive
  metabolic_rate_dist: [1, 4]
  max_age_dist: [60, 100]
  initial_wealth_dist: [5, 25]
decision:
  strategy: "greedy"             # Stage 1: only "greedy" is implemented
run:
  n_steps: 1000
  metrics_every: 1
  output_dir: "outputs/stage1_baseline_seed42"
visualization:
  animate: true
  frames_per_save: 5
  save_static_plots: true
```

A config schema (using `pydantic`) validates the file and gives clear errors on missing/wrong fields.

---

## 8. Metrics and outputs

### 8.1 Per-step metrics (logged to a long-format CSV / parquet)

| Metric | Definition |
| :----- | :--------- |
| `step` | simulation step |
| `population` | count of living agents |
| `mean_wealth` | mean $w_i$ over living agents |
| `gini_wealth` | Gini coefficient of $\{w_i\}$ |
| `spatial_dispersion` | std of agent positions, averaged over $x$ and $y$ |
| `mean_age` | mean $a_i$ |
| `deaths_starvation` | deaths from $w \le 0$ this step |
| `deaths_senescence` | deaths from $a \ge \tau$ this step |
| `total_sugar` | $\sum_{ij} s(i, j, t)$ |

### 8.2 Static plots saved at run end

- $N(t)$ — population over time
- Gini of wealth over time
- Spatial dispersion over time
- Wealth histogram at $t = 0, t = T/2, t = T$
- Final agent-position heatmap on the sugar capacity field

### 8.3 Animation

- Side-by-side: sugar field (heatmap) and agent positions, one frame per `frames_per_save` steps. Saved as `.mp4` or `.gif`.

### 8.4 Output structure

```
outputs/stage1_baseline_seed42/
├── config.yaml          # copy of the config used
├── metrics.parquet      # per-step metrics
├── final_state.parquet  # final agent states
├── plots/
│   ├── population.png
│   ├── gini.png
│   ├── dispersion.png
│   ├── wealth_histogram.png
│   └── final_positions.png
└── animation.mp4
```

---

## 9. Success criteria (Stage 1 done = all of these pass)

The reference Sugarscape (Epstein-Axtell ch. 2 with M, $G_1$, R) has known qualitative results. Stage 1 is considered complete only when all of the following are observed for `seed=42` and the canonical parameters above:

1. **Population stability.** $N(t)$ does not crash to extinction and does not explode. Replacement rule keeps it at ~250. (Trivially satisfied if R is implemented correctly.)
2. **Skewed wealth distribution emerges.** The wealth histogram at $t=1000$ is visibly right-skewed (long tail of rich agents), not uniform. **Gini coefficient of wealth in the range $[0.4, 0.6]$** at steady state. This is the canonical "Sugarscape produces inequality" result.
3. **Spatial clustering on peaks.** At $t = 1000$, agent density is visibly concentrated on the two sugar peaks. Quantitatively: more than 50% of living agents are within distance 10 of one of the two peaks.
4. **Reproducibility.** Two runs with the same seed produce identical metrics traces. Different seeds produce qualitatively similar but quantitatively different results.
5. **Tests pass.** All pytest tests in `tests/` pass. Minimum tests required:
   - `test_world`: capacity field is correctly computed, growback obeys cap.
   - `test_growback`: $G_\alpha$ adds exactly $\alpha$ per step until capped.
   - `test_greedy_decision`: argmax-with-tiebreak picks the correct cell on a constructed example.
   - `test_metrics`: Gini coefficient matches scipy/known reference values on test inputs.

If any of (1)–(4) fail on the canonical parameters, the substrate is incorrect and must be fixed before declaring Stage 1 done. The Gini band $[0.4, 0.6]$ is the most diagnostic — if it's far outside, something in $M$, $R$, or wealth accounting is wrong.

---

## 10. Coding-agent directives

These are instructions for Claude Code (or whichever agent is doing the implementation).

1. **Read before coding.** Before writing any source files, read:
   - This blueprint, end to end. The North Star (§0) is mandatory context for every session.
   - The JASSS appendix: `https://jasss.soc.surrey.ac.uk/12/1/6/appendixB/EpsteinAxtell1996.html` — formal model description.
   - The Mesa documentation, at minimum the `mesa.Model`, `mesa.Agent`, and `mesa.space.MultiGrid` pages.
   - Skim the Agents.jl Sugarscape page for parameter values and structure: `https://juliadynamics.github.io/Agents.jl/v4.1/examples/sugarscape/`
2. **Propose a plan.** Before writing code, produce a short plan: file-by-file structure, key classes, what each test will check. Confirm with the human supervisor.
3. **Implement bottom-up.** World and growback first, then agent base, then greedy decision, then run loop, then metrics, then visualization. Each layer has tests before moving up.
4. **Validate against the success criteria as you go.** Don't wait until everything is built to check that Gini lands in $[0.4, 0.6]$ — run early, run often, with a small grid first (e.g., 20×20, 40 agents, 200 steps) for fast iteration.
5. **If a result deviates from the success criteria,** stop and investigate before adding more code. Common failure modes:
   - Gini too low → wealth accounting double-counts or movement rule ties favor the spread of agents.
   - Gini too high → metabolism not applied, or peaks too dominant.
   - Population unstable → replacement rule misfiring on death detection.
6. **Do not invent features.** If something is in §3.2 (out of scope) or §11 (deferred), do not pre-build it. Flag it as future work and continue with Stage 1 scope only. **Scope creep is the single biggest failure mode for this kind of project.** When in doubt, do less.
7. **Ask before architectural deviations.** If you find the modular structure in §5 is wrong for some reason, surface this to the human supervisor before refactoring.
8. **Random seeds and reproducibility.** Every stochastic call must go through a seeded `numpy.random.Generator` or Python `random.Random`. No bare `random.random()` or `np.random.X` calls. Seed comes from the config.
9. **Maintain a `LITERATURE.md` at the repo root.** When any paper, model, or implementation is consulted during development, log it in `LITERATURE.md` with: full citation, what was lifted/learned from it, and what was rejected as inappropriate for this project. This file builds the positioning document for the eventual paper and prevents reinventing already-published mechanisms. Seed entries: Epstein & Axtell (1996), Klein et al. (2024) on common-random-numbers, Klemm et al. (2003), Gigerenzer & Brighton (2009), and the BTH papers (Galam 2018-style status models).
10. **Pre-registration discipline (relevant from Stage 2 onwards).** When defining metrics for a comparative run, the metric list and expected-direction-of-effect must be committed (to the repo, with timestamp) *before* the runs are executed. No post-hoc metric selection. For Stage 1 this is light (success criteria are already pinned in §9); the discipline matters most when comparison runs begin.
11. **Common random numbers for paired comparisons (relevant from Stage 2 onwards).** When comparing two conditions (C vs Si, parameter A vs parameter B) on the same world, both runs must reuse the same RNG seed sequence for environmental stochasticity (sugar field initialization, growback if stochastic, agent attribute draws). Only the decision-noise RNG draws differ between conditions. This is the Klein et al. (2024) CRN method and is the right hammer for variance-matched comparison.
12. **Report negative results.** If a run *fails* to reproduce a canonical result, log it, attempt to diagnose, and report in the run's `report.md` Notes section. Do not silently rerun until success. Reproducible failure is more informative than unreproduced success.

---

## 11. Deferred items (explicit TBD list)

Cataloged here so the coding agent does not silently invent them, and so they're easy to pick up in later stages:

- **Cred** $\mathcal{C}$, **status-coupled noise** $\sigma(\mathcal{C})$, **Matthew reward partition.** → Stage 2.
- **Si bounded-rational variant.** → Stage 3.
- **Environmental perturbations** (seasonal sugar oscillation, mobile resources, shocks). → Stage 4.
- **Multi-world / parameter sweep infrastructure.** → Stage 5.
- **Statistical experimental design** (effect sizes, power, pre-registration). → Stage 6.
- **Heuristic vector $H$, genetic drive $\phi$, biparental reproduction.** → Stage 7+.
- **Connectivity sweep** (Pangea → Archipelago). → Stage 7+.
- **Inheritance / legacy mechanics.** → Stage 7+.
- **Sex / culture / trade / combat / disease** (Sugarscape ch. 3+ rules). → As needed by experimental design.
- **Performance optimization** (spatial hashing, JIT, parallel runs). → When population × steps actually demands it. Stage 1's 250 agents × 1000 steps does not.

---

## 12. References

**Primary:**
- Epstein, J. M. & Axtell, R. L. (1996). *Growing Artificial Societies: Social Science from the Bottom Up.* MIT Press / Brookings.
- Epstein, J. M. (2006). *Generative Social Science: Studies in Agent-Based Computational Modeling.* Princeton University Press. [Open PDF here.](http://www.cs.unibo.it/babaoglu/courses/cas/papers/Epstein%20-%202006%20-%20Generative%20Social%20Science%20Studies%20in%20Agent-Based%20Computational%20Modeling.pdf) — the best accessible substitute for the 1996 book; covers Sugarscape extensively.
- JASSS formal appendix (Epstein & Axtell 1996, chapter 2): `https://jasss.soc.surrey.ac.uk/12/1/6/appendixB/EpsteinAxtell1996.html`
- Agents.jl Sugarscape implementation: `https://juliadynamics.github.io/Agents.jl/v4.1/examples/sugarscape/`

**Theoretical context (read for Stages 2+):**
- March, J. G. (1991). "Exploration and Exploitation in Organizational Learning." *Organization Science* 2(1).
- Axelrod, R. (1997). "The Dissemination of Culture." *Journal of Conflict Resolution* 41(2).
- Klemm, K. et al. (2003). "Global culture: A noise-induced transition in finite systems." *Physical Review E* 67.
- Gigerenzer, G. & Brighton, H. (2009). "Homo Heuristicus: Why Biased Minds Make Better Inferences." *Topics in Cognitive Science* 1.
- Turchin, P. (2003). *Historical Dynamics: Why States Rise and Fall.* Princeton.
- Boyd, R. & Richerson, P. J. (1985). *Culture and the Evolutionary Process.* University of Chicago Press.

---

## 13. Open questions (for the human supervisor, not the coding agent)

Status as of blueprint v0.2 — see §15 for the locked Stage 2 / Stage 3 design commitments.

| Q | Topic | Status |
| :- | :---- | :----- |
| Q1 | Cred mechanics — accumulation sources | **Resolved** (see §15). Cred from joint-task events only (option *a*); Stage 2 introduces minimal joint-task mechanic. |
| Q2 | Matthew Power $\alpha$ value | **Deferred** — parameter to sweep, not a design decision. Default 1.5; sweep range $[1.0, 2.0]$. |
| Q3 | Honest-Si form | **Resolved** (see §15). Same softmax as C, fixed variance-matched temperature, no Cred state, egalitarian sharing, local vision. |
| Q4 | Variance-matching protocol | **Deferred** — requires Stage 2 data (mean decision entropy of C at quasi-steady-state). Settle when first C runs exist. |

---

## 14. Reporting protocol

Every run, regardless of stage, produces a standardized report under its output directory. This is the contract by which the coding agent returns results to the human supervisor for chat-based review.

### 14.1 The report.py module

`src/sic_games/report.py` exposes one function:

```python
def generate_report(
    run_dir: Path,
    config: Config,
    metrics_df: pd.DataFrame,
    success_checks: list[SuccessCheck],
    agent_notes: str = "",
) -> Path:
    """Generate report.md + referenced PNG plots in run_dir.
    Returns the path to report.md.
    """
```

A `SuccessCheck` is a small dataclass: criterion description (string), pass/fail bool, observed value (string or numeric), threshold (string). Each stage supplies its own list of `SuccessCheck` instances (for Stage 1, see §9).

The report module is shared across stages — only the success-criteria list changes.

### 14.2 The report.md schema (fixed across stages)

```markdown
# Run report: <run_name>

**Seed:** 42 | **Steps:** 1000 | **Strategy:** greedy | **Date:** YYYY-MM-DD

## TL;DR
- [✓ or ✗] All success criteria met
- Final population: 250 | Final Gini: 0.47 | Mean dispersion: 8.3

## Success criteria
| Criterion | Status | Observed | Threshold |
|---|---|---|---|
| Population stable | ✓ | 250 ± 0 | [200, 300] |
| Gini in [0.4, 0.6] | ✓ | 0.47 ± 0.02 | [0.4, 0.6] |
| Agents near peaks (>50%) | ✓ | 68% | >50% |
| Reproducibility | ✓ | identical trace | identical |

## Key metrics (final 100 steps, mean ± std)
| Metric | Value |
|---|---|
| Population | 250.0 ± 0.0 |
| Mean wealth | 18.3 ± 1.1 |
| Gini wealth | 0.47 ± 0.02 |
| Spatial dispersion | 8.3 ± 0.4 |
| Deaths/step (starvation) | 1.2 |
| Deaths/step (senescence) | 1.8 |

## Plots
![Population over time](plots/population.png)
![Gini over time](plots/gini.png)
![Wealth distribution](plots/wealth_histogram.png)
![Final positions](plots/final_positions.png)

## Notes
<free-form notes from the implementing agent: anomalies, observations,
deviations from the expected, anything the supervisor should look at>

## Configuration
<copy of the config YAML, for reproducibility>
```

### 14.3 Output directory layout

```
outputs/<run_name>/
├── report.md           # primary deliverable for chat upload
├── config.yaml         # echoed run config
├── metrics.parquet     # full per-step metrics
├── final_state.parquet # final agent states
└── plots/
    ├── population.png
    ├── gini.png
    ├── dispersion.png
    ├── wealth_histogram.png
    └── final_positions.png
```

### 14.4 The upload contract

To pass results back to chat: upload `report.md` plus the contents of `plots/` together in one message. The relative paths in `report.md` resolve when the supervisor views the attached images alongside the markdown text.

This is the standard contract for every run. Do not deviate from it — consistency across runs is what makes the report immediately legible without ramp-up. If the agent wants to add new diagnostic outputs (always allowed, often useful), they go in the `Notes` section or as additional plots referenced from `Notes`, not in a different file.

---

## 15. Stage 2 & Stage 3 design commitments

This section is **not** for Stage 1 implementation. It captures the locked design forms for Stage 2 (C decision strategy) and Stage 3 (honest Si decision strategy), so they're recorded in one place. The coding agent should **not** build these in Stage 1; this section exists so the Stage 2 blueprint, when written, can lift these forms directly.

### 15.1 Shared substrate (applies equally to C and Si)

- **Same Sugarscape physics:** grid, sugar field, growback rule $G_\alpha$, von Neumann movement neighborhood, "two agents can't share a cell," replacement rule $R$ to maintain population.
- **Same biology:** vision $v_i$, metabolism $m_i$, max-age $\tau_i$, initial wealth $w_i(0)$ all drawn from the canonical distributions at birth (see §6.3). Same for both populations.
- **Same vision regime:** local vision (each agent sees only within its own vision radius). No information pooling, no hive-mind. Same for both populations.
- **Same reproduction:** non-strategic, governed by the substrate's replacement rule. Same for both populations.
- **Same softmax decision logic:** the difference is in the *parameters* and *utility terms*, not the structure.

The C-vs-Si distinction is **only** in the two knobs below.

### 15.2 Knob 1 — Decision noise structure (the σ form)

**C agents:** ego-noise saturates with status.
$$\sigma_i^{(C)} \;=\; \sigma_{\text{base}} \;+\; \kappa \cdot \tanh\!\big(\mathcal{C}_i / \mathcal{C}^{*}\big)$$
- $\sigma_{\text{base}}$: baseline exploration noise.
- $\kappa$: maximum *additional* noise hubris adds.
- $\mathcal{C}^{*}$: Cred scale where hubris is at half max.

**Si agents:** fixed temperature, no status coupling.
$$\sigma_i^{(Si)} \;=\; \sigma_{\text{Si}} \;\; \text{(constant across agents and time)}$$
- $\sigma_{\text{Si}}$ calibrated so the population-mean per-step decision entropy of Si matches C's at quasi-steady-state (Q4 — calibration protocol TBD until Stage 2 data exists).

### 15.3 Knob 2 — Reward partition shape (in joint-task events with cluster $\mathfrak{C}$)

**C agents:** super-proportional / Matthean.
$$\Delta\mathcal{R}_i^{(C)} = \mathcal{R}_{\text{tot}} \cdot \frac{(\mathcal{C}_i + \varepsilon)^{\alpha}}{\sum_{j\in\mathfrak{C}} (\mathcal{C}_j + \varepsilon)^{\alpha}}, \qquad \Delta\mathcal{C}_i^{(C)} = \mathcal{C}_{\text{tot}} \cdot \frac{(\mathcal{C}_i + \varepsilon)^{\alpha}}{\sum_{j\in\mathfrak{C}} (\mathcal{C}_j + \varepsilon)^{\alpha}}$$
- $\alpha \in [1.0, 2.0]$, default 1.5. Sweep target.
- $\varepsilon \approx 0.01$ Laplace smoothing.

**Si agents:** egalitarian split.
$$\Delta\mathcal{R}_i^{(Si)} = \mathcal{R}_{\text{tot}} / |\mathfrak{C}|$$
- No Cred state for Si — the $\mathcal{C}_{\text{tot}}$ side of the partition does not apply.

### 15.4 Cred state (C agents only)

- Scalar per agent: $\mathcal{C}_i \in \mathbb{R}_{\ge 0}$, initialized to 0 at birth.
- Update: $\mathcal{C}_i(t+1) = (1 - \delta) \mathcal{C}_i(t) + \Delta\mathcal{C}_i(t)$.
- $\Delta\mathcal{C}_i(t)$ is zero in any step where the agent did not participate in a joint-task event.
- $\delta \in (0, 1)$ per-step decay; value TBD (start in 0.005–0.02 range).

### 15.5 Sources of Cred (option *a* — locked)

- Cred is generated *only* from **joint-task events** with cluster size $|\mathfrak{C}| \ge 2$.
- Solo harvesting (one agent on a cell) generates no Cred.
- Stage 2 must therefore introduce a minimal joint-task event type. Simplest implementation: when $\ge 2$ agents are within distance $d$ of a sugar cell with capacity above a threshold, the cell becomes a joint task with $E_a^{\text{eff}} = E_a \cdot \exp(-\gamma \mathcal{S}(\mathfrak{C}))$ reduction and Matthew partition of payoff. Full V1.3-style Mines and Great Beasts defer to Stage 4.

### 15.6 Utility function and weights (C agents)

Per-task utility for C agent $i$ choosing action $j$:
$$U_{ij}^{(C)} \;=\; w_R^{(i)} \cdot \widehat{\Delta\mathcal{R}}_{ij} \;+\; w_C^{(i)} \cdot \widehat{\Delta\mathcal{C}}_{ij}$$

Per-task utility for Si agent $i$ (no Cred term):
$$U_{ij}^{(Si)} \;=\; w_R \cdot \widehat{\Delta\mathcal{R}}_{ij}$$

**Weight assignment (Stage 2 lock-in):**

- A new per-agent attribute $\phi_i \in [0, 1]$ drawn at birth from a truncated normal: $\phi_i \sim \mathcal{N}(0.5, \sigma_\phi^2)$ clipped to $[0, 1]$. Distribution parameters TBD; start with $\sigma_\phi = 0.2$.
- $\phi_i$ is constant for the agent's lifetime. Equivalent in spirit to V1.3's "Rationalist (0) ↔ Pretender (1)" axis.
- For C agents: $w_C^{(i)} = \phi_i$, $w_R^{(i)} = 1 - \phi_i$. Born-rationalist agents weight sugar; born-egomaniac agents weight Cred.
- For Si agents: $\phi_i$ exists in state for code symmetry but is ignored in the utility (Si has no Cred term).

**Status amplification (Stage 3+ refinement, NOT in Stage 2):**

When Stage 3 introduces it, $w_C$ becomes time-varying and status-amplifying:
$$w_C^{(i)}(t) \;=\; \phi_i \cdot f(\mathcal{C}_i(t))$$
for some monotone-increasing $f$ (e.g., $f(\mathcal{C}) = 1 + \beta \tanh(\mathcal{C}/\mathcal{C}^{**})$). Born-egomaniacs who succeed at accumulating Cred become *more* status-seeking; born-rationalists stay rationalists regardless. Form to be locked when Stage 3 is planned.

### 15.7 Estimated gains $\widehat{\Delta\mathcal{R}}_{ij}, \widehat{\Delta\mathcal{C}}_{ij}$

For Stage 2, the simplest reasonable estimates:

- $\widehat{\Delta\mathcal{R}}_{ij} = s(x_j, y_j, t)$ for solo move to cell $j$ (sugar at the target cell, just like vanilla Sugarscape).
- For joint-task candidates, $\widehat{\Delta\mathcal{R}}_{ij}$ uses the agent's predicted Matthew share if joining the cluster (requires the agent to know its own and visible neighbors' Cred — which it does, within local vision).
- $\widehat{\Delta\mathcal{C}}_{ij}$ is zero for solo moves; for joint-task candidates, equals the agent's predicted Matthew share of $\mathcal{C}_{\text{tot}}$.

This is the simplest viable Stage 2 specification. Richer estimators (multi-step lookahead, discounted future returns, etc.) can be considered later but should NOT be added prematurely.

### 15.8 What is NOT locked yet

- Specific parameter *values*: $\sigma_{\text{base}}, \kappa, \mathcal{C}^{*}, \delta, \alpha, \varepsilon, \sigma_\phi$, the joint-task detection distance $d$, the joint-task barrier $E_a$ and reduction strength $\gamma$. All are sweep / tuning targets for Stage 2.
- $\sigma_{\text{Si}}$ calibration (Q4 — variance-matching protocol). Needs Stage 2 data.
- Stage 3 status-amplification function $f$.
- Heuristic vector $H$, biparental reproduction, environmental perturbations, multi-world infrastructure. All Stage 4+.

### 15.9 Summary table — the two knobs

| | Si | C |
| :--- | :--- | :--- |
| Substrate | shared | shared |
| Biology (vision, metabolism, age, wealth) | shared | shared |
| Vision regime | local | local |
| Reproduction rule | shared (substrate) | shared (substrate) |
| Decision logic | softmax | softmax |
| **Decision temperature** | **fixed $\sigma_{\text{Si}}$** | **$\sigma_{\text{base}} + \kappa \tanh(\mathcal{C}_i/\mathcal{C}^{*})$** |
| Cred state | none (or ignored) | scalar with decay |
| Utility includes Cred term | no | yes ($w_C^{(i)} = \phi_i$) |
| **Joint-task reward partition** | **egalitarian** ($1/|\mathfrak{C}|$) | **Matthew** ($(\mathcal{C}+\varepsilon)^{\alpha}$ weighted) |
| Born-trait $\phi_i$ | ignored | weights Cred utility |

The two bolded rows are the *only* mechanism differences. Everything else is the same. This is what makes the comparison interpretable.
