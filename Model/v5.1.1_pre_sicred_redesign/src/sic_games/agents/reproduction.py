"""ReproductionRule abstraction — Stage 3.3+.

Fixed-N replacement (Stage 1-4):
    new_agent, fallback = reproduction_rule.replace(world, dead_pos, rng)

Dynamic birth (Stage 4.1a+):
    offspring = coordinator.attempt_birth(agent, world, rng, mean_w)
    # Returns None if no birth this step, BaseAgent if birth occurs.

Stage 4+ will add PrestigeBiasReproduction without touching the run loop.
"""
from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, Protocol

from sic_games.agents.traits import TraitVector

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.run import SugarWorld


def _clip(v: float) -> float:
    return max(0.0, min(1.0, v))


def carry_discount(N_C: int, N_carry: int, alpha_carry: float = 1.0) -> float:
    """Stage 4.5: density-dependent birth discount for C agents.

    Returns max(0, 1 - alpha_carry * N_C / N_carry).

    Behaviour:
    - N_C = 0        → 1.0 (no discount, full birth rate)
    - N_C = N_carry  → 0.0 (births fully suppressed; at alpha_carry=1.0)
    - N_C = N_carry/2 → 0.5 (half rate; at alpha_carry=1.0)
    - N_C > N_carry  → 0.0 (clamped; never negative)

    C only. Si reproduces via fission; this function is never called for Si.
    """
    return max(0.0, 1.0 - alpha_carry * (N_C / N_carry))


def _toroidal_chebyshev(
    p1: tuple[int, int], p2: tuple[int, int], w: int, h: int
) -> int:
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    return max(min(dx, w - dx), min(dy, h - dy))


def _mix_traits(
    a: TraitVector,
    b: TraitVector,
    sigma: float,
    rng: random.Random,
) -> TraitVector:
    """Midpoint average + independent Gaussian copy-error per dimension."""
    return TraitVector(
        phi=_clip((a.phi + b.phi) / 2.0 + rng.gauss(0.0, sigma)),
        psi=_clip((a.psi + b.psi) / 2.0 + rng.gauss(0.0, sigma)),
        c1=_clip((a.c1 + b.c1) / 2.0 + rng.gauss(0.0, sigma)),
        c2=_clip((a.c2 + b.c2) / 2.0 + rng.gauss(0.0, sigma)),
    )


class ReproductionRule(Protocol):
    """Protocol for the replacement rule called after each agent death.

    Returns (new_agent, fallback_fired):
      new_agent     — the spawned replacement
      fallback_fired — True if biparental fell back to random replacement
    """

    def replace(
        self,
        world: "SugarWorld",
        dead_pos: tuple[int, int],
        rng: random.Random,
    ) -> tuple["BaseAgent", bool]:
        ...


class RandomReplacement:
    """Stage 1/2/3 behaviour: spawn a fresh agent with randomly drawn traits."""

    def replace(
        self,
        world: "SugarWorld",
        dead_pos: tuple[int, int],
        rng: random.Random,
    ) -> tuple["BaseAgent", bool]:
        return world._spawn_one(), False


class BiparentalReproduction:
    """Biparental reproduction with spatial parent search.

    Parent selection: all living agents within toroidal Chebyshev distance
    parent_radius of dead_pos. Falls back to fresh random agent when < 2
    candidates are available.

    Trait mixing: per-dimension midpoint + N(0, inherit_sigma²) copy-error,
    clipped to [0, 1].
    """

    def __init__(self, parent_radius: int = 3, inherit_sigma: float = 0.05) -> None:
        self.parent_radius = parent_radius
        self.inherit_sigma = inherit_sigma

    def replace(
        self,
        world: "SugarWorld",
        dead_pos: tuple[int, int],
        rng: random.Random,
    ) -> tuple["BaseAgent", bool]:
        w, h = world.cfg.world.grid_size
        candidates = [
            a for a in world.agents
            if _toroidal_chebyshev(a.pos, dead_pos, w, h) <= self.parent_radius
        ]

        if len(candidates) >= 2:
            parent_a, parent_b = rng.sample(candidates, 2)
            mixed = _mix_traits(parent_a.traits, parent_b.traits, self.inherit_sigma, rng)
            return world._spawn_one(traits=mixed), False
        else:
            return world._spawn_one(), True


