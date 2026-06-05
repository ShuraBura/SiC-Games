from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sic_games.world import SugarField

# Canonical colours per strategy — used consistently across all plots
STRATEGY_COLOR = {
    "greedy": "steelblue",
    "si_bounded": "steelblue",
    "carbon": "darkorange",
}
STRATEGY_LABEL = {
    "greedy": "greedy-Si",
    "si_bounded": "bounded-Si",
    "carbon": "carbon-C",
}


def _agent_color(strategy: str) -> str:
    return STRATEGY_COLOR.get(strategy, "steelblue")


def _title(base: str, strategy: str) -> str:
    return f"{base} ({STRATEGY_LABEL.get(strategy, strategy)})"


def save_snapshots(snapshots: list, out_dir: Path) -> Path:
    """Persist animation snapshots to disk so comparison animations can load them."""
    path = Path(out_dir) / "snapshots.pkl"
    with open(path, "wb") as f:
        pickle.dump(snapshots, f, protocol=4)
    return path


def load_snapshots(run_dir: Path) -> list | None:
    path = Path(run_dir) / "snapshots.pkl"
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def save_comparison_animation(
    si_snapshots: list,
    c_snapshots: list,
    output_path: Path,
    sugar_max: int,
) -> None:
    """Side-by-side animation: Si (blue, left) vs C (orange, right)."""
    from matplotlib.animation import FuncAnimation, FFMpegWriter

    n_frames = min(len(si_snapshots), len(c_snapshots))
    si_color = STRATEGY_COLOR["greedy"]
    c_color = STRATEGY_COLOR["carbon"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax_si, ax_c = axes

    def _init_panel(ax, snapshots, color, label):
        sugar, agents = snapshots[0]
        im = ax.imshow(
            sugar.T, origin="lower", cmap="YlOrRd",
            vmin=0, vmax=sugar_max, interpolation="nearest",
        )
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        xs = [p[0] for p in agents]
        ys = [p[1] for p in agents]
        sc = ax.scatter(xs, ys, s=4, c=color, alpha=0.7, label=label)
        ax.set_xlim(0, sugar.shape[0])
        ax.set_ylim(0, sugar.shape[1])
        ax.set_aspect("equal")
        ax.set_title(label)
        ax.legend(loc="upper right", markerscale=3)
        return im, sc

    im_si, sc_si = _init_panel(ax_si, si_snapshots, si_color, STRATEGY_LABEL["greedy"])
    im_c, sc_c = _init_panel(ax_c, c_snapshots, c_color, STRATEGY_LABEL["carbon"])
    frame_title = fig.suptitle("Step 0")

    def update(i: int):
        s_sugar, s_agents = si_snapshots[i]
        c_sugar, c_agents = c_snapshots[i]
        im_si.set_data(s_sugar.T)
        im_c.set_data(c_sugar.T)
        for sc, agents in [(sc_si, s_agents), (sc_c, c_agents)]:
            xs = [p[0] for p in agents]
            ys = [p[1] for p in agents]
            sc.set_offsets(np.column_stack([xs, ys]) if xs else np.empty((0, 2)))
        frame_title.set_text(f"Step {i * 5}")
        return im_si, im_c, sc_si, sc_c, frame_title

    anim = FuncAnimation(fig, update, frames=n_frames, interval=100, blit=False)
    output_path = Path(output_path)
    try:
        writer = FFMpegWriter(fps=10)
        anim.save(str(output_path.with_suffix(".mp4")), writer=writer)
    except Exception:
        anim.save(str(output_path.with_suffix(".gif")), writer="pillow", fps=10)
    plt.close(fig)


def save_stage2_plots(
    metrics_df: pd.DataFrame,
    plots_dir: Path,
    strategy: str = "carbon",
) -> None:
    """Save the four additional Stage 2 diagnostic plots."""
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    steps = metrics_df["step"]
    color = _agent_color(strategy)

    for col, ylabel, base_title, fname in [
        ("mean_cred", "Mean Cred", "Mean Cred over time", "mean_cred.png"),
        ("gini_cred", "Gini (Cred)", "Gini of Cred over time", "gini_cred.png"),
        ("mean_sigma", "Mean sigma", "Mean decision temperature over time", "mean_sigma.png"),
        ("joint_task_count", "Joint tasks / step", "Joint-task events per step", "joint_task_count.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(steps, metrics_df[col], color=color)
        ax.set_xlabel("Step")
        ax.set_ylabel(ylabel)
        ax.set_title(_title(base_title, strategy))
        fig.tight_layout()
        fig.savefig(plots_dir / fname, dpi=100)
        plt.close(fig)


def save_static_plots(
    metrics_df: pd.DataFrame,
    agent_states_df: pd.DataFrame,
    sugar_field: SugarField,
    plots_dir: Path,
    strategy: str = "greedy",
) -> None:
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    steps = metrics_df["step"]
    color = _agent_color(strategy)

    # Population over time
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(steps, metrics_df["population"], color=color)
    ax.set_xlabel("Step")
    ax.set_ylabel("Population")
    ax.set_title(_title("Population over time", strategy))
    ax.set_ylim(0, max(300, metrics_df["population"].max() * 1.1))
    fig.tight_layout()
    fig.savefig(plots_dir / "population.png", dpi=100)
    plt.close(fig)

    # Gini over time
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(steps, metrics_df["gini_wealth"], color=color)
    ax.axhline(0.4, color="gray", linestyle="--", linewidth=0.8, label="target band")
    ax.axhline(0.6, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Step")
    ax.set_ylabel("Gini coefficient")
    ax.set_title(_title("Wealth Gini over time", strategy))
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(plots_dir / "gini.png", dpi=100)
    plt.close(fig)

    # Spatial dispersion over time
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(steps, metrics_df["spatial_dispersion"], color=color)
    ax.set_xlabel("Step")
    ax.set_ylabel("Spatial dispersion")
    ax.set_title(_title("Agent spatial dispersion over time", strategy))
    fig.tight_layout()
    fig.savefig(plots_dir / "dispersion.png", dpi=100)
    plt.close(fig)

    # Wealth histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(agent_states_df["wealth"], bins=40, color=color, edgecolor="none")
    ax.set_xlabel("Wealth")
    ax.set_ylabel("Count")
    ax.set_title(_title("Wealth distribution at final step", strategy))
    fig.tight_layout()
    fig.savefig(plots_dir / "wealth_histogram.png", dpi=100)
    plt.close(fig)

    # Final agent positions on sugar capacity field
    fig, ax = plt.subplots(figsize=(7, 7))
    capacity_display = sugar_field.capacity.T  # transpose: x→col, y→row
    im = ax.imshow(
        capacity_display,
        origin="lower",
        cmap="YlOrRd",
        interpolation="nearest",
        vmin=0,
        vmax=sugar_field.capacity.max(),
    )
    ax.scatter(
        agent_states_df["x"],
        agent_states_df["y"],
        s=4,
        c=color,
        alpha=0.7,
        label=STRATEGY_LABEL.get(strategy, strategy),
    )
    plt.colorbar(im, ax=ax, label="Sugar capacity")
    ax.set_title(_title("Final agent positions on sugar capacity field", strategy))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper right", markerscale=3)
    fig.tight_layout()
    fig.savefig(plots_dir / "final_positions.png", dpi=100)
    plt.close(fig)


def save_comparison_plots(
    carbon_df: pd.DataFrame,
    si_df: pd.DataFrame,
    plots_dir: Path,
    carbon_strategy: str = "carbon",
) -> None:
    """Overlay plots: Si (blue) vs C (orange) on shared axes for four key metrics."""
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)

    si_color = STRATEGY_COLOR["greedy"]
    c_color = STRATEGY_COLOR["carbon"]
    si_label = STRATEGY_LABEL["greedy"]
    c_label = STRATEGY_LABEL.get(carbon_strategy, carbon_strategy)

    for col, ylabel, base_title, fname in [
        ("gini_wealth", "Gini coefficient", "Gini Wealth over time", "compare_gini_wealth.png"),
        ("mean_wealth", "Mean wealth", "Mean Wealth over time", "compare_mean_wealth.png"),
        ("spatial_dispersion", "Spatial dispersion", "Spatial Dispersion over time", "compare_dispersion.png"),
        ("deaths_starvation", "Deaths / step", "Starvation Deaths over time", "compare_starvation.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(si_df["step"], si_df[col], color=si_color, alpha=0.85, label=si_label, linewidth=1.2)
        ax.plot(carbon_df["step"], carbon_df[col], color=c_color, alpha=0.85, label=c_label, linewidth=1.2)
        ax.set_xlabel("Step")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{base_title} — Si vs C (seed={carbon_df['step'].iloc[0] if False else '42'})")
        ax.legend()
        fig.tight_layout()
        fig.savefig(plots_dir / fname, dpi=100)
        plt.close(fig)


def save_animation(
    model_snapshots: list[tuple[np.ndarray, list[tuple[int, int]]]],
    sugar_max: int,
    output_path: Path,
    strategy: str = "greedy",
) -> None:
    """Save an animation of (sugar_field, agent_positions) snapshots."""
    from matplotlib.animation import FuncAnimation, FFMpegWriter

    color = _agent_color(strategy)
    strat_label = STRATEGY_LABEL.get(strategy, strategy)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    ax_sugar, ax_agents = axes

    first_sugar, first_agents = model_snapshots[0]
    im_sugar = ax_sugar.imshow(
        first_sugar.T, origin="lower", cmap="YlOrRd",
        vmin=0, vmax=sugar_max, interpolation="nearest"
    )
    ax_sugar.set_title("Sugar field")
    plt.colorbar(im_sugar, ax=ax_sugar)

    xs = [p[0] for p in first_agents]
    ys = [p[1] for p in first_agents]
    scatter = ax_agents.scatter(xs, ys, s=4, c=color, alpha=0.7, label=strat_label)
    ax_agents.set_xlim(0, first_sugar.shape[0])
    ax_agents.set_ylim(0, first_sugar.shape[1])
    ax_agents.set_title(_title("Agent positions", strategy))
    ax_agents.set_aspect("equal")
    ax_agents.legend(loc="upper right", markerscale=3)

    frame_title = fig.suptitle(f"Step 0 — {strat_label}")

    def update(frame_idx: int):
        sugar, agents = model_snapshots[frame_idx]
        im_sugar.set_data(sugar.T)
        xs = [p[0] for p in agents]
        ys = [p[1] for p in agents]
        scatter.set_offsets(np.column_stack([xs, ys]) if xs else np.empty((0, 2)))
        frame_title.set_text(f"Step {frame_idx} — {strat_label}")
        return im_sugar, scatter, frame_title

    anim = FuncAnimation(fig, update, frames=len(model_snapshots), interval=100, blit=False)

    output_path = Path(output_path)
    try:
        writer = FFMpegWriter(fps=10)
        anim.save(str(output_path.with_suffix(".mp4")), writer=writer)
    except Exception:
        anim.save(str(output_path.with_suffix(".gif")), writer="pillow", fps=10)

    plt.close(fig)
