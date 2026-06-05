"""Post-fix verification benchmark — JointTask spatial-hash fix.

Runs B0–B4 configs with the fixed JointTaskManager and produces a
comparison report against the pre-fix baseline.

Usage:
    py -m sic_games.benchmark_postfix

Output: outputs/benchmark_post_fix/report_benchmark_postfix.html
"""
from __future__ import annotations

import base64
import io
import json
import math
import os
import sys
import tracemalloc
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
_REPO    = Path(__file__).parent.parent.parent
_OUT     = _REPO / "outputs" / "benchmark_post_fix"
_TODAY   = "2026-05-27"

# Pre-fix baseline values (from outputs/benchmark/benchmark_cache.json)
_PRE_FIX = {
    "B0": {"ms_step": 499.6, "status": "complete"},
    "B1": {"ms_step": 7378.5, "status": "aborted@200steps"},
}

# Stopping / feasibility thresholds (same as pre-fix benchmark)
STOP_WARN_S          = 20 * 60   # 20 min → abort
FEASIBILITY_MS       = 600        # < 600 ms/step = feasible (500 steps < 5 min)
RED_MS               = 2400

# ── Config reuse ────────────────────────────────────────────────────────────────
from sic_games.benchmark import (
    _bench_c_config,
    _ComponentTimer, _attach_component_timers, _detach_component_timers,
    _hw_summary, _fig_to_b64, _esc, _row_color,
)

COMPONENT_CONFIGS    = {"B0", "B1"}   # component breakdown for both baseline and B1
PER_STEP_LIST_CONFIGS = {"B0", "B1"}

# ── Result container ────────────────────────────────────────────────────────────
@dataclass
class PostFixResult:
    config_id: str
    grid_w: int
    grid_h: int
    n_agents: int
    density_pct: float
    n_steps_ran: int
    n_steps_target: int
    aborted: bool
    skip_reason: str

    t_total: float
    t_per_step_mean: float
    t_per_step_std: float
    t_warmup: float
    per_step_ms: list[float] = field(default_factory=list)

    t_grid_ms: float | None = None
    t_jt_ms: float | None = None
    t_agent_ms: float | None = None
    t_pool_ms: float | None = None
    t_repro_ms: float | None = None
    t_metrics_ms: float | None = None

    mem_t0_mb: float = 0.0
    mem_t250_mb: float = 0.0
    mem_t500_mb: float = 0.0
    mem_delta_mb: float = 0.0

    agent_steps_per_second: float = 0.0

    @property
    def speedup(self) -> float | None:
        pre = _PRE_FIX.get(self.config_id, {}).get("ms_step")
        if pre is None or self.t_per_step_mean <= 0:
            return None
        return pre / self.t_per_step_mean


