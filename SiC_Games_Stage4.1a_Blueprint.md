# SiC Games — Stage 4.1a Blueprint: Variable Population

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 4.1a only. Remove fixed-N constraint. Simplest possible birth rule.
**Prerequisite:** Stage 4 complete. ROADMAP.md C/Si distinction table reviewed.

---

## 0. North Star (read first, every session)

**Stage 4.1a goal:** decouple births from deaths. Population N(t) is now a dynamic
variable constrained only by the world's carrying capacity — sugar physics, not a
fixed replacement rule. The simplest possible birth rule is implemented first.
No efficiency ramp, no support pool, no Si Cred yet. Just: does the population
find a stable attractor without the fixed-N safety net?

**Why this matters for H1(ii).** Stage 4 showed N=250 throughout all 5 seasons
at A=0.5 because every death was immediately replaced. Population-level resilience
was invisible. Variable population makes N(t) the primary H1(ii) diagnostic —
C and Si populations can now genuinely differ in their trough survival.

**The carrying capacity is enforced by the world, not by code.** Finite grid,
finite sugar capacity, finite growback rate. No artificial population cap is
needed or wanted. If birth parameters are miscalibrated and population explodes
transiently, agents starve and the system self-corrects. This is the mechanism
working as intended.

**What Stage 4.1a is not.** It is not the full life history model. No age-efficiency
ramp (Stage 4.1b), no support pool (Stage 4.1c), no Cred-modulated birth (deferred),
no wealth inheritance active (λ=0 default from Stage 4.1a config). One thing:
variable population with minimal birth rule.

**Read ROADMAP.md C/Si distinction table before touching any reproduction code.**
The Stage 3.3 biparental-Si error (BUG-002) happened because this check was skipped.

**Failure modes to watch for:**
- Population explosion: N(t) grows unboundedly because birth rate >> death rate.
  Diagnostic: N(t) > 500 sustained for > 100 steps. This indicates birth
  parameters are too generous — reduce P_birth_max.
- Population collapse to zero in null control (static world): if C or Si
  collapses in the absence of perturbation, birth rate is too low. Increase
  P_birth_max or lower θ_birth.
- Oscillatory instability: N(t) oscillates wildly (>±50% amplitude) even in
  static world. Indicates birth/death rates are tuned at the edge of stability.
  Increase velocity_tau for birth smoothing.
- Si reproduction using biparental logic: **immediate halt**. Check
  ReproductionCoordinator is C/Si-aware. See BUG-002.

---

## 1. What changes in Stage 4.1a

### 1.1 Remove fixed-N replacement rule

The Stage 1 replacement rule R (every death immediately replaced by a fresh agent)
is **disabled**. Deaths are no longer compensated automatically.

The run loop death handling changes from:
```python
# OLD (Stage 1 replacement rule)
if agent.is_dead():
    world.remove(agent)
    world.add(fresh_agent())  # immediate replacement
```
to:
```python
# NEW (Stage 4.1a)
if agent.is_dead():
    world.remove(agent)
    # no automatic replacement — births handled separately
```

A config flag controls this:
```yaml
population:
  mode: "fixed"      # Stage 1 behavior — replacement on every death
  mode: "dynamic"    # Stage 4.1a — births and deaths decoupled
```

Setting `mode: "fixed"` recovers all prior behavior exactly. All Stage 1-4
configs continue to work unchanged.

### 1.2 Birth rule (C agents)

Each step, after deaths are processed, each living C agent within reproductive
age window attempts birth with probability P_birth:

$$P_{\text{birth}}^C(w_i, a_i) = \begin{cases}
0 & w_i < \theta_{\text{sub}} \text{ or } a_i \notin [a_{\text{rep\_min}}, a_{\text{rep\_max}}] \\
P_{\text{max}} & \theta_{\text{sub}} \le w_i < \bar{w}(t) \cdot r_{\text{stress}} \\
P_{\text{max}} \cdot \exp\!\left(-\frac{w_i - \bar{w}(t) \cdot r_{\text{stress}}}{\bar{w}(t) \cdot r_{\text{wealth}}}\right) & w_i \ge \bar{w}(t) \cdot r_{\text{stress}}
\end{cases}$$

where:
- $\theta_{\text{sub}}$ = subsistence floor = agent's own metabolism × τ_sub (default τ_sub=5)
- $\bar{w}(t)$ = current population mean wealth (computed once per step)
- $r_{\text{stress}}$ = stress zone upper boundary multiplier (default 0.75)
- $r_{\text{wealth}}$ = prosperity decay scale (default 0.5)
- $P_{\text{max}}$ = maximum birth probability per step (default 0.02)
- $a_{\text{rep\_min}}$ = 15, $a_{\text{rep\_max}}$ = τ_max - 10

