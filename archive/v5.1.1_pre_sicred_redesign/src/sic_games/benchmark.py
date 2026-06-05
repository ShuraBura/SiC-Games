"""Runtime Benchmark — SiC Games Stage 5 model.

Measures wall-clock timing, component breakdown, memory, and scaling across
seven grid/N configurations (B0–B6). Produces outputs/benchmark/report_benchmark.html.

Usage:
    py -m sic_games.benchmark

Directive: G:/My Drive/docs/SiC Games/SiC_Games_Benchmark_Runtime.md
"""
from __future__ import annotations

import base64
import ctypes
import io
import math
import os
import platform
import sys
import time
import tracemalloc
import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
_REPO = Path(__file__).parent.parent.parent   # sic_games/
_OUT  = _REPO / "outputs" / "benchmark"
_TODAY = "2026-05-27"

# ── Benchmark configurations table ────────────────────────────────────────────
# (id, grid_w, grid_h, n_agents, density_pct, n_steps)
BENCH_CONFIGS = [
    ("B0", 50,  50,   250, 10.0,  500),
    ("B1", 100, 100,  500,  5.0,  500),
    ("B2", 100, 100, 1000, 10.0,  500),
    ("B3", 150, 150, 1000,  4.4,  500),
    ("B4", 150, 150, 2000,  8.9,  500),
    ("B5", 200, 200, 1500,  3.75, 500),
    ("B6", 200, 200, 3000,  7.5,  500),
]

# Component breakdown only for these config IDs
COMPONENT_CONFIGS = {"B0", "B2"}
# Per-step time list for these config IDs
PER_STEP_LIST_CONFIGS = {"B0", "B2", "B4"}

# Stopping rule thresholds (seconds)
STOP_WARN_S  = 20 * 60   # 20 min → skip remaining configs
SKIP_B4_S    = 10 * 60   # if B3 > 10 min → skip B4, run B5 only
SKIP_B6_S    = 20 * 60   # if B5 > 20 min → skip B6 and flag

FEASIBILITY_THRESHOLD_MS = 600   # ms/step → 500 steps = 5 min (green)
RED_THRESHOLD_MS          = 2400  # ms/step → 500 steps = 20 min (red)


# ── Config factory ─────────────────────────────────────────────────────────────

