"""Agriculture tier LAYER A: do FARMING villages form on fertile land via the S_pot swap? A temperate world
(cultivable land, LITTLE aquatic food); enable_agriculture OFF vs ON (aggregation-sedentism ON both). OFF ⇒
S_pot=aquatic_food (low on farmland) ⇒ no settlements; ON ⇒ S_pot=max(aquatic,cultivability) ⇒ settlements form
on fertile land and pack→morph like fishery villages (the generality payoff). Soil still static (Layer B next).

Run:  py -3 -u outputs/climate_viz/run_agriculture_layerA.py
"""
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

FOUNDERS, STEPS, PACK = 400, 1200, 0.091
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_cult, _aq = _f.cultivability, _f.aquatic_food
print(f"flat-temperate world: cultivability max={_cult.max():.2f} mean={_cult.mean():.3f} "
      f"cells>=0.3={int((_cult>=0.3).sum())};  aquatic_food max={_aq.max():.2f} mean={_aq.mean():.3f}")


def run(agri):
    cap = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    farm = [(x, y) for y in range(100) for x in range(100)
            if cap.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
    zone = set()
    for (x, y) in farm:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cx, cy = (x + dx) % 100, (y + dy) % 100
                if cap.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0:
                    zone.add((cx, cy))
    zone = sorted(zone) or [(x, y) for y in range(100) for x in range(100) if cap.level(x, y) > 0]
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True, enable_agriculture=agri))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    tag = "AGRI-ON " if agri else "AGRI-OFF"
    print(f"  [{tag}] {len(farm)} fertile cells (cult>=0.5) in the seeded zone", flush=True)
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print(f"  [{tag}] EXTINCT {i+1}", flush=True); return
        if i % 300 == 299 or i == STEPS - 1:
            bm = defaultdict(int); bc = defaultdict(set)
            for a in al:
                bm[a._group.band_id] += 1; bc[a._group.band_id].add(a.pos)
            dens = [bm[b] / (len(bc[b]) * _CELL_KM2) for b in bm]
            packed = sum(1 for d in dens if d >= PACK) / len(dens)
            soc = Counter(w._band_society.get(b) for b in bm)
            cplx = (soc.get("complex_forager", 0) + soc.get("stratified_chiefdom", 0)) / max(1, sum(soc.values()))
            print(f"  [{tag}] step {i+1:4d}: pop={len(al):4d}  settlements={len(w._settlement_sites):2d}  "
                  f"band_dens_max={max(dens):.3f}  %packed={100*packed:3.0f}%  %cplx={100*cplx:3.0f}%", flush=True)


def main():
    print("\nAGRICULTURE LAYER A — do farming villages form on fertile land via the S_pot swap?\n")
    run(False)
    print()
    run(True)


if __name__ == "__main__":
    main()
