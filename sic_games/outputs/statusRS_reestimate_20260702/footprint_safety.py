"""Pre-canonicalization safety check (R-43 gate): does comove_footprint=1 preserve status->RS (~0.13, E.3/R-26)
and the full-stack equilibrium? Runs the reestimate estimator with footprint 0 (baseline) vs 1, on the STATIC
substrate + realistic config. If rs_full stays ~0.13 and pop stays healthy, footprint=1 is safe to canonicalize."""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(__file__))
import reestimate as RE

SEEDS = list(range(6))

def run(seed, fp):
    demog = RE.realistic_forager_demog().model_copy(update=dict(enable_genealogy_log=True, comove_footprint=fp))
    fields = RE.generate_world(RE.knobs_for(seed)); base = RE.SubWindowCapacity(fields)
    pos = RE.band_positions_patch(fields, base, 300)
    from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
    from sic_games.phase1_model import TerrainWorld
    from collections import Counter
    w = TerrainWorld(n_agents=300, kcal_cfg=KcalEconomyConfig(), terrain_knobs=RE.knobs_for(seed), game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **RE.GRP),
        harvest_field=base, placement_positions=pos, demography_cfg=demog)
    for _ in range(RE.STEPS):
        w.step()
        if not w.agent_list: return None
    al = w.agent_list
    off = Counter(r[4] for r in w._genealogy_log if r[1] == "birth" and r[4] >= 0)
    males = [a for a in al if a.sex == "male"]
    st = lambda a: a.cred * getattr(a, "prowess", 1.0)
    rs = RE.corr([st(a) for a in males], [off.get(a.unique_id, 0) for a in males])
    return dict(pop=len(al), rs=rs)

def main():
    print(f"footprint safety — status->RS + pop, {len(SEEDS)} seeds x {RE.STEPS} steps (static substrate, realistic config)\n")
    for fp in (0, 1):
        rows = [run(s, fp) for s in SEEDS]
        rows = [r for r in rows if r]
        rss = [r["rs"] for r in rows if r["rs"] is not None]
        pops = [r["pop"] for r in rows]
        m = statistics.mean(rss); se = statistics.pstdev(rss)/math.sqrt(len(rss))
        print(f"  footprint={fp}:  status->RS mean={m:+.3f}  [95% CI {m-1.96*se:+.3f},{m+1.96*se:+.3f}]  "
              f"eq_pop mean={statistics.mean(pops):.0f}  (n={len(rows)})")
    print("\n  Safe to canonicalize if footprint=1 rs stays ~0.13 (overlapping CI) and pop stays healthy.")

if __name__ == "__main__":
    main()
