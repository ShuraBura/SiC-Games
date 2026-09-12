"""Plot the tier-5 band-size diagnosis: it is a spatial limit, not a cohesion-cap limit.

band_arr_<clim>.npz: sizes, thr (split_thr), coh (cohesion_frac), util (size/thr), band_med_adults."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}


def main():
    biomes = ["temperate", "savanna"]
    d = {b: dict(np.load(os.path.join(SP, f"band_arr_{b}.npz"))) for b in biomes}

    fig, ax = plt.subplots(2, 2, figsize=(12.5, 9))
    fig.suptitle("R-106 tier-5 — band size is a SPATIAL limit, not a cohesion-cap limit: bands sit far below "
                 "their fission threshold,\nand the UNSATURATED biome (savanna) has the SMALLER bands "
                 "(canon, 600 agents, steps 740-800, 3-world panel)", fontsize=10, fontweight="bold")

    # (a) size vs its own split_thr — mass below the diagonal = bands never fill their cap.
    a = ax[0, 0]
    for b in biomes:
        a.scatter(d[b]["thr"], d[b]["sizes"], s=6, alpha=0.25, color=COL[b], label=b)
    lim = 120
    a.plot([0, lim], [0, lim], "k--", lw=1, label="size = fission cap")
    a.set_xlim(0, lim); a.set_ylim(0, lim)
    a.set_xlabel("split_thr (this band's fission threshold)")
    a.set_ylabel("realised band size (people)")
    a.set_title("(a) bands sit FAR below the size they are allowed", fontsize=9.5)
    a.legend(fontsize=8)

    # (b) util = size/split_thr distribution, with the 1.0 (at-cap) line.
    a = ax[0, 1]
    for b in biomes:
        u = d[b]["util"]; u = u[u <= 2]
        a.hist(u, bins=np.linspace(0, 2, 41), alpha=0.5, color=COL[b], density=True,
               label=f"{b} (median {np.median(d[b]['util']):.2f})")
    a.axvline(1.0, color="k", lw=1, ls="--"); a.text(1.03, a.get_ylim()[1]*0.9, "at fission cap", fontsize=7.5)
    a.set_xlabel("band size / its fission threshold")
    a.set_ylabel("density (band-records)")
    a.set_title("(b) most bands are at 0.3-0.6 of their cap — cap does not bind", fontsize=9.5)
    a.legend(fontsize=8)

    # (c) THE NATURAL CONTROL: cohesion saturation vs band_med_adults. savanna unsaturated yet smaller.
    a = ax[1, 0]
    x = np.arange(len(biomes))
    sat = [(d[b]["coh"] >= 0.999).mean() for b in biomes]
    a.bar(x - 0.18, sat, width=0.36, color=[COL[b] for b in biomes], alpha=0.5, label="cohesion_frac saturated (frac=1.0)")
    a2 = a.twinx()
    bma = [d[b]["band_med_adults"].mean() for b in biomes]
    bma_e = [d[b]["band_med_adults"].std(ddof=1)/np.sqrt(len(d[b]["band_med_adults"])) for b in biomes]
    a2.errorbar(x + 0.18, bma, yerr=bma_e, fmt="o", color="black", capsize=4, label="band_med_adults")
    for i, b in enumerate(biomes):
        a.text(i - 0.18, sat[i] + 0.02, f"{sat[i]:.0%}", ha="center", fontsize=8.5)
        a2.text(i + 0.18, bma[i] + 1.2, f"{bma[i]:.1f}", ha="center", fontsize=8.5)
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("cohesion budget saturated (fraction)"); a2.set_ylabel("band_med_adults")
    a.set_ylim(0, 1.0); a2.set_ylim(0, 30)
    a2.axhline(28.2, color="green", lw=1, ls=":"); a2.text(1.4, 28.6, "Hill 28.2", fontsize=7.5, ha="right", color="green")
    a.set_title("(c) natural control: savanna UNSATURATED yet SMALLER -> de-saturation is not the lever", fontsize=9.2)

    # (d) composition: adults per band vs total people per band — child-heavy, and both far below Hill.
    a = ax[1, 1]
    # median total size and derived adults from the marker; use band_med_adults (npz) and median size.
    med_size = [np.median(d[b]["sizes"]) for b in biomes]
    for i, b in enumerate(biomes):
        tot = med_size[i]; adu = d[b]["band_med_adults"].mean()
        a.bar(i, tot, color=COL[b], alpha=0.4, label="total people" if i == 0 else None)
        a.bar(i, adu, color=COL[b], label="adults" if i == 0 else None)
        a.text(i, tot + 1, f"{tot:.0f} ppl", ha="center", fontsize=8.5)
        a.text(i, adu + 1, f"{adu:.0f} ad", ha="center", fontsize=8.5, color="white")
    a.axhline(28.2, color="green", lw=1, ls=":"); a.text(1.4, 29, "Hill 28.2 adults", fontsize=7.5, ha="right", color="green")
    a.axhline(73, color="grey", lw=0.8, ls=":"); a.text(1.4, 74, "~73 ppl needed for 28.2 adults", fontsize=7, ha="right")
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("people per band (median)"); a.set_ylim(0, 80)
    a.set_title("(d) child-heavy bands: ~10-12 adults inside ~20-23 people", fontsize=9.5)
    a.legend(fontsize=8, loc="upper left")

    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = os.path.join(SP, "bp_bandsize_diagnosis.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
