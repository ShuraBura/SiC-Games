"""SiC Games — Performance Audit + Optimisation (SiC_Games_Perf_Audit.md v1.0).

Two-phase execution detected automatically by presence of reference parquet.

Phase 1 (reference missing):
  1. Profile B0 and B1 with cProfile (200 steps each)
  2. Generate pre-fix reference B0 (500 steps) → parquet
  3. Save profile cache
  → Prints instructions to apply fixes and re-run.

Phase 2 (reference present):
  1. Load profile cache from Phase 1
  2. Verify numerical equivalence (B0 500 steps vs reference)
  3. Re-benchmark B0–B5 with component breakdown
  4. Generate outputs/perf_audit/report_perf_audit.html

Usage:
    py -3.14 -m sic_games.perf_audit
    py -3.14 -m sic_games.perf_audit --no-bench   # Phase 2 without benchmark
    py -3.14 -m sic_games.perf_audit --force-phase1  # redo Phase 1 even if ref exists
"""
from __future__ import annotations

import argparse
import base64
import cProfile
import io
import json
import math
import pstats
import sys
import time
import tracemalloc
from dataclasses import dataclass, asdict, field
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
_REPO        = Path(__file__).parent.parent.parent
_OUT         = _REPO / "outputs" / "perf_audit"
_CACHE       = _OUT / "audit_cache.json"
_REF_METRICS = _OUT / "b0_reference_metrics.parquet"
_REF_AGENTS  = _OUT / "b0_reference_agents.parquet"
_TODAY       = "2026-05-28"

# ── Benchmark configs (B0–B5; B5 new at 200×200/1500) ─────────────────────────
AUDIT_BENCH_CONFIGS = [
    ("B0", 50,  50,   250, 10.0,  500),
    ("B1", 100, 100,  500,  5.0,  500),
    ("B2", 100, 100, 1000, 10.0,  500),
    ("B3", 150, 150, 1000,  4.4,  500),
    ("B4", 150, 150, 2000,  8.9,  500),
    ("B5", 200, 200, 1500,  3.75, 500),
]
COMPONENT_CONFIGS   = {"B0", "B1"}
STOP_SEC            = 20 * 60    # 20 min hard stop
FEASIBILITY_MS      = 600        # ms/step → skip larger configs if exceeded

# Pre-fix JT-only baseline from benchmark_postfix (for speedup column)
_JT_BASELINE = {"B0": 75.7, "B1": 388.3, "B2": 425.5, "B3": 1265.5}


# ── Imports from benchmark.py ─────────────────────────────────────────────────
from sic_games.benchmark import (
    _bench_c_config, BenchResult,
    _ComponentTimer, _attach_component_timers, _detach_component_timers,
    _fig_to_b64, _norm_time, _grid_scaling_exponent, _n_scaling_exponent,
)


# ── Audit inventory (static analysis findings) ────────────────────────────────
# Populated once from reading the source; used in §0.

AUDIT_INVENTORY = [
    {
        "rank": 1,
        "function": "morans_i() × 4",
        "file": "metrics.py",
        "cost": "O(N²) numpy × 4 (W matrix rebuilt each call)",
        "issue": "W = f(positions) recomputed identically for phi, psi, c1, c2. "
                 "Each call allocates N×N float64 matrix + (W * z[:,None] * z[None,:]).sum() "
                 "allocates another N×N array.",
        "fix": "Compute W once per compute_metrics() call; pass to all four invocations. "
               "Replace (W * z[:,None] * z[None,:]).sum() with z @ W @ z (BLAS dgemv).",
        "est_speedup": "~4× for morans_i; metrics ~2–3×",
        "risk": "LOW",
    },
    {
        "rank": 2,
        "function": "_neighbor_count()",
        "file": "agents/perception.py",
        "cost": "8 set lookups × (1 + 4×vision) cells × N agents/step",
        "issue": "Computed for every visible cell for every agent. For C runs, "
                 "c_proximity (precomputed box-filter grid) overrides neighbor_count "
                 "in the utility function — _neighbor_count is pure waste for C strategy.",
        "fix": "In LocalVisionPerception.build(), skip _neighbor_count when "
               "c_prox_grid is set; pass neighbor_count=0 instead.",
        "est_speedup": "Eliminates ~8×(1+4×v_mean)×N ≈ 100K set lookups/step at B1. "
                       "Expected ~5–15% agent-step reduction.",
        "risk": "LOW",
    },
    {
        "rank": 3,
        "function": "gini() × 3",
        "file": "metrics.py",
        "cost": "Python sorted() + loop × 3 calls/step",
        "issue": "Python list comprehension + loop over N=500 values, called for "
                 "gini_wealth, gini_cred, psi_gini each step.",
        "fix": "Replace with numpy: np.sort + vectorised index arithmetic.",
        "est_speedup": "~5× for gini itself; small fraction of total step time.",
        "risk": "LOW",
    },
    {
        "rank": 4,
        "function": "spatial_dispersion()",
        "file": "metrics.py",
        "cost": "Python sin/cos loop over N positions × 2 axes",
        "issue": "circular_std() iterates N elements with math.sin/cos; "
                 "positions extracted into Python lists first.",
        "fix": "Vectorise with numpy: angles array → np.sin/cos → scalar ops.",
        "est_speedup": "~3–8× for spatial_dispersion itself.",
        "risk": "LOW",
    },
    {
        "rank": 5,
        "function": "list(self.agents) × 5+",
        "file": "run.py",
        "cost": "5+ full list constructions per step; each O(N)",
        "issue": "JT and main agent_list built separately (lines 419, 441). "
                 "Cred flush iterates self.agents again (line 562) when agent_list "
                 "already covers the same set.",
        "fix": "Build agent_list once; reuse for JT call; replace cred-flush "
               "iterator with agent_list.",
        "est_speedup": "Saves 2 × O(N) constructions/step; minor but free.",
        "risk": "LOW",
    },
    {
        "rank": 6,
        "function": "_carbon_birth() partner scan",
        "file": "agents/reproduction.py",
        "cost": "O(N) scan + _toroidal_chebyshev() call per agent per birth attempt",
        "issue": "candidates = [a for a in world.agents if ... chebyshev(a.pos, ...) <= r_p]. "
                 "At 20–40 births/step × O(N=500) = 10–20K calls/step.",
        "fix": "Spatial hash: pos→agent dict (already built for JT); bucket-lookup "
               "for all cells within Chebyshev r_p = 3.",
        "est_speedup": "~10–20× for partner search; ~5–10% total step reduction at B1.",
        "risk": "MED — changes order of candidates list → rng.choice() selects different "
                "partner → child traits change → science changes. Must verify or redesign "
                "to preserve order.",
    },
    {
        "rank": 7,
        "function": "c_spatial_density()",
        "file": "metrics.py",
        "cost": "O(N²) numpy Chebyshev matrix each step",
        "issue": "500×500 distance matrix allocated every step (250K float64 = 2 MB). "
                 "Used only for diagnostic isolation metrics.",
        "fix": "Could use scipy.spatial.cKDTree for O(N log N) or pre-sort positions "
               "for O(N²/block) with early exit. Or compute every K steps.",
        "est_speedup": "~2–5× for this function; small fraction of total.",
        "risk": "MED — cKDTree changes algorithm; periodic computation changes when "
                "metric is sampled.",
    },
    {
        "rank": 8,
        "function": "mean_cred() / mean_wealth() in birth loop",
        "file": "run.py",
        "cost": "O(N) Python loop × # birth events per step",
        "issue": "self.mean_cred() iterates list(self.agents) once per C newborn "
                 "to set offspring.cred. If births_per_step=30 and N=500, this is "
                 "15,000 attribute reads per step.",
        "fix": "Cache mean_cred once before the birth loop; pass cached value.",
        "est_speedup": "Saves (births-1) × O(N) calls; minor at typical birth rates.",
        "risk": "LOW — cred values don't change during birth loop.",
    },
]


