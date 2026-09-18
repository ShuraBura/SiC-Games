"""R-106 Add.103 figure: #17's marker is a WINDOW, not a partition. On the village unit Alberti's anchor actually
uses, only montane genuinely over-runs."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

units = ["exact cell\n(one camp)", "VILLAGE\n(Voronoi partition\n= Alberti's unit)",
         "3x3 window\n(the Add.93 marker\nNOT a partition)", "band_id\n(dispersed\naffiliation)"]
temp = [114.5, 192.5, 255.7, 439.0]
sav = [100.9, 154.1, 155.1, 403.8]
mont = [102.6, 288.0, 301.6, 1079.8]

x = np.arange(4); w = 0.26
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.axhline(158, ls="--", c="crimson", lw=1.5, label="Alberti 158 (scalar-stress ceiling)")
ax.axhline(250, ls=":", c="darkred", lw=1.5, label="Alvard 250 (ethnographic max)")
b1 = ax.bar(x - w, temp, w, color="#1f77b4", label="temperate")
b2 = ax.bar(x, sav, w, color="#e0a030", label="savanna")
b3 = ax.bar(x + w, mont, w, color="#5a8f5a", label="montane")
for bars, vals in ((b1, temp), (b2, sav), (b3, mont)):
    for r, v in zip(bars, vals):
        ax.text(r.get_x() + r.get_width()/2, v * 1.04, f"{v:.0f}", ha="center", fontsize=8.5)
ax.set_xticks(x); ax.set_xticklabels(units, fontsize=9)
ax.set_ylabel("people in the largest unit")
ax.set_yscale("log"); ax.set_ylim(70, 1400)
ax.set_title("R-106 Add.103 — #17 depends entirely on the UNIT\n"
             "the 3x3 window straddles ~3 villages / 41 bands; on the VILLAGE unit only MONTANE over-runs 250")
ax.legend(fontsize=8.5, loc="upper left")
ax.grid(axis="y", alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_fission_unit.png", dpi=110)
print("wrote bp_fission_unit.png")
