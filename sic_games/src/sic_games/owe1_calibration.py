"""OWE-1: Absolute-Scale Calibration.

Tasks:
  1. Benchmark T1-T5 (100-120 grid, N=2000-4000).
  2. N_carry scaling rule + correctness gate (100×100, N=2000, 2000 steps).
  3. Home-range calibration: cell→km, kcal/unit.
  4. Timescale + compute budget table.

Generates: outputs/owe1_calibration/report_owe1.html

Usage:
    py -m sic_games.owe1_calibration
"""
from __future__ import annotations

import base64
import io
import math
import time
import warnings
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_REPO = Path(__file__).parent.parent.parent
_OUT  = _REPO / "outputs" / "owe1_calibration"
_TODAY = "2026-05-30"

# ── Config factory ──────────────────────────────────────────────────────────

def _bench_config(grid_w: int, grid_h: int, n_agents: int,
                  n_steps: int = 500, seed: int = 42,
                  n_carry_override: int | None = None) -> Any:
    """Full Stage 5.2-locked C config, scaling peaks/carry with grid."""
    from sic_games.config import (
        AgentsConfig, BirthCConfig, BirthSiConfig, C2DefectionConfig,
        CarbonConfig, CarryingCostConfig, Config, DeffuantConfig,
        DecisionConfig, DormancyConfig, InitializationConfig,
        JointTaskConfig, LifeHistoryConfig, PerturbationConfig,
        PopulationConfig, ReproductionConfig, RunConfig, SiBoundedConfig,
        SiCredConfig, SupportPoolConfig, VisualizationConfig, WorldConfig,
    )
    px0 = int(round(0.2 * grid_w)); py0 = int(round(0.8 * grid_h))
    px1 = int(round(0.8 * grid_w)); py1 = int(round(0.2 * grid_h))
    band_k = max(1, int(round(grid_w / 50 * 6)))
    n_carry = n_carry_override if n_carry_override is not None else (
        max(400, int(400 * (grid_w * grid_h) / (50 * 50)))
    )
    return Config(
        seed=seed,
        world=WorldConfig(
            grid_size=(grid_w, grid_h), toroidal=True,
            sugar_peaks=[(px0, py0), (px1, py1)],
            max_sugar_capacity=16, band_width_k=band_k, growth_rate_alpha=4,
        ),
        agents=AgentsConfig(
            initial_population=n_agents, vision_dist=(1, 6),
            metabolic_rate_dist=(1, 4), max_age_dist=(60, 100),
            initial_wealth_dist=(25, 75),   # Stage 5 scaling (wealth_init_scale_k=True → ×4)
            phi_mean=0.5, phi_std=0.2,
            psi_mean=0.5, psi_std=0.2, psi_beta_a=2.0, psi_beta_b=2.0,
            c1_mean=0.5, c1_std=0.2, c2_mean=0.5, c2_std=0.2,
        ),
        decision=DecisionConfig(strategy="carbon"),
        carbon=CarbonConfig(
            sigma_base=0.5, kappa=2.0, cred_scale=10.0, cred_decay=0.01,
            matthew_alpha=2.0, epsilon=0.01, cred_bonus_per_participant=1.0,
            velocity_tau=10, velocity_scale=1.0, f_C=0.25,
            status_amplification_beta=1.0,
        ),
        si_bounded=SiBoundedConfig(sigma_si=1.238, beta_metabolism=1.0),
        joint_task=JointTaskConfig(distance_d=1, capacity_threshold=4),
        c2_defection=C2DefectionConfig(enabled=True),
        deffuant=DeffuantConfig(enabled=False),  # off for benchmark
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            p_max=0.12, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
            r_wealth=0.5, rep_age_min=15, gamma=0.2, c_star_birth=10.0,
            carrying_cost=CarryingCostConfig(
                enabled=True, N_carry=n_carry, alpha_carry=1.0,
            ),
        ),
        birth_si=BirthSiConfig(p_fission_max=0.065, fission_wealth_mult=1.5,
                               rep_age_min=15),
        reproduction=ReproductionConfig(mode="biparental", parent_radius=3,
                                        inherit_sigma=0.10, lambda_inheritance=0.1),
        si_cred=SiCredConfig(enabled=False),
        dormancy=DormancyConfig(enabled=False),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(
            age_distribution="realistic", age_init_upper_frac=0.25,
            wealth_init_scale_k=True, cluster_init=True,
            cluster_peak_index=0, cluster_radius=10,
        ),
        life_history=LifeHistoryConfig(forage_age_min=15, forage_age_max_offset=10,
                                       eta_min=0.3, eta_old=0.4),
        support_pool=SupportPoolConfig(
            enabled=True, r_pool=5, tau_parent=0.0, tau_pool=0.05,
            k_reserve=5.0, k_draw=3.0, tau_cred=0.5, tau_cred_reward=0.1,
            rho_carryover=0.3, k_pool_cap=0.0,
        ),
        run=RunConfig(n_steps=n_steps, metrics_every=1, k_density=10, k_moran=10,
                      output_dir=""),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )


