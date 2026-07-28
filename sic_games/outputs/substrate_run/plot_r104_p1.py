"""R-104 Phase 1 on the R-105-fixed substrate: error bars on the wealth-in-people headline, + the P2 gradient so far."""
import glob
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "r104_phase1_fixed.png")
CELLS = [("base_ctemp_forage", "coastal-temperate\nforage"),
         ("ctrop_forage", "coastal-tropical\nforage"),
         ("ctrop_agri", "coastal-tropical\nagri (the R-103h anomaly)")]
# R-103h single-seed values on the BUGGY substrate — what these arms are putting error bars on. Only the two
# arms R-103h reported individually are marked; its other arms are covered by the 3.3-5.8 band shaded below.
PRE = {"ctrop_forage": 3.97, "ctrop_agri": 1.11}


def final(tag):
    f = os.path.join(HERE, f"campaign_trajectory_r104_{tag}.json")
    return json.load(open(f, encoding="utf-8"))["traj"][-1] if os.path.exists(f) else None


def ci(v):
    m = statistics.mean(v)
    h = 2.776 * statistics.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
    return m, h


fig, ax = plt.subplots(1, 3, figsize=(15, 4.8))

# ── A. the headline, with error bars for the first time ─────────────────────────────────────────
a = ax[0]
for i, (tag, lab) in enumerate(CELLS):
    vals = [r["noble_lineage_size_lift"] for s in range(5) if (r := final(f"{tag}_s{s}"))]
    if not vals:
        continue
    m, h = ci(vals)
    a.errorbar(i, m, yerr=h, fmt="o", ms=9, color="steelblue", capsize=6, lw=2)
    a.scatter([i] * len(vals), vals, s=22, color="steelblue", alpha=.35, zorder=3)
    if tag in PRE:
        a.scatter([i], [PRE[tag]], marker="x", s=90, color="crimson", zorder=4)
    a.text(i + .09, m, f"{m:.2f}±{h:.2f}", fontsize=9, va="center")
a.axhspan(3.3, 5.8, color="crimson", alpha=.08)
a.text(-0.42, 5.85, "R-103h reported band, buggy substrate (3.3-5.8)", fontsize=8, color="crimson")
a.axhline(1.0, color="k", lw=1, ls="--")
a.text(-0.42, 1.05, "no elite (lift = 1)", fontsize=8)
a.scatter([], [], marker="x", color="crimson", label="R-103h single-seed value, buggy substrate")
a.errorbar([], [], yerr=[], fmt="o", color="steelblue", label="R-104 fixed, mean ± 95% CI (n=5)")
a.set_xticks(range(len(CELLS))); a.set_xticklabels([c[1] for c in CELLS], fontsize=8)
a.set_ylabel("noble lineage_size_lift"); a.set_xlim(-.5, len(CELLS) - .3)
a.set_title("A. wealth-in-people: replicated, with error bars", fontsize=10, loc="left")
a.legend(fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 0.06)); a.grid(alpha=.25, axis="y")

# ── B. people vs goods, same runs ───────────────────────────────────────────────────────────────
a = ax[1]
for i, (tag, lab) in enumerate(CELLS):
    for key, col, off in (("noble_lineage_size_lift", "steelblue", -.13),
                          ("noble_material_lift", "darkorange", .13)):
        vals = [r[key] for s in range(5) if (r := final(f"{tag}_s{s}"))]
        if not vals:
            continue
        m, h = ci(vals)
        a.errorbar(i + off, m, yerr=h, fmt="o", ms=8, color=col, capsize=5, lw=2)
a.axhline(1.0, color="k", lw=1, ls="--")
a.errorbar([], [], yerr=[], fmt="o", color="steelblue", label="PEOPLE (lineage size)")
a.errorbar([], [], yerr=[], fmt="o", color="darkorange", label="GOODS (material)")
a.set_xticks(range(len(CELLS))); a.set_xticklabels([c[1] for c in CELLS], fontsize=8)
a.set_ylabel("lift vs commoner"); a.set_title("B. the elite is in people, not goods", fontsize=10, loc="left")
a.legend(fontsize=8); a.grid(alpha=.25, axis="y")

# ── C. Phase 2 circumscription gradient (partial) ───────────────────────────────────────────────
a = ax[2]
pts = []
for f in sorted(glob.glob(os.path.join(HERE, "campaign_trajectory_r104_circ_p*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    hc = d["meta"].get("habitable_cells", 0); r = d["traj"][-1]
    if hc:
        pts.append((r["pop"] / hc, r["noble_lineage_size_lift"], r["noble_material_lift"],
                    int(os.path.basename(f).split("_p")[1].split(".")[0])))
pts.sort()
if pts:
    a.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color="steelblue", lw=2, label="PEOPLE (lineage size)")
    a.plot([p[0] for p in pts], [p[2] for p in pts], "o-", color="darkorange", lw=2, label="GOODS (material)")
    for d_, l_, m_, P in pts:
        a.annotate(f"patch {P}", (d_, l_), textcoords="offset points", xytext=(4, 7), fontsize=8)
a.axhline(1.0, color="k", lw=1, ls="--")
a.set_xlabel("density (agents / habitable cell)"); a.set_ylabel("lift vs commoner")
a.set_title(f"C. circumscription gradient ({len(pts)}/4 arms done)", fontsize=10, loc="left")
a.legend(fontsize=8); a.grid(alpha=.25)

fig.suptitle("R-104 on the R-105-fixed substrate — Phase 1 complete (15/15 arms, full 5000 steps)", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(OUT, dpi=140)
print("wrote", OUT)
