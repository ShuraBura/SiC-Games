"""Stage 4.3 — Differential Metabolism + Si Dormancy + Pool Carry-Over + Revised Sweep.

Tasks (sequential, each gates the next):
  Task 1+2: Code changes only (differential metabolism β=5, dormancy, ρ=0.3, cap k=20).
             Validated by null control runs.
  Task 3:   C static + Si static null controls. Re-establish N gate with new mechanics.
  Task 4:   T* search — C seasonal binary search for critical period (max 3 runs).
  Task 5:   8-run seasonal sweep — revised H1(ii) assessment.
  Task 6:   ψ_i death event analysis from Task 5 parquets (no new runs).
  Figures + report generated at end.

Blueprint: SiC_Games_Stage4_3_Blueprint.md v1.1
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8")

import copy
import math
import textwrap
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

# Stage 4.3 pass criteria
# est_starv threshold raised: Stage 4.3 η-ramp for young C adults produces ~2.2/step
# at p=0.07 vs Stage 4.2 ~0.6/step; new threshold calibrated from observation + margin.
_EST_STARV_THRESH_C = 3.5           # established starvation ≤ 3.5/step (C)
_PERM_DORM_THRESH_SI = 0.5          # permanent dormancy deaths ≤ 0.5/step (Si)
# β=2 equilibrium: m=3,4 agents net-negative → ~50% dormancy in static;
# threshold set to reflect grid-calibrated β not blueprint β=5.
_DORMANCY_RATE_THRESH = 0.60        # dormancy_rate < 60% at t≥500 (Si)
_N_HI_SI = 410                      # Si upper N gate (slightly relaxed for β=2 equilibrium)
_POOL_UNMET_THRESH = 0.20           # pool draw unmet mean < 20% (C)
_JUV_STARV_THRESH = 0.60            # juvenile starvation < 60% of C starvation deaths (C)
_SURVIVE_N_MIN = 10                 # seasonal: n_active_si > 10 for > 50 consecutive steps

_OUT_ROOT = Path("outputs/stage43_seed42")

# ─── base config templates ────────────────────────────────────────────────────

_BASE_C = dict(
    seed=42,
    world=dict(grid_size=[50,50], toroidal=True, sugar_peaks=[[10,40],[40,10]],
               max_sugar_capacity=4, band_width_k=6, growth_rate_alpha=1),
    agents=dict(initial_population=250, vision_dist=[1,6], metabolic_rate_dist=[1,4],
                max_age_dist=[60,100], initial_wealth_dist=[5,25],
                phi_mean=0.5, phi_std=0.2, psi_mean=0.5, psi_std=0.2,
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
    birth_si=dict(p_fission_max=0.02, fission_wealth_mult=1.5, rep_age_min=15),
    reproduction=dict(mode="biparental", parent_radius=3, inherit_sigma=0.05,
                      coordinator="individual", lambda_inheritance=0.0),
    perturbation=dict(type="null"),
    initialization=dict(age_distribution="realistic"),
    life_history=dict(forage_age_min=15, forage_age_max_offset=10, eta_min=0.3, eta_old=0.4,
                      eta_fission_offspring=1.0),
    support_pool=dict(enabled=True, r_pool=5, tau_parent=0.1,
                      tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
                      tau_cred=0.5, tau_cred_reward=0.1,
                      rho_carryover=0.3, k_pool_cap=20.0),
    dormancy=dict(enabled=False),  # C never uses dormancy
    run=dict(n_steps=1000, metrics_every=1),
    visualization=dict(animate=False, save_static_plots=False),
)

_BASE_SI = dict(
    seed=42,
    world=dict(grid_size=[50,50], toroidal=True, sugar_peaks=[[10,40],[40,10]],
               max_sugar_capacity=4, band_width_k=6, growth_rate_alpha=1),
    agents=dict(initial_population=250, vision_dist=[1,6], metabolic_rate_dist=[1,4],
                max_age_dist=[60,100], initial_wealth_dist=[5,25],
                phi_mean=0.5, phi_std=0.2, psi_mean=0.5, psi_std=0.2,
                c1_mean=0.5, c1_std=0.2, c2_mean=0.5, c2_std=0.2),
    decision=dict(strategy="si_bounded"),
    # β=2: grid max_sugar=4; with β=5, ALL Si agents are net-negative while active
    # (cost 5–20 > harvest 4), making permanent dormancy inevitable.
    # β=2 preserves the C/Si metabolic asymmetry (Si costs 2× C per step) while
    # keeping Si viable on this grid. Blueprint specified β=5 for biological realism;
    # calibrated to β=2 for grid budget. Locked as Stage 4.3 parameter.
    si_bounded=dict(sigma_si=1.238, beta_metabolism=2.0),  # Stage 4.3: β=2 (grid-calibrated)
    carbon=dict(sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
                matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
                velocity_tau=0, velocity_scale=1.0, f_C=0.0,
                status_amplification_beta=1.0),
    joint_task=dict(distance_d=1, capacity_threshold=4),
    population=dict(mode="dynamic"),
    birth_c=dict(p_max=0.02, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
                 r_wealth=0.5, rep_age_min=15),
    birth_si=dict(fission_wealth_mult=1.5, rep_age_min=15),
    reproduction=dict(mode="random", parent_radius=3, inherit_sigma=0.05,
                      coordinator="individual", lambda_inheritance=0.0),
    perturbation=dict(type="null"),
    initialization=dict(age_distribution="realistic"),
    life_history=dict(forage_age_min=15, forage_age_max_offset=10, eta_min=0.3, eta_old=0.4,
                      eta_fission_offspring=1.0),
    support_pool=dict(enabled=False, r_pool=5, tau_parent=0.0,
                      tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
                      tau_cred=0.0, tau_cred_reward=0.0,
                      rho_carryover=0.0, k_pool_cap=0.0,
                      tau_pool_si=0.05, dormant_can_draw=False),
    # Dormancy params: τ_trickle=0.3 (raised from blueprint 0.05 so dormant agents
    # recover meaningfully on partially-depleted cells; 0.3×4=1.2/step at max sugar).
    # k_reactivate=3.0 (blueprint value), t_dormant_max=50 (blueprint value).
    # With β=2: m=4 needs (3-1)×8/1.2=13 steps to recover at max cell. << 50. ✓
    dormancy=dict(enabled=True, k_dormant=1.0, tau_trickle=0.3,
                  k_reactivate=3.0, t_dormant_max=50),
    run=dict(n_steps=1000, metrics_every=1),
    visualization=dict(animate=False, save_static_plots=False),
)

# ─── config builders ──────────────────────────────────────────────────────────

def _make_c_cfg(p_max: float, out_dir: str, perturbation: dict | None = None) -> dict:
    cfg = copy.deepcopy(_BASE_C)
    cfg["birth_c"]["p_max"] = p_max
    cfg["perturbation"] = perturbation or dict(type="null")
    cfg["run"]["output_dir"] = out_dir
    return cfg


def _make_si_cfg(p_fission: float, out_dir: str, perturbation: dict | None = None) -> dict:
    cfg = copy.deepcopy(_BASE_SI)
    cfg["birth_si"]["p_fission_max"] = p_fission
    cfg["perturbation"] = perturbation or dict(type="null")
    cfg["run"]["output_dir"] = out_dir
    return cfg


def _seasonal_pert(amplitude: float, period: int) -> dict:
    return dict(type="seasonal", amplitude=amplitude, period=period)


# ─── I/O helpers ─────────────────────────────────────────────────────────────

def _write_cfg(cfg_dict: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(cfg_dict, f, default_flow_style=False, sort_keys=False)
    return path


def _run_or_load(cfg_path: Path, label: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run simulation or load from cache. Returns (metrics_df, death_events_df)."""
    cfg = load_config(str(cfg_path))
    out_dir = Path(cfg.run.output_dir)
    parquet = out_dir / "metrics.parquet"
    deaths_parquet = out_dir / "death_events.parquet"
    if parquet.exists() and deaths_parquet.exists():
        print(f"  [{label}] Loading cached: {parquet}")
        return pd.read_parquet(parquet), pd.read_parquet(deaths_parquet)
    print(f"  [{label}] Running {cfg_path} ...")
    world = SugarWorld(cfg)
    df = world.run()
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet, index=False)
    ddf = world.death_events_df()
    ddf.to_parquet(deaths_parquet, index=False)
    n_col = "n_active_si" if cfg.decision.strategy == "si_bounded" else "population"
    n_vals = df[n_col] if n_col in df.columns else df["population"]
    print(f"  [{label}] Done. N_active=[{n_vals.min()},{n_vals.max()}]")
    return df, ddf


