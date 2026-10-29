"""R-106 Add.122 figure: the pair (enable_condition_full_scale + enable_orphan_norm_by_age) on the Add.121 canon.
Top: period NON-starvation death rate by age / the de-warfared Siler schedule the canon uses, canon vs pair.
Bottom: #18-#21, canon vs pair per world, mean +/- 1 SE over 3 seeds, the G&K 2007 forager band shaded."""
import glob
import json
import math
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
EV = os.path.join(ROOT, "docs", "evidence")
a1, b1, a2, a3, b3 = 0.1611, 0.6775, 0.00813, 3.781e-5, 0.1025
h = lambda t: a1 * math.exp(-b1 * t) + a2 + a3 * math.exp(b3 * t)
H = lambda t: (a1 / b1) * (1 - math.exp(-b1 * t)) + a2 * t + (a3 / b3) * (math.exp(b3 * t) - 1)
BANDS = [(0, 1), (1, 2), (2, 5), (5, 10), (10, 15), (15, 30), (30, 45), (45, 60), (60, 75)]
W = ["temperate", "savanna", "montane"]
ARMS = {"three": ("canon (Add.121)", "#52514e"), "pair": ("+ condition + orphan-by-age", "#2a78d6")}


def siler_m(lo, hi, n=400):
    xs = [lo + (i + .5) * (hi - lo) / n for i in range(n)]
    return sum(math.exp(-H(x)) * h(x) for x in xs) / sum(math.exp(-H(x)) for x in xs)


fig, axes = plt.subplots(2, 4, figsize=(18, 8))
for j, w in enumerate(W):
    ax = axes[0, j]
    ax.axhline(1.0, color="#52514e", lw=0.9)
    for arm, (lab, col) in ARMS.items():
        runs = []
        for p in sorted(glob.glob(os.path.join(OUT, f"campaign_trajectory_s2_{w}_{arm}_s*.json"))):
            m = json.load(open(p, encoding="utf-8"))["meta"]
            F, S = m["life_table_final"], m["life_table_snap"]
            runs.append([sum((F["lt_deaths"][a] - S["lt_deaths"][a]) - (F["lt_deaths_starv"][a] - S["lt_deaths_starv"][a])
                             for a in range(lo, hi))
                         / (sum(F["lt_exposure"][a] - S["lt_exposure"][a] for a in range(lo, hi)) / 12.0)
                         / siler_m(lo, hi) for lo, hi in BANDS])
        ax.plot(range(len(BANDS)), [sum(x) / len(x) for x in zip(*runs)], "o-", color=col, lw=2.2, ms=6, label=lab)
    ax.set_xticks(range(len(BANDS)))
    ax.set_xticklabels([f"{lo}-{hi}" for lo, hi in BANDS], fontsize=8)
    ax.set_title(f"{w}: non-starvation hazard / schedule", fontsize=10)
    ax.grid(alpha=0.25)
    if j == 0:
        ax.legend(fontsize=8.5, frameon=False)
axes[0, 3].axis("off")
axes[0, 3].text(0.0, 0.5, "Top: with the pair, the hazard equals the\nschedule at every age on every world.\n\n"
                "Bottom: the pair moves #18/#19 up by ~2.2 yr\nand ~0.04; temperate ends 0.45 yr and 0.002\n"
                "over the band's top edge (the Ache).\n\n3 worlds x 3 paired seeds, 15,000 steps,\n"
                "period life table after step 7,500.", fontsize=9, va="center")
sc = {a: json.load(open(os.path.join(EV, f), encoding="utf-8"))["summary"]
      for a, f in (("three", "scorecard_add118_three.json"), ("pair", "scorecard_add122_pair.json"))}
BAND = {"#18": (21, 37), "#19": (0.45, 0.66), "#20": (28.6, 42.5), "#21": (0.26, 0.43)}
for j, lab in enumerate([k for k in sc["three"] if k.startswith(("#18", "#19", "#20", "#21"))]):
    ax = axes[1, j]
    lo, hi = BAND[lab[:3]]
    ax.axhspan(lo, hi, color="#1baf7a", alpha=0.10, zorder=0)
    for i, w in enumerate(W):
        for k, (arm, (alab, col)) in enumerate(ARMS.items()):
            c = sc[arm][lab][w]
            ax.errorbar(i + (k - 0.5) * 0.25, c["mean"], yerr=st.stdev(c["values"]) / 3 ** 0.5, fmt="o", ms=6,
                        color=col, capsize=2, lw=1.5, label=alab if i == 0 else None)
    ax.set_xticks(range(3))
    ax.set_xticklabels(W, fontsize=9)
    ax.set_title(lab, fontsize=9.5)
    ax.grid(axis="y", alpha=0.25)
fig.suptitle("R-106 Add.122 - the condition fix + the per-age orphan divisor, as a pair, on the Add.121 canon", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.95))
png = os.path.join(EV, "add122_pair.png")
fig.savefig(png, dpi=120)
print("wrote", png)
