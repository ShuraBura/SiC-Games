"""Demographic dashboard (R-75) — print every marker for a world, broken down by village.

Usage:  py -3 sic_games/outputs/phase1_biome_mortality/report_demography.py [steps] [seed]

WHY. R-74 burned a session chasing a "3.4× orphan excess" that was R-16's fertility-pinning working
correctly; four hypotheses died before the answer arrived. All of it sits in one table here. Run this
before believing any demographic claim, and after any change that could move the substrate.

Benchmarks printed alongside each marker — see the test (`tests/test_demography_diagnostics.py`) for the
standing assertions and MODEL_SPEC/LITERATURE for the anchors.
"""
import os
import statistics
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "phase1_social_evolution")))

from run_se0_controlled_climate import emergent_village_demog          # noqa: E402

from sic_games.capacity import NPPCapacityField                        # noqa: E402
from sic_games.climate import ClimateField                             # noqa: E402
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig   # noqa: E402
from sic_games.demography import ACHE_FOREST_NATURAL as NAT            # noqa: E402
from sic_games.phase1_model import TerrainWorld                        # noqa: E402
from sic_games.terrain import generate_world, world_lottery_climate    # noqa: E402

BURN = 75000.0

# marker -> (label, benchmark text). The benchmark is the ANCHOR, not the model's current value.
BENCH = [
    ("n",                     "population",            ""),
    ("sex_ratio_m_f",         "sex ratio M:F",         "~1.05 at birth (SRB 0.512, MODEL_SPEC §366)"),
    ("median_age_yr",         "median age (yr)",       "stationary forager ~20; a GROWING pop is younger"),
    ("mean_age_yr",           "mean age (yr)",         ""),
    ("frac_child",            "frac <15",              "stationary forager ~0.35-0.42"),
    ("frac_adult",            "frac 15-59",            ""),
    ("frac_elder",            "frac >=60",             ""),
    ("dependency_ratio",      "dependency ratio",      "(child+elder)/adult; forager ~0.8"),
    ("frac_paired_adult_f",   "frac adult ♀ paired",   ""),
    ("mean_wives_married_m",  "mean wives | married ♂", "preset polygyny_rate 0.3 / max_wives 3"),
    ("frac_polygynous_m",     "frac polygynous ♂",     "forager LOW — Hadza ~4% (Marlowe); Aché monogamy-dominant"),
    ("n_risk_0_9",            "n children 0-9",        ""),
    ("frac_motherless",       "frac motherless",       "Aché 0.02 EXPOSURE (Tab 13.1); model MUST exceed (R-16 pinning)"),
    ("frac_fatherless",       "frac fatherless",       "Aché 0.05 (Tab 13.1)"),
    ("frac_parents_divorced", "frac parents divorced", "Aché 0.14 (Tab 13.1, both parents living)"),
]


def build(seed=0, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, BURN, patch=(20, 20, 60), mode="tallavaara",
                                       aquatic=True, enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, BURN, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    pos = [land[i % len(land)] for i in range(n)]
    d = emergent_village_demog().model_copy(update=dict(
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_paternity=True, divorce_rate=0.004,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True, enable_catchment_ceiling=True,
        enable_settlement_scalar_stress=True, enable_landscape_packing=True, enable_sedentism_fertility=True))
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=pos, demography_cfg=d)


def main():
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    w = build(seed=seed)
    births = starv = senesc = orph = 0
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            print("EXTINCT"); return
        births += w.births_this_step
        starv += w.deaths_starv_this_step
        senesc += w.deaths_senesc_this_step
        orph += getattr(w, "deaths_orphan_this_step", 0)

    whole = w.demography()
    print(f"\n=== WHOLE POPULATION (seed {seed}, {steps} steps = {steps/12:.0f} yr) ===")
    for key, label, bench in BENCH:
        v = whole.get(key)
        s = f"{v:.3f}" if isinstance(v, float) else str(v)
        print(f"  {label:24} {s:>9}   {bench}")

    tot = starv + senesc
    print(f"\n=== FLOWS (cumulative) ===")
    print(f"  births {births}  deaths {tot}  (starvation {starv} = {100*starv/tot if tot else 0:.1f}%, "
          f"Siler {senesc} = {100*senesc/tot if tot else 0:.1f}%, orphan-flagged {orph})")
    print(f"  NB ~half of deaths being starvation is R-16's fertility-pinning at K, not a defect:")
    print(f"     at r=0 the life table is set by FERTILITY (e0 ~28), not the natural-mortality coefficients.")

    vil = w.demography(by="village")
    hinter = vil.get(None, {}).get("n", 0)
    big = {k: m for k, m in vil.items() if k is not None and m["n"] >= 50}
    print(f"\n=== VILLAGES ({len([k for k in vil if k is not None])} settlements, "
          f"{len(big)} large; hinterland {hinter}) ===")
    hdr = f"{'site':>12} {'n':>5} {'sexR':>6} {'medAge':>7} {'child':>6} {'depR':>6} {'pairF':>6} {'mless':>6} {'fless':>6}"
    print(hdr); print("-" * len(hdr))
    for site, m in sorted(big.items(), key=lambda t: -t[1]["n"]):
        print(f"{str(site):>12} {m['n']:5d} {m['sex_ratio_m_f']:6.2f} {m['median_age_yr']:7.1f} "
              f"{m['frac_child']:6.2f} {m['dependency_ratio']:6.2f} {m['frac_paired_adult_f']:6.2f} "
              f"{m['frac_motherless']:6.3f} {m['frac_fatherless']:6.3f}")
    if big:
        print("\n  spread across large villages (a sane MEAN can hide a village at 37% motherless):")
        for key, label, _ in BENCH:
            vals = [m[key] for m in big.values() if isinstance(m.get(key), float) and m[key] == m[key]]
            if vals and len(vals) > 1:
                print(f"    {label:24} min {min(vals):7.3f}  med {statistics.median(vals):7.3f}  max {max(vals):7.3f}")


if __name__ == "__main__":
    main()
