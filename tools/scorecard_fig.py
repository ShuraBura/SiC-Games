"""Plot a scorecard evidence file (tools/scorecard.py --out): every banded marker as the run values, the world mean,
and the band, one panel per marker. Optional second file = the previous canon, drawn grey for comparison.

Run:  py -3 tools/scorecard_fig.py docs/evidence/scorecard_add113_canon.json [docs/evidence/scorecard_add109_canon.json]
          [--png docs/evidence/scorecard_add113_canon.png]
"""
import argparse
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from scorecard import TRAJ_MARKERS, LT_MARKERS   # noqa: E402

W = ["temperate", "savanna", "montane"]
COL = {"PASS": "#1b7f5a", "FAIL": "#c0392b", "unres.": "#e07a1f", "": "#4a6fa5"}

ap = argparse.ArgumentParser()
ap.add_argument("cur")
ap.add_argument("prev", nargs="?")
ap.add_argument("--png")
a = ap.parse_args()
cur = json.load(open(os.path.join(ROOT, a.cur), encoding="utf-8"))["summary"]
prev = json.load(open(os.path.join(ROOT, a.prev), encoding="utf-8"))["summary"] if a.prev else {}
M = [m for m in TRAJ_MARKERS + LT_MARKERS if not m[0].startswith("context")]
n = len(M)
cols = 6
rows = math.ceil(n / cols)
fig, axes = plt.subplots(rows, cols, figsize=(3.3 * cols, 2.7 * rows))
for ax, (label, fld, anchor, lo, hi) in zip(axes.flat, M):
    s = cur.get(label, {})
    ys = [v for w in W for v in s.get(w, {}).get("values", [])] + \
         [v for w in W for v in prev.get(label, {}).get(w, {}).get("values", [])]
    if lo is not None or hi is not None:
        y0 = lo if lo is not None else min(ys + [hi]) - 0.1 * abs(hi or 1)
        y1 = hi if hi is not None else max(ys + [lo]) + 0.1 * abs(lo or 1)
        ax.axhspan(y0, y1, color="#2a9d8f", alpha=0.10, zorder=0)
    for i, w in enumerate(W):
        if w in prev.get(label, {}):
            p = prev[label][w]
            ax.scatter([i - 0.15] * len(p["values"]), p["values"], s=10, color="#bbbbbb", zorder=2)
            ax.hlines(p["mean"], i - 0.25, i - 0.05, color="#999999", lw=1.6, zorder=3)
        if w in s:
            c = s[w]
            ax.scatter([i + 0.15] * len(c["values"]), c["values"], s=14, color=COL[c["verdict"]], zorder=3)
            ax.hlines(c["mean"], i + 0.05, i + 0.25, color=COL[c["verdict"]], lw=2.4, zorder=4)
    ax.set_xticks(range(3)); ax.set_xticklabels(["temp", "sav", "mont"], fontsize=7)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_title(label.replace(" (", "\n("), fontsize=7.5)
    ax.grid(axis="y", alpha=0.25)
for ax in list(axes.flat)[n:]:
    ax.axis("off")
fig.suptitle(f"Marker scorecard — {os.path.basename(a.cur)}  (green = PASS at 1 SE, orange = unresolved, red = FAIL, "
             f"blue = reported without a verdict; shaded = band; grey = {os.path.basename(a.prev) if a.prev else 'n/a'})",
             fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.97))
out = os.path.join(ROOT, a.png or a.cur.replace(".json", ".png"))
fig.savefig(out, dpi=100)
print("wrote", os.path.relpath(out, ROOT))
