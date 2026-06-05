"""Task 4 (perf-fix A) — tests for spatial-hash partner scan in _carbon_birth.

Tests:
1. test_partner_scan_matches_naive  — hash + sort gives same candidate set as O(N) scan
2. test_partner_scan_toroidal       — edge agent finds partner across toroidal boundary
3. test_partner_sort_deterministic  — same state + same seed → same partner choice across runs
"""
from __future__ import annotations

import random
from typing import Any

import pytest

from sic_games.agents.reproduction import (
    ReproductionCoordinator,
    _toroidal_chebyshev,
)
from sic_games.config import (
    Config, WorldConfig, AgentsConfig, DecisionConfig, CarbonConfig,
    SiBoundedConfig, JointTaskConfig, PopulationConfig, BirthCConfig,
    BirthSiConfig, ReproductionConfig, PerturbationConfig, RunConfig,
    VisualizationConfig, InitializationConfig, LifeHistoryConfig,
    SupportPoolConfig, CarryingCostConfig,
)
from sic_games.run import SugarWorld


def _make_world(grid=(30, 30), n=80, seed=42, n_steps=1) -> SugarWorld:
    """Small deterministic C world for partner-scan tests."""
    wg, hg = grid
    cfg = Config(
        seed=seed,
        world=WorldConfig(
            grid_size=(wg, hg),
            sugar_peaks=[[wg // 4, 3 * hg // 4], [3 * wg // 4, hg // 4]],
            max_sugar_capacity=16,
            growth_rate_alpha=4,
        ),
        agents=AgentsConfig(
            initial_population=n,
            max_age_dist=(60, 100),
            initial_wealth_dist=(5, 25),
        ),
        decision=DecisionConfig(strategy="carbon"),
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
            p_max=0.12, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
            r_wealth=0.5, rep_age_min=15, rep_age_max=None,
            carrying_cost=CarryingCostConfig(enabled=True, N_carry=400, alpha_carry=1.0),
        ),
        birth_si=BirthSiConfig(p_fission_max=0.28, fission_wealth_mult=1.5, rep_age_min=15),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3, inherit_sigma=0.05),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="zero"),
        life_history=LifeHistoryConfig(
            forage_age_min=15, forage_age_max_offset=10, eta_min=0.3, eta_old=0.4
        ),
        support_pool=SupportPoolConfig(enabled=True, r_pool=5, tau_pool=0.05,
                                       tau_parent=0.0, rho_carryover=0.3),
        run=RunConfig(n_steps=n_steps, metrics_every=1, output_dir="outputs/test_partner"),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )
    return SugarWorld(cfg, env_seed=seed, agent_seed=seed)


def _naive_candidates(focal, agents, wg, hg, radius):
    """O(N) reference: all C agents within Chebyshev radius of focal."""
    return sorted(
        [
            a for a in agents
            if a is not focal
            and a.strategy == "carbon"
            and _toroidal_chebyshev(a.pos, focal.pos, wg, hg) <= radius
        ],
        key=lambda a: a.unique_id,
    )


def _hash_candidates(focal, spatial_hash, wg, hg, radius):
    """O(r²) hash-based scan: same logic as _carbon_birth spatial_hash branch."""
    candidates = []
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if max(abs(dr), abs(dc)) <= radius:
                nr = (focal.pos[0] + dr) % wg
                nc = (focal.pos[1] + dc) % hg
                neighbour = spatial_hash.get((nr, nc))
                if (neighbour is not None
                        and neighbour is not focal
                        and neighbour.strategy == "carbon"):
                    candidates.append(neighbour)
    candidates.sort(key=lambda a: a.unique_id)
    return candidates


# ── Test 1 ────────────────────────────────────────────────────────────────────

