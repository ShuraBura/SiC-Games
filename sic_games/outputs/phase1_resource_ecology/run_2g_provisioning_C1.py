"""Resource-Ecology — Phase C.1: the CHILDHOOD DEFICIT (graded production + age-scaled consumption,
provisioning OFF).

R-8: the modulators need a sustained "lean but alive" class; only DEPENDENTS can be one. But in the
demographic path `_use_eta` is off, so newborns forage as full adults — no dependency. C.1 turns on the
deficit:
  - PRODUCTION: own intake = η(age)·share  (η ramps 0 → 1 over [0, forage_age_min]; Kaplan 2000)
  - CONSUMPTION: burn = burn_adult·c(age)  (c ramps cons_min → 1; FAO / Kaplan 2000)
With production starting at ~0 while consumption starts at cons_min, young children run a NET deficit.
Provisioning is OFF here, so the deficit is UNFUNDED.

THE TEST: does the unfunded childhood deficit produce a recruitment wall — children can't self-feed to
maturity, so the population fails to recruit and declines — while the children-as-adults baseline stays
stable (R-4)? That establishes the deficit is real and large → provisioning (C.2) is essential. The
444-suite must stay green (η/consumption are no-ops without lh_cfg).
[Constant R-4 economy (isolates dependency from depletion). Linear η/c — JV-1 approximation; convex
Kaplan curve deferred. forage_age_min=180 mo = 15 yr.]
Run:  py -3 -u outputs/phase1_resource_ecology/run_2g_provisioning_C1.py
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

from sic_games.config import KcalEconomyConfig, LifeHistoryConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_spec = _iu.spec_from_file_location("r2pre", _p); _r2 = _iu.module_from_spec(_spec); _spec.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEED, MATURE = 400, 1200, 42, 180          # MATURE = 180 mo = 15 yr


def run_one(lh_on, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    lh = LifeHistoryConfig(forage_age_min=MATURE, forage_age_max_offset=120,
                           eta_min=0.0, eta_old=0.4, cons_min=0.3) if lh_on else None
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, lh_cfg=lh,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=False))
    pop, n_child, n_adult, births, cdeaths = [], [], [], [], []
    for step in range(STEPS):
        w.step()
        al = w.agent_list
        pop.append(len(al))
        if not al:
            break
        ages = np.array([a.age for a in al])
        n_child.append(int(np.sum(ages < MATURE)))
        n_adult.append(int(np.sum(ages >= MATURE)))
        births.append(w.births_this_step)
        cdeaths.append(w.deaths_starv_this_step)
    tail = slice(int(0.6 * len(pop)), None)
    # trend = sign of slope over the back half
    yy = np.array(pop[tail], float); xx = np.arange(len(yy))
    slope = float(np.polyfit(xx, yy, 1)[0]) if len(yy) > 2 else 0.0
    return dict(lh_on=lh_on, pop=pop, n_child=n_child, n_adult=n_adult, births=births, cdeaths=cdeaths,
                final_pop=pop[-1], eq_pop=float(np.mean(pop[tail])) if pop[-1] else 0.0, slope=slope,
                final_child=n_child[-1] if pop[-1] else 0, final_adult=n_adult[-1] if pop[-1] else 0)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2g.txt")
    res = {}
    for name, lh_on in (("baseline (children=adults)", False), ("C.1 (childhood deficit, no provisioning)", True)):
        r = run_one(lh_on); res[name] = r
        trend = "rising" if r["slope"] > 1 else ("declining" if r["slope"] < -1 else "flat")
        msg = (f"{name}: final_pop {r['final_pop']} (eq {r['eq_pop']:.0f}, {trend}) | "
               f"children {r['final_child']} adults {r['final_adult']}")
        print(f"[2g] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2g: {msg} | elapsed {time.time()-t0:.0f}s\n")

    base, c1 = res["baseline (children=adults)"], res["C.1 (childhood deficit, no provisioning)"]
    # the wall: C.1 fails to recruit (declines / collapses) while baseline is stable/rising
    wall = (c1["slope"] < -1) and (c1["final_pop"] < 0.7 * base["eq_pop"])
    verdict = (f"CHILDHOOD DEFICIT CONFIRMED — unfunded, the deficit is a recruitment wall: C.1 declines "
               f"(slope {c1['slope']:.1f}/step, final pop {c1['final_pop']} vs baseline eq {base['eq_pop']:.0f}) "
               f"as children cannot self-feed to maturity. The deficit is real and large → provisioning (C.2) "
               f"is essential. Baseline ({base['eq_pop']:.0f}, stable) confirms the core is intact (lh_cfg opt-in)."
               if wall else
               f"NO WALL — C.1 pop {c1['final_pop']} (slope {c1['slope']:.1f}) did not collapse vs baseline "
               f"{base['eq_pop']:.0f}. Children survive the deficit unfunded → η/consumption too mild "
               f"(raise the deficit) or the endowment carries them. Re-check the curves.")

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    cols = {"baseline (children=adults)": "#718096", "C.1 (childhood deficit, no provisioning)": "#e53e3e"}
    for name, r in res.items():
        yr = np.arange(len(r["pop"])) / 12.0
        ax[0].plot(yr, r["pop"], color=cols[name], lw=1.2, label=name)
    ax[0].set_xlabel("year"); ax[0].set_ylabel("population"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[0].set_title("Population: does the unfunded childhood deficit wall recruitment?")
    for name, r in res.items():
        yr = np.arange(len(r["n_child"])) / 12.0
        ax[1].plot(yr, r["n_child"], color=cols[name], lw=1.2, label=name)
    ax[1].set_xlabel("year"); ax[1].set_ylabel("# children (age < 15 yr)"); ax[1].grid(alpha=0.25)
    ax[1].set_title("Surviving children")
    figs["ts"] = fig_b64(fig)

    results = dict(verdict=verdict, wall=wall,
                   conditions={n: {k: r[k] for k in ("final_pop", "eq_pop", "slope", "final_child",
                                                     "final_adult")} for n, r in res.items()},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, mature_mo=MATURE, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2g.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, wall)
    print(f"[2g] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, wall):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['final_pop']}</td><td>{r['eq_pop']:.0f}</td><td>{r['slope']:.1f}</td>"
        f"<td>{r['final_child']}</td><td>{r['final_adult']}</td></tr>" for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Resource-Ecology C.1 — childhood deficit</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Resource-Ecology · Phase C.1 — the childhood deficit (provisioning OFF)</h1>
<p>Graded η(age) production + age-scaled c(age) consumption (Kaplan 2000 / FAO), provisioning OFF.
Constant R-4 economy, seed {SEED}, {STEPS} steps. <b>Test:</b> does the unfunded deficit wall recruitment
(C.1 declines, children can't self-feed to maturity) while the children-as-adults baseline stays stable?</p>
<div class="box {'ok' if wall else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>final pop</th><th>back-half eq</th><th>slope/step</th><th>children</th><th>adults</th></tr>{rows}</table>
<h2>Population &amp; surviving children</h2><div class="fig">{img('ts')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">C.1 · {time.strftime('%Y-%m-%d')} · linear η/c
(JV-1 approximation) · provisioning OFF (C.2 next) · constant economy · 1 seed · synergy off.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2g.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
