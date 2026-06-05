"""Stage 3 runner and report generator.

Runs three simulations in strict order:
  1. stage3_si_bounded_seed42  — bounded-rational Si (stability check)
  2. stage3_carbon_no_endowment_seed42 — C with f_C=0.0 (no endowment)
  3. stage3_carbon_seed42      — C with f_C=0.1 (canonical Stage 3)

Then generates a four-way comparison report (Stage 2 C-patched + three Stage 3 runs).
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
# Run helpers
# ---------------------------------------------------------------------------

_RUN_LABEL = {
    "si_bounded": "bounded-Si",
    "carbon_no_endowment": "C (f_C=0)",
    "carbon": "C (f_C=0.1)",
}

_RUN_COLOR = {
    "si_bounded": "steelblue",
    "carbon_no_endowment": "goldenrod",
    "carbon": "darkorange",
}


def _run_one(config_path: Path, run_key: str) -> tuple[pd.DataFrame, list[float]]:
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
    print(f"  {run_key} reproducibility: {'OK' if repro else 'FAIL'}")

    return metrics_df, starvation_creds


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _save_stage3_plots(
    runs: list[tuple[str, pd.DataFrame]],
    s2_df: pd.DataFrame | None,
    plots_dir: Path,
) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Four metric overlay plots (all three Stage 3 runs)
    for col, ylabel, title, fname in [
        ("mean_wealth", "Mean wealth", "Mean wealth over time", "s3_mean_wealth.png"),
        ("gini_wealth", "Gini coefficient", "Gini wealth over time", "s3_gini_wealth.png"),
        ("deaths_starvation", "Deaths / step", "Starvation deaths over time", "s3_starvation.png"),
        ("mean_cred", "Mean Cred", "Mean Cred over time", "s3_mean_cred.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 4))
        if s2_df is not None and col in s2_df.columns:
            ax.plot(
                s2_df["step"], s2_df[col],
                color="gray", label="Stage 2 C (patched)", alpha=0.5,
                linewidth=1.0, linestyle="--",
            )
        for key, df in runs:
            ax.plot(
                df["step"], df[col],
                color=_RUN_COLOR[key],
                label=_RUN_LABEL[key],
                alpha=0.85, linewidth=1.3,
            )
        ax.set_xlabel("Step")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        fig.tight_layout()
        fig.savefig(plots_dir / fname, dpi=100)
        plt.close(fig)

    # Age-split starvation plot (newborn vs established, C runs only)
    fig, ax = plt.subplots(figsize=(9, 4))
    for key, df in runs:
        if "deaths_starvation_newborn" not in df.columns:
            continue
        color = _RUN_COLOR[key]
        label = _RUN_LABEL[key]
        ax.plot(df["step"], df["deaths_starvation_newborn"],
                color=color, linewidth=1.0, linestyle="--",
                label=f"{label} newborn (<20)", alpha=0.8)
        ax.plot(df["step"], df["deaths_starvation_established"],
                color=color, linewidth=1.3, linestyle="-",
                label=f"{label} established (>=20)", alpha=0.8)
    ax.set_xlabel("Step")
    ax.set_ylabel("Deaths / step")
    ax.set_title("Age-split starvation deaths over time")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(plots_dir / "s3_age_split_starvation.png", dpi=100)
    plt.close(fig)

    # Sigma over time (for Si vs C comparison)
    fig, ax = plt.subplots(figsize=(9, 4))
    for key, df in runs:
        if "mean_sigma" not in df.columns:
            continue
        ax.plot(df["step"], df["mean_sigma"],
                color=_RUN_COLOR[key], label=_RUN_LABEL[key],
                alpha=0.85, linewidth=1.3)
    ax.set_xlabel("Step")
    ax.set_ylabel("Mean sigma")
    ax.set_title("Decision temperature over time")
    ax.legend()
    fig.tight_layout()
    fig.savefig(plots_dir / "s3_mean_sigma.png", dpi=100)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_stage3_report(
    runs: list[tuple[str, pd.DataFrame, list[float]]],
    s2_df: pd.DataFrame | None,
    out_dir: Path,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"

    _save_stage3_plots([(k, df) for k, df, _ in runs], s2_df, plots_dir)

    # Column headers
    s2_col = " Stage 2 C (patched) |" if s2_df is not None else ""
    run_cols = "".join(f" {_RUN_LABEL[k]} |" for k, _, _ in runs)
    header = f"| Metric (final 100 steps) |{s2_col}{run_cols}"
    sep = "|---|" + ("---|" * (1 if s2_df is not None else 0)) + "---|" * len(runs)

    metrics = [
        ("Mean wealth", "mean_wealth", "{:.1f}"),
        ("Gini wealth", "gini_wealth", "{:.3f}"),
        ("Spatial dispersion", "spatial_dispersion", "{:.1f}"),
        ("Deaths/step (starvation)", "deaths_starvation", "{:.2f}"),
        ("Deaths/step (senescence)", "deaths_senescence", "{:.2f}"),
        ("Deaths/step (newborn)", "deaths_starvation_newborn", "{:.2f}"),
        ("Deaths/step (established)", "deaths_starvation_established", "{:.2f}"),
        ("Mean Cred", "mean_cred", "{:.3f}"),
        ("Gini Cred", "gini_cred", "{:.3f}"),
        ("Max Cred fraction", "max_cred_fraction", "{:.3f}"),
        ("Mean sigma", "mean_sigma", "{:.3f}"),
        ("Joint tasks/step", "joint_task_count", "{:.2f}"),
        ("mean_w_C", "mean_w_C", "{:.3f}"),
        ("frac_suppressed", "frac_suppressed", "{:.3f}"),
    ]

    table_rows = []
    for label, col, fmt in metrics:
        s2_cell = ""
        if s2_df is not None:
            if col in s2_df.columns:
                s2_cell = f" {fmt.format(_tail_mean(s2_df, col))} |"
            else:
                s2_cell = " — |"
        run_cells = []
        for _, df, _ in runs:
            if col in df.columns:
                run_cells.append(fmt.format(_tail_mean(df, col)))
            else:
                run_cells.append("—")
        table_rows.append(f"| {label} |{s2_cell} " + " | ".join(run_cells) + " |")
    comparison_table = "\n".join([header, sep] + table_rows)

    # Quartile starvation table
    q_header = "| Cred quartile |" + "".join(f" {_RUN_LABEL[k]} |" for k, _, _ in runs)
    q_sep = "|---|" + "---|" * len(runs)
    quartile_labels = ["Q1 (lowest Cred)", "Q2", "Q3", "Q4 (highest Cred)"]
    quartile_results = []
    for k, df, creds in runs:
        all_creds = _all_creds_from_df(df)
        n_steps = len(df)
        qs = _quartile_starvation(creds, all_creds)
        # Scale to deaths/step using actual n_steps
        if n_steps != 1000:
            qs = tuple(q * 1000.0 / n_steps for q in qs)
        quartile_results.append(qs)

    q_rows = []
    for i, qlabel in enumerate(quartile_labels):
        cells = [qlabel]
        for qs in quartile_results:
            cells.append(f"{qs[i]:.3f}")
        q_rows.append("| " + " | ".join(cells) + " |")
    quartile_table = "\n".join([q_header, q_sep] + q_rows)

    # Tail-mean age-split starvation delta for C canonical vs Si
    si_newborn = _tail_mean(runs[0][1], "deaths_starvation_newborn") if runs else 0.0
    si_established = _tail_mean(runs[0][1], "deaths_starvation_established") if runs else 0.0
    c_canonical_key = runs[-1][0] if runs else ""
    c_newborn = _tail_mean(runs[-1][1], "deaths_starvation_newborn") if runs else 0.0
    c_established = _tail_mean(runs[-1][1], "deaths_starvation_established") if runs else 0.0

    report = f"""# Stage 3 Report — Variance-matched Si vs C comparison

