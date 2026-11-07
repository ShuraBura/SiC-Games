"""Add.130 figures, and the last numbers for the addendum. Fig 1: starvation hazard by status decile. Fig 2: the store at the moment of death. Fig 3: the banking gate. Fig 4: flows and the food outside."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
EV = os.path.join(ROOT, "docs", "evidence")
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
OFF, ON, WARM, LIGHT = "#6b6a63", "#2a78d6", "#d03b3b", "#7fb2ea"
W = ("temperate", "savanna", "montane")
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
M = json.load(open(os.path.join(EV, "add130_measurement.json"), encoding="utf-8"))
G = json.load(open(os.path.join(EV, "add130_gate.json"), encoding="utf-8"))


def jl(pre, tag):
    return [json.loads(x) for x in open(os.path.join(L, f"{pre}{tag}.jsonl"), encoding="utf-8")]


def style(ax):
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)


# figure 1
fig, axs = plt.subplots(2, 3, figsize=(13, 6.8), sharex=True, sharey=True)
ages = ("under 15", "15-25", "26-45", "46+")
cols = ("#b58a2a", WARM, ON, OFF)
for r, fl in enumerate(("off", "on")):
    for j, w in enumerate(W):
        ax = axs[r, j]
        for c in range(4):
            h = M[w][fl]["hazard"][c]
            ax.plot(np.arange(1, 11), [max(x, 0.05) if x is not None else None for x in h], color=cols[c], lw=1.8, marker="o", ms=3.5, label=ages[c])
        ax.set_yscale("log")
        ax.set_ylim(0.04, 600)
        style(ax)
        ax.set_title(f"{w}, flag {fl}", loc="left", fontsize=10.5, fontweight="bold", color=INK)
        if r == 1:
            ax.set_xlabel("Status decile inside the draw (1 = lowest)")
        if j == 0:
            ax.set_ylabel("Starvation deaths per 1,000 per year")
axs[0, 0].legend(frameon=False, loc="upper right", fontsize=8.5)
fig.text(0.995, 0.005, "Settled people. Points at 0.05 are zero or below the axis.", ha="right", fontsize=8, color=MUTED)
fig.tight_layout(rect=(0, 0.015, 1, 1))
fig.savefig(os.path.join(EV, "add130_status_hazard.png"), dpi=150, facecolor="white")

# figure 2 and the numbers
num = {}
fig, axs = plt.subplots(1, 3, figsize=(13, 3.9), sharey=True)
for ax, w in zip(axs, W):
    num[w] = {}
    for fl, col in (("off", OFF), ("on", ON)):
        D = [d for s in (0, 1) for d in jl("dth", f"_vl_{w}_{fl}_s{s}")]
        sett = [d for d in D if d["s"] is not None and d["inq"]]
        ad = [d for d in sett if d["age"] >= 180]
        x = np.sort([d["left"] / (d["nn"] * 75000.0) for d in sett])
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(np.clip(x, 0.01, None), y, color=col, lw=1.8, label=f"flag {fl}")
        num[w][fl] = dict(all=len(D), settled=len([d for d in D if d["s"] is not None]), mobile=len([d for d in D if d["s"] is None]), in_draw=len(sett), stranded=sum(1 for d in sett if d["left"] >= d["short"]),
                          short_need=float(np.median([d["short"] / d["need"] for d in ad])), left_need=float(np.median([d["left"] / d["nn"] / 75000.0 for d in ad])), got_share=float(np.median([d["sh"] for d in ad])), age_mode=int(np.bincount([d["age"] // 12 for d in ad]).argmax()),
                          decile0=sum(1 for d in sett if d["pct"] < 0.1) / len(sett))
    ax.axvline(1.0, color=INK, lw=1.0)
    ax.annotate("1 step of adult burn", (1.0, 0.03), xytext=(4, 0), textcoords="offset points", fontsize=8.5, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(0.01, 30)
    ax.set_ylim(0, 1)
    style(ax)
    ax.set_title(w, loc="left", fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xlabel("Store left at the death, per claimant, in steps of burn")
axs[0].set_ylabel("Cumulative share of settled starvation deaths")
axs[0].legend(frameon=False, loc="upper left", fontsize=8.5)
fig.tight_layout()
fig.savefig(os.path.join(EV, "add130_store_at_death.png"), dpi=150, facecolor="white")

# figure 3
fig, axs = plt.subplots(1, 3, figsize=(13, 3.8))
x = np.arange(2)
panels = (("hungry", "Share of village-years with a store below 1 step", "%.2f"), ("sph_med", "Median store per head (steps of burn)", "%.1f"), ("starv_rate", "Starvation deaths per head per year", "%.3f"))
for ax, (k, name, fm) in zip(axs, panels):
    a = [G["montane_off"]["open"][k], G["montane_off"]["shut"][k]]
    b = [G["montane_on"]["open"][k], G["montane_on"]["shut"][k]]
    ax.bar(x - 0.19, a, 0.34, color=OFF, label="flag off")
    ax.bar(x + 0.19, b, 0.34, color=ON, label="flag on")
    for i in range(2):
        ax.annotate(fm % a[i], (i - 0.19, a[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
        ax.annotate(fm % b[i], (i + 0.19, b[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(("Gate open at the site", "Gate shut at the site"))
    ax.set_title(name, loc="left", fontsize=10, fontweight="bold", color=INK)
    ax.margins(y=0.16)
    style(ax)
axs[0].legend(frameon=False, loc="upper left", fontsize=8.5)
fig.tight_layout()
fig.savefig(os.path.join(EV, "add130_gate.png"), dpi=150, facecolor="white")

# figure 4
fig, axs = plt.subplots(1, 2, figsize=(11, 3.9))
ax = axs[0]
xs = np.arange(3)
v = {w: [json.loads(l) for s in (0, 1) for l in open(os.path.join(L, f"vlg_vl_{w}_on_s{s}.jsonl"), encoding="utf-8")] for w in W}
fl = {}
for w in W:
    vs = [r for r in v[w] if r["n"] >= 6]
    H = [r for r in vs if r["sph_min"] < 1]
    F = [r for r in vs if r["sph_min"] >= 1]
    rate = lambda g, ks: sum(sum(r[k] for k in ks) for r in g) / sum(r["heads"] for r in g)
    fl[w] = dict(in_h=rate(H, ("in_mob", "in_vil")), out_h=rate(H, ("out_mob", "out_vil")), in_f=rate(F, ("in_mob", "in_vil")), out_f=rate(F, ("out_mob", "out_vil")), mob_h=rate(H, ("out_mob",)), mob_f=rate(F, ("out_mob",)),
                 hard_h=float(np.mean([r["hard"] for r in H])), ss_h=float(np.mean([r["ss"] for r in H])))
wd = 0.2
ax.bar(xs - 1.5 * wd, [fl[w]["in_f"] for w in W], wd, color="#c9c8c0", label="fed, in")
ax.bar(xs - 0.5 * wd, [fl[w]["out_f"] for w in W], wd, color=OFF, label="fed, out")
ax.bar(xs + 0.5 * wd, [fl[w]["in_h"] for w in W], wd, color=LIGHT, label="hungry, in")
ax.bar(xs + 1.5 * wd, [fl[w]["out_h"] for w in W], wd, color=ON, label="hungry, out")
ax.set_xticks(xs)
ax.set_xticklabels(W)
ax.set_title("Movers per head per year, flag on", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, ncol=2, fontsize=8.5, loc="upper left")
ax.margins(y=0.25)
style(ax)
ax = axs[1]
a = [M[w]["on"]["pc_lean_h"] for w in W]
b = [M[w]["on"]["alt_h"] for w in W]
ax.bar(xs - 0.19, a, 0.34, color=ON, label="inside the hungry village, per head")
ax.bar(xs + 0.19, b, 0.34, color=LIGHT, label="best cell on rings 3-5, for one more person")
for i in range(3):
    ax.annotate(f"{a[i]:.2f}", (i - 0.19, a[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
    ax.annotate(f"{b[i]:.2f}", (i + 0.19, b[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
ax.set_xticks(xs)
ax.set_xticklabels(W)
ax.set_title("Lean-step food, in adult burns per step (medians)", loc="left", fontsize=10.5, fontweight="bold", color=INK)
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
ax.margins(y=0.3)
style(ax)
fig.tight_layout()
fig.savefig(os.path.join(EV, "add130_flows.png"), dpi=150, facecolor="white")

# the gate at the site is a proxy: the villages also bank from the other cells of the village
z = np.load(os.path.join(L, "owz_vz_montane.npz"))
gate = (z["temperature"] <= float(z["tthr"])) | (z["amp"] >= float(z["athr"]))
vs = [r for r in v["montane"] if r["n"] >= 6 and not gate[r["s"][1], r["s"][0]]]


def fopen(s):
    c = [gate[(s[1] + dy) % gate.shape[0], (s[0] + dx) % gate.shape[1]] for dy in range(-2, 3) for dx in range(-2, 3) if z["water"][(s[1] + dy) % gate.shape[0], (s[0] + dx) % gate.shape[1]] == 0]
    return float(np.mean(c)) if c else 0.0


g0 = [r for r in vs if fopen(r["s"]) == 0.0]
g1 = [r for r in vs if fopen(r["s"]) > 0.0]
num["montane_shut_all"] = dict(n=len(g0), hungry=sum(1 for r in g0 if r["sph_min"] < 1) / max(1, len(g0)), sph=float(np.median([r["sph"] for r in g0])) if g0 else None)
num["montane_shut_some"] = dict(n=len(g1), hungry=sum(1 for r in g1 if r["sph_min"] < 1) / max(1, len(g1)), sph=float(np.median([r["sph"] for r in g1])) if g1 else None)
num["flows"] = fl
print(json.dumps(num, indent=0)[:3000])
json.dump(num, open(os.path.join(EV, "add130_numbers.json"), "w", encoding="utf-8"), indent=1)
