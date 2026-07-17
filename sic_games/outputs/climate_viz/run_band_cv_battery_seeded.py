"""Band-size environment-dependence: SEEDED biome battery (R-72 follow-up).

The 1-seed/world battery gave corr(g*, ON-OFF delta) = +0.374, n=18, n.s. — underpowered, not
necessarily null. Averaging each world over seeds kills the per-world draw noise; the ON-vs-OFF pairing
(same world, same seed) controls the biome-CV/productivity confound that inflates the raw across-world r.
"""
import sys, os
from collections import Counter
sys.path.insert(0,"sic_games/outputs/phase1_social_evolution"); sys.path.insert(0,"sic_games/outputs/biome_society_20260702")
from run_se0_controlled_climate import emergent_village_demog
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
import numpy as np, time

SEEDS = [0, 1, 2, 3]
STEPS = 200
names = {0:'water',1:'wetland',2:'forest',3:'savanna',4:'grass',5:'desert',6:'mountain'}
OUT = os.path.dirname(os.path.abspath(__file__))

def run(terr, clim, on, seed):
    k = world_lottery_climate(seed, terrain=terr, climate=clim); f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f,BURN,patch=(X0,Y0,PATCH),mode="tallavaara",aquatic=True,enable_depletion=True)
    land = [(x,y) for y in range(100) for x in range(100) if f.isWater[y,x]==0 and hf0.level(x,y)>0]
    if not land: return None
    pos = [land[i % len(land)] for i in range(800)]
    d = emergent_village_demog().model_copy(update=dict(enable_emergent_band_size=on))
    w = TerrainWorld(n_agents=800, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True,k_cell=0,movement_mode="diffusion",contest_exponent=1.5,move_cost_flat=0.0,**GRP),
        harvest_field=hf, placement_positions=pos, demography_cfg=d)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list: return None
    if len(w.agent_list) < 100: return None                   # degenerate/near-extinct → band pinned at floor
    s = list(Counter(a._group.band_id for a in w.agent_list).values())
    cvf = w._return_cv_field()
    mcv = float(np.median([cvf[a.pos[1],a.pos[0]] for a in w.agent_list])) if cvf is not None else float('nan')
    bio = Counter(names[int(f.biome[a.pos[1],a.pos[0]])] for a in w.agent_list).most_common(1)[0][0]
    return bio, mcv, len(w.agent_list), float(np.median(s))

def main():
    t0 = time.time(); prog = os.path.join(OUT, "progress_band_seeded.txt")
    rows = []
    for terr in ("flat","hilly","mountainous","coastal","alpine"):
        for clim in ("temperate","tropical","boreal","savanna"):
            per = []
            for sd in SEEDS:
                a = run(terr,clim,True,sd); b = run(terr,clim,False,sd)
                if a is None or b is None: continue
                per.append((a[1], a[3], b[3]))                # (med CV, band ON, band OFF)
            if not per: continue
            cv = float(np.mean([p[0] for p in per])); on = float(np.mean([p[1] for p in per]))
            off = float(np.mean([p[2] for p in per])); g = cv/0.037
            rows.append((f"{terr}/{clim}", cv, g, on, off, len(per)))
            print(f"  {terr+'/'+clim:22} CV {cv:.2f}  g* {g:5.1f}  band ON {on:5.1f}  OFF {off:5.1f}  "
                  f"(n_seeds {len(per)})  [{time.time()-t0:.0f}s]", flush=True)
            with open(prog,"w",encoding="utf-8") as fh:
                fh.write(f"{terr}/{clim} done | {len(rows)} worlds | {time.time()-t0:.0f}s\n")
    g = np.array([r[2] for r in rows]); on = np.array([r[3] for r in rows]); off = np.array([r[4] for r in rows])
    dl = on - off
    from math import sqrt
    def rep(name, x, y):
        r = np.corrcoef(x,y)[0,1]; n = len(x); t = r*sqrt((n-2)/(1-r*r))
        print(f"  {name:34} r={r:+.3f}  t={t:+.2f}  n={n}  {'SIGNIFICANT' if abs(t)>2.12 else 'not significant'}", flush=True)
    print(f"\n=== SEEDED ({len(SEEDS)} seeds/world, {len(rows)} worlds) ===", flush=True)
    rep("corr(g*, ON-OFF delta) [PAIRED]", g, dl)
    rep("corr(g*, band ON)     [confounded]", g, on)
    rep("corr(g*, band OFF)    [confound ref]", g, off)
    print(f"\n  g*>25 mean delta {dl[g>25].mean():+.2f} (n={int((g>25).sum())}) | g*<25 {dl[g<25].mean():+.2f} (n={int((g<25).sum())})", flush=True)
    print(f"  band ON  range {on.min():.1f}-{on.max():.1f} (spread {on.max()/on.min():.2f}x)", flush=True)
    print(f"  band OFF range {off.min():.1f}-{off.max():.1f} (spread {off.max()/off.min():.2f}x)", flush=True)

main()
