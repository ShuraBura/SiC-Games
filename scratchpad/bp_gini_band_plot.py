"""R-106 Addendum 86 figure: the tolerance band turns the bang-bang levelers into a graded dial that reaches BHM 0.36."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- probe 1 (bp_gini_band): leveling-band sweep, concentrators on ---
lt = [0.0, 0.5, 1.0, 2.0, 4.0]
lev_feaston = [0.171, 0.210, 0.229, 0.235, 0.242]      # feast ON  -> saturates ~0.24
lt_nf = [0.0, 1.0, 2.0, 4.0]
lev_feastoff = [0.176, 0.373, 0.490, 0.603]            # feast OFF -> spans, 0.37 at band=1

# --- probe 2 (bp_gini_band2): feast on 0.25 throughout ---
ft = [0.5, 1.0, 2.0, 4.0]
feast_only = [0.181, 0.193, 0.192, 0.175]              # feast band alone (leveling at canon) -> flat, leveling pins it
# both bands (leveling_tolerance, feast_tolerance) -> gini
both = {"lt1,ft1": (1.0, 0.303), "lt1,ft2": (2.0, 0.384), "lt1,ft3": (3.0, 0.382), "lt2,ft2": (2.0, 0.442)}

BHM = 0.36
CANON = 0.174

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))

# Panel A: each leveler alone is a ceiling
ax[0].axhline(BHM, ls="--", c="crimson", lw=1.3, label="BHM 2009 target 0.36")
ax[0].axhline(CANON, ls=":", c="0.5", lw=1.2, label="canon 0.174")
ax[0].plot(lt, lev_feaston, "o-", c="#1f77b4", label="leveling band, feast ON")
ax[0].plot(ft, feast_only, "s-", c="#2ca02c", label="feast band, leveling ON (canon)")
ax[0].plot(lt_nf, lev_feastoff, "^-", c="#9467bd", label="leveling band, feast OFF")
ax[0].set_xlabel("tolerance band width")
ax[0].set_ylabel("material Gini (3-world panel)")
ax[0].set_title("A. Each leveler is a ceiling on its own\n(one band open, the other still pins to the mean)")
ax[0].legend(fontsize=8, loc="center right")
ax[0].set_ylim(0.10, 0.65)
ax[0].grid(alpha=0.3)

# Panel B: both bands together, feast kept ON, reach the target
xs = [0.0, 1.0, 2.0, 3.0, 4.0]
# a monotone read of the joint dial: canon(0,0)=0.174; (lt1,ft1)=0.303; (lt1,ft2)=0.384; (lt1,ft3)=0.382; (lt2,ft2)=0.442
joint_x = [0.0, 2.0, 3.0, 4.0, 4.0]  # sum of the two band widths as an ordering axis
joint_y = [0.174, 0.303, 0.384, 0.382, 0.442]
joint_lbl = ["canon", "lt1+ft1", "lt1+ft2", "lt1+ft3", "lt2+ft2"]
ax[1].axhline(BHM, ls="--", c="crimson", lw=1.3, label="BHM 2009 target 0.36")
ax[1].axhspan(0.33, 0.39, color="crimson", alpha=0.08)
ax[1].plot(joint_x, joint_y, "o-", c="#d62728", lw=2)
for x, y, l in zip(joint_x, joint_y, joint_lbl):
    ax[1].annotate(l, (x, y), textcoords="offset points", xytext=(6, -10), fontsize=8)
ax[1].set_xlabel("combined band width (leveling + feast tolerance)")
ax[1].set_ylabel("material Gini")
ax[1].set_title("B. Both bands open, FEAST KEPT ON (canon 0.25)\nreaches 0.36-0.38; guardrails + tier-11 intact")
ax[1].legend(fontsize=8, loc="upper left")
ax[1].set_ylim(0.10, 0.50)
ax[1].grid(alpha=0.3)

fig.suptitle("R-106 Add.86 — the tolerance band converts the bang-bang levelers to a graded dial (temperate, concentrators on)",
             fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_gini_band.png", dpi=110)
print("wrote bp_gini_band.png")