# ── Benchmark runner ────────────────────────────────────────────────────────

def _run_benchmark(grid_w: int, grid_h: int, n: int, steps: int = 500,
                   n_carry_override: int | None = None,
                   record_population: bool = False
                   ) -> dict:
    """Run benchmark, return timing + optional population trace."""
    from sic_games.run import SugarWorld
    cfg = _bench_config(grid_w, grid_h, n, steps, n_carry_override=n_carry_override)
    model = SugarWorld(cfg)
    n_carry_used = cfg.birth_c.carrying_cost.N_carry
    step_times = []
    pop_trace = []
    t0 = time.perf_counter()
    for _ in range(steps):
        ts = time.perf_counter()
        model.step()
        step_times.append(time.perf_counter() - ts)
        if record_population:
            pop_trace.append(len(list(model.agents)))
    t_total = time.perf_counter() - t0
    step_arr = np.array(step_times) * 1000  # ms
    return {
        "grid_w": grid_w, "grid_h": grid_h, "n_agents": n,
        "n_carry": n_carry_used, "n_steps": steps,
        "t_total_s": t_total,
        "ms_mean": float(step_arr.mean()),
        "ms_std": float(step_arr.std()),
        "ms_per_step": float(step_arr.mean()),
        "pop_trace": pop_trace,
        "final_pop": pop_trace[-1] if pop_trace else int(len(list(model.agents))),
    }


# ── Home-range estimator ─────────────────────────────────────────────────────

def _run_homerange(grid_w: int = 100, grid_h: int = 100, n: int = 2000,
                   steps: int = 2500) -> dict:
    """Run the C-static-medium config for home-range estimation.

    For each agent, track the set of distinct cells visited; report
    population median of unique-cell count over lifetime.
    """
    from sic_games.run import SugarWorld
    cfg = _bench_config(grid_w, grid_h, n, steps)
    model = SugarWorld(cfg)
    # Track per-agent visited cells
    agent_cells: dict[int, set] = {}  # uid -> set of (x,y)
    step_times = []
    pop_trace = []
    for step_i in range(steps):
        ts = time.perf_counter()
        model.step()
        step_times.append(time.perf_counter() - ts)
        for agent in model.agents:
            if agent.unique_id not in agent_cells:
                agent_cells[agent.unique_id] = set()
            agent_cells[agent.unique_id].add(agent.pos)
        pop_trace.append(len(list(model.agents)))

    # Unique cells visited per agent (proxy for home-range in cells)
    home_ranges_cells = [len(cells) for cells in agent_cells.values()]
    ms_arr = np.array(step_times) * 1000

    return {
        "n_agents_init": n, "steps": steps,
        "ms_mean": float(ms_arr.mean()),
        "median_cells": float(np.median(home_ranges_cells)),
        "q25_cells": float(np.percentile(home_ranges_cells, 25)),
        "q75_cells": float(np.percentile(home_ranges_cells, 75)),
        "mean_cells": float(np.mean(home_ranges_cells)),
        "n_carry": cfg.birth_c.carrying_cost.N_carry,
        "pop_trace": pop_trace,
    }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fig_b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return b64


def _html_table(rows: list[tuple], headers: list[str]) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join(
        f"<tr>{''.join(f'<td>{c}</td>' for c in row)}</tr>" for row in rows
    )
    return f"<table border='1' cellpadding='4' cellspacing='0'><tr>{th}</tr>{trs}</table>"


# ── Main orchestration ────────────────────────────────────────────────────────

