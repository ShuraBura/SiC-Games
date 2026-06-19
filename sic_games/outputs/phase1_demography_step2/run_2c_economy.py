"""Demographic stage — Step 2, Tier-0: FOOD-ECONOMY fix comparison (red-team 2b prerequisite).

The 2b red-team found the scramble economy (S/n, no per-capita floor) pins every adult at the
starvation floor (mean reserve ~25k of a 20k–100k band), which saturates the nutrition-synergy and
makes μ_max impossible to calibrate. This harness tests two fixes head-to-head — which produces a
REALISTIC equilibrium reserve (well above the floor) at a sensible carrying capacity:

  A — energetic fertility: births scale with maternal reserve → the population caps BEFORE reserves
      drain to the floor.
  B — density-disease as the population cap: occupancy-driven mortality (re-anchored ρ_half) caps the
      population below the food ceiling.

Synergy is OFF in all conditions (we are fixing the economy so synergy can be calibrated LATER).
Run:  py -3 -u outputs/phase1_demography_step2/run_2c_economy.py
"""
from __future__ import annotations
import base64, io, json, os, time
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
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_spec = _iu.spec_from_file_location("r2pre", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                          "run_2a_pre.py"))
_r2 = _iu.module_from_spec(_spec); _spec.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEED = 400, 2000, 42
FLOOR, FULL = 20_000.0, 100_000.0
CONDITIONS = {
    "baseline (scramble)": dict(),
    "A: energetic fertility": dict(enable_energetic_fertility=True),
    "B: density-cap": dict(enable_density_disease=True, dens_rho_half=0.05, dens_delta=2.0),
    "A+B": dict(enable_energetic_fertility=True, enable_density_disease=True,
                dens_rho_half=0.05, dens_delta=2.0),
}


