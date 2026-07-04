"""Layer 2b — (1) settlement LIFESPAN across seeds (right-censoring still-alive settlements), and (2) an AUTOPSY
of why a settlement dissolves (the window before each dissolution: settled-pop, starvation vs senescence deaths,
shock, storage). Distinguishes a stable century-village from churn, and food-deficit dispersal from drift/noise.

Run:  py -3 -u outputs/climate_viz/run_shock_lifespan.py
"""
import sys, os, statistics
from collections import deque
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField

FOUNDERS, STEPS, SEEDS = 400, 1800, [0, 1, 2, 3]
_k = world_lottery_climate(0, terrain="mountainous", climate="tropical")
_f = generate_world(_k, mode="climate")
_aq = _f.aquatic_food
_reach = [(x, y) for y in range(100) for x in range(100)
          if _f.isWater[y, x] == 0 and _aq[y, x] >= 0.5]
_zone = set()
for (x, y) in _reach:
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            _zone.add(((x + dx) % 100, (y + dy) % 100))


def run(update, seed, autopsy=False):
    cap = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    zone = sorted(c for c in _zone if cap.level(*c) > 0 and _f.isWater[c[1], c[0]] == 0)
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True, **update))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    rad = w._demog.settle_radius
    prev, age, dissolved = set(), {}, []
    buf = deque(maxlen=8); autopsied = 0
    for i in range(STEPS):
        w.step()
        al = w.agent_list
        if not al:
            break
        now = set(w._settlement_sites)
        spop = sum(1 for a in al if any(w._torus_cheby(a.pos[0], a.pos[1], s[0], s[1]) <= rad for s in now | prev))
        rec = (i + 1, spop, w.deaths_starv_this_step, getattr(w, "deaths_senesc_this_step", 0),
               w._tier2_shock, sum(w._cell_store.get(s, 0.0) for s in (now | prev)))
        buf.append(rec)
        for s in now - prev:
            age[s] = i
        for s in prev - now:
            dissolved.append(i - age.pop(s, i))
            if autopsy and autopsied < 2:
                autopsied += 1
                print(f"    -- dissolution autopsy (seed {seed}) — window before collapse "
                      f"[step: settled_pop starv senesc shock store] --")
                for (st, sp, sv, sn, sh, sto) in buf:
                    print(f"       {st:4d}: pop={sp:4d}  starv={sv:2d} senesc={sn:2d}  shock={sh:.2f}  store={sto:8.0f}")
        prev = now
    censored = [STEPS - a for a in age.values()]      # still-alive settlements at end (right-censored)
    return dissolved, censored


def characterize(name, update):
    dis_all, cen_all = [], []
    for s in SEEDS:
        d, c = run(update, s)
        dis_all += d; cen_all += c
    md = statistics.mean(dis_all) if dis_all else float('nan')
    mc = statistics.mean(cen_all) if cen_all else float('nan')
    print(f"  {name:20s} dissolved: n={len(dis_all):2d} mean_life={md:5.0f} ({md/12:4.1f}yr)   "
          f"still-alive@end: n={len(cen_all):2d} mean_age={mc:5.0f} ({mc/12:4.1f}yr)")


def main():
    print(f"LAYER 2b LIFESPAN — {len(SEEDS)} seeds × {STEPS} steps (1 step = 1 month)\n")
    characterize("no-shock", dict(enable_tier2_shock=False))
    characterize("IID cv0.6", dict(enable_tier2_shock=True, shock_cv=0.6, shock_rho=0.0))
    characterize("regime cv0.6 rho.85", dict(enable_tier2_shock=True, shock_cv=0.6, shock_rho=0.85))
    print("\n  AUTOPSY (regime cv0.6 rho0.85):")
    for s in SEEDS[:2]:
        run(dict(enable_tier2_shock=True, shock_cv=0.6, shock_rho=0.85), s, autopsy=True)


if __name__ == "__main__":
    main()
