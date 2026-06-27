"""DECISIVE TEST: run the emergent-bands substrate on the CC-1 NPP-capacity field (the field R-18/19 used,
~30-50 persons/cell) instead of the bare terrain forage (~1-8/cell). Hypothesis: on the rich field a cell can
hold a whole band, density-disease regulates instead of starvation, and per-CELL bonded mating sustains a
turning-over population. Full-grid (no patch mask) so bands spread across biomes."""
from __future__ import annotations

from collections import Counter
import numpy as np

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld, _DEFAULT_KNOBS
from sic_games.terrain import generate_world, N as GRID_N

BURN = 75000.0
NPP_THRESH, DENS_SLOPE, DENS_CAP, CELL_KM2 = 1360.0, 0.3, 0.5, 100.0


class CC1Capacity:
    """Full-grid CC-1 capacity (the R-18/19 SubWindowCapacity, no patch mask): E = dens·cell_km2·burn,
    dens = min(DENS_CAP, DENS_SLOPE·NPP/NPP_THRESH) persons/km². E/burn = supportable persons/cell."""
    def __init__(self, fields):
        self.width = self.height = GRID_N
        dens = np.minimum(DENS_CAP, DENS_SLOPE * fields.npp_gm2 / NPP_THRESH)
        self._E = dens * CELL_KM2 * BURN
        self._cap = dens * CELL_KM2
    def level(self, x, y): return float(self._E[y, x])
    def harvest(self, x, y): return float(self._E[y, x])


def seed_on_capacity(fields, cap_field, n, band_size=25, territory_radius=4, rng=None):
    """Seed band sites on the highest-capacity land cells (territory-spaced); stack band_size per site
    (the cell can hold it now). Returns placement_positions."""
    import random as _random
    rng = rng or _random.Random(0)
    cap = np.array([[cap_field.level(x, y) / BURN for x in range(GRID_N)] for y in range(GRID_N)])
    land = np.asarray(fields.isWater) == 0
    cand = sorted(((cap[y, x], x, y) for y in range(GRID_N) for x in range(GRID_N)
                   if land[y, x] and cap[y, x] >= band_size * 0.6), reverse=True)
    sites, positions = [], []
    n_bands = max(1, n // band_size)
    for (_, x, y) in cand:
        if len(sites) >= n_bands:
            break
        if all(max(abs(x - px), abs(y - py)) >= territory_radius for (px, py) in sites):
            sites.append((x, y)); positions.extend([(x, y)] * band_size)
    i = 0
    while len(positions) < n and sites:
        positions.append(sites[i % len(sites)]); i += 1
    return positions[:n], sites


def run(bonded, density_disease=True, steps=1500, seed=7, n=250, kappa=0.0, grouping=False, mate_r=0):
    fields = generate_world({**_DEFAULT_KNOBS, "seedStr": f"world{seed}"})
    cap = CC1Capacity(fields)
    import random
    pos, sites = seed_on_capacity(fields, cap, n, rng=random.Random(seed))
    grp = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0,
               group_mate_floor=0.2) if grouping else {}
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=kappa,
                         move_cost_flat=0.0, **grp)
    dkw = dict(siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
               enable_bonded_mating=bonded, bonded_mate_radius=mate_r)
    if density_disease:
        dkw.update(enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_DEFAULT_KNOBS,
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=sc, harvest_field=cap, placement_positions=pos,
                     demography_cfg=DemographyConfig(**dkw))
    print(f"\n=== CC-1 capacity, bonded={bonded}, mate_r={mate_r}, dens_disease={density_disease}, "
          f"grouping={grouping}, {len(sites)} band sites ===")
    print(f"{'step':>5} {'pop':>5} {'births':>7} {'deaths':>7} {'meanocc':>7} {'maxocc':>6}")
    wb = wd = 0
    for s in range(1, steps + 1):
        w.step(); wb += w.births_this_step; wd += w.deaths_starv_this_step + w.deaths_senesc_this_step
        if s % 150 == 0:
            occ = Counter(a.pos for a in w.agent_list); nc = len(occ)
            mo = (sum(occ.values()) / nc) if nc else 0.0
            mx = max(occ.values()) if occ else 0
            print(f"{s:>5} {len(w.agent_list):>5} {wb:>7} {wd:>7} {mo:>7.2f} {mx:>6}")
            wb = wd = 0


if __name__ == "__main__":
    run(bonded=True, grouping=True, mate_r=0)   # per-cell gate (baseline: bleeds out)
    run(bonded=True, grouping=True, mate_r=1)   # neighbourhood r=1 (band territory)
    run(bonded=True, grouping=True, mate_r=2)   # neighbourhood r=2
