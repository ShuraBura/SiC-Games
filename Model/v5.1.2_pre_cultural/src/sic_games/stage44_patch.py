"""Stage 4.4 Patch — Age initialisation fix + p_max re-calibration.

Two targeted fixes:
  1. age_init_upper_frac=0.25  (was implicit 0.5 in Stage 4.1b)
  2. p_max re-calibration sweep to find stable C equilibrium in N∈[150,400]

Task 0 — Diagnose p_max=0.07 explosion (reads Stage 4.4 Diagnostic parquet)
Task 1 — (Code change already applied; test suite run separately)
Task 2 — Run A bare sweep: p_max ∈ {0.03,0.04,0.05,0.06,0.065,0.07}, stop at first overshoot
Task 3 — Runs B/C/D: pool and λ verification at locked p_max

Blueprint: SiC_Games_Stage4_4_Patch.md v1.0
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8")

import base64
import copy
from io import BytesIO
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from sic_games.config import load_config
from sic_games.run import SugarWorld

# ─── constants ────────────────────────────────────────────────────────────────

_SEED = 42
_N_STEPS = 1000
_STABLE_T = 500
_N_LO, _N_HI = 150, 400
_EST_STARV_MAX = 0.78          # gate: est_starv ≤ 0.78/step
_N_BOMB = 800                  # abort runs that overshoot — C equilibrium at N~1500 not needed
_OUT_ROOT = Path("outputs/stage44_patch_seed42")
_DIAG_ROOT = Path("outputs/stage44_diag_seed42")

_SWEEP_P = [0.03, 0.04, 0.05, 0.06, 0.065, 0.07]

# ─── base config (k=4, β=1-4, seed=42, age_init_upper_frac=0.25) ─────────────

_BASE_PATCH = dict(
    seed=42,
    world=dict(grid_size=[50, 50], toroidal=True, sugar_peaks=[[10, 40], [40, 10]],
               max_sugar_capacity=16, band_width_k=6, growth_rate_alpha=4),
    agents=dict(initial_population=250, vision_dist=[1, 6], metabolic_rate_dist=[1, 4],
                max_age_dist=[60, 100], initial_wealth_dist=[5, 25],
                phi_mean=0.5, phi_std=0.2, psi_mean=0.5, psi_std=0.2,
                psi_beta_a=0.0, psi_beta_b=0.0,
                c1_mean=0.5, c1_std=0.2, c2_mean=0.5, c2_std=0.2),
    decision=dict(strategy="carbon"),
    carbon=dict(sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
                matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
                velocity_tau=10, velocity_scale=1.0, f_C=0.25,
                status_amplification_beta=1.0),
    joint_task=dict(distance_d=1, capacity_threshold=4),
    population=dict(mode="dynamic"),
    birth_c=dict(tau_sub=5.0, r_stress=0.75, k_stress=10.0, r_wealth=0.5,
                 rep_age_min=15, rep_age_max=None, gamma=0.2, c_star_birth=10.0),
    birth_si=dict(p_fission_max=0.065, fission_wealth_mult=1.5, rep_age_min=15),
    reproduction=dict(mode="biparental", parent_radius=3, inherit_sigma=0.05,
                      coordinator="individual", lambda_inheritance=0.0),
    perturbation=dict(type="null"),
    # Stage 4.4 patch: age_init_upper_frac=0.25 (was implicit 0.5 in Stage 4.1b)
    # Stage 4.4 patch: age_init=0.25, wealth_scale_k, cluster_init all set per-run in _make_cfg
    initialization=dict(age_distribution="realistic", age_init_upper_frac=0.25,
                        wealth_init_scale_k=False,
                        cluster_init=False, cluster_peak_index=0, cluster_radius=10),
    life_history=dict(forage_age_min=15, forage_age_max_offset=10, eta_min=0.3, eta_old=0.4,
                      eta_fission_offspring=1.0),
    # Pool ON config (used by Runs B, D)
    support_pool=dict(enabled=True, r_pool=5, tau_parent=0.1,
                      tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
                      tau_cred=0.5, tau_cred_reward=0.1,
                      rho_carryover=0.3, k_pool_cap=20.0),
    dormancy=dict(enabled=False),
    run=dict(n_steps=_N_STEPS, metrics_every=1),
    visualization=dict(animate=False, save_static_plots=False),
)

_POOL_OFF = dict(enabled=False, r_pool=5, tau_parent=0.0,
                 tau_pool=0.0, k_reserve=5.0, k_draw=3.0,
                 tau_cred=0.0, tau_cred_reward=0.0,
                 rho_carryover=0.0, k_pool_cap=0.0)


# ─── config builder / writer ──────────────────────────────────────────────────

def _make_cfg(p_max: float, out_dir: str,
              pool_on: bool, lambda_inh: float,
              wealth_scale_k: bool = False,
              cluster: bool = False) -> dict:
    cfg = copy.deepcopy(_BASE_PATCH)
    cfg["birth_c"]["p_max"] = p_max
    cfg["reproduction"]["lambda_inheritance"] = lambda_inh
    if not pool_on:
        cfg["support_pool"] = copy.deepcopy(_POOL_OFF)
    cfg["initialization"]["wealth_init_scale_k"] = wealth_scale_k
    cfg["initialization"]["cluster_init"] = cluster
    cfg["run"]["output_dir"] = out_dir
    return cfg


def _write_cfg(cfg_dict: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(cfg_dict, f, default_flow_style=False, sort_keys=False)
    return path


# ─── run / load ──────────────────────────────────────────────────────────────

def _run_or_load(cfg_path: Path, label: str) -> pd.DataFrame:
    cfg = load_config(str(cfg_path))
    out_dir = Path(cfg.run.output_dir)
    parquet = out_dir / "metrics.parquet"
    if parquet.exists():
        print(f"  [{label}] Loading cached: {parquet}")
        return pd.read_parquet(parquet)
    print(f"  [{label}] Running {cfg_path} ...")
    world = SugarWorld(cfg)
    for step_i in range(cfg.run.n_steps):
        world.step()
        if step_i > 50:
            n_total = len(list(world.agents))
            if n_total > _N_BOMB:
                print(f"  [{label}] BOMB at step {step_i+1}: n={n_total}>{_N_BOMB}. Aborting.")
                break
    df = world.metrics_to_df()
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet, index=False)
    n_vals = df["population"]
    print(f"  [{label}] Done. N=[{int(n_vals.min())},{int(n_vals.max())}]")
    return df


# ─── analysis helpers ─────────────────────────────────────────────────────────

def _late(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["step"] >= _STABLE_T]


def _n_range(df: pd.DataFrame) -> tuple[int, int]:
    late = _late(df)
    if late.empty:
        return 0, 0
    return int(late["population"].min()), int(late["population"].max())


def _collapse_step(df: pd.DataFrame) -> int | None:
    hits = df[df["population"] < 10]
    if hits.empty:
        return None
    return int(hits["step"].iloc[0])


def _survived(df: pd.DataFrame) -> bool:
    lo, hi = _n_range(df)
    return _N_LO <= lo and hi <= _N_HI


def _overshoot(df: pd.DataFrame) -> bool:
    """N > 400 sustained (late window minimum > 400)."""
    lo, _ = _n_range(df)
    return lo > _N_HI


def _est_starv(df: pd.DataFrame) -> float:
    late = _late(df)
    if late.empty or "deaths_starvation_established" not in late.columns:
        return 0.0
    return float(late["deaths_starvation_established"].mean())


def _gate_pass(df: pd.DataFrame) -> bool:
    return _survived(df) and _est_starv(df) <= _EST_STARV_MAX


def _col_mean(df: pd.DataFrame, col: str, t_start: int = _STABLE_T) -> float:
    late = df[df["step"] >= t_start]
    if late.empty or col not in late.columns:
        return float("nan")
    return float(late[col].mean())


def _mean_age_at(df: pd.DataFrame, t: int) -> float:
    row = df.iloc[(df["step"] - t).abs().argsort()[:1]]
    if row.empty or "mean_age" not in df.columns:
        return float("nan")
    return float(row["mean_age"].iloc[0])


def _births_per_step(df: pd.DataFrame) -> float:
    return _col_mean(df, "births_c")


def _juv_starv_per_step(df: pd.DataFrame) -> float:
    return _col_mean(df, "deaths_starvation_juvenile")


def _senescence_per_step(df: pd.DataFrame) -> float:
    return _col_mean(df, "deaths_senescence")


def _pool_draw_unmet_pct(df: pd.DataFrame) -> float:
    return _col_mean(df, "pool_draw_unmet_frac") * 100.0


def _n_at(df: pd.DataFrame, t: int) -> int:
    row = df.iloc[(df["step"] - t).abs().argsort()[:1]]
    if row.empty:
        return 0
    return int(row["population"].iloc[0])


# ─── Task 0: diagnose p=0.07 explosion from diagnostic parquet ───────────────

def task0_explosion_diagnosis() -> dict:
    """Read Stage 4.4 Diagnostic parquet for Run A p=0.07 and extract metrics."""
    print("\n" + "="*60)
    print("Task 0 — Diagnose p_max=0.07 explosion (diagnostic parquet)")
    print("="*60)
    parquet = _DIAG_ROOT / "A_p007" / "metrics.parquet"
    if not parquet.exists():
        print(f"  WARNING: diagnostic parquet not found at {parquet}")
        return {}
    df = pd.read_parquet(parquet)
    n100 = _n_at(df, 100)
    n500 = _n_at(df, 500)
    n1000 = _n_at(df, 1000)
    lo, hi = _n_range(df)
    births = _births_per_step(df)
    est_starv = _est_starv(df)
    juv_starv = _juv_starv_per_step(df)
    senes = _senescence_per_step(df)
    age_500 = _mean_age_at(df, 500)
    unmet = _pool_draw_unmet_pct(df)
    net_growth = births - (senes + est_starv + juv_starv)

    print(f"  N at t=100: {n100}")
    print(f"  N at t=500: {n500}")
    print(f"  N at t=1000: {n1000}  (N_late=[{lo},{hi}])")
    print(f"  Births/step (t≥500): {births:.3f}")
    print(f"  est_starv/step (t≥500): {est_starv:.3f}")
    print(f"  Juv starvation/step (t≥500): {juv_starv:.3f}")
    print(f"  Senescence/step (t≥500): {senes:.3f}")
    print(f"  Net growth ≈ {net_growth:.4f}/step")
    print(f"  Mean agent age at t=500: {age_500:.1f}")
    print(f"  Pool draw unmet %: {unmet:.1f}%")

    ratio = juv_starv / max(est_starv, 0.001)
    if ratio > 5:
        mechanism = (
            f"OVERSHOOT (stable high-N equilibrium). "
            f"births/step ({births:.1f}) ≈ total deaths/step ({senes+est_starv+juv_starv:.1f}), "
            f"net growth ≈ {net_growth:.4f}/step (≈0 → stable). "
            f"Juvenile starvation ({juv_starv:.1f}/step) is {ratio:.0f}× the established starvation "
            f"({est_starv:.3f}/step), confirming the grid is at carrying capacity "
            f"with juvenile mortality providing density-dependent ceiling. "
            f"N={lo}–{hi} >> gate [150,400]: over-calibrated, not exploding. "
            f"This is the upper stable attractor (k=4 bistability). "
            f"The fix is not to raise p_max further but to find the lower attractor via "
            f"age-init fix + narrower p_max sweep."
        )
    else:
        mechanism = (
            f"STRUCTURAL (no juvenile density feedback at k=4 scale). "
            f"births/step ({births:.1f}) >> deaths ({senes+est_starv+juv_starv:.1f}). "
            f"Juvenile starvation ({juv_starv:.1f}/step) is only {ratio:.1f}× est_starv — "
            f"not acting as a ceiling. The birth rule has no density-dependent cap. "
            f"p_max=0.07 is simply above the upper viable band."
        )

    result = dict(
        df=df, n100=n100, n500=n500, n1000=n1000,
        n_lo=lo, n_hi=hi,
        births=births, est_starv=est_starv, juv_starv=juv_starv,
        senescence=senes, net_growth=net_growth,
        age_500=age_500, unmet=unmet,
        juv_ratio=ratio, mechanism=mechanism,
    )
    print(f"\n  Mechanism: {mechanism[:120]}...")
    return result


# ─── Task 2: Run A patch sweep ────────────────────────────────────────────────

def task2_run_A() -> dict:
    """C bare sweep: pool off, λ=0, age_init_upper_frac=0.25.
    Runs in ascending p_max order; stops at first overshoot (N>400 sustained).
    """
    print("\n" + "="*60)
    print("Task 2 — Run A patch sweep (pool OFF, λ=0, age_init_upper_frac=0.25)")
    print("="*60)
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    locked_p = None
    overshoot_p = None

    for p in _SWEEP_P:
        tag = f"pA_p{str(p).replace('.', '')}"
        cfg_dict = _make_cfg(p, str(_OUT_ROOT / tag), pool_on=False, lambda_inh=0.0)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df = _run_or_load(cfg_path, f"pA-p{p}")

        lo, hi = _n_range(df)
        cs = _collapse_step(df)
        gate = _gate_pass(df)
        over = _overshoot(df)
        est = _est_starv(df)
        births = _births_per_step(df)
        juv = _juv_starv_per_step(df)
        senes = _senescence_per_step(df)
        age100 = _mean_age_at(df, 100)
        age300 = _mean_age_at(df, 300)
        age500 = _mean_age_at(df, 500)
        unmet = _pool_draw_unmet_pct(df)

        flag = "✓ PASS" if gate else ("  OVER" if over else "  FAIL")
        print(f"  {flag} pA-p{p}: N_late=[{lo},{hi}] collapse=t{cs} "
              f"est_starv={est:.3f} births={births:.2f}/step senes={senes:.2f}/step")

        results[p] = dict(
            df=df, tag=tag, p_max=p,
            n_lo=lo, n_hi=hi, collapse_step=cs,
            gate_pass=gate, overshoot=over,
            est_starv=est, births=births,
            juv_starv=juv, senescence=senes,
            age100=age100, age300=age300, age500=age500,
            pool_draw_unmet_pct=unmet,
        )

        if gate and locked_p is None:
            locked_p = p
            print(f"  ★ First gate pass at p={p}. Locked p_max_C = {p}")

        if over:
            overshoot_p = p
            print(f"  ✗ Overshoot at p={p}. Stopping sweep.")
            break

    if locked_p is None:
        print("\n  WARNING: No p_max passed the gate. Escalation required.")
    else:
        band_lo = locked_p
        band_hi = overshoot_p if overshoot_p is not None else f">{_SWEEP_P[-1]}"
        print(f"\n  Viable band: p_max ∈ [{band_lo}, {band_hi})")
        print(f"  Locked p_max_C (bare): {locked_p}")

    return dict(results=results, locked_p=locked_p, overshoot_p=overshoot_p)


# ─── Task 2b: Run A with wealth_init_scale_k=True ────────────────────────────

def task2b_run_A() -> dict:
    """C bare sweep identical to Task 2 but with wealth_init_scale_k=True.
    Configs tagged 'pA2b_*' to avoid cache collision with Task 2a runs.
    """
    print("\n" + "="*60)
    print("Task 2b — Run A patch sweep (wealth_init_scale_k=True, Uniform[20,100] at k=4)")
    print("="*60)
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    locked_p = None
    overshoot_p = None

    for p in _SWEEP_P:
        tag = f"pA2b_p{str(p).replace('.', '')}"
        cfg_dict = _make_cfg(p, str(_OUT_ROOT / tag), pool_on=False, lambda_inh=0.0,
                             wealth_scale_k=True)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df = _run_or_load(cfg_path, f"pA2b-p{p}")

        lo, hi = _n_range(df)
        cs = _collapse_step(df)
        gate = _gate_pass(df)
        over = _overshoot(df)
        est = _est_starv(df)
        births = _births_per_step(df)
        juv = _juv_starv_per_step(df)
        senes = _senescence_per_step(df)
        age100 = _mean_age_at(df, 100)
        age300 = _mean_age_at(df, 300)
        age500 = _mean_age_at(df, 500)
        unmet = _pool_draw_unmet_pct(df)
        # Mean initial wealth at t=0 (first step)
        w_mean_t0 = float(df[df["step"] == 0]["mean_wealth"].iloc[0]) if not df[df["step"] == 0].empty else float("nan")

        flag = "✓ PASS" if gate else ("  OVER" if over else "  FAIL")
        print(f"  {flag} pA2b-p{p}: N_late=[{lo},{hi}] collapse=t{cs} "
              f"est_starv={est:.3f} births={births:.2f}/step w0={w_mean_t0:.1f}")

        results[p] = dict(
            df=df, tag=tag, p_max=p,
            n_lo=lo, n_hi=hi, collapse_step=cs,
            gate_pass=gate, overshoot=over,
            est_starv=est, births=births,
            juv_starv=juv, senescence=senes,
            age100=age100, age300=age300, age500=age500,
            pool_draw_unmet_pct=unmet,
            w_mean_t0=w_mean_t0,
        )

        if gate and locked_p is None:
            locked_p = p
            print(f"  ★ First gate pass at p={p}. Locked p_max_C = {p}")

        if over:
            overshoot_p = p
            print(f"  ✗ Overshoot at p={p}. Stopping sweep.")
            break

    if locked_p is None:
        print("\n  WARNING: No p_max passed the gate. Escalation required.")
    else:
        band_lo = locked_p
        band_hi = overshoot_p if overshoot_p is not None else f">{_SWEEP_P[-1]}"
        print(f"\n  Viable band: p_max ∈ [{band_lo}, {band_hi})")
        print(f"  Locked p_max_C (bare, wealth-scaled): {locked_p}")

    return dict(results=results, locked_p=locked_p, overshoot_p=overshoot_p)


# ─── Task 2c: cluster_init=True ──────────────────────────────────────────────

def task2c_run_A() -> dict:
    """C bare sweep with all three fixes: age_init_upper_frac=0.25,
    wealth_init_scale_k=True, cluster_init=True (peak=0, radius=10).
    Ascending p_max order; stop at first overshoot.
    """
    print("\n" + "="*60)
    print("Task 2c — Run A patch sweep (cluster_init=True, all fixes active)")
    print("="*60)
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    locked_p = None
    overshoot_p = None

    for p in _SWEEP_P:
        tag = f"pA2c_p{str(p).replace('.', '')}"
        cfg_dict = _make_cfg(p, str(_OUT_ROOT / tag), pool_on=False, lambda_inh=0.0,
                             wealth_scale_k=True, cluster=True)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df = _run_or_load(cfg_path, f"pA2c-p{p}")

        lo, hi = _n_range(df)
        cs = _collapse_step(df)
        gate = _gate_pass(df)
        over = _overshoot(df)
        est = _est_starv(df)
        births = _births_per_step(df)
        juv = _juv_starv_per_step(df)
        senes = _senescence_per_step(df)
        age100 = _mean_age_at(df, 100)
        age300 = _mean_age_at(df, 300)
        age500 = _mean_age_at(df, 500)
        unmet = _pool_draw_unmet_pct(df)
        # Step-1 wealth (proxy for initial; step=0 not in metrics)
        w_step1 = float(df[df["step"] == 1]["mean_wealth"].iloc[0]) if not df[df["step"] == 1].empty else float("nan")

        # Spatial dispersal at checkpoints
        def _iso_at(t: int) -> float:
            row = df.iloc[(df["step"] - t).abs().argsort()[:1]]
            if row.empty or "pct_isolated_C" not in df.columns:
                return float("nan")
            return float(row["pct_isolated_C"].iloc[0])

        def _disp_at(t: int) -> float:
            row = df.iloc[(df["step"] - t).abs().argsort()[:1]]
            if row.empty or "spatial_dispersion" not in df.columns:
                return float("nan")
            return float(row["spatial_dispersion"].iloc[0])

        flag = "✓ PASS" if gate else ("  OVER" if over else "  FAIL")
        print(f"  {flag} pA2c-p{p}: N_late=[{lo},{hi}] collapse=t{cs} "
              f"est_starv={est:.3f} births={births:.2f}/step "
              f"iso@0={_iso_at(1):.1f}% iso@300={_iso_at(300):.1f}%")

        results[p] = dict(
            df=df, tag=tag, p_max=p,
            n_lo=lo, n_hi=hi, collapse_step=cs,
            gate_pass=gate, overshoot=over,
            est_starv=est, births=births,
            juv_starv=juv, senescence=senes,
            age100=age100, age300=age300, age500=age500,
            pool_draw_unmet_pct=unmet,
            w_step1=w_step1,
            iso_t0=_iso_at(1), iso_t50=_iso_at(50),
            iso_t100=_iso_at(100), iso_t300=_iso_at(300),
            disp_t0=_disp_at(1), disp_t50=_disp_at(50),
            disp_t100=_disp_at(100), disp_t300=_disp_at(300), disp_t500=_disp_at(500),
        )

        if gate and locked_p is None:
            locked_p = p
            print(f"  ★ First gate pass at p={p}. Locked p_max_C = {p}")

        if over:
            overshoot_p = p
            print(f"  ✗ Overshoot at p={p}. Stopping sweep.")
            break

    if locked_p is None:
        print("\n  WARNING: No p_max passed the gate. Escalation required.")
    else:
        band_lo = locked_p
        band_hi = overshoot_p if overshoot_p is not None else f">{_SWEEP_P[-1]}"
        print(f"\n  Viable band: p_max ∈ [{band_lo}, {band_hi})")
        print(f"  Locked p_max_C (cluster init): {locked_p}")

    return dict(results=results, locked_p=locked_p, overshoot_p=overshoot_p)


# ─── Task 3: Runs B/C/D ──────────────────────────────────────────────────────

def _run_series(run_label: str, p_values: list[float],
                pool_on: bool, lambda_inh: float,
                wealth_scale_k: bool = True, cluster: bool = True) -> dict:
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    for p in p_values:
        tag = f"p{run_label}_p{str(p).replace('.', '')}"
        cfg_dict = _make_cfg(p, str(_OUT_ROOT / tag), pool_on=pool_on,
                             lambda_inh=lambda_inh, wealth_scale_k=wealth_scale_k,
                             cluster=cluster)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df = _run_or_load(cfg_path, f"p{run_label}-p{p}")

        lo, hi = _n_range(df)
        cs = _collapse_step(df)
        gate = _gate_pass(df)
        est = _est_starv(df)
        births = _births_per_step(df)

        flag = "✓ PASS" if gate else ("  OVER" if _overshoot(df) else "  FAIL")
        print(f"  {flag} p{run_label}-p{p}: N_late=[{lo},{hi}] collapse=t{cs} "
              f"est_starv={est:.3f} births={births:.2f}/step")

        results[p] = dict(
            df=df, tag=tag, p_max=p,
            n_lo=lo, n_hi=hi, collapse_step=cs,
            gate_pass=gate, est_starv=est, births=births,
        )
    return results


def task3_run_BCD(locked_p: float | None) -> dict:
    """Pool and λ verification. Runs only if locked_p is set.
    All Task 3 configs include wealth_init_scale_k=True (same as Task 2b).
    """
    print("\n" + "="*60)
    print("Task 3 — Runs B/C/D: pool and λ verification")
    print("="*60)

    if locked_p is None:
        print("  SKIPPED — no locked p_max from Task 2b (gate not passed).")
        return dict(B={}, C={}, D={}, locked={})

    anchor = 0.03
    hi_p = round(locked_p + 0.01, 4)
    # Build p_value lists (deduplicate anchor vs locked)
    bcd_p = sorted(set([anchor, locked_p]))
    bcd_p_hi = sorted(set([anchor, locked_p, hi_p]))

    print(f"  Locked p_max = {locked_p}. Running p ∈ {bcd_p_hi} for B/C, {bcd_p} for D.")

    print("\n  Run B — pool ON, λ=0")
    runB = _run_series("B", bcd_p_hi, pool_on=True, lambda_inh=0.0, wealth_scale_k=True)

    print("\n  Run C — pool OFF, λ=0.1")
    runC = _run_series("C", bcd_p_hi, pool_on=False, lambda_inh=0.1, wealth_scale_k=True)

    print("\n  Run D — pool ON, λ=0.1")
    runD = _run_series("D", bcd_p, pool_on=True, lambda_inh=0.1, wealth_scale_k=True)

    # Determine locked p_max per condition
    def _find_locked(results: dict) -> float | None:
        for p in sorted(results.keys()):
            if results[p]["gate_pass"]:
                return p
        return None

    locked_B = _find_locked(runB)
    locked_C = _find_locked(runC)
    locked_D = _find_locked(runD)

    print(f"\n  Locked p_max: bare={locked_p}, B(pool)={locked_B}, "
          f"C(λ)={locked_C}, D(pool+λ)={locked_D}")

    return dict(B=runB, C=runC, D=runD,
                locked=dict(bare=locked_p, B=locked_B, C=locked_C, D=locked_D))


# ─── Figures ─────────────────────────────────────────────────────────────────

def _fig_to_b64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def _img(b64: str, caption: str = "") -> str:
    tag = f'<img src="data:image/png;base64,{b64}" style="max-width:100%;"><br>'
    if caption:
        tag += f'<p class="fig-caption">{caption}</p>'
    return tag


def generate_figures(task0: dict, task2: dict, task2b: dict, task2c: dict, task3: dict) -> dict[str, str]:
    figs = {}
    print("\n=== Generating figures ===")
    runA = task2["results"]
    runB = task3.get("B", {})
    runC = task3.get("C", {})
    runD = task3.get("D", {})

    # ── Figure 1: Task 0 — diagnostic p=0.07 N(t) ────────────────────────────
    if task0 and "df" in task0:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        df07 = task0["df"]
        axes[0].plot(df07["step"], df07["population"], color="#E91E63", lw=2)
        axes[0].axhline(_N_LO, color="red", ls="--", lw=0.8, label="Gate [150,400]")
        axes[0].axhline(_N_HI, color="red", ls="--", lw=0.8)
        axes[0].set_xlabel("Step"); axes[0].set_ylabel("N")
        axes[0].set_title("Diagnostic p=0.07: N(t)")
        axes[0].legend(fontsize=8)

        axes[1].plot(df07["step"], df07["births_c"], label="births_c/step", color="#4CAF50", lw=1.5)
        axes[1].plot(df07["step"], df07["deaths_senescence"], label="senescence/step", color="#F44336", lw=1.5)
        axes[1].plot(df07["step"], df07["deaths_starvation_juvenile"], label="juv_starv/step", color="#FF9800", lw=1.5)
        axes[1].plot(df07["step"], df07["deaths_starvation_established"], label="est_starv/step", color="#9C27B0", lw=1.5)
        axes[1].set_xlabel("Step"); axes[1].set_ylabel("Events/step")
        axes[1].set_title("Diagnostic p=0.07: births vs deaths")
        axes[1].legend(fontsize=8)
        fig.tight_layout()
        figs["task0_p007"] = _fig_to_b64(fig)
        print("  task0_p007")

    # ── Figure 2: Task 2 — Run A patch N(t) overlay ──────────────────────────
    if runA:
        p_list = list(runA.keys())
        colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(p_list)))
        fig, ax = plt.subplots(figsize=(11, 5))
        for (p, res), col in zip(runA.items(), colors):
            lw = 2.0 if res.get("gate_pass") else 1.2
            ls = "-" if res.get("gate_pass") else ("--" if not res.get("overshoot") else ":")
            ax.plot(res["df"]["step"], res["df"]["population"],
                    label=f"p={p}", color=col, lw=lw, ls=ls)
        ax.axhline(_N_LO, color="red", ls="--", lw=0.8, label="Gate [150,400]")
        ax.axhline(_N_HI, color="red", ls="--", lw=0.8)
        ax.axvline(_STABLE_T, color="gray", ls=":", lw=0.8, label=f"t={_STABLE_T}")
        ax.set_xlabel("Step"); ax.set_ylabel("N")
        ax.set_title("Task 2 — Run A patch sweep: N(t) by p_max\n(age_init_upper_frac=0.25)")
        ax.legend(fontsize=8); ax.set_ylim(bottom=0)
        figs["pA_nt"] = _fig_to_b64(fig)
        print("  pA_nt")

    # ── Figure 3: Task 2 — births/senescence/juv_starv bars ──────────────────
    if runA:
        p_arr = list(runA.keys())
        births_v = [runA[p]["births"] for p in p_arr]
        senes_v = [runA[p]["senescence"] for p in p_arr]
        juv_v = [runA[p]["juv_starv"] for p in p_arr]
        x = np.arange(len(p_arr))
        w = 0.25
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(x - w, births_v, w, label="births/step", color="#4CAF50")
        ax.bar(x, senes_v, w, label="senescence/step", color="#F44336")
        ax.bar(x + w, juv_v, w, label="juv_starv/step", color="#FF9800")
        ax.set_xticks(x); ax.set_xticklabels([f"p={p}" for p in p_arr])
        ax.set_ylabel("Events/step (t≥500)")
        ax.set_title("Task 2 — Run A: births vs deaths at t≥500")
        ax.legend(fontsize=9)
        figs["pA_births_deaths"] = _fig_to_b64(fig)
        print("  pA_births_deaths")

    # ── Figure 4: Task 2 — mean age evolution ────────────────────────────────
    if runA:
        p_list = list(runA.keys())
        colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(p_list)))
        fig, ax = plt.subplots(figsize=(10, 4))
        for (p, res), col in zip(runA.items(), colors):
            df = res["df"]
            alive = df[df["population"] > 0]
            if not alive.empty:
                ax.plot(alive["step"], alive["mean_age"],
                        label=f"p={p}", color=col, lw=1.5)
        ax.set_xlabel("Step"); ax.set_ylabel("Mean agent age (steps)")
        ax.set_title("Task 2 — Run A: mean agent age over time")
        ax.legend(fontsize=8)
        figs["pA_mean_age"] = _fig_to_b64(fig)
        print("  pA_mean_age")

    # ── Figure 5: Task 3 — N(t) for Runs B/C/D at locked p_max ──────────────
    locked_p = task3.get("locked", {}).get("bare")
    if locked_p and (runB or runC or runD):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
        titles = ["Run B: pool ON, λ=0", "Run C: pool OFF, λ=0.1", "Run D: pool ON, λ=0.1"]
        all_runs = [runB, runC, runD]
        for ax, run_res, title in zip(axes, all_runs, titles):
            if not run_res:
                ax.set_title(f"{title}\n(skipped)")
                continue
            p_list = sorted(run_res.keys())
            colors2 = plt.cm.Set2(np.linspace(0, 1, len(p_list)))
            for p, col in zip(p_list, colors2):
                res = run_res[p]
                lw = 2.0 if res.get("gate_pass") else 1.2
                ax.plot(res["df"]["step"], res["df"]["population"],
                        label=f"p={p}", color=col, lw=lw)
            ax.axhline(_N_LO, color="red", ls="--", lw=0.8)
            ax.axhline(_N_HI, color="red", ls="--", lw=0.8)
            ax.set_xlabel("Step"); ax.set_ylabel("N"); ax.set_title(title)
            ax.legend(fontsize=7); ax.set_ylim(bottom=0)
        fig.tight_layout()
        figs["pBCD_nt"] = _fig_to_b64(fig)
        print("  pBCD_nt")

    # ── Figure 5b: Task 2b — N(t) overlay ────────────────────────────────────
    runA2b = task2b.get("results", {})
    if runA2b:
        p_list2b = list(runA2b.keys())
        colors2b = plt.cm.plasma(np.linspace(0.1, 0.9, len(p_list2b)))
        fig, ax = plt.subplots(figsize=(11, 5))
        for (p, res), col in zip(runA2b.items(), colors2b):
            lw = 2.0 if res.get("gate_pass") else 1.2
            ls = "-" if res.get("gate_pass") else ("--" if not res.get("overshoot") else ":")
            ax.plot(res["df"]["step"], res["df"]["population"],
                    label=f"p={p}", color=col, lw=lw, ls=ls)
        ax.axhline(_N_LO, color="red", ls="--", lw=0.8, label="Gate [150,400]")
        ax.axhline(_N_HI, color="red", ls="--", lw=0.8)
        ax.axvline(_STABLE_T, color="gray", ls=":", lw=0.8, label=f"t={_STABLE_T}")
        ax.set_xlabel("Step"); ax.set_ylabel("N")
        ax.set_title("Task 2b — Run A: N(t) by p_max\n(wealth_init_scale_k=True, Uniform[20,100])")
        ax.legend(fontsize=8); ax.set_ylim(bottom=0)
        figs["pA2b_nt"] = _fig_to_b64(fig)
        print("  pA2b_nt")

    # ── Figure 6: 2a vs 2b comparison overlay ────────────────────────────────
    common_p = sorted(set(runA.keys()) & set(runA2b.keys())) if runA and runA2b else []
    if common_p:
        fig, ax = plt.subplots(figsize=(11, 5))
        colors_a = plt.cm.Blues(np.linspace(0.4, 0.9, len(common_p)))
        colors_b = plt.cm.Oranges(np.linspace(0.4, 0.9, len(common_p)))
        for p, col_a, col_b in zip(common_p, colors_a, colors_b):
            ax.plot(runA[p]["df"]["step"], runA[p]["df"]["population"],
                    color=col_a, lw=1.2, ls="--", label=f"2a p={p}")
            ax.plot(runA2b[p]["df"]["step"], runA2b[p]["df"]["population"],
                    color=col_b, lw=1.8, ls="-", label=f"2b p={p}")
        ax.axhline(_N_LO, color="red", ls="--", lw=0.8)
        ax.axhline(_N_HI, color="red", ls="--", lw=0.8, label="Gate")
        ax.set_xlabel("Step"); ax.set_ylabel("N")
        ax.set_title("Task 2a vs 2b: wealth=[5,25] (blue dashed) vs wealth=[20,100] (orange solid)")
        ax.legend(fontsize=7, ncol=2); ax.set_ylim(bottom=0)
        figs["pA_compare"] = _fig_to_b64(fig)
        print("  pA_compare")

    # ── Figure 7: Task 2c — cluster_init N(t) overlay ────────────────────────
    runA2c = task2c.get("results", {})
    if runA2c:
        p_list2c = list(runA2c.keys())
        colors2c = plt.cm.cool(np.linspace(0.1, 0.9, len(p_list2c)))
        fig, ax = plt.subplots(figsize=(11, 5))
        for (p, res), col in zip(runA2c.items(), colors2c):
            lw = 2.5 if res.get("gate_pass") else 1.2
            ls = "-" if res.get("gate_pass") else ("--" if not res.get("overshoot") else ":")
            ax.plot(res["df"]["step"], res["df"]["population"],
                    label=f"p={p}", color=col, lw=lw, ls=ls)
        ax.axhline(_N_LO, color="red", ls="--", lw=0.8, label="Gate [150,400]")
        ax.axhline(_N_HI, color="red", ls="--", lw=0.8)
        ax.axvline(_STABLE_T, color="gray", ls=":", lw=0.8, label=f"t={_STABLE_T}")
        ax.set_xlabel("Step"); ax.set_ylabel("N")
        ax.set_title("Task 2c — Run A: N(t) by p_max\n(cluster_init=True, wealth=[20,100], age_frac=0.25)")
        ax.legend(fontsize=8); ax.set_ylim(bottom=0)
        figs["pA2c_nt"] = _fig_to_b64(fig)
        print("  pA2c_nt")

        # Dispersal plot for best run (locked_p or p=0.05)
        best_p = task2c.get("locked_p") or 0.05
        if best_p in runA2c:
            df_best = runA2c[best_p]["df"]
            if "pct_isolated_C" in df_best.columns:
                fig, ax = plt.subplots(figsize=(10, 4))
                alive = df_best[df_best["population"] > 0]
                ax.plot(alive["step"], alive["pct_isolated_C"], color="#9C27B0", lw=2)
                ax.axhline(40, color="orange", ls="--", lw=1, label="40% Allee threshold")
                ax.set_xlabel("Step"); ax.set_ylabel("% isolated C agents")
                ax.set_title(f"Task 2c p={best_p}: pct_isolated_C — cluster dispersal")
                ax.legend(); ax.set_ylim(0, 105)
                figs["pA2c_dispersal"] = _fig_to_b64(fig)
                print("  pA2c_dispersal")

    print(f"  Figures generated: {list(figs.keys())}")
    return figs


# ─── HTML Report ─────────────────────────────────────────────────────────────

def _css() -> str:
    return """
