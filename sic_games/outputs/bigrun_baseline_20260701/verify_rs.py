"""Verify status->RS with a BETTER estimator: total offspring per living male via the genealogy log (all births,
alive or dead), vs the alive-father estimator. Also the R-18 death-deficit (do low-status die first?)."""
import sys, os, math, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as iu
from collections import Counter
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

def corr(xs, ys):
    n = len(xs)
    if n < 3: return 0.0
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12) if dx*dy else 0.0

for seed in (0, 2, 6):
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
    males = [a for a in al if a.sex == "male"]
    # total logged offspring per father uid (all births ever, alive or dead)
    off = Counter(r[4] for r in w._genealogy_log if r[1] == "birth" and r[4] >= 0)   # r[4]=father_uid
    total_rs = corr([a.cred*getattr(a,"prowess",1.0) for a in males], [off.get(a.unique_id, 0) for a in males])
    # alive-father RS (the old estimator)
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        f = getattr(a, "_father", None)
        if f is not None and id(f) in ids: fc[id(f)] = fc.get(id(f), 0) + 1
    alive_rs = corr([a.cred*getattr(a,"prowess",1.0) for a in males], [fc.get(id(a),0) for a in males])
    print(f"seed {seed}: status->RS  total-offspring {total_rs:+.3f}  |  alive-father {alive_rs:+.3f}  "
          f"(pop {len(al)}, {len(off)} fathers logged)", flush=True)
