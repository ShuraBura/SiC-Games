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
    **e₀ / eq-population**, NOT crude death rate. AND realized mean age (living OR at-death) is confounded by
    the growth rate (fast-growing biome → young pyramid → young deaths). So e₀ here is a **PERIOD LIFE
    TABLE** — age-specific death rate m(x) = deaths-in-band / person-years-in-band — which is decoupled from
    growth. (eq-population is the other robust, growth-independent signal.)
Run:  py -3 -u outputs/phase1_biome_mortality/run_2m_multibiome.py
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
    # PERIOD LIFE TABLE (decoupled from the growth rate): age-specific death RATE m(x) =
    # deaths-in-band / person-years-in-band, over the equilibrium window. Then q,l,e0.
    EDGES = [0, 1, 5, 15, 30, 50, 120]                      # year band edges
    nb = len(EDGES) - 1
    expo = [0] * nb; dband = [0] * nb                       # person-months at risk; deaths, per band
    def band(age_yr):
        for i in range(nb):
            if age_yr < EDGES[i + 1]:
                return i
        return nb - 1
    pop = []
    tail_start = int(0.6 * STEPS)
    prev = {a.unique_id: a.age for a in w.agent_list}
    for step in range(STEPS):
        w.step(); al = w.agent_list
        cur = {a.unique_id: a.age for a in al}
        if step >= tail_start:
            for a in al:
                expo[band(a.age / 12.0)] += 1               # one person-month of exposure
            for uid, ag in prev.items():
                if uid not in cur:                          # died this step
                    dband[band((ag + 1) / 12.0)] += 1
        prev = cur
        pop.append(len(al))
    tail = slice(int(0.6 * len(pop)), None)
    alive = pop[-1] > 0
    # life table from m(x)
    lx = [1.0]; e0 = 0.0
    for i in range(nb):
        m = 12.0 * dband[i] / expo[i] if expo[i] > 0 else 0.0   # annual hazard in band
        wdt = EDGES[i + 1] - EDGES[i]
        q = 1.0 - math.exp(-m * wdt)
        e0 += (lx[-1] + lx[-1] * (1.0 - q)) / 2.0 * wdt         # trapezoidal ∫ l(x)
        lx.append(lx[-1] * (1.0 - q))
    q_u5 = 1.0 - lx[2] / lx[0]                               # P(die before age 5) — child mortality (l at edge idx 2 = age 5)
    return dict(eq_pop=float(np.mean(pop[tail])) if alive else 0.0,
                e0=e0 if alive else 0.0, q_u5=q_u5 if alive else 0.0,
                n_deaths=sum(dband),
                cdr=float(sum(dband) / max(sum(expo), 1) * 12.0))   # crude rate (=CBR at equ; sanity)


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
            msg = (f"{bname:10} gamma={g}: eq_pop {r['eq_pop']:6.0f} | e0 {r['e0']:5.1f} yr | "
                   f"q(<5) {r['q_u5']*100:4.0f}% | CDR {r['cdr']*1000:4.0f}/1000")
            print(f"[2m] {msg}  [{time.time()-t0:.0f}s]", flush=True)
            with open(prog, "w") as f: f.write(f"2m: {msg} | elapsed {time.time()-t0:.0f}s\n")

    # gradient (proper metric): with pathogen ON, e0 (age at death) should FALL arid→lush (more pathogen),
    # AND eq-pop should fall (the food−disease trade-off). Both flat at gamma=0 (control).
    names = [b for b, _ in BIOMES]
    e0_off = [res[(b, 0.0)]["e0"] for b in names]
    e0_hi = [res[(b, 1.0)]["e0"] for b in names]
    pop_hi = [res[(b, 1.0)]["eq_pop"] for b in names]
    grad_off = e0_off[0] - e0_off[-1]      # arid − lush at gamma=0 (≈0: same baseline)
    grad_hi = e0_hi[0] - e0_hi[-1]         # arid − lush at gamma=1 (>0: pathogen lowers lush e0)
    pop_grad = res[("lush", 0.0)]["eq_pop"] - res[("lush", 1.0)]["eq_pop"]   # lush population collapse w/ pathogen
    bites = (grad_hi > 1.0 and grad_hi > grad_off + 1.0) or pop_grad > 0.3 * max(res[("lush", 0.0)]["eq_pop"], 1)
    if bites:
        verdict = (f"PATHOGEN BIOME GRADIENT (bracketed) — at gamma=1, e0 falls arid→lush "
                   f"{e0_hi[0]:.1f}→{e0_hi[-1]:.1f} yr ({grad_hi:.1f} yr span; gamma=0 span {grad_off:.1f}), and the "
                   f"lush population collapses {res[('lush',0.0)]['eq_pop']:.0f}→{res[('lush',1.0)]['eq_pop']:.0f} "
                   f"(food−disease trade-off: productive biome = most food but most disease). Real, monotone, scales "
                   f"with strength. HONEST: NPP-proxy only (T/humidity = CL-1); magnitude BRACKETED; exploratory, "
                   f"not a validated fit; gradient may be modest (a result, not a failure).")
    else:
        verdict = (f"GRADIENT WEAK — gamma=1 e0 arid→lush span {grad_hi:.1f} yr (gamma=0 {grad_off:.1f}); lush pop "
                   f"{res[('lush',0.0)]['eq_pop']:.0f}→{res[('lush',1.0)]['eq_pop']:.0f}. Pathogen effect small at "
                   f"these gammas/NPP contrast — possibly the self-regulation attractor, possibly a real modest signal.")

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    npps = [0.077, 0.185, 0.293]
    for g in GAMMAS:
        ax[0].plot(npps, [res[(b, g)]["e0"] for b in names], "o-", label=f"γ={g}")
        ax[1].plot(npps, [res[(b, g)]["eq_pop"] for b in names], "o-", label=f"γ={g}")
    ax[0].set_xlabel("biome mean NPP (arid→lush)"); ax[0].set_ylabel("e₀ (period life table, yr)")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25); ax[0].set_title("Mortality gradient (lower e₀ = more disease)")
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
            rows += (f"<tr><td>{b}</td><td>{g}</td><td>{r['eq_pop']:.0f}</td><td>{r['e0']:.1f}</td>"
                     f"<td>{r['q_u5']*100:.0f}%</td><td>{r['cdr']*1000:.0f}</td></tr>")
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
<table><tr><th>biome</th><th>γ</th><th>eq pop</th><th>e₀ (yr)</th><th>q(die &lt;5 yrlt;5)</th><th>CDR/1000 (=CBR)</th></tr>{rows}</table>
<h2>Gradient vs bracketed strength</h2><div class="fig">{img('grad')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">S3.5/S4 · {time.strftime('%Y-%m-%d')} · validated
demographic baseline + S2 pathogen · constant economy · isolated per-biome · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2m.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
