"""Stage 7.5 Workstream B -- GATE B1 JT parity tests.

Two tiers of testing:

  1. **Unit parity tests** (mechanics correctness):
     - Matthew shares arithmetic matches oracle exactly
     - Sugar conservation, double-count guard, no-event recovery

  2. **Tier-3 statistical battery** (the GATE B1 equivalence test):
     - 10 matched seed pairs (oracle vs vec JT), full-model runs
     - Tests 1-4 from ARCHITECTURE ss12.1-H (pre-registered 2026-06-06)
     - N(t) envelope, KS distributions, moments, JT event rate
     Marked @pytest.mark.slow: ~5-10 min on a dev machine.
     Run with:  pytest tests/test_soa_jt.py -m slow -v

The battery uses a hybrid model: oracle run.py with _jt_manager swapped for
VecJointTaskManager.  The oracle code is NOT modified (D4 frozen).
"""
from __future__ import annotations

import time

import numpy as np
import pytest
from scipy.stats import ks_2samp

from sic_games.config import (
    AgentsConfig,
    BirthCConfig,
    C2DefectionConfig,
    CarryingCostConfig,
    Config,
    DecisionConfig,
    JointTaskConfig,
    PopulationConfig,
    RunConfig,
    SubstrateConfig,
    WorldConfig,
)
from sic_games.joint_task import JointTaskEvent, JointTaskManager, matthew_shares
from sic_games.run import SugarWorld
from sic_games.soa_jt import VecJointTaskManager


# ---------------------------------------------------------------------------
# Small-model helpers (unit tests use a 20x20 grid, N=50, fixed population)
# ---------------------------------------------------------------------------

def _make_cfg(
    seed: int = 42,
    n_steps: int = 1,
    n_agents: int = 50,
    grid: tuple[int, int] = (20, 20),
    peaks: list[tuple[int, int]] | None = None,
    c2_defect: bool = True,
    multi_occ: bool = False,
    kappa: float = 0.0,
) -> Config:
    """Build a minimal carbon Config for unit tests."""
    if peaks is None:
        peaks = [(5, 5), (15, 15)]
    substrate = SubstrateConfig(
        enabled=multi_occ,
        k_cell=0,
        movement_mode="legacy",
        contest_exponent=kappa,
    )
    return Config(
        seed=seed,
        agents=AgentsConfig(initial_population=n_agents),
        world=WorldConfig(grid_size=grid, sugar_peaks=peaks),
        decision=DecisionConfig(strategy="carbon"),
        run=RunConfig(n_steps=n_steps),
        c2_defection=C2DefectionConfig(enabled=c2_defect),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        substrate=substrate,
    )


def _make_model(seed: int = 42, steps: int = 0, **kwargs) -> SugarWorld:
    cfg = _make_cfg(seed=seed, **kwargs)
    m = SugarWorld(cfg)
    for _ in range(steps):
        m.step()
    return m


def _vec_jt_for_model(model: SugarWorld) -> VecJointTaskManager:
    """Clone VecJointTaskManager from the model's oracle JT parameters."""
    jt = model._jt_manager
    return VecJointTaskManager(
        distance_d=jt.distance_d,
        capacity_threshold=jt.capacity_threshold,
        matthew_alpha=jt.matthew_alpha,
        epsilon=jt.epsilon,
        cred_bonus_per_participant=jt.cred_bonus_per_participant,
        seed=model.cfg.seed,
        c2_defection_enabled=jt.c2_defection_enabled,
    )


# ---------------------------------------------------------------------------
# Unit parity tests
# ---------------------------------------------------------------------------