def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)

    # ── Task 1: Benchmark T1–T5 ──────────────────────────────────────────────
    print("\n=== Task 1: Benchmarks T1-T5 (500 steps each) ===")
    ABORT_SECS = 20 * 60  # 20 min abort

    bench_configs = [
        ("T1", 100, 100, 2000),
        ("T2", 100, 100, 3000),
        ("T3", 100, 100, 4000),
        ("T4", 110, 110, 2000),
        ("T5", 120, 120, 2000),
    ]

    bench_results = {}
    skip_remaining = False
    for bid, gw, gh, n in bench_configs:
        if skip_remaining:
            print(f"  SKIPPED {bid} (prior run exceeded {ABORT_SECS//60} min)")
            continue
        n_carry = max(400, int(400 * gw * gh // 2500))
        print(f"  Running {bid}: {gw}x{gh}, N={n}, N_carry={n_carry} ...")
        t_start = time.perf_counter()
        try:
            res = _run_benchmark(gw, gh, n, 500)
            t_elapsed = time.perf_counter() - t_start
            bench_results[bid] = res
            print(f"    {res['ms_mean']:.1f} ms/step  ({t_elapsed:.0f}s total)")
            if t_elapsed > ABORT_SECS:
                print(f"    ABORT: exceeded {ABORT_SECS//60} min — skipping remaining")
                skip_remaining = True
        except Exception as e:
            print(f"    FAILED: {e}")
            bench_results[bid] = {"ms_mean": float("nan"), "error": str(e)}

    # Fit N-exponent (T1, T2, T3 — fixed 100x100 grid, varying N)
    n_vals = [2000, 3000, 4000]
    ms_vals = [bench_results.get(bid, {}).get("ms_mean", float("nan"))
               for bid in ["T1", "T2", "T3"]]
    n_exp = float("nan")
    if all(not math.isnan(v) for v in ms_vals):
        log_n = np.log(n_vals)
        log_ms = np.log(ms_vals)
        n_exp = float(np.polyfit(log_n, log_ms, 1)[0])
        print(f"  N-exponent (fixed 100x100): {n_exp:.3f}")

    # Fit grid-exponent (T1, T4, T5 — fixed N=2000, varying grid)
    grid_areas = [100*100, 110*110, 120*120]
    grid_ms = [bench_results.get(bid, {}).get("ms_mean", float("nan"))
               for bid in ["T1", "T4", "T5"]]
    grid_exp = float("nan")
    if all(not math.isnan(v) for v in grid_ms):
        log_a = np.log(grid_areas)
        log_gms = np.log(grid_ms)
        grid_exp = float(np.polyfit(log_a, log_gms, 1)[0])
        print(f"  Grid-exponent (fixed N=2000): {grid_exp:.3f}")

    # ── Task 2: N_carry scaling + correctness gate ────────────────────────────
    print("\n=== Task 2: N_carry scaling + correctness gate ===")
    # N_carry in the model: plain config constant, no automatic area scaling.
    # The benchmark harness applies: n_carry = max(400, 400 * grid_area / 2500)
    n_carry_50x50 = 400
    n_carry_100x100 = max(400, int(400 * 100*100 / (50*50)))
    print(f"  N_carry 50x50 (production): {n_carry_50x50}")
    print(f"  N_carry 100x100 (area-scaled): {n_carry_100x100}")
    print(f"  N=2000 vs N_carry={n_carry_100x100}: {'ABOVE' if 2000 > n_carry_100x100 else 'BELOW'} ceiling")

    print("  Running correctness gate: 100x100, N=2000, 2000 steps ...")
    gate_result = _run_benchmark(100, 100, 2000, steps=2000, record_population=True)
    pop_trace = gate_result["pop_trace"]
    settled_n = float(np.mean(pop_trace[1500:]))  # mean over last 500 steps
    ratio = settled_n / n_carry_100x100
    initial_decline = pop_trace[0] > pop_trace[99] if len(pop_trace) > 100 else False
    gate_pass = (
        len(pop_trace) > 0 and
        pop_trace[-1] > 10 and  # not extinct
        settled_n < n_carry_100x100 and  # below ceiling
        settled_n > 50  # non-trivial population
    )
    print(f"  Final N: {pop_trace[-1] if pop_trace else 'N/A'}")
    print(f"  Settled N (t>=1500): {settled_n:.0f}")
    print(f"  settled-N / N_carry: {ratio:.3f}")
    print(f"  Gate: {'PASS' if gate_pass else 'FAIL'}")

    if not gate_pass:
        print("  GATE FAIL: stopping before Task 3 — see corrected N in report")
        # Corrected init-N: aim for ~50% of N_carry
        corrected_n = int(n_carry_100x100 * 0.5)
        print(f"  Corrected initial N for headroom: ~{corrected_n}")

    # ── Task 3: Physical-unit calibration ─────────────────────────────────────
    print("\n=== Task 3: Home-range calibration ===")
    if gate_pass:
        print("  Running home-range reference run: C-static-medium, 2500 steps ...")
        hr = _run_homerange(100, 100, 2000, steps=2500)
        median_hr_cells = hr["median_cells"]
        q25_hr = hr["q25_cells"]
        q75_hr = hr["q75_cells"]
        print(f"  Median home-range: {median_hr_cells:.1f} cells  (IQR: [{q25_hr:.0f}, {q75_hr:.0f}])")
        # Solve for ell: median_hr_cells * ell^2 = 100 km^2
        # ell = sqrt(100 / median_hr_cells) km/cell
        target_km2 = 100.0  # forager home-range ~100 km^2
        ell_km = math.sqrt(target_km2 / median_hr_cells) if median_hr_cells > 0 else float("nan")
        ell_target = 10.0  # committed cell-size target (km/cell), OWE-1 §3.2
        # Consistency: how far the home-range-implied cell size is from the committed target.
        # CONSISTENT if within a factor of 2 of 10 km/cell (i.e. ell in [5, 20]).
        consistency_factor = ell_target / ell_km if ell_km > 0 else float("nan")
        ell_consistent = 5.0 <= ell_km <= 20.0
        # At the COMMITTED 10 km/cell, the model's emergent home-range would be:
        implied_hr_at_target = median_hr_cells * (ell_target ** 2)  # km^2
        hr_overshoot_factor = implied_hr_at_target / target_km2
        print(f"  Solved ell: {ell_km:.2f} km/cell  (committed target ~10 km)")
        print(f"  Consistency: ell solved is {consistency_factor:.1f}x smaller than 10km target -> {'CONSISTENT' if ell_consistent else 'GROSS INCONSISTENCY (finding)'}")
        print(f"  At committed 10km/cell: implied home-range = {implied_hr_at_target:.0f} km^2 ({hr_overshoot_factor:.0f}x the ~100km^2 forager band)")
        # Metabolic unit → kcal
        # 1 step = 1 month = 30 days
        # TEE = ~2000 kcal/day → per-step debit = 30 × 2000 = 60,000 kcal/agent/month
        # Per-step metabolism drain = agent.metabolism (mean ~2.5 metabolic units/step)
        mean_metabolism = 2.5  # mean of Uniform{1,2,3,4}
        tee_kcal_per_step = 30 * 2000  # 60,000 kcal/month for 2000 kcal/day forager
        kcal_per_unit = tee_kcal_per_step / mean_metabolism
        print(f"  kcal per metabolic unit: {kcal_per_unit:.0f} kcal")
        # Sanity: sugar unit kcal (1 sugar ~ 1/alpha metabolic unit per step)
        # Cell max_sugar = 16; growback = 4/step; metabolism mean ~2.5/step
        # Cell energy content implied: 16 units × kcal_per_unit / alpha(4) ~ estimate
        print(f"  kcal per sugar unit: ~{kcal_per_unit:.0f} kcal  (1 sugar unit = 1 metabolic-unit)")
        # Day-range sanity: world = 100×100 cells × ell_km^2 = total km^2
        world_km2 = (100 * ell_km) ** 2
        cell_area_km2 = ell_km ** 2
        print(f"  World area: {world_km2:.0f} km^2  Cell area: {cell_area_km2:.2f} km^2")
        print(f"  Day-range sanity: ell={ell_km:.2f} km/cell (~10 km target)")
        hr_median_km2 = median_hr_cells * cell_area_km2  # = 100 by construction
        hr_q25_km2 = q25_hr * cell_area_km2
        hr_q75_km2 = q75_hr * cell_area_km2
        # The home-range gate is met BY CONSTRUCTION (we solved ell to land at 100 km^2).
        # The REAL gate (blueprint 3.5) is cell-size consistency: does the solved ell
        # agree with the committed ~10 km/cell? It does NOT. Report as finding.
        hr_gate_pass = ell_consistent  # the honest gate is the consistency check
        print(f"  Home-range at solved ell: {hr_median_km2:.1f} km^2 (=100 by construction)")
        print(f"  HONEST GATE (cell-size consistency): {'PASS' if hr_gate_pass else 'FAIL - calibration tension, see report'}")
    else:
        # Provide placeholder values
        hr = {"median_cells": float("nan"), "ms_mean": 0.0, "pop_trace": []}
        ell_km = float("nan")
        ell_target = 10.0
        consistency_factor = float("nan")
        ell_consistent = False
        implied_hr_at_target = float("nan")
        hr_overshoot_factor = float("nan")
        kcal_per_unit = float("nan")
        hr_median_km2 = float("nan")
        hr_gate_pass = False

    # ── Task 4: Timescale + budget ────────────────────────────────────────────
    print("\n=== Task 4: Timescale + budget ===")
    t1_ms = bench_results.get("T1", {}).get("ms_mean", float("nan"))
    print(f"  T1 (100x100, N=2000) ms/step = {t1_ms:.1f}")
    # Timescale table
    run_lengths = [10_000, 12_000, 24_000]
    years_list = [r / 12 for r in run_lengths]
    secular_cycles = [y / 250 for y in years_list]
    wc_hours = [(r * t1_ms / 1000 / 3600) if not math.isnan(t1_ms) else float("nan")
                for r in run_lengths]
    # Campaign budget
    # ⟨ρ⟩: 3 levels × A: 3 × T: 4 × seeds: 5 × strategies: 2 = 360 runs
    # But T* sweep needs extra: ~20 additional
    total_runs = 3 * 3 * 4 * 5 * 2  # = 360
    wc_4workers_h = (total_runs * 12_000 * t1_ms / 1000 / 3600 / 4) if not math.isnan(t1_ms) else float("nan")
    print(f"  Full matrix ({total_runs} runs, 12k steps, 4 workers): {wc_4workers_h:.1f} h")

    # ── Build HTML report ─────────────────────────────────────────────────────
    print("\n=== Building HTML report ===")

    # §0 Model state
    import subprocess, sys
    test_result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
                                  capture_output=True, text=True, cwd=str(_REPO))
    test_line = [l for l in test_result.stdout.splitlines() if "passed" in l]
    test_count = test_line[0] if test_line else "unknown"

    # Benchmark plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    ax = axes[0]
    bids = [bid for bid in ["T1","T2","T3","T4","T5"] if bid in bench_results]
    ms_plot = [bench_results[bid].get("ms_mean", 0) for bid in bids]
    colors = ["steelblue","steelblue","steelblue","darkorange","darkorange"][:len(bids)]
    ax.bar(bids[:len(ms_plot)], ms_plot[:len(bids)], color=colors[:len(bids)])
    ax.set_ylabel("ms/step"); ax.set_title("Task 1: Benchmark T1-T5")
    for i, (b, v) in enumerate(zip(bids, ms_plot)):
        ax.text(i, v + 0.5, f"{v:.0f}", ha="center", fontsize=8)

    ax2 = axes[1]
    if gate_pass and hr.get("pop_trace"):
        t_ax = list(range(len(hr["pop_trace"])))
        ax2.plot(t_ax, hr["pop_trace"], color="steelblue", lw=1)
        ax2.axhline(n_carry_100x100, ls="--", color="red", alpha=0.6, label=f"N_carry={n_carry_100x100}")
        ax2.set_xlabel("Step"); ax2.set_ylabel("N"); ax2.set_title("Task 2 gate: N(t) 100×100 N=2000")
        ax2.legend(fontsize=8)
    elif gate_result.get("pop_trace"):
        t_ax = list(range(len(gate_result["pop_trace"])))
        ax2.plot(t_ax, gate_result["pop_trace"], color="steelblue", lw=1)
        ax2.axhline(n_carry_100x100, ls="--", color="red", alpha=0.6, label=f"N_carry={n_carry_100x100}")
        ax2.set_xlabel("Step"); ax2.set_ylabel("N"); ax2.set_title("Task 2 gate: N(t) 100×100 N=2000")
        ax2.legend(fontsize=8)
    fig.tight_layout()
    bench_plot = _fig_b64(fig)

    # Timescale table HTML
    ts_rows = [
        (f"{rl:,}", f"{y:.0f}", f"~{sc:.1f}", f"{wh:.1f} h")
        for rl, y, sc, wh in zip(run_lengths, years_list, secular_cycles, wc_hours)
    ]

    bench_table_rows = []
    for bid, gw, gh, n in bench_configs:
        res = bench_results.get(bid, {})
        ms = res.get("ms_mean", float("nan"))
        n_c = max(400, int(400 * gw * gh // 2500))
        bench_table_rows.append((
            bid, f"{gw}x{gh}", str(n), str(n_c),
            f"{ms:.1f}" if not math.isnan(ms) else "SKIPPED",
        ))

    gate_color = "green" if gate_pass else "red"
    hr_gate_color = "green" if hr_gate_pass else "orange"
    n_exp_str = f"{n_exp:.3f}" if not math.isnan(n_exp) else "insufficient data"
    g_exp_str = f"{grid_exp:.3f}" if not math.isnan(grid_exp) else "insufficient data"
    claim_verdict = ""
    if not math.isnan(n_exp) and not math.isnan(grid_exp):
        claim_verdict = (
            f"N-exponent={n_exp:.3f}, grid-exponent={grid_exp:.3f}. "
            f"{'Claim SUPPORTED: N-scaling shallower than grid-scaling.' if n_exp < grid_exp else 'Claim NOT supported: N-scaling not clearly shallower.'}"
        )

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>OWE-1 Absolute-Scale Calibration ({_TODAY})</title>
  <style>
    body {{font-family: Arial, sans-serif; max-width: 1100px; margin: auto; padding: 20px;}}
    h1 {{color: #2c3e50;}}
    h2 {{color: #2c6fa8; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 28px;}}
    h3 {{color: #444;}}
    table {{border-collapse: collapse; margin: 8px 0; font-size: 0.92em;}}
    th {{background: #dce8f5; padding: 5px 10px;}}
    td {{padding: 4px 10px;}}
    code {{background: #f4f4f4; padding: 1px 4px; border-radius: 3px;}}
    .pass {{color: green; font-weight: bold;}}
    .fail {{color: red; font-weight: bold;}}
  </style>
</head>
<body>
<h1>OWE-1 — Absolute-Scale Calibration</h1>
<p><b>Date:</b> {_TODAY} &nbsp;|&nbsp;
   <b>Model state:</b> Stage 5.2 (post-cultural-dynamics) &nbsp;|&nbsp;
   <b>Tests:</b> {test_count}</p>
<p><b>Grid target:</b> 100×100 &nbsp;|&nbsp;
   <b>N target:</b> 2000 &nbsp;|&nbsp;
   <b>Step:</b> 1 month (locked Route A)</p>

<h2>§0 Model State</h2>
<p>Committed version: Stage 5.2 complete (c2 defection, Deffuant, sigma_inherit=0.10).
Test suite: {test_count}. No git repo — version by directory backup. Current backup:
<code>v5.1.2_pre_cultural</code>.</p>

<h2>§1 Target-Geometry Benchmark</h2>
<img src="data:image/png;base64,{bench_plot}" style="max-width:100%">
{_html_table(bench_table_rows, ["ID","Grid","N","N_carry (area-scaled)","ms/step"])}
<p><b>N-exponent</b> (T1/T2/T3, fixed 100×100): {n_exp_str}<br>
   <b>Grid-exponent</b> (T1/T4/T5, fixed N=2000): {g_exp_str}<br>
   {claim_verdict}</p>

<h2>§2 Carrying-Capacity Gate</h2>
<p><b>N_carry scaling rule in code:</b> HARD CONSTANT (400) in the model config.
The benchmark harness applies area-scaling: <code>N_carry = max(400, 400 × grid_area / 2500)</code>.
This lives in <code>benchmark.py</code> and <code>owe1_calibration.py</code>,
NOT in the model mechanics. Production Stage 5+ configs use N_carry=400 for the 50×50 world.</p>
<p><b>100×100 N_carry (area-scaled):</b> {n_carry_100x100}<br>
   <b>N=2000 vs ceiling:</b> {"ABOVE — initial transient expected; monitor for stable settlement" if 2000 > n_carry_100x100 else "BELOW — no initial crash expected"}</p>
{_html_table([
    ("N_carry (50x50 production)", str(n_carry_50x50)),
    ("N_carry (100x100 area-scaled)", str(n_carry_100x100)),
    ("Initial N", "2000"),
    ("Final N (t=2000)", str(gate_result.get("pop_trace", [0])[-1]) if gate_result.get("pop_trace") else "N/A"),
    ("Settled N (t>=1500)", f"{settled_n:.0f}"),
    ("settled-N / N_carry", f"{ratio:.3f}"),
    ("Gate", "PASS" if gate_pass else "FAIL — see corrected N"),
], ["Metric","Value"])}
<p><b>Gate: <span class="{'pass' if gate_pass else 'fail'}">{'PASS' if gate_pass else 'FAIL'}</span>.</b>
{"Population settled below carrying capacity with headroom for boom phase." if gate_pass
 else f"Population did not settle adequately. Corrected initial N = ~{int(n_carry_100x100*0.5)} (50% of N_carry)."}</p>

<h2>§3 Absolute-Scale Calibration</h2>
{"" if gate_pass else "<p><b>CARRYING-CAPACITY GATE FAILED — calibration results are provisional.</b></p>"}
<p><b>Reference config:</b> C arm, static (unshocked) world, medium-⟨ρ⟩ (settled density
~{settled_n/10000*100:.1f}% at N≈{settled_n:.0f} on 100×100), seed=42, 2500 steps.
Per blueprint §3.4, the gate is "C-static-medium hits the band," and C-vs-Si / across-⟨ρ⟩
divergences are recorded as emergent outputs, never tuned away.</p>
{_html_table([
    ("Median home-range (cells)", f"{hr.get('median_cells', float('nan')):.1f}" if not math.isnan(hr.get('median_cells', float('nan'))) else "N/A"),
    ("IQR home-range (cells)", f"[{hr.get('q25_cells', float('nan')):.0f}, {hr.get('q75_cells', float('nan')):.0f}]" if not math.isnan(hr.get('median_cells', float('nan'))) else "N/A"),
    ("Solved cell length ell (km), to hit 100 km^2", f"{ell_km:.2f}" if not math.isnan(ell_km) else "N/A"),
    ("Committed cell-size target (OWE-1 §3.2)", "~10 km"),
    ("Consistency factor (target / solved)", f"{consistency_factor:.1f}x" if not math.isnan(consistency_factor) else "N/A"),
    ("Implied home-range AT committed 10 km/cell", f"{implied_hr_at_target:.0f} km^2" if not math.isnan(implied_hr_at_target) else "N/A"),
    ("Overshoot vs ~100 km^2 forager band", f"{hr_overshoot_factor:.0f}x" if not math.isnan(hr_overshoot_factor) else "N/A"),
    ("Mean metabolism drain (units/step)", "2.5 (mean of Uniform{{1,2,3,4}})"),
    ("TEE anchor (kcal/agent/month)", "60,000 (30 days x 2000 kcal/day)"),
    ("kcal per metabolic unit", f"{kcal_per_unit:.0f}" if not math.isnan(kcal_per_unit) else "N/A"),
], ["Metric","Value"])}
<p><b>FINDING — cell-size consistency: <span class="{'pass' if ell_consistent else 'fail'}">{'CONSISTENT' if ell_consistent else 'GROSS INCONSISTENCY'}</span>.</b>
The home-range "gate" of landing C-static-medium at ~100 km^2 is met only by setting
ell = {ell_km:.2f} km/cell — roughly {consistency_factor:.0f}x smaller than the committed
~10 km/cell geometry. Equivalently: <b>at the committed 10 km/cell, the model's emergent
median home-range is ~{implied_hr_at_target:.0f} km^2, about {hr_overshoot_factor:.0f}x the
~100 km^2 forager band.</b> Per blueprint §3.5 this gross inconsistency is reported, NOT forced.</p>
<p><b>Interpretation (for supervisor):</b> the model's C agents occupy ~{hr.get('median_cells', float('nan')):.0f}
distinct cells over a lifetime — far more mobile (in cell units) than a forager is in
home-range units. Two mutually exclusive readings, neither resolvable here (locked params
+ committed geometry are both out of scope to retune):
(a) accept ~1.3 km cells (world only ~{(100*ell_km):.0f}x{(100*ell_km):.0f} km ≈ {(100*ell_km)**2:.0f} km^2),
which is too small for the 20–60 ethnographic bands at forager density the §3.2 geometry intends; or
(b) keep ~10 km cells and accept that emergent home-range is ~{hr_overshoot_factor:.0f}x forager scale,
i.e. the model's mobility does not map to forager territoriality at this resolution.
This is a genuine model-vs-ethnography scale tension surfaced by the calibration, registered
as a finding. Note: home-range is legitimately <i>joint</i> (foraging + ψ social pull, C2
mechanism) — no foraging-only isolation attempted.</p>

<h2>§4 Timescale + Budget</h2>
<h3>Timescale table (1 step = 1 month, T1 ms/step = {t1_ms:.1f} ms)</h3>
{_html_table(ts_rows, ["Run length (steps)","Simulated (yr)","Secular cycles (~250yr)","Wall-clock (h, 1 worker)"])}
<h3>Phenomenon adequacy (monthly resolution)</h3>
{_html_table([
    ("Secular cycles (~250 yr = ~3000 steps)", "PASS — 12k steps = 4 full cycles"),
    ("Asabiyyah rise/decay (decades = ~120–360 steps)", "PASS — well above monthly resolution"),
    ("Demographic generations (~25–30 yr = ~300–360 steps)", "PASS"),
    ("Seasonal shocks (T=200 steps = ~16.7 yr)", "PASS — T=200 >> 12 steps (Nyquist)"),
    ("Seasonal shocks (T=50 steps = ~4.2 yr)", "PASS — T=50 >> 12 steps"),
    ("Sub-monthly shocks", "OUT OF SCOPE by design — absorbed by buffer mechanism"),
], ["Phenomenon","Adequacy"])}
<h3>Full-matrix campaign budget</h3>
<p>Sweep matrix: ⟨ρ⟩(3) × A(3) × T(4) × seeds(5) × {'{'}C,Si{'}'} = {total_runs} runs.
Standard run-length: 12,000 steps.
Wall-clock at 4 workers: <b>{wc_4workers_h:.1f} h</b>.
</p>
<h3>H-EMERGE-1 consequence (flag only)</h3>
<p>At 12,000 steps (1000 yr, ~4 secular cycles), the standard run length
<i>is</i> adequate for secular-cycle emergence detection (≥3 complete cycles required
for cycle-length estimation). At 10,000 steps (~3.3 cycles), the run length is marginal.
<b>FLAG:</b> if H-EMERGE-1 requires detecting the onset of a first cycle as well as
subsequent cycles, the transient (~500 steps) must be excluded, leaving ~9,500 productive
steps (~3.2 cycles). Supervisor to decide whether to use 12,000 or 24,000 steps as the
standard; this blueprint does not rescope H-EMERGE-1.</p>

<h2>§5 Doc fold-in</h2>
<p>The following were executed in this pass:</p>
<ul>
<li><b>ROADMAP.md:</b> Added "Sweep-Matrix axes" section (⟨ρ⟩ axis registered).
    Added "Owed items" section with OWE-1 through OWE-13.
    Added H-ORTHOGONALITY and H-instinct-debt to Pre-registered Hypotheses.
    No contradictions found with live values.
    Note: OWE-2 through OWE-10 derived from project context (chat_handoff.md,
    CLAUDE.md, MODEL_SPEC.md); no separate "2026-05-30 Standing Handoff" file
    found — items added from best available sources.</li>
<li><b>MODEL_SPEC.md §9:</b> Already present from today's full extraction (v0.2).
    Added §9.3 physical-unit calibration section with OWE-1 standing constraint,
    target geometry, calibration anchors, home-range gate description, and OWE-13
    planned diagnostic. Davies/Loihi citation updated to [INLINE] with OWE-4 flag.
    No contradictions.</li>
<li><b>HYPOTHESES.md:</b> Created new file. Registered H-ORTHOGONALITY (OPEN),
    H-instinct-debt (OPEN), H_cc (partially supported). H1(ii) documented as
    INVERTED/confirmed finding.</li>
<li><b>No CONTRADICTORY entries found.</b> No auto-resolutions were made.</li>
</ul>
</body>
</html>"""

    report_path = _OUT / "report_owe1.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"\nReport written: {report_path}")


if __name__ == "__main__":
    main()
