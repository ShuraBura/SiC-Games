"""Plot the reach/perception/pull mechanism of the packing paradox."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}


def main():
    biomes = ["temperate", "savanna"]
    d = {b: dict(np.load(os.path.join(SP, f"reach_arr_{b}.npz"))) for b in biomes}

    fig, ax = plt.subplots(2, 2, figsize=(12.5, 9))
    fig.suptitle("R-106 — the empty land goes unused for DIFFERENT reasons by biome: temperate = PULL, savanna = REACH\n"
                 "(canon, bp OFF, 600 agents, equilibrium steps 740-800, 3-world panel; ADULT food-short, full-eta)",
                 fontsize=10.5, fontweight="bold")

    # (a) per-step displacement — how far an agent actually moves.
    a = ax[0, 0]
    for b in biomes:
        disp = d[b]["disp"]
        a.hist(disp, bins=np.arange(-0.5, 10.5, 1), alpha=0.5, color=COL[b], density=True,
               label=f"{b} (median {np.median(disp):.0f}, stay-put {(disp==0).mean():.0%})")
    a.set_xlabel("cells moved per step (Chebyshev)")
    a.set_ylabel("density (agent-steps)")
    a.set_title("(a) agents move ~1 cell per step — no residential relocation", fontsize=9.5)
    a.legend(fontsize=8)

    # (b) adult-short agents' distance to the nearest EMPTY feeding cell, vs the realized 1-step reach.
    a = ax[0, 1]
    for b in biomes:
        sd = d[b]["short_dist"]
        sd = sd[sd < 1e8]
        a.hist(sd, bins=np.arange(-0.5, 12.5, 1), alpha=0.5, color=COL[b], density=True,
               label=f"{b} (median {np.median(sd):.0f})")
    reach = max(int(np.percentile(d["savanna"]["disp"], 90)), 1)
    a.axvline(reach + 0.5, color="k", lw=1.0, ls="--")
    a.text(reach + 0.7, a.get_ylim()[1] * 0.9, "1-step reach", fontsize=7.5)
    a.set_xlabel("distance to nearest empty feeding cell (cells)")
    a.set_ylabel("density (adult-short agents)")
    a.set_title("(b) temperate: escape is ADJACENT; savanna: escape is ~5 cells away", fontsize=9.5)
    a.legend(fontsize=8)

    # (c) fraction of adult-short with a feeding cell WITHIN reach (perception/pull) vs beyond (reach).
    a = ax[1, 0]
    x = np.arange(len(biomes))
    within = [d[b]["short_reachable"].mean() for b in biomes]
    verdict = {"temperate": "PULL\n(escape reachable,\nbut agent stays)", "savanna": "REACH\n(escape too far)"}
    a.bar(x, within, color=[COL[b] for b in biomes])
    for i, b in enumerate(biomes):
        a.text(i, within[i] + 0.03, f"{within[i]:.0%} within reach", ha="center", fontsize=9)
        a.text(i, within[i] / 2, verdict[b], ha="center", va="center", fontsize=9,
               color="white", fontweight="bold")
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("fraction of adult-short with escape within reach")
    a.set_ylim(0, 1.1)
    a.set_title("(c) temperate escapes ARE reachable (so PULL); savanna's are not (REACH)", fontsize=9.5)

    # (d) eta of adult-short agents — they are full-efficiency, so moving (not provisioning) is their fix.
    a = ax[1, 1]
    for b in biomes:
        se = d[b]["short_eta"]
        a.hist(se, bins=np.linspace(0, 1.2, 25), alpha=0.5, color=COL[b], density=True,
               label=f"{b} (median {np.median(se):.2f})")
    a.axvline(0.95, color="k", lw=0.8, ls=":")
    a.text(0.5, a.get_ylim()[1] * 0.9, "fed-adult eta ~0.95", fontsize=7.5)
    a.set_xlabel("eta (foraging efficiency) of adult-short agents")
    a.set_ylabel("density")
    a.set_title("(d) these are full-eta adults — spatially trapped, not inefficient", fontsize=9.5)
    a.legend(fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(SP, "bp_reach_diagnosis.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