def test_matthew_arithmetic_matches_oracle():
    """Vec Matthew shares match oracle matthew_shares() exactly (pure arithmetic)."""

    class _FakeAgent:
        def __init__(self, cred):
            self.cred = cred

    rng = np.random.default_rng(7)
    for _ in range(20):
        n = rng.integers(2, 8)
        creds = rng.uniform(0, 5, n)
        total = float(rng.uniform(1, 10))
        alpha = 2.0
        eps = 0.01

        agents_fake = [_FakeAgent(c) for c in creds]
        oracle_shares = matthew_shares(agents_fake, total, alpha, eps)

        # Vec arithmetic (mirrors soa_jt.py inner block)
        w_raw = (creds + eps) ** alpha
        w_sum = w_raw.sum()
        vec_shares = (total * w_raw / w_sum).tolist()

        assert np.allclose(oracle_shares, vec_shares, rtol=1e-9, atol=0.0), (
            f"Matthew mismatch: oracle={oracle_shares} vec={vec_shares}"
        )


def test_vec_jt_instantiation():
    """VecJointTaskManager constructs with correct parameters and offset table."""
    vtm = VecJointTaskManager(
        distance_d=1,
        capacity_threshold=4,
        matthew_alpha=2.0,
        epsilon=0.01,
        cred_bonus_per_participant=1.0,
        seed=42,
        c2_defection_enabled=True,
    )
    assert vtm.distance_d == 1
    assert vtm.capacity_threshold == 4
    assert vtm.matthew_alpha == 2.0
    assert vtm.c2_defection_enabled is True
    # d=1 Euclidean offsets: centre (0,0) + 4 cardinals = 5
    assert len(vtm._offsets) == 5


def test_vec_jt_no_event_when_no_sugar():
    """Zero-sugar field: no events fired, agent state unchanged."""
    m = _make_model(seed=42, steps=5)
    m.sugar_field.sugar[:] = 0.0

    agents = list(m.agents)
    wealth_before = [a.wealth for a in agents]
    cred_before = [a._pending_cred_delta for a in agents]

    vtm = _vec_jt_for_model(m)
    events = vtm.process_step(m.sugar_field, agents, None)

    assert events == []
    assert [a.wealth for a in agents] == wealth_before
    assert [a._pending_cred_delta for a in agents] == cred_before


def test_vec_jt_no_event_when_no_agents():
    """Empty agent list returns empty events without error."""
    m = _make_model(seed=42, steps=0)
    vtm = _vec_jt_for_model(m)
    events = vtm.process_step(m.sugar_field, [], None)
    assert events == []


def test_vec_jt_returns_joint_task_event_objects():
    """When JT fires, events are JointTaskEvent instances with correct structure."""
    # Dense 10x10 grid with 1 peak -- many agents near the peak => JT likely
    m = _make_model(seed=0, n_agents=30, grid=(10, 10), peaks=[(5, 5)], steps=10)
    vtm = _vec_jt_for_model(m)
    m.sugar_field.sugar[5, 5] = 4.0  # ensure the peak cell has sugar
    agents = list(m.agents)
    events = vtm.process_step(m.sugar_field, agents, None)

    for ev in events:
        assert isinstance(ev, JointTaskEvent)
        assert isinstance(ev.cell, tuple) and len(ev.cell) == 2
        assert len(ev.cluster) >= 2
        assert ev.total_sugar >= 0.0
        assert len(ev.sugar_shares) == len(ev.cluster)
        assert len(ev.cred_shares) == len(ev.cluster)
        # Sugar shares must sum to total_sugar
        assert abs(sum(ev.sugar_shares) - ev.total_sugar) < 1e-9, (
            f"sugar_shares don't sum to total: "
            f"{sum(ev.sugar_shares):.9f} != {ev.total_sugar:.9f}"
        )


