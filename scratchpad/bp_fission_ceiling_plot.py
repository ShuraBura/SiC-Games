"""R-106 #17 figure (final): community size vs neighborhood radius. At the FACE-TO-FACE scale (r=1) the model sits AT
Alberti 158 / Yanomamo 200, below Alvard 250 -- no over-run. Exact-cell under-counts, r=2/cluster over-count."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

r = [0, 1, 2]
xlab = ["r=0 cell\n(100 km2)", "r=1 3x3\n(900 km2, face-to-face)", "r=2 5x5\n(2500 km2, region)"]
temp = [92, 155, 308]
sav = [116, 200, 324]

fig, ax = plt.subplots(figsize=(9.5, 5.4))
ax.axhspan(147, 170, color="crimson", alpha=0.08)
ax.axhline(158, ls="--", c="crimson", lw=1.4, label="Alberti 158 (scalar-stress ceiling)")
ax.axhline(200, ls="-.", c="#b5651d", lw=1.2, label="Yanomamo ~200 (fission threshold)")
ax.axhline(250, ls=":", c="darkred", lw=1.4, label="Alvard 250 (ethnographic max)")
ax.plot(r, temp, "o-", c="#1f77b4", lw=2, label="temperate")
ax.plot(r, sav, "s-", c="#e0a030", lw=2, label="savanna")
for i in range(3):
    ax.annotate(f"{temp[i]}", (r[i], temp[i]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color="#1f77b4")
    ax.annotate(f"{sav[i]}", (r[i], sav[i]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color="#b8860b")
ax.set_xticks(r); ax.set_xticklabels(xlab, fontsize=9)
ax.set_ylabel("densest community size (people)")
ax.set_title("R-106 #17 fission ceiling (current canon) — at the FACE-TO-FACE scale the model sits AT the anchor\n"
             "no over-run; the recorded 'miss at 220' was stale + wrong-scale (exact-cell under / band_id-cluster over)")
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 360)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_fission_ceiling.png", dpi=110)
print("wrote bp_fission_ceiling.png")