**Date:** {date.today()} | **Seed:** 42 | **Steps:** 1000
**Strategy:** bounded-Si (sigma_Si=1.051) vs C (kappa=2.0, f_C=0 and f_C=0.1)

## Experimental design

Three runs in strict order (no Stage 2 directories overwritten):

1. **bounded-Si** (`stage3_si_bounded_seed42`) — Sugarscape with fixed softmax temperature
   sigma_Si=1.051 (calibrated from Stage 2.2 kappa=2.0 mean_sigma). No Cred, no joint tasks
   paid in Cred. Serves as the variance-matched baseline — same exploration noise as C.

2. **C no-endowment** (`stage3_carbon_no_endowment_seed42`) — Full carbon-C model with
   f_C=0.0 (newborns start at cred=0). Isolates the endowment effect from the strategy effect.

3. **C canonical** (`stage3_carbon_seed42`) — Full carbon-C with f_C=0.1 (newborns endowed
   with 10% of mean Cred at birth). Canonical Stage 3 C configuration.

The primary question: does the C vs Si starvation difference survive variance-matching?
The secondary question: does newborn Cred endowment reduce newborn starvation?

## Four-way comparison table

{comparison_table}

## Starvation by Cred quartile (deaths / step)

{quartile_table}

## Age-split starvation (final 100 steps)

