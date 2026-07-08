"""Does the finite resource create an EMERGENT size limit + boom-bust when a catchment is STRESSED (packed near/over
its food capacity)? Force high local density on a small patch, run long, track the stock B, population, and per-capita
— looking for deplete → per-capita crash → die-off/disperse → stock recovers → regrow (the Malthusian cycle that
makes band/village size EMERGENT, not hardcoded). Sweep depletion strength (deplete_frac) + recovery lag.

Run:  py -3 -u outputs/climate_viz/run_catchment_stress.py
"""
import sys, os
import numpy as np
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

STEPS = 300
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
# a small rich patch (3x3) — force high local density to STRESS the catchment
_rich = max(((x, y) for y in range(100) for x in range(100) if _f.isWater[y, x] == 0 and _hf0.level(x, y) > 0),
            key=lambda c: _hf0.level(*c))
_patch = [((_rich[0] + dx) % 100, (_rich[1] + dy) % 100) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]


def _run(deplete_frac, recovery_scale, n=400):
    base = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True,
                            deplete_frac=deplete_frac, recovery_scale=recovery_scale)
    hf = ClimateField(base, a_seas=0.5)
    pos = [_patch[i % len(_patch)] for i in range(n)]       # ~44/cell on the 3x3 patch → stressed
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=0,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=emergent_village_demog())
    pops, Bmins = [], []
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            pops.append(0); break
        pops.append(len(w.agent_list))
        Bmins.append(float(base._B[base._B > 0].min()))     # most-depleted cell stock
    pops = np.array(pops)
    # detect a cycle: does pop overshoot then fall then recover?
    peak = pops.max(); trough = pops[len(pops) // 3:].min() if len(pops) > 10 else pops.min()
    return dict(final=pops[-1], peak=int(peak), trough=int(trough), amp=100 * (peak - trough) / max(peak, 1),
                Bmin=min(Bmins) if Bmins else 1.0)


def main():
    print(f"CATCHMENT STRESS — 400 agents forced onto a 3x3 patch, {STEPS} steps. Looking for deplete→crash→recover.")
    print("  Bmin↓ = stock depletes (finite bites); amp = pop overshoot-collapse % (the Malthusian cycle).\n")
    print(f"  {'deplete_frac':>12} {'recovery':>8} {'peak':>5} {'trough':>6} {'final':>5} {'overshoot_amp':>13} {'min_stock_B':>11}")
    for df in (0.5, 2.0, 5.0):
        for rs in (1.0, 0.25):
            r = _run(df, rs)
            print(f"  {df:>12g} {rs:>8g} {r['peak']:>5} {r['trough']:>6} {r['final']:>5} {r['amp']:>12.0f}% {r['Bmin']:>11.2f}")


if __name__ == "__main__":
    main()
