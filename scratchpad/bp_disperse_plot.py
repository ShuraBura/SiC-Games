"""Plot intervention test #1: enable_hunger_dispersal unpacks the population but hurts temperate e0.

Parses bp_disperse.log (per-world OFF->ON values)."""
import os
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}
LINE = re.compile(r"(\w+) w\d+a\d+: e0 ([\d.]+)->([\d.]+) surv15 ([\d.]+)->([\d.]+) "
                  r"dens [\d.]+->[\d.]+ spatial ([\d.]+)->([\d.]+)")


def parse(clim):
    o = {"e0": [], "s15": [], "sp": []}
    n = {"e0": [], "s15": [], "sp": []}
    for ln in open(os.path.join(SP, "bp_disperse.log"), encoding="utf-8"):
        m = LINE.match(ln.strip())
        if m and m.group(1) == clim:
            o["e0"].append(float(m.group(2))); n["e0"].append(float(m.group(3)))
            o["s15"].append(float(m.group(4))); n["s15"].append(float(m.group(5)))
            o["sp"].append(float(m.group(6))); n["sp"].append(float(m.group(7)))
    return {k: np.array(v) for k, v in o.items()}, {k: np.array(v) for k, v in n.items()}


def mse(v):
    return v.mean(), (v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)


def main():
    biomes = ["temperate", "savanna"]
    data = {b: parse(b) for b in biomes}
    x = np.arange(len(biomes))

    fig, ax = plt.subplots(1, 3, figsize=(14, 4.6))
    fig.suptitle("R-106 intervention #1 — enable_hunger_dispersal UNPACKS the population but CRASHES temperate e0: "
                 "the clusters are adaptive buffers\n(canon vs flag ON, 600 agents, period LT 400-800, "
                 "3-world panel, mean +/- SE)", fontsize=10, fontweight="bold")

    def panel(a, key, title, ylab):
        for i, b in enumerate(biomes):
            o, n = data[b]
            mo, so = mse(o[key]); mn, sn = mse(n[key])
            a.bar(i - 0.18, mo, width=0.36, yerr=so, capsize=4, color="#999999", label="OFF (canon)" if i == 0 else None)
            a.bar(i + 0.18, mn, width=0.36, yerr=sn, capsize=4, color=[COL[b]], label="ON" if i == 0 else None)
            d = n[key] - o[key]
            md = d.mean(); sd = d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else 0.0
            z = md / sd if sd > 0 else 0.0
            col = "firebrick" if (key != "sp" and md < 0 and abs(z) > 1.5) else ("green" if md > 0 and abs(z) > 1.5 else "k")
            a.text(i, max(mo, mn) + max(so, sn) + (0.5 if key == "e0" else 0.02),
                   f"{md:+.2f}\n(z={z:.1f})", ha="center", fontsize=8.5, color=col)
        a.set_xticks(x); a.set_xticklabels(biomes)
        a.set_ylabel(ylab); a.set_title(title, fontsize=9.5)

    panel(ax[0], "sp", "(a) spatial use — the flag DOES unpack them", "fraction of land occupied")
    ax[0].legend(fontsize=8)
    panel(ax[1], "e0", "(b) e0 — but temperate CRASHES (clusters were buffering)", "life expectancy e0 (yr)")
    ax[1].axhline(36.6, color="k", lw=0.8, ls=":"); ax[1].text(1.4, 37.0, "Ache anchor 36.6", fontsize=7.5, ha="right")
    panel(ax[2], "s15", "(c) survival-to-15 — falls in temperate too", "survival to age 15")

    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = os.path.join(SP, "bp_disperse_diagnosis.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
