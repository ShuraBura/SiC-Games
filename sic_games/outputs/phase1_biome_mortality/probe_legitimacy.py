"""R-86 — does the LEGITIMACY channel produce HEREDITARY rank where material accumulation could not?

Flannery ch.10 says our elite layer's premise is insufficient on its own: feasting "produced individual Big Men
who had no way of bequeathing renown to their offspring", which is exactly what R-83/R-84 measured. Friedman's
endogenous mechanism converts achieved standing into ASCRIBED rank via a legitimating belief.

Two pre-registered targets this must move, neither of which it is fitted to:
  T-6  father-was-leader -> Hayden 1995's "about 75% of New Guinea Entrepreneur Big Men had fathers that were
       also Big Men".  Baseline without legitimacy: 53-69%.
  T-5  the BHM alpha-weighted composite Gini -> 0.48 under AGRICULTURAL weights (0.27/0.14/0.59).
       Baseline best: 0.435, and flat in the levy (R-84b).
"""
import os
import statistics
import sys

sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog

from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

ALPHA = {"forager": (0.46, 0.39, 0.15, 0.25), "agricultural": (0.27, 0.14, 0.59, 0.48)}


def gini(xs):
    xs = sorted(v for v in xs if v == v)
    n = len(xs)
    if n == 0 or sum(xs) <= 0:
        return 0.0
    return (2.0 * sum((i + 1) * v for i, v in enumerate(xs))) / (n * sum(xs)) - (n + 1.0) / n


def run(feast=0.0, cred_gain=0.0, thr=0.5, seed=0, steps=600, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_capture_frac=0.0,
        material_decay=0.002, aggrandizer_frac=0.15,
        enable_leader_share=True, leader_share_frac=0.20,
        enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
        enable_leader_office=True, office_grievance_gain=0.05,
        enable_legitimacy=(feast > 0.0), legit_feast_frac=feast,
        legit_cred_gain=cred_gain, legit_threshold=thr, legit_decay=0.02))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                     demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            return None
    al = [a for a in w.agent_list if a.age >= 15 * 12]
    if not al:
        return None
    ge = gini([getattr(a, "prowess", 1.0) for a in al])
    gr = gini([a.cred for a in al])
    gm = gini([a.material for a in al])
    lg = w.legitimacy()
    t = w.leader_tenure()
    return dict(ge=ge, gr=gr, gm=gm, pop=len(w.agent_list), fwl=t["father_was_leader"],
                n_legit=lg["n_ascribed"], n_lin=lg["n_lineages"], lmax=lg["max"],
                lfrac=lg["ascribed_frac_pop"], tenure=t["mean_years"])


if __name__ == "__main__":
    print(__doc__.strip().split("\n")[0])
    print(f"\n{'feast':>6} {'credg':>6} {'thr':>5} {'n_ascr':>8} {'/lin':>5} {'L_max':>6} {'popfrac':>8} "
          f"{'G_prow':>7} {'G_cred':>7} {'G_matl':>7} {'forager':>8} {'agri':>7} {'fath=ldr':>9} {'pop':>6}")
    print("-" * 110)
    for feast, cg, thr in ((0.0, 0.0, 0.50), (0.25, 2.0, 0.15), (0.25, 5.0, 0.15), (0.25, 10.0, 0.15),
                           (0.25, 20.0, 0.15), (0.10, 10.0, 0.15), (0.10, 10.0, 0.10)):
        rs = [r for r in (run(feast, cg, thr, seed=s) for s in (0, 1)) if r]
        if not rs:
            print(f"{feast:6.2f} {cg:6.2f} {thr:5.2f}   *** EXTINCT ***")
            continue
        a = lambda k: statistics.mean(r[k] for r in rs)
        comp = {kk: v[0] * a("ge") + v[1] * a("gr") + v[2] * a("gm") for kk, v in ALPHA.items()}
        print(f"{feast:6.2f} {cg:6.2f} {thr:5.2f} {a('n_legit'):8.1f} {a('n_lin'):5.0f} {a('lmax'):6.3f} "
              f"{a('lfrac'):8.3f} {a('ge'):7.3f} {a('gr'):7.3f} {a('gm'):7.3f} {comp['forager']:8.3f} "
              f"{comp['agricultural']:7.3f} {a('fwl') * 100:8.0f}% {a('pop'):6.0f}")
    print(f"\n{'TARGETS':>13}: forager composite 0.25 | agricultural 0.48 | father-was-leader 75% (Hayden)")
    print(f"{'BASELINE':>13}: agricultural best 0.435 (leveling off) | father-was-leader 53-69%")
