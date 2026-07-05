"""Agglomeration P1 — does increasing-returns-to-co-location NUCLEATE villages under IFD (no discrete-settlement
code), and at what α does it flip from band-scale to village-scale? Static S_pot (cultivability), soil=1. Sweep
aggl_alpha; measure peak cell occupancy + packed cells (≥9/cell = Binford 0.091/km²) + %pop packed.

Run:  py -3 -u outputs/climate_viz/run_agglomeration_p1.py
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

FOUNDERS, STEPS = 400, 800
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_cult = _f.cultivability


def run(aggl, alpha=1.15):
    cap = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    farm = [(x, y) for y in range(100) for x in range(100)
            if cap.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
    zone = sorted(set((cx, cy) for (x, y) in farm for dx in range(-2, 3) for dy in range(-2, 3)
                      for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                      if cap.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=aggl, aggl_alpha=alpha, aggl_half=100.0,
        aggl_tier2=40.0, aggl_catchment_radius=1))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    for i in range(STEPS):
        w.step()
        if not w.agent_list:
            return f"  [{'OFF' if not aggl else f'α={alpha}'}] EXTINCT at {i+1}"
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}          # ≥9/cell = Binford 0.091/km²
    pop_packed = sum(packed.values())
    tag = "OFF (IFD)" if not aggl else f"α={alpha}"
    return (f"  [{tag:9s}] pop={len(al):4d}  max/cell={max(occ.values()):4d}  "
            f"packed_cells(≥9)={len(packed):3d}  %pop_packed={100*pop_packed/len(al):3.0f}%  "
            f"occupied_cells={len(occ):4d}")


def main():
    print("AGGLOMERATION P1 — nucleation vs α (increasing returns to co-location; no discrete settlements)\n")
    print(run(False))
    print()
    for a in (1.15, 1.3, 1.5, 2.0):
        print(run(True, a))


if __name__ == "__main__":
    main()
