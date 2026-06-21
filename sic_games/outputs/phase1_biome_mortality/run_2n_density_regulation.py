"""Biome-Mortality — density-disease regulation test (the make-or-break for realistic biome mortality).

R-12: the model regulates the population via ACUTE STARVATION (the hard food brake), because r≈+3.3%
intrinsic growth meets no graded brake — the density-dependent modulators that were meant to bring r→0 at
the CC (Step-2 design, R-3) are inert (R-5…R-12 self-regulation attractor). Result: food-poor biomes get
heavy starvation mortality (arid 47% of deaths), an over-strong biome gradient that diverges from the
broadly-similar forager data.

THE TEST: turn ON density-disease (`enable_density_disease`, δ = the FREE lever) and sweep δ. Does a
calibrated δ hold the equilibrium population BELOW the food ceiling — regulating r→0 via graded DISEASE so
the **starvation fraction collapses toward 0** — or do agents spread to keep local density low and render it
inert like every other modulator? CAVEATS: δ is a calibration (not lit-anchored); `density_mult` reads
LOCAL cell density (the attractor risk). Single biome (temperate) first; multi-biome follows if it bites.
Run:  py -3 -u outputs/phase1_biome_mortality/run_2n_density_regulation.py
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
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEED = 400, 2000, 42
DELTAS = [0.0, 2.0, 4.0, 8.0, 16.0]   # density-disease free lever (0 = off / the R-12 baseline)


def run_one(delta, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))           # temperate (base knobs)
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_density_disease=(delta > 0.0),
                                                     dens_delta=delta, dens_rho_half=0.2))
    pop, starv, senesc = [], 0, 0
    for step in range(STEPS):
        w.step(); al = w.agent_list
        pop.append(len(al))
        if step >= int(0.6 * STEPS):
            starv += w.deaths_starv_this_step; senesc += w.deaths_senesc_this_step
        if not al:
            break
    tail = slice(int(0.6 * len(pop)), None)
    tot = starv + senesc
    return dict(delta=delta, eq_pop=float(np.mean(pop[tail])) if pop[-1] else 0.0,
                starv_frac=float(starv / max(tot, 1)),
                disease_deaths=senesc, starv_deaths=starv)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2n.txt")
    res = []
    for d in DELTAS:
        r = run_one(d); res.append(r)
        msg = (f"delta={d:4.0f}: eq_pop {r['eq_pop']:6.0f} | starvation {r['starv_frac']*100:4.0f}% of deaths "
               f"(disease {r['disease_deaths']}, starv {r['starv_deaths']})")
        print(f"[2n] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2n: {msg} | elapsed {time.time()-t0:.0f}s\n")

    base = res[0]                                          # delta=0 = food-ceiling / starvation-regulated baseline
    # works if a delta drops eq_pop meaningfully below the ceiling AND collapses the starvation fraction
    best = min(res[1:], key=lambda r: r["starv_frac"]) if len(res) > 1 else base
    regulates = best["starv_frac"] < 0.5 * max(base["starv_frac"], 0.01) and best["eq_pop"] < 0.85 * base["eq_pop"]
    if regulates:
        verdict = (f"DENSITY-DISEASE REGULATES — at delta={best['delta']:.0f} the population settles "
                   f"{best['eq_pop']:.0f} (vs {base['eq_pop']:.0f} food-ceiling baseline) and the starvation fraction "
                   f"collapses {base['starv_frac']*100:.0f}%→{best['starv_frac']*100:.0f}%. Graded disease holds r→0 "
                   f"BELOW the food ceiling — the Step-2 design works; mortality becomes disease-regulated, not "
                   f"starvation. (delta is a calibration, large; multi-biome next.)")
    else:
        worst = res[-1]
        verdict = (f"DENSITY-DISEASE INERT (the attractor wins) — even at delta={worst['delta']:.0f} the starvation "
                   f"fraction is {worst['starv_frac']*100:.0f}% (baseline {base['starv_frac']*100:.0f}%) and eq_pop "
                   f"{worst['eq_pop']:.0f} vs {base['eq_pop']:.0f}. Agents spread to keep LOCAL cell density low so "
                   f"density_mult stays ~1 — the same wash-out as R-5…R-12. Density measured per-cell can't "
                   f"regulate; would need a coarser-scale density or a different brake.")

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    ds = [r["delta"] for r in res]
    ax[0].plot(ds, [r["eq_pop"] for r in res], "o-", color="#3182ce")
    ax[0].axhline(base["eq_pop"], color="#e53e3e", ls="--", lw=0.8, label="food ceiling (δ=0)")
    ax[0].set_xlabel("density-disease δ (free lever)"); ax[0].set_ylabel("equilibrium population")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25); ax[0].set_title("Does disease hold the pop below the food ceiling?")
    ax[1].plot(ds, [r["starv_frac"] * 100 for r in res], "o-", color="#dd6b20")
    ax[1].set_xlabel("density-disease δ (free lever)"); ax[1].set_ylabel("% of deaths = starvation")
    ax[1].grid(alpha=0.25); ax[1].set_title("Does starvation give way to graded disease?")
    figs["sweep"] = fig_b64(fig)

    results = dict(verdict=verdict, regulates=regulates,
                   conditions=[{k: r[k] for k in ("delta", "eq_pop", "starv_frac", "disease_deaths", "starv_deaths")} for r in res],
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2n.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, regulates)
    print(f"[2n] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, regulates):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(f"<tr><td>{r['delta']:.0f}</td><td>{r['eq_pop']:.0f}</td><td>{r['starv_frac']*100:.0f}%</td>"
                   f"<td>{r['disease_deaths']}</td><td>{r['starv_deaths']}</td></tr>" for r in res)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Biome-Mortality — density-disease regulation</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Biome-Mortality · density-disease regulation test</h1>
<p>Can a calibrated density-disease lever (δ) hold the population BELOW the food ceiling so r→0 via graded
disease and starvation collapses — or do agents dodge local density (R-5 attractor)? Temperate biome,
{STEPS} steps. δ=0 is the R-12 starvation-regulated baseline.</p>
<div class="box {'ok' if regulates else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>δ</th><th>eq pop</th><th>% starvation</th><th>disease deaths</th><th>starv deaths</th></tr>{rows}</table>
<h2>Population vs food ceiling · starvation vs disease</h2><div class="fig">{img('sweep')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">{time.strftime('%Y-%m-%d')} · δ is a calibration
(free lever, not lit-anchored); density_mult reads local cell density · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2n.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
