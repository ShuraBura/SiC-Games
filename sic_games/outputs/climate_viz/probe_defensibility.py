"""Diagnose why econ-defensibility never claims: is aquatic_food present, what is its range in the patch, and
what is the per-band occupancy on the richest aquatic cells (the bootstrapping question)?"""
import sys, os
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

k = world_lottery_climate(0, terrain="mountainous", climate="tropical")
f = generate_world(k, mode="climate")
cap = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
cells = [(x, y) for y in range(100) for x in range(100) if cap.level(x, y) > 0]
pos = [cells[i % len(cells)] for i in range(600)]
demog = realistic_forager_demog().model_copy(update=dict(enable_economic_defensibility=True))
w = TerrainWorld(n_agents=600, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
    carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
        movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
    harvest_field=cap, placement_positions=pos, demography_cfg=demog)

aq = getattr(w._fields, "aquatic_food", None)
print(f"model _fields.aquatic_food present: {aq is not None}")
if aq is not None:
    print(f"  global: max={aq.max():.3f} mean={aq.mean():.4f}  nonzero cells={int((aq>0).sum())}")
    patch_mask = np.zeros_like(aq, dtype=bool)
    patch_mask[Y0:Y0+PATCH, X0:X0+PATCH] = True
    aqp = aq[patch_mask]
    print(f"  in patch: max={aqp.max():.3f}  cells>0={int((aqp>0).sum())}")
    for thr in (0.05, 0.10, 0.15, 0.30, 0.50):
        print(f"    patch cells with aquatic_food >= {thr}: {int((aqp>=thr).sum())}")

for i in range(300):
    w.step()
al = w.agent_list
print(f"\nafter 300 steps: pop={len(al)}  owned cells={len(w._cell_owner)}")
# occupancy on the richest aquatic cells: how many agents, and same-band clustering?
occ_band = defaultdict(lambda: defaultdict(int))
for a in al:
    occ_band[a.pos][a._group.band_id] += 1
isw = w._fields.isWater
if aq is not None:
    rich = sorted(((float(aq[y, x]), (x, y)) for (x, y) in cells if aq[y, x] > 0), reverse=True)[:12]
    print(f"top aquatic cells in habitable set (value, isWater, total_occ, max_same_band_occ):")
    for val, c in rich:
        bands = occ_band.get(c, {})
        tot = sum(bands.values()); mx = max(bands.values()) if bands else 0
        print(f"  {c} aq={val:.3f}  water={int(isw[c[1], c[0]])}  total_occ={tot:3d}  max_same_band={mx:3d}")
# where ARE the agents, relative to aquatic_food + water; and the best same-band cluster ANYWHERE
occ_aq = [float(aq[y, x]) for (x, y) in occ_band]
land_occ = sum(1 for (x, y) in occ_band if isw[y, x] == 0)
print(f"\noccupied cells: {len(occ_band)} ({land_occ} land / {len(occ_band)-land_occ} water)")
print(f"  aquatic_food at occupied cells: max={max(occ_aq):.3f} mean={sum(occ_aq)/len(occ_aq):.3f}")
best = max(((max(b.values()), c, dict(b)) for c, b in occ_band.items()))
print(f"  BEST same-band cluster anywhere: {best[0]} members on {best[1]} (aq={float(aq[best[1][1],best[1][0]]):.3f}, water={int(isw[best[1][1],best[1][0]])})")
print(f"  cells with any band >=3 same-band: {sum(1 for b in occ_band.values() if max(b.values())>=3)}")
print(f"  cells with any band >=2 same-band: {sum(1 for b in occ_band.values() if max(b.values())>=2)}")