def test_vec_jt_sugar_conservation():
    """Sugar removed from field == wealth distributed to agents."""
    m = _make_model(seed=42, steps=10)
    agents = list(m.agents)

    sugar_before = float(m.sugar_field.sugar.sum())
    wealth_before = sum(a.wealth for a in agents)

    vtm = _vec_jt_for_model(m)
    events = vtm.process_step(m.sugar_field, agents, None)

    sugar_after = float(m.sugar_field.sugar.sum())
    wealth_after = sum(a.wealth for a in agents)

    sugar_consumed = sugar_before - sugar_after
    wealth_gained = wealth_after - wealth_before

    # cred_bonus is free (not drawn from sugar); only sugar_shares come from field
    assert abs(wealth_gained - sugar_consumed) < 1e-9, (
        f"Conservation violated: consumed={sugar_consumed:.6f} gained={wealth_gained:.6f} "
        f"over {len(events)} event(s)"
    )


def test_vec_jt_no_double_count():
    """Each agent participates in at most one JT event per step."""
    m = _make_model(seed=99, steps=3, n_agents=20, grid=(10, 10),
                    peaks=[(2, 2), (8, 8)])
    agents = list(m.agents)
    m.sugar_field.sugar[2, 2] = 4.0
    m.sugar_field.sugar[8, 8] = 4.0

    vtm = _vec_jt_for_model(m)
    events = vtm.process_step(m.sugar_field, agents, None)

    seen_ids: set[int] = set()
    for ev in events:
        for a in ev.cluster:
            assert a.unique_id not in seen_ids, (
                f"Agent {a.unique_id} appeared in multiple JT events"
            )
            seen_ids.add(a.unique_id)


def test_vec_jt_step_counter_advances():
    """_step increments once per process_step call."""
    vtm = VecJointTaskManager(
        distance_d=1, capacity_threshold=4, matthew_alpha=2.0,
        epsilon=0.01, cred_bonus_per_participant=1.0, seed=0,
    )
    assert vtm._step == 0
    m = _make_model(seed=0, steps=0)
    m.sugar_field.sugar[:] = 0.0  # no events, but step must count
    vtm.process_step(m.sugar_field, list(m.agents), None)
    assert vtm._step == 1
    vtm.process_step(m.sugar_field, list(m.agents), None)
    assert vtm._step == 2


def test_vec_jt_replaces_oracle_smoke():
    """Model with _jt_manager swapped to VecJTM runs N steps without error."""
    m = _make_model(seed=42, steps=0)
    m._jt_manager = _vec_jt_for_model(m)
    for _ in range(20):
        m.step()
    assert len(m.metrics_log) == 20
    assert m.metrics_log[-1].population > 0


# ---------------------------------------------------------------------------
# Tier-3 statistical battery (GATE B1 -- ARCHITECTURE ss12.1-H)
# ---------------------------------------------------------------------------

SEEDS = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
N_STEPS = 400
WINDOW_START = 251   # steps 251..400 = last 150 steps for steady-state pool


def _make_battery_cfg(seed: int) -> Config:
    """Config as pre-registered in ARCHITECTURE ss12.1-H.

    NOTE: This config leads to population extinction before step 254 under
    diffusion+multi-occ at N_carry=800, so the WINDOW_START=251 sampling
    window is never reached.  The battery test FAILS with this config.
    This is an open finding requiring supervisor direction (see GATE B1 report).
    """
    return Config(
        seed=seed,
        agents=AgentsConfig(initial_population=500),
        world=WorldConfig(
            grid_size=(100, 100),
            sugar_peaks=[(25, 25), (25, 75), (75, 25), (75, 75)],
        ),
        decision=DecisionConfig(strategy="carbon"),
        run=RunConfig(n_steps=N_STEPS),
        c2_defection=C2DefectionConfig(enabled=True),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        substrate=SubstrateConfig(
            enabled=True,
            k_cell=0,
            movement_mode="diffusion",
            contest_exponent=1.0,
        ),
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            carrying_cost=CarryingCostConfig(enabled=True, N_carry=800),
        ),
    )


