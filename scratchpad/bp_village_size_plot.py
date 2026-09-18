"""R-106 #3 figure: village size on a clean nearest-site partition lands at/near Alvard 50-250; the exact-cell
marker fragments and under-reads."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

groups = ["temperate", "savanna"]
vmed = [44, 74]; vmax = [142, 210]; exact = [32, 36]

x = np.arange(2); w = 0.26
fig, ax = plt.subplots(figsize=(9, 5.3))
ax.axhspan(50, 250, color="green", alpha=0.08, label="Alvard 2009 village 50-250")
ax.bar(x - w, exact, w, color="#c0c0c0", label="exact-cell settle_med (old marker, fragments)")
ax.bar(x, vmed, w, color="#1f77b4", label="village_med (nearest-site partition)")
ax.bar(x + w, vmax, w, color="#7fb2e0", label="village_max (nearest-site)")
for i in range(2):
    ax.text(i - w, exact[i] + 4, f"{exact[i]}", ha="center", fontsize=9)
    ax.text(i, vmed[i] + 4, f"{vmed[i]}", ha="center", fontsize=9)
    ax.text(i + w, vmax[i] + 4, f"{vmax[i]}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=10)
ax.set_ylabel("village size (people)")
ax.set_title("R-106 #3 village size — clean nearest-site partition lands at/near Alvard 50-250\n"
             "savanna med 74 IN range, temperate med 44 just below the 50 floor (max 142/210 in range); exact-cell fragments")
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 270)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_village_size.png", dpi=110)
print("wrote bp_village_size.png")
