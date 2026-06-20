"""Resource-Ecology — Phase A.2: DEPLETION (the trap).

A.1 (R-6): uniform seasonality regulates the CC to the lean-season bottleneck but does NOT create
nutritional stress — the population self-adjusts and stays fed. The red-team's fix: depletion. A cell
holds a freshness `f∈[0,1]` (= fraction of standing stock); harvest pressure draws it down, it regrows
slowly, so a heavily-used region STAYS depleted and agents in it cannot instantly flee to a fresh cell.

THE TEST: does depletion create PER-AGENT scarcity — a spread of `synergy_mult` across agents (some on
depleted cells under-fed → synergy > 1) — that uniform seasonality could not? (red-team A: the per-agent
variance the modulators need.)

[PROVISIONAL: depletion-lite — the stock magnitude / regrow rate are provisional pending CC-1; tagged.]
Run:  py -3 -u outputs/phase1_resource_ecology/run_2e_depletion.py
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
FOUNDERS, STEPS, SEED, PERIOD = 400, 2500, 42, 12
DEPLETE_RATE, REGROW_RATE = 0.30, 0.10   # [PROVISIONAL] occupied cells deplete faster than they regrow


class DepletableSeasonalCapacity:
    """CC-1 capacity × seasonal s(t) × per-cell freshness f (depletes under harvest, regrows slowly)."""
    def __init__(self, fields, s_min, deplete_rate=DEPLETE_RATE, regrow_rate=REGROW_RATE):
        self.width = self.height = N
        dens = np.minimum(DENS_CAP, DENS_SLOPE * fields.npp_gm2 / NPP_THRESH)
        self.K = dens * CELL_KM2
        E = self.K * BURN
        self.mask = np.zeros((N, N), bool); self.mask[Y0:Y0 + PATCH, X0:X0 + PATCH] = True
        E[~self.mask] = 0.0
        self._E = E; self.s_min = s_min; self.t = 0
        self.f = np.ones((N, N)); self.deplete_rate = deplete_rate; self.regrow_rate = regrow_rate
        self.ceiling = float(self.K[self.mask & (fields.isWater == 0)].sum())
    def season(self):
        return self.s_min + (1.0 - self.s_min) * 0.5 * (1.0 + math.cos(2 * math.pi * self.t / PERIOD))
    def level(self, x, y): return float(self._E[y, x] * self.f[y, x] * self.season())
    def harvest(self, x, y): return self.level(x, y)
    def consume(self, occ_count):
        for (x, y), n in occ_count.items():           # deplete occupied cells ∝ harvest pressure (occ/K)
            pressure = min(1.0, n / max(self.K[y, x], 0.5))
            self.f[y, x] = max(0.05, self.f[y, x] - self.deplete_rate * pressure)
        self.f += self.regrow_rate * (1.0 - self.f)   # regrow all (logistic toward 1)
        np.clip(self.f, 0.05, 1.0, out=self.f)


def run_one(s_min, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = DepletableSeasonalCapacity(fields, s_min)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=True))
    pop, deaths, syn_mean, syn_frac, fresh = [], [], [], [], []
    for step in range(STEPS):
        cap.t = step
        w.step()
        al = w.agent_list
        pop.append(len(al)); deaths.append(w.deaths_starv_this_step + w.deaths_senesc_this_step)
        if al:
            s = np.array([synergy_mult(a._fed_reserve, a.reserve_floor, 100000, 2.5) for a in al])
            syn_mean.append(float(s.mean())); syn_frac.append(float(np.mean(s > 1.2)))
            fresh.append(float(cap.f[cap.mask].mean()))
        else:
            break
    tail = slice(int(0.6 * len(pop)), None)
    return dict(s_min=s_min, ceiling=cap.ceiling, pop=pop, deaths=deaths, syn_mean=syn_mean,
                syn_frac=syn_frac, fresh=fresh,
                eq_pop=float(np.mean(pop[tail])) if pop[-1] else 0.0,
                synmean_eq=float(np.mean(syn_mean[tail])) if pop[-1] else 1.0,
                synfrac_eq=float(np.mean(syn_frac[tail])) if pop[-1] else 0.0,
                synmax_eq=float(np.max(syn_mean[tail])) if pop[-1] else 1.0,
                fresh_eq=float(np.mean(fresh[tail])) if pop[-1] else 1.0)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2e.txt")
    res = {}
    for name, s_min in (("depletion only (s=1)", 1.0), ("seasonal×depletion (s=0.4)", 0.4)):
        r = run_one(s_min); res[name] = r
        msg = (f"{name}: eq_pop {r['eq_pop']:.0f} ({100*r['eq_pop']/r['ceiling']:.0f}% peak) | "
               f"synergy mean {r['synmean_eq']:.2f} | frac>1.2 {r['synfrac_eq']*100:.0f}% | "
               f"freshness {r['fresh_eq']:.2f}")
        print(f"[2e] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2e: {msg} | elapsed {time.time()-t0:.0f}s\n")

    # the trap test: does depletion create PER-AGENT scarcity (a non-trivial fraction with synergy>1.2)?
    bites = any(r["synfrac_eq"] > 0.05 for r in res.values())
    verdict = ("DEPLETION BITES — per-agent scarcity appears (a fraction of agents under-fed → synergy "
               "fires per-agent), which seasonality alone could not produce. The modulators are LIVE."
               if bites else
               "DEPLETION INERT — agents still dodge to fresh cells; synergy ~1 across agents. The trap is "
               "too weak (raise deplete/regrow ratio) or movement still escapes it.")

    figs = {}
    fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    cols = {"depletion only (s=1)": "#dd6b20", "seasonal×depletion (s=0.4)": "#3182ce"}
    for name, r in res.items():
        yr = np.arange(len(r["pop"])) / 12.0
        ax[0].plot(yr, r["pop"], color=cols[name], lw=1.0, label=name)
        ax[1].plot(np.arange(len(r["synfrac"])) / 12.0 if False else np.arange(len(r["syn_frac"])) / 12.0,
                   np.array(r["syn_frac"]) * 100, color=cols[name], lw=1.0)
        ax[2].plot(np.arange(len(r["fresh"])) / 12.0, r["fresh"], color=cols[name], lw=1.0)
    ax[0].axhline(res["depletion only (s=1)"]["ceiling"], color="k", ls="--", lw=0.7, label="peak ceiling")
    ax[0].set_ylabel("population"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[1].set_ylabel("% agents synergy>1.2\n(under-fed)"); ax[1].grid(alpha=0.25)
    ax[2].set_ylabel("mean cell freshness"); ax[2].set_xlabel("year"); ax[2].grid(alpha=0.25)
    ax[0].set_title("Phase A.2 — does depletion create per-agent scarcity? (synergy ON)")
    figs["ts"] = fig_b64(fig)

    results = dict(verdict=verdict, bites=bites, deplete_rate=DEPLETE_RATE, regrow_rate=REGROW_RATE,
                   conditions={n: {k: r[k] for k in ("eq_pop", "ceiling", "synmean_eq", "synfrac_eq",
                                                     "synmax_eq", "fresh_eq")} for n, r in res.items()},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2e.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, bites)
    print(f"[2e] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, bites):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['eq_pop']:.0f}</td><td>{100*r['eq_pop']/r['ceiling']:.0f}%</td>"
        f"<td>{r['synmean_eq']:.2f}</td><td>{r['synfrac_eq']*100:.0f}%</td><td>{r['fresh_eq']:.2f}</td></tr>"
        for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Resource-Ecology A.2 — depletion</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Resource-Ecology · Phase A.2 — depletion (the trap)</h1>
<p>Per-cell freshness `f` depletes under harvest pressure (rate {DEPLETE_RATE}) and regrows slowly (rate
{REGROW_RATE}), so a used region stays depleted and can't be instantly fled. synergy ON, 40×40 sub-window,
seed {SEED}, {STEPS} steps. <b>Test:</b> does this create PER-AGENT scarcity (some agents under-fed →
synergy fires) that uniform seasonality (A.1) could not? [depletion-lite — PROVISIONAL pending CC-1.]</p>
<div class="box {'ok' if bites else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>eq. pop</th><th>% peak ceiling</th><th>synergy mean</th><th>% under-fed (synergy&gt;1.2)</th><th>mean freshness</th></tr>{rows}</table>
<h2>Population · % under-fed · cell freshness over time</h2><div class="fig">{img('ts')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">A.2 · {time.strftime('%Y-%m-%d')} · depletion-lite
(provisional stock/regrow; CC-1 sets the real magnitude) · forage-only · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2e.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
