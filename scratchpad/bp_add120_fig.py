"""R-106 Add.120 figure: the period NON-STARVATION death rate by age divided by the Siler schedule the canon really
uses (the de-warfared ACHE_FOREST_NATURAL, e0 42.7), canon vs the four fixes, per world. Mean of 3 seeds."""
import glob
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
a1, b1, a2, a3, b3 = 0.1611, 0.6775, 0.00813, 3.781e-5, 0.1025
h = lambda t: a1 * math.exp(-b1 * t) + a2 + a3 * math.exp(b3 * t)
H = lambda t: (a1 / b1) * (1 - math.exp(-b1 * t)) + a2 * t + (a3 / b3) * (math.exp(b3 * t) - 1)
BANDS = [(0, 1), (1, 2), (2, 5), (5, 10), (10, 15), (15, 30), (30, 45), (45, 60), (60, 75)]
ARMS = {"riskvg": ("canon (Add.113)", "#52514e"), "all4": ("four fixes", "#2a78d6")}


def siler_m(lo, hi, n=400):
    xs = [lo + (i + .5) * (hi - lo) / n for i in range(n)]
    return sum(math.exp(-H(x)) * h(x) for x in xs) / sum(math.exp(-H(x)) for x in xs)


fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
for ax, w in zip(axes, ("temperate", "savanna", "montane")):
    ax.axhline(1.0, color="#52514e", lw=0.9)
    ax.axhspan(0.6, 0.72, xmin=0, xmax=0.2, color="#eda100", alpha=0.18, lw=0)
    for arm, (lab, col) in ARMS.items():
        runs = []
        for p in sorted(glob.glob(os.path.join(OUT, f"campaign_trajectory_s2_{w}_{arm}_s*.json"))):
            m = json.load(open(p, encoding="utf-8"))["meta"]
            F, S = m["life_table_final"], m["life_table_snap"]
            r = []
            for lo, hi in BANDS:
                d = sum((F["lt_deaths"][a] - S["lt_deaths"][a]) - (F["lt_deaths_starv"][a] - S["lt_deaths_starv"][a])
                        for a in range(lo, hi))
                e = sum(F["lt_exposure"][a] - S["lt_exposure"][a] for a in range(lo, hi)) / 12.0
                r.append(d / e / siler_m(lo, hi))
            runs.append(r)
            ax.plot(range(len(BANDS)), r, color=col, lw=0.7, alpha=0.4)
        ax.plot(range(len(BANDS)), [sum(x) / len(x) for x in zip(*runs)], "o-", color=col, lw=2.2, ms=6, label=lab)
    ax.set_xticks(range(len(BANDS)))
    ax.set_xticklabels([f"{lo}-{hi}" for lo, hi in BANDS], fontsize=8)
    ax.set_xlabel("age band (yr)")
    ax.set_title(w, fontsize=10.5)
    ax.grid(alpha=0.25)
axes[0].set_ylabel("non-starvation death rate / schedule")
axes[0].legend(fontsize=9, frameon=False, loc="upper right")
axes[0].text(0.05, 0.55, "orphan normalisation:\ninfants x0.66 (probe)", fontsize=8, color="#8a5a00")
fig.suptitle("R-106 Add.120 - the canon's hazard vs the schedule it uses (de-warfared Aché Siler, e0 42.7): the constant "
             "synergy doubled ages 5-15; the pooled orphan normalisation cut infants by a third", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.93))
png = os.path.join(ROOT, "docs", "evidence", "add120_hazard_vs_schedule.png")
fig.savefig(png, dpi=120)
print("wrote", png)
