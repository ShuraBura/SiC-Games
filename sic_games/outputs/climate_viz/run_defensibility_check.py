"""Economic-defensibility A/B (the "does it work?" test). Same canonical full-stack config, aquatic+depletion
world, defensibility OFF vs ON. Question: does letting bands OWN + DEFEND the dense predictable aquatic cells
finally make them CONCENTRATE on those reaches (band density crosses Binford packing 0.091; owned cells fill),
where the C8 subsidy alone could not (GATE-3)? Interior egalitarian + no-extinction must survive.

Run:  py -3 -u outputs/climate_viz/run_defensibility_check.py
"""
import sys, os
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

FOUNDERS, STEPS = 600, 1500
PACK = 0.091


def run(defend, seed=0):
    k = world_lottery_climate(seed, terrain="mountainous", climate="tropical")
    f = generate_world(k, mode="climate")
    cap = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    cells = [(x, y) for y in range(100) for x in range(100) if cap.level(x, y) > 0]
    pos = [cells[i % len(cells)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(enable_economic_defensibility=defend))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    tag = "DEFEND" if defend else "  OFF "
    print(f"  [{tag}] ceiling={cap.ceiling:.0f}", flush=True)
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            print(f"  [{tag}] EXTINCT at step {i+1}", flush=True); return
        if i % 300 == 299 or i == STEPS - 1:
            occ = Counter(a.pos for a in al)
            bm = defaultdict(int); bc = defaultdict(set)
            for a in al:
                bm[a._group.band_id] += 1; bc[a._group.band_id].add(a.pos)
            dens = [bm[b] / (len(bc[b]) * _CELL_KM2) for b in bm]
            packed = sum(1 for d in dens if d >= PACK) / len(dens)
            soc = Counter(w._band_society.get(b) for b in bm)
            cplx = (soc.get("complex_forager", 0) + soc.get("stratified_chiefdom", 0)) / max(1, sum(soc.values()))
            owner = w._cell_owner
            oocc = [occ.get(c, 0) for c in owner]
            print(f"  [{tag}] step {i+1:4d}: pop={len(al):5d}  max/cell={max(occ.values()):3d}  "
                  f"band_dens_max={max(dens):.3f}  %packed={100*packed:3.0f}%  %cplx={100*cplx:3.0f}%  "
                  f"owned={len(owner):3d}  owned_occ_max={max(oocc) if oocc else 0:3d}  "
                  f"owned_occ_mean={sum(oocc)/len(oocc) if oocc else 0:.1f}", flush=True)


def main():
    print(f"ECON-DEFENSIBILITY A/B — mountainous-tropical, {FOUNDERS} founders x {STEPS} steps, aquatic+depletion; "
          f"packing threshold {PACK}/km^2\n")
    run(False)
    print()
    run(True)


if __name__ == "__main__":
    main()