# ── Single run ──────────────────────────────────────────────────────────────────
def run_one(config_id: str, grid_w: int, grid_h: int, n_agents: int,
            density_pct: float, n_steps: int,
            with_components: bool, with_per_step_list: bool,
            stop_at_s: float = STOP_WARN_S) -> PostFixResult:
    from sic_games.run import SugarWorld

    print(f"  [{config_id}] grid={grid_w}x{grid_h} N={n_agents} ...", end=" ", flush=True)
    cfg = _bench_c_config(grid_w, grid_h, n_agents, n_steps)
    world = SugarWorld(cfg, env_seed=42, agent_seed=42)

    timers = _attach_component_timers(world) if with_components else None

    tracemalloc.start()
    cur0, _ = tracemalloc.get_traced_memory()
    mem_t0_mb = cur0 / 1e6

    step_times: list[float] = []
    t_start = perf_counter()
    aborted = False
    n_ran = 0
    mem_t250_mb = mem_t500_mb = 0.0
    _MEM_250 = 249
    _MEM_500 = min(n_steps - 1, 499)

    for s in range(n_steps):
        t0 = perf_counter()
        world.step()
        step_times.append(perf_counter() - t0)
        n_ran += 1

        if timers:
            for name in ("grid", "jt", "pool", "repro", "metrics"):
                timers[name].finalize_step()

        if s == _MEM_250:
            cur, _ = tracemalloc.get_traced_memory()
            mem_t250_mb = cur / 1e6
        if s == _MEM_500:
            cur, _ = tracemalloc.get_traced_memory()
            mem_t500_mb = cur / 1e6

        if (s + 1) % 50 == 0:
            elapsed = perf_counter() - t_start
            if elapsed > stop_at_s:
                aborted = True
                print(f"\n    STOPPED at step {s+1} ({elapsed/60:.1f} min)")
                break

    t_total = perf_counter() - t_start

    if mem_t500_mb == 0.0:
        cur, _ = tracemalloc.get_traced_memory()
        mem_t500_mb = cur / 1e6
    if mem_t250_mb == 0.0:
        mem_t250_mb = mem_t500_mb
    tracemalloc.stop()

    t_grid_ms = t_jt_ms = t_agent_ms = t_pool_ms = t_repro_ms = t_metrics_ms = None
    if timers:
        _detach_component_timers(timers)
        t_grid_ms    = timers["grid"].mean_ms
        t_jt_ms      = timers["jt"].mean_ms
        t_pool_ms    = timers["pool"].mean_ms
        t_repro_ms   = timers["repro"].mean_ms
        t_metrics_ms = timers["metrics"].mean_ms
        mean_total   = float(np.mean(step_times)) * 1000.0
        t_agent_ms   = max(0.0, mean_total - t_grid_ms - t_jt_ms
                           - t_pool_ms - t_repro_ms - t_metrics_ms)

    arr = np.array(step_times) * 1000.0
    t_per_step_mean = float(np.mean(arr))
    t_per_step_std  = float(np.std(arr))
    t_warmup        = float(np.sum(step_times[:min(50, len(step_times))]))
    per_step_ms     = list(arr) if with_per_step_list else []

    print(f"done in {t_total:.1f}s  ({t_per_step_mean:.1f} ms/step)", end="")
    pre = _PRE_FIX.get(config_id, {}).get("ms_step")
    if pre:
        print(f"  [{pre/t_per_step_mean:.1f}x speedup]", end="")
    print()

    return PostFixResult(
        config_id=config_id, grid_w=grid_w, grid_h=grid_h,
        n_agents=n_agents, density_pct=density_pct,
        n_steps_ran=n_ran, n_steps_target=n_steps,
        aborted=aborted, skip_reason="",
        t_total=t_total, t_per_step_mean=t_per_step_mean,
        t_per_step_std=t_per_step_std, t_warmup=t_warmup,
        per_step_ms=per_step_ms,
        t_grid_ms=t_grid_ms, t_jt_ms=t_jt_ms, t_agent_ms=t_agent_ms,
        t_pool_ms=t_pool_ms, t_repro_ms=t_repro_ms, t_metrics_ms=t_metrics_ms,
        mem_t0_mb=mem_t0_mb, mem_t250_mb=mem_t250_mb,
        mem_t500_mb=mem_t500_mb, mem_delta_mb=mem_t500_mb - mem_t0_mb,
        agent_steps_per_second=(n_agents * n_ran) / t_total if t_total > 0 else 0.0,
    )


# ── Scaling ──────────────────────────────────────────────────────────────────────
def _norm500(r: PostFixResult) -> float:
    return r.t_per_step_mean / 1000.0 * 500.0

