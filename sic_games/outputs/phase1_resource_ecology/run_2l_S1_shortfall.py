"""Biome-Mortality — S1: child-priority SHORTFALL-SHARING (the coupled complement to S0).

S0 (run_2k) was inert: on binary overflow-only provisioning a child is either fully fed (condition 1.0) or
cut off → starves at the floor in ~1 step (gone before condition degrades). S1 lets the mother provision her
child's deficit from her own reserve DOWN TO `provision_self_keep`·(her cap), so in a lean season the
shortfall is SHARED — the child dwells at a *mild* deficit (condition degrades → graded disease, not the
floor) and the mother absorbs the deeper end.

THE TEST (S0 ON throughout): sweep the child-priority knob `provision_self_keep` 1.0 (=C.2b overflow-only,
the inert S0 baseline) → 0.7 → 0.4 (more sacrifice). Does shortfall-sharing (i) make juvenile condition
degrade in the lean season, (ii) reroute seasonal child mortality STARVATION → graded DISEASE, and (iii)
keep child starvation low — while watching whether the stress lands on children (intended) or over-stresses
the mothers (adult condition)?
Run:  py -3 -u outputs/phase1_resource_ecology/run_2l_S1_shortfall.py
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


def run_one(self_keep, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = DepletableSeasonalCapacity(fields, s_min=0.4)
    pos = patch_positions(fields, FOUNDERS, rng)
    lh = LifeHistoryConfig(forage_age_min=MATURE, forage_age_max_offset=120,
                           eta_min=0.0, eta_old=0.4, cons_min=0.3, reserve_min=0.3)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, lh_cfg=lh,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=True, enable_provisioning=True,
                                                     enable_condition=True, mu_max=2.5,
                                                     provision_self_keep=self_keep))
    pop, starv, dis, season, jcond, acond = [], [], [], [], [], []
    for step in range(STEPS):
        cap.t = step
        w.step()
        al = w.agent_list
        pop.append(len(al)); season.append(cap.season())
        starv.append(w.deaths_starv_this_step); dis.append(w.deaths_senesc_this_step)
        if not al:
            jcond.append(0.0); acond.append(0.0); break
        jc = [getattr(a, "_condition", 1.0) for a in al if a.age < MATURE]
        ac = [getattr(a, "_condition", 1.0) for a in al if a.age >= MATURE]
        jcond.append(float(np.mean(jc)) if jc else 1.0); acond.append(float(np.mean(ac)) if ac else 1.0)
    tail = slice(int(0.5 * len(pop)), None)
    sea = np.array(season[tail]); lean = sea < 0.55; good = sea > 0.85
    f = lambda a, m: float(np.array(a[tail], float)[m].mean()) if np.any(m) else 0.0
    return dict(self_keep=self_keep, pop=pop, starv=starv, dis=dis, season=season, jcond=jcond, acond=acond,
                final_pop=pop[-1], eq_pop=float(np.mean(pop[tail])) if pop[-1] else 0.0,
                starv_lean=f(starv, lean), dis_lean=f(dis, lean), dis_good=f(dis, good),
                jcond_lean=f(jcond, lean), jcond_good=f(jcond, good),
                acond_lean=f(acond, lean), acond_good=f(acond, good))


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2l.txt")
    res = {}
    for sk in (1.0, 0.7, 0.4):
        r = run_one(sk); res[sk] = r
        tag = "S0 only (sk=1.0)" if sk == 1.0 else f"S0+S1 sk={sk}"
        msg = (f"{tag}: eq_pop {r['eq_pop']:.0f} | STARV lean {r['starv_lean']:.1f} | DISEASE lean {r['dis_lean']:.1f}"
               f"/good {r['dis_good']:.1f} | juv cond {r['jcond_good']:.2f}->{r['jcond_lean']:.2f} | "
               f"adult cond {r['acond_good']:.2f}->{r['acond_lean']:.2f}")
        print(f"[2l] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2l: {msg} | elapsed {time.time()-t0:.0f}s\n")

    base = res[1.0]; best = res[0.4]
    jdeg = best["jcond_good"] - best["jcond_lean"]
    reroute = best["dis_lean"] > base["dis_lean"] + 2 and best["starv_lean"] < 0.8 * max(base["starv_lean"], 1)
    if jdeg > 0.03 and reroute:
        verdict = (f"S1 ROUTES THROUGH DISEASE — child-priority shortfall-sharing makes juvenile condition "
                   f"degrade in the lean season ({best['jcond_good']:.2f}→{best['jcond_lean']:.2f}) and seasonal child "
                   f"mortality reroutes STARVATION→DISEASE (sk=0.4: starv lean {best['starv_lean']:.0f}, disease lean "
                   f"{best['dis_lean']:.0f} vs S0-only disease {base['dis_lean']:.0f}). The graded disease channel "
                   f"(Pelletier) is LIVE on the dependent class. Adult cond {best['acond_good']:.2f}→{best['acond_lean']:.2f} "
                   f"({'mothers also stressed — watch the split' if best['acond_lean']<0.9 else 'adults stay fed'}). "
                   f"Calibrate self_keep + μ_max to the Aché child-disease target next.")
    elif jdeg > 0.03:
        verdict = (f"PARTIAL — juvenile condition degrades (sk=0.4 {best['jcond_good']:.2f}→{best['jcond_lean']:.2f}) but "
                   f"the disease reroute is weak (disease lean {best['dis_lean']:.1f} vs S0-only {base['dis_lean']:.1f}; "
                   f"starv lean {best['starv_lean']:.1f}). Raise μ_max, or lower self_keep further / tune α.")
    else:
        verdict = (f"STILL FLAT — even at sk=0.4 juvenile condition barely moves "
                   f"({best['jcond_good']:.2f}→{best['jcond_lean']:.2f}); shortfall-sharing isn't producing the dwell "
                   f"(mothers fully cover, or the squeeze still cuts children off acutely). Re-examine the allocation.")

    figs = {}
    fig, ax = plt.subplots(2, 1, figsize=(11, 7))
    sks = list(res.keys())
    ax[0].plot(sks, [res[s]["starv_lean"] for s in sks], "o-", color="#e53e3e", label="starvation (lean)")
    ax[0].plot(sks, [res[s]["dis_lean"] for s in sks], "s-", color="#3182ce", label="disease (lean)")
    ax[0].set_xlabel("provision_self_keep (← more child priority)"); ax[0].set_ylabel("deaths/step (lean trough)")
    ax[0].invert_xaxis(); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[0].set_title("S1: does child-priority reroute seasonal child mortality starvation→disease?")
    ax[1].plot(sks, [res[s]["jcond_lean"] for s in sks], "o-", color="#dd6b20", label="juvenile cond (lean)")
    ax[1].plot(sks, [res[s]["acond_lean"] for s in sks], "s-", color="#805ad5", label="adult cond (lean)")
    ax[1].set_xlabel("provision_self_keep (← more child priority)"); ax[1].set_ylabel("mean condition (lean)")
    ax[1].invert_xaxis(); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.25)
    ax[1].set_title("Where does the stress land — children (intended) or mothers?")
    figs["sweep"] = fig_b64(fig)

    results = dict(verdict=verdict,
                   conditions={str(s): {k: r[k] for k in ("eq_pop", "starv_lean", "dis_lean", "dis_good",
                       "jcond_lean", "jcond_good", "acond_lean", "acond_good")} for s, r in res.items()},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2l.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict)
    print(f"[2l] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{'S0 only' if s==1.0 else 'S0+S1'} (sk={s})</td><td>{r['eq_pop']:.0f}</td>"
        f"<td>{r['starv_lean']:.1f}</td><td>{r['dis_lean']:.1f}/{r['dis_good']:.1f}</td>"
        f"<td>{r['jcond_good']:.2f}→{r['jcond_lean']:.2f}</td><td>{r['acond_good']:.2f}→{r['acond_lean']:.2f}</td></tr>"
        for s, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Biome-Mortality S1 — shortfall-sharing</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Biome-Mortality · S1 — child-priority shortfall-sharing (with S0)</h1>
<p>Mother provisions her child's deficit from her own reserve down to `provision_self_keep`·cap (S1), so the
child dwells at a mild deficit → condition degrades → graded disease (S0). S0 ON throughout; sweep the
priority knob. C.2b seasonal squeeze. <b>Test:</b> does seasonal child mortality reroute starvation→disease,
and where does the stress land (children vs mothers)?</p>
<div class="box"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>eq pop</th><th>starv (lean)</th><th>disease (lean/good)</th><th>juv cond (good→lean)</th><th>adult cond (good→lean)</th></tr>{rows}</table>
<h2>Child-priority sweep</h2><div class="fig">{img('sweep')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">S1 · {time.strftime('%Y-%m-%d')} · S0 condition α=0.25
· μ_max=2.5 · provisioning+depletion+seasonality · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2l.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
