"""R-106 Addendum 102 — rank the candidate drivers of #11 status->RS, WITHIN each world.

Cross-world the mating-pool size (connubium reach) tracks status->RS monotonically (633/409/576 vs
0.283/0.141/0.262), but n=3 is weak. This correlates status_rs_r_partial against each candidate driver ACROSS the
601 trajectory snapshots WITHIN each world, which is a far stronger test and one the cross-world ranking cannot fake.

Candidates: connubium reach (mate-choice pool), population/density, operational sex ratio, gini_cred (status
spread available to sort on), polygyny, unpaired-men fraction, male RS gini (the skew itself).

CAVEAT stated up front: trajectory series are autocorrelated, so these r values are for RANKING candidates, not for
significance. A first-difference correlation is reported alongside, which largely removes the shared trend.
"""
import json
import numpy as np

WORLDS = {
    "temperate": "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_temperate.json",
    "savanna":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_savanna.json",
    "montane":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_montane.json",
}
TARGET = "status_rs_r_partial"
CANDS = ["connubium_med", "pop", "density_occupied_per_km2", "operational_sex_ratio", "gini_cred",
         "frac_polygynous_all_m", "frac_unpaired_adult_m", "male_rs_gini", "n_bands", "eff_lineages"]


def series(traj, f):
    return [(r.get("step"), r.get(f)) for r in traj]


def paired(traj, a, b):
    xs, ys = [], []
    for r in traj:
        va, vb = r.get(a), r.get(b)
        if va is None or vb is None or va != va or vb != vb:
            continue
        xs.append(float(va)); ys.append(float(vb))
    return np.array(xs), np.array(ys)


def r_of(x, y):
    if len(x) < 5 or x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def main():
    data = {w: json.load(open(p))["traj"] for w, p in WORLDS.items()}
    # drop the early transient: the first 20% is the founder shakeout (lineages crash, gini_cred climbs)
    for w in data:
        n = len(data[w])
        data[w] = data[w][int(n * 0.2):]
    print(f"corr( {TARGET} , candidate ) within world, after dropping the first 20% (founder transient)")
    print("levels r  /  first-difference r  (the latter removes the shared trend)\n")
    print(f"{'candidate':28s} " + "".join(f"{w:>22s}" for w in WORLDS))
    print("-" * 95)
    rows = []
    for c in CANDS:
        cells, mags = [], []
        for w in WORLDS:
            x, y = paired(data[w], c, TARGET)
            rl = r_of(x, y)
            dx, dy = np.diff(x), np.diff(y)
            rd = r_of(dx, dy)
            cells.append(f"{rl:+.2f} / {rd:+.2f}".rjust(22))
            if rl == rl:
                mags.append(abs(rl))
        rows.append((np.mean(mags) if mags else 0.0, c, "".join(cells)))
    for mag, c, cells in sorted(rows, reverse=True):
        print(f"{c:28s} {cells}   |mean r|={mag:.2f}")


if __name__ == "__main__":
    main()