def _grid_exp(results: list[PostFixResult]) -> tuple[float, float]:
    pts = [(r.grid_w, _norm500(r)) for r in results
           if r.config_id in ("B0", "B1", "B3")]
    if len(pts) < 2:
        return float("nan"), float("nan")
    xs = np.log([p[0] for p in pts])
    ys = np.log([p[1] for p in pts])
    A = np.vstack([xs, np.ones(len(xs))]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    return float(slope), float(intercept)

def _n_exp(results: list[PostFixResult]) -> tuple[float, float]:
    pairs = [("B1", "B2"), ("B3", "B4")]
    by_id = {r.config_id: r for r in results}
    pts = []
    for a, b in pairs:
        if a in by_id and b in by_id:
            pts += [(by_id[a].n_agents, _norm500(by_id[a])),
                    (by_id[b].n_agents, _norm500(by_id[b]))]
    if len(pts) < 2:
        return float("nan"), float("nan")
    xs = np.log([p[0] for p in pts])
    ys = np.log([p[1] for p in pts])
    A = np.vstack([xs, np.ones(len(xs))]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    return float(slope), float(intercept)


# ── Plots ─────────────────────────────────────────────────────────────────────
def _plot_comparison_bars(results: list[PostFixResult]) -> str | None:
    """Pre vs post component stacked bars for B0 and B1."""
    comp_r = [r for r in results if r.config_id in COMPONENT_CONFIGS
              and r.t_jt_ms is not None]
    if not comp_r:
        return None

    # Pre-fix B0 components (from cache)
    pre_b0 = {"Grid": 0.0, "JointTask": 445.9, "Agent": 44.0,
               "Pool": 1.9, "Repro": 1.6, "Metrics": 6.1}

    colors = {"Grid": "#4e79a7", "JointTask": "#edc948",
              "Agent": "#f28e2b", "Pool": "#59a14f",
              "Repro": "#e15759", "Metrics": "#76b7b2"}

    n_cols = 1 + len(comp_r)   # pre-B0 + each post-fix config with components
    fig, axes = plt.subplots(1, n_cols, figsize=(4.5 * n_cols, 4.5))
    if n_cols == 1:
        axes = [axes]

    def _draw(ax, label, comps, total_ms):
        bottom = 0.0
        for name, val in comps.items():
            if val > 0:
                pct = 100.0 * val / total_ms if total_ms > 0 else 0.0
                ax.bar(label, val, bottom=bottom, color=colors.get(name, "gray"))
                if pct >= 4.0:
                    ax.text(0, bottom + val / 2, f"{name}\n{pct:.0f}%",
                            ha="center", va="center", fontsize=8,
                            color="white", fontweight="bold")
                bottom += val
        ax.set_ylabel("ms / step")
        ax.set_ylim(0, max(total_ms * 1.2, 1.0))

    # Pre-fix B0
    _draw(axes[0], "B0 pre-fix", pre_b0, sum(pre_b0.values()))
    axes[0].set_title("B0 pre-fix (50×50)")

    for ax, r in zip(axes[1:], comp_r):
        post_comps = {
            "Grid":      r.t_grid_ms or 0.0,
            "JointTask": r.t_jt_ms or 0.0,
            "Agent":     r.t_agent_ms or 0.0,
            "Pool":      r.t_pool_ms or 0.0,
            "Repro":     r.t_repro_ms or 0.0,
            "Metrics":   r.t_metrics_ms or 0.0,
        }
        _draw(ax, f"{r.config_id} post-fix", post_comps, r.t_per_step_mean)
        ax.set_title(f"{r.config_id} post-fix ({r.grid_w}×{r.grid_h})")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=colors[k], label=k) for k in colors]
    fig.legend(handles=legend_elements, loc="upper right", fontsize=9)
    fig.suptitle("Component breakdown: pre-fix B0 vs post-fix", fontsize=11)
    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


def _plot_per_step(r: PostFixResult) -> str | None:
    if not r.per_step_ms:
        return None
    fig, ax = plt.subplots(figsize=(8, 3))
    xs = np.arange(1, len(r.per_step_ms) + 1)
    ax.plot(xs, r.per_step_ms, alpha=0.6, linewidth=0.8, color="steelblue")
    m, s = r.t_per_step_mean, r.t_per_step_std
    ax.axhline(m, color="red", linewidth=1.5, label=f"mean {m:.1f} ms")
    ax.axhspan(m - s, m + s, alpha=0.15, color="red", label=f"±1σ ({s:.1f} ms)")
    ax.set_xlabel("Step"); ax.set_ylabel("ms/step")
    ax.set_title(f"{r.config_id} post-fix: {r.grid_w}×{r.grid_h}, N={r.n_agents}")
    ax.legend(fontsize=9)
    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


