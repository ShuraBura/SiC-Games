"""Investigate the MATING-POOL size problem (Wobst connubium). _do_pairing pools mates over bands(bonded_mate_radius)
= connected occupied cells. Under agglomeration this blob balloons into a thousands-strong regional cluster treated
as ONE panmictic pool (the O(clump^2) + anthropologically wrong). Measure the actual mating-pool size distribution
over a run vs the connubium scale (~500, Wobst 1974), and the relationship to social band_id sizes.

Run:  py -3 -u outputs/climate_viz/run_matepool_probe.py
"""
import sys, os
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

FOUNDERS, WOBST = 4000, 500
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_land = [(x, y) for y in range(100) for x in range(100) if _f.isWater[y, x] == 0 and _hf0.level(x, y) > 0]


def main():
    hf = ClimateField(NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True), a_seas=0.5)
    pos = [_land[i % len(_land)] for i in range(FOUNDERS)]
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=emergent_village_demog())
    rad = w._demog.bonded_mate_radius
    print(f"MATING-POOL PROBE — {FOUNDERS} founders, bonded_mate_radius={rad}. Connubium (Wobst) ~{WOBST}.\n")
    print(f"  {'step':>4} {'pop':>5} {'#pools':>6} {'maxpool':>7} {'pools>500':>9} {'%pop in >500':>12} {'#cells_maxpool':>14} {'maxband_id':>10}")
    for step in range(1, 121):
        w.step()
        if not w.agent_list:
            break
        if step in (10, 30, 60, 90, 120):
            al = w.agent_list
            pools = [len(b) for b in w.bands(rad)]
            pools.sort(reverse=True)
            big = [p for p in pools if p > WOBST]
            pop_big = sum(big)
            # cells spanned by the largest mating pool
            biggest = max(w.bands(rad), key=len)
            ncells = len({a.pos for a in biggest})
            bands_id = Counter(a._group.band_id for a in al)
            print(f"  {step:>4} {len(al):>5} {len(pools):>6} {pools[0]:>7} {len(big):>9} {100*pop_big/len(al):>11.0f}% {ncells:>14} {max(bands_id.values()):>10}")


if __name__ == "__main__":
    main()