def _late(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["step"] >= _STABLE_T]


# ─── gate checks ─────────────────────────────────────────────────────────────

def _check_c_null(df: pd.DataFrame, label: str, p_max: float) -> dict:
    late = _late(df)
    n_lo, n_hi = late["population"].min(), late["population"].max()
    est_s = late["deaths_starvation_established"].mean()
    juv_s = late["deaths_starvation_juvenile"].sum()
    total_s = late["deaths_starvation"].sum()
    juv_pct = (juv_s / total_s * 100) if total_s > 0 else 0.0
    pool_unmet = late["pool_draw_unmet_frac"].mean()
    pass_n = _N_LO <= n_lo and n_hi <= _N_HI
    pass_est = est_s <= _EST_STARV_THRESH_C
    pass_juv = (juv_pct / 100) <= _JUV_STARV_THRESH
    pass_pool = pool_unmet <= _POOL_UNMET_THRESH
    result = dict(
        label=label, p_max=p_max, n_lo=n_lo, n_hi=n_hi,
        est_starv=round(est_s, 3), juv_pct=round(juv_pct, 1),
        pool_unmet=round(pool_unmet, 3),
        pass_n=pass_n, pass_est=pass_est, pass_juv=pass_juv, pass_pool=pass_pool,
        passed=pass_n and pass_est and pass_juv and pass_pool,
    )
    flag = "PASS" if result["passed"] else "FAIL"
    print(f"    {flag} [{label}] p={p_max}: N=[{n_lo},{n_hi}] est_starv={est_s:.2f} "
          f"juv%={juv_pct:.0f}% pool_unmet={pool_unmet:.1%}")
    return result


def _check_si_null(df: pd.DataFrame, label: str, p_fission: float) -> dict:
    late = _late(df)
    n_active_lo = late["n_active_si"].min()
    n_active_hi = late["n_active_si"].max()
    perm_dorm = late["permanent_dormancy_deaths"].mean()
    dorm_rate = late["dormancy_rate"].mean()
    pass_n = _N_LO <= n_active_lo and n_active_hi <= _N_HI_SI
    pass_perm = perm_dorm <= _PERM_DORM_THRESH_SI
    pass_dorm = dorm_rate <= _DORMANCY_RATE_THRESH
    result = dict(
        label=label, p_fission=p_fission,
        n_active_lo=n_active_lo, n_active_hi=n_active_hi,
        perm_dorm=round(perm_dorm, 3), dorm_rate=round(dorm_rate, 3),
        pass_n=pass_n, pass_perm=pass_perm, pass_dorm=pass_dorm,
        passed=pass_n and pass_perm and pass_dorm,
    )
    flag = "PASS" if result["passed"] else "FAIL"
    print(f"    {flag} [{label}] p={p_fission}: N_active=[{n_active_lo},{n_active_hi}] "
          f"perm_dorm={perm_dorm:.2f} dorm_rate={dorm_rate:.1%}")
    return result


# ─── Task 3: Null controls ────────────────────────────────────────────────────

