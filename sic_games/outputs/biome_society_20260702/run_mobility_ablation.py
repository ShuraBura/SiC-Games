"""MOBILITY ABLATION on the biome->society experiment (validates §4.8.19, R-39 root fix).

R-39 diagnosed the low-NPP (savanna/desert) collapse as fixed-r=1 mobility: agents can't spread over sparse
territory, so families pile on the few rich cells -> overcrowd -> starve. This runs each archetype with
`enable_productivity_mobility` OFF (the R-37 collapse) vs ON (productivity-scaled stride) and reports eq_pop +
realized per-cell density, to test whether the pile-up dissipates and marginal biomes now SUSTAIN a society.

Run:  py -3 -u outputs/biome_society_20260702/run_mobility_ablation.py
"""
import sys, os, statistics, time
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from run_biome_society import (realistic_forager_demog, capacity_aware_seed, BURN, X0, Y0, PATCH,
                               FOUNDERS, STEPS, TAIL, GRP)
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery, WORLD_ARCHETYPE_ORDER
from sic_games.capacity import NPPCapacityField

SEEDS_PER = 3


def run(archetype, seed, mobility):
    knobs = world_lottery(seed * 5, archetype=archetype)
    fields = generate_world(knobs)
    cap = NPPCapacityField(fields, BURN, patch=(X0, Y0, PATCH), mode="tallavaara")
    pos = capacity_aware_seed(cap, BURN, FOUNDERS)
    if not pos:
        return None
    demog = realistic_forager_demog()
    if mobility:
        demog = demog.model_copy(update=dict(enable_productivity_mobility=True))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs, game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                      contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    pops, occ_max, dens_occ = [], [], []
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            return dict(extinct=True)
        if step >= STEPS - TAIL:
            pops.append(len(al))
            cells = Counter(a.pos for a in al)
            occ_max.append(max(cells.values()))
            dens_occ.append(len(al) / len(cells))     # mean persons per OCCUPIED cell (the pile-up metric)
    return dict(extinct=False, eq_pop=statistics.mean(pops),
                occ_max=statistics.mean(occ_max), dens_occ=statistics.mean(dens_occ))


def main():
    t0 = time.time()
    res = {(a, m): [] for a in WORLD_ARCHETYPE_ORDER for m in (False, True)}
    ext = defaultdict(int)
    for arch in WORLD_ARCHETYPE_ORDER:
        for m in (False, True):
            for seed in range(SEEDS_PER):
                r = run(arch, seed, m)
                if r is None:
                    continue
                if r.get("extinct"):
                    ext[(arch, m)] += 1
                else:
                    res[(arch, m)].append(r)
        print(f"  {arch:<8} done  [{time.time()-t0:.0f}s]", flush=True)

    print(f"\n=== MOBILITY ABLATION (Tallavaara CC-1, {SEEDS_PER} seeds/arm) — "
          f"does productivity-scaled stride relieve the low-NPP pile-up? ===")
    print(f"  {'archetype':<9}{'arm':>5}{'survive':>9}{'eq_pop':>8}{'occ/cell':>10}{'max/cell':>10}")
    for arch in WORLD_ARCHETYPE_ORDER:
        for m in (False, True):
            rows = res[(arch, m)]
            tag = "ON" if m else "OFF"
            if not rows:
                print(f"  {arch:<9}{tag:>5}{'0/'+str(SEEDS_PER):>9}   (all extinct)")
                continue
            mm = lambda k: statistics.mean(r[k] for r in rows)
            print(f"  {arch:<9}{tag:>5}{str(len(rows))+'/'+str(SEEDS_PER):>9}"
                  f"{mm('eq_pop'):>8.0f}{mm('dens_occ'):>10.2f}{mm('occ_max'):>10.1f}")
    print("\n  Read: if ON lifts eq_pop / survival AND lowers occ-per-cell in savanna/desert/mixed, the fixed-r=1\n"
          "  pile-up (R-39) is the collapse root and productivity-scaled mobility relieves it (R-40).")


if __name__ == "__main__":
    main()
