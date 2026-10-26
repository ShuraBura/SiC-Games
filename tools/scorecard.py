"""Marker scorecard — score canonical campaign runs against docs/MARKER_MATRIX.md, seed as the replication unit.

WHY (2026-10-26, audit preparation). The Add.100 scorecard (`scratchpad/bp_scorecard99.py`) scored ONE run per world
and hard-coded its file names. Rule 5 of MARKER_MATRIX says an absolute marker value is valid only on the canon it
was measured on, so every adoption needs a re-score. This tool scores any set of `run_campaign.py` trajectories:

  per run    — each trajectory field: mean over the SUSTAINED window (the last 15% of rows, as Add.100);
               markers #18-#21: the PERIOD life table between the run's snapshot (meta.life_table_snap, written at
               C_LT_SNAP_STEP) and its end (meta.life_table_final) — the same computation as Stage 2.
  per world  — mean ± SE across the runs (seeds) of that world; verdict at 1 SE against the marker band:
               PASS (the 1-SE interval inside the band), FAIL (outside it), unres. (it straddles an edge).

Markers #5 (lineage dynamics per generation), #8 (fission rate per large-village-year) and #9 (the pre-registered
cross-world ordering) need computations that a trajectory row does not carry; their raw fields are reported
without a verdict, and MARKER_MATRIX states how each is scored.

Run:  py -3 tools/scorecard.py --glob "campaign_trajectory_s2_*_riskvg_s*.json" --world-re "s2_([a-z]+)_" \
          [--out docs/evidence/scorecard_<name>.json]
The --out file is the compact, committed evidence (the raw trajectories are git-ignored by design).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import statistics as st
import sys
from types import SimpleNamespace

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
OUTDIR = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
KEYS = ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc")

# (marker, trajectory field, anchor text, lo, hi) — bands from docs/MARKER_MATRIX.md; None = no verdict
TRAJ_MARKERS = [
    ("#1 band size (mean-experienced adults/cell)", "band_experienced_adults", "Hill 2011 = 28.2", 12, 40),
    ("#3 village size (median)", "village_med", "Alvard 2009 50-250", 50, 250),
    ("#3 village size (max, Voronoi catchment)", "village_max", "not the ceiling test: see #17 (Add.104)", None, None),
    ("#4 connubium reach (median)", "connubium_med", "Wobst ~475; floor White MVP 150", 150, None),
    ("#5 lineages (count; dynamics per MARKER_MATRIX)", "n_lineages", "Guyon 2024 (per-gen rates)", None, None),
    ("#7 nobility share", "ascribed_frac", "no documented band (rule 2)", None, None),
    ("#8 bud events (cumulative; rate per MARKER_MATRIX)", "bud_events", "Bandy 2004 2-5e-3/large-village-yr", None, None),
    ("#9 hierarchy index gini_cred", "gini_cred", "pre-registered ordering (T-7)", None, None),
    ("#10 polygyny (of ALL men)", "frac_polygynous_all_m", "Marlowe ~0.04", 0.02, 0.06),
    ("#11 status->RS (age-controlled)", "status_rs_r_partial", "NOT COMPARABLE, wrong channel (Add.102)", None, None),
    ("#12 rank-size slope", "village_zipf", "Zipf ~ -1.0", -1.5, -0.6),
    ("#13 primacy", "village_primate", "~1 (no primate centre)", 1.0, 2.0),
    ("#14 material Gini (adults)", "material_gini_adults", "BHM 2009 HG = 0.36", 0.30, 0.42),
    ("#14 material Gini (within-cell)", "material_gini_within_cell", "Agta within-camp 0.23 [0-0.44]", 0.0, 0.44),
    ("#15 orphanhood (motherless)", "frac_motherless", "Aché ~0.02 (point, no band)", None, None),
    ("#16 dependency ratio", "dependency_ratio", "H&H 1996 T4.4: 0.598-0.899", 0.598, 0.899),
    ("#16 share under 15", "frac_child", "H&H 1996 T4.4: 0.287-0.454", 0.287, 0.454),
    ("#16 sex ratio (m/f)", "sex_ratio_m_f", "H&H 1996 T4.4: 0.896-1.368", 0.896, 1.368),
    ("#16 median age (yr)", "median_age_yr", "reported with #16 (no band)", None, None),
    ("#17 fission ceiling (co-resident max)", "settle_max", "Alberti 158 / Alvard <=250", None, 250),
    ("context: population", "pop", "", None, None),
    ("context: starvation share of deaths", "starv_share", "", None, None),
    ("context: land use fraction", "spatial_land_use_frac", "", None, None),
]
LT_MARKERS = [
    ("#18 e0 (period)", "e0", "G&K 2007 forager band 21-37", 21.0, 37.0),
    ("#19 survival to 15 (period)", "surv_to_15", "G&K 2007 band 0.45-0.66", 0.45, 0.66),
    ("#20 e15 (period)", "e15", "G&K 2007 band 28.6-42.5", 28.6, 42.5),
    ("#21 survival to 45 from birth (period)", "surv_to_45", "G&K 2007 band 0.26-0.43", 0.26, 0.43),
]


def sustained_mean(traj, field, frac=0.15):
    win = traj[-max(1, int(len(traj) * frac)):]
    v = [r[field] for r in win if isinstance(r.get(field), (int, float)) and r[field] == r[field]]
    return st.mean(v) if v else None


def period_lt(meta):
    from sic_games.phase1_model import TerrainWorld
    fin, snap = meta.get("life_table_final"), meta.get("life_table_snap")
    if not fin or not snap:
        return None
    fake = SimpleNamespace(**{k: list(fin[k]) for k in KEYS})
    return TerrainWorld.life_table(fake, since={k: snap[k] for k in KEYS})


def verdict(m, se, lo, hi):
    if lo is None and hi is None:
        return ""
    a, b = m - se, m + se
    lo_ok, hi_ok = (lo is None or a >= lo), (hi is None or b <= hi)
    if lo_ok and hi_ok:
        return "PASS"
    if (lo is not None and b < lo) or (hi is not None and a > hi):
        return "FAIL"
    return "unres."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", required=True, help="trajectory file glob inside sic_games/outputs/substrate_run")
    ap.add_argument("--world-re", default=r"s2_([a-z]+)_", help="regex whose group 1 is the world name")
    ap.add_argument("--out", help="write the per-run and per-world numbers to this JSON (compact evidence)")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(OUTDIR, a.glob)))
    if not files:
        sys.exit(f"no files match {a.glob}")
    runs: dict = {}
    for f in files:
        w = re.search(a.world_re, os.path.basename(f)).group(1)
        d = json.load(open(f, encoding="utf-8"))
        row = {fld: sustained_mean(d["traj"], fld) for _, fld, *_ in TRAJ_MARKERS}
        lt = period_lt(d["meta"])
        if lt:
            row.update({k: lt[k] for _, k, *_ in LT_MARKERS})
        row["_file"] = os.path.basename(f)
        row["_steps"] = d["traj"][-1]["step"]
        runs.setdefault(w, []).append(row)
    worlds = list(runs)
    summary = {}
    print(f"runs: " + ", ".join(f"{w} n={len(runs[w])} (steps {runs[w][0]['_steps']})" for w in worlds))
    print(f"\n{'marker':48s}" + "".join(f"{w:>24s}" for w in worlds) + "   anchor")
    print("-" * (48 + 24 * len(worlds) + 30))
    for label, fld, anchor, lo, hi in TRAJ_MARKERS + LT_MARKERS:
        cells = []
        for w in worlds:
            v = [r[fld] for r in runs[w] if r.get(fld) is not None]
            if not v:
                cells.append(f"{'n/a':>24s}")
                continue
            m = st.mean(v)
            se = st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
            vd = verdict(m, se, lo, hi)
            summary.setdefault(label, {})[w] = dict(mean=m, se=se, n=len(v), verdict=vd, values=v)
            cells.append(f"{m:>11.4g} ±{se:<7.2g}{vd:>5s}")
        print(f"{label:48s}" + "".join(cells) + f"   {anchor}")
    if a.out:
        out = os.path.join(ROOT, a.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump(dict(glob=a.glob, runs=runs, summary=summary,
                       method="sustained window = last 15% of rows; #18-#21 = period life table "
                              "(snapshot -> end); world = mean ± SE over runs; verdict at 1 SE"),
                  open(out, "w", encoding="utf-8"), indent=1)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
