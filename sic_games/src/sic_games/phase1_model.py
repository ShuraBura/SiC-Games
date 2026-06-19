"""phase1_model.py — TerrainWorld: Mesa model for Phase 1.

Replaces the Sugarscape SugarField harvest path with terrain kcal economy.
C agents only. Si excluded (Phase 1 terrain path).

Economy (A-1, kcal):
  burn_per_step  = burn_kcal_per_day × days_per_month                     [NOMINAL]
  intake_per_step = rate_kcal_per_hr × foraging_hours_per_day × days/month [NOMINAL]
  reserve += intake − burn; death at reserve ≤ reserve_floor              [PLACEHOLDER MR-1]
  reserve capped at reserve_full                                            [PLACEHOLDER MR-1]

Sex-based stream selection (A-2):
  female default → forage_kcal stream; male default → game_kcal stream;
  switch only under deficit pressure (no new tunable). [non-rivalrous; CC-1 deferred]

Child age-gate (A-2, binary): below age_productive_min → intake = 0. [JV-1 seam]

Multi-occupancy rivalry (A-3, opt-in `substrate_cfg`, supervisor-directed 2026-06-16):
  The default Blueprint-A path is NON-rivalrous (each agent gets the full cell rate) and
  has no density-dependence, so reproduction would explode with no carrying capacity.
  When a `SubstrateConfig` is supplied (enabled), the model adopts the Stage-6.0a
  multi-occupancy substrate on the terrain field:
    - movement: `diffusion_select_target` (von-Neumann r=1, per-capita-yield utility,
      self-limiting — a mobbed rich cell offers a small share so it stops attracting).
    - harvest: the cell's total return rate S = forage_level(cell) is SPLIT among its
      occupants via `compute_harvest_shares` (κ=contest_exponent: 0 → even split /
      "Cred=1 for all"; κ>0 → share ∝ (φ+ε)^κ). Affinity/crowd hooks held neutral (=1).
  Density-dependence (hence a terrain-discovered carrying capacity ≈ Σ S_cell/burn over
  survivable cells) emerges from rivalry, NOT an imposed N_carry. This is a minimal
  PROVISIONAL preview of CC-1; S = forage-rate-as-cell-total under-estimates the true
  NPP-derived extractable rate (CC-1 deferred) — the *dynamics* are the finding, the
  absolute capacity is provisional. Forage-only (game stream off) for this shakedown.

Demographic layer (A-3, opt-in `reproduction=True`):
  Blueprint A shipped death-only. A minimal PROVISIONAL reproduction rule is added so the
  population can settle: eligible = alive, age ≥ repro_min_age, reserve ≥ birth_threshold;
  then reproduce with prob p_birth. On birth the parent pays birth_cost; the child is
  placed on the parent's cell (multi-occupancy; it disperses via diffusion), age 0,
  reserve = child_endowment. NOT the full C biparental/Cred reproduction (deferred to the
  Phase-1 demographic stage / RECAL). All repro params are [PROVISIONAL — shakedown].

Placement: pass `placement_positions` (a list of (x,y), len = n_agents) to use a
deterministic founder-cluster layout instead of random land sampling.
"""
from __future__ import annotations

import mesa

from sic_games.agents.base import BaseAgent
from sic_games.agents.costs import KcalBurnModel
from sic_games.agents.perception import LocalVisionPerception
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.traits import TraitVector
from sic_games.config import KcalEconomyConfig, LifeHistoryConfig, SubstrateConfig
from sic_games.demography import (
    DemographyConfig, density_mult, energetic_fertility_factor, is_fertile, risk_mult, synergy_mult,
)
from sic_games.substrate import compute_harvest_shares, diffusion_select_target
from sic_games.terrain import N, WorldFields, generate_world
from sic_games.terrain_field import TerrainField

