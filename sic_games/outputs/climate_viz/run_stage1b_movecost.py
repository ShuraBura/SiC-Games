"""Stage 1b — terrain-dependent MOVEMENT COST. Relocating burns move_cost_kcal·cost[dest] (cost∈[0.15,1], the terrain
traversal difficulty), drained at metabolism (movers deplete → sedentism selected) and perceived in IFD (prefer to
stay / take cheap-terrain steps → central-place foraging). Locomotion was previously free. Test on the SAME flat-farm
world as Stage 1 (its `cost` field still varies, std~0.15 — slope is per-world normalized). KEY SIGNALS: (1) occupied
cells shift to LOWER terrain cost than the land mean (0.44) — agents settle cheap valleys; (2) more packing/sedentism.
Sweep move_cost_kcal as a fraction of BURN (75000). Full stack: point-superlinear + cap + Stage 1 village scaling.

Run:  py -3 -u outputs/climate_viz/run_stage1b_movecost.py
"""
import sys, os
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

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
_LANDMEAN = float(_f.cost[_f.isWater == 0].mean())


def _one(seed, mc_kcal):
    hf = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = [_zone[i % len(_zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
        comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
        enable_leader_coherence=True, leader_coherence_gain=2.0, enable_size_repulsion=True, repulsion_gain=0.3,
        enable_village_scaling=True, village_gain=5.0,
        enable_terrain_move_cost=(mc_kcal > 0), move_cost_kcal=mc_kcal))
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
    occ_cost = sum(_f.cost[y, x] * n for (x, y), n in occ.items()) / len(al)   # occupancy-weighted terrain cost
    bands = Counter(a._group.band_id for a in al)
    return dict(pop=len(al), maxcell=max(occ.values()), pct=100 * sum(packed.values()) / len(al),
               occ=len(occ), occcost=occ_cost, maxband=max(bands.values()))


def run(label, mc_kcal):
    rs = [r for s in SEEDS if (r := _one(s, mc_kcal)) is not None]
    if not rs:
        print(f"  {label:26s} EXTINCT"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    print(f"  {label:26s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}  %packed={mean('pct'):4.1f}%  "
          f"occ={mean('occ'):4.0f}  occ_cost={mean('occcost'):.3f}(land {_LANDMEAN:.3f})  MAXBAND={mean('maxband'):4.0f}")


def main():
    print(f"STAGE 1b — terrain move cost (mean {len(SEEDS)} seeds, {STEPS} steps). occ_cost<{_LANDMEAN:.2f} = settling cheap terrain.\n")
    run("move cost OFF", 0.0)
    for frac in (0.005, 0.01, 0.02, 0.04):
        run(f"move cost {frac:g}*BURN ({frac*BURN:.0f})", frac * BURN)


if __name__ == "__main__":
    main()
