"""phase1_model.py — TerrainWorld: Mesa model for Phase 1 Blueprint A.

Replaces the Sugarscape SugarField harvest path with terrain kcal economy.
C agents only. Si excluded (Blueprint A scope).

Economy (A-1, kcal):
  burn_per_step  = burn_kcal_per_day × days_per_month                     [NOMINAL]
  intake_per_step = rate_kcal_per_hr × foraging_hours_per_day × days/month [NOMINAL]
  reserve += intake − burn; death at reserve ≤ reserve_floor              [PLACEHOLDER MR-1]
  reserve capped at reserve_full                                            [PLACEHOLDER MR-1]

Sex-based stream selection (A-2):
  female default → forage_kcal stream
  male   default → game_kcal stream
  switch (energy-balance, no new tunable): deviate from default only under deficit pressure
    male switch condition:  game_rate_step < burn AND forage_rate_step > game_rate_step
    female switch condition: forage_rate_step < burn AND game_rate_step > forage_rate_step
    if both streams fail to cover burn: hold default (fall to floor; existing mortality handles it)
  [PROVISIONAL — non-rivalrous harvest; rivalry deferred to CC-1]

Child age-gate (A-2, binary):
  below age_productive_min (= lh_config.forage_age_min = 15) → intake = 0
  at/above → full adult income
  [JV-1 seam: graded curve deferred]
"""
from __future__ import annotations

import random as _random
from typing import Sequence

import mesa

from sic_games.agents.base import BaseAgent
from sic_games.agents.costs import KcalBurnModel
from sic_games.agents.perception import LocalVisionPerception
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.traits import TraitVector
from sic_games.config import KcalEconomyConfig, LifeHistoryConfig
from sic_games.terrain import N, WorldFields, generate_world
from sic_games.terrain_field import TerrainField

# Default terrain knobs (production 100×100 grid)
_DEFAULT_KNOBS: dict = {
    "seedStr": "world42",
    "relief": 0.50,
    "rough": 0.50,
    "waterK": 0.30,
    "forestK": 0.55,
    "aridK": 0.40,
}


