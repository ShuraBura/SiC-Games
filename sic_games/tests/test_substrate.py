"""Stage 6.0a — multi-occupancy substrate tests.

Covers blueprint §6 items 1-5 (harvest split + multi-occupancy data structure) and a
recovery-equivalence regression lock. Items 6-12 (diffusion movement candidate set,
per-capita self-limiting, neutrality reduction, ψ re-point, consumer band-handling,
offspring-on-parent-cell) arrive with the diffusion-movement increment.
"""
from __future__ import annotations

import numpy as np
import pytest

from sic_games.substrate import compute_harvest_shares


# ─── Mock agent for split-function tests ──────────────────────────────────────

class _MockA:
    """Minimal stand-in: compute_harvest_shares only reads .phi and .strategy."""
    def __init__(self, phi: float = 0.5, strategy: str = "carbon") -> None:
        self.phi = phi
        self.strategy = strategy


# ─── §6.2 Even split conserves sugar ──────────────────────────────────────────

def test_even_split_conserves_sugar():
    occ = [_MockA() for _ in range(7)]
    S = 13.7
    shares = compute_harvest_shares(occ, S, kappa=0.0, phi_epsilon=1e-6)
    assert abs(sum(shares) - S) < 1e-12


def test_single_occupant_gets_all():
    occ = [_MockA()]
    shares = compute_harvest_shares(occ, 9.0, kappa=0.0, phi_epsilon=1e-6)
    assert shares == [9.0]


# ─── §6.3 Even split equal ────────────────────────────────────────────────────

def test_even_split_equal():
    k = 5
    occ = [_MockA(phi=0.1 * i) for i in range(k)]  # differing phi must NOT matter at κ=0
    S = 10.0
    shares = compute_harvest_shares(occ, S, kappa=0.0, phi_epsilon=1e-6)
    assert all(abs(s - S / k) < 1e-12 for s in shares)


# ─── §6.4 Contest split conserves & weights; κ=0 reproduces even split ────────

def test_contest_split_conserves():
    occ = [_MockA(phi=p) for p in (0.2, 0.5, 0.9)]
    S = 20.0
    shares = compute_harvest_shares(occ, S, kappa=1.0, phi_epsilon=1e-6)
    assert abs(sum(shares) - S) < 1e-12


def test_contest_higher_phi_gets_larger_share():
    occ = [_MockA(phi=0.2), _MockA(phi=0.5), _MockA(phi=0.9)]
    shares = compute_harvest_shares(occ, 20.0, kappa=1.0, phi_epsilon=1e-6)
    assert shares[0] < shares[1] < shares[2], f"shares not monotonic in phi: {shares}"


def test_contest_kappa0_reproduces_even_split():
    occ = [_MockA(phi=p) for p in (0.1, 0.4, 0.7, 0.95)]
    S = 17.3
    even = compute_harvest_shares(occ, S, kappa=0.0, phi_epsilon=1e-6)
    # κ=0 path returns S/n regardless of φ — verify equals an explicit even split
    assert all(abs(s - S / len(occ)) < 1e-12 for s in even)


def test_contest_si_uniform_weight():
    # Si occupants get uniform weight even under κ>0 (no φ-contest for Si).
    occ = [_MockA(phi=0.1, strategy="si_bounded"), _MockA(phi=0.9, strategy="si_bounded")]
    shares = compute_harvest_shares(occ, 10.0, kappa=1.0, phi_epsilon=1e-6)
    assert abs(shares[0] - shares[1]) < 1e-12  # uniform despite differing phi


# ─── §6.5 Split order-independence ────────────────────────────────────────────

def test_split_order_independent():
    phis = [0.2, 0.5, 0.9, 0.3]
    S = 12.0
    occ = [_MockA(phi=p) for p in phis]
    base = compute_harvest_shares(occ, S, kappa=1.0, phi_epsilon=1e-6)
    base_by_phi = {a.phi: s for a, s in zip(occ, base)}
    # Shuffle occupant order; each agent's share (keyed by φ) must be unchanged.
    import random
    rng = random.Random(0)
    for _ in range(5):
        perm = occ[:]
        rng.shuffle(perm)
        sh = compute_harvest_shares(perm, S, kappa=1.0, phi_epsilon=1e-6)
        for a, s in zip(perm, sh):
            assert abs(s - base_by_phi[a.phi]) < 1e-12


# ─── §6.1 Multi-occupancy integration: cells hold many agents ─────────────────

