"""Add.129 figures: whole curves. Fig 1: population over the run, flag off and on, each seed. Fig 2: the shock, annual, flag on. Fig 3: the gates and the account."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
O = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
L = os.path.join(ROOT, "scratchpad", "design_logs")
EV = os.path.join(ROOT, "docs", "evidence")
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
OFF, ON, Y1, Y5 = "#6b6a63", "#2a78d6", "#eb6834", "#d03b3b"
W = ("temperate", "savanna", "montane")
S = (0, 1)
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def traj(tag):
    return json.load(open(os.path.join(O, f"campaign_trajectory{tag}.json"), encoding="utf-8"))["traj"]


def jl(pre, tag):
    return [json.loads(x) for x in open(os.path.join(L, f"{pre}{tag}.jsonl"), encoding="utf-8")]


# figure 1
fig, axs = plt.subplots(1, 3, figsize=(13, 3.9))
for ax, w in zip(axs, W):
    for fl, col, lab in (("off", OFF, "flag off (canon)"), ("on", ON, "flag on")):
        for s in S:
            t = traj(f"_vc_{w}_{fl}_c_s{s}")
            ax.plot([r["step"] / 12 for r in t], [r["pop"] for r in t], color=col, lw=1.8 if s == 0 else 1.1, alpha=0.95 if s == 0 else 0.6, label=lab if s == 0 else None)
    ax.set_title(w, loc="left", fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xlabel("Years")
    ax.set_ylim(0, None)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
axs[0].set_ylabel("Population")
axs[0].legend(frameon=False, loc="lower right", fontsize=8.5)
fig.tight_layout()
fig.savefig(os.path.join(EV, "add129_population.png"), dpi=150, facecolor="white")

# figure 2
rows = (("Population", "pop"), ("Births per year", "births"), ("Deaths aged 1-9 per year", "d19"), ("Deaths aged 15-44 per year", "d1544"), ("Store per head (steps of burn)", "store"))
fig, axs = plt.subplots(len(rows), 3, figsize=(13, 11.5), sharex=True)
for j, w in enumerate(W):
    for arm, col, lab, lw in (("c", ON, "control", 1.8), ("y1", Y1, "×0.70, 1 yr", 1.4), ("y5", Y5, "×0.70, 5 yr", 1.8)):
        sig = [jl("sig", f"_vc_{w}_on_{arm}_s{s}") for s in S]
        sto = [jl("sto", f"_vc_{w}_on_{arm}_s{s}") for s in S]
        n = (len(sig[0]) - 1) // 12
        yr = np.arange(n) + 0.5 - 3
        def ann(fn):
            return np.array([np.mean([fn(sig[k], sto[k], 12 * i, 12 * i + 12) for k in range(2)]) for i in range(n)])
        A = dict(pop=ann(lambda a, b, i, e: a[e - 1]["pop"]),
                 births=ann(lambda a, b, i, e: sum(r["births"] for r in a[i:e])),
                 d19=ann(lambda a, b, i, e: sum(a[e]["deaths"][1:10]) - sum(a[i]["deaths"][1:10])),
                 d1544=ann(lambda a, b, i, e: sum(a[e]["deaths"][15:45]) - sum(a[i]["deaths"][15:45])),
                 store=ann(lambda a, b, i, e: np.mean([r["all"]["sph_m"] for r in b[i:e]])))
        for r, (name, key) in enumerate(rows):
            axs[r, j].plot(yr, A[key], color=col, lw=lw, label=lab)
    for r, (name, key) in enumerate(rows):
        ax = axs[r, j]
        ax.axvspan(0, 5, color="#f3e7dc", lw=0, zorder=0)
        ax.grid(axis="y", color=GRID, lw=0.7)
        ax.set_axisbelow(True)
        ax.set_xlim(-3, 30)
        ax.set_ylim(0, None)
        if j == 0:
            ax.set_ylabel(name)
    axs[0, j].set_title(w, loc="left", fontsize=10.5, fontweight="bold", color=INK)
    axs[-1, j].set_xlabel("Years after the onset (shaded: the 5-year shock)")
axs[0, 0].legend(frameon=False, loc="lower right", fontsize=8.5)
fig.tight_layout()
fig.savefig(os.path.join(EV, "add129_shock.png"), dpi=150, facecolor="white")

# figure 3
E = json.load(open(os.path.join(EV, "add129_measurement.json"), encoding="utf-8"))["worlds"]
D = json.load(open(os.path.join(EV, "add129_diag.json"), encoding="utf-8"))
x = np.arange(3)
fig, axs = plt.subplots(2, 3, figsize=(13, 7.2))
panels = ((lambda d: d["pop"], "Population", None, "%.0f"), (lambda d: np.mean(d["e0s"]), "e0, period (years)", (37.0, "top of the forager band 37 (floor 21)"), "%.1f"),
          (lambda d: d["surv_to_15"], "Survival to 15, period", (0.57, "forager average 0.57 (band 0.45-0.66)"), "%.2f"),
          (lambda d: d["deaths_starv"] / d["deaths"], "Starvation share of deaths", (0.40, "stop rule 0.40"), "%.2f"))
for ax, (fn, name, ref, fm) in zip(axs.flat, panels):
    a = [fn(E[w]["off"]) for w in W]
    b = [fn(E[w]["on"]) for w in W]
    ax.bar(x - 0.19, a, 0.34, color=OFF, label="flag off")
    ax.bar(x + 0.19, b, 0.34, color=ON, label="flag on")
    for i in range(3):
        ax.annotate(fm % a[i], (i - 0.19, a[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
        ax.annotate(fm % b[i], (i + 0.19, b[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
    if ref:
        ax.axhline(ref[0], color=INK, lw=1.0)
        ax.annotate(ref[1], (2.47, ref[0]), xytext=(0, 3), textcoords="offset points", ha="right", fontsize=8.5, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(W)
    ax.set_title(name, loc="left", fontsize=10.5, fontweight="bold", color=INK)
    ax.margins(y=0.16)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
axs[0, 0].legend(frameon=False, loc="upper right", fontsize=8.5)
ax = axs[1, 1]
a = [D[w]["off"]["store"] for w in W]
b = [D[w]["on"]["store"] for w in W]
c = [D[w]["on"]["store_p10"] for w in W]
ax.bar(x - 0.27, a, 0.26, color=OFF, label="flag off, mean")
ax.bar(x, b, 0.26, color=ON, label="flag on, mean")
ax.bar(x + 0.27, c, 0.26, color="#7fb2ea", label="flag on, 10th percentile")
for i in range(3):
    for dx, v in ((-0.27, a[i]), (0, b[i]), (0.27, c[i])):
        ax.annotate(f"{v:.1f}", (i + dx, v), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
ax.set_xticks(x)
ax.set_xticklabels(W)
ax.set_title("Store per head, control (steps of burn; cap 20.8)", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, loc="upper right", fontsize=8.5, ncol=1)
ax.set_ylim(0, 30)
ax.grid(axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax = axs[1, 2]
a = [D[w]["off_starv"]["settled"] for w in W]
b = [D[w]["on_starv"]["settled"] for w in W]
c = [D[w]["off_starv"]["mobile"] for w in W]
d = [D[w]["on_starv"]["mobile"] for w in W]
ax.bar(x - 0.19, a, 0.34, color=OFF, label="flag off, settled")
ax.bar(x - 0.19, c, 0.34, bottom=a, color="#c9c8c0", label="flag off, mobile", edgecolor="white", linewidth=1.5)
ax.bar(x + 0.19, b, 0.34, color=ON, label="flag on, settled")
ax.bar(x + 0.19, d, 0.34, bottom=b, color="#7fb2ea", label="flag on, mobile", edgecolor="white", linewidth=1.5)
ax.set_xticks(x)
ax.set_xticklabels(W)
ax.set_title("Starvation deaths per year, control (2 seeds)", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, loc="upper left", fontsize=8.5, ncol=2)
ax.set_ylim(0, 100)
ax.grid(axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(EV, "add129_gates.png"), dpi=150, facecolor="white")
print("ok")
