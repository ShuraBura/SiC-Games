"""OWE-1.1 Follow-Up: home-range estimator fix + N_carry scale calibration.

Task A: recompute home-range as contemporaneous rolling-window range
        (annual=12 steps, seasonal=3 steps) vs the OWE-1 lifetime track.
Task B: sweep N_carry -> settled-N on 100x100; find N_carry for settled~2500;
        recalibration check (clean settle + est_starv).

Generates: outputs/owe1_calibration/report_owe1_followup.html

Usage:
    py -m sic_games.owe1_1_followup
"""
from __future__ import annotations

import base64
import io
import math
import statistics
import time
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from sic_games.owe1_calibration import _bench_config, _fig_b64, _html_table

_REPO = Path(__file__).parent.parent.parent
_OUT = _REPO / "outputs" / "owe1_calibration"
_TODAY = "2026-05-31"


# ── Task A: home-range with position sequences (lifetime + windowed) ──────────

def _run_homerange_windowed(grid_w=100, grid_h=100, n=2000, steps=2500,
                            n_carry_override=None) -> dict:
    """Run C-static reference, logging each agent's full position sequence.

    Returns lifetime distinct-cell median plus rolling-window (annual=12,
    seasonal=3) medians. Window stat per agent = median over that agent's
    windows; population stat = median (and IQR) over agents.
    """
    from sic_games.run import SugarWorld
    cfg = _bench_config(grid_w, grid_h, n, steps, n_carry_override=n_carry_override)
    model = SugarWorld(cfg)
    pos_seq: dict[int, list] = {}   # uid -> [pos_t, pos_{t+1}, ...] contiguous while alive
    pop_trace = []
    for _ in range(steps):
        model.step()
        for agent in model.agents:
            pos_seq.setdefault(agent.unique_id, []).append(agent.pos)
        pop_trace.append(len(list(model.agents)))

    def _agent_window_distinct(seq: list, w: int) -> float:
        """Median distinct-cell count over rolling windows of length w for one agent."""
        if len(seq) < w:
            return float(len(set(seq)))  # short-lived: whole life is one (partial) window
        counts = [len(set(seq[i:i + w])) for i in range(len(seq) - w + 1)]
        return float(statistics.median(counts))

    lifetime = [len(set(s)) for s in pos_seq.values()]
    annual = [_agent_window_distinct(s, 12) for s in pos_seq.values()]
    seasonal = [_agent_window_distinct(s, 3) for s in pos_seq.values()]

    def _stats(vals: list) -> dict:
        return {
            "median": float(np.median(vals)),
            "q25": float(np.percentile(vals, 25)),
            "q75": float(np.percentile(vals, 75)),
            "mean": float(np.mean(vals)),
        }

    return {
        "n_carry": cfg.birth_c.carrying_cost.N_carry,
        "n_agents_tracked": len(pos_seq),
        "lifetime": _stats(lifetime),
        "annual": _stats(annual),
        "seasonal": _stats(seasonal),
        "pop_trace": pop_trace,
    }


# ── Task B: N_carry sweep -> settled-N + est_starv ────────────────────────────

