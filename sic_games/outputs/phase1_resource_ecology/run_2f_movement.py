"""Resource-Ecology — Phase B: CONSTRAINED MOVEMENT (break the ideal free distribution).

R-7: seasonality + depletion only lower the CC — under the ideal free distribution (agents diffuse to
equalize per-capita yield) every survivor ends up fed at the margin, so the graded modulators never bite.
This tests the red-team's structural fix: a MOVE COST (`move_cost_flat`, already in the substrate; a pure
DECISION friction subtracted from cell utility, NOT a wealth debit — so it adds stickiness without
re-lowering the mean) makes agents tolerate a depleting cell before paying to leave → an ideal-DESPOTIC
distribution where fitness is NOT equalized → some agents dwell chronically lean → synergy fires.

TWO read-outs (the reason B is benchmarkable before C):
  1. MOVEMENT REALISM — emergent residential moves/yr + range, to be tuned into the Binford 2001 /
     Kelly 2013 mobility envelope (the external lit benchmark).
  2. MECHANISM — does the under-fed fraction (synergy>1.2) finally rise off the R-7 zero?

Depletion ON (the heterogeneity to get stuck in), seasonality OFF (isolate movement). Baseline = the
current unconstrained diffusion (move_cost=0). [PROVISIONAL: depletion-lite backdrop; move_cost not yet
lit-tuned — this run finds the response curve; the Binford tune is the next step.]
Run:  py -3 -u outputs/phase1_resource_ecology/run_2f_movement.py
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
from sic_games.demography import DemographyConfig, synergy_mult
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_here = os.path.dirname(os.path.abspath(__file__))
_e = _iu.spec_from_file_location("r2e", os.path.join(_here, "run_2e_depletion.py"))
_r2e = _iu.module_from_spec(_e); _e.loader.exec_module(_r2e)
DepletableSeasonalCapacity = _r2e.DepletableSeasonalCapacity
knobs_for, patch_positions = _r2e.knobs_for, _r2e.patch_positions
BURN = _r2e.BURN

OUT = _here
FOUNDERS, STEPS, SEED = 400, 2500, 42
WINDOW = 24                       # final-window over which moves/yr + range are measured
MULTS = [0.0, 0.05, 0.15, 0.35]   # move_cost = mult * BURN  (0.0 = baseline / unconstrained IFD)


def run_one(mult, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = DepletableSeasonalCapacity(fields, s_min=1.0)          # depletion ON, season OFF
    pos = patch_positions(fields, FOUNDERS, rng)
    move_cost = mult * BURN
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=move_cost),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_nutrition_synergy=True))
    pop, synfrac = [], []
    tracks: dict[int, list] = {}                                  # agent_id -> [pos,...] over final window
    track_from = STEPS - WINDOW
    for step in range(STEPS):
        cap.t = step
        w.step()
        al = w.agent_list
        pop.append(len(al))
        if not al:
            break
        s = np.array([synergy_mult(a._fed_reserve, a.reserve_floor, 100000, 2.5) for a in al])
        synfrac.append(float(np.mean(s > 1.2)))
        if step >= track_from:
            for a in al:
                tracks.setdefault(a.unique_id, []).append(tuple(a.pos))
        if step == STEPS - 1:
            occ = {}
            for a in al:
                occ[tuple(a.pos)] = occ.get(tuple(a.pos), 0) + 1
            occ_vals = np.array(list(occ.values()), float)
            occ_cv = float(occ_vals.std() / occ_vals.mean()) if len(occ_vals) else 0.0

    # movement metrics over agents present the whole window
    full = [p for p in tracks.values() if len(p) == WINDOW]
    moves = [sum(p[i] != p[i - 1] for i in range(1, len(p))) for p in full]
    rng_cells = [len(set(p)) for p in full]
    moves_yr = float(np.mean(moves)) * (12.0 / WINDOW) if full else 0.0
    range_cells = float(np.mean(rng_cells)) if full else 0.0
    tail = slice(int(0.6 * len(pop)), None)
    return dict(mult=mult, move_cost=move_cost, pop=pop, synfrac=synfrac,
                eq_pop=float(np.mean(pop[tail])) if pop[-1] else 0.0,
                synfrac_eq=float(np.mean(synfrac[tail])) if pop[-1] else 0.0,
                synfrac_max=float(np.max(synfrac[tail])) if pop[-1] else 0.0,
                moves_yr=moves_yr, range_cells=range_cells, occ_cv=occ_cv if pop[-1] else 0.0,
                n_tracked=len(full))


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2f.txt")
    res = []
    for mult in MULTS:
        r = run_one(mult); res.append(r)
        tag = "baseline (IFD)" if mult == 0.0 else f"move_cost {mult:.2f}*burn"
        msg = (f"{tag}: eq_pop {r['eq_pop']:.0f} | moves/yr {r['moves_yr']:.1f} | range {r['range_cells']:.1f} "
               f"cells | occ_CV {r['occ_cv']:.2f} | under-fed {r['synfrac_eq']*100:.1f}% (max {r['synfrac_max']*100:.1f}%)")
        print(f"[2f] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2f: {msg} | elapsed {time.time()-t0:.0f}s\n")

    base, top = res[0], res[-1]
    bites = any(r["synfrac_eq"] > 0.02 for r in res[1:])
    verdict = (f"CONSTRAINED MOVEMENT BITES — stickiness drops moves/yr {base['moves_yr']:.1f}->{top['moves_yr']:.1f} "
               f"and pushes the under-fed fraction off zero (max {max(r['synfrac_eq'] for r in res)*100:.1f}%). "
               f"Breaking the IFD does produce per-agent variance — R-7 confirmed. Next: tune move_cost to the "
               f"Binford/Kelly mobility window, then Phase C."
               if bites else
               f"STILL INERT — even at move_cost {MULTS[-1]:.2f}*burn (moves/yr {top['moves_yr']:.1f}) the under-fed "
               f"fraction stays ~0. Stickiness alone does not trap agents lean (the despotic claim or graded "
               f"reserves are needed). Escalate the constraint or go to provisioning.")

    figs = {}
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    mc = [r["mult"] for r in res]
    ax[0].plot(mc, [r["moves_yr"] for r in res], "o-", color="#3182ce", label="moves/yr")
    ax[0].set_xlabel("move_cost (×burn)"); ax[0].set_ylabel("residential moves/yr", color="#3182ce")
    ax[0].tick_params(axis="y", labelcolor="#3182ce"); ax[0].grid(alpha=0.25)
    a0b = ax[0].twinx(); a0b.plot(mc, [r["range_cells"] for r in res], "s--", color="#dd6b20")
    a0b.set_ylabel("range (distinct cells/yr)", color="#dd6b20"); a0b.tick_params(axis="y", labelcolor="#dd6b20")
    ax[0].set_title("Mobility vs move cost (tune target: Binford/Kelly)")
    ax[1].plot(mc, [r["synfrac_eq"] * 100 for r in res], "o-", color="#e53e3e", label="mean")
    ax[1].plot(mc, [r["synfrac_max"] * 100 for r in res], "o:", color="#e53e3e", alpha=0.5, label="max")
    ax[1].set_xlabel("move_cost (×burn)"); ax[1].set_ylabel("% agents under-fed (synergy>1.2)")
    ax[1].axhline(0, color="#999", lw=0.6); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.25)
    ax[1].set_title("Does breaking the IFD create per-agent scarcity?")
    figs["sweep"] = fig_b64(fig)

    results = dict(verdict=verdict, bites=bites, window=WINDOW,
                   conditions=[{k: r[k] for k in ("mult", "move_cost", "eq_pop", "moves_yr", "range_cells",
                                                  "occ_cv", "synfrac_eq", "synfrac_max", "n_tracked")} for r in res],
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2f.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, verdict, bites)
    print(f"[2f] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, res, verdict, bites):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{'baseline (IFD)' if r['mult']==0 else f'{r['mult']:.2f}×burn'}</td><td>{r['eq_pop']:.0f}</td>"
        f"<td>{r['moves_yr']:.1f}</td><td>{r['range_cells']:.1f}</td><td>{r['occ_cv']:.2f}</td>"
        f"<td>{r['synfrac_eq']*100:.1f}%</td><td>{r['synfrac_max']*100:.1f}%</td></tr>" for r in res)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Resource-Ecology B — constrained movement</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1040px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282}}.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Resource-Ecology · Phase B — constrained movement (break the IFD)</h1>
<p>A move cost (decision friction, not a wealth debit) makes agents tolerate a depleting cell before
leaving → ideal-despotic distribution → some agents dwell chronically lean. Depletion ON, season OFF,
synergy ON, 40×40 sub-window, seed {SEED}, {STEPS} steps. Baseline = unconstrained diffusion (the IFD).
<b>Test:</b> does breaking the IFD push the under-fed fraction off the R-7 zero, and what is the
mobility response (to be tuned to Binford/Kelly)?</p>
<div class="box {'ok' if bites else 'flag'}"><b>{verdict}</b></div>
<table><tr><th>condition</th><th>eq. pop</th><th>moves/yr</th><th>range (cells/yr)</th><th>occ CV</th><th>under-fed mean</th><th>under-fed max</th></tr>{rows}</table>
<h2>Mobility &amp; per-agent scarcity vs move cost</h2><div class="fig">{img('sweep')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">B · {time.strftime('%Y-%m-%d')} · move_cost not yet
lit-tuned (this is the response curve) · 1 cell = 10 km, 1 step = 1 month · depletion-lite backdrop · 1 seed.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2f.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
