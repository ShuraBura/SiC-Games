from __future__ import annotations

from typing import TYPE_CHECKING

import mesa

from sic_games.agents.costs import CostModel, MetabolicOnly
from sic_games.agents.decision import DecisionLogic
from sic_games.agents.perception import LocalVisionPerception, PerceptionBuilder
from sic_games.agents.traits import TraitVector

if TYPE_CHECKING:
    from sic_games.world import SugarField


class BaseAgent(mesa.Agent):
    """Shared agent state for all Stage 1+ agent types.

    Stage 3.3 additions:
      traits -- TraitVector H_i = [φ, ψ, c1, c2]; phi is now backed by traits.
      si_cred -- null Si Cred field (always 0.0 until Stage 5+).
    Stage 4.1b additions:
      lh_config -- LifeHistoryConfig; if provided, eta(a) ramp is active.
    """

    def __init__(
        self,
        model: mesa.Model,
        vision: int,
        metabolism: int,
        max_age: int,
        initial_wealth: float,
        decision_logic: DecisionLogic,
        perception_builder: PerceptionBuilder | None = None,
        cost_model: CostModel | None = None,
        phi: float = 0.5,
        traits: TraitVector | None = None,
        strategy: str = "greedy",
        lh_config=None,
        reserve_floor: float = 0.0,
        sex: str = "female",
    ) -> None:
        super().__init__(model)
        self.vision = vision
        self.metabolism = metabolism
        self.max_age = max_age
        self.wealth = initial_wealth
        self.age = 0
        self.alive = True
        self.strategy = strategy  # Stage 4.1a: "carbon", "si_bounded", or "greedy"
        # Phase 1 Blueprint A: kcal economy fields (default 0.0 = backward-compatible)
        self.reserve_floor: float = reserve_floor
        self.sex: str = sex  # "female" or "male"; A2.1

        # Stage 4.1b: age-efficiency ramp η(a). lh_config=None → η=1.0 always.
        if lh_config is not None:
            self._forage_age_min: int = lh_config.forage_age_min
            self._forage_age_max_offset: int = lh_config.forage_age_max_offset
            self._eta_min: float = lh_config.eta_min
            self._eta_old: float = lh_config.eta_old
            self._use_eta: bool = True
        else:
            self._use_eta = False

        # Stage 3.3: trait vector H_i. If traits supplied, phi arg is ignored.
        if traits is not None:
            self.traits = traits
        else:
            self.traits = TraitVector(phi=phi, psi=0.5, c1=0.5, c2=0.5)

        # Stage 2 fields — neutral defaults leave greedy-Si unaffected
        self.cred: float = 0.0
        self._pending_cred_delta: float = 0.0
        self.wealth_velocity: float = 0.0

        # Stage 3.3: null Si Cred infrastructure (inactive until Stage 5+)
        self.si_cred: float = 0.0

        # Stage 4.3: dormancy state (Si only; C agents always stay False/0)
        self.dormant: bool = False
        self.dormant_steps: int = 0

        self._decision = decision_logic
        self._perception = perception_builder or LocalVisionPerception()
        self._cost = cost_model or MetabolicOnly()

        self.pos: tuple[int, int] = (0, 0)

        self._last_moved: bool = False
        self._last_harvested: float = 0.0

    # ------------------------------------------------------------------
    # Trait convenience properties — all existing code using agent.phi
    # continues to work; new code can use agent.traits.psi etc.
    # ------------------------------------------------------------------

    @property
    def phi(self) -> float:
        return self.traits.phi

    @phi.setter
    def phi(self, v: float) -> None:
        self.traits.phi = v

    @property
    def psi(self) -> float:
        return self.traits.psi

    @psi.setter
    def psi(self, v: float) -> None:
        self.traits.psi = v

    @property
    def c1(self) -> float:
        return self.traits.c1

    @c1.setter
    def c1(self, v: float) -> None:
        self.traits.c1 = v

    @property
    def c2(self) -> float:
        return self.traits.c2

    @c2.setter
    def c2(self, v: float) -> None:
        self.traits.c2 = v

    # ------------------------------------------------------------------
    # Stage 4.1b: age-efficiency ramp
    # ------------------------------------------------------------------

    def eta(self) -> float:
        """Harvest efficiency η(a) ∈ [eta_min, 1.0].

        Piecewise linear ramp: juvenile ramp (0→forage_age_min), full window,
        elder decline (forage_age_max→max_age). Returns 1.0 if lh_config absent.
        """
        if not self._use_eta:
            return 1.0
        a = self.age
        a_min = self._forage_age_min
        a_max = self.max_age - self._forage_age_max_offset  # per-agent
        if a < a_min:
            if a_min == 0:
                return 1.0
            return self._eta_min + (1.0 - self._eta_min) * a / a_min
        elif a <= a_max:
            return 1.0
        else:
            remaining = self.max_age - a_max
            if remaining <= 0:
                return self._eta_old
            return 1.0 - (1.0 - self._eta_old) * (a - a_max) / remaining

    def is_juvenile(self) -> bool:
        return self._use_eta and self.age < self._forage_age_min

    def is_elder(self) -> bool:
        return self._use_eta and self.age > (self.max_age - self._forage_age_max_offset)

    def act(self, sugar_field, occupied, velocity_tau=0):
        """Backward-compatible full step. Calls act_harvest then act_metabolize."""
        result = self.act_harvest(sugar_field, occupied)
        self.act_metabolize(velocity_tau=velocity_tau)
        return result

    def act_harvest(
        self,
        sugar_field: "SugarField",
        occupied: set[tuple[int, int]],
    ) -> dict:
        """Phase 1: perceive → decide → move → harvest. Does NOT pay metabolism.
        Stores results for act_metabolize(). Called before pool step."""
        perception = self._perception.build(self, sugar_field, occupied)
        target = self._decision.select_target(self, perception, self.random)

        old_pos = self.pos
        moved = target != old_pos
        if moved:
            occupied.discard(old_pos)
            occupied.add(target)
            self.pos = target

        raw_harvested = sugar_field.harvest(*self.pos)
        harvested = raw_harvested * self.eta()
        self.wealth += harvested

        self._last_moved = moved
        self._last_harvested = harvested
        return {"moved": moved, "harvested": harvested}

    def act_move(
        self,
        sugar_field: "SugarField",
        blocked: set[tuple[int, int]],
    ) -> dict:
        """Stage 6.0a substrate Phase 1a: perceive -> decide -> move. NO harvest.

        `blocked` = cells at/over the K_cell occupancy ceiling (treated exactly as the
        legacy `occupied` set by the perception filter; the agent's own current cell is
        always a candidate regardless). Does NOT mutate `blocked` — the run loop maintains
        occupancy incrementally so the next agent perceives this move. Harvest is deferred
        to the per-cell split resolved by the run loop after all agents have moved.
        """
        perception = self._perception.build(self, sugar_field, blocked)
        target = self._decision.select_target(self, perception, self.random)
        old_pos = self.pos
        moved = target != old_pos
        if moved:
            self.pos = target
        self._last_moved = moved
        self._last_harvested = 0.0   # set by the split phase
        return {"moved": moved, "old_pos": old_pos}

    def act_metabolize(self, velocity_tau: int = 0) -> None:
        """Phase 2: pay metabolism, update velocity EMA, age, check alive.
        Uses _last_moved / _last_harvested set by act_harvest(). Called after pool step."""
        moved    = self._last_moved
        harvested = self._last_harvested

        cost = self._cost.step_cost(self, {"moved": moved, "harvested": harvested})
        delta_w = harvested - cost
        self.wealth -= cost

        if velocity_tau > 0:
            alpha = 1.0 / velocity_tau
            self.wealth_velocity = (1 - alpha) * self.wealth_velocity + alpha * delta_w

        self.age += 1

        if self.wealth <= self.reserve_floor or self.age >= self.max_age:
            self.alive = False
