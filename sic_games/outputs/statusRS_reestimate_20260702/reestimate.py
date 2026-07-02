"""High-seed status->RS re-estimation (2026-07-02). Pin the von-Rueden calibration (documented 0.13, R-26) with
~16 seeds on the STATIC substrate + R-26 realistic config. Uses the genealogy total-offspring estimator (better
than alive-father). Decomposes: full status (cred*prowess), prime-age-only (age-bias control), cred-only,
prowess-only. Reports the DISTRIBUTION (mean, sd, SE, 95% CI) so the true mean + spread are known."""
import sys, os, json, math, statistics
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

SEEDS = list(range(16))
STEPS = 1500

def corr(xs, ys):
    n = len(xs)
    if n < 3: return None
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy+1e-12) if dx*dy else None

def run(seed):
    demog = realistic_forager_demog().model_copy(update=dict(enable_genealogy_log=True))
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, 300)
    w = TerrainWorld(n_agents=300, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed), game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=base, placement_positions=pos, demography_cfg=demog)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list: return None
    al = w.agent_list
    off = Counter(r[4] for r in w._genealogy_log if r[1] == "birth" and r[4] >= 0)   # total offspring per father uid
    males = [a for a in al if a.sex == "male"]
    def rs(subset, statfn):
        ms = [a for a in males if subset(a)]
        return corr([statfn(a) for a in ms], [off.get(a.unique_id, 0) for a in ms])
    st = lambda a: a.cred * getattr(a, "prowess", 1.0)
    prime = lambda a: 240 <= a.age <= 540   # 20-45 yr in months
    return dict(seed=seed, pop=len(al),
                rs_full=rs(lambda a: True, st), rs_prime=rs(prime, st),
                rs_cred=rs(lambda a: True, lambda a: a.cred),
                rs_prowess=rs(lambda a: True, lambda a: getattr(a, "prowess", 1.0)))

def summ(vals):
    vals = [v for v in vals if v is not None]
    if len(vals) < 2: return {}
    m, sd = statistics.mean(vals), statistics.pstdev(vals)
    se = sd / math.sqrt(len(vals))
    return dict(n=len(vals), mean=round(m,3), sd=round(sd,3), se=round(se,3),
                ci95=[round(m-1.96*se,3), round(m+1.96*se,3)], min=round(min(vals),3), max=round(max(vals),3))

def main():
    import time; t0 = time.time()
    rows = []
    for seed in SEEDS:
        r = run(seed)
        if r is None: print(f"  seed {seed}: EXTINCT", flush=True); continue
        rows.append(r)
        print(f"  seed {seed}: RS_full {r['rs_full']:+.3f}  prime {r['rs_prime']:+.3f}  "
              f"cred {r['rs_cred']:+.3f}  prowess {r['rs_prowess']:+.3f}  (pop {r['pop']})  [{time.time()-t0:.0f}s]", flush=True)
    out = {"config": "R-26 realistic, static, genealogy total-offspring RS", "steps": STEPS, "n_seeds": len(SEEDS),
           "rs_full": summ([r["rs_full"] for r in rows]), "rs_prime": summ([r["rs_prime"] for r in rows]),
           "rs_cred": summ([r["rs_cred"] for r in rows]), "rs_prowess": summ([r["rs_prowess"] for r in rows]), "rows": rows}
    print("\n=== status->RS DISTRIBUTION (%d live seeds) ===" % len(rows))
    for k in ("rs_full", "rs_prime", "rs_cred", "rs_prowess"):
        s = out[k]
        print(f"  {k:<11} mean {s['mean']:+.3f} +/- {s['se']:.3f} (SE)  95%CI [{s['ci95'][0]:+.3f},{s['ci95'][1]:+.3f}]  range [{s['min']:+.3f},{s['max']:+.3f}]")
    print(f"\n  vs documented 0.13 (R-26). Is 0.13 inside the CI?")
    with open(os.path.join(os.path.dirname(__file__), "reestimate_results.json"), "w") as f: json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
