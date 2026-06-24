"""B+ step 5 — paternal_provision_frac calibration to Marlowe 2003 (male share of <3-yr provisioning ≈ 58%).

LIFE-HISTORY run (lh_cfg → graded η + body-scaled reserves → a real dependent class; forage_age_min=36 so the
dependency window = the Marlowe <3-yr critical period). Full B+ (m=4, the R-19 calibrated value) + maternal
provisioning. Sweep `paternal_provision_frac`; measure the emergent **male share of provisioning to <3-yr
children** = Σ_paternal / (Σ_maternal + Σ_paternal), and pick the frac nearest Marlowe's 58% (baseline ~43%).
Run:  py -3 -u outputs/phase1_biome_mortality/run_3d_paternal_calib.py
"""
from __future__ import annotations
import json, math, os, time, statistics
import numpy as np
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig, LifeHistoryConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

OUT = os.path.dirname(os.path.abspath(__file__))
FOUNDERS, STEPS, SEEDS = 400, 900, [11, 23, 42]
FRACS = [0.0, 0.3, 0.5, 0.7, 0.9]


def run_one(frac, seed):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     lh_cfg=LifeHistoryConfig(forage_age_min=36),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(
                         siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
                         enable_game=True, game_meat_frac=0.55, game_meat_cv=0.73,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_prowess_facet=True, prowess_decay=0.1, sex_division=1.0,
                         enable_paternity=True, mate_choice_strength=4.0, patriline_weight=0.5,
                         lineage_reversion=0.1, enable_provisioning=True, paternal_provision_frac=frac))
    mat = pat = 0.0
    t0 = int(0.4 * STEPS)
    for step in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if step >= t0:
            mat += w.prov_young_maternal; pat += w.prov_young_paternal
    share = pat / (mat + pat) if (mat + pat) > 0 else float("nan")
    return share


def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_3d.txt")
    res = {}
    for fr in FRACS:
        shares = [s for s in (run_one(fr, sd) for sd in SEEDS) if not math.isnan(s)]
        m = statistics.mean(shares) if shares else float("nan")
        se = (statistics.stdev(shares) / math.sqrt(len(shares))) if len(shares) > 1 else 0.0
        res[fr] = (m, se)
        msg = f"paternal_provision_frac={fr:.1f}: male share of <3yr provisioning {m*100:.0f}%±{se*100:.0f}"
        print(f"[3d] {msg}  [{time.time()-t0:.0f}s]", flush=True)
        with open(prog, "w", encoding="utf-8") as f:
            f.write(f"3d {msg} | {time.time()-t0:.0f}s\n")
    valid = {fr: v[0] for fr, v in res.items() if not math.isnan(v[0])}
    best = min(valid, key=lambda fr: abs(valid[fr] - 0.58)) if valid else None
    verdict = (f"paternal_provision_frac ≈ {best:.1f} → male share {valid[best]*100:.0f}% (Marlowe target 58%; "
               f"baseline ~43%). This is the calibrated value." if best is not None else "no valid runs")
    print(f"\n[3d] VERDICT: {verdict}  [{time.time()-t0:.0f}s]", flush=True)
    with open(os.path.join(OUT, "results_3d.json"), "w") as f:
        json.dump(dict(verdict=verdict, recommended_frac=best,
                       by_frac={str(fr): list(v) for fr, v in res.items()},
                       seeds=len(SEEDS), steps=STEPS), f, indent=2, default=str)


if __name__ == "__main__":
    main()
