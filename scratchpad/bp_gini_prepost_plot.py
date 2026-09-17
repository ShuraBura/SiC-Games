"""R-106 Add.90 figure: on the BHM-comparable ADULTS statistic, Add.87's concentrators gave real but PARTIAL
progress (0.13-0.14 -> 0.16-0.22), still ~2x below 0.36. The all-ages 'pass' at 0.36 was child-inflation."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

groups = ["temperate", "savanna"]
pre_ad = [0.141, 0.128]; pre_e = [0.037, 0.041]
post_ad = [0.216, 0.160]; post_e = [0.019, 0.013]
post_all = [0.363, 0.372]
BHM = 0.36

x = np.arange(2); w = 0.26
fig, ax = plt.subplots(figsize=(9.5, 5.3))
ax.axhline(BHM, ls="--", c="crimson", lw=1.5, label="BHM 2009 = 0.36 (age-adjusted ADULTS)")
ax.bar(x - w, pre_ad, w, yerr=pre_e, capsize=4, color="#9ecae1", label="adults, pre-Add.87")
ax.bar(x, post_ad, w, yerr=post_e, capsize=4, color="#1f77b4", label="adults, adopted (Add.87)")
ax.bar(x + w, post_all, w, color="#c0c0c0", label="all-ages, adopted (the mis-specified marker)")
for i in range(2):
    ax.text(i - w, pre_ad[i] + 0.01, f"{pre_ad[i]:.2f}", ha="center", fontsize=9)
    ax.text(i, post_ad[i] + 0.01, f"{post_ad[i]:.2f}", ha="center", fontsize=9)
    ax.text(i + w, post_all[i] + 0.01, f"{post_all[i]:.2f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=10)
ax.set_ylabel("material Gini")
ax.set_title("R-106 Add.90 - #14 re-assessed on the ADULTS statistic\n"
             "Add.87 gave PARTIAL adult concentration (0.14->0.22), still ~2x below 0.36; the 0.36 'pass' was child-inflated")
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 0.45)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_gini_prepost.png", dpi=110)
print("wrote bp_gini_prepost.png")
