"""Arc-closer: two spatial levers, one adaptive equilibrium. e0 by intervention, per biome.

canon vs +hunger_dispersal (bp_disperse.log) vs +intake_mobility (bp_intake.log). Shows nothing lifts savanna,
hunger_dispersal breaks temperate, intake is inert."""
import os
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}
RE_D = re.compile(r"(\w+) w\d+a\d+: e0 ([\d.]+)->([\d.]+) surv15 ([\d.]+)->([\d.]+) dens [\d.]+->[\d.]+ "
                  r"spatial ([\d.]+)->([\d.]+)")


def parse(logname, clim):
    off_e0, on_e0, off_sp, on_sp = [], [], [], []
    for ln in open(os.path.join(SP, logname), encoding="utf-8"):
        m = RE_D.match(ln.strip())
        if m and m.group(1) == clim:
            off_e0.append(float(m.group(2))); on_e0.append(float(m.group(3)))
            off_sp.append(float(m.group(6))); on_sp.append(float(m.group(7)))
    return list(map(np.array, (off_e0, on_e0, off_sp, on_sp)))


def mse(v):
    return v.mean(), (v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)


def main():
    biomes = ["temperate", "savanna"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("R-106 — two spatial levers, one adaptive equilibrium: nothing lifts savanna, and forced dispersal "
                 "only breaks temperate\n(canon vs the two built movement flags, 600 agents, period e0 400-800, "
                 "3-world panel, mean +/- SE)", fontsize=10, fontweight="bold")
    labels = ["canon\n(npp)", "+hunger\ndispersal", "+intake\nmobility"]
    for bi, b in enumerate(biomes):
        a = ax[bi]
        off_e0, on_e0_disp, _, _ = parse("bp_disperse.log", b)
        _, on_e0_int, _, _ = parse("bp_intake.log", b)
        means = [mse(off_e0), mse(on_e0_disp), mse(on_e0_int)]
        xs = np.arange(3)
        cols = ["#999999", COL[b], COL[b]]
        hatch = [None, "//", None]
        for i in range(3):
            a.bar(xs[i], means[i][0], yerr=means[i][1], capsize=4, color=cols[i], hatch=hatch[i],
                  edgecolor="white")
            a.text(xs[i], means[i][0] + means[i][1] + 0.6, f"{means[i][0]:.1f}", ha="center", fontsize=9)
        a.set_xticks(xs); a.set_xticklabels(labels, fontsize=8.5)
        a.set_ylabel("life expectancy e0 (yr)")
        a.set_ylim(0, 42)
        if b == "temperate":
            a.axhline(36.6, color="k", lw=0.9, ls=":"); a.text(2.4, 37.2, "Ache forest anchor 36.6",
                                                              fontsize=7.5, ha="right")
            a.set_title("(a) temperate — at anchor; hunger dispersal CRASHES it", fontsize=9.5)
        else:
            a.axhspan(21, 37, color="grey", alpha=0.12)
            a.text(2.4, 21.6, "ethnographic forager e0 range 21-37", fontsize=7.5, ha="right")
            a.set_title("(b) savanna — in-range; NO lever lifts it", fontsize=9.5)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = os.path.join(SP, "bp_arc_close.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
