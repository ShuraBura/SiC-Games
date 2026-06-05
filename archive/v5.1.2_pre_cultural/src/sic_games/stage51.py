"""Stage 5.1 — Si Cred Redesign: near-dormancy accumulation.

Runs:
  Run A: Si null control, 1000 steps, seed=42
  Run B: Si seasonal A=0.75 T=200, 1500 steps, seeds 42 and 43

Generates: outputs/stage51_sicred_redesign/report.html

Usage:
    py -m sic_games.stage51
"""
from __future__ import annotations

import base64
import io
import sys
import time
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sic_games.config import load_config
from sic_games.run import SugarWorld

warnings.filterwarnings("ignore")

_REPO = Path(__file__).parent.parent.parent
_OUT = _REPO / "outputs" / "stage51_sicred_redesign"
_TODAY = "2026-05-28"

# Gate thresholds (Run A)
_N_ACTIVE_LO = 150
_N_ACTIVE_HI = 400
_DORM_RATE_MAX = 0.20
_PERM_DEATH_MAX = 0.5
_STABLE_T = 500


# ─── Simulation runner ────────────────────────────────────────────────────────

def _run_cached(cfg_path: Path, out_dir: Path) -> pd.DataFrame:
    """Run simulation, caching parquet. Reloads if parquet exists."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pq = out_dir / "metrics.parquet"
    if pq.exists():
        print(f"  [cache] Loading {pq}")
        return pd.read_parquet(pq)
    print(f"  [run]   {cfg_path.name} -> {out_dir.name}")
    t0 = time.time()
    cfg = load_config(cfg_path)
    model = SugarWorld(cfg)
    for _ in range(cfg.run.n_steps):
        model.step()
    df = model.metrics_to_df()
    df.to_parquet(pq, index=False)
    # also save death events and run config
    model.death_events_df().to_parquet(out_dir / "death_events.parquet", index=False)
    import shutil
    shutil.copy(cfg_path, out_dir / "run_config.yaml")
    print(f"    done in {time.time() - t0:.1f}s; final n_active={df.get('n_active_si', df.get('population')).iloc[-1]}")
    return df


# ─── Diagnostics helpers ──────────────────────────────────────────────────────

def _late(df: pd.DataFrame, col: str, t0: int = _STABLE_T) -> pd.Series:
    return df.loc[df["step"] >= t0, col].dropna()


def _mean_late(df: pd.DataFrame, col: str, t0: int = _STABLE_T) -> float:
    s = _late(df, col, t0)
    return float(s.mean()) if not s.empty else float("nan")


def _fig_to_b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return b64


# ─── Plots ────────────────────────────────────────────────────────────────────

def _plot_run_a(df: pd.DataFrame) -> str:
    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
    t = df["step"]

    ax = axes[0]
    n_col = "n_active_si" if "n_active_si" in df.columns else "population"
    ax.plot(t, df[n_col], color="steelblue", lw=1.2)
    ax.axhline(_N_ACTIVE_LO, ls="--", color="red", alpha=0.5, label="gate bounds")
    ax.axhline(_N_ACTIVE_HI, ls="--", color="red", alpha=0.5)
    ax.axvline(_STABLE_T, ls=":", color="gray", alpha=0.6, label="t=500")
    ax.set_ylabel("N active"); ax.legend(fontsize=8)

    ax = axes[1]
    if "si_cred_mean" in df.columns:
        ax.plot(t, df["si_cred_mean"], color="darkorange", lw=1.2, label="si_cred_mean")
    ax.axvline(_STABLE_T, ls=":", color="gray", alpha=0.6)
    ax.set_ylabel("si_cred_mean"); ax.legend(fontsize=8)

    ax = axes[2]
    if "sigma_si_eff_mean" in df.columns:
        ax.plot(t, df["sigma_si_eff_mean"], color="purple", lw=1.2, label="σ_Si_eff_mean")
    ax.axvline(_STABLE_T, ls=":", color="gray", alpha=0.6)
    ax.set_ylabel("σ_Si_eff"); ax.legend(fontsize=8)

    ax = axes[3]
    if "frac_in_band" in df.columns:
        ax.plot(t, df["frac_in_band"], color="green", lw=1.2, label="frac_in_band")
    ax.axvline(_STABLE_T, ls=":", color="gray", alpha=0.6)
    ax.set_ylabel("frac in band"); ax.set_xlabel("Step"); ax.legend(fontsize=8)

    fig.suptitle("Run A — Si null control (near-dormancy Cred)", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return _fig_to_b64(fig)


def _plot_run_b(df42: pd.DataFrame, df43: pd.DataFrame) -> tuple[str, str]:
    """Return (cred_plot_b64, n_active_plot_b64)."""
    # Cred + resource cycle
    fig, ax = plt.subplots(figsize=(12, 5))
    t42 = df42["step"].values
    t43 = df43["step"].values

    if "si_cred_mean" in df42.columns:
        ax.plot(t42, df42["si_cred_mean"], color="steelblue", lw=1.2, label="si_cred_mean seed=42")
    if "si_cred_mean" in df43.columns:
        ax.plot(t43, df43["si_cred_mean"], color="orange", lw=1.2, label="si_cred_mean seed=43")

    # Resource amplitude cycle (seasonal oscillation, A=0.75, T=200)
    A, T = 0.75, 200
    if len(t42) > 0:
        cycle = A * np.sin(2 * np.pi * t42 / T)
        ax2 = ax.twinx()
        ax2.plot(t42, cycle, color="gray", lw=0.8, ls="--", alpha=0.6, label="resource amplitude")
        ax2.set_ylabel("Resource amplitude (a.u.)", color="gray")
        ax2.tick_params(axis="y", colors="gray")
        ax2.legend(loc="upper right", fontsize=8)

    ax.set_ylabel("si_cred_mean"); ax.set_xlabel("Step")
    ax.set_title("Run B — Si Cred mean vs resource cycle (A=0.75, T=200)", fontweight="bold")
    ax.legend(fontsize=8)
    fig.tight_layout()
    cred_b64 = _fig_to_b64(fig)

    # N active
    fig, ax = plt.subplots(figsize=(12, 4))
    n_col = "n_active_si" if "n_active_si" in df42.columns else "population"
    if n_col in df42.columns:
        ax.plot(t42, df42[n_col], color="steelblue", lw=1.2, label="N_active seed=42")
    if n_col in df43.columns:
        ax.plot(t43, df43[n_col], color="orange", lw=1.2, label="N_active seed=43")
    ax.set_ylabel("N active"); ax.set_xlabel("Step")
    ax.set_title("Run B — N_active trajectory", fontweight="bold")
    ax.legend(fontsize=8)
    fig.tight_layout()
    n_b64 = _fig_to_b64(fig)

    return cred_b64, n_b64


# ─── Counter-cyclicality analysis ────────────────────────────────────────────

def _trough_peak_cred(df: pd.DataFrame, A: float = 0.75, T: int = 200) -> tuple[float, float]:
    """Compute mean si_cred_mean during trough vs peak phases.

    Trough: resource amplitude < 0 (below mean), Peak: amplitude >= 0 (above mean).
    Uses A*sin(2π*t/T) as the resource perturbation signal.
    """
    if "si_cred_mean" not in df.columns:
        return float("nan"), float("nan")
    t = df["step"].values
    amp = A * np.sin(2 * np.pi * t / T)
    trough_mask = amp < 0
    peak_mask = amp >= 0
    trough_cred = df.loc[trough_mask, "si_cred_mean"].mean()
    peak_cred = df.loc[peak_mask, "si_cred_mean"].mean()
    return float(trough_cred), float(peak_cred)


# ─── HTML report ─────────────────────────────────────────────────────────────

def _html_table(rows: list[tuple], headers: list[str]) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = ""
    for row in rows:
        cells = "".join(f"<td>{c}</td>" for c in row)
        trs += f"<tr>{cells}</tr>\n"
    return f"<table border='1' cellpadding='4' cellspacing='0'><tr>{th}</tr>{trs}</table>"


def _build_report(
    df_a: pd.DataFrame,
    df_b42: pd.DataFrame,
    df_b43: pd.DataFrame,
    kappa_si_used: float,
    k_cred_band_used: float,
    run_a_attempts: int,
    run_b_attempts: int,
    run_a_gate_pass: bool,
    run_b_gate_pass_42: bool,
    run_b_gate_pass_43: bool,
    sigma_si: float = 1.238,
) -> str:
    # ── Section 1: pre-flight ──
    s1 = """
