"""Resource-dependent storability (Testart). storable_fraction becomes a per-cell weighted average of the local
resource mix (grain 0.85 / fish 0.80 / forage 0.15 / game 0.35) instead of a flat 0.5. Hypothesis: granaries +
villages concentrate MORE on high-storability (grain/fish) cells — the storable-resource sites sustain sedentism
through the lean season, fresh-forage sites can't. Measure occupancy-weighted storability + total granary stock +
packing, OFF (scalar 0.5) vs ON (resource-dependent). Full village stack + site appraisal.

Run:  py -3 -u outputs/climate_viz/run_storability.py
"""
import sys, os
import numpy as np
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.demography import STORABILITY_BY_RESOURCE as SB

FOUNDERS, STEPS, SEEDS = 400, 600, (0, 1, 2)
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_cult = _f.cultivability
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_farm = [(x, y) for y in range(100) for x in range(100)
         if _hf0.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
_zone = sorted(set((cx, cy) for (x, y) in _farm for dx in range(-2, 3) for dy in range(-2, 3)
                   for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                   if _hf0.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
_num = _cult * SB["grain"] + _f.aquatic_food * SB["fish"] + _f.forage * SB["forage"] + _f.game * SB["game"]
_den = _cult + _f.aquatic_food + _f.forage + _f.game
_SFRAC = np.where(_den > 0, _num / _den, 0.5)   # per-cell storability for measuring


def _one(seed, res_stor):
    hf = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = [_zone[i % len(_zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
        comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
        enable_leader_coherence=True, leader_coherence_gain=2.0, enable_size_repulsion=True, repulsion_gain=0.3,
        enable_village_scaling=True, village_gain=5.0,
        enable_site_appraisal=True, site_gain=0.3, site_radius=2, site_lambda=1.0,
        enable_resource_storability=res_stor))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=demog)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}
    occ_sfrac = sum(_SFRAC[y, x] * n for (x, y), n in occ.items()) / len(al)
    total_store = sum(getattr(w, "_cell_store", {}).values())
    return dict(pop=len(al), maxcell=max(occ.values()), pct=100 * sum(packed.values()) / len(al),
               occ=len(occ), sfrac=occ_sfrac, store=total_store / len(al))


def run(label, res_stor):
    rs = [r for s in SEEDS if (r := _one(s, res_stor)) is not None]
    if not rs:
        print(f"  {label:22s} EXTINCT"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    print(f"  {label:22s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}  %packed={mean('pct'):4.1f}%  "
          f"occ={mean('occ'):4.0f}  occ_storability={mean('sfrac'):.3f}  store/cap={mean('store'):.0f}")


def main():
    print(f"RESOURCE-DEPENDENT STORABILITY (mean {len(SEEDS)} seeds, {STEPS} steps). occ_storability UP = villages on storable-resource cells.\n")
    run("scalar 0.5 (OFF)", False)
    run("resource-dependent (ON)", True)


if __name__ == "__main__":
    main()
