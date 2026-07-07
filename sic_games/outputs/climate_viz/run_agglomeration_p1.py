"""Agglomeration P1 — CLEAN multi-seed harness (post bug-fix 2026-07).

Fundamentals check after fixing: (1) R mis-scale (level-kcal mistaken for a 0-1 fraction → R≈54M defeated the cap;
now R = tier2·Σ(S_pot·cv_ref) ≈ few×cv); (2) the `cap` variable-shadowing bug that forced the forage cap ON in
every run; (3) band-scale `half`. Clean 2×2 {forage-cap off/on}×{agglomeration off/on} + a cap-hours sweep to test
the CARRYING-CAPACITY prediction (optimal group ≈ S/cv → lower cap ⇒ bigger villages). Multi-seed (mean over seeds)
to separate mechanism signal from stochastic divergence.

Run:  py -3 -u outputs/climate_viz/run_agglomeration_p1.py
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


def _one(aggl, cap, alpha, half, tier2, cap_hours, seed):
    hf = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    farm = [(x, y) for y in range(100) for x in range(100)
            if hf.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
    zone = sorted(set((cx, cy) for (x, y) in farm for dx in range(-2, 3) for dy in range(-2, 3)
                      for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                      if hf.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
    pos = [zone[i % len(zone)] for i in range(FOUNDERS)]
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=aggl, aggl_alpha=alpha, aggl_half=half,
        aggl_tier2=tier2, aggl_catchment_radius=1, comove_footprint=0,       # families STACK (not 3×3 scatter)
        enable_forage_cap=cap, forage_cap_hours=cap_hours))                  # `cap` is a REAL bool now (no shadow)
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
    packed = {c: n for c, n in occ.items() if n >= 9}      # ≥9/cell = Binford 0.091/km²
    return dict(pop=len(al), maxcell=max(occ.values()), packed=len(packed),
               pct=100 * sum(packed.values()) / len(al), occ=len(occ))


def run(label, aggl=False, cap=False, alpha=1.5, half=50.0, tier2=2.0, cap_hours=100.0):
    rs = [_one(aggl, cap, alpha, half, tier2, cap_hours, s) for s in SEEDS]
    rs = [r for r in rs if r is not None]
    if not rs:
        print(f"  {label:34s} EXTINCT (all seeds)"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    pcts = sorted(r["pct"] for r in rs)
    print(f"  {label:34s} pop={mean('pop'):4.0f}  max/cell={mean('maxcell'):4.1f}  "
          f"packed(≥9)={mean('packed'):4.1f}  %packed={mean('pct'):4.1f}% [{pcts[0]:.0f}-{pcts[-1]:.0f}]  "
          f"occ={mean('occ'):4.0f}")


def main():
    print(f"AGGLOMERATION P1 — CLEAN 2×2 + carrying-capacity sweep (mean over {len(SEEDS)} seeds, {STEPS} steps)\n")
    print("  [A] clean 2×2  {forage-cap}×{agglomeration}  (half=50, tier2=2):")
    run("cap OFF, aggl OFF (pure IFD+GRP)", aggl=False, cap=False)
    run("cap OFF, aggl ON", aggl=True, cap=False)
    run("cap ON,  aggl OFF", aggl=False, cap=True)
    run("cap ON,  aggl ON", aggl=True, cap=True)
    print("\n  [B] carrying-capacity: cap-hours sweep (aggl OFF) — lower cap ⇒ bigger villages? (opt≈S/cv):")
    for ch in (50.0, 100.0, 200.0):
        run(f"cap ON h={ch:g} (cv≈forage·{ch:g})", aggl=False, cap=True, cap_hours=ch)
    print("\n  [C] can agglomeration add village scale? tier2 sweep (cap ON h=100, half=50):")
    for t2 in (2.0, 5.0, 10.0):
        run(f"cap ON, aggl ON tier2={t2:g}", aggl=True, cap=True, tier2=t2, cap_hours=100.0)


if __name__ == "__main__":
    main()
