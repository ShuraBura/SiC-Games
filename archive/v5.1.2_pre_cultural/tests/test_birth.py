"""Stage 4.5 — tests for carry_discount birth ceiling.

Tests:
1.  carry_discount at N_C=0 → 1.0
2.  carry_discount at N_C=N_carry → 0.0
3.  carry_discount at midpoint (N_C=N_carry/2) → 0.5
4.  carry_discount never goes below 0.0 (N_C > N_carry)
5.  carry_discount with alpha_carry=2.0 at midpoint → 0.0 (fully suppressed)
6.  carry_discount with alpha_carry=0.5 at N_carry → 0.5 (partial suppression)
7.  carry_discount with non-default alpha_carry=1.5 (spot check)
8.  When carrying_cost disabled: birth probability unchanged (no discount applied)
"""
from __future__ import annotations

import pytest

from sic_games.agents.reproduction import carry_discount


# ── Tests 1–7: carry_discount function ──────────────────────────────────────

def test_carry_discount_at_zero():
    """carry_discount = 1.0 when N_C = 0 (no agents → no discount)."""
    assert carry_discount(N_C=0, N_carry=400, alpha_carry=1.0) == 1.0


def test_carry_discount_at_capacity():
    """carry_discount = 0.0 when N_C = N_carry (fully suppressed)."""
    assert carry_discount(N_C=400, N_carry=400, alpha_carry=1.0) == 0.0


def test_carry_discount_midpoint():
    """carry_discount = 0.5 at N_C = N_carry/2 (alpha_carry=1.0)."""
    result = carry_discount(N_C=200, N_carry=400, alpha_carry=1.0)
    assert abs(result - 0.5) < 1e-9


def test_carry_discount_no_negative():
    """carry_discount never goes below 0.0 even when N_C > N_carry."""
    assert carry_discount(N_C=800, N_carry=400, alpha_carry=1.0) == 0.0


def test_carry_discount_alpha_two_midpoint():
    """alpha_carry=2.0 at N_C=N_carry/2 → fully suppressed (1 - 2×0.5 = 0)."""
    result = carry_discount(N_C=200, N_carry=400, alpha_carry=2.0)
    assert result == 0.0


def test_carry_discount_alpha_half_at_capacity():
    """alpha_carry=0.5 at N_C=N_carry → 0.5 (gentler ceiling)."""
    result = carry_discount(N_C=400, N_carry=400, alpha_carry=0.5)
    assert abs(result - 0.5) < 1e-9


def test_carry_discount_alpha_1p5_spot():
    """alpha_carry=1.5 at N_C=200, N_carry=400 → max(0, 1 - 1.5*0.5) = 0.25."""
    result = carry_discount(N_C=200, N_carry=400, alpha_carry=1.5)
    assert abs(result - 0.25) < 1e-9


# ── Test 8: carrying_cost disabled → birth probability unchanged ─────────────

