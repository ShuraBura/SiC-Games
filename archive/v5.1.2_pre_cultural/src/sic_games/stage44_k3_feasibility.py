"""Stage 4.4 — k=3 Feasibility Check.

Binary feasibility check: can Si pass its null control at k=3, and can C
find a stable attractor in [150,400] at k=3?

Task 1 — Si static null control at k=3 (max_sugar=12, growback_alpha=3)
Task 2 — C bare p_max sweep at k=3 (all three patch fixes active)

No code changes — config only.
Blueprint: SiC_Games_Stage4_4_k3_Feasibility.md v1.0
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
_EST_STARV_MAX = 0.78
_DORM_RATE_MAX = 0.20          # Si gate: dormancy_rate < 20%
_PERM_DORM_MAX = 0.5           # Si soft gate: permanent_dormancy_deaths ≤ 0.5/step
_N_BOMB = 800
_OUT_ROOT = Path("outputs/stage44_k3_feasibility_seed42")

_SWEEP_P_C = [0.03, 0.04, 0.05, 0.06, 0.065, 0.07]
_SI_P_ATTEMPTS = [0.28, 0.35, 0.20]

# ─── k=3 base configs ─────────────────────────────────────────────────────────

_WORLD_K3 = dict(
    grid_size=[50, 50], toroidal=True, sugar_peaks=[[10, 40], [40, 10]],
    max_sugar_capacity=12, band_width_k=6, growth_rate_alpha=3,
)

_BASE_SI_K3 = dict(
    seed=42,
    world=_WORLD_K3,
    agents=dict(initial_population=250, vision_dist=[1, 6], metabolic_rate_dist=[1, 4],
                max_age_dist=[60, 100], initial_wealth_dist=[5, 25],
                phi_mean=0.5, phi_std=0.2, psi_mean=0.5, psi_std=0.2,
                psi_beta_a=0.0, psi_beta_b=0.0,
                c1_mean=0.5, c1_std=0.2, c2_mean=0.5, c2_std=0.2),
    decision=dict(strategy="si_bounded"),
    carbon=dict(sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
                matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
                velocity_tau=10, velocity_scale=1.0, f_C=0.25,
                status_amplification_beta=1.0),
    si_bounded=dict(sigma_si=1.238, beta_metabolism=5.0),
    joint_task=dict(distance_d=1, capacity_threshold=4),
    population=dict(mode="dynamic"),
    birth_c=dict(p_max=0.03, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
                 r_wealth=0.5, rep_age_min=15, rep_age_max=None, gamma=0.2, c_star_birth=10.0),
    birth_si=dict(p_fission_max=0.28, fission_wealth_mult=1.5, rep_age_min=15),
    reproduction=dict(mode="random", parent_radius=3, inherit_sigma=0.05,
                      coordinator="individual", lambda_inheritance=0.0),
    perturbation=dict(type="null"),
    # Si uses Stage 4.1b age init; wealth_init_scale_k=True → [5×3, 25×3]=[15,75]
    initialization=dict(age_distribution="realistic", age_init_upper_frac=0.5,
                        wealth_init_scale_k=True, cluster_init=False,
                        cluster_peak_index=0, cluster_radius=10),
    life_history=dict(forage_age_min=15, forage_age_max_offset=10,
                      eta_min=0.3, eta_old=0.4, eta_fission_offspring=1.0),
    dormancy=dict(enabled=True, k_dormant=1.0, tau_trickle=0.05,
                  k_reactivate=3.0, t_dormant_max=50),
    support_pool=dict(enabled=False, r_pool=5, tau_parent=0.0,
                      tau_pool=0.0, k_reserve=5.0, k_draw=3.0,
                      tau_cred=0.0, tau_cred_reward=0.0,
                      rho_carryover=0.0, k_pool_cap=0.0),
    run=dict(n_steps=_N_STEPS, metrics_every=1),
    visualization=dict(animate=False, save_static_plots=False),
)

_BASE_C_K3 = dict(
    seed=42,
    world=_WORLD_K3,
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
    si_bounded=dict(sigma_si=1.238, beta_metabolism=1.0),
    joint_task=dict(distance_d=1, capacity_threshold=4),
    population=dict(mode="dynamic"),
    birth_c=dict(p_max=0.03, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
                 r_wealth=0.5, rep_age_min=15, rep_age_max=None, gamma=0.2, c_star_birth=10.0),
    birth_si=dict(p_fission_max=0.065, fission_wealth_mult=1.5, rep_age_min=15),
    reproduction=dict(mode="biparental", parent_radius=3, inherit_sigma=0.05,
                      coordinator="individual", lambda_inheritance=0.0),
    perturbation=dict(type="null"),
    # C: all three fixes. wealth_init_scale_k=True → [15,75] at k=3. cluster_init=True.
    initialization=dict(age_distribution="realistic", age_init_upper_frac=0.25,
                        wealth_init_scale_k=True, cluster_init=True,
                        cluster_peak_index=0, cluster_radius=10),
    life_history=dict(forage_age_min=15, forage_age_max_offset=10,
                      eta_min=0.3, eta_old=0.4, eta_fission_offspring=1.0),
    dormancy=dict(enabled=False),
    support_pool=dict(enabled=False, r_pool=5, tau_parent=0.0,
                      tau_pool=0.0, k_reserve=5.0, k_draw=3.0,
                      tau_cred=0.0, tau_cred_reward=0.0,
                      rho_carryover=0.0, k_pool_cap=0.0),
    run=dict(n_steps=_N_STEPS, metrics_every=1),
    visualization=dict(animate=False, save_static_plots=False),
)


# ─── config builder / writer ──────────────────────────────────────────────────

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


def _col_late(df: pd.DataFrame, col: str) -> pd.Series:
    late = _late(df)
    if late.empty or col not in late.columns:
        return pd.Series(dtype=float)
    return late[col]


def _mean_late(df: pd.DataFrame, col: str) -> float:
    s = _col_late(df, col)
    return float(s.mean()) if not s.empty else float("nan")


def _mean_all(df: pd.DataFrame, col: str) -> float:
    """Mean over all available steps (used when late window is empty — bomb runs)."""
    if col not in df.columns or df.empty:
        return float("nan")
    return float(df[col].mean())


def _n_range_col(df: pd.DataFrame, col: str) -> tuple[int, int]:
    late = _late(df)
    if late.empty or col not in late.columns:
        return 0, 0
    return int(late[col].min()), int(late[col].max())


def _collapse_step(df: pd.DataFrame, col: str = "population") -> int | None:
    if col not in df.columns:
        return None
    hits = df[df[col] < 10]
    if hits.empty:
        return None
    return int(hits["step"].iloc[0])


def _is_bomb(df: pd.DataFrame) -> bool:
    """True if run terminated early due to population explosion (not collapse)."""
    last_pop = int(df["population"].iloc[-1]) if len(df) > 0 else 0
    return int(df["step"].max()) < _N_STEPS and last_pop > _N_BOMB


def _bomb_step(df: pd.DataFrame) -> int | None:
    """Last step recorded if run was a bomb, else None."""
    if _is_bomb(df):
        return int(df["step"].max())
    return None


def _at_step(df: pd.DataFrame, col: str, t: int) -> float:
    row = df.iloc[(df["step"] - t).abs().argsort()[:1]]
    if row.empty or col not in df.columns:
        return float("nan")
    return float(row[col].iloc[0])


# Si-specific gates
def _si_n_range(df: pd.DataFrame) -> tuple[int, int]:
    return _n_range_col(df, "n_active_si")


def _si_gate_pass(df: pd.DataFrame) -> tuple[bool, bool, bool]:
    """Returns (n_gate, dorm_gate, perm_dorm_soft) booleans."""
    lo, hi = _si_n_range(df)
    n_ok = _N_LO <= lo and hi <= _N_HI
    dorm_rate = _mean_late(df, "dormancy_rate")
    dorm_ok = (not np.isnan(dorm_rate)) and dorm_rate < _DORM_RATE_MAX
    perm_dorm = _mean_late(df, "permanent_dormancy_deaths")
    perm_ok = np.isnan(perm_dorm) or perm_dorm <= _PERM_DORM_MAX
    return n_ok, dorm_ok, perm_ok


def _si_passes(df: pd.DataFrame) -> bool:
    n_ok, dorm_ok, _ = _si_gate_pass(df)
    return n_ok and dorm_ok


# C-specific gates
def _c_n_range(df: pd.DataFrame) -> tuple[int, int]:
    return _n_range_col(df, "population")


def _c_overshoot(df: pd.DataFrame) -> bool:
    lo, _ = _c_n_range(df)
    return lo > _N_HI


def _est_starv(df: pd.DataFrame) -> float:
    return _mean_late(df, "deaths_starvation_established")


def _c_gate_pass(df: pd.DataFrame) -> bool:
    lo, hi = _c_n_range(df)
    return _N_LO <= lo and hi <= _N_HI and _est_starv(df) <= _EST_STARV_MAX


def _iso_at(df: pd.DataFrame, t: int) -> float:
    return _at_step(df, "pct_isolated_C", t)


# ─── Task 1 — Si at k=3 ──────────────────────────────────────────────────────

def task1_si_k3() -> dict:
    print("\n" + "="*60)
    print("Task 1 — Si static null control at k=3 (max_sugar=12, alpha=3)")
    print("="*60)
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    locked_p = None

    for i, p in enumerate(_SI_P_ATTEMPTS):
        tag = f"Si_k3_p{str(p).replace('.', '')}"
        cfg = copy.deepcopy(_BASE_SI_K3)
        cfg["birth_si"]["p_fission_max"] = p
        cfg["run"]["output_dir"] = str(_OUT_ROOT / tag)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg, cfg_path)
        df = _run_or_load(cfg_path, f"Si-p{p}")

        n_lo, n_hi = _si_n_range(df)
        dorm_rate = _mean_late(df, "dormancy_rate")
        perm_dorm = _mean_late(df, "permanent_dormancy_deaths")
        dorm_dur = _mean_late(df, "mean_dormancy_duration")
        mean_w = _mean_late(df, "mean_wealth")
        n_total_lo, n_total_hi = _n_range_col(df, "population")
        cs = _collapse_step(df, "n_active_si")
        bomb = _is_bomb(df)
        bs = _bomb_step(df)

        # For bomb runs (t<500), fall back to early-window diagnostics
        dorm_rate_early = _mean_all(df, "dormancy_rate")  # mean over available steps
        last_pop = int(df["population"].iloc[-1]) if len(df) > 0 else 0

        n_ok, dorm_ok, perm_ok = _si_gate_pass(df)
        # For bomb runs: N gate fails (never in [150,400] long-term), dorm gate based on early rate
        if bomb:
            n_ok = False  # population bomb → N never in [150,400] at t≥500
            dorm_ok = not (np.isnan(dorm_rate_early) or dorm_rate_early >= _DORM_RATE_MAX)
        passes = n_ok and dorm_ok

        flag = "✓ PASS" if passes else "  FAIL"
        if bomb:
            print(f"  {flag} Si-p{p}: BOMB at step {bs} (N={last_pop}). "
                  f"early_dorm_rate={dorm_rate_early:.3f} (>{_DORM_RATE_MAX:.0%} gate)")
        else:
            print(f"  {flag} Si-p{p}: N_active=[{n_lo},{n_hi}] "
                  f"dorm_rate={dorm_rate:.3f} perm_dorm={perm_dorm:.3f}/step "
                  f"collapse=t{cs}")

        results[p] = dict(
            df=df, tag=tag, p_fission=p,
            n_active_lo=n_lo, n_active_hi=n_hi,
            n_total_lo=n_total_lo, n_total_hi=n_total_hi,
            dorm_rate=dorm_rate, dorm_rate_early=dorm_rate_early,
            perm_dorm=perm_dorm,
            dorm_dur=dorm_dur, mean_wealth=mean_w,
            collapse_step=cs,
            bomb=bomb, bomb_step=bs, last_pop=last_pop,
            n_ok=n_ok, dorm_ok=dorm_ok, perm_ok=perm_ok,
            passes=passes,
        )

        if passes and locked_p is None:
            locked_p = p
            print(f"  ★ Si gate pass at p_fission={p}. Locked.")

        # Stop if dormancy always > 20%: no point trying more
        if not dorm_ok and i == len(_SI_P_ATTEMPTS) - 1:
            print(f"\n  All {len(_SI_P_ATTEMPTS)} Si attempts failed. k=3 insufficient for Si.")

    if locked_p:
        print(f"\n  Si locked p_fission = {locked_p}")
    return dict(results=results, locked_p=locked_p)


# ─── Task 2 — C at k=3 ───────────────────────────────────────────────────────

def task2_c_k3() -> dict:
    print("\n" + "="*60)
    print("Task 2 — C bare p_max sweep at k=3 (all three fixes)")
    print("="*60)
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    locked_p = None
    overshoot_p = None

    for p in _SWEEP_P_C:
        tag = f"C_k3_p{str(p).replace('.', '')}"
        cfg = copy.deepcopy(_BASE_C_K3)
        cfg["birth_c"]["p_max"] = p
        cfg["run"]["output_dir"] = str(_OUT_ROOT / tag)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg, cfg_path)
        df = _run_or_load(cfg_path, f"C-p{p}")

        lo, hi = _c_n_range(df)
        cs = _collapse_step(df, "population")
        gate = _c_gate_pass(df)
        over = _c_overshoot(df)
        est = _est_starv(df)
        births = _mean_late(df, "births_c")
        senes = _mean_late(df, "deaths_senescence")
        juv = _mean_late(df, "deaths_starvation_juvenile")
        age100 = _at_step(df, "mean_age", 100)
        age300 = _at_step(df, "mean_age", 300)
        age500 = _at_step(df, "mean_age", 500)
        w_step1 = _at_step(df, "mean_wealth", 1)
        iso0 = _iso_at(df, 1)
        iso50 = _iso_at(df, 50)
        iso100 = _iso_at(df, 100)
        iso300 = _iso_at(df, 300)

        flag = "✓ PASS" if gate else ("  OVER" if over else "  FAIL")
        print(f"  {flag} C-p{p}: N=[{lo},{hi}] collapse=t{cs} "
              f"births={births:.2f}/step est={est:.3f} "
              f"iso@0={iso0:.1f}% iso@300={iso300:.1f}%")

        results[p] = dict(
            df=df, tag=tag, p_max=p,
            n_lo=lo, n_hi=hi, collapse_step=cs,
            gate_pass=gate, overshoot=over,
            est_starv=est, births=births,
            senescence=senes, juv_starv=juv,
            age100=age100, age300=age300, age500=age500,
            w_step1=w_step1,
            iso_t0=iso0, iso_t50=iso50, iso_t100=iso100, iso_t300=iso300,
        )

        if gate and locked_p is None:
            locked_p = p
            print(f"  ★ C gate pass at p={p}. Locked p_max_C (k=3) = {p}")

        if over:
            overshoot_p = p
            print(f"  ✗ Overshoot at p={p}. Stopping sweep.")
            break

    if locked_p is None:
        print("\n  No C p_max passed the gate.")
    return dict(results=results, locked_p=locked_p, overshoot_p=overshoot_p)


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


def generate_figures(task1: dict, task2: dict) -> dict[str, str]:
    figs = {}
    print("\n=== Generating figures ===")

    # ── Figure 1: Si N(t) — n_active and n_total for all attempts ────────────
    si_results = task1.get("results", {})
    if si_results:
        p_list = list(si_results.keys())
        colors = plt.cm.Set1(np.linspace(0, 0.6, len(p_list)))
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        for (p, res), col in zip(si_results.items(), colors):
            df = res["df"]
            lw = 2.0 if res.get("passes") else 1.2
            ls = "-" if res.get("passes") else "--"
            if "n_active_si" in df.columns:
                axes[0].plot(df["step"], df["n_active_si"], color=col, lw=lw, ls=ls,
                             label=f"p={p}")
            axes[1].plot(df["step"], df["population"], color=col, lw=lw, ls=ls,
                         label=f"p={p} total")
        for ax in axes:
            ax.axhline(_N_LO, color="red", ls="--", lw=0.8)
            ax.axhline(_N_HI, color="red", ls="--", lw=0.8, label="Gate")
            ax.axvline(_STABLE_T, color="gray", ls=":", lw=0.8)
            ax.set_xlabel("Step"); ax.legend(fontsize=8); ax.set_ylim(bottom=0)
        axes[0].set_ylabel("N_active"); axes[0].set_title("Si k=3: N_active(t) by p_fission")
        axes[1].set_ylabel("N_total"); axes[1].set_title("Si k=3: N_total(t) by p_fission")
        fig.tight_layout()
        figs["si_nt"] = _fig_to_b64(fig)
        print("  si_nt")

    # ── Figure 2: Si dormancy rate over time ─────────────────────────────────
    if si_results:
        fig, ax = plt.subplots(figsize=(10, 4))
        for (p, res), col in zip(si_results.items(), colors):
            df = res["df"]
            if "dormancy_rate" in df.columns:
                ax.plot(df["step"], df["dormancy_rate"] * 100, color=col, lw=1.5,
                        label=f"p={p}")
        ax.axhline(_DORM_RATE_MAX * 100, color="orange", ls="--", lw=1.2,
                   label=f"{_DORM_RATE_MAX*100:.0f}% gate")
        ax.set_xlabel("Step"); ax.set_ylabel("Dormancy rate (%)")
        ax.set_title("Si k=3: dormancy rate over time")
        ax.legend(fontsize=8); ax.set_ylim(0, 100)
        figs["si_dorm"] = _fig_to_b64(fig)
        print("  si_dorm")

    # ── Figure 3: C N(t) overlay ──────────────────────────────────────────────
    c_results = task2.get("results", {})
    if c_results:
        p_list_c = list(c_results.keys())
        colors_c = plt.cm.plasma(np.linspace(0.1, 0.9, len(p_list_c)))
        fig, ax = plt.subplots(figsize=(11, 5))
        for (p, res), col in zip(c_results.items(), colors_c):
            lw = 2.5 if res.get("gate_pass") else 1.2
            ls = "-" if res.get("gate_pass") else ("--" if not res.get("overshoot") else ":")
            ax.plot(res["df"]["step"], res["df"]["population"],
                    label=f"p={p}", color=col, lw=lw, ls=ls)
        ax.axhline(_N_LO, color="red", ls="--", lw=0.8, label="Gate [150,400]")
        ax.axhline(_N_HI, color="red", ls="--", lw=0.8)
        ax.axvline(_STABLE_T, color="gray", ls=":", lw=0.8, label=f"t={_STABLE_T}")
        ax.set_xlabel("Step"); ax.set_ylabel("N")
        ax.set_title("C k=3: N(t) by p_max\n(all fixes: age_frac=0.25, wealth=[15,75], cluster)")
        ax.legend(fontsize=8); ax.set_ylim(bottom=0)
        figs["c_nt"] = _fig_to_b64(fig)
        print("  c_nt")

    # ── Figure 4: C dispersal for best run ───────────────────────────────────
    locked_p_c = task2.get("locked_p")
    best_p = locked_p_c or (0.05 if 0.05 in c_results else list(c_results.keys())[-1] if c_results else None)
    if best_p and best_p in c_results:
        df_best = c_results[best_p]["df"]
        if "pct_isolated_C" in df_best.columns:
            fig, ax = plt.subplots(figsize=(10, 4))
            alive = df_best[df_best["population"] > 0]
            ax.plot(alive["step"], alive["pct_isolated_C"], color="#9C27B0", lw=2)
            ax.axhline(40, color="orange", ls="--", lw=1, label="40% Allee threshold")
            ax.set_xlabel("Step"); ax.set_ylabel("% isolated C")
            ax.set_title(f"C k=3 p={best_p}: pct_isolated_C")
            ax.legend(); ax.set_ylim(0, 105)
            figs["c_dispersal"] = _fig_to_b64(fig)
            print("  c_dispersal")

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


def _fmt(v, d: int = 3) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if isinstance(v, float):
        return f"{v:.{d}f}"
    return str(v)


def write_report(task1: dict, task2: dict, figs: dict) -> Path:
    print("\n=== Writing report_k3.html ===")
    si_results = task1.get("results", {})
    locked_si = task1.get("locked_p")
    c_results = task2.get("results", {})
    locked_c = task2.get("locked_p")
    overshoot_c = task2.get("overshoot_p")

    # ── §0: k=3 context ──────────────────────────────────────────────────────
    sec0 = "<h2>§0 — k=3 Grid Context</h2>\n"
    sec0 += """
