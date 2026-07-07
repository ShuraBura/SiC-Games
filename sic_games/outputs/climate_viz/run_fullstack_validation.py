"""Branch A FULL-STACK validation — EVERY emergent village mechanism ON together, across the scarcity gradient.
Confirms the mechanisms compose coherently (no crash, healthy pop) and reproduces the headline: villages emerge
where land is CIRCUMSCRIBED (scarce), disperse where abundant (emergent Carneiro). Stack: point-superlinear + forage
cap + hierarchy-gated village scaling (leader + scalar-stress) + terrain move metabolism + catchment site-appraisal +
resource-dependent storability, on top of the full realistic_forager_demog (bands + morph + assabiyah + polygyny).

Run:  py -3 -u outputs/climate_viz/run_fullstack_validation.py
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

FULL = dict(
    enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
    comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
    enable_leader_coherence=True, leader_coherence_gain=2.0, enable_size_repulsion=True, repulsion_gain=0.3,
    enable_village_scaling=True, village_gain=5.0,
    enable_site_appraisal=True, site_gain=0.3, site_radius=SITE_R, site_lambda=SITE_LAM,
    enable_terrain_move_cost=True, move_cost_kcal=0.01 * BURN,
    enable_resource_storability=True)


def _setup(terrain):
    k = world_lottery_climate(0, terrain=terrain, climate="temperate")
    f = generate_world(k, mode="climate")
    hf0 = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    cult = f.cultivability
    farm = [(x, y) for y in range(100) for x in range(100)
            if hf0.level(x, y) > 0 and f.isWater[y, x] == 0 and cult[y, x] >= 0.5]
    zone = sorted(set((cx, cy) for (x, y) in farm for dx in range(-2, 3) for dy in range(-2, 3)
                      for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                      if hf0.level(cx, cy) > 0 and f.isWater[cy, cx] == 0))
    sp = np.maximum(f.aquatic_food, cult); ct = f.cost
    acc = np.zeros_like(sp)
    for dy in range(-SITE_R, SITE_R + 1):
        for dx in range(-SITE_R, SITE_R + 1):
            d = max(abs(dx), abs(dy))
            if d == 0:
                acc += sp; continue
            acc += np.roll(np.roll(sp, dy, 0), dx, 1) * np.exp(-SITE_LAM * d * (0.5 + np.roll(np.roll(ct, dy, 0), dx, 1)))
    return k, f, zone, acc / acc.max(), len(farm)


def _one(env, seed):
    k, f, zone, suit, _ = env
    hf = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=FULL)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
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
    occ_suit = sum(suit[y, x] * n for (x, y), n in occ.items()) / len(al)
    bands = Counter(a._group.band_id for a in al)
    soc = getattr(w, "_band_society", {})
    cplx = sum(bands[b] for b in bands if soc.get(b) in ("complex_forager", "stratified_chiefdom")) / len(al)
    return dict(pop=len(al), maxcell=max(occ.values()), pct=100 * sum(packed.values()) / len(al),
               occ=len(occ), suit=occ_suit, maxband=max(bands.values()), cplx=100 * cplx)


def run(env, label):
    rs = [r for s in SEEDS if (r := _one(env, s)) is not None]
    if not rs:
        print(f"  {label:24s} EXTINCT (all seeds)"); return
    def mean(kk): return sum(r[kk] for r in rs) / len(rs)
    print(f"  {label:24s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}  %packed={mean('pct'):4.1f}%  "
          f"occ={mean('occ'):4.0f}  MAXBAND={mean('maxband'):4.0f}  occ_suit={mean('suit'):.2f}  %complex={mean('cplx'):3.0f}%")


def main():
    print(f"FULL-STACK VALIDATION — all Branch A mechanisms ON (mean {len(SEEDS)} seeds, {STEPS} steps).\n")
    for terrain in ("flat", "hilly", "mountainous"):
        env = _setup(terrain)
        run(env, f"{terrain} (cult={env[4]})")


if __name__ == "__main__":
    main()