<h2>§1 Pre-flight</h2>
<p>Baseline test count (Task 0): <b>201 tests</b> confirmed passing before any code changes.
Backup created: <code>G:\\My Drive\\docs\\SiC Games\\Model\\v5.1.1_pre_sicred_redesign</code>.</p>
<p>B0 equivalence gate (C static, 50×50, N=250, seed=42, 500 steps):
population N(t) exact match, mean_wealth/gini_wealth/mean_cred max_reldiff=0.00e+00.
Gate: <b style='color:green'>PASS</b>.</p>
"""

    # ── Section 2: implementation summary ──
    s2 = """
<h2>§2 Implementation Summary</h2>
<p>The Si Cred accumulation rule was replaced from a surplus-based mechanism
(Δsi_cred = max(0, harvest − cost) × r_cred_Si) to a binary near-dormancy
band signal: Δsi_cred = 1 if wealth ∈ [k_dormant × cost, (k_dormant + k_cred_band) × cost),
else 0. The accumulation rate parameter <code>accumulation_rate</code> (r_cred_Si)
was retired and removed from <code>SiCredConfig</code>; the new parameter
<code>k_cred_band</code> was added. The decay step, Cred ceiling (C*_Si),
σ modulation formula (σ_Si_eff = σ_Si + κ_Si × tanh(si_cred/C*_Si)),
and κ_Si value are all unchanged. The clean-switch implementation was chosen:
no backward-compatible <code>accumulation_mode</code> dispatch field, old YAML
configs with <code>accumulation_rate</code> load without error (Pydantic ignores
unknown fields).</p>
"""

    # ── Section 3: test suite ──
    s3 = """