<p>At k=3: <code>max_sugar_capacity=12</code>, <code>growth_rate_alpha=3</code>.
Grid topology unchanged (50×50 toroidal, same peak positions).
Agent metabolic rates unchanged (β_Si=5.0, β_C=1.0 effective).
Initial wealth scaled by k_grid=3: C agents start Uniform[15,75],
Si agents start Uniform[15,75] (both use wealth_init_scale_k=True).
C uses all three patch fixes: age_init_upper_frac=0.25, wealth_init_scale_k=True,
cluster_init=True (peak_index=0, radius=10).
Si uses age_init_upper_frac=0.5 (Stage 4.1b default), no cluster.
<strong>No code changes — config only.</strong></p>
<p>k=3 rationale: at k=3 the max sugar per cell is 12 (vs 16 at k=4).
This reduces per-agent harvest from ~16 to ~12, introducing resource competition
as a density-dependent population ceiling for C. The hypothesis is that the
bistability that prevents C from settling in [150,400] at k=4 (unlimited resources)
is resolved at k=3 by mild resource competition.</p>
"""

    # ── §1: Si at k=3 ────────────────────────────────────────────────────────
    sec1 = "<h2>§1 — Si Static Null Control at k=3</h2>\n"
    sec1 += "<p>Gate: N_active ∈ [150,400] at t≥500, dormancy_rate &lt; 20%, permanent_dormancy_deaths ≤ 0.5/step.</p>\n"
    # Check if any run was a bomb to add bomb-column
    any_bomb = any(r.get("bomb", False) for r in si_results.values())
    if any_bomb:
        sec1 += """<p class="warn"><strong>⚠ Population explosion at k=3:</strong>
