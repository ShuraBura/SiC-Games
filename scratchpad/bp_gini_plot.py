"""Tier-10 material Gini: status concentrates but material does not follow it.

Means from bp_gini.log (3-world panel). Anchor BHM 2009 material Gini 0.36."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}
D = {
    "temperate": dict(mat=0.174, within=0.123, between=0.102, top10=0.153, corr=0.211, cred=0.359,
                      mat_e=0.030, corr_e=0.059, cred_e=0.021),
    "savanna":   dict(mat=0.175, within=0.159, between=0.059, top10=0.150, corr=0.170, cred=0.318,
                      mat_e=0.034, corr_e=0.115, cred_e=0.021),
}
ANCHOR = 0.36
biomes = ["temperate", "savanna"]


def main():
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.8))
    fig.suptitle("R-106 tier-10 — status concentrates to the anchor, but material does NOT follow it: "
                 "a broken status->material coupling\n(canon, 600 agents, step 800, 3-world panel; "
                 "anchor BHM 2009 material Gini 0.36)", fontsize=10.5, fontweight="bold")
    x = np.arange(len(biomes))

    # (a) material Gini decomposition vs anchor
    a = ax[0]
    for i, b in enumerate(biomes):
        a.bar(i - 0.25, D[b]["mat"], width=0.25, yerr=D[b]["mat_e"], capsize=3, color=COL[b], label="total" if i == 0 else None)
        a.bar(i, D[b]["within"], width=0.25, color=COL[b], alpha=0.6, label="within-band" if i == 0 else None)
        a.bar(i + 0.25, D[b]["between"], width=0.25, color=COL[b], alpha=0.3, label="between-band" if i == 0 else None)
    a.axhline(ANCHOR, color="green", lw=1.2, ls=":"); a.text(1.4, ANCHOR + 0.008, "BHM 0.36", color="green", fontsize=8, ha="right")
    a.set_xticks(x); a.set_xticklabels(biomes); a.set_ylabel("material Gini"); a.set_ylim(0, 0.42)
    a.set_title("(a) material Gini 0.17 << 0.36; within ~ between", fontsize=9.5)
    a.legend(fontsize=8)

    # (b) THE GAP: cred (status) Gini vs material Gini
    a = ax[1]
    for i, b in enumerate(biomes):
        a.bar(i - 0.18, D[b]["cred"], width=0.36, yerr=D[b]["cred_e"], capsize=3, color=COL[b], alpha=0.55, label="cred (status) Gini" if i == 0 else None)
        a.bar(i + 0.18, D[b]["mat"], width=0.36, yerr=D[b]["mat_e"], capsize=3, color=COL[b], label="material Gini" if i == 0 else None)
        a.annotate("", xy=(i + 0.18, D[b]["mat"]), xytext=(i - 0.18, D[b]["cred"]),
                   arrowprops=dict(arrowstyle="->", color="firebrick", lw=1.5))
        a.text(i, (D[b]["cred"] + D[b]["mat"]) / 2 + 0.02, "status does\nNOT buy\nmaterial", ha="center",
               fontsize=7.5, color="firebrick")
    a.axhline(ANCHOR, color="green", lw=1.2, ls=":"); a.text(1.4, ANCHOR + 0.008, "BHM 0.36", color="green", fontsize=8, ha="right")
    a.set_xticks(x); a.set_xticklabels(biomes); a.set_ylabel("Gini"); a.set_ylim(0, 0.45)
    a.set_title("(b) status Gini AT the anchor; material falls short", fontsize=9.5)
    a.legend(fontsize=8, loc="upper right")

    # (c) the coupling: corr(cred, material), weak vs the R-82 "strongly positive" target
    a = ax[2]
    for i, b in enumerate(biomes):
        a.bar(i, D[b]["corr"], yerr=D[b]["corr_e"], capsize=4, color=COL[b])
        a.text(i, D[b]["corr"] + D[b]["corr_e"] + 0.02, f"{D[b]['corr']:.2f}", ha="center", fontsize=9)
    a.axhspan(0.5, 1.0, color="green", alpha=0.10)
    a.text(1.4, 0.62, "R-82 target:\nstrongly positive", fontsize=7.5, ha="right", color="green")
    a.set_xticks(x); a.set_xticklabels(biomes); a.set_ylabel("corr(cred, material)"); a.set_ylim(0, 1.0)
    a.set_title("(c) status->material coupling is weak (~0.2)", fontsize=9.5)

    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = os.path.join(SP, "bp_gini_diagnosis.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