def test_carry_discount_disabled():
    """When carrying_cost.enabled=False, birth probability is unchanged.

    We verify this by constructing a world with carrying_cost disabled and
    confirming the carry_discount_mean metric is NaN (no discount applied).
    """
    import math
    from sic_games.config import (
        Config, WorldConfig, AgentsConfig, DecisionConfig, CarbonConfig,
        SiBoundedConfig, JointTaskConfig, PopulationConfig, BirthCConfig,
        BirthSiConfig, ReproductionConfig, PerturbationConfig, RunConfig,
        VisualizationConfig, InitializationConfig, LifeHistoryConfig,
        CarryingCostConfig,
    )
    from sic_games.run import SugarWorld

    cfg = Config(
        seed=99,
        world=WorldConfig(grid_size=(20, 20), sugar_peaks=[[5, 15], [15, 5]],
                          max_sugar_capacity=16, growth_rate_alpha=4),
        agents=AgentsConfig(initial_population=50, max_age_dist=(60, 100),
                            initial_wealth_dist=(5, 25)),
        decision=DecisionConfig(strategy="carbon"),
        carbon=CarbonConfig(sigma_base=0.5, kappa=2.0, cred_scale=10.0,
                            cred_decay=0.01, matthew_alpha=2.0, epsilon=0.01,
                            cred_bonus_per_participant=1.0, velocity_tau=10,
                            velocity_scale=1.0, f_C=0.25,
                            status_amplification_beta=1.0),
        si_bounded=SiBoundedConfig(sigma_si=1.238),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            p_max=0.05, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
            r_wealth=0.5, rep_age_min=15, rep_age_max=None,
            carrying_cost=CarryingCostConfig(enabled=False),
        ),
        birth_si=BirthSiConfig(p_fission_max=0.28, fission_wealth_mult=1.5,
                               rep_age_min=15),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3,
                                        inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="zero"),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=0.3, eta_old=0.4),
        run=RunConfig(n_steps=5, metrics_every=1, output_dir="outputs/test_birth"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    world = SugarWorld(cfg)
    for _ in range(5):
        world.step()
    df = world.metrics_to_df()
    # When disabled, carry_discount_mean should be NaN for every step
    assert "carry_discount_mean" in df.columns, "carry_discount_mean missing from parquet"
    for v in df["carry_discount_mean"]:
        assert math.isnan(v), f"Expected NaN when disabled, got {v}"


# ── Tests 9–10: Stage 4.5 Task 2 — ψ Beta(2,2) birth distribution ───────────

def test_psi_beta_distribution_range():
    """Beta(2,2) ψ values drawn by _draw_trait_vector stay in [0,1].

    Runs a short simulation with psi_beta_a=2, psi_beta_b=2 and confirms
    every agent's psi attribute is within [0,1].
    """
    from sic_games.config import (
        Config, WorldConfig, AgentsConfig, DecisionConfig, CarbonConfig,
        SiBoundedConfig, JointTaskConfig, PopulationConfig, BirthCConfig,
        BirthSiConfig, ReproductionConfig, PerturbationConfig, RunConfig,
        VisualizationConfig, InitializationConfig, LifeHistoryConfig,
        CarryingCostConfig,
    )
    from sic_games.run import SugarWorld

    cfg = Config(
        seed=7,
        world=WorldConfig(grid_size=(20, 20), sugar_peaks=[[5, 15], [15, 5]],
                          max_sugar_capacity=16, growth_rate_alpha=4),
        agents=AgentsConfig(initial_population=50, max_age_dist=(60, 100),
                            initial_wealth_dist=(5, 25),
                            psi_beta_a=2.0, psi_beta_b=2.0),
        decision=DecisionConfig(strategy="carbon"),
        carbon=CarbonConfig(sigma_base=0.5, kappa=2.0, cred_scale=10.0,
                            cred_decay=0.01, matthew_alpha=2.0, epsilon=0.01,
                            cred_bonus_per_participant=1.0, velocity_tau=10,
                            velocity_scale=1.0, f_C=0.25,
                            status_amplification_beta=1.0),
        si_bounded=SiBoundedConfig(sigma_si=1.238),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            p_max=0.12, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
            r_wealth=0.5, rep_age_min=15, rep_age_max=None,
            carrying_cost=CarryingCostConfig(enabled=True, N_carry=400, alpha_carry=1.0),
        ),
        birth_si=BirthSiConfig(p_fission_max=0.28, fission_wealth_mult=1.5,
                               rep_age_min=15),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3,
                                        inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="zero"),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=0.3, eta_old=0.4),
        run=RunConfig(n_steps=3, metrics_every=1, output_dir="outputs/test_psi_beta"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    world = SugarWorld(cfg)
    # All initial agents should have psi in [0,1]
    for agent in world.agents:
        if agent.strategy == "carbon":
            assert 0.0 <= agent.psi <= 1.0, f"psi={agent.psi} out of [0,1]"


def test_psi_beta_mean_near_half():
    """Beta(2,2) produces mean ψ ≈ 0.5 across a large initial population."""
    import statistics
    from sic_games.config import (
        Config, WorldConfig, AgentsConfig, DecisionConfig, CarbonConfig,
        SiBoundedConfig, JointTaskConfig, PopulationConfig, BirthCConfig,
        BirthSiConfig, ReproductionConfig, PerturbationConfig, RunConfig,
        VisualizationConfig, InitializationConfig, LifeHistoryConfig,
        CarryingCostConfig,
    )
    from sic_games.run import SugarWorld

    cfg = Config(
        seed=13,
        world=WorldConfig(grid_size=(20, 20), sugar_peaks=[[5, 15], [15, 5]],
                          max_sugar_capacity=16, growth_rate_alpha=4),
        agents=AgentsConfig(initial_population=200, max_age_dist=(60, 100),
                            initial_wealth_dist=(5, 25),
                            psi_beta_a=2.0, psi_beta_b=2.0),
        decision=DecisionConfig(strategy="carbon"),
        carbon=CarbonConfig(sigma_base=0.5, kappa=2.0, cred_scale=10.0,
                            cred_decay=0.01, matthew_alpha=2.0, epsilon=0.01,
                            cred_bonus_per_participant=1.0, velocity_tau=10,
                            velocity_scale=1.0, f_C=0.25,
                            status_amplification_beta=1.0),
        si_bounded=SiBoundedConfig(sigma_si=1.238),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            p_max=0.12, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
            r_wealth=0.5, rep_age_min=15, rep_age_max=None,
            carrying_cost=CarryingCostConfig(enabled=True, N_carry=400, alpha_carry=1.0),
        ),
        birth_si=BirthSiConfig(p_fission_max=0.28, fission_wealth_mult=1.5,
                               rep_age_min=15),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3,
                                        inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="zero"),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=0.3, eta_old=0.4),
        run=RunConfig(n_steps=1, metrics_every=1, output_dir="outputs/test_psi_beta_mean"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    world = SugarWorld(cfg)
    psi_vals = [a.psi for a in world.agents if a.strategy == "carbon"]
    assert len(psi_vals) >= 50, f"Too few C agents: {len(psi_vals)}"
    mean_psi = statistics.mean(psi_vals)
    # Beta(2,2) mean = 0.5; with 200 agents, expect within ±0.08
    assert abs(mean_psi - 0.5) < 0.08, f"psi mean={mean_psi:.4f} too far from 0.5"