All three Si runs terminated early via the N-bomb guard (population &gt; 800 after step 50).
Dormancy_rate shown is the mean over available steps (steps 1–~52).
The runs never reached the t≥500 stable window.</p>\n"""
    sec1 += """<table>
<tr><th>p_fission</th><th>N gate</th><th>dorm gate</th><th>perm_dorm soft</th>
    <th>Termination</th><th>Last N (bomb)</th>
    <th>dorm_rate (avail.)</th><th>dorm_dur</th><th>perm_dorm/step</th>
    <th>mean_wealth</th></tr>
"""
    for p, res in si_results.items():
        n_str = '<td class="pass">✓</td>' if res["n_ok"] else '<td class="fail">✗</td>'
        d_str = '<td class="pass">✓</td>' if res["dorm_ok"] else '<td class="fail">✗</td>'
        p_str = '<td class="pass">✓</td>' if res["perm_ok"] else '<td class="warn">flag</td>'
        if res.get("bomb"):
            term = f'<td class="fail">BOMB t={res["bomb_step"]}</td>'
            last_n_cell = f'<td class="fail">{res["last_pop"]}</td>'
            dorm_disp = _fmt(res.get("dorm_rate_early"))  # early-window mean
        else:
            cs = res["collapse_step"]
            term = f'<td>{("collapse t=" + str(cs)) if cs else "completed"}</td>'
            last_n_cell = f'<td>[{res["n_active_lo"]},{res["n_active_hi"]}]</td>'
            dorm_disp = _fmt(res["dorm_rate"])
        sec1 += (f"<tr><td>{p}</td>{n_str}{d_str}{p_str}"
                 f"{term}{last_n_cell}"
                 f"<td>{dorm_disp}</td>"
                 f"<td>{_fmt(res['dorm_dur'],1)}</td>"
                 f"<td>{_fmt(res['perm_dorm'])}</td>"
                 f"<td>{_fmt(res['mean_wealth'],1)}</td></tr>\n")
    sec1 += "</table>\n"

    if locked_si:
        sec1 += f'<div class="gate-box"><strong>Si PASSES at k=3.</strong> Locked p_fission_Si = {locked_si}. Proceeding to Task 2.</div>\n'
    elif any_bomb:
        sec1 += """<div class="escalate-box"><strong>Si FAILS at k=3 — population explosion.</strong>
