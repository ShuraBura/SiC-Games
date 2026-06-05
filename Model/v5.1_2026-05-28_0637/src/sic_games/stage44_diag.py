"""Stage 4.4 Diagnostic — C null control failure analysis.

Factorial design isolating the cause of C extinction at k=4 grid:
  Run A — C bare (pool off, λ=0), p_max ∈ {0.03, 0.05, 0.07, 0.10, 0.15}
  Run B — C with pool, no λ  (p_max = 0.03 + best Run-A survivors ± 0.01)
  Run C — C with λ, no pool  (same p_max as Run B)
  Run D — C full (pool + λ)  (p_max = 0.03 + best Run-A survivor)

Key new diagnostics: pct_isolated_C and mean_nearest_C_dist (per step).

Blueprint: SiC_Games_Stage4_4_Diagnostic.md v1.0
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
_ISOLATION_RADIUS = 3          # Chebyshev radius for pct_isolated_C
_ISOLATION_THRESH = 40.0       # % isolated threshold for Allee dispersal confirmation
_N_BOMB = 800                  # abort runs exceeding this — keeps each run under ~5 min
# NOTE: 3000 caused p=0.10 to run all 1000 steps at N~2000 (4 hrs).
# For the diagnostic, we only need to know IF a population survives to t≥500.
# A run that hits 800 before step 100 clearly won't stay in [150,400], so abort early.
_OUT_ROOT = Path("outputs/stage44_diag_seed42")

# ─── base config (k=4, β_Si=5, seed=42) ─────────────────────────────────────
# Built on Stage 4.4 locked parameters.

_BASE_DIAG = dict(
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
    initialization=dict(age_distribution="realistic"),
    life_history=dict(forage_age_min=15, forage_age_max_offset=10, eta_min=0.3, eta_old=0.4,
                      eta_fission_offspring=1.0),
    # Pool ON config (used by Runs B, D); overridden to OFF in Runs A, C
    support_pool=dict(enabled=True, r_pool=5, tau_parent=0.1,
                      tau_pool=0.05, k_reserve=5.0, k_draw=3.0,
                      tau_cred=0.5, tau_cred_reward=0.1,
                      rho_carryover=0.3, k_pool_cap=20.0),
    dormancy=dict(enabled=False),
    run=dict(n_steps=_N_STEPS, metrics_every=1),
    visualization=dict(animate=False, save_static_plots=False),
)

_POOL_OFF = dict(enabled=False, r_pool=5, tau_parent=0.0,
                 tau_pool=0.0, k_reserve=5.0, k_draw=3.0,  # must be >0 per pydantic; ignored when enabled=False
                 tau_cred=0.0, tau_cred_reward=0.0,
                 rho_carryover=0.0, k_pool_cap=0.0)


# ─── config builder ───────────────────────────────────────────────────────────

def _make_cfg(p_max: float, out_dir: str,
              pool_on: bool, lambda_inh: float) -> dict:
    cfg = copy.deepcopy(_BASE_DIAG)
    cfg["birth_c"]["p_max"] = p_max
    cfg["reproduction"]["lambda_inheritance"] = lambda_inh
    if not pool_on:
        cfg["support_pool"] = copy.deepcopy(_POOL_OFF)
    cfg["run"]["output_dir"] = out_dir
    return cfg


def _write_cfg(cfg_dict: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(cfg_dict, f, default_flow_style=False, sort_keys=False)
    return path


# ─── run / load ──────────────────────────────────────────────────────────────

def _run_or_load(cfg_path: Path, label: str) -> pd.DataFrame:
    """Run simulation or load cached metrics. Returns metrics_df only."""
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
        if step_i > 100:
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


# ─── gate + analysis helpers ─────────────────────────────────────────────────

def _late(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["step"] >= _STABLE_T]


def _n_range(df: pd.DataFrame) -> tuple[int, int]:
    late = _late(df)
    if late.empty:
        return 0, 0
    return int(late["population"].min()), int(late["population"].max())


def _collapse_step(df: pd.DataFrame) -> int | None:
    """First step where N drops below 10. None if never."""
    hits = df[df["population"] < 10]
    if hits.empty:
        return None
    return int(hits["step"].iloc[0])


def _spatial_at(df: pd.DataFrame, step: int) -> tuple[float, float]:
    """(mean_nearest_C_dist, pct_isolated_C) at a given step (nearest actual step)."""
    row = df.iloc[(df["step"] - step).abs().argsort()[:1]]
    if row.empty:
        return 0.0, 0.0
    if "mean_nearest_C_dist" not in df.columns:
        return 0.0, 0.0
    return float(row["mean_nearest_C_dist"].iloc[0]), float(row["pct_isolated_C"].iloc[0])


def _survived(df: pd.DataFrame) -> bool:
    lo, hi = _n_range(df)
    return _N_LO <= lo and hi <= _N_HI


def _est_starv(df: pd.DataFrame) -> float:
    late = _late(df)
    if late.empty or "deaths_starvation_established" not in late.columns:
        return 0.0
    return float(late["deaths_starvation_established"].mean())


def _n_series(df: pd.DataFrame, checkpoints=(0, 50, 100, 200, 300, 500, 1000)) -> dict[int, int]:
    out = {}
    for t in checkpoints:
        row = df[df["step"] == t]
        out[t] = int(row["population"].iloc[0]) if not row.empty else 0
    return out


# ─── Run A ────────────────────────────────────────────────────────────────────

def run_A() -> dict:
    """C bare (pool off, λ=0). p_max ∈ {0.03, 0.05, 0.07, 0.10, 0.15}."""
    print("\n" + "="*60)
    print("Run A — C bare (pool OFF, λ=0)")
    print("="*60)
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    p_values = [0.03, 0.05, 0.07, 0.10, 0.15]

    for p in p_values:
        tag = f"A_p{str(p).replace('.', '')}"
        cfg_dict = _make_cfg(p, str(_OUT_ROOT / tag), pool_on=False, lambda_inh=0.0)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df = _run_or_load(cfg_path, f"A-p{p}")

        lo, hi = _n_range(df)
        cs = _collapse_step(df)
        spat100 = _spatial_at(df, 100)
        spat300 = _spatial_at(df, 300)
        surv = _survived(df)
        flag = "✓ PASS" if surv else "  FAIL"
        print(f"  {flag} A-p{p}: N_late=[{lo},{hi}] collapse=t{cs} "
              f"iso@100={spat100[1]:.1f}% iso@300={spat300[1]:.1f}%")
        results[p] = dict(
            df=df, tag=tag, p_max=p, n_lo=lo, n_hi=hi,
            survived=surv, collapse_step=cs,
            est_starv=_est_starv(df),
            n_series=_n_series(df),
            spat_100=spat100, spat_300=spat300,
        )
    return results


# ─── Runs B / C / D ──────────────────────────────────────────────────────────

def _run_series(run_label: str, p_values: list[float],
                pool_on: bool, lambda_inh: float) -> dict:
    cfg_dir = _OUT_ROOT / "configs"
    results = {}
    pool_tag = "on" if pool_on else "off"
    lam_tag = f"lam{str(lambda_inh).replace('.', '')}"
    for p in p_values:
        tag = f"{run_label}_p{str(p).replace('.', '')}"
        cfg_dict = _make_cfg(p, str(_OUT_ROOT / tag), pool_on=pool_on,
                             lambda_inh=lambda_inh)
        cfg_path = cfg_dir / f"{tag}.yaml"
        _write_cfg(cfg_dict, cfg_path)
        df = _run_or_load(cfg_path, f"{run_label}-p{p}")

        lo, hi = _n_range(df)
        cs = _collapse_step(df)
        spat100 = _spatial_at(df, 100)
        surv = _survived(df)
        flag = "✓ PASS" if surv else "  FAIL"
        print(f"  {flag} {run_label}-p{p}: N_late=[{lo},{hi}] collapse=t{cs} "
              f"iso@100={spat100[1]:.1f}%")
        results[p] = dict(
            df=df, tag=tag, p_max=p, n_lo=lo, n_hi=hi,
            survived=surv, collapse_step=cs,
            est_starv=_est_starv(df),
            n_series=_n_series(df),
            spat_100=spat100,
        )
    return results


def run_B(p_values: list[float]) -> dict:
    print("\n" + "="*60)
    print("Run B — C with pool ON, λ=0")
    print("="*60)
    return _run_series("B", p_values, pool_on=True, lambda_inh=0.0)


def run_C(p_values: list[float]) -> dict:
    print("\n" + "="*60)
    print("Run C — C pool OFF, λ=0.1")
    print("="*60)
    return _run_series("C", p_values, pool_on=False, lambda_inh=0.1)


def run_D(p_values: list[float]) -> dict:
    print("\n" + "="*60)
    print("Run D — C full (pool ON, λ=0.1) — replicates Stage 4.4")
    print("="*60)
    return _run_series("D", p_values, pool_on=True, lambda_inh=0.1)


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


def generate_figures(runA: dict, runB: dict, runC: dict, runD: dict) -> dict[str, str]:
    figs = {}
    print("\n=== Generating figures ===")

    # ── Figure 1: Run A N(t) for all p_max values ──────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(runA)))
    for (p, res), col in zip(runA.items(), colors):
        ax.plot(res["df"]["step"], res["df"]["population"],
                label=f"p={p}", color=col, lw=1.5)
    ax.axhline(_N_LO, color="red", ls="--", lw=0.8, label="N gates")
    ax.axhline(_N_HI, color="red", ls="--", lw=0.8)
    ax.set_xlabel("Step"); ax.set_ylabel("N"); ax.set_title("Run A: N(t) — C bare (pool OFF, λ=0)")
    ax.legend(fontsize=8); ax.set_ylim(bottom=0)
    figs["runA_nt"] = _fig_to_b64(fig)

    # ── Figure 2: Run A pct_isolated_C over time ────────────────────────────
    if "pct_isolated_C" in next(iter(runA.values()))["df"].columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        for (p, res), col in zip(runA.items(), colors):
            df = res["df"]
            if (df["population"] > 0).any():
                alive = df[df["population"] > 0]
                ax.plot(alive["step"], alive["pct_isolated_C"],
                        label=f"p={p}", color=col, lw=1.5)
        ax.axhline(_ISOLATION_THRESH, color="orange", ls="--", lw=1,
                   label=f"{_ISOLATION_THRESH}% Allee threshold")
        ax.set_xlabel("Step"); ax.set_ylabel("% isolated C agents")
        ax.set_title("Run A: pct_isolated_C — Allee dispersal signal")
        ax.legend(fontsize=8); ax.set_ylim(0, 105)
        figs["runA_isolated"] = _fig_to_b64(fig)

    # ── Figure 3: Run A mean_nearest_C_dist over time ───────────────────────
    if "mean_nearest_C_dist" in next(iter(runA.values()))["df"].columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        for (p, res), col in zip(runA.items(), colors):
            df = res["df"]
            if (df["population"] > 0).any():
                alive = df[df["population"] > 0]
                ax.plot(alive["step"], alive["mean_nearest_C_dist"],
                        label=f"p={p}", color=col, lw=1.5)
        ax.axhline(_ISOLATION_RADIUS, color="orange", ls="--", lw=1,
                   label=f"parent_radius={_ISOLATION_RADIUS}")
        ax.set_xlabel("Step"); ax.set_ylabel("Mean nearest C distance (Chebyshev)")
        ax.set_title("Run A: mean nearest C distance")
        ax.legend(fontsize=8)
        figs["runA_dist"] = _fig_to_b64(fig)

    # ── Figure 4: factorial N_late comparison ──────────────────────────────
    all_p = sorted(set(
        list(runA.keys()) + list(runB.keys()) +
        list(runC.keys()) + list(runD.keys())
    ))
    x = np.arange(len(all_p))
    w = 0.2
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, (run_res, label, color) in enumerate([
        (runA, "A: bare", "#2196F3"),
        (runB, "B: pool", "#4CAF50"),
        (runC, "C: λ", "#FF9800"),
        (runD, "D: pool+λ", "#9C27B0"),
    ]):
        heights = []
        for p in all_p:
            if p in run_res:
                lo, hi = run_res[p]["n_lo"], run_res[p]["n_hi"]
                heights.append((lo + hi) / 2.0 if (lo + hi) > 0 else 0)
            else:
                heights.append(float("nan"))
        ax.bar(x + i * w, heights, w, label=label, color=color, alpha=0.8)
    ax.axhline(_N_LO, color="red", ls="--", lw=0.8)
    ax.axhline(_N_HI, color="red", ls="--", lw=0.8, label="N gates")
    ax.set_xticks(x + 1.5 * w); ax.set_xticklabels([f"p={p}" for p in all_p])
    ax.set_ylabel("Mean N (late window t≥500)")
    ax.set_title("Factorial comparison: mean N at t≥500 by Run × p_max")
    ax.legend(fontsize=8)
    figs["factorial_N"] = _fig_to_b64(fig)

    print(f"  Figures generated: {list(figs.keys())}")
    return figs


# ─── Diagnosis ────────────────────────────────────────────────────────────────

def _diagnose(runA: dict) -> dict:
    """Determine which hypothesis is confirmed from Run A data."""
    survivors = {p: r for p, r in runA.items() if r["survived"]}
    collapses = {p: r for p, r in runA.items() if not r["survived"]}

    # Allee signal: mean pct_isolated_C at t=100 before collapse
    iso_vals = []
    for p, r in runA.items():
        df = r["df"]
        cs = r["collapse_step"]
        if cs is not None and cs > 20:
            # Sample early isolation — before or around collapse
            sample_t = min(cs - 10, 100)
            row = df.iloc[(df["step"] - sample_t).abs().argsort()[:1]]
            if not row.empty and "pct_isolated_C" in df.columns:
                iso_vals.append(float(row["pct_isolated_C"].iloc[0]))

    mean_iso_pre_collapse = float(np.mean(iso_vals)) if iso_vals else 0.0

    if survivors:
        # Run A shows survival at some p_max — H_B (birth rate) confirmed
        best_p = min(survivors.keys())
        diagnosis = "H_B"
        summary = (
            f"Hypothesis B confirmed: C is viable at k=4 when p_max is sufficiently high. "
            f"Minimum passing p_max = {best_p} (Run A, pool OFF, λ=0). "
            f"p_max was simply under-calibrated for the k=4 richer grid. "
            f"Action: re-lock p_max_C at {best_p} and re-run Stage 4.4 seasonal sweep."
        )
        action = f"parameter_fix:p_max={best_p}"
    elif mean_iso_pre_collapse > _ISOLATION_THRESH:
        # High isolation before collapse — H_A (Allee dispersal) confirmed
        diagnosis = "H_A"
        summary = (
            f"Hypothesis A confirmed: Allee dispersal collapse. "
            f"Mean pct_isolated_C before collapse = {mean_iso_pre_collapse:.1f}% "
            f"(threshold {_ISOLATION_THRESH}%). Agents on the k=4 grid are too sparse "
            f"for biparental reproduction with parent_radius=3. "
            f"Action: supervisor decision required — expand parent_radius to 5 "
            f"OR cluster initialisation (see diagnostic blueprint §3)."
        )
        action = "escalate:supervisor_required"
    else:
        # N=0 but not obviously Allee — mixed or age-out
        diagnosis = "H_B_partial"
        summary = (
            f"C collapses at all tested p_max (0.03–0.15). Mean pre-collapse isolation "
            f"= {mean_iso_pre_collapse:.1f}% (below Allee threshold {_ISOLATION_THRESH}%). "
            f"Collapse is driven by age-out: initial realistic age distribution depletes "
            f"faster than p_max generates new births. Raising p_max further or adjusting "
            f"the initial age distribution may rescue C. "
            f"Action: flag for Stage 4.5 carrying-cost redesign."
        )
        action = "flag:stage45_carrying_cost"

    return dict(
        diagnosis=diagnosis, summary=summary, action=action,
        survivors=list(survivors.keys()),
        collapses=list(collapses.keys()),
        mean_iso_pre_collapse=round(mean_iso_pre_collapse, 1),
    )


# ─── HTML Report ─────────────────────────────────────────────────────────────

def _pass_cell(ok: bool) -> str:
    return f'<td class="{"pass" if ok else "fail"}">{"✓ PASS" if ok else "FAIL"}</td>'


def _run_table_rows(run_res: dict, label: str) -> str:
    rows = []
    for p, r in sorted(run_res.items()):
        cs = r.get("collapse_step") or "—"
        iso100 = f"{r.get('spat_100', (0,0))[1]:.1f}%" if r.get("spat_100") else "—"
        surv = r.get("survived", False)
        rows.append(
            f"<tr>{_pass_cell(surv)}"
            f"<td>{label}</td>"
            f"<td>{p}</td>"
            f"<td>[{r['n_lo']},{r['n_hi']}]</td>"
            f"<td>{r.get('est_starv',0.0):.3f}</td>"
            f"<td>{iso100}</td>"
            f"<td>{cs}</td></tr>"
        )
    return "\n".join(rows)


def generate_html_report(runA, runB, runC, runD, diagnosis, figs) -> Path:
    print("\n=== Writing report_diag.html ===")

    def _img_section(key, caption=""):
        if key in figs:
            return f'<img src="data:image/png;base64,{figs[key]}" style="max-width:100%;">\n<p class="fig-caption">{caption}</p>'
        return ""

    all_rows = (
        _run_table_rows(runA, "A (bare)") + "\n" +
        _run_table_rows(runB, "B (pool)") + "\n" +
        _run_table_rows(runC, "C (λ)") + "\n" +
        _run_table_rows(runD, "D (pool+λ)")
    )

    verdict_class = "pass" if diagnosis["diagnosis"].startswith("H_B") else "fail"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Stage 4.4 Diagnostic Report</title>
<style>
  body {{font-family: Georgia, serif; max-width: 1100px; margin: auto; padding: 20px;
         line-height: 1.6; color: #222;}}
  h1, h2, h3 {{color: #1a1a6e;}}
  h2 {{border-bottom: 2px solid #1a1a6e; padding-bottom: 4px;}}
  table {{border-collapse: collapse; width: 100%; margin: 12px 0;}}
  th, td {{border: 1px solid #bbb; padding: 6px 10px; text-align: left;}}
  th {{background: #e8e8f8;}}
  tr:nth-child(even) {{background: #f9f9f9;}}
  .pass {{color: green; font-weight: bold;}}
  .fail {{color: #c00;}}
  .verdict {{padding: 14px; border-radius: 4px; margin: 14px 0;
             border: 2px solid;}}
  .verdict.pass {{background: #e8f4e8; border-color: #4a9;}}
  .verdict.fail {{background: #fdf0f0; border-color: #c66;}}
  .fig-caption {{font-size: 0.85em; color: #555; margin-bottom: 16px;}}
  pre {{background: #f4f4f4; padding: 10px; overflow-x: auto; font-size: 0.9em;}}
</style>
</head>
<body>
<h1>Stage 4.4 Diagnostic — C Null Control Failure Analysis</h1>
<p><strong>Seed:</strong> 42 &nbsp;&nbsp;
   <strong>k_grid:</strong> 4 (max_sugar=16, α=4) &nbsp;&nbsp;
   <strong>β_Si:</strong> 5.0 &nbsp;&nbsp;
   <strong>parent_radius:</strong> {_ISOLATION_RADIUS} &nbsp;&nbsp;
   <strong>N target:</strong> [{_N_LO}, {_N_HI}]</p>

<h2>§0 Hypotheses</h2>
<table>
<tr><th>Hypothesis</th><th>Mechanism</th><th>Prediction (Run A)</th></tr>
<tr><td><strong>H_A</strong> — Allee dispersal</td>
    <td>k=4 grid spreads agents; biparental r=3 finds no mates → birth rate → 0</td>
    <td>N=0 at ALL p_max; pct_isolated_C &gt; {_ISOLATION_THRESH}% before collapse</td></tr>
<tr><td><strong>H_B</strong> — p_max under-calibration</td>
    <td>p_max=0.03–0.05 gives birth rate &lt; senescence death rate; agents age out</td>
    <td>N&gt;0 (stable) at p_max ≥ 0.07; collapse step &gt; 500 at low p</td></tr>
<tr><td><strong>H_C</strong> — Pool over-drain</td>
    <td>τ_pool=0.05 extracts surplus, destabilises wealth buffer</td>
    <td>Run A (pool OFF) survives; Run B (pool ON) still collapses</td></tr>
<tr><td><strong>H_D</strong> — λ interaction</td>
    <td>λ boost on declining pop creates pathological feedback</td>
    <td>Run C (λ ON, pool OFF) collapses; Run A (λ=0) survives</td></tr>
</table>

<h2>§1 Spatial density diagnostic (Run A)</h2>
{_img_section("runA_isolated",
    "Figure 1: pct_isolated_C over time for Run A (C bare). "
    f"Orange dashed = {_ISOLATION_THRESH}% Allee threshold. "
    "High isolation before collapse confirms H_A (Allee dispersal).")}
{_img_section("runA_dist",
    "Figure 2: mean_nearest_C_dist over time (Run A). "
    f"Orange dashed = parent_radius={_ISOLATION_RADIUS}. "
    "If mean distance exceeds parent_radius early, mating fails.")}
{_img_section("runA_nt",
    "Figure 3: N(t) for all Run A p_max values. "
    "Red dashed = N gates [150, 400].")}

<h2>§2 Run matrix results</h2>
<table>
<tr><th>Gate</th><th>Run</th><th>p_max</th><th>N_late</th>
    <th>est_starv</th><th>iso@t=100</th><th>collapse_step</th></tr>
{all_rows}
</table>
{_img_section("factorial_N",
    "Figure 4: Mean N at t≥500 by Run × p_max. Bars at 0 = collapsed.")}

<h2>§3 Conclusion</h2>
<div class="verdict {verdict_class}">
<strong>Diagnosis: {diagnosis['diagnosis']}</strong><br>
{diagnosis['summary']}<br><br>
<strong>Pre-collapse mean pct_isolated_C:</strong> {diagnosis['mean_iso_pre_collapse']}%
(threshold for H_A confirmation: {_ISOLATION_THRESH}%)<br>
<strong>Run A survivors:</strong> {diagnosis['survivors'] or 'none'}<br>
<strong>Run A collapses:</strong> {diagnosis['collapses']}
</div>

<h2>§4 Recommended action</h2>
<pre>{diagnosis['action']}</pre>
<p>
{'<strong>H_B confirmed → Stage 4.4 Patch.</strong> '
 'Re-lock p_max_C at the minimum Run A passing value. '
 'Runs B/C/D verify pool and λ do not break the viable p_max. '
 'If pool shifts the viable range: reduce τ_pool in steps of 0.01. '
 'Then re-run Stage 4.4 seasonal sweep with corrected p_max_C.'
 if diagnosis["diagnosis"].startswith("H_B") else
 '<strong>Supervisor decision required.</strong> '
 'H_A (Allee dispersal) confirmed. Two options: '
 '(1) expand parent_radius from 3 → 5 to match k=4 territory scale; '
 '(2) cluster initialisation (C agents seeded in one quadrant). '
 'Do not implement without approval (blueprint §3, option 1 or 2).'}
</p>
</body>
</html>
"""

    report_path = _OUT_ROOT / "report_diag.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"  Report written: {report_path}")
    return report_path


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Stage 4.4 Diagnostic: C Null Control Failure Analysis")
    print("=" * 60)
    _OUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Run A first — determines B/C/D p_max values
    resA = run_A()

    # Determine B/C/D p_max set
    survivors = sorted(p for p, r in resA.items() if r["survived"])
    if survivors:
        # Use 0.03 anchor + two values bracketing the minimum survivor
        best = survivors[0]
        bcd_p = sorted(set([0.03, best, round(best - 0.01, 3), round(best + 0.01, 3)]))
        bcd_p = [p for p in bcd_p if p > 0]
    else:
        # No survivors — use 0.03 anchor + two highest-tested values
        bcd_p = [0.03, 0.07, 0.15]

    resB = run_B(bcd_p)
    resC = run_C(bcd_p)
    resD = run_D([0.03] + ([survivors[0]] if survivors else [0.07]))

    diagnosis = _diagnose(resA)
    print(f"\n  Diagnosis: {diagnosis['diagnosis']}")
    print(f"  {diagnosis['summary']}")

    figs = generate_figures(resA, resB, resC, resD)
    report_path = generate_html_report(resA, resB, resC, resD, diagnosis, figs)

    print("\n" + "=" * 60)
    print("Stage 4.4 Diagnostic complete.")
    print(f"  Report: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