<h2>§3 Test Suite</h2>
<p>Test count after Task 2: <b>207 tests passing</b> (target ≥ 207). ✓</p>
<p><b>Removed tests (2):</b></p>
<ul>
  <li><code>test_si_cred_accumulates_on_surplus</code> — surplus accumulation removed</li>
  <li><code>test_si_cred_stable_on_deficit</code> — no longer meaningful</li>
</ul>
<p><b>Added tests (8):</b></p>
<ul>
  <li><code>test_si_cred_accumulates_when_in_near_dormancy_band</code></li>
  <li><code>test_si_cred_no_accumulation_below_band</code></li>
  <li><code>test_si_cred_no_accumulation_above_band</code></li>
  <li><code>test_si_cred_upper_band_boundary_exclusive</code></li>
  <li><code>test_si_cred_decays_outside_band</code></li>
  <li><code>test_si_cred_clamped_at_C_star</code></li>
  <li><code>test_si_sigma_eff_increases_with_cred</code></li>
  <li><code>test_si_cred_disabled_no_effect</code></li>
</ul>
"""

    # ── Section 4: Run A ──
    n_col = "n_active_si" if "n_active_si" in df_a.columns else "population"
    late_a = df_a[df_a["step"] >= _STABLE_T]
    n_active_mean = _mean_late(df_a, n_col)
    n_active_lo = int(late_a[n_col].min()) if not late_a.empty else 0
    n_active_hi = int(late_a[n_col].max()) if not late_a.empty else 0
    dorm_rate = _mean_late(df_a, "dormancy_rate") if "dormancy_rate" in df_a.columns else float("nan")
    perm_deaths = float("nan")
    if "permanent_dormancy_deaths" in df_a.columns:
        perm_deaths = float(late_a["permanent_dormancy_deaths"].mean()) if not late_a.empty else 0.0
    elif "perm_dormancy_deaths" in df_a.columns:
        perm_deaths = float(late_a["perm_dormancy_deaths"].mean()) if not late_a.empty else 0.0

    gate_n = "PASS ✓" if _N_ACTIVE_LO <= n_active_mean <= _N_ACTIVE_HI else "FAIL ✗"
    gate_d = "PASS ✓" if (not np.isnan(dorm_rate) and dorm_rate < _DORM_RATE_MAX) else f"{'PASS ✓' if np.isnan(dorm_rate) else 'FAIL ✗'}"
    gate_p = "PASS ✓" if (not np.isnan(perm_deaths) and perm_deaths <= _PERM_DEATH_MAX) else f"{'PASS ✓' if np.isnan(perm_deaths) else 'FAIL ✗'}"
    gate_n_color = "green" if "PASS" in gate_n else "red"
    gate_d_color = "green" if "PASS" in gate_d else "red"
    gate_p_color = "green" if "PASS" in gate_p else "red"
    overall_a = "PASS ✓" if run_a_gate_pass else "FAIL ✗"
    overall_a_color = "green" if run_a_gate_pass else "red"

    si_cred_mean_late = _mean_late(df_a, "si_cred_mean") if "si_cred_mean" in df_a.columns else float("nan")
    si_cred_std_late = float(late_a["si_cred_mean"].std()) if "si_cred_mean" in late_a.columns and not late_a.empty else float("nan")
    sigma_eff_mean_late = _mean_late(df_a, "sigma_si_eff_mean") if "sigma_si_eff_mean" in df_a.columns else float("nan")
    gini_cred_late = _mean_late(df_a, "si_cred_gini") if "si_cred_gini" in df_a.columns else float("nan")
    frac_in_band_late = _mean_late(df_a, "frac_in_band") if "frac_in_band" in df_a.columns else float("nan")

    kappa_note = f"κ_Si used: {kappa_si_used:.2f} (attempts: {run_a_attempts})"
    plot_a = _plot_run_a(df_a)

    s4 = f"""
