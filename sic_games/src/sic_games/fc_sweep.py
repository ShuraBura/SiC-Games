"""f_C sweep runner and report generator for Stage 3.1.

f_C=0.0 and f_C=0.1 are loaded from confirmed parquets (do not re-run).
f_C=0.25 and f_C=0.5 are run fresh with reproducibility checks.

Confirmed quartile starvation values for the two baseline runs (from Stage 3
execution, 2026-05-16, seed=42):
"""
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
from sic_games.sweep import _all_creds_from_df, _quartile_starvation, _tail_mean


# ---------------------------------------------------------------------------
# Confirmed baselines — loaded from parquet, quartiles hardcoded from Stage 3
# ---------------------------------------------------------------------------

_CONFIRMED = {
    0.0: {
        "parquet": "outputs/stage3_carbon_no_endowment_seed42/metrics.parquet",
        "quartiles": (2.129, 0.005, 0.426, 0.288),
    },
    0.1: {
        "parquet": "outputs/stage3_carbon_seed42/metrics.parquet",
        "quartiles": (0.887, 0.880, 0.982, 0.288),
    },
}

_FC_COLORS = {
    0.0:  "#2166ac",
    0.1:  "#74add1",
    0.25: "#f4a582",
    0.5:  "#d6604d",
}

_FC_LABELS = {f: f"f_C={f}" for f in [0.0, 0.1, 0.25, 0.5]}


# ---------------------------------------------------------------------------
# Runner for new configs
# ---------------------------------------------------------------------------

