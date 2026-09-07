"""MESH GEOMETRY: does a village occupy ONE cell with gaps to its neighbours, or a blob/mesh?

    py -3 sic_games/outputs/substrate_run/mesh_report.py vpool_sep vpool_test arch_swap

Reads campaign_spatial_<tag>.npz. For each site it measures, on the torus:
  * nearest-neighbour Chebyshev distance to another site  -> the GAP
  * on-site population vs ring-1 catchment population       -> the CONCENTRATION
A '1 cell + gaps' geography needs NN distance > 2 cells (disjoint radius-1 catchments,
Vita-Finzi & Higgs) AND most residents ON the site, not in the ring. Purely descriptive;
no anchors invented here (the 2-cell disjointness follows from settle_catchment_radius=1).
"""
from __future__ import annotations
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def _cheb_torus(a, b, N):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    dx = min(dx, N - dx); dy = min(dy, N - dy)
    return max(dx, dy)


def _mesh(tag):
    p = os.path.join(HERE, f"campaign_spatial_{tag}.npz")
    if not os.path.exists(p):
        return None
    d = np.load(p)
    sites = d["sites"]; people = d["people"].astype(float)
    N = sites.shape[0]
    S = [tuple(v) for v in np.argwhere(sites > 0)]   # (row=y, col=x)
    n = len(S)
    if n == 0:
        return {"n": 0}
    # nearest-neighbour spacing
    nn = []
    for i, s in enumerate(S):
        best = N
        for j, t in enumerate(S):
            if i == j:
                continue
            best = min(best, _cheb_torus(s, t, N))
        nn.append(best)
    nn = np.array(nn)
    siteset = set(S)
    on_site = 0.0; ring = 0.0
    for (sy, sx) in S:
        on_site += people[sy, sx]
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                cy = (sy + dy) % N; cx = (sx + dx) % N
                if (cy, cx) in siteset:
                    continue
                ring += people[cy, cx]
    return {
        "n": n,
        "nn_med": float(np.median(nn)),
        "pct_adj": float((nn <= 1).mean()),     # within 1 cell of another site (the mesh)
        "pct_disjoint": float((nn > 2).mean()),  # catchments fully disjoint
        "on_site": on_site, "ring": ring,
        "conc": on_site / (on_site + ring) if (on_site + ring) else float("nan"),
        "step": int(d["step"]),
    }


def report(tags):
    M = {t: _mesh(t) for t in tags}
    tags = [t for t in tags if M[t] is not None and M[t].get("n", 0) > 0]
    if not tags:
        raise SystemExit("no spatial dumps with sites")
    w = max(11, max(len(t) for t in tags) + 1)
    print("MESH GEOMETRY  (1 cell + gaps, or blob/mesh?)")
    print(f"  {'':<22}" + "".join(f"{t:>{w}}" for t in tags) + "     want")
    rows = [
        ("n sites", lambda m: f"{m['n']}", ""),
        ("NN dist median", lambda m: f"{m['nn_med']:.2f}", "> 2 cells"),
        ("% adjacent (<=1)", lambda m: f"{100*m['pct_adj']:.0f}%", "-> 0%"),
        ("% disjoint (>2)", lambda m: f"{100*m['pct_disjoint']:.0f}%", "-> high"),
        ("on-site pop", lambda m: f"{m['on_site']:.0f}", ""),
        ("catchment-ring pop", lambda m: f"{m['ring']:.0f}", ""),
        ("concentration", lambda m: f"{m['conc']:.2f}", "-> 1.0"),
    ]
    for lab, fn, want in rows:
        print(f"  {lab:<22}" + "".join(f"{fn(M[t]):>{w}}" for t in tags) + f"     {want}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    report(sys.argv[1:])