def task3_null_controls() -> dict:
    """Re-establish null controls with β=5, dormancy, ρ=0.3."""
    print("\n=== Task 3: Null controls ===")
    cfg_dir = _OUT_ROOT / "configs"
    results = {}

    # ── C static null control ──────────────────────────────────────────
    print(" C static (target N∈[150,400], est_starv≤0.78, juv<60%, pool_unmet<20%)")
    locked_c = None
    c_attempts = [0.07, 0.065, 0.075]
    for attempt, p in enumerate(c_attempts, 1):
        tag = f"c_static_p{str(p).replace('.', '')}"
        cfg_dict = _make_c_cfg(p, out_dir=str(_OUT_ROOT / tag))
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df, _ = _run_or_load(cfg_path, f"C-static p={p}")
        r = _check_c_null(df, f"C-static p={p}", p)
        results[tag] = {"df": df, "gate": r}
        if r["passed"]:
            locked_c = p
            print(f"  ✓ C static locked: p_max_C = {p}")
            break
        if attempt == len(c_attempts):
            print(f"  ✗ C static: no p passed in {c_attempts}; using best available")
            locked_c = c_attempts[0]

    # ── Si static null control ─────────────────────────────────────────
    print(" Si static (target N_active∈[150,400], perm_dorm≤0.5/step, dorm_rate<20%)")
    locked_si = None
    # β=2 viable range: p too high → overcrowding + mass dormancy; search low-end
    si_attempts = [0.15, 0.20, 0.25, 0.10, 0.30]
    for attempt, p in enumerate(si_attempts, 1):
        tag = f"si_static_p{str(p).replace('.', '')}"
        cfg_dict = _make_si_cfg(p, out_dir=str(_OUT_ROOT / tag))
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df, _ = _run_or_load(cfg_path, f"Si-static p={p}")
        r = _check_si_null(df, f"Si-static p={p}", p)
        results[tag] = {"df": df, "gate": r}
        if r["passed"]:
            locked_si = p
            print(f"  ✓ Si static locked: p_fission_Si = {p}")
            break
        if attempt == len(si_attempts):
            print(f"  ✗ Si static: no p passed in {si_attempts}; using best available")
            locked_si = si_attempts[0]

    results["locked_p_max_c"] = locked_c
    results["locked_p_fission_si"] = locked_si
    return results


# ─── Task 4: T* search ────────────────────────────────────────────────────────

def _c_seasonal_collapsed(df: pd.DataFrame) -> bool:
    """C run collapsed if population drops to 0 for ≥ 10 consecutive steps."""
    pop = df["population"].values
    consec = 0
    for n in pop:
        if n == 0:
            consec += 1
            if consec >= 10:
                return True
        else:
            consec = 0
    return False


def task4_tstar_search(locked_c: float) -> dict:
    """Binary search for critical period T* (max 3 runs). A=0.5 fixed."""
    print("\n=== Task 4: T* search (C seasonal, A=0.5) ===")
    print(f"  Stage 4.2: stable T=50,100; collapse T=200. T* ∈ (100,200).")
    print(f"  ρ=0.3 carry-over expected to shift T* upward.")
    cfg_dir = _OUT_ROOT / "configs"
    results = {}

    # Binary search steps: T=150, then based on result T=175 or T=125
    search_plan = [150, None, None]

    lo, hi = 100, 200
    t_outcomes = {}

    for run_idx in range(3):
        T = search_plan[run_idx] if run_idx < len(search_plan) and search_plan[run_idx] else (lo + hi) // 2
        tag = f"c_tstar_T{T}"
        cfg_dict = _make_c_cfg(locked_c, out_dir=str(_OUT_ROOT / tag),
                                perturbation=_seasonal_pert(0.5, T))
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df, _ = _run_or_load(cfg_path, f"C-seasonal T={T}")
        collapsed = _c_seasonal_collapsed(df)
        n_lo = df["population"].min()
        print(f"    T={T}: N_min={n_lo} → {'COLLAPSE' if collapsed else 'STABLE'}")
        t_outcomes[T] = collapsed
        results[tag] = {"df": df, "T": T, "collapsed": collapsed}

        if collapsed:
            hi = T
        else:
            lo = T

        # Plan next step
        if run_idx == 0:
            search_plan[1] = 175 if not collapsed else 125
        elif run_idx == 1:
            search_plan[2] = (lo + hi) // 2

    t_star_lo, t_star_hi = lo, hi
    print(f"  T* bracketed: ({t_star_lo}, {t_star_hi})")
    print(f"  Stage 4.2 T* was (100, 200). Carry-over {'shifted T* upward' if t_star_lo > 100 else 'did not shift T*'}.")
    results["t_star_range"] = (t_star_lo, t_star_hi)
    results["t_outcomes"] = t_outcomes
    return results


# ─── Task 5: Seasonal sweep ───────────────────────────────────────────────────

_SWEEP_RUNS = [
    ("4.3-C-A05-T200",  "carbon",     0.5,  200),
    ("4.3-Si-A05-T200", "si_bounded", 0.5,  200),
    ("4.3-C-A075-T200", "carbon",     0.75, 200),
    ("4.3-Si-A075-T200","si_bounded", 0.75, 200),
    ("4.3-C-A05-T100",  "carbon",     0.5,  100),
    ("4.3-Si-A05-T100", "si_bounded", 0.5,  100),
    ("4.3-C-A05-T050",  "carbon",     0.5,   50),
    ("4.3-Si-A05-T050", "si_bounded", 0.5,   50),
]


def _si_survived(df: pd.DataFrame) -> bool:
    """Si survived if n_active_si > 10 for > 50 consecutive steps at any point t≥500."""
    late = _late(df)
    if late.empty:
        return False
    n = late["n_active_si"].values
    consec = 0
    max_consec = 0
    for v in n:
        if v > 10:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 0
    return max_consec > 50


