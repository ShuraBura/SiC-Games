"""Demographic stage — STEP 2, stage 2b: terrain-modulator ABLATION.

Wires the three live a2 modulators (terrain-risk × density-disease × nutrition-synergy; pathogen
OFF, deferred to the climate stage) onto the demography core, and measures — per modulator and all
together — how far each pulls the demographic carrying capacity BELOW the pure-food equilibrium (the
2a-pre ~95%-of-ceiling plateau), and how the population sorts across terrain (occupancy vs risk).

Anchors (MODEL_SPEC §4.3.3): risk-scale (Hiwi accidents ~10%), μ_max≈2.5 (Pelletier 1994), density
δ/ρ_half = free lever. 40×40 sub-window, 1 seed (first-pass shapes), 2000 steps.

Run:  py -3 -u outputs/phase1_demography_step2/run_2b.py
"""
from __future__ import annotations
import base64, io, json, os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

import sys as _sys
try:                              # Windows console is cp1252; force utf-8 so unicode prints don't crash
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import N, generate_world
import importlib.util as _iu
_spec = _iu.spec_from_file_location("r2pre", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                          "run_2a_pre.py"))
_r2 = _iu.module_from_spec(_spec); _spec.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions
X0, Y0, PATCH = _r2.X0, _r2.Y0, _r2.PATCH

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEED = 400, 2000, 42
CONDITIONS = {
    "baseline (all off)": dict(),
    "+risk": dict(enable_terrain_risk=True),
    "+density-disease": dict(enable_density_disease=True),
    "+synergy": dict(enable_nutrition_synergy=True),
    "all (risk+dens+syn)": dict(enable_terrain_risk=True, enable_density_disease=True,
                                enable_nutrition_synergy=True),
}


def run_one(flags, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos, demography_cfg=DemographyConfig(**flags))
    pop = []
    agent_steps = 0
    for _ in range(STEPS):
        w.step()
        pop.append(len(w.agent_list))
        agent_steps += len(w.agent_list)
        if not w.agent_list:
            break
    # equilibrium = last-15% mean
    eq = float(np.mean(pop[int(0.85 * len(pop)):])) if pop[-1] else 0.0
    # spatial sorting: per-cell occupancy vs terrain risk, over occupied patch land cells
    occ = np.zeros((N, N))
    for a in w.agent_list:
        occ[a.pos[1], a.pos[0]] += 1
    patch = np.zeros((N, N), bool); patch[Y0:Y0 + PATCH, X0:X0 + PATCH] = True
    sel = patch & (fields.isWater == 0) & (occ > 0)
    corr = float(spearmanr(occ[sel], fields.risk[sel]).statistic) if sel.sum() > 10 else float("nan")
    cap_frac = w.a2_cap_hits / max(1, agent_steps)
    return dict(eq=eq, ceiling=cap.ceiling, corr=corr, cap_frac=cap_frac, pop=pop, occ=occ,
                risk=fields.risk.copy())


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time()
    prog = os.path.join(OUT, "progress_2b.txt")
    res = {}
    base_eq = None
    for i, (name, flags) in enumerate(CONDITIONS.items()):
        r = run_one(flags)
        res[name] = r
        if base_eq is None:
            base_eq = r["eq"]
        shift = 100 * (1 - r["eq"] / base_eq) if base_eq else 0.0
        msg = (f"{name}: eq {r['eq']:.0f} ({100*r['eq']/r['ceiling']:.0f}% of ceiling, "
               f"{shift:+.0f}% vs baseline) | occ-risk rho={r['corr']:+.2f} | cap-bind {r['cap_frac']*100:.1f}%")
        print(f"[2b] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f:
            f.write(f"2b: {i+1}/{len(CONDITIONS)} | {msg} | elapsed {time.time()-t0:.0f}s\n")

    # ablation additivity check (red-team M-1): sum of single-modulator shifts ≈ all-on shift
    def shiftpct(name): return 100 * (1 - res[name]["eq"] / base_eq)
    singles = shiftpct("+risk") + shiftpct("+density-disease") + shiftpct("+synergy")
    allon = shiftpct("all (risk+dens+syn)")

    # plots
    figs = {}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for name, r in res.items():
        ax.plot(np.arange(len(r["pop"])) / 12.0, r["pop"], lw=1.1, label=name)
    ax.axhline(res["baseline (all off)"]["ceiling"], color="k", ls="--", lw=0.8, label="food ceiling")
    ax.set_xlabel("year"); ax.set_ylabel("population"); ax.grid(alpha=0.25); ax.legend(fontsize=8)
    ax.set_title("2b ablation — each a2 modulator pulls the carrying capacity below the food ceiling")
    figs["pop"] = fig_b64(fig)

    base, allr = res["baseline (all off)"], res["all (risk+dens+syn)"]
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    for ax, r, ttl in ((axs[0], base, "baseline (off)"), (axs[1], allr, "all modulators on")):
        o = r["occ"][Y0:Y0 + PATCH, X0:X0 + PATCH]
        im = ax.imshow(np.where(o > 0, o, np.nan), cmap="inferno", origin="lower")
        ax.set_title(f"occupancy — {ttl}"); ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, shrink=0.8)
    figs["occ"] = fig_b64(fig)

    results = dict(
        base_eq=base_eq, food_ceiling=base["ceiling"],
        conditions={n: dict(eq=r["eq"], pct_ceiling=100 * r["eq"] / r["ceiling"],
                            shift_vs_baseline_pct=100 * (1 - r["eq"] / base_eq),
                            occ_risk_spearman=r["corr"], cap_bind_frac=r["cap_frac"])
                    for n, r in res.items()},
        ablation_additivity=dict(sum_of_singles_pct=singles, all_on_pct=allon),
        founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2b.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, res, base_eq, singles, allon)
    print(f"[2b] done in {time.time()-t0:.0f}s. additivity: singles {singles:+.0f}% vs all-on {allon:+.0f}%.", flush=True)


