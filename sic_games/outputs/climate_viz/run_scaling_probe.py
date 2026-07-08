"""SCALING PROBE — measure real per-step cost + memory as agent count grows toward the 30K-100K target (Turchin
secular-cycle campaign, ~18000 steps for 1500 yr). Spread placement across all land (realistic density), short runs,
report ms/step, us/agent/step, and peak Python-heap. Extrapolate to 100K and flag where scaling breaks (superlinear
ops, grid saturation on the 100x100 = 10k-cell map).

Run:  py -3 -u outputs/climate_viz/run_scaling_probe.py
"""
import sys, os, time, tracemalloc, gc
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

STEPS = 8   # measure per-step COMPUTE at scale, before over-capacity die-off confounds it
_k = world_lottery_climate(0, terrain="flat", climate="temperate")   # NOT scarce_arable (want productive land for the perf test)
_f = generate_world(_k, mode="climate")
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_land = [(x, y) for y in range(100) for x in range(100) if _f.isWater[y, x] == 0 and _hf0.level(x, y) > 0]


def _run(founders):
    hf = ClimateField(NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True), a_seas=0.5)
    pos = [_land[i % len(_land)] for i in range(founders)]        # spread across PRODUCTIVE land
    gc.collect(); tracemalloc.start()
    w = TerrainWorld(n_agents=founders, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=emergent_village_demog())
    t0 = time.perf_counter()
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    dt = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    pop = len(w.agent_list)
    ms = 1000 * dt / STEPS
    return founders, pop, ms, 1e6 * dt / STEPS / max(pop, 1), peak / 1e6


def main():
    print(f"SCALING PROBE — emergent_village_demog, spread placement, {STEPS} steps/run.")
    print(f"  {'founders':>8} {'pop':>6} {'ms/step':>8} {'us/agent':>9} {'heap_MB':>8}  (target: 30K-100K agents x ~18000 steps)")
    prev = None
    for nf in (1000, 2000, 4000, 8000, 16000, 32000):
        nf_, pop, ms, us, mb = _run(nf)
        creep = f" ({us/prev:.2f}x us/agent vs prev)" if prev else ""
        print(f"  {nf_:8d} {pop:6d} {ms:8.1f} {us:9.1f} {mb:8.0f}{creep}")
        prev = us
    print("\n  Extrapolate to 18000 steps: hours/run = us/agent * agents * 18000 / 3.6e9")


if __name__ == "__main__":
    main()
