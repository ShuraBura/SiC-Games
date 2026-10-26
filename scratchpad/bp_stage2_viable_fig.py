"""R-106 Add.106 Stage-2 figure: canon vs `enable_density_fill_matched_radius` on the three canonical worlds.

Raw per-seed points and paired means, with the anchors placed by BIOME (the WHICH-ANCHOR check):
  e0             cross-forager range 21-37 (Gurven & Kaplan 2007); Ache forest 37 is the TOP of it (Ache a1 is
                 ~half other foragers'); Add.73's biome point anchors temperate 37 / savanna 31
  survival to 15 Ache 0.66, again the top of the range
"""
import importlib.util
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
spec = importlib.util.spec_from_file_location("an", os.path.join(ROOT, "scratchpad", "bp_stage2_analyse.py"))
an = importlib.util.module_from_spec(spec)
spec.loader.exec_module(an)

WORLDS = ["temperate", "savanna", "montane"]
SEEDS = [0, 1, 2]
data = {}
for w in WORLDS:
    for arm in ("canon", "viable"):
        for s in SEEDS:
            f = os.path.join(an.OUTDIR, f"campaign_trajectory_s2_{w}_{arm}_s{s}.json")
            r, _ = an.load(f)
            data[(w, arm, s)] = r

C_CANON, C_FIX = "#4a6fa5", "#c8553d"
fig, ax = plt.subplots(1, 3, figsize=(16, 5.4))


def panel(a, key, title, ylabel, bands):
    for i, w in enumerate(WORLDS):
        for j, (arm, col) in enumerate((("canon", C_CANON), ("viable", C_FIX))):
            x = i + (-0.16 if j == 0 else 0.16)
            vals = [data[(w, arm, s)][key] for s in SEEDS]
            a.scatter([x] * len(vals), vals, s=34, color=col, alpha=0.55, zorder=3,
                      label=(arm if i == 0 else None))
            a.hlines(st.mean(vals), x - 0.11, x + 0.11, color=col, lw=2.6, zorder=4)
        # paired lines per seed
        for s in SEEDS:
            a.plot([i - 0.16, i + 0.16], [data[(w, "canon", s)][key], data[(w, "viable", s)][key]],
                   color="#999999", lw=0.8, zorder=2)
    for kind, val, lab, col in bands:
        if kind == "band":
            a.axhspan(val[0], val[1], color=col, alpha=0.10, zorder=0)
            a.text(2.45, val[1], lab, fontsize=8, color=col, va="top", ha="right")
        else:
            a.axhline(val, ls="--", lw=1.2, color=col, zorder=1)
            a.text(2.45, val, lab, fontsize=8, color=col, va="bottom", ha="right")
    a.set_xticks(range(3))
    a.set_xticklabels(WORLDS)
    a.set_title(title, fontsize=10)
    a.set_ylabel(ylabel)
    a.grid(axis="y", alpha=0.3)


panel(ax[0], "e0", "A. e0, PERIOD life table (equilibrium half)\ntemperate +4.6 yr; savanna and montane fall slightly",
      "e0 (yr)",
      [("band", (21, 37), "cross-forager range 21-37", "#2a9d8f"),
       ("line", 37, "Ache 37 = forager CEILING (tropical forest)", "#555555"),
       ("line", 27, "Hiwi 27 = savanna (llanos) biome match", "#b5838d")])
ax[0].set_ylim(18, 40)
ax[0].legend(loc="lower left", fontsize=9)

panel(ax[1], "pop", "B. Population (sustained, after the snapshot)\nthe fix raises population on every world",
      "people", [])

panel(ax[2], "surv15", "C. Survival to 15, PERIOD\nUP in temperate, DOWN in savanna and montane",
      "l(15)", [("line", 0.66, "Ache 0.66 = forager CEILING", "#555555"), ("line", 0.53, "Hiwi 0.53 (savanna match)", "#b5838d"), ("line", 0.45, "forager FLOOR 0.45 (Agta)", "#2a9d8f")])
ax[2].set_ylim(0.35, 0.70)

fig.suptitle("R-106 Add.107 Stage 2 — FOOD-VIABLE DAUGHTER SITE fix on the three canonical worlds "
             "(real pipeline, 15000 steps, planet fixed, 3 paired demographic seeds; grey = same seed)",
             fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.93))
out = os.path.join(ROOT, "scratchpad", "bp_stage2_viable.png")
fig.savefig(out, dpi=115)
print("wrote", out)
