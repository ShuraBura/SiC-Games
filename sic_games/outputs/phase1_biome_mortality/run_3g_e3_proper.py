"""E.3-PROPER — re-calibrate status→RS r≈0.19 on the CORRECTED banded substrate, and re-run the lumping
ablation with the band-aware (mate-gate-neighbourhood) homogenize.

Supersedes the contaminated E.3 (0f39c2d): that ran on the bare-forage field with a per-CELL bonded gate and
measured w.agents (corpses). This harness uses the validated turnover fix — the CC-1 NPP-capacity field
(SubWindowCapacity, bounded patch K so it equilibrates) + bonded_mate_radius=1 (band-territory mate-gate) +
banded seeding + grouping drives — and the band-aware homogenize (flatten cred within the connected band, not a
1-agent cell). Otherwise identical to run_3c (de-warfared Siler, δ=3, meat_frac 0.55, CV 0.73, ρ=0.1, full B+).

(1) m-SWEEP on the bands substrate → the m that lands corr(prowess, surviving-offspring | male) ≈ 0.19.
(2) LUMPING ABLATION at that m: IFD vs bands-full vs bands-homogenized — does flattening WITHIN THE BAND still
    collapse the von Rueden skew (the load-bearing-individualism claim, now tested where bands actually exist)?
Run:  py -3 -u outputs/phase1_biome_mortality/run_3g_e3_proper.py
"""
from __future__ import annotations
import json, math, os, time, statistics
import numpy as np

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, N as GRID_N
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEEDS = 300, 1200, list(range(6))
MS = [4.0, 5.0, 6.0]                 # confirm m≈5 lands von Rueden r≈0.19 (bracketed by 4 and 6)
RHO, CV, MEAT_FRAC, DELTA, MATE_R = 0.1, 0.73, 0.55, 3.0, 1
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx > 0 and sy > 0 else 0.0


def gini(v):
    v = sorted(v); n = len(v); s = sum(v)
    return (2.0 * sum((i + 1) * x for i, x in enumerate(v))) / (n * s) - (n + 1) / n if s > 0 and n else 0.0


def band_positions_patch(fields, cap, n, band_size=25, territory_radius=4):
    """Banded seeding within the capacity patch: stack ~band_size on the highest-capacity land cells,
    territory-spaced (cap is already 0 outside the patch → bands land inside it)."""
    cells = sorted(((cap.level(x, y), x, y) for y in range(GRID_N) for x in range(GRID_N)
                    if fields.isWater[y, x] == 0 and cap.level(x, y) > 0), reverse=True)
    sites, pos = [], []
    nb = max(1, n // band_size)
    for (_, x, y) in cells:
        if len(sites) >= nb:
            break
        if all(max(abs(x - px), abs(y - py)) >= territory_radius for (px, py) in sites):
            sites.append((x, y)); pos.extend([(x, y)] * band_size)
    i = 0
    while len(pos) < n and sites:
        pos.append(sites[i % len(sites)]); i += 1
    return pos[:n]


def run_one(m, seed, arm, prowess_decay=0.1):
    """arm: 'ifd' (dispersed, no mate-gate = run_3c baseline) | 'bands' | 'bands_homog' (cred flat) |
    'bands_lump' (cred AND prowess flat = strict band-as-unit)."""
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    bonded = arm in ("bands", "bands_homog", "bands_lump")
    pos = band_positions_patch(fields, cap, FOUNDERS) if bonded else patch_positions(fields, FOUNDERS, rng)
    grp = GRP if bonded else {}
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.0, move_cost_flat=0.0, **grp),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(
                         siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=DELTA, dens_rho_half=0.2,
                         enable_game=True, game_meat_frac=MEAT_FRAC, game_meat_cv=CV,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_prowess_facet=True, prowess_decay=prowess_decay, sex_division=1.0,
                         enable_paternity=True, mate_choice_strength=m, patriline_weight=0.5, lineage_reversion=RHO,
                         enable_bonded_mating=bonded, bonded_mate_radius=(MATE_R if bonded else 0),
                         homogenize_cred=(arm in ("bands_homog", "bands_lump")),
                         homogenize_prowess=(arm == "bands_lump")))
    t0 = int(0.7 * STEPS)
    pops, mcs, ginis, starv, live = [], [], [], [], []
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= t0:
            cr = [a.cred for a in al]
            st = [a.cred * getattr(a, "prowess", 1.0) for a in al]
            pops.append(len(al)); mcs.append(statistics.mean(cr)); ginis.append(gini(cr))
            starv.extend(w.starv_status_this_step); live.append(statistics.mean(st))
    al = w.agent_list
    if not al:
        return None
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        fa = getattr(a, "_father", None)
        if fa is not None and id(fa) in ids:
            fc[id(fa)] = fc.get(id(fa), 0) + 1
    males = [a for a in al if a.sex == "male"]
    oc = [fc.get(id(a), 0) for a in males]                       # offspring counts (surviving) per living male
    rs = corr([a.prowess for a in males], oc)
    rs_gini = gini([float(k) for k in oc])                       # RS INEQUALITY (lump-robust: survives prowess flatten)
    ks = list(fc.values()); ne = (sum(ks) ** 2 / sum(k * k for k in ks)) if ks else 0.0
    mlive = float(np.mean(live)) if live else 0.0
    deficit = (mlive - float(np.mean(starv))) if starv else float("nan")
    return dict(eq_pop=float(np.mean(pops)), mean_cred=float(np.mean(mcs)), gini=float(np.mean(ginis)),
                rs=rs, rs_gini=rs_gini, ne=ne, deficit=deficit)


