"""Main entry point: python -m sic_games.main <config.yaml>"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pandas as pd

from sic_games.config import load_config
from sic_games.report import generate_report, stage1_success_checks, stage2_success_checks
from sic_games.run import SugarWorld
from sic_games.visualize import (
    load_snapshots,
    save_animation,
    save_comparison_animation,
    save_comparison_plots,
    save_snapshots,
    save_stage2_plots,
    save_static_plots,
)


def run_single(config_path: str | Path, *, animate: bool | None = None) -> Path:
    config = load_config(config_path)
    out_dir = Path(config.run.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy(config_path, out_dir / "config.yaml")

    do_animate = animate if animate is not None else config.visualization.animate
    strategy = config.decision.strategy
    is_carbon = strategy == "carbon"

    # Run simulation
    model = SugarWorld(config)
    snapshots: list = []

    for step in range(config.run.n_steps):
        model.step()
        if do_animate and (step % config.visualization.frames_per_save == 0):
            sugar_copy = model.sugar_field.sugar.copy()
            positions = [a.pos for a in model.agents]
            snapshots.append((sugar_copy, positions))

    metrics_df = model.metrics_to_df()
    agent_states_df = model.agent_states_df()

    metrics_df.to_parquet(out_dir / "metrics.parquet", index=False)
    agent_states_df.to_parquet(out_dir / "final_state.parquet", index=False)

    # Reproducibility check
    model2 = SugarWorld(config)
    for _ in range(config.run.n_steps):
        model2.step()
    metrics_df2 = model2.metrics_to_df()

    # Static plots
    if config.visualization.save_static_plots:
        save_static_plots(
            metrics_df=metrics_df,
            agent_states_df=agent_states_df,
            sugar_field=model.sugar_field,
            plots_dir=out_dir / "plots",
            strategy=strategy,
        )
        if is_carbon:
            save_stage2_plots(
                metrics_df=metrics_df,
                plots_dir=out_dir / "plots",
                strategy=strategy,
            )

    # Comparison overlay plots (carbon only, when a Stage 1 reference dir is configured)
    si_df: pd.DataFrame | None = None
    si_ref = config.run.si_reference_dir
    if is_carbon and si_ref:
        si_parquet = Path(si_ref) / "metrics.parquet"
        if si_parquet.exists():
            si_df = pd.read_parquet(si_parquet)
            save_comparison_plots(
                carbon_df=metrics_df,
                si_df=si_df,
                plots_dir=out_dir / "plots",
                carbon_strategy=strategy,
            )

    # Animation
    if do_animate and snapshots:
        save_snapshots(snapshots, out_dir)
        save_animation(
            model_snapshots=snapshots,
            sugar_max=int(model.sugar_field.capacity.max()),
            output_path=out_dir / "animation",
            strategy=strategy,
        )
        # Comparison animation (carbon only, when Si snapshots are available)
        if is_carbon and si_ref:
            si_snaps = load_snapshots(Path(si_ref))
            if si_snaps:
                save_comparison_animation(
                    si_snapshots=si_snaps,
                    c_snapshots=snapshots,
                    output_path=out_dir / "animation_compare",
                    sugar_max=int(model.sugar_field.capacity.max()),
                )

    # Load C no-switch baseline for three-way comparison table
    baseline_df: pd.DataFrame | None = None
    c_ref = config.run.c_reference_dir
    if is_carbon and c_ref:
        c_ref_parquet = Path(c_ref) / "metrics.parquet"
        if c_ref_parquet.exists():
            baseline_df = pd.read_parquet(c_ref_parquet)

    # Success checks + report
    is_patched = is_carbon and "patched" in out_dir.name
    if is_carbon:
        checks = stage2_success_checks(
            metrics_df=metrics_df,
            config=config,
            seed_b_metrics=metrics_df2,
            patched=is_patched,
        )
    else:
        checks = stage1_success_checks(
            metrics_df=metrics_df,
            agent_states_df=agent_states_df,
            config=config,
            seed_b_metrics=metrics_df2,
        )

    report_path = generate_report(
        run_dir=out_dir,
        config=config,
        metrics_df=metrics_df,
        success_checks=checks,
        stage2=is_carbon,
        baseline_df=baseline_df,
    )

    print(f"\nReport written to: {report_path}")
    for c in checks:
        symbol = "PASS" if c.passed else "FAIL"
        print(f"  [{symbol}] {c.criterion}: {c.observed} (threshold: {c.threshold})")

    return report_path


if __name__ == "__main__":
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "configs/stage1_baseline.yaml"
    run_single(cfg_path)
