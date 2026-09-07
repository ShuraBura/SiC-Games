"""R-90 CALIBRATION — pick `lineage_branch_rate` in the regime that actually COLLAPSES.

FIRST CUT WAS INVALID (D1/D4), recorded here so it is not repeated. Sweeping on the plain substrate
(no elite stack, 1200 steps) gave 7.34 lineages/band and dom-share 0.355 AT RATE 0.0 — i.e. the FILED Hill
2011 target (~7 / 0.38) was already met with the mechanism off. No positive control, and the swept parameter
was not rate-limiting, so the sweep could only ever have said "change nothing."

The collapse (R-89: 3000 patrilines → 5, frozen) happened with the ELITE STACK ON, where measured
`male_rs_gini` ≈ 0.70. Extreme male reproductive skew is precisely what crushes male effective population
size and fixates patrilines — so that is the regime to calibrate in.

WHAT THIS SWEEP MUST SHOW, in order:
  1. POSITIVE CONTROL (rate 0.0): the collapse reproduces — lineages fall far below the Hill target and
     `ascribed_frac` saturates, freezing reversions. If it does not, the probe is not diagnostic and no
     verdict about the fix may be read off it.
  2. Only then, the rate that restores ~7 lineages/band + dom-share ~0.38 WITHOUT capping top_share.

NOTE ON INTERPRETATION, so the direction is not mistaken for a failure: male-lineage collapse under an
inequality layer is what Karmin 2015 REPORTS (female Ne up to 17x male Ne, 8-4 kya, tracking the spread of
farming). The model reproducing a Y-bottleneck is correct. What is wrong is that it cannot RECOVER from one:
with no branching, `_lineage` is absorbing, so the bottleneck is permanent instead of a dip.
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

N = 500
STEPS = int(os.environ.get("CAL_STEPS", "3000"))
RATES = [float(x) for x in os.environ.get("CAL_RATES", "0.0,0.01,0.03,0.08").split(",")]
TARGET_LPB, TARGET_DOM = 7.0, 0.38

# the R-82...R-87 elite stack, at run_campaign.py's ELITE_KW values — the regime that collapses
ELITE_KW = dict(
    enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002, aggrandizer_frac=0.15,
    enable_leader_share=True, leader_share_frac=0.20,
    enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
    enable_leader_office=True, office_grievance_gain=0.05,
    enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0, legit_threshold=0.15, legit_decay=0.02,
    enable_delegitimation=True, resent_alpha=0.001, resent_threshold=0.5, resent_privilege_ref=10.0,
)

k = world_lottery_climate(0, terrain="coastal", climate="temperate")
f = generate_world(k, mode="climate")
_hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and _hf0.level(x, y) > 0]


def run(rate, seed=0):
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    d = DemographyConfig(
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_paternity=True, mate_choice_strength=5.0, enable_prowess_facet=True,
        enable_pair_bonds=True, enable_band_affiliation=True,
        band_cohesion=0.3, band_split_size=45, band_merge_size=10,
        enable_game=True, game_meat_frac=0.55,
        enable_lineage_branching=(rate > 0.0), lineage_branch_rate=rate,
        **ELITE_KW)
    w = TerrainWorld(n_agents=N, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(N)],
                     demography_cfg=d)
    revs = 0
    revs_late = 0                      # reversions in the LAST THIRD — the trap test (are they still firing?)
    cut = int(STEPS * 2 / 3)
    for s in range(1, STEPS + 1):
        w.step()
        if not w.agent_list:
            return None
        revs += w.reversions_this_step
        if s > cut:
            revs_late += w.reversions_this_step
    dy = w.dynasties()
    lg = w.legitimacy()
    return dict(rate=rate, pop=len(w.agent_list),
                lineages_per_band=dy["lineages_per_band"], dom_lineage_share=dy["dom_lineage_share"],
                n_lineages=dy["n_lineages"], top_share=dy["top_share"], eff_lineages=dy["eff_lineages"],
                ascribed_frac=round(lg["ascribed_frac_pop"], 3), revs=revs, revs_late=revs_late)


print(f"R-90 calibration (ELITE STACK ON) | N={N} steps={STEPS} | TARGET lin/band~{TARGET_LPB} dom~{TARGET_DOM}")
print(f"{'rate':>6} {'lin/band':>9} {'dom':>7} {'n_lin':>6} {'top':>6} {'eff':>6} {'asc':>6} "
      f"{'revs':>6} {'revs_late':>10} {'pop':>6}")
rows = []
for r in RATES:
    t0 = time.time()
    d = run(r)
    if d is None:
        print(f"{r:>6.3f}   EXTINCT")
        continue
    rows.append(d)
    print(f"{r:>6.3f} {d['lineages_per_band']:>9.2f} {d['dom_lineage_share']:>7.3f} {d['n_lineages']:>6d} "
          f"{d['top_share']:>6.3f} {d['eff_lineages']:>6.1f} {d['ascribed_frac']:>6.3f} "
          f"{d['revs']:>6d} {d['revs_late']:>10d} {d['pop']:>6d}   ({time.time()-t0:.0f}s)", flush=True)

out = os.path.join(os.path.dirname(__file__), "calib_lineage_branch.json")
with open(out, "w") as fh:
    json.dump(rows, fh, indent=1)
print("wrote", out)
if rows and rows[0]["rate"] == 0.0:
    pc = rows[0]
    print(f"\nPOSITIVE CONTROL (rate 0.0): lin/band={pc['lineages_per_band']} (target {TARGET_LPB}), "
          f"asc={pc['ascribed_frac']}, revs_late={pc['revs_late']}")
    print("  -> collapse+trap reproduced" if (pc["lineages_per_band"] < 4.0 or pc["revs_late"] == 0)
          else "  -> NOT reproduced: this probe is not diagnostic; do not read a verdict off it")
