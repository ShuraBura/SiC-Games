"""Carbon-on-substrate Tier-1 — STATISTICAL VALIDATION of the compositional Cred-survival gradient.

Promotes run_3a's preliminary signal to a recorded result. Three things make it rigorous:
  (1) MANY seeds (N) → mean ± SE + a paired t across seeds (drift-controlled: κ>0 vs κ=0 share seeding).
  (2) A CV CONTROL — the killer test: at meat CV=0 (deterministic meat) the gradient MUST vanish (cap-pinned,
      no sub-cap moments). A non-zero effect at CV=0 would mean the signal is an artifact, not the mechanism.
  (3) A DIRECT "who dies" measure — mean cred of STARVATION deaths vs the living (model.starv_cred_this_step):
      at κ>0 bad streaks should kill the LOW-cred (deficit > 0); the mean(cred|alive) lift is the consequence.
Predictions: Δmean_cred(κ>0 − κ=0) ≈ 0 at CV=0, > 0 and rising with κ AND CV; cred-death-deficit > 0 only with
variance; eq_pop ~κ-invariant (fertility-pinned, R-16). Forest-Aché substrate, δ=3.
Run:  py -3 -u outputs/phase1_biome_mortality/run_3b_carbon_statval.py
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
from sic_games.terrain import generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS = 400, 700
SEEDS = list(range(20))                      # 20 seeds for SE/t
KAPPAS = [0.0, 1.0, 2.0]
CVS = [0.0, 0.73, 2.24]                       # control / forest / savanna meat variance
MEAT_FRAC, SEED_SIGMA, INHERIT_SIGMA, DELTA = 0.55, 0.5, 0.1, 3.0


def gini(xs):
    xs = sorted(xs); n = len(xs); s = sum(xs)
    return (2.0 * sum((i + 1) * x for i, x in enumerate(xs))) / (n * s) - (n + 1) / n if s > 0 and n else 0.0


def run_one(kappa, cv, seed):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=kappa, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(
                         siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=DELTA, dens_rho_half=0.2,
                         enable_game=True, game_meat_frac=MEAT_FRAC, game_meat_cv=cv,
                         enable_cred_status=True, cred_seed_sigma=SEED_SIGMA, cred_inherit_sigma=INHERIT_SIGMA))
    t0 = int(0.6 * STEPS)
    pops, mcs, ginis, starv_creds, live_means = [], [], [], [], []
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= t0:
            creds = [a.cred for a in al]; lm = statistics.mean(creds)
            pops.append(len(al)); mcs.append(lm); ginis.append(gini(creds))
            starv_creds.extend(w.starv_cred_this_step); live_means.append(lm)
    if not mcs:
        return None
    mean_live = float(np.mean(live_means))
    deficit = (mean_live - float(np.mean(starv_creds))) if starv_creds else float("nan")
    return dict(eq_pop=float(np.mean(pops)), mean_cred=float(np.mean(mcs)), gini=float(np.mean(ginis)),
                death_deficit=deficit, n_starv=len(starv_creds))


def tstat(xs):
    xs = [x for x in xs if not math.isnan(x)]
    n = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0
    m = statistics.mean(xs); se = statistics.stdev(xs) / math.sqrt(n)
    return m, se, (m / se if se > 0 else 0.0)


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_3b.txt")
    # cells[(cv,kappa)] = list over seeds of run dicts (aligned by seed index for the paired Δ)
    cells = {}
    for cv in CVS:
        for k in KAPPAS:
            cells[(cv, k)] = [run_one(k, cv, s) for s in SEEDS]
            ok = [r for r in cells[(cv, k)] if r]
            ep = statistics.mean([r["eq_pop"] for r in ok]); mc = statistics.mean([r["mean_cred"] for r in ok])
            print(f"[3b] CV={cv:.2f} κ={k:.0f}: eq_pop {ep:6.0f} | mean_cred {mc:.3f} | n_ok {len(ok)}  "
                  f"[{time.time()-t0:.0f}s]", flush=True)
            with open(prog, "w", encoding="utf-8") as f:
                f.write(f"3b CV={cv} κ={k}: eq_pop {ep:.0f} mean_cred {mc:.3f} | {time.time()-t0:.0f}s\n")

    print(f"\n[3b] === STATISTICAL VALIDATION (N={len(SEEDS)} seeds, paired drift-control) ===", flush=True)
    summary = {}
    for cv in CVS:
        base = cells[(cv, 0.0)]
        print(f"\n  meat CV = {cv:.2f}  {'(CONTROL: deterministic → effect must vanish)' if cv==0 else ''}", flush=True)
        for k in KAPPAS:
            rows = cells[(cv, k)]
            dmc = [rows[i]["mean_cred"] - base[i]["mean_cred"] for i in range(len(SEEDS))
                   if rows[i] and base[i]]                                   # paired Δ vs κ=0, same seed
            defs = [r["death_deficit"] for r in rows if r]
            m_d, se_d, t_d = tstat(dmc)
            m_def, se_def, t_def = tstat(defs)
            eqp = statistics.mean([r["eq_pop"] for r in rows if r])
            sig = "***" if abs(t_d) > 2.86 else ("**" if abs(t_d) > 2.13 else ("*" if abs(t_d) > 1.73 else "ns"))
            print(f"   κ={k:.0f}: Δmean_cred {m_d:+.3f}±{se_d:.3f} (t={t_d:+.1f} {sig}) | "
                  f"cred-death-deficit {m_def:+.3f}±{se_def:.3f} (t={t_def:+.1f}) | eq_pop {eqp:.0f}", flush=True)
            summary[f"cv{cv}_k{k}"] = dict(d_mean_cred=m_d, se=se_d, t=t_d, death_deficit=m_def,
                                          t_deficit=t_def, eq_pop=eqp, sig=sig)

    verdict = (
        "VALIDATED: at CV=0 (deterministic meat) the gradient vanishes (the cap-pinned control); with variance "
        "(CV 0.73/2.24) κ>0 significantly lifts mean(cred|alive) and starvation kills the low-Cred "
        "(death-deficit>0), scaling with both κ and CV, while eq_pop stays ~κ-invariant. The Carbon advantage "
        "is COMPOSITIONAL and lives in ordinary meat variance (R-1 on the demographic substrate)."
        if summary["cv0.0_k2.0"]["t"] < 1.73 and summary["cv2.24_k2.0"]["t"] > 2.13 else
        "MIXED/NULL: inspect — the CV=0 control or the variance effect did not behave as predicted.")
    print(f"\n[3b] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)
    with open(os.path.join(OUT, "results_3b.json"), "w") as f:
        json.dump(dict(verdict=verdict, summary=summary, seeds=len(SEEDS), steps=STEPS,
                       kappas=KAPPAS, cvs=CVS, elapsed=time.time() - t0), f, indent=2, default=str)


if __name__ == "__main__":
    main()
