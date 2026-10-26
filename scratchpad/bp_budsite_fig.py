"""R-106 Add.107 figure: buds found daughter villages OFF the food patch; those villages die; their people starve."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
W = ["temperate", "montane", "savanna"]
D = {w: json.load(open(os.path.join(ROOT, "scratchpad", f"budprobe_{w}.json"), encoding="utf-8")) for w in W}


def fr(xs, p):
    return sum(1 for x in xs if p(x)) / len(xs) if xs else 0.0


fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))
x = np.arange(3)

# A: where buds put their daughters (sites born >= 1000)
off = [fr([s for s in D[w]["sites"] if s["bud"] and s["born"] >= 1000], lambda s: not s["on_patch"]) for w in W]
n = [len([s for s in D[w]["sites"] if s["bud"] and s["born"] >= 1000]) for w in W]
b = ax[0].bar(x, off, color="#c8553d")
for r, v, k in zip(b, off, n):
    ax[0].text(r.get_x() + r.get_width() / 2, v + 0.02, f"{v:.0%}\n(n={k})", ha="center", fontsize=9)
ax[0].set_xticks(x); ax[0].set_xticklabels(W); ax[0].set_ylim(0, 1)
ax[0].set_title("A. Daughter villages founded OFF the food patch\n(buds after step 1000)", fontsize=10)
ax[0].set_ylabel("fraction of bud sites"); ax[0].grid(axis="y", alpha=0.3)

# B: temperate village lifetimes, on vs off patch (the only world with enough buds)
S = [s for s in D["temperate"]["sites"] if s["bud"] and s["born"] >= 1000]
end = 6000
for i, (lab, grp, col) in enumerate((("ON patch", [s for s in S if s["on_patch"]], "#4a6fa5"),
                                     ("OFF patch", [s for s in S if not s["on_patch"]], "#c8553d"))):
    life = [(s["died"] if s["died"] is not None else end) - s["born"] for s in grp]
    cens = [s["died"] is None for s in grp]
    xs = np.full(len(life), i) + np.linspace(-0.15, 0.15, len(life)) if life else []
    ax[1].scatter(xs, life, s=40, color=col, alpha=0.8,
                  edgecolors=["k" if c else col for c in cens], linewidths=[1.2 if c else 0 for c in cens])
ax[1].set_yscale("log"); ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["ON patch", "OFF patch"])
ax[1].set_ylabel("village lifetime (steps, log)")
ax[1].set_title("B. Temperate: how long each daughter village lived\n(black edge = still alive at the end)", fontsize=10)
ax[1].grid(axis="y", alpha=0.3, which="both")

# C: where the starving are, vs the living
wd = 0.2
for j, (lab, fn, col) in enumerate((
        ("dying: OFF patch", lambda w: fr(D[w]["deaths"], lambda d: not d["on_patch"]), "#c8553d"),
        ("dying: in an off-patch bud village", lambda w: fr(D[w]["deaths"], lambda d: d["in_bud_village"] and d["bud_village_on_patch"] is False), "#e9a178"),
        ("living: OFF patch", lambda w: fr(D[w]["living"], lambda d: not d["on_patch"]), "#4a6fa5"))):
    vals = [fn(w) for w in W]
    bb = ax[2].bar(x + (j - 1) * wd, vals, wd, color=col, label=lab)
    for r, v in zip(bb, vals):
        ax[2].text(r.get_x() + r.get_width() / 2, v + 0.01, f"{v:.0%}", ha="center", fontsize=8)
ax[2].set_xticks(x); ax[2].set_xticklabels(W); ax[2].set_ylim(0, 1)
ax[2].set_title("C. Starvation deaths are OFF the food patch\n(temperate: mostly inside off-patch bud villages)", fontsize=10)
ax[2].set_ylabel("fraction"); ax[2].legend(fontsize=8, loc="upper right"); ax[2].grid(axis="y", alpha=0.3)

fig.suptitle("R-106 Add.107 — colonizing budding founds daughter villages on land with NO food "
             "(the site rule reads S_pot, never the harvest field). Real pipeline, canonical worlds, steps 3000-6000.",
             fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.93))
out = os.path.join(ROOT, "scratchpad", "bp_budsite.png")
fig.savefig(out, dpi=110)
print("wrote", out)
