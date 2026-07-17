import sys, statistics, os
sys.path.insert(0,"sic_games/outputs/phase1_demography_step2")
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu
_p = os.path.join("sic_games/outputs/phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions
FOUNDERS, STEPS = 400, 700

def run(delta, orph, seed):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    d = DemographyConfig(siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=(delta > 0), dens_delta=delta, dens_rho_half=0.2,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, divorce_rate=0.004,
                         enable_orphan_mortality=orph)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos, demography_cfg=d)
    # accumulate EXPOSURE (child-months) the way Table 13.1's mean value is defined
    exp_tot = exp_md = exp_fd = 0
    pops = []
    for s in range(STEPS):
        w.step()
        if not w.agent_list: return None
        if s >= int(0.5*STEPS):
            for a in w.agent_list:
                if a.age > 9*12: continue
                m = getattr(a,"_mother",None); f = getattr(a,"_father",None)
                if m is None and f is None: continue          # founders: unknown parentage
                exp_tot += 1
                if m is not None and not m.alive: exp_md += 1
                if f is not None and not f.alive: exp_fd += 1
            pops.append(len(w.agent_list))
    if not exp_tot: return None
    return statistics.mean(pops), exp_md/exp_tot, exp_fd/exp_tot

print(f"{'dens_delta':>10} {'orphan':>7} {'eq_pop':>8} {'motherless':>11} {'fatherless':>11}")
print('-'*54)
for delta in (0.0, 1.0, 3.0):
    for orph in (False, True):
        rs = [run(delta, orph, s) for s in range(3)]
        rs = [r for r in rs if r]
        if not rs: print(f"{delta:10.1f} {str(orph):>7}  extinct"); continue
        print(f"{delta:10.1f} {str(orph):>7} {statistics.mean([r[0] for r in rs]):8.0f} "
              f"{statistics.mean([r[1] for r in rs])*100:10.1f}% {statistics.mean([r[2] for r in rs])*100:10.1f}%")
print()
print("Ache Table 13.1 (EXPOSURE-weighted, post-selection): motherless 2.0%, fatherless 5.0%")
