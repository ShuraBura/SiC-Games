"""R-106 Add.125 figure: the drought test on the adopted canon. Four small panels, one measure each, no dual axis.
A: age-standardised death rate, drought minus pre, split into starvation and non-starvation, per world and depth.
B: m(x) drought / pre at yield x0.70, by age, with the Poisson-plus-seed spread.
C: the signals through time at x0.70, drought / paired control: median intake and body condition.
D: period TFR against the mean fertility brake factor: every window, depth and seed, one curve.
"""
import json
import math
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
W = ("temperate", "savanna", "montane")
COL = dict(temperate="#2a78d6", savanna="#eb6834", montane="#1baf7a")
MARK = dict(temperate="o", savanna="s", montane="^")
S = (0, 1, 2)
BK = ("0-1", "1-5", "5-15", "15-45", "45-65", "65-100")
d = json.load(open(os.path.join(ROOT, "scratchpad", "drought_age_pair.json"), encoding="utf-8"))
pts = json.load(open(os.path.join(ROOT, "scratchpad", "drought_fert_points.json")))
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7,
                     "axes.axisbelow": True, "axes.titlesize": 9.5, "axes.titleweight": "bold", "axes.titlelocation": "left"})
fig, ax = plt.subplots(2, 2, figsize=(13.2, 8.8))


def parts(w, m, s, wn):
    r = d[w][m][str(s)][wn]
    return r["asdr_ns"], r["asdr_s"]   # by single year of age, so the parts sum to the exact ASDR


# A
A = ax[0, 0]
x, labels, summary = 0, [], {}
for w in W:
    for m in ("085", "070"):
        dn = [parts(w, m, s, "drought")[0] - parts(w, m, s, "pre")[0] for s in S]
        ds = [parts(w, m, s, "drought")[1] - parts(w, m, s, "pre")[1] for s in S]
        tot = [a + b for a, b in zip(dn, ds)]
        pre = st.mean(sum(parts(w, m, s, "pre")) for s in S)
        se = st.stdev(tot) / math.sqrt(3)
        summary[f"{w}|{m}"] = dict(asdr_pre=pre, total=st.mean(tot), se=se, nonstarv=st.mean(dn), starv=st.mean(ds), pct=st.mean(tot) / pre * 100)
        A.bar(x - 0.19, st.mean(dn), 0.34, color=MUTED, edgecolor="white", linewidth=1)
        A.bar(x + 0.19, st.mean(ds), 0.34, color=COL[w], edgecolor="white", linewidth=1)
        A.errorbar(x + 0.46, st.mean(tot), yerr=se, fmt="D", color=INK, ms=5, capsize=3, lw=1.1)
        labels.append(f"{w[:4]}\n×0.{m[1:]}")
        x += 1
A.axhline(0, color=INK, lw=0.9)
A.set_xticks(range(6), labels)
A.set_ylabel("change in age-standardised death rate\n(per 1000 per year, drought − pre-drought)")
A.set_title("A. Mortality barely moves: the non-starvation hazard is flat")
A.legend(handles=[Patch(color=MUTED, label="non-starvation part (grey)"), Patch(color=COL["temperate"], label="starvation part (colour = world)"),
                  Line2D([], [], marker="D", color=INK, ls="", ms=5, label="total ± SE of 3 seeds")], frameon=False, loc="upper right", fontsize=8)
A.set_ylim(-1.6, 2.4)

# B
B = ax[0, 1]
for i, w in enumerate(W):
    rr = d[w]["070"]
    ys, lo, hi = [], [], []
    for k in BK:
        q = [rr[str(s)]["drought"]["bands"][k]["m"] / rr[str(s)]["pre"]["bands"][k]["m"] for s in S]
        ys.append(st.mean(q))
        lo.append(st.mean(q) - min(q))
        hi.append(max(q) - st.mean(q))
    xs = np.arange(len(BK)) + (i - 1) * 0.1
    B.errorbar(xs, ys, yerr=[lo, hi], color=COL[w], marker=MARK[w], ms=6, lw=2, capsize=2.5, label=w)
B.axhline(1, color=INK, lw=0.9)
B.set_xticks(range(len(BK)), BK)
B.set_xlabel("age band (years)")
B.set_ylabel("death rate: drought ÷ pre-drought")
B.set_title("B. Yield ×0.70: death rates by age (bars: seed range)")
B.set_ylim(0.75, 1.2)
B.legend(frameon=False, loc="upper left", fontsize=8)

# C
C = ax[1, 0]
for w in W:
    ctl = [{r["step"]: r for r in json.load(open(os.path.join(OUT, f"campaign_trajectory_s2_{w}_pair_s{s}.json"), encoding="utf-8"))["traj"]} for s in S]
    run = [{r["step"]: r for r in json.load(open(os.path.join(OUT, f"campaign_trajectory_dr_pair_{w}_m070_s{s}.json"), encoding="utf-8"))["traj"]} for s in S]
    steps = [t for t in sorted(run[0]) if 8700 <= t <= 10000]
    for key, ls, lab in (("intake_ema_p50", "-", "median intake (EMA)"), ("condition_mean", ":", "body condition")):
        ratio = [st.mean(run[s][t][key] / ctl[s][t][key] for s in S) for t in steps]
        C.plot(steps, ratio, color=COL[w], ls=ls, lw=2 if ls == "-" else 2.2, label=f"{w}: {lab}")
C.axvspan(9000, 9360, color="#999890", alpha=0.18, lw=0)
C.axhline(1, color=INK, lw=0.7)
C.set_xlabel("step (month); grey = the 30-year drought")
C.set_ylabel("drought ÷ paired control")
C.set_title("C. Yield ×0.70: intake falls, the condition signal does not (dotted, at 1.00)")
C.legend(frameon=False, ncol=3, loc="lower center", fontsize=7.5, bbox_to_anchor=(0.5, -0.33))

# D
D = ax[1, 1]
for w in W:
    for lab, a, f in (("drought", "9000", False), ("after", "9360", True)):
        q = [p for p in pts if p[0] == w and p[3] == a]
        D.scatter([p[4] for p in q], [p[5] for p in q], s=42, marker=MARK[w], facecolor=COL[w] if not f else "white", edgecolor=COL[w], linewidth=1.4,
                  label=f"{w}, {lab}")
x = np.array([p[4] for p in pts])
y = np.array([p[5] for p in pts])
c = np.polyfit(np.log(x), np.log(y), 1)
xs = np.linspace(x.min(), x.max(), 50)
D.plot(xs, np.exp(np.polyval(c, np.log(xs))), color=INK, lw=1.1, label=f"fit: TFR ∝ factor^{c[0]:.2f}")
D.set_xlabel("mean fertility brake factor on a woman at risk\n(1 = no brake; about 0.17–0.18 before the drought)")
D.set_ylabel("period TFR in the window")
D.set_title("D. One curve for all worlds: brake factor sets TFR (r = 0.99, log)")
D.legend(frameon=False, fontsize=8, ncol=2, loc="lower right")

fig.suptitle("R-106 Add.125: 30-year drought on the adopted canon (3 worlds × 3 paired seeds): births carry the contraction, mortality does not",
             x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
fig.tight_layout(rect=(0, 0.02, 1, 0.96))
fig.subplots_adjust(hspace=0.34)
fig.savefig(os.path.join(ROOT, "docs", "evidence", "add125_drought_on_canon.png"), dpi=125, facecolor="white")
for k, v in summary.items():
    print(k, {a: round(b, 2) for a, b in v.items()})
json.dump(summary, open(os.path.join(ROOT, "scratchpad", "drought_asdr_summary.json"), "w"), indent=1)
