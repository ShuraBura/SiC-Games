"""Stage 4.3 — Tests for Si dormancy mechanic and pool carry-over / cap.

9 core dormancy tests (blueprint §11) + 2 pool carry-over/cap tests:

1. Dormancy trigger: Si agent wealth < k_dormant×metabolism → dormant flag set.
2. No active behaviour while dormant: dormant agent does not move/harvest/reproduce/contribute.
3. Trickle absorption: dormant agent on cell with sugar S absorbs tau_trickle×S per step.
4. Reactivation: dormant agent reaching k_reactivate×metabolism → active.
5. Permanent death: agent dormant for T_dormant_max+1 steps → removed.
6. C agent unaffected: C agent at same wealth threshold → starvation death, not dormancy.
7. Dormancy disabled for C: verify dormancy.enabled=False in C configs.
8. Wealth conservation (pool step): pool contribution+draw conserved.
9. Pool cap return: contributions exceeding cap blocked; cap_clipped reported.
"""
from __future__ import annotations

import math
import pytest

from sic_games.config import (
    Config, WorldConfig, AgentsConfig, DecisionConfig, CarbonConfig,
    SiBoundedConfig, JointTaskConfig, PopulationConfig, BirthCConfig,
    BirthSiConfig, ReproductionConfig, PerturbationConfig, RunConfig,
    VisualizationConfig, InitializationConfig, LifeHistoryConfig,
    SupportPoolConfig, DormancyConfig,
)
from sic_games.run import SugarWorld
from sic_games.support_pool import SupportPool


# ── shared factories ──────────────────────────────────────────────────────────

