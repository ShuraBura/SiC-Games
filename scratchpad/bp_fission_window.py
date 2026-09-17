"""R-106 #17 — bracket the face-to-face community size without full-blob merging. Exact-cell under-counts (fragments
a multi-cell village); union-find (r=2, merge within 4) over-counts (packing blob). Measure the densest LOCAL
neighborhood: max population in a (2r+1)x(2r+1) window for r=1 (3x3) and r=2 (5x5). That is a clean 'largest
face-to-face community' bracket vs Alberti 158 / Alvard 250. Current canon, both biomes, 3 worlds."""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = 800


def window_max(pop_positions, H, W, r):
    grid = np.zeros((H, W), dtype=np.int32)
    for x, y in pop_positions:
        grid[y % H, x % W] += 1
    # box filter via cumulative sum
    k = 2 * r + 1
    cs = np.pad(grid, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    best = 0
    for y in range(H):
        for x in range(W):
            y0, x0 = max(0, y - r), max(0, x - r)
            y1, x1 = min(H, y + r + 1), min(W, x + r + 1)
            tot = cs[y1, x1] - cs[y0, x1] - cs[y1, x0] + cs[y0, x0]
            if tot > best:
                best = int(tot)
    return best


def run_one(clim, ws):
    w = build(dict(runconfig.load()["DemographyConfig"]), ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    H = getattr(w.terrain_field, "height", 100); W = getattr(w.terrain_field, "width", 100)
    pos = [a.pos for a in w.agent_list]
    return window_max(pos, H, W, 1), window_max(pos, H, W, 2), len(w.agent_list)


def ms(v):
    v = np.array(v, float); return v.mean()


for clim in ("temperate", "savanna"):
    rows = [run_one(clim, ws) for ws in (0, 1, 2)]
    print(f"== {clim.upper()} | densest local community (window-max) vs Alberti 158 / Alvard 250 ==", flush=True)
    print(f"  max 3x3 (r=1) {ms([r[0] for r in rows]):.0f}   max 5x5 (r=2) {ms([r[1] for r in rows]):.0f}   "
          f"pop {ms([r[2] for r in rows]):.0f}", flush=True)
