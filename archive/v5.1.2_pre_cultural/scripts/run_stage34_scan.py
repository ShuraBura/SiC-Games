"""Stage 3.4: 2D parameter scan, kappa x alpha (3x3 grid).

Simple batch loop — not a parallel infrastructure (Stage 5 BatchRunner is separate).

Grid:
  kappa in {1.0, 2.0, 3.0}  x-axis of heatmaps
  alpha in {1.0, 1.5, 2.0}  y-axis of heatmaps

Cell (2,2) = (kappa=2.0, alpha=1.5): loaded from confirmed Stage 3.3 parquet.
  Directive path: outputs/stage33_carbon_seed42/metrics.parquet
  Actual path:    outputs/stage3.3_seed42/metrics.parquet  (config name vs output dir)

Run order: kappa ascending, then alpha ascending within each kappa.
Cell (1,1) verified before proceeding to full grid.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

# Ensure package is importable when run as a script
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from sic_games.config import Config
from sic_games.run import SugarWorld

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KAPPAS = [1.0, 2.0, 3.0]
ALPHAS = [1.0, 1.5, 2.0]

_ANCHOR_PARQUET = _REPO_ROOT / "outputs" / "stage3.3_seed42" / "metrics.parquet"
_ANCHOR_KAPPA   = 2.0
_ANCHOR_ALPHA   = 1.5

_SCAN_OUT  = _REPO_ROOT / "outputs" / "stage34_scan_seed42"
_TAIL_N    = 100    # final N steps for observable averages

# Base config: Stage 3.3 biparental canonical (all params except kappa / alpha)
_BASE_CONFIG_RAW = {
    "seed": 42,
    "world": {
        "grid_size": [50, 50],
        "toroidal": True,
        "sugar_peaks": [[10, 40], [40, 10]],
        "max_sugar_capacity": 4,
        "band_width_k": 6,
        "growth_rate_alpha": 1,
    },
    "agents": {
        "initial_population": 250,
        "vision_dist": [1, 6],
        "metabolic_rate_dist": [1, 4],
        "max_age_dist": [60, 100],
        "initial_wealth_dist": [5, 25],
        "phi_mean": 0.5, "phi_std": 0.2,
        "psi_mean": 0.5, "psi_std": 0.2,
        "c1_mean":  0.5, "c1_std":  0.2,
        "c2_mean":  0.5, "c2_std":  0.2,
    },
    "decision": {"strategy": "carbon"},
    "carbon": {
        "sigma_base": 0.5,
        "cred_scale": 10.0,
        "cred_decay": 0.01,
        "epsilon": 0.01,
        "cred_bonus_per_participant": 1.0,
        "velocity_tau": 10,
        "velocity_scale": 1.0,
        "f_C": 0.25,
        "status_amplification_beta": 1.0,
        # kappa and matthew_alpha overridden per cell
    },
    "joint_task": {"distance_d": 1, "capacity_threshold": 4},
    "reproduction": {"mode": "biparental", "parent_radius": 3, "inherit_sigma": 0.05},
    "run": {"n_steps": 1000, "metrics_every": 1},
    "visualization": {"animate": False, "save_static_plots": False},
}


def _cell_tag(kappa: float, alpha: float) -> str:
    k = str(kappa).replace(".", "")
    a = str(alpha).replace(".", "")
    return f"k{k}_a{a}"


def _out_dir(kappa: float, alpha: float) -> Path:
    return _REPO_ROOT / "outputs" / f"stage34_{_cell_tag(kappa, alpha)}_seed42"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run_cell(kappa: float, alpha: float) -> pd.DataFrame:
    raw = {**_BASE_CONFIG_RAW}
    raw["carbon"] = {**_BASE_CONFIG_RAW["carbon"], "kappa": kappa, "matthew_alpha": alpha}
    out = _out_dir(kappa, alpha)
    raw["run"] = {"n_steps": 1000, "metrics_every": 1, "output_dir": str(out)}
    cfg = Config.model_validate(raw)
    out.mkdir(parents=True, exist_ok=True)
    world = SugarWorld(cfg)
    df = world.run()
    df.to_parquet(out / "metrics.parquet", index=False)
    return df


def _load_anchor() -> pd.DataFrame:
    if not _ANCHOR_PARQUET.exists():
        raise FileNotFoundError(
            f"Stage 3.3 anchor parquet not found: {_ANCHOR_PARQUET}\n"
            f"Run stage33.py first or check path."
        )
    return pd.read_parquet(_ANCHOR_PARQUET)


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def _tail_mean(df: pd.DataFrame, col: str) -> float:
    return float(df[col].iloc[-_TAIL_N:].mean())


def _observables(df: pd.DataFrame) -> dict:
    return {
        "gini_cred":        _tail_mean(df, "gini_cred"),
        "deaths_starvation": _tail_mean(df, "deaths_starvation"),
        "joint_task_count": _tail_mean(df, "joint_task_count"),
        "std_phi":          _tail_mean(df, "std_phi"),
        "mean_sigma":       _tail_mean(df, "mean_sigma"),
    }


def _passes(obs: dict) -> bool:
    return (
        0.60 <= obs["gini_cred"]         <= 0.85
        and 2.0 <= obs["deaths_starvation"] <= 3.5
        and 20  <= obs["joint_task_count"]  <= 45
        and obs["std_phi"] > 0.08
    )


# ---------------------------------------------------------------------------
# Cred trajectory diagnostic
# ---------------------------------------------------------------------------

def _cred_growth_rate(df: pd.DataFrame) -> float:
    """Mean cred growth rate per 100 steps, measured over t=500-1000."""
    sub = df[df["step"] >= 500]
    if len(sub) < 200:
        return float("nan")
    early = sub["mean_cred"].iloc[:100].mean()
    late  = sub["mean_cred"].iloc[-100:].mean()
    if early == 0:
        return float("nan")
    return 100.0 * (late - early) / early   # percent per 100 steps


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def _fmt(v: float, decimals: int = 3) -> str:
    return f"{v:.{decimals}f}"


def _heatmap_observable(
    grid: np.ndarray,
    lo: float | None,
    hi: float | None,
    title: str,
    label: str,
    labels_grid: list[list[str]],
    out_path: Path,
) -> None:
    """Single observable heatmap. Green = in range, red = out of range."""
    fig, ax = plt.subplots(figsize=(6, 5))

    # Build pass mask
    mask = np.ones_like(grid, dtype=float)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            v = grid[i, j]
            in_range = True
            if lo is not None and v < lo:
                in_range = False
            if hi is not None and v > hi:
                in_range = False
            mask[i, j] = 1.0 if in_range else 0.0

    cmap = mcolors.ListedColormap(["#d73027", "#1a9850"])
    im = ax.imshow(mask, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    # Cell labels (numeric values)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            ax.text(j, i, labels_grid[i][j], ha="center", va="center",
                    fontsize=11, fontweight="bold", color="white")

    ax.set_xticks(range(len(KAPPAS)))
    ax.set_xticklabels([f"k={k}" for k in KAPPAS])
    ax.set_yticks(range(len(ALPHAS)))
    ax.set_yticklabels([f"a={a}" for a in ALPHAS])
    ax.set_xlabel("kappa")
    ax.set_ylabel("alpha")
    ax.set_title(title)

    if lo is not None or hi is not None:
        rng_str = f"[{lo if lo is not None else '-inf'}, {hi if hi is not None else 'inf'}]"
        ax.text(0.5, -0.13, f"Target range: {rng_str}", transform=ax.transAxes,
                ha="center", fontsize=9, color="gray")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _heatmap_passfail(pass_grid: np.ndarray, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    cmap = mcolors.ListedColormap(["#d73027", "#1a9850"])
    ax.imshow(pass_grid, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for i in range(pass_grid.shape[0]):
        for j in range(pass_grid.shape[1]):
            txt = "PASS" if pass_grid[i, j] else "FAIL"
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=13, fontweight="bold", color="white")
    ax.set_xticks(range(len(KAPPAS)))
    ax.set_xticklabels([f"k={k}" for k in KAPPAS])
    ax.set_yticks(range(len(ALPHAS)))
    ax.set_yticklabels([f"a={a}" for a in ALPHAS])
    ax.set_xlabel("kappa")
    ax.set_ylabel("alpha")
    ax.set_title("Stage 3.4 — Pass/fail (all 4 criteria)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _build_report(results: dict[tuple, dict]) -> None:
    _SCAN_OUT.mkdir(parents=True, exist_ok=True)

    # Build grids: rows = alpha index, cols = kappa index
    obs_keys = ["gini_cred", "deaths_starvation", "joint_task_count", "std_phi", "mean_sigma"]
    grids = {k: np.zeros((len(ALPHAS), len(KAPPAS))) for k in obs_keys}
    pass_grid = np.zeros((len(ALPHAS), len(KAPPAS)))
    growth_grid = np.full((len(ALPHAS), len(KAPPAS)), float("nan"))
    label_grids = {k: [[""]*len(KAPPAS) for _ in ALPHAS] for k in obs_keys}

    for (ki, ai), r in results.items():
        obs  = r["obs"]
        for k in obs_keys:
            grids[k][ai, ki] = obs[k]
            label_grids[k][ai][ki] = _fmt(obs[k])
        pass_grid[ai, ki] = 1.0 if r["pass"] else 0.0
        growth_grid[ai, ki] = r["growth"]

    # Generate heatmaps
    specs = [
        ("gini_cred",         0.60, 0.85, "Gini Cred",          "heatmap_gini_cred.png"),
        ("deaths_starvation", 2.0,  3.5,  "Deaths/step (starv)","heatmap_deaths.png"),
        ("joint_task_count",  20.0, 45.0, "Joint tasks/step",   "heatmap_jt.png"),
        ("std_phi",           0.08, None, "std(phi)",            "heatmap_std_phi.png"),
    ]
    for col, lo, hi, title, fname in specs:
        _heatmap_observable(
            grids[col], lo, hi, title, col, label_grids[col],
            _SCAN_OUT / fname,
        )
    _heatmap_passfail(pass_grid, _SCAN_OUT / "heatmap_passfail.png")

    # Markdown report
    lines = [
        f"# Stage 3.4 — 2D Parameter Scan: kappa x alpha",
        f"",
        f"**Date:** {date.today().isoformat()}  ",
        f"**Seed:** 42  ",
        f"**Steps:** 1000  ",
        f"**Grid:** kappa in {{1.0, 2.0, 3.0}} x alpha in {{1.0, 1.5, 2.0}}  ",
        f"**Cell (2,2):** loaded from `outputs/stage3.3_seed42/metrics.parquet` (no re-run)",
        f"",
        f"## Pass/fail criteria",
        f"",
        f"| Observable | Target range |",
        f"|---|---|",
        f"| Gini Cred | [0.60, 0.85] |",
        f"| Deaths/step (starvation) | [2.0, 3.5] |",
        f"| Joint tasks/step | [20, 45] |",
        f"| std(phi) | > 0.08 |",
        f"",
        f"## Full metrics table (tail {_TAIL_N} steps)",
        f"",
        f"| Cell | kappa | alpha | Gini Cred | Starvation | Joint tasks | std(phi) | Mean sigma | Pass? |",
        f"|---|---|---|---|---|---|---|---|---|",
    ]

    cell_labels = {(1, 1): "(1,1)", (1, 2): "(1,2)", (1, 3): "(1,3)",
                   (2, 1): "(2,1)", (2, 2): "(2,2)*", (2, 3): "(2,3)",
                   (3, 1): "(3,1)", (3, 2): "(3,2)", (3, 3): "(3,3)"}
    for ki, kappa in enumerate(KAPPAS):
        for ai, alpha in enumerate(ALPHAS):
            r = results[(ki, ai)]
            obs = r["obs"]
            clabel = cell_labels.get((ki + 1, ai + 1), f"({ki+1},{ai+1})")
            p = "PASS" if r["pass"] else "FAIL"
            lines.append(
                f"| {clabel} | {kappa} | {alpha} "
                f"| {obs['gini_cred']:.4f} "
                f"| {obs['deaths_starvation']:.4f} "
                f"| {obs['joint_task_count']:.2f} "
                f"| {obs['std_phi']:.4f} "
                f"| {obs['mean_sigma']:.4f} "
                f"| {p} |"
            )

    lines += [
        f"",
        f"\\* Cell (2,2) = confirmed Stage 3.3 biparental anchor (kappa=2.0, alpha=1.5).",
        f"",
        f"## Cred trajectory diagnostic (t=500-1000)",
        f"",
        f"Growth rate = percent change in mean_cred per 100 steps over t=500-1000.",
        f"Flag threshold: Gini Cred > 0.85 OR growth > 5% per 100 steps.",
        f"",
        f"| Cell | kappa | alpha | Growth rate (%/100 steps) | Flag? |",
        f"|---|---|---|---|---|",
    ]

    for ki, kappa in enumerate(KAPPAS):
        for ai, alpha in enumerate(ALPHAS):
            r = results[(ki, ai)]
            obs = r["obs"]
            g = growth_grid[ai, ki]
            g_str = f"{g:.2f}" if not np.isnan(g) else "n/a"
            flag = (obs["gini_cred"] > 0.85) or (not np.isnan(g) and g > 5.0)
            flag_str = "FLAG" if flag else "-"
            clabel = cell_labels.get((ki + 1, ai + 1), f"({ki+1},{ai+1})")
            lines.append(
                f"| {clabel} | {kappa} | {alpha} | {g_str} | {flag_str} |"
            )

    lines += [
        f"",
        f"## Plots",
        f"",
        f"- `heatmap_passfail.png` — primary pass/fail overlay",
        f"- `heatmap_gini_cred.png` — Gini Cred heatmap",
        f"- `heatmap_deaths.png` — starvation deaths/step heatmap",
        f"- `heatmap_jt.png` — joint tasks/step heatmap",
        f"- `heatmap_std_phi.png` — std(phi) heatmap",
        f"",
        f"## Canonical cell selection",
        f"",
        f"Supervisor selects canonical (kappa, alpha) from above. The mean_sigma of the",
        f"selected cell becomes the new sigma_Si for Stage 4.",
        f"Claude Code does not select the canonical cell.",
    ]

    report_path = _SCAN_OUT / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report -> {report_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=== Stage 3.4: 2D parameter scan kappa x alpha ===")
    print(f"Grid: kappa={KAPPAS} x alpha={ALPHAS}")
    print(f"Cell (2,2) = anchor, loaded from parquet (no re-run)")

    results: dict[tuple, dict] = {}

    # Run cell (1,1) first and verify health before proceeding
    print("\n[Check] Running cell (1,1): kappa=1.0, alpha=1.0 ...")
    df_11 = _run_cell(1.0, 1.0)
    pop_11 = df_11["population"].iloc[-100:].mean()
    if pop_11 < 200 or pop_11 > 300:
        print(f"ABORT: cell (1,1) population out of range: {pop_11:.1f}")
        sys.exit(1)
    print(f"  cell (1,1) OK: population tail mean = {pop_11:.1f}")
    obs_11 = _observables(df_11)
    results[(0, 0)] = {
        "obs": obs_11,
        "pass": _passes(obs_11),
        "growth": _cred_growth_rate(df_11),
    }

    # Remaining cells in order (skip (1,1) already done, skip anchor (2,2))
    for ki, kappa in enumerate(KAPPAS):
        for ai, alpha in enumerate(ALPHAS):
            if (ki, ai) == (0, 0):  # already done
                continue
            if kappa == _ANCHOR_KAPPA and alpha == _ANCHOR_ALPHA:
                continue  # anchor: load from parquet below
            print(f"  Running cell ({ki+1},{ai+1}): kappa={kappa}, alpha={alpha} ...")
            df = _run_cell(kappa, alpha)
            pop = df["population"].iloc[-100:].mean()
            print(f"    population tail mean = {pop:.1f}")
            obs = _observables(df)
            results[(ki, ai)] = {
                "obs": obs,
                "pass": _passes(obs),
                "growth": _cred_growth_rate(df),
            }

    # Load anchor cell (2,2)
    ki_anc = KAPPAS.index(_ANCHOR_KAPPA)
    ai_anc = ALPHAS.index(_ANCHOR_ALPHA)
    print(f"\n  Loading anchor cell (2,2): kappa={_ANCHOR_KAPPA}, alpha={_ANCHOR_ALPHA} from parquet ...")
    df_anc = _load_anchor()
    obs_anc = _observables(df_anc)
    results[(ki_anc, ai_anc)] = {
        "obs": obs_anc,
        "pass": _passes(obs_anc),
        "growth": _cred_growth_rate(df_anc),
    }
    print(f"    anchor loaded: {obs_anc}")

    print("\nGenerating report and heatmaps ...")
    _build_report(results)

    # Summary
    n_pass = sum(1 for r in results.values() if r["pass"])
    print(f"\nScan complete: {n_pass}/9 cells pass all criteria.")
    print("Awaiting supervisor canonical cell selection.")


if __name__ == "__main__":
    main()
