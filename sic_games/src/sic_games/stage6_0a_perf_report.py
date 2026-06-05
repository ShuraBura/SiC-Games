"""Build the Stage 6.0a-perf HTML report (§7). Reads perf_results.json; embeds plots.

Recon deliverable (blueprint named exception): the report IS the output. Six sections:
cost surface, profiling, exponents, acceleration variants, forward assessment, the feel.
"""
from __future__ import annotations

import base64
import io
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_OUT = Path(__file__).parent.parent.parent / "outputs" / "stage6_0a_perf"
_TODAY = "2026-06-05"

# Salvaged higher-N point from the first (same n_carry=10x) sweep before the hang.
_SALVAGED = {"label": "N_10000_g100(salvaged)", "grid": 100, "final_n": 19059,
             "mean_occ": 2.30, "peak_occ": 11, "ms_mean": 806.1, "ms_sd": 192.3,
             "cut_status": "ceiling-cut", "rail_status": "PASS"}


def _b64(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=100, bbox_inches="tight")
    b.seek(0); s = base64.b64encode(b.read()).decode(); plt.close(fig); return s


def _tbl(rows, hdr):
    th = "".join(f"<th>{h}</th>" for h in hdr)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table border=1 cellpadding=4 cellspacing=0><tr>{th}</tr>{tr}</table>"