def run_one(flags, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos, demography_cfg=DemographyConfig(**flags))
    pop, res = [], []
    for _ in range(STEPS):
        w.step()
        al = w.agent_list
        pop.append(len(al))
        res.append(float(np.mean([a.wealth for a in al])) if al else 0.0)
        if not al:
            break
    tail = slice(int(0.85 * len(pop)), None)
    eq_pop = float(np.mean(pop[tail])) if pop[-1] else 0.0
    eq_res = float(np.mean(res[tail])) if pop[-1] else 0.0
    wealths = np.array([a.wealth for a in w.agent_list], float)
    frac_above_50k = float(np.mean(wealths > 50_000)) if wealths.size else 0.0
    frac_near_floor = float(np.mean(wealths < 25_000)) if wealths.size else 0.0
    # stationarity: slope of last-15% pop (≈0 ⇒ settled)
    t = np.arange(len(pop))[tail]
    slope = float(np.polyfit(t, np.array(pop)[tail], 1)[0]) if pop[-1] and len(t) > 5 else float("nan")
    return dict(eq_pop=eq_pop, eq_res=eq_res, ceiling=cap.ceiling, frac_above_50k=frac_above_50k,
                frac_near_floor=frac_near_floor, slope=slope, pop=pop, res=res)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time()
    prog = os.path.join(OUT, "progress_2c.txt")
    res = {}
    for i, (name, flags) in enumerate(CONDITIONS.items()):
        r = run_one(flags)
        res[name] = r
        # "healthy" = mean equilibrium reserve well above floor (reserve fraction of band > 0.4)
        rfrac = (r["eq_res"] - FLOOR) / (FULL - FLOOR)
        msg = (f"{name}: eq_pop {r['eq_pop']:.0f} ({100*r['eq_pop']/r['ceiling']:.0f}% ceiling) | "
               f"eq_reserve {r['eq_res']:.0f} (band {rfrac:.2f}) | >50k {r['frac_above_50k']*100:.0f}% | "
               f"near-floor {r['frac_near_floor']*100:.0f}% | slope {r['slope']:+.1f}")
        print(f"[2c] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f:
            f.write(f"2c: {i+1}/{len(CONDITIONS)} | {msg} | elapsed {time.time()-t0:.0f}s\n")

    def healthy(r): return (r["eq_res"] - FLOOR) / (FULL - FLOOR) > 0.40 and r["eq_pop"] > 0
    winners = [n for n, r in res.items() if healthy(r)]

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    for name, r in res.items():
        yr = np.arange(len(r["pop"])) / 12.0
        ax[0].plot(yr, r["pop"], lw=1.1, label=name)
        ax[1].plot(yr, r["res"], lw=1.1, label=name)
    ax[0].axhline(res["baseline (scramble)"]["ceiling"], color="k", ls="--", lw=0.8, label="food ceiling")
    ax[0].set_title("population"); ax[0].set_xlabel("year"); ax[0].set_ylabel("pop"); ax[0].grid(alpha=0.25); ax[0].legend(fontsize=7)
    ax[1].axhline(FLOOR, color="#e53e3e", ls=":", lw=0.9, label="starvation floor")
    ax[1].axhline(FULL, color="#38a169", ls=":", lw=0.7, label="full")
    ax[1].set_title("mean reserve (the pathology test)"); ax[1].set_xlabel("year"); ax[1].set_ylabel("kcal")
    ax[1].grid(alpha=0.25); ax[1].legend(fontsize=7)
    figs["main"] = fig_b64(fig)

    results = dict(winners=winners, floor=FLOOR, full=FULL,
                   conditions={n: dict(eq_pop=r["eq_pop"], pct_ceiling=100 * r["eq_pop"] / r["ceiling"],
                                       eq_reserve=r["eq_res"], reserve_band_frac=(r["eq_res"] - FLOOR) / (FULL - FLOOR),
                                       frac_above_50k=r["frac_above_50k"], frac_near_floor=r["frac_near_floor"],
                                       slope=r["slope"]) for n, r in res.items()},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2c.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, winners)
    print(f"[2c] done in {time.time()-t0:.0f}s. healthy-reserve condition(s): {winners or 'NONE'}.", flush=True)


def _write_html(figs, res, winners):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['eq_pop']:.0f}</td><td>{100*r['eq_pop']/r['ceiling']:.0f}%</td>"
        f"<td>{r['eq_res']:.0f}</td><td>{(r['eq_res']-20000)/80000:.2f}</td>"
        f"<td>{r['frac_above_50k']*100:.0f}%</td><td>{r['frac_near_floor']*100:.0f}%</td></tr>"
        for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>2c economy-fix comparison</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282;margin-top:28px}}
.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Demographic stage · 2c — food-economy fix comparison (Tier-0)</h1>
<p>The 2b red-team prerequisite: the scramble economy pins reserves at the starvation floor (~25k of a
20k–100k band), saturating synergy and blocking μ_max calibration. <b>Which fix gives a realistic
equilibrium reserve?</b> Synergy OFF in all. 40×40 sub-window, seed {SEED}, {STEPS} steps.</p>
<div class="box {'ok' if winners else 'flag'}"><b>Healthy-reserve condition(s): {', '.join(winners) if winners else 'NONE'}</b>
(criterion: mean equilibrium reserve > 40% of the floor→full band, i.e. > 52k).</div>
<table><tr><th>condition</th><th>eq. pop</th><th>% ceiling</th><th>eq. reserve</th><th>band frac</th><th>&gt;50k</th><th>near-floor</th></tr>{rows}</table>
<p>The <b>reserve</b> columns are the test: baseline should sit near the floor (band ~0.06, near-floor ~100%);
a working fix lifts mean reserve well above the floor so the population isn't chronically starving.</p>
<h2>Population &amp; reserve trajectories</h2><div class="fig">{img('main')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">2c · {time.strftime('%Y-%m-%d')} · synergy OFF;
first-pass (1 seed); the winning economy fix becomes the base for μ_max calibration (Tier-2).</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2c.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
