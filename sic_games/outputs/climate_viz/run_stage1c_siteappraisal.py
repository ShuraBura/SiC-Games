"""Stage 1c — catchment SITE-APPRAISAL. A static central-place suitability field (Σ_catchment S_pot·exp(−λ·dist·
(0.5+cost)), normalized, ·site_gain·BURN) perceived in the IFD utility. This is the ASSEMBLY solution: a GLOBAL
gradient agents climb toward prime central places (Kennett-Winterhalder IFD-suitability), which the earlier analysis
found missing (local IFD couldn't assemble villages from scatter). KEY SIGNALS: (1) occupied cells shift to HIGHER
suitability (agents converge on prime real-estate); (2) FEWER occupied cells + higher max/cell (assembly/tightening);
(3) more packing. Sweep site_gain. Full stack: point-superlinear + cap + Stage 1 village scaling.

Run:  py -3 -u outputs/climate_viz/run_stage1c_siteappraisal.py
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

FOUNDERS, STEPS, SEEDS = 400, 600, (0, 1, 2)
SITE_R, SITE_LAM = 2, 1.0
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_cult = _f.cultivability
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_farm = [(x, y) for y in range(100) for x in range(100)
         if _hf0.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
_zone = sorted(set((cx, cy) for (x, y) in _farm for dx in range(-2, 3) for dy in range(-2, 3)
                   for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                   if _hf0.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
# normalized suitability field for MEASURING where agents settle
_sp = np.maximum(_f.aquatic_food, _cult); _ct = _f.cost
_acc = np.zeros_like(_sp)
for _dy in range(-SITE_R, SITE_R + 1):
    for _dx in range(-SITE_R, SITE_R + 1):
        _d = max(abs(_dx), abs(_dy))
        if _d == 0:
            _acc += _sp; continue
        _acc += np.roll(np.roll(_sp, _dy, 0), _dx, 1) * np.exp(-SITE_LAM * _d * (0.5 + np.roll(np.roll(_ct, _dy, 0), _dx, 1)))
_SUIT = _acc / _acc.max()


def _one(seed, site_gain):
    hf = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = [_zone[i % len(_zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
        comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
        enable_leader_coherence=True, leader_coherence_gain=2.0, enable_size_repulsion=True, repulsion_gain=0.3,
        enable_village_scaling=True, village_gain=5.0,
        enable_site_appraisal=(site_gain > 0), site_gain=site_gain, site_radius=SITE_R, site_lambda=SITE_LAM))
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
    occ_suit = sum(_SUIT[y, x] * n for (x, y), n in occ.items()) / len(al)   # occupancy-weighted site suitability
    bands = Counter(a._group.band_id for a in al)
    return dict(pop=len(al), maxcell=max(occ.values()), pct=100 * sum(packed.values()) / len(al),
               occ=len(occ), suit=occ_suit, maxband=max(bands.values()))


def run(label, site_gain):
    rs = [r for s in SEEDS if (r := _one(s, site_gain)) is not None]
    if not rs:
        print(f"  {label:24s} EXTINCT"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    print(f"  {label:24s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}  %packed={mean('pct'):4.1f}%  "
          f"occ={mean('occ'):4.0f}  occ_suit={mean('suit'):.3f}  MAXBAND={mean('maxband'):4.0f}")


def main():
    print(f"STAGE 1c — catchment site-appraisal (mean {len(SEEDS)} seeds, {STEPS} steps). occ_suit UP = converging on prime sites.\n")
    run("site appraisal OFF", 0.0)
    for g in (0.1, 0.3, 0.6):
        run(f"site_gain={g:g}", g)


if __name__ == "__main__":
    main()
