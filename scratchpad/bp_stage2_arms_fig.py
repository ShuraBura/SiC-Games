"""R-106 Add.108 figure: four arms x three worlds, scored on CHILD and ADULT survival against Gurven & Kaplan 2007.
e0 hides an adult crash (it is dominated by child mortality), so the adult markers e15 and l45 are shown too."""
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
ARMS = [("canon", "canon", "#4a6fa5"), ("viable", "viable site", "#2a9d8f"),
        ("bandprov", "band provisioning", "#e9a178"), ("both", "both", "#c8553d")]


def per(path):
    d = json.load(open(path, encoding="utf-8"))
    m = d["meta"]
    fake = SimpleNamespace(**{k: list(m["life_table_final"][k]) for k in an.KEYS})
    return TerrainWorld.life_table(fake, since={k: m["life_table_snap"][k] for k in an.KEYS})


V = {}
for w in W:
    for a, _, _ in ARMS:
        ps = [per(os.path.join(an.OUTDIR, f"campaign_trajectory_s2_{w}_{a}_s{s}.json")) for s in (0, 1, 2)]
        V[(w, a)] = {k: [p[k] for p in ps] for k in ("surv_to_15", "e15", "surv_to_45")}

PANELS = [("surv_to_15", "A. Survival to 15 — l(15)  [#19]", (0.45, 0.66), [(0.53, "Hiwi")]),
          ("e15", "B. Adult life expectancy at 15 — e15", (28.6, 42.5), [(32.2, "Hiwi"), (37.7, "HG avg")]),
          ("surv_to_45", "C. Survival to 45 — l(45)", (0.26, 0.43), [(0.29, "Hiwi"), (0.36, "HG avg")])]
fig, axes = plt.subplots(1, 3, figsize=(17, 5.4))
x = np.arange(3)
wd = 0.2
for ax, (k, title, (lo, hi), pts) in zip(axes, PANELS):
    ax.axhspan(lo, hi, color="#2a9d8f", alpha=0.10, zorder=0)
    ax.text(2.55, hi, f"forager band {lo}-{hi}", fontsize=8, color="#2a9d8f", ha="right", va="bottom")
    for v, lab in pts:
        ax.axhline(v, ls=":", lw=1, color="#777777", zorder=0)
        ax.text(-0.45, v, lab, fontsize=7, color="#555555", va="bottom")
    for j, (a, lab, col) in enumerate(ARMS):
        xs = x + (j - 1.5) * wd
        means = [st.mean(V[(w, a)][k]) for w in W]
        ax.bar(xs, means, wd, color=col, label=lab, alpha=0.9)
        for i, w in enumerate(W):
            ax.scatter([xs[i]] * 3, V[(w, a)][k], s=10, color="k", zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(W)
    ax.set_title(title, fontsize=10)
    ymin = min(min(v[k]) for v in V.values()) * 0.9
    ax.set_ylim(ymin, max(hi, max(max(v[k]) for v in V.values())) * 1.06)
    ax.grid(axis="y", alpha=0.3)
axes[0].legend(fontsize=8, loc="upper right")
fig.suptitle("R-106 Add.108 — band provisioning saves CHILDREN (A) but, in savanna, drops ADULT e15 below the forager "
             "floor (B): it moves deaths, it does not prevent them.\nThe food-viable-site rule alone brings temperate to "
             "the forager average on all three and flips no marker from pass to fail elsewhere. "
             "(real pipeline, period life table, 3 paired seeds; dots = seeds)", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.9))
out = os.path.join(ROOT, "scratchpad", "bp_stage2_arms.png")
fig.savefig(out, dpi=110)
print("wrote", out)
