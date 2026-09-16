"""R-106 Add.86 validation figure: the joint band lands material Gini at BHM 0.36 in BOTH biomes (not a temperate artifact)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

arms = ["lt0.6\nft2.0", "lt0.8\nft1.5", "lt0.8\nft2.0", "lt1.0\nft1.5", "lt1.0\nft1.75"]
temp = [0.325, 0.332, 0.353, 0.367, 0.365]
temp_e = [0.007, 0.008, 0.006, 0.011, 0.006]
sav = [0.321, 0.354, 0.363, 0.367, 0.383]
sav_e = [0.003, 0.014, 0.015, 0.008, 0.010]
BHM = 0.36

x = np.arange(len(arms))
w = 0.36
fig, ax = plt.subplots(figsize=(9.5, 5.2))
ax.axhspan(0.33, 0.39, color="crimson", alpha=0.08, label="0.36 +/- 0.03")
ax.axhline(BHM, ls="--", c="crimson", lw=1.4, label="BHM 2009 material Gini 0.36")
ax.axhline(0.174, ls=":", c="0.5", lw=1.2, label="canon 0.174 (pre-band)")
ax.bar(x - w/2, temp, w, yerr=temp_e, capsize=3, color="#1f77b4", label="temperate")
ax.bar(x + w/2, sav, w, yerr=sav_e, capsize=3, color="#e0a030", label="savanna")
ax.set_xticks(x)
ax.set_xticklabels(arms, fontsize=9)
ax.set_ylabel("material Gini (3-world panel, mean +/- SE)")
ax.set_xlabel("leveling_tolerance / feast_tolerance  (feast ON 0.25, concentrators on)")
ax.set_title("R-106 Add.86 — graded levelers reach BHM 0.36 in BOTH biomes\n"
             "lt1.0/ft1.5 lands 0.367/0.367 (biome-invariant); guardrails + tier-11 intact")
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 0.45)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_gini_band_biome.png", dpi=110)
print("wrote bp_gini_band_biome.png")