class TerrainWorld(mesa.Model):
    """Mesa model: C agents on a terrain kcal economy.

    No reproduction (Blueprint A scope). No SugarField in the C harvest path.
    Gate A-1 uses this model with game_stream=False (forage only).
    Gate A-2 exercises game_stream=True and the sex-based switch.
    """

    def __init__(
        self,
        n_agents: int,
        kcal_cfg: KcalEconomyConfig,
        terrain_knobs: dict | None = None,
        carbon_cfg=None,
        lh_cfg: LifeHistoryConfig | None = None,
        game_stream: bool = True,
        seed: int = 42,
    ) -> None:
        super().__init__(seed=seed)

        knobs = terrain_knobs or {**_DEFAULT_KNOBS, "seedStr": f"world{seed}"}
        self._fields: WorldFields = generate_world(knobs)
        self._hours_per_step = kcal_cfg.foraging_hours_per_day * kcal_cfg.days_per_month
        self.terrain_field = TerrainField(self._fields, self._hours_per_step)
        self._kcal_cfg = kcal_cfg
        self._burn = kcal_cfg.burn_kcal_per_day * kcal_cfg.days_per_month
        self._reserve_full = kcal_cfg.reserve_full_kcal
        self._reserve_floor = kcal_cfg.reserve_floor_kcal
        self._game_stream = game_stream
        self._lh_cfg = lh_cfg

        self._carbon_cfg = carbon_cfg
        self.agent_list: list[BaseAgent] = []
        self.occupied: set[tuple[int, int]] = set()
        self.step_count: int = 0

        self._init_agents(n_agents, kcal_cfg, lh_cfg)

    # ── Initialisation ─────────────────────────────────────────────────────

    def _init_agents(
        self,
        n: int,
        kcal_cfg: KcalEconomyConfig,
        lh_cfg: LifeHistoryConfig | None,
    ) -> None:
        land_cells = [
            (x, y)
            for y in range(N)
            for x in range(N)
            if self._fields.isWater[y, x] == 0
        ]
        n_place = min(n, len(land_cells))
        positions: list[tuple[int, int]] = self.random.sample(land_cells, n_place)

        for pos in positions:
            sex = "female" if self.random.random() < kcal_cfg.p_female else "male"
            agent = self._make_agent(sex=sex, lh_cfg=lh_cfg)
            agent.pos = pos
            self.agent_list.append(agent)
            self.occupied.add(pos)

    def _make_agent(self, sex: str, lh_cfg: LifeHistoryConfig | None) -> BaseAgent:
        from sic_games.agents.strategies.greedy import GreedyMaximizer

        decision: object
        if self._carbon_cfg is not None:
            decision = CarbonDecision(
                sigma_base=self._carbon_cfg.sigma_base,
                kappa=self._carbon_cfg.kappa,
                cred_scale=self._carbon_cfg.cred_scale,
                matthew_alpha=self._carbon_cfg.matthew_alpha,
                epsilon=self._carbon_cfg.epsilon,
                cred_bonus_per_participant=self._carbon_cfg.cred_bonus_per_participant,
                velocity_scale=self._carbon_cfg.velocity_scale,
                beta=self._carbon_cfg.status_amplification_beta,
            )
        else:
            decision = GreedyMaximizer()

        cost = KcalBurnModel(
            burn_kcal_per_day=self._kcal_cfg.burn_kcal_per_day,
            days_per_month=self._kcal_cfg.days_per_month,
        )

        perception = LocalVisionPerception()

        agent = BaseAgent(
            model=self,
            vision=3,
            metabolism=1,        # unused in kcal economy; kept for compatibility
            max_age=self._kcal_cfg.lifespan_months,  # in steps=months (1 step=1 month LOCKED)
            initial_wealth=self._reserve_full,
            decision_logic=decision,
            perception_builder=perception,
            cost_model=cost,
            traits=TraitVector(phi=0.5, psi=0.5, c1=0.5, c2=0.5),
            strategy="carbon" if self._carbon_cfg else "greedy",
            lh_config=lh_cfg,
            reserve_floor=self._reserve_floor,
            sex=sex,
        )
        return agent

    # ── Step ───────────────────────────────────────────────────────────────

    def step(self) -> None:
        self.step_count += 1
        agents = list(self.agent_list)
        self.random.shuffle(agents)

        for agent in agents:
            if not agent.alive:
                continue
            self._step_agent(agent)

        # Prune dead agents
        for a in self.agent_list:
            if not a.alive:
                self.occupied.discard(a.pos)
        self.agent_list = [a for a in self.agent_list if a.alive]

    def _step_agent(self, agent: BaseAgent) -> None:
        tf = self.terrain_field

        # 1. Perceive + decide (movement uses forage signal for navigation)
        perception = agent._perception.build(agent, tf, self.occupied)
        target = agent._decision.select_target(agent, perception, agent.random)
        old_pos = agent.pos
        if target != old_pos:
            self.occupied.discard(old_pos)
            self.occupied.add(target)
            agent.pos = target

        x, y = agent.pos

        # 2. A2.4 child age-gate: binary [JV-1: graded curve deferred]
        if agent.is_juvenile():
            # zero subsistence below age_productive_min [PROVISIONAL JV-1 seam]
            rate_step = 0.0
        else:
            # 3. A2.2 sex-based stream selection (game_stream only if enabled)
            if self._game_stream:
                forage_step = tf.forage_level(x, y)
                game_step = tf.game_level(x, y)
                rate_step = self._select_stream(agent.sex, forage_step, game_step)
            else:
                # A-1 forage-only path
                rate_step = tf.forage_level(x, y)

        # 4. Intake + reserve cap [PLACEHOLDER MR-1]
        intake = rate_step  # rate already in kcal/step; η not applied (no age ramp in kcal)
        agent.wealth = min(agent.wealth + intake, self._reserve_full)

        # 5. Burn + age + mortality
        agent.wealth -= self._burn
        agent.age += 1
        if agent.wealth <= agent.reserve_floor or agent.age >= agent.max_age:
            agent.alive = False

    def _select_stream(self, sex: str, forage_step: float, game_step: float) -> float:
        """A2.2 energy-balance stream selection. No new tunable beyond A-1 placeholders.

        Switch condition (male): game_rate < burn AND forage_rate > game_rate → use forage
        Switch condition (female): forage_rate < burn AND game_rate > forage_rate → use game
        When both streams cover burn comfortably: hold sex default.
        When both streams fail burn: hold sex default (fall to floor; mortality handles it).
        [RS-1 seam: risk/variance calc deferred]
        """
        burn = self._burn
        if sex == "male":
            if game_step >= burn:
                return game_step                     # default covers burn
            if forage_step > game_step:
                return forage_step                   # switch: forage covers better
            return game_step                         # both fail; hold default
        else:
            if forage_step >= burn:
                return forage_step                   # default covers burn
            if game_step > forage_step:
                return game_step                     # switch: game covers better
            return forage_step                       # both fail; hold default

    # ── Diagnostics ────────────────────────────────────────────────────────

    def population(self) -> int:
        return len(self.agent_list)

    def mean_reserve(self) -> float:
        if not self.agent_list:
            return 0.0
        return sum(a.wealth for a in self.agent_list) / len(self.agent_list)

    def any_alive_below_floor(self) -> bool:
        return any(a.wealth < self._reserve_floor for a in self.agent_list)