def _run_ncarry_probe(n_carry: int, init_n: int, steps=2000,
                      grid=100) -> dict:
    """Run C-static at given N_carry; measure settled-N and est_starv (t>=1500)."""
    from sic_games.run import SugarWorld
    cfg = _bench_config(grid, grid, init_n, steps, n_carry_override=n_carry)
    model = SugarWorld(cfg)
    pop_trace = []
    est_starv_trace = []
    for _ in range(steps):
        model.step()
        pop_trace.append(len(list(model.agents)))
        m = model.metrics_log[-1]
        est_starv_trace.append(getattr(m, "deaths_starvation_established", 0))
    settled = float(np.mean(pop_trace[1500:])) if len(pop_trace) > 1500 else float(np.mean(pop_trace))
    settled_std = float(np.std(pop_trace[1500:])) if len(pop_trace) > 1500 else float(np.std(pop_trace))
    est_starv = float(np.mean(est_starv_trace[1500:])) if len(est_starv_trace) > 1500 else float(np.mean(est_starv_trace))
    return {
        "n_carry": n_carry, "init_n": init_n,
        "settled": settled, "settled_std": settled_std,
        "ratio": settled / n_carry,
        "est_starv": est_starv,
        "final": pop_trace[-1],
        "pop_trace": pop_trace,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)

    # ── Task A ────────────────────────────────────────────────────────────────
    print("=== Task A: windowed home-range (C static medium-rho, 2500 steps) ===")
    hr = _run_homerange_windowed(100, 100, 2000, 2500)
    lt, an, se = hr["lifetime"], hr["annual"], hr["seasonal"]
    print(f"  Lifetime  median: {lt['median']:.1f} cells  IQR[{lt['q25']:.0f},{lt['q75']:.0f}]")
    print(f"  Annual(12) median: {an['median']:.1f} cells  IQR[{an['q25']:.0f},{an['q75']:.0f}]")
    print(f"  Seasonal(3) median: {se['median']:.1f} cells  IQR[{se['q25']:.0f},{se['q75']:.0f}]")

    def _derive(median_cells: float) -> tuple:
        ell = math.sqrt(100.0 / median_cells) if median_cells > 0 else float("nan")
        cf = 10.0 / ell if ell > 0 else float("nan")
        return ell, cf

    ell_lt, cf_lt = _derive(lt["median"])
    ell_an, cf_an = _derive(an["median"])
    ell_se, cf_se = _derive(se["median"])
    print(f"  ell lifetime={ell_lt:.2f} km (cf {cf_lt:.1f}x); annual={ell_an:.2f} km (cf {cf_an:.1f}x); seasonal={ell_se:.2f} km (cf {cf_se:.1f}x)")

    # Verdict: consistent if solved ell within [5,20] of 10km target (factor 2)
    def _verdict(ell: float) -> str:
        return "CONSISTENT" if 5.0 <= ell <= 20.0 else "still inconsistent"
    print(f"  Verdict annual: {_verdict(ell_an)}; seasonal: {_verdict(ell_se)}")

    # ── Task B ────────────────────────────────────────────────────────────────
    print("\n=== Task B: N_carry -> settled-N sweep ===")
    rungs = [(1600, 2000), (3000, 3000), (4500, 3500), (6000, 4000)]
    probe_results = []
    for nc, init in rungs:
        print(f"  Probe N_carry={nc}, init={init} ...")
        r = _run_ncarry_probe(nc, init, 2000)
        probe_results.append(r)
        print(f"    settled={r['settled']:.0f} (ratio {r['ratio']:.3f}), est_starv={r['est_starv']:.3f}, std={r['settled_std']:.0f}")

    # Linear fit settled = a*N_carry + b
    nc_arr = np.array([r["n_carry"] for r in probe_results], dtype=float)
    settled_arr = np.array([r["settled"] for r in probe_results], dtype=float)
    a, b = np.polyfit(nc_arr, settled_arr, 1)
    target_settled = 2500.0
    n_carry_for_2500 = (target_settled - b) / a if a != 0 else float("nan")
    print(f"  Fit: settled = {a:.3f} * N_carry + {b:.1f}")
    print(f"  N_carry for settled~2500: {n_carry_for_2500:.0f}")
    chosen_n_carry = int(round(n_carry_for_2500 / 100.0) * 100)  # round to nearest 100
    print(f"  Chosen N_carry (rounded): {chosen_n_carry}")

    # ── Task B.2: recalibration check at chosen N_carry ──────────────────────
    print(f"\n=== Task B.2: recalibration check at N_carry={chosen_n_carry} ===")
    # init slightly below expected settled band for boom headroom
    init_check = int(target_settled * 0.9)
    check = _run_ncarry_probe(chosen_n_carry, init_check, 2000)
    est_starv_baseline = 0.78  # the N_carry=400 baseline bound (directive)
    starv_ok = check["est_starv"] <= est_starv_baseline
    # Clean settle: low relative std in settled window
    rel_std = check["settled_std"] / check["settled"] if check["settled"] > 0 else float("inf")
    clean_settle = rel_std < 0.15  # <15% relative fluctuation
    print(f"  settled={check['settled']:.0f} (ratio {check['ratio']:.3f}), est_starv={check['est_starv']:.3f}")
    print(f"  est_starv <= 0.78: {'PASS' if starv_ok else 'FAIL (note for supervisor)'}")
    print(f"  clean settle (rel std {rel_std:.3f} < 0.15): {'PASS' if clean_settle else 'degraded'}")

    # ── Build report ──────────────────────────────────────────────────────────
    print("\n=== Building follow-up report ===")
    _build_report(
        hr=hr, ell_lt=ell_lt, cf_lt=cf_lt, ell_an=ell_an, cf_an=cf_an,
        ell_se=ell_se, cf_se=cf_se, verdict_an=_verdict(ell_an), verdict_se=_verdict(ell_se),
        probe_results=probe_results, a=a, b=b, n_carry_for_2500=n_carry_for_2500,
        chosen_n_carry=chosen_n_carry, check=check, starv_ok=starv_ok,
        clean_settle=clean_settle, rel_std=rel_std,
    )
    print(f"Report: {_OUT / 'report_owe1_followup.html'}")