def _bench_c_config(grid_w: int, grid_h: int, n_agents: int,
                    n_steps: int = 500) -> Any:
    """Full Stage 5-locked C config for benchmarking.

    Differences from Stage 5 production config:
    - grid_size, sugar_peaks, band_width_k scale with grid
    - initial_population = n_agents
    - N_carry scales proportionally to grid area
    - perturbation = null (static world)
    - output_dir = '' (no file I/O in benchmark loop)
    - metrics_every = 1 (we time compute_metrics)
    """
    from sic_games.config import (
        AgentsConfig, BirthCConfig, BirthSiConfig, CarbonConfig,
        CarryingCostConfig, Config, DecisionConfig, DormancyConfig,
        InitializationConfig, JointTaskConfig, LifeHistoryConfig,
        PerturbationConfig, PopulationConfig, ReproductionConfig,
        RunConfig, SiBoundedConfig, SiCredConfig, SupportPoolConfig,
        VisualizationConfig, WorldConfig,
    )

    # Scale peaks, band_width_k proportionally to grid
    px0 = int(round(0.2 * grid_w))
    py0 = int(round(0.8 * grid_h))
    px1 = int(round(0.8 * grid_w))
    py1 = int(round(0.2 * grid_h))
    band_k = max(1, int(round(grid_w / 50 * 6)))  # e.g. 6, 12, 18, 24

    # Scale N_carry proportionally to grid area so carry_discount behaves
    # the same way across grid sizes (prevents instant collapse at large N)
    n_carry = max(400, int(400 * (grid_w * grid_h) / (50 * 50)))

    return Config(
        seed=42,
        world=WorldConfig(
            grid_size=(grid_w, grid_h),
            toroidal=True,
            sugar_peaks=[(px0, py0), (px1, py1)],
            max_sugar_capacity=16,   # k_grid=4: max_sugar = 4*4 = 16
            band_width_k=band_k,
            growth_rate_alpha=4,     # k_grid=4
        ),
        agents=AgentsConfig(
            initial_population=n_agents,
            vision_dist=(1, 6),
            metabolic_rate_dist=(1, 4),
            max_age_dist=(60, 100),
            initial_wealth_dist=(5, 25),
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
        population=PopulationConfig(mode="dynamic"),
        birth_c=BirthCConfig(
            p_max=0.12, tau_sub=5.0, r_stress=0.75, k_stress=10.0,
            r_wealth=0.5, rep_age_min=15, gamma=0.2, c_star_birth=10.0,
            carrying_cost=CarryingCostConfig(
                enabled=True, N_carry=n_carry, alpha_carry=1.0,
            ),
        ),
        birth_si=BirthSiConfig(
            p_fission_max=0.065, fission_wealth_mult=1.5, rep_age_min=15,
        ),
        reproduction=ReproductionConfig(
            mode="biparental", parent_radius=3,
            inherit_sigma=0.05, lambda_inheritance=0.1,
        ),
        si_cred=SiCredConfig(enabled=False),
        dormancy=DormancyConfig(enabled=False),
        perturbation=PerturbationConfig(type="null"),
        initialization=InitializationConfig(
            age_distribution="realistic", age_init_upper_frac=0.25,
            wealth_init_scale_k=True, cluster_init=True,
            cluster_peak_index=0,
            cluster_radius=max(5, int(10 * grid_w / 50)),
        ),
        life_history=LifeHistoryConfig(
            forage_age_min=15, forage_age_max_offset=10,
            eta_min=0.3, eta_old=0.4,
        ),
        support_pool=SupportPoolConfig(
            enabled=True, r_pool=5, tau_parent=0.0, tau_pool=0.05,
            k_reserve=5.0, k_draw=3.0, tau_cred=0.5, tau_cred_reward=0.1,
            rho_carryover=0.3, k_pool_cap=0.0,
        ),
        run=RunConfig(
            n_steps=n_steps, metrics_every=1, output_dir="",
        ),
        visualization=VisualizationConfig(animate=False, save_static_plots=False),
    )


# ── Result container ───────────────────────────────────────────────────────────

@dataclass
class BenchResult:
    config_id: str
    grid_w: int
    grid_h: int
    n_agents_initial: int
    density_pct: float
    n_steps_ran: int
    n_steps_target: int
    aborted: bool           # True if stopped by 20-min rule
    skip_reason: str        # e.g. "B3 exceeded 10 min" or ""

    t_total: float          # seconds
    t_warmup: float         # first 50 steps
    t_per_step_mean: float  # ms
    t_per_step_std: float   # ms
    per_step_ms: list[float] = field(default_factory=list)   # empty unless in PER_STEP_LIST

    # Component breakdown (ms/step) — None if not measured
    t_grid_ms: float | None = None
    t_jt_ms: float | None = None    # JointTask detection — O(cells × N)
    t_agent_ms: float | None = None  # residual: harvest + metabolize + cred + misc
    t_pool_ms: float | None = None
    t_repro_ms: float | None = None
    t_metrics_ms: float | None = None

    # Memory
    mem_t0_mb: float = 0.0
    mem_t250_mb: float = 0.0
    mem_t500_mb: float = 0.0
    mem_delta_mb: float = 0.0

    agent_steps_per_second: float = 0.0


# ── Component timing instrumentation ──────────────────────────────────────────

class _ComponentTimer:
    """Accumulates per-call timings for a named component.

    Usage: wrap a callable:
        timer = _ComponentTimer()
        orig = obj.method
        obj.method = timer.wrap(orig)
    Then call timer.step_totals to get the list of per-step accumulated sums.
    """
    def __init__(self):
        self._step_acc: float = 0.0
        self.step_totals: list[float] = []   # seconds per step (appended by finalize_step)

    def wrap(self, fn):
        _acc = self
        def _timed(*args, **kwargs):
            t0 = perf_counter()
            result = fn(*args, **kwargs)
            _acc._step_acc += perf_counter() - t0
            return result
        return _timed

    def finalize_step(self):
        """Called once per step to snapshot the accumulated time."""
        self.step_totals.append(self._step_acc)
        self._step_acc = 0.0

    @property
    def mean_ms(self) -> float:
        if not self.step_totals:
            return 0.0
        return float(np.mean(self.step_totals)) * 1000.0


def _attach_component_timers(world) -> dict[str, _ComponentTimer]:
    """Monkey-patch world instance methods to collect component timings.

    Returns dict of timers keyed by component name.
    Patches:
      grid    → sugar_field.growback, shed_excess_sugar, perturbation.apply
      pool    → _support_pool.step
      repro   → _coordinator.attempt_birth (per-agent call; accumulated per step)
    metrics timing is handled via sic_games.run module patching (see below).
    """
    timers: dict[str, _ComponentTimer] = {
        "grid":    _ComponentTimer(),
        "jt":      _ComponentTimer(),   # JointTask detection — O(cells × N)
        "pool":    _ComponentTimer(),
        "repro":   _ComponentTimer(),
        "metrics": _ComponentTimer(),
    }

    # Grid update: perturbation.apply + shed_excess_sugar + growback
    t_grid = timers["grid"]
    sf = world.sugar_field
    sf.growback = t_grid.wrap(sf.growback)
    sf.shed_excess_sugar = t_grid.wrap(sf.shed_excess_sugar)
    world._perturbation.apply = t_grid.wrap(world._perturbation.apply)

    # Joint task detection (O(candidate_cells × N) — the key scaling bottleneck)
    if world._jt_manager is not None:
        t_jt = timers["jt"]
        world._jt_manager.process_step = t_jt.wrap(world._jt_manager.process_step)

    # Pool step
    if world._support_pool is not None:
        t_pool = timers["pool"]
        world._support_pool.step = t_pool.wrap(world._support_pool.step)

    # Repro: wrap coordinator.attempt_birth
    if world._coordinator is not None:
        t_repro = timers["repro"]
        world._coordinator.attempt_birth = t_repro.wrap(
            world._coordinator.attempt_birth
        )

    # Metrics: patch sic_games.run.compute_metrics at module level
    import sic_games.run as _run_mod
    _orig_cm = _run_mod.compute_metrics
    t_met = timers["metrics"]
    def _timed_compute_metrics(*args, **kwargs):
        t0 = perf_counter()
        result = _orig_cm(*args, **kwargs)
        t_met._step_acc += perf_counter() - t0
        return result
    _run_mod.compute_metrics = _timed_compute_metrics

    # Store original so we can restore after the run
    timers["_orig_compute_metrics"] = _orig_cm   # type: ignore
    timers["_run_mod"] = _run_mod                 # type: ignore

    return timers


def _detach_component_timers(timers: dict) -> None:
    """Restore the patched sic_games.run.compute_metrics."""
    _run_mod = timers.get("_run_mod")
    orig = timers.get("_orig_compute_metrics")
    if _run_mod is not None and orig is not None:
        _run_mod.compute_metrics = orig


# ── Single benchmark run ───────────────────────────────────────────────────────

def run_one(
    config_id: str,
    grid_w: int, grid_h: int,
    n_agents: int,
    density_pct: float,
    n_steps: int,
    with_components: bool,
    with_per_step_list: bool,
    stop_at_seconds: float = STOP_WARN_S,
    print_progress: bool = True,
) -> BenchResult:
    """Run a single benchmark configuration and return a BenchResult."""
    from sic_games.run import SugarWorld

    if print_progress:
        print(f"  [{config_id}] grid={grid_w}x{grid_h} N={n_agents} ...", end=" ", flush=True)

    cfg = _bench_c_config(grid_w, grid_h, n_agents, n_steps)

    # Build world
    world = SugarWorld(cfg, env_seed=42, agent_seed=42)

    timers: dict[str, _ComponentTimer] | None = None
    if with_components:
        timers = _attach_component_timers(world)

    # tracemalloc — use current (not peak) for each snapshot to detect steady-state growth
    tracemalloc.start()
    current0, _ = tracemalloc.get_traced_memory()
    mem_t0_mb = current0 / 1e6

    step_times: list[float] = []   # seconds per step
    t_run_start = perf_counter()
    aborted = False
    n_ran = 0
    mem_t250_mb = 0.0
    mem_t500_mb = 0.0

    WARMUP = 50
    # Half-step markers (0-indexed: step 249 = after 250th world.step call)
    _MEM_250 = 249
    _MEM_500 = min(n_steps - 1, 499)

    for s in range(n_steps):
        # Step
        t0_step = perf_counter()
        world.step()
        dt_step = perf_counter() - t0_step

        step_times.append(dt_step)
        n_ran += 1

        # Finalize component timers each step
        if timers is not None:
            for name in ("grid", "jt", "pool", "repro", "metrics"):
                timers[name].finalize_step()

        # Memory snapshots (after the step completes)
        if s == _MEM_250:
            cur, _ = tracemalloc.get_traced_memory()
            mem_t250_mb = cur / 1e6
        if s == _MEM_500:
            cur, _ = tracemalloc.get_traced_memory()
            mem_t500_mb = cur / 1e6

        # Stopping rule: check every 50 steps
        if (s + 1) % 50 == 0:
            elapsed = perf_counter() - t_run_start
            if elapsed > stop_at_seconds:
                aborted = True
                if print_progress:
                    print(f"\n    STOPPED at step {s+1} ({elapsed/60:.1f} min > {stop_at_seconds/60:.0f} min limit)")
                break

    t_total = perf_counter() - t_run_start

    # Fill in memory snapshots if not enough steps ran
    if mem_t500_mb == 0.0:
        cur, _ = tracemalloc.get_traced_memory()
        mem_t500_mb = cur / 1e6
    if mem_t250_mb == 0.0:
        mem_t250_mb = mem_t500_mb

    tracemalloc.stop()

    # Component breakdown
    t_grid_ms: float | None = None
    t_jt_ms: float | None = None
    t_pool_ms: float | None = None
    t_repro_ms: float | None = None
    t_metrics_ms: float | None = None
    t_agent_ms: float | None = None

    if timers is not None:
        _detach_component_timers(timers)
        t_grid_ms    = timers["grid"].mean_ms
        t_jt_ms      = timers["jt"].mean_ms
        t_pool_ms    = timers["pool"].mean_ms
        t_repro_ms   = timers["repro"].mean_ms
        t_metrics_ms = timers["metrics"].mean_ms
        # t_agent = residual: harvest + metabolize + cred flush + misc
        t_step_mean_ms = float(np.mean(step_times)) * 1000.0
        t_agent_ms = max(0.0, t_step_mean_ms - t_grid_ms - t_jt_ms
                         - t_pool_ms - t_repro_ms - t_metrics_ms)

    # Step time stats
    arr = np.array(step_times) * 1000.0  # ms
    t_per_step_mean = float(np.mean(arr))
    t_per_step_std  = float(np.std(arr))
    t_warmup        = float(np.sum(step_times[:min(WARMUP, len(step_times))]))

    per_step_ms = list(arr) if with_per_step_list else []

    # Throughput
    agent_steps_per_sec = (n_agents * n_ran) / t_total if t_total > 0 else 0.0

    if print_progress:
        print(f"done in {t_total:.1f}s  ({t_per_step_mean:.1f} ms/step)")

    return BenchResult(
        config_id=config_id,
        grid_w=grid_w, grid_h=grid_h,
        n_agents_initial=n_agents,
        density_pct=density_pct,
        n_steps_ran=n_ran,
        n_steps_target=n_steps,
        aborted=aborted,
        skip_reason="",
        t_total=t_total,
        t_warmup=t_warmup,
        t_per_step_mean=t_per_step_mean,
        t_per_step_std=t_per_step_std,
        per_step_ms=per_step_ms,
        t_grid_ms=t_grid_ms,
        t_jt_ms=t_jt_ms,
        t_agent_ms=t_agent_ms,
        t_pool_ms=t_pool_ms,
        t_repro_ms=t_repro_ms,
        t_metrics_ms=t_metrics_ms,
        mem_t0_mb=mem_t0_mb,
        mem_t250_mb=mem_t250_mb,
        mem_t500_mb=mem_t500_mb,
        mem_delta_mb=mem_t500_mb - mem_t0_mb,
        agent_steps_per_second=agent_steps_per_sec,
    )


# ── Smoke test ─────────────────────────────────────────────────────────────────

def smoke_test() -> float:
    """10-step smoke test to confirm timing is active. Returns ms/step."""
    from sic_games.run import SugarWorld
    cfg = _bench_c_config(50, 50, 250, n_steps=10)
    world = SugarWorld(cfg, env_seed=42, agent_seed=42)
    times = []
    for _ in range(10):
        t0 = perf_counter()
        world.step()
        times.append(perf_counter() - t0)
    ms = float(np.mean(times)) * 1000.0
    print(f"  Smoke test: 10 steps, mean {ms:.2f} ms/step — timing active")
    return ms


# ── Scaling analysis ───────────────────────────────────────────────────────────

def _norm_time(r: BenchResult) -> float:
    """Normalised total time: extrapolate to 500 steps using mean step time.

    This lets aborted runs contribute to scaling fits on equal footing.
    """
    return r.t_per_step_mean / 1000.0 * 500.0  # seconds for 500 steps


def _grid_scaling_exponent(results: list[BenchResult]) -> tuple[float, float, list]:
    """Fit log(t_norm) ~ exp * log(grid_side) + const.

    Use B0 (grid=50), B1 (grid=100), B3 (grid=150) — N roughly proportional.
    Include aborted configs via normalised time.
    """
    pts = [(r.grid_w, _norm_time(r)) for r in results
           if r.config_id in ("B0", "B1", "B3")]
    if len(pts) < 2:
        return float("nan"), float("nan"), pts
    xs = np.log([p[0] for p in pts])
    ys = np.log([p[1] for p in pts])
    A = np.vstack([xs, np.ones(len(xs))]).T
    try:
        slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    except Exception:
        slope, intercept = float("nan"), float("nan")
    return float(slope), float(intercept), pts


def _n_scaling_exponent(results: list[BenchResult]) -> tuple[float, float, list]:
    """Fit log(t_norm) ~ exp * log(N) + const.

    Use same-grid pairs: (B1 vs B2), (B3 vs B4), (B5 vs B6).
    Include aborted configs via normalised time.
    """
    pairs = [("B1", "B2"), ("B3", "B4"), ("B5", "B6")]
    by_id = {r.config_id: r for r in results}

    fit_pts = []
    for a, b in pairs:
        if a in by_id and b in by_id:
            ra, rb = by_id[a], by_id[b]
            fit_pts.append((ra.n_agents_initial, _norm_time(ra)))
            fit_pts.append((rb.n_agents_initial, _norm_time(rb)))

    if len(fit_pts) < 2:
        return float("nan"), float("nan"), fit_pts

    xs = np.log([p[0] for p in fit_pts])
    ys = np.log([p[1] for p in fit_pts])
    A = np.vstack([xs, np.ones(len(xs))]).T
    try:
        slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    except Exception:
        slope, intercept = float("nan"), float("nan")
    return float(slope), float(intercept), fit_pts


# ── Plot helpers ───────────────────────────────────────────────────────────────

def _fig_to_b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def _plot_per_step(result: BenchResult) -> str | None:
    if not result.per_step_ms:
        return None
    fig, ax = plt.subplots(figsize=(8, 3))
    xs = np.arange(1, len(result.per_step_ms) + 1)
    ax.plot(xs, result.per_step_ms, alpha=0.6, linewidth=0.8, color="steelblue")
    mean_v = result.t_per_step_mean
    std_v  = result.t_per_step_std
    ax.axhline(mean_v, color="red", linewidth=1.5, label=f"mean {mean_v:.1f} ms")
    ax.axhspan(mean_v - std_v, mean_v + std_v, alpha=0.15, color="red",
               label=f"±1σ ({std_v:.1f} ms)")
    ax.set_xlabel("Step")
    ax.set_ylabel("ms/step")
    ax.set_title(f"{result.config_id}: per-step timing ({result.grid_w}×{result.grid_h}, N={result.n_agents_initial})")
    ax.legend(fontsize=9)
    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


def _plot_component_bars(results: list[BenchResult]) -> str | None:
    comp_results = [r for r in results if r.config_id in COMPONENT_CONFIGS
                    and r.t_grid_ms is not None]
    if not comp_results:
        return None

    fig, axes = plt.subplots(1, len(comp_results), figsize=(5 * len(comp_results), 4))
    if len(comp_results) == 1:
        axes = [axes]

    colors = {
        "Grid":      "#4e79a7",
        "JointTask": "#edc948",   # yellow — the O(cells×N) bottleneck
        "Agent":     "#f28e2b",
        "Pool":      "#59a14f",
        "Repro":     "#e15759",
        "Metrics":   "#76b7b2",
    }

    for ax, r in zip(axes, comp_results):
        total_ms = r.t_per_step_mean
        comps = {
            "Grid":      r.t_grid_ms or 0.0,
            "JointTask": r.t_jt_ms or 0.0,
            "Agent":     r.t_agent_ms or 0.0,
            "Pool":      r.t_pool_ms or 0.0,
            "Repro":     r.t_repro_ms or 0.0,
            "Metrics":   r.t_metrics_ms or 0.0,
        }
        bottom = 0.0
        for label, val in comps.items():
            if val > 0:
                pct = 100.0 * val / total_ms if total_ms > 0 else 0.0
                bar = ax.bar(r.config_id, val, bottom=bottom,
                             color=colors[label], label=label)
                if pct >= 5.0:
                    ax.text(0, bottom + val / 2, f"{label}\n{pct:.0f}%",
                            ha="center", va="center", fontsize=8, color="white",
                            fontweight="bold")
                bottom += val

        ax.set_ylabel("ms / step")
        ax.set_title(f"{r.config_id}: {r.grid_w}×{r.grid_h}, N={r.n_agents_initial}")
        ax.set_ylim(0, max(total_ms * 1.15, 1.0))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", fontsize=9)
    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


def _plot_scaling(results: list[BenchResult],
                  grid_exp: float, grid_intercept: float, grid_pts: list,
                  n_exp: float, n_intercept: float, n_pts: list) -> str:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # --- Grid scaling ---
    ids = ("B0", "B1", "B3")
    clr_map = {"B0": "#4e79a7", "B1": "#f28e2b", "B2": "#59a14f",
                "B3": "#e15759", "B4": "#76b7b2", "B5": "#af7aa1", "B6": "#ff9da7"}

    completed = {r.config_id: r for r in results if not r.aborted}

    for cid in ("B0", "B1", "B3"):
        if cid in completed:
            r = completed[cid]
            ax1.scatter(r.grid_w, r.t_total, color=clr_map[cid], zorder=5,
                        s=80, label=cid)

    # Fitted line
    if not math.isnan(grid_exp):
        xs_fit = np.linspace(40, 220, 100)
        ys_fit = np.exp(grid_intercept) * xs_fit ** grid_exp
        ax1.plot(xs_fit, ys_fit, "k--", alpha=0.6,
                 label=f"fit: slope={grid_exp:.2f}")

    ax1.set_xscale("log"); ax1.set_yscale("log")
    ax1.set_xlabel("Grid side (cells)")
    ax1.set_ylabel("t_total (s)")
    ax1.set_title("Grid scaling (N roughly constant)")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # --- N scaling ---
    pair_colors = {"B1": "#4e79a7", "B2": "#4e79a7",
                   "B3": "#f28e2b", "B4": "#f28e2b",
                   "B5": "#59a14f", "B6": "#59a14f"}
    for cid in ("B1", "B2", "B3", "B4", "B5", "B6"):
        if cid in completed:
            r = completed[cid]
            ax2.scatter(r.n_agents_initial, r.t_total,
                        color=pair_colors.get(cid, "gray"), zorder=5,
                        s=80, label=cid)

    if not math.isnan(n_exp):
        ns_fit = np.linspace(400, 3500, 100)
        ts_fit = np.exp(n_intercept) * ns_fit ** n_exp
        ax2.plot(ns_fit, ts_fit, "k--", alpha=0.6,
                 label=f"fit: slope={n_exp:.2f}")

    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel("N agents")
    ax2.set_ylabel("t_total (s)")
    ax2.set_title("N scaling (grid roughly constant within pairs)")
    ax2.legend(fontsize=9, ncol=2)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


# ── Hardware summary ───────────────────────────────────────────────────────────

def _hw_summary() -> dict:
    cpu_str = platform.processor() or "Unknown"
    # Friendly model from registry or fallback
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
    except Exception:
        cpu_name = cpu_str

    n_cpu = os.cpu_count() or 0

    # RAM via Windows API
    try:
        kb = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(kb))
        ram_gb = kb.value / 1e6 / 1000.0
        if ram_gb < 0.5:
            raise ValueError("unlikely")
    except Exception:
        ram_gb = 0.0

    # Try PowerShell fallback for RAM
    if ram_gb < 0.5:
        try:
            import subprocess
            out = subprocess.check_output(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"],
                text=True, timeout=5
            ).strip()
            ram_gb = int(out) / 1e9
        except Exception:
            ram_gb = 0.0

    return {
        "cpu_name": cpu_name.strip(),
        "n_cpu_logical": n_cpu,
        "ram_gb": ram_gb,
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "platform": platform.platform(),
    }