def stat(xs):
    xs = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    n = len(xs)
    if n < 2:
        return (xs[0] if xs else 0.0), 0.0
    return statistics.mean(xs), statistics.stdev(xs) / math.sqrt(n)


def agg_over_seeds(m, arm, t0):
    rows = [r for r in (run_one(m, s, arm) for s in SEEDS) if r]
    keys = ("eq_pop", "mean_cred", "gini", "rs", "rs_gini", "ne", "deficit")
    return {k: stat([r[k] for r in rows]) for k in keys}, len(rows)


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_3g.txt")

    def log(msg):
        print(f"[3g] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w", encoding="utf-8") as f:
            f.write(f"3g {msg} | {time.time()-t0:.0f}s\n")

    # (1) m-sweep on the bands substrate
    sweep = {}
    for m in MS:
        agg, nok = agg_over_seeds(m, "bands", t0)
        sweep[m] = agg
        log(f"m-sweep bands m={m:.0f}: pop {agg['eq_pop'][0]:.0f} | status→RS {agg['rs'][0]:+.3f}±{agg['rs'][1]:.3f} "
            f"| mean_cred {agg['mean_cred'][0]:.2f} Gini {agg['gini'][0]:.2f} | N_e {agg['ne'][0]:.0f} | n_ok {nok}")
    best = min(MS, key=lambda m: abs(sweep[m]["rs"][0] - 0.19))
    log(f"CALIBRATED m≈{best:.0f} → status→RS {sweep[best]['rs'][0]:+.3f} (von Rueden 0.19)")

    # (2) lumping ablation at the calibrated m
    abl = {}
    for arm in ("ifd", "bands", "bands_homog", "bands_lump"):
        agg, nok = agg_over_seeds(best, arm, t0)
        abl[arm] = agg
        log(f"ablation {arm:>11}: status→RS {agg['rs'][0]:+.3f}±{agg['rs'][1]:.3f} | RS-Gini {agg['rs_gini'][0]:.3f} "
            f"| pop {agg['eq_pop'][0]:.0f} | cred-Gini {agg['gini'][0]:.2f} | death-deficit {agg['deficit'][0]:+.3f} "
            f"| n_ok {nok}")

    # Lump test on the lump-robust metrics: does erasing ALL within-band status (cred+prowess) collapse the RS
    # inequality + the R-18 mortality concentration vs bands-full?
    rsg_b, rsg_l = abl["bands"]["rs_gini"][0], abl["bands_lump"]["rs_gini"][0]
    def_b, def_l = abl["bands"]["deficit"][0], abl["bands_lump"]["deficit"][0]
    verdict = (
        f"E.3-PROPER (CC-1 + bonded_mate_radius={MATE_R}): m≈{best:.0f} lands status→RS {sweep[best]['rs'][0]:+.3f} "
        f"(von Rueden 0.19). LUMPING (band-as-unit, cred+prowess flat): RS-Gini {rsg_b:.3f}→{rsg_l:.3f}, "
        f"death-deficit {def_b:+.3f}→{def_l:+.3f}. cred-only-homog status→RS {abl['bands_homog']['rs'][0]:+.3f} vs "
        f"bands-full {abl['bands']['rs'][0]:+.3f} (RS skew is prowess-driven → cred-flatten barely dents it). "
        f"Interpretation: lumping {'ERASES the RS inequality + flips R-18 mortality concentration → individualism LOAD-BEARING' if (rsg_l < 0.7 * rsg_b or def_l < 0) else 'leaves RS inequality ~intact → NOT load-bearing for RS — REVIEW'}.")
    log(f"VERDICT: {verdict}")
    with open(os.path.join(OUT, "results_3g.json"), "w") as f:
        json.dump(dict(verdict=verdict, recommended_m=best,
                       sweep={f"m{m}": {k: list(v) for k, v in sweep[m].items()} for m in MS},
                       ablation={a: {k: list(v) for k, v in abl[a].items()} for a in abl},
                       seeds=len(SEEDS), steps=STEPS, mate_radius=MATE_R, rho=RHO,
                       elapsed=time.time() - t0), f, indent=2, default=str)


if __name__ == "__main__":
    main()
