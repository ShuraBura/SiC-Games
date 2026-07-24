"""R-103h — DIVERSE-WORLD DIAGNOSTIC SWEEP (overnight, current validated machinery).

TWO jobs, both from R-103g's reframe (the elite lives in PEOPLE, not goods):
  1. ROBUSTNESS — does the wealth-in-people aristocracy (noble_lineage_size_lift ~2.9, lineage_size_gini ~0.50,
     goods lifts ~1.0) replicate across biomes, or is it a coastal-tropical artifact?
  2. BIOME FORK (Nieboer-Domar first look) — does the GOODS axis wake up where land is worked/ownable? Each world
     is run in a matched pair: FORAGE (improved_land OFF, open resources) vs AGRI (improved_land ON, land becomes
     a claimable estate). Prediction: people-elite everywhere; goods-lift only (if ever) in the AGRI arm.
And it doubles as the user's "run diverse worlds and see what floats up" — live invariant checks + extinction/
anomaly watching over a deep horizon on the current committed stack (R-89...R-101; the R-103 GOODS mechanisms OFF,
since R-103g deferred them to the circumscribed arm).

Safe to run unsupervised: validated machinery (912 tests, bit-exact), sleep-aware compute budget per arm, progress
flushed every LOGEVERY, cheapest world first so the morning has finished arms whatever the tropics do.
"""
import os, subprocess, sys, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# viable worlds only (mountainous-boreal went extinct in R-102 — excluded), marginal -> rich
WORLDS = [
    ("hilly", "temperate"),       # leanest viable — cheapest
    ("coastal", "temperate"),     # the R-64 validated baseline
    ("coastal", "tropical"),      # rich aquatic
    ("flat", "tropical"),         # rich agrarian (explodes -> budget-capped)
]
ARMS = [("forage", "0"), ("agri", "1")]          # improved_land OFF vs ON (the open vs worked-land axis)

STEPS = os.environ.get("DIAG_STEPS", "15000")
FOUNDERS = os.environ.get("DIAG_FOUNDERS", "3000")
MAXMIN = os.environ.get("DIAG_MAXMIN", "40")     # per arm; 8 arms x 40 = 5.3h worst case

# the CURRENT validated elite stack (R-89...R-101). R-103 GOODS mechanisms (tribute/inherit/exempt) left OFF.
STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal", C_DEFEND="1")

PROG = os.path.join(HERE, "diag_progress.txt")


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


if __name__ == "__main__":
    open(PROG, "w").close()
    jobs = [(t, c, an, av) for (t, c) in WORLDS for (an, av) in ARMS]
    log(f"R-103h diverse-world diagnostic: {len(jobs)} arms x {STEPS} steps (budget {MAXMIN}m/arm)")
    t0 = time.time()
    done = []
    for i, (terr, clim, an, imp) in enumerate(jobs, 1):
        tag = f"_diag_{terr}_{clim}_{an}"
        env = dict(os.environ, C_TAG=tag, C_TERR=terr, C_CLIM=clim, C_STEPS=STEPS, C_FOUNDERS=FOUNDERS,
                   C_MAXMIN=MAXMIN, C_IMPROVED=imp, **STACK)
        log(f"[{i}/{len(jobs)}] {terr}-{clim} {an} (improved_land={imp})  elapsed {(time.time()-t0)/60:.0f}m")
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "run_campaign.py")],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            log(f"      rc={r.returncode} STDERR: {r.stderr.strip()[-400:]}"); continue
        try:
            m = json.load(open(os.path.join(HERE, f"campaign_trajectory{tag}.json"), encoding="utf-8"))
            meta, row = m["meta"], m["traj"][-1]
            done.append((tag, meta, row))
            log(f"      steps={meta.get('steps_completed')} trunc={meta.get('truncated')} pop={row['pop']} "
                f"| PEOPLE: lin_size_lift={row.get('noble_lineage_size_lift')} lin_gini={row.get('lineage_size_gini')} "
                f"| GOODS: matl={row.get('noble_material_lift')} cred={row.get('noble_cred_lift')} "
                f"| strat={row.get('pct_stratified')}% gapd={row.get('village_gap_d_med')}")
        except Exception as e:
            log(f"      (readback failed: {e})")
    log(f"\nR-103h DONE in {(time.time()-t0)/60:.0f} min")
    log("SUMMARY — wealth-in-PEOPLE aristocracy vs GOODS, by world x land-use:")
    log(f"  {'arm':30s} {'linSizeLift':>11} {'linGini':>8} {'matlLift':>9} {'strat%':>7}")
    for tag, meta, row in done:
        log(f"  {tag[6:]:30s} {str(row.get('noble_lineage_size_lift')):>11} {str(row.get('lineage_size_gini')):>8} "
            f"{str(row.get('noble_material_lift')):>9} {str(row.get('pct_stratified')):>7}")
