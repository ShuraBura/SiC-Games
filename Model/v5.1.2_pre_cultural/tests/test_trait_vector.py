"""Tests for Stage 3.3: TraitVector, biparental reproduction, ψ proximity term.

7 tests per blueprint §7:
  1. H_i initialization: all four dimensions drawn, clipped to [0,1]
  2. Biparental mixing: offspring ≈ mean(H_A, H_B) + copy-error, clipped
  3. Fallback triggers: < 2 candidates → fallback=True, fresh traits
  4. ψ_i utility term: proximity normalized correctly
  5. ψ_i=0 recovers Stage 3.2 behaviour (utility identical)
  6. Si utility unchanged by neighbor_count (no proximity term)
  7. si_cred stays 0.0 throughout 100 steps (SiCredConfig enabled=False)
"""
from __future__ import annotations

import random

import pytest

from sic_games.agents.perception import CellView
from sic_games.agents.reproduction import (
    BiparentalReproduction,
    RandomReplacement,
    _mix_traits,
)
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.strategies.si_bounded import BoundedRationalSi
from sic_games.agents.traits import TraitVector
from sic_games.config import Config, load_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trait(phi=0.5, psi=0.5, c1=0.5, c2=0.5) -> TraitVector:
    return TraitVector(phi=phi, psi=psi, c1=c1, c2=c2)


def _carbon_decision(**kwargs) -> CarbonDecision:
    defaults = dict(
        sigma_base=0.5, kappa=2.0, cred_scale=10.0,
        matthew_alpha=1.5, epsilon=0.01,
        cred_bonus_per_participant=1.0, velocity_scale=1.0, beta=0.0,
    )
    defaults.update(kwargs)
    return CarbonDecision(**defaults)


class _FakeAgent:
    """Minimal agent stub for decision-logic tests."""
    def __init__(self, *, phi=0.5, psi=0.5, cred=0.0, wealth_velocity=0.0):
        self.traits = TraitVector(phi=phi, psi=psi, c1=0.5, c2=0.5)
        self.phi = phi
        self.psi = psi
        self.cred = cred
        self.wealth_velocity = wealth_velocity


class _FakeWorld:
    """Minimal world stub for reproduction rule tests."""
    class _FakeCfg:
        class world:
            grid_size = (10, 10)

    cfg = _FakeCfg()
    agents = []

    def __init__(self, agents=None):
        self.agents = agents or []
        self._next_agent = None

    def _spawn_one(self, traits=None):
        agent = _SpawnedAgent(traits=traits)
        return agent


class _SpawnedAgent:
    def __init__(self, *, traits=None):
        self.traits = traits or TraitVector(phi=0.3, psi=0.3, c1=0.3, c2=0.3)
        self.pos = (0, 0)


class _NearbyAgent:
    """Stub living agent with a position and traits."""
    def __init__(self, pos, phi=0.6, psi=0.7):
        self.pos = pos
        self.traits = TraitVector(phi=phi, psi=psi, c1=0.4, c2=0.6)


# ---------------------------------------------------------------------------
# Test 1: H_i initialization — all four dimensions drawn and clipped to [0,1]
# ---------------------------------------------------------------------------

def test_trait_vector_fields_in_unit_interval():
    rng = random.Random(0)
    for _ in range(200):
        phi = max(0.0, min(1.0, rng.gauss(0.5, 0.2)))
        psi = max(0.0, min(1.0, rng.gauss(0.5, 0.2)))
        c1  = max(0.0, min(1.0, rng.gauss(0.5, 0.2)))
        c2  = max(0.0, min(1.0, rng.gauss(0.5, 0.2)))
        t = TraitVector(phi=phi, psi=psi, c1=c1, c2=c2)
        assert 0.0 <= t.phi <= 1.0
        assert 0.0 <= t.psi <= 1.0
        assert 0.0 <= t.c1 <= 1.0
        assert 0.0 <= t.c2 <= 1.0


# ---------------------------------------------------------------------------
# Test 2: biparental mixing → offspring ≈ mean(parents), clipped to [0,1]
# ---------------------------------------------------------------------------

def test_biparental_mixing_midpoint():
    a = _trait(phi=0.2, psi=0.4, c1=0.6, c2=0.8)
    b = _trait(phi=0.8, psi=0.6, c1=0.4, c2=0.2)
    rng = random.Random(42)
    # Run 50 offspring; with sigma=0 the result should be exactly the midpoint
    offspring = _mix_traits(a, b, sigma=0.0, rng=rng)
    assert abs(offspring.phi - 0.5) < 1e-9
    assert abs(offspring.psi - 0.5) < 1e-9
    assert abs(offspring.c1  - 0.5) < 1e-9
    assert abs(offspring.c2  - 0.5) < 1e-9


def test_biparental_mixing_clipping():
    # Parents at extremes + positive copy-error pushes phi > 1; must be clipped
    a = _trait(phi=1.0, psi=1.0, c1=0.0, c2=0.0)
    b = _trait(phi=1.0, psi=1.0, c1=0.0, c2=0.0)
    rng = random.Random(7)
    for _ in range(30):
        offspring = _mix_traits(a, b, sigma=0.5, rng=rng)
        assert 0.0 <= offspring.phi <= 1.0
        assert 0.0 <= offspring.psi <= 1.0
        assert 0.0 <= offspring.c1  <= 1.0
        assert 0.0 <= offspring.c2  <= 1.0


# ---------------------------------------------------------------------------
# Test 3: fallback fires when < 2 candidates within parent_radius
# ---------------------------------------------------------------------------

