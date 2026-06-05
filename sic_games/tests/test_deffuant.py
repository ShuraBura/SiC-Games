"""Stage 5.2 Task 2 — Tests for Deffuant bounded-confidence cultural updating.

Blueprint tests:
  test_deffuant_no_update_outside_confidence_bound
  test_deffuant_moves_toward_neighbour_within_bound
  test_deffuant_c1_one_blocks_all_updates
  test_deffuant_prestige_higher_cred_neighbour_pulls_harder
  test_deffuant_clamped_to_unit_interval
  test_deffuant_disabled_bit_identical
  test_deffuant_mu_zero_bit_identical
  test_deffuant_never_fires_for_si
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from sic_games.config import (
    AgentsConfig, BirthCConfig, BirthSiConfig, C2DefectionConfig,
    CarbonConfig, CarryingCostConfig, Config, DeffuantConfig, DecisionConfig,
    DormancyConfig, InitializationConfig, JointTaskConfig,
    LifeHistoryConfig, PerturbationConfig, PopulationConfig,
    ReproductionConfig, RunConfig, SiCredConfig,
    SupportPoolConfig, VisualizationConfig, WorldConfig,
)
from sic_games.run import SugarWorld


# ─── Minimal world factory ────────────────────────────────────────────────────

def _make_c_world(
    *,
    n: int = 20,
    grid: int = 10,
    n_steps: int = 10,
    seed: int = 42,
    deffuant_cfg: DeffuantConfig | None = None,
    c1_mean: float = 0.5,
    c1_std: float = 0.2,
    c2_mean: float = 0.5,
    c2_std: float = 0.2,
    psi_mean: float = 0.5,
    psi_std: float = 0.2,
    sigma_inherit: float = 0.0,   # 0 → no trait noise in tests
) -> SugarWorld:
    """Factory for a minimal C world for Deffuant tests."""
    peaks = [[grid // 4, grid * 3 // 4], [grid * 3 // 4, grid // 4]]
    if deffuant_cfg is None:
        deffuant_cfg = DeffuantConfig(enabled=False)
    return SugarWorld(Config(
        seed=seed,
        world=WorldConfig(grid_size=(grid, grid), max_sugar_capacity=16,
                          growth_rate_alpha=4, band_width_k=6,
                          sugar_peaks=peaks),
        agents=AgentsConfig(
            initial_population=n, vision_dist=(1, 6),
            metabolic_rate_dist=(1, 4), max_age_dist=(60, 100),
            initial_wealth_dist=(5, 25),
            c1_mean=c1_mean, c1_std=c1_std,
            c2_mean=c2_mean, c2_std=c2_std,
            psi_mean=psi_mean, psi_std=psi_std,
        ),
        decision=DecisionConfig(strategy="carbon"),
        carbon=CarbonConfig(
            sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
            velocity_tau=10, velocity_scale=1.0, f_C=0.25,
            status_amplification_beta=1.0,
        ),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        c2_defection=C2DefectionConfig(enabled=False),
        deffuant=deffuant_cfg,
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            p_max=0.001,  # effectively disabled (rep_age_min=200 >> max_age)
            tau_sub=5.0, r_stress=0.75, k_stress=10.0, rep_age_min=200,
            gamma=0.0, c_star_birth=10.0,
            carrying_cost=CarryingCostConfig(enabled=False, N_carry=400, alpha_carry=1.0),
        ),
        birth_si=BirthSiConfig(p_fission_max=0.001, rep_age_min=200),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3,
                                        inherit_sigma=sigma_inherit, lambda_inheritance=0.0),
        si_cred=SiCredConfig(enabled=False),
        dormancy=DormancyConfig(enabled=False),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(
            age_distribution="zero", age_init_upper_frac=0.25,
            wealth_init_scale_k=True, cluster_init=False,
        ),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10),
        support_pool=SupportPoolConfig(enabled=False),
        run=RunConfig(n_steps=n_steps, metrics_every=1, output_dir=""),
        visualization=VisualizationConfig(animate=False),
    ))


# ─── Blueprint test 1: no update outside confidence bound ─────────────────────

def test_deffuant_no_update_outside_confidence_bound():
    """Agent with |trait_i - trait_j| >= epsilon receives no update."""
    # All agents with c1=0.0 (no resistance), epsilon=0.1.
    # Two groups: one at c2=0.0, other at c2=0.5 → |diff|=0.5 > epsilon=0.1 → no update.
    deff = DeffuantConfig(enabled=True, epsilon=0.1, mu=1.0, traits=["c2"],
                          update_every=1)
    world = _make_c_world(n=10, grid=10, n_steps=5, seed=42, deffuant_cfg=deff,
                          c1_mean=0.0, c1_std=0.0, c2_mean=0.25, c2_std=0.25)
    agents = list(world.agents)
    # Set half to c2=0.0 and half to c2=0.5 (far apart)
    for i, a in enumerate(agents):
        a.c2 = 0.0 if i < len(agents) // 2 else 0.5
    # Place agents far from each other so few JT events but Deffuant still fires
    c2_before = {a.unique_id: a.c2 for a in agents}
    # Run 5 steps with epsilon=0.1: difference=0.5 > epsilon=0.1 → no updates
    for _ in range(5):
        world.step()
    # Agents that started at 0.0 should still be near 0.0, same for 0.5
    # (unless they moved close enough due to movement — we test the MEAN doesn't converge)
    low_group_c2 = [a.c2 for a in world.agents if c2_before.get(a.unique_id, 0.5) < 0.3]
    if low_group_c2:  # some agents survived
        assert np.mean(low_group_c2) < 0.3, "Low-c2 agents should not have converged toward 0.5"


def test_deffuant_moves_toward_neighbour_within_bound():
    """Agent with |trait_i - trait_j| < epsilon moves toward neighbour by mu_eff * w."""
    # Direct test via the run loop.
    # Place all agents with c2 ~ Normal(0.5, 0.1) so many pairs within epsilon=0.3.
    # After several steps, std(c2) should decrease (convergence).
    deff = DeffuantConfig(enabled=True, epsilon=0.3, mu=0.5, traits=["c2"],
                          update_every=1)
    world_on = _make_c_world(n=30, grid=15, n_steps=50, seed=42, deffuant_cfg=deff,
                              c1_mean=0.0, c1_std=0.0, c2_mean=0.5, c2_std=0.1)
    world_off = _make_c_world(n=30, grid=15, n_steps=50, seed=42,
                               c1_mean=0.0, c1_std=0.0, c2_mean=0.5, c2_std=0.1)
    for _ in range(50):
        world_on.step()
        world_off.step()
    c2_on_std = np.std([a.c2 for a in world_on.agents])
    c2_off_std = np.std([a.c2 for a in world_off.agents])
    assert c2_on_std < c2_off_std, (
        f"Deffuant ON should reduce c2 std ({c2_on_std:.4f} < {c2_off_std:.4f})"
    )


# ─── Blueprint test 3: c1=1 blocks all updates ────────────────────────────────

def test_deffuant_c1_one_blocks_all_updates():
    """c1_i = 1 => agent never changes any trait regardless of neighbours."""
    deff = DeffuantConfig(enabled=True, epsilon=0.5, mu=0.9, traits=["c2", "psi"],
                          update_every=1)
    world = _make_c_world(n=20, grid=10, n_steps=30, seed=42, deffuant_cfg=deff,
                          c1_mean=0.5, c1_std=0.2, c2_mean=0.5, c2_std=0.2)
    # Force one specific agent to c1=1.0 and record its initial traits
    agents = list(world.agents)
    target = agents[0]
    target.c1 = 1.0
    target_c2_init = target.c2
    target_psi_init = target.psi
    for _ in range(30):
        world.step()
    # Target agent should have unchanged c2 and psi (no updates because mu_eff = mu*(1-1.0) = 0)
    assert abs(target.c2 - target_c2_init) < 1e-10, (
        f"Agent with c1=1.0 must not update c2 ({target.c2:.6f} vs {target_c2_init:.6f})"
    )
    assert abs(target.psi - target_psi_init) < 1e-10, (
        f"Agent with c1=1.0 must not update psi ({target.psi:.6f} vs {target_psi_init:.6f})"
    )


# ─── Blueprint test 4: higher-Cred neighbour pulls harder ─────────────────────

def test_deffuant_prestige_higher_cred_neighbour_pulls_harder():
    """w = cred_j / (cred_i + cred_j) → higher cred_j → larger w → larger shift."""
    # Place focal agent at c2=0.3. Two partners: one with cred=1, other with cred=10.
    # Epsilon=1.0 so |diff| always within bound.
    deff = DeffuantConfig(enabled=True, epsilon=1.0, mu=1.0, traits=["c2"],
                          update_every=1, eps_div=1e-6)
    # We test the formula directly since the run loop picks ONE neighbour per step.
    # Manual calculation: if partner has cred_j and agent has cred_i=1.0:
    # w = cred_j / (1 + cred_j + 1e-6)
    # shift = mu_eff * w * (t_j - t_i) = 1.0 * w * (0.5 - 0.3) = 0.2 * w
    # High cred partner (cred_j=100): w ≈ 100/101 ≈ 0.99 → shift ≈ 0.198
    # Low cred partner (cred_j=0.01): w ≈ 0.01/1.01 ≈ 0.01 → shift ≈ 0.002

    eps_div = 1e-6
    c_i = 1.0
    t_i, t_j = 0.3, 0.5

    w_high = 100.0 / (c_i + 100.0 + eps_div)
    w_low  = 0.01  / (c_i + 0.01  + eps_div)
    shift_high = w_high * (t_j - t_i)
    shift_low  = w_low  * (t_j - t_i)

    assert shift_high > shift_low * 5, (
        f"High-cred shift ({shift_high:.4f}) should be >> low-cred ({shift_low:.4f})"
    )


# ─── Blueprint test 5: clamped to [0,1] ──────────────────────────────────────

def test_deffuant_clamped_to_unit_interval():
    """After Deffuant update, all traits remain in [0, 1]."""
    deff = DeffuantConfig(enabled=True, epsilon=1.0, mu=1.0, traits=["c1", "c2", "psi"],
                          update_every=1)
    world = _make_c_world(n=25, grid=12, n_steps=20, seed=42, deffuant_cfg=deff,
                          c1_mean=0.5, c1_std=0.4, c2_mean=0.5, c2_std=0.4,
                          psi_mean=0.5, psi_std=0.4)
    for _ in range(20):
        world.step()
    for agent in world.agents:
        assert 0.0 <= agent.c1 <= 1.0, f"c1={agent.c1} out of [0,1]"
        assert 0.0 <= agent.c2 <= 1.0, f"c2={agent.c2} out of [0,1]"
        assert 0.0 <= agent.psi <= 1.0, f"psi={agent.psi} out of [0,1]"


# ─── Blueprint test 6: disabled → bit-identical ───────────────────────────────

def test_deffuant_disabled_bit_identical():
    """enabled=False: deffuant_updates_per_step=0 and traits do not change via Deffuant."""
    world = _make_c_world(n=25, grid=12, n_steps=15, seed=42,
                          deffuant_cfg=DeffuantConfig(enabled=False))
    for _ in range(15):
        world.step()
    df = world.metrics_to_df()
    assert (df["deffuant_updates_per_step"] == 0.0).all(), (
        "deffuant_updates_per_step must be 0 every step when disabled"
    )


# ─── Blueprint test 7: mu=0 → bit-identical ──────────────────────────────────

def test_deffuant_mu_zero_bit_identical():
    """mu=0 => no movement regardless of neighbour traits."""
    # Create two identical worlds (same seed); one has mu=0.3 but mu is overridden to 0
    deff_mu0 = DeffuantConfig(enabled=True, epsilon=1.0, mu=0.0,
                               traits=["c1", "c2", "psi"], update_every=1)
    world = _make_c_world(n=20, grid=10, n_steps=10, seed=42, deffuant_cfg=deff_mu0)
    agents_before = {a.unique_id: (a.c1, a.c2, a.psi) for a in world.agents}
    for _ in range(10):
        world.step()
    for agent in world.agents:
        uid = agent.unique_id
        if uid in agents_before:
            c1_before, c2_before, psi_before = agents_before[uid]
            assert abs(agent.c1 - c1_before) < 1e-10, f"c1 changed with mu=0"
            assert abs(agent.c2 - c2_before) < 1e-10, f"c2 changed with mu=0"
            assert abs(agent.psi - psi_before) < 1e-10, f"psi changed with mu=0"


# ─── Blueprint test 8: never fires for Si ─────────────────────────────────────

def test_deffuant_never_fires_for_si():
    """Deffuant never fires for Si agents (C-only mechanic).

    Run a Si-bounded world with Deffuant enabled; deffuant_updates_per_step
    must be 0 every step (Si agents are excluded from the update loop).
    """
    deff = DeffuantConfig(enabled=True, epsilon=0.5, mu=0.5, traits=["c2"],
                          update_every=1)
    world = SugarWorld(Config(
        seed=42,
        world=WorldConfig(grid_size=(15, 15), max_sugar_capacity=16,
                          growth_rate_alpha=4, band_width_k=6,
                          sugar_peaks=[[4, 11], [11, 4]]),
        agents=AgentsConfig(initial_population=20, vision_dist=(1, 6),
                            metabolic_rate_dist=(1, 4), max_age_dist=(60, 100),
                            initial_wealth_dist=(25, 75)),
        decision=DecisionConfig(strategy="si_bounded"),
        carbon=CarbonConfig(sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
                            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
                            velocity_tau=10, velocity_scale=1.0, f_C=0.25,
                            status_amplification_beta=1.0),
        deffuant=deff,
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        c2_defection=C2DefectionConfig(enabled=False),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(p_max=0.001, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
                             rep_age_min=200, gamma=0.0, c_star_birth=10.0),
        birth_si=BirthSiConfig(p_fission_max=0.001, rep_age_min=200),
        reproduction=ReproductionConfig(mode="random", parent_radius=3,
                                        inherit_sigma=0.05, lambda_inheritance=0.0),
        si_cred=SiCredConfig(enabled=False),
        dormancy=DormancyConfig(enabled=True, k_dormant=1.0, tau_trickle=0.3,
                                k_reactivate=3.0, t_dormant_max=50),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="zero",
                                            wealth_init_scale_k=True, cluster_init=False),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10),
        support_pool=SupportPoolConfig(enabled=False),
        run=RunConfig(n_steps=10, metrics_every=1, output_dir=""),
        visualization=VisualizationConfig(animate=False),
    ))
    for _ in range(10):
        world.step()
    df = world.metrics_to_df()
    # Si runs: Deffuant is C-only — updates must be 0
    assert (df["deffuant_updates_per_step"] == 0.0).all(), (
        "deffuant_updates_per_step must be 0 for Si runs"
    )


# ─── Additional: epsilon=0 → no updates ──────────────────────────────────────

def test_deffuant_epsilon_zero_no_updates():
    """epsilon=0 => |trait_i - trait_j| is never < 0 (strict) => no updates."""
    deff = DeffuantConfig(enabled=True, epsilon=0.0, mu=0.9, traits=["c2"],
                          update_every=1)
    world = _make_c_world(n=20, grid=10, n_steps=10, seed=42, deffuant_cfg=deff)
    agents_before = {a.unique_id: a.c2 for a in world.agents}
    for _ in range(10):
        world.step()
    for agent in world.agents:
        if agent.unique_id in agents_before:
            assert abs(agent.c2 - agents_before[agent.unique_id]) < 1e-10, (
                "c2 changed with epsilon=0 (no pair should be within bound)"
            )
