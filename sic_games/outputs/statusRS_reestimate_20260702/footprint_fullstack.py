"""Fuller pre-canonicalization check (R-44 gate ext): does comove_footprint=1 preserve the FULL-STACK shape results
(R-25/R-26) beyond status->RS? Compares footprint 0 vs 1 on the static substrate + realistic config over 6 seeds:
eq_pop, agent-wt band size, median band, mean cred, Gini, %complex, assabiyah, status->RS, dominant-lineage frac
(N_e proxy). A safe canonicalization keeps Gini ~0.2-0.28, band ~25 (Wobst), %complex, assabiyah, RS ~0.13 intact
(pop is EXPECTED to ~2x per R-44)."""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(__file__))
import reestimate as RE
from collections import Counter
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld

SEEDS = list(range(6))

def gini(xs):
    xs = [x for x in xs if x is not None]
    s = sum(xs)
    if s <= 0 or len(xs) < 2: return 0.0
    return sum(abs(a-b) for a in xs for b in xs) / (2*len(xs)*s)

def run(seed, fp):
    demog = RE.realistic_forager_demog().model_copy(update=dict(enable_genealogy_log=True, comove_footprint=fp))
    fields = RE.generate_world(RE.knobs_for(seed)); base = RE.SubWindowCapacity(fields)
    pos = RE.band_positions_patch(fields, base, 300)
    w = TerrainWorld(n_agents=300, kcal_cfg=KcalEconomyConfig(), terrain_knobs=RE.knobs_for(seed), game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **RE.GRP),
        harvest_field=base, placement_positions=pos, demography_cfg=demog)
    for _ in range(RE.STEPS):
        w.step()
        if not w.agent_list: return None
    al = w.agent_list
    sz = Counter(a._group.band_id for a in al); tot = sum(sz.values())
    awt = sum(n*n for n in sz.values())/tot if tot else 0.0
    med = statistics.median(sz.values()) if sz else 0
    off = Counter(r[4] for r in w._genealogy_log if r[1] == "birth" and r[4] >= 0)
    males = [a for a in al if a.sex == "male"]
    st = lambda a: a.cred * getattr(a, "prowess", 1.0)
    rs = RE.corr([st(a) for a in males], [off.get(a.unique_id, 0) for a in males])
    soc = Counter(w._band_society.get(b) for b in sz); nsoc = sum(soc.values()) or 1
    pctc = (soc.get("complex_forager",0)+soc.get("stratified_chiefdom",0))/nsoc
    lin = Counter(getattr(a, "lineage", None) for a in al); domlin = max(lin.values())/len(al) if al else 0
    assab = statistics.mean(w._band_assabiyah.values()) if w._band_assabiyah else 0.0
    return dict(pop=len(al), awt=awt, med=med, cred=statistics.mean(a.cred for a in al),
                gini=gini([a.cred for a in al]), pctc=pctc, assab=assab, rs=rs, domlin=domlin)

def main():
    print(f"footprint full-stack check — {len(SEEDS)} seeds x {RE.STEPS} steps (static substrate, realistic config)\n")
    print(f"  {'fp':>3}{'pop':>7}{'band_awt':>9}{'band_med':>9}{'cred':>6}{'gini':>6}{'%cplx':>7}{'assab':>7}{'status_RS':>10}{'domlin':>8}")
    for fp in (0, 1):
        rows = [r for r in (run(s, fp) for s in SEEDS) if r]
        m = lambda k: statistics.mean(r[k] for r in rows if r[k] is not None)
        print(f"  {fp:>3}{m('pop'):>7.0f}{m('awt'):>9.1f}{m('med'):>9.1f}{m('cred'):>6.2f}{m('gini'):>6.2f}"
              f"{m('pctc')*100:>6.0f}%{m('assab'):>7.2f}{m('rs'):>+10.3f}{m('domlin'):>8.2f}")

if __name__ == "__main__":
    main()
