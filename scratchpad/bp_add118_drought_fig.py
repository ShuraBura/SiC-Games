"""R-106 Add.118: the drought test on the canon (Add.117) and on the four-fix arm (all4), same seeds, same drought.

Top row: population, drought run / paired control run, x0.70 for 30 years (steps 9000-9360); thin = seeds, thick = mean.
Bottom row: the change (drought - control) in the crude birth rate and the crude death rate, per 1000 per year, over
the drought window, mean +/- 1 SE over 3 seeds. Reads the two summary files that bp_drought_analyse.py writes.
"""
import json
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
W = ["temperate", "savanna", "montane"]
ARMS = {"canon": ("riskvg", "", "#52514e"), "all4": ("all4", "all4_", "#2a78d6")}
ONSET, END = 9000, 9360


def traj(p):
    return {r["step"]: r["pop"] for r in json.load(open(p, encoding="utf-8"))["traj"]}


fig, axes = plt.subplots(2, 3, figsize=(17, 8.4))
for j, w in enumerate(W):
    ax = axes[0, j]
    ax.axvspan(0, (END - ONSET) / 12, color="#eda100", alpha=0.15, lw=0)
    for name, (ctl, pre, col) in ARMS.items():
        curves = []
        for s in (0, 1, 2):
            c = traj(os.path.join(OUT, f"campaign_trajectory_s2_{w}_{ctl}_s{s}.json"))
            d = traj(os.path.join(OUT, f"campaign_trajectory_dr_{pre}{w}_m070_s{s}.json"))
            steps = [k for k in sorted(d) if k >= ONSET - 600 and k in c]
            curves.append([d[k] / c[k] for k in steps])
            ax.plot([(k - ONSET) / 12 for k in steps], curves[-1], color=col, lw=0.7, alpha=0.45)
        ax.plot([(k - ONSET) / 12 for k in steps], [st.mean(v) for v in zip(*curves)], color=col, lw=2.2, label=name)
    ax.axhline(1.0, color="#52514e", lw=0.8)
    ax.set_title(f"{w}: population, drought x0.70 / control", fontsize=10)
    ax.set_xlabel("years since drought onset (shaded = drought)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, frameon=False)

S = {n: json.load(open(os.path.join(ROOT, "scratchpad", f"drought_summary{'' if n == 'canon' else '_all4'}.json"),
                       encoding="utf-8")) for n in ARMS}
for j, w in enumerate(W):
    ax = axes[1, j]
    x = 0
    ticks, labs = [], []
    for m in ("085", "070"):
        for k, key in enumerate(("births_py", "deaths_py")):
            for i, (name, (_, _, col)) in enumerate(ARMS.items()):
                v = S[name][f"{w}|{m}"]["windows"]["drought"]
                diff = [a[key] - b[key] for a, b in zip(v["drought"], v["control"]) if a and b]
                se = st.stdev(diff) / len(diff) ** 0.5
                ax.bar(x + i * 0.4, st.mean(diff), 0.38, yerr=se, color=col, capsize=2,
                       label=name if (m, key) == ("085", "births_py") else None)
            ticks.append(x + 0.2)
            labs.append(f"{'births' if key == 'births_py' else 'deaths'}\nx{int(m) / 100:.2f}")
            x += 1.2
        x += 0.4
    ax.axhline(0, color="#52514e", lw=0.8)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_ylabel("drought - control, per 1000 per yr")
    ax.set_title(f"{w}: crude rates during the drought", fontsize=10)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8, frameon=False)
fig.suptitle("R-106 Add.118 - drought on the canon vs on the four mortality fixes (3 seeds, paired controls). "
             "Births carry the contraction in both; the crude death rate goes from falling (canon) to flat or rising (all4)",
             fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.95))
png = os.path.join(ROOT, "docs", "evidence", "add118_drought_all4_vs_canon.png")
fig.savefig(png, dpi=120)
print("wrote", png)
