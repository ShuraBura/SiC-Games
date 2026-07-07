"""Branch A — POINT-superlinear agglomeration (Bettencourt-correct). The cell's OWN intensive output scales
super-linearly with occupancy: O(n)=A_cell·n^β, so per-capita PREMIUM = A_cell·(n^(β-1)-1) RISES with co-location
(0 for a lone agent). A_cell = tier2·S_pot·cv_ref. Math (decomp3) predicts an emergent band→village TRANSITION as
the intensification multiple tier2 rises (peak n: 15 at tier2≤5 → carrying-capacity/village at tier2≥10). This run
tests whether the SIMULATION realizes that transition (packing + largest-settlement size), and locates the tier2/β
nucleation threshold. cap ON, GRP on, multi-seed.

Run:  py -3 -u outputs/climate_viz/run_agglomeration_pointA.py
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


def _one(aggl, beta, tier2, seed, cap_hours=100.0):
    hf = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    farm = [(x, y) for y in range(100) for x in range(100)
            if hf.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
    zone = sorted(set((cx, cy) for (x, y) in farm for dx in range(-2, 3) for dy in range(-2, 3)
                      for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                      if hf.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=aggl, aggl_mode="point", aggl_beta=beta,
        aggl_tier2=tier2, comove_footprint=0, enable_forage_cap=True, forage_cap_hours=cap_hours))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=_k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=demog)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    al = w.agent_list
    occ = Counter(a.pos for a in al)
    packed = {c: n for c, n in occ.items() if n >= 9}
    return dict(pop=len(al), maxcell=max(occ.values()), packed=len(packed),
               pct=100 * sum(packed.values()) / len(al), occ=len(occ))


def run(label, aggl=True, beta=1.15, tier2=5.0):
    rs = [_one(aggl, beta, tier2, s) for s in SEEDS]
    rs = [r for r in rs if r is not None]
    if not rs:
        print(f"  {label:30s} EXTINCT (all seeds)"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    pcts = sorted(r["pct"] for r in rs); mx = sorted(r["maxcell"] for r in rs)
    print(f"  {label:30s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}[{mx[0]}-{mx[-1]}]  "
          f"packed(≥9)={mean('packed'):4.1f}  %packed={mean('pct'):4.1f}% [{pcts[0]:.0f}-{pcts[-1]:.0f}]  occ={mean('occ'):4.0f}")


def main():
    print(f"BRANCH A — POINT-superlinear agglomeration (mean over {len(SEEDS)} seeds, {STEPS} steps)\n")
    print("  baseline (agglomeration OFF, cap+GRP only) for reference:")
    run("aggl OFF", aggl=False)
    print("\n  [A] tier2 sweep (β=1.15) — does the band→village transition realize? (math: >~10 ⇒ village):")
    for t2 in (2.0, 5.0, 8.0, 12.0, 20.0):
        run(f"point β=1.15 tier2={t2:g}", aggl=True, beta=1.15, tier2=t2)
    print("\n  [B] β sweep (tier2=5) — a stronger exponent lowers the nucleation threshold?:")
    for b in (1.15, 1.3, 1.5):
        run(f"point β={b:g} tier2=5", aggl=True, beta=b, tier2=5.0)


if __name__ == "__main__":
    main()
