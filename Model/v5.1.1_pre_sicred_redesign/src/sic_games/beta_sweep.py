"""Beta (status amplification) sweep runner and report generator — Stage 3.2.

β=0.0 baseline loaded from confirmed Stage 3.1 parquet (f_C=0.25 run).
β=0.5, 1.0, 2.0 run fresh with reproducibility checks, in that order.

Note: the blueprint points to outputs/stage3_carbon_seed42 (f_C=0.1) as the
β=0.0 baseline, but the pre-filled numbers in the blueprint table match the
f_C=0.25 run from Stage 3.1. This runner loads from the correct source:
outputs/stage3_fC025_seed42/metrics.parquet.
"""
from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sic_games.config import load_config
from sic_games.fc_sweep import _cred_runaway
from sic_games.run import SugarWorld
from sic_games.sweep import _all_creds_from_df, _quartile_starvation, _tail_mean


# ---------------------------------------------------------------------------
# Confirmed β=0.0 baseline (Stage 3.1 f_C=0.25 run)
# ---------------------------------------------------------------------------

_BETA00_PARQUET = "outputs/stage3_fC025_seed42/metrics.parquet"

# Confirmed quartile starvation values from Stage 3.1 f_C=0.25 row
_BETA00_QUARTILES = (0.796, 0.902, 1.116, 0.310)