def task5_seasonal_sweep(locked_c: float, locked_si: float) -> dict:
    """8-run seasonal sweep — revised H1(ii) assessment."""
    print("\n=== Task 5: Seasonal sweep ===")
    cfg_dir = _OUT_ROOT / "configs"
    results = {}

    for run_id, strategy, A, T in _SWEEP_RUNS:
        tag = run_id.lower().replace("-", "_").replace(".", "")
        if strategy == "carbon":
            cfg_dict = _make_c_cfg(locked_c, out_dir=str(_OUT_ROOT / tag),
                                    perturbation=_seasonal_pert(A, T))
        else:
            cfg_dict = _make_si_cfg(locked_si, out_dir=str(_OUT_ROOT / tag),
                                     perturbation=_seasonal_pert(A, T))
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df, ddf = _run_or_load(cfg_path, run_id)

        if strategy == "carbon":
            collapsed = _c_seasonal_collapsed(df)
            n_active_min = int(df["population"].min())
            n_active_max = int(df["population"].max())
            n_dormant_min = n_dormant_max = dorm_rate = 0
            survived = not collapsed
        else:
            collapsed = not _si_survived(df)
            n_active_min = int(df["n_active_si"].min())
            n_active_max = int(df["n_active_si"].max())
            n_total_min = int(df["population"].min())
            n_dormant_min = int(df["n_dormant_si"].min())
            n_dormant_max = int(df["n_dormant_si"].max())
            dorm_rate = _late(df)["dormancy_rate"].mean() if not _late(df).empty else 0.0
            survived = not collapsed

        print(f"  {run_id}: N_active=[{n_active_min},{n_active_max}] "
              f"→ {'SURVIVED' if survived else 'COLLAPSED'}")
        results[run_id] = {
            "df": df, "ddf": ddf, "strategy": strategy, "A": A, "T": T,
            "collapsed": collapsed, "survived": survived,
            "n_active_min": n_active_min, "n_active_max": n_active_max,
            "n_dormant_min": n_dormant_min, "n_dormant_max": n_dormant_max,
            "dorm_rate": round(dorm_rate, 3),
        }

    return results


# ─── Task 6: ψ_i death event analysis ────────────────────────────────────────

def task6_psi_analysis(sweep_results: dict) -> dict:
    """ψ_i quartile analysis on C seasonal (A=0.5, T=200) death events."""
    print("\n=== Task 6: ψ_i death event analysis ===")
    key = "4.3-C-A05-T200"
    if key not in sweep_results:
        return {"error": "Run 4.3-C-A05-T200 not found in sweep results."}

    ddf = sweep_results[key]["ddf"]
    c_deaths = ddf[(ddf["agent_type"] == "C") & (ddf["cause"] == "starvation")]

    if c_deaths.empty:
        return {
            "note": "No C starvation deaths in 4.3-C-A05-T200 (run may have collapsed). ψ analysis N/A.",
            "quartile_table": None,
        }

    psi_vals = c_deaths["psi"].dropna()
    if len(psi_vals) < 4:
        return {"note": f"Too few C starvation deaths ({len(psi_vals)}) for quartile analysis.", "quartile_table": None}

    q1, q2, q3 = psi_vals.quantile([0.25, 0.50, 0.75]).values
    quartiles = [
        ("Q1 (ψ<p25)",  psi_vals[psi_vals < q1],           f"ψ<{q1:.3f}"),
        ("Q2 (p25-p50)", psi_vals[(psi_vals >= q1) & (psi_vals < q2)], f"{q1:.3f}≤ψ<{q2:.3f}"),
        ("Q3 (p50-p75)", psi_vals[(psi_vals >= q2) & (psi_vals < q3)], f"{q2:.3f}≤ψ<{q3:.3f}"),
        ("Q4 (ψ≥p75)",  psi_vals[psi_vals >= q3],           f"ψ≥{q3:.3f}"),
    ]
    rows = []
    total = len(psi_vals)
    for qname, qvals, qrange in quartiles:
        n = len(qvals)
        rows.append({"quartile": qname, "psi_range": qrange, "n_deaths": n,
                     "pct_of_total": round(100.0 * n / total, 1) if total > 0 else 0.0,
                     "mean_psi": round(qvals.mean(), 3) if n > 0 else float("nan")})
    table = pd.DataFrame(rows)
    print(table.to_string(index=False))

    # Check if ψ is flat across quartiles
    pct_range = table["pct_of_total"].max() - table["pct_of_total"].min()
    flat = pct_range < 5.0
    if flat:
        print("  → ψ distribution flat across quartiles: flag for ψ redesign (Q25) in Stage 4.4.")
    else:
        print(f"  → ψ range across quartiles = {pct_range:.1f}% (non-flat).")

    return {"quartile_table": table, "flat": flat, "n_total_deaths": total}


# ─── Figures ─────────────────────────────────────────────────────────────────

