"""R-84 challenge-succession: does a TENURED office produce ethnographic tenure, and does Boehm's
deposition(9):desertion(17) split come out the way it went in? Also: does the overreach loop bite —
i.e. does a greedier `leader_share_frac` shorten the tenure of the man taking it?"""
import sys, os, statistics
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def run(lf, lev, office, gain=1.0, dissolve=False, seed=0, steps=600, n=500):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    pos = [land[i % len(land)] for i in range(n)]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_capture_frac=0.0,
        material_decay=0.002, aggrandizer_frac=0.15,
        enable_leader_share=(lf > 0), leader_share_frac=lf,
        enable_leveling=lev, leveling_strength=(0.79 if lev else 0.0), leveling_share=(0.8 if lev else 0.0),
        enable_leader_office=office, office_grievance_gain=gain, succession_dissolve=dissolve))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=pos, demography_cfg=d)
    dep = des = chal = 0
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            return None
        dep += w.depositions_this_step
        des += w.desertions_this_step
        chal += w.challenges_this_step
    m = w.demography()
    t = w.leader_tenure()
    leaders = set(id(x) for x in w.band_leaders().values())
    al = [a for a in w.agent_list if a.age >= 15 * 12]
    ld = [a.material for a in al if id(a) in leaders]
    ot = [a.material for a in al if id(a) not in leaders]
    ratio = (statistics.mean(ld) / max(1e-9, statistics.mean(ot))) if ld and ot else float("nan")
    return dict(gini=m["material_gini"], ratio=ratio, top10=m["material_top10_share"],
                pop=len(w.agent_list), dep=dep, des=des, chal=chal, tenure_y=t["mean_years"],
                n_closed=t["n_closed"], vacant=t["vacant"], n_bands=t["n_bands"],
                fwl=t["father_was_leader"], n_scored=t["n_scored"], age=t["leader_age"],
                d_death=t["ends"]["death"], d_coll=t["ends"]["collision"], d_dep=t["ends"]["deposed"])


if __name__ == "__main__":
    print("R-84 CHALLENGE-SUCCESSION. Boehm 9:17 deposition:desertion is the ATTEMPT ratio (a challenge can fail).")
    print("gain=0 => tenure is ended by DEATH ALONE ('holds office until he dies') = the baseline to trim.")
    print("Hayden 1995 target: 75% of Big Men had Big Man fathers (EMERGENT here — office is not inherited).")
    print(f"\n{'share':>6} {'lev':>5} {'gain':>5} {'tenure_yr':>10} {'chal':>5} {'dep':>4} {'des':>5} "
          f"{'att.des%':>9} {'fath=ldr':>9} {'ldr_age':>8} {'gini':>6} {'ld/oth':>7} {'pop':>6}")
    print("-" * 96)
    for lf, lev, gain in ((0.2, True, 0.0), (0.2, True, 0.02), (0.2, True, 0.05), (0.2, True, 0.15),
                          (0.5, True, 0.05), (0.5, False, 0.05), (0.0, True, 0.05)):
        rs = [r for r in (run(lf, lev, True, gain, seed=s) for s in (0, 1)) if r]
        if not rs:
            continue
        a = lambda k: statistics.mean(r[k] for r in rs)
        att = a("chal") + a("des")
        print(f"{lf:6.2f} {str(lev):>5} {gain:5.2f} {a('tenure_y'):10.1f} {a('chal'):5.0f} {a('dep'):4.0f} "
              f"{a('des'):5.0f} {(a('des')/att*100 if att else 0):8.0f}% {a('fwl')*100:8.0f}% {a('age'):8.1f} "
              f"{a('gini'):6.3f} {a('ratio'):7.2f} {a('pop'):6.0f}")

    print("\nSAHLINS REGIMES (share=0.2, leveling on, gain=1.0): chiefly office vs big-man dissolution")
    for dis in (False, True):
        rs = [r for r in (run(0.2, True, True, 1.0, dissolve=dis, seed=s) for s in (0, 1)) if r]
        if not rs:
            continue
        a = lambda k: statistics.mean(r[k] for r in rs)
        print(f"  succession_dissolve={str(dis):5s}  tenure {a('tenure_y'):5.1f} yr   vacant {a('vacant'):4.0f}"
              f"/{a('n_bands'):3.0f} bands   gini {a('gini'):.3f}   ld/oth {a('ratio'):.2f}   pop {a('pop'):.0f}")
