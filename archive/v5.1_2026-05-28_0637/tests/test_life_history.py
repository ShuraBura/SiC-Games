"""Stage 4.1b — tests for η(a) ramp and initialization fix.

Tests:
1. η formula correctness at key boundary ages
2. η boundary values: η(0)=eta_min, η(forage_min)=1.0, η(tau_max)≈eta_old
3. Cell fully depleted regardless of η
4. Si offspring always start at age=0 with η=eta_min
5. Realistic initialization: mean age ≈ mean_max_age/4; no agent older than tau_max/2
6. Zero initialization regression: all agents at age=0
"""
from __future__ import annotations

import pytest

from sic_games.config import load_config
from sic_games.run import SugarWorld


# ── shared config factory ──────────────────────────────────────────────────

def _make_world(
    strategy: str = "carbon",
    age_distribution: str = "zero",
    age_init_upper_frac: float = 0.5,
    wealth_init_scale_k: bool = False,
    cluster_init: bool = False,
    cluster_peak_index: int = 0,
    cluster_radius: int = 10,
    eta_min: float = 0.2,
    eta_old: float = 0.4,
    forage_age_min: int = 15,
    forage_age_max_offset: int = 10,
    n: int = 20,
    grid: int = 10,
    grid_k: int = 1,
    seed: int = 99,
    pop_mode: str = "dynamic",
    p_max: float = 0.10,
    p_fission: float = 0.15,
):
    from sic_games.config import (
        Config, WorldConfig, AgentsConfig, DecisionConfig, CarbonConfig,
        SiBoundedConfig, JointTaskConfig, PopulationConfig, BirthCConfig,
        BirthSiConfig, ReproductionConfig, PerturbationConfig, RunConfig,
        VisualizationConfig, InitializationConfig, LifeHistoryConfig,
    )
    peaks = [[grid // 4, grid * 3 // 4], [grid * 3 // 4, grid // 4]]
    cfg = Config(
        seed=seed,
        world=WorldConfig(grid_size=(grid, grid), sugar_peaks=peaks,
                          max_sugar_capacity=4 * grid_k, growth_rate_alpha=grid_k),
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
        population=PopulationConfig(mode=pop_mode),
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
        initialization=InitializationConfig(age_distribution=age_distribution,
                                            age_init_upper_frac=age_init_upper_frac,
                                            wealth_init_scale_k=wealth_init_scale_k,
                                            cluster_init=cluster_init,
                                            cluster_peak_index=cluster_peak_index,
                                            cluster_radius=cluster_radius),
        life_history=LifeHistoryConfig(
            forage_age_min=forage_age_min,
            forage_age_max_offset=forage_age_max_offset,
            eta_min=eta_min,
            eta_old=eta_old,
        ),
        run=RunConfig(n_steps=5, metrics_every=1, output_dir="outputs/test_lh"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    return SugarWorld(cfg)


# ── Test 1: η formula correctness at boundary ages ─────────────────────────

def test_eta_formula_correctness():
    """η matches analytic piecewise formula at a=0, forage_min-1, forage_min,
    forage_max, forage_max+1, tau_max."""
    world = _make_world(eta_min=0.2, eta_old=0.4, forage_age_min=15, forage_age_max_offset=10)
    agent = next(iter(world.agents))
    agent.max_age = 80
    agent._use_eta = True
    agent._forage_age_min = 15
    agent._forage_age_max_offset = 10
    agent._eta_min = 0.2
    agent._eta_old = 0.4
    a_max = 80 - 10  # = 70

    # a=0: juvenile start
    agent.age = 0
    assert abs(agent.eta() - 0.2) < 1e-9

    # a=forage_min-1=14: still juvenile
    agent.age = 14
    expected = 0.2 + 0.8 * 14 / 15
    assert abs(agent.eta() - expected) < 1e-9

    # a=forage_min=15: active window begins
    agent.age = 15
    assert abs(agent.eta() - 1.0) < 1e-9

    # a=a_max=70: active window ends exactly
    agent.age = 70
    assert abs(agent.eta() - 1.0) < 1e-9

    # a=71: elder ramp begins
    agent.age = 71
    remaining = 80 - 70  # = 10
    expected = 1.0 - (1.0 - 0.4) * (71 - 70) / remaining
    assert abs(agent.eta() - expected) < 1e-9

    # a=tau_max=80: elder at death
    agent.age = 80
    assert abs(agent.eta() - 0.4) < 1e-9


# ── Test 2: η boundary values ──────────────────────────────────────────────

def test_eta_boundary_values():
    world = _make_world(eta_min=0.2, eta_old=0.4, forage_age_min=15, forage_age_max_offset=10)
    agent = next(iter(world.agents))
    agent.max_age = 80
    agent._use_eta = True
    agent._forage_age_min = 15
    agent._forage_age_max_offset = 10
    agent._eta_min = 0.2
    agent._eta_old = 0.4

    agent.age = 0
    assert agent.eta() == pytest.approx(0.2)

    agent.age = 15
    assert agent.eta() == pytest.approx(1.0)

    agent.age = 80
    assert agent.eta() == pytest.approx(0.4)


def test_eta_disabled_returns_one():
    """Without lh_config (legacy mode), η=1.0 always."""
    world = _make_world()
    agent = next(iter(world.agents))
    agent._use_eta = False
    for age in [0, 10, 30, 70]:
        agent.age = age
        assert agent.eta() == 1.0


# ── Test 3: cell fully depleted regardless of η ────────────────────────────

def test_cell_depleted_regardless_of_eta():
    """After harvest, cell sugar = 0 even when η < 1."""
    world = _make_world(eta_min=0.2, eta_old=0.4)
    agent = next(iter(world.agents))
    agent._use_eta = True
    agent._forage_age_min = 15
    agent._forage_age_max_offset = 10
    agent._eta_min = 0.2
    agent._eta_old = 0.4
    agent.age = 0  # juvenile: η = 0.2

    # Put sugar on the cell
    x, y = agent.pos
    world.sugar_field.sugar[x, y] = 4.0
    world.sugar_field.effective_capacity[x, y] = 4.0

    pre_sugar = world.sugar_field.level(x, y)
    assert pre_sugar > 0

    # Harvest
    raw = world.sugar_field.harvest(x, y)
    assert raw > 0
    assert world.sugar_field.level(x, y) == 0.0  # cell fully depleted


# ── Test 4: Si offspring always start at age=0 ─────────────────────────────

def test_si_fission_offspring_age_zero():
    """Fission produces offspring with age=0 and η=eta_min, regardless of parent age."""
    world = _make_world(strategy="si_bounded", eta_min=0.2, eta_old=0.4, n=5)
    parent = next(iter(world.agents))
    parent.max_age = 80  # fix max_age so elder zone is predictable
    parent.age = 75  # > 80-10=70: in elder zone
    parent._use_eta = True
    parent._forage_age_min = 15
    parent._forage_age_max_offset = 10
    parent._eta_min = 0.2
    parent._eta_old = 0.4
    assert parent.eta() < 1.0  # confirm parent is in elder zone

    offspring = world._spawn_one(
        traits=parent.traits,
        preferred_pos=parent.pos,
    )
    assert offspring.age == 0
    offspring._use_eta = True
    offspring._forage_age_min = 15
    offspring._forage_age_max_offset = 10
    offspring._eta_min = 0.2
    offspring._eta_old = 0.4
    assert offspring.eta() == pytest.approx(0.2)


# ── Test 5: realistic initialization distribution ──────────────────────────

def test_realistic_init_age_distribution():
    """Realistic init: mean age ≈ mean_max_age/4 ≈ 20; no agent older than tau_max/2."""
    world = _make_world(age_distribution="realistic", n=500, grid=30, seed=7)
    agents = list(world.agents)
    ages = [a.age for a in agents]
    max_ages = [a.max_age for a in agents]

    # No agent older than floor(tau_max/2)
    for a, m in zip(ages, max_ages):
        assert a <= m // 2, f"Agent age {a} > max_age//2 = {m//2}"

    # Mean age should be approximately mean(Uniform[0, tau_max/2]) = tau_max/4
    # mean_max_age ≈ 80 (midpoint of [60,100]), so expected mean age ≈ 20
    mean_age = sum(ages) / len(ages)
    assert 10.0 < mean_age < 35.0, f"Unexpected mean age: {mean_age:.1f}"


# ── Test 6: zero initialization regression ────────────────────────────────

def test_zero_init_all_age_zero():
    """Zero initialization (default) produces all agents at age=0."""
    world = _make_world(age_distribution="zero", n=100, grid=20)
    agents = list(world.agents)
    assert all(a.age == 0 for a in agents), "Some agents not at age=0 with zero init"


# ── Tests 7–8: Stage 4.4 patch — age_init_upper_frac ─────────────────────

def test_age_init_upper_frac():
    """age_init_upper_frac=0.25 produces no agent older than floor(tau_max * 0.25)."""
    import math
    world = _make_world(age_distribution="realistic", age_init_upper_frac=0.25,
                        n=500, grid=30, seed=42)
    agents = list(world.agents)
    for a in agents:
        upper = math.floor(a.max_age * 0.25)
        assert a.age <= upper, (
            f"Agent age {a.age} exceeds floor(tau_max={a.max_age} × 0.25) = {upper}"
        )


def test_age_init_upper_frac_default():
    """age_init_upper_frac=0.5 (default) produces no agent older than floor(tau_max * 0.5)."""
    import math
    world = _make_world(age_distribution="realistic", age_init_upper_frac=0.5,
                        n=500, grid=30, seed=42)
    agents = list(world.agents)
    for a in agents:
        upper = math.floor(a.max_age * 0.5)
        assert a.age <= upper, (
            f"Agent age {a.age} exceeds floor(tau_max={a.max_age} × 0.5) = {upper}"
        )


# ── Tests 9–10: Stage 4.4 patch amendment — wealth_init_scale_k ──────────

def test_wealth_init_scale_k_true():
    """wealth_init_scale_k=True scales initial wealth by k_grid (growth_rate_alpha)."""
    k = 4
    w_min, w_max = 5, 25
    world = _make_world(wealth_init_scale_k=True, grid_k=k,
                        n=500, grid=30, seed=42)
    agents = list(world.agents)
    for a in agents:
        assert w_min * k <= a.wealth <= w_max * k, (
            f"Agent wealth {a.wealth} outside [{w_min*k}, {w_max*k}]"
        )


def test_wealth_init_scale_k_false():
    """wealth_init_scale_k=False (default) leaves initial wealth in [5, 25]."""
    w_min, w_max = 5, 25
    world = _make_world(wealth_init_scale_k=False, grid_k=4,
                        n=500, grid=30, seed=42)
    agents = list(world.agents)
    for a in agents:
        assert w_min <= a.wealth <= w_max, (
            f"Agent wealth {a.wealth} outside [{w_min}, {w_max}]"
        )


# ── Tests 11–12: Stage 4.4 patch amendment 2 — cluster_init ─────────────

def _cheb_toroidal(x1: int, y1: int, x2: int, y2: int, W: int, H: int) -> int:
    """Toroidal Chebyshev distance."""
    dx = min(abs(x1 - x2), W - abs(x1 - x2))
    dy = min(abs(y1 - y2), H - abs(y1 - y2))
    return max(dx, dy)


def test_cluster_init_placement():
    """cluster_init=True places all t=0 agents within cluster_radius of the peak."""
    grid = 50
    radius = 10
    # _make_world computes peaks as [[grid//4, grid*3//4], ...] = [[12, 37], ...]
    peak = (grid // 4, grid * 3 // 4)   # = (12, 37) for grid=50
    world = _make_world(cluster_init=True, cluster_peak_index=0, cluster_radius=radius,
                        n=250, grid=grid, seed=42)
    agents = list(world.agents)
    for a in agents:
        dist = _cheb_toroidal(a.pos[0], a.pos[1], peak[0], peak[1], grid, grid)
        assert dist <= radius, (
            f"Agent at {a.pos} is distance {dist} from peak {peak} — "
            f"exceeds cluster_radius={radius}"
        )


def test_cluster_init_false_is_uniform():
    """cluster_init=False (default) distributes agents across full grid."""
    grid = 50
    world = _make_world(cluster_init=False, n=250, grid=grid, seed=42)
    agents = list(world.agents)
    xs = [a.pos[0] for a in agents]
    ys = [a.pos[1] for a in agents]
    # Both halves of the grid should be populated
    assert any(x < grid // 2 for x in xs) and any(x >= grid // 2 for x in xs), \
        "X coords only in one half — cluster_init=False should be uniform"
    assert any(y < grid // 2 for y in ys) and any(y >= grid // 2 for y in ys), \
        "Y coords only in one half — cluster_init=False should be uniform"