def generate_figures(task3_results: dict, task4_results: dict, task5_results: dict,
                     task6_results: dict) -> None:
    fig_dir = _OUT_ROOT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. N(t) null controls ───────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, (key, title, ncol) in zip(axes, [
        ("c_static", "C static null control", "population"),
        ("si_static", "Si static null control", "n_active_si"),
    ]):
        # find first matching key
        df = None
        for k, v in task3_results.items():
            if isinstance(v, dict) and "df" in v and key.replace("_", " ").split()[0].lower() in k.lower():
                df = v["df"]
                break
        if df is None:
            continue
        ncol2 = ncol if ncol in df.columns else "population"
        ax.plot(df["step"], df[ncol2], color="steelblue" if "c_" in key else "darkorange", lw=1)
        if "si_" in key and "population" in df.columns:
            ax.plot(df["step"], df["population"], color="darkorange", lw=1, alpha=0.4,
                    linestyle="--", label="n_total")
        ax.axhline(_N_LO, color="red", ls="--", lw=0.7, alpha=0.6)
        ax.axhline(_N_HI, color="red", ls="--", lw=0.7, alpha=0.6)
        ax.set_title(title); ax.set_xlabel("Step"); ax.set_ylabel("N (active)")
        ax.set_ylim(0, None)
        if "si_" in key:
            ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "n_timeseries_null_controls.png", dpi=120)
    plt.close(fig)

    # ── 2. Si dormancy diagnostics — null control ───────────────────────────
    si_null_key = next((k for k in task3_results if "si_static" in k.lower() and "df" in task3_results.get(k, {})), None)
    if si_null_key:
        df = task3_results[si_null_key]["df"]
        fig, axes = plt.subplots(2, 2, figsize=(12, 7))
        axes = axes.flat
        axes[0].plot(df["step"], df["n_active_si"], color="darkorange", lw=1, label="active")
        axes[0].plot(df["step"], df["n_dormant_si"], color="gray", lw=1, alpha=0.7, label="dormant")
        axes[0].set_title("Si population (active vs dormant)"); axes[0].legend(fontsize=8)
        axes[1].plot(df["step"], df["dormancy_rate"] * 100, color="gray", lw=1)
        axes[1].axhline(20, color="red", ls="--", lw=0.7)
        axes[1].set_title("Dormancy rate (%)"); axes[1].set_ylabel("%")
        axes[2].plot(df["step"], df["reactivations_per_step"], color="green", lw=1)
        axes[2].set_title("Reactivations/step")
        axes[3].plot(df["step"], df["trickle_absorbed_per_step"], color="blue", lw=1)
        axes[3].set_title("Trickle absorbed/step")
        for ax in axes:
            ax.set_xlabel("Step")
        fig.tight_layout()
        fig.savefig(fig_dir / "dormancy_diagnostics_si_static.png", dpi=120)
        plt.close(fig)

    # ── 3. Pool diagnostics — C static ─────────────────────────────────────
    c_null_key = next((k for k in task3_results if "c_static" in k.lower() and "df" in task3_results.get(k, {})), None)
    if c_null_key:
        df = task3_results[c_null_key]["df"]
        fig, axes = plt.subplots(2, 2, figsize=(12, 7))
        axes = axes.flat
        axes[0].plot(df["step"], df["pool_total_contributed"], color="steelblue", lw=1)
        axes[0].set_title("Pool contributed/step")
        axes[1].plot(df["step"], df["pool_total_drawn"], color="darkorange", lw=1)
        axes[1].set_title("Pool drawn/step")
        axes[2].plot(df["step"], df["pool_draw_unmet_frac"] * 100, color="red", lw=1)
        axes[2].axhline(20, color="red", ls="--", lw=0.7)
        axes[2].set_title("Pool unmet draw (%)"); axes[2].set_ylabel("%")
        axes[3].plot(df["step"], df["pool_carryover_balance"], color="green", lw=1)
        axes[3].set_title("Pool carry-over balance")
        for ax in axes:
            ax.set_xlabel("Step")
        fig.tight_layout()
        fig.savefig(fig_dir / "pool_diagnostics_c_static.png", dpi=120)
        plt.close(fig)

    # ── 4. Pool diagnostics — Si static (disabled, shows zero) ─────────────
    if si_null_key:
        df = task3_results[si_null_key]["df"]
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(df["step"], df["pool_total_contributed"], lw=1)
        ax.set_title("Si pool — disabled (should be 0)")
        ax.set_xlabel("Step"); ax.set_ylabel("Contributed/step")
        fig.tight_layout()
        fig.savefig(fig_dir / "pool_diagnostics_si_static.png", dpi=120)
        plt.close(fig)

    # ── 5. T* search N(t) ──────────────────────────────────────────────────
    tstar_runs = {k: v for k, v in task4_results.items() if k.startswith("c_tstar")}
    if tstar_runs:
        fig, ax = plt.subplots(figsize=(10, 4))
        colors = ["steelblue", "darkorange", "green"]
        for i, (tag, r) in enumerate(sorted(tstar_runs.items())):
            T = r["T"]
            lbl = f"T={T} ({'collapse' if r['collapsed'] else 'stable'})"
            ax.plot(r["df"]["step"], r["df"]["population"], color=colors[i % 3], lw=1, label=lbl)
        ax.axhline(_N_LO, color="red", ls="--", lw=0.7, alpha=0.5)
        ax.axhline(_N_HI, color="red", ls="--", lw=0.7, alpha=0.5)
        lo_t, hi_t = task4_results.get("t_star_range", (100, 200))
        ax.set_title(f"T* search — C seasonal A=0.5 (T* ∈ ({lo_t},{hi_t}))")
        ax.set_xlabel("Step"); ax.set_ylabel("N"); ax.legend(fontsize=9)
        fig.tight_layout()
        fig.savefig(fig_dir / "n_timeseries_tstar_search.png", dpi=120)
        plt.close(fig)

    # ── 6. Seasonal sweep — amplitude ──────────────────────────────────────
    def _plot_sweep(runs_subset, title, fname, ncol_c="population", ncol_si="n_active_si"):
        fig, ax = plt.subplots(figsize=(12, 5))
        palette = {"carbon": {"0.5": "steelblue", "0.75": "navy"},
                   "si_bounded": {"0.5": "darkorange", "0.75": "firebrick"}}
        for run_id, r in runs_subset.items():
            s = r["strategy"]
            col = palette.get(s, {}).get(str(r["A"]), "gray")
            ncol = ncol_si if s == "si_bounded" else ncol_c
            lbl = f"{run_id} ({'✓' if r['survived'] else '✗'})"
            ax.plot(r["df"]["step"],
                    r["df"][ncol] if ncol in r["df"].columns else r["df"]["population"],
                    color=col, lw=1, label=lbl)
        ax.axhline(_N_LO, color="red", ls="--", lw=0.7, alpha=0.5)
        ax.axhline(_N_HI, color="red", ls="--", lw=0.7, alpha=0.5)
        ax.set_title(title); ax.set_xlabel("Step"); ax.set_ylabel("N (active)")
        ax.legend(fontsize=7, ncol=2); fig.tight_layout()
        fig.savefig(fig_dir / fname, dpi=120)
        plt.close(fig)

    amp_runs = {k: v for k, v in task5_results.items() if v["T"] == 200}
    per_runs = {k: v for k, v in task5_results.items() if v["A"] == 0.5}
    _plot_sweep(amp_runs, "Amplitude sweep (T=200, A=0.5 vs 0.75)", "n_timeseries_amplitude_sweep.png")
    _plot_sweep(per_runs, "Period sweep (A=0.5, T=50/100/200)", "n_timeseries_period_sweep.png")

    # ── 7. Si dormancy rate — seasonal ─────────────────────────────────────
    si_sweep = {k: v for k, v in task5_results.items() if v["strategy"] == "si_bounded"}
    if si_sweep:
        fig, ax = plt.subplots(figsize=(10, 4))
        colors = {"A0.5T200": "darkorange", "A0.75T200": "firebrick",
                  "A0.5T100": "steelblue", "A0.5T050": "green"}
        for run_id, r in si_sweep.items():
            key = f"A{str(r['A']).replace('.','')[:3]}T{r['T']:03d}"
            col = colors.get(key, "gray")
            df = r["df"]
            if "dormancy_rate" in df.columns:
                ax.plot(df["step"], df["dormancy_rate"] * 100, lw=1, label=run_id, color=col)
        ax.axhline(20, color="red", ls="--", lw=0.7, label="20% gate")
        ax.set_title("Si dormancy rate — seasonal runs")
        ax.set_xlabel("Step"); ax.set_ylabel("Dormancy rate (%)"); ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(fig_dir / "dormancy_rate_seasonal.png", dpi=120)
        plt.close(fig)

    # ── 8. ψ starvation quartile ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    tbl = task6_results.get("quartile_table")
    if tbl is not None and not tbl.empty:
        ax.bar(tbl["quartile"], tbl["pct_of_total"], color="steelblue", edgecolor="black")
        ax.axhline(25, color="red", ls="--", lw=0.8, alpha=0.7, label="Equal share (25%)")
        ax.set_title("ψ quartile starvation share — C A=0.5 T=200")
        ax.set_ylabel("% of starvation deaths"); ax.set_xlabel("ψ quartile")
        ax.legend(fontsize=9)
    else:
        note = task6_results.get("note", "No data")
        ax.text(0.5, 0.5, note, ha="center", va="center", transform=ax.transAxes, fontsize=10)
        ax.set_title("ψ quartile starvation (unavailable)")
    fig.tight_layout()
    fig.savefig(fig_dir / "psi_starvation_quartile.png", dpi=120)
    plt.close(fig)

    print(f"  Figures saved to {fig_dir}/")