# ── HTML report ────────────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def _row_color(ms_per_step: float) -> str:
    if ms_per_step < FEASIBILITY_THRESHOLD_MS:
        return "background:#d4edda;"
    if ms_per_step > RED_THRESHOLD_MS:
        return "background:#f8d7da;"
    return ""


def build_html_report(
    results: list[BenchResult],
    skipped: dict[str, str],    # config_id → skip reason
    grid_exp: float, n_exp: float,
    grid_pts: list, n_pts: list,
    grid_intercept: float, n_intercept: float,
    hw: dict,
    bench_start_time: float,
) -> str:
    by_id = {r.config_id: r for r in results}
    all_ids = [cfg[0] for cfg in BENCH_CONFIGS]

    # Per-step plots
    psp_plots = {}
    for r in results:
        if r.per_step_ms:
            psp_plots[r.config_id] = _plot_per_step(r)

    # Component bar chart
    comp_bar = _plot_component_bars(results)

    # Scaling plot
    scaling_plot = _plot_scaling(
        results, grid_exp, grid_intercept, grid_pts,
        n_exp, n_intercept, n_pts
    )

    # Bottleneck analysis (B0 and B2)
    bottleneck_text = ""
    for cid in ("B0", "B2"):
        if cid in by_id:
            r = by_id[cid]
            if r.t_grid_ms is not None:
                total = r.t_per_step_mean
                def pct(v): return 100.0 * v / total if total > 0 else 0.0
                bottleneck_text += (
                    f"<b>{cid}</b>: grid {r.t_grid_ms:.1f} ms ({pct(r.t_grid_ms):.0f}%), "
                    f"joint-task {r.t_jt_ms:.1f} ms ({pct(r.t_jt_ms):.0f}%), "
                    f"agent {r.t_agent_ms:.1f} ms ({pct(r.t_agent_ms):.0f}%), "
                    f"pool {r.t_pool_ms:.1f} ms ({pct(r.t_pool_ms):.0f}%), "
                    f"repro {r.t_repro_ms:.1f} ms ({pct(r.t_repro_ms):.0f}%), "
                    f"metrics {r.t_metrics_ms:.1f} ms ({pct(r.t_metrics_ms):.0f}%)<br>"
                )

    # Identify dominant component at B2 (or B0)
    dom_r = by_id.get("B2") or by_id.get("B0")
    if dom_r and dom_r.t_grid_ms is not None:
        comps_vals = {
            "grid update":  dom_r.t_grid_ms,
            "joint-task":   dom_r.t_jt_ms or 0.0,
            "agent step":   dom_r.t_agent_ms or 0.0,
            "pool step":    dom_r.t_pool_ms or 0.0,
            "repro step":   dom_r.t_repro_ms or 0.0,
            "metrics":      dom_r.t_metrics_ms or 0.0,
        }
        total_dom = dom_r.t_per_step_mean
        dom_name = max(comps_vals, key=comps_vals.get)
        dom_pct  = 100.0 * comps_vals[dom_name] / total_dom if total_dom > 0 else 0.0
    else:
        dom_name = "unknown"
        dom_pct  = 0.0

    # Feasibility lists — categorise by single-run time, then LHS estimate
    # single_run_s = actual run time for n_steps_ran steps, extrapolated to 500
    def _run500s(r: BenchResult) -> float:
        return r.t_per_step_mean / 1000.0 * 500.0   # seconds for 500 steps

    def _lhs_hrs(r: BenchResult) -> float:
        return _run500s(r) * 300.0 / 4.0 / 3600.0

    feasible = [r for r in results if _run500s(r) < 300 and not r.aborted]  # single run < 5 min
    needs_opt = [r for r in results if _run500s(r) >= 300 or r.aborted]

    # LHS 300-run wall time estimate at 4 workers (using extrapolated 500-step time)
    def est_lhs_hrs(r: BenchResult) -> str:
        return f"{_lhs_hrs(r):.1f}h"

    # N exponent interpretation
    n_exp_safe = n_exp if not math.isnan(n_exp) else 999.0
    if n_exp_safe < 1.3:
        n_scaling_verdict = f"O(N^{n_exp:.2f}) — linear or near-linear (no super-linear bottleneck)"
    else:
        n_scaling_verdict = (f"O(N^{n_exp:.2f}) — SUPER-LINEAR, "
                             f"pool pair-checking or O(N^2) code present. Fix before scaling.")

    grid_exp_safe = grid_exp if not math.isnan(grid_exp) else 999.0

    total_bench_time = perf_counter() - bench_start_time

    # ── §5 feasibility verdict text ──────────────────────────────────────────
    feasible_ids  = [r.config_id for r in feasible]
    needs_opt_ids = [r.config_id for r in needs_opt]

    verdict_grid = (
        f"Runtime scales as O(grid^{grid_exp:.2f}) "
        f"based on B0/B1/B3 comparison."
        if not math.isnan(grid_exp) else
        "Insufficient data for grid scaling fit (need B0, B1, B3 to complete)."
    )
    verdict_n = (
        f"Runtime scales as O(N^{n_exp:.2f}) "
        f"based on B1/B2 and B3/B4 comparisons."
        if not math.isnan(n_exp) else
        "Insufficient data for N scaling fit."
    )
    verdict_bottleneck = (
        f"The dominant cost at current scale ({dom_r.config_id if dom_r else '?'}) "
        f"is {dom_name} at {dom_pct:.0f}% of step time."
    )

    if feasible_ids:
        verdict_feasibility = (
            f"Configurations feasible for LHS-scale work "
            f"(500 steps < 5 min): {', '.join(feasible_ids)}. "
        )
    else:
        verdict_feasibility = "No configurations completed 500 steps in < 5 minutes. "
    if needs_opt_ids:
        verdict_feasibility += (
            f"Configurations requiring optimisation: {', '.join(needs_opt_ids)}."
        )

    # §6 recommendations
    # §6 buckets by single-run time (500 steps) and LHS estimate
    safe_r  = [r for r in results if not r.aborted and _lhs_hrs(r) < 4.0]
    care_r  = [r for r in results if not r.aborted and 4.0 <= _lhs_hrs(r) <= 12.0]
    # Needs optimisation: single run > 5 min (300s) OR aborted
    opt_r   = [r for r in results if r.aborted or _run500s(r) > 300.0]
    skipped_r = [(cid, reason) for cid, reason in skipped.items()]

    def lhs_table_row(r: BenchResult) -> str:
        t_total_est = r.t_total
        lhs_secs = 300 * t_total_est / 4
        lhs_hrs = lhs_secs / 3600
        return (f"<tr><td>{r.config_id}</td><td>{r.grid_w}×{r.grid_h}</td>"
                f"<td>{r.n_agents_initial}</td>"
                f"<td>{r.t_per_step_mean:.1f}</td>"
                f"<td>{lhs_hrs:.1f}h</td></tr>")

    # ── Build HTML ────────────────────────────────────────────────────────────
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SiC Games Runtime Benchmark — 2026-05-27</title>
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; color: #222; line-height: 1.5; }
  h1 { color: #1a3a5c; }
  h2 { color: #2c5f8a; border-bottom: 2px solid #2c5f8a; padding-bottom: 4px; margin-top: 2em; }
  h3 { color: #3a7bbf; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 1.5em; }
  th { background: #2c5f8a; color: white; padding: 8px 12px; text-align: left; }
  td { padding: 7px 12px; border-bottom: 1px solid #ddd; }
  tr:hover td { background: #f5f9ff; }
  .green { background: #d4edda !important; }
  .red   { background: #f8d7da !important; }
  .skip  { background: #fff3cd !important; color: #856404; }
  pre { background: #f4f4f4; padding: 12px; border-radius: 4px; font-size: 13px; }
  .verdict { background: #eaf4fb; border-left: 4px solid #2c5f8a; padding: 12px 16px;
             border-radius: 0 4px 4px 0; margin: 1em 0; }
  .warn { background: #fff3cd; border-left: 4px solid #e09900; }
  .ok   { background: #d4edda; border-left: 4px solid #28a745; }
  img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin: 8px 0; }
  .toc { background: #f8f9fa; padding: 12px 20px; border-radius: 4px; display: inline-block; }
  .toc a { color: #2c5f8a; text-decoration: none; display: block; margin: 4px 0; }
  .toc a:hover { text-decoration: underline; }
</style>
</head>
<body>
<h1>SiC Games — Runtime Benchmark Report</h1>
<p><b>Date:</b> 2026-05-27 &nbsp;|&nbsp; <b>Total benchmark time:</b> """ + f"{total_bench_time/60:.1f} min" + """</p>
<div class="toc">
  <b>Contents</b>
  <a href="#s0">§0 Configuration &amp; Hardware</a>
  <a href="#s1">§1 Timing Results</a>
  <a href="#s2">§2 Component Breakdown</a>
  <a href="#s3">§3 Scaling Plots</a>
  <a href="#s4">§4 Memory Table</a>
  <a href="#s5">§5 Feasibility Verdict</a>
  <a href="#s6">§6 Recommended Grid Sizes</a>
</div>
""")

    # §0 — Config table + hardware
    html_parts.append('<h2 id="s0">§0 — Configuration &amp; Hardware</h2>')

    # Hardware
    html_parts.append("<h3>Hardware / Software Summary</h3>")
    html_parts.append(f"""<table style="width:auto">
<tr><th>Item</th><th>Value</th></tr>
<tr><td>CPU</td><td>{_esc(hw['cpu_name'])}</td></tr>
<tr><td>Logical cores</td><td>{hw['n_cpu_logical']}</td></tr>
<tr><td>RAM</td><td>{hw['ram_gb']:.1f} GB</td></tr>
<tr><td>Python</td><td>{hw['python_version']}</td></tr>
<tr><td>numpy</td><td>{hw['numpy_version']}</td></tr>
<tr><td>Platform</td><td>{_esc(hw['platform'])}</td></tr>
</table>""")

    # Config table
    html_parts.append("<h3>Benchmark Configurations</h3>")
    html_parts.append("""<table>
<tr><th>ID</th><th>Grid</th><th>N</th><th>Density</th><th>Steps</th>
    <th>band_k</th><th>N_carry</th><th>Purpose</th><th>Status</th></tr>""")

    purposes = {
        "B0": "Baseline (50x50)",
        "B1": "2x grid, half density",
        "B2": "2x grid, same density",
        "B3": "3x grid, lower density",
        "B4": "3x grid, same density",
        "B5": "4x grid, lower density",
        "B6": "4x grid, near-same density",
    }
    for cid, gw, gh, n, dens, ns in BENCH_CONFIGS:
        bk = max(1, int(round(gw / 50 * 6)))
        nc = max(400, int(400 * (gw * gh) / (50 * 50)))
        if cid in by_id:
            r = by_id[cid]
            status = "&#10003; ran" if not r.aborted else "&#9888; aborted"
            css = "" if not r.aborted else ' class="skip"'
        elif cid in skipped:
            status = f"&#8212; skipped: {_esc(skipped[cid])}"
            css = ' class="skip"'
        else:
            status = "&#8212; not reached"
            css = ' class="skip"'
        html_parts.append(
            f"<tr{css}><td>{cid}</td><td>{gw}x{gh}</td><td>{n}</td>"
            f"<td>{dens:.1f}%</td><td>{ns}</td><td>{bk}</td><td>{nc}</td>"
            f"<td>{purposes.get(cid,'')}</td><td>{status}</td></tr>"
        )
    html_parts.append("</table>")

    html_parts.append("""<p><small>
  <b>Scaling rules:</b> peak positions at (0.2W, 0.8H) and (0.8W, 0.2H);
  band_width_k = W/50 &times; 6; k_grid=4 (max_sugar=16, alpha=4);
  N_carry scales proportionally to grid area.
  All runs: seed=42, static world (null perturbation), C strategy, full Stage 5 mechanics.
</small></p>""")

    # §1 — Timing table
    html_parts.append('<h2 id="s1">§1 — Timing Results</h2>')
    html_parts.append("""<p>
  <span style="background:#d4edda;padding:2px 8px;border-radius:3px">Green</span> = ms/step &lt; 600 (500 steps &lt; 5 min). &nbsp;
  <span style="background:#f8d7da;padding:2px 8px;border-radius:3px">Red</span> = ms/step &gt; 2400 (500 steps &gt; 20 min).
</p>""")
    html_parts.append("""<table>
<tr><th>ID</th><th>Grid</th><th>N</th><th>Steps ran</th>
    <th>t_total (s)</th><th>ms/step (mean)</th><th>ms/step (std)</th>
    <th>t_warmup (s)</th><th>agent-steps/s</th><th>Status</th></tr>""")

    for cid, gw, gh, n, dens, ns in BENCH_CONFIGS:
        if cid in by_id:
            r = by_id[cid]
            ms = r.t_per_step_mean
            css_color = _row_color(ms)
            css = f' style="{css_color}"' if css_color else ""
            aborted_flag = " (aborted)" if r.aborted else ""
            html_parts.append(
                f"<tr{css}><td>{cid}</td><td>{gw}x{gh}</td><td>{n}</td>"
                f"<td>{r.n_steps_ran}{aborted_flag}</td>"
                f"<td>{r.t_total:.2f}</td>"
                f"<td>{r.t_per_step_mean:.1f}</td>"
                f"<td>{r.t_per_step_std:.1f}</td>"
                f"<td>{r.t_warmup:.2f}</td>"
                f"<td>{r.agent_steps_per_second:,.0f}</td>"
                f"<td>{'&#10003;' if not r.aborted else '&#9888;'}</td></tr>"
            )
        elif cid in skipped:
            html_parts.append(
                f'<tr class="skip"><td>{cid}</td><td>{gw}x{gh}</td><td>{n}</td>'
                f'<td colspan="7">Skipped: {_esc(skipped[cid])}</td></tr>'
            )
        else:
            html_parts.append(
                f'<tr class="skip"><td>{cid}</td><td>{gw}x{gh}</td><td>{n}</td>'
                f'<td colspan="7">Not reached</td></tr>'
            )
    html_parts.append("</table>")

    # Per-step time series plots
    if psp_plots:
        html_parts.append("<h3>Per-step time series (B0, B2, B4)</h3>")
        html_parts.append("<p>A flat line confirms steady-state timing; "
                          "upward drift indicates memory pressure.</p>")
        for cid in ("B0", "B2", "B4"):
            if cid in psp_plots and psp_plots[cid]:
                html_parts.append(f'<img src="data:image/png;base64,{psp_plots[cid]}" '
                                   f'alt="{cid} per-step timing">')

    # §2 — Component breakdown
    html_parts.append('<h2 id="s2">§2 — Component Breakdown (B0 and B2)</h2>')
    if comp_bar:
        html_parts.append(f'<img src="data:image/png;base64,{comp_bar}" '
                          f'alt="Component breakdown stacked bars">')
    else:
        html_parts.append("<p><i>No component timing data available.</i></p>")

    if bottleneck_text:
        html_parts.append(f"<p>{bottleneck_text}</p>")

    # §3 — Scaling plots
    html_parts.append('<h2 id="s3">§3 — Scaling Plots</h2>')
    grid_exp_str = f"{grid_exp:.3f}" if not math.isnan(grid_exp) else "N/A"
    n_exp_str    = f"{n_exp:.3f}"    if not math.isnan(n_exp)    else "N/A"
    html_parts.append(f"""<p>
  <b>Grid exponent:</b> {grid_exp_str} (expected ~2 if grid update dominates, ~1 if agent loop dominates)<br>
  <b>N exponent:</b> {n_exp_str} (expected ~1 if O(N), ~2 if O(N^2) bottleneck)
</p>""")
    if not math.isnan(n_exp) and n_exp > 1.3:
        html_parts.append(
            f'<div class="verdict warn"><b>Warning:</b> N exponent = {n_exp:.2f} &gt; 1.3 — '
            f'super-linear scaling detected. Pool pair-checking or O(N^2) code may be present. '
            f'Investigate before LHS-scale work.</div>'
        )
    if scaling_plot:
        html_parts.append(f'<img src="data:image/png;base64,{scaling_plot}" '
                          f'alt="Scaling log-log plots">')

    # §4 — Memory table
    html_parts.append('<h2 id="s4">§4 — Memory</h2>')
    html_parts.append("""<table>
<tr><th>ID</th><th>mem_t0 (MB)</th><th>mem_t250 (MB)</th><th>mem_t500 (MB)</th>
    <th>mem_delta (MB)</th><th>Leak?</th></tr>""")
    for r in results:
        leak = "YES" if r.mem_delta_mb > 10 else "no"
        leak_css = ' style="color:red;font-weight:bold"' if r.mem_delta_mb > 10 else ' style="color:green"'
        html_parts.append(
            f"<tr><td>{r.config_id}</td>"
            f"<td>{r.mem_t0_mb:.1f}</td>"
            f"<td>{r.mem_t250_mb:.1f}</td>"
            f"<td>{r.mem_t500_mb:.1f}</td>"
            f"<td>{r.mem_delta_mb:+.1f}</td>"
            f"<td{leak_css}>{leak}</td></tr>"
        )
    html_parts.append("</table>")
    html_parts.append(
        "<p><small>mem_delta = mem_t500 - mem_t0 (peak traced). "
        "Values &gt; 10 MB indicate a possible memory leak in parquet buffering "
        "or metric accumulation.</small></p>"
    )

    # §5 — Feasibility verdict
    html_parts.append('<h2 id="s5">§5 — Feasibility Verdict</h2>')
    html_parts.append('<div class="verdict">')
    html_parts.append(f"<p><b>1. Grid scaling:</b> {_esc(verdict_grid)}</p>")
    html_parts.append(f"<p><b>2. N scaling:</b> {_esc(verdict_n)}</p>")
    html_parts.append(f"<p><b>3. Bottleneck:</b> {_esc(verdict_bottleneck)}</p>")
    html_parts.append(f"<p><b>4. Feasibility boundary:</b> {_esc(verdict_feasibility)}</p>")
    html_parts.append("</div>")

    # §6 — Grid recommendations
    html_parts.append('<h2 id="s6">§6 — Recommended Grid Sizes for Stage 5.x</h2>')
    html_parts.append("""<p>
  LHS reference workload: 30-run LHS × 5 seeds × 2 strategies = <b>300 runs</b>,
  4 parallel workers.
</p>""")

    if safe_r:
        html_parts.append('<h3>Safe (no changes needed)</h3>')
        html_parts.append("<p>LHS wall time &lt;4 hours at 4 workers:</p>")
        html_parts.append('<table><tr><th>ID</th><th>Grid</th><th>N</th>'
                          '<th>ms/step</th><th>Est. LHS wall time</th></tr>')
        for r in safe_r:
            html_parts.append(lhs_table_row(r))
        html_parts.append("</table>")
    else:
        html_parts.append('<h3>Safe (no changes needed)</h3>')
        html_parts.append('<p><i>No configuration achieves &lt;4-hour LHS at 4 workers with current code.</i></p>')

    if care_r:
        html_parts.append('<h3>Feasible with care (LHS 4–12 hours, weekend batch viable)</h3>')
        html_parts.append('<table><tr><th>ID</th><th>Grid</th><th>N</th>'
                          '<th>ms/step</th><th>Est. LHS wall time</th></tr>')
        for r in care_r:
            html_parts.append(lhs_table_row(r))
        html_parts.append("</table>")

    if opt_r:
        html_parts.append('<h3>Needs optimisation first (single runs &gt;5 min)</h3>')
        html_parts.append('<table><tr><th>ID</th><th>Grid</th><th>N</th><th>Reason</th></tr>')
        for r in opt_r:
            reason = "aborted (>20 min)" if r.aborted else f"{r.t_per_step_mean:.0f} ms/step"
            html_parts.append(f"<tr><td>{r.config_id}</td><td>{r.grid_w}x{r.grid_h}</td>"
                               f"<td>{r.n_agents_initial}</td><td>{reason}</td></tr>")
        html_parts.append("</table>")

    if skipped_r:
        html_parts.append("<h3>Skipped</h3>")
        html_parts.append('<table><tr><th>ID</th><th>Reason</th></tr>')
        for cid, reason in skipped_r:
            html_parts.append(f"<tr><td>{cid}</td><td>{_esc(reason)}</td></tr>")
        html_parts.append("</table>")

    # JT bottleneck action box — fires whenever JT was measured (B0 always timed)
    jt_r = by_id.get("B0") or by_id.get("B2")
    jt_dominant = (jt_r is not None and jt_r.t_jt_ms is not None
                   and jt_r.t_per_step_mean > 0
                   and (jt_r.t_jt_ms / jt_r.t_per_step_mean) > 0.3)
    if jt_dominant:
        jt_pct = 100.0 * jt_r.t_jt_ms / jt_r.t_per_step_mean
        html_parts.append(f"""
<div class="verdict warn">
<b>Action required before Stage 5.x scale-up:</b>
<code>JointTaskManager.process_step()</code> accounts for {jt_pct:.0f}% of step time at {jt_r.config_id}.
It iterates over every candidate cell &times; every agent — <b>O(W&times;H&times;N)</b> per step.
At constant density N&nbsp;&prop;&nbsp;W&times;H, this is <b>O(grid&#178;&times;N)&nbsp;=&nbsp;O(grid&#179;)</b>,
measured grid exponent {grid_exp_str}.
<br><br>
<b>Fix (before Stage 5.x):</b> In <code>joint_task.py JointTaskManager.process_step()</code>,
replace the full agent scan per candidate cell with a spatial hash (cell&nbsp;&rarr;&nbsp;agents at distance&nbsp;d=1).
At d=1, each candidate cell only needs to check the 9 adjacent cells — O(1) per cell
regardless of N, reducing JT to O(W&times;H) per step.
Expected speedup at B1 scale: &gt;10&times;.
</div>""")
    elif not math.isnan(n_exp) and n_exp > 1.3:
        html_parts.append(f"""
<div class="verdict warn">
<b>Super-linear N scaling detected (exponent={n_exp_str}).</b>
Investigate O(N^2) code paths (pool pair-checking, vision scan, joint-task detection).
</div>""")
    elif not math.isnan(n_exp):
        html_parts.append(f"""
<div class="verdict ok">
<b>N scaling confirmed linear-ish (exponent={n_exp_str}).</b>
No O(N^2) bottleneck detected.
</div>""")

    html_parts.append(f"""
<hr>
<p><small>Generated by <code>sic_games.benchmark</code> on {_TODAY}.
Benchmark total wall time: {total_bench_time/60:.1f} min.</small></p>
</body></html>""")

    return "".join(html_parts)


# ── Main orchestration ─────────────────────────────────────────────────────────

def _save_cache(results: list[BenchResult], skipped: dict, hw: dict,
                bench_elapsed: float) -> None:
    """Persist benchmark results to JSON for report-only re-runs."""
    import dataclasses, json
    cache = {
        "results": [dataclasses.asdict(r) for r in results],
        "skipped": skipped,
        "hw": hw,
        "bench_elapsed": bench_elapsed,
    }
    cache_path = _OUT / "benchmark_cache.json"
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    print(f"  Cache saved: {cache_path}")


def _load_cache() -> tuple[list[BenchResult], dict, dict, float] | None:
    """Load cached results. Returns (results, skipped, hw, bench_elapsed) or None."""
    import json
    cache_path = _OUT / "benchmark_cache.json"
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        results = [BenchResult(**r) for r in data["results"]]
        return results, data["skipped"], data["hw"], data.get("bench_elapsed", 0.0)
    except Exception as e:
        print(f"  Cache load failed ({e}), re-running benchmarks.")
        return None


def main() -> None:
    import sys
    report_only = "--report-only" in sys.argv

    print(f"SiC Games Runtime Benchmark — {_TODAY}")
    print(f"Output: {_OUT}")
    _OUT.mkdir(parents=True, exist_ok=True)

    hw = _hw_summary()
    bench_start = perf_counter()

    if report_only:
        cached = _load_cache()
        if cached is None:
            print("No cache found; run without --report-only first.")
            sys.exit(1)
        results, skipped, hw, bench_elapsed = cached
        print(f"  Loaded {len(results)} cached results.")
        print("Building HTML report...")
        grid_exp, grid_intercept, grid_pts = _grid_scaling_exponent(results)
        n_exp, n_intercept, n_pts = _n_scaling_exponent(results)
        html = build_html_report(
            results=results, skipped=skipped,
            grid_exp=grid_exp, n_exp=n_exp,
            grid_pts=grid_pts, n_pts=n_pts,
            grid_intercept=grid_intercept, n_intercept=n_intercept,
            hw=hw, bench_start_time=perf_counter() - bench_elapsed,
        )
        report_path = _OUT / "report_benchmark.html"
        report_path.write_text(html, encoding="utf-8")
        print(f"  Report written: {report_path}")
        return

    print(f"  CPU:  {hw['cpu_name']}")
    print(f"  RAM:  {hw['ram_gb']:.1f} GB  |  {hw['n_cpu_logical']} logical CPUs")
    print(f"  Python {hw['python_version']}  |  numpy {hw['numpy_version']}")
    print()

    # Smoke test
    print("Smoke test (10 steps, B0 config):")
    smoke_ms = smoke_test()
    print()

    bench_start = perf_counter()

    results: list[BenchResult] = []
    skipped: dict[str, str] = {}   # config_id → reason

    def _should_run(cid: str) -> bool:
        return cid not in skipped

    # ── B0 ────────────────────────────────────────────────────────────────────
    print("Running benchmarks:")
    r = run_one("B0", 50, 50, 250, 10.0, 500,
                with_components=True, with_per_step_list=True)
    results.append(r)
    if r.aborted or r.t_total > STOP_WARN_S:
        skipped.update({c: f"B0 exceeded {STOP_WARN_S/60:.0f} min limit"
                        for c in ("B1","B2","B3","B4","B5","B6")})

    # ── B1 ────────────────────────────────────────────────────────────────────
    if _should_run("B1"):
        r = run_one("B1", 100, 100, 500, 5.0, 500,
                    with_components=False, with_per_step_list=False)
        results.append(r)
        if r.aborted or r.t_total > STOP_WARN_S:
            skipped.update({c: f"B1 exceeded {STOP_WARN_S/60:.0f} min limit"
                            for c in ("B2","B3","B4","B5","B6")})

    # ── B2 ────────────────────────────────────────────────────────────────────
    if _should_run("B2"):
        r = run_one("B2", 100, 100, 1000, 10.0, 500,
                    with_components=True, with_per_step_list=True)
        results.append(r)
        if r.aborted or r.t_total > STOP_WARN_S:
            skipped.update({c: f"B2 exceeded {STOP_WARN_S/60:.0f} min limit"
                            for c in ("B3","B4","B5","B6")})

    # ── B3 ────────────────────────────────────────────────────────────────────
    if _should_run("B3"):
        r = run_one("B3", 150, 150, 1000, 4.4, 500,
                    with_components=False, with_per_step_list=False)
        results.append(r)
        if r.aborted or r.t_total > STOP_WARN_S:
            skipped.update({c: f"B3 exceeded {STOP_WARN_S/60:.0f} min limit"
                            for c in ("B4","B5","B6")})
        elif r.t_total > SKIP_B4_S:
            print(f"    B3 total = {r.t_total/60:.1f} min > 10 min → skipping B4, running B5 only")
            skipped["B4"] = f"B3 took {r.t_total/60:.1f} min > 10 min threshold"

    # ── B4 ────────────────────────────────────────────────────────────────────
    if _should_run("B4"):
        r = run_one("B4", 150, 150, 2000, 8.9, 500,
                    with_components=False, with_per_step_list=True)
        results.append(r)
        if r.aborted or r.t_total > STOP_WARN_S:
            skipped.update({c: f"B4 exceeded {STOP_WARN_S/60:.0f} min limit"
                            for c in ("B5","B6")})

    # ── B5 ────────────────────────────────────────────────────────────────────
    if _should_run("B5"):
        r = run_one("B5", 200, 200, 1500, 3.75, 500,
                    with_components=False, with_per_step_list=False)
        results.append(r)
        if r.aborted or r.t_total > SKIP_B6_S:
            reason = (f"B5 exceeded {SKIP_B6_S/60:.0f} min limit"
                      if r.t_total > SKIP_B6_S
                      else "B5 aborted")
            skipped["B6"] = reason
            print(f"    B5 total = {r.t_total/60:.1f} min > 20 min → skipping B6 and flagging")

    # ── B6 ────────────────────────────────────────────────────────────────────
    if _should_run("B6"):
        r = run_one("B6", 200, 200, 3000, 7.5, 500,
                    with_components=False, with_per_step_list=False)
        results.append(r)

    print()

    # ── Save cache ────────────────────────────────────────────────────────────
    _save_cache(results, skipped, hw, perf_counter() - bench_start)

    # ── Scaling analysis ──────────────────────────────────────────────────────
    print("Computing scaling exponents...")
    grid_exp, grid_intercept, grid_pts = _grid_scaling_exponent(results)
    n_exp, n_intercept, n_pts = _n_scaling_exponent(results)

    if not math.isnan(grid_exp):
        print(f"  Grid exponent: {grid_exp:.3f}")
    else:
        print("  Grid exponent: N/A (insufficient data)")
    if not math.isnan(n_exp):
        print(f"  N exponent:    {n_exp:.3f}")
    else:
        print("  N exponent: N/A (insufficient data)")

    # ── Build report ──────────────────────────────────────────────────────────
    print("Building HTML report...")
    html = build_html_report(
        results=results,
        skipped=skipped,
        grid_exp=grid_exp,
        n_exp=n_exp,
        grid_pts=grid_pts,
        n_pts=n_pts,
        grid_intercept=grid_intercept,
        n_intercept=n_intercept,
        hw=hw,
        bench_start_time=bench_start,
    )

    report_path = _OUT / "report_benchmark.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"  Report written: {report_path}")

    # Summary
    total_t = perf_counter() - bench_start
    print()
    print(f"Benchmark complete in {total_t/60:.1f} min.")
    print(f"Report: {report_path}")
    print()

    # Print summary table to console
    print(f"{'ID':<4} {'Grid':<10} {'N':>5}  {'ms/step':>9}  {'agent-steps/s':>14}  {'status'}")
    print("-" * 60)
    by_id = {r.config_id: r for r in results}
    for cid, gw, gh, n, _, _ in BENCH_CONFIGS:
        if cid in by_id:
            r = by_id[cid]
            flag = "ABORTED" if r.aborted else ("OK" if r.t_per_step_mean < FEASIBILITY_THRESHOLD_MS else "SLOW")
            print(f"{cid:<4} {gw}x{gh:<6}  {n:>5}  {r.t_per_step_mean:>9.1f}  {r.agent_steps_per_second:>14,.0f}  {flag}")
        elif cid in skipped:
            print(f"{cid:<4} {gw}x{gh:<6}  {n:>5}  {'---':>9}  {'---':>14}  SKIP: {skipped[cid][:30]}")


if __name__ == "__main__":
    main()
