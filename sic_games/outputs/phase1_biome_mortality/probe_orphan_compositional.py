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

def run(orph, seed, steps=700):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, 400, rng)
    d = DemographyConfig(siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, divorce_rate=0.004, enable_orphan_mortality=orph)
    w = TerrainWorld(n_agents=400, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos, demography_cfg=d)
    pops=[]; e_mults=[]
    exp_tot=exp_md=0
    for s in range(steps):
        w.step()
        if not w.agent_list: return None
        if s >= int(0.5*steps):
            pops.append(len(w.agent_list))
            if orph: e_mults.append(w._orphan_e_mult_live())
            for a in w.agent_list:
                if a.age > 9*12: continue
                m=getattr(a,"_mother",None); f=getattr(a,"_father",None)
                if m is None and f is None: continue
                exp_tot += 1
                if m is not None and not m.alive: exp_md += 1
    return statistics.mean(pops), (statistics.mean(e_mults) if e_mults else float('nan')), (exp_md/exp_tot if exp_tot else 0)

print(f"{'arm':>5} {'eq_pop':>8} {'E[mult] live':>13} {'motherless':>11}")
print('-'*42)
res={}
for orph in (False, True):
    rs=[run(orph,s) for s in range(3)]; rs=[r for r in rs if r]
    ep=statistics.mean([r[0] for r in rs]); em=statistics.mean([r[1] for r in rs]); ml=statistics.mean([r[2] for r in rs])
    res[orph]=ep
    print(f"{'ON' if orph else 'OFF':>5} {ep:8.0f} {em:13.2f} {ml*100:10.1f}%")
print()
d = 100*(res[True]-res[False])/res[False]
print(f"eq_pop change ON vs OFF: {d:+.1f}%   (was -47% with the fixed Ache normaliser)")
print("compositional => eq_pop ~unchanged (how many is fertility-pinned, R-16); only WHO dies shifts")
