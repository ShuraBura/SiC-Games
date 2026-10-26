"""R-106 Add.105 figure — the packing paradox is a UNIT BUG in the settlement economy.

Panel A  THE SCALE MISMATCH. Every term of a settled agent's food budget, on one log axis, against BURN (the
         per-person yearly requirement). Tier-2 — the term written to feed the packed village — sits four
         orders of magnitude under one person's needs.
Panel B  THE RAW SIGNAL. Per-agent distribution of (food one step away) / (food where it stands), with 1.0
         marked. If the packing were adaptive this mass would sit at or below 1.
Panel C  WHAT A CELL FEEDS vs WHAT STANDS ON IT.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
DUMP = os.path.join(ROOT, "scratchpad", "malthus_ratios.jsonl")

# measured by scratchpad/bp_malthus_scale.py + bp_malthus_cliff.py (temperate, canonical config)
BURN = 75000.0
TIER1_MED = 9.165e5
AGGL_PC_100 = 1.536e5
TIER2_CATCH = 90.0
TIER2_MEASURED = 37.3          # bp_malthus_cliff.py, mean over ACTIVE sites, 3 seeds

fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))

# ── A: the scale mismatch ────────────────────────────────────────────────────────────────────────
labels = ["tier-1\n(cell forage)", "agglomeration\nper-capita, n=100",
          "tier-2\n(9-cell catchment)", "tier-2\nMEASURED at sites"]
vals = [TIER1_MED, AGGL_PC_100, TIER2_CATCH, TIER2_MEASURED]
cols = ["#1f77b4", "#2a9d8f", "#c1121f", "#c1121f"]
bars = ax[0].bar(range(4), vals, color=cols)
ax[0].set_yscale("log")
ax[0].set_ylim(10, 1e7)
ax[0].axhline(BURN, ls="--", c="k", lw=1.6)
ax[0].text(3.42, BURN * 1.35, "BURN = 75,000\none person, one year",
           ha="right", fontsize=8.5, style="italic")
for r, v in zip(bars, vals):
    ax[0].text(r.get_x() + r.get_width() / 2, v * 1.5, f"{v:,.0f}", ha="center", fontsize=8.5)
ax[0].set_xticks(range(4))
ax[0].set_xticklabels(labels, fontsize=8.5)
ax[0].set_ylabel("kcal (log scale)")
ax[0].set_title("A. The settlement economy has one dead leg\n"
                "both terms read the same [0,1] S_pot index;\n"
                "only agglomeration is multiplied by cv_ref into kcal", fontsize=9.5)
ax[0].grid(axis="y", alpha=0.3, which="both")

# ── B: the raw per-agent signal ──────────────────────────────────────────────────────────────────
if os.path.exists(DUMP):
    rs = [json.loads(l)["r"] for l in open(DUMP) if l.strip()]
    rs = [r for r in rs if r == r and r > 0]
    lr = np.log10(rs)
    ax[1].hist(lr, bins=60, color="#1f77b4", alpha=0.85)
    ax[1].axvline(0.0, ls="--", c="crimson", lw=2)
    ax[1].text(0.06, ax[1].get_ylim()[1] * 0.92, "1.0 — indifferent\n(adaptive packing\nwould sit here)",
               color="crimson", fontsize=8.5, va="top")
    frac = sum(1 for r in rs if r > 1) / len(rs)
    med = float(np.median(rs))
    ax[1].text(0.97, 0.72, f"{frac*100:.1f}% of people\nwould eat MORE\none step away\n\nmedian ratio {med:.2f}x",
               transform=ax[1].transAxes, ha="right", fontsize=9,
               bbox=dict(boxstyle="round", fc="#fff3cd", ec="#c1121f"))
    ax[1].set_xlabel("log10( food one step away / food where it stands )")
    ax[1].set_ylabel(f"agents (n = {len(rs):,})")
else:
    ax[1].text(0.5, 0.5, "run bp_malthus_cliff2.py with C_DUMP first",
               ha="center", transform=ax[1].transAxes)
ax[1].set_title("B. The pin holds people against their own interest\n"
                "agglomeration bonus INCLUDED on both sides", fontsize=9.5)
ax[1].grid(axis="y", alpha=0.3)

# ── C: what a cell feeds vs what stands on it ────────────────────────────────────────────────────
names = ["a median cell\nFEEDS", "people per\noccupied cell", "people on a\nSITE cell"]
v2 = [TIER1_MED / BURN, 14.8, 44.2]
e2 = [0.0, 2.0, 4.6]
b2 = ax[2].bar(range(3), v2, yerr=e2, capsize=4, color=["#2a9d8f", "#1f77b4", "#c1121f"])
for r, v in zip(b2, v2):
    ax[2].text(r.get_x() + r.get_width() / 2, v + 1.6, f"{v:.1f}", ha="center", fontsize=9.5)
ax[2].axhline(TIER1_MED / BURN, ls="--", c="#2a9d8f", lw=1.6)
ax[2].set_ylabel("people")
ax[2].set_title("C. The consequence\n"
                "the pin puts 44 people on a cell that feeds 12,\n"
                "and the catchment meant to feed them yields 90 kcal", fontsize=9.5)
ax[2].grid(axis="y", alpha=0.3)

fig.suptitle("R-106 Add.105 — the packing paradox is a UNIT BUG, not an adaptive equilibrium "
             "(temperate, canonical config, 3 seeds, 800 steps)", fontsize=11.5)
fig.tight_layout(rect=(0, 0, 1, 0.93))
out = os.path.join(ROOT, "scratchpad", "bp_malthus_unitbug.png")
fig.savefig(out, dpi=115)
print("wrote", out)
