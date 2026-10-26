"""R-106 Add.113 figure: the spec risk term and the village granary, alone and together, on #18-#21."""
import importlib.util
import io
import json
import os
import statistics as st
import sys
from types import SimpleNamespace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
spec = importlib.util.spec_from_file_location("an", os.path.join(ROOT, "scratchpad", "bp_stage2_analyse.py"))
_o = sys.stdout; sys.stdout = io.StringIO()
an = importlib.util.module_from_spec(spec); spec.loader.exec_module(an)
sys.stdout = _o
from sic_games.phase1_model import TerrainWorld   # noqa: E402

W = ["temperate", "savanna", "montane"]
ARMS = [("pat", "canon (Add.109)", "#4a6fa5"), ("risk", "+ risk as 10% accident share", "#e07a1f"),
        ("vgran", "+ village granary", "#8fbc8f"), ("riskvg", "+ both", "#1b7f5a")]
OFF = {"pat": -0.3, "risk": -0.1, "vgran": 0.1, "riskvg": 0.3}


def per(f):
    m = json.load(open(f, encoding="utf-8"))["meta"]
    fake = SimpleNamespace(**{k: list(m["life_table_final"][k]) for k in an.KEYS})
    return TerrainWorld.life_table(fake, since={k: m["life_table_snap"][k] for k in an.KEYS})


V = {(w, a): [per(os.path.join(an.OUTDIR, f"campaign_trajectory_s2_{w}_{a}_s{s}.json")) for s in (0, 1, 2)]
     for w in W for a, _, _ in ARMS}
PANELS = [("e0", "A. Life expectancy at birth — #18", (21, 37), [(27, "Hiwi")]),
          ("surv_to_15", "B. Survival to 15 — #19", (0.45, 0.66), [(0.53, "Hiwi"), (0.57, "HG avg")]),
          ("e15", "C. Adult life expectancy at 15 — #20", (28.6, 42.5), [(32.2, "Hiwi"), (37.7, "HG avg")]),
          ("surv_to_45", "D. Survival to 45 — #21", (0.26, 0.43), [(0.29, "Hiwi"), (0.36, "HG avg")])]
fig, axes = plt.subplots(1, 4, figsize=(20, 5.4))
for ax, (k, title, (lo, hi), pts) in zip(axes, PANELS):
    ax.axhspan(lo, hi, color="#2a9d8f", alpha=0.08, zorder=0)
    for v, lab in pts:
        ax.axhline(v, ls=":", lw=1, color="#888888", zorder=0)
        ax.text(-0.48, v, lab, fontsize=7, color="#555555", va="bottom")
    for i, w in enumerate(W):
        for a, lab, col in ARMS:
            vals = [p[k] for p in V[(w, a)]]
            ax.scatter([i + OFF[a]] * 3, vals, s=22, color=col, zorder=3, label=lab if i == 0 else None)
            ax.hlines(st.mean(vals), i + OFF[a] - 0.08, i + OFF[a] + 0.08, color=col, lw=2.6, zorder=4)
    ax.set_xticks(range(3)); ax.set_xticklabels(W)
    ax.set_title(title + f"\n(shaded = forager band {lo}-{hi})", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=9, frameon=False)
fig.suptitle("R-106 Add.113 — the spec risk term ALONE lowers survival (it restores missing mortality); the village granary ALONE "
             "overshoots temperate; TOGETHER all three worlds pass #18-#21\n(12/12 inside the band at 1 SE, every seed inside). "
             "Real pipeline, period table, 3 paired seeds.", fontsize=10)
fig.tight_layout(rect=(0, 0.06, 1, 0.88))
out = os.path.join(ROOT, "scratchpad", "bp_stage2_risk.png")
fig.savefig(out, dpi=105)
print("wrote", out)
