"""R-89 -- plot the ascription-saturation trap directly from the T-9 stratified pilot's logged trajectory.
One-off diagnostic script, not part of the test suite."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("campaign_trajectory_t9_stratified.json") as f:
    traj = json.load(f)["traj"]

step = [r["step"] for r in traj]
asc = [r["ascribed_frac"] for r in traj]
gumsa = [r["frac_gumsa"] for r in traj]
giniC = [r["gini_cred"] for r in traj]
eff = [r["eff_lineages"] for r in traj]
top = [r["lin_top_share"] for r in traj]
nlin = [r["n_lineages"] for r in traj]

TRAP_STEP = 2625

fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

ax = axes[0]
ax.plot(step, asc, label="ascribed_frac (pop-weighted)", color="tab:red")
ax.plot(step, gumsa, label="frac_gumsa (band-weighted)", color="tab:orange", alpha=0.8)
ax.axvline(TRAP_STEP, color="k", ls="--", lw=1, label=f"first full saturation (step {TRAP_STEP})")
ax.set_ylabel("fraction")
ax.set_title("R-89: the delegitimation trap -- T-9 stratified pilot, 4000 steps / 3000 founders")
ax.legend(loc="lower right", fontsize=8)
ax.set_ylim(-0.05, 1.05)

ax = axes[1]
ax.plot(step, giniC, color="tab:purple")
ax.axvline(TRAP_STEP, color="k", ls="--", lw=1)
ax.set_ylabel("gini_cred")
ax.set_yscale("log")

ax = axes[2]
ax.plot(step, eff, color="tab:blue", label="eff_lineages")
ax.axvline(TRAP_STEP, color="k", ls="--", lw=1)
ax.set_ylabel("eff_lineages (log)")
ax.set_yscale("log")
ax2 = ax.twinx()
ax2.plot(step, top, color="tab:green", label="lin_top_share")
ax2.set_ylabel("lin_top_share", color="tab:green")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=8)

ax = axes[3]
ax.plot(step, nlin, color="tab:brown")
ax.axvline(TRAP_STEP, color="k", ls="--", lw=1)
ax.set_ylabel("n_lineages (log)")
ax.set_yscale("log")
ax.set_xlabel("step (yr)")

fig.tight_layout()
fig.savefig("plots/r89_ascription_trap.png", dpi=130)
print("wrote plots/r89_ascription_trap.png")

# Zoomed companion: steps 2000-4000 only, linear scale, so the "no visible shift at the
# trap" claim (eff_lineages/top_share/giniC before vs after step 2625) is directly checkable.
lo = next(i for i, s in enumerate(step) if s >= 2000)
fig2, axes2 = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
ax = axes2[0]
ax.plot(step[lo:], asc[lo:], color="tab:red", label="ascribed_frac")
ax.plot(step[lo:], gumsa[lo:], color="tab:orange", label="frac_gumsa")
ax.axvline(TRAP_STEP, color="k", ls="--", lw=1)
ax.set_ylabel("fraction")
ax.set_title("R-89 zoom (step 2000-4000): eff_lineages/top_share show no shift where asc/gumsa lock to 1.0")
ax.legend(fontsize=8)

ax = axes2[1]
ax.plot(step[lo:], eff[lo:], color="tab:blue", label="eff_lineages")
ax.axvline(TRAP_STEP, color="k", ls="--", lw=1)
ax.set_ylabel("eff_lineages")
ax2 = ax.twinx()
ax2.plot(step[lo:], top[lo:], color="tab:green", label="lin_top_share")
ax2.set_ylabel("lin_top_share", color="tab:green")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=8)

ax = axes2[2]
ax.plot(step[lo:], giniC[lo:], color="tab:purple")
ax.axvline(TRAP_STEP, color="k", ls="--", lw=1)
ax.set_ylabel("gini_cred")
ax.set_xlabel("step (yr)")

fig2.tight_layout()
fig2.savefig("plots/r89_ascription_trap_zoom.png", dpi=130)
print("wrote plots/r89_ascription_trap_zoom.png")