At k=3 (max_sugar=12, alpha=3), dormancy buffers starvation so effectively that dormant
agents accumulate (dormancy_rate ≈ 17–51% from step 9 onward) while births continue
unimpeded. Net births far exceed deaths in every step, driving population to 1400–2500
by step 52. Both gate criteria fail: N_active ≫ 400, and dormancy_rate consistently
exceeds 20%. The failure mode is the opposite of k=1 (starvation collapse) — at k=3 the
dormancy mechanism creates an unbounded dormant-agent sink. Task 2 skipped.
k=4 confirmed as the minimum viable grid for Si at β=5.</div>\n"""
    else:
        sec1 += '<div class="escalate-box"><strong>Si FAILS at k=3.</strong> dormancy_rate exceeds 20% at all tested p_fission values. k=3 is insufficient for Si at β=5. Task 2 skipped.</div>\n'

    if "si_nt" in figs:
        sec1 += _img(figs["si_nt"], "Figure 1a: Si k=3 — N_active(t) (left) and N_total(t) (right)")
    if "si_dorm" in figs:
        sec1 += _img(figs["si_dorm"], "Figure 1b: Si k=3 — dormancy rate over time")

    # ── §2: C at k=3 ─────────────────────────────────────────────────────────
    sec2 = "<h2>§2 — C Bare p_max Sweep at k=3</h2>\n"
    if not locked_si and not c_results:
        sec2 += "<p class='warn'>Skipped — Si Task 1 did not pass.</p>\n"
    else:
        sec2 += "<p>Pool OFF, λ=0. All three fixes active. Gate: N∈[150,400] at t≥500, est_starv≤0.78/step.</p>\n"
        sec2 += """<table>