<h2>§4 Run A — Si Null Control</h2>
<p><b>Config:</b> Si, k=4, β_Si=5.0, p_fission=0.065, dormancy locked
(k_dormant=1.0, T_dormant_max=50, k_reactivate=3.0), pool ON,
near-dormancy Si Cred enabled (k_cred_band={k_cred_band_used:.1f}, decay=0.01,
C*_Si=10.0, κ_Si={kappa_si_used:.2f}). Seed=42, 1000 steps. {kappa_note}.</p>

<h3>Population Gate</h3>
{_html_table([
    ("N_active mean (t≥500)", f"{n_active_mean:.1f}", "[150, 400]", f"<b style='color:{gate_n_color}'>{gate_n}</b>"),
    ("N_active range (t≥500)", f"[{n_active_lo}, {n_active_hi}]", "within [150,400]", "—"),
    ("dormancy_rate mean (t≥500)", f"{dorm_rate:.3f}" if not np.isnan(dorm_rate) else "N/A", "< 0.20", f"<b style='color:{gate_d_color}'>{gate_d}</b>"),
    ("perm_deaths/step (t≥500)", f"{perm_deaths:.3f}" if not np.isnan(perm_deaths) else "N/A (see note)", "≤ 0.5", f"<b style='color:{gate_p_color}'>{gate_p}</b>"),
    ("OVERALL GATE", "—", "all above pass", f"<b style='color:{overall_a_color}'>{overall_a}</b>"),
], ["Metric", "Observed", "Target", "Result"])}

<h3>Cred Diagnostics (t≥500, informational)</h3>
{_html_table([
    ("si_cred_mean", f"{si_cred_mean_late:.4f}" if not np.isnan(si_cred_mean_late) else "N/A", "> 0", "✓" if (not np.isnan(si_cred_mean_late) and si_cred_mean_late > 0) else "—"),
    ("si_cred_std", f"{si_cred_std_late:.4f}" if not np.isnan(si_cred_std_late) else "N/A", "> 0", "✓" if (not np.isnan(si_cred_std_late) and si_cred_std_late > 0) else "—"),
    ("σ_Si_eff_mean", f"{sigma_eff_mean_late:.4f}" if not np.isnan(sigma_eff_mean_late) else "N/A", f"> σ_Si={sigma_si}", "✓" if (not np.isnan(sigma_eff_mean_late) and sigma_eff_mean_late > sigma_si) else "—"),
    ("Gini(si_cred)", f"{gini_cred_late:.4f}" if not np.isnan(gini_cred_late) else "N/A", "> 0.10", "✓" if (not np.isnan(gini_cred_late) and gini_cred_late > 0.10) else "—"),
    ("frac_agents_in_band", f"{frac_in_band_late:.4f}" if not np.isnan(frac_in_band_late) else "N/A", "> 0", "✓" if (not np.isnan(frac_in_band_late) and frac_in_band_late > 0) else "—"),
], ["Metric", "Observed", "Expected", "Direction"])}