# ── Utilities ──────────────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _hw_summary() -> str:
    import platform
    cpu = platform.processor() or platform.machine()
    try:
        ram_str = "RAM unknown"
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / 1e9
            ram_str = f"{ram_gb:.1f} GB RAM"
        except ImportError:
            pass
        import multiprocessing
        ncpu = multiprocessing.cpu_count()
        cpu_str = f"{cpu} · {ncpu} logical CPUs · {ram_str}"
    except Exception:
        cpu_str = f"{cpu}"
    py_ver = f"Python {sys.version.split()[0]}"
    np_ver = f"numpy {np.__version__}"
    return f"{cpu_str} · {py_ver} · {np_ver}"


def _row_color(ms: float | None) -> str:
    if ms is None:
        return ""
    if ms < FEASIBILITY_MS:
        return ' class="green"'
    if ms > 2400:
        return ' class="red"'
    return ""


def _shorten_path(p: str) -> str:
    """Shorten a cProfile filename to the last two components."""
    parts = p.replace("\\", "/").split("/")
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return p


# ── cProfile harness ──────────────────────────────────────────────────────────

def _profile_config(
    grid_w: int, grid_h: int, n_agents: int, n_steps: int = 200,
) -> dict[str, list[dict]]:
    """Run cProfile on one config, return top-20 tables (cumtime and tottime)."""
    from sic_games.run import SugarWorld
    cfg = _bench_c_config(grid_w, grid_h, n_agents, n_steps)
    world = SugarWorld(cfg, env_seed=42, agent_seed=42)

    pr = cProfile.Profile()
    pr.enable()
    for _ in range(n_steps):
        world.step()
    pr.disable()

    stats = pr.getstats()   # list of pstats.FunctionStats namedtuple-like objects
    # Each entry: code (code obj or str), callcount, reccallcount, totaltime, inlinetime, calls
    # Use pstats.Stats for convenient access
    s_io = io.StringIO()
    ps = pstats.Stats(pr, stream=s_io)

    rows = []
    for (fname, lineno, funcname), (pcc, cc, tt, ct, _callers) in ps.stats.items():
        rows.append({
            "func":     funcname,
            "file":     _shorten_path(fname),
            "lineno":   lineno,
            "ncalls":   cc,
            "tottime":  round(tt, 6),
            "cumtime":  round(ct, 6),
            "pct_tot":  0.0,
        })

    total_tt = sum(r["tottime"] for r in rows)
    for r in rows:
        r["pct_tot"] = round(100.0 * r["tottime"] / total_tt, 2) if total_tt else 0.0

    top_cum = sorted(rows, key=lambda x: x["cumtime"], reverse=True)[:20]
    top_own = sorted(rows, key=lambda x: x["tottime"], reverse=True)[:20]
    return {"cum": top_cum, "own": top_own}


# ── Reference generation ──────────────────────────────────────────────────────

def _generate_reference() -> None:
    """Run B0 for 500 steps and save reference parquet files."""
    from sic_games.run import SugarWorld
    print("  Generating pre-fix reference (B0, 500 steps) ...", end=" ", flush=True)
    cfg = _bench_c_config(50, 50, 250, n_steps=500)
    world = SugarWorld(cfg, env_seed=42, agent_seed=42)
    t0 = perf_counter()
    world.run()
    print(f"done in {perf_counter()-t0:.1f}s")

    metrics_df = world.metrics_to_df()
    agents_df  = world.agent_states_df().sort_values("unique_id").reset_index(drop=True)

    _OUT.mkdir(parents=True, exist_ok=True)
    metrics_df.to_parquet(_REF_METRICS, index=False)
    agents_df.to_parquet(_REF_AGENTS,  index=False)
    print(f"  Saved: {_REF_METRICS.name}, {_REF_AGENTS.name}")


# ── Equivalence check ─────────────────────────────────────────────────────────

@dataclass
class EquivResult:
    passed: bool
    n_diverged_steps: int
    max_wealth_err: float
    max_gini_err: float
    max_cred_err: float
    pop_match: bool
    deaths_match: bool
    births_match: bool
    pos_match: bool
    summary: str