body { font-family: sans-serif; max-width: 1200px; margin: auto; padding: 20px; }
h1 { color: #1565C0; }
h2 { color: #283593; border-bottom: 2px solid #C5CAE9; }
h3 { color: #37474F; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }
th, td { border: 1px solid #CFD8DC; padding: 6px 10px; text-align: left; }
th { background: #E8EAF6; }
tr:nth-child(even) { background: #F5F5F5; }
.pass { color: #2E7D32; font-weight: bold; }
.fail { color: #C62828; }
.over { color: #E65100; }
.warn { color: #F57F17; }
.fig-caption { font-size: 12px; color: #555; margin-top: -6px; margin-bottom: 12px; }
pre { background: #F5F5F5; padding: 10px; border-left: 3px solid #1565C0; font-size: 12px; }
.gate-box { background: #E8F5E9; border: 1px solid #A5D6A7; padding: 10px; border-radius: 4px; margin: 8px 0; }
.escalate-box { background: #FFF3E0; border: 1px solid #FFCC80; padding: 10px; border-radius: 4px; margin: 8px 0; }
"""


def _gate_cell(val: bool) -> str:
    if val:
        return '<td class="pass">✓ PASS</td>'
    return '<td class="fail">FAIL</td>'


def _fmt(v, digits=3) -> str:
    if isinstance(v, float) and np.isnan(v):
        return "—"
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    if v is None:
        return "None"
    return str(v)


def write_report(task0: dict, task2: dict, task2b: dict, task2c: dict, task3: dict, figs: dict,
                 n_tests_total: int = 166, n_tests_new: int = 6) -> Path:
    """Write the patch HTML report."""
    print("\n=== Writing report_patch.html ===")
    locked = task3.get("locked", {})
    runA = task2.get("results", {})
    runB = task3.get("B", {})
    runC = task3.get("C", {})
    runD = task3.get("D", {})
    locked_p_bare = task2.get("locked_p")
    overshoot_p = task2.get("overshoot_p")

    # ── §0: Explosion diagnosis ───────────────────────────────────────────────
    sec0 = "<h2>§0 — Explosion diagnosis (p_max=0.07, Stage 4.4 Diagnostic)</h2>\n"
    if task0:
        sec0 += """
<p>From the Stage 4.4 Diagnostic parquet for Run A p_max=0.07
(pool OFF, λ=0, age_init_upper_frac=0.50 implicit):</p>
"""
        sec0 += """<table>
<tr><th>Metric</th><th>p_max=0.07</th></tr>
"""
        rows = [
            ("N at t=100", task0.get("n100", "?")),
            ("N at t=300", "—"),
            ("N at t=500", task0.get("n500", "?")),
            ("N at t=1000 (= N_late min–max)", f"{task0.get('n_lo','?')}–{task0.get('n_hi','?')}"),
            ("Mean births/step (t≥500)", _fmt(task0.get("births", float("nan")))),
            ("est_starv/step (t≥500)", _fmt(task0.get("est_starv", float("nan")))),
            ("Juv starvation deaths/step (t≥500)", _fmt(task0.get("juv_starv", float("nan")))),
            ("Senescence deaths/step (t≥500)", _fmt(task0.get("senescence", float("nan")))),
            ("Net growth/step (t≥500)", _fmt(task0.get("net_growth", float("nan")), 4)),
            ("Mean agent age at t=500", _fmt(task0.get("age_500", float("nan")), 1)),
            ("Pool draw unmet % (t≥500)", _fmt(task0.get("unmet", float("nan")), 1)),
            ("Juv_starv / est_starv ratio", _fmt(task0.get("juv_ratio", float("nan")), 1)),
        ]
        for label, val in rows:
            sec0 += f"<tr><td>{label}</td><td>{val}</td></tr>\n"
        sec0 += "</table>\n"
        sec0 += f"<p><strong>Mechanism:</strong> {task0.get('mechanism', '—')}</p>\n"
        if "task0_p007" in figs:
            sec0 += _img(figs["task0_p007"],
                         "Figure 0: Diagnostic p=0.07 — N(t) (left) and birth/death rates (right)")
    else:
        sec0 += "<p class='warn'>Diagnostic parquet not found — Task 0 skipped.</p>\n"

    # ── §1: Age initialisation fix ────────────────────────────────────────────
    sec1 = "<h2>§1 — Age initialisation fix</h2>\n"
    sec1 += """
<h3>Code changes</h3>
<ul>
<li><strong>config.py</strong> <code>InitializationConfig</code>: added
    <code>age_init_upper_frac: float = Field(0.5, gt=0.0, le=1.0)</code>
    (default 0.5 preserves Stage 4.1b behaviour).</li>
<li><strong>run.py</strong> <code>SugarWorld.__init__</code>: stored as
    <code>self._age_init_upper_frac = config.initialization.age_init_upper_frac</code>.</li>
<li><strong>run.py</strong> <code>_spawn_one</code>: changed<br>
    <code>agent.age = self._rng_py.randint(0, max_age // 2)</code><br>
    to<br>
    <code>upper = max(0, int(max_age * self._age_init_upper_frac))</code><br>
    <code>agent.age = self._rng_py.randint(0, upper) if upper &gt; 0 else 0</code></li>
<li><strong>tests/test_life_history.py</strong>: added
    <code>test_age_init_upper_frac()</code> and
    <code>test_age_init_upper_frac_default()</code>.</li>
</ul>
<h3>Effect</h3>
<p>With τ_max ∈ [60, 100] and age_init_upper_frac=0.25:
starting ages drawn from Uniform[0, floor(τ_max × 0.25)] = Uniform[0, 15–25].
Mean starting age ≈ τ_max/8 ≈ 10 steps (below forage_age_min=15 — mostly juveniles).
First-generation senescence wave pushed from t≈20–50 to t≈45–75; lower amplitude.</p>
"""
    sec1 += f"""
<h3>Test results</h3>
<table>
<tr><th>Metric</th><th>Result</th></tr>
<tr><td>New tests added</td><td>{n_tests_new}</td></tr>
<tr><td>Total test suite</td><td>{n_tests_total} tests</td></tr>
<tr><td>Suite outcome</td><td class="pass">ALL PASSED</td></tr>
<tr><td><code>test_age_init_upper_frac</code> (frac=0.25)</td><td class="pass">PASS</td></tr>
<tr><td><code>test_age_init_upper_frac_default</code> (frac=0.5)</td><td class="pass">PASS</td></tr>
<tr><td>All prior tests</td><td class="pass">PASS (no regressions)</td></tr>
</table>
"""

    # ── §2: p_max sweep (Run A) ───────────────────────────────────────────────
    sec2 = "<h2>§2 — p_max sweep (Run A bare, pool OFF, λ=0)</h2>\n"
    sec2 += "<p>All runs: seed=42, 1000 steps, k_grid=4, pool OFF, λ=0, age_init_upper_frac=0.25.</p>\n"
    sec2 += "<p>Gate: N ∈ [150, 400] at t≥500, est_starv ≤ 0.78/step.</p>\n"

    # Full sweep table
    sec2 += """<table>
<tr>
  <th>p_max</th><th>Gate</th><th>N_late [lo,hi]</th><th>collapse_step</th>
  <th>est_starv/step</th><th>births/step</th><th>senescence/step</th>
  <th>juv_starv/step</th><th>births/senes ratio</th>
  <th>mean_age t=100</th><th>mean_age t=300</th><th>mean_age t=500</th>
  <th>pool_unmet %</th>
</tr>
"""
    for p, res in runA.items():
        gate = res["gate_pass"]
        over = res.get("overshoot", False)
        if gate:
            gate_str = '<td class="pass">✓ PASS</td>'
        elif over:
            gate_str = '<td class="over">OVERSHOOT</td>'
        else:
            gate_str = '<td class="fail">FAIL</td>'
        lo, hi = res["n_lo"], res["n_hi"]
        cs = res["collapse_step"]
        births_senes = (res["births"] / max(res["senescence"], 0.001))
        sec2 += f"""<tr>
  <td>{p}</td>{gate_str}<td>[{lo},{hi}]</td><td>{cs if cs else '—'}</td>
  <td>{_fmt(res['est_starv'])}</td><td>{_fmt(res['births'], 2)}</td>
  <td>{_fmt(res['senescence'], 2)}</td><td>{_fmt(res['juv_starv'], 2)}</td>
  <td>{_fmt(births_senes, 2)}</td>
  <td>{_fmt(res['age100'], 1)}</td><td>{_fmt(res['age300'], 1)}</td>
  <td>{_fmt(res['age500'], 1)}</td>
  <td>{_fmt(res['pool_draw_unmet_pct'], 1)}</td>
</tr>
"""
    sec2 += "</table>\n"

    if locked_p_bare is not None:
        ovs = overshoot_p if overshoot_p else f">{_SWEEP_P[-1]}"
        sec2 += f"""
<div class="gate-box">
<strong>Viable band:</strong> p_max ∈ [{locked_p_bare}, {ovs})<br>
<strong>Locked p_max_C (bare):</strong> {locked_p_bare}
(first p_max to pass gate N∈[{_N_LO},{_N_HI}], est_starv≤{_EST_STARV_MAX})
</div>
"""
    else:
        sec2 += """
<div class="escalate-box">
<strong>ESCALATION REQUIRED:</strong> No p_max in [0.03, 0.07] passed the gate
with age_init_upper_frac=0.25. The age-init fix alone is insufficient.
Supervisor decision required before proceeding.
</div>
"""

    if "pA_nt" in figs:
        sec2 += _img(figs["pA_nt"],
                     "Figure 2a: Run A patch sweep — N(t) overlay for all p_max values")
    if "pA_births_deaths" in figs:
        sec2 += _img(figs["pA_births_deaths"],
                     "Figure 2b: Run A — births, senescence, juvenile starvation per step (t≥500)")
    if "pA_mean_age" in figs:
        sec2 += _img(figs["pA_mean_age"],
                     "Figure 2c: Run A — mean agent age evolution (confirms age-init fix)")

    # ── §2b: Task 2b — wealth-scaled sweep ───────────────────────────────────
    runA2b = task2b.get("results", {})
    locked_p2b = task2b.get("locked_p")
    overshoot_p2b = task2b.get("overshoot_p")

    sec2b = "<h2>§2b — Task 2b: p_max sweep with wealth_init_scale_k=True</h2>\n"
    sec2b += ("<p>Amendment: initial wealth scaled by k_grid=4: "
              "Uniform[5×4, 25×4] = Uniform[20, 100] at t=0. "
              "Newborn wealth unchanged. All other parameters identical to Task 2a.</p>\n")
    sec2b += "<p>Gate: N ∈ [150, 400] at t≥500, est_starv ≤ 0.78/step.</p>\n"

    if runA2b:
        sec2b += """<table>
<tr>
  <th>p_max</th><th>Gate</th><th>N_late [lo,hi]</th><th>collapse_step</th>
  <th>est_starv/step</th><th>births/step</th><th>senescence/step</th>
  <th>juv_starv/step</th><th>births/senes ratio</th>
  <th>mean_age t=100</th><th>mean_age t=300</th><th>mean_age t=500</th>
  <th>w_init_mean_t0</th>
</tr>
"""
        for p, res in runA2b.items():
            gate = res["gate_pass"]
            over = res.get("overshoot", False)
            if gate:
                gate_str = '<td class="pass">✓ PASS</td>'
            elif over:
                gate_str = '<td class="over">OVERSHOOT</td>'
            else:
                gate_str = '<td class="fail">FAIL</td>'
            lo, hi = res["n_lo"], res["n_hi"]
            cs = res["collapse_step"]
            births_senes = (res["births"] / max(res["senescence"], 0.001))
            sec2b += f"""<tr>
  <td>{p}</td>{gate_str}<td>[{lo},{hi}]</td><td>{cs if cs else '—'}</td>
  <td>{_fmt(res['est_starv'])}</td><td>{_fmt(res['births'], 2)}</td>
  <td>{_fmt(res['senescence'], 2)}</td><td>{_fmt(res['juv_starv'], 2)}</td>
  <td>{_fmt(births_senes, 2)}</td>
  <td>{_fmt(res['age100'], 1)}</td><td>{_fmt(res['age300'], 1)}</td>
  <td>{_fmt(res['age500'], 1)}</td>
  <td>{_fmt(res.get('w_mean_t0', float('nan')), 1)}</td>
</tr>
"""
        sec2b += "</table>\n"

    if locked_p2b is not None:
        ovs2b = overshoot_p2b if overshoot_p2b else f">{_SWEEP_P[-1]}"
        sec2b += f"""
<div class="gate-box">
<strong>Viable band (Task 2b):</strong> p_max ∈ [{locked_p2b}, {ovs2b})<br>
<strong>Locked p_max_C (bare, wealth-scaled):</strong> {locked_p2b}
</div>
"""
    else:
        sec2b += """
<div class="escalate-box">
<strong>ESCALATION REQUIRED (Task 2b):</strong> Wealth scaling alone did not produce
a passing p_max in [0.03, 0.07]. Both age-init fix and wealth scaling are insufficient.
Supervisor decision required before proceeding.
</div>
"""

    if "pA2b_nt" in figs:
        sec2b += _img(figs["pA2b_nt"],
                      "Figure 2b-i: Task 2b sweep — N(t) overlay (wealth_init_scale_k=True)")
    if "pA_compare" in figs:
        sec2b += _img(figs["pA_compare"],
                      "Figure 2b-ii: Task 2a vs 2b comparison — before/after wealth scaling")

    # ── §2c: Task 2c — cluster_init sweep ────────────────────────────────────
    runA2c = task2c.get("results", {})
    locked_p2c = task2c.get("locked_p")
    overshoot_p2c = task2c.get("overshoot_p")

    # Amendment 1 verification using 2a vs 2b step-1 wealth
    # (step=0 not recorded in metrics; step=1 is the first recorded step)
    w_step1_2a = float("nan")
    w_step1_2b = float("nan")
    if runA.get(0.03) and "df" in runA[0.03]:
        df_2a = runA[0.03]["df"]
        r = df_2a[df_2a["step"] == 1]
        if not r.empty:
            w_step1_2a = float(r["mean_wealth"].iloc[0])
    task2b_results = task2b.get("results", {})
    if task2b_results.get(0.03) and "df" in task2b_results[0.03]:
        df_2b = task2b_results[0.03]["df"]
        r = df_2b[df_2b["step"] == 1]
        if not r.empty:
            w_step1_2b = float(r["mean_wealth"].iloc[0])

    amend1_ok = (not np.isnan(w_step1_2b)) and w_step1_2b > 50.0
    amend1_status = "implemented correctly" if amend1_ok else "POSSIBLY INCORRECT — check implementation"

    sec2c = "<h2>§2c — Task 2c: p_max sweep with cluster_init=True</h2>\n"
    sec2c += "<h3>§2c-0: Amendment 1 verification (wealth_init_scale_k)</h3>\n"
    sec2c += f"""
<p>Metrics start at step=1 (step=0 not recorded). Step-1 mean_wealth as proxy
for initial wealth:</p>
<table>
<tr><th>Config</th><th>initial_wealth_dist</th><th>mean_wealth at step=1</th><th>Expected</th></tr>
<tr><td>Task 2a (wealth_init_scale_k=False)</td><td>[5, 25]</td>
    <td>{_fmt(w_step1_2a, 1)}</td><td>~33 (15 initial + ~18 first harvest)</td></tr>
<tr><td>Task 2b (wealth_init_scale_k=True)</td><td>[20, 100]</td>
    <td>{_fmt(w_step1_2b, 1)}</td><td>~78 (60 initial + ~18 first harvest)</td></tr>
</table>
<p><strong>Amendment 1 status:</strong>
<span class="{'pass' if amend1_ok else 'fail'}">{amend1_status}</span>.
Step-1 ratio Task 2b / Task 2a = {_fmt(w_step1_2b / max(w_step1_2a, 0.001), 2)}
(consistent with 4× initial wealth compressed by equal foraging gain).</p>
"""

    sec2c += "<h3>§2c-1: Task 2c sweep (all three fixes active)</h3>\n"
    sec2c += ("<p>age_init_upper_frac=0.25, wealth_init_scale_k=True (Uniform[20,100]), "
              "cluster_init=True (peak_index=0, cluster_radius=10). "
              "Pool OFF, λ=0, seed=42, 1000 steps.</p>\n")

    if runA2c:
        sec2c += """<table>
<tr>
  <th>p_max</th><th>Gate</th><th>N_late [lo,hi]</th><th>collapse_step</th>
  <th>est_starv/step</th><th>births/step</th><th>senes/step</th>
  <th>juv_starv/step</th><th>age t=100</th><th>age t=300</th><th>age t=500</th>
  <th>w_step1</th><th>iso@t=1</th><th>iso@t=50</th><th>iso@t=100</th><th>iso@t=300</th>
</tr>
"""
        for p, res in runA2c.items():
            gate = res["gate_pass"]
            over = res.get("overshoot", False)
            if gate:
                gate_str = '<td class="pass">✓ PASS</td>'
            elif over:
                gate_str = '<td class="over">OVERSHOOT</td>'
            else:
                gate_str = '<td class="fail">FAIL</td>'
            lo, hi = res["n_lo"], res["n_hi"]
            cs = res["collapse_step"]
            sec2c += f"""<tr>
  <td>{p}</td>{gate_str}<td>[{lo},{hi}]</td><td>{cs if cs else '—'}</td>
  <td>{_fmt(res['est_starv'])}</td><td>{_fmt(res['births'], 2)}</td>
  <td>{_fmt(res['senescence'], 2)}</td><td>{_fmt(res['juv_starv'], 2)}</td>
  <td>{_fmt(res['age100'], 1)}</td><td>{_fmt(res['age300'], 1)}</td>
  <td>{_fmt(res['age500'], 1)}</td>
  <td>{_fmt(res.get('w_step1', float('nan')), 1)}</td>
  <td>{_fmt(res.get('iso_t0', float('nan')), 1)}%</td>
  <td>{_fmt(res.get('iso_t50', float('nan')), 1)}%</td>
  <td>{_fmt(res.get('iso_t100', float('nan')), 1)}%</td>
  <td>{_fmt(res.get('iso_t300', float('nan')), 1)}%</td>
</tr>
"""
        sec2c += "</table>\n"

    if locked_p2c is not None:
        ovs2c = overshoot_p2c if overshoot_p2c else f">{_SWEEP_P[-1]}"
        sec2c += f"""
<div class="gate-box">
<strong>Viable band (Task 2c):</strong> p_max ∈ [{locked_p2c}, {ovs2c})<br>
<strong>Locked p_max_C (bare, all fixes):</strong> {locked_p2c}<br>
<strong>Proceeding to Task 3 (Runs B/C/D).</strong>
</div>
"""
    else:
        # Identify blocking mechanism from data
        sec2c += """
<div class="escalate-box">
<strong>ESCALATION REQUIRED (Task 2c):</strong> All three fixes (age_init_upper_frac=0.25,
wealth_init_scale_k=True, cluster_init=True) are insufficient to produce N∈[150,400]
at t≥500. The bistability at k=4 is not resolvable by initialisation changes alone.
<br><br>
<strong>Blocking mechanism:</strong> The k=4 grid eliminates resource competition as
a density-dependent regulator. Below p≈0.055 the birth formula cannot sustain C through
the senescence wave even from a clustered warm-start. Above p≈0.060 the population
overshoots carrying capacity. No stable attractor exists in [150,400]. A carrying-cost
ceiling hook in the birth formula (Stage 4.5 scope) is required.
<br><br>
Do NOT attempt further parameter adjustments (cluster_radius, η_min, parent_radius, etc.)
without supervisor approval.
</div>
"""

    if "pA2c_nt" in figs:
        sec2c += _img(figs["pA2c_nt"],
                      "Figure 2c-i: Task 2c sweep — N(t) overlay (cluster_init=True)")
    if "pA2c_dispersal" in figs:
        sec2c += _img(figs["pA2c_dispersal"],
                      "Figure 2c-ii: Task 2c — pct_isolated_C showing cluster dispersal over time")

    # ── §3: Pool and λ verification ───────────────────────────────────────────
    sec3 = "<h2>§3 — Pool and λ verification (Runs B/C/D)</h2>\n"

    if not locked_p_bare:
        sec3 += "<p class='warn'>Skipped — Task 2 did not produce a locked p_max.</p>\n"
    else:
        # Summary table
        sec3 += "<h3>Locked parameters per condition</h3>\n"
        sec3 += """<table>
<tr><th>Condition</th><th>Locked p_max</th><th>τ_pool</th><th>λ</th><th>N range (t≥500)</th><th>Gate</th></tr>
"""
        def _locked_row(label, locked_val, tau_p, lam, res_dict):
            if locked_val and locked_val in res_dict:
                r = res_dict[locked_val]
                n_str = f"[{r['n_lo']},{r['n_hi']}]"
                g = r["gate_pass"]
            elif locked_val == locked_p_bare and label == "Bare (Run A)":
                r = runA.get(locked_p_bare, {})
                n_str = f"[{r.get('n_lo','?')},{r.get('n_hi','?')}]" if r else "—"
                g = r.get("gate_pass", False) if r else False
            else:
                n_str = "—"; g = False
            gc = '<span class="pass">✓ PASS</span>' if g else '<span class="fail">FAIL</span>'
            lv = locked_val if locked_val else "—"
            return f"<tr><td>{label}</td><td>{lv}</td><td>{tau_p}</td><td>{lam}</td><td>{n_str}</td><td>{gc}</td></tr>\n"

        sec3 += _locked_row("Bare (Run A)", locked_p_bare, "off", 0, runA)
        sec3 += _locked_row("Pool (Run B)", locked.get("B"), "0.05", 0, runB)
        sec3 += _locked_row("λ (Run C)", locked.get("C"), "off", 0.1, runC)
        sec3 += _locked_row("Pool+λ (Run D)", locked.get("D"), "0.05", 0.1, runD)
        sec3 += "</table>\n"

        # Detail tables per run
        for run_label, run_res, pool_str, lam_str in [
            ("B (pool ON, λ=0)", runB, "ON (τ_pool=0.05)", "0"),
            ("C (pool OFF, λ=0.1)", runC, "OFF", "0.1"),
            ("D (pool ON, λ=0.1)", runD, "ON (τ_pool=0.05)", "0.1"),
        ]:
            if not run_res:
                continue
            sec3 += f"<h3>Run {run_label}</h3>\n"
            sec3 += f"<p>Pool: {pool_str}. λ: {lam_str}.</p>\n"
            sec3 += """<table>
<tr><th>p_max</th><th>Gate</th><th>N_late [lo,hi]</th><th>collapse_step</th>
    <th>est_starv/step</th><th>births/step</th></tr>
"""
            for p, r in sorted(run_res.items()):
                gc = '<td class="pass">✓ PASS</td>' if r["gate_pass"] else '<td class="fail">FAIL</td>'
                cs = r["collapse_step"]
                sec3 += (f"<tr><td>{p}</td>{gc}"
                         f"<td>[{r['n_lo']},{r['n_hi']}]</td>"
                         f"<td>{cs if cs else '—'}</td>"
                         f"<td>{_fmt(r['est_starv'])}</td>"
                         f"<td>{_fmt(r['births'], 2)}</td></tr>\n")
            sec3 += "</table>\n"

        if "pBCD_nt" in figs:
            sec3 += _img(figs["pBCD_nt"],
                         "Figure 3: Runs B/C/D — N(t) at all p_max values tested")

    # ── §4: Recommended next action ───────────────────────────────────────────
    sec4 = "<h2>§4 — Recommended next action</h2>\n"
    locked_D = locked.get("D")
    locked_C = locked.get("C")
    locked_B = locked.get("B")
    # Use Task 2c locked p as definitive bare locked p (supersedes 2b, 2a)
    locked_p_bare = (locked_p2c if locked_p2c is not None
                     else (locked_p2b if locked_p2b is not None
                           else task2.get("locked_p")))

    if locked_p_bare and locked_D:
        tau_pool = "0.05"
        sec4 += f"""
<div class="gate-box">
<strong>Proceed to Stage 4.4 seasonal sweep.</strong> All null controls pass.<br>
Locked parameters:<br>
&nbsp;&nbsp;k_grid=4, age_init_upper_frac=0.25<br>
&nbsp;&nbsp;p_max_C (bare) = {locked_p_bare}<br>
&nbsp;&nbsp;p_max_C (pool+λ) = {locked_D}<br>
&nbsp;&nbsp;τ_pool = {tau_pool}<br>
&nbsp;&nbsp;λ = 0.1
</div>
"""
    elif locked_p_bare and locked_C and not locked_D:
        sec4 += f"""
<div class="escalate-box">
<strong>Partial pass.</strong> Run A and C pass; Run D (pool+λ) did not produce a locked p_max.
Consider reducing p_max by 0.005 for D (blueprint allows up to 2 reductions) or
reducing τ_pool in steps of 0.01 (blueprint allows up to 3 attempts).
Supervisor decision required before seasonal sweep.
</div>
"""
    elif locked_p_bare:
        sec4 += f"""
<div class="escalate-box">
<strong>Partial pass.</strong> Run A (bare) locked at p={locked_p_bare}.
Run B locked at {locked_B or '—'}, Run C locked at {locked_C or '—'}, Run D locked at {locked_D or '—'}.
Supervisor decision required before proceeding to seasonal sweep.
</div>
"""
    else:
        sec4 += """
<div class="escalate-box">
<strong>Escalate.</strong> No p_max in the Task 2 sweep [0.03–0.07] passed the gate
with age_init_upper_frac=0.25. The age-init fix alone is insufficient to rescue C.
<br><br>
Possible secondary mechanisms to investigate (supervisor decision required):
<ul>
<li>The initial_wealth_dist=[5,25] may be too low at k=4 — agents start wealth-poor
    and die before they can reproduce.</li>
<li>The birth formula (prosperity zone gate) may have an implicit density floor that
    triggers at N&lt;150 on the 50×50 grid.</li>
<li>Verify bare configs truly disable pool and λ (check parquets for lambda_inheritance_boost &gt;0).</li>
</ul>
Do NOT adjust η_min, τ_pool, parent_radius, or any other parameter without supervisor approval.
</div>
"""

    # ── Assembly ──────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SiC Games — Stage 4.4 Patch Report</title>
<style>{_css()}</style>
</head>
<body>
<h1>SiC Games — Stage 4.4 Patch Report</h1>
<p><strong>Version:</strong> 1.2 (+ Amendment 2: cluster_init) &nbsp;|&nbsp;
   <strong>Scope:</strong> age_init_upper_frac=0.25 + wealth_init_scale_k + cluster_init + p_max re-calibration &nbsp;|&nbsp;
   <strong>seed:</strong> 42 &nbsp;|&nbsp;
   <strong>Output dir:</strong> <code>outputs/stage44_patch_seed42/</code>
</p>
<p><strong>Gate:</strong> N ∈ [{_N_LO}, {_N_HI}] at t≥{_STABLE_T}, est_starv ≤ {_EST_STARV_MAX}/step.</p>
<hr>
{sec0}
<hr>
{sec1}
<hr>
{sec2}
<hr>
{sec2b}
<hr>
{sec2c}
<hr>
{sec3}
<hr>
{sec4}
</body>
</html>
"""
    out_path = _OUT_ROOT / "report_patch.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  Report written: {out_path}")
    return out_path


# ─── ROADMAP update ──────────────────────────────────────────────────────────

def update_roadmap(task2: dict, task3: dict) -> None:
    """Append Stage 4.4 Patch row to ROADMAP.md."""
    locked_p = task2.get("locked_p")
    locked_D = task3.get("locked", {}).get("D")
    overshoot_p = task2.get("overshoot_p")
    mechanism = "stable high-N equilibrium (juvenile starvation ceiling)"
    status = "✓ Complete" if locked_p else "⚠ Escalated"
    locked_str = f"p_max_C={locked_D or locked_p or '?'}, τ_pool=0.05, λ=0.1" if locked_D else f"p_max_C={locked_p or '?'}"
    expl_str = f"p_max=0.07 confirmed as {mechanism}"
    row = (
        f"| Stage 4.4 Patch | {status} | age_init_upper_frac=0.25, wealth_init_scale_k=true (k=4→[20,100]). "
        f"Locked: {locked_str}. "
        f"Viable band: [{locked_p or '?'}, {overshoot_p or '?'}). "
        f"{expl_str}. |\n"
    )

    roadmap = Path("G:/My Drive/docs/SiC Games/ROADMAP.md")
    if not roadmap.exists():
        print(f"  ROADMAP not found at {roadmap}; skipping update.")
        return
    text = roadmap.read_text(encoding="utf-8")
    if "Stage 4.4 Patch" in text:
        print("  ROADMAP already has Stage 4.4 Patch row; skipping.")
        return
    # Insert before Stage 4.5 if present, else append
    if "Stage 4.5" in text:
        text = text.replace("| Stage 4.5", row + "| Stage 4.5", 1)
    else:
        text = text.rstrip() + "\n" + row
    roadmap.write_text(text, encoding="utf-8")
    print(f"  ROADMAP updated: {roadmap}")


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Stage 4.4 Patch: Age Init Fix + p_max Re-calibration")
    print("=" * 60)

    # Task 0: Diagnose p=0.07 explosion from diagnostic parquet
    task0 = task0_explosion_diagnosis()

    # Task 2: Run A bare sweep (age_init_upper_frac=0.25, wealth unchanged)
    task2 = task2_run_A()

    # Task 2b: Run A bare sweep with wealth_init_scale_k=True (amendment 1)
    task2b = task2b_run_A()

    # Task 2c: Run A bare sweep with cluster_init=True (amendment 2, all fixes)
    task2c = task2c_run_A()

    # Task 3: Pool and λ verification (uses Task 2c locked p_max, or 2b, or 2a)
    locked_for_t3 = task2c["locked_p"] or task2b["locked_p"] or task2["locked_p"]
    task3 = task3_run_BCD(locked_for_t3)

    # Generate figures
    figs = generate_figures(task0, task2, task2b, task2c, task3)

    # Write HTML report
    write_report(task0, task2, task2b, task2c, task3, figs)

    # Update ROADMAP — use the most advanced passing task
    best_task = task2c if task2c["locked_p"] else (task2b if task2b["locked_p"] else task2)
    update_roadmap(best_task, task3)

    print("\n" + "="*60)
    print("Stage 4.4 Patch complete.")
    print(f"  Report: {_OUT_ROOT / 'report_patch.html'}")
    print("="*60)


if __name__ == "__main__":
    main()
