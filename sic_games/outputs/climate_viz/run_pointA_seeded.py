"""Branch A — DECISIVE disambiguation. The spread-seed sweep (run_agglomeration_pointA) showed point-superlinear does
NOT assemble a village under local IFD — it forms multiple locally-stable clumps. Question: is that because (i) the
ECONOMICS can't SUSTAIN a village, or (ii) local IFD can't ASSEMBLE one (a symmetry-breaking/global-gradient gap)?

Test: SEED all founders CONCENTRATED on one 2×2 block (a pre-formed proto-village), then see if a large settlement
PERSISTS. If point-mode HOLDS/grows the seeded village while baseline DISPERSES it → economics is fine, only ASSEMBLY
is missing (→ add migration-to-largest / pin). If point ALSO disperses it → the returns don't support villages.

Run:  py -3 -u outputs/climate_viz/run_pointA_seeded.py
"""
import sys, os
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
_k = world_lottery_climate(0, terrain="flat", climate="temperate")
_f = generate_world(_k, mode="climate")
_cult = _f.cultivability
# richest cultivable cell → seed all founders on its 2×2 block (a pre-formed proto-village)
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_bx, _by = max(((x, y) for y in range(100) for x in range(100)
                if _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5), key=lambda c: _hf0.level(*c))
_block = [((_bx + dx) % 100, (_by + dy) % 100) for dx in (0, 1) for dy in (0, 1)]
_SEEDPOS = [_block[i % len(_block)] for i in range(FOUNDERS)]   # ~100 agents/cell, 4 cells


def _one(aggl, tier2, seed, beta=1.15):
    hf = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=aggl, aggl_mode="point", aggl_beta=beta,
        aggl_tier2=tier2, comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=_SEEDPOS, demography_cfg=demog)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}
    return dict(pop=len(al), maxcell=max(occ.values()), pct=100 * sum(packed.values()) / len(al), occ=len(occ))


def run(label, aggl=True, tier2=10.0, beta=1.15):
    rs = [r for s in SEEDS if (r := _one(aggl, tier2, s, beta)) is not None]
    if not rs:
        print(f"  {label:26s} EXTINCT"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    mx = sorted(r["maxcell"] for r in rs)
    print(f"  {label:26s} pop={mean('pop'):4.0f}  FINAL max/cell={mean('maxcell'):5.1f}[{mx[0]}-{mx[-1]}]  "
          f"%packed={mean('pct'):4.1f}%  occ={mean('occ'):4.0f}")


def main():
    print(f"BRANCH A — SEEDED proto-village persistence (400 agents seeded on a 2×2 block ~100/cell; {STEPS} steps)\n")
    print("  Does a PRE-FORMED village persist? (seed max/cell = 100)")
    run("baseline (aggl OFF)", aggl=False)
    for t2 in (10.0, 20.0, 50.0):
        run(f"point β=1.15 tier2={t2:g}", aggl=True, tier2=t2)
    run("point β=1.5 tier2=20", aggl=True, tier2=20.0, beta=1.5)


if __name__ == "__main__":
    main()
