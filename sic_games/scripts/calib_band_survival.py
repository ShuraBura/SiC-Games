"""Calibrate founder survival of the first season(s): sweep (founder_buffer_steps) x (seeding: stacked vs
capacity-gated spread). Measures LIVE population (corpses now removed) at the end of season 1 (step 12),
season 1y (100), and long (400), plus births and band cohesion (mean live cell-occupancy + neighbourhood
clustering). Answers the supervisor's question: what initial buffer / seeding lets a band survive its first
season, and does fixing capacity then solve the mate problem (births > 0 under bonded mating)?"""
from __future__ import annotations

from collections import Counter

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import (TerrainWorld, seed_band_positions,
                                    seed_band_positions_spread, _DEFAULT_KNOBS)
from sic_games.terrain import generate_world

SEED = 7
N = 250
KC = KcalEconomyConfig()
BURN = KC.burn_kcal_per_day * KC.days_per_month
HOURS = KC.foraging_hours_per_day * KC.days_per_month
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


def _neighbours_mean(occ):
    """Mean over occupied cells of (occupants within Chebyshev r=1, incl self) — band cohesion at the
    territory grain even when each cell holds ~1 agent."""
    cells = list(occ)
    if not cells:
        return 0.0
    tot = 0
    for (x, y) in cells:
        s = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                s += occ.get((x + dx, y + dy), 0)
        tot += s
    return tot / len(cells)


def run(seeding, buffer_steps, bonded=True, steps=400, fill=1.0, spread_radius=2):
    fields = generate_world({**_DEFAULT_KNOBS, "seedStr": f"world{SEED}"})
    if seeding == "stacked":
        pos = seed_band_positions(fields, N, band_size=25, territory_radius=3)
    else:
        pos = seed_band_positions_spread(fields, N, HOURS, BURN, band_size=25, territory_radius=3,
                                         spread_radius=spread_radius, target_fill=fill)
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=0.0, **GRP)
    w = TerrainWorld(n_agents=N, kcal_cfg=KC, seed=SEED, game_stream=False, substrate_cfg=sc,
                     demography_cfg=DemographyConfig(enable_bonded_mating=bonded),
                     placement_positions=pos, founder_buffer_steps=buffer_steps)
    marks = {12: None, 100: None, 400: None}
    births = 0
    for s in range(1, steps + 1):
        w.step()
        births += w.births_this_step
        if s in marks:
            occ = Counter(a.pos for a in w.agent_list)
            marks[s] = (len(w.agent_list), _neighbours_mean(occ), births)
    return marks


def main():
    print(f"burn/step={BURN:.0f}  N={N}  bonded=True  (live population; corpses removed)")
    print(f"{'seeding':>8} {'buf':>4} | {'s12 pop':>8} {'nbr':>5} | {'s100 pop':>8} {'nbr':>5} {'births':>7} | "
          f"{'s400 pop':>8} {'nbr':>5} {'births':>7}")
    for seeding in ("stacked", "spread"):
        for buf in (0, 1, 3, 6, 12):
            m = run(seeding, buf)
            p12, n12, _ = m[12]
            p100, n100, b100 = m[100]
            p400, n400, b400 = m[400]
            print(f"{seeding:>8} {buf:>4} | {p12:>8} {n12:>5.1f} | {p100:>8} {n100:>5.1f} {b100:>7} | "
                  f"{p400:>8} {n400:>5.1f} {b400:>7}")


if __name__ == "__main__":
    main()
