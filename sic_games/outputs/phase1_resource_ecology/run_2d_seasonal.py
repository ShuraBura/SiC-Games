"""Resource-Ecology — Phase A.1: SEASONALITY (net-new TerrainField seasonal path).

The 2b/2c red-team: on a CONSTANT economy the demographic a2 modulators are inert (agents fully fed).
Phase A.1 adds a seasonal multiplier `s(t)` on the harvest so a lean season can push S/n below burn.
THE TEST (red-team A): does the seasonal trough actually draw reserves down AT EQUILIBRIUM (occ/K≈1,
where S/n≈burn), making synergy fire and a seasonal mortality pulse appear — or do agents stay fed?

NOTE: this is the UNIFORM seasonal signal — it does not change cell ranking, so it produces a TEMPORAL
reserve oscillation (a seasonal mortality pulse), NOT per-agent variance. Per-agent variance (some agents
trapped leaner than others) needs depletion (Phase A.2) — the red-team's point. A.1 tests whether
seasonality bites at all + delivers the seasonal pulse.

Run:  py -3 -u outputs/phase1_resource_ecology/run_2d_seasonal.py
"""
from __future__ import annotations
import base64, io, json, math, os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig, synergy_mult
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import N, generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_spec = _iu.spec_from_file_location("r2pre", _p); _r2 = _iu.module_from_spec(_spec); _spec.loader.exec_module(_r2)
knobs_for, patch_positions = _r2.knobs_for, _r2.patch_positions
X0, Y0, PATCH, BURN = _r2.X0, _r2.Y0, _r2.PATCH, _r2.BURN
NPP_THRESH, DENS_SLOPE, DENS_CAP, CELL_KM2 = _r2.NPP_THRESH, _r2.DENS_SLOPE, _r2.DENS_CAP, _r2.CELL_KM2

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEED, PERIOD = 400, 2500, 42, 12  # 12 steps = 1 year


class SeasonalCapacity:
    """CC-1 capacity field × a UNIFORM seasonal multiplier s(t) ∈ [s_min, 1] (annual cosine).
    s_min=1.0 → constant (the control). The harness sets `.t` before each model step."""
    def __init__(self, fields, s_min):
        self.width = self.height = N
        dens = np.minimum(DENS_CAP, DENS_SLOPE * fields.npp_gm2 / NPP_THRESH)
        E = dens * CELL_KM2 * BURN
        mask = np.zeros((N, N), bool); mask[Y0:Y0 + PATCH, X0:X0 + PATCH] = True
        E[~mask] = 0.0
        self._E = E; self.s_min = s_min; self.t = 0
        self.ceiling = float((dens * CELL_KM2)[mask & (fields.isWater == 0)].sum())
    def season(self):                      # 1 at peak (t=0), s_min at trough (t=period/2)
        return self.s_min + (1.0 - self.s_min) * 0.5 * (1.0 + math.cos(2 * math.pi * self.t / PERIOD))
    def level(self, x, y): return float(self._E[y, x] * self.season())
    def harvest(self, x, y): return self.level(x, y)


