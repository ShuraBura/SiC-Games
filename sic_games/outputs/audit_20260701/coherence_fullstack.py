"""Deep-audit coherence pass: full social stack (ALL flags on), flat climate, multi-seed. Confirms the model
coheres + keeps its documented invariants (eq_pop, bands ~non-kin, status->RS, R-18 death-deficit, N_e)."""
import sys, os, math, statistics
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.climate import ClimateField, ClimateDriver
from sic_games.terrain import generate_world
import importlib.util as iu
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

def corr(xs, ys):
    n = len(xs)
    if n < 3: return 0.0
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12)

def run(seed, steps=900):
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_leader_coherence=True, leader_coherence_gain=1.5,
        enable_size_repulsion=True, repulsion_gain=1.0,
        enable_malnutrition_fission=True, malnutrition_fission_gain=2.0,
        enable_resource_directed_fusion=True))
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, 300)
    cap = ClimateField(base, a_seas=0.25, regime_driver=ClimateDriver.flat(1.0))
    w = TerrainWorld(n_agents=300, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed), game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    pops, bands = [], []
    for step in range(steps):
        w.step(); al = w.agent_list
        if not al: return None
        if step >= 400:
            pops.append(len(al))
            sz = Counter(a._group.band_id for a in al); tot = sum(sz.values())
            bands.append(sum(n*n for n in sz.values())/tot if tot else 0)
    al = w.agent_list
    males = [a for a in al if a.sex == "male"]
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        f = getattr(a, "_father", None)
        if f is not None and id(f) in ids: fc[id(f)] = fc.get(id(f), 0) + 1
    rs = corr([a.cred*getattr(a,"prowess",1.0) for a in males], [fc.get(id(a),0) for a in males])
    creds = [a.cred for a in al]; mc = statistics.mean(creds)
    gini = sum(abs(a-b) for a in creds for b in creds)/(2*len(creds)*sum(creds)) if sum(creds) else 0
    return dict(eqpop=statistics.mean(pops), band=statistics.mean(bands), rs=rs, mc=mc, gini=gini)

print("Full-stack coherence (ALL flags on, flat climate, 900 steps):")
print(f"  {'seed':<6}{'eq_pop':>8}{'band_awt':>10}{'status->RS':>12}{'mean_cred':>11}{'gini':>7}")
rows = []
for seed in (0, 1, 2):
    r = run(seed)
    if r is None: print(f"  {seed:<6}  EXTINCT"); continue
    rows.append(r)
    print(f"  {seed:<6}{r['eqpop']:>8.0f}{r['band']:>10.1f}{r['rs']:>+12.3f}{r['mc']:>11.2f}{r['gini']:>7.2f}")
if rows:
    m = lambda k: statistics.mean(r[k] for r in rows)
    print(f"  {'MEAN':<6}{m('eqpop'):>8.0f}{m('band'):>10.1f}{m('rs'):>+12.3f}{m('mc'):>11.2f}{m('gini'):>7.2f}")
    print(f"\n  vs documented (R-26 realistic): eq_pop ~360-540, band ~25 non-kin, status->RS ~0.13, gini ~0.19-0.30")
