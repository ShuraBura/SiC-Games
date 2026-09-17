"""R-106 marker audit figure: #14 was calibrated on the WRONG statistic. The marker is all-ages material Gini
(child-inflated); BHM 0.36 is age-adjusted ADULTS. On the comparable adults statistic the model is 0.16-0.22, still
~2x below the anchor -- Add.87's 'pass' is on the child-inflated number."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

labels = ["ALL-AGES\n(the marker,\ncalibrated to 0.36)", "ADULTS-ONLY\n(BHM-comparable)"]
temp = [0.363, 0.216]; temp_e = [0.005, 0.019]
sav = [0.372, 0.160]; sav_e = [0.002, 0.013]
BHM = 0.36

x = np.arange(2); w = 0.36
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.axhline(BHM, ls="--", c="crimson", lw=1.5, label="BHM 2009 = 0.36 (age-adjusted ADULTS)")
b1 = ax.bar(x - w/2, temp, w, yerr=temp_e, capsize=4, color="#1f77b4", label="temperate")
b2 = ax.bar(x + w/2, sav, w, yerr=sav_e, capsize=4, color="#e0a030", label="savanna")
for bars, vals in ((b1, temp), (b2, sav)):
    for r, v in zip(bars, vals):
        ax.text(r.get_x() + r.get_width()/2, v + 0.008, f"{v:.3f}", ha="center", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("material Gini")
ax.set_title("R-106 marker audit - #14 was calibrated (Add.87) on the WRONG statistic\n"
             "all-ages Gini hits 0.36 via child-inflation; the BHM-comparable ADULTS Gini is 0.16-0.22, still ~2x low")
ax.legend(fontsize=9, loc="upper right")
ax.set_ylim(0, 0.45)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_gini_adults.png", dpi=110)
print("wrote bp_gini_adults.png")
