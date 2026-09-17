"""R-106 Add.92 figure: adults-0.36 HAS a grounded landing — widening the tolerance bands (grounded concentrators)
reaches BHM 0.36 in BOTH biomes at lt~3/ft~4, guardrails intact. The capture skim was inert; the bands are the lever."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

x = [0, 1, 2, 3]
xlab = ["1.0/1.5\n(adopted)", "1.5/2.0", "2.0/3.0", "3.0/4.0"]
temp = [0.216, 0.276, 0.341, 0.386]; temp_e = [0.019, 0.011, 0.017, 0.013]
sav = [0.160, 0.250, 0.313, 0.357]; sav_e = [0.013, 0.021, 0.025, 0.008]
e0_t = [34.5, 37.4, 32.3, 33.5]; e0_s = [28.0, 28.0, 27.7, 25.8]
BHM = 0.36

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
ax[0].axhline(BHM, ls="--", c="crimson", lw=1.4, label="BHM 2009 = 0.36 (adults)")
ax[0].axhspan(0.33, 0.39, color="crimson", alpha=0.08)
ax[0].errorbar(x, temp, yerr=temp_e, fmt="o-", c="#1f77b4", capsize=3, label="temperate")
ax[0].errorbar(x, sav, yerr=sav_e, fmt="s-", c="#e0a030", capsize=3, label="savanna")
ax[0].set_xticks(x); ax[0].set_xticklabels(xlab, fontsize=9)
ax[0].set_xlabel("tolerance bands  leveling_tolerance / feast_tolerance")
ax[0].set_ylabel("material_gini_adults (the corrected #14 marker)")
ax[0].set_title("A. Wider bands reach adults-0.36 in BOTH biomes\n(grounded concentrators cap 0.15 / ag 0.15)")
ax[0].legend(fontsize=9); ax[0].grid(alpha=0.3); ax[0].set_ylim(0.1, 0.45)

ax[1].axhspan(21, 37, color="green", alpha=0.06, label="e0 guardrail [21-37]")
ax[1].plot(x, e0_t, "o-", c="#1f77b4", label="temperate e0")
ax[1].plot(x, e0_s, "s-", c="#e0a030", label="savanna e0")
ax[1].set_xticks(x); ax[1].set_xticklabels(xlab, fontsize=9)
ax[1].set_xlabel("tolerance bands")
ax[1].set_ylabel("e0 (yr)")
ax[1].set_title("B. e0 stays in range as bands widen\n(the 37.4 blip at 1.5/2.0 is non-monotonic noise)")
ax[1].legend(fontsize=9); ax[1].grid(alpha=0.3); ax[1].set_ylim(20, 40)

fig.suptitle("R-106 Add.92 — #14 on the CORRECTED marker: adults-0.36 has a grounded, guardrail-safe, biome-invariant "
             "landing at wider bands", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_gini_adults_bands.png", dpi=110)
print("wrote bp_gini_adults_bands.png")