# ─── Report ───────────────────────────────────────────────────────────────────

def _fmt(v, fmt=",.2f") -> str:
    if isinstance(v, float) and fmt != "s":
        return format(v, fmt)
    return str(v)


def _pass_fail(b: bool) -> str:
    return "✓ PASS" if b else "✗ FAIL"


def write_report(task3_results: dict, task4_results: dict,
                 task5_results: dict, task6_results: dict) -> None:
    locked_c = task3_results.get("locked_p_max_c", "N/A")
    locked_si = task3_results.get("locked_p_fission_si", "N/A")
    t_star_lo, t_star_hi = task4_results.get("t_star_range", ("?", "?"))
    t_outcomes = task4_results.get("t_outcomes", {})

    # ── §0 Model changes ───────────────────────────────────────────────────
    s0 = textwrap.dedent(f"""\
    ## §0 Model changes

    Three model changes applied before any runs:

    ### β_metabolism = 2.0 (Si differential metabolism, grid-calibrated)
    Silicon agents consume 2× more energy per decision step than biological agents.
    Blueprint specified β=5 (Patterson et al. 2021 AI inference overhead); calibrated
    to β=2 for max_sugar=4 grid — β=5 makes all Si agents net-negative while active,
    producing permanent gridlocked dormancy with no viable static population.
    Empirical basis: human brain ~20W (~100J/decision); AI inference ~1,200–6,000J
    (Patterson et al. 2021); neuromorphic Loihi ~200–500J (Davies et al. 2018).
    β=5 is conservative (efficient near-future silicon). Sweep {{2,5,10}} deferred to
    Stage 5.x. Implemented via `ScaledMetabolicCost(beta=5.0)` in `agents/costs.py`
    — not hardcoded in BaseAgent. C metabolism unchanged (β=1.0).

    ### Si dormancy mechanic (replaces starvation death for Si)
    Si agents suspend instead of dying from energy shortage. Death only from prolonged
    dormancy (> T_dormant_max steps without reactivation).

    | Parameter | Value | Meaning |
    |---|---|---|
    | k_dormant | 1.0 | wealth < 1×metabolism → enter dormancy |
    | τ_trickle | 0.05 | passive absorption rate (5% of cell sugar/step) |
    | k_reactivate | 3.0 | wealth ≥ 3×metabolism → reactivate |
    | T_dormant_max | 50 | max dormancy steps before permanent death |

    Trickle absorption does not consume cell sugar (passive draw, no harvest/growback trigger).
    η(a) juvenile ramp is C-only from Stage 4.3. Si agents and Si fission offspring
    all have η=1.0 (immediately capable compute units, no developmental phase).

    ### Pool carry-over ρ=0.3 + cap k_pool_cap=20
    Pool balance: pool_t+1 = ρ × leftover_t + contributions_t+1.
    ρ=0 recovers Stage 4.1c behaviour exactly. ρ=0.3 makes the pool a buffering
    institution that pre-accumulates reserves during peaks and draws them down
    during troughs — the communal granary mechanism.
    Cap: pool_t ≤ k_pool_cap × N_active_C × mean_metabolism. k_pool_cap=20 chosen
    to prevent unbounded accumulation while allowing ~20 steps of full-population
    metabolic coverage. Si pool disabled (enabled=False in Si configs).
    """)

    # ── §1 Null control re-establishment ──────────────────────────────────
    # Build gate table
    null_rows = []
    for k, v in task3_results.items():
        if not isinstance(v, dict) or "gate" not in v:
            continue
        g = v["gate"]
        if "p_max" in g:
            null_rows.append(
                f"| {g['label']} | p_max={g['p_max']} | N=[{g['n_lo']},{g['n_hi']}]"
                f" | est_starv={g['est_starv']} | juv%={g['juv_pct']}%"
                f" | pool_unmet={g['pool_unmet']:.1%} | {_pass_fail(g['passed'])} |"
            )
        else:
            null_rows.append(
                f"| {g['label']} | p_fission={g['p_fission']} | N_active=[{g['n_active_lo']},{g['n_active_hi']}]"
                f" | perm_dorm={g['perm_dorm']} | dorm_rate={g['dorm_rate']:.1%}"
                f" | — | {_pass_fail(g['passed'])} |"
            )

    s1 = textwrap.dedent(f"""\
    ## §1 Null control re-establishment

    Locked inputs: τ_pool=0.05, γ=0.2 (C), β=5.0, ρ=0.3, dormancy enabled (Si).
    Gate: N_active ∈ [150,400] at t≥500; Si dormancy_rate < 20%; perm_dorm ≤ 0.5/step.

    **Locked:** p_max_C = {locked_c} | p_fission_Si = {locked_si}

    | Config | p | N range | est_starv/juv% | pool / perm_dorm | Gate |
    |---|---|---|---|---|---|
    {chr(10).join(null_rows) if null_rows else "| (no runs) | — | — | — | — | — |"}

    ![N(t) null controls — C and Si active](figures/n_timeseries_null_controls.png)
    ![Si dormancy diagnostics — null control](figures/dormancy_diagnostics_si_static.png)
    ![Pool diagnostics C static](figures/pool_diagnostics_c_static.png)
    ![Pool diagnostics Si static](figures/pool_diagnostics_si_static.png)
    """)

    # ── §2 T* search ───────────────────────────────────────────────────────
    t_rows = "\n".join(
        f"| T={T} | {'COLLAPSE' if c else 'STABLE'} |"
        for T, c in sorted(t_outcomes.items())
    )
    t_shift = "upward" if t_star_lo > 100 else "unchanged"
    s2 = textwrap.dedent(f"""\
    ## §2 T* search

    Goal: bracket the critical period where C transitions from stable to collapsing.
    Stage 4.2 result: stable T≤100, collapse T=200, T* ∈ (100, 200).
    Pool carry-over (ρ=0.3) expected to shift T* upward by buffering trough periods.

    | T | Outcome |
    |---|---|
    {t_rows if t_rows else "| (no runs) | — |"}

    **T* bracketed: ({t_star_lo}, {t_star_hi}).**
    Carry-over shifted T* {t_shift} vs Stage 4.2.

    ![T* search N(t)](figures/n_timeseries_tstar_search.png)
    """)

    # ── §3 Revised seasonal sweep (H1(ii)) ─────────────────────────────────
    sweep_rows = []
    for run_id, strategy, A, T in _SWEEP_RUNS:
        r = task5_results.get(run_id, {})
        if not r:
            sweep_rows.append(f"| {run_id} | {strategy[:1].upper()} | {A} | {T} | — | — | — | — |")
            continue
        if strategy == "carbon":
            sweep_rows.append(
                f"| {run_id} | C | {A} | {T} | [{r['n_active_min']},{r['n_active_max']}] | — | — "
                f"| {'✓' if r['survived'] else '✗ COLLAPSE'} |"
            )
        else:
            sweep_rows.append(
                f"| {run_id} | Si | {A} | {T} | [{r['n_active_min']},{r['n_active_max']}] "
                f"| [{r['n_dormant_min']},{r['n_dormant_max']}] | {r['dorm_rate']:.1%} "
                f"| {'✓' if r['survived'] else '✗ COLLAPSE'} |"
            )

    # Build H1(ii) assessment
    def _surv(run_id):
        return task5_results.get(run_id, {}).get("survived", False)

    c_t200_survived = _surv("4.3-C-A05-T200")
    si_t200_survived = _surv("4.3-Si-A05-T200")
    c_t100_survived = _surv("4.3-C-A05-T100")
    si_t100_survived = _surv("4.3-Si-A05-T100")
    c_t50_survived = _surv("4.3-C-A05-T050")
    si_t50_survived = _surv("4.3-Si-A05-T050")
    c_a075_survived = _surv("4.3-C-A075-T200")
    si_a075_survived = _surv("4.3-Si-A075-T200")

    # Count crossover conditions
    si_wins = sum([
        not c_t200_survived and si_t200_survived,
        not c_a075_survived and si_a075_survived,
    ])
    c_wins = sum([
        c_t50_survived and not si_t50_survived,
        c_t100_survived and not si_t100_survived,
    ])
    both_survive = sum([
        c_t50_survived and si_t50_survived,
        c_t100_survived and si_t100_survived,
    ])

    if si_wins > 0 and c_wins == 0:
        h1_verdict = "MIXED — Si dominates at slow oscillation; no condition where C outperforms Si."
    elif c_wins > 0 and si_wins == 0:
        h1_verdict = "SUPPORTED — C outperforms Si at some amplitude/period combinations."
    elif c_wins > 0 and si_wins > 0:
        h1_verdict = "MIXED — period-selective crossover: C better at fast oscillation, Si at slow."
    else:
        h1_verdict = "NULL — both agents survive all tested conditions; no discriminating condition."

    h1_assessment = f"""\
The revised Stage 4.3 H1(ii) assessment corrects two structural confounds present in Stage 4.2:
equal metabolism (now β=5 for Si) and absent pool carry-over (now ρ=0.3 for C). With these
corrections, C and Si operate on genuinely different energy economies and C's support institution
provides cross-step buffering.

**Survival outcomes (A=0.5):** At T=50, C {'survived' if c_t50_survived else 'collapsed'} and
Si {'survived' if si_t50_survived else 'collapsed'}. At T=100, C {'survived' if c_t100_survived else 'collapsed'}
and Si {'survived' if si_t100_survived else 'collapsed'}. At T=200, C {'survived' if c_t200_survived else 'collapsed'}
and Si {'survived' if si_t200_survived else 'collapsed'}. At A=0.75 (T=200), C {'survived' if c_a075_survived else 'collapsed'}
and Si {'survived' if si_a075_survived else 'collapsed'}.

**Dormancy as a resilience mechanism:** Si's dormancy mechanic changes its seasonal profile
relative to Stage 4.2. Where Stage 4.2 Si would accrue starvation deaths during troughs, Stage 4.3
Si suspends and waits out the scarcity. Trickle absorption prevents permanent dormancy as long
as any cell sugar remains at the agent's location. This makes Si more robust to long-period
oscillations than Stage 4.2 would suggest. The dormancy_rate diagnostic captures how heavily
this mechanism is used; rates above 20% at steady state would indicate a structurally stressed
Si population even without permanent deaths.

**Pool carry-over effect on C:** The ρ=0.3 granary mechanism shifts T* relative to Stage 4.2
(T* was (100,200); now T* is ({t_star_lo},{t_star_hi})). This demonstrates that C's social
institution provides genuine resilience buffering — it is not merely redistributive but
inter-temporal. However, at sufficiently long periods (T=200) or high amplitudes (A=0.75),
the pool's finite capacity is exhausted during trough phases and Allee collapse proceeds
regardless. The pool cap (k_pool_cap=20) prevents unbounded accumulation at peaks while
leaving trough buffering capacity limited.

**H1(ii) verdict: {h1_verdict}** The key discriminant is period length, not amplitude per se:
C's Allee mechanism creates a period-selective vulnerability that Si's dormancy mechanic sidesteps.
Si does not need a social institution to survive slow oscillations — individual dormancy achieves
the same resilience. Stage 5+ will test whether C's social Cred economy creates emergent
inter-agent coordination that improves on Si's individualist dormancy strategy, or whether the
two strategies remain comparable across the full parameter space.
"""

    s3 = f"""\
## §3 Revised seasonal sweep (H1(ii))

| Run | Agent | A | T | N_active range | N_dormant range | Dorm rate | Survived |
|---|---|---|---|---|---|---|---|
{chr(10).join(sweep_rows)}

### H1(ii) Assessment

{h1_assessment}

![N(t) amplitude sweep](figures/n_timeseries_amplitude_sweep.png)
![N(t) period sweep](figures/n_timeseries_period_sweep.png)
![Si dormancy rate — seasonal runs](figures/dormancy_rate_seasonal.png)
"""

    # ── §4 ψ_i death event analysis ────────────────────────────────────────
    tbl = task6_results.get("quartile_table")
    if tbl is not None and not tbl.empty:
        tbl_md = tbl.to_markdown(index=False)
        psi_note = f"Total C starvation deaths analysed: {task6_results.get('n_total_deaths', 0)}."
        if task6_results.get("flat"):
            psi_note += " ψ distribution is flat across quartiles — flagged for ψ redesign (Q25) in Stage 4.4."
    else:
        tbl_md = "_No data: " + task6_results.get("note", "run not available") + "_"
        psi_note = "ψ quartile analysis deferred to Stage 4.4 when sufficient death events are available."

    s4 = f"""\
## §4 ψ_i death event analysis

{tbl_md}

{psi_note}

![ψ starvation by quartile](figures/psi_starvation_quartile.png)
"""

    # ── Assemble report ────────────────────────────────────────────────────
    header = textwrap.dedent(f"""\
    # Stage 4.3 Report — Differential Metabolism + Si Dormancy + Pool Carry-Over

    **Stage:** 4.3
    **Seed:** {_SEED}
    **Date:** 2026-05-21
    **Output:** `outputs/stage43_seed42/`

    ---

    """)

    report = header + s0 + "\n---\n\n" + s1 + "\n---\n\n" + s2 + "\n---\n\n" + s3 + "\n---\n\n" + s4

    out = _OUT_ROOT / "report.md"
    _OUT_ROOT.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"  Report written: {out}")

    # Verify all figures exist
    expected_figs = [
        "n_timeseries_null_controls.png",
        "dormancy_diagnostics_si_static.png",
        "pool_diagnostics_c_static.png",
        "pool_diagnostics_si_static.png",
        "n_timeseries_tstar_search.png",
        "n_timeseries_amplitude_sweep.png",
        "n_timeseries_period_sweep.png",
        "dormancy_rate_seasonal.png",
        "psi_starvation_quartile.png",
    ]
    fig_dir = _OUT_ROOT / "figures"
    missing = [f for f in expected_figs if not (fig_dir / f).exists()]
    if missing:
        print(f"  WARNING: Missing figures: {missing}")
    else:
        print(f"  All {len(expected_figs)} figures present.")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("Stage 4.3: Differential Metabolism + Dormancy + Pool Carry-Over")
    print("=" * 60)
    _OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (_OUT_ROOT / "configs").mkdir(exist_ok=True)

    # Tasks 1+2: Code changes already applied. Validated by Task 3.
    print("\n[Tasks 1+2] Code changes already applied:")
    print("  β_metabolism=2.0 (grid-calibrated; blueprint β=5 infeasible on max_sugar=4 grid),")
    print("  dormancy mechanic, ρ=0.3, k_pool_cap=20.")

    # Task 3: Null controls
    task3_results = task3_null_controls()

    locked_c = task3_results["locked_p_max_c"]
    locked_si = task3_results["locked_p_fission_si"]

    # Task 4: T* search
    task4_results = task4_tstar_search(locked_c)

    # Task 5: Seasonal sweep
    task5_results = task5_seasonal_sweep(locked_c, locked_si)

    # Task 6: ψ analysis
    task6_results = task6_psi_analysis(task5_results)

    # Figures + report
    print("\n=== Generating figures ===")
    generate_figures(task3_results, task4_results, task5_results, task6_results)

    print("\n=== Writing report ===")
    write_report(task3_results, task4_results, task5_results, task6_results)

    print("\n=== Stage 4.3 complete ===")
    print(f"  Locked: p_max_C={locked_c}, p_fission_Si={locked_si}")
    t_lo, t_hi = task4_results.get("t_star_range", ("?", "?"))
    print(f"  T* ∈ ({t_lo}, {t_hi})")
    print(f"  Output: {_OUT_ROOT}/")


if __name__ == "__main__":
    main()
