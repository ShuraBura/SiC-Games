"""R-106 Add.87 figure: with a GROUNDED capture fraction (0.15, the thigh-from-every-animal rate), the bands still land 0.36."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# grounded capfrac=0.15 grid, mat_gini
lts = [1.0, 1.5, 2.0]
fts = [1.5, 2.0, 3.0]
temp = {(1.0,1.5):0.363,(1.0,2.0):0.381,(1.0,3.0):0.377,(1.5,1.5):0.404,(1.5,2.0):0.432,(1.5,3.0):0.433,(2.0,1.5):0.412,(2.0,2.0):0.444,(2.0,3.0):0.484}
sav  = {(1.0,1.5):0.372,(1.0,2.0):0.389,(1.0,3.0):0.395,(1.5,1.5):0.401,(1.5,2.0):0.426,(1.5,3.0):0.447,(2.0,1.5):0.428,(2.0,2.0):0.457,(2.0,3.0):0.496}
BHM = 0.36

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0))
for ax, data, name in [(axes[0], temp, "temperate"), (axes[1], sav, "savanna")]:
    M = np.array([[data[(lt, ft)] for ft in fts] for lt in lts])
    im = ax.imshow(M, origin="lower", cmap="viridis", vmin=0.30, vmax=0.50, aspect="auto")
    ax.set_xticks(range(len(fts))); ax.set_xticklabels([f"{f:.1f}" for f in fts])
    ax.set_yticks(range(len(lts))); ax.set_yticklabels([f"{l:.1f}" for l in lts])
    ax.set_xlabel("feast_tolerance"); ax.set_ylabel("leveling_tolerance")
    for i, lt in enumerate(lts):
        for j, ft in enumerate(fts):
            v = data[(lt, ft)]
            on = abs(v - BHM) <= 0.03
            ax.text(j, i, f"{v:.3f}", ha="center", va="center",
                    color=("white" if v < 0.42 else "black"),
                    fontweight=("bold" if on else "normal"),
                    bbox=(dict(boxstyle="round", fc="none", ec="red", lw=2) if on else None))
    ax.set_title(f"{name} material Gini  (grounded capfrac 0.15, feast ON 0.25)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

fig.suptitle("R-106 Add.87 — grounded capture (0.15): lt1.0/ft1.5 lands 0.363/0.372 (red box = within 0.36+/-0.03)",
             fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_gini_ground.png", dpi=110)
print("wrote bp_gini_ground.png")
