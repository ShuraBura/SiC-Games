"""R-106 Add.104 figure: montane's big 'villages' are not a good-spot effect. The resource landscape matches
temperate almost exactly; what differs is settlement-site density, which inflates the Voronoi catchment."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))

# --- left: resource landscape (the hypothesis) -- near-identical
labels = ["forage Gini", "occupied/empty\nforage ratio", "forage left\nUNUSED (frac)", "land use\n(frac)"]
temp = [0.220, 1.41 / 3, 0.829, 0.128]
mont = [0.241, 1.41 / 3, 0.825, 0.131]
x = np.arange(4); w = 0.36
ax[0].bar(x - w/2, temp, w, color="#1f77b4", label="temperate")
ax[0].bar(x + w/2, mont, w, color="#5a8f5a", label="montane")
for i in range(4):
    ax[0].text(i - w/2, temp[i] + 0.015, f"{temp[i]:.2f}", ha="center", fontsize=8)
    ax[0].text(i + w/2, mont[i] + 0.015, f"{mont[i]:.2f}", ha="center", fontsize=8)
ax[0].set_xticks(x); ax[0].set_xticklabels(labels, fontsize=8.5)
ax[0].set_title("A. Resource landscape: NEARLY IDENTICAL\n"
                "montane is not patchier and does not lack alternatives\n(ratio shown /3 to fit the axis)")
ax[0].legend(fontsize=9); ax[0].grid(axis="y", alpha=0.3)

# --- right: what actually differs
labels2 = ["settlement\nsites", "occupied cells\nPER SITE", "people per\noccupied cell",
           "largest single\nCELL (people)", "village_max\n(catchment)"]
t2 = [47, 4.3, 15.4, 108, 192.5]
m2 = [23, 9.1, 11.1, 103, 288.0]
x2 = np.arange(5)
b1 = ax[1].bar(x2 - w/2, t2, w, color="#1f77b4", label="temperate")
b2 = ax[1].bar(x2 + w/2, m2, w, color="#5a8f5a", label="montane")
for bars, vals in ((b1, t2), (b2, m2)):
    for r, v in zip(bars, vals):
        ax[1].text(r.get_x() + r.get_width()/2, v * 1.06, f"{v:g}", ha="center", fontsize=8)
ax[1].axhline(158, ls="--", c="crimson", lw=1.4, label="Alberti 158")
ax[1].axhline(250, ls=":", c="darkred", lw=1.3, label="Alvard 250")
ax[1].set_xticks(x2); ax[1].set_xticklabels(labels2, fontsize=8.5)
ax[1].set_yscale("log"); ax[1].set_ylim(3, 500)
ax[1].set_title("B. What actually differs: SITE DENSITY\n"
                "half the sites over the same footprint => 2x the catchment.\n"
                "True co-residence (largest CELL) is 103 vs 108 — both under 158")
ax[1].legend(fontsize=8, loc="upper left"); ax[1].grid(axis="y", alpha=0.3, which="both")

fig.suptitle("R-106 Add.104 — why montane carries the largest 'villages': not a good spot, a sparse-site artifact",
             fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_montane_why.png", dpi=110)
print("wrote bp_montane_why.png")
