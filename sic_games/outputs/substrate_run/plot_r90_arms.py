"""R-90 two-arm comparison plot: control (branching OFF) vs branching (rate 0.03), campaign scale.

Both arms 3000 steps / 3000 founders / elite stack ON. The control MUST reproduce the R-89 collapse
(n_lineages -> 5, reversions frozen) or no verdict may be read off the comparison (D1).
Targets/thresholds drawn on the same axes as the data (D11).
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARMS = [("campaign_trajectory_r90_ctrl.json", "control (branching OFF)", "tab:red"),
        ("campaign_trajectory_r90_branch.json", "branching (rate 0.03)", "tab:blue")]
HILL_LPB = 7.0          # Hill 2011, FILED: ~7 lineages per band
HILL_DOM = 0.38         # Hill 2011, FILED: dominant-lineage share within a band

data = {}
for path, label, colour in ARMS:
    with open(path) as f:
        data[label] = (json.load(f)["traj"], colour)

fig, axes = plt.subplots(3, 2, figsize=(14, 11))

SKIP = 100      # drop the founding transient: at step 1 everyone sits in 2 bands, so lineages/band reads
                # ~1450 and squashes every later value into the axis floor. Same scaling trap as the R-89 plot.

def panel(ax, key, title, ylabel, logy=False, hline=None, hlabel=None, skip=0):
    for label, (traj, colour) in data.items():
        xs = [r["step"] for r in traj if r.get(key) is not None and r["step"] >= skip]
        ys = [r[key] for r in traj if r.get(key) is not None and r["step"] >= skip]
        ax.plot(xs, ys, color=colour, label=label, lw=1.4)
    if hline is not None:
        ax.axhline(hline, color="k", ls=":", lw=1.2, label=hlabel)
    if logy:
        ax.set_yscale("log")
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=8)

panel(axes[0][0], "n_lineages", "Lineage count — the absorbing collapse and whether branching halts it",
      "n_lineages (log)", logy=True)
axes[0][0].axhline(5, color="tab:red", ls="--", lw=0.9, alpha=0.6, label="R-89 floor = 5")
axes[0][0].legend(fontsize=7)

panel(axes[0][1], "lineages_per_band", f"Per-band diversity vs the FILED Hill 2011 target (from step {SKIP})",
      "lineages / band", hline=HILL_LPB, hlabel="Hill 2011 target ~7", skip=SKIP)
axes[0][1].legend(fontsize=7)

panel(axes[1][0], "ascribed_frac", "Ascription — 1.0 means no commoner left anywhere (the trap)",
      "ascribed_frac")
axes[1][0].axhline(1.0, color="k", ls="--", lw=0.9, alpha=0.5, label="saturation = trap")
axes[1][0].set_ylim(-0.05, 1.08)
axes[1][0].legend(fontsize=7)

panel(axes[1][1], "cum_reversions", "Cumulative gumsa->gumlao reversions — FLAT means the elite layer is frozen",
      "cum. reversions")
axes[1][1].legend(fontsize=7)

panel(axes[2][0], "lin_top_share", "Largest lineage's share — NB unit: this is top-1, Yan 2014 is top-3 combined",
      "top_share")
axes[2][0].legend(fontsize=7)
axes[2][0].set_xlabel("step (yr)", fontsize=9)

panel(axes[2][1], "eff_lineages", f"EFFECTIVE lineages (inverse-Simpson) — the measure that matters (from step {SKIP})",
      "eff_lineages (log)", logy=True, skip=SKIP)
axes[2][1].legend(fontsize=7)
axes[2][1].set_xlabel("step (yr)", fontsize=9)

fig.suptitle("R-90: lineage branching at campaign scale (3000 founders x 3000 steps, elite stack ON)\n"
             "control must reproduce the R-89 collapse for the comparison to be readable",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("plots/r90_arms.png", dpi=130)
print("wrote plots/r90_arms.png")

# ---- final-state summary, both arms, computed the same way for each
print(f"\n{'metric':>22} | {'control':>12} | {'branch 0.03':>12}")
for key in ("n_lineages", "lineages_per_band", "dom_lineage_share", "lin_top_share",
            "eff_lineages", "ascribed_frac", "cum_reversions", "pct_stratified", "pop"):
    vals = []
    for label, (traj, _) in data.items():
        vals.append(traj[-1].get(key))
    print(f"{key:>22} | {str(vals[0]):>12} | {str(vals[1]):>12}")

# did reversions still fire in the last third? (the trap test)
print("\nreversions in final third (trap test — 0 means frozen):")
for label, (traj, _) in data.items():
    cut = traj[-1]["step"] * 2 // 3
    late = [r for r in traj if r["step"] >= cut]
    d = late[-1].get("cum_reversions", 0) - late[0].get("cum_reversions", 0)
    print(f"  {label:>26}: {d}")
