"""Stage 5 Task 3 — Tests for Si Cred accumulation and σ modulation.

Tests (6):
  1. BoundedRationalSi.temperature increases monotonically with si_cred when kappa>0
  2. kappa_si=0 → temperature is always sigma_si regardless of si_cred (disabled path)
  3. Si Cred accumulates in a running world when si_cred.enabled=True
  4. Si Cred remains zero when si_cred.enabled=False
  5. Si Cred never exceeds C_star_Si (ceiling respected)
  6. Metrics DataFrame contains non-zero si_cred_mean column when enabled
"""
from __future__ import annotations

import math

import pytest

from sic_games.agents.strategies.si_bounded import BoundedRationalSi
from sic_games.config import (
    AgentsConfig,
    CarbonConfig,
    Config,
    DecisionConfig,
    DormancyConfig,
    InitializationConfig,
    JointTaskConfig,
    LifeHistoryConfig,
    PerturbationConfig,
    PopulationConfig,
    ReproductionConfig,
    RunConfig,
    SiBoundedConfig,
    SiCredConfig,
    BirthCConfig,
    BirthSiConfig,
    SupportPoolConfig,
    VisualizationConfig,
    WorldConfig,
)
from sic_games.run import SugarWorld


# ── helpers ───────────────────────────────────────────────────────────────────

class _FakeSiAgent:
    """Minimal stand-in for BaseAgent — only si_cred field needed for temperature()."""
    def __init__(self, si_cred: float = 0.0) -> None:
        self.si_cred = si_cred