| Cohort | bounded-Si | C (f_C=0.1) | Delta |
|---|---|---|---|
| Newborn (age<20) | {si_newborn:.3f} | {c_newborn:.3f} | {c_newborn - si_newborn:+.3f} |
| Established (age>=20) | {si_established:.3f} | {c_established:.3f} | {c_established - si_established:+.3f} |

## Plots

### Metric overlays (three Stage 3 runs + Stage 2 C reference)
![Mean wealth](plots/s3_mean_wealth.png)
![Gini wealth](plots/s3_gini_wealth.png)
![Starvation](plots/s3_starvation.png)
![Mean Cred](plots/s3_mean_cred.png)

### Age-split starvation
![Age-split starvation](plots/s3_age_split_starvation.png)

### Decision temperature
![Mean sigma](plots/s3_mean_sigma.png)

## Interpretation notes

- If C starvation > Si starvation after variance-matching, the mechanism (Cred inequality,
  joint-task access) is the driver — not raw exploration noise.
- If C newborn starvation drops with f_C=0.1 vs f_C=0.0, the endowment works as intended.
- Established-cohort delta is the cleaner signal: older agents have accumulated Cred and the
  endowment effect is diluted; any persistent excess reflects the Matthew effect.
"""

    report_path = out_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_DEFAULT_CONFIGS = [
    ("si_bounded", "configs/stage3_si_bounded_seed42.yaml"),
    ("carbon_no_endowment", "configs/stage3_carbon_no_endowment_seed42.yaml"),
    ("carbon", "configs/stage3_carbon_seed42.yaml"),
]

_S2_PATCHED_PARQUET = "outputs/stage2_carbon_patched_seed42/metrics.parquet"


def run_stage3(
    config_triples: list[tuple[str, str | Path]] | None = None,
    out_dir: str | Path = "outputs/stage3_report",
    s2_parquet: str | Path | None = _S2_PATCHED_PARQUET,
) -> Path:
    if config_triples is None:
        config_triples = _DEFAULT_CONFIGS

    runs = []
    for run_key, config_path in config_triples:
        config_path = Path(config_path)
        print(f"\nRunning {run_key} ({config_path.name}) ...")
        df, creds = _run_one(config_path, run_key)
        runs.append((run_key, df, creds))
        print(f"  done. mean_wealth={_tail_mean(df, 'mean_wealth'):.1f}, "
              f"starvation={_tail_mean(df, 'deaths_starvation'):.2f}/step, "
              f"mean_sigma={_tail_mean(df, 'mean_sigma'):.3f}")

    s2_df: pd.DataFrame | None = None
    if s2_parquet:
        s2_path = Path(s2_parquet)
        if s2_path.exists():
            s2_df = pd.read_parquet(s2_path)
        else:
            print(f"  [warn] Stage 2 parquet not found at {s2_path}; omitting four-way column")

    report_path = generate_stage3_report(runs, s2_df, Path(out_dir))
    print(f"\nStage 3 report written to: {report_path}")
    return report_path


if __name__ == "__main__":
    run_stage3()
