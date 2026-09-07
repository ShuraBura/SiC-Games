"""R-86v — VALIDATE the father-was-leader = 76% claim (TARGETS T-6, Hayden's 75%).

This is the day's one positive result and it has never been held to the standard the other results now are:
it is a SINGLE SUMMARY STATISTIC over a possibly-skewed population, which is exactly the shape that failed in
R-87d (mean dwell 2.7 yr described almost none of the actual spells).

THE NULL NOBODY COMPUTED (charter D2). `father_was_leader` = P(father ever led | self ever led). If a LARGE
share of the population ever leads, then leaders having leader fathers is arithmetic, not heredity. The correct
baseline is the unconditional base rate B = P(father ever led), over all live agents with a father. Under
independence the two are EQUAL, so the quantity with meaning is the LIFT = measured / B, not the raw fraction.
A permutation test (shuffle who-ever-led, preserving the count) gives the same null with a spread.

D14 — computed two ways: the analytic base-rate ratio, and a permutation null. They must agree.
D1 — positive control: a synthetic population with KNOWN father-son transmission must return the lift it was
built with, or the statistic cannot measure heredity at all.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog

from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def run(legit=True, feast=0.25, cg=20.0, thr=0.15, seed=0, steps=600, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002, aggrandizer_frac=0.15,
        enable_leader_share=True, leader_share_frac=0.20,
        enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
        enable_leader_office=True, office_grievance_gain=0.05,
        enable_legitimacy=legit, legit_feast_frac=(feast if legit else 0.0),
        legit_cred_gain=cg, legit_threshold=thr, legit_decay=0.02))
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
    return w


def analyse(w, trials=400, rng=None):
    """Measured statistic, its base-rate null, a permutation null, and the lift."""
    rng = rng or np.random.default_rng(0)
    ever = w._ever_leader
    pop = [a for a in w.agent_list if getattr(a, "_father", None) is not None]
    if not pop:
        return None
    self_led = np.array([a.unique_id in ever for a in pop])
    dad_led = np.array([a._father.unique_id in ever for a in pop])
    if self_led.sum() == 0:
        return None
    measured = float(dad_led[self_led].mean())          # P(father led | self led)  <- the reported number
    base = float(dad_led.mean())                        # P(father led)             <- the null under independence
    # permutation null: shuffle WHO ever led, preserving the count
    perm = []
    k = int(self_led.sum())
    idx = np.arange(len(pop))
    for _ in range(trials):
        pick = rng.choice(idx, size=k, replace=False)
        perm.append(float(dad_led[pick].mean()))
    perm = np.asarray(perm)
    # odds ratio, the second estimator (D14)
    a = int((self_led & dad_led).sum()); b = int((self_led & ~dad_led).sum())
    c = int((~self_led & dad_led).sum()); dd = int((~self_led & ~dad_led).sum())
    orr = (a * dd) / (b * c) if b * c > 0 else float("inf")
    return {"measured": measured, "base_rate": base, "lift": measured / base if base > 0 else float("nan"),
            "perm_mean": float(perm.mean()), "perm_p95": float(np.quantile(perm, 0.95)),
            "perm_max": float(perm.max()), "n_scored": k, "n_pop": len(pop),
            "frac_ever_led": float(self_led.mean()), "odds_ratio": orr,
            "z": float((measured - perm.mean()) / perm.std()) if perm.std() > 0 else float("nan")}


def positive_control(lift_target=2.0, n=800, base=0.35, trials=1, seed=0):
    """D1 — a synthetic population with KNOWN father-son transmission. If the statistic cannot recover a lift
    it was built with, it cannot measure heredity."""
    rng = np.random.default_rng(seed)
    dad_led = rng.random(n) < base
    p_self = np.where(dad_led, min(0.95, base * lift_target), base * (1 - base * (lift_target - 1) / (1 - base)))
    self_led = rng.random(n) < p_self
    measured = float(dad_led[self_led].mean()); b = float(dad_led.mean())
    return measured / b if b > 0 else float("nan")


if __name__ == "__main__":
    print(__doc__.strip().split("\n")[0])
    print("\n=== D1 POSITIVE CONTROL — can the lift statistic recover a KNOWN transmission? ===")
    for tgt in (1.0, 1.5, 2.0, 2.5):
        got = np.mean([positive_control(tgt, seed=s) for s in range(20)])
        print(f"    built-in lift {tgt:.1f}  ->  recovered {got:.2f}   {'ok' if abs(got-tgt) < 0.25 else '*** MISMATCH'}")

    print("\n=== THE REAL MEASUREMENT (2 seeds x 600 steps) ===")
    hdr = f"{'arm':>14} {'measured':>9} {'base rate':>10} {'LIFT':>6} {'perm null':>10} {'p95':>7} {'z':>7} {'odds':>7} {'%ever led':>10} {'n':>5}"
    print(hdr); print("-" * len(hdr))
    for lab, legit in (("legitimacy ON", True), ("baseline OFF", False)):
        rows = []
        for s in (0, 1):
            w = run(legit=legit, seed=s)
            if w is None:
                continue
            r = analyse(w, rng=np.random.default_rng(100 + s))
            if r:
                rows.append(r)
        if not rows:
            print(f"{lab:>14}   *** no data ***"); continue
        m = lambda k: float(np.mean([r[k] for r in rows]))
        print(f"{lab:>14} {m('measured'):9.3f} {m('base_rate'):10.3f} {m('lift'):6.2f} "
              f"{m('perm_mean'):10.3f} {m('perm_p95'):7.3f} {m('z'):7.2f} {m('odds_ratio'):7.2f} "
              f"{m('frac_ever_led'):10.3f} {m('n_scored'):5.0f}")
    print("\nHayden's anchor is 75% as a RAW FRACTION. If the base rate is already ~70%, a measured 76% is")
    print("a lift of ~1.09 and carries almost no information about heredity.")
