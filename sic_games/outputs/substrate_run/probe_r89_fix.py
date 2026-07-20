"""R-89 fix validation: small-N (fast), REALISTIC ELITE_KW parameters (not the test file's hair-trigger
ones), per-step instrumentation of resentment/ascription/reversions, dumped to JSON for plotting."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

N = 500
STEPS = 5500
k = world_lottery_climate(0, terrain="coastal", climate="temperate")
f = generate_world(k, mode="climate")
hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
d = DemographyConfig(
    enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
    enable_paternity=True, mate_choice_strength=5.0, enable_prowess_facet=True,
    enable_pair_bonds=True, enable_band_affiliation=True,
    band_cohesion=0.3, band_split_size=45, band_merge_size=10,
    enable_game=True, game_meat_frac=0.55,
    enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002, aggrandizer_frac=0.15,
    enable_leader_share=True, leader_share_frac=0.20,
    enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
    enable_leader_office=True, office_grievance_gain=0.05,
    enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0, legit_threshold=0.15, legit_decay=0.02,
    enable_delegitimation=True, resent_alpha=0.001, resent_threshold=0.5, resent_privilege_ref=10.0,
)
w = TerrainWorld(n_agents=N, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                  carbon_cfg=CarbonConfig(kappa=1.5),
                  substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                 contest_exponent=1.5, move_cost_flat=0.0),
                  harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(N)],
                  demography_cfg=d)

rows = []
cum_reversions = 0
for step in range(1, STEPS + 1):
    w.step()
    if not w.agent_list:
        print("population collapsed at step", step)
        break
    g = w.legitimacy()
    cum_reversions += w.reversions_this_step
    rs = list(w._band_resentment.values())
    rows.append(dict(step=step, asc=g["ascribed_frac_pop"], n_ascribed=g["n_ascribed"],
                      n_lineages=g["n_lineages"], reversions_this_step=w.reversions_this_step,
                      cum_reversions=cum_reversions,
                      max_resent=max(rs) if rs else 0.0, mean_resent=(sum(rs) / len(rs)) if rs else 0.0))
    if step % 200 == 0 or w.reversions_this_step > 0:
        r = rows[-1]
        print(f"[{step}] asc={r['asc']:.3f} n_ascribed={r['n_ascribed']} reversions={r['reversions_this_step']} "
              f"cum={cum_reversions} max_resent={r['max_resent']:.3f} mean_resent={r['mean_resent']:.3f}")

out_path = os.path.join(os.path.dirname(__file__), "probe_r89_fix_trajectory.json")
with open(out_path, "w") as fh:
    json.dump(rows, fh)
print("wrote", out_path, "rows=", len(rows), "total reversions=", cum_reversions)
