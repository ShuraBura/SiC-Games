"""Re-arch Tier 0 A/B — mate_within_band_id. The mating pool was O(clump²) (spatial bands() balloons under
agglomeration). Fix = pool by social band_id (O(n)). Measure BOTH the perf win AND the fidelity price (does the
mating skew / village dynamics change? — the status→RS concern). A = spatial pool (current), B = band_id pool.

Run:  py -3 -u outputs/climate_viz/run_matefix_ab.py
"""
import sys, os, time
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

FOUNDERS, STEPS = 8000, 40
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_land = [(x, y) for y in range(100) for x in range(100) if _f.isWater[y, x] == 0 and _hf0.level(x, y) > 0]


def _run(band_id_pool):
    hf = ClimateField(NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True), a_seas=0.5)
    pos = [_land[i % len(_land)] for i in range(FOUNDERS)]
    demog = emergent_village_demog().model_copy(update=dict(mate_within_band_id=band_id_pool))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=demog)
    t0 = time.perf_counter()
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    dt = time.perf_counter() - t0
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}
    bands = Counter(a._group.band_id for a in al)
    soc = getattr(w, "_band_society", {})
    cplx = 100 * sum(bands[b] for b in bands if soc.get(b) in ("complex_forager", "stratified_chiefdom")) / len(al)
    # mate-skew proxy: #wives among adult males (the status→RS channel)
    males = [a for a in al if a.sex == "male" and a.age >= w._demog.menarche_months]
    wives = [len(a._wives) for a in males] if males else [0]
    married = [x for x in wives if x >= 1]
    return dict(ms=1000 * dt / STEPS, pop=len(al), maxcell=max(occ.values()), pct=100 * sum(packed.values()) / len(al),
                maxband=max(bands.values()), cplx=cplx, max_wives=max(wives),
                frac_married=100 * len(married) / max(len(males), 1), mean_wives=sum(wives) / max(len(males), 1))


def main():
    print(f"TIER 0 A/B — mate_within_band_id ({FOUNDERS} founders, {STEPS} steps).\n")
    print(f"  {'config':22s} {'ms/step':>7} {'pop':>4} {'max/cell':>8} {'%packed':>7} {'MAXBAND':>7} {'%cplx':>5} {'maxWiv':>6} {'%marr':>5} {'meanWiv':>7}")
    for label, bp in (("A spatial pool (current)", False), ("B band_id pool (fix)", True)):
        r = _run(bp)
        print(f"  {label:22s} {r['ms']:7.1f} {r['pop']:4.0f} {r['maxcell']:8.0f} {r['pct']:6.1f}% {r['maxband']:7.0f} {r['cplx']:4.0f}% "
              f"{r['max_wives']:6.0f} {r['frac_married']:4.0f}% {r['mean_wives']:7.2f}")


if __name__ == "__main__":
    main()
