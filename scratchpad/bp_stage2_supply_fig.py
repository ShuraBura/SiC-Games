"""R-106 Add.111 figure: the two supply-gap repairs vs canon, child vs adult survival."""
import importlib.util
import json
import os
import statistics as st
from types import SimpleNamespace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
spec = importlib.util.spec_from_file_location("an", os.path.join(ROOT, "scratchpad", "bp_stage2_analyse.py"))
an = importlib.util.module_from_spec(spec)
spec.loader.exec_module(an)
from sic_games.phase1_model import TerrainWorld   # noqa: E402

W = ["temperate", "savanna", "montane"]
ARMS = [("pat", "canon (Add.109)", "#4a6fa5"), ("vgran", "+ village granary", "#2a9d8f"), ("sticky", "+ sticky pin release", "#e07a1f")]


def per(f):
    m = json.load(open(f, encoding="utf-8"))["meta"]
    fake = SimpleNamespace(**{k: list(m["life_table_final"][k]) for k in an.KEYS})
    return TerrainWorld.life_table(fake, since={k: m["life_table_snap"][k] for k in an.KEYS})


V = {(w, a): [per(os.path.join(an.OUTDIR, f"campaign_trajectory_s2_{w}_{a}_s{s}.json")) for s in (0, 1, 2)]
     for w in W for a, _, _ in ARMS}
PANELS = [("surv_to_15", "A. Survival to 15 — #19", (0.45, 0.66), [(0.53, "Hiwi"), (0.57, "HG avg")]),
          ("e15", "B. Adult life expectancy at 15 — #20", (28.6, 42.5), [(32.2, "Hiwi"), (37.7, "HG avg")]),
          ("surv_to_45", "C. Survival to 45 — #21", (0.26, 0.43), [(0.29, "Hiwi"), (0.36, "HG avg")])]
fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
for ax, (k, title, (lo, hi), pts) in zip(axes, PANELS):
    ax.axhspan(lo, hi, color="#2a9d8f", alpha=0.08, zorder=0)
    ax.text(2.45, hi, f"forager band {lo}-{hi}", fontsize=8, color="#2a9d8f", ha="right", va="bottom")
    for v, lab in pts:
        ax.axhline(v, ls=":", lw=1, color="#888888", zorder=0)
        ax.text(-0.45, v, lab, fontsize=7, color="#555555", va="bottom")
    for i, w in enumerate(W):
        vals = {a: [p[k] for p in V[(w, a)]] for a, _, _ in ARMS}
        offs = {"pat": -0.25, "vgran": 0.0, "sticky": 0.25}
        for s in range(3):
            ax.plot([i + offs[a] for a, _, _ in ARMS], [vals[a][s] for a, _, _ in ARMS], color="#bbbbbb", lw=0.7, zorder=2)
        for a, lab, col in ARMS:
            ax.scatter([i + offs[a]] * 3, vals[a], s=30, color=col, zorder=3, label=lab if i == 0 else None)
            ax.hlines(st.mean(vals[a]), i + offs[a] - 0.09, i + offs[a] + 0.09, color=col, lw=2.6, zorder=4)
    ax.set_xticks(range(3)); ax.set_xticklabels(W)
    ax.set_title(title, fontsize=10)
    ax.grid(axis="y", alpha=0.3)
axes[0].legend(fontsize=8, loc="upper right")
fig.suptitle("R-106 Add.111 - the two supply-gap repairs. VILLAGE GRANARY: savanna #19 FAIL -> PASS, montane #21 FAIL -> PASS, adults gain too "
             "(not zero-sum);\nbut temperate goes OVER the forager ceiling on #19 and #21 (e0 40 > 37). STICKY RELEASE: worse on savanna "
             "and temperate. Real pipeline, period table, 3 paired seeds (grey = same seed).", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.9))
out = os.path.join(ROOT, "scratchpad", "bp_stage2_supply.png")
fig.savefig(out, dpi=110)
print("wrote", out)