_BETA_COLORS = {
    0.0: "#2166ac",
    0.5: "#74add1",
    1.0: "#f4a582",
    2.0: "#d6604d",
}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run_one(config_path: Path, beta: float) -> tuple[pd.DataFrame, tuple]:
    config = load_config(config_path)
    out_dir = Path(config.run.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = SugarWorld(config)
    for _ in range(config.run.n_steps):
        model.step()

    df = model.metrics_to_df()
    starvation_creds = list(model.starvation_cred_log)
    df.to_parquet(out_dir / "metrics.parquet", index=False)

    model2 = SugarWorld(config)
    for _ in range(config.run.n_steps):
        model2.step()
    repro = df["gini_wealth"].round(6).equals(model2.metrics_to_df()["gini_wealth"].round(6))
    print(f"  beta={beta} reproducibility: {'OK' if repro else 'FAIL'}")

    all_creds = _all_creds_from_df(df)
    quartiles = _quartile_starvation(starvation_creds, all_creds)
    return df, quartiles


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _save_beta_plots(runs: list[tuple[float, pd.DataFrame]], plots_dir: Path) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)

    for col, ylabel, title, fname in [
        ("mean_w_C", "Mean w_C", "Mean effective Cred-seeking weight", "beta_mean_wC.png"),
        ("std_w_C", "Std w_C", "Behavioral diversity (std of w_C)", "beta_std_wC.png"),
        ("deaths_starvation_established", "Deaths / step", "Established starvation over time", "beta_established_starvation.png"),
        ("mean_cred", "Mean Cred", "Mean Cred over time", "beta_mean_cred.png"),
        ("joint_task_count", "Joint tasks / step", "Joint tasks over time", "beta_joint_tasks.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 4))
        for beta, df in runs:
            if col not in df.columns:
                continue
            ax.plot(
                df["step"], df[col],
                color=_BETA_COLORS.get(beta, "gray"),
                label=f"beta={beta}",
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

def generate_beta_sweep_report(
    runs: list[tuple[float, pd.DataFrame, tuple]],
    out_dir: Path,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"

    _save_beta_plots([(b, df) for b, df, _ in runs], plots_dir)

    beta_vals = [b for b, _, _ in runs]

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
        ("Mean sigma", "mean_sigma", "{:.3f}"),
        ("Joint tasks/step", "joint_task_count", "{:.2f}"),
        ("mean_w_C", "mean_w_C", "{:.3f}"),
        ("std_w_C", "std_w_C", "{:.3f}"),
        ("mean_amplification", "mean_amplification", "{:.3f}"),
        ("frac_amplified", "frac_amplified", "{:.3f}"),
    ]

    header = "| Metric (final 100 steps) |" + "".join(f" beta={b} |" for b in beta_vals)
    sep = "|---|" + "---|" * len(runs)
    rows = []
    for label, col, fmt in metrics:
        cells = [label]
        for _, df, _ in runs:
            cells.append(fmt.format(_tail_mean(df, col)) if col in df.columns else "—")
        rows.append("| " + " | ".join(cells) + " |")
    comparison_table = "\n".join([header, sep] + rows)

    # Quartile table
    q_header = "| Cred quartile |" + "".join(f" beta={b} |" for b in beta_vals)
    q_sep = "|---|" + "---|" * len(runs)
    q_labels = ["Q1 (lowest Cred)", "Q2", "Q3", "Q4 (highest Cred)"]
    q_rows = []
    for i, ql in enumerate(q_labels):
        cells = [ql] + [f"{qs[i]:.3f}" for _, _, qs in runs]
        q_rows.append("| " + " | ".join(cells) + " |")
    quartile_table = "\n".join([q_header, q_sep] + q_rows)

    # Trajectory diagnostic
    diag_lines = []
    for b, df, _ in runs:
        is_runaway, rate = _cred_runaway(df)
        flag = " ** RUNAWAY **" if is_runaway else ""
        diag_lines.append(f"- **beta={b}**: {rate:+.3f} per 100 steps after t=500{flag}")
    diag_section = "\n".join(diag_lines)

    # Success criteria check
    baseline_estab = _tail_mean(runs[0][1], "deaths_starvation_established")
    estab_threshold = baseline_estab * 1.5
    crit_lines = []
    for b, df, _ in runs:
        issues = []
        is_runaway, rate = _cred_runaway(df)
        if is_runaway:
            issues.append(f"Cred runaway ({rate:+.3f}/100 steps)")
        if "std_w_C" in df.columns:
            std_wc = _tail_mean(df, "std_w_C")
            if std_wc <= 0.05:
                issues.append(f"behavioral collapse (std_w_C={std_wc:.3f})")
        q4 = runs[[r[0] for r in runs].index(b)][2][3]
        q3 = runs[[r[0] for r in runs].index(b)][2][2]
        if q4 > q3:
            issues.append(f"Q4 starvation > Q3 ({q4:.3f} > {q3:.3f})")
        estab = _tail_mean(df, "deaths_starvation_established")
        if estab > estab_threshold:
            issues.append(f"established deaths > 1.5x baseline ({estab:.2f} > {estab_threshold:.2f})")
        status = "FAIL: " + "; ".join(issues) if issues else "PASS"
        crit_lines.append(f"- **beta={b}**: {status}")
    criteria_section = "\n".join(crit_lines)

    report = f"""# beta (status amplification) sweep report — Stage 3.2

**Date:** {date.today()} | **Seed:** 42 | **Steps:** 1000
**Varied:** status_amplification_beta in {{0.0, 0.5, 1.0, 2.0}}

beta=0.0 loaded from confirmed Stage 3.1 parquet (f_C=0.25 run,
`outputs/stage3_fC025_seed42/metrics.parquet`). beta=0.5, 1.0, 2.0 run fresh.

## Primary comparison table

{comparison_table}

## Starvation by Cred quartile (deaths / step)

beta=0.0 quartile values confirmed from Stage 3.1 (f_C=0.25 row, 2026-05-16).

{quartile_table}

## Cred trajectory diagnostic

Linear growth rate of mean_cred in steps 501–1000, normalised per 100 steps.
Runaway threshold: >5% per 100 steps.

{diag_section}

## Success criteria (§5 of blueprint)

Established starvation threshold: ≤ {estab_threshold:.2f}/step (1.5× beta=0.0 baseline of {baseline_estab:.2f}).

{criteria_section}

## Overlay plots

![Mean w_C](plots/beta_mean_wC.png)
![Std w_C (behavioral diversity)](plots/beta_std_wC.png)
![Established starvation](plots/beta_established_starvation.png)
![Mean Cred](plots/beta_mean_cred.png)
![Joint tasks](plots/beta_joint_tasks.png)

## beta selection guidance

Prefer the value where:
1. No Cred runaway (< 5% growth per 100 steps after t=500)
2. std_w_C > 0.05 — behavioral diversity intact
3. Q4 starvation does not exceed Q3 (utility saturation absent)
4. Established deaths ≤ 1.5× beta=0.0 baseline ({estab_threshold:.2f}/step)
"""

    report_path = out_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_NEW_CONFIGS = [
    (0.5,  Path("configs/stage32_beta05_seed42.yaml")),
    (1.0,  Path("configs/stage32_beta10_seed42.yaml")),
    (2.0,  Path("configs/stage32_beta20_seed42.yaml")),
]


def run_beta_sweep(
    out_dir: str | Path = "outputs/stage3.2_beta_sweep_seed42",
) -> Path:
    out_dir = Path(out_dir)
    runs: list[tuple[float, pd.DataFrame, tuple]] = []

    # Load confirmed β=0.0 baseline
    p = Path(_BETA00_PARQUET)
    if not p.exists():
        raise FileNotFoundError(
            f"Confirmed baseline missing: {p}. Do not re-run — check Stage 3.1 outputs."
        )
    df00 = pd.read_parquet(p)
    runs.append((0.0, df00, _BETA00_QUARTILES))
    print(f"Loaded beta=0.0 from {p}  "
          f"(mean_wealth={_tail_mean(df00, 'mean_wealth'):.1f}, "
          f"starvation={_tail_mean(df00, 'deaths_starvation'):.2f}/step)")

    # Run new configs in order: 0.5 → 1.0 → 2.0
    for beta, cfg_path in _NEW_CONFIGS:
        print(f"\nRunning beta={beta} ({cfg_path.name}) ...")
        df, quartiles = _run_one(cfg_path, beta)
        runs.append((beta, df, quartiles))
        is_runaway, rate = _cred_runaway(df)
        print(f"  mean_wealth={_tail_mean(df, 'mean_wealth'):.1f}, "
              f"starvation={_tail_mean(df, 'deaths_starvation'):.2f}/step, "
              f"std_w_C={_tail_mean(df, 'std_w_C'):.3f}, "
              f"mean_amp={_tail_mean(df, 'mean_amplification'):.3f}, "
              f"cred_trend={rate:+.3f}/100steps"
              + (" ** RUNAWAY **" if is_runaway else ""))

    runs.sort(key=lambda x: x[0])
    report_path = generate_beta_sweep_report(runs, out_dir)
    print(f"\nBeta sweep report written to: {report_path}")
    return report_path


if __name__ == "__main__":
    run_beta_sweep()
