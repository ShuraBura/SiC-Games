"""Biome-Mortality — S0: lagged BODY-CONDITION signal routes the seasonal squeeze through graded DISEASE.

R-8/R-10: the synergy modulator reads the INSTANTANEOUS post-harvest reserve, which is bang-bang (full or
draining-to-floor in ~1 step) — so a squeezed child starves (hard floor) before it can dwell in the synergy
zone; deaths register as starvation, synergy stays ~1. But the data (MODEL_SPEC §4.2.7) says child
nutritional death ≈0 — nutrition kills by potentiating DISEASE (Pelletier), spread over weeks.

S0 adds `_condition` ∈ [0,1] = a slow EMA (α=0.25, ~2.4-month half-life) of nutritional status (immune
competence), and the synergy modulator reads CONDITION instead of the instantaneous reserve:
`synergy = 1 + (μ_max−1)·(1−condition)`. So a child with weeks of poor provisioning degrades → elevated
DISEASE (a2) mortality → dies graded, in the senescence/baseline bucket, NOT the starvation floor.

THE TEST: on the C.2b seasonal squeeze (provisioning + depletion + seasonality), does enabling the
condition signal (i) make juvenile condition degrade in the lean season, and (ii) ROUTE seasonal child
mortality from the STARVATION bucket toward the DISEASE (senescence) bucket — vs the R-10 baseline where
synergy reads the instantaneous reserve and the deaths are all starvation?
Run:  py -3 -u outputs/phase1_resource_ecology/run_2k_condition.py
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
from sic_games.demography import DemographyConfig
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


def run_one(condition_on, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = DepletableSeasonalCapacity(fields, s_min=0.4)          # depletion + seasonality (the squeeze)
    pos = patch_positions(fields, FOUNDERS, rng)
    lh = LifeHistoryConfig(forage_age_min=MATURE, forage_age_max_offset=120,
                           eta_min=0.0, eta_old=0.4, cons_min=0.3, reserve_min=0.3)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, lh_cfg=lh,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=True, enable_provisioning=True,
                                                     enable_condition=condition_on, mu_max=2.5))
    pop, starv, dis, season, jcond = [], [], [], [], []
    for step in range(STEPS):
        cap.t = step
        w.step()
        al = w.agent_list
        pop.append(len(al)); season.append(cap.season())
        starv.append(w.deaths_starv_this_step); dis.append(w.deaths_senesc_this_step)
        if not al:
            jcond.append(0.0); break
        juv = [a for a in al if a.age < MATURE]
        jcond.append(float(np.mean([getattr(a, "_condition", 1.0) for a in juv])) if juv else 1.0)
    tail = slice(int(0.5 * len(pop)), None)
    sea = np.array(season[tail]); sv = np.array(starv[tail], float); ds = np.array(dis[tail], float)
    jc = np.array(jcond[tail])
    lean = sea < 0.55; good = sea > 0.85
    f = lambda arr, m: float(arr[m].mean()) if np.any(m) else 0.0
    return dict(condition_on=condition_on, pop=pop, starv=starv, dis=dis, season=season, jcond=jcond,
                final_pop=pop[-1], eq_pop=float(np.mean(pop[tail])) if pop[-1] else 0.0,
                starv_lean=f(sv, lean), starv_good=f(sv, good), dis_lean=f(ds, lean), dis_good=f(ds, good),
                jcond_lean=f(jc, lean), jcond_good=f(jc, good))


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2k.txt")
    res = {}
    for name, c in (("synergy on reserve (R-10)", False), ("synergy on condition (S0)", True)):
        r = run_one(c); res[name] = r
        msg = (f"{name}: eq_pop {r['eq_pop']:.0f} | STARV lean {r['starv_lean']:.1f}/good {r['starv_good']:.1f} | "
               f"DISEASE lean {r['dis_lean']:.1f}/good {r['dis_good']:.1f} | juv cond lean {r['jcond_lean']:.2f}/good {r['jcond_good']:.2f}")
        print(f"[2k] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2k: {msg} | elapsed {time.time()-t0:.0f}s\n")

    base, s0 = res["synergy on reserve (R-10)"], res["synergy on condition (S0)"]
    cond_degrades = s0["jcond_lean"] < s0["jcond_good"] - 0.02
    dis_pulse = s0["dis_lean"] > s0["dis_good"] + 2 and s0["dis_lean"] > base["dis_lean"] + 2
    starv_softens = s0["starv_lean"] < 0.8 * base["starv_lean"]
    if cond_degrades and dis_pulse:
        verdict = (f"S0 ROUTES THROUGH DISEASE — juvenile condition degrades in the lean season "
                   f"({s0['jcond_good']:.2f}→{s0['jcond_lean']:.2f}) and seasonal child mortality now appears in the "
                   f"DISEASE bucket (lean {s0['dis_lean']:.0f}/step vs good {s0['dis_good']:.1f}; R-10 baseline disease "
                   f"{base['dis_lean']:.1f}). Starvation pulse {base['starv_lean']:.0f}→{s0['starv_lean']:.0f}/step "
                   f"({'softened' if starv_softens else 'persists — S1 child-priority needed to slow the drain'}). "
                   f"The graded disease-potentiation channel (Pelletier) is LIVE; μ_max calibratable next.")
    elif cond_degrades:
        verdict = (f"PARTIAL — condition degrades in lean ({s0['jcond_good']:.2f}→{s0['jcond_lean']:.2f}) but disease "
                   f"deaths didn't clearly pulse (lean {s0['dis_lean']:.1f} vs base {base['dis_lean']:.1f}); the floor "
                   f"still wins the race (starv lean {s0['starv_lean']:.0f}). S1 child-priority (slow the drain so "
                   f"children dwell) is the needed complement; raise μ_max or condition_alpha.")
    else:
        verdict = (f"INERT — condition barely moved ({s0['jcond_good']:.2f}→{s0['jcond_lean']:.2f}); the squeeze is too "
                   f"acute (children cut off → floor before condition degrades). Needs S1 (partial provisioning) first.")

    figs = {}
    fig, ax = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    yr = np.arange(len(s0["starv"])) / 12.0; lo = max(0, len(yr) - 120)
    ax[0].plot(yr[lo:], np.array(base["starv"])[lo:], color="#e53e3e", lw=0.9, label="starvation (R-10 reserve)")
    ax[0].plot(yr[lo:], np.array(s0["starv"])[lo:], color="#dd6b20", lw=0.9, label="starvation (S0 condition)")
    ax[0].set_ylabel("starv deaths/step"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[0].set_title("S0: does the lagged condition reroute seasonal child mortality starvation → disease?")
    ax[1].plot(yr[lo:], np.array(base["dis"])[lo:], color="#3182ce", lw=0.9, label="disease (R-10)")
    ax[1].plot(yr[lo:], np.array(s0["dis"])[lo:], color="#2f855a", lw=0.9, label="disease (S0)")
    ax[1].set_ylabel("disease deaths/step"); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.25)
    ax[2].plot(yr[lo:], np.array(s0["jcond"])[lo:], color="#805ad5", lw=1.0, label="juv condition (S0)")
    ax[2].plot(yr[lo:], np.array(s0["season"])[lo:], color="#38a169", lw=0.7, label="season s(t)")
    ax[2].set_ylabel("condition / season"); ax[2].set_xlabel("year"); ax[2].legend(fontsize=8); ax[2].grid(alpha=0.25)
    figs["ts"] = fig_b64(fig)

    results = dict(verdict=verdict, cond_degrades=cond_degrades, dis_pulse=dis_pulse, starv_softens=starv_softens,
                   conditions={n: {k: r[k] for k in ("eq_pop", "starv_lean", "starv_good", "dis_lean", "dis_good",
                                                     "jcond_lean", "jcond_good")} for n, r in res.items()},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2k.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, cond_degrades and dis_pulse)
    print(f"[2k] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, good):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['eq_pop']:.0f}</td><td>{r['starv_lean']:.1f}/{r['starv_good']:.1f}</td>"
        f"<td>{r['dis_lean']:.1f}/{r['dis_good']:.1f}</td><td>{r['jcond_lean']:.2f}/{r['jcond_good']:.2f}</td></tr>"
        for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Biome-Mortality S0 — body condition</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Biome-Mortality · S0 — lagged body-condition signal</h1>
<p>Synergy reads `_condition` (EMA α=0.25 of nutritional status) instead of the bang-bang reserve, so
sustained undernutrition potentiates DISEASE (Pelletier). On the C.2b seasonal squeeze. <b>Test:</b> does
seasonal child mortality reroute from the STARVATION floor to the graded DISEASE bucket? (deaths shown as
lean-trough / good-season per step.)</p>
<div class="box {'ok' if good else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>eq pop</th><th>starv (lean/good)</th><th>disease (lean/good)</th><th>juv condition (lean/good)</th></tr>{rows}</table>
<h2>Rerouting + condition over the seasonal cycle</h2><div class="fig">{img('ts')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">S0 · {time.strftime('%Y-%m-%d')} · condition EMA
α=0.25 · μ_max=2.5 · provisioning+depletion+seasonality · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2k.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
