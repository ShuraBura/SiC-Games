"""R-106 Add.89 figure: with the RIGHT unit (the cell = the model's own co-residence unit) and the RIGHT statistic
(person-weighted mean-experienced), the model matches Hill 28.2. band_id is a ~8-cell affiliation (not a camp);
the cluster is the whole agglomerated region."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

units = ["cell\n(camp: model's own\nco-residence unit)", "band_id\n(affiliation,\n~8 cells)", "cluster\n(whole occupied\nregion)"]
temp = [33.3, 48.2, 357.1]
sav = [22.9, 58.8, 210.0]
HILL = 28.2

x = np.arange(3); w = 0.36
fig, ax = plt.subplots(figsize=(10.5, 5.6))
ax.axhline(HILL, ls="--", c="crimson", lw=1.5, label="Hill 2011 = 28.2 (mean-experienced adults)")
ax.axhspan(11.7, 40, color="crimson", alpha=0.07, label="Hill per-society range (~12-40)")
b1 = ax.bar(x - w/2, temp, w, color="#1f77b4", label="temperate")
b2 = ax.bar(x + w/2, sav, w, color="#e0a030", label="savanna")
for bars, vals in ((b1, temp), (b2, sav)):
    for r, v in zip(bars, vals):
        ax.text(r.get_x() + r.get_width()/2, min(v, 360) + 6, f"{v:.0f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(units, fontsize=9)
ax.set_ylabel("mean-experienced adults (person-weighted)")
ax.set_title("R-106 Add.89 - the tier-5 'miss' was wrong STATISTIC + wrong UNIT\n"
             "the CELL (the model's co-residence unit, used for leveling/consumption) matches Hill 28.2")
ax.legend(fontsize=8, loc="upper left")
ax.set_yscale("log"); ax.set_ylim(8, 500)
ax.grid(axis="y", alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_bandsize_unit.png", dpi=110)
print("wrote bp_bandsize_unit.png")