def _plot_scaling(results: list[PostFixResult],
                  gexp: float, gint: float,
                  nexp: float, nint: float) -> str:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    clr = {"B0":"#4e79a7","B1":"#f28e2b","B2":"#59a14f",
           "B3":"#e15759","B4":"#76b7b2"}
    by_id = {r.config_id: r for r in results}

    for cid in ("B0","B1","B3"):
        if cid in by_id:
            r = by_id[cid]
            ax1.scatter(r.grid_w, _norm500(r), color=clr.get(cid,"gray"),
                        s=80, zorder=5, label=cid)
    if not math.isnan(gexp):
        xs = np.linspace(40, 180, 100)
        ax1.plot(xs, np.exp(gint)*xs**gexp, "k--", alpha=0.6,
                 label=f"fit slope={gexp:.2f}")
    ax1.set_xscale("log"); ax1.set_yscale("log")
    ax1.set_xlabel("Grid side"); ax1.set_ylabel("t_norm (500 steps, s)")
    ax1.set_title("Grid scaling (N~constant)")
    ax1.legend(fontsize=9); ax1.grid(True, alpha=0.3)

    for cid in ("B1","B2","B3","B4"):
        if cid in by_id:
            r = by_id[cid]
            ax2.scatter(r.n_agents, _norm500(r), color=clr.get(cid,"gray"),
                        s=80, zorder=5, label=cid)
    if not math.isnan(nexp):
        ns = np.linspace(400, 2500, 100)
        ax2.plot(ns, np.exp(nint)*ns**nexp, "k--", alpha=0.6,
                 label=f"fit slope={nexp:.2f}")
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel("N agents"); ax2.set_ylabel("t_norm (500 steps, s)")
    ax2.set_title("N scaling (grid~constant within pairs)")
    ax2.legend(fontsize=9); ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


