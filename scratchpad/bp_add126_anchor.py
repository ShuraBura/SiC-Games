"""R-106 Add.126: the model's drought response on the scale of the Scania anchor.

Dribe, Olsson & Svensson 2010, Table 3, Scania 1749-1859, about 400 parishes, annual, elasticity to grain OUTPUT, model
with one lag. Response to a 10% fall in output, % change in the rate: e * ln(0.9) -> as ratio^... via elasticities:
   same year = 0.9**e - 1,  sum of the two years = 0.9**(e_t + e_t1) - 1.
Model: the same conversion from drought/pre ratios: elasticity e = ln(ratio)/ln(yield).
   births: period TFR drought / TFR pre (Add.122 period TFR).
   deaths: m(x) drought / pre. Bands 1-5 and 5-15 stand for Scania 1-9; band 15-45 stands for Scania 15-24.
UNIT WARNING printed with the output: the model's window is 30 years, the anchor's shock is one year.
Also: the first 75 steps (6.25 yr) of the drought against the paired control, births and deaths, the nearest thing in
the existing runs to a short shock.
"""
import json
import math
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
W = ("temperate", "savanna", "montane")
COL = dict(temperate="#2a78d6", savanna="#eb6834", montane="#1baf7a")
MARK = dict(temperate="o", savanna="s", montane="^")
TFR0 = dict(temperate=3.76, savanna=4.14, montane=4.11)
S = ("0", "1", "2")
Y = {"085": 0.85, "070": 0.70}
d = json.load(open(os.path.join(ROOT, "scratchpad", "drought_age_pair.json"), encoding="utf-8"))
ANCHOR = {"births": (-0.001, 0.082), "deaths 1-9": (-0.521, -0.612), "deaths 15-24": (-0.261, -0.404)}


def traj(tag):
    return {r["step"]: r for r in json.load(open(os.path.join(OUT, f"campaign_trajectory_{tag}.json"), encoding="utf-8"))["traj"]}


def per10(e):
    return (0.9 ** e - 1) * 100


print("ANCHOR, % change in the rate for a 10% fall in output")
for k, (a, b) in ANCHOR.items():
    print(f"  {k:13s} same year {per10(a):+.1f}%  lag year {per10(b):+.1f}%  two-year sum {per10(a + b):+.1f}%  elasticities {a:+.3f} {b:+.3f} sum {a + b:+.3f}")

model = {}
print("\nMODEL, 30-year window (elasticity; % for a 10% fall)")
for w in W:
    for m, y in Y.items():
        tf = st.mean(d[w][m][s]["drought"]["tfr"] for s in S)
        e_b = math.log(tf / TFR0[w]) / math.log(y)
        rr = lambda k: st.mean(d[w][m][s]["drought"]["bands"][k]["m"] / d[w][m][s]["pre"]["bands"][k]["m"] for s in S)
        # person-exposure weighted 1-15, as a stand-in for 1-9
        e1, e2 = [st.mean(d[w][m][s]["drought"]["bands"][k]["e"] for s in S) for k in ("1-5", "5-15")]
        r115 = (rr("1-5") * e1 + rr("5-15") * e2) / (e1 + e2)
        e_c = math.log(r115) / math.log(y)
        e_a = math.log(rr("15-45")) / math.log(y)
        e_i = math.log(rr("0-1")) / math.log(y)
        model[f"{w}|{m}"] = dict(births=per10(e_b), child=per10(e_c), adult=per10(e_a), infant=per10(e_i), e_b=e_b, e_c=e_c, e_a=e_a, e_i=e_i)
        print(f"  {w[:4]} x{y:.2f} births e={e_b:+.2f} ({per10(e_b):+.1f}%) | deaths 1-15 e={e_c:+.2f} ({per10(e_c):+.1f}%)"
              f" | deaths 15-45 e={e_a:+.2f} ({per10(e_a):+.1f}%) | infants e={e_i:+.2f} ({per10(e_i):+.1f}%)")

