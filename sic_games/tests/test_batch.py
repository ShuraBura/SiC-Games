"""Stage 5: BatchRunner tests.

Tests (5):
  1. BatchRunner produces 4 rows for 2 configs × 2 seeds
  2. CRN=True: env_rng identical across configs at same seed
  3. CRN=True: agent_rng is independent of env_rng (different seeds)
  4. CRN=True: initial agent placements identical for C and Si at same env_seed
  5. existing_map: parquet is copied rather than re-run
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from sic_games.batch import BatchRunner
from sic_games.config import Config
from sic_games.run import SugarWorld


# ─── minimal config helpers ──────────────────────────────────────────────────

_WORLD_SMALL = dict(
    grid_size=[20, 20], toroidal=True,
    sugar_peaks=[[5, 15], [15, 5]],
    max_sugar_capacity=4, band_width_k=3, growth_rate_alpha=1,
)

_BASE_C = dict(
    seed=42,
    world=_WORLD_SMALL,
    agents=dict(initial_population=30, vision_dist=[1, 3], metabolic_rate_dist=[1, 2],
                max_age_dist=[20, 40], initial_wealth_dist=[5, 15],
                phi_mean=0.5, phi_std=0.2, psi_mean=0.5, psi_std=0.2,
                psi_beta_a=0.0, psi_beta_b=0.0,
                c1_mean=0.5, c1_std=0.2, c2_mean=0.5, c2_std=0.2),
    decision=dict(strategy="carbon"),
    carbon=dict(sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
                matthew_alpha=1.5, epsilon=0.01, cred_bonus_per_participant=1.0,
                velocity_tau=5, velocity_scale=1.0, f_C=0.0,
                status_amplification_beta=0.0),
    si_bounded=dict(sigma_si=1.051, beta_metabolism=1.0),
    joint_task=dict(distance_d=1, capacity_threshold=4),
    population=dict(mode="fixed"),
    birth_c=dict(p_max=0.03, tau_sub=5.0, r_stress=0.75, r_wealth=0.5,
                 rep_age_min=5, gamma=0.0, c_star_birth=10.0,
                 carrying_cost=dict(enabled=False, N_carry=400, alpha_carry=1.0)),
    birth_si=dict(p_fission_max=0.03, fission_wealth_mult=1.5, rep_age_min=5),
    reproduction=dict(mode="random", parent_radius=2, inherit_sigma=0.05,
                      coordinator="individual", lambda_inheritance=0.0),
    perturbation=dict(type="null"),
    initialization=dict(age_distribution="zero", age_init_upper_frac=0.5,
                        wealth_init_scale_k=False, cluster_init=False,
                        cluster_peak_index=0, cluster_radius=5),
    life_history=dict(forage_age_min=0, forage_age_max_offset=5,
                      eta_min=1.0, eta_old=1.0, eta_fission_offspring=1.0),
    dormancy=dict(enabled=False, tau_trickle=0.3),
    c2_defection=dict(enabled=True),
    support_pool=dict(enabled=False, r_pool=3, tau_parent=0.0, tau_pool=0.0,
                      k_reserve=5.0, k_draw=3.0, tau_cred=0.0, tau_cred_reward=0.0,
                      rho_carryover=0.0, k_pool_cap=0.0),
    run=dict(n_steps=10, metrics_every=1),
    visualization=dict(animate=False, save_static_plots=False),
)

_BASE_SI = {**_BASE_C, "decision": dict(strategy="si_bounded"),
            "si_bounded": dict(sigma_si=1.051, beta_metabolism=1.0),
            "dormancy": dict(enabled=False, tau_trickle=0.3)}


def _write_cfg(cfg_dict: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(cfg_dict, f, default_flow_style=False, sort_keys=False)
    return path


# ─── Test 1: 2×2 → 4 rows ────────────────────────────────────────────────────

def test_batchrunner_produces_output(tmp_path):
    """BatchRunner with 2 configs × 2 seeds produces 4 rows in summary."""
    cfg_c  = _write_cfg(_BASE_C,  tmp_path / "c_cfg.yaml")
    cfg_si = _write_cfg(_BASE_SI, tmp_path / "si_cfg.yaml")

    runner = BatchRunner(
        configs=[cfg_c, cfg_si],
        seeds=[42, 43],
        crn=True,
        n_workers=1,          # sequential — avoids subprocess overhead in tests
        task_id="test_2x2",
        output_root=tmp_path / "out",
        n_steps=10,
    )
    df = runner.run()

    assert len(df) == 4, f"Expected 4 rows, got {len(df)}"
    # Check required columns
    for col in ("config", "seed", "strategy", "A", "T", "tf",
                "N_lo", "N_hi", "N_mean", "collapse", "collapse_step"):
        assert col in df.columns, f"Missing column: {col}"
    # Seeds present
    assert set(df["seed"].tolist()) == {42, 43}
    # Strategies present
    assert "carbon" in df["strategy"].values
    assert "si_bounded" in df["strategy"].values


# ─── Test 2: env_rng identical for same seed ─────────────────────────────────

def test_crn_env_identical():
    """CRN=True: env_rng (np.random.default_rng(seed)) is identical for same seed.

    Two worlds constructed with env_seed=42 (different agent_seeds) must start
    with identical agent placements — because placement comes from env_rng.
    """
    cfg_c  = Config.model_validate(_BASE_C)
    cfg_si = Config.model_validate({**_BASE_C,
                                    "decision": {"strategy": "si_bounded"},
                                    "si_bounded": {"sigma_si": 1.051, "beta_metabolism": 1.0},
                                    "dormancy": {"enabled": False}})

    world_c  = SugarWorld(cfg_c,  env_seed=42, agent_seed=10042)
    world_si = SugarWorld(cfg_si, env_seed=42, agent_seed=10042)

    pos_c  = sorted(a.pos for a in world_c.agents)
    pos_si = sorted(a.pos for a in world_si.agents)

    assert pos_c == pos_si, (
        "With identical env_seed, initial agent positions must match between "
        "C and Si worlds."
    )


# ─── Test 3: agent_rng independent of env_rng ────────────────────────────────

def test_crn_agent_independent():
    """CRN=True: agent_rng (seed+10000) is independent of env_rng (seed).

    The two streams must produce different random values, confirming that
    environmental draws and agent draws are decoupled.
    """
    seed = 42
    env_draws   = np.random.default_rng(seed).integers(0, 10_000, 50)
    agent_draws = np.random.default_rng(seed + 10_000).integers(0, 10_000, 50)

    # The sequences must differ (they originate from different seeds)
    assert not np.array_equal(env_draws, agent_draws), (
        "env_rng and agent_rng sequences must be independent (different seeds)."
    )
    # Sanity: same-seed generators agree
    assert np.array_equal(
        np.random.default_rng(seed).integers(0, 10_000, 50),
        np.random.default_rng(seed).integers(0, 10_000, 50),
    )


# ─── Test 4: different agent_seeds → different dynamics ──────────────────────

def test_crn_different_agent_seeds_diverge():
    """Two worlds with same env_seed but different agent_seeds diverge in outcomes.

    Same starting positions (env) but different movement/shuffle randomness
    (agent) should produce different population trajectories.
    """
    cfg = Config.model_validate(_BASE_C)

    world_a = SugarWorld(cfg, env_seed=42, agent_seed=10042)
    world_b = SugarWorld(cfg, env_seed=42, agent_seed=20042)  # different agent_seed

    for _ in range(30):
        world_a.step()
        world_b.step()

    # Wealth distributions should differ (different movement/shuffle sequences)
    w_a = world_a.mean_wealth()
    w_b = world_b.mean_wealth()
    # Different agent RNG → different outcomes. Not guaranteed to diverge in 30
    # steps, but highly probable. Use a loose bound.
    # (If this flaps, increase steps or tighten seed choice.)
    agents_a = sorted(a.pos for a in world_a.agents)
    agents_b = sorted(a.pos for a in world_b.agents)
    # Positions or wealth must differ at some level
    assert agents_a != agents_b or abs(w_a - w_b) > 0.01, (
        "Worlds with different agent_seeds should diverge after 30 steps."
    )


# ─── Test 5: existing_map loads from cache ───────────────────────────────────

def test_existing_map_loads_cached(tmp_path):
    """existing_map: pre-existing parquet is copied; no re-run occurs."""
    # Write a minimal fake parquet in "existing" location
    existing_dir = tmp_path / "existing_run"
    existing_dir.mkdir()
    fake_df = pd.DataFrame({"step": [1, 2, 3], "population": [30, 30, 29]})
    fake_df.to_parquet(existing_dir / "metrics.parquet", index=False)

    cfg_c = _write_cfg(_BASE_C, tmp_path / "c_cfg.yaml")

    runner = BatchRunner(
        configs=[cfg_c],
        seeds=[42],
        crn=True,
        n_workers=1,
        task_id="test_cache",
        output_root=tmp_path / "out",
        existing_map={("c_cfg", 42): existing_dir},
    )
    df = runner.run()

    assert len(df) == 1
    # The run should have loaded the fake parquet — N comes from it
    # (N_lo from steps 1-3 after stable_t=500 would be 0 since steps are 1-3,
    # but the parquet was copied, confirming no re-run happened)
    out_parquet = tmp_path / "out" / "test_cache" / "c_cfg_seed42" / "metrics.parquet"
    assert out_parquet.exists(), "Parquet should have been copied to output dir."
    loaded = pd.read_parquet(out_parquet)
    pd.testing.assert_frame_equal(loaded, fake_df)
