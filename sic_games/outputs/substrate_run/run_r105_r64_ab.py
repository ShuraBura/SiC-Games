"""R-105 — R-64 RE-VALIDATION A/B: how much of the validated stratification rode on the capacity bug?

R-64 (docs/RESULTS.md) validated, on coastal-temperate over 2000 steps: village median ~100, p90 ~154, 77% in
Bar-Yosef 50-150, bounded stratified tail ~240, **stratification sustained 9-16%**, population plateau ~7200.
That run predates the R-105 fix, so it was grown on the INFLATED carrying capacity (the superlinear agglomeration
bonus escaped the R-63 ceiling at non-settlement cells). This A/B varies ONLY `C_AGGLCEIL` on matched seeds:

  ceil0 = the bug present (bit-exact with every pre-R-105 result)   ceil1 = the fix

Config matches R-64 as closely as the campaign harness allows: coastal-temperate, forage, ELITE off, DEFEND off
(the harness's C_DEFEND comment records that economic defensibility was NOT in the R-64 validation).
Arms run CONCURRENTLY (independent seeded processes; deterministic, so parallelism cannot change a result).

Run:  py -3 -u sic_games/outputs/substrate_run/run_r105_r64_ab.py       (from repo root)
"""
import os, subprocess, sys, time, json, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SEEDS = [int(s) for s in os.environ.get("AB_SEEDS", "0,1").split(",")]
STEPS = os.environ.get("AB_STEPS", "2000")            # R-64's horizon
LOGEVERY = "200"                                      # gives R-64's 400/800/1200/2000 rows exactly

BASE = dict(C_TERR="coastal", C_CLIM="temperate", C_IMPROVED="0", C_FOUNDERS="3000",
            C_ELITE="0", C_DEFEND="0", C_GENEA="0", C_GENOME="1",
            C_STEPS=STEPS, C_LOGEVERY=LOGEVERY, C_MAXMIN="0")

PROG = os.path.join(HERE, "r105_r64_ab_progress.txt")
# R-64's four headline claims + the capacity diagnostics that localise the bug.
KEYS = ("pop", "pct_stratified", "bigband_med", "bigband_max", "n_bigbands",
        "n_settle", "settle_max", "surplus_med", "deaths_starv", "gini_cred")


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


# NOTE on scope: R-64's "77% in Bar-Yosef 50-150" needs the village SIZE DISTRIBUTION, which the trajectory does
# not carry (only med/max). This A/B therefore compares median/max village size and %stratified, and does not
# recompute the 77%.


def launch(tag, seed, ceil):
    env = dict(os.environ, C_TAG=tag, C_SEED=str(seed), C_AGGLCEIL=str(ceil), **BASE)
    out = open(os.path.join(HERE, f"r105ab_stdout{tag}.txt"), "w", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-u", os.path.join(HERE, "run_campaign.py")],
                         cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, text=True)
    return p, out


def readback(tag):
    try:
        d = json.load(open(os.path.join(HERE, f"campaign_trajectory{tag}.json"), encoding="utf-8"))
        return d["meta"], d["traj"]
    except Exception as e:
        log(f"      (readback failed for {tag}: {e})")
        return None, None


if __name__ == "__main__":
    open(PROG, "w").close()
    t0 = time.time()
    log(f"R-105 / R-64 A/B: seeds {SEEDS} x ceil{{0,1}} @ {STEPS} steps, coastal-temperate, ELITE=0 DEFEND=0")

    procs = {}
    for seed in SEEDS:
        for ceil in (0, 1):
            tag = f"_r105ab_s{seed}_ceil{ceil}"
            procs[(seed, ceil)] = (tag,) + launch(tag, seed, ceil)
            log(f"  launched {tag}")

    for (seed, ceil), (tag, p, out) in procs.items():
        p.wait(); out.close()
        log(f"  finished {tag} rc={p.returncode}  (elapsed {(time.time()-t0)/60:.0f}m)")

    log("\n=== TRAJECTORIES (R-64 published: step 2000 -> pop 7210, village med 102 / max 241, strat 9%) ===")
    finals = {}
    for seed in SEEDS:
        for ceil in (0, 1):
            tag = procs[(seed, ceil)][0]
            meta, traj = readback(tag)
            if not traj:
                continue
            log(f"\n-- seed {seed}  C_AGGLCEIL={ceil}  (steps_completed={meta.get('steps_completed')}, "
                f"wall={meta.get('wall_minutes')}m, habitable={meta.get('habitable_cells')})")
            log("   " + " ".join(f"{k:>14}" for k in ("step",) + KEYS))
            for r in traj:
                log("   " + " ".join(f"{r.get(k):>14}" for k in ("step",) + KEYS))
            finals[(seed, ceil)] = traj[-1]
            # R-64's claim is about a SUSTAINED level, not one snapshot (R-65: strat wobbles 7-29%).
            tail = [r["pct_stratified"] for r in traj if r["step"] >= 800]
            log(f"   strat over steps>=800: min {min(tail)} med {statistics.median(tail)} max {max(tail)}")

    log("\n=== A/B DELTA (ceil1 vs ceil0) at the final snapshot ===")
    for seed in SEEDS:
        a, b = finals.get((seed, 0)), finals.get((seed, 1))
        if not (a and b):
            continue
        log(f"  seed {seed}:")
        for k in KEYS:
            va, vb = a.get(k), b.get(k)
            if va is None or vb is None:
                continue
            rel = f" ({(vb - va) / va * 100:+.0f}%)" if isinstance(va, (int, float)) and va else ""
            log(f"      {k:18s} ceil0 {va:>10} -> ceil1 {vb:>10}{rel}")

    log(f"\nR-105/R-64 A/B DONE in {(time.time()-t0)/60:.0f} min")
