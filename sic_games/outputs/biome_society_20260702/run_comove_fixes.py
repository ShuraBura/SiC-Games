"""CENTRAL-PLACE co-movement fixes — comparison (R-41 → the fix).

R-41: family co-movement over-subscribes the mother's (root's) cell → energetic-fertility collapse in marginal
biomes (savanna births 4x lower). Real foragers CO-RESIDE but forage DISPERSED + SHARE (central place). Three
ablatable prototypes, compared here on savanna (the collapse) + forest (must stay healthy — the control):
  (i)  comove_anticipate       — root evaluates per-capita on S/(n+family)
  (ii) comove_footprint=k      — followers scatter to low-occupancy cells within k of the head (dispersed camp)
  (iii)comove_provision_exclude— juvenile followers take NO forage share (provisioned, central-place)
Reference arms: A = full canonical (exact-snap co-move, the collapse); OFF = enable_pair_bonds False (no bonds).

Run:  py -3 -u outputs/biome_society_20260702/run_comove_fixes.py
"""
import sys, os, statistics, time
sys.path.insert(0, os.path.dirname(__file__))
from run_biome_society import realistic_forager_demog, capacity_aware_seed, BURN, X0, Y0, PATCH, FOUNDERS, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery
from sic_games.capacity import NPPCapacityField

STEPS, SEEDS = 900, 3
ARMS = {
    "A canon (exact snap)": {},
    "i anticipate":         dict(comove_anticipate=True),
    "ii footprint=1":       dict(comove_footprint=1),
    "ii footprint=2":       dict(comove_footprint=2),
    "iii provis-exclude":   dict(comove_provision_exclude=True),
    "i+ii anticip+fp1":     dict(comove_anticipate=True, comove_footprint=1),
    "OFF (no pair_bonds)":  dict(enable_pair_bonds=False),
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
    print(f"CENTRAL-PLACE co-movement fixes — savanna (collapse) + forest (control), {SEEDS} seeds x {STEPS} steps\n")
    for arch in ("savanna", "forest"):
        print(f"  === {arch} ===")
        print(f"    {'arm':<22}{'pop(mean)':>11}{'survive':>9}{'births':>9}")
        for label, upd in ARMS.items():
            rows = [run(arch, s, upd) for s in range(SEEDS)]
            alive = [r for r in rows if r["pop"] > 0]
            popm = statistics.mean(r["pop"] for r in alive) if alive else 0.0
            bm = statistics.mean(r["births"] for r in rows)
            print(f"    {label:<22}{popm:>11.0f}{str(len(alive))+'/'+str(SEEDS):>9}{bm:>9.0f}   [{time.time()-t0:.0f}s]")
        print()
    print("  Read: a good fix lifts savanna pop/births toward the OFF reference WITHOUT hurting forest (control).")


if __name__ == "__main__":
    main()
