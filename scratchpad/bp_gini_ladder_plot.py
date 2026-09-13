"""Tier-10 material Gini: the intervention ladder brackets the BHM 0.36 anchor.

Values from bp_gini_isolate.log / _capsweep.log / _maxstack.log (3-world temperate means)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
# (label, material Gini, corr(aggr,material))
ARMS = [
    ("canon\n(cap=0, level 0.79)", 0.174, 0.02),
    ("no_leveling", 0.229, None),
    ("heir_status", 0.190, None),
    ("cap_frac=0.75\n(leveling ON)", 0.173, 0.12),
    ("cap=0.75 +\nleveling OFF", 0.246, 0.49),
    ("max_stack\n(cap+heir+no-level)", 0.778, 0.63),
]
ANCHOR = 0.36


def main():
    fig, (ax, axr) = plt.subplots(1, 2, figsize=(13.5, 5.2), gridspec_kw={"width_ratios": [3, 2]})
    fig.suptitle("R-106 tier-10 — the intervention ladder BRACKETS BHM 0.36: material Gini IS movable "
                 "(root: dead capture knob + status-blind inheritance)\n"
                 "(canon, 600 agents, step 800, 3-world temperate panel)", fontsize=10.5, fontweight="bold")

    labels = [a[0] for a in ARMS]
    ginis = [a[1] for a in ARMS]
    x = np.arange(len(ARMS))
    cols = ["#999999"] + ["#1f77b4"] * (len(ARMS) - 2) + ["#d62728"]
    ax.bar(x, ginis, color=cols)
    for i, g in enumerate(ginis):
        ax.text(i, g + 0.015, f"{g:.2f}", ha="center", fontsize=9)
    ax.axhline(ANCHOR, color="green", lw=1.4, ls="--")
    ax.text(len(ARMS) - 0.5, ANCHOR + 0.02, "BHM 0.36 (anchor)", color="green", fontsize=9, ha="right")
    ax.axhspan(0.30, 0.42, color="green", alpha=0.08)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel("material Gini"); ax.set_ylim(0, 0.85)
    ax.set_title("(a) canon far below; max_stack far above — 0.36 is reachable in between", fontsize=9.5)

    # right: corr(aggr, material) — capture only bites once leveling is off
    pts = [(a[0], a[2]) for a in ARMS if a[2] is not None]
    xr = np.arange(len(pts))
    axr.bar(xr, [p[1] for p in pts], color=["#999999", "#1f77b4", "#1f77b4", "#d62728"])
    for i, p in enumerate(pts):
        axr.text(i, p[1] + 0.02, f"{p[1]:.2f}", ha="center", fontsize=9)
    axr.set_xticks(xr); axr.set_xticklabels([p[0] for p in pts], fontsize=7.5)
    axr.set_ylabel("corr(aggrandizer, material)"); axr.set_ylim(0, 0.75)
    axr.set_title("(b) capture bites onto aggrandizers only\nonce leveling stops removing it", fontsize=9.5)

    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = os.path.join(SP, "bp_gini_ladder.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
