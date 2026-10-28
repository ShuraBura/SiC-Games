"""R-106 Add.118: figure + modal adult death for the four mortality-structure fixes vs the Add.113 canon (riskvg).

Top row: PERIOD age-at-death distribution (deaths per year of age, share of deaths at age >= 15), canon vs `life`.
  The 900-month cap makes a spike at age 75 in canon; the `life` arm must remove it.
Bottom row: #18-#21 (period life table) per world and arm, mean +/- 1 SE over 3 seeds, the G&K 2007 band shaded.
Also prints the modal adult death age per run and the paired seed differences of #1 and #17 per arm.
"""
import glob
import json
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
EV = os.path.join(ROOT, "docs", "evidence")
W = ["temperate", "savanna", "montane"]
ARMS = ["riskvg", "life", "cond", "dwin", "eta1"]
NAME = {"riskvg": "canon", "life": "life", "cond": "cond", "dwin": "dwin", "eta1": "eta1"}
COL = {"riskvg": "#52514e", "life": "#2a78d6", "cond": "#eb6834", "dwin": "#1baf7a", "eta1": "#6250d6"}


def period_deaths(path):
    m = json.load(open(path, encoding="utf-8"))["meta"]
    fin, snap = m["life_table_final"]["lt_deaths"], m["life_table_snap"]["lt_deaths"]
    return [f - s for f, s in zip(fin, snap)]


def modal_adult(d):
    return max(range(15, len(d)), key=lambda a: d[a])


fig, axes = plt.subplots(2, 4, figsize=(17, 7.6))
print("modal adult death age (period), per seed")
for j, w in enumerate(W):
    ax = axes[0, j]
    for arm in ("riskvg", "life"):
        runs = [period_deaths(f) for f in sorted(glob.glob(os.path.join(OUT, f"campaign_trajectory_s2_{w}_{arm}_s*.json")))]
        print(f"  {w:9s} {NAME[arm]:6s}", [modal_adult(d) for d in runs],
              " share of adult deaths at 75:", [round(d[75] / sum(d[15:]), 3) for d in runs],
              " at >75:", [round(sum(d[76:]) / sum(d[15:]), 3) for d in runs])
        tot = [sum(x) for x in zip(*runs)]
        ad = sum(tot[15:])
        ax.plot(range(15, 100), [tot[a] / ad for a in range(15, 100)], color=COL[arm], lw=2,
                label=f"{NAME[arm]} (mode {modal_adult(tot)})")
    ax.set_title(f"{w}: age at death, period, ages 15+", fontsize=10)
    ax.set_xlabel("age (yr)")
    ax.set_ylabel("share of adult deaths")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, frameon=False)
axes[0, 3].axis("off")
axes[0, 3].text(0.0, 0.5, "Top: the canon spike at 75 is the 900-month cap\n(lifespan_months, audit F-05).\n"
                "enable_lifespan_from_siler removes it.\n\nBottom: each arm alone on the Add.113 canon,\n"
                "3 worlds x 3 seeds, 15,000 steps,\nperiod life table after step 7,500.\nShaded = G&K 2007 forager band.",
                fontsize=9, va="center")

sc = {a: json.load(open(os.path.join(EV, f"scorecard_add118_{a}.json"), encoding="utf-8"))["summary"] for a in ARMS}
LT = [k for k in sc["riskvg"] if k.startswith(("#18", "#19", "#20", "#21"))]
BAND = {"#18": (21, 37), "#19": (0.45, 0.66), "#20": (28.6, 42.5), "#21": (0.26, 0.43)}
for j, lab in enumerate(LT):
    ax = axes[1, j]
    lo, hi = BAND[lab[:3]]
    ax.axhspan(lo, hi, color="#1baf7a", alpha=0.10, zorder=0)
    for i, w in enumerate(W):
        for k, arm in enumerate(ARMS):
            c = sc[arm][lab][w]
            se = st.stdev(c["values"]) / len(c["values"]) ** 0.5
            x = i + (k - 2) * 0.15
            ax.errorbar(x, c["mean"], yerr=se, fmt="o", ms=6, color=COL[arm], capsize=2, lw=1.5,
                        label=NAME[arm] if i == 0 else None)
    ax.set_xticks(range(3))
    ax.set_xticklabels(W, fontsize=9)
    ax.set_title(lab, fontsize=9.5)
    ax.grid(axis="y", alpha=0.25)
    if j == 0:
        ax.legend(fontsize=8, frameon=False, ncol=2)
fig.suptitle("R-106 Add.118 - four audit mortality fixes vs the Add.113 canon", fontsize=12)
fig.tight_layout()
png = os.path.join(EV, "add118_mortality_fixes.png")
fig.savefig(png, dpi=130)
print("wrote", png)

print("\npaired seed differences (arm - canon), mean +/- SE")
for lab in [k for k in sc["riskvg"] if k.startswith(("#1 ", "#17"))]:
    for arm in ARMS[1:]:
        row = []
        for w in W:
            a, b = sc["riskvg"][lab][w]["values"], sc[arm][lab][w]["values"]
            d = [y - x for x, y in zip(a, b)]
            row.append(f"{w[:4]} {st.mean(d):+6.1f} +/- {st.stdev(d) / 3 ** 0.5:4.1f}")
        print(f"  {lab[:28]:28s} {arm:5s}", " | ".join(row))