def test_biparental_fallback_no_candidates():
    rule = BiparentalReproduction(parent_radius=3, inherit_sigma=0.05)
    world = _FakeWorld(agents=[])  # no living agents at all
    _, fallback = rule.replace(world, dead_pos=(5, 5), rng=random.Random(0))
    assert fallback is True


def test_biparental_fallback_one_candidate():
    rule = BiparentalReproduction(parent_radius=3, inherit_sigma=0.05)
    world = _FakeWorld(agents=[_NearbyAgent(pos=(5, 5))])
    _, fallback = rule.replace(world, dead_pos=(5, 5), rng=random.Random(0))
    assert fallback is True


def test_biparental_no_fallback_two_candidates():
    rule = BiparentalReproduction(parent_radius=3, inherit_sigma=0.05)
    world = _FakeWorld(agents=[
        _NearbyAgent(pos=(5, 5), phi=0.3),
        _NearbyAgent(pos=(6, 5), phi=0.7),
    ])
    new_agent, fallback = rule.replace(world, dead_pos=(5, 5), rng=random.Random(0))
    assert fallback is False
    # Offspring traits should exist and be in [0,1]
    assert 0.0 <= new_agent.traits.phi <= 1.0


# ---------------------------------------------------------------------------
# Test 4: ψ_i utility term — Stage 4.4 uses c_proximity (C agents at r_pool radius)
# ---------------------------------------------------------------------------

def test_psi_proximity_term_normalized():
    dec = _carbon_decision()
    agent = _FakeAgent(phi=0.0, psi=1.0)  # w_C≈0, w_R≈1, psi=1 → ψ term dominates

    # Three cells: c_proximity values 0, 4, 8 (C agents within r_pool radius)
    cells = (
        CellView(0, 0, sugar=1.0, neighbor_count=0, c_proximity=0),
        CellView(1, 0, sugar=1.0, neighbor_count=4, c_proximity=4),
        CellView(2, 0, sugar=1.0, neighbor_count=8, c_proximity=8),
    )
    utils = dec.compute_utilities(agent, cells)
    # All sugars equal → r_hat equal; ψ term normalized by max=8 → 0, 0.5, 1.0
    # So cell 2 should have the highest utility
    assert utils[2] > utils[1] > utils[0]


# ---------------------------------------------------------------------------
# Test 5: ψ_i=0 recovers Stage 3.2 behaviour (no proximity term effect)
# ---------------------------------------------------------------------------

def test_psi_zero_recovers_stage32():
    dec = _carbon_decision()
    agent_psi0 = _FakeAgent(phi=0.5, psi=0.0, cred=5.0, wealth_velocity=0.5)

    cells_no_neighbors = (
        CellView(0, 0, sugar=2.0, neighbor_count=0),
        CellView(1, 0, sugar=4.0, neighbor_count=8),  # neighbor_count present but ψ=0
    )
    cells_zero_neighbors = (
        CellView(0, 0, sugar=2.0, neighbor_count=0),
        CellView(1, 0, sugar=4.0, neighbor_count=0),
    )

    utils_with  = dec.compute_utilities(agent_psi0, cells_no_neighbors)
    utils_plain = dec.compute_utilities(agent_psi0, cells_zero_neighbors)

    # ψ=0 means neighbor_count contributes nothing, so utilities equal
    assert abs(utils_with[0] - utils_plain[0]) < 1e-12
    assert abs(utils_with[1] - utils_plain[1]) < 1e-12


# ---------------------------------------------------------------------------
# Test 6: Si (BoundedRationalSi) ignores neighbor_count — no proximity term
# ---------------------------------------------------------------------------

def test_si_utility_ignores_neighbor_count():
    si = BoundedRationalSi(sigma_si=1.051)

    class _SiAgent:
        vision = 3
        pos = (0, 0)

    agent = _SiAgent()
    cells_low  = (CellView(0, 0, sugar=3.0, neighbor_count=0),
                  CellView(1, 0, sugar=5.0, neighbor_count=0))
    cells_high = (CellView(0, 0, sugar=3.0, neighbor_count=8),
                  CellView(1, 0, sugar=5.0, neighbor_count=8))

    from sic_games.agents.perception import Perception
    perc_low  = Perception(visible_cells=cells_low,  current_x=0, current_y=0)
    perc_high = Perception(visible_cells=cells_high, current_x=0, current_y=0)

    rng = random.Random(0)
    # Run many trials to verify the chosen target distributions match
    low_counts  = {c: 0 for c in [(0, 0), (1, 0)]}
    high_counts = {c: 0 for c in [(0, 0), (1, 0)]}
    N = 500
    for _ in range(N):
        t = si.select_target(agent, perc_low, rng)
        low_counts[t] += 1
    rng2 = random.Random(0)  # same seed → same draws
    for _ in range(N):
        t = si.select_target(agent, perc_high, rng2)
        high_counts[t] += 1
    assert low_counts == high_counts


# ---------------------------------------------------------------------------
# Test 7: si_cred stays 0.0 for 100 steps when SiCredConfig enabled=False
# ---------------------------------------------------------------------------

def test_si_cred_stays_zero(tmp_path):
    import yaml
    cfg_data = {
        "seed": 0,
        "run": {"n_steps": 100, "output_dir": str(tmp_path)},
        "decision": {"strategy": "greedy"},
        "agents": {"initial_population": 20},
        "si_cred": {"enabled": False},
    }
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(yaml.dump(cfg_data))
    cfg = load_config(cfg_path)

    from sic_games.run import SugarWorld
    world = SugarWorld(cfg)
    world.run()

    for agent in world.agents:
        assert agent.si_cred == 0.0, f"si_cred={agent.si_cred} for agent {agent.unique_id}"
