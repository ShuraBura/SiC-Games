"""R-106 Add.88 figure: the graded-cohesion-band idea does NOT transfer to tier-5 (re-confirmed on the adopted canon).

The savanna natural control is the whole argument: it runs UNSATURATED cohesion (5% at cap) yet its bands are NOT
bigger than temperate's saturated ones — so de-saturating cohesion cannot be the band-size lever. And in BOTH biomes
bands sit far below their own fission cap (size/split_thr < 0.6), a spatial packing limit, not a cohesion-cap one.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

biomes = ["temperate", "savanna"]
coh_sat = [58.96, 4.94]        # % of band-records with cohesion_frac at 1.0
band_ad = [10.5, 10.5]         # band_med_adults
util = [0.30, 0.55]            # median size / split_thr
HILL = 28.2

fig, ax = plt.subplots(1, 3, figsize=(13, 4.6))
x = np.arange(2)

ax[0].bar(x, coh_sat, color=["#1f77b4", "#e0a030"])
ax[0].set_xticks(x); ax[0].set_xticklabels(biomes)
ax[0].set_ylabel("% of bands with cohesion at cap (1.0)")
ax[0].set_title("Cohesion saturation\nsavanna already DE-SATURATED (5%)")
for i, v in enumerate(coh_sat):
    ax[0].text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=10)
ax[0].set_ylim(0, 70)

ax[1].axhline(HILL, ls="--", c="crimson", lw=1.4, label="Hill 2011 = 28.2")
ax[1].bar(x, band_ad, color=["#1f77b4", "#e0a030"])
ax[1].set_xticks(x); ax[1].set_xticklabels(biomes)
ax[1].set_ylabel("band_med_adults")
ax[1].set_title("Band size (adults)\nde-saturated savanna is NOT bigger")
for i, v in enumerate(band_ad):
    ax[1].text(i, v + 0.6, f"{v:.1f}", ha="center", fontsize=10)
ax[1].legend(fontsize=8); ax[1].set_ylim(0, 32)

ax[2].axhline(1.0, ls=":", c="0.4", lw=1.2, label="fission cap")
ax[2].axhline(0.8, ls="--", c="crimson", lw=1.0, label="cohesion-cap threshold 0.8")
ax[2].bar(x, util, color=["#1f77b4", "#e0a030"])
ax[2].set_xticks(x); ax[2].set_xticklabels(biomes)
ax[2].set_ylabel("median band size / split_thr")
ax[2].set_title("Bands sit FAR below their cap\n-> SPATIAL limit, not a cohesion cap")
for i, v in enumerate(util):
    ax[2].text(i, v + 0.03, f"{v:.2f}", ha="center", fontsize=10)
ax[2].legend(fontsize=8); ax[2].set_ylim(0, 1.1)

fig.suptitle("R-106 Add.88 (adopted canon) — the tolerance-band pattern does NOT transfer to tier-5 band size "
             "(Add.80 falsification holds)", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_bandsize_add87.png", dpi=110)
print("wrote bp_bandsize_add87.png")
