"""R-106 Add.108 figure: why children starve — orphans (no feeding route) vs children of mothers with no overflow."""
import json
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
W = ["savanna", "montane", "temperate"]
D = {w: json.load(open(os.path.join(ROOT, "scratchpad", f"childprobe_{w}.json"), encoding="utf-8")) for w in W}


def fr(xs, p):
    return sum(1 for x in xs if p(x)) / len(xs) if xs else 0.0


fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))
x = np.arange(3)

# A: decomposition of juvenile starvation deaths
orph = [fr(D[w]["deaths"], lambda d: d.get("mother") != "alive") for w in W]
gap = [fr(D[w]["deaths"], lambda d: d.get("mother") == "alive" and not d["m_at_cap"] and d["m_shareable"] > 0.5) for w in W]
other = [1 - o - g for o, g in zip(orph, gap)]
ax[0].bar(x, orph, color="#6d597a", label="ORPHAN — no feeding route at all")
ax[0].bar(x, gap, bottom=orph, color="#c8553d",
          label="mother alive, NO overflow,\nholds reserve she may not share")
ax[0].bar(x, other, bottom=[o + g for o, g in zip(orph, gap)], color="#bbbbbb", label="mother alive, other")
for i in range(3):
    ax[0].text(i, orph[i] / 2, f"{orph[i]:.0%}", ha="center", color="white", fontsize=9)
    ax[0].text(i, orph[i] + gap[i] / 2, f"{gap[i]:.0%}", ha="center", color="white", fontsize=9)
ax[0].set_xticks(x); ax[0].set_xticklabels(W); ax[0].set_ylim(0, 1)
ax[0].set_ylabel("share of juvenile starvation deaths")
ax[0].set_title("A. What the starving child lacked", fontsize=10)
ax[0].legend(fontsize=8, loc="upper left")

# B: mother at cap (has overflow), dying vs living
wd = 0.36
dv = [fr([d for d in D[w]["deaths"] if d.get("mother") == "alive"], lambda d: d["m_at_cap"]) for w in W]
lv = [fr([d for d in D[w]["living"] if d.get("mother") == "alive"], lambda d: d["m_at_cap"]) for w in W]
b1 = ax[1].bar(x - wd / 2, dv, wd, color="#c8553d", label="dying child")
b2 = ax[1].bar(x + wd / 2, lv, wd, color="#4a6fa5", label="living child")
for bars, vals in ((b1, dv), (b2, lv)):
    for r, v in zip(bars, vals):
        ax[1].text(r.get_x() + r.get_width() / 2, v + 0.01, f"{v:.0%}", ha="center", fontsize=8)
ax[1].set_xticks(x); ax[1].set_xticklabels(W); ax[1].set_ylim(0, 1.1)
ax[1].set_title("B. Mother at her reserve cap = has overflow to give\n(tier 1 is the ONLY route open)", fontsize=10)
ax[1].legend(fontsize=8); ax[1].grid(axis="y", alpha=0.3)

# C: mother's intake, dying vs living — the supply gap underneath
dv = [st.median([d["m_intake"] for d in D[w]["deaths"] if d.get("mother") == "alive"]) for w in W]
lv = [st.median([d["m_intake"] for d in D[w]["living"] if d.get("mother") == "alive"]) for w in W]
b1 = ax[2].bar(x - wd / 2, dv, wd, color="#c8553d", label="mother of a dying child")
b2 = ax[2].bar(x + wd / 2, lv, wd, color="#4a6fa5", label="mother of a living child")
for bars, vals in ((b1, dv), (b2, lv)):
    for r, v in zip(bars, vals):
        ax[2].text(r.get_x() + r.get_width() / 2, v + 0.05, f"{v:.2f}", ha="center", fontsize=8)
ax[2].axhline(1.0, ls="--", c="k", lw=1)
ax[2].set_xticks(x); ax[2].set_xticklabels(W)
ax[2].set_ylabel("mother's intake, x her own need (median)")
ax[2].set_title("C. The dying child's mother harvests less\n(dashed = her own need)", fontsize=10)
ax[2].legend(fontsize=8); ax[2].grid(axis="y", alpha=0.3)

fig.suptitle("R-106 Add.108 — children starve by two routes: ORPHANS (no feeding route; band provisioning is off) and "
             "children of mothers with no overflow\n(`provision_self_keep` = 1.0 forbids sharing the reserve). "
             "Real pipeline, steps 3000-6000.", fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.9))
out = os.path.join(ROOT, "scratchpad", "bp_childprobe.png")
fig.savefig(out, dpi=110)
print("wrote", out)
