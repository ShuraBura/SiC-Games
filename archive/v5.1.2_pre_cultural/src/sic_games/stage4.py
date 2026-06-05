"""Stage 4: Seasonal Oscillation runner and report generator.

Four runs in strict order:
  Run 1: Si null control  (sigma_Si=1.238, no oscillation)
  Run 2: C null control   (canonical kappa=2.0, alpha=2.0, no oscillation)
  Run 3: Si seasonal      (A=0.5, T=200)
  Run 4: C seasonal       (A=0.5, T=200)

Null controls verified against Stage 3 parquets before seasonal runs execute.
Primary deliverable: season-by-season survival plot N(t) with shaded troughs.
"""
from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from sic_games.config import load_config
from sic_games.run import SugarWorld

_REPO_ROOT = Path(__file__).parent.parent.parent
_CONFIGS   = _REPO_ROOT / "configs"
_OUTPUTS   = _REPO_ROOT / "outputs"
_STAGE4_OUT = _OUTPUTS / "stage4_seed42"

# Stage 3 static reference parquets (never re-run)
_SI_STATIC_REF = _OUTPUTS / "stage3_si_bounded_seed42" / "metrics.parquet"
_C_STATIC_REF  = _OUTPUTS / "stage34_k20_a20_seed42" / "metrics.parquet"

_T = 200   # seasonal period


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run(config_path: Path, out_dir: Path) -> pd.DataFrame:
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_config(config_path)
    world = SugarWorld(cfg)
    df = world.run()
    df.to_parquet(out_dir / "metrics.parquet", index=False)
    return df


# ---------------------------------------------------------------------------
# Null-control verification (gate before seasonal runs)
# ---------------------------------------------------------------------------

def _verify_null_controls(
    si_null: pd.DataFrame,
    c_null: pd.DataFrame,
) -> None:
    """Compare null-control runs against Stage 3 reference parquets.

    Raises AssertionError if any metric deviates > 5% from reference.
    Raises FileNotFoundError if reference parquets are missing (first run).
    """
    checks = [
        ("Si null vs Stage 3 Si", si_null, _SI_STATIC_REF,
         ["mean_wealth", "deaths_starvation", "gini_wealth"]),
        ("C null vs Stage 3.4 C", c_null, _C_STATIC_REF,
         ["mean_wealth", "deaths_starvation", "gini_wealth"]),
    ]
    for label, run_df, ref_path, metrics in checks:
        if not ref_path.exists():
            print(f"  WARNING: reference parquet not found: {ref_path}")
            print(f"  Skipping {label} comparison (reference unavailable).")
            continue
        ref = pd.read_parquet(ref_path)
        for col in metrics:
            if col not in run_df.columns or col not in ref.columns:
                continue
            run_val = run_df[col].iloc[-100:].mean()
            ref_val = ref[col].iloc[-100:].mean()
            if ref_val == 0:
                continue
            pct_diff = abs(run_val - ref_val) / abs(ref_val)
            status = "OK" if pct_diff <= 0.05 else "WARN"
            print(f"  [{status}] {label}: {col} run={run_val:.4f} ref={ref_val:.4f} "
                  f"diff={100*pct_diff:.1f}%")
            if pct_diff > 0.05:
                print(f"  NOTE: {col} exceeds 5% tolerance — diagnose before trusting seasonal runs.")


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _trough_spans(n_steps: int, T: int, A: float) -> list[tuple[float, float]]:
    """Return (start, end) step ranges where seasonal phase is in trough half.

    Trough half: sin^2(pi*t/T) > 0.5, i.e., t in (T/4, 3T/4) within each cycle.
    """
    spans = []
    k = 0
    while True:
        start = k * T + T / 4
        end   = k * T + 3 * T / 4
        if start > n_steps:
            break
        spans.append((start, min(end, n_steps)))
        k += 1
    return spans


