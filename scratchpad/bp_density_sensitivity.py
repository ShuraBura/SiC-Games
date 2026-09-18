"""R-106 Addendum 101 — which markers are DENSITY/HARNESS sensitive, and which are robust?

Add.100 found #11 and #17 diverging between the Add.86-99 probe harness and the canonical campaign. Add.101's
controlled test showed the cause is NOT the time horizon (the campaign already disagrees at step 800) but the
HARNESS: the probe builds a different world (capacity patch (20,20,24) vs the campaign's (30,30,40)) and the
campaign is founder-path-dependent (600 founders -> pop 471; 3000 -> 3832).

This tabulates each marker across four regimes spanning an ~8x population range, and plots the sensitivity, so
the verdicts that are density-specific are separated from the ones that hold everywhere.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# regime -> (label, population)
REG = [("probe\n600f", 1270), ("campaign\n600f", 471), ("campaign\n3000f @800", 3832), ("campaign\n3000f late", 3133)]

# marker -> values in the four regimes (temperate)
M = {
    "#14 material Gini (adults)":   [0.386, 0.387, 0.403, 0.422],
    "#14 Gini (within-cell)":       [0.280, None,  0.296, 0.316],
    "#3 village median":            [44.0,  67.5,  67.3,  70.7],
    "#1 band experienced adults":   [33.3,  45.0,  29.4,  30.6],
    "#17 community max":            [155.0, 205.3, 224.3, 255.7],
    "#11 status->RS (age-ctrl)":    [0.157, 0.133, 0.305, 0.283],
    "#9 gini_cred":                 [None,  0.276, 0.428, 0.663],
    "#10 polygyny (all men)":       [0.022, 0.013, 0.022, 0.042],
}


def spread(v):
    x = [t for t in v if t is not None]
    return max(x) / min(x) if x and min(x) > 0 else float("nan")


print(f"{'marker':32s} " + " ".join(f"{r[0].replace(chr(10),' '):>20s}" for r in REG) + "   max/min")
print("-" * 130)
for k, v in sorted(M.items(), key=lambda kv: spread(kv[1])):
    cells = " ".join(f"{('n/a' if t is None else f'{t:.3f}'):>20s}" for t in v)
    print(f"{k:32s} {cells}   {spread(v):.2f}x")

# --- figure: normalised sensitivity ---
fig, ax = plt.subplots(figsize=(10.5, 5.6))
x = np.arange(len(REG))
for k, v in M.items():
    vals = [t for t in v]
    base = next(t for t in vals if t is not None)
    norm = [(t / base if t is not None else np.nan) for t in vals]
    robust = spread(v) < 1.25
    ax.plot(x, norm, "o-" if robust else "s--", lw=2.4 if robust else 1.6,
            color=("#1f77b4" if robust else "#d62728"), alpha=0.95 if robust else 0.8,
            label=f"{k}  ({spread(v):.2f}x)")
ax.axhline(1.0, color="0.4", lw=1, ls=":")
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in REG], fontsize=9)
ax.set_ylabel("value relative to the probe regime")
ax.set_title("R-106 Add.101 — marker sensitivity to harness/density (temperate, ~8x population range)\n"
             "blue solid = robust (<1.25x); red dashed = density-sensitive, so its verdict is regime-specific")
ax.legend(fontsize=7.5, loc="upper left", ncol=2)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_density_sensitivity.png", dpi=110)
print("\nwrote bp_density_sensitivity.png")