_CELL_KM2 = 100.0   # CC-1: each cell = 100 km² (local density = cell occupancy / _CELL_KM2)

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

    Death-only by default (Blueprint A). Set `reproduction=True` for the A-3
    demographic layer. No SugarField in the C harvest path.
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
        placement_positions: list[tuple[int, int]] | None = None,
        substrate_cfg: SubstrateConfig | None = None,
        harvest_field=None,   # CC-1: swap the rivalrous cell yield (default = terrain_field forage)
        # ── A-3 demographic layer (opt-in; PROVISIONAL shakedown params) ──
        reproduction: bool = False,
        repro_min_age: int = 15,
        birth_threshold: float = 80_000.0,
        birth_cost: float = 40_000.0,
        child_endowment: float = 40_000.0,
        p_birth: float = 0.10,
        # ── Demographic-stage core (opt-in): Siler mortality + IBI reproduction ──
        demography_cfg: DemographyConfig | None = None,
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
        self._placement_positions = placement_positions
        self._substrate_cfg = substrate_cfg
        self._rivalrous = substrate_cfg is not None and substrate_cfg.enabled
        self._harvest_field = harvest_field if harvest_field is not None else self.terrain_field

        # demographic layer
        self._reproduction = reproduction
        self._repro_min_age = repro_min_age
        self._birth_threshold = birth_threshold
        self._birth_cost = birth_cost
        self._child_endowment = child_endowment
        self._p_birth = p_birth
        # demographic-stage core (opt-in): sex-specific Siler + IBI; modulators OFF here (2a-pre).
        self._demog = demography_cfg
        if demography_cfg is not None:
            self._siler = {"female": demography_cfg.siler("female"),
                           "male": demography_cfg.siler("male")}
            self._siler_both = demography_cfg.siler()
            land = self._fields.isWater == 0
            self._risk_ref = float(self._fields.risk[land].mean())  # mean land risk (normalization)
            self.a2_cap_hits = 0   # red-team m-4: agent-steps where the a2_eff cap binds

        self.agent_list: list[BaseAgent] = []
        self.occupied: set[tuple[int, int]] = set()
        self.step_count: int = 0
        # per-step demographic counters (read by diagnostics each step)
        self.births_this_step: int = 0
        self.deaths_starv_this_step: int = 0
        self.deaths_senesc_this_step: int = 0

        self._init_agents(n_agents, kcal_cfg, lh_cfg)

    # ── Initialisation ─────────────────────────────────────────────────────

    def _init_agents(
        self,
        n: int,
        kcal_cfg: KcalEconomyConfig,
        lh_cfg: LifeHistoryConfig | None,
    ) -> None:
        if self._placement_positions is not None:
            positions: list[tuple[int, int]] = list(self._placement_positions)
        else:
            land_cells = [
                (x, y)
                for y in range(N)
                for x in range(N)
                if self._fields.isWater[y, x] == 0
            ]
            n_place = min(n, len(land_cells))
            positions = self.random.sample(land_cells, n_place)

        for pos in positions:
            sex = "female" if self.random.random() < kcal_cfg.p_female else "male"
            agent = self._make_agent(sex=sex, lh_cfg=lh_cfg)
            agent.pos = pos
            if self._demog is not None:
                agent.age = self._sample_founder_age()   # staggered founders (stationary ∝ l(x))
            self.agent_list.append(agent)
            self.occupied.add(pos)   # set: founder stacking (many agents, one cell) is allowed

    def _sample_founder_age(self) -> int:
        """Staggered founder age (months) ∝ survivorship l(x) — the stationary / young pyramid."""
        if not hasattr(self, "_founder_age_pool"):
            p = self._siler_both
            ages = list(range(0, 90 * 12, 6))
            wts = [p.survivorship(a / 12.0) for a in ages]
            self._founder_age_pool = (ages, wts)
        ages, wts = self._founder_age_pool
        return int(self.random.choices(ages, weights=wts, k=1)[0])

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

        agent = BaseAgent(
            model=self,
            vision=3,
            metabolism=1,        # unused in kcal economy; kept for compatibility
            max_age=self._kcal_cfg.lifespan_months,  # in steps=months (1 step=1 month LOCKED)
            initial_wealth=self._reserve_full,
            decision_logic=decision,
            perception_builder=LocalVisionPerception(),
            cost_model=cost,
            traits=TraitVector(phi=0.5, psi=0.5, c1=0.5, c2=0.5),
            strategy="carbon" if self._carbon_cfg else "greedy",
            lh_config=lh_cfg,
            reserve_floor=self._reserve_floor,
            sex=sex,
        )
        agent.months_since_birth = 10**9   # IBI counter (huge → first birth not blocked by refractory)
        agent.parity = 0
        return agent

    # ── Step ───────────────────────────────────────────────────────────────

    def step(self) -> None:
        self.step_count += 1
        self.births_this_step = 0
        self.deaths_starv_this_step = 0
        self.deaths_senesc_this_step = 0

        if self._rivalrous:
            self._step_rivalrous()
        else:
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

        # Demographic layer: births (opt-in)
        if self._demog is not None:
            self._do_births_ibi()
        elif self._reproduction:
            self._do_births()
        self.occupied = {a.pos for a in self.agent_list}

    def _step_rivalrous(self) -> None:
        """Stage-6.0a multi-occupancy substrate on the terrain field (forage-only).
        Diffusion movement (per-capita yield) → per-cell harvest split → metabolism."""
        sc = self._substrate_cfg
        kappa = sc.contest_exponent
        phi_eps = sc.phi_epsilon
        tf = self._harvest_field   # CC-1 capacity field (or terrain forage if none)

        # 1. occupancy maps
        occ_count: dict[tuple[int, int], int] = {}
        occ_wsum: dict[tuple[int, int], float] | None = {} if kappa > 0.0 else None
        for a in self.agent_list:
            occ_count[a.pos] = occ_count.get(a.pos, 0) + 1
            if occ_wsum is not None:
                wt = (a.phi + phi_eps) ** kappa if a.strategy == "carbon" else 1.0
                occ_wsum[a.pos] = occ_wsum.get(a.pos, 0.0) + wt

        # 2. diffusion movement (per-capita-yield, self-limiting)
        agents = list(self.agent_list)
        self.random.shuffle(agents)
        for agent in agents:
            old = agent.pos
            temp = None
            tfn = getattr(agent._decision, "temperature", None)
            if callable(tfn):
                temp = tfn(agent)
            target = diffusion_select_target(agent, tf, occ_count, occ_wsum, sc, agent.random, temp)
            if target != old and self._fields.isWater[target[1], target[0]] != 0:
                target = old   # terrain guard: never step onto water (diffusion is water-blind)
            if target != old:
                occ_count[old] -= 1
                if occ_count[old] == 0:
                    del occ_count[old]
                occ_count[target] = occ_count.get(target, 0) + 1
                if occ_wsum is not None:
                    wt = (agent.phi + phi_eps) ** kappa if agent.strategy == "carbon" else 1.0
                    occ_wsum[old] = occ_wsum.get(old, 0.0) - wt
                    occ_wsum[target] = occ_wsum.get(target, 0.0) + wt
                agent.pos = target
        self.occupied = set(occ_count.keys())

        # 3. per-cell harvest split (forage-only; S = cell total return rate, flow)
        occ_lists: dict[tuple[int, int], list[BaseAgent]] = {}
        for a in self.agent_list:
            occ_lists.setdefault(a.pos, []).append(a)
        for (cx, cy), occ in occ_lists.items():
            S = tf.level(cx, cy)
            shares = compute_harvest_shares(occ, S, kappa, phi_eps)
            for a, sh in zip(occ, shares):
                intake = 0.0 if a.is_juvenile() else sh
                a.wealth = min(a.wealth + intake, self._reserve_full)

        # 4. metabolism: burn + age + mortality (cause-attributed)
        demog = self._demog
        for a in self.agent_list:
            a.wealth -= self._burn
            a.age += 1
            if demog is not None:
                a.months_since_birth += 1
                if a.wealth <= a.reserve_floor:          # starvation backstop (reserve ≤ floor)
                    a.alive = False
                    self.deaths_starv_this_step += 1
                else:
                    a2m = self._a2_mult(a, occ_count)     # Step-2 a2 modulators (1.0 if all flags off)
                    if a.random.random() < self._siler[a.sex].monthly_death_prob(a.age, a2m):
                        a.alive = False                   # Siler baseline+senescence
                        self.deaths_senesc_this_step += 1
            elif a.wealth <= a.reserve_floor:
                a.alive = False
                self.deaths_starv_this_step += 1
            elif a.age >= a.max_age:
                a.alive = False
                self.deaths_senesc_this_step += 1

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
            rate_step = 0.0
        else:
            # 3. A2.2 sex-based stream selection (game_stream only if enabled)
            if self._game_stream:
                forage_step = tf.forage_level(x, y)
                game_step = tf.game_level(x, y)
                rate_step = self._select_stream(agent.sex, forage_step, game_step)
            else:
                rate_step = tf.forage_level(x, y)   # A-1 forage-only path

        # 4. Intake + reserve cap [PLACEHOLDER MR-1]
        agent.wealth = min(agent.wealth + rate_step, self._reserve_full)

        # 5. Burn + age + mortality (with cause attribution)
        agent.wealth -= self._burn
        agent.age += 1
        if agent.wealth <= agent.reserve_floor:
            agent.alive = False
            self.deaths_starv_this_step += 1
        elif agent.age >= agent.max_age:
            agent.alive = False
            self.deaths_senesc_this_step += 1

    def _select_stream(self, sex: str, forage_step: float, game_step: float) -> float:
        """A2.2 energy-balance stream selection. No new tunable beyond A-1 placeholders."""
        burn = self._burn
        if sex == "male":
            if game_step >= burn:
                return game_step
            if forage_step > game_step:
                return forage_step
            return game_step
        else:
            if forage_step >= burn:
                return forage_step
            if game_step > forage_step:
                return game_step
            return forage_step

    # ── Demographic layer (A-3) ──────────────────────────────────────────────

    def _do_births(self) -> None:
        """Asexual, reserve-gated reproduction [PROVISIONAL shakedown]. Child is placed on
        the parent's cell (multi-occupancy allowed); density-dependence comes from rivalry
        (crowded cells → small per-capita share → starvation), not from space. The child
        disperses next step via diffusion movement. Deterministic agent_list order."""
        newborns: list[BaseAgent] = []
        for agent in self.agent_list:
            if agent.age < self._repro_min_age:
                continue
            if agent.wealth < self._birth_threshold:
                continue
            if self.random.random() < self._p_birth:
                agent.wealth -= self._birth_cost
                sex = "female" if self.random.random() < self._kcal_cfg.p_female else "male"
                child = self._make_agent(sex=sex, lh_cfg=self._lh_cfg)
                child.pos = agent.pos
                child.wealth = self._child_endowment
                child.age = 0
                newborns.append(child)
                self.births_this_step += 1
        self.agent_list.extend(newborns)

    def _do_births_ibi(self) -> None:
        """Demographic-stage reproduction: female-only, IBI-gated (Siler+IBI core). Maternal folded
        into the all-cause female schedule (approach (ii)); the energetic fertility modifier is OFF
        here (2a-pre strict stability test). Child on the parent's cell; disperses via diffusion."""
        cfg = self._demog
        newborns: list[BaseAgent] = []
        for a in self.agent_list:
            if a.sex != "female":
                continue
            if not is_fertile(a.age, a.months_since_birth, cfg):
                continue
            p_birth = cfg.fecundability
            if cfg.enable_energetic_fertility:                 # economy fix (A): births scale w/ reserve
                p_birth *= energetic_fertility_factor(a.wealth, a.reserve_floor, self._reserve_full)
            if a.random.random() < p_birth:
                a.months_since_birth = 0
                a.parity += 1
                csex = "male" if a.random.random() < cfg.srb_male else "female"
                child = self._make_agent(sex=csex, lh_cfg=self._lh_cfg)
                child.pos = a.pos
                child.age = 0
                child.wealth = self._reserve_full
                newborns.append(child)
                self.births_this_step += 1
        self.agent_list.extend(newborns)

    def _a2_mult(self, a, occ_count) -> float:
        """Step-2 baseline-mortality (a2) multiplier from the live modulators (1.0 if all flags off) —
        the only Siler term the world modulates. Capped (red-team n-1). Pathogen OFF in 2b."""
        cfg = self._demog
        m = 1.0
        if cfg.enable_terrain_risk:
            m *= risk_mult(float(self._fields.risk[a.pos[1], a.pos[0]]), self._risk_ref, cfg.risk_cap)
        if cfg.enable_density_disease:
            rho = occ_count.get(a.pos, 1) / _CELL_KM2           # agents/km²
            m *= density_mult(rho, cfg.dens_delta, cfg.dens_rho_half)
        if cfg.enable_nutrition_synergy:
            m *= synergy_mult(a.wealth, a.reserve_floor, self._reserve_full, cfg.mu_max)
        if m > cfg.a2_cap:
            self.a2_cap_hits += 1
            return cfg.a2_cap
        return m

    # ── Diagnostics ──────────────────────────────────────────────────────────

    def population(self) -> int:
        return len(self.agent_list)

    def mean_reserve(self) -> float:
        if not self.agent_list:
            return 0.0
        return sum(a.wealth for a in self.agent_list) / len(self.agent_list)

    def mean_age(self) -> float:
        if not self.agent_list:
            return 0.0
        return sum(a.age for a in self.agent_list) / len(self.agent_list)

    def any_alive_below_floor(self) -> bool:
        return any(a.wealth < self._reserve_floor for a in self.agent_list)