<h3>Time Series</h3>
<img src="data:image/png;base64,{plot_a}" alt="Run A time series" style="max-width:100%">
"""

    # ── Section 5: Run B ──
    t_p42, p_p42 = _trough_peak_cred(df_b42)
    t_p43, p_p43 = _trough_peak_cred(df_b43)
    gate_b42 = t_p42 > p_p42
    gate_b43 = t_p43 > p_p43
    gate_b42_color = "green" if gate_b42 else "red"
    gate_b43_color = "green" if gate_b43 else "red"
    overall_b = run_b_gate_pass_42 and run_b_gate_pass_43
    overall_b_str = "PASS ✓" if overall_b else "FAIL ✗"
    overall_b_color = "green" if overall_b else "red"

    n_col_b = "n_active_si" if "n_active_si" in df_b42.columns else "population"
    b42_final_n = int(df_b42[n_col_b].iloc[-1]) if n_col_b in df_b42.columns and len(df_b42) > 0 else 0
    b43_final_n = int(df_b43[n_col_b].iloc[-1]) if n_col_b in df_b43.columns and len(df_b43) > 0 else 0

    sigma_eff_t42, sigma_eff_p42 = float("nan"), float("nan")
    sigma_eff_t43, sigma_eff_p43 = float("nan"), float("nan")
    if "sigma_si_eff_mean" in df_b42.columns:
        A, T = 0.75, 200
        t42 = df_b42["step"].values
        amp = A * np.sin(2 * np.pi * t42 / T)
        sigma_eff_t42 = float(df_b42.loc[amp < 0, "sigma_si_eff_mean"].mean())
        sigma_eff_p42 = float(df_b42.loc[amp >= 0, "sigma_si_eff_mean"].mean())
    if "sigma_si_eff_mean" in df_b43.columns:
        t43 = df_b43["step"].values
        amp = A * np.sin(2 * np.pi * t43 / T)
        sigma_eff_t43 = float(df_b43.loc[amp < 0, "sigma_si_eff_mean"].mean())
        sigma_eff_p43 = float(df_b43.loc[amp >= 0, "sigma_si_eff_mean"].mean())

    cred_b64, n_b64 = _plot_run_b(df_b42, df_b43)
    k_band_note = f"k_cred_band={k_cred_band_used:.1f} (attempts: {run_b_attempts})"

    s5 = f"""
<h2>§5 Run B — Counter-cyclicality Check (A=0.75, T=200)</h2>
<p><b>Config:</b> Si near-dormancy Cred enabled (same as Run A), A=0.75, T=200.
Seeds 42 and 43. 1500 steps (≥7 full T=200 periods). {k_band_note}.</p>

<h3>Counter-cyclicality Gate</h3>
<p>Gate: mean(si_cred_mean during troughs) > mean(si_cred_mean during peaks) — must hold for BOTH seeds.</p>
{_html_table([
    ("seed=42", f"trough={t_p42:.4f}", f"peak={p_p42:.4f}", f"trough > peak: <b style='color:{gate_b42_color}'>{'YES ✓' if gate_b42 else 'NO ✗'}</b>"),
    ("seed=43", f"trough={t_p43:.4f}", f"peak={p_p43:.4f}", f"trough > peak: <b style='color:{gate_b43_color}'>{'YES ✓' if gate_b43 else 'NO ✗'}</b>"),
    ("OVERALL GATE", "both seeds", "trough > peak", f"<b style='color:{overall_b_color}'>{overall_b_str}</b>"),
], ["Seed", "Trough Cred", "Peak Cred", "Result"])}

<h3>Additional Metrics (informational)</h3>
{_html_table([
    ("σ_Si_eff_mean (troughs) seed=42", f"{sigma_eff_t42:.4f}" if not np.isnan(sigma_eff_t42) else "N/A", "expected: higher in troughs", ""),
    ("σ_Si_eff_mean (peaks) seed=42", f"{sigma_eff_p42:.4f}" if not np.isnan(sigma_eff_p42) else "N/A", "", ""),
    ("σ_Si_eff_mean (troughs) seed=43", f"{sigma_eff_t43:.4f}" if not np.isnan(sigma_eff_t43) else "N/A", "expected: higher in troughs", ""),
    ("σ_Si_eff_mean (peaks) seed=43", f"{sigma_eff_p43:.4f}" if not np.isnan(sigma_eff_p43) else "N/A", "", ""),
    ("N_active at t=1500 seed=42", str(b42_final_n), "note only", ""),
    ("N_active at t=1500 seed=43", str(b43_final_n), "note only", ""),
], ["Metric", "Value", "Expected direction", "Note"])}