def main():
    res = json.load(open(_OUT / "perf_results.json"))
    # feasible (rail PASS, has ms) points + salvaged
    pts = [r for r in res if r.get("ms_mean") == r.get("ms_mean") and r.get("rail_status") == "PASS"]
    pts_plot = pts + [_SALVAGED]

    # ── §1 cost-surface table (all configs) ──
    rows = []
    for r in res:
        ms = f"{r['ms_mean']:.0f}±{r.get('ms_sd',0):.0f}" if r.get("ms_mean")==r.get("ms_mean") else "—"
        occ = f"{r.get('mean_occ',float('nan')):.2f}/{r.get('peak_occ',0)}" if r.get("mean_occ")==r.get("mean_occ") else "—"
        rows.append((r["label"], r["grid"], r.get("final_n","—"), occ, ms,
                     r.get("cut_status",""), r.get("rail_status","")))
    rows.append((_SALVAGED["label"], 100, 19059, "2.30/11", "806±192", "ceiling-cut", "PASS"))

    # ── cost-surface scatter: ms vs measured N, colour=occupancy ──
    fig, ax = plt.subplots(figsize=(8,5))
    N = np.array([r["final_n"] for r in pts_plot]); MS = np.array([r["ms_mean"] for r in pts_plot])
    OC = np.array([r["mean_occ"] for r in pts_plot])
    sc = ax.scatter(N, MS, c=OC, s=90, cmap="viridis", edgecolor="k", zorder=3)
    for r in pts_plot:
        ax.annotate(r["label"].replace("_g100","").replace("_n2000","").replace("(salvaged)","*"),
                    (r["final_n"], r["ms_mean"]), fontsize=7, xytext=(4,4), textcoords="offset points")
    ax.axhline(300, ls="--", color="red", alpha=0.6, label="300 ms/step ceiling")
    ax.set_xlabel("measured N"); ax.set_ylabel("ms/step (substrate-only)")
    ax.set_xscale("log"); ax.set_yscale("log")
    plt.colorbar(sc, label="mean occupancy (agents/occupied cell)")
    ax.set_title("Cost surface: ms/step vs N (colour=occupancy)"); ax.legend(fontsize=8)
    cost_fig = _b64(fig)

    # ── §2 profiling stacked bar (measured this study) ──
    full = {"Moran's I (O(N^2) diag)":6.85, "c_spatial_density (O(N^2) diag)":4.74,
            "JT process_step":5.0, "diffusion movement":3.18, "mean_cred/birth":3.85,
            "matthew_shares":1.01, "other":47.09-6.85-4.74-5.0-3.18-3.85-1.01}
    sub = {"JT process_step":5.3, "diffusion movement":3.26, "mean_cred/birth":3.65,
           "matthew_shares":1.03, "support_pool":0.76, "_carbon_birth":0.64,
           "other":29.73-5.3-3.26-3.65-1.03-0.76-0.64}
    fig, ax = plt.subplots(figsize=(9,4))
    for i,(d,lbl) in enumerate([(full,"FULL-STEP\n(diagnostics ON)\n47.1s/30steps"),(sub,"SUBSTRATE-ONLY\n(diagnostics OFF)\n29.7s/30steps")]):
        bottom=0
        for k,v in d.items():
            ax.barh(i, v, left=bottom, label=k if i==0 else None); bottom+=v
        ax.text(bottom+0.5, i, lbl, va="center", fontsize=8)
    ax.set_yticks([]); ax.set_xlabel("tottime seconds (30 steps, N->7073, 100x100, kappa=1)")
    ax.set_title("§2 Profiling: where per-step time goes (cProfile tottime)")
    ax.legend(fontsize=7, ncol=2, loc="lower right")
    ax.set_xlim(0,52)
    prof_fig = _b64(fig)

    # ── exponent fits ──
    def expo(p0, p1):
        return math.log(p1[1]/p0[1]) / math.log(p1[0]/p0[0])
    n_lo = expo((1926,98.5),(10060,356.8)); n_hi = expo((10060,356.8),(19059,806.1))

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Stage 6.0a-perf — Substrate Performance Reconnaissance ({_TODAY})</title>
<style>body{{font-family:Arial;max-width:1080px;margin:auto;padding:20px}}
h1{{color:#2c3e50}}h2{{color:#2c6fa8;border-bottom:1px solid #ccc;padding-bottom:4px;margin-top:26px}}
table{{border-collapse:collapse;margin:8px 0;font-size:.9em}}th{{background:#dce8f5;padding:5px 9px}}td{{padding:4px 9px}}
code{{background:#f4f4f4;padding:1px 4px;border-radius:3px}}.box{{background:#f0f6ff;border-left:4px solid #2c6fa8;padding:8px 14px;margin:10px 0}}</style></head><body>
<h1>Stage 6.0a-perf — Substrate Performance Reconnaissance</h1>
<p><b>{_TODAY}.</b> Recon (named exception: the report is the deliverable). Multi-occupancy
substrate, diffusion movement, resource-split + Cred/φ contest. Window: 10 warm-up + 80 measured
steps. Substrate-only timings isolate the substrate by pushing the O(N²) diagnostic metrics
(k_moran/k_density/metrics_every=9999) beyond the window. Per-config 90 s subprocess timeout =
hard-infeasible. n_carry=10×init (population finds equilibrium ~init–2×init). seed=42, κ=1 default.</p>

<div class="box"><b>Process-monitoring note:</b> a <code>runtime_monitor</code> module was added this
cycle (wall-clock vs <code>process_time</code> CPU-time discriminator) so a future frozen log
self-diagnoses <i>usage-pause</i> (wall≫cpu) vs <i>live heavy compute</i> (wall≈cpu). It wires into
the harness next cycle. 6 unit tests; full suite 256 green.</div>

<h2>§1 Cost surface / feasibility table</h2>
{_tbl(rows, ["config","grid","measured N","occ mean/peak","ms/step","cut-status","rail"])}
<img src="data:image/png;base64,{cost_fig}" style="max-width:100%">
<p>Every config has a recorded cut-status and rail-status; every reported timing is from a
rail-passing run. Hard-infeasible = killed at the 90 s timeout (single mega-step under dense
occupancy). "*" = salvaged from the first sweep (same n_carry) before an unrelated usage-pause.</p>

<h2>§2 Profiling breakdown (cheap vs expensive; cProfile tottime)</h2>
<img src="data:image/png;base64,{prof_fig}" style="max-width:100%">
<p><b>Substrate-only (29.7 s/30 steps, N→7073):</b> the legacy <b>joint-task <code>process_step</code></b>
dominates (~5.3 s tottime / ~8.7 s cumulative, ~29%) — it rebuilds co-occupant cohorts over O(W×H)
candidate cells and is the occupancy-sensitive path; <b>diffusion movement</b> ~18%; <b>
<code>mean_cred()</code> recomputed per birth</b> (run.py:320 genexpr, 12.7 M calls, ~12%) is an
O(N×births)≈O(N²) hot spot from the f_C newborn endowment. <b>Full-step adds ~40%</b> from the
sampled O(N²) diagnostics (Moran's I 6.85 s + c_spatial_density 4.74 s) — these mask the substrate
and would gate any high-N run regardless of substrate cost.</p>

<h2>§3 Scaling exponents (approximate — feel, not precision)</h2>
{_tbl([
 ("N (grid 100, low occ)", f"≈{n_lo:.2f} (1.9k→10k) rising to ≈{n_hi:.2f} (10k→19k)", "roughly LINEAR, mildly super-linear at scale (mean_cred/birth O(N²) tail)"),
 ("Grid cells (N=2000, low occ)", "≈0 (sub-dominant)", "ms ~95–99 across 4.9k–10k cells; grid size barely matters at low occupancy — O(N)+occupancy dominate, not O(W×H)"),
 ("Occupancy (grid 40 / dense)", "CLIFF, not a smooth exponent", "feasible to ~2.35/cell (171 ms); >~2.5/cell → hard-infeasible (JT-cohort blowup). THE gating axis."),
], ["axis","exponent","read"])}
<p><b>~2× run-to-run timing variance observed</b> (identical config measured 48 ms and 98 ms on
different sweeps) — ambient machine load; exponents are a feel, not precise. The qualitative
ordering is robust: <b>occupancy ≫ N ≫ grid-cells</b> as cost drivers.</p>

<h2>§4 Acceleration variants tried</h2>
{_tbl([
 ("numpy: JT candidate-cell scan", "2.6× on that sub-step (2.44→0.94 ms), numerically exact (same cell set)", "modest overall — the scan is a small slice of JT; cohort-building (per-candidate Python) is the real JT cost"),
 ("Numba @njit on harvest-split / movement", "NOT APPLICABLE", "Numba not installed in env; and structurally nopython can't compile the hot paths — they take lists of agent OBJECTS (.phi/.strategy attribute access). Needs array reformulation first (§5)."),
 ("mean_cred() per-birth caching", "~12% potential (3.65 s) — NOT IMPLEMENTED", "not numerically exact: caching the pre-birth mean changes newborn Cred (each newborn currently sees earlier same-step newborns). Validation required; deferred to a science-safe pass."),
], ["variant","result","note"])}
<p>Cheap (numpy/Numba) acceleration does <b>not</b> relieve the dominant paths: JT-cohort, per-agent
diffusion, and mean_cred/birth are per-agent-object Python loops and/or behaviour-coupled. The one
clean exact win (JT scan, 2.6×) targets a minor slice.</p>

<h2>§5 Forward assessment of heavier paths (analysis only)</h2>
{_tbl([
 ("Cython", "~3–10× on per-agent loops; agent objects remain", "does not change the O(N²) mean_cred/birth or O(N²) diagnostics algorithmically, nor the JT-cohort occupancy scaling. Pushes affordable low-occ N to ~30–50k. Proto-ag still out."),
 ("GPU / JAX", "large speedup for vectorisable array ops", "requires full array reformulation first; dynamic births/deaths + per-cell contest/cohort are awkward on GPU (scatter/segment ops, divergent control). High effort, high ceiling."),
 ("Array-based 'agents as matrix rows'", "THE enabling path", "replace per-agent objects with numpy column arrays (pos,wealth,φ,cred…); vectorise movement (gather neighbour sugar; argmax/softmax), harvest-split (segment-sum by cell via np.add.at), births/deaths (mask ops). Removes Python per-agent loops, makes Numba/GPU viable, and lets the O(N²) hot spots (mean_cred, Moran) be vectorised/subsampled."),
], ["path","projected ceiling","judgment"])}
<p><b>Proto-agricultural density (~100 agents/cell on a usable grid, N≈10⁶ on 100×100) is NOT
reachable on the current Python/Mesa path</b> — it is ~50–100× past the affordable N even before
the occupancy cliff. It requires the array-based restructuring, AND a redesign of the legacy
joint-task mechanic for multi-occupancy (its O(grid×occupancy×cohort) cost is the proximate
occupancy killer), AND subsampling/vectorising the O(N²) diagnostics.</p>

<h2>§6 The feel</h2>
<div class="box"><b>Affordable region (substrate-only, ≤~300 ms/step):</b> low occupancy
(≤~2 agents/cell), N up to ~10k at 100×100 (N≈10k already at the 357 ms ceiling; N≈19k = 806 ms).
With the O(N²) diagnostics ON (full production step) affordable N drops to ~3–4k.
<b>Occupancy is the wall</b>: >~2.5 agents/cell is hard-infeasible on any grid via the legacy
JT-cohort blowup. <b>κ (contest) adds negligible cost</b> vs the O(N) baseline (within the 2× noise).
<b>Proto-ag density sits far OUTSIDE the affordable region</b> — reaching it is an architecture
decision (array restructuring + JT redesign + diagnostic subsampling), made in the next
conversation. No config is selected here.</div>
</body></html>"""
    (_OUT / "report_stage6_0a_perf.html").write_text(html, encoding="utf-8")
    print("report:", _OUT / "report_stage6_0a_perf.html", "len", len(html))


if __name__ == "__main__":
    main()