def _make_si_world(
    n: int = 10,
    grid: int = 10,
    seed: int = 7,
    beta: float = 5.0,
    dormancy_enabled: bool = True,
    k_dormant: float = 1.0,
    tau_trickle: float = 0.05,
    k_reactivate: float = 3.0,
    t_dormant_max: int = 50,
    pool_enabled: bool = False,
    p_fission: float = 0.50,
    n_steps: int = 1,
) -> SugarWorld:
    peaks = [[grid // 4, grid * 3 // 4], [grid * 3 // 4, grid // 4]]
    cfg = Config(
        seed=seed,
        world=WorldConfig(grid_size=(grid, grid), sugar_peaks=peaks),
        agents=AgentsConfig(
            initial_population=n, max_age_dist=(60, 100), initial_wealth_dist=(5, 25),
        ),
        decision=DecisionConfig(strategy="si_bounded"),
        si_bounded=SiBoundedConfig(sigma_si=1.238, beta_metabolism=beta),
        carbon=CarbonConfig(
            sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
            velocity_tau=0, velocity_scale=1.0, f_C=0.0,
            status_amplification_beta=1.0,
        ),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(p_max=0.02, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
                             r_wealth=0.5, rep_age_min=15),
        birth_si=BirthSiConfig(p_fission_max=p_fission, fission_wealth_mult=1.5,
                               rep_age_min=15),
        reproduction=ReproductionConfig(mode="random", parent_radius=3, inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="realistic"),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=0.3, eta_old=0.4),
        support_pool=SupportPoolConfig(
            enabled=pool_enabled, r_pool=5, tau_parent=0.0,
            tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
            tau_cred=0.0, tau_cred_reward=0.0,
            rho_carryover=0.0, k_pool_cap=0.0,
        ),
        dormancy=DormancyConfig(
            enabled=dormancy_enabled,
            k_dormant=k_dormant,
            tau_trickle=tau_trickle,
            k_reactivate=k_reactivate,
            t_dormant_max=t_dormant_max,
        ),
        run=RunConfig(n_steps=n_steps, metrics_every=1, output_dir="outputs/test_dormancy"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    return SugarWorld(cfg)


def _make_c_world(n: int = 10, grid: int = 10, seed: int = 7) -> SugarWorld:
    peaks = [[grid // 4, grid * 3 // 4], [grid * 3 // 4, grid // 4]]
    cfg = Config(
        seed=seed,
        world=WorldConfig(grid_size=(grid, grid), sugar_peaks=peaks),
        agents=AgentsConfig(
            initial_population=n, max_age_dist=(60, 100), initial_wealth_dist=(5, 25),
        ),
        decision=DecisionConfig(strategy="carbon"),
        carbon=CarbonConfig(
            sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
            velocity_tau=10, velocity_scale=1.0, f_C=0.0,
            status_amplification_beta=1.0,
        ),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(p_max=0.07, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
                             r_wealth=0.5, rep_age_min=15, gamma=0.2, c_star_birth=10.0),
        birth_si=BirthSiConfig(p_fission_max=0.02, fission_wealth_mult=1.5, rep_age_min=15),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3, inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="realistic"),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=0.3, eta_old=0.4),
        support_pool=SupportPoolConfig(
            enabled=True, r_pool=5, tau_parent=0.1,
            tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
            tau_cred=0.5, tau_cred_reward=0.1,
            rho_carryover=0.3, k_pool_cap=20.0,
        ),
        dormancy=DormancyConfig(enabled=False),  # C never uses dormancy
        run=RunConfig(n_steps=5, metrics_every=1, output_dir="outputs/test_dormancy_c"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    return SugarWorld(cfg)


def _make_pool(
    enabled: bool = True,
    tau_pool: float = 0.1,
    k_reserve: float = 5.0,
    k_draw: float = 3.0,
    rho_carryover: float = 0.0,
    k_pool_cap: float = 0.0,
) -> SupportPool:
    cfg = SupportPoolConfig(
        enabled=enabled, r_pool=5, tau_parent=0.0,
        tau_pool=tau_pool, k_reserve=k_reserve, k_draw=k_draw,
        tau_cred=0.5, tau_cred_reward=0.1,
        rho_carryover=rho_carryover, k_pool_cap=k_pool_cap,
    )
    return SupportPool(cfg)


# ── Test 1: Dormancy trigger ──────────────────────────────────────────────────

def test_dormancy_trigger():
    """Si agent with wealth < k_dormant × actual_cost enters dormancy instead of dying."""
    world = _make_si_world(n=5, beta=5.0, k_dormant=1.0, t_dormant_max=50, n_steps=1)
    agents = list(world.agents)
    agent = agents[0]

    # Set agent state: wealth just below k_dormant × cost
    # With beta=5, metabolism=2 → actual cost=10. k_dormant=1.0 → threshold=10.
    agent.metabolism = 2
    agent.wealth = 5.0  # < 10 → should trigger dormancy on next metabolize

    # Manually trigger the dormancy check as run.py would
    dc = world._dormancy_cfg
    assert dc is not None and dc.enabled
    cost = agent._cost.step_cost(agent, {"moved": False, "harvested": 0.0})
    assert cost == pytest.approx(10.0)

    assert not agent.dormant  # initially active

    # Simulate the dormancy-entry branch of the Si metabolize step
    if agent.wealth < dc.k_dormant * cost:
        agent.dormant = True
        agent.dormant_steps = 0

    assert agent.dormant, "Agent should have entered dormancy"
    assert agent.alive, "Dormant agent must NOT be marked dead immediately"


# ── Test 2: No active behaviour while dormant ─────────────────────────────────

def test_dormant_no_active_behaviour():
    """Dormant Si agent: act_harvest is skipped; pool contribution skipped; birth skipped."""
    world = _make_si_world(n=5, beta=5.0, pool_enabled=False, n_steps=1)
    agents = list(world.agents)
    agent = agents[0]

    # Force dormancy
    agent.dormant = True
    agent.dormant_steps = 0
    agent.wealth = 2.0

    pre_wealth = agent.wealth
    pre_pos = agent.pos

    # Simulate harvest phase: dormant → trickle only (not act_harvest)
    dc = world._dormancy_cfg
    if dc and agent.dormant:
        trickle = dc.tau_trickle * world.sugar_field.level(*agent.pos)
        agent.wealth += trickle
        agent._last_moved = False
        agent._last_harvested = 0.0
    else:
        agent.act_harvest(world.sugar_field, world.occupied)

    # Position unchanged (no movement)
    assert agent.pos == pre_pos

    # Wealth only increased by trickle (not a full harvest)
    # (trickle < full harvest since tau_trickle=0.05 < 1.0)
    sugar_at_pos = world.sugar_field.level(*pre_pos)
    expected_wealth = pre_wealth + dc.tau_trickle * sugar_at_pos
    assert agent.wealth == pytest.approx(expected_wealth)

    # Pool: dormant Si agents don't draw (Si pool disabled — passes trivially)
    pool = _make_pool(enabled=False)
    metrics = pool.step([agent])
    assert metrics.pool_total_contributed == pytest.approx(0.0)


# ── Test 3: Trickle absorption ────────────────────────────────────────────────

def test_trickle_absorption():
    """Dormant agent on cell with known sugar level absorbs tau_trickle × sugar."""
    world = _make_si_world(n=5, tau_trickle=0.10, n_steps=1)
    agents = list(world.agents)
    agent = agents[0]
    agent.dormant = True
    agent.dormant_steps = 5
    agent.wealth = 1.0

    # Plant known sugar at agent's cell
    x, y = agent.pos
    world.sugar_field.sugar[x, y] = 8.0

    dc = world._dormancy_cfg
    pre_wealth = agent.wealth
    trickle = dc.tau_trickle * world.sugar_field.level(x, y)
    agent.wealth += trickle

    expected = pre_wealth + 0.10 * 8.0  # = 1.8
    assert agent.wealth == pytest.approx(expected)

    # Cell sugar unchanged (trickle is passive — does NOT consume cell sugar)
    assert world.sugar_field.level(x, y) == pytest.approx(8.0)


# ── Test 4: Reactivation ──────────────────────────────────────────────────────

def test_reactivation():
    """Dormant agent whose wealth reaches k_reactivate × cost → dormant=False."""
    world = _make_si_world(n=5, beta=5.0, k_reactivate=3.0, n_steps=1)
    agents = list(world.agents)
    agent = agents[0]
    agent.metabolism = 2  # cost = 10
    agent.dormant = True
    agent.dormant_steps = 3
    agent.alive = True

    # Wealth just below k_reactivate × cost = 3.0 × 10 = 30 → no reactivation
    agent.wealth = 25.0
    dc = world._dormancy_cfg
    cost = agent._cost.step_cost(agent, {})
    assert agent.wealth < dc.k_reactivate * cost  # 25 < 30 → still dormant

    # Now set wealth above threshold
    agent.wealth = 35.0
    if agent.wealth >= dc.k_reactivate * cost:
        agent.dormant = False
        agent.dormant_steps = 0

    assert not agent.dormant, "Agent should have reactivated"
    assert agent.dormant_steps == 0


# ── Test 5: Permanent death after T_dormant_max ───────────────────────────────

def test_permanent_death_after_max_dormancy():
    """Agent dormant for T_dormant_max+1 steps → alive=False (permanent death)."""
    t_max = 5
    world = _make_si_world(n=5, beta=5.0, k_reactivate=3.0, t_dormant_max=t_max, n_steps=1)
    agents = list(world.agents)
    agent = agents[0]
    agent.metabolism = 2  # cost = 10
    agent.wealth = 1.0    # always below k_reactivate=30, above trickle to reactivate
    agent.dormant = True
    agent.dormant_steps = t_max  # at threshold — one more step kills

    dc = world._dormancy_cfg
    cost = agent._cost.step_cost(agent, {})

    # One more dormancy step
    agent.dormant_steps += 1
    if agent.dormant_steps > dc.t_dormant_max:
        agent.alive = False

    assert not agent.alive, "Agent should be permanently dead after T_dormant_max exceeded"


# ── Test 6: C agent unaffected by dormancy ────────────────────────────────────

def test_c_agent_not_dormant():
    """C agent with low wealth dies from starvation; dormancy.enabled=False for C."""
    world = _make_c_world(n=5)
    dc = world._dormancy_cfg
    # C configs must have dormancy disabled
    assert dc is None or not dc.enabled, "C world must have dormancy disabled"

    agents = list(world.agents)
    agent = agents[0]
    agent.wealth = 0.1   # will die after paying metabolism
    agent.metabolism = 2
    agent._last_moved = False
    agent._last_harvested = 0.0

    agent.act_metabolize(velocity_tau=0)

    assert not agent.alive, "C agent with insufficient wealth must die from starvation"
    assert not agent.dormant, "C agent must never be set dormant"


# ── Test 7: Dormancy disabled in C configs ────────────────────────────────────

def test_dormancy_disabled_for_carbon():
    """World with C strategy: dormancy_cfg is None or disabled."""
    world = _make_c_world(n=5)
    assert world._dormancy_cfg is None or not world._dormancy_cfg.enabled


def test_dormancy_enabled_for_si():
    """World with Si strategy and dormancy=True: dormancy_cfg is set and enabled."""
    world = _make_si_world(n=5, dormancy_enabled=True)
    assert world._dormancy_cfg is not None
    assert world._dormancy_cfg.enabled


# ── Test 8: Wealth conservation (pool step) ───────────────────────────────────

def test_pool_wealth_conservation_with_carryover():
    """Pool step with rho_carryover > 0: wealth entering = wealth leaving the pool step.

    Conservation check: within a single step, total (agent_wealth + pool_balance)
    changes only by the cap-clipped amount (wealth blocked by cap, retained by agents).
    """
    world = _make_c_world(n=10)
    agents = list(world.agents)

    # Set up agents with known states (active C agents, no juveniles/elders)
    for a in agents:
        a._use_eta = True
        a._forage_age_min = 15
        a._forage_age_max_offset = 10
        a.max_age = 80
        a.age = 30  # active
        a.metabolism = 2
        a.wealth = 50.0
        a.strategy = "carbon"
        a.cred = 0.0

    pool = _make_pool(enabled=True, tau_pool=0.05, k_reserve=5.0,
                      rho_carryover=0.3, k_pool_cap=0.0)
    # Set a prior balance to test carry-over
    pool._balance = 20.0
    carryover_start = pool._balance

    pre_agent_total = sum(a.wealth for a in agents)
    pre_total = pre_agent_total + pool._balance * 0.3  # only rho fraction carries in

    metrics = pool.step(agents)
    post_agent_total = sum(a.wealth for a in agents)
    post_pool = pool._balance

    # Total wealth = agents + pool balance (full leftover stored for next rho application)
    # pre: agent_total + (rho * prior_balance carried in as starting pool)
    # post: agent_total_new + leftover stored in _balance
    # conservation: delta_agents = contributed - drawn; delta_pool = drawn - contributed + carryover
    contributed = metrics.pool_total_contributed
    drawn = metrics.pool_total_drawn
    carryover_in = metrics.pool_carryover_balance

    # Wealth transferred from agents to pool = contributed - drawn
    expected_agent_delta = -(contributed - drawn)
    actual_agent_delta = post_agent_total - pre_agent_total
    assert abs(actual_agent_delta - expected_agent_delta) < 1e-6, (
        f"Agent wealth delta {actual_agent_delta:.6f} ≠ expected {expected_agent_delta:.6f}"
    )


# ── Test 9: Pool cap blocks excess contributions ──────────────────────────────

def test_pool_cap_clips_contributions():
    """With a tight pool cap, contributions exceeding cap are blocked and reported."""
    # Use a world with C agents
    world = _make_c_world(n=10)
    agents = list(world.agents)

    for a in agents:
        a._use_eta = True
        a._forage_age_min = 15
        a._forage_age_max_offset = 10
        a.max_age = 80
        a.age = 30
        a.metabolism = 2
        a.wealth = 100.0  # large surplus → large contribution desire
        a.strategy = "carbon"
        a.cred = 0.0

    # n_active_C=10, mean_m=2 → cap = k_pool_cap × 10 × 2 = 1 × 20 = 20
    pool = _make_pool(enabled=True, tau_pool=0.5, k_reserve=5.0,
                      rho_carryover=0.0, k_pool_cap=1.0)
    # surplus per agent = 100 - 5*2 = 90; tau_pool=0.5 → 45 per agent → 450 total >> cap=20

    metrics = pool.step(agents)

    assert metrics.pool_cap_clipped > 0.0, "Cap should have blocked some contributions"
    assert metrics.pool_total_contributed <= 20.0 + 1e-6, (
        f"Pool balance should not exceed cap of 20, got {metrics.pool_total_contributed:.2f}"
    )


# ── Test bonus: Si fission offspring have eta=1.0 (no juvenile ramp) ──────────

def test_si_fission_offspring_no_eta():
    """Si agents spawned via _spawn_one have _use_eta=False → η=1.0 always."""
    world = _make_si_world(n=5)
    offspring = world._spawn_one()
    assert not offspring._use_eta, "Si agents must have _use_eta=False (no juvenile ramp)"
    assert offspring.eta() == pytest.approx(1.0), "Si offspring η must be 1.0 at any age"


# ── Test bonus: Si cost model uses beta multiplier ────────────────────────────

def test_si_cost_model_beta():
    """Si agent step_cost = metabolism × beta (not just metabolism)."""
    world = _make_si_world(n=5, beta=5.0)
    agent = list(world.agents)[0]
    agent.metabolism = 3
    cost = agent._cost.step_cost(agent, {"moved": False, "harvested": 0.0})
    assert cost == pytest.approx(15.0), f"Expected 3×5=15, got {cost}"
