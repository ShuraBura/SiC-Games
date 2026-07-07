"""Scarcity calibration — STAGE 1: seasonal lean + hard-won storage (activate the dormant Testart/storage half).

Two levers vs the land-of-plenty (R-56):
  (1) SEASONALITY ON — harvest wrapped in ClimateField(a_seas) so there's a growing-season glut → lean-season draw
      (the village harnesses ran seasonless: bare NPPCapacityField has no .season()).
  (2) HARD-WON STORAGE — raise store_capacity_reserves so a full granary is an ACHIEVEMENT only storable-efficient
      cells reach (storable_fraction sets the FILL RATE; with a low cap both storable+forage cells fill it → no
      differential; with a HIGH cap, forage cells can't fill before winter → storable villages survive, forage don't).

Validation: (a) stores actually DRAW DOWN over the year (drawdown frac > 0 = the lean bites, not saturated);
(b) with the high cap, storability ON should SEPARATE (occ_storability up = villages on storable-resource sites).
Instruments the living-granary total over the last 3 years to measure seasonal draw-down.

Run:  py -3 -u outputs/climate_viz/run_scarcity_stage1.py
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
from sic_games.demography import STORABILITY_BY_RESOURCE as SB

FOUNDERS, STEPS, SEEDS = 400, 600, (0, 1, 2)
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_cult = _f.cultivability
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_farm = [(x, y) for y in range(100) for x in range(100)
         if _hf0.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
_zone = sorted(set((cx, cy) for (x, y) in _farm for dx in range(-2, 3) for dy in range(-2, 3)
                   for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                   if _hf0.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
_num = _cult * SB["grain"] + _f.aquatic_food * SB["fish"] + _f.forage * SB["forage"] + _f.game * SB["game"]
_den = _cult + _f.aquatic_food + _f.forage + _f.game
_SFRAC = np.full_like(_cult, 0.5, dtype=float); np.divide(_num, _den, out=_SFRAC, where=_den > 0)

BASE = dict(
    enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
    comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
    enable_leader_coherence=True, leader_coherence_gain=2.0, enable_size_repulsion=True, repulsion_gain=0.3,
    enable_village_scaling=True, village_gain=5.0,
    enable_site_appraisal=True, site_gain=0.3, site_radius=2, site_lambda=1.0)


def _one(seed, a_seas, store_cap, res_stor):
    base = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    hf = ClimateField(base, a_seas=a_seas) if a_seas > 0 else base
    pos = [_zone[i % len(_zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        BASE, store_capacity_reserves=store_cap, enable_resource_storability=res_stor))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=demog)
    store_series = []
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
        if t >= STEPS - 36:                                  # sample living-granary total over the last 3 years
            occ = {a.pos for a in w.agent_list}
            cs = getattr(w, "_cell_store", {})
            store_series.append(sum(cs.get(c, 0.0) for c in occ))
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}
    occ_sfrac = sum(_SFRAC[y, x] * n for (x, y), n in occ.items()) / len(al)
    smax = max(store_series) if store_series else 0.0
    drawdown = (smax - min(store_series)) / smax if smax > 0 else 0.0
    return dict(pop=len(al), pct=100 * sum(packed.values()) / len(al), maxcell=max(occ.values()),
               sfrac=occ_sfrac, drawdown=100 * drawdown)


def run(label, a_seas, store_cap, res_stor):
    rs = [r for s in SEEDS if (r := _one(s, a_seas, store_cap, res_stor)) is not None]
    if not rs:
        print(f"  {label:38s} EXTINCT"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    print(f"  {label:38s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}  %packed={mean('pct'):4.1f}%  "
          f"store_drawdown={mean('drawdown'):4.0f}%  occ_storability={mean('sfrac'):.3f}")


def main():
    print(f"SCARCITY STAGE 1 — seasonal lean + hard-won storage (mean {len(SEEDS)} seeds, {STEPS} steps).")
    print("  store_drawdown>0 = lean bites (not saturated); occ_storability ON>OFF = storable villages win.\n")
    print("  [A] seasonal a_seas=0.6, LOW granary cap=3 (default — both cell types fill it):")
    run("cap=3, storability OFF", 0.6, 3.0, False)
    run("cap=3, storability ON", 0.6, 3.0, True)
    print("\n  [B] seasonal a_seas=0.6, HIGH granary cap=12 (only storable cells fill it → storability binds?):")
    run("cap=12, storability OFF", 0.6, 12.0, False)
    run("cap=12, storability ON", 0.6, 12.0, True)


if __name__ == "__main__":
    main()
