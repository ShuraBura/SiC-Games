import sys, statistics
sys.path.insert(0,"sic_games/outputs/phase1_biome_mortality"); sys.path.insert(0,"sic_games/outputs/phase1_demography_step2")
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as _iu, os
_p = os.path.join("sic_games/outputs/phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for, patch_positions = _r2.SubWindowCapacity, _r2.knobs_for, _r2.patch_positions

FOUNDERS, STEPS = 400, 700

def run(on, seed):
    import random
    rng = random.Random(seed)
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = patch_positions(fields, FOUNDERS, rng)
    d = DemographyConfig(siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
                         enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
                         enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, divorce_rate=0.004,
                         enable_orphan_mortality=on)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=0.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=0.0, move_cost_flat=0.0),
                     harvest_field=cap, placement_positions=pos, demography_cfg=d)
    orph_deaths = 0
    pops = []
    for s in range(STEPS):
        w.step()
        orph_deaths += getattr(w, "deaths_orphan_this_step", 0)
        if s >= int(0.6*STEPS): pops.append(len(w.agent_list))
        if not w.agent_list: return None
    # measure realised parental status among live children
    kids = [a for a in w.agent_list if a.age <= 9*12]
    md = sum(1 for a in kids if getattr(a,"_mother",None) is not None and not a._mother.alive)
    fd = sum(1 for a in kids if getattr(a,"_father",None) is not None and not a._father.alive)
    return statistics.mean(pops), orph_deaths, len(kids), md, fd

print(f"{'arm':>6} {'eq_pop':>8} {'orphan-flagged deaths':>22} {'kids':>6} {'moth.dead':>10} {'fath.dead':>10}")
print('-'*70)
for on in (False, True):
    rs = [run(on, s) for s in range(4)]
    rs = [r for r in rs if r]
    ep = statistics.mean([r[0] for r in rs]); od = statistics.mean([r[1] for r in rs])
    kd = statistics.mean([r[2] for r in rs]); md = statistics.mean([r[3] for r in rs]); fd = statistics.mean([r[4] for r in rs])
    mdf = md/kd if kd else 0; fdf = fd/kd if kd else 0
    print(f"{'ON' if on else 'OFF':>6} {ep:8.0f} {od:22.0f} {kd:6.0f} {mdf*100:9.1f}% {fdf*100:9.1f}%")
print()
print("Ache Table 13.1 mean values: mother dead 2.0%, father dead 5.0% of child risk-intervals")
