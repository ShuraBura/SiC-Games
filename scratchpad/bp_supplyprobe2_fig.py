"""R-106 Add.110 figure 2: the child dies on the step its mother is released from the village pin and moves off stock."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
W = ["savanna", "montane", "temperate"]
D = {w: json.load(open(os.path.join(ROOT, "scratchpad", f"supplyprobe2_{w}.json"), encoding="utf-8")) for w in W}
CD, CL = "#c0392b", "#2a7ab0"
x = np.arange(3)


def bars(ax, fn, title, ylab):
    for off, key, col, lab in ((-0.18, "deaths", CD, "mother of a child who starves"),
                               (0.18, "living", CL, "mother of a living child")):
        v = [fn(D[w][key]) for w in W]
        ax.bar(x + off, v, 0.34, color=col, label=lab)
        for i, y in enumerate(v):
            ax.text(i + off, y + 0.02, f"{y:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(W); ax.set_ylim(0, 1.12)
    ax.set_title(title, fontsize=10); ax.set_ylabel(ylab, fontsize=9); ax.grid(axis="y", alpha=0.3)


fig, axes = plt.subplots(1, 3, figsize=(17, 5.4))
vil = lambda R: [r for r in R if r["village"]]
rel = lambda R: [r for r in vil(R) if r["branch"] == "ifd"]
bars(axes[0], lambda R: len(rel(R)) / len(vil(R)),
     "A. Village member RELEASED from the pin this step\n(abandonment or crowding stress -> free IFD move)",
     "fraction of village-member mothers")
axes[0].legend(fontsize=8, loc="upper left")
bars(axes[1], lambda R: np.mean([r["ifd_to_stock"] for r in rel(R)]),
     "B. Released mother's IFD move lands on a cell WITH stored food\n(the village site is stocked for 99% of savanna ones)",
     "fraction of released mothers")
bars(axes[2], lambda R: np.mean([r["band_on_stock"] for r in rel(R) if r["stock_nbr"]]),
     "C. Her band is present on the neighbouring stock\n(so the IFD DOES value it — substrate.py:280)",
     "fraction of released mothers")
fig.suptitle("R-106 Add.110 — the starving child dies on the step its mother is RELEASED from the village pin and the IFD "
             "moves the family one cell\noff the granary. The release is a per-step coin flip (p = hardship ~0.3-0.7); "
             "living families are released too, but their move lands on stock. Real pipeline, seed 0, steps 3000-6000.",
             fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.88))
out = os.path.join(ROOT, "scratchpad", "bp_supplyprobe2.png")
fig.savefig(out, dpi=110)
print("wrote", out)
