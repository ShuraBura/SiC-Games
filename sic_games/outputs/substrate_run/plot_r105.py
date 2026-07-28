"""R-105 figure: the runaway, the fix, and the R-64 A/B — raw trajectories with the thresholds drawn on."""
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "r105_ceiling_fix.png")


def traj(path):
    return json.load(open(path, encoding="utf-8"))["traj"]


def series(t, k):
    return [r["step"] for r in t], [r[k] for r in t]


fig, ax = plt.subplots(2, 2, figsize=(13, 8.5))

# ── A. the runaway vs the fix, on the SAME specimen ─────────────────────────────────────────────
bug = traj(os.path.join(HERE, "pre_r105_buggy", "campaign_trajectory_r104_ctrop_forage_s3.json"))
fix = traj(os.path.join(HERE, "campaign_trajectory_fix.json"))
a = ax[0][0]
a.semilogy(*series(bug, "pop"), color="crimson", lw=2, label="gap OPEN (pre-R-105)")
a.semilogy(*series(fix, "pop"), color="steelblue", lw=2, label="gap CLOSED (enable_aggl_ceiling)")
a.axvline(2000, color="0.5", ls=":", lw=1)
a.text(2020, 3e3, "step 2000\n(buggy arm tips)", fontsize=8, color="0.35")
a.set_title("A. coastal-tropical seed 3 — the runaway specimen", fontsize=10, loc="left")
a.set_xlabel("step"); a.set_ylabel("population (log)"); a.legend(fontsize=8); a.grid(alpha=.25)

# ── B. what food was doing while it happened ────────────────────────────────────────────────────
a = ax[0][1]
a.plot(*series(bug, "surplus_med"), color="crimson", lw=2, label="surplus_med, gap OPEN")
a.plot(*series(fix, "surplus_med"), color="steelblue", lw=2, label="surplus_med, gap CLOSED")
a.axhline(1.0, color="k", ls="--", lw=1)
a.text(60, 1.01, "saturation (food stops binding)", fontsize=8)
a2 = a.twinx()
a2.plot(*series(bug, "deaths_starv"), color="crimson", lw=1, alpha=.45, ls="-.")
a2.plot(*series(fix, "deaths_starv"), color="steelblue", lw=1, alpha=.45, ls="-.")
a2.set_ylabel("starvation deaths / snapshot (dash-dot)", fontsize=8)
a.set_title("B. the Malthusian limit: gone, then restored", fontsize=10, loc="left")
a.set_xlabel("step"); a.set_ylabel("median surplus"); a.legend(fontsize=8, loc="center right"); a.grid(alpha=.25)

# ── C/D. the R-64 A/B, 5 seeds × 2 arms ─────────────────────────────────────────────────────────
arms = {}
for f in sorted(glob.glob(os.path.join(HERE, "campaign_trajectory_r105ab_s*_ceil*.json"))):
    b = os.path.basename(f)
    arms[(int(b.split("_s")[1].split("_")[0]), int(b.split("_ceil")[1].split(".")[0]))] = traj(f)

for a, key, title, ylab in ((ax[1][0], "pop", "C. R-64 A/B — population (5 seeds)", "population"),
                            (ax[1][1], "pct_stratified", "D. R-64 A/B — %stratified", "% of pop in stratified bands")):
    for (seed, ceil), t in arms.items():
        a.plot(*series(t, key), color=("crimson" if ceil == 0 else "steelblue"),
               lw=1.4, alpha=.75, ls=("-" if ceil == 0 else "--"))
    a.plot([], [], color="crimson", ls="-", label="gap OPEN (ceil0)")
    a.plot([], [], color="steelblue", ls="--", label="gap CLOSED (ceil1)")
    a.set_title(title, fontsize=10, loc="left")
    a.set_xlabel("step"); a.set_ylabel(ylab); a.grid(alpha=.25); a.legend(fontsize=8)

ax[1][0].axhline(7200, color="darkgreen", lw=1.2, ls=":")
ax[1][0].text(60, 7400, "R-64 published plateau ~7200", fontsize=8, color="darkgreen")
ax[1][1].axhspan(9, 16, color="darkgreen", alpha=.12)
ax[1][1].text(60, 16.5, "R-64 published band 9-16%", fontsize=8, color="darkgreen")

fig.suptitle("R-105 — the agglomeration bonus escaped the carrying-capacity ceiling: fix + R-64 re-validation",
             fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.savefig(OUT, dpi=140)
print("wrote", OUT)
