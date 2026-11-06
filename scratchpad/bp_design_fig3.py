"""Design task, third observer run: the food account of a village, in units of the ceiling that the brake reads."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
OUT = os.path.join(ROOT, "docs", "evidence", "add128_food_account.png")
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
W = ("temperate", "savanna", "montane")
A = {}
for w in W:
    rows = [json.loads(l) for s in (0, 1) for l in open(os.path.join(L, f"acc_dacc_{w}_s{s}.jsonl"), encoding="utf-8")]
    n = len(rows)
    t = {k: sum(r[k] for r in rows) / n for k in ("need", "intake", "cap", "S_site", "S_oth", "lev_oth")}
    A[w] = dict(site=t["S_site"] / t["cap"], oth=t["lev_oth"] / t["cap"], bonus=(t["S_oth"] - t["lev_oth"]) / t["cap"], need=t["need"] / t["cap"],
                intake=t["intake"] / t["cap"], fill=sum(r["fill_pw"] for r in rows) / n)
print(json.dumps(A, indent=1))
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.9), gridspec_kw=dict(width_ratios=[1.25, 1]))
ax = axs[0]
x = np.arange(3)
c1, c2, c3 = "#2a78d6", "#7fb2ea", "#eb6834"
b0 = np.zeros(3)
for key, col, lab in (("site", c1, "pool at the site cell"), ("oth", c2, "bare yield, other occupied cells"), ("bonus", c3, "agglomeration bonus, other occupied cells")):
    v = np.array([A[w][key] for w in W])
    ax.bar(x - 0.2, v, 0.34, bottom=b0, color=col, label=lab, edgecolor="white", linewidth=1.5)
    b0 += v
ax.bar(x + 0.2, [A[w]["need"] for w in W], 0.34, color=MUTED, label="need of the members")
for i, w in enumerate(W):
    ax.annotate(f"{b0[i]:.2f}", (i - 0.2, b0[i]), xytext=(0, 3), textcoords="offset points", ha="center", color=INK, fontsize=8.5)
    ax.annotate(f"{A[w]['need']:.2f}", (i + 0.2, A[w]["need"]), xytext=(0, 3), textcoords="offset points", ha="center", color=INK, fontsize=8.5)
ax.axhline(1, color=INK, lw=1.1)
ax.annotate("the ceiling (9-cell sum at the site)", (2.47, 1), xytext=(0, 4), textcoords="offset points", ha="right", color=INK, fontsize=8.5)
ax.set_xticks(x)
ax.set_xticklabels(W)
ax.set_ylim(0, 4.2)
ax.set_ylabel("Food per step, in units of the ceiling")
ax.set_title("Supply is 1.7–3.6 × the ceiling; need is below it", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
ax.grid(axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)

ax = axs[1]
ax.bar(x - 0.2, [A[w]["fill"] for w in W], 0.34, color="#d03b3b", label="fill that the brake reads (person weighted)")
ax.bar(x + 0.2, [A[w]["need"] for w in W], 0.34, color=MUTED, label="need / ceiling")
for i, w in enumerate(W):
    ax.annotate(f"{A[w]['fill']:.2f}", (i - 0.2, A[w]["fill"]), xytext=(0, 3), textcoords="offset points", ha="center", color=INK, fontsize=8.5)
    ax.annotate(f"{A[w]['need']:.2f}", (i + 0.2, A[w]["need"]), xytext=(0, 3), textcoords="offset points", ha="center", color=INK, fontsize=8.5)
ax.axhline(1, color=INK, lw=1.1)
ax.set_xticks(x)
ax.set_xticklabels(W)
ax.set_ylim(0, 2.9)
ax.set_title("The brake reads 2–3.4 × the true need ratio", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
ax.grid(axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT, dpi=150, facecolor="white")
print(OUT)
