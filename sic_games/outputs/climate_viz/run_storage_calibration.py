"""Storage recalibration (lit-grounded). Targets (LITERATURE.md storage survey): stored fraction of surplus ~0.5-0.8;
granary capacity ~1-2 YEARS of subsistence (Halstead normal-surplus: annual cycle + bad-year buffer); decay ~10-30%/yr;
and the granary must run a strong ANNUAL FILL->DEPLETE cycle, not stay full. Model mapping: store_capacity_reserves
~9-18 for 1-2 yr (default 3 = 4 months, far too low), storable_fraction ~0.7, storage_decay ~0.02/mo (~22%/yr).

This traces the per-capita granary (in MONTHS of subsistence) over the last 4 years to check for a realistic seasonal
sawtooth: max ~= capacity (12-24 mo), trough ~= a reserve floor, deep drawdown each lean. Sweeps lean depth a_seas.

Run:  py -3 -u outputs/climate_viz/run_storage_calibration.py
"""
import sys, os
import numpy as np
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

FOUNDERS, STEPS, SEEDS = 400, 600, (0, 1)
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_cult = _f.cultivability
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_farm = [(x, y) for y in range(100) for x in range(100)
         if _hf0.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
_zone = sorted(set((cx, cy) for (x, y) in _farm for dx in range(-2, 3) for dy in range(-2, 3)
                   for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                   if _hf0.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))

CAL = dict(  # lit-calibrated storage
    enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
    comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
    enable_leader_coherence=True, leader_coherence_gain=2.0, enable_size_repulsion=True, repulsion_gain=0.3,
    enable_village_scaling=True, village_gain=5.0,
    enable_site_appraisal=True, site_gain=0.3, site_radius=2, site_lambda=1.0,
    store_capacity_reserves=12.0, storable_fraction=0.7, storage_decay=0.02)


def _one(seed, a_seas, store_cap):
    base = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    hf = ClimateField(base, a_seas=a_seas)
    pos = [_zone[i % len(_zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(CAL, store_capacity_reserves=store_cap))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=demog)
    series = []
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        if t >= STEPS - 48:                                  # per-capita living-granary in MONTHS of subsistence
            occ = {a.pos for a in w.agent_list}
            cs = getattr(w, "_cell_store", {})
            tot = sum(cs.get(c, 0.0) for c in occ)
            series.append(tot / len(w.agent_list) / BURN)     # months of BURN per capita
    return dict(pop=len(w.agent_list), series=series)


def run(label, a_seas, store_cap):
    rs = [r for s in SEEDS if (r := _one(s, a_seas, store_cap)) is not None]
    if not rs:
        print(f"  {label:30s} EXTINCT"); return
    ser = np.mean([r["series"] for r in rs], axis=0)
    smax, smin = ser.max(), ser.min()
    dd = 100 * (smax - smin) / smax if smax > 0 else 0
    pop = np.mean([r["pop"] for r in rs])
    spark = "".join("▁▂▃▄▅▆▇█"[min(7, int(v / max(smax, 1e-9) * 7.99))] for v in ser[::2])
    print(f"  {label:30s} pop={pop:4.0f}  cap_reached={smax:4.1f}mo  trough={smin:4.1f}mo  drawdown={dd:3.0f}%  |{spark}|")


def main():
    print(f"STORAGE CALIBRATION — per-capita granary in MONTHS over last 4 yr (mean {len(SEEDS)} seeds).")
    print("  Target: cap 12-24 mo (1-2 yr), DEEP annual drawdown (sawtooth), trough = reserve floor.\n")
    print("  [cap=12 (~16 mo), storable=0.7, decay=0.02/mo] — lean-depth sweep:")
    for a in (0.3, 0.6, 0.85):
        run(f"a_seas={a:g}", a, 12.0)
    print("\n  granary-capacity check (a_seas=0.6):")
    for sc in (3.0, 12.0, 18.0):
        run(f"store_cap={sc:g} (~{sc*1.33:.0f} mo)", 0.6, sc)


if __name__ == "__main__":
    main()