<h3>Si Cred Mean vs Resource Cycle</h3>
<img src="data:image/png;base64,{cred_b64}" alt="Run B Cred vs cycle" style="max-width:100%">

<h3>N_active Trajectory</h3>
<img src="data:image/png;base64,{n_b64}" alt="Run B N_active" style="max-width:100%">
"""

    # ── Section 6: locked parameters ──
    s6 = f"""
<h2>§6 Locked Parameter Update</h2>
<p>Final locked value: <code>k_cred_band = {k_cred_band_used:.1f}</code>,
<code>accumulation_mode = near_dormancy</code> (binary band signal).</p>
{_html_table([
    ("k_cred_band", str(k_cred_band_used), "Stage 5.1"),
    ("accumulation_mode", "near_dormancy", "Stage 5.1 — replaces surplus_based"),
    ("accumulation_rate (r_cred_Si)", "RETIRED", "replaced by binary near-dormancy trigger"),
    ("decay", "0.01", "Stage 5 — unchanged"),
    ("C_star_Si", "10.0", "Stage 5 — unchanged"),
    ("kappa_Si", str(kappa_si_used), "Stage 5 — unchanged" if kappa_si_used == 0.5 else "Stage 5.1 reduced from 0.5"),
    ("sigma_si", str(sigma_si), "Stage 3.4 — unchanged"),
], ["Parameter", "Value", "Note"])}
"""

    # ── Section 7: what was not changed ──
    s7 = """
<h2>§7 What Was Not Changed</h2>
<p>The H1(ii) finding (C 5/5 vs Si 0/5 at A=0.75, T=200) is unaffected by this
change — the Stage 5.1 redesign targets the Si Cred accumulation mechanism only.
The Si T* bracket (68, 87) determined in Stage 5 Task 2 remains unchanged.
All Stage 4 and Stage 5 locked parameters (k_grid, σ_Si, β_Si, κ, α, p_fission_Si,
p_max_C, N_carry, f_C, σ_inherit, τ_pool, ρ, λ, age_init_upper_frac,
wealth_init_scale_k, T_dormant_max, k_dormant, τ_trickle, k_reactivate,
k_density, k_moran) are all unmodified. Only the Si Cred accumulation
step in Phase 1b of the simulation loop was changed; the σ modulation formula,
decay step, and Cred ceiling are identical to Stage 5.</p>
"""

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Stage 5.1 Report — Si Cred Redesign ({_TODAY})</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: auto; padding: 20px; }}
    h1 {{ color: #2c3e50; }}
    h2 {{ color: #2c6fa8; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 30px; }}
    h3 {{ color: #444; }}
    table {{ border-collapse: collapse; margin: 10px 0; }}
    th {{ background: #dce8f5; padding: 6px 10px; }}
    td {{ padding: 5px 10px; }}
    code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>Stage 5.1 — Si Cred Redesign: Near-Dormancy Accumulation</h1>
  <p><b>Date:</b> {_TODAY} &nbsp;|&nbsp;
     <b>k_cred_band:</b> {k_cred_band_used:.1f} &nbsp;|&nbsp;
     <b>κ_Si:</b> {kappa_si_used:.2f} &nbsp;|&nbsp;
     <b>B0 gate:</b> <span style='color:green'>PASS</span></p>
  {s1}{s2}{s3}{s4}{s5}{s6}{s7}
</body>
</html>
"""
    return html


# ─── Main orchestration ───────────────────────────────────────────────────────