def _make_si_world(
    *,
    si_cred_enabled: bool,
    accumulation_rate: float = 0.5,
    c_star_si: float = 10.0,
    kappa_si: float = 0.5,
    n: int = 20,
    grid: int = 15,
    n_steps: int = 30,
    seed: int = 99,
) -> SugarWorld:
    """Factory for a minimal Si world with configurable Si Cred settings."""
    peaks = [[grid // 4, grid * 3 // 4], [grid * 3 // 4, grid // 4]]
    cfg = Config(
        seed=seed,
        world=WorldConfig(
            grid_size=(grid, grid),
            sugar_peaks=peaks,
            max_sugar_capacity=4,
            band_width_k=4,
            growth_rate_alpha=1,
        ),
        agents=AgentsConfig(
            initial_population=n,
            vision_dist=(1, 4),
            metabolic_rate_dist=(1, 2),
            max_age_dist=(60, 100),
            initial_wealth_dist=(10, 25),
        ),
        decision=DecisionConfig(strategy="si_bounded"),
        si_bounded=SiBoundedConfig(sigma_si=1.051, beta_metabolism=1.0),
        si_cred=SiCredConfig(
            enabled=si_cred_enabled,
            accumulation_rate=accumulation_rate,
            decay=0.01,
            C_star_Si=c_star_si,
            kappa_Si=kappa_si,
        ),
        carbon=CarbonConfig(
            sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
            velocity_tau=0, velocity_scale=1.0, f_C=0.0,
            status_amplification_beta=0.0,
        ),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(p_max=0.02, tau_sub=5.0, r_stress=0.75, r_wealth=0.5,
                             rep_age_min=15),
        birth_si=BirthSiConfig(p_fission_max=0.065, fission_wealth_mult=1.5,
                               rep_age_min=15),
        reproduction=ReproductionConfig(mode="random", parent_radius=3, inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="realistic"),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=1.0, eta_old=1.0),
        support_pool=SupportPoolConfig(
            enabled=False, r_pool=5, tau_parent=0.0,
            tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
            tau_cred=0.0, tau_cred_reward=0.0,
        ),
        dormancy=DormancyConfig(enabled=False),
        run=RunConfig(n_steps=n_steps, metrics_every=1,
                      output_dir="outputs/test_si_cred"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    return SugarWorld(cfg)


# ── Test 1: temperature increases monotonically with si_cred ─────────────────

def test_temperature_increases_with_si_cred():
    """σ_Si_eff = σ_Si + κ × tanh(c/C*) is strictly increasing in c when κ>0."""
    sigma, kappa, c_star = 1.051, 0.5, 10.0
    dec = BoundedRationalSi(sigma_si=sigma, kappa_si=kappa, c_star_si=c_star)

    prev_temp = -1.0
    for si_cred in [0.0, 1.0, 3.0, 7.0, 10.0, 20.0]:
        agent = _FakeSiAgent(si_cred=si_cred)
        temp = dec.temperature(agent)
        assert temp > prev_temp, (
            f"temperature should increase with si_cred; got {temp} ≤ {prev_temp} "
            f"at si_cred={si_cred}"
        )
        prev_temp = temp

    # Analytic spot-check at si_cred=C*: σ_Si + κ×tanh(1) = 1.051 + 0.5×tanh(1)
    agent_at_star = _FakeSiAgent(si_cred=c_star)
    expected = sigma + kappa * math.tanh(1.0)
    assert dec.temperature(agent_at_star) == pytest.approx(expected, rel=1e-9)


# ── Test 2: kappa=0 → constant temperature ───────────────────────────────────

def test_temperature_constant_when_kappa_zero():
    """kappa_si=0 disables Cred modulation; temperature always equals sigma_si."""
    sigma = 1.051
    dec = BoundedRationalSi(sigma_si=sigma, kappa_si=0.0, c_star_si=10.0)
    for si_cred in [0.0, 0.5, 5.0, 10.0, 100.0]:
        agent = _FakeSiAgent(si_cred=si_cred)
        assert dec.temperature(agent) == pytest.approx(sigma), (
            f"Expected constant sigma={sigma} with kappa=0, "
            f"got {dec.temperature(agent)} at si_cred={si_cred}"
        )


# ── Test 3: Si Cred accumulates in world run ──────────────────────────────────

def test_si_cred_accumulates_in_world():
    """After 30 steps with enabled Si Cred, mean si_cred across agents should be > 0.

    Sugar-rich grid (max_capacity=4) gives agents frequent surpluses.
    accumulation_rate=0.5 is large enough to produce measurable Cred in 30 steps.
    """
    world = _make_si_world(si_cred_enabled=True, accumulation_rate=0.5, n_steps=30)
    world.run()

    all_agents = list(world.agents)
    assert len(all_agents) > 0, "World population must survive 30 steps"

    mean_cred = sum(a.si_cred for a in all_agents) / len(all_agents)
    assert mean_cred > 0.0, (
        f"Expected si_cred > 0 after 30 steps with accumulation_rate=0.5; got {mean_cred:.4f}"
    )


# ── Test 4: Si Cred stays zero when disabled ─────────────────────────────────

def test_si_cred_zero_when_disabled():
    """With si_cred.enabled=False, agent.si_cred stays 0.0 throughout the run."""
    world = _make_si_world(si_cred_enabled=False, n_steps=30)
    world.run()

    all_agents = list(world.agents)
    assert len(all_agents) > 0
    for agent in all_agents:
        assert agent.si_cred == pytest.approx(0.0), (
            f"si_cred should remain 0.0 when disabled; got {agent.si_cred}"
        )


# ── Test 5: Si Cred never exceeds C_star_Si ──────────────────────────────────

def test_si_cred_respects_ceiling():
    """si_cred must never exceed C_star_Si, even with high accumulation_rate.

    Uses accumulation_rate=5.0 (very aggressive) and C_star_Si=3.0 (low ceiling)
    to stress-test the ceiling clamp.
    """
    c_star = 3.0
    world = _make_si_world(
        si_cred_enabled=True,
        accumulation_rate=5.0,
        c_star_si=c_star,
        n_steps=50,
        seed=77,
    )
    world.run()

    all_agents = list(world.agents)
    assert len(all_agents) > 0
    for agent in all_agents:
        assert agent.si_cred <= c_star + 1e-9, (
            f"si_cred={agent.si_cred:.4f} exceeds C_star_Si={c_star}"
        )


# ── Test 6: Metrics DataFrame captures si_cred_mean ──────────────────────────

def test_si_cred_metrics_in_dataframe():
    """When enabled, DataFrame must contain a non-zero si_cred_mean column.

    Verifies the full metrics pipeline: accumulation → StepMetrics → DataFrame.
    Also checks that sigma_si_eff_mean > sigma_si (Cred is boosting temperature).
    """
    sigma_si = 1.051
    world = _make_si_world(
        si_cred_enabled=True,
        accumulation_rate=0.5,
        kappa_si=0.5,
        c_star_si=10.0,
        n_steps=50,
    )
    df = world.run()

    assert "si_cred_mean" in df.columns, "DataFrame must have si_cred_mean column"
    assert "sigma_si_eff_mean" in df.columns, "DataFrame must have sigma_si_eff_mean column"

    # By step 50, si_cred_mean should have risen above zero
    final_cred_mean = df["si_cred_mean"].iloc[-1]
    assert final_cred_mean > 0.0, (
        f"si_cred_mean in DataFrame should be > 0 after 50 steps; got {final_cred_mean}"
    )

    # sigma_si_eff_mean should be >= sigma_si (Cred only adds to temperature)
    final_sigma_eff = df["sigma_si_eff_mean"].iloc[-1]
    assert final_sigma_eff >= sigma_si - 1e-9, (
        f"sigma_si_eff_mean={final_sigma_eff} should be >= sigma_si={sigma_si}"
    )
