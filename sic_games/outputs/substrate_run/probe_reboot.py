"""Is the founder boom a STARTUP ARTIFACT or a reproducible dynamic? And are post-crash agents mobile?
Run the m*=25 Cut-2 config to the plateau, measuring per-step MOBILITY (fraction of agents that changed cell)
in a founder-growth window vs a plateau window. Then at KILL_STEP remove KILL_FRAC of the population (create
growth headroom on the already-worked landscape) and watch whether it RE-BOOMS. If it re-booms → the boom is a
generic below-capacity response (founder condition not privileged; cycles just need a recurring knock-down). If it
just re-glides to the flat plateau → the pristine-landscape overshoot was the special ingredient (startup artifact).

Run:  py -3 -u sic_games/outputs/substrate_run/probe_reboot.py    (from repo root)
Env:  KILL_STEP 10000 | END_STEP 18000 | KILL_FRAC 0.5 | SEED 0
"""
import sys, os, time, json, random
from collections import Counter

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(HERE, "..", "biome_society_20260702"))
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from run_se0_controlled_climate import emergent_village_demog
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField

KILL = int(os.environ.get("KILL_STEP", "10000"))
END  = int(os.environ.get("END_STEP", "18000"))
KILL_FRAC = float(os.environ.get("KILL_FRAC", "0.5"))
SEED = int(os.environ.get("SEED", "0"))
BAND_SPLIT = 45
TAG = os.environ.get("RTAG", "")
PROG = os.path.join(HERE, f"reboot_progress{TAG}.txt")
OUT  = os.path.join(HERE, f"reboot_traj{TAG}.json")


def log(m):
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(m + "\n"); fh.flush()
    print(m, flush=True)


def main():
    open(PROG, "w").close()
    k = world_lottery_climate(SEED, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base.level(x, y) > 0]
    cap = ClimateField(base, a_seas=0.4, regime_driver=None)
    pos = [land[i % len(land)] for i in range(3000)]
    cut2 = os.environ.get("CONNUBIUM", "cut2") == "cut2"
    demog = emergent_village_demog().model_copy(update=dict(
        enable_landscape_packing=True, enable_sedentism_fertility=True,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
        enable_catchment_ceiling=True, enable_settlement_scalar_stress=True, settle_catchment_radius=1,
        enable_adaptive_connubium=cut2, mate_search_min_eligible=(25 if cut2 else 3),
        enable_exogamy=cut2, exogamy_degree="lineage", enable_genome=False, enable_genealogy_log=False))
    w = TerrainWorld(n_agents=3000, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=SEED,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    log(f"reboot probe: seed={SEED} kill {KILL_FRAC:.0%} @ step {KILL}, run to {END}. "
        f"Q: does removing pop re-boom (generic) or re-glide flat (startup artifact)?")
    prev = {}
    def mobility():
        al = w.agent_list
        if not al:
            return 0.0
        mv = sum(1 for a in al if prev.get(a.unique_id, a.pos) != a.pos)
        for a in al:
            prev[a.unique_id] = a.pos
        return mv / len(al)

    traj = []
    win = []          # accumulate mobility between logs
    killed = False
    t0 = time.time()
    for step in range(1, END + 1):
        w.step()
        win.append(mobility())
        if step == KILL and not killed:
            al = w.agent_list
            keep = set(id(a) for a in random.Random(SEED).sample(al, int(len(al) * (1 - KILL_FRAC))))
            n0 = len(al)
            for a in al:
                if id(a) not in keep:
                    a.alive = False
            killed = True
            log(f"  [{step}] KILLED {KILL_FRAC:.0%}: {n0} -> ~{len(keep)} (headroom created; landscape already worked)")
        if step % 250 == 0 or step == 1:
            al = w.agent_list
            pop = len(al)
            if not pop:
                log(f"  [{step}] EXTINCT"); break
            sizes = Counter(a._group.band_id for a in al)
            vil = sum(1 for n in sizes.values() if n > BAND_SPLIT)
            mob = round(sum(win) / len(win), 3) if win else 0.0
            win = []
            occ = len(set(a.pos for a in al))
            row = dict(step=step, pop=pop, vil=vil, mobility=mob, occ=occ, phase="post-kill" if killed else "pre-kill")
            traj.append(row)
            json.dump(traj, open(OUT, "w"))
            if step % 1000 == 0 or step == 1 or (killed and step <= KILL + 1000):
                log(f"  [{step:5d}] pop={pop:6d} vil={vil:3d} mobility={mob:.3f} occ={occ} {'POST-KILL' if killed else ''} "
                    f"| {(time.time()-t0)/60:.1f}m")
    log(f"DONE {(time.time()-t0)/60:.1f}m -> {OUT}")


if __name__ == "__main__":
    main()