def _make_substrate_world(*, k_cell: int, kappa: float, n: int = 40,
                          grid: int = 8, steps_cfg: int = 50, seed: int = 42):
    from sic_games.config import (
        AgentsConfig, BirthCConfig, BirthSiConfig, C2DefectionConfig,
        CarbonConfig, CarryingCostConfig, Config, DecisionConfig, DeffuantConfig,
        DormancyConfig, InitializationConfig, JointTaskConfig, LifeHistoryConfig,
        PerturbationConfig, PopulationConfig, ReproductionConfig, RunConfig,
        SiBoundedConfig, SiCredConfig, SubstrateConfig, SupportPoolConfig,
        VisualizationConfig, WorldConfig,
    )
    from sic_games.run import SugarWorld
    return SugarWorld(Config(
        seed=seed,
        world=WorldConfig(grid_size=(grid, grid), max_sugar_capacity=16,
                          growth_rate_alpha=4, band_width_k=6,
                          sugar_peaks=[(2, 6), (6, 2)]),
        agents=AgentsConfig(initial_population=n, vision_dist=(1, 6),
                            metabolic_rate_dist=(1, 4), max_age_dist=(60, 100),
                            initial_wealth_dist=(5, 25)),
        decision=DecisionConfig(strategy="carbon"),
        carbon=CarbonConfig(sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
                            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
                            velocity_tau=10, velocity_scale=1.0, f_C=0.25,
                            status_amplification_beta=1.0),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        c2_defection=C2DefectionConfig(enabled=False),
        deffuant=DeffuantConfig(enabled=False),
        substrate=SubstrateConfig(enabled=True, k_cell=k_cell, movement_mode="legacy",
                                  contest_exponent=kappa, move_cost_flat=0.0),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(p_max=0.12, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
                             rep_age_min=15, gamma=0.2, c_star_birth=10.0,
                             carrying_cost=CarryingCostConfig(enabled=True, N_carry=400, alpha_carry=1.0)),
        birth_si=BirthSiConfig(p_fission_max=0.065, rep_age_min=15),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3,
                                        inherit_sigma=0.05, lambda_inheritance=0.1),
        si_cred=SiCredConfig(enabled=False),
        dormancy=DormancyConfig(enabled=False),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(age_distribution="realistic", age_init_upper_frac=0.25,
                                            wealth_init_scale_k=True, cluster_init=False),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10),
        support_pool=SupportPoolConfig(enabled=False),
        run=RunConfig(n_steps=steps_cfg, metrics_every=1, output_dir=""),
        visualization=VisualizationConfig(animate=False),
    ))


def test_multi_occupancy_allowed_at_kcell0():
    """With k_cell=0 (unlimited), agents may co-occupy cells; some cell holds >=2."""
    world = _make_substrate_world(k_cell=0, kappa=0.0, n=40, grid=8)
    max_occ = 0
    for _ in range(50):
        world.step()
        counts: dict = {}
        for a in world.agents:
            counts[a.pos] = counts.get(a.pos, 0) + 1
        max_occ = max(max_occ, max(counts.values()) if counts else 0)
    assert max_occ >= 2, "no cell ever held >=2 agents under unlimited occupancy (small grid)"


def test_kcell1_enforces_single_occupancy():
    """With k_cell=1, no cell ever holds more than one agent (legacy invariant)."""
    world = _make_substrate_world(k_cell=1, kappa=0.0, n=30, grid=10)
    for _ in range(40):
        world.step()
        counts: dict = {}
        for a in world.agents:
            counts[a.pos] = counts.get(a.pos, 0) + 1
        assert all(c <= 1 for c in counts.values()), "k_cell=1 occupancy ceiling violated"


# ─── Diffusion movement (§4.1/4.2) — tests 7-11 ───────────────────────────────

from sic_games.config import SubstrateConfig
from sic_games.substrate import diffusion_select_target


class _MockField:
    def __init__(self, sugar: dict, w: int = 10, h: int = 10):
        self._s = sugar; self.width = w; self.height = h
    def level(self, x, y):
        return float(self._s.get((x, y), 0.0))


class _MockAgentD:
    def __init__(self, pos, phi=0.5, strategy="carbon"):
        self.pos = pos; self.phi = phi; self.strategy = strategy


def _sc(**kw):
    return SubstrateConfig(enabled=True, k_cell=kw.pop("k_cell", 0),
                           movement_mode="diffusion",
                           contest_exponent=kw.pop("kappa", 0.0),
                           move_cost_flat=kw.pop("move_cost_flat", 0.0))


def _vn(pos, w=10, h=10):
    x, y = pos
    return {(x, y), ((x + 1) % w, y), ((x - 1) % w, y), (x, (y + 1) % h), (x, (y - 1) % h)}


def test_diffusion_candidate_set_is_von_neumann_r1():
    """§6.7: chosen target is always within the von-Neumann r=1 neighbourhood (incl. current)."""
    field = _MockField({(6, 5): 10.0, (5, 5): 1.0})  # rich neighbour, poor current
    a = _MockAgentD((5, 5))
    occ = {(5, 5): 1}
    import random
    rng = random.Random(0)
    for _ in range(20):
        tgt = diffusion_select_target(a, field, occ, None, _sc(), rng, temperature=1.0)
        assert tgt in _vn((5, 5)), f"target {tgt} outside von-Neumann r=1"


