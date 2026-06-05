from __future__ import annotations

import random
from pathlib import Path

import mesa
import numpy as np
import pandas as pd

from sic_games.agents.base import BaseAgent
from sic_games.agents.costs import ScaledMetabolicCost
from sic_games.agents.perception import LocalVisionPerception
from sic_games.world_perturbation import NullPerturbation, SeasonalOscillation
from sic_games.agents.reproduction import (
    BiparentalReproduction,
    RandomReplacement,
    ReproductionCoordinator,
    ReproductionRule,
    carry_discount,
)
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.strategies.greedy import GreedyMaximizer
from sic_games.agents.strategies.si_bounded import BoundedRationalSi
from sic_games.agents.traits import TraitVector
from sic_games.config import Config
from sic_games.joint_task import JointTaskManager
from sic_games.metrics import StepMetrics, c_spatial_density, compute_metrics
from sic_games.support_pool import SupportPool
from sic_games.world import SugarField

_NEWBORN_AGE_CUTOFF = 20  # agents younger than this count as "newborn" for starvation split


class SugarWorld(mesa.Model):
    """Sugarscape model — Stage 1 through Stage 3.

    Scheduling each step:
      1. G_alpha: sugar growback
      2. Joint-task detection + Matthew payoff distribution
      3. Agent step in random order (perceive → decide → move → harvest → pay → age)
      4. Cred update: flush pending deltas, apply decay to all (carbon only)
      5. Replacement R (with newborn Cred endowment for carbon)
      6. Metrics
    """

    def __init__(self, config: Config,
                 env_seed: int | None = None,
                 agent_seed: int | None = None) -> None:
        """Initialise world from config.

        CRN (common-random-numbers) support: when `env_seed` and `agent_seed`
        are provided, the world uses two independent RNG streams:
          - env_rng  = np.random.default_rng(env_seed)   ← placement, bio draws
          - agent_rng = random.Random(agent_seed)          ← shuffles, movement
        Both C and Si worlds at the same seed receive identical env_seed, ensuring
        that differences in population outcomes are attributable to strategy, not
        environmental variance. When None (default), config.seed is used for both,
        preserving all prior behaviour exactly.
        """
        _env_seed = env_seed if env_seed is not None else config.seed
        _agent_seed = agent_seed if agent_seed is not None else config.seed
        super().__init__(rng=_env_seed)

        self.cfg = config
        wc = config.world
        ac = config.agents
        cc = config.carbon
        jc = config.joint_task
        sbc = config.si_bounded

        self.sugar_field = SugarField(
            width=wc.grid_size[0],
            height=wc.grid_size[1],
            peaks=wc.sugar_peaks,
            max_capacity=wc.max_sugar_capacity,
            band_width_k=wc.band_width_k,
            alpha=wc.growth_rate_alpha,
        )

        self._sugar_peaks: list[tuple[int, int]] = wc.sugar_peaks
        self.occupied: set[tuple[int, int]] = set()
        self._rng_np = np.random.default_rng(_env_seed)
        self._rng_py = random.Random(_agent_seed)

        strategy = config.decision.strategy
        self._is_carbon = strategy == "carbon"
        self._is_si_bounded = strategy == "si_bounded"
        self._strategy_name = strategy  # passed to each spawned agent

        if self._is_carbon:
            self._carbon_decision = CarbonDecision(
                sigma_base=cc.sigma_base,
                kappa=cc.kappa,
                cred_scale=cc.cred_scale,
                matthew_alpha=cc.matthew_alpha,
                epsilon=cc.epsilon,
                cred_bonus_per_participant=cc.cred_bonus_per_participant,
                velocity_scale=cc.velocity_scale,
                beta=cc.status_amplification_beta,
            )
            self._decision = self._carbon_decision
            self._jt_manager = JointTaskManager(
                distance_d=jc.distance_d,
                capacity_threshold=jc.capacity_threshold,
                matthew_alpha=cc.matthew_alpha,
                epsilon=cc.epsilon,
                cred_bonus_per_participant=cc.cred_bonus_per_participant,
            )
            self._cred_decay = cc.cred_decay
            self._velocity_tau = cc.velocity_tau
            self._f_C = cc.f_C
            self._si_bounded_sigma = 0.0

        elif self._is_si_bounded:
            self._carbon_decision = None
            sc5 = config.si_cred  # Stage 5: Si Cred modulation
            self._decision = BoundedRationalSi(
                sigma_si=sbc.sigma_si,
                kappa_si=sc5.kappa_Si if sc5.enabled else 0.0,
                c_star_si=sc5.C_star_Si,
            )
            # JT manager enabled; cred_bonus=0 so no Cred deltas are queued
            self._jt_manager = JointTaskManager(
                distance_d=jc.distance_d,
                capacity_threshold=jc.capacity_threshold,
                matthew_alpha=cc.matthew_alpha,  # degenerate to equal shares (all cred=0)
                epsilon=cc.epsilon,
                cred_bonus_per_participant=0.0,
            )
            self._cred_decay = 0.0
            self._velocity_tau = 0
            self._f_C = 0.0
            self._si_bounded_sigma = sbc.sigma_si
            # Stage 4.3: Si differential metabolism via CostModel (β ≥ 1)
            self._si_cost_model = ScaledMetabolicCost(
                beta=sbc.beta_metabolism,
                k_carry=sbc.k_carry,   # Stage 4.5 Task 3: None → disabled (default)
                phi_carry=sbc.phi_carry,
            )

        else:  # greedy
            self._carbon_decision = None
            self._decision = GreedyMaximizer()
            self._jt_manager = None
            self._cred_decay = 0.0
            self._velocity_tau = 0
            self._f_C = 0.0
            self._si_bounded_sigma = 0.0
            self._si_cost_model = None  # greedy uses MetabolicOnly (default in BaseAgent)

        if not self._is_si_bounded:
            self._si_cost_model = None  # ensure attribute always set

        pc = config.perturbation
        if pc.type == "seasonal":
            self._perturbation = SeasonalOscillation(
                amplitude=pc.amplitude, period=pc.period,
                trough_fraction=pc.trough_fraction,  # Stage 4.5: asymmetric (default=0.5)
            )
        else:
            self._perturbation = NullPerturbation()
        self._perturbation_period: int = pc.period

        rc = config.reproduction
        if rc.mode == "biparental":
            self._reproduction_rule: ReproductionRule = BiparentalReproduction(
                parent_radius=rc.parent_radius,
                inherit_sigma=rc.inherit_sigma,
            )
        else:
            self._reproduction_rule = RandomReplacement()

        # Stage 4.1a: dynamic population mode
        self._pop_mode = config.population.mode
        if self._pop_mode == "dynamic":
            self._coordinator = ReproductionCoordinator(
                birth_c_config=config.birth_c,
                birth_si_config=config.birth_si,
                parent_radius=rc.parent_radius,
                inherit_sigma=rc.inherit_sigma,
                pool_cfg=config.support_pool,
                lambda_inheritance=rc.lambda_inheritance,  # Stage 4.4: λ wealth inheritance (C only)
            )
        else:
            self._coordinator = None

        # Stage 4.4: shared perception builder for C agents.
        # Updated each step with the C-proximity grid so ψ uses r_pool-radius social density.
        if self._is_carbon:
            self._shared_perception: LocalVisionPerception | None = LocalVisionPerception()
        else:
            self._shared_perception = None

        # Stage 4.1c: proximity support pool
        pool_cfg = config.support_pool
        self._support_pool: SupportPool | None = None
        if pool_cfg.enabled:
            self._support_pool = SupportPool(pool_cfg)
            if self._coordinator is not None:
                self._coordinator._pool_cfg = pool_cfg
                self._coordinator._pool = self._support_pool

        # Stage 4.1b: life-history config (None → η=1.0 always, backward compat)
        lhc = config.life_history
        self._lh_config = lhc if lhc.eta_min < 1.0 or lhc.eta_old < 1.0 else None
        # Stage 4.3: Si agents never use the juvenile η ramp (η=1.0 is C-only from 4.3+).
        # Si agents receive lh_config=None in _spawn_one regardless of life_history config.
        self._use_realistic_age = (
            config.initialization.age_distribution == "realistic"
        )
        # Stage 4.4 patch: configurable upper bound for realistic age draw
        self._age_init_upper_frac: float = config.initialization.age_init_upper_frac
        # Stage 4.4 patch amendment: scale initial wealth by k_grid at t=0 only
        # k_grid = growth_rate_alpha (both scaled together: max_sugar=4k, alpha=k)
        self._wealth_init_scale_k: bool = config.initialization.wealth_init_scale_k
        self._k_grid: int = config.world.growth_rate_alpha  # =1 at k=1, =4 at k=4
        # Stage 4.4 patch amendment 2: cluster initialisation (C only; t=0 only)
        self._cluster_init: bool = config.initialization.cluster_init
        if self._cluster_init:
            peaks = config.world.sugar_peaks
            self._cluster_peak: tuple[int, int] = tuple(peaks[config.initialization.cluster_peak_index])  # type: ignore
            self._cluster_radius: int = config.initialization.cluster_radius
        else:
            self._cluster_peak = (0, 0)
            self._cluster_radius = 0

        # Stage 4.3: dormancy config (enabled in Si configs only)
        dc = config.dormancy
        self._dormancy_cfg = dc if dc.enabled else None

        # Stage 5 Task 3: Si Cred config (always stored; accumulation gated on enabled)
        self._si_cred_cfg = config.si_cred

        # Stage 4.3: death event log — per-run list of dicts, saved to death_events.parquet
        self._death_events: list[dict] = []

        self._spawn_agents(ac.initial_population)
        self._population_min: int = ac.initial_population

        self.metrics_log: list[StepMetrics] = []
        self._step_count = 0
        self._step_fallback_count = 0
        self.starvation_cred_log: list[float] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _random_unoccupied(self) -> tuple[int, int]:
        w, h = self.cfg.world.grid_size
        while True:
            x = int(self._rng_np.integers(0, w))
            y = int(self._rng_np.integers(0, h))
            if (x, y) not in self.occupied:
                return x, y

    def _build_cluster_candidates(self) -> list[tuple[int, int]]:
        """All cells within Chebyshev radius of the cluster peak (toroidal)."""
        W, H = self.cfg.world.grid_size
        px, py = self._cluster_peak
        r = self._cluster_radius
        cells = []
        for x in range(W):
            for y in range(H):
                dx = min(abs(x - px), W - abs(x - px))
                dy = min(abs(y - py), H - abs(y - py))
                if max(dx, dy) <= r:
                    cells.append((x, y))
        return cells

    def _random_from_cluster(self, cluster_cells: list[tuple[int, int]]) -> tuple[int, int]:
        """Pick a random unoccupied cell from the cluster; fall back to full grid if full."""
        available = [c for c in cluster_cells if c not in self.occupied]
        if not available:
            return self._random_unoccupied()
        idx = int(self._rng_np.integers(0, len(available)))
        return available[idx]

    def _draw_bio_attrs(self):
        ac = self.cfg.agents
        vision = int(self._rng_np.integers(ac.vision_dist[0], ac.vision_dist[1] + 1))
        metabolism = int(self._rng_np.integers(ac.metabolic_rate_dist[0], ac.metabolic_rate_dist[1] + 1))
        max_age = int(self._rng_np.integers(ac.max_age_dist[0], ac.max_age_dist[1] + 1))
        wealth = int(self._rng_np.integers(ac.initial_wealth_dist[0], ac.initial_wealth_dist[1] + 1))
        return vision, metabolism, max_age, wealth

    def _draw_trait_vector(self) -> TraitVector:
        ac = self.cfg.agents
        def _clip(v: float) -> float:
            return float(max(0.0, min(1.0, v)))
        # Stage 4.4: ψ drawn from Beta(psi_beta_a, psi_beta_b) when both > 0 in config.
        # Otherwise falls back to Normal(psi_mean, psi_std) for backward compatibility.
        if ac.psi_beta_a > 0.0 and ac.psi_beta_b > 0.0:
            psi_val = float(self._rng_np.beta(ac.psi_beta_a, ac.psi_beta_b))
        else:
            psi_val = _clip(self._rng_np.normal(ac.psi_mean, ac.psi_std))
        return TraitVector(
            phi=_clip(self._rng_np.normal(ac.phi_mean, ac.phi_std)),
            psi=psi_val,
            c1=_clip(self._rng_np.normal(ac.c1_mean, ac.c1_std)),
            c2=_clip(self._rng_np.normal(ac.c2_mean, ac.c2_std)),
        )

    def mean_cred(self) -> float:
        agents = list(self.agents)
        if not agents:
            return 0.0
        return sum(a.cred for a in agents) / len(agents)

    def _find_adjacent_unoccupied(
        self, pos: tuple[int, int]
    ) -> tuple[int, int] | None:
        w, h = self.cfg.world.grid_size
        x, y = pos
        neighbors = [
            ((x + 1) % w, y), ((x - 1) % w, y),
            (x, (y + 1) % h), (x, (y - 1) % h),
        ]
        self._rng_py.shuffle(neighbors)
        for n in neighbors:
            if n not in self.occupied:
                return n
        return None

    def mean_wealth(self) -> float:
        agents = list(self.agents)
        if not agents:
            return 0.0
        return sum(a.wealth for a in agents) / len(agents)

    def _spawn_one(
        self,
        traits: TraitVector | None = None,
        preferred_pos: tuple[int, int] | None = None,
        realistic_age: bool = False,
        si_fission: bool = False,
        w_scale: float = 1.0,
        cluster_cells: list[tuple[int, int]] | None = None,
    ) -> BaseAgent:
        vision, metabolism, max_age, wealth = self._draw_bio_attrs()
        # Stage 4.4 patch amendment: wealth scaling (t=0 init only, passed via _spawn_agents)
        if w_scale != 1.0:
            wealth = int(wealth * w_scale)
        if traits is None:
            traits = self._draw_trait_vector()

        # Stage 4.3: Si agents don't use η(a) juvenile ramp (C-only from Stage 4.3).
        # Si always gets lh_config=None so η=1.0 regardless of life_history config.
        lh_config_for_agent = (
            None if self._strategy_name == "si_bounded" else self._lh_config
        )

        agent = BaseAgent(
            model=self,
            vision=vision,
            metabolism=metabolism,
            max_age=max_age,
            initial_wealth=float(wealth),
            decision_logic=self._decision,
            cost_model=self._si_cost_model,  # None for C/greedy → defaults to MetabolicOnly
            # Stage 4.4: C agents share a single perception builder so c_prox_grid updates
            # once per step and all agents see the same C-proximity data.
            perception_builder=self._shared_perception,
            traits=traits,
            strategy=self._strategy_name,
            lh_config=lh_config_for_agent,
        )
        # Stage 4.1b: realistic initialization draws age ~ Uniform[0, floor(tau_max * age_init_upper_frac)]
        # Stage 4.4 patch: age_init_upper_frac=0.25 (was implicit 0.5). Default 0.5 preserves Stage 4.1b behaviour.
        if realistic_age:
            upper = max(0, int(max_age * self._age_init_upper_frac))
            agent.age = self._rng_py.randint(0, upper) if upper > 0 else 0
        # si_fission flag is informational — Si already has lh_config=None so η=1.0.
        # Kept for documentation clarity.
        if preferred_pos is not None:
            pos = self._find_adjacent_unoccupied(preferred_pos)
            if pos is None:
                pos = self._random_unoccupied()
        elif cluster_cells is not None:
            # Stage 4.4 patch amendment 2: cluster init placement (t=0 only; C only)
            pos = self._random_from_cluster(cluster_cells)
        else:
            pos = self._random_unoccupied()
        agent.pos = pos
        self.occupied.add(pos)
        return agent

    def _spawn_agents(self, n: int) -> None:
        # Stage 4.4 patch amendment: at t=0, optionally scale initial wealth by k_grid.
        # Newborns spawned during the run call _spawn_one directly (w_scale=1.0 default).
        w_scale = float(self._k_grid) if self._wealth_init_scale_k else 1.0
        # Stage 4.4 patch amendment 2: cluster init — C only; newborns placed normally.
        cluster_cells = None
        if self._cluster_init and self._strategy_name == "carbon":
            cluster_cells = self._build_cluster_candidates()
        for _ in range(n):
            self._spawn_one(realistic_age=self._use_realistic_age,
                            w_scale=w_scale, cluster_cells=cluster_cells)

    # ------------------------------------------------------------------
    # Mesa step protocol
    # ------------------------------------------------------------------

    def step(self) -> None:
        t = self._step_count + 1  # 1-indexed step number used for seasonal formula

        # 1. WorldPerturbation: update effective_capacity
        self._perturbation.apply(self.sugar_field, t, self._rng_py)

        # 2. Sugar shedding: clip current sugar to effective_capacity
        self.sugar_field.shed_excess_sugar()

        # 3. Growback (uses effective_capacity, not max_capacity)
        self.sugar_field.growback()

        # 4. Joint-task detection + payoff
        # Build agent_list once here; reuse for JT and all subsequent per-agent
        # phases (harvest, pool, metabolize, cred flush). JT does not move agents,
        # so the list is valid for all pre-death phases. [perf-fix: merged list calls]
        agent_list = list(self.agents)

        joint_task_events = []
        if self._jt_manager is not None:
            joint_task_events = self._jt_manager.process_step(
                self.sugar_field, agent_list, rng=self._rng_py
            )
            if self._carbon_decision is not None:
                jt_cells = {e.cell for e in joint_task_events}
                self._carbon_decision.joint_task_cells = jt_cells

        # 3. Agent step in random order
        deaths_starvation = 0
        deaths_starvation_newborn = 0
        deaths_starvation_established = 0
        deaths_starvation_juvenile = 0
        deaths_starvation_elder = 0
        deaths_senescence = 0
        # Stage 4.3: Si-specific counters
        permanent_dormancy_deaths = 0
        reactivations_this_step = 0
        trickle_absorbed = 0.0
        dead: list[BaseAgent] = []
        dead_causes: dict[int, str] = {}  # unique_id → cause for death_events log

        self._rng_py.shuffle(agent_list)

        # Stage 4.4: update C-proximity grid before harvest so each agent's perception
        # reflects the social density map at the start of this step.
        # Fast vectorised: place C agents in a binary grid, then apply a 2D box-filter
        # of size (2*r_pool+1)^2 using cumulative sums with toroidal (wrap) padding.
        # O(W*H) instead of O(N*(2r+1)^2) Python loops.
        if self._shared_perception is not None:
            wg, hg = self.cfg.world.grid_size
            r = self.cfg.support_pool.r_pool
            c_grid = np.zeros((wg, hg), dtype=np.int32)
            for a in agent_list:
                if a.strategy == "carbon" and not a.dormant:
                    c_grid[a.pos[0], a.pos[1]] += 1
            # Toroidal box-sum via padding + zero-prefixed 2D prefix sum.
            # cs[m,n] = sum of padded[0:m, 0:n]  (exclusive upper bounds).
            size = 2 * r + 1
            padded = np.pad(c_grid, r, mode="wrap")        # (W+2r) × (H+2r)
            cs = np.zeros((padded.shape[0] + 1, padded.shape[1] + 1), dtype=np.int64)
            cs[1:, 1:] = padded.cumsum(axis=0).cumsum(axis=1)  # shape (W+2r+1, H+2r+1)
            # sum of padded[i:i+size, j:j+size] for i∈[0,W), j∈[0,H):
            # = cs[i+size, j+size] − cs[i, j+size] − cs[i+size, j] + cs[i, j]
            c_prox = (cs[size:wg+size, size:hg+size] - cs[:wg, size:hg+size]
                      - cs[size:wg+size, :hg] + cs[:wg, :hg]).astype(np.int32)
            self._shared_perception.c_prox_grid = c_prox

        # Phase 1: harvest phase
        # Dormant Si agents do passive trickle absorption (not competitive harvest).
        # Active agents (C and non-dormant Si) do normal act_harvest.
        dc = self._dormancy_cfg
        for agent in agent_list:
            if dc is not None and agent.dormant:
                # Passive trickle — reads cell sugar without consuming it (no harvest/growback trigger)
                trickle = dc.tau_trickle * self.sugar_field.level(*agent.pos)
                agent.wealth += trickle
                trickle_absorbed += trickle
                agent._last_moved = False
                agent._last_harvested = 0.0
            else:
                agent.act_harvest(self.sugar_field, self.occupied)

        # Phase 1b: Si Cred accumulation (Stage 5 Task 3)
        # Only runs when strategy=si_bounded AND si_cred.enabled=True.
        # For each active (non-dormant) Si agent:
        #   surplus = max(0, last_harvested − effective_cost)
        #   si_cred ← min(si_cred × (1−δ) + surplus × r_cred_Si, C*_Si)
        # kappa_si=0.0 (default) leaves σ unchanged — Stage 4.5 behaviour is preserved exactly.
        if self._is_si_bounded and self._si_cred_cfg.enabled:
            _sc = self._si_cred_cfg
            _beta = self._si_cost_model.beta if self._si_cost_model is not None else 1.0
            for agent in agent_list:
                if not agent.dormant:
                    surplus = max(0.0, agent._last_harvested - float(agent.metabolism) * _beta)
                    delta = surplus * _sc.accumulation_rate
                    agent.si_cred = min(
                        agent.si_cred * (1.0 - _sc.decay) + delta,
                        _sc.C_star_Si,
                    )

        # Phase 2: pool step (contribution then draw) — between harvest and metabolism
        # Dormant Si agents don't contribute or draw (Si pool disabled in Stage 4.3; dormant flag
        # also guards against any future Si pool scenario with dormant_can_draw=False).
        pool_metrics = None
        if self._support_pool is not None:
            pool_metrics = self._support_pool.step(agent_list)

        # Phase 3: metabolize + dormancy management
        # C agents: normal act_metabolize (starvation death as before).
        # Si agents: dormancy-aware step (no starvation death; enter/exit dormancy instead).
        for agent in agent_list:
            if dc is not None:
                # --- Si dormancy-aware metabolize ---
                cost = agent._cost.step_cost(agent, {"moved": agent._last_moved, "harvested": agent._last_harvested})

                if agent.dormant:
                    # Dormant: no metabolism payment, track dormancy duration, check reactivation/permanent death
                    agent.dormant_steps += 1
                    if agent.wealth >= dc.k_reactivate * cost:
                        # Reactivate
                        agent.dormant = False
                        agent.dormant_steps = 0
                        reactivations_this_step += 1
                    elif agent.dormant_steps > dc.t_dormant_max:
                        # Permanent death from prolonged dormancy
                        agent.alive = False
                        permanent_dormancy_deaths += 1
                    agent.age += 1
                    if agent.age >= agent.max_age:
                        agent.alive = False
                else:
                    # Active Si: pay cost, check dormancy entry BEFORE declaring dead
                    if agent.wealth < dc.k_dormant * cost:
                        # Enter dormancy instead of dying
                        agent.dormant = True
                        agent.dormant_steps = 0
                        agent.age += 1
                        if agent.age >= agent.max_age:
                            agent.alive = False
                    else:
                        # Normal Si step: pay cost, check senescence
                        agent.wealth -= cost
                        delta_w = agent._last_harvested - cost
                        if self._velocity_tau > 0:
                            alpha = 1.0 / self._velocity_tau
                            agent.wealth_velocity = (1 - alpha) * agent.wealth_velocity + alpha * delta_w
                        agent.age += 1
                        if agent.wealth <= 0 or agent.age >= agent.max_age:
                            agent.alive = False

                if not agent.alive:
                    dead.append(agent)

            else:
                # --- C / greedy: normal act_metabolize ---
                agent.act_metabolize(velocity_tau=self._velocity_tau)
                if not agent.alive:
                    dead.append(agent)

        # 4. Cred flush + decay (carbon only)
        # Use agent_list (built pre-harvest) rather than self.agents iterator.
        # Dead agents are still in self.agents at this point (removed below), so
        # both sets are identical here. agent_list avoids a second AgentSet traversal.
        if self._is_carbon:
            for agent in agent_list:
                agent.cred = (1 - self._cred_decay) * agent.cred + agent._pending_cred_delta
                agent._pending_cred_delta = 0.0

        # Determine season phase for death event log (1=peak, 0=trough)
        T_period = self._perturbation_period
        _s_ph = (self._step_count % T_period) / T_period if T_period > 0 else 0.0
        _is_peak = int(_s_ph < 0.25 or _s_ph >= 0.75)  # sin² trough centered at phase=0.5

        # 5. Remove dead agents + record death events
        for agent in dead:
            self.occupied.discard(agent.pos)
            # Classify cause
            if dc is not None and agent.dormant:
                # Permanent dormancy death (Si only)
                cause = "permanent_dormancy"
            elif agent.wealth <= 0:
                cause = "starvation"
                deaths_starvation += 1
                self.starvation_cred_log.append(agent.cred)
                if agent.age < _NEWBORN_AGE_CUTOFF:
                    deaths_starvation_newborn += 1
                else:
                    deaths_starvation_established += 1
                if agent.is_juvenile():
                    deaths_starvation_juvenile += 1
                elif agent.is_elder():
                    deaths_starvation_elder += 1
            else:
                cause = "senescence"
                deaths_senescence += 1

            # Stage 4.3: record death event
            self._death_events.append({
                "step": self._step_count + 1,  # 1-indexed
                "cause": cause,
                "age": agent.age,
                "wealth": float(agent.wealth),
                "psi": float(agent.psi) if agent.strategy == "carbon" else float("nan"),
                "cred": float(agent.cred) if agent.strategy == "carbon" else float("nan"),
                "agent_type": "C" if agent.strategy == "carbon" else "Si",
                "season_phase": _is_peak,
                "dormancy_duration": int(agent.dormant_steps) if agent.strategy == "si_bounded" else 0,
            })
            agent.remove()

        # 5b. Birth / replacement (path depends on population mode)
        step_fallbacks = 0
        births_c = 0
        births_si = 0

        if self._pop_mode == "fixed":
            # Stage 1–4: immediate one-for-one replacement
            for agent in dead:
                new_agent, fallback = self._reproduction_rule.replace(self, agent.pos, self._rng_py)
                if self._is_carbon and self._f_C > 0.0:
                    new_agent.cred = self._f_C * self.mean_cred()
                if fallback:
                    step_fallbacks += 1
        else:
            # Stage 4.1a dynamic: birth probability loop over living agents
            # Dormant Si agents cannot reproduce
            mean_w = self.mean_wealth()
            living_snapshot = list(self.agents)
            for agent in living_snapshot:
                if agent.dormant:
                    continue  # dormant agents do not reproduce
                offspring = self._coordinator.attempt_birth(agent, self, self._rng_py, mean_w)
                if offspring is not None:
                    if agent.strategy == "carbon":
                        births_c += 1
                        if self._f_C > 0.0:
                            offspring.cred = self._f_C * self.mean_cred()
                    elif agent.strategy == "si_bounded":
                        births_si += 1

        # Stage 4.1b: read stress zone counters and reset for next step
        if self._coordinator is not None:
            births_stress_zone = self._coordinator.births_stress_zone
            births_prosperity_zone = self._coordinator.births_prosperity_zone
            gamma_birth_boost = self._coordinator.gamma_birth_boost
            lambda_boost = self._coordinator.lambda_inheritance_boost  # Stage 4.4
            # Stage 4.5: carry_discount metrics
            carry_disc_mean = self._coordinator.carry_discount_mean
            p_birth_eff_mean = self._coordinator.p_birth_effective_mean
            self._coordinator.reset_step_counters()
        else:
            births_stress_zone = 0
            births_prosperity_zone = 0
            gamma_birth_boost = 1.0
            lambda_boost = 0.0
            carry_disc_mean = float("nan")
            p_birth_eff_mean = float("nan")

        # Stage 4.4: ψ proximity utility — mean(ψ_i × c_proximity_i) across active C agents.
        # c_prox_grid was built from positions at start of step (pre-movement approximation).
        psi_prox_utility = 0.0
        if self._is_carbon and self._shared_perception is not None and self._shared_perception.c_prox_grid is not None:
            cpg = self._shared_perception.c_prox_grid
            c_agents = [a for a in agent_list if a.strategy == "carbon" and not a.dormant]
            if c_agents:
                psi_prox_utility = sum(a.psi * int(cpg[a.pos[0], a.pos[1]]) for a in c_agents) / len(c_agents)

        self._step_fallback_count += step_fallbacks

        # 6. Metrics
        self._step_count += 1

        # Stage 4.3: Si dormancy population counts
        if self._is_si_bounded:
            all_si = list(self.agents)
            n_dormant_si = sum(1 for a in all_si if a.dormant)
            n_active_si = len(all_si) - n_dormant_si
        else:
            n_dormant_si = 0
            n_active_si = 0

        if self._step_count % self.cfg.run.metrics_every == 0:
            # Seasonal diagnostic values
            sf = self.sugar_field
            T = self._perturbation_period
            s_phase = (self._step_count % T) / T
            mean_eff_cap = float(sf.effective_capacity.mean())
            peak_sugar = float(
                sum(sf.level(px, py) for px, py in self._sugar_peaks) / len(self._sugar_peaks)
            ) if self._sugar_peaks else 0.0

            elder_starvation_pct = (100.0 * deaths_starvation_elder / deaths_starvation) if deaths_starvation > 0 else 0.0

            # Stage 5 Task 3: Si Cred diagnostics
            if self._is_si_bounded and self._si_cred_cfg.enabled:
                active_si = [a for a in list(self.agents) if not a.dormant]
                if active_si:
                    from sic_games.metrics import gini as _gini_fn
                    _cred_vals = [a.si_cred for a in active_si]
                    si_cred_mean = float(np.mean(_cred_vals))
                    si_cred_std = float(np.std(_cred_vals))
                    si_cred_gini = _gini_fn(_cred_vals)
                    sigma_si_eff_mean = float(np.mean([self._decision.temperature(a) for a in active_si]))
                else:
                    si_cred_mean = si_cred_std = si_cred_gini = 0.0
                    sigma_si_eff_mean = self._si_bounded_sigma
            else:
                si_cred_mean = si_cred_std = si_cred_gini = 0.0
                sigma_si_eff_mean = self._si_bounded_sigma

            # Stage 4.4 Diagnostic: C spatial density (Allee dispersal check)
            if self._is_carbon:
                c_pos = [a.pos for a in list(self.agents)
                         if a.strategy == "carbon" and not a.dormant]
                _wg, _hg = self.cfg.world.grid_size
                mean_nearest_C_dist, pct_isolated_C = c_spatial_density(
                    c_pos, _wg, _hg, isolation_radius=3
                )
            else:
                mean_nearest_C_dist = 0.0
                pct_isolated_C = 0.0

            m = compute_metrics(
                step=self._step_count,
                agents=list(self.agents),
                sugar_field=self.sugar_field,
                deaths_starvation=deaths_starvation,
                deaths_senescence=deaths_senescence,
                deaths_starvation_newborn=deaths_starvation_newborn,
                deaths_starvation_established=deaths_starvation_established,
                joint_task_events=joint_task_events,
                carbon_decision=self._carbon_decision,
                si_bounded_sigma=self._si_bounded_sigma,
                reproduction_fallback_count=step_fallbacks,
                season_phase=s_phase,
                mean_effective_capacity=mean_eff_cap,
                peak_sugar_mean=peak_sugar,
                births_c=births_c,
                births_si=births_si,
                population_min=self._population_min,
                deaths_starvation_juvenile=deaths_starvation_juvenile,
                deaths_starvation_elder=deaths_starvation_elder,
                births_stress_zone=births_stress_zone,
                births_prosperity_zone=births_prosperity_zone,
                pool_total_contributed=pool_metrics.pool_total_contributed if pool_metrics else 0.0,
                pool_total_drawn=pool_metrics.pool_total_drawn if pool_metrics else 0.0,
                pool_draw_unmet=pool_metrics.pool_draw_unmet if pool_metrics else 0,
                pool_draw_unmet_frac=pool_metrics.pool_draw_unmet_frac if pool_metrics else 0.0,
                mean_parental_transfer=pool_metrics.mean_parental_transfer if pool_metrics else 0.0,
                cred_pool_contribution=pool_metrics.cred_pool_contribution if pool_metrics else 0.0,
                elder_starvation_pct=elder_starvation_pct,
                gamma_birth_boost=gamma_birth_boost,
                # Stage 4.3
                n_active_si=n_active_si,
                n_dormant_si=n_dormant_si,
                reactivations_per_step=reactivations_this_step,
                permanent_dormancy_deaths=permanent_dormancy_deaths,
                trickle_absorbed_per_step=trickle_absorbed,
                pool_carryover_balance=pool_metrics.pool_carryover_balance if pool_metrics else 0.0,
                pool_cap_clipped=pool_metrics.pool_cap_clipped if pool_metrics else 0.0,
                # Stage 4.4
                lambda_inheritance_boost=lambda_boost,
                psi_proximity_utility=psi_prox_utility,
                # Stage 4.4 Diagnostic
                mean_nearest_C_dist=mean_nearest_C_dist,
                pct_isolated_C=pct_isolated_C,
                # Stage 4.5: carry_discount diagnostics
                carry_discount_mean=carry_disc_mean,
                p_birth_effective_mean=p_birth_eff_mean,
                # Stage 5 Task 3: Si Cred diagnostics
                si_cred_mean=si_cred_mean,
                si_cred_std=si_cred_std,
                si_cred_gini=si_cred_gini,
                sigma_si_eff_mean=sigma_si_eff_mean,
            )
            self.metrics_log.append(m)

        # Update running population minimum (use n_active_si for Si, total for C)
        current_n = n_active_si if self._is_si_bounded else len(list(self.agents))
        if current_n < self._population_min:
            self._population_min = current_n

    def run(self) -> pd.DataFrame:
        for _ in range(self.cfg.run.n_steps):
            self.step()
        return self.metrics_to_df()

    def metrics_to_df(self) -> pd.DataFrame:
        return pd.DataFrame([vars(m) for m in self.metrics_log])

    def death_events_df(self) -> pd.DataFrame:
        """Stage 4.3: Return per-agent death event log as a DataFrame.

        Columns: step, cause, age, wealth, psi, cred, agent_type,
                 season_phase, dormancy_duration.
        psi/cred are NaN for Si agents. dormancy_duration is 0 for C.
        """
        if not self._death_events:
            return pd.DataFrame(columns=[
                "step", "cause", "age", "wealth", "psi", "cred",
                "agent_type", "season_phase", "dormancy_duration",
            ])
        return pd.DataFrame(self._death_events)

    def agent_states_df(self) -> pd.DataFrame:
        rows = [
            {
                "unique_id": a.unique_id,
                "x": a.pos[0],
                "y": a.pos[1],
                "wealth": a.wealth,
                "age": a.age,
                "vision": a.vision,
                "metabolism": a.metabolism,
                "max_age": a.max_age,
                "cred": a.cred,
                "phi": a.phi,
                "psi": a.psi,
                "c1": a.c1,
                "c2": a.c2,
                "si_cred": a.si_cred,
            }
            for a in self.agents
        ]
        return pd.DataFrame(rows)
