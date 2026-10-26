"""R-106 Add.110 figure: mothers of starving children vs mothers of living children, three worlds."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
W = ["savanna", "montane", "temperate"]
D = {w: json.load(open(os.path.join(ROOT, "scratchpad", f"supplyprobe_{w}.json"), encoding="utf-8")) for w in W}
CD, CL = "#c0392b", "#2a7ab0"

fig, axes = plt.subplots(1, 3, figsize=(17, 5.4))

# A: own cell stocked (store per head > 0.01 body-reserves)
ax = axes[0]
x = np.arange(3)
for off, key, col, lab in ((-0.18, "deaths", CD, "mother of a child who starves"), (0.18, "living", CL, "mother of a living child")):
    v = [np.mean([r["store_ph"] > 0.01 for r in D[w][key]]) for w in W]
    ax.bar(x + off, v, 0.34, color=col, label=lab)
    for i, y in enumerate(v):
        ax.text(i + off, y + 0.02, f"{y:.2f}", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(W); ax.set_ylim(0, 1.12)
ax.set_title("A. Mother's own cell holds stored food", fontsize=10)
ax.legend(fontsize=8, loc="upper right"); ax.grid(axis="y", alpha=0.3)

# B: distance to nearest stocked cell
ax = axes[1]
for i, w in enumerate(W):
    for off, key, col in ((-0.18, "deaths", CD), (0.18, "living", CL)):
        g = np.array([r["gdist"] for r in D[w][key]])
        f0, f1, f2 = np.mean(g == 0), np.mean(g == 1), np.mean(g >= 2)
        ax.bar(i + off, f0, 0.34, color=col)
        ax.bar(i + off, f1, 0.34, bottom=f0, color=col, alpha=0.45)
        ax.bar(i + off, f2, 0.34, bottom=f0 + f1, color="#555555")
        ax.text(i + off, f0 / 2, "0", ha="center", va="center", fontsize=8, color="white")
        if f1 > 0.05:
            ax.text(i + off, f0 + f1 / 2, "1", ha="center", va="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(W); ax.set_ylim(0, 1.05)
ax.set_title("B. Distance to the nearest stored food (cells)\nsolid = 0 (on it), pale = 1 cell, grey = 2+", fontsize=10)
ax.grid(axis="y", alpha=0.3)

# C: mother's intake / need, distributions
ax = axes[2]
xs = np.linspace(0, 3, 301)
for w, lw in zip(W, (2.4, 1.3, 0.8)):
    for key, col, ls in (("deaths", CD, "-"), ("living", CL, "--")):
        v = np.sort([r["m_intake"] for r in D[w][key]])
        ax.plot(xs, np.searchsorted(v, xs, side="right") / len(v), color=col, ls=ls, lw=lw)
    v = np.sort([r["m_intake"] for r in D[w]["living"]])
    y = np.searchsorted(v, 2.2, side="right") / len(v)
    ax.text(2.25, y + 0.01, w, fontsize=8, color=CL)
ax.axvline(1.0, color="#333333", ls=":", lw=1)
ax.text(1.03, 0.03, "need", fontsize=8)
ax.set_xlim(0, 3); ax.set_ylim(0, 1.02); ax.grid(alpha=0.3)
ax.set_xlabel("mother's own intake / need")
ax.set_ylabel("cumulative fraction of mothers")
ax.set_title("C. Mother's harvest this step (thick = savanna, thin = temperate)\n"
             "red solid = child starves, blue dashed = child lives", fontsize=10)

fig.suptitle("R-106 Add.110 — the savanna supply gap is an ACCESS gap: on every world the starving child's mother stands on a "
             "cell with no stored food,\nwith stored food at most ONE cell away. The granary belongs to one cell, and only "
             "its occupants fill it or eat from it. Real pipeline, new canon, seed 0, steps 3000-6000.", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.88))
out = os.path.join(ROOT, "scratchpad", "bp_supplyprobe.png")
fig.savefig(out, dpi=110)
print("wrote", out)
