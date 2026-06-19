"""Demographic stage — STEP 2, stage 2a-pre: STABILITY TEST (red-team B-1).

Runs the demographic core (sex-specific Siler + IBI, modulators OFF) on a 100×100 terrain
SUB-WINDOW (red-team m-1: a same-resolution patch, NOT a rescaled world) with the CC-1 food
economy, and asks the one question the Step-2 blueprint rests on:

    Does the +3.3%/yr Aché-calibrated population SETTLE against the density-dependent food wall,
    or OVERSHOOT → oscillate / collapse?

A-3 gave no answer (it was a frozen, non-reproducing fill). Gate: bounded settling — no extinction
across seeds; post-settling peak-to-trough oscillation below a pre-registered threshold.

Run:  py -3 -u outputs/phase1_demography_step2/run_2a_pre.py
"""
from __future__ import annotations
import base64, io, json, os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import N, generate_world

OUT = os.path.dirname(os.path.abspath(__file__))
BURN = 75000.0
NPP_THRESH, DENS_SLOPE, DENS_CAP, CELL_KM2 = 1360.0, 0.3, 0.5, 100.0
PATCH = 40                # sub-window edge (same-resolution patch of the 100×100 world)
X0 = Y0 = (N - PATCH) // 2
FOUNDERS = 400
STEPS = 2500
SEEDS = [42, 43, 44]
OSC_THRESHOLD = 0.25      # pre-registered: post-settling trough ≥ (1−0.25)·plateau → "bounded"


class SubWindowCapacity:
    """CC-1 capacity field masked to a PATCH sub-window (0 capacity outside → agents stay in it)."""
    def __init__(self, fields):
        self.width = self.height = N
        dens = np.minimum(DENS_CAP, DENS_SLOPE * fields.npp_gm2 / NPP_THRESH)
        E = dens * CELL_KM2 * BURN
        mask = np.zeros((N, N), bool); mask[Y0:Y0 + PATCH, X0:X0 + PATCH] = True
        E[~mask] = 0.0
        self._E = E
        self.ceiling = float((dens * CELL_KM2)[mask & (fields.isWater == 0)].sum())  # patch K-sum
    def level(self, x, y): return float(self._E[y, x])
    def harvest(self, x, y): return float(self._E[y, x])


def knobs_for(seed):
    return {"seedStr": f"world{seed}", "relief": 0.50, "rough": 0.50,
            "waterK": 0.30, "forestK": 0.55, "aridK": 0.40}


def patch_positions(fields, n, rng):
    land = [(x, y) for y in range(Y0, Y0 + PATCH) for x in range(X0, X0 + PATCH)
            if fields.isWater[y, x] == 0]
    return [land[rng.randrange(len(land))] for _ in range(n)]


def run_one(seed):
    rng = __import__("random").Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(),
                     terrain_knobs=knobs_for(seed), game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
                                                   movement_mode="diffusion", contest_exponent=0.0,
                                                   move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig())
    pop, births, deaths, res = [], [], [], []
    for _ in range(STEPS):
        w.step()
        al = w.agent_list
        pop.append(len(al))
        births.append(w.births_this_step)
        deaths.append(w.deaths_starv_this_step + w.deaths_senesc_this_step)
        res.append(float(np.mean([a.wealth for a in al])) if al else 0.0)
        if not al:
            break
    return dict(seed=seed, ceiling=cap.ceiling, pop=pop, births=births, deaths=deaths, res=res)