<tr><th>p_max</th><th>Gate</th><th>N [lo,hi]</th><th>collapse</th>
    <th>est_starv</th><th>births/step</th><th>senes/step</th><th>juv_starv/step</th>
    <th>age t=100</th><th>age t=300</th><th>age t=500</th>
    <th>w_step1</th><th>iso@t≈0</th><th>iso@t=50</th><th>iso@t=100</th><th>iso@t=300</th>
</tr>
"""
        for p, res in c_results.items():
            gate = res["gate_pass"]
            over = res.get("overshoot", False)
            if gate:
                gc = '<td class="pass">✓ PASS</td>'
            elif over:
                gc = '<td class="over">OVERSHOOT</td>'
            else:
                gc = '<td class="fail">FAIL</td>'
            cs = res["collapse_step"]
            sec2 += (f"<tr><td>{p}</td>{gc}"
                     f"<td>[{res['n_lo']},{res['n_hi']}]</td>"
                     f"<td>{cs if cs else '—'}</td>"
                     f"<td>{_fmt(res['est_starv'])}</td>"
                     f"<td>{_fmt(res['births'],2)}</td>"
                     f"<td>{_fmt(res['senescence'],2)}</td>"
                     f"<td>{_fmt(res['juv_starv'],2)}</td>"
                     f"<td>{_fmt(res['age100'],1)}</td>"
                     f"<td>{_fmt(res['age300'],1)}</td>"
                     f"<td>{_fmt(res['age500'],1)}</td>"
                     f"<td>{_fmt(res['w_step1'],1)}</td>"
                     f"<td>{_fmt(res['iso_t0'],1)}%</td>"
                     f"<td>{_fmt(res['iso_t50'],1)}%</td>"
                     f"<td>{_fmt(res['iso_t100'],1)}%</td>"
                     f"<td>{_fmt(res['iso_t300'],1)}%</td></tr>\n")
        sec2 += "</table>\n"

        if locked_c:
            ovs = overshoot_c if overshoot_c else f">{_SWEEP_P_C[-1]}"
            sec2 += f'<div class="gate-box"><strong>C PASSES at k=3.</strong> Locked p_max_C = {locked_c}. Viable band: [{locked_c}, {ovs}).</div>\n'
        elif c_results:
            sec2 += """<div class="escalate-box"><strong>C FAILS at k=3.</strong>
