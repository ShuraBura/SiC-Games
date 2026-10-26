"""R-106 Add.109 figure: fathers feeding (paternal_provision_frac 0.5) vs the new canon, child vs adult survival."""
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
ARMS = [("viable", "canon (viable sites)", "#4a6fa5"), ("pat", "+ fathers feed (0.5)", "#2a9d8f")]


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
        a0 = [p[k] for p in V[(w, "viable")]]
        a1 = [p[k] for p in V[(w, "pat")]]
        for s in range(3):
            ax.plot([i - 0.15, i + 0.15], [a0[s], a1[s]], color="#999999", lw=0.8, zorder=2)
        for off, vals, (_, lab, col) in ((-0.15, a0, ARMS[0]), (0.15, a1, ARMS[1])):
            ax.scatter([i + off] * 3, vals, s=34, color=col, zorder=3, label=lab if i == 0 else None)
            ax.hlines(st.mean(vals), i + off - 0.1, i + off + 0.1, color=col, lw=2.6, zorder=4)
    ax.set_xticks(range(3)); ax.set_xticklabels(W)
    ax.set_title(title, fontsize=10)
    ax.grid(axis="y", alpha=0.3)
axes[0].legend(fontsize=8, loc="upper right")
fig.suptitle("R-106 Add.109 — fathers feeding their children (paternal_provision_frac 0.0 -> 0.5, the documented forager "
             "value): montane #19 moves FAIL -> PASS; temperate improves;\nsavanna gains little and loses ~1.1 yr of "
             "adult e15 (still in band). Real pipeline, period table, 3 paired seeds (grey = same seed).", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.9))
out = os.path.join(ROOT, "scratchpad", "bp_stage2_pat.png")
fig.savefig(out, dpi=110)
print("wrote", out)
