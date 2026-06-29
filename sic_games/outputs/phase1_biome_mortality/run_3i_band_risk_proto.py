"""F.2 PROTOTYPE — does the band risk-dilution (loner penalty, scaled by biome incident rate) measurably shift
the emergent band-size distribution, and does the disease(↑)–safety(↓) tradeoff yield an optimal band size?

Corrected substrate (CC-1 capacity patch + grouping + bonded mating) with terrain-risk ON (the anchored biome
baseline) + density-disease ON. Sweep band_risk_penalty; measure the connected-component band-size distribution
+ the fraction of agents living in sub-viable vs viable bands. If the modal/mean band size rises with the
penalty (loners selected out) and density-disease caps the top, an optimum exists. If the effect is negligible,
that is the (honest) finding: risk-dilution on the Aché-accident scale is too small to set band size.
Run:  py -3 -u outputs/phase1_biome_mortality/run_3i_band_risk_proto.py
"""
from __future__ import annotations
import os, time, statistics
from collections import Counter

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, N as GRID_N
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

OUT = os.path.dirname(os.path.abspath(__file__))
SEEDS = list(range(5))
STEPS, FOUNDERS = 800, 300
MATE_R = 1
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)
PENALTIES = [0.0, 1.0, 3.0, 6.0]


def band_sizes(world, radius=MATE_R):
    """Connected-component band sizes (cells linked when Chebyshev-adjacent within radius)."""
    occ = Counter(a.pos for a in world.agent_list)
    cells = list(occ)
    if not cells:
        return []
    parent = {c: c for c in cells}
    def find(c):
        while parent[c] != c:
            parent[c] = parent[parent[c]]; c = parent[c]
        return c
    cs = set(cells)
    for (x, y) in cells:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nb = (x + dx, y + dy)
                if nb in cs:
                    parent[find((x, y))] = find(nb)
    comp = {}
    for c in cells:
        comp[find(c)] = comp.get(find(c), 0) + occ[c]
    return list(comp.values())


def band_positions_patch(fields, cap, n, band_size=25, sep=4):
    cells = sorted(((cap.level(x, y), x, y) for y in range(GRID_N) for x in range(GRID_N)
                    if fields.isWater[y, x] == 0 and cap.level(x, y) > 0), reverse=True)
    sites, pos = [], []
    for (_, x, y) in cells:
        if len(sites) >= max(1, n // band_size):
            break
        if all(max(abs(x - px), abs(y - py)) >= sep for (px, py) in sites):
            sites.append((x, y)); pos.extend([(x, y)] * band_size)
    i = 0
    while len(pos) < n and sites:
        pos.append(sites[i % len(sites)]); i += 1
    return pos[:n]


def run_one(penalty, seed):
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, cap, FOUNDERS)
    demog = DemographyConfig(
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_terrain_risk=True, risk_cap=3.0,
        enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_bonded_mating=True, bonded_mate_radius=MATE_R,
        enable_band_risk=(penalty > 0.0), band_risk_penalty=penalty, band_risk_size=25)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.0, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    t0 = int(0.6 * STEPS)
    sizes_accum, pops = [], []
    for step in range(STEPS):
        w.step()
        if step >= t0 and w.agent_list:
            sizes_accum.append(band_sizes(w)); pops.append(len(w.agent_list))
    flat = [s for snap in sizes_accum for s in snap]
    if not flat:
        return None
    pop = statistics.mean(pops)
    # agent-weighted band size (the band size the average AGENT lives in) + small-band fraction
    aw = sum(s * s for s in flat) / sum(flat)
    n_bands = statistics.mean([len(snap) for snap in sizes_accum])
    frac_small = sum(s for s in flat if s < 5) / sum(flat)       # agents in sub-viable (<5) bands
    frac_viable = sum(s for s in flat if s >= 15) / sum(flat)    # agents in viable (≥15) bands
    return dict(pop=pop, agentwt_band=aw, n_bands=n_bands, max_band=max(flat),
                frac_small=frac_small, frac_viable=frac_viable)


def main():
    t0 = time.time()
    print(f"{'penalty':>8} {'pop':>5} {'agentwt_band':>13} {'n_bands':>8} {'max_band':>9} {'frac<5':>7} {'frac>=15':>9}")
    for p in PENALTIES:
        rows = [r for r in (run_one(p, s) for s in SEEDS) if r]
        agg = {k: statistics.mean([r[k] for r in rows]) for k in rows[0]}
        print(f"{p:>8.1f} {agg['pop']:>5.0f} {agg['agentwt_band']:>13.1f} {agg['n_bands']:>8.1f} "
              f"{agg['max_band']:>9.0f} {agg['frac_small']:>7.2f} {agg['frac_viable']:>9.2f}  "
              f"[{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