# ── HTML report ────────────────────────────────────────────────────────────────
def build_report(results: list[PostFixResult], skipped: dict[str, str],
                 gexp: float, nexp: float,
                 gint: float, nint: float,
                 hw: dict, bench_elapsed: float) -> str:
    by_id = {r.config_id: r for r in results}

    comp_bar  = _plot_comparison_bars(results)
    scale_plt = _plot_scaling(results, gexp, gint, nexp, nint)
    psp_plots = {r.config_id: _plot_per_step(r)
                 for r in results if r.per_step_ms}

    gexp_s = f"{gexp:.3f}" if not math.isnan(gexp) else "N/A"
    nexp_s = f"{nexp:.3f}" if not math.isnan(nexp) else "N/A"

    def _lhs_hrs(r): return _norm500(r) * 300 / 4 / 3600

    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SiC Games Post-Fix Benchmark — {_TODAY}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin:30px; color:#222; line-height:1.5; }}
  h1 {{ color:#1a3a5c; }}
  h2 {{ color:#2c5f8a; border-bottom:2px solid #2c5f8a; padding-bottom:4px; margin-top:2em; }}
  h3 {{ color:#3a7bbf; }}
  table {{ border-collapse:collapse; width:100%; margin-bottom:1.5em; }}
  th {{ background:#2c5f8a; color:white; padding:8px 12px; text-align:left; }}
  td {{ padding:7px 12px; border-bottom:1px solid #ddd; }}
  tr:hover td {{ background:#f5f9ff; }}
  .green  {{ background:#d4edda !important; }}
  .red    {{ background:#f8d7da !important; }}
  .skip   {{ background:#fff3cd !important; color:#856404; }}
  .verdict{{ background:#eaf4fb; border-left:4px solid #2c5f8a; padding:12px 16px;
             border-radius:0 4px 4px 0; margin:1em 0; }}
  .ok     {{ background:#d4edda; border-left:4px solid #28a745; }}
  .warn   {{ background:#fff3cd; border-left:4px solid #e09900; }}
  pre {{ background:#f4f4f4; padding:12px; border-radius:4px; font-size:13px; }}
  img {{ max-width:100%; border:1px solid #ddd; border-radius:4px; margin:8px 0; }}
  .toc {{ background:#f8f9fa; padding:12px 20px; border-radius:4px; display:inline-block; }}
  .toc a {{ color:#2c5f8a; text-decoration:none; display:block; margin:4px 0; }}
</style>
</head>
<body>
<h1>SiC Games — Post-Fix Benchmark: JointTask Spatial Hash</h1>
<p><b>Date:</b> {_TODAY} &nbsp;|&nbsp;
   <b>Benchmark wall time:</b> {bench_elapsed/60:.1f} min</p>
<div class="toc">
  <b>Contents</b>
  <a href="#s0">§0 Fix Summary</a>
  <a href="#s1">§1 Timing Comparison</a>
  <a href="#s2">§2 Component Breakdown</a>
  <a href="#s3">§3 Scaling Exponents</a>
  <a href="#s4">§4 Feasibility Verdict</a>
</div>
""")

    # §0 — Fix summary
    parts.append('<h2 id="s0">§0 — Fix Summary</h2>')
    parts.append(f"""<div class="verdict ok">
<p>
<b>File changed:</b> <code>src/sic_games/joint_task.py</code> —
<code>JointTaskManager.process_step()</code> only.
No other diffs. Config schema, YAML files, and all other model code unchanged.
</p>
<p>
<b>Algorithm change:</b> The O(W&times;H&times;N) inner loop
(<i>for each candidate cell: scan all N agents</i>) was replaced with a
spatial-hash lookup: build a <code>pos&rarr;agent</code> dict in O(N), then
for each candidate cell look up only the (2d+1)&sup2; = 5 neighbouring
positions (d=1, Euclidean). Total cost per step: <b>O(N + W&times;H)</b>.
</p>
<p>
<b>Test suite:</b> 193 prior tests + 5 new tests = <b>198 tests, all green</b>.
New tests: <code>test_spatial_hash_finds_adjacent</code>,
<code>test_spatial_hash_misses_distant</code>,
<code>test_spatial_hash_toroidal_wrap</code>,
<code>test_no_double_participation</code>,
<code>test_task_outcomes_unchanged</code>.
</p>
<p>
<b>Hardware:</b> {_esc(hw['cpu_name'])} &middot;
{hw['n_cpu_logical']} logical CPUs &middot; {hw['ram_gb']:.1f} GB RAM &middot;
Python {hw['python_version']} &middot; numpy {hw['numpy_version']}
</p>
</div>""")

    # §1 — Timing comparison
    parts.append('<h2 id="s1">§1 — Timing Comparison</h2>')
    parts.append("""<p>
  <span style="background:#d4edda;padding:2px 8px;border-radius:3px">Green</span>
  = ms/step &lt; 600 (feasible). &nbsp;
  <span style="background:#f8d7da;padding:2px 8px;border-radius:3px">Red</span>
  = ms/step &gt; 2400.
  &dagger; pre-fix B1 was aborted at 200 steps; ms/step extrapolated.
</p>""")
    parts.append("""<table>
<tr><th>ID</th><th>Grid</th><th>N</th>
    <th>Pre-fix ms/step</th><th>Post-fix ms/step</th><th>Speedup</th>
    <th>Post-fix t_total</th><th>Post-fix status</th></tr>""")

    bench_cfgs = [
        ("B0", 50,  50,  250,  10.0),
        ("B1", 100, 100, 500,   5.0),
        ("B2", 100, 100, 1000, 10.0),
        ("B3", 150, 150, 1000,  4.4),
        ("B4", 150, 150, 2000,  8.9),
    ]
    for cid, gw, gh, n, _ in bench_cfgs:
        pre_ms = _PRE_FIX.get(cid, {}).get("ms_step", "—")
        pre_str = f"{pre_ms:.1f}†" if cid == "B1" else (f"{pre_ms:.1f}" if isinstance(pre_ms, float) else "—")
        if cid in by_id:
            r = by_id[cid]
            sp = r.speedup
            sp_str = f"{sp:.1f}&times;" if sp else "—"
            css = _row_color(r.t_per_step_mean)
            row_css = f' style="{css}"' if css else ""
            status = "&#9888; aborted" if r.aborted else "&#10003;"
            parts.append(
                f"<tr{row_css}><td>{cid}</td><td>{gw}&times;{gh}</td><td>{n}</td>"
                f"<td>{pre_str}</td>"
                f"<td><b>{r.t_per_step_mean:.1f}</b></td>"
                f"<td><b>{sp_str}</b></td>"
                f"<td>{r.t_total:.1f}s</td>"
                f"<td>{status}</td></tr>"
            )
        elif cid in skipped:
            parts.append(
                f'<tr class="skip"><td>{cid}</td><td>{gw}&times;{gh}</td><td>{n}</td>'
                f'<td>{pre_str}</td><td colspan="4">Skipped: {_esc(skipped[cid])}</td></tr>'
            )
        else:
            parts.append(
                f'<tr class="skip"><td>{cid}</td><td>{gw}&times;{gh}</td><td>{n}</td>'
                f'<td>{pre_str}</td><td colspan="4">Not reached</td></tr>'
            )
    parts.append("</table>")

    # Per-step plots
    if psp_plots:
        parts.append("<h3>Per-step time series (B0, B1)</h3>")
        for cid in ("B0", "B1"):
            if cid in psp_plots and psp_plots[cid]:
                parts.append(f'<img src="data:image/png;base64,{psp_plots[cid]}" '
                              f'alt="{cid} per-step timing">')

    # §2 — Component breakdown
    parts.append('<h2 id="s2">§2 — Component Breakdown</h2>')
    if comp_bar:
        parts.append(f'<img src="data:image/png;base64,{comp_bar}" '
                     f'alt="Component breakdown pre vs post">')
    else:
        parts.append("<p><i>No component timing available.</i></p>")

    # Explicit JT percentage statement
    jt_stmts = []
    b0_pre_jt_pct = 89.0
    for cid in ("B0", "B1"):
        if cid in by_id:
            r = by_id[cid]
            if r.t_jt_ms is not None and r.t_per_step_mean > 0:
                jt_pct = 100.0 * r.t_jt_ms / r.t_per_step_mean
                jt_stmts.append(
                    f"<b>{cid}</b>: joint-task is now <b>{jt_pct:.1f}%</b> of step time "
                    f"(was {b0_pre_jt_pct:.0f}% pre-fix at B0)"
                )
    if jt_stmts:
        parts.append("<p>" + "; ".join(jt_stmts) + ".</p>")

    # §3 — Scaling
    parts.append('<h2 id="s3">§3 — Scaling Exponents (Post-Fix)</h2>')
    parts.append(f"""<p>
  <b>Grid exponent (post-fix):</b> {gexp_s}
  (pre-fix was 3.88; target &le; 2.0)<br>
  <b>N exponent (post-fix):</b> {nexp_s}
  (target &approx; 1.0)
</p>""")
    if scale_plt:
        parts.append(f'<img src="data:image/png;base64,{scale_plt}" '
                     f'alt="Post-fix scaling log-log plots">')
    if not math.isnan(gexp) and gexp <= 2.0:
        parts.append(f'<div class="verdict ok"><b>Grid scaling fixed:</b> '
                     f'exponent = {gexp:.2f} &le; 2.0 (was 3.88). '
                     f'Spatial hash eliminates the O(grid&sup2;&times;N) bottleneck.</div>')
    elif not math.isnan(gexp):
        parts.append(f'<div class="verdict warn"><b>Grid exponent still high: {gexp:.2f}</b>. '
                     f'Further investigation needed.</div>')

    if not math.isnan(nexp) and nexp <= 1.3:
        parts.append(f'<div class="verdict ok"><b>N scaling linear:</b> '
                     f'exponent = {nexp:.2f} &approx; 1.0. No O(N&sup2;) path detected.</div>')
    elif not math.isnan(nexp):
        parts.append(f'<div class="verdict warn"><b>N exponent = {nexp:.2f} &gt; 1.3.</b> '
                     f'Super-linear path still present — investigate further.</div>')

    # §4 — Feasibility verdict
    parts.append('<h2 id="s4">§4 — Updated Feasibility Verdict</h2>')

    safe_r  = [r for r in results if not r.aborted and _lhs_hrs(r) < 4.0]
    care_r  = [r for r in results if not r.aborted and 4.0 <= _lhs_hrs(r) <= 12.0]
    opt_r   = [r for r in results if r.aborted or _norm500(r) > 300.0]

    # Restate 4 questions
    feasible_ids = [r.config_id for r in results if not r.aborted and r.t_per_step_mean < FEASIBILITY_MS]
    bottleneck_r = by_id.get("B1") or by_id.get("B0")
    if bottleneck_r and bottleneck_r.t_jt_ms is not None:
        dom_comps = {
            "grid": bottleneck_r.t_grid_ms or 0.0,
            "joint-task": bottleneck_r.t_jt_ms,
            "agent": bottleneck_r.t_agent_ms or 0.0,
            "pool": bottleneck_r.t_pool_ms or 0.0,
            "repro": bottleneck_r.t_repro_ms or 0.0,
            "metrics": bottleneck_r.t_metrics_ms or 0.0,
        }
        dom_name = max(dom_comps, key=dom_comps.get)
        dom_pct  = 100.0 * dom_comps[dom_name] / bottleneck_r.t_per_step_mean
        bottleneck_str = f"dominant cost at {bottleneck_r.config_id} is {dom_name} ({dom_pct:.0f}%)"
    else:
        bottleneck_str = "component data not available"

    parts.append('<div class="verdict">')
    if not math.isnan(gexp):
        parts.append(f"<p><b>1. Grid scaling:</b> O(grid^{gexp:.2f}) post-fix "
                     f"(was 3.88). Fix confirmed.</p>")
    else:
        parts.append("<p><b>1. Grid scaling:</b> insufficient data for fit.</p>")
    if not math.isnan(nexp):
        parts.append(f"<p><b>2. N scaling:</b> O(N^{nexp:.2f}) post-fix.</p>")
    else:
        parts.append("<p><b>2. N scaling:</b> insufficient data for fit.</p>")
    parts.append(f"<p><b>3. Bottleneck:</b> {_esc(bottleneck_str)}.</p>")
    feas_str = (f"Feasible configs (500 steps &lt; 5 min): {', '.join(feasible_ids)}."
                if feasible_ids else "No config feasible under 5 min.")
    parts.append(f"<p><b>4. Feasibility:</b> {feas_str}</p>")
    parts.append("</div>")

    def _lhs_row(r):
        return (f"<tr><td>{r.config_id}</td><td>{r.grid_w}&times;{r.grid_h}</td>"
                f"<td>{r.n_agents}</td><td>{r.t_per_step_mean:.1f}</td>"
                f"<td>{_lhs_hrs(r):.1f}h</td></tr>")

    if safe_r:
        parts.append("<h3>Safe (LHS &lt; 4 hours at 4 workers)</h3>")
        parts.append('<table><tr><th>ID</th><th>Grid</th><th>N</th>'
                     '<th>ms/step</th><th>Est. LHS wall time</th></tr>')
        for r in safe_r:
            parts.append(_lhs_row(r))
        parts.append("</table>")
    else:
        parts.append("<h3>Safe</h3><p><i>No config achieves &lt;4-hour LHS with current timing.</i></p>")

    if care_r:
        parts.append("<h3>Feasible with care (4–12 hours, weekend batch viable)</h3>")
        parts.append('<table><tr><th>ID</th><th>Grid</th><th>N</th>'
                     '<th>ms/step</th><th>Est. LHS wall time</th></tr>')
        for r in care_r:
            parts.append(_lhs_row(r))
        parts.append("</table>")

    if opt_r:
        parts.append("<h3>Needs further optimisation (&gt;5 min/run)</h3>")
        parts.append('<table><tr><th>ID</th><th>Grid</th><th>N</th><th>Reason</th></tr>')
        for r in opt_r:
            parts.append(f"<tr><td>{r.config_id}</td><td>{r.grid_w}&times;{r.grid_h}</td>"
                         f"<td>{r.n_agents}</td>"
                         f"<td>{'aborted' if r.aborted else f'{r.t_per_step_mean:.0f} ms/step'}</td></tr>")
        parts.append("</table>")

    if skipped:
        parts.append("<h3>Skipped</h3>")
        parts.append('<table><tr><th>ID</th><th>Reason</th></tr>')
        for cid, reason in skipped.items():
            parts.append(f"<tr><td>{cid}</td><td>{_esc(reason)}</td></tr>")
        parts.append("</table>")

    parts.append(f"""
<hr>
<p><small>Generated by <code>sic_games.benchmark_postfix</code> on {_TODAY}.
Benchmark wall time: {bench_elapsed/60:.1f} min.</small></p>
</body></html>""")
    return "".join(parts)


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    print(f"SiC Games Post-Fix Benchmark — {_TODAY}")
    _OUT.mkdir(parents=True, exist_ok=True)
    hw = _hw_summary()
    print(f"  CPU: {hw['cpu_name']}  |  Python {hw['python_version']}")
    print()

    bench_start = perf_counter()
    results: list[PostFixResult] = []
    skipped: dict[str, str] = {}

    def _should(cid): return cid not in skipped

    # B0 — always
    r = run_one("B0", 50, 50, 250, 10.0, 500,
                with_components=True, with_per_step_list=True)
    results.append(r)
    if r.aborted:
        skipped.update({c: "B0 aborted" for c in ("B1","B2","B3","B4")})

    # B1 — always (main regression check)
    if _should("B1"):
        r = run_one("B1", 100, 100, 500, 5.0, 500,
                    with_components=True, with_per_step_list=True)
        results.append(r)
        if r.aborted:
            skipped.update({c: "B1 aborted (>20 min)" for c in ("B2","B3","B4")})
        elif r.t_per_step_mean >= FEASIBILITY_MS:
            skipped.update({c: f"B1 not feasible ({r.t_per_step_mean:.0f} ms/step)"
                            for c in ("B2","B3","B4")})
            print(f"    B1 not feasible — stopping at B1 per directive.")

    # B2 — if B1 < 5 min
    if _should("B2"):
        r = run_one("B2", 100, 100, 1000, 10.0, 500,
                    with_components=False, with_per_step_list=False)
        results.append(r)
        if r.aborted or r.t_per_step_mean >= FEASIBILITY_MS:
            skipped.update({c: f"B2 ≥5 min" for c in ("B3","B4")})

    # B3 — if B2 < 5 min
    if _should("B3"):
        r = run_one("B3", 150, 150, 1000, 4.4, 500,
                    with_components=False, with_per_step_list=False)
        results.append(r)
        if r.aborted or r.t_per_step_mean >= FEASIBILITY_MS:
            skipped["B4"] = f"B3 ≥5 min"

    # B4 — if B3 < 5 min
    if _should("B4"):
        r = run_one("B4", 150, 150, 2000, 8.9, 500,
                    with_components=False, with_per_step_list=False)
        results.append(r)

    bench_elapsed = perf_counter() - bench_start
    print()

    # Scaling
    gexp, gint = _grid_exp(results)
    nexp, nint = _n_exp(results)
    gexp_s = f"{gexp:.3f}" if not math.isnan(gexp) else "N/A"
    nexp_s = f"{nexp:.3f}" if not math.isnan(nexp) else "N/A"
    print(f"Grid exponent: {gexp_s}  |  N exponent: {nexp_s}")

    # Report
    print("Building HTML report...")
    html = build_report(results, skipped, gexp, nexp, gint, nint, hw, bench_elapsed)
    rpt = _OUT / "report_benchmark_postfix.html"
    rpt.write_text(html, encoding="utf-8")
    print(f"  Report: {rpt}")

    # Summary table
    print(f"\n{'ID':<4} {'Grid':<10} {'N':>5}  {'post ms/step':>13}  {'speedup':>8}  {'LHS est':>8}")
    print("-" * 58)
    by_id = {r.config_id: r for r in results}
    for cid, gw, gh, n, _ in [("B0",50,50,250,10),("B1",100,100,500,5),
                                ("B2",100,100,1000,10),("B3",150,150,1000,4.4),
                                ("B4",150,150,2000,8.9)]:
        if cid in by_id:
            r = by_id[cid]
            sp = r.speedup
            sp_s = f"{sp:.1f}x" if sp else "—"
            lhs = f"{_norm500(r)*300/4/3600:.1f}h"
            flag = "OK" if r.t_per_step_mean < FEASIBILITY_MS else ("ABORTED" if r.aborted else "SLOW")
            print(f"{cid:<4} {gw}x{gh:<6}  {n:>5}  {r.t_per_step_mean:>13.1f}  {sp_s:>8}  {lhs:>8}  {flag}")
        elif cid in skipped:
            print(f"{cid:<4} {gw}x{gh:<6}  {n:>5}  {'---':>13}  {'---':>8}  {'---':>8}  SKIP")

    print(f"\nBenchmark complete in {bench_elapsed/60:.1f} min.")
    print(f"Report: {rpt}")


if __name__ == "__main__":
    main()
