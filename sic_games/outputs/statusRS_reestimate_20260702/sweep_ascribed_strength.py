"""Pin ascribed_mate_strength: sweep a so the composite status->RS lands near the von-Rueden ~0.13 (measured at
the complex point, the only society type present; the stratified point is implied by the gate ratio, validated
later). 10 seeds/value, genealogy total-offspring composite RS."""
import sys, os, math, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
from collections import Counter
import importlib.util as iu, time
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for
def corr(xs, ys):
    n=len(xs)
    if n<3: return None
    mx,my=sum(xs)/n,sum(ys)/n; num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx=math.sqrt(sum((x-mx)**2 for x in xs)); dy=math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12) if dx*dy else None
def run(seed, a):
    demog = realistic_forager_demog().model_copy(update=dict(enable_genealogy_log=True,
        enable_ascribed_mate_choice=(a>0), ascribed_mate_strength=a))
    fields=generate_world(knobs_for(seed)); base=SubWindowCapacity(fields); pos=band_positions_patch(fields,base,300)
    w=TerrainWorld(n_agents=300, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed), game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0,**GRP),
        harvest_field=base, placement_positions=pos, demography_cfg=demog)
    for _ in range(1500):
        w.step()
        if not w.agent_list: return None
    al=w.agent_list; off=Counter(r[4] for r in w._genealogy_log if r[1]=="birth" and r[4]>=0)
    males=[x for x in al if x.sex=="male"]; kids=[off.get(x.unique_id,0) for x in males]
    g=[x.cred for x in al]; gini=sum(abs(p-q) for p in g for q in g)/(2*len(g)*sum(g)) if sum(g) else 0
    return corr([x.cred*getattr(x,"prowess",1.0) for x in males], kids), gini
t0=time.time()
for a in (0.0, 2.5, 3.5, 4.5):
    comps=[]; ginis=[]
    for seed in range(10):
        r=run(seed,a)
        if r: comps.append(r[0]); ginis.append(r[1])
    comps=[c for c in comps if c is not None]
    m=statistics.mean(comps); se=statistics.pstdev(comps)/math.sqrt(len(comps))
    print(f"  a={a:<4} composite->RS {m:+.3f} +/- {se:.3f}   cred_gini {statistics.mean(ginis):.3f}   [{time.time()-t0:.0f}s]", flush=True)