def _write_html(figs, res, base_eq, singles, allon):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rows = "".join(
        f"<tr><td>{n}</td><td>{r['eq']:.0f}</td><td>{100*r['eq']/r['ceiling']:.0f}%</td>"
        f"<td>{100*(1-r['eq']/base_eq):+.0f}%</td><td>{r['corr']:+.2f}</td><td>{r['cap_frac']*100:.1f}%</td></tr>"
        for n, r in res.items())
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>2b modulator ablation</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282;margin-top:28px}}
.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}
th{{background:#edf2f7}}td:first-child{{text-align:left}}.fig{{margin:16px 0;text-align:center}}code{{background:#edf2f7;padding:1px 5px;border-radius:3px}}</style></head><body>
<h1>Demographic stage · 2b — terrain-modulator ablation</h1>
<p>Three live <code>a2</code> modulators (terrain-risk × density-disease × nutrition-synergy; pathogen OFF,
deferred to the climate stage) on the demography core, 40×40 sub-window, seed {SEED}, {STEPS} steps.
Anchors (MODEL_SPEC §4.3.3): risk-scale (Hiwi ~10%), μ_max≈2.5 (Pelletier), density = free lever.</p>
<div class="box"><b>Each modulator pulls the demographic carrying capacity below the pure-food ceiling</b>
— the 2a finding (modulators shift the equilibrium DOWN). Ablation-additivity (red-team M-1): sum of
single-modulator shifts {singles:+.0f}% vs all-on {allon:+.0f}% (≈ ⇒ near-independent; ≫ ⇒ interaction).</div>
<table><tr><th>condition</th><th>equilibrium</th><th>% of food ceiling</th><th>shift vs baseline</th><th>occ–risk ρ</th><th>a2-cap bind</th></tr>{rows}</table>
<p>Negative <b>occ–risk ρ</b> = the population sorts off high-risk cells (the spatial-sorting prediction).
<b>a2-cap bind</b> should be small (else the cap is doing demographic work — red-team m-4).</p>
<h2>Population trajectories</h2><div class="fig">{img('pop')}</div>
<h2>Spatial occupancy — baseline vs all-on</h2><div class="fig">{img('occ')}</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">2b · {time.strftime('%Y-%m-%d')} · first-pass shapes
(1 seed, default free knobs δ=1.0/ρ_half=0.2); full calibration + multi-seed + 100×100 confirmation next.</p>
</body></html>"""
    with open(os.path.join(OUT, "report_2b.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
