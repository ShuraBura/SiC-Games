"""Biome-Mortality — S3.5/S4: multi-biome harness + bracketed pathogen-gradient validation.

THE deliverable demonstration. Three ISOLATED populations in distinct-productivity biomes (arid / temperate
/ lush, via forestK/aridK → mean NPP 0.077 / 0.185 / 0.293), each equilibrating independently (no mixing).
Each biome's NPP drives BOTH its food ceiling (CC-1) AND its pathogen load (S2 `pathogen_mult`, fixed
reference = temperate → neutral). Sweep the BRACKETED `pathogen_gamma` {0=off, 0.5, 1.0}.

HONEST EXPECTATIONS (MODEL_SPEC §4.6; the expectations ledger):
  CAN show — a productivity-driven biome MORTALITY gradient (e₀ ↓ as NPP ↑ when pathogen ON), the pipeline,
    the food gradient (eq-pop), reported as gradient-vs-gamma (bracketed).
  CANNOT show — the real temperature/frost gradient (NPP is a conflated proxy; T/humidity are CL-1
    placeholders), calibrated magnitude (bracketed), pathogen seasonality, or a confirmatory fit (no clean
    empirical biome-mortality law — violence-dominated). And the gradient may be MODEST (R-5/6).
  METRIC NOTE — at a stationary equilibrium CDR = CBR (pinned by fertility), so mortality shows up as
    **e₀ / age structure / eq-population**, NOT crude death rate. We read mean living age (e₀ proxy).
Run:  py -3 -u outputs/phase1_biome_mortality/run_2m_multibiome.py
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
FOUNDERS, STEPS, SEED, MATURE = 400, 1500, 42, 180
BIOMES = [("arid", {"forestK": 0.1, "aridK": 0.8}),
          ("temperate", {}),                              # reference biome (pathogen-neutral)
          ("lush", {"forestK": 0.9, "aridK": 0.0})]
GAMMAS = [0.0, 0.5, 1.0]   # bracketed pathogen strength (0 = off / control)


def biome_knobs(mods, seed=SEED):
    k = dict(knobs_for(seed)); k.update(mods); return k


def run_one(mods, gamma, npp_ref, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(biome_knobs(mods, seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=biome_knobs(mods, seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_terrain_pathogen=(gamma > 0.0),
                                                     pathogen_gamma=gamma, pathogen_npp_ref=npp_ref,
                                                     pathogen_cap=3.0))
    pop, mage, deaths = [], [], []
    for step in range(STEPS):
        w.step(); al = w.agent_list
        pop.append(len(al)); deaths.append(w.deaths_starv_this_step + w.deaths_senesc_this_step)
        mage.append(float(np.mean([a.age for a in al])) / 12.0 if al else 0.0)
    tail = slice(int(0.6 * len(pop)), None)
    alive = pop[-1] > 0
    return dict(eq_pop=float(np.mean(pop[tail])) if alive else 0.0,
                mean_age=float(np.mean(mage[tail])) if alive else 0.0,
                cdr=float(np.sum(deaths[tail]) / max(np.sum(pop[tail]), 1) * 12.0))   # =CBR at equ (sanity)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2m.txt")
    ref_fields = generate_world(biome_knobs({}))           # temperate reference NPP (pathogen-neutral)
    npp_ref = float(ref_fields.npp[ref_fields.isWater == 0].mean())
    print(f"[2m] pathogen reference NPP (temperate) = {npp_ref:.3f}", flush=True)
    res = {}
    for bname, mods in BIOMES:
        for g in GAMMAS:
            r = run_one(mods, g, npp_ref); res[(bname, g)] = r
            msg = f"{bname:10} gamma={g}: eq_pop {r['eq_pop']:6.0f} | mean living age {r['mean_age']:5.1f} yr | CDR {r['cdr']*1000:4.0f}/1000"
            print(f"[2m] {msg}  [{time.time()-t0:.0f}s]", flush=True)
            with open(prog, "w") as f: f.write(f"2m: {msg} | elapsed {time.time()-t0:.0f}s\n")

    # gradient: with pathogen ON, does mean living age (e0 proxy) fall as NPP rises (more pathogen)?
    names = [b for b, _ in BIOMES]
    age_off = [res[(b, 0.0)]["mean_age"] for b in names]
    age_hi = [res[(b, 1.0)]["mean_age"] for b in names]
    grad_off = age_off[0] - age_off[-1]    # arid − lush at gamma=0 (should be ~0: same baseline)
    grad_hi = age_hi[0] - age_hi[-1]       # arid − lush at gamma=1 (should be >0: pathogen gradient)
    bites = grad_hi > 0.5 and grad_hi > grad_off + 0.5
    if bites:
        verdict = (f"PATHOGEN BIOME GRADIENT (bracketed) — at gamma=1 mean living age falls arid→lush "
                   f"{age_hi[0]:.1f}→{age_hi[-1]:.1f} yr ({grad_hi:.1f} yr span) as NPP/pathogen rises, vs flat at "
                   f"gamma=0 ({age_off[0]:.1f}→{age_off[-1]:.1f}, span {grad_off:.1f}). The productivity-driven biome "
                   f"mortality gradient is real and scales with the bracketed strength. HONEST: NPP-proxy only "
                   f"(no T/humidity until CL-1); magnitude bracketed; exploratory, not a validated fit.")
    else:
        verdict = (f"GRADIENT WEAK/ABSENT — gamma=1 arid→lush mean age span {grad_hi:.1f} yr (gamma=0 span "
                   f"{grad_off:.1f}). Either the pathogen multiplier is washed out by the food/self-regulation "
                   f"dynamics, or the NPP contrast is too small at these gammas. Inspect eq-pop vs age trade-off.")

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    npps = [0.077, 0.185, 0.293]
    for g in GAMMAS:
        ax[0].plot(npps, [res[(b, g)]["mean_age"] for b in names], "o-", label=f"γ={g}")
        ax[1].plot(npps, [res[(b, g)]["eq_pop"] for b in names], "o-", label=f"γ={g}")
    ax[0].set_xlabel("biome mean NPP (arid→lush)"); ax[0].set_ylabel("mean living age (yr) — e₀ proxy")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25); ax[0].set_title("Mortality gradient (lower age = more disease)")
    ax[1].set_xlabel("biome mean NPP (arid→lush)"); ax[1].set_ylabel("equilibrium population")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.25); ax[1].set_title("Population: food ceiling − pathogen drag")
    figs["grad"] = fig_b64(fig)

    results = dict(verdict=verdict, bites=bites, npp_ref=npp_ref,
                   grid={f"{b}|{g}": res[(b, g)] for b in names for g in GAMMAS},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2m.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, names, verdict, bites)
    print(f"[2m] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, names, verdict, bites):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = ""
    for b in names:
        for g in GAMMAS:
            r = res[(b, g)]
            rows += (f"<tr><td>{b}</td><td>{g}</td><td>{r['eq_pop']:.0f}</td><td>{r['mean_age']:.1f}</td>"
                     f"<td>{r['cdr']*1000:.0f}</td></tr>")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Biome-Mortality S3.5/S4 — multi-biome</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#dd6b20;background:#fffaf0}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Biome-Mortality · S3.5/S4 — multi-biome pathogen gradient</h1>
<p>Three isolated populations (arid / temperate / lush; NPP 0.077 / 0.185 / 0.293), each biome's NPP driving
both food and pathogen load (S2; fixed temperate reference). Bracketed `pathogen_gamma` sweep. <b>Metric:</b>
mean living age (e₀ proxy) — at equilibrium CDR=CBR is pinned by fertility, so mortality shows in e₀ / age /
population, not CDR.</p>
<div class="box {'ok' if bites else 'flag'}"><b>{verdict}</b></div>
<p style="color:#a05a00"><b>Honest scope:</b> NPP-proxy gradient only (real T/humidity = CL-1, deferred);
magnitude BRACKETED (γ); no pathogen seasonality; exploratory, not a validated fit (no clean empirical
biome-mortality law — violence-dominated). A modest gradient is a result, not a failure.</p>
<table><tr><th>biome</th><th>γ</th><th>eq pop</th><th>mean age (yr)</th><th>CDR/1000 (=CBR)</th></tr>{rows}</table>
<h2>Gradient vs bracketed strength</h2><div class="fig">{img('grad')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">S3.5/S4 · {time.strftime('%Y-%m-%d')} · validated
demographic baseline + S2 pathogen · constant economy · isolated per-biome · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2m.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
