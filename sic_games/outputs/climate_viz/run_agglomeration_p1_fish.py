"""Agglomeration P1 — POINT-resource test. On the aquatic (mountainous-tropical) world, S_pot=aquatic is
CONCENTRATED on rare reaches (not areal like farmland). Does the same increasing-returns economy now nucleate
PACKED villages on the reaches (where geography forces concentration)? α=1.5, sweep half; GRP neutralised.
"""
import sys, os
from collections import Counter
sys.path.insert(0, "outputs/biome_society_20260702"); sys.path.insert(0, "outputs/phase1_social_evolution")
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
F, STEPS = 400, 800
_k = world_lottery_climate(0, terrain="mountainous", climate="tropical")
_f = generate_world(_k, mode="climate"); _aq = _f.aquatic_food

def run(aggl, half=15.0, tier2=2.0, dd=True, fp=1):
    cap = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    reach = [(x, y) for y in range(100) for x in range(100)
             if cap.level(x, y) > 0 and _f.isWater[y, x] == 0 and _aq[y, x] >= 0.5]
    zone = sorted(set((cx, cy) for (x, y) in reach for dx in range(-2, 3) for dy in range(-2, 3)
                      for cx, cy in [((x+dx) % 100, (y+dy) % 100)] if cap.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
    pos = [zone[i % len(zone)] for i in range(F)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=aggl, aggl_alpha=1.5, aggl_half=half,
        aggl_tier2=tier2, aggl_catchment_radius=1, enable_density_disease=dd, comove_footprint=fp))
    grp = dict(group_safety_max=0.0, group_safety_scale=15.0, group_mate_min=0.0, group_mate_floor=0.2)
    w = TerrainWorld(n_agents=F, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **grp),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    for i in range(STEPS):
        w.step()
        if not w.agent_list: return f"  [{'OFF' if not aggl else f'h={half:g} t={tier2:g}'}] EXTINCT {i+1}"
    occ = Counter(a.pos for a in w.agent_list)
    packed = {c: n for c, n in occ.items() if n >= 9}
    tag = "OFF (IFD)" if not aggl else f"h={half:g} t={tier2:g}"
    return (f"  [{tag:12s}] pop={len(w.agent_list):4d}  max/cell={max(occ.values()):4d}  "
            f"packed(≥9)={len(packed):3d}  %pop_packed={100*sum(packed.values())/len(w.agent_list):3.0f}%  occ_cells={len(occ):4d}")

print("AGGLOMERATION P1 POINT-RESOURCE — aquatic (mountainous-tropical) world; does a CONCENTRATED reach nucleate packed villages?\n")
print(run(False))
print()
for h in (10.0, 25.0, 50.0):
    print(run(True, half=h, tier2=2.0))
print()
for t in (20.0, 50.0, 150.0):
    print(run(True, half=25.0, tier2=t))
print()
print("  -- density-disease OFF (is it the cap?) --")
print(run(True, half=25.0, tier2=20.0, dd=False))
print(run(True, half=50.0, tier2=20.0, dd=False))
print()
print("  -- footprint OFF (families STACK, not scatter) --")
print(run(True, half=25.0, tier2=20.0, fp=0))
print(run(True, half=15.0, tier2=20.0, fp=0))