def _run_new(config_path: Path, f_C: float) -> tuple[pd.DataFrame, tuple[float, float, float, float]]:
    config = load_config(config_path)
    out_dir = Path(config.run.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = SugarWorld(config)
    for _ in range(config.run.n_steps):
        model.step()

    metrics_df = model.metrics_to_df()
    starvation_creds = list(model.starvation_cred_log)
    metrics_df.to_parquet(out_dir / "metrics.parquet", index=False)

    model2 = SugarWorld(config)
    for _ in range(config.run.n_steps):
        model2.step()
    repro = metrics_df["gini_wealth"].round(6).equals(
        model2.metrics_to_df()["gini_wealth"].round(6)
    )
    print(f"  f_C={f_C} reproducibility: {'OK' if repro else 'FAIL'}")

    all_creds = _all_creds_from_df(metrics_df)
    quartiles = _quartile_starvation(starvation_creds, all_creds)
    return metrics_df, quartiles


# ---------------------------------------------------------------------------
# Trajectory diagnostic
# ---------------------------------------------------------------------------

def _cred_runaway(df: pd.DataFrame) -> tuple[bool, float]:
    """Return (is_runaway, growth_rate_per_100_steps) for post-t=500 mean_cred."""
    late = df[df["step"] > 500]
    if len(late) < 50:
        return False, 0.0

    # Fit linear slope to mean_cred in [501, 1000]
    x = late["step"].values.astype(float)
    y = late["mean_cred"].values
    slope, _ = np.polyfit(x, y, 1)  # units: cred / step

    base = late["mean_cred"].iloc[0]
    if base <= 0.0:
        return False, 0.0

    growth_per_100 = slope * 100.0 / base  # fractional growth per 100 steps
    return growth_per_100 > 0.05, growth_per_100


# ---------------------------------------------------------------------------
# Overlay plots
# ---------------------------------------------------------------------------

def _save_fc_plots(runs: list[tuple[float, pd.DataFrame]], plots_dir: Path) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)

    for col, ylabel, title, fname in [
        ("mean_cred", "Mean Cred", "Mean Cred over time", "fc_mean_cred.png"),
        ("deaths_starvation", "Deaths / step", "Total starvation over time", "fc_starvation.png"),
        ("deaths_starvation_newborn", "Deaths / step", "Newborn starvation over time", "fc_newborn_starvation.png"),
        ("gini_cred", "Gini Cred", "Gini of Cred over time", "fc_gini_cred.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 4))
        for f_C, df in runs:
            if col not in df.columns:
                continue
            ax.plot(
                df["step"], df[col],
                color=_FC_COLORS[f_C],
                label=_FC_LABELS[f_C],
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

def generate_fc_sweep_report(
    runs: list[tuple[float, pd.DataFrame, tuple[float, float, float, float]]],
    out_dir: Path,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"

    _save_fc_plots([(f, df) for f, df, _ in runs], plots_dir)

    # Primary comparison table
    metrics = [
        ("Mean wealth", "mean_wealth", "{:.1f}"),
        ("Gini wealth", "gini_wealth", "{:.3f}"),
        ("Spatial dispersion", "spatial_dispersion", "{:.1f}"),
        ("Deaths/step (starvation)", "deaths_starvation", "{:.2f}"),
        ("Deaths/step (newborn)", "deaths_starvation_newborn", "{:.2f}"),
        ("Deaths/step (established)", "deaths_starvation_established", "{:.2f}"),
        ("Mean Cred", "mean_cred", "{:.3f}"),
        ("Gini Cred", "gini_cred", "{:.3f}"),
        ("Max Cred fraction", "max_cred_fraction", "{:.3f}"),
        ("Mean sigma", "mean_sigma", "{:.3f}"),
        ("Joint tasks/step", "joint_task_count", "{:.2f}"),
        ("mean_w_C", "mean_w_C", "{:.3f}"),
    ]

    f_vals = [f for f, _, _ in runs]
    header = "| Metric (final 100 steps) |" + "".join(f" f_C={f} |" for f in f_vals)
    sep = "|---|" + "---|" * len(runs)
    table_rows = []
    for label, col, fmt in metrics:
        cells = [label]
        for _, df, _ in runs:
            if col in df.columns:
                cells.append(fmt.format(_tail_mean(df, col)))
            else:
                cells.append("—")
        table_rows.append("| " + " | ".join(cells) + " |")
    comparison_table = "\n".join([header, sep] + table_rows)

    # Quartile table
    quartile_labels = ["Q1 (lowest Cred)", "Q2", "Q3", "Q4 (highest Cred)"]
    q_header = "| Cred quartile |" + "".join(f" f_C={f} |" for f in f_vals)
    q_sep = "|---|" + "---|" * len(runs)
    q_rows = []
    for i, qlabel in enumerate(quartile_labels):
        cells = [qlabel]
        for _, _, qs in runs:
            cells.append(f"{qs[i]:.3f}")
        q_rows.append("| " + " | ".join(cells) + " |")
    quartile_table = "\n".join([q_header, q_sep] + q_rows)

    # Trajectory diagnostic section
    diag_rows = []
    for f, df, _ in runs:
        is_runaway, rate = _cred_runaway(df)
        flag = " ** RUNAWAY **" if is_runaway else ""
        diag_rows.append(
            f"- **f_C={f}**: growth rate {rate:+.3f} per 100 steps after t=500{flag}"
        )
    diag_section = "\n".join(diag_rows)

    # Watch metrics (final 100)
    gini_vals = {f: _tail_mean(df, "gini_cred") for f, df, _ in runs}
    jt_vals = {f: _tail_mean(df, "joint_task_count") for f, df, _ in runs}

    gini_warnings = [
        f"  - f_C={f}: Gini Cred = {v:.3f} ** BELOW 0.6 — Matthew effect weakened **"
        for f, v in gini_vals.items() if v < 0.6
    ]
    jt_warnings = [
        f"  - f_C={f}: Joint tasks/step = {v:.2f} ** BELOW 25 — Cred engine suppressed **"
        for f, v in jt_vals.items() if v < 25.0
    ]
    watch_section = ""
    if gini_warnings:
        watch_section += "\n**Gini Cred watch (threshold 0.6):**\n" + "\n".join(gini_warnings)
    if jt_warnings:
        watch_section += "\n\n**Joint tasks watch (threshold 25/step):**\n" + "\n".join(jt_warnings)
    if not watch_section:
        watch_section = "All watch metrics within acceptable bounds."

    report = f"""# f_C sweep report — Stage 3.1

**Date:** {date.today()} | **Seed:** 42 | **Steps:** 1000
**Varied:** f_C (newborn Cred endowment fraction) in {{0.0, 0.1, 0.25, 0.5}}

f_C=0.0 and f_C=0.1 loaded from confirmed Stage 3 parquets (not re-run).
f_C=0.25 and f_C=0.5 run fresh with reproducibility confirmation.

## Primary comparison table

{comparison_table}

## Starvation by Cred quartile (deaths / step)

Quartile boundaries from population Cred distribution. f_C=0.0 and f_C=0.1
values are confirmed from Stage 3 execution (2026-05-16).

{quartile_table}

## Cred trajectory diagnostic

Linear growth rate of mean_cred in steps 501–1000, normalised per 100 steps.
Threshold for runaway: >5% per 100 steps.

{diag_section}

## Watch metrics

{watch_section}

## Overlay plots

![Mean Cred over time](plots/fc_mean_cred.png)
![Total starvation over time](plots/fc_starvation.png)
![Newborn starvation over time](plots/fc_newborn_starvation.png)
![Gini Cred over time](plots/fc_gini_cred.png)

## f_C selection guidance

Selection criteria (all must hold):
1. No Cred runaway (growth < 5% per 100 steps after t=500)
2. Gini Cred > 0.6 (Matthew effect intact)
3. Joint tasks/step > 25 (Cred engine firing)
4. Total starvation not catastrophically above f_C=0.0 baseline (2.86/step)
"""

    report_path = out_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_fc_sweep(
    out_dir: str | Path = "outputs/stage3.1_fC_sweep_seed42",
) -> Path:
    out_dir = Path(out_dir)
    runs: list[tuple[float, pd.DataFrame, tuple]] = []

    # Load confirmed baselines from parquet
    for f_C, info in sorted(_CONFIRMED.items()):
        parquet = Path(info["parquet"])
        if not parquet.exists():
            raise FileNotFoundError(
                f"Confirmed parquet missing: {parquet}. Do not re-run — check Stage 3 outputs."
            )
        df = pd.read_parquet(parquet)
        runs.append((f_C, df, info["quartiles"]))
        print(f"Loaded f_C={f_C} from {parquet}  "
              f"(mean_wealth={_tail_mean(df, 'mean_wealth'):.1f}, "
              f"starvation={_tail_mean(df, 'deaths_starvation'):.2f}/step)")

    # Run new configs
    new_configs = [
        (0.25, Path("configs/stage3_fC025_seed42.yaml")),
        (0.5,  Path("configs/stage3_fC05_seed42.yaml")),
    ]
    for f_C, cfg_path in new_configs:
        print(f"\nRunning f_C={f_C} ({cfg_path.name}) ...")
        df, quartiles = _run_new(cfg_path, f_C)
        runs.append((f_C, df, quartiles))
        print(f"  done. mean_wealth={_tail_mean(df, 'mean_wealth'):.1f}, "
              f"starvation={_tail_mean(df, 'deaths_starvation'):.2f}/step, "
              f"gini_cred={_tail_mean(df, 'gini_cred'):.3f}, "
              f"joint_tasks={_tail_mean(df, 'joint_task_count'):.2f}/step")

    runs.sort(key=lambda x: x[0])
    report_path = generate_fc_sweep_report(runs, out_dir)
    print(f"\nf_C sweep report written to: {report_path}")
    return report_path


if __name__ == "__main__":
    run_fc_sweep()