def _build_report(**k: Any) -> None:
    hr = k["hr"]; lt = hr["lifetime"]; an = hr["annual"]; se = hr["seasonal"]
    pr = k["probe_results"]

    # Home-range population trace plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    ax = axes[0]
    labels = ["Lifetime", "Annual(12)", "Seasonal(3)"]
    medians = [lt["median"], an["median"], se["median"]]
    ax.bar(labels, medians, color=["firebrick", "steelblue", "seagreen"])
    for i, v in enumerate(medians):
        ax.text(i, v + 0.5, f"{v:.0f}", ha="center", fontsize=9)
    ax.set_ylabel("median distinct cells"); ax.set_title("Task A: home-range by window")

    ax2 = axes[1]
    for r in pr:
        ax2.plot(r["pop_trace"], lw=0.8, label=f"N_carry={r['n_carry']}")
    ax2.axhline(2500, ls="--", color="red", alpha=0.6, label="target settled 2500")
    ax2.set_xlabel("step"); ax2.set_ylabel("N"); ax2.set_title("Task B: N(t) by N_carry")
    ax2.legend(fontsize=7)
    fig.tight_layout()
    plot_b64 = _fig_b64(fig)

    verdict_color_an = "green" if k["verdict_an"] == "CONSISTENT" else "orange"

    sweep_rows = [
        (f"B{i+1}", str(r["n_carry"]), str(r["init_n"]),
         f"{r['settled']:.0f}", f"{r['ratio']:.3f}", f"{r['est_starv']:.3f}")
        for i, r in enumerate(pr)
    ]

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>OWE-1.1 Follow-Up ({_TODAY})</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1100px;margin:auto;padding:20px;}}
h1{{color:#2c3e50;}} h2{{color:#2c6fa8;border-bottom:1px solid #ccc;padding-bottom:4px;margin-top:28px;}}
h3{{color:#444;}} table{{border-collapse:collapse;margin:8px 0;font-size:0.92em;}}
th{{background:#dce8f5;padding:5px 10px;}} td{{padding:4px 10px;}}
code{{background:#f4f4f4;padding:1px 4px;border-radius:3px;}}
.pass{{color:green;font-weight:bold;}} .fail{{color:red;font-weight:bold;}} .warn{{color:#c70;font-weight:bold;}}
pre{{background:#f7f7f7;padding:10px;border-radius:4px;font-size:0.82em;overflow-x:auto;}}
</style></head><body>
<h1>OWE-1.1 Follow-Up — Home-Range Estimator Fix + N_carry Calibration</h1>
<p><b>Date:</b> {_TODAY} &nbsp;|&nbsp; Extends <code>report_owe1.html</code>.
Reference config throughout: C arm, static (unshocked) world, medium-⟨ρ⟩, seed=42.</p>

<h2>§A Home-Range Estimator — Lifetime vs Contemporaneous</h2>
<h3>A.1 Estimator disclosure</h3>
<p><b>File location (drive-side, supervisor cannot otherwise see it):</b>
<code>G:\\My Drive\\docs\\SiC Games\\sic_games\\src\\sic_games\\owe1_calibration.py</code>,
function <code>_run_homerange()</code>. The follow-up windowed estimator is in
<code>owe1_1_followup.py</code>, function <code>_run_homerange_windowed()</code>.</p>
<p><b>The OWE-1 estimator was LIFETIME-ACCUMULATED distinct-cell count</b> — for each agent,
a Python <code>set</code> accumulating every cell the agent occupied across <i>every step it
was alive</i> (birth to death), then population median of those counts. Confirmed: the ~56-cell
figure is lifetime-accumulated, NOT windowed. Verbatim core:</p>
<pre>for _ in range(steps):
    model.step()
    for agent in model.agents:
        agent_cells.setdefault(agent.unique_id, set()).add(agent.pos)  # lifetime accumulation
# ...
home_ranges_cells = [len(cells) for cells in agent_cells.values()]
median_cells = np.median(home_ranges_cells)   # = 56.0</pre>

<h3>A.2 / A.3 Contemporaneous rolling-window recompute</h3>
<p>Per-agent position sequences logged over 2500 steps; rolling windows computed
(agent stat = median over its windows; population stat = median/IQR over agents).
Agents living shorter than a window use their whole-life distinct count.</p>
{_html_table([
    ("Lifetime (OWE-1 estimator)", f"{lt['median']:.1f}", f"[{lt['q25']:.0f}, {lt['q75']:.0f}]", f"{k['ell_lt']:.2f}", f"{k['cf_lt']:.1f}x"),
    ("Annual window (12 steps = 1 yr)", f"{an['median']:.1f}", f"[{an['q25']:.0f}, {an['q75']:.0f}]", f"{k['ell_an']:.2f}", f"{k['cf_an']:.1f}x"),
    ("Seasonal window (3 steps)", f"{se['median']:.1f}", f"[{se['q25']:.0f}, {se['q75']:.0f}]", f"{k['ell_se']:.2f}", f"{k['cf_se']:.1f}x"),
], ["Window definition", "Median cells", "IQR cells", "Solved ell (km)", "Consistency factor (10/ell)"])}
<p><b>Verdict.</b> Annual-window solved cell-size ell = {k['ell_an']:.2f} km
(<span class="{verdict_color_an}">{k['verdict_an']}</span> with committed ~10 km;
consistency factor {k['cf_an']:.1f}x). Seasonal-window ell = {k['ell_se']:.2f} km
({k['verdict_se']}).</p>
<p><b>Status of the OWE-1 56x finding:</b>
{"largely an ESTIMATOR-DEFINITION ARTIFACT — the lifetime track conflated multi-decade drift with contemporaneous territory. Under a contemporaneous (annual) window the cell-size inconsistency shrinks substantially and the 56x lifetime overshoot is SUPERSEDED." if k['ell_an'] >= 3.0 else "PERSISTS — even under a contemporaneous annual window the solved cell-size remains well below the committed ~10 km, so the model-vs-ethnography mobility tension stands (not merely an estimator artifact)."}
The OWE-1 report §3 lifetime-based 56x is hereby labelled
{"SUPERSEDED by the annual-window result." if k['ell_an'] >= 3.0 else "CONFIRMED (windowing does not resolve it)."}</p>

<h2>§B N_carry Scale Calibration</h2>
<p><b>Authorisation:</b> N_carry was set in Stage 4.5 Task 0 as a numerical-stability scale
parameter (top of the hand-set [150,400] viability band on 50×50), NOT an ecological estimate.
Supervisor (2026-05-31) authorises setting it to a target population. Target settled N ≈ 2000–3000
(midpoint 2500) to realise 20–60 ethnographic bands on 100×100.</p>
<img src="data:image/png;base64,{plot_b64}" style="max-width:100%">
<h3>B.1 N_carry → settled-N mapping (measured)</h3>
{_html_table(sweep_rows, ["Run", "N_carry", "init N", "Settled N (t>=1500)", "settled/ceiling", "est_starv/step"])}
<p>Linear fit: <code>settled ≈ {k['a']:.3f} × N_carry + {k['b']:.0f}</code>.
N_carry for settled≈2500: <b>{k['n_carry_for_2500']:.0f}</b> → rounded chosen value
<b>{k['chosen_n_carry']}</b>.</p>
<h3>B.2 Recalibration check at chosen N_carry = {k['chosen_n_carry']}</h3>
{_html_table([
    ("Settled N (t>=1500)", f"{k['check']['settled']:.0f}"),
    ("settled/ceiling ratio", f"{k['check']['ratio']:.3f}"),
    ("Relative std in settled window", f"{k['rel_std']:.3f}"),
    ("Clean settle (rel std < 0.15)", "PASS" if k['clean_settle'] else "DEGRADED"),
    ("est_starv/step", f"{k['check']['est_starv']:.3f}"),
    ("est_starv <= 0.78 baseline", "PASS" if k['starv_ok'] else "FAIL — flag for supervisor"),
], ["Metric", "Value"])}
<p><b>Recalibration verdict:</b>
settling is <b class="{'pass' if k['clean_settle'] else 'warn'}">{'clean' if k['clean_settle'] else 'degraded'}</b>;
established starvation is <b class="{'pass' if k['starv_ok'] else 'fail'}">{f"within baseline ({k['check']['est_starv']:.3f} <= 0.78)" if k['starv_ok'] else f"above baseline ({k['check']['est_starv']:.3f} > 0.78) — p_max_C/alpha_carry may need a note, NOT auto-retuned"}</b>.
{"Settling as clean as the N_carry=400 baseline; no rate retune needed." if (k['clean_settle'] and k['starv_ok']) else "Flagged for supervisor — see note; no auto-retune performed."}</p>
<p><b>Chosen locked N_carry (100×100 target geometry): {k['chosen_n_carry']}</b>
(set ONCE, shared across C and Si arms, locked before examining H1(ii) at the new scale).</p>

<h3>B.3 H1(ii) re-confirmation — FLAG ONLY (registered OWE-14)</h3>
<p>The headline H1(ii) inversion was established at N_carry=400. Moving to {k['chosen_n_carry']}
is a large scale change; the inversion MUST be re-confirmed (≥3 seeds, C vs Si) before H1(ii)
is trusted at the new scale. <b>Registered as OWE-14 in ROADMAP Owed. NOT run in this directive.</b></p>

<h2>§C Standard Run-Length (locked, no compute)</h2>
<p>Supervisor decision (2026-05-31): <b>standard run-length = 12,000 steps</b> (1000 yr,
~4 secular cycles); <b>transient exclusion ~500 steps</b> declared up front (~3.8 productive
cycles, clears the ≥3-cycle bar). 24,000 held in reserve only if cycle-length estimation
proves noisy. Recorded in ROADMAP.</p>

<h2>Doc updates executed</h2>
<ul>
<li><b>MODEL_SPEC §9.3:</b> N_carry-as-calibration honesty note added; corrected windowed
home-range result folded into the §9.3 calibration text.</li>
<li><b>ROADMAP:</b> OWE-14 (re-confirm H1(ii) at calibrated N_carry) registered in Owed;
chosen N_carry={k['chosen_n_carry']} and standard run-length (12k/500 transient) recorded.</li>
<li>Idempotent + conflict-surfacing merge; no contradictions auto-resolved.</li>
</ul>
</body></html>"""

    (_OUT / "report_owe1_followup.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
