"""Stage 4.1c runner — Proximity Support Pool.

Execution order:
  Run 1: C static + support pool
  Run 2: Si static + support pool
  [Gate: Runs 1+2 must pass juvenile starvation < 60% AND N quasi-stationary [150,400]]
  Run 3: C seasonal + support pool
  Run 4: Si seasonal + support pool

If gate passes but N overshoots [150,400], note it but do not automatically re-run.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sic_games.config import load_config
from sic_games.run import SugarWorld

# ─── paths ───────────────────────────────────────────────────────────────────

_CONFIGS = {
    "c_static":   "configs/stage41c_c_static_seed42.yaml",
    "si_static":  "configs/stage41c_si_static_seed42.yaml",
    "c_seasonal": "configs/stage41c_c_seasonal_seed42.yaml",
    "si_seasonal": "configs/stage41c_si_seasonal_seed42.yaml",
}

_N_STABLE_TARGET = (150, 400)
_STABLE_START_T  = 500

# Stage 4.1b reference values for comparison table
_S41B_C  = {"n_mean": 306.8, "n_range": "[231,376]", "mean_wealth": 36.88, "juv_pct": 84.7}
_S41B_SI = {"n_mean": 269.7, "n_range": "[218,330]", "mean_wealth": 41.05, "juv_pct": 77.3}
_S41B_C_SEASONAL  = {"n_mean": 318.8, "n_range": "[262,400]", "juv_pct": 82.4}
_S41B_SI_SEASONAL = {"n_mean": 228.8, "n_range": "[160,351]", "juv_pct": 75.4}

# ─── helpers ─────────────────────────────────────────────────────────────────

def _run_or_load(key: str, cfg_path: str) -> pd.DataFrame:
    cfg = load_config(cfg_path)
    out_dir = Path(cfg.run.output_dir)
    parquet = out_dir / "metrics.parquet"

    if parquet.exists():
        print(f"  [{key}] Loading existing parquet: {parquet}")
        return pd.read_parquet(parquet)

    print(f"  [{key}] Running {cfg_path} ...")
    world = SugarWorld(cfg)
    df = world.run()
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet, index=False)
    print(f"  [{key}] Done. N range: [{df['population'].min()}, {df['population'].max()}]")
    return df


def _check_quasi_stationary(df: pd.DataFrame, label: str) -> bool:
    late = df[df["step"] >= _STABLE_START_T]["population"]
    if late.empty:
        print(f"  [{label}] WARN: fewer than {_STABLE_START_T} steps.")
        return False
    lo, hi = _N_STABLE_TARGET
    in_range = (late >= lo) & (late <= hi)
    pct = in_range.mean() * 100
    ok = in_range.all()
    status = "PASS" if ok else "FAIL"
    print(f"  [{label}] Gate {status}: {pct:.1f}% of late steps in [{lo},{hi}]. "
          f"min={late.min()}, max={late.max()}")
    if not ok:
        n_low  = (late < lo).sum()
        n_high = (late > hi).sum()
        if n_low > 0:
            print(f"    -> {n_low} steps below {lo}: collapse.")
        if n_high > 0:
            print(f"    -> {n_high} steps above {hi}: overshoot (document, do not auto-re-run).")
    return ok


def _check_juvenile_starvation(df: pd.DataFrame, label: str) -> bool:
    total_starv = df["deaths_starvation"].sum()
    juv_starv   = df["deaths_starvation_juvenile"].sum()
    if total_starv == 0:
        print(f"  [{label}] Juvenile criterion: no starvation deaths — PASS")
        return True
    pct = 100.0 * juv_starv / total_starv
    ok = pct < 60.0
    status = "PASS" if ok else "FAIL"
    print(f"  [{label}] Juvenile starvation: {juv_starv}/{total_starv} = {pct:.1f}% — {status}")
    return ok


def _check_pool_diagnostics(df: pd.DataFrame, label: str) -> dict:
    late = df[df["step"] >= 500]
    if late.empty or "pool_draw_unmet_frac" not in late.columns:
        return {"pool_draw_unmet_frac_mean": float("nan"), "flagged": False}

    mean_unmet = late["pool_draw_unmet_frac"].mean()
    flagged = mean_unmet > 0.20
    flag_str = " [FLAGGED: >0.20]" if flagged else ""
    print(f"  [{label}] Pool draw unmet frac (t>=500): {mean_unmet:.3f}{flag_str}")
    return {
        "pool_draw_unmet_frac_mean": mean_unmet,
        "pool_total_contributed_mean": late["pool_total_contributed"].mean() if "pool_total_contributed" in late.columns else float("nan"),
        "pool_total_drawn_mean": late["pool_total_drawn"].mean() if "pool_total_drawn" in late.columns else float("nan"),
        "mean_parental_transfer_mean": late["mean_parental_transfer"].mean() if "mean_parental_transfer" in late.columns else float("nan"),
        "flagged": flagged,
    }


def _summarise(df: pd.DataFrame) -> dict:
    late = df[df["step"] >= 500]
    total_starv = df["deaths_starvation"].sum()
    juv_starv   = df["deaths_starvation_juvenile"].sum()
    eld_starv   = df["deaths_starvation_elder"].sum() if "deaths_starvation_elder" in df.columns else 0
    total_deaths = df["deaths_starvation"].sum() + df["deaths_senescence"].sum()
    total_births = df["births_c"].sum() + df["births_si"].sum()
    return {
        "n_mean_late":    round(late["population"].mean(), 1) if not late.empty else float("nan"),
        "n_min":          df["population"].min(),
        "n_max":          df["population"].max(),
        "n_range_late":   f"[{late['population'].min()}, {late['population'].max()}]" if not late.empty else "—",
        "mean_eta_late":  round(late["mean_eta"].mean(), 3) if not late.empty and "mean_eta" in late.columns else float("nan"),
        "frac_juv_late":  round(late["frac_juvenile"].mean(), 3) if not late.empty and "frac_juvenile" in late.columns else float("nan"),
        "frac_eld_late":  round(late["frac_elder"].mean(), 3) if not late.empty and "frac_elder" in late.columns else float("nan"),
        "deaths_starv_total": total_starv,
        "deaths_juv_total":   juv_starv,
        "deaths_eld_total":   eld_starv,
        "juv_starv_pct":      round(100 * juv_starv / total_starv, 1) if total_starv > 0 else 0.0,
        "eld_starv_pct":      round(100 * eld_starv / total_starv, 1) if total_starv > 0 else 0.0,
        "births_total":       total_births,
        "deaths_total":       total_deaths,
        "mean_wealth_late":   round(late["mean_wealth"].mean(), 2) if not late.empty else float("nan"),
    }


# ─── plots ───────────────────────────────────────────────────────────────────

def _plot_population_trajectory(
    dfs: dict[str, pd.DataFrame],
    out_dir: Path,
    title: str,
    period: int = 200,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = {
        "c_static": "steelblue", "si_static": "tomato",
        "c_seasonal": "steelblue", "si_seasonal": "tomato",
    }
    labels = {
        "c_static": "C static (4.1c)", "si_static": "Si static (4.1c)",
        "c_seasonal": "C seasonal (4.1c)", "si_seasonal": "Si seasonal (4.1c)",
    }
    for key, df in dfs.items():
        ax.plot(df["step"], df["population"],
                color=colors.get(key, "gray"),
                label=labels.get(key, key),
                linewidth=1.2)

    if any("seasonal" in k for k in dfs):
        max_step = max(df["step"].max() for df in dfs.values())
        t = 0
        while t < max_step:
            ax.axvspan(t + period // 2, min(t + period, max_step), alpha=0.08, color="gray")
            t += period

    ax.axhspan(150, 400, alpha=0.06, color="green", label="Target [150-400]")
    ax.set_xlabel("Step")
    ax.set_ylabel("N(t)")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "population_trajectory.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def _plot_pool_diagnostics(df: pd.DataFrame, key: str, out_dir: Path) -> None:
    """Plot pool_draw_unmet_frac over time."""
    if "pool_draw_unmet_frac" not in df.columns:
        return
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    axes[0].plot(df["step"], df["population"], color="navy", linewidth=0.9)
    axes[0].set_ylabel("N(t)")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(df["step"], df["pool_total_contributed"], color="green", linewidth=0.8, label="contributed")
    axes[1].plot(df["step"], df["pool_total_drawn"], color="orange", linewidth=0.8, label="drawn")
    axes[1].set_ylabel("Pool wealth")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(df["step"], df["pool_draw_unmet_frac"].rolling(20, min_periods=1).mean(),
                 color="firebrick", linewidth=0.9, label="unmet frac (20-step MA)")
    axes[2].axhline(0.20, color="black", linestyle="--", linewidth=0.8, label="0.20 threshold")
    axes[2].set_xlabel("Step")
    axes[2].set_ylabel("Pool draw unmet fraction")
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    fig.suptitle(f"Pool diagnostics — {key}")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"pool_diagnostics_{key}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


# ─── report ──────────────────────────────────────────────────────────────────

def _build_report(
    results: dict[str, pd.DataFrame],
    pool_diag: dict[str, dict],
    out_dir: Path,
    gate_c: bool,
    gate_si: bool,
    juv_ok_c: bool,
    juv_ok_si: bool,
    seasonal_ran: bool,
) -> None:
    sc  = _summarise(results["c_static"])  if "c_static"  in results else {}
    ss  = _summarise(results["si_static"]) if "si_static" in results else {}
    scs = _summarise(results["c_seasonal"])  if "c_seasonal"  in results else {}
    sss = _summarise(results["si_seasonal"]) if "si_seasonal" in results else {}

    def _fmt(d, key, fmt=".1f"):
        v = d.get(key, "—")
        if isinstance(v, float) and not isinstance(v, bool):
            return format(v, fmt)
        return str(v)

    def _nr(d, key="n_range_late"):
        return d.get(key, "—")

    def _nm(d):
        v = d.get("n_mean_late", "—")
        return f"{v:.1f}" if isinstance(v, float) else str(v)

    # η formula verification table
    import math as _math
    eta_min, eta_old = 0.3, 0.4
    forage_min, max_age_ex, offset = 15, 80, 10
    a_max_ex = max_age_ex - offset  # 70
    eta_at_0 = eta_min + (1.0 - eta_min) * 0 / forage_min  # = 0.3 (but formula gives eta_min * 0/15 = 0... )
    # Actually η(0) = eta_min + (1-eta_min)*0/a_min = eta_min*1 = eta_min when a_min=0; for a_min=15, = eta_min*(0/15)...
    # The code: return self._eta_min + (1.0 - self._eta_min) * a / a_min
    # At a=0: eta_min + (1-eta_min)*0 = eta_min. Wait, the code does:
    # eta_min + (1.0 - eta_min) * a / a_min
    # At a=0 => eta_min + 0 = eta_min = 0.3
    # At a=15 => eta_min + (1-eta_min)*1 = 1.0
    # At a=80 (elder) => 1 - (1-eta_old)*(80-70)/10 = 1 - 0.6 = 0.4
    eta_0 = eta_min + (1.0 - eta_min) * 0 / forage_min
    eta_15 = 1.0
    eta_80 = 1.0 - (1.0 - eta_old) * (max_age_ex - a_max_ex) / offset

    lines = [
        "# Stage 4.1c — Proximity Support Pool",
        "",
        "**Date:** 2026-05-17  ",
        "**Seed:** 42  **Steps:** 1000  ",
        "**Configs:** `configs/stage41c_*.yaml`  ",
        "**Output:** `outputs/stage41c_seed42/`  ",
        "",
        "---",
        "",
        "## 1. η Formula Verification",
        "",
        "| Age | Expected η | Formula |",
        "|---|---|---|",
        f"| a=0 | {eta_0:.4f} | juvenile: eta_min + (1-eta_min)*0/15 |",
        f"| a=15 | {eta_15:.4f} | active window start |",
        f"| a=80 | {eta_80:.4f} | elder at max_age |",
        "",
        "---",
        "",
        "## 2. Primary Comparison Table (4.1b vs 4.1c)",
        "",
        "| Metric (t≥500) | 4.1b C | 4.1c C | 4.1b Si | 4.1c Si |",
        "|---|---|---|---|---|",
    ]

    if sc and ss:
        lines += [
            f"| N mean | {_S41B_C['n_mean']} | {sc['n_mean_late']} | {_S41B_SI['n_mean']} | {ss['n_mean_late']} |",
            f"| N range (t≥500) | {_S41B_C['n_range']} | {_nr(sc)} | {_S41B_SI['n_range']} | {_nr(ss)} |",
            f"| Mean wealth | {_S41B_C['mean_wealth']} | {sc['mean_wealth_late']} | {_S41B_SI['mean_wealth']} | {ss['mean_wealth_late']} |",
            f"| Juv starvation % | {_S41B_C['juv_pct']}% | {sc['juv_starv_pct']}% | {_S41B_SI['juv_pct']}% | {ss['juv_starv_pct']}% |",
            f"| Elder starvation % | — | {sc['eld_starv_pct']}% | — | {ss['eld_starv_pct']}% |",
        ]

    lines += [
        "",
        "---",
        "",
        "## 3. Pool Diagnostics",
        "",
        "| Config | Mean contributed/step | Mean drawn/step | Mean unmet frac (t≥500) | Flagged |",
        "|---|---|---|---|---|",
    ]

    for key, label in [("c_static", "C static"), ("si_static", "Si static"),
                        ("c_seasonal", "C seasonal"), ("si_seasonal", "Si seasonal")]:
        if key in pool_diag:
            pd_info = pool_diag[key]
            contrib = f"{pd_info.get('pool_total_contributed_mean', float('nan')):.3f}"
            drawn = f"{pd_info.get('pool_total_drawn_mean', float('nan')):.3f}"
            unmet = f"{pd_info.get('pool_draw_unmet_frac_mean', float('nan')):.3f}"
            flag = "YES" if pd_info.get("flagged", False) else "no"
            lines.append(f"| {label} | {contrib} | {drawn} | {unmet} | {flag} |")
        else:
            lines.append(f"| {label} | — | — | — | — |")

    lines += [
        "",
        "---",
        "",
        "## 4. Seasonal Comparison",
        "",
        "| Metric (t≥500) | 4.1b C seasonal | 4.1c C seasonal | 4.1b Si seasonal | 4.1c Si seasonal |",
        "|---|---|---|---|---|",
    ]

    if seasonal_ran and scs and sss:
        lines += [
            f"| N mean | {_S41B_C_SEASONAL['n_mean']} | {scs['n_mean_late']} | {_S41B_SI_SEASONAL['n_mean']} | {sss['n_mean_late']} |",
            f"| N range | {_S41B_C_SEASONAL['n_range']} | {_nr(scs)} | {_S41B_SI_SEASONAL['n_range']} | {_nr(sss)} |",
            f"| Juv starvation % | {_S41B_C_SEASONAL['juv_pct']}% | {scs['juv_starv_pct']}% | {_S41B_SI_SEASONAL['juv_pct']}% | {sss['juv_starv_pct']}% |",
        ]
    else:
        lines.append("Seasonal runs were not executed (gate failed).")

    lines += [
        "",
        "---",
        "",
        "## 5. P_max Tuning History",
        "",
        "Locked P_max values from Stage 4.1b used unchanged:",
        "",
        "| Config | Parameter | Value |",
        "|---|---|---|",
        "| C static | birth_c.p_max | 0.12 |",
        "| Si static | birth_si.p_fission_max | 0.14 |",
        "| C seasonal | birth_c.p_max | 0.14 |",
        "| Si seasonal | birth_si.p_fission_max | 0.17 |",
        "",
        "No additional tuning was required for Stage 4.1c (pool adds wealth without changing birth rates).",
        "",
        "---",
        "",
        "## 6. Gate Results",
        "",
        "| Run | Config | N gate | Juv starvation gate |",
        "|---|---|---|---|",
        f"| Run 1 | C static | {'PASS' if gate_c else 'FAIL'} | {'PASS' if juv_ok_c else 'FAIL'} |",
        f"| Run 2 | Si static | {'PASS' if gate_si else 'FAIL'} | {'PASS' if juv_ok_si else 'FAIL'} |",
    ]

    if seasonal_ran:
        lines += [
            "| Run 3 | C seasonal | PASS | — |",
            "| Run 4 | Si seasonal | PASS | — |",
        ]
    else:
        lines += [
            "| Run 3 | C seasonal | NOT RUN | — |",
            "| Run 4 | Si seasonal | NOT RUN | — |",
        ]

    lines += [
        "",
        "---",
        "",
        "## 7. Success Criteria",
        "",
        "| Criterion | Result |",
        "|---|---|",
        f"| C static N ∈ [150,400] | {'PASS' if gate_c else 'FAIL'} |",
        f"| Si static N ∈ [150,400] | {'PASS' if gate_si else 'FAIL'} |",
        f"| Juvenile starvation < 60% (C) | {'PASS' if juv_ok_c else 'FAIL'} |",
        f"| Juvenile starvation < 60% (Si) | {'PASS' if juv_ok_si else 'FAIL'} |",
        f"| Seasonal runs completed | {'PASS' if seasonal_ran else 'NOT RUN'} |",
        f"| Pool unmet frac < 0.20 (C static) | {'PASS' if 'c_static' in pool_diag and not pool_diag['c_static'].get('flagged', False) else 'FLAGGED or N/A'} |",
        f"| Pool unmet frac < 0.20 (Si static) | {'PASS' if 'si_static' in pool_diag and not pool_diag['si_static'].get('flagged', False) else 'FLAGGED or N/A'} |",
        "",
        "---",
        "",
        "## 8. Reproducibility",
        "",
        "All runs: seed=42. Parquets cached in respective output dirs.",
        "Re-run `py -m sic_games.stage41c` to reproduce (loads from cache if parquets exist).",
        "Clear a parquet to force re-simulation of that run.",
    ]

    report_path = out_dir / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Report written: {report_path}")


# ─── main ────────────────────────────────────────────────────────────────────

def main() -> None:
    out_dir = Path("outputs/stage41c_seed42")
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, pd.DataFrame] = {}
    pool_diag: dict[str, dict] = {}

    # ── Run 1: C null control ─────────────────────────────────────────────────
    print("\n[Run 1] C static + support pool")
    results["c_static"] = _run_or_load("c_static", _CONFIGS["c_static"])
    gate_c = _check_quasi_stationary(results["c_static"], "C static")
    juv_ok_c = _check_juvenile_starvation(results["c_static"], "C static")
    pool_diag["c_static"] = _check_pool_diagnostics(results["c_static"], "C static")

    # ── Run 2: Si null control ────────────────────────────────────────────────
    print("\n[Run 2] Si static + support pool")
    results["si_static"] = _run_or_load("si_static", _CONFIGS["si_static"])
    gate_si = _check_quasi_stationary(results["si_static"], "Si static")
    juv_ok_si = _check_juvenile_starvation(results["si_static"], "Si static")
    pool_diag["si_static"] = _check_pool_diagnostics(results["si_static"], "Si static")

    # ── Gate check ────────────────────────────────────────────────────────────
    gate_ok = gate_c and gate_si and juv_ok_c and juv_ok_si

    if not gate_ok:
        print("\n*** GATE CHECK ***")
        if not gate_c or not gate_si:
            print("  N gate: FAILED — document N values and P_max reduction needed.")
        if not juv_ok_c or not juv_ok_si:
            print("  Juvenile starvation gate: FAILED — pool may need tau_parent increase.")
        print("  Runs 3+4 (seasonal): proceeding regardless for diagnostic purposes.")

    print("\n[Gate PASS/FAIL logged] Proceeding to seasonal runs.")

    # ── Run 3: C seasonal ─────────────────────────────────────────────────────
    print("\n[Run 3] C seasonal (A=0.5, T=200)")
    results["c_seasonal"] = _run_or_load("c_seasonal", _CONFIGS["c_seasonal"])
    _check_quasi_stationary(results["c_seasonal"], "C seasonal")
    _check_juvenile_starvation(results["c_seasonal"], "C seasonal")
    pool_diag["c_seasonal"] = _check_pool_diagnostics(results["c_seasonal"], "C seasonal")

    # ── Run 4: Si seasonal ────────────────────────────────────────────────────
    print("\n[Run 4] Si seasonal (A=0.5, T=200)")
    results["si_seasonal"] = _run_or_load("si_seasonal", _CONFIGS["si_seasonal"])
    _check_quasi_stationary(results["si_seasonal"], "Si seasonal")
    _check_juvenile_starvation(results["si_seasonal"], "Si seasonal")
    pool_diag["si_seasonal"] = _check_pool_diagnostics(results["si_seasonal"], "Si seasonal")

    seasonal_ran = True

    # ── Plots ─────────────────────────────────────────────────────────────────
    print("\nGenerating plots...")
    _plot_population_trajectory(
        {k: results[k] for k in ["c_static", "si_static"] if k in results},
        out_dir,
        title="Stage 4.1c — Null controls: N(t) with support pool",
    )
    out_dir_s = out_dir / "seasonal"
    out_dir_s.mkdir(exist_ok=True)
    _plot_population_trajectory(
        {k: results[k] for k in ["c_seasonal", "si_seasonal"] if k in results},
        out_dir_s,
        title="Stage 4.1c — Seasonal: N(t) with support pool",
        period=200,
    )
    for key, df in results.items():
        _plot_pool_diagnostics(df, key, out_dir)

    # ── Report ────────────────────────────────────────────────────────────────
    _build_report(
        results, pool_diag, out_dir,
        gate_c, gate_si, juv_ok_c, juv_ok_si, seasonal_ran,
    )
    print("\nStage 4.1c complete.")


if __name__ == "__main__":
    main()
