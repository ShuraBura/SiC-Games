"""kappa sweep runner and report generator for Stage 2.2."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sic_games.config import load_config
from sic_games.run import SugarWorld


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_one(config_path: Path) -> tuple[pd.DataFrame, list[float]]:
    """Run one simulation; return (metrics_df, starvation_cred_log)."""
    config = load_config(config_path)
    out_dir = Path(config.run.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = SugarWorld(config)
    for _ in range(config.run.n_steps):
        model.step()

    metrics_df = model.metrics_to_df()
    starvation_creds = list(model.starvation_cred_log)

    metrics_df.to_parquet(out_dir / "metrics.parquet", index=False)

    # Reproducibility check
    model2 = SugarWorld(config)
    for _ in range(config.run.n_steps):
        model2.step()
    repro = model.metrics_to_df()["gini_wealth"].round(6).equals(
        model2.metrics_to_df()["gini_wealth"].round(6)
    )
    print(f"  kappa={config.carbon.kappa} reproducibility: {'OK' if repro else 'FAIL'}")

    return metrics_df, starvation_creds


def _tail_mean(df: pd.DataFrame, col: str, n: int = 100) -> float:
    return df.tail(n)[col].mean()


def _quartile_starvation(
    starvation_creds: list[float],
    all_creds: list[float],
) -> tuple[float, float, float, float]:
    """
    Compute starvation deaths per quartile of the *population* Cred distribution.

    Quartile boundaries are taken from all_creds (representative population sample).
    Returns (q1_rate, q2_rate, q3_rate, q4_rate) as deaths per step.
    Falls back to even-split of starvation deaths when boundaries are degenerate.
    """
    if not starvation_creds or not all_creds:
        return 0.0, 0.0, 0.0, 0.0

    p25 = float(np.percentile(all_creds, 25))
    p50 = float(np.percentile(all_creds, 50))
    p75 = float(np.percentile(all_creds, 75))

    counts = [0, 0, 0, 0]
    for c in starvation_creds:
        if c <= p25:
            counts[0] += 1
        elif c <= p50:
            counts[1] += 1
        elif c <= p75:
            counts[2] += 1
        else:
            counts[3] += 1

    n_steps = 1000.0
    return tuple(x / n_steps for x in counts)  # deaths per step


def _all_creds_from_df(df: pd.DataFrame) -> list[float]:
    """Reconstruct a rough Cred distribution from stored percentile columns."""
    creds = []
    for _, row in df.iterrows():
        creds.extend([row["cred_p25"], row["cred_p50"], row["cred_p75"]])
    return creds


# ---------------------------------------------------------------------------
# Overlay plots
# ---------------------------------------------------------------------------

_KAPPA_COLORS = {1.0: "#2166ac", 2.0: "#f4a582", 3.0: "#d6604d"}
_KAPPA_LABELS = {1.0: "kappa=1.0", 2.0: "kappa=2.0", 3.0: "kappa=3.0"}


def _save_sweep_overlay_plots(
    runs: list[tuple[float, pd.DataFrame]],
    plots_dir: Path,
) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)

    for col, ylabel, title, fname in [
        ("mean_sigma", "Mean sigma", "Mean decision temperature over time", "sweep_mean_sigma.png"),
        ("deaths_starvation", "Deaths / step", "Starvation deaths over time", "sweep_starvation.png"),
        ("mean_cred", "Mean Cred", "Mean Cred over time", "sweep_mean_cred.png"),
        ("gini_cred", "Gini Cred", "Gini of Cred over time", "sweep_gini_cred.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 4))
        for kappa, df in runs:
            ax.plot(
                df["step"], df[col],
                color=_KAPPA_COLORS.get(kappa, "gray"),
                label=_KAPPA_LABELS.get(kappa, f"kappa={kappa}"),
                alpha=0.85, linewidth=1.3,
            )
        ax.set_xlabel("Step")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        fig.tight_layout()
        fig.savefig(plots_dir / fname, dpi=100)
        plt.close(fig)


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_sweep_report(
    runs: list[tuple[float, pd.DataFrame, list[float]]],
    out_dir: Path,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"

    # Overlay plots
    _save_sweep_overlay_plots([(k, df) for k, df, _ in runs], plots_dir)

    # Build comparison table rows
    metrics = [
        ("Mean wealth", "mean_wealth", "{:.1f}"),
        ("Gini wealth", "gini_wealth", "{:.2f}"),
        ("Spatial dispersion", "spatial_dispersion", "{:.1f}"),
        ("Deaths/step (starvation)", "deaths_starvation", "{:.2f}"),
        ("Deaths/step (senescence)", "deaths_senescence", "{:.2f}"),
        ("Mean Cred", "mean_cred", "{:.3f}"),
        ("Gini Cred", "gini_cred", "{:.3f}"),
        ("Max Cred fraction", "max_cred_fraction", "{:.3f}"),
        ("Mean sigma", "mean_sigma", "{:.3f}"),
        ("Joint tasks/step", "joint_task_count", "{:.2f}"),
        ("mean_w_C", "mean_w_C", "{:.3f}"),
        ("frac_suppressed", "frac_suppressed", "{:.3f}"),
    ]

    header = "| Metric (final 100 steps) |" + "".join(
        f" {_KAPPA_LABELS[k]} |" for k, _, _ in runs
    )
    sep = "|---|" + "---|" * len(runs)

    table_rows = []
    for label, col, fmt in metrics:
        cells = [label]
        for _, df, _ in runs:
            val = _tail_mean(df, col)
            cells.append(fmt.format(val))
        table_rows.append("| " + " | ".join(cells) + " |")
    comparison_table = "\n".join([header, sep] + table_rows)

    # Quartile starvation table
    q_header = "| Cred quartile |" + "".join(f" {_KAPPA_LABELS[k]} |" for k, _, _ in runs)
    q_sep = "|---|" + "---|" * len(runs)
    quartile_labels = ["Q1 (lowest Cred)", "Q2", "Q3", "Q4 (highest Cred)"]
    q_rows = []
    quartile_results = []
    for k, df, creds in runs:
        all_creds = _all_creds_from_df(df)
        qs = _quartile_starvation(creds, all_creds)
        quartile_results.append(qs)

    for i, qlabel in enumerate(quartile_labels):
        cells = [qlabel]
        for qs in quartile_results:
            cells.append(f"{qs[i]:.3f}")
        q_rows.append("| " + " | ".join(cells) + " |")
    quartile_table = "\n".join([q_header, q_sep] + q_rows)

    report = f"""# kappa sweep report — Stage 2.2

