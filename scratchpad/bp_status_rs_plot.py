"""R-106 #11 figure: the raw marker under-reads (age confound); age-controlled status->RS = 0.15 = von Rueden monogamous."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

labels = ["r_all\n(raw marker,\nall repro males)", "r_mature\n(age>=40)", "r_partial\n(age-controlled;\nvon-Rueden-comparable)"]
temp = [0.106, 0.178, 0.157]; temp_e = [0.052, 0.097, 0.063]
sav = [0.112, 0.139, 0.143]; sav_e = [0.032, 0.071, 0.050]

x = np.arange(3); w = 0.36
fig, ax = plt.subplots(figsize=(9.5, 5.2))
ax.axhspan(0.13, 0.15, color="crimson", alpha=0.10, label="von Rueden monogamous ~0.13-0.15")
ax.axhline(0.15, ls="--", c="crimson", lw=1.3)
ax.axhline(0.19, ls=":", c="darkred", lw=1.2, label="cross-system 0.19 (polygyny-inflated)")
b1 = ax.bar(x - w/2, temp, w, yerr=temp_e, capsize=4, color="#1f77b4", label="temperate")
b2 = ax.bar(x + w/2, sav, w, yerr=sav_e, capsize=4, color="#e0a030", label="savanna")
for bars, vals in ((b1, temp), (b2, sav)):
    for r, v in zip(bars, vals):
        ax.text(r.get_x() + r.get_width()/2, v + 0.006, f"{v:.2f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("corr(prowess, offspring | male)")
ax.set_title("R-106 #11 status->RS — the raw marker under-reads (age confound)\n"
             "age-controlled = 0.157/0.143 = von Rueden monogamous 0.15 (MET); polygyny-inflation gone (R-77)")
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 0.24)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_status_rs.png", dpi=110)
print("wrote bp_status_rs.png")
