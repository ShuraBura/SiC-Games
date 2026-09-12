"""Tier-3 age-structure: markers vs their forager anchor bands (normalized forest plot).

Values are the 3-world means +/- SE from bp_agestruct.log (corrected CBR/r). Anchor bands from DEMOG_ANCHORS.
Each marker is normalized x=(val-lo)/(hi-lo) so the anchor band maps to [0,1]; a point in [0,1] is in-anchor.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}

# marker: (lo, hi anchor), then per-biome (mean, se)  -- from bp_agestruct.log
M = [
    ("frac_child",   (0.287, 0.454), {"temperate": (0.37, 0.02), "savanna": (0.42, 0.02)}),
    ("dependency",   (0.598, 0.899), {"temperate": (0.81, 0.03), "savanna": (0.95, 0.05)}),
    ("TFR",          (4.69, 8.03),   {"temperate": (5.54, 0.24), "savanna": (7.50, 0.35)}),
    ("e0",           (21.0, 37.0),   {"temperate": (36.25, 1.77), "savanna": (24.62, 2.21)}),
    ("surv_to_15",   (0.46, 0.86),   {"temperate": (0.61, 0.02), "savanna": (0.44, 0.04)}),
]
GROWTH = {"temperate": (1.16, 0.36), "savanna": (0.90, 0.49)}   # corrected r %/yr (near-stationary, iso-consistent)


def main():
    fig, (ax, axr) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [3, 1]})
    fig.suptitle("R-106 tier-3 age structure PASSES on current canon — the ladder's \"too many children\" is stale\n"
                 "(canon, 600 agents, period 400-800, 3-world panel; markers vs forager anchor bands)",
                 fontsize=11, fontweight="bold")
    ys = np.arange(len(M))[::-1]
    ax.axvspan(0, 1, color="green", alpha=0.10)
    ax.axvline(0, color="grey", lw=0.8); ax.axvline(1, color="grey", lw=0.8)
    for yi, (name, (lo, hi), vals) in zip(ys, M):
        rng = hi - lo
        for j, b in enumerate(("temperate", "savanna")):
            m, e = vals[b]
            xn = (m - lo) / rng; xe = e / rng
            off = 0.14 * (1 if b == "savanna" else -1)
            inb = 0 <= xn <= 1
            ax.errorbar(xn, yi + off, xerr=xe, fmt="o", color=COL[b], capsize=3,
                        markeredgecolor="black" if inb else "red", markeredgewidth=1.2,
                        label=b if yi == ys[0] else None)
            ax.text(xn, yi + off + 0.16, f"{m:g}", ha="center", fontsize=7.5, color=COL[b])
    ax.set_yticks(ys); ax.set_yticklabels([m[0] for m in M])
    ax.set_xlim(-0.35, 1.35)
    ax.set_xlabel("position within forager anchor band  (0 = low anchor, 1 = high anchor; green = in-band)")
    ax.set_title("(a) all temperate markers in-band; savanna 3/5 in-band, 2 marginally out (harsh-biome side)",
                 fontsize=9.5)
    ax.text(0.5, len(M) - 0.4, "IN-ANCHOR", ha="center", fontsize=8, color="green", alpha=0.7)
    ax.legend(fontsize=8, loc="lower right")

    # right: growth rate — corrected r near 0, iso-growth consistent (the +5% earlier was a births double-count bug)
    x = np.arange(2)
    for i, b in enumerate(("temperate", "savanna")):
        m, e = GROWTH[b]
        axr.bar(i, m, yerr=e, capsize=4, color=COL[b])
        axr.text(i, m + e + 0.1, f"{m:.1f}", ha="center", fontsize=9)
    axr.axhspan(0, 2, color="green", alpha=0.10)
    axr.set_xticks(x); axr.set_xticklabels(["temperate", "savanna"])
    axr.set_ylabel("growth rate r (%/yr, corrected)")
    axr.set_ylim(-1, 6)
    axr.set_title("(b) near-stationary,\niso-growth consistent\n(+5% was a probe bug)", fontsize=9)

    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = os.path.join(SP, "bp_agestruct_diagnosis.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
