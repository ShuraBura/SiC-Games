"""R-84b ANCHOR for `leader_share_frac` — Borgerhoff Mulder et al. 2009 (Science 326:682) Table 2.

No source gives a chiefly-due PERCENTAGE (checked Sahlins 1972 and Ames 1994 directly), so the levy rate is
anchored on its OUTCOME, as `leveling_strength` was on Boehm 38/48 and status→RS on von Rueden r=0.19.

BHM's three wealth classes ARE the model's three status facets, and Table 1 confirms it by what they measured:
  EMBODIED  = Hadza grip strength / body weight / foraging returns, Ache hunting returns  -> `prowess`
  RELATIONAL= Ju/'hoansi exchange partners, Lamalera food-share partners                  -> `cred`
  MATERIAL  = Lamalera quality of housing, boat shares                                    -> `material`
Table 2 gives the IMPORTANCE weights alpha and the alpha-weighted Gini per economic system:
                  a_emb  a_rel  a_mat   Gini
  hunter-gatherer  0.46   0.39   0.15   0.25
  horticultural    0.53   0.26   0.21   0.27
  pastoral         0.26   0.14   0.61   0.42
  agricultural     0.27   0.14   0.59   0.48
So the target is the alpha-WEIGHTED composite, not the material Gini alone -- and for foragers material carries
only 15% of the weight, which is the check on making material the whole stratification story.
"""
import sys, os, statistics
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

ALPHA = {"hunter-gatherer": (0.46, 0.39, 0.15, 0.25), "horticultural": (0.53, 0.26, 0.21, 0.27),
         "pastoral": (0.26, 0.14, 0.61, 0.42), "agricultural": (0.27, 0.14, 0.59, 0.48)}


def gini(xs):
    xs = sorted(v for v in xs if v == v)
    n = len(xs)
    if n == 0 or sum(xs) <= 0:
        return 0.0
    cum = sum((i + 1) * v for i, v in enumerate(xs))
    return (2.0 * cum) / (n * sum(xs)) - (n + 1.0) / n


def run(lf, lev, office=True, gain=0.05, seed=0, steps=600, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_capture_frac=0.0,
        material_decay=0.002, aggrandizer_frac=0.15,
        enable_leader_share=(lf > 0), leader_share_frac=lf,
        enable_leveling=lev, leveling_strength=(0.79 if lev else 0.0), leveling_share=(0.8 if lev else 0.0),
        enable_leader_office=office, office_grievance_gain=gain))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)], demography_cfg=d)
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            return None
    al = [a for a in w.agent_list if a.age >= 15 * 12]
    if not al:
        return None
    g_e = gini([getattr(a, "prowess", 1.0) for a in al])
    g_r = gini([a.cred for a in al])
    g_m = gini([a.material for a in al])
    return g_e, g_r, g_m, len(w.agent_list)


if __name__ == "__main__":
    print(__doc__.split("\n\n")[0])
    print("\nMODEL FACET GINIs and the BHM alpha-weighted COMPOSITE (2 seeds x 600 steps).")
    print(f"{'share':>6} {'lev':>6} {'G_prow':>7} {'G_cred':>7} {'G_matl':>7} | "
          + " ".join(f"{k[:9]:>10}" for k in ALPHA) + "   pop")
    print("-" * 92)
    for lf, lev in ((0.0, True), (0.1, True), (0.2, True), (0.35, True), (0.5, True),
                    (0.2, False), (0.5, False)):
        rs = [r for r in (run(lf, lev, seed=s) for s in (0, 1)) if r]
        if not rs:
            continue
        ge, gr, gm = (statistics.mean(r[i] for r in rs) for i in range(3))
        pop = statistics.mean(r[3] for r in rs)
        comp = {k: a_e * ge + a_r * gr + a_m * gm for k, (a_e, a_r, a_m, _) in ALPHA.items()}
        print(f"{lf:6.2f} {str(lev):>6} {ge:7.3f} {gr:7.3f} {gm:7.3f} | "
              + " ".join(f"{comp[k]:10.3f}" for k in ALPHA) + f" {pop:6.0f}")
    print("\nBHM TARGET   (alpha-weighted Gini)      " + " ".join(f"{ALPHA[k][3]:10.2f}" for k in ALPHA))
    print("A forager arm should land near 0.25 under its OWN weights (col 1); the agricultural column shows")
    print("what the SAME facet spread would read as if material carried 59% of the weight instead of 15%.")
