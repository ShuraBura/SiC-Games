"""Scarcity calibration — STAGE 2: RESOURCE-STRUCTURED (river-ribbon) world. Sharpen cultivability into thin ribbons
along river channels: cult_ribbon = cult · exp(−d2river/λ). This (a) makes prime arable SCARCE + linear (Nile-valley
structure → circumscription) and (b) makes storable(river-grain) vs perishable(hinterland-forage) sites SPATIALLY
DISTINCT — so the lean season has something to select on: river villages store grain + survive; hinterland foragers
can't store → must stay mobile / contract. Seasonal (ClimateField a_seas) + hard-won storage (high granary cap).

PREDICTION (vs the land-of-plenty, R-56): on the ribbon world, storability ON should finally SEPARATE — occupancy
concentrates on storable river ribbons (occ_storability up, near-river fraction up), because only storable sites
buffer the lean. If ON>OFF here (where it was flat on the abundant world), the Testart mechanism is validated.

Run:  py -3 -u outputs/climate_viz/run_scarcity_stage2.py
"""
import sys, os
import numpy as np
from collections import Counter
from scipy import ndimage
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
LAM_RIVER, A_SEAS, STORE_CAP = 0.8, 0.6, 12.0

_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_river = (_f.isRiver != 0)
_d2r = ndimage.distance_transform_edt(~_river)
_NEAR = (_d2r <= 1) & (_f.isWater == 0)                      # river-ribbon mask (for occupancy measurement)
# SHARPEN cultivability into river ribbons (inject into the world fields — WorldFields is mutable)
_cult_ribbon = _f.cultivability * np.exp(-_d2r / LAM_RIVER)
_f.cultivability = _cult_ribbon
_land = _f.isWater == 0
_prime = (_cult_ribbon >= 0.5) & _land
print(f"[ribbon world] cultivable>=0.5: {int(_prime.sum())} cells ({100*_prime.sum()/_land.sum():.0f}% of land; was ~20%)  "
      f"river ribbon (d<=1): {int(_NEAR.sum())} cells", flush=True)

_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_farm = [(x, y) for y in range(100) for x in range(100)
         if _hf0.level(x, y) > 0 and _land[y, x] and _cult_ribbon[y, x] >= 0.4]
_zone = sorted(set((cx, cy) for (x, y) in _farm for dx in range(-2, 3) for dy in range(-2, 3)
                   for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                   if _hf0.level(cx, cy) > 0 and _land[cy, cx]))
_den = _cult_ribbon + _f.aquatic_food + _f.forage + _f.game


def _sfrac_field():
    num = _cult_ribbon * SB["grain"] + _f.aquatic_food * SB["fish"] + _f.forage * SB["forage"] + _f.game * SB["game"]
    out = np.full_like(_cult_ribbon, 0.5, dtype=float); np.divide(num, _den, out=out, where=_den > 0)
    return out

FULL = dict(
    enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
    comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
    enable_leader_coherence=True, leader_coherence_gain=2.0, enable_size_repulsion=True, repulsion_gain=0.3,
    enable_village_scaling=True, village_gain=5.0,
    enable_site_appraisal=True, site_gain=0.3, site_radius=2, site_lambda=1.0,
    enable_terrain_move_cost=True, move_cost_kcal=0.01 * BURN, store_capacity_reserves=STORE_CAP)


def _one(seed, res_stor, sharp=False):
    if sharp:                                            # fresh forage barely stores; grain keeps -> 18x contrast
        SB.update(grain=0.90, fish=0.85, forage=0.05, game=0.20)
    else:
        SB.update(grain=0.85, fish=0.80, forage=0.15, game=0.35)
    sfrac = _sfrac_field()
    base = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    hf = ClimateField(base, a_seas=A_SEAS)
    pos = [_zone[i % len(_zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(FULL, enable_resource_storability=res_stor))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=demog)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}
    occ_sfrac = sum(sfrac[y, x] * n for (x, y), n in occ.items()) / len(al)
    near_frac = 100 * sum(1 for a in al if _NEAR[a.pos[1], a.pos[0]]) / len(al)
    return dict(pop=len(al), pct=100 * sum(packed.values()) / len(al), maxcell=max(occ.values()),
               sfrac=occ_sfrac, near=near_frac)


def run(label, res_stor, sharp=False):
    rs = [r for s in SEEDS if (r := _one(s, res_stor, sharp)) is not None]
    if not rs:
        print(f"  {label:24s} EXTINCT"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    print(f"  {label:24s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}  %packed={mean('pct'):4.1f}%  "
          f"near_river={mean('near'):4.0f}%  occ_storability={mean('sfrac'):.3f}")


def main():
    print(f"\nSCARCITY STAGE 2 — river-ribbon world (mean {len(SEEDS)} seeds, {STEPS} steps, a_seas={A_SEAS}, cap={STORE_CAP:g}).")
    print("  storability ON>OFF (occ_storability + near_river) = villages concentrate on storable river ribbons.\n")
    run("storability OFF", False)
    run("storability ON (default 0.85/0.15)", True)
    run("storability ON (SHARP 0.90/0.05)", True, sharp=True)


if __name__ == "__main__":
    main()