def _run_one(seed: int, use_vec_jt: bool) -> dict:
    """Run a full battery simulation; return trajectory + steady-state stats."""
    m = SugarWorld(_make_battery_cfg(seed))

    if use_vec_jt:
        jt = m._jt_manager
        m._jt_manager = VecJointTaskManager(
            distance_d=jt.distance_d,
            capacity_threshold=jt.capacity_threshold,
            matthew_alpha=jt.matthew_alpha,
            epsilon=jt.epsilon,
            cred_bonus_per_participant=jt.cred_bonus_per_participant,
            seed=seed,
            c2_defection_enabled=jt.c2_defection_enabled,
        )

    pop_traj: list[int] = []
    w_pool, c_pool, phi_pool, psi_pool, c1_pool, c2_pool = [], [], [], [], [], []
    mw_list, mc_list, gw_list, gc_list, jt_list = [], [], [], [], []

    for _ in range(N_STEPS):
        m.step()
        if not m.metrics_log:
            continue
        mets = m.metrics_log[-1]
        pop_traj.append(int(mets.population))
        if mets.step >= WINDOW_START:
            agents_snap = list(m.agents)
            w_pool.extend(a.wealth for a in agents_snap)
            c_pool.extend(a.cred for a in agents_snap)
            phi_pool.extend(a.phi for a in agents_snap)
            psi_pool.extend(a.psi for a in agents_snap)
            c1_pool.extend(a.c1 for a in agents_snap)
            c2_pool.extend(a.c2 for a in agents_snap)
            mw_list.append(mets.mean_wealth)
            mc_list.append(mets.mean_cred)
            gw_list.append(mets.gini_wealth)
            gc_list.append(mets.gini_cred)
            jt_list.append(mets.joint_task_count)

    def _mean(lst: list) -> float:
        return float(np.mean(lst)) if lst else 0.0

    return dict(
        pop_traj=pop_traj,
        wealth=w_pool,
        cred=c_pool,
        phi=phi_pool,
        psi=psi_pool,
        c1=c1_pool,
        c2=c2_pool,
        mean_wealth=_mean(mw_list),
        mean_cred=_mean(mc_list),
        gini_wealth=_mean(gw_list),
        gini_cred=_mean(gc_list),
        jt_per_step=_mean(jt_list),
    )


