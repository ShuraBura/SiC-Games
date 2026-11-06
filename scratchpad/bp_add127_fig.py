"""R-106 Add.127 figures: the year-by-year response, and the response per 10% against Scania."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = r"C:\Users\syatom\Projects\SiC Games"
A = json.load(open(os.path.join(ROOT, "scratchpad", "add127_response.json"), encoding="utf-8"))
R, KS = A["res"], A["KS"]
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
CD = {"085": "#2a78d6", "070": "#eb6834"}
MK = {"085": "o", "070": "s"}
LB = {"085": "yield ×0.85", "070": "yield ×0.70"}
W = ("temperate", "savanna", "montane")
COL = dict(temperate="#2a78d6", savanna="#eb6834", montane="#1baf7a")
MARK = dict(temperate="o", savanna="s", montane="^")
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(2, 3, figsize=(13, 7))
P = [("births", "Birth rate"), ("d 1-9", "Deaths, ages 1–9"), ("d 25-44", "Deaths, ages 25–44"), ("s all", "Starvation deaths, all ages"), ("d all", "Deaths, all ages")]
show = list(range(KS.index(-4), KS.index(8) + 1))
xs = [KS[i] for i in show]
for ax, (n, t) in zip(axs.flat, P):
    ax.axvspan(-0.5, 0.5, color="#f0efe8", lw=0)
    ax.axhline(0, color=INK, lw=0.9)
    for d in ("085", "070"):
        v = R[f"pooled|{d}"]
        y = [(v["ratio"][n][i] - 1) * 100 for i in show]
        lo = [(v["ratio_ci"][n][0][i] - 1) * 100 for i in show]
        hi = [(v["ratio_ci"][n][1][i] - 1) * 100 for i in show]
        ax.fill_between(xs, lo, hi, color=CD[d], alpha=0.15, lw=0)
        ax.plot(xs, y, color=CD[d], lw=2, marker=MK[d], ms=5, label=LB[d])
    ax.set_title(t, loc="left", fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xlabel("year from the shock (grey = shock year)")
    ax.set_ylabel("% change from the baseline years")
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
axs[0, 0].legend(frameon=False, loc="lower right")
ax = axs[1, 2]
ctl, a, b = [82, 67, 86], [43, 33, 51], [24, 22, 41]
for i, (w, c, x, y) in enumerate(zip(W, ctl, a, b)):
    ax.bar([i - .27, i, i + .27], [c, x, y], width=.25, color=[MUTED, CD["085"], CD["070"]])
    for xx, val in zip((i - .27, i, i + .27), (c, x, y)):
        ax.text(xx, val + 1.5, str(val), ha="center", fontsize=8.5, color=INK)
ax.set_xticks(range(3), W)
ax.set_ylabel("births in that one step, sum of 3 seeds")
ax.set_title("Births in one shocked step, identical state", loc="left", fontsize=10.5, fontweight="bold", color=INK)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=MUTED, label="control"), Patch(color=CD["085"], label="×0.85"), Patch(color=CD["070"], label="×0.70")], frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.1))
ax.grid(axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
fig.suptitle("Add.127: 90 one-year shocks at each depth. Births fall at once and rebound; adults and starvation move; children do not. Band = 95% CI", x=0.01, ha="left", fontsize=11.5, fontweight="bold", color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(os.path.join(ROOT, "docs", "evidence", "add127_one_year_response.png"), dpi=130, facecolor="white")
ANCHOR = {"births": (-0.001, 0.082), "d 1-9": (-0.521, -0.612), "d 15-24": (-0.261, -0.404)}
per10 = lambda e: (0.9 ** e - 1) * 100
fig, ax = plt.subplots(figsize=(11, 5))
rows = [("births", "births", 2), ("d 1-9", "deaths, ages 1–9", 1), ("d 15-24", "deaths, ages 15–24", 0)]
for n, lab, yy in rows:
    a, b = ANCHOR[n]
    ax.plot([per10(a), per10(a + b)], [yy + .24] * 2, color=INK, lw=2.4, solid_capstyle="round")
    ax.scatter([per10(a)], [yy + .24], s=62, color="white", edgecolor=INK, linewidth=1.6, zorder=3)
    ax.scatter([per10(a + b)], [yy + .24], s=62, color=INK, zorder=3)
    for d, y0 in (("085", 0.02), ("070", -0.22)):
        v = R[f"pooled|{d}"]
        lo, hi = v["ci"][n]
        ax.plot([lo, hi], [yy + y0 + .08] * 2, color=MUTED, lw=1.6)
        ax.scatter([v["per10"][n]], [yy + y0 + .08], s=70, marker="D", facecolor=INK if d == "070" else "white", edgecolor=INK, linewidth=1.4, zorder=3)
        for i, w in enumerate(W):
            ax.scatter(R[f"{w}|{d}"]["per10"][n], yy + y0 + (i - 1) * .03, s=30, marker=MARK[w], facecolor=COL[w] if d == "070" else "white", edgecolor=COL[w], linewidth=1.2, zorder=2)
ax.axvline(0, color=INK, lw=0.9)
ax.set_yticks([2, 1, 0], [r[1] for r in rows])
ax.set_ylim(-.45, 2.5)
ax.set_xlim(-32, 48)
ax.set_xlabel("% change in the rate for a 10% fall in food supply, two-year window")
ax.grid(axis="x", color=GRID, lw=.7)
ax.set_axisbelow(True)
ax.tick_params(axis="y", length=0)
ax.scatter([], [], s=62, color="white", edgecolor=INK, linewidth=1.6, label="Scania: same year")
ax.scatter([], [], s=62, color=INK, label="Scania: two-year sum")
ax.scatter([], [], s=70, marker="D", color=INK, label="model pooled, ×0.70, with 95% CI")
ax.scatter([], [], s=70, marker="D", facecolor="white", edgecolor=INK, label="model pooled, ×0.85, with 95% CI")
for w in W:
    ax.scatter([], [], s=30, marker=MARK[w], color=COL[w], label=f"{w} (filled ×0.70, open ×0.85)")
ax.legend(frameon=False, fontsize=8.5, loc="center right")
ax.set_title("Add.127: on the anchor's own time scale the gap stays for births and for children\nModel = 20 one-year shocks per run; Scania = Dribe, Olsson & Svensson 2010, Table 3", loc="left", fontsize=10.5, fontweight="bold", color=INK)
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "docs", "evidence", "add127_response_vs_scania.png"), dpi=130, facecolor="white")
