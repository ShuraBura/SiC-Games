"""R-89 fix validation plot: resentment/ascription trajectory from probe_r89_fix.py's saved run."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("probe_r89_fix_trajectory.json") as f:
    rows = json.load(f)

step = [r["step"] for r in rows]
asc = [r["asc"] for r in rows]
maxr = [r["max_resent"] for r in rows]
meanr = [r["mean_resent"] for r in rows]
rev_steps = [r["step"] for r in rows if r["reversions_this_step"] > 0]

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

ax = axes[0]
ax.plot(step, asc, color="tab:red")
for rs in rev_steps:
    ax.axvline(rs, color="k", ls="--", lw=1, alpha=0.7)
ax.set_ylabel("ascribed_frac (pop-weighted)")
ax.set_title("R-89 fix validation: N=500, realistic params (resent_alpha=0.001, thr=0.5, ref=10.0)\n"
             "dashed line = a reversion actually fired")
ax.set_ylim(-0.05, 1.05)

ax = axes[1]
ax.plot(step, maxr, color="tab:blue", label="max_resent (any band)")
ax.plot(step, meanr, color="tab:green", label="mean_resent (all bands)")
ax.axhline(0.5, color="gray", ls=":", lw=1, label="resent_threshold=0.5")
for rs in rev_steps:
    ax.axvline(rs, color="k", ls="--", lw=1, alpha=0.7)
ax.set_ylabel("resentment")
ax.set_xlabel("step (yr)")
ax.legend(fontsize=8)

fig.tight_layout()
fig.savefig("plots/r89_fix_validation.png", dpi=130)
print("wrote plots/r89_fix_validation.png")