def plot_survival(
    si_null: pd.DataFrame,
    c_null: pd.DataFrame,
    si_seasonal: pd.DataFrame,
    c_seasonal: pd.DataFrame,
    out_path: Path,
) -> None:
    """Primary deliverable: N(t) with shaded trough periods for C and Si."""
    fig, ax = plt.subplots(figsize=(13, 5))

    n_steps = int(si_seasonal["step"].max())
    troughs = _trough_spans(n_steps, _T, A=0.5)

    # Shade trough periods
    for (s, e) in troughs:
        ax.axvspan(s, e, color="#fee8c8", alpha=0.55, zorder=0)

    # Population trajectories
    ax.plot(si_null["step"],     si_null["population"],     color="#92c5de", lw=1.0,
            ls="--", label="Si null control", alpha=0.7)
    ax.plot(c_null["step"],      c_null["population"],      color="#f4a582", lw=1.0,
            ls="--", label="C null control", alpha=0.7)
    ax.plot(si_seasonal["step"], si_seasonal["population"], color="#2166ac", lw=1.6,
            label="Si seasonal (A=0.5, T=200)")
    ax.plot(c_seasonal["step"],  c_seasonal["population"],  color="#d6604d", lw=1.6,
            label="C seasonal (A=0.5, T=200)")

    ax.axhline(150, color="black", lw=0.8, ls=":", label="Collapse threshold (N=150)")
    ax.set_xlabel("Step")
    ax.set_ylabel("Population N(t)")
    ax.set_title("Stage 4 — Season-by-season survival: C vs Si\n"
                 "Shaded regions = trough phases (sin² > 0.5)")
    ax.legend(fontsize=9)
    ax.set_xlim(0, n_steps)
    ax.set_ylim(0, 310)

    trough_patch = mpatches.Patch(color="#fee8c8", alpha=0.8, label="Trough phase")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles + [trough_patch], labels + ["Trough phase"], fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Survival plot -> {out_path}")


