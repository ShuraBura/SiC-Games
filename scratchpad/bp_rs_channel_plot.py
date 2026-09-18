"""R-106 Add.102 figure: every channel von Rueden's anchor describes fails to move the model's status->RS."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

labels = ["canon\n(m=5.0)", "m=0\nno status\nmate choice", "m=1", "m=2",
          "max_wives=1\npolygyny=0", "control for\ncondition", "control for\ncond.+wealth"]
vals = [0.157, 0.112, 0.142, 0.156, 0.171, 0.118, 0.123]
errs = [0.063, 0.008, 0.048, 0.043, 0.039, 0.075, 0.079]
kind = ["canon", "ablate", "ablate", "ablate", "ablate", "control", "control"]
col = {"canon": "#1f77b4", "ablate": "#d62728", "control": "#7f7f7f"}

fig, ax = plt.subplots(figsize=(10.5, 5.4))
ax.axhspan(0.13, 0.15, color="crimson", alpha=0.10)
ax.axhline(0.15, ls="--", c="crimson", lw=1.5, label="von Rueden monogamous ~0.15")
ax.axhline(0.19, ls=":", c="darkred", lw=1.2, label="cross-system 0.19 (polygyny-inflated)")
x = np.arange(len(vals))
ax.bar(x, vals, yerr=errs, capsize=4, color=[col[k] for k in kind])
for i, v in enumerate(vals):
    ax.text(i, v + errs[i] + 0.006, f"{v:.3f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("partial corr(prowess, offspring | age)")
ax.set_title("R-106 Add.102 — the #11 status->RS survives every ablation of its supposed mechanism\n"
             "red = channel ablated (mate choice, polygyny); grey = confound controlled. Nothing collapses it.")
ax.legend(fontsize=8, loc="upper right")
ax.set_ylim(0, 0.26)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_rs_channel.png", dpi=110)
print("wrote bp_rs_channel.png")
