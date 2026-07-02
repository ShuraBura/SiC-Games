"""BIOME -> SOCIETY experiment: does a biome-dominated world grow a society characteristic of that biome?
Runs the canonical model on the world-lottery ensemble (forest/savanna/desert/montane/mixed), on the FITTED
Tallavaara CC-1 substrate (so NPP->density->capacity varies by biome), and reports the emergent society per
archetype. Hypothesis (Binford/Kelly): productivity shapes density, band size, mobility, morph, and stratification.
"""
import sys, os, math, statistics
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery, WORLD_ARCHETYPE_ORDER
from sic_games.capacity import NPPCapacityField
import importlib.util as iu, time
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
BURN, X0, Y0, PATCH = _r2.BURN, _r2.X0, _r2.Y0, _r2.PATCH

FOUNDERS, STEPS, TAIL, SEEDS_PER = 220, 1300, 400, 5
from sic_games.terrain import N as GRID_N


def capacity_aware_seed(cap, burn, n, fill=0.7):
    """Seed founders at SUSTAINABLE density: patch cells (cap>0) by capacity desc, up to fill·(E/burn) per cell
    (min 1), so no cell is over-stacked. Fixes the founder-overcrowding collapse on low-NPP worlds (25/cell was
    lethal at 1.5–3.7 capacity)."""
    cells = sorted(((cap.level(x, y) / burn, x, y) for y in range(GRID_N) for x in range(GRID_N)
                    if cap.level(x, y) > 0.0), reverse=True)
    pos, rem = [], n
    for cpc, x, y in cells:
        k = min(rem, max(1, int(cpc * fill)))
        pos.extend([(x, y)] * k); rem -= k
        if rem <= 0:
            break
    return pos

def corr(xs, ys):
    n=len(xs)
    if n<3: return 0.0
    mx,my=sum(xs)/n,sum(ys)/n; num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx=math.sqrt(sum((x-mx)**2 for x in xs)); dy=math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12) if dx*dy else 0.0

def run(archetype, seed):
    knobs = world_lottery(seed*5, archetype=archetype)   # spread seeds; force the archetype
    fields = generate_world(knobs)
    cap = NPPCapacityField(fields, BURN, patch=(X0, Y0, PATCH), mode="tallavaara")
    pos = capacity_aware_seed(cap, BURN, FOUNDERS)
    if not pos: return None
    demog = realistic_forager_demog()
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs, game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    pops, bands = [], []
    starv, senesc = 0, 0
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al: return dict(archetype=archetype, extinct=True)
        starv += w.deaths_starv_this_step; senesc += getattr(w, "deaths_senesc_this_step", 0)
        if step >= STEPS - TAIL:
            pops.append(len(al))
            sz = Counter(a._group.band_id for a in al); tot = sum(sz.values())
            bands.append(sum(n*n for n in sz.values())/tot if tot else 0.0)
    al = w.agent_list
    males = [a for a in al if a.sex == "male"]
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        f = getattr(a, "_father", None)
        if f is not None and id(f) in ids: fc[id(f)] = fc.get(id(f), 0)+1
    rs = corr([a.cred*getattr(a,"prowess",1.0) for a in males], [fc.get(id(a),0) for a in males])
    soc = Counter(w._band_society.get(b) for b in {a._group.band_id for a in al}); nsoc = sum(soc.values()) or 1
    creds = [a.cred for a in al]
    gini = sum(abs(a-b) for a in creds for b in creds)/(2*len(creds)*sum(creds)) if sum(creds) else 0
    return dict(archetype=archetype, extinct=False, eq_pop=statistics.mean(pops), band=statistics.mean(bands),
        n_bands=statistics.mean([len(Counter(a._group.band_id for a in al))]),
        frac_complex=(soc.get("complex_forager",0)+soc.get("stratified_chiefdom",0))/nsoc,
        frac_egal=1.0-(soc.get("complex_forager",0)+soc.get("stratified_chiefdom",0))/nsoc,
        assab=statistics.mean(w._band_assabiyah.values()) if w._band_assabiyah else 0.0,
        rs=rs, gini=gini, starv_frac=starv/max(1,starv+senesc), cap=cap.ceiling)

def main():
    t0=time.time(); agg=defaultdict(list); ext=defaultdict(int)
    for arch in WORLD_ARCHETYPE_ORDER:
        for seed in range(SEEDS_PER):
            r = run(arch, seed)
            if r is None: continue
            if r.get("extinct"): ext[arch]+=1
            else: agg[arch].append(r)
        print(f"  {arch:<8} done ({len(agg[arch])} survived / {SEEDS_PER})  [{time.time()-t0:.0f}s]", flush=True)
    print(f"\n=== BIOME -> SOCIETY (Tallavaara CC-1, {SEEDS_PER} seeds/archetype, canonical config) ===")
    print(f"  {'archetype':<9}{'survive':>8}{'cap':>7}{'eq_pop':>8}{'density':>8}{'band':>7}{'%complex':>9}{'assab':>7}{'status_RS':>10}{'gini':>6}{'starv%':>7}")
    for arch in WORLD_ARCHETYPE_ORDER:
        rows=agg[arch]
        if not rows:
            print(f"  {arch:<9}{'0/'+str(SEEDS_PER):>8}  (all extinct)"); continue
        m=lambda k: statistics.mean(r[k] for r in rows)
        dens = m("eq_pop")/(PATCH*PATCH)   # persons per patch-cell (realized)
        print(f"  {arch:<9}{str(len(rows))+'/'+str(SEEDS_PER):>8}{m('cap'):>7.0f}{m('eq_pop'):>8.0f}{dens:>8.3f}{m('band'):>7.1f}{m('frac_complex')*100:>8.0f}%{m('assab'):>7.2f}{m('rs'):>+10.3f}{m('gini'):>6.2f}{m('starv_frac')*100:>6.0f}%")

if __name__ == "__main__":
    main()