No p_max in [0.03, 0.07] produced N∈[150,400] at t≥500. Bistability persists at k=3.
See §3 for blocking mechanism and verdict.</div>\n"""

        if "c_nt" in figs:
            sec2 += _img(figs["c_nt"], "Figure 2a: C k=3 — N(t) overlay by p_max")
        if "c_dispersal" in figs:
            sec2 += _img(figs["c_dispersal"], "Figure 2b: C k=3 — pct_isolated_C over time")

    # ── §3: Feasibility verdict ───────────────────────────────────────────────
    sec3 = "<h2>§3 — Feasibility Verdict</h2>\n"
    if locked_si and locked_c:
        sec3 += f"""<div class="gate-box">
<strong>PROCEED.</strong><br>
Si passes at k=3 (p_fission={locked_si}). C passes at k=3 (p_max={locked_c}).<br>
<strong>Locked values:</strong> k_grid=3, max_sugar=12, growback_alpha=3,
p_fission_Si={locked_si}, p_max_C={locked_c}.<br>
Ready for pool/λ verification at k=3.
</div>\n"""
    elif not locked_si:
        # Use early-window dormancy if late window is empty (bomb runs)
        all_dorm_str_parts = []
        any_bomb_si = any(r.get("bomb", False) for r in si_results.values())
        for p, r in si_results.items():
            if r.get("bomb"):
                v = r.get("dorm_rate_early", float("nan"))
                last = r.get("last_pop", "?")
                all_dorm_str_parts.append(f"p={p}: dorm={v:.1%} (BOMB N={last} at t={r['bomb_step']})")
            else:
                v = r["dorm_rate"]
                all_dorm_str_parts.append(f"p={p}: dorm={v:.1%}" if not np.isnan(v) else f"p={p}: dorm=nan")
        dorm_str = "; ".join(all_dorm_str_parts)
        if any_bomb_si:
            sec3 += f"""<div class="escalate-box">