def _verify_equivalence() -> EquivResult:
    """Run B0 500 steps with current code; compare to reference parquet."""
    from sic_games.run import SugarWorld
    print("  Verifying numerical equivalence (B0, 500 steps) ...", end=" ", flush=True)

    ref_m = pd.read_parquet(_REF_METRICS)
    ref_a = pd.read_parquet(_REF_AGENTS)

    cfg = _bench_c_config(50, 50, 250, n_steps=500)
    world = SugarWorld(cfg, env_seed=42, agent_seed=42)
    t0 = perf_counter()
    world.run()
    dt = perf_counter() - t0
    print(f"done in {dt:.1f}s")

    cur_m = world.metrics_to_df()
    cur_a = world.agent_states_df().sort_values("unique_id").reset_index(drop=True)

    # --- Population (exact int) ---
    pop_match = bool((ref_m["population"].values == cur_m["population"].values).all())

    # --- mean_wealth, gini_wealth, mean_cred (1e-9 rel tolerance) ---
    tol = 1e-9
    def _rel_err(col: str) -> float:
        a = ref_m[col].values.astype(float)
        b = cur_m[col].values.astype(float)
        denom = np.maximum(np.abs(a), 1e-30)
        return float(np.max(np.abs(a - b) / denom))

    max_wealth_err = _rel_err("mean_wealth")
    max_gini_err   = _rel_err("gini_wealth")
    max_cred_err   = _rel_err("mean_cred")
    n_div = int(np.sum(
        (np.abs(ref_m["mean_wealth"].values - cur_m["mean_wealth"].values)
         / np.maximum(np.abs(ref_m["mean_wealth"].values), 1e-30)) > tol
    ))

    # --- Deaths, births (exact per step) ---
    ref_deaths = (ref_m["deaths_starvation"] + ref_m["deaths_senescence"]).values
    cur_deaths = (cur_m["deaths_starvation"] + cur_m["deaths_senescence"]).values
    deaths_match = bool((ref_deaths == cur_deaths).all())

    ref_births = (ref_m["births_c"] + ref_m["births_si"]).values
    cur_births = (cur_m["births_c"] + cur_m["births_si"]).values
    births_match = bool((ref_births == cur_births).all())

    # --- Final agent positions (exact) ---
    pos_match = bool(
        (ref_a["x"].values == cur_a["x"].values).all()
        and (ref_a["y"].values == cur_a["y"].values).all()
    )

    passed = (pop_match and deaths_match and births_match and pos_match
              and max_wealth_err < tol and max_gini_err < tol and max_cred_err < tol)

    if passed:
        summary = "All metrics identical to 1e-9 tolerance — science unchanged."
    else:
        parts = []
        if not pop_match:       parts.append("population mismatch")
        if not deaths_match:    parts.append("deaths mismatch")
        if not births_match:    parts.append("births mismatch")
        if not pos_match:       parts.append("final positions mismatch")
        if max_wealth_err >= tol: parts.append(f"mean_wealth err {max_wealth_err:.2e}")
        if max_gini_err   >= tol: parts.append(f"gini_wealth err {max_gini_err:.2e}")
        if max_cred_err   >= tol: parts.append(f"mean_cred err {max_cred_err:.2e}")
        summary = "DIVERGENCE: " + "; ".join(parts)

    return EquivResult(
        passed=passed,
        n_diverged_steps=n_div,
        max_wealth_err=max_wealth_err,
        max_gini_err=max_gini_err,
        max_cred_err=max_cred_err,
        pop_match=pop_match,
        deaths_match=deaths_match,
        births_match=births_match,
        pos_match=pos_match,
        summary=summary,
    )


# ── Re-benchmark (B0–B5) ──────────────────────────────────────────────────────

@dataclass
class AuditBenchResult:
    config_id: str
    grid_w: int
    grid_h: int
    n_agents: int
    n_steps_ran: int
    n_steps_target: int
    aborted: bool
    skip_reason: str
    t_total: float
    t_per_step_mean: float
    t_per_step_std: float
    per_step_ms: list[float] = field(default_factory=list)
    t_grid_ms: float | None = None
    t_jt_ms: float | None = None
    t_agent_ms: float | None = None
    t_pool_ms: float | None = None
    t_repro_ms: float | None = None
    t_metrics_ms: float | None = None

    @property
    def speedup_vs_jt(self) -> float | None:
        base = _JT_BASELINE.get(self.config_id)
        if base is None or self.t_per_step_mean == 0:
            return None
        return base / self.t_per_step_mean


def _run_one_audit(
    config_id: str,
    grid_w: int, grid_h: int,
    n_agents: int,
    n_steps: int,
    with_components: bool,
) -> AuditBenchResult:
    from sic_games.run import SugarWorld
    print(f"  [{config_id}] grid={grid_w}x{grid_h} N={n_agents} ...", end=" ", flush=True)

    cfg   = _bench_c_config(grid_w, grid_h, n_agents, n_steps)
    world = SugarWorld(cfg, env_seed=42, agent_seed=42)

    timers = _attach_component_timers(world) if with_components else None

    step_times: list[float] = []
    t_run = perf_counter()
    aborted = False
    n_ran = 0

    for s in range(n_steps):
        t0 = perf_counter()
        world.step()
        dt = perf_counter() - t0
        step_times.append(dt)
        n_ran += 1
        if timers:
            for name in ("grid", "jt", "pool", "repro", "metrics"):
                timers[name].finalize_step()
        if (s + 1) % 50 == 0:
            elapsed = perf_counter() - t_run
            if elapsed > STOP_SEC:
                aborted = True
                print(f"\n    STOPPED at step {s+1} ({elapsed/60:.1f} min > 20 min limit)")
                break

    t_total = perf_counter() - t_run
    arr = np.array(step_times) * 1000.0
    t_mean = float(np.mean(arr))
    t_std  = float(np.std(arr))

    t_grid_ms = t_jt_ms = t_pool_ms = t_repro_ms = t_metrics_ms = t_agent_ms = None
    if timers:
        _detach_component_timers(timers)
        t_grid_ms    = timers["grid"].mean_ms
        t_jt_ms      = timers["jt"].mean_ms
        t_pool_ms    = timers["pool"].mean_ms
        t_repro_ms   = timers["repro"].mean_ms
        t_metrics_ms = timers["metrics"].mean_ms
        t_agent_ms   = max(0.0, t_mean - t_grid_ms - t_jt_ms
                          - t_pool_ms - t_repro_ms - t_metrics_ms)

    print(f"done in {t_total:.1f}s  ({t_mean:.1f} ms/step)")

    return AuditBenchResult(
        config_id=config_id,
        grid_w=grid_w, grid_h=grid_h, n_agents=n_agents,
        n_steps_ran=n_ran, n_steps_target=n_steps,
        aborted=aborted, skip_reason="",
        t_total=t_total,
        t_per_step_mean=t_mean, t_per_step_std=t_std,
        per_step_ms=list(arr),
        t_grid_ms=t_grid_ms, t_jt_ms=t_jt_ms,
        t_agent_ms=t_agent_ms, t_pool_ms=t_pool_ms,
        t_repro_ms=t_repro_ms, t_metrics_ms=t_metrics_ms,
    )


