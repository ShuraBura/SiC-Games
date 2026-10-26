"""R-106 Add.107 figure: what the STARVING lack, compared with the LIVING, on the three canonical worlds."""
import json
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
W = ["temperate", "savanna", "montane"]
data = {w: json.load(open(os.path.join(ROOT, "scratchpad", f"deathprobe_{w}.json"), encoding="utf-8")) for w in W}


def fr(xs, p):
    return sum(1 for x in xs if p(x)) / len(xs)


def md(xs, k):
    return st.median([x[k] for x in xs])


PANELS = [
    ("A. On a cell holding stored food", lambda xs: fr(xs, lambda x: x["store"] > 0.1), "fraction", (0, 1.05)),
    ("B. Food per head on own cell (x need)", lambda xs: md(xs, "food_pc"), "median, x need", None),
    ("C. People on own cell", lambda xs: md(xs, "occ"), "median", None),
    ("D. No family head (no provider)", lambda xs: fr(xs, lambda x: x["head"] == "none"), "fraction", (0, 1.05)),
    ("E. Juvenile", lambda xs: fr(xs, lambda x: x["juv"]), "fraction", (0, 1.05)),
    ("F. Intake this step (x need)", lambda xs: md(xs, "intake"), "median, x need", None),
]
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
x = np.arange(3)
wd = 0.36
for ax, (title, fn, ylab, ylim) in zip(axes.ravel(), PANELS):
    dv = [fn(data[w]["deaths"]) for w in W]
    lv = [fn(data[w]["living"]) for w in W]
    b1 = ax.bar(x - wd / 2, dv, wd, color="#c8553d", label="dying")
    b2 = ax.bar(x + wd / 2, lv, wd, color="#4a6fa5", label="living")
    for bars, vals in ((b1, dv), (b2, lv)):
        for r, v in zip(bars, vals):
            ax.text(r.get_x() + r.get_width() / 2, v, f"{v:.2f}" if v < 10 else f"{v:.0f}",
                    ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(W)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(ylab)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(axis="y", alpha=0.3)
axes[0, 0].legend(fontsize=9)
fig.suptitle("R-106 Add.107 — the starving die AWAY from stored food (A); in temperate/montane on FOOD-EMPTY cells (B) "
             "without a provider (D);\nin savanna as CHILDREN on a food-rich cell with the mother present "
             "(B, E — see text). Real pipeline, steps 3000-6000, deaths vs same-schedule living sample.", fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.92))
out = os.path.join(ROOT, "scratchpad", "bp_deathprobe.png")
fig.savefig(out, dpi=110)
print("wrote", out)