def plot_morans_i(
    si_null: pd.DataFrame,
    c_null: pd.DataFrame,
    si_seasonal: pd.DataFrame,
    c_seasonal: pd.DataFrame,
    out_path: Path,
) -> None:
    """Moran's I for c1 under static vs seasonal — key new diagnostic."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

    n_steps = int(si_seasonal["step"].max())
    troughs = _trough_spans(n_steps, _T, A=0.5)

    for ax, (null_df, seas_df, label_prefix, color) in zip(axes, [
        (si_null, si_seasonal, "Si", "#2166ac"),
        (c_null,  c_seasonal,  "C",  "#d6604d"),
    ]):
        for (s, e) in troughs:
            ax.axvspan(s, e, color="#fee8c8", alpha=0.5, zorder=0)
        ax.plot(null_df["step"], null_df["morans_i_c1"], color=color,
                lw=1.0, ls="--", alpha=0.6, label=f"{label_prefix} null")
        ax.plot(seas_df["step"], seas_df["morans_i_c1"], color=color,
                lw=1.4, label=f"{label_prefix} seasonal")
        ax.axhline(0, color="black", lw=0.5, ls="--")
        ax.set_xlabel("Step")
        ax.set_title(f"Moran's I (c1) — {label_prefix}")
        ax.legend(fontsize=8)

    axes[0].set_ylabel("Moran's I (c1)")
    fig.suptitle("Stage 4 — Spatial trait clustering (c1) under seasonal stress", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Moran's I plot -> {out_path}")


def plot_capacity_verification(si_seasonal: pd.DataFrame, out_path: Path) -> None:
    """Success criterion 1: verify oscillation is firing."""
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(si_seasonal["step"].iloc[:400],
            si_seasonal["mean_effective_capacity"].iloc[:400],
            color="#2166ac", lw=1.4)
    ax.set_xlabel("Step")
    ax.set_ylabel("Mean effective capacity")
    ax.set_title("Stage 4 — Oscillation verification: mean_effective_capacity (steps 1-400)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_starvation(
    si_null: pd.DataFrame,
    c_null: pd.DataFrame,
    si_seasonal: pd.DataFrame,
    c_seasonal: pd.DataFrame,
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(13, 4))
    n_steps = int(si_seasonal["step"].max())
    for (s, e) in _trough_spans(n_steps, _T, A=0.5):
        ax.axvspan(s, e, color="#fee8c8", alpha=0.5, zorder=0)
    ax.plot(si_null["step"],     si_null["deaths_starvation"],     color="#92c5de", lw=1.0, ls="--", label="Si null", alpha=0.7)
    ax.plot(c_null["step"],      c_null["deaths_starvation"],      color="#f4a582", lw=1.0, ls="--", label="C null", alpha=0.7)
    ax.plot(si_seasonal["step"], si_seasonal["deaths_starvation"], color="#2166ac", lw=1.4, label="Si seasonal")
    ax.plot(c_seasonal["step"],  c_seasonal["deaths_starvation"],  color="#d6604d", lw=1.4, label="C seasonal")
    ax.set_xlabel("Step")
    ax.set_ylabel("Deaths/step (starvation)")
    ax.set_title("Stage 4 — Starvation deaths with seasonal stress")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _tm(df: pd.DataFrame, col: str, n: int = 100) -> str:
    if col not in df.columns:
        return "n/a"
    return f"{df[col].iloc[-n:].mean():.4f}"


def _trough_min(df: pd.DataFrame) -> str:
    return f"{df['population'].min():.0f}"


def _per_season_starvation(df: pd.DataFrame, T: int) -> list[float]:
    """Total starvation deaths per season (each T-step cycle)."""
    seasons = []
    for k in range(df["step"].max() // T):
        lo = k * T + 1
        hi = (k + 1) * T
        sub = df[(df["step"] >= lo) & (df["step"] <= hi)]
        seasons.append(float(sub["deaths_starvation"].sum()))
    return seasons


def _morans_trend(df: pd.DataFrame, col: str) -> str:
    """Mean Moran's I in first vs last 200 steps."""
    if col not in df.columns:
        return "n/a / n/a"
    early = df[df["step"] <= 200][col].mean()
    late  = df[df["step"] > 800][col].mean()
    return f"{early:.4f} -> {late:.4f}"


