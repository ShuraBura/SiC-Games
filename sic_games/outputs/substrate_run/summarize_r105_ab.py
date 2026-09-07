"""R-105 / R-64 A/B aggregator — reads the arm trajectories directly (not the interleaved launcher log).

Reports, per seed and pooled over seeds, the R-64 headline quantities with the ceiling gap OPEN (ceil0, what every
pre-R-105 result was grown on) vs CLOSED (ceil1, the fix). R-65's lesson is built in: %stratified FLUCTUATES (7-29%
on one world), so a single final snapshot is not the statistic — the sustained median over steps>=800 is.
"""
import glob
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
# NOTE on which column answers R-64. The campaign harness's `village_*` counts BANDS larger than `band_split`
# (45), which is NOT R-64's village — R-64's "village median ~100 / max ~241" was SITE-CELL OCCUPANCY, i.e. this
# harness's `settle_*`. Compare settle_med/settle_max against R-64, not village_med.
KEYS = ("pop", "pct_stratified", "gini_cred", "settle_med", "settle_max", "n_settle",
        "bigband_med", "bigband_max", "n_bigbands", "surplus_med", "deaths_starv")


def arms():
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, "campaign_trajectory_r105ab_s*_ceil*.json"))):
        b = os.path.basename(f)
        seed = int(b.split("_s")[1].split("_")[0])
        ceil = int(b.split("_ceil")[1].split(".")[0])
        d = json.load(open(f, encoding="utf-8"))
        out[(seed, ceil)] = (d["meta"], d["traj"])
    return out


def sustained(traj, key, from_step=800):
    v = [r[key] for r in traj if r["step"] >= from_step and r.get(key) is not None]
    return statistics.median(v) if v else None


def band(vals):
    return f"{min(vals):.3g}-{max(vals):.3g}" if vals else "n/a"


if __name__ == "__main__":
    A = arms()
    seeds = sorted({s for s, _ in A})
    print(f"R-105 / R-64 A/B — coastal-temperate, 2000 steps, ELITE=0 DEFEND=0, seeds {seeds}")
    print("R-64 published (pre-fix stack): pop plateau ~7200, %strat SUSTAINED 9-16, village med ~100 / max ~241\n")

    print("PER-SEED, sustained median over steps>=800 (the fluctuating-quantity statistic, R-65)")
    hdr = f"{'seed':>5} {'ceil':>5} " + " ".join(f"{k:>14}" for k in KEYS) + f" {'steps':>7}"
    print(hdr)
    for s in seeds:
        for c in (0, 1):
            if (s, c) not in A:
                continue
            meta, traj = A[(s, c)]
            row = " ".join(f"{sustained(traj, k)!s:>14}" for k in KEYS)
            print(f"{s:>5} {c:>5} {row} {meta.get('steps_completed'):>7}")
        print()

    print("POOLED over seeds (median of the per-seed sustained values), ceil0 -> ceil1")
    for k in KEYS:
        v0 = [sustained(A[(s, 0)][1], k) for s in seeds if (s, 0) in A]
        v1 = [sustained(A[(s, 1)][1], k) for s in seeds if (s, 1) in A]
        v0 = [x for x in v0 if x is not None]; v1 = [x for x in v1 if x is not None]
        if not (v0 and v1):
            continue
        m0, m1 = statistics.median(v0), statistics.median(v1)
        rel = f"  ({(m1 - m0) / m0 * 100:+.0f}%)" if m0 else ""
        print(f"  {k:16s} ceil0 {m0:>9.3g} [{band(v0):>13}]  ->  ceil1 {m1:>9.3g} [{band(v1):>13}]{rel}")

    print("\nFINAL SNAPSHOT (step 2000) — for comparability with how R-64 was reported")
    for s in seeds:
        for c in (0, 1):
            if (s, c) not in A:
                continue
            r = A[(s, c)][1][-1]
            print(f"  seed {s} ceil{c}: step {r['step']} pop {r['pop']} strat {r['pct_stratified']}% "
                  f"giniC {r['gini_cred']} bigbd_med {r['bigband_med']} bigbd_max {r['bigband_max']} "
                  f"n_vil {r['n_villages']} n_set {r['n_settle']} surplus {r['surplus_med']}")

    print("\nDOES THE GAP-OPEN ARM STILL REPRODUCE R-64? (pop ~7200, strat 9-16 sustained)")
    for s in seeds:
        if (s, 0) not in A:
            continue
        traj = A[(s, 0)][1]
        print(f"  seed {s}: pop {sustained(traj,'pop')}, strat sustained {sustained(traj,'pct_stratified')}%, "
              f"strat range {band([r['pct_stratified'] for r in traj if r['step']>=800])}")
