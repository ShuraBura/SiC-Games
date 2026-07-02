"""Recalibration: does enable_ascribed_mate_choice lift cred->RS + the composite? Paired off-vs-on, same seeds,
16-seed genealogy total-offspring RS decomposition (cred / prowess / composite)."""
import sys, os, math, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
from collections import Counter
import importlib.util as iu
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

def corr(xs, ys):
    n = len(xs)
    if n < 3: return None
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx=math.sqrt(sum((x-mx)**2 for x in xs)); dy=math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12) if dx*dy else None

def run(seed, asc_on, a=2.0):
    demog = realistic_forager_demog().model_copy(update=dict(enable_genealogy_log=True,
        enable_ascribed_mate_choice=asc_on, ascribed_mate_strength=a))
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, 300)
    w = TerrainWorld(n_agents=300, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed), game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=base, placement_positions=pos, demography_cfg=demog)
    for _ in range(1500):
        w.step()
        if not w.agent_list: return None
    al = w.agent_list
    off = Counter(r[4] for r in w._genealogy_log if r[1]=="birth" and r[4]>=0)
    males = [a for a in al if a.sex=="male"]
    kids = [off.get(a.unique_id,0) for a in males]
    return dict(cred=corr([a.cred for a in males], kids),
                prow=corr([getattr(a,"prowess",1.0) for a in males], kids),
                comp=corr([a.cred*getattr(a,"prowess",1.0) for a in males], kids),
                gini=(lambda v: sum(abs(x-y) for x in v for y in v)/(2*len(v)*sum(v)) if sum(v) else 0)([a.cred for a in al]),
                pop=len(al))

def summ(vals):
    vals=[v for v in vals if v is not None]
    return (statistics.mean(vals), statistics.pstdev(vals)/math.sqrt(len(vals))) if len(vals)>1 else (float('nan'),0)

import time; t0=time.time()
res = {"off": {"cred":[],"prow":[],"comp":[],"gini":[]}, "on": {"cred":[],"prow":[],"comp":[],"gini":[]}}
for seed in range(16):
    for arm, on in (("off",False),("on",True)):
        r = run(seed, on)
        if r:
            for k in ("cred","prow","comp","gini"): res[arm][k].append(r[k])
    print(f"  seed {seed} done  [{time.time()-t0:.0f}s]", flush=True)
print("\n=== RS decomposition: OFF vs ON (ascribed_mate_strength=2.0, complex gate 0.5) ===")
for k in ("cred","prow","comp","gini"):
    mo,so = summ(res["off"][k]); mn,sn = summ(res["on"][k])
    print(f"  {k:<6} OFF {mo:+.3f}+/-{so:.3f}   ON {mn:+.3f}+/-{sn:.3f}   delta {mn-mo:+.3f}")