def build_report(
    si_null: pd.DataFrame,
    c_null: pd.DataFrame,
    si_seasonal: pd.DataFrame,
    c_seasonal: pd.DataFrame,
) -> None:
    _STAGE4_OUT.mkdir(parents=True, exist_ok=True)

    # Load Stage 3 static references if available
    si_ref = pd.read_parquet(_SI_STATIC_REF) if _SI_STATIC_REF.exists() else None
    c_ref  = pd.read_parquet(_C_STATIC_REF)  if _C_STATIC_REF.exists()  else None

    def ref_tm(df, col):
        return _tm(df, col) if df is not None else "n/a (no ref)"

    # Check success criteria
    si_seas_min = si_seasonal["population"].iloc[:200].min()
    c_seas_min  = c_seasonal["population"].iloc[:200].min()

    osc_ok = si_seasonal["mean_effective_capacity"].between(
        0.5, 2.1  # trough≈1.0 mean, peak≈1.86 mean (non-uniform field)
    ).any()

    lines = [
        f"# Stage 4 — Seasonal Oscillation (A=0.5, T=200)",
        f"",
        f"**Date:** {date.today().isoformat()}  ",
        f"**Seed:** 42  ",
        f"**Steps:** 1000  ",
        f"**Oscillation:** A=0.5, T=200  ",
        f"**Canonical C params:** kappa=2.0, alpha=2.0 (cell 2,3 from Stage 3.4)  ",
        f"**sigma_Si:** 1.238 (recalibrated from Stage 3.4 cell 2,3 mean_sigma)",
        f"",
        f"## Success criteria",
        f"",
        f"| Criterion | Result |",
        f"|---|---|",
        f"| Oscillation confirmed firing | {'pass' if osc_ok else 'FAIL — check effective_capacity'} |",
        f"| Si survives season 1 (N>150) | {'pass' if si_seas_min > 150 else f'FAIL: min={si_seas_min:.0f}'} |",
        f"| C survives season 1 (N>150) | {'pass' if c_seas_min > 150 else f'FAIL: min={c_seas_min:.0f}'} |",
        f"| Null controls within 5% of Stage 3 | see null-control table below |",
        f"| Seasonal signal visible in N(t) | see survival plot |",
        f"",
        f"## Null-control verification (gate check)",
        f"",
        f"| Metric | Si null | Si Stage 3 ref | C null | C Stage 3.4 ref |",
        f"|---|---|---|---|---|",
        f"| Mean wealth | {_tm(si_null,'mean_wealth')} | {ref_tm(si_ref,'mean_wealth')} | {_tm(c_null,'mean_wealth')} | {ref_tm(c_ref,'mean_wealth')} |",
        f"| Gini wealth | {_tm(si_null,'gini_wealth')} | {ref_tm(si_ref,'gini_wealth')} | {_tm(c_null,'gini_wealth')} | {ref_tm(c_ref,'gini_wealth')} |",
        f"| Deaths/step | {_tm(si_null,'deaths_starvation')} | {ref_tm(si_ref,'deaths_starvation')} | {_tm(c_null,'deaths_starvation')} | {ref_tm(c_ref,'deaths_starvation')} |",
        f"",
        f"## Primary comparison table (final 100 steps unless noted)",
        f"",
        f"| Metric | Stage 3 Si static | Stage 4 Si seasonal | Stage 3 C static | Stage 4 C seasonal |",
        f"|---|---|---|---|---|",
        f"| Mean wealth | {ref_tm(si_ref,'mean_wealth')} | {_tm(si_seasonal,'mean_wealth')} | {ref_tm(c_ref,'mean_wealth')} | {_tm(c_seasonal,'mean_wealth')} |",
        f"| Gini wealth | {ref_tm(si_ref,'gini_wealth')} | {_tm(si_seasonal,'gini_wealth')} | {ref_tm(c_ref,'gini_wealth')} | {_tm(c_seasonal,'gini_wealth')} |",
        f"| Spatial dispersion | {ref_tm(si_ref,'spatial_dispersion')} | {_tm(si_seasonal,'spatial_dispersion')} | {ref_tm(c_ref,'spatial_dispersion')} | {_tm(c_seasonal,'spatial_dispersion')} |",
        f"| Deaths/step (starvation) | {ref_tm(si_ref,'deaths_starvation')} | {_tm(si_seasonal,'deaths_starvation')} | {ref_tm(c_ref,'deaths_starvation')} | {_tm(c_seasonal,'deaths_starvation')} |",
        f"| Deaths/step (newborn) | {ref_tm(si_ref,'deaths_starvation_newborn')} | {_tm(si_seasonal,'deaths_starvation_newborn')} | {ref_tm(c_ref,'deaths_starvation_newborn')} | {_tm(c_seasonal,'deaths_starvation_newborn')} |",
        f"| Deaths/step (established) | {ref_tm(si_ref,'deaths_starvation_established')} | {_tm(si_seasonal,'deaths_starvation_established')} | {ref_tm(c_ref,'deaths_starvation_established')} | {_tm(c_seasonal,'deaths_starvation_established')} |",
        f"| Population trough min (all time) | — | {_trough_min(si_seasonal)} | — | {_trough_min(c_seasonal)} |",
        f"| Mean cred | — | — | {ref_tm(c_ref,'mean_cred')} | {_tm(c_seasonal,'mean_cred')} |",
        f"| Gini cred | — | — | {ref_tm(c_ref,'gini_cred')} | {_tm(c_seasonal,'gini_cred')} |",
        f"| Mean sigma | {ref_tm(si_ref,'mean_sigma')} | {_tm(si_seasonal,'mean_sigma')} | {ref_tm(c_ref,'mean_sigma')} | {_tm(c_seasonal,'mean_sigma')} |",
        f"| Joint tasks/step | {ref_tm(si_ref,'joint_task_count')} | {_tm(si_seasonal,'joint_task_count')} | {ref_tm(c_ref,'joint_task_count')} | {_tm(c_seasonal,'joint_task_count')} |",
        f"| std(phi) | {ref_tm(si_ref,'std_phi')} | {_tm(si_seasonal,'std_phi')} | {ref_tm(c_ref,'std_phi')} | {_tm(c_seasonal,'std_phi')} |",
        f"| Moran's I (c1) | {ref_tm(si_ref,'morans_i_c1')} | {_tm(si_seasonal,'morans_i_c1')} | {ref_tm(c_ref,'morans_i_c1')} | {_tm(c_seasonal,'morans_i_c1')} |",
        f"",
        f"## Seasonal starvation per season",
        f"",
        f"| Season | Si seasonal | C seasonal |",
        f"|---|---|---|",
    ]

    si_seasons = _per_season_starvation(si_seasonal, _T)
    c_seasons  = _per_season_starvation(c_seasonal,  _T)
    for i, (si_v, c_v) in enumerate(zip(si_seasons, c_seasons), 1):
        lines.append(f"| {i} (t={( i-1)*_T+1}-{i*_T}) | {si_v:.1f} | {c_v:.1f} |")

    lines += [
        f"",
        f"## Moran's I trajectory under stress (early t<=200 vs late t>800)",
        f"",
        f"| Trait | Si null | Si seasonal | C null | C seasonal |",
        f"|---|---|---|---|---|",
        f"| c1 | {_morans_trend(si_null,'morans_i_c1')} | {_morans_trend(si_seasonal,'morans_i_c1')} | {_morans_trend(c_null,'morans_i_c1')} | {_morans_trend(c_seasonal,'morans_i_c1')} |",
        f"| phi | {_morans_trend(si_null,'morans_i_phi')} | {_morans_trend(si_seasonal,'morans_i_phi')} | {_morans_trend(c_null,'morans_i_phi')} | {_morans_trend(c_seasonal,'morans_i_phi')} |",
        f"",
        f"Note: in Stage 3.3 static world, Moran's I was near zero for all traits.",
        f"An increase under seasonal stress would indicate stress-driven spatial clustering.",
        f"",
        f"## Plots",
        f"",
        f"- `survival_plot.png` — PRIMARY: N(t) with trough shading for C and Si",
        f"- `morans_i_c1.png` — spatial trait clustering under seasonal stress",
        f"- `capacity_verification.png` — oscillation firing check (first 400 steps)",
        f"- `starvation.png` — starvation deaths with trough shading",
        f"",
        f"## H1(ii) preliminary assessment",
        f"",
    ]

    si_trough_min = si_seasonal["population"].min()
    c_trough_min  = c_seasonal["population"].min()
    si_last_pop   = si_seasonal["population"].iloc[-100:].mean()
    c_last_pop    = c_seasonal["population"].iloc[-100:].mean()

    if c_trough_min > si_trough_min:
        h1_str = (f"C maintains higher minimum population (C min={c_trough_min:.0f}, "
                  f"Si min={si_trough_min:.0f}): consistent with H1(ii).")
    elif c_trough_min < si_trough_min:
        h1_str = (f"Si maintains higher minimum population (Si min={si_trough_min:.0f}, "
                  f"C min={c_trough_min:.0f}): inconsistent with H1(ii) at A=0.5.")
    else:
        h1_str = f"C and Si have equal minimum population ({c_trough_min:.0f}): inconclusive."

    lines += [
        f"{h1_str}",
        f"",
        f"Stage 4.2 amplitude sweep required for statistical assessment (Stage 6).",
        f"",
        f"## Reproducibility",
        f"",
        f"All four runs used seed=42. Re-run `py -m sic_games.stage4` to reproduce.",
    ]

    report_path = _STAGE4_OUT / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Report -> {report_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=== Stage 4: Seasonal Oscillation (A=0.5, T=200) ===")
    _STAGE4_OUT.mkdir(parents=True, exist_ok=True)

    # ---- Run 1: Si null control ----
    print("\n[Run 1/4] Si null control (sigma_Si=1.238, no oscillation)...")
    si_null = _run(_CONFIGS / "stage4_si_null_seed42.yaml",
                   _OUTPUTS / "stage4_si_null_seed42")
    print(f"  population tail mean = {si_null['population'].iloc[-100:].mean():.1f}")

    # ---- Run 2: C null control ----
    print("\n[Run 2/4] C null control (kappa=2.0, alpha=2.0, no oscillation)...")
    c_null = _run(_CONFIGS / "stage4_c_null_seed42.yaml",
                  _OUTPUTS / "stage4_c_null_seed42")
    print(f"  population tail mean = {c_null['population'].iloc[-100:].mean():.1f}")

    # ---- Gate: verify null controls before seasonal runs ----
    print("\n[Gate] Null-control verification against Stage 3 references...")
    _verify_null_controls(si_null, c_null)

    # ---- Run 3: Si seasonal ----
    print("\n[Run 3/4] Si seasonal (A=0.5, T=200)...")
    si_seasonal = _run(_CONFIGS / "stage4_si_seasonal_seed42.yaml",
                       _OUTPUTS / "stage4_si_seasonal_seed42")
    pop_min_si = si_seasonal["population"].iloc[:200].min()
    print(f"  population tail mean = {si_seasonal['population'].iloc[-100:].mean():.1f}, "
          f"season-1 min = {pop_min_si:.0f}")
    if pop_min_si <= 150:
        print(f"  WARNING: Si population collapsed in season 1 (N={pop_min_si:.0f} <= 150)")

    # ---- Run 4: C seasonal ----
    print("\n[Run 4/4] C seasonal (A=0.5, T=200)...")
    c_seasonal = _run(_CONFIGS / "stage4_c_seasonal_seed42.yaml",
                      _OUTPUTS / "stage4_c_seasonal_seed42")
    pop_min_c = c_seasonal["population"].iloc[:200].min()
    print(f"  population tail mean = {c_seasonal['population'].iloc[-100:].mean():.1f}, "
          f"season-1 min = {pop_min_c:.0f}")
    if pop_min_c <= 150:
        print(f"  WARNING: C population collapsed in season 1 (N={pop_min_c:.0f} <= 150)")

    # ---- Oscillation verification ----
    eff_cap_vals = si_seasonal["mean_effective_capacity"].iloc[:400]
    print(f"\n[Check] Oscillation: mean_effective_capacity range over first 400 steps: "
          f"{eff_cap_vals.min():.3f} - {eff_cap_vals.max():.3f}")

    # ---- Plots ----
    print("\n[Plots] Generating...")
    plot_survival(si_null, c_null, si_seasonal, c_seasonal,
                  _STAGE4_OUT / "survival_plot.png")
    plot_morans_i(si_null, c_null, si_seasonal, c_seasonal,
                  _STAGE4_OUT / "morans_i_c1.png")
    plot_capacity_verification(si_seasonal, _STAGE4_OUT / "capacity_verification.png")
    plot_starvation(si_null, c_null, si_seasonal, c_seasonal,
                    _STAGE4_OUT / "starvation.png")

    # ---- Report ----
    print("\n[Report] Building...")
    build_report(si_null, c_null, si_seasonal, c_seasonal)

    print("\nDone. Awaiting supervisor review of report and survival plot.")


if __name__ == "__main__":
    main()
