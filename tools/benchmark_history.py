"""Benchmark HISTORY across canon snapshots: which benchmarks hit now, which missed now, which have NEVER hit.

WHY (2026-10-26, audit folder). "Does the model hit benchmark X?" has a time dimension: a marker can pass today and
have failed for months, or fail today after passing (fertility: in band at Add.81, below band at Add.113). One table
across every canon whose full-length runs are still on disk answers it with one rule.

SNAPSHOTS (the full-length 15,000-step canonical campaigns that exist on disk; trajectories are git-ignored):
  Add.100  `campaign_trajectory_scorecard99_<world>.json`   1 run per world, no period life table
  Add.106  `campaign_trajectory_s2_<world>_canon_s<k>.json`  3 seeds (the canon before food-viable sites)
  Add.108  `..._viable_s<k>`  + food-viable daughter sites (adopted Add.108)
  Add.109  `..._pat_s<k>`     + fathers provision their children (adopted Add.109)
  Add.113  `..._riskvg_s<k>`  + village granary + terrain risk as a 10% accident share (adopted Add.113) = TODAY

BENCHMARKS: (a) every banded marker of docs/MARKER_MATRIX.md, bands from `tools/scorecard.py`; (b) every anchored entry
of the demography monitor `demography.DEMOG_ANCHORS` — a "point" anchor with a tolerance is scored as the band
[anchor·(1−tol), anchor·(1+tol)] and LABELLED a reporting threshold (the code says it is "never a calibration
target"). `band_med_adults` is reported without a verdict: RESULTS Add.89 retracted that statistic.

RULE: per run, the mean over the sustained window (last 15% of rows); #18–#21 from the period life table where the run
has a snapshot. Per world, mean ± SE over runs; PASS if the 1-SE interval is inside the band, FAIL if outside, unres.
otherwise (n=1 ⇒ SE 0). Category over the snapshot history:
  HITS NOW          PASS on all three worlds at Add.113
  PARTLY NOW        PASS on 1–2 worlds at Add.113
  MISSES NOW, HIT BEFORE   no world passes at Add.113, but some world passed in an earlier snapshot
  NEVER HIT (in the measured window)   no world passed in any snapshot
The window is 2026-09-18 → 2026-10-26; RESULTS may record passes on older canons (state that next to the table).

Run:  py -3 tools/benchmark_history.py --outdir audit/2026-10-26/evidence
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as st
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from scorecard import TRAJ_MARKERS, LT_MARKERS, sustained_mean, period_lt, verdict, OUTDIR   # noqa: E402

W = ["temperate", "savanna", "montane"]
SNAPS = [("Add.100", "campaign_trajectory_scorecard99_{w}.json", "2026-09-18"),
         ("Add.106", "campaign_trajectory_s2_{w}_canon_s*.json", "2026-09-22"),
         ("Add.108", "campaign_trajectory_s2_{w}_viable_s*.json", "2026-09-24"),
         ("Add.109", "campaign_trajectory_s2_{w}_pat_s*.json", "2026-09-24"),
         ("Add.113", "campaign_trajectory_s2_{w}_riskvg_s*.json", "2026-09-26")]
REPORT_ONLY = {"band_med_adults": "statistic retracted (RESULTS Add.89); marker #1 uses band_experienced_adults"}


def benchmarks():
    from sic_games.demography import DEMOG_ANCHORS
    out = []
    for label, fld, anchor, lo, hi in TRAJ_MARKERS + LT_MARKERS:
        if label.startswith("context"):
            continue
        kind = "period-LT" if (label, fld, anchor, lo, hi) in LT_MARKERS else "trajectory"
        out.append(dict(id=label, field=fld, source="MARKER_MATRIX", anchor=anchor, lo=lo, hi=hi, kind=kind,
                        note="" if (lo is not None or hi is not None) else "report-only / no band"))
    for key, spec in DEMOG_ANCHORS.items():
        if spec[0] == "band":
            _, lo, hi, src = spec
            note = ""
        else:
            _, a, tol, src = spec
            lo, hi = a * (1 - tol), a * (1 + tol)
            note = f"point {a} ±{tol:.0%} — a REPORTING threshold, not a calibration target"
        if key in REPORT_ONLY:
            lo = hi = None
            note = REPORT_ONLY[key]
        out.append(dict(id=f"monitor: {key}", field=key, source="demography_health", anchor=src[:90], lo=lo, hi=hi,
                        kind="trajectory", note=note))
    return out


def run_values(path, bms):
    d = json.load(open(path, encoding="utf-8"))
    row = {}
    lt = period_lt(d["meta"])
    for b in bms:
        if b["kind"] == "period-LT":
            row[b["id"]] = lt[b["field"]] if lt else None
        else:
            row[b["id"]] = sustained_mean(d["traj"], b["field"])
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    bms = benchmarks()
    hist = {b["id"]: {} for b in bms}
    nruns = {}
    for snap, pat, date in SNAPS:
        for w in W:
            files = sorted(glob.glob(os.path.join(OUTDIR, pat.format(w=w))))
            nruns[(snap, w)] = len(files)
            rows = [run_values(f, bms) for f in files]
            for b in bms:
                v = [r[b["id"]] for r in rows if isinstance(r.get(b["id"]), (int, float))]
                if not v:
                    continue
                m = st.mean(v)
                se = st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
                hist[b["id"]].setdefault(snap, {})[w] = dict(mean=m, se=se, n=len(v), verdict=verdict(m, se, b["lo"], b["hi"]))
    cats = {}
    for b in bms:
        h = hist[b["id"]]
        if b["lo"] is None and b["hi"] is None:
            cats[b["id"]] = "NOT SCORED"
            continue
        now = [h.get("Add.113", {}).get(w, {}).get("verdict") for w in W]
        ever = any(c.get("verdict") == "PASS" for s in h.values() for c in s.values())
        npass = sum(v == "PASS" for v in now)
        if not any(now):
            cats[b["id"]] = "NO DATA NOW"
        elif npass == 3:
            cats[b["id"]] = "HITS NOW"
        elif npass > 0:
            cats[b["id"]] = "PARTLY NOW"
        elif ever:
            cats[b["id"]] = "MISSES NOW, HIT BEFORE"
        else:
            cats[b["id"]] = "NEVER HIT (in window)"
    os.makedirs(os.path.join(ROOT, a.outdir), exist_ok=True)
    out = dict(snapshots=SNAPS, runs={f"{s}|{w}": n for (s, w), n in nruns.items()}, benchmarks=bms, history=hist,
               category=cats, rule=__doc__.split("RULE:")[1].split("Run:")[0].strip())
    jp = os.path.join(ROOT, a.outdir, "benchmark_history.json")
    json.dump(out, open(jp, "w", encoding="utf-8"), indent=1, default=str)
    # markdown table
    sym = {"PASS": "✅", "FAIL": "❌", "unres.": "⚠️", "": "▫️", None: "·"}
    L = ["| benchmark | band | " + " | ".join(s for s, _, _ in SNAPS) + " | category |",
         "|---|---|" + "---|" * len(SNAPS) + "---|"]
    order = ["HITS NOW", "PARTLY NOW", "MISSES NOW, HIT BEFORE", "NEVER HIT (in window)", "NO DATA NOW", "NOT SCORED"]
    for c in order:
        for b in bms:
            if cats[b["id"]] != c:
                continue
            band = ("—" if b["lo"] is None and b["hi"] is None else
                    f"[{'' if b['lo'] is None else f'{b['lo']:.3g}'}, {'' if b['hi'] is None else f'{b['hi']:.3g}'}]")
            cells = []
            for s, _, _ in SNAPS:
                h = hist[b["id"]].get(s, {})
                cells.append("".join(sym[h.get(w, {}).get("verdict")] for w in W) if h else "·")
            L.append(f"| {b['id']} | {band} | " + " | ".join(cells) + f" | **{c}** |")
    mp = os.path.join(ROOT, a.outdir, "benchmark_history.md")
    open(mp, "w", encoding="utf-8").write(
        "# Benchmark history (GENERATED by tools/benchmark_history.py)\n\nEach cell = temperate · savanna · montane: "
        "✅ PASS, ⚠️ unresolved, ❌ FAIL, ▫️ reported without a verdict, · no data. Runs per world: Add.100 = 1, "
        "others = 3.\n\n" + "\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(jp, ROOT)} and {os.path.relpath(mp, ROOT)}")
    for c in order:
        ids = [b["id"] for b in bms if cats[b["id"]] == c]
        print(f"{c:26s} {len(ids):3d}  " + "; ".join(ids))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