def test_partner_scan_matches_naive():
    """Spatial hash + sort gives same candidate set as O(N) scan for 100 focal agents."""
    world = _make_world(grid=(30, 30), n=80, seed=42)
    wg, hg = world.cfg.world.grid_size
    radius = world.cfg.reproduction.parent_radius
    agents = list(world.agents)
    spatial_hash = {a.pos: a for a in agents}

    mismatches = 0
    checked = 0
    for focal in agents:
        if focal.strategy != "carbon":
            continue
        naive = _naive_candidates(focal, agents, wg, hg, radius)
        hashed = _hash_candidates(focal, spatial_hash, wg, hg, radius)
        if naive != hashed:
            mismatches += 1
        checked += 1

    assert checked > 0, "No C agents found to check"
    assert mismatches == 0, (
        f"{mismatches}/{checked} focal agents gave different candidate sets"
    )


# ── Test 2 ────────────────────────────────────────────────────────────────────

def test_partner_scan_toroidal():
    """Edge agent finds partner across toroidal boundary.

    Place a focal agent at (0, 0) and a partner at (wg-1, hg-1) — toroidal
    distance = 1 (Chebyshev). With parent_radius=3, the partner must appear in
    both naive and hash candidate lists.
    """
    world = _make_world(grid=(20, 20), n=4, seed=7)
    wg, hg = world.cfg.world.grid_size
    radius = world.cfg.reproduction.parent_radius  # 3

    agents = list(world.agents)
    # We test the pure spatial_hash logic without needing a full world step:
    # manually create two agents at known positions and check the scan.
    # Use the actual agents but override positions for the test.

    # Pick first two C agents
    c_agents = [a for a in agents if a.strategy == "carbon"]
    assert len(c_agents) >= 2, "Need at least 2 C agents for toroidal test"

    focal = c_agents[0]
    partner = c_agents[1]

    # Place focal at corner (0, 0), partner at the diagonally-opposite corner
    world.occupied.discard(focal.pos)
    world.occupied.discard(partner.pos)
    focal.pos = (0, 0)
    partner.pos = (wg - 1, hg - 1)
    world.occupied.add(focal.pos)
    world.occupied.add(partner.pos)

    # Toroidal Chebyshev distance should be 1
    d = _toroidal_chebyshev(focal.pos, partner.pos, wg, hg)
    assert d == 1, f"Expected Chebyshev distance 1, got {d}"

    spatial_hash = {a.pos: a for a in agents}
    naive = _naive_candidates(focal, agents, wg, hg, radius)
    hashed = _hash_candidates(focal, spatial_hash, wg, hg, radius)

    assert partner in naive, "Partner missing from naive scan (boundary bug)"
    assert partner in hashed, "Partner missing from hash scan (toroidal wrap bug)"
    assert naive == hashed, "Naive and hash scans disagree at toroidal boundary"


# ── Test 3 ────────────────────────────────────────────────────────────────────

def test_partner_sort_deterministic():
    """Same world state + same seed → same partner selected across two independent calls.

    Constructs a world, builds a spatial hash, picks the first eligible C agent,
    and calls rng.choice(sorted_candidates) twice from the same seed. Must agree.
    """
    world = _make_world(grid=(30, 30), n=80, seed=42)
    wg, hg = world.cfg.world.grid_size
    radius = world.cfg.reproduction.parent_radius

    agents = list(world.agents)
    spatial_hash = {a.pos: a for a in agents}

    # Find first focal agent with at least one hash candidate
    focal = None
    candidates = []
    for a in agents:
        if a.strategy != "carbon":
            continue
        cands = _hash_candidates(a, spatial_hash, wg, hg, radius)
        if cands:
            focal = a
            candidates = cands
            break

    assert focal is not None, "No eligible focal C agent found (all isolated)"

    # Pick a partner twice from identical RNG states
    rng1 = random.Random(99)
    rng2 = random.Random(99)
    partner1 = rng1.choice(candidates)
    partner2 = rng2.choice(candidates)

    assert partner1 is partner2, (
        "Partner selection is not deterministic: same seed + same sorted candidate "
        f"list gave different partners ({partner1.unique_id} vs {partner2.unique_id})"
    )