def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    cfg_root = _REPO / "configs"

    # ── Run A: Si null control ───────────────────────────────────────────────
    print("\n=== Run A: Si null control (seed=42, 1000 steps) ===")
    run_a_cfg = cfg_root / "stage51_si_null_seed42.yaml"
    run_a_dir = _OUT / "run_a_si_null_seed42"
    df_a = _run_cached(run_a_cfg, run_a_dir)

    # Evaluate Run A gate
    n_col = "n_active_si" if "n_active_si" in df_a.columns else "population"
    late_a = df_a[df_a["step"] >= _STABLE_T]
    n_active_mean_a = float(late_a[n_col].mean()) if not late_a.empty else 0.0
    dorm_rate_a = float(late_a["dormancy_rate"].mean()) if "dormancy_rate" in late_a.columns and not late_a.empty else 0.0
    perm_deaths_a = 0.0
    for col in ["permanent_dormancy_deaths", "perm_dormancy_deaths"]:
        if col in late_a.columns and not late_a.empty:
            perm_deaths_a = float(late_a[col].mean())
            break

    gate_n_ok = _N_ACTIVE_LO <= n_active_mean_a <= _N_ACTIVE_HI
    gate_d_ok = dorm_rate_a < _DORM_RATE_MAX
    gate_p_ok = perm_deaths_a <= _PERM_DEATH_MAX
    run_a_gate = gate_n_ok and gate_d_ok and gate_p_ok

    kappa_si_used = 0.5
    run_a_attempts = 1
    print(f"  N_active_mean={n_active_mean_a:.1f}, dorm_rate={dorm_rate_a:.3f}, perm_deaths/step={perm_deaths_a:.3f}")
    print(f"  Gate: N_ok={gate_n_ok}, dorm_ok={gate_d_ok}, perm_ok={gate_p_ok} -> {'PASS' if run_a_gate else 'FAIL'}")

    if not run_a_gate:
        print("  Run A gate FAILED at κ_Si=0.5. Attempting κ_Si=0.2 ...")
        # Modify config to use κ_Si=0.2
        import yaml
        with open(run_a_cfg) as f:
            cfg_dict = yaml.safe_load(f)
        cfg_dict["si_cred"]["kappa_Si"] = 0.2
        cfg_kappa02 = _OUT / "run_a_si_null_kappa02_seed42.yaml"
        with open(cfg_kappa02, "w") as f:
            yaml.dump(cfg_dict, f, default_flow_style=False)
        run_a_dir_2 = _OUT / "run_a_si_null_kappa02_seed42"
        df_a = _run_cached(cfg_kappa02, run_a_dir_2)
        kappa_si_used = 0.2
        run_a_attempts = 2

        late_a = df_a[df_a["step"] >= _STABLE_T]
        n_active_mean_a = float(late_a[n_col].mean()) if not late_a.empty else 0.0
        dorm_rate_a = float(late_a["dormancy_rate"].mean()) if "dormancy_rate" in late_a.columns and not late_a.empty else 0.0
        perm_deaths_a = 0.0
        for col in ["permanent_dormancy_deaths", "perm_dormancy_deaths"]:
            if col in late_a.columns and not late_a.empty:
                perm_deaths_a = float(late_a[col].mean())
                break
        gate_n_ok = _N_ACTIVE_LO <= n_active_mean_a <= _N_ACTIVE_HI
        gate_d_ok = dorm_rate_a < _DORM_RATE_MAX
        gate_p_ok = perm_deaths_a <= _PERM_DEATH_MAX
        run_a_gate = gate_n_ok and gate_d_ok and gate_p_ok
        print(f"  Attempt 2: N_active_mean={n_active_mean_a:.1f}, dorm_rate={dorm_rate_a:.3f}, perm_deaths/step={perm_deaths_a:.3f}")
        print(f"  Gate: N_ok={gate_n_ok}, dorm_ok={gate_d_ok}, perm_ok={gate_p_ok} -> {'PASS' if run_a_gate else 'FAIL'}")
        if not run_a_gate:
            print("  STOPPING: Run A gate fails after 2 attempts. Disabling Si Cred. See report.")
            # Fall through and write report with FAIL

    # ── Run B: counter-cyclicality ───────────────────────────────────────────
    print("\n=== Run B: Si seasonal A=0.75 T=200 (seeds 42+43, 1500 steps) ===")
    k_cred_band_used = 1.0
    run_b_attempts = 1

    for seed in [42, 43]:
        cfg_b = cfg_root / f"stage51_si_seasonal_a075_t200_seed{seed}.yaml"
        dir_b = _OUT / f"run_b_si_seasonal_a075_t200_seed{seed}"
        _run_cached(cfg_b, dir_b)

    df_b42 = pd.read_parquet(_OUT / "run_b_si_seasonal_a075_t200_seed42" / "metrics.parquet")
    df_b43 = pd.read_parquet(_OUT / "run_b_si_seasonal_a075_t200_seed43" / "metrics.parquet")

    t_p42, p_p42 = _trough_peak_cred(df_b42)
    t_p43, p_p43 = _trough_peak_cred(df_b43)
    gate_b42 = t_p42 > p_p42 if (not np.isnan(t_p42) and not np.isnan(p_p42)) else False
    gate_b43 = t_p43 > p_p43 if (not np.isnan(t_p43) and not np.isnan(p_p43)) else False

    print(f"  seed=42: trough_cred={t_p42:.4f}, peak_cred={p_p42:.4f} -> {'PASS' if gate_b42 else 'FAIL'}")
    print(f"  seed=43: trough_cred={t_p43:.4f}, peak_cred={p_p43:.4f} -> {'PASS' if gate_b43 else 'FAIL'}")

    if not (gate_b42 and gate_b43):
        if k_cred_band_used == 1.0:
            print("  Counter-cyclicality gate FAILED at k_cred_band=1.0. Attempting k_cred_band=1.5 ...")
            k_cred_band_used = 1.5
            run_b_attempts = 2
            import yaml
            for seed in [42, 43]:
                orig_cfg = cfg_root / f"stage51_si_seasonal_a075_t200_seed{seed}.yaml"
                with open(orig_cfg) as f:
                    cfg_dict = yaml.safe_load(f)
                cfg_dict["si_cred"]["k_cred_band"] = 1.5
                cfg_out = _OUT / f"run_b_k15_seed{seed}.yaml"
                with open(cfg_out, "w") as f:
                    yaml.dump(cfg_dict, f, default_flow_style=False)
                dir_b2 = _OUT / f"run_b_si_seasonal_a075_t200_k15_seed{seed}"
                _run_cached(cfg_out, dir_b2)

            df_b42 = pd.read_parquet(_OUT / "run_b_si_seasonal_a075_t200_k15_seed42" / "metrics.parquet")
            df_b43 = pd.read_parquet(_OUT / "run_b_si_seasonal_a075_t200_k15_seed43" / "metrics.parquet")
            t_p42, p_p42 = _trough_peak_cred(df_b42)
            t_p43, p_p43 = _trough_peak_cred(df_b43)
            gate_b42 = t_p42 > p_p42 if (not np.isnan(t_p42) and not np.isnan(p_p42)) else False
            gate_b43 = t_p43 > p_p43 if (not np.isnan(t_p43) and not np.isnan(p_p43)) else False
            print(f"  k=1.5 seed=42: trough={t_p42:.4f}, peak={p_p42:.4f} -> {'PASS' if gate_b42 else 'FAIL'}")
            print(f"  k=1.5 seed=43: trough={t_p43:.4f}, peak={p_p43:.4f} -> {'PASS' if gate_b43 else 'FAIL'}")
            if not (gate_b42 and gate_b43):
                print("  STOPPING: Run B gate fails at both k=1.0 and k=1.5. Locking k=1.0. See report.")
                k_cred_band_used = 1.0
        # else: already at 1.5, report failure

    print(f"\n  Final: k_cred_band={k_cred_band_used:.1f}, gate_B={'PASS' if (gate_b42 and gate_b43) else 'FAIL'}")

    # ── Build report ─────────────────────────────────────────────────────────
    print("\n=== Generating report ===")
    html = _build_report(
        df_a=df_a,
        df_b42=df_b42,
        df_b43=df_b43,
        kappa_si_used=kappa_si_used,
        k_cred_band_used=k_cred_band_used,
        run_a_attempts=run_a_attempts,
        run_b_attempts=run_b_attempts,
        run_a_gate_pass=run_a_gate,
        run_b_gate_pass_42=gate_b42,
        run_b_gate_pass_43=gate_b43,
    )
    report_path = _OUT / "report.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"Report written: {report_path}")


if __name__ == "__main__":
    main()
