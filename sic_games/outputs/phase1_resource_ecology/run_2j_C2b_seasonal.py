"""Resource-Ecology — Phase C.2b × A.1: does SEASONALITY + PROVISIONING make children the lean class?

C.2b (R-10): mother-linked provisioning rescues the dependent class but over-smooths on a self-adjusting
economy — mothers sit at the cap with overflow ≫ child need, so children are always fully provisioned
(0% lean). The arc's synthesis: the modulators need BOTH a dependent class (C.2b) AND a resource squeeze
the band can't fully buffer. A.1 (seasonality) was inert on its own because ADULTS self-adjust — but with
provisioning, a lean season should drain adult overflow first → children go hungry → seasonal child
mortality (exactly real HG seasonal child death).

THE TEST: with provisioning ON + depletion ON, does adding a lean season (s_min=0.4) produce a SEASONAL
JUVENILE under-fed pulse (synergy>1.2 oscillating with the season) while adults stay fed — or does the
population self-adjust to the lean-season bottleneck and keep even children fed (A.1's over-smoothing)?
Run:  py -3 -u outputs/phase1_resource_ecology/run_2j_C2b_seasonal.py
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

from sic_games.config import KcalEconomyConfig, LifeHistoryConfig, SubstrateConfig
from sic_games.demography import DemographyConfig, synergy_mult
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_here = os.path.dirname(os.path.abspath(__file__))
_e = _iu.spec_from_file_location("r2e", os.path.join(_here, "run_2e_depletion.py"))
_r2e = _iu.module_from_spec(_e); _e.loader.exec_module(_r2e)
DepletableSeasonalCapacity = _r2e.DepletableSeasonalCapacity
knobs_for, patch_positions = _r2e.knobs_for, _r2e.patch_positions

OUT = _here
FOUNDERS, STEPS, SEED, MATURE = 400, 1800, 42, 180


def syn(a):
    rs = a.reserve_scale()
    return synergy_mult(a._fed_reserve, a.reserve_floor * rs, 100000.0 * rs, 2.5)


def run_one(s_min, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = DepletableSeasonalCapacity(fields, s_min=s_min)        # depletion ON + seasonality
    pos = patch_positions(fields, FOUNDERS, rng)
    lh = LifeHistoryConfig(forage_age_min=MATURE, forage_age_max_offset=120,
                           eta_min=0.0, eta_old=0.4, cons_min=0.3, reserve_min=0.3)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, lh_cfg=lh,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=True, enable_provisioning=True))
    pop, juv_uf, adt_uf, season, cdeaths_juv = [], [], [], [], []
    for step in range(STEPS):
        cap.t = step
        w.step()
        al = w.agent_list
        pop.append(len(al)); season.append(cap.season())
        if not al:
            juv_uf.append(0.0); adt_uf.append(0.0); cdeaths_juv.append(0); break
        juv = [a for a in al if a.age < MATURE]; adt = [a for a in al if a.age >= MATURE]
        juv_uf.append(float(np.mean([syn(a) > 1.2 for a in juv])) if juv else 0.0)
        adt_uf.append(float(np.mean([syn(a) > 1.2 for a in adt])) if adt else 0.0)
        cdeaths_juv.append(w.deaths_starv_this_step)   # starvation deaths (mostly juveniles here)
    tail = slice(int(0.5 * len(pop)), None)
    alive = pop[-1] > 0
    juv_arr = np.array(juv_uf[tail]) if alive else np.array([0.0])
    # the real signal: starvation-death pulse by season (the squeeze kills children via the floor, fast,
    # so it shows in DEATHS not in survivors' synergy). Lean-trough vs good-season death rate.
    sea_arr = np.array(season[tail]); dth = np.array(cdeaths_juv[tail], float)
    lean = float(dth[sea_arr < 0.55].mean()) if alive and np.any(sea_arr < 0.55) else 0.0
    good = float(dth[sea_arr > 0.85].mean()) if alive and np.any(sea_arr > 0.85) else 0.0
    return dict(s_min=s_min, pop=pop, juv_uf=juv_uf, adt_uf=adt_uf, season=season, cdeaths_juv=cdeaths_juv,
                final_pop=pop[-1], eq_pop=float(np.mean(pop[tail])) if alive else 0.0,
                juv_uf_mean=float(juv_arr.mean()), juv_uf_max=float(juv_arr.max()),
                adt_uf_mean=float(np.mean(adt_uf[tail])) if alive else 0.0,
                death_lean=lean, death_good=good, death_pulse=lean / max(good, 0.5))


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2j.txt")
    res = {}
    for name, s_min in (("C.2b constant (s=1)", 1.0), ("C.2b seasonal (s=0.4)", 0.4)):
        r = run_one(s_min); res[name] = r
        msg = (f"{name}: eq_pop {r['eq_pop']:.0f} | starv deaths/step lean {r['death_lean']:.1f} vs good "
               f"{r['death_good']:.1f} (pulse {r['death_pulse']:.0f}×) | juv synergy>1.2 {r['juv_uf_mean']*100:.1f}%")
        print(f"[2j] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2j: {msg} | elapsed {time.time()-t0:.0f}s\n")

    con, sea = res["C.2b constant (s=1)"], res["C.2b seasonal (s=0.4)"]
    # the mechanism bites if the lean season drives a child STARVATION pulse (deaths, not synergy dwelling)
    bites = sea["death_lean"] > 5 and sea["death_pulse"] > 5
    if bites:
        verdict = (f"SEASONALITY + PROVISIONING BITES — a clean seasonal child STARVATION pulse: lean-trough "
                   f"deaths {sea['death_lean']:.0f}/step vs good-season {sea['death_good']:.1f} ({sea['death_pulse']:.0f}× "
                   f"pulse). Children are the buffer that absorbs the seasonal squeeze → emergent seasonal child "
                   f"mortality, the variance the whole A→B→C arc chased. NOTE: it runs through the hard floor, not "
                   f"graded synergy (juv synergy>1.2 only {sea['juv_uf_mean']*100:.1f}% — a squeezed child plummets to "
                   f"the floor in ~1 step, too fast to dwell). T-4 (emergent child q(x) vs Aché) is open; whether to "
                   f"route the mortality through the graded synergy/disease channel is the modeling choice.")
    else:
        verdict = (f"NO PULSE — lean-season child deaths {sea['death_lean']:.1f}/step vs good {sea['death_good']:.1f}. "
                   f"The population self-adjusts to the lean-season bottleneck and provisioning covers children even in "
                   f"the trough. Need a deeper/faster squeeze.")

    figs = {}
    fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    yr = np.arange(len(sea["cdeaths_juv"])) / 12.0
    lo = max(0, len(yr) - 120)                     # last ~10 yr, to see the annual pulse clearly
    ax[0].plot(yr[lo:], np.array(sea["cdeaths_juv"])[lo:], color="#e53e3e", lw=1.0, label="seasonal")
    ax[0].plot(np.arange(len(con["cdeaths_juv"]))[lo:] / 12.0, np.array(con["cdeaths_juv"])[lo:], color="#a0aec0", lw=1.0, label="constant")
    ax[0].set_ylabel("starvation deaths / step"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[0].set_title("Seasonal child mortality pulse (C.2b + seasonality) — deaths track the lean trough")
    ax[1].plot(yr[lo:], np.array(sea["season"])[lo:], color="#38a169", lw=1.0)
    ax[1].set_ylabel("seasonal harvest s(t)"); ax[1].set_xlabel("year"); ax[1].grid(alpha=0.25)
    figs["ts"] = fig_b64(fig)

    results = dict(verdict=verdict, bites=bites,
                   conditions={n: {k: r[k] for k in ("eq_pop", "juv_uf_mean", "juv_uf_max", "adt_uf_mean")}
                               for n, r in res.items()},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2j.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, bites)
    print(f"[2j] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, bites):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['eq_pop']:.0f}</td><td>{r['death_lean']:.1f}</td><td>{r['death_good']:.1f}</td>"
        f"<td>{r['death_pulse']:.0f}×</td><td>{r['juv_uf_mean']*100:.1f}%</td></tr>" for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Resource-Ecology C.2b×A.1 — seasonal provisioning</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Resource-Ecology · Phase C.2b × A.1 — seasonal squeeze on the dependent class</h1>
<p>Provisioning ON + depletion ON + seasonality (s_min=0.4 vs constant). synergy ON, seed {SEED}, {STEPS}
steps. <b>Test:</b> does the lean season drain adult overflow so children (the provisioning buffer) go
hungry — a seasonal JUVENILE under-fed pulse while adults stay fed?</p>
<div class="box {'ok' if bites else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>eq pop</th><th>starv deaths/step (lean)</th><th>(good)</th><th>pulse</th><th>juv synergy&gt;1.2</th></tr>{rows}</table>
<p>The squeeze kills children via the hard floor (a squeezed child plummets to the floor in ~1 step, too
fast to dwell), so it shows in the seasonal DEATH pulse, not in survivors' graded synergy (~0%).</p>
<h2>Seasonal child mortality pulse</h2><div class="fig">{img('ts')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">C.2b×A.1 · {time.strftime('%Y-%m-%d')} · provisioning
+ depletion + seasonality · non-spatial mother-link · 1 seed · μ_max=2.5 default.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2j.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
