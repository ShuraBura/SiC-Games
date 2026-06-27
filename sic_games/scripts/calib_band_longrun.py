"""Does spread-seeding + founder buffer reach a SUSTAINED, turning-over equilibrium (not a slow bleed)?
Run the promising configs to 1800 steps (~150 yr); print the population trajectory + per-window births/deaths
and the generational turnover (births per 100 steps at the tail)."""
from __future__ import annotations

from collections import Counter

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import (TerrainWorld, seed_band_positions_spread, _DEFAULT_KNOBS)
from sic_games.terrain import generate_world

SEED = 7
N = 250
KC = KcalEconomyConfig()
BURN = KC.burn_kcal_per_day * KC.days_per_month
HOURS = KC.foraging_hours_per_day * KC.days_per_month
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


def run(buf, bonded=True, steps=1800, fill=1.0, spread_radius=2):
    fields = generate_world({**_DEFAULT_KNOBS, "seedStr": f"world{SEED}"})
    pos = seed_band_positions_spread(fields, N, HOURS, BURN, band_size=25, territory_radius=3,
                                     spread_radius=spread_radius, target_fill=fill)
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=0.0, **GRP)
    w = TerrainWorld(n_agents=N, kcal_cfg=KC, seed=SEED, game_stream=False, substrate_cfg=sc,
                     demography_cfg=DemographyConfig(enable_bonded_mating=bonded),
                     placement_positions=pos, founder_buffer_steps=buf)
    print(f"\n=== spread buf={buf} bonded={bonded} ===")
    print(f"{'step':>5} {'pop':>5} {'births':>7} {'deaths':>7}")
    wb = wd = 0
    for s in range(1, steps + 1):
        w.step()
        wb += w.births_this_step
        wd += w.deaths_starv_this_step + w.deaths_senesc_this_step
        if s % 200 == 0:
            print(f"{s:>5} {len(w.agent_list):>5} {wb:>7} {wd:>7}")
            wb = wd = 0
    return len(w.agent_list)


if __name__ == "__main__":
    run(6, bonded=False)   # control: asexual female-IBI (no mate requirement)
    run(6, bonded=True)    # bonded: per-CELL co-resident mate required