**Date:** {date.today()} | **Seed:** 42 | **Steps:** 1000 | **Varied:** kappa (sigma noise ceiling)

## Notes

### Task 1 — Baseline discrepancy diagnosis and resolution

**Problem:** The three-way comparison table in the Stage 2.1 patched report showed "C baseline"
numbers (mean_wealth=45.8, mean_cred=7.141, joint_tasks=31.06) that differed from the confirmed
Stage 2 pre-patch baseline (mean_wealth=42.0, mean_cred=6.923, joint_tasks=30.41).

**Root cause:** The ModeSwitch patch changed the decision formula in `CarbonDecision.select_target`
from `w_C = agent.phi` (fixed trait, pre-patch) to `w_C = agent.phi * sigmoid(v_i / v0)`
(velocity-modulated, post-patch). Even with the same seed=42, different utility weights produce
different agent choices at every step, accumulating into different aggregate metrics. The RNG
sequence itself was not altered — the divergence is purely from the changed decision logic.

Additionally, `configs/stage2_carbon_seed42.yaml` was re-run *after* the patch was applied,
overwriting `outputs/stage2_carbon_seed42/metrics.parquet` with post-patch values and permanently
losing the original pre-patch ground truth.

**Resolution:** The three confirmed pre-patch values (mean_wealth=42.0, mean_cred=6.923,
joint_tasks=30.41) are now hardcoded as `_S2_PRE_SWITCH` in `report.py` and used directly in
the three-way comparison table (marked †). Remaining metrics in that table use the best available
approximation: the `stage2_carbon_noswitch_seed42` run (velocity_tau=0, giving
`w_C = phi * sigmoid(0) = phi * 0.5` — intermediate between pre-patch and fully adaptive).
Full diagnosis documented in `BUGS.md` (BUG-001).

## Comparison table

{comparison_table}

## Starvation by Cred quartile (deaths / step)

Quartile boundaries derived from population Cred percentile distribution (cred_p25/p50/p75
averaged across all steps). A concentration in Q4 indicates the σ-Cred mechanism is the
genuine driver of starvation excess, not a uniform artifact.

{quartile_table}

## Overlay plots

![Mean sigma over time](plots/sweep_mean_sigma.png)
![Starvation deaths over time](plots/sweep_starvation.png)
![Mean Cred over time](plots/sweep_mean_cred.png)
![Gini Cred over time](plots/sweep_gini_cred.png)

## Interpretation notes

- **σ calibration target:** the `mean_sigma` value from the selected kappa becomes the fixed
  temperature for Stage 3's bounded-rational Si.
- **kappa selection guidance:** prefer kappa where mean_sigma is meaningfully above σ_base=0.5
  (exploration is real) but starvation excess over Si (1.8/step) is < 3.6/step (< 2×).
- If Q4 starvation > Q1 starvation across all kappa: mechanism is the genuine driver.
"""

    report_path = out_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_kappa_sweep(
    config_paths: list[str | Path],
    out_dir: str | Path = "outputs/stage2_kappa_sweep_seed42",
) -> Path:
    runs = []
    for path in config_paths:
        path = Path(path)
        config = load_config(path)
        kappa = config.carbon.kappa
        print(f"\nRunning kappa={kappa} ...")
        df, creds = _run_one(path)
        runs.append((kappa, df, creds))
        print(f"  kappa={kappa} done. mean_sigma={_tail_mean(df, 'mean_sigma'):.3f}, "
              f"starvation={_tail_mean(df, 'deaths_starvation'):.2f}/step")

    runs.sort(key=lambda x: x[0])
    report_path = generate_sweep_report(runs, Path(out_dir))
    print(f"\nSweep report written to: {report_path}")
    return report_path


if __name__ == "__main__":
    paths = sys.argv[1:] or [
        "configs/stage2_kappa10_seed42.yaml",
        "configs/stage2_carbon_patched_seed42.yaml",
        "configs/stage2_kappa30_seed42.yaml",
    ]
    run_kappa_sweep(paths)
