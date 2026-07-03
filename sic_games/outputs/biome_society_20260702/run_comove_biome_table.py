"""FULL biome→society validation of the central-place footprint fix (R-42) across ALL archetypes.

The co-residence/co-foraging decoupling must work in EVERY biome, not just savanna. Compares, per archetype:
  A canon (exact snap)    — the R-37 collapse
  footprint=1 (uniform)   — fixed dispersed camp (the supervisor lean)
  footprint-scaled        — biome-scaled monthly range (k∝1/NPP: forest≈0 tight, savanna≈2-3) — the principled
                            form honoring "10 km cell = forest monthly range" without variable cells
  OFF (no pair_bonds)     — the no-co-movement reference ceiling
Reports eq_pop, survival, births per arm. A good fix lifts the marginal biomes toward OFF while keeping forest
sane (the uniform footprint over-spreads the forest — the scaled form should keep forest tight).

Run:  py -3 -u outputs/biome_society_20260702/run_comove_biome_table.py
"""
import sys, os, statistics, time
sys.path.insert(0, os.path.dirname(__file__))
from run_biome_society import realistic_forager_demog, capacity_aware_seed, BURN, X0, Y0, PATCH, FOUNDERS, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery, WORLD_ARCHETYPE_ORDER
from sic_games.capacity import NPPCapacityField

STEPS, SEEDS = 900, 3
ARMS = {
    "A exact-snap":     {},
    "footprint=1":      dict(comove_footprint=1),
    "footprint-scaled": dict(comove_footprint_scaled=True, comove_footprint_max=3),
    "OFF (no bonds)":   dict(enable_pair_bonds=False),
}


def run(archetype, seed, update):
    knobs = world_lottery(seed * 5, archetype=archetype)
    fields = generate_world(knobs)
    cap = NPPCapacityField(fields, BURN, patch=(X0, Y0, PATCH), mode="tallavaara")
    pos = capacity_aware_seed(cap, BURN, FOUNDERS)
    demog = realistic_forager_demog().model_copy(update=update)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs, game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                      contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    B = 0
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return dict(pop=0, births=B)
        B += w.births_this_step
    return dict(pop=len(w.agent_list), births=B)


def main():
    t0 = time.time()
    print(f"FULL biome→society × central-place fix — {SEEDS} seeds × {STEPS} steps\n")
    print(f"  {'archetype':<9}{'arm':<18}{'pop':>7}{'survive':>9}{'births':>9}")
    for arch in WORLD_ARCHETYPE_ORDER:
        for label, upd in ARMS.items():
            rows = [run(arch, s, upd) for s in range(SEEDS)]
            alive = [r for r in rows if r["pop"] > 0]
            popm = statistics.mean(r["pop"] for r in alive) if alive else 0.0
            bm = statistics.mean(r["births"] for r in rows)
            print(f"  {arch:<9}{label:<18}{popm:>7.0f}{str(len(alive))+'/'+str(SEEDS):>9}{bm:>9.0f}   [{time.time()-t0:.0f}s]")
        print()


if __name__ == "__main__":
    main()
