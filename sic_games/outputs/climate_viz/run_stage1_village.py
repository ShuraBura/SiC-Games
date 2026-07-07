"""Stage 1 (village-nucleation) — cost-benefit fission ceiling. band_split_size (45) is normally a HARD cap. This
turns on the dormant hierarchy (leader_coherence) + scalar-stress (size_repulsion) terms and the new supra-band
SCALING (net payoff above saturation adds village headroom past 45). The anthropological chain is already wired:
prime site -> point-superlinear surplus -> storage -> complexity MORPH -> leader weight unlocks (0 in egalitarian,
0.5 complex, 1.0 stratified) + scalar-stress relief -> net_raw>1 -> village. Measures max BAND size (does any band
exceed 45?), max/cell, %packed, and the society mix (confirming the morph->hierarchy->village chain).

Run:  py -3 -u outputs/climate_viz/run_stage1_village.py
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
_hf0 = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
_farm = [(x, y) for y in range(100) for x in range(100)
         if _hf0.level(x, y) > 0 and _f.isWater[y, x] == 0 and _cult[y, x] >= 0.5]
_zone = sorted(set((cx, cy) for (x, y) in _farm for dx in range(-2, 3) for dy in range(-2, 3)
                   for cx, cy in [((x + dx) % 100, (y + dy) % 100)]
                   if _hf0.level(cx, cy) > 0 and _f.isWater[cy, cx] == 0))
_bx, _by = max(_farm, key=lambda c: _hf0.level(*c))
_block = [((_bx + dx) % 100, (_by + dy) % 100) for dx in range(-1, 2) for dy in range(-1, 2)]  # 3×3 proto-village


def _one(seed, village, leader_g, rep_g, vg, tier2=5.0, seed_mode="spread"):
    hf = NPPCapacityField(_f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = ([_zone[i % len(_zone)] for i in range(FOUNDERS)] if seed_mode == "spread"
           else [_block[i % len(_block)] for i in range(FOUNDERS)])
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_agriculture=True, enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=tier2,
        comove_footprint=0, enable_forage_cap=True, forage_cap_hours=100.0,
        enable_leader_coherence=(leader_g > 0), leader_coherence_gain=leader_g,
        enable_size_repulsion=(rep_g > 0), repulsion_gain=rep_g,
        enable_village_scaling=village, village_gain=vg))
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
    bands = Counter(a._group.band_id for a in al)
    soc = getattr(w, "_band_society", {})
    complex_frac = sum(bands[b] for b in bands if soc.get(b) in ("complex_forager", "stratified_chiefdom")) / len(al)
    return dict(pop=len(al), maxcell=max(occ.values()), pct=100 * sum(packed.values()) / len(al),
               maxband=max(bands.values()), nbands=len(bands), cplx=100 * complex_frac)


def run(label, village=True, leader_g=0.0, rep_g=0.0, vg=0.0, seed_mode="spread"):
    rs = [r for s in SEEDS if (r := _one(s, village, leader_g, rep_g, vg, seed_mode=seed_mode)) is not None]
    if not rs:
        print(f"  {label:34s} EXTINCT"); return
    def mean(k): return sum(r[k] for r in rs) / len(rs)
    mb = sorted(r["maxband"] for r in rs)
    print(f"  {label:34s} pop={mean('pop'):4.0f}  MAXBAND={mean('maxband'):5.1f}[{mb[0]}-{mb[-1]}]  "
          f"max/cell={mean('maxcell'):4.1f}  %packed={mean('pct'):4.1f}%  #bands={mean('nbands'):3.0f}  %complex={mean('cplx'):4.0f}%")


def main():
    print(f"STAGE 1 — cost-benefit fission ceiling (mean over {len(SEEDS)} seeds, {STEPS} steps). MAXBAND>45 = village.\n")
    print("  [A] SPREAD seed (can villages assemble+grow?):")
    run("village OFF (hard cap 45)", village=False, leader_g=1.0, rep_g=0.3)
    run("village ON  L=1 R=0.3 vg=3", village=True, leader_g=1.0, rep_g=0.3, vg=3.0)
    run("village ON  L=2 R=0.3 vg=3", village=True, leader_g=2.0, rep_g=0.3, vg=3.0)
    run("village ON  L=2 R=0.3 vg=5", village=True, leader_g=2.0, rep_g=0.3, vg=5.0)
    run("village ON  L=2 R=0.5 vg=5", village=True, leader_g=2.0, rep_g=0.5, vg=5.0)
    print("\n  [B] BLOCK seed (isolate the CEILING: does a pre-formed village grow past 45?):")
    run("village OFF (hard cap 45)", village=False, leader_g=2.0, rep_g=0.3, seed_mode="block")
    run("village ON  L=2 R=0.3 vg=5", village=True, leader_g=2.0, rep_g=0.3, vg=5.0, seed_mode="block")


if __name__ == "__main__":
    main()
