"""Tier-10 is BIMODAL: material Gini plateaus ~0.2 for any nonzero leveling/feast, then cliffs to 0.78 when both
are fully off. 0.36 has no grounded stable landing. Values from the calibration logs (3-world temperate means)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
# ordered by "levelers removed": (label, material Gini)
LAD = [
    ("canon\n(no concentrators)", 0.174),
    ("+concentrators\nlevel 0.79, feast 0.25", 0.171),
    ("level 0.20\nfeast 0.25", 0.214),
    ("level 0.20\nfeast 0.15", 0.217),
    ("level 0.20\nfeast 0.05", 0.221),
    ("level 0.00\nfeast 0.25", 0.264),
    ("level OFF\nfeast OFF", 0.778),
]
GUARD = {  # adoptable partial-fix point (concentrators + level 0.20 + feast 0.15) vs canon
    "canon":       dict(gini=0.174, e0=36.2, frac_child=0.37, pop=1354, pct_strat=0.66),
    "partial_fix": dict(gini=0.217, e0=34.5, frac_child=0.37, pop=1237, pct_strat=0.68),
}
ANCHOR = 0.36


def main():
    fig, (ax, axg) = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [3, 2]})
    fig.suptitle("R-106 tier-10 — material Gini is BIMODAL: a ~0.2 egalitarian plateau, then a cliff to 0.78; "
                 "0.36 has no grounded landing\n(capture 0.75 + heir_by_status; canon 600 agents, 3-world panel)",
                 fontsize=10, fontweight="bold")
    x = np.arange(len(LAD))
    ginis = [g for _, g in LAD]
    cols = ["#999999"] + ["#1f77b4"] * 5 + ["#d62728"]
    ax.bar(x, ginis, color=cols)
    for i, g in enumerate(ginis):
        ax.text(i, g + 0.015, f"{g:.2f}", ha="center", fontsize=8.5)
    ax.axhline(ANCHOR, color="green", lw=1.4, ls="--")
    ax.text(0.1, ANCHOR + 0.02, "BHM 0.36 — falls in the UNREACHABLE gap", color="green", fontsize=8.5)
    ax.annotate("plateau: any nonzero\nleveling/feast pins ~0.2", xy=(3, 0.22), xytext=(2.4, 0.5),
                fontsize=8, ha="center", arrowprops=dict(arrowstyle="->", color="grey"))
    ax.annotate("cliff: both OFF\n(ungrounded) -> runaway", xy=(6, 0.72), xytext=(4.6, 0.66),
                fontsize=8, ha="center", arrowprops=dict(arrowstyle="->", color="firebrick"))
    ax.set_xticks(x); ax.set_xticklabels([l for l, _ in LAD], fontsize=6.8)
    ax.set_ylabel("material Gini"); ax.set_ylim(0, 0.85)
    ax.set_title("(a) plateau ~0.2 (levelers on) -> cliff 0.78 (both off); nothing sits at 0.36", fontsize=9.2)

    # right: the adoptable partial fix (dead-knob fixes) vs canon — guardrails intact, ~40% of the gap closed
    a = axg
    keys = ["gini", "e0", "frac_child", "pct_strat"]
    labs = ["material\nGini", "e0\n(/40)", "frac\nchild", "pct\nstrat"]
    xn = np.arange(len(keys))
    cv = [GUARD["canon"]["gini"], GUARD["canon"]["e0"] / 40, GUARD["canon"]["frac_child"], GUARD["canon"]["pct_strat"]]
    pv = [GUARD["partial_fix"]["gini"], GUARD["partial_fix"]["e0"] / 40, GUARD["partial_fix"]["frac_child"], GUARD["partial_fix"]["pct_strat"]]
    a.bar(xn - 0.18, cv, width=0.36, color="#999999", label="canon")
    a.bar(xn + 0.18, pv, width=0.36, color="#1f77b4", label="dead-knob fix\n(cap+heir, levelers kept)")
    a.axhline(ANCHOR, color="green", lw=1, ls=":"); a.text(3.3, ANCHOR + 0.01, "0.36", color="green", fontsize=7.5, ha="right")
    a.set_xticks(xn); a.set_xticklabels(labs, fontsize=8)
    a.set_ylabel("value (e0 scaled /40)"); a.set_ylim(0, 1.0)
    a.set_title("(b) fixing the two dead knobs: 0.17->0.22,\nguardrails intact (still short of 0.36)", fontsize=9.2)
    a.legend(fontsize=7.5, loc="upper right")

    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = os.path.join(SP, "bp_gini_regime.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