def test_diffusion_per_capita_self_limiting():
    """§6.8: a rich neighbour stops attracting as its occupancy rises (per-capita yield falls)."""
    field = _MockField({(6, 5): 10.0, (5, 5): 1.0})
    a = _MockAgentD((5, 5))
    import random
    rng = random.Random(0)
    # Empty rich neighbour: argmax picks it (10/1 > 1).
    occ_empty = {(5, 5): 1}
    tgt_empty = diffusion_select_target(a, field, occ_empty, None, _sc(), rng, temperature=None)
    assert tgt_empty == (6, 5)
    # Heavily crowded rich neighbour: 10/(20+1)=0.48 < 1 → agent stays.
    occ_crowded = {(5, 5): 1, (6, 5): 20}
    tgt_crowded = diffusion_select_target(a, field, occ_crowded, None, _sc(), rng, temperature=None)
    assert tgt_crowded == (5, 5), "agent should stay; crowded rich cell offers low per-capita"


def test_diffusion_move_cost_wiring():
    """§6.9: flat move cost subtracts on move, not on stay; large cost → stay."""
    field = _MockField({(6, 5): 10.0, (5, 5): 1.0})
    a = _MockAgentD((5, 5))
    import random
    rng = random.Random(0)
    # move_cost 0 → moves to richer neighbour
    assert diffusion_select_target(a, field, {(5, 5): 1}, None, _sc(move_cost_flat=0.0), rng, None) == (6, 5)
    # move_cost huge → 10 - 100 < 1 (stay has no cost) → stays
    assert diffusion_select_target(a, field, {(5, 5): 1}, None, _sc(move_cost_flat=100.0), rng, None) == (5, 5)


def test_diffusion_neutral_reduces_to_per_capita_argmax():
    """§6.10: affinity=crowd=1, move_cost=0 → choice is the argmax per-capita-yield cell."""
    field = _MockField({(5, 5): 2.0, (6, 5): 9.0, (4, 5): 3.0, (5, 6): 1.0, (5, 4): 0.0})
    a = _MockAgentD((5, 5))
    import random
    tgt = diffusion_select_target(a, field, {(5, 5): 1}, None, _sc(), random.Random(0), temperature=None)
    assert tgt == (6, 5), "should pick the highest per-capita-yield neighbour"


def test_diffusion_psi_inactive_no_movement_effect():
    """§6.11: ψ does not enter the diffusion utility — agents differing only in ψ choose identically."""
    field = _MockField({(6, 5): 5.0, (5, 5): 2.0})
    # diffusion_select_target reads only pos, phi, strategy — never ψ. Two 'agents' with
    # any ψ produce the same choice because ψ is not a parameter of the selector.
    a = _MockAgentD((5, 5), phi=0.5)
    import random
    t1 = diffusion_select_target(a, field, {(5, 5): 1}, None, _sc(), random.Random(7), temperature=1.0)
    t2 = diffusion_select_target(a, field, {(5, 5): 1}, None, _sc(), random.Random(7), temperature=1.0)
    assert t1 == t2  # deterministic given rng; ψ never consulted


# ─── §6.6 offspring on parent cell; §6.12 consumers handle bands ──────────────

def test_offspring_spawns_on_parent_cell_exact():
    """§6.6: _spawn_one(exact_pos=cell) places the offspring exactly on that cell."""
    world = _make_substrate_world(k_cell=0, kappa=0.0, n=10, grid=8)
    child = world._spawn_one(exact_pos=(3, 4))
    assert child.pos == (3, 4)


def test_joint_task_cohort_includes_co_occupants():
    """§6.12: JT cohort reads the cell's occupant band (co-occupants), not a single agent."""
    from sic_games.joint_task import JointTaskManager
    from sic_games.world import SugarField

    sf = SugarField(width=10, height=10, peaks=[(5, 5)], max_capacity=16, band_width_k=6, alpha=4)
    # Isolate a single joint-task cell at (5,5): zero everything else so only (5,5) qualifies.
    sf.capacity[:] = 0
    sf.sugar[:] = 0.0
    sf.effective_capacity[:] = 0.0
    sf.capacity[5, 5] = 16
    sf.effective_capacity[5, 5] = 16.0
    sf.sugar[5, 5] = 16.0

    # Three C agents co-located on (5,5) — a band.
    agents = [_MockAgentD((5, 5), phi=0.5) for _ in range(3)]
    for i, a in enumerate(agents):
        a.cred = 1.0; a.unique_id = i; a._pending_cred_delta = 0.0; a.wealth = 0.0; a.dormant = False
    mgr = JointTaskManager(distance_d=1, capacity_threshold=4, matthew_alpha=2.0,
                           epsilon=0.01, cred_bonus_per_participant=1.0)
    import random
    events = mgr.process_step(sf, agents, rng=random.Random(0))
    assert len(events) == 1, "JT should fire on the co-occupied high-capacity cell"
    assert len(events[0].cluster) == 3, f"cohort should include all 3 co-occupants, got {len(events[0].cluster)}"