def run_one(s_min, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SeasonalCapacity(fields, s_min)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=True))
    pop, res, deaths, syn, seas = [], [], [], [], []
    for step in range(STEPS):
        cap.t = step
        w.step()
        al = w.agent_list
        pop.append(len(al))
        deaths.append(w.deaths_starv_this_step + w.deaths_senesc_this_step)
        if al:
            fed = np.array([a._fed_reserve for a in al])
            res.append(float(fed.mean()))
            syn.append(float(np.mean([synergy_mult(a._fed_reserve, a.reserve_floor, 100000, 2.5) for a in al])))
        else:
            res.append(0.0); syn.append(1.0); break
        seas.append(cap.season())
    tail = slice(int(0.6 * len(pop)), None)
    return dict(s_min=s_min, ceiling=cap.ceiling, pop=pop, res=res, deaths=deaths, syn=syn, seas=seas,
                eq_pop=float(np.mean(pop[tail])) if pop[-1] else 0.0,
                res_min=float(np.min(res[tail])) if pop[-1] else 0.0,
                res_max=float(np.max(res[tail])) if pop[-1] else 0.0,
                syn_max=float(np.max(syn[tail])) if pop[-1] else 1.0,
                syn_mean=float(np.mean(syn[tail])) if pop[-1] else 1.0)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2d.txt")
    res = {}
    for name, s_min in (("constant (control)", 1.0), ("seasonal (s_min=0.4)", 0.4)):
        r = run_one(s_min); res[name] = r
        msg = (f"{name}: eq_pop {r['eq_pop']:.0f} ({100*r['eq_pop']/r['ceiling']:.0f}% peak-ceiling) | "
               f"reserve {r['res_min']:.0f}–{r['res_max']:.0f} | synergy mean {r['syn_mean']:.2f} max {r['syn_max']:.2f}")
        print(f"[2d] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2d: {msg} | elapsed {time.time()-t0:.0f}s\n")

    bites = res["seasonal (s_min=0.4)"]["syn_max"] > 1.2  # does the lean season make synergy fire?
    verdict = ("SEASONALITY BITES — the lean season draws reserves down at equilibrium and synergy fires "
               "(temporal pulse). Per-agent variance still needs depletion (Phase A.2)."
               if bites else
               "SEASONALITY INERT — even at equilibrium the trough does not draw reserves below maintenance; "
               "synergy stays ~1. Depletion (A.2) is required.")

    figs = {}
    fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    cols = {"constant (control)": "#718096", "seasonal (s_min=0.4)": "#3182ce"}
    for name, r in res.items():
        yr = np.arange(len(r["pop"])) / 12.0
        ax[0].plot(yr, r["pop"], color=cols[name], lw=1.0, label=name)
        ax[1].plot(yr, r["res"], color=cols[name], lw=1.0)
        ax[2].plot(np.arange(len(r["syn"])) / 12.0, r["syn"], color=cols[name], lw=1.0)
    ax[0].axhline(res["constant (control)"]["ceiling"], color="k", ls="--", lw=0.7, label="peak food ceiling")
    ax[0].set_ylabel("population"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[1].axhline(20000, color="#e53e3e", ls=":", lw=0.8); ax[1].axhline(100000, color="#38a169", ls=":", lw=0.6)
    ax[1].set_ylabel("mean fed reserve"); ax[1].grid(alpha=0.25)
    ax[2].axhline(1.0, color="#999", ls=":", lw=0.8)
    ax[2].set_ylabel("mean synergy_mult"); ax[2].set_xlabel("year"); ax[2].grid(alpha=0.25)
    ax[0].set_title("Phase A.1 — does seasonality bite at equilibrium? (synergy ON)")
    figs["ts"] = fig_b64(fig)

    results = dict(verdict=verdict, bites=bites,
                   conditions={n: {k: r[k] for k in ("eq_pop", "ceiling", "res_min", "res_max",
                                                     "syn_mean", "syn_max")} for n, r in res.items()},
                   s_min=0.4, founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2d.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, bites)
    print(f"[2d] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, bites):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['eq_pop']:.0f}</td><td>{100*r['eq_pop']/r['ceiling']:.0f}%</td>"
        f"<td>{r['res_min']:.0f}–{r['res_max']:.0f}</td><td>{r['syn_mean']:.2f}</td><td>{r['syn_max']:.2f}</td></tr>"
        for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Resource-Ecology A.1 — seasonality</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Resource-Ecology · Phase A.1 — seasonality (the unblock test)</h1>
<p>Net-new TerrainField seasonal multiplier `s(t)` (uniform annual cosine, s_min=0.4), synergy ON, 40×40
sub-window, seed {SEED}, {STEPS} steps. <b>Test:</b> at equilibrium (occ/K≈1, S/n≈burn), does the lean
season push intake below maintenance so reserves draw down and synergy fires?</p>
<div class="box {'ok' if bites else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>eq. pop</th><th>% peak ceiling</th><th>reserve range</th><th>synergy mean</th><th>synergy max</th></tr>{rows}</table>
<p>Reserve oscillating toward the floor in the lean season + synergy_mult rising above 1 = seasonality
bites. Flat reserve at 100k + synergy ~1 = still inert (agents stay fed → depletion needed, A.2).</p>
<h2>Population · reserve · synergy over time</h2><div class="fig">{img('ts')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">A.1 · {time.strftime('%Y-%m-%d')} · UNIFORM seasonal
(temporal pulse only; per-agent variance needs depletion A.2) · provisional s_min; forage-only.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2d.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