print("\nMODEL, first 6.25 years against the paired control, % change in crude rate (mean of seeds; range)")
early = {}
for w in W:
    for m, y in Y.items():
        db, dd = [], []
        for s in (0, 1, 2):
            a, b = 9000, 9075
            T = traj(f"dr_pair_{w}_m{m}_s{s}")
            C = traj(f"s2_{w}_pair_s{s}")
            def rates(R):
                deaths = R[b]["lt_deaths_total"] - R[a]["lt_deaths_total"]
                births = R[b]["pop"] - R[a]["pop"] + deaths
                return births, deaths
            bT, dT = rates(T)
            bC, dC = rates(C)
            db.append((bT / bC - 1) * 100)
            dd.append((dT / dC - 1) * 100)
        early[f"{w}|{m}"] = dict(births=st.mean(db), deaths=st.mean(dd))
        print(f"  {w[:4]} x{y:.2f} births {st.mean(db):+.1f}% [{min(db):+.1f}..{max(db):+.1f}]  deaths {st.mean(dd):+.1f}% [{min(dd):+.1f}..{max(dd):+.1f}]")
json.dump(dict(model=model, early=early), open(os.path.join(ROOT, "docs", "evidence", "add126_response_vs_scania.json"), "w", encoding="utf-8"), indent=1)

INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False})
fig, ax = plt.subplots(figsize=(10.5, 4.6))
rows = [("births", "births", "births", 2), ("deaths 1-9", "child", "child deaths\n(Scania 1–9; model 1–15)", 1), ("deaths 15-24", "adult", "young-adult deaths\n(Scania 15–24; model 15–45)", 0)]
for key, mk, lab, yy in rows:
    a, b = ANCHOR[key]
    ax.plot([per10(a), per10(a + b)], [yy + 0.2, yy + 0.2], color=INK, lw=2.4, solid_capstyle="round")
    ax.scatter([per10(a)], [yy + 0.2], s=62, color="white", edgecolor=INK, linewidth=1.6, zorder=3)
    ax.scatter([per10(a + b)], [yy + 0.2], s=62, color=INK, zorder=3)
    for i, w in enumerate(W):
        for m, y0 in (("085", -0.03), ("070", -0.17)):
            ax.scatter(model[f"{w}|{m}"][mk], yy + y0 + (i - 1) * 0.045, s=46, marker=MARK[w], facecolor=COL[w] if m == "070" else "white", edgecolor=COL[w], linewidth=1.4, zorder=3)
ax.axvline(0, color=INK, lw=0.9)
ax.set_yticks([2, 1, 0], ["births", rows[1][2], rows[2][2]])
ax.set_ylim(-0.5, 2.55)
ax.set_xlabel("% change in the rate for a 10% fall in food supply")
ax.grid(axis="x", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.tick_params(axis="y", length=0)
ax.scatter([], [], s=62, color="white", edgecolor=INK, linewidth=1.6, label="Scania 1749–1859: same year")
ax.scatter([], [], s=62, color=INK, label="Scania: two-year sum")
for w in W:
    ax.scatter([], [], s=46, marker=MARK[w], color=COL[w], label=f"model, {w}, yield ×0.70")
ax.scatter([], [], s=46, marker="o", facecolor="white", edgecolor=MUTED, linewidth=1.4, label="open: yield ×0.85")
ax.set_xlim(-16, 27)
ax.legend(frameon=False, fontsize=8.5, loc="center right")
ax.set_title("Add.126: the model answers a food shock with births; the anchor answers with deaths\nModel = 30-year mean; Scania = one-year shock. The time scales differ (see text)",
             loc="left", fontsize=10.5, fontweight="bold", color=INK)
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "docs", "evidence", "add126_response_vs_scania.png"), dpi=130, facecolor="white")
print("\nwrote docs/evidence/add126_response_vs_scania.png")
