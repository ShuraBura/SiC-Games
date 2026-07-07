"""FULL AUDIT — perf + heavy diagnostics for the emergent-village stack across maps. Runs emergent_village_demog()
(the whole stack ON) on each terrain with scarce_arable + seasonality, reporting BOTH timing (ms/step, scaling with
agent count) and the full diagnostic panel (pop, packing, villages, complexity, riverine concentration, storage).

Run:  py -3 -u outputs/climate_viz/run_full_audit.py
"""
import sys, os, time
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

STEPS, A_SEAS = 400, 0.5


def _build(terrain, seed=0):
    k = world_lottery_climate(seed, terrain=terrain, climate="temperate", scarce_arable=True)
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True), a_seas=A_SEAS)
    cult = f.cultivability
    river = (f.isRiver != 0)
    from scipy import ndimage
    near = (ndimage.distance_transform_edt(~river) <= 1) & (f.isWater == 0)
    zone = sorted((x, y) for y in range(100) for x in range(100)
                  if f.isWater[y, x] == 0 and hf.level(x, y) > 0 and cult[y, x] >= 0.3)
    if not zone:
        zone = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    return k, f, hf, zone, near


def _run(terrain, founders, steps, timing_only=False):
    k, f, hf, zone, near = _build(terrain)
    hf = ClimateField(NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True), a_seas=A_SEAS)
    pos = [zone[i % len(zone)] for i in range(founders)]
    w = TerrainWorld(n_agents=founders, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=emergent_village_demog())
    t0 = time.perf_counter()
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            break
    dt = time.perf_counter() - t0
    al = w.agent_list
    ms = 1000 * dt / steps
    if not al:
        return dict(terrain=terrain, founders=founders, ms=ms, pop=0)
    if timing_only:
        return dict(terrain=terrain, founders=founders, ms=ms, pop=len(al), ms_per_agent=1000 * dt / steps / max(len(al), 1))
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}
    bands = Counter(a._group.band_id for a in al)
    soc = getattr(w, "_band_society", {})
    cplx = sum(bands[b] for b in bands if soc.get(b) in ("complex_forager", "stratified_chiefdom")) / len(al)
    near_frac = 100 * sum(1 for a in al if near[a.pos[1], a.pos[0]]) / len(al)
    cs = getattr(w, "_cell_store", {})
    store_mo = sum(cs.get(c, 0.0) for c in occ) / len(al) / BURN
    return dict(terrain=terrain, founders=founders, ms=ms, pop=len(al), maxcell=max(occ.values()),
                pct=100 * sum(packed.values()) / len(al), occ=len(occ), maxband=max(bands.values()),
                cplx=100 * cplx, near=near_frac, store=store_mo)


def main():
    print(f"FULL AUDIT — emergent_village_demog + scarce_arable + seasonal (a_seas={A_SEAS}), {STEPS} steps.\n")
    print("  [A] DIAGNOSTICS across maps (founders=400):")
    print(f"  {'terrain':12s} {'ms/step':>7} {'pop':>4} {'max/cell':>8} {'%packed':>7} {'MAXBAND':>7} {'%cplx':>5} {'near_riv':>8} {'store_mo':>8}")
    for terr in ("flat", "hilly", "mountainous", "coastal"):
        r = _run(terr, 400, STEPS)
        if r.get("pop", 0) == 0:
            print(f"  {terr:12s} {r['ms']:7.1f}  EXTINCT"); continue
        print(f"  {terr:12s} {r['ms']:7.1f} {r['pop']:4.0f} {r['maxcell']:8.0f} {r['pct']:6.1f}% {r['maxband']:7.0f} {r['cplx']:4.0f}% {r['near']:7.0f}% {r['store']:7.1f}")
    print("\n  [B] PERF SCALING — flat map, ms/step vs agent count (100 steps):")
    print(f"  {'founders':>8} {'pop':>4} {'ms/step':>7} {'us/agent/step':>13}")
    for nf in (200, 400, 800, 1600):
        r = _run("flat", nf, 100, timing_only=True)
        print(f"  {nf:8d} {r['pop']:4.0f} {r['ms']:7.1f} {1000*r.get('ms_per_agent',0):12.1f}")


if __name__ == "__main__":
    main()