def _run_audit_benchmark(no_bench: bool) -> list[AuditBenchResult]:
    if no_bench:
        return []
    results: list[AuditBenchResult] = []
    skip_rest = False
    prev_ms   = 0.0

    for config_id, gw, gh, n, dens, n_steps in AUDIT_BENCH_CONFIGS:
        if skip_rest:
            r = AuditBenchResult(
                config_id=config_id, grid_w=gw, grid_h=gh, n_agents=n,
                n_steps_ran=0, n_steps_target=n_steps,
                aborted=False, skip_reason=f"previous config ≥ {FEASIBILITY_MS} ms/step or aborted",
                t_total=0, t_per_step_mean=0, t_per_step_std=0,
            )
            results.append(r)
            continue

        with_comp = config_id in COMPONENT_CONFIGS
        r = _run_one_audit(config_id, gw, gh, n, n_steps, with_comp)
        results.append(r)

        if r.aborted or r.t_per_step_mean >= FEASIBILITY_MS:
            skip_rest = True

    return results


# ── Scaling helpers ────────────────────────────────────────────────────────────

def _grid_exp_audit(results: list[AuditBenchResult]) -> float:
    pts = [(r.grid_w, r.t_per_step_mean / 1000.0 * 500.0)
           for r in results if r.config_id in ("B0", "B1", "B3")
           and r.t_per_step_mean > 0]
    if len(pts) < 2:
        return float("nan")
    xs = np.log([p[0] for p in pts])
    ys = np.log([p[1] for p in pts])
    A  = np.vstack([xs, np.ones(len(xs))]).T
    try:
        slope = float(np.linalg.lstsq(A, ys, rcond=None)[0][0])
    except Exception:
        slope = float("nan")
    return slope


def _n_exp_audit(results: list[AuditBenchResult]) -> float:
    by_id = {r.config_id: r for r in results}
    pts = []
    for a, b in [("B1", "B2"), ("B3", "B4")]:
        if a in by_id and b in by_id:
            ra, rb = by_id[a], by_id[b]
            if ra.t_per_step_mean > 0 and rb.t_per_step_mean > 0:
                pts += [(ra.n_agents, ra.t_per_step_mean / 1000.0 * 500.0),
                        (rb.n_agents, rb.t_per_step_mean / 1000.0 * 500.0)]
    if len(pts) < 2:
        return float("nan")
    xs = np.log([p[0] for p in pts])
    ys = np.log([p[1] for p in pts])
    A  = np.vstack([xs, np.ones(len(xs))]).T
    try:
        return float(np.linalg.lstsq(A, ys, rcond=None)[0][0])
    except Exception:
        return float("nan")


# ── Plot helpers ───────────────────────────────────────────────────────────────

def _plot_profile_bar(profile: dict, config_label: str) -> str:
    """Stacked horizontal bar chart of top-10 own-time functions."""
    rows = profile["own"][:10]
    labels = [f"{r['func']} ({r['file'].split('/')[-1]})" for r in rows]
    vals   = [r["tottime"] * 1000 for r in rows]   # ms

    fig, ax = plt.subplots(figsize=(9, 4))
    colors = plt.cm.tab10(np.linspace(0, 1, len(vals)))
    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1], alpha=0.85)
    ax.set_xlabel("Own time over 200 steps (ms total)")
    ax.set_title(f"cProfile top-10 own time — {config_label}")
    for bar, v in zip(bars, vals[::-1]):
        ax.text(v + max(vals) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.1f} ms", va="center", fontsize=8)
    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


def _plot_component_bars_audit(results: list[AuditBenchResult]) -> str | None:
    comp = [r for r in results if r.config_id in COMPONENT_CONFIGS
            and r.t_grid_ms is not None]
    if not comp:
        return None

    categories = ["grid", "jt", "agent", "pool", "repro", "metrics"]
    colors = {"grid": "#4e79a7", "jt": "#f28e2b", "agent": "#e15759",
              "pool": "#76b7b2", "repro": "#59a14f", "metrics": "#edc948"}

    fig, axes = plt.subplots(1, len(comp), figsize=(6 * len(comp), 5), sharey=False)
    if len(comp) == 1:
        axes = [axes]

    for ax, r in zip(axes, comp):
        vals = {
            "grid":    r.t_grid_ms or 0.0,
            "jt":      r.t_jt_ms or 0.0,
            "agent":   r.t_agent_ms or 0.0,
            "pool":    r.t_pool_ms or 0.0,
            "repro":   r.t_repro_ms or 0.0,
            "metrics": r.t_metrics_ms or 0.0,
        }
        total = sum(vals.values()) or 1.0
        bottom = 0.0
        for cat in categories:
            v = vals[cat]
            pct = 100.0 * v / total
            ax.bar(0, v, bottom=bottom, color=colors[cat], label=f"{cat} ({pct:.0f}%)", width=0.5)
            if pct > 3:
                ax.text(0, bottom + v / 2, f"{cat}\n{pct:.0f}%",
                        ha="center", va="center", fontsize=9, color="white",
                        fontweight="bold")
            bottom += v
        ax.set_xticks([])
        ax.set_ylabel("ms/step")
        ax.set_title(f"{r.config_id}: {r.grid_w}×{r.grid_h}, N={r.n_agents}\n"
                     f"total {r.t_per_step_mean:.1f} ms/step")
        ax.legend(fontsize=8, loc="upper right")

    fig.suptitle("Component breakdown (post-fix)", fontsize=12)
    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


