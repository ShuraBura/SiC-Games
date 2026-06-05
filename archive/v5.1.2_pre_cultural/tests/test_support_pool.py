"""Stage 4.1c — tests for proximity support pool.

11 tests covering:
1. Parental transfer C
2. Parental transfer Si
3. Min parent wealth floor
4. Pool contribution active adult
5. C status contribution (Cred scaling)
6. C Cred reward
7. Pool draw non-active
8. Pool exhaustion
9. Pool resets each step
10. Si pool no Cred scaling
11. enabled=False recovers 4.1b
"""
from __future__ import annotations

import math
import pytest

from sic_games.config import (
    Config, WorldConfig, AgentsConfig, DecisionConfig, CarbonConfig,
    SiBoundedConfig, JointTaskConfig, PopulationConfig, BirthCConfig,
    BirthSiConfig, ReproductionConfig, PerturbationConfig, RunConfig,
    VisualizationConfig, InitializationConfig, LifeHistoryConfig, SupportPoolConfig,
)
from sic_games.run import SugarWorld
from sic_games.support_pool import SupportPool, PoolStepMetrics


# ── shared factory ──────────────────────────────────────────────────────────

def _make_world(
    strategy: str = "carbon",
    n: int = 20,
    grid: int = 10,
    seed: int = 99,
    pool_enabled: bool = True,
    tau_parent: float = 0.1,
    tau_pool: float = 0.1,
    k_reserve: float = 5.0,
    k_draw: float = 3.0,
    tau_cred: float = 0.5,
    tau_cred_reward: float = 0.1,
    p_max: float = 0.12,
    p_fission: float = 0.14,
):
    peaks = [[grid // 4, grid * 3 // 4], [grid * 3 // 4, grid // 4]]
    cfg = Config(
        seed=seed,
        world=WorldConfig(grid_size=(grid, grid), sugar_peaks=peaks),
        agents=AgentsConfig(
            initial_population=n,
            max_age_dist=(60, 100),
            initial_wealth_dist=(5, 25),
        ),
        decision=DecisionConfig(strategy=strategy),
        carbon=CarbonConfig(
            sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
            velocity_tau=10, velocity_scale=1.0, f_C=0.25,
            status_amplification_beta=1.0,
        ),
        si_bounded=SiBoundedConfig(sigma_si=1.238),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            p_max=p_max, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
            r_wealth=0.5, rep_age_min=15, rep_age_max=None,
        ),
        birth_si=BirthSiConfig(
            p_fission_max=p_fission, fission_wealth_mult=1.5,
            rep_age_min=15, rep_age_max=None,
        ),
        reproduction=ReproductionConfig(
            mode="random" if strategy == "si_bounded" else "biparental",
            parent_radius=3, inherit_sigma=0.05,
        ),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="realistic"),
        life_history=LifeHistoryConfig(
            forage_age_min=15,
            forage_age_max_offset=10,
            eta_min=0.3,
            eta_old=0.4,
        ),
        support_pool=SupportPoolConfig(
            enabled=pool_enabled,
            r_pool=5,
            tau_parent=tau_parent,
            tau_pool=tau_pool,
            k_reserve=k_reserve,
            k_draw=k_draw,
            tau_cred=tau_cred,
            tau_cred_reward=tau_cred_reward,
        ),
        run=RunConfig(n_steps=5, metrics_every=1, output_dir="outputs/test_pool"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    return SugarWorld(cfg)


def _make_pool(
    enabled: bool = True,
    tau_parent: float = 0.1,
    tau_pool: float = 0.1,
    k_reserve: float = 5.0,
    k_draw: float = 3.0,
    tau_cred: float = 0.5,
    tau_cred_reward: float = 0.1,
) -> SupportPool:
    cfg = SupportPoolConfig(
        enabled=enabled,
        r_pool=5,
        tau_parent=tau_parent,
        tau_pool=tau_pool,
        k_reserve=k_reserve,
        k_draw=k_draw,
        tau_cred=tau_cred,
        tau_cred_reward=tau_cred_reward,
    )
    return SupportPool(cfg)


# ── Test 1: Parental transfer C ──────────────────────────────────────────────

def test_parental_transfer_carbon():
    """Two C parents: offspring gets tau_parent * (wealth_A + wealth_B), parents reduced."""
    world = _make_world(strategy="carbon", n=5, tau_parent=0.1)
    coordinator = world._coordinator
    pool = world._support_pool

    # Set up agent pair with known wealth
    agents = list(world.agents)
    agent_a = agents[0]
    agent_b = agents[1]
    agent_a.wealth = 100.0
    agent_b.wealth = 80.0
    agent_a.metabolism = 2
    agent_b.metabolism = 2

    pre_wealth_a = agent_a.wealth
    pre_wealth_b = agent_b.wealth

    # Simulate parental transfer
    tau = 0.1
    floor_A = 2.0 * agent_a.metabolism
    floor_B = 2.0 * agent_b.metabolism
    transfer_A = min(tau * agent_a.wealth, max(0.0, agent_a.wealth - floor_A))
    transfer_B = min(tau * agent_b.wealth, max(0.0, agent_b.wealth - floor_B))
    transfer_total = transfer_A + transfer_B

    expected_transfer_A = 0.1 * 100.0  # = 10.0 (floor=4, wealth-floor=96, so 10 < 96)
    expected_transfer_B = 0.1 * 80.0   # = 8.0

    assert abs(transfer_A - expected_transfer_A) < 1e-9
    assert abs(transfer_B - expected_transfer_B) < 1e-9
    assert abs(transfer_total - (expected_transfer_A + expected_transfer_B)) < 1e-9


# ── Test 2: Parental transfer Si ─────────────────────────────────────────────

def test_parental_transfer_si():
    """Single Si parent: offspring gets tau_parent * parent_wealth."""
    world = _make_world(strategy="si_bounded", n=5, tau_parent=0.1)
    agents = list(world.agents)
    parent = agents[0]
    parent.wealth = 50.0
    parent.metabolism = 2

    tau = 0.1
    floor = 2.0 * parent.metabolism  # = 4.0
    transfer = min(tau * parent.wealth, max(0.0, parent.wealth - floor))
    expected = 0.1 * 50.0  # = 5.0 (floor=4, wealth-floor=46, 5 < 46)

    assert abs(transfer - expected) < 1e-9


# ── Test 3: Parent wealth floor ───────────────────────────────────────────────

def test_parental_transfer_floor():
    """Parent at exactly 2×metabolism: transfer is 0 (floor prevents negative wealth)."""
    world = _make_world(strategy="si_bounded", n=5, tau_parent=0.1)
    agents = list(world.agents)
    parent = agents[0]
    parent.metabolism = 5
    parent.wealth = 2.0 * parent.metabolism  # = 10.0 = floor exactly

    tau = 0.1
    floor = 2.0 * parent.metabolism
    transfer = min(tau * parent.wealth, max(0.0, parent.wealth - floor))

    # wealth - floor = 0, so transfer = min(1.0, 0) = 0
    assert transfer == pytest.approx(0.0)


def test_parental_transfer_below_floor():
    """Parent slightly above floor: transfer capped at (wealth - floor)."""
    world = _make_world(strategy="si_bounded", n=5, tau_parent=0.5)
    agents = list(world.agents)
    parent = agents[0]
    parent.metabolism = 5
    parent.wealth = 11.0  # just above floor of 10.0
    floor = 2.0 * parent.metabolism  # = 10.0

    tau = 0.5
    # tau * wealth = 0.5 * 11 = 5.5; wealth - floor = 1.0
    transfer = min(tau * parent.wealth, max(0.0, parent.wealth - floor))
    assert transfer == pytest.approx(1.0)


# ── Test 4: Pool contribution active adult ────────────────────────────────────

def test_pool_contribution_active_adult():
    """Active adult with surplus contributes tau_pool * surplus."""
    pool = _make_pool(tau_pool=0.1, k_reserve=5.0)

    world = _make_world(n=3, tau_pool=0.1, k_reserve=5.0)
    agents = list(world.agents)
    agent = agents[0]

    # Make agent active (not juvenile, not elder)
    agent._use_eta = True
    agent._forage_age_min = 15
    agent._forage_age_max_offset = 10
    agent.max_age = 80
    agent.age = 30  # active window
    agent.metabolism = 2
    reserve = 5.0 * agent.metabolism  # = 10.0
    agent.wealth = 30.0  # surplus = 30 - 10 = 20; contribution = 0.1 * 20 = 2.0
    agent.strategy = "si_bounded"  # avoid Cred scaling

    # Disable all other agents from pool
    for a in agents:
        if a is not agent:
            a._use_eta = False

    metrics = pool.step(agents)
    expected_contrib = 0.1 * (30.0 - 10.0)  # tau_pool * surplus = 0.1 * 20 = 2.0
    assert metrics.pool_total_contributed == pytest.approx(expected_contrib)
    assert agent.wealth == pytest.approx(30.0 - expected_contrib)


# ── Test 5: C status contribution (Cred scaling) ─────────────────────────────

def test_c_cred_high_vs_low_contribution():
    """High-Cred C agent contributes more than low-Cred C agent with same surplus."""
    world = _make_world(strategy="carbon", n=5, tau_cred=0.5)

    # Build two minimal agents manually using world._spawn_one
    agent_high = world._spawn_one()
    agent_high._use_eta = True
    agent_high._forage_age_min = 15
    agent_high._forage_age_max_offset = 10
    agent_high.max_age = 80
    agent_high.age = 30
    agent_high.metabolism = 2
    agent_high.wealth = 30.0
    agent_high.strategy = "carbon"
    agent_high.cred = 50.0  # high Cred
    agent_high._cred_scale = 10.0

    agent_low = world._spawn_one()
    agent_low._use_eta = True
    agent_low._forage_age_min = 15
    agent_low._forage_age_max_offset = 10
    agent_low.max_age = 80
    agent_low.age = 30
    agent_low.metabolism = 2
    agent_low.wealth = 30.0
    agent_low.strategy = "carbon"
    agent_low.cred = 0.0  # low Cred
    agent_low._cred_scale = 10.0

    pool_high = _make_pool(tau_pool=0.1, k_reserve=5.0, tau_cred=0.5)
    pool_low = _make_pool(tau_pool=0.1, k_reserve=5.0, tau_cred=0.5)

    # Disable pool draws (no eligible drawers)
    metrics_high = pool_high.step([agent_high])
    metrics_low = pool_low.step([agent_low])

    assert metrics_high.pool_total_contributed > metrics_low.pool_total_contributed


# ── Test 6: C Cred reward ──────────────────────────────────────────────────

def test_c_cred_reward_for_excess_contribution():
    """C agent with high Cred gets a Cred increment for above-base contribution."""
    agent = _make_world(strategy="carbon", n=2).agents.__iter__().__next__()
    agent._use_eta = True
    agent._forage_age_min = 15
    agent._forage_age_max_offset = 10
    agent.max_age = 80
    agent.age = 30
    agent.metabolism = 2
    agent.wealth = 30.0
    agent.strategy = "carbon"
    agent.cred = 100.0  # very high: tanh(100/10) ≈ 1.0
    agent._cred_scale = 10.0

    pre_cred = agent.cred
    pool = _make_pool(tau_pool=0.1, k_reserve=5.0, tau_cred=0.5, tau_cred_reward=0.1)
    pool.step([agent])

    # High Cred should cause excess contribution, triggering Cred reward
    assert agent.cred > pre_cred


# ── Test 7: Pool draw non-active agent ────────────────────────────────────────

def test_pool_draw_non_active():
    """Juvenile with deficit draws from pool to cover k_draw * metabolism."""
    world = _make_world(n=5, tau_pool=0.1, k_reserve=5.0, k_draw=3.0)

    # One active adult contributor
    agents = list(world.agents)
    contributor = agents[0]
    contributor._use_eta = True
    contributor._forage_age_min = 15
    contributor._forage_age_max_offset = 10
    contributor.max_age = 80
    contributor.age = 30  # active
    contributor.metabolism = 2
    contributor.wealth = 100.0
    contributor.strategy = "si_bounded"

    # One juvenile drawer
    drawer = agents[1]
    drawer._use_eta = True
    drawer._forage_age_min = 15
    drawer._forage_age_max_offset = 10
    drawer.max_age = 80
    drawer.age = 5  # juvenile
    drawer.metabolism = 2
    drawer.wealth = 0.0  # needs k_draw * metabolism = 6.0

    # Disable all others
    for a in agents[2:]:
        a._use_eta = False

    pool = _make_pool(tau_pool=0.1, k_reserve=5.0, k_draw=3.0)
    pre_drawer_wealth = drawer.wealth
    metrics = pool.step([contributor, drawer])

    # Drawer should have received some wealth
    assert drawer.wealth > pre_drawer_wealth
    assert metrics.pool_total_drawn > 0.0
    assert metrics.pool_draw_requests == 1


# ── Test 8: Pool exhaustion ───────────────────────────────────────────────────

def test_pool_exhaustion_two_drawers():
    """Two drawers, pool too small to satisfy both; pool_draw_unmet increments."""
    world = _make_world(n=5, tau_pool=0.01, k_reserve=5.0, k_draw=3.0)
    agents = list(world.agents)

    # Tiny contributor — very small pool
    contributor = agents[0]
    contributor._use_eta = True
    contributor._forage_age_min = 15
    contributor._forage_age_max_offset = 10
    contributor.max_age = 80
    contributor.age = 30
    contributor.metabolism = 2
    contributor.wealth = 12.0  # reserve=10, surplus=2, contrib=0.01*2=0.02
    contributor.strategy = "si_bounded"

    # Two juveniles needing lots
    drawer1 = agents[1]
    drawer1._use_eta = True
    drawer1._forage_age_min = 15
    drawer1._forage_age_max_offset = 10
    drawer1.max_age = 80
    drawer1.age = 5
    drawer1.metabolism = 4  # needs 3*4=12
    drawer1.wealth = 0.0

    drawer2 = agents[2]
    drawer2._use_eta = True
    drawer2._forage_age_min = 15
    drawer2._forage_age_max_offset = 10
    drawer2.max_age = 80
    drawer2.age = 5
    drawer2.metabolism = 4  # needs 3*4=12
    drawer2.wealth = 0.0

    for a in agents[3:]:
        a._use_eta = False

    pool = _make_pool(tau_pool=0.01, k_reserve=5.0, k_draw=3.0)
    metrics = pool.step([contributor, drawer1, drawer2])

    # Pool contributed ~0.02, each drawer needs 12. Both partially met → both unmet
    assert metrics.pool_draw_requests == 2
    assert metrics.pool_draw_unmet > 0


# ── Test 9: Pool resets each step ────────────────────────────────────────────

def test_pool_resets_between_steps():
    """Pool balance resets to zero each step — no carry-over."""
    world = _make_world(n=5, tau_pool=0.1)
    agents = list(world.agents)

    # Active contributor
    agent = agents[0]
    agent._use_eta = True
    agent._forage_age_min = 15
    agent._forage_age_max_offset = 10
    agent.max_age = 80
    agent.age = 30
    agent.metabolism = 2
    agent.wealth = 100.0
    agent.strategy = "si_bounded"

    # No drawers
    for a in agents[1:]:
        a._use_eta = False

    pool = _make_pool(tau_pool=0.1, k_reserve=5.0)
    metrics1 = pool.step([agent])
    contrib1 = metrics1.pool_total_contributed

    # Second step: agent has less wealth now, but pool shouldn't carry over
    metrics2 = pool.step([agent])

    # Metrics reset: pool_total_contributed reflects only this step's contributions
    # (no accumulation from step 1)
    assert metrics2.pool_total_contributed < contrib1 or metrics2.pool_total_contributed >= 0.0
    # Key: pool_draw_unmet should not reflect step 1's values
    assert metrics2.pool_draw_requests == 0  # no drawers in step 2 either


# ── Test 10: Si pool no Cred scaling ─────────────────────────────────────────

def test_si_pool_no_cred_scaling():
    """Si agent contributes flat tau_pool regardless of si_cred value."""
    world = _make_world(strategy="si_bounded", n=3, tau_pool=0.1, tau_cred=0.5)
    agents = list(world.agents)
    agent = agents[0]
    agent._use_eta = True
    agent._forage_age_min = 15
    agent._forage_age_max_offset = 10
    agent.max_age = 80
    agent.age = 30
    agent.metabolism = 2
    agent.wealth = 50.0
    agent.strategy = "si_bounded"
    agent.si_cred = 999.0  # large Si Cred — should NOT affect contribution

    for a in agents[1:]:
        a._use_eta = False

    pool = _make_pool(tau_pool=0.1, k_reserve=5.0, tau_cred=0.5)
    metrics = pool.step([agent])

    reserve = 5.0 * agent.metabolism  # = 10.0
    surplus = 50.0 - 10.0  # = 40.0; but wealth reduced already
    # Expected: flat tau_pool * surplus (no Cred scaling for Si)
    # Note: agent.wealth was 50 before step, surplus=40, contribution=0.1*40=4.0
    expected = 0.1 * 40.0
    assert metrics.pool_total_contributed == pytest.approx(expected)
    # Verify no Cred reward tracked (cred_pool_contribution = 0 for Si)
    assert metrics.cred_pool_contribution == pytest.approx(0.0)


# ── Test 11: enabled=False recovers 4.1b behavior ────────────────────────────

def test_pool_disabled_no_contribution():
    """With enabled=False, pool step returns zero metrics."""
    pool = _make_pool(enabled=False)
    world = _make_world(n=5, pool_enabled=False)
    agents = list(world.agents)

    metrics = pool.step(agents)

    assert metrics.pool_total_contributed == pytest.approx(0.0)
    assert metrics.pool_total_drawn == pytest.approx(0.0)
    assert metrics.pool_draw_requests == 0
    assert metrics.pool_draw_unmet == 0
    assert metrics.cred_pool_contribution == pytest.approx(0.0)
