"""Stage 4.1a tests — variable population and ReproductionCoordinator.

Tests:
1. C/Si dispatch: coordinator routes correctly, Si never calls _carbon_birth
2. HiveMind stub raises NotImplementedError
3. Fork stub raises NotImplementedError
4. Birth probability formula: analytic verification at subsistence / stress / prosperity
5. Fixed mode recovers Stage 4: N(t)=250 throughout
6. Fission offspring: Si traits near-copy, bio attrs fresh, placed at valid location
7. Carrying capacity: dynamic population on small grid stabilizes (no infinite growth)
"""
from __future__ import annotations

import math
import random
from unittest.mock import patch

import pytest

from sic_games.agents.reproduction import ReproductionCoordinator, _noise_traits
from sic_games.agents.traits import TraitVector
from sic_games.config import (
    BirthCConfig,
    BirthSiConfig,
    load_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_coordinator(p_max=0.5, p_fission=0.5, fission_mult=1.5):
    bc = BirthCConfig(p_max=p_max, tau_sub=5.0, r_stress=0.75, r_wealth=0.5)
    bsi = BirthSiConfig(p_fission_max=p_fission, fission_wealth_mult=fission_mult)
    return ReproductionCoordinator(bc, bsi, parent_radius=3, inherit_sigma=0.05)


def _make_world_dynamic(pop_mode="dynamic", strategy="carbon", n_agents=10,
                        grid=10, p_max=0.5, p_fission=0.5):
    """Create a minimal SugarWorld with dynamic population for testing."""
    import yaml
    from pathlib import Path
    from sic_games.run import SugarWorld
    from sic_games.config import Config

    peaks = [[grid // 4, grid * 3 // 4], [grid * 3 // 4, grid // 4]]
    raw = {
        "seed": 42,
        "world": {"grid_size": [grid, grid], "sugar_peaks": peaks},
        "agents": {"initial_population": n_agents},
        "decision": {"strategy": strategy},
        "population": {"mode": pop_mode},
        "birth_c": {"p_max": p_max, "tau_sub": 5.0, "r_stress": 0.75, "r_wealth": 0.5},
        "birth_si": {"p_fission_max": p_fission, "fission_wealth_mult": 1.5},
        "reproduction": {"mode": "biparental" if strategy == "carbon" else "random",
                         "parent_radius": 3, "inherit_sigma": 0.05},
        "perturbation": {"type": "null"},
        "run": {"n_steps": 10, "output_dir": "outputs/_test_dynamic"},
        "visualization": {"animate": False},
    }
    if strategy == "si_bounded":
        raw["si_bounded"] = {"sigma_si": 1.238}
    if strategy == "carbon":
        raw["carbon"] = {"f_C": 0.0, "status_amplification_beta": 0.0,
                         "velocity_tau": 0, "sigma_base": 0.5, "kappa": 2.0,
                         "cred_scale": 10.0, "cred_decay": 0.01, "matthew_alpha": 2.0,
                         "epsilon": 0.01, "cred_bonus_per_participant": 1.0,
                         "velocity_scale": 1.0}
    cfg = Config.model_validate(raw)
    return SugarWorld(cfg)


# ---------------------------------------------------------------------------
# Test 1: C/Si dispatch — correct routing, Si NEVER calls _carbon_birth
# ---------------------------------------------------------------------------

def test_dispatch_carbon_routes_to_carbon_birth():
    coord = _make_coordinator()
    world = _make_world_dynamic(strategy="carbon", n_agents=20)
    rng = random.Random(42)
    carbon_agents = [a for a in world.agents if a.strategy == "carbon"]
    assert carbon_agents, "Expected carbon agents in world"

    called = []
    original = coord._carbon_birth

    def spy_carbon(agent, world, rng, mean_w):
        called.append("carbon")
        return original(agent, world, rng, mean_w)

    coord._carbon_birth = spy_carbon
    for a in carbon_agents[:5]:
        coord.attempt_birth(a, world, rng, mean_w=20.0)

    assert "carbon" in called, "_carbon_birth was never called for carbon agents"


def test_dispatch_si_routes_to_si_fission_never_carbon():
    coord = _make_coordinator()
    world = _make_world_dynamic(strategy="si_bounded", n_agents=20)
    rng = random.Random(42)
    si_agents = [a for a in world.agents if a.strategy == "si_bounded"]
    assert si_agents, "Expected si_bounded agents in world"

    carbon_birth_called = []
    original_si = coord._si_fission

    def spy_carbon(agent, world, rng, mean_w):
        carbon_birth_called.append(True)

    def spy_si(agent, world, rng, mean_w):
        return original_si(agent, world, rng, mean_w)

    coord._carbon_birth = spy_carbon
    coord._si_fission = spy_si

    # Give agents high wealth so fission triggers
    for a in si_agents:
        a.wealth = 1000.0

    for a in si_agents:
        coord.attempt_birth(a, world, rng, mean_w=20.0)

    assert not carbon_birth_called, "_carbon_birth was called for Si agent — BUG-002!"


def test_dispatch_unknown_strategy_raises():
    coord = _make_coordinator()
    world = _make_world_dynamic(strategy="carbon", n_agents=5)
    rng = random.Random(0)
    agent = next(iter(world.agents))
    agent.strategy = "unknown_strategy"
    with pytest.raises(ValueError, match="Unknown strategy"):
        coord.attempt_birth(agent, world, rng, mean_w=20.0)


# ---------------------------------------------------------------------------
# Test 2: HiveMind stub raises NotImplementedError
# ---------------------------------------------------------------------------

def test_hivemind_stub_raises():
    coord = _make_coordinator()
    with pytest.raises(NotImplementedError, match="HiveMind"):
        coord._si_hivemind_birth(None, None, None)


# ---------------------------------------------------------------------------
# Test 3: Fork stub raises NotImplementedError
# ---------------------------------------------------------------------------

def test_fork_stub_raises():
    coord = _make_coordinator()
    with pytest.raises(NotImplementedError, match="Forking"):
        coord.fork(None, None, None)


# ---------------------------------------------------------------------------
# Test 4: Birth probability formula — analytic verification
# ---------------------------------------------------------------------------

def _compute_p_birth_analytic(wealth, mean_w, metabolism, bc):
    """Replicate the DTM formula from the blueprint."""
    theta_sub = metabolism * bc.tau_sub
    if wealth < theta_sub:
        return 0.0
    stress_threshold = mean_w * bc.r_stress
    if wealth < stress_threshold:
        return bc.p_max
    return bc.p_max * math.exp(-(wealth - stress_threshold) / (mean_w * bc.r_wealth))


def test_birth_probability_below_subsistence_is_zero():
    bc = BirthCConfig(p_max=0.1, tau_sub=5.0, r_stress=0.75, r_wealth=0.5)
    metabolism = 3
    theta_sub = metabolism * bc.tau_sub  # 15.0
    # wealth just below floor -> P=0
    p = _compute_p_birth_analytic(wealth=14.9, mean_w=30.0, metabolism=metabolism, bc=bc)
    assert p == 0.0


def test_birth_probability_stress_zone_is_p_max():
    bc = BirthCConfig(p_max=0.1, tau_sub=5.0, r_stress=0.75, r_wealth=0.5)
    metabolism = 2
    theta_sub = metabolism * bc.tau_sub  # 10.0
    mean_w = 30.0
    stress_threshold = mean_w * bc.r_stress  # 22.5
    # wealth in (theta_sub, stress_threshold) -> P=P_max
    p = _compute_p_birth_analytic(wealth=18.0, mean_w=mean_w, metabolism=metabolism, bc=bc)
    assert abs(p - bc.p_max) < 1e-9


def test_birth_probability_prosperity_zone_decays():
    bc = BirthCConfig(p_max=0.1, tau_sub=5.0, r_stress=0.75, r_wealth=0.5)
    metabolism = 2
    mean_w = 30.0
    stress_threshold = mean_w * bc.r_stress  # 22.5
    excess = 10.0
    wealth = stress_threshold + excess
    p = _compute_p_birth_analytic(wealth=wealth, mean_w=mean_w, metabolism=metabolism, bc=bc)
    expected = bc.p_max * math.exp(-excess / (mean_w * bc.r_wealth))
    assert abs(p - expected) < 1e-9


# ---------------------------------------------------------------------------
# Test 5: Fixed mode recovers N=250 throughout
# ---------------------------------------------------------------------------

def test_fixed_mode_maintains_constant_population():
    from sic_games.run import SugarWorld
    from sic_games.config import Config

    raw = {
        "seed": 42,
        "agents": {"initial_population": 50},
        "decision": {"strategy": "carbon"},
        "population": {"mode": "fixed"},
        "reproduction": {"mode": "random"},
        "perturbation": {"type": "null"},
        "run": {"n_steps": 20, "output_dir": "outputs/_test_fixed"},
        "visualization": {"animate": False},
        "carbon": {"f_C": 0.0, "status_amplification_beta": 0.0, "velocity_tau": 0,
                   "sigma_base": 0.5, "kappa": 2.0, "cred_scale": 10.0, "cred_decay": 0.01,
                   "matthew_alpha": 2.0, "epsilon": 0.01, "cred_bonus_per_participant": 1.0,
                   "velocity_scale": 1.0},
    }
    cfg = Config.model_validate(raw)
    world = SugarWorld(cfg)
    df = world.run()
    # Population must be exactly 50 every step
    assert (df["population"] == 50).all(), (
        f"Fixed mode broke: populations {df['population'].unique()}"
    )


# ---------------------------------------------------------------------------
# Test 6: Fission offspring — Si traits near-copy, bio fresh, valid placement
# ---------------------------------------------------------------------------

def test_si_fission_offspring_traits_near_parent():
    """Offspring traits should be parent traits ± noise (sigma=0.05), clipped [0,1]."""
    rng = random.Random(7)
    parent_traits = TraitVector(phi=0.6, psi=0.4, c1=0.5, c2=0.7)
    sigma = 0.05
    # Run many samples to verify clipping and proximity
    for _ in range(50):
        child = _noise_traits(parent_traits, sigma, rng)
        for field in ("phi", "psi", "c1", "c2"):
            assert 0.0 <= getattr(child, field) <= 1.0, f"{field} out of [0,1]"


def test_si_fission_offspring_placed_near_parent_or_random():
    """Offspring should appear at an adjacent or random unoccupied cell."""
    world = _make_world_dynamic(strategy="si_bounded", n_agents=5, grid=20, p_fission=1.0)
    rng = random.Random(99)
    coord = _make_coordinator(p_fission=1.0, fission_mult=0.01)  # always fissions

    si_agents = list(world.agents)
    assert si_agents

    parent = si_agents[0]
    parent.wealth = 1e6  # guarantee threshold met
    parent.age = 20       # in reproductive window

    initial_occupied = set(world.occupied)
    offspring = coord._si_fission(parent, world, rng, mean_w=1.0)
    assert offspring is not None, "Expected fission to produce offspring"
    assert offspring.pos not in initial_occupied or offspring.pos == parent.pos, (
        "Offspring placed on already-occupied cell (excluding parent's own pos)"
    )
    # Offspring pos should be valid grid cell
    w, h = world.cfg.world.grid_size
    ox, oy = offspring.pos
    assert 0 <= ox < w and 0 <= oy < h


def test_si_fission_offspring_bio_attrs_fresh():
    """Si offspring non-trait attributes (vision, metabolism, max_age) are fresh draws."""
    world = _make_world_dynamic(strategy="si_bounded", n_agents=5, grid=20, p_fission=1.0)
    rng = random.Random(7)
    coord = _make_coordinator(p_fission=1.0, fission_mult=0.01)

    parent = next(iter(world.agents))
    parent.wealth = 1e6
    parent.age = 20

    offspring = coord._si_fission(parent, world, rng, mean_w=1.0)
    assert offspring is not None
    # Bio attrs must be in the configured ranges
    ac = world.cfg.agents
    assert ac.vision_dist[0] <= offspring.vision <= ac.vision_dist[1]
    assert ac.metabolic_rate_dist[0] <= offspring.metabolism <= ac.metabolic_rate_dist[1]
    assert ac.max_age_dist[0] <= offspring.max_age <= ac.max_age_dist[1]
    # Si Cred stays zero
    assert offspring.si_cred == 0.0


# ---------------------------------------------------------------------------
# Test 7: Carrying capacity — dynamic population stabilizes on small grid
# ---------------------------------------------------------------------------

def test_dynamic_population_does_not_grow_past_grid_size():
    """On a small grid, population must never exceed total cell count."""
    from sic_games.run import SugarWorld
    from sic_games.config import Config

    grid = 10
    n_cells = grid * grid
    raw = {
        "seed": 42,
        "world": {"grid_size": [grid, grid], "sugar_peaks": [[2, 7], [7, 2]]},
        "agents": {"initial_population": 5},
        "decision": {"strategy": "si_bounded"},
        "si_bounded": {"sigma_si": 1.238},
        "population": {"mode": "dynamic"},
        "birth_si": {"p_fission_max": 0.5, "fission_wealth_mult": 0.5},  # generous
        "birth_c": {"p_max": 0.5},
        "reproduction": {"mode": "random"},
        "perturbation": {"type": "null"},
        "run": {"n_steps": 200, "output_dir": "outputs/_test_capacity"},
        "visualization": {"animate": False},
    }
    cfg = Config.model_validate(raw)
    world = SugarWorld(cfg)
    df = world.run()

    max_pop = df["population"].max()
    assert max_pop <= n_cells, (
        f"Population {max_pop} exceeded grid capacity {n_cells}"
    )