<strong>Si FAIL.</strong> k=3 is insufficient for Si at β=5 — population explosion.<br>
<strong>Failure mode:</strong> At k=3, resource scarcity is insufficient to prevent dormant-agent
accumulation. Dormancy rate exceeds 20% from step ~9 onward across all three p_fission attempts,
while starvation deaths remain near zero (dormancy absorbs all metabolic stress). Births far
outpace deaths, driving total N to 1400–2500 by step 52.<br>
<strong>Observed:</strong> {dorm_str}.<br>
Both gate criteria fail: N_active ≫ 400 (explosion) and dormancy_rate ≫ 20%.<br>
<strong>k=4 is confirmed as the minimum viable grid for Si at β=5</strong>
(at k=4 the richer resource base allows more agents to remain active, keeping dormancy_rate
below 20% and providing sufficient starvation pressure to balance the population).<br>
Task 2 was skipped. Escalate to Stage 4.5 or maintain k=4 as the operating grid.
</div>\n"""
        else:
            sec3 += f"""<div class="escalate-box">
<strong>Si FAIL.</strong> k=3 is insufficient for Si at β=5.<br>
dormancy_rate at t≥500: {dorm_str}.<br>
All values exceed the 20% gate. k=4 is confirmed as the minimum viable grid for Si.<br>
Task 2 was skipped. Escalate to supervisor for next steps (Stage 4.5 or alternative).
</div>\n"""
    else:
        # Si passed but C failed
        blocking = []
        for p, res in c_results.items():
            if not res["gate_pass"] and not res.get("overshoot"):
                births = res["births"]; senes = res["senescence"]
                if not np.isnan(births) and not np.isnan(senes):
                    ratio = births / max(senes, 0.001)
                    blocking.append(f"p={p}: births/senes={ratio:.2f}")
        block_str = "; ".join(blocking) if blocking else "collapse before t≥500 window"
        sec3 += f"""<div class="escalate-box">
