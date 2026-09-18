"""R-106 Addendum 103 — does the #17 marker's 3x3 window STRADDLE multiple communities?

Add.93 chose a 3x3 window for `settle_community_max` as a compromise: the exact cell under-counts a multi-cell
village, union-find over-merges the packing blob. But a WINDOW IS NOT A PARTITION. If villages are small and packed,
one window can cover parts of two, and the marker then reports the sum of two communities as one.

Canon hierarchy (temperate): exact-cell 114 < Voronoi village 192 < 3x3 window 256 < band_id 439, and the
window/village ratio is 1.33 temperate (small packed villages) but ~1.0 in savanna (villages far apart) and montane
(villages large). This tests the straddle directly: for the DENSEST 3x3 window, count how many distinct nearest-site
villages and band_ids its occupants belong to. >1 village => the window sums separate communities.

Built at CANONICAL scale (n=3000, patch=40) per Add.101 — absolute spatial structure needs the canonical world.
"""
import os
import sys
import statistics as st
from collections import Counter

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
NAG = int(os.environ.get("C_N", "3000"))
PAT = int(os.environ.get("C_PATCH", "40"))


def run_one(clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, n=NAG, patch=PAT, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    pop = w.agent_list
    sites = list(getattr(w, "_settlement_sites", ()))
    r = int(getattr(w._demog, "settle_radius", 2))

    # nearest-site (village) label per agent, as village_sizes() does
    def village_of(a):
        if not sites:
            return None
        ax, ay = a.pos
        best = None
        for (sx, sy) in sites:
            d = max(abs(ax - sx), abs(ay - sy))
            if best is None or d < best[0]:
                best = (d, (sx, sy))
        return best[1] if best[0] <= r else None

    cell = {}
    for a in pop:
        cell.setdefault(a.pos, []).append(a)

    # densest 3x3 window
    best, bestn = None, -1
    for (cx, cy) in cell:
        occ = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                occ += cell.get((cx + dx, cy + dy), [])
        if len(occ) > bestn:
            best, bestn = occ, len(occ)

    vills = Counter(village_of(a) for a in best)
    bands = Counter(a._group.band_id for a in best)
    vills_real = {k: v for k, v in vills.items() if k is not None}
    top_v = max(vills_real.values()) if vills_real else 0
    return dict(window=bestn, n_villages_in_window=len(vills_real),
                largest_village_share=top_v, n_bands_in_window=len(bands),
                largest_band_in_window=max(bands.values()), pop=len(pop),
                n_sites=len(sites), occupied=len(cell))


def ms(v):
    return st.mean(v) if v else float("nan")


for clim in os.environ.get("C_BIOMES", "temperate,savanna,montane").split(","):
    terr = "mountainous" if clim == "montane" else "coastal"
    cl = "savanna" if clim == "montane" else clim
    rows = []
    for ws in (0, 1, 2):
        try:
            rows.append(run_one(cl, ws) if clim != "montane" else None)
        except Exception as e:
            print(f"  {clim} seed {ws} failed: {e}")
    rows = [r for r in rows if r]
    if not rows:
        continue
    print(f"== {clim.upper()} (n={NAG}, patch={PAT}, {STEPS} steps) ==")
    print(f"  densest 3x3 window holds        {ms([r['window'] for r in rows]):.0f} people")
    print(f"  ... spanning                    {ms([r['n_villages_in_window'] for r in rows]):.1f} distinct villages")
    print(f"  ... largest single village in it{ms([r['largest_village_share'] for r in rows]):>6.0f} people")
    print(f"  ... spanning                    {ms([r['n_bands_in_window'] for r in rows]):.1f} distinct band_ids")
    print(f"  ... largest single band in it   {ms([r['largest_band_in_window'] for r in rows]):>6.0f} people")
    print(f"  pop {ms([r['pop'] for r in rows]):.0f}  sites {ms([r['n_sites'] for r in rows]):.0f}  "
          f"occupied cells {ms([r['occupied'] for r in rows]):.0f}")
    print()
