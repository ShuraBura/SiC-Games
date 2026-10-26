"""Analyse probe 2: is the starving child's mother pinned, released, or blind to the store? + observer control."""
import json
import os
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUTD = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
W = sys.argv[1:] or ["savanna"]


def fin(tag):
    f = os.path.join(OUTD, f"campaign_trajectory_{tag}.json")
    if not os.path.exists(f):
        return None
    t = json.load(open(f, encoding="utf-8"))["traj"][-1]
    return t["pop"], t["realised_e0"], t["lt_deaths_total"]


def frac(R, key, val=True):
    S = [r for r in R if r[key] is not None]
    return (sum(1 for r in S if r[key] == val) / len(S)) if S else float("nan"), len(S)


for w in W:
    f = os.path.join(ROOT, "scratchpad", f"supplyprobe2_{w}.json")
    if not os.path.exists(f):
        print(w, "missing"); continue
    a, b = fin(f"sp_{w}"), fin(f"sp2_{w}")
    print(f"\n=== {w.upper()}   OBSERVER CONTROL probe1 vs probe2 final (pop, e0, deaths):{a} vs {b} -> "
          f"{'ok' if a == b and a is not None else 'MISMATCH'}")
    d = json.load(open(f, encoding="utf-8"))
    for name, R in (("DYING", d["deaths"]), ("LIVING", d["living"])):
        n = len(R)
        br = {k: sum(1 for r in R if r["branch"] == k) / n for k in ("pinned", "ifd", "none")}
        vil = [r for r in R if r["village"]]
        rel = [r for r in vil if r["branch"] == "ifd"]
        print(f"  {name:6s} n={n}: pinned {br['pinned']:.2f}  released->IFD {br['ifd']:.2f}  no site {br['none']:.2f}"
              f" | village members released {len(rel) / max(len(vil), 1):.2f}")
        if vil:
            pa = sorted(r["p_ab"] for r in vil); ps = sorted(r["p_ss"] for r in vil)
            print(f"         release prob (village members): abandonment median {pa[len(pa) // 2]:.2f} "
                  f"mean {sum(pa) / len(pa):.2f} | scalar stress median {ps[len(ps) // 2]:.2f} mean {sum(ps) / len(ps):.2f}")
        for lab, S in (("released village member", rel), ("pinned village member", [r for r in vil if r["branch"] == "pinned"]),
                       ("no site (mobile)", [r for r in R if not r["village"]])):
            if not S:
                continue
            m = len(S)
            ifds = [r for r in S if r["ifd_to_stock"] is not None]
            print(f"         {lab:25s} n={m:5d}  own cell stocked {sum(r['own_stock'] for r in S) / m:.2f}  "
                  f"stock 1 cell away {sum(r['stock_nbr'] for r in S) / m:.2f}  band on that stock "
                  f"{sum(r['band_on_stock'] for r in S) / max(sum(r['stock_nbr'] for r in S), 1):.2f}  "
                  + (f"IFD chose stock {sum(r['ifd_to_stock'] for r in ifds) / len(ifds):.2f}  " if ifds else "")
                  + (f"site stocked {sum(bool(r['site_stock']) for r in S) / m:.2f}  band on site "
                     f"{sum(bool(r['band_on_site']) for r in S) / m:.2f}" if S[0]['village'] else ""))
