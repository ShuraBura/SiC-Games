"""Plot the R-106 food-economy carrying-capacity diagnosis.

Finding (canon, bp OFF, biome_seasonality ON, 600 agents, steps 400-800, 3-world panel):
  The carrying-capacity shortfall is the PACKING PARADOX, not seasonality or food quantity. The population
  occupies only ~14% of the food-bearing land and clusters within it: the median occupied cell sits at ~12-19%
  of its Tallavaara capacity while the top decile is packed to/over capacity, and agents STARVE in those
  clusters (28-52% of deaths) while 86% of the food-bearing patch is empty. Density holds at 4-10% of the
  Tallavaara anchor. Savanna is worse (denser clustering at water / dry-season resources). The lever is spatial
  dispersal/mobility, not the food base.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}


def main():
    biomes = ["temperate", "savanna"]
    d = {b: dict(np.load(os.path.join(SP, f"fc_arr_{b}.npz"))) for b in biomes}
    x = np.arange(len(biomes))

    fig, ax = plt.subplots(2, 2, figsize=(12.5, 9))
    fig.suptitle("R-106 — the carrying-capacity shortfall is the PACKING PARADOX (a spatial-dispersal failure), "
                 "not seasonality or food quantity\n"
                 "(canon, biome_seasonality ON, 600 agents, steps 400-800, 3-world panel)",
                 fontsize=10.5, fontweight="bold")

    # (a) headline: density/anchor and land actually used, per biome.
    a = ax[0, 0]
    dens = [d[b]["density_ratio"][0] for b in biomes]
    dens_e = [d[b]["density_ratio"][1] for b in biomes]
    spat = [d[b]["spatial_use"][0] for b in biomes]
    spat_e = [d[b]["spatial_use"][1] for b in biomes]
    a.bar(x - 0.18, dens, width=0.36, yerr=dens_e, capsize=4, color=[COL[b] for b in biomes],
          label="pop / Tallavaara anchor")
    a.bar(x + 0.18, spat, width=0.36, yerr=spat_e, capsize=4, color=[COL[b] for b in biomes], alpha=0.45,
          label="fraction of food-bearing land occupied")
    for i in range(len(biomes)):
        a.text(i - 0.18, dens[i] + 0.008, f"{dens[i]:.0%}", ha="center", fontsize=8.5)
        a.text(i + 0.18, spat[i] + 0.008, f"{spat[i]:.0%}", ha="center", fontsize=8.5)
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("fraction")
    a.set_title("(a) the population uses only ~14% of the food-bearing land", fontsize=9.5)
    a.legend(fontsize=8, loc="upper right")
    a.text(0.5, 0.60, "anchor = aquatic-inflated patch ceiling (overstates the gap);\n"
           "ethnographic /km2 grounding: temperate ~74%, savanna ~46%",
           transform=a.transAxes, va="top", ha="center", fontsize=7.2, style="italic")

    # (b) THE PACKING SKEW: per-cell occupancy / capacity. Most cells near-empty, a tail packed past 1.0.
    a = ax[0, 1]
    for b in biomes:
        f = d[b]["fills"]
        f = f[f <= 3.0]
        a.hist(f, bins=np.linspace(0, 3, 46), alpha=0.5, color=COL[b], density=True,
               label=f"{b} (median {np.median(d[b]['fills']):.2f})")
    a.axvline(1.0, color="k", lw=1.0, ls="--")
    a.text(1.03, a.get_ylim()[1] * 0.9, "cell at Tallavaara capacity", fontsize=7.5)
    a.set_xlabel("occupancy / cell Tallavaara capacity")
    a.set_ylabel("density (occupied cells)")
    a.set_title("(b) cells are either near-empty or packed past capacity", fontsize=9.5)
    a.legend(fontsize=8)

    # (c) starvation share of deaths — high despite empty land = access failure, not senescence.
    a = ax[1, 0]
    sf = [d[b]["starv_frac"][0] for b in biomes]
    sfe = [d[b]["starv_frac"][1] for b in biomes]
    a.bar(x, sf, yerr=sfe, capsize=4, color=[COL[b] for b in biomes])
    for i in range(len(biomes)):
        a.text(i, sf[i] + 0.02, f"{sf[i]:.0%}", ha="center", fontsize=9)
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("starvation share of all deaths")
    a.set_ylim(0, 0.7)
    a.set_title("(c) starvation dominates deaths while 86% of food land is empty", fontsize=9.5)

    # (d) body-condition distribution: the well-fed cluster + the starving tail (below the floor).
    a = ax[1, 1]
    for b in biomes:
        c = d[b]["conds"]
        c = c[c <= 1.2]
        a.hist(c, bins=np.linspace(0, 1.2, 61), alpha=0.5, color=COL[b],
               label=f"{b} (mean {d[b]['cond_mean'][0]:.2f})")
    a.axvline(0.42, color="k", lw=1.0, ls="--")
    a.text(0.44, a.get_ylim()[1] * 0.9, "~0.42 food margin", fontsize=7.5)
    a.set_xlabel("body condition (reserve / cap)")
    a.set_ylabel("living agents (count)")
    a.set_title("(d) survivors are pinned at the food margin, though 86% of land is empty", fontsize=9.5)
    a.legend(fontsize=8, loc="upper right")

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(SP, "bp_foodchain_diagnosis.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