def _noise_traits(a: TraitVector, sigma: float, rng: random.Random) -> TraitVector:
    """Near-copy: each dimension gets independent Gaussian noise, clipped to [0,1]."""
    return TraitVector(
        phi=_clip(a.phi + rng.gauss(0.0, sigma)),
        psi=_clip(a.psi + rng.gauss(0.0, sigma)),
        c1=_clip(a.c1 + rng.gauss(0.0, sigma)),
        c2=_clip(a.c2 + rng.gauss(0.0, sigma)),
    )


class ReproductionCoordinator:
    """Stage 4.1a single dispatch entry point for all births.

    Dispatches to C biparental or Si fission based on agent.strategy.
    NEVER applies biparental logic to Si agents (BUG-002 guardrail).

    Stage 4.1b: DTM stress zone is now metabolism-relative when bc.k_stress is set,
    replacing the wealth-relative threshold that failed to self-regulate under
    seasonal stress (diagnosed: trough/peak birth_rate ratio=0.922).
    """

    def __init__(
        self,
        birth_c_config,
        birth_si_config,
        parent_radius: int = 3,
        inherit_sigma: float = 0.05,
        pool_cfg=None,
        lambda_inheritance: float = 0.0,
    ) -> None:
        self._bc = birth_c_config
        self._bsi = birth_si_config
        self._parent_radius = parent_radius
        self._inherit_sigma = inherit_sigma
        # Stage 4.1b: per-step counters, reset by run.py after each step
        self.births_stress_zone: int = 0
        self.births_prosperity_zone: int = 0
        self._pool_cfg = pool_cfg  # SupportPoolConfig | None
        self._pool: "SupportPool | None" = None  # set by run.py after pool creation
        # Stage 4.2: Cred-modulated birth tracking
        self._gamma_boost_sum: float = 0.0
        self._gamma_boost_count: int = 0
        # Stage 4.4: λ wealth inheritance (C only)
        self._lambda_inheritance: float = lambda_inheritance
        self._lambda_boost_sum: float = 0.0
        self._lambda_boost_count: int = 0
        # Stage 4.5: carry_discount metrics (C only)
        # N_C is fixed per step → carry_discount is the same for all attempts.
        # Cache N_C on first call; reset each step via reset_step_counters().
        self._n_c_step: int | None = None       # cached N_C for this step
        self._carry_disc_step: float = float("nan")  # carry_discount(N_C) this step
        self._p_birth_eff_sum: float = 0.0      # sum of effective birth probs
        self._p_birth_eff_count: int = 0        # birth attempts with carry active

    @property
    def gamma_birth_boost(self) -> float:
        """Mean (1 + γ·tanh(C/C***)) across C birth events this step. 1.0 if no births."""
        if self._gamma_boost_count == 0:
            return 1.0
        return self._gamma_boost_sum / self._gamma_boost_count

    @property
    def lambda_inheritance_boost(self) -> float:
        """Mean λ×mean_w wealth boost per C birth event this step. 0.0 if no births."""
        if self._lambda_boost_count == 0:
            return 0.0
        return self._lambda_boost_sum / self._lambda_boost_count

    @property
    def carry_discount_mean(self) -> float:
        """Per-step carry_discount(N_C) value. nan if carrying_cost disabled or no C agents."""
        return self._carry_disc_step

    @property
    def p_birth_effective_mean(self) -> float:
        """Mean p_birth_effective across C birth attempts this step. nan if none."""
        if self._p_birth_eff_count == 0:
            return float("nan")
        return self._p_birth_eff_sum / self._p_birth_eff_count

    def reset_step_counters(self) -> None:
        self.births_stress_zone = 0
        self.births_prosperity_zone = 0
        self._gamma_boost_sum = 0.0
        self._gamma_boost_count = 0
        self._lambda_boost_sum = 0.0
        self._lambda_boost_count = 0
        # Stage 4.5: reset carry_discount step cache
        self._n_c_step = None
        self._carry_disc_step = float("nan")
        self._p_birth_eff_sum = 0.0
        self._p_birth_eff_count = 0

    def attempt_birth(
        self,
        agent: "BaseAgent",
        world: "SugarWorld",
        rng: random.Random,
        mean_w: float,
        spatial_hash: "dict[tuple[int,int], BaseAgent] | None" = None,
    ) -> "BaseAgent | None":
        """Returns offspring if birth occurs, None otherwise.

        Dispatches to C or Si logic based on agent.strategy.
        NEVER applies biparental logic to Si agents.

        Optional spatial_hash: pre-built {pos: agent} dict from run.py.
        When provided, _carbon_birth uses O(r²) hash lookup instead of O(N) scan.
        """
        if agent.strategy == "carbon":
            return self._carbon_birth(agent, world, rng, mean_w, spatial_hash=spatial_hash)
        elif agent.strategy == "si_bounded":
            return self._si_fission(agent, world, rng, mean_w)
        else:
            raise ValueError(f"Unknown strategy: {agent.strategy}")

    def _carbon_birth(
        self,
        agent: "BaseAgent",
        world: "SugarWorld",
        rng: random.Random,
        mean_w: float,
        spatial_hash: "dict[tuple[int,int], BaseAgent] | None" = None,
    ) -> "BaseAgent | None":
        bc = self._bc
        rep_age_max = bc.rep_age_max if bc.rep_age_max is not None else (agent.max_age - 10)
        if agent.age < bc.rep_age_min or agent.age > rep_age_max:
            return None

        theta_sub = agent.metabolism * bc.tau_sub
        if agent.wealth < theta_sub:
            return None

        if mean_w <= 0:
            return None

        # Stage 4.1b: k_stress set → absolute stress zone (metabolism-relative).
        # Legacy: r_stress set → wealth-relative (proportion of mean_w).
        if bc.k_stress is not None:
            stress_threshold = theta_sub + bc.k_stress * agent.metabolism
        else:
            stress_threshold = mean_w * bc.r_stress

        if agent.wealth < stress_threshold:
            p = bc.p_max
            in_stress = True
        else:
            p = bc.p_max * math.exp(
                -(agent.wealth - stress_threshold) / (mean_w * bc.r_wealth)
            )
            in_stress = False

        # Stage 4.2: Cred-modulated birth (Turchin elite overproduction, C only)
        # P_birth_i *= (1 + γ·tanh(C_i / C***))
        gamma = bc.gamma  # 0.0 when not configured
        if gamma > 0.0:
            c_star_birth = bc.c_star_birth
            boost = 1.0 + gamma * math.tanh(agent.cred / c_star_birth)
            p = min(1.0, p * boost)
            self._gamma_boost_sum += boost
            self._gamma_boost_count += 1

        # Stage 4.5: density-dependent birth ceiling (C only, never Si).
        # carry_discount(N_C) is computed once per step; N_C cached in _n_c_step.
        cc = self._bc.carrying_cost
        if cc.enabled:
            if self._n_c_step is None:
                self._n_c_step = sum(
                    1 for a in world.agents if a.strategy == "carbon"
                )
            disc = carry_discount(self._n_c_step, cc.N_carry, cc.alpha_carry)
            self._carry_disc_step = disc
            p = p * disc
            self._p_birth_eff_sum += p
            self._p_birth_eff_count += 1

        if rng.random() >= p:
            return None

        # Check grid has space
        wg, hg = world.cfg.world.grid_size
        if len(world.occupied) >= wg * hg:
            return None

        # Find partner within Chebyshev parent_radius.
        # Task 4 (perf-fix A): spatial hash lookup O(r²) instead of O(N) scan.
        # Sort candidates by id before rng.choice() to preserve RNG determinism.
        r = self._parent_radius
        if spatial_hash is not None:
            candidates = []
            for dr in range(-r, r + 1):
                for dc in range(-r, r + 1):
                    if max(abs(dr), abs(dc)) <= r:   # Chebyshev condition
                        nr = (agent.pos[0] + dr) % wg
                        nc = (agent.pos[1] + dc) % hg
                        neighbour = spatial_hash.get((nr, nc))
                        if (neighbour is not None
                                and neighbour is not agent
                                and neighbour.strategy == "carbon"):
                            candidates.append(neighbour)
        else:
            # Fallback: O(N) scan (used when spatial_hash not supplied)
            candidates = [
                a for a in world.agents
                if a is not agent
                and a.strategy == "carbon"
                and _toroidal_chebyshev(a.pos, agent.pos, wg, hg) <= r
            ]
        # CRITICAL: sort by id before rng.choice() to preserve determinism
        candidates.sort(key=lambda a: a.unique_id)
        if not candidates:
            return None

        partner = rng.choice(candidates)
        mixed = _mix_traits(agent.traits, partner.traits, self._inherit_sigma, rng)
        offspring = world._spawn_one(traits=mixed)
        if in_stress:
            self.births_stress_zone += 1
        else:
            self.births_prosperity_zone += 1

        # Level 1 parental transfer (Stage 4.1c)
        if self._pool_cfg is not None and self._pool_cfg.enabled and offspring is not None:
            tau = self._pool_cfg.tau_parent
            floor_A = 2.0 * agent.metabolism
            floor_B = 2.0 * partner.metabolism
            transfer_A = min(tau * agent.wealth, max(0.0, agent.wealth - floor_A))
            transfer_B = min(tau * partner.wealth, max(0.0, partner.wealth - floor_B))
            transfer_total = transfer_A + transfer_B
            agent.wealth -= transfer_A
            partner.wealth -= transfer_B
            offspring.wealth += transfer_total
            if self._pool is not None:
                self._pool.record_parental_transfer(transfer_total)

        # Stage 4.4: λ wealth inheritance — additional boost proportional to mean C wealth.
        # C-only; never applied to Si (Si fission uses _si_fission exclusively).
        if self._lambda_inheritance > 0.0 and offspring is not None and mean_w > 0.0:
            boost = self._lambda_inheritance * mean_w
            offspring.wealth += boost
            self._lambda_boost_sum += boost
            self._lambda_boost_count += 1

        return offspring

    def _si_fission(
        self,
        agent: "BaseAgent",
        world: "SugarWorld",
        rng: random.Random,
        mean_w: float,
    ) -> "BaseAgent | None":
        # NEVER calls _carbon_birth — single parent only
        bsi = self._bsi
        rep_age_max = bsi.rep_age_max if bsi.rep_age_max is not None else (agent.max_age - 10)
        if agent.age < bsi.rep_age_min or agent.age > rep_age_max:
            return None

        if mean_w <= 0:
            return None
        theta_fission = mean_w * bsi.fission_wealth_mult
        if agent.wealth < theta_fission:
            return None

        if rng.random() >= bsi.p_fission_max:
            return None

        # Check grid has space
        wg, hg = world.cfg.world.grid_size
        if len(world.occupied) >= wg * hg:
            return None

        offspring_traits = _noise_traits(agent.traits, self._inherit_sigma, rng)
        # Stage 4.3: si_fission=True — Si receives lh_config=None in _spawn_one
        # so η=1.0 always (no juvenile ramp; C-only from Stage 4.3 onwards).
        offspring = world._spawn_one(traits=offspring_traits, preferred_pos=agent.pos, si_fission=True)
        # Level 1 parental transfer (Stage 4.1c)
        if self._pool_cfg is not None and self._pool_cfg.enabled and offspring is not None:
            tau = self._pool_cfg.tau_parent
            floor = 2.0 * agent.metabolism
            transfer = min(tau * agent.wealth, max(0.0, agent.wealth - floor))
            agent.wealth -= transfer
            offspring.wealth += transfer
            if self._pool is not None:
                self._pool.record_parental_transfer(transfer)
        return offspring

    def _si_hivemind_birth(
        self, agent: "BaseAgent", world: "SugarWorld", rng: random.Random
    ) -> "BaseAgent":
        raise NotImplementedError(
            "HiveMind coordinator not yet implemented. "
            "Set reproduction.coordinator='individual' for Si."
        )

    def fork(self, agent: "BaseAgent", world: "SugarWorld", rng: random.Random) -> "BaseAgent":
        raise NotImplementedError(
            "Forking not yet implemented. "
            "Flagged for Stage 7+ -- requires agent lifecycle refactor."
        )
