"""R-106 figure: the tier-5 band-size 'miss' is a statistic-choice artifact. Hill's 28.2 is the MEAN EXPERIENCED
(person-weighted) adult band size (verbatim: 'the mean of all band sizes weighted by the number of individuals').
The marker scores the MEDIAN over band_ids. On the model's bimodal distribution the median undershoots and the
correct (person-weighted) statistic overshoots 28.2 -- so the model has no band-size deficit."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

labels = ["median over bands\n(CURRENT MARKER)", "mean over bands", "MEAN EXPERIENCED\n(Hill's statistic)"]
temp = [10.5, 21.3, 48.2]; temp_e = [0.3, 0.0, 9.5]
sav = [10.5, 22.7, 58.8]; sav_e = [0.8, 0.0, 30.8]
HILL = 28.2

x = np.arange(3); w = 0.36
fig, ax = plt.subplots(figsize=(10, 5.4))
ax.axhline(HILL, ls="--", c="crimson", lw=1.5, label="Hill 2011 = 28.2 (person-weighted adults)")
ax.axhspan(11.7, 25.0, color="crimson", alpha=0.07, label="Hill per-society range (Paiute 11.7 - Paliyan 25.0 shown)")
b1 = ax.bar(x - w/2, temp, w, yerr=temp_e, capsize=4, color="#1f77b4", label="temperate")
b2 = ax.bar(x + w/2, sav, w, yerr=sav_e, capsize=4, color="#e0a030", label="savanna")
for bars, vals in ((b1, temp), (b2, sav)):
    for r, v in zip(bars, vals):
        ax.text(r.get_x() + r.get_width()/2, v + 1.5, f"{v:.1f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("adult band size")
ax.set_title("R-106 — tier-5 'band too small' is a STATISTIC-CHOICE artifact\n"
             "the marker uses the MEDIAN (10.5); Hill's anchor is the PERSON-WEIGHTED mean, where the model is 48-59")
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 70)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_bandsize_experienced.png", dpi=110)
print("wrote bp_bandsize_experienced.png")
