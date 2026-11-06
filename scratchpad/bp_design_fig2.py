"""Design task, second observer run: the village store under a five-year shock, the village food supply, who starves."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
OUT = os.path.join(ROOT, "docs", "evidence", "add128_store.png")
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
W = ("temperate", "savanna", "montane")
COL = dict(temperate="#2a78d6", savanna="#eb6834", montane="#1baf7a")
MARK = dict(temperate="o", savanna="s", montane="^")


def load(w, a, s):
    return [json.loads(l) for l in open(os.path.join(L, f"sto_dsto_{w}_{a}_s{s}.jsonl"), encoding="utf-8")]


D = {(w, a, s): load(w, a, s) for w in W for a in ("c", "y5") for s in (0, 1)}
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 3, figsize=(14.5, 4.9))
yrs = list(range(-3, 7))


def yr(w, a, g, k):
    o = []
    for y in yrs:
        i0 = 36 + 12 * y
        t = [(r[g][k] if g else r[k]) for s in (0, 1) for r in D[(w, a, s)][i0:i0 + 12]]
        o.append(sum(t) / len(t))
    return o


ax = axs[0]
ax.axvspan(-0.5, 4.5, color="#f0efe8", lw=0)
for w in W:
    ax.plot(yrs, yr(w, "c", "all", "sph_m"), color=COL[w], lw=1.2, ls="--")
    ax.plot(yrs, yr(w, "y5", "all", "sph_m"), color=COL[w], lw=2, marker=MARK[w], ms=5, label=w)
ax.axhline(20.8, color=INK, lw=0.9)
ax.annotate("store cap", (2, 20.8), xytext=(0, 3), textcoords="offset points", color=MUTED, fontsize=8.5)
ax.set_ylim(0, 22)
ax.set_xlabel("Year from the shock onset (grey = ×0.70 for five years)")
ax.set_ylabel("Village store per head (steps of adult burn)")
ax.set_title("Five years at ×0.70 do not empty the store", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, loc="lower left", title="solid: shock, dashed: control", title_fontsize=8.5)
ax.grid(axis="y", color=GRID, lw=0.7)

ax = axs[1]
ax.axvspan(-0.5, 4.5, color="#f0efe8", lw=0)
for w in W:
    ax.plot(yrs, yr(w, "c", None, "v_sup_p50"), color=COL[w], lw=1.2, ls="--")
    ax.plot(yrs, yr(w, "y5", None, "v_sup_p50"), color=COL[w], lw=2, marker=MARK[w], ms=5)
ax.axhline(1, color=INK, lw=0.9)
ax.annotate("harvest = need", (6, 1), xytext=(0, 4), textcoords="offset points", ha="right", color=MUTED, fontsize=8.5)
ax.set_ylim(0, 5.2)
ax.set_xlabel("Year from the shock onset")
ax.set_ylabel("Village harvest / village need (median village)")
ax.set_title("The median village harvests more than its need", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.grid(axis="y", color=GRID, lw=0.7)

ax = axs[2]
Cs = {}
for w in W:
    dd = [d for s in (0, 1) for r in load(w, "c", s) for d in r["dead"] if 12 <= d["age"] < 120]
    n = len(dd)
    mob = sum(d["mob"] for d in dd)
    pm = sum(r["C"]["mobile"] for s in (0, 1) for r in D[(w, "c", s)]) / sum(len(D[(w, "c", s)]) for s in (0, 1)) * 100
    Cs[w] = (pm, mob / n * 100, n)
import numpy as np
x = np.arange(3)
ax.bar(x - 0.19, [Cs[w][0] for w in W], 0.36, color=MUTED, label="all children aged 1–9")
ax.bar(x + 0.19, [Cs[w][1] for w in W], 0.36, color="#d03b3b", label="children aged 1–9 who starve")
for i, w in enumerate(W):
    ax.annotate(f"n = {Cs[w][2]}", (i + 0.19, Cs[w][1]), xytext=(0, 3), textcoords="offset points", ha="center", color=INK, fontsize=8.5)
ax.set_xticks(x)
ax.set_xticklabels(W)
ax.set_ylim(0, 112)
ax.set_ylabel("Share outside every village (%)")
ax.set_title("Children who starve live outside the villages", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
ax.grid(axis="y", color=GRID, lw=0.7)
fig.tight_layout()
fig.savefig(OUT, dpi=150, facecolor="white")
print(OUT)