def stability(pop):
    """Bounded-settling metric measured AFTER settling onset — the GROWTH phase must not be counted
    as a 'trough'. plateau = mean of the last 15%; onset = first step reaching 0.9·plateau;
    settled_trough / settled_peak = min / max over [onset, end] relative to plateau (oscillation)."""
    pop = np.asarray(pop, float)
    if pop[-1] == 0:
        return dict(extinct=True, plateau=0.0, onset=len(pop), settled_trough=0.0, settled_peak=0.0)
    n = len(pop)
    plateau = pop[int(0.85 * n):].mean()
    onset = int(np.argmax(pop >= 0.9 * plateau))
    post = pop[onset:]
    return dict(extinct=False, plateau=float(plateau), onset=onset,
                settled_trough=float(post.min() / plateau), settled_peak=float(post.max() / plateau))


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time()
    prog = os.path.join(OUT, "progress.txt")
    runs = []
    for sd in SEEDS:
        r = run_one(sd)
        r["stab"] = stability(r["pop"])
        runs.append(r)
        msg = (f"seed {sd}: final {r['pop'][-1]} | plateau {r['stab']['plateau']:.0f} "
               f"| settled_peak {r['stab']['settled_peak']:.2f}x | settled_trough {r['stab']['settled_trough']:.2f}x "
               f"| onset~step{r['stab']['onset']} | ceiling {r['ceiling']:.0f}")
        print(f"[2a-pre] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f:
            f.write(f"2a-pre: {len(runs)}/{len(SEEDS)} done | {msg} | elapsed {time.time()-t0:.0f}s\n")

    extinct = any(r["stab"]["extinct"] for r in runs)
    ok = [r["stab"] for r in runs if not r["stab"]["extinct"]]
    bounded = (not extinct) and all(s["settled_trough"] >= (1 - OSC_THRESHOLD)
                                    and s["settled_peak"] <= (1 + OSC_THRESHOLD) for s in ok)
    verdict = ("BOUNDED SETTLING — food density-dependence stabilizes the growing population"
               if bounded else
               "NOT BOUNDED — overshoot/oscillation/collapse; food alone does NOT stabilize")

    # plots
    figs = {}
    cols = {42: "#3182ce", 43: "#e53e3e", 44: "#38a169"}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for r in runs:
        yr = np.arange(len(r["pop"])) / 12.0
        ax.plot(yr, r["pop"], color=cols[r["seed"]], lw=1.1, label=f"seed {r['seed']}")
        ax.axhline(r["stab"]["plateau"], color=cols[r["seed"]], ls=":", lw=0.7)
    ax.axhline(runs[0]["ceiling"], color="k", ls="--", lw=0.9, label=f"food ceiling {runs[0]['ceiling']:.0f}")
    ax.set_xlabel("year"); ax.set_ylabel("population (patch)"); ax.grid(alpha=0.25); ax.legend(fontsize=8)
    ax.set_title("2a-pre stability test — does the +3.3%/yr population settle or overshoot?")
    figs["pop"] = fig_b64(fig)

    rep = runs[0]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    def yearly(a): a = np.array(a, float); m = len(a)//12*12; return a[:m].reshape(-1, 12).sum(1)
    ax[0].plot(yearly(rep["births"]), color="#38a169", label="births/yr")
    ax[0].plot(yearly(rep["deaths"]), color="#e53e3e", label="deaths/yr")
    ax[0].set_title(f"births vs deaths (seed {rep['seed']})"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    ax[0].set_xlabel("year")
    ax[1].plot(np.arange(len(rep["res"]))/12.0, rep["res"], color="#805ad5")
    ax[1].axhline(20000, color="#e53e3e", ls=":", lw=0.8, label="starvation floor")
    ax[1].set_title("mean reserve (kcal)"); ax[1].set_xlabel("year"); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.25)
    figs["dyn"] = fig_b64(fig)

    results = dict(verdict=verdict, bounded=bounded, extinct=extinct,
                   osc_threshold=OSC_THRESHOLD, patch=PATCH, founders=FOUNDERS, steps=STEPS,
                   runs=[dict(seed=r["seed"], ceiling=r["ceiling"], stab=r["stab"],
                              pop_every25=r["pop"][::25]) for r in runs],
                   elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, runs, verdict, bounded)
    print(f"[2a-pre] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


def _write_html(figs, runs, verdict, bounded):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{r['seed']}</td><td>{r['pop'][-1]}</td><td>{r['stab']['plateau']:.0f}</td>"
        f"<td>{r['stab']['settled_peak']:.2f}×</td><td>{r['stab']['settled_trough']:.2f}×</td>"
        f"<td>{r['ceiling']:.0f}</td></tr>" for r in runs)
    cls = "ok" if bounded else "flag"
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>2a-pre stability test</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282;margin-top:28px}}
.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}
.ok{{border-left-color:#38a169;background:#f0fff4}}.flag{{border-left-color:#e53e3e;background:#fff5f5}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}
th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Demographic stage · 2a-pre stability test (red-team B-1)</h1>
<p>Sex-specific Siler + IBI (modulators OFF) on a {PATCH}×{PATCH} terrain sub-window with the CC-1 food
economy, {FOUNDERS} staggered founders, {STEPS} steps, {len(runs)} seeds. <b>The question:</b> does the
+3.3%/yr Aché-calibrated population settle against the density-dependent food wall, or overshoot?</p>
<div class="box {cls}"><b>VERDICT: {verdict}.</b> Gate: no extinction across seeds AND, after settling
onset, trough ≥ 0.75× plateau AND peak ≤ 1.25× plateau (oscillation bounded).</div>
<table><tr><th>seed</th><th>final</th><th>plateau</th><th>settled peak</th><th>settled trough</th><th>food ceiling</th></tr>{rows}</table>
<h2>Population trajectories</h2><div class="fig">{img('pop')}</div>
<h2>Births/deaths &amp; reserve (seed {runs[0]['seed']})</h2><div class="fig">{img('dyn')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">2a-pre · {time.strftime('%Y-%m-%d')} · demography
core opt-in on TerrainWorld; modulators OFF; energetic fertility modifier OFF (strict test).</p>
</body></html>"""
    with open(os.path.join(OUT, "report.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
