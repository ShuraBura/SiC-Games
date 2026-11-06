"""Design task, first observer run: which signals move in the shock year, and where the births come from."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
OUT = os.path.join(ROOT, "docs", "evidence", "add128_signals.png")
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
W = ("temperate", "savanna", "montane")
COL = dict(temperate="#2a78d6", savanna="#eb6834", montane="#1baf7a")
MARK = dict(temperate="o", savanna="s", montane="^")
M = ("10", "085", "070")


def load(w, m, s):
    return [json.loads(l) for l in open(os.path.join(L, f"sig_dsig_{w}_m{m}_s{s}.jsonl"), encoding="utf-8")]


D = {(w, m, s): load(w, m, s) for w in W for m in M for s in (0, 1)}
SIG = [("Mean brake factor, women at risk", "W", "fd_m"), ("Fill, women at risk", "W", "fill_m"), ("Harvest / need, median woman", "W", "raw_p50"),
       ("Harvest / need, 10th pct woman", "W", "raw_p10"), ("Intake fertility factor", "W", "f_int_m"), ("Mother intake EMA", None, "m_ema"),
       ("Post-harvest reserve, children", "C", "fed_m"), ("condition, children", "C", "cond_m")]


def val(w, m, g, k):
    t = 0.0
    for s in (0, 1):
        rows = D[(w, m, s)][36:48]
        t += sum((r[g][k] if g else r[k]) for r in rows) / 12
    return t / 2


plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 3, figsize=(14.5, 5.2), gridspec_kw=dict(width_ratios=[1.35, 1, 1]))
ax = axs[0]
ax.axvline(0, color=INK, lw=0.9)
ys = list(range(len(SIG)))[::-1]
for y, (lab, g, k) in zip(ys, SIG):
    ax.axhline(y, color=GRID, lw=0.7, zorder=0)
    for j, w in enumerate(W):
        c = val(w, "10", g, k)
        x = (val(w, "070", g, k) / c - 1) * 100
        ax.plot(x, y + (j - 1) * 0.16, MARK[w], color=COL[w], ms=7, mec="white", mew=0.8, label=w if y == ys[0] else None)
ax.set_yticks(ys)
ax.set_yticklabels([s[0] for s in SIG])
ax.set_xlabel("Change in the shock year, yield ×0.70, against the paired control (%)")
ax.set_title("Only the brake inputs and the raw harvest move", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, loc="lower left")
ax.tick_params(axis="y", length=0)

mo = list(range(12))
ax = axs[1]
for w in W:
    rows = [r for s in (0, 1) for r in D[(w, "10", s)][:36]]
    y = [sum(r["W"]["fd_m"] for r in rows if r["step"] % 12 == m) / sum(1 for r in rows if r["step"] % 12 == m) for m in mo]
    ax.plot(mo, y, color=COL[w], lw=2, marker=MARK[w], ms=5, label=w)
ax.set_xlabel("Month of the year (step mod 12)")
ax.set_ylabel("Mean brake factor 1 − fill⁶")
ax.set_ylim(0, None)
ax.set_title("The brake opens in the peak season only", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.grid(axis="y", color=GRID, lw=0.7)

ax = axs[2]
Q = ("raw_p10", "raw_p50")
for w in W:
    rows = [r for s in (0, 1) for r in D[(w, "10", s)][:36]]
    lo = sum(r["W"]["raw_p10"] for r in rows) / len(rows)
    md = sum(r["W"]["raw_p50"] for r in rows) / len(rows)
    fl = sum(r["W"]["fill_m"] for r in rows) / len(rows)
    gt = sum(r["W"]["fill_gt1"] for r in rows) / len(rows) * 100
    ax.plot([gt], [md], MARK[w], color=COL[w], ms=11, mec="white", mew=0.8)
    ax.plot([gt, gt], [lo, md], color=COL[w], lw=2, zorder=0)
    ax.plot([gt], [lo], MARK[w], color=COL[w], ms=6, mec="white", mew=0.8)
    ax.annotate(w, (gt, md), xytext=(0, 9 if w != "savanna" else -30), textcoords="offset points", ha="left" if w == "savanna" else "center", color=INK) if w != "savanna" else ax.annotate(w, (gt, md), xytext=(8, -4), textcoords="offset points", color=INK)
ax.axhline(1, color=INK, lw=0.9)
ax.annotate("harvest = need", (70, 1), xytext=(0, 4), textcoords="offset points", color=MUTED, fontsize=8.5)
ax.set_xlim(50, 80)
ax.set_ylim(0, 3.4)
ax.set_xlabel("Women at risk in a village with fill ≥ 1, brake shut (%)")
ax.set_ylabel("Harvest / own need, 10th pct to median")
ax.set_title("Over the ceiling, harvest ample", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.grid(axis="y", color=GRID, lw=0.7)
fig.tight_layout()
fig.savefig(OUT, dpi=150, facecolor="white")
print(OUT)
