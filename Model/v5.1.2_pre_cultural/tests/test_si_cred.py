"""Stage 5.1 — Tests for Si Cred near-dormancy accumulation and σ modulation.

Removed from Stage 5 (surplus-based rule, now invalid):
  - test_si_cred_accumulates_in_world
  - test_si_cred_respects_ceiling

Kept from Stage 5 (4 tests):
  - test_temperature_increases_with_si_cred
  - test_temperature_constant_when_kappa_zero
  - test_si_cred_zero_when_disabled
  - test_si_cred_metrics_in_dataframe  (updated: column-presence + σ_eff=σ_Si when si_cred=0)

New — Stage 5.1 near-dormancy band (8 tests):
  - test_si_cred_accumulates_when_in_near_dormancy_band
  - test_si_cred_no_accumulation_below_band
  - test_si_cred_no_accumulation_above_band
  - test_si_cred_upper_band_boundary_exclusive
  - test_si_cred_decays_outside_band
  - test_si_cred_clamped_at_C_star
  - test_si_sigma_eff_increases_with_cred
  - test_si_cred_disabled_no_effect

Net: −2 removed + 8 new = +6. Target suite total: ≥ 207.
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
    c_star_si: float = 10.0,
    kappa_si: float = 0.5,
    k_cred_band: float = 1.0,
    n: int = 20,
    grid: int = 15,
    n_steps: int = 30,
    seed: int = 99,
) -> SugarWorld:
    """Factory for a minimal Si world (rich grid, high wealth) for disabled/metrics tests."""
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
            k_cred_band=k_cred_band,
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


def _make_si_world_for_band_test(
    *,
    n: int = 5,
    seed: int = 99,
    c_star_si: float = 10.0,
    kappa_si: float = 0.5,
    k_cred_band: float = 1.0,
    si_cred_enabled: bool = True,
) -> SugarWorld:
    """Factory for band-boundary tests.

    Key properties:
      - metabolism=1 (fixed), beta=1.0 → cost=1 per step
      - k_dormant=1.0, k_cred_band=1.0 → near-dormancy band [1.0, 2.0)
      - dormancy enabled: below-band agents enter dormancy rather than dying
      - initial_wealth=5 (above band); tests set wealth manually before stepping
      - max_sugar_capacity=0: no sugar, so harvest=0 and wealth is stable at set value
      - no reproduction (p_fission_max=0): population stays fixed
    """
    grid = 5
    cfg = Config(
        seed=seed,
        world=WorldConfig(
            grid_size=(grid, grid),
            sugar_peaks=[[1, 1], [3, 3]],
            max_sugar_capacity=1,
            band_width_k=4,
            growth_rate_alpha=1,
        ),
        agents=AgentsConfig(
            initial_population=n,
            vision_dist=(1, 1),
            metabolic_rate_dist=(1, 1),  # metabolism=1 always
            max_age_dist=(100, 200),      # long-lived; won't age out in short tests
            initial_wealth_dist=(5, 5),   # start above band; tests override manually
        ),
        decision=DecisionConfig(strategy="si_bounded"),
        si_bounded=SiBoundedConfig(sigma_si=1.051, beta_metabolism=1.0),
        si_cred=SiCredConfig(
            enabled=si_cred_enabled,
            k_cred_band=k_cred_band,
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
        birth_c=BirthCConfig(p_max=0.001, tau_sub=5.0, r_stress=0.75, r_wealth=0.5,
                             rep_age_min=200),   # rep_age_min > max_age: no births
        birth_si=BirthSiConfig(p_fission_max=0.001, fission_wealth_mult=1.5,
                               rep_age_min=200),  # rep_age_min > max_age: no births
        reproduction=ReproductionConfig(mode="random", parent_radius=3, inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="zero"),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=1.0, eta_old=1.0),
        support_pool=SupportPoolConfig(
            enabled=False, r_pool=5, tau_parent=0.0,
            tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
            tau_cred=0.0, tau_cred_reward=0.0,
        ),
        dormancy=DormancyConfig(
            enabled=True,
            k_dormant=1.0,
            tau_trickle=0.0,   # no sugar anyway
            k_reactivate=3.0,
            t_dormant_max=50,
        ),
        run=RunConfig(n_steps=1, metrics_every=1,
                      output_dir="outputs/test_si_cred_band"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    return SugarWorld(cfg)


# ── Kept from Stage 5: σ modulation math ─────────────────────────────────────

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

    agent_at_star = _FakeSiAgent(si_cred=c_star)
    expected = sigma + kappa * math.tanh(1.0)
    assert dec.temperature(agent_at_star) == pytest.approx(expected, rel=1e-9)


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


# ── Kept from Stage 5: disabled path and metrics pipeline ────────────────────

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


def test_si_cred_metrics_in_dataframe():
    """Metrics DataFrame must contain si_cred_mean and sigma_si_eff_mean columns.

    On a rich grid with high initial wealth, agents stay well above the near-dormancy
    band, so si_cred=0 and sigma_si_eff_mean equals sigma_si exactly.
    Verifies the full metrics pipeline produces the correct column schema.
    """
    sigma_si = 1.051
    world = _make_si_world(
        si_cred_enabled=True,
        kappa_si=0.5,
        c_star_si=10.0,
        n_steps=50,
    )
    df = world.run()

    assert "si_cred_mean" in df.columns, "DataFrame must have si_cred_mean column"
    assert "sigma_si_eff_mean" in df.columns, "DataFrame must have sigma_si_eff_mean column"

    # Wealthy agents are above the near-dormancy band: si_cred=0, sigma_eff=sigma_si.
    final_sigma_eff = df["sigma_si_eff_mean"].iloc[-1]
    assert final_sigma_eff == pytest.approx(sigma_si, rel=1e-9), (
        f"sigma_si_eff_mean should equal sigma_si={sigma_si} when si_cred=0; "
        f"got {final_sigma_eff}"
    )


def _freeze_sugar_at_zero(world: SugarWorld) -> None:
    """Prevent any sugar from appearing during a step.

    Zeros both sugar and effective_capacity so that growback produces 0
    (min(0+alpha, 0)=0) and harvest returns 0. Wealth is stable at whatever
    value the test sets, making band membership fully predictable.
    """
    world.sugar_field.sugar[:] = 0.0
    world.sugar_field.effective_capacity[:] = 0.0


# ── New: Stage 5.1 near-dormancy band tests ───────────────────────────────────
#
# All band tests use _make_si_world_for_band_test:
#   metabolism=1, beta=1.0, cost=1, k_dormant=1.0, k_cred_band=1.0
#   → near-dormancy band: [1.0, 2.0)  (wealth post-harvest, pre-metabolize)
#   Dormancy enabled; no sugar via _freeze_sugar_at_zero; wealth set manually.

def test_si_cred_accumulates_when_in_near_dormancy_band():
    """Agent with wealth in [k_dormant, k_dormant + k_cred_band) × cost receives Δsi_cred=1."""
    world = _make_si_world_for_band_test()
    # Set all agents to wealth=1.5, firmly inside band [1.0, 2.0).
    for agent in world.agents:
        agent.wealth = 1.5
    # Zero sugar guarantees harvest=0; wealth at Phase 1b equals the set value exactly.
    _freeze_sugar_at_zero(world)

    world.step()

    agents = list(world.agents)
    assert len(agents) > 0, "Agents should survive one step at wealth=1.5"
    for agent in agents:
        # si_cred_0=0, delta=1 → si_cred_1 = min(0*0.99 + 1, 10) = 1.0
        assert agent.si_cred == pytest.approx(1.0, rel=1e-9), (
            f"Expected si_cred=1.0 for in-band agent; got {agent.si_cred}"
        )


def test_si_cred_no_accumulation_below_band():
    """Agent with wealth below the band (< k_dormant × cost) receives Δsi_cred=0.

    Below-band agents enter dormancy in Phase 3; the accumulation check (Phase 1b)
    evaluates wealth before dormancy entry. Since wealth < w_lo, delta=0.
    """
    world = _make_si_world_for_band_test()
    # wealth=0.5 is below the band lower bound of 1.0.
    for agent in world.agents:
        agent.wealth = 0.5
    _freeze_sugar_at_zero(world)

    world.step()

    # Agents enter dormancy (wealth=0.5 < k_dormant*cost=1.0) but survive the step.
    agents = list(world.agents)
    assert len(agents) > 0
    for agent in agents:
        assert agent.si_cred == pytest.approx(0.0, rel=1e-9), (
            f"Expected si_cred=0.0 for below-band agent; got {agent.si_cred}"
        )


def test_si_cred_no_accumulation_above_band():
    """Agent with wealth ≥ (k_dormant + k_cred_band) × cost receives Δsi_cred=0."""
    world = _make_si_world_for_band_test()
    # wealth=10.0 is well above the band upper bound of 2.0.
    for agent in world.agents:
        agent.wealth = 10.0
    _freeze_sugar_at_zero(world)

    world.step()

    agents = list(world.agents)
    assert len(agents) > 0
    for agent in agents:
        assert agent.si_cred == pytest.approx(0.0, rel=1e-9), (
            f"Expected si_cred=0.0 for above-band agent; got {agent.si_cred}"
        )


def test_si_cred_upper_band_boundary_exclusive():
    """Agent with wealth exactly equal to (k_dormant + k_cred_band) × cost receives Δsi_cred=0.

    The upper bound of the band is a strict inequality (< w_hi_i), so the agent
    at exactly wealth=2.0 (=w_hi with k_dormant=1, k_cred_band=1, cost=1) is outside.
    """
    world = _make_si_world_for_band_test()
    # wealth=2.0 is exactly at the upper bound; strict inequality means delta=0.
    for agent in world.agents:
        agent.wealth = 2.0
    _freeze_sugar_at_zero(world)

    world.step()

    agents = list(world.agents)
    assert len(agents) > 0
    for agent in agents:
        assert agent.si_cred == pytest.approx(0.0, rel=1e-9), (
            f"Expected si_cred=0.0 at upper-band boundary (exclusive); got {agent.si_cred}"
        )


def test_si_cred_decays_outside_band():
    """Agent outside the band for N consecutive steps: si_cred decays by (1-decay)^N.

    Verified at N=10. Agents stay well above band throughout (wealth=100, cost=1/step).
    """
    world = _make_si_world_for_band_test()
    # Start with si_cred=1.0, wealth=100 (above band [1.0, 2.0)).
    for agent in world.agents:
        agent.si_cred = 1.0
        agent.wealth = 100.0
    _freeze_sugar_at_zero(world)

    n_steps = 10
    decay = 0.01
    for _ in range(n_steps):
        world.step()

    expected = 1.0 * (1.0 - decay) ** n_steps  # ≈ 0.9044

    agents = list(world.agents)
    assert len(agents) > 0
    for agent in agents:
        assert agent.si_cred == pytest.approx(expected, rel=1e-9), (
            f"Expected si_cred≈{expected:.6f} after {n_steps} steps outside band; "
            f"got {agent.si_cred:.6f}"
        )


def test_si_cred_clamped_at_C_star():
    """Agent in band with si_cred near C_star_Si: clamp prevents exceeding ceiling.

    Sets si_cred=4.5 and C_star_Si=5.0. One in-band step gives
    si_cred_new = min(4.5×0.99 + 1, 5.0) = min(5.455, 5.0) = 5.0.
    """
    c_star = 5.0
    world = _make_si_world_for_band_test(c_star_si=c_star)
    # Set si_cred close to ceiling; wealth in band [1.0, 2.0).
    for agent in world.agents:
        agent.si_cred = 4.5
        agent.wealth = 1.5
    _freeze_sugar_at_zero(world)

    world.step()

    agents = list(world.agents)
    assert len(agents) > 0
    for agent in agents:
        assert agent.si_cred == pytest.approx(c_star, rel=1e-9), (
            f"Expected si_cred clamped at C_star_Si={c_star}; got {agent.si_cred}"
        )


def test_si_sigma_eff_increases_with_cred():
    """σ_Si_eff_i > σ_Si when si_cred_i > 0; σ_Si_eff_i = σ_Si when si_cred_i = 0.

    Carry-over from Stage 5. Verifies the σ modulation formula:
    σ_Si_eff = σ_Si + κ_Si × tanh(si_cred / C*_Si).
    """
    sigma_si = 1.051
    kappa_si = 0.5
    c_star = 10.0
    dec = BoundedRationalSi(sigma_si=sigma_si, kappa_si=kappa_si, c_star_si=c_star)

    agent_zero = _FakeSiAgent(si_cred=0.0)
    agent_pos = _FakeSiAgent(si_cred=3.0)

    assert dec.temperature(agent_zero) == pytest.approx(sigma_si, rel=1e-9), (
        "σ_Si_eff should equal σ_Si when si_cred=0"
    )
    assert dec.temperature(agent_pos) > sigma_si, (
        "σ_Si_eff should exceed σ_Si when si_cred > 0"
    )
    expected = sigma_si + kappa_si * math.tanh(3.0 / c_star)
    assert dec.temperature(agent_pos) == pytest.approx(expected, rel=1e-9)


def test_si_cred_disabled_no_effect():
    """With enabled=False: si_cred stays 0 for all agents, even when wealth is in band.

    Carry-over from Stage 5. Confirms the enabled=False gate prevents any accumulation
    regardless of agent wealth position relative to the near-dormancy band.
    """
    world = _make_si_world_for_band_test(si_cred_enabled=False)
    # Agents in band — accumulation would fire if enabled; must stay zero when disabled.
    for agent in world.agents:
        agent.wealth = 1.5
    _freeze_sugar_at_zero(world)

    world.step()

    agents = list(world.agents)
    assert len(agents) > 0
    for agent in agents:
        assert agent.si_cred == pytest.approx(0.0, rel=1e-9), (
            f"si_cred should remain 0.0 with enabled=False; got {agent.si_cred}"
        )
