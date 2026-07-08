"""Does the FINITE + CYCLIC resource actually cap per-cell density and drive Malthusian boom-bust? Track, over a run:
(1) true per-cell density max/cell (dispel the '2000/cell' idea), (2) the resource STOCK at packed vs empty cells
(is a crowded cell hunted out? = depletion working), (3) per-capita intake at the densest cell (does it crash under
crowding? = finite limit). Enable_depletion is ON (GD-1). Seasonal via ClimateField.

Run:  py -3 -u outputs/climate_viz/run_resource_dynamics.py
"""
import sys, os
import numpy as np
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

FOUNDERS = 3000
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_land = [(x, y) for y in range(100) for x in range(100) if _f.isWater[y, x] == 0 and _hf0.level(x, y) > 0]


def _stock(base):
    # resource stock fraction B (finite depletable) if exposed, else current level as proxy
    return getattr(base, "B", getattr(base, "_B", None))


def main():
    base = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    hf = ClimateField(base, a_seas=0.5)
    pos = [_land[i % len(_land)] for i in range(FOUNDERS)]
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=emergent_village_demog())
    B = _stock(base)
    print(f"RESOURCE DYNAMICS — {FOUNDERS} founders. Finite stock B∈[0,1] present: {B is not None}\n")
    print(f"  {'step':>4} {'pop':>5} {'max/cell':>8} {'mean_occ':>8} {'B@packed':>9} {'B@empty':>8} {'percap@max/BURN':>16}")
    for step in range(1, 151):
        w.step()
        if not w.agent_list:
            break
        if step % 25 == 0:
            al = w.agent_list
            occ = Counter(a.pos for a in al)
            mx = max(occ, key=occ.get); mxn = occ[mx]
            packed = [c for c, n in occ.items() if n >= 9]
            empty = [(x, y) for (x, y) in _land if (x, y) not in occ][:2000]
            Bp = np.mean([B[y, x] for (x, y) in packed]) if (B is not None and packed) else float("nan")
            Be = np.mean([B[y, x] for (x, y) in empty]) if (B is not None and empty) else float("nan")
            percap = hf.level(mx[0], mx[1]) / mxn / BURN     # per-capita at densest cell, in units of subsistence
            print(f"  {step:>4} {len(al):>5} {mxn:>8} {sum(occ.values())/len(occ):>8.1f} {Bp:>9.2f} {Be:>8.2f} {percap:>16.2f}")


if __name__ == "__main__":
    main()