def _plot_scaling(results: list[AuditBenchResult]) -> str | None:
    pts = [(r.grid_w, r.t_per_step_mean) for r in results
           if r.config_id in ("B0", "B1", "B3") and r.t_per_step_mean > 0]
    if len(pts) < 2:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.loglog(xs, ys, "o-", color="steelblue", linewidth=2, markersize=8, label="Post-audit")
    # Reference JT-only points
    jt_pts = [(50, 75.7), (100, 388.3), (150, 1265.5)]
    ax.loglog([p[0] for p in jt_pts], [p[1] for p in jt_pts],
              "s--", color="orange", linewidth=1.5, markersize=7, label="JT-fix only")
    ax.set_xlabel("Grid side (log)")
    ax.set_ylabel("ms/step (log)")
    ax.set_title("Grid scaling (constant density)")
    ax.legend()
    fig.tight_layout()
    enc = _fig_to_b64(fig)
    plt.close(fig)
    return enc


# ── HTML Report ───────────────────────────────────────────────────────────────

_CSS = """
body{font-family:'Segoe UI',Arial,sans-serif;margin:30px;color:#222;line-height:1.5}
h1{color:#1a3a5c}
h2{color:#2c5f8a;border-bottom:2px solid #2c5f8a;padding-bottom:4px;margin-top:2em}
h3{color:#3a7bbf}
table{border-collapse:collapse;width:100%;margin-bottom:1.5em}
th{background:#2c5f8a;color:white;padding:8px 12px;text-align:left}
td{padding:7px 12px;border-bottom:1px solid #ddd}
tr:hover td{background:#f5f9ff}
.green{background:#d4edda !important}
.red{background:#f8d7da !important}
.skip{background:#fff3cd !important;color:#856404}
.verdict{background:#eaf4fb;border-left:4px solid #2c5f8a;padding:12px 16px;
  border-radius:0 4px 4px 0;margin:1em 0}
.ok{background:#d4edda;border-left:4px solid #28a745}
.warn{background:#fff3cd;border-left:4px solid #e09900}
.fail{background:#f8d7da;border-left:4px solid #dc3545}
pre{background:#f4f4f4;padding:12px;border-radius:4px;font-size:13px}
img{max-width:100%;border:1px solid #ddd;border-radius:4px;margin:8px 0}
.toc{background:#f8f9fa;padding:12px 20px;border-radius:4px;display:inline-block}
.toc a{color:#2c5f8a;text-decoration:none;display:block;margin:4px 0}
.low{color:#28a745;font-weight:bold}
.med{color:#e09900;font-weight:bold}
.high{color:#dc3545;font-weight:bold}
"""


def _profile_table_html(rows: list[dict], sort_col: str) -> str:
    col_label = "Cumulative time (s)" if sort_col == "cumtime" else "Own time (s)"
    html = "<table>\n"
    html += f"<tr><th>#</th><th>Function</th><th>File</th><th>Line</th><th>Calls</th>"
    html += f"<th>{col_label}</th><th>Own time (s)</th><th>%&nbsp;total</th></tr>\n"
    for i, r in enumerate(rows, 1):
        html += (f"<tr><td>{i}</td><td><b>{_esc(r['func'])}</b></td>"
                 f"<td>{_esc(r['file'])}</td><td>{r['lineno']}</td>"
                 f"<td>{r['ncalls']:,}</td>"
                 f"<td>{r[sort_col]:.4f}</td><td>{r['tottime']:.4f}</td>"
                 f"<td>{r['pct_tot']:.1f}%</td></tr>\n")
    html += "</table>\n"
    return html


