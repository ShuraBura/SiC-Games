"""R-106 tier-5 UNIT CHECK: which model unit is Hill 2011's 'residential group'?

The band_id-based mean-experienced adult size (48-59) OVERSHOOTS Hill's 28.2, with a heavy tail (band_ids of 100+
adults). Is band_id a residential CAMP, or does it lump village-scale co-residence? This computes the person-weighted
mean-experienced ADULT size under three residential-unit definitions and reports how spatially spread band_ids are:
  - band_id  (affiliation unit; the current-ish unit)
  - cell     (physical co-location: agents on the same grid cell)
  - cluster  (connected component of occupied cells, 8-connectivity = a camp/settlement)
Hill's residential group is people who physically co-reside, so `cell`/`cluster` are the spatial analogues.
Canon, low-noise 3-world panel.
"""
import os
import sys
import statistics as st
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
ADULT_MO = 15.0 * 12.0


def mean_experienced_adults(groups):
    """groups: list of (adult_count, total_size). person-weighted mean of adult_count."""
    tot = sum(n for _, n in groups)
    return (sum(a * n for a, n in groups) / tot) if tot else 0.0


def clusters_of(cells):
    """8-connected components over a set of (x,y) cells. Returns dict cell->cluster_id."""
    cid = {}
    k = 0
    cellset = set(cells)
    for c in cellset:
        if c in cid:
            continue
        stack = [c]; cid[c] = k
        while stack:
            x, y = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (x + dx, y + dy)
                    if nb in cellset and nb not in cid:
                        cid[nb] = k; stack.append(nb)
        k += 1
    return cid


def run_one(clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    agents = [(a._group.band_id, a.pos, 1 if a.age >= ADULT_MO else 0) for a in w.agent_list]

    def groups_by(keyfn):
        g = {}
        for bid, pos, ad in agents:
            k = keyfn(bid, pos)
            ga, gn = g.get(k, (0, 0))
            g[k] = (ga + ad, gn + 1)
        return list(g.values())

    exp_band = mean_experienced_adults(groups_by(lambda bid, pos: bid))
    exp_cell = mean_experienced_adults(groups_by(lambda bid, pos: pos))
    cid = clusters_of([pos for _, pos, _ in agents])
    exp_clus = mean_experienced_adults(groups_by(lambda bid, pos: cid[pos]))

    # spatial spread of band_ids: distinct cells per band_id
    band_cells = {}
    for bid, pos, _ in agents:
        band_cells.setdefault(bid, set()).add(pos)
    spread = [len(s) for s in band_cells.values()]
    # biggest band by adults: how many cells does it span?
    badult = {}
    for bid, pos, ad in agents:
        badult[bid] = badult.get(bid, 0) + ad
    big = max(badult, key=badult.get)
    big_adults = badult[big]; big_cells = len(band_cells[big])
    return exp_band, exp_cell, exp_clus, st.median(spread), float(np.mean(spread)), big_adults, big_cells


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    biomes = os.environ.get("C_BIOMES", "temperate,savanna").split(",")
    print(f"BAND-SIZE UNIT CHECK | canon | {STEPS} steps | worlds {worlds} | Hill mean-experienced = 28.2 ADULTS",
          flush=True)
    for clim in biomes:
        rows = [run_one(clim, ws) for ws in worlds]
        A = np.array(rows, float)
        m = A.mean(axis=0)
        print(f"== {clim.upper()} ==", flush=True)
        print(f"  mean-experienced adults  |  band_id {m[0]:.1f}   cell {m[1]:.1f}   cluster {m[2]:.1f}   "
              f"(Hill 28.2)", flush=True)
        print(f"  band_id spatial spread   |  median {m[3]:.1f} cells/band  mean {m[4]:.1f}   "
              f"| biggest band: {m[5]:.0f} adults across {m[6]:.0f} cells", flush=True)


if __name__ == "__main__":
    main()