@pytest.mark.slow
def test_tier3_gate_b1_battery():
    """GATE B1 Tier-3 statistical equivalence battery (ARCHITECTURE ss12.1-H).

    Pre-registered thresholds (locked before any B1 code was written):
      Test 1: N(t) envelope -- min seed coverage >= 0.90 within oracle mean +/- 2sigma
      Test 2: KS statistic < 0.10 for all of {wealth, cred, phi, psi, c1, c2}
      Test 3: moment diff < 10% for >= 8/10 seeds (all 5 moments)
      Test 4: JT event rate within 20% for >= 9/10 seeds
    """
    oracle_runs: list[dict] = []
    vec_runs: list[dict] = []

    print("\nRunning Tier-3 battery (10 seeds x 2 models x 400 steps)...")
    for seed in SEEDS:
        t0 = time.perf_counter()
        o = _run_one(seed, use_vec_jt=False)
        v = _run_one(seed, use_vec_jt=True)
        dt = time.perf_counter() - t0
        print(
            f"  seed={seed}  oracle_jt={o['jt_per_step']:.1f}/step  "
            f"vec_jt={v['jt_per_step']:.1f}/step  ({dt:.1f}s)"
        )
        oracle_runs.append(o)
        vec_runs.append(v)

    # --- Test 1: N(t) trajectory envelope -----------------------------------
    T = min(len(r["pop_traj"]) for r in oracle_runs)
    oracle_pops = np.array([r["pop_traj"][:T] for r in oracle_runs], dtype=float)
    vec_pops = np.array([r["pop_traj"][:T] for r in vec_runs], dtype=float)
    oracle_mean = oracle_pops.mean(axis=0)
    oracle_std = oracle_pops.std(axis=0)
    lo = oracle_mean - 2.0 * oracle_std
    hi = oracle_mean + 2.0 * oracle_std
    per_seed_cov = np.array([
        float(np.mean((vec_pops[k] >= lo) & (vec_pops[k] <= hi)))
        for k in range(10)
    ])
    min_cov = float(per_seed_cov.min())
    print(
        f"\nTest 1 N(t) envelope: min coverage={min_cov:.3f} "
        f"per-seed={[f'{x:.2f}' for x in per_seed_cov]}"
    )
    assert min_cov >= 0.90, (
        f"Test 1 FAIL: N(t) min coverage {min_cov:.3f} < 0.90"
    )

    # --- Test 2: KS statistic on pooled steady-state distributions ----------
    VARS = ("wealth", "cred", "phi", "psi", "c1", "c2")
    KS_THRESHOLD = 0.10
    pool_o = {v: np.array(sum([r[v] for r in oracle_runs], [])) for v in VARS}
    pool_v = {v: np.array(sum([r[v] for r in vec_runs], [])) for v in VARS}
    ks_stats = {v: float(ks_2samp(pool_o[v], pool_v[v]).statistic) for v in VARS}
    print(f"\nTest 2 KS (threshold <{KS_THRESHOLD}):")
    for var, stat in ks_stats.items():
        print(f"  {var}: KS={stat:.4f}  {'PASS' if stat < KS_THRESHOLD else 'FAIL'}")
    failed_ks = [v for v, s in ks_stats.items() if s >= KS_THRESHOLD]
    assert not failed_ks, (
        "Test 2 FAIL: KS breached for: "
        + ", ".join(f"{v}={ks_stats[v]:.4f}" for v in failed_ks)
    )

    # --- Test 3: per-seed moment check --------------------------------------
    MOMENTS = ("mean_wealth", "mean_cred", "gini_wealth", "gini_cred", "jt_per_step")
    MOMENT_THRESH = 0.10
    MOMENT_MIN = 8
    moment_pass: dict[str, int] = {mk: 0 for mk in MOMENTS}
    for k in range(10):
        for mk in MOMENTS:
            o_val = oracle_runs[k][mk]
            v_val = vec_runs[k][mk]
            denom = max(abs(o_val), 1e-6)
            if abs(v_val - o_val) / denom < MOMENT_THRESH:
                moment_pass[mk] += 1
    print(f"\nTest 3 moments (diff <{MOMENT_THRESH*100:.0f}% for >={MOMENT_MIN}/10 seeds):")
    failed_moments = []
    for mk in MOMENTS:
        ok = moment_pass[mk] >= MOMENT_MIN
        print(f"  {mk}: {moment_pass[mk]}/10  {'PASS' if ok else 'FAIL'}")
        if not ok:
            failed_moments.append(mk)
    assert not failed_moments, (
        "Test 3 FAIL: moments not met for: "
        + ", ".join(f"{mk}({moment_pass[mk]}/10)" for mk in failed_moments)
    )

    # --- Test 4: JT event rate ----------------------------------------------
    JT_THRESH = 0.20
    JT_MIN = 9
    jt_pass = sum(
        1 for k in range(10)
        if oracle_runs[k]["jt_per_step"] > 0.0
        and (abs(vec_runs[k]["jt_per_step"] - oracle_runs[k]["jt_per_step"])
             / max(oracle_runs[k]["jt_per_step"], 1e-6)) < JT_THRESH
    )
    print(
        f"\nTest 4 JT rate (<{JT_THRESH*100:.0f}% diff): {jt_pass}/10 seeds  "
        f"{'PASS' if jt_pass >= JT_MIN else 'FAIL'}"
    )
    assert jt_pass >= JT_MIN, (
        f"Test 4 FAIL: JT rate criterion met only {jt_pass}/10 seeds (need {JT_MIN})"
    )

    print("\nGATE B1 Tier-3 battery: ALL 4 TESTS PASS")
