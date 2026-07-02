"""Diagnose WHY cred->RS is negative. Per living male: cred, prowess, age, total offspring, band_id.
Compute pairwise + PARTIAL correlations (control for age / prowess) + between-band structure."""
import sys, os, math, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
from collections import Counter, defaultdict
import importlib.util as iu
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

def corr(xs, ys):
    n = len(xs)
    if n < 3: return 0.0
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12) if dx*dy else 0.0

def partial(x, y, z):  # r(x,y | z)
    rxy, rxz, ryz = corr(x,y), corr(x,z), corr(y,z)
    d = math.sqrt(max(1e-9,(1-rxz**2)*(1-ryz**2)))
    return (rxy - rxz*ryz)/d

agg = defaultdict(list)
for seed in (0, 2, 6, 14):   # incl. the strongly-negative-cred seeds
    demog = realistic_forager_demog().model_copy(update=dict(enable_genealogy_log=True))
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, 300)
    w = TerrainWorld(n_agents=300, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed), game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=base, placement_positions=pos, demography_cfg=demog)
    for _ in range(1500):
        w.step()
        if not w.agent_list: break
    al = w.agent_list
    off = Counter(r[4] for r in w._genealogy_log if r[1]=="birth" and r[4]>=0)
    males = [a for a in al if a.sex=="male" and a.age >= 200]  # past juvenile
    cred = [a.cred for a in males]; prow=[getattr(a,"prowess",1.0) for a in males]
    age=[a.age for a in males]; kids=[off.get(a.unique_id,0) for a in males]
    # between-band: mean cred vs mean offspring per band
    bc=defaultdict(list); bk=defaultdict(list)
    for a in males:
        bc[a._group.band_id].append(a.cred); bk[a._group.band_id].append(off.get(a.unique_id,0))
    bands=[b for b in bc if len(bc[b])>=2]
    bcred=[statistics.mean(bc[b]) for b in bands]; bkids=[statistics.mean(bk[b]) for b in bands]
    print(f"seed {seed} (n={len(males)} males, {len(bands)} bands):")
    print(f"   corr(cred,kids) {corr(cred,kids):+.3f} | corr(prow,kids) {corr(prow,kids):+.3f} | corr(cred,prow) {corr(cred,prow):+.3f}")
    print(f"   corr(cred,age) {corr(cred,age):+.3f} | corr(prow,age) {corr(prow,age):+.3f} | corr(age,kids) {corr(age,kids):+.3f}")
    print(f"   PARTIAL cred->kids | age {partial(cred,kids,age):+.3f} | prow {partial(cred,kids,prow):+.3f}")
    print(f"   BETWEEN-BAND corr(mean_cred, mean_kids) {corr(bcred,bkids):+.3f}", flush=True)
    agg['cred_kids'].append(corr(cred,kids)); agg['cred_age'].append(corr(cred,age))
    agg['cred_kids|age'].append(partial(cred,kids,age)); agg['cred_kids|prow'].append(partial(cred,kids,prow))
    agg['cred_prow'].append(corr(cred,prow)); agg['between_band'].append(corr(bcred,bkids))
print("\n=== MEANS across seeds ===")
for k,v in agg.items(): print(f"   {k:<16}{statistics.mean(v):+.3f}")
