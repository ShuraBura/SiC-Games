"""Resource-Ecology — Phase C.2b: MOTHER-LINKED PROVISIONING (the variance, at last).

The whole arc: A.1/A.2/B (R-6/7/8) showed mean-lowering + spatial mechanisms can't make the modulators
bite — under the ideal free distribution every self-feeding adult is fed-at-cap or culled, no lean band.
C.1/C.2a built a DEPENDENT class (graded η deficit + body-sized neonatal reserve) that, unfunded, goes
extinct (R-9). C.2b funds it: a mother's harvest overflow (above her cap, otherwise wasted) is redirected
to her dependent children. A mother on a poor/depleted cell has little overflow → her children dwell lean.

THE TEST (the variance we've chased all stage):
  - does provisioning RESCUE the population from C.2a extinction?
  - does a non-trivial fraction of JUVENILES dwell lean (synergy>1.2) — the sustained "lean but alive"
    class the food economy could never give us — while ADULTS stay fed (under-fed ≈ 0)?
If yes: the modulators are LIVE on the demographically vulnerable, μ_max becomes calibratable, and the
path to T-4 (emergent child mortality vs Aché) is open.
Depletion ON (cell-quality variance → mothers differ in overflow), synergy ON. 444 stays green (opt-in).
Run:  py -3 -u outputs/phase1_resource_ecology/run_2i_C2b_provisioning.py
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
FOUNDERS, STEPS, SEED, MATURE = 400, 1500, 42, 180


def syn(a):
    rs = a.reserve_scale()
    return synergy_mult(a._fed_reserve, a.reserve_floor * rs, 100000.0 * rs, 2.5)


def run_one(provision, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = DepletableSeasonalCapacity(fields, s_min=1.0)          # depletion ON, season OFF
    pos = patch_positions(fields, FOUNDERS, rng)
    lh = LifeHistoryConfig(forage_age_min=MATURE, forage_age_max_offset=120,
                           eta_min=0.0, eta_old=0.4, cons_min=0.3, reserve_min=0.3)   # reserve_min=cons_min (cap≥burn)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, lh_cfg=lh,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=True,
                                                     enable_provisioning=provision))
    pop, juv_uf, adt_uf, n_juv, n_adt = [], [], [], [], []
    for step in range(STEPS):
        cap.t = step
        w.step()
        al = w.agent_list
        pop.append(len(al))
        if not al:
            juv_uf.append(0.0); adt_uf.append(0.0); n_juv.append(0); n_adt.append(0); break
        juv = [a for a in al if a.age < MATURE]
        adt = [a for a in al if a.age >= MATURE]
        n_juv.append(len(juv)); n_adt.append(len(adt))
        juv_uf.append(float(np.mean([syn(a) > 1.2 for a in juv])) if juv else 0.0)
        adt_uf.append(float(np.mean([syn(a) > 1.2 for a in adt])) if adt else 0.0)
    tail = slice(int(0.6 * len(pop)), None)
    alive = pop[-1] > 0
    return dict(provision=provision, pop=pop, juv_uf=juv_uf, adt_uf=adt_uf, n_juv=n_juv, n_adt=n_adt,
                final_pop=pop[-1], eq_pop=float(np.mean(pop[tail])) if alive else 0.0,
                juv_uf_eq=float(np.mean(juv_uf[tail])) if alive else 0.0,
                adt_uf_eq=float(np.mean(adt_uf[tail])) if alive else 0.0,
                juv_frac_eq=float(np.mean(np.array(n_juv[tail]) / np.maximum(np.array(pop[tail]), 1))) if alive else 0.0)


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2i.txt")
    res = {}
    for name, prov in (("C.2a (provisioning OFF)", False), ("C.2b (provisioning ON)", True)):
        r = run_one(prov); res[name] = r
        msg = (f"{name}: final_pop {r['final_pop']} (eq {r['eq_pop']:.0f}) | juv under-fed {r['juv_uf_eq']*100:.1f}% | "
               f"adult under-fed {r['adt_uf_eq']*100:.1f}% | juv frac {r['juv_frac_eq']*100:.0f}%")
        print(f"[2i] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2i: {msg} | elapsed {time.time()-t0:.0f}s\n")

    c2a, c2b = res["C.2a (provisioning OFF)"], res["C.2b (provisioning ON)"]
    rescued = c2b["final_pop"] > 0 and c2b["eq_pop"] > 5 * max(c2a["eq_pop"], 1)
    bites = c2b["juv_uf_eq"] > 0.02 and c2b["juv_uf_eq"] > 3 * c2b["adt_uf_eq"]
    if rescued and bites:
        verdict = (f"PROVISIONING WORKS — and the modulators are LIVE. Provisioning rescues the population "
                   f"(eq {c2b['eq_pop']:.0f} vs C.2a {c2a['eq_pop']:.0f}) AND a sustained {c2b['juv_uf_eq']*100:.1f}% of "
                   f"JUVENILES dwell lean (synergy>1.2) while adults stay fed ({c2b['adt_uf_eq']*100:.1f}%). The "
                   f"variance lands on the demographically vulnerable — the lean-but-alive class the food economy "
                   f"could never produce (R-7/R-8). μ_max is now calibratable; T-4 is open.")
    elif rescued:
        verdict = (f"PROVISIONING RESCUES but variance still thin — pop recovers (eq {c2b['eq_pop']:.0f}) but juvenile "
                   f"under-fed only {c2b['juv_uf_eq']*100:.1f}% (adults {c2b['adt_uf_eq']*100:.1f}%). Children are "
                   f"provisioned almost fully even on poor cells → tighten provisioning (partial transfer) or sharpen "
                   f"cell-quality variance to widen the lean dwell.")
    else:
        verdict = (f"PROVISIONING INSUFFICIENT — pop {c2b['final_pop']} (eq {c2b['eq_pop']:.0f}) did not clearly "
                   f"recover from C.2a ({c2a['eq_pop']:.0f}). The overflow-redirect is too weak (mothers at the cap "
                   f"give little) — revisit the provisioning source/target.")

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    cols = {"C.2a (provisioning OFF)": "#e53e3e", "C.2b (provisioning ON)": "#38a169"}
    for name, r in res.items():
        yr = np.arange(len(r["pop"])) / 12.0
        ax[0].plot(yr, r["pop"], color=cols[name], lw=1.2, label=name)
    ax[0].set_xlabel("year"); ax[0].set_ylabel("population"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[0].set_title("Does provisioning rescue the population?")
    r = res["C.2b (provisioning ON)"]
    yr = np.arange(len(r["juv_uf"])) / 12.0
    ax[1].plot(yr, np.array(r["juv_uf"]) * 100, color="#dd6b20", lw=1.1, label="juveniles")
    ax[1].plot(yr, np.array(r["adt_uf"]) * 100, color="#3182ce", lw=1.1, label="adults")
    ax[1].set_xlabel("year"); ax[1].set_ylabel("% under-fed (synergy>1.2)"); ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.25); ax[1].set_title("C.2b: who dwells lean? (the variance)")
    figs["ts"] = fig_b64(fig)

    results = dict(verdict=verdict, rescued=rescued, bites=bites,
                   conditions={n: {k: r[k] for k in ("final_pop", "eq_pop", "juv_uf_eq", "adt_uf_eq",
                                                     "juv_frac_eq")} for n, r in res.items()},
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2i.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, rescued and bites)
    print(f"[2i] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, good):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['final_pop']}</td><td>{r['eq_pop']:.0f}</td><td>{r['juv_uf_eq']*100:.1f}%</td>"
        f"<td>{r['adt_uf_eq']*100:.1f}%</td><td>{r['juv_frac_eq']*100:.0f}%</td></tr>" for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Resource-Ecology C.2b — provisioning</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Resource-Ecology · Phase C.2b — mother-linked provisioning</h1>
<p>A mother's harvest overflow (above her cap) is redirected to her dependent children; on a poor/depleted
cell she has little overflow → her children dwell lean. Depletion ON, synergy ON, seed {SEED}, {STEPS} steps.
<b>Test:</b> does provisioning rescue the population from C.2a extinction AND make JUVENILES (not adults)
the lean-but-alive class the food economy could never produce (R-7/R-8)?</p>
<div class="box {'ok' if good else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>final pop</th><th>eq pop</th><th>juv under-fed</th><th>adult under-fed</th><th>juv frac</th></tr>{rows}</table>
<h2>Population rescue &amp; who dwells lean</h2><div class="fig">{img('ts')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">C.2b · {time.strftime('%Y-%m-%d')} · non-spatial
mother-link (co-move deferred) · flow-based overflow redirect · depletion-lite backdrop · 1 seed · μ_max=2.5 default.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2i.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