**Note on P_max=0.02:** at N=250 with ~62 agents in reproductive window,
expected births/step ≈ 1.25 at P_max. Deaths/step in Stage 4 were ~5.3.
P_max needs tuning — the null control run will reveal the right value.
Do not pre-tune; report what emerges and adjust if criteria fail.

**Cred-modulated birth (γ term) is NOT in Stage 4.1a.** Deferred to Stage 4.2
sweep. This stage uses wealth-only birth probability for C.

**Offspring:** produced via existing biparental rule (proximity r=3, H_i mixing,
σ_inherit=0.05). Wealth inheritance λ=0 (offspring get fresh wealth draw from
[w_floor, w_floor + w_range]). f_C endowment applies as before.

### 1.3 Birth rule (Si agents)

Each step, each living Si agent within reproductive age window attempts fission
with probability P_fission:

$$P_{\text{fission}}^{Si}(w_i, a_i) = \begin{cases}
0 & w_i < \theta_{\text{fission}} \text{ or } a_i \notin [a_{\text{rep\_min}}, a_{\text{rep\_max}}] \\
P_{\text{fission\_max}} & w_i \ge \theta_{\text{fission}}
\end{cases}$$

where:
- $\theta_{\text{fission}}$ = wealth threshold for fission (default = mean wealth × 1.5)
  — Si agents only reproduce when comfortably above average
- $P_{\text{fission\_max}}$ = maximum fission probability per step (default 0.02)

**Si fission mechanics:**
- Single parent only. No partner selection.
- Offspring H_i = parent H_i + ε (ε ~ N(0, σ_inherit²) per dimension, clipped [0,1])
- Non-trait attributes (vision, metabolism, max-age) drawn fresh from distributions
- Offspring placed at parent location or adjacent empty cell
- Si Cred of offspring = 0 (Si Cred economy not yet active)
- **No biparental logic of any kind.** ReproductionCoordinator must confirm
  Si strategy before any parent selection code runs.

### 1.4 ReproductionCoordinator — C/Si awareness

The existing ReproductionCoordinator protocol is extended with explicit
C/Si dispatch:

```python
class ReproductionCoordinator:
    def attempt_birth(
        self,
        agent: "BaseAgent",
        world: "World",
        rng,
    ) -> "BaseAgent | None":
        """
        Returns offspring if birth occurs, None otherwise.
        Dispatches to C or Si logic based on agent strategy.
        NEVER applies biparental logic to Si agents.
        """
        if agent.strategy == "carbon":
            return self._carbon_birth(agent, world, rng)
        elif agent.strategy == "si_bounded":
            return self._si_fission(agent, world, rng)
        else:
            raise ValueError(f"Unknown strategy: {agent.strategy}")

    def _carbon_birth(self, agent, world, rng):
        # Biparental: select two proximate parents, mix H_i
        ...

    def _si_fission(self, agent, world, rng):
        # Single parent: near-copy with noise
        # ASSERT: never calls _carbon_birth
        ...

    # HiveMind stub — Si only, Stage 7+
    def _si_hivemind_birth(self, agent, world, rng):
        raise NotImplementedError(
            "HiveMind coordinator not yet implemented. "
            "Set reproduction.coordinator='individual' for Si."
        )

    # Fork stub — Si only, Stage 7+
    def fork(self, agent: "BaseAgent", world: "World", rng) -> "BaseAgent":
        raise NotImplementedError(
            "Forking not yet implemented. "
            "Flagged for Stage 7+ — requires agent lifecycle refactor."
        )
```

### 1.5 New config section

```yaml
population:
  mode: "dynamic"           # "fixed" = Stage 1 behavior, "dynamic" = Stage 4.1a+

birth_c:
  p_max: 0.02               # P_max — maximum birth probability per step
  tau_sub: 5                # subsistence floor = metabolism × tau_sub
  r_stress: 0.75            # stress zone upper boundary (× mean wealth)
  r_wealth: 0.5             # prosperity decay scale (× mean wealth)
  rep_age_min: 15           # reproductive window minimum age
  rep_age_max: null         # null → τ_max - 10 per agent

birth_si:
  p_fission_max: 0.02       # maximum fission probability per step
  fission_wealth_mult: 1.5  # θ_fission = mean wealth × this multiplier
  rep_age_min: 15
  rep_age_max: null

reproduction:
  coordinator: "individual" # "individual" or "hivemind" (Si only, Stage 7+)
  lambda_inheritance: 0.0   # wealth inheritance fraction (0 = no inheritance)
```

---

## 2. New metrics

| Metric | Definition |
|---|---|
| `population` | N(t) — now variable, primary H1(ii) diagnostic |
| `births_per_step_c` | C births this step |
| `births_per_step_si` | Si births this step |
| `birth_rate_c` | births_c / N_c — per-capita birth rate |
| `birth_rate_si` | births_si / N_si |
| `net_growth_rate` | (births - deaths) / N — positive = growing |
| `population_min` | minimum N(t) observed so far — running minimum |
| `carrying_capacity_est` | mean sugar / mean metabolism — rough world capacity |

