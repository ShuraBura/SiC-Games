"""Resource-Ecology — Phase C.2a: per-class (age-scaled) RESERVES make the childhood deficit bite.

R-9 (C.1): the graded-η + age-scaled-consumption childhood deficit did NOT wall recruitment, because
newborns inherit reserve_full = 100k — a full ADULT fat reserve (~1.3 mo maintenance) — which buffers
the early deficit. C.2a scales the reserve (floor + cap + birth endowment) by body size (reserve_min at
birth → 1.0 at forage_age_min; Pontzer 2012 / body-mass), so a neonate cannot self-buffer a month of
maintenance.

THE TEST (three-way, isolating the reserve scaling):
  - baseline      : children = adults (no lh_cfg)                  → stable (R-4)
  - C.1 (flat)    : deficit on, reserve_min=1.0 (adult reserves)   → no wall (reproduces R-9)
  - C.2a (scaled) : deficit on, reserve_min=0.1 (body-sized)       → EXPECT a recruitment wall
If C.2a walls while C.1 does not, the body-sized neonatal reserve is what makes the deficit real →
mother-linked provisioning (C.2b) is then load-bearing. 444-suite must stay green (reserve_scale=1
without lh_cfg).
Run:  py -3 -u outputs/phase1_resource_ecology/run_2h_C2a_reserves.py
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
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_spec = _iu.spec_from_file_location("r2pre", _p); _r2 = _iu.module_from_spec(_spec); _spec.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEED, MATURE = 400, 1200, 42, 180


def run_one(mode, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    if mode == "baseline":
        lh = None
    else:
        rmin = 1.0 if mode == "C.1 (flat reserves)" else 0.1
        lh = LifeHistoryConfig(forage_age_min=MATURE, forage_age_max_offset=120,
                               eta_min=0.0, eta_old=0.4, cons_min=0.3, reserve_min=rmin)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, lh_cfg=lh,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=False))
    pop, n_child = [], []
    for step in range(STEPS):
        w.step()
        al = w.agent_list
        pop.append(len(al))
        if not al:
            break
        n_child.append(int(np.sum(np.array([a.age for a in al]) < MATURE)))
    tail = slice(int(0.6 * len(pop)), None)
    yy = np.array(pop[tail], float); xx = np.arange(len(yy))
    slope = float(np.polyfit(xx, yy, 1)[0]) if len(yy) > 2 else 0.0
    return dict(mode=mode, pop=pop, n_child=n_child, final_pop=pop[-1] if pop else 0,
                eq_pop=float(np.mean(pop[tail])) if pop and pop[-1] else 0.0, slope=slope,
                final_child=n_child[-1] if n_child and pop[-1] else 0)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2h.txt")
    modes = ["baseline", "C.1 (flat reserves)", "C.2a (body-scaled reserves)"]
    res = {}
    for m in modes:
        r = run_one(m); res[m] = r
        trend = "rising" if r["slope"] > 1 else ("declining" if r["slope"] < -1 else "flat")
        msg = f"{m}: final_pop {r['final_pop']} (eq {r['eq_pop']:.0f}, {trend}, slope {r['slope']:.1f}) | children {r['final_child']}"
        print(f"[2h] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2h: {msg} | elapsed {time.time()-t0:.0f}s\n")

    base, c1, c2a = res["baseline"], res["C.1 (flat reserves)"], res["C.2a (body-scaled reserves)"]
    walls = (c2a["slope"] < -1) or (c2a["final_pop"] < 0.5 * c1["eq_pop"])
    bites = walls and not (c1["slope"] < -1)
    verdict = (f"RESERVE SCALING MAKES THE DEFICIT BITE — C.2a walls (final {c2a['final_pop']}, slope "
               f"{c2a['slope']:.1f}) where C.1 with adult-sized reserves did not (eq {c1['eq_pop']:.0f}, "
               f"slope {c1['slope']:.1f}). A body-sized neonatal reserve is the missing piece (R-9 confirmed) "
               f"→ mother-linked provisioning (C.2b) is now load-bearing. Core intact (baseline "
               f"{base['eq_pop']:.0f})."
               if bites else
               f"INCONCLUSIVE — C.2a final {c2a['final_pop']} (slope {c2a['slope']:.1f}) vs C.1 "
               f"{c1['eq_pop']:.0f} (slope {c1['slope']:.1f}). Reserve scaling did not clearly flip the "
               f"outcome; re-check reserve_min / the deficit curves.")

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    cols = {"baseline": "#718096", "C.1 (flat reserves)": "#dd6b20", "C.2a (body-scaled reserves)": "#e53e3e"}
    for m, r in res.items():
        yr = np.arange(len(r["pop"])) / 12.0
        ax[0].plot(yr, r["pop"], color=cols[m], lw=1.2, label=m)
    ax[0].set_xlabel("year"); ax[0].set_ylabel("population"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[0].set_title("Does a body-sized neonatal reserve wall recruitment?")
    for m, r in res.items():
        yr = np.arange(len(r["n_child"])) / 12.0
        ax[1].plot(yr, r["n_child"], color=cols[m], lw=1.2, label=m)
    ax[1].set_xlabel("year"); ax[1].set_ylabel("# children (< 15 yr)"); ax[1].grid(alpha=0.25)
    ax[1].set_title("Surviving children")
    figs["ts"] = fig_b64(fig)

    results = dict(verdict=verdict, bites=bites,
                   conditions={m: {k: r[k] for k in ("final_pop", "eq_pop", "slope", "final_child")}
                               for m, r in res.items()},
                   reserve_min_C2a=0.1, founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2h.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, bites)
    print(f"[2h] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, bites):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{m}</td><td>{r['final_pop']}</td><td>{r['eq_pop']:.0f}</td><td>{r['slope']:.1f}</td>"
        f"<td>{r['final_child']}</td></tr>" for m, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Resource-Ecology C.2a — per-class reserves</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Resource-Ecology · Phase C.2a — body-sized neonatal reserve (provisioning OFF)</h1>
<p>Scale the reserve (floor + cap + birth endowment) by body size (reserve_min=0.1 at birth → 1.0 at 15 yr;
Pontzer 2012 / body-mass). Three-way: baseline (children=adults) vs C.1 (deficit, ADULT-sized reserves) vs
C.2a (deficit, body-sized reserves). Constant R-4 economy, seed {SEED}, {STEPS} steps. <b>Test:</b> does the
body-sized reserve make the C.1 deficit finally wall recruitment?</p>
<div class="box {'ok' if bites else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>final pop</th><th>back-half eq</th><th>slope/step</th><th>children</th></tr>{rows}</table>
<h2>Population &amp; surviving children</h2><div class="fig">{img('ts')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">C.2a · {time.strftime('%Y-%m-%d')} · linear reserve
ramp (Pontzer-anchored, sex-split deferred) · provisioning OFF (C.2b next) · constant economy · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2h.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
