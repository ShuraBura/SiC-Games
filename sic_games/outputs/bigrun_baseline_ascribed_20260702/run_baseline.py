"""BIG BASELINE RUN (2026-07-01) — canonical realistic forager on the PROVISIONAL CC-1 substrate (SubWindowCapacity,
static, no climate). The reference to compare the full Tallavaara CC-1 against. Model held fixed; only the capacity
field will change in the CC-1 rerun. Comprehensive metrics -> JSON.

Config: R-26 realistic (families + modest polygyny 0.3/cap3, prowess_decay 0.05, cred/paternity/lineage,
storage/morph, band affiliation + dynamic bands + assabiyah + family knobs). NEW Stage-1 flags OFF (leader/
repulsion/M2/F are exploratory). Genealogy observer ON (bit-exact). Static SubWindowCapacity.

Run:  py -3 -u outputs/bigrun_baseline_20260701/run_baseline.py
"""
import sys, os, json, math, statistics, time
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase1_social_evolution"))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world
import importlib.util as iu
_p = os.path.join(os.path.dirname(__file__), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = iu.spec_from_file_location("r2", _p); _r2 = iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

SEEDS = list(range(8))
FOUNDERS, STEPS, TAIL = 300, 2500, 800
SOC_TYPES = ("egalitarian_forager", "complex_forager", "stratified_chiefdom")

def corr(xs, ys):
    n = len(xs)
    if n < 3: return 0.0
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12) if dx*dy else 0.0

def gini(v):
    v = [x for x in v if x >= 0]
    if not v or sum(v) == 0: return 0.0
    return sum(abs(a-b) for a in v for b in v) / (2*len(v)*sum(v))

def make_world(seed):
    demog = realistic_forager_demog().model_copy(update=dict(enable_genealogy_log=True))
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, FOUNDERS)
    return TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
        game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=base, placement_positions=pos, demography_cfg=demog)

def run(seed):
    w = make_world(seed)
    pops, bands, nb = [], [], []
    starv, senesc, births = 0, 0, 0
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al: return dict(seed=seed, extinct=True, extinct_step=step)
        starv += w.deaths_starv_this_step; senesc += getattr(w, "deaths_senesc_this_step", 0); births += w.births_this_step
        if step >= STEPS - TAIL:
            pops.append(len(al))
            sz = Counter(a._group.band_id for a in al); tot = sum(sz.values())
            bands.append(sum(n*n for n in sz.values())/tot if tot else 0.0); nb.append(len(sz))
    al = w.agent_list
    males = [a for a in al if a.sex == "male"]
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        f = getattr(a, "_father", None)
        if f is not None and id(f) in ids: fc[id(f)] = fc.get(id(f), 0) + 1
    rs = corr([a.cred*getattr(a,"prowess",1.0) for a in males], [fc.get(id(a),0) for a in males])
    soc = Counter(w._band_society.get(b) for b in {a._group.band_id for a in al})
    n_soc = sum(soc.values()) or 1
    lineages = Counter(getattr(a, "_lineage", None) for a in al)
    return dict(seed=seed, extinct=False,
        eq_pop=statistics.mean(pops), pop_cv=statistics.pstdev(pops)/statistics.mean(pops) if statistics.mean(pops) else 0,
        band_awt=statistics.mean(bands), n_bands=statistics.mean(nb),
        mean_cred=statistics.mean(a.cred for a in al), cred_gini=gini([a.cred for a in al]),
        status_rs=rs, mean_assab=statistics.mean(w._band_assabiyah.values()) if w._band_assabiyah else 0.0,
        frac_egal=soc.get("egalitarian_forager",0)/n_soc, frac_complex=soc.get("complex_forager",0)/n_soc,
        frac_strat=soc.get("stratified_chiefdom",0)/n_soc,
        cum_starv=starv, cum_senesc=senesc, cum_births=births,
        n_lineages_alive=len(lineages), largest_lineage=max(lineages.values()) if lineages else 0,
        genea_records=len(w._genealogy_log) if w._genealogy_log else 0)

def main():
    t0 = time.time()
    rows = []
    for seed in SEEDS:
        r = run(seed); rows.append(r)
        tag = "EXTINCT@%d" % r.get("extinct_step", -1) if r.get("extinct") else \
              f"eq_pop {r['eq_pop']:.0f} | band {r['band_awt']:.1f} | RS {r['status_rs']:+.3f} | gini {r['cred_gini']:.2f}"
        print(f"  seed {seed}: {tag}   [{time.time()-t0:.0f}s]", flush=True)
    live = [r for r in rows if not r.get("extinct")]
    out = dict(config="CANONICAL (ascribed mate-choice a=2.5) + genealogy-ON, STATIC SubWindowCapacity (provisional CC-1)",
               founders=FOUNDERS, steps=STEPS, tail=TAIL, seeds=len(SEEDS), n_live=len(live), rows=rows)
    if live:
        m = lambda k: statistics.mean(r[k] for r in live)
        out["mean"] = {k: m(k) for k in ("eq_pop","pop_cv","band_awt","n_bands","mean_cred","cred_gini","status_rs",
                        "mean_assab","frac_egal","frac_complex","frac_strat","cum_starv","cum_senesc","cum_births",
                        "n_lineages_alive","largest_lineage")}
        print("\n=== BASELINE MEAN (%d live / %d seeds) ===" % (len(live), len(SEEDS)))
        for k, v in out["mean"].items(): print(f"  {k:<18}{v:>10.3f}")
    path = os.path.join(os.path.dirname(__file__), "baseline_results.json")
    with open(path, "w") as f: json.dump(out, f, indent=2)
    print(f"\nsaved -> {path}   [total {time.time()-t0:.0f}s]")

if __name__ == "__main__":
    main()
