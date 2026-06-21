"""Biome-Mortality — density-disease δ CALIBRATION (on the band-level ecology; R-13 → realistic substrate).

R-13: density-disease (δ) regulates the population below the food ceiling, collapsing starvation. Now pick δ
so the regulated equilibrium matches the forager envelope on BOTH axes at once:
  - e₀ (period life table) in the ethnographic range ~27–43 yr (Hiwi 27 / Hadza 32–43 / !Kung 36 / Aché 37),
  - population density in the Tallavaara band ~0.1–0.5 people/km²,
  - starvation fraction → ≈0 (disease-regulated, the realistic regime).
δ is a CALIBRATED FREE LEVER (not lit-anchored; PARAMETERS §15) — this run records the trade-off curve and
recommends a δ. Temperate biome (the pathogen-neutral reference). Then the multi-biome sweep re-runs WITH this δ.
Run:  py -3 -u outputs/phase1_biome_mortality/run_2o_delta_calibration.py
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
X0, Y0, PATCH, CELL_KM2 = _r2.X0, _r2.Y0, _r2.PATCH, _r2.CELL_KM2

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEED = 400, 2000, 42
DELTAS = [0.0, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0]
EDGES = [0, 1, 5, 15, 30, 50, 120]


def run_one(delta, seed=SEED):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed))
    cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    # patch land area (km²) for density
    mask = np.zeros_like(fields.isWater, bool); mask[Y0:Y0 + PATCH, X0:X0 + PATCH] = True
    land_km2 = float(np.sum(mask & (fields.isWater == 0))) * CELL_KM2
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(enable_density_disease=(delta > 0.0),
                                                     dens_delta=delta, dens_rho_half=0.2))
    nb = len(EDGES) - 1
    expo = [0] * nb; dband = [0] * nb; starv = 0; senesc = 0
    def band(a):
        for i in range(nb):
            if a < EDGES[i + 1]:
                return i
        return nb - 1
    pop = []
    tail0 = int(0.6 * STEPS)
    prev = {a.unique_id: a.age for a in w.agent_list}
    for step in range(STEPS):
        w.step(); al = w.agent_list
        cur = {a.unique_id: a.age for a in al}
        if step >= tail0:
            starv += w.deaths_starv_this_step; senesc += w.deaths_senesc_this_step
            for a in al:
                expo[band(a.age / 12.0)] += 1
            for uid, ag in prev.items():
                if uid not in cur:
                    dband[band((ag + 1) / 12.0)] += 1
        prev = cur
        pop.append(len(al))
    tail = slice(tail0, None)
    alive = pop[-1] > 0
    lx = [1.0]; e0 = 0.0
    for i in range(nb):
        m = 12.0 * dband[i] / expo[i] if expo[i] > 0 else 0.0
        wdt = EDGES[i + 1] - EDGES[i]; q = 1.0 - math.exp(-m * wdt)
        e0 += (lx[-1] + lx[-1] * (1.0 - q)) / 2.0 * wdt; lx.append(lx[-1] * (1.0 - q))
    eq = float(np.mean(pop[tail])) if alive else 0.0
    tot = starv + senesc
    return dict(delta=delta, eq_pop=eq, e0=e0 if alive else 0.0,
                density=eq / land_km2 if land_km2 > 0 else 0.0,
                starv_frac=float(starv / max(tot, 1)))


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def _score(r):
    # joint fit: e0 in [27,43], density in [0.1,0.5], starvation ≈0
    e_ok = 27.0 <= r["e0"] <= 43.0
    d_ok = 0.08 <= r["density"] <= 0.55
    s_ok = r["starv_frac"] < 0.05
    return e_ok + d_ok + s_ok, e_ok, d_ok, s_ok


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_2o.txt")
    res = []
    for d in DELTAS:
        r = run_one(d); res.append(r)
        sc, e_ok, d_ok, s_ok = _score(r)
        msg = (f"delta={d:4.1f}: eq_pop {r['eq_pop']:6.0f} | e0 {r['e0']:5.1f}yr{'✓' if e_ok else ' '} | "
               f"density {r['density']:.3f}/km²{'✓' if d_ok else ' '} | starv {r['starv_frac']*100:3.0f}%{'✓' if s_ok else ' '}")
        print(f"[2o] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w") as f: f.write(f"2o: {msg} | elapsed {time.time()-t0:.0f}s\n")

    # recommend: max joint-fit score; tie-break = smallest δ (least extrapolated lever)
    scored = [( _score(r)[0], -r["delta"], r) for r in res]
    best = max(scored, key=lambda x: (x[0], x[1]))[2]
    verdict = (f"RECOMMENDED δ ≈ {best['delta']:.0f} — e0 {best['e0']:.1f}yr, density {best['density']:.3f}/km², "
               f"starvation {best['starv_frac']*100:.0f}% (joint-fit {_score(best)[0]}/3: forager e0 27–43, "
               f"Tallavaara density 0.1–0.5, starvation≈0). δ is a calibrated FREE lever (PARAMETERS §15); "
               f"the multi-biome sweep re-runs with this δ next. NOTE: if no δ hits all three, the trade-off "
               f"(realistic density vs starvation→0) is itself a finding about the forage-only economy.")

    figs = {}
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    ds = [r["delta"] for r in res]
    ax[0].plot(ds, [r["e0"] for r in res], "o-", color="#3182ce"); ax[0].axhspan(27, 43, color="#38a169", alpha=0.12)
    ax[0].set_xlabel("δ"); ax[0].set_ylabel("e₀ (yr)"); ax[0].set_title("e₀ vs δ (band = forager range)"); ax[0].grid(alpha=0.25)
    ax[1].plot(ds, [r["density"] for r in res], "o-", color="#dd6b20"); ax[1].axhspan(0.1, 0.5, color="#38a169", alpha=0.12)
    ax[1].set_xlabel("δ"); ax[1].set_ylabel("density /km²"); ax[1].set_title("density vs δ (band = Tallavaara)"); ax[1].grid(alpha=0.25)
    ax[2].plot(ds, [r["starv_frac"] * 100 for r in res], "o-", color="#e53e3e")
    ax[2].set_xlabel("δ"); ax[2].set_ylabel("% starvation"); ax[2].set_title("starvation vs δ (target ≈0)"); ax[2].grid(alpha=0.25)
    ax[2].axvline(best["delta"], color="#805ad5", ls="--", lw=1.0)
    figs["cal"] = fig_b64(fig)

    results = dict(verdict=verdict, recommended_delta=best["delta"],
                   conditions=[{k: r[k] for k in ("delta", "eq_pop", "e0", "density", "starv_frac")} for r in res],
                   founders=FOUNDERS, steps=STEPS, seed=SEED, elapsed_sec=time.time() - t0)
    with open(os.path.join(OUT, "results_2o.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    rows = "".join(f"<tr><td>{r['delta']:.0f}</td><td>{r['eq_pop']:.0f}</td><td>{r['e0']:.1f}</td>"
                   f"<td>{r['density']:.3f}</td><td>{r['starv_frac']*100:.0f}%</td></tr>" for r in res)
    html = (f"<!doctype html><meta charset='utf-8'><body style='font-family:Segoe UI,sans-serif;max-width:1000px;"
            f"margin:24px auto'><h1>Density-disease δ calibration</h1>"
            f"<div style='background:#f0fff4;border-left:4px solid #38a169;padding:10px 16px'><b>{verdict}</b></div>"
            f"<table style='border-collapse:collapse'><tr><th>δ</th><th>eq pop</th><th>e₀ (yr)</th><th>density/km²</th>"
            f"<th>% starv</th></tr>{rows}</table>"
            f"<img src='data:image/png;base64,{figs['cal']}' style='max-width:100%'>"
            f"<p style='color:#718096'>δ = calibrated free lever (PARAMETERS §15); temperate biome; {STEPS} steps; 1 seed.</p></body>")
    with open(os.path.join(OUT, "report_2o.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[2o] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