---

## 3. Runs to execute

Four runs in strict order:

| Run | Config | Purpose |
|---|---|---|
| 1 | `stage41a_c_static_seed42.yaml` | C null control — static world, dynamic population |
| 2 | `stage41a_si_static_seed42.yaml` | Si null control — static world, dynamic population |
| 3 | `stage41a_c_seasonal_seed42.yaml` | C seasonal — dynamic population under oscillation |
| 4 | `stage41a_si_seasonal_seed42.yaml` | Si seasonal — dynamic population under oscillation |

Runs 1 and 2 are gates. **Do not run 3 or 4 until 1 and 2 confirm stable
quasi-stationary N(t).** If null controls collapse or explode, birth parameters
need adjustment before seasonal runs are meaningful.

All runs: seed=42, 1000 steps, A=0.5, T=200 for seasonal configs.

---

## 4. Success criteria

1. **Null controls reach quasi-stationary N(t).** N(t) stabilizes within
   [150, 400] by t=500 and stays there through t=1000. If N < 150: P_max too low.
   If N > 400: P_max too high or θ_birth too low.

2. **No Si biparental reproduction.** Verify in code audit before running.
   ReproductionCoordinator._si_fission never calls _carbon_birth. Automated
   assertion in test suite.

3. **Seasonal signal visible in N(t).** Under seasonal oscillation, N(t) shows
   oscillatory pattern correlated with seasonal phase. N(t) dips during troughs.
   If N(t) is flat under seasonal oscillation, the birth/death coupling is too
   slow to respond to seasonal timescale T=200.

4. **Carrying capacity respected.** N(t) does not exceed carrying_capacity_est
   × 1.5 at any sustained period. World physics enforces this — if it's violated,
   investigate birth rule.

5. **Tests pass.** See §5.

6. **Reproducibility** confirmed for all four runs.

---

## 5. Tests

`tests/test_variable_population.py`:

1. **C/Si dispatch:** verify ReproductionCoordinator calls _carbon_birth for
   carbon agents and _si_fission for si_bounded agents. Assert _si_fission
   never calls _carbon_birth under any circumstance.

2. **HiveMind stub raises:** verify coordinator="hivemind" raises
   NotImplementedError cleanly.

3. **Fork stub raises:** verify fork() raises NotImplementedError cleanly.

4. **Birth probability formula:** for known (w_i, mean_w, metabolism), verify
   P_birth matches analytic formula at subsistence floor, stress zone, and
   prosperity zone.

5. **Fixed mode recovers Stage 4:** verify population.mode="fixed" produces
   identical N(t)=250 throughout as Stage 4 runs.

6. **Fission offspring:** verify Si offspring H_i = parent H_i + ε (clipped),
   non-trait attributes fresh, placed at valid location.

7. **Carrying capacity:** on a 10×10 grid with 2 agents and dynamic population,
   verify N(t) stabilizes rather than growing to fill all cells.

---

## 6. Coding-agent directives

1. **Read ROADMAP.md C/Si distinction table first.** Before writing any
   reproduction code. This is non-negotiable after BUG-002.

2. **population.mode="fixed" must recover Stage 4 exactly.** Run the Stage 4
   C seasonal config with mode="fixed" and confirm metrics match Stage 4 parquet
   to within floating point. This is the regression gate.

3. **Null controls before seasonal runs.** Runs 1+2 gate Runs 3+4. Do not
   proceed if null controls fail success criterion 1.

4. **P_max is exploratory.** Default 0.02 is a starting point. If null controls
   fail criterion 1, adjust P_max and document the adjustment in the report
   Notes section. Do not silently tune — report what was tried.

5. **ReproductionCoordinator is the single entry point for all births.**
   No birth logic anywhere else in the codebase.

6. **Fork and HiveMind stubs are mandatory.** Even though they raise
   NotImplementedError, they must exist as named methods. Stage 7+ should
   find them, not need to add them.

7. **Update ROADMAP.md** at completion: mark Stage 4.1a complete, record
   quasi-stationary N(t) range, update locked parameters if P_max is tuned.

---

## 7. Deferred

- Age-efficiency ramp η(a). → Stage 4.1b.
- Proximity support pool. → Stage 4.1c.
- Cred-modulated birth (γ term). → Stage 4.2 sweep.
- Wealth inheritance (λ > 0). → Stage 4.2 sweep.
- Si Cred economy. → Stage 5+.
- Si ψ_i utility hook. → Stage 5+.
- HiveMind implementation. → Stage 7+.
- Fork/merge mechanics. → Stage 7+.
- Inter-pool connectivity. → Stage 5+.
- Defection/criminal emergence. → Stage 6+ (requires c2 hook).
- Compute/energy as Si Cred (Q28). → Stage 5+ design decision.