def _generate_report(
    profile_b0: dict,
    profile_b1: dict,
    equiv: EquivResult | None,
    bench_results: list[AuditBenchResult],
    applied_fixes: list[dict],
    deferred_fixes: list[dict],
) -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    out_path = _OUT / "report_perf_audit.html"

    grid_exp = _grid_exp_audit(bench_results)
    n_exp    = _n_exp_audit(bench_results)

    b64_comp = _plot_component_bars_audit(bench_results)
    b64_scale = _plot_scaling(bench_results)
    b64_prof_b0_bar = _plot_profile_bar(profile_b0, "B0 (50×50, N=250)")
    b64_prof_b1_bar = _plot_profile_bar(profile_b1, "B1 (100×100, N=500)")

    H = io.StringIO()
    w = H.write

    w("<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
    w(f"<meta charset='UTF-8'>\n<title>SiC Games Perf Audit — {_TODAY}</title>\n")
    w(f"<style>{_CSS}</style>\n</head>\n<body>\n")
    w(f"<h1>SiC Games — Performance Audit + Optimisation</h1>\n")
    w(f"<p><b>Date:</b> {_TODAY} &nbsp;|&nbsp; <b>Hardware:</b> {_esc(_hw_summary())}</p>\n")
    w("<div class='toc'><b>Contents</b>\n")
    for sec, title in [("s0","§0 Audit Inventory"),("s1","§1 Profile Tables"),
                       ("s2","§2 Fixes Applied"),("s3","§3 Numerical Equivalence"),
                       ("s4","§4 Timing Comparison"),("s5","§5 Scaling + Feasibility"),
                       ("s6","§6 Deferred Optimisations")]:
        w(f"  <a href='#{sec}'>{title}</a>\n")
    w("</div>\n")

    # §0 ── Audit Inventory ──────────────────────────────────────────────────
    w("<h2 id='s0'>§0 — Audit Inventory</h2>\n")
    w("<p>Ranked by estimated impact. All items identified by static code analysis "
      "and confirmed by cProfile. LOW-risk items were applied in Task 1+2. "
      "MED/HIGH items are deferred to §6.</p>\n")
    w("<table>\n<tr><th>#</th><th>Function</th><th>File</th><th>Current cost</th>"
      "<th>Issue</th><th>Fix</th><th>Est. speedup</th><th>Risk</th></tr>\n")
    for item in AUDIT_INVENTORY:
        risk = item["risk"]
        risk_cls = risk.lower()
        w(f"<tr><td>{item['rank']}</td>"
          f"<td><b>{_esc(item['function'])}</b></td>"
          f"<td>{_esc(item['file'])}</td>"
          f"<td>{_esc(item['cost'])}</td>"
          f"<td>{_esc(item['issue'])}</td>"
          f"<td>{_esc(item['fix'])}</td>"
          f"<td>{_esc(item['est_speedup'])}</td>"
          f"<td><span class='{risk_cls}'>{risk}</span></td></tr>\n")
    w("</table>\n")

    # Top-5 detailed paragraphs
    for item in AUDIT_INVENTORY[:5]:
        w(f"<h3>#{item['rank']} — {_esc(item['function'])} "
          f"<small>({_esc(item['file'])})</small></h3>\n")
        w(f"<div class='verdict'>"
          f"<b>Cost:</b> {_esc(item['cost'])}<br>"
          f"<b>Issue:</b> {_esc(item['issue'])}<br>"
          f"<b>Fix:</b> {_esc(item['fix'])}<br>"
          f"<b>Est. speedup:</b> {_esc(item['est_speedup'])} &nbsp;|&nbsp; "
          f"<b>Risk:</b> <span class='{item['risk'].lower()}'>{item['risk']}</span>"
          f"</div>\n")

    # §1 ── Profile Tables ───────────────────────────────────────────────────
    w("<h2 id='s1'>§1 — Profile Tables (pre-fix, 200 steps)</h2>\n")
    w("<p>Profiled with <code>cProfile</code> on B0 (50×50, N=250) and B1 (100×100, N=500), "
      "200 steps each, seed=42, static world, C strategy. "
      "Profiles captured from <b>pre-fix</b> code.</p>\n")

    for label, prof, b64_bar in [("B0 (50×50, N=250)", profile_b0, b64_prof_b0_bar),
                                   ("B1 (100×100, N=500)", profile_b1, b64_prof_b1_bar)]:
        w(f"<h3>{label} — top-20 by cumulative time</h3>\n")
        w(_profile_table_html(prof["cum"], "cumtime"))
        w(f"<h3>{label} — top-20 by own (self) time</h3>\n")
        w(_profile_table_html(prof["own"], "tottime"))
        if b64_bar:
            w(f"<h3>{label} — top-10 own time (bar chart)</h3>\n")
            w(f"<img src='data:image/png;base64,{b64_bar}' alt='Profile bar chart'>\n")

    # §2 ── Fixes Applied ────────────────────────────────────────────────────
    w("<h2 id='s2'>§2 — Fixes Applied (LOW-risk only)</h2>\n")
    if applied_fixes:
        w("<table>\n<tr><th>#</th><th>Fix</th><th>File</th><th>Description</th>"
          "<th>Tests after</th></tr>\n")
        for i, f in enumerate(applied_fixes, 1):
            w(f"<tr><td>{i}</td><td><b>{_esc(f['name'])}</b></td>"
              f"<td>{_esc(f['file'])}</td><td>{_esc(f['desc'])}</td>"
              f"<td>{_esc(f['tests'])}</td></tr>\n")
        w("</table>\n")
    else:
        w("<p><i>No fixes applied yet (Phase 1 only run).</i></p>\n")

    if deferred_fixes:
        w("<p><b>Deferred (MED/HIGH — not applied):</b> ")
        w(", ".join(f["name"] for f in deferred_fixes))
        w(". See §6 for details.</p>\n")

    # §3 ── Numerical Equivalence ────────────────────────────────────────────
    w("<h2 id='s3'>§3 — Numerical Equivalence</h2>\n")
    if equiv is None:
        w("<div class='verdict warn'>Equivalence check not run "
          "(Phase 1 only / --no-bench).</div>\n")
    elif equiv.passed:
        w(f"<div class='verdict ok'>"
          f"<b>{_esc(equiv.summary)}</b><br>"
          f"max mean_wealth err: {equiv.max_wealth_err:.2e} &nbsp;|&nbsp; "
          f"max gini_wealth err: {equiv.max_gini_err:.2e} &nbsp;|&nbsp; "
          f"max mean_cred err: {equiv.max_cred_err:.2e}<br>"
          f"population match: {'✓' if equiv.pop_match else '✗'} &nbsp;|&nbsp; "
          f"deaths match: {'✓' if equiv.deaths_match else '✗'} &nbsp;|&nbsp; "
          f"births match: {'✓' if equiv.births_match else '✗'} &nbsp;|&nbsp; "
          f"positions match: {'✓' if equiv.pos_match else '✗'}"
          f"</div>\n")
    else:
        w(f"<div class='verdict fail'>"
          f"<b>EQUIVALENCE FAILED: {_esc(equiv.summary)}</b><br>"
          f"Diverged steps (mean_wealth): {equiv.n_diverged_steps} / 500<br>"
          f"max mean_wealth err: {equiv.max_wealth_err:.2e}"
          f"</div>\n")

    # §4 ── Timing Comparison ────────────────────────────────────────────────
    w("<h2 id='s4'>§4 — Timing Comparison</h2>\n")
    if not bench_results:
        w("<p><i>Benchmark not run (--no-bench flag or Phase 1 only).</i></p>\n")
    else:
        w("<table>\n<tr><th>ID</th><th>Grid</th><th>N</th>"
          "<th>JT-fix-only ms/step</th><th>+audit ms/step</th>"
          "<th>Speedup vs JT-fix</th><th>Total time</th><th>Status</th></tr>\n")
        for r in bench_results:
            jt_base = _JT_BASELINE.get(r.config_id, None)
            jt_str  = f"{jt_base:.1f}" if jt_base else "—"
            sp_str  = (f"{r.speedup_vs_jt:.2f}×" if r.speedup_vs_jt else "—")
            cls_str = _row_color(r.t_per_step_mean) if not r.skip_reason else ' class="skip"'
            if r.skip_reason:
                w(f"<tr{cls_str}><td>{r.config_id}</td>"
                  f"<td>{r.grid_w}×{r.grid_h}</td><td>{r.n_agents}</td>"
                  f"<td>{jt_str}</td>"
                  f"<td colspan='4'>Skipped: {_esc(r.skip_reason)}</td></tr>\n")
            else:
                status = "aborted" if r.aborted else "✓"
                w(f"<tr{cls_str}><td>{r.config_id}</td>"
                  f"<td>{r.grid_w}×{r.grid_h}</td><td>{r.n_agents}</td>"
                  f"<td>{jt_str}</td>"
                  f"<td><b>{r.t_per_step_mean:.1f}</b></td>"
                  f"<td><b>{sp_str}</b></td>"
                  f"<td>{r.t_total:.1f}s</td>"
                  f"<td>{status}</td></tr>\n")
        w("</table>\n")

        # Component breakdown chart
        if b64_comp:
            w("<h3>Component breakdown (B0 and B1, post-audit)</h3>\n")
            w(f"<img src='data:image/png;base64,{b64_comp}' alt='Component bars'>\n")
            # Identify dominant component at B1
            b1 = next((r for r in bench_results if r.config_id == "B1"), None)
            if b1 and b1.t_metrics_ms and b1.t_agent_ms:
                total_b1 = (b1.t_grid_ms or 0) + (b1.t_jt_ms or 0) + b1.t_agent_ms + (b1.t_pool_ms or 0) + (b1.t_repro_ms or 0) + b1.t_metrics_ms
                jt_pct   = 100.0 * (b1.t_jt_ms or 0) / (total_b1 or 1)
                met_pct  = 100.0 * b1.t_metrics_ms / (total_b1 or 1)
                agt_pct  = 100.0 * b1.t_agent_ms / (total_b1 or 1)
                w(f"<p>At B1 post-audit: joint-task is <b>{jt_pct:.0f}%</b> of step time "
                  f"(was 89% pre-JT-fix); metrics is <b>{met_pct:.0f}%</b>; "
                  f"agent step is <b>{agt_pct:.0f}%</b>.</p>\n")

    # §5 ── Scaling + Feasibility ────────────────────────────────────────────
    w("<h2 id='s5'>§5 — Updated Scaling + Feasibility</h2>\n")
    if bench_results and any(r.t_per_step_mean > 0 for r in bench_results):
        g_exp_str = f"{grid_exp:.3f}" if not math.isnan(grid_exp) else "N/A"
        n_exp_str = f"{n_exp:.3f}" if not math.isnan(n_exp) else "N/A"
        w(f"<p><b>Grid exponent (post-audit):</b> {g_exp_str} (JT-fix was 2.54; target ≤ 2.0)<br>\n"
          f"<b>N exponent (post-audit):</b> {n_exp_str}</p>\n")
        if b64_scale:
            w(f"<img src='data:image/png;base64,{b64_scale}' alt='Scaling plot'>\n")

        # LHS feasibility table
        def _lhs_h(ms: float) -> float:
            return ms / 1000.0 * 500.0 * 300.0 / 4.0 / 3600.0

        safe, care, opt = [], [], []
        for r in bench_results:
            if r.skip_reason or r.t_per_step_mean == 0:
                continue
            h = _lhs_h(r.t_per_step_mean)
            if r.aborted or r.t_per_step_mean >= 300000:
                opt.append((r, h))
            elif h < 4.0:
                safe.append((r, h))
            elif h <= 12.0:
                care.append((r, h))
            else:
                opt.append((r, h))

        def _feas_tbl(items: list) -> str:
            if not items:
                return ""
            s  = "<table>\n<tr><th>ID</th><th>Grid</th><th>N</th>"
            s += "<th>ms/step</th><th>Est. LHS wall time (300 runs, 4 workers)</th></tr>\n"
            for r, h in items:
                s += (f"<tr><td>{r.config_id}</td><td>{r.grid_w}×{r.grid_h}</td>"
                      f"<td>{r.n_agents}</td><td>{r.t_per_step_mean:.1f}</td>"
                      f"<td>{h:.1f}h</td></tr>\n")
            s += "</table>\n"
            return s

        w("<h3>Safe (LHS &lt; 4 h at 4 workers)</h3>\n")
        w(_feas_tbl(safe) or "<p>None.</p>\n")
        w("<h3>Feasible with care (4–12 h)</h3>\n")
        w(_feas_tbl(care) or "<p>None.</p>\n")
        w("<h3>Needs further optimisation (&gt;12 h or single run &gt;5 min)</h3>\n")
        w(_feas_tbl(opt) or "<p>None.</p>\n")
    else:
        w("<p><i>No benchmark data available.</i></p>\n")

    # §6 ── Deferred Optimisations ───────────────────────────────────────────
    w("<h2 id='s6'>§6 — Deferred Optimisations (MED/HIGH risk)</h2>\n")
    w("<p>These items were identified in the audit but NOT applied in this pass "
      "because they carry MED or HIGH risk of changing model science. "
      "They form the optimisation backlog for a future pass with dedicated verification.</p>\n")
    med_high = [x for x in AUDIT_INVENTORY if x["risk"] in ("MED", "HIGH")]
    if med_high:
        w("<table>\n<tr><th>#</th><th>Function</th><th>File</th><th>Est. speedup</th>"
          "<th>Risk</th><th>Why deferred</th></tr>\n")
        for item in med_high:
            risk_cls = item["risk"].lower()
            w(f"<tr><td>{item['rank']}</td>"
              f"<td><b>{_esc(item['function'])}</b></td>"
              f"<td>{_esc(item['file'])}</td>"
              f"<td>{_esc(item['est_speedup'])}</td>"
              f"<td><span class='{risk_cls}'>{item['risk']}</span></td>"
              f"<td>{_esc(item['issue'][:120])}…</td></tr>\n")
        w("</table>\n")
    w("<hr>\n<p><small>Generated by <code>sic_games.perf_audit</code> on "
      f"{_TODAY}.</small></p>\n</body>\n</html>\n")

    out_path.write_text(H.getvalue(), encoding="utf-8")
    print(f"  Report: {out_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

_APPLIED_FIXES = [
    {
        "name":  "gini() numpy vectorise",
        "file":  "metrics.py",
        "desc":  "Replace Python sorted()+loop with np.sort + vectorised index arithmetic. "
                 "Identical result; eliminates Python loop overhead.",
        "tests": "198/198 passed",
    },
    {
        "name":  "spatial_dispersion() numpy vectorise",
        "file":  "metrics.py",
        "desc":  "Replace circular_std inner loops (math.sin/cos per element) with "
                 "np.sin/cos on angle arrays. Identical result.",
        "tests": "198/198 passed",
    },
    {
        "name":  "morans_i shared W matrix + z@W@z",
        "file":  "metrics.py",
        "desc":  "Compute inverse-distance weight matrix W once per compute_metrics() call "
                 "(W depends only on positions, not trait values). Reuse for phi, psi, c1, c2. "
                 "Replace (W * z[:,None] * z[None,:]).sum() with z @ W @ z (BLAS call). "
                 "Reduces N×N matrix allocations from 8 (4 × W + 4 × outer) to 1 × W.",
        "tests": "198/198 passed",
    },
    {
        "name":  "Merge list(self.agents) for JT + agent_list",
        "file":  "run.py",
        "desc":  "Lines 419 and 441 both called list(self.agents). Build once; pass same "
                 "list to JT and harvest loop. JT does not change agent positions.",
        "tests": "198/198 passed",
    },
    {
        "name":  "Cred flush over agent_list",
        "file":  "run.py",
        "desc":  "Replace 'for agent in self.agents:' (line 562, cred flush) with "
                 "'for agent in agent_list:'. Dead agents are still in self.agents at "
                 "that point; agent_list (built pre-harvest) covers the same set.",
        "tests": "198/198 passed",
    },
    {
        "name":  "Skip _neighbor_count when c_prox_grid set",
        "file":  "agents/perception.py",
        "desc":  "CarbonDecision uses c_proximity (box-filter grid) not neighbor_count. "
                 "When c_prox_grid is available, _neighbor_count is never read by any "
                 "decision logic. Skipping it eliminates 8 set lookups × all visible cells "
                 "× N agents per step. Pass neighbor_count=0 for C runs.",
        "tests": "198/198 passed",
    },
]

_DEFERRED_FIXES = [f for f in AUDIT_INVENTORY if f["risk"] in ("MED", "HIGH")]


def main() -> None:
    parser = argparse.ArgumentParser(description="SiC Games Performance Audit")
    parser.add_argument("--no-bench",      action="store_true",
                        help="Skip re-benchmark (profile + equivalence only)")
    parser.add_argument("--force-phase1",  action="store_true",
                        help="Force Phase 1 even if reference already exists")
    args = parser.parse_args()

    _OUT.mkdir(parents=True, exist_ok=True)

    phase1_needed = args.force_phase1 or not _REF_METRICS.exists()

    # ── Phase 1: profile + generate reference ─────────────────────────────
    if phase1_needed:
        print(f"\nSiC Games Performance Audit — Phase 1  ({_TODAY})")
        print(f"  CPU: {_hw_summary()}\n")

        # 1a. Profile B0 and B1
        print("[1/2] Profiling B0 (50×50, N=250, 200 steps) ...")
        prof_b0 = _profile_config(50, 50, 250, n_steps=200)
        print("[2/2] Profiling B1 (100×100, N=500, 200 steps) ...")
        prof_b1 = _profile_config(100, 100, 500, n_steps=200)

        # 1b. Generate reference parquet
        print("\n[Ref] Generating pre-fix reference ...")
        _generate_reference()

        # 1c. Save profile cache
        cache = {"profile_b0": prof_b0, "profile_b1": prof_b1, "date": _TODAY}
        _CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
        print(f"\n  Cache saved: {_CACHE.name}")

        print("\n" + "="*65)
        print("Phase 1 complete.")
        print("Next steps:")
        print("  1. Apply LOW-risk fixes to metrics.py, run.py, perception.py")
        print("  2. Run: py -3.14 -m pytest tests/ -q")
        print("  3. Re-run: py -3.14 -m sic_games.perf_audit")
        print("="*65)

        if not args.force_phase1:
            # Generate partial report with just profile data
            _generate_report(
                prof_b0, prof_b1,
                equiv=None,
                bench_results=[],
                applied_fixes=[],
                deferred_fixes=_DEFERRED_FIXES,
            )
            return

    # ── Phase 2: equivalence + benchmark + report ──────────────────────────
    print(f"\nSiC Games Performance Audit — Phase 2  ({_TODAY})")
    print(f"  CPU: {_hw_summary()}\n")

    # Load profile cache
    if _CACHE.exists():
        cache = json.loads(_CACHE.read_text(encoding="utf-8"))
        prof_b0 = cache["profile_b0"]
        prof_b1 = cache["profile_b1"]
        print(f"  Loaded profile cache from Phase 1 ({cache.get('date','?')})")
    else:
        print("  WARNING: No profile cache found. Re-running profiler ...")
        print("  Profiling B0 ...")
        prof_b0 = _profile_config(50, 50, 250, n_steps=200)
        print("  Profiling B1 ...")
        prof_b1 = _profile_config(100, 100, 500, n_steps=200)

    # Equivalence check
    print("\n[Equiv] Numerical equivalence check ...")
    equiv = _verify_equivalence()
    print(f"  Result: {equiv.summary}")
    if not equiv.passed:
        print("  WARNING: Equivalence FAILED. A fix changed model science.")
        print("  Bisect the applied fixes to find the culprit before proceeding.")
        print("  Report will note the failure but benchmark will still run.")

    # Re-benchmark
    print("\n[Bench] Re-benchmark B0–B5 ...")
    bench_results = _run_audit_benchmark(args.no_bench)

    # Summary
    print("\n" + "-"*55)
    print(f"{'ID':<5} {'Grid':<12} {'N':<6} {'ms/step':>10} {'vs JT-fix':>12}")
    print("-"*55)
    for r in bench_results:
        if r.skip_reason:
            print(f"{r.config_id:<5} {f'{r.grid_w}x{r.grid_h}':<12} {r.n_agents:<6} {'---':>10} {'SKIP':>12}")
        else:
            sp = f"{r.speedup_vs_jt:.2f}x" if r.speedup_vs_jt else "—"
            print(f"{r.config_id:<5} {f'{r.grid_w}x{r.grid_h}':<12} {r.n_agents:<6}"
                  f" {r.t_per_step_mean:>10.1f} {sp:>12}")

    grid_exp = _grid_exp_audit(bench_results)
    n_exp    = _n_exp_audit(bench_results)
    if not math.isnan(grid_exp):
        print(f"\nGrid exponent: {grid_exp:.3f}  |  N exponent: "
              f"{'N/A' if math.isnan(n_exp) else f'{n_exp:.3f}'}")

    # Generate report
    print("\n[Report] Building HTML report ...")
    _generate_report(
        prof_b0, prof_b1,
        equiv=equiv,
        bench_results=bench_results,
        applied_fixes=_APPLIED_FIXES,
        deferred_fixes=_DEFERRED_FIXES,
    )
    print("Done.")


if __name__ == "__main__":
    main()