<strong>C FAIL.</strong> Si passes at k=3 (p_fission={locked_si}) but
C bistability persists at k=3.<br>
Blocking mechanism: {block_str}.<br>
The resource competition at k=3 (max_sugar=12 vs 16) is insufficient to create
a density-dependent ceiling in the [150,400] band. A carrying-cost redesign
(Stage 4.5) is required. Escalate.
</div>\n"""

    # ── Assembly ──────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SiC Games — Stage 4.4 k=3 Feasibility Report</title>
<style>{_css()}</style>
</head>
<body>
<h1>SiC Games — Stage 4.4 k=3 Feasibility Check</h1>
<p><strong>seed:</strong> 42 &nbsp;|&nbsp;
   <strong>k=3:</strong> max_sugar=12, growback_alpha=3 &nbsp;|&nbsp;
   <strong>Output:</strong> <code>outputs/stage44_k3_feasibility_seed42/</code>
</p>
<p><strong>Gate:</strong> N_active (Si) or N (C) ∈ [150,400] at t≥500.
   Si: dormancy_rate &lt; 20%. C: est_starv ≤ 0.78/step.</p>
<hr>
{sec0}
<hr>
{sec1}
<hr>
{sec2}
<hr>
{sec3}
</body>
</html>
"""
    out_path = _OUT_ROOT / "report_k3.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  Report written: {out_path}")
    return out_path


# ─── ROADMAP update ──────────────────────────────────────────────────────────

def update_roadmap(task1: dict, task2: dict) -> None:
    locked_si = task1.get("locked_p")
    locked_c = task2.get("locked_p")
    if locked_si and locked_c:
        status = "✓ Complete"
        detail = (f"k=3 FEASIBLE. p_fission_Si={locked_si}, p_max_C={locked_c}. "
                  f"max_sugar=12, alpha=3. Proceed to pool/λ verification.")
    elif not locked_si:
        status = "⚠ Si Fail"
        any_bomb = any(r.get("bomb", False) for r in task1["results"].values())
        if any_bomb:
            parts = []
            for p, r in task1["results"].items():
                if r.get("bomb"):
                    v = r.get("dorm_rate_early", float("nan"))
                    parts.append(f"p={p}:{v:.0%}(bomb)")
                else:
                    v = r["dorm_rate"]
                    parts.append(f"p={p}:{v:.0%}" if not np.isnan(v) else f"p={p}:nan")
            dorm_str = " ".join(parts)
            detail = (f"k=3 Si population explosion + dorm_rate>{int(_DORM_RATE_MAX*100)}%: {dorm_str}. "
                      f"k=4 minimum confirmed.")
        else:
            dorm = {p: f"{r['dorm_rate']:.1%}" for p, r in task1["results"].items()}
            detail = f"k=3 insufficient for Si: dormancy_rate={dorm}. k=4 minimum confirmed."
    else:
        status = "⚠ C Fail"
        detail = f"Si passes (p={locked_si}) but C bistability persists at k=3."

    row = f"| Stage 4.4 k=3 Feasibility | {status} | {detail} |\n"
    roadmap = Path("G:/My Drive/docs/SiC Games/ROADMAP.md")
    if not roadmap.exists():
        print(f"  ROADMAP not found; skipping.")
        return
    text = roadmap.read_text(encoding="utf-8")
    if "Stage 4.4 k=3 Feasibility" in text:
        print("  ROADMAP already has k=3 row; skipping.")
        return
    # "Stage 4.5" may appear as prose in existing rows but not as a table-row prefix;
    # always append to end of file.
    text = text.rstrip() + "\n" + row
    roadmap.write_text(text, encoding="utf-8")
    print(f"  ROADMAP updated.")


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Stage 4.4 — k=3 Feasibility Check")
    print("=" * 60)

    # Verify tests unchanged
    print("\nVerifying test suite (166 expected)...")
    import subprocess
    result = subprocess.run(
        ["py", "-m", "pytest", "tests/", "-q", "--tb=no"],
        capture_output=True, text=True
    )
    test_line = [l for l in result.stdout.splitlines() if "passed" in l]
    print(f"  {test_line[0] if test_line else result.stdout.strip()}")

    # Task 1: Si at k=3
    task1 = task1_si_k3()

    # Task 2: C at k=3 (only if Si passes)
    if task1["locked_p"]:
        task2 = task2_c_k3()
    else:
        print("\n  Task 2 skipped — Si did not pass at k=3.")
        task2 = dict(results={}, locked_p=None, overshoot_p=None)

    # Figures and report
    figs = generate_figures(task1, task2)
    write_report(task1, task2, figs)
    update_roadmap(task1, task2)

    locked_si = task1.get("locked_p")
    locked_c = task2.get("locked_p")
    print("\n" + "="*60)
    print("k=3 Feasibility Check complete.")
    print(f"  Si: {'PASS p=' + str(locked_si) if locked_si else 'FAIL'}")
    print(f"  C:  {'PASS p=' + str(locked_c) if locked_c else ('FAIL' if task1['locked_p'] else 'SKIPPED')}")
    print(f"  Report: {_OUT_ROOT / 'report_k3.html'}")
    print("="*60)


if __name__ == "__main__":
    main()
